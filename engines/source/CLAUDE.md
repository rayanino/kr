# Source Engine — محرك المصادر

**Responsibility:** Discovering, identifying, acquiring, freezing, and documenting raw knowledge sources (§2.2).
**Phase:** 1 (source-format-specific, above the normalization boundary).

## Required Reading
1. This engine's SPEC.md
2. VISION.md §7 (source pipeline architecture)
3. VISION.md §2.2 (engine definition), §2.5 (source vocabulary)
4. Output boundary: Phase 1 internal (frozen source + source metadata → normalization engine)

## SPEC Summary (see SPEC.md for full detail)

**Three-tier identity model:**
- `source_id` (`src_{8_char_hash}`): per acquired file/set, derived from frozen SHA-256
- `work_id` (`wrk_{author_slug}_{title_slug}`): groups all editions of same abstract work
- `canonical_id` (`sch_{5_digit_sequence}`): scholar authority, centralized registry

**Primary outputs:** Frozen source files + source metadata record (JSON) + updates to three registries (sources, works, scholars).

**Key architectural decisions (SPEC §4):**
- Multi-model consensus for author identification and work matching (highest cascade risk)
- Trust evaluation: 5-factor weighted scoring → verified/flagged tiers
- Text fidelity tracked separately from scholarly trustworthiness
- Work relationship graph (sharh_of, hashiyah_on, mukhtasar_of, etc.)
- OpenITI corpus enrichment for scholar authority bootstrapping (§4.B.1)
- Bibliographic intelligence from minimal input (§4.B.2)
- Citation network discovery [NOT YET IMPLEMENTED] (§4.B.3)
- Acquisition gap analysis [NOT YET IMPLEMENTED] (§4.B.4)

## Current State
Legacy code migrated from ABD (Arabic Book Digester). ABD was a narrow Shamela-only tool — its design decisions have zero authority in KR (D-019). The code works for Shamela intake but the SPEC defines what this engine SHOULD be, which is much broader. 12 known gaps between current code and SPEC — see SPEC §9.

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
10. **Source authority level.** Classify each source as primary (مصدر أصلي — original scholarly content), reference (مرجع — compiles/organizes), or modern compilation (معاصر). The synthesizer uses this to weight sources differently. See DOMAIN.md "Primary vs. Secondary Source Distinction."
11. **Multi-layer composition detection.** Identify whether a source is a multi-layer work (matn+sharh, sharh+hashiyah, etc.) and record which layers are present and who authored each. This is critical for downstream layer attribution. See DOMAIN.md "The Multi-Layer Text Problem."
12. **Book structural format classification.** Classify each source's format: prose treatise, versified text (نظم), Q&A/fatwa format (مسائل), tabular disagreement catalog, dictionary format, or commentary. Downstream engines use this to apply format-appropriate processing. See DOMAIN.md "Book Structures Beyond Prose."
13. **Quran and hadith collections are special.** Quran text should use a canonical digital source (no OCR needed). Hadith collections have standard numbering (e.g., "Bukhari #6018") that must be captured. See DOMAIN.md "Special Source Types."
