"""Tests for multi-layer text detection (Pass 5) — SPEC §4.A.5.

19 test categories covering:
  ADV-011: Bold with transition marker (two-factor conflict)
  ADV-012: Bold at exactly 5% boundary
  ADV-013: Entire page bold (100%)
  ADV-014: Coverage gap
  ADV-015: Metadata single-layer, normalizer detects multi-layer
  #6:  ibn_aqil real fixture (full pipeline)
  #7:  Single-layer passthrough
  #8:  Transition marker detection
  #9:  Bracket detection
  #10: Short bracket exclusion
  #11: Layer map construction
  #12: Bold HTML cleaning
  #13: Multiple markers interleaved
  #14: Empty primary_text
  #15: Duplicate bold text
  #16: Author canonical_id mapping
  #17: Matn proportion warning
  #18: Conservative default
  #19: Marker_state persistence
"""

from __future__ import annotations

import logging
from typing import Any

import pytest

from engines.normalization.contracts import LayerMapEntry, LayerType, TextLayerSegment
from engines.normalization.src.errors import NormErrorCode
from engines.normalization.src.layer_detector import (
    LayerBoundary,
    PageDetectionResult,
    TRANSITION_MARKER_PATTERNS,
    _apply_conservative_default,
    _assign_author_ids,
    _build_layer_map,
    _build_segments,
    _classify_bold_signal,
    _detect_bracket_regions,
    _detect_transition_markers,
    _fill_gaps,
    _map_bold_to_primary,
    _merge_adjacent,
    _resolve_default_commentary_layer,
    detect_layers,
    pre_scan_multi_layer,
)
from engines.normalization.src.normalizers.shamela import CleanedPage
from engines.source.contracts import ScholarReference, TextLayer

# Reuse shared test infrastructure from conftest.py
from engines.normalization.tests.conftest import (
    FIXTURES_ENGINE,
    FIXTURES_REAL,
    IBN_AQIL,
    _assert_full_coverage,
    _full_pipeline,
    _make_cleaned_page,
    _make_html,
    _make_source_metadata,
    _make_text_layers_sharh,
    _wrap_page,
)


# ══════════════════════════════════════════════════════════════════════
# ADV-011: Bold with transition marker (two-factor conflict)
# ══════════════════════════════════════════════════════════════════════


class TestADV011BoldWithMarker:
    """Bold span containing a transition marker → excluded as layer indicator."""

    def test_bold_with_marker_inside_returns_emphasis(self):
        """Bold >=50 chars with 'قوله:' inside → emphasis, not layer_indicator."""
        # Construct ~500 char text. Bold region containing "قوله:" (marker inside)
        bold_text = (
            "هذا النص الطويل يحتوي على قوله: في داخل النص المعلم وهو نص "
            "تجريبي للاختبار فقط لا غير"
        )
        assert len(bold_text) >= 50  # passes two-factor length check
        remaining = "و" * (500 - len(bold_text) - 1)  # pad to ~500 chars
        primary_text = bold_text + "\n" + remaining

        page = _make_cleaned_page(
            primary_text=primary_text,
            bold_spans=[(0, 100, bold_text)],  # HTML coords don't matter for detection
        )

        bold_regions = _map_bold_to_primary(page)
        assert len(bold_regions) == 1
        assert bold_regions[0] == (0, len(bold_text))

        classification, filtered = _classify_bold_signal(page, bold_regions, True)
        assert classification == "emphasis"
        assert filtered == []


# ══════════════════════════════════════════════════════════════════════
# ADV-012: Bold at exactly 5% boundary
# ══════════════════════════════════════════════════════════════════════


class TestADV012BoldBoundary:
    """Bold at exactly 5% threshold — boundary precision test."""

    @pytest.mark.parametrize(
        "bold_len,expected_class",
        [
            (50, "layer_indicator"),  # 50/1000 = 5.0%, NOT < 5%
            (49, "emphasis"),         # 49/1000 = 4.9% < 5%
        ],
    )
    def test_bold_percentage_boundary(
        self, bold_len: int, expected_class: str
    ):
        bold_text = "ب" * bold_len
        remaining = "ا" * (1000 - bold_len)
        primary_text = bold_text + remaining

        page = _make_cleaned_page(
            primary_text=primary_text,
            bold_spans=[(0, bold_len + 10, bold_text)],
        )

        bold_regions = _map_bold_to_primary(page)
        classification, filtered = _classify_bold_signal(page, bold_regions, True)
        assert classification == expected_class
        if expected_class == "layer_indicator":
            assert len(filtered) == 1
        else:
            assert filtered == []


# ══════════════════════════════════════════════════════════════════════
# ADV-013: Entire page bold (100%)
# ══════════════════════════════════════════════════════════════════════


class TestADV013EntirePageBold:
    """100% bold → emphasis. Full page attributed to default commentary."""

    def test_full_page_bold_is_emphasis(self):
        text = "هذا النص كله بخط عريض " * 20  # ~440 chars, all bold
        page = _make_cleaned_page(
            primary_text=text,
            bold_spans=[(0, len(text) + 10, text)],
        )

        bold_regions = _map_bold_to_primary(page)
        classification, _ = _classify_bold_signal(page, bold_regions, True)
        assert classification == "emphasis"

    def test_full_page_bold_gets_default_commentary(self):
        text = "هذا النص كله بخط عريض " * 20
        metadata = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )

        page = _make_cleaned_page(
            primary_text=text,
            bold_spans=[(0, len(text) + 10, text)],
        )

        result = detect_layers(page, metadata, True, LayerType.SHARH)
        assert len(result.segments) == 1
        assert result.segments[0].layer_type == LayerType.SHARH
        assert result.segments[0].start == 0
        assert result.segments[0].end == len(text)


# ══════════════════════════════════════════════════════════════════════
# ADV-014: Coverage gap
# ══════════════════════════════════════════════════════════════════════


class TestADV014CoverageGap:
    """Gaps in segment arrays are filled with UNCERTAIN by _fill_gaps.

    The state machine naturally covers all regions (no gaps from the walk
    itself), but _fill_gaps is a safety net for edge cases. We test it
    directly with hand-crafted segment arrays that have gaps.
    """

    def test_gap_filled_with_uncertain(self):
        """Gap [90, 95) between two segments → UNCERTAIN at confidence 0.30."""
        segments = [
            TextLayerSegment(
                layer_type=LayerType.MATN, start=0, end=90, confidence=0.75
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH, start=95, end=200, confidence=0.80
            ),
        ]

        filled = _fill_gaps(segments, 200)

        # Verify full coverage
        _assert_full_coverage(filled, 200)

        # Check that the gap is UNCERTAIN
        gap_segs = [s for s in filled if s.layer_type == LayerType.UNCERTAIN]
        assert len(gap_segs) == 1
        gap = gap_segs[0]
        assert gap.start == 90
        assert gap.end == 95
        assert gap.confidence <= 0.30

    def test_build_segments_always_full_coverage(self):
        """The state machine produces gapless output for any input."""
        primary_text = "ا" * 200

        # Bold [0, 90), marker at 95 — the walk covers [90, 95) naturally
        segments = _build_segments(
            primary_text,
            bold_regions=[(0, 90)],
            markers=[
                LayerBoundary(
                    char_offset=95,
                    to_layer=LayerType.SHARH,
                    confidence=0.80,
                    marker_text="أي:",
                )
            ],
            bracket_regions=[],
            default_commentary_layer=LayerType.SHARH,
        )

        _assert_full_coverage(segments, 200)
        # Every char is covered — no UNCERTAIN gaps
        for i in range(200):
            covered = any(s.start <= i < s.end for s in segments)
            assert covered, f"Char {i} not covered by any segment"


# ══════════════════════════════════════════════════════════════════════
# ADV-015: Metadata says single-layer, normalizer detects multi-layer
# ══════════════════════════════════════════════════════════════════════


class TestADV015MetadataOverride:
    """Pre-scan detects multi-layer signals despite metadata.is_multi_layer=False."""

    def test_pre_scan_detects_multi_layer(self):
        """5 pages with bold >10% and markers → pre_scan returns True."""
        pages: list[CleanedPage] = []
        for i in range(5):
            bold_text = "قال المصنف هنا النص الأصلي للمتن الذي يشرحه المؤلف"
            sharh_text = " قوله: هذا النص شرح للمتن"
            full = bold_text + sharh_text
            pages.append(
                _make_cleaned_page(
                    primary_text=full,
                    bold_spans=[(0, len(bold_text) + 10, bold_text)],
                    unit_index=i,
                )
            )

        assert pre_scan_multi_layer(pages) is True

    def test_pre_scan_negative_for_single_layer(self):
        """5 pages with no bold, no markers → pre_scan returns False."""
        pages = [
            _make_cleaned_page(
                primary_text="هذا نص عادي بدون إشارات طبقية " * 5,
                unit_index=i,
            )
            for i in range(5)
        ]
        assert pre_scan_multi_layer(pages) is False

    def test_pass5_logs_warning_on_override(self, normalizer, caplog):
        """Full integration: _pass5_detect_layers logs NORM_LAYER_UNCERTAIN."""
        pages: list[CleanedPage] = []
        for i in range(5):
            bold_text = "قال المصنف هنا النص الأصلي للمتن الذي يشرحه المؤلف"
            sharh_text = " قوله: هذا النص شرح وتفسير للمتن الأصلي"
            full = bold_text + sharh_text
            pages.append(
                _make_cleaned_page(
                    primary_text=full,
                    bold_spans=[(0, len(bold_text) + 10, bold_text)],
                    unit_index=i,
                )
            )

        metadata = _make_source_metadata(
            is_multi_layer=False,
            text_layers=[],
        )

        with caplog.at_level(logging.WARNING):
            normalizer._pass5_detect_layers(pages, metadata)

        assert any(
            NormErrorCode.LAYER_UNCERTAIN.value in record.message
            for record in caplog.records
        )


# ══════════════════════════════════════════════════════════════════════
# #6: ibn_aqil real fixture (full pipeline)
# ══════════════════════════════════════════════════════════════════════


class TestIbnAqilFixture:
    """Full pipeline test on the multi-layer ibn_aqil fixture."""

    @pytest.fixture
    def ibn_aqil_pages(self, normalizer) -> list[CleanedPage]:
        html = IBN_AQIL.read_text(encoding="utf-8")
        return _full_pipeline(normalizer, html)

    @pytest.fixture
    def ibn_aqil_metadata(self) -> SourceMetadata:
        return _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )

    def test_page_count(self, ibn_aqil_pages):
        """5 content pages after metadata page removal."""
        assert len(ibn_aqil_pages) == 5

    def test_page0_matn_plus_sharh(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Page 0 (ص: ١٥): MATN segment from bold verse + SHARH after."""
        page = ibn_aqil_pages[0]
        result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)

        _assert_full_coverage(result.segments, len(page.primary_text))

        layer_types = [s.layer_type for s in result.segments]
        assert LayerType.MATN in layer_types
        assert LayerType.SHARH in layer_types

        # MATN segment starts at 0 (bold verse is first)
        matn_seg = [s for s in result.segments if s.layer_type == LayerType.MATN][0]
        assert matn_seg.start == 0
        assert matn_seg.confidence >= 0.70

    def test_page1_sharh_only(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Page 1 (ص: ١٦): SHARH only — no bold, no standalone markers."""
        page = ibn_aqil_pages[1]
        result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)

        _assert_full_coverage(result.segments, len(page.primary_text))

        layer_types = {s.layer_type for s in result.segments}
        assert layer_types == {LayerType.SHARH}

    def test_page2_matn_plus_sharh(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Page 2 (ص: ١٧): MATN from bold verse + SHARH after."""
        page = ibn_aqil_pages[2]
        result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)

        _assert_full_coverage(result.segments, len(page.primary_text))

        layer_types = [s.layer_type for s in result.segments]
        assert LayerType.MATN in layer_types
        assert LayerType.SHARH in layer_types

    def test_page3_sharh_only(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Page 3 (ص: ١٨): SHARH only — 'أي:' creates SHARH→SHARH transition."""
        page = ibn_aqil_pages[3]
        result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)

        _assert_full_coverage(result.segments, len(page.primary_text))

        layer_types = {s.layer_type for s in result.segments}
        assert layer_types == {LayerType.SHARH}

    def test_page4_sharh_only(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Page 4 (ص: ١٩): SHARH only — no signals at all."""
        page = ibn_aqil_pages[4]
        result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)

        _assert_full_coverage(result.segments, len(page.primary_text))

        layer_types = {s.layer_type for s in result.segments}
        assert layer_types == {LayerType.SHARH}

    def test_all_pages_full_coverage(self, ibn_aqil_pages, ibn_aqil_metadata):
        """Every page has segments[0].start == 0, segments[-1].end == len(text)."""
        for page in ibn_aqil_pages:
            if page.is_blank:
                continue
            result = detect_layers(page, ibn_aqil_metadata, True, LayerType.SHARH)
            _assert_full_coverage(result.segments, len(page.primary_text))


# ══════════════════════════════════════════════════════════════════════
# #7: Single-layer passthrough
# ══════════════════════════════════════════════════════════════════════


class TestSingleLayerPassthrough:
    """Single-layer sources get one MATN segment at confidence 1.0."""

    def test_single_layer_one_segment(self):
        text = "هذا نص المتن الأصلي بدون شرح"
        metadata = _make_source_metadata(is_multi_layer=False)
        page = _make_cleaned_page(primary_text=text)

        result = detect_layers(page, metadata, False, LayerType.SHARH)

        assert len(result.segments) == 1
        seg = result.segments[0]
        assert seg.layer_type == LayerType.MATN
        assert seg.start == 0
        assert seg.end == len(text)
        assert seg.confidence == 1.0


# ══════════════════════════════════════════════════════════════════════
# #8: Transition marker detection
# ══════════════════════════════════════════════════════════════════════


class TestTransitionMarkerDetection:
    """Verify marker regex matching and char_offset computation."""

    def test_qal_al_musannif_detected(self):
        text = "وهذا الشرح ثم قال المصنف: النص الأصلي للمتن"
        boundaries = _detect_transition_markers(text, LayerType.SHARH)
        assert len(boundaries) == 1
        assert boundaries[0].to_layer == LayerType.MATN
        assert boundaries[0].confidence == 0.90
        # char_offset is after "قال المصنف: " (marker + trailing space)
        assert text[boundaries[0].char_offset :].startswith("النص")

    def test_qawluhu_detected(self):
        text = "والمراد قوله: هذا النص"
        boundaries = _detect_transition_markers(text, LayerType.SHARH)
        assert len(boundaries) == 1
        assert boundaries[0].to_layer == LayerType.MATN

    def test_ay_targets_default_commentary(self):
        text = "والمراد أي: التفسير هنا"
        boundaries = _detect_transition_markers(text, LayerType.SHARH)
        assert len(boundaries) == 1
        assert boundaries[0].to_layer == LayerType.SHARH

    def test_embedded_biqawlihi_not_matched(self):
        """'بقوله' (with ب prefix) is NOT a standalone marker."""
        text = "واحترز بقوله «لفظ» عن الإشارة"
        boundaries = _detect_transition_markers(text, LayerType.SHARH)
        # No match because بقوله has ب directly attached to قوله
        qawluhu_matches = [b for b in boundaries if "قوله" in b.marker_text]
        assert len(qawluhu_matches) == 0

    def test_qawluhu_without_colon_not_matched(self):
        """'قوله' without a colon is NOT matched."""
        text = "ومعنى قوله «لشبه من الحروف مدني» أنه لأجل شبه"
        boundaries = _detect_transition_markers(text, LayerType.SHARH)
        assert len(boundaries) == 0

    def test_qal_al_sharih_detected(self):
        """'قال الشارح:' → transition to SHARH (for 3-layer hashiyah sources)."""
        text = "والمسألة هنا قال الشارح: النص المنسوب إلى الشارح"
        boundaries = _detect_transition_markers(text, LayerType.HASHIYAH)
        sharih_matches = [b for b in boundaries if "الشارح" in b.marker_text]
        assert len(sharih_matches) == 1
        assert sharih_matches[0].to_layer == LayerType.SHARH
        assert sharih_matches[0].confidence == 0.90
        # char_offset is after "قال الشارح: "
        assert text[sharih_matches[0].char_offset:].startswith("النص")


# ══════════════════════════════════════════════════════════════════════
# #9: Bracket detection
# ══════════════════════════════════════════════════════════════════════


class TestBracketDetection:
    """Long bracket regions detected, short ones excluded."""

    def test_long_bracket_detected(self):
        text = "الشرح: [هذا هو نص المتن الأصلي الذي يشرحه المؤلف] ثم الشرح"
        regions = _detect_bracket_regions(text)
        assert len(regions) == 1
        start, end = regions[0]
        assert text[start] == "["
        assert text[end - 1] == "]"


# ══════════════════════════════════════════════════════════════════════
# #10: Short bracket exclusion
# ══════════════════════════════════════════════════════════════════════


class TestShortBracketExclusion:

    def test_quran_ref_excluded(self):
        """[التحريم: 5] (9 chars) → no bracket region."""
        text = "قال تعالى [التحريم: 5] في كتابه"
        regions = _detect_bracket_regions(text)
        assert len(regions) == 0

    def test_short_bracket_excluded(self):
        text = "انظر [المرجع] هنا"
        regions = _detect_bracket_regions(text)
        assert len(regions) == 0


# ══════════════════════════════════════════════════════════════════════
# #11: Layer map construction
# ══════════════════════════════════════════════════════════════════════


class TestLayerMapConstruction:
    """Layer map aggregates across pages with correct author info."""

    def test_ibn_aqil_layer_map(self, normalizer):
        html = IBN_AQIL.read_text(encoding="utf-8")
        pages = _full_pipeline(normalizer, html)
        metadata = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )

        _, layer_map = normalizer._pass5_detect_layers(pages, metadata)

        layer_types = {entry.layer_type for entry in layer_map}
        assert LayerType.MATN in layer_types
        assert LayerType.SHARH in layer_types

    def test_layer_map_has_markers(self, normalizer):
        html = IBN_AQIL.read_text(encoding="utf-8")
        pages = _full_pipeline(normalizer, html)
        metadata = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )

        _, layer_map = normalizer._pass5_detect_layers(pages, metadata)

        matn_entry = next(e for e in layer_map if e.layer_type == LayerType.MATN)
        assert "bold" in matn_entry.markers


# ══════════════════════════════════════════════════════════════════════
# #12: Bold HTML cleaning
# ══════════════════════════════════════════════════════════════════════


class TestBoldHTMLCleaning:
    """Nested tags in bold_spans → correct primary_text mapping."""

    def test_nested_font_in_bold(self):
        bold_inner = '<font color="red">النص المهم جداً في هذا الكتاب للشرح</font>'
        clean_text = "النص المهم جداً في هذا الكتاب للشرح"
        primary = clean_text + " وبقية الشرح"

        page = _make_cleaned_page(
            primary_text=primary,
            bold_spans=[(0, 100, bold_inner)],
        )

        regions = _map_bold_to_primary(page)
        assert len(regions) == 1
        assert regions[0] == (0, len(clean_text))


# ══════════════════════════════════════════════════════════════════════
# #13: Multiple markers interleaved
# ══════════════════════════════════════════════════════════════════════


class TestMultipleMarkers:
    """Multiple markers create alternating layer segments with no gaps."""

    def test_qawluhu_then_ay_alternation(self):
        text = "الشرح الأول للمتن قوله: نص المتن الأصلي هنا أي: وتفسير ذلك"
        markers = _detect_transition_markers(text, LayerType.SHARH)
        assert len(markers) == 2
        assert markers[0].to_layer == LayerType.MATN
        assert markers[1].to_layer == LayerType.SHARH

        segments = _build_segments(
            text,
            bold_regions=[],
            markers=markers,
            bracket_regions=[],
            default_commentary_layer=LayerType.SHARH,
        )

        _assert_full_coverage(segments, len(text))


# ══════════════════════════════════════════════════════════════════════
# #14: Empty primary_text
# ══════════════════════════════════════════════════════════════════════


class TestEmptyPrimaryText:

    def test_empty_returns_no_segments(self):
        page = _make_cleaned_page(primary_text="")
        metadata = _make_source_metadata(is_multi_layer=True)
        result = detect_layers(page, metadata, True, LayerType.SHARH)
        assert result.segments == []

    def test_build_segments_empty(self):
        segments = _build_segments(
            "", [], [], [], LayerType.SHARH
        )
        assert segments == []


# ══════════════════════════════════════════════════════════════════════
# #15: Duplicate bold text
# ══════════════════════════════════════════════════════════════════════


class TestDuplicateBoldText:
    """Sequential search assigns MATN to first (bold) occurrence only."""

    def test_duplicate_text_first_occurrence_mapped(self):
        # Same text appears twice, only first is bold
        repeated = "النص المتكرر في هذا الموضع من الكتاب المبارك"
        primary = repeated + " الشرح " + repeated
        page = _make_cleaned_page(
            primary_text=primary,
            bold_spans=[(0, 100, repeated)],
        )

        regions = _map_bold_to_primary(page)
        assert len(regions) == 1
        assert regions[0] == (0, len(repeated))


# ══════════════════════════════════════════════════════════════════════
# #16: Author canonical_id mapping
# ══════════════════════════════════════════════════════════════════════


class TestAuthorCanonicalIdMapping:
    """MATN segments carry matn author's canonical_id from metadata."""

    def test_matn_gets_author_id(self):
        text = "ب" * 200
        metadata = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )
        bold_text = "ب" * 80
        page = _make_cleaned_page(
            primary_text=text,
            bold_spans=[(0, 100, bold_text)],
        )

        result = detect_layers(page, metadata, True, LayerType.SHARH)

        matn_segs = [s for s in result.segments if s.layer_type == LayerType.MATN]
        assert len(matn_segs) >= 1
        assert matn_segs[0].author_canonical_id == "sch_00001"

        sharh_segs = [s for s in result.segments if s.layer_type == LayerType.SHARH]
        assert len(sharh_segs) >= 1
        assert sharh_segs[0].author_canonical_id == "sch_00002"


# ══════════════════════════════════════════════════════════════════════
# #17: Matn proportion warning
# ══════════════════════════════════════════════════════════════════════


class TestMatnProportionWarning:
    """55% matn across pages → NORM_LAYER_UNCERTAIN logged."""

    def test_high_matn_proportion_logs_warning(self, normalizer, caplog):
        # Build pages where bold (matn) covers >40% of text
        pages: list[CleanedPage] = []
        for i in range(5):
            matn = "م" * 120  # 120 chars matn
            sharh = "ش" * 80   # 80 chars sharh
            text = matn + sharh
            pages.append(
                _make_cleaned_page(
                    primary_text=text,
                    bold_spans=[(0, 130, matn)],
                    unit_index=i,
                )
            )

        metadata = _make_source_metadata(
            is_multi_layer=True,
            text_layers=_make_text_layers_sharh(),
        )

        with caplog.at_level(logging.WARNING):
            normalizer._pass5_detect_layers(pages, metadata)

        assert any(
            NormErrorCode.LAYER_UNCERTAIN.value in record.message
            and "40%" in record.message
            for record in caplog.records
        )


# ══════════════════════════════════════════════════════════════════════
# #18: Conservative default
# ══════════════════════════════════════════════════════════════════════


class TestConservativeDefault:
    """MATN at confidence < 0.50 → reclassified to SHARH."""

    def test_low_confidence_matn_reclassified(self):
        segments = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                start=0,
                end=100,
                confidence=0.40,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                start=100,
                end=200,
                confidence=0.60,
            ),
        ]

        result = _apply_conservative_default(segments, LayerType.SHARH)

        # After reclassification + merge, should be one SHARH segment
        assert len(result) == 1
        assert result[0].layer_type == LayerType.SHARH
        assert result[0].start == 0
        assert result[0].end == 200

    def test_high_confidence_matn_preserved(self):
        segments = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                start=0,
                end=100,
                confidence=0.75,
            ),
        ]

        result = _apply_conservative_default(segments, LayerType.SHARH)
        assert result[0].layer_type == LayerType.MATN


# ══════════════════════════════════════════════════════════════════════
# #19: Marker_state persistence across bounded regions
# ══════════════════════════════════════════════════════════════════════


class TestMarkerStatePersistence:
    """After bold_exit, text continues in marker's layer, not default."""

    def test_marker_persists_past_bold_exit(self):
        """Marker at 6 → MATN 0.90, bold [20,80). After bold_exit, [80,end) is MATN."""
        primary_text = "ا" * 150

        markers = [
            LayerBoundary(
                char_offset=6,
                to_layer=LayerType.MATN,
                confidence=0.90,
                marker_text="قوله:",
            )
        ]
        bold_regions = [(20, 80)]

        segments = _build_segments(
            primary_text,
            bold_regions=bold_regions,
            markers=markers,
            bracket_regions=[],
            default_commentary_layer=LayerType.SHARH,
        )

        _assert_full_coverage(segments, 150)

        # First segment [0, 6) should be SHARH (before marker)
        assert segments[0].layer_type == LayerType.SHARH
        assert segments[0].end == 6

        # Everything from 6 onward should be MATN (after merge)
        remaining = [s for s in segments if s.start >= 6]
        assert all(s.layer_type == LayerType.MATN for s in remaining), (
            f"Expected all MATN after offset 6, got: "
            f"{[(s.layer_type.value, s.start, s.end) for s in remaining]}"
        )

    def test_without_marker_state_bold_exit_would_revert(self):
        """Verify the scenario: WITHOUT marker_state, bold_exit reverts to SHARH.

        This test documents why marker_state is needed — it's the
        inverse of test_marker_persists_past_bold_exit.
        """
        primary_text = "ا" * 150

        # Same setup but NO marker — bold_exit should revert to default SHARH
        segments = _build_segments(
            primary_text,
            bold_regions=[(20, 80)],
            markers=[],
            bracket_regions=[],
            default_commentary_layer=LayerType.SHARH,
        )

        _assert_full_coverage(segments, 150)

        # [0, 20) SHARH, [20, 80) MATN, [80, 150) SHARH
        assert segments[0].layer_type == LayerType.SHARH
        matn_seg = [s for s in segments if s.layer_type == LayerType.MATN]
        assert len(matn_seg) == 1
        assert matn_seg[0].start == 20
        assert matn_seg[0].end == 80

        after_bold = [s for s in segments if s.start >= 80]
        assert all(s.layer_type == LayerType.SHARH for s in after_bold)


# ══════════════════════════════════════════════════════════════════════
# Helper function tests
# ══════════════════════════════════════════════════════════════════════


class TestResolveDefaultCommentaryLayer:

    def test_sharh_from_matn_sharh_pair(self):
        metadata = _make_source_metadata(text_layers=_make_text_layers_sharh())
        assert _resolve_default_commentary_layer(metadata) == LayerType.SHARH

    def test_hashiyah_when_present(self):
        layers = _make_text_layers_sharh() + [
            TextLayer(
                layer_type="hashiyah",
                author=ScholarReference(
                    canonical_id="sch_00003",
                    name_arabic="المعلق",
                    confidence=1.0,
                    source_of_identification="test",
                ),
            ),
        ]
        metadata = _make_source_metadata(text_layers=layers)
        assert _resolve_default_commentary_layer(metadata) == LayerType.HASHIYAH

    def test_empty_layers_defaults_to_sharh(self):
        metadata = _make_source_metadata(text_layers=[])
        assert _resolve_default_commentary_layer(metadata) == LayerType.SHARH


class TestMergeAdjacent:

    def test_same_type_merged(self):
        segments = [
            TextLayerSegment(layer_type=LayerType.SHARH, start=0, end=50, confidence=0.60),
            TextLayerSegment(layer_type=LayerType.SHARH, start=50, end=100, confidence=0.80),
        ]
        merged = _merge_adjacent(segments)
        assert len(merged) == 1
        assert merged[0].confidence == 0.60  # min
        assert merged[0].end == 100

    def test_different_types_not_merged(self):
        segments = [
            TextLayerSegment(layer_type=LayerType.MATN, start=0, end=50, confidence=0.75),
            TextLayerSegment(layer_type=LayerType.SHARH, start=50, end=100, confidence=0.60),
        ]
        merged = _merge_adjacent(segments)
        assert len(merged) == 2


class TestFillGaps:

    def test_gap_at_start(self):
        segments = [
            TextLayerSegment(layer_type=LayerType.SHARH, start=10, end=100, confidence=0.60),
        ]
        filled = _fill_gaps(segments, 100)
        assert filled[0].layer_type == LayerType.UNCERTAIN
        assert filled[0].start == 0
        assert filled[0].end == 10

    def test_empty_segments_filled(self):
        filled = _fill_gaps([], 50)
        assert len(filled) == 1
        assert filled[0].layer_type == LayerType.UNCERTAIN
        assert filled[0].end == 50
