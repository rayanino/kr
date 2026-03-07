# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Source engine HARDENING session.** The source engine SPEC has completed both CREATIVE and PRECISION sessions. It now has 10 §4.B capabilities (all fully specified), 0 HIGH defects from `check_spec_quality.py`, all error codes in §7 (including 6 new codes from §4.B capabilities), and contracts.py aligned with the SPEC.

This HARDENING session should: verify no knowledge corruption paths exist (every write validated, every error handled, no silent data loss), verify all KNOWLEDGE_INTEGRITY.md invariants hold across all §4.A and §4.B rules, test adversarial scenarios (what if LLM returns wrong data? what if external APIs return corrupt data? what if two processes run intake simultaneously?), and verify the enrichment invariant system is watertight.

## What to Read

1. `engines/source/SPEC.md` — Full SPEC. Focus on: §4.A.2 (acquisition workflow atomicity), §4.A.5 (scholar record consistency checks), §4.A.8 (trust evaluation), §4.B.5-§4.B.10 (external data integration — main corruption surface).
2. `KNOWLEDGE_INTEGRITY.md` — Full file. Test every invariant against every SPEC rule.
3. `engines/source/contracts.py` — Verify all validation constraints are correct.
4. Run `python3 scripts/check_spec_quality.py engines/source/SPEC.md` — Confirm 0 HIGH defects persist.

**Do NOT read:** VISION.md, other engine SPECs, CREATIVE_MANDATE.md. This is hardening work.

## Definition of Done

1. ≥10 adversarial scenarios tested (documented in SPEC §7 or a hardening appendix)
2. ≥2 error cascade paths traced end-to-end
3. Every KNOWLEDGE_INTEGRITY.md invariant verified against every §4.A and §4.B rule
4. All external data integration points (OpenITI, KITAB, Usul-Data, Wikidata) have corruption defenses
5. No new HIGH defects introduced
6. contracts.py unchanged or only tightened
7. NEXT.md written (for normalization engine CREATIVE session)
8. SESSION_LOG.md updated
9. Committed and pushed

## Key Areas to Stress-Test

- **Concurrent intake:** What happens if two sources are being processed simultaneously and both reference the same scholar? (§4.A.5 registry atomicity)
- **External API corruption:** What if Wikidata returns a valid response for the wrong scholar? (§4.B.8 cross-validation)
- **LLM hallucination in genealogy:** What if the LLM invents a teacher-student link that doesn't exist? (§4.B.7 depth limits and consensus)
- **Edition comparison on divergent structures:** What if two editions have completely different chapter structures? (§4.B.6 fallback)
- **Enrichment write-back loops:** Can an enrichment trigger a cascade that triggers another enrichment that creates a loop?

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
