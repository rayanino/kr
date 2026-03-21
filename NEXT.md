# NEXT — Weekend Task 3: Verification + Calibration Report

## Current Position

- **Phase:** Post-fix verification + data analysis
- **Mode:** AUTONOMOUS DATA COLLECTION AND ANALYSIS — no architect interaction needed
- **Previous:** Task 1 (corpus sweeps) complete. Task 2 (bug fix sprint) complete.
- **Purpose:** (1) Verify bug fixes resolved crashes. (2) Produce the calibration report the architect needs for the normalization transition gate.

## Rules for This Session

1. **Do NOT modify any engine source code.** Task 2 handled fixes. This task is data collection only.
2. **Do NOT modify any SPEC or contracts.**
3. **You MAY modify or create scripts** in `scripts/` for analysis.
4. **Budget: €0.** No LLM API calls.

## What to Do

### Part A: Verify Bug Fixes (30-60 minutes)

**Step 1:** Determine re-sweep scope by checking what Task 2 changed.

Run:
```bash
git log --oneline --all | grep "fix:" | head -20
# Then for each fix commit:
git diff COMMIT~1 COMMIT --name-only -- engines/normalization/src/ engines/source/src/
```

Classify each changed file:

- **Error-path-only changes** (added None guard, added try/except, fixed missing key check): These only affect books that previously CRASHED. A crash-only re-run is sufficient.
- **Logic changes** (modified regex, changed parsing behavior, altered threshold, changed control flow): These could affect ALL books. A full re-sweep is needed.

**Step 2a:** If ALL changes are error-path-only → crash-only verification:

```bash
python scripts/rerun_crash_books.py results/normalization_sweep/crash_books.txt shamela-export-samples results/normalization_sweep/rerun_subset
python scripts/normalization_corpus_sweep.py --collection-dir results/normalization_sweep/rerun_subset --output-dir results/normalization_sweep/rerun_results --resume
```

Write `results/VERIFICATION_REPORT.md`:
```markdown
# Verification Report

## Re-sweep Scope: Crash books only
**Rationale:** All Task 2 fixes are error-path-only (None guards, try/except). Non-crashing books are unaffected.

| Metric | Task 1 (before) | Rerun (after) |
|--------|-----------------|---------------|
| Crash books tested | N | N |
| Still crashing | — | M |
| Now OK | — | K |
```

**Step 2b:** If ANY change touches core logic → full re-sweep:

```bash
python scripts/normalization_corpus_sweep.py --collection-dir shamela-export-samples --output-dir results/normalization_sweep_v2 --resume
```

Write `results/VERIFICATION_REPORT.md` with full before/after comparison table.

### Part B: Calibration Report (1-2 hours)

**Use Task 1 results for calibration** unless you did a full re-sweep in Step 2b, in which case use v2 results. Filter out CRASH entries — the calibration is about healthy books.

Create a reusable analysis script AND the report:

```bash
python scripts/analyze_sweep_results.py --input results/normalization_sweep/corpus_sweep.jsonl --output results/CALIBRATION_REPORT.md
```

The script reads the JSONL and produces `CALIBRATION_REPORT.md` with these sections:

**B.1: Corpus Statistics**
- Total books processed, success rate, crash rate
- Processing time: mean, median, p95, max
- Book size (content_units): mean, median, p95, max
- Total pages across corpus

**B.2: Multi-Layer Detection at Scale**
- Books where `auto_upgraded_multi == true`: count and percentage
- Of auto-upgraded: distribution of `multi_layer_units` counts
- **KEY METRIC:** What percentage of auto-upgraded books look like false positives? (Heuristic: multi_layer_units > 50% of content_units AND all from bracket detection)
- Top 20 auto-upgraded books by multi_layer_units (name, count)

**B.3: Division Tree**
- `division_count` distribution: mean, median, p95, max
- Books with zero divisions: count, percentage
- Books with division overlap warnings: count, percentage
- Compare overlap rate to 63-fixture rate (14% in evaluation)

**B.4: Boundary Continuity**
- Mean `bc_coverage` across all OK books
- Aggregate `bc_types` distribution: % mid_sentence, mid_paragraph, mid_argument, section_break, unknown
- Books with 0% BC coverage: count, percentage

**B.5: Content Flags**
- Total has_hadith / has_quran / has_verse pages across corpus
- Books with zero content flags: count
- Percentage of corpus pages with each flag

**B.6: Arabic Text Quality**
- `arabic_ratio` distribution: mean, median, p5 (bottom 5%), min
- Books with arabic_ratio < 70%: count, list top 20 by lowest ratio
- Diacritic density (diacritic_count / total_chars × 1000): mean, median, p95
- Books with zero diacritics: count

**B.7: Warning Patterns at Scale**
- Warning type distribution from `warn_categories` (sorted by frequency)
- Total warnings across corpus
- Top 10 most-warned books

**B.8: Passaging Contract Alignment**
- Books failing `check4_count_match`: count — **list all by name** (potential engine bug)
- Books failing `check5_ordered` or `check5_no_gaps`: count — **list all by name** (potential engine bug)
- Books failing `check6_division_consistent`: count, percentage
- Books passing ALL checks: count, percentage

**B.9: Page Loss**
- `page_loss` distribution: mean, median, p95, max
- Books with page_loss > 5: count, list by name
- Books with page_loss == 0: percentage (perfect preservation rate)

### Part C: Commit

```bash
git add results/VERIFICATION_REPORT.md results/CALIBRATION_REPORT.md scripts/analyze_sweep_results.py
git commit -m "sweep: Verification + calibration report"
```

## Read First

1. This file (NEXT.md)
2. `results/SWEEP_FIX_SUMMARY.md` — what was fixed in Task 2 (determines re-sweep scope)
3. `results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md` — Task 1 baseline
4. `engines/normalization/EVALUATION_REPORT.md` — what the 63-fixture evaluation found
5. `engines/normalization/KNOWN_LIMITATIONS.md` — known limitations to expect at scale

## Do NOT Do

1. **Do NOT modify engine source code.** Data collection only.
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT run LLM API calls.**
4. **Do NOT commit per-book JSON/JSONL files >100MB to git.**
5. **Do NOT interpret findings beyond reporting numbers.** The architect interprets.

## Verification

- [x] VERIFICATION_REPORT.md has before/after comparison
- [x] VERIFICATION_REPORT.md states rationale for re-sweep scope (full — both fixes are logic changes)
- [x] CALIBRATION_REPORT.md has all 9 sections (B.1-B.9)
- [x] analyze_sweep_results.py is committed and produces the report when run
- [x] No engine source code modified
- [x] All commits use `sweep:` prefix
