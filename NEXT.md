# NEXT — Write Session 4 handoff (Architect session)

## Current position: Session 3 COMPLETE and ACCEPTED (commit 1452e3e). Structure discovery implemented: 1,212 lines, 19 tests, all 13 fixtures produce valid division trees, L-003 documented. Cumulative: 3,266 impl lines, 125 tests, 13/51 ADV.
## What to do: Write Build Session 4 NEXT.md for Claude Code — Layer Detection (§4.A.5).
## Context: Session 4 implements Pass 5 of the Shamela normalizer. It consumes `CleanedPage` fields from Session 2 (bold_spans, font_size_spans, primary_text) and source metadata (is_multi_layer, genre) to identify which portions of each page belong to which text layer (matn, sharh, hashiyah). Output: `text_layers` array per content unit.
## Owner action needed: YES after — to give the Session 4 handoff to CC.

---

## Session 3 Deliverables (what's already built)

Session 3 produced the complete structure discovery pipeline:

| Module | Lines | What it does |
|--------|-------|-------------|
| `src/structure_discovery.py` | 1,212 | 4-tier heading detection, hierarchy inference, division tree construction |
| `tests/test_structure_discovery.py` | 638 | 19 mandatory tests: ADV-016/017/018, 3 real fixtures, keyword/TOC/edge cases |

Key contract changes: `HeadingConfidence.MINIMAL` added, `heading_level` widened to ge=0 (volumes at level 0), passaging `DivisionPathEntry.heading_level` aligned to ge=0.

Known limitations: L-001 (bare-number footnotes), L-002 (ضياء السالك collision — Session 4 fixes this), L-003 (same-page heading chaining, 214 instances).

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` — Session 4 row: "Layer detection (typographic signals for Shamela) | §4.A.5".
2. `engines/normalization/SPEC.md` — §4.A.5 (layer detection) and §4.A.2 Pass 5 overview (lines 209-217).
3. `engines/normalization/contracts.py` — `TextLayers`, `LayerType`, `LayerMapEntry`, `text_layers` on ContentUnit.
4. `engines/normalization/src/normalizers/shamela.py` — `CleanedPage.bold_spans`, `font_size_spans`. These are the typographic signals Session 4 consumes.
5. `engines/normalization/KNOWN_LIMITATIONS.md` — L-002 (ضياء السالك) is fixed by layer detection.
6. `engines/normalization/reference/structural_patterns.yaml` — supplementary section has حاشية/شرح patterns (excluded from Tier 2 heading detection, relevant for layer markers).
7. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — ADV cases for §4.A.5.

## After Writing

Follow `reference/protocols/PRE_HANDOFF_VERIFICATION.md` — verify every file ref, trace data flows, test regexes empirically. Commit only after verification.

When CC finishes Session 4: follow `reference/protocols/REVIEW_PROTOCOL.md` and fill `reference/protocols/REVIEW_CHECKLIST_TEMPLATE.md` (copy to `reference/archive/sessions/reviews/session_4_review.md`). ALL boxes checked, ALL fixes committed BEFORE verdict.
