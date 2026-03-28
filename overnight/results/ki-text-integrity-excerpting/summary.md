# T-3 Text Corruption Probe — Arabic Text Serialization Integrity

**Task:** ki-text-integrity-excerpting
**Engine:** Excerpting (writer.py)
**Threat:** T-3 (Text Corruption) — silent byte-level alteration during serialization

## Verdict: CLEAN — No corruption found

The serialization path `ExcerptRecord → model_dump(mode="json") → json.dumps(ensure_ascii=False) → UTF-8 JSONL → json.loads` preserves Arabic text **byte-for-byte** across all tested corruption vectors.

## What Was Tested

| Vector | Chars Tested | Result |
|--------|-------------|--------|
| Full tashkeel (diacritics) | U+064B–U+0652 (fathah, dammah, kasrah, shadda, sukun, tanwin) | PASS |
| ZWNJ | U+200C between Arabic letters | PASS |
| Tatweel (kashida) | U+0640 inside words | PASS |
| Superscript alef | U+0670 (dagger alef in Quranic text) | PASS |
| **Paragraph breaks** | \n, \n\n, \n\n\n, leading/trailing \n, \r\n | **PASS** (NEW) |
| **JSONL structure** | Newlines inside text don't break line boundaries | **PASS** (NEW) |
| **NFC normalization** | Decomposed hamza/maddah forms NOT composed | **PASS** (NEW) |
| Combined vectors | All special chars + paragraph breaks in one record | PASS |
| All Arabic fields | primary_text, text_snippet, context_hint, evidence_refs, description_arabic, div_path | PASS |
| Gate queue | All corruption vectors through gate_queue.jsonl path | PASS |

## Tests Added

- **12 paragraph break tests** (TestParagraphBreaksRoundtrip): single \n, double \n\n, triple \n\n\n, multiple paragraphs, leading/trailing newlines, CRLF, JSONL structural integrity, combined with tashkeel/ZWNJ/superscript alef/tatweel
- **4 NFC normalization guards** (TestNFCNormalizationGuard): decomposed hamza above, hamza below, alef maddah, mixed composed+decomposed

## Test Counts

- Before: 752
- After: 768 (+16 new tests)
- Failures: 0

## Why This Matters

Paragraph breaks in `primary_text` are a structural integrity concern in JSONL format. If `json.dumps` failed to escape `\n` inside string values, the newline would break the JSONL line boundary, producing truncated or corrupt records on read-back. This test verifies the escape mechanism works correctly.

NFC normalization is a silent corruption vector specific to Arabic OCR sources. Some OCR engines produce decomposed Unicode forms (e.g., alef + combining hamza) instead of precomposed forms (e.g., U+0623). If any layer of the serialization chain applies NFC, the byte representation changes without visible difference in rendered text — but downstream byte-level comparisons (checksums, dedup) would produce false mismatches.
