# Book Analysis: ext_39_masala

**Structural Status:** STRUCTURAL_FAIL
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 16 |
| Phase 2b units | 203 |
| Final excerpts | 200 |
| Errors | 3 |

## Operational

- Total time: 2301.8s
- Total cost: EUR 3.2735
- LLM calls: 0

## Anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 3 grouped unit(s) lost between Phase 2b and final excerpts

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** 0.9852
- **phase1_chunk_count:** 16
- **phase2b_unit_count:** 203
- **final_excerpt_count:** 200
- **unit_loss_count:** 3
- **chunk_coverage_ratio:** 1.0
- **truncation_count:** 0
- **zero_output_with_activity:** False
- **error_count:** 3

## Metrics: Operational

- **total_time_seconds:** 2301.76
- **phase1_time_seconds:** 0.04
- **phase2a_time_seconds:** 446.8
- **phase2b_time_seconds:** 571.72
- **phase3_time_seconds:** 1283.19
- **total_llm_cost:** 0
- **total_tokens_in:** 0
- **total_tokens_out:** 0
- **call_count_by_inferred_phase:** {}
- **call_count_by_model:** {}

## Metrics: Review-Risk

- **partial_rate:** 0.38
- **dependent_count:** 3
- **review_flag_count:** 5
- **gate_flag_count:** 3

## Metrics: Descriptive

- **function_distribution:** {"editorial_note": 2, "rule_statement": 131, "condition_exception": 24, "evidence_rational": 3, "evidence_hadith": 27, "definition": 4, "opinion_statement": 1, "structural_transition": 5, "refutation": 3}
- **self_containment_distribution:** {"FULL": 121, "PARTIAL": 76, "DEPENDENT": 3}
- **mean_excerpt_word_count:** 94.6
- **school_attribution_rate:** 0.045
- **quoted_scholars_rate:** 0.685

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Pre-L-001 runs lack chunk_id in raw traces: the analyzer reads chunk_id from request JSON when present (post-L-001); for older run directories chunk_id is None (semantic phase inference unaffected).
