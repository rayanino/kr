# Synthesizing Engine — محرك التوليف

**Responsibility:** Generating encyclopedic entries from placed excerpt collections at leaves, and managing entry lifecycle — staleness detection and regeneration (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary). This engine is science-aware: it reads Level 3 per-science documentation for school handling and scholarly conventions.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §6 (the entry: definition, structure, staleness, quality)
3. VISION.md §2.2 (engine definition), §1.6 (entry as primary knowledge product), §2.4 (verified/flagged, school-group, staleness)
4. Input schema: `schemas/placed_excerpt` (placed excerpts read from library)
5. Output schema: `schemas/entry`

## Current State
Status: Not started. No synthesis code exists in ABD codebase (§12.3). This is entirely new development.
Tests: 0 passing, 0 failing.
Known issues: The OPEN QUESTION in §6.4 (analytical layer boundary — how far may synthesized reasoning go beyond source excerpts) needs resolution before SPEC.md can be finalized.

## Commands
```
cd engines/synthesis && python -m pytest tests/
```

## Key Constraints
1. **Factual layer is traceable** (§6.4): every factual claim must trace to specific excerpts. No unattributed scholarly claims.
2. **School-group cardinality** (§6.2): where schools exist, each school-group gets its own entry. Entries from different schools are never mixed.
3. **Verified-only factual layer** (§6.2): flagged excerpts never appear in the factual layer. Analytical layer may reference flagged content; critical analysis section is structurally separate.
