"""Tests for Phase 2a: classify_chunk, run_phase2a, and retry logic (§5.2, §5.5).

Uses mocked instructor client — no real LLM calls.
Integration tests with real LLM are in test_phase2_integration.py (gated).
"""

from __future__ import annotations

import logging
import time
from typing import Any
from unittest.mock import MagicMock, call, patch

import pytest
from pydantic import ValidationError

from engines.excerpting.contracts import (
    ClassificationResult,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ScholarlyFunction,
)
from engines.excerpting.src.phase2_classify import (
    CLASSIFY_SYSTEM_PROMPT,
    _SNIPPET_NOT_FOUND_FEEDBACK,
    classify_chunk,
    normalize_offsets,
    run_phase2a,
    verify_segments,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_classification_result,
    _make_mock_instructor_client,
)

# ─── Longer test text with segments extractable by normalize_offsets ───
_TEST_TEXT = (
    "الوضوء هو استعمال الماء في أعضاء مخصوصة بنية التطهر "
    "وقد قال النبي صلى الله عليه وسلم لا يقبل الله صلاة أحدكم إذا أحدث حتى يتوضأ "
    "والحكم أن الوضوء فرض لكل صلاة مكتوبة عند جمهور العلماء"
)
_TEST_TOKENS = _TEST_TEXT.split()
_TEST_TOTAL = len(_TEST_TOKENS)
_TEST_WORD_COUNT = _TEST_TOTAL  # all words are Arabic


def _make_test_chunk(**overrides: Any) -> Any:
    """Shortcut: assembled chunk with _TEST_TEXT."""
    defaults = {
        "assembled_text": _TEST_TEXT,
        "word_count": _TEST_WORD_COUNT,
        "total_tokens": _TEST_TOTAL,
    }
    defaults.update(overrides)
    return _make_assembled_chunk(**defaults)


# ═══════════════════════════════════════════════════════════════════
# Tests — CLASSIFY_SYSTEM_PROMPT
# ═══════════════════════════════════════════════════════════════════


class TestClassifySystemPrompt:
    def test_contains_arabic_header(self) -> None:
        """SPEC §5.2.2 prompt contains Arabic analysis header."""
        assert "تحليل النصوص العلمية الإسلامية" in CLASSIFY_SYSTEM_PROMPT

    def test_contains_all_16_functions(self) -> None:
        """All 16 scholarly function types listed in prompt."""
        for fn in ScholarlyFunction:
            assert fn.value in CLASSIFY_SYSTEM_PROMPT, f"Missing: {fn.value}"

    def test_has_single_format_variable(self) -> None:
        """Only {structural_format} is a format variable."""
        # Substitute it and verify no remaining braces
        filled = CLASSIFY_SYSTEM_PROMPT.format(structural_format="prose")
        assert "{" not in filled
        assert "}" not in filled

    def test_text_snippet_instruction(self) -> None:
        """Prompt instructs FIRST 50 CHARACTERS copied EXACTLY."""
        assert "FIRST 50 CHARACTERS" in CLASSIFY_SYSTEM_PROMPT
        assert "copied EXACTLY" in CLASSIFY_SYSTEM_PROMPT


# ═══════════════════════════════════════════════════════════════════
# Tests — classify_chunk
# ═══════════════════════════════════════════════════════════════════


class TestClassifyChunk:
    def test_prompt_construction(self) -> None:
        """System prompt formatted with structural_format; user message wraps text."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        classify_chunk(chunk, client, config)

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        assert messages[0]["role"] == "system"
        assert "prose" in messages[0]["content"]  # structural_format
        assert messages[1]["role"] == "user"
        assert "<text>" in messages[1]["content"]
        assert _TEST_TEXT in messages[1]["content"]
        assert "</text>" in messages[1]["content"]

    def test_max_retries_zero(self) -> None:
        """DD-S2-8: max_retries=0 on instructor call."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        classify_chunk(chunk, client, config)

        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["max_retries"] == 0

    def test_error_feedback_appended_to_user_message(self) -> None:
        """DD-S2-5: error feedback goes in user message, not system prompt."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        feedback = "\n\nNote: fix your snippets"
        classify_chunk(chunk, client, config, error_feedback=feedback)

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        # Feedback in user message
        assert "fix your snippets" in messages[1]["content"]
        # System prompt unchanged
        assert "fix your snippets" not in messages[0]["content"]

    def test_response_model_is_classification_result(self) -> None:
        """Instructor receives response_model=ClassificationResult."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        classify_chunk(chunk, client, config)

        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["response_model"] is ClassificationResult


# ═══════════════════════════════════════════════════════════════════
# Tests — run_phase2a (orchestrator + retry logic)
# ═══════════════════════════════════════════════════════════════════


class TestRunPhase2a:
    def test_happy_path(self) -> None:
        """Valid classification → normalized + verified segments returned."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=2)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result
        segments = result[chunk.chunk_id]
        assert len(segments) == 2
        assert segments[0].start_word == 0
        assert segments[-1].end_word == _TEST_TOTAL - 1

    def test_multiple_chunks(self) -> None:
        """Each chunk processed independently."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        c1 = _make_test_chunk(chunk_id="chunk_a", div_id="chunk_a")
        c2 = _make_test_chunk(chunk_id="chunk_b", div_id="chunk_b")

        result = run_phase2a([c1, c2], client, config)

        assert "chunk_a" in result
        assert "chunk_b" in result

    def test_retry_on_api_error(self) -> None:
        """API error → exponential backoff → retry succeeds."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(
            side_effect=[RuntimeError("API timeout"), cr]
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with patch("engines.excerpting.src.phase2_classify.time.sleep") as mock_sleep:
            result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result
        mock_sleep.assert_called_once_with(1)  # 2^0 = 1 second

    def test_all_retries_exhausted_api_error(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """All 3 attempts fail → chunk absent from result, error logged."""
        client = _make_mock_instructor_client(
            side_effect=RuntimeError("API down")
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with (
            patch("engines.excerpting.src.phase2_classify.time.sleep"),
            caplog.at_level(logging.ERROR),
        ):
            result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id not in result
        assert ExcerptingErrorCodes.EX_C_001 in caplog.text
        assert "FAILED" in caplog.text

    def test_retry_on_normalization_failure(self) -> None:
        """Snippet not found → retry with snippet feedback."""
        # First call: bad snippet that won't be found
        bad_cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=10,
                    text_snippet="هذا نص غير موجود في الأصل أبدا ولن يوجد",
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ],
            total_segments=1,
        )
        # Second call: good snippet
        good_cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(side_effect=[bad_cr, good_cr])
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result
        # Second call should have snippet feedback in user message
        second_call = client.chat.completions.create.call_args_list[1]
        user_msg = second_call.kwargs["messages"][1]["content"]
        assert "text_snippet that could not be located" in user_msg

    def test_retry_on_validation_error(self) -> None:
        """Pydantic ValidationError → retry with error feedback."""
        good_cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(
            side_effect=[
                ValidationError.from_exception_data(
                    title="ClassificationResult",
                    line_errors=[
                        {
                            "type": "missing",
                            "loc": ("segments",),
                            "msg": "Field required",
                            "input": {},
                        }
                    ],
                ),
                good_cr,
            ]
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result

    def test_telemetry_logging(self, caplog: pytest.LogCaptureFixture) -> None:
        """INFO log emitted with source_id, chunk_id, latency, attempt."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=1)
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with caplog.at_level(logging.INFO):
            run_phase2a([chunk], client, config)

        assert "Phase 2a classify" in caplog.text
        assert "source_id=src_test" in caplog.text
        assert "attempt=1" in caplog.text

    def test_coverage_failure_retry_with_feedback(self) -> None:
        """Coverage invariant violation → retry with invariant error feedback."""
        # Build a CR where normalization succeeds but verification fails:
        # two segments whose anchors resolve but produce a gap
        # (e.g., single segment that doesn't start at 0)
        text = "أ ب ت ث ج ح خ"
        tokens = text.split()
        total = len(tokens)

        # Segment whose snippet is "ب" → anchors at token 1, not 0 → I-CS-3 fail
        bad_cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=99,
                    text_snippet="ب",
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ],
            total_segments=1,
        )
        # Good CR with snippet starting at token 0
        good_cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=99,
                    text_snippet="أ",
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ],
            total_segments=1,
        )
        client = _make_mock_instructor_client(side_effect=[bad_cr, good_cr])
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=total,
            total_tokens=total,
        )

        result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result
        # Second call had coverage invariant feedback
        second_call = client.chat.completions.create.call_args_list[1]
        user_msg = second_call.kwargs["messages"][1]["content"]
        assert "coverage invariant" in user_msg

    def test_v_p2_9_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """total_segments mismatch → warning logged, actual count used."""
        cr = _make_classification_result(_TEST_TEXT, n_segments=2)
        # Tamper with total_segments to trigger V-P2-9
        cr_bad = ClassificationResult(
            segments=cr.segments,
            total_segments=99,
        )
        client = _make_mock_instructor_client(return_value=cr_bad)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with caplog.at_level(logging.WARNING):
            result = run_phase2a([chunk], client, config)

        assert chunk.chunk_id in result
        assert "V-P2-9" in caplog.text
        # Still works — actual count (2) used
        assert len(result[chunk.chunk_id]) == 2

    def test_empty_chunks_list(self) -> None:
        """Empty input → empty output."""
        client = _make_mock_instructor_client()
        config = ExcerptingConfig()
        result = run_phase2a([], client, config)
        assert result == {}
