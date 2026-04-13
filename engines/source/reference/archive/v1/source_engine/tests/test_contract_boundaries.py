"""Contract boundary tests for source engine output.

Verifies that SourceMetadata output satisfies normalization engine expectations.
Tests the source→normalization contract boundary.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.source.contracts import (
    InferredFieldConfidence,
    ScholarReference,
    SourceFormat,
    SourceMetadata,
    TextLayer,
    TrustworthinessFactor,
)
from engines.source.src.extractors.shamela_html import extract_shamela_metadata
from engines.source.src.format_detection import detect_format


FIXTURES_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
SHAMELA_ROOT = FIXTURES_ROOT / "shamela_real"


def _make_minimal_source_metadata(**overrides: object) -> SourceMetadata:
    """Factory for minimal valid SourceMetadata."""
    defaults = {
        "source_id": "src_boundary_test",
        "work_id": "wrk_boundary_test",
        "human_label": "Boundary Test",
        "title_arabic": "كتاب الاختبار",
        "author": ScholarReference(
            canonical_id="sch_00001",
            name_arabic="المؤلف",
            confidence=1.0,
            source_of_identification="test",
        ),
        "science_scope": ["nahw"],
        "genre": "sharh",
        "source_format": "shamela_html",
        "authority_level": "primary",
        "structural_format": "prose",
        "is_multi_layer": False,
        "text_layers": [],
        "trust_tier": "verified",
        "trust_score": 0.85,
        "trust_factors": [
            TrustworthinessFactor(
                name="author_standing", weight=0.3, score=0.9, reason="test"
            ),
        ],
        "trust_reason": "test",
        "text_fidelity": "high",
        "text_fidelity_reason": "test",
        "confidence_scores": InferredFieldConfidence(
            genre=1.0,
            science_scope=1.0,
            structural_format=1.0,
            authority_level=1.0,
        ),
        "status": "acquired",
        "intake_timestamp": "2026-01-01T00:00:00Z",
        "acquisition_path": "manual",
        "frozen_path": "library/sources/src_boundary_test/frozen/",
        "frozen_hash": "abc123",
        "frozen_file_hashes": {"test.htm": "abc123"},
    }
    defaults.update(overrides)
    return SourceMetadata(**defaults)


class TestSourceOutputContract:
    """SourceMetadata fields needed by normalization engine."""

    def test_source_format_is_valid_enum(self) -> None:
        """source_format must be a valid SourceFormat value."""
        meta = _make_minimal_source_metadata()
        assert meta.source_format in [sf.value for sf in SourceFormat]

    def test_source_id_not_empty(self) -> None:
        """source_id must be non-empty for D-023 traceability."""
        meta = _make_minimal_source_metadata()
        assert meta.source_id
        assert len(meta.source_id) > 0

    def test_is_multi_layer_is_bool(self) -> None:
        """is_multi_layer must be a proper boolean, not truthy/falsy."""
        meta_true = _make_minimal_source_metadata(is_multi_layer=True)
        meta_false = _make_minimal_source_metadata(is_multi_layer=False)
        assert isinstance(meta_true.is_multi_layer, bool)
        assert isinstance(meta_false.is_multi_layer, bool)

    def test_text_layers_with_multi_layer(self) -> None:
        """Multi-layer sources should have text_layers entries."""
        layers = [
            TextLayer(
                layer_type="matn",
                author=ScholarReference(
                    canonical_id="sch_001",
                    name_arabic="ابن مالك",
                    confidence=1.0,
                    source_of_identification="test",
                ),
            ),
            TextLayer(
                layer_type="sharh",
                author=ScholarReference(
                    canonical_id="sch_002",
                    name_arabic="ابن عقيل",
                    confidence=1.0,
                    source_of_identification="test",
                ),
            ),
        ]
        meta = _make_minimal_source_metadata(is_multi_layer=True, text_layers=layers)
        assert len(meta.text_layers) == 2

    def test_trust_score_in_range(self) -> None:
        """trust_score is between 0 and 1."""
        meta = _make_minimal_source_metadata(trust_score=0.85)
        assert 0.0 <= meta.trust_score <= 1.0

    def test_structural_format_valid(self) -> None:
        """structural_format is a recognized value."""
        valid_formats = ["prose", "commentary", "versified", "tabular", "qa", "entries"]
        meta = _make_minimal_source_metadata(structural_format="prose")
        assert meta.structural_format in valid_formats


class TestExtractionOutputConsistency:
    """Extraction output fields are consistent across fixtures."""

    @pytest.mark.parametrize("fixture_name", [
        "01_nahw_simple", "02_nahw_muhaqiq", "03_fiqh", "04_hadith",
    ])
    def test_extraction_has_title(self, fixture_name: str) -> None:
        """Every fixture extraction produces a title_full."""
        path = SHAMELA_ROOT / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        result = extract_shamela_metadata(path)
        assert result.get("title_full"), f"No title_full in {fixture_name}"

    @pytest.mark.parametrize("fixture_name", [
        "01_nahw_simple", "02_nahw_muhaqiq", "03_fiqh", "04_hadith",
    ])
    def test_extraction_has_page_count(self, fixture_name: str) -> None:
        """Every fixture extraction produces a positive page_count."""
        path = SHAMELA_ROOT / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        result = extract_shamela_metadata(path)
        assert result.get("page_count", 0) >= 1

    @pytest.mark.parametrize("fixture_name", [
        "01_nahw_simple", "02_nahw_muhaqiq", "03_fiqh", "04_hadith",
    ])
    def test_extraction_has_shamela_category(self, fixture_name: str) -> None:
        """Every fixture extraction produces shamela_category."""
        path = SHAMELA_ROOT / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        result = extract_shamela_metadata(path)
        assert "shamela_category" in result


class TestFormatDetectionBoundary:
    """Format detection produces values the normalization engine can route."""

    def test_shamela_produces_shamela_html(self) -> None:
        """Shamela directory → SHAMELA_HTML."""
        path = SHAMELA_ROOT / "01_nahw_simple"
        assert detect_format(path) == SourceFormat.SHAMELA_HTML

    def test_plain_text_produces_plain_text(self, tmp_path: Path) -> None:
        """Plain .txt file → PLAIN_TEXT."""
        txt = tmp_path / "test.txt"
        txt.write_text("بسم الله", encoding="utf-8")
        assert detect_format(txt) == SourceFormat.PLAIN_TEXT

    def test_unknown_format_raises(self, tmp_path: Path) -> None:
        """Unknown file type raises SourceEngineError."""
        from engines.source.src.exceptions import SourceEngineError

        pdf = tmp_path / "test.pdf"
        pdf.write_bytes(b"%PDF-1.4 fake")
        with pytest.raises(SourceEngineError):
            detect_format(pdf)
