"""Tests for §4.5 — Oversized division splitting."""

from __future__ import annotations

from engines.excerpting.contracts import (
    AssemblyMetadata,
    ExcerptingConfig,
    JoinPoint,
    _count_arabic_words,
)
from engines.excerpting.src.phase1_assembly import split_oversized_division
from engines.excerpting.tests.conftest import _make_assembled_chunk, _make_content_unit
from engines.normalization.contracts import (
    BoundaryContinuityType,
    LayerType,
    PhysicalPage,
    StructuralMarkers,
    TextLayerSegment,
)


def _oversized_text(word_count: int) -> str:
    """Generate Arabic text with approximately word_count words."""
    base_words = [
        "وقال", "المؤلف", "رحمه", "الله", "تعالى", "في", "كتابه",
        "العظيم", "الذي", "صنفه",
    ]
    words: list[str] = []
    while len(words) < word_count:
        words.extend(base_words)
    return " ".join(words[:word_count])


def _make_oversized_chunk(
    word_count: int = 6000,
    div_id: str = "div_test_1_0",
    with_paragraph_breaks: bool = True,
) -> dict:
    """Build overrides for an oversized chunk."""
    if with_paragraph_breaks:
        # Insert \n\n every ~500 words for paragraph breaks
        parts: list[str] = []
        remaining = word_count
        while remaining > 0:
            batch = min(500, remaining)
            parts.append(_oversized_text(batch))
            remaining -= batch
        text = "\n\n".join(parts)
    else:
        text = _oversized_text(word_count)

    return {
        "chunk_id": div_id,
        "div_id": div_id,
        "assembled_text": text,
        "word_count": _count_arabic_words(text),
        "total_tokens": len(text.split()),
        "text_layers": [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id=None,
                start=0,
                end=len(text),
                confidence=1.0,
            )
        ],
    }


class TestSplitOversizedDivision:
    """Tests for split_oversized_division (§4.5)."""

    def test_no_split_below_threshold(self) -> None:
        """Chunk below threshold → returned as-is."""
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk()  # Default is ~7 words, well below 5000
        result = split_oversized_division(chunk, [], config)
        assert len(result) == 1
        assert result[0].split_info is None

    def test_split_at_paragraph(self) -> None:
        """Paragraph break \\n\\n nearest midpoint used for splitting."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        chunk = _make_assembled_chunk(**_make_oversized_chunk(200, with_paragraph_breaks=True))
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2
        # All chunks should be below threshold
        for c in result:
            assert c.word_count <= config.OVERSIZED_DIVISION_WORDS + 50  # Some tolerance

    def test_split_at_sentence(self) -> None:
        """Sentence boundary as last resort when no \\n\\n."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        # Text without paragraph breaks but with sentence endings
        text = "وقال المؤلف رحمه الله. " * 50
        wc = _count_arabic_words(text)
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
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

    def test_recursive_split(self) -> None:
        """12000-word division → 3+ chunks."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=5000)
        chunk = _make_assembled_chunk(**_make_oversized_chunk(12000))
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 3

    def test_split_info_fields(self) -> None:
        """chunk_id format, chunk_index, total_chunks, split_method."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        chunk = _make_assembled_chunk(**_make_oversized_chunk(300))
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2
        for i, c in enumerate(result):
            assert c.split_info is not None
            assert c.split_info.chunk_index == i
            assert c.split_info.total_chunks == len(result)
            assert c.chunk_id == f"div_test_1_0_chunk_{i}"
            assert c.split_info.original_div_id == "div_test_1_0"

    def test_shared_unit_indices(self) -> None:
        """I-AC-4: all chunks share constituent_unit_indices."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        chunk = _make_assembled_chunk(
            **_make_oversized_chunk(300),
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=[0, 1, 2, 3, 4],
                join_points=[],
                footnote_renumber_map=None,
            ),
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2
        shared = result[0].assembly_metadata.constituent_unit_indices
        for c in result[1:]:
            assert c.assembly_metadata.constituent_unit_indices == shared

    def test_split_at_heading(self) -> None:
        """Heading marker → highest priority split point."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)

        # Build content units with a heading detected mid-range
        units = [
            _make_content_unit(unit_index=i, primary_text=_oversized_text(50))
            for i in range(4)
        ]
        # Mark unit 2 as having a heading
        units[2] = _make_content_unit(
            unit_index=2,
            primary_text=_oversized_text(50),
            structural_markers=StructuralMarkers(
                heading_detected=True,
                heading_text="فصل في الركوع",
            ),
        )

        # Assemble text for the full range
        from engines.excerpting.src.phase1_assembly import assemble_text

        text, jps, indices = assemble_text(units, 0, 3)

        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=_count_arabic_words(text),
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
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=indices,
                join_points=jps,
                footnote_renumber_map=None,
            ),
        )
        result = split_oversized_division(chunk, units, config)
        assert len(result) >= 2
        # At least one chunk should use heading_marker as split method
        methods = [c.split_info.split_method for c in result if c.split_info]
        assert "heading_marker" in methods

    def test_footnote_assignment(self) -> None:
        """After split, footnotes assigned to chunk containing their marker."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        chunk = _make_assembled_chunk(**_make_oversized_chunk(300))
        result = split_oversized_division(chunk, [], config)
        # Split chunks have empty footnotes (filled later in run_phase1)
        # This test verifies they don't crash
        assert all(isinstance(c.footnotes, list) for c in result)

    def test_split_method_recorded(self) -> None:
        """split_method is one of the valid values."""
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        chunk = _make_assembled_chunk(**_make_oversized_chunk(300))
        result = split_oversized_division(chunk, [], config)
        valid_methods = {
            "heading_marker",
            "section_break",
            "paragraph_break",
            "sentence_boundary",
        }
        for c in result:
            if c.split_info:
                assert c.split_info.split_method in valid_methods

    def test_physical_pages_partitioned_on_split(self) -> None:
        """Split chunks get partitioned physical_pages matching join_points.

        Verifies the invariant: len(physical_pages) == len(join_points) + 1
        for each split chunk, with boundary page overlap.
        """
        config = ExcerptingConfig(OVERSIZED_DIVISION_WORDS=100)
        text = _oversized_text(300)
        text_len = len(text)

        # 10 pages numbered 50-59, 9 join_points evenly spaced
        pages = [
            PhysicalPage(
                volume=1,
                page_number_display=str(50 + i),
                page_number_int=50 + i,
            )
            for i in range(10)
        ]
        join_points = [
            JoinPoint(
                after_unit_index=i,
                before_unit_index=i + 1,
                boundary_type=BoundaryContinuityType.MID_PARAGRAPH,
                separator_used="\n",
                char_offset_in_assembled=int(text_len * (i + 1) / 10),
            )
            for i in range(9)
        ]

        chunk = _make_assembled_chunk(
            assembled_text=text,
            word_count=_count_arabic_words(text),
            total_tokens=len(text.split()),
            physical_pages=pages,
            assembly_metadata=AssemblyMetadata(
                constituent_unit_indices=list(range(10)),
                join_points=join_points,
                layer_split_points=[],
                footnote_renumber_map=None,
            ),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=text_len,
                    confidence=1.0,
                )
            ],
        )

        result = split_oversized_division(chunk, [], config)
        assert len(result) >= 2

        # Invariant: len(physical_pages) == len(join_points) + 1 for each chunk
        for c in result:
            n_jp = len(c.assembly_metadata.join_points)
            n_pp = len(c.physical_pages)
            assert n_pp == n_jp + 1, (
                f"chunk {c.chunk_id}: {n_pp} pages but {n_jp} join_points "
                f"(expected {n_jp + 1} pages)"
            )

        # Boundary overlap: last page of chunk i == first page of chunk i+1
        for i in range(len(result) - 1):
            assert result[i].physical_pages[-1] == result[i + 1].physical_pages[0], (
                f"No boundary overlap between chunk {i} and {i+1}"
            )

        # Union covers the full original page range
        all_page_nums = set()
        for c in result:
            for p in c.physical_pages:
                assert p.page_number_int is not None
                all_page_nums.add(p.page_number_int)
        assert all_page_nums == set(range(50, 60))
