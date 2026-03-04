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
8. **Per-science behavior.** Different sciences have fundamentally different characteristics: fiqh has 4 active schools (entries are per-school), nahw has historical but extinct schools (entries trace evolution), tajwid has virtually no scholarly disagreement (entries state rules). SCIENCE.md (Level 3) customizes behavior, but the synthesizer must have HOOKS for this customization. See DOMAIN.md "Per-Science Behavioral Differences."
9. **Primary vs. secondary source weighting.** A definition from سيبويه's الكتاب (primary, foundational) carries more weight than the same definition paraphrased in a modern textbook. The synthesizer must cite primary sources directly and use secondary/reference sources (مراجع) to confirm or contextualize, not as primary evidence. Source authority level is in source metadata.
10. **Confidence-aware synthesis.** The synthesizer receives LLM confidence scores from upstream engines. Low-confidence attributions should be noted ("tentatively attributed to the Basran school") rather than stated as fact. The entry's quality is only as good as the weakest-confidence claim that isn't flagged.
11. **Staleness cascade management.** Adding a single large source (e.g., a 12-volume encyclopedia) can trigger hundreds of entry regenerations across hundreds of leaves. The synthesizer must handle this gracefully: batch processing, priority ordering (the owner's current study topics first), and incremental updates (only regenerate what the new excerpts affect). See DOMAIN.md "What Happens When the Library Grows."
12. **Entry versioning.** The owner may have studied an entry that later gets regenerated. The system must track entry versions so the scholar interface can say: "This entry was updated since you last studied it. Key changes: [summary]." This is essential for keeping the owner's knowledge current.
13. **Excerpt deduplication awareness.** Multiple sources at the same leaf may express the same content (especially hadith citations). The synthesizer must detect semantic redundancy and present each unique position ONCE (citing the strongest source), not present 5 redundant excerpts as 5 independent pieces of evidence.
14. **Ellipsis expansion.** Arabic scholarly texts commonly omit words "understood from context." When the owner's level is beginner, the entry must EXPAND these elliptical passages into explicit statements. When the owner is advanced, the terse original may be preferred.
15. **Library vs. LLM traceability boundary (CRITICAL).** The factual layer (§6.4) must contain ONLY library-grounded claims — every statement must trace to specific excerpts. LLM-contributed context (historical framing, institutional dynamics, connections beyond what sources state) belongs in the analytical layer or clearly marked contextual sections. An entry that mixes library evidence with LLM training data without marking the boundary destroys traceability. See DOMAIN.md "The Traceability Boundary."
16. **Physical citation in every entry.** Every factual claim must carry a citation the owner can physically verify: source title, author, edition, volume, page. The synthesizer assembles these from passage-level page metadata that flows through the pipeline.
