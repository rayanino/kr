# NEXT SESSION

**Written by:** Session 2026-03-05 (passaging engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Write the atomization engine SPEC (Phase 2, Round 4).

**Output file:** `engines/atomization/SPEC.md` (overwrite the existing stub)

**Definition of done — this session is complete when ALL of these are true:**
1. `engines/atomization/SPEC.md` follows the full SPEC template (all 10 sections, non-stub)
2. `engines/atomization/CLAUDE.md` is consistent with the SPEC (update if needed — SPEC is source of truth)
3. `reference/kr_decisions.md` has entries for any architectural decisions made during SPEC writing
4. `reference/RESOURCES.md` is updated with findings from the mandatory resource survey (Arabic text segmentation, scholarly pattern detection, atom type classification)
5. VISION.md defect ledger for §7.5–§7.8 produced (accumulated from source, normalization, passaging SPEC work)
6. `NEXT.md` is overwritten with handoff for the next session (excerpting engine SPEC)
7. Self-review checklist passed — defects fixed before commit
8. All changes committed and pushed

## Context

The passaging engine SPEC is complete (502 lines). It defines:
- Five-phase processing pipeline: load→assemble→strategy-select→create→emit (§4.A.1)
- Cross-page text assembly with 4-rule joining logic and footnote renumbering (§4.A.2)
- Six format-specific strategies: prose, verse, Q&A, tabular_khilaf, dictionary, commentary (§4.A.3–§4.A.9)
- Prose strategy with division-guided boundaries + semantic splitting for oversized divisions (§4.A.4)
- Verse strategy with absolute بيت integrity rule and commentary-on-verse handling (§4.A.5)
- Commentary-unit strategy keeping matn+sharh together in one passage (§4.A.9)
- Size targets: 200–800 Arabic words target, 50 min, 2000 hard max
- Self-validation with 7 automated checks (§4.A.10)
- Four transformative capabilities: quality prediction, implicit structure discovery, commentary-matn alignment, cross-edition correspondence (§4.B)

The atomization engine is the SECOND Phase 2 engine — it receives passages and breaks them into atoms (smallest indivisible text units). This is where scholarly text patterns are first detected: definitions, evidence markers, isnad chains, opinion markers, examples. Atom types are critical metadata that flows to the excerpting engine.

**Why this engine matters:** The atomization engine's type classifications determine how the excerpting engine groups content and what metadata excerpts carry. If a definition atom is misclassified as an example, the excerpt may be incomplete. If an isnad chain isn't detected as such, the excerpting engine treats evidence transmission metadata as regular text. Atom type IS downstream metadata (D-023).

## Files to Read — IN THIS ORDER

**Step 1 — Domain and user context (refresh only what's needed):**
1. `reference/DOMAIN.md` — "Atomization engine must:" section in Design Implications
2. `reference/PIPELINE_TRACE.md` — Stage 4 (atomization) inputs and outputs

**Step 2 — Architecture:**
3. `VISION.md` §2.4 (atom definition) → `python3 scripts/extract_vision_sections.py 2`
4. `engines/passaging/SPEC.md` — the COMPLETE passaging SPEC. §3 (output contract) defines exactly what the atomization engine receives. Read §3 carefully — it's your input contract.
5. `schemas/atoms.json` — current ABD-era atom schema
6. `schemas/SCHEMA_ANALYSIS.md` — pipeline schema overview

**Step 3 — Existing code:**
7. `engines/atomization/CLAUDE.md` — current state overview
8. Any existing atomization code (check `engines/atomization/src/`)

**Step 4 — Research:**
9. `reference/RESOURCES.md` — tools already cataloged
10. Web searches: Arabic scholarly text pattern detection, isnad chain recognition, Arabic NLP for evidence detection, LLM-based text segmentation

**Note:** The atomization engine is heavily LLM-driven — identifying atom types requires understanding Arabic scholarly conventions. The resource survey should focus on: (1) existing Arabic NER/pattern detection for scholarly text, (2) LLM prompting strategies for fine-grained text classification, (3) isnad chain detection algorithms.

## Key Design Questions

- **Atom type taxonomy:** What types exist? Definition, rule, example, evidence (Quran, hadith, logical), opinion marker, isnad chain, scholarly reference, refutation, condition/exception, cross-reference. How many types? Too few → excerpting engine loses signal. Too many → classification accuracy drops.
- **Atom granularity:** How small is the smallest atom? A single Arabic word (e.g., "نحو" introducing an example)? A full sentence? A paragraph? Atoms are the SMALLEST indivisible units — but "indivisible" needs precise definition for Arabic scholarly text.
- **Multi-layer atoms:** In a commentary passage with text_layers, atoms should carry layer attribution. A matn quotation atom belongs to the matn author; the surrounding commentary atoms belong to the sharh author.
- **Character offsets vs. text extraction:** Atoms are defined by character offsets within passage_text. Should atoms also carry their own extracted text, or should downstream engines slice from passage_text using offsets?
- **LLM vs. rule-based detection:** Some atom types are detectable by patterns (isnad chains, "لقوله تعالى" evidence markers). Others require understanding (distinguishing a definition from an example). What's the right mix?

## Pending Owner Questions

None currently pending.

## What This Session Did

Completed the passaging engine SPEC (502 lines, all 10 sections). Updated CLAUDE.md to match SPEC. Updated RESOURCES.md with semantic text chunking research, Arabic segmentation findings, and multilingual embedding models. Recorded D-033 (secure by design) from owner input — propagated to DOMAIN.md Core Identity. VISION defect ledger deferred to atomization session (accumulating from source+normalization+passaging).

## New Decisions

D-033 (Secure by design — error prevention over error correction). Owner-initiated foundational principle: every engine must be designed so errors are structurally prevented, not just detected. Immutable artifacts, explicit decisions, fail-loud behavior, verification at every boundary, mandatory provenance, continuous corruption detection, bounded blast radius. Read full entry in kr_decisions.md.
