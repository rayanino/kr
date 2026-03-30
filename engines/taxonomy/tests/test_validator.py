"""Tests for placement validation (SPEC §4.A.4).

Tests verify leaf existence checks and byte-identical Arabic text preservation.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.taxonomy.contracts_core import LoadedTree
from engines.taxonomy.src.validator import validate_placement, verify_written_file

# Arabic text with diacritics, ZWNJ, and various script features
_ARABIC_WITH_DIACRITICS = (
    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n"
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ"
)

_ARABIC_WITH_ZWNJ = (
    "بسم الله الرحمن الرحيم\n"
    "\u200c\u200cحروف الجر\n"
    "هاك حروف الجر وهي من إلى"
)

_ARABIC_WITH_MIXED_SCRIPT = (
    "قال ابن مالك في ألفيته:\n"
    "كلامنا لفظ مفيد كاستقم (Alfiyyah, v.1)"
)


# ── Leaf Validation ───────────────────────────────────────────────


class TestValidatePlacement:
    def test_valid_leaf_returns_true(self, nahw_tree: LoadedTree) -> None:
        valid_path = "muqaddimat/ta3rif_alnahw/ta3rif_alnahw_lugha"
        assert validate_placement(valid_path, nahw_tree) is True

    def test_nonexistent_path_returns_false(self, nahw_tree: LoadedTree) -> None:
        assert validate_placement("nonexistent/path", nahw_tree) is False

    def test_branch_path_returns_false(self, nahw_tree: LoadedTree) -> None:
        """Branch nodes are not valid placement targets."""
        assert validate_placement("muqaddimat", nahw_tree) is False

    def test_empty_string_returns_false(self, nahw_tree: LoadedTree) -> None:
        assert validate_placement("", nahw_tree) is False

    def test_aqidah_overview_leaf_valid(self, aqidah_tree: LoadedTree) -> None:
        """__overview nodes should be valid leaves."""
        overview_leaves = [
            leaf for leaf in aqidah_tree.all_leaves if "__overview" in leaf.id
        ]
        assert len(overview_leaves) > 0
        for leaf in overview_leaves:
            assert validate_placement(leaf.path, aqidah_tree) is True


# ── Byte-Identical Verification ───────────────────────────────────


class TestVerifyWrittenFile:
    def test_matching_arabic_text(self, tmp_path: Path) -> None:
        text = _ARABIC_WITH_DIACRITICS
        file_path = tmp_path / "test.json"
        file_path.write_text(
            json.dumps({"primary_text": text}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, text) is True

    def test_zwnj_preserved(self, tmp_path: Path) -> None:
        """ZWNJ characters (\u200c) must survive round-trip."""
        text = _ARABIC_WITH_ZWNJ
        file_path = tmp_path / "zwnj.json"
        file_path.write_text(
            json.dumps({"primary_text": text}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, text) is True

    def test_mixed_script_preserved(self, tmp_path: Path) -> None:
        text = _ARABIC_WITH_MIXED_SCRIPT
        file_path = tmp_path / "mixed.json"
        file_path.write_text(
            json.dumps({"primary_text": text}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, text) is True

    def test_corrupted_text_detected(self, tmp_path: Path) -> None:
        original = _ARABIC_WITH_DIACRITICS
        corrupted = original.replace("الرَّحْمَٰنِ", "الرحمن")
        file_path = tmp_path / "corrupt.json"
        file_path.write_text(
            json.dumps({"primary_text": corrupted}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, original) is False

    def test_missing_primary_text_field(self, tmp_path: Path) -> None:
        file_path = tmp_path / "no_field.json"
        file_path.write_text(
            json.dumps({"other_field": "value"}),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, "anything") is False

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        assert verify_written_file(tmp_path / "nope.json", "text") is False

    def test_whitespace_difference_detected(self, tmp_path: Path) -> None:
        original = "حروف الجر"
        modified = "حروف  الجر"  # Extra space
        file_path = tmp_path / "ws.json"
        file_path.write_text(
            json.dumps({"primary_text": modified}, ensure_ascii=False),
            encoding="utf-8",
        )
        assert verify_written_file(file_path, original) is False
