# NEXT SESSION

## Session Type
HARDENING (see SESSION_TYPES.md for full framework)

## Immediate Task

**Taxonomy engine HARDENING session.** The taxonomy SPEC now has 0 high-severity defects, 12 concrete examples across §4.A and §4.B, and fully specified LLM calls. The HARDENING session must: map KNOWLEDGE_INTEGRITY.md threats to taxonomy-specific prevention mechanisms, verify no knowledge corruption paths exist (especially in placement, evolution, and migration), add adversarial test cases to §10, and verify error cascades are handled.

## What to Read

1. `engines/taxonomy/SPEC.md` — The hardened target. Focus on §4.A.1 (placement), §4.A.5 (evolution), §4.A.7 (migration), §7 (error handling).
2. `KNOWLEDGE_INTEGRITY.md` — Threat model. Map each threat to taxonomy-specific vectors.
3. `engines/taxonomy/contracts.py` — Verify invariants are enforced in model constraints.

**Do NOT read:** ENTRY_EXAMPLE.md, USER_SCENARIOS.md, DOMAIN.md, other engine SPECs, CREATIVE_MANDATE.md — save context for hardening work.

## Definition of Done

1. Every KNOWLEDGE_INTEGRITY.md threat mapped to taxonomy-specific prevention mechanisms
2. At least 4 adversarial test cases added to §10 (placement corruption, evolution orphan, migration data loss, rollback consistency)
3. Error cascade analysis: what happens when upstream errors propagate (wrong science_id from excerpting, invalid proposed_leaf, corrupted tree YAML)
4. check_spec_quality.py shows 0 high-severity defects (maintained)
5. Self-audit performed: ≥4 structural/semantic defects found and fixed
6. NEXT.md written (for synthesis engine CREATIVE session — next in pipeline)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Session Did (Precision)

- Fixed 47→0 high-severity defects (28 vague quantifiers, 1 handwave LLM, 1 missing threshold)
- Added 12 concrete examples across all §4 subsections
- Specified LLM calls fully for §4.A.1 (Stage 1b + Stage 2), §4.A.4, §4.B.4
- Fixed contracts.py: added missing `entry_lifecycle_propagation` to EvolutionInvariantChecks
- Self-audit: 4 structural defects found and fixed
- Final: 0 high, 6 medium (false-positive "significant" concept terms), 2 low

## Hardening Focus Areas

Key corruption vectors to investigate:
1. **Placement writes incorrect leaf:** LLM returns non-existent path; tree changes between generation and write
2. **Evolution orphans excerpts:** Redistribution plan incomplete; new excerpt arrives during evolution
3. **Migration data loss:** File move fails midway; rollback itself fails
4. **Coverage analytics drift:** Cache vs actual files; nightly check frequency
5. **Concurrent placement:** Two excerpts at same leaf simultaneously; race conditions

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
