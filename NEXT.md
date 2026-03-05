# NEXT SESSION

**Written by:** Session 2026-03-05 (normalization engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Write the passaging engine SPEC (Phase 2, Round 3).

**Output file:** `engines/passaging/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/passaging/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/passaging/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey (text chunking, Arabic sentence boundary detection, semantic passage segmentation)
5. VISION.md §7.5–§7.6 defect ledger from normalization SPEC writing is produced (alongside the §7.1–7.4 ledger from source SPEC)
6. `NEXT.md` is overwritten with handoff for the next session (atomization engine SPEC)
7. Self-review checklist passed — defects fixed before commit
8. All changes committed and pushed

## Context

The normalization engine SPEC is complete (664 lines). It defines:
- Dispatcher-normalizer architecture with 7 normalizer types (§4.A.1)
- Shamela normalizer with 6-pass pipeline including multi-layer detection and structure discovery (§4.A.2)
- PDF normalizer using Docling for text extraction and layout analysis (§4.A.3)
- Scanned PDF/image normalizer with tiered OCR: Mistral OCR 3 + Qari-OCR + dual-OCR comparison (§4.A.4, D-028)
- Multi-layer text detection with explicit transition markers, typographic signals, and content-based inference (§4.A.5)
- Structure discovery with 4-tier confidence architecture (§4.A.6)
- Normalized package schema: manifest + content JSONL with source_id reference model (D-029)
- Universal footnote reference markers ⌜N⌝ (D-031)
- Four transformative capabilities: layer intelligence, format auto-detection, fine-grained fidelity mapping, footnote apparatus classification (§4.B)

The passaging engine is the FIRST Phase 2 engine — it sits immediately below the normalization boundary. It consumes normalized packages and produces passages (processing units for atomization and excerpting). This is the critical engine that determines how text is divided for downstream processing.

**Why this engine matters:** The passaging engine's output determines what the excerpting engine works with. A passage that splits a definition in half produces broken excerpts. A passage that's too large (contains 5 unrelated topics) produces excerpts with poor self-containment. A passage that crosses a verse boundary destroys verse structure. Getting passage boundaries right is essential for excerpt quality.

## Files to Read — IN THIS ORDER

**Step 1 — Vision and user (refresh only what's needed):**
1. `reference/DOMAIN.md` — "Book Structures Beyond Prose", "Versified Texts", "Passage containment rule"
2. `reference/USER_SCENARIOS.md` — how passages serve the overall pipeline
3. `reference/PIPELINE_TRACE.md` — trace Stage 3 (passaging) inputs and outputs

**Step 2 — Architecture:**
4. `VISION.md` §2.2 (passaging engine definition), §2.5 (passage definition) → `python3 scripts/extract_vision_sections.py 2`
5. `engines/normalization/SPEC.md` — the COMPLETE normalization engine SPEC. §3 (output contract) defines exactly what the passaging engine receives. Read §3 carefully — it's your input contract.
6. `schemas/passage.json` — current ABD-era passage schema
7. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code:**
8. `engines/passaging/CLAUDE.md` — current state overview
9. Any existing passaging code (check `engines/passaging/src/`)
10. The structure discovery pass in `engines/normalization/src/discover_structure.py` already creates passage-like units — understand what exists

**Step 4 — Research:**
11. `reference/RESOURCES.md` — text chunking tools already cataloged
12. Web searches: semantic text chunking for Arabic, passage boundary detection in scholarly texts, LangChain/LlamaIndex text splitting strategies

**Note:** The passaging engine has LESS existing code than normalization. Design from first principles: what makes a good passage boundary for Islamic scholarly texts?

## Key Design Questions

- **Passage size calibration:** Arabic text is morphologically denser than English. A 200-word Arabic passage ≈ 500-word English passage in information content. What's the right size for downstream processing?
- **Structure-guided boundaries:** The normalization engine provides a division tree. How does the passaging engine use it? Divisions are heading-based (author's intended structure); passages are processing-based (right-sized for excerpting). They're related but not identical.
- **Verse-aware passaging:** For versified texts (منظومات), each بيت is a self-contained unit. Passage boundaries must respect verse structure. A بيت must never be split across passages.
- **Cross-page text continuity:** The normalization engine outputs per-page content units. The passaging engine must join text that flows across page boundaries. How are cross-page sentences handled?
- **Format-aware strategies:** Q&A format → passage at Q&A pair boundaries. Dictionary → passage at entry boundaries. Tabular khilaf → passage at مسألة boundaries. The normalization engine provides `structural_format` metadata.
- **Commentary passage alignment:** In multi-layer sources, should a passage contain only one layer's text, or both the matn snippet and its commentary? The passage containment rule (D-011: excerpts cannot span passage boundaries) makes this critical.

## New Decisions from This Session

D-028 (OCR strategy), D-029 (normalized package schema), D-030 (conservative layer default), D-031 (universal footnote markers). Read full entries in kr_decisions.md.

## Pending Owner Questions

- **Entry language:** Resolved (D-032). Entries must be in Arabic. Interface/guidance may use any of the owner's languages.

## What This Session Did

Completed the normalization engine SPEC (664 lines, all 10 sections). Updated CLAUDE.md, kr_decisions.md (D-028–D-031), RESOURCES.md (Mistral OCR 3, Qari-OCR). Wrote 4 transformative capabilities: layer intelligence, format auto-detection, fine-grained fidelity mapping, footnote apparatus classification. Did not produce VISION §7.5–§7.6 defect ledger (deferred to passaging session alongside accumulated ledger from source+normalization SPECs).
