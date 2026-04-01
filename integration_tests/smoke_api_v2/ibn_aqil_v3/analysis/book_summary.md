# Book Analysis: ibn_aqil_v3

**Structural Status:** STRUCTURAL_FAIL
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 28 |
| Phase 2b units | 283 |
| Final excerpts | 278 |
| Errors | 6 |

## Operational

- Total time: 2669.5s
- Total cost: EUR 4.2977
- LLM calls: 0

## Anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 5 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-P2A-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2a classification

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** 0.9823
- **phase1_chunk_count:** 28
- **phase2b_unit_count:** 283
- **final_excerpt_count:** 278
- **unit_loss_count:** 5
- **chunk_coverage_ratio:** 0.9643
- **truncation_count:** 0
- **zero_output_with_activity:** False
- **error_count:** 6

## Metrics: Operational

- **total_time_seconds:** 2669.51
- **phase1_time_seconds:** 0.05
- **phase2a_time_seconds:** 1023.39
- **phase2b_time_seconds:** 583.57
- **phase3_time_seconds:** 1062.49
- **total_llm_cost:** 0
- **total_tokens_in:** 0
- **total_tokens_out:** 0
- **call_count_by_inferred_phase:** {}
- **call_count_by_model:** {}

## Metrics: Review-Risk

- **partial_rate:** 0.1978
- **dependent_count:** 1
- **review_flag_count:** 48
- **gate_flag_count:** 1

## Metrics: Descriptive

- **function_distribution:** {"structural_transition": 2, "definition": 43, "rule_statement": 178, "example": 1, "opinion_statement": 26, "condition_exception": 26, "refutation": 1, "cross_reference": 1}
- **self_containment_distribution:** {"FULL": 222, "PARTIAL": 55, "DEPENDENT": 1}
- **mean_excerpt_word_count:** 88.0
- **school_attribution_rate:** 0.0
- **quoted_scholars_rate:** 0.3849

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Pre-L-001 runs lack chunk_id in raw traces: the analyzer reads chunk_id from request JSON when present (post-L-001); for older run directories chunk_id is None (semantic phase inference unaffected).
