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
