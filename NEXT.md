# NEXT SESSION

**Written by:** Session 2026-03-04-h (coordination audit)
**Date:** 2026-03-04

## Immediate Task

Start the source engine SPEC (Phase 2, Round 1 per the roadmap). Resource survey needed first.

## Context

No SPECs have been written yet. Phase 1 (structural cleanup) is complete. The source engine is the pipeline entry point — no upstream dependencies. The roadmap (always in your context as a project file) has detailed guidance for Round 1 under "Round 1: Source Engine", including key questions and schema impact notes.

Read the `<design_philosophy>` block in your instructions carefully. The source engine is the first opportunity to design something transformative. Don't just document how Shamela files get ingested — design an engine that autonomously discovers and acquires Islamic scholarly sources across the entire web, tracks new publications, follows citation networks, and monitors manuscript repositories. The owner's explicit mandate: no limiting factors other than the extent you can think and reason to.

## Files to Read

1. `VISION.md` §7.1–§7.4 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
2. `engines/source/src/intake.py` (1476L) — current source ingestion code
3. `engines/source/src/enrich.py` (580L) — metadata enrichment
4. `engines/source/src/corpus_audit.py` (228L) — corpus validation
5. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec (most important reference)
6. `engines/source/reference/edge_cases.md` (127L) — known edge cases
7. `schemas/source_metadata.json` (234L) — current output schema
8. `schemas/SCHEMA_ANALYSIS.md` (329L) — pipeline schema overview
9. `reference/RESOURCES.md` — check for source-engine-relevant tools before designing

## Decisions Needed

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- Shamela-specific fields: what evolves from current `intake_metadata.json` for KR?

## Pending Owner Questions

None currently. The SPEC process will likely surface domain questions about Islamic scholarly source types.

## What the Last Session Did

Coordination audit: found and fixed 21 defects across the project setup in two audit passes. Rewrote PROJECT_INSTRUCTIONS.md (git config, error handling, roadmap acknowledgment, SPEC file locations, context management, blocking question guidance, multi-session continuity). Rewrote CLAUDE.md (pure repo map). Rewrote HOW_TO_START.md. Cleaned STATUS.md. Archived PREPARATORY_WORKPLAN.md. Created missing content/ dirs.
