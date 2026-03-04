# Synthesizing Engine — محرك التوليف

**Responsibility:** Generating encyclopedic entries from placed excerpts, enriched by metadata and LLM research (§6). This is the engine that produces the knowledge products the owner actually reads. Everything upstream exists to feed this engine.
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §6 (the entry definition)
3. VISION.md §2.3 (entry vocabulary)
4. `reference/ENTRY_EXAMPLE.md` — **THE quality target.** Read this first. This shows what a finished entry looks like and why metadata matters.
5. `reference/DOMAIN.md` — especially: "Core Scholarly Methodology Concepts," "Evidence Hierarchy and Hadith Methodology," "Scholarly Integrity Risks," and the synthesizing engine section in "Design Implications"
6. Input boundary: placed excerpts from taxonomy engine + ALL upstream metadata
7. Output boundary: entries → scholar interface (interface/scholar/)

## Current State
No code exists. This is entirely new development. No ABD equivalent existed.

Code: 0L.
Tests: 0.
Reference: 0 docs.

## Key Constraints
1. **Factual layer is traceable** (§6.4): every factual claim must trace to specific excerpts. No unattributed scholarly claims.
2. **School-group cardinality** (§6.2): where schools exist, each school-group gets its own entry. Entries from different schools are never mixed.
3. **Verified-only factual layer** (§6.2): flagged excerpts never appear in the factual layer. Analytical layer may reference flagged content; critical analysis section is structurally separate.
4. **Three input sources (D-023):** This engine consumes (1) excerpt text content, (2) the full metadata chain from all upstream engines (author bios, dates, school affiliations, teacher-student chains, work genres, text fidelity signals), and (3) its own LLM research — actively adding context, connections, and scholarly analysis beyond what any individual source says. Metadata is synthesis FUEL, not documentation.
5. **Explanation quality (D-021):** Every entry must explain from the ground up, step by step, with explicit prerequisites, edge cases, and common misunderstandings addressed. The standard is "explain like I'm 5" CLARITY (not simplification) — maximum navigability of complex ideas.
6. **Scholarly methodology awareness:** Must distinguish خلاف types (verbal vs. substantive, respected vs. aberrant). Must perform تحرير المسألة (precise issue formulation) before presenting positions. Must track evidence types (Quran, hadith, ijma, qiyas) and hadith grading. Must identify abrogated content.
7. **Anti-bias:** Must not let library composition bias (more sources from one school) distort scholarly landscape representation. Must distinguish "appears more in our library" from "is the majority scholarly position."
