> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Pinned strategic reminder — do not lose this

A benchmark-quality owner example was recorded on 2026-04-03 and must be revisited during the next serious planning/frontier-selection cycle, even if the owner forgets to bring it up explicitly.

Reference brief:
- `docs/codex/2026-04-03-golden-example-multiresolution-digester.md`

What it is:
- not a default implementation request
- a gold-standard benchmark for the kind of autonomous, high-leverage idea generation the KR system should eventually produce on its own

Current benchmark conclusion:
- the live system does **not** yet reach this level of reasoning
- coworker-backed architectural conclusion: if this ever becomes an implementation target, the primary insertion boundary is excerpting Phase 2b → Phase 3/output, with taxonomy as the secondary required contract change

This note does not replace `ACTIVE.md`. It is a pinned strategic memory item for the next Claude-led planning conversation.

## Session purpose
Build the excerpting evaluation layer v1 and patch all observability gaps in the runner.

## What this session completed

### Evaluation layer (8 new files)
- `scripts/excerpting_eval/{__init__, models, ingest, analysis, packet}.py` — shared module
- `scripts/analyze_excerpting_run.py` — per-book analyzer
- `scripts/analyze_excerpting_campaign.py` — campaign aggregator
- `scripts/export_excerpting_review_packet.py` — review packet exporter

### Runner observability patches (2 files modified)
- `scripts/run_integration_test.py` — failure ledgers, validation drops, gate verification, trace metadata, call-level error propagation
- `engines/excerpting/src/phase3_orchestrator.py` — `Phase3Result.validation_drops` field + set-diff computation

### Analyzer bug fix
- `scripts/excerpting_eval/packet.py` — book-level key collision fixed (B1)

### Analyzer upgrades for new artifacts
- Consumes `validation_drops.jsonl` → upgrades evidence to OBSERVED
- Consumes `phase2a/2b_failures.jsonl` → new `detect_phase_failures` detector
- Reads `semantic_phase` from trace requests when present → skips content inference

## All 6 regression checks pass
1. taysir grouped-unit loss (indices [2, 9]) — detected
2. ibn_aqil_v3 zero-output — detected
3. truncation finish_reason=length — detected
4. client-label ambiguity — no false anomaly
5. semantic phase inference — 4/4 correct
6. clean books — 3/3 STRUCTURALLY_CLEAN

808 excerpting engine tests pass, 0 failures.

## Deferred flaw: L-001

**chunk_id not in raw LLM traces.** The runner sets `semantic_phase` but cannot set `chunk_id` because phase functions iterate internally. Requires threading `trace_context` through `run_phase2a` → `classify_chunk` and `run_phase2b` → `group_chunk`.

**Documented in:** `scripts/excerpting_eval/KNOWN_LIMITATIONS.md`
**When to fix:** Before the first campaign that processes >1 chunk per book. The current test data uses 1 chunk per book, so this is dormant.
**Impact if unfixed:** Analyzer infers chunk association from call sequence — works but fragile for multi-chunk runs.

## Current resume point
Resume from `ACTIVE.md`. The frontier is completed. Owner decision needed on next frontier.
