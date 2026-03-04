# NEXT SESSION

**Written by:** Session 2026-03-04-f
**Date:** 2026-03-04

## Immediate Task

Start the source engine SPEC (Round 1 per the roadmap).

## Context for This Task

No SPECs have been written yet. The source engine is the pipeline entry point — it's the natural first SPEC because it has no upstream dependencies. The advisory workplan and roadmap both recommend starting here.

## Files to Read First

1. `VISION.md` §7.1–§7.4 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
2. `engines/source/src/intake.py` (1476L) — current source ingestion code
3. `engines/source/src/enrich.py` (580L) — metadata enrichment
4. `engines/source/src/corpus_audit.py` (228L) — corpus validation
5. `engines/source/reference/ABD_INTAKE_SPEC.md` (795L) — ABD-era spec (most important reference)
6. `engines/source/reference/edge_cases.md` (127L) — known edge cases
7. `schemas/source_metadata.json` (234L) — current output schema
8. `schemas/SCHEMA_ANALYSIS.md` (329L) — pipeline schema overview
9. `reference/RESOURCES.md` — check for source-engine-relevant tools before designing

## Key Decisions Needed This Session

- Source identity model: what is a "source"? Does `book_id` → `source_id`? Multi-volume works?
- Source engine output: just `source_metadata.json` + frozen file, or other artifacts?
- Source registry: how does `library/sources/registry.yaml` work?
- Shamela-specific fields: what evolves from current `intake_metadata.json` for KR?

## Pending Owner Questions

None currently. But the SPEC process will likely surface domain questions about Islamic scholarly source types.

## What the Last Session Did

Established the scope boundary (Chat=architect, Code=builder), added mandatory web search requirement, created external resource catalog. No application architecture work was done — this was all coordination infrastructure.
