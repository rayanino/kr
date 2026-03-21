# NEXT — Autonomous Hardening: Corpus Sweeps on Source + Normalization Engines

## Current Position

- **Phase:** Post-evaluation hardening (between normalization evaluation GO and transition gate)
- **Mode:** AUTONOMOUS DATA COLLECTION — no architect interaction available
- **Previous:** Normalization evaluation GO at commit `7f81052`. Source engine complete. Both engines stable.
- **Purpose:** Stress-test both engines on the full 20K+ Shamela collection. Collect data. Report findings. Do NOT fix anything.

## Rules for This Session

**READ THESE CAREFULLY — they override normal build procedures.**

1. **DO NOT modify any engine source code** (`engines/source/src/`, `engines/normalization/src/`). Not even small fixes. Report bugs in your output files — the architect fixes them.
2. **DO NOT modify any SPEC** (`SPEC.md`, `SPEC_CORE.md`). Report inconsistencies in your output files.
3. **DO NOT modify contracts.py** in any engine. Report contract issues.
4. **DO NOT make architectural decisions.** If you find something ambiguous, document it and move on.
5. **You MAY modify scripts** (in `scripts/`) to fix crashes in the sweep scripts themselves. This is expected — the sweep scripts were written for the 63-fixture scale and may need adaptation for 20K.
6. **You MAY create new files** in `results/` for output data.
7. **You MAY add test fixtures** if you find interesting edge cases — put them in `tests/fixtures/shamela_edge_cases/`.
8. **Commit periodically** (every major task completion). Use commit messages prefixed with `sweep:`.

## What to Do

### Task A: Normalization Corpus Sweep (PRIMARY — do this first)

**Script:** `scripts/normalization_corpus_sweep.py`
**Input:** `shamela-export-samples/` (20K+ .htm files on local filesystem)
**Output:** `results/normalization_sweep/corpus_sweep.jsonl` + `CORPUS_SWEEP_SUMMARY.md`

1. Verify the script can import correctly:
   ```
   python -c "from scripts.normalization_corpus_sweep import discover_books; print('OK')"
   ```

2. Install dependencies if needed:
   ```
   pip install beautifulsoup4 lxml pydantic pyyaml
   ```

3. Test on a small sample first (10 books):
   ```
   python scripts/normalization_corpus_sweep.py --collection-dir shamela-export-samples --limit 10
   ```

4. If the small sample works, run the full sweep:
   ```
   python scripts/normalization_corpus_sweep.py --collection-dir shamela-export-samples
   ```
   This will take 1-2 hours. The script streams results to JSONL, so partial results are saved even if interrupted. Use `--resume` to continue after interruption.

5. After completion, read `results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md` and write your analysis in `results/normalization_sweep/CC_ANALYSIS.md`. Focus on:
   - **Crash patterns:** What types of books crash? Are there common HTML structures that break the parser?
   - **Warning patterns at scale:** Do the same warning types dominate? Any new warning types?
   - **Multi-layer auto-upgrade rate:** What percentage of books auto-upgrade? Is this reasonable?
   - **Passaging contract alignment:** What percentage fail passaging checks? Which checks?
   - **Anomalies:** Any books with surprising metrics (very high page loss, zero diacritics, extremely low Arabic ratio)?
   - **Edge cases:** Save 3-5 interesting crash-causing or anomalous books as test fixtures in `tests/fixtures/shamela_edge_cases/`

6. Commit results:
   ```
   git add results/normalization_sweep/ tests/fixtures/shamela_edge_cases/
   git commit -m "sweep: Normalization corpus sweep on 20K+ books"
   ```

### Task B: Source Engine Deterministic Sweep

**Script:** `scripts/phases/run_phase_a.py` (already implemented)
**Input:** Same `shamela-export-samples/` directory
**Output:** Output directory specified via `--output-dir`

1. Test on a small sample (10 books):
   ```
   python scripts/phases/run_phase_a.py shamela-export-samples --output-dir results/source_sweep --limit 10
   ```

2. If the small sample works, run the full sweep:
   ```
   python scripts/phases/run_phase_a.py shamela-export-samples --output-dir results/source_sweep
   ```

3. Analyze the results. Focus on:
   - **Format detection accuracy:** How many are detected as shamela_html vs other?
   - **Extraction success rate:** What percentage extract cleanly?
   - **Crash patterns:** What HTML structures cause crashes?
   - **Hashing:** Any duplicate hashes (identical content across different books)?

4. Write analysis in `results/source_sweep/CC_ANALYSIS.md`.

5. **IMPORTANT — git commit rules for source sweep:**
   The source sweep produces one JSON file per item (20K+ files). Do NOT commit per-book JSON files to git — the repo cannot handle 20K+ files.
   
   Commit ONLY summary files:
   ```
   git add results/source_sweep/PHASE_A_SUMMARY.json results/source_sweep/CC_ANALYSIS.md
   git commit -m "sweep: Source engine deterministic sweep on 20K+ books (summaries only, per-book JSON local)"
   ```
   
   The per-book JSON files stay on disk for local analysis but are NOT pushed to git.

6. **Note on UNSUPPORTED_FORMAT errors:** The source sweep iterates ALL items in the collection directory, including non-book items (metadata files, etc.). These will produce `SRC_UNSUPPORTED_FORMAT` errors — that is expected and correct. In your CC_ANALYSIS.md, separate these from genuine extraction errors. Report the error count EXCLUDING unsupported format errors.

### Task C: Cross-Engine Findings Report (if time remains)

After Tasks A and B, write `results/CROSS_ENGINE_FINDINGS.md` analyzing:
- Books that succeed in source but crash in normalization (or vice versa)
- Common failure patterns across both engines
- Corpus statistics useful for passaging design (size distribution, footnote density, multi-layer frequency)
- Top 10 most unusual books and why they're unusual

Commit:
```
git add results/CROSS_ENGINE_FINDINGS.md
git commit -m "sweep: Cross-engine findings report"
```

## Read First

1. This file (NEXT.md)
2. `engines/normalization/CLAUDE.md` — normalization engine orientation
3. `engines/normalization/EVALUATION_REPORT.md` — what we already know
4. `scripts/normalization_corpus_sweep.py` — understand the script before running
5. `scripts/phases/run_phase_a.py` — understand the source sweep script

## Do NOT Do

1. **Do NOT modify engine source code.** Even if you find obvious bugs. Document them.
2. **Do NOT modify SPECs or contracts.** Document issues.
3. **Do NOT start building the passaging engine.** This session is data collection only.
4. **Do NOT run any LLM API calls.** Both sweeps are fully deterministic (€0 cost).
5. **Do NOT delete or overwrite any existing test fixtures.** Only ADD new edge cases.
6. **Do NOT push results that are larger than 100MB per file.** The JSONL files may get large — that's fine for local storage but check size before committing to git. If corpus_sweep.jsonl is too large, commit only the summary .md files and a note about where to find the full data.

## Verification

After each task, verify:
- [ ] Script ran to completion (or saved partial results with --resume capability)
- [ ] Summary report is written and readable
- [ ] CC_ANALYSIS.md documents findings, not fixes
- [ ] No engine source code was modified (check with `git diff engines/`)
- [ ] Results committed with `sweep:` prefix

## After This

When the owner returns:
1. The architect reads CC_ANALYSIS.md files and CORPUS_SWEEP_SUMMARY.md
2. Decides which findings are CORE GAPs vs LESSON LEARNEDs
3. Creates fix tasks if needed (before or after transition gate)
4. Proceeds with the normalization transition gate in a separate session

## Context

The normalization engine has 420 tests passing on 63 fixtures. The evaluation found zero CORE GAPs and zero ENGINE BUGs. But 63 fixtures is a small sample. The full Shamela collection has 20K+ books spanning every genre, era, and formatting style. This sweep finds what 63 fixtures can't — edge cases in HTML structure, encoding, heading patterns, footnote formats, and multi-layer detection that only manifest at scale.

The source engine has been validated on 204 books with LLM calls. The deterministic sweep (format detection + extraction + hashing without LLM) has never run on the full collection. This is Step 2 on the source engine validation roadmap.

Both sweeps cost €0 (no LLM calls) and produce data that directly strengthens the foundation for the passaging engine build.
