"""Integration tests for Phase 2 with real LLM calls.

Gated by OPENROUTER_API_KEY environment variable — skipped when absent.
These tests verify end-to-end: classify → normalize → verify → group → verify.
"""

from __future__ import annotations

import os

import instructor
import openai
import pytest

from engines.excerpting.contracts import (
    AssembledChunk,
    ExcerptingConfig,
    SelfContainmentLevel,
    validate_cs_invariants,
    validate_tu_invariants,
)
from engines.excerpting.src.phase2_classify import (
    classify_chunk,
    normalize_offsets,
    verify_segments,
)
from engines.excerpting.src.phase2_group import group_chunk, verify_units
from engines.excerpting.tests.conftest import _make_assembled_chunk

_HAS_API_KEY = bool(os.environ.get("OPENROUTER_API_KEY"))
_SKIP_MSG = "OPENROUTER_API_KEY not set"

# Short fiqh text (~100 words) for integration testing.
_INTEGRATION_TEXT = (
    "باب أحكام الوضوء "
    "الوضوء هو استعمال الماء الطهور في الأعضاء الأربعة على صفة مخصوصة في الشرع "
    "وهو فرض لكل صلاة مكتوبة بإجماع أهل العلم "
    "ودليل ذلك قوله تعالى يا أيها الذين آمنوا إذا قمتم إلى الصلاة فاغسلوا وجوهكم "
    "وأيديكم إلى المرافق وامسحوا برءوسكم وأرجلكم إلى الكعبين "
    "وقال النبي صلى الله عليه وسلم لا يقبل الله صلاة أحدكم إذا أحدث حتى يتوضأ "
    "فدل الكتاب والسنة على وجوب الوضوء للصلاة "
    "وأركان الوضوء عند الجمهور ستة "
    "غسل الوجه وغسل اليدين إلى المرافق ومسح الرأس وغسل الرجلين إلى الكعبين والترتيب والموالاة"
)
_INTEGRATION_TOKENS = _INTEGRATION_TEXT.split()
_INTEGRATION_TOTAL = len(_INTEGRATION_TOKENS)


def _get_client() -> instructor.Instructor:
    """Create instructor client for OpenRouter (proven experiment pattern)."""
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.environ["OPENROUTER_API_KEY"],
        ),
        mode=instructor.Mode.JSON,
    )


def _make_integration_chunk() -> AssembledChunk:
    """Build an AssembledChunk with the integration test text."""
    return _make_assembled_chunk(
        assembled_text=_INTEGRATION_TEXT,
        word_count=_INTEGRATION_TOTAL,
        total_tokens=_INTEGRATION_TOTAL,
    )


@pytest.mark.skipif(not _HAS_API_KEY, reason=_SKIP_MSG)
class TestPhase2aIntegration:
    """Classify small Arabic text and verify canonical segments."""

    def test_classify_and_normalize(self) -> None:
        client = _get_client()
        config = ExcerptingConfig()
        chunk = _make_integration_chunk()

        # Classify
        cr = classify_chunk(chunk, client, config)
        assert len(cr.segments) >= 1

        # Normalize offsets
        canonical = normalize_offsets(
            cr.segments, chunk.assembled_text, chunk.total_tokens
        )
        assert len(canonical) == len(cr.segments)
        assert canonical[0].start_word == 0
        assert canonical[-1].end_word == _INTEGRATION_TOTAL - 1

        # Verify invariants
        verify_segments(canonical, chunk.total_tokens)
        validate_cs_invariants(canonical, chunk.total_tokens)


@pytest.mark.skipif(not _HAS_API_KEY, reason=_SKIP_MSG)
class TestPhase2FullIntegration:
    """Full classify + group pipeline with real LLM."""

    def test_full_pipeline(self) -> None:
        client = _get_client()
        config = ExcerptingConfig()
        chunk = _make_integration_chunk()

        # Phase 2a: Classify + normalize + verify
        cr = classify_chunk(chunk, client, config)
        canonical = normalize_offsets(
            cr.segments, chunk.assembled_text, chunk.total_tokens
        )
        verify_segments(canonical, chunk.total_tokens)

        # Phase 2b: Group + verify
        er = group_chunk(chunk, canonical, client, config)
        assert len(er.teaching_units) >= 1

        repaired = verify_units(
            er.teaching_units, canonical, chunk.total_tokens
        )
        validate_tu_invariants(repaired, canonical, chunk.total_tokens)

        # Basic sanity checks on output
        for unit in repaired:
            assert unit.start_word >= 0
            assert unit.end_word < _INTEGRATION_TOTAL
            assert len(unit.segment_indices) >= 1
            assert unit.self_containment in (
                SelfContainmentLevel.FULL,
                SelfContainmentLevel.PARTIAL,
                SelfContainmentLevel.DEPENDENT,
            )
