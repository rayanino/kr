# NEXT — Step 4 Preparation (Claude Chat)

## Status: Step 3 Bug Fixes COMPLETE → Step 4 Preparation

Claude Code fixed BUG-01 through BUG-05 (commit `c640a9b`). 562 tests pass. No smoke test with real books yet.

The `STEP4_PREPARATION_PLAN.md` defines the complete workflow. Read it first.

---

## Current Task: Phase A — Verify Bug Fixes + Smoke Test + Book Selection

Before any €20 pipeline run, we must:

1. **Verify Claude Code's fixes** — pull the repo, read the diff from `c640a9b`, verify each of the 5 bug fixes against `STEP3_FINAL_BUG_LIST.md`. Multiple review rounds.

2. **Write the Claude Code prompt for Step A** — a prompt that tells Claude Code (on the owner's machine) to:
   - Run the full test suite
   - Run 5 specific books end-to-end as a smoke test
   - Analyze Shamela category distribution across all 2,519 books
   - Generate stratified random sample of ~130 new books

3. **After owner runs Step A** — verify smoke test results and book selection before proceeding to Step B (€20 pipeline run).

---

## Key State

- **Pipeline version:** `c640a9b` (post-bug-fix, untested with real LLM calls)
- **Phase C manifest:** `needs_rerun: false` for all 73 books — MUST be updated to `true` before Step 4 run (they were processed on pre-fix pipeline `10644a6`)
- **Budget spent:** €9.20 (Step 0: €1.80, Phase C: €7.00, smoke test pending: ~€0.50)
- **Budget remaining:** ~€90.80
- **Step 4 estimated cost:** ~€20 (200 books × €0.10/book)

## Critical Context

- **BUG-01 Layer 2:** Check 5c (author-science mismatch) was downgraded from gate to warning. Reasoning: 0/76 true positives, 100% false-positive rate, semantic mismatch in data source. Decision documented in `STEP3_FINAL_BUG_LIST.md` with full analysis.
- **BUG-03 refinement:** Tahqiq-note override does NOT require muhaqiq in extraction (1/4 known false positives lacks muhaqiq). Layer-type pattern alone is sufficient.
- **Phase C correction:** Aggregation report Section 2.7 incorrectly claimed 3/4 ML disagreement cases had wrong pipeline output. Actually, Command A is canonical in 3/4 cases (higher author_conf), so all 4 canonical results are correct.
- **22 Phase C success books succeeded BECAUSE their canonical model had empty or None-valued school_affiliations** — so BUG-01's {"primary": school} never got stored, and check 5c never fired.

## Governing Documents (read in this order)

1. **This file** (NEXT.md)
2. **STEP4_PREPARATION_PLAN.md** — the complete 4-step workflow
3. **STEP3_FINAL_BUG_LIST.md** — the 7 bugs, evidence, fixes, and self-review appendix
4. **PHASE_C_AGGREGATION_REPORT.md** — Phase C evaluation results (76 verdicts, 59V/17P)
5. **PHASE_C_ERRATA.md** — corrections to the evaluation framework
6. **PHASE_C_EVALUATION_FRAMEWORK.md** — how evaluation sessions work
7. **RESULT_PRESERVATION.md** — result persistence protocol
8. **engines/source/VALIDATION_PLAN.md** — Step 4 definition and GO/NO-GO criteria
9. **SPEC_CORE.md** — behavioral authority for the source engine
