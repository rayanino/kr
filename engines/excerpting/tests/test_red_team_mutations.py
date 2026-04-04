"""Red-team mutation tests for excerpting engine (FP-19, FP-20, FP-21).

These tests are derived from the owner's F7/F8 red-team test specifications
and validate that the engine catches corruption rather than silently passing it.

RT-F7-001: Diacritic injection — corrupt Arabic text, verify fail-loud.
RT-F7-002: Split/merge mutation — force alternative decisions, check detection.

Governed by: FP-5 (knowledge corruption is worst failure), FP-19 (omission
honesty), FP-20 (validation rigor — prove hard cases).
"""

from __future__ import annotations

import pytest

from engines.excerpting.contracts import (
    ExcerptingErrorCodes,
    ExcerptRecord,
    ScholarlyFunction,
    SelfContainmentLevel,
)
from engines.excerpting.src.phase3_validation import validate_excerpt

from .conftest import _make_excerpt_record


# ═══════════════════════════════════════════════════════════════════
# RT-F7-001: Diacritic Injection — Arabic text corruption detection
# ═══════════════════════════════════════════════════════════════════


class TestDiacriticInjection:
    """FP-5 + FP-19: Inject diacritic corruption into Arabic source text and
    verify that frozen-source comparison and downstream lineage fail loudly.

    Source: F7/09_red_team_tests.jsonl RT-001.
    """

    @pytest.mark.red_team
    @pytest.mark.parametrize(
        "original,corrupted,description",
        [
            pytest.param(
                "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
                "بِسْمِ اللّهِ الرَّحْمَنِ الرَّحِيمِ",
                "Removed shadda from اللَّهِ → اللّهِ (single diacritic removal)",
                id="shadda-removal",
            ),
            pytest.param(
                "يَجِبُ الصَّوْمُ عَلَى الْبَالِغِ الْعَاقِلِ",
                "يَجِبُ الصَّوْمُ عَلَي الْبَالِغِ الْعَاقِلِ",
                "Changed عَلَى to عَلَي (alef maqsura → ya, changes meaning)",
                id="alef-maqsura-swap",
            ),
            pytest.param(
                "قَالَ أَبُو حَنِيفَةَ رَحِمَهُ اللَّهُ",
                "قَالَ أَبُو حَنِيفَةَ رَحِمَهُ اللَّهُ\u200b",
                "Appended zero-width space (invisible Unicode corruption)",
                id="zwsp-injection",
                marks=pytest.mark.xfail(
                    reason="Known gap: V-P3-2 normalizes whitespace, stripping "
                    "ZWSP. Trailing invisible chars escape detection. "
                    "Mitigated by input-sanitization rules at ingestion boundary.",
                    strict=True,
                ),
            ),
            pytest.param(
                "وَأَصَحُّهَا مَا ذَهَبَ إِلَيْهِ الْجُمْهُورُ",
                "وَأَصَحُّهَا مَا ذَهَبَ إِلَيْهِ الْجُمْهُور",
                "Removed final damma from الْجُمْهُورُ (grammatical case change)",
                id="final-damma-removal",
                marks=pytest.mark.xfail(
                    reason="Known gap: V-P3-2 compares at min(len), so a "
                    "snippet truncated by one trailing diacritic passes as "
                    "prefix match. Fix: compare at max(len) or require exact "
                    "length match.",
                    strict=True,
                ),
            ),
        ],
    )
    def test_text_integrity_catches_diacritic_corruption(
        self, original: str, corrupted: str, description: str
    ) -> None:
        """V-P3-2 must detect when text_snippet doesn't match primary_text.

        If the frozen source has diacritics but the excerpt's snippet diverges
        (even by a single codepoint), the validation must either fail loud
        (EX-V-002) or the texts must match exactly. Silent pass = FP-5 violation.
        """
        # Arrange: excerpt where primary_text is original but snippet is corrupted
        exc = _make_excerpt_record(
            primary_text=original,
            text_snippet=corrupted[:80],
        )

        # Act
        result, errors = validate_excerpt(exc)

        # Assert: either dropped (None + EX-V-002) or the corruption was detected
        if original[:min(len(original), 80)] != corrupted[:min(len(corrupted), 80)]:
            # Texts actually differ at snippet level — must be caught
            assert result is None, (
                f"FP-5 violation: corrupted excerpt passed validation silently. "
                f"Corruption: {description}"
            )
            assert ExcerptingErrorCodes.EX_V_002 in errors

    @pytest.mark.red_team
    def test_identical_text_passes(self) -> None:
        """Baseline: uncorrupted Arabic text must pass validation."""
        text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
        exc = _make_excerpt_record(
            primary_text=text,
            text_snippet=text[:80],
        )
        result, errors = validate_excerpt(exc)
        assert result is not None
        assert ExcerptingErrorCodes.EX_V_002 not in errors


# ═══════════════════════════════════════════════════════════════════
# RT-F7-002: Split/Merge Mutation — boundary decision verification
# ═══════════════════════════════════════════════════════════════════


class TestSplitMergeMutation:
    """FP-19 + FP-20: Force alternative split/merge decisions and verify
    that meaning, anchoring, and study usability are preserved or that
    the engine detects the problem.

    Source: F7/09_red_team_tests.jsonl RT-002.
    These are deterministic structural tests — they verify that the engine's
    data model catches boundary violations, not LLM behavior.
    """

    @pytest.mark.red_team
    @pytest.mark.xfail(
        reason="Known gap: TeachingUnit constructor does not validate segment "
        "contiguity — validation occurs in §5.5.1 during extraction response "
        "parsing, not at model construction time. A Pydantic model_validator "
        "should be added to enforce contiguity at construction.",
        strict=True,
    )
    def test_segment_indices_must_be_contiguous(self) -> None:
        """A teaching unit with non-contiguous segment_indices indicates
        a boundary mutation — segments were skipped without omission honesty."""
        from engines.excerpting.contracts import TeachingUnit

        # Non-contiguous: [0, 2] skips segment 1 — hidden omission
        with pytest.raises((ValueError, Exception)):
            TeachingUnit(
                unit_index=0,
                segment_indices=[0, 2],  # Gap at index 1
                start_word=0,
                end_word=100,
                text_snippet="بسم الله الرحمن الرحيم",
                primary_function=ScholarlyFunction.DEFINITION,
                secondary_functions=[],
                description_arabic="وصف عربي",
                self_containment=SelfContainmentLevel.FULL,
                self_containment_notes=None,
            )

    @pytest.mark.red_team
    @pytest.mark.xfail(
        reason="Known gap: validate_excerpt() does not check start_word < end_word. "
        "Inverted boundaries pass silently. Fix: add V-P3 boundary-order check.",
        strict=True,
    )
    def test_word_boundaries_must_be_ordered(self) -> None:
        """start_word must be < end_word — inverted boundaries indicate
        a split mutation that broke the excerpt's span."""
        exc = _make_excerpt_record(
            start_word=50,
            end_word=10,  # Inverted
        )
        result, errors = validate_excerpt(exc)
        # The validation or model construction should catch this
        assert result is None or len(errors) > 0, (
            "FP-20 gap: inverted word boundaries passed validation silently."
        )

    @pytest.mark.red_team
    def test_empty_primary_text_fails_loud(self) -> None:
        """An excerpt with empty primary_text is a total boundary failure —
        the split removed all content."""
        exc = _make_excerpt_record(
            primary_text="",
            text_snippet="",
        )
        result, errors = validate_excerpt(exc)
        assert result is None, (
            "FP-5 violation: empty-text excerpt passed validation."
        )

    @pytest.mark.red_team
    @pytest.mark.xfail(
        reason="Known gap: V-P3-2 compares at min(len), so a truncated "
        "snippet that is a prefix of primary_text passes. This is the most "
        "dangerous gap (FP-21): dropping a condition from a ruling turns a "
        "restricted concession into an absolute ruling, and V-P3-2 does not "
        "catch it. Fix: V-P3-2 should require snippet length >= threshold "
        "AND flag significant length differences between snippet and primary.",
        strict=True,
    )
    def test_excerpt_with_condition_removed_is_detectable(self) -> None:
        """FP-21 concrete case: dropping a condition from a ruling.

        If 'تصح الصلاة في هذه الحالة إن لم يجد غيرها' is excerpted as
        'تصح الصلاة في هذه الحالة', the text_snippet won't match primary_text.
        This validates that the V-P3-2 check catches the semantic truncation.
        """
        full_ruling = "تصح الصلاة في هذه الحالة إن لم يجد غيرها وهذا قول الجمهور"
        truncated = "تصح الصلاة في هذه الحالة"

        exc = _make_excerpt_record(
            primary_text=full_ruling,
            text_snippet=truncated,
        )
        result, errors = validate_excerpt(exc)
        assert result is None, (
            "FP-21 violation: condition-stripped ruling passed as valid. "
            "A restricted concession now reads as an absolute ruling."
        )
        assert ExcerptingErrorCodes.EX_V_002 in errors
