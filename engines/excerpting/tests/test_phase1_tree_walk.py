"""Tests for §4.2 — Division tree walking and skip criteria."""

from __future__ import annotations


from engines.excerpting.contracts import ExcerptingErrorCodes
from engines.excerpting.src.phase1_assembly import (
    _matches_exclude_keyword,
    find_leaf_divisions,
    should_skip_division,
)
from engines.excerpting.tests.conftest import (
    _make_content_unit,
    _make_division_node,
)
from engines.normalization.contracts import ContentFlags, DivisionType


# ═══════════════════════════════════════════════════════════════════
# find_leaf_divisions
# ═══════════════════════════════════════════════════════════════════


class TestFindLeafDivisions:
    """Tests for find_leaf_divisions (§4.2)."""

    def test_leaf_identification(self) -> None:
        """Leaf = node with empty children list."""
        leaf = _make_division_node(div_id="div_test_1_0")
        result = find_leaf_divisions([leaf])
        assert len(result) == 1
        assert result[0][0].div_id == "div_test_1_0"

    def test_heading_path(self) -> None:
        """heading_path contains root-to-leaf heading_text values."""
        child = _make_division_node(
            div_id="div_test_1_0", heading_text="فصل في الركوع"
        )
        root = _make_division_node(
            div_id="div_test_0_0",
            heading_text="كتاب الصلاة",
            children=[child],
            end_unit_index=5,
        )
        result = find_leaf_divisions([root])
        assert len(result) == 1
        assert result[0][1] == ["كتاب الصلاة", "فصل في الركوع"]

    def test_volume_passthrough(self) -> None:
        """Volume nodes are structural containers — walk into children."""
        leaf = _make_division_node(div_id="div_test_2_0", heading_text="باب")
        volume = _make_division_node(
            div_id="div_test_1_0",
            heading_text="المجلد الأول",
            division_type=DivisionType.VOLUME,
            children=[leaf],
        )
        result = find_leaf_divisions([volume])
        assert len(result) == 1
        assert result[0][0].div_id == "div_test_2_0"
        assert result[0][1] == ["المجلد الأول", "باب"]

    def test_single_root_no_children(self) -> None:
        """Single root with no children → one leaf = one chunk."""
        root = _make_division_node(
            div_id="div_test_0_0", heading_text="مقدمة", end_unit_index=10
        )
        result = find_leaf_divisions([root])
        assert len(result) == 1
        assert result[0][0].div_id == "div_test_0_0"

    def test_empty_tree(self) -> None:
        """Empty division tree → no leaves."""
        result = find_leaf_divisions([])
        assert result == []

    def test_deep_nesting(self) -> None:
        """Three-level nesting: root → child → grandchild (leaf)."""
        grandchild = _make_division_node(
            div_id="div_test_2_0", heading_text="مطلب"
        )
        child = _make_division_node(
            div_id="div_test_1_0",
            heading_text="فصل",
            children=[grandchild],
        )
        root = _make_division_node(
            div_id="div_test_0_0",
            heading_text="كتاب",
            children=[child],
        )
        result = find_leaf_divisions([root])
        assert len(result) == 1
        assert result[0][1] == ["كتاب", "فصل", "مطلب"]

    def test_multiple_leaves(self) -> None:
        """Multiple leaves under one root."""
        leaves = [
            _make_division_node(div_id=f"div_test_1_{i}", heading_text=f"فصل {i}")
            for i in range(3)
        ]
        root = _make_division_node(
            div_id="div_test_0_0",
            heading_text="كتاب",
            children=leaves,
        )
        result = find_leaf_divisions([root])
        assert len(result) == 3


# ═══════════════════════════════════════════════════════════════════
# should_skip_division
# ═══════════════════════════════════════════════════════════════════


class TestShouldSkipDivision:
    """Tests for should_skip_division (§4.2 skip criteria)."""

    def test_skip_toc_division(self) -> None:
        """All-TOC divisions skipped with reason code."""
        node = _make_division_node(start_unit_index=0, end_unit_index=1)
        units = [
            _make_content_unit(
                unit_index=0, content_flags=ContentFlags(is_toc_page=True)
            ),
            _make_content_unit(
                unit_index=1, content_flags=ContentFlags(is_toc_page=True)
            ),
        ]
        result = should_skip_division(node, units)
        assert result == "all_toc"

    def test_skip_index_division(self) -> None:
        """All-index divisions skipped."""
        node = _make_division_node(start_unit_index=0, end_unit_index=0)
        units = [
            _make_content_unit(
                unit_index=0, content_flags=ContentFlags(is_index_page=True)
            ),
        ]
        result = should_skip_division(node, units)
        assert result == "all_index"

    def test_skip_blank_division(self) -> None:
        """All-blank divisions skipped."""
        node = _make_division_node(start_unit_index=0, end_unit_index=0)
        units = [
            _make_content_unit(
                unit_index=0, content_flags=ContentFlags(is_blank=True)
            ),
        ]
        result = should_skip_division(node, units)
        assert result == "all_blank"

    def test_skip_bibliography(self) -> None:
        """مصادر/مراجع/فهرس headings skipped (exact match)."""
        for keyword in ["مصادر", "مراجع", "فهرس", "المراجع", "المصادر والمراجع"]:
            node = _make_division_node(
                heading_text=keyword, start_unit_index=0, end_unit_index=0
            )
            units = [_make_content_unit(unit_index=0)]
            result = should_skip_division(node, units)
            assert result == "bibliography_keyword", f"Failed for keyword: {keyword}"

    def test_no_false_positive_masadir(self) -> None:
        """'مصادر الأحكام' is a content chapter, NOT bibliography."""
        node = _make_division_node(
            heading_text="مصادر الأحكام", start_unit_index=0, end_unit_index=0
        )
        units = [_make_content_unit(unit_index=0)]
        result = should_skip_division(node, units)
        assert result is None  # Must NOT be skipped

    def test_skip_empty_range(self) -> None:
        """start > end → EX-A-002, skip."""
        node = _make_division_node(start_unit_index=5, end_unit_index=3)
        result = should_skip_division(node, [])
        assert result is not None
        assert ExcerptingErrorCodes.EX_A_002 in result

    def test_normal_division_not_skipped(self) -> None:
        """Normal content division returns None (should be processed)."""
        node = _make_division_node(
            heading_text="باب الطهارة", start_unit_index=0, end_unit_index=1
        )
        units = [
            _make_content_unit(unit_index=0),
            _make_content_unit(unit_index=1),
        ]
        result = should_skip_division(node, units)
        assert result is None


# ═══════════════════════════════════════════════════════════════════
# _matches_exclude_keyword
# ═══════════════════════════════════════════════════════════════════


class TestMatchesExcludeKeyword:
    """Tests for _matches_exclude_keyword (§4.2)."""

    def test_exact_match_simple(self) -> None:
        """Simple keyword exact match."""
        assert _matches_exclude_keyword("مصادر") is True
        assert _matches_exclude_keyword("مراجع") is True
        assert _matches_exclude_keyword("فهرس") is True

    def test_compound_keywords(self) -> None:
        """Compound bibliography keywords from expanded list."""
        assert _matches_exclude_keyword("المصادر والمراجع") is True
        assert _matches_exclude_keyword("فهرس المصادر") is True
        assert _matches_exclude_keyword("قائمة المراجع") is True

    def test_no_false_positive_content_chapter(self) -> None:
        """Content chapter headings must NOT match."""
        assert _matches_exclude_keyword("مصادر الأحكام") is False
        assert _matches_exclude_keyword("باب في المراجعة") is False

    def test_diacritics_stripped_for_matching(self) -> None:
        """Diacritics are stripped before comparison."""
        assert _matches_exclude_keyword("مَصَادِرُ") is True  # مصادر with diacritics

    def test_empty_heading(self) -> None:
        """Empty heading never matches."""
        assert _matches_exclude_keyword("") is False
