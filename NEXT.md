# NEXT SESSION

**Written by:** Session 2026-03-05 (synthesizing engine SPEC)
**Date:** 2026-03-05

## Immediate Task

Cross-SPEC consistency verification + VISION.md corrections. This is the final SPEC-phase session before moving to implementation.

**Definition of done — this session is complete when ALL of these are true:**
1. Every engine's output contract matches the next engine's input contract (verified across all 7 engines)
2. Shared component integration is consistent across all consumers (scholar authority model, user model)
3. VISION.md cross-cutting sections corrected: §8 (Quality Architecture), §10 (Implementation Strategy), §11 (Design Principles), §12 (Codebase Relationship)
4. VISION.md §6.4 OPEN QUESTION resolved with D-040 decision text
5. VISION.md §0-§4, §13 re-verified with engine-deep-dive knowledge
6. All concepts (source, excerpt, entry, atom, passage) mean the same thing across all documents
7. STATUS.md updated to reflect all SPECs complete
8. All changes committed and pushed

## Context

All 7 engine SPECs are now complete:
- Source engine: 582L (D-024 through D-027)
- Normalization engine: 664L (D-028 through D-031)
- Passaging engine: 502L
- Atomization engine: 580L (D-034, D-035)
- Excerpting engine: 559L (D-036, D-037)
- Taxonomy engine: 562L (D-038, D-039)
- Synthesizing engine: 582L (D-040)

The synthesizing engine SPEC resolves the VISION.md §6.4 OPEN QUESTION about analytical layer boundary via D-040 (structured traceability with grounding_type field). This decision needs to be integrated into VISION.md.

This session should verify the entire documentation stack for internal consistency before Claude Code implementation begins.

## Files to Read — IN THIS ORDER

**Step 1 — All SPECs (focused read: §2 Input Contract and §3 Output Contract of each):**
1. `engines/source/SPEC.md` §2-§3
2. `engines/normalization/SPEC.md` §2-§3
3. `engines/passaging/SPEC.md` §2-§3
4. `engines/atomization/SPEC.md` §2-§3
5. `engines/excerpting/SPEC.md` §2-§3
6. `engines/taxonomy/SPEC.md` §2-§3
7. `engines/synthesis/SPEC.md` §2-§3

**Step 2 — Cross-cutting VISION sections:**
8. `python3 scripts/extract_vision_sections.py 8` (Quality Architecture)
9. `python3 scripts/extract_vision_sections.py 10` (Implementation Strategy)
10. `python3 scripts/extract_vision_sections.py 11` (Design Principles)
11. `python3 scripts/extract_vision_sections.py 12` (Codebase Relationship)
12. `python3 scripts/extract_vision_sections.py 13` (Documentation Hierarchy)

**Step 3 — Verify core vocabulary consistency:**
13. `python3 scripts/extract_vision_sections.py 2` (Glossary — focused check on terms used across SPECs)

**Step 4 — Schemas:**
14. `schemas/SCHEMA_ANALYSIS.md` — verify all schema notes are current

## Key Verification Checks

- **Source → Normalization boundary:** Does the normalization engine's input contract match what the source engine produces?
- **Normalization → Passaging (THE normalization boundary):** Does the normalized package schema match both sides?
- **Passaging → Atomization → Excerpting chain:** Do passage and atom schemas flow correctly?
- **Excerpting → Taxonomy:** Does the draft excerpt format match the taxonomy engine's input contract?
- **Taxonomy → Synthesizing:** Does the placed excerpt format match what the synthesizing engine reads? (This was the focus of the synthesizing SPEC §2.1.)
- **Scholar authority model:** Is the shared model consistently referenced across source, excerpting, taxonomy, and synthesizing engines?
- **User model:** Is it consistently referenced by the synthesizing engine and scholar interface?
- **Metadata pass-through (D-023):** Does metadata accumulate correctly from source to synthesis without loss at any boundary?

## Pending Owner Questions

None currently pending.

## What This Session Did

Completed the synthesizing engine SPEC (582 lines, all 10 sections). Key design: five-phase generation pipeline (collection → scholarly analysis → narrative construction → integrity verification → finalization). Resolves §6.4 OPEN QUESTION via D-040 (grounding_type traceability boundary). Eight integrity checks in Phase 4. Per-science customization via 6 SCIENCE.md hooks. Prioritized regeneration with batch mode for large source processing. Diagnostic entries for failed generation. Four transformative capabilities: scholarly consensus mapping, intellectual genealogy reconstruction, predictive gap synthesis, entry quality self-assessment. Updated RESOURCES.md with synthesis-relevant tools (Attr-First, FRONT, ContraDoc, multi-LLM summarization research). Updated CLAUDE.md.

## New Decisions

D-040 (Analytical layer boundary — structured traceability via grounding_type).
