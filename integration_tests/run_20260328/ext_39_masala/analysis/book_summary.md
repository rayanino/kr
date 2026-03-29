# Book Analysis: ext_39_masala

**Structural Status:** STRUCTURALLY_CLEAN
**Source ID:** src_test0001

## Pipeline Accounting

| Stage | Count |
|-------|-------|
| Phase 1 chunks | 16 |
| Phase 2b units | 14 |
| Final excerpts | 14 |
| Errors | 0 |

## Operational

- Total time: 128.7s
- Total cost: EUR 0.4163
- LLM calls: 4

## Metrics: Decision-Grade Structural

- **unit_yield_ratio:** 1.0
- **phase1_chunk_count:** 16
- **phase2b_unit_count:** 14
- **final_excerpt_count:** 14
- **unit_loss_count:** 0
- **chunk_coverage_ratio:** 0.0625
- **truncation_count:** 0
- **zero_output_with_activity:** False
- **error_count:** 0

## Metrics: Operational

- **total_time_seconds:** 128.71
- **phase1_time_seconds:** 0.02
- **phase2a_time_seconds:** 43.01
- **phase2b_time_seconds:** 42.04
- **phase3_time_seconds:** 43.64
- **total_llm_cost:** 0.416263
- **total_tokens_in:** 28957
- **total_tokens_out:** 11042
- **call_count_by_inferred_phase:** {"classification": 1, "grouping": 1, "enrichment": 1, "verification": 1}
- **call_count_by_model:** {"anthropic/claude-opus-4.6": 3, "openai/gpt-5.4": 1}

## Metrics: Review-Risk

- **partial_rate:** 0.1429
- **dependent_count:** 0
- **review_flag_count:** 0
- **gate_flag_count:** 0

## Metrics: Descriptive

- **function_distribution:** {"structural_transition": 1, "editorial_note": 1, "rule_statement": 12}
- **self_containment_distribution:** {"FULL": 12, "PARTIAL": 2}
- **mean_excerpt_word_count:** 98.6
- **school_attribution_rate:** 0.0
- **quoted_scholars_rate:** 0.3571

## LLM Trace Summary

| Call | Phase (inferred) | Model | Finish | Label Match |
|------|------------------|-------|--------|-------------|
| enrich_0001 | classification | anthropic/claude-opus-4.6 | stop | yes |
| enrich_0002 | grouping | anthropic/claude-opus-4.6 | stop | yes |
| enrich_0003 | enrichment | anthropic/claude-opus-4.6 | stop | yes |
| verify_0001 | verification | openai/gpt-5.4 | stop | yes |

## Observability Limitations

- EX-V-002 dropped unit identity unknown: processing_log records error codes but not affected unit indices. The analyzer correlates by count but cannot confirm the specific unit-to-error mapping.
- Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's classification fails, no output file is written. The analyzer detects absence but cannot distinguish 'not attempted' (--max-chunks) from 'attempted and failed silently'.
- Validation drops are not first-class artifacts: dropped units have no dedicated artifact. The analyzer infers drops from the gap between phase2b unit set and excerpt set.
- gate_queue verification not invoked by runner: gate_queue.jsonl is empty in all test books despite GATE_ON_* flags being true. The analyzer notes gate_count=0 but cannot determine if gates should have fired.
- Raw traces lack semantic phase and chunk_id: the analyzer infers semantic phase from request content via pattern matching. If prompt templates change, inference patterns must be updated.
- Retry vs multi-chunk ambiguity: repeated identical requests are classified as retries by content comparison, but if two different chunks had identical text, retries would be indistinguishable from separate chunk attempts.
