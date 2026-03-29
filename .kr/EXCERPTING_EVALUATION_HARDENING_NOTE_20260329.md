> Purpose: Preserve the hardened implementation conclusions from the deep review session without losing them before the next repo-writing session updates the primary control files.
> Status: active supplement.
> Authority rule: This note does not override `.kr/ACTIVE.md`, but it is the authoritative supplement for excerpting-evaluation implementation semantics until the primary control files are updated again.

# Excerpting Evaluation Hardening Note — 2026-03-29

## Why this note exists
A deep aspect-by-aspect hardening review was completed after the original excerpting evaluation brief and active-frontier update. That review confirmed the frontier, but tightened several implementation rules that must not be lost.

## What changed conceptually
The frontier is still: build analyzer v1, campaign aggregation, and the first review-packet exporter.

However, the implementation must now follow these corrections:
- use a canonical per-unit ledger keyed by `(source_id, div_id, chunk_index, unit_index)`;
- separate observed facts from inferred causes;
- use machine structural status first (`STRUCTURAL_FAIL`, `STRUCTURAL_CONCERN`, `STRUCTURALLY_CLEAN`) rather than final scholarly `PASS / CONCERN / FAIL`;
- infer semantic phase from raw request structure first, not from client/file prefixes like `enrich_0001.json`;
- tier metrics by authority so weak heuristic or LLM-enriched metrics do not directly drive structural status;
- require review packets to include sentinel audit sampling and stratified positive controls, not anomaly-only selections.

## Important correction from the review
The earlier assumption that a file like `raw_llm_responses/enrich_0001.json` represented a mislabeled enrichment-stage call was too strong. In the current runner, the shared `enrich_client` is used for classification, grouping, and enrichment, so the filename prefix is a client label, not an authoritative stage label. This means the analyzer must treat such prefixes as ambiguous metadata and infer true semantic phase from request content.

## Required companion artifact
Use `reference/EXCERPTING_EVALUATION_HARDENING_PACK.md` as the detailed implementation supplement. That file contains:
- the hardened contract,
- the exact implementation prompt,
- the corrected regression checks,
- and the acceptance checklist.

## Safe next move
The next implementation session should stay standalone and post-run. It should build:
- `scripts/analyze_excerpting_run.py`
- `scripts/analyze_excerpting_campaign.py`
- `scripts/export_excerpting_review_packet.py`

and prove them on `integration_tests/run_20260328/` before any dashboard work or deeper engine wiring.

## Known observability cautions
The analyzer must stay conservative because current artifacts still have limits:
- failed Phase 2a / Phase 2b chunks may disappear without a dedicated failure ledger;
- validation drops are not persisted as first-class artifacts;
- `verify_gate_queue()` exists but is not currently invoked by the runner;
- raw traces do not explicitly store semantic phase or chunk ID.

These do not block analyzer v1, but they do block overconfident claims.