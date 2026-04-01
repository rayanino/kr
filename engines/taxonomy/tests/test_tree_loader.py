"""Tests for tree loading and normalization (SPEC §4.A.1).

Tests use real science tree YAML files from library/sciences/.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from engines.taxonomy.contracts_core import LoadedTree, TreeNode
from engines.taxonomy.src.tree_loader import (
    TreeLoadError,
    build_branch_view,
    build_leaf_view,
    collect_leaves,
    detect_yaml_format,
    load_tree,
    normalize_v0,
    normalize_v1,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _PROJECT_ROOT / "library" / "sciences" / "taxonomy_registry.yaml"


# ── Format Detection ──────────────────────────────────────────────


class TestDetectYamlFormat:
    def test_v1_format_detected(self) -> None:
        data = {"taxonomy": {"id": "test", "title": "Test", "nodes": []}}
        assert detect_yaml_format(data) == "v1"

    def test_v0_format_detected(self) -> None:
        data = {"aqidah": {"al_iman": {"_label": "الإيمان", "_leaf": True}}}
        assert detect_yaml_format(data) == "v0"

    def test_v0_when_taxonomy_key_missing_nodes(self) -> None:
        data = {"taxonomy": "something_else"}
        assert detect_yaml_format(data) == "v0"

    def test_real_nahw_is_v1(self) -> None:
        tree_path = _PROJECT_ROOT / "library" / "sciences" / "nahw" / "tree.yaml"
        data = yaml.safe_load(tree_path.read_text(encoding="utf-8"))
        assert detect_yaml_format(data) == "v1"

    def test_real_aqidah_is_v0(self) -> None:
        tree_path = _PROJECT_ROOT / "library" / "sciences" / "aqidah" / "tree.yaml"
        data = yaml.safe_load(tree_path.read_text(encoding="utf-8"))
        assert detect_yaml_format(data) == "v0"


# ── v1 Normalization ──────────────────────────────────────────────


class TestNormalizeV1:
    def test_nahw_leaf_count(self, nahw_tree: LoadedTree) -> None:
        assert nahw_tree.leaf_count == 183

    def test_sarf_leaf_count(self, all_trees: dict[str, LoadedTree]) -> None:
        assert all_trees["sarf"].leaf_count == 226

    def test_balagha_leaf_count(self, all_trees: dict[str, LoadedTree]) -> None:
        assert all_trees["balagha"].leaf_count == 335

    def test_imlaa_leaf_count(self, all_trees: dict[str, LoadedTree]) -> None:
        assert all_trees["imlaa"].leaf_count == 105

    def test_nahw_version(self, nahw_tree: LoadedTree) -> None:
        assert nahw_tree.tree_version == "nahw_v2_0"

    def test_nahw_display_name(self, nahw_tree: LoadedTree) -> None:
        assert nahw_tree.display_name_ar == "علم النحو"

    def test_nahw_known_leaf_path(self, nahw_tree: LoadedTree) -> None:
        """Verify a known leaf exists at the expected path."""
        assert "mabadi_al_nahw_wa_ahkam_al_irab/al_kalam_wa_al_kalima_wa_aqsamuha/aqsam_al_kalima" in nahw_tree.leaf_by_path

    def test_leaf_path_uses_slash_separator(self, nahw_tree: LoadedTree) -> None:
        for leaf in nahw_tree.all_leaves:
            assert "\\" not in leaf.path, f"Backslash in path: {leaf.path}"
            if "/" in leaf.path:
                parts = leaf.path.split("/")
                assert all(p for p in parts), f"Empty segment in path: {leaf.path}"

    def test_all_leaf_paths_unique(self, nahw_tree: LoadedTree) -> None:
        paths = [leaf.path for leaf in nahw_tree.all_leaves]
        assert len(paths) == len(set(paths))

    def test_leaf_has_parent_title(self, nahw_tree: LoadedTree) -> None:
        leaf = nahw_tree.leaf_by_path["mabadi_al_nahw_wa_ahkam_al_irab/al_kalam_wa_al_kalima_wa_aqsamuha/aqsam_al_kalima"]
        assert leaf.parent_title == "الكلام والكلمة وأقسامها"


# ── v0 Normalization ──────────────────────────────────────────────


class TestNormalizeV0:
    def test_aqidah_leaf_count(self, aqidah_tree: LoadedTree) -> None:
        assert aqidah_tree.leaf_count == 30

    def test_aqidah_version(self, aqidah_tree: LoadedTree) -> None:
        assert aqidah_tree.tree_version == "aqidah_v0_2"

    def test_double_underscore_overview_is_leaf(
        self, aqidah_tree: LoadedTree
    ) -> None:
        """__overview nodes ARE real leaves (SPEC §4.A.1)."""
        overview_leaves = [
            leaf for leaf in aqidah_tree.all_leaves if "__overview" in leaf.id
        ]
        assert len(overview_leaves) == 2, (
            f"Expected 2 __overview leaves, found {len(overview_leaves)}"
        )

    def test_overview_leaf_titles_arabic(self, aqidah_tree: LoadedTree) -> None:
        overview_leaves = [
            leaf for leaf in aqidah_tree.all_leaves if "__overview" in leaf.id
        ]
        for leaf in overview_leaves:
            assert "نظرة عامة" in leaf.title

    def test_envelope_key_not_in_paths(self, aqidah_tree: LoadedTree) -> None:
        """Top-level envelope key (aqidah) must NOT appear in leaf paths."""
        for leaf in aqidah_tree.all_leaves:
            assert not leaf.path.startswith("aqidah/"), (
                f"Envelope key in path: {leaf.path}"
            )

    def test_known_aqidah_leaf_path(self, aqidah_tree: LoadedTree) -> None:
        assert (
            "al_iman_billah/asma_wa_sifat/manhaj_ahl_al_sunna_fi_al_sifat"
            in aqidah_tree.leaf_by_path
        )

    def test_karamat_is_leaf(self, aqidah_tree: LoadedTree) -> None:
        """al_karamat is a top-level leaf node."""
        assert "al_karamat" in aqidah_tree.leaf_by_path

    def test_all_aqidah_leaf_paths_unique(self, aqidah_tree: LoadedTree) -> None:
        paths = [leaf.path for leaf in aqidah_tree.all_leaves]
        assert len(paths) == len(set(paths))


# ── load_tree function ────────────────────────────────────────────


class TestLoadTree:
    def test_load_all_five_sciences(
        self, all_trees: dict[str, LoadedTree]
    ) -> None:
        assert len(all_trees) == 5
        for sid, tree in all_trees.items():
            assert tree.science_id == sid
            assert tree.leaf_count > 0
            assert len(tree.all_leaves) == tree.leaf_count

    def test_override_path(self, tmp_path: Path) -> None:
        """load_tree with override_path uses the override file."""
        tree_yaml = {
            "taxonomy": {
                "id": "test_v1",
                "title": "اختبار",
                "nodes": [
                    {"id": "branch1", "title": "فرع ١", "children": [
                        {"id": "leaf1", "title": "ورقة ١", "leaf": True},
                    ]},
                ],
            }
        }
        override_file = tmp_path / "test_tree.yaml"
        override_file.write_text(
            yaml.dump(tree_yaml, allow_unicode=True), encoding="utf-8"
        )

        tree = load_tree("nahw", _REGISTRY_PATH, override_path=override_file)
        assert tree.leaf_count == 1
        assert tree.all_leaves[0].title == "ورقة ١"

    def test_nonexistent_science_raises(self) -> None:
        with pytest.raises(TreeLoadError) as exc_info:
            load_tree("nonexistent_science", _REGISTRY_PATH)
        assert exc_info.value.error_code == "TAX_INVALID_SCIENCE"

    def test_empty_yaml_raises(self, tmp_path: Path) -> None:
        empty_file = tmp_path / "empty.yaml"
        empty_file.write_text("", encoding="utf-8")
        with pytest.raises(TreeLoadError):
            load_tree("nahw", _REGISTRY_PATH, override_path=empty_file)

    def test_zero_leaves_raises(self, tmp_path: Path) -> None:
        tree_yaml = {
            "taxonomy": {
                "id": "empty_v1",
                "title": "Empty",
                "nodes": [
                    {"id": "branch_only", "title": "Branch"},
                ],
            }
        }
        tree_file = tmp_path / "no_leaves.yaml"
        tree_file.write_text(
            yaml.dump(tree_yaml, allow_unicode=True), encoding="utf-8"
        )
        with pytest.raises(TreeLoadError, match="zero leaves"):
            load_tree("nahw", _REGISTRY_PATH, override_path=tree_file)


# ── Branch and Leaf Views ─────────────────────────────────────────


class TestBranchLeafViews:
    def test_branch_view_contains_arabic(self, nahw_tree: LoadedTree) -> None:
        view = build_branch_view(nahw_tree.root_nodes)
        assert "مبادئ" in view
        assert "Branch:" in view

    def test_branch_view_has_root_nodes(self, nahw_tree: LoadedTree) -> None:
        view = build_branch_view(nahw_tree.root_nodes)
        for root in nahw_tree.root_nodes:
            assert root.id in view

    def test_leaf_view_contains_paths(self, aqidah_tree: LoadedTree) -> None:
        view = build_leaf_view(aqidah_tree.all_leaves)
        for leaf in aqidah_tree.all_leaves[:5]:
            assert leaf.path in view
            assert leaf.title in view

    def test_leaf_view_includes_parent(self, nahw_tree: LoadedTree) -> None:
        view = build_leaf_view(nahw_tree.all_leaves[:3])
        assert "(under:" in view
