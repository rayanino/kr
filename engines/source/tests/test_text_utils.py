"""Tests for slug generation in text_utils — SPEC §4.A.1.

Tests use real Arabic text from the transliteration config.
"""

from __future__ import annotations

import pytest

from engines.source.src.text_utils import (
    ARABIC_DIACRITICS,
    TRANSLIT_MAP,
    generate_human_label,
    generate_slug,
    generate_work_id,
    strip_diacritics,
    transliterate_chars,
)


# ── transliteration table fixture ──

TRANSLIT_TABLE: dict[str, dict[str, str]] = {
    "scholars": {
        "ابن عقيل": "ibn_aqil",
        "ابن مالك": "ibn_malik",
        "السيوطي": "suyuti",
        "النووي": "nawawi",
        "ابن تيمية": "ibn_taymiyyah",
        "البخاري": "bukhari",
        "مالك بن نبي": "malik_bennabi",
        "الزاحم": "zahim",
    },
    "titles": {
        "ألفية": "alfiyyah",
        "المغني": "mughni",
        "همع الهوامع": "hama_alhawami",
        "جمع الجوامع": "jam_aljawami",
        "أحكام": "ahkam",
        "مذكرات": "mudhakkirat",
    },
}


class TestStripDiacritics:
    """Test Arabic diacritics stripping."""

    def test_removes_fathah(self) -> None:
        # كَتَبَ → كتب
        assert strip_diacritics("كَتَبَ") == "كتب"

    def test_removes_shaddah(self) -> None:
        # محمّد → محمد
        assert strip_diacritics("محمّد") == "محمد"

    def test_removes_multiple_diacritics(self) -> None:
        text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
        result = strip_diacritics(text)
        # No diacritics should remain
        for ch in result:
            assert ch not in ARABIC_DIACRITICS

    def test_preserves_base_text(self) -> None:
        assert strip_diacritics("كتاب") == "كتاب"

    def test_empty_string(self) -> None:
        assert strip_diacritics("") == ""

    def test_superscript_alef(self) -> None:
        # U+0670 SUPERSCRIPT ALEF
        assert strip_diacritics("رَحْمٰن") == "رحمن"


class TestTransliterateChars:
    """Test Arabic → Latin transliteration for slug use."""

    def test_basic_word(self) -> None:
        result = transliterate_chars("كتاب")
        assert result == "ktab"

    def test_al_prefix(self) -> None:
        result = transliterate_chars("الكتاب")
        assert result == "al_ktab"

    def test_spaces_to_underscores(self) -> None:
        result = transliterate_chars("ابن مالك")
        assert "_" in result

    def test_no_special_chars(self) -> None:
        result = transliterate_chars("كتاب (الأول)")
        assert "(" not in result
        assert ")" not in result


class TestGenerateSlug:
    """Test slug generation with table lookup and fallback."""

    def test_table_lookup_exact(self) -> None:
        """Known scholar name found in table → table slug."""
        result = generate_slug("السيوطي", TRANSLIT_TABLE["scholars"])
        assert result == "suyuti"

    def test_table_lookup_substring(self) -> None:
        """Table entry found as substring → use table slug."""
        result = generate_slug("همع الهوامع في شرح جمع الجوامع", TRANSLIT_TABLE["titles"])
        assert result == "hama_alhawami"

    def test_table_lookup_longest_match(self) -> None:
        """Longest matching substring wins."""
        table = {"أحكام": "ahkam", "أحكام الاضطباع": "ahkam_aliditiaba"}
        result = generate_slug("أحكام الاضطباع والرمل", table)
        assert result == "ahkam_aliditiaba"

    def test_fallback_transliteration(self) -> None:
        """Unknown text falls back to transliteration."""
        result = generate_slug("مصطلح غير معروف", {})
        assert result  # Not empty
        assert all(c.isalnum() or c == "_" for c in result)

    def test_empty_input_md5(self) -> None:
        """Empty input → MD5 hash prefix."""
        result = generate_slug("", {})
        assert len(result) == 8
        assert all(c in "0123456789abcdef" for c in result)

    def test_max_length_20(self) -> None:
        """Slug truncated to 20 chars."""
        long_table = {"مفتاح": "a_very_long_slug_that_exceeds_twenty_characters"}
        result = generate_slug("مفتاح", long_table)
        assert len(result) <= 20

    def test_diacritics_only_input(self) -> None:
        """Text that is only diacritics → MD5 fallback."""
        result = generate_slug("\u064E\u064F\u0650", {})
        assert len(result) == 8  # MD5 fallback


class TestGenerateWorkId:
    """Test work_id generation: wrk_{author_slug}_{title_slug}."""

    def test_known_author_and_title(self) -> None:
        result = generate_work_id("السيوطي", "همع الهوامع", TRANSLIT_TABLE)
        assert result.startswith("wrk_")
        assert "suyuti" in result
        assert "hama_alhawami" in result

    def test_unknown_author(self) -> None:
        """Unknown author → transliteration fallback."""
        result = generate_work_id("عبد الله الزاحم", "أحكام", TRANSLIT_TABLE)
        assert result.startswith("wrk_")
        assert "ahkam" in result

    def test_max_length_50(self) -> None:
        """Work ID max 50 chars."""
        result = generate_work_id(
            "السيوطي",
            "همع الهوامع في شرح جمع الجوامع",
            TRANSLIT_TABLE,
        )
        assert len(result) <= 50

    def test_format(self) -> None:
        result = generate_work_id("النووي", "المغني", TRANSLIT_TABLE)
        parts = result.split("_", 2)
        assert parts[0] == "wrk"


class TestGenerateHumanLabel:
    """Test human-readable label generation."""

    def test_known_title(self) -> None:
        result = generate_human_label("همع الهوامع", TRANSLIT_TABLE)
        assert result == "hama_alhawami"

    def test_max_length_30(self) -> None:
        result = generate_human_label("مفتاح العلوم الكبرى والصغرى", TRANSLIT_TABLE)
        assert len(result) <= 30

    def test_lowercase(self) -> None:
        result = generate_human_label("أحكام", TRANSLIT_TABLE)
        assert result == result.lower()
