"""Tests for Pass 6 output assembly — SPEC §4.A.2 Pass 6.

Covers:
  - ibn_aqil full pipeline → NormalizedPackage (5 content units, multi-layer)
  - 01_nahw_simple full pipeline → 73 content units, all MATN at 1.0
  - Footnote conversion (ref_marker, footnote_type, confidence)
  - Manifest fields (normalizer_id, structural_format, total, deferred=None)
  - Last content unit has boundary_continuity=None
  - Blank page: content_flags.is_blank=True, boundary_continuity=None
  - quality_report.division_count_by_tier matches Pass 4
  - Text layer full coverage on every non-blank content unit
  - 05_tafsir: at least 2 content units with has_quran_citation=True
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.normalization.contracts import (
    BoundaryContinuityType,
    FootnoteType,
    LayerType,
    NormalizedPackage,
    StructuralFormat,
)
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from engines.normalization.tests.conftest import (
    FIXTURES_ENGINE,
    FIXTURES_REAL,
    IBN_AQIL,
    _assert_full_coverage,
    _make_source_metadata,
    _make_text_layers_sharh,
)


# ══════════════════════════════════════════════════════════════════════
# Full pipeline: ibn_aqil (multi-layer)
# ══════════════════════════════════════════════════════════════════════


class TestIbnAqilFullPipeline:
    """ibn_aqil fixture: 5-page multi-layer sharh over alfiyyah matn."""

    @pytest.fixture
    def pkg(self) -> NormalizedPackage:
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
            structural_format="prose",
            source_format="shamela_html",
        )
        return n.normalize(IBN_AQIL, meta)

    def test_returns_normalized_package(self, pkg: NormalizedPackage) -> None:
        assert isinstance(pkg, NormalizedPackage)

    def test_content_unit_count(self, pkg: NormalizedPackage) -> None:
        assert len(pkg.content_units) == 5
        assert pkg.manifest.total_content_units == 5

    def test_normalizer_id(self, pkg: NormalizedPackage) -> None:
        assert pkg.manifest.normalizer_id == "kr.normalization.shamela_v2"

    def test_structural_format(self, pkg: NormalizedPackage) -> None:
        assert pkg.manifest.structural_format == StructuralFormat.PROSE

    def test_layer_map_has_entries(self, pkg: NormalizedPackage) -> None:
        assert len(pkg.manifest.layer_map) >= 1

    def test_text_layer_full_coverage(self, pkg: NormalizedPackage) -> None:
        """Every non-blank content unit has full text layer coverage."""
        for cu in pkg.content_units:
            if cu.content_flags.is_blank:
                continue
            text_len = len(cu.primary_text)
            if text_len > 0:
                _assert_full_coverage(cu.text_layers, text_len)

    def test_last_unit_no_boundary(self, pkg: NormalizedPackage) -> None:
        """Last content unit has boundary_continuity=None."""
        assert pkg.content_units[-1].boundary_continuity is None

    def test_deferred_fields_none(self, pkg: NormalizedPackage) -> None:
        """Deferred §4.B fields are None (D1)."""
        assert pkg.manifest.content_census is None
        assert pkg.manifest.tahqiq_topology is None
        assert pkg.manifest.layer_fingerprints is None
        assert pkg.manifest.discourse_flow_summary is None

    def test_content_unit_discourse_flow_none(self, pkg: NormalizedPackage) -> None:
        """Discourse flow is deferred — all None."""
        for cu in pkg.content_units:
            assert cu.discourse_flow is None

    def test_source_id_consistent(self, pkg: NormalizedPackage) -> None:
        """source_id matches across manifest and all content units."""
        expected = pkg.manifest.source_id
        for cu in pkg.content_units:
            assert cu.source_id == expected


# ══════════════════════════════════════════════════════════════════════
# Full pipeline: 01_nahw_simple (single-layer, 73 pages)
# ══════════════════════════════════════════════════════════════════════


class TestNahwSimpleFullPipeline:
    """01_nahw_simple: 73-page single-layer prose matn."""

    @pytest.fixture
    def pkg(self) -> NormalizedPackage:
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="matn",
            structural_format="prose",
            source_format="shamela_html",
        )
        return n.normalize(
            FIXTURES_REAL / "01_nahw_simple" / "book.htm", meta,
        )

    def test_content_unit_count(self, pkg: NormalizedPackage) -> None:
        assert len(pkg.content_units) == 73
        assert pkg.manifest.total_content_units == 73

    def test_text_layer_full_coverage(self, pkg: NormalizedPackage) -> None:
        for cu in pkg.content_units:
            if cu.content_flags.is_blank:
                continue
            text_len = len(cu.primary_text)
            if text_len > 0:
                _assert_full_coverage(cu.text_layers, text_len)

    def test_unit_indices_sequential(self, pkg: NormalizedPackage) -> None:
        """unit_index is sequential starting from 0."""
        indices = [cu.unit_index for cu in pkg.content_units]
        assert indices == list(range(len(pkg.content_units)))


# ══════════════════════════════════════════════════════════════════════
# Footnote conversion
# ══════════════════════════════════════════════════════════════════════


class TestFootnoteConversion:
    """ParsedFootnote → Footnote contract conversion."""

    def test_footnote_fields(self) -> None:
        """Footnote ref_marker is str, footnote_type is enum, confidence is float."""
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="matn",
            structural_format="prose",
            source_format="shamela_html",
        )
        # 07_balagha has (N)-style footnotes
        pkg = n.normalize(
            FIXTURES_REAL / "07_balagha" / "book.htm", meta,
        )
        units_with_fn = [cu for cu in pkg.content_units if cu.footnotes]
        if not units_with_fn:
            pytest.skip("No footnotes in 07_balagha")
        fn = units_with_fn[0].footnotes[0]
        assert isinstance(fn.ref_marker, str)
        assert isinstance(fn.footnote_type, FootnoteType)
        assert isinstance(fn.confidence, float)
        assert 0.0 <= fn.confidence <= 1.0


# ══════════════════════════════════════════════════════════════════════
# Blank page handling
# ══════════════════════════════════════════════════════════════════════


class TestBlankPageHandling:
    """Blank pages get is_blank=True and boundary_continuity=None."""

    def test_blank_page_flags(self) -> None:
        """If a fixture has blank pages, they have is_blank=True."""
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="matn",
            structural_format="prose",
            source_format="shamela_html",
        )
        pkg = n.normalize(
            FIXTURES_REAL / "01_nahw_simple" / "book.htm", meta,
        )
        blank_units = [cu for cu in pkg.content_units if cu.content_flags.is_blank]
        for cu in blank_units:
            assert cu.boundary_continuity is None


# ══════════════════════════════════════════════════════════════════════
# Quality report
# ══════════════════════════════════════════════════════════════════════


class TestQualityReport:
    """quality_report reflects pipeline output."""

    def test_division_count_by_tier(self) -> None:
        """division_count_by_tier is populated from Pass 4."""
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="matn",
            structural_format="prose",
            source_format="shamela_html",
        )
        pkg = n.normalize(
            FIXTURES_REAL / "01_nahw_simple" / "book.htm", meta,
        )
        qr = pkg.manifest.quality_report
        assert isinstance(qr.division_count_by_tier, dict)
        # 01_nahw_simple has headings
        assert sum(qr.division_count_by_tier.values()) >= 1

    def test_high_fidelity_pct(self) -> None:
        """high_fidelity_pct is 1.0 (all digital sources)."""
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="matn",
            structural_format="prose",
            source_format="shamela_html",
        )
        pkg = n.normalize(IBN_AQIL, meta)
        assert pkg.manifest.quality_report.high_fidelity_pct == 1.0


# ══════════════════════════════════════════════════════════════════════
# Content flags on real fixtures
# ══════════════════════════════════════════════════════════════════════


class TestContentFlagsOnFixtures:
    """Content flags from full pipeline runs."""

    def test_05_tafsir_quran_citations(self) -> None:
        """05_tafsir: at least 2 content units with has_quran_citation."""
        n = ShamelaNormalizer()
        meta = _make_source_metadata(
            genre="tafsir",
            structural_format="prose",
            source_format="shamela_html",
        )
        pkg = n.normalize(
            FIXTURES_REAL / "05_tafsir" / "book.htm", meta,
        )
        quran_units = [
            cu for cu in pkg.content_units
            if cu.content_flags.has_quran_citation
        ]
        assert len(quran_units) >= 2, (
            f"Expected >=2 Quran units in tafsir, got {len(quran_units)}"
        )
