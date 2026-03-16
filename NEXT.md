# NEXT — Post-Evaluation Fixes

## Status: GO verdict confirmed. 4 mandatory fixes ready for Claude Code implementation. See `CLAUDE_CODE_POST_EVAL_FIXES.md`.

## What happened

204 books processed. 4-layer evaluation complete (programmatic + pattern analysis + 60 per-book + aggregation). GO verdict issued with 3 mandatory fixes. Adversarial critical review (`PHASE_D_CRITICAL_REVIEW.md`) expanded to 4 mandatory fixes. Domain questions resolved.

## Current task: Implement 4 mandatory fixes

Claude Code reads `CLAUDE_CODE_POST_EVAL_FIXES.md` — contains precise file-by-file specifications based on actual code investigation.

**Fix 1 — Missing Genre Values:** Add `rihlah` and `usul_al_fiqh` to Genre enum, prompt, synonyms. Root cause: valid LLM output was silently discarded by enum validation fallback to "other".

**Fix 2 — ERR-01 hashiyah validation:** Escalate hashiyah+ML=False+no_layers from severity="warning" to severity="gate". Hashiyah structurally requires 3 layers, so this is always contradictory.

**Fix 3 — ERR-03 death date warning:** Add validation warning when death date comes from single-model inference only (other model abstained). Requires adding `death_date_single_model` field to MetadataInferenceResult and injecting it into validation data dict.

**Fix 4 — ERR-02 documentation:** Document the compiler-as-muhaqiq pattern in SPEC_CORE.md and OPEN_PROBLEMS.md. No code changes.

## After fixes

1. Run full test suite — all existing tests must pass + new tests
2. Commit and push
3. Final batch through source engine (per ENGINE TRANSITION rule) → produce structured input for normalization engine
4. Begin normalization engine SPEC design

## Key files

- `CLAUDE_CODE_POST_EVAL_FIXES.md` — THE handoff prompt for Claude Code (read this)
- `PHASE_D_CRITICAL_REVIEW.md` — adversarial review of the evaluation
- `PHASE_D_AGGREGATION_REPORT.md` — original GO verdict
- `PHASE_D_SESSION_ERRATA.md` — evaluation methodology lessons

## Budget

- Spent: €30.10
- Remaining: ~€70
- Fix implementation: ~€0 (no API calls)
- Final batch: ~€10-15
- Normalization engine: ~€20-30
