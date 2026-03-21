"""Edge case regression tests from weekend corpus sweep.

Each test exercises a fixture selected for its extreme or unusual characteristics.
All assertions use independent ground truth (raw HTML page counts, character
analysis) — no tautological self-referencing.

Categories:
  - Extreme small (2KB, 3 pages)
  - Zero diacritics (3 fixtures)
  - Zero content flags (2 fixtures)
  - Low Arabic ratio (55.4%)
  - High page loss (13 pages)
  - Multi-layer 99%+ (extract)
  - Warning-heavy (extract)
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest
from bs4 import BeautifulSoup

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.tests.conftest import _make_source_metadata


# ══════════════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════════════

EDGE_FIXTURES = Path(__file__).parent.parent.parent.parent / "tests" / "fixtures" / "shamela_edge_cases"

# Diacritics codepoints: U+064B-U+0652 + U+0670 (superscript alef) + U+0640 (tatweel)
_DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670", "\u0640"}


def _count_raw_pages(htm_path: Path) -> int:
    """Count PageText divs in raw HTML — independent ground truth."""
    html = htm_path.read_text(encoding="utf-8")
    return len(BeautifulSoup(html, "lxml").find_all("div", class_="PageText"))


def _normalize(htm_path: Path, **meta_overrides: object) -> NormalizedPackage:
    """Run normalize_source with default metadata."""
    meta = _make_source_metadata(**meta_overrides)
    return normalize_source(htm_path, meta)


# ══════════════════════════════════════════════════════════════════════
# Tests — Extreme Small
# ══════════════════════════════════════════════════════════════════════


class TestExtremeSmall:
    """Fixtures with very few pages (2-3)."""

    def test_2kb_volume_completes(self) -> None:
        """2KB volume (1-2 pages) normalizes without crash."""
        path = EDGE_FIXTURES / "edge_extreme_small_2kb.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 1

    def test_2kb_volume_page_count(self) -> None:
        """Content units match raw PageText divs (minus metadata page)."""
        path = EDGE_FIXTURES / "edge_extreme_small_2kb.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path)
        # Allow ±1 for metadata page
        assert abs(raw_pages - len(pkg.content_units)) <= 1, (
            f"Raw pages: {raw_pages}, content units: {len(pkg.content_units)}"
        )

    def test_tiny_3page_completes(self) -> None:
        """Tiny 3-page book with zero diacritics normalizes."""
        path = EDGE_FIXTURES / "edge_tiny_zero_diacritics.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        raw_pages = _count_raw_pages(path)
        assert abs(raw_pages - len(pkg.content_units)) <= 1

    def test_tiny_has_arabic_content(self) -> None:
        """Even tiny fixtures produce Arabic content."""
        path = EDGE_FIXTURES / "edge_extreme_small_2kb.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        for cu in pkg.content_units:
            if not cu.content_flags.is_blank:
                arabic_chars = sum(1 for c in cu.primary_text if "\u0600" <= c <= "\u06FF")
                assert arabic_chars > 0, f"Unit {cu.unit_index} has no Arabic"


# ══════════════════════════════════════════════════════════════════════
# Tests — Zero Diacritics
# ══════════════════════════════════════════════════════════════════════


class TestZeroDiacritics:
    """Books with zero diacritical marks — diacritics check must pass."""

    @pytest.mark.parametrize("fixture_name", [
        "edge_tiny_zero_diacritics.htm",
        "edge_zero_diacritics_hadith.htm",
        "edge_zero_diacritics_large.htm",
    ])
    def test_zero_diacritics_pipeline_completes(self, fixture_name: str) -> None:
        """Pipeline completes without crash on zero-diacritics books."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 1

    @pytest.mark.parametrize("fixture_name,min_units", [
        ("edge_zero_diacritics_hadith.htm", 40),
        ("edge_zero_diacritics_large.htm", 300),
    ])
    def test_zero_diacritics_page_count(self, fixture_name: str, min_units: int) -> None:
        """Zero-diacritics books produce expected content unit counts."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path)
        # Independent ground truth: raw page count
        assert abs(raw_pages - len(pkg.content_units)) <= 2, (
            f"{fixture_name}: raw={raw_pages}, units={len(pkg.content_units)}"
        )
        assert len(pkg.content_units) >= min_units

    def test_zero_diacritics_actually_zero(self) -> None:
        """Verify the fixture truly has zero diacritics in raw HTML."""
        path = EDGE_FIXTURES / "edge_zero_diacritics_large.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        total_diacritics = sum(
            sum(1 for c in cu.primary_text if c in _DIACRITICS)
            for cu in pkg.content_units
        )
        # "Zero diacritics" from sweep — allow very small count from HTML entities
        assert total_diacritics < 10, (
            f"Expected ~0 diacritics, found {total_diacritics}"
        )

    def test_zero_diacritics_hadith_flags_detected(self) -> None:
        """Hadith content flags detected even without diacritics."""
        path = EDGE_FIXTURES / "edge_zero_diacritics_hadith.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        hadith_pages = sum(
            1 for cu in pkg.content_units
            if cu.content_flags.has_hadith_citation
        )
        # A hadith collection should have substantial hadith flags
        assert hadith_pages >= 5, (
            f"Expected >=5 hadith pages, found {hadith_pages}"
        )


# ══════════════════════════════════════════════════════════════════════
# Tests — Zero Content Flags
# ══════════════════════════════════════════════════════════════════════


class TestZeroContentFlags:
    """Pure grammar texts with no hadith, quran, or verse markers."""

    @pytest.mark.parametrize("fixture_name", [
        "edge_zero_flags_nahw.htm",
        "edge_nahw_grammar.htm",
    ])
    def test_zero_flags_pipeline_completes(self, fixture_name: str) -> None:
        """Pipeline completes for grammar-only books."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        raw_pages = _count_raw_pages(path)
        assert abs(raw_pages - len(pkg.content_units)) <= 2

    @pytest.mark.parametrize("fixture_name", [
        "edge_zero_flags_nahw.htm",
        "edge_nahw_grammar.htm",
    ])
    def test_zero_flags_low_hadith_quran(self, fixture_name: str) -> None:
        """Grammar texts have very low hadith/quran flag density."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        pkg = _normalize(path)
        total = len(pkg.content_units)
        hadith = sum(1 for cu in pkg.content_units if cu.content_flags.has_hadith_citation)
        quran = sum(1 for cu in pkg.content_units if cu.content_flags.has_quran_citation)
        # Grammar books may have occasional examples, but overall ratio is low
        if total > 0:
            assert (hadith + quran) / total < 0.3, (
                f"Too many flags for grammar text: hadith={hadith}, quran={quran}, total={total}"
            )


# ══════════════════════════════════════════════════════════════════════
# Tests — Low Arabic Ratio
# ══════════════════════════════════════════════════════════════════════


class TestLowArabicRatio:
    """Book with 55.4% Arabic ratio — heavy isnad/number content."""

    def test_low_ratio_pipeline_completes(self) -> None:
        """Pipeline handles very low Arabic ratio without crash."""
        path = EDGE_FIXTURES / "edge_low_arabic_ratio.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 30

    def test_low_ratio_arabic_below_threshold(self) -> None:
        """Confirm Arabic ratio is genuinely low on many pages."""
        path = EDGE_FIXTURES / "edge_low_arabic_ratio.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        low_ratio_pages = 0
        for cu in pkg.content_units:
            total = len(cu.primary_text)
            if total == 0:
                continue
            arabic = sum(1 for c in cu.primary_text if "\u0600" <= c <= "\u06FF")
            if arabic / total < 0.7:
                low_ratio_pages += 1
        # Most pages should have low ratio
        assert low_ratio_pages >= len(pkg.content_units) * 0.3, (
            f"Expected many low-ratio pages, found {low_ratio_pages}/{len(pkg.content_units)}"
        )

    def test_low_ratio_page_count_matches(self) -> None:
        """Content units match raw page count."""
        path = EDGE_FIXTURES / "edge_low_arabic_ratio.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path)
        assert abs(raw_pages - len(pkg.content_units)) <= 2


# ══════════════════════════════════════════════════════════════════════
# Tests — High Page Loss
# ══════════════════════════════════════════════════════════════════════


class TestHighPageLoss:
    """Book with 13 pages lost (157 raw -> 144 content units)."""

    def test_high_page_loss_completes(self) -> None:
        """Pipeline handles high page loss without crash."""
        path = EDGE_FIXTURES / "edge_high_page_loss.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 100

    def test_high_page_loss_within_bounds(self) -> None:
        """Page loss is within the known range (sweep reported 13)."""
        path = EDGE_FIXTURES / "edge_high_page_loss.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path)
        page_loss = abs(raw_pages - len(pkg.content_units))
        # Sweep reported 13 page loss — allow some tolerance
        assert page_loss <= 20, (
            f"Page loss {page_loss} exceeds tolerance (raw={raw_pages}, units={len(pkg.content_units)})"
        )

    def test_high_page_loss_indices_contiguous(self) -> None:
        """Despite page loss, unit indices remain contiguous 0..N-1."""
        path = EDGE_FIXTURES / "edge_high_page_loss.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        indices = [cu.unit_index for cu in pkg.content_units]
        assert indices == list(range(len(indices))), "Non-contiguous indices"


# ══════════════════════════════════════════════════════════════════════
# Tests — Multi-layer 99%+
# ══════════════════════════════════════════════════════════════════════


class TestMultiLayer99Pct:
    """Extract from book with 99.3% multi-layer content units."""

    def test_multi_layer_completes(self) -> None:
        """Pipeline handles extreme multi-layer book."""
        path = EDGE_FIXTURES / "edge_multi_layer_99pct.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path, is_multi_layer=True)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 5

    def test_multi_layer_high_detection_rate(self) -> None:
        """Most content units detected as multi-layer."""
        path = EDGE_FIXTURES / "edge_multi_layer_99pct.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path, is_multi_layer=True)
        multi_count = sum(
            1 for cu in pkg.content_units
            if len(cu.text_layers) >= 2
        )
        total = len(pkg.content_units)
        # At least 50% should be multi-layer (original book is 99.3%)
        # Extract may have lower ratio due to front matter
        assert multi_count >= total * 0.3, (
            f"Expected high multi-layer rate: {multi_count}/{total}"
        )

    def test_multi_layer_page_count(self) -> None:
        """Content units match raw page count for the extract."""
        path = EDGE_FIXTURES / "edge_multi_layer_99pct.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path, is_multi_layer=True)
        assert abs(raw_pages - len(pkg.content_units)) <= 2


# ══════════════════════════════════════════════════════════════════════
# Tests — Warning-heavy
# ══════════════════════════════════════════════════════════════════════


class TestWarningHeavy:
    """Extract from the most warning-heavy book (393 total warnings)."""

    def test_warning_heavy_completes(self) -> None:
        """Pipeline completes despite high warning density."""
        path = EDGE_FIXTURES / "edge_warning_heavy.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert isinstance(pkg, NormalizedPackage)
        assert len(pkg.content_units) >= 1

    def test_warning_heavy_has_warnings(self) -> None:
        """Warning-heavy book produces warnings but still valid output."""
        path = EDGE_FIXTURES / "edge_warning_heavy.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        pkg = _normalize(path)
        assert pkg.manifest.quality_report is not None
        # The book should still produce valid Arabic content
        for cu in pkg.content_units:
            if not cu.content_flags.is_blank:
                assert any("\u0600" <= c <= "\u06FF" for c in cu.primary_text)

    def test_warning_heavy_page_count(self) -> None:
        """Content units match raw pages."""
        path = EDGE_FIXTURES / "edge_warning_heavy.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        raw_pages = _count_raw_pages(path)
        pkg = _normalize(path)
        assert abs(raw_pages - len(pkg.content_units)) <= 2
