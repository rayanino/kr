"""Source engine tests using real Arabic scholarly fixtures."""

import json
import os
from pathlib import Path

import pytest

from engines.source.src.format_detector import detect_format
from engines.source.src.freezer import freeze_source, verify_frozen_integrity, FreezeError
from engines.source.src.identity import (
    compute_file_hash,
    generate_source_id,
    generate_work_id,
    generate_human_label,
)
from engines.source.src.intake import intake_source, IntakeError
from engines.source.src.registry import SourceRegistry


# ──────────────────────────────────────────────────────────────────
# Format Detection
# ──────────────────────────────────────────────────────────────────

class TestFormatDetection:
    def test_pdf_detection(self, waraqat_pdf):
        fmt = detect_format(waraqat_pdf)
        assert fmt in ("pdf_text", "pdf_scanned")

    def test_text_detection(self, alfiyyah_txt):
        fmt = detect_format(alfiyyah_txt)
        assert fmt == "plain_text"

    def test_image_directory_detection(self, photo_scan_dir):
        fmt = detect_format(photo_scan_dir)
        assert fmt == "image_scan"

    def test_unsupported_format(self, tmp_path):
        bad_file = tmp_path / "test.xyz"
        bad_file.write_text("test")
        with pytest.raises(ValueError, match="SRC_UNSUPPORTED_FORMAT"):
            detect_format(bad_file)

    def test_nonexistent_path(self, tmp_path):
        with pytest.raises(ValueError, match="SRC_UNSUPPORTED_FORMAT"):
            detect_format(tmp_path / "nonexistent.pdf")


# ──────────────────────────────────────────────────────────────────
# Identity Model
# ──────────────────────────────────────────────────────────────────

class TestIdentity:
    def test_source_id_format(self):
        sid = generate_source_id("abcdef1234567890abcdef1234567890abcdef1234567890abcdef1234567890")
        assert sid.startswith("src_")
        assert len(sid) == 12  # src_ + 8 hex chars

    def test_source_id_deterministic(self):
        hash1 = "abcdef1234567890abcdef1234567890"
        assert generate_source_id(hash1) == generate_source_id(hash1)

    def test_work_id_arabic(self):
        wid = generate_work_id("ابن مالك", "ألفية ابن مالك")
        assert wid.startswith("wrk_")
        assert len(wid) <= 44
        # Should contain transliterated parts
        assert "abn" in wid or "malik" in wid.lower() or "malk" in wid.lower()

    def test_human_label(self):
        label = generate_human_label("ألفية ابن مالك")
        assert len(label) > 0
        assert len(label) <= 30


# ──────────────────────────────────────────────────────────────────
# Freezer
# ──────────────────────────────────────────────────────────────────

class TestFreezer:
    def test_freeze_single_file(self, waraqat_pdf, tmp_path):
        frozen_dir = tmp_path / "frozen"
        composite_hash, file_hashes = freeze_source(waraqat_pdf, frozen_dir)

        assert len(composite_hash) == 64  # SHA-256 hex
        assert len(file_hashes) == 1
        assert "waraqat.pdf" in file_hashes

        # File should exist and be set to read-only mode (0o444)
        frozen_file = frozen_dir / "waraqat.pdf"
        assert frozen_file.exists()
        file_mode = oct(frozen_file.stat().st_mode)[-3:]
        assert file_mode == "444", f"Expected mode 444, got {file_mode}"

    def test_freeze_directory(self, photo_scan_dir, tmp_path):
        frozen_dir = tmp_path / "frozen"
        composite_hash, file_hashes = freeze_source(photo_scan_dir, frozen_dir)

        assert len(composite_hash) == 64
        assert len(file_hashes) >= 1  # Multiple photos

    def test_freeze_deterministic(self, waraqat_pdf, tmp_path):
        dir1 = tmp_path / "frozen1"
        dir2 = tmp_path / "frozen2"
        hash1, _ = freeze_source(waraqat_pdf, dir1)
        hash2, _ = freeze_source(waraqat_pdf, dir2)
        assert hash1 == hash2

    def test_verify_integrity_ok(self, waraqat_pdf, tmp_path):
        frozen_dir = tmp_path / "frozen"
        _, file_hashes = freeze_source(waraqat_pdf, frozen_dir)

        errors = verify_frozen_integrity(frozen_dir, file_hashes)
        assert errors == []

    def test_freeze_nonexistent(self, tmp_path):
        with pytest.raises(FreezeError):
            freeze_source(tmp_path / "nonexistent", tmp_path / "frozen")


# ──────────────────────────────────────────────────────────────────
# Registry
# ──────────────────────────────────────────────────────────────────

class TestRegistry:
    def test_register_and_find(self, tmp_path):
        reg = SourceRegistry(tmp_path / "sources.json")
        reg.register(
            source_id="src_test1234",
            work_id="wrk_test",
            title_arabic="اختبار",
            author_canonical_id="sch_unresolved",
            trust_tier="flagged",
            frozen_hash="abc123",
            acquisition_path="manual",
        )

        assert reg.exists("src_test1234")
        assert reg.find_by_hash("abc123") == "src_test1234"
        assert reg.find_by_hash("nonexistent") is None

    def test_persistence(self, tmp_path):
        path = tmp_path / "sources.json"
        reg1 = SourceRegistry(path)
        reg1.register("src_a", "wrk_a", "test", "sch_00001", "flagged", "hash_a", "manual")

        # New instance should see the same data
        reg2 = SourceRegistry(path)
        assert reg2.exists("src_a")


# ──────────────────────────────────────────────────────────────────
# End-to-End Intake
# ──────────────────────────────────────────────────────────────────

class TestIntake:
    def test_pdf_intake(self, waraqat_pdf, tmp_library):
        result = intake_source(waraqat_pdf, library_root=tmp_library)

        assert result["source_id"].startswith("src_")
        assert result["work_id"].startswith("wrk_")
        assert result["source_format"] in ("pdf_text", "pdf_scanned")

        # Check metadata.json was created and is valid
        metadata_path = Path(result["metadata_path"])
        assert metadata_path.exists()
        with open(metadata_path) as f:
            metadata = json.load(f)

        assert metadata["source_id"] == result["source_id"]
        assert metadata["status"] == "acquired"
        assert metadata["frozen_hash"]
        assert len(metadata["frozen_file_hashes"]) == 1

        # Check frozen file exists
        frozen_dir = Path(result["frozen_dir"])
        assert frozen_dir.exists()
        frozen_files = list(frozen_dir.iterdir())
        assert len(frozen_files) == 1

        # Check registry was updated
        reg = SourceRegistry(tmp_library / "registries" / "sources.json")
        assert reg.exists(result["source_id"])

    def test_duplicate_detection(self, waraqat_pdf, tmp_library):
        # First intake should succeed
        intake_source(waraqat_pdf, library_root=tmp_library)

        # Second intake of same file should be rejected
        with pytest.raises(IntakeError, match="SRC_DUPLICATE_EXACT"):
            intake_source(waraqat_pdf, library_root=tmp_library)

    def test_text_intake(self, alfiyyah_txt, tmp_library):
        result = intake_source(alfiyyah_txt, library_root=tmp_library)

        assert result["source_format"] == "plain_text"
        metadata_path = Path(result["metadata_path"])
        with open(metadata_path) as f:
            metadata = json.load(f)
        # Title should be extracted from first line of text
        assert metadata["title_arabic"] is not None
        assert len(metadata["title_arabic"]) > 0

    def test_empty_file_rejected(self, tmp_library, tmp_path):
        empty_file = tmp_path / "empty.pdf"
        empty_file.write_bytes(b"")
        with pytest.raises(IntakeError, match="SRC_EMPTY_INPUT"):
            intake_source(empty_file, library_root=tmp_library)

    def test_owner_hints_override(self, waraqat_pdf, tmp_library):
        result = intake_source(
            waraqat_pdf,
            library_root=tmp_library,
            owner_hints={"title": "الورقات في أصول الفقه", "author": "إمام الحرمين الجويني"},
        )
        with open(result["metadata_path"]) as f:
            metadata = json.load(f)

        assert metadata["title_arabic"] == "الورقات في أصول الفقه"
        assert metadata["author"]["name_arabic"] == "إمام الحرمين الجويني"
        assert metadata["author"]["confidence"] >= 0.5  # Owner-provided = higher confidence
