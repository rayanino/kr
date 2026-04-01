# Taysir Scale-Collapse Packet — 2026-04-02

Purpose: capture the third-ranked but highest-severity operational failure in
`smoke_api_v2`: the `taysir` package consumed most of the campaign cost/time,
timed out deep in consensus, and produced zero final excerpts.

## Core Facts

- package: `integration_tests/smoke_api_v2/taysir`
- final status: `error`
- final error: `batch_timeout: exceeded 28800s in batch runner`
- elapsed time: `28800.96s`
- cost: `42.819313`
- final excerpts: `0`

## Upstream Progress Reached

From `progress.jsonl`:

- `phase2a`: `180` done / `4` failed
- `phase2b`: `179` done / `1` failed
- `phase3_enrich`: `179` done
- `phase3_consensus`: `124` done

Last completed consensus entry:

- `div_src_test0001_6_083` at `2026-04-01T16:17:47.154918+00:00`

## Failure Signature

- `verify_0124.json` request exists
- no matching `verify_0124.json` response artifact exists
- responses stop at `verify_0123.json`
- the batch runner later records the timeout and kills the child process

## Primary Evidence Paths

- `integration_tests/smoke_api_v2/SUMMARY.json`
- `integration_tests/smoke_api_v2/taysir/run_metadata.json`
- `integration_tests/smoke_api_v2/taysir/progress.jsonl`
- `integration_tests/smoke_api_v2/taysir/STALL_REPORT.md`
- `integration_tests/smoke_api_v2/taysir/analysis/book_summary.md`
- `docs/codex/taysir_timeout_analysis_2026_04_02.md`
- `docs/codex/taysir_verify_tail_analysis_2026_04_02.md`

## Why It Matters

This is the most expensive single failure in the weekend run and it blocks all
`taysir`-dependent handoff work:

- CJ-2 / CJ-3 filling
- `V2_TAYSIR_REVIEW.md`
- before/after regression work that depends on the new `taysir` output

## Immediate Reading

This does **not** look like a trivial “writer failed after everything else
completed” case.

The package got deep into consensus verification and then lost the race against
the parent timeout while still upstream of final excerpt writing.

## Next Useful Checks

1. Use the new timeout trace-health reporting on future timed-out runs.
2. Keep `taysir` isolated from successful-book analysis until a valid
   `excerpts.jsonl` exists.
3. When engine work reopens, pair this packet with the `EX-V-002` and
   `EX-C-003` packets to avoid treating the `taysir` collapse as a single
   isolated mystery.
