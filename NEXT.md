# NEXT SESSION

**Written by:** Session 2026-03-06 (Scholar Interface SPEC §1–§4.A)
**Date:** 2026-03-06

## Immediate Task

Continue the scholar interface SPEC (interface/scholar/SPEC.md) from §4.B (Transformative Capabilities) through §10. The core processing rules (§4.A) are complete — §4.B through §10 remain.

**Definition of done — this session is complete when:**
1. Scholar interface SPEC completed (all 10 sections)
2. VISION.md corrections based on scholar interface design insights (if any discovered during §4.B–§10 writing)
3. Any new decisions recorded in kr_decisions.md
4. Changes committed and pushed

## Context

The scholar interface SPEC §1–§4.A is complete (~450 lines). The seven §4.A subsections cover:
- §4.A.1 — Guiding: curriculum generation, daily session orchestration
- §4.A.2 — Answering: query classification, retrieval strategy, response generation, stale entries, multi-turn conversation, book briefing
- §4.A.3 — Teaching: Socratic assessment design, evaluation, spaced repetition orchestration, gap detection from assessments
- §4.A.4 — Discovering: new content alerts, cross-science connections, coverage gap alerting, scholarly briefings, contradiction surfacing
- §4.A.5 — Assisting: evidence compilation, writing assistance, tarjih scaffolding, lesson plan generation
- §4.A.6 — Navigating: science map, taxonomy browsing, scholar network exploration, temporal exploration
- §4.A.7 — Correction and feedback integration: error identification, correction routing, pattern detection

Remaining sections:
- **§4.B — Transformative Capabilities.** This is the most important remaining section. Think deeply: what capabilities can the scholar interface provide that would make a world-class Islamic scholar say "I didn't know that was possible"? Some directions to explore:
  - Scholarly debate simulation (simulate historical debates between scholars)
  - Research gap cartography (map what hasn't been studied)
  - Adaptive explanation engine (explanations calibrated to exact prerequisite mastery)
  - Position evolution visualization (how a scholarly position mutated through centuries)
  - Intellectual influence propagation analysis
  - Question generation that reveals unstudied angles
- **§5 — Validation and Quality.** How to validate that responses are correctly grounded, citations are accurate, assessments are fair.
- **§6 — Consensus Integration.** Which interface operations use multi-model consensus.
- **§7 — Error Handling.** All error codes and recovery for the interface.
- **§8 — Configuration.** Parameters controlling interface behavior.
- **§9 — Current Implementation State.** Nothing exists — document that.
- **§10 — Test Requirements.** What must be tested.

## Files to Read — IN THIS ORDER

1. `interface/scholar/SPEC.md` — the partial SPEC. Read it first to continue seamlessly.
2. `reference/ENTRY_EXAMPLE.md` — refresh the quality target. Think about what §4.B capabilities would produce entries at that level or enable interactions beyond entries.
3. `engines/synthesis/SPEC.md` §4.B — the synthesis engine's transformative capabilities. The scholar interface should complement these, not duplicate them.
4. `shared/consensus/SPEC.md` §4.A — for §6 (Consensus Integration) of the scholar interface.
5. `shared/feedback/SPEC.md` §4 — for the correction integration details.

**Re-read only these files.** Do NOT re-read DOMAIN.md, USER_SCENARIOS.md, user_model SPEC, taxonomy SPEC, scholar_authority SPEC — their relevant content is already captured in the partial SPEC's design decisions.

## Decisions Needed

- **Curriculum knowledge base format.** The SPEC references a "curriculum knowledge base" (§4.A.1.1) — a structured data file per science encoding classical text progressions. What format? YAML? Where does it live? Who populates it (the architect hardcodes initial progressions, or the owner provides them, or the interface infers them)?
- **Arabic embedding model selection.** §4.A.2.2 references semantic similarity for query-to-topic matching. Which model? This needs research.
- **Session context persistence.** §4.A.2.5 says session context is in-memory. Should any cross-session context be persisted beyond what the user model captures?

## Pending Owner Questions

None.

## What This Session Did

Started the scholar interface SPEC — the most important SPEC in the project. Completed §1 through §4.A (~450 lines) covering all six capability domains (Guiding, Answering, Teaching, Discovering, Assisting, Navigating), the correction feedback loop, and the input/output contracts. Researched Socratic AI tutoring systems, knowledge graph RAG architectures, and classical Islamic pedagogical progressions. Updated RESOURCES.md with findings.

## New Decisions

None (no new architectural decisions were needed — the scholar interface design follows from D-016, D-017, D-018, D-021, D-022, D-023, D-032, D-033, D-042).
