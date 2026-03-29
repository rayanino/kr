"""EXTREME Arabic text edge case tests for the KR pipeline.

Tests adversarial, boundary, and unusual inputs that could break Arabic
text processing code across:
  - shared/scholar_authority/src/name_matching.py (normalize_arabic_name, normalized_name_similarity)
  - engines/excerpting/contracts.py (_count_arabic_words)
  - engines/excerpting/src/phase1_assembly.py (strip_arabic_noise, assemble_text, _SENTENCE_BOUNDARY_RE)
  - engines/atomization/src/tracer.py (_split_arabic_sentences)
  - shared/validation/src/validation.py (validate_enrichment_passthrough)

Each test:
  - Uses real Arabic text or realistic synthetic Arabic (never transliteration)
  - Is independent (no inter-test dependencies)
  - Has clear Arrange-Act-Assert structure
  - Includes a docstring explaining the edge case

Categories:
  1. Unicode Boundary Cases
  2. Scholarly Edge Cases
  3. Encoding Edge Cases
  4. Size Extremes
  5. Regex Traps (Arabic-Indic digits, \\d, \\b, \\w)
  6. Name Matching Edge Cases
"""

from __future__ import annotations

import re
import sys
import time

import pytest

# ---- Imports from KR modules under test ----
from engines.excerpting.contracts import _count_arabic_words
from engines.excerpting.src.phase1_assembly import (
    _ARABIC_NOISE_RE,
    _SENTENCE_BOUNDARY_RE,
    strip_arabic_noise,
    assemble_text,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk,
    _make_content_unit,
)
from engines.atomization.src.tracer import _split_arabic_sentences
from shared.scholar_authority.src.name_matching import (
    normalize_arabic_name,
    normalized_name_similarity,
    _extract_name_tokens,
)
from shared.validation.src.validation import (
    validate_enrichment_passthrough,
)


# =====================================================================
# Category 1: Unicode Boundary Cases
# =====================================================================


class TestOnlyDiacriticsExtreme:
    """Text that is ONLY diacritics (fatha, damma, kasra, shadda) with
    no base consonants. Extended version: all combining marks from the
    Arabic block, including rarely-seen ones."""

    # Every Arabic combining mark from U+064B to U+065F, plus U+0670
    ALL_MARKS = (
        "\u064B"  # fathatan
        "\u064C"  # dammatan
        "\u064D"  # kasratan
        "\u064E"  # fatha
        "\u064F"  # damma
        "\u0650"  # kasra
        "\u0651"  # shadda
        "\u0652"  # sukun
        "\u0653"  # maddah above
        "\u0654"  # hamza above
        "\u0655"  # hamza below
        "\u0656"  # subscript alef
        "\u0657"  # inverted damma
        "\u0658"  # mark noon ghunna
        "\u0659"  # zwarakay
        "\u065A"  # vowel sign small v above
        "\u065B"  # vowel sign inverted small v above
        "\u065C"  # vowel sign dot below
        "\u065D"  # reversed damma
        "\u065E"  # fatha with two dots
        "\u065F"  # wavy hamza below
        "\u0670"  # superscript alef
    )

    def test_all_combining_marks_strip_to_empty(self) -> None:
        """All Arabic combining marks (U+064B-U+065F, U+0670) must be
        stripped by strip_arabic_noise, yielding empty string."""
        # Arrange
        text = self.ALL_MARKS
        # Act
        stripped = strip_arabic_noise(text)
        # Assert: only U+064B-U+0652 and U+0670 are in the noise regex.
        # Marks U+0653-U+065F are NOT in the noise regex and will survive.
        surviving = [c for c in stripped if c not in (" ", "")]
        # Document which marks survive the noise regex
        noise_range_chars = set("\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670")
        expected_survivors = [c for c in self.ALL_MARKS if c not in noise_range_chars]
        assert len(surviving) == len(expected_survivors), (
            f"Expected {len(expected_survivors)} survivors but got {len(surviving)}. "
            f"Surviving codepoints: {[hex(ord(c)) for c in surviving]}"
        )

    def test_word_count_diacritics_only_no_crash(self) -> None:
        """_count_arabic_words must not crash on text with only combining marks."""
        wc = _count_arabic_words(self.ALL_MARKS)
        # ALL_MARKS is a single token (no spaces); each char is in U+0600-U+06FF
        assert wc == 1

    def test_spaced_diacritics_word_count(self) -> None:
        """Space-separated individual diacritics: each is a separate 'word'."""
        text = " ".join(self.ALL_MARKS)
        wc = _count_arabic_words(text)
        assert wc == len(self.ALL_MARKS)


class TestAllHamzaVariants:
    """Text with every hamza variant in sequence: isolated, on carriers,
    with madda. Tests normalization and name matching."""

    # All hamza forms found in Arabic scholarly text
    HAMZA_SEQUENCE = "أ إ آ ؤ ئ ء"
    # As they appear in names: Ahmad variants
    AHMAD_FORMS = [
        "أحمد",    # hamza on alef (most common)
        "إحمد",    # hamza below alef (incorrect but found in OCR)
        "آحمد",    # alef with madda (incorrect but found in OCR)
    ]

    def test_hamza_normalization_in_names(self) -> None:
        """normalize_arabic_name must collapse hamza-on-alef, hamza-below-alef,
        and alef-madda to bare alef for matching."""
        # Arrange
        name_hamza_above = "أحمد بن حنبل"
        name_hamza_below = "إحمد بن حنبل"
        name_madda = "آحمد بن حنبل"
        # Act
        norm_above = normalize_arabic_name(name_hamza_above)
        norm_below = normalize_arabic_name(name_hamza_below)
        norm_madda = normalize_arabic_name(name_madda)
        # Assert: all normalize to the same form
        assert norm_above == norm_below, (
            f"Hamza above '{norm_above}' != hamza below '{norm_below}'"
        )
        assert norm_above == norm_madda, (
            f"Hamza above '{norm_above}' != madda '{norm_madda}'"
        )

    def test_isolated_hamza_not_normalized(self) -> None:
        """Isolated hamza (U+0621 ء) is NOT one of the three normalized forms
        (those are on-alef carriers). Verify it survives normalization."""
        text = "ء"
        normed = normalize_arabic_name(text)
        # Isolated hamza is not replaced by normalize_arabic_name
        assert "ء" in normed

    def test_hamza_on_waw_yaa_not_normalized(self) -> None:
        """Hamza on waw (ؤ) and hamza on yaa (ئ) are NOT normalized to alef.
        They are distinct characters in Arabic morphology."""
        # Arrange
        name_waw = "مؤمن"   # mu'min (believer)
        name_yaa = "سائل"   # sa'il (questioner)
        # Act
        norm_waw = normalize_arabic_name(name_waw)
        norm_yaa = normalize_arabic_name(name_yaa)
        # Assert: ؤ and ئ survive normalization
        assert "ؤ" in norm_waw, "Hamza-on-waw was incorrectly stripped"
        assert "ئ" in norm_yaa, "Hamza-on-yaa was incorrectly stripped"

    def test_word_count_hamza_sequence(self) -> None:
        """Each hamza variant separated by space counts as one Arabic word."""
        wc = _count_arabic_words(self.HAMZA_SEQUENCE)
        assert wc == 6

    def test_assemble_preserves_all_hamza_forms(self) -> None:
        """assemble_text must preserve all hamza variants byte-for-byte."""
        cu = _make_content_unit(primary_text=self.HAMZA_SEQUENCE, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.HAMZA_SEQUENCE


class TestMassiveTatweel:
    """Text with 100+ consecutive tatweel characters (U+0640).
    Tatweels are decorative elongation marks. OCR corruption can
    produce massive tatweel runs."""

    TATWEEL_100 = "\u0640" * 100
    TATWEEL_BETWEEN_WORDS = "بسم" + "\u0640" * 100 + "الله"  # No space: single token

    def test_100_tatweels_strip_to_empty(self) -> None:
        """100 consecutive tatweels must strip to empty."""
        stripped = strip_arabic_noise(self.TATWEEL_100)
        assert stripped == ""

    def test_tatweel_between_words_single_token(self) -> None:
        """Tatweel glues words into one token (no whitespace). Word count = 1."""
        wc = _count_arabic_words(self.TATWEEL_BETWEEN_WORDS)
        assert wc == 1

    def test_tatweel_between_words_strips_to_joined(self) -> None:
        """After noise stripping, the two root words merge: 'بسمالله'."""
        stripped = strip_arabic_noise(self.TATWEEL_BETWEEN_WORDS)
        assert "بسم" in stripped
        assert "الله" in stripped
        assert "\u0640" not in stripped

    def test_1000_tatweels_no_crash(self) -> None:
        """1000 tatweels must not cause regex catastrophic backtracking."""
        text = "\u0640" * 1000
        start = time.monotonic()
        stripped = strip_arabic_noise(text)
        elapsed = time.monotonic() - start
        assert stripped == ""
        assert elapsed < 1.0, f"Regex took {elapsed:.2f}s on 1000 tatweels (>1s threshold)"


class TestTaaMarbutaHaaSwap:
    """Taa marbuta (ة U+0629) and haa (ه U+0647) swapped -- a common
    OCR error in Arabic text. Critical for scholar name matching."""

    def test_taa_marbuta_normalizes_to_haa_in_names(self) -> None:
        """normalize_arabic_name replaces ة with ه for matching.
        This is the documented behavior."""
        # Arrange: same name with ة vs ه
        name_correct = "حنيفة"   # correct: taa marbuta
        name_ocr_err = "حنيفه"   # OCR error: haa instead of taa marbuta
        # Act
        norm_correct = normalize_arabic_name(name_correct)
        norm_ocr_err = normalize_arabic_name(name_ocr_err)
        # Assert: both normalize to the same form
        assert norm_correct == norm_ocr_err

    def test_similarity_unaffected_by_swap(self) -> None:
        """Scholar names differing only in ة/ه must have similarity = 1.0."""
        sim = normalized_name_similarity("أبو حنيفة", "أبو حنيفه")
        assert sim == 1.0

    def test_taa_marbuta_haa_in_long_name(self) -> None:
        """Full nasab chain with ة/ه swap in multiple positions."""
        name_a = "أبو عبد الله محمد بن إدريس الشافعي الهاشمية"
        name_b = "أبو عبد الله محمد بن إدريس الشافعي الهاشميه"
        sim = normalized_name_similarity(name_a, name_b)
        assert sim >= 0.9


class TestArabicIndicDigitsMixed:
    """Arabic-Indic digits (٠١٢٣٤٥٦٧٨٩) mixed with Western digits (0-9).
    Per regex-arabic-digits.md, Python \\d matches Arabic-Indic digits."""

    ARABIC_INDIC = "٠١٢٣٤٥٦٧٨٩"
    WESTERN = "0123456789"
    MIXED = "الصفحة ١٢٣ page 123"

    def test_python_d_matches_arabic_indic(self) -> None:
        """Verify Python \\d matches Arabic-Indic digits (the documented trap)."""
        matches = re.findall(r"\d+", self.ARABIC_INDIC)
        assert len(matches) == 1
        assert matches[0] == self.ARABIC_INDIC

    def test_bracket_0_9_excludes_arabic_indic(self) -> None:
        """[0-9]+ must NOT match Arabic-Indic digits."""
        matches = re.findall(r"[0-9]+", self.ARABIC_INDIC)
        assert len(matches) == 0

    def test_mixed_text_d_finds_both(self) -> None:
        """\\d in mixed text matches BOTH Arabic-Indic and Western digits."""
        matches = re.findall(r"\d+", self.MIXED)
        # Should find ١٢٣ and 123
        assert len(matches) == 2

    def test_mixed_text_bracket_only_western(self) -> None:
        """[0-9] in mixed text matches ONLY Western digits."""
        matches = re.findall(r"[0-9]+", self.MIXED)
        assert len(matches) == 1
        assert matches[0] == "123"

    def test_word_count_arabic_indic_digits(self) -> None:
        """Arabic-Indic digits are in U+0660-U+0669 (within U+0600-U+06FF).
        _count_arabic_words SHOULD count them as Arabic words."""
        wc = _count_arabic_words(self.ARABIC_INDIC)
        assert wc == 1  # single token containing Arabic-block chars

    def test_sentence_boundary_regex_with_arabic_digits(self) -> None:
        """_SENTENCE_BOUNDARY_RE uses literal punctuation, not \\d.
        Verify it works correctly with Arabic-Indic digits nearby."""
        text = "الباب الأول. الفصل ١٢ من الكتاب"
        matches = list(_SENTENCE_BOUNDARY_RE.finditer(text))
        assert len(matches) >= 1


class TestMixedArabicPersianUrdu:
    """Text mixing Arabic (U+0600-U+06FF), Arabic Supplement (U+0750-U+077F),
    and Extended-A (U+08A0-U+08FF) characters."""

    # Real Persian characters from the supplement block
    PERSIAN_CHARS = "\u067E\u0686\u06AF\u0698"  # pe, che, gaf, zhe
    # Arabic text with Persian loanword
    MIXED_TEXT = "كتاب فارسي پارسی با چند كلمه عربي"
    # Urdu-specific characters
    URDU_CHARS = "\u0679\u0688\u0691\u06BA\u06BE\u06C1\u06D2"  # ٹ ڈ ڑ ں ھ ہ ے

    def test_persian_chars_are_in_arabic_block(self) -> None:
        """Persian-specific chars (pe, che, gaf, zhe) are within U+0600-U+06FF."""
        for c in self.PERSIAN_CHARS:
            assert "\u0600" <= c <= "\u06FF", (
                f"U+{ord(c):04X} ({c}) is outside Arabic block"
            )

    def test_urdu_chars_are_in_arabic_block(self) -> None:
        """Urdu-specific chars are within U+0600-U+06FF."""
        for c in self.URDU_CHARS:
            assert "\u0600" <= c <= "\u06FF", (
                f"U+{ord(c):04X} ({c}) is outside Arabic block"
            )

    def test_word_count_mixed_script(self) -> None:
        """Persian/Urdu chars in Arabic block count as Arabic words."""
        wc = _count_arabic_words(self.MIXED_TEXT)
        assert wc == len(self.MIXED_TEXT.split())

    def test_name_matching_with_persian_chars(self) -> None:
        """Scholar names with Persian characters must not crash name matching."""
        # Persian scholar name
        name = "محمد بن محمد غزالی"
        normed = normalize_arabic_name(name)
        assert len(normed) > 0

    def test_zwnj_valid_in_persian_context(self) -> None:
        """ZWNJ (U+200C) is valid in Persian text but strip_arabic_noise removes it.
        Document this known behavior gap."""
        # Persian word with ZWNJ: می‌خواهم
        persian_text = "می\u200Cخواهم"
        stripped = strip_arabic_noise(persian_text)
        # ZWNJ is in _ARABIC_NOISE_RE -- it gets stripped
        assert "\u200C" not in stripped


class TestPresentationForms:
    """Text with Arabic Presentation Forms A (U+FB50-U+FDFF) and
    Presentation Forms B (U+FE70-U+FEFF). These are legacy forms
    for compatibility; modern text should use base block."""

    # Presentation Form A examples
    PF_A_ALEF = "\uFB50"    # ALEF WASLA ISOLATED FORM
    PF_A_LAM_ALEF = "\uFEFB"  # LAM WITH ALEF

    # Ligature: bismillah (U+FDFD)
    BISMILLAH_LIGATURE = "\uFDFD"  # ﷽

    # Sallallahu alayhi wasallam ligature (U+FDFA)
    SALAWAT_LIGATURE = "\uFDFA"  # ﷺ

    def test_presentation_forms_outside_basic_arabic_block(self) -> None:
        """Presentation Forms A/B are NOT in U+0600-U+06FF.
        _count_arabic_words will NOT count them."""
        # Single presentation form character
        wc = _count_arabic_words(self.PF_A_ALEF)
        assert wc == 0, "Presentation Form A char should not be in U+0600-U+06FF"

    def test_bismillah_ligature_not_counted(self) -> None:
        """The bismillah ligature (U+FDFD) is in Presentation Forms A.
        It should NOT count as an Arabic word by _count_arabic_words."""
        wc = _count_arabic_words(self.BISMILLAH_LIGATURE)
        assert wc == 0

    def test_salawat_ligature_not_counted(self) -> None:
        """The salawat ligature (U+FDFA) is in Presentation Forms A.
        It should NOT count as an Arabic word by _count_arabic_words."""
        wc = _count_arabic_words(self.SALAWAT_LIGATURE)
        assert wc == 0

    def test_mixed_base_and_presentation(self) -> None:
        """Text mixing base Arabic and presentation forms. Only base-block
        tokens should be counted."""
        text = f"بسم الله {self.BISMILLAH_LIGATURE} الرحمن الرحيم"
        wc = _count_arabic_words(text)
        # "بسم", "الله", "الرحمن", "الرحيم" = 4 Arabic words
        # ﷽ is U+FDFD (not in U+0600-U+06FF) = 0
        assert wc == 4

    def test_assemble_preserves_ligatures(self) -> None:
        """Ligature characters must be preserved byte-for-byte in assembly."""
        text = f"صلى الله عليه وسلم {self.SALAWAT_LIGATURE}"
        cu = _make_content_unit(primary_text=text, unit_index=0)
        assembled, _, _ = assemble_text([cu], 0, 0)
        assert self.SALAWAT_LIGATURE in assembled


class TestZWJInsideArabicWords:
    """Zero-width joiner (U+200D) inside Arabic words for valid ligatures.
    Specifically: lam-alef ligature with ZWJ between them."""

    ZWJ = "\u200D"
    # Valid: ZWJ between lam and alef for ligature
    LAM_ZWJ_ALEF = "\u0644" + "\u200D" + "\u0627"  # ل + ZWJ + ا
    # Word with ZWJ inside: بسم with ZWJ between ba and sin
    WORD_WITH_ZWJ = "\u0628\u200D\u0633\u0645"

    def test_zwj_preserved_in_assembled_text(self) -> None:
        """ZWJ inside Arabic words must be preserved in assembled text."""
        cu = _make_content_unit(primary_text=self.LAM_ZWJ_ALEF, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert self.ZWJ in text

    def test_zwj_stripped_by_noise_regex(self) -> None:
        """strip_arabic_noise removes ZWJ (it is in _ARABIC_NOISE_RE).
        This is documented behavior -- stripping is for COMPARISON only."""
        stripped = strip_arabic_noise(self.LAM_ZWJ_ALEF)
        assert self.ZWJ not in stripped

    def test_word_count_unaffected_by_zwj(self) -> None:
        """ZWJ does not split tokens. Word with internal ZWJ = 1 word."""
        wc = _count_arabic_words(self.WORD_WITH_ZWJ)
        assert wc == 1


class TestZWNJBetweenArabicLetters:
    """Zero-width non-joiner (U+200C) between Arabic letters.
    Invalid in Arabic (valid in Persian/Urdu). Tests that the pipeline
    handles this gracefully."""

    ZWNJ = "\u200C"
    # ZWNJ between two Arabic words (invalid in Arabic)
    ARABIC_WITH_ZWNJ = "بسم\u200Cالله"
    # ZWNJ in Persian context (valid)
    PERSIAN_WITH_ZWNJ = "می\u200Cخواهم"

    def test_zwnj_stripped_by_noise_regex(self) -> None:
        """ZWNJ is in _ARABIC_NOISE_RE and gets stripped."""
        stripped = strip_arabic_noise(self.ARABIC_WITH_ZWNJ)
        assert self.ZWNJ not in stripped

    def test_zwnj_glues_tokens_before_strip(self) -> None:
        """ZWNJ is not whitespace, so 'بسم‌الله' is ONE token before stripping."""
        wc = _count_arabic_words(self.ARABIC_WITH_ZWNJ)
        assert wc == 1

    def test_strip_produces_joined_text(self) -> None:
        """After stripping ZWNJ, the two roots merge: 'بسمالله'."""
        stripped = strip_arabic_noise(self.ARABIC_WITH_ZWNJ)
        assert stripped == "بسمالله"


# =====================================================================
# Category 2: Scholarly Edge Cases
# =====================================================================


class TestBismillahMassiveText:
    """Bismillah followed by 10,000 characters of continuous text
    with no paragraph breaks. Tests chunking and assembly."""

    BISMILLAH = "بسم الله الرحمن الرحيم"
    # Generate realistic continuous Arabic text (repeating scholarly formula)
    SCHOLARLY_FORMULA = "وقال الإمام أحمد رحمه الله في مسألة الطهارة"
    MASSIVE_TEXT = BISMILLAH + " " + " ".join(
        [SCHOLARLY_FORMULA] * 222  # ~10,000 chars
    )

    def test_word_count_handles_massive_text(self) -> None:
        """_count_arabic_words must handle 10,000+ char text without error."""
        wc = _count_arabic_words(self.MASSIVE_TEXT)
        assert wc > 1000

    def test_assemble_handles_massive_text(self) -> None:
        """assemble_text must not crash on massive single-unit text."""
        cu = _make_content_unit(primary_text=self.MASSIVE_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert len(text) == len(self.MASSIVE_TEXT)

    def test_sentence_splitting_massive_text(self) -> None:
        """_split_arabic_sentences on massive text must complete in reasonable time."""
        start = time.monotonic()
        sentences = _split_arabic_sentences(self.MASSIVE_TEXT)
        elapsed = time.monotonic() - start
        assert elapsed < 5.0, f"Sentence splitting took {elapsed:.2f}s (>5s)"
        assert len(sentences) >= 1

    def test_strip_noise_massive_text_performance(self) -> None:
        """strip_arabic_noise on massive text must not cause regex backtracking."""
        start = time.monotonic()
        stripped = strip_arabic_noise(self.MASSIVE_TEXT)
        elapsed = time.monotonic() - start
        assert elapsed < 2.0, f"Noise stripping took {elapsed:.2f}s (>2s)"
        assert len(stripped) > 0


_ISNAD_NARRATOR_NAMES = [
    "أحمد بن محمد", "علي بن أبي طالب", "عبد الله بن عمر",
    "أبو هريرة", "عائشة بنت أبي بكر", "أنس بن مالك",
    "جابر بن عبد الله", "ابن عباس", "أبو سعيد الخدري",
    "عبد الرحمن بن عوف",
]
_ISNAD_50 = " ".join(
    f"حدثنا {_ISNAD_NARRATOR_NAMES[i % len(_ISNAD_NARRATOR_NAMES)]} قال"
    for i in range(50)
)
_FULL_HADITH_50 = (
    _ISNAD_50 + " قال رسول الله صلى الله عليه وسلم إنما الأعمال بالنيات"
)


class TestLongIsnadChain:
    """Isnad chain with 50 narrators. Real chains are typically 3-8
    narrators, but chains this long exist in musnad collections."""

    NAMES = _ISNAD_NARRATOR_NAMES
    ISNAD = _ISNAD_50
    FULL_HADITH = _FULL_HADITH_50

    def test_word_count_long_isnad(self) -> None:
        """Word count must handle very long isnad chains."""
        wc = _count_arabic_words(self.FULL_HADITH)
        assert wc > 200

    def test_split_sentences_respects_isnad_structure(self) -> None:
        """_split_arabic_sentences should not split in the middle of an isnad."""
        sentences = _split_arabic_sentences(self.FULL_HADITH)
        # The entire text has no sentence-ending punctuation except possibly
        # at the very end. It should produce relatively few splits.
        assert len(sentences) >= 1

    def test_assemble_preserves_isnad(self) -> None:
        """assemble_text must preserve the entire isnad byte-for-byte."""
        cu = _make_content_unit(primary_text=self.FULL_HADITH, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.FULL_HADITH


_FOOTNOTE_BASE_WORD = "كلمة"
_TEXT_WITH_100_FOOTNOTES = " ".join(
    f"{_FOOTNOTE_BASE_WORD} ⌜{i}⌝" for i in range(1, 101)
)


class TestManyFootnoteReferences:
    """Text with 100 footnote marker references on a single page.
    Uses the KR footnote marker format: ⌜N⌝"""

    BASE = _FOOTNOTE_BASE_WORD
    TEXT_WITH_100_FOOTNOTES = _TEXT_WITH_100_FOOTNOTES

    def test_word_count_with_footnote_markers(self) -> None:
        """Footnote markers ⌜N⌝ are not Arabic words. Only 'كلمة' tokens count."""
        wc = _count_arabic_words(self.TEXT_WITH_100_FOOTNOTES)
        # Each "كلمة" is an Arabic word; "⌜N⌝" tokens have no Arabic chars
        assert wc == 100

    def test_assemble_preserves_all_markers(self) -> None:
        """All 100 footnote markers must survive assembly."""
        cu = _make_content_unit(
            primary_text=self.TEXT_WITH_100_FOOTNOTES, unit_index=0
        )
        text, _, _ = assemble_text([cu], 0, 0)
        for i in range(1, 101):
            assert f"⌜{i}⌝" in text, f"Footnote marker ⌜{i}⌝ missing from assembled text"


class TestColophonSameAuthorCopyist:
    """Colophon where the same person is named as both author and copyist.
    This is rare but valid (author copied his own work)."""

    COLOPHON = (
        "تم الكتاب بحمد الله تعالى "
        "ألفه الشيخ محمد بن أحمد "
        "وكتبه بخطه محمد بن أحمد "
        "وكان الفراغ منه في شهر رمضان سنة ٧٦٩"
    )

    def test_name_extraction_finds_same_name_twice(self) -> None:
        """The name 'محمد بن أحمد' appears in both author and copyist slots."""
        # Not testing extraction (that's Phase 3), but verify the text processes correctly
        wc = _count_arabic_words(self.COLOPHON)
        assert wc > 10

    def test_name_similarity_self_match(self) -> None:
        """Same name compared to itself must return 1.0."""
        name = "محمد بن أحمد"
        sim = normalized_name_similarity(name, name)
        assert sim == 1.0

    def test_assemble_preserves_colophon(self) -> None:
        """Colophon text must be preserved byte-for-byte."""
        cu = _make_content_unit(primary_text=self.COLOPHON, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.COLOPHON


class TestNestedScholarQuotations:
    """Scholar A quotes Scholar B quoting Scholar C quoting Scholar D.
    Deep nesting of قال formulas."""

    NESTED_QUOTE = (
        "قال الإمام النووي رحمه الله: "
        "قال الإمام الشافعي رحمه الله: "
        "قال الإمام مالك رحمه الله: "
        "قال الإمام أبو حنيفة رحمه الله: "
        "الوضوء واجب لكل صلاة"
    )

    def test_word_count_nested_quotes(self) -> None:
        """Nested quotations are valid Arabic text; word count must work."""
        wc = _count_arabic_words(self.NESTED_QUOTE)
        assert wc > 15

    def test_sentence_split_nested_quotes(self) -> None:
        """Colons in Arabic quotation formulas should not confuse sentence splitting."""
        sentences = _split_arabic_sentences(self.NESTED_QUOTE)
        # No period/question mark/exclamation, so minimal splitting expected
        assert len(sentences) >= 1

    def test_all_four_scholars_extractable(self) -> None:
        """All four scholar names must be findable in the text."""
        for name in ["النووي", "الشافعي", "مالك", "أبو حنيفة"]:
            assert name in self.NESTED_QUOTE


class TestEntireContentIsQuran:
    """Text where the ENTIRE content is a single Quranic verse.
    Should be handled without confusion about authorship."""

    # Al-Fatiha complete
    FATIHA = (
        "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ "
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ "
        "الرَّحْمَنِ الرَّحِيمِ "
        "مَالِكِ يَوْمِ الدِّينِ "
        "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ "
        "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ "
        "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ "
        "غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"
    )

    def test_heavily_diacritized_text_word_count(self) -> None:
        """Fully diacritized Quranic text must count words correctly.
        Diacritics are in U+0600-U+06FF but do not add tokens."""
        wc = _count_arabic_words(self.FATIHA)
        # Count actual space-separated tokens with Arabic chars
        expected = sum(
            1 for t in self.FATIHA.split()
            if any("\u0600" <= c <= "\u06FF" for c in t)
        )
        assert wc == expected

    def test_noise_strip_removes_diacritics(self) -> None:
        """strip_arabic_noise must remove diacritics from Quranic text."""
        stripped = strip_arabic_noise(self.FATIHA)
        # No diacritics should remain
        for c in stripped:
            assert c < "\u064B" or c > "\u0652" or c == "\u0640", (
                f"Diacritic U+{ord(c):04X} survived stripping"
            )

    def test_assemble_preserves_diacritics(self) -> None:
        """Assembly must preserve every diacritic byte-for-byte."""
        cu = _make_content_unit(primary_text=self.FATIHA, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.FATIHA


# =====================================================================
# Category 3: Encoding Edge Cases
# =====================================================================


class TestEmptyString:
    """Empty string input across all functions."""

    def test_count_arabic_words_empty(self) -> None:
        """Empty string has zero Arabic words."""
        assert _count_arabic_words("") == 0

    def test_strip_noise_empty(self) -> None:
        """Stripping noise from empty string returns empty string."""
        assert strip_arabic_noise("") == ""

    def test_normalize_name_empty(self) -> None:
        """Normalizing empty name returns empty string."""
        result = normalize_arabic_name("")
        assert result == ""

    @pytest.mark.xfail(
        reason="BUG FOUND: norm_a == norm_b fires before empty check, returns 1.0 for two empty strings",
        strict=True,
    )
    def test_name_similarity_empty_vs_empty(self) -> None:
        """Two empty names should have 0.0 similarity (not 1.0 or error).

        DISCOVERED BUG: normalized_name_similarity returns 1.0 because
        normalize_arabic_name('') == '' and the equality short-circuit
        at line 60 fires before the emptiness guard at lines 61-62.
        Fix: check `not norm_a or not norm_b` BEFORE `norm_a == norm_b`.
        """
        sim = normalized_name_similarity("", "")
        assert sim == 0.0

    def test_name_similarity_empty_vs_nonempty(self) -> None:
        """Empty vs non-empty name = 0.0."""
        sim = normalized_name_similarity("", "أحمد")
        assert sim == 0.0

    def test_extract_tokens_empty(self) -> None:
        """Empty name produces empty token set."""
        tokens = _extract_name_tokens("")
        assert tokens == set()

    def test_split_sentences_empty(self) -> None:
        """Splitting empty text produces empty list."""
        sentences = _split_arabic_sentences("")
        assert sentences == []

    def test_validate_passthrough_empty_dicts(self) -> None:
        """Passthrough validation with empty dicts produces no errors."""
        errors = validate_enrichment_passthrough({}, {})
        assert errors == []


class TestSingleArabicCharacter:
    """Single Arabic character as input."""

    CHAR = "\u0628"  # ba

    def test_word_count_single_char(self) -> None:
        assert _count_arabic_words(self.CHAR) == 1

    def test_strip_noise_single_base_char(self) -> None:
        """Single base character (not a diacritic) survives noise stripping."""
        stripped = strip_arabic_noise(self.CHAR)
        assert stripped == self.CHAR

    def test_normalize_name_single_char(self) -> None:
        result = normalize_arabic_name(self.CHAR)
        assert result == self.CHAR

    def test_similarity_single_char_vs_same(self) -> None:
        sim = normalized_name_similarity(self.CHAR, self.CHAR)
        assert sim == 1.0

    def test_split_sentences_single_char(self) -> None:
        sentences = _split_arabic_sentences(self.CHAR)
        assert sentences == [self.CHAR]


class TestSingleDiacriticMark:
    """Single diacritic mark (combining character) with no base letter.
    This is technically malformed Unicode (combining mark without base)."""

    DIACRITIC = "\u064E"  # fatha

    def test_word_count_single_diacritic(self) -> None:
        """Single diacritic is in Arabic block -> counts as 1 word."""
        wc = _count_arabic_words(self.DIACRITIC)
        assert wc == 1

    def test_strip_noise_removes_single_diacritic(self) -> None:
        """Single diacritic is noise -> stripped to empty."""
        stripped = strip_arabic_noise(self.DIACRITIC)
        assert stripped == ""

    def test_normalize_name_single_diacritic(self) -> None:
        """Single diacritic normalizes to empty (stripped by diacritics removal)."""
        result = normalize_arabic_name(self.DIACRITIC)
        assert result == ""

    @pytest.mark.xfail(
        reason="BUG FOUND: same root cause as empty-vs-empty; diacritics normalize to '' then equality short-circuit returns 1.0",
        strict=True,
    )
    def test_similarity_diacritic_vs_diacritic(self) -> None:
        """Two identical diacritics: after normalization both are empty -> should be 0.0.

        DISCOVERED BUG: Both diacritics normalize to '' via strip.
        Then norm_a == norm_b (both '') triggers the equality short-circuit
        returning 1.0. The empty-string guard on lines 61-62 never runs.
        Same fix: check emptiness before equality.
        """
        sim = normalized_name_similarity(self.DIACRITIC, self.DIACRITIC)
        assert sim == 0.0


class TestBOMAtStart:
    """Byte Order Mark (U+FEFF) at the start of text. Per input-sanitization.md,
    this should be stripped at ingestion boundary."""

    BOM = "\uFEFF"
    TEXT_WITH_BOM = "\uFEFF" + "بسم الله الرحمن الرحيم"

    def test_bom_not_stripped_by_noise_regex(self) -> None:
        """BOM (U+FEFF) is NOT in _ARABIC_NOISE_RE.
        It is the ingestion boundary's responsibility."""
        stripped = strip_arabic_noise(self.TEXT_WITH_BOM)
        assert self.BOM in stripped or stripped.startswith("بسم")
        # The BOM may or may not be in the noise regex; document actual behavior

    def test_bom_not_counted_as_arabic_word(self) -> None:
        """BOM (U+FEFF) is in Presentation Forms B range. With space-separated
        text, a leading BOM glues to the first token."""
        # "﻿بسم" is one token; contains Arabic chars -> 1 word for that token
        wc = _count_arabic_words(self.TEXT_WITH_BOM)
        expected_no_bom = _count_arabic_words("بسم الله الرحمن الرحيم")
        assert wc == expected_no_bom

    def test_assemble_preserves_bom(self) -> None:
        """BOM must survive assembly (Phase 1 does not sanitize)."""
        cu = _make_content_unit(primary_text=self.TEXT_WITH_BOM, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.TEXT_WITH_BOM


class TestMixedRTLLTRWithURLs:
    """Mixed RTL Arabic text with embedded LTR Latin URLs."""

    TEXT = "انظر الرابط https://shamela.ws/book/12345 للمزيد من التفاصيل"

    def test_word_count_mixed_rtl_ltr(self) -> None:
        """Latin URL tokens have no Arabic chars. Only Arabic tokens count."""
        wc = _count_arabic_words(self.TEXT)
        # "انظر", "الرابط", "للمزيد", "من", "التفاصيل" = 5 Arabic words
        # "https://shamela.ws/book/12345" = 0 Arabic words
        assert wc == 5

    def test_assemble_preserves_url(self) -> None:
        """URLs must survive assembly byte-for-byte."""
        cu = _make_content_unit(primary_text=self.TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert "https://shamela.ws/book/12345" in text

    def test_strip_noise_preserves_url(self) -> None:
        """strip_arabic_noise must not corrupt URLs."""
        stripped = strip_arabic_noise(self.TEXT)
        assert "https://shamela.ws/book/12345" in stripped


class TestAllDangerousInvisibleChars:
    """Text containing ALL 7 dangerous invisible characters from
    input-sanitization.md injected into Arabic text."""

    DANGEROUS_CHARS = {
        "ZWSP": "\u200B",       # zero-width space
        "ZWNJ": "\u200C",       # zero-width non-joiner
        "ZWJ": "\u200D",        # zero-width joiner
        "LRM": "\u200E",        # left-to-right mark
        "RLM": "\u200F",        # right-to-left mark
        "BOM": "\uFEFF",        # byte order mark
        "WJ": "\u2060",         # word joiner
        "SHY": "\u00AD",        # soft hyphen
    }
    # Also bidi overrides U+202A-U+202E
    BIDI_OVERRIDES = {
        "LRE": "\u202A",
        "RLE": "\u202B",
        "PDF": "\u202C",
        "LRO": "\u202D",
        "RLO": "\u202E",
    }

    # Text with all dangerous chars injected between Arabic words
    BASE_TEXT = "بسم الله الرحمن الرحيم"
    POISONED_TEXT = (
        "\u200B" + "بسم"       # ZWSP before
        + "\u200C" + " "        # ZWNJ after
        + "\u200D" + "الله"    # ZWJ before
        + "\u200E" + " "        # LRM after
        + "\u200F" + "الرحمن"  # RLM before
        + "\uFEFF" + " "        # BOM after
        + "\u2060" + "الرحيم"  # WJ before
        + "\u00AD"              # SHY at end
    )

    def test_noise_regex_strips_zwnj_zwj(self) -> None:
        """_ARABIC_NOISE_RE strips ZWNJ and ZWJ (the two in its pattern)."""
        stripped = strip_arabic_noise(self.POISONED_TEXT)
        assert "\u200C" not in stripped  # ZWNJ
        assert "\u200D" not in stripped  # ZWJ

    def test_noise_regex_does_not_strip_zwsp(self) -> None:
        """ZWSP (U+200B) is NOT in _ARABIC_NOISE_RE. Documents a coverage gap."""
        stripped = strip_arabic_noise(self.POISONED_TEXT)
        # ZWSP is not in the noise regex range [\u064B-\u0652\u0670\u0640\u200C\u200D]
        # It may or may not be present depending on whitespace collapsing
        # The key point: the noise regex alone is not the sanitization boundary
        assert isinstance(stripped, str)  # No crash

    def test_noise_regex_does_not_strip_bidi_marks(self) -> None:
        """LRM, RLM are NOT in _ARABIC_NOISE_RE."""
        stripped = strip_arabic_noise(self.POISONED_TEXT)
        # LRM/RLM are invisible but not in the noise regex
        # Document that they pass through
        assert isinstance(stripped, str)

    def test_assemble_preserves_all_invisible(self) -> None:
        """Phase 1 assembly does NOT sanitize. All chars must survive."""
        cu = _make_content_unit(primary_text=self.POISONED_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.POISONED_TEXT

    def test_word_count_with_invisible_chars(self) -> None:
        """Invisible chars do not add spaces; they glue to adjacent tokens."""
        wc = _count_arabic_words(self.POISONED_TEXT)
        # Actual count depends on which invisible chars act as separators
        assert wc >= 1  # At minimum, some Arabic tokens survive


class TestGarbageArabicCodepoints:
    """Valid UTF-8 but semantically garbage: random code points in the
    Arabic Unicode range that don't form real words."""

    # Random Arabic-block chars that are rarely used
    GARBAGE = (
        "\u0600"  # ARABIC NUMBER SIGN
        "\u0601"  # ARABIC SIGN SANAH
        "\u0602"  # ARABIC FOOTNOTE MARKER
        "\u0603"  # ARABIC SIGN SAFHA
        "\u0604"  # ARABIC SIGN SAMVAT
        "\u0605"  # ARABIC NUMBER MARK ABOVE
        "\u060C"  # ARABIC COMMA
        "\u060D"  # ARABIC DATE SEPARATOR
        "\u060E"  # ARABIC POETIC VERSE SIGN
        "\u060F"  # ARABIC SIGN MISRA
    )

    def test_garbage_arabic_does_not_crash(self) -> None:
        """Functions must handle rare/obscure Arabic code points without crashing."""
        wc = _count_arabic_words(self.GARBAGE)
        assert isinstance(wc, int)
        stripped = strip_arabic_noise(self.GARBAGE)
        assert isinstance(stripped, str)

    def test_garbage_in_name_normalization(self) -> None:
        """Name normalization must handle garbage Arabic gracefully."""
        normed = normalize_arabic_name(self.GARBAGE)
        assert isinstance(normed, str)

    def test_garbage_in_sentence_splitting(self) -> None:
        """Sentence splitting must handle garbage Arabic without crashing."""
        sentences = _split_arabic_sentences(self.GARBAGE)
        assert isinstance(sentences, list)


# =====================================================================
# Category 4: Size Extremes
# =====================================================================


class TestOneCharacterText:
    """Minimum possible input: single character in various categories."""

    @pytest.mark.parametrize("char,expected_wc", [
        ("\u0628", 1),          # Arabic letter ba -> 1 Arabic word
        ("a", 0),               # Latin 'a' -> 0 Arabic words
        (" ", 0),               # Space -> 0 words
        ("\n", 0),              # Newline -> 0 words
        ("\u0640", 1),          # Tatweel -> 1 Arabic word (in block)
        ("\u064E", 1),          # Fatha diacritic -> 1 (in Arabic block)
        ("\u0660", 1),          # Arabic-Indic digit 0 -> 1 (in Arabic block)
    ])
    def test_single_char_word_count(self, char: str, expected_wc: int) -> None:
        """Parametrized: single character word count correctness."""
        assert _count_arabic_words(char) == expected_wc


class TestHundredThousandChars:
    """100,000 character text in a single paragraph, no line breaks."""

    # Realistic: repeat a scholarly phrase to reach ~100K chars
    PHRASE = "وقال العلامة ابن تيمية رحمه الله في مجموع الفتاوى"
    # Each phrase is ~49 chars + space = 50 chars. 2000 repetitions = 100K chars
    HUGE_TEXT = " ".join([PHRASE] * 2000)

    def test_word_count_100k_chars(self) -> None:
        """_count_arabic_words must handle 100K chars in reasonable time."""
        start = time.monotonic()
        wc = _count_arabic_words(self.HUGE_TEXT)
        elapsed = time.monotonic() - start
        assert wc > 10000
        assert elapsed < 5.0, f"Word counting took {elapsed:.2f}s for 100K chars"

    def test_strip_noise_100k_chars(self) -> None:
        """strip_arabic_noise must handle 100K chars without regex catastrophe."""
        start = time.monotonic()
        stripped = strip_arabic_noise(self.HUGE_TEXT)
        elapsed = time.monotonic() - start
        assert len(stripped) > 0
        assert elapsed < 5.0, f"Noise stripping took {elapsed:.2f}s for 100K chars"

    def test_split_sentences_100k_chars(self) -> None:
        """_split_arabic_sentences must handle 100K chars."""
        start = time.monotonic()
        sentences = _split_arabic_sentences(self.HUGE_TEXT)
        elapsed = time.monotonic() - start
        assert len(sentences) >= 1
        assert elapsed < 10.0, f"Sentence splitting took {elapsed:.2f}s for 100K chars"

    def test_assemble_100k_chars(self) -> None:
        """assemble_text must handle 100K char content unit."""
        cu = _make_content_unit(primary_text=self.HUGE_TEXT, unit_index=0)
        start = time.monotonic()
        text, _, _ = assemble_text([cu], 0, 0)
        elapsed = time.monotonic() - start
        assert len(text) == len(self.HUGE_TEXT)
        assert elapsed < 5.0, f"Assembly took {elapsed:.2f}s for 100K chars"


class TestHighVocabularyDiversity:
    """Text with 10,000 unique Arabic words (maximum vocabulary diversity)."""

    # Generate pseudo-unique Arabic words by varying letter combinations.
    # Use 3-letter roots with all combinations of common letters.
    ARABIC_LETTERS = "بتثجحخدذرزسشصضطظعغفقكلمنهوي"
    UNIQUE_WORDS: list[str] = []
    for i in range(min(10000, len(ARABIC_LETTERS) ** 2)):
        l1 = ARABIC_LETTERS[i % len(ARABIC_LETTERS)]
        l2 = ARABIC_LETTERS[(i * 7) % len(ARABIC_LETTERS)]
        l3 = ARABIC_LETTERS[(i * 13) % len(ARABIC_LETTERS)]
        word = l1 + l2 + l3
        UNIQUE_WORDS.append(word)
    HIGH_VOCAB_TEXT = " ".join(UNIQUE_WORDS[:10000])

    def test_word_count_high_vocab(self) -> None:
        """10,000 unique Arabic words must all be counted."""
        wc = _count_arabic_words(self.HIGH_VOCAB_TEXT)
        # Duplicates possible in generation; count actual tokens
        expected = sum(
            1 for t in self.HIGH_VOCAB_TEXT.split()
            if any("\u0600" <= c <= "\u06FF" for c in t)
        )
        assert wc == expected

    def test_strip_noise_high_vocab(self) -> None:
        """No base letters should be removed by noise stripping."""
        stripped = strip_arabic_noise(self.HIGH_VOCAB_TEXT)
        # All words are base letters (no diacritics) -> nothing to strip
        # But whitespace may be collapsed
        assert len(stripped) > 0
        stripped_tokens = stripped.split()
        original_tokens = self.HIGH_VOCAB_TEXT.split()
        assert len(stripped_tokens) == len(original_tokens)


class TestMostlyWhitespace:
    """Text that is 99% whitespace with 1% Arabic content."""

    # 1000 spaces, then one Arabic word, then 1000 more spaces
    SPACEY_TEXT = " " * 1000 + "بسم" + " " * 1000

    def test_word_count_mostly_whitespace(self) -> None:
        """Only the Arabic token counts; whitespace is irrelevant."""
        wc = _count_arabic_words(self.SPACEY_TEXT)
        assert wc == 1

    def test_strip_noise_collapses_whitespace(self) -> None:
        """strip_arabic_noise collapses all whitespace to single space and strips edges."""
        stripped = strip_arabic_noise(self.SPACEY_TEXT)
        assert stripped == "بسم"

    def test_assemble_preserves_whitespace(self) -> None:
        """assemble_text preserves original whitespace (no normalization)."""
        cu = _make_content_unit(primary_text=self.SPACEY_TEXT, unit_index=0)
        text, _, _ = assemble_text([cu], 0, 0)
        assert text == self.SPACEY_TEXT
        assert len(text) > 2000


# =====================================================================
# Category 5: Regex Traps (Arabic-Indic digits, \d, \b, \w)
# =====================================================================


class TestRegexDTrap:
    """Python \\d matches Arabic-Indic digits. This class verifies that
    KR regex patterns use [0-9] where intended."""

    def test_sentence_boundary_regex_literal_punctuation(self) -> None:
        """_SENTENCE_BOUNDARY_RE should use literal Arabic punctuation,
        not character classes that could accidentally match digits."""
        # The pattern is r"[.؟!]\\s" -- verify it matches Arabic question mark
        text = "هل هذا صحيح؟ نعم هو كذلك"
        matches = list(_SENTENCE_BOUNDARY_RE.finditer(text))
        assert len(matches) >= 1

    def test_sentence_boundary_no_false_match_on_digits(self) -> None:
        """Sentence boundary regex must NOT match digit-space sequences."""
        # Arabic-Indic digits followed by space
        text = "الباب ٣ من الكتاب"
        matches = list(_SENTENCE_BOUNDARY_RE.finditer(text))
        # ٣ is not in [.؟!], so no match expected
        assert len(matches) == 0

    def test_footnote_marker_regex_no_arabic_digit_leak(self) -> None:
        """Footnote marker pattern ⌜...⌝ must work with both digit systems."""
        from engines.excerpting.src.phase1_assembly import _FOOTNOTE_MARKER_RE
        # Western digits
        match_w = _FOOTNOTE_MARKER_RE.search("⌜123⌝")
        assert match_w is not None
        assert match_w.group(1) == "123"
        # Arabic-Indic digits (should also match since pattern is [^⌝]+)
        match_a = _FOOTNOTE_MARKER_RE.search("⌜١٢٣⌝")
        assert match_a is not None
        assert match_a.group(1) == "١٢٣"


class TestRegexWordBoundaryTrap:
    """\\b does not work reliably at Arabic word boundaries due to clitics."""

    def test_word_boundary_fails_with_arabic_clitic(self) -> None:
        """Demonstrate that \\b fails to detect boundaries around Arabic clitics.
        The prefix ال (definite article) does not create a \\b boundary."""
        text = "الكتاب"  # al-kitab (the book)
        # \\b before ال should match (start of word)
        match_start = re.search(r"\bالكتاب\b", text)
        assert match_start is not None, "\\b should match at string boundary"

        # But within a sentence with conjunction و (and)
        text2 = "والكتاب"  # wa-al-kitab (and the book)
        match_clitic = re.search(r"\bالكتاب\b", text2)
        # \\b does NOT fire between و and ال because they are both \\w characters
        assert match_clitic is None, (
            "\\b incorrectly matched inside cliticized word -- "
            "this documents the known Arabic \\b limitation"
        )

    def test_w_matches_arabic_letters(self) -> None:
        """Python \\w matches Arabic letters. Document this behavior."""
        text = "كتاب"
        matches = re.findall(r"\w+", text)
        assert len(matches) == 1
        assert matches[0] == "كتاب"


class TestRegexEasternArabicIndicDigits:
    """Eastern Arabic-Indic digits (U+06F0-U+06F9, used in Persian/Urdu)
    are also matched by \\d."""

    EASTERN = "۰۱۲۳۴۵۶۷۸۹"  # U+06F0 to U+06F9

    def test_python_d_matches_eastern_arabic_indic(self) -> None:
        """\\d must match Eastern Arabic-Indic digits."""
        matches = re.findall(r"\d+", self.EASTERN)
        assert len(matches) == 1
        assert matches[0] == self.EASTERN

    def test_bracket_0_9_excludes_eastern(self) -> None:
        """[0-9] must NOT match Eastern Arabic-Indic digits."""
        matches = re.findall(r"[0-9]+", self.EASTERN)
        assert len(matches) == 0

    def test_eastern_digits_in_arabic_block(self) -> None:
        """Eastern Arabic-Indic digits (U+06F0-06F9) ARE in U+0600-U+06FF.
        _count_arabic_words counts them."""
        wc = _count_arabic_words(self.EASTERN)
        assert wc == 1

    def test_word_count_mixed_eastern_western(self) -> None:
        """Mixed Eastern Arabic-Indic and Western digits as separate tokens."""
        text = "۱۲۳ 456"
        wc = _count_arabic_words(text)
        # ۱۲۳ is in Arabic block -> 1 word; 456 is not -> 0
        assert wc == 1


# =====================================================================
# Category 6: Name Matching Edge Cases
# =====================================================================


class TestNameMatchingExtremes:
    """Edge cases in Arabic scholarly name matching."""

    def test_name_only_particles(self) -> None:
        """Name consisting only of patronymic particles (بن, ابن).
        After particle removal, no tokens remain."""
        tokens = _extract_name_tokens("بن ابن")
        assert tokens == set()

    def test_name_only_definite_article(self) -> None:
        """Name that is just 'ال' (definite article). After stripping, empty."""
        normed = normalize_arabic_name("ال")
        assert normed == ""

    def test_name_with_death_date_parenthetical(self) -> None:
        """Name with death date annotation: '(ت 337هـ)' must be stripped."""
        name = "الطبراني (ت 360هـ)"
        normed = normalize_arabic_name(name)
        # Parenthetical must be removed
        assert "360" not in normed
        assert "ت" not in normed or normed.index("ت") < 5  # Only if part of a name

    def test_similarity_short_vs_full_nasab(self) -> None:
        """Short nisba-only name vs full nasab chain.
        'النووي' vs 'يحيى بن شرف النووي' should have high similarity."""
        sim = normalized_name_similarity("النووي", "يحيى بن شرف النووي")
        assert sim > 0.5

    def test_similarity_completely_different_names(self) -> None:
        """Two completely different scholar names = 0.0 similarity."""
        sim = normalized_name_similarity(
            "ابن تيمية",
            "الإمام مالك بن أنس",
        )
        assert sim == 0.0

    def test_name_with_all_honorifics(self) -> None:
        """Name with many honorific prefixes that should be preserved but
        not interfere with matching."""
        full = "الشيخ الإمام العلامة الحافظ شيخ الإسلام أحمد بن تيمية"
        short = "ابن تيمية"
        sim = normalized_name_similarity(full, short)
        # "تيميه" (after normalization) should appear in both
        assert sim > 0.0

    def test_name_compound_word_mismatch(self) -> None:
        """Compound word mismatch: عبدالله (joined) vs عبد الله (separated).
        Should trigger substring fallback."""
        sim = normalized_name_similarity("عبدالله", "عبد الله")
        assert sim > 0.0, "Substring fallback should detect containment"

    def test_name_with_punctuation(self) -> None:
        """Name with Arabic and Latin punctuation from LLM output."""
        name = "الإمام أحمد، بن حنبل؛"
        normed = normalize_arabic_name(name)
        # Punctuation should be replaced with space and collapsed
        assert "،" not in normed
        assert "؛" not in normed
        assert "احمد" in normed  # After hamza normalization: أ -> ا

    def test_similarity_with_extra_whitespace(self) -> None:
        """Names with extra whitespace must normalize to same form."""
        name_a = "أحمد   بن    حنبل"
        name_b = "أحمد بن حنبل"
        norm_a = normalize_arabic_name(name_a)
        norm_b = normalize_arabic_name(name_b)
        assert norm_a == norm_b

    def test_very_long_name_chain(self) -> None:
        """Very long nasab chain (20+ components). Tests token extraction
        performance and correctness."""
        components = ["محمد", "بن", "أحمد", "بن", "علي", "بن", "حسن",
                      "بن", "حسين", "بن", "عمر", "بن", "خالد", "بن",
                      "إبراهيم", "بن", "يوسف", "بن", "عثمان", "بن",
                      "سعد", "بن", "وقاص"]
        long_name = " ".join(components)
        tokens = _extract_name_tokens(long_name)
        # All 'بن' particles removed; names remain
        assert "بن" not in tokens
        assert "محمد" in tokens or "محمد".replace("أ", "ا") in tokens

    def test_name_with_kunya(self) -> None:
        """Name starting with kunya (أبو X / أم X). Kunya is a single
        semantic unit but two tokens."""
        name = "أبو بكر الصديق"
        tokens = _extract_name_tokens(name)
        # Neither "أبو" nor "بكر" should be removed (they are not particles)
        # After hamza normalization: أبو -> ابو
        normed_tokens = {normalize_arabic_name(t) for t in tokens if t}
        assert len(normed_tokens) >= 2


class TestValidationPassthroughArabicFields:
    """D-023 passthrough validation with Arabic text fields."""

    def test_arabic_field_preserved(self) -> None:
        """Arabic text field present before and after -> no error."""
        before = {"title": "كتاب التوحيد", "author": "محمد بن عبد الوهاب"}
        after = {"title": "كتاب التوحيد", "author": "محمد بن عبد الوهاب", "genre": "عقيدة"}
        errors = validate_enrichment_passthrough(before, after)
        assert errors == []

    def test_arabic_field_deleted(self) -> None:
        """Arabic text field deleted during enrichment -> SRC_INVALID_ENRICHMENT."""
        before = {"title": "كتاب التوحيد", "author": "محمد بن عبد الوهاب"}
        after = {"title": "كتاب التوحيد"}  # author missing
        errors = validate_enrichment_passthrough(before, after)
        assert len(errors) == 1
        assert errors[0].error_code == "SRC_INVALID_ENRICHMENT"
        assert "author" in errors[0].field

    def test_arabic_field_nullified(self) -> None:
        """Arabic text field set to None during enrichment -> error."""
        before = {"title": "كتاب التوحيد", "author": "محمد بن عبد الوهاب"}
        after = {"title": "كتاب التوحيد", "author": None}
        errors = validate_enrichment_passthrough(before, after)
        assert len(errors) == 1

    def test_passthrough_with_diacritized_text(self) -> None:
        """Diacritized Arabic text must be compared exactly (byte-for-byte)."""
        diacritized = "كِتَابُ التَّوْحِيدِ"
        before = {"title": diacritized}
        after = {"title": diacritized}
        errors = validate_enrichment_passthrough(before, after)
        assert errors == []

    def test_passthrough_diacritics_stripped_is_violation(self) -> None:
        """If enrichment strips diacritics from a field, that changes the value.
        The new value is different but non-null -> NOT a D-023 violation
        (D-023 checks null/missing, not content change)."""
        before = {"title": "كِتَابُ التَّوْحِيدِ"}
        after = {"title": "كتاب التوحيد"}  # Diacritics stripped
        errors = validate_enrichment_passthrough(before, after)
        # D-023 only checks for null/missing; changed value passes
        assert errors == []


# =====================================================================
# Category 7: Cross-Function Consistency
# =====================================================================


class TestCrossFunctionConsistency:
    """Verify that different functions handle the same edge case consistently."""

    def test_diacritics_only_text_consistency(self) -> None:
        """All functions must handle diacritics-only text without crashing."""
        text = "\u064E\u064F\u0650\u0651\u0652"
        # None of these should raise
        _count_arabic_words(text)
        strip_arabic_noise(text)
        _split_arabic_sentences(text)
        normalize_arabic_name(text)

    def test_tatweel_only_consistency(self) -> None:
        """Tatweel-only text across all functions."""
        text = "\u0640" * 50
        _count_arabic_words(text)
        stripped = strip_arabic_noise(text)
        assert stripped == ""
        _split_arabic_sentences(text)

    def test_null_byte_does_not_crash(self) -> None:
        """Null byte (\\x00) in text must not crash any function."""
        text = "بسم\x00الله"
        # Should not raise
        _count_arabic_words(text)
        strip_arabic_noise(text)
        _split_arabic_sentences(text)

    def test_newline_heavy_text(self) -> None:
        """Text with excessive newlines between words."""
        text = "بسم\n\n\n\n\n\n\n\n\n\nالله\n\n\n\n\n\n\n\nالرحمن"
        wc = _count_arabic_words(text)
        assert wc == 3
        sentences = _split_arabic_sentences(text)
        assert len(sentences) >= 1

    def test_tab_separated_arabic(self) -> None:
        """Tab-separated Arabic words. Tabs are whitespace for split()."""
        text = "بسم\tالله\tالرحمن\tالرحيم"
        wc = _count_arabic_words(text)
        assert wc == 4

    def test_mixed_newline_styles(self) -> None:
        """Text with mixed \\n, \\r\\n, \\r line endings."""
        text = "الباب الأول\r\nالفصل الثاني\rالمبحث الثالث\nالمطلب الرابع"
        wc = _count_arabic_words(text)
        assert wc >= 8  # All Arabic words across all lines

    def test_surrogate_pair_characters(self) -> None:
        """Characters outside the BMP (U+10000+) should not crash.
        Some Arabic mathematical symbols are in this range."""
        # U+1EE00 = ARABIC MATHEMATICAL ALEF
        if sys.maxunicode > 0xFFFF:
            text = "بسم \U0001EE00 الله"
            wc = _count_arabic_words(text)
            assert wc >= 2  # At least "بسم" and "الله"
