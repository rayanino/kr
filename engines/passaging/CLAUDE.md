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
4. **Passage quality affects everything downstream.** A bad passage boundary (splitting a topic in the middle of a sentence, combining unrelated topics) forces the excerpting engine to either produce a defective excerpt or span boundaries — which §5.3 forbids. Passage construction is the FOUNDATION for excerpt quality.
5. **Metadata pass-through (D-023).** Passages must carry all source and normalization metadata. The passage adds its own positional metadata (division path, sequence number) but must preserve everything upstream.
6. **Islamic text structural awareness.** Arabic scholarly texts have conventions: بسملة opens books, باب/فصل/مسألة mark structural divisions, قال المصنف signals return to the main text author after commentary. The passaging engine (or normalization — the boundary question D-010) must use these conventions for intelligent boundary placement.
