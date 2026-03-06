# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Source engine CREATIVE session.** The synthesis engine SPEC is now hardened (CREATIVE + PRECISION + HARDENING complete). Following the refinement priority order (upstream first), the source engine is next. The source engine is the pipeline entry point — it defines what enters the library, and all downstream quality depends on its decisions.

The source engine SPEC exists (933 lines) but was written during the preparatory phase, before KNOWLEDGE_INTEGRITY.md, before the research on attribution-first generation, and before the synthesis engine's threat model revealed how critical upstream metadata quality is. This CREATIVE session should: research state-of-the-art in digital Islamic library management, invent transformative capabilities, and ensure the §4.B section contains architect-originated capabilities that match the ambition level of the synthesis engine's §4.B.

## What to Read

1. `engines/source/SPEC.md` — The full SPEC. This is a CREATIVE session — read the whole thing to understand what exists before inventing.
2. `KNOWLEDGE_INTEGRITY.md` — Refresh on threats T-1 (silent text corruption), T-6 (metadata poisoning), T-7 (duplication). These originate at the source engine.
3. `engines/synthesis/SPEC.md` §2.1 — What the synthesis engine expects from upstream. The source engine's output quality directly determines entry quality.
4. `CREATIVE_MANDATE.md` — The invention protocol. Follow it.
5. `reference/RESOURCES.md` — Check what tools/libraries exist for source acquisition and processing.
6. `DOMAIN.md` §3 (Islamic scholarly text structure) — Essential for understanding source types.

**Do NOT read:** VISION.md (use extract script if needed). Do NOT read other engine SPECs beyond §2 input contracts.

## Definition of Done

1. At least 8 web searches (3 problem space, 3 possibility, 2 validation)
2. Invention notes with ≥ 3 new §4.B capabilities, each with named technology and concrete output example
3. §4.A rules reviewed for precision — every rule implementable by Claude Code with zero clarifying questions
4. §4.B capabilities fully specified (inputs, outputs, triggers, behavioral rules)
5. contracts.py updated to match any SPEC changes
6. SPEC quality check run, defect baseline established
7. Self-audit: ≥ 3 structural/semantic defects found and fixed
8. NEXT.md written (for source engine PRECISION session)
9. SESSION_LOG.md updated
10. Committed and pushed

## Research Directions (Starting Points)

- How do digital Islamic libraries (Shamela, Waqfeya, Turath.io) organize and validate sources?
- What source-level metadata can predict downstream extraction quality?
- Can source fingerprinting detect editions automatically?
- What makes one edition better than another (tahqiq quality signals)?
- Can the source engine pre-analyze a source's table of contents to predict what the library will learn from it?

## Key Context from Synthesis HARDENING

The synthesis engine's cascade analysis revealed two critical upstream dependencies:
1. **Scholar authority registry completeness** — metadata resolution failures cause position loss. The source engine should ensure scholar records are created during source registration.
2. **Duplicate cluster accuracy** — the synthesis engine now verifies clusters but depends on the taxonomy engine's deduplication, which depends on the source engine's work-level matching. The source engine's edition detection quality is a root cause.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
