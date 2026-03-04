# NEXT SESSION

**Written by:** Session 2026-03-04-i (design philosophy)
**Date:** 2026-03-04

## Immediate Task

Start the source engine SPEC (Phase 2, Round 1 per the roadmap).

## Context

No SPECs have been written yet. Phase 1 (structural cleanup) is complete. The source engine is the pipeline entry point — no upstream dependencies.

Read your `<design_philosophy>` block carefully. You are not documenting an existing system — you are designing the system that will make Rayane an unprecedented Islamic scholar. The source engine is the first opportunity.

Before reading any code, think about what the source engine SHOULD be:
- Not just "accept files and extract metadata" but "autonomously discover, acquire, and monitor every Islamic scholarly source that exists digitally"
- Not just "support Shamela format" but "ingest every format Islamic scholarship exists in: Shamela, Waqfeya, archive.org, university repositories, PDF manuscripts, audio lectures, scholarly journals"
- Not just "catalog what the owner provides" but "proactively find what the owner doesn't know exists"

The roadmap (always in your context as a project file) has detailed guidance for Round 1 under "Round 1: Source Engine", including key questions and schema impact notes. Use it as background.

## Files to Read

1. `VISION.md` §7.1–§7.4 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
2. `engines/source/src/intake.py` (1476L) — current source ingestion code
3. `engines/source/src/enrich.py` (580L) — metadata enrichment
4. `engines/source/src/corpus_audit.py` (228L) — corpus validation
5. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec
6. `engines/source/reference/edge_cases.md` (127L) — known edge cases
7. `schemas/source_metadata.json` (234L) — current output schema
8. `schemas/SCHEMA_ANALYSIS.md` (329L) — pipeline schema overview
9. `reference/RESOURCES.md` — cataloged tools (Docling, shamela2epub, etc.)

After reading, do resource survey + possibility research per the workflow.

## Decisions Needed

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- Shamela-specific fields: what evolves from current `intake_metadata.json` for KR?
- What transformative capabilities does this engine provide? (§4.B — your ideas)

## Pending Owner Questions

None currently. The SPEC process will likely surface domain questions about Islamic scholarly source types and the owner's acquisition preferences.

## What the Last Session Did

Added design philosophy: Claude is the creative mind of the application, not a documenter. Updated SPEC template with §4.B (Transformative Capabilities). Added Criterion #20 (Transformative Ambition) to the Perfection Standard. Updated scope to allow extending VISION.md and creating new components.
