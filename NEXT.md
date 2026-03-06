# NEXT SESSION

**Written by:** Session 2026-03-06 (Scholar Interface SPEC completion)
**Date:** 2026-03-06

## Immediate Task

Cross-SPEC consistency verification and cross-cutting VISION.md corrections. This is the final preparatory phase work before implementation.

**Definition of done — this session is complete when:**
1. Cross-SPEC consistency verified: every engine's output contract matches the next engine's input contract, especially the scholar interface's reads from all upstream components
2. Full coherence review: concepts ("source," "excerpt," "entry," "leaf") verified to mean the same thing across all 14 SPECs + VISION.md
3. Cross-cutting VISION.md sections corrected: §8 (Quality Architecture), §10 (Implementation Strategy), §11 (Design Principles), §12 (Codebase Relationship)
4. Re-verify VISION.md §0–§4, §13 with engine-deep-dive knowledge
5. Claude Code environment (.claude/ directory) populated or task scoped for next session
6. Changes committed and pushed

## Context

ALL 14 SPECs are now complete:
- 7 engines: source (582L), normalization (664L), passaging (502L), atomization (580L), excerpting (559L), taxonomy (562L), synthesizing (582L)
- 6 shared components: consensus (405L), validation (406L), human_gate (413L), feedback (461L), user_model (368L), scholar_authority (462L)
- 1 interface: scholar (872L)

Total: ~7,416 lines of specification.

The preparatory phase was described in the archived roadmap (reference/archive/kr_definitive_roadmap_v2.md) Phase 3 / Round 9. The current state matches the "all SPECs complete" checkpoint described there. The next step is the verification and correction pass.

## Files to Read — IN THIS ORDER

1. Read ALL 14 SPECs — but ONLY §2 (Input Contract) and §3 (Output Contract) of each. This is the boundary verification pass. Read them in pipeline order:
   - `engines/source/SPEC.md` §2-§3
   - `engines/normalization/SPEC.md` §2-§3
   - `engines/passaging/SPEC.md` §2-§3
   - `engines/atomization/SPEC.md` §2-§3
   - `engines/excerpting/SPEC.md` §2-§3
   - `engines/taxonomy/SPEC.md` §2-§3
   - `engines/synthesis/SPEC.md` §2-§3
   - `shared/consensus/SPEC.md` §2-§3
   - `shared/validation/SPEC.md` §2-§3
   - `shared/human_gate/SPEC.md` §2-§3
   - `shared/feedback/SPEC.md` §2-§3
   - `shared/user_model/SPEC.md` §2-§3
   - `shared/scholar_authority/SPEC.md` §2-§3
   - `interface/scholar/SPEC.md` §2-§3

2. After boundary verification, read VISION.md §8, §10, §11, §12, §13 for correction pass. Use `python3 scripts/extract_vision_sections.py 8 10 11 12 13`.

3. `reference/kr_decisions.md` — verify no decisions are contradicted by the final SPEC set.

**Context budget note:** Reading 14 × ~30L of §2-§3 = ~420 lines. VISION sections = ~5K-10K tokens. This should fit within budget with room for corrections. If context runs low, prioritize: (1) boundary verification, (2) VISION §8 and §11 corrections (most likely to need updating), (3) defer §10/§12/§13 and .claude/ to another session.

## Decisions Needed

- **Cross-SPEC inconsistencies.** The boundary verification in the 2026-03-05 session (STATUS.md) predates the shared component SPECs and the scholar interface. Re-verify all boundaries.
- **VISION §8 (Quality Architecture).** This section was written before the validation, consensus, and human_gate SPECs existed. It likely needs significant correction to match the actual quality architecture as specified.
- **Claude Code environment.** The `.claude/` directory needs to be populated for implementation. This may be a separate session if context is limited.

## Pending Owner Questions

None.

## What This Session Did

Completed the scholar interface SPEC: wrote §4.B (5 transformative capabilities: debate simulation, scholarly fingerprinting, unanswered question discovery, optimal source prediction, knowledge decay prediction), §5-§10. Upgraded §4.A.2.2 with full hybrid retrieval pipeline (Qdrant vector store, Arabic embeddings, cross-encoder re-ranking, four retrieval strategies, grounding enforcement thresholds). Updated CLAUDE.md and STATUS.md. Total SPEC: 872 lines.

## New Decisions

None this session. (The retrieval architecture and grounding thresholds are interface-internal design choices, not project-level decisions requiring kr_decisions.md entries.)
