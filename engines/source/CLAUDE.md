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
5. **Work vs. source distinction** (DOMAIN.md): a work (مؤلَّف) is the abstract intellectual creation (e.g., al-Mughni by Ibn Qudamah). A source (مصدر) is a specific manifestation (e.g., al-Turki's tahqiq of al-Mughni published by Dar Alam al-Kutub). Same work, different tahqiq = different sources. The source identity model must handle this cleanly.
6. **Manual acquisition is first-class** (D-020): owner provides iPhone photos of physical books and manually downloaded files from login-gated repositories. These are not edge cases.
7. **Metadata is synthesis fuel** (D-023): source metadata isn't just documentation — it's a primary input to the synthesizing engine. Author biography, dates, school affiliations, teacher-student relationships, work genre, tahqiq quality — all of this enables the synthesizer to produce scholarly narratives with temporal depth and intellectual genealogy. See `reference/ENTRY_EXAMPLE.md`.
8. **Pipeline priority** (D-020): Get the identity model and metadata architecture right — these cascade to every downstream engine. Keep acquisition workflows minimal for v1. Don't over-engineer sourcing.
9. **Book briefing metadata** (D-022): The source engine captures the foundation for the scholar interface's "book briefing" product: author profile, work classification, scope, reputation, edition quality, comparative edition data.
