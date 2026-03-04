# Passaging Engine — محرك التقطيع

**Responsibility:** Segmenting normalized content into passages (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §2.2 (passaging definition)
3. Input boundary: normalized package from normalization engine
4. Output boundary: passages → atomization engine

## Current State
Scaffold only, migrated from ABD. The boundary question (D-010) — whether `discover_structure.py`'s `build_passages()` belongs here or in normalization — is deferred to the normalization/passaging SPEC sessions. ABD design decisions have zero authority in KR (D-019).

Code: `engines/passaging/src/scaffold_passage.py` (279L).
Tests: 0.

## Key Constraints
1. **Source-agnostic** (§7.6): operates on normalized packages only. No format-specific logic.
2. **Passage boundaries must be deterministic** (§2.2): given the same normalized package, the same passages result.
3. **Passages are the unit of downstream processing** (§2.2): atomization and excerpting operate within passage boundaries.
