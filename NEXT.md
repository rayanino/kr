# NEXT — Source Engine Validation, Step 2 Bug Fixes

**Governing document:** `engines/source/VALIDATION_PLAN.md` — read this first in every new session.
**Result preservation:** `/RESULT_PRESERVATION.md` — every test result is a reusable artifact, not disposable validation. Read this before any pipeline run.

**Previous steps:**
- Step 0 COMPLETE — 12/13 fixtures pass. See `engines/source/review/STEP0_RESULTS.md`.
- Step 1 COMPLETE — Code audit + 6 bug fixes. See `engines/source/review/CODE_AUDIT_SESSION6.md`. Fixes in commit `4b51718`. 768 tests passing, 22 skipped.
- Step 2 Phase A RUN COMPLETE — 2,519/2,519 success, zero crashes, 28.5 seconds. Results in `tests/results/source_engine/phase_a/`. Review found 2 critical bugs, 1 moderate bug, and 2 minor fixes.

**Current task:** Fix all 5 Phase A findings before Step 3. See `PHASE_A_FIXES.md` for the complete task specification.

**What to do:**

1. **Read `PHASE_A_FIXES.md`** — contains 5 findings with root cause analysis, concrete examples, fix instructions, and verification criteria.
2. **Fix all 5 issues** in `engines/source/src/extractors/shamela_html.py` (and FIELD_MAP).
3. **Run existing tests** — all 768+ must pass, no regressions.
4. **Re-run Phase A** on the full collection and compare against baseline metrics in the task file.
5. **Write `PHASE_A_LESSONS.md`** — document everything learned for future sessions.

**After fixes:** Step 2 is fully COMPLETE. Proceed to Step 3 (Targeted LLM Probes, 30 books, €5–10). The owner will select 30 books for diversity coverage.

**Important context:**
- The Phase A results zip (2,521 files, 16 MB uncompressed) is the baseline. Keep it for comparison.
- 57 books have author_short only (no card field) — these genuinely need LLM inference in Step 3, not a bug fix.
- 90 books have page count mismatches and 32 have truncation signals — these are real Shamela export quality issues, not extraction bugs. Do not attempt to fix them.
- Zero duplicates found in the collection.
