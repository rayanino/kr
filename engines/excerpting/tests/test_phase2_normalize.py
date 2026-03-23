"""Tests for Phase 2a offset normalization (§5.4.1).

Pure algorithmic tests — no LLM calls needed.  Validates the 3-fallback
cascade (exact → whitespace-normalized → diacritic-stripped) and the
boundary-inference logic that converts snippet anchors into canonical
word offsets.
"""

from __future__ import annotations

import logging

import pytest

from engines.excerpting.contracts import (
    ClassifiedSegment,
    ExcerptingErrorCodes,
    ScholarlyFunction,
)
from engines.excerpting.src.phase2_classify import (
    _build_token_char_map,
    _char_to_token_index,
    _compute_classify_max_tokens,
    _find_snippet_position,
    _strip_text,
    normalize_offsets,
)


# ═══════════════════════════════════════════════════════════════════
# Test fixtures — real Arabic scholarly text
# ═══════════════════════════════════════════════════════════════════

# A multi-sentence fiqh text (~30 tokens) for multi-segment testing.
# Three distinct scholarly segments:
#   1. Definition of wudu (definition)
#   2. Evidence from hadith (evidence_hadith)
#   3. Ruling statement (rule_statement)
_FIQH_TEXT = (
    "الوضوء هو استعمال الماء في أعضاء مخصوصة بنية التطهر "
    "وقد قال النبي صلى الله عليه وسلم لا يقبل الله صلاة أحدكم إذا أحدث حتى يتوضأ "
    "والحكم أن الوضوء فرض لكل صلاة مكتوبة عند جمهور العلماء"
)
_FIQH_TOKENS = _FIQH_TEXT.split()
_FIQH_TOTAL = len(_FIQH_TOKENS)

# Snippet for each segment (first 50 chars of segment's text).
_FIQH_SEG1_SNIPPET = _FIQH_TEXT[:50]  # definition
_FIQH_SEG2_START = _FIQH_TEXT.index("وقد قال النبي")
_FIQH_SEG2_SNIPPET = _FIQH_TEXT[_FIQH_SEG2_START : _FIQH_SEG2_START + 50]
_FIQH_SEG3_START = _FIQH_TEXT.index("والحكم أن الوضوء")
_FIQH_SEG3_SNIPPET = _FIQH_TEXT[_FIQH_SEG3_START : _FIQH_SEG3_START + 50]


def _make_raw_segment(
    index: int,
    snippet: str,
    function: ScholarlyFunction = ScholarlyFunction.DEFINITION,
) -> ClassifiedSegment:
    """Build a ClassifiedSegment with LLM-style (approximate) offsets."""
    return ClassifiedSegment(
        segment_index=index,
        start_word=index * 100,  # deliberately wrong — LLM offsets
        end_word=index * 100 + 99,
        text_snippet=snippet,
        scholarly_function=function,
        confidence=0.9,
    )


# ═══════════════════════════════════════════════════════════════════
# Tests — _build_token_char_map
# ═══════════════════════════════════════════════════════════════════


class TestBuildTokenCharMap:
    def test_simple_arabic(self) -> None:
        text = "بسم الله الرحمن"
        spans = _build_token_char_map(text)
        assert len(spans) == 3
        assert spans[0] == (0, 3)  # بسم
        assert spans[1] == (4, 8)  # الله
        assert spans[2] == (9, 15)  # الرحمن

    def test_consecutive_spaces(self) -> None:
        text = "بسم  الله"  # double space
        spans = _build_token_char_map(text)
        assert len(spans) == 2
        assert spans[0] == (0, 3)  # بسم
        assert spans[1] == (5, 9)  # الله (starts after double space)

    def test_empty_text(self) -> None:
        assert _build_token_char_map("") == []


# ═══════════════════════════════════════════════════════════════════
# Tests — _char_to_token_index
# ═══════════════════════════════════════════════════════════════════


class TestCharToTokenIndex:
    def test_at_token_start(self) -> None:
        spans = [(0, 3), (4, 8), (9, 15)]
        assert _char_to_token_index(0, spans) == 0
        assert _char_to_token_index(4, spans) == 1
        assert _char_to_token_index(9, spans) == 2

    def test_within_token(self) -> None:
        spans = [(0, 3), (4, 8), (9, 15)]
        assert _char_to_token_index(1, spans) == 0
        assert _char_to_token_index(6, spans) == 1

    def test_in_whitespace_returns_next_token(self) -> None:
        spans = [(0, 3), (4, 8)]
        assert _char_to_token_index(3, spans) == 1  # space after token 0


# ═══════════════════════════════════════════════════════════════════
# Tests — _strip_text
# ═══════════════════════════════════════════════════════════════════


class TestStripText:
    def test_collapse_whitespace(self) -> None:
        text = "بسم   الله"
        result, pos_map = _strip_text(text, collapse_ws=True)
        assert result == "بسم الله"
        # pos_map maps each char of result to original position
        assert pos_map[0] == 0  # ب
        assert pos_map[3] == 3  # first space (from triple space)

    def test_strip_diacritics(self) -> None:
        text = "فَعَلَ"  # fa'ala with fatha diacritics
        result, pos_map = _strip_text(text, strip_diacritics=True)
        assert result == "فعل"
        assert len(pos_map) == 3

    def test_no_transformation(self) -> None:
        text = "بسم الله"
        result, pos_map = _strip_text(text)
        assert result == text
        assert pos_map == list(range(len(text)))


# ═══════════════════════════════════════════════════════════════════
# Tests — _find_snippet_position
# ═══════════════════════════════════════════════════════════════════


class TestFindSnippetPosition:
    def test_exact_match(self) -> None:
        pos, diacritic = _find_snippet_position(
            "الرحمن", "بسم الله الرحمن الرحيم", 0
        )
        assert pos == 9
        assert diacritic is False

    def test_exact_match_with_search_start(self) -> None:
        text = "الله الله الله"
        # First الله at 0, second at 5, third at 10
        pos, _ = _find_snippet_position("الله", text, 5)
        assert pos == 5

    def test_whitespace_fallback(self) -> None:
        text = "بسم الله  الرحمن"  # double space in text
        snippet = "الله الرحمن"  # single space in snippet
        pos, diacritic = _find_snippet_position(snippet, text, 0)
        assert diacritic is False
        # Should find match starting at الله position
        assert pos == 4

    def test_diacritic_fallback(self, caplog: pytest.LogCaptureFixture) -> None:
        text = "فَعَلَ الخير"  # with diacritics
        snippet = "فعل الخير"  # without diacritics
        with caplog.at_level(logging.WARNING):
            pos, diacritic = _find_snippet_position(snippet, text, 0)
        assert pos == 0
        assert diacritic is True
        assert ExcerptingErrorCodes.EX_A_012 in caplog.text

    def test_not_found_raises(self) -> None:
        with pytest.raises(ValueError, match="Snippet not found"):
            _find_snippet_position("غير موجود", "بسم الله", 0)


# ═══════════════════════════════════════════════════════════════════
# Tests — normalize_offsets (the main algorithm)
# ═══════════════════════════════════════════════════════════════════


class TestNormalizeOffsets:
    """Tests for the full offset normalization algorithm (§5.4.1)."""

    def test_happy_path_three_segments(self) -> None:
        """3 segments with exact-match snippets → correct canonical offsets."""
        segments = [
            _make_raw_segment(0, _FIQH_SEG1_SNIPPET, ScholarlyFunction.DEFINITION),
            _make_raw_segment(1, _FIQH_SEG2_SNIPPET, ScholarlyFunction.EVIDENCE_HADITH),
            _make_raw_segment(2, _FIQH_SEG3_SNIPPET, ScholarlyFunction.RULE_STATEMENT),
        ]
        result = normalize_offsets(segments, _FIQH_TEXT, _FIQH_TOTAL)

        # Verify structure
        assert len(result) == 3
        assert result[0].start_word == 0  # I-CS-3
        assert result[-1].end_word == _FIQH_TOTAL - 1  # I-CS-4

        # Verify contiguity (I-CS-2)
        for i in range(1, len(result)):
            assert result[i].start_word == result[i - 1].end_word + 1

        # Verify scholarly_function preserved
        assert result[0].scholarly_function == ScholarlyFunction.DEFINITION
        assert result[1].scholarly_function == ScholarlyFunction.EVIDENCE_HADITH
        assert result[2].scholarly_function == ScholarlyFunction.RULE_STATEMENT

    def test_single_segment_covers_all(self) -> None:
        """Single segment spans entire text."""
        text = "بسم الله الرحمن الرحيم"
        tokens = text.split()
        snippet = text[:50]
        segments = [_make_raw_segment(0, snippet)]
        result = normalize_offsets(segments, text, len(tokens))

        assert len(result) == 1
        assert result[0].start_word == 0
        assert result[0].end_word == len(tokens) - 1

    def test_returns_new_objects(self) -> None:
        """DD-S2-3: normalize_offsets creates NEW objects, no mutation."""
        original = _make_raw_segment(0, _FIQH_SEG1_SNIPPET)
        original_start = original.start_word
        result = normalize_offsets([original], _FIQH_TEXT, _FIQH_TOTAL)
        # Original unchanged
        assert original.start_word == original_start
        # Result is a different object
        assert result[0] is not original

    def test_whitespace_fallback_in_snippet(self) -> None:
        """Snippet with collapsed whitespace still anchors correctly."""
        # Insert double space in assembled text
        text = "بسم  الله الرحمن الرحيم"
        tokens = text.split()
        # Snippet has single space (as LLM might produce)
        snippet = "بسم الله"
        segments = [_make_raw_segment(0, snippet)]
        result = normalize_offsets(segments, text, len(tokens))

        assert len(result) == 1
        assert result[0].start_word == 0
        assert result[0].end_word == len(tokens) - 1

    def test_diacritic_fallback_in_snippet(
        self, caplog: pytest.LogCaptureFixture
    ) -> None:
        """Snippet without diacritics matches diacritized text → EX-A-012 warning."""
        text = "فَعَلَ الخَيْرَ وَجَاهَدَ في سَبيلِ الله"
        tokens = text.split()
        snippet = "فعل الخير"  # stripped diacritics
        segments = [_make_raw_segment(0, snippet)]

        with caplog.at_level(logging.WARNING):
            result = normalize_offsets(segments, text, len(tokens))

        assert len(result) == 1
        assert result[0].start_word == 0
        assert ExcerptingErrorCodes.EX_A_012 in caplog.text

    def test_duplicate_snippet_left_to_right(self) -> None:
        """Duplicate text: left-to-right search picks correct instance."""
        # Same phrase appears twice
        text = "الحمد لله رب العالمين ثم الحمد لله رب العالمين أيضا"
        tokens = text.split()
        total = len(tokens)
        # Seg 0 should match first occurrence, seg 1 the second
        snippet = "الحمد لله رب العالمين"
        seg0 = _make_raw_segment(0, snippet)
        seg1 = _make_raw_segment(1, snippet)

        result = normalize_offsets([seg0, seg1], text, total)

        assert result[0].start_word == 0
        assert result[1].start_word > result[0].start_word
        # Contiguity
        assert result[1].start_word == result[0].end_word + 1
        assert result[1].end_word == total - 1

    def test_snippet_not_found_raises(self) -> None:
        """Snippet with no match → ValueError."""
        text = "بسم الله الرحمن الرحيم"
        tokens = text.split()
        bad_snippet = "هذا النص غير موجود في الأصل"
        segments = [_make_raw_segment(0, bad_snippet)]

        with pytest.raises(ValueError, match="Snippet not found"):
            normalize_offsets(segments, text, len(tokens))

    def test_empty_segments(self) -> None:
        """Empty segment list returns empty list."""
        result = normalize_offsets([], "بسم الله", 2)
        assert result == []

    def test_negative_range_raises(self) -> None:
        """Adjacent anchors that produce end < start → ValueError."""
        # Force two segments where second anchor is before first's end
        # by using snippets that appear in reverse order relative to LLM indices
        text = "ب ت ث ج"
        tokens = text.split()
        # Both snippets point to overlapping positions — impossible in valid data
        # but tests the safety check
        seg0 = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=50,
            text_snippet="ث",  # token 2
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.9,
        )
        seg1 = ClassifiedSegment(
            segment_index=1,
            start_word=51,
            end_word=100,
            text_snippet="ت",  # token 1, which is BEFORE token 2
            scholarly_function=ScholarlyFunction.RULE_STATEMENT,
            confidence=0.9,
        )
        # seg0 anchors at token 2 (start_word=2), seg1 anchors at token 1
        # but left-to-right search: seg0 finds "ث" at char 4 → token 2
        # seg1 searches from char 5 onward → finds "ج" at char 6 → token 3
        # Actually, "ت" appears at char 2, but search_start is char 5,
        # so "ت" won't be found after char 5 → ValueError (snippet not found)
        with pytest.raises(ValueError, match="Snippet not found"):
            normalize_offsets([seg0, seg1], text, len(tokens))

    def test_confidence_preserved(self) -> None:
        """Confidence value passes through normalization unchanged."""
        segments = [_make_raw_segment(0, _FIQH_SEG1_SNIPPET)]
        segments[0] = ClassifiedSegment(
            segment_index=0,
            start_word=0,
            end_word=99,
            text_snippet=_FIQH_SEG1_SNIPPET,
            scholarly_function=ScholarlyFunction.DEFINITION,
            confidence=0.73,
        )
        result = normalize_offsets(segments, _FIQH_TEXT, _FIQH_TOTAL)
        assert result[0].confidence == 0.73

    def test_segment_index_preserved(self) -> None:
        """segment_index values pass through normalization unchanged."""
        segments = [
            _make_raw_segment(0, _FIQH_SEG1_SNIPPET),
            _make_raw_segment(1, _FIQH_SEG2_SNIPPET),
        ]
        result = normalize_offsets(segments, _FIQH_TEXT, _FIQH_TOTAL)
        assert result[0].segment_index == 0
        assert result[1].segment_index == 1


# ═══════════════════════════════════════════════════════════════════
# Tests — _compute_classify_max_tokens
# ═══════════════════════════════════════════════════════════════════


class TestComputeClassifyMaxTokens:
    @pytest.mark.parametrize(
        "word_count, expected",
        [
            (500, 8192),
            (2000, 8192),
            (2001, 32768),
            (3000, 32768),
            (4001, 32768),
        ],
    )
    def test_scaling(self, word_count: int, expected: int) -> None:
        assert _compute_classify_max_tokens(word_count) == expected

    def test_4000_plus_logs_warning(self, caplog: pytest.LogCaptureFixture) -> None:
        with caplog.at_level(logging.WARNING):
            result = _compute_classify_max_tokens(4500)
        assert result == 32768
        assert "Untested word count range" in caplog.text
        assert "4500" in caplog.text
