# Protected State Divergence Note — 2026-04-02

Purpose: record control-plane or protected-file truth mismatches discovered
during unattended Codex work when the runtime is not allowed to edit the
protected source directly.

## Current Divergence

### `.kr/HANDOFF.md` still describes `L-001` as deferred

Current protected file:

- `.kr/HANDOFF.md`
  - says `L-001: chunk_id not in raw LLM traces`
  - says it is deferred and dormant until multi-chunk campaigns

Current analysis-layer source of truth:

- `scripts/excerpting_eval/KNOWN_LIMITATIONS.md`
  - says `L-001` is **fixed** on `2026-03-31`
  - documents the threaded `trace_context["chunk_id"]` change in:
    - `engines/excerpting/src/phase2_classify.py`
    - `engines/excerpting/src/phase2_group.py`
    - `scripts/run_integration_test.py`
    - `scripts/excerpting_eval/ingest.py`

## Operational Rule For Future Sessions

Until the protected handoff file is explicitly refreshed by an allowed lane,
treat the `L-001` status in `.kr/HANDOFF.md` as stale for excerpting-eval work.

Use:

- `scripts/excerpting_eval/KNOWN_LIMITATIONS.md`
- actual trace request artifacts containing `semantic_phase` and `chunk_id`

as the more current evidence for this specific limitation.

## Why This Note Exists

The unattended runtime must not edit `.kr/HANDOFF.md`, but it also must not let
stale protected state silently mislead the next serious session.
