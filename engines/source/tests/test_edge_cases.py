"""Edge case tests for source engine — format detection and extraction.

Tests the 10 edge case fixtures from the weekend corpus sweep through the
source engine's format detection and Shamela HTML extraction pipelines.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.source.contracts import SourceFormat
from engines.source.src.extractors.shamela_html import extract_shamela_metadata
from engines.source.src.format_detection import detect_format


EDGE_FIXTURES = Path(__file__).resolve().parents[3] / "tests" / "fixtures" / "shamela_edge_cases"

EDGE_FIXTURE_FILES = [
    "edge_extreme_small_2kb.htm",
    "edge_tiny_zero_diacritics.htm",
    "edge_zero_diacritics_hadith.htm",
    "edge_zero_flags_nahw.htm",
    "edge_low_arabic_ratio.htm",
    "edge_high_page_loss.htm",
    "edge_zero_diacritics_large.htm",
    "edge_multi_layer_99pct.htm",
    "edge_nahw_grammar.htm",
    "edge_warning_heavy.htm",
]


class TestEdgeCaseFormatDetection:
    """All edge case fixtures should be detected as Shamela HTML."""

    @pytest.mark.parametrize("fixture_name", EDGE_FIXTURE_FILES)
    def test_format_detection(self, fixture_name: str) -> None:
        """Edge case fixture detected as SHAMELA_HTML."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        assert detect_format(path) == SourceFormat.SHAMELA_HTML


class TestEdgeCaseExtraction:
    """Shamela extraction completes on all edge case fixtures."""

    @pytest.mark.parametrize("fixture_name", EDGE_FIXTURE_FILES)
    def test_extraction_completes(self, fixture_name: str) -> None:
        """Shamela extraction produces a result without crash."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        result = extract_shamela_metadata(path)
        # Should produce a result dict with at least title_full
        assert isinstance(result, dict)
        assert "title_full" in result

    @pytest.mark.parametrize("fixture_name", EDGE_FIXTURE_FILES)
    def test_extraction_has_page_count(self, fixture_name: str) -> None:
        """Extraction produces a page count for all fixtures."""
        path = EDGE_FIXTURES / fixture_name
        if not path.exists():
            pytest.skip(f"Fixture {fixture_name} not found")
        result = extract_shamela_metadata(path)
        assert "page_count" in result
        assert isinstance(result["page_count"], int)
        assert result["page_count"] >= 1

    def test_extreme_small_extraction(self) -> None:
        """2KB fixture extracts basic metadata."""
        path = EDGE_FIXTURES / "edge_extreme_small_2kb.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        result = extract_shamela_metadata(path)
        assert result["page_count"] >= 1
        assert result.get("title_full")  # Should have some title

    def test_large_zero_diacritics_extraction(self) -> None:
        """Large zero-diacritics book extracts full metadata."""
        path = EDGE_FIXTURES / "edge_zero_diacritics_large.htm"
        if not path.exists():
            pytest.skip("Fixture not found")
        result = extract_shamela_metadata(path)
        assert result["page_count"] >= 300
