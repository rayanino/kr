"""Tests for §4.4 — Tiny division merging."""

from __future__ import annotations

from engines.excerpting.contracts import ExcerptingConfig, _count_arabic_words
from engines.excerpting.src.phase1_assembly import merge_tiny_divisions
from engines.excerpting.tests.conftest import _make_assembled_chunk


def _tiny_chunk(div_id: str, word_count: int = 10) -> dict:
    """Build overrides for a tiny chunk with specified word count."""
    # Generate Arabic text with the specified word count
    words = ["كتاب", "الله", "العظيم", "في", "الفقه", "والأصول", "والنحو", "والصرف", "والبلاغة", "والمنطق"]
    text = " ".join(words[:word_count] if word_count <= len(words) else words * (word_count // len(words) + 1))
    text = " ".join(text.split()[:word_count])
    return {
        "chunk_id": div_id,
        "div_id": div_id,
        "div_path": [f"باب {div_id}"],
        "assembled_text": text,
        "word_count": _count_arabic_words(text),
        "total_tokens": len(text.split()),
    }


class TestMergeTinyDivisions:
    """Tests for merge_tiny_divisions (§4.4)."""

    def test_merge_two_tiny(self) -> None:
        """Adjacent <50-word siblings merged with '\\n\\n' separator."""
        config = ExcerptingConfig()
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        assert len(result) == 1
        assert "\n\n" in result[0].assembled_text

    def test_merge_chain(self) -> None:
        """Three consecutive tiny → one chunk after recursive merging."""
        config = ExcerptingConfig()
        chunks = [
            _make_assembled_chunk(**_tiny_chunk(f"div_test_1_{i}", 10))
            for i in range(3)
        ]
        result = merge_tiny_divisions(chunks, "div_test_0_0", config)
        assert len(result) == 1

    def test_size_guard(self) -> None:
        """Merge blocked if combined > OVERSIZED_DIVISION_WORDS."""
        config = ExcerptingConfig(TINY_DIVISION_WORDS=50, OVERSIZED_DIVISION_WORDS=15)
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        # Combined would be ~20, exceeding oversized=15 → merge blocked
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        assert len(result) == 2  # Both left as-is

    def test_only_child(self) -> None:
        """No siblings → process as-is regardless of size."""
        config = ExcerptingConfig()
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 5))
        result = merge_tiny_divisions([c1], "div_test_0_0", config)
        assert len(result) == 1
        assert result[0].merge_history is None  # No merge occurred

    def test_merge_history(self) -> None:
        """I-AC-6: ≥2 entries, first = div_id."""
        config = ExcerptingConfig()
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        merged = result[0]
        assert merged.merge_history is not None
        assert len(merged.merge_history) >= 2
        assert merged.merge_history[0] == merged.div_id

    def test_merge_keeps_div_path(self) -> None:
        """Merged chunk has first division's div_path."""
        config = ExcerptingConfig()
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        assert result[0].div_path == c1.div_path

    def test_i_ac_7_no_merge_split(self) -> None:
        """Merge and split never both present (I-AC-7)."""
        config = ExcerptingConfig()
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        for chunk in result:
            assert not (
                chunk.merge_history is not None and chunk.split_info is not None
            ), "I-AC-7 violated: both merge_history and split_info present"

    def test_non_tiny_untouched(self) -> None:
        """Chunks above threshold are not merged."""
        config = ExcerptingConfig(TINY_DIVISION_WORDS=5)
        c1 = _make_assembled_chunk(**_tiny_chunk("div_test_1_0", 10))
        c2 = _make_assembled_chunk(**_tiny_chunk("div_test_1_1", 10))
        result = merge_tiny_divisions([c1, c2], "div_test_0_0", config)
        assert len(result) == 2  # Both above threshold, untouched
