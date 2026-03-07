# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Normalization engine HARDENING session.** The normalization SPEC has completed CREATIVE (10 §4.B capabilities) and PRECISION (0 HIGH defects, 5 examples added, 5 structural defects fixed, contracts updated, 4 normalizer outlines added). This session stress-tests the SPEC for knowledge corruption paths and failure cascades.

## What to Read

1. `engines/normalization/SPEC.md` — Focus on §4 (processing), §5 (validation), §7 (error handling).
2. `KNOWLEDGE_INTEGRITY.md` — The threat model for knowledge corruption.
3. `engines/source/SPEC.md` §3 — Verify the source→normalization interface cannot produce corrupt inputs.
4. `reference/DOMAIN.md` §236-248 — Arabic text hazards that could corrupt normalization.

**Do NOT read:** VISION.md whole, kr_decisions.md, other engine SPECs beyond source §3.

## Definition of Done

1. At least 10 adversarial scenarios tested (each: attack vector, what breaks, what prevents it, SPEC change if needed)
2. At least 2 error cascade analyses (multi-step failure chains)
3. At least 5 invariants verified (properties that must NEVER be violated, with the specific SPEC rules that guarantee them)
4. `check_spec_quality.py` still shows 0 HIGH defects after any changes
5. Every §7 error code has a clear trigger scenario — no theoretical-only error codes
6. Multi-layer misattribution scenarios: at least 3 concrete attack vectors on §4.A.5 + §4.B.9 (this is the highest-risk operation)
7. OCR corruption scenarios: at least 2 scenarios where OCR errors could propagate into the library as false knowledge
8. New §4.B.8/§4.B.10 interaction verified under adversarial conditions (what if continuity says mid_argument but discourse flow says cycle complete on the SAME content unit?)
9. Self-audit performed per DEEP_REASONING_PROTOCOL: ≥3 defects found and fixed
10. `session_quality_gate.py` passes
11. NEXT.md written (for passaging engine CREATIVE session)
12. SESSION_LOG.md updated
13. Committed and pushed

## Notes for Next Architect

- The PRECISION session added §5 validation checks 10-12 for the new §4.B.8-10 fields. Hardening should verify these checks catch real failures.
- Contracts.py was updated with `BoundaryContinuity`, `DiscourseFlow`, `LayerFingerprint`, and related models. Verify these models cannot represent invalid states (e.g., `argument_cycle_complete: true` with non-empty `cycle_missing_elements` — should this be a Pydantic validator?).
- The `HeadingDetectionMethod` enum now includes `LAYOUT_DETECTED` for PDF/Docling/EPUB headings.
- Pass 6 now has an explicit §4.B processing order with 11 steps + cross-validation. Hardening should verify this ordering is correct and no circular dependencies exist.
- New error codes: `NORM_CONTINUITY_INCONSISTENT`, `NORM_DISCOURSE_INCONSISTENT`, `NORM_FINGERPRINT_INVALID`, `NORM_ORPHAN_FOOTNOTE_REF`. Verify each has a concrete trigger scenario.
- §4.A.4a-4d are behavioral outlines only — they do not need hardening until full specs are written.
- The heading inclusion rule (§4.A.6) now explicitly distinguishes Shamela PageHead (excluded from primary_text) from PDF/other headings (included). Verify this distinction is adversarial-proof.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
