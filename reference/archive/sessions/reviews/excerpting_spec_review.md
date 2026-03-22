# Excerpting Engine SPEC Review — BLOCKED

**Date:** 2026-03-22
**Reviewer:** Claude Chat (Architect)
**Files reviewed:** engines/excerpting/SPEC.md (98KB), engines/excerpting/contracts.py (22KB)
**Verdict:** BLOCKED (16 findings: 3 CRITICAL, 6 HIGH, 5 MEDIUM, 2 LOW)

---

## Executive Summary

The excerpting engine SPEC was written for a 7-engine architecture where passaging and atomization were separate upstream engines. The committed architecture (ARCHITECTURE_DECISION.md, commit 5636ceb) absorbed both into excerpting as internal phases. The SPEC was never restructured to reflect this change.

The domain knowledge in the SPEC (decontextualization prevention, multi-layer handling, evidence/hadith handling, implicit reference resolution, verse-format handling, adversarial test cases) is excellent and must be preserved in a restructured document. The structural framework needs to be rebuilt around the actual data flow.

---

## Finding Inventory

### CRITICAL

**F1: Input Contract Describes Nonexistent Data**
- §2 specifies atom streams from `library/sources/{source_id}/atoms/atoms.jsonl`
- No atomization engine exists in the committed architecture
- Actual input is NormalizedManifest + ContentUnit stream from the normalization engine
- 18+ fields specified per atom (atom_id, passage_id, structural_type, scholarly_function, etc.) describe an intermediate representation, not an input format
- The entire §2 Input Contract needs replacement

**F2: §5.1, §5.2, §5.3, §5.5 Cross-Referenced But Don't Exist**
- §4.A.1 Phase 2 references "the §5.1 standard" for self-containment
- §4.A.6 references "§5.3 rules" for cross-topic handling
- §3 review flags mention "one-excerpt-per-source-per-leaf diagnostic, §5.5"
- §4.A.1 references "§5.2" for completeness criterion
- §5 contains only Layer 1/2/3 descriptions and safeguards — no numbered subsections
- The self-containment standard — the most important quality criterion — has no formal definition

**F10: Atom Concept Is Unspecified Internal Intermediate**
- Since atomization was absorbed, atoms must be produced internally by this engine
- SPEC never defines: segmentation algorithm, the 7 structural types, the 16 scholarly functions, how atom_relations are detected, how bonded_reason bonds are established, how embedded_refs are detected
- Old atomization SPEC (178KB) presumably defines all this, but excerpting SPEC doesn't reference or incorporate it
- CC implementer would have no specification for the most complex part of the engine

### HIGH

**F3: §4.B References Nonexistent Atomization Engine Artifacts**
- §4.B.2 references "fingerprint_text_hash from the atomization engine's semantic fingerprint" and "fingerprint_key_terms"
- §4.B.8 references "semantic fingerprints from atomization engine (§4.B.5 in atomization SPEC)"
- No atomization SPEC exists in the committed architecture

**F4: D-011 Definition Changed But SPEC Uses Old Definition**
- ARCHITECTURE_DECISION.md: "D-011 transforms from 'excerpt contained within passage' to 'excerpt contained within division or chunk'"
- SPEC enforces passage containment throughout (V-1, processing per-passage, passage_id references)
- The word "passage" appears dozens of times as the processing unit
- Should be "division" (or "chunk" for oversized divisions)

**F5: §9 Describes ABD-Era Code as Starting Point**
- References extract_passages.py (2288 lines), assemble_excerpts.py (1021 lines), schemas/excerpt.json
- These predate the architecture decision and normalization engine
- Operates on different data model (book_id vs source_id)
- Misleads CC about implementation approach

**F11: Experiment's Validated Approach Doesn't Match SPEC's Three-Phase Model**
- Experiment validated: (1) classify segments by scholarly function, (2) group into teaching units — both on assembled text
- SPEC describes: (1) Boundary Detection on pre-classified atoms, (2) Self-Containment Evaluation, (3) Metadata Enrichment
- Experiment had no atom_relations or bonded_reason constraints — LLM inferred all boundaries from text
- Different processing architecture with different failure modes

**F12: MAX_TOKENS Constraint Not Captured**
- Format diversity experiment: Approach B classify on 2500-3100w divisions produces 125-166 segments
- Required MAX_TOKENS=32768 (original was 8192)
- SPEC has no mention of token limits, segment count scaling, or this operational finding

**F13: Passaging Phase Completely Unspecified**
- Architecture decision described absorbed passaging: cross-page assembly, division-to-chunk mapping, tiny division merging, format-specific handling, CRLF normalization (~800 lines estimated)
- SPEC contains zero specification of any of this
- This is the primary reason for the absorption

### MEDIUM

**F6: contracts.py Models 8 Unimplemented §4.B Capabilities**
- Full Pydantic models for ArgumentRole, DialogueLink, SemanticDuplicateLink, MasalaAnalysis, EvidenceChain, ResonanceLink, RepairSuggestion, ArgumentCompleteness
- All 8 marked "[NOT YET IMPLEMENTED]" in SPEC
- Creates confusion about build scope for CC

**F7: No Formal LLM Prompt Specification**
- Experiment validated specific prompts (APPROACH_A_SYSTEM, APPROACH_B_CLASSIFY_SYSTEM, APPROACH_B_GROUP_SYSTEM)
- SPEC describes what the LLM should do but never specifies prompt structure, Pydantic schemas for LLM output, or in-context examples

**F8: 5 Previously Flagged Concerns Unaddressed**
- From memory: taxonomy atom_ids→segment_ids contract break, old contracts.py confusion risk, Phase 3 prompts untested, evidence patterns untested, concrete example untraced
- None resolved in current SPEC

**F14: Approach B Over-Segments on Longer Texts**
- taysir/661 (3111w): B=41 units vs A=24 units (1.71x ratio)
- Consistent pattern across longer divisions
- No guidance on managing segment-count inflation or expected teaching unit size

**F15: D-023 Metadata Pass-Through Uses Wrong References**
- SPEC says upstream metadata preserved "by reference (source_id, passage_id, atom_ids)"
- passage_id and atom_ids don't exist in normalization output
- Should be: source_id, div_id, unit_index ranges

### LOW

**F9: CLAUDE.md Is Stale**
- Says "Input boundary: atom stream from atomization engine"
- Says "Fifth engine in pipeline order"
- Should be third engine, receiving normalized packages

**F16: passage_id Is Required Field on ExcerptRecord**
- No Optional, no default
- Passages don't exist in the architecture
- Should be div_id or similar

---

## What Must Happen

The SPEC needs section-by-section rewriting with the correct architecture as foundation. The domain knowledge (§4.A.2–§4.A.7) is preserved and relocated. The rewrite:

1. Replace §2 with actual input contract (NormalizedManifest + ContentUnit stream)
2. Replace §4.A.1 with architecture decision's three-phase model:
   - Phase 1: Deterministic Preprocessing (passaging absorption)
   - Phase 2: LLM Teaching Unit Extraction (classify-then-group, validated by experiment)
   - Phase 3: Metadata Enrichment
3. Specify Phase 1 using architecture decision + extract_divisions.py as design basis
4. Specify Phase 2 using experiment's Approach B, including MAX_TOKENS constraint
5. Define scholarly function taxonomy (the 16 types)
6. Define self-containment standard as formal §5.1
7. Replace passage_id → div_id throughout
8. Replace atom-as-input → segment-as-internal-intermediate
9. Separate core vs deferred §4.B capabilities
10. Update contracts.py to match

---

## Evidence Trail

- Architecture decision: `experiments/architecture_test/ARCHITECTURE_DECISION.md` (commit 5636ceb)
- Normalization output contracts: `engines/normalization/contracts.py` (NormalizedManifest, ContentUnit)
- Experiment data flow: `experiments/architecture_test/extract_divisions.py` (division assembly from packages)
- Experiment LLM interface: `experiments/architecture_test/run_tests.py` (Approach B schemas and prompts)
- Format diversity results: `experiments/format_diversity_test/results/RUN_SUMMARY.md` (MAX_TOKENS finding)
- Old absorbed SPECs: `engines/passaging/SPEC.md` (148KB), `engines/atomization/SPEC.md` (178KB)

---

## Review Protocol Compliance

- [x] Round 1 (Structural): Full SPEC + contracts read, cross-referenced against architecture decision + normalization contracts
- [x] Round 2 (Adversarial): Traced normalization→experiment→SPEC data flow, verified experiment schemas against SPEC phases, checked downstream contract compatibility
- [x] Round 3 (Self-Verification): Every factual claim verified with tool calls (file reads, size checks), rationalization check on all conclusions
- [x] Verdict delivered in separate response from Round 2
- [x] Checklist committed before verdict
