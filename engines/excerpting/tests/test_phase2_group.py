"""Tests for Phase 2b: group_chunk, verify_units, run_phase2b (§5.3, §5.4.3).

Uses mocked instructor client — no real LLM calls.
"""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import patch

import pytest
from engines.excerpting.contracts import (
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExtractionResult,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
)
from engines.excerpting.src.phase2_group import (
    GROUP_SYSTEM_PROMPT,
    _build_group_user_message,
    _build_segment_summary,
    compute_active_modules,
    group_chunk,
    run_phase2b,
    verify_units,
)
from engines.excerpting.src.prompts import (
    GROUP_DIALECTICAL_RULES,
    GROUP_FIQH_RULES,
    GROUP_HADITH_RULES,
    GROUP_INTRO_RULES,
    GROUP_VERSE_RULES,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_classified_segment,
    _make_mock_instructor_client,
)


# ═══════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════

_TEST_TEXT = (
    "الوضوء هو استعمال الماء في أعضاء مخصوصة بنية التطهر "
    "وقد قال النبي صلى الله عليه وسلم لا يقبل الله صلاة أحدكم إذا أحدث حتى يتوضأ "
    "والحكم أن الوضوء فرض لكل صلاة مكتوبة عند جمهور العلماء"
)
_TEST_TOKENS = _TEST_TEXT.split()
_TEST_TOTAL = len(_TEST_TOKENS)


def _make_test_chunk(**overrides: Any) -> Any:
    defaults = {
        "assembled_text": _TEST_TEXT,
        "word_count": _TEST_TOTAL,
        "total_tokens": _TEST_TOTAL,
    }
    defaults.update(overrides)
    return _make_assembled_chunk(**defaults)


def _make_two_segments() -> list[ClassifiedSegment]:
    """Two contiguous segments covering all tokens in _TEST_TEXT."""
    mid = _TEST_TOTAL // 2
    return [
        ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=mid - 1,
            text_snippet=_TEST_TEXT[:50],
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        ),
        ClassifiedSegment(
            segment_index=1,
            start_word=mid,
            end_word=_TEST_TOTAL - 1,
            text_snippet=_TEST_TEXT[
                len(" ".join(_TEST_TOKENS[:mid])) + 1 :
                len(" ".join(_TEST_TOKENS[:mid])) + 51
            ],
            scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
            confidence=0.85,
        ),
    ]


def _make_valid_extraction_result(
    segments: list[ClassifiedSegment],
) -> ExtractionResult:
    """Build a valid ExtractionResult that groups all segments into one unit."""
    return ExtractionResult(
        teaching_units=[
            TeachingUnit(
                unit_index=0,
                segment_indices=[s.segment_index for s in segments],
                start_word=segments[0].start_word,
                end_word=segments[-1].end_word,
                text_snippet=_TEST_TEXT[:80],
                primary_function=segments[0].scholarly_function,
                secondary_functions=[
                    s.scholarly_function
                    for s in segments[1:]
                    if s.scholarly_function != segments[0].scholarly_function
                ],
                description_arabic="تعريف الوضوء وحكمه وأدلته من السنة النبوية الشريفة",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )
        ],
        total_units=1,
        notes=None,
    )


# ═══════════════════════════════════════════════════════════════════
# Tests — GROUP_SYSTEM_PROMPT
# ═══════════════════════════════════════════════════════════════════


class TestGroupSystemPrompt:
    def test_contains_arabic_header(self) -> None:
        assert "تحليل النصوص العلمية الإسلامية" in GROUP_SYSTEM_PROMPT

    def test_contains_self_containment_criteria(self) -> None:
        for criterion in ["C-SC-1", "C-SC-2", "C-SC-3", "C-SC-4", "C-SC-5"]:
            assert criterion in GROUP_SYSTEM_PROMPT, f"Missing: {criterion}"

    def test_has_single_format_variable(self) -> None:
        filled = GROUP_SYSTEM_PROMPT.format(structural_format="prose")
        assert "{" not in filled
        assert "}" not in filled

    def test_decontextualization_rules(self) -> None:
        assert "قال أبو حنيفة" in GROUP_SYSTEM_PROMPT
        assert "ورد عليه بأن" in GROUP_SYSTEM_PROMPT

    def test_ee1_explained_explanation_unity(self) -> None:
        """EE-1: General explained+explanation unity rule is present."""
        assert "EE-1" in GROUP_SYSTEM_PROMPT
        assert "explained object" in GROUP_SYSTEM_PROMPT
        assert "explanation form one teaching unit" in GROUP_SYSTEM_PROMPT
        # Verify specific instances are still listed
        assert "hadith + sharh" in GROUP_SYSTEM_PROMPT
        assert "verse (matn) + commentary" in GROUP_SYSTEM_PROMPT
        assert "definition + examples" in GROUP_SYSTEM_PROMPT


# ═══════════════════════════════════════════════════════════════════
# Tests — compute_active_modules (DR28 IU-4)
# ═══════════════════════════════════════════════════════════════════


class TestComputeActiveModules:
    def test_empty_segments_returns_no_modules(self) -> None:
        assert compute_active_modules([]) == []

    def test_unclassified_triggers_nothing(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.UNCLASSIFIED,
        )
        assert compute_active_modules([seg]) == []

    def test_evidence_hadith_triggers_hadith(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
        )
        modules = compute_active_modules([seg])
        assert GROUP_HADITH_RULES in modules
        assert len(modules) == 1

    def test_narration_triggers_hadith(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.NARRATION,
        )
        assert GROUP_HADITH_RULES in compute_active_modules([seg])

    def test_evidence_quran_triggers_verse(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.EVIDENCE_QURAN,
        )
        modules = compute_active_modules([seg])
        assert GROUP_VERSE_RULES in modules
        assert len(modules) == 1

    @pytest.mark.parametrize("fn", [
        ScholarlyFunction.RULE_STATEMENT,
        ScholarlyFunction.CONDITION_EXCEPTION,
        ScholarlyFunction.EVIDENCE_IJMA,
        ScholarlyFunction.EVIDENCE_QIYAS,
    ])
    def test_fiqh_triggers(self, fn: ScholarlyFunction) -> None:
        seg = _make_classified_segment(scholarly_function=fn)
        assert GROUP_FIQH_RULES in compute_active_modules([seg])

    def test_refutation_triggers_dialectical(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.REFUTATION,
        )
        assert GROUP_DIALECTICAL_RULES in compute_active_modules([seg])

    def test_structural_transition_triggers_intro(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.STRUCTURAL_TRANSITION,
        )
        assert GROUP_INTRO_RULES in compute_active_modules([seg])

    def test_multiple_triggers_load_multiple_modules(self) -> None:
        """A chunk with hadith + fiqh + dialectical content loads 3 modules."""
        segs = [
            _make_classified_segment(
                segment_index=0,
                scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
            ),
            _make_classified_segment(
                segment_index=1, start_word=10, end_word=19,
                scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            ),
            _make_classified_segment(
                segment_index=2, start_word=20, end_word=29,
                scholarly_function=ScholarlyFunction.REFUTATION,
            ),
        ]
        modules = compute_active_modules(segs)
        assert GROUP_HADITH_RULES in modules
        assert GROUP_FIQH_RULES in modules
        assert GROUP_DIALECTICAL_RULES in modules
        assert len(modules) == 3

    def test_definition_triggers_fiqh_rules(self) -> None:
        """DEFINITION triggers GROUP_FIQH_RULES for FP-25 definition pair splitting (DR40)."""
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.DEFINITION,
        )
        assert compute_active_modules([seg]) == [GROUP_FIQH_RULES]


# ═══════════════════════════════════════════════════════════════════
# Tests — _build_group_user_message (DR28 IU-5)
# ═══════════════════════════════════════════════════════════════════


class TestBuildGroupUserMessage:
    def test_contains_xml_structure(self) -> None:
        """DR28 user message has <active_rules>, <input>, <critical_reminders>."""
        chunk = _make_test_chunk()
        segments = _make_two_segments()
        msg = _build_group_user_message(chunk, segments)
        assert "<active_rules>" in msg
        assert "</active_rules>" in msg
        assert "<input>" in msg
        assert "</input>" in msg
        assert "<critical_reminders>" in msg
        assert "</critical_reminders>" in msg

    def test_contains_text_and_segments(self) -> None:
        """Input block wraps <text> and <classified_segments>."""
        chunk = _make_test_chunk()
        segments = _make_two_segments()
        msg = _build_group_user_message(chunk, segments)
        assert "<text>" in msg
        assert "</text>" in msg
        assert "<classified_segments>" in msg
        assert "</classified_segments>" in msg

    def test_core_rules_always_present(self) -> None:
        """CORE rules appear in active_rules regardless of segment types."""
        chunk = _make_test_chunk()
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.DEFINITION,
        )
        msg = _build_group_user_message(chunk, [seg])
        assert "EE-1" in msg
        assert "DECONTEXTUALIZATION" in msg

    def test_hadith_module_loaded_when_hadith_present(self) -> None:
        chunk = _make_test_chunk()
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
        )
        msg = _build_group_user_message(chunk, [seg])
        assert "HADITH RULES:" in msg
        assert "DERIVED BENEFITS" in msg

    def test_hadith_module_absent_for_grammar(self) -> None:
        chunk = _make_test_chunk()
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.DEFINITION,
        )
        msg = _build_group_user_message(chunk, [seg])
        assert "HADITH RULES:" not in msg
        assert "DERIVED BENEFITS" not in msg

    def test_structural_format_substituted(self) -> None:
        """The {structural_format} variable is resolved in the output format."""
        chunk = _make_test_chunk()
        segments = _make_two_segments()
        msg = _build_group_user_message(chunk, segments)
        assert "The text format is: prose" in msg
        assert "{structural_format}" not in msg


# ═══════════════════════════════════════════════════════════════════
# Tests — _build_segment_summary
# ═══════════════════════════════════════════════════════════════════


class TestBuildSegmentSummary:
    def test_format(self) -> None:
        seg = _make_classified_segment(
            segment_index=3,
            start_word=10,
            end_word=20,
            scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
        )
        summary = _build_segment_summary([seg])
        assert "Segment 3:" in summary
        assert "words 10\u201320" in summary  # en-dash
        assert "function=evidence_hadith" in summary
        assert 'snippet="' in summary

    def test_uses_scholarly_function_value(self) -> None:
        seg = _make_classified_segment(
            scholarly_function=ScholarlyFunction.OPINION_STATEMENT
        )
        summary = _build_segment_summary([seg])
        assert "function=opinion_statement" in summary


# ═══════════════════════════════════════════════════════════════════
# Tests — group_chunk
# ═══════════════════════════════════════════════════════════════════


class TestGroupChunk:
    def test_prompt_construction(self) -> None:
        """User message contains <text> and <classified_segments> blocks."""
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        group_chunk(chunk, segments, client, config)

        call_kwargs = client.chat.completions.create.call_args
        messages = call_kwargs.kwargs["messages"]
        user_msg = messages[1]["content"]
        assert "<text>" in user_msg
        assert "</text>" in user_msg
        assert "<classified_segments>" in user_msg
        assert "</classified_segments>" in user_msg
        assert "Segment 0:" in user_msg
        assert "Segment 1:" in user_msg

    def test_max_retries_zero(self) -> None:
        """CLI adapter handles retries; outer loop provides error feedback."""
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        group_chunk(chunk, segments, client, config)

        call_kwargs = client.chat.completions.create.call_args
        assert call_kwargs.kwargs["max_retries"] == 0

    def test_error_feedback_in_user_message(self) -> None:
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        group_chunk(chunk, segments, client, config, error_feedback="\n\nFix it")

        messages = client.chat.completions.create.call_args.kwargs["messages"]
        assert "Fix it" in messages[1]["content"]
        assert "Fix it" not in messages[0]["content"]


# ═══════════════════════════════════════════════════════════════════
# Tests — verify_units
# ═══════════════════════════════════════════════════════════════════


class TestVerifyUnits:
    def test_valid_units_pass(self) -> None:
        segments = _make_two_segments()
        units = [
            TeachingUnit(
                unit_index=0,
                segment_indices=[0, 1],
                start_word=segments[0].start_word,
                end_word=segments[-1].end_word,
                text_snippet=_TEST_TEXT[:80],
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
                description_arabic="شرح الوضوء وأحكامه وأدلته من السنة الشريفة",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )
        ]
        result = verify_units(units, segments, _TEST_TOTAL)
        assert len(result) == 1

    def test_v_p2_14_derives_word_offsets(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-14: LLM word offsets differ → derived values used + warning."""
        segments = _make_two_segments()
        units = [
            TeachingUnit(
                unit_index=0,
                segment_indices=[0, 1],
                start_word=999,  # wrong — should be segments[0].start_word
                end_word=888,  # wrong — should be segments[-1].end_word
                text_snippet=_TEST_TEXT[:80],
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
                description_arabic="شرح الوضوء وأحكامه وأدلته من السنة الشريفة",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )
        ]
        with caplog.at_level(logging.WARNING):
            result = verify_units(units, segments, _TEST_TOTAL)

        assert result[0].start_word == segments[0].start_word
        assert result[0].end_word == segments[-1].end_word
        assert "V-P2-14" in caplog.text

    def test_v_p2_15_full_with_notes_via_construct(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-15: FULL + notes → notes cleared (via model_construct bypass)."""
        segments = _make_two_segments()
        # Use model_construct to bypass the model_validator
        unit = TeachingUnit.model_construct(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=segments[0].start_word,
            end_word=segments[-1].end_word,
            text_snippet=_TEST_TEXT[:80],
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic="شرح الوضوء وأحكامه وأدلته من السنة الشريفة",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes="should be cleared",
        )

        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segments, _TEST_TOTAL)

        assert result[0].self_containment_notes is None
        assert "V-P2-15" in caplog.text

    def test_v_p2_15_partial_without_notes_via_construct(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-15: PARTIAL + missing notes → fallback string (via model_construct)."""
        segments = _make_two_segments()
        unit = TeachingUnit.model_construct(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=segments[0].start_word,
            end_word=segments[-1].end_word,
            text_snippet=_TEST_TEXT[:80],
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic="شرح الوضوء وأحكامه وأدلته من السنة الشريفة",
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes=None,
        )

        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segments, _TEST_TOTAL)

        assert result[0].self_containment_notes == "No notes provided"
        assert "V-P2-15" in caplog.text

    def test_returns_repaired_list(self) -> None:
        """verify_units returns the (repaired) list — not None."""
        segments = _make_two_segments()
        units = [
            TeachingUnit(
                unit_index=0,
                segment_indices=[0, 1],
                start_word=segments[0].start_word,
                end_word=segments[-1].end_word,
                text_snippet=_TEST_TEXT[:80],
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
                description_arabic="شرح الوضوء وأحكامه وأدلته من السنة الشريفة",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )
        ]
        result = verify_units(units, segments, _TEST_TOTAL)
        assert result is units  # same list returned


# ═══════════════════════════════════════════════════════════════════
# Tests — run_phase2b
# ═══════════════════════════════════════════════════════════════════


class TestRunPhase2b:
    def test_happy_path(self) -> None:
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()
        classified = {chunk.chunk_id: segments}

        result = run_phase2b([chunk], classified, client, config)

        assert chunk.chunk_id in result
        assert len(result[chunk.chunk_id]) == 1

    def test_skips_chunks_not_in_classified(self) -> None:
        """Chunks that failed Phase 2a are silently skipped."""
        client = _make_mock_instructor_client()
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        result = run_phase2b([chunk], {}, client, config)

        assert result == {}
        # Client should not have been called
        client.chat.completions.create.assert_not_called()

    def test_retry_on_api_error(self) -> None:
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(
            side_effect=[RuntimeError("timeout"), er]
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with patch("engines.excerpting.src.phase2_group.time.sleep"):
            result = run_phase2b([chunk], {chunk.chunk_id: segments}, client, config)

        assert chunk.chunk_id in result

    def test_all_retries_exhausted(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        segments = _make_two_segments()
        client = _make_mock_instructor_client(
            side_effect=RuntimeError("API down")
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with (
            patch("engines.excerpting.src.phase2_group.time.sleep"),
            caplog.at_level(logging.ERROR),
        ):
            result = run_phase2b(
                [chunk], {chunk.chunk_id: segments}, client, config
            )

        assert chunk.chunk_id not in result
        assert ExcerptingErrorCodes.EX_C_002 in caplog.text

    def test_classification_preserved_across_retries(self) -> None:
        """Retry reuses classification — does NOT re-classify."""
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(
            side_effect=[RuntimeError("fail"), er]
        )
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with patch("engines.excerpting.src.phase2_group.time.sleep"):
            run_phase2b(
                [chunk], {chunk.chunk_id: segments}, client, config
            )

        # Both calls used the same segments (canonical offsets)
        for c in client.chat.completions.create.call_args_list:
            user_msg = c.kwargs["messages"][1]["content"]
            assert "<classified_segments>" in user_msg

    def test_empty_classified_dict(self) -> None:
        client = _make_mock_instructor_client()
        config = ExcerptingConfig()
        chunk = _make_test_chunk()
        result = run_phase2b([chunk], {}, client, config)
        assert result == {}

    def test_telemetry_logging(self, caplog: pytest.LogCaptureFixture) -> None:
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        with caplog.at_level(logging.INFO):
            run_phase2b([chunk], {chunk.chunk_id: segments}, client, config)

        assert "Phase 2b group" in caplog.text
        assert "attempt=1" in caplog.text

    def test_trace_context_chunk_id_set_per_chunk(self) -> None:
        """L-001 regression: trace_context['chunk_id'] set before each LLM call."""
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        captured_chunk_ids: list[str | None] = []
        trace_context: dict[str, Any] = {
            "semantic_phase": "grouping",
            "chunk_id": None,
        }

        def capture_side_effect(**kwargs: Any) -> Any:
            captured_chunk_ids.append(trace_context.get("chunk_id"))
            return er

        client = _make_mock_instructor_client()
        client.chat.completions.create.side_effect = capture_side_effect
        config = ExcerptingConfig()
        c1 = _make_test_chunk(chunk_id="chunk_alpha", div_id="chunk_alpha")
        c2 = _make_test_chunk(chunk_id="chunk_beta", div_id="chunk_beta")
        classified = {
            "chunk_alpha": segments,
            "chunk_beta": segments,
        }

        result = run_phase2b(
            [c1, c2], classified, client, config, trace_context=trace_context
        )

        assert "chunk_alpha" in result
        assert "chunk_beta" in result
        # Each LLM call should have seen its chunk's ID
        assert captured_chunk_ids == ["chunk_alpha", "chunk_beta"]
        # After completion, chunk_id should be reset
        assert trace_context["chunk_id"] is None

    def test_trace_context_none_is_safe(self) -> None:
        """Passing trace_context=None (default) does not break run_phase2b."""
        segments = _make_two_segments()
        er = _make_valid_extraction_result(segments)
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = _make_test_chunk()

        result = run_phase2b(
            [chunk], {chunk.chunk_id: segments}, client, config, trace_context=None
        )
        assert chunk.chunk_id in result
