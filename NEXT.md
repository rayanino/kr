# NEXT SESSION

**Written by:** Session 2026-03-04 (source engine SPEC)
**Date:** 2026-03-04

## Immediate Task

Write the normalization engine SPEC (Phase 2, Round 2).

**Output file:** `engines/normalization/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/normalization/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/normalization/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey (Arabic OCR tools, HTML/PDF/image parsers, structure discovery approaches)
5. VISION.md §7.5–§7.6 defect ledger produced (corrections queued alongside the §7.1–7.4 ledger from source SPEC)
6. `NEXT.md` is overwritten with handoff for the next session (passaging engine SPEC)
7. Self-review checklist passed — defects fixed before commit
8. All changes committed and pushed

## Context

The source engine SPEC is complete (582 lines). It defines:
- Three-tier identity model (source_id, work_id, canonical_id) — D-024
- Source metadata record at `library/sources/{source_id}/metadata.json`
- Frozen files at `library/sources/{source_id}/frozen/`
- Scholar authority registry at `library/registries/scholars.json` — D-025
- Work relationship graph — D-027
- Text fidelity separate from trust tier — D-026

The normalization engine is the second pipeline stage — still Phase 1 (above normalization boundary). Its output crosses the normalization boundary: everything downstream is source-format-agnostic. This makes the normalization engine the CRITICAL translation layer between diverse source formats and the universal pipeline.

**Why this engine matters:** The normalization engine determines what information survives from format-specific sources into the universal pipeline. If it fails to detect multi-layer text composition, the excerpting engine will misattribute text. If it fails to preserve page boundaries, citations become unverifiable. If it loses diacritics, downstream Arabic processing degrades. Quality here cascades everywhere.

**Pipeline priority (D-020) still applies:** Get the normalized package schema RIGHT — it's the input for all Phase 2 engines. But also invest heavily in multi-layer text detection and structure discovery, because these are where scholarly integrity is at stake.

## Files to Read — IN THIS ORDER

**Step 1 — Vision and user (refresh):**
1. `reference/DOMAIN.md` — pay special attention to: "The Multi-Layer Text Problem", "Arabic as a Processing Language", "Versified Texts", "Book Structures Beyond Prose", "Physical Reference Preservation", "Design Implications → Normalization Engine"
2. `reference/USER_SCENARIOS.md` — Scenario 6 (book briefing uses normalized content), Scenario 2 (new source processing)
3. `reference/ENTRY_EXAMPLE.md` — notice how the entry distinguishes matn text from sharh commentary — this separation is the normalization engine's job
4. `reference/PIPELINE_TRACE.md` — trace what the normalization engine receives and produces

**Step 2 — Architecture:**
5. `VISION.md` §7.5–§7.6 and §2 → run `python3 scripts/extract_vision_sections.py 7 2`
6. `engines/source/SPEC.md` — the COMPLETE source engine SPEC. §3 (output contract) defines exactly what the normalization engine receives. Read this carefully — it's your input contract.
7. `schemas/normalized_content.json` — current ABD-era normalized output schema
8. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code and reference:**
9. `engines/normalization/reference/ABD_NORMALIZATION_SPEC.md` — ABD-era normalization spec (Shamela only, D-019 applies)
10. `engines/normalization/reference/ABD_STRUCTURE_SPEC.md` — ABD structure discovery spec
11. `engines/normalization/reference/SHAMELA_HTML_REFERENCE.md` — Shamela HTML format documentation (critical for the Shamela normalizer)
12. `engines/normalization/reference/structural_patterns.yaml` — known structural patterns
13. `engines/normalization/reference/structure_edge_cases.md` — edge cases
14. `engines/normalization/src/normalizers/` — existing Shamela normalizer code
15. `engines/normalization/src/discover_structure.py` (2896L) — structure discovery code (the largest single file — skim for concepts, don't memorize)
16. `engines/normalization/src/validate_structure.py` (333L) — validation

**Step 4 — Research:**
17. `reference/RESOURCES.md` — Docling, CAMeL Tools, OCR tools already cataloged
18. Web searches: Arabic multi-layer text detection approaches, text structure discovery for scholarly Arabic, diacritics-aware text processing, PDF structure extraction for Arabic books

**CRITICAL: The normalization engine has the MOST existing code (4352 lines across 3 files, 292 tests, 15 reference docs). Do NOT let the volume of existing code constrain your design. Read it to understand what exists, but design from first principles. The existing code handles only Shamela HTML; the SPEC must define normalization for ALL source types.**

## Key Design Questions

These are starting points, not exhaustive:

- **Normalized package schema:** What exactly does the normalized package contain? The current schema is ABD-era. Design the universal schema that carries everything downstream engines need: text content, structural annotations, layer identification, page boundaries, text fidelity signals, diacritics, and ALL source metadata (D-023).
- **Multi-layer text detection:** How does each normalizer identify matn vs. sharh vs. hashiyah vs. tahqiq notes? Shamela uses typography (bold, brackets, font size). PDFs use layout cues. This is the highest-integrity-risk processing step.
- **Structure discovery:** How are chapters, sections, subsections identified from format-specific markup? This is a MASSIVE topic — discover_structure.py is 2896 lines for Shamela alone.
- **Page boundary preservation:** How are physical page numbers mapped to the normalized text? Different formats represent pages differently.
- **One normalizer per source type:** The architecture mandates modular normalizers. What interface must they conform to? What does each one produce?
- **Text fidelity output:** The source engine records text fidelity at the source level. The normalization engine needs to produce text fidelity at a finer grain — per-page or per-passage confidence based on actual processing quality (OCR confidence scores, structural detection confidence).
- **What crosses the boundary:** Everything in the normalized package must be source-format-agnostic. What format-specific information is useful to encode in a universal way? (e.g., "this text was bold in the original" → "this text is layer 1 (matn)")

## VISION §7.5–§7.6 Known Issues

(From earlier review — verify and expand during SPEC writing)
- §7.5 describes structure discovery at a high level but doesn't specify what "structural signals" means for non-Shamela formats
- §7.6 (normalization boundary) is one of the best-defined sections but may need updates based on multi-layer composition handling
- The normalized package schema in VISION may not account for all the metadata fields the source SPEC now produces

## New Decisions from This Session

D-024 (three-tier identity model), D-025 (source engine as primary scholar authority creator), D-026 (text fidelity separate from trust), D-027 (work relationship graph with placeholders). Read full entries in kr_decisions.md.

## Pending Owner Questions

- **Entry language:** Should entries be in Arabic, English, or bilingual? (Carried forward — still unanswered. Does not block normalization SPEC.)

## What This Session Did

Completed the source engine SPEC (582 lines, all 10 sections). Updated CLAUDE.md, kr_decisions.md (D-024–D-027), RESOURCES.md (OpenITI, KITAB, sunnah.com API, hadith-json), SCHEMA_ANALYSIS.md. Produced VISION §7.1–§7.4 defect ledger (reference/vision_defects_s7.md, queued for application). Self-review passed.

## Quality Calibration

The source engine SPEC sets the quality bar. Read it before writing the normalization SPEC. Key quality indicators: every processing step has explicit edge case handling, every metadata field has a defined consumer downstream, every [NOT YET IMPLEMENTED] capability is fully specified, confidence thresholds are concrete numbers not vague qualifiers.
