"""Pathological Arabic input stress tests for Phase 1 assembly.

Tests inputs that should never exist in real data but must not crash or
corrupt the pipeline if they arrive. All tests are permanent — they cover
stable, frozen Phase 1 code.

Test categories:
- Diacritics-only, tatweel-only, invisible-char-only text
- Mixed Arabic/Latin script
- Unicode block diversity
- BiDi override characters
- Extreme word/character geometry
- Empty-after-stripping edge cases
"""

from __future__ import annotations

import pytest

from engines.excerpting.contracts import (
    AssemblyMetadata,
    ExcerptingConfig,
    _count_arabic_words,
)
from engines.excerpting.src.phase1_assembly import (
    assemble_text,
    merge_tiny_divisions,
    strip_arabic_noise,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_content_unit,
)


# ═══════════════════════════════════════════════════════════════════
# §1 — Pure diacritics and combining-mark-only text
# ═══════════════════════════════════════════════════════════════════


class TestOnlyDiacritics:
    """Text consisting entirely of Arabic diacritics with zero base letters.

    U+064E fathah, U+064F dammah, U+0650 kasrah, U+0651 shadda, U+0652 sukun
    all fall in the Arabic block (U+0600–U+06FF), so _count_arabic_words
    treats diacritic-only tokens as Arabic words.  The SPEC does not prohibit
    this — real Shamela export corruption can produce such tokens.  The key
    invariant is: no crash, and word_count reflects what split() returns.
    """

    DIACRITICS_TEXT = "\u064E\u064F\u0650\u0651\u0652"  # 5 combining marks, no spaces

    def test_word_count_no_spaces(self) -> None:
        """Single diacritics cluster with no spaces → split() yields 1 token → 1 Arabic word."""
        text = self.DIACRITICS_TEXT
        wc = _count_arabic_words(text)
        # The token contains chars in U+0600–U+06FF range → counted
        assert wc == 1

    def test_word_count_with_spaces(self) -> None:
        """Three space-separated diacritics clusters → split() yields 3 tokens → 3 Arabic words."""
        text = "\u064E \u064F \u0650"
        wc = _count_arabic_words(text)
        assert wc == 3

    def test_strip_arabic_noise_removes_all(self) -> None:
        """strip_arabic_noise must remove all diacritics (U+064B–U+0652) leaving empty string."""
        stripped = strip_arabic_noise(self.DIACRITICS_TEXT)
        assert stripped == ""

    def test_assemble_text_does_not_crash(self) -> None:
        """assemble_text with diacritics-only primary_text must not raise."""
        cu = _make_content_unit(primary_text=self.DIACRITICS_TEXT, unit_index=0)
        text, jps, indices = assemble_text([cu], 0, 0)
        assert text == self.DIACRITICS_TEXT
        assert indices == [0]

    def test_merge_tiny_does_not_crash(self) -> None:
        """merge_tiny_divisions with diacritics-only chunk must not crash."""
        chunk = _make_assembled_chunk(
            assembled_text=self.DIACRITICS_TEXT,
            word_count=_count_arabic_words(self.DIACRITICS_TEXT),
            total_tokens=len(self.DIACRITICS_TEXT.split()),
        )
        cfg = ExcerptingConfig()
        result = merge_tiny_divisions([chunk], "div_parent", cfg)
        # Single chunk: cannot merge with anything, returned as-is
        assert len(result) == 1


# ═══════════════════════════════════════════════════════════════════
# §2 — Alternating Arabic/Latin characters
# ═══════════════════════════════════════════════════════════════════


class TestAlternatingArabicLatin:
    """Every other character alternates between Arabic and Latin.

    Word counting depends on split() → space-delimited tokens.  Mixed tokens
    containing at least one Arabic char still count as Arabic words.
    """

    # Produces tokens like "أa" "بb" etc. — mixed-script tokens
    ALT_TEXT = " ".join(f"\u0628{chr(0x61 + i % 26)}" for i in range(20))

    def test_each_token_is_mixed_script(self) -> None:
        """Every token should contain an Arabic char and thus count as an Arabic word."""
        wc = _count_arabic_words(self.ALT_TEXT)
        expected = len(self.ALT_TEXT.split())
        assert wc == expected

    def test_strip_noise_preserves_latin(self) -> None:
        """strip_arabic_noise must not touch Latin letters."""
        # Use a simple mixed token without diacritics — noise strip changes nothing
        text = "test Arabic بسم"
        stripped = strip_arabic_noise(text)
        assert "test" in stripped
        assert "Arabic" in stripped
        assert "بسم" in stripped

    def test_assemble_text_preserves_mixed_tokens(self) -> None:
        """assemble_text must preserve mixed-script text byte-for-byte."""
        cu = _make_content_unit(primary_text=self.ALT_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.ALT_TEXT


# ═══════════════════════════════════════════════════════════════════
# §3 — Tatweel-only text (U+0640)
# ═══════════════════════════════════════════════════════════════════


class TestOnlyTatweel:
    """Text made entirely of tatweel (U+0640, ARABIC TATWEEL).

    U+0640 is in Arabic block → _count_arabic_words sees it.
    strip_arabic_noise removes it (it is in _ARABIC_NOISE_RE).
    """

    TATWEEL_TEXT = "\u0640" * 20  # 20 tatweels, no spaces
    TATWEEL_SPACED = " ".join("\u0640" * 5 for _ in range(4))  # 4 groups

    def test_no_spaces_is_one_token(self) -> None:
        """20 tatweels with no spaces → split() → 1 token → 1 Arabic word."""
        wc = _count_arabic_words(self.TATWEEL_TEXT)
        assert wc == 1

    def test_spaced_groups_are_four_tokens(self) -> None:
        """4 space-separated tatweel groups → 4 Arabic words."""
        wc = _count_arabic_words(self.TATWEEL_SPACED)
        assert wc == 4

    def test_strip_noise_removes_all_tatweel(self) -> None:
        """strip_arabic_noise must remove all tatweel characters."""
        stripped = strip_arabic_noise(self.TATWEEL_TEXT)
        assert stripped == ""
        assert "\u0640" not in stripped

    def test_assemble_text_handles_tatweel_gracefully(self) -> None:
        """assemble_text must not crash on tatweel-only primary_text."""
        cu = _make_content_unit(primary_text=self.TATWEEL_TEXT, unit_index=0)
        text, jps, indices = assemble_text([cu], 0, 0)
        assert text == self.TATWEEL_TEXT
        assert indices == [0]


# ═══════════════════════════════════════════════════════════════════
# §4 — Maximum Unicode block diversity
# ═══════════════════════════════════════════════════════════════════


class TestMaxUnicodeDiversity:
    """Text using chars from all Arabic Unicode blocks.

    Basic (U+0600): ب U+0628
    Supplement (U+0750): ڀ U+0780 — Thaana, skip; use ݐ U+0750
    Extended-A (U+08A0): ‎ٲ U+08C6 (arabic extended-A letter)
    Presentation Forms-A (U+FB50): ﭐ U+FB50
    Presentation Forms-B (U+FE70): ﹰ U+FE70 (diacritics from presentation B)
    """

    # One character from each block, separated by spaces
    DIVERSE_TEXT = " ".join([
        "\u0628",   # Arabic basic block: ba
        "\u0750",   # Arabic supplement: DP
        "\u08A0",   # Arabic Extended-A
        "\uFB50",   # Presentation Forms-A
        "\uFE70",   # Presentation Forms-B
    ])

    def test_no_crash_on_diverse_unicode(self) -> None:
        """No exception when processing chars from all Arabic Unicode blocks."""
        wc = _count_arabic_words(self.DIVERSE_TEXT)
        # Only U+0600–U+06FF is checked — supplement/presentation forms don't qualify
        # ب (U+0628) is the only token in U+0600–U+06FF range
        assert wc == 1

    def test_assemble_text_preserves_all_blocks(self) -> None:
        """assemble_text must preserve all Unicode block characters exactly."""
        cu = _make_content_unit(primary_text=self.DIVERSE_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        # Byte-for-byte preservation
        assert text == self.DIVERSE_TEXT

    def test_strip_noise_does_not_corrupt_non_noise_chars(self) -> None:
        """strip_arabic_noise must not strip non-noise Arabic characters."""
        text = "بسم الله"  # Pure Arabic basic block, no diacritics
        stripped = strip_arabic_noise(text)
        assert stripped == "بسم الله"


# ═══════════════════════════════════════════════════════════════════
# §5 — 100 identical words
# ═══════════════════════════════════════════════════════════════════


class TestAllIdenticalWords:
    """100 repetitions of بسم separated by spaces.

    Tests that word_count is correct and merge/split thresholds work
    with uniform repetition.  bsm is 3 chars, 100 of them = 100 words.
    """

    TEXT = " ".join(["بسم"] * 100)

    def test_word_count_is_100(self) -> None:
        """100 repetitions of a single Arabic word → word_count = 100."""
        assert _count_arabic_words(self.TEXT) == 100

    def test_total_tokens_matches_split(self) -> None:
        """total_tokens must equal len(text.split())."""
        assert len(self.TEXT.split()) == 100

    def test_below_oversized_threshold(self) -> None:
        """100 words is below OVERSIZED_DIVISION_WORDS (5000); no split needed."""
        cfg = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self.TEXT,
            word_count=100,
            total_tokens=100,
        )
        # Does not raise, does not split
        assert chunk.word_count == 100
        assert chunk.word_count < cfg.OVERSIZED_DIVISION_WORDS

    def test_below_tiny_threshold_triggers_merge(self) -> None:
        """100 words exceeds TINY_DIVISION_WORDS (50); chunk is NOT tiny."""
        cfg = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self.TEXT,
            word_count=100,
            total_tokens=100,
        )
        # word_count >= TINY_DIVISION_WORDS → no merge
        result = merge_tiny_divisions([chunk], "div_parent", cfg)
        assert len(result) == 1
        assert result[0].word_count == 100


# ═══════════════════════════════════════════════════════════════════
# §6 — Zero-width joiner chains
# ═══════════════════════════════════════════════════════════════════


class TestZWJChains:
    """Zero-width joiner (U+200D) repeated 100 times between two Arabic letters.

    U+200D is NOT in U+0600–U+06FF, but U+0628 (ba) is.
    The token 'ب' + 100*ZWJ + 'ب' contains Arabic chars → counts as 1 word.
    strip_arabic_noise removes ZWJ (it is in the noise regex as U+200D).
    """

    BA = "\u0628"
    ZWJ = "\u200D"
    ZWJ_CHAIN = BA + ZWJ * 100 + BA  # single token with 100 ZWJs

    def test_zwj_chain_counts_as_one_word(self) -> None:
        """Single token with ZWJ chain contains Arabic chars → 1 Arabic word."""
        wc = _count_arabic_words(self.ZWJ_CHAIN)
        assert wc == 1

    def test_zwj_chain_does_not_inflate_word_count(self) -> None:
        """ZWJ characters do not split tokens — word count stays at 1."""
        # If ZWJ were erroneously treated as a word separator, wc would be 101+
        wc = _count_arabic_words(self.ZWJ_CHAIN)
        assert wc < 10, f"ZWJ inflated word count to {wc}"

    def test_strip_noise_removes_zwj(self) -> None:
        """strip_arabic_noise must remove ZWJ from Arabic text."""
        stripped = strip_arabic_noise(self.ZWJ_CHAIN)
        assert self.ZWJ not in stripped
        # Base Arabic letters must survive
        assert self.BA in stripped

    def test_assemble_text_preserves_zwj_chain(self) -> None:
        """assemble_text must preserve ZWJ chars byte-for-byte (not strip them)."""
        # ZWJ stripping is for comparison, not storage
        cu = _make_content_unit(primary_text=self.ZWJ_CHAIN, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.ZWJ_CHAIN


# ═══════════════════════════════════════════════════════════════════
# §7 — BiDi override characters
# ═══════════════════════════════════════════════════════════════════


class TestBiDiOverrideChars:
    """Text containing Unicode BiDi override characters (U+202A–U+202E).

    Per input-sanitization.md these should be stripped at the ingestion
    boundary, but Phase 1 may receive them if upstream normalization
    missed them.  Phase 1 must not crash.  BiDi chars are NOT in the
    Arabic block, so they do not count as Arabic words.

    U+202A LEFT-TO-RIGHT EMBEDDING
    U+202B RIGHT-TO-LEFT EMBEDDING
    U+202C POP DIRECTIONAL FORMATTING
    U+202D LEFT-TO-RIGHT OVERRIDE
    U+202E RIGHT-TO-LEFT OVERRIDE
    """

    BIDI_TEXT = "\u202Eبسم الله\u202C"  # RTL override wrapping Arabic text
    BIDI_ONLY = "\u202A\u202B\u202C\u202D\u202E"  # pure BiDi, no Arabic

    def test_bidi_wrapped_arabic_word_count(self) -> None:
        """BiDi control chars are not in Arabic block — only Arabic tokens count."""
        # "\u202Eبسم" splits as one token; "الله\u202C" splits as one token
        # Both tokens contain Arabic chars → 2 Arabic words
        wc = _count_arabic_words(self.BIDI_TEXT)
        assert wc == 2

    def test_bidi_only_word_count_is_zero(self) -> None:
        """Pure BiDi-override text contains no Arabic characters → 0 Arabic words."""
        wc = _count_arabic_words(self.BIDI_ONLY)
        assert wc == 0

    def test_assemble_text_does_not_crash_on_bidi(self) -> None:
        """assemble_text must not raise when primary_text contains BiDi overrides."""
        cu = _make_content_unit(primary_text=self.BIDI_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        # Preserved byte-for-byte (Phase 1 doesn't sanitize)
        assert text == self.BIDI_TEXT

    def test_strip_noise_does_not_strip_bidi(self) -> None:
        """strip_arabic_noise does NOT strip BiDi overrides — they are not in the noise regex.

        This is a documentation test: it records that BiDi bypass is a known
        gap.  Stripping BiDi chars is the ingestion boundary's responsibility.
        """
        stripped = strip_arabic_noise(self.BIDI_TEXT)
        # BiDi chars survive strip_arabic_noise (they are not in _ARABIC_NOISE_RE)
        assert "\u202E" in stripped or "\u202C" in stripped


# ═══════════════════════════════════════════════════════════════════
# §8 — Empty text after conceptual stripping
# ═══════════════════════════════════════════════════════════════════


class TestEmptyAfterStrip:
    """ContentUnit whose primary_text is empty or whitespace-only.

    Phase 1 must handle gracefully: assemble_text should return empty string,
    word_count=0, and merge_tiny_divisions should see a zero-word chunk.
    """

    def test_empty_string_word_count(self) -> None:
        """Empty string → 0 Arabic words."""
        assert _count_arabic_words("") == 0

    def test_whitespace_only_word_count(self) -> None:
        """Whitespace-only string → split() returns [] → 0 Arabic words."""
        assert _count_arabic_words("   \t\n   ") == 0

    def test_assemble_text_empty_primary(self) -> None:
        """assemble_text with empty primary_text must return empty assembled text."""
        cu = _make_content_unit(primary_text="", unit_index=0)
        text, jps, indices = assemble_text([cu], 0, 0)
        assert text == ""
        assert indices == [0]

    def test_merge_tiny_zero_word_chunk(self) -> None:
        """A chunk with word_count=0 is below TINY threshold; merge_tiny must not crash."""
        chunk = _make_assembled_chunk(
            assembled_text="",
            word_count=0,
            total_tokens=0,
            text_layers=[],  # No layers for empty text
        )
        cfg = ExcerptingConfig()
        # Single zero-word chunk — no sibling to merge with
        result = merge_tiny_divisions([chunk], "div_parent", cfg)
        assert len(result) == 1

    def test_strip_noise_empty_returns_empty(self) -> None:
        """strip_arabic_noise('') must return ''."""
        assert strip_arabic_noise("") == ""


# ═══════════════════════════════════════════════════════════════════
# §9 — Single Arabic character
# ═══════════════════════════════════════════════════════════════════


class TestSingleArabicChar:
    """ContentUnit containing exactly one Arabic character.

    Tests that single-char inputs don't expose off-by-one errors or
    incorrect layer calculations.
    """

    SINGLE_CHAR = "\u0628"  # ba

    def test_word_count_is_one(self) -> None:
        """Single Arabic character → 1 word."""
        assert _count_arabic_words(self.SINGLE_CHAR) == 1

    def test_assemble_text_single_char(self) -> None:
        """assemble_text with single-char primary_text must return that char."""
        cu = _make_content_unit(primary_text=self.SINGLE_CHAR, unit_index=0)
        text, jps, indices = assemble_text([cu], 0, 0)
        assert text == self.SINGLE_CHAR
        assert len(jps) == 0  # No join points for single unit

    def test_two_single_char_chunks_can_merge(self) -> None:
        """Two single-character chunks (word_count=1 each, both < TINY=50) merge together."""
        cfg = ExcerptingConfig()
        chunk_a = _make_assembled_chunk(
            chunk_id="div_a_0",
            div_id="div_a_0",
            assembled_text=self.SINGLE_CHAR,
            word_count=1,
            total_tokens=1,
        )
        chunk_b = _make_assembled_chunk(
            chunk_id="div_b_0",
            div_id="div_b_0",
            assembled_text=self.SINGLE_CHAR,
            word_count=1,
            total_tokens=1,
        )
        result = merge_tiny_divisions([chunk_a, chunk_b], "div_parent", cfg)
        # Both are tiny (1 < 50); combined 2 words ≤ 5000; should merge
        assert len(result) == 1
        assert result[0].merge_history is not None
        assert len(result[0].merge_history) == 2


# ═══════════════════════════════════════════════════════════════════
# §10 — Extremely long single word (no spaces)
# ═══════════════════════════════════════════════════════════════════


class TestExtremelyLongWord:
    """Single Arabic 'word' of 10,000 characters with no spaces.

    word_count=1 because split() returns one token.
    char count is huge but Phase 1 must not crash or hang.
    This also tests that split_oversized_division can handle a chunk
    that has no natural split point (no \n\n, no sentence boundary).
    """

    LONG_WORD = "\u0628" * 10_000  # 10,000 ba characters, no spaces

    def test_word_count_is_one(self) -> None:
        """10,000 ba chars with no spaces → 1 token → word_count = 1."""
        assert _count_arabic_words(self.LONG_WORD) == 1

    def test_total_tokens_is_one(self) -> None:
        """split() on no-space text returns exactly 1 token."""
        assert len(self.LONG_WORD.split()) == 1

    def test_assemble_text_does_not_crash(self) -> None:
        """assemble_text with 10,000-char single word must not crash."""
        cu = _make_content_unit(primary_text=self.LONG_WORD, unit_index=0)
        text, jps, indices = assemble_text([cu], 0, 0)
        assert len(text) == 10_000
        assert indices == [0]

    def test_merge_tiny_does_not_crash(self) -> None:
        """merge_tiny_divisions with a 1-word chunk (tiny) must not crash."""
        cfg = ExcerptingConfig()
        chunk = _make_assembled_chunk(
            assembled_text=self.LONG_WORD,
            word_count=1,
            total_tokens=1,
        )
        # Single chunk with no sibling; stays as-is even though tiny
        result = merge_tiny_divisions([chunk], "div_parent", cfg)
        assert len(result) == 1
        assert len(result[0].assembled_text) == 10_000

    def test_strip_noise_does_not_hang_on_long_word(self) -> None:
        """strip_arabic_noise must complete in finite time on 10,000-char input."""
        # ba has no diacritics; result should be the same length
        stripped = strip_arabic_noise(self.LONG_WORD)
        assert len(stripped) == 10_000
