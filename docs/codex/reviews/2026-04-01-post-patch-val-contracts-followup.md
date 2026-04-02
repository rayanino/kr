# KR `val-contracts` Post-Patch Follow-Up

Date: 2026-04-01
Current stable Codex branch head: `46b46f81`
Authority: `active_authority: claude`
Runtime mode: `shadow_setup`

## Validated State

### A3 is closed

- `engines/excerpting/src/writer.py` no longer mutates `primary_text`
- `engines/excerpting/tests/test_writer.py` now enforces byte-identical preservation, including double/triple ZWNJ cases
- direct validation:
  - `engines/excerpting/tests/test_writer.py` → `25 passed`

### A2 is closed

- `engines/taxonomy/src/engine.py` now allows empty `excerpt_topic` only when `review_flags` contains `llm_enrichment_failed`
- `engines/taxonomy/tests/test_engine.py` now covers:
  - empty topic without flag → reject
  - empty topic with `llm_enrichment_failed` → accept
  - empty topic with unrelated flag → reject
- direct validation:
  - `engines/taxonomy/tests/test_engine.py` → `18 passed`

## Remaining Issue

### A1 is not cleanly partial/deferred yet

The patch documents the intended runtime contract, but the executable validation layer still points at legacy shapes:

- `engines/taxonomy/contracts_core.py` is now the authoritative runtime placement model
- `engines/synthesis/contracts.py` now defines `TaxonomyPlacedExcerpt`
- but `scripts/run_pipeline.py` still validates the taxonomy boundary against deprecated `PlacedExcerptAdditions`
- `tools/check_cross_engine_contracts.py` still ignores `contracts_core.py`
- `scripts/verify_metadata_flow.py` still reads SPEC text rather than runtime models

So A1 is not just “synthesis tracer deferred”. It is still internally inconsistent in the active validation/executable boundary layer.

## Highest-Value Next Fix

Claude should fix the executable `taxonomy -> synthesis` boundary and the local boundary validators, in this order:

1. `scripts/run_pipeline.py`
   - stop validating taxonomy output against deprecated `PlacedExcerptAdditions`
   - validate against the authoritative runtime taxonomy shape plus the synthesis-side `TaxonomyPlacedExcerpt`
   - stop treating `06_taxonomy_output.json` as the live taxonomy artifact if that file is tracer-era only
2. `tools/check_cross_engine_contracts.py`
   - inspect `contracts_core.py` in addition to `contracts.py`
   - compare real model/field surfaces, not just inline `Field(...)` constraints
3. `scripts/verify_metadata_flow.py`
   - stop using SPEC text as the operative boundary source of truth
   - use runtime contracts or explicit model-level field sets instead

## Do Not Reopen

Do not reopen these unless a fresh regression proves them broken:

- `engines/excerpting/src/writer.py`
- `engines/excerpting/tests/test_writer.py`
- `engines/taxonomy/src/engine.py`
- `engines/taxonomy/tests/test_engine.py`

## Claude Handoff Prompt

```text
Work from the current stable branch head and treat A2/A3 as already patched and directly validated.

Do not reopen the writer or taxonomy empty-topic fixes unless you find a concrete new regression.

Focus on the executable boundary inconsistency that remains after the patch:
- scripts/run_pipeline.py
- tools/check_cross_engine_contracts.py
- scripts/verify_metadata_flow.py

Goal:
1. align runtime validation to the authoritative taxonomy runtime shape (`contracts_core.py`)
2. align synthesis-side boundary validation to `TaxonomyPlacedExcerpt`
3. stop validating legacy tracer-era taxonomy shapes as if they were the active boundary

Constraints:
- keep A1 explicitly partial/deferred on the synthesis runtime consumer side
- do not pretend tracer alignment is complete
- do not touch Codex control-plane files in this pass
```
