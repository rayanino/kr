"""Boundary-exhaustive tests for frozen, stable excerpting engine thresholds.

Tests every ±1 value around each hard-coded threshold:
- §4.4 Merge: TINY_DIVISION_WORDS = 50  (merge if word_count < 50)
- §4.5 Split: OVERSIZED_DIVISION_WORDS = 5000  (split if word_count > 5000)
- §4.6 Layer gap repair: gap ≤ 5 chars → repair; gap > 5 chars → fatal
- §7.1 F-DET-3 LA-1: dominant layer coverage ≥ 0.80 → LA-1 fires

These tests remain valid for the entire lifetime of the engine — they
test SPEC-defined constants, not implementation details.
"""

from __future__ import annotations

import logging

import pytest

from engines.excerpting.contracts import (
    AssemblyMetadata,
    ExcerptingConfig,
    _count_arabic_words,
)
from engines.excerpting.src.phase1_assembly import (
    merge_tiny_divisions,
    rebase_text_layers,
    split_oversized_division,
)
from engines.excerpting.src.phase3_deterministic import compute_layer_attribution
from engines.excerpting.tests.conftest import _make_assembled_chunk, _make_content_unit
from engines.normalization.contracts import (
    LayerType,
    TextLayerSegment,
)


# ═══════════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════════

_ARABIC_WORDS = [
    "وقال", "المؤلف", "رحمه", "الله", "تعالى",
    "في", "كتابه", "العظيم", "الذي", "صنفه",
]


def _arabic_text(n: int) -> str:
    """Return Arabic text containing exactly n Arabic words (tokens)."""
    if n == 0:
        return "..."  # non-Arabic — zero Arabic word count
    words = (_ARABIC_WORDS * (n // len(_ARABIC_WORDS) + 1))[:n]
    return " ".join(words)


def _arabic_text_paragraphs(n: int, para_size: int = 500) -> str:
    """Return Arabic text with n words split into paragraphs every para_size words.

    Paragraph breaks (double newline) allow the split algorithm to find
    a split point without falling back to sentence-boundary last resort.
    """
    parts: list[str] = []
    remaining = n
    while remaining > 0:
        batch = min(para_size, remaining)
        parts.append(_arabic_text(batch))
        remaining -= batch
    return "\n\n".join(parts)


def _chunk_overrides(word_count: int, *, with_paragraphs: bool = False) -> dict:
    """Build _make_assembled_chunk overrides for an exact word_count."""
    text = (
        _arabic_text_paragraphs(word_count)
        if with_paragraphs
        else _arabic_text(word_count)
    )
    actual_wc = _count_arabic_words(text)
    assert actual_wc == word_count, (
        f"Helper bug: requested {word_count} words, got {actual_wc}"
    )
    return {
        "assembled_text": text,
        "word_count": actual_wc,
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


def _meta() -> AssemblyMetadata:
    """Minimal AssemblyMetadata for layer-attribution tests."""
    return AssemblyMetadata(
        constituent_unit_indices=[0],
        join_points=[],
        layer_split_points=[],
        footnote_renumber_map=None,
    )


# ═══════════════════════════════════════════════════════════════════
# §4.4 — Merge threshold (TINY_DIVISION_WORDS = 50)
# ═══════════════════════════════════════════════════════════════════


class TestMergeThresholdBoundary:
    """Exact boundary tests for §4.4 merge threshold (TINY_DIVISION_WORDS=50).

    The predicate is: merge if word_count < 50
    So 49 → merge, 50 → standalone, 51 → standalone.
    """

    def test_merge_49_words(self) -> None:
        """49 words (< 50) MUST merge with next sibling.

        This is the one below the threshold. The 49-word chunk cannot
        stand alone — it must be merged with its sibling.
        """
        config = ExcerptingConfig()
        c_tiny = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(49),
        )
        sibling_text = _arabic_text(60)
        c_sibling = _make_assembled_chunk(
            chunk_id="div_test_1_1",
            div_id="div_test_1_1",
            assembled_text=sibling_text,
            word_count=_count_arabic_words(sibling_text),
            total_tokens=len(sibling_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(sibling_text),
                    confidence=1.0,
                )
            ],
        )
        result = merge_tiny_divisions([c_tiny, c_sibling], "div_test_0_0", config)
        # 49-word chunk merged into sibling → single combined chunk
        assert len(result) == 1
        assert result[0].merge_history is not None
        assert "div_test_1_0" in result[0].merge_history

    def test_merge_50_words_standalone(self) -> None:
        """Exactly 50 words must NOT merge (≥50 stands alone).

        The threshold is strictly less-than: merge only if word_count < 50.
        A 50-word chunk is at the boundary but is considered non-tiny.
        """
        config = ExcerptingConfig()
        c_at_threshold = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(50),
        )
        sibling_text = _arabic_text(50)
        c_sibling = _make_assembled_chunk(
            chunk_id="div_test_1_1",
            div_id="div_test_1_1",
            assembled_text=sibling_text,
            word_count=_count_arabic_words(sibling_text),
            total_tokens=len(sibling_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(sibling_text),
                    confidence=1.0,
                )
            ],
        )
        result = merge_tiny_divisions(
            [c_at_threshold, c_sibling], "div_test_0_0", config
        )
        # Both at threshold → neither is tiny → both remain separate
        assert len(result) == 2
        assert result[0].merge_history is None
        assert result[1].merge_history is None

    def test_merge_51_words_standalone(self) -> None:
        """51 words (> 50) must NOT merge — it is above the threshold."""
        config = ExcerptingConfig()
        c_above = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(51),
        )
        sibling_text = _arabic_text(51)
        c_sibling = _make_assembled_chunk(
            chunk_id="div_test_1_1",
            div_id="div_test_1_1",
            assembled_text=sibling_text,
            word_count=_count_arabic_words(sibling_text),
            total_tokens=len(sibling_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(sibling_text),
                    confidence=1.0,
                )
            ],
        )
        result = merge_tiny_divisions(
            [c_above, c_sibling], "div_test_0_0", config
        )
        assert len(result) == 2
        assert all(c.merge_history is None for c in result)

    def test_merge_1_word(self) -> None:
        """A single-word chunk (trivially tiny) merges with its sibling."""
        config = ExcerptingConfig()
        c_single = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(1),
        )
        sibling_text = _arabic_text(55)
        c_sibling = _make_assembled_chunk(
            chunk_id="div_test_1_1",
            div_id="div_test_1_1",
            assembled_text=sibling_text,
            word_count=_count_arabic_words(sibling_text),
            total_tokens=len(sibling_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(sibling_text),
                    confidence=1.0,
                )
            ],
        )
        result = merge_tiny_divisions([c_single, c_sibling], "div_test_0_0", config)
        assert len(result) == 1
        assert result[0].merge_history is not None

    def test_merge_0_words_with_sibling(self) -> None:
        """0 Arabic words (only non-Arabic content) triggers merge with sibling.

        V-P1-3 warns on empty chunks. The merge logic (word_count < 50)
        still applies — 0 < 50 → tiny → merged with sibling.
        """
        config = ExcerptingConfig()
        # Non-Arabic text → 0 Arabic word count
        zero_text = "... (title page)"
        c_zero = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            assembled_text=zero_text,
            word_count=0,
            total_tokens=len(zero_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(zero_text),
                    confidence=1.0,
                )
            ],
        )
        sibling_text = _arabic_text(60)
        c_sibling = _make_assembled_chunk(
            chunk_id="div_test_1_1",
            div_id="div_test_1_1",
            assembled_text=sibling_text,
            word_count=_count_arabic_words(sibling_text),
            total_tokens=len(sibling_text.split()),
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=len(sibling_text),
                    confidence=1.0,
                )
            ],
        )
        result = merge_tiny_divisions([c_zero, c_sibling], "div_test_0_0", config)
        # 0 < 50 → treated as tiny → merged with sibling
        assert len(result) == 1
        assert result[0].merge_history is not None


# ═══════════════════════════════════════════════════════════════════
# §4.5 — Split threshold (OVERSIZED_DIVISION_WORDS = 5000)
# ═══════════════════════════════════════════════════════════════════


class TestSplitThresholdBoundary:
    """Exact boundary tests for §4.5 split threshold (OVERSIZED_DIVISION_WORDS=5000).

    The predicate is: split if word_count > 5000
    So 4999 → no split, 5000 → no split, 5001 → split.
    """

    def test_split_4999_words_no_split(self) -> None:
        """4999 words (< 5000) must NOT trigger splitting."""
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(4999),
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) == 1
        assert result[0].split_info is None

    def test_split_5000_words_no_split(self) -> None:
        """Exactly 5000 words must NOT split — threshold is strictly greater-than.

        The SPEC uses > 5000 (not ≥ 5000) as the split predicate.
        A 5000-word chunk is at the limit and is considered non-oversized.
        """
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(5000),
        )
        result = split_oversized_division(chunk, [], config)
        assert len(result) == 1
        assert result[0].split_info is None
        assert result[0].word_count == 5000

    def test_split_5001_words_must_split(self) -> None:
        """5001 words (> 5000) MUST split into exactly 2 chunks.

        This is the one word above the threshold. Each result chunk
        must satisfy word_count ≤ 5000.
        """
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(5001, with_paragraphs=True),
        )
        result = split_oversized_division(chunk, [], config)
        # Must split into ≥ 2 chunks
        assert len(result) >= 2
        # Every result chunk must be within threshold
        for c in result:
            assert c.word_count <= config.OVERSIZED_DIVISION_WORDS, (
                f"Chunk {c.chunk_id} still oversized after split: {c.word_count} words"
            )
        # All result chunks must have split_info set
        for c in result:
            assert c.split_info is not None

    def test_split_10001_words_recursive_three_chunks(self) -> None:
        """10001 words requires recursive splitting into ≥ 3 chunks.

        First split produces two chunks. One of them exceeds 5000 words
        and triggers a second split, yielding ≥ 3 total chunks.
        Each chunk must be ≤ 5000 words (V-P1-4).
        """
        config = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            chunk_id="div_test_1_0",
            div_id="div_test_1_0",
            **_chunk_overrides(10001, with_paragraphs=True),
        )
        result = split_oversized_division(chunk, [], config)
        # Recursive split required → at least 3 chunks
        assert len(result) >= 3
        # V-P1-4: no chunk may exceed the threshold
        for c in result:
            assert c.word_count <= config.OVERSIZED_DIVISION_WORDS, (
                f"Chunk {c.chunk_id} violates V-P1-4: {c.word_count} words"
            )
        # All must carry split_info
        for c in result:
            assert c.split_info is not None


# ═══════════════════════════════════════════════════════════════════
# §7.1 F-DET-3 — LA rule dispatch (80% coverage threshold)
# ═══════════════════════════════════════════════════════════════════


class TestLayerAttributionBoundary:
    """Exact boundary tests for LA-1/LA-2/LA-3 dispatch.

    LA-1 fires when dominant layer coverage ≥ 0.80 (inclusive).
    LA-2 fires when 2 layers present and neither reaches 0.80.
    LA-3 fires when ≥ 3 layers present or dominant < 0.60.

    Uses a 1000-char single-token text ("ا" * 1000) for precise
    fractional coverage without floating-point rounding surprises.
    """

    # ── 1000-char Arabic single-token text for precise coverage math ──
    _UNIT_TEXT = "ا" * 1000  # 1 token, 1000 chars, 1 Arabic word

    def _two_layer_meta(self) -> AssemblyMetadata:
        return _meta()

    def test_la1_at_79_point_9_percent(self) -> None:
        """79.9% coverage (799/1000 chars) must NOT trigger LA-1.

        With 2 layers and dominant coverage = 79.9% < 80%, the cascade
        falls to LA-2 (outermost layer attribution).
        """
        text = self._UNIT_TEXT
        assert len(text) == 1000
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=0,
                end=799,  # 79.9%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=799,
                end=1000,
                confidence=1.0,
            ),
        ]
        result = compute_layer_attribution(text, layers, 0, 0, self._two_layer_meta())
        # 79.9% < 80% → NOT LA-1
        assert result.rule_applied != "LA-1", (
            f"Expected NOT LA-1 at 79.9% coverage, got {result.rule_applied}"
        )
        # 2 layers, neither ≥80% → LA-2
        assert result.rule_applied == "LA-2"

    def test_la1_at_80_point_1_percent(self) -> None:
        """80.1% coverage (801/1000 chars) MUST trigger LA-1.

        Just above the 80% threshold: dominant layer unambiguously wins.
        """
        text = self._UNIT_TEXT
        assert len(text) == 1000
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=0,
                end=801,  # 80.1%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=801,
                end=1000,
                confidence=1.0,
            ),
        ]
        result = compute_layer_attribution(text, layers, 0, 0, self._two_layer_meta())
        assert result.rule_applied == "LA-1", (
            f"Expected LA-1 at 80.1% coverage, got {result.rule_applied}"
        )
        assert abs(result.coverage_pct - 0.801) < 0.001

    def test_la_two_layers_each_50_percent(self) -> None:
        """50%/50% split across two layers → LA-3 (H-7: dominant <60%).

        Neither layer dominates (both at exactly 50% < 60%).
        H-7: 2-layer cases with dominant <60% route to LA-3 for consensus.
        """
        text = self._UNIT_TEXT
        layers = [
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=0,
                end=500,  # 50%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=500,
                end=1000,  # 50%
                confidence=1.0,
            ),
        ]
        result = compute_layer_attribution(text, layers, 0, 0, self._two_layer_meta())
        # 50% < 60% → H-7 routes to LA-3 (attribution ambiguous)
        assert result.rule_applied == "LA-3", (
            f"Expected LA-3 at 50/50 split (H-7: dominant <60%), got {result.rule_applied}"
        )

    def test_la_three_layers_each_33_percent(self) -> None:
        """Three layers at ~33% each → LA-3 (ambiguous attribution).

        No layer reaches 80%. Three layers are present.
        §6.2 LA-3: three or more layers → EX-M-001, flag for consensus.
        """
        text = "ا" * 900  # 900 chars, divisible by 3
        layers = [
            TextLayerSegment(
                layer_type=LayerType.MATN,
                author_canonical_id="sch_m",
                start=0,
                end=300,  # 33.3%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.SHARH,
                author_canonical_id="sch_s",
                start=300,
                end=600,  # 33.3%
                confidence=1.0,
            ),
            TextLayerSegment(
                layer_type=LayerType.HASHIYAH,
                author_canonical_id="sch_h",
                start=600,
                end=900,  # 33.3%
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
        # 3 layers, none ≥ 80% → LA-3
        assert result.rule_applied == "LA-3", (
            f"Expected LA-3 for 3-layer 33%/33%/34%, got {result.rule_applied}"
        )


# ═══════════════════════════════════════════════════════════════════
# §4.6 — Layer gap repair (threshold: gap ≤ 5 chars repaired, > 5 fatal)
# ═══════════════════════════════════════════════════════════════════


class TestLayerGapRepairBoundary:
    """Exact boundary tests for §4.6 layer gap repair.

    EX-A-003 repair rule: gap ≤ 5 chars → extend preceding segment (WARNING).
    Gap > 5 chars → not repaired → validate_layer_coverage raises I-AC-2 (FATAL).

    Existing tests use gap=2 (repaired) and gap=10 (fatal).
    This class tests the exact boundary values: 4, 5, 6.
    """

    def _make_gapped_unit(self, text: str, gap_start: int, gap_size: int):
        """Return a ContentUnit whose two text layers have a gap of gap_size chars."""
        gap_end = gap_start + gap_size
        assert gap_end < len(text), "Gap must be within text bounds"
        return _make_content_unit(
            unit_index=0,
            primary_text=text,
            text_layers=[
                TextLayerSegment(
                    layer_type=LayerType.MATN,
                    author_canonical_id=None,
                    start=0,
                    end=gap_start,
                    confidence=1.0,
                ),
                TextLayerSegment(
                    layer_type=LayerType.SHARH,
                    author_canonical_id=None,
                    start=gap_end,  # Gap of exactly gap_size chars
                    end=len(text),
                    confidence=1.0,
                ),
            ],
        )

    def test_layer_gap_4_chars_repaired(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """4-char gap (< 5) → auto-repair, EX-A-003 WARNING emitted.

        Gap of 4 is comfortably within the ≤5 repair range.
        The preceding segment must be extended by 4 chars.
        """
        # Text long enough to have a 4-char gap mid-way
        text = "بسم الله الرحمن الرحيم وبعد فهذا كتاب"  # 38+ chars
        assert len(text) >= 20, "Test text must be long enough for gap"
        gap_start = 5  # End of first segment
        gap_size = 4
        unit = self._make_gapped_unit(text, gap_start, gap_size)

        with caplog.at_level(logging.WARNING):
            result = rebase_text_layers([unit], [0], [], len(text))

        # Repair: preceding segment extended from gap_start to gap_start+4
        assert result[0].end == gap_start + gap_size, (
            f"Expected gap repaired to end={gap_start + gap_size}, "
            f"got end={result[0].end}"
        )
        # EX-A-003 warning must be emitted
        assert any("EX-A-003" in rec.message for rec in caplog.records), (
            "Expected EX-A-003 warning for 4-char gap"
        )

    def test_layer_gap_5_chars_repaired(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """5-char gap (= 5) → auto-repair, EX-A-003 WARNING emitted.

        This is the exact boundary value. Gap of 5 is the maximum
        repairable gap (≤ 5 rule).
        """
        text = "بسم الله الرحمن الرحيم وبعد فهذا كتاب"
        gap_start = 5
        gap_size = 5  # Exactly at the boundary
        unit = self._make_gapped_unit(text, gap_start, gap_size)

        with caplog.at_level(logging.WARNING):
            result = rebase_text_layers([unit], [0], [], len(text))

        # Repair: preceding segment extended by 5 chars
        assert result[0].end == gap_start + gap_size, (
            f"Expected gap repaired to end={gap_start + gap_size}, "
            f"got end={result[0].end}"
        )
        # EX-A-003 warning must be emitted
        assert any("EX-A-003" in rec.message for rec in caplog.records), (
            "Expected EX-A-003 warning for 5-char gap (boundary)"
        )

    def test_layer_gap_6_chars_fatal(self) -> None:
        """6-char gap (> 5) → NOT repaired → validate_layer_coverage raises I-AC-2.

        One char above the repair boundary. This gap is too large to be
        attributed to rounding error, so the engine treats it as a FATAL
        layer coverage failure (I-AC-2 invariant violation).
        """
        text = "بسم الله الرحمن الرحيم وبعد فهذا كتاب"
        gap_start = 5
        gap_size = 6  # One above the repair boundary
        unit = self._make_gapped_unit(text, gap_start, gap_size)

        with pytest.raises(ValueError, match="I-AC-2"):
            rebase_text_layers([unit], [0], [], len(text))
