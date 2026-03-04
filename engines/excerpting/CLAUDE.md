# Excerpting Engine — محرك الاقتطاف

**Responsibility:** Grouping atoms into self-contained excerpts (§5).
**Phase:** 2 (source-agnostic, below the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §5 (the excerpt definition — the core intellectual specification)
3. VISION.md §2.3 (excerpt vocabulary)
4. Input boundary: atoms from atomization engine
5. Output boundary: draft excerpts → taxonomy engine

## Current State
Legacy code migrated from ABD. The excerpting engine is the intellectual core of the pipeline — ABD's reference docs encode months of extraction experience. However, ABD design decisions have zero authority in KR (D-019). Read ABD reference docs for domain knowledge, not as binding rules.

Code: `engines/excerpting/src/` (extract_passages.py 2288L, assemble_excerpts.py 1021L).
Tests: 258 tests in `engines/excerpting/tests/`.
Reference: 10 ABD-era docs (including binding decisions, runbook, edge cases — treat as historical reference).

## Key Constraints
1. **Self-containment is the defining property** (§5.1): every excerpt must be independently understandable. An excerpt that requires another excerpt to make sense is defective.
2. **Taxonomy-independent creation** (§5.2): excerpts are created without reference to any taxonomy tree. Placement happens later.
3. **Content integrity over taxonomic precision** (§5.3 Rule 3): never break an excerpt's self-containment to achieve cleaner taxonomy placement.
