# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Taxonomy engine CREATIVE session.** The excerpting engine SPEC is now hardened (0 quality defects, adversarial test cases verified, threat model mapped, error cascades analyzed). The taxonomy engine is the next pipeline stage and has no SPEC refinement yet. Begin with the Creative Exploration Protocol: read the existing SPEC, run quality checks, research the problem space (taxonomy/classification in Arabic NLP), then invent transformative capabilities.

## What to Read

1. `engines/taxonomy/SPEC.md` — The full SPEC. Primary target.
2. `engines/taxonomy/contracts.py` — If it exists.
3. `reference/ENTRY_EXAMPLE.md` — Quality target (how entries use taxonomy).
4. `reference/USER_SCENARIOS.md` — Who benefits and how.

**Do NOT read:** Other SPECs (excerpting, atomization), KNOWLEDGE_INTEGRITY.md, DOMAIN.md — save context for creative work.

## Definition of Done

1. §4.B has 3+ new transformative capabilities, fully specified (not hollow)
2. Each §4.B capability has: input, output, processing rules, edge cases, technical approach
3. §4.A core processing reviewed and grounded (defects noted for PRECISION session)
4. contracts.py created or updated to match §3
5. `check_spec_quality.py` baseline recorded
6. `creative_verification.py` score ≥ 70/100
7. NEXT.md written (for taxonomy PRECISION session)
8. SESSION_LOG.md updated
9. Committed and pushed

## What the Previous Session Did

- HARDENING session for excerpting engine
- Mapped all 7 KNOWLEDGE_INTEGRITY.md threats to SPEC prevention mechanisms
- Found and fixed 6 defects:
  1. §3/§4.B.3 mismatch: `argument_completeness` field missing `continuation_detected`, `continuation_passage_id`
  2. Whitespace_separator atom coverage ambiguity: V-3 and §3 now explicitly exclude whitespace_separator atoms
  3. Source metadata cross-validation: added Layer 2 checks for school mismatch and layer distribution plausibility
  4. Bidirectional update error handling (§4.B.6): added atomic rollback and retry queue with schema validation
  5. Batch post-processing partial failure (§4.B.2): added checkpoint/resume and distinguishing null vs. empty list
  6. Upstream layer error cascade: added `EXCERPT_LAYER_DISTRIBUTION_UNIFORM` warning for homogeneously wrong layers
- Added 6 adversarial test cases to §10: 3 for decontextualization, 2 for multi-layer attribution, 1 for evidence integrity
- Added 4 new error codes: `EXCERPT_SOURCE_SCHOOL_MISMATCH`, `EXCERPT_LAYER_DISTRIBUTION_UNIFORM`, `EXCERPT_DIALOGUE_UPDATE_FAILED`
- check_spec_quality.py: 0 defects

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
