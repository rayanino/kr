# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Grouping atoms into self-contained excerpts and enriching them with all required metadata (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary). No source-format-specific logic permitted.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §5 (the excerpt: self-containment, boundaries, metadata, diagnostics)
3. VISION.md §2.2 (engine definition), §2.4 (excerpt lifecycle, school, content type)
4. Input schema: `schemas/atoms`
5. Output schema: `schemas/excerpt` (draft excerpts with proposed leaf)

## Current State
Status: Migrated from ABD. Code in `engines/excerpting/src/` (extract_passages.py, assemble_excerpts.py).
Tests: 258 tests in `engines/excerpting/tests/` (test_extraction.py, test_assembly.py).
Known issues: Separation from atomization logic. Science-specific metadata enrichment (§5.4) depends on science scope flowing through pipeline (§7.3).

## Commands
```
cd engines/excerpting && python -m pytest tests/
```

## Key Constraints
1. **Self-containment is the defining property** (§5.1): every excerpt must be independently understandable. An excerpt that requires another excerpt to make sense is defective.
2. **Taxonomy-independence** (§5.2): group first by content coherence, then place. The taxonomy has zero influence on grouping decisions.
3. **Content integrity over taxonomic precision** (§5.3 Rule 3): never break an excerpt's self-containment to achieve cleaner taxonomy placement.
