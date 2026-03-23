"""Tests for §4.3 — Cross-page text assembly."""

from __future__ import annotations

from engines.excerpting.contracts import ExcerptingErrorCodes
from engines.excerpting.src.phase1_assembly import (
    _get_bc_separator,
    _should_insert_space_mid_sentence,
    assemble_text,
)
from engines.excerpting.tests.conftest import _make_content_unit
from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContentFlags,
    ContinuityDetectionMethod,
)


def _bc(bc_type: BoundaryContinuityType) -> BoundaryContinuity:
    """Shorthand factory for BoundaryContinuity."""
    return BoundaryContinuity(
        type=bc_type,
        confidence=0.9,
        detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
        continuation_hint=None,
    )


# ═══════════════════════════════════════════════════════════════════
# _get_bc_separator
# ═══════════════════════════════════════════════════════════════════


class TestGetBcSeparator:
    """Tests for _get_bc_separator (§4.3)."""

    def test_separator_mapping(self) -> None:
        """Each boundary_continuity type maps to correct separator."""
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_SENTENCE)) == ""
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_PARAGRAPH)) == "\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_ARGUMENT)) == "\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.SECTION_BREAK)) == "\n\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.DIVISION_BREAK)) == "\n\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.UNKNOWN)) == "\n"

    def test_null_boundary(self) -> None:
        """null boundary_continuity → '\\n' separator."""
        assert _get_bc_separator(None) == "\n"


# ═══════════════════════════════════════════════════════════════════
# _should_insert_space_mid_sentence
# ═══════════════════════════════════════════════════════════════════


class TestMidSentenceSpace:
    """Tests for _should_insert_space_mid_sentence (§4.3)."""

    def test_word_final_taa_marbuta(self) -> None:
        """taa marbuta (ة) → space inserted (word complete)."""
        assert _should_insert_space_mid_sentence("الصلاة", "والزكاة") is True

    def test_word_final_alif_maqsura(self) -> None:
        """alif maqsura (ى) → space inserted."""
        assert _should_insert_space_mid_sentence("موسى", "عليه") is True

    def test_word_final_tanwin(self) -> None:
        """tanwin diacritic as last char → space inserted."""
        # "كتابٌ" ends with dammatan (U+064C) as the last code point
        assert _should_insert_space_mid_sentence("كتابٌ", "جديد") is True

    def test_connecting_letter(self) -> None:
        """Connecting letter → no separator (word continues)."""
        # Letter "ب" is a connecting letter (middle of a word)
        assert _should_insert_space_mid_sentence("كتا", "ب الله") is False

    def test_trailing_whitespace(self) -> None:
        """Original text ending with whitespace → space inserted."""
        assert _should_insert_space_mid_sentence("كتاب ", "الله") is True

    def test_empty_prev(self) -> None:
        """Empty prev_text → no space."""
        assert _should_insert_space_mid_sentence("", "الله") is False


# ═══════════════════════════════════════════════════════════════════
# assemble_text
# ═══════════════════════════════════════════════════════════════════


class TestAssembleText:
    """Tests for assemble_text (§4.3)."""

    def test_two_units_mid_paragraph(self) -> None:
        """Two units with mid_paragraph boundary → joined with \\n."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="الحمد لله",
                boundary_continuity=_bc(BoundaryContinuityType.MID_PARAGRAPH),
            ),
            _make_content_unit(
                unit_index=1,
                primary_text="رب العالمين",
            ),
        ]
        text, jps, indices = assemble_text(units, 0, 1)
        assert text == "الحمد لله\nرب العالمين"
        assert len(jps) == 1
        assert jps[0].separator_used == "\n"
        assert indices == [0, 1]

    def test_skip_toc_in_range(self) -> None:
        """TOC pages skipped during assembly, index still recorded."""
        units = [
            _make_content_unit(unit_index=0, primary_text="بداية"),
            _make_content_unit(
                unit_index=1,
                primary_text="فهرس",
                content_flags=ContentFlags(is_toc_page=True),
            ),
            _make_content_unit(unit_index=2, primary_text="نهاية"),
        ]
        text, jps, indices = assemble_text(units, 0, 2)
        assert "فهرس" not in text
        assert text == "بداية\nنهاية"
        assert indices == [0, 1, 2]  # All indices including skipped

    def test_diacritics_preserved(self) -> None:
        """Arabic diacritics byte-for-byte identical after assembly."""
        diacritized = "الحَمْدُ لِلَّهِ رَبِّ العَالَمِينَ"
        units = [_make_content_unit(unit_index=0, primary_text=diacritized)]
        text, _, _ = assemble_text(units, 0, 0)
        assert text == diacritized

    def test_footnote_markers_preserved(self) -> None:
        """⌜N⌝ markers preserved in text after assembly."""
        text_with_fn = "وقال ⌜1⌝ المؤلف في كتابه"
        units = [_make_content_unit(unit_index=0, primary_text=text_with_fn)]
        text, _, _ = assemble_text(units, 0, 0)
        assert "⌜1⌝" in text

    def test_join_points_recorded(self) -> None:
        """JoinPoint per boundary with correct char_offset."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="أولاً",
                boundary_continuity=_bc(BoundaryContinuityType.SECTION_BREAK),
            ),
            _make_content_unit(unit_index=1, primary_text="ثانياً"),
        ]
        text, jps, _ = assemble_text(units, 0, 1)
        assert len(jps) == 1
        jp = jps[0]
        assert jp.after_unit_index == 0
        assert jp.before_unit_index == 1
        assert jp.separator_used == "\n\n"
        assert jp.char_offset_in_assembled == len("أولاً")

    def test_constituent_unit_indices(self) -> None:
        """All unit_indices in range recorded including skipped."""
        units = [
            _make_content_unit(unit_index=0, primary_text="text"),
            _make_content_unit(
                unit_index=1,
                primary_text="blank",
                content_flags=ContentFlags(is_blank=True),
            ),
            _make_content_unit(unit_index=2, primary_text="more"),
        ]
        _, _, indices = assemble_text(units, 0, 2)
        assert indices == [0, 1, 2]

    def test_mid_sentence_word_final_inserts_space(self) -> None:
        """Mid-sentence with taa marbuta ending → space inserted."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="الصلاة",
                boundary_continuity=_bc(BoundaryContinuityType.MID_SENTENCE),
            ),
            _make_content_unit(unit_index=1, primary_text="والزكاة"),
        ]
        text, jps, _ = assemble_text(units, 0, 1)
        assert text == "الصلاة والزكاة"
        assert jps[0].separator_used == " "

    def test_mid_sentence_connecting_no_space(self) -> None:
        """Mid-sentence with connecting letter → empty separator."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="كتا",
                boundary_continuity=_bc(BoundaryContinuityType.MID_SENTENCE),
            ),
            _make_content_unit(unit_index=1, primary_text="ب الله"),
        ]
        text, jps, _ = assemble_text(units, 0, 1)
        assert text == "كتاب الله"
        assert jps[0].separator_used == ""

    def test_missing_content_unit_ex_a_011(self) -> None:
        """Missing content unit → EX-A-011 warning, skipped gracefully."""
        # Unit index 1 is in range but not in content_units list
        units = [
            _make_content_unit(unit_index=0, primary_text="بداية"),
            _make_content_unit(unit_index=2, primary_text="نهاية"),
        ]
        text, _, indices = assemble_text(units, 0, 2)
        assert "بداية" in text
        assert "نهاية" in text
        assert indices == [0, 1, 2]  # Index 1 is still in constituent list
