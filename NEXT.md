# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine HARDENING session.** The passaging SPEC has completed Creative (discourse flow integration, 2 new §4.B capabilities) and Precision (116 lines of Arabic examples, 18 defects fixed, signal hierarchy cross-validated, contracts verified). This session stress-tests the SPEC against adversarial scenarios, verifies error cascade paths, and confirms invariants hold under edge cases.

## What to Read

1. `engines/passaging/SPEC.md` — The full SPEC (now ~1009 lines). Focus on: §4.A.2 (cross-page assembly with boundary_continuity), §4.B.6 (argument detection with dual-signal system), §4.B.7 (discourse cost table), §4.B.8 (completeness forecast with corrective merge), §7 (error handling — 28 error codes).
2. `DEEP_REASONING_PROTOCOL.md` — Perfection standard, especially Criterion #9 (adversarial-proof) and #11 (exhaustive error handling).
3. `KNOWLEDGE_INTEGRITY.md` — Threat model. Passaging touches T-1 (text corruption during assembly), T-2 (misattribution during layer rebasing), and T-4 (silent data loss).

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, DOMAIN.md.

## Definition of Done

1. **12 adversarial scenarios** tested against the SPEC — each scenario: attack vector, which SPEC section it targets, expected defense, whether defense is adequate, fix if not
2. **2 error cascade analyses** — trace what happens when one error triggers another (e.g., PSG_DIVISION_INCONSISTENT → flat passaging → PSG_ARGUMENT_NO_SUBBOUNDARY)
3. **6 invariant verifications** — formal invariants (coverage, ordering, non-overlap, text preservation, author preservation, link consistency) verified to hold under all processing paths including error recovery
4. **Signal disagreement attack:** Construct a scenario where discourse flow and keyword state machine produce contradictory argument boundaries. Verify the coverage-based resolution (added in this session) handles it correctly.
5. **Corrective merge cascade attack:** Construct a scenario where completeness forecast triggers repeated merges. Verify the max-1-merge-per-boundary cap prevents oversized passages.
6. **Discourse cost table completeness:** Verify that every pair of discourse types from the 15-type taxonomy either has an explicit cost or falls through to the 0.4 default. Check for pairs where the default is clearly wrong.
7. `check_spec_quality.py` shows 0 non-VAGUE_QUANTIFIER HIGH defects (current: 0)
8. `session_quality_gate.py` passes
9. NEXT.md written (for atomization engine CREATIVE session or next pipeline engine)
10. SESSION_LOG.md updated
11. Committed and pushed

## Notes for Next Architect

- The 22 VAGUE_QUANTIFIER defects are documented false positives (see SESSION_LOG.md). Don't re-triage — focus on adversarial scenarios.
- The discourse cost table has 15 explicit rows + a default. With 15 discourse types, there are 225 possible (from, to) pairs. 15 are explicit, 210 use the default. Check whether any of the 210 default-cost pairs should be explicitly lower or higher.
- The corrective merge in §4.B.8 is capped at 1 merge per boundary. Verify this is sufficient — can a sequence of 3+ fragments occur in practice? If so, the cap prevents repair. Document when this is acceptable vs problematic.
- The `PSG_ARGUMENT_SIGNAL_DISAGREEMENT` resolution now uses character-count coverage ratio. Construct a scenario where this metric is misleading (e.g., keyword detects many small arguments, discourse flow detects one large argument — coverage could be similar but meaning differs).
- Check whether the boundary_continuity `mid_argument` proxy costs (0.8) in §4.B.7 are consistent with the actual discourse transition costs for argument-internal transitions.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
