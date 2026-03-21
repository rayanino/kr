# NEXT — Overnight Autonomous Work Program (8+ hours)

## Mode

**FULLY AUTONOMOUS — owner is asleep, architect is unavailable.**

You will work through 5 phases sequentially. Commit after each phase. Do NOT ask questions — make reasonable decisions and document your reasoning. If something is ambiguous, pick the safer option and note it in your output files.

**If you finish all 5 phases and have time remaining, re-run the full test suite one final time and write `results/OVERNIGHT_SUMMARY.md` with everything you accomplished.**

## Rules (apply to ALL phases)

1. **Do NOT modify engine source code** (`engines/*/src/`) EXCEPT in Phase 1 where Task 5 explicitly allows test-only changes.
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT make any LLM API calls.** All phases are €0.
4. **Commit after EVERY phase** with descriptive messages. Use `git push` after each commit.
5. **If a phase fails or gets stuck**, document what happened in a `PHASE_X_BLOCKED.md` file, commit it, and move to the next phase. Do NOT spin on errors.
6. **Do NOT ask questions.** Make the best decision you can and document your reasoning.
7. **Run `/compact` between phases** if your context is getting large. This keeps you sharp for the full run.

---

## Phase 1: Test Fixture Expansion (Task 5)

**Time estimate: 1-2 hours**

Follow the pre-written Task 5 directive exactly. The full instructions are in `reference/archive/sessions/weekend/TASK_5_NEXT.md` — read that file, not this summary.

**Key steps:**
1. Select 10-15 edge cases from sweep results
2. Create fixtures in `tests/fixtures/shamela_edge_cases/` with companion .json
3. Write regression tests (non-tautological — check against independent ground truth)
4. Run full test suite, verify zero regressions
5. Commit: `harden: Add N edge-case fixtures + M regression tests from weekend sweep`

**Read first:** `reference/archive/sessions/weekend/TASK_5_NEXT.md` (the full directive)

---

## Phase 2: Cross-Engine Normalization Validation

**Time estimate: 1-2 hours**

Run the normalization pipeline on the 70 Phase E books to verify cross-engine compatibility. The source engine produced SourceMetadata for these books — now verify the normalization engine can process their raw HTML too.

### Step 2.1: Identify Phase E books on disk

```python
import json
from pathlib import Path

phase_e_manifest = json.loads(Path("tests/results/source_engine/phase_e/PHASE_E_MANIFEST.json").read_text())
phase_e_books = list(phase_e_manifest.get("books", {}).keys())
print(f"Phase E books: {len(phase_e_books)}")
```

### Step 2.2: Run normalization sweep on Phase E books only

Create a temporary directory with symlinks to Phase E books from `shamela-export-samples/`, then run the normalization sweep:

```bash
python scripts/normalization_corpus_sweep.py \
    --collection-dir shamela-export-samples \
    --output-dir results/cross_engine_validation \
    --book-list results/cross_engine_phase_e_books.txt \
    --resume
```

If `--book-list` is not a supported flag, write a small wrapper script (`scripts/run_normalization_subset.py`) that:
1. Reads a book list file (one name per line)
2. Creates a temp directory with symlinks to matching books in `shamela-export-samples/`
3. Runs the normalization sweep on that temp directory
4. Copies results to the output directory

### Step 2.3: Analyze cross-engine results

Write `results/CROSS_ENGINE_VALIDATION.md`:
- How many Phase E books normalize successfully?
- Do any crash? (These are books the source engine handled fine)
- For books where source engine said `is_multi_layer=true` (LLM inference), does normalization auto-detect multi-layer?
- Are there Phase E gate_abort books where normalization reveals content issues?
- Compare normalization content_unit counts with source engine page_count

### Step 2.4: Commit

```bash
git add results/cross_engine_validation/ results/CROSS_ENGINE_VALIDATION.md scripts/run_normalization_subset.py
git commit -m "validate: Cross-engine normalization on 70 Phase E books"
git push
```

---

## Phase 3: Source Engine Completion Report

**Time estimate: 1-2 hours**

Write a comprehensive report that an architect can use for the transition gate. This saves the architect hours of manual analysis.

### Step 3.1: Gather all data

Read and synthesize:
- `tests/results/source_engine/MASTER_MANIFEST.json` (274 books)
- `tests/results/source_engine/COST_LOG.json` (spending history)
- `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md`
- `tests/results/source_engine/phase_e/PHASE_E_LESSONS.md`
- `results/source_sweep/CC_ANALYSIS.md` (7,475-book deterministic sweep)
- `results/CALIBRATION_REPORT.md` (normalization calibration)
- `results/VERIFICATION_REPORT.md` (post-fix verification)
- `results/CROSS_ENGINE_FINDINGS.md`
- Phase E selection rationale and results

### Step 3.2: Write `results/SOURCE_ENGINE_COMPLETION_REPORT.md`

Structure:
1. **Executive Summary** — what the source engine does, current state, recommendation
2. **Validation Coverage**
   - Phase A: 7,475 deterministic (100% success)
   - Phase C: 73 LLM (100% after reruns)
   - Phase D: 204 LLM (100% success)
   - Phase E: 70 LLM (success/gate_abort/error breakdown)
   - Total: 274 books with full LLM metadata, 7,475 with deterministic extraction
3. **Quality Metrics**
   - Success rates across phases
   - Gate abort analysis (what triggers them, are they correct?)
   - Sanity check flag patterns
   - Consensus disagreement analysis
   - Field coverage (which metadata fields are populated at what rates)
4. **Genre Coverage**
   - Per-category book counts (Phase D + E combined)
   - Remaining blind spots
5. **Known Limitations**
   - Books that gate_abort (and why)
   - author_name_clean coverage gap (59.5%)
   - muhaqiq_name_clean coverage gap (4.6%)
   - Categories with <3 books
6. **Cost Summary**
   - Per-phase cost breakdown
   - Cost per book
   - Total lifetime spend
7. **Downstream Impact**
   - What the normalization engine receives
   - What the passaging engine needs to know
   - Remaining human gate queue
8. **Transition Gate Readiness Checklist**
   - [ ] All engine code passing tests
   - [ ] Full corpus deterministic sweep: pass rate, crash rate
   - [ ] LLM validation on diverse sample
   - [ ] Cross-engine compatibility validated
   - [ ] Edge case regression tests in place
   - [ ] Known limitations documented
   - [ ] SPEC errata documented

### Step 3.3: Commit

```bash
git add results/SOURCE_ENGINE_COMPLETION_REPORT.md
git commit -m "report: Source engine completion report for transition gate"
git push
```

---

## Phase 4: Normalization Engine Transition Preparation

**Time estimate: 1-2 hours**

Prepare data and analysis the architect needs for the normalization engine transition gate.

### Step 4.1: Write `results/NORMALIZATION_TRANSITION_DATA.md`

Synthesize all normalization data into one architect-ready document:

1. **Build Metrics** — test count, impl lines, ADV coverage, limitations L-001 through L-012
2. **Corpus Sweep Results** — from CALIBRATION_REPORT.md, but summarized with architect-relevant conclusions
3. **Evaluation Results** — from `engines/normalization/EVALUATION_REPORT.md`
4. **Bug Fix Impact** — Task 2 fixes, Task 3 verification, before/after numbers
5. **Passaging Contract Readiness**
   - What percentage of books pass all passaging input checks?
   - Which checks fail and why?
   - What does the passaging engine need to handle gracefully?
6. **Edge Cases Discovered** — from sweep, now with test fixtures
7. **SPEC Errata** — SPEC-NOTE-1, SPEC-NOTE-2, SPEC-NOTE-3 (from evaluation)
8. **Open Questions for Architect**
   - Should SPEC diacritics range include extended marks? (SWEEP_ARCHITECT_REVIEW.md)
   - Should pageless books get a quality flag?
   - Division overlap handling strategy for passaging

### Step 4.2: Run full normalization test suite and capture output

```bash
python -m pytest engines/normalization/tests/ -v --tb=short > results/normalization_test_output.txt 2>&1
echo "Exit code: $?" >> results/normalization_test_output.txt
```

Count: total tests, passed, failed, skipped, warnings.

### Step 4.3: Commit

```bash
git add results/NORMALIZATION_TRANSITION_DATA.md results/normalization_test_output.txt
git commit -m "report: Normalization transition data for architect review"
git push
```

---

## Phase 5: Test Coverage Analysis + Gap Filling

**Time estimate: 2-3 hours**

### Step 5.1: Analyze test coverage gaps

For both engines, identify what's tested and what isn't:

```bash
# Normalization engine
python -m pytest engines/normalization/tests/ --co -q > results/normalization_test_inventory.txt 2>&1

# Source engine
python -m pytest engines/source/tests/ --co -q > results/source_test_inventory.txt 2>&1
```

Read both inventories. Identify:
- Functions/modules with zero test coverage
- Edge cases from sweeps that don't have regression tests yet
- Contract boundary tests (do normalized outputs conform to passaging input requirements?)
- Error path coverage (do error codes get raised correctly?)

### Step 5.2: Write gap-filling tests

Write additional tests targeting identified gaps. Focus on:
1. **Contract boundary tests** — verify normalization output matches passaging input contracts
2. **Error path tests** — verify specific error codes are raised for known bad inputs
3. **Edge case regression** — any sweep findings not already covered by Phase 1 fixtures
4. **Anti-tautological** — every assertion checks against independent ground truth

Place new tests in appropriate test files. Use existing conftest helpers.

### Step 5.3: Run full test suite (both engines)

```bash
python -m pytest engines/normalization/tests/ engines/source/tests/ -v --tb=short
```

Zero regressions. Document final test count.

### Step 5.4: Commit

```bash
git add engines/normalization/tests/ engines/source/tests/ results/normalization_test_inventory.txt results/source_test_inventory.txt
git commit -m "harden: Test coverage gap analysis + N new tests"
git push
```

---

## When All Phases Complete

Write `results/OVERNIGHT_SUMMARY.md`:

```markdown
# Overnight Work Summary

**Date:** [date]
**Duration:** [start time] to [end time]
**Phases completed:** [list]

## Per-Phase Results
[summary of each phase — commits, key metrics, any issues]

## Test Count
- Before: [count from start of overnight]
- After: [final count]
- New tests added: [delta]

## Files Modified
[list of all files added/modified across all phases]

## Issues for Architect
[anything that needs architect attention, ordered by priority]

## Commits
[list of all commits made overnight, with hashes]
```

```bash
git add results/OVERNIGHT_SUMMARY.md
git commit -m "report: Overnight work summary — N phases completed"
git push
```

---

## Read First

1. This file (NEXT.md)
2. `reference/archive/sessions/weekend/TASK_5_NEXT.md` — Phase 1 full instructions
3. `results/CALIBRATION_REPORT.md` — normalization calibration data
4. `engines/normalization/tests/conftest.py` — test helper patterns
5. `tests/results/source_engine/phase_e/PHASE_E_LESSONS.md` — latest findings
6. `results/CROSS_ENGINE_FINDINGS.md` — cross-engine analysis

## Do NOT Do

1. **Do NOT modify engine source code** (except adding tests in Phase 1/5).
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT make LLM API calls.** All phases are €0.
4. **Do NOT ask questions.** Decide and document.
5. **Do NOT spend more than 3 hours on any single phase.** If stuck, write PHASE_X_BLOCKED.md and move on.
6. **Do NOT skip committing and pushing between phases.** Progress must be saved.
