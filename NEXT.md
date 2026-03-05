# NEXT SESSION

**Written by:** Session 2026-03-05 (excerpting engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Write the taxonomy engine SPEC (Phase 2, Round 6).

**Output file:** `engines/taxonomy/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/taxonomy/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/taxonomy/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey
5. VISION.md defect ledger for §7.5–§7.8 produced (accumulated from source, normalization, passaging, atomization, excerpting SPEC work) — OR defer to synthesizing session if context is tight
6. `NEXT.md` is overwritten with handoff for the next session (synthesizing engine SPEC)
7. Self-review checklist passed — defects fixed before commit
8. All changes committed and pushed

## Context

The excerpting engine SPEC is complete (559 lines). It defines:
- Three-phase per-passage processing: boundary detection → self-containment evaluation → metadata enrichment (D-037, §4.A.1)
- Multi-model consensus for self-containment and school attribution (D-036, §6)
- Decontextualization prevention (§4.A.2) — detecting reported positions that could be misattributed
- Multi-layer excerpt handling with correct author attribution (§4.A.3)
- Evidence and hadith handling with grading capture and takhrij extraction (§4.A.4)
- Implicit reference resolution using scholar authority registry (§4.A.5)
- Cross-topic handling implementing §5.3 rules (§4.A.6)
- Three transformative capabilities: cross-excerpt scholarly dialogue detection, self-containment repair suggestions, scholarly argument completeness analysis (§4.B)

The taxonomy engine is the FOURTH Phase 2 engine — it receives draft excerpts and places them at leaves in science trees. It also manages tree evolution (when the tree needs to grow more granular) and tracks coverage. This is where excerpts become library content.

**Why this engine matters:** The taxonomy engine determines the structure of Rayane's knowledge. The tree IS the map of each science — its structure makes the science's internal logic visible (D-021). Placement decisions determine which excerpts appear together, which shapes entry generation. Evolution decisions determine whether the tree grows to capture finer distinctions. Coverage tracking reveals what Rayane knows and doesn't know.

## Files to Read — IN THIS ORDER

**Step 1 — Domain and user context (refresh only what's needed):**
1. `reference/DOMAIN.md` — "Taxonomy engine must:" section in Design Implications
2. `reference/PIPELINE_TRACE.md` — Stage 6 (taxonomy) inputs and outputs
3. `reference/USER_SCENARIOS.md` — Scenario 7 ("Show Me the Whole Science")

**Step 2 — Architecture:**
4. `VISION.md` §4 (science trees — the core specification) → `python3 scripts/extract_vision_sections.py 4`
5. `VISION.md` §2.3 (science tree vocabulary) — already included in §2 extraction
6. `engines/excerpting/SPEC.md` — the COMPLETE excerpting SPEC. §3 (output contract) defines exactly what the taxonomy engine receives. Read §3 carefully — it's your input contract.
7. `schemas/placed_excerpt.json` — current ABD-era placed excerpt schema (if it exists)
8. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code:**
9. `engines/taxonomy/CLAUDE.md` — current state overview
10. Any existing taxonomy code (check `engines/taxonomy/src/`)

**Step 4 — Research:**
11. `reference/RESOURCES.md` — tools already cataloged
12. Web searches: taxonomy management algorithms, knowledge graph tools for hierarchical classification, topic modeling for Arabic text, tree evolution/restructuring algorithms, coverage analytics

**Note:** The taxonomy engine has both classification (placing excerpts) and structural (evolving the tree) responsibilities. The resource survey should cover: (1) hierarchical classification approaches, (2) tree/ontology management libraries, (3) coverage analytics and gap detection.

## Key Design Questions

- **Placement algorithm:** How does the engine decide which leaf an excerpt belongs at? The excerpting engine proposes a leaf — does the taxonomy engine verify or re-classify?
- **Evolution triggers:** When does a leaf need to split? The §2.3 evolution signal concept. How many excerpts at a leaf before considering evolution?
- **Human gate for evolution:** Tree evolution is structural change — it affects all excerpts at the affected node. Must be human-gated. What does the evolution proposal look like?
- **Coverage metrics:** What dimensions? Per-school, per-source, per-evidence-type? What defines a "gap"?
- **Initial tree creation:** Where do the initial science trees come from? Are they manually created or seeded from a standard reference?
- **Narrative ordering:** §5.3 in DOMAIN.md mentions topics having a "storyline" — logical study order. How is this encoded in the tree?

## Pending Owner Questions

None currently pending.

## What This Session Did

Completed the excerpting engine SPEC (559 lines, all 10 sections). Key design: three-phase pipeline (D-037), multi-model consensus for self-containment and school attribution (D-036), decontextualization prevention, multi-layer handling, evidence/hadith grading capture with takhrij extraction, implicit reference resolution, cross-topic handling per §5.3. Updated CLAUDE.md, RESOURCES.md (ContextGem, LLM4IE papers, sentence-transformers). 

## New Decisions

D-036 (Multi-model consensus for excerpting — self-containment + school attribution). Two models from different providers; conservative scoring on disagreement.
D-037 (Three-phase excerpting pipeline — boundary → self-containment → enrichment). Separates concerns for independent validation and optimization.
