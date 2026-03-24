# Overnight Review: Phase 3.1 Deterministic Metadata Assembly (Pass 2)

**Task:** Deep independent code review of Phase 3.1 deterministic metadata assembly
**Status:** COMPLETE
**Date:** 2026-03-24
**Reviewer:** Claude Opus 4.6 (second-pass independent review)

## Result

**PASS with findings.** No critical bugs. 2 HIGH, 7 MEDIUM, 8 LOW findings.
All 37 tests passing. Pass 2 confirmed all Pass 1 findings and added 4 new ones.

## Key Findings

### HIGH (2)
- **H-1 (confirmed):** Missing adjacency check in `_compute_layer_coverages` split-point merge. DD-S3-7 requires `layer.start == merged[-1][2]`. One-line fix.
- **H-2 (NEW):** Interleaved same-type layers (MATN-SHARH-MATN) inflate LA rule layer count. Triggers LA-3 instead of LA-1/LA-2 for genuinely 2-layer texts. Conservative outcome (flags for review, no corruption).

### MEDIUM (7) — 2 new
- **M-1:** review_flags for DEPENDENT unnecessary
- **M-2:** Test fixture I-AC-2 gap (1 char between layers)
- **M-3:** Magic sentinel in page range
- **M-4:** SPEC LA-2/LA-3 condition (b) unreachable
- **M-5:** Test name misleading (dominant is 63%, not below 60%)
- **M-6 (NEW):** Unused `primary_text` parameter in `filter_relevant_footnotes`
- **M-7 (NEW):** No test for `author_canonical_id=None` → `"unknown"` fallback

### What Passed Review
- All 10 functions implement SPEC §7.1 correctly
- LA rule cascade order: LA-4 → LA-1 → LA-2 → LA-3
- Arabic text safety: no `.lower()`, `.strip()`, `\d` violations
- Off-by-one: exclusive-end convention consistent throughout
- D-023: all 33 ExcerptRecord fields explicitly populated
- SPEC deviations documented (SPEC-NOTE-8, SPEC-NOTE-9)
- 37 tests covering all functions and all 4 LA rules

## Action Items

- **Before Session 4:** Fix H-1 (adjacency check)
- **Before transition gate:** Fix M-1 through M-7
- **Track:** H-2 in KNOWN_LIMITATIONS.md, L-1 through L-8

## Detailed Report

See `overnight/results/review-phase3/review.md` for the full review with code references, SPEC citations, and recommended fixes.

## Files Reviewed

| File | Lines | Purpose |
|------|-------|---------|
| `engines/excerpting/src/phase3_deterministic.py` | 637 | Implementation |
| `engines/excerpting/tests/test_phase3_deterministic.py` | 739 | Tests |
| `engines/excerpting/tests/conftest.py` | 598 | Fixtures |
| `engines/excerpting/contracts.py` | selected | ExcerptRecord, validators, sub-models |
| `engines/excerpting/src/phase2_classify.py` | 105-123 | `_build_token_char_map` |
| `engines/excerpting/SPEC.md` | §6.2, §7.1 | Governing spec |
| `NEXT.md` | all | Design decisions DD-S3-1 through DD-S3-9 |
| `reference/SPEC_ERRATA.md` | all | SPEC-NOTE-8, SPEC-NOTE-9 |
