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

These are all ABD-era artifacts. ABD was a narrow Shamela-only tool; its decisions have zero authority (D-019). Read them to understand what code exists, NOT as a template for what to build. If your vision from Phase 1-2 conflicts with what ABD does, your vision wins.

6. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec for Shamela intake only
7. `engines/source/reference/edge_cases.md` (127L) — known edge cases (Shamela-specific)
8. `engines/source/src/intake.py` (1476L) — current source ingestion code (Shamela only)
9. `engines/source/src/enrich.py` (580L) — metadata enrichment (Shamela only)
10. `engines/source/src/corpus_audit.py` (228L) — corpus validation

**Phase 4 — Research:**
11. `reference/RESOURCES.md` — cataloged tools and possibility research starting points
12. Then do web searches: resource survey + possibility research per the workflow

**CRITICAL: After Phase 1 and before Phase 3, pause and think.** Write down (in your working memory, not a file) what the source engine SHOULD be if you could design it from scratch for the goal of making Rayane an unprecedented scholar. THEN read the existing code and see how it compares. Don't let the existing code shrink your vision.

## Known VISION §7 Gaps (for SPEC → VISION correction step)

VISION §7 explicitly defers 8 topics to "Level 2" (the SPEC). The SPEC must resolve all of them:
- Deduplication criteria and registry structure
- Repository-specific interface logic
- Relevance evaluation criteria
- Metadata fields, data types, and validation rules
- Enrichment write-back mechanism
- Trustworthiness evaluation criteria and threshold
- Normalized package contents and schema
- Discovery strategies

VISION §7 is SILENT on topics DOMAIN.md requires:
- Work-to-work relationships (sharh→matn chains) — not mentioned at all
- Author disambiguation — not mentioned at all
- Tahqiq quality criteria — mentioned only as "editor (محقق)" in metadata
- Edition variant tracking — mentioned only as "edition information"

These are gaps the SPEC fills, not contradictions the SPEC corrects.

## Decisions Needed

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
  **Known tension:** VISION §2.5 defines "Work" (مؤلَّف) narrowly as linking volumes of a multi-volume work. DOMAIN.md defines it broadly as the abstract intellectual creation (grouping different tahqiq editions). Both concepts are real — the architect must resolve whether `work_id` covers both or whether two levels of grouping are needed.
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- What metadata model does KR need? (The current schema has Shamela-specific fields from ABD — design from first principles for ALL source types, not from the existing schema.)
- Manual acquisition workflow: owner provides scans/photos of physical books (no digital version exists), or files manually downloaded from login-gated sites. How does the source engine ingest these? What metadata can be auto-extracted vs. what must the owner provide?
- What transformative capabilities does this engine provide? (§4.B — your ideas)
- What does the source engine produce that the scholar interface (interface/scholar/) will need? Design with that consumer in mind.

**ABD legacy rule (D-019):** The existing code and reference docs are from ABD, a narrow Shamela-only tool. ABD design decisions have ZERO authority in KR. Read the code and reference docs to understand what currently exists, but design the SPEC from first principles for a system that acquires sources from ANY scholarly repository in ANY format.

**Note:** The scholar interface and user model (shared/user_model/) were added as D-016 and D-017. The roadmap doesn't cover them — they're extensions beyond the original 7+4 architecture. Their SPECs should be written after the 7 engine SPECs and 4 shared component SPECs, or when the architect judges it's the right time.

## Pending Owner Questions

None currently. The SPEC process will likely surface domain questions about Islamic scholarly source types and the owner's acquisition preferences.

## New Decisions Since Last SPEC Session

No previous SPEC sessions — this is the first. Read all of kr_decisions.md (D-001 through D-019). Pay special attention to D-018 (core identity) and D-019 (ABD legacy rule).

## What the Last Session Did

Set up the complete autonomous working environment: design philosophy (Claude as creative mind), core identity (KR IS Rayane's knowledge), domain primer, user scenarios, scholar interface, user model, 25-criterion Perfection Standard, session mechanics.

## Quality Note

This is the first SPEC. Every future session will read it and calibrate to its quality level. If this SPEC is conservative and incremental, every subsequent SPEC will be too. If this SPEC is ambitious, deeply-researched, and precisely specified, the bar rises for the entire project. Write the SPEC you'd want to read if you were Session 2.
