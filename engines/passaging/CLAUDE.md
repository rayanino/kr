# Passaging Engine — محرك التقطيع

**Responsibility:** Dividing normalized content into passages — appropriately sized, topically coherent processing units for downstream engines (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary). No source-format-specific logic permitted.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §2.2 (engine definition, source-agnostic, science-agnostic)
3. Input schema: `schemas/normalized_package`
4. Output schema: `schemas/passage`

## Current State
Status: Not started. No dedicated passaging code exists in ABD; passaging was embedded in the monolithic extraction logic.
Tests: 0 passing, 0 failing.
Known issues: Passaging logic must be separated from extraction logic during restructure.

## Commands
```
cd engines/passaging && python -m pytest tests/
```

## Key Constraints
1. **Source-agnostic** (§2.2): operates on normalized content only. No knowledge of source format or acquisition method.
2. **Science-agnostic** (§2.2): core algorithm does not change based on which science the content belongs to.
3. **Not structure discovery** (§2.2): normalization engine identifies source-native structure (headings, chapters); this engine creates processing units from that structure.
