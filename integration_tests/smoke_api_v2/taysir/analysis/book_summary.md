# Book Analysis: taysir

**Structural Status:** STRUCTURAL_FAIL
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 184 |
| Phase 2b units | 3107 |
| Final excerpts | 0 |
| Errors | 1 |

## Operational

- Total time: 28801.0s
- Total cost: EUR 42.8193
- LLM calls: 0

## Anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 3107 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-ZERO-OUTPUT** [structural_fail] (observed): Zero excerpts produced despite upstream processing activity
- **ANO-P2A-FAILURES** [structural_fail] (observed): 4 chunk(s) failed Phase 2a classification
- **ANO-P2B-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2b grouping

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** 0.0
- **phase1_chunk_count:** 184
- **phase2b_unit_count:** 3107
- **final_excerpt_count:** 0
- **unit_loss_count:** 3107
- **chunk_coverage_ratio:** 0.9728
- **truncation_count:** 0
- **zero_output_with_activity:** False
- **error_count:** 0

## Metrics: Operational

- **total_time_seconds:** 0
- **phase1_time_seconds:** 0
- **phase2a_time_seconds:** 0
- **phase2b_time_seconds:** 0
- **phase3_time_seconds:** 0
- **total_llm_cost:** 0
- **total_tokens_in:** 0
- **total_tokens_out:** 0
- **call_count_by_inferred_phase:** {}
- **call_count_by_model:** {}

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Pre-L-001 runs lack chunk_id in raw traces: the analyzer reads chunk_id from request JSON when present (post-L-001); for older run directories chunk_id is None (semantic phase inference unaffected).
