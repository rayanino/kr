# NEXT SESSION

## Session Type
IMPLEMENTATION_PREP (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine IMPLEMENTATION_PREP session.** The passaging SPEC has completed Creative (2 new §4.B capabilities), Precision (18 defects fixed, 116 lines of Arabic examples), and Hardening (12 adversarial scenarios, 2 error cascades, 6 invariants verified, 18 defects fixed, 3 new error codes). The SPEC is ready for implementation preparation.

## What to Read

1. `engines/passaging/SPEC.md` — The full SPEC (~1038 lines). Focus on: §2 (input contract — what schemas exist), §3 (output contract — what schemas need creating), §9 (current implementation state — what exists today), §10 (test requirements — what fixtures are needed).
2. `engines/passaging/contracts.py` — The existing Pydantic models.
3. `SESSION_TYPES.md` — IMPLEMENTATION_PREP checklist.
4. `reference/RESOURCES.md` — External tools and libraries.

**Do NOT read:** VISION.md, kr_decisions.md, other engine SPECs, KNOWLEDGE_INTEGRITY.md.

## Definition of Done

1. `engines/passaging/contracts.py` — Updated Pydantic models matching §2 and §3 exactly (input manifest fields, output PassageRecord schema). Verify every §3 field is present with correct type.
2. `tests/fixtures/` — Verify test fixtures exist for all 12 §10 test categories. Create missing fixture stubs with clear descriptions of what each needs.
3. `engines/passaging/CLAUDE.md` — Written with accurate implementation state, module architecture guidance, and what Claude Code should build first.
4. `MILESTONES.md` — Task decomposition for passaging engine implementation.
5. Module stubs created: directory skeleton with SPEC-referencing docstrings for Claude Code.
6. `engines/passaging/IMPLEMENTATION_ORDER.md` — Build plan: what to implement first, dependencies between modules.
7. `engines/passaging/TEST_PLAN.md` — Test cases mapped to fixtures for all 12 §10 categories.
8. `requirements.txt` — All passaging dependencies present.
9. `check_spec_quality.py` shows 0 non-VAGUE_QUANTIFIER HIGH defects.
10. `session_quality_gate.py` passes.
11. NEXT.md written (pointing to source engine IMPL_PREP or next engine).
12. SESSION_LOG.md updated.
13. Committed and pushed.

## Notes for Next Architect

- The SPEC is 1038 lines and has had 3 refinement sessions. It should be stable.
- contracts.py was created during the normalization IMPL_PREP session. Check if passaging-specific models (PassageRecord, argument_structure, completeness_forecast) are already defined or need creation.
- The 25 VAGUE_QUANTIFIER HIGH defects are documented false positives — don't re-triage.
- The HARDENING session added 3 new error codes, 14 new discourse cost entries, and fixed the corrective merge cap (now max 2 merges per fragment). These changes need reflection in contracts.py if they affect schema fields.
- §4.B capabilities are all [NOT YET IMPLEMENTED] — Claude Code should build §4.A (core processing) first, then §4.B capabilities incrementally.
- The `argument_depth_exceeded` review flag was added during HARDENING — verify it's in the PassageRecord review_flags enum.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
