> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

# KR Active Frontier

Status: completed — ready for next frontier

## Previous frontier (completed 2026-03-29)
Build the excerpting evaluation layer v1 (analyzer, campaign aggregator, review-packet exporter) and patch all 6 observability gaps in the runner.

## What was delivered

### Evaluation layer (8 files)
- `scripts/excerpting_eval/` shared module (models, ingest, analysis, packet)
- `scripts/analyze_excerpting_run.py` — per-book analyzer
- `scripts/analyze_excerpting_campaign.py` — campaign aggregator
- `scripts/export_excerpting_review_packet.py` — review packet exporter

### Observability patches (5 of 6 gaps closed)
- Runner emits `phase2a_failures.jsonl` and `phase2b_failures.jsonl` (failure ledgers)
- Runner emits `validation_drops.jsonl` with per-unit drop identity
- Runner invokes `verify_gate_queue()` after writing gate entries
- Runner annotates raw traces with `semantic_phase` metadata
- Runner propagates call-level LLM errors to processing_log

### Deferred (1 gap remaining)
- **L-001:** `chunk_id` not in raw traces — requires engine-level change to thread context through `run_phase2a` → `classify_chunk`. See `scripts/excerpting_eval/KNOWN_LIMITATIONS.md`. Fix before first multi-chunk campaign.

## Recommended next frontier
1. **Run the real 5-book excerpting campaign** — the evaluation layer and observability are ready.
2. **Fix L-001 (chunk_id in traces)** — if multi-chunk processing is imminent.
3. **Calibrate concern thresholds** — using campaign data.

## Relevant decisions
- OPS-DEC-001 through OPS-DEC-005
