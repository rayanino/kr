# NEXT — Session 7: Integration Testing (Handoff Not Yet Prepared)

## Status: AWAITING HANDOFF PREPARATION

Session 6 was ACCEPTED at commit `760b5f4` (335 tests, 12 skipped, 30/51 ADV).
Session 7 handoff has NOT been written yet. The architect must prepare it in a fresh chat.

## What the architect must do (in a new Claude Chat session)

1. Clone the repo fresh
2. Read this file + `engines/normalization/CLAUDE.md` + last 5 commits
3. Invoke `kr-preparing-cc-handoffs` + `critical-review` skills
4. Write the Session 7 NEXT.md directive for CC

## Session 7 scope (from build plan)

Session 7 is the **final normalization engine build session**. Focus: integration testing.

### What needs to happen

1. **Unskip the 12 remaining tests in `test_kr_output.py`:**
   - `TestContentCensus::test_census_on_synthetic_content` — 1 test
   - `TestContentFlagger` (3 tests): quran_verse, hadith_marker, poetry_verse
   - `TestShamelaNormalizer` (8 tests): schema, Arabic preservation, footnotes, layers, diacritics, pages, structure, flags

2. **Full pipeline integration tests on all 63 fixtures:**
   - Run `normalize_source()` on all 13 real + 50 extended fixtures
   - Verify NormalizedPackage schema compliance for each
   - Verify Arabic text preservation (spot-check diacritics on selected pages)
   - Verify footnote separation on fixtures with known footnotes (03_fiqh, 04_hadith)
   - Verify layer detection on multi-layer fixture (02_nahw_muhaqiq with is_multi_layer=True)
   - Verify structure discovery produces divisions on all fixtures with headings

3. **End-to-end `normalize_and_write()` test:**
   - Write to temp dir, verify manifest.json + content.jsonl, verify roundtrip

4. **Adversarial gap coverage:**
   - Review SPEC_ADVERSARY_NORMALIZATION.md for any untested core ADV cases
   - Currently at 30/51 — identify which remaining ones are core vs deferred

## After Session 7

3-probe evaluation gates the transition from normalization engine to the next engine.
The architect conducts the evaluation using `kr-evaluate` skill.

## Key files for Session 7

- `engines/normalization/tests/test_kr_output.py` — the 12 skipped tests
- `engines/normalization/CLAUDE.md` — module map, build metrics, critical rules
- `engines/normalization/SPEC.md` — behavioral authority
- `tests/fixtures/shamela_real/` — 13 fixtures
- `tests/fixtures/shamela_extended/` — 50 fixtures
- `engines/normalization/tests/conftest.py` — test factories
- `tools/smoke_test_validation.py` — empirical validation script
- `reference/SPEC_ADVERSARY_NORMALIZATION.md` — ADV catalog
- `engines/normalization/KNOWN_LIMITATIONS.md` — L-001 through L-011
- `reference/SPEC_ERRATA.md` — SPEC-NOTE-1 through SPEC-NOTE-3
