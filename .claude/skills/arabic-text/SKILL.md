---
name: arabic-text
description: Guidelines for handling Arabic scholarly text in code. Use when writing any code that processes, stores, compares, or displays Arabic text. Covers encoding, directionality, diacritics, morphological complexity, and common pitfalls.
---

# Arabic Text Handling for KR

Arabic scholarly text has properties that break naive string processing. Every developer (human or AI) working on KR must understand these.

## Critical Properties

### Encoding
- ALL text in KR is UTF-8. No exceptions. No Latin-1, no Windows-1256, no ISO-8859-6.
- Shamela exports may use Windows-1256. Convert at normalization. Verify with frozen source after conversion.
- A single Arabic character may be 2-4 bytes in UTF-8. `len(text)` in Python counts characters, not bytes. Use `len(text.encode('utf-8'))` for byte counts.

### Diacritics (التشكيل)
- Diacritics are MEANINGFUL in scholarly text. فَعَلَ (fa'ala, he did) vs فُعِلَ (fu'ila, it was done) vs فَعَّلَ (fa''ala, he made do).
- NEVER strip diacritics from primary_text.
- For SEARCH and MATCHING: create a separate diacritics-stripped index. Never modify the stored text.
- Diacritics are combining characters in Unicode. A "character" with diacritics is actually multiple code points: ب + َ = بَ

### Normalization Hazards
- Unicode normalization (NFC/NFD/NFKC/NFKD) can ALTER Arabic text. Use NFC consistently, but VERIFY that primary text is preserved byte-for-byte.
- Alef variants: أ إ آ ا are DIFFERENT characters with DIFFERENT meanings. Do NOT normalize them for storage. Normalize only for search indexing.
- Taa marbuta ة vs haa ه — different characters, commonly confused in OCR.
- Hamza placement: ء أ ؤ ئ — meaningful distinctions.

### Text Direction
- Arabic is right-to-left (RTL). Mixed Arabic/Latin text requires bidirectional handling.
- Scholarly texts commonly embed Latin (transliteration, dates, reference numbers).
- Python string operations work correctly on RTL text at the character level. Display is a separate concern.

### Morphological Density
- Arabic words carry more information than English words. A single word can be a complete sentence.
- Word boundaries are not always clear. Prepositions and conjunctions attach to words: والكتاب = و + ال + كتاب
- This affects: tokenization, search, passage boundary detection, atom detection.

### Regex Patterns
- `\d` matches Arabic-Indic digits (٠-٩) in Python 3. Use `[0-9]` for ASCII-only digit matching. This is the #1 source of silent bugs in Arabic text processing.
- `\w` matches Arabic letters. Use `[a-zA-Z]` or `[a-zA-Z0-9]` for Latin-only word characters.
- `\b` (word boundary) does NOT work reliably at Arabic word boundaries — clitics (ال, و, ب) don't create `\b` boundaries.
- `\s` is generally safe but verify ZWNJ (U+200C), ZWSP (U+200B), ZWJ (U+200D) are preserved — they are NOT whitespace in Python 3 but future versions could change.
- Prefer explicit Unicode ranges: `[\u0600-\u06FF]` for Arabic block, `[\u0750-\u077F]` for supplement.

## Code Patterns

### Safe String Comparison
```python
# WRONG — may fail on decomposed vs composed Unicode
text1 == text2

# RIGHT — normalize first, then compare
import unicodedata
unicodedata.normalize('NFC', text1) == unicodedata.normalize('NFC', text2)

# For search matching (diacritics-insensitive):
import regex  # not re — regex handles Unicode properties
stripped = regex.sub(r'\p{Mn}', '', text)  # Remove combining marks
```

### Safe Text Storage
```python
# ALWAYS specify encoding explicitly
with open(path, 'w', encoding='utf-8') as f:
    f.write(text)

# ALWAYS verify after write
with open(path, 'r', encoding='utf-8') as f:
    stored = f.read()
assert stored == text, "Text corruption detected on write"
```

### Safe Text Extraction
```python
# When extracting a substring, verify boundaries don't split a character
# Arabic combining characters (diacritics) must stay with their base character
import unicodedata

def safe_slice(text, start, end):
    """Slice text ensuring we don't split combining character sequences."""
    # Extend end to include any trailing combining marks
    while end < len(text) and unicodedata.combining(text[end]):
        end += 1
    return text[start:end]
```

## Common Pitfalls in KR Context

1. **OCR output may contain Latin lookalikes.** The Arabic ه (haa) and the digit ٥ (5) can be confused with Latin 'o' and '5' by OCR. Always validate character ranges after OCR.

2. **Shamela HTML uses custom encoding for special characters.** The normalization engine handles this, but verify the mapping is complete.

3. **Scholarly abbreviations are domain-specific.** رحمه الله, رضي الله عنه, صلى الله عليه وسلم — these have standard abbreviations that may appear differently across sources.

4. **Verse markers in Quran text.** Quran text includes verse-end markers (۞, ۝) that are Unicode characters, not decorations. Preserve them.

5. **Isnad chains contain proper names.** These names may have unusual spellings and must be preserved exactly as they appear in the source.

## Testing Arabic Text

- ALWAYS use real Arabic text in tests, not transliteration or placeholders.
- Include test cases with: diacritized text, mixed Arabic/Latin, Quran verses, isnad chains, poetry (with meter-significant characters).
- Test with texts from different eras — classical Arabic orthography differs from modern.
- Verify round-trip integrity: text → process → stored text should be byte-identical to input.
