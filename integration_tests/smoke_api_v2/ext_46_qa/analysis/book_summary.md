# Book Analysis: ext_46_qa

**Structural Status:** STRUCTURAL_FAIL
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 38 |
| Phase 2b units | 289 |
| Final excerpts | 277 |
| Errors | 13 |

## Operational

- Total time: 2761.8s
- Total cost: EUR 4.2960
- LLM calls: 0

## Anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 12 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-P2A-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2a classification

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** 0.9585
- **phase1_chunk_count:** 38
- **phase2b_unit_count:** 289
- **final_excerpt_count:** 277
- **unit_loss_count:** 12
- **chunk_coverage_ratio:** 0.9737
- **truncation_count:** 0
- **zero_output_with_activity:** False
- **error_count:** 13

## Metrics: Operational

- **total_time_seconds:** 2761.76
- **phase1_time_seconds:** 0.09
- **phase2a_time_seconds:** 736.6
- **phase2b_time_seconds:** 579.4
- **phase3_time_seconds:** 1445.65
- **total_llm_cost:** 0
- **total_tokens_in:** 0
- **total_tokens_out:** 0
- **call_count_by_inferred_phase:** {}
- **call_count_by_model:** {}

## Metrics: Review-Risk

- **partial_rate:** 0.3141
- **dependent_count:** 5
- **review_flag_count:** 5
- **gate_flag_count:** 5

## Metrics: Descriptive

- **function_distribution:** {"definition": 72, "rule_statement": 56, "opinion_statement": 69, "condition_exception": 10, "narration": 6, "evidence_rational": 11, "evidence_ijma": 3, "refutation": 13, "editorial_note": 5, "evidence_qiyas": 1, "example": 19, "structural_transition": 8, "cross_reference": 3, "evidence_hadith": 1}
- **self_containment_distribution:** {"FULL": 185, "PARTIAL": 87, "DEPENDENT": 5}
- **mean_excerpt_word_count:** 81.9
- **school_attribution_rate:** 0.0144
- **quoted_scholars_rate:** 0.7004

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Pre-L-001 runs lack chunk_id in raw traces: the analyzer reads chunk_id from request JSON when present (post-L-001); for older run directories chunk_id is None (semantic phase inference unaffected).
