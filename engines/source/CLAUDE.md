# Source Engine — محرك المصادر

**Responsibility:** Discovering, identifying, acquiring, freezing, and documenting raw knowledge sources (§2.2).
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §7 (source pipeline architecture)
3. VISION.md §2.2 (engine definition), §2.5 (source vocabulary)
4. Output boundary: Phase 1 internal (frozen source + source metadata → normalization engine)

## Current State
Status: Not started. ABD codebase has partial implementation (`tools/intake.py`, `tools/enrich.py`) to be restructured into `engines/source/src/` per §12.2.
Tests: 0 passing, 0 failing.
Known issues: Only manual/single-source intake exists in ABD. Autonomous discovery (§7.2) not yet built. Science scope metadata field (§7.3) not yet implemented.

## Commands
```
cd engines/source && python -m pytest tests/
```

## Key Constraints
1. **Freezing is immediate and absolute** (§2.5, §7.2): source frozen upon acquisition, before any processing. No component may modify the frozen copy.
2. **Trustworthiness defaults to flagging** (§7.4): when uncertain, classify as flagged. False verification contaminates; false flagging is correctable.
3. **Science scope required** (§7.3): source metadata must record which science(s) the source covers. This data flows downstream through the normalized package.
