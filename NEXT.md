# NEXT — Source Engine Pre-Batch Hardening

## Current position: STEP 3 — Subtask 3C
## What to do: Critical review and gap resolution — cross-reference source output (3A) with normalization expectations (3B), resolve specific questions, write CONTRACT_VERIFICATION_REPORT.md
## Context: Steps 1-2 complete. 3A mapped source output (56 fields + 3 runner). 3B mapped normalization inputs (8 declared + 2 undeclared). Key findings: 2 field name mismatches (multi_layer→is_multi_layer, layers→text_layers), 1 enum mismatch (TextFidelity unknown vs very_low), 1 unlisted dependency (page_count for §5 check 2), work_id declared but unused in code.
## Owner action needed: No — Claude Chat executes this subtask

Read `reference/PRE_BATCH_EXECUTION_PROTOCOL.md` — the governing protocol (Step 3 instructions).

## Budget

- Spent: €30.10
- Remaining: ~€70
