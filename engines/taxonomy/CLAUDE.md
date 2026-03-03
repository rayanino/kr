# Taxonomy Engine — محرك التصنيف

**Responsibility:** Placing excerpts at correct science tree leaves, managing taxonomy evolution, tracking coverage, and transitioning reviewed excerpts to placed status (§2.2, §2.4).
**Phase:** 2 (source-agnostic, below the normalization boundary). No source-format-specific logic permitted.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §4 (science trees: qualification, construction, evolution governance, schools)
3. VISION.md §2.2 (engine definition), §2.3 (tree vocabulary), §3.3 (within-leaf organization)
4. VISION.md §8 (quality architecture — this engine participates in all five defense layers)
5. Input schema: `schemas/excerpt` (draft excerpts from excerpting engine)
6. Output: placed excerpts written to `library/sciences/*/content/`; placed excerpt schema: `schemas/placed_excerpt`

## Current State
Status: Not started. ABD has taxonomy trees for 4 Arabic language sciences (~892 leaves total) in `taxonomy/`; to be moved to `library/sciences/` per §12.2. No placement or evolution code exists yet.
Tests: 0 passing, 0 failing.
Known issues: Evolution (§4.4) and coverage tracking not yet implemented. Placement logic not yet built.

## Commands
```
cd engines/taxonomy && python -m pytest tests/
```

## Key Constraints
1. **Zero orphans** (§4.4): after any evolution, every pre-existing excerpt must have a valid leaf. Invalid proposals must not reach the human gate.
2. **Sibling coherence** (§4.4): no excerpt should plausibly belong to more than one sibling after evolution. Overlap = invalid proposal.
3. **Topic-only branching** (§4.5): no node in any tree represents a school. Schools are within-leaf organization only.
