# NEXT — Source Engine Pre-Batch Hardening

## Status: 4 mandatory fixes IMPLEMENTED (commit a8b17ff, 511 tests pass). Pre-batch hardening IN PROGRESS.

## Current step: STEP 1 — mypy crash fix handoff

Read `reference/PRE_BATCH_EXECUTION_PROTOCOL.md` for the full autonomous protocol.
Read `reference/PRE_BATCH_VERIFICATION_PLAN.md` for the technical details and evidence.

Execute STEP 1: Write the Claude Code handoff prompt for mypy crash fixes.

## Protocol summary

7 steps, mostly autonomous. Owner only needs to:
- Say "continue" between steps
- Run Claude Code when prompted (Steps 1, 5, 6)
- Confirm "looks good" when asked

## Key files

- `reference/PRE_BATCH_EXECUTION_PROTOCOL.md` — **THE PROTOCOL** — step-by-step with self-review
- `reference/PRE_BATCH_VERIFICATION_PLAN.md` — technical evidence and 5-layer plan
- `CLAUDE_CODE_POST_EVAL_FIXES.md` — the 4-fix handoff (COMPLETED, commit a8b17ff)

## Budget

- Spent: €30.10
- Remaining: ~€70
- Pre-batch verification: ~€1.50-2.00
- Final batch: ~€5-10
