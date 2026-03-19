"""Tests for boundary continuity classifier — SPEC §4.B.8.

Covers:
  - Volume boundary → division_break (0.95)
  - Heading at next page (5 confidence levels) → section_break
  - Heading overrides punctuation (signal priority)
  - Argument flow: evidence_chain opener, no closer → mid_argument (0.90)
  - Argument flow with terminal punct → mid_argument (0.70)
  - Opener closed on same page → NOT mid_argument
  - وذهب word boundary check
  - Mid-sentence (no terminal punct, no markers) → 0.90
  - Mid-paragraph (terminal punct) → 0.75
  - ADV-026: terminal punct → NOT mid_sentence
  - Blank/image next page → unknown (0.30)
  - Connective boost adds hint
  - SPEC concrete example (lines 1184-1212)
  - Real fixture boundary spot-checks
"""

from __future__ import annotations

import pytest

from engines.normalization.contracts import (
    BoundaryContinuityType,
    ContinuityDetectionMethod,
    HeadingConfidence,
    StructuralMarkers,
)
from engines.normalization.src.boundary_continuity import (
    _check_argument_flow,
    _has_terminal_punct,
    _has_word_boundary_after,
    classify_boundary,
)
from engines.normalization.tests.conftest import (
    FIXTURES_REAL,
    _full_pipeline,
    _make_cleaned_page,
)
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer


def _markers(
    heading: bool = False,
    confidence: HeadingConfidence | None = None,
) -> StructuralMarkers:
    """Build a StructuralMarkers with heading info."""
    return StructuralMarkers(
        heading_detected=heading,
        heading_text="باب" if heading else None,
        heading_confidence=confidence,
    )


# ══════════════════════════════════════════════════════════════════════
# Priority 1: Volume boundary → division_break
# ══════════════════════════════════════════════════════════════════════


class TestVolumeBoundary:
    def test_volume_boundary_division_break(self) -> None:
        """Volume boundary → division_break at 0.95."""
        cur = _make_cleaned_page("نص الصفحة الأخيرة من المجلد الأول")
        nxt = _make_cleaned_page("نص الصفحة الأولى من المجلد الثاني")
        result = classify_boundary(cur, nxt, None, None, is_volume_boundary=True)
        assert result.type == BoundaryContinuityType.DIVISION_BREAK
        assert result.confidence == 0.95
        assert result.detection_method == ContinuityDetectionMethod.STRUCTURAL_MARKER


# ══════════════════════════════════════════════════════════════════════
# Priority 2: Heading at next page → section_break
# ══════════════════════════════════════════════════════════════════════


class TestHeadingBoundary:
    @pytest.mark.parametrize("conf,expected_score", [
        (HeadingConfidence.CONFIRMED, 0.95),
        (HeadingConfidence.HIGH, 0.95),
        (HeadingConfidence.MEDIUM, 0.85),
        (HeadingConfidence.LOW, 0.75),
        (HeadingConfidence.MINIMAL, 0.65),
    ])
    def test_heading_confidence_levels(
        self, conf: HeadingConfidence, expected_score: float,
    ) -> None:
        """All 5 confidence levels produce correct boundary confidence."""
        cur = _make_cleaned_page("نص ينتهي بنقطة.")
        nxt = _make_cleaned_page("باب الفصل الأول")
        result = classify_boundary(
            cur, nxt, None, _markers(heading=True, confidence=conf),
            is_volume_boundary=False,
        )
        assert result.type == BoundaryContinuityType.SECTION_BREAK
        assert result.confidence == expected_score

    def test_heading_overrides_punctuation(self) -> None:
        """Signal priority: heading > punctuation. Even with no terminal
        punct (which would be mid_sentence), heading wins."""
        cur = _make_cleaned_page("نص بدون نقطة في النهاية")
        nxt = _make_cleaned_page("باب جديد")
        result = classify_boundary(
            cur, nxt, None,
            _markers(heading=True, confidence=HeadingConfidence.HIGH),
            is_volume_boundary=False,
        )
        assert result.type == BoundaryContinuityType.SECTION_BREAK


# ══════════════════════════════════════════════════════════════════════
# Priority 3: Argument flow
# ══════════════════════════════════════════════════════════════════════


class TestArgumentFlow:
    def test_evidence_chain_no_closer(self) -> None:
        """Evidence opener in last 200 chars, no closer → mid_argument 0.80."""
        text = "والمسألة فيها خلاف ولنا حديث رسول الله في ذلك"
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("وهذا يدل على صحة القول")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_ARGUMENT
        assert result.confidence == 0.80
        assert result.detection_method == ContinuityDetectionMethod.ARGUMENT_FLOW

    def test_argument_with_terminal_punct(self) -> None:
        """Argument opener + terminal punct → mid_argument at 0.70."""
        text = "والمسألة فيها خلاف ولنا حديث في ذلك."
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("تتمة الكلام")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_ARGUMENT
        assert result.confidence == 0.70

    def test_opener_closed_on_same_page(self) -> None:
        """Opener + closer on same page → NOT mid_argument → falls to punct."""
        text = "ولنا في المسألة دليل واضح فثبت أنه حق."
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("مسألة أخرى")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        # Closer exists → not mid_argument → falls to mid_paragraph (terminal punct)
        assert result.type == BoundaryContinuityType.MID_PARAGRAPH

    def test_position_statement_opener(self) -> None:
        """Position statement: وذهب opener → mid_argument."""
        text = "وذهب الشافعي إلى أن الماء إذا بلغ قلتين"
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("لم يحمل خبثا")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_ARGUMENT

    def test_objection_response_opener(self) -> None:
        """Objection-response: فإن قيل opener → mid_argument."""
        text = "فإن قيل كيف يصح هذا مع ما تقدم من الأدلة"
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("قلنا الجواب عن ذلك")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_ARGUMENT

    def test_heading_overrides_argument(self) -> None:
        """Signal priority: heading > argument. Even with open argument,
        heading on next page wins."""
        text = "ولنا في المسألة حديث شريف"
        cur = _make_cleaned_page(text)
        nxt = _make_cleaned_page("باب جديد")
        result = classify_boundary(
            cur, nxt, None,
            _markers(heading=True, confidence=HeadingConfidence.CONFIRMED),
            is_volume_boundary=False,
        )
        assert result.type == BoundaryContinuityType.SECTION_BREAK


# ══════════════════════════════════════════════════════════════════════
# Word boundary checks (وذهب vs وذهبت)
# ══════════════════════════════════════════════════════════════════════


class TestWordBoundary:
    def test_wadhahaba_with_space(self) -> None:
        """وذهب followed by space → triggers (word boundary present)."""
        assert _has_word_boundary_after("وذهب الشافعي", 4) is True

    def test_wadhahabat_no_boundary(self) -> None:
        """وذهبت (she went) — no word boundary at position 4."""
        assert _has_word_boundary_after("وذهبت", 4) is False

    def test_word_at_end(self) -> None:
        """Word at end of string → boundary present."""
        assert _has_word_boundary_after("وذهب", 4) is True


# ══════════════════════════════════════════════════════════════════════
# Priority 4: Punctuation analysis
# ══════════════════════════════════════════════════════════════════════


class TestPunctuationAnalysis:
    def test_mid_sentence_no_terminal(self) -> None:
        """No terminal punct, no markers → mid_sentence 0.90."""
        cur = _make_cleaned_page("وهذا النص يستمر في الصفحة التالية")
        nxt = _make_cleaned_page("وتتمة الكلام هنا")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_SENTENCE
        assert result.confidence == 0.90

    def test_adv026_terminal_punct_not_mid_sentence(self) -> None:
        """ADV-026: terminal punct → mid_paragraph, NOT mid_sentence."""
        cur = _make_cleaned_page("وهذا الحكم واضح لا خلاف فيه.")
        nxt = _make_cleaned_page("مسألة أخرى")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_PARAGRAPH
        assert result.type != BoundaryContinuityType.MID_SENTENCE
        assert result.confidence == 0.75

    def test_arabic_question_mark(self) -> None:
        """Arabic question mark ؟ is terminal punctuation."""
        assert _has_terminal_punct("ما حكم ذلك؟") is True

    def test_arabic_semicolon(self) -> None:
        """Arabic semicolon ؛ is terminal punctuation."""
        assert _has_terminal_punct("أولا: الفعل؛") is True


# ══════════════════════════════════════════════════════════════════════
# Priority 0: Blank/image next page → unknown
# ══════════════════════════════════════════════════════════════════════


class TestBlankNextPage:
    def test_blank_next_page(self) -> None:
        """Blank next page → unknown 0.30."""
        cur = _make_cleaned_page("نص عادي.")
        nxt = _make_cleaned_page("", is_blank=True)
        result = classify_boundary(cur, nxt, None, None, is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.UNKNOWN
        assert result.confidence == 0.30

    def test_image_only_next_page(self) -> None:
        """Image-only next page → unknown 0.30."""
        cur = _make_cleaned_page("نص عادي.")
        nxt = _make_cleaned_page("", is_image_only=True)
        result = classify_boundary(cur, nxt, None, None, is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.UNKNOWN
        assert result.confidence == 0.30


# ══════════════════════════════════════════════════════════════════════
# Connective hint
# ══════════════════════════════════════════════════════════════════════


class TestConnectiveHint:
    def test_connective_wa(self) -> None:
        """Next page starts with و → continuation_hint."""
        cur = _make_cleaned_page("نص ينتهي هنا")
        nxt = _make_cleaned_page("والباقي في الصفحة التالية")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.continuation_hint is not None
        assert "و" in result.continuation_hint

    def test_connective_fa(self) -> None:
        """Next page starts with ف → continuation_hint."""
        cur = _make_cleaned_page("نص ينتهي هنا")
        nxt = _make_cleaned_page("فيكون الحكم كذا")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.continuation_hint is not None
        assert "ف" in result.continuation_hint

    def test_connective_thumma(self) -> None:
        """Next page starts with ثم → continuation_hint."""
        cur = _make_cleaned_page("نص ينتهي هنا")
        nxt = _make_cleaned_page("ثم يأتي الكلام التالي")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.continuation_hint is not None
        assert "ثم" in result.continuation_hint


# ══════════════════════════════════════════════════════════════════════
# SPEC concrete example (§4.B.8 lines 1184-1212)
# ══════════════════════════════════════════════════════════════════════


class TestSpecConcreteExample:
    def test_spec_example_mid_argument(self) -> None:
        """SPEC example: ولنا حديث...قال: → mid_argument, 0.80."""
        cur_text = (
            "واختلف العلماء في هذه المسألة على قولين "
            "ولنا حديث عائشة رضي الله عنها أن النبي "
            "صلى الله عليه وسلم قال:"
        )
        cur = _make_cleaned_page(cur_text)
        nxt = _make_cleaned_page("إنما الأعمال بالنيات فثبت ما ذهبنا إليه")
        result = classify_boundary(cur, nxt, None, _markers(), is_volume_boundary=False)
        assert result.type == BoundaryContinuityType.MID_ARGUMENT
        # No terminal punct at end → 0.80 (SPEC range max)
        assert result.confidence == 0.80


# ══════════════════════════════════════════════════════════════════════
# Real fixture spot-checks
# ══════════════════════════════════════════════════════════════════════


class TestRealFixtureSpotChecks:
    def test_01_nahw_simple_has_boundaries(self) -> None:
        """01_nahw_simple: boundary classification produces valid types."""
        htm = (FIXTURES_REAL / "01_nahw_simple" / "book.htm").read_text(encoding="utf-8")
        n = ShamelaNormalizer()
        cleaned = _full_pipeline(n, htm)
        if len(cleaned) < 2:
            pytest.skip("Need at least 2 pages")
        result = classify_boundary(
            cleaned[0], cleaned[1], None, _markers(), is_volume_boundary=False,
        )
        assert result.type in BoundaryContinuityType.__members__.values()
        assert 0.0 <= result.confidence <= 1.0

    def test_03_fiqh_has_argument_flow(self) -> None:
        """03_fiqh: at least one boundary classified as non-unknown."""
        htm = (FIXTURES_REAL / "03_fiqh" / "book.htm").read_text(encoding="utf-8")
        n = ShamelaNormalizer()
        cleaned = _full_pipeline(n, htm)
        types_found: set[BoundaryContinuityType] = set()
        for i in range(len(cleaned) - 1):
            result = classify_boundary(
                cleaned[i], cleaned[i + 1], None, _markers(),
                is_volume_boundary=False,
            )
            types_found.add(result.type)
        # Fiqh text should have at least one non-unknown boundary
        assert types_found - {BoundaryContinuityType.UNKNOWN}, (
            f"All boundaries are UNKNOWN in fiqh text: {types_found}"
        )
