# NEXT — Weekend Task 2: Sweep Bug Fix Sprint

## Current Position

- **Phase:** Post-sweep hardening
- **Mode:** AUTONOMOUS BUG FIXING — architect unavailable for design decisions
- **Previous:** Corpus sweeps complete (Task 1). Normalization sweep on 20K+ books. Source engine deterministic sweep on 20K+ books. Cross-engine findings report written.
- **Purpose:** Fix every crash and obvious bug found in the sweeps. Each fix requires a test. Document anything needing architect judgment.

## Rules for This Session

1. **You MAY modify engine source code** (`engines/source/src/`, `engines/normalization/src/`) to fix bugs found during the sweeps. Every fix MUST have a new or modified test that proves the fix.
2. **Do NOT modify any SPEC** (`SPEC.md`, `SPEC_CORE.md`). If a fix would conflict with the SPEC, document it in SWEEP_ARCHITECT_REVIEW.md and skip the fix.
3. **Do NOT modify contracts.py** unless a field type is clearly wrong (e.g., Optional that should be required). Document any contract changes in your commit message.
4. **Do NOT make architectural decisions.** If a fix requires judgment about the right approach, document both options in SWEEP_ARCHITECT_REVIEW.md and skip it.
5. **You MAY add test fixtures** from edge cases found during sweeps.
6. **Commit each fix separately** with descriptive messages prefixed with `fix:`. Include the crash count and pattern in the commit message.
7. **Run full test suite after EVERY fix** — zero regressions allowed.
8. **Budget: €0.** Do NOT run any LLM API calls.

## What to Do

### Step 1: Read the Sweep Results

Read these files (produced by Task 1):
- `results/normalization_sweep/CC_ANALYSIS.md`
- `results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md`
- `results/source_sweep/CC_ANALYSIS.md` (if exists)
- `results/source_sweep/PHASE_A_SUMMARY.json` (if exists)
- `results/CROSS_ENGINE_FINDINGS.md` (if exists)

From the normalization sweep, extract:
- Every CRASH pattern (group by error type and traceback root cause)
- Every VALIDATION_FAILED pattern
- Books with anomalous metrics (page_loss > 10, arabic_ratio < 50%, zero content_units)

From the source sweep, extract:
- Every error pattern EXCEPT `SRC_UNSUPPORTED_FORMAT` (those are non-book items in the directory, not real errors)
- Books with missing critical fields (no title_full, no source_format detection)

### Step 2: Triage Crashes by Fixability

For each crash pattern, classify as:
- **FIX NOW:** Root cause is clear, fix is localized (changes ≤50 lines in ≤2 files), test is obvious. Examples: missing None check, regex not handling a character class, encoding error on specific input.
- **ARCHITECT REVIEW:** Root cause is clear but fix requires a design choice (e.g., should we skip this HTML structure or support it?). Or fix touches >50 lines or >2 files. Or fix might change behavior for non-crashing books.
- **DEFER:** Crash affects <5 books AND the books have unusual/corrupt HTML that isn't worth supporting.

Document the triage in `results/SWEEP_BUG_TRIAGE.md`:
```markdown
| # | Engine | Crash Pattern | Error Type | Books Affected | Classification | Rationale |
|---|--------|---------------|------------|----------------|----------------|-----------|
```

### Step 3: Fix Every FIX NOW Bug

For each FIX NOW bug, in order from most-affected to least-affected:

1. **Write a failing test FIRST.** Use one of the crashing books as a fixture if it's small (<500KB). Otherwise, create a minimal reproducing HTML fixture that triggers the same crash.
2. Implement the fix.
3. Run pytest — verify the new test passes AND zero regressions on existing tests.
4. Run pyright — no new type errors.
5. Commit: `fix: [engine] description (N books affected)`

### Step 4: Write Summary Reports

**`results/SWEEP_FIX_SUMMARY.md`** — REQUIRED:
```markdown
# Sweep Fix Summary

## Normalization Engine
- Crashes found: N
- Crashes fixed (FIX NOW): N (with test coverage)
- Crashes deferred: N
- Crashes for architect review: N
- Test count before fixes: [run pytest --co -q and count]
- Test count after fixes: [run pytest --co -q and count]

## Source Engine
- Errors found (excluding UNSUPPORTED_FORMAT): N
- Errors fixed: N
- ...

## Crash Books List
[List the book names that crashed, grouped by fix status]
```

**`results/SWEEP_ARCHITECT_REVIEW.md`** — REQUIRED even if empty:
For each ARCHITECT REVIEW bug:
- Crash pattern and traceback
- Root cause analysis
- Option A: [describe fix approach + trade-offs]
- Option B: [describe alternative fix + trade-offs]
- CC recommendation: [which option and why]
- Affected book count
- Affected book names (first 10)

If no bugs need architect review, write: "No bugs required architect review. All crashes were either FIX NOW (fixed with tests) or DEFER (<5 books with corrupt HTML)."

### Step 5: Collect Crash Book Lists for Re-Sweep

Create these files (Task 3 needs them):

**`results/normalization_sweep/crash_books.txt`** — one book directory name per line, for books that CRASHED (not VALIDATION_FAILED) in the normalization sweep. Extract from `errors.jsonl`:
```python
import json
with open("results/normalization_sweep/errors.jsonl") as f:
    names = [json.loads(line)["name"] for line in f if json.loads(line)["status"] == "CRASH"]
with open("results/normalization_sweep/crash_books.txt", "w") as f:
    f.write("\n".join(sorted(set(names))))
```

**`results/normalization_sweep/still_crashing.txt`** — same format, but only books that STILL crash after fixes. Re-run the crash_books list through the normalization sweep to check:
```bash
# Create a temporary directory with just the crash books
python -c "
import shutil, pathlib
books = pathlib.Path('results/normalization_sweep/crash_books.txt').read_text().strip().split('\n')
out = pathlib.Path('results/normalization_sweep/rerun_subset')
out.mkdir(exist_ok=True)
base = pathlib.Path('shamela-export-samples')
for b in books:
    src = base / b
    if src.exists():
        dst = out / b
        if not dst.exists():
            dst.symlink_to(src)  # symlink to avoid copying
"
python scripts/normalization_corpus_sweep.py --collection-dir results/normalization_sweep/rerun_subset --output-dir results/normalization_sweep/rerun_results
```

Compare crash counts before and after. Record the delta.

### Step 6: Commit Everything

```bash
git add results/SWEEP_BUG_TRIAGE.md results/SWEEP_FIX_SUMMARY.md results/SWEEP_ARCHITECT_REVIEW.md
git add results/normalization_sweep/crash_books.txt results/normalization_sweep/still_crashing.txt
git commit -m "sweep: Bug fix sprint summary — N fixed, M remaining"
```

## Read First

1. This file (NEXT.md)
2. `results/normalization_sweep/CC_ANALYSIS.md`
3. `results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md`
4. `results/source_sweep/CC_ANALYSIS.md` (if exists)
5. `results/CROSS_ENGINE_FINDINGS.md` (if exists)
6. `engines/normalization/KNOWN_LIMITATIONS.md` — don't re-discover known issues

## Do NOT Do

1. **Do NOT rewrite large modules.** If a fix requires changing >50 lines in one file, classify as ARCHITECT REVIEW.
2. **Do NOT add new detection heuristics** (new markers, new thresholds). Only fix existing logic that crashes.
3. **Do NOT run any LLM API calls.** This session is €0.
4. **Do NOT modify SPECs or contracts.**
5. **Do NOT delete existing test fixtures.** Only ADD new ones.
6. **Do NOT fix bugs classified as ARCHITECT REVIEW.** Document them and move on.
7. **Do NOT spend more than 30 minutes on any single bug.** If a fix isn't clear after 30 minutes, it's ARCHITECT REVIEW.

## Verification

After all fixes:
- [ ] Full pytest passes (both engines) with zero regressions
- [ ] Pyright clean (or no NEW errors)
- [ ] Every fix has at least one new test
- [ ] SWEEP_BUG_TRIAGE.md documents every crash pattern
- [ ] SWEEP_FIX_SUMMARY.md has before/after crash counts and test counts
- [ ] SWEEP_ARCHITECT_REVIEW.md exists (even if "no bugs needed review")
- [ ] crash_books.txt and still_crashing.txt exist
- [ ] No SPEC or contract files modified: `git diff engines/*/SPEC*.md engines/*/contracts.py` returns empty
- [ ] All fix commits use `fix:` prefix
