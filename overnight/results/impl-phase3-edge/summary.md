# Phase 3.1 Edge Case & Adversarial Tests — Results

**Task:** impl-phase3-edge
**Date:** 2026-03-24
**Agent:** Claude Opus 4.6 (overnight autonomous)

## Outcome: PASS

**22 new adversarial tests** added to `test_phase3_deterministic.py`.
All 86 Phase 3 tests pass. All 235 excerpting engine tests pass. 0 failures.

## Review Findings Addressed

The deep review (Pass 2) found **no CRITICAL bugs**. H-1 (missing adjacency check in split-point merging) was already fixed in the prior session at line 130 of `phase3_deterministic.py`. No code changes needed.

## Tests Added

### TestAdversarialLayerAttribution (5 tests)
| Test | Category | What it proves |
|------|----------|----------------|
| `test_la3_dominant_coverage_value_correct` | LA-3 path | 3 layers (SHARH+HASHIYAH+MATN), verifies coverage_pct in result |
| `test_la3_four_distinct_layer_types` | LA-3 path | 4 layer types (TAHQIQ+HASHIYAH+SHARH+MATN), LA-3 fires |
| `test_different_type_at_split_point_no_merge` | Split-point guard | SHARH→MATN at split boundary NOT merged (different types) |
| `test_same_type_different_author_at_split_point_no_merge` | Split-point guard | Same type, different author at split point NOT merged |
| `test_quoted_scholars_split_point_merging_effect` | L-3 gap fill | Merging 2 SHARH segments → 1 quoted scholar entry |

### TestAdversarialSplitChunkId (2 tests)
| Test | Category | What it proves |
|------|----------|----------------|
| `test_split_info_chunk_index_zero_with_split_info` | Split chunk | chunk_index=0 with split_info present (I-AC-5 compliance) |
| `test_split_info_large_chunk_index` | Split chunk | chunk_index=99 correctly reflected in excerpt_id |

### TestAdversarialEvidenceDetection (7 tests)
| Test | Category | What it proves |
|------|----------|----------------|
| `test_hadith_all_markers_with_waw_proclitic` | DD-S3-8 | All 6 hadith markers detected with و prefix |
| `test_ijma_all_markers_with_fa_proclitic` | DD-S3-8 | All 5 ijma markers detected with ف prefix |
| `test_repeated_marker_both_occurrences_detected` | L-2 gap fill | Same marker at 2 positions → both detected |
| `test_marker_at_very_end_of_text` | Boundary | Marker at text end → snippet clamped correctly |
| `test_quran_verse_with_hamza_and_madda` | Arabic safety | آ/أ/إ preserved byte-for-byte in ﴿...﴾ |
| `test_adjacent_quran_verses_both_detected` | Edge case | ﴾﴿ directly adjacent → both verses detected |
| `test_no_false_positive_on_similar_words` | False positive | Similar Arabic words (يرويه, جمعوا) don't trigger markers |

### TestAdversarialTextExtraction (5 tests)
| Test | Category | What it proves |
|------|----------|----------------|
| `test_multiple_paragraph_breaks_all_preserved` | I-ER-2 | 3 × \n\n breaks all preserved in substring extraction |
| `test_single_newline_preserved` | I-ER-2 | Single \n preserved (not just \n\n) |
| `test_first_word_extraction` | Boundary | start_word=0, end_word=0 → first word only |
| `test_last_word_extraction` | Boundary | Last word index → last word only |
| `test_long_text_offsets_at_start_middle_end` | Offset accuracy | 1500-word text: verified at positions 0, 750, and end |

### TestAdversarialFootnotes (3 tests)
| Test | Category | What it proves |
|------|----------|----------------|
| `test_all_footnotes_outside_unit_range` | Range exclusion | Markers exist but all outside unit range → empty |
| `test_footnote_at_exact_char_start_included` | Inclusive boundary | Marker at char_start=0 → included |
| `test_footnote_at_exact_char_end_excluded` | Exclusive boundary | Marker at char_end position → excluded |

## Test Count Progression

| Stage | Phase 3 Tests | Total Excerpting |
|-------|--------------|-----------------|
| Session 3 build | 37 | 186 |
| Pass 1 hardening | 64 | 213 |
| **This session** | **86** | **235** |

## Review Gaps Closed

- **L-2** (evidence dedup at same position): `test_repeated_marker_both_occurrences_detected`
- **L-3** (split-point merging effect on quoted scholars): `test_quoted_scholars_split_point_merging_effect`
- **M-7** was already closed by Pass 1 hardening
