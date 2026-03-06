# NEXT SESSION

**Written by:** Session 2026-03-06 (Scholar Authority SPEC)
**Date:** 2026-03-06

## Immediate Task

Begin the scholar interface SPEC (interface/scholar/SPEC.md). This is the user-facing intelligence layer — the primary product that Rayane interacts with. All engine and shared component SPECs are now complete; the scholar interface consumes their outputs.

**This is the most important SPEC in the project.** The engines exist to feed the interface. If the engines work perfectly but the interface doesn't guide study, KR has failed (DOMAIN.md: "The scholar interface is not optional or secondary — it is the primary product").

**Definition of done — this session is complete when:**
1. Scholar interface SPEC started with at least §1–§4.A done (the interface is large enough to take 2–3 sessions)
2. Any new decisions recorded in kr_decisions.md
3. Changes committed and pushed

**Note: this SPEC will almost certainly take 2–3 sessions** due to the breadth of the interface's five capability domains (Answering, Teaching, Discovering, Assisting, Navigating — see D-016). Plan accordingly: aim for depth over speed, commit at clean section boundaries.

## Context

All shared component SPECs are now complete:
- **consensus** — multi-model dispatch (D-041)
- **validation** — schema + semantic validation
- **human_gate** — owner decision checkpoints (D-042 update done)
- **feedback** — correction and pattern learning
- **user_model** — engagement tracking, knowledge state, gaps, curriculum
- **scholar_authority** — canonical identities, teacher-student graph, disambiguation

All engine SPECs are complete:
- source, normalization, passaging, atomization, excerpting, taxonomy, synthesis

The scholar interface sits on top of everything. It reads: placed excerpts (from taxonomy), entries (from synthesis), scholar records (from scholar_authority), user state (from user_model), taxonomy trees (from taxonomy engine), and source metadata (from source engine). It writes to: user_model (engagement events, assessment results).

## Files to Read — IN THIS ORDER

1. `reference/DOMAIN.md` — particularly "The User" section (study profile, frustrations, design implications for scholar interface) and "Core Identity" (KR is Rayane's knowledge)
2. `reference/USER_SCENARIOS.md` — ALL scenarios. The scholar interface is the component that makes these scenarios real. Every scenario describes an interface interaction.
3. `interface/scholar/CLAUDE.md` — existing orientation file with the five capability domains
4. `shared/user_model/SPEC.md` — the interface reads and writes user state. §4.A.1 (engagement tracking), §4.A.2 (knowledge state), §4.A.4 (expertise levels), §4.A.5 (gap analysis), §4.A.6 (curriculum)
5. `engines/synthesis/SPEC.md` §3 — entry schema that the interface presents
6. `engines/taxonomy/SPEC.md` §3 — taxonomy tree queries that the interface uses for navigation
7. `shared/scholar_authority/SPEC.md` §4.A.8 — the serving interface for scholar data
8. `reference/ENTRY_EXAMPLE.md` — the quality target for what the interface presents

## Decisions Needed

- **How does the interface generate study curricula?** DOMAIN.md says KR must design complete study paths from zero. Where does pedagogical sequencing knowledge come from? Options: (a) hardcoded classical progressions (mutun → shuruh → hawashi) per SCIENCE.md, (b) inferred from prerequisite metadata in taxonomy trees, (c) LLM research on classical Islamic pedagogy, (d) combination.
- **What is the interaction modality?** Is the interface a chat-like conversational UI, a structured dashboard, or both? The owner's "living scholarly partner" model suggests conversational, but curriculum tracking and science maps suggest structured views.
- **Socratic assessment design.** How does the interface test understanding? Free-form questions? Multiple choice? Scenario-based? What level of assessment rigor is appropriate?

## Pending Owner Questions

None.

## What This Session Did

Completed shared/scholar_authority SPEC (all 10 sections, ~500 lines). Key designs: five-signal weighted matching algorithm with conservative bias (name alone capped below auto-match), teacher-student graph as first-class queryable data structure (chain/connection/subgraph queries), progressive enrichment with per-field provenance tracking, career phase modeling for scholars who changed positions, three external enrichment sources (OpenITI, LLM inference, Wikidata), and three transformative capabilities (intellectual genealogy as knowledge product, scholarly influence network analysis, automatic disambiguation rule generation). Updated human gate SPEC §4.A.4 per D-042 (confidence data now from user model). Updated RESOURCES.md with entity resolution libraries and Islamic scholar databases.

## New Decisions

None (no new architectural decisions were needed — the scholar authority design follows naturally from D-024, D-025, D-023).
