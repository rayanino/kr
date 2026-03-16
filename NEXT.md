# NEXT — Source Engine Pre-Batch Hardening

## Status: 4 mandatory fixes IMPLEMENTED (commit a8b17ff, 511 tests pass). Pre-batch verification PENDING.

## What happened

204 books processed. 4-layer evaluation complete. GO verdict with 4 mandatory fixes — all implemented:
- **Fix 1:** Added `rihlah` and `usul_al_fiqh` to Genre enum, prompt, synonyms, SPEC. Added `validate_enum_value` logging.
- **Fix 2:** Escalated hashiyah+ML=False+no_layers to gate severity. Added gate handler.
- **Fix 3:** Added `death_date_single_model` field, single-model death date warning (check 5g), and fixed pre-existing `needs_review_fields` merge gap in engine.py.
- **Fix 4:** Documented compiler-as-muhaqiq pattern in SPEC_CORE.md and OPEN_PROBLEMS.md.

Post-fix analysis discovered additional issues that must be resolved BEFORE the final batch:
- **37 mypy type errors** including crash risks in consensus.py (None-access on genre_chain) and engine.py (Optional field passed as non-Optional)
- **Contract boundary gaps** at source→normalization boundary (22 fields flagged by verify_metadata_flow.py, most suspected false positives but need verification)
- **SPEC consistency** needs audit after the 4 fix modifications
- **Zero end-to-end fix validation** — unit tests pass but no book has been run through the fixed pipeline

## Current task — READ THIS FIRST

**`reference/PRE_BATCH_VERIFICATION_PLAN.md`** — the governing document for this phase.

Five layers, ordered by cost-effectiveness:
1. **Fix mypy crash risks** (€0, Claude Code) — consensus.py None-access, engine.py type mismatches
2. **Contract boundary verification** (€0, Claude Chat) — confirm source output matches normalization input expectations
3. **SPEC consistency audit** (€0, Claude Chat) — verify SPEC matches code after 4 fixes
4. **Targeted end-to-end validation** (~€1.50, run 4-5 specific books) — validate each fix works in production
5. **Batch design decisions** (€0, Claude Chat + owner) — book selection, downstream consumption, flag rate

After all 5 layers: final batch (~€5-10, ~50 new books per ENGINE TRANSITION rule).

## Key files

- `reference/PRE_BATCH_VERIFICATION_PLAN.md` — **START HERE** — the pre-batch hardening plan
- `CLAUDE_CODE_POST_EVAL_FIXES.md` — the 4-fix handoff (COMPLETED)
- `PHASE_D_CRITICAL_REVIEW.md` — adversarial review of the evaluation
- `PHASE_D_AGGREGATION_REPORT.md` — original GO verdict
- `reference/ENGINE_FACTORY_PLAN.md` — post-source-engine autonomous build system (for after source engine is done)

## Budget

- Spent: €30.10
- Remaining: ~€70
- Pre-batch verification: ~€1.50-2.00
- Final batch: ~€5-10
- Normalization engine: ~€20-30
