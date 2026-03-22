"""Contract boundary tests — source→normalization and normalization→passaging.

Verifies that:
1. SourceMetadata required fields are consumed correctly
2. NormalizedPackage output satisfies passaging contract expectations
3. Edge cases in contract fields don't cause silent failures
4. D-023 metadata flow is preserved
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.normalization.contracts import (
    ContentFlags,
    ContentUnit,
    DivisionNode,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerMapEntry,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    QualityReport,
    StructuralFormat,
    TextFidelity,
    TextFidelityLevel,
    TextFidelitySummary,
    TextLayerSegment,
)
from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.tests.conftest import (
    FIXTURES_REAL,
    _make_content_unit,
    _make_normalized_package,
    _make_source_metadata,
)


# ══════════════════════════════════════════════════════════════════════
# Source → Normalization boundary
# ══════════════════════════════════════════════════════════════════════


class TestSourceToNormBoundary:
    """Verify SourceMetadata fields are consumed correctly by normalization."""

    def test_source_format_routing(self) -> None:
        """source_format='shamela_html' routes to Shamela normalizer."""
        path = FIXTURES_REAL / "01_nahw_simple"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata(source_format="shamela_html")
        pkg = normalize_source(htm, meta)
        assert "shamela" in pkg.manifest.normalizer_id.lower()

    def test_plain_text_routing(self, tmp_path: Path) -> None:
        """source_format='plain_text' routes to plain text normalizer."""
        txt = tmp_path / "test.txt"
        txt.write_text("بسم الله الرحمن الرحيم\n\nالحمد لله", encoding="utf-8")
        meta = _make_source_metadata(source_format="plain_text")
        pkg = normalize_source(txt, meta)
        assert "plain_text" in pkg.manifest.normalizer_id.lower()

    def test_unsupported_format_raises(self, tmp_path: Path) -> None:
        """Unsupported source_format raises clear error."""
        txt = tmp_path / "test.pdf"
        txt.write_text("dummy", encoding="utf-8")
        # Use a valid SourceFormat enum value that the normalizer doesn't handle
        meta = _make_source_metadata(source_format="pdf_text")
        with pytest.raises(Exception):
            normalize_source(txt, meta)

    def test_source_id_preserved_in_output(self) -> None:
        """source_id from SourceMetadata appears in NormalizedManifest (D-023)."""
        path = FIXTURES_REAL / "01_nahw_simple"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata(source_id="src_d023_test")
        pkg = normalize_source(htm, meta)
        assert pkg.manifest.source_id == "src_d023_test"
        for cu in pkg.content_units:
            assert cu.source_id == "src_d023_test"

    def test_multi_layer_flag_respected(self) -> None:
        """is_multi_layer=True enables layer detection in output."""
        path = FIXTURES_REAL / "02_nahw_muhaqiq"
        htm = list(path.glob("*.htm"))[0]

        # With multi-layer enabled
        meta_multi = _make_source_metadata(is_multi_layer=True)
        pkg_multi = normalize_source(htm, meta_multi)
        multi_layers = sum(1 for cu in pkg_multi.content_units if len(cu.text_layers) >= 2)

        # With multi-layer disabled
        meta_single = _make_source_metadata(is_multi_layer=False)
        pkg_single = normalize_source(htm, meta_single)
        single_layers = sum(1 for cu in pkg_single.content_units if len(cu.text_layers) >= 2)

        # Multi-layer flag should produce more multi-layer units
        # (auto-upgrade may still detect some in single mode)
        assert multi_layers >= single_layers


# ══════════════════════════════════════════════════════════════════════
# Normalization → Passaging boundary
# ══════════════════════════════════════════════════════════════════════


class TestNormToPassagingBoundary:
    """Verify NormalizedPackage output satisfies passaging expectations."""

    def test_content_units_contiguous_indices(self) -> None:
        """Passaging expects unit_index to be contiguous 0..N-1."""
        path = FIXTURES_REAL / "03_fiqh"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)
        indices = [cu.unit_index for cu in pkg.content_units]
        assert indices == list(range(len(indices)))

    def test_manifest_total_matches_units(self) -> None:
        """Passaging relies on total_content_units matching actual count."""
        path = FIXTURES_REAL / "04_hadith"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)
        assert pkg.manifest.total_content_units == len(pkg.content_units)

    def test_division_tree_references_valid_indices(self) -> None:
        """Division tree start/end indices are within content unit range."""
        path = FIXTURES_REAL / "06_usul"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)

        max_idx = len(pkg.content_units) - 1
        for node in pkg.manifest.division_tree:
            assert node.start_unit_index >= 0
            assert node.end_unit_index <= max_idx
            assert node.start_unit_index <= node.end_unit_index

    def test_layer_map_not_empty(self) -> None:
        """Passaging expects at least one layer_map entry."""
        path = FIXTURES_REAL / "01_nahw_simple"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)
        assert len(pkg.manifest.layer_map) >= 1

    def test_text_layers_cover_full_text(self) -> None:
        """Every content unit's text_layers cover [0, len(primary_text))."""
        path = FIXTURES_REAL / "02_nahw_muhaqiq"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata(is_multi_layer=True)
        pkg = normalize_source(htm, meta)

        for cu in pkg.content_units:
            if not cu.primary_text:
                continue
            text_len = len(cu.primary_text)
            if cu.text_layers:
                assert cu.text_layers[0].start == 0, (
                    f"Unit {cu.unit_index}: first layer starts at {cu.text_layers[0].start}"
                )
                assert cu.text_layers[-1].end == text_len, (
                    f"Unit {cu.unit_index}: last layer ends at {cu.text_layers[-1].end}, text_len={text_len}"
                )

    def test_physical_page_volume_always_set(self) -> None:
        """Passaging needs volume info for multi-volume handling."""
        path = FIXTURES_REAL / "01_nahw_simple"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)
        for cu in pkg.content_units:
            assert cu.physical_page.volume is not None
            assert cu.physical_page.volume >= 1

    def test_content_flags_always_present(self) -> None:
        """Every content unit has a ContentFlags object."""
        path = FIXTURES_REAL / "04_hadith"
        htm = list(path.glob("*.htm"))[0]
        meta = _make_source_metadata()
        pkg = normalize_source(htm, meta)
        for cu in pkg.content_units:
            assert cu.content_flags is not None
            assert isinstance(cu.content_flags, ContentFlags)


# ══════════════════════════════════════════════════════════════════════
# Contract model validation edge cases
# ══════════════════════════════════════════════════════════════════════


class TestContractModelEdgeCases:
    """Edge cases in Pydantic contract models."""

    def test_empty_primary_text_allowed(self) -> None:
        """ContentUnit can have empty primary_text (blank pages)."""
        cu = _make_content_unit(primary_text="", unit_index=0)
        assert cu.primary_text == ""

    def test_none_boundary_continuity_allowed(self) -> None:
        """boundary_continuity can be None (first page, no prior context)."""
        cu = _make_content_unit(unit_index=0)
        assert cu.boundary_continuity is None

    def test_division_node_zero_heading_level(self) -> None:
        """heading_level=0 is valid (root division)."""
        node = DivisionNode(
            div_id="div_test",
            division_type=None,
            heading_text="root",
            heading_level=0,
            start_unit_index=0,
            end_unit_index=10,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        assert node.heading_level == 0

    def test_quality_report_defaults(self) -> None:
        """QualityReport defaults are valid."""
        qr = QualityReport()
        assert qr.pages_with_warnings == 0
        assert qr.high_fidelity_pct == 1.0

    def test_normalized_package_single_unit(self) -> None:
        """Package with a single content unit is valid."""
        pkg = _make_normalized_package(num_units=1)
        assert len(pkg.content_units) == 1
        assert pkg.manifest.total_content_units == 1

    def test_layer_map_entry_with_none_author(self) -> None:
        """LayerMapEntry with author_canonical_id=None is valid."""
        entry = LayerMapEntry(
            layer_type=LayerType.SHARH,
            author_canonical_id=None,
            confidence=1.0,
        )
        assert entry.author_canonical_id is None
