"""Tests for division tree completion — preamble gap handling (§4.2).

When a parent DivisionNode has children that don't cover its full range,
_complete_division_tree() inserts synthetic leaf nodes so that
find_leaf_divisions() returns leaves covering ALL content units.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.excerpting.contracts import (
    AssembledChunk,
    ExcerptingConfig,
    _count_arabic_words,
)
from engines.excerpting.src.phase1_assembly import (
    _complete_division_tree,
    run_phase1,
    split_oversized_division,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_division_node,
)
from engines.normalization.contracts import (
    ContentUnit,
    DivisionType,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════
# Unit tests for _complete_division_tree
# ═══════════════════════════════════════════════════════════════════


class TestCompleteDivisionTree:
    """Tests for _complete_division_tree (§4.2 tree completion)."""

    def test_preamble_gap_creates_synthetic_leaf(self) -> None:
        """Parent [0..9] with child [5..9] → synthetic preamble [0..4]."""
        child = _make_division_node(
            div_id="div_test_1_0",
            heading_level=3,
            start_unit_index=5,
            end_unit_index=9,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=9,
            children=[child],
        )

        result = _complete_division_tree([parent])

        assert len(result) == 1
        completed_parent = result[0]
        assert len(completed_parent.children) == 2

        synthetic = completed_parent.children[0]
        assert synthetic.div_id == "div_test_0_0_pre"
        assert synthetic.division_type == DivisionType.MUQADDIMAH
        assert synthetic.heading_text == "مقدمة"
        assert synthetic.children == []
        assert synthetic.start_unit_index == 0
        assert synthetic.end_unit_index == 4
        assert synthetic.heading_level == 3  # Same as sibling, not parent

        original = completed_parent.children[1]
        assert original.div_id == "div_test_1_0"

    def test_no_gap_no_change(self) -> None:
        """Parent [0..9] with children [0..4]+[5..9] → no synthetic added."""
        child_a = _make_division_node(
            div_id="div_test_1_0",
            start_unit_index=0,
            end_unit_index=4,
        )
        child_b = _make_division_node(
            div_id="div_test_1_1",
            start_unit_index=5,
            end_unit_index=9,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            start_unit_index=0,
            end_unit_index=9,
            children=[child_a, child_b],
        )

        result = _complete_division_tree([parent])

        assert len(result) == 1
        assert len(result[0].children) == 2

    def test_flat_tree_no_change(self) -> None:
        """3 leaf nodes → returned unchanged."""
        leaves = [
            _make_division_node(div_id=f"div_test_1_{i}", start_unit_index=i * 10, end_unit_index=i * 10 + 9)
            for i in range(3)
        ]

        result = _complete_division_tree(leaves)

        assert len(result) == 3
        for node in result:
            assert node.children == []

    def test_inter_child_gap_creates_synthetic_leaf(self) -> None:
        """Parent [0..19] with children [0..4]+[10..19] → gap synthetic [5..9]."""
        child_a = _make_division_node(
            div_id="div_test_1_0",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=4,
        )
        child_b = _make_division_node(
            div_id="div_test_1_1",
            heading_level=2,
            start_unit_index=10,
            end_unit_index=19,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=19,
            children=[child_a, child_b],
        )

        result = _complete_division_tree([parent])

        completed = result[0]
        assert len(completed.children) == 3

        assert completed.children[0].div_id == "div_test_1_0"
        synthetic = completed.children[1]
        assert synthetic.div_id == "div_test_0_0_gap_0"
        assert synthetic.division_type is None
        assert synthetic.start_unit_index == 5
        assert synthetic.end_unit_index == 9
        assert completed.children[2].div_id == "div_test_1_1"

    def test_trailing_gap_creates_synthetic_leaf(self) -> None:
        """Parent [0..19] with child [0..9] → trailing synthetic [10..19]."""
        child = _make_division_node(
            div_id="div_test_1_0",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=9,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=19,
            children=[child],
        )

        result = _complete_division_tree([parent])

        completed = result[0]
        assert len(completed.children) == 2

        assert completed.children[0].div_id == "div_test_1_0"
        synthetic = completed.children[1]
        assert synthetic.div_id == "div_test_0_0_post"
        assert synthetic.division_type is None
        assert synthetic.start_unit_index == 10
        assert synthetic.end_unit_index == 19

    def test_nested_preamble_gaps(self) -> None:
        """Grandparent [0..29] → parent [10..29] → child [20..29].

        Two preamble gaps: [0..9] at grandparent level, [10..19] at parent level.
        """
        child = _make_division_node(
            div_id="div_test_2_0",
            heading_level=3,
            start_unit_index=20,
            end_unit_index=29,
        )
        parent = _make_division_node(
            div_id="div_test_1_0",
            heading_level=2,
            start_unit_index=10,
            end_unit_index=29,
            children=[child],
        )
        grandparent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=29,
            children=[parent],
        )

        result = _complete_division_tree([grandparent])

        gp = result[0]
        assert len(gp.children) == 2  # synthetic preamble + completed parent

        gp_pre = gp.children[0]
        assert gp_pre.div_id == "div_test_0_0_pre"
        assert gp_pre.start_unit_index == 0
        assert gp_pre.end_unit_index == 9
        assert gp_pre.children == []

        completed_parent = gp.children[1]
        assert len(completed_parent.children) == 2  # synthetic preamble + original child

        parent_pre = completed_parent.children[0]
        assert parent_pre.div_id == "div_test_1_0_pre"
        assert parent_pre.start_unit_index == 10
        assert parent_pre.end_unit_index == 19
        assert parent_pre.children == []

        assert completed_parent.children[1].div_id == "div_test_2_0"

    def test_original_tree_not_mutated(self) -> None:
        """Completing the tree must not modify the original nodes."""
        child = _make_division_node(
            div_id="div_test_1_0",
            start_unit_index=5,
            end_unit_index=9,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            start_unit_index=0,
            end_unit_index=9,
            children=[child],
        )
        original_child_count = len(parent.children)

        _complete_division_tree([parent])

        assert len(parent.children) == original_child_count

    def test_synthetic_leaf_heading_level_matches_siblings(self) -> None:
        """Synthetic preamble uses first child's heading_level, not parent's."""
        child = _make_division_node(
            div_id="div_test_1_0",
            heading_level=3,
            start_unit_index=5,
            end_unit_index=9,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=2,
            start_unit_index=0,
            end_unit_index=9,
            children=[child],
        )

        result = _complete_division_tree([parent])
        synthetic = result[0].children[0]
        assert synthetic.heading_level == 3  # child level, not parent (2)

    def test_preamble_combined_with_trailing(self) -> None:
        """Parent [0..29] with child [10..19] → preamble [0..9] + trailing [20..29]."""
        child = _make_division_node(
            div_id="div_test_1_0",
            heading_level=2,
            start_unit_index=10,
            end_unit_index=19,
        )
        parent = _make_division_node(
            div_id="div_test_0_0",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=29,
            children=[child],
        )

        result = _complete_division_tree([parent])

        completed = result[0]
        assert len(completed.children) == 3

        pre = completed.children[0]
        assert pre.div_id == "div_test_0_0_pre"
        assert pre.start_unit_index == 0
        assert pre.end_unit_index == 9

        assert completed.children[1].div_id == "div_test_1_0"

        post = completed.children[2]
        assert post.div_id == "div_test_0_0_post"
        assert post.start_unit_index == 20
        assert post.end_unit_index == 29

    def test_empty_children_list_treated_as_leaf(self) -> None:
        """Node with children=[] is a leaf, not a parent with missing children."""
        node = _make_division_node(
            div_id="div_test_1_0",
            start_unit_index=0,
            end_unit_index=9,
            children=[],
        )

        result = _complete_division_tree([node])

        assert len(result) == 1
        assert result[0].children == []

    def test_preamble_heading_alignment_ok_true(self) -> None:
        """F-1: Synthetic preamble chunks must have heading_alignment_ok=True.

        Preamble nodes get heading "مقدمة" assigned by _complete_division_tree,
        which won't match the assembled text. The F-1 fix skips the heading
        alignment check for _pre nodes so they always pass.
        """
        pkg_path = PACKAGES_DIR / "ibn_aqil_v1"
        if not pkg_path.exists():
            pytest.skip("ibn_aqil_v1 package not available")

        pkg = _load_package(pkg_path)
        chunks, _ = run_phase1(pkg, ExcerptingConfig())

        preamble_chunks = [c for c in chunks if "_pre" in c.div_id]
        assert len(preamble_chunks) > 0, "Expected at least one preamble chunk"
        for chunk in preamble_chunks:
            assert chunk.heading_alignment_ok is True, (
                f"Preamble chunk {chunk.chunk_id} should have "
                f"heading_alignment_ok=True (F-1 fix)"
            )

    def test_preamble_oversized_split(self) -> None:
        """F-3: Preamble chunks split correctly when oversized.

        Constructs a ~6000-word preamble chunk and verifies that
        split_oversized_division produces correct chunk_ids with _pre
        prefix preserved, and that each split chunk passes I-AC-5 validation.
        """
        # Generate ~6000 Arabic words using scholarly vocabulary cycle
        base_words = [
            "وقال", "المؤلف", "رحمه", "الله", "تعالى", "في", "كتابه",
            "العظيم", "الذي", "صنفه", "في", "علم", "الفقه", "والأصول",
            "والنحو", "والصرف", "والبلاغة", "والمنطق", "والحديث", "والتفسير",
        ]
        words: list[str] = []
        while len(words) < 6000:
            words.extend(base_words)
        words = words[:6000]
        # Insert paragraph break at midpoint for a reliable split point
        mid = len(words) // 2
        text = " ".join(words[:mid]) + "\n\n" + " ".join(words[mid:])

        wc = _count_arabic_words(text)
        chunk = _make_assembled_chunk(
            chunk_id="div_test_0_0_pre",
            div_id="div_test_0_0_pre",
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )

        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=5000)
        result = split_oversized_division(chunk, [], config)

        assert len(result) >= 2, f"Expected split, got {len(result)} chunks"
        assert result[0].chunk_id == "div_test_0_0_pre_chunk_0"
        assert result[0].split_info is not None

        # Re-validate each split chunk through Pydantic (I-AC-5)
        for split_chunk in result:
            AssembledChunk.model_validate(split_chunk.model_dump())


# ═══════════════════════════════════════════════════════════════════
# Integration tests on real packages
# ═══════════════════════════════════════════════════════════════════


PACKAGES_DIR = Path("experiments/format_diversity_test/packages")


def _load_package(pkg_path: Path) -> NormalizedPackage:
    """Load a NormalizedPackage from a format_diversity_test package directory."""
    manifest = NormalizedManifest.model_validate_json(
        (pkg_path / "manifest.json").read_text(encoding="utf-8")
    )
    units: list[ContentUnit] = []
    with open(pkg_path / "content.jsonl", encoding="utf-8") as fh:
        for line in fh:
            stripped = line.strip()
            if stripped:
                units.append(ContentUnit.model_validate_json(stripped))
    return NormalizedPackage(manifest=manifest, content_units=units)


class TestRunPhase1Integration:
    """Integration tests: run Phase 1 on real packages after tree completion."""

    def test_run_phase1_ibn_aqil_v1_passes(self) -> None:
        """ibn_aqil_v1 — formerly failed EX-V-001, now passes with tree completion."""
        pkg_path = PACKAGES_DIR / "ibn_aqil_v1"
        if not pkg_path.exists():
            pytest.skip("ibn_aqil_v1 package not available")

        pkg = _load_package(pkg_path)
        chunks, validation = run_phase1(pkg, ExcerptingConfig())

        assert len(chunks) > 0
        for result in validation:
            assert result["status"] in ("pass", "warning"), (
                f"Unexpected failure: {result}"
            )

    @pytest.mark.parametrize(
        "package_name",
        ["ext_39_masala", "ext_46_qa", "ibn_aqil_v1", "ibn_aqil_v3", "taysir"],
    )
    def test_run_phase1_all_packages_pass(self, package_name: str) -> None:
        """All 5 format diversity packages must pass Phase 1 after tree completion."""
        pkg_path = PACKAGES_DIR / package_name
        if not pkg_path.exists():
            pytest.skip(f"{package_name} package not available")

        pkg = _load_package(pkg_path)
        chunks, validation = run_phase1(pkg, ExcerptingConfig())

        assert len(chunks) > 0, f"{package_name}: no chunks produced"
        for result in validation:
            assert result["status"] in ("pass", "warning"), (
                f"{package_name}: unexpected failure: {result}"
            )
