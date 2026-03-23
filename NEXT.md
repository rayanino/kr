# NEXT — Excerpting Engine: Phase 2 Preparation

## Current Position

- Excerpting Phase 1: **ACCEPTED** (commit 28a188ad)
- SPEC-NOTE-4 (T-1 word-merge corruption): **RESOLVED** (commit fe37f1d9)
  - mid_sentence separator changed from `""` to `" "` (always space)
  - 92% word-merge corruption → 0%
  - SPEC-NOTE-5 subsumed (tanwin+alif edge case no longer relevant)
- Test baseline: **77 passed** (excerpting), **503 passed** (normalization)
- Open SPEC errata: SPEC-NOTE-6 (documentation), SPEC-NOTE-7 (documentation)

## What's Next

Phase 2 (LLM classification) is unblocked. The architect must:

1. Resolve SPEC-NOTE-6 and SPEC-NOTE-7 (documentation fixes, non-blocking for Phase 2 but should be cleaned up)
2. Design the Phase 2 CC handoff using `kr-preparing-cc-handoffs`
3. Write NEXT.md Session 2 directive for CC

## Open SPEC Errata (documentation only)

- **SPEC-NOTE-6:** §4.2 EXCLUDE_KEYWORDS expanded beyond SPEC list — CC added 8 compound forms with zero false positives. SPEC should be updated to match.
- **SPEC-NOTE-7:** §4.2 "word-boundary-aware" wording contradicts example — should say "exact match after noise stripping."

## Key Files

- `engines/excerpting/SPEC.md` — the governing SPEC
- `engines/excerpting/src/phase1_assembly.py` — Phase 1 implementation
- `reference/SPEC_ERRATA.md` — all errata including resolved ones
