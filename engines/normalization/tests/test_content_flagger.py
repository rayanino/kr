"""Tests for content flagging — SPEC §4.A.9.

Covers:
  - Quran citation detection (4 patterns)
  - Hadith citation detection (4 patterns)
  - Index page detection (5 keywords)
  - TOC page pass-through
  - Blank page detection
  - has_verse / has_table pass-through from Pass 3
  - ADV-024: non-standard Quran prefix (curly braces)
  - ADV-050: non-standard hadith intro (ﷺ)
  - ADV-051: TOC page detection via structure discovery
  - Negative: plain nahw text (no citations)
  - Real fixture: 05_tafsir Quran citations
  - Real fixture: 10_no_author hadith citations
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.normalization.contracts import ContentFlags
from engines.normalization.src.content_flagger import (
    _has_hadith_citation,
    _has_quran_citation,
    _is_index_page,
    compute_content_flags,
)
from engines.normalization.tests.conftest import (
    FIXTURES_REAL,
    _full_pipeline,
    _make_cleaned_page,
)
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer


# ══════════════════════════════════════════════════════════════════════
# Quran citation detection
# ══════════════════════════════════════════════════════════════════════


class TestQuranCitation:
    """Quran citation detection via 4 independent patterns."""

    def test_qala_taala(self) -> None:
        """Pattern 1: قال تعالى triggers Quran flag."""
        text = "وقد قال تعالى في كتابه الكريم"
        assert _has_quran_citation(text) is True

    def test_curly_brackets(self) -> None:
        """Pattern 2: {Arabic text} triggers Quran flag (ADV-024)."""
        text = "ومن الدليل {وأقيموا الصلاة وآتوا الزكاة} وهذا واضح"
        assert _has_quran_citation(text) is True

    def test_ornate_brackets(self) -> None:
        """Pattern 3: ﴿Arabic text﴾ triggers Quran flag."""
        text = "قوله ﴿إن الله على كل شيء قدير﴾ يدل على ذلك"
        assert _has_quran_citation(text) is True

    def test_surah_name(self) -> None:
        """Pattern 4: سورة + name triggers Quran flag."""
        text = "كما جاء في سورة البقرة من الآيات الدالة"
        assert _has_quran_citation(text) is True

    def test_negative_no_quran(self) -> None:
        """Plain nahw text without Quran should NOT trigger."""
        text = "الفاعل مرفوع والمفعول به منصوب وهذه قاعدة أساسية في النحو"
        assert _has_quran_citation(text) is False


# ══════════════════════════════════════════════════════════════════════
# Hadith citation detection
# ══════════════════════════════════════════════════════════════════════


class TestHadithCitation:
    """Hadith citation detection via 4 independent patterns."""

    def test_saws_unicode(self) -> None:
        """Pattern 1: ﷺ (ADV-050) triggers hadith flag."""
        text = "قال النبي \uFDFA إنما الأعمال بالنيات"
        assert _has_hadith_citation(text) is True

    def test_saws_phrase(self) -> None:
        """Pattern 2: صلى الله عليه وسلم triggers hadith flag."""
        text = "قال رسول الله صلى الله عليه وسلم في الحديث الشريف"
        assert _has_hadith_citation(text) is True

    def test_rawahu_collector(self) -> None:
        """Pattern 3: رواه + collector name triggers hadith flag."""
        text = "وفي الحديث المتفق عليه رواه البخاري ومسلم"
        assert _has_hadith_citation(text) is True

    def test_guillemet_with_qala(self) -> None:
        """Pattern 4: قال + «Arabic text» within short distance."""
        text = "وقد قال «إنما الأعمال بالنيات وإنما لكل امرئ ما نوى»"
        assert _has_hadith_citation(text) is True

    def test_guillemet_long_isnad_60_chars(self) -> None:
        """L-009 fix: 60-char isnad chain should be detected at distance 80.

        Real pattern: حدثنا فلان عن فلان عن فلان قال «hadith text»
        The narrator chain between قال and « can span 60+ characters.
        Old threshold (50) would miss this. New threshold (80) catches it.
        """
        # Realistic isnad chain: ~62 chars between قال and «
        text = (
            "حدثنا عبد الله بن يوسف عن مالك بن أنس عن نافع عن عبد الله بن عمر أن رسول الله "
            "قال في حديثه الذي رواه عنه أصحابه الكبار والصغار"
            " «إنما الأعمال بالنيات وإنما لكل امرئ ما نوى»"
        )
        assert _has_hadith_citation(text) is True

    def test_guillemet_long_isnad_75_chars(self) -> None:
        """L-009 fix: 75-char distance still within threshold 80."""
        # Build text where قال is ~75 chars before «
        isnad = "قال" + " " + "و" * 73 + " "
        text = isnad + "«إنما الأعمال بالنيات»"
        assert _has_hadith_citation(text) is True

    def test_guillemet_beyond_threshold_85_chars(self) -> None:
        """Distance 85 exceeds threshold 80 — should NOT match guillemet pattern.

        May still be detected by other hadith patterns (ﷺ, رواه, etc.).
        """
        # Build text where قال is ~85 chars before «
        isnad = "قال" + " " + "و" * 83 + " "
        text = isnad + "«إنما الأعمال بالنيات»"
        # This specific text has no ﷺ, no صلى الله عليه وسلم, no رواه
        assert _has_hadith_citation(text) is False

    def test_negative_no_hadith(self) -> None:
        """Plain fiqh text without hadith should NOT trigger."""
        text = "والراجح في المذهب أن الماء إذا بلغ قلتين لم يحمل خبثا"
        assert _has_hadith_citation(text) is False

    @pytest.mark.parametrize("collector", [
        "البخاري", "مسلم", "أبو داود", "الترمذي",
        "النسائي", "ابن ماجه", "أحمد",
    ])
    def test_all_collectors(self, collector: str) -> None:
        """All 7 hadith collectors detected with رواه prefix."""
        text = f"رواه {collector} في صحيحه"
        assert _has_hadith_citation(text) is True


# ══════════════════════════════════════════════════════════════════════
# SPEC §4.A.9 concrete example: mixed fiqh page
# ══════════════════════════════════════════════════════════════════════


class TestSpecConcreteExample:
    """SPEC §4.A.9 (lines 674-696): mixed fiqh page with both citations."""

    def test_mixed_fiqh_page(self) -> None:
        """Page with both Quran and hadith → both flags True."""
        text = (
            "باب الزكاة\n"
            "قال تعالى {وأقيموا الصلاة وآتوا الزكاة}\n"
            "وقد قال النبي صلى الله عليه وسلم في الحديث المتفق عليه "
            "بُنِيَ الإسلام على خمس\n"
            "رواه البخاري ومسلم"
        )
        page = _make_cleaned_page(text)
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.has_quran_citation is True
        assert flags.has_hadith_citation is True
        assert flags.is_blank is False


# ══════════════════════════════════════════════════════════════════════
# Index page detection
# ══════════════════════════════════════════════════════════════════════


class TestIndexPage:
    """Index page detection via 5 keywords."""

    @pytest.mark.parametrize("keyword", [
        "فهرس الأعلام", "فهرس الأحاديث", "فهرس الآيات",
        "فهرس المصادر", "فهرس الأبيات",
    ])
    def test_index_keyword_in_head(self, keyword: str) -> None:
        """Index keyword in first 200 chars triggers is_index_page."""
        text = f"{keyword}\n" + "أ" * 300
        assert _is_index_page(text, []) is True

    def test_index_keyword_in_title_spans(self) -> None:
        """Index keyword in title_spans triggers is_index_page."""
        assert _is_index_page("بعض النص العادي", ["فهرس الأعلام"]) is True

    def test_keyword_beyond_200_chars(self) -> None:
        """Index keyword beyond 200 chars does NOT trigger."""
        text = "أ" * 250 + "فهرس الأعلام"
        assert _is_index_page(text, []) is False


# ══════════════════════════════════════════════════════════════════════
# TOC / Blank / Pass-through flags
# ══════════════════════════════════════════════════════════════════════


class TestPassThroughFlags:
    """Flags that pass through from Pass 3 or structure discovery."""

    def test_toc_page_passthrough(self) -> None:
        """ADV-051: is_toc_page passed through from structure discovery."""
        page = _make_cleaned_page("فهرس الموضوعات")
        flags = compute_content_flags(page, is_toc_page=True)
        assert flags.is_toc_page is True

    def test_not_toc_page(self) -> None:
        page = _make_cleaned_page("نص عادي")
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.is_toc_page is False

    def test_blank_page_from_pass3(self) -> None:
        """is_blank from CleanedPage.is_blank."""
        page = _make_cleaned_page("", is_blank=True)
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.is_blank is True

    def test_blank_page_empty_text(self) -> None:
        """Empty primary_text → is_blank even if is_blank=False."""
        page = _make_cleaned_page("   ")
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.is_blank is True

    def test_image_only_page(self) -> None:
        """is_image_only → is_blank."""
        page = _make_cleaned_page("", is_image_only=True)
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.is_blank is True

    def test_has_verse_passthrough(self) -> None:
        """has_verse from Pass 3."""
        page = _make_cleaned_page("بيت شعري", has_verse=True)
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.has_verse is True

    def test_has_table_passthrough(self) -> None:
        """has_table from Pass 3 (has_tables field)."""
        page = _make_cleaned_page("جدول بيانات", has_tables=True)
        flags = compute_content_flags(page, is_toc_page=False)
        assert flags.has_table is True


# ══════════════════════════════════════════════════════════════════════
# Real fixture tests
# ══════════════════════════════════════════════════════════════════════


class TestRealFixtures:
    """Content flags on real Shamela fixtures."""

    def test_05_tafsir_quran_citations(self) -> None:
        """05_tafsir: at least 2 pages with Quran citations."""
        htm = (FIXTURES_REAL / "05_tafsir" / "book.htm").read_text(encoding="utf-8")
        n = ShamelaNormalizer()
        cleaned = _full_pipeline(n, htm)
        quran_pages = [
            p for p in cleaned if _has_quran_citation(p.primary_text)
        ]
        assert len(quran_pages) >= 2, (
            f"Expected >=2 Quran pages in tafsir, got {len(quran_pages)}"
        )

    def test_10_no_author_hadith_citations(self) -> None:
        """10_no_author: at least 2 pages with hadith citations."""
        htm = (FIXTURES_REAL / "10_no_author" / "book.htm").read_text(encoding="utf-8")
        n = ShamelaNormalizer()
        cleaned = _full_pipeline(n, htm)
        hadith_pages = [
            p for p in cleaned if _has_hadith_citation(p.primary_text)
        ]
        assert len(hadith_pages) >= 2, (
            f"Expected >=2 hadith pages in 10_no_author, got {len(hadith_pages)}"
        )
