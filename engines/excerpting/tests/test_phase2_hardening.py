"""Phase 2 edge case and hardening tests.

Tests deterministic offset normalization, snippet matching cascades,
segment/unit invariant validation, and orchestrator retry logic under
adversarial conditions. No real LLM calls — all mocked.

Categories:
  1. Token-char mapping with complex whitespace
  2. Char-to-token index boundary conditions
  3. Strip text combined transformations
  4. Snippet position cascade edge cases
  5. Normalize offsets boundary/adversarial cases
  6. Segment invariant violation patterns (I-CS-*)
  7. Unit invariant violation patterns (I-TU-*)
  8. Unit auto-repair combinations (V-P2-14, V-P2-15)
  9. Orchestrator mixed error recovery (run_phase2a, run_phase2b)
  10. Cross-cutting: build_segment_summary edge cases
  11. ZWNJ character in offset normalization
  12. Snippet at exact boundary between tokens
  13. Single segment classification (run_phase2a flow)
  14. Grouping with single unit covering all segments
  15. DD-S2-8: ValidationError does NOT append error feedback
  16. V-P2-14: Wildly wrong offsets (off by >100 words)
  17. V-P2-15: All three containment levels with edge cases
  18. Max token computation exact boundary values
"""

from __future__ import annotations

import logging
from typing import Any
from unittest.mock import patch

import pytest
from pydantic import ValidationError

from engines.excerpting.contracts import (
    ClassificationResult,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExtractionResult,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
    validate_cs_invariants,
    validate_tu_invariants,
)
from engines.excerpting.src.phase2_classify import (
    _build_classify_user_message,
    _build_token_char_map,
    _char_to_token_index,
    _compute_classify_max_tokens,
    _find_snippet_position,
    _strip_text,
    normalize_offsets,
    run_phase2a,
)
from engines.excerpting.src.phase2_group import (
    _build_segment_summary,
    run_phase2b,
    verify_units,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_classified_segment,
    _make_mock_instructor_client,
    _make_classification_result,
    _make_teaching_unit,
)


# ═══════════════════════════════════════════════════════════════════
# Shared fixtures
# ═══════════════════════════════════════════════════════════════════

# Longer text with diacritics for cascade tests
_DIACRITIZED_TEXT = (
    "فَعَلَ الخَيْرَ وَجَاهَدَ فِي سَبِيلِ اللهِ "
    "وَصَلَّى رَكْعَتَيْنِ قَبْلَ الفَجْرِ"
)
_DIACRITIZED_TOKENS = _DIACRITIZED_TEXT.split()
_DIACRITIZED_TOTAL = len(_DIACRITIZED_TOKENS)


def _make_test_chunk(**overrides: Any) -> Any:
    """Shortcut: assembled chunk with customizable text."""
    text = overrides.pop("assembled_text", "بسم الله الرحمن الرحيم")
    tokens = text.split()
    defaults: dict[str, Any] = {
        "assembled_text": text,
        "word_count": len(tokens),
        "total_tokens": len(tokens),
    }
    defaults.update(overrides)
    return _make_assembled_chunk(**defaults)


def _make_segments_covering(
    total_tokens: int,
    n_segments: int,
    text: str,
) -> list[ClassifiedSegment]:
    """Build n contiguous segments covering [0, total_tokens-1]."""
    tokens = text.split()
    segs: list[ClassifiedSegment] = []
    for i in range(n_segments):
        start = (total_tokens * i) // n_segments
        if i < n_segments - 1:
            end = (total_tokens * (i + 1)) // n_segments - 1
        else:
            end = total_tokens - 1
        # Snippet: first word of this segment's range
        snippet = tokens[start] if start < len(tokens) else tokens[-1]
        segs.append(
            ClassifiedSegment(
                segment_index=i,
                start_word=start,
                end_word=end,
                text_snippet=snippet,
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        )
    return segs


# ═══════════════════════════════════════════════════════════════════
# 1. Token-char mapping edge cases
# ═══════════════════════════════════════════════════════════════════


class TestTokenCharMapEdgeCases:
    """Edge cases for _build_token_char_map tokenization."""

    def test_single_token_no_whitespace(self) -> None:
        """Single word with no whitespace."""
        spans = _build_token_char_map("بسم")
        assert len(spans) == 1
        assert spans[0] == (0, 3)  # بسم = 3 chars (U+0628, U+0633, U+0645)

    def test_leading_whitespace(self) -> None:
        """Leading space before first token."""
        spans = _build_token_char_map("  الله")
        assert len(spans) == 1
        assert spans[0] == (2, 6)  # الله starts at pos 2

    def test_trailing_whitespace(self) -> None:
        """Trailing space after last token — does not create phantom token."""
        spans = _build_token_char_map("الله  ")
        assert len(spans) == 1
        assert spans[0] == (0, 4)

    def test_tab_separated_tokens(self) -> None:
        """Tab character is whitespace for split()."""
        spans = _build_token_char_map("بسم\tالله")
        assert len(spans) == 2
        assert spans[0] == (0, 3)
        assert spans[1] == (4, 8)  # الله after tab

    def test_newline_separated_tokens(self) -> None:
        """Newline character is whitespace for split()."""
        spans = _build_token_char_map("بسم\nالله")
        assert len(spans) == 2
        assert spans[0] == (0, 3)
        assert spans[1] == (4, 8)

    def test_diacritized_single_token(self) -> None:
        """Token with diacritics — char positions include diacritics."""
        # فَعَلَ = ف + fatha + ع + fatha + ل + fatha = 6 chars
        text = "فَعَلَ"
        spans = _build_token_char_map(text)
        assert len(spans) == 1
        assert spans[0] == (0, len(text))

    def test_mixed_whitespace_types(self) -> None:
        """Mix of space, tab, and newline between tokens."""
        text = "أ \t\n ب"
        spans = _build_token_char_map(text)
        assert len(spans) == 2
        assert spans[0] == (0, 1)  # أ
        assert spans[1] == (5, 6)  # ب at pos 5


# ═══════════════════════════════════════════════════════════════════
# 2. Char-to-token index boundary conditions
# ═══════════════════════════════════════════════════════════════════


class TestCharToTokenIndexEdgeCases:
    """Boundary conditions for _char_to_token_index."""

    def test_single_token_at_start(self) -> None:
        """Single-token text: any char pos maps to token 0."""
        spans = [(0, 5)]
        assert _char_to_token_index(0, spans) == 0
        assert _char_to_token_index(3, spans) == 0

    def test_past_all_tokens(self) -> None:
        """char_pos beyond last token → last token index."""
        spans = [(0, 3), (4, 8)]
        assert _char_to_token_index(99, spans) == 1

    def test_exactly_at_token_end(self) -> None:
        """char_pos at token end boundary → next token."""
        spans = [(0, 3), (4, 8)]
        # pos 3 is past token 0 (end exclusive), before token 1 (start=4)
        assert _char_to_token_index(3, spans) == 1


# ═══════════════════════════════════════════════════════════════════
# 3. Strip text combined transformations
# ═══════════════════════════════════════════════════════════════════


class TestStripTextCombined:
    """_strip_text with both collapse_ws and strip_diacritics simultaneously."""

    def test_both_flags(self) -> None:
        """Combine whitespace collapse + diacritic stripping."""
        text = "فَعَلَ   الخَيْرَ"
        result, pos_map = _strip_text(
            text, collapse_ws=True, strip_diacritics=True
        )
        assert result == "فعل الخير"
        # Verify pos_map length matches result length
        assert len(pos_map) == len(result)

    def test_empty_input(self) -> None:
        """Empty string → empty output."""
        result, pos_map = _strip_text("", collapse_ws=True, strip_diacritics=True)
        assert result == ""
        assert pos_map == []

    def test_only_whitespace(self) -> None:
        """All whitespace → single space (collapse) or empty (no collapse)."""
        result_collapsed, _ = _strip_text("   \t\n  ", collapse_ws=True)
        assert result_collapsed == " "

    def test_only_diacritics(self) -> None:
        """All diacritics → empty string."""
        # Fatha + Damma + Kasra = 3 diacritics
        text = "\u064E\u064F\u0650"
        result, pos_map = _strip_text(text, strip_diacritics=True)
        assert result == ""
        assert pos_map == []

    def test_pos_map_accuracy_with_diacritics(self) -> None:
        """Position map correctly skips diacritic positions."""
        # فَ = pos 0 (ف), pos 1 (fatha)
        text = "فَ"
        result, pos_map = _strip_text(text, strip_diacritics=True)
        assert result == "ف"
        assert pos_map == [0]  # maps to original pos 0


# ═══════════════════════════════════════════════════════════════════
# 4. Snippet position cascade edge cases
# ═══════════════════════════════════════════════════════════════════


class TestSnippetPositionCascade:
    """Edge cases in the 3-step matching cascade."""

    def test_search_start_at_end_of_text(self) -> None:
        """search_start == len(text) → snippet not found."""
        text = "بسم الله الرحمن"
        with pytest.raises(ValueError, match="Snippet not found"):
            _find_snippet_position("الله", text, len(text))

    def test_single_char_arabic_snippet(self) -> None:
        """Single Arabic character snippet found via exact match."""
        text = "أ ب ت ث"
        pos, diacritic = _find_snippet_position("ت", text, 0)
        assert pos == 4  # ت is at position 4
        assert diacritic is False

    def test_whitespace_only_difference(self) -> None:
        """Snippet differs only in whitespace → whitespace fallback."""
        text = "بسم   الله   الرحمن"
        snippet = "الله الرحمن"
        pos, diacritic = _find_snippet_position(snippet, text, 0)
        assert diacritic is False
        # Should find الله at position 6
        assert pos == 6

    def test_diacritic_only_difference(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Snippet differs only in diacritics → diacritic fallback with warning."""
        text = "وَقَالَ النَّبِيُّ"
        snippet = "وقال النبي"
        with caplog.at_level(logging.WARNING):
            pos, diacritic = _find_snippet_position(snippet, text, 0)
        assert pos == 0
        assert diacritic is True
        assert ExcerptingErrorCodes.EX_A_012 in caplog.text

    def test_empty_search_region(self) -> None:
        """search_start at very end → snippet not found."""
        text = "الحمد لله"
        with pytest.raises(ValueError, match="Snippet not found"):
            _find_snippet_position("الحمد", text, 100)

    def test_tatweel_in_text_not_stripped(self) -> None:
        """Tatweel (U+0640) is NOT in the diacritic set → not stripped.

        Text with tatweel won't match snippet without it via diacritic cascade.
        """
        text = "اللـــه"  # tatweel between lam and ha
        snippet = "الله"  # without tatweel
        with pytest.raises(ValueError, match="Snippet not found"):
            _find_snippet_position(snippet, text, 0)


# ═══════════════════════════════════════════════════════════════════
# 5. Normalize offsets boundary/adversarial cases
# ═══════════════════════════════════════════════════════════════════


class TestNormalizeOffsetsHardening:
    """Boundary and adversarial tests for normalize_offsets."""

    def test_many_segments_10(self) -> None:
        """10 segments in a medium text → all contiguous."""
        text = " ".join(f"كلمة{i}" for i in range(30))
        tokens = text.split()
        total = len(tokens)
        # Build 10 segments with snippets at evenly spaced positions
        segs: list[ClassifiedSegment] = []
        for i in range(10):
            tok_start = (total * i) // 10
            snippet = tokens[tok_start]
            segs.append(
                ClassifiedSegment(
                    segment_index=i,
                    start_word=i * 100,  # deliberately wrong LLM offsets
                    end_word=i * 100 + 50,
                    text_snippet=snippet,
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            )
        result = normalize_offsets(segs, text, total)
        assert len(result) == 10
        assert result[0].start_word == 0
        assert result[-1].end_word == total - 1
        # Verify contiguity
        for j in range(1, len(result)):
            assert result[j].start_word == result[j - 1].end_word + 1

    def test_all_diacritized_text_exact_snippets(self) -> None:
        """Fully diacritized text with exact snippets → no fallback needed."""
        text = _DIACRITIZED_TEXT
        snippet = text[:50]  # first 50 chars
        segs = [
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=99,
                text_snippet=snippet,
                scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
                confidence=0.95,
            )
        ]
        result = normalize_offsets(segs, text, _DIACRITIZED_TOTAL)
        assert result[0].start_word == 0
        assert result[0].end_word == _DIACRITIZED_TOTAL - 1

    def test_two_segments_diacritic_fallback(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Two segments where second snippet needs diacritic fallback."""
        text = "فَعَلَ الخَيْرَ وَأَحْسَنَ العَمَلَ"
        tokens = text.split()
        total = len(tokens)
        # First segment: exact snippet match
        seg0 = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=50,
            text_snippet=text[:10],  # exact
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        # Second segment: diacritic-stripped snippet
        # "وأحسن" without diacritics — original "وَأَحْسَنَ" in text
        seg1 = ClassifiedSegment(
            segment_index=1,
            start_word=51,
            end_word=99,
            text_snippet="وأحسن",
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.85,
        )
        with caplog.at_level(logging.WARNING):
            result = normalize_offsets([seg0, seg1], text, total)
        assert len(result) == 2
        assert result[0].start_word == 0
        assert result[-1].end_word == total - 1

    def test_single_token_text(self) -> None:
        """Text with exactly one token."""
        text = "بسم"
        segs = [
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=99,
                text_snippet="بسم",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        result = normalize_offsets(segs, text, 1)
        assert result[0].start_word == 0
        assert result[0].end_word == 0


# ═══════════════════════════════════════════════════════════════════
# 6. Segment invariant violation patterns (I-CS-*)
# ═══════════════════════════════════════════════════════════════════


class TestSegmentInvariantViolations:
    """Test that each I-CS-* invariant is properly enforced."""

    def test_i_cs_1_index_mismatch(self) -> None:
        """I-CS-1: segment_index != position → ValueError."""
        segs = [
            ClassifiedSegment(
                segment_index=1,  # should be 0
                start_word=0,
                end_word=4,
                text_snippet="بسم الله",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        with pytest.raises(ValueError, match="I-CS-1"):
            validate_cs_invariants(segs, 5)

    def test_i_cs_2_gap_between_segments(self) -> None:
        """I-CS-2: gap between segments → ValueError."""
        segs = [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=2,
                text_snippet="أ", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
            ClassifiedSegment(
                segment_index=1, start_word=4, end_word=6,  # gap at word 3
                text_snippet="ب", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
        ]
        with pytest.raises(ValueError, match="I-CS-2"):
            validate_cs_invariants(segs, 7)

    def test_i_cs_3_first_not_zero(self) -> None:
        """I-CS-3: first segment start_word != 0 → ValueError."""
        segs = [
            ClassifiedSegment(
                segment_index=0, start_word=1, end_word=4,
                text_snippet="أ", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        with pytest.raises(ValueError, match="I-CS-3"):
            validate_cs_invariants(segs, 5)

    def test_i_cs_4_last_not_total_minus_one(self) -> None:
        """I-CS-4: last segment end_word != total_tokens-1 → ValueError."""
        segs = [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=3,
                text_snippet="أ", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        with pytest.raises(ValueError, match="I-CS-4"):
            validate_cs_invariants(segs, 10)  # end_word=3 != 9

    def test_i_cs_5_no_segments_positive_tokens(self) -> None:
        """I-CS-5: empty segments with total_tokens > 0 → ValueError."""
        with pytest.raises(ValueError, match="I-CS-5"):
            validate_cs_invariants([], 5)

    def test_i_cs_5_empty_segments_zero_tokens_ok(self) -> None:
        """I-CS-5: empty segments with total_tokens = 0 → passes."""
        validate_cs_invariants([], 0)

    def test_i_cs_6_confidence_out_of_range(self) -> None:
        """I-CS-6: confidence > 1.0 → ValueError from validator."""
        with pytest.raises((ValueError, ValidationError)):
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=4,
                text_snippet="أ", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=1.5,  # out of range
            )


# ═══════════════════════════════════════════════════════════════════
# 7. Unit invariant violation patterns (I-TU-*)
# ═══════════════════════════════════════════════════════════════════


class TestUnitInvariantViolations:
    """Test that each I-TU-* invariant is properly enforced."""

    def _make_segs(self, n: int) -> list[ClassifiedSegment]:
        """Build n contiguous segments covering [0, n*5-1]."""
        return [
            ClassifiedSegment(
                segment_index=i,
                start_word=i * 5,
                end_word=i * 5 + 4,
                text_snippet="نص",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
            for i in range(n)
        ]

    def test_i_tu_1_index_mismatch(self) -> None:
        """I-TU-1: unit_index != position → ValueError."""
        segs = self._make_segs(1)
        units = [
            _make_teaching_unit(
                unit_index=5,  # should be 0
                segment_indices=[0],
                start_word=0, end_word=4,
            )
        ]
        with pytest.raises(ValueError, match="I-TU-1"):
            validate_tu_invariants(units, segs, 5)

    def test_i_tu_2_non_contiguous_indices(self) -> None:
        """I-TU-2: non-contiguous segment_indices → ValueError."""
        segs = self._make_segs(3)
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[0, 2],  # gap at 1
                start_word=0, end_word=14,
            )
        ]
        with pytest.raises(ValueError, match="I-TU-2"):
            validate_tu_invariants(units, segs, 15)

    def test_i_tu_2_empty_segment_indices(self) -> None:
        """I-TU-2: empty segment_indices → ValueError."""
        segs = self._make_segs(1)
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[],
                start_word=0, end_word=4,
            )
        ]
        with pytest.raises(ValueError, match="I-TU-2"):
            validate_tu_invariants(units, segs, 5)

    def test_i_tu_3_no_units_with_segments(self) -> None:
        """I-TU-3: no units but segments exist → ValueError."""
        segs = self._make_segs(2)
        with pytest.raises(ValueError, match="I-TU-3"):
            validate_tu_invariants([], segs, 10)

    def test_i_tu_3_segment_not_assigned(self) -> None:
        """I-TU-3: some segments not assigned to any unit → ValueError."""
        segs = self._make_segs(3)
        # Only unit covers segments [0, 1], skipping segment 2
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[0, 1],
                start_word=0, end_word=9,
            )
        ]
        with pytest.raises(ValueError, match="I-TU-3"):
            validate_tu_invariants(units, segs, 15)

    def test_i_tu_4_gap_between_units(self) -> None:
        """I-TU-4: gap in word space between units → ValueError.

        Segments must have a gap so units' start_word/end_word match
        segment boundaries (I-TU-5 passes) but word-space gap triggers I-TU-4.
        """
        # Segments with a gap: seg 0 ends at 4, seg 1 starts at 6
        segs = [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=4,
                text_snippet="نص", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
            ClassifiedSegment(
                segment_index=1, start_word=6, end_word=9,
                text_snippet="نص", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
        ]
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[0],
                start_word=0, end_word=4,
            ),
            _make_teaching_unit(
                unit_index=1,
                segment_indices=[1],
                start_word=6, end_word=9,
            ),
        ]
        with pytest.raises(ValueError, match="I-TU-4"):
            validate_tu_invariants(units, segs, 10)

    def test_i_tu_9_primary_function_not_in_segments(self) -> None:
        """I-TU-9: primary_function not in constituent segments → ValueError."""
        segs = self._make_segs(1)  # all DEFINITION
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[0],
                start_word=0, end_word=4,
                primary_function=ScholarlyFunction.EVIDENCE_HADITH,  # not in segs
            )
        ]
        with pytest.raises(ValueError, match="I-TU-9"):
            validate_tu_invariants(units, segs, 5)

    def test_valid_two_units_covering_all(self) -> None:
        """Two units fully covering two segments → passes."""
        segs = self._make_segs(2)
        units = [
            _make_teaching_unit(
                unit_index=0,
                segment_indices=[0],
                start_word=0, end_word=4,
            ),
            _make_teaching_unit(
                unit_index=1,
                segment_indices=[1],
                start_word=5, end_word=9,
            ),
        ]
        validate_tu_invariants(units, segs, 10)  # no exception


# ═══════════════════════════════════════════════════════════════════
# 8. Unit auto-repair combinations (V-P2-14, V-P2-15)
# ═══════════════════════════════════════════════════════════════════


class TestVerifyUnitsAutoRepair:
    """verify_units auto-repair edge cases."""

    def _make_segs_and_chunk(
        self,
    ) -> tuple[list[ClassifiedSegment], int]:
        """Two contiguous segments, total=10 tokens."""
        segs = [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=4,
                text_snippet="نص اختبار",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
            ClassifiedSegment(
                segment_index=1, start_word=5, end_word=9,
                text_snippet="فقه إسلامي",
                scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
                confidence=0.85,
            ),
        ]
        return segs, 10

    def test_v_p2_14_both_offsets_wrong(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-14: both start_word and end_word wrong → both derived."""
        segs, total = self._make_segs_and_chunk()
        unit = TeachingUnit(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=100,  # wrong
            end_word=200,  # wrong
            text_snippet="نص اختبار" + " " * 70,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic="تعريف واستدلال بحديث نبوي شريف في الفقه",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, total)
        assert result[0].start_word == 0  # derived from seg 0
        assert result[0].end_word == 9  # derived from seg 1
        assert caplog.text.count("V-P2-14") == 2  # both logged

    def test_v_p2_14_correct_offsets_not_warned(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-14: correct offsets → no warning logged."""
        segs, total = self._make_segs_and_chunk()
        unit = TeachingUnit(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=0,
            end_word=9,
            text_snippet="نص اختبار" + " " * 70,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic="تعريف واستدلال بحديث نبوي شريف في الفقه",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        with caplog.at_level(logging.WARNING):
            verify_units([unit], segs, total)
        assert "V-P2-14" not in caplog.text

    def test_v_p2_15_dependent_without_notes(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """V-P2-15: DEPENDENT + no notes → auto-fill 'No notes provided'."""
        segs, total = self._make_segs_and_chunk()
        unit = TeachingUnit.model_construct(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=0,
            end_word=9,
            text_snippet="نص اختبار" + " " * 70,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic="تعريف واستدلال بحديث نبوي شريف في الفقه",
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes=None,  # missing for DEPENDENT
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, total)
        assert result[0].self_containment_notes == "No notes provided"
        assert "V-P2-15" in caplog.text

    def test_v_p2_14_out_of_range_segment_raises(self) -> None:
        """V-P2-14: segment_indices out of range → ValueError."""
        segs, total = self._make_segs_and_chunk()
        unit = TeachingUnit.model_construct(
            unit_index=0,
            segment_indices=[0, 5],  # index 5 doesn't exist
            start_word=0,
            end_word=9,
            text_snippet="نص" + " " * 78,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[],
            description_arabic="تعريف واستدلال بحديث نبوي شريف في الفقه",
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        with pytest.raises(ValueError, match="V-P2-14"):
            verify_units([unit], segs, total)


# ═══════════════════════════════════════════════════════════════════
# 9. Orchestrator mixed error recovery
# ═══════════════════════════════════════════════════════════════════


class TestRunPhase2aMixedErrors:
    """run_phase2a edge cases with mixed error types."""

    _TEXT = "الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين"
    _TOKENS = _TEXT.split()
    _TOTAL = len(_TOKENS)

    def _chunk(self, **kw: Any) -> Any:
        defaults = {
            "assembled_text": self._TEXT,
            "word_count": self._TOTAL,
            "total_tokens": self._TOTAL,
        }
        defaults.update(kw)
        return _make_assembled_chunk(**defaults)

    def test_validation_then_normalize_then_success(self) -> None:
        """ValidationError → normalization error → success on 3rd attempt."""
        good_cr = _make_classification_result(self._TEXT, n_segments=1)
        bad_snippet_cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=10,
                    text_snippet="نص لا يوجد في الأصل أبدا",
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ],
            total_segments=1,
        )
        client = _make_mock_instructor_client(
            side_effect=[
                ValidationError.from_exception_data(
                    title="ClassificationResult",
                    line_errors=[{
                        "type": "missing",
                        "loc": ("segments",),
                        "input": {},
                        "ctx": {},
                    }],
                ),
                bad_snippet_cr,  # normalize will fail
                good_cr,  # success
            ]
        )
        config = ExcerptingConfig()
        chunk = self._chunk()
        result = run_phase2a([chunk], client, config)
        assert chunk.chunk_id in result

    def test_multiple_chunks_partial_success(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Two chunks: first succeeds, second fails all retries."""
        good_cr = _make_classification_result(self._TEXT, n_segments=1)
        client = _make_mock_instructor_client(
            side_effect=[
                good_cr,  # chunk_a succeeds
                RuntimeError("fail"),  # chunk_b attempt 1
                RuntimeError("fail"),  # chunk_b attempt 2
                RuntimeError("fail"),  # chunk_b attempt 3
            ]
        )
        config = ExcerptingConfig()
        chunk_a = self._chunk(chunk_id="chunk_a", div_id="chunk_a")
        chunk_b = self._chunk(chunk_id="chunk_b", div_id="chunk_b")

        with (
            patch("engines.excerpting.src.phase2_classify.time.sleep"),
            caplog.at_level(logging.ERROR),
        ):
            result = run_phase2a([chunk_a, chunk_b], client, config)

        assert "chunk_a" in result
        assert "chunk_b" not in result
        assert "FAILED" in caplog.text


class TestRunPhase2bMixedErrors:
    """run_phase2b edge cases with mixed error types."""

    _TEXT = "الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين"
    _TOKENS = _TEXT.split()
    _TOTAL = len(_TOKENS)

    def _chunk(self, **kw: Any) -> Any:
        defaults = {
            "assembled_text": self._TEXT,
            "word_count": self._TOTAL,
            "total_tokens": self._TOTAL,
        }
        defaults.update(kw)
        return _make_assembled_chunk(**defaults)

    def _segs(self) -> list[ClassifiedSegment]:
        """Single segment covering all tokens."""
        return [
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=self._TOTAL - 1,
                text_snippet=self._TEXT[:50],
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]

    def _good_er(self, segs: list[ClassifiedSegment]) -> ExtractionResult:
        return ExtractionResult(
            teaching_units=[
                TeachingUnit(
                    unit_index=0,
                    segment_indices=[0],
                    start_word=0,
                    end_word=self._TOTAL - 1,
                    text_snippet=self._TEXT[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[],
                    description_arabic="بيان الحمد لله وأسمائه الحسنى وصفاته العلى",
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
            ],
            total_units=1,
            notes=None,
        )

    def test_verify_failure_then_success(self) -> None:
        """First grouping violates invariant → retry → success."""
        segs = self._segs()
        # Bad ER: unit references non-existent segment index
        bad_er = ExtractionResult(
            teaching_units=[
                TeachingUnit.model_construct(
                    unit_index=0,
                    segment_indices=[0, 1],  # seg 1 doesn't exist
                    start_word=0,
                    end_word=self._TOTAL - 1,
                    text_snippet=self._TEXT[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[],
                    description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات",
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
            ],
            total_units=1,
            notes=None,
        )
        good_er = self._good_er(segs)
        client = _make_mock_instructor_client(side_effect=[bad_er, good_er])
        config = ExcerptingConfig()
        chunk = self._chunk()

        result = run_phase2b([chunk], {chunk.chunk_id: segs}, client, config)
        assert chunk.chunk_id in result

    def test_multiple_chunks_mixed_classified(self) -> None:
        """Three chunks: one not in classified, one succeeds, one fails."""
        segs = self._segs()
        good_er = self._good_er(segs)
        client = _make_mock_instructor_client(
            side_effect=[
                good_er,  # chunk_b succeeds
                RuntimeError("fail"), RuntimeError("fail"), RuntimeError("fail"),
            ]
        )
        config = ExcerptingConfig()
        chunk_a = self._chunk(chunk_id="chunk_a", div_id="chunk_a")
        chunk_b = self._chunk(chunk_id="chunk_b", div_id="chunk_b")
        chunk_c = self._chunk(chunk_id="chunk_c", div_id="chunk_c")

        classified = {
            # chunk_a NOT in classified → skipped
            "chunk_b": segs,
            "chunk_c": segs,
        }

        with patch("engines.excerpting.src.phase2_group.time.sleep"):
            result = run_phase2b(
                [chunk_a, chunk_b, chunk_c], classified, client, config
            )

        assert "chunk_a" not in result  # skipped (not classified)
        assert "chunk_b" in result  # succeeded
        assert "chunk_c" not in result  # all retries failed

    def test_v_p2_18_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """V-P2-18: total_units mismatch → warning logged, actual used."""
        segs = self._segs()
        er = self._good_er(segs)
        # Tamper total_units
        bad_er = ExtractionResult(
            teaching_units=er.teaching_units,
            total_units=99,
            notes=None,
        )
        client = _make_mock_instructor_client(return_value=bad_er)
        config = ExcerptingConfig()
        chunk = self._chunk()

        with caplog.at_level(logging.WARNING):
            result = run_phase2b([chunk], {chunk.chunk_id: segs}, client, config)

        assert chunk.chunk_id in result
        assert "V-P2-18" in caplog.text


# ═══════════════════════════════════════════════════════════════════
# 10. Cross-cutting: build_segment_summary edge cases
# ═══════════════════════════════════════════════════════════════════


class TestBuildSegmentSummaryEdgeCases:
    """Edge cases in the segment summary format for group prompts."""

    def test_empty_segments(self) -> None:
        """No segments → empty string."""
        assert _build_segment_summary([]) == ""

    def test_arabic_diacritics_preserved_in_snippet(self) -> None:
        """Diacritics in text_snippet preserved verbatim in summary."""
        seg = _make_classified_segment(
            text_snippet="فَعَلَ الخَيْرَ",
            scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
        )
        summary = _build_segment_summary([seg])
        assert "فَعَلَ الخَيْرَ" in summary

    def test_many_segments_output(self) -> None:
        """10 segments → 10 lines in output."""
        segs = [
            _make_classified_segment(
                segment_index=i,
                start_word=i * 5,
                end_word=i * 5 + 4,
            )
            for i in range(10)
        ]
        summary = _build_segment_summary(segs)
        lines = summary.strip().split("\n")
        assert len(lines) == 10
        assert "Segment 0:" in lines[0]
        assert "Segment 9:" in lines[9]


# ═══════════════════════════════════════════════════════════════════
# 11. ZWNJ character in offset normalization
# ═══════════════════════════════════════════════════════════════════


class TestZWNJCharacterHandling:
    """ZWNJ (U+200C) is a zero-width non-joiner used in Arabic/Persian text.

    Python split() does NOT split on ZWNJ — it is a non-whitespace character.
    Tokens containing ZWNJ have more chars than visible glyphs.
    """

    def test_token_map_with_zwnj_inside_token(self) -> None:
        """Token with ZWNJ: char count includes the invisible character."""
        # ZWNJ between miim and alif-lam: "بسم‌الله" is one token for split()
        text = "بسم\u200cالله الرحمن"
        spans = _build_token_char_map(text)
        assert len(spans) == 2
        # First token: بسم (3) + ZWNJ (1) + الله (4) = 8 chars
        assert spans[0] == (0, 8)
        assert spans[1][0] == 9  # الرحمن starts after space

    def test_snippet_with_zwnj_exact_match(self) -> None:
        """Snippet containing ZWNJ matches exactly in assembled text."""
        text = "قال\u200cالنبي صلى الله عليه وسلم"
        snippet = "قال\u200cالنبي"
        pos, diacritic = _find_snippet_position(snippet, text, 0)
        assert pos == 0
        assert diacritic is False

    def test_normalize_offsets_with_zwnj_token(self) -> None:
        """Full normalization pipeline with ZWNJ in text — single segment."""
        text = "بسم\u200cالله الرحمن الرحيم"
        tokens = text.split()
        total = len(tokens)
        snippet = text[:10]
        segs = [
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=99,
                text_snippet=snippet,
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        result = normalize_offsets(segs, text, total)
        assert result[0].start_word == 0
        assert result[0].end_word == total - 1

    def test_zwnj_two_segment_boundary(self) -> None:
        """Two segments where ZWNJ-containing token is an anchor."""
        text = "أول ثاني\u200cالكلمة ثالث رابع"
        tokens = text.split()
        total = len(tokens)
        assert total == 4

        seg0 = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=50,
            text_snippet="أول",
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        seg1 = ClassifiedSegment(
            segment_index=1,
            start_word=51,
            end_word=99,
            text_snippet="ثاني\u200cالكلمة",
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.85,
        )
        result = normalize_offsets([seg0, seg1], text, total)
        assert result[0].start_word == 0
        assert result[0].end_word == 0  # Only "أول"
        assert result[1].start_word == 1
        assert result[1].end_word == total - 1


# ═══════════════════════════════════════════════════════════════════
# 12. Snippet at exact boundary between tokens
# ═══════════════════════════════════════════════════════════════════


class TestSnippetAtTokenBoundary:
    """Snippets that start at or near whitespace between tokens."""

    def test_char_to_token_in_whitespace_gap(self) -> None:
        """char_pos in whitespace between tokens → returns next token."""
        # "أ ب ت" → spans at (0,1), (2,3), (4,5)
        spans = [(0, 1), (2, 3), (4, 5)]
        assert _char_to_token_index(1, spans) == 1
        assert _char_to_token_index(3, spans) == 2

    def test_snippet_at_exact_token_start(self) -> None:
        """Snippet matching at the exact character start of a token."""
        text = "أول ثاني ثالث رابع خامس"
        tokens = text.split()
        total = len(tokens)

        seg0 = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=50,
            text_snippet="أول",
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        seg1 = ClassifiedSegment(
            segment_index=1,
            start_word=51,
            end_word=99,
            text_snippet="ثالث",
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.85,
        )
        result = normalize_offsets([seg0, seg1], text, total)
        assert result[0].start_word == 0
        assert result[0].end_word == 1  # أول + ثاني
        assert result[1].start_word == 2
        assert result[1].end_word == total - 1

    def test_snippet_matching_last_token(self) -> None:
        """Last segment snippet anchors at the very last token."""
        text = "أ ب ت ث ج"
        tokens = text.split()
        total = len(tokens)

        seg0 = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=50,
            text_snippet="أ",
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        seg1 = ClassifiedSegment(
            segment_index=1,
            start_word=51,
            end_word=99,
            text_snippet="ج",
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.85,
        )
        result = normalize_offsets([seg0, seg1], text, total)
        assert result[0].start_word == 0
        assert result[0].end_word == 3  # أ ب ت ث
        assert result[1].start_word == 4  # ج
        assert result[1].end_word == 4  # single token segment


# ═══════════════════════════════════════════════════════════════════
# 13. Single segment classification (run_phase2a flow)
# ═══════════════════════════════════════════════════════════════════


class TestSingleSegmentClassification:
    """run_phase2a with single segment covering all text."""

    _TEXT = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
    _TOKENS = _TEXT.split()
    _TOTAL = len(_TOKENS)

    def test_single_segment_covers_all_tokens(self) -> None:
        """Single segment from LLM → normalized to [0, total-1]."""
        cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=999,  # LLM overshoot
                    text_snippet=self._TEXT[:50],
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.95,
                )
            ],
            total_segments=1,
        )
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self._TEXT,
            word_count=self._TOTAL,
            total_tokens=self._TOTAL,
        )
        result = run_phase2a([chunk], client, config)
        assert chunk.chunk_id in result
        segments = result[chunk.chunk_id]
        assert len(segments) == 1
        assert segments[0].start_word == 0
        assert segments[0].end_word == self._TOTAL - 1

    def test_single_segment_preserves_metadata(self) -> None:
        """Function and confidence preserved through normalization."""
        cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=50,
                    text_snippet=self._TEXT[:50],
                    scholarly_function=ScholarlyFunction.NARRATION,
                    confidence=0.72,
                )
            ],
            total_segments=1,
        )
        client = _make_mock_instructor_client(return_value=cr)
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self._TEXT,
            word_count=self._TOTAL,
            total_tokens=self._TOTAL,
        )
        result = run_phase2a([chunk], client, config)
        seg = result[chunk.chunk_id][0]
        assert seg.scholarly_function == ScholarlyFunction.NARRATION
        assert seg.confidence == 0.72


# ═══════════════════════════════════════════════════════════════════
# 14. Grouping with single unit covering all segments
# ═══════════════════════════════════════════════════════════════════


class TestSingleUnitGrouping:
    """run_phase2b with single unit grouping all classified segments."""

    _TEXT = (
        "الوضوء هو استعمال الماء في أعضاء مخصوصة بنية التطهر "
        "وقد قال النبي صلى الله عليه وسلم لا يقبل الله صلاة أحدكم"
    )
    _TOKENS = _TEXT.split()
    _TOTAL = len(_TOKENS)

    def _chunk(self) -> Any:
        return _make_assembled_chunk(
            assembled_text=self._TEXT,
            word_count=self._TOTAL,
            total_tokens=self._TOTAL,
        )

    def _three_segments(self) -> list[ClassifiedSegment]:
        """Three contiguous segments covering all tokens."""
        mid1 = self._TOTAL // 3
        mid2 = (self._TOTAL * 2) // 3
        return [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=mid1 - 1,
                text_snippet=self._TEXT[:50],
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
            ClassifiedSegment(
                segment_index=1, start_word=mid1, end_word=mid2 - 1,
                text_snippet="في",
                scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
                confidence=0.85,
            ),
            ClassifiedSegment(
                segment_index=2, start_word=mid2, end_word=self._TOTAL - 1,
                text_snippet="لا",
                scholarly_function=ScholarlyFunction.RULE_STATEMENT,
                confidence=0.8,
            ),
        ]

    def test_single_unit_groups_three_segments(self) -> None:
        """One unit covering [0,1,2] → passes all verification."""
        segs = self._three_segments()
        er = ExtractionResult(
            teaching_units=[
                TeachingUnit(
                    unit_index=0,
                    segment_indices=[0, 1, 2],
                    start_word=segs[0].start_word,
                    end_word=segs[-1].end_word,
                    text_snippet=self._TEXT[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[
                        ScholarlyFunction.EVIDENCE_HADITH,
                        ScholarlyFunction.RULE_STATEMENT,
                    ],
                    description_arabic=(
                        "تعريف الوضوء وحكمه وأدلته من السنة النبوية الشريفة"
                    ),
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
            ],
            total_units=1,
            notes=None,
        )
        client = _make_mock_instructor_client(return_value=er)
        config = ExcerptingConfig()
        chunk = self._chunk()

        result = run_phase2b([chunk], {chunk.chunk_id: segs}, client, config)
        assert chunk.chunk_id in result
        units = result[chunk.chunk_id]
        assert len(units) == 1
        assert units[0].segment_indices == [0, 1, 2]
        assert units[0].start_word == 0
        assert units[0].end_word == self._TOTAL - 1


# ═══════════════════════════════════════════════════════════════════
# 15. DD-S2-8: ValidationError does NOT append error feedback
# ═══════════════════════════════════════════════════════════════════


class TestDDS28NoFeedbackOnValidationError:
    """DD-S2-8: Schema validation errors are structural, not content.

    After a ValidationError, error_feedback must be None — no snippet
    or coverage feedback appended to the retry prompt.
    """

    _TEXT = "الحمد لله رب العالمين الرحمن الرحيم مالك يوم الدين"
    _TOKENS = _TEXT.split()
    _TOTAL = len(_TOKENS)

    def test_classify_retry_no_feedback_after_validation_error(self) -> None:
        """After ValidationError in classify, retry user message has no feedback."""
        good_cr = ClassificationResult(
            segments=[
                ClassifiedSegment(
                    segment_index=0,
                    start_word=0,
                    end_word=50,
                    text_snippet=self._TEXT[:50],
                    scholarly_function=ScholarlyFunction.DEFINITION,
                    confidence=0.9,
                )
            ],
            total_segments=1,
        )
        client = _make_mock_instructor_client(
            side_effect=[
                ValidationError.from_exception_data(
                    title="ClassificationResult",
                    line_errors=[{
                        "type": "missing",
                        "loc": ("segments",),
                        "input": {},
                        "ctx": {},
                    }],
                ),
                good_cr,
            ]
        )
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self._TEXT,
            word_count=self._TOTAL,
            total_tokens=self._TOTAL,
        )
        result = run_phase2a([chunk], client, config)
        assert chunk.chunk_id in result

        # Key: second call has NO error feedback in user message
        second_call = client.chat.completions.create.call_args_list[1]
        user_msg = second_call.kwargs["messages"][1]["content"]
        assert "text_snippet that could not be located" not in user_msg
        assert "coverage invariant" not in user_msg
        # User message is the clean DR28 message (no feedback appended)
        assert user_msg == _build_classify_user_message(chunk)

    def test_group_retry_no_feedback_after_validation_error(self) -> None:
        """After ValidationError in group, retry user message has no feedback."""
        segs = [
            ClassifiedSegment(
                segment_index=0,
                start_word=0,
                end_word=self._TOTAL - 1,
                text_snippet=self._TEXT[:50],
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            )
        ]
        good_er = ExtractionResult(
            teaching_units=[
                TeachingUnit(
                    unit_index=0,
                    segment_indices=[0],
                    start_word=0,
                    end_word=self._TOTAL - 1,
                    text_snippet=self._TEXT[:80],
                    primary_function=ScholarlyFunction.DEFINITION,
                    secondary_functions=[],
                    description_arabic=(
                        "بيان الحمد لله وأسمائه الحسنى وصفاته العلى"
                    ),
                    self_containment=SelfContainmentLevel.FULL,
                    self_containment_notes=None,
                )
            ],
            total_units=1,
            notes=None,
        )
        client = _make_mock_instructor_client(
            side_effect=[
                ValidationError.from_exception_data(
                    title="ExtractionResult",
                    line_errors=[{
                        "type": "missing",
                        "loc": ("teaching_units",),
                        "input": {},
                        "ctx": {},
                    }],
                ),
                good_er,
            ]
        )
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self._TEXT,
            word_count=self._TOTAL,
            total_tokens=self._TOTAL,
        )
        result = run_phase2b([chunk], {chunk.chunk_id: segs}, client, config)
        assert chunk.chunk_id in result

        # Key: second call has NO invariant feedback
        second_call = client.chat.completions.create.call_args_list[1]
        user_msg = second_call.kwargs["messages"][1]["content"]
        assert "coverage invariant" not in user_msg
        assert "violated" not in user_msg


# ═══════════════════════════════════════════════════════════════════
# 16. V-P2-14: Wildly wrong offsets (off by >100 words)
# ═══════════════════════════════════════════════════════════════════


class TestVP214WildlyWrongOffsets:
    """V-P2-14: LLM produces offsets off by >100 words from derived values.

    Even with extreme discrepancies, verify_units must silently correct
    to the derived values from constituent segments.
    """

    def _make_segs(self) -> list[ClassifiedSegment]:
        return [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=4,
                text_snippet="نص", scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
            ClassifiedSegment(
                segment_index=1, start_word=5, end_word=9,
                text_snippet="فقه",
                scholarly_function=ScholarlyFunction.EVIDENCE_HADITH,
                confidence=0.85,
            ),
        ]

    def test_offsets_off_by_5000(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """start_word=5000, end_word=10000 but derived is 0, 9."""
        segs = self._make_segs()
        unit = TeachingUnit(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=5000,
            end_word=10000,
            text_snippet="نص اختبار" + " " * 70,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic=(
                "تعريف واستدلال بحديث نبوي شريف في الفقه"
            ),
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)

        assert result[0].start_word == 0
        assert result[0].end_word == 9
        assert caplog.text.count("V-P2-14") == 2

    def test_start_off_by_200_end_correct(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Only start_word wildly wrong, end_word correct → one warning."""
        segs = self._make_segs()
        unit = TeachingUnit(
            unit_index=0,
            segment_indices=[0, 1],
            start_word=200,
            end_word=9,
            text_snippet="نص اختبار" + " " * 70,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[ScholarlyFunction.EVIDENCE_HADITH],
            description_arabic=(
                "تعريف واستدلال بحديث نبوي شريف في الفقه"
            ),
            self_containment=SelfContainmentLevel.FULL,
            self_containment_notes=None,
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)

        assert result[0].start_word == 0
        assert result[0].end_word == 9
        # Only start_word warned
        assert caplog.text.count("V-P2-14") == 1


# ═══════════════════════════════════════════════════════════════════
# 17. V-P2-15: All three containment levels with edge cases
# ═══════════════════════════════════════════════════════════════════


class TestVP215AllContainmentLevels:
    """V-P2-15: Self-containment notes consistency for FULL, PARTIAL, DEPENDENT.

    Uses model_construct to bypass the model_validator so we can create
    intentionally inconsistent state for the auto-repair to fix.
    """

    def _make_segs(self) -> list[ClassifiedSegment]:
        return [
            ClassifiedSegment(
                segment_index=0, start_word=0, end_word=9,
                text_snippet="نص",
                scholarly_function=ScholarlyFunction.DEFINITION,
                confidence=0.9,
            ),
        ]

    def _make_unit(
        self,
        containment: SelfContainmentLevel,
        notes: str | None,
    ) -> TeachingUnit:
        """Build unit via model_construct to bypass validator."""
        return TeachingUnit.model_construct(
            unit_index=0,
            segment_indices=[0],
            start_word=0,
            end_word=9,
            text_snippet="نص اختبار للمحتوى العلمي" + " " * 55,
            primary_function=ScholarlyFunction.DEFINITION,
            secondary_functions=[],
            description_arabic=(
                "تعريف واستدلال بحديث نبوي شريف في الفقه"
            ),
            self_containment=containment,
            self_containment_notes=notes,
        )

    def test_full_without_notes_passes(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """FULL + no notes → normal case, no warning."""
        segs = self._make_segs()
        unit = self._make_unit(SelfContainmentLevel.FULL, None)
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert result[0].self_containment_notes is None
        assert "V-P2-15" not in caplog.text

    def test_full_with_notes_cleared(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """FULL + notes → notes set to None + warning."""
        segs = self._make_segs()
        unit = self._make_unit(
            SelfContainmentLevel.FULL, "should be cleared"
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert result[0].self_containment_notes is None
        assert "V-P2-15" in caplog.text

    def test_partial_with_notes_passes(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """PARTIAL + notes → normal case, no warning."""
        segs = self._make_segs()
        unit = self._make_unit(
            SelfContainmentLevel.PARTIAL,
            "يحتاج لمراجعة السياق المحيط بالنص",
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert (
            result[0].self_containment_notes
            == "يحتاج لمراجعة السياق المحيط بالنص"
        )
        assert "V-P2-15" not in caplog.text

    def test_partial_without_notes_autofilled(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """PARTIAL + no notes → autofill + warning."""
        segs = self._make_segs()
        unit = self._make_unit(SelfContainmentLevel.PARTIAL, None)
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert result[0].self_containment_notes == "No notes provided"
        assert "V-P2-15" in caplog.text

    def test_dependent_with_notes_passes(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """DEPENDENT + notes → normal case, no warning."""
        segs = self._make_segs()
        unit = self._make_unit(
            SelfContainmentLevel.DEPENDENT,
            "يعتمد على تعريف سابق في الباب",
        )
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert (
            result[0].self_containment_notes
            == "يعتمد على تعريف سابق في الباب"
        )
        assert "V-P2-15" not in caplog.text

    def test_dependent_without_notes_autofilled(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """DEPENDENT + no notes → autofill + warning."""
        segs = self._make_segs()
        unit = self._make_unit(SelfContainmentLevel.DEPENDENT, None)
        with caplog.at_level(logging.WARNING):
            result = verify_units([unit], segs, 10)
        assert result[0].self_containment_notes == "No notes provided"
        assert "V-P2-15" in caplog.text


# ═══════════════════════════════════════════════════════════════════
# 18. Max token computation exact boundary values
# ═══════════════════════════════════════════════════════════════════


class TestMaxTokenBoundaryValues:
    """_compute_classify_max_tokens boundary conditions at 1500 and 4000.

    §5.5.1: <=1500 → 8192, >1500 → 32768, >4000 → 32768 with warning.
    Threshold lowered from 2000 to 1500 (2026-03-28, ibn_aqil_v3 regression).
    """

    @pytest.mark.parametrize(
        "word_count, expected_tokens, expect_warning",
        [
            (1500, 8192, False),     # exactly 1500 → 8192 (not >1500)
            (1501, 32768, False),    # just above → 32768, no warning
            (1987, 32768, False),    # ibn_aqil_v3 regression case
            (4000, 32768, False),    # exactly 4000 → 32768, no warning
            (4001, 32768, True),     # just above → 32768, with warning
        ],
    )
    def test_boundary_value(
        self,
        word_count: int,
        expected_tokens: int,
        expect_warning: bool,
        caplog: pytest.LogCaptureFixture,
    ) -> None:
        """Verify exact boundary behavior at 1500 and 4000 thresholds."""
        with caplog.at_level(logging.WARNING):
            result = _compute_classify_max_tokens(word_count)
        assert result == expected_tokens
        if expect_warning:
            assert "Untested word count range" in caplog.text
        else:
            assert "Untested word count range" not in caplog.text
