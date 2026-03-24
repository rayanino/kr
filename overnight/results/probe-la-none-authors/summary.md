# Probe: LA Rules with All-None author_canonical_id

**Status:** PASS — No corruption found
**Tests added:** 5
**Bug found:** No
**Date:** 2026-03-24

## Corruption Vector Investigated

When all `text_layers` in a teaching unit have `author_canonical_id=None`, could
`_compute_layer_coverages()` merge DISTINCT scholarly layers (MATN + SHARH + HASHIYAH)
into a single entry — causing LA-4 (100% single layer) to fire instead of LA-3
(ambiguous, needs consensus gate)?

## Finding

**The code is correct.** The merge key in `_compute_layer_coverages()` is
`(layer_type, author_canonical_id)`. Since MATN, SHARH, and HASHIYAH have different
`LayerType` enum values, they are **never merged** regardless of whether
`author_canonical_id` is `None` for all of them.

The merge condition (line 127–130 of `phase3_deterministic.py`) requires:
1. Same `layer_type` — prevents cross-type merging
2. Same `author_canonical_id` — `None == None` is True, but only after type check
3. Previous segment end in `split_set` — must be at page boundary
4. Adjacency: `layer.start == merged[-1][2]` — H-1 fix prevents gap merging

## Tests Added (5)

| Test | Scenario | Expected | Result |
|------|----------|----------|--------|
| `test_three_layers_all_none_authors_fires_la3` | MATN+SHARH+HASHIYAH, all None authors | LA-3 + EX-M-001 | PASS |
| `test_two_different_types_none_authors_at_split_not_merged` | MATN+SHARH, None authors, at split point | LA-2, not merged | PASS |
| `test_single_layer_none_author_fires_la4` | Single MATN, None author | LA-4 correctly | PASS |
| `test_same_type_none_authors_at_split_merge_correctly` | Two SHARH(None) at split point | LA-4 (correct merge) | PASS |
| `test_three_none_authors_quoted_scholars_all_distinct` | F-DET-9 with 3 None-author layers | 2 distinct quoted scholars | PASS |

## Why This Matters

Test 4 is a **guard against over-correction**: if someone later "fixes" None-author
merging to prevent ALL None merges (including same-type at split points), test 4
catches the regression. Same-type/same-author merges at split points are correct
DD-S3-7 behavior — they reconstruct page-split layers.

Test 5 verifies F-DET-9 (quoted_scholars) also handles None authors correctly,
producing distinct entries for each non-primary layer type.

## Test Suite Impact

- Before: 514 tests, 0 failures
- After: 519 tests, 0 failures
