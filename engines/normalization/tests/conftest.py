"""Shared test infrastructure for normalization engine tests.

Extracted from test_layer_detection.py (Session 4) for reuse across
test_content_flagger.py, test_boundary_continuity.py, test_pass6_assembly.py.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

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
from engines.normalization.src.normalizers.shamela import (
    CleanedPage,
    ShamelaNormalizer,
)
from engines.source.contracts import (
    InferredFieldConfidence,
    ScholarReference,
    SourceMetadata,
    TextLayer,
    TrustworthinessFactor,
)


# ══════════════════════════════════════════════════════════════════════
# Path constants
# ══════════════════════════════════════════════════════════════════════

FIXTURES_REAL = Path("tests/fixtures/shamela_real")
FIXTURES_ENGINE = Path("engines/normalization/tests/fixtures")
IBN_AQIL = FIXTURES_ENGINE / "shamela_ibn_aqil.htm"


# ══════════════════════════════════════════════════════════════════════
# Factory functions
# ══════════════════════════════════════════════════════════════════════


def _make_source_metadata(**overrides: Any) -> SourceMetadata:
    """Factory for SourceMetadata with sensible defaults.

    Returns a valid SourceMetadata with all 23+ required fields populated.
    Tests pass only the fields they care about via overrides.
    """
    defaults: dict[str, Any] = {
        "source_id": "src_test0001",
        "work_id": "wrk_test_test",
        "human_label": "Test Source",
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
        "frozen_path": "library/sources/src_test0001/frozen/",
        "frozen_hash": "abc123",
        "frozen_file_hashes": {"test.htm": "abc123"},
    }
    defaults.update(overrides)
    return SourceMetadata(**defaults)


def _make_text_layers_sharh() -> list[TextLayer]:
    """Standard matn+sharh layer pair for ibn_aqil-style tests."""
    return [
        TextLayer(
            layer_type="matn",
            author=ScholarReference(
                canonical_id="sch_00001",
                name_arabic="ابن مالك",
                confidence=1.0,
                source_of_identification="test",
            ),
        ),
        TextLayer(
            layer_type="sharh",
            author=ScholarReference(
                canonical_id="sch_00002",
                name_arabic="ابن عقيل",
                confidence=1.0,
                source_of_identification="test",
            ),
        ),
    ]


def _make_cleaned_page(
    primary_text: str,
    bold_spans: list[tuple[int, int, str]] | None = None,
    unit_index: int = 0,
    **overrides: Any,
) -> CleanedPage:
    """Create a minimal CleanedPage for unit testing.

    Accepts additional keyword overrides for CleanedPage fields
    (e.g., title_spans, has_verse, has_tables, warnings).
    """
    fields: dict[str, Any] = {
        "unit_index": unit_index,
        "volume": 1,
        "primary_text": primary_text,
        "bold_spans": bold_spans or [],
    }
    fields.update(overrides)
    return CleanedPage(**fields)


def _make_content_unit(
    primary_text: str = "بسم الله الرحمن الرحيم وبعد فهذا كتاب في النحو",
    unit_index: int = 0,
    source_id: str = "src_test0001",
    **overrides: Any,
) -> ContentUnit:
    """Create a minimal valid ContentUnit for testing.

    Builds text_layers covering [0, len(primary_text)) automatically.
    """
    fields: dict[str, Any] = {
        "source_id": source_id,
        "unit_index": unit_index,
        "physical_page": PhysicalPage(volume=1, page_number_display=None, page_number_int=None),
        "primary_text": primary_text,
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=0,
                end=len(primary_text),
                confidence=1.0,
            ),
        ],
        "footnotes": [],
        "content_flags": ContentFlags(),
        "text_fidelity": TextFidelity(score=TextFidelityLevel.HIGH, ocr_confidence=None),
        "boundary_continuity": None,
        "verse_info": None,
        "discourse_flow": None,
    }
    fields.update(overrides)
    return ContentUnit(**fields)


def _make_normalized_package(
    num_units: int = 1,
    primary_text: str = "بسم الله الرحمن الرحيم وبعد فهذا كتاب في النحو",
    source_id: str = "src_test0001",
    **overrides: Any,
) -> NormalizedPackage:
    """Factory for a minimal valid NormalizedPackage.

    Builds N content units with contiguous unit_index, a single-entry
    layer_map, a root division covering [0, N-1], and a valid manifest.
    Tests override individual fields via overrides or by mutating the result.

    Supported overrides:
      - content_units: replace auto-generated units
      - manifest: replace auto-generated manifest
      - Any NormalizedManifest field: applied to the generated manifest
    """
    # Build content units unless overridden
    content_units = overrides.pop("content_units", None)
    if content_units is None:
        content_units = [
            _make_content_unit(
                primary_text=primary_text,
                unit_index=i,
                source_id=source_id,
            )
            for i in range(num_units)
        ]

    # Build manifest unless overridden
    manifest = overrides.pop("manifest", None)
    if manifest is None:
        manifest_fields: dict[str, Any] = {
            "source_id": source_id,
            "normalizer_id": "kr.normalization.test_v1",
            "normalization_utc": "2026-01-01T00:00:00+00:00",
            "division_tree": [
                DivisionNode(
                    div_id=f"div_{source_id}_0_0",
                    division_type=None,
                    heading_text="root",
                    heading_level=0,
                    start_unit_index=0,
                    end_unit_index=max(0, len(content_units) - 1),
                    detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                    confidence=HeadingConfidence.HIGH,
                ),
            ],
            "layer_map": [
                LayerMapEntry(
                    layer_type=LayerType.SHARH,
                    author_canonical_id=None,
                    confidence=1.0,
                ),
            ],
            "structural_format": StructuralFormat.PROSE,
            "text_fidelity_summary": TextFidelitySummary(
                mean_ocr_confidence=None,
                character_level_fidelity_estimate=None,
                pages_with_warnings=0,
                total_pages=len(content_units),
            ),
            "total_content_units": len(content_units),
            "quality_report": QualityReport(),
        }
        manifest_fields.update(overrides)
        manifest = NormalizedManifest(**manifest_fields)

    return NormalizedPackage(
        manifest=manifest,
        content_units=content_units,
    )


@pytest.fixture
def normalizer() -> ShamelaNormalizer:
    return ShamelaNormalizer()


def _wrap_page(content: str, page_num: str | None = None) -> str:
    """Wrap content in a PageText div with optional page number."""
    parts = ["<div class='PageText'>"]
    if page_num is not None:
        parts.append(
            f"<div class='PageHead'>"
            f"<span class='PageNumber'>(ص: {page_num})</span>"
            f"<hr/></div>"
        )
    parts.append(content)
    parts.append("</div>")
    return "".join(parts)


def _make_html(*page_contents: str) -> str:
    """Build a minimal Shamela HTML document from page contents."""
    return (
        "<html><head></head><body>"
        + "".join(page_contents)
        + "</body></html>"
    )


def _full_pipeline(
    normalizer: ShamelaNormalizer, html: str, volume: int = 1
) -> list[CleanedPage]:
    """Run Passes 1–3 on HTML text."""
    raw = normalizer._pass1_parse(html, volume=volume, seq_offset=0)
    sep = normalizer._pass2_separate(raw)
    return normalizer._pass3_clean(sep)


def _assert_full_coverage(segments: list[TextLayerSegment], text_len: int) -> None:
    """Assert segments cover [0, text_len) with no gaps."""
    if text_len == 0:
        assert segments == []
        return
    assert segments[0].start == 0, f"First segment starts at {segments[0].start}, not 0"
    assert segments[-1].end == text_len, (
        f"Last segment ends at {segments[-1].end}, not {text_len}"
    )
    for i in range(len(segments) - 1):
        assert segments[i].end == segments[i + 1].start, (
            f"Gap between segments {i} and {i+1}: "
            f"[{segments[i].end}, {segments[i+1].start})"
        )
