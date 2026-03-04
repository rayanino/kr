# Source Engine — محرك المصادر

**Responsibility:** Discovering, identifying, acquiring, freezing, and documenting raw knowledge sources (§2.2).
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §7 (source pipeline architecture)
3. VISION.md §2.2 (engine definition), §2.5 (source vocabulary)
4. Output boundary: Phase 1 internal (frozen source + source metadata → normalization engine)

## Current State
Legacy code migrated from ABD (Arabic Book Digester). ABD was a narrow Shamela-only tool — its design decisions have zero authority in KR (D-019). The code works for Shamela intake but the SPEC defines what this engine SHOULD be, which is much broader.

Code: `engines/source/src/` (intake.py 1476L, enrich.py 580L, corpus_audit.py 228L).
Tests: 112 tests in `engines/source/tests/` (test_intake.py, test_enrich.py).
Reference: 2 ABD-era docs in `engines/source/reference/` — describe what WAS built, not what to build.

## Commands
```
cd engines/source && python -m pytest tests/
```

## Key Constraints
1. **Freezing is immediate and absolute** (§2.5, §7.2): source frozen upon acquisition, before any processing. No component may modify the frozen copy.
2. **Trustworthiness defaults to flagging** (§7.4): when uncertain, classify as flagged. False verification contaminates; false flagging is correctable.
3. **Science scope required** (§7.3): source metadata must record which science(s) the source covers. This data flows downstream through the normalized package.
4. **Not Shamela-only** (D-019): KR acquires sources from any scholarly repository in any format. Shamela is ONE source type among many.
