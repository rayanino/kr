"""Tests for §4.3 — Cross-page text assembly."""

from __future__ import annotations

from engines.excerpting.src.phase1_assembly import (
    _get_bc_separator,
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
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_SENTENCE)) == " "
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_PARAGRAPH)) == "\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.MID_ARGUMENT)) == "\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.SECTION_BREAK)) == "\n\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.DIVISION_BREAK)) == "\n\n"
        assert _get_bc_separator(_bc(BoundaryContinuityType.UNKNOWN)) == "\n"

    def test_null_boundary(self) -> None:
        """null boundary_continuity → '\\n' separator."""
        assert _get_bc_separator(None) == "\n"


# ═══════════════════════════════════════════════════════════════════
# mid_sentence separator (§4.3, SPEC-NOTE-4)
# ═══════════════════════════════════════════════════════════════════


class TestMidSentenceSeparator:
    """Verify mid_sentence always uses space separator (SPEC-NOTE-4 fix).

    Shamela page breaks always fall between complete words (Arabic print
    does not split words across pages). Empirically verified: 0/294
    genuine mid-word splits across all fixture packages. The old
    word-final heuristic (ة, ى, tanwin) produced 92% word-merge
    corruption and has been removed.
    """

    def test_separator_map_mid_sentence_is_space(self) -> None:
        """BC_SEPARATOR_MAP["mid_sentence"] must be a single space."""
        from engines.excerpting.src.phase1_assembly import BC_SEPARATOR_MAP
        assert BC_SEPARATOR_MAP["mid_sentence"] == " "


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

    def test_mid_sentence_always_space(self) -> None:
        """Mid-sentence always inserts space (SPEC-NOTE-4 fix).

        Even text ending with a connecting letter gets a space — Shamela
        page breaks never split words. The old heuristic that used empty
        separator for connecting letters produced 92% word-merge corruption.
        """
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="كتاب",
                boundary_continuity=_bc(BoundaryContinuityType.MID_SENTENCE),
            ),
            _make_content_unit(unit_index=1, primary_text="الله"),
        ]
        text, jps, _ = assemble_text(units, 0, 1)
        assert text == "كتاب الله"
        assert jps[0].separator_used == " "

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
