# Handoff Checklist — Session 6: Validation + Writer + Plain Text + Dispatcher

**Date:** 2026-03-20
**Commit:** 5d9ab43
**Architect:** Claude Chat

---

## Step 2: Test Baseline
- [x] pytest run: `256 passed, 22 skipped`
- [x] Count matches NEXT.md header: yes ("256 tests passing, 22 skipped")

## Step 3: File References
| File | Exists | Lines Verified |
|------|--------|---------------|
| `engines/normalization/CLAUDE.md` (109L) | ✅ | ✅ |
| `engines/normalization/SPEC.md` lines 1466–1510 | ✅ | ✅ §5 validation checks |
| `engines/normalization/SPEC.md` lines 233–239 | ✅ | ✅ Atomic write + recovery |
| `engines/normalization/SPEC.md` lines 462–476 | ✅ | ✅ §4.A.4c plain text |
| `engines/normalization/src/validation.py` (101L) | ✅ | ✅ stub with signatures |
| `engines/normalization/src/writer.py` (45L) | ✅ | ✅ stub with signature |
| `engines/normalization/src/dispatcher.py` (67L) | ✅ | ✅ empty registry |
| `engines/normalization/contracts.py` (726L) | ✅ | ✅ all models read |
| `engines/normalization/src/errors.py` (130L) | ✅ | ✅ all codes present |
| `engines/normalization/src/normalizers/base.py` (57L) | ✅ | ✅ interface verified |
| `engines/normalization/src/normalizers/shamela.py` lines 1047–1240 | ✅ | ✅ _pass6_assemble |
| `engines/normalization/tests/conftest.py` (189L) | ✅ | ✅ all helpers verified |
| `engines/normalization/tests/test_kr_output.py` (158L) | ✅ | ✅ 22 skipped tests |
| `engines/source/contracts.py` lines 46–55 | ✅ | ✅ SourceFormat enum |
| `engines/normalization/src/structure_discovery.py` lines 99-106, 1144-1158 | ✅ | ✅ StructureResult + discover_structure |
| `engines/normalization/src/content_flagger.py` line 131 | ✅ | ✅ compute_content_flags |
| `engines/normalization/src/boundary_continuity.py` lines 201-211 | ✅ | ✅ classify_boundary |
| `reference/SPEC_ADVERSARY_NORMALIZATION.md` | ✅ | ✅ ADV cases verified |
| `engines/normalization/tests/test_validation.py` (NEW) | N/A | N/A — CC creates |
| `engines/normalization/tests/test_writer.py` (NEW) | N/A | N/A — CC creates |
| `engines/normalization/tests/test_plain_text.py` (NEW) | N/A | N/A — CC creates |
| `engines/normalization/src/normalizers/plain_text.py` (NEW) | N/A | N/A — CC creates |

## Step 5: SPEC Example Traces
| SPEC Section / ADV | Input | Algorithm Output | Expected | Match |
|---|---|---|---|---|
| ADV-025 (check 3) | 70% Arabic chars | >= 0.70 → passes | passes | ✅ |
| ADV-025 (check 3) | 69% Arabic chars | < 0.70 → flagged | flagged | ✅ |
| ADV-028 (check 2) | 89/100 units | 11% > 10% → warning | warning | ✅ |
| ADV-028 (check 2) | 91/100 units | 9% ≤ 10% → pass | pass | ✅ |
| ADV-028 (check 2) | 90/100 units | 10% = 10% → pass (> not >=) | pass | ✅ |
| ADV-029 (check 3) | 20 identical chars | regex `(.)\1{20,}` → no match | no flag | ✅ |
| ADV-029 (check 3) | 21 identical chars | regex `(.)\1{20,}` → match | flag | ✅ |
| ADV-026 (check 10) | mid_sentence + `.` ending | terminal punct detected | CONTINUITY_INCONSISTENT | ✅ |
| ADV-026 (check 10) | mid_sentence + `؟` ending | terminal punct detected | CONTINUITY_INCONSISTENT | ✅ |
| ADV-047 (writer) | 2 prev dirs, invalid temp | latest timestamp selected | restore from T115500 | ✅ |
| ADV-021/045 (check 8) | 15 diacritics in source | DIACRITICS_CHECK8 set, 10 codepoints | counts match | ✅ |
| D6-3 char set | SPEC U+064B–U+0652, U+0670, U+0640 | 10 codepoints exactly | matches SPEC line 1501 | ✅ |

## Step 6: Fixture Testing
| Detection Logic | Total Pages | Matches | Rate | Acceptable |
|---|---|---|---|---|
| Check 8 diacritics set on ibn_aqil | 5 pages | 106 diacritics | 21.2/page | ✅ |
| Check 8 diacritics set on 13 shamela_real fixtures | 1987 pages | 229,132 diacritics | varies | ✅ |
| Tatweel (U+0640) included in check 8 | 13 fixtures | 262 tatweels total | present in 9/13 | ✅ important — would be missed by old set |

No new Arabic detection patterns in this session — check 8 operates on known Unicode codepoints, not text patterns.

## Step 7: Prerequisites
- [x] Test baseline verified (Step 2)
- [x] All Read First files exist (18 items, 4 are NEW)
- [x] All line numbers verified (view tool on each)
- [x] SPEC sections referenced specifically (§5 lines 1472-1505, §4.A.2 lines 233-239, §4.A.4c lines 462-476)
- [x] Do NOT Do covers scope creep (14 items, including checks 11-14, Layer 2/3, census, LLM tier 3, tight coverage)
- [x] Verification has concrete pass/fail (256 existing + 47 new + 10 unskipped, 8 ADV cases, cross-engine contracts)
- [x] AGENT_ARCHITECTURE.md checked (build phase, focused sessions, one concern per session)
- [x] ENGINE_BUILD_BLUEPRINT.md checked (session design principles, handoff prompt requirements)
- [x] Fixture claims verified by running code (diacritics check 8 set tested on all 13 fixtures)
- [x] SPEC thresholds copy-pasted with line numbers (70% Arabic, >20 identical chars, ±10% coverage, terminal punct set, diacritics codepoints)
- [x] All SPEC examples traced (Step 5) — 12 traces, all match
- [x] New detection logic tested on fixtures (Step 6) — check 8 diacritics set verified
- [x] Cross-engine contracts verified (`tools/check_cross_engine_contracts.py` PASS)

## Step 8: Adversarial Questions
1. **Judgment calls not covered?** D6-1 through D6-10 cover all design decisions. Check 8 placement (normalizer vs validate_package), footnote comparison scope, diacritics character set, plain text splitting algorithm, coverage check scope, mojibake pattern, terminal punctuation set — all resolved.
2. **Missing files?** Added items 15-17 (structure_discovery, content_flagger, boundary_continuity) after adversarial read found plain text normalizer needs their signatures. All Read First files verified.
3. **Ambiguous "done"?** Pass criteria specifies exact counts: 256 existing + 47 new + 10 unskipped = 313 total. 8 ADV cases with dedicated tests. Cross-engine PASS.
4. **Wrong output that passes verification?** Risk: CC could implement check 3 Arabic ratio using total chars instead of non-whitespace-non-punct chars → wrong threshold behavior. Mitigated: NEXT.md explicitly says "divide by total non-whitespace-non-punctuation chars." Risk: CC could use `_ARABIC_DIACRITICS` instead of `DIACRITICS_CHECK8` → wrong character set. Mitigated: D6-3 explicit warning with codepoint counts. Risk: check 10 uses wrong terminal punct set → Arabic question mark `؟` missed. Mitigated: D6-10 enumerates exact Unicode codepoints.
5. **Unverified claims?** All SPEC line numbers verified by view tool. All threshold values copy-pasted from SPEC. All fixture data from pytest runs. ADV case line numbers verified by grep.
6. **Missing test helpers?** Added `_make_normalized_package()` factory instruction for conftest.py. CC needs this to construct test packages for validation/writer tests.

## Verdict
- [x] ALL boxes checked → READY
- Commit: e6e1573
