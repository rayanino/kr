# NEXT — Overnight Autonomous Work Program (8+ hours, €0)

## CRITICAL CONTEXT — READ THIS FIRST

You are running unattended for 8+ hours overnight. The owner is asleep. The architect is unavailable. **No one can help you, unstick you, or answer questions until morning.**

This means:
- **If you get stuck, the entire night is wasted.** There is no retry. Every hour you spend stuck on one problem is an hour of productive work lost forever.
- **If you ask a question, no one will answer.** You will sit idle until morning. That is the worst possible outcome.
- **If you hit an error, you must route around it.** Document it, commit what you have, and move to the next phase. A completed Phase 3 with a blocked Phase 2 is infinitely better than being stuck on Phase 2 all night.
- **The 30-minute stuck rule is absolute.** If something isn't working after 30 minutes of trying: stop. Write `results/PHASE_X_BLOCKED.md` explaining what happened. Commit. Move on. The architect will handle it tomorrow with fresh context.
- **Commit and push constantly.** Every piece of work pushed is saved. Work that exists only in your context is lost if anything goes wrong.
- **Run `/compact` between phases.** Your context will degrade over 8 hours. Fresh context per phase keeps quality high.

Your goal: wake up the owner to find 5 phases of committed, pushed, high-quality work in the repo. Partial completion of all 5 phases beats perfect completion of 2 phases.

## Mode

**FULLY AUTONOMOUS — owner is asleep, architect is unavailable.**

Work through 5 phases sequentially. Commit and push after each phase. Do NOT ask questions — make reasonable decisions and document your reasoning.

**Run `/compact` between every phase.**

**Budget: €0. No LLM API calls in any phase.** All work is deterministic analysis, test writing, and report generation.

## Rules (apply to ALL phases)

1. **Do NOT modify engine source code** (`engines/*/src/`, `shared/*/src/`).
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT make any LLM API calls.** All phases are €0.
4. **Commit and `git push` after EVERY phase.**
5. **If a phase gets stuck for >30 minutes**, document in `results/PHASE_X_BLOCKED.md`, commit, move on.
6. **Do NOT ask questions.** Decide and document.
7. **Run `/compact` between phases.**
8. **3-hour hard cap per phase.**

---

## Phase 0: Baseline Smoke Test (5 minutes)

Before starting any work, verify the test suite passes and record the baseline:

```bash
python -m pytest engines/normalization/tests/ -x -q 2>&1 | tail -3
python -m pytest engines/source/tests/ -x -q 2>&1 | tail -3
```

Write down the test counts (e.g., "439 passed, 14 skipped" for normalization, "503 passed" for source). You will need these for before/after comparison in later phases.

**If tests are already failing:** Do NOT try to fix them. Document the failures in `results/BASELINE_FAILURES.md`, commit, push, and proceed with the phases. The architect will handle pre-existing failures.

```bash
# Only if there are failures:
git add results/BASELINE_FAILURES.md
git commit -m "report: Baseline test failures found before overnight work"
git push
```

---

## Phase 1: Test Fixture Expansion

**Time estimate: 1-2 hours**

Follow `reference/archive/sessions/weekend/TASK_5_NEXT.md` for Steps 1-5 (selection, fixture creation, test writing, tautology check, test suite run).

**Override Task 5's Step 6 (commit) with this:**
```bash
git add tests/fixtures/shamela_edge_cases/
git add engines/normalization/tests/
git add engines/source/tests/
git commit -m "harden: Add N edge-case fixtures + M regression tests from weekend sweep"
git push
```
**The `git push` is critical. Do NOT skip it. If you crash later, pushed work is safe.**

**Read first:** `reference/archive/sessions/weekend/TASK_5_NEXT.md`

**After completing, run `/compact`.**

---

## Phase 2: Cross-Engine Normalization Validation on Phase E Books

**Time estimate: 1-2 hours**

The source engine produced LLM metadata for 70 Phase E books. Run these books through the normalization pipeline to verify cross-engine compatibility.

### Step 2.1: Identify Phase E books

```python
import json
from pathlib import Path
phase_e = json.loads(Path("tests/results/source_engine/phase_e/PHASE_E_MANIFEST.json").read_text())
books = list(phase_e.get("books", {}).keys())
print(f"Phase E books: {len(books)}")
```

### Step 2.2: Write a book list file and run normalization sweep

Write the Phase E book names to a file (one per line):

```python
import json
from pathlib import Path

phase_e = json.loads(Path("tests/results/source_engine/phase_e/PHASE_E_MANIFEST.json").read_text())
books = list(phase_e.get("books", {}).keys())

book_list_path = Path("results/cross_engine_validation/phase_e_books.txt")
book_list_path.parent.mkdir(parents=True, exist_ok=True)
book_list_path.write_text("\n".join(books), encoding="utf-8")
print(f"Wrote {len(books)} book names to {book_list_path}")
```

Then run the sweep with `--book-list`:

```bash
python scripts/normalization_corpus_sweep.py \
    --collection-dir shamela-export-samples \
    --output-dir results/cross_engine_validation \
    --book-list results/cross_engine_validation/phase_e_books.txt \
    --resume
```

The `--book-list` flag filters the discovered books to only those in the file. It handles `.htm` extension mismatches automatically.

Output goes to `results/cross_engine_validation/`.

### Step 2.3: Analyze and write `results/CROSS_ENGINE_VALIDATION.md`

- How many Phase E books normalize successfully?
- Any crashes? (books the source engine handled fine but normalization can't)
- For books where source engine LLM said `is_multi_layer=true`: does normalization auto-detect multi-layer?
- Content unit counts vs source engine page counts — discrepancies?
- For the 16 Phase E gate_abort books: do they normalize differently?

### Step 2.4: Commit and push

```bash
git add results/cross_engine_validation/
git add results/CROSS_ENGINE_VALIDATION.md
git commit -m "validate: Cross-engine normalization on 70 Phase E books"
git push
```

**After completing, run `/compact`.**

---

## Phase 3: Deep Analysis of All 274 LLM-Probed Books

**Time estimate: 2-3 hours**

Produce analysis the architect needs for the source engine transition gate. This is NOT a summary — it's original analysis computing new metrics from per-book result files.

**CRITICAL: Write Python aggregation scripts. Do NOT read files one by one with your file tool.** There are 347 books across 3 phases (C/D/E), each with 3-5 JSON files. That's 1,000+ files. Reading them individually will fill your context and stall you. Write a script, run it, read the output.

### Step 3.1: Gate Abort Deep Dive

Write `scripts/analyze_gate_aborts.py` that:
1. Walks `tests/results/source_engine/phase_c/`, `phase_d/`, `phase_e/`
2. For each book dir, reads `result.json`
3. Filters for `status == "gate_abort"`
4. Extracts: book name, phase, `error_code`, `gate_errors` list, and checks if `extraction.json` has `author_name_raw`
5. Groups by gate error reason
6. Outputs a markdown report to `results/GATE_ABORT_ANALYSIS.md`

Run it: `python scripts/analyze_gate_aborts.py`

The report should include per-group analysis: is the gate correct? Which books are candidates for threshold adjustment?

### Step 3.2: Consensus Disagreement Analysis

Write `scripts/analyze_consensus.py` that:
1. Walks all 3 phase directories
2. Reads each `consensus.json` — checks `agreed` field
3. For books where `agreed == false`: reads both files in `llm_responses/`, extracts `parsed` dict from each
4. Compares fields: `genre`, `is_multi_layer`, `author_identification.canonical_name_ar`, `structural_format`, `science_scope`
5. Tallies which fields disagree most
6. Outputs `results/CONSENSUS_ANALYSIS.md`

Run it: `python scripts/analyze_consensus.py`

Data point: there are 27 disagreements across all phases (6 in C, 14 in D, 7 in E). The script only needs to deep-read LLM responses for those 27 books.

### Step 3.3: Field Coverage and Quality Matrix

Write `scripts/analyze_field_coverage.py` that:
1. Walks all 3 phase directories
2. For each book: reads `extraction.json` (deterministic fields) and `result.json` (LLM-inferred fields)
3. For each metadata field: counts how many books have it from extraction vs from final result
4. Computes extraction→inference improvement rates
5. Outputs `results/FIELD_QUALITY_MATRIX.md` with per-field coverage table

Run it: `python scripts/analyze_field_coverage.py`

### Step 3.4: Commit and push

```bash
git add scripts/analyze_gate_aborts.py scripts/analyze_consensus.py scripts/analyze_field_coverage.py
git add results/GATE_ABORT_ANALYSIS.md results/CONSENSUS_ANALYSIS.md results/FIELD_QUALITY_MATRIX.md
git commit -m "analysis: Deep dive on 274 LLM-probed books — gate aborts, consensus, field quality"
git push
```

**After completing, run `/compact`.**

---

## Phase 4: Completion Reports and Transition Preparation

**Time estimate: 1-2 hours**

**Note:** If Phase 3 was blocked, write these reports using raw data files directly (MASTER_MANIFEST, COST_LOG, CALIBRATION_REPORT, VERIFICATION_REPORT, EVALUATION_REPORT). Do not block on missing Phase 3 outputs — produce what you can.

### Step 4.1: Source Engine Completion Report

Write `results/SOURCE_ENGINE_COMPLETION_REPORT.md`:

Data sources: `tests/results/source_engine/MASTER_MANIFEST.json`, `tests/results/source_engine/COST_LOG.json`, `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md`, `tests/results/source_engine/phase_e/PHASE_E_LESSONS.md`, `results/source_sweep/CC_ANALYSIS.md`, and Phase 3 outputs if they exist.

1. **Executive Summary**
2. **Validation Coverage** — Phase A (7,475 deterministic), C (73), D (204), E (70). Total.
3. **Quality Metrics** — success rates, gate abort analysis (from Phase 3 if available, or compute from manifests), field coverage
4. **Genre Coverage** — per-category counts, remaining blind spots
5. **Known Limitations** — gate aborts, name parsing gaps, thin categories
6. **Cost Summary** — per-phase breakdown from COST_LOG.json, total lifetime spend
7. **Downstream Impact** — what normalization/passaging receives
8. **Transition Gate Readiness Checklist** — evidence-backed

### Step 4.2: Normalization Transition Data

Write `results/NORMALIZATION_TRANSITION_DATA.md`:

Data sources: `engines/normalization/KNOWN_LIMITATIONS.md` (L-001 to L-012), `reference/SPEC_ERRATA.md` (SPEC-NOTE-1 to 3), `results/CALIBRATION_REPORT.md`, `results/VERIFICATION_REPORT.md`, `engines/normalization/EVALUATION_REPORT.md`.

1. Build Metrics — test count (from pytest), limitations from `engines/normalization/KNOWN_LIMITATIONS.md`
2. Corpus Sweep — 7,475 books calibration summary from `results/CALIBRATION_REPORT.md`
3. Bug Fix Impact — Task 2/3 before/after from `results/VERIFICATION_REPORT.md`
4. Passaging Contract Readiness — check pass rates from `results/CALIBRATION_REPORT.md` section B.8
5. Edge Cases — fixtures from Phase 1 (list what was added)
6. SPEC Errata — from `reference/SPEC_ERRATA.md`
7. Open Questions for architect

### Step 4.3: Capture test suite output

```bash
python -m pytest engines/normalization/tests/ -v --tb=short > results/normalization_test_output.txt 2>&1
python -m pytest engines/source/tests/ -v --tb=short > results/source_test_output.txt 2>&1
```

### Step 4.4: Commit and push

```bash
git add results/SOURCE_ENGINE_COMPLETION_REPORT.md results/NORMALIZATION_TRANSITION_DATA.md results/*test_output*
git commit -m "report: Source engine completion + normalization transition data"
git push
```

**After completing, run `/compact`.**

---

## Phase 5: Test Coverage Gap Filling

**Time estimate: 2-3 hours**

### Step 5.1: Inventory all tests

```bash
python -m pytest engines/normalization/tests/ --co -q > results/normalization_test_inventory.txt 2>&1
python -m pytest engines/source/tests/ --co -q > results/source_test_inventory.txt 2>&1
```

### Step 5.2: Identify and fill gaps

Focus on: contract boundary tests, error path tests, edge case regression, anti-tautological assertions.

### Step 5.3: Run full test suite — zero regressions

Document before/after count.

### Step 5.4: Commit and push

```bash
git add engines/normalization/tests/ engines/source/tests/ results/*test_inventory*
git commit -m "harden: Test coverage gap analysis + N new tests"
git push
```

---

## When All Phases Complete

Write `results/OVERNIGHT_SUMMARY.md`:

- Phases completed with status
- Test count before/after
- All commits with hashes
- Key findings for architect (ordered by priority)
- Cross-engine validation results
- Analysis highlights (gate abort patterns, consensus disagreements)

```bash
git add results/OVERNIGHT_SUMMARY.md
git commit -m "report: Overnight summary — N phases completed, M new tests, 0 EUR spent"
git push
```

## Read First

1. This file (NEXT.md)
2. `reference/archive/sessions/weekend/TASK_5_NEXT.md` — Phase 1 instructions
3. `RESULT_PRESERVATION.md`
4. `tests/results/source_engine/MASTER_MANIFEST.json`
5. `results/CALIBRATION_REPORT.md`
6. `engines/normalization/tests/conftest.py`

## Do NOT Do

1. **Do NOT modify engine source code or shared modules.**
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT make any LLM API calls.** Zero cost overnight.
4. **Do NOT re-process books from MASTER_MANIFEST.json.**
5. **Do NOT ask questions.**
6. **Do NOT skip committing and pushing between phases.**
