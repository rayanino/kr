---
name: arabic-text-quality
description: Detecting OCR corruption, encoding artifacts, diacritic quality, and Shamela-specific issues in Arabic scholarly text. Use when processing source text, evaluating text quality, debugging encoding problems, or assessing whether text needs re-extraction.
---

# Arabic Text Quality Assessment

Arabic scholarly text arrives through multiple digitization paths, each with characteristic quality issues. This skill teaches how to detect corruption, assess quality, and decide whether text is pipeline-ready or needs re-extraction.

---

## 1. OCR Corruption Patterns

Arabic OCR has systematic confusion patterns due to letter shape similarity. These create SILENT corruption — the text looks plausible but is wrong.

### High-Frequency Character Confusions

| Correct | Confused With | Context | Detection Heuristic |
|---------|--------------|---------|---------------------|
| ه (ha) | ة (ta marbuta) | Word-final | If word-final ه follows a fatha or appears in a known pattern (e.g., كتابه vs كتابة), check against dictionary |
| ة (ta marbuta) | ه (ha) | Word-final | Reverse of above — ة misread as ه changes meaning (صلاة→صلاه is invalid) |
| ي (ya) | ئ (ya+hamza) | All positions | Missing hamza seat — الشيء→الشي is common OCR error |
| ا (alif) | أ (alif+hamza) | Word-initial | أحمد→احمد — OCR frequently drops initial hamza |
| ة (ta marbuta) | ۃ (ta marbuta goal) | Word-final | Urdu ta marbuta substituted — encoding issue, not OCR |
| ك (kaf) | ک (kaf with no dot) | All positions | Persian/Urdu kaf vs Arabic kaf — U+06A9 vs U+0643 |
| ي (ya) | ى (alif maqsura) | Word-final | ى and ي are DISTINCT in Arabic but OCR confuses them. مصطفى≠مصطفي |
| ر (ra) | ز (zayn) | All positions | Dot presence/absence — OCR dot detection failure |
| د (dal) | ذ (dhal) | All positions | Same shape, dot above — OCR dot detection |
| ع (ayn) | غ (ghayn) | All positions | Dot above — same issue |
| ح (ha) | خ (kha) / ج (jim) | All positions | Three similar shapes, differentiated by dots |
| ب (ba) | ت (ta) / ث (tha) | Initial/medial | Dot count and placement |
| ن (nun) | dot of adjacent letter | Isolated | OCR merges nun dot with adjacent letter dot |

### Detection Strategy
1. **Frequency analysis**: Real Arabic text has predictable letter frequencies. Abnormal ه/ة ratio or ي/ى ratio suggests systematic OCR confusion.
2. **Dictionary check**: Run suspicious words against a wordlist. Non-dictionary words with known confusion pairs → likely OCR error.
3. **Hamza consistency**: If text has أ sometimes and ا sometimes for the same word root → inconsistent OCR, not author variation.
4. **Diacritic coverage**: If diacritics appear sporadically (some words fully diacritized, most bare) → likely partial OCR diacritic detection, not authorial choice.

---

## 2. Encoding Issues

### UTF-8 Validation
All KR text MUST be UTF-8. Common encoding artifacts:

| Symptom | Cause | Fix |
|---------|-------|-----|
| Ù…Ø­Ù…Ø¯ instead of محمد | UTF-8 bytes decoded as Latin-1 then re-encoded | Decode as Latin-1, re-encode as UTF-8 |
| Â followed by Arabic | Double UTF-8 encoding | Decode once, not twice |
| ? or □ replacing characters | Encoding truncation or unsupported char | Re-extract from source |
| ﻻ (U+FEFB) instead of لا | Arabic presentation form | Normalize to composed form لا (lam + alif) |
| Isolated diacritics without base letters | Encoding split | Invalid text — re-extract |

### Presentation Forms (U+FB50-U+FEFF)
Arabic presentation forms are rendering-level characters that should NOT appear in stored text. Their presence indicates:
- Copy from a PDF renderer that used presentation forms
- Bad conversion from legacy encoding
- **Action**: Normalize to standard Arabic block (U+0600-U+06FF) equivalents

### Windows-1256 Artifacts
Shamela originally used Windows-1256. Conversion artifacts include:
- Misplaced diacritics (diacritic attached to wrong base letter)
- Missing characters replaced with `?` or `\x00`
- Truncated multi-byte sequences
- **Detection**: Check for byte sequences that are valid Windows-1256 but invalid UTF-8

---

## 3. Diacritic Quality Assessment

### Diacritization Levels
Arabic text exists on a spectrum of diacritization:

| Level | Description | Typical Source | KR Handling |
|-------|-------------|----------------|-------------|
| **Full (مشكول بالكامل)** | Every letter has explicit diacritic | Quran, classical mutun, learning texts | Preserve exactly — diacritics ARE content |
| **Partial (مشكول جزئياً)** | Ambiguous words diacritized, common words bare | Most scholarly texts | Preserve as-is — partial diacritization is intentional |
| **Minimal (غير مشكول)** | No diacritics except where essential | Modern prints, newspapers | Record as undiacritized — DO NOT add diacritics |
| **Inconsistent** | Random diacritization — some pages full, some bare | OCR artifacts, mixed sources | Flag for quality review — likely OCR problem |

### Diacritic Integrity Checks
- **Count ratio**: Count diacritics (U+064B-U+0653, U+0670) per Arabic base letter. Fully diacritized text has ratio ~1.0-1.5. Partial: 0.1-0.3. Bare: <0.05.
- **Consistency**: If ratio varies dramatically between pages/sections → quality problem.
- **Shadda (ّ) test**: Shadda (gemination mark) is the rarest diacritic. Its presence strongly indicates intentional diacritization.
- **Tanwin test**: Tanwin (ً ٌ ٍ) at word boundaries is a strong diacritization signal.

### KR Rules for Diacritics
1. NEVER add diacritics that aren't in the source
2. NEVER remove diacritics that are in the source
3. Record the diacritization level as metadata
4. If diacritization is inconsistent, flag for re-extraction review
5. Diacritics in Quran citations MUST match mushaf text exactly

---

## 4. Shamela-Specific Quality Issues

### Known Shamela HTML Patterns

| Issue | Pattern | Detection | Severity |
|-------|---------|-----------|----------|
| **Missing pages** | Page number jumps (e.g., p.45 → p.48) | Page sequence gap detection | HIGH — content loss |
| **Concatenated books** | Two different books merged in one entry | Author/topic sudden change mid-text | HIGH — misattribution |
| **Metadata mismatch** | Shamela author field doesn't match actual author | Compare metadata vs. colophon/introduction | MODERATE |
| **HTML artifacts** | Leftover `&amp;`, `<br>`, `</span>` in text | Regex for HTML entities in content | LOW — cleanup |
| **Empty sections** | Division headers with no content | Empty div after heading | LOW — structural |
| **Encoding mix** | Arabic + Latin numeral confusion in page refs | ١٢٣ vs 123 mixed in same field | LOW — normalize |
| **Footnote displacement** | Footnotes placed at wrong location | Footnote reference without corresponding note | MODERATE |

### Quality Score
For each source text, compute a quality assessment:
- **A (pipeline-ready)**: UTF-8 clean, consistent diacritization, complete pages, metadata matches content
- **B (usable with caveats)**: Minor encoding artifacts, 1-2 missing pages, metadata partially matches
- **C (needs review)**: OCR artifacts, inconsistent diacritization, multiple missing pages
- **D (re-extract)**: Major encoding issues, concatenated books, completely wrong metadata

---

## 5. Text Integrity Verification

### Frozen Source Comparison
After any processing step, verify against the frozen source:
```python
# Pseudocode — do NOT modify frozen source
original_hash = sha256(frozen_source_bytes)
processed_text_bytes = processed_text.encode('utf-8')
# The hash will differ (processing changes text), but:
# - Arabic letter count must be >= original (no lost letters)
# - Diacritic count must be == original (no lost/added diacritics)
# - Quran citations must be byte-identical to original
```

### Processing Invariants
After ANY processing step, these must hold:
1. No Arabic base letter (U+0621-U+064A) was deleted
2. No diacritic (U+064B-U+0653) was added or removed
3. No encoding conversion occurred (still UTF-8)
4. No Unicode normalization (NFC/NFD/NFKC/NFKD) was applied
5. Quran citations are byte-identical to source
6. Page boundary markers are preserved
