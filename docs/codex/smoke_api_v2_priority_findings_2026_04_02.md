# Smoke API V2 Priority Findings — 2026-04-02

Source set:

- `integration_tests/smoke_api_v2/analysis/campaign_summary.md`
- per-book `integration_tests/smoke_api_v2/*/analysis/book_summary.md`
- runtime notes from the failed `taysir` package

## Priority 1: `EX-V-002` Post-Grouping Validation Drops

Why first:

- present in all 5 books
- directly destroys already-processed units after the expensive upstream work is done
- ranges from small leaks in successful books to total collapse in `taysir`

Evidence:

- `integration_tests/smoke_api_v2/analysis/campaign_summary.md`
  - recurring anomaly pattern: `grouped_unit_loss` in all books
- packet: `docs/codex/ex_v002_drop_packet_2026_04_02.md`
- repair map: `docs/codex/ex_v002_repair_map_2026_04_02.md`
- `integration_tests/smoke_api_v2/ext_39_masala/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ext_46_qa/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v1/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v3/validation_drops.jsonl`
- `integration_tests/smoke_api_v2/taysir/analysis/book_summary.md`
  - `ANO-UNIT-LOSS`: `3107` grouped units lost
- `integration_tests/smoke_api_v2/ext_46_qa/analysis/book_summary.md`
  - `ANO-UNIT-LOSS`: `12` grouped units lost

Interpretation:

This is the highest-leverage failure class because it burns Phase 1, Phase 2a,
and Phase 2b work but still loses units before final output.

## Priority 2: `EX-C-003` Phase 2a Chunk Failures

Why second:

- present in 4 of 5 books
- each failing chunk removes an entire upstream branch from the pipeline
- fixing this improves coverage before the expensive later phases

Evidence:

- `integration_tests/smoke_api_v2/analysis/campaign_summary.md`
  - recurring anomaly pattern: `phase2a_chunk_failures`
- packet: `docs/codex/ex_c003_phase2a_failure_packet_2026_04_02.md`
- repair map: `docs/codex/ex_c003_repair_map_2026_04_02.md`
- `integration_tests/smoke_api_v2/ext_46_qa/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/taysir/analysis/book_summary.md`
  - `ANO-P2A-FAILURES`: `4` chunks failed Phase 2a
- `integration_tests/smoke_api_v2/ibn_aqil_v1/analysis/book_summary.md`
  - `ANO-P2A-FAILURES`: `2` chunks failed Phase 2a
- `integration_tests/smoke_api_v2/ibn_aqil_v1/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v3/phase2a_failures.jsonl`

Interpretation:

This is the next most leverage-rich lane because every recovered chunk improves
coverage and lowers downstream ambiguity.

## Priority 3: `taysir` Long-Run Timeout / Incomplete Finalization

Why third:

- localized to one book, but it is the most expensive and operationally severe failure
- proves the current pipeline/runtime combination still breaks at larger scale
- blocks the weekend handoff’s `taysir`-dependent tasks entirely

Evidence:

- packet: `docs/codex/taysir_scale_collapse_packet_2026_04_02.md`
- `integration_tests/smoke_api_v2/taysir/analysis/book_summary.md`
  - `ANO-ZERO-OUTPUT`
  - `ANO-P2B-FAILURES`
  - `ANO-UNIT-LOSS`
- `docs/codex/taysir_timeout_analysis_2026_04_02.md`
  - package timed out during `phase3_consensus`
- `docs/codex/taysir_verify_tail_analysis_2026_04_02.md`
  - missing verifier response `verify_0124`

Interpretation:

This is the highest operational-risk failure, but it should be attacked after
or alongside the broader unit-loss and Phase 2a robustness issues, because the
shared failure classes likely contribute to the collapse.

## Suggested Execution Order

1. Reduce grouped unit loss and validation-drop leakage.
2. Reduce Phase 2a chunk failures.
3. Revisit the `taysir` timeout/scale-collapse path with the new runtime diagnostics in place.
