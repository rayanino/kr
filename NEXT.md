# NEXT — Overnight Autonomous Work Program (8+ hours)

## Mode

**FULLY AUTONOMOUS — owner is asleep, architect is unavailable.**

You will work through 5 phases sequentially. Commit and push after each phase. Do NOT ask questions — make reasonable decisions and document your reasoning. If something is ambiguous, pick the safer option and note it in your output files.

**Run `/compact` between every phase to keep your context fresh.**

**If you finish all 5 phases and have time remaining, re-run the full test suite one final time and write `results/OVERNIGHT_SUMMARY.md` with everything you accomplished.**

## Rules (apply to ALL phases)

1. **Do NOT modify engine source code** (`engines/*/src/`) EXCEPT in Phases 1 and 5 where test files may be added.
2. **Do NOT modify SPECs or contracts.**
3. **You MAY make LLM API calls in Phase 2.** Budget is unlimited — quality matters, not cost. Track spend in COST_LOG.json.
4. **Commit and `git push` after EVERY phase.** Progress must be saved incrementally.
5. **If a phase fails or gets stuck for >30 minutes**, document what happened in a `results/PHASE_X_BLOCKED.md` file, commit it, and move to the next phase. Do NOT spin on errors.
6. **Do NOT ask questions.** Make the best decision you can and document your reasoning.
7. **Run `/compact` between phases** to keep context fresh for the full run.
8. **3-hour hard cap per phase.** If a phase is not done in 3 hours, wrap up what you have, commit, and move on.

---

## Phase 1: Test Fixture Expansion (Task 5) — €0

**Time estimate: 1-2 hours**

Follow the pre-written Task 5 directive exactly. The full instructions are in `reference/archive/sessions/weekend/TASK_5_NEXT.md` — read that file, not this summary.

**Key steps:**
1. Select 10-15 edge cases from sweep results
2. Create fixtures in `tests/fixtures/shamela_edge_cases/` with companion .json
3. Write regression tests (non-tautological — check against independent ground truth)
4. Run full test suite, verify zero regressions
5. Commit and push: `harden: Add N edge-case fixtures + M regression tests from weekend sweep`

**Read first:** `reference/archive/sessions/weekend/TASK_5_NEXT.md`

**After completing Phase 1, run `/compact` before starting Phase 2.**

---

## Phase 2: Extended LLM Probes — Fill Remaining Genre Gaps — ~€5-15

**Time estimate: 2-3 hours (includes ~30 min pipeline run)**

Phase D+E covered 274 books across 24 Shamela categories — but 13 categories still have ≤2 books. Run more LLM probes to fill the remaining gaps.

### Step 2.1: Identify remaining thin categories

```python
import json
from pathlib import Path

# Load MASTER_MANIFEST (274 books after Phase E)
master = json.loads(Path("tests/results/source_engine/MASTER_MANIFEST.json").read_text())
existing_books = set(master.get("books", {}).keys())

# Load Phase D category distribution (maps book names to Shamela categories)
cat_dist = json.loads(Path("tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json").read_text())

# Count per-category coverage in existing 274 books
category_coverage = {}
for cat_name, cat_info in cat_dist["categories"].items():
    covered = [b for b in cat_info["books"] if b in existing_books]
    category_coverage[cat_name] = {
        "total_in_corpus": cat_info["count"],
        "covered": len(covered),
        "gap": max(0, 5 - len(covered))  # Target: 5 per category
    }

# Print thin categories (< 5 covered books)
thin = {k: v for k, v in category_coverage.items() if v["covered"] < 5}
print(f"Thin categories (< 5 books): {len(thin)}")
for cat, info in sorted(thin.items(), key=lambda x: x[1]["covered"]):
    print(f"  {info['covered']}/{info['total_in_corpus']}  {cat}  (need {info['gap']} more)")
```

### Step 2.2: Select books to fill gaps

For each thin category, pick books that:
1. Are NOT in MASTER_MANIFEST.json (not already processed)
2. Are NOT duplicates (check source sweep duplicate report)
3. Prefer books with `author_name_raw` present (more metadata = better LLM inference)
4. Prefer medium-sized books (50-300 pages) — not too small, not too large

Target: 5 books per category minimum. Total selection: ~30-50 books depending on how many categories are thin.

Write selection to `tests/results/source_engine/phase_f/PHASE_F_SELECTION.md` with per-book rationale.
Write book list to `tests/results/source_engine/phase_f/books.txt`.

### Step 2.3: Back up COST_LOG.json (CRITICAL)

Same issue as Phase E — `run_phase_c.py` overwrites `phases["C"]`.

```python
import json, shutil
from pathlib import Path

cost_log_path = Path("tests/results/source_engine/COST_LOG.json")
backup_path = Path("tests/results/source_engine/COST_LOG_BACKUP_PRE_PHASE_F.json")
shutil.copy2(cost_log_path, backup_path)

# Verify
original = json.loads(cost_log_path.read_text())
backup = json.loads(backup_path.read_text())
assert original == backup
assert original["phases"]["C"]["books"] == 73
print(f"Backup verified. Current total: {original['total_eur']} EUR")
```

### Step 2.4: Run the pipeline

```bash
python scripts/phases/run_phase_c.py shamela-export-samples \
    --books tests/results/source_engine/phase_f/books.txt \
    --output-dir tests/results/source_engine/phase_f \
    --budget-eur 200 \
    --resume
```

### Step 2.5: Post-processing (same pattern as Phase E Step 6)

**6a. Rename manifests:** `PHASE_C_MANIFEST.json` → `PHASE_F_MANIFEST.json`, fix phase identifiers and result_path prefixes.

**6b. Restore COST_LOG.json:** Extract Phase F data from `phases["C"]`, restore real Phase C from backup, write Phase F data to `phases["F"]`, recalculate total.

**6c. Update MASTER_MANIFEST.json:** Merge Phase F books with `"phase": "F"` tag.

### Step 2.6: Write PHASE_F_LESSONS.md

Focus on:
- Which categories are now adequately covered (≥5 books)?
- Which remain thin? (Document for architect)
- Any new gate_abort patterns on underrepresented genres?
- Cost summary

### Step 2.7: Commit and push

```bash
du -sh tests/results/source_engine/phase_f/
git add -f tests/results/source_engine/phase_f/
git add -f tests/results/source_engine/MASTER_MANIFEST.json
git add -f tests/results/source_engine/COST_LOG.json
git commit -m "validate: Phase F — ~N genre-gap LLM probes (€X.XX spent), M categories now ≥5 books"
git push
```

**After completing Phase 2, run `/compact` before starting Phase 3.**

---

## Phase 3: Cross-Engine Normalization Validation — €0

**Time estimate: 1-2 hours**

Run the normalization pipeline on the Phase E+F books to verify cross-engine compatibility.

### Step 3.1: Gather all LLM-probed books not yet normalization-tested

Combine Phase E + Phase F book lists. These books have source engine SourceMetadata but have NOT been individually normalization-tested (the corpus sweep used `is_multi_layer=False` for all books; now we have real LLM metadata).

### Step 3.2: Run normalization sweep on these books

If `normalization_corpus_sweep.py` supports `--book-list`, use it. Otherwise write a small wrapper that creates a temp directory with symlinks to the selected books from `shamela-export-samples/`, then runs the sweep on that directory.

Output to `results/cross_engine_validation/`.

### Step 3.3: Analyze cross-engine results

Write `results/CROSS_ENGINE_VALIDATION.md`:
- How many books normalize successfully?
- Do any crash? (These are books the source engine handled fine)
- For books where source engine said `is_multi_layer=true`, does normalization agree?
- Content unit counts vs source engine page counts — any major discrepancies?

### Step 3.4: Commit and push

```bash
git add results/cross_engine_validation/ results/CROSS_ENGINE_VALIDATION.md
git commit -m "validate: Cross-engine normalization on Phase E+F books"
git push
```

**After completing Phase 3, run `/compact` before starting Phase 4.**

---

## Phase 4: Completion Reports — €0

**Time estimate: 1-2 hours**

Write two comprehensive reports the architect needs for transition gates.

### Step 4.1: Source Engine Completion Report

Write `results/SOURCE_ENGINE_COMPLETION_REPORT.md`:

1. **Executive Summary** — what the source engine does, current state, recommendation
2. **Validation Coverage** — Phase A (7,475 deterministic), C (73 LLM), D (204 LLM), E (70 LLM), F (N LLM). Total books with full metadata.
3. **Quality Metrics** — success rates, gate abort analysis, sanity check flags, consensus disagreements, field coverage rates
4. **Genre Coverage** — per-category counts (all phases combined), remaining blind spots
5. **Known Limitations** — gate abort triggers, author_name_clean gap (59.5%), muhaqiq gap (4.6%), thin categories
6. **Cost Summary** — per-phase breakdown, cost per book, total lifetime spend
7. **Downstream Impact** — what normalization receives, what passaging needs
8. **Transition Gate Readiness Checklist** — all criteria with evidence

### Step 4.2: Normalization Transition Data

Write `results/NORMALIZATION_TRANSITION_DATA.md`:

1. **Build Metrics** — test count, impl lines, ADV coverage, L-001 to L-012
2. **Corpus Sweep Results** — calibration summary with architect-relevant conclusions
3. **Bug Fix Impact** — Task 2 fixes, Task 3 verification, before/after
4. **Passaging Contract Readiness** — pass rates per check, what passaging must handle
5. **Edge Cases** — discovered in sweep, now with test fixtures
6. **SPEC Errata** — SPEC-NOTE-1, 2, 3
7. **Open Questions** — diacritics range, pageless quality flag, division overlap strategy

### Step 4.3: Run and capture test suite output

```bash
python -m pytest engines/normalization/tests/ -v --tb=short > results/normalization_test_output.txt 2>&1
python -m pytest engines/source/tests/ -v --tb=short > results/source_test_output.txt 2>&1
```

### Step 4.4: Commit and push

```bash
git add results/SOURCE_ENGINE_COMPLETION_REPORT.md results/NORMALIZATION_TRANSITION_DATA.md results/normalization_test_output.txt results/source_test_output.txt
git commit -m "report: Source engine completion report + normalization transition data"
git push
```

**After completing Phase 4, run `/compact` before starting Phase 5.**

---

## Phase 5: Test Coverage Analysis + Gap Filling — €0

**Time estimate: 2-3 hours**

### Step 5.1: Inventory all tests

```bash
python -m pytest engines/normalization/tests/ --co -q > results/normalization_test_inventory.txt 2>&1
python -m pytest engines/source/tests/ --co -q > results/source_test_inventory.txt 2>&1
```

### Step 5.2: Identify gaps

Read both inventories. Identify:
- Functions/modules with zero test coverage
- Edge cases from sweeps without regression tests
- Contract boundary tests (normalized output → passaging input)
- Error path coverage

### Step 5.3: Write gap-filling tests

Focus on:
1. Contract boundary tests
2. Error path tests
3. Edge case regression (anything not covered by Phase 1 fixtures)
4. Anti-tautological assertions only (independent ground truth)

### Step 5.4: Run full test suite

```bash
python -m pytest engines/normalization/tests/ engines/source/tests/ -v --tb=short
```

Record before/after test count. Zero regressions.

### Step 5.5: Commit and push

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
**Phases completed:** [list with status]

## Per-Phase Results
[summary of each phase — commits, key metrics, issues]

## Test Count
- Before overnight: [count]
- After overnight: [final count]
- New tests added: [delta]

## Ground Truth Growth
- Before overnight: 274 books in MASTER_MANIFEST
- After overnight: [new count]
- New books added: [delta]
- Cost of overnight LLM probes: €[amount]

## Category Coverage
[which categories reached ≥5 books, which remain thin]

## Issues for Architect
[anything needing architect attention, ordered by priority]

## Commits
[list of all commits, with hashes and descriptions]
```

```bash
git add results/OVERNIGHT_SUMMARY.md
git commit -m "report: Overnight work summary — N phases completed"
git push
```
