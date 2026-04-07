# SOFTENED Items Resolution — Session 8

**Date:** 2026-04-07
**Resolver:** CC Session 8
**Source:** BCV_SESSION4_SUPPLEMENTARY_REPORT.md (12 items)
**Protocol:** v5.0.2 §3A.3 (SOFTENED = takhfif, direction preserved but urgency/force reduced)

---

## Resolution Summary

| Disposition | Count | Items |
|-------------|-------|-------|
| ACCEPT-AS-IS | 11 | F1-MCU-027, F1-MCU-055b, F1-MCU-055c, F1-MCU-019, F2-002, F2-022, F2-023, F2-037, F2-039, F2-041, F2-042 |
| UPDATE (ledger) | 1 | F1-MCU-046 |
| **Total** | **12** | |

**No items required SPEC or prompt changes.**

---

## F1 Resolutions

### F1-MCU-027 — "NO POTENTIAL SHOULD BE LOST" → FP-18
**Disposition:** ACCEPT-AS-IS
**Reasoning:** FP-18 (SPEC line 69) captures three quality levels (excerpt candidate, acceptable, study-ready). The ALL-CAPS urgency is preserved in Layer A raw file (`f1_owner_original_notes_2026_04_03.txt` line 78). The measured prose in FP-18 is appropriate for a SPEC principle — SPECs are operational documents, not emotional archives. The raw files ARE the emotional archive.

### F1-MCU-046 — EE-1 chronological origin in F1, not just F5
**Disposition:** UPDATE LEDGER
**Action taken:** Updated Ledger Atom 1:
- Added F1 raw file (`f1_owner_original_notes_2026_04_03.txt` lines 222-224) to "Raw owner artifacts used"
- Added "Origin: F1 line 222 (first stated), F5 (expanded)" to Atom Register entry
**Reasoning:** EE-1 was first articulated in F1 ("the explained and explanation should NEVER be separated") before being expanded in F5. The ledger should credit chronological origin for traceability.

### F1-MCU-055b — "DO YOU SEE THE STRATEGY?" → FP-6
**Disposition:** ACCEPT-AS-IS
**Reasoning:** FP-6 (rules + intelligence + uncertainty gates) captures the strategic excerpting demand. The ALL-CAPS emphasis signals urgency, not a different principle. Raw Layer A preserves the emphasis.

### F1-MCU-055c — Strategic intertwining not standalone FP
**Disposition:** ACCEPT-AS-IS
**Reasoning:** The strategic intertwining insight IS captured through multiple channels:
- **B4-SP14** (MAQ-050): Mechanical protocol for intertwined content (A×B protocol)
- **F1-MCU-038** → mapped to B4-SP14 in mcu_trace.jsonl
- **F1-MCU-039** → mapped to META, explicitly noted as "Captured in scholarly-design skill + protocol v5.0 pedagogical grounding"
- The insight about purposeful topic mixing for comprehension is absorbed into the v5.0 protocol's pedagogical framework (DR11 Gemini DR, DR13 Gemini batch lifecycle)
No standalone FP is needed because the pedagogical dimension is distributed across the protocol's learning model, not isolated as a single principle.

### F1-MCU-019 — General post-production checklist
**Disposition:** ACCEPT-AS-IS
**Reasoning:** Phase 3 validation pipeline (V-P3-1 through V-P3-9) implements a comprehensive post-production checklist. The owner's checklist concept is broader than threat-detection, but the 9 validation rules cover: structural integrity, metadata completeness, self-containment verification, scholarly function coverage, and boundary coherence. The gap between "general checklist" and "Phase 3 validators" is minimal.

---

## F2 Resolutions

### F2-002 — Two levels of self-containment merged
**Disposition:** ACCEPT-AS-IS
**Reasoning:** Library-level self-containment ("the library also is self contained") is an architectural concern spanning all 7 engines + the scholar interface. The excerpting engine handles excerpt-level self-containment (SelfContainmentLevel enum). Library-level self-containment emerges from the pipeline working correctly, not from a single FP in one engine's SPEC.

### F2-022 — "I HATE LOOSE KNOWLEDGE" urgency halved
**Disposition:** ACCEPT-AS-IS
**Reasoning:** The anti-loose-knowledge principle IS captured in multiple FPs (FP-4 source-driven excerpting, FP-9 overgranulation worse than undergranulation, FP-18 study-readiness). The ALL-CAPS urgency is preserved in `f2_owner_raw_reaction_2026_04_04.txt` line 10 (Layer A). Systematic ALL-CAPS reduction is a known extraction pattern (see below).

### F2-023 — "I HATE ATTENDING A LECTURE..." emotional force lost
**Disposition:** ACCEPT-AS-IS
**Reasoning:** Same systematic pattern as F2-022. The lecture pain point is captured in the user memory (`user_study_pain.md`: "Owner spends HALF study time on prep"). The emotional force is in Layer A.

### F2-037 — 90/10 ratio → "main part / small part"
**Disposition:** ACCEPT-AS-IS
**Reasoning:** META-031 (MAQ line 128) preserves the verbatim text: "90% of my effort should go to memorizing ... Zero percent worrying about pipeline correctness." The quantitative precision is retained in the META entry. The structured extraction files use "main part / small part" as a paraphrase, but this is the Faqih (meaning) standard — the Hafiz (verbatim) standard is met by META-031.

### F2-039 — Universal corpus ambition absent from extraction
**Disposition:** ACCEPT-AS-IS
**Reasoning:** META-032 (MAQ line 129) preserves verbatim: "every single source of knowledge available on the internet should be integrated ... otherwise that would be a limit of knowledge." MAQ-078 also references full-corpus ambition. This is a PROJECT-LEVEL vision concern, not an excerpting-engine principle. It belongs in VISION.md (already present: §1 defines the library's scope as unbounded).

### F2-041 — Absolute boundary weakened to aspiration
**Disposition:** ACCEPT-AS-IS
**Reasoning:** The absolute definition ("its limits are only what is impossible: put the knowledge in my brain") is preserved in `f2_owner_raw_reaction_2026_04_04.txt` line 26 (Layer A). The weakening to "the dream is that..." in structured files is an extraction artifact. The principle is captured through FP-18's three-level quality framework and the project's overall vision.

### F2-042 — Excerpt-level mastery detail lost
**Disposition:** ACCEPT-AS-IS
**Reasoning:** The mastery concept ("list all excerpts one by one, re-write their contents") describes a study workflow, not an excerpting principle. The excerpting engine's job is to produce study-ready excerpts; the study workflow (list, reproduce, master) is a scholar interface concern. The raw text is preserved in Layer A for future UI design.

---

## Systematic Pattern: ALL-CAPS → Calm Prose

**Observation:** 5 of 12 SOFTENED items (F1-MCU-027, F1-MCU-055b, F2-022, F2-023, F2-041) are instances of the same extraction artifact: ChatGPT's Q&A process systematically normalizes ALL-CAPS urgency to measured prose.

**Assessment:** This is NOT a blocking issue because:
1. Raw .txt files (Layer A) preserve ALL-CAPS verbatim
2. META entries in MAQ preserve verbatim anchors
3. FPs capture principles in operational language appropriate for a SPEC

**Process improvement for future intake:** When processing new owner reaction files, the extraction pipeline should:
- Flag ALL-CAPS passages with a `severity: owner_emphasis` tag
- Preserve the urgency level in structured output alongside the measured paraphrase
- This prevents the same SOFTENED pattern from recurring in future batches

This improvement is NOT urgent (no current intake batches pending) but should be implemented before the next collection bundle.

---

## Verification

All 12 items resolved. 0 require SPEC changes. 0 require prompt changes. 1 ledger update applied.
The BCV Session 4 SOFTENED debt is now CLEARED.
