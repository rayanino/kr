"""Arabic JSON Serialization Roundtrip Tests — probe-json-arabic-roundtrip.

Verifies that write_excerpts() and write_gate_queue() preserve Arabic text
byte-for-byte through the full write → disk → read cycle.

CORRUPTION VECTOR: Pydantic model_dump(mode='json') + json.dumps + json.loads
could alter Unicode normalization, escape ZWNJ, or change diacritics.

All assertions use: original.encode('utf-8') == roundtripped.encode('utf-8')
to catch byte-level corruption that string equality would miss.
"""

from __future__ import annotations

import json
from pathlib import Path

from engines.excerpting.contracts import (
    EvidenceRef,
    SelfContainmentLevel,
)
from engines.excerpting.src.writer import write_excerpts, write_gate_queue

from .conftest import _make_excerpt_record


# ═══════════════════════════════════════════════════════════════════
# Helper
# ═══════════════════════════════════════════════════════════════════


def _roundtrip_primary_text(text: str, tmp_path: Path) -> str:
    """Write ExcerptRecord with given primary_text, read back, return primary_text."""
    snippet = text[:80] if len(text) >= 1 else "بسم الله"
    exc = _make_excerpt_record(primary_text=text, text_snippet=snippet)
    path = write_excerpts([exc], tmp_path)
    with open(path, "r", encoding="utf-8") as f:
        data = json.loads(f.readline())
    return data["primary_text"]


def _bytes_match(original: str, roundtripped: str) -> bool:
    """Compare UTF-8 byte representation — catches normalization changes."""
    return original.encode("utf-8") == roundtripped.encode("utf-8")


def _make_gate_entry(**overrides: object) -> dict[str, object]:
    """Factory for SPEC-complete gate_queue.jsonl rows."""
    gate_code = str(overrides.get("gate_code", "EX-G-001"))
    context_override = overrides.pop("context", None)
    if gate_code == "EX-G-002":
        context: dict[str, object] = {
            "primary_text": "نص عربي كامل",
            "primary_text_snippet": "نص عربي",
            "self_containment_notes": "يحتاج إلى السياق السابق",
            "adjacent_teaching_units": [],
            "failed_criteria_context": "يحتاج إلى السياق السابق",
        }
        if isinstance(context_override, dict):
            context.update(context_override)
    else:
        context = {
            "primary_text": "نص عربي كامل",
            "primary_text_snippet": "نص عربي",
        }
        if isinstance(context_override, dict):
            context.update(context_override)

    entry: dict[str, object] = {
        "excerpt_id": "exc_gq_0_0_0",
        "gate_code": gate_code,
        "timestamp": "2026-03-24T00:00:00+00:00",
        "context": context,
        "status": "pending",
    }
    entry.update(overrides)
    return entry


# ═══════════════════════════════════════════════════════════════════
# 1. Full Tashkeel — all diacritic forms
# ═══════════════════════════════════════════════════════════════════


class TestFullTashkeelRoundtrip:
    """Verify all diacritic forms survive write → read byte-for-byte."""

    # Fathah (U+064E), Dammah (U+064F), Kasrah (U+0650)
    FATHAH = "\u064e"
    DAMMAH = "\u064f"
    KASRAH = "\u0650"
    # Sukun (U+0652), Shadda (U+0651)
    SUKUN = "\u0652"
    SHADDA = "\u0651"
    # Tanwin forms: fath (U+064B), damm (U+064C), kasr (U+064D)
    TANWIN_FATH = "\u064b"
    TANWIN_DAMM = "\u064c"
    TANWIN_KASR = "\u064d"

    def test_fathah_preserved(self, tmp_path: Path) -> None:
        """Fathah (U+064E) survives roundtrip byte-for-byte."""
        text = f"كَتَبَ الطَّالِبُ"  # Multiple fathah
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Fathah corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_dammah_preserved(self, tmp_path: Path) -> None:
        """Dammah (U+064F) survives roundtrip byte-for-byte."""
        text = "الرَّجُلُ يَكْتُبُ كِتَابًا"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Dammah corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_kasrah_preserved(self, tmp_path: Path) -> None:
        """Kasrah (U+0650) survives roundtrip byte-for-byte."""
        text = "بِسْمِ اللهِ الرَّحْمنِ الرَّحِيمِ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Kasrah corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_sukun_preserved(self, tmp_path: Path) -> None:
        """Sukun (U+0652) survives roundtrip byte-for-byte."""
        text = "أَنْعَمْتَ عَلَيْهِمْ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Sukun corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_shadda_preserved(self, tmp_path: Path) -> None:
        """Shadda (U+0651) survives roundtrip byte-for-byte."""
        text = "الشَّمْسُ تُضِيءُ الدُّنْيَا"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Shadda corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_tanwin_fath_preserved(self, tmp_path: Path) -> None:
        """Tanwin fath (U+064B) survives roundtrip byte-for-byte."""
        text = "كِتَابًا نَافِعًا مُفِيدًا"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Tanwin fath corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_tanwin_damm_preserved(self, tmp_path: Path) -> None:
        """Tanwin damm (U+064C) survives roundtrip byte-for-byte."""
        text = "عِلْمٌ نَافِعٌ وَعَمَلٌ صَالِحٌ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Tanwin damm corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_tanwin_kasr_preserved(self, tmp_path: Path) -> None:
        """Tanwin kasr (U+064D) survives roundtrip byte-for-byte."""
        text = "بِعِلْمٍ وَبَصِيرَةٍ وَيَقِينٍ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Tanwin kasr corrupted: {text.encode('utf-8')} != {rt.encode('utf-8')}"
        )

    def test_all_diacritics_combined(self, tmp_path: Path) -> None:
        """All diacritic forms in a single text survive roundtrip."""
        # A fully vowelled Quranic verse
        text = (
            "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ "
            "الرَّحْمَٰنِ الرَّحِيمِ "
            "مَالِكِ يَوْمِ الدِّينِ"
        )
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Combined diacritics corrupted.\n"
            f"original bytes: {text.encode('utf-8')[:50]}\n"
            f"roundtrip bytes: {rt.encode('utf-8')[:50]}"
        )

    def test_shadda_combined_with_dammah(self, tmp_path: Path) -> None:
        """Shadda + dammah stacked (U+0651 U+064F) survive roundtrip."""
        # رَبِّ has shadda+kasrah on ب
        text = "رَبِّ الْعَالَمِينَ الرَّحْمَنِ الرَّحِيمِ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Shadda+dammah combination corrupted"


# ═══════════════════════════════════════════════════════════════════
# 2. ZWNJ (U+200C)
# ═══════════════════════════════════════════════════════════════════


class TestZWNJRoundtrip:
    """U+200C Zero Width Non-Joiner must survive serialization."""

    ZWNJ = "\u200c"

    def test_zwnj_between_arabic_letters_preserved(self, tmp_path: Path) -> None:
        """ZWNJ between Arabic letters survives roundtrip byte-for-byte."""
        zwnj = self.ZWNJ
        # ZWNJ used to prevent ligature formation
        text = f"لا{zwnj}يعلم"  # prevent lam-alef ligature
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"ZWNJ corrupted — was: {list(text)} roundtripped: {list(rt)}"
        )
        assert zwnj in rt, "ZWNJ character dropped during serialization"

    def test_zwnj_not_escaped_as_unicode_escape(self, tmp_path: Path) -> None:
        """ZWNJ must not be \\u200c-escaped in JSONL output."""
        zwnj = self.ZWNJ
        text = f"كلمة{zwnj}أخرى"
        exc = _make_excerpt_record(primary_text=text, text_snippet=text[:80])
        path = write_excerpts([exc], tmp_path)
        raw_content = path.read_text(encoding="utf-8")
        # If ZWNJ is escaped, it appears as \\u200c in the file
        assert "\\u200c" not in raw_content, (
            "ZWNJ was escaped as \\u200c — ensure_ascii=False should prevent this"
        )

    def test_zwnj_roundtrip_multiple_positions(self, tmp_path: Path) -> None:
        """Multiple ZWNJ at different positions all survive."""
        zwnj = self.ZWNJ
        text = f"نص{zwnj}عربي{zwnj}فيه{zwnj}فواصل"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Multiple ZWNJ positions corrupted"
        assert rt.count(zwnj) == 3, (
            f"Expected 3 ZWNJ, got {rt.count(zwnj)}"
        )


# ═══════════════════════════════════════════════════════════════════
# 3. Tatweel (U+0640)
# ═══════════════════════════════════════════════════════════════════


class TestTatweelRoundtrip:
    """U+0640 Arabic Tatweel (kashida) must survive serialization."""

    TATWEEL = "\u0640"

    def test_tatweel_inside_word_preserved(self, tmp_path: Path) -> None:
        """Tatweel inside a word survives roundtrip byte-for-byte."""
        text = f"الله\u0640\u0640\u0640\u0640ُ أكبر"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Tatweel corrupted — was: {list(text)} roundtripped: {list(rt)}"
        )

    def test_tatweel_not_stripped(self, tmp_path: Path) -> None:
        """Tatweel must NOT be stripped by the writer."""
        tatweel = self.TATWEEL
        text = f"كتـاب النـور"  # tatweel in كتاب and النور
        rt = _roundtrip_primary_text(text, tmp_path)
        assert tatweel in rt, "Tatweel was stripped during roundtrip"

    def test_tatweel_count_preserved(self, tmp_path: Path) -> None:
        """Exact count of tatweel characters preserved."""
        tatweel = self.TATWEEL
        text = "علـم الفقـه والأصـول"  # 3 tatweel
        original_count = text.count(tatweel)
        rt = _roundtrip_primary_text(text, tmp_path)
        assert rt.count(tatweel) == original_count, (
            f"Tatweel count changed: {original_count} → {rt.count(tatweel)}"
        )


# ═══════════════════════════════════════════════════════════════════
# 4. Superscript Alef (U+0670)
# ═══════════════════════════════════════════════════════════════════


class TestSuperscriptAlefRoundtrip:
    """U+0670 Arabic Letter Superscript Alef (dagger alef) must survive."""

    SUPERSCRIPT_ALEF = "\u0670"

    def test_superscript_alef_preserved(self, tmp_path: Path) -> None:
        """Superscript alef (U+0670) survives roundtrip byte-for-byte."""
        sa = self.SUPERSCRIPT_ALEF
        # Dagger alef appears in Quranic text: الرَّحْمَٰن
        text = f"الرَّحْمَ{sa}نِ الرَّحِيمِ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Superscript alef corrupted.\n"
            f"original: {text.encode('utf-8')}\n"
            f"roundtrip: {rt.encode('utf-8')}"
        )

    def test_superscript_alef_not_escaped(self, tmp_path: Path) -> None:
        """Superscript alef must not be \\u0670-escaped in JSONL output."""
        sa = self.SUPERSCRIPT_ALEF
        text = f"الرَّحْمَ{sa}نِ"
        exc = _make_excerpt_record(primary_text=text, text_snippet=text[:80])
        path = write_excerpts([exc], tmp_path)
        raw_content = path.read_text(encoding="utf-8")
        assert "\\u0670" not in raw_content, (
            "Superscript alef escaped as \\u0670 — ensure_ascii=False should prevent this"
        )

    def test_superscript_alef_distinct_from_alef(self, tmp_path: Path) -> None:
        """Superscript alef (U+0670) is NOT normalized to regular alef (U+0627)."""
        sa = self.SUPERSCRIPT_ALEF
        text = f"مَ{sa}ء"  # superscript alef on meem
        rt = _roundtrip_primary_text(text, tmp_path)
        # Must not normalize U+0670 → U+0627
        assert sa in rt, f"Superscript alef normalized to regular alef"
        assert rt.index(sa) == text.index(sa), "Superscript alef position changed"


# ═══════════════════════════════════════════════════════════════════
# 5. Arabic Presentation Forms (U+FB50–U+FDFF)
# ═══════════════════════════════════════════════════════════════════


class TestPresentationFormsRoundtrip:
    """Presentation form characters must survive without normalization."""

    def test_arabic_ligature_bismillah_preserved(self, tmp_path: Path) -> None:
        """U+FDFD (Bismillah ligature) survives roundtrip byte-for-byte."""
        bismillah_ligature = "\ufdfd"
        text = f"{bismillah_ligature} هذا النص التالي"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Bismillah ligature corrupted.\n"
            f"original: {text.encode('utf-8')[:6]}\n"
            f"roundtrip: {rt.encode('utf-8')[:6]}"
        )
        assert bismillah_ligature in rt, "Bismillah ligature dropped"

    def test_arabic_letter_alef_wasla_preserved(self, tmp_path: Path) -> None:
        """U+FB50 (Alef Wasla — presentation form A) survives roundtrip."""
        alef_wasla = "\ufb50"
        text = f"{alef_wasla}ستأذنوا في البيوت"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Alef Wasla presentation form corrupted.\n"
            f"original bytes: {text.encode('utf-8')[:6]}\n"
            f"roundtrip bytes: {rt.encode('utf-8')[:6]}"
        )

    def test_arabic_ligature_sallallahu_preserved(self, tmp_path: Path) -> None:
        """U+FDFA (Sallallahu alayhi wa sallam ligature) survives roundtrip."""
        saws_ligature = "\ufdfa"
        text = f"قال النبي {saws_ligature} في هذا الحديث"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Saws ligature corrupted.\n"
            f"original: {text.encode('utf-8')}\n"
            f"roundtrip: {rt.encode('utf-8')}"
        )
        assert saws_ligature in rt, "Saws ligature (U+FDFA) dropped or normalized"

    def test_presentation_forms_not_normalized_to_base(self, tmp_path: Path) -> None:
        """Presentation form chars must NOT be NFC/NFKC-normalized to base chars."""
        import unicodedata
        # U+FB50 should NOT normalize to U+0627 under NFKC
        alef_wasla = "\ufb50"
        text = f"في {alef_wasla}ستأذنوا"
        rt = _roundtrip_primary_text(text, tmp_path)
        # If NFKC normalization occurred, alef_wasla → regular alef
        nfkc_normalized = unicodedata.normalize("NFKC", text)
        # The roundtrip should NOT equal the NFKC form if they differ
        if nfkc_normalized != text:
            assert rt == text, (
                "Presentation forms were NFKC-normalized during serialization. "
                f"Original had {alef_wasla!r}, roundtrip lost it."
            )

    def test_presentation_forms_not_escaped(self, tmp_path: Path) -> None:
        """Presentation form chars (U+FB50+) must not be \\uXXXX-escaped."""
        alef_wasla = "\ufb50"
        text = f"{alef_wasla}لله"
        exc = _make_excerpt_record(primary_text=text, text_snippet=text[:80])
        path = write_excerpts([exc], tmp_path)
        raw_content = path.read_text(encoding="utf-8")
        assert "\\ufb50" not in raw_content, (
            "Alef Wasla (U+FB50) escaped as \\ufb50 — ensure_ascii=False should prevent this"
        )


# ═══════════════════════════════════════════════════════════════════
# 6. Byte-level comparison for text_snippet, context_hint, evidence_refs
# ═══════════════════════════════════════════════════════════════════


class TestAllArabicFieldsRoundtrip:
    """Byte-level verification for all Arabic-bearing ExcerptRecord fields."""

    COMPLEX_ARABIC = (
        "الْحَمْدُ لِلَّهِ\u0670 رَبِّ الْعَالَمِينَ"  # superscript alef
        "\u200c"  # ZWNJ
        " الرَّحْمَ\u0670نِ الرَّحِيمِ"
    )

    def test_text_snippet_byte_level(self, tmp_path: Path) -> None:
        """text_snippet with complex Arabic survives byte-for-byte."""
        snippet = self.COMPLEX_ARABIC[:80]
        exc = _make_excerpt_record(
            primary_text=self.COMPLEX_ARABIC,
            text_snippet=snippet,
        )
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_snippet = data["text_snippet"]
        assert snippet.encode("utf-8") == rt_snippet.encode("utf-8"), (
            f"text_snippet corrupted at byte level.\n"
            f"original: {snippet.encode('utf-8')}\n"
            f"roundtrip: {rt_snippet.encode('utf-8')}"
        )

    def test_context_hint_byte_level(self, tmp_path: Path) -> None:
        """context_hint with complex Arabic survives byte-for-byte."""
        hint = "يقصد المؤلف هنا الكلامَ\u0670 عن الفقه الحنفي"
        exc = _make_excerpt_record(
            self_containment=SelfContainmentLevel.PARTIAL,
            self_containment_notes="نص يحتاج سياقاً",
            context_hint=hint,
        )
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_hint = data["context_hint"]
        assert hint.encode("utf-8") == rt_hint.encode("utf-8"), (
            f"context_hint corrupted at byte level.\n"
            f"original: {hint.encode('utf-8')}\n"
            f"roundtrip: {rt_hint.encode('utf-8')}"
        )

    def test_evidence_refs_text_snippet_byte_level(self, tmp_path: Path) -> None:
        """EvidenceRef.text_snippet with tashkeel survives byte-for-byte."""
        snippet = "قُلْ هُوَ اللَّهُ أَحَدٌ"
        evidence = EvidenceRef(
            type="quran",
            surah=112,
            ayah_start=1,
            ayah_end=1,
            text_snippet=snippet,
        )
        exc = _make_excerpt_record(evidence_refs=[evidence])
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_snippet = data["evidence_refs"][0]["text_snippet"]
        assert snippet.encode("utf-8") == rt_snippet.encode("utf-8"), (
            f"EvidenceRef.text_snippet corrupted at byte level.\n"
            f"original: {snippet.encode('utf-8')}\n"
            f"roundtrip: {rt_snippet.encode('utf-8')}"
        )

    def test_description_arabic_byte_level(self, tmp_path: Path) -> None:
        """description_arabic with full tashkeel survives byte-for-byte."""
        desc = "تَعْرِيفُ الإِيمَانِ وَشُرُوطُهُ عِنْدَ أَهْلِ السُّنَّةِ"
        exc = _make_excerpt_record(description_arabic=desc)
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_desc = data["description_arabic"]
        assert desc.encode("utf-8") == rt_desc.encode("utf-8"), (
            f"description_arabic corrupted at byte level."
        )

    def test_div_path_arabic_byte_level(self, tmp_path: Path) -> None:
        """div_path with Arabic headings survive byte-for-byte."""
        div_path = [
            "كِتَابُ الصَّلَاةِ",
            "بَابُ شُرُوطِهَا",
            "فَصْلٌ فِي النِّيَّةِ",
        ]
        exc = _make_excerpt_record(div_path=div_path)
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_path = data["div_path"]
        for i, (original, rt) in enumerate(zip(div_path, rt_path)):
            assert original.encode("utf-8") == rt.encode("utf-8"), (
                f"div_path[{i}] corrupted at byte level.\n"
                f"original: {original.encode('utf-8')}\n"
                f"roundtrip: {rt.encode('utf-8')}"
            )


# ═══════════════════════════════════════════════════════════════════
# 7. Gate queue Arabic field byte-level roundtrip
# ═══════════════════════════════════════════════════════════════════


class TestGateQueueArabicRoundtrip:
    """write_gate_queue preserves Arabic text byte-for-byte."""

    def test_gate_queue_tashkeel_preserved(self, tmp_path: Path) -> None:
        """Gate queue Arabic context with tashkeel survives byte-for-byte."""
        arabic_text = "الرَّحْمَنِ الرَّحِيمِ مَالِكِ يَوْمِ الدِّينِ"
        entries = [
            _make_gate_entry(context={"primary_text_snippet": arabic_text})
        ]
        path = write_gate_queue(entries, tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_text = data["context"]["primary_text_snippet"]
        assert arabic_text.encode("utf-8") == rt_text.encode("utf-8"), (
            f"Gate queue tashkeel corrupted.\n"
            f"original: {arabic_text.encode('utf-8')}\n"
            f"roundtrip: {rt_text.encode('utf-8')}"
        )

    def test_gate_queue_zwnj_preserved(self, tmp_path: Path) -> None:
        """Gate queue Arabic context with ZWNJ survives byte-for-byte."""
        zwnj = "\u200c"
        arabic_text = f"نص{zwnj}عربي فيه حرف خاص"
        entries = [
            _make_gate_entry(
                gate_code="EX-G-002",
                context={"text": arabic_text},
            )
        ]
        path = write_gate_queue(entries, tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_text = data["context"]["text"]
        assert arabic_text.encode("utf-8") == rt_text.encode("utf-8"), (
            f"Gate queue ZWNJ corrupted."
        )
        assert zwnj in rt_text, "ZWNJ dropped from gate queue context"

    def test_gate_queue_presentation_forms_preserved(self, tmp_path: Path) -> None:
        """Gate queue Arabic context with presentation forms survives byte-for-byte."""
        saws = "\ufdfa"  # ﷺ
        entries = [
            _make_gate_entry(
                gate_code="EX-G-003",
                context={
                    "scholar": f"قال النبي {saws} في هذا الحديث",
                    "school": "حَنْبَلِيٌّ",
                },
            )
        ]
        path = write_gate_queue(entries, tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_scholar = data["context"]["scholar"]
        original_scholar = entries[0]["context"]["scholar"]  # type: ignore[index]
        assert original_scholar.encode("utf-8") == rt_scholar.encode("utf-8"), (  # type: ignore[union-attr]
            f"Gate queue presentation form corrupted."
        )

    def test_gate_queue_superscript_alef_preserved(self, tmp_path: Path) -> None:
        """Gate queue Arabic context with superscript alef survives byte-for-byte."""
        sa = "\u0670"
        arabic_text = f"الرَّحْمَ{sa}نِ الرَّحِيمِ"
        entries = [
            _make_gate_entry(context={"quran_snippet": arabic_text})
        ]
        path = write_gate_queue(entries, tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_text = data["context"]["quran_snippet"]
        assert arabic_text.encode("utf-8") == rt_text.encode("utf-8"), (
            f"Gate queue superscript alef corrupted."
        )

    def test_gate_queue_tatweel_preserved(self, tmp_path: Path) -> None:
        """Gate queue Arabic context with tatweel survives byte-for-byte."""
        tatweel = "\u0640"
        arabic_text = f"كتـاب النـور المبـين"
        entries = [
            _make_gate_entry(context={"title": arabic_text})
        ]
        path = write_gate_queue(entries, tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())
        rt_text = data["context"]["title"]
        assert arabic_text.encode("utf-8") == rt_text.encode("utf-8"), (
            f"Gate queue tatweel corrupted."
        )
        assert rt_text.count(tatweel) == arabic_text.count(tatweel), (
            "Tatweel count changed in gate queue"
        )


# ═══════════════════════════════════════════════════════════════════
# 8. Multi-field combined: write one record with all problematic chars
# ═══════════════════════════════════════════════════════════════════


class TestCombinedArabicCorruptionProbe:
    """One record exercises all corruption vectors simultaneously."""

    def test_full_corpus_of_special_chars_roundtrip(self, tmp_path: Path) -> None:
        """A single ExcerptRecord with ALL special Arabic chars roundtrips intact."""
        # Build text containing every corruption vector
        text_parts = [
            # Full tashkeel
            "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ",
            # Tanwin all forms
            "كِتَابًا نَافِعًا وَعِلْمٌ صَالِحٌ بِعِلْمٍ",
            # ZWNJ
            "لا\u200cيعلم",
            # Tatweel
            "كتـاب",
            # Superscript alef
            "الرَّحْمَ\u0670نِ",
            # Saws ligature (presentation form)
            "النبي \ufdfa",
        ]
        primary_text = " ".join(text_parts)
        snippet = primary_text[:80]

        exc = _make_excerpt_record(
            primary_text=primary_text,
            text_snippet=snippet,
            description_arabic="وَصْفٌ جَامِعٌ لِأَنْوَاعِ الحُرُوفِ العَرَبِيَّةِ",
        )
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        rt_primary = data["primary_text"]
        rt_snippet = data["text_snippet"]

        assert primary_text.encode("utf-8") == rt_primary.encode("utf-8"), (
            "Combined Arabic text corrupted in primary_text"
        )
        assert snippet.encode("utf-8") == rt_snippet.encode("utf-8"), (
            "Combined Arabic text corrupted in text_snippet"
        )

        # Verify each special character is still present
        assert "\u200c" in rt_primary, "ZWNJ missing after roundtrip"
        assert "\u0640" in rt_primary, "Tatweel missing after roundtrip"
        assert "\u0670" in rt_primary, "Superscript alef missing after roundtrip"
        assert "\ufdfa" in rt_primary, "Saws ligature missing after roundtrip"


# ═══════════════════════════════════════════════════════════════════
# 9. Paragraph Breaks (\n\n) in primary_text
# ═══════════════════════════════════════════════════════════════════


class TestParagraphBreaksRoundtrip:
    """Paragraph breaks and newlines in primary_text must survive
    the write → JSONL → read cycle byte-for-byte.

    JSONL uses \\n as record separator — json.dumps MUST escape \\n
    inside string values to \\\\n. If it doesn't, the JSONL structure
    breaks and read-back produces truncated or corrupt records.
    """

    def test_double_newline_preserved(self, tmp_path: Path) -> None:
        """Double newline (\\n\\n) paragraph break survives roundtrip."""
        text = "بسم الله الرحمن الرحيم\n\nالحمد لله رب العالمين"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Paragraph break corrupted.\n"
            f"original: {text.encode('utf-8')!r}\n"
            f"roundtrip: {rt.encode('utf-8')!r}"
        )
        assert "\n\n" in rt, "Double newline collapsed or stripped"

    def test_single_newline_preserved(self, tmp_path: Path) -> None:
        """Single newline (\\n) survives roundtrip."""
        text = "السطر الأول\nالسطر الثاني"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Single newline corrupted"
        assert "\n" in rt, "Single newline stripped"

    def test_triple_newline_preserved(self, tmp_path: Path) -> None:
        """Triple newline (\\n\\n\\n) — section gap — survives roundtrip."""
        text = "نهاية الفصل\n\n\nبداية الفصل التالي"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Triple newline corrupted"
        assert "\n\n\n" in rt, "Triple newline collapsed"

    def test_multiple_paragraphs(self, tmp_path: Path) -> None:
        """Multi-paragraph scholarly text (3+ paragraphs) survives roundtrip."""
        text = (
            "قال الإمام النووي رحمه الله\n\n"
            "اعلم أن الأمر بالمعروف والنهي عن المنكر "
            "قد يكون فرض عين وقد يكون فرض كفاية\n\n"
            "فأما إذا كان في موضع لا يعلم به إلا هو "
            "تعين عليه"
        )
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Multi-paragraph text corrupted"
        assert rt.count("\n\n") == 2, (
            f"Expected 2 paragraph breaks, got {rt.count(chr(10) + chr(10))}"
        )

    def test_trailing_newline_preserved(self, tmp_path: Path) -> None:
        """Trailing newline at end of text survives roundtrip."""
        text = "نص ينتهي بسطر جديد\n"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Trailing newline corrupted"
        assert rt.endswith("\n"), "Trailing newline stripped"

    def test_leading_newline_preserved(self, tmp_path: Path) -> None:
        """Leading newline at start of text survives roundtrip."""
        text = "\nنص يبدأ بسطر جديد"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Leading newline corrupted"
        assert rt.startswith("\n"), "Leading newline stripped"

    def test_newlines_in_jsonl_structure(self, tmp_path: Path) -> None:
        """Newlines inside primary_text do NOT break JSONL line structure.

        If json.dumps fails to escape \\n inside the string,
        the JSONL file would have extra lines and read-back fails.
        """
        text = "أول\n\nثاني\n\nثالث"
        exc = _make_excerpt_record(primary_text=text, text_snippet=text[:80])
        path = write_excerpts([exc], tmp_path)
        # JSONL: exactly 1 line per record + optional trailing newline
        raw = path.read_text(encoding="utf-8")
        lines = [l for l in raw.split("\n") if l.strip()]
        assert len(lines) == 1, (
            f"JSONL structure broken: expected 1 data line, got {len(lines)}. "
            "json.dumps likely failed to escape \\n inside primary_text."
        )
        # Verify content survives
        data = json.loads(lines[0])
        assert _bytes_match(text, data["primary_text"]), (
            "primary_text corrupted after JSONL structure verification"
        )

    def test_carriage_return_preserved(self, tmp_path: Path) -> None:
        """Carriage return (\\r) and CRLF (\\r\\n) survive roundtrip.

        Some OCR sources produce Windows-style line endings.
        They must not be silently converted to \\n.
        """
        text = "سطر أول\r\nسطر ثاني\rسطر ثالث"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"CR/CRLF corrupted.\n"
            f"original: {text.encode('utf-8')!r}\n"
            f"roundtrip: {rt.encode('utf-8')!r}"
        )

    def test_paragraph_breaks_with_tashkeel(self, tmp_path: Path) -> None:
        """Paragraph breaks combined with full tashkeel survive roundtrip."""
        text = (
            "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ\n\n"
            "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ\n\n"
            "الرَّحْمَنِ الرَّحِيمِ"
        )
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            "Paragraph breaks + tashkeel corrupted"
        )

    def test_paragraph_breaks_with_zwnj(self, tmp_path: Path) -> None:
        """Paragraph breaks combined with ZWNJ survive roundtrip."""
        zwnj = "\u200c"
        text = f"نص{zwnj}عربي\n\nفقرة{zwnj}ثانية"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Paragraph breaks + ZWNJ corrupted"
        assert rt.count(zwnj) == 2, "ZWNJ count changed with paragraph breaks"

    def test_paragraph_breaks_with_superscript_alef(self, tmp_path: Path) -> None:
        """Paragraph breaks combined with superscript alef survive roundtrip."""
        sa = "\u0670"
        text = f"الرَّحْمَ{sa}نِ\n\nمَالِكِ يَوْمِ الدِّينِ"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            "Paragraph breaks + superscript alef corrupted"
        )

    def test_paragraph_breaks_with_tatweel(self, tmp_path: Path) -> None:
        """Paragraph breaks combined with tatweel survive roundtrip."""
        text = "كتـاب الفقـه\n\nبـاب الطهـارة"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), "Paragraph breaks + tatweel corrupted"


# ═══════════════════════════════════════════════════════════════════
# 10. NFC Normalization Guard — decomposed Arabic forms
# ═══════════════════════════════════════════════════════════════════


class TestNFCNormalizationGuard:
    """Verify that serialization does NOT apply Unicode NFC normalization.

    NFC would silently compose decomposed Arabic forms:
    - U+0627 + U+0654 (alef + hamza above) → U+0623 (أ)
    - U+0627 + U+0655 (alef + hamza below) → U+0625 (إ)
    - U+0627 + U+0653 (alef + maddah) → U+0622 (آ)

    If sources contain decomposed forms (common in OCR), NFC changes
    the byte representation, corrupting scholarly text.
    """

    def test_decomposed_hamza_above_preserved(self, tmp_path: Path) -> None:
        """Alef + Hamza Above (U+0627 U+0654) NOT composed to U+0623."""
        import unicodedata
        # Decomposed form: alef + combining hamza above
        decomposed = "\u0627\u0654"
        text = f"ب{decomposed}مر الله"
        # Verify this IS different from NFC
        nfc = unicodedata.normalize("NFC", text)
        assert text != nfc, "Test setup: text already in NFC form"
        # Roundtrip must preserve decomposed form
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Decomposed hamza above was NFC-normalized.\n"
            f"original bytes: {text.encode('utf-8')!r}\n"
            f"roundtrip bytes: {rt.encode('utf-8')!r}\n"
            f"NFC would be: {nfc.encode('utf-8')!r}"
        )

    def test_decomposed_hamza_below_preserved(self, tmp_path: Path) -> None:
        """Alef + Hamza Below (U+0627 U+0655) NOT composed to U+0625."""
        import unicodedata
        decomposed = "\u0627\u0655"
        text = f"ف{decomposed}ن هذا"
        nfc = unicodedata.normalize("NFC", text)
        assert text != nfc, "Test setup: text already in NFC form"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Decomposed hamza below was NFC-normalized.\n"
            f"original: {text.encode('utf-8')!r}\n"
            f"roundtrip: {rt.encode('utf-8')!r}"
        )

    def test_decomposed_alef_maddah_preserved(self, tmp_path: Path) -> None:
        """Alef + Maddah (U+0627 U+0653) NOT composed to U+0622 (آ)."""
        import unicodedata
        decomposed = "\u0627\u0653"
        text = f"{decomposed}ية من القرآن"
        nfc = unicodedata.normalize("NFC", text)
        assert text != nfc, "Test setup: text already in NFC form"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            f"Decomposed alef maddah was NFC-normalized.\n"
            f"original: {text.encode('utf-8')!r}\n"
            f"roundtrip: {rt.encode('utf-8')!r}"
        )

    def test_mixed_composed_and_decomposed(self, tmp_path: Path) -> None:
        """Text with BOTH composed and decomposed forms preserves each."""
        import unicodedata
        # Composed أ (U+0623) alongside decomposed (U+0627+U+0654)
        composed = "\u0623"
        decomposed = "\u0627\u0654"
        text = f"{composed}مر الله ب{decomposed}مره"
        nfc = unicodedata.normalize("NFC", text)
        # They should differ because of the decomposed form
        assert text != nfc, "Test setup: text already in NFC"
        rt = _roundtrip_primary_text(text, tmp_path)
        assert _bytes_match(text, rt), (
            "Mixed composed/decomposed hamza corrupted by normalization"
        )
