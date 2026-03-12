# NEXT — Step 4 Phase D Pipeline Run

## Status: Pre-run preparation COMPLETE. Owner runs pipeline next.

## What the owner does

Open a terminal in the `kr` directory and run:

```
set ANTHROPIC_API_KEY=<your key>
set OPENROUTER_API_KEY=<your key>
set PYTHONIOENCODING=utf-8

# Step 1: Merge the two collection directories (one-time, ~30 seconds)
xcopy /E /I phase_c_collection combined_collection
xcopy /E /I phase_d_collection combined_collection

# Step 2: Run all 204 books
python scripts/run_phase_c.py combined_collection --books scripts/step4_all_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 50
```

If disconnected mid-run:

```
python scripts/run_phase_c.py combined_collection --books scripts/step4_all_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 50 --resume
```

**Why merge first?** The 204 books span two prepared collection directories (`phase_c_collection/` and `phase_d_collection/`). `run_phase_c.py` takes one collection directory, and its manifest generation (PHASE_C_MANIFEST.json) would be incomplete if run twice to the same output directory — the second run overwrites the first run's manifest.

Expected: ~1-2 hours, ~EUR 20 cost, 204 books processed.

After the run completes, open Claude Code and paste Prompt 3 (post-processing + GUI generation).

## Known limitation

`run_phase_c.py` hardcodes `result_path: "phase_c/..."` in the manifest regardless of actual output directory. Post-processing (Prompt 3) should use `phase_d/{book_name}/result.json` instead of the manifest's `result_path` field.

## Key state
- Pipeline version: HEAD (post-bug-fix, smoke-tested)
- Books: 204 (73 reruns + 131 new)
- Combined list: `scripts/step4_all_books.txt`
- Budget spent: EUR 9.70, estimated Phase D: ~EUR 20-30, remaining: ~EUR 60-70
- Rerun tracking: `tests/results/source_engine/phase_d/RERUN_BOOKS.json`
- Verification: `scripts/verify_step4_books.py` — all 6 checks PASS
- Source engine tests: 502 passed, 0 failures
