# Tool Evaluation Results — 2026-03-28

Three tools evaluated for KR factory integration. Results from hands-on testing.

---

## Task A: usul-data (seemorg/usul-data) — HIGHLY VALUABLE

**Repository:** https://github.com/seemorg/usul-data (MIT license)
**Sources:** OpenITI corpus + Turath.io (includes Shamela) + PDFs + external links

| Metric | Value |
|--------|-------|
| Total authors | 6,159 |
| Total books | 15,655 (16,920 versions) |
| Genres | 39 top-level categories |
| Data format | JSON files (authors.json = 71 MB, books.json = 41 MB) |

### Author Entry Fields (13 fields)

| Field | Type | Example | KR Relevance |
|-------|------|---------|--------------|
| `id` | string | `"0728IbnTaymiyya"` | HIGH — OpenITI URI, prefixed with Hijri death year |
| `year` | int/null | `728` | HIGH — Hijri death year (74.7% coverage = 4,600 authors) |
| `yearStatus` | string/null | `null`, `"Alive"`, `"Unknown"` | HIGH — disambiguates year semantics |
| `primaryNameTranslations` | array of `{locale, text}` | 14 languages incl. Arabic | HIGH — Arabic canonical name |
| `otherNameTranslations` | array | Alternative name forms | MEDIUM — name variants |
| `transliteration` | string | `"Ibn Taymiyya"` | MEDIUM — academic transliteration |
| `locations` | array of `{id}` | `[{"id": "died@basra_..."}, ...]` | MEDIUM — birth/death/residence |
| `bioTranslations` | array | LLM-generated bios | LOW — contains factual errors, NOT scholarly |
| `slug`, `numberOfBooks`, `extraProperties`, `createdAt`, `updatedAt` | various | — | LOW |

**Author ID format:** `{4-digit-hijri-year}{LatinizedName}` (e.g., `0728IbnTaymiyya` = died 728 AH). Living/unknown-date authors get a random hash ID.

**Verified accuracy:** Ibn Taymiyya (728), Ibn Qayyim (751), Nawawi (676), Majd al-Din Ibn Taymiyya (652) — all correct.

### Book Entry Fields (14 fields)

| Field | Type | Example | KR Relevance |
|-------|------|---------|--------------|
| `id` | string | `"0728IbnTaymiyya.Istighatha"` | HIGH — OpenITI book URI |
| `authorId` | string | `"0728IbnTaymiyya"` | HIGH — FK to authors |
| `versions` | array | See below | HIGH — contains Shamela/Turath IDs |
| `genres` | array of `{id}` | `[{"id":"fiqh-hanbali"}]` | HIGH — genre classification (52.1% coverage) |
| `primaryNameTranslations` | array | 14 languages | HIGH — Arabic title |
| `physicalDetails` | object/null | publisher, edition, year | MEDIUM (751 books) |
| `transliteration`, `slug`, `coverImageUrl`, etc. | various | — | LOW-MEDIUM |

**Version sub-object (inside `versions[]`):**

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `value` | string | `"22593"` (turath) or OpenITI URI | **THIS IS THE SHAMELA/TURATH NUMERIC ID for turath sources** |
| `source` | string | `"openiti"`, `"turath"`, `"pdf"`, `"external"` | Source repository |
| `publicationDetails` | object | publisher, editionNumber, publicationYear, publisherLocation, investigator | Rich for turath versions |

**Version source distribution:** turath=7,442 books, openiti=4,726, pdf=2,896, external=501.

**publicationDetails coverage:** publisher=10,428, editionNumber=9,206, publicationYear=8,582, publisherLocation=7,708, investigator (muhaqqiq)=5,758.

### Key Answers

| Question | Answer |
|----------|--------|
| **Death dates (hijri)?** | YES — `year` field for 74.7% of authors (4,600/6,159). Also in ID prefix. |
| **Death dates (gregorian)?** | NO — only Hijri. |
| **Shamela IDs?** | YES — `versions[].value` for `source: "turath"` entries (7,442 books). |
| **Madhab?** | NOT directly on authors. Inferred from book genre tags: `fiqh-hanafi`, `fiqh-maliki`, `fiqh-shafi`, `fiqh-hanbali`, `fiqh-shii`, `fiqh-zaheri`. |

### Full Genre Taxonomy (39 genres)

| ID | Arabic | English | Books |
|----|--------|---------|-------|
| `hadith` | الحديث | Hadith | 1,316 |
| `fiqh-shii` | الفقه الشيعي | Shia Jurisprudence | 964 |
| `fiqh-maliki` | الفقه المالكي | Maliki Jurisprudence | 911 |
| `fiqh` | الفقه | Jurisprudence | 867 |
| `creeds-and-sects` | العقائد والملل | Creeds and Sects | 759 |
| `biographies-and-generations` | التراجم والطبقات | Biographies and Classes | 665 |
| `fiqh-hanafi` | الفقه الحنفي | Hanafi Fiqh | 585 |
| `literature` | الأدب | Literature | 564 |
| `ulum-al-hadith` | علوم الحديث | Hadith Studies | 551 |
| `fiqh-shafi` | الفقه الشافعي | Shafi'i Jurisprudence | 512 |
| `history` | التاريخ | History | 475 |
| `usul-al-fiqh` | أصول الفقه | Usul al-Fiqh | 473 |
| `tasawuf` | التصوف | Sufism | 427 |
| `blagha` | البلاغة | Rhetoric | 367 |
| `fatawa` | الفتاوى | Fatwas | 333 |
| `quranic-sciences` | علوم القرآن | Quranic Sciences | 314 |
| `tafsir` | التفسير | Tafsir | 240 |
| `poetry` | الشعر | Poetry | 239 |
| `fiqh-al-lugha` | فقه اللغة | Philology | 242 |
| `fiqh-hanbali` | الفقه الحنبلي | Hanbali Jurisprudence | 211 |
| `arabic-grammar-and-morphology` | النحو والصرف | Grammar and Morphology | 197 |
| `qawaid-fiqhiya` | القواعد الفقهية | Jurisprudential Rules | 191 |
| `language-dictionaries` | المعاجم اللغة | Lexicography | 175 |
| `geography` | الجغرافيا | Geography | 152 |
| `sira-nabawiya` | السيرة النبوية | Prophetic Biography | 142 |
| `islamic-governance-and-judiciary` | السياسة الشرعية والقضاء | Public Policy and Judiciary | 97 |
| `genealogy-arabic` | الأنساب | Genealogy | 81 |
| `book-indices-and-guides` | فهارس الكتب والأدلة | Bibliographies and Guides | 79 |
| `rudud` | الردود | Responses | 73 |
| `philosophy` | الفلسفة | Philosophy | 68 |
| `natural-sciences` | علم الطبيعيات | Natural Science | 51 |
| `logic` | المنطق | Logic | 43 |
| `other-madhabs` | مذاهب أخرى | Other Religions | 26 |
| `fiqh-zaheri` | الفقه الظاهري | Zahiri Jurisprudence | 26 |
| `dialectics-and-debate` | علم الجدل والمناظرة | Dialectics and Debate | 24 |
| `metrics-and-rhymes` | العروض والقوافي | Prosody and Rhyme | 20 |
| `astronomy` | علم الفلك | Astronomy | 17 |
| `ilm-al-kalam` | علم الكلام | Islamic Theology | 14 |
| `tafsir-ahlam` | تفسير الأحلام | Dream Interpretation | 8 |

### Limitations

- No madhab field on authors (only inferable from book genres)
- No full name decomposition (ism, nasab, kunya, laqab, nisba not parsed)
- LLM-generated bios contain factual errors — do NOT trust for scholarly claims
- 47.9% of books lack genre tags
- No Gregorian dates
- Static dump (4 commits total), unclear update frequency
- 71 MB authors.json is bloated by 14-language translations and LLM bios

### Recommended KR Integration

1. Extract a cross-reference index: Arabic author names + death years + Turath IDs (strip 14-language translations and LLM bios)
2. Use Turath numeric IDs to link KR's 2,519 Shamela exports to this dataset
3. Use 4,600 death years as validation ground truth for source engine consensus
4. Use 39-genre taxonomy as candidate mapping for taxonomy engine (noting KR will be more granular)
5. Do NOT trust LLM-generated bios for any scholarly claim

---

## Task B: CAMeL Tools — PARTIALLY USEFUL, PARTIAL INSTALL

**Package:** `camel-tools` v1.4.1 (NYU Abu Dhabi)
**Install:** Partial on Windows/Python 3.13 — core works, C extensions fail

### What Works

| Feature | Status | Notes |
|---------|--------|-------|
| Unicode normalization (`normalize_unicode`) | PASS | NFC normalization |
| Alef normalization (`normalize_alef_ar`) | PASS | Normalizes hamzated alefs to bare alef |
| Dediacritization (`dediac_ar`) | PASS | Strips all tashkeel correctly |
| Diacritics detection | PASS | Character range check works |
| Simple word tokenization | PASS | Whitespace-based only (does NOT split clitics like والحمد) |
| Morphological analysis | PASS | Rich output: root, POS, gloss, diacritized form, Buckwalter |
| Buckwalter transliteration | PASS | Round-trip preserves Arabic text |
| Arabic charsets | PASS | 42 letters, 10 diacritics defined |

### Morphological Analysis Quality

Rich structured output per word:
- **Root extraction** (ك.ت.ب for كتاب, ف.ق.ه for fiqh, ح.د.ث for hadith) — useful for root-based search
- **5-18 analyses per word** depending on ambiguity
- **POS tags** (noun, verb, noun_prop, etc.)
- **English glosses** — scholarly terms recognized: "Imam", "Sheikh", "(Islamic) jurisprudence", "Hadith", "exegesis"
- **Diacritized forms** — full tashkeel restored
- **Buckwalter encoding** for each analysis

### What Doesn't Work (on Windows without C compiler)

| Feature | Status | Reason |
|---------|--------|--------|
| `editdistance` dependency | FAIL | No wheel for Python 3.13/Windows, needs C compiler |
| `camel-kenlm` dependency | FAIL | Needs cmake + C compiler |
| Dialect identification | BLOCKED | Needs camel-kenlm |
| BERT-based disambiguation | BLOCKED | Needs camel-kenlm |
| NER, Sentiment | BLOCKED | Needs missing dependencies |

### Issues

1. **Windows encoding:** All commands need `PYTHONIOENCODING=utf-8` — Arabic output crashes on cp1252 without it
2. **No `camel_data` CLI on PATH** — must use `python3 -m camel_tools.cli.camel_data`
3. **No "light" data package** — v1.4.1 has 26 named packages, no "light" meta-package
4. **`simple_word_tokenize` is whitespace-only** — does not split clitics; morphological tokenization needs full disambiguation pipeline
5. **Installing Visual Studio Build Tools (C++ workload)** would resolve the C extension issues

### KR Relevance Assessment

- **Root extraction** — most valuable feature; could power scholarly search in Scholar Interface
- **Normalization functions** — overlap with what KR normalization engine already has
- **Buckwalter transliteration** — useful for debugging Arabic text
- **Verdict:** DEFER to Scholar Interface phase. Not needed for current pipeline build.

---

## Task C: Mutmut — BLOCKED ON WINDOWS

**Package:** `mutmut` v3.5.0
**Install:** Succeeds via pip, but CANNOT EXECUTE on Windows

### What Happened

| Check | Result |
|-------|--------|
| Installation | OK — pip install succeeds, v3.5.0 |
| Python import | Partial — `mutmut.__version__` works |
| Any command execution | BLOCKED — hard `sys.exit(1)` on Windows |
| Mutant generation | Not possible on native Windows |
| File parsing | Not possible on native Windows |

### Root Cause

`mutmut/__main__.py` lines 8-10 contain a hard `platform.system() == 'Windows'` check that calls `sys.exit(1)` with message "please use the WSL". Even if bypassed, line 18 imports `resource` (Unix-only stdlib module), and the tool uses Unix signal handling incompatible with Windows.

**Tracked at:** https://github.com/boxed/mutmut/issues/397

### Workarounds

1. **Run inside WSL2** (as mutmut itself suggests) — most viable for factory
2. Use `cosmic-ray` or `mutatest` (Windows-compatible alternatives)
3. Use mutmut v2.x (reportedly had partial Windows support)

### KR File Survey (completed before Windows block)

80+ source files across 7 engines. Small mutation testing candidates:
- `atomization/src/attribution_detection.py` (28 lines, 1 function)
- `atomization/src/completeness_scoring.py` (26 lines, 1 function)
- `passaging/src/emitter.py` (25 lines, 1 function)

Note: Several files with Arabic content need `encoding='utf-8'` to open on Windows.

### Verdict

DEFER to WSL2 factory setup. When factory runs on WSL2 (planned in roadmap), mutmut becomes viable as a quality mode. Alternative: try `cosmic-ray` on native Windows now.

---

## Summary Table

| Tool | Verdict | Priority | When to Integrate |
|------|---------|----------|-------------------|
| **usul-data** | HIGH VALUE — 4,600 death dates + 7,442 Shamela IDs + 39-genre taxonomy | HIGH | Before next source engine validation |
| **CAMeL Tools** | Partial install, morphological analysis works, normalization overlaps with KR | LOW | Scholar Interface phase |
| **Mutmut** | Blocked on Windows, needs WSL2 | LOW | Factory Session 3+ on WSL2 |
