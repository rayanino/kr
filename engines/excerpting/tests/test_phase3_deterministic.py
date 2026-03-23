"""Tests for Phase 3 deterministic metadata assembly (SPEC §7.1, §6.2).

Covers F-DET-1 through F-DET-9, orchestrator (F10), and critical
design decisions DD-S3-1 through DD-S3-9.
"""

from __future__ import annotations

import logging
from typing import Any

import pytest

from engines.excerpting.contracts import (
    AssemblyMetadata,
    AuthorAttribution,
    ClassifiedSegment,
    EvidenceRef,
    ExcerptRecord,
    ExcerptingErrorCodes,
    JoinPoint,
    ScholarAttribution,
    ScholarlyFunction,
    SelfContainmentLevel,
    SplitInfo,
    TeachingUnit,
)
from engines.excerpting.src.phase3_deterministic import (
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
)
from engines.normalization.contracts import (
    BoundaryContinuityType,
    Footnote,
    FootnoteType,
    LayerType,
    PhysicalPage,
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
        """LA-2: Two layers, neither >= 80% -> outermost (highest level) wins."""
        # 50/50 split between MATN and SHARH
        text = "قال ابن مالك الكلام لفظ مفيد يريد أن اللفظ المفيد"
        mid = len(text) // 2
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=0,
                end=mid,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=mid,
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
        assert result.rule_applied == "LA-2"
        # SHARH > MATN in _LAYER_LEVEL
        assert result.layer_id == "sharh"

    def test_la2_even_with_dominant_below_60pct(self) -> None:
        """LA-2 catches ALL 2-layer cases (even dominant < 60%).

        LA-3's 'dominant <60%' condition never fires for 2-layer cases
        because LA-2 is checked first.
        """
        # MATN=40%, SHARH=60% — neither >= 80%, exactly 2 layers
        text = "أ ب ج د ه و ز ح ط ي"  # 10 tokens
        mid = len(text) * 4 // 10  # ~40% for MATN
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
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # LA-2, not LA-3 — LA-2 catches all 2-layer cases
        assert result.rule_applied == "LA-2"

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
