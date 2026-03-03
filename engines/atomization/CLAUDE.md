# Atomization Engine — محرك التذرير

**Responsibility:** Breaking each passage into its constituent atoms — the smallest indivisible units of text, each typed and located by character offsets (§2.2).
**Phase:** 2 (source-agnostic, below the normalization boundary). No source-format-specific logic permitted.

## Required Reading
1. This engine's SPEC.md
2. VISION.md §2.2 (engine definition), §2.4 (atom definition, content type)
3. Input schema: `schemas/passage`
4. Output schema: `schemas/atoms`

## Current State
Status: Not started. ABD codebase has atomization logic embedded in `engines/excerpting/src/extract_passages.py` (~2100 lines spanning both atomization and excerpting); to be separated and restructured per §12.2.
Tests: 0 passing, 0 failing (ABD has tests covering the combined extraction logic in `engines/excerpting/tests/`).
Known issues: Separation of atomization from excerpting logic is the primary restructuring task.
**Note:** Atomization logic currently lives in `engines/excerpting/src/extract_passages.py` (placed there during migration per §12.2: "separation into distinct engine directories occurs during restructuring").

## Commands
```
cd engines/atomization && python -m pytest tests/
```

## Key Constraints
1. **Science-agnostic** (§2.2): core algorithm does not vary by science. Content type taxonomy is defined in this engine's SPEC.md.
2. **LLM-driven** (§2.2): atom boundary identification requires content understanding, not pattern matching.
3. **Character offsets are precise** (§2.4): every atom must be locatable within its passage by exact character offsets. Offset errors corrupt downstream excerpt construction.
