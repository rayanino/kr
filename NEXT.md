# NEXT — Step 4 Phase D Pipeline Run

## Status: Pre-run preparation COMPLETE. Owner runs pipeline next.

## What the owner does

Open a terminal in the `kr` directory and run:

```
set ANTHROPIC_API_KEY=<your key>
set OPENROUTER_API_KEY=<your key>

# Run 1: Rerun 73 Phase C books on fixed pipeline
python scripts/run_phase_c.py phase_c_collection --books scripts/phase_c_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 20

# Run 2: Process 131 new books
python scripts/run_phase_c.py phase_d_collection --books scripts/phase_d_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 35
```

If disconnected mid-run, add `--resume` to the command that was interrupted:

```
python scripts/run_phase_c.py phase_c_collection --books scripts/phase_c_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 20 --resume
python scripts/run_phase_c.py phase_d_collection --books scripts/phase_d_books.txt --output-dir tests/results/source_engine/phase_d/ --budget-eur 35 --resume
```

**Why two commands?** The 204 books span two prepared collection directories (`phase_c_collection/` and `phase_d_collection/`). `shamela export samples/` only has 46/204 as directories — verified by `scripts/verify_step4_books.py`.

Expected: ~1-2 hours total, ~EUR 20 cost, 204 books processed.

After both runs complete, open Claude Code and paste Prompt 3 (post-processing + GUI generation).

## Key state
- Pipeline version: HEAD (post-bug-fix, smoke-tested)
- Books: 204 (73 reruns + 131 new)
- Combined list: `scripts/step4_all_books.txt`
- Budget spent: EUR 9.70, estimated Phase D: ~EUR 20-30, remaining: ~EUR 60-70
- Rerun tracking: `tests/results/source_engine/phase_d/RERUN_BOOKS.json`
- Verification: `scripts/verify_step4_books.py` — all 6 checks PASS
- Source engine tests: 502 passed, 0 failures
