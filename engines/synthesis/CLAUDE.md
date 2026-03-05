# Synthesizing Engine — محرك التوليف

**Responsibility:** Generating encyclopedic entries from placed excerpts (§6, D-005). This is the engine that produces the knowledge products the owner actually reads. Everything upstream exists to feed this engine.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. **This engine's SPEC.md** — the sole governing document. Read it first.
2. `reference/ENTRY_EXAMPLE.md` — THE quality target. Shows what a finished entry looks like.
3. VISION.md §6 (entry definition) and §2.4 (entry vocabulary).
4. `reference/DOMAIN.md` — especially: "Core Scholarly Methodology Concepts," "Scholarly Integrity Risks," and the synthesizing engine section in "Design Implications."

## Current State
**Code:** 0L. No code exists. No ABD equivalent.
**Tests:** 0. No tests.

## Architecture at a Glance

**Five-phase pipeline:**
1. **Collection & Preparation** — gather excerpts, resolve metadata chains, detect duplicates
2. **Scholarly Analysis** — identify positions, classify khilaf, tahrir al-mas'ala, detect contradictions, find mu'tamad
3. **Narrative Construction** — build factual layer (excerpt-grounded) + analytical layer (engine-contributed)
4. **Integrity Verification** — 8 automated checks (citation completeness, school isolation, grounding type consistency, etc.)
5. **Finalization** — staleness hash, version management, atomic write

**Three input sources (D-023):** (1) excerpt text, (2) full upstream metadata chain (author bios, dates, schools, teacher-student links, work genres, text fidelity), (3) LLM research (historical context, connections beyond what sources state).

**The traceability boundary:** Factual layer → library-grounded only. Analytical layer → may include LLM-contributed context, marked via `grounding_type` field. Every claim has a citation with explicit grounding type.

## Key Constraints
1. **Entries in Arabic** (D-032).
2. **School isolation** (§6.2): per-school entries never mix excerpts from different schools.
3. **Verified-only factual layer** (§6.2): flagged excerpts → critical_analysis section only.
4. **Citation completeness**: every factual claim traceable to a specific excerpt.
5. **Owner constraints survive regeneration** (Scenario 8).
6. **Per-science customization** via SCIENCE.md hooks (school handling, evidence hierarchy, mu'tamad, abrogation, entry format).
7. **Staleness detection and prioritized regeneration** — user-initiated > study-focus > background.
8. **Diagnostic entries** when generation fails — never a silent gap.

## Transformative Capabilities (§4.B)
1. **Scholarly Consensus Mapping** — automatic consensus strength classification per position.
2. **Intellectual Genealogy Reconstruction** — teacher-student chain discovery and narrativization.
3. **Predictive Gap Synthesis** — provisional notes on missing perspectives with acquisition recommendations.
4. **Entry Quality Self-Assessment** — structured quality scoring across multiple dimensions.

## External Dependencies
- Instructor (structured LLM output)
- DSPy (pipeline orchestration, prompt optimization)
- LiteLLM (multi-provider routing for consensus)
- NetworkX (teacher-student graph traversal)
- Sentence-transformers (deduplication, contradiction detection)
