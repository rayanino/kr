# Phase 2 Hardening Tests — Summary

## Task
Add edge case hardening tests for Phase 2 (LLM classification + grouping) of the excerpting engine.

## Result
**76 tests in `test_phase2_hardening.py`** — all passing. Full suite: **351/351 passed** in 27s.

## New Tests Added (24 tests across 8 categories)

### 11. ZWNJ Character Handling (4 tests)
- Token-char map with ZWNJ (U+200C) inside token — invisible char counted in span
- Snippet containing ZWNJ matches via exact match
- Full normalization pipeline with ZWNJ tokens
- Two-segment boundary where ZWNJ token is anchor

### 12. Snippet at Exact Token Boundary (3 tests)
- char_pos in whitespace gap returns next token index
- Snippet matching at exact character start of a token
- Last segment snippet anchoring at the very last token

### 13. Single Segment Classification (2 tests)
- run_phase2a with single segment covering all text → [0, total-1]
- Scholarly function and confidence preserved through normalization

### 14. Single Unit Grouping (1 test)
- run_phase2b with single unit covering 3 segments → passes verification

### 15. DD-S2-8: ValidationError No Feedback (2 tests)
- classify retry after ValidationError: user message has NO snippet/coverage feedback
- group retry after ValidationError: user message has NO invariant feedback

### 16. V-P2-14: Wildly Wrong Offsets (2 tests)
- start_word=5000, end_word=10000 when derived is 0,9 → corrected with warnings
- Only start_word wrong (off by 200), end_word correct → one warning

### 17. V-P2-15: All Three Containment Levels (6 tests)
- FULL without notes → passes (no warning)
- FULL with notes → cleared to None (warning)
- PARTIAL with notes → passes (no warning)
- PARTIAL without notes → autofilled "No notes provided" (warning)
- DEPENDENT with notes → passes (no warning)
- DEPENDENT without notes → autofilled "No notes provided" (warning)

### 18. Max Token Boundary Values (4 parametrized tests)
- 2000 → 8192 (exact boundary, no warning)
- 2001 → 32768 (just above, no warning)
- 4000 → 32768 (exactly 4000, no warning)
- 4001 → 32768 (just above, with warning)

## Pre-existing Tests (52 tests across categories 1-10)
All preserved and passing. No regressions.

## Key Technical Observations
- ZWNJ (U+200C) is non-whitespace for Python `split()`, so tokens containing it have more chars than visible glyphs. The token-char map handles this correctly.
- DD-S2-8 design decision: schema errors (ValidationError) get `error_feedback=None` because they are structural, not content. Content feedback would confuse the LLM about what to fix.
- V-P2-14 auto-repair works even with extreme discrepancies (5000+ word offsets) because derived values from segments are always authoritative.
- The 4000/4001 boundary distinction matters: 4000 is `>2000` (returns 32768) but NOT `>4000` (no warning). Only 4001+ triggers the untested-range warning.
