"""Tests for source freezing — SPEC §4.A.2 Steps 5-6.

Uses real Arabic fixtures from tests/fixtures/shamela_real/.
All tests are deterministic (no LLM calls).
"""

from __future__ import annotations

import shutil
import time
from pathlib import Path

import pytest

from engines.source.src.exceptions import SourceEngineError
from engines.source.src.freezer import (
    FreezeResult,
    freeze_source,
    verify_staging_integrity,
)
from engines.source.src.staging import compute_composite_hash, compute_file_hash

FIXTURES_ROOT = Path("tests/fixtures/shamela_real")


# ──────────────────────────────────────────────────────────────────
# TestFreezeSource
# ──────────────────────────────────────────────────────────────────


class TestFreezeSource:
    """Tests for freeze_source()."""

    def test_single_file_freeze(self, tmp_path: Path) -> None:
        """Freeze a single Shamela fixture and verify result shape."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)
        htm_file = staging / "book.htm"
        staging_hashes = {"book.htm": compute_file_hash(htm_file)}

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_test1234",
            library_root=tmp_path / "library",
            staging_hashes=staging_hashes,
        )

        # Assert
        assert isinstance(result, FreezeResult)
        assert result.source_id == "src_test1234"
        assert result.frozen_path.exists()
        assert result.frozen_path.is_dir()
        assert (result.frozen_path / "book.htm").exists()
        assert result.frozen_file_hashes["book.htm"] == staging_hashes["book.htm"]
        assert result.file_count == 1

    def test_multi_file_freeze(self, tmp_path: Path) -> None:
        """Freeze multi-volume fixture (3 files) and verify all files are frozen."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "11_multi_small", staging)
        staging_hashes: dict[str, str] = {}
        for f in sorted(staging.glob("*.htm")):
            staging_hashes[f.name] = compute_file_hash(f)

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_multi123",
            library_root=tmp_path / "library",
            staging_hashes=staging_hashes,
        )

        # Assert
        assert result.file_count == 3
        assert "001.htm" in result.frozen_file_hashes
        assert "002.htm" in result.frozen_file_hashes
        assert "003.htm" in result.frozen_file_hashes

        # Verify composite hash is deterministic
        expected_composite = compute_composite_hash(result.frozen_file_hashes)
        assert result.frozen_hash == expected_composite

    def test_frozen_files_byte_identical(self, tmp_path: Path) -> None:
        """Frozen files must be byte-identical to originals."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)
        staging_hashes = {"book.htm": compute_file_hash(staging / "book.htm")}

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_verify12",
            library_root=tmp_path / "library",
            staging_hashes=staging_hashes,
        )

        # Assert — re-hash independently to confirm byte identity
        frozen_hash = compute_file_hash(result.frozen_path / "book.htm")
        assert frozen_hash == staging_hashes["book.htm"]

    def test_hash_determinism(self, tmp_path: Path) -> None:
        """Same content produces same hash regardless of path."""
        # Arrange
        staging1 = tmp_path / "s1" / "source"
        staging2 = tmp_path / "s2" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging1)
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging2)

        # Act
        hash1 = compute_file_hash(staging1 / "book.htm")
        hash2 = compute_file_hash(staging2 / "book.htm")

        # Assert
        assert hash1 == hash2

    def test_muqaddima_included_in_hash(self, tmp_path: Path) -> None:
        """المقدمة.htm is included in staging hashes and present in frozen files."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "12_multi_muq", staging)
        staging_hashes: dict[str, str] = {}
        for f in sorted(staging.glob("*.htm")):
            staging_hashes[f.name] = compute_file_hash(f)

        # Assert fixture structure assumption
        assert "المقدمة.htm" in staging_hashes

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_muq12345",
            library_root=tmp_path / "library",
            staging_hashes=staging_hashes,
        )

        # Assert
        assert "المقدمة.htm" in result.frozen_file_hashes
        assert (result.frozen_path / "المقدمة.htm").exists()

    def test_frozen_directory_path_structure(self, tmp_path: Path) -> None:
        """Frozen directory follows library/sources/{source_id}/frozen/ layout."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)
        staging_hashes = {"book.htm": compute_file_hash(staging / "book.htm")}
        library_root = tmp_path / "library"

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_pathtest",
            library_root=library_root,
            staging_hashes=staging_hashes,
        )

        # Assert
        assert result.frozen_path == library_root / "sources" / "src_pathtest" / "frozen"

    def test_composite_hash_matches_frozen_files(self, tmp_path: Path) -> None:
        """frozen_hash is the composite hash of frozen_file_hashes, not staging hashes."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "11_multi_small", staging)
        staging_hashes = {
            f.name: compute_file_hash(f) for f in sorted(staging.glob("*.htm"))
        }

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_composite",
            library_root=tmp_path / "library",
            staging_hashes=staging_hashes,
        )

        # Assert
        recomputed = compute_composite_hash(result.frozen_file_hashes)
        assert result.frozen_hash == recomputed

    def test_freeze_creates_parent_directories(self, tmp_path: Path) -> None:
        """Freeze creates library/sources/{source_id}/frozen/ even if library is empty."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)
        staging_hashes = {"book.htm": compute_file_hash(staging / "book.htm")}
        # library_root does not exist yet
        library_root = tmp_path / "brand_new_library"

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_newlib00",
            library_root=library_root,
            staging_hashes=staging_hashes,
        )

        # Assert
        assert result.frozen_path.exists()


# ──────────────────────────────────────────────────────────────────
# TestVerifyStagingIntegrity
# ──────────────────────────────────────────────────────────────────


class TestVerifyStagingIntegrity:
    """Tests for TOCTOU staging lock detection via verify_staging_integrity()."""

    def test_unmodified_passes(self, tmp_path: Path) -> None:
        """Unmodified files pass integrity check without raising."""
        # Arrange
        staging = tmp_path / "source"
        staging.mkdir()
        test_file = staging / "book.htm"
        test_file.write_bytes(b"\xd9\x83\xd8\xaa\xd8\xa7\xd8\xa8")  # Arabic bytes

        mtime = test_file.stat().st_mtime
        hashes = {"book.htm": compute_file_hash(test_file)}
        timestamps = {"book.htm": mtime}

        # Act / Assert — should not raise
        verify_staging_integrity(staging, hashes, timestamps)

    def test_modified_file_raises(self, tmp_path: Path) -> None:
        """Modified file triggers SRC_STAGING_MODIFIED."""
        # Arrange
        staging = tmp_path / "source"
        staging.mkdir()
        test_file = staging / "book.htm"
        test_file.write_text("original", encoding="utf-8")

        mtime = test_file.stat().st_mtime
        timestamps = {"book.htm": mtime}
        hashes = {"book.htm": compute_file_hash(test_file)}

        # Ensure mtime changes on Windows (FAT/NTFS resolution can be coarse)
        time.sleep(0.11)
        test_file.write_text("modified content", encoding="utf-8")

        # Act / Assert
        with pytest.raises(SourceEngineError) as exc_info:
            verify_staging_integrity(staging, hashes, timestamps)

        assert exc_info.value.error.error_code.value == "SRC_STAGING_MODIFIED"

    def test_missing_file_raises(self, tmp_path: Path) -> None:
        """Deleted file triggers SRC_STAGING_MODIFIED."""
        # Arrange
        staging = tmp_path / "source"
        staging.mkdir()
        test_file = staging / "book.htm"
        test_file.write_text("content", encoding="utf-8")

        timestamps = {"book.htm": test_file.stat().st_mtime}
        hashes = {"book.htm": compute_file_hash(test_file)}

        test_file.unlink()

        # Act / Assert
        with pytest.raises(SourceEngineError) as exc_info:
            verify_staging_integrity(staging, hashes, timestamps)

        assert exc_info.value.error.error_code.value == "SRC_STAGING_MODIFIED"

    def test_single_file_path_not_dir(self, tmp_path: Path) -> None:
        """verify_staging_integrity handles staged_path pointing directly to a file."""
        # Arrange
        test_file = tmp_path / "book.htm"
        test_file.write_text("content", encoding="utf-8")

        mtime = test_file.stat().st_mtime
        hashes = {"book.htm": compute_file_hash(test_file)}
        timestamps = {"book.htm": mtime}

        # Act / Assert — should not raise when staged_path is the file itself
        verify_staging_integrity(test_file, hashes, timestamps)


# ──────────────────────────────────────────────────────────────────
# TestFreezeWithTOCTOU
# ──────────────────────────────────────────────────────────────────


class TestFreezeWithTOCTOU:
    """Tests for freeze_source() with TOCTOU timestamp checking."""

    def test_freeze_with_valid_timestamps(self, tmp_path: Path) -> None:
        """Freeze passes when timestamps match recorded values."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)

        htm = staging / "book.htm"
        hashes = {"book.htm": compute_file_hash(htm)}
        timestamps = {"book.htm": htm.stat().st_mtime}

        # Act
        result = freeze_source(
            staged_path=staging,
            source_id="src_toctou123",
            library_root=tmp_path / "library",
            staging_hashes=hashes,
            staging_timestamps=timestamps,
        )

        # Assert
        assert result.file_count == 1

    def test_freeze_rejects_modified_staging(self, tmp_path: Path) -> None:
        """Freeze aborts when staging file was modified after timestamps were recorded."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)

        htm = staging / "book.htm"
        hashes = {"book.htm": compute_file_hash(htm)}
        timestamps = {"book.htm": htm.stat().st_mtime}

        # Tamper with the file after recording timestamps
        time.sleep(0.11)
        htm.write_text("tampered content", encoding="utf-8")

        # Act / Assert
        with pytest.raises(SourceEngineError) as exc_info:
            freeze_source(
                staged_path=staging,
                source_id="src_tampered1",
                library_root=tmp_path / "library",
                staging_hashes=hashes,
                staging_timestamps=timestamps,
            )

        assert exc_info.value.error.error_code.value == "SRC_STAGING_MODIFIED"

    def test_freeze_without_timestamps_skips_toctou(self, tmp_path: Path) -> None:
        """Freeze proceeds normally when staging_timestamps is None."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "01_nahw_simple", staging)

        htm = staging / "book.htm"
        hashes = {"book.htm": compute_file_hash(htm)}

        # Modify the file — but no timestamps means no TOCTOU check
        time.sleep(0.11)
        original_bytes = htm.read_bytes()
        htm.write_bytes(original_bytes)  # same content, new mtime

        # Act — should succeed without TOCTOU check
        result = freeze_source(
            staged_path=staging,
            source_id="src_notoctou1",
            library_root=tmp_path / "library",
            staging_hashes=hashes,
            staging_timestamps=None,
        )

        assert result.file_count == 1

    def test_freeze_multi_volume_toctou(self, tmp_path: Path) -> None:
        """TOCTOU check works correctly for multi-volume sources."""
        # Arrange
        staging = tmp_path / "staging" / "source"
        shutil.copytree(FIXTURES_ROOT / "11_multi_small", staging)

        hashes = {f.name: compute_file_hash(f) for f in sorted(staging.glob("*.htm"))}
        timestamps = {f.name: f.stat().st_mtime for f in sorted(staging.glob("*.htm"))}

        # Act — all timestamps valid, should succeed
        result = freeze_source(
            staged_path=staging,
            source_id="src_multitoc1",
            library_root=tmp_path / "library",
            staging_hashes=hashes,
            staging_timestamps=timestamps,
        )

        assert result.file_count == 3
