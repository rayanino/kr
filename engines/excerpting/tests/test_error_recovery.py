"""Error recovery tests — verifies LLM failure modes and retry behavior.

Tests that the pipeline correctly handles: single-chunk failures (skip+continue),
exponential backoff on API errors, and coverage retry with error feedback.
"""

from __future__ import annotations

import time
from typing import Any, Optional
from unittest.mock import patch

from engines.excerpting.contracts import (
    ClassificationResult,
    ClassifiedSegment,
    ExcerptingConfig,
    ScholarlyFunction,
)
from engines.excerpting.src.phase2_classify import run_phase2a

from .conftest import (
    _make_assembled_chunk,
    _make_classification_result,
    _make_mock_instructor_client,
)


# ═══════════════════════════════════════════════════════════════════
# Shared helpers
# ═══════════════════════════════════════════════════════════════════


_REAL_ARABIC_TEXT = (
    "بسم الله الرحمن الرحيم الحمد لله رب العالمين "
    "والصلاة والسلام على أشرف المرسلين "
    "قال المؤلف رحمه الله تعالى باب الطهارة "
    "الطهارة في اللغة النظافة والنزاهة "
    "وفي الاصطلاح رفع الحدث وزوال الخبث"
)


def _make_valid_cr(text: str) -> ClassificationResult:
    """Build a valid ClassificationResult covering the entire text."""
    tokens = text.split()
    return ClassificationResult(
        segments=[
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=len(tokens) - 1,
                text_snippet=text[:50],
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
        ],
        total_segments=1,
    )


# ═══════════════════════════════════════════════════════════════════
# Test 1: Single-chunk LLM failure (skip + continue)
# ═══════════════════════════════════════════════════════════════════


class TestSingleChunkFailure:
    """Create 3 chunks. Mock raises for chunk 2. Chunks 1+3 succeed."""

    def test_failing_chunk_skipped_others_succeed(self) -> None:
        """Chunk 2 fails all retries → absent from result. Chunks 1+3 present."""
        chunk1 = _make_assembled_chunk(
            chunk_id="div_1_0", div_id="div_1_0",
            source_id="src_test", assembled_text=_REAL_ARABIC_TEXT,
            total_tokens=len(_REAL_ARABIC_TEXT.split()),
            word_count=len(_REAL_ARABIC_TEXT.split()),
        )
        chunk2 = _make_assembled_chunk(
            chunk_id="div_2_0", div_id="div_2_0",
            source_id="src_test", assembled_text=_REAL_ARABIC_TEXT,
            total_tokens=len(_REAL_ARABIC_TEXT.split()),
            word_count=len(_REAL_ARABIC_TEXT.split()),
        )
        chunk3 = _make_assembled_chunk(
            chunk_id="div_3_0", div_id="div_3_0",
            source_id="src_test", assembled_text=_REAL_ARABIC_TEXT,
            total_tokens=len(_REAL_ARABIC_TEXT.split()),
            word_count=len(_REAL_ARABIC_TEXT.split()),
        )

        call_tracker: dict[str, int] = {}

        def mock_classify(
            chunk: Any, client: Any, config: Any,
            error_feedback: Optional[str] = None,
        ) -> ClassificationResult:
            cid = chunk.chunk_id
            call_tracker.setdefault(cid, 0)
            call_tracker[cid] += 1
            if cid == "div_2_0":
                raise Exception("API error for chunk 2")
            return _make_classification_result(
                chunk.assembled_text, n_segments=1
            )

        config = ExcerptingConfig()
        mock_client = _make_mock_instructor_client()

        with patch(
            "engines.excerpting.src.phase2_classify.classify_chunk",
            side_effect=mock_classify,
        ):
            result = run_phase2a([chunk1, chunk2, chunk3], mock_client, config)

        # Chunks 1 and 3 succeed, chunk 2 is absent
        assert "div_1_0" in result
        assert "div_2_0" not in result
        assert "div_3_0" in result
        assert len(result) == 2

        # Chunk 2 was retried max_attempts times (1 + RETRY_COUNT = 3)
        assert call_tracker["div_2_0"] == 1 + config.RETRY_COUNT


# ═══════════════════════════════════════════════════════════════════
# Test 2: Exponential backoff on API error
# ═══════════════════════════════════════════════════════════════════


class TestExponentialBackoff:
    """Mock raises once then succeeds. Verify backoff delay."""

    def test_backoff_delay_on_api_error(self) -> None:
        """API error on attempt 1 → backoff → success on attempt 2. Total ≥1s."""
        chunk = _make_assembled_chunk(
            assembled_text=_REAL_ARABIC_TEXT,
            total_tokens=len(_REAL_ARABIC_TEXT.split()),
            word_count=len(_REAL_ARABIC_TEXT.split()),
        )
        attempt_counter = {"n": 0}

        def mock_classify(
            chunk: Any, client: Any, config: Any,
            error_feedback: Optional[str] = None,
        ) -> ClassificationResult:
            attempt_counter["n"] += 1
            if attempt_counter["n"] == 1:
                raise Exception("rate limit exceeded")
            return _make_classification_result(
                chunk.assembled_text, n_segments=1
            )

        config = ExcerptingConfig()
        mock_client = _make_mock_instructor_client()

        start = time.monotonic()
        with patch(
            "engines.excerpting.src.phase2_classify.classify_chunk",
            side_effect=mock_classify,
        ):
            result = run_phase2a([chunk], mock_client, config)
        elapsed = time.monotonic() - start

        # Should have the chunk in results (succeeded on retry)
        assert chunk.chunk_id in result
        # Exponential backoff: 2**0 = 1 second sleep on first failure
        assert elapsed >= 0.9, f"Expected ≥1s backoff, got {elapsed:.2f}s"


# ═══════════════════════════════════════════════════════════════════
# Test 3: Coverage retry with error feedback
# ═══════════════════════════════════════════════════════════════════


class TestCoverageRetry:
    """verify_segments raises ValueError → outer loop retries with error feedback."""

    def test_coverage_gap_triggers_retry(self) -> None:
        """First attempt: verify_segments raises → retry with error feedback → succeeds."""
        chunk = _make_assembled_chunk(
            assembled_text=_REAL_ARABIC_TEXT,
            total_tokens=len(_REAL_ARABIC_TEXT.split()),
            word_count=len(_REAL_ARABIC_TEXT.split()),
        )

        valid_cr = _make_classification_result(_REAL_ARABIC_TEXT, n_segments=1)
        attempt_counter = {"n": 0}
        feedback_received: list[Optional[str]] = []

        def mock_classify(
            chunk: Any, client: Any, config: Any,
            error_feedback: Optional[str] = None,
        ) -> ClassificationResult:
            attempt_counter["n"] += 1
            feedback_received.append(error_feedback)
            return valid_cr

        verify_counter = {"n": 0}

        def mock_verify(segments: Any, total_tokens: int) -> None:
            verify_counter["n"] += 1
            if verify_counter["n"] == 1:
                raise ValueError("Coverage gap: tokens 6-7 not covered by any segment")
            # Second call passes (after retry with error feedback)

        config = ExcerptingConfig()
        mock_client = _make_mock_instructor_client()

        with patch(
            "engines.excerpting.src.phase2_classify.classify_chunk",
            side_effect=mock_classify,
        ), patch(
            "engines.excerpting.src.phase2_classify.verify_segments",
            side_effect=mock_verify,
        ):
            result = run_phase2a([chunk], mock_client, config)

        # Should succeed on second attempt
        assert chunk.chunk_id in result
        # classify_chunk was called at least twice
        assert attempt_counter["n"] >= 2
        # Second call got error feedback about the coverage violation
        assert feedback_received[1] is not None
        assert "coverage" in feedback_received[1].lower()
