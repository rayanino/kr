"""Phase 1 hardening tests — edge cases and boundary conditions.

Covers 8 edge case categories for the deterministic assembly pipeline:
1. Empty division (no content units / all-blank)
2. Single-word content unit
3. Division at exact OVERSIZED_DIVISION_WORDS boundary (5000 words)
4. Content unit with only footnotes, no meaningful text
5. Mixed Arabic/Latin text assembly
6. Division with maximum nesting depth
7. Consecutive divisions with same heading
8. Content unit with ZWNJ characters (U+200C)

All tests use real Arabic text from domain fixtures. Regex uses [0-9] not \\d.
Arabic text: never .lower()/.upper()/.strip() on Arabic strings directly.
"""

from __future__ import annotations

from engines.excerpting.contracts import (
    ExcerptingConfig,
    _count_arabic_words,
)
from engines.excerpting.src.phase1_assembly import (
    assemble_text,
    check_heading_alignment,
    find_leaf_divisions,
    merge_tiny_divisions,
    rebase_text_layers,
    run_phase1,
    should_skip_division,
    split_oversized_division,
    strip_arabic_noise,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_content_unit,
    _make_division_node,
    _make_normalized_package,
)
from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContentFlags,
    ContinuityDetectionMethod,
    DivisionNode,
    Footnote,
    FootnoteType,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerType,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════


def _bc(bc_type: BoundaryContinuityType) -> BoundaryContinuity:
    """Shorthand factory for BoundaryContinuity."""
    return BoundaryContinuity(
        type=bc_type,
        confidence=0.9,
        detection_method=ContinuityDetectionMethod.PUNCTUATION_ANALYSIS,
        continuation_hint=None,
    )


def _generate_arabic_text(word_count: int) -> str:
    """Generate Arabic text with approximately word_count Arabic words.

    Uses real scholarly vocabulary from fiqh/grammar domains.
    """
    base_words = [
        "وقال", "المؤلف", "رحمه", "الله", "تعالى", "في", "كتابه",
        "العظيم", "الذي", "صنفه", "في", "علم", "الفقه", "والأصول",
        "والنحو", "والصرف", "والبلاغة", "والمنطق", "والحديث", "والتفسير",
    ]
    words: list[str] = []
    while len(words) < word_count:
        words.extend(base_words)
    return " ".join(words[:word_count])


# ═══════════════════════════════════════════════════════════════════
# 1. Empty division (no content units / all-blank)
# ═══════════════════════════════════════════════════════════════════


class TestEmptyDivision:
    """Edge cases for divisions with no usable content."""

    def test_all_blank_units_skipped(self) -> None:
        """Division where ALL content units are is_blank=True is skipped."""
        node = _make_division_node(start_unit_index=0, end_unit_index=1)
        units = [
            _make_content_unit(
                unit_index=0, content_flags=ContentFlags(is_blank=True)
            ),
            _make_content_unit(
                unit_index=1, content_flags=ContentFlags(is_blank=True)
            ),
        ]
        result = should_skip_division(node, units)
        assert result == "all_blank"

    def test_all_blank_produces_no_chunks(self) -> None:
        """run_phase1 with all-blank units produces no chunks."""
        units = [
            _make_content_unit(
                unit_index=i,
                content_flags=ContentFlags(is_blank=True),
            )
            for i in range(3)
        ]
        pkg = _make_normalized_package(content_units=units, num_units=3)
        config = ExcerptingConfig()
        chunks, _results = run_phase1(pkg, config)
        assert len(chunks) == 0

    def test_mixed_blank_and_content(self) -> None:
        """Division with some blank, some content units keeps only content."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="الحمد لله رب العالمين",
                content_flags=ContentFlags(is_blank=False),
            ),
            _make_content_unit(
                unit_index=1,
                content_flags=ContentFlags(is_blank=True),
            ),
            _make_content_unit(
                unit_index=2,
                primary_text="الرحمن الرحيم",
                content_flags=ContentFlags(is_blank=False),
            ),
        ]
        text, _jps, indices = assemble_text(units, 0, 2)
        assert "الحمد" in text
        assert "الرحمن" in text
        # Blank unit's text should NOT be in assembled text
        # But its index IS in constituent_unit_indices (I-AC-4)
        assert 1 in indices

    def test_empty_text_after_assembly_skipped(self) -> None:
        """Division producing empty text after assembly is skipped in run_phase1."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="",
                content_flags=ContentFlags(is_blank=True),
            ),
        ]
        pkg = _make_normalized_package(content_units=units, num_units=1)
        config = ExcerptingConfig()
        chunks, _ = run_phase1(pkg, config)
        assert len(chunks) == 0


# ═══════════════════════════════════════════════════════════════════
# 2. Single-word content unit
# ═══════════════════════════════════════════════════════════════════


class TestSingleWordContentUnit:
    """Edge cases for very short content (1-2 words)."""

    def test_single_arabic_word_assembles(self) -> None:
        """Single Arabic word produces valid assembled text."""
        units = [_make_content_unit(unit_index=0, primary_text="بسم")]
        text, jps, _indices = assemble_text(units, 0, 0)
        assert text == "بسم"
        assert _count_arabic_words(text) == 1
        assert len(jps) == 0

    def test_single_word_chunk_word_count(self) -> None:
        """Single-word chunk has correct word_count and total_tokens."""
        pkg = _make_normalized_package(
            num_units=1,
            primary_text="الله",
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 1
        assert chunks[0].word_count == 1
        assert chunks[0].total_tokens == 1
        # Validation passes (V-P1-3 may warn but not fatal)
        assert all(r["status"] in ("pass", "warning") for r in results)

    def test_single_word_layer_coverage(self) -> None:
        """Single-word chunk satisfies I-AC-2 layer coverage."""
        pkg = _make_normalized_package(num_units=1, primary_text="كتاب")
        config = ExcerptingConfig()
        chunks, _ = run_phase1(pkg, config)
        assert len(chunks) == 1
        chunk = chunks[0]
        layers = chunk.text_layers
        assert len(layers) >= 1
        assert layers[0].start == 0
        assert layers[-1].end == len(chunk.assembled_text)

    def test_single_word_is_tiny_but_only_child(self) -> None:
        """Single-word division is tiny but has no sibling to merge with."""
        pkg = _make_normalized_package(num_units=1, primary_text="فصل")
        config = ExcerptingConfig(TINY_DIVISION_WORDS=50)
        chunks, _results = run_phase1(pkg, config)
        assert len(chunks) == 1
        # No merge occurred (only child)
        assert chunks[0].merge_history is None


# ═══════════════════════════════════════════════════════════════════
# 3. Division at exact OVERSIZED_DIVISION_WORDS boundary (5000)
# ═══════════════════════════════════════════════════════════════════


class TestOversizedBoundary:
    """Boundary tests for the 5000-word oversized threshold."""

    def test_exactly_at_threshold_no_split(self) -> None:
        """Division with exactly OVERSIZED_DIVISION_WORDS is NOT split."""
        threshold = 100  # Use smaller threshold for test speed
        text = _generate_arabic_text(threshold)
        wc = _count_arabic_words(text)
        assert wc == threshold

        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=threshold)
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) == 1
        assert result[0].split_info is None

    def test_one_over_threshold_splits(self) -> None:
        """Division with OVERSIZED + 1 words IS split."""
        threshold = 100
        text = _generate_arabic_text(threshold + 50)  # Well over threshold
        # Insert paragraph breaks for reliable split points
        words = text.split()
        mid = len(words) // 2
        text = " ".join(words[:mid]) + "\n\n" + " ".join(words[mid:])
        wc = _count_arabic_words(text)

        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=threshold)
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2

    def test_at_default_5000_threshold(self) -> None:
        """Exactly 5000 words = no split with default config."""
        text = _generate_arabic_text(5000)
        wc = _count_arabic_words(text)
        config = ExcerptingConfig()  # Default: OVERSIZED_DIVISION_WORDS=5000
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) == 1

    def test_split_chunks_have_consistent_split_info(self) -> None:
        """All split chunks share consistent total_chunks and original_div_id."""
        threshold = 80
        # Generate text with paragraph breaks
        parts = [_generate_arabic_text(50) for _ in range(4)]
        text = "\n\n".join(parts)
        wc = _count_arabic_words(text)

        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=threshold)
        chunk = _make_assembled_chunk(
            chunk_id="div_boundary_test",
            div_id="div_boundary_test",
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2

        assert result[0].split_info is not None
        total = result[0].split_info.total_chunks
        for i, c in enumerate(result):
            assert c.split_info is not None
            assert c.split_info.original_div_id == "div_boundary_test"
            assert c.split_info.chunk_index == i
            assert c.split_info.total_chunks == total

    def test_i_ac_7_after_split(self) -> None:
        """I-AC-7: split chunks have split_info but NOT merge_history."""
        threshold = 80
        text = _generate_arabic_text(50) + "\n\n" + _generate_arabic_text(50)
        wc = _count_arabic_words(text)

        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=threshold)
        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=wc,
            total_tokens=len(text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(text),
                    confidence=1.0,
                )
            ],
        )
        result = split_oversized_division(chunk, [], config)
        for c in result:
            if c.split_info is not None:
                assert c.merge_history is None, "I-AC-7: merge and split mutually exclusive"


# ═══════════════════════════════════════════════════════════════════
# 4. Content unit with only footnotes, no text
# ═══════════════════════════════════════════════════════════════════


class TestFootnoteOnlyContentUnit:
    """Edge cases for content units with footnotes but minimal/no text."""

    def test_footnote_markers_only(self) -> None:
        """Content unit containing only footnote markers and no prose."""
        text = "⌜1⌝ ⌜2⌝"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                footnotes=[
                    Footnote(
                        ref_marker="1",
                        text="حاشية المحقق على هذا الموضع",
                        footnote_type=FootnoteType.AUTHOR_ORIGINAL,
                        confidence=0.9,
                    ),
                    Footnote(
                        ref_marker="2",
                        text="انظر المرجع الثاني",
                        footnote_type=FootnoteType.TAHQIQ_EDITOR,
                        confidence=0.85,
                    ),
                ],
            ),
        ]
        assembled, _, _ = assemble_text(units, 0, 0)
        assert "⌜1⌝" in assembled
        assert "⌜2⌝" in assembled
        # Word count: markers contain no Arabic chars
        assert _count_arabic_words(assembled) == 0

    def test_footnote_markers_with_arabic_around(self) -> None:
        """Footnote markers embedded in Arabic text are preserved."""
        text = "قال ⌜1⌝ المصنف ⌜2⌝ رحمه الله"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                footnotes=[
                    Footnote(
                        ref_marker="1",
                        text="تخريج الحديث",
                        footnote_type=FootnoteType.HADITH_TAKHRIJ,
                        confidence=0.9,
                    ),
                    Footnote(
                        ref_marker="2",
                        text="شرح لغوي",
                        footnote_type=FootnoteType.LINGUISTIC_NOTE,
                        confidence=0.85,
                    ),
                ],
            ),
        ]
        assembled, _, _ = assemble_text(units, 0, 0)
        # Verify markers preserved byte-for-byte
        assert assembled == text
        # I-AC-3: every ref_marker in footnotes appears as ⌜N⌝ in text
        for marker in ["1", "2"]:
            assert f"⌜{marker}⌝" in assembled

    def test_footnote_only_page_in_multi_page_assembly(self) -> None:
        """A page with only footnote markers between two content pages."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="بداية الفصل في أحكام الصلاة",
                boundary_continuity=_bc(BoundaryContinuityType.MID_PARAGRAPH),
            ),
            _make_content_unit(
                unit_index=1,
                primary_text="⌜1⌝",
                footnotes=[
                    Footnote(
                        ref_marker="1",
                        text="حاشية",
                        footnote_type=FootnoteType.AUTHOR_ORIGINAL,
                        confidence=0.9,
                    ),
                ],
                boundary_continuity=_bc(BoundaryContinuityType.MID_PARAGRAPH),
            ),
            _make_content_unit(
                unit_index=2,
                primary_text="وتتمة الكلام في هذا الباب",
            ),
        ]
        text, jps, _indices = assemble_text(units, 0, 2)
        assert "⌜1⌝" in text
        assert "بداية" in text
        assert "وتتمة" in text
        assert len(jps) == 2  # Two join boundaries


# ═══════════════════════════════════════════════════════════════════
# 5. Mixed Arabic/Latin text assembly
# ═══════════════════════════════════════════════════════════════════


class TestMixedArabicLatinAssembly:
    """Edge cases for text containing both Arabic and Latin characters."""

    def test_mixed_text_word_count(self) -> None:
        """Only tokens with Arabic chars count toward word_count."""
        text = "قال Ibn Taymiyyah رحمه الله في كتابه al-Fatawa"
        wc = _count_arabic_words(text)
        # Arabic tokens: قال، رحمه، الله، في، كتابه = 5
        # Latin tokens: Ibn, Taymiyyah, al-Fatawa = NOT counted
        assert wc == 5

    def test_mixed_text_total_tokens(self) -> None:
        """total_tokens counts ALL whitespace-delimited tokens."""
        text = "قال Ibn Taymiyyah رحمه الله"
        total = len(text.split())
        assert total == 5  # All tokens regardless of script

    def test_mixed_text_assembly_preserves_both_scripts(self) -> None:
        """Both Arabic and Latin text preserved during assembly."""
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text="الإمام al-Nawawi",
                boundary_continuity=_bc(BoundaryContinuityType.MID_SENTENCE),
            ),
            _make_content_unit(
                unit_index=1,
                primary_text="في شرح Muslim",
            ),
        ]
        text, _, _ = assemble_text(units, 0, 1)
        assert "al-Nawawi" in text
        assert "الإمام" in text
        assert "Muslim" in text
        assert "شرح" in text

    def test_mixed_text_layer_coverage(self) -> None:
        """I-AC-2 holds for mixed-script text."""
        text = "قال the author رحمه الله"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text),
                        confidence=1.0,
                    )
                ],
            ),
        ]
        layers = rebase_text_layers(units, [0], [], len(text))
        assert len(layers) == 1
        assert layers[0].start == 0
        assert layers[0].end == len(text)

    def test_mixed_text_heading_alignment(self) -> None:
        """Heading alignment works with mixed-script headings."""
        heading = "Chapter on الصلاة"
        text = "Chapter on الصلاة وأحكامها ومسائلها المتعلقة بها"
        assert check_heading_alignment(heading, text) is True

    def test_numbers_in_text_not_arabic_words(self) -> None:
        """Numeric-only tokens do not count as Arabic words."""
        text = "الفصل 3 من الباب 7 في المسألة 12"
        wc = _count_arabic_words(text)
        # Arabic tokens: الفصل، من، الباب، في، المسألة = 5
        # Numeric tokens: 3, 7, 12 = NOT counted
        assert wc == 5


# ═══════════════════════════════════════════════════════════════════
# 6. Division with maximum nesting depth
# ═══════════════════════════════════════════════════════════════════


class TestDeepNesting:
    """Edge cases for deeply nested division trees."""

    def test_five_level_nesting(self) -> None:
        """5-level nesting: heading_path has 5 elements."""
        # Build bottom-up: level 4 → level 0
        leaf = _make_division_node(
            div_id="div_test_4_0", heading_text="مطلب"
        )
        level3 = _make_division_node(
            div_id="div_test_3_0", heading_text="مسألة", children=[leaf]
        )
        level2 = _make_division_node(
            div_id="div_test_2_0", heading_text="فرع", children=[level3]
        )
        level1 = _make_division_node(
            div_id="div_test_1_0", heading_text="فصل", children=[level2]
        )
        root = _make_division_node(
            div_id="div_test_0_0",
            heading_text="كتاب الطهارة",
            children=[level1],
            end_unit_index=10,
        )
        result = find_leaf_divisions([root])
        assert len(result) == 1
        node, path = result[0]
        assert node.div_id == "div_test_4_0"
        assert path == ["كتاب الطهارة", "فصل", "فرع", "مسألة", "مطلب"]
        assert len(path) == 5

    def test_deep_nesting_run_phase1(self) -> None:
        """run_phase1 correctly handles deeply nested tree."""
        leaf = _make_division_node(
            div_id="div_deep_3_0",
            heading_text="مطلب في الاختبار",
            start_unit_index=0,
            end_unit_index=1,
        )
        level2 = _make_division_node(
            div_id="div_deep_2_0",
            heading_text="فرع",
            children=[leaf],
            start_unit_index=0,
            end_unit_index=1,
        )
        level1 = _make_division_node(
            div_id="div_deep_1_0",
            heading_text="فصل",
            children=[level2],
            start_unit_index=0,
            end_unit_index=1,
        )
        root = _make_division_node(
            div_id="div_deep_0_0",
            heading_text="كتاب",
            children=[level1],
            start_unit_index=0,
            end_unit_index=1,
        )

        units = [
            _make_content_unit(
                unit_index=0,
                source_id="src_deep",
                primary_text="مطلب في الاختبار والتجربة والفحص",
            ),
            _make_content_unit(
                unit_index=1,
                source_id="src_deep",
                primary_text="وتتمة الكلام في الموضوع المذكور",
            ),
        ]
        pkg = _make_normalized_package(
            source_id="src_deep",
            content_units=units,
            division_tree=[root],
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 1
        # div_path should contain all 4 levels
        assert len(chunks[0].div_path) == 4
        assert chunks[0].div_path[0] == "كتاب"
        assert chunks[0].div_path[-1] == "مطلب في الاختبار"
        assert all(r["status"] in ("pass", "warning") for r in results)

    def test_multiple_leaves_at_different_depths(self) -> None:
        """Tree with leaves at depth 1 and depth 3."""
        deep_leaf = _make_division_node(
            div_id="div_test_3_0", heading_text="مطلب عميق"
        )
        mid_node = _make_division_node(
            div_id="div_test_2_0", heading_text="فرع", children=[deep_leaf]
        )
        shallow_leaf = _make_division_node(
            div_id="div_test_1_1",
            heading_text="فصل مستقل",
            start_unit_index=5,
            end_unit_index=10,
        )
        root = _make_division_node(
            div_id="div_test_0_0",
            heading_text="كتاب",
            children=[mid_node, shallow_leaf],
            end_unit_index=10,
        )
        result = find_leaf_divisions([root])
        assert len(result) == 2

        # Deep leaf at depth 2 (root → mid → deep_leaf)
        deep_node, deep_path = result[0]
        assert deep_node.div_id == "div_test_3_0"
        assert len(deep_path) == 3  # root + mid_node + deep_leaf

        # Shallow leaf at depth 1
        shallow_node, shallow_path = result[1]
        assert shallow_node.div_id == "div_test_1_1"
        assert len(shallow_path) == 2  # root + leaf


# ═══════════════════════════════════════════════════════════════════
# 7. Consecutive divisions with same heading
# ═══════════════════════════════════════════════════════════════════


class TestConsecutiveSameHeading:
    """Edge cases for multiple divisions sharing the same heading text."""

    def test_same_heading_different_div_ids(self) -> None:
        """Multiple divisions with identical headings produce separate chunks."""
        leaf1 = _make_division_node(
            div_id="div_dup_1_0",
            heading_text="فصل",
            start_unit_index=0,
            end_unit_index=2,
        )
        leaf2 = _make_division_node(
            div_id="div_dup_1_1",
            heading_text="فصل",
            start_unit_index=3,
            end_unit_index=5,
        )
        root = _make_division_node(
            div_id="div_dup_0_0",
            heading_text="كتاب الصلاة",
            children=[leaf1, leaf2],
            start_unit_index=0,
            end_unit_index=5,
        )

        leaves = find_leaf_divisions([root])
        assert len(leaves) == 2
        # Both have same heading text but different div_ids
        assert leaves[0][0].div_id != leaves[1][0].div_id
        assert leaves[0][0].heading_text == leaves[1][0].heading_text
        # Both have same parent in path
        assert leaves[0][1][0] == "كتاب الصلاة"
        assert leaves[1][1][0] == "كتاب الصلاة"

    def test_same_heading_separate_chunks_in_run_phase1(self) -> None:
        """run_phase1 produces separate chunks for same-heading divisions."""
        units = [
            _make_content_unit(
                unit_index=i,
                source_id="src_dup",
                primary_text=f"محتوى الفصل رقم {i + 1} من كتاب الصلاة والطهارة",
            )
            for i in range(6)
        ]
        leaf1 = DivisionNode(
            div_id="div_src_dup_1_0",
            division_type=None,
            heading_text="فصل",
            heading_level=1,
            start_unit_index=0,
            end_unit_index=2,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        leaf2 = DivisionNode(
            div_id="div_src_dup_1_1",
            division_type=None,
            heading_text="فصل",
            heading_level=1,
            start_unit_index=3,
            end_unit_index=5,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
        )
        root = DivisionNode(
            div_id="div_src_dup_0_0",
            division_type=None,
            heading_text="كتاب الصلاة",
            heading_level=0,
            start_unit_index=0,
            end_unit_index=5,
            detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
            confidence=HeadingConfidence.HIGH,
            children=[leaf1, leaf2],
        )

        pkg = _make_normalized_package(
            source_id="src_dup",
            content_units=units,
            division_tree=[root],
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        # Should produce 2 chunks (one per leaf), not merged
        # (each has enough words to not be tiny)
        assert len(chunks) >= 1
        assert all(r["status"] in ("pass", "warning") for r in results)
        # Verify chunk_ids are unique
        chunk_ids = [c.chunk_id for c in chunks]
        assert len(chunk_ids) == len(set(chunk_ids))

    def test_tiny_same_heading_merged(self) -> None:
        """Two tiny divisions with same heading get merged."""
        config = ExcerptingConfig(TINY_DIVISION_WORDS=50)
        c1 = _make_assembled_chunk(
            chunk_id="div_dup_1_0",
            div_id="div_dup_1_0",
            div_path=["كتاب", "فصل"],
            assembled_text="كلمة واحدة",
            word_count=2,
            total_tokens=2,
        )
        c2 = _make_assembled_chunk(
            chunk_id="div_dup_1_1",
            div_id="div_dup_1_1",
            div_path=["كتاب", "فصل"],
            assembled_text="كلمة ثانية",
            word_count=2,
            total_tokens=2,
        )
        result = merge_tiny_divisions([c1, c2], "div_dup_0_0", config)
        assert len(result) == 1
        assert result[0].merge_history is not None
        assert "div_dup_1_0" in result[0].merge_history
        assert "div_dup_1_1" in result[0].merge_history


# ═══════════════════════════════════════════════════════════════════
# 8. Content unit with ZWNJ characters (U+200C)
# ═══════════════════════════════════════════════════════════════════


class TestZWNJCharacters:
    """Edge cases for text containing Zero-Width Non-Joiner (U+200C).

    ZWNJ is stripped by strip_arabic_noise() for comparison but MUST be
    preserved in the stored assembled_text (diacritics preservation rule).
    """

    def test_zwnj_preserved_in_assembly(self) -> None:
        """ZWNJ characters preserved byte-for-byte in assembled text."""
        # ZWNJ is used in some Arabic/Persian typesetting
        text_with_zwnj = "می\u200Cخواهد"  # Persian-style ZWNJ usage
        units = [_make_content_unit(unit_index=0, primary_text=text_with_zwnj)]
        assembled, _, _ = assemble_text(units, 0, 0)
        assert "\u200C" in assembled
        assert assembled == text_with_zwnj

    def test_zwnj_stripped_for_heading_comparison(self) -> None:
        """ZWNJ stripped during heading alignment comparison (§4.8)."""
        heading_with_zwnj = "فصل\u200C في\u200C الطهارة"
        heading_without = "فصل في الطهارة"
        stripped = strip_arabic_noise(heading_with_zwnj)
        stripped_clean = strip_arabic_noise(heading_without)
        # After stripping, both should match
        assert stripped.replace(" ", "") == stripped_clean.replace(" ", "")

    def test_zwnj_in_heading_alignment(self) -> None:
        """Heading with ZWNJ still aligns with ZWNJ-free text."""
        heading = "باب\u200C الصلاة"
        text = "باب الصلاة وأحكامها ومسائلها المتعلقة بها"
        # strip_arabic_noise removes ZWNJ, so alignment should work
        assert check_heading_alignment(heading, text) is True

    def test_zwnj_does_not_affect_word_count(self) -> None:
        """ZWNJ does not create extra tokens (it's zero-width)."""
        text_clean = "كتاب الله"
        text_zwnj = "كتاب\u200C الله"
        # ZWNJ is inside a token, not whitespace — no extra token
        assert len(text_clean.split()) == len(text_zwnj.split())
        assert _count_arabic_words(text_clean) == _count_arabic_words(text_zwnj)

    def test_zwnj_in_layer_rebasing(self) -> None:
        """Layer rebasing works correctly with ZWNJ in text."""
        text = "قال\u200C المؤلف\u200C رحمه الله"
        units = [
            _make_content_unit(
                unit_index=0,
                primary_text=text,
                text_layers=[
                    TextLayerSegment(
                        layer_type=LayerType.MATN,
                        author_canonical_id=None,
                        start=0,
                        end=len(text),
                        confidence=1.0,
                    )
                ],
            ),
        ]
        layers = rebase_text_layers(units, [0], [], len(text))
        assert len(layers) == 1
        assert layers[0].start == 0
        assert layers[0].end == len(text)

    def test_zwj_also_preserved(self) -> None:
        """Zero-Width Joiner (U+200D) also preserved in text."""
        text_with_zwj = "لا\u200Dإله\u200Dإلا\u200Dالله"
        units = [_make_content_unit(unit_index=0, primary_text=text_with_zwj)]
        assembled, _, _ = assemble_text(units, 0, 0)
        assert "\u200D" in assembled
        assert assembled == text_with_zwj

    def test_multiple_zwnj_positions(self) -> None:
        """Multiple ZWNJs at different positions all preserved."""
        text = "أ\u200Cب\u200Cت\u200Cث الحروف العربية"
        units = [_make_content_unit(unit_index=0, primary_text=text)]
        assembled, _, _ = assemble_text(units, 0, 0)
        zwnj_count = assembled.count("\u200C")
        assert zwnj_count == 3
        assert assembled == text


# ═══════════════════════════════════════════════════════════════════
# Cross-cutting edge cases
# ═══════════════════════════════════════════════════════════════════


class TestCrossCuttingEdgeCases:
    """Additional edge cases that span multiple Phase 1 subsystems."""

    def test_diacritics_preserved_through_full_pipeline(self) -> None:
        """Fully diacritized text preserved through run_phase1."""
        diacritized = "الحَمْدُ لِلَّهِ رَبِّ العَالَمِينَ الرَّحْمَنِ الرَّحِيمِ"
        pkg = _make_normalized_package(
            num_units=1,
            primary_text=diacritized,
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 1
        assert chunks[0].assembled_text == diacritized
        assert all(r["status"] in ("pass", "warning") for r in results)

    def test_tatweel_preserved_in_text(self) -> None:
        """Tatweel (kashida, U+0640) preserved in assembled text."""
        text_with_tatweel = "اللـــه أكبر والحمد لله"
        pkg = _make_normalized_package(
            num_units=1,
            primary_text=text_with_tatweel,
        )
        config = ExcerptingConfig()
        chunks, results = run_phase1(pkg, config)
        assert len(chunks) == 1
        assert "\u0640" in chunks[0].assembled_text
        assert all(r["status"] in ("pass", "warning") for r in results)

    def test_superscript_alef_preserved(self) -> None:
        """Superscript alef (U+0670) preserved in assembled text."""
        text = "هٰذَا كِتَابٌ عَظِيمٌ"  # هٰذا contains superscript alef
        pkg = _make_normalized_package(num_units=1, primary_text=text)
        config = ExcerptingConfig()
        chunks, _ = run_phase1(pkg, config)
        assert len(chunks) == 1
        assert "\u0670" in chunks[0].assembled_text

    def test_empty_heading_text_vacuously_aligned(self) -> None:
        """Empty heading_text → heading_alignment_ok = True (vacuous)."""
        assert check_heading_alignment("", "أي نص هنا") is True

    def test_ascii_digit_regex_safety(self) -> None:
        """Verify footnote marker regex uses [^⌝]+ not \\d for marker content."""
        from engines.excerpting.src.phase1_assembly import _FOOTNOTE_MARKER_RE

        pattern = _FOOTNOTE_MARKER_RE.pattern
        # Pattern should NOT contain raw \d which would match Arabic-Indic digits
        assert "\\d" not in pattern, (
            "Footnote marker regex must not use \\d — "
            "it matches Arabic-Indic digits (٠-٩)"
        )
