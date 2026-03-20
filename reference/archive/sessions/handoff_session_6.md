# Handoff Checklist — Session 6: Validation + Writer + Plain Text + Dispatcher

**Date:** 2026-03-20
**Commit:** b9fce31
**Architect:** Claude Chat

---

## Step 2: Test Baseline
- [x] pytest run: `256 passed, 22 skipped`
- [x] Count matches NEXT.md header: yes

## Step 3: File References
| File | Exists | Lines Verified |
|------|--------|---------------|
| `engines/normalization/CLAUDE.md` (109L) | ✅ | ✅ |
| `engines/normalization/SPEC.md` lines 1466–1510 | ✅ | ✅ §5 checks |
| `engines/normalization/SPEC.md` lines 233–239 | ✅ | ✅ Atomic write |
| `engines/normalization/SPEC.md` lines 462–476 | ✅ | ✅ §4.A.4c |
| `engines/normalization/src/validation.py` (101L) | ✅ | ✅ stub |
| `engines/normalization/src/writer.py` (45L) | ✅ | ✅ stub |
| `engines/normalization/src/dispatcher.py` (67L) | ✅ | ✅ empty registry |
| `engines/normalization/contracts.py` (726L) | ✅ | ✅ all models |
| `engines/normalization/src/errors.py` (130L) | ✅ | ✅ all codes |
| `engines/normalization/src/normalizers/base.py` (57L) | ✅ | ✅ interface |
| `engines/normalization/src/normalizers/shamela.py` L1047–1240 | ✅ | ✅ _pass6_assemble |
| `engines/normalization/tests/conftest.py` (189L) | ✅ | ✅ all helpers |
| `engines/normalization/tests/test_kr_output.py` (158L) | ✅ | ✅ 22 skipped |
| `engines/source/contracts.py` lines 46–55 | ✅ | ✅ SourceFormat |
| `engines/normalization/src/structure_discovery.py` L99-106,1144-1158 | ✅ | ✅ |
| `engines/normalization/src/content_flagger.py` L131 | ✅ | ✅ |
| `engines/normalization/src/boundary_continuity.py` L201-211 | ✅ | ✅ |
| `reference/SPEC_ADVERSARY_NORMALIZATION.md` | ✅ | ✅ ADV cases |
| NEW: `engines/normalization/tests/test_validation.py` | N/A | N/A |
| NEW: `engines/normalization/tests/test_writer.py` | N/A | N/A |
| NEW: `engines/normalization/tests/test_plain_text.py` | N/A | N/A |
| NEW: `engines/normalization/src/normalizers/plain_text.py` | N/A | N/A |
| NEW: `tools/smoke_test_validation.py` | N/A | N/A |

## Step 5: SPEC Example Traces
| Trace | Input | Output | Expected | Match |
|---|---|---|---|---|
| ADV-025 (check 3) | 70% Arabic | >= 0.70 → pass | pass | ✅ |
| ADV-025 (check 3) | 69% Arabic | < 0.70 → flag | flag | ✅ |
| ADV-028 (check 2) | 89/100 | 11% > 10% → warn | warn | ✅ |
| ADV-028 (check 2) | 91/100 | 9% ≤ 10% → pass | pass | ✅ |
| ADV-028 (check 2) | 90/100 | 10% = 10% → pass (> not >=) | pass | ✅ |
| ADV-029 (check 3) | 20 identical | no match | no flag | ✅ |
| ADV-029 (check 3) | 21 identical | match | flag | ✅ |
| ADV-026 (check 10) | mid_sentence + `.` | terminal detected | INCONSISTENT | ✅ |
| ADV-026 (check 10) | mid_sentence + `؟` | terminal detected | INCONSISTENT | ✅ |
| ADV-047 (writer) | 2 prev, invalid temp | latest timestamp | restore T115500 | ✅ |
| D6-3 char set | SPEC U+064B-0652,0670,0640 | 10 codepoints | matches SPEC | ✅ |
| Check 5 overlap | [0,5] + [5,10] | 5 >= 5 → overlap | overlap | ✅ |
| Check 5 no overlap | [0,5] + [6,10] | 5 < 6 → ok | ok | ✅ |
| D6-6 CRLF | `\r\n\r\n.split(\n\n)` | 1 part (BROKEN) | FIXED: step 0 | ✅ |

## Step 6: Fixture Testing
| Test | Scope | Result | Acceptable |
|---|---|---|---|
| Check 8 diacritics on ibn_aqil | 5 pages, 106 diacritics | all detected | ✅ |
| Check 8 diacritics on 13 shamela_real | 1987 pages | 229,132 diacritics | ✅ |
| Tatweel U+0640 in check 8 set | 13 fixtures, 262 tatweels | included | ✅ |
| normalize_source on 50 extended | 50 fixtures | 50/50 OK, 0 FAIL | ✅ |
| Minimal NormalizedPackage build | 1 unit | Pydantic validates | ✅ |

## Step 7: Prerequisites
- [x] Test baseline verified (Step 2)
- [x] All Read First files exist (18 items, 5 are NEW)
- [x] All line numbers verified (view tool on each)
- [x] SPEC sections referenced specifically
- [x] Do NOT Do covers scope creep (14 items)
- [x] Verification has concrete pass/fail
- [x] AGENT_ARCHITECTURE.md checked
- [x] ENGINE_BUILD_BLUEPRINT.md checked
- [x] Fixture claims verified by running code
- [x] SPEC thresholds copy-pasted with line numbers
- [x] All SPEC examples traced (Step 5, 14 traces)
- [x] New detection logic tested on fixtures (Step 6)
- [x] Cross-engine contracts verified (PASS)
- [x] validate_handoff.py: 3 findings, all NEW files (accepted)

## Step 8: Adversarial Questions + Deep Review

### Standard adversarial questions:
1. **Judgment calls?** D6-1–D6-10 all resolved. Stub signature change noted.
2. **Missing files?** Added items 15-17 after first review; CleanedPage import specified.
3. **Ambiguous "done"?** 256+48+10=314 tests, 8 ADV, 63 fixture smoke test.
4. **Wrong output passes?** Mitigated: D6-3 WARNING, explicit denominators, D6-10 codepoints.
5. **Unverified claims?** All verified by tool execution.
6. **Missing helpers?** `_make_normalized_package()` factory added.

### Deep review findings (8 total, all applied):
| # | Severity | Finding | Fix Applied |
|---|----------|---------|-------------|
| F1 | HIGH | D6-6 fails on Windows CRLF (`\r\n\r\n.split(\n\n)` → 1 part) | Step 0: CRLF → LF before split |
| F2 | MEDIUM | CleanedPage import path unspecified for plain_text.py | Explicit import from `normalizers.shamela` with line refs |
| F3 | MEDIUM | `_make_cleaned_page()` test helper referenced in production | Direct `CleanedPage(...)` constructor |
| F4 | MEDIUM | 50 extended + 20K samples unused for empirical testing | `smoke_test_validation.py` as deliverable |
| F5 | MEDIUM | Warnings silently discarded in normalize_and_write | Logging + propagation to manifest.normalization_warnings |
| F6 | LOW | Check 5 overlap ambiguous with inclusive end | Explicit: `end >= next_start → overlap` |
| F7 | LOW | validate_package stub has extra `source_html` param | "Remove it" note added |
| F8 | LOW | CRLF test case missing from plain text tests | Added as 13th test (Minimum: 13) |

### Empirical verification:
- All 50 extended fixtures: 50/50 OK via normalize_source()
- 5 NORM_SPARSE_STRUCTURE warnings (expected — sparse headings)
- 2 NORM_LAYER_UNCERTAIN warnings (expected — metadata mismatch)

## Verdict
- [x] ALL boxes checked → READY
- Commit: b9fce31
