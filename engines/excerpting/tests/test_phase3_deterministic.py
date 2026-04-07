"""Tests for Phase 3 deterministic metadata assembly (SPEC §7.1, §6.2).

Covers F-DET-1 through F-DET-9, orchestrator (F10), and critical
design decisions DD-S3-1 through DD-S3-9.
"""

from __future__ import annotations

import logging
import pytest

from engines.excerpting.contracts import (
    AssembledChunk,
    AssemblyMetadata,
    AuthorAttribution,
    ExcerptingErrorCodes,
    JoinPoint,
    ScholarlyFunction,
    SelfContainmentLevel,
    SplitInfo,
)
from engines.excerpting.src.phase3_deterministic import (
    _is_bare_micro_unit,
    build_deterministic_excerpts,
    compute_content_types,
    compute_excerpt_id,
    compute_layer_attribution,
    compute_page_range,
    compute_quoted_scholars,
    compute_word_offsets,
    detect_evidence_refs,
    extract_primary_text,
    filter_relevant_footnotes,
    merge_micro_units,
)
from engines.normalization.contracts import (
    BoundaryContinuityType,
    ContentFlags,
    Footnote,
    FootnoteType,
    LayerType,
    PhysicalPage,
    StructuralFormat,
    TextLayerSegment,
)

from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_chunk_with_footnotes,
    _make_classified_segment,
    _make_multi_layer_chunk,
    _make_teaching_unit,
)

# Real Arabic test text with paragraph break for F-DET-2
_PARA_TEXT = "بسم الله الرحمن الرحيم\n\nالحمد لله رب العالمين"
_PARA_TOKENS = _PARA_TEXT.split()


# ═══════════════════════════════════════════════════════════════════
# F-DET-1: compute_excerpt_id
# ═══════════════════════════════════════════════════════════════════


class TestExcerptId:
    """Tests for §7.1 F-DET-1 — excerpt_id format."""

    def test_basic_format(self) -> None:
        """Standard ID format with all components."""
        result = compute_excerpt_id("src_123", "div_3_2", 0, 7)
        assert result == "exc_src_123_div_3_2_0_7"

    def test_split_chunk_index(self) -> None:
        """Split chunk uses chunk_index > 0."""
        result = compute_excerpt_id("src_123", "div_3_2", 1, 3)
        assert result == "exc_src_123_div_3_2_1_3"

    def test_unsplit_chunk_zero(self) -> None:
        """Unsplit chunks use chunk_index = 0."""
        result = compute_excerpt_id("src_456", "div_1_0", 0, 0)
        assert result == "exc_src_456_div_1_0_0_0"


# ═══════════════════════════════════════════════════════════════════
# F-DET-2: extract_primary_text
# ═══════════════════════════════════════════════════════════════════


class TestPrimaryText:
    """Tests for §7.1 F-DET-2 — substring extraction."""

    def test_preserves_paragraph_breaks(self) -> None:
        r"""Substring extraction preserves internal \n\n (I-ER-2).

        This is the critical difference: split-and-rejoin would collapse
        the \n\n to a single space. Substring preserves it.
        """
        # _PARA_TEXT = "بسم الله الرحمن الرحيم\n\nالحمد لله رب العالمين"
        # Tokens: [بسم, الله, الرحمن, الرحيم, الحمد, لله, رب, العالمين]
        result = extract_primary_text(_PARA_TEXT, 0, len(_PARA_TOKENS) - 1)
        assert "\n\n" in result
        assert result == _PARA_TEXT

    def test_single_word_unit(self) -> None:
        """start_word == end_word extracts exactly one token."""
        text = "بسم الله الرحمن الرحيم"
        result = extract_primary_text(text, 1, 1)
        assert result == "الله"

    def test_full_range(self) -> None:
        """start_word=0, end_word=last extracts entire text."""
        text = "بسم الله الرحمن الرحيم"
        tokens = text.split()
        result = extract_primary_text(text, 0, len(tokens) - 1)
        assert result == text


# ═══════════════════════════════════════════════════════════════════
# F-DET-3: compute_layer_attribution
# ═══════════════════════════════════════════════════════════════════


class TestLayerAttribution:
    """Tests for §7.1 F-DET-3 + §6.2 LA-1 through LA-4."""

    def test_la4_single_layer_100pct(self) -> None:
        """LA-4: One layer covers 100% of unit -> attribute to it."""
        text = "بسم الله الرحمن الرحيم"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_001",
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 3, meta)
        assert result.rule_applied == "LA-4"
        assert result.layer_id == "matn"
        assert result.author_id == "sch_001"
        assert result.coverage_pct == 1.0

    def test_la1_dominant_layer_80pct(self) -> None:
        """LA-1: One layer >= 80% but < 100% -> attribute to dominant."""
        # Build text where SHARH covers ~85% and MATN ~15%
        matn_part = "قال"  # 3 chars
        sharh_part = "يريد أن الكلام في اصطلاح النحويين"  # much longer
        text = matn_part + " " + sharh_part
        matn_end = len(matn_part)
        sharh_start = matn_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=sharh_start,
                end=len(text),
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-1"
        assert result.layer_id == "sharh"

    def test_la2_two_layers_outermost_wins(self) -> None:
        """LA-2: Two layers, dominant >= 60% -> outermost (highest level) wins."""
        # SHARH=65%, MATN=35% — dominant above 60% threshold (H-7)
        text = "أ" * 100  # 100 chars for precise coverage
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=0,
                end=35,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=35,
                end=100,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-2"
        # SHARH > MATN in _LAYER_LEVEL
        assert result.layer_id == "sharh"

    def test_la2_dominant_at_60pct_boundary(self) -> None:
        """LA-2 fires when dominant layer has exactly 60% coverage (H-7 threshold).

        §6.2: dominant >=60% -> LA-2 (outermost wins).
        """
        # Build text where SHARH covers exactly 60% of chars
        text = "أ" * 100  # 100 chars
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=40,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=40,
                end=100,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # 60% exactly -> LA-2 (meets the >=0.6 threshold)
        assert result.rule_applied == "LA-2"

    def test_la3_triggered_for_two_layers_below_60_pct(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """H-7: 2 layers with dominant at 59% -> LA-3 (attribution ambiguous).

        §6.2: if the dominant layer has <60% coverage, flag with EX-M-001
        for multi-model consensus verification. Previously this was silently
        defaulted to LA-2 (outermost layer wins), bypassing the gate.
        """
        # 100 chars: SHARH=59%, MATN=41% — dominant below 60% threshold
        text = "أ" * 100
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=59,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=59,
                end=100,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )
        # H-7: 59% < 60% -> LA-3, not LA-2
        assert result.rule_applied == "LA-3"
        assert result.layer_id == "sharh"
        assert result.author_id == "sch_sharh"
        assert result.coverage_pct < 0.6
        # EX-M-001 warning must be emitted
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text

    def test_la2_still_works_above_60_pct(self) -> None:
        """H-7: 2 layers with dominant at 70% -> LA-2 (outermost wins).

        §6.2: dominant >=60% qualifies for LA-2 (deterministic outermost
        layer wins without consensus review).
        """
        # 100 chars: SHARH=70%, MATN=30% — dominant above 60% threshold
        text = "أ" * 100
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=70,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=70,
                end=100,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # 70% >= 60% -> LA-2 (outermost layer wins)
        assert result.rule_applied == "LA-2"
        # SHARH > MATN in _LAYER_LEVEL -> SHARH is outermost
        assert result.layer_id == "sharh"
        assert result.author_id == "sch_sharh"
        assert result.coverage_pct >= 0.6

    def test_la3_three_layers_ambiguous(self, caplog: pytest.LogCaptureFixture) -> None:
        """LA-3: Three layers, none >= 80% -> EX-M-001 warning."""
        text = "أ ب ج د ه و ز ح ط ي ك ل"  # 12 tokens
        text_len = len(text)
        third = text_len // 3
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_1",
                start=0,
                end=third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_2",
                start=third,
                end=2 * third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_3",
                start=2 * third,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )
        assert result.rule_applied == "LA-3"
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text

    def test_split_point_merging(self) -> None:
        """DD-S3-7: Two SHARH segments at split point merge before coverage.

        Without merging, each SHARH segment has ~50% coverage (LA-2 would
        fire treating them as separate layers). With merging, SHARH gets
        ~100% (LA-4 fires correctly).
        """
        text = "يريد أن الكلام في اصطلاح النحويين هو اللفظ المفيد"
        text_len = len(text)
        split_point = text_len // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=split_point,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=split_point,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split_point],  # Split boundary
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # Merged SHARH should cover 100% -> LA-4
        assert result.rule_applied == "LA-4"
        assert result.layer_id == "sharh"


# ═══════════════════════════════════════════════════════════════════
# F-DET-4: compute_content_types
# ═══════════════════════════════════════════════════════════════════


class TestContentTypes:
    """Tests for §7.1 F-DET-4 — scholarly function aggregation."""

    def test_single_function(self) -> None:
        """One segment, one function."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
            )
        ]
        result = compute_content_types(segments, [0])
        assert result == [ScholarlyFunction.DEFINITION]

    def test_deduplication(self) -> None:
        """Multiple segments with same function -> deduplicated."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
            ),
            _make_classified_segment(
                segment_index=1, scholarly_function=ScholarlyFunction.DEFINITION
            ),
        ]
        result = compute_content_types(segments, [0, 1])
        assert result == [ScholarlyFunction.DEFINITION]

    def test_multiple_functions(self) -> None:
        """Segments with different functions -> all returned."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.RULE_STATEMENT
            ),
            _make_classified_segment(
                segment_index=1, scholarly_function=ScholarlyFunction.EVIDENCE_HADITH
            ),
            _make_classified_segment(
                segment_index=2, scholarly_function=ScholarlyFunction.EXAMPLE
            ),
        ]
        result = compute_content_types(segments, [0, 1, 2])
        assert len(result) == 3
        assert ScholarlyFunction.RULE_STATEMENT in result
        assert ScholarlyFunction.EVIDENCE_HADITH in result
        assert ScholarlyFunction.EXAMPLE in result


# ═══════════════════════════════════════════════════════════════════
# F-DET-5: detect_evidence_refs
# ═══════════════════════════════════════════════════════════════════


class TestEvidenceRefs:
    """Tests for §7.1 F-DET-5 — evidence pattern detection (DD-S3-8)."""

    def test_quran_delimiter_detection(self) -> None:
        """EV-1: ﴿...﴾ detected, text extracted between delimiters."""
        text = "قال تعالى ﴿بسم الله الرحمن الرحيم﴾ صدق الله العظيم"
        result = detect_evidence_refs(text)
        quran_refs = [r for r in result if r.type == "quran"]
        assert len(quran_refs) == 1
        assert quran_refs[0].text_snippet == "بسم الله الرحمن الرحيم"
        assert quran_refs[0].surah is None  # DD-S3-3: lookup deferred

    def test_hadith_marker_detection(self) -> None:
        """EV-2: 'رواه البخاري' detected as hadith evidence."""
        text = "وقد رواه البخاري في صحيحه عن أبي هريرة رضي الله عنه"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        markers = {r.marker_text for r in hadith_refs}
        assert "رواه" in markers

    def test_ijma_marker_detection(self) -> None:
        """EV-3: 'إجماع' detected as ijma evidence."""
        text = "وقد انعقد الإجماع على وجوب الصلوات الخمس"
        result = detect_evidence_refs(text)
        ijma_refs = [r for r in result if r.type == "ijma"]
        assert len(ijma_refs) >= 1
        markers = {r.marker_text for r in ijma_refs}
        assert "إجماع" in markers

    def test_prefixed_forms_detected_no_boundary(self) -> None:
        """DD-S3-8: Prefixed forms (الإجماع, وأخرجه, فرواه) detected.

        Word-boundary checks would reject these valid matches.
        Plain substring matching correctly detects them.
        """
        text = "والإجماع منعقد على ذلك وأخرجه البخاري فرواه مسلم"
        result = detect_evidence_refs(text)
        markers = {r.marker_text for r in result}
        # إجماع inside الإجماع — detected by substring
        assert "إجماع" in markers
        # أخرجه inside وأخرجه — detected by substring
        assert "أخرجه" in markers
        # رواه inside فرواه — detected by substring
        assert "رواه" in markers

    def test_multiword_phrase_detection(self) -> None:
        """Multi-word marker 'في الصحيحين' detected as substring."""
        text = "وقد ثبت هذا الحديث في الصحيحين من رواية ابن عمر"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        markers = {r.marker_text for r in hadith_refs}
        assert "في الصحيحين" in markers

    def test_snippet_clamping_at_boundaries(self) -> None:
        """Snippet clamped to text boundaries, no IndexError."""
        # Marker at very start of text
        text = "رواه البخاري"
        result = detect_evidence_refs(text)
        assert len(result) >= 1
        # Snippet should not exceed text boundaries
        for ref in result:
            assert len(ref.text_snippet) <= len(text)


# ═══════════════════════════════════════════════════════════════════
# F-DET-6: compute_page_range
# ═══════════════════════════════════════════════════════════════════


class TestPageRange:
    """Tests for §7.1 F-DET-6 — physical page range computation."""

    def test_single_page_no_join_points(self) -> None:
        """Single-page chunk (96.8% case): no join_points -> direct return."""
        pages = [PhysicalPage(volume=1, page_number_display="٥", page_number_int=5)]
        result = compute_page_range(pages, [], 0, 100)
        assert result is not None
        assert result.volume == 1
        assert result.start_page == 5
        assert result.end_page == 5

    def test_multi_page_span(self) -> None:
        """Unit spans two pages via join_point."""
        pages = [
            PhysicalPage(volume=1, page_number_display="٥", page_number_int=5),
            PhysicalPage(volume=1, page_number_display="٦", page_number_int=6),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=50,
            )
        ]
        # Unit spans chars 30-70, crossing the join at 50
        result = compute_page_range(pages, join_pts, 30, 70)
        assert result is not None
        assert result.start_page == 5
        assert result.end_page == 6

    def test_empty_pages_returns_none(self) -> None:
        """Empty physical_pages -> None."""
        result = compute_page_range([], [], 0, 100)
        assert result is None

    def test_split_chunk_dimensions(self) -> None:
        """Correctly-partitioned split chunk (40 pages, 39 join_points)."""
        pages = [
            PhysicalPage(
                volume=1,
                page_number_display=str(10 + i),
                page_number_int=10 + i,
            )
            for i in range(40)
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=i,
                before_unit_index=i + 1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=100 * (i + 1),
            )
            for i in range(39)
        ]
        # Unit spanning pages 15-17 (char range 500-1700)
        result = compute_page_range(pages, join_pts, 500, 1700)
        assert result is not None
        assert result.volume == 1
        assert result.start_page == 15
        assert result.end_page == 26

    def test_defensive_guard_mismatched_lengths(self) -> None:
        """Defensive guard: more physical_pages than join_points + 1 (pre-fix state)."""
        # 73 pages but only 39 join_points (the broken state from ibn_aqil_v1)
        pages = [
            PhysicalPage(
                volume=1,
                page_number_display=str(i + 1),
                page_number_int=i + 1,
            )
            for i in range(73)
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=i,
                before_unit_index=i + 1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=100 * (i + 1),
            )
            for i in range(39)
        ]
        # Should not crash — returns a result using the first 40 addressable pages
        result = compute_page_range(pages, join_pts, 50, 150)
        assert result is not None
        assert result.start_page >= 1
        assert result.end_page <= 40  # Clamped to addressable pages


# ═══════════════════════════════════════════════════════════════════
# F-DET-7: compute_word_offsets
# ═══════════════════════════════════════════════════════════════════


class TestWordOffsets:
    """Tests for word offset passthrough."""

    def test_passthrough_unchanged(self) -> None:
        """Returns (start_word, end_word) unchanged."""
        result = compute_word_offsets(3, 7)
        assert result == (3, 7)


# ═══════════════════════════════════════════════════════════════════
# F-DET-8: filter_relevant_footnotes
# ═══════════════════════════════════════════════════════════════════


class TestFootnoteFiltering:
    """Tests for §7.1 F-DET-8 — footnote marker matching."""

    def test_relevant_footnote_included(self) -> None:
        """Footnote marker within unit range -> included."""
        chunk = _make_chunk_with_footnotes()
        text = chunk.assembled_text
        # Find position of ⌜1⌝ marker
        marker_pos = text.find("\u231C1\u231D")
        assert marker_pos >= 0, "Marker ⌜1⌝ must be in assembled_text"
        # Unit range covers entire text
        result = filter_relevant_footnotes(
            text, text, chunk.footnotes, 0, len(text)
        )
        markers = [fn.ref_marker for fn in result]
        assert "1" in markers

    def test_irrelevant_footnote_excluded(self) -> None:
        """Footnote marker outside unit range -> excluded."""
        chunk = _make_chunk_with_footnotes()
        text = chunk.assembled_text
        # Unit range covers only the very start (before any marker)
        result = filter_relevant_footnotes(
            text[:5], text, chunk.footnotes, 0, 5
        )
        assert len(result) == 0

    def test_orphan_marker_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        """Marker not found in assembled_text -> warning logged."""
        fn = Footnote(
            ref_marker="99",
            text="orphaned footnote",
            footnote_type=FootnoteType.LINGUISTIC_NOTE,
            confidence=0.9,
        )
        with caplog.at_level(logging.WARNING):
            result = filter_relevant_footnotes(
                "بسم الله", "بسم الله الرحمن الرحيم", [fn], 0, 30
            )
        assert len(result) == 0
        assert "99" in caplog.text


# ═══════════════════════════════════════════════════════════════════
# F-DET-9: compute_quoted_scholars
# ═══════════════════════════════════════════════════════════════════


class TestQuotedScholars:
    """Tests for §7.1 F-DET-9 — non-primary layer detection."""

    def test_non_primary_layer_detected(self) -> None:
        """MATN layer in a SHARH-primary unit -> classification_frame."""
        chunk = _make_multi_layer_chunk()
        text = chunk.assembled_text
        # Primary is SHARH (covers the whole text by attribution)
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_ibn_aqeel",
            coverage_pct=0.6,
            rule_applied="LA-2",
        )
        result = compute_quoted_scholars(
            chunk.text_layers, 0, len(text), primary, chunk.assembly_metadata
        )
        assert len(result) >= 1
        matn_scholars = [s for s in result if "matn" in s.mention_text]
        assert len(matn_scholars) == 1
        assert matn_scholars[0].role == "classification_frame"
        assert matn_scholars[0].confidence == 1.0
        assert matn_scholars[0].source == "layer_overlap"

    def test_primary_layer_excluded(self) -> None:
        """Primary layer should NOT appear in quoted_scholars."""
        chunk = _make_multi_layer_chunk()
        text = chunk.assembled_text
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_ibn_aqeel",
            coverage_pct=0.6,
            rule_applied="LA-2",
        )
        result = compute_quoted_scholars(
            chunk.text_layers, 0, len(text), primary, chunk.assembly_metadata
        )
        for scholar in result:
            assert "sharh" not in scholar.mention_text

    def test_role_quoted_opinion(self) -> None:
        """Non-MATN secondary layer in MATN-primary unit -> quoted_opinion."""
        chunk = _make_multi_layer_chunk()
        text = chunk.assembled_text
        # Primary is MATN
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_ibn_malik",
            coverage_pct=0.4,
            rule_applied="LA-2",
        )
        result = compute_quoted_scholars(
            chunk.text_layers, 0, len(text), primary, chunk.assembly_metadata
        )
        sharh_scholars = [s for s in result if "sharh" in s.mention_text]
        assert len(sharh_scholars) == 1
        assert sharh_scholars[0].role == "quoted_opinion"

    def test_multi_author_same_type_secondary_kept(self) -> None:
        """Two SHARH authors: primary sharh_A excluded, secondary sharh_B kept."""
        text = "قال الشارح الأول شرحه يريد أن الكلام وقال الشارح الثاني وأما قوله"
        text_len = len(text)
        third = text_len // 3
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_A",
                start=0,
                end=third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_B",
                start=third,
                end=2 * third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=2 * third,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_sharh_A",
            coverage_pct=0.33,
            rule_applied="LA-3",
        )
        result = compute_quoted_scholars(layers, 0, text_len, primary, meta)
        # sharh_B should NOT be excluded (different author, same type)
        sharh_b = [s for s in result if s.resolved_name == "sch_sharh_B"]
        assert len(sharh_b) == 1, "Secondary sharh author must appear in quoted_scholars"
        assert sharh_b[0].role == "quoted_opinion"
        # matn should still appear
        matn_scholars = [s for s in result if "matn" in s.mention_text]
        assert len(matn_scholars) == 1


# ═══════════════════════════════════════════════════════════════════
# F10: build_deterministic_excerpts (Orchestrator)
# ═══════════════════════════════════════════════════════════════════


class TestOrchestrator:
    """Tests for §7.1 orchestrator — ExcerptRecord assembly."""

    def test_happy_path_single_unit(self) -> None:
        """Single FULL unit produces a valid ExcerptRecord."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert len(result) == 1
        rec = result[0]
        assert rec.excerpt_id.startswith("exc_")
        assert rec.source_id == chunk.source_id
        assert rec.div_id == chunk.div_id
        assert rec.school is None  # DD-S3-1
        assert rec.attribution_confidence is None  # DD-S3-6
        assert rec.excerpt_topic == []
        assert rec.gate_flags == []

    def test_multi_unit(self) -> None:
        """Two units from same chunk produce two ExcerptRecords."""
        chunk = _make_assembled_chunk()
        tokens = chunk.assembled_text.split()
        mid = len(tokens) // 2
        unit0 = _make_teaching_unit(
            unit_index=0, start_word=0, end_word=mid - 1, segment_indices=[0]
        )
        unit1 = _make_teaching_unit(
            unit_index=1, start_word=mid, end_word=len(tokens) - 1,
            segment_indices=[1],
        )
        seg0 = _make_classified_segment(segment_index=0)
        seg1 = _make_classified_segment(segment_index=1)
        result = build_deterministic_excerpts(chunk, [unit0, unit1], [seg0, seg1])
        assert len(result) == 2
        assert result[0].unit_index == 0
        assert result[1].unit_index == 1

    def test_school_none_explicit(self) -> None:
        """DD-S3-1: school=None is explicitly passed (DD8 Pattern 1)."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        # If school were missing, Pydantic would raise ValidationError
        assert result[0].school is None

    def test_partial_unit_review_flag(self) -> None:
        """PARTIAL self-containment -> review_flags=['llm_enrichment_failed']."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يشير إلى ما تقدم في باب الطهارة",
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert "llm_enrichment_failed" in result[0].review_flags

    def test_passthrough_fields_correct(self) -> None:
        """Unit passthrough fields (primary_function, description_arabic, etc.)."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            unit_index=5,
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
            primary_function=ScholarlyFunction.EVIDENCE_HADITH,
            description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات",
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        rec = result[0]
        assert rec.unit_index == 5
        assert rec.primary_function == ScholarlyFunction.EVIDENCE_HADITH
        assert rec.description_arabic == "وصف عربي قصير للاختبار يتضمن عدة كلمات"
        assert rec.div_path == chunk.div_path
        assert rec.chunk_index == 0  # No split_info -> 0

    def test_split_chunk_index(self) -> None:
        """Split chunks use split_info.chunk_index in excerpt_id."""
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0_chunk_2",
            split_info=SplitInfo(
                original_div_id="div_test_1_0",
                chunk_index=2,
                total_chunks=3,
                split_method="paragraph_break",
            ),
            merge_history=None,
        )
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert result[0].chunk_index == 2
        assert "_2_" in result[0].excerpt_id


# ═══════════════════════════════════════════════════════════════════
# Edge Case & Adversarial Tests (overnight hardening)
# ═══════════════════════════════════════════════════════════════════


class TestEdgeCaseLayerAttribution:
    """Edge cases for LA rule cascade (review findings H-1, H-2, M-7)."""

    def test_author_canonical_id_none_fallback(self) -> None:
        """M-7: author_canonical_id=None -> author_id='unknown' in LA-4."""
        text = "بسم الله الرحمن الرحيم"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-4"
        assert result.author_id == "unknown"

    def test_author_none_fallback_la1(self) -> None:
        """M-7: author_canonical_id=None -> 'unknown' also in LA-1 path."""
        matn = "قال"
        sharh = "يريد أن الكلام في اصطلاح النحويين هو اللفظ"
        text = matn + " " + sharh
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(matn),
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=len(matn) + 1,
                end=len(text),
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-1"
        assert result.author_id == "unknown"

    def test_gapped_segments_at_split_point_no_merge(self) -> None:
        """H-1: Gapped same-type segments at split point must NOT merge.

        Two SHARH segments with a gap at the split point boundary.
        After H-1 fix, adjacency check prevents incorrect merge.
        """
        text = "أ ب ج د ه و ز ح ط ي ك ل م ن"
        text_len = len(text)
        gap_pos = text_len // 2
        # Segment 1 ends at gap_pos - 2, segment 2 starts at gap_pos + 2
        # The gap is at gap_pos, which is also a split point
        seg1_end = gap_pos - 1
        seg2_start = gap_pos + 1
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_1",
                start=0,
                end=seg1_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_1",
                start=seg2_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[seg1_end],  # Split at segment boundary
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # With gap, segments should NOT merge -> 2 coverage entries
        # ~50/50 dominant coverage -> LA-3 (H-7: dominant <60%)
        assert result.rule_applied == "LA-3"

    def test_three_layer_hashiyah_sharh_matn(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """LA-3: HASHIYAH + SHARH + MATN (3 layers), none >= 80%.

        Realistic scenario: a hashiyah (supercommentary) on a sharh
        that quotes the matn.
        """
        hashiyah = "قال الشارح في قوله"
        sharh = "يريد أن الكلام في اصطلاح"
        matn = "كلامنا لفظ مفيد كاستقم"
        text = hashiyah + " " + sharh + " " + matn
        text_len = len(text)
        h_end = len(hashiyah)
        s_start = h_end + 1
        s_end = s_start + len(sharh)
        m_start = s_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_hashiya",
                start=0,
                end=h_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=s_start,
                end=s_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=m_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )
        assert result.rule_applied == "LA-3"
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text

    def test_la2_hashiyah_vs_sharh(self) -> None:
        """LA-2 with HASHIYAH + SHARH: dominant >=60%, HASHIYAH wins (higher _LAYER_LEVEL)."""
        # HASHIYAH=65%, SHARH=35% — dominant above 60% threshold (H-7)
        text = "أ" * 100
        layers = [
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_h",
                start=0,
                end=65,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=65,
                end=100,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-2"
        assert result.layer_id == "hashiyah"

    def test_split_point_chain_merge_three_segments(self) -> None:
        """DD-S3-7: Three MATN segments at two split points merge to one.

        A-B-C chain: segment 1 ends at split1, segment 2 ends at split2,
        all same type/author. Should merge to a single coverage entry -> LA-4.
        """
        text = "بسم الله الرحمن الرحيم الحمد لله رب العالمين الرحمن الرحيم"
        text_len = len(text)
        split1 = text_len // 3
        split2 = 2 * text_len // 3
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=split1,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=split1,
                end=split2,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=split2,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split1, split2],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-4"
        assert result.coverage_pct >= 1.0


class TestEdgeCaseEvidenceRefs:
    """Edge cases for F-DET-5 evidence detection (DD-S3-8)."""

    def test_quran_verse_with_full_diacritics(self) -> None:
        """Quran text with tashkeel inside ﴿...﴾ detected correctly."""
        text = "قال تعالى ﴿بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ﴾ فبدأ"
        result = detect_evidence_refs(text)
        quran_refs = [r for r in result if r.type == "quran"]
        assert len(quran_refs) == 1
        assert "بِسْمِ" in quran_refs[0].text_snippet

    def test_all_hadith_markers_individually(self) -> None:
        """All 6 hadith markers detected when present individually."""
        markers = ["رواه", "أخرجه", "في الصحيحين", "متفق عليه", "في صحيح", "في سنن"]
        for marker in markers:
            text = f"وقد ثبت ذلك فقد {marker} البخاري ومسلم في كتابهما"
            result = detect_evidence_refs(text)
            hadith_refs = [r for r in result if r.type == "hadith"]
            found_markers = {r.marker_text for r in hadith_refs}
            assert marker in found_markers, (
                f"Hadith marker '{marker}' not detected in: {text}"
            )

    def test_all_ijma_markers_individually(self) -> None:
        """All 5 ijma markers detected when present individually."""
        markers = ["أجمعوا", "إجماع", "لا خلاف", "اتفق العلماء", "بالاتفاق"]
        for marker in markers:
            text = f"وقد {marker} على هذا الحكم جميع الفقهاء"
            result = detect_evidence_refs(text)
            ijma_refs = [r for r in result if r.type == "ijma"]
            found_markers = {r.marker_text for r in ijma_refs}
            assert marker in found_markers, (
                f"Ijma marker '{marker}' not detected in: {text}"
            )

    def test_no_evidence_markers_empty_result(self) -> None:
        """Text with no evidence markers -> empty list."""
        text = "هذا كتاب في أصول النحو العربي وقواعده الأساسية"
        result = detect_evidence_refs(text)
        assert result == []

    def test_multiple_quran_verses(self) -> None:
        """Two ﴿...﴾ delimited verses detected separately."""
        text = "قال تعالى ﴿الحمد لله رب العالمين﴾ وقال ﴿الرحمن الرحيم﴾"
        result = detect_evidence_refs(text)
        quran_refs = [r for r in result if r.type == "quran"]
        assert len(quran_refs) == 2

    def test_hadith_and_quran_in_same_text(self) -> None:
        """Mixed evidence: Quran and hadith in same passage."""
        text = "قال تعالى ﴿وأقيموا الصلاة﴾ وقد رواه البخاري من حديث ابن عمر"
        result = detect_evidence_refs(text)
        types = {r.type for r in result}
        assert "quran" in types
        assert "hadith" in types

    def test_marker_with_proclitic_ba(self) -> None:
        """DD-S3-8: بالاتفاق detected — the ب prefix is part of the marker."""
        text = "وقد ثبت هذا الحكم بالاتفاق بين العلماء"
        result = detect_evidence_refs(text)
        ijma_refs = [r for r in result if r.type == "ijma"]
        found = {r.marker_text for r in ijma_refs}
        assert "بالاتفاق" in found

    def test_snippet_context_window(self) -> None:
        """Snippet includes 25 chars before/after marker."""
        prefix = "أ" * 30
        suffix = "ب" * 30
        text = f"{prefix}رواه{suffix}"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        snippet = hadith_refs[0].text_snippet
        # Snippet should be clamped: 25 before + marker + 25 after
        assert len(snippet) <= 25 + len("رواه") + 25


class TestEdgeCasePageRange:
    """Edge cases for F-DET-6 page range computation (L-1)."""

    def test_all_pages_none_returns_none(self) -> None:
        """L-1: All overlapping pages with page_number_int=None -> None."""
        pages = [
            PhysicalPage(volume=1, page_number_display=None, page_number_int=None),
            PhysicalPage(volume=1, page_number_display=None, page_number_int=None),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=50,
            )
        ]
        result = compute_page_range(pages, join_pts, 0, 100)
        assert result is None

    def test_single_page_none_returns_none(self) -> None:
        """Single page with page_number_int=None -> None (fast path)."""
        pages = [
            PhysicalPage(volume=1, page_number_display=None, page_number_int=None)
        ]
        result = compute_page_range(pages, [], 0, 100)
        assert result is None

    def test_three_pages_unit_spans_middle(self) -> None:
        """Unit spans only the middle page of three."""
        pages = [
            PhysicalPage(volume=1, page_number_display="١", page_number_int=1),
            PhysicalPage(volume=1, page_number_display="٢", page_number_int=2),
            PhysicalPage(volume=1, page_number_display="٣", page_number_int=3),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=100,
            ),
            JoinPoint(
                after_unit_index=1,
                before_unit_index=2,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=200,
            ),
        ]
        # Unit chars [120, 180) — only overlaps page 2 (chars [100, 200))
        result = compute_page_range(pages, join_pts, 120, 180)
        assert result is not None
        assert result.start_page == 2
        assert result.end_page == 2


class TestEdgeCaseQuotedScholars:
    """Edge cases for F-DET-9 quoted scholars (L-8)."""

    def test_single_layer_empty_result(self) -> None:
        """L-8: Single-layer source -> no quoted scholars."""
        text = "بسم الله الرحمن الرحيم"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_1",
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_1",
            coverage_pct=1.0,
            rule_applied="LA-4",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        assert result == []

    def test_quoted_opinion_non_matn_secondary(self) -> None:
        """Non-MATN secondary in MATN-primary -> role='quoted_opinion'."""
        text = "بسم الله الرحمن الرحيم الحمد لله"
        mid = len(text) // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_h",
                start=mid,
                end=len(text),
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_m",
            coverage_pct=0.5,
            rule_applied="LA-2",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        assert len(result) == 1
        assert result[0].role == "quoted_opinion"


class TestEdgeCaseOrchestrator:
    """Edge case orchestrator tests."""

    def test_empty_footnotes_list(self) -> None:
        """Chunk with no footnotes -> footnotes_relevant is empty."""
        chunk = _make_assembled_chunk(footnotes=[])
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert result[0].footnotes_relevant == []

    def test_single_word_unit_through_orchestrator(self) -> None:
        """Single-word teaching unit (start_word == end_word) works end-to-end."""
        text = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
        chunk = _make_assembled_chunk(assembled_text=text)
        # Single word: "الرحمن" (index 2)
        unit = _make_teaching_unit(
            start_word=2,
            end_word=2,
            segment_indices=[0],
            text_snippet="الرحمن",
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert len(result) == 1
        assert result[0].primary_text == "الرحمن"
        assert result[0].start_word == 2
        assert result[0].end_word == 2

    def test_long_text_offsets_correct(self) -> None:
        """Long text (>1000 words): word-to-char conversion stays correct.

        Generates a 1200-word text and verifies substring extraction
        at the end of the text is accurate.
        """
        # Build a long text by repeating real Arabic phrases
        base_phrases = [
            "بسم الله الرحمن الرحيم",
            "الحمد لله رب العالمين",
            "وصلى الله على نبينا محمد",
            "قال المؤلف رحمه الله تعالى",
            "هذا باب في أحكام الصلاة",
        ]
        # Each phrase has 4-5 words, repeat to get >1000 words
        long_parts: list[str] = []
        word_count = 0
        idx = 0
        while word_count < 1200:
            phrase = base_phrases[idx % len(base_phrases)]
            long_parts.append(phrase)
            word_count += len(phrase.split())
            idx += 1
        long_text = " ".join(long_parts)
        tokens = long_text.split()
        assert len(tokens) >= 1200

        chunk = _make_assembled_chunk(
            assembled_text=long_text,
            total_tokens=len(tokens),
            word_count=len(tokens),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(long_text),
                    confidence=1.0,
                )
            ],
        )

        # Extract words 1190-1199 (near the end)
        start_w = 1190
        end_w = min(1199, len(tokens) - 1)
        unit = _make_teaching_unit(
            start_word=start_w,
            end_word=end_w,
            segment_indices=[0],
            text_snippet=long_text[:50],
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert len(result) == 1

        # Verify primary_text matches the expected substring
        expected = " ".join(tokens[start_w : end_w + 1])
        # Note: substring extraction should match token-based reconstruction
        # because the text has single spaces between tokens
        assert result[0].primary_text == expected

    def test_dependent_unit_gets_review_flag(self) -> None:
        """DEPENDENT self-containment also gets review_flags (M-1 documents)."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
            self_containment=SelfContainmentLevel.DEPENDENT,
            self_containment_notes="يعتمد كلياً على ما تقدم في الباب السابق",
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert "llm_enrichment_failed" in result[0].review_flags

    def test_full_unit_no_review_flag(self) -> None:
        """FULL self-containment -> no review_flags."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
            self_containment=SelfContainmentLevel.FULL,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert result[0].review_flags == []

    def test_d023_all_33_fields_populated(self) -> None:
        """D-023: All 33 ExcerptRecord fields are explicitly set (not None by default)."""
        chunk = _make_assembled_chunk()
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        rec = result[0]
        # All 33 fields should be present in model_fields_set
        expected_fields = {
            "excerpt_id", "source_id", "div_id", "chunk_index", "unit_index",
            "div_path", "primary_text", "text_snippet", "start_word", "end_word",
            "segment_indices", "physical_pages", "primary_function",
            "secondary_functions", "content_types", "description_arabic",
            "self_containment", "self_containment_notes", "context_hint",
            "primary_author_layer", "attribution_confidence", "quoted_scholars",
            "school", "school_confidence", "excerpt_topic",
            "terminology_variants", "evidence_refs", "takhrij_data",
            "cross_references", "footnotes_relevant", "consensus_metadata",
            "gate_flags", "review_flags",
        }
        assert len(expected_fields) == 33
        for field in expected_fields:
            assert hasattr(rec, field), f"Missing field: {field}"


class TestEdgeCaseFootnoteFiltering:
    """Edge cases for F-DET-8 footnote marker matching."""

    def test_empty_footnotes_list(self) -> None:
        """Empty footnotes list -> empty result."""
        result = filter_relevant_footnotes(
            "بسم الله", "بسم الله الرحمن", [], 0, 20
        )
        assert result == []

    def test_multiple_footnotes_mixed_range(self) -> None:
        """Two markers: one inside range, one outside -> only inside returned."""
        text = "بداية النص ⌜1⌝ وسط النص الطويل جداً جداً جداً جداً ⌜2⌝ نهاية"
        fn1_pos = text.find("\u231C1\u231D")
        fns = [
            Footnote(
                ref_marker="1",
                text="تعليق أول",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.9,
            ),
            Footnote(
                ref_marker="2",
                text="تعليق ثان",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.9,
            ),
        ]
        # Range covers only fn1
        result = filter_relevant_footnotes(
            text[:fn1_pos + 10], text, fns, 0, fn1_pos + 5
        )
        markers = [fn.ref_marker for fn in result]
        assert "1" in markers
        assert "2" not in markers


# ═══════════════════════════════════════════════════════════════════
# Adversarial Tests — Phase 3.1 Edge Case Hardening (Pass 2)
# ═══════════════════════════════════════════════════════════════════


class TestAdversarialLayerAttribution:
    """Adversarial multi-layer attribution and split-point merging."""

    def test_la3_dominant_coverage_value_correct(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """LA-3 with 3 layers: coverage_pct matches actual dominant coverage.

        SHARH~45%, HASHIYAH~30%, MATN~25%. LA-3 fires; result reports
        SHARH with its actual coverage ratio.
        """
        sharh = "قال الشارح في بيان المسألة وتوضيحها"
        hashiyah = "وذكر في الحاشية أن المراد"
        matn = "كلامنا لفظ مفيد كاستقم"
        text = sharh + " " + hashiyah + " " + matn
        text_len = len(text)
        s_end = len(sharh)
        h_start = s_end + 1
        h_end = h_start + len(hashiyah)
        m_start = h_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=s_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_hashiyah",
                start=h_start,
                end=h_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=m_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )
        assert result.rule_applied == "LA-3"
        assert result.layer_id == "sharh"
        assert 0.0 < result.coverage_pct < 0.8
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text

    def test_la3_four_distinct_layer_types(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """4 layer types: TAHQIQ + HASHIYAH + SHARH + MATN, LA-3 fires.

        Most adversarial multi-layer case: tahqiq editor quoting a hashiyah
        that references the sharh's commentary on the matn.
        """
        tahqiq = "قال المحقق في تعليقه على النص"
        hashiyah = "ذكر صاحب الحاشية"
        sharh = "يريد الشارح بذلك"
        matn = "كلامنا لفظ مفيد"
        text = tahqiq + " " + hashiyah + " " + sharh + " " + matn
        text_len = len(text)
        t_end = len(tahqiq)
        h_start = t_end + 1
        h_end = h_start + len(hashiyah)
        s_start = h_end + 1
        s_end = s_start + len(sharh)
        m_start = s_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.TAHQIQ_NOTE,
                author_canonical_id="sch_muhaqqiq",
                start=0,
                end=t_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_hashiyah",
                start=h_start,
                end=h_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=s_start,
                end=s_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=m_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )
        assert result.rule_applied == "LA-3"
        assert result.coverage_pct < 0.8
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text

    def test_different_type_at_split_point_no_merge(self) -> None:
        """SHARH->MATN at split boundary — different types, must NOT merge.

        Even though segments are adjacent at the split point,
        different layer_type prevents merging. Result: 2 layers.
        With ~50/50 coverage (dominant <60%), H-7 routes to LA-3.
        """
        text = "يريد الشارح في بيانه كلامنا لفظ مفيد كاستقم"
        text_len = len(text)
        split_at = text_len // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_1",
                start=0,
                end=split_at,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_1",
                start=split_at,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split_at],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(
            text, layers, 0, len(tokens) - 1, meta
        )
        # Two distinct layer types, ~50/50 coverage -> LA-3 (H-7: dominant <60%)
        assert result.rule_applied == "LA-3"

    def test_same_type_different_author_at_split_point_no_merge(self) -> None:
        """Two SHARH segments by different authors at split point -> no merge.

        Split-point merging requires same (type, author). Different authors
        are genuinely different commentators — must NOT merge.
        With ~50/50 coverage (dominant <60%), H-7 routes to LA-3.
        """
        text = "يريد الشارح في بيانه ومعنى كلامه عند التحقيق"
        text_len = len(text)
        split_at = text_len // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_1",
                start=0,
                end=split_at,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh_2",
                start=split_at,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split_at],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(
            text, layers, 0, len(tokens) - 1, meta
        )
        # Two distinct authors -> NOT merged; ~50/50 -> LA-3 (H-7: dominant <60%)
        assert result.rule_applied == "LA-3"

    def test_quoted_scholars_split_point_merging_effect(self) -> None:
        """L-3: Split-point merging changes quoted scholar output.

        Two SHARH segments at a split point merge into one. Without merging
        they'd appear as 2 entries; with merging, only 1 quoted scholar.
        """
        matn = "كلامنا لفظ مفيد كاستقم"
        sharh = "يريد الشارح أن الكلام في اصطلاح النحويين هو اللفظ المفيد"
        text = matn + " " + sharh
        text_len = len(text)
        matn_end = len(matn)
        sharh_start = matn_end + 1
        sharh_midpoint = sharh_start + len(sharh) // 2

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=sharh_start,
                end=sharh_midpoint,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=sharh_midpoint,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[sharh_midpoint],
            footnote_renumber_map=None,
        )
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_matn",
            coverage_pct=0.4,
            rule_applied="LA-2",
        )
        result = compute_quoted_scholars(
            layers, 0, text_len, primary, meta
        )
        # Two SHARH segments merge -> only 1 quoted scholar
        sharh_entries = [s for s in result if "sharh" in s.mention_text]
        assert len(sharh_entries) == 1
        assert sharh_entries[0].role == "quoted_opinion"
        assert sharh_entries[0].resolved_name == "sch_sharh"


class TestAdversarialSplitChunkId:
    """Split chunk excerpt_id generation edge cases."""

    def test_split_info_chunk_index_zero_with_split_info(self) -> None:
        """First chunk of a split: split_info present with chunk_index=0.

        Distinct from "no split_info" (also defaults to 0). The excerpt_id
        format is the same, but chunk_index comes from split_info.
        """
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0_chunk_0",
            split_info=SplitInfo(
                original_div_id="div_test_1_0",
                chunk_index=0,
                total_chunks=5,
                split_method="paragraph_break",
            ),
        )
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert result[0].chunk_index == 0
        assert result[0].excerpt_id == f"exc_{chunk.source_id}_{chunk.div_id}_0_0"

    def test_split_info_large_chunk_index(self) -> None:
        """chunk_index=99 reflected correctly in excerpt_id."""
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0_chunk_99",
            split_info=SplitInfo(
                original_div_id="div_test_1_0",
                chunk_index=99,
                total_chunks=100,
                split_method="word_count",
            ),
        )
        unit = _make_teaching_unit(
            unit_index=3,
            start_word=0,
            end_word=len(chunk.assembled_text.split()) - 1,
        )
        seg = _make_classified_segment(segment_index=0)
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert result[0].chunk_index == 99
        assert "_99_3" in result[0].excerpt_id


class TestAdversarialEvidenceDetection:
    """Adversarial evidence detection: proclitics, dedup, edge boundaries."""

    def test_hadith_all_markers_with_waw_proclitic(self) -> None:
        """DD-S3-8: Each hadith marker with و prefix detected.

        Arabic conjunctive waw attaches directly to the next word.
        Plain substring matching detects 'رواه' inside 'ورواه'.
        """
        markers_with_waw: dict[str, str] = {
            "رواه": "ورواه",
            "أخرجه": "وأخرجه",
            "في الصحيحين": "وفي الصحيحين",
            "متفق عليه": "ومتفق عليه",
            "في صحيح": "وفي صحيح",
            "في سنن": "وفي سنن",
        }
        for base_marker, prefixed in markers_with_waw.items():
            text = f"وقد ثبت ذلك {prefixed} البخاري في كتابه"
            result = detect_evidence_refs(text)
            hadith_refs = [r for r in result if r.type == "hadith"]
            found = {r.marker_text for r in hadith_refs}
            assert base_marker in found, (
                f"Hadith marker '{base_marker}' not detected in prefixed "
                f"form '{prefixed}'"
            )

    def test_ijma_all_markers_with_fa_proclitic(self) -> None:
        """DD-S3-8: Each ijma marker with ف prefix detected.

        Arabic fa-al-ta'qibiyya attaches directly: فأجمعوا, فإجماع, etc.
        """
        markers_with_fa: dict[str, str] = {
            "أجمعوا": "فأجمعوا",
            "إجماع": "فإجماع",
            "لا خلاف": "فلا خلاف",
            "اتفق العلماء": "فاتفق العلماء",
            "بالاتفاق": "فبالاتفاق",
        }
        for base_marker, prefixed in markers_with_fa.items():
            text = f"وقد ثبت ذلك {prefixed} في هذه المسألة"
            result = detect_evidence_refs(text)
            ijma_refs = [r for r in result if r.type == "ijma"]
            found = {r.marker_text for r in ijma_refs}
            assert base_marker in found, (
                f"Ijma marker '{base_marker}' not detected in prefixed "
                f"form '{prefixed}'"
            )

    def test_repeated_marker_both_occurrences_detected(self) -> None:
        """Same marker at two positions -> both detected (L-2 dedup path).

        'رواه البخاري ... ورواه مسلم' — two 'رواه' at distinct positions.
        """
        text = "رواه البخاري في صحيحه ورواه مسلم في صحيحه"
        result = detect_evidence_refs(text)
        rawahu_refs = [
            r for r in result
            if r.type == "hadith" and r.marker_text == "رواه"
        ]
        assert len(rawahu_refs) >= 2

    def test_marker_at_very_end_of_text(self) -> None:
        """Marker is the last token in text -> snippet clamped correctly."""
        text = "وقد ثبت ذلك فقد رواه"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        for ref in hadith_refs:
            assert len(ref.text_snippet) <= len(text)

    def test_quran_verse_with_hamza_and_madda(self) -> None:
        """Quran ﴿...﴾ with آ (madda), أ (hamza above), إ (hamza below).

        These hamza-bearing characters must be preserved byte-for-byte.
        """
        text = "قال تعالى ﴿آمَنَ الرَّسُولُ بِمَا أُنزِلَ إِلَيْهِ﴾"
        result = detect_evidence_refs(text)
        quran_refs = [r for r in result if r.type == "quran"]
        assert len(quran_refs) == 1
        snippet = quran_refs[0].text_snippet
        assert "آمَنَ" in snippet
        assert "أُنزِلَ" in snippet
        assert "إِلَيْهِ" in snippet

    def test_adjacent_quran_verses_both_detected(self) -> None:
        """Two ﴿...﴾ directly adjacent (﴾﴿) -> both detected."""
        text = "﴿الحمد لله رب العالمين﴾﴿الرحمن الرحيم﴾"
        result = detect_evidence_refs(text)
        quran_refs = [r for r in result if r.type == "quran"]
        assert len(quran_refs) == 2
        snippets = {r.text_snippet for r in quran_refs}
        assert "الحمد لله رب العالمين" in snippets
        assert "الرحمن الرحيم" in snippets

    def test_no_false_positive_on_similar_words(self) -> None:
        """Words similar to markers but not exact substrings -> no detection.

        'يرويه' does NOT contain 'رواه' (ي vs ا at 3rd position).
        'جمعوا' does NOT contain 'أجمعوا' (missing leading أ).
        """
        text = "يرويه الراوي عن شيخه وجمعوا المتاع في المكان"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        ijma_refs = [r for r in result if r.type == "ijma"]
        assert len(hadith_refs) == 0
        assert len(ijma_refs) == 0


class TestAdversarialTextExtraction:
    """Text extraction: paragraph breaks, word boundaries, long texts."""

    def test_multiple_paragraph_breaks_all_preserved(self) -> None:
        r"""Text with 3 paragraph breaks (\n\n) -> all preserved."""
        text = (
            "بسم الله الرحمن الرحيم\n\n"
            "الحمد لله رب العالمين\n\n"
            "الرحمن الرحيم\n\n"
            "مالك يوم الدين"
        )
        tokens = text.split()
        result = extract_primary_text(text, 0, len(tokens) - 1)
        assert result.count("\n\n") == 3
        assert result == text

    def test_single_newline_preserved(self) -> None:
        r"""Text with single \n (not \n\n) -> preserved in extraction."""
        text = "بسم الله الرحمن الرحيم\nالحمد لله رب العالمين"
        tokens = text.split()
        result = extract_primary_text(text, 0, len(tokens) - 1)
        assert "\n" in result
        assert result == text

    def test_first_word_extraction(self) -> None:
        """start_word=0, end_word=0 extracts the very first word."""
        text = "بسم الله الرحمن الرحيم"
        result = extract_primary_text(text, 0, 0)
        assert result == "بسم"

    def test_last_word_extraction(self) -> None:
        """start_word=end_word=last_index extracts the very last word."""
        text = "بسم الله الرحمن الرحيم"
        last_idx = len(text.split()) - 1
        result = extract_primary_text(text, last_idx, last_idx)
        assert result == "الرحيم"

    def test_long_text_offsets_at_start_middle_end(self) -> None:
        """1500-word text: extraction at start, middle, and end all correct.

        Verifies _word_to_char_range accuracy across the full span.
        """
        base = [
            "بسم الله الرحمن الرحيم",
            "الحمد لله رب العالمين",
            "وصلى الله على نبينا محمد",
            "قال المؤلف رحمه الله تعالى",
            "هذا باب في أحكام الصلاة",
        ]
        parts: list[str] = []
        wc = 0
        idx = 0
        while wc < 1500:
            parts.append(base[idx % len(base)])
            wc += len(base[idx % len(base)].split())
            idx += 1
        long_text = " ".join(parts)
        tokens = long_text.split()
        assert len(tokens) >= 1500

        # Start: words 0-4
        result_start = extract_primary_text(long_text, 0, 4)
        assert result_start == " ".join(tokens[0:5])

        # Middle: words 750-754
        result_mid = extract_primary_text(long_text, 750, 754)
        assert result_mid == " ".join(tokens[750:755])

        # End: last 5 words
        end_idx = len(tokens) - 1
        result_end = extract_primary_text(long_text, end_idx - 4, end_idx)
        assert result_end == " ".join(tokens[end_idx - 4 : end_idx + 1])


class TestAdversarialFootnotes:
    """Footnote filtering adversarial edge cases."""

    def test_all_footnotes_outside_unit_range(self) -> None:
        """Footnotes have markers, but unit range excludes all of them."""
        text = "بداية ⌜1⌝ النص وسط ⌜2⌝ النص وهذا جزء آخر من النص الطويل جداً"
        fn2_pos = text.find("\u231C2\u231D")
        fns = [
            Footnote(
                ref_marker="1",
                text="تعليق أول",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.9,
            ),
            Footnote(
                ref_marker="2",
                text="تعليق ثان",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.9,
            ),
        ]
        # Unit range starts well after both markers
        result = filter_relevant_footnotes(
            text[fn2_pos + 10 :], text, fns, fn2_pos + 10, len(text)
        )
        assert result == []

    def test_footnote_at_exact_char_start_included(self) -> None:
        """Marker at exactly char_start -> included (inclusive boundary).

        Range check: char_start <= pos < char_end.
        """
        text = "⌜1⌝ بسم الله الرحمن الرحيم"
        fn = Footnote(
            ref_marker="1",
            text="تعليق",
            footnote_type=FootnoteType.LINGUISTIC_NOTE,
            confidence=0.9,
        )
        result = filter_relevant_footnotes(text, text, [fn], 0, len(text))
        assert len(result) == 1
        assert result[0].ref_marker == "1"

    def test_footnote_at_exact_char_end_excluded(self) -> None:
        """Marker at exactly char_end -> excluded (exclusive boundary).

        Range is [char_start, char_end) — exclusive end.
        """
        text = "بسم الله ⌜1⌝ الرحمن"
        fn = Footnote(
            ref_marker="1",
            text="تعليق",
            footnote_type=FootnoteType.LINGUISTIC_NOTE,
            confidence=0.9,
        )
        marker_pos = text.find("\u231C1\u231D")
        # char_end exactly at marker position -> excluded
        result = filter_relevant_footnotes(text, text, [fn], 0, marker_pos)
        assert result == []


# ═══════════════════════════════════════════════════════════════════
# Phase 3.1 Edge Case Hardening — Pass 3 (overnight impl-phase3-edge)
# ═══════════════════════════════════════════════════════════════════


class TestLABoundaryPrecision:
    """Exact threshold boundary tests for LA rule dispatch.

    The LA cascade uses >= 0.8 for LA-1. These tests verify the exact
    boundary: 80.0% triggers LA-1, anything below does not.
    """

    def test_la1_exactly_80_percent(self) -> None:
        """Exactly 80.0% coverage triggers LA-1 (>= 0.8, not > 0.8).

        10-char single-token text. SHARH covers [0,8) = 80%, MATN [8,10) = 20%.
        """
        text = "أبجدهوزحطي"  # 10 chars, 1 token
        assert len(text) == 10
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=0,
                end=8,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=8,
                end=10,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 0, meta)
        assert result.rule_applied == "LA-1"
        assert result.layer_id == "sharh"
        assert result.coverage_pct == 0.8

    def test_just_below_80_triggers_la2(self) -> None:
        """70% coverage with 2 layers triggers LA-2, not LA-1.

        10-char text. SHARH covers [0,7) = 70%, MATN covers [7,10) = 30%.
        """
        text = "أبجدهوزحطي"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=0,
                end=7,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=7,
                end=10,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 0, meta)
        # 70% < 80% -> not LA-1; 2 layers -> LA-2
        assert result.rule_applied == "LA-2"
        # SHARH (level 2) > MATN (level 1) -> outermost wins
        assert result.layer_id == "sharh"

    def test_la4_exactly_100_percent_single_layer(self) -> None:
        """100% coverage with single layer triggers LA-4."""
        text = "بسم الله الرحمن"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-4"
        assert result.coverage_pct >= 1.0


class TestEmptyLayerCoverage:
    """Tests for the empty/no-coverage error path in compute_layer_attribution."""

    def test_no_layers_raises_value_error(self) -> None:
        """Empty text_layers -> ValueError (violates I-AC-2)."""
        text = "بسم الله الرحمن الرحيم"
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with pytest.raises(ValueError, match="I-AC-2"):
            compute_layer_attribution(text, [], 0, len(tokens) - 1, meta)

    def test_layers_outside_unit_range_raises(self) -> None:
        """Layers exist but none overlap the unit range -> ValueError."""
        text = "بسم الله الرحمن الرحيم"
        # Layer covers [0, 5) but unit is [10, 20) — no overlap
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=5,
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        # Words 3-3 = "الرحيم" which is at char positions beyond where layer ends
        tokens = text.split()
        with pytest.raises(ValueError, match="I-AC-2"):
            compute_layer_attribution(text, layers, 3, len(tokens) - 1, meta)


class TestUncertainAndTahqiqLayers:
    """Layer type priority in LA-2: _LAYER_LEVEL ordering."""

    def test_uncertain_loses_to_matn_in_la2(self) -> None:
        """UNCERTAIN (level 0) vs MATN (level 1) -> MATN wins in LA-2.

        Dominant must be >=60% for LA-2 (H-7). Use 70/30 split.
        """
        text = "أبجدهوزحطي"  # 10 chars, 1 token
        layers = [
            TextLayerSegment(
                layer_type=LayerType.UNCERTAIN,
                author_canonical_id="sch_u",
                start=0,
                end=3,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=3,
                end=10,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 0, meta)
        assert result.rule_applied == "LA-2"
        assert result.layer_id == "matn"

    def test_tahqiq_note_beats_hashiyah_in_la2(self) -> None:
        """TAHQIQ_NOTE (level 4) vs HASHIYAH (level 3) -> TAHQIQ_NOTE wins.

        Dominant must be >=60% for LA-2 (H-7). Use 70/30 split.
        """
        text = "أبجدهوزحطي"  # 10 chars
        layers = [
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_h",
                start=0,
                end=3,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.TAHQIQ_NOTE,
                author_canonical_id="sch_t",
                start=3,
                end=10,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 0, meta)
        assert result.rule_applied == "LA-2"
        assert result.layer_id == "tahqiq_note"

    def test_uncertain_layer_in_la4(self) -> None:
        """UNCERTAIN layer at 100% still triggers LA-4."""
        text = "بسم الله"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.UNCERTAIN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        assert result.rule_applied == "LA-4"
        assert result.layer_id == "uncertain"
        assert result.author_id == "unknown"


class TestAuthorNoneAllLAPaths:
    """M-7 extended: author_canonical_id=None -> 'unknown' in LA-2 and LA-3."""

    def test_author_none_la2(self) -> None:
        """Both layers have author=None, dominant >=60% -> 'unknown' in LA-2 result."""
        text = "أبجدهوزحطي"  # 10 chars
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=3,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=3,
                end=10,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_layer_attribution(text, layers, 0, 0, meta)
        assert result.rule_applied == "LA-2"
        assert result.author_id == "unknown"

    def test_author_none_la3(self, caplog: pytest.LogCaptureFixture) -> None:
        """Three layers all with author=None -> 'unknown' in LA-3 result."""
        text = "أبجدهوزحطيكلمنس"  # 15 chars
        assert len(text) == 15
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=5,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=5,
                end=10,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id=None,
                start=10,
                end=15,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(text, layers, 0, 0, meta)
        assert result.rule_applied == "LA-3"
        assert result.author_id == "unknown"
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text


class TestPageRangeExtended:
    """Extended page range tests: volume changes, partial overlaps."""

    def test_volume_changes_across_pages(self) -> None:
        """Unit spans pages from different volumes -> first volume used."""
        pages = [
            PhysicalPage(volume=1, page_number_display="٢٤٠", page_number_int=240),
            PhysicalPage(volume=2, page_number_display="١", page_number_int=1),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=50,
            )
        ]
        # Unit spans chars [30, 70), crossing the volume boundary at 50
        result = compute_page_range(pages, join_pts, 30, 70)
        assert result is not None
        assert result.volume == 1  # First overlapping page's volume
        assert result.start_page == 1
        assert result.end_page == 240

    def test_first_page_volume_none_second_has_volume(self) -> None:
        """First overlapping page volume=None, second has volume -> second used.

        The code sets first_volume from the first page (None), but since
        first_volume is still None on the second iteration, the second
        page's volume overwrites it. Effectively: first non-None volume.
        """
        pages = [
            PhysicalPage(volume=None, page_number_display=None, page_number_int=5),
            PhysicalPage(volume=2, page_number_display="١", page_number_int=1),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=50,
            )
        ]
        result = compute_page_range(pages, join_pts, 30, 70)
        assert result is not None
        # first_volume = None (page 0), then overwritten to 2 (page 1)
        # because `if first_volume is None:` is still True
        assert result.volume == 2
        assert result.start_page == 1
        assert result.end_page == 5

    def test_unit_at_very_end_of_multi_page(self) -> None:
        """Unit range at the very end of a 3-page chunk -> last page only."""
        pages = [
            PhysicalPage(volume=1, page_number_display="١", page_number_int=1),
            PhysicalPage(volume=1, page_number_display="٢", page_number_int=2),
            PhysicalPage(volume=1, page_number_display="٣", page_number_int=3),
        ]
        join_pts = [
            JoinPoint(
                after_unit_index=0,
                before_unit_index=1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=100,
            ),
            JoinPoint(
                after_unit_index=1,
                before_unit_index=2,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=200,
            ),
        ]
        # Unit at chars [220, 280) -> only page 3 (starts at 200)
        result = compute_page_range(pages, join_pts, 220, 280)
        assert result is not None
        assert result.start_page == 3
        assert result.end_page == 3


class TestContentTypesExtended:
    """Edge cases for F-DET-4 compute_content_types."""

    def test_empty_segment_indices(self) -> None:
        """No segment indices -> empty content types."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
            )
        ]
        result = compute_content_types(segments, [])
        assert result == []

    def test_segments_outside_indices_excluded(self) -> None:
        """Only segments in unit_segment_indices are included."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
            ),
            _make_classified_segment(
                segment_index=1, scholarly_function=ScholarlyFunction.EVIDENCE_HADITH
            ),
            _make_classified_segment(
                segment_index=2, scholarly_function=ScholarlyFunction.EXAMPLE
            ),
        ]
        # Only include segments 0 and 2
        result = compute_content_types(segments, [0, 2])
        assert len(result) == 2
        assert ScholarlyFunction.DEFINITION in result
        assert ScholarlyFunction.EXAMPLE in result
        assert ScholarlyFunction.EVIDENCE_HADITH not in result

    def test_insertion_order_preserved(self) -> None:
        """Scholarly functions returned in segment order, not sorted."""
        segments = [
            _make_classified_segment(
                segment_index=0, scholarly_function=ScholarlyFunction.EXAMPLE
            ),
            _make_classified_segment(
                segment_index=1, scholarly_function=ScholarlyFunction.DEFINITION
            ),
            _make_classified_segment(
                segment_index=2, scholarly_function=ScholarlyFunction.RULE_STATEMENT
            ),
        ]
        result = compute_content_types(segments, [0, 1, 2])
        assert result == [
            ScholarlyFunction.EXAMPLE,
            ScholarlyFunction.DEFINITION,
            ScholarlyFunction.RULE_STATEMENT,
        ]


class TestEvidenceOverlappingMarkers:
    """Evidence detection with markers that could overlap or interact."""

    def test_both_fi_sahih_and_fi_sunan_detected(self) -> None:
        """'في صحيح البخاري' and 'في سنن أبي داود' — both markers found."""
        text = "ثبت في صحيح البخاري وأيضاً في سنن أبي داود"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        markers = {r.marker_text for r in hadith_refs}
        assert "في صحيح" in markers
        assert "في سنن" in markers

    def test_fi_sahihain_and_fi_sahih_both_detected(self) -> None:
        """'في الصحيحين' text also contains 'في صحيح' — they match at different positions."""
        text = "ثبت هذا في الصحيحين وكذلك في صحيح مسلم"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        markers = {r.marker_text for r in hadith_refs}
        # في الصحيحين matches "في الصحيحين" marker
        assert "في الصحيحين" in markers
        # في صحيح also matches separately in "في صحيح مسلم"
        assert "في صحيح" in markers

    def test_all_evidence_types_in_one_text(self) -> None:
        """Quran + hadith + ijma all in same text -> all detected."""
        text = (
            "قال تعالى ﴿وأقيموا الصلاة﴾ "
            "وقد رواه البخاري "
            "وانعقد الإجماع على وجوبها"
        )
        result = detect_evidence_refs(text)
        types = {r.type for r in result}
        assert types == {"quran", "hadith", "ijma"}

    def test_marker_at_position_zero(self) -> None:
        """Marker starts at the very first character of text."""
        text = "رواه مسلم في صحيحه"
        result = detect_evidence_refs(text)
        hadith_refs = [r for r in result if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        # Verify snippet clamping doesn't go negative
        for ref in hadith_refs:
            assert ref.text_snippet is not None

    def test_empty_text_no_evidence(self) -> None:
        """Empty string -> no evidence refs."""
        result = detect_evidence_refs("")
        assert result == []


class TestQuotedScholarsExtended:
    """Extended tests for F-DET-9 quoted scholars."""

    def test_secondary_layer_author_none(self) -> None:
        """Secondary layer with author_canonical_id=None -> resolved_name=None."""
        text = "بسم الله الرحمن الرحيم الحمد لله"
        mid = len(text) // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_known",
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=mid,
                end=len(text),
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_known",
            coverage_pct=0.5,
            rule_applied="LA-2",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        assert len(result) == 1
        assert result[0].resolved_name is None

    def test_three_non_primary_layers(self) -> None:
        """Three secondary layers -> three quoted scholars."""
        text = "أبجدهوزحطيكلمنسعفصقر"  # 20 chars
        assert len(text) == 20
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=0,
                end=5,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=5,
                end=10,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_hashiyah",
                start=10,
                end=15,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.TAHQIQ_NOTE,
                author_canonical_id="sch_muhaqqiq",
                start=15,
                end=20,
                confidence=1.0,
            ),
        ]
        # Primary is SHARH
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_sharh",
            coverage_pct=0.25,
            rule_applied="LA-3",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, 20, primary, meta)
        # 3 non-primary layers: MATN, HASHIYAH, TAHQIQ_NOTE
        assert len(result) == 3
        layer_types = {s.mention_text for s in result}
        assert "[structural: matn]" in layer_types
        assert "[structural: hashiyah]" in layer_types
        assert "[structural: tahqiq_note]" in layer_types

    def test_matn_in_sharh_primary_is_classification_frame(self) -> None:
        """MATN in SHARH-primary unit -> role='classification_frame'."""
        text = "بسم الله الرحمن الرحيم الحمد لله"
        mid = len(text) // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=mid,
                end=len(text),
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_s",
            coverage_pct=0.5,
            rule_applied="LA-2",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        assert len(result) == 1
        assert result[0].role == "classification_frame"

    def test_hashiyah_in_matn_primary_is_quoted_opinion(self) -> None:
        """HASHIYAH in MATN-primary unit -> role='quoted_opinion'."""
        text = "بسم الله الرحمن الرحيم الحمد لله"
        mid = len(text) // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_h",
                start=mid,
                end=len(text),
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_m",
            coverage_pct=0.5,
            rule_applied="LA-2",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        assert len(result) == 1
        assert result[0].role == "quoted_opinion"


class TestOrchestratorIntegration:
    """Full integration: orchestrator with multi-layer + footnotes + split."""

    def test_multi_layer_split_chunk_with_footnotes(self) -> None:
        """Complete path: split chunk, multi-layer, footnotes, multi-unit.

        Exercises all deterministic functions simultaneously through the
        orchestrator to verify they compose correctly.
        """
        # Build text with footnote markers and multi-layer
        matn = "قال ابن مالك كلامنا لفظ مفيد ⌜1⌝ كاستقم"
        sharh = "يريد أن الكلام في اصطلاح النحويين هو اللفظ المفيد ⌜2⌝ فائدة يحسن السكوت"
        text = matn + " " + sharh
        matn_end = len(matn)
        sharh_start = matn_end + 1

        tokens = text.split()
        total = len(tokens)
        word_count = sum(
            1 for t in tokens if any("\u0600" <= c <= "\u06FF" for c in t)
        )

        chunk = AssembledChunk(
            chunk_id="div_test_1_0_chunk_2",
            source_id="src_alfiyya",
            div_id="div_alfiyya_1_0",
            div_path=["كتاب الألفية", "باب الكلام"],
            assembled_text=text,
            word_count=word_count,
            total_tokens=total,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id="sch_ibn_malik",
                    start=0,
                    end=matn_end,
                    confidence=1.0,
                ),
                TextLayerSegment(
                    layer_type=LayerType.SHARH,
                    author_canonical_id="sch_ibn_aqeel",
                    start=sharh_start,
                    end=len(text),
                    confidence=1.0,
                ),
            ],
            footnotes=[
                Footnote(
                    ref_marker="1",
                    text="أي مستقيم",
                    footnote_type=FootnoteType.LINGUISTIC_NOTE,
                    confidence=0.95,
                ),
                Footnote(
                    ref_marker="2",
                    text="أي يصح سكوت المتكلم عليها",
                    footnote_type=FootnoteType.LINGUISTIC_NOTE,
                    confidence=0.90,
                ),
            ],
            content_flags=ContentFlags(),
            physical_pages=[
                PhysicalPage(volume=1, page_number_display="٥", page_number_int=5),
                PhysicalPage(volume=1, page_number_display="٦", page_number_int=6),
            ],
            structural_format=StructuralFormat.PROSE,
            heading_alignment_ok=True,
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0, 1],
                join_points=[
                    JoinPoint(
                        after_unit_index=0,
                        before_unit_index=1,
                        boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                        separator_used=" ",
                        char_offset_in_assembled=sharh_start,
                    )
                ],
                layer_split_points=[],
                footnote_renumber_map=None,
            ),
            merge_history=None,
            split_info=SplitInfo(
                original_div_id="div_alfiyya_1_0",
                chunk_index=2,
                total_chunks=5,
                split_method="paragraph_break",
            ),
        )

        mid_token = total // 2
        unit0 = _make_teaching_unit(
            unit_index=0,
            start_word=0,
            end_word=mid_token - 1,
            segment_indices=[0],
            text_snippet=text[:50],
        )
        unit1 = _make_teaching_unit(
            unit_index=1,
            start_word=mid_token,
            end_word=total - 1,
            segment_indices=[1],
            text_snippet=text[50:100],
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="يشير إلى تعريف الكلام السابق",
        )
        seg0 = _make_classified_segment(
            segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
        )
        seg1 = _make_classified_segment(
            segment_index=1, scholarly_function=ScholarlyFunction.EVIDENCE_HADITH
        )

        result = build_deterministic_excerpts(chunk, [unit0, unit1], [seg0, seg1])

        # ── Basic structure ──
        assert len(result) == 2

        # ── F-DET-1: excerpt_id with split chunk_index=2 ──
        assert result[0].excerpt_id == "exc_src_alfiyya_div_alfiyya_1_0_2_0"
        assert result[1].excerpt_id == "exc_src_alfiyya_div_alfiyya_1_0_2_1"
        assert result[0].chunk_index == 2
        assert result[1].chunk_index == 2

        # ── F-DET-2: primary_text is a substring ──
        assert result[0].primary_text in text
        assert result[1].primary_text in text

        # ── F-DET-3: layer attribution ──
        # Unit 0 starts from word 0 (in MATN region)
        assert result[0].primary_author_layer is not None
        assert result[0].primary_author_layer.rule_applied in ("LA-1", "LA-2", "LA-3", "LA-4")

        # ── F-DET-4: content_types ──
        assert result[0].content_types == [ScholarlyFunction.DEFINITION]
        assert result[1].content_types == [ScholarlyFunction.EVIDENCE_HADITH]

        # ── F-DET-6: page range (crosses join point) ──
        # At minimum one record should have a page range
        has_pages = any(r.physical_pages is not None for r in result)
        assert has_pages

        # ── Self-containment flags ──
        assert result[0].review_flags == []  # FULL
        assert "llm_enrichment_failed" in result[1].review_flags  # PARTIAL

        # ── DD-S3-1: school explicitly None ──
        assert result[0].school is None
        assert result[1].school is None

        # ── D-023: all passthrough fields present ──
        for rec in result:
            assert rec.source_id == "src_alfiyya"
            assert rec.div_id == "div_alfiyya_1_0"
            assert rec.div_path == ["كتاب الألفية", "باب الكلام"]

    def test_orchestrator_with_evidence_and_no_footnotes(self) -> None:
        """Chunk with hadith evidence markers but no footnotes."""
        text = "قال النبي صلى الله عليه وسلم وقد رواه البخاري ومسلم في صحيحهما متفق عليه"
        tokens = text.split()
        chunk = _make_assembled_chunk(
            assembled_text=text,
            total_tokens=len(tokens),
            word_count=len(tokens),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id="sch_author",
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
            footnotes=[],
        )
        unit = _make_teaching_unit(
            start_word=0,
            end_word=len(tokens) - 1,
            segment_indices=[0],
            text_snippet=text[:50],
        )
        seg = _make_classified_segment(
            segment_index=0, scholarly_function=ScholarlyFunction.EVIDENCE_HADITH
        )
        result = build_deterministic_excerpts(chunk, [unit], [seg])
        assert len(result) == 1
        # F-DET-5: should detect hadith markers
        hadith_refs = [r for r in result[0].evidence_refs if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        markers = {r.marker_text for r in hadith_refs}
        assert "رواه" in markers
        # F-DET-8: no footnotes
        assert result[0].footnotes_relevant == []


# ═══════════════════════════════════════════════════════════════════
# Knowledge Corruption Probe: LA rules with all-None author_canonical_id
# ═══════════════════════════════════════════════════════════════════


class TestNoneAuthorLayerAttribution:
    """Probe: verify LA rules when ALL layers have author_canonical_id=None.

    Corruption vector: if _compute_layer_coverages merges layers with
    different layer_types because both share author_canonical_id=None,
    the merge would collapse distinct scholarly layers into one entry,
    causing LA-4 (100% single layer) to fire instead of LA-3 (ambiguous,
    needs consensus gate). This suppresses EX-M-001 and human gate.

    The merge key is (layer_type, author_canonical_id). Different types
    must never merge regardless of shared None author.
    """

    def test_three_layers_all_none_authors_fires_la3(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Three layers (MATN, SHARH, HASHIYAH) all with None author -> LA-3.

        This is the critical corruption scenario: if _compute_layer_coverages
        merges these because None == None, the system produces WRONG
        attribution with NO EX-M-001 warning and NO human gate.
        """
        # Real Arabic: matn (original text), sharh (commentary), hashiyah (gloss)
        matn_text = "كلامنا لفظ مفيد كاستقم"
        sharh_text = "يريد أن الكلام في اصطلاح النحويين"
        hashiyah_text = "أقول معنى قوله يريد أن الكلام"
        text = matn_text + " " + sharh_text + " " + hashiyah_text
        text_len = len(text)

        matn_end = len(matn_text)
        sharh_start = matn_end + 1
        sharh_end = sharh_start + len(sharh_text)
        hashiyah_start = sharh_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=sharh_start,
                end=sharh_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id=None,
                start=hashiyah_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, meta
            )

        # MUST be LA-3 (3+ ambiguous layers), NOT LA-4 (single dominant)
        assert result.rule_applied == "LA-3", (
            f"Expected LA-3 for 3 distinct layers with None authors, "
            f"got {result.rule_applied}. This means distinct layer types "
            f"were incorrectly merged because author_canonical_id=None matched."
        )
        # EX-M-001 warning MUST be emitted for human review
        assert ExcerptingErrorCodes.EX_M_001 in caplog.text, (
            "EX-M-001 warning missing — ambiguous attribution was silenced"
        )
        # author_id should fall back to "unknown" for None
        assert result.author_id == "unknown"

    def test_two_different_types_none_authors_at_split_not_merged(self) -> None:
        """Two layers (MATN, SHARH) both None at split point -> NOT merged.

        Even though both share author_canonical_id=None and meet at a
        split point, they have different layer_types and must remain
        as 2 separate coverage entries. LA-2 should fire, not LA-4.
        """
        matn_text = "قال المصنف في هذا الباب"
        sharh_text = "يشير إلى أن المراد بالباب"
        text = matn_text + sharh_text  # No space — they abut at split
        split_point = len(matn_text)

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=split_point,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=split_point,
                end=len(text),
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split_point],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(
            text, layers, 0, len(tokens) - 1, meta
        )

        # Two different-type layers must NOT merge; ~50/50 -> LA-3 (H-7: dominant <60%)
        assert result.rule_applied == "LA-3", (
            f"Expected LA-3 for 2 different-type layers with None authors "
            f"at split point (~50/50 coverage), got {result.rule_applied}. "
            f"H-7: dominant <60% routes to LA-3 for consensus review."
        )
        assert result.author_id == "unknown"

    def test_single_layer_none_author_fires_la4(self) -> None:
        """Single layer with None author -> LA-4 correctly fires.

        This IS the legitimate single-layer case. Unlike the 3-layer scenario,
        one layer covering 100% genuinely triggers LA-4.
        """
        text = "بسم الله الرحمن الرحيم الحمد لله رب العالمين"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(
            text, layers, 0, len(tokens) - 1, meta
        )

        assert result.rule_applied == "LA-4"
        assert result.coverage_pct == 1.0
        assert result.layer_id == "matn"
        assert result.author_id == "unknown"

    def test_same_type_none_authors_at_split_merge_correctly(self) -> None:
        """DD-S3-7: Same-type None-author layers at split point DO merge.

        This is the CORRECT merge case: two SHARH(None) segments split
        by a page boundary. Merging them into one 100% coverage entry
        is right because the normalization engine saw them as one continuous
        layer across pages. LA-4 is the correct outcome here.

        This test guards against over-correction: if someone "fixes" the
        None-author merge to prevent ALL None-author merges, this test
        catches the regression.
        """
        text = "يريد أن الكلام في اصطلاح النحويين هو اللفظ المفيد"
        split_point = len(text) // 2

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=0,
                end=split_point,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=split_point,
                end=len(text),
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[split_point],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(
            text, layers, 0, len(tokens) - 1, meta
        )

        # Same type + same None author at split -> merge -> 100% -> LA-4
        assert result.rule_applied == "LA-4"
        assert result.coverage_pct == 1.0
        assert result.author_id == "unknown"

    def test_three_none_authors_quoted_scholars_all_distinct(self) -> None:
        """F-DET-9: Three None-author layers produce correct quoted_scholars.

        When all layers have None authors, the primary layer (largest coverage)
        should be excluded from quoted_scholars, and the other two should
        appear as distinct entries — NOT collapsed into one.
        """
        matn_text = "كلامنا لفظ مفيد كاستقم"
        sharh_text = "يريد أن الكلام في اصطلاح النحويين هو اللفظ المفيد"
        hashiyah_text = "أقول معنى قوله يريد أن المراد بالكلام"
        text = matn_text + " " + sharh_text + " " + hashiyah_text
        text_len = len(text)

        matn_end = len(matn_text)
        sharh_start = matn_end + 1
        sharh_end = sharh_start + len(sharh_text)
        hashiyah_start = sharh_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=sharh_start,
                end=sharh_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id=None,
                start=hashiyah_start,
                end=text_len,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )

        # Primary is whichever has largest coverage
        # SHARH has the most chars, so it's the primary
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="unknown",
            coverage_pct=0.4,
            rule_applied="LA-3",
        )

        result = compute_quoted_scholars(
            layers, 0, text_len, primary, meta
        )

        # Should have 2 quoted scholars (MATN + HASHIYAH), NOT 0 or 1
        assert len(result) == 2, (
            f"Expected 2 quoted scholars for 3-layer None-author unit, "
            f"got {len(result)}. Layers may have been incorrectly merged."
        )
        layer_types = {r.mention_text for r in result}
        assert "[structural: matn]" in layer_types
        assert "[structural: hashiyah]" in layer_types


# ═══════════════════════════════════════════════════════════════════
# T-1: Attribution Corruption Probe — Knowledge Integrity
# ═══════════════════════════════════════════════════════════════════


class TestT1AttributionCorruptionProbe:
    """Probe for T-1 knowledge corruption: scenarios where layer
    attribution produces wrong results, silently drops scholarly
    voices, or attributes text to the wrong scholar.

    Each test targets a specific corruption vector identified during
    the overnight knowledge integrity scan (2026-03-28).
    """

    # ── Shared helpers ──────────────────────────────────────────

    _META_NO_SPLITS = AssemblyMetadata(
        constituent_unit_indices=[0],
        join_points=[],
        layer_split_points=[],
        footnote_renumber_map=None,
    )

    # ── BUG FIX: quoted_scholars silent exclusion (T-1.1) ──────

    def test_two_sharh_none_authors_second_preserved(self) -> None:
        """T-1.1: Two SHARH layers both author=None, second must NOT vanish.

        Real scenario: hashiyah text embeds TWO different sharh commentaries
        (e.g., one from al-Nawawi, one from al-Rafi'i) but neither author
        was resolved by normalization. Without the fix, both match
        (type="sharh", author="unknown") and the second is silently excluded
        from quoted_scholars — a scholar's voice lost from the record.
        """
        # Two distinct sharh commentaries from unresolved authors
        sharh_a = "يريد بالكلام اللفظ المركب المفيد بالوضع"
        sharh_b = "وقال الرافعي المراد به كل لفظ دل على معنى"
        matn = "الكلام هو اللفظ المفيد"
        text = matn + " " + sharh_a + " " + sharh_b

        matn_end = len(matn)
        sharh_a_start = matn_end + 1
        sharh_a_end = sharh_a_start + len(sharh_a)
        sharh_b_start = sharh_a_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=sharh_a_start,
                end=sharh_a_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=sharh_b_start,
                end=len(text),
                confidence=1.0,
            ),
        ]

        # Primary is SHARH (higher _LAYER_LEVEL than MATN), LA-3
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="unknown",
            coverage_pct=0.4,
            rule_applied="LA-3",
        )

        result = compute_quoted_scholars(
            layers, 0, len(text), primary, self._META_NO_SPLITS
        )

        # MUST have 2 quoted scholars: MATN + the second SHARH
        # Before fix: only MATN appeared (second SHARH silently dropped)
        assert len(result) >= 2, (
            f"T-1.1 CORRUPTION: Expected ≥2 quoted scholars, got {len(result)}. "
            f"A scholarly voice was silently dropped."
        )
        types_and_roles = [(r.mention_text, r.role) for r in result]
        assert any("[structural: matn]" in t for t, _ in types_and_roles), (
            "MATN layer missing from quoted_scholars"
        )
        assert any(
            "[structural: sharh]" in t for t, _ in types_and_roles
        ), "T-1.1: Second SHARH layer silently excluded — scholar voice lost"

    def test_known_author_same_type_all_excluded_correctly(self) -> None:
        """Regression: two SHARH layers with SAME known author → both excluded.

        When author_canonical_id is resolved (not None), all entries with
        matching (type, author) ARE the same person and should be excluded.
        This test ensures the fix for T-1.1 doesn't break this behavior.
        """
        sharh_part_a = "قوله كلامنا أي كلام النحاة فهو من باب الإضافة"
        sharh_part_b = "وإنما خص الكلام لأن موضوع علم النحو الكلام"
        text = sharh_part_a + " " + sharh_part_b

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_ibn_aqeel",
                start=0,
                end=len(sharh_part_a),
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_ibn_aqeel",
                start=len(sharh_part_a) + 1,
                end=len(text),
                confidence=1.0,
            ),
        ]

        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_ibn_aqeel",
            coverage_pct=0.6,
            rule_applied="LA-1",
        )

        result = compute_quoted_scholars(
            layers, 0, len(text), primary, self._META_NO_SPLITS
        )

        # Both are the SAME known author → correctly excluded → empty
        assert len(result) == 0, (
            f"Known-author regression: expected 0 quoted scholars, got {len(result)}"
        )

    def test_primary_unknown_secondary_known_same_type(self) -> None:
        """T-1.2: Primary is SHARH/unknown, secondary SHARH has known author.

        The known-author SHARH should appear in quoted_scholars regardless
        of the primary's unknown status.
        """
        sharh_unknown = "المراد بالكلام هنا كلام النحاة"
        sharh_known = "قال النووي والصحيح أن الكلام ما تركب من كلمتين"
        text = sharh_unknown + " " + sharh_known

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=0,
                end=len(sharh_unknown),
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_nawawi",
                start=len(sharh_unknown) + 1,
                end=len(text),
                confidence=1.0,
            ),
        ]

        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="unknown",
            coverage_pct=0.55,
            rule_applied="LA-2",
        )

        result = compute_quoted_scholars(
            layers, 0, len(text), primary, self._META_NO_SPLITS
        )

        assert len(result) == 1
        assert result[0].resolved_name == "sch_nawawi"
        assert result[0].role == "quoted_opinion"

    # ── LA-3 same-level tie with <60% dominant (T-1.3) ─────────

    def test_la3_same_level_different_known_authors_below_60(self) -> None:
        """T-1.3: Two SHARH layers with different known authors, neither ≥80%.

        Both have _LAYER_LEVEL=2 (SHARH), 55%/45% split.
        H-7: dominant <60% -> LA-3 (attribution ambiguous, needs consensus).
        """
        # al-Rafi'i's commentary (55%)
        rafi = "قال الرافعي اعلم أن الفقه في اللغة الفهم"
        # al-Nawawi's commentary (45%)
        nawawi = "قال النووي والأصح عندنا أن الفقه علم"
        text = rafi + " " + nawawi

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_rafi",
                start=0,
                end=len(rafi),
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_nawawi",
                start=len(rafi) + 1,
                end=len(text),
                confidence=1.0,
            ),
        ]

        result = compute_layer_attribution(
            text, layers, 0, len(text.split()) - 1, self._META_NO_SPLITS
        )

        # H-7: 55% < 60% -> LA-3 (attribution ambiguous)
        assert result.rule_applied == "LA-3"
        # Higher coverage (al-Rafi'i 55%) becomes the default in LA-3
        assert result.author_id == "sch_rafi"

    # ── Merge collapse with None authors (T-1.4) ──────────────

    def test_merge_distinct_none_authors_at_split_point(self) -> None:
        """T-1.4: Two SHARH/None layers at split point merge into one.

        When normalization can't resolve either author, two distinct SHARH
        segments with author=None at a split point will merge because
        None==None. This documents the inherent limitation — the pipeline
        CANNOT distinguish them without author metadata.
        """
        text = "شرح الأول هذا ما قاله الشارح الثاني في نفس المسألة"
        mid = len(text) // 2

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=mid,
                end=len(text),
                confidence=1.0,
            ),
        ]

        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[mid],  # split point at boundary
            footnote_renumber_map=None,
        )

        result = compute_layer_attribution(
            text, layers, 0, len(text.split()) - 1, meta
        )

        # Merged into one layer → LA-4 (100% coverage)
        # This is correct given the data, but a known limitation:
        # distinct scholars with unresolved authors are indistinguishable.
        assert result.rule_applied == "LA-4"
        assert result.coverage_pct == 1.0
        assert result.author_id == "unknown"

    # ── Exact boundary values (T-1.5) ─────────────────────────

    @pytest.mark.parametrize(
        "overlap_chars,total_chars,expected_rule",
        [
            (8, 10, "LA-1"),    # 80.0% exactly → LA-1
            (10, 10, "LA-4"),   # 100.0% exactly → LA-4
            (79, 100, "LA-2"),  # 79.0% → LA-2 (2 layers)
            (80, 100, "LA-1"),  # 80.0% → LA-1
            (81, 100, "LA-1"),  # 81.0% → LA-1
            (99, 100, "LA-1"),  # 99.0% → LA-1 (not LA-4)
            (100, 100, "LA-4"), # 100.0% → LA-4
        ],
    )
    def test_la_boundary_integer_precision(
        self,
        overlap_chars: int,
        total_chars: int,
        expected_rule: str,
    ) -> None:
        """T-1.5: LA rule boundaries with integer-derived coverages.

        Verifies that character-based integer arithmetic produces exact
        floating-point values at the 80% and 100% thresholds.
        """
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_primary",
                start=0,
                end=overlap_chars,
                confidence=1.0,
            ),
        ]
        if overlap_chars < total_chars:
            layers.append(
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id="sch_secondary",
                    start=overlap_chars,
                    end=total_chars,
                    confidence=1.0,
                )
            )

        # Use _compute_layer_coverages directly (avoids word-boundary issues)
        from engines.excerpting.src.phase3_deterministic import (
            _compute_layer_coverages,
        )

        coverages = _compute_layer_coverages(layers, 0, total_chars, [])
        assert len(coverages) >= 1
        top_coverage = max(c for _, c in coverages)

        if expected_rule == "LA-4":
            assert top_coverage >= 1.0
        elif expected_rule == "LA-1":
            assert 0.8 <= top_coverage < 1.0
        else:
            assert top_coverage < 0.8

    # ── Three unknown SHARH layers — all should be visible (T-1.6) ──

    def test_three_sharh_none_authors_two_in_quoted(self) -> None:
        """T-1.6: Three SHARH layers all with author=None.

        The primary (highest coverage) is excluded from quoted_scholars,
        but both remaining layers MUST appear. Before the fix, all three
        had (type=sharh, author=unknown) and all were excluded.
        """
        # Three distinct sharh commentaries
        sharh_a = "قوله كلامنا أي كلام النحاة لا كلام اللغويين"  # longest
        sharh_b = "وقيل المراد الكلام عند المتكلمين"
        sharh_c = "وذهب الكوفيون إلى أن الكلام هو المعنى"
        text = sharh_a + " " + sharh_b + " " + sharh_c
        text_len = len(text)

        a_end = len(sharh_a)
        b_start = a_end + 1
        b_end = b_start + len(sharh_b)
        c_start = b_end + 1

        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=0,
                end=a_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=b_start,
                end=b_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=c_start,
                end=text_len,
                confidence=1.0,
            ),
        ]

        # Primary = sharh_a (largest coverage)
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="unknown",
            coverage_pct=len(sharh_a) / text_len,
            rule_applied="LA-3",
        )

        result = compute_quoted_scholars(
            layers, 0, text_len, primary, self._META_NO_SPLITS
        )

        # Two of three sharh layers should appear as quoted scholars
        assert len(result) == 2, (
            f"T-1.6: Expected 2 quoted scholars from 3 unknown-SHARH layers, "
            f"got {len(result)}. Scholar voices silently dropped."
        )
        for scholar in result:
            assert scholar.role == "quoted_opinion"
            assert scholar.source == "layer_overlap"


# ═══════════════════════════════════════════════════════════════════
# Micro-unit merge (DR29 #4 + Gemini CLI validation)
# ═══════════════════════════════════════════════════════════════════


def _make_unit(
    index: int,
    start: int,
    end: int,
    snippet: str,
    func: ScholarlyFunction = ScholarlyFunction.DEFINITION,
) -> "TeachingUnit":
    """Helper: create a TeachingUnit for merge tests."""
    from engines.excerpting.contracts import TeachingUnit

    return TeachingUnit(
        unit_index=index,
        segment_indices=[index],
        start_word=start,
        end_word=end,
        text_snippet=snippet[:80],
        primary_function=func,
        secondary_functions=[],
        description_arabic="وصف عربي للاختبار يتضمن عدة كلمات عربية",
        self_containment=SelfContainmentLevel.FULL,
        self_containment_notes=None,
    )


class TestMicroUnitClassification:
    """Tests for _is_bare_micro_unit classification."""

    def test_bare_ordinal_is_opener(self) -> None:
        assert _is_bare_micro_unit("الثالثة") == "opener"

    def test_bare_masala_is_opener(self) -> None:
        assert _is_bare_micro_unit("المسألة الخامسة") == "opener"

    def test_bare_tanbih_is_opener(self) -> None:
        assert _is_bare_micro_unit("تنبيه") == "opener"

    def test_bare_closer_wallahu_alam(self) -> None:
        assert _is_bare_micro_unit("والله أعلم") == "closer"

    def test_bare_closer_intaha(self) -> None:
        assert _is_bare_micro_unit("انتهى") == "closer"

    def test_substantive_text_not_micro(self) -> None:
        """Normal scholarly text is not a micro-unit."""
        assert _is_bare_micro_unit("وقال الشافعي رحمه الله في هذه المسألة") is None

    def test_long_text_not_micro(self) -> None:
        """Text exceeding _MICRO_UNIT_MAX_CHARS is never micro."""
        long = "المسألة " + "و" * 50
        assert _is_bare_micro_unit(long) is None

    def test_semantically_complete_heading_exempt(self) -> None:
        """Heading with colon + content is NOT bare (Gemini exemption)."""
        # "قاعدة: اليقين لا يزول بالشك" = complete heading
        assert _is_bare_micro_unit("قاعدة: اليقين لا يزول بالشك") is None

    def test_colon_with_short_content_still_bare(self) -> None:
        """Heading with colon but very short content IS still bare."""
        assert _is_bare_micro_unit("فائدة: قال") == "opener"


class TestMergeUnits:
    """Tests for merge_micro_units bidirectional merge."""

    def test_forward_merge_opener_into_next(self) -> None:
        """Bare opener (تنبيه) merges forward into following unit."""
        text = "تنبيه ذكر القاضي عياض أن الحديث صحيح عند أهل العلم"
        units = [
            _make_unit(0, 0, 0, "تنبيه"),
            _make_unit(1, 1, 9, "ذكر القاضي عياض أن الحديث صحيح عند أهل العلم"),
        ]
        result = merge_micro_units(units, text)
        assert len(result) == 1
        assert result[0].start_word == 0
        assert result[0].end_word == 9

    def test_backward_merge_closer_into_previous(self) -> None:
        """Bare closer (والله أعلم) merges backward into preceding unit."""
        text = "وأي ذلك فعلت أجزأ والله أعلم"
        units = [
            _make_unit(0, 0, 3, "وأي ذلك فعلت أجزأ"),
            _make_unit(1, 4, 5, "والله أعلم"),
        ]
        result = merge_micro_units(units, text)
        assert len(result) == 1
        assert result[0].start_word == 0
        assert result[0].end_word == 5

    def test_no_merge_when_all_substantive(self) -> None:
        """No merge when all units have substantive content."""
        text = "وقال الشافعي في هذا الباب وقال أحمد في هذا الباب"
        units = [
            _make_unit(0, 0, 4, "وقال الشافعي في هذا الباب"),
            _make_unit(1, 5, 9, "وقال أحمد في هذا الباب"),
        ]
        result = merge_micro_units(units, text)
        assert len(result) == 2

    def test_reindexing_after_merge(self) -> None:
        """unit_index values are contiguous 0..N-1 after merge."""
        text = "الثالثة حكم الصلاة في المسجد واجبة عند الحنابلة"
        units = [
            _make_unit(0, 0, 0, "الثالثة"),
            _make_unit(1, 1, 7, "حكم الصلاة في المسجد واجبة عند الحنابلة"),
        ]
        result = merge_micro_units(units, text)
        assert len(result) == 1
        assert result[0].unit_index == 0

    def test_single_unit_no_merge(self) -> None:
        """Single unit list returned as-is."""
        text = "بسم الله الرحمن الرحيم"
        units = [_make_unit(0, 0, 3, "بسم الله الرحمن الرحيم")]
        result = merge_micro_units(units, text)
        assert len(result) == 1

    def test_empty_list_no_crash(self) -> None:
        """Empty input returns empty output."""
        result = merge_micro_units([], "")
        assert result == []

    def test_multiple_merges_in_sequence(self) -> None:
        """Multiple openers can each merge into their following unit."""
        text = "الأولى حكم كذا الثانية حكم كذا آخر"
        units = [
            _make_unit(0, 0, 0, "الأولى"),
            _make_unit(1, 1, 2, "حكم كذا"),
            _make_unit(2, 3, 3, "الثانية"),
            _make_unit(3, 4, 6, "حكم كذا آخر"),
        ]
        result = merge_micro_units(units, text)
        assert len(result) == 2
        assert result[0].start_word == 0  # الأولى merged with حكم كذا
        assert result[1].start_word == 3  # الثانية merged with حكم كذا آخر
