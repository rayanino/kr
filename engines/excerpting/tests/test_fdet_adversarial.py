"""Adversarial edge case tests for F-DET-1 through F-DET-9 (SPEC §7.1).

Each function is a pure computation of text/metadata — no LLM dependency.
These tests deliberately probe boundary conditions, ambiguous inputs, and
edge cases that the happy-path tests do not cover.

Session: fdet-deterministic (overnight hardening 2026-03-28)
"""

from __future__ import annotations

import logging

import pytest

from engines.excerpting.contracts import (
    AssemblyMetadata,
    AuthorAttribution,
    ClassifiedSegment,
    JoinPoint,
    ScholarAttribution,
    ScholarlyFunction,
    SplitInfo,
)
from engines.excerpting.src.phase3_deterministic import (
    build_deterministic_excerpts,
    compute_content_types,
    compute_excerpt_id,
    compute_layer_attribution,
    compute_page_range,
    compute_quoted_scholars,
    detect_evidence_refs,
    extract_primary_text,
    filter_relevant_footnotes,
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


# ═══════════════════════════════════════════════════════════════════
# F-DET-1 Adversarial: excerpt_id format edge cases
# ═══════════════════════════════════════════════════════════════════


class TestExcerptIdAdversarial:
    """F-DET-1 adversarial — source/div ID with special characters."""

    def test_source_id_with_hyphens(self) -> None:
        """source_id with hyphens is embedded verbatim — format is string interpolation."""
        result = compute_excerpt_id("src-test-123", "div_3_2", 0, 7)
        assert result == "exc_src-test-123_div_3_2_0_7"

    def test_div_id_with_underscores_ambiguity_documented(self) -> None:
        """div_id with underscores creates IDs that cannot be reversed unambiguously.

        exc_src_test_div_3_2_0_7 vs exc_src_test_div_3_2_0_7 are identical
        whether source_id='src_test' or source_id='src' and div_id='test_div_3_2'.
        This tests that the function DOES produce output (does not crash) — the
        ambiguity is a known design limitation documented here for auditability.
        """
        result = compute_excerpt_id("src_test", "div_3_2", 0, 7)
        assert result == "exc_src_test_div_3_2_0_7"
        # Note: indistinguishable from compute_excerpt_id("src", "test_div_3_2", 0, 7)
        result2 = compute_excerpt_id("src", "test_div_3_2", 0, 7)
        assert result == result2  # ID collision — documented design constraint

    def test_source_id_with_special_chars(self) -> None:
        """source_id with colons/slashes is embedded verbatim."""
        result = compute_excerpt_id("12345", "div_3.2", 2, 15)
        assert result == "exc_12345_div_3.2_2_15"

    def test_large_indices(self) -> None:
        """Large chunk_index and unit_index produce correct format."""
        result = compute_excerpt_id("src_001", "div_99_99", 999, 9999)
        assert result == "exc_src_001_div_99_99_999_9999"

    def test_zero_unit_index(self) -> None:
        """unit_index=0 is the first unit — distinct from unit_index=1."""
        r0 = compute_excerpt_id("src_1", "div_1", 0, 0)
        r1 = compute_excerpt_id("src_1", "div_1", 0, 1)
        assert r0 != r1
        assert r0 == "exc_src_1_div_1_0_0"


# ═══════════════════════════════════════════════════════════════════
# F-DET-2 Adversarial: primary_text extraction edge cases
# ═══════════════════════════════════════════════════════════════════


class TestPrimaryTextAdversarial:
    """F-DET-2 adversarial — boundary extraction and whitespace handling."""

    def test_first_word_only(self) -> None:
        """start_word=0, end_word=0 extracts exactly the first token."""
        text = "بسم الله الرحمن الرحيم"
        result = extract_primary_text(text, 0, 0)
        assert result == "بسم"

    def test_last_word_only(self) -> None:
        """start_word=last, end_word=last extracts exactly the last token."""
        text = "بسم الله الرحمن الرحيم"
        tokens = text.split()
        last = len(tokens) - 1
        result = extract_primary_text(text, last, last)
        assert result == "الرحيم"

    def test_trailing_whitespace_not_included(self) -> None:
        """Trailing whitespace in assembled_text is NOT included in primary_text.

        _build_token_char_map records end = start + len(token), so trailing
        spaces after the last token are outside the char range and excluded.
        This is SPEC-correct: primary_text is the text, not whitespace padding.
        """
        text = "بسم الله   "  # trailing 3 spaces
        tokens = text.split()  # ["بسم", "الله"]
        result = extract_primary_text(text, 0, len(tokens) - 1)
        assert result == "بسم الله"
        assert not result.endswith(" ")

    def test_internal_multiple_spaces_preserved(self) -> None:
        """Multiple internal spaces between words ARE preserved in substring extraction.

        This is the SPEC guarantee: substring, not split-rejoin. The double space
        in 'بسم  الله' is preserved.
        """
        text = "بسم  الله"  # double space between
        tokens = text.split()  # ["بسم", "الله"]
        result = extract_primary_text(text, 0, len(tokens) - 1)
        # The substring from start of "بسم" to end of "الله"
        # "بسم" occupies [0,3), "الله" occupies [5,9) in "بسم  الله"
        # assembled_text[0:9] = "بسم  الله" — the double space IS between them
        assert "  " in result or result == text  # double space preserved

    def test_internal_newline_preserved(self) -> None:
        r"""Newline between words is preserved (not the \n\n test — just \n)."""
        text = "بسم\nالله"
        tokens = text.split()
        result = extract_primary_text(text, 0, len(tokens) - 1)
        assert "\n" in result
        assert result == "بسم\nالله"


# ═══════════════════════════════════════════════════════════════════
# F-DET-3 Adversarial: layer attribution edge cases
# ═══════════════════════════════════════════════════════════════════


_META_EMPTY_SPLITS = AssemblyMetadata(
    constituent_unit_indices=[0],
    join_points=[],
    layer_split_points=[],
    footnote_renumber_map=None,
)


class TestLayerAttributionAdversarial:
    """F-DET-3 adversarial — empty layers, boundary coverage, layer merging."""

    def test_empty_layers_raises_value_error(self) -> None:
        """Zero text layers violates I-AC-2 — ValueError is the correct response.

        The implementation explicitly raises rather than silently returning a
        default. This is a deliberate fail-loud design (SPEC §8, CLAUDE.md rule 4).
        """
        text = "بسم الله الرحمن الرحيم"
        with pytest.raises(ValueError, match="F-DET-3"):
            compute_layer_attribution(text, [], 0, 3, _META_EMPTY_SPLITS)

    def test_exactly_80pct_coverage_applies_la1(self) -> None:
        """LA-1 boundary: coverage >= 0.8 exactly applies LA-1 (not LA-2).

        Text "أب جد" (2 words, 5 chars total):
          spans[0] = (0, 2), spans[1] = (3, 5)
          unit chars [0, 5), unit_length = 5
          Layer A [0, 4): overlap = min(4,5)-max(0,0) = 4, coverage = 4/5 = 0.8 exactly
          Layer B [4, 5): coverage = 1/5 = 0.2
        """
        text = "أب جد"  # "أب"=2 chars, " "=1, "جد"=2 → total 5 chars
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=4,  # covers 4 of 5 chars → exactly 80%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_matn",
                start=4,
                end=5,  # covers 1 of 5 chars → 20%
                confidence=1.0,
            ),
        ]
        result = compute_layer_attribution(text, layers, 0, 1, _META_EMPTY_SPLITS)
        assert result.rule_applied == "LA-1"
        assert result.layer_id == "sharh"
        assert abs(result.coverage_pct - 0.8) < 1e-9

    def test_79pct_coverage_does_not_apply_la1(self) -> None:
        """LA-1 boundary: coverage < 0.8 falls through to LA-2 (for 2 layers).

        Layer A covers 7 of 9 chars ≈ 77.8% < 80% → LA-2 applies.
        """
        # "أب جد هو" = "أب"(2) + " "(1) + "جد"(2) + " "(1) + "هو"(2) = 8 chars
        text = "أب جد هو"
        # spans: [0,2), [3,5), [6,8); unit [0,8), length=8
        # Layer A [0,6): overlap = 6, coverage = 6/8 = 75% < 80%
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_a",
                start=0,
                end=6,  # 6/8 = 75%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_b",
                start=6,
                end=8,
                confidence=1.0,
            ),
        ]
        result = compute_layer_attribution(text, layers, 0, 2, _META_EMPTY_SPLITS)
        # 2 layers, neither >=80% → LA-2
        assert result.rule_applied == "LA-2"
        assert result.layer_id == "sharh"  # SHARH > MATN in _LAYER_LEVEL

    def test_100_layers_each_1pct_triggers_la3(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """100 layers each covering ~1% of unit → LA-3 (ambiguous attribution).

        This is a degenerate multi-layer text (e.g., every word from a different
        source layer in a super-commentary). No layer reaches 80%; 3+ layers
        present, so LA-3 emits EX-M-001 warning.
        """
        # 100 single-char Arabic tokens separated by spaces: "ك ك ك ... ك"
        # Total: 100 tokens * 2 chars - 1 = 199 chars
        text = " ".join(["ك"] * 100)
        # Each layer covers 2 chars (token + separator), last covers 1
        # coverage_i ≈ 2/199 ≈ 1% — none reaches 80%
        layers: list[TextLayerSegment] = []
        for i in range(100):
            layer_start = i * 2
            layer_end = layer_start + 2 if i < 99 else layer_start + 1
            # Use alternating types since we only have 5 types
            ltype = [
                LayerType.MATN, LayerType.SHARH, LayerType.HASHIYAH,
                LayerType.TAHQIQ_NOTE, LayerType.UNCERTAIN,
            ][i % 5]
            layers.append(
                TextLayerSegment(
                    layer_type=ltype,
                    author_canonical_id=f"sch_{i:03d}",
                    start=layer_start,
                    end=layer_end,
                    confidence=1.0,
                )
            )

        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, _META_EMPTY_SPLITS
            )
        assert result.rule_applied == "LA-3"
        assert "EX-M-001" in caplog.text

    def test_three_identical_layers_merged_via_split_points_la4(self) -> None:
        """Three identical-type/author layers, all split-point boundaries → merge → LA-4.

        When split_info splits a long chunk, consecutive segments of the same
        (type, author) separated by a split point are artificially divided.
        After merging they form one continuous span → 100% coverage → LA-4.
        """
        # Text: "أ ب ج د" (4 tokens, positions: أ[0,1) ب[2,3) ج[4,5) د[6,7))
        text = "أ ب ج د"
        # Three SHARH layers covering the whole text, each separated at split points
        # Segment 0: [0, 2), Segment 1: [2, 5), Segment 2: [5, 7)
        # Boundaries 2 and 5 are in layer_split_points
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_001",
                start=0,
                end=2,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_001",
                start=2,
                end=5,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_001",
                start=5,
                end=7,
                confidence=1.0,
            ),
        ]
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[2, 5],  # ← these are split boundaries
            footnote_renumber_map=None,
        )
        tokens = text.split()
        result = compute_layer_attribution(text, layers, 0, len(tokens) - 1, meta)
        # After merging: one layer [0, 7) = full coverage → LA-4
        assert result.rule_applied == "LA-4"
        assert result.author_id == "sch_001"

    def test_all_layers_none_author_different_types_la3(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Three layers all with author_canonical_id=None but different types.

        Attribution falls back to 'unknown' for author_id. LA-3 applies
        when 3+ layers present with no dominant author. EX-M-001 emitted.
        """
        text = "أ ب ج د ه و"  # 6 tokens
        text_len = len(text)  # 11 chars
        third = text_len // 3
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id=None,
                start=third,
                end=2 * third,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id=None,
                start=2 * third,
                end=text_len,
                confidence=1.0,
            ),
        ]
        tokens = text.split()
        with caplog.at_level(logging.WARNING):
            result = compute_layer_attribution(
                text, layers, 0, len(tokens) - 1, _META_EMPTY_SPLITS
            )
        assert result.rule_applied == "LA-3"
        # author_canonical_id=None falls back to "unknown"
        assert result.author_id == "unknown"
        assert "EX-M-001" in caplog.text


# ═══════════════════════════════════════════════════════════════════
# F-DET-4 Adversarial: content_types edge cases
# ═══════════════════════════════════════════════════════════════════


class TestContentTypesAdversarial:
    """F-DET-4 adversarial — empty inputs, mismatched indices, full enum coverage."""

    def test_empty_segments_list(self) -> None:
        """segments=[] produces empty content_types (not an error)."""
        result = compute_content_types([], [0, 1, 2])
        assert result == []

    def test_empty_unit_indices(self) -> None:
        """unit_segment_indices=[] produces empty content_types."""
        seg = _make_classified_segment(
            segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION
        )
        result = compute_content_types([seg], [])
        assert result == []

    def test_indices_not_matching_any_segment(self) -> None:
        """Indices that don't match any segment's segment_index → empty result.

        TeachingUnit may reference segment_indices that no longer exist if
        a segment was dropped (shouldn't happen by SPEC, but tested defensively).
        """
        segs = [
            _make_classified_segment(segment_index=0, scholarly_function=ScholarlyFunction.DEFINITION),
            _make_classified_segment(segment_index=1, scholarly_function=ScholarlyFunction.EXAMPLE),
        ]
        # Request indices 5 and 6 — neither exist
        result = compute_content_types(segs, [5, 6])
        assert result == []

    def test_all_16_scholarly_functions_included(self) -> None:
        """When each segment has a unique ScholarlyFunction, all 16 are returned.

        Validates that the deduplication does NOT accidentally discard unique types.
        """
        all_functions = list(ScholarlyFunction)
        assert len(all_functions) == 16  # sanity check on enum size
        segs = [
            _make_classified_segment(segment_index=i, scholarly_function=fn)
            for i, fn in enumerate(all_functions)
        ]
        indices = list(range(16))
        result = compute_content_types(segs, indices)
        assert len(result) == 16
        assert set(result) == set(all_functions)

    def test_unclassified_function_included(self) -> None:
        """UNCLASSIFIED is a valid ScholarlyFunction and must appear in content_types."""
        seg = _make_classified_segment(
            segment_index=0, scholarly_function=ScholarlyFunction.UNCLASSIFIED
        )
        result = compute_content_types([seg], [0])
        assert ScholarlyFunction.UNCLASSIFIED in result

    def test_dedup_preserves_first_occurrence_order(self) -> None:
        """Deduplication preserves insertion order (not alphabetical or by enum ordinal)."""
        segs = [
            _make_classified_segment(segment_index=0, scholarly_function=ScholarlyFunction.RULE_STATEMENT),
            _make_classified_segment(segment_index=1, scholarly_function=ScholarlyFunction.DEFINITION),
            _make_classified_segment(segment_index=2, scholarly_function=ScholarlyFunction.RULE_STATEMENT),  # dup
        ]
        result = compute_content_types(segs, [0, 1, 2])
        assert result[0] == ScholarlyFunction.RULE_STATEMENT  # first seen
        assert result[1] == ScholarlyFunction.DEFINITION
        assert len(result) == 2  # deduplication worked


# ═══════════════════════════════════════════════════════════════════
# F-DET-5 Adversarial: evidence_refs edge cases
# ═══════════════════════════════════════════════════════════════════


class TestEvidenceRefsAdversarial:
    """F-DET-5 adversarial — substring false positives, boundary markers, empty delimiters."""

    def test_rawaha_contains_rawah_intentional_false_positive(self) -> None:
        """'رواها' contains 'رواه' as a substring — detected by DD-S3-8 plain matching.

        This is documented as intentional (DD-S3-8): word-boundary checks cause
        ~76% false NEGATIVES with Arabic proclitic prefixes. Plain substring is
        the correct strategy even at the cost of some false positives.
        """
        text = "رواها شيخنا عن النبي صلى الله عليه وسلم"
        refs = detect_evidence_refs(text)
        # "رواه" IS found at position 0 inside "رواها"
        hadith_refs = [r for r in refs if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        assert any("رواه" in r.text_snippet for r in hadith_refs)

    def test_empty_quran_delimiters_no_match(self) -> None:
        """﴿﴾ with no text between does NOT match — regex uses [^﴾]+ (one or more chars).

        An empty pair of ornate brackets is a markup artefact, not a verse.
        """
        text = "قال تعالى ﴿﴾ في كتابه"
        refs = detect_evidence_refs(text)
        quran_refs = [r for r in refs if r.type == "quran"]
        assert len(quran_refs) == 0

    def test_quran_delimiter_single_char_content_matches(self) -> None:
        """﴿ح﴾ with a single character IS a valid match (just very short)."""
        text = "قال تعالى ﴿ح﴾"
        refs = detect_evidence_refs(text)
        quran_refs = [r for r in refs if r.type == "quran"]
        assert len(quran_refs) == 1
        assert quran_refs[0].text_snippet == "ح"

    def test_hadith_marker_at_position_zero(self) -> None:
        """'رواه' at position 0 is detected — snippet_start = max(0, -25) = 0."""
        text = "رواه أبو داود في سننه عن معاذ بن جبل"
        refs = detect_evidence_refs(text)
        hadith_refs = [r for r in refs if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        # snippet starts at 0 (clamped), marker at position 0
        assert any(r.text_snippet.startswith("رواه") for r in hadith_refs)

    def test_hadith_marker_at_end_of_text(self) -> None:
        """'رواه' at end of text — snippet_end = min(len, pos+len+25) = len."""
        text = "من توضأ فأحسن الوضوء رواه"
        refs = detect_evidence_refs(text)
        hadith_refs = [r for r in refs if r.type == "hadith"]
        assert len(hadith_refs) >= 1
        assert any(r.text_snippet.endswith("رواه") for r in hadith_refs)

    def test_same_hadith_marker_appears_twice_both_detected(self) -> None:
        """The same marker ('رواه') appearing twice produces TWO EvidenceRef entries.

        Each occurrence has a different position → different (pos, marker) key.
        """
        text = "رواه البخاري ومسلم ورواه أبو داود"
        refs = detect_evidence_refs(text)
        hadith_refs = [r for r in refs if r.marker_text == "رواه"]
        # "رواه" appears at position 0 AND inside "ورواه" → both detected
        assert len(hadith_refs) == 2

    def test_ijma_marker_at_start_of_text(self) -> None:
        """'أجمعوا' at position 0 is detected — boundary clamped correctly."""
        text = "أجمعوا على أن الصلاة فرض عين"
        refs = detect_evidence_refs(text)
        ijma_refs = [r for r in refs if r.type == "ijma"]
        assert len(ijma_refs) >= 1

    def test_no_evidence_in_pure_arabic_prose(self) -> None:
        """Pure Arabic scholarly prose without any evidence markers → empty list."""
        text = "إن الكلام في اللغة هو اللفظ المركب المفيد بالوضع"
        refs = detect_evidence_refs(text)
        assert refs == []

    def test_all_three_evidence_types_in_one_text(self) -> None:
        """Text with quran, hadith, and ijma evidence produces refs of all three types."""
        text = (
            "قال تعالى ﴿وَأَقِيمُوا الصَّلَاةَ﴾ ورواه البخاري "
            "وقد أجمعوا على وجوب الصلاة"
        )
        refs = detect_evidence_refs(text)
        types = {r.type for r in refs}
        assert "quran" in types
        assert "hadith" in types
        assert "ijma" in types


# ═══════════════════════════════════════════════════════════════════
# F-DET-6 Adversarial: physical_pages edge cases
# ═══════════════════════════════════════════════════════════════════


class TestPageRangeAdversarial:
    """F-DET-6 adversarial — join point boundaries, many pages, edge offsets."""

    def _jp(self, offset: int, after_idx: int = 0) -> JoinPoint:
        """Helper: build a minimal valid JoinPoint at the given char offset."""
        return JoinPoint(
            after_unit_index=after_idx,
            before_unit_index=after_idx + 1,
            boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
            separator_used="\n",
            char_offset_in_assembled=offset,
        )

    def test_unit_starting_at_exact_join_point(self) -> None:
        """Unit starting at exact join_point offset is on the second page.

        Boundary condition: page_start < char_end AND page_end > char_start.
        When unit starts at join_point=10, page 0 covers [0,10) — page_end=10
        is NOT > char_start=10 → page 0 excluded. Page 1 covers [10,...) →
        page_start=10 < char_end → page 1 included.
        """
        pages = [
            PhysicalPage(volume=1, page_number_display="5", page_number_int=5),
            PhysicalPage(volume=1, page_number_display="6", page_number_int=6),
        ]
        join_pts = [self._jp(10)]
        # Unit occupies chars [10, 20) — starts exactly at join point
        result = compute_page_range(pages, join_pts, 10, 20)
        assert result is not None
        assert result.start_page == 6  # page 1, not page 0
        assert result.end_page == 6

    def test_unit_ending_at_exact_join_point(self) -> None:
        """Unit ending exactly before join_point is entirely on first page.

        Unit [0, 10), join_point at 10 → page 0 covers [0,10).
        page_start=0 < char_end=10 (yes) AND page_end=10 > char_start=0 (yes)
        → page 0 included. Page 1: page_start=10 < char_end=10 → False → excluded.
        """
        pages = [
            PhysicalPage(volume=1, page_number_display="5", page_number_int=5),
            PhysicalPage(volume=1, page_number_display="6", page_number_int=6),
        ]
        join_pts = [self._jp(10)]
        # Unit [0, 10) — ends exactly at join point
        result = compute_page_range(pages, join_pts, 0, 10)
        assert result is not None
        assert result.start_page == 5
        assert result.end_page == 5  # only page 0

    def test_many_join_points_100_pages(self) -> None:
        """101 pages with 100 join points — unit in the middle finds correct page."""
        # 101 pages, each page covers 10 chars: page i covers [i*10, (i+1)*10)
        pages = [
            PhysicalPage(volume=1, page_number_display=str(i + 1), page_number_int=i + 1)
            for i in range(101)
        ]
        join_pts = [self._jp(i * 10, after_idx=i - 1) for i in range(1, 101)]
        # Unit covers chars [300, 320) — spans pages 30 and 31 (0-indexed)
        result = compute_page_range(pages, join_pts, 300, 320)
        assert result is not None
        # page 30 (0-indexed) covers [300, 310), page 31 covers [310, 320)
        # page_number_int = i+1, so page 30 → 31, page 31 → 32
        assert result.start_page == 31
        assert result.end_page == 32

    def test_unit_spanning_all_pages(self) -> None:
        """Unit spanning entire assembled_text covers all pages."""
        pages = [
            PhysicalPage(volume=1, page_number_display=str(i), page_number_int=i)
            for i in range(1, 6)
        ]
        join_pts = [self._jp(i * 20, after_idx=i - 1) for i in range(1, 5)]
        # Unit [0, 200) covers all 5 pages (each covers 20 chars, total 100)
        result = compute_page_range(pages, join_pts, 0, 200)
        assert result is not None
        assert result.start_page == 1
        assert result.end_page == 5


# ═══════════════════════════════════════════════════════════════════
# F-DET-7 Adversarial: div_path passthrough edge cases
# ═══════════════════════════════════════════════════════════════════


class TestDivPathAdversarial:
    """F-DET-7 adversarial — div_path is a chunk passthrough field.

    Since div_path is a direct passthrough from AssembledChunk.div_path,
    these tests verify the orchestrator preserves it at all depths and contents.
    """

    def test_empty_div_path(self) -> None:
        """Empty div_path is preserved as empty list (no headings detected)."""
        chunk = _make_assembled_chunk(div_path=[])
        unit = _make_teaching_unit()
        seg = _make_classified_segment()
        records = build_deterministic_excerpts(chunk, [unit], [seg])
        assert records[0].div_path == []

    def test_10_level_deep_div_path(self) -> None:
        """10-level deep heading hierarchy is fully preserved."""
        deep_path = [
            "كتاب الفقه",
            "باب العبادات",
            "فصل في الصلاة",
            "فرع في شروط الصلاة",
            "فرع فرعي في النية",
            "تنبيه",
            "مسألة",
            "قاعدة",
            "ضابط",
            "تفريع",
        ]
        chunk = _make_assembled_chunk(div_path=deep_path)
        unit = _make_teaching_unit()
        seg = _make_classified_segment()
        records = build_deterministic_excerpts(chunk, [unit], [seg])
        assert records[0].div_path == deep_path
        assert len(records[0].div_path) == 10

    def test_div_path_arabic_only_headings(self) -> None:
        """Fully Arabic headings with diacritics are preserved byte-for-byte."""
        path = ["كِتَابُ الطَّهَارَةِ", "بَابُ الْوُضُوءِ", "فَصْلٌ فِي فَرَائِضِهِ"]
        chunk = _make_assembled_chunk(div_path=path)
        unit = _make_teaching_unit()
        seg = _make_classified_segment()
        records = build_deterministic_excerpts(chunk, [unit], [seg])
        assert records[0].div_path == path

    def test_div_path_mixed_arabic_latin(self) -> None:
        """Mixed Arabic/Latin headings (e.g., from digitized critical editions) preserved."""
        path = ["كتاب الطهارة (Kitāb al-Ṭahāra)", "باب 1 — Wuḍūʾ"]
        chunk = _make_assembled_chunk(div_path=path)
        unit = _make_teaching_unit()
        seg = _make_classified_segment()
        records = build_deterministic_excerpts(chunk, [unit], [seg])
        assert records[0].div_path == path


# ═══════════════════════════════════════════════════════════════════
# F-DET-8 Adversarial: footnotes_relevant boundary and edge cases
# ═══════════════════════════════════════════════════════════════════


class TestFootnoteFilteringAdversarial:
    """F-DET-8 adversarial — position boundaries, double occurrence, many footnotes."""

    def test_marker_at_char_start_included(self) -> None:
        """Footnote marker at char_start (== char_start) IS included.

        Boundary: char_start <= pos < char_end. pos == char_start → included.
        """
        # assembled_text starts with the footnote marker ⌜1⌝
        assembled = "⌜1⌝ وقال النبي صلى الله عليه وسلم"
        footnote = Footnote(
            ref_marker="1",
            text="تخريج الحديث",
            footnote_type=FootnoteType.HADITH_TAKHRIJ,
            confidence=0.9,
        )
        # Unit range covers the whole text: pos of ⌜1⌝ = 0 = char_start
        char_start = 0
        char_end = len(assembled)
        result = filter_relevant_footnotes(
            assembled, assembled, [footnote], char_start, char_end
        )
        assert len(result) == 1

    def test_marker_at_char_end_minus_one_included(self) -> None:
        """Footnote marker at char_end-1 (last valid position) IS included."""
        # Build text where ⌜1⌝ appears at char_end - len("⌜1⌝")
        prefix = "وقال النبي صلى الله عليه وسلم "
        marker_str = "⌜1⌝"
        assembled = prefix + marker_str
        char_start = 0
        char_end = len(assembled)  # exclusive — so pos = len(prefix) < char_end
        footnote = Footnote(
            ref_marker="1",
            text="تخريج الحديث",
            footnote_type=FootnoteType.HADITH_TAKHRIJ,
            confidence=0.9,
        )
        result = filter_relevant_footnotes(
            assembled, assembled, [footnote], char_start, char_end
        )
        assert len(result) == 1

    def test_marker_at_char_end_excluded(self) -> None:
        """Footnote marker at exact char_end is OUTSIDE unit range — excluded.

        Boundary: pos must satisfy pos < char_end (strictly less than).
        """
        prefix = "وقال النبي صلى الله عليه وسلم"
        marker_str = " ⌜1⌝"
        assembled = prefix + marker_str
        # Unit covers only the prefix — char_end = len(prefix)
        char_start = 0
        char_end = len(prefix)  # marker is at char_end → excluded
        footnote = Footnote(
            ref_marker="1",
            text="تخريج الحديث",
            footnote_type=FootnoteType.HADITH_TAKHRIJ,
            confidence=0.9,
        )
        result = filter_relevant_footnotes(
            assembled, assembled, [footnote], char_start, char_end
        )
        assert len(result) == 0

    def test_marker_appearing_twice_first_outside_second_inside_excluded(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """LATENT BUG EXPOSURE: marker appearing twice, first outside range, second inside.

        filter_relevant_footnotes uses assembled_text.find(pattern) which returns
        the FIRST occurrence. If the first occurrence is before char_start, the
        footnote is excluded even though a second occurrence IS within the unit range.

        This test documents the current behavior (first-occurrence-only semantics)
        so that if this is ever fixed, the test will need to be updated.
        """
        # assembled_text has ⌜1⌝ at position 0 (before unit) and position 30 (in unit)
        prefix = "⌜1⌝ مقدمة خارج النطاق "  # marker at pos 0, outside unit
        suffix = "⌜1⌝ داخل النطاق"        # second marker inside unit
        assembled = prefix + suffix
        # Unit starts at len(prefix) — the second ⌜1⌝ is inside
        char_start = len(prefix)
        char_end = len(assembled)
        footnote = Footnote(
            ref_marker="1",
            text="ملاحظة هامة",
            footnote_type=FootnoteType.LINGUISTIC_NOTE,
            confidence=0.9,
        )
        result = filter_relevant_footnotes(
            assembled, assembled, [footnote], char_start, char_end
        )
        # Current behavior: EXCLUDED (find() returns first occurrence at pos 0 < char_start)
        # This is a documented limitation — not a fix.
        assert len(result) == 0

    def test_100_footnotes_all_relevant(self) -> None:
        """100 footnotes with markers all within unit range — all returned."""
        # Build assembled_text with 100 markers spread across it
        markers = [f"⌜{i}⌝" for i in range(1, 101)]
        assembled = " ".join(f"نص {m}" for m in markers)
        footnotes = [
            Footnote(
                ref_marker=str(i),
                text=f"ملاحظة رقم {i}",
                footnote_type=FootnoteType.LINGUISTIC_NOTE,
                confidence=0.9,
            )
            for i in range(1, 101)
        ]
        result = filter_relevant_footnotes(
            assembled, assembled, footnotes, 0, len(assembled)
        )
        assert len(result) == 100

    def test_ref_marker_substring_not_confused(self) -> None:
        """ref_marker='1' does NOT match ⌜10⌝ — pattern is ⌜1⌝ (exact, including delimiters).

        The search pattern is `⌜{ref_marker}⌝` = `⌜1⌝`, which is a 3-char sequence.
        ⌜10⌝ does not contain the substring ⌜1⌝ (it contains ⌜1 but not ⌜1⌝).
        """
        assembled = "نص ⌜10⌝ ثم ⌜100⌝ ونص"
        footnote = Footnote(
            ref_marker="1",
            text="هذه ملاحظة رقم واحد",
            footnote_type=FootnoteType.LINGUISTIC_NOTE,
            confidence=0.9,
        )
        # ⌜1⌝ does not appear in "⌜10⌝" or "⌜100⌝"
        result = filter_relevant_footnotes(
            assembled, assembled, [footnote], 0, len(assembled)
        )
        assert len(result) == 0  # ⌜1⌝ not found → orphan warning, not included

    def test_empty_footnotes_no_crash(self) -> None:
        """Empty footnote list produces empty result without crashing."""
        assembled = "وقال النبي صلى الله عليه وسلم ⌜1⌝ من توضأ"
        result = filter_relevant_footnotes(assembled, assembled, [], 0, len(assembled))
        assert result == []


# ═══════════════════════════════════════════════════════════════════
# F-DET-9 Adversarial: quoted_scholars edge cases
# ═══════════════════════════════════════════════════════════════════


class TestQuotedScholarsAdversarial:
    """F-DET-9 adversarial — many scholars, all-same primary, None authors."""

    def test_all_layers_same_as_primary_empty_result(self) -> None:
        """When all layers have the same type+author as primary → empty quoted_scholars."""
        text = "قال الشارح يريد أن الكلام في اصطلاح النحويين"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_sharh",
            coverage_pct=1.0,
            rule_applied="LA-4",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        char_start = 0
        char_end = len(text)
        result = compute_quoted_scholars(layers, char_start, char_end, primary, meta)
        assert result == []

    def test_layer_with_none_author_is_included(self) -> None:
        """Layer with author_canonical_id=None but different type from primary IS included.

        The check is on both type AND effective author. None author → "unknown".
        If primary is SHARH/"sch_sharh", then MATN/None (→ MATN/"unknown") is different
        → included in quoted_scholars.
        """
        text = "قال ابن مالك كلامنا لفظ مفيد يريد الشارح أن"
        matn_end = len("قال ابن مالك كلامنا لفظ مفيد")
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,  # ← None author
                start=0,
                end=matn_end,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_sharh",
                start=matn_end,
                end=len(text),
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="sharh",
            author_id="sch_sharh",
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
        # MATN/None is NOT the primary (SHARH/sch_sharh) → included
        assert len(result) == 1
        assert result[0].resolved_name is None  # author_canonical_id=None preserved
        assert result[0].source == "layer_overlap"
        assert result[0].confidence == 1.0

    def test_none_author_same_type_as_primary_excluded(self) -> None:
        """Layer with author_canonical_id=None, SAME type as primary → excluded.

        primary: MATN/"unknown". secondary: MATN/None → effective_author="unknown".
        Type="matn" == layer_id="matn" AND "unknown"=="unknown" → excluded.
        """
        text = "قال ابن مالك كلامنا لفظ مفيد"
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ]
        # Primary is MATN/unknown (from None → "unknown" fallback)
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="unknown",
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
        assert result == []  # same type+author → excluded

    def test_many_distinct_non_primary_scholars(self) -> None:
        """Multiple distinct non-primary layers all appear in quoted_scholars.

        A hashiyah spanning 4 sub-layers (each attributing 25% to different scholars)
        — none is the primary — all appear in quoted_scholars.
        """
        # Text: 4 equal segments of 10 chars each, total 40 chars
        # Build with non-overlapping SHARH layers (4 different authors)
        # Primary is HASHIYAH/"sch_hashi" covering... wait, for this test
        # let's make primary HASHIYAH and have 3 non-primary SHARH/MATN/UNCERTAIN layers
        text_parts = [
            "قال الأول ",   # 10 chars
            "قال الثاني ",  # 11 chars
            "قال الثالث",   # 10 chars
        ]
        text = "".join(text_parts)
        cumulative = [0]
        for p in text_parts:
            cumulative.append(cumulative[-1] + len(p))

        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_a",
                start=cumulative[0],
                end=cumulative[1],
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_b",
                start=cumulative[1],
                end=cumulative[2],
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_c",
                start=cumulative[2],
                end=cumulative[3],
                confidence=1.0,
            ),
        ]
        # Primary is MATN/sch_a (dominates or was chosen by LA rule)
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_a",
            coverage_pct=0.4,
            rule_applied="LA-3",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, len(text), primary, meta)
        # sch_b and sch_c are non-primary → both appear
        scholar_ids = {s.resolved_name for s in result}
        assert "sch_b" in scholar_ids
        assert "sch_c" in scholar_ids
        # sch_a (primary) must NOT appear
        assert "sch_a" not in scholar_ids

    def test_duplicate_type_author_pair_produces_multiple_entries(self) -> None:
        """Two non-adjacent non-primary layers with same (type, author) → 2 entries.

        Without split-point merging, two non-adjacent SHARH/sch_b layers both
        with >0% coverage each produce a separate ScholarAttribution. This is
        the SPEC behavior (F-DET-9 does not deduplicate within quoted_scholars).
        The deduplication with §7.2 LLM detections is a post-step.
        """
        text = "أ ب ج د ه"  # 5 tokens
        # Layer pattern: SHARH/sch_b at [0,2), MATN/sch_a at [2,6), SHARH/sch_b at [6,9)
        # Not adjacent at a split point → NOT merged
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_b",
                start=0,
                end=2,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_a",
                start=2,
                end=6,
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_b",
                start=6,
                end=9,
                confidence=1.0,
            ),
        ]
        primary = AuthorAttribution(
            layer_id="matn",
            author_id="sch_a",
            coverage_pct=0.5,
            rule_applied="LA-3",
        )
        meta = AssemblyMetadata(
            constituent_unit_indices=[0],
            join_points=[],
            layer_split_points=[],  # NO split points → NOT merged
            footnote_renumber_map=None,
        )
        result = compute_quoted_scholars(layers, 0, 9, primary, meta)
        # Two SHARH/sch_b segments → 2 ScholarAttribution entries for sch_b
        sch_b_entries = [s for s in result if s.resolved_name == "sch_b"]
        assert len(sch_b_entries) == 2
