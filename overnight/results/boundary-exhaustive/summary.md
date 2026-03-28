# Boundary-Exhaustive Hardening — Session Summary

**Date:** 2026-03-28 (overnight)
**Engine:** Excerpting
**Task:** Boundary value tests for frozen SPEC thresholds

## Results

| Metric | Value |
|--------|-------|
| Tests before | 597 |
| Tests added | 16 |
| Tests after | 613 |
| Bugs found | 0 |
| All tests passing | ✅ |

## What Was Tested

### §4.4 Merge (TINY_DIVISION_WORDS=50) — 5 tests

Predicate: `word_count < 50` triggers merge.

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| test_merge_49_words | 49 words | MERGED | ✅ |
| test_merge_50_words_standalone | 50 words (at boundary) | STANDALONE | ✅ |
| test_merge_51_words_standalone | 51 words | STANDALONE | ✅ |
| test_merge_1_word | 1 word | MERGED | ✅ |
| test_merge_0_words_with_sibling | 0 Arabic words | MERGED | ✅ |

**Key finding:** The 50-words-standalone test is the critical boundary guard. If someone changed `< 50` to `<= 50`, this test would catch it.

### §4.5 Split (OVERSIZED_DIVISION_WORDS=5000) — 4 tests

Predicate: `word_count > 5000` triggers split.

| Test | Input | Expected | Result |
|------|-------|----------|--------|
| test_split_4999_words_no_split | 4999 words | NO SPLIT | ✅ |
| test_split_5000_words_no_split | 5000 words (at boundary) | NO SPLIT | ✅ |
| test_split_5001_words_must_split | 5001 words | SPLIT ≥2 chunks | ✅ |
| test_split_10001_words_recursive | 10001 words | SPLIT ≥3 chunks | ✅ |

**Key finding:** The 5000-word no-split test is the most valuable. A change from `>` to `>=` would cause unnecessary splitting of valid chunks.

### §4.6 Layer Gap Repair (threshold: gap ≤ 5 chars) — 3 tests

Predicate: `gap <= 5` → repair with EX-A-003 warning; `gap > 5` → I-AC-2 FATAL.

| Test | Gap Size | Expected | Result |
|------|----------|----------|--------|
| test_layer_gap_4_chars_repaired | 4 chars | REPAIR + EX-A-003 | ✅ |
| test_layer_gap_5_chars_repaired | 5 chars (exact boundary) | REPAIR + EX-A-003 | ✅ |
| test_layer_gap_6_chars_fatal | 6 chars (one above) | I-AC-2 FATAL | ✅ |

**Key finding:** Existing tests used gap=2 and gap=10. The 5/6 boundary was untested. Gap=5 repairs; gap=6 is fatal.

### §7.1 F-DET-3 LA Rules (80% coverage threshold) — 4 tests

Predicate: dominant layer coverage `>= 0.80` → LA-1.

| Test | Coverage | Layers | Expected Rule | Result |
|------|----------|--------|---------------|--------|
| test_la1_at_79_point_9_percent | 79.9% | 2 | LA-2 | ✅ |
| test_la1_at_80_point_1_percent | 80.1% | 2 | LA-1 | ✅ |
| test_la_two_layers_each_50_percent | 50%/50% | 2 | LA-2 (SHARH outermost) | ✅ |
| test_la_three_layers_each_33_percent | 33%/33%/34% | 3 | LA-3 | ✅ |

**Key finding:** Existing tests already had exact 80% and 70% coverage. The new 79.9% and 80.1% tests provide tighter probes at the boundary. The 3-layer LA-3 test adds coverage for the multi-layer ambiguous case.

## Architecture Notes

The test file uses a single-character Arabic text (`"ا" * 1000`) to achieve precise fractional character coverage (e.g., 799/1000 = 79.9%) without floating-point surprise. This technique is more reliable than constructing Arabic prose of exact character counts.

The merge/split helpers generate Arabic text by cycling through 10 common Arabic words. `_count_arabic_words` is verified against the generated text before constructing each test fixture.

## No Bugs Found

All 16 boundary tests passed on first run. The implementation correctly handles:
- Strict `<` for merge (not `<=`)
- Strict `>` for split (not `>=`)
- Inclusive `<=` for gap repair (gap=5 repairs, gap=6 is fatal)
- Inclusive `>=` for LA-1 (coverage=0.80 triggers LA-1)
