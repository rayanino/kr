# Structural Excerpt Report

Generated: `2026-03-31T16:16:31.251078+00:00`  Packages: `5`  Excerpts: `133`

## Overall

| Metric | Value |
| --- | ---: |
| Packages | 5 |
| Excerpts | 133 |
| Phase 2 teaching units | 137 |
| Validation drops | 4 |
| Gate queue entries | 13 |
| Consensus records | 42 |

## Check Summary

| Check | Status | Findings |
| --- | --- | ---: |
| Required Fields | `pass` | 0 |
| Word Offset Consistency | `pass` | 0 |
| text_snippet Prefix Match | `pass` | 0 |
| segment_indices Validity | `pass` | 0 |
| excerpt_id Format | `pass` | 0 |
| Empty Field Detection | `pass` | 0 |
| Consensus Structure | `pass` | 0 |
| ZWNJ Scan | `warn` | 8 |
| Duplicate Detection | `fail` | 10 |
| Gate Cross-Reference | `pass` | 0 |
| Short/Long Outliers | `warn` | 9 |
| author_id Audit | `warn` | 133 |
| Consensus Coverage | `pass` | 0 |
| Physical Pages | `pass` | 0 |
| Function Taxonomy Validation | `pass` | 0 |

## Key Findings

- Duplicate excerpt IDs: `10` keys across `20` records.
- `author_id` sentinel `unknown`: `133` of `133` excerpts.
- ZWNJ-bearing excerpts: `8` with `36` total U+200C occurrences.
- Word-count outliers: `3` short and `6` long.

## Per-Check Details

### Required Fields

Status: `pass`

Top-level required ExcerptRecord fields are present and each record validates against the Pydantic contract.

| Metric | Value |
| --- | --- |
| `required_field_count` | `16` |
| `required_fields` | `["chunk_index", "description_arabic", "div_id", "div_path", "end_word", "excerpt_id", "excerpt_topic", "primary_author_layer", "primary_function", "primary_text", "school", "self_containment", "source_id", "start_word", "text_snippet", "unit_index"]` |
| `records_evaluated` | `133` |

No findings.

### Word Offset Consistency

Status: `pass`

start_word/end_word resolve to the exact primary_text substring and agree with the Phase 2 grouping boundaries.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### text_snippet Prefix Match

Status: `pass`

Whitespace-normalized first 80 characters of primary_text match text_snippet per SPEC V-P3-2.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### segment_indices Validity

Status: `pass`

segment_indices are non-empty, contiguous, ascending, and match Phase 2 unit/segment provenance.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### excerpt_id Format

Status: `pass`

excerpt_id exactly matches exc_{source_id}_{div_id}_{chunk_index}_{unit_index}.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### Empty Field Detection

Status: `pass`

Required structural strings are non-blank and required collections are not empty when the SPEC expects content.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### Consensus Structure

Status: `pass`

consensus_metadata is structurally valid and internally coherent when present.

| Metric | Value |
| --- | --- |
| `records_with_consensus_metadata` | `42` |
| `decision_type_counts` | `{"author_attribution": 12, "school_attribution": 11, "self_containment": 24}` |

No findings.

### ZWNJ Scan

Status: `warn`

Invisible U+200C characters are inventoried across excerpt fields for follow-up review.

| Metric | Value |
| --- | --- |
| `excerpt_count_with_zwnj` | `8` |
| `total_zwnj_occurrences` | `36` |
| `field_occurrence_counts` | `{"primary_text": 18, "text_snippet": 16, "cross_references.1.reference_text": 2}` |

Sample findings:
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_3_000_pre_0_6: U+200C detected in excerpt payload.
- `warning` ibn_aqil_v1 / exc_src_test0001_div_src_test0001_2_000_0_0: U+200C detected in excerpt payload.
- `warning` ibn_aqil_v1 / exc_src_test0001_div_src_test0001_2_001_0_1: U+200C detected in excerpt payload.
- `warning` ibn_aqil_v3 / exc_src_test0001_div_src_test0001_3_000_0_0: U+200C detected in excerpt payload.
- `warning` ibn_aqil_v3 / exc_src_test0001_div_src_test0001_3_001_0_0: U+200C detected in excerpt payload.
- `warning` taysir / exc_src_test0001_div_src_test0001_7_000_0_1: U+200C detected in excerpt payload.

### Duplicate Detection

Status: `fail`

Duplicate excerpt IDs, duplicate coordinate keys, and duplicate normalized primary_text bodies are detected across the corpus.

| Metric | Value |
| --- | --- |
| `duplicate_excerpt_id_count` | `10` |
| `duplicate_excerpt_instances` | `20` |
| `duplicate_coordinate_key_count` | `10` |
| `duplicate_primary_text_count` | `0` |

Sample findings:
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_0: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_1: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_2: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_3: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_4: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_5: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_6: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_7: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_8: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_0_9: Duplicate excerpt_id detected across the smoke corpus.

### Gate Cross-Reference

Status: `pass`

gate_flags and gate_queue.jsonl entries agree in both directions within each package.

| Metric | Value |
| --- | --- |
| `records_with_gate_flags` | `13` |
| `gate_queue_entry_count` | `13` |

No findings.

### Short/Long Outliers

Status: `warn`

Word-count outliers are reported using a hybrid short-threshold plus Tukey upper-fence audit.

| Metric | Value |
| --- | --- |
| `min_word_count` | `4` |
| `median_word_count` | `86` |
| `max_word_count` | `555` |
| `q1_word_count` | `51.0` |
| `q3_word_count` | `163.0` |
| `iqr_word_count` | `112.0` |
| `upper_fence` | `331.0` |
| `short_threshold_words` | `10` |
| `short_outlier_count` | `3` |
| `long_outlier_count` | `6` |

Sample findings:
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_0: Long word-count outlier.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_3_000_pre_0_6: Short word-count outlier.
- `warning` ibn_aqil_v1 / exc_src_test0001_div_src_test0001_2_000_0_5: Long word-count outlier.
- `warning` ibn_aqil_v1 / exc_src_test0001_div_src_test0001_2_001_0_0: Short word-count outlier.
- `warning` ibn_aqil_v1 / exc_src_test0001_div_src_test0001_2_001_0_4: Long word-count outlier.
- `warning` taysir / exc_src_test0001_div_src_test0001_6_000_0_12: Long word-count outlier.
- `warning` taysir / exc_src_test0001_div_src_test0001_6_000_0_16: Long word-count outlier.
- `warning` taysir / exc_src_test0001_div_src_test0001_6_000_0_19: Long word-count outlier.
- `warning` taysir / exc_src_test0001_div_src_test0001_7_000_0_0: Short word-count outlier.

### author_id Audit

Status: `warn`

primary_author_layer.author_id values are inventoried, including sentinel values such as unknown.

| Metric | Value |
| --- | --- |
| `unique_author_id_count` | `1` |
| `author_id_counts` | `{"unknown": 133}` |
| `unknown_author_id_count` | `133` |

Sample findings:
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_0: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_1: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_2: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_3: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_4: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_5: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_6: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_7: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_8: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_9: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_10: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_11: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_1: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_2: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_3: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_4: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_5: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_6: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_7: primary_author_layer.author_id uses the sentinel value unknown.

### Consensus Coverage

Status: `pass`

Records with consensus-only signals always carry consensus_metadata, and decision types are summarized.

| Metric | Value |
| --- | --- |
| `records_with_consensus_metadata` | `42` |
| `records_with_consensus_signals` | `16` |
| `decision_type_counts` | `{"author_attribution": 12, "school_attribution": 11, "self_containment": 24}` |

No findings.

### Physical Pages

Status: `pass`

physical_pages matches the page span implied by Phase 1 join points and token-derived character ranges.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |

No findings.

### Function Taxonomy Validation

Status: `pass`

All function fields are valid ScholarlyFunction values and agree with Phase 2 provenance.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `133` |
| `valid_function_count` | `16` |
| `valid_functions` | `["condition_exception", "cross_reference", "definition", "editorial_note", "evidence_hadith", "evidence_ijma", "evidence_qiyas", "evidence_quran", "evidence_rational", "example", "narration", "opinion_statement", "refutation", "rule_statement", "structural_transition", "unclassified"]` |

No findings.

## Package Summary

| Package | Excerpts | Gate Entries | Validation Drops |
| --- | ---: | ---: | ---: |
| ext_39_masala | 22 | 0 | 0 |
| ext_46_qa | 20 | 0 | 1 |
| ibn_aqil_v1 | 19 | 0 | 0 |
| ibn_aqil_v3 | 44 | 12 | 0 |
| taysir | 28 | 1 | 3 |
