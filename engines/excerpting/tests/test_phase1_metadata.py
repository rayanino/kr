"""Tests for §4.7 — Content flag/footnote aggregation and renumbering."""

from __future__ import annotations

from engines.excerpting.src.phase1_assembly import (
    aggregate_content_flags,
    aggregate_footnotes,
    collect_physical_pages,
    renumber_footnotes,
)
from engines.excerpting.tests.conftest import _make_content_unit
from engines.normalization.contracts import (
    ContentFlags,
    Footnote,
    FootnoteType,
    PhysicalPage,
)


def _fn(ref_marker: str, text: str = "footnote text") -> Footnote:
    """Shorthand footnote factory."""
    return Footnote(
        ref_marker=ref_marker,
        text=text,
        footnote_type=FootnoteType.AUTHOR_ORIGINAL,
        confidence=0.9,
    )


# ═══════════════════════════════════════════════════════════════════
# aggregate_content_flags
# ═══════════════════════════════════════════════════════════════════


class TestAggregateContentFlags:
    """Tests for aggregate_content_flags (§4.7)."""

    def test_or_aggregate_flags(self) -> None:
        """Any unit with has_verse=true → chunk has_verse=true."""
        units = [
            _make_content_unit(
                unit_index=0,
                content_flags=ContentFlags(has_verse=True),
            ),
            _make_content_unit(
                unit_index=1,
                content_flags=ContentFlags(has_quran_citation=True),
            ),
        ]
        result = aggregate_content_flags(units, [0, 1])
        assert result.has_verse is True
        assert result.has_quran_citation is True
        assert result.has_table is False

    def test_all_false(self) -> None:
        """No flags set → all False."""
        units = [_make_content_unit(unit_index=0)]
        result = aggregate_content_flags(units, [0])
        assert result.has_verse is False
        assert result.has_hadith_citation is False


# ═══════════════════════════════════════════════════════════════════
# aggregate_footnotes
# ═══════════════════════════════════════════════════════════════════


class TestAggregateFootnotes:
    """Tests for aggregate_footnotes (§4.7)."""

    def test_collect_in_order(self) -> None:
        """Footnotes collected in unit_index order."""
        units = [
            _make_content_unit(unit_index=0, footnotes=[_fn("1")]),
            _make_content_unit(unit_index=1, footnotes=[_fn("2")]),
        ]
        result = aggregate_footnotes(units, [0, 1])
        assert len(result) == 2
        assert result[0].ref_marker == "1"
        assert result[1].ref_marker == "2"

    def test_duplicate_ref_marker_kept(self) -> None:
        """All footnotes kept including duplicates (for renumbering)."""
        units = [
            _make_content_unit(unit_index=0, footnotes=[_fn("1", "text A")]),
            _make_content_unit(unit_index=1, footnotes=[_fn("1", "text B")]),
        ]
        result = aggregate_footnotes(units, [0, 1])
        assert len(result) == 2  # Both kept for renumbering


# ═══════════════════════════════════════════════════════════════════
# renumber_footnotes
# ═══════════════════════════════════════════════════════════════════


class TestRenumberFootnotes:
    """Tests for renumber_footnotes (§4.7)."""

    def test_no_renumber_needed(self) -> None:
        """No collisions → renumber_map is None."""
        text = "وقال ⌜1⌝ المؤلف ⌜2⌝"
        fns = [_fn("1"), _fn("2")]
        new_text, new_fns, rmap = renumber_footnotes(text, fns)
        assert rmap is None
        assert new_text == text

    def test_footnote_renumber(self) -> None:
        """Colliding ⌜1⌝ markers → renumbered sequentially."""
        text = "وقال ⌜1⌝ المؤلف ⌜1⌝"
        fns = [_fn("1", "note A"), _fn("1", "note B")]
        new_text, new_fns, rmap = renumber_footnotes(text, fns)
        assert "⌜1⌝" in new_text
        assert "⌜2⌝" in new_text
        assert len(new_fns) == 2
        assert new_fns[0].ref_marker == "1"
        assert new_fns[1].ref_marker == "2"

    def test_renumber_updates_text(self) -> None:
        """assembled_text markers updated when renumbering."""
        text = "أ ⌜1⌝ ب ⌜2⌝ ج ⌜1⌝"
        fns = [_fn("1", "A"), _fn("2", "B"), _fn("1", "C")]
        new_text, _, rmap = renumber_footnotes(text, fns)
        assert new_text.count("⌜") == 3
        # Markers should be 1, 2, 3 (sequential)
        assert "⌜1⌝" in new_text
        assert "⌜2⌝" in new_text
        assert "⌜3⌝" in new_text

    def test_renumber_map(self) -> None:
        """old→new mapping in renumber_map."""
        text = "⌜1⌝ ⌜1⌝"
        fns = [_fn("1", "A"), _fn("1", "B")]
        _, _, rmap = renumber_footnotes(text, fns)
        assert rmap is not None
        # "1" was renumbered — second occurrence became "2"
        assert "1" in rmap

    def test_empty_footnotes(self) -> None:
        """Empty footnotes → pass through unchanged."""
        text = "no footnotes here"
        new_text, new_fns, rmap = renumber_footnotes(text, [])
        assert new_text == text
        assert new_fns == []
        assert rmap is None


# ═══════════════════════════════════════════════════════════════════
# collect_physical_pages
# ═══════════════════════════════════════════════════════════════════


class TestCollectPhysicalPages:
    """Tests for collect_physical_pages (§4.7)."""

    def test_physical_pages_order(self) -> None:
        """Pages collected in unit_index order."""
        units = [
            _make_content_unit(
                unit_index=0,
                physical_page=PhysicalPage(
                    volume=1, page_number_display="١", page_number_int=1
                ),
            ),
            _make_content_unit(
                unit_index=1,
                physical_page=PhysicalPage(
                    volume=1, page_number_display="٢", page_number_int=2
                ),
            ),
        ]
        result = collect_physical_pages(units, [0, 1])
        assert len(result) == 2
        assert result[0].page_number_int == 1
        assert result[1].page_number_int == 2
