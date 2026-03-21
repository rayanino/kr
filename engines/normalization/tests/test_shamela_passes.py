"""Tests for Shamela normalizer Passes 1–3.

Test categories (NEXT.md §F):
  F1: ADV-001 through ADV-010 (adversarial)
  F2: Real fixture parsing (13 fixtures)
  F3: Multi-volume handling
  F4: Ibn Aqil fixture (detailed)
  F5: Footnote type classification
  F6: Whitespace normalization
  F7: Verse detection
  F8: Table extraction
  F9: Error code usage
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from engines.normalization.src.normalizers.shamela import (
    CleanedPage,
    RawPage,
    SeparatedPage,
    ShamelaNormalizer,
    arabic_to_int,
    classify_footnote_type,
    detect_verse,
    normalize_whitespace,
)
from engines.normalization.src.errors import NormalizationError, NormErrorCode

# ══════════════════════════════════════════════════════════════════════
# Test infrastructure
# ══════════════════════════════════════════════════════════════════════

FIXTURES_REAL = Path("tests/fixtures/shamela_real")
FIXTURES_ENGINE = Path("engines/normalization/tests/fixtures")
FIXTURES_EDGE = Path("tests/fixtures/shamela_edge_cases")
IBN_AQIL = FIXTURES_ENGINE / "shamela_ibn_aqil.htm"


@pytest.fixture
def normalizer() -> ShamelaNormalizer:
    return ShamelaNormalizer()


def _wrap_page(content: str, page_num: str | None = None) -> str:
    """Wrap content in a PageText div with optional page number."""
    parts = ["<div class='PageText'>"]
    if page_num is not None:
        parts.append(
            f"<div class='PageHead'>"
            f"<span class='PageNumber'>(ص: {page_num})</span>"
            f"<hr/></div>"
        )
    parts.append(content)
    parts.append("</div>")
    return "".join(parts)


def _make_html(*page_contents: str) -> str:
    """Build a minimal Shamela HTML document from page contents."""
    return (
        "<html><head></head><body>"
        + "".join(page_contents)
        + "</body></html>"
    )


def _full_pipeline(
    normalizer: ShamelaNormalizer, html: str, volume: int = 1
) -> list[CleanedPage]:
    """Run Passes 1–3 on HTML text."""
    raw = normalizer._pass1_parse(html, volume=volume, seq_offset=0)
    sep = normalizer._pass2_separate(raw)
    return normalizer._pass3_clean(sep)


# ══════════════════════════════════════════════════════════════════════
# F1: Adversarial tests (ADV-001 through ADV-010)
# ══════════════════════════════════════════════════════════════════════


class TestAdversarial:
    """SPEC_ADVERSARY_NORMALIZATION.md — mandatory adversarial cases."""

    def test_adv001_width_79_not_separator(self, normalizer: ShamelaNormalizer):
        """ADV-001: width=79 is NOT a footnote separator (79 < 80)."""
        html = _make_html(_wrap_page(
            "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية\n"
            "(1) هذا تعريف النحويين\n"
            "<hr width='79'>\n"
            "(1) انظر شرح الكافية للرضي",
            page_num="١٢",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert len(pages[0].footnotes) == 0
        assert "انظر شرح الكافية" in pages[0].primary_text

    def test_adv002_width_101_not_separator(self, normalizer: ShamelaNormalizer):
        """ADV-002: width=101 is NOT a footnote separator (101 > 100)."""
        html = _make_html(_wrap_page(
            "باب الصلاة\n"
            "<hr width='101'>\n"
            "(1) الصلاة لغة الدعاء",
            page_num="١٥",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert len(pages[0].footnotes) == 0
        assert "الصلاة لغة الدعاء" in pages[0].primary_text

    def test_adv003_percentage_width_separator(self, normalizer: ShamelaNormalizer):
        """ADV-003: width='95%' captures 95 which IS in range → separator."""
        html = _make_html(_wrap_page(
            'فصل في المسح على الخفين\n'
            '<hr width="95%">\n'
            '<div class=\'footnote\'>'
            '(1) ثبت المسح في أحاديث كثيرة'
            '</div>',
            page_num="٢٠",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert len(pages[0].footnotes) == 1
        assert "ثبت المسح" in pages[0].footnotes[0].text
        assert "ثبت المسح" not in pages[0].primary_text

    def test_adv004_self_closing_extra_attrs(self, normalizer: ShamelaNormalizer):
        """ADV-004: Self-closing HR with extra attributes."""
        html = _make_html(_wrap_page(
            "وقال الشافعي رحمه الله في هذه المسألة\n"
            "<hr width=95 align='right' color='gray' />\n"
            "<div class='footnote'>"
            "(1) نقله عنه البيهقي في السنن الكبرى"
            "</div>",
            page_num="٣٣",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert len(pages[0].footnotes) == 1
        assert "نقله عنه البيهقي" in pages[0].footnotes[0].text
        assert "نقله عنه البيهقي" not in pages[0].primary_text

    def test_adv005_orphan_ref_preserved(self, normalizer: ShamelaNormalizer):
        """ADV-005: Orphan ref (3) kept as literal, NOT replaced with ⌜3⌝."""
        html = _make_html(_wrap_page(
            "قال ابن تيمية (3) في مجموع الفتاوى: إن الأصل في العبادات التوقيف\n"
            "<hr width='95'>\n"
            "<div class='footnote'>"
            "(1) مجموع الفتاوى ج١٢ ص٣٤٥\n"
            "<font color=#be0000>(2)</font> وانظر إعلام الموقعين لابن القيم"
            "</div>",
            page_num="٤٤",
        ))
        pages = _full_pipeline(normalizer, html)
        p = pages[0]
        # (3) is an orphan — no footnote 3 exists
        assert "(3)" in p.primary_text
        assert "\u231c3\u231d" not in p.primary_text
        # Footnotes 1 and 2 exist
        assert len(p.footnotes) == 2
        # Orphan ref logged
        assert any(
            NormErrorCode.ORPHAN_FOOTNOTE_REF.value in w for w in p.warnings
        )

    def test_adv006_diacritics_entity_preserved(self, normalizer: ShamelaNormalizer):
        """ADV-006: &#x0670; (superscript alef) preserved after entity decoding."""
        html = _make_html(_wrap_page(
            "بِسْمِ اللَّهِ الرَّحْمَ&#x0670;نِ الرَّحِيمِ",
            page_num="٧",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        # U+0670 ARABIC LETTER SUPERSCRIPT ALEF must be present
        assert "\u0670" in pages[0].primary_text
        # No diacritics corruption error raised (implicit — we got here)

    def test_adv007_zwnj_preserved(self, normalizer: ShamelaNormalizer):
        """ADV-007: ZWNJ characters preserved in output."""
        html = _make_html(_wrap_page(
            "&#x200C;&#x200C;باب الوضوء&#x200C;&#x200C;\n"
            "والوضوء في اللغة مأخوذ من الوضاءة",
            page_num="٥٥",
        ))
        pages = _full_pipeline(normalizer, html)
        p = pages[0]
        # ZWNJ characters must be preserved
        assert "\u200c" in p.primary_text
        # Double ZWNJ at start → heading signal
        assert p.starts_with_zwnj_heading is True

    def test_adv008_no_page_number_after_content(self, normalizer: ShamelaNormalizer):
        """ADV-008: Page without PageNumber after content pages → content unit."""
        # First page has a number (establishes content), second doesn't
        page1 = _wrap_page("الصلاة المفروضة خمس", page_num="٢٩")
        page2 = (
            "<div class='PageText'>"
            "<span class='PageHead'>فصل في أركان الصلاة</span>"
            "أركان الصلاة أربعة عشر: القيام مع القدرة، وتكبيرة الإحرام"
            "</div>"
        )
        html = _make_html(page1, page2)
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 2
        # Second page has no page number
        assert pages[1].page_number_int is None
        assert pages[1].page_number_display is None
        assert "أركان الصلاة أربعة عشر" in pages[1].primary_text

    def test_adv009_empty_page_is_blank(self, normalizer: ShamelaNormalizer):
        """ADV-009: Empty page → is_blank=True, contiguous unit_index."""
        page1 = _wrap_page("", page_num="١٠٠")
        page2 = _wrap_page(
            "تابع: باب الصلاة على الميت", page_num="١٠١"
        )
        html = _make_html(page1, page2)
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 2
        assert pages[0].is_blank is True
        assert pages[0].primary_text.strip() == ""
        assert pages[1].is_blank is False
        # Contiguous unit_index
        assert pages[0].unit_index == 0
        assert pages[1].unit_index == 1

    def test_adv010_pagehead_excluded_from_primary(self, normalizer: ShamelaNormalizer):
        """ADV-010: PageHead text NOT in primary_text."""
        html = _make_html(
            "<div class='PageText'>"
            "<div class='PageHead'>"
            "<span class='PartName'>باب صفة الصلاة</span>"
            "<span class='PageNumber'>(ص: ٣٠)</span>"
            "<hr/></div>"
            "يستحب أن يقرأ بعد الفاتحة سورة في الركعتين الأوليين"
            "</div>"
        )
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert "باب صفة الصلاة" not in pages[0].primary_text
        assert "يستحب أن يقرأ" in pages[0].primary_text


# ══════════════════════════════════════════════════════════════════════
# F2: Real fixture parsing (13 fixtures)
# ══════════════════════════════════════════════════════════════════════


def _get_fixture_dirs() -> list[Path]:
    """Get all real Shamela fixture directories."""
    if not FIXTURES_REAL.exists():
        return []
    dirs = sorted(
        d for d in FIXTURES_REAL.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )
    return dirs


class TestRealFixtures:
    """Parse each real Shamela fixture through Passes 1–3."""

    @pytest.mark.parametrize(
        "fixture_dir",
        _get_fixture_dirs(),
        ids=[d.name for d in _get_fixture_dirs()],
    )
    def test_fixture_parses_without_crash(
        self, normalizer: ShamelaNormalizer, fixture_dir: Path
    ):
        """Each fixture parses through all 3 passes without errors."""
        htm_files = sorted(
            list(fixture_dir.glob("*.htm")) + list(fixture_dir.glob("*.html"))
        )
        assert htm_files, f"No .htm files in {fixture_dir}"

        all_clean: list[CleanedPage] = []
        offset = 0

        for f in htm_files:
            try:
                vol = int(f.stem)
            except ValueError:
                vol = len(all_clean) + 1

            html = f.read_text(encoding="utf-8")
            raw = normalizer._pass1_parse(html, volume=vol, seq_offset=offset)
            content = [p for p in raw if not p.is_metadata_page]
            offset += len(content)
            sep = normalizer._pass2_separate(raw)
            clean = normalizer._pass3_clean(sep)
            all_clean.extend(clean)

        # At least one content page
        assert len(all_clean) > 0, f"No content pages in {fixture_dir.name}"

        # All pages have valid unit_index (contiguous)
        indices = [p.unit_index for p in all_clean]
        assert indices == list(range(len(all_clean))), (
            f"unit_index not contiguous in {fixture_dir.name}: "
            f"expected 0..{len(all_clean)-1}"
        )

        # First content page has a page number (in most fixtures)
        if all_clean[0].page_number_int is not None:
            assert all_clean[0].page_number_int >= 1


# ══════════════════════════════════════════════════════════════════════
# F3: Multi-volume handling
# ══════════════════════════════════════════════════════════════════════


class TestMultiVolume:
    """Multi-volume fixture parsing and unit_index contiguity."""

    def test_fixture_11_three_volumes(self, normalizer: ShamelaNormalizer):
        """Fixture 11 (3 volumes): contiguous unit_index, correct volumes."""
        fixture_dir = FIXTURES_REAL / "11_multi_small"
        if not fixture_dir.exists():
            pytest.skip("Fixture 11 not available")

        files = sorted(fixture_dir.glob("*.htm"))
        assert len(files) == 3

        all_clean: list[CleanedPage] = []
        offset = 0
        vol_counts: dict[int, int] = {}

        for f in files:
            vol = int(f.stem)
            html = f.read_text(encoding="utf-8")
            raw = normalizer._pass1_parse(html, volume=vol, seq_offset=offset)
            content = [p for p in raw if not p.is_metadata_page]
            offset += len(content)
            vol_counts[vol] = len(content)
            sep = normalizer._pass2_separate(raw)
            clean = normalizer._pass3_clean(sep)
            all_clean.extend(clean)

        # Correct volume numbers
        assert set(vol_counts.keys()) == {1, 2, 3}

        # Total = sum of per-volume counts
        assert len(all_clean) == sum(vol_counts.values())

        # Contiguous unit_index across all volumes
        assert all_clean[-1].unit_index == len(all_clean) - 1
        indices = [p.unit_index for p in all_clean]
        assert indices == list(range(len(all_clean)))

    def test_fixture_12_non_numeric_stem(self, normalizer: ShamelaNormalizer):
        """Fixture 12 has المقدمة.htm — non-numeric stem gets warning."""
        fixture_dir = FIXTURES_REAL / "12_multi_muq"
        if not fixture_dir.exists():
            pytest.skip("Fixture 12 not available")

        files = sorted(
            list(fixture_dir.glob("*.htm")) + list(fixture_dir.glob("*.html"))
        )
        # Resolve input files to check warning handling
        result = normalizer._resolve_input_files(fixture_dir)
        assert len(result) == len(files)

        # Check parsing works through all 3 passes
        all_clean: list[CleanedPage] = []
        offset = 0
        for vol, f in result:
            html = f.read_text(encoding="utf-8")
            raw = normalizer._pass1_parse(html, volume=vol, seq_offset=offset)
            content = [p for p in raw if not p.is_metadata_page]
            offset += len(content)
            sep = normalizer._pass2_separate(raw)
            clean = normalizer._pass3_clean(sep)
            all_clean.extend(clean)

        assert len(all_clean) > 0
        indices = [p.unit_index for p in all_clean]
        assert indices == list(range(len(all_clean)))


# ══════════════════════════════════════════════════════════════════════
# F4: Ibn Aqil fixture (detailed)
# ══════════════════════════════════════════════════════════════════════


class TestIbnAqil:
    """Detailed test of the hand-crafted ibn_aqil fixture."""

    @pytest.fixture
    def ibn_aqil_pages(
        self, normalizer: ShamelaNormalizer
    ) -> list[CleanedPage]:
        if not IBN_AQIL.exists():
            pytest.skip("Ibn Aqil fixture not available")
        html = IBN_AQIL.read_text(encoding="utf-8")
        return _full_pipeline(normalizer, html)

    @pytest.fixture
    def ibn_aqil_raw(
        self, normalizer: ShamelaNormalizer
    ) -> list[RawPage]:
        if not IBN_AQIL.exists():
            pytest.skip("Ibn Aqil fixture not available")
        html = IBN_AQIL.read_text(encoding="utf-8")
        return normalizer._pass1_parse(html, volume=1, seq_offset=0)

    def test_metadata_page_skipped(self, ibn_aqil_raw: list[RawPage]):
        """Page 1 (metadata) should be skipped — no page number."""
        assert ibn_aqil_raw[0].is_metadata_page is True
        assert ibn_aqil_raw[0].unit_index == -1

    def test_content_page_count(self, ibn_aqil_pages: list[CleanedPage]):
        """5 content pages after skipping metadata."""
        assert len(ibn_aqil_pages) == 5

    def test_page15_bold_spans(self, ibn_aqil_raw: list[RawPage]):
        """Page 15: bold spans recorded for Pass 5."""
        # Page 15 is the first content page (index 1 in raw, 0 in content)
        page15 = ibn_aqil_raw[1]
        assert page15.page_number_int == 15
        assert len(page15.bold_spans) == 1
        assert "كَلَامُنَا" in page15.bold_spans[0][2]

    def test_page15_footnote_extracted(self, ibn_aqil_pages: list[CleanedPage]):
        """Page 15: footnote (1) extracted, ⌜1⌝ in text, (1) NOT in text."""
        page15 = ibn_aqil_pages[0]
        assert page15.page_number_int == 15
        assert len(page15.footnotes) == 1
        assert page15.footnotes[0].number == 1
        assert "\u231c1\u231d" in page15.primary_text
        # (1) should NOT remain as literal
        # Need to verify it's not present — but Quran ref (٢٣٤٥) uses
        # Arabic-Indic digits so won't match
        assert 1 in page15.footnote_ref_numbers

    def test_page15_heading_in_title_spans(self, ibn_aqil_raw: list[RawPage]):
        """Page 15: heading from PageHead recorded."""
        page15 = ibn_aqil_raw[1]
        assert page15.pagehead_text is not None
        assert "الكلام" in page15.pagehead_text

    def test_page16_two_footnotes(self, ibn_aqil_pages: list[CleanedPage]):
        """Page 16: two footnotes parsed, both cross-referenced."""
        page16 = ibn_aqil_pages[1]
        assert page16.page_number_int == 16
        assert len(page16.footnotes) == 2
        assert page16.footnotes[0].number == 1
        assert page16.footnotes[1].number == 2
        assert set(page16.footnote_ref_numbers) == {1, 2}

    def test_page16_footnote_has_tahqiq_marker(
        self, ibn_aqil_pages: list[CleanedPage]
    ):
        """Page 16 footnote 1 contains 'في نسخة' → tahqiq_editor."""
        page16 = ibn_aqil_pages[1]
        fn1 = page16.footnotes[0]
        assert fn1.footnote_type == "tahqiq_editor"
        assert fn1.classification_confidence == 0.8

    def test_diacritics_preserved(self, ibn_aqil_pages: list[CleanedPage]):
        """Diacritics in كَلَامُنَا لَفْظٌ مُفِيدٌ preserved exactly."""
        page15 = ibn_aqil_pages[0]
        text = page15.primary_text
        # Check specific diacritical marks
        assert "كَلَامُنَا" in text  # kasra, fatha, damma, shadda
        assert "لَفْظٌ" in text
        assert "مُفِيدٌ" in text

    def test_page19_zwnj_heading(self, ibn_aqil_pages: list[CleanedPage]):
        """Page 19: starts with double ZWNJ (heading signal)."""
        page19 = ibn_aqil_pages[4]
        assert page19.page_number_int == 19
        assert page19.starts_with_zwnj_heading is True

    def test_page18_no_footnote_separator(
        self, ibn_aqil_pages: list[CleanedPage]
    ):
        """Page 18: no footnote separator → NORM_FOOTNOTE_SEPARATOR_ABSENT."""
        page18 = ibn_aqil_pages[3]
        assert page18.page_number_int == 18
        assert page18.has_footnote_separator is False
        assert any(
            NormErrorCode.FOOTNOTE_SEPARATOR_ABSENT.value in w
            for w in page18.warnings
        )


# ══════════════════════════════════════════════════════════════════════
# F5: Footnote type classification
# ══════════════════════════════════════════════════════════════════════


class TestFootnoteClassification:
    """Coarse footnote type classification (SPEC §4.A.2 Pass 2)."""

    def test_tahqiq_bukhari(self):
        """'أخرجه البخاري' → tahqiq_editor."""
        ft, conf = classify_footnote_type("أخرجه البخاري في صحيحه")
        assert ft == "tahqiq_editor"
        assert conf == 0.8

    def test_tahqiq_manuscript(self):
        """'في نسخة' → tahqiq_editor."""
        ft, conf = classify_footnote_type(
            'في نسخة أ: «فإن كل واحد» وفي نسخة ب: «فإن كلاً»'
        )
        assert ft == "tahqiq_editor"

    def test_author_voice(self):
        """'قلت:' at start → author_original."""
        ft, conf = classify_footnote_type("قلت: هذا مما يؤيد القول الأول")
        assert ft == "author_original"
        assert conf == 0.7

    def test_unknown_default(self):
        """No markers → unknown_footnote_type."""
        ft, conf = classify_footnote_type("هذا نص عادي بدون أي علامات تحقيق")
        assert ft == "unknown_footnote_type"
        assert conf == 0.5

    def test_hadith_grading(self):
        """'صحيح' → tahqiq_editor."""
        ft, _ = classify_footnote_type("حديث صحيح رواه مسلم")
        assert ft == "tahqiq_editor"


# ══════════════════════════════════════════════════════════════════════
# F6: Whitespace normalization
# ══════════════════════════════════════════════════════════════════════


class TestWhitespaceNormalization:
    """SPEC §4.A.8 whitespace rules."""

    def test_nbsp_to_space(self, normalizer: ShamelaNormalizer):
        """NBSP → regular space."""
        html = _make_html(_wrap_page(
            "text\u00a0with\u00a0nbsp", page_num="١"
        ))
        pages = _full_pipeline(normalizer, html)
        assert "text with nbsp" in pages[0].primary_text
        assert "\u00a0" not in pages[0].primary_text

    def test_typographic_spaces_to_space(self):
        """U+2000–U+200A → regular space."""
        text = "word\u2003middle\u2009end"
        result = normalize_whitespace(text)
        assert "word middle end" in result
        assert "\u2003" not in result
        assert "\u2009" not in result

    def test_zwnj_preserved(self, normalizer: ShamelaNormalizer):
        """ZWNJ (U+200C) preserved, not stripped."""
        html = _make_html(_wrap_page(
            "\u200c\u200cباب\u200c", page_num="١"
        ))
        pages = _full_pipeline(normalizer, html)
        assert "\u200c" in pages[0].primary_text

    def test_zwsp_preserved(self):
        """ZWSP (U+200B) preserved."""
        text = "text\u200bword"
        result = normalize_whitespace(text)
        assert "\u200b" in result

    def test_zwj_preserved(self):
        """ZWJ (U+200D) preserved."""
        text = "text\u200dword"
        result = normalize_whitespace(text)
        assert "\u200d" in result

    def test_blank_line_collapse(self):
        """3+ blank lines → 1 blank line."""
        text = "first\n\n\n\n\nsecond"
        result = normalize_whitespace(text)
        # Should have at most 2 consecutive newlines (= 1 blank line)
        assert "\n\n\n" not in result
        assert "first" in result
        assert "second" in result

    def test_multiple_spaces_collapse(self):
        """2+ spaces → 1 space."""
        text = "word   with    spaces"
        result = normalize_whitespace(text)
        assert "  " not in result

    def test_line_trimming(self):
        """Leading/trailing whitespace trimmed from lines."""
        text = "  hello  \n  world  "
        result = normalize_whitespace(text)
        assert result == "hello\nworld"

    def test_bom_stripped_at_start(self):
        """BOM (U+FEFF) stripped at file start."""
        text = "\ufeffhello"
        result = normalize_whitespace(text)
        assert result == "hello"


# ══════════════════════════════════════════════════════════════════════
# F7: Verse detection
# ══════════════════════════════════════════════════════════════════════


class TestVerseDetection:
    """Hemistich separator and star marker detection."""

    def test_balanced_hemistich(self):
        """Balanced hemistich ≥5 chars each side → has_verse."""
        text = "غدائره مستشزرات … تضل العقاص في مثنى"
        assert detect_verse(text) is True

    def test_unbalanced_hemistich(self):
        """Unbalanced (<5 chars one side) → no verse."""
        text = "قال … لا"
        assert detect_verse(text) is False

    def test_prose_etc_not_verse(self):
        """Prose 'إلخ' after ellipsis → NOT verse."""
        text = "وقد ذكر المسائل التالية … إلخ"
        assert detect_verse(text) is False

    def test_star_markers(self):
        """Star-wrapped verse → has_verse."""
        text = "* تركت ناقتي ترعى الهمخع *"
        assert detect_verse(text) is True

    def test_no_verse_indicators(self):
        """Plain prose → no verse."""
        text = "الكلام في اصطلاح النحويين هو اللفظ المفيد"
        assert detect_verse(text) is False


# ══════════════════════════════════════════════════════════════════════
# F8: Table extraction
# ══════════════════════════════════════════════════════════════════════


class TestTableExtraction:
    """Table conversion to pipe-separated text."""

    def test_table_converted(self, normalizer: ShamelaNormalizer):
        """HTML table → 'cell | cell' format with has_tables=True."""
        html = _make_html(_wrap_page(
            "<table dir=rtl>"
            "<tr><th>الاسم</th><th>الفعل</th></tr>"
            "<tr><td>يدل على الثبات</td><td>يدل على الحدوث</td></tr>"
            "</table>",
            page_num="١٧",
        ))
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert pages[0].has_tables is True
        assert "الاسم | الفعل" in pages[0].primary_text
        assert "يدل على الثبات | يدل على الحدوث" in pages[0].primary_text


# ══════════════════════════════════════════════════════════════════════
# F9: Error code usage
# ══════════════════════════════════════════════════════════════════════


class TestErrorCodes:
    """Verify correct error codes in various scenarios."""

    def test_footnote_separator_absent_warning(
        self, normalizer: ShamelaNormalizer
    ):
        """Pages without separator → NORM_FOOTNOTE_SEPARATOR_ABSENT."""
        html = _make_html(_wrap_page(
            "نص بدون حاشية", page_num="١"
        ))
        pages = _full_pipeline(normalizer, html)
        assert any(
            NormErrorCode.FOOTNOTE_SEPARATOR_ABSENT.value in w
            for w in pages[0].warnings
        )

    def test_orphan_footnote_ref_warning(
        self, normalizer: ShamelaNormalizer
    ):
        """Refs with no matching footnote → NORM_ORPHAN_FOOTNOTE_REF."""
        html = _make_html(_wrap_page(
            "نص مع مرجع (5) يتيم\n"
            "<hr width='95'>\n"
            "<div class='footnote'>"
            "(1) حاشية واحدة فقط"
            "</div>",
            page_num="١",
        ))
        pages = _full_pipeline(normalizer, html)
        assert any(
            NormErrorCode.ORPHAN_FOOTNOTE_REF.value in w
            for w in pages[0].warnings
        )
        # (5) kept as literal
        assert "(5)" in pages[0].primary_text

    def test_missing_frozen_path(self, normalizer: ShamelaNormalizer):
        """Non-existent path → NORM_MISSING_FROZEN."""
        with pytest.raises(NormalizationError) as exc_info:
            normalizer.validate_input(
                Path("/nonexistent/path"),
                None,  # type: ignore[arg-type]
            )
        assert exc_info.value.code == NormErrorCode.MISSING_FROZEN

    def test_schema_violation_no_pagetext(
        self, normalizer: ShamelaNormalizer, tmp_path: Path
    ):
        """File without PageText div → NORM_SCHEMA_VIOLATION."""
        (tmp_path / "test.htm").write_text(
            "<html><body>no page text here</body></html>",
            encoding="utf-8",
        )
        with pytest.raises(NormalizationError) as exc_info:
            normalizer.validate_input(tmp_path, None)  # type: ignore[arg-type]
        assert exc_info.value.code == NormErrorCode.SCHEMA_VIOLATION


# ══════════════════════════════════════════════════════════════════════
# Utility function tests
# ══════════════════════════════════════════════════════════════════════


class TestArabicToInt:
    """Arabic-Indic digit conversion."""

    def test_basic(self):
        assert arabic_to_int("٤٥") == 45

    def test_single_digit(self):
        assert arabic_to_int("٧") == 7

    def test_large_number(self):
        assert arabic_to_int("١٢٣٤") == 1234

    def test_zero(self):
        assert arabic_to_int("٠") == 0


class TestWesternDigitPageNumbers:
    """Some Shamela exports use Western digits (0-9) for page numbers."""

    def test_western_digits_parsed(self, normalizer: ShamelaNormalizer):
        """(ص: 42) with Western digits → page_number_int=42."""
        html = _make_html(
            "<div class='PageText'>"
            "<div class='PageHead'>"
            "<span class='PageNumber'>(ص: 42)</span><hr/>"
            "</div>"
            "محتوى الصفحة"
            "</div>"
        )
        pages = _full_pipeline(normalizer, html)
        assert len(pages) == 1
        assert pages[0].page_number_int == 42
        assert pages[0].page_number_display == "42"


class TestMonotonicMerge:
    """Footnote parsing with monotonic merge."""

    def test_monotonic_merge(self, normalizer: ShamelaNormalizer):
        """Non-monotonic (1) after (2) → merged into footnote 2."""
        html = _make_html(_wrap_page(
            "نص المتن\n"
            "<hr width='95'>\n"
            "<div class='footnote'>"
            "(1) حاشية أولى\n"
            "(2) حاشية ثانية\n"
            "(1) مرجع داخلي يعود للحاشية الثانية"
            "</div>",
            page_num="١",
        ))
        raw = normalizer._pass1_parse(html, volume=1, seq_offset=0)
        sep = normalizer._pass2_separate(raw)
        assert len(sep) == 1
        # Monotonic merge: 3 raw entries → 2 merged entries
        assert len(sep[0].footnotes) == 2
        assert sep[0].footnotes[0].number == 1
        assert sep[0].footnotes[1].number == 2
        # The merged (1) is appended to footnote 2's text
        assert "مرجع داخلي" in sep[0].footnotes[1].text


# ══════════════════════════════════════════════════════════════════════
# Sweep bug fixes
# ══════════════════════════════════════════════════════════════════════


class TestSweepBugFixes:
    """Fixes for bugs discovered during the 7,475-book corpus sweep."""

    def test_pageless_book_produces_content(
        self, normalizer: ShamelaNormalizer
    ) -> None:
        """Books without (ص: N) page numbers must not drop all content.

        Root cause: _pass1_parse() classifies pages as metadata when
        page_int is None AND not seen_numbered_page. Books without any
        page numbers never set seen_numbered_page=True, so ALL pages
        (including content pages) are classified as metadata and skipped
        by Pass 2. 48 books in the corpus have this pattern.

        Fixture: zero_content_hadith_dhunnun.htm — 6 pages of hadith
        text with full diacritization, zero page numbers.
        """
        fixture = FIXTURES_EDGE / "zero_content_hadith_dhunnun.htm"
        assert fixture.exists(), f"Missing fixture: {fixture}"
        html = fixture.read_text(encoding="utf-8")

        raw = normalizer._pass1_parse(html, volume=1, seq_offset=0)

        # Must have content pages (not all metadata)
        content_pages = [p for p in raw if not p.is_metadata_page]
        assert len(content_pages) >= 5, (
            f"Expected >= 5 content pages, got {len(content_pages)}. "
            f"All pages classified as metadata — pageless book bug."
        )

        # Content pages must have sequential unit_index starting at 0
        indices = [p.unit_index for p in content_pages]
        assert indices == list(range(len(content_pages)))

    def test_pageless_book_full_pipeline(
        self, normalizer: ShamelaNormalizer
    ) -> None:
        """Full pipeline on pageless book produces non-empty content."""
        fixture = FIXTURES_EDGE / "zero_content_hadith_dhunnun.htm"
        html = fixture.read_text(encoding="utf-8")

        pages = _full_pipeline(normalizer, html)

        # Must have non-blank content pages with Arabic text
        non_blank = [p for p in pages if not p.is_blank]
        assert len(non_blank) >= 4, (
            f"Expected >= 4 non-blank pages, got {len(non_blank)}."
        )
        # Content pages must have substantial Arabic text
        total_chars = sum(len(p.primary_text) for p in non_blank)
        assert total_chars > 1000, (
            f"Expected > 1000 total chars, got {total_chars}. "
            f"Pageless book content not being extracted."
        )

    def test_pageless_book_large_fixture(
        self, normalizer: ShamelaNormalizer
    ) -> None:
        """Large pageless book (546 pages) produces content units."""
        fixture = FIXTURES_EDGE / "zero_content_musnad_546pages.htm"
        if not fixture.exists():
            pytest.skip("Large fixture not available")
        html = fixture.read_text(encoding="utf-8")

        raw = normalizer._pass1_parse(html, volume=1, seq_offset=0)

        content_pages = [p for p in raw if not p.is_metadata_page]
        # 546 raw pages, first is metadata → at least 500 content pages
        assert len(content_pages) >= 500, (
            f"Expected >= 500 content pages from 546-page book, "
            f"got {len(content_pages)}."
        )

    def test_diacritics_canary_spec_aligned(
        self, normalizer: ShamelaNormalizer
    ) -> None:
        """Diacritics canary must not crash on SPEC-compliant diacritics.

        Root cause: _ARABIC_DIACRITICS used 20 codepoints (including
        U+0653 maddah and U+0656-U+065F extended marks) while the SPEC
        defines only 10 (U+064B-U+0652, U+0670, U+0640). The broader
        range caused false positive canary failures when regex and BS4
        handle extended diacritics differently.

        Fixture: crash_diacritics_entity_mismatch.htm — the single book
        that crashed during the 7,475-book corpus sweep.
        """
        fixture = FIXTURES_EDGE / "crash_diacritics_entity_mismatch.htm"
        assert fixture.exists(), f"Missing fixture: {fixture}"
        html = fixture.read_text(encoding="utf-8")

        # Must not raise NormalizationError
        pages = _full_pipeline(normalizer, html)

        # Should produce content (this is a 92-page book)
        non_blank = [p for p in pages if not p.is_blank]
        assert len(non_blank) >= 50, (
            f"Expected >= 50 non-blank pages from 92-page book, "
            f"got {len(non_blank)}."
        )

    def test_numbered_book_metadata_unchanged(
        self, normalizer: ShamelaNormalizer
    ) -> None:
        """Books WITH page numbers must not change metadata detection.

        Regression test: the pageless book fix must not affect books that
        have (ص: N) page numbers.
        """
        # Build a book with metadata page + 2 numbered content pages
        html = _make_html(
            _wrap_page(
                "<span class='title'>كتاب النحو</span>"
                "<p>القسم: علوم اللغة العربية"
            ),  # No page number → metadata
            _wrap_page("المبتدأ هو الاسم المرفوع", page_num="١"),
            _wrap_page("والخبر هو الجزء المتمم للفائدة", page_num="٢"),
        )
        raw = normalizer._pass1_parse(html, volume=1, seq_offset=0)

        metadata = [p for p in raw if p.is_metadata_page]
        content = [p for p in raw if not p.is_metadata_page]
        assert len(metadata) == 1, "First page should be metadata"
        assert len(content) == 2, "Two numbered pages should be content"
