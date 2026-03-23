# Overnight Review: Phase 3.1 Deterministic Metadata Assembly

**Task:** Thorough code review of Phase 3.1 deterministic metadata assembly
**Status:** COMPLETE
**Date:** 2026-03-24

## Result

**PASS with minor findings.** No critical bugs. 1 HIGH, 5 MEDIUM, 6 LOW findings.

## Key Findings

### HIGH (1)
- **H-1:** Missing adjacency check in `_compute_layer_coverages` split-point merge (line 125-129). DD-S3-7 requires `layer.start == merged[-1][2]`. Inert for valid input but deviates from design spec. One-line fix.

### MEDIUM (5)
- **M-1:** `review_flags=["llm_enrichment_failed"]` set for DEPENDENT units unnecessarily (only needed for PARTIAL)
- **M-2:** Multi-layer fixture has 1-char gap between MATN and SHARH layers, violating I-AC-2
- **M-3:** Magic sentinel `char_end + 1_000_000` in F-DET-6 instead of named constant
- **M-4:** SPEC tension — LA-2 catches 2-layer cases that LA-3 condition (b) would flag
- **M-5:** Test name `test_la2_even_with_dominant_below_60pct` — dominant is actually 63%

### What Passed Review
- All 10 functions (F-DET-1 through F-DET-9 + orchestrator) correctly implement SPEC 7.1
- LA rule cascade order correct (LA-4 -> LA-1 -> LA-2 -> LA-3)
- No Arabic text safety violations
- No off-by-one errors in word-to-char conversion
- D-023 metadata pass-through complete (all 33 ExcerptRecord fields)
- SPEC deviations documented (SPEC-NOTE-8, SPEC-NOTE-9)
- 37 test functions covering all functions and all 4 LA rules

## Detailed Report

See `overnight/results/review-phase3/review.md` for the full review with code references, SPEC citations, and recommended fixes.

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| `engines/excerpting/src/phase3_deterministic.py` | 637 | Implementation |
| `engines/excerpting/tests/test_phase3_deterministic.py` | 739 | Tests |
| `engines/excerpting/tests/conftest.py` | 598 | Fixtures (Phase 3 additions) |
| `engines/excerpting/contracts.py` | excerpts | ExcerptRecord model, validators |
| `engines/excerpting/SPEC.md` | 6.2, 7.1 | Governing spec |
| `NEXT.md` | all | Design decisions DD-S3-1 through DD-S3-9 |
| `reference/SPEC_ERRATA.md` | all | SPEC-NOTE-8, SPEC-NOTE-9 |
