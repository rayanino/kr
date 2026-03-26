---
name: quranic-text-handling
description: Guidelines for detecting, preserving, and cross-referencing Quranic text within Islamic scholarly works. Use when processing any text that may contain Quran citations, when building division trees near Quranic content, when excerpting passages that quote the Quran, or when classifying whether a text constitutes tafsir.
---

# Quranic Text Handling for KR

Quranic text embedded in scholarly works has the highest preservation requirements of any content type in KR. The Quran is the single text that every Muslim scholar quotes, every science references, and every reader expects to be letter-perfect. A single diacritic error in a Quranic quotation is not a typo — it is a corruption of divine text. The pipeline must detect Quranic content with high precision and preserve it with zero modification.

**Usage:** Reference this skill when implementing any code path that touches text which may contain Quran citations — normalization, passaging, excerpting, taxonomy, and synthesis. Every engine in the pipeline must be Quran-aware.

---

## 1. Detection of Quran in Scholarly Text

Quranic text appears in scholarly works through several mechanisms, each with different reliability as a detection signal.

### 1.1 Bracket Markers (Highest Reliability)

The ornate parentheses ﴿ (U+FD3F) and ﴾ (U+FD3E) are the standard delimiters for Quranic text in modern digital editions. Any text enclosed in these brackets is almost certainly a Quranic quotation.

```
﴿وَأَقِيمُوا الصَّلَاةَ وَآتُوا الزَّكَاةَ﴾
```

**Detection pattern:**
```python
import re
# Match text between Quranic brackets
QURAN_BRACKET_PATTERN = re.compile(r'\uFD3F([^\uFD3E]+)\uFD3E')
```

**Caveats:**
- Some older Shamela editions use regular parentheses or curly braces instead. Do not assume non-bracketed text is non-Quranic.
- Some editions place the brackets around the entire verse group including the reference, others only around the Arabic text.

### 1.2 Citation Formulas (High Reliability)

Scholars introduce Quranic quotations with formulaic phrases. The text following these formulas is Quranic until the next structural break or commentary resumes.

| Formula | Arabic | Context |
|---------|--------|---------|
| God said (exalted) | قال تعالى | Most common introduction |
| His saying (exalted) | قوله تعالى | Referring to a previously mentioned verse |
| Due to His saying (exalted) | لقوله تعالى | Citing verse as evidence (dalil) |
| God Almighty said | قال الله تعالى | More formal variant |
| The Mighty and Majestic said | قال عز وجل | Alternative divine epithet |
| As in His saying | كما في قوله تعالى | Cross-reference to another verse |
| And His saying | وقوله تعالى | Adding another verse citation |
| The Most High said | قال سبحانه وتعالى | Extended reverence formula |

**Detection pattern:**
```python
QURAN_CITATION_FORMULAS = [
    r'قال\s+تعالى',
    r'قوله\s+تعالى',
    r'لقوله\s+تعالى',
    r'قال\s+الله\s+تعالى',
    r'قال\s+عز\s+وجل',
    r'قال\s+سبحانه\s+وتعالى',
    r'كما\s+في\s+قوله\s+تعالى',
    r'وقوله\s+تعالى',
]
```

**Caveats:**
- The formula `قال تعالى` can rarely introduce hadith qudsi if immediately preceded by an isnad chain. Check for isnad absence before classifying as Quran.
- Some scholars omit `تعالى` and write simply `قال الله` — less reliable but still a signal.

### 1.3 Surah-Ayah References (High Reliability for Identification, Not Detection)

Explicit surah-ayah citations confirm that a nearby text is Quranic and provide the exact location for cross-referencing.

**Common formats:**
```
[البقرة: ٢٣٤]                    # Square bracket notation
(سورة البقرة، الآية ٢٣٤)          # Parenthetical with surah prefix
{البقرة: 234}                     # Curly braces with ASCII digits
سورة البقرة آية ٢٣٤               # Inline text reference
البقرة ٢/٢٣٤                     # Surah number / ayah number
```

**Detection pattern:**
```python
# Surah name followed by ayah number — use [0-9] not \d for ASCII digits
SURAH_AYAH_REF = re.compile(
    r'[\[\(﴿{]\s*'
    r'(?:سورة\s+)?'
    r'([\u0600-\u06FF\s]+?)'   # Surah name in Arabic
    r'[\s:،,/]\s*'
    r'([0-9\u0660-\u0669]+)'   # Ayah number (ASCII or Arabic-Indic)
    r'\s*[\]\)﴾}]'
)
```

**Important:** References may use Arabic-Indic numerals (٢٣٤) or ASCII numerals (234) depending on the edition. Handle both.

### 1.4 Ayah End Markers (Medium Reliability)

The ayah end marker ۝ (U+06DD) appears in some digital Quran editions and may propagate into scholarly quotations that copy from digital mushaf sources.

```
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ ۝ الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ ۝
```

**Caveats:**
- Many scholarly editions do NOT include ayah markers in their Quran quotations — absence of ۝ does not mean the text is non-Quranic.
- The symbol ۞ (U+06DE) is a rubic hizb mark (section marker), not an ayah separator. Both are valid Quranic structural markers and must be preserved.

### 1.5 Basmalah Detection

The phrase بسم الله الرحمن الرحيم appears in two very different contexts:

**As Quran (Surah al-Fatihah, ayah 1):**
- Appears within ﴿ ﴾ brackets as part of a Quranic quotation
- Appears after a citation formula (قال تعالى)
- Appears at the beginning of a surah in a tafsir text being explained verse by verse

**As structural prose (author's opening):**
- Appears at the very beginning of a book before the hamdala (الحمد لله...)
- Appears at the start of a new volume or major section
- NOT preceded by a citation formula
- Often followed immediately by الحمد لله رب العالمين and then the author's muqaddimah

**Disambiguation rule:** Basmalah at position 0 of a book/volume (before the hamdala) is structural prose, part of the muqaddimah. Basmalah inside text after a citation formula or inside Quranic brackets is a Quran citation. When ambiguous, default to structural prose unless positive Quranic signals are present.

### 1.6 Hadith Qudsi — The Critical False Positive

Hadith qudsi (divine hadith) reports God's speech but is NOT Quran. It is transmitted through hadith channels with an isnad, not through tawatur (mass-transmission) like the Quran.

**Key distinction:**
- **Quran:** قال تعالى ﴿وَأَقِيمُوا الصَّلَاةَ﴾ — no isnad, divine brackets
- **Hadith qudsi:** عن أبي هريرة قال: قال رسول الله صلى الله عليه وسلم: قال الله تعالى: أنا عند ظن عبدي بي — preceded by isnad, narrator chain to the Prophet, then God's speech

**Detection rule:** If the phrase "قال الله" or "يقول الله" is reached through an isnad chain (حدثنا...عن...قال رسول الله...قال الله), the text is hadith qudsi, NOT Quran. Apply `hadith_qudsi: true` tag, NOT `quranic_text: true`.

---

## 2. Preservation Rules

### 2.1 Zero Modification Principle

Quranic text tagged with `quranic_text: true` MUST NOT be modified at any pipeline stage:

- **No normalization:** Do not apply any Unicode normalization (NFC/NFD/NFKC/NFKD) to Quranic text. Verify byte-for-byte preservation.
- **No diacritic removal:** Diacritics in Quran are part of the text, not decoration. Never strip them for indexing or matching.
- **No whitespace changes:** Do not trim, collapse, or modify whitespace within Quranic text.
- **No character substitution:** Do not normalize alef variants (أ/إ/آ/ا), hamza placement, or taa marbuta in Quranic text.

### 2.2 Diacritics as Authenticity Signal

Fully diacritized Arabic text in a Quranic context indicates an exact citation from the mushaf. Partially diacritized or undiacritized text that matches Quran content indicates a quotation from memory (بالمعنى) or a paraphrase.

| Diacritization Level | Interpretation | KR Tag |
|---------------------|----------------|--------|
| Full diacritics matching mushaf | Exact Quran citation | `quranic_text: true, citation_type: exact` |
| Partial diacritics, text matches | Likely exact citation, edition stripped diacritics | `quranic_text: true, citation_type: probable_exact` |
| No diacritics, text matches | Quotation from memory or paraphrase | `quranic_text: true, citation_type: paraphrase` |
| Text diverges from all standard readings | Not Quran, or severely corrupted OCR | Flag for human review |

### 2.3 Variant Readings (Qira'at)

The Quran has multiple valid readings (qira'at) transmitted through different chains. The seven canonical readings (القراءات السبع) and three additional accepted readings (القراءات العشر) all produce valid Quranic text that may differ in wording.

**Examples of variant readings:**
- Hafs reading: مَالِكِ يَوْمِ الدِّينِ (Malik — owner)
- Warsh reading: مَلِكِ يَوْمِ الدِّينِ (Malik — king)

Both are valid Quran. The pipeline MUST NOT "correct" one reading to another. Preserve whichever reading appears in the source text.

**Detection:** Most scholarly texts in Shamela follow the Hafs reading (the most widespread). Texts from North/West Africa often follow the Warsh reading. Tafsir texts may explicitly discuss variant readings — preserve all variants mentioned.

### 2.4 Metadata Tagging

Every identified Quranic segment must carry:

```python
{
    "quranic_text": True,
    "citation_type": "exact" | "probable_exact" | "paraphrase",
    "surah_number": int | None,       # 1-114
    "ayah_number": int | None,         # varies by surah
    "ayah_range_end": int | None,      # if spanning multiple ayahs
    "reading": "hafs" | "warsh" | "other" | None,  # if identifiable
    "detection_method": "bracket" | "formula" | "reference" | "manual",
}
```

---

## 3. Cross-Reference Patterns

### 3.1 Standard Numbering

The standard Quran citation uses surah number (1-114) and ayah number. Surah ayah counts vary:

| Surah | Name | Ayah Count (Kufi) |
|-------|------|--------------------|
| 1 | الفاتحة | 7 |
| 2 | البقرة | 286 |
| 3 | آل عمران | 200 |
| ... | ... | ... |
| 114 | الناس | 6 |

**Important:** Ayah counts differ between counting systems (Kufi, Basri, Makki, Madani, Shami). The Kufi count is standard in modern printed mushafs (Hafs edition). Most Shamela sources use the Kufi count. If a reference cites an ayah number that is off by 1-2 from the Kufi standard, it may be using a different counting system — do not flag as error.

### 3.2 Named Surah References

Surahs are referenced by name in Arabic. Some require special handling:

| Surah | Name Variants | Trap |
|-------|--------------|------|
| آل عمران | آل عمران, سورة آل عمران | Initial alef-lam-lam: do NOT normalize the ال into the آل |
| الإسراء | الإسراء, بني إسرائيل, سبحان | Has multiple traditional names |
| غافر | غافر, المؤمن | Different names for same surah |
| فصلت | فصلت, حم السجدة | Alternative name with حم prefix |
| محمد | محمد, القتال | Two traditional names |

### 3.3 Juz and Hizb References

Less common in fiqh/hadith scholarship but frequent in tafsir and Quran-specific texts:
- **جزء (juz):** 30 divisions of the Quran. جزء عم = juz 30.
- **حزب (hizb):** 60 divisions (half-juz each).
- **ربع (rub'):** Quarter-hizb markers.

These references identify approximate location rather than exact ayah.

### 3.4 Cross-Reference Resolution

When the pipeline encounters a Quran reference, it should attempt to resolve it to a canonical (surah, ayah) pair:

1. If numeric reference is given (e.g., [2:234]), resolve directly.
2. If named surah is given (e.g., سورة البقرة آية ٢٣٤), map name to number, then resolve.
3. If only surah name is given without ayah (e.g., "كما في سورة البقرة"), record surah-level reference without ayah.
4. If neither surah nor ayah is given but the Quranic text itself is identifiable, attempt to match against a Quran text database to determine the citation's location.

---

## 4. Processing Implications for KR Pipeline

### 4.1 Division Tree — Atomic Quranic Units

Quranic quotations are ATOMIC — they must never be split across divisions, passages, or excerpts. If a Quran citation spans a passage boundary, the boundary must be adjusted to keep the citation intact.

**Rule:** If a passage boundary falls within `quranic_text: true` content, move the boundary to after the end of the Quranic segment plus any immediately following surah-ayah reference.

### 4.2 Excerpting — Quran as Part of Teaching Units

A Quranic citation in a scholarly work almost never stands alone. It is part of a teaching unit that includes:
1. The citation formula (قال تعالى)
2. The Quranic text itself
3. The scholar's explanation or the point being supported

All three components form a single teaching unit for excerpting purposes. Do NOT excerpt the Quranic text alone without its surrounding scholarly context.

### 4.3 Taxonomy — Quranic Cross-References

Every identified Quranic citation creates a link in the taxonomy:
- The source text's taxonomy node gains a cross-reference to the cited surah/ayah
- This enables queries like "all scholarly discussions of ayah X across the library"
- Quranic cross-references are HIGH-VALUE taxonomy links — they connect texts across sciences

### 4.4 Science Scope — Quran Citations Do NOT Determine Science

The presence of Quranic quotations does NOT make a text tafsir. A fiqh text quotes Quran as evidence (dalil). A hadith commentary quotes Quran for context. An aqidah text quotes Quran for creedal proof. The science is determined by the author's purpose and the text's organizational structure, not by what it quotes.

**Only classify as tafsir when:** The text is organized by Quranic verse order AND its primary purpose is explaining the Quran's meaning.

---

## 5. Common Traps

### 5.1 Short Phrases That Match Quran

Many short phrases in common scholarly usage happen to be identical to Quranic text:

| Phrase | Quran Source | Scholarly Usage |
|--------|-------------|----------------|
| الحمد لله | al-Fatihah 1:2 | Common praise formula in any context |
| بسم الله | al-Fatihah 1:1 / al-Naml 27:30 | Common invocation before any action |
| إن شاء الله | al-Kahf 18:69 | Common conditional expression |
| ما شاء الله | al-Kahf 18:39 | Common expression of admiration |
| لا حول ولا قوة إلا بالله | — (NOT Quran) | Commonly mistaken as Quran; it is hadith |
| حسبنا الله ونعم الوكيل | Aal Imran 3:173 | Common du'a formula |

**Rule:** Short phrases (fewer than 5 words) that match Quran text require positive contextual signals (bracket, formula, reference) to be tagged as Quranic. Do NOT tag standalone الحمد لله or بسم الله as Quran citations without surrounding context.

### 5.2 Quotation from Memory

Classical scholars frequently quoted the Quran from memory. Their quotations may:
- Omit a word or phrase from the middle of a verse (quoting the relevant portion only)
- Combine fragments from two different verses in a single sentence
- Use slightly different word order from the standard mushaf text
- Lack diacritics entirely

These are NOT textual corruptions. Tag as `citation_type: paraphrase` and preserve exactly as the scholar wrote.

### 5.3 Du'a Resembling Quran

Supplication (du'a) texts use elevated Arabic that closely resembles Quranic language. Many du'as include Quranic phrases but are not themselves Quran. The du'a corpus (اللهم إني أسألك, أعوذ بالله من, ربنا آتنا) overlaps with Quranic phrases but the overall du'a text is human composition that incorporates divine words.

**Rule:** A du'a that embeds a Quranic phrase should have only the Quranic phrase tagged, not the entire du'a. Example: "اللهم ﴿رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الْآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ﴾" — the bracketed portion is Quran, the "اللهم" prefix is not.

### 5.4 Quranic Vocabulary in Non-Quranic Context

Words that are distinctively Quranic (الصِّرَاطَ, الْمُسْتَقِيمَ, طه, يس) may appear in scholarly discussion without being Quran citations. A scholar writing "الصراط المستقيم هو طريق الحق" is using Quranic vocabulary in their own prose, not citing the Quran.

**Rule:** Quranic vocabulary in authorial prose is NOT a Quran citation. Require explicit citation signals (bracket, formula, or reference) for tagging.
