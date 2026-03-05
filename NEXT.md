# NEXT SESSION

**Written by:** Session 2026-03-05 (taxonomy engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Write the synthesizing engine SPEC (Phase 2, Round 7 — the final engine SPEC).

**Output file:** `engines/synthesizing/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/synthesizing/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/synthesizing/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey
5. `NEXT.md` is overwritten with handoff for the next session (cross-SPEC consistency verification + VISION corrections)
6. Self-review checklist passed — defects fixed before commit
7. All changes committed and pushed

## Context

The taxonomy engine SPEC is complete (562 lines). It defines:
- Two-stage placement algorithm: candidate generation (3 sources: excerpting proposal + LLM search + embedding similarity) → candidate ranking (D-038, §4.A.1)
- Limited multi-model consensus for ambiguous placements only (D-039, §6)
- Four-phase tree construction workflow: Research → Draft → Validation → Commitment (§4.A.3)
- Five evolution signal types with accumulation threshold and all four §4.4 invariant checks (§4.A.5)
- Six coverage gap types: school, source diversity, temporal, evidence, prerequisite, empty (§4.A.6)
- Atomic evolution application with full rollback (§4.A.7)
- Semantic deduplication detection via embeddings (§4.A.8)
- Cross-science link management (§4.A.9) and terminology synonym management (§4.A.10)
- Three transformative capabilities: topic significance scoring, difficulty estimation, corpus-driven tree construction (§4.B)

The synthesizing engine is the FINAL Phase 2 engine — it receives ALL placed excerpts at a leaf plus ALL their metadata chains plus the taxonomy tree context, and produces encyclopedic entries. This is where all upstream work culminates. The synthesizer also does its own research (D-023) — it adds context, connections, and analysis beyond what sources explicitly say.

**Why this engine matters:** The synthesizing engine produces the primary knowledge product (D-005). The entry at each leaf IS what Rayane knows about that topic. Entry quality directly determines KR's value. The target quality is defined by `reference/ENTRY_EXAMPLE.md`. Every design decision in this SPEC must serve producing entries at that level.

## Files to Read — IN THIS ORDER

**Step 1 — Domain and user context:**
1. `reference/DOMAIN.md` — "Synthesizing engine must:" section in Design Implications
2. `reference/ENTRY_EXAMPLE.md` — THE quality target. Read this FIRST and keep it in mind throughout.
3. `reference/PIPELINE_TRACE.md` — Stage 7 (synthesizing) inputs and outputs
4. `reference/USER_SCENARIOS.md` — Scenarios 1-6 all culminate in synthesis

**Step 2 — Architecture:**
5. `VISION.md` §6 (entry generation — if it exists as a section) → `python3 scripts/extract_vision_sections.py 6`
6. `VISION.md` §2.4 (knowledge content vocabulary — entry, school-group, verified/flagged)
7. `engines/taxonomy/SPEC.md` — the COMPLETE taxonomy SPEC. §3 (output contract) defines exactly what the synthesizer receives. Read §3 carefully — it's your input contract.
8. `schemas/entry.json` — current ABD-era entry schema
9. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code:**
10. `engines/synthesizing/CLAUDE.md` — current state overview
11. Any existing synthesizing code (check `engines/synthesizing/src/`)

**Step 4 — Research:**
12. `reference/RESOURCES.md` — tools already cataloged (especially RAG frameworks, multi-document summarization)
13. Web searches: multi-document scholarly summarization, Arabic text generation quality, LLM-based encyclopedic article generation, citation-grounded synthesis, contradiction detection in text corpora

## Key Design Questions

- **Entry structure:** What does an entry look like structurally? Reference/ENTRY_EXAMPLE.md shows the target, but the SPEC must define the schema precisely.
- **Factual vs. analytical layer:** §2.4 defines two layers. How does the engine generate each? How are they distinguished in the output?
- **Three input sources (D-023):** (1) excerpt content, (2) metadata chain, (3) LLM research. How does the engine orchestrate these three sources?
- **School-group entries:** When a science has schools, each school-group gets its own entry. What's the generation workflow?
- **Staleness and regeneration:** When should entries be regenerated? What triggers staleness?
- **Library composition bias:** How does the synthesizer avoid presenting corpus bias as scholarly consensus?
- **Entry versioning:** Are entries versioned? What happens when an entry is regenerated?

## Pending Owner Questions

None currently pending.

## What This Session Did

Completed the taxonomy engine SPEC (562 lines, all 10 sections). Key design: two-stage placement algorithm (D-038), limited consensus for ambiguous placements only (D-039), four-phase tree construction with validation, five evolution signal types with invariant enforcement, six coverage gap types, semantic deduplication, cross-science links, terminology synonyms. Three transformative capabilities: topic significance scoring, difficulty estimation, corpus-driven tree construction. Updated CLAUDE.md, RESOURCES.md (NetworkX, hierarchical text classification research, nxontology).

## New Decisions

D-038 (Two-stage placement algorithm with three candidate sources).
D-039 (Limited multi-model consensus for taxonomy — placement only, ambiguous range).
