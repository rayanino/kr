# Overnight: Phase 3.1 Review + Edge Case Hardening

**Tasks:** (1) Deep code review, (2) Fix H-1, (3) Edge case + adversarial tests
**Status:** COMPLETE
**Date:** 2026-03-24
**Agent:** Claude Opus 4.6 (overnight autonomous)

## Results

### Task 1: Code Review (Pass 2)

**PASS with findings.** No critical bugs. 2 HIGH, 7 MEDIUM, 8 LOW findings.
Pass 2 confirmed all Pass 1 findings and added 4 new ones.

### Task 2: H-1 Fix Applied

Added adjacency check `and layer.start == merged[-1][2]` to `_compute_layer_coverages` merge condition (line 130). One-line fix as recommended by review. All tests pass.

### Task 3: Edge Case Tests (+27 tests)

**64 total tests** (37 original + 27 new). All passing. 0 pyright errors.

| Category | Tests | Coverage |
|----------|-------|----------|
| LA rule edge cases | 6 | author_id=None fallback (M-7), gapped segments at split (H-1), 3-layer HASHIYAH+SHARH+MATN, HASHIYAH-vs-SHARH LA-2, 3-segment chain merge |
| Evidence detection | 8 | All 6 hadith markers, all 5 ijma markers, Quran with diacritics, multiple Quran verses, mixed evidence, proclitic prefix, snippet context window, empty text |
| Page range | 3 | All-pages-None (L-1), single-page-None, 3-page middle span |
| Quoted scholars | 2 | Single-layer empty result (L-8), non-MATN secondary role |
| Orchestrator | 6 | Empty footnotes, single-word unit, 1200-word text offsets, DEPENDENT review flag, FULL no flag, D-023 all 33 fields |
| Footnote filtering | 2 | Empty list, mixed range selection |

## Key Findings (from review)

### HIGH (2)
- **H-1:** Missing adjacency check in split-point merge. **FIXED.**
- **H-2:** Interleaved same-type layers inflate layer count. Conservative outcome (no corruption). Track in KNOWN_LIMITATIONS.md.

### MEDIUM (7) — remaining for transition gate
- M-1: review_flags for DEPENDENT unnecessary
- M-2: Test fixture I-AC-2 gap (1 char between layers)
- M-3: Magic sentinel in page range
- M-4: SPEC LA-2/LA-3 condition (b) unreachable
- M-5: Test name misleading
- M-6: Unused `primary_text` parameter in `filter_relevant_footnotes`
- M-7: No test for author_id=None fallback **— NOW TESTED**

## Action Items (remaining)

- **Before transition gate:** Fix M-1 through M-6
- **Track:** H-2 in KNOWN_LIMITATIONS.md, L-1 through L-8

## Detailed Report

See `overnight/results/review-phase3/review.md` for the full review.

## Files Modified

| File | Change |
|------|--------|
| `engines/excerpting/src/phase3_deterministic.py` | H-1 fix: adjacency check (1 line) |
| `engines/excerpting/tests/test_phase3_deterministic.py` | +27 edge case tests (739 → ~1050 lines) |
