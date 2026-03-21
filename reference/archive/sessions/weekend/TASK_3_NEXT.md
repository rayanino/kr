# NEXT — Weekend Task 3: Verification Re-Sweep + Calibration Report

## Current Position

- **Phase:** Post-fix verification + data analysis
- **Mode:** AUTONOMOUS DATA COLLECTION AND ANALYSIS — no architect interaction needed
- **Previous:** Task 1 (corpus sweeps) complete. Task 2 (bug fix sprint) complete. Crashes fixed with tests. Some books may still crash (documented in still_crashing.txt).
- **Purpose:** (1) Verify that bug fixes actually resolved crashes at scale. (2) Produce the calibration report the architect needs for the normalization transition gate.

## Rules for This Session

1. **Do NOT modify any engine source code.** Task 2 handled fixes. This task is data collection only.
2. **Do NOT modify any SPEC or contracts.**
3. **You MAY modify scripts** in `scripts/` to support re-sweep and analysis.
4. **You MAY create new analysis scripts** in `scripts/` or `results/`.
5. **Budget: €0.** No LLM API calls.

## What to Do

### Part A: Verification Re-Sweep (1 hour)

**Goal:** Re-run the full normalization corpus sweep to get clean numbers post-fixes.

1. **Re-run the normalization sweep on the FULL collection** (not just crash books):
   ```bash
   # Fresh output directory — don't mix with Task 1 results
   python scripts/normalization_corpus_sweep.py --collection-dir shamela-export-samples --output-dir results/normalization_sweep_v2
   ```
   
   This re-run uses the FIXED engine code from Task 2. It should take the same time as Task 1 (~1-2 hours).

2. **While that runs, re-run the source sweep if Task 2 fixed any source engine bugs:**
   ```bash
   python scripts/phases/run_phase_a.py shamela-export-samples --output-dir results/source_sweep_v2
   ```
   If Task 2 made no source engine changes, skip this — use Task 1 results.

3. **Compare before/after:**
   ```markdown
   | Metric | Task 1 (before fixes) | Task 3 (after fixes) | Delta |
   |--------|----------------------|---------------------|-------|
   | Total books | | | |
   | OK | | | |
   | CRASH | | | |
   | VALIDATION_FAILED | | | |
   | Crash rate | | | |
   ```

4. Write comparison in `results/VERIFICATION_REPORT.md`.

### Part B: Calibration Report (1 hour)

**Goal:** Analyze the sweep data (use Task 3 v2 results if available, otherwise Task 1 results) to produce distributions and baselines for the transition gate.

Create `results/CALIBRATION_REPORT.md` with these sections:

#### B.1: Corpus Statistics
- Total books processed
- Success rate
- Processing time distribution (mean, median, p95, max)
- Book size distribution (pages: mean, median, p95, max)

#### B.2: Multi-Layer Detection at Scale
- Books where auto-upgrade triggered (count and percentage)
- Of auto-upgraded books: distribution of multi-layer unit counts
- Of auto-upgraded books: mean/median matn confidence scores
- **KEY QUESTION:** What percentage of auto-upgraded books have mean matn confidence < 0.70? (These are likely false positives per EVALUATION_REPORT.md F-1)
- List the top 20 auto-upgraded books by multi-layer unit count (name, unit count, mean matn confidence)

#### B.3: Division Tree
- Distribution of division count per book (mean, median, p95, max)
- Books with zero divisions (count, percentage — these are flat-structure books)
- Books with division overlap warnings (count, percentage — L-010 rate at scale)

#### B.4: Boundary Continuity
- Mean BC coverage across all books
- BC type distribution across all pages (% mid_sentence, % mid_paragraph, % mid_argument, % section_break, % unknown)
- Books with 0% BC coverage (count, percentage, reason — likely 1-page books)

#### B.5: Content Flags
- Total hadith pages across corpus
- Total quran pages across corpus
- Total verse pages across corpus
- Books with zero content flags (count — these are non-Islamic-text books or content flagger gaps)

#### B.6: Arabic Text Quality
- Arabic ratio distribution (mean, median, min, p5)
- Books with arabic_ratio < 70% (count, list top 20 by lowest ratio)
- Diacritic density distribution (diacritics per 1000 Arabic chars: mean, median, p95)
- Books with zero diacritics (count — likely printed texts without tashkeel)

#### B.7: Warning Patterns at Scale
- Warning type distribution (sorted by frequency)
- Top 10 most-warned books (name, warning count, dominant warning type)

#### B.8: Passaging Contract Alignment
- Books failing check 4 (count mismatch): count
- Books failing check 5 (ordering/gaps): count
- Books failing check 6 (division inconsistency): count
- **Any book failing checks 4 or 5 is a potential engine bug — list them by name**

#### B.9: Footnote Distribution
- Books with structured footnotes (count, percentage)
- Mean footnote pages per book (across books that have any)
- This tells us what percentage of the passaging workload involves footnote renumbering

### Part C: Analysis Script

Write the analysis as a reusable Python script:
```
scripts/analyze_sweep_results.py --input results/normalization_sweep_v2/corpus_sweep.jsonl --output results/CALIBRATION_REPORT.md
```

This makes it re-runnable after future sweeps. Commit the script alongside the report.

### Step 4: Commit Everything

```bash
git add results/VERIFICATION_REPORT.md results/CALIBRATION_REPORT.md scripts/analyze_sweep_results.py
# Do NOT add the full v2 sweep JSONL if >100MB — add only summary files
git add results/normalization_sweep_v2/CORPUS_SWEEP_SUMMARY.md
git commit -m "sweep: Verification re-sweep + calibration report"
```

## Read First

1. This file (NEXT.md)
2. `results/SWEEP_FIX_SUMMARY.md` — what was fixed in Task 2
3. `results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md` — Task 1 baseline
4. `engines/normalization/EVALUATION_REPORT.md` — what the 63-fixture evaluation found
5. `engines/normalization/KNOWN_LIMITATIONS.md` — known limitations to expect at scale

## Do NOT Do

1. **Do NOT modify engine source code.** Data collection only.
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT run LLM API calls.**
4. **Do NOT commit per-book JSON/JSONL files >100MB to git.**
5. **Do NOT interpret findings.** Report numbers and distributions. The architect interprets.

## Verification

- [ ] VERIFICATION_REPORT.md has before/after comparison table
- [ ] CALIBRATION_REPORT.md has all 9 sections (B.1-B.9)
- [ ] analyze_sweep_results.py is committed and executable
- [ ] No engine source code modified
- [ ] All commits use `sweep:` prefix
