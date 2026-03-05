# NEXT SESSION

**Written by:** Session 2026-03-05 (atomization engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Write the excerpting engine SPEC (Phase 2, Round 5).

**Output file:** `engines/excerpting/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/excerpting/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/excerpting/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey
5. VISION.md defect ledger for §7.5–§7.8 produced (accumulated from source, normalization, passaging, atomization SPEC work)
6. `NEXT.md` is overwritten with handoff for the next session (taxonomy engine SPEC)
7. Self-review checklist passed — defects fixed before commit
8. All changes committed and pushed

## Context

The atomization engine SPEC is complete (580 lines). It defines:
- Five-phase per-passage processing: pre-screen → rule-based pre-detection → LLM atomization → post-processing → self-validation (§4.A.1)
- Two-tier atom type taxonomy: 7 structural types × 16 scholarly function types (D-034, §4.A.3)
- Rule-based pre-detection for Quran (canonical text matching), hadith markers, evidence markers, poetry (§4.A.4)
- LLM-driven classification using Instructor/Pydantic for structured output (§4.A.5)
- Multi-layer attribution algorithm with LLM layer override capability (§4.A.6)
- Six format-specific strategies matching passaging engine's formats (§4.A.7)
- Character offset integrity with correction algorithm (§4.A.8)
- Seven self-validation checks (§4.A.10)
- No multi-model consensus (D-035) — single model with escalation
- Three transformative capabilities: rhetorical structure analysis, implicit layer transition detection, atom type distribution analytics (§4.B)

The excerpting engine is the THIRD Phase 2 engine — it receives atoms and groups them into self-contained excerpts. This is where the transition from "text processing" to "knowledge products" happens. Excerpts are the primary building blocks of the library. They must be self-contained, correctly attributed, and carry all metadata the synthesizer needs.

**Why this engine matters:** The excerpting engine determines what constitutes a "unit of knowledge." It decides which atoms form a coherent teaching unit, what school/topic/author metadata each excerpt carries, and whether the excerpt is self-contained. These decisions directly shape the quality of entries the synthesizer produces. A bad excerpting boundary (splitting a definition from its evidence, or merging two unrelated definitions) propagates as a bad entry.

## Files to Read — IN THIS ORDER

**Step 1 — Domain and user context (refresh only what's needed):**
1. `reference/DOMAIN.md` — "Excerpting engine must:" section in Design Implications
2. `reference/PIPELINE_TRACE.md` — Stage 5 (excerpting) inputs and outputs

**Step 2 — Architecture:**
3. `VISION.md` §2.4 (excerpt definition) and §5 (excerpting) → `python3 scripts/extract_vision_sections.py 2 5`
4. `engines/atomization/SPEC.md` — the COMPLETE atomization SPEC. §3 (output contract) defines exactly what the excerpting engine receives. Read §3 carefully — it's your input contract.
5. `schemas/excerpt.json` — current ABD-era excerpt schema
6. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code:**
7. `engines/excerpting/CLAUDE.md` — current state overview
8. Any existing excerpting code (check `engines/excerpting/src/`)
9. `engines/excerpting/reference/` — ABD-era excerpting specs

**Step 4 — Research:**
10. `reference/RESOURCES.md` — tools already cataloged (especially Instructor, DSPy)
11. Web searches: LLM-based information extraction, self-contained text unit detection, multi-document metadata enrichment, scholarly text excerpt quality metrics

**Note:** The excerpting engine is the most LLM-intensive Phase 2 engine — it must understand Arabic scholarly text well enough to determine self-containment, attribute scholars, classify topics, and enrich with metadata. The resource survey should focus on: (1) structured extraction frameworks (Instructor, DSPy), (2) self-containment detection in text units, (3) Arabic NER for scholar identification in classical texts.

## Key Design Questions

- **Self-containment criteria:** What makes an excerpt self-contained? A reader should be able to understand what it teaches without needing other excerpts. But how is this operationalized?
- **Excerpt boundaries:** The excerpting engine groups atoms. What determines that these 5 atoms belong together but that 6th atom starts a new excerpt?
- **Metadata enrichment:** Each excerpt needs topic, school, author, content type, proposed leaf. How much of this comes from atom types vs. LLM analysis?
- **Cross-passage excerpts:** The passage containment rule (D-011) says excerpts cannot span passages. But what about multi-passage topics? How does the engine signal that two excerpts from adjacent passages cover the same topic?
- **Consensus usage:** Unlike atomization (D-035), excerpting decisions are higher-stakes. Does the excerpting engine use multi-model consensus?

## Pending Owner Questions

None currently pending.

## What This Session Did

Completed the atomization engine SPEC (580 lines, all 10 sections). Key design: two-tier atom type taxonomy (7 structural × 16 scholarly function types, D-034), rule-based + LLM hybrid processing, no consensus for atomization (D-035). Updated CLAUDE.md, RESOURCES.md (Quran_Detector, Instructor, hadith segmenter, CANERCorpus, Arabic discourse segmentation research). VISION defect ledger still deferred to post-excerpting session (accumulating defects from all Phase 2 engine SPECs).

## New Decisions

D-034 (Two-tier atom type system — structural type + scholarly function). Atoms classified on two independent dimensions.
D-035 (No multi-model consensus for atomization). Single model with escalation fallback.
