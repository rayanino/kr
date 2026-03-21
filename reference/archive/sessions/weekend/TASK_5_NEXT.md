# NEXT — Weekend Task 5: Test Fixture Expansion + Regression Hardening

## Current Position

- **Phase:** Regression hardening
- **Mode:** AUTONOMOUS TEST WRITING — architect unavailable
- **Previous:** Tasks 1-4 complete. Sweeps done, bugs fixed, calibration produced, LLM probes run.
- **Purpose:** Turn the most interesting edge cases from the sweeps into permanent test fixtures. Add regression tests that protect against future breakage.

## Rules for This Session

1. **You MAY add test fixtures** to `tests/fixtures/shamela_edge_cases/` and write new test functions.
2. **You MAY modify existing test files** to add new test cases. Do NOT modify existing test assertions.
3. **Do NOT modify engine source code.** Tests only.
4. **Do NOT modify SPECs or contracts.**
5. **Budget: €0.** No LLM API calls.

## What to Do

### Step 1: Select Edge Cases for Permanent Fixtures

From the sweep results (Tasks 1-3), identify 10-15 books that represent unique edge cases worth preserving as test fixtures. Categories:

| Category | Target Count | What to Look For |
|----------|-------------|------------------|
| Crash-causing (now fixed) | 3-4 | Books that crashed in Task 1 but were fixed in Task 2. The fixture preserves the regression test. |
| Unusual HTML structure | 2-3 | Books with HTML patterns not seen in the 63 existing fixtures (unusual div nesting, non-standard class names, embedded objects). |
| Multi-layer edge cases | 2-3 | Books where auto-upgrade triggered correctly OR incorrectly (from CALIBRATION_REPORT.md B.2). |
| Extreme metrics | 2-3 | Very large (>500 pages), very small (1-3 pages), very low Arabic ratio, zero diacritics. |
| Warning-heavy | 1-2 | Books with unusual warning patterns not in existing fixtures. |

**Fixture size limit:** Each fixture .htm file must be under 500KB. If a book is larger, extract the relevant pages (first 10 + the page that triggers the edge case) into a minimal fixture.

### Step 2: Create Fixtures

For each selected book:

1. Copy the .htm file (or create a minimal extract) to `tests/fixtures/shamela_edge_cases/`
2. Name it descriptively: `edge_{category}_{brief_description}.htm` (e.g., `edge_crash_missing_pagetext_div.htm`)
3. Create a companion `.json` metadata file with:
   ```json
   {
     "original_book": "full book name from shamela-export-samples",
     "category": "crash_fix|unusual_html|multi_layer|extreme|warning",
     "description": "Why this fixture is interesting",
     "discovered_in": "weekend_sweep_task1",
     "key_feature": "what makes this different from existing fixtures",
     "expected_behavior": "what the normalization engine should do with this"
   }
   ```

### Step 3: Write Tests

For each new fixture, add at least one test to the appropriate test file:

**For normalization engine fixtures:**
- Add to `engines/normalization/tests/test_integration.py` (or create `test_edge_cases.py` if it doesn't exist)
- Use the existing test helpers from `conftest.py`: `_make_source_metadata()`, `_make_cleaned_page()`, `_full_pipeline()`
- Each test should verify:
  - Pipeline completes without crash (smoke test)
  - Content unit count matches raw PageText div count (anti-page-loss)
  - Validation passes (or produces expected warnings, not fatals)
  - Any fixture-specific assertion (e.g., "this multi-layer fixture produces ≥2 layer types")

**For source engine fixtures:**
- Add to `engines/source/tests/test_deterministic.py` (or create `test_edge_cases.py`)
- Each test should verify:
  - Format detection succeeds
  - Extraction completes without crash
  - Expected fields are present

### Step 4: Check for Tautological Tests

**CRITICAL (S7 lesson):** For every new test assertion, ask: "What BROKEN implementation would still pass this?"

Bad (tautological):
```python
assert pkg.manifest.total_content_units == len(pkg.content_units)
# Both set by the same code — catches nothing
```

Good (independent source of truth):
```python
raw_pages = count_pagetext_divs(fixture_path)
assert len(pkg.content_units) == raw_pages  # Independent ground truth
```

### Step 5: Run Full Test Suite

```bash
python -m pytest engines/normalization/tests/ -v --tb=short
python -m pytest engines/source/tests/ -v --tb=short
```

Record before/after test counts. Zero regressions allowed.

### Step 6: Commit

```bash
git add tests/fixtures/shamela_edge_cases/
git add engines/normalization/tests/
git add engines/source/tests/
git commit -m "harden: Add N edge-case fixtures + M regression tests from weekend sweep"
```

## Read First

1. This file (NEXT.md)
2. `results/CALIBRATION_REPORT.md` — identifies interesting edge cases
3. `results/SWEEP_BUG_TRIAGE.md` — crash patterns (for regression fixtures)
4. `results/SWEEP_FIX_SUMMARY.md` — which bugs were fixed (test the fixes)
5. `engines/normalization/tests/conftest.py` — test helper patterns
6. `tests/fixtures/shamela_edge_cases/` — existing edge case fixtures (don't duplicate)

## Do NOT Do

1. **Do NOT modify engine source code.**
2. **Do NOT modify existing test assertions.** Only ADD new tests.
3. **Do NOT add fixtures larger than 500KB.** Extract minimal reproducing cases.
4. **Do NOT run LLM API calls.**
5. **Do NOT modify SPECs or contracts.**

## Verification

- [ ] All new fixtures are in `tests/fixtures/shamela_edge_cases/` with companion .json
- [ ] Each fixture has at least one test
- [ ] No tautological assertions (verified per Step 4)
- [ ] Full test suite passes with zero regressions
- [ ] Test count increased (document before/after in commit message)
- [ ] No engine source code modified
- [ ] No existing test assertions changed
