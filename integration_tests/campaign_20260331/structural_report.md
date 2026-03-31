# Structural Excerpt Report

Generated: `2026-03-31T19:58:34.877631+00:00`  Packages: `5`  Excerpts: `2303`

## Overall

| Metric | Value |
| --- | ---: |
| Packages | 5 |
| Excerpts | 2303 |
| Phase 2 teaching units | 2487 |
| Validation drops | 184 |
| Gate queue entries | 65 |
| Consensus records | 788 |

## Check Summary

| Check | Status | Findings |
| --- | --- | ---: |
| Required Fields | `pass` | 0 |
| Word Offset Consistency | `fail` | 124 |
| text_snippet Prefix Match | `fail` | 1135 |
| segment_indices Validity | `fail` | 208 |
| excerpt_id Format | `pass` | 0 |
| Empty Field Detection | `pass` | 0 |
| Consensus Structure | `pass` | 0 |
| ZWNJ Scan | `warn` | 100 |
| Duplicate Detection | `fail` | 192 |
| Gate Cross-Reference | `fail` | 3 |
| Short/Long Outliers | `warn` | 172 |
| author_id Audit | `warn` | 2302 |
| Consensus Coverage | `pass` | 0 |
| Physical Pages | `fail` | 104 |
| Function Taxonomy Validation | `fail` | 283 |

## Key Findings

- Duplicate excerpt IDs: `186` keys across `413` records.
- `author_id` sentinel `unknown`: `2302` of `2303` excerpts.
- ZWNJ-bearing excerpts: `100` with `368` total U+200C occurrences.
- Word-count outliers: `48` short and `124` long.

## Per-Check Details

### Required Fields

Status: `pass`

Top-level required ExcerptRecord fields are present and each record validates against the Pydantic contract.

| Metric | Value |
| --- | --- |
| `required_field_count` | `16` |
| `required_fields` | `["chunk_index", "description_arabic", "div_id", "div_path", "end_word", "excerpt_id", "excerpt_topic", "primary_author_layer", "primary_function", "primary_text", "school", "self_containment", "source_id", "start_word", "text_snippet", "unit_index"]` |
| `records_evaluated` | `2303` |

No findings.

### Word Offset Consistency

Status: `fail`

start_word/end_word resolve to the exact primary_text substring and agree with the Phase 2 grouping boundaries.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

Sample findings:
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_1: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_001_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_004_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_005_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_006_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_007_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_008_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_009_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_012_0_0: Word offsets do not resolve to the stored primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_0: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_1: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_2: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_3: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_4: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_5: No matching Phase 1 chunk found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_6: No matching Phase 1 chunk found for div_id.

### text_snippet Prefix Match

Status: `fail`

Whitespace-normalized first 80 characters of primary_text match text_snippet per SPEC V-P3-2.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

Sample findings:
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_0: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_1: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_2: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_3: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_4: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_6: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_8: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_9: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_10: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_11: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_12: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_13: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_14: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_001_0_0: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_0: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_2: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_3: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_4: text_snippet is not a normalized prefix of the first 80 characters of primary_text.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_0: text_snippet is not a normalized prefix of the first 80 characters of primary_text.

### segment_indices Validity

Status: `fail`

segment_indices are non-empty, contiguous, ascending, and match Phase 2 unit/segment provenance.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

Sample findings:
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_0: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_0: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_1: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_1: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_2: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_2: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_3: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_3: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_4: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_4: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_5: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_5: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_6: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_6: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_7: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_7: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_8: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_8: No matching Phase 2 classification file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_9: No matching Phase 2 grouping file found for div_id.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_9: No matching Phase 2 classification file found for div_id.

### excerpt_id Format

Status: `pass`

excerpt_id exactly matches exc_{source_id}_{div_id}_{chunk_index}_{unit_index}.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

No findings.

### Empty Field Detection

Status: `pass`

Required structural strings are non-blank and required collections are not empty when the SPEC expects content.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

No findings.

### Consensus Structure

Status: `pass`

consensus_metadata is structurally valid and internally coherent when present.

| Metric | Value |
| --- | --- |
| `records_with_consensus_metadata` | `788` |
| `decision_type_counts` | `{"author_attribution": 45, "school_attribution": 299, "self_containment": 521}` |

No findings.

### ZWNJ Scan

Status: `warn`

Invisible U+200C characters are inventoried across excerpt fields for follow-up review.

| Metric | Value |
| --- | --- |
| `excerpt_count_with_zwnj` | `100` |
| `total_zwnj_occurrences` | `368` |
| `field_occurrence_counts` | `{"text_snippet": 202, "primary_text": 162, "evidence_refs.0.text_snippet": 2, "evidence_refs.1.text_snippet": 2}` |

Sample findings:
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_001_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_004_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_005_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_006_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_007_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_008_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_009_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_012_0_0: U+200C detected in excerpt payload.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_000_pre_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_001_pre_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_002_pre_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_003_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_005_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_008_pre_0_0: U+200C detected in excerpt payload.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_3_000_pre_0_7: U+200C detected in excerpt payload.

### Duplicate Detection

Status: `fail`

Duplicate excerpt IDs, duplicate coordinate keys, and duplicate normalized primary_text bodies are detected across the corpus.

| Metric | Value |
| --- | --- |
| `duplicate_excerpt_id_count` | `186` |
| `duplicate_excerpt_instances` | `413` |
| `duplicate_coordinate_key_count` | `186` |
| `duplicate_primary_text_count` | `6` |

Sample findings:
- `error` n/a / exc_src_test0001_div_src_test0001_1_002_pre_0_0: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_1_002_pre_0_1: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_0: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_1: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_3: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_4: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_5: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_2_000_0_6: Duplicate excerpt_id detected across the smoke corpus.
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
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_pre_0_0: Duplicate excerpt_id detected across the smoke corpus.
- `error` n/a / exc_src_test0001_div_src_test0001_3_000_pre_0_1: Duplicate excerpt_id detected across the smoke corpus.

### Gate Cross-Reference

Status: `fail`

gate_flags and gate_queue.jsonl entries agree in both directions within each package.

| Metric | Value |
| --- | --- |
| `records_with_gate_flags` | `62` |
| `gate_queue_entry_count` | `65` |

Sample findings:
- `error` ibn_aqil_v3 / exc_src_test0001_div_src_test0001_3_010_0_10: gate_queue.jsonl contains an entry with no matching gate_flags in excerpts.jsonl.
- `error` ibn_aqil_v3 / exc_src_test0001_div_src_test0001_4_004_0_0: gate_queue.jsonl contains an entry with no matching gate_flags in excerpts.jsonl.
- `error` taysir / exc_src_test0001_div_src_test0001_6_044_0_2: gate_queue.jsonl contains an entry with no matching gate_flags in excerpts.jsonl.

### Short/Long Outliers

Status: `warn`

Word-count outliers are reported using a hybrid short-threshold plus Tukey upper-fence audit.

| Metric | Value |
| --- | --- |
| `min_word_count` | `4` |
| `median_word_count` | `64` |
| `max_word_count` | `1165` |
| `q1_word_count` | `34.0` |
| `q3_word_count` | `107.0` |
| `iqr_word_count` | `73.0` |
| `upper_fence` | `216.5` |
| `short_threshold_words` | `10` |
| `short_outlier_count` | `48` |
| `long_outlier_count` | `124` |

Sample findings:
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_1: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_001_0_0: Short word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_006_0_0: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_007_0_11: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_009_0_12: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_8: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_9: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_012_0_0: Short word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_012_0_22: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_1: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_2: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_12: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_1: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_9: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_12: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_16: Long word-count outlier.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_18: Long word-count outlier.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_006_0_0: Short word-count outlier.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_006_0_20: Long word-count outlier.
- `warning` ext_46_qa / exc_src_test0001_div_src_test0001_1_008_pre_0_0: Short word-count outlier.

### author_id Audit

Status: `warn`

primary_author_layer.author_id values are inventoried, including sentinel values such as unknown.

| Metric | Value |
| --- | --- |
| `unique_author_id_count` | `2` |
| `author_id_counts` | `{"unknown": 2302, "ينبغي إسناد الوحدة إلى ابن عقيل نفسه في طبقة الشرح، لا إلى unknown.": 1}` |
| `unknown_author_id_count` | `2302` |

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
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_12: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_13: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_14: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_0: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_1: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_2: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_3: primary_author_layer.author_id uses the sentinel value unknown.
- `warning` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_4: primary_author_layer.author_id uses the sentinel value unknown.

### Consensus Coverage

Status: `pass`

Records with consensus-only signals always carry consensus_metadata, and decision types are summarized.

| Metric | Value |
| --- | --- |
| `records_with_consensus_metadata` | `788` |
| `records_with_consensus_signals` | `83` |
| `decision_type_counts` | `{"author_attribution": 45, "school_attribution": 299, "self_containment": 521}` |

No findings.

### Physical Pages

Status: `fail`

physical_pages matches the page span implied by Phase 1 join points and token-derived character ranges.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |

Sample findings:
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_0: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_1: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_2: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_3: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_4: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_5: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_6: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_7: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_8: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_9: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_11: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_12: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_13: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_0_14: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_0: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_1: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_2: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_3: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_4: No matching Phase 1 chunk found for physical page validation.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_013_1_5: No matching Phase 1 chunk found for physical page validation.

### Function Taxonomy Validation

Status: `fail`

All function fields are valid ScholarlyFunction values and agree with Phase 2 provenance.

| Metric | Value |
| --- | --- |
| `records_evaluated` | `2303` |
| `valid_function_count` | `16` |
| `valid_functions` | `["condition_exception", "cross_reference", "definition", "editorial_note", "evidence_hadith", "evidence_ijma", "evidence_qiyas", "evidence_quran", "evidence_rational", "example", "narration", "opinion_statement", "refutation", "rule_statement", "structural_transition", "unclassified"]` |

Sample findings:
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_2_000_pre_0_10: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_7: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_8: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_000_0_9: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_002_0_3: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_1: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_2: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_3: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_4: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_003_0_6: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_006_0_2: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_008_0_12: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_3: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_4: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_5: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_010_0_14: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_011_0_2: secondary_functions is not a subset of content_types.
- `error` ext_39_masala / exc_src_test0001_div_src_test0001_3_011_0_12: secondary_functions is not a subset of content_types.
- `error` ext_46_qa / exc_src_test0001_div_src_test0001_1_001_pre_0_2: secondary_functions is not a subset of content_types.
- `error` ext_46_qa / exc_src_test0001_div_src_test0001_1_002_pre_0_2: secondary_functions is not a subset of content_types.

## Package Summary

| Package | Excerpts | Gate Entries | Validation Drops |
| --- | ---: | ---: | ---: |
| ext_39_masala | 197 | 0 | 3 |
| ext_46_qa | 300 | 2 | 1 |
| ibn_aqil_v1 | 241 | 21 | 4 |
| ibn_aqil_v3 | 282 | 22 | 15 |
| taysir | 1283 | 20 | 161 |
