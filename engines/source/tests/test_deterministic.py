"""Deterministic tests for source engine Sessions 1-2.

Session 1: Staging Pipeline + Format Detection (SPEC §4.A.2)
Session 2: Shamela HTML + Plain Text Extraction (SPEC §4.A.3)

All tests use real Arabic fixtures from tests/fixtures/.
"""

from __future__ import annotations

import json
import time
from pathlib import Path

import pytest

from engines.source.contracts import ErrorCode, SourceFormat
from engines.source.src.config import SourceEngineConfig
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.format_detection import _is_shamela_html, detect_format
from engines.source.src.staging import (
    StagingResult,
    cleanup_orphaned_locks,
    compute_composite_hash,
    compute_file_hash,
    create_staging_lock,
    derive_source_id,
    record_file_timestamps,
    remove_staging_lock,
    stage_source,
    verify_timestamps_unchanged,
)

# ──────────────────────────────────────────────────────────────────
# Fixture paths (hardcoded — tests/fixtures/ is in .claudeignore)
# ──────────────────────────────────────────────────────────────────

FIXTURES_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
SHAMELA_ROOT = FIXTURES_ROOT / "shamela_real"
ALFIYYAH_PATH = FIXTURES_ROOT / "alfiyyah_versified" / "alfiyyah.txt"

ALL_SHAMELA_FIXTURES = [
    "01_nahw_simple",
    "02_nahw_muhaqiq",
    "03_fiqh",
    "04_hadith",
    "05_tafsir",
    "06_usul",
    "07_balagha",
    "08_death_date",
    "09_alt_title",
    "10_no_author",
    "11_multi_small",
    "12_multi_muq",
]


# ──────────────────────────────────────────────────────────────────
# Format Detection
# ──────────────────────────────────────────────────────────────────


class TestFormatDetection:
    """Tests for detect_format() — SPEC §4.A.2 Step 2."""

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_shamela_directory_detection(self, fixture_name: str) -> None:
        """Each shamela fixture directory is detected as SHAMELA_HTML."""
        path = SHAMELA_ROOT / fixture_name
        assert path.exists(), f"Fixture missing: {path}"
        assert detect_format(path) == SourceFormat.SHAMELA_HTML

    def test_shamela_single_file_detection(self) -> None:
        """A single .htm Shamela file is detected as SHAMELA_HTML."""
        path = SHAMELA_ROOT / "01_nahw_simple" / "book.htm"
        assert detect_format(path) == SourceFormat.SHAMELA_HTML

    def test_plain_text_file_detection(self) -> None:
        """alfiyyah.txt plain text is detected as PLAIN_TEXT."""
        assert ALFIYYAH_PATH.exists(), f"Fixture missing: {ALFIYYAH_PATH}"
        assert detect_format(ALFIYYAH_PATH) == SourceFormat.PLAIN_TEXT

    def test_plain_text_directory_detection(self, tmp_path: Path) -> None:
        """Directory with a single .txt file is detected as PLAIN_TEXT."""
        txt_file = tmp_path / "sample.txt"
        txt_file.write_text("بسم الله الرحمن الرحيم", encoding="utf-8")
        assert detect_format(tmp_path) == SourceFormat.PLAIN_TEXT

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        """A .pdf file raises UNSUPPORTED_FORMAT."""
        pdf_file = tmp_path / "test.pdf"
        pdf_file.write_bytes(b"%PDF-1.4")
        with pytest.raises(SourceEngineError) as exc_info:
            detect_format(pdf_file)
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT

    def test_empty_file_raises(self, tmp_path: Path) -> None:
        """An empty .txt file raises EMPTY_INPUT."""
        empty = tmp_path / "empty.txt"
        empty.write_text("")
        with pytest.raises(SourceEngineError) as exc_info:
            detect_format(empty)
        assert exc_info.value.error.error_code == ErrorCode.EMPTY_INPUT

    def test_empty_directory_raises(self, tmp_path: Path) -> None:
        """An empty directory raises EMPTY_INPUT."""
        empty_dir = tmp_path / "empty_source"
        empty_dir.mkdir()
        with pytest.raises(SourceEngineError) as exc_info:
            detect_format(empty_dir)
        assert exc_info.value.error.error_code == ErrorCode.EMPTY_INPUT

    def test_non_shamela_html_raises(self, tmp_path: Path) -> None:
        """An HTML file without Shamela markers raises UNSUPPORTED_FORMAT."""
        html_file = tmp_path / "generic.htm"
        html_file.write_text("<html><body><p>Hello</p></body></html>", encoding="utf-8")
        with pytest.raises(SourceEngineError) as exc_info:
            detect_format(html_file)
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT

    def test_multi_volume_shamela_directory(self) -> None:
        """11_multi_small (3 .htm files) detected as SHAMELA_HTML."""
        path = SHAMELA_ROOT / "11_multi_small"
        assert detect_format(path) == SourceFormat.SHAMELA_HTML

    def test_multi_volume_with_arabic_filename(self) -> None:
        """12_multi_muq (contains المقدمة.htm) detected as SHAMELA_HTML."""
        path = SHAMELA_ROOT / "12_multi_muq"
        assert detect_format(path) == SourceFormat.SHAMELA_HTML

    def test_nonexistent_path_raises(self, tmp_path: Path) -> None:
        """A nonexistent path raises UNSUPPORTED_FORMAT."""
        with pytest.raises(SourceEngineError) as exc_info:
            detect_format(tmp_path / "does_not_exist")
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT


# ──────────────────────────────────────────────────────────────────
# Shamela HTML Marker Detection
# ──────────────────────────────────────────────────────────────────


class TestIsShamelaHtml:
    """Tests for _is_shamela_html() marker detection."""

    def test_real_fixture_has_all_markers(self) -> None:
        """Real fixture 01 has all three Shamela detection markers."""
        path = SHAMELA_ROOT / "01_nahw_simple" / "book.htm"
        assert _is_shamela_html(path) is True

    def test_missing_page_text_marker(self, tmp_path: Path) -> None:
        """HTML with Main and title but no PageText fails detection."""
        f = tmp_path / "test.htm"
        f.write_text(
            "<div class='Main'><span class='title'>test</span></div>",
            encoding="utf-8",
        )
        assert _is_shamela_html(f) is False

    def test_missing_main_marker(self, tmp_path: Path) -> None:
        """HTML with PageText and title but no Main fails detection."""
        f = tmp_path / "test.htm"
        f.write_text(
            "<div class='PageText'><span class='title'>test</span></div>",
            encoding="utf-8",
        )
        assert _is_shamela_html(f) is False

    def test_missing_title_marker(self, tmp_path: Path) -> None:
        """HTML with PageText and Main but no title span fails detection."""
        f = tmp_path / "test.htm"
        f.write_text(
            "<div class='Main'><div class='PageText'>test</div></div>",
            encoding="utf-8",
        )
        assert _is_shamela_html(f) is False


# ──────────────────────────────────────────────────────────────────
# SHA-256 Hashing
# ──────────────────────────────────────────────────────────────────


class TestHashing:
    """Tests for compute_file_hash() and compute_composite_hash()."""

    def test_sha256_deterministic(self) -> None:
        """Same file always produces the same SHA-256 hash."""
        path = SHAMELA_ROOT / "01_nahw_simple" / "book.htm"
        h1 = compute_file_hash(path)
        h2 = compute_file_hash(path)
        assert h1 == h2
        assert len(h1) == 64  # SHA-256 hex is 64 chars

    def test_different_files_different_hashes(self) -> None:
        """Different fixtures produce different hashes."""
        h1 = compute_file_hash(SHAMELA_ROOT / "01_nahw_simple" / "book.htm")
        h2 = compute_file_hash(SHAMELA_ROOT / "02_nahw_muhaqiq" / "book.htm")
        assert h1 != h2

    def test_composite_hash_deterministic(self) -> None:
        """Composite hash is deterministic for the same file hashes."""
        hashes = {"a.htm": "abc123", "b.htm": "def456"}
        c1 = compute_composite_hash(hashes)
        c2 = compute_composite_hash(hashes)
        assert c1 == c2
        assert len(c1) == 64

    def test_composite_hash_order_independent(self) -> None:
        """Composite hash is the same regardless of dict insertion order."""
        h1 = compute_composite_hash({"b.htm": "def", "a.htm": "abc"})
        h2 = compute_composite_hash({"a.htm": "abc", "b.htm": "def"})
        assert h1 == h2

    def test_multi_volume_composite_hash(self) -> None:
        """11_multi_small composite hash includes all 3 volume files."""
        path = SHAMELA_ROOT / "11_multi_small"
        file_hashes = {}
        for f in sorted(path.iterdir()):
            if f.is_file():
                file_hashes[f.name] = compute_file_hash(f)
        assert len(file_hashes) == 3
        composite = compute_composite_hash(file_hashes)
        assert len(composite) == 64

    def test_alfiyyah_plain_text_hash(self) -> None:
        """alfiyyah.txt produces a valid SHA-256 hash."""
        h = compute_file_hash(ALFIYYAH_PATH)
        assert len(h) == 64
        assert all(c in "0123456789abcdef" for c in h)


# ──────────────────────────────────────────────────────────────────
# Source ID Generation
# ──────────────────────────────────────────────────────────────────


class TestSourceIdGeneration:
    """Tests for derive_source_id() — SPEC §4.A.1."""

    def test_source_id_format(self) -> None:
        """source_id is src_{8_hex_chars}."""
        hash_val = "a7c3e91fabcdef1234567890abcdef1234567890abcdef1234567890abcdef12"
        sid = derive_source_id(hash_val)
        assert sid == "src_a7c3e91f"
        assert sid.startswith("src_")
        assert len(sid) == 12  # "src_" (4) + 8 hex chars

    def test_no_collision_no_suffix(self) -> None:
        """Without collision, no suffix is added."""
        existing = {"src_different1"}
        sid = derive_source_id(
            "a7c3e91fabcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
            existing_ids=existing,
        )
        assert sid == "src_a7c3e91f"

    def test_collision_appends_suffix(self) -> None:
        """First collision appends _2."""
        existing = {"src_a7c3e91f"}
        sid = derive_source_id(
            "a7c3e91fabcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
            existing_ids=existing,
        )
        assert sid == "src_a7c3e91f_2"

    def test_double_collision_appends_3(self) -> None:
        """Double collision appends _3."""
        existing = {"src_a7c3e91f", "src_a7c3e91f_2"}
        sid = derive_source_id(
            "a7c3e91fabcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
            existing_ids=existing,
        )
        assert sid == "src_a7c3e91f_3"

    def test_none_existing_ids(self) -> None:
        """None existing_ids means no collision check."""
        sid = derive_source_id(
            "a7c3e91fabcdef1234567890abcdef1234567890abcdef1234567890abcdef12",
            existing_ids=None,
        )
        assert sid == "src_a7c3e91f"


# ──────────────────────────────────────────────────────────────────
# Staging Locks
# ──────────────────────────────────────────────────────────────────


class TestStagingLock:
    """Tests for staging lock creation, removal, and cleanup."""

    def test_lock_creation(self, tmp_path: Path) -> None:
        """create_staging_lock creates .kr_processing file in directory."""
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        (source_dir / "book.htm").write_text("content", encoding="utf-8")
        lock = create_staging_lock(source_dir)
        assert lock.exists()
        assert lock.name == ".kr_processing"

    def test_lock_contains_metadata(self, tmp_path: Path) -> None:
        """Lock file contains created_at timestamp and pid."""
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        lock = create_staging_lock(source_dir)
        data = json.loads(lock.read_text(encoding="utf-8"))
        assert "created_at" in data
        assert "pid" in data
        assert isinstance(data["pid"], int)

    def test_lock_removal(self, tmp_path: Path) -> None:
        """remove_staging_lock deletes the lock file."""
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        lock = create_staging_lock(source_dir)
        assert lock.exists()
        remove_staging_lock(lock)
        assert not lock.exists()

    def test_lock_removal_idempotent(self, tmp_path: Path) -> None:
        """Removing a non-existent lock does not raise."""
        remove_staging_lock(tmp_path / ".kr_processing")

    def test_duplicate_lock_raises(self, tmp_path: Path) -> None:
        """Creating a lock when one exists raises STAGING_MODIFIED."""
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        create_staging_lock(source_dir)
        with pytest.raises(SourceEngineError) as exc_info:
            create_staging_lock(source_dir)
        assert exc_info.value.error.error_code == ErrorCode.STAGING_MODIFIED

    def test_orphaned_lock_cleanup(self, tmp_path: Path) -> None:
        """Locks older than timeout are cleaned up."""
        source_dir = tmp_path / "test_source"
        source_dir.mkdir()
        lock = create_staging_lock(source_dir)
        # Artificially age the lock by rewriting with old timestamp
        old_data = json.dumps(
            {
                "created_at": "2020-01-01T00:00:00+00:00",
                "pid": 12345,
            }
        )
        lock.write_text(old_data, encoding="utf-8")
        removed = cleanup_orphaned_locks(tmp_path, timeout_seconds=1)
        assert len(removed) == 1
        assert not lock.exists()


# ──────────────────────────────────────────────────────────────────
# Timestamp Recording
# ──────────────────────────────────────────────────────────────────


class TestTimestampRecording:
    """Tests for TOCTOU timestamp recording and verification."""

    def test_record_timestamps_multi_volume(self) -> None:
        """record_file_timestamps captures mtime for each file in 11_multi_small."""
        path = SHAMELA_ROOT / "11_multi_small"
        ts = record_file_timestamps(path)
        assert len(ts) == 3
        assert "001.htm" in ts
        assert "002.htm" in ts
        assert "003.htm" in ts

    def test_record_timestamps_single_file(self) -> None:
        """record_file_timestamps works for a single file."""
        ts = record_file_timestamps(ALFIYYAH_PATH)
        assert len(ts) == 1
        assert "alfiyyah.txt" in ts

    def test_verify_unchanged_passes(self, tmp_path: Path) -> None:
        """Unchanged files pass timestamp verification."""
        f = tmp_path / "test.txt"
        f.write_text("بسم الله", encoding="utf-8")
        ts = record_file_timestamps(tmp_path)
        verify_timestamps_unchanged(tmp_path, ts)  # Should not raise

    def test_verify_changed_raises(self, tmp_path: Path) -> None:
        """Modified file triggers STAGING_MODIFIED."""
        f = tmp_path / "test.txt"
        f.write_text("original content", encoding="utf-8")
        ts = record_file_timestamps(tmp_path)
        # Ensure filesystem timestamp changes
        time.sleep(0.05)
        f.write_text("modified content", encoding="utf-8")
        with pytest.raises(SourceEngineError) as exc_info:
            verify_timestamps_unchanged(tmp_path, ts)
        assert exc_info.value.error.error_code == ErrorCode.STAGING_MODIFIED

    def test_verify_deleted_file_raises(self, tmp_path: Path) -> None:
        """Deleted file triggers STAGING_MODIFIED."""
        f = tmp_path / "test.txt"
        f.write_text("content", encoding="utf-8")
        ts = record_file_timestamps(tmp_path)
        f.unlink()
        with pytest.raises(SourceEngineError) as exc_info:
            verify_timestamps_unchanged(tmp_path, ts)
        assert exc_info.value.error.error_code == ErrorCode.STAGING_MODIFIED


# ──────────────────────────────────────────────────────────────────
# Integration: stage_source()
# ──────────────────────────────────────────────────────────────────


class TestStageSource:
    """Integration tests for the stage_source() orchestrator."""

    def test_stage_shamela_single_volume(self, tmp_path: Path) -> None:
        """Stage a copied shamela fixture end-to-end."""
        import shutil

        source_dir = tmp_path / "staging" / "test_source"
        shutil.copytree(SHAMELA_ROOT / "01_nahw_simple", source_dir)

        config = SourceEngineConfig(staging_path=tmp_path / "staging")
        result = stage_source(source_dir, config)

        assert isinstance(result, StagingResult)
        assert result.source_format == SourceFormat.SHAMELA_HTML
        assert result.source_id.startswith("src_")
        assert len(result.source_id) == 12
        assert len(result.file_hashes) == 1
        assert "book.htm" in result.file_hashes
        assert len(result.composite_hash) == 64
        assert result.lock_path.exists()

        # Cleanup lock
        remove_staging_lock(result.lock_path)

    def test_stage_multi_volume(self, tmp_path: Path) -> None:
        """Stage multi-volume shamela fixture."""
        import shutil

        source_dir = tmp_path / "staging" / "multi_test"
        shutil.copytree(SHAMELA_ROOT / "11_multi_small", source_dir)

        config = SourceEngineConfig(staging_path=tmp_path / "staging")
        result = stage_source(source_dir, config)

        assert result.source_format == SourceFormat.SHAMELA_HTML
        assert len(result.file_hashes) == 3
        assert len(result.file_timestamps) == 3
        assert "001.htm" in result.file_hashes
        assert "002.htm" in result.file_hashes
        assert "003.htm" in result.file_hashes

        remove_staging_lock(result.lock_path)

    def test_stage_plain_text(self, tmp_path: Path) -> None:
        """Stage a plain text file."""
        import shutil

        staging = tmp_path / "staging"
        staging.mkdir()
        txt_file = staging / "alfiyyah.txt"
        shutil.copy2(ALFIYYAH_PATH, txt_file)

        config = SourceEngineConfig(staging_path=staging)
        result = stage_source(txt_file, config)

        assert result.source_format == SourceFormat.PLAIN_TEXT
        assert result.source_id.startswith("src_")
        assert len(result.file_hashes) == 1
        assert "alfiyyah.txt" in result.file_hashes

        remove_staging_lock(result.lock_path)

    def test_stage_deterministic_source_id(self, tmp_path: Path) -> None:
        """Same source staged twice produces the same source_id."""
        import shutil

        # Stage once
        dir1 = tmp_path / "staging1" / "source"
        shutil.copytree(SHAMELA_ROOT / "01_nahw_simple", dir1)
        config1 = SourceEngineConfig(staging_path=tmp_path / "staging1")
        r1 = stage_source(dir1, config1)
        remove_staging_lock(r1.lock_path)

        # Stage again (different staging dir, same content)
        dir2 = tmp_path / "staging2" / "source"
        shutil.copytree(SHAMELA_ROOT / "01_nahw_simple", dir2)
        config2 = SourceEngineConfig(staging_path=tmp_path / "staging2")
        r2 = stage_source(dir2, config2)
        remove_staging_lock(r2.lock_path)

        assert r1.source_id == r2.source_id
        assert r1.composite_hash == r2.composite_hash

    def test_stage_muqaddima_with_arabic_filename(self, tmp_path: Path) -> None:
        """Stage fixture 12 with المقدمة.htm (Arabic filename)."""
        import shutil

        source_dir = tmp_path / "staging" / "muq_test"
        shutil.copytree(SHAMELA_ROOT / "12_multi_muq", source_dir)

        config = SourceEngineConfig(staging_path=tmp_path / "staging")
        result = stage_source(source_dir, config)

        assert result.source_format == SourceFormat.SHAMELA_HTML
        assert len(result.file_hashes) == 2
        # Arabic filename preserved exactly
        assert "\u0627\u0644\u0645\u0642\u062f\u0645\u0629.htm" in result.file_hashes

        remove_staging_lock(result.lock_path)

    def test_stage_nonexistent_raises(self, tmp_path: Path) -> None:
        """Staging a nonexistent path raises."""
        config = SourceEngineConfig(staging_path=tmp_path)
        with pytest.raises(SourceEngineError):
            stage_source(tmp_path / "nonexistent", config)

    def test_stage_cleans_lock_on_failure(self, tmp_path: Path) -> None:
        """Lock is cleaned up if staging fails after lock creation."""
        empty_dir = tmp_path / "staging" / "empty"
        empty_dir.mkdir(parents=True)
        config = SourceEngineConfig(staging_path=tmp_path / "staging")

        with pytest.raises(SourceEngineError):
            stage_source(empty_dir, config)

        # Lock should not persist after failure
        lock = empty_dir / ".kr_processing"
        assert not lock.exists()


# ══════════════════════════════════════════════════════════════════
# SESSION 2: Metadata Extraction (SPEC §4.A.3)
# ══════════════════════════════════════════════════════════════════

from engines.source.src.extractors import extract_metadata
from engines.source.src.extractors.plain_text import extract_plaintext_metadata
from engines.source.src.extractors.shamela_html import extract_shamela_metadata
from engines.source.src.text_utils import (
    ARABIC_ORDINALS,
    parse_arabic_ordinal,
    strip_tags,
)

# Load MANIFEST.json as ground truth for all Shamela fixtures
_MANIFEST_PATH = SHAMELA_ROOT / "MANIFEST.json"
with open(_MANIFEST_PATH, encoding="utf-8") as _f:
    MANIFEST: dict = json.load(_f)


def _extract(fixture_name: str) -> dict:
    """Helper: extract metadata from a Shamela fixture by name."""
    return extract_shamela_metadata(SHAMELA_ROOT / fixture_name)


# ──────────────────────────────────────────────────────────────────
# Text Utilities
# ──────────────────────────────────────────────────────────────────


class TestTextUtils:
    """Tests for shared text utilities (SPEC §4.A.1)."""

    def test_strip_tags_removes_html(self) -> None:
        assert strip_tags("<span class='title'>الكتاب</span>") == "الكتاب"

    def test_strip_tags_decodes_entities(self) -> None:
        # &nbsp; decodes to U+00A0 (non-breaking space), not regular space
        assert strip_tags("Title&nbsp;&nbsp;Extra") == "Title\xa0\xa0Extra"

    def test_strip_tags_arabic_preserved(self) -> None:
        """Arabic text with diacritics passes through byte-for-byte."""
        arabic = "الْكِتَابُ"
        assert strip_tags(f"<b>{arabic}</b>") == arabic

    def test_strip_tags_font_color(self) -> None:
        """Red font wrapper around punctuation is removed."""
        html = "الكتاب<font color=#be0000>:</font>"
        assert strip_tags(html) == "الكتاب:"

    def test_arabic_ordinal_first(self) -> None:
        assert parse_arabic_ordinal("الأولى، 1408 هـ") == 1

    def test_arabic_ordinal_second(self) -> None:
        assert parse_arabic_ordinal("الثانية") == 2

    def test_arabic_ordinal_tenth(self) -> None:
        assert parse_arabic_ordinal("العاشرة") == 10

    def test_arabic_ordinal_bare_digit(self) -> None:
        assert parse_arabic_ordinal("الطبعة 3") == 3

    def test_arabic_ordinal_none(self) -> None:
        assert parse_arabic_ordinal("no number here") is None

    def test_arabic_ordinals_coverage(self) -> None:
        """All ordinals 1-10 are covered."""
        for num in range(1, 11):
            assert num in ARABIC_ORDINALS.values()


# ──────────────────────────────────────────────────────────────────
# Shamela Extraction — Parametrized Across All 12 Fixtures
# ──────────────────────────────────────────────────────────────────


class TestShamelaExtraction:
    """Core extraction tests parametrized over all 12 Shamela fixtures."""

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_title_extraction(self, fixture_name: str) -> None:
        """Every fixture produces a title_full or display_title."""
        r = _extract(fixture_name)
        title = r.get("title_full") or r.get("display_title")
        assert title, f"No title extracted for {fixture_name}"
        manifest_meta = MANIFEST[fixture_name]["metadata"]
        expected_title = manifest_meta.get("الكتاب") or manifest_meta.get("اسم الكتاب")
        if expected_title:
            assert r.get("title_full") == expected_title

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_display_title(self, fixture_name: str) -> None:
        """Every fixture produces a display_title from the card header."""
        r = _extract(fixture_name)
        expected = MANIFEST[fixture_name]["metadata"]["display_title"]
        assert r["display_title"] == expected

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_category_extraction(self, fixture_name: str) -> None:
        """Every fixture has a shamela_category."""
        r = _extract(fixture_name)
        assert "shamela_category" in r
        assert len(r["shamela_category"]) > 0

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_body_page_count(self, fixture_name: str) -> None:
        """Digital body page count matches MANIFEST."""
        r = _extract(fixture_name)
        expected = MANIFEST[fixture_name]["body_pages_in_first_file"]
        assert r["page_count"] == expected

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_text_sample_nonempty(self, fixture_name: str) -> None:
        """Text sample is always non-empty."""
        r = _extract(fixture_name)
        assert len(r["text_sample"]) > 0

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_text_sample_max_2000(self, fixture_name: str) -> None:
        """Text sample never exceeds 2000 characters."""
        r = _extract(fixture_name)
        assert len(r["text_sample"]) <= 2000

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_format_specific_metadata_is_dict(self, fixture_name: str) -> None:
        r = _extract(fixture_name)
        assert isinstance(r["format_specific_metadata"], dict)

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_quality_issues_is_list(self, fixture_name: str) -> None:
        r = _extract(fixture_name)
        assert isinstance(r["_quality_issues"], list)


# ──────────────────────────────────────────────────────────────────
# Shamela Extraction — Fixture-Specific Tests
# ──────────────────────────────────────────────────────────────────


class TestShamelaFixtureSpecific:
    """Tests targeting specific fixture behaviors and edge cases."""

    # ── Author extraction ──

    def test_author_01_with_death_date(self) -> None:
        """Fixture 01: author with (ت 337هـ) death date pattern."""
        r = _extract("01_nahw_simple")
        assert "author_name_raw" in r
        assert r["author_death_hijri"] == 337
        assert "author_name_clean" in r

    def test_author_03_modern_no_death_date(self) -> None:
        """Fixture 03: modern author, no death date."""
        r = _extract("03_fiqh")
        assert r["author_name_raw"] == "عبد الله بن إبراهيم الزاحم"
        assert "author_death_hijri" not in r

    def test_author_06_birth_death_range(self) -> None:
        """Fixture 06: author with (631 - 676 هـ) birth-death range."""
        r = _extract("06_usul")
        assert r["author_birth_hijri"] == 631
        assert r["author_death_hijri"] == 676

    def test_author_10_uses_إعداد(self) -> None:
        """Fixture 10: no المؤلف field, uses إعداد instead."""
        r = _extract("10_no_author")
        assert "author_name_raw" in r
        assert r["_field_source_author_name_raw"] == "إعداد"
        assert "ناصر" in r["author_name_raw"]

    def test_author_diacritics_preserved(self) -> None:
        """Fixture 02: diacritics in author name preserved byte-for-byte.

        The fixture has: ق + fatha(U+064E) + ط + shadda(U+0651) + fatha(U+064E)
        This exact byte sequence must be preserved — no normalization allowed.
        """
        r = _extract("02_nahw_muhaqiq")
        # Exact codepoints: qaf + fatha + ta' + shadda + fatha + alif + 'ayn
        expected_fragment = "\u0642\u064e\u0637\u0651\u064e\u0627\u0639"
        assert expected_fragment in r["author_name_raw"]

    # ── Muhaqiq extraction ──

    def test_muhaqiq_04_hadith(self) -> None:
        """Fixture 04: المحقق field present."""
        r = _extract("04_hadith")
        assert "muhaqiq_name_raw" in r
        assert r["_field_source_muhaqiq_name_raw"] == "المحقق"

    def test_muhaqiq_02_tahqiq_wa_dirasah(self) -> None:
        """Fixture 02: تحقيق ودراسة variant maps to muhaqiq."""
        r = _extract("02_nahw_muhaqiq")
        assert r["muhaqiq_name_raw"] == "أحمد محمد عبد الدايم"
        assert r["_field_source_muhaqiq_name_raw"] == "تحقيق ودراسة"

    def test_muhaqiq_death_date_06(self) -> None:
        """Fixture 06: muhaqiq with [ت 1438 هـ] square bracket pattern."""
        r = _extract("06_usul")
        assert r["muhaqiq_death_hijri"] == 1438
        assert r["muhaqiq_name_clean"] == "بسام عبد الوهاب الجابي"

    def test_no_muhaqiq_01(self) -> None:
        """Fixture 01: no muhaqiq field at all."""
        r = _extract("01_nahw_simple")
        assert "muhaqiq_name_raw" not in r

    def test_muhaqiq_is_not_author(self) -> None:
        """Muhaqiq and author are NEVER the same person in fixture 04."""
        r = _extract("04_hadith")
        assert r["author_name_raw"] != r["muhaqiq_name_raw"]

    # ── Title variants ──

    def test_alt_title_09(self) -> None:
        """Fixture 09: uses اسم الكتاب instead of الكتاب."""
        r = _extract("09_alt_title")
        assert r["title_full"] == "أسلوب خطبة الجمعة"
        assert r["_field_source_title_full"] == "اسم الكتاب"

    # ── Multi-volume ──

    def test_multi_volume_11(self) -> None:
        """Fixture 11: 3-volume work."""
        r = _extract("11_multi_small")
        assert r["is_multi_volume"] is True
        assert r["volume_count"] == 3
        assert r["_metadata_volume_count"] == 3

    def test_multi_volume_with_muqaddima_12(self) -> None:
        """Fixture 12: 1 numbered file + المقدمة.htm = multi-volume."""
        r = _extract("12_multi_muq")
        assert r["is_multi_volume"] is True
        assert r["volume_count"] == 1  # Only numbered files count
        assert r["has_muqaddima"] is True

    def test_single_volume_01(self) -> None:
        """Fixture 01: single file, not multi-volume."""
        r = _extract("01_nahw_simple")
        assert r["is_multi_volume"] is False
        assert r["volume_count"] == 1

    # ── Edition parsing ──

    def test_edition_04_full(self) -> None:
        """Fixture 04: الأولى، 1418هـ - 1998م → number=1, both years."""
        r = _extract("04_hadith")
        assert r["edition_number"] == 1
        assert r["edition_year_hijri"] == 1418
        assert r["edition_year_miladi"] == 1998

    def test_edition_07_miladi_only(self) -> None:
        """Fixture 07: الأولى، 1980 م → miladi only."""
        r = _extract("07_balagha")
        assert r["edition_number"] == 1
        assert r["edition_year_miladi"] == 1980

    def test_edition_12_bare_year(self) -> None:
        """Fixture 12: الأولى، 2007 → bare year heuristic (>1500 = miladi)."""
        r = _extract("12_multi_muq")
        assert r["edition_number"] == 1
        assert r["edition_year_miladi"] == 2007

    def test_edition_08_bare_pair(self) -> None:
        """Fixture 08: الأولى، 1410 - 1990 → hijri/miladi pair."""
        r = _extract("08_death_date")
        assert r["edition_number"] == 1
        assert r["edition_year_hijri"] == 1410
        assert r["edition_year_miladi"] == 1990

    # ── Publisher ──

    def test_publisher_03(self) -> None:
        """Fixture 03: publisher extraction."""
        r = _extract("03_fiqh")
        assert r["publisher"] == "الجامعة الإسلامية بالمدينة المنورة"

    def test_publisher_06(self) -> None:
        r = _extract("06_usul")
        assert "دار الفكر" in r["publisher"]

    # ── Preparer (أعده للشاملة) ──

    def test_preparer_02(self) -> None:
        """Fixture 02: أعده للشاملة stored in format_specific_metadata."""
        r = _extract("02_nahw_muhaqiq")
        assert "preparer" in r["format_specific_metadata"]
        assert "رابطة النساخ" in r["format_specific_metadata"]["preparer"]

    def test_preparer_12(self) -> None:
        r = _extract("12_multi_muq")
        assert "preparer" in r["format_specific_metadata"]

    # ── Extra fields ──

    def test_extra_fields_12(self) -> None:
        """Fixture 12: تقديم, ترجمة mapped; تصدير goes to extra_card_fields."""
        r = _extract("12_multi_muq")
        assert r.get("foreword_by") == "الدكتور أحمد بن نعمان"
        assert r.get("translator") == "نور الدين خندودي"
        extra = r["format_specific_metadata"].get("extra_card_fields", {})
        assert any("تصدير" in k for k in extra)

    # ── Physical page count ──

    def test_physical_page_count_01(self) -> None:
        """Physical page count from عدد الصفحات stored in format_specific_metadata."""
        r = _extract("01_nahw_simple")
        assert r["format_specific_metadata"]["physical_page_count"] == 73

    def test_physical_vs_digital_distinction(self) -> None:
        """Physical page count differs from digital page count for fixture 03."""
        r = _extract("03_fiqh")
        assert r["page_count"] == 102  # digital
        assert r["format_specific_metadata"]["physical_page_count"] == 322  # physical
        assert r["page_count"] != r["format_specific_metadata"]["physical_page_count"]

    # ── Publication year fallback ──

    def test_publication_year_fallback_02(self) -> None:
        """Fixture 02: عام النشر provides year when الطبعة is absent."""
        r = _extract("02_nahw_muhaqiq")
        assert r.get("edition_year_miladi") == 1999


# ──────────────────────────────────────────────────────────────────
# Shamela Quality Inspection
# ──────────────────────────────────────────────────────────────────


class TestShamelaQualityInspection:
    """Tests for the 5 quality inspection checks."""

    @pytest.mark.parametrize("fixture_name", ALL_SHAMELA_FIXTURES)
    def test_no_encoding_issues_real_fixtures(self, fixture_name: str) -> None:
        """No real fixture has U+FFFD replacement characters."""
        r = _extract(fixture_name)
        encoding_issues = [
            q for q in r["_quality_issues"] if q["check"] == "encoding_suspect"
        ]
        assert len(encoding_issues) == 0

    def test_quality_issues_structure(self) -> None:
        """Quality issues have correct dict structure."""
        r = _extract("01_nahw_simple")
        for issue in r["_quality_issues"]:
            assert "check" in issue
            assert "severity" in issue
            assert "detail" in issue
            assert issue["severity"] in ("info", "warning")


# ──────────────────────────────────────────────────────────────────
# Shamela Edge Cases
# ──────────────────────────────────────────────────────────────────


class TestShamelaEdgeCases:
    """Edge case tests for Shamela extractor error handling."""

    def test_missing_pagetext_raises(self, tmp_path: Path) -> None:
        """HTML without PageText div raises FORMAT_STRUCTURE_MISSING."""
        html_file = tmp_path / "bad.htm"
        html_file.write_text("<html><body>no PageText</body></html>", encoding="utf-8")
        with pytest.raises(SourceEngineError) as exc_info:
            extract_shamela_metadata(html_file)
        assert exc_info.value.error.error_code == ErrorCode.FORMAT_STRUCTURE_MISSING

    def test_empty_directory_raises(self, tmp_path: Path) -> None:
        """Empty directory with no .htm files raises EMPTY_INPUT."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        with pytest.raises(SourceEngineError) as exc_info:
            extract_shamela_metadata(empty_dir)
        assert exc_info.value.error.error_code == ErrorCode.EMPTY_INPUT

    def test_non_utf8_raises(self, tmp_path: Path) -> None:
        """Non-UTF-8 file raises UNSUPPORTED_FORMAT."""
        bad_file = tmp_path / "bad_encoding.htm"
        bad_file.write_bytes(b"\x80\x81\x82\x83")
        with pytest.raises(SourceEngineError) as exc_info:
            extract_shamela_metadata(bad_file)
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT

    def test_ahdahu_lil_shamela_maps_to_preparer(self, tmp_path: Path) -> None:
        """أهداه للشاملة maps to preparer (stress test discovery)."""
        html = (
            "<html><body><div class='Main'>"
            "<div class='PageText'>"
            "<span class='title'>الكتاب<font color='#0000FF'>:</font></span> كتاب تجريبي<p>"
            "<span class='title'>أهداه للشاملة<font color='#0000FF'>:</font></span> أحمد محمد<p>"
            "</div>"
            "<div class='PageText'>صفحة أولى</div>"
            "<div class='PageText'>صفحة ثانية</div>"
            "<div class='PageText'>صفحة ثالثة</div>"
            "</div></body></html>"
        )
        f = tmp_path / "test.htm"
        f.write_text(html, encoding="utf-8")
        result = extract_shamela_metadata(f)
        assert result["preparer"] == "أحمد محمد"
        assert result["_field_source_preparer"] == "أهداه للشاملة"

    def test_mulahaza_maps_to_editorial_note(self, tmp_path: Path) -> None:
        """ملاحظة maps to editorial_note (stress test discovery)."""
        html = (
            "<html><body><div class='Main'>"
            "<div class='PageText'>"
            "<span class='title'>الكتاب<font color='#0000FF'>:</font></span> كتاب تجريبي<p>"
            "<span class='title'>ملاحظة<font color='#0000FF'>:</font></span> "
            "هذا الكتاب منسوب وليس محققا<p>"
            "</div>"
            "<div class='PageText'>صفحة أولى</div>"
            "<div class='PageText'>صفحة ثانية</div>"
            "<div class='PageText'>صفحة ثالثة</div>"
            "</div></body></html>"
        )
        f = tmp_path / "test.htm"
        f.write_text(html, encoding="utf-8")
        result = extract_shamela_metadata(f)
        assert result["editorial_note"] == "هذا الكتاب منسوب وليس محققا"
        assert result["_field_source_editorial_note"] == "ملاحظة"


# ──────────────────────────────────────────────────────────────────
# Plain Text Extraction
# ──────────────────────────────────────────────────────────────────


class TestPlainTextExtraction:
    """Tests for plain text metadata extraction — SPEC §4.A.3."""

    def test_alfiyyah_title(self) -> None:
        """Title extracted from first line of alfiyyah.txt."""
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert r["title_arabic"] == "متن الفية ابن مالك فى علم النحو والصرف"

    def test_alfiyyah_page_count_none(self) -> None:
        """Plain text has no page count."""
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert r["page_count"] is None

    def test_alfiyyah_text_sample(self) -> None:
        """Text sample is non-empty and capped at 2000 chars."""
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert len(r["text_sample"]) > 0
        assert len(r["text_sample"]) <= 2000

    def test_alfiyyah_char_count(self) -> None:
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert r["format_specific_metadata"]["char_count"] > 0

    def test_alfiyyah_line_count(self) -> None:
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert r["format_specific_metadata"]["line_count"] > 0

    def test_alfiyyah_detected_encoding(self) -> None:
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        assert r["format_specific_metadata"]["detected_encoding"] == "utf-8"

    def test_preamble_skip(self, tmp_path: Path) -> None:
        """بسم الله preamble is skipped; title is second line."""
        txt = tmp_path / "test.txt"
        txt.write_text(
            "بسم الله الرحمن الرحيم\nالعنوان الحقيقي\nمحتوى", encoding="utf-8"
        )
        r = extract_plaintext_metadata(txt)
        assert r["title_arabic"] == "العنوان الحقيقي"

    def test_preamble_hamdala_skip(self, tmp_path: Path) -> None:
        """الحمد لله preamble is also skipped."""
        txt = tmp_path / "test.txt"
        txt.write_text("الحمد لله رب العالمين\nعنوان الكتاب\nمحتوى", encoding="utf-8")
        r = extract_plaintext_metadata(txt)
        assert r["title_arabic"] == "عنوان الكتاب"

    def test_no_preamble_uses_first_line(self, tmp_path: Path) -> None:
        """Without preamble, first line is the title."""
        txt = tmp_path / "test.txt"
        txt.write_text("عنوان مباشر\nمحتوى", encoding="utf-8")
        r = extract_plaintext_metadata(txt)
        assert r["title_arabic"] == "عنوان مباشر"

    def test_bad_encoding_raises(self, tmp_path: Path) -> None:
        """Invalid encoding raises UNSUPPORTED_FORMAT."""
        txt = tmp_path / "bad.txt"
        txt.write_bytes(b"\x80\x81\x82")
        with pytest.raises(SourceEngineError) as exc_info:
            extract_plaintext_metadata(txt, detected_encoding="utf-8")
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT

    def test_arabic_diacritics_preserved(self) -> None:
        """Diacritics in alfiyyah text are preserved byte-for-byte."""
        r = extract_plaintext_metadata(ALFIYYAH_PATH)
        # The alfiyyah contains heavily diacritized text
        assert "قَ" in r["text_sample"] or "مُ" in r["text_sample"]


# ──────────────────────────────────────────────────────────────────
# Extractor Dispatch
# ──────────────────────────────────────────────────────────────────


class TestExtractorDispatch:
    """Tests for the extract_metadata() dispatcher."""

    def test_dispatch_shamela(self) -> None:
        r = extract_metadata(SHAMELA_ROOT / "01_nahw_simple", SourceFormat.SHAMELA_HTML)
        assert "title_full" in r

    def test_dispatch_plain_text(self) -> None:
        r = extract_metadata(ALFIYYAH_PATH, SourceFormat.PLAIN_TEXT)
        assert "title_arabic" in r

    def test_dispatch_unsupported_raises(self, tmp_path: Path) -> None:
        """Unsupported format raises UNSUPPORTED_FORMAT."""
        dummy = tmp_path / "test.pdf"
        dummy.write_bytes(b"%PDF-1.4")
        with pytest.raises(SourceEngineError) as exc_info:
            extract_metadata(dummy, SourceFormat.PDF_TEXT)
        assert exc_info.value.error.error_code == ErrorCode.UNSUPPORTED_FORMAT
