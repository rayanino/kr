# NEXT — Overnight Autonomous Work Program (8+ hours)

## Mode

**FULLY AUTONOMOUS — owner is asleep, architect is unavailable.**

Work through 4 phases sequentially. Commit and push after each phase. Do NOT ask questions — make reasonable decisions and document your reasoning.

**Run `/compact` between every phase.**

**API Configuration:** All LLM calls route through OpenRouter. The `OPENROUTER_API_KEY` environment variable should already be set. Both models in the consensus pipeline use OpenRouter:
- Model A: `openrouter/cohere/command-a`
- Model B: `openrouter/anthropic/claude-opus-4-6`
- Fallback: `openrouter/openai/gpt-5.4`

Verify: `python -c "import os; print(bool(os.environ.get('OPENROUTER_API_KEY')))"`

If not set, the key is: `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`

## Rules (apply to ALL phases)

1. **Do NOT modify engine source code** (`engines/*/src/`, `shared/*/src/`) — already updated to route all models through OpenRouter.
2. **Do NOT modify SPECs or contracts.**
3. **You MAY make LLM API calls.** Budget: $85 maximum on OpenRouter (leave $10 safety margin from the $95 balance). Track spend in COST_LOG.json. The script's `--budget-eur` flag tracks EUR; use `--budget-eur 100` for ample headroom.
4. **Commit and `git push` after EVERY phase.** Progress must be saved incrementally.
5. **If a phase gets stuck for >30 minutes**, document in `results/PHASE_X_BLOCKED.md`, commit, move on.
6. **Do NOT ask questions.** Decide and document.
7. **Run `/compact` between phases.**
8. **3-hour hard cap per phase.** Wrap up, commit, move on.

---

## Phase 1: Test Fixture Expansion — €0

**Time estimate: 1-2 hours**

Follow `reference/archive/sessions/weekend/TASK_5_NEXT.md` exactly.

**Key steps:**
1. Select 10-15 edge cases from sweep results
2. Create fixtures in `tests/fixtures/shamela_edge_cases/` with companion .json
3. Write regression tests (non-tautological)
4. Run full test suite, zero regressions
5. Commit and push: `harden: Add N edge-case fixtures + M regression tests from weekend sweep`

**After completing, run `/compact`.**

---

## Phase 2: Mass LLM Ground Truth Expansion — ~$50-70

**Time estimate: 3-4 hours (pipeline runtime ~2h for 500 books)**

This is the highest-value phase. Process ~500 books through the full LLM pipeline, bringing total ground truth from 274 to ~774 books (10% of the corpus).

### Step 2.1: Plan the selection (~500 books)

**Tier 1 — Fill thin categories to ≥5 books (~50-80 books)**

Load `tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json`. For every Shamela category with <5 books in `MASTER_MANIFEST.json`, select enough books to reach 5. Prefer books with `author_name_raw` present (richer metadata for LLM).

**Tier 2 — Stratified random sample of remaining corpus (~420-450 books)**

From the remaining ~7,000 un-processed books, select a stratified random sample:
- For each Shamela category, select proportionally to its corpus share
- Within each category, pick randomly (use a fixed seed: `random.seed(42)`)
- Skip books already in MASTER_MANIFEST.json
- Skip the 1 book that crashed in the normalization sweep (مواقف النبي)

The goal: after this phase, every Shamela category has ≥5 books with full LLM metadata AND we have broad coverage across the corpus.

### Step 2.2: Filter against existing results

```python
import json
master = json.loads(open("tests/results/source_engine/MASTER_MANIFEST.json").read())
existing = set(master.get("books", {}).keys())
selected = [b for b in all_selected if b not in existing]
```

Write selection to `tests/results/source_engine/phase_f/PHASE_F_SELECTION.md` with tier breakdown.
Write book list to `tests/results/source_engine/phase_f/books.txt`.

### Step 2.3: Back up COST_LOG.json (CRITICAL)

```python
import shutil
shutil.copy2(
    "tests/results/source_engine/COST_LOG.json",
    "tests/results/source_engine/COST_LOG_BACKUP_PRE_PHASE_F.json"
)
```

### Step 2.4: Run the pipeline

```bash
python scripts/phases/run_phase_c.py shamela-export-samples \
    --books tests/results/source_engine/phase_f/books.txt \
    --output-dir tests/results/source_engine/phase_f \
    --budget-eur 100 \
    --resume
```

Use `--resume` — if interrupted, restart and it picks up where it left off.

**Monitor:** The script prints per-book status and running cost. If cost exceeds $70, let the current book finish, then stop (Ctrl+C is safe with --resume).

### Step 2.5: Post-processing (same as Phase E)

**a. Rename manifests:** `PHASE_C_MANIFEST.json` → `PHASE_F_MANIFEST.json`, fix `"phase"` to `"F"`, fix `result_path` prefixes from `phase_c/` to `phase_f/`. Rename `PHASE_C_SUMMARY.json` → `PHASE_F_SUMMARY.json`.

**b. Restore COST_LOG.json:** The script overwrote `phases["C"]` with Phase F data. Extract it, restore real Phase C from backup, write Phase F data to `phases["F"]`, recalculate total.

**c. Update MASTER_MANIFEST.json:** Merge Phase F books with `"phase": "F"` tag. Print final count.

### Step 2.6: Write PHASE_F_LESSONS.md

- Results summary (success/gate_abort/error)
- Category coverage: which categories now have ≥5 books?
- New patterns not seen in Phase D/E
- Cost summary
- Any books that failed and why

### Step 2.7: Commit and push

```bash
du -sh tests/results/source_engine/phase_f/

# If under 50MB total
git add -f tests/results/source_engine/phase_f/
git add -f tests/results/source_engine/MASTER_MANIFEST.json
git add -f tests/results/source_engine/COST_LOG.json
git commit -m "validate: Phase F — N books processed (€X.XX), total ground truth now M books"
git push

# If over 50MB, commit only summaries/manifests/lessons
git add -f tests/results/source_engine/phase_f/PHASE_F_*.md
git add -f tests/results/source_engine/phase_f/PHASE_F_*.json
git add -f tests/results/source_engine/MASTER_MANIFEST.json
git add -f tests/results/source_engine/COST_LOG.json
git commit -m "validate: Phase F summaries — N books (€X.XX), raw responses local"
git push
```

**After completing, run `/compact`.**

---

## Phase 3: Completion Reports — €0

**Time estimate: 1-2 hours**

### Step 3.1: Source Engine Completion Report

Write `results/SOURCE_ENGINE_COMPLETION_REPORT.md`:

1. **Executive Summary** — engine status, total books processed, recommendation
2. **Validation Coverage** — Phase A (7,475), C (73), D (204), E (70), F (N). Total with full LLM metadata.
3. **Quality Metrics** — success rates, gate abort analysis, sanity flags, consensus disagreements, field coverage
4. **Genre Coverage** — per-category counts (all phases), remaining blind spots
5. **Known Limitations** — gate aborts, name parsing gaps, thin categories
6. **Cost Summary** — per-phase breakdown, total lifetime spend
7. **Downstream Impact** — what normalization/passaging receives
8. **Transition Gate Readiness Checklist**

### Step 3.2: Normalization Transition Data

Write `results/NORMALIZATION_TRANSITION_DATA.md`:

1. Build Metrics — 420+ tests, L-001 to L-012
2. Corpus Sweep Results — 7,475 books, 99.987% → 100% after fixes
3. Bug Fix Impact — Task 2/3 before/after
4. Passaging Contract Readiness — check pass rates
5. Edge Cases — fixtures from Phase 1
6. SPEC Errata — SPEC-NOTE-1, 2, 3
7. Open Questions for Architect

### Step 3.3: Capture test suite output

```bash
python -m pytest engines/normalization/tests/ -v --tb=short > results/normalization_test_output.txt 2>&1
python -m pytest engines/source/tests/ -v --tb=short > results/source_test_output.txt 2>&1
```

### Step 3.4: Commit and push

```bash
git add results/SOURCE_ENGINE_COMPLETION_REPORT.md results/NORMALIZATION_TRANSITION_DATA.md results/*.txt
git commit -m "report: Source engine completion + normalization transition data"
git push
```

**After completing, run `/compact`.**

---

## Phase 4: Test Coverage Gap Filling — €0

**Time estimate: 2-3 hours**

### Step 4.1: Inventory all tests

```bash
python -m pytest engines/normalization/tests/ --co -q > results/normalization_test_inventory.txt 2>&1
python -m pytest engines/source/tests/ --co -q > results/source_test_inventory.txt 2>&1
```

### Step 4.2: Identify and fill gaps

Focus on: contract boundary tests, error path tests, edge case regression, anti-tautological assertions.

### Step 4.3: Run full test suite

Zero regressions. Document before/after count.

### Step 4.4: Commit and push

```bash
git add engines/normalization/tests/ engines/source/tests/ results/*test_inventory*
git commit -m "harden: Test coverage gap analysis + N new tests"
git push
```

---

## When All Phases Complete

Write `results/OVERNIGHT_SUMMARY.md`:

- Phases completed with status
- Ground truth growth (274 → ?)
- Total cost overnight
- Category coverage final state
- Test count before/after
- All commits with hashes
- Issues for architect

```bash
git add results/OVERNIGHT_SUMMARY.md
git commit -m "report: Overnight summary — N phases, M new books, K new tests"
git push
```

## Read First

1. This file (NEXT.md)
2. `reference/archive/sessions/weekend/TASK_5_NEXT.md` — Phase 1 full instructions
3. `RESULT_PRESERVATION.md` — preservation protocol
4. `scripts/phases/run_phase_c.py` — the pipeline script
5. `tests/results/source_engine/MASTER_MANIFEST.json` — existing books
6. `tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json` — category data
7. `results/CALIBRATION_REPORT.md` — normalization calibration

## Do NOT Do

1. **Do NOT modify engine source code or shared modules.**
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT spend more than $85 on OpenRouter.** Leave $10 safety margin.
4. **Do NOT re-process books already in MASTER_MANIFEST.json.**
5. **Do NOT skip the COST_LOG.json backup before running the pipeline.**
6. **Do NOT ask questions.**
7. **Do NOT skip committing and pushing between phases.**
