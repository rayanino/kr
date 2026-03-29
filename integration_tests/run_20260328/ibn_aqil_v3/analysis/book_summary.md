# Book Analysis: ibn_aqil_v3

**Structural Status:** STRUCTURAL_FAIL
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 28 |
| Phase 2b units | 0 |
| Final excerpts | 0 |
| Errors | 0 |

## Operational

- Total time: 725.7s
- Total cost: EUR 1.4887
- LLM calls: 6

## Anomalies

- **ANO-ZERO-OUTPUT** [structural_fail] (observed): Zero excerpts produced despite upstream processing activity
- **ANO-TRUNCATION** [structural_fail] (observed): 6 LLM response(s) truncated (finish_reason=length)
- **ANO-CONTRADICTION** [structural_fail] (inferred_high_confidence): Zero output + zero logged errors despite substantial activity

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** None
- **phase1_chunk_count:** 28
- **phase2b_unit_count:** 0
- **final_excerpt_count:** 0
- **unit_loss_count:** 0
- **chunk_coverage_ratio:** 0.0
- **truncation_count:** 6
- **zero_output_with_activity:** True
- **error_count:** 0

## Metrics: Operational

- **total_time_seconds:** 725.68
- **phase1_time_seconds:** 0.03
- **phase2a_time_seconds:** 725.64
- **phase2b_time_seconds:** 0.0
- **phase3_time_seconds:** 0.0
- **total_llm_cost:** 1.48872
- **total_tokens_in:** 51984
- **total_tokens_out:** 49152
- **call_count_by_inferred_phase:** {"classification": 6}
- **call_count_by_model:** {"anthropic/claude-opus-4.6": 6}

## LLM Trace Summary

| Call | Phase (inferred) | Model | Finish | Label Match |
|------|------------------|-------|--------|-------------|
| enrich_0001 | classification | anthropic/claude-opus-4.6 | length | yes |
| enrich_0002 | classification | anthropic/claude-opus-4.6 | length | yes |
| enrich_0003 | classification | anthropic/claude-opus-4.6 | length | yes |
| enrich_0004 | classification | anthropic/claude-opus-4.6 | length | yes |
| enrich_0005 | classification | anthropic/claude-opus-4.6 | length | yes |
| enrich_0006 | classification | anthropic/claude-opus-4.6 | length | yes |

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Raw traces lack semantic phase and chunk_id: the analyzer infers semantic phase from request content via pattern matching. If prompt templates change, inference patterns must be updated.
- Retry vs multi-chunk ambiguity: repeated identical requests are classified as retries by content comparison, but if two different chunks had identical text, retries would be indistinguishable from separate chunk attempts.
