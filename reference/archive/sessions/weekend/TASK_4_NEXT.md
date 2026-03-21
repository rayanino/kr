# NEXT — Weekend Task 4: Source Engine LLM Edge-Case Probes

## Current Position

- **Phase:** Source engine hardening — extending ground truth
- **Mode:** AUTONOMOUS LLM VALIDATION — architect unavailable
- **Previous:** Tasks 1-3 complete. Sweeps done, bugs fixed, calibration report produced.
- **Purpose:** Run ~70 strategically selected books through the full source engine pipeline with LLM inference. Extend ground truth beyond the 204 Phase D books with maximum coverage of gaps.

## Rules for This Session

1. **You MAY run LLM API calls.** Budget is unlimited — quality and coverage matter, not cost. Track actual spend in COST_LOG.json for accounting purposes, but do NOT stop due to cost.
2. **Follow RESULT_PRESERVATION.md strictly.** Every API call persists full structured output. Raw LLM responses saved per-model. No unsaved calls.
3. **Do NOT modify engine source code.** If a bug causes a book to fail, log it and continue. Do not fix it.
4. **Do NOT modify SPECs or contracts.**
5. **Use the source engine's existing pipeline** — `engines/source/src/engine.py` or the equivalent run script.
6. **Commit results to `tests/results/source_engine/phase_e/`** following the Phase D structure.

## API Configuration

The pipeline uses environment variables for API keys (same as Phase C/D):
```
ANTHROPIC_API_KEY  — for Claude Opus 4.6 (primary model)
OPENROUTER_API_KEY — for Command A (secondary) and GPT-5.4 (fallback)
```

These should already be set in your environment from Phase D. Verify with:
```bash
python -c "import os; print('ANTHROPIC:', bool(os.environ.get('ANTHROPIC_API_KEY'))); print('OPENROUTER:', bool(os.environ.get('OPENROUTER_API_KEY')))"
```

If not set, load them from the project knowledge files (API keys are in the root of the project's Claude Project files).

## What to Do

### Step 1: Select ~70 Books

Select books from `shamela-export-samples/` targeting 6 strategic categories. Use the Task 1 sweep results (`results/source_sweep/PHASE_A_SUMMARY.json` or per-book JSONs on disk), normalization sweep results, and Phase D data to identify candidates.

**Selection criteria (~70 books total):**

| Category | Count | Selection Method |
|----------|-------|-----------------|
| Genre diversity gaps | 20-25 | **Priority 1.** Phase D has 12 categories with ≤2 books each (الفقه الشافعي, الطبراني, الفقه المالكي, الفقه الحنبلي, الغريب والمعاجم, الرقائق والآداب والأذكار, التاريخ, السيرة النبوية, الجوامع, التراجم والطبقات, مسائل فقهية, الفقه الحنفي). Pick 2-3 per thin category to reach minimum 3 each. **Also:** scan the full corpus (`shamela-export-samples/`) for Shamela categories that have ZERO books in Phase D — these are complete blind spots. Pick 2-3 from each discovered zero-coverage category. Use `tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json` and per-book extraction JSONs from source sweep (on local disk at `results/source_sweep/`) for category data. |
| Multi-layer candidates | 15 | Books that auto-upgraded to multi-layer in the normalization sweep (from `results/CALIBRATION_REPORT.md` section B.2 top list, or from `results/normalization_sweep_v2/corpus_sweep.jsonl` filtering for `auto_upgraded_multi=true`). Pick diverse multi-layer rates (some 30%, some 60%, some 85%+) to test the LLM's `is_multi_layer` field against normalization auto-detection. |
| Source extraction anomalies | 10 | Books where source sweep succeeded but metadata is sparse: missing `author_name_raw` (263 books lack it), or missing `title_full`, or having many extra card fields. These stress-test the LLM's ability to infer from limited extraction data. Use per-book JSONs from `results/source_sweep/` on local disk. |
| Extreme metrics | 8 | 3 largest books (most pages/content units), 3 smallest non-trivial books (3-10 pages), 2 with highest diacritic density. Tests pipeline at scale extremes. |
| Formerly zero-content books | 8 | Books from the 48 that were fixed in Task 2 (now producing content after the pageless-books fix). These are hadith compilations without page numbers — verify their LLM metadata inference works. Pick 8 diverse ones from the zero-content list in `results/normalization_sweep/CC_ANALYSIS.md` §3. |
| Previously unknown | 5 | Books whose names don't appear in Phase D results at all AND don't fit the above categories. Aims for maximum novelty. |

**Important:** Do NOT select books that CRASHED in the source sweep (format detection failed). Those can't go through LLM inference because extraction didn't produce output. Source sweep had 0 crashes, so this is not a concern for this corpus.

Write the selection with rationale in `tests/results/source_engine/phase_e/PHASE_E_SELECTION.md`. For each book, state: (a) which category it fills, (b) why this specific book was chosen over alternatives, (c) its Shamela category.

### Step 2: Filter Against Existing Results

Before running, check that no selected book already exists in Phase D:
```python
import json
manifest = json.load(open("tests/results/source_engine/MASTER_MANIFEST.json"))
existing = set(manifest.get("books", {}).keys())
# Remove any selected books that are already in MASTER_MANIFEST
selected = [b for b in selected_books if b not in existing]
```

Write the final filtered book list to `tests/results/source_engine/phase_e/books.txt` (one book name per line).

### Step 3: Back Up COST_LOG.json

**CRITICAL — do this BEFORE running the pipeline.**

`run_phase_c.py` hardcodes `cost_log["phases"]["C"]` when updating the cost log. Running it for Phase E will **overwrite Phase C's real data** (73 books, €7.00). Back up the cost log so we can restore it:

```python
import json, shutil
from pathlib import Path

cost_log_path = Path("tests/results/source_engine/COST_LOG.json")
backup_path = Path("tests/results/source_engine/COST_LOG_BACKUP_PRE_PHASE_E.json")
shutil.copy2(cost_log_path, backup_path)
print(f"Backed up COST_LOG.json to {backup_path}")

# Verify backup
original = json.loads(cost_log_path.read_text())
backup = json.loads(backup_path.read_text())
assert original == backup, "Backup mismatch!"
print(f"Phase C data to preserve: {original['phases']['C']}")
```

### Step 4: Run the Pipeline

Use the **existing** `run_phase_c.py` script — it handles all artifact capture, consensus, and result persistence. Point it at a Phase E output directory:

```bash
python scripts/phases/run_phase_c.py shamela-export-samples \
    --books tests/results/source_engine/phase_e/books.txt \
    --output-dir tests/results/source_engine/phase_e \
    --budget-eur 200 \
    --resume
```

**Note on --budget-eur 200:** This is set high intentionally. The script's pre-flight check adds `already_spent` (€30.60 from all prior phases) to `estimated`. With a low ceiling, the script aborts before processing anything. The €200 ceiling gives ample headroom. Actual spend will be ~€7-10 for ~70 books at €0.10/book.

This produces the same per-book structure as Phase D:
```
tests/results/source_engine/phase_e/
  {book_name}/
    result.json        — full SourceMetadata
    extraction.json    — raw extraction
    consensus.json     — per-field consensus details
    prompt_sent.json   — exact prompt sent
    llm_responses/
      opus_4_6.json    — raw Opus response
      command_a.json   — raw Command A response
      fallback.json    — fallback (if triggered)
    sanity_checks.json — automated quality flags
```

If a book fails (gate_abort, error), all available artifacts are still saved. Use `--resume` to continue after interruption.

### Step 5: Write PHASE_E_LESSONS.md

Follow the same format as `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md`:
- Results summary (success rate, gate_abort rate, error rate)
- Patterns observed (new extraction patterns, inference quality, consensus disagreements)
- What worked / what to watch
- Field stability notes
- New findings not seen in Phase D
- **New section: Genre coverage analysis** — which categories now have ≥3 books? Which are still thin?
- **New section: Multi-layer LLM vs normalization comparison** — does LLM `is_multi_layer` agree with normalization auto-detection? List disagreements.
- **New section: Formerly zero-content books** — did LLM inference work on the hadith compilations that were fixed in Task 2?

### Step 6: Fix Manifest Metadata + Restore Cost Log + Update Master Manifest

`run_phase_c.py` hardcodes Phase C identifiers in several outputs. Fix all of them:

**6a. Fix phase manifest and summary filenames:**

```python
import json
from pathlib import Path

# Fix manifest
manifest_path = Path("tests/results/source_engine/phase_e/PHASE_C_MANIFEST.json")
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))

# Fix phase identifier
manifest["phase"] = "E"

# Fix result paths
for book_name, entry in manifest.get("books", {}).items():
    if "result_path" in entry:
        entry["result_path"] = entry["result_path"].replace("phase_c/", "phase_e/")

# Write as PHASE_E_MANIFEST.json
out_path = manifest_path.parent / "PHASE_E_MANIFEST.json"
out_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
manifest_path.unlink()  # Remove the phase_c named file

# Same for summary
summary_path = Path("tests/results/source_engine/phase_e/PHASE_C_SUMMARY.json")
if summary_path.exists():
    summary_path.rename(summary_path.parent / "PHASE_E_SUMMARY.json")
```

**6b. Restore COST_LOG.json — fix Phase C overwrite:**

```python
import json
from pathlib import Path

cost_log_path = Path("tests/results/source_engine/COST_LOG.json")
backup_path = Path("tests/results/source_engine/COST_LOG_BACKUP_PRE_PHASE_E.json")

# Load both
current = json.loads(cost_log_path.read_text(encoding="utf-8"))
backup = json.loads(backup_path.read_text(encoding="utf-8"))

# The script overwrote phases["C"] with Phase E data. Extract Phase E data first.
phase_e_data = current["phases"]["C"].copy()

# Restore Phase C from backup
current["phases"]["C"] = backup["phases"]["C"]

# Write Phase E data to correct key
current["phases"]["E"] = phase_e_data
current["phases"]["E"]["status"] = "complete"

# Recalculate total
total = sum(p.get("cost_eur", 0) for p in current["phases"].values())
current["total_eur"] = round(total, 2)

cost_log_path.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")

print(f"Restored Phase C: {current['phases']['C']}")
print(f"Phase E: {current['phases']['E']}")
print(f"New total: {current['total_eur']} EUR")
```

**6c. Merge Phase E books into MASTER_MANIFEST.json:**

```python
import json
from pathlib import Path

master_path = Path("tests/results/source_engine/MASTER_MANIFEST.json")
phase_e_manifest_path = Path("tests/results/source_engine/phase_e/PHASE_E_MANIFEST.json")

master = json.loads(master_path.read_text(encoding="utf-8"))
phase_e = json.loads(phase_e_manifest_path.read_text(encoding="utf-8"))

# Merge Phase E books into master
for book_name, entry in phase_e.get("books", {}).items():
    entry["phase"] = "E"
    master["books"][book_name] = entry

master_path.write_text(json.dumps(master, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Master manifest: {len(master['books'])} books (was 204, added {len(phase_e.get('books', {}))})")
```

### Step 7: Commit

**IMPORTANT:** `tests/results/` is in `.gitignore`. You must use `git add -f` (force) to commit results. This is how all Phase C/D results were committed.

```bash
# Check size first — raw LLM responses can be large
du -sh tests/results/source_engine/phase_e/

# If under 50MB total, commit everything (MUST use -f)
git add -f tests/results/source_engine/phase_e/
git add -f tests/results/source_engine/MASTER_MANIFEST.json
git add -f tests/results/source_engine/COST_LOG.json
git commit -m "validate: Phase E — ~70 edge-case LLM probes (€X.XX spent)"

# If over 50MB, commit only manifests, summaries, and lessons
# Keep raw LLM responses local
git add -f tests/results/source_engine/phase_e/PHASE_E_*.md
git add -f tests/results/source_engine/phase_e/PHASE_E_*.json
git add -f tests/results/source_engine/MASTER_MANIFEST.json
git add -f tests/results/source_engine/COST_LOG.json
git commit -m "validate: Phase E summaries — ~70 edge-case probes (€X.XX, raw responses local)"
```

## Read First

1. This file (NEXT.md)
2. `RESULT_PRESERVATION.md` — the preservation protocol (NON-NEGOTIABLE)
3. `scripts/phases/run_phase_c.py` — THE SCRIPT YOU WILL USE (read the docstring and arg parser)
4. `tests/results/source_engine/MASTER_MANIFEST.json` — books already processed (skip these)
5. `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md` — what Phase D learned
6. `tests/results/source_engine/PHASE_D_CATEGORY_DISTRIBUTION.json` — Phase D category distribution (for genre gap selection)
7. `results/CALIBRATION_REPORT.md` — sweep baselines (for book selection)
8. `results/normalization_sweep/CC_ANALYSIS.md` — zero-content book list (for formerly zero-content selection)

## Do NOT Do

1. **Do NOT modify engine source code.** Log bugs, don't fix them.
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT re-process books already in Phase D.** Check MASTER_MANIFEST.json.
4. **Do NOT discard any LLM response.** Every call is persisted per RESULT_PRESERVATION.md.
5. **Do NOT skip the COST_LOG.json backup in Step 3.** The pipeline script will overwrite Phase C data without it.

## Verification

- [ ] PHASE_E_SELECTION.md documents all selected books with per-book rationale and category assignment
- [ ] books.txt has the filtered list (no Phase D duplicates)
- [ ] PHASE_E_MANIFEST.json has entries for all processed books (NOT named PHASE_C_MANIFEST.json)
- [ ] PHASE_E_LESSONS.md follows Phase D format PLUS new sections (genre coverage, multi-layer comparison, zero-content books)
- [ ] COST_LOG.json has BOTH Phase C (73 books, €7.00) AND Phase E data as separate entries — Phase C was NOT overwritten
- [ ] MASTER_MANIFEST.json has 204 + N Phase E books
- [ ] Every processed book has result.json + extraction.json + consensus.json + raw LLM responses
- [ ] No engine source code modified
- [ ] No books from Phase D re-processed (verified against MASTER_MANIFEST.json)
