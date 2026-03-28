# Probe: JSON Arabic Roundtrip — Session Summary

**Date:** 2026-03-28
**Task:** probe-json-arabic-roundtrip
**Result:** PASSED — no corruption detected, 35 new regression tests added

## What Was Tested

The writer (`engines/excerpting/src/writer.py`) uses this serialization pipeline:

```
ExcerptRecord → model_dump(mode='json') → json.dumps(ensure_ascii=False) → disk
disk → open(encoding='utf-8') → json.loads → Python dict
```

The probe verified that **every Arabic-specific Unicode character** survives this
cycle byte-for-byte:

| Corruption Vector | Codepoints | Result |
|---|---|---|
| Full tashkeel | U+064B–U+0652 (8 forms) | ✅ PRESERVED |
| Tanwin (all 3) | U+064B, U+064C, U+064D | ✅ PRESERVED |
| Shadda+kasrah stacked | U+0651 + U+0650 | ✅ PRESERVED |
| ZWNJ | U+200C | ✅ PRESERVED, not escaped |
| Tatweel | U+0640 | ✅ PRESERVED, not stripped |
| Superscript alef | U+0670 | ✅ PRESERVED, not normalized to U+0627 |
| Bismillah ligature | U+FDFD | ✅ PRESERVED |
| Saws ligature | U+FDFA | ✅ PRESERVED |
| Alef Wasla | U+FB50 | ✅ PRESERVED, not NFKC-normalized |

## Fields Verified

- `primary_text` — main Arabic text body
- `text_snippet` — first 80 chars
- `context_hint` — PARTIAL/DEPENDENT context string
- `description_arabic` — Arabic description field
- `div_path` — heading hierarchy (list of strings)
- `evidence_refs[].text_snippet` — Quranic/hadith evidence snippets
- `gate_queue` context dicts — all string values

## Bugs Found

**None.** The writer is correct. Pydantic v2's `model_dump(mode='json')` does not
apply any Unicode normalization, and `json.dumps(ensure_ascii=False)` preserves all
Arabic Unicode characters including presentation forms without escaping.

## Tests Added

**35 new tests** in `engines/excerpting/tests/test_writer_arabic_roundtrip.py`

These tests are **permanent regression guards**. If a future Pydantic version upgrade
or Python version change introduces serialization behavior changes, these tests will
catch it before it corrupts the library.

## Test Count

- Before: 704
- After: 739 (+35)
- Failures: 0
