"""Tests for atomic disk writer — SPEC §4.A.2.

Uses tmp_path pytest fixture for isolated filesystem operations.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.normalization.contracts import NormalizedManifest
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.writer import (
    recover_interrupted_write,
    write_normalized_package,
)
from engines.normalization.tests.conftest import _make_normalized_package


class TestWriteNormalizedPackage:
    """Tests for write_normalized_package()."""

    def test_write_creates_manifest_and_content(self, tmp_path: Path):
        """Writer produces manifest.json + content.jsonl at correct paths."""
        pkg = _make_normalized_package(num_units=3)
        result_dir = write_normalized_package(pkg, "src_test0001", tmp_path)
        assert result_dir == tmp_path / "sources" / "src_test0001" / "normalized"
        assert (result_dir / "manifest.json").exists()
        assert (result_dir / "content.jsonl").exists()

    def test_manifest_is_valid_json(self, tmp_path: Path):
        """Written manifest.json is parseable as JSON and as NormalizedManifest."""
        pkg = _make_normalized_package(num_units=2)
        result_dir = write_normalized_package(pkg, "src_test0001", tmp_path)
        manifest_path = result_dir / "manifest.json"
        with open(manifest_path, encoding="utf-8") as f:
            data = json.load(f)
        # Must be parseable as NormalizedManifest
        parsed = NormalizedManifest.model_validate(data)
        assert parsed.source_id == "src_test0001"
        assert parsed.total_content_units == 2

    def test_content_jsonl_line_count(self, tmp_path: Path):
        """content.jsonl line count == len(content_units)."""
        pkg = _make_normalized_package(num_units=5)
        result_dir = write_normalized_package(pkg, "src_test0001", tmp_path)
        content_path = result_dir / "content.jsonl"
        with open(content_path, encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        assert len(lines) == 5

    def test_each_jsonl_line_is_valid_json(self, tmp_path: Path):
        """Every line in content.jsonl parses as valid JSON."""
        pkg = _make_normalized_package(num_units=3)
        result_dir = write_normalized_package(pkg, "src_test0001", tmp_path)
        content_path = result_dir / "content.jsonl"
        with open(content_path, encoding="utf-8") as f:
            for i, line in enumerate(f):
                if line.strip():
                    data = json.loads(line)
                    assert data["unit_index"] == i

    def test_reprocessing_replaces_old(self, tmp_path: Path):
        """When normalized/ already exists, old is replaced by new write."""
        pkg1 = _make_normalized_package(num_units=2)
        write_normalized_package(pkg1, "src_test0001", tmp_path)

        pkg2 = _make_normalized_package(num_units=4)
        result_dir = write_normalized_package(pkg2, "src_test0001", tmp_path)

        # Should have 4 units now (from pkg2)
        content_path = result_dir / "content.jsonl"
        with open(content_path, encoding="utf-8") as f:
            lines = [line for line in f if line.strip()]
        assert len(lines) == 4

        # No prev dirs should remain
        base = tmp_path / "sources" / "src_test0001"
        prev_dirs = list(base.glob("normalized_prev_*"))
        assert len(prev_dirs) == 0

    def test_no_temp_dirs_remain_after_success(self, tmp_path: Path):
        """After successful write, no temp directories remain."""
        pkg = _make_normalized_package(num_units=2)
        write_normalized_package(pkg, "src_test0001", tmp_path)
        base = tmp_path / "sources" / "src_test0001"
        temp_dirs = list(base.glob("normalized_tmp_*"))
        assert len(temp_dirs) == 0

    def test_write_failure_raises_norm_write_failed(self, tmp_path: Path):
        """Write failure → NORM_WRITE_FAILED raised, no temp remains."""
        pkg = _make_normalized_package(num_units=2)
        # Use a non-existent path that we block by creating a file with same name
        # as the expected directory
        blocked_base = tmp_path / "sources" / "src_blocked"
        blocked_base.mkdir(parents=True)
        # Create a FILE named "normalized_tmp_..." so mkdir inside write fails
        # Actually, a simpler approach: pass a path to a file as library_root
        fake_root = tmp_path / "not_a_dir.txt"
        fake_root.write_text("block")

        with pytest.raises(NormalizationError) as exc_info:
            write_normalized_package(pkg, "src_test0001", fake_root)
        assert exc_info.value.code == NormErrorCode.WRITE_FAILED


class TestRecoverInterruptedWrite:
    """Tests for recover_interrupted_write()."""

    def test_no_recovery_needed(self, tmp_path: Path):
        """No temp dirs → returns False."""
        base = tmp_path / "sources" / "src_test0001"
        base.mkdir(parents=True)
        result = recover_interrupted_write("src_test0001", tmp_path)
        assert result is False

    def test_recovery_valid_temp_promoted(self, tmp_path: Path):
        """Valid temp dir (with both files) → promoted to normalized/."""
        base = tmp_path / "sources" / "src_test0001"
        temp = base / "normalized_tmp_20260317T120000"
        temp.mkdir(parents=True)

        # Write valid files into temp
        pkg = _make_normalized_package(num_units=2)
        manifest_path = temp / "manifest.json"
        manifest_path.write_text(pkg.manifest.model_dump_json(indent=2), encoding="utf-8")
        content_path = temp / "content.jsonl"
        with open(content_path, "w", encoding="utf-8") as f:
            for cu in pkg.content_units:
                f.write(cu.model_dump_json() + "\n")

        # Create a prev dir as well
        prev = base / "normalized_prev_20260317T115500"
        prev.mkdir(parents=True)
        (prev / "manifest.json").write_text("{}", encoding="utf-8")

        result = recover_interrupted_write("src_test0001", tmp_path)
        assert result is True
        assert (base / "normalized").exists()
        assert not temp.exists()
        assert not prev.exists()

    def test_adv047_invalid_temp_restores_from_latest_prev(self, tmp_path: Path):
        """ADV-047: invalid temp + multiple prev dirs → restore from LATEST prev."""
        base = tmp_path / "sources" / "src_test0001"

        # Invalid temp (missing content.jsonl)
        temp = base / "normalized_tmp_20260317T120000"
        temp.mkdir(parents=True)
        (temp / "manifest.json").write_text('{"source_id": "test"}', encoding="utf-8")
        # No content.jsonl → invalid

        # Two prev dirs with valid files
        prev_old = base / "normalized_prev_20260317T110000"
        prev_old.mkdir(parents=True)
        (prev_old / "manifest.json").write_text('{"old": true}', encoding="utf-8")
        (prev_old / "content.jsonl").write_text('{"unit_index": 0}\n', encoding="utf-8")

        prev_latest = base / "normalized_prev_20260317T115500"
        prev_latest.mkdir(parents=True)
        (prev_latest / "manifest.json").write_text('{"latest": true}', encoding="utf-8")
        (prev_latest / "content.jsonl").write_text('{"unit_index": 0}\n', encoding="utf-8")

        result = recover_interrupted_write("src_test0001", tmp_path)
        assert result is True

        # Should have restored from latest (T115500)
        normalized = base / "normalized"
        assert normalized.exists()
        with open(normalized / "manifest.json", encoding="utf-8") as f:
            data = json.load(f)
        assert data.get("latest") is True

        # All temp and prev dirs cleaned up
        assert not temp.exists()
        assert not prev_old.exists()
        assert not prev_latest.exists()

    def test_orphaned_temp_with_normalized_existing(self, tmp_path: Path):
        """Temp exists but normalized/ also exists → just clean temp."""
        base = tmp_path / "sources" / "src_test0001"
        normalized = base / "normalized"
        normalized.mkdir(parents=True)
        (normalized / "manifest.json").write_text("{}", encoding="utf-8")

        temp = base / "normalized_tmp_20260317T120000"
        temp.mkdir(parents=True)
        (temp / "manifest.json").write_text("{}", encoding="utf-8")

        result = recover_interrupted_write("src_test0001", tmp_path)
        assert result is True
        assert normalized.exists()  # kept
        assert not temp.exists()  # cleaned

    def test_nonexistent_base_dir_returns_false(self, tmp_path: Path):
        """Base dir doesn't exist → returns False."""
        result = recover_interrupted_write("src_nonexistent", tmp_path)
        assert result is False
