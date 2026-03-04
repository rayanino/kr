# Taxonomy Engine — محرك التصنيف

**Responsibility:** Placing excerpts at correct taxonomy leaves and managing tree evolution (§4, §5.5).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §4 (science trees), §5.5 (one-per-source diagnostic)
3. VISION.md §9 (human gates — taxonomy is the primary gate site)
4. Input boundary: draft excerpts from excerpting engine
5. Output boundary: placed excerpts → synthesizing engine

## Current State
Legacy code migrated from ABD. ABD design decisions have zero authority in KR (D-019).

Code: `engines/taxonomy/src/evolve_taxonomy.py` (2377L).
Tests: 109 tests in `engines/taxonomy/tests/`.
Reference: 1 ABD-era doc.
Taxonomy trees: `library/sciences/` (5 sciences with tree.yaml files).

## Key Constraints
1. **Zero orphans** (§4.4): after any evolution, every pre-existing excerpt must have a valid leaf. Invalid proposals must not reach the human gate.
2. **Sibling coherence** (§4.4): no excerpt should plausibly belong to more than one sibling after evolution. Overlap = invalid proposal.
3. **Human gate required for evolution** (§9): tree evolution proposals require owner approval.
4. **The tree IS the science map (D-021).** The taxonomy tree is not just an organizational tool — it is the owner's visualization of the entire science: every topic, how topics correlate, which are foundational vs. derived, what depends on what. The tree structure must make the science's internal logic visible to the scholar interface.
5. **Prerequisite edges.** The tree must track dependency relationships between topics beyond parent→child: "understanding X requires understanding Y." These are study-order dependencies used by the scholar interface for curriculum design and by the synthesizer for "prerequisites" sections in entries.
6. **Narrative ordering.** Topics at the same level have a pedagogical sequence: after المبتدأ comes الخبر, then نواسخ المبتدأ والخبر. This ordering must be explicit — it's the "storyline" the owner wants (D-021).
7. **Per-leaf scholarly landscape.** The taxonomy engine must track: which schools have positions at this leaf, how many sources cover it, what's the significance of this topic within the science. This data feeds both the synthesizer and the scholar interface.
8. **Cross-science topic links.** The same concept (e.g., الاستثناء) appears in multiple sciences with different treatments. Each science has its own leaf — these are NOT merged. But the taxonomy engine must record cross-science links ("nahw/الاستثناء is conceptually related to usul/الاستثناء") so the synthesizer can produce cross-science entries and the scholar interface can suggest connections (Scenario 3). See DOMAIN.md "Cross-Science Topic Overlap."
9. **Terminology synonym mapping.** The same concept may have different names across schools or periods (e.g., "المفعول له" vs. "المفعول من أجله"). The taxonomy must handle this — different names mapping to the same leaf. The synthesizer must note when scholars use different terminology for the same concept.
10. **Excerpt deduplication signal.** When 5 sources at the same leaf all say the same thing (common with hadith citations or well-known definitions), the taxonomy engine should detect semantic overlap and signal it to the synthesizer, so entries present the content ONCE (citing the strongest source) rather than redundantly.
11. **Evolution → entry cascade.** When a leaf SPLITS (one leaf becomes two children), existing excerpts must be re-placed at one of the children, and the parent's entry is replaced by two new entries at the children. When a leaf MERGES (rare — two siblings collapse), excerpts from both move to the merged leaf and the entry must be regenerated from the combined set. The taxonomy engine must produce a structured migration plan that the synthesizing engine consumes.
