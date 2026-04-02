# `EX-C-003` Phase 2a Failure Packet — 2026-04-02

Purpose: capture the exact chunk set behind the second-ranked failure class in
`smoke_api_v2`: Phase 2a chunk failures that prevent downstream grouping and
excerpt generation.

## Scope

Books with explicit `phase2a_failures.jsonl` evidence:

- `ext_46_qa`: `1` failed chunk
- `ibn_aqil_v1`: `2` failed chunks
- `ibn_aqil_v3`: `1` failed chunk
- `taysir`: `4` failed chunks

Confirmed minimum total: `8` failed Phase 2a chunks.

## Evidence Paths

- `integration_tests/smoke_api_v2/ext_46_qa/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v1/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/ibn_aqil_v3/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/taysir/phase2a_failures.jsonl`
- `integration_tests/smoke_api_v2/analysis/campaign_summary.md`

## Failed Chunks

### ext_46_qa

- `div_src_test0001_3_006`
  - `word_count = 91`

### ibn_aqil_v1

- `div_src_test0001_2_000`
  - `word_count = 1397`
- `div_src_test0001_2_001`
  - `word_count = 1381`

### ibn_aqil_v3

- `div_src_test0001_4_008`
  - `word_count = 790`

### taysir

- `div_src_test0001_7_017`
  - `word_count = 495`
- `div_src_test0001_2_006_pre`
  - `word_count = 1236`
- `div_src_test0001_6_067`
  - `word_count = 524`
- `div_src_test0001_6_082`
  - `word_count = 816`

## Immediate Reading

These are not only tiny fringe chunks.

- `ibn_aqil_v1` lost two very large chunks (`1397` and `1381` words)
- `taysir` lost four mid-to-large chunks
- even the small `ext_46_qa` failure shows the failure class is not just “oversized prompt” by itself

That suggests the next serious fix lane should not assume a single size-only
threshold bug. Chunk content structure, schema fragility, or retry/error-path
handling may be involved.

## Next Useful Checks

1. Inspect the exact Phase 2a retry/error feedback path on these chunk ids.
2. Compare the failed chunks’ raw request/response artifacts against successful
   nearby chunks of similar size.
3. Use these chunk ids as the first regression fixture set for Phase 2a recovery
   hardening.
