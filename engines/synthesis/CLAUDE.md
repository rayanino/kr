# Synthesizing Engine — محرك التوليف

**Responsibility:** Generating encyclopedic entries from placed excerpts (§6).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §6 (the entry definition)
3. VISION.md §2.3 (entry vocabulary)
4. Input boundary: placed excerpts from taxonomy engine
5. Output boundary: entries → scholar interface (interface/scholar/)

## Current State
No code exists. This is entirely new development. No ABD equivalent existed.

Code: 0L.
Tests: 0.
Reference: 0 docs.

## Key Constraints
1. **Factual layer is traceable** (§6.4): every factual claim must trace to specific excerpts. No unattributed scholarly claims.
2. **School-group cardinality** (§6.2): where schools exist, each school-group gets its own entry. Entries from different schools are never mixed.
3. **Verified-only factual layer** (§6.2): flagged excerpts never appear in the factual layer. Analytical layer may reference flagged content; critical analysis section is structurally separate.
