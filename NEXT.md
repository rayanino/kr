# NEXT SESSION

**Written by:** Session 2026-03-04 (environment setup)
**Date:** 2026-03-04

## Immediate Task

Start the source engine SPEC (Phase 2, Round 1 per the archived roadmap).

## Context

No SPECs have been written yet. Phase 1 (structural cleanup) is complete. The source engine is the pipeline entry point — no upstream dependencies.

The roadmap (`reference/archive/kr_definitive_roadmap_v2.md`) has detailed guidance for Round 1 under "Round 1: Source Engine", including key questions and schema impact notes. Consult it if useful, but it predates the design philosophy and scholar interface — don't let it constrain your thinking.

## Files to Read — IN THIS ORDER

The order matters. Think about what the engine SHOULD be before seeing what it currently IS.

**Phase 1 — Understand the vision and the user (read these FIRST):**
1. `reference/DOMAIN.md` — the core identity ("KR IS Rayane's knowledge") and scholarly domain grounding. This shapes every design decision. Pay special attention to "Design Implications" — these are concrete requirements for the source engine.
2. `reference/USER_SCENARIOS.md` — 5 concrete scenarios showing what Rayane actually experiences. These are your acceptance tests. Every feature in your SPEC must serve at least one scenario. List which scenarios in §1.

**Phase 2 — Understand the architecture:**
3. `VISION.md` §7.1–§7.4 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
4. `schemas/source_metadata.json` (234L) — current output schema
5. `schemas/SCHEMA_ANALYSIS.md` (329L) — pipeline schema overview

**Phase 3 — Now look at existing code and reference (after you've formed your own vision):**
6. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec. This describes the OLD system. Use it to understand what exists, NOT as a template for what to build.
7. `engines/source/reference/edge_cases.md` (127L) — known edge cases
8. `engines/source/src/intake.py` (1476L) — current source ingestion code
9. `engines/source/src/enrich.py` (580L) — metadata enrichment
10. `engines/source/src/corpus_audit.py` (228L) — corpus validation

**Phase 4 — Research:**
11. `reference/RESOURCES.md` — cataloged tools and possibility research starting points
12. Then do web searches: resource survey + possibility research per the workflow

**CRITICAL: After Phase 1 and before Phase 3, pause and think.** Write down (in your working memory, not a file) what the source engine SHOULD be if you could design it from scratch for the goal of making Rayane an unprecedented scholar. THEN read the existing code and see how it compares. Don't let the existing code shrink your vision.

## Decisions Needed

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- Shamela-specific fields: what evolves from current `intake_metadata.json` for KR?
- What transformative capabilities does this engine provide? (§4.B — your ideas)
- What does the source engine produce that the scholar interface (interface/scholar/) will need? Design with that consumer in mind.

**Note:** The scholar interface and user model (shared/user_model/) were added as D-016 and D-017. The roadmap doesn't cover them — they're extensions beyond the original 7+4 architecture. Their SPECs should be written after the 7 engine SPECs and 4 shared component SPECs, or when the architect judges it's the right time.

## Pending Owner Questions

None currently. The SPEC process will likely surface domain questions about Islamic scholarly source types and the owner's acquisition preferences.

## New Decisions Since Last SPEC Session

No previous SPEC sessions — this is the first. Read all of kr_decisions.md (D-001 through D-018).

## What the Last Session Did

Set up the complete autonomous working environment: design philosophy (Claude as creative mind), core identity (KR IS Rayane's knowledge), domain primer, user scenarios, scholar interface, user model, 25-criterion Perfection Standard, session mechanics.

## Quality Note

This is the first SPEC. Every future session will read it and calibrate to its quality level. If this SPEC is conservative and incremental, every subsequent SPEC will be too. If this SPEC is ambitious, deeply-researched, and precisely specified, the bar rises for the entire project. Write the SPEC you'd want to read if you were Session 2.
