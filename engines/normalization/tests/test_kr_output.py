"""Tests for normalization engine — SPEC §10.

Organized in two layers:
  Layer 1: Format-agnostic infrastructure tests (validation, writer, dispatcher)
           These pass regardless of which normalizers are implemented.
  Layer 2: Per-normalizer tests (one test class per format)

Test categories (from SPEC §10):
  1. Output schema compliance (manifest + content units)
  2. Content preservation fidelity
  3. Footnote separation correctness
  4. Multi-layer detection accuracy
  5. Structure discovery regression
  6. Diacritics preservation
  7. Page boundary accuracy
  8. Content flag correctness
  9. Error handling (all NORM_* codes)
"""

from __future__ import annotations

import json
import logging

import pytest
from pathlib import Path

from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from engines.normalization.src.validation import validate_package
from engines.normalization.src.writer import write_normalized_package
from engines.normalization.tests.conftest import (
    _make_content_unit,
    _make_normalized_package,
    _make_source_metadata,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
GOLD_DIR = Path(__file__).parent / "gold_baselines"
logger = logging.getLogger(__name__)


# ============================================================
# Layer 1: Format-Agnostic Infrastructure Tests
# ============================================================

class TestValidation:
    """SPEC §5: Validation checks that apply to ANY normalized package."""

    def test_valid_package_passes(self):
        """A correctly formed NormalizedPackage passes all validation."""
        pkg = _make_normalized_package(num_units=3)
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert result.passed
        assert len(result.fatal_errors) == 0

    def test_empty_content_stream_rejected(self):
        """A package with zero content units but total > 0 is rejected."""
        pkg = _make_normalized_package(num_units=0)
        pkg.manifest.total_content_units = 1  # mismatch
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_missing_manifest_fields_rejected(self):
        """A manifest with invalid schema is rejected."""
        pkg = _make_normalized_package(num_units=1)
        # Corrupt the manifest by setting an invalid field
        pkg.manifest.total_content_units = -1  # violates ge=0 constraint
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed

    def test_content_unit_sequence_gaps_detected(self):
        """Non-contiguous sequence numbers are flagged."""
        units = [
            _make_content_unit(unit_index=0),
            _make_content_unit(unit_index=2),  # gap: missing 1
        ]
        pkg = _make_normalized_package(content_units=units)
        pkg.manifest.total_content_units = 2
        meta = _make_source_metadata()
        result = validate_package(pkg, meta)
        assert not result.passed
        assert any(e.code == NormErrorCode.UNIT_INDEX_VIOLATION for e in result.fatal_errors)

    def test_metadata_passthrough_verified(self):
        """D-023: source_id preserved from metadata to package."""
        source_id = "src_d023_test"
        pkg = _make_normalized_package(num_units=2, source_id=source_id)
        meta = _make_source_metadata(source_id=source_id)
        result = validate_package(pkg, meta)
        assert result.passed
        assert pkg.manifest.source_id == source_id
        for cu in pkg.content_units:
            assert cu.source_id == source_id


class TestWriter:
    """SPEC §4.A output writing — atomic write of any normalized package."""

    def test_atomic_write_creates_manifest_and_content(self, tmp_path: Path):
        """Writer produces manifest.json + content.jsonl at correct paths."""
        pkg = _make_normalized_package(num_units=2)
        result = write_normalized_package(pkg, "src_test0001", tmp_path)
        assert (result / "manifest.json").exists()
        assert (result / "content.jsonl").exists()

    def test_interrupted_write_leaves_no_partial_output(self, tmp_path: Path):
        """After successful write, no temp directories remain."""
        pkg = _make_normalized_package(num_units=2)
        write_normalized_package(pkg, "src_test0001", tmp_path)
        base = tmp_path / "sources" / "src_test0001"
        temp_dirs = list(base.glob("normalized_tmp_*"))
        prev_dirs = list(base.glob("normalized_prev_*"))
        assert len(temp_dirs) == 0
        assert len(prev_dirs) == 0

    def test_written_files_are_valid_json(self, tmp_path: Path):
        """Written manifest.json and content.jsonl are parseable."""
        pkg = _make_normalized_package(num_units=3)
        result = write_normalized_package(pkg, "src_test0001", tmp_path)
        with open(result / "manifest.json", encoding="utf-8") as f:
            manifest = json.load(f)
        assert manifest["source_id"] == "src_test0001"
        with open(result / "content.jsonl", encoding="utf-8") as f:
            lines = [json.loads(line) for line in f if line.strip()]
        assert len(lines) == 3


class TestDispatcher:
    """SPEC §4.A.1: Dispatcher routes source_format to correct normalizer."""

    def test_known_format_routes_correctly(self, tmp_path: Path):
        """SHAMELA_HTML routes to ShamelaNormalizer via registry."""
        from engines.normalization.src.dispatcher import _NORMALIZER_REGISTRY
        from engines.source.contracts import SourceFormat

        assert SourceFormat.SHAMELA_HTML in _NORMALIZER_REGISTRY
        assert _NORMALIZER_REGISTRY[SourceFormat.SHAMELA_HTML] is ShamelaNormalizer

    def test_unknown_format_raises_error(self, tmp_path: Path):
        """Unregistered source_format raises NORM_UNKNOWN_SOURCE_FORMAT."""
        meta = _make_source_metadata(source_format="pdf_text")
        dummy_pdf = tmp_path / "dummy.pdf"
        dummy_pdf.write_text("dummy", encoding="utf-8")
        with pytest.raises(NormalizationError) as exc_info:
            normalize_source(dummy_pdf, meta)
        assert exc_info.value.code == NormErrorCode.UNKNOWN_SOURCE_FORMAT


class TestContentCensus:
    """SPEC §4.B.5: Content census produces statistics for any content stream."""

    def test_census_on_synthetic_content(self):
        """Census produces expected statistics from synthetic content units."""
        pytest.skip("§4.B.5 DEFERRED — content census not in core build (CORE_EXTRACTION.md)")


class TestContentFlagger:
    """SPEC §4.A: Content flags detected in any content stream."""

    def test_quran_verse_detection(self):
        """Quran verse patterns detected and flagged."""
        pytest.skip("Superseded by test_integration.py::TestContentFlagger::test_quran_verse_detection — Session 7")

    def test_hadith_marker_detection(self):
        """Hadith narration patterns detected and flagged."""
        pytest.skip("Superseded by test_integration.py::TestContentFlagger::test_hadith_marker_detection — Session 7")

    def test_poetry_verse_detection(self):
        """Poetry meter patterns detected and flagged."""
        pytest.skip("Superseded by test_integration.py::TestContentFlagger::test_poetry_verse_detection — Session 7")


# ============================================================
# Layer 2: Per-Normalizer Tests
# ============================================================

class TestShamelaNormalizer:
    """Tests for the Shamela HTML normalizer — SPEC §4.A.2."""

    FIXTURE = FIXTURE_DIR / "shamela_ibn_aqil.htm"

    def test_fixture_exists(self):
        """Test fixture is available."""
        assert self.FIXTURE.exists(), f"Shamela fixture missing: {self.FIXTURE}"

    def test_output_schema_compliance(self):
        """Shamela normalizer output validates against NormalizedManifest model."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_output_schema_compliance — Session 7")

    def test_content_preservation_arabic_text(self):
        """Arabic text preserved byte-for-byte through normalization."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_content_preservation_arabic_text — Session 7")

    def test_footnote_separation(self):
        """Footnotes correctly separated from primary text."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_footnote_separation — Session 7")

    def test_multi_layer_detection(self):
        """Matn/sharh layers detected in commentary text."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_multi_layer_detection — Session 7")

    def test_diacritics_preservation(self):
        """Tashkeel diacritics preserved through normalization."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_diacritics_preservation — Session 7")

    def test_page_boundaries(self):
        """Page breaks correctly identified from Shamela PageText divs."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_page_boundaries — Session 7")

    def test_structure_discovery(self):
        """Chapter/section headings detected from Shamela markup."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_structure_discovery — Session 7")

    def test_content_flags(self):
        """Quran, hadith, poetry markers detected in content."""
        pytest.skip("Superseded by test_integration.py::TestShamelaNormalizer::test_content_flags — Session 7")


# Additional normalizer test classes added here as normalizers are built:
# class TestPdfNormalizer:
# class TestPlainTextNormalizer:
# class TestImageNormalizer:
# etc.
