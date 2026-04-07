# Merged Atom Queue -- Excerpting Foundations Hardening

> Single source of truth for all atoms from F1-F8 owner feedback.
> Generated: 2026-04-04, Session 2.
> Sources: F1_F8_COMPLETE_ATOM_EXTRACTION.md (81 atoms), QUEUE_AUDIT (124 gaps), CRITICAL_ATOMS (63 NN + 62 RT)
> Cross-referenced against: SPEC.md section 1.1b (FP-1 through FP-18), FOUNDATIONS_HARDENING_LEDGER.md (atoms 1-17), THEMATIC_BATCHES.md (7 batches)
>
> **Dedup reconciliation: 2026-04-07, Session 10.** All 80 actionable atoms reconciled against ledger B1-B6 and SPEC content. See `DEDUP_RECONCILIATION_SESSION10.md` for full mapping.

---

## Summary Statistics

| Category | Count |
|----------|-------|
| **Unique MAQ entries (Sections D-I)** | 88 (80 actionable, 8 merged into other MAQs) |
| **Already finalized (Section A, ledger atoms 1-17)** | 17 |
| **Already captured in FPs, verify only (Section B)** | 18 |
| **Meta-directives from F1/F2 (Section C)** | 47 |
| **Deferred / cross-engine (Section J)** | 18 |
| **Red-team tests to automate (Section K)** | 62 |
| **Total owner ideas accounted for** | 250 |
| **Silent drops** | **0** |

### Reconciled implementation status (Session 10 dedup)

| Status | Count | Notes |
|--------|-------|-------|
| **IMPLEMENTED** (code/SPEC changes exist) | 37 | B1 FPs + B2 prompt/SPEC + B3 §6.7-6.10 + B4-P1 prompt + Session 10 §6.11-6.17 + FP-7/8 |
| **COVERED** (existing FPs/rules adequate) | 22 | No new changes needed |
| **SPEC-PENDING** | **0** | All 10 written in Session 10 |
| **MERGED** | 8 | Consolidated into other MAQs |
| **CAPTURED** | 4 | Already fully encoded in FPs |
| **DEFERRED** | 10 | Cross-engine or future capability |
| **OPEN** | 3 | Design questions needing DR or research |
| **PROJECT-LEVEL** | 4 | Budget/infrastructure, not excerpting SPEC |
| **DOCUMENTED** | 1 | Design rationale recorded |
| **REFERENCE** | 3 | Canonical examples for reference docs |
| **Section K** | 1 | Red-team test cross-reference |

### Authority distribution (new MAQ atoms, Sections D-I)

| Authority | Count |
|-----------|-------|
| owner_explicit | 58 |
| owner_consistent_inference | 11 |
| model_only | 5 |

---

## Section A: ALREADY FINALIZED (Ledger Atoms 1-17)

These atoms have been processed through the full hardening protocol (research, coworker challenge, doctrine adoption, SPEC/prompt/test encoding). No further action needed -- verify only during batch processing that their SPEC encoding has not drifted.

| Ledger # | Name | Status | SPEC Location |
|----------|------|--------|---------------|
| 1 | Explained-explanation unity (EE-1) | FINALIZED + EMPIRICALLY VALIDATED | FP-1, section 6.4b |
| 2 | Note-compensation vs source-preserving context (NC-1) | FINALIZED | FP-2, section 3 PARTIAL def |
| 3 | Linking-word preservation | FINALIZED | FP-3, C-SC-2 expanded |
| 4 | Rule/proof split without scholar linkage loss | DOCUMENTED -- deferred to K-1/K-2/K-3 | FP-8, section 6.1 design note |
| 5 | Disagreement mention vs tarjih separation | DOCUMENTED -- deferred to K-1/K-2/K-3 | FP-8, section 6.1 design note |
| 6 | Overgranulation vs undergranulation | FINALIZED | FP-9 |
| 7 | Forgiving rule / percentage threshold | DOCUMENTED | No SPEC change; empirical |
| 8 | Taxonomy must not bias excerpting | FINALIZED | FP-4 |
| 9 | Omission honesty | DOCUMENTED | Covered by C-SC-4/C-SC-5 |
| 10 | Fetched proof vs book-preserved proof | FINALIZED | FP-7 |
| 11 | Uncertainty gates for unseen methodologies | FINALIZED | FP-6 |
| 12 | Global trust poisoning from one local error | FINALIZED | FP-5 |
| 13 | Sanad-matn awareness | FINALIZED | FP-11 |
| 14 | Implied dependency detection (taqdir) | FINALIZED | FP-12, C-SC-2 expanded |
| 15 | Post-grouping viability check (MV-1) | FINALIZED | section 5.3 MV-1 |
| 16 | Principle conflict precedence | FINALIZED | FP-13 |
| 17 | Speaker-role inversion protection | FINALIZED | FP-14 |

---

## Section B: ALREADY CAPTURED IN FPs (Verify Only)

These extraction atoms map directly to existing FPs and need no further work beyond a verification pass confirming the SPEC text matches the owner's intent.

| FP | Extraction Atoms Covered | Verification Action |
|----|--------------------------|---------------------|
| FP-1 | ATOM-F5-001, ATOM-F5-003 | Verify section 6.4b covers variant/grading sensitivity detail from F5 |
| FP-3 | ATOM-F4-004, ATOM-CROSS-003 | Verify C-SC-2 covers all specific Arabic patterns listed in atoms |
| FP-4 | ATOM-F8-001, ATOM-F8-002, ATOM-F8-003, ATOM-F8-004, ATOM-F8-008 | Verify FP-4 text covers invariance, excerpting-bias naming, stage contamination |
| FP-5 | ATOM-F7-001, ATOM-F7-002, ATOM-CROSS-005 | Verify FP-5 covers cascading trust collapse, always-assume-wrong |
| FP-6 | ATOM-F5-005, ATOM-F5-009, ATOM-F6-007, ATOM-CROSS-002 | Verify FP-6 covers operational uncertainty gate mechanism |
| FP-7 | ATOM-F5-004, ATOM-F6-006 | Verify FP-7 covers both layers explicitly |
| FP-8 | ATOM-F4-001 | Verify FP-8 covers separation requirement; K-1/K-2/K-3 deferred |
| FP-9 | ATOM-F8-003 | Verify FP-9 covers cake metaphor reasoning (overgranulation harder to fix) |
| FP-14 | ATOM-F7-008 | Verify FP-14 covers attribution flattening prohibition |
| FP-15 | (covered by FP-14 extension) | Verify rhetorical posture detection scope |

---

## Section C: META-DIRECTIVES (F1/F2 Foundational Vision)

These are NOT individual excerpting atoms. They are foundational project-level principles, personal vision statements, study methodology requirements, and AI behavior directives from the owner's F1 and F2 raw notes. They belong in CLAUDE.md, principles.md, agent memory, or as engineering guidelines -- not as individual SPEC FPs.

**Disposition:** Each item is classified for where it should be encoded: CLAUDE.md (project rules), MEMORY (agent memory/principles.md), USER_MODEL (study workflow requirements), or DEFERRED_FEATURE (future capability).

### C.1 -- Project Identity and Motivation

| ID | Source | Owner Signal | Target |
|----|--------|-------------|--------|
| META-001 | MISSED-F1-009 | "The goal of me is to become the most knowledgeable scholar. The man with the most unmatched understanding and knowledge." | MEMORY -- owner's life goal driving the project |
| META-002 | MISSED-F1-010 | "This will give me the edge. No previous student of knowledge in history had the technology and Ai available." | MEMORY -- unprecedented edge ambition |
| META-003 | MISSED-F1-011 | "THIS IS THE DRIVING MOTIVATION ... The project should never be limited by 'the owner said this' or 'the usual way is like this'." ALL-CAPS. | CLAUDE.md -- anti-complacency directive |
| META-004 | MISSED-F1-024 | "PREVIOUS SCHOLARS HAD TO RELY ON LONG UNSTRUCTURED TEXT. I GET TO SEE EXACTLY HOW EVERYTHING IS CONNECTED." ALL-CAPS. | MEMORY -- vision statement |
| META-005 | MISSED-F1-034 | "THIS IS WHAT THE LIBRARY AIMS FOR; THE BEST POSSIBLE ENVIRONMENT." ALL-CAPS. | MEMORY -- quality standard |
| META-006 | MISSED-F7-003 | "it is a representation of my islamic knowledge ... what my life and religion practise will be built on ... what I will teach to thousands ... what my children will inherit ... the project of a lifetime." | MEMORY -- personal stakes (already partially in user_personal_connection.md) |
| META-007 | MISSED-F2-009 | "I HATE LOOSE KNOWLEDGE ... PLEASE MAKE SURE THIS IS UNDERSTOOD." ALL-CAPS with explicit request for understanding. | CLAUDE.md + MEMORY -- emotional core of the library's purpose |

### C.2 -- AI Behavior Directives

| ID | Source | Owner Signal | Target |
|----|--------|-------------|--------|
| META-008 | MISSED-F1-012 | "AI can be stupid and follow exactly what I say ... but that's not what will make my goal ... it is if AI can think outside the box, as if it were a team of 200 iq scientists." | CLAUDE.md -- already partially captured in role-definition.md but needs the "200 IQ scientists" framing |
| META-009 | MISSED-F1-014 | "This text ... must be understood by any agent working on this project." | CLAUDE.md -- F1/F2 principles must be understood, not merely documented |
| META-010 | MISSED-F7-001 (raw) | "I need you to find any possible bad scenario ... You need to really be extensive and exhaustive." | CLAUDE.md -- exhaustive threat identification directive |
| META-011 | MISSED-F7-002 (raw) | "YOU MUST THINK THOROUGHLY AND DEEPLY ABOUT ANY NIGHTMARE SCENARIO ... NO LENGTH LIMIT." ALL-CAPS. | CLAUDE.md -- no-length-limit exhaustive analysis |
| META-012 | MISSED-F7-012 (raw) | "not doing enough research ... I have the best research models available ... utilize it to the max." | CLAUDE.md -- already in coworker-dispatch rules but needs strengthening |
| META-013 | MISSED-F7-013 (raw) | "blind spots of agents ... collaboration has not yet been formalized ... no clear roles have been defined." | CLAUDE.md -- already addressed by coworker-dispatch.md |
| META-014 | MISSED-F7-014 (raw) | "not thinking about EVERY SINGLE THING WE CAN DO TO MAKE THIS LIBRARY better ... lacking in creative ideas, research." ALL-CAPS. | CLAUDE.md -- creative ideation demand |
| META-015 | MISSED-F7-010 (raw) | "ANYTHING THAT CAN BE BENEFICIALLY USED TO EXPAND POSSIBILITIES MUST BE IDENTIFIED AND INCORPORATED." ALL-CAPS. | CLAUDE.md -- technology-survey skill already exists, reinforce usage |
| META-016 | MISSED-F7-011 (raw) | "agent should have absolutely no limiting factor ... nothing that limits their potential." | CLAUDE.md -- agent environment optimization |

### C.3 -- Study Methodology and UX Vision

| ID | Source | Owner Signal | Target |
|----|--------|-------------|--------|
| META-017 | MISSED-F1-013 | "ONCE I START MY ISLAMIC STUDY JOURNEY ... MY ONLY WORRY SHOULD BE: MEMORIZING. PLEASE CATCH THIS CLEARLY." ALL-CAPS. | MEMORY + USER_MODEL -- the single most important UX principle |
| META-018 | MISSED-F2-001 | "I go to my room and lock the door ... the library needs to have everything I need at one place." | USER_MODEL -- library self-containment |
| META-019 | MISSED-F2-002 | "I'm not leaving this room until I know the exact rulings of prayer ... no man more knowledgeable than me concerning prayer." | USER_MODEL -- total immersion study sessions |
| META-020 | MISSED-F2-003 | "I can give the answer, explain why, explain the difference of opinions, lay down the proofs, and make a complete layman understand deeply." | USER_MODEL -- mastery benchmark |
| META-021 | MISSED-F2-004 | "explain it to a 5 year old in a way that he will outbeat Ibn Taymiyyah." | USER_MODEL -- hyperbolic mastery threshold |
| META-022 | MISSED-F2-005 | "my library ... leaves only the human factor up to me; memorizing. Linking topics, 'aha moments', mappings, gathering of knowledge, ... is all done by the library." | USER_MODEL + MEMORY -- library does everything except memorizing |
| META-023 | MISSED-F2-006 | "The library has made a revolutionary change, going against the hundreds year old tradition ... but this change is correct." | MEMORY -- library surpassing traditional scholarly organization |
| META-024 | MISSED-F2-007 | "I see connections you can only get after years of study ... branches ... where each branch ends." | USER_MODEL -- instant structural insight |
| META-025 | MISSED-F2-008 | "make one connection in the tree ... 'replicate-draw' it on paper ... summarize everything from the very first." | USER_MODEL -- step-by-step study process |
| META-026 | MISSED-F2-010 | Mnemonic/spatial linking methodology: "letter 'ش' and 'ص' sound alike." | USER_MODEL -- memorization technique informing navigation |
| META-027 | MISSED-F2-011 | "The best way for me is q&a. Being challenged and deeply asked about the knowledge." | DEFERRED_FEATURE -- Q&A/challenge feature requirement |
| META-028 | MISSED-F2-012 | "library should allow a smooth pane by pane guidance in learning ... full support to multiple panes." | DEFERRED_FEATURE -- multi-pane study support |
| META-029 | MISSED-F2-013 | Audio excerpting: "excerpt audio just like it excerpts text ... audio to be converted to text in the source engine." | DEFERRED_FEATURE -- audio-to-text-to-excerpt pipeline |
| META-030 | MISSED-F2-014 | Cyclic study: "skim over all three level 1 ... read properly ... active recall ... go back at a higher level." | USER_MODEL -- multi-pass deepening cycle |
| META-031 | MISSED-F2-015 | "90% of my effort should go to memorizing ... Zero percent worrying about pipeline correctness." | MEMORY -- 90/10 effort split |
| META-032 | MISSED-F2-016 | "every single source of knowledge available on the internet should be integrated ... otherwise that would be a limit of knowledge." | MEMORY -- universal corpus ambition |
| META-033 | MISSED-F2-017 | "the library's ONLY limit is that it cannot put knowledge in the owner's brain. Everything else is the library's job." | MEMORY -- ultimate boundary definition |
| META-034 | MISSED-F2-018 | "I can replicate it from scratch ... list all excerpts ... re-write their contents." | USER_MODEL -- mastery definition |

### C.4 -- Excerpting-Relevant Meta-Principles (from F1)

These F1 items are meta-principles that GOVERN how excerpting atoms are implemented. They are not individual atoms but constraints on all atoms.

| ID | Source | Owner Signal | Target | Affects Atoms |
|----|--------|-------------|--------|---------------|
| META-035 | MISSED-F1-001 | "capturing one scholar's whole explanation on one topic in particular." | MEMORY -- excerpt = one scholar, one topic | All granularity atoms |
| META-036 | MISSED-F1-002 | "by topic, I do not mean 'heading' ... 'one exact granulated thing the conversation is about'." | MEMORY -- topic != heading | All granularity atoms |
| META-037 | MISSED-F1-003 | Owner's fear of the definition CAPPING POTENTIAL. "I'm not sure if this will cause some potential being lost." | MEMORY -- anti-cap principle | All atoms |
| META-038 | MISSED-F1-005 | "making an encyclopedia of the science, but in a different structure; with a taxonomy tree, with excerpts." | MEMORY -- encyclopedia framing | All atoms |
| META-039 | MISSED-F1-006 | "The whole point is that it's not that simple. We can't just literally separate every single topic." | MEMORY -- naive separation destroys library | All granularity atoms |
| META-040 | MISSED-F1-007 | "I open a topic ... see what a particular source said. True mastery comes by mastering every single topic ... understanding relationships, structure, reason." | MEMORY -- experience specification | All atoms |
| META-041 | MISSED-F1-008 | The 99%/1% problem across 1000 books. | MEMORY -- fundamental justification for excerpting | All atoms |
| META-042 | MISSED-F1-016 | DOUBLE DANGER: (1) tearing continuous text, (2) forcing diverse structures into one taxonomy. | MEMORY -- risk awareness | Safety + boundary atoms |
| META-043 | MISSED-F1-019 | "the core architecture is missing ... still room for ambiguity ... no clear protocols." Origin of hardening operation. | MEMORY -- already addressed by hardening |
| META-044 | MISSED-F1-028 | "excerpting is NOT just producing an excerpt -- it requires post-production protocol." ALL-CAPS "catastrophic!" | CLAUDE.md -- post-production evaluation mandate |
| META-045 | MISSED-F1-029 | "llms see their only jobs: produce an excerpt .. no evaluation, no reasoning ... catastrophic!" | CLAUDE.md -- excerpting must include reasoning |
| META-046 | MISSED-F1-037 | "current version has skipped too quickly from the 'analysis' / 'research' phase into implementation." | MEMORY -- already addressed by hardening |
| META-047 | MISSED-F5-004 | "the main concept the entire library should revolve around: separation of concerns." | MEMORY -- highest-level design principle |

---

## Section D: BATCH 1 -- Safety & Integrity

Focus: trust poisoning, silent failures, deceptive cleanliness, corruption prevention, severity classification.
Prompt surface: minimal (these are mostly SPEC principles + validation rules).

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-001 | ATOM-F4-007, F4-NN-002, F4-NN-009 | owner_explicit | Surrounding context may be used diagnostically for engineering but must NEVER silently rescue the owner-facing verdict on a defective excerpt. Owner-verdict vs engineering-reconstruction separation. | NEW | SPEC | Add FP or explicit rule in section 3 distinguishing engineering layer from owner-facing verdict. |
| MAQ-002 | ATOM-F5-002, F5-NN-001, MISSED-F5-011 | owner_explicit | Generated summary notes must not silently replace source-preserving context. "ALWAYS TRY TO KEEP THINGS AS CLOSE TO THE ORIGINAL AUTHORS WORDINGS / WORK / SOURCE AS POSSIBLE." NN: F5-NN-001. | PARTIAL (FP-2 exists but anti-replacement prohibition is weaker) | SPEC | Strengthen FP-2 with explicit anti-replacement prohibition. |
| MAQ-003 | ATOM-F6-008, F6-NN-010, MISSED-F6-006 | owner_explicit | Secondary help layers (comparisons, summaries, chunking) must never silently replace the preserved source layer. "original text should not be altered, only excerpted." NN: F6-NN-010. | NEW | SPEC | Add explicit layer-separation rule: help layers sit BESIDE source, never overwrite. |
| MAQ-004 | ATOM-F7-003, MISSED-F8-002 | owner_explicit | Confirmed corruption triggers immediate stop-using threshold. Cascading trust collapse: wrong excerpt -> whole book -> whole engine -> whole knowledge base. Severity ladder. | NEW | SPEC | Add severity ladder to FP-5 (threshold levels for response actions). |
| MAQ-005 | ATOM-F7-005, F7-NG-003 | owner_explicit | No unbounded content error may remain live without immediate containment, blast-radius assessment, and visible warning. NN: F7-NG-003. | NEW | SPEC + Phase 3 | Add blast-radius containment requirement to error handling section. |
| MAQ-006 | ATOM-F7-009, ATOM-CROSS-007, F7-NG-008 | owner_explicit | Excerpting cuts must be honest -- result must not look like uninterrupted source flow. "NO DECEPTION; CLEAR AND HONEST." Deceptive cleanliness is a named failure mode. NN: F7-NG-008. | NEW | SPEC + Phase 3 | Add omission-honesty rule: cuts must be visible, not hidden. Add to FP or new principle. |
| MAQ-007 | ATOM-F7-010, F7-NG-009 | owner_explicit | Validation must prove hard cases, not merely pass polished easy-path examples. Hollow evaluation is itself a failure. NN: F7-NG-009. | NEW | SPEC + tests | Add validation rigor requirement. Affects test design philosophy. |
| MAQ-008 | ATOM-F7-015 | owner_explicit | Hidden omission makes user memorize a surgically cleaned artifact as faithful source flow. Deceptive cleanliness is a specific damage path. | MERGED into MAQ-006 | -- | -- |
| MAQ-009 | ATOM-F8-009, F8-NN-004, MISSED-F8-001 | owner_explicit | Silent excerpt corruption and visible taxonomy misplacement are different severity classes. Owner: "An excerpt being placed at the wrong taxonomy leaf does not worry me nearly as much as excerpts being wrong." | NEW | SPEC + contracts | Formalize severity-class distinction. Add to FP-5 or new FP. |
| MAQ-010 | ATOM-F8-006, F8-NN-007 | model_only | Placement validation must never silently reject or reshape excerpts merely because they fit the current tree badly. Validator must not become a covert second excerpter. | NEW | Phase 3 | Add validator-integrity constraint to Phase 3 validation rules. |
| MAQ-011 | ATOM-F7-018 | owner_explicit | Suboptimality (loose architecture, insufficient research, weak tools) is itself a failure even if nothing is directly corrupt -- it permanently lowers the ceiling of scholarship. | NEW | SPEC (meta) | Add as guiding principle. Not prompt-affecting. |
| MAQ-012 | MISSED-F1-017, MISSED-F1-018 | owner_explicit | Dedicated threat-detection using ALL LLMs. Mandatory threat checklist per excerpt. "this should be a top priority." Excerpting is NOT just producing excerpts -- it requires post-production protocol. | NEW | SPEC + Phase 3 | Add post-production verification mandate. Links to Phase 3 consensus + validation. |
| MAQ-013 | MISSED-F3-003 | owner_explicit | "WE SHOULD TAKE ABSOLUTELY NO RISKS WHEN IT COMES TO CORRUPTION POTENTIAL, MISUNDERSTANDINGS." ALL-CAPS. | MERGED into MAQ-004/006 | -- | Reinforces MAQ-004 and MAQ-006. |
| MAQ-014 | MISSED-F5-010 | owner_explicit | "NEVER ASSUME EXCERPTING CANNOT GO WRONG. ALWAYS ASSUME AN EXCERPT IS WRONGFULLY EXCERPTED UNTIL PROVEN OTHERWISE." Owner demands EXPANDING list of NEVER/ALWAYS constraints. | PARTIAL (FP-5 has "always assume wrong") | SPEC | Verify FP-5 captures the full list. Consider creating an expanding checklist artifact. |
| MAQ-015 | MISSED-F4-002 | owner_explicit | "There should not be one safety net to identifying excerpts ... absolutely no room for looseness." Multiple safety nets required. | NEW | SPEC | Links to Phase 3 multi-model consensus. Document as multi-layer safety requirement. |
| MAQ-016 | MISSED-F5-005 | owner_explicit | "A SOURCE INTAKEN BY THE LIBRARY SHOULD NOT BE LOST - NOT IN FULL NOR PARTS OF IT." ALL-CAPS completeness-of-ingestion principle. | NEW | SPEC | Add completeness principle: no silent content loss during excerpting. |
| MAQ-017 | F7-NG-004, ATOM-F7-006 | owner_explicit | System must never present low-confidence knowledge with the same confidence profile as strongly verified knowledge. Confidence-differentiated presentation. | NEW | Phase 3 + display | Add confidence-profile differentiation requirement to Phase 3 enrichment. |

---

## Section E: BATCH 2 -- Self-Containment

Focus: C-SC criteria, linking words, taqdir, backward hunting, entry frames, title retention.
Prompt surface: C-SC-2 expansion, self-containment evaluation instructions.

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-018 | ATOM-F3-001, F3-NN-001, MISSED-F3-006 | owner_explicit | Surface chapter-intro language must not be treated as decisive for function classification. "ABSOLUTELY NO ROOM FOR BLIND EXCERPTING." NN: F3-NN-001. | NEW | PROMPT | Add anti-surface-classification rule to Phase 2 classify prompt. |
| MAQ-019 | ATOM-F3-003, F3-NN-006 | owner_explicit | Small, strongly linked carryover material may remain attached when removing it would produce worse self-containment. Forgiving retention for linked carryover. NN: F3-NN-006. | NEW | PROMPT + SPEC | Add explicit forgiving-retention logic to C-SC rules. |
| MAQ-020 | ATOM-F3-004, F3-NN-004, MISSED-F3-004, MISSED-F3-007 | owner_explicit | Chapter titles must be retained when "هذا الباب" depends on them. Retention is asymmetric per excerpt. POSITIONAL CONTEXT: title retention reveals WHERE in the source the scholar placed the content. Linking-word detection system required. NN: F3-NN-004. | NEW | PROMPT + SPEC | Add title-retention asymmetry rule. Add positional-context insight. |
| MAQ-021 | ATOM-F3-009, F3-NN-010, ATOM-CROSS-001 | owner_explicit (5 collections) | Function classification and split/merge must never be automated by one blunt heuristic. Dependency analysis must precede all decisions. Anti-"ENCOUNTERED -> ENFORCING PROTOCOL X" pattern. Cross-collection: F3/F4/F5/F6/F8. NN: F3-NN-010. | PARTIAL (FP-3 + FP-6) | PROMPT | Elevate to explicit anti-heuristic principle. Strengthen Phase 2 prompt. |
| MAQ-022 | ATOM-CROSS-006 | owner_explicit (2 collections) | Surface appearance must never override actual function analysis. System must look past what text "looks like" to what it "does." | MERGED with MAQ-018 | -- | -- |
| MAQ-023 | MISSED-F1-020, MISSED-F1-021 | owner_explicit | Two-layer model: theory layer + context layer. "the context part is clearly not well defined yet." "A SCHOLAR'S KNOWLEDGE SHOULD NEVER BE BASED ON GUESSES." "I SHOULD BE ABLE TO STUDY DIRECTLY FROM THE EXCERPT." ALL-CAPS. | NEW | SPEC | Formalize the two-layer excerpt model. Links to FP-18 (three quality levels). |
| MAQ-024 | MISSED-F1-022, MISSED-F1-031 | owner_explicit | "Linked list" concept: each excerpt should reference its predecessor in the original source. "Angel on my shoulder" vision: ideal context delivery per excerpt. | DEFERRED_FEATURE | -- | Save to deferred features. Informs source-surroundings (FP-10) design. |
| MAQ-025 | MISSED-F5-003 | owner_explicit | Owner's honest ambivalence: he WANTS explanation-explained separation but FEARS tradeoffs. "I could totally be wrong." Current EE-1 is a risk-based default, not absolute doctrine. | DOCUMENTED | -- | Record as design rationale for EE-1. No action needed -- EE-1 already accounts for this. |

---

## Section F: BATCH 3 -- Boundary & Grouping

Focus: teaching unit formation, EE-1 extensions, function mixing, sibling topics, chapter vs full-topic scope.
Prompt surface: GROUPING RULES section of GROUP_SYSTEM_PROMPT.

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-026 | ATOM-F3-002, F3-NN-002, SOFTENED-F3-001 | owner_explicit | Multi-function passage (intro + ruling + proof-overview + refutation) must not be kept merged when all functions are substantively present. Owner: "THIS IS NOT A GOOD EXCERPT. IT IS TOO BROAD." ALL-CAPS. | NEW | PROMPT + SPEC | Add multi-function split rule to Phase 2 grouping prompt. |
| MAQ-027 | ATOM-F3-005, F3-NN-005, MISSED-F3-006 | owner_explicit | Chapter-specific introduction must be distinguished from full-topic introduction. Confusing them creates source-scope mismatch. "reading an introduction that comes from a source that covers the topic only partially can seriously harm the understanding." | NEW | PROMPT + SPEC | Add introduction-scope classification to Phase 2. |
| MAQ-028 | ATOM-F5-007, F5-NN-006 | owner_explicit | Note question must not cap deeper diagnosis: when a pair is structurally malformed, note-visibility is a surface symptom, not the real issue. NN: F5-NN-006. | NEW | SPEC | Add malformation-first-diagnosis rule to Phase 3 note-handling logic. |
| MAQ-029 | ATOM-F7-007, F7-NG-005 | owner_explicit | Boundary decisions must not distort meaning, remove necessary anchoring, or atomize study units into unusable fragments. NN: F7-NG-005. | PARTIAL (FP-1 + FP-3 + FP-9) | SPEC | Verify existing FPs collectively cover this. May need a synthesis principle. |
| MAQ-030 | ATOM-F8-012, F8-NN-006 | owner_consistent_inference | Blind or weakly guided processing must be audited for boundary consistency across comparable passages. Uneven excerpt families are a real danger. NN: F8-NN-006. | NEW | SPEC + tests | Add boundary-consistency audit requirement. Design cross-passage comparison tests. |
| MAQ-031 | MISSED-F3-005 | owner_explicit | "EXCERPTING IS WAY MORE THAN IDENTIFYING EXCERPTS. IT'S ANALYSIS, PROTOCOLS, SUB-EXCERPTING." ALL-CAPS. | MERGED into MAQ-012 | -- | Reinforces MAQ-012 (post-production mandate). |
| MAQ-032 | MISSED-F1-033 | owner_explicit | Scholar-quoting-scholar protocol: quote-layer preservation, quote-as-proof vs quote-as-emphasis distinction, "who quoted who" analytics, prefixing excerpted quotes with "قال ابن مالك: ....". Complete intertextual quotation handling. | NEW | PROMPT + SPEC + contracts | Add quote-layer handling rules. Links to FP-14/FP-15. Major new capability. |
| MAQ-033 | MISSED-F1-035 | owner_explicit | Three-part proof structure: (1) mention proof, (2) explain proof, (3) defend/refute. "1 & 2 should be together." Refutations get a separate leaf: "الردود." | NEW | PROMPT + SPEC | Add proof-structure taxonomy to Phase 2 grouping rules. |
| MAQ-034 | MISSED-F1-036 | owner_explicit | ibn_aqil_v1 #11 analysis: confusion at matn vs poetry vs evidence, "undercover opposition" context problem, "welcome-note" concept for context. | NEW | PROMPT + SPEC | Informs welcome-note feature (MAQ-037). Concrete use case for context confusion. |
| MAQ-035 | MISSED-F1-046 | owner_explicit | "و" self-containment problem + owner's 7-excerpt worked example showing proper excerpting. "NO DECEPTION; CLEAR AND HONEST." Strategic intertwining insight. | PARTIAL (FP-3 covers linking words) | PROMPT | Use owner's 7-excerpt example as few-shot or calibration reference. |

---

## Section G: BATCH 4 -- Granularity

Focus: split/merge thresholds, mention vs topic, forgiving rule, minimum viability, quantitative gates.
Prompt surface: Derived Benefits Rule, Numbered Item Boundaries, MV-1.

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-036 | ATOM-F3-006, F3-NN-007, MISSED-F1-039 | owner_explicit | Forgiving rule has a quantitative limit: at ~33% overlap the forgiving rule no longer applies. F1 origin: dual-gate system (percentage AND character count, 10000-word/500-word example). Anti-over-forgiveness constraint. NN: F3-NN-007. | NEW | PROMPT + SPEC | Add quantitative threshold to forgiving rule. Design dual-gate (percentage + absolute count). |
| MAQ-037 | ATOM-F3-007, F3-NN-008 | owner_explicit | Duplicating a whole large merged passage across multiple leaves is not acceptable when sub-excerpting is available. NN: F3-NN-008. | NEW | SPEC | Add anti-duplication-via-sub-excerpting rule. |
| MAQ-038 | ATOM-F3-008, F3-NN-009 | owner_explicit | Short hukm-return phrase inside refutation may stay, but hukm must ALSO be represented at hukm home. Knowledge-scattering prevention. NN: F3-NN-009. | NEW | PROMPT + SPEC | Add hukm-visibility rule: hukm must appear in hukm-focused excerpt regardless of where else it appears. |
| MAQ-039 | ATOM-F4-005, F4-NN-006 | owner_explicit | Disagreement marker and full unbiased opinion listing answer the same question and should remain together as one disagreement-structure excerpt. "THIS IS TOO GRANUAL." | NEW | PROMPT + SPEC | Add intra-khilaf clustering rule to Phase 2 grouping. |
| MAQ-040 | ATOM-F4-006, MISSED-F4-007 | owner_explicit | Question-cluster reasoning ("what question is each segment answering?") as methodology for split/keep decisions. Owner proposed a checklist of questions with "heavy emphasis on logical reasoning." NN: F4-NN-008. | NEW | PROMPT + SPEC | Add question-cluster methodology to Phase 2 classification prompt. |
| MAQ-041 | ATOM-F8-007, F8-NN-008 | owner_explicit | Tree revision must not retroactively rewrite already-frozen excerpt truth. Placement changes allowed, excerpt identity changes are not. | PARTIAL (implied by FP-4) | SPEC | Make the retroactive prohibition explicit in FP-4 or as a new rule. |
| MAQ-042 | ATOM-F8-013, F8-NN-010 | owner_explicit | Any sign that excerpting is configuration-sensitive rather than source-sensitive must trigger an audit, not normalization. | NEW | SPEC + tests | Add configuration-sensitivity detection requirement and audit trigger. |
| MAQ-043 | ATOM-F8-015 | owner_explicit | Overgranulated placement creates false contradictions between sibling leaves: related excerpts look contradictory in separate overcut leaves. | NEW | SPEC + taxonomy | Add false-contradiction mechanism to FP-9 explanation. |
| MAQ-044 | MISSED-F1-004 | owner_explicit | The granulation cascade example: "definition of al-sarf" -> "in the arabic language" -> "the al-basra school" -> opinion level. The ONLY place the owner demonstrated granulation by progressive example. | NEW | SPEC (reference) | Preserve as canonical granulation example in SPEC or reference doc. |
| MAQ-045 | MISSED-F1-040 | owner_explicit | Two principles: (1) no hard character-count caps on excerpts -- "goes entirely against intelligent library," (2) no layout mutation of determined excerpts -- "MUTATES the original source text." | NEW | SPEC + PROMPT | Add anti-cap and anti-mutation rules. |
| MAQ-046 | MISSED-F1-041 | owner_explicit | Examples in wrong locations "should be seen as equal to it not existing." Surrounding text around examples should always give context of how transition went from theory to practice. | NEW | PROMPT | Add wrong-location = nonexistent rule. Theory-to-practice transition context. |
| MAQ-047 | MISSED-F1-043 | owner_explicit | "a mention IS NOT A REASON TO EXCERPT." Detecting a topic mentioned is not sufficient to create an excerpt. "The system should not be 'forced' to 'find' an excerpt." | NEW | PROMPT + SPEC | Add mention-vs-excerpt distinction. Critical anti-false-positive rule. |
| MAQ-048 | MISSED-F1-044 | owner_explicit | Theory-example vs practice-example distinction. "Examples should be separated. One example per excerpt." Example leafs are an "archive" of practical application. | NEW | PROMPT + SPEC | Add example classification rule to Phase 2. |
| MAQ-049 | MISSED-F1-042 | owner_explicit | "Solutions should NEVER be separated from the thing they solve." Solved-solver unity rule extends explained-explanation principle. | NEW | PROMPT + SPEC | Add solved-solver unity as EE-1 extension. |
| MAQ-050 | MISSED-F1-030 | owner_explicit | The "A x B intertwined" protocol: if both short, duplicate at both leaves; if A long B short, B stays in A but not reverse. Decision protocol for intertwined content. | NEW | PROMPT + SPEC | Add intertwined-content handling protocol. |
| MAQ-051 | MISSED-F7-008 (raw) | owner_explicit | Fear of excerpts degenerating to single sentences/atoms. "extreme granulation ... an excerpt pretty much just became one sentence." | MERGED into FP-9 | -- | Reinforces FP-9 (overgranulation). Verify SPEC captures single-sentence degeneration risk. |
| MAQ-052 | F5-NN-007 | model_only | Readable note-backed explanation is not proven safe if explanation-to-proof linkage is unresolved. Readability masking integrity failure. | NEW | SPEC | Add readability-does-not-equal-correctness principle. |

---

## Section H: BATCH 5 -- Tarjih, Khilaf, Proof & Evidence (Merged)

Focus: disagreement handling, tarjih separation, proof layers, variant analysis, isnad handling, fetched proofs.
Prompt surface: DECONTEXTUALIZATION PREVENTION, tarjih rule, EV-1/EV-2/EV-3 evidence rules.

NOTE: Batches 5 (Tarjih & Khilaf, 7 atoms) and 6 (Proof & Evidence, 18 atoms) from THEMATIC_BATCHES.md are merged here per the batches document instruction.

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-053 | ATOM-F4-002, F4-NN-003, SOFTENED-F4-003 | owner_explicit | Tarjih is attribution-critical: it records what a specific scholar prefers. Clipping/flattening tarjih changes what the scholar is recorded as saying. "THE ترجيح OF A SCHOLAR IS EXTREMELY IMPORTANT." ALL-CAPS. NN: F4-NN-003. | PARTIAL (FP-8 exists but attribution-loss risk not emphasized) | PROMPT + SPEC | Strengthen FP-8 with attribution-critical framing. |
| MAQ-054 | ATOM-F4-003, F4-NN-005 | owner_explicit | Clipped tarjih lead-in (e.g., "وأصحها ما ذهب إليه الجمهور" without completion) must not be accepted as standalone excerpt. Tarjih must be completed. NN: F4-NN-005. | NEW | PROMPT + SPEC | Add tarjih-completeness rule to Phase 2 classify/group prompt. |
| MAQ-055 | ATOM-F4-006 (sub-entry for khilaf), MISSED-F4-005 | owner_explicit | "AN IMPORTANT PART OF FIQH IS KNOWING HOW THE OPINIONS ARE DIVIDED." Why disagreement-marking matters. | MERGED into MAQ-039 | -- | Reinforces rationale for MAQ-039 (intra-khilaf clustering). |
| MAQ-056 | ATOM-F5-006, MISSED-F5-002 | owner_explicit | Hadith variant risk: scholars may explain different wordings/routes while appearing to discuss the same proof. Concrete examples: versions, ratings, the "hunting" problem. "I don't want to be hunting." | NEW | SPEC | Add variant-mismatch risk to FP-7 or as a new FP. |
| MAQ-057 | ATOM-F5-008, ATOM-CROSS-004 | owner_consistent_inference / owner_explicit | Alignment layer needed: link book-preserved proof wording to authoritative fetched proof wording. Record match type (exact / close variant / materially different). Three layers: (1) scholar-book witness, (2) authoritative fetched, (3) comparison/alignment. | DEFERRED (cross-engine) | -- | Save for cross-engine design phase. Informs FP-7 implementation. |
| MAQ-058 | ATOM-F6-001, MISSED-F6-001 | owner_explicit | Scholar-book proof = witness, not memorization source. "automatically a red flag concerning directly memorizing this hadith like this." | PARTIAL (FP-7) | SPEC | Verify FP-7 explicitly calls scholar-book proof "not a memorization source." |
| MAQ-059 | ATOM-F6-002, F6-NN-002 | owner_explicit | Original author's wording must never be mutated for study convenience. Help sits BESIDE source as parallel layer. NN: F6-NN-002. | NEW | SPEC | Add parallel-layer principle. Extends primary-text immutability to study contexts. |
| MAQ-060 | ATOM-F6-003, F6-NN-009, MISSED-F6-003 | owner_explicit | Wording differences between proof variants must be classified: significant (affects meaning/ruling), non-significant, or uncertain. Concrete Aa/Ab/Ac example. NN: F6-NN-009. | DEFERRED (cross-engine) | -- | Save for proof-alignment cross-engine design. |
| MAQ-061 | ATOM-F6-004, MISSED-F6-004, MISSED-F6-005 | owner_explicit | Map which scholars used which proof variants. Show when wording differences correlate with different conclusions. "UNPRECEDENTED ADVANTAGE." "percentage of scholars who chose a specific opinion ... INDICATE THIS CLEARLY. MAKE SURE THIS IS NOT LOST." ALL-CAPS. | DEFERRED (cross-engine / data analysis) | -- | Save for cross-engine analytics design. MUST NOT BE LOST. |
| MAQ-062 | ATOM-F6-005, F6-NN-008, MISSED-F6-006 | owner_explicit | Study-friendly chunking belongs to authoritative fetched proof layer, NOT scholar-book witness. Layer-aware chunking required. Concrete hadith chunking example. NN: F6-NN-008. | DEFERRED (cross-engine) | -- | Save for proof-layer chunking design. |
| MAQ-063 | ATOM-F7-004 | owner_explicit | Every study-facing unit must remain auditably tied to source, version, and processing lineage (provenance). Weak provenance makes blast-radius containment impossible. NN: F7-NG-002. | NEW | SPEC + contracts | Add provenance-auditability requirement. Links to D-023 but stronger. |
| MAQ-064 | ATOM-F7-014 | owner_explicit | Excerpting is where source text becomes study units; errors here directly shape what is memorized. Highest-risk transformation stage. | MERGED into FP-5 | -- | Verify FP-5 captures excerpting as highest-risk stage. |
| MAQ-065 | MISSED-F1-023 | owner_explicit | "a CLEAR DISTINCTION between 'rules' and 'proofs'" with concrete taxonomy example: استحباب اجتماع --> الحكم / الأدلة --> من الحديث --> حديث أنس. First articulation of rule/proof/evidence hierarchy. | NEW | SPEC (reference) | Preserve as canonical proof-taxonomy example. Informs FP-8 and K-1/K-2/K-3. |
| MAQ-066 | MISSED-F1-025 | owner_explicit | "mentioning of a proof by a scholar and his explanation should NOT be separated." F1 ORIGIN of EE-1 (predates F5). | CAPTURED (FP-1/EE-1) | -- | Verify chronological attribution in EE-1 references F1 as origin. |
| MAQ-067 | MISSED-F1-026, MISSED-F1-027 | owner_explicit | Proof-stack grouping per scholar: knowing which set of proofs a scholar used together. Losing this is "a CORRUPTION." Proposed solution: "clearly separated section that says: 'this scholar's other proof stack is: ....'" | NEW | SPEC + contracts | Add proof-stack cross-reference requirement. Inform taxonomy design. |
| MAQ-068 | MISSED-F5-006, MISSED-F5-007 | owner_explicit | "THE IMPORTANT NEW RULE: KNOWLEDGE SOURCES SHOULD NOT BE OUR FINAL AUTHORITATIVE SOURCE FOR PROOFS." ALL-CAPS "A NIGHTMARE: I DO NOT WANT TO STUDY SOURCES THAT ARE NOT 100% CONFIRMED." Covers ALL proof types: Quran, hadith, Arabic poetry. | CAPTURED (FP-7) | -- | Verify FP-7 scope covers all proof types, not just hadith. |
| MAQ-069 | MISSED-F5-008 | owner_explicit | Concrete scholarly methodology pattern: topic -> proof1 -> explanation-containing-rules -> proof2 -> more explanations. Deeply interconnected rulings and proof explanations. | NEW | PROMPT | Add interleaved-methodology awareness to Phase 2 prompt. |
| MAQ-070 | MISSED-F5-009 | owner_explicit | "FOCUS ON INTELLIGENCE, WISDOM AND REASONING OF THE LLM ITSELF ... INSTEAD OF ONLY RELYING ON RULES AND PROTOCOLS." ALL-CAPS. New-scholar-born scenario as justification. | CAPTURED (FP-6) | -- | Verify FP-6 captures intelligence-over-rules with sufficient emphasis. |
| MAQ-071 | MISSED-F1-045 | owner_explicit | Footnote handling: "never separate a directly related footnote from the thing it is footnoting." Footnotes can become "sub-books." Owner's default: "always lean towards keeping the footnote glued." | NEW | PROMPT + SPEC | Add footnote-handling protocol to Phase 1/Phase 2 rules. |
| MAQ-072 | F5-NN-008, ATOM-F5-003 | owner_explicit | Do not collapse all hadith explanations into one generic proof source when version, wording, or grading may differ. Version-sensitivity of hadith explanations. | PARTIAL (FP-7 + EE-1) | SPEC | Verify FP-7 covers version-sensitivity explicitly. |
| MAQ-073 | MISSED-F4-001 | owner_explicit | "IMPORTANT IDEA: A POSSIBLE 'DEFINITION' FOR AN EXCERPT IS LIKE A 'quote'." Excerpt = quote conceptual framing with scholar-quoting context-preservation analogy. | NEW | SPEC (reference) | Preserve as conceptual definition. Informs excerpt-definition canon. |

---

## Section I: BATCH 6 -- Other

Items that do not cleanly fit batches 1-5, including open questions, project-level concerns, methodology, and miscellaneous.

| MAQ-ID | Source(s) | Authority | Summary | Status | Prompt? | Action |
|--------|-----------|-----------|---------|--------|---------|--------|
| MAQ-074 | ATOM-F3-012 | owner_explicit | OPEN QUESTION: How should the system mark a chapter-specific introduction so it is not mistaken for a full-topic introduction at the topic leaf? | OPEN | Phase 2 | Requires design decision. Links to MAQ-027 (intro-scope classification). |
| MAQ-075 | ATOM-F5-010 | owner_explicit | OPEN QUESTION: Under what strict metadata and linkage conditions can explanation and explained text be safely separated in hadith-heavy materials? | OPEN | -- | Requires deep research. Links to EE-1 exceptions. |
| MAQ-076 | ATOM-F8-005 | owner_consistent_inference | Post-excerpting guidance from taxonomy is ALLOWED for placement, ranking, navigation, presentation -- but only after excerpt truth is frozen. Positive allowance for post-excerpting guidance. | NEW | SPEC | Add positive allowance statement to FP-4 (currently only states the prohibition). |
| MAQ-077 | ATOM-F8-014 | owner_explicit | OPEN QUESTION: Is there any non-taxonomic guidance that would be acceptable if it improved consistency without altering rightful excerpt output? | OPEN | -- | Requires design research. |
| MAQ-078 | ATOM-F7-011 | owner_explicit | Economics/performance model must remain compatible with full-corpus ambition. "50 euros on 5 books" is not viable at scale. "every source on the internet" is the target. NN: F7-NG-011. | PROJECT-LEVEL | -- | Tracked in project budget/scaling docs, not excerpting SPEC. |
| MAQ-079 | ATOM-F7-012, F7-NG-012 | owner_explicit | Project memory durability: progress, artifacts, backups, exports, datasets must survive failure and migration. 5TB Google Drive available. NN: F7-NG-012. | PROJECT-LEVEL | -- | Tracked in project infrastructure docs. |
| MAQ-080 | ATOM-F7-013, F7-NG-013 | owner_explicit | All collected data structured for future reuse, audit, and local-model training. Today's outputs cannot be disposable. NN: F7-NG-013. | PROJECT-LEVEL | -- | Already in CLAUDE.md Rule 13. |
| MAQ-081 | ATOM-F7-019 | owner_explicit | Bad preserved data becomes bad training substrate, multiplying defects through future local models. Data quality = future cognition quality. | PROJECT-LEVEL | -- | Already in CLAUDE.md Rule 13. Reinforced. |
| MAQ-082 | ATOM-F7-020 | owner_consistent_inference | Polished presentation is a force multiplier for both good and bad systems. False confidence from polish magnifies harmful study. | MERGED into MAQ-006 | -- | Reinforces deceptive cleanliness (MAQ-006). |
| MAQ-083 | ATOM-F8-011 | owner_consistent_inference | RED-TEAM TEST: Inject a misleading prior doctrinal box and test whether excerpter starts cutting to fit it. | Section K | -- | See RT-K-003 in Section K. |
| MAQ-084 | MISSED-F1-015 | owner_explicit | "Green box" / "welcome-note" concept: LLM adds explanatory comments within excerpts, like high-school textbook green boxes. | DEFERRED_FEATURE | -- | Save for Phase 3 enrichment enhancement. |
| MAQ-085 | MISSED-F1-032 | owner_explicit | "we need to define as many edge cases as possible, naming them exactly." Named edge case tracking with data collection per case. | NEW | SPEC (process) | Add named-edge-case registry requirement to hardening process. |
| MAQ-086 | MISSED-F1-047 | owner_explicit | "WE SHOULD BUILD A PROPER BOOK DIGESTER, NOT JUST A BOOK EXCERPTER!!!!" Multi-level preservation: full books at top, chapters next, down to fine-grained excerpts. | DEFERRED_FEATURE | -- | Save for architecture v2. Informs multi-level excerpt representation. |
| MAQ-087 | MISSED-F5-012 | owner_explicit | Excerpting must be independent of ANY outside player -- broader than just taxonomy. | CAPTURED (FP-4) | -- | Verify FP-4 covers "any outside player," not just taxonomy. |
| MAQ-088 | F8-NN-009 | owner_explicit | Search, ranking, and presentation must not turn a wrong box into false authority. Presentation-amplified structural bias. | DEFERRED (display/synthesis) | -- | Save for synthesis/UI layer design. |

---

## Section J: DEFERRED (Cross-Engine / Future Capability)

Items that are outside the excerpting engine's current scope. They are recorded here to prevent loss and assigned to their target engine/phase.

| MAQ-ID | Source(s) | Target | Summary |
|--------|-----------|--------|---------|
| DEF-001 | MAQ-057 (ATOM-F5-008, ATOM-CROSS-004) | Cross-engine design | Three-layer proof system: scholar-book witness + authoritative fetched + comparison/alignment layer. |
| DEF-002 | MAQ-060 (ATOM-F6-003, F6-NN-009) | Cross-engine design | Proof-variant significance classification: significant / non-significant / uncertain. Aa/Ab/Ac model. |
| DEF-003 | MAQ-061 (ATOM-F6-004) | Cross-engine analytics | Scholar-to-proof-variant mapping. "Percentage of scholars" per opinion. Data analysis layer. |
| DEF-004 | MAQ-062 (ATOM-F6-005) | Cross-engine proof-layer | Study-friendly chunking for memorization on authoritative fetched proof layer only. |
| DEF-005 | MAQ-024 (MISSED-F1-022, F1-031) | Synthesis/UI | "Linked list" excerpt chaining + "angel on my shoulder" context vision. |
| DEF-006 | MAQ-084 (MISSED-F1-015) | Phase 3 enrichment | "Green box" / "welcome-note" -- LLM-generated explanatory comments within excerpts. |
| DEF-007 | MAQ-086 (MISSED-F1-047) | Architecture v2 | "Book digester" multi-level preservation concept. |
| DEF-008 | META-027 (MISSED-F2-011) | Synthesis/UI | Q&A / challenge feature for repetition. |
| DEF-009 | META-028 (MISSED-F2-012) | Synthesis/UI | Multi-pane study support. |
| DEF-010 | META-029 (MISSED-F2-013) | Source engine | Audio-to-text-to-excerpt pipeline. |
| DEF-011 | MAQ-088 (F8-NN-009) | Synthesis/UI | Presentation-amplified structural bias prevention. |
| DEF-012 | MISSED-F6-FI-001 | Cross-engine design | Owner's 9-point deeper hierarchy for proof handling (flattened in extraction). |
| DEF-013 | MISSED-F7-007 (raw) | Project budget | Concrete cost figures: 50 euros on 5 books. Scale economic modeling. |
| DEF-014 | MISSED-F7-009 (raw) | Infrastructure | 5TB Google Drive for training data storage. |
| DEF-015 | META-023 (MISSED-F2-006) | Taxonomy engine | Library surpassing traditional scholarly organization -- revolutionary restructuring. |
| DEF-016 | ATOM-F3-007, F3-NN-008 | Taxonomy engine | Anti-large-passage-duplication via sub-excerpting (involves taxonomy placement decisions). |
| DEF-017 | ATOM-F3-005 (cross-engine aspect) | Taxonomy engine | Chapter-specific vs full-topic introduction distinction affects taxonomy leaf placement. |
| DEF-018 | ATOM-F6-009 | Cross-engine tests | RED-TEAM: study-friendly chunking applied to scholar-book witness layer (layer boundary test). |

---

## Section K: RED-TEAM TESTS (To Automate as pytest Cases)

All 62 red-team tests from CRITICAL_ATOMS_NONNEGOTIABLES_AND_REDTEAM.md, grouped by batch with related MAQ atoms.

### K.1 -- F3 Red-Team Tests (9 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F3-001 | F3/10_red_team_tests RT-001 | mutation | Remove chapter title from introduction excerpt; test whether "هذا الباب" remains safely interpretable. | MAQ-020 | NEW |
| RT-F3-002 | F3/10_red_team_tests RT-002 | mutation | Start ruling excerpt directly at "لأن" without retained upstream context; evaluate safety. | Ledger #3 (FP-3) | NEW |
| RT-F3-003 | F3/10_red_team_tests RT-003 | mutation | Remove retained lead-in; test whether "عليهما" and "غسلهما" still have safe internal anchor. | Ledger #14 (FP-12) | NEW |
| RT-F3-004 | F3/10_red_team_tests RT-004 | contrast | Keep entire passage merged as one entry vs split candidates; compare function clarity. | MAQ-026 | NEW |
| RT-F3-005 | F3/10_red_team_tests RT-005 | audit | Classify whole passage as introduction-only; inspect what ruling/proof/refutation becomes misplaced. | MAQ-018 | NEW |
| RT-F3-006 | F3/10_red_team_tests RT-006 | simulation | Treat first sentence as full-topic introduction instead of proof-specific chapter introduction. | MAQ-027 | NEW |
| RT-F3-007 | F3/10_red_team_tests RT-007 | stress | Apply forgiving rule too aggressively; verify proof overview and refutation remain wrongly trapped. | MAQ-036 | NEW |
| RT-F3-008 | F3/10_red_team_tests RT-008 | mutation | Isolate proof-overview excerpt at "فهو ..." with no retained anchor; evaluate grounding safety. | MAQ-019 | NEW |
| RT-F3-009 | F3/10_red_team_tests RT-009 | contrast | Compare refutation excerpt with vs without short hukm-return clause. | MAQ-038 | NEW |

### K.2 -- F4 Red-Team Tests (9 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F4-001 | F4/10_red_team_tests RT-001 | contrast | Keep excerpt merged vs split treatment separating disagreement marker from tarjih. | Ledger #5 (FP-8) | NEW |
| RT-F4-002 | F4/10_red_team_tests RT-002 | mutation | Split disagreement marker from tarjih; evaluate clarity improvement. | Ledger #5 (FP-8) | NEW |
| RT-F4-003 | F4/10_red_team_tests RT-003 | simulation | Simulate disagreement marker immediately followed by opinion list; test cluster coherence. | MAQ-039 | NEW |
| RT-F4-004 | F4/10_red_team_tests RT-004 | contrast | Treat opening "و" as always externally dependent vs intelligent local-continuation reading. | Ledger #3 (FP-3) | NEW |
| RT-F4-005 | F4/10_red_team_tests RT-005 | audit | Use surrounding context in engineering layer only; verify owner verdict on as-given excerpt unchanged. | MAQ-001 | NEW |
| RT-F4-006 | F4/10_red_team_tests RT-006 | mutation | Classify whole excerpt as pure disagreement; inspect attribution loss. | MAQ-053 | NEW |
| RT-F4-007 | F4/10_red_team_tests RT-007 | mutation | Classify whole excerpt as pure tarjih; inspect disagreement signal loss. | MAQ-053 | NEW |
| RT-F4-008 | F4/10_red_team_tests RT-008 | stress | Strip explicit completion from tarjih candidate; test excerpt viability as attributed preference. | MAQ-054 | NEW |
| RT-F4-009 | F4/10_red_team_tests RT-009 | audit | Run question-cluster analysis first, then surface segmentation only; compare excerpt maps. | MAQ-040 | NEW |

### K.3 -- F5 Red-Team Tests (9 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F5-001 | F5/11_red_team_tests RT-001 | mutation | Remove note entirely; present explanation starting at "المعنى الإجمالي:". | Ledger #1 (EE-1) | NEW |
| RT-F5-002 | F5/11_red_team_tests RT-002 | contrast | Compare generated summary note vs source-preserving context block with actual hadith material. | MAQ-002 | NEW |
| RT-F5-003 | F5/11_red_team_tests RT-003 | stress | Split explanation from explained; inject two similar hadith variants; check correct pairing. | MAQ-056 | NEW |
| RT-F5-004 | F5/11_red_team_tests RT-004 | contrast | Compare studying from book-proof alone vs fetched-proof alone vs both layers linked. | Ledger #10 (FP-7) | NEW |
| RT-F5-005 | F5/11_red_team_tests RT-005 | simulation | Scholar explanation presupposes one grading while fetched proof defaults to another. | MAQ-056 | NEW |
| RT-F5-006 | F5/11_red_team_tests RT-006 | simulation | Scholar methodology where topic, proof, explanation are deeply interwoven; test separability. | MAQ-069 | NEW |
| RT-F5-007 | F5/11_red_team_tests RT-007 | contrast | For broken pair: default-visible note vs collapsible note. | MAQ-028 | NEW |
| RT-F5-008 | F5/11_red_team_tests RT-008 | audit | Audit whether fetched proof is explicitly linked to the exact wording/version the scholar assumes. | MAQ-057 (DEF-001) | NEW |
| RT-F5-009 | F5/11_red_team_tests RT-009 | stress | Make note rich enough to feel readable while leaving explained/explanation split untouched. | MAQ-052 | NEW |

### K.4 -- F6 Red-Team Tests (9 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F6-001 | F6/13_red_team_tests RT-001 | contrast | Compare memorization from scholar-book proof vs authoritative fetched proof. | Ledger #10 (FP-7) | NEW |
| RT-F6-002 | F6/13_red_team_tests RT-002 | contrast | Compare proof variants: non-significant drift vs material meaning change. | MAQ-060 (DEF-002) | NEW |
| RT-F6-003 | F6/13_red_team_tests RT-003 | audit | Test scholar-explanation-to-proof-version linkage correctness. | MAQ-057 (DEF-001) | NEW |
| RT-F6-004 | F6/13_red_team_tests RT-004 | mutation | Apply study-friendly chunking to scholar-book witness; check layer boundary loss. | MAQ-062 (DEF-004) | NEW |
| RT-F6-005 | F6/13_red_team_tests RT-005 | simulation | Introduce new scholar methodology with different interleaving pattern. | Ledger #11 (FP-6) | NEW |
| RT-F6-006 | F6/13_red_team_tests RT-006 | stress | Genuinely unclear variant significance; test uncertainty reporting. | Ledger #11 (FP-6) | NEW |
| RT-F6-007 | F6/13_red_team_tests RT-007 | mutation | Present help layer without clear separation from original source text. | MAQ-003 | NEW |
| RT-F6-008 | F6/13_red_team_tests RT-008 | audit | Remove authoritative fetched proof; test if system still pushes memorization from scholar-book. | Ledger #10 (FP-7) | NEW |
| RT-F6-009 | F6/13_red_team_tests RT-009 | stress | Large-scale cross-source analysis; check proof-layer collapse risk. | MAQ-061 (DEF-003) | NEW |

### K.5 -- F7 Red-Team Tests (16 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F7-001 | F7/09_red_team_tests RT-001 | injection | Inject single-character/diacritic corruption into Arabic text; verify loud failure. | Ledger #12 (FP-5) | NEW |
| RT-F7-002 | F7/09_red_team_tests RT-002 | mutation | Force alternative split/merge decisions; check meaning, anchoring, honesty preservation. | MAQ-006, MAQ-029 | NEW |
| RT-F7-003 | F7/09_red_team_tests RT-003 | audit | Pick random study-facing units; reconstruct full provenance from stored lineage alone. | MAQ-063 | NEW |
| RT-F7-004 | F7/09_red_team_tests RT-004 | contrast | Same quoted text playing different roles in different sources; verify current-source classification. | Ledger #17 (FP-14) | NEW |
| RT-F7-005 | F7/09_red_team_tests RT-005 | contrast | Near-neighbor branches and secondary mentions; test true-topic vs mere-mention distinction. | MAQ-047 | NEW |
| RT-F7-006 | F7/09_red_team_tests RT-006 | simulation | Hide proof link, example link, and ranking signal; observe downstream misleadingness. | MAQ-006 | NEW |
| RT-F7-007 | F7/09_red_team_tests RT-007 | audit | Audit all study-facing views for suppressed confidence, uncertainty, missing lineage. | MAQ-017 | NEW |
| RT-F7-008 | F7/09_red_team_tests RT-008 | stress | Build happy-path test suites that pass despite incorrect edge rule; verify harness catches hollowness. | MAQ-007 | NEW |
| RT-F7-009 | F7/09_red_team_tests RT-009 | audit | Pick core contract; enumerate downstream consequences of one field/assumption change. | MAQ-011 | NEW |
| RT-F7-010 | F7/09_red_team_tests RT-010 | stress | Corpus-scale cost/latency projections with worst-case assumptions. | MAQ-078 | NEW |
| RT-F7-011 | F7/09_red_team_tests RT-011 | simulation | End-to-end disaster recovery drill from backups/exports only. | MAQ-079 | NEW |
| RT-F7-012 | F7/09_red_team_tests RT-012 | audit | Sample training-candidate dataset; trace lineage safety for future local-model use. | MAQ-080 | NEW |
| RT-F7-013 | F7/09_red_team_tests RT-013 | audit | Red-team the build environment: missing tools, hooks, weak role definition, unclaimed zones. | PROJECT-LEVEL | NEW |
| RT-F7-014 | F7/09_red_team_tests RT-014 | contrast | Same footnote-heavy source under crude policies (always glue vs always split); compare outcomes. | MAQ-071 | NEW |
| RT-F7-015 | F7/09_red_team_tests RT-015 | simulation | Force pipeline onto weaker fallback models for ambiguous cases; compare outputs. | Ledger #11 (FP-6) | NEW |
| RT-F7-016 | F7/09_red_team_tests RT-016 | mutation | Introduce defect, let it survive into artifacts, fix it, test contamination enumeration. | MAQ-005 | NEW |

### K.6 -- F8 Red-Team Tests (10 tests)

| RT-ID | Source | Type | Test Description | Related MAQ | Status |
|-------|--------|------|-----------------|-------------|--------|
| RT-F8-001 | F8/10_red_team_tests RT-001 | contrast | Same source under correct/under/over-granulated trees; compare excerpt invariance. | Ledger #8 (FP-4) | NEW |
| RT-F8-002 | F8/10_red_team_tests RT-002 | contrast | Process passage with and without prior topic guidance; compare boundaries. | Ledger #8 (FP-4) | NEW |
| RT-F8-003 | F8/10_red_team_tests RT-003 | injection | Inject misleading prior doctrinal box; test whether excerpter cuts to fit it. | Ledger #8 (FP-4) | NEW |
| RT-F8-004 | F8/10_red_team_tests RT-004 | stress | Correct excerpt set in over- vs under-granulated tree; compare user confusion. | MAQ-043 | NEW |
| RT-F8-005 | F8/10_red_team_tests RT-005 | contrast | Visible wrong leaf placement vs silent excerpt corruption; same source and topic. | MAQ-009 | NEW |
| RT-F8-006 | F8/10_red_team_tests RT-006 | audit | Instrument placement validation to prove tree-fit scores never suppress/reshape excerpts. | MAQ-010 | NEW |
| RT-F8-007 | F8/10_red_team_tests RT-007 | simulation | Freeze excerpts, redesign tree, verify excerpt identity unchanged. | MAQ-041 | NEW |
| RT-F8-008 | F8/10_red_team_tests RT-008 | stress | Surface deliberately misboxed excerpt through search/ranking; test authoritative feel. | MAQ-088 (DEF-011) | NEW |
| RT-F8-009 | F8/10_red_team_tests RT-009 | audit | Boundary consistency across family of similar passages from different books. | MAQ-030 | NEW |
| RT-F8-010 | F8/10_red_team_tests RT-010 | simulation | Delayed discovery: compare source text against long-used excerpt set post-memorization. | Ledger #12 (FP-5) | NEW |

---

## Cross-Reference Index

### Extraction Atom -> MAQ Mapping

| Extraction Atom | MAQ-ID | Section |
|-----------------|--------|---------|
| ATOM-F3-001 | MAQ-018 | E |
| ATOM-F3-002 | MAQ-026 | F |
| ATOM-F3-003 | MAQ-019 | E |
| ATOM-F3-004 | MAQ-020 | E |
| ATOM-F3-005 | MAQ-027 | F |
| ATOM-F3-006 | MAQ-036 | G |
| ATOM-F3-007 | MAQ-037 | G |
| ATOM-F3-008 | MAQ-038 | G |
| ATOM-F3-009 | MAQ-021 | E |
| ATOM-F3-010 | RT-F3-002 (test) | K |
| ATOM-F3-011 | RT-F3-005 (test) | K |
| ATOM-F3-012 | MAQ-074 | I |
| ATOM-F4-001 | Section B (FP-8) | B |
| ATOM-F4-002 | MAQ-053 | H |
| ATOM-F4-003 | MAQ-054 | H |
| ATOM-F4-004 | Section B (FP-3) | B |
| ATOM-F4-005 | MAQ-039 | G |
| ATOM-F4-006 | MAQ-040 | G |
| ATOM-F4-007 | MAQ-001 | D |
| ATOM-F4-008 | RT-F4-006/007 (test) | K |
| ATOM-F5-001 | Section B (FP-1) | B |
| ATOM-F5-002 | MAQ-002 | D |
| ATOM-F5-003 | Section B (FP-1) | B |
| ATOM-F5-004 | Section B (FP-7) | B |
| ATOM-F5-005 | Section B (FP-6) | B |
| ATOM-F5-006 | MAQ-056 | H |
| ATOM-F5-007 | MAQ-028 | F |
| ATOM-F5-008 | MAQ-057 -> DEF-001 | J |
| ATOM-F5-009 | Section B (FP-6) | B |
| ATOM-F5-010 | MAQ-075 | I |
| ATOM-F6-001 | MAQ-058 | H |
| ATOM-F6-002 | MAQ-059 | H |
| ATOM-F6-003 | MAQ-060 -> DEF-002 | J |
| ATOM-F6-004 | MAQ-061 -> DEF-003 | J |
| ATOM-F6-005 | MAQ-062 -> DEF-004 | J |
| ATOM-F6-006 | Section B (FP-7) | B |
| ATOM-F6-007 | Section B (FP-6) | B |
| ATOM-F6-008 | MAQ-003 | D |
| ATOM-F6-009 | RT-F6-004 (test) | K |
| ATOM-F7-001 | Section B (FP-5) | B |
| ATOM-F7-002 | Section B (FP-5) | B |
| ATOM-F7-003 | MAQ-004 | D |
| ATOM-F7-004 | MAQ-063 | H |
| ATOM-F7-005 | MAQ-005 | D |
| ATOM-F7-006 | MAQ-017 | D |
| ATOM-F7-007 | MAQ-029 | F |
| ATOM-F7-008 | Section B (FP-14) | B |
| ATOM-F7-009 | MAQ-006 | D |
| ATOM-F7-010 | MAQ-007 | D |
| ATOM-F7-011 | MAQ-078 | I |
| ATOM-F7-012 | MAQ-079 | I |
| ATOM-F7-013 | MAQ-080 | I |
| ATOM-F7-014 | MAQ-064 (merged FP-5) | H |
| ATOM-F7-015 | MAQ-008 (merged MAQ-006) | D |
| ATOM-F7-016 | RT-F7-001 (test) | K |
| ATOM-F7-017 | RT-F7-002 (test) | K |
| ATOM-F7-018 | MAQ-011 | D |
| ATOM-F7-019 | MAQ-081 | I |
| ATOM-F7-020 | MAQ-082 (merged MAQ-006) | I |
| ATOM-F8-001 | Section B (FP-4) | B |
| ATOM-F8-002 | Section B (FP-4) | B |
| ATOM-F8-003 | Section B (FP-4/FP-9) | B |
| ATOM-F8-004 | Section B (FP-4) | B |
| ATOM-F8-005 | MAQ-076 | I |
| ATOM-F8-006 | MAQ-010 | D |
| ATOM-F8-007 | MAQ-041 | G |
| ATOM-F8-008 | Section B (FP-4) | B |
| ATOM-F8-009 | MAQ-009 | D |
| ATOM-F8-010 | RT-F8-001 (test) | K |
| ATOM-F8-011 | RT-F8-003 (test) | K |
| ATOM-F8-012 | MAQ-030 | F |
| ATOM-F8-013 | MAQ-042 | G |
| ATOM-F8-014 | MAQ-077 | I |
| ATOM-F8-015 | MAQ-043 | G |
| ATOM-CROSS-001 | MAQ-021 | E |
| ATOM-CROSS-002 | Section B (FP-6) | B |
| ATOM-CROSS-003 | Section B (FP-3) | B |
| ATOM-CROSS-004 | MAQ-057 -> DEF-001 | J |
| ATOM-CROSS-005 | Section B (FP-5) | B |
| ATOM-CROSS-006 | MAQ-022 (merged MAQ-018) | E |
| ATOM-CROSS-007 | MAQ-006 | D |

### NN -> MAQ Mapping (Non-Negotiables from CRITICAL_ATOMS)

All 63 nonnegotiables are accounted for. Each maps to either an existing FP (Section B verification), a MAQ entry (Sections D-I), or both.

| Collection | NN Count | Mapped to FP (verify) | Mapped to MAQ (new work) |
|------------|----------|-----------------------|--------------------------|
| F3 | 10 | 1 (NN-003 -> FP-3) | 9 |
| F4 | 9 | 2 (NN-001 -> FP-8, NN-004 -> FP-3) | 7 |
| F5 | 10 | 5 (NN-002/003/004/005/009) | 5 |
| F6 | 10 | 5 (NN-001/003/005/007/002) | 5 |
| F7 | 14 | 2 (NG-001/006) | 12 |
| F8 | 10 | 5 (NN-001/002/003/005/007) | 5 |
| **Total** | **63** | **20** | **43** |

---

## Processing Priority

Based on batch ordering from THEMATIC_BATCHES.md (highest-impact first) and remaining new-work count:

| Priority | Section | Batch | New MAQ Count | Prompt-Affecting |
|----------|---------|-------|---------------|------------------|
| 1 | D | Safety & Integrity | 14 (after merges) | 4 |
| 2 | E | Self-Containment | 6 | 5 |
| 3 | F | Boundary & Grouping | 8 | 6 |
| 4 | G | Granularity | 15 | 11 |
| 5 | H | Tarjih/Khilaf/Proof/Evidence | 14 (after merges + deferrals) | 8 |
| 6 | I | Other | 10 (after merges) | 2 |

### Prompt-Affecting Atoms (must modify Phase 2 LLM prompts)

These MAQ entries directly affect how the LLM behaves during excerpting. They are the highest-priority for the hardening operation:

MAQ-018, MAQ-019, MAQ-020, MAQ-021, MAQ-026, MAQ-027, MAQ-032, MAQ-033, MAQ-035, MAQ-036, MAQ-038, MAQ-039, MAQ-040, MAQ-045, MAQ-046, MAQ-047, MAQ-048, MAQ-049, MAQ-050, MAQ-053, MAQ-054, MAQ-056, MAQ-069, MAQ-071

**Total: 24 prompt-affecting atoms.**

---

---

## Section L: G/SC SERIES INTAKE (Session 5, 2026-04-07)

> 7 bundles (G1-G4, SC1-SC3) ingested via 7 parallel extraction agents.
> 157 raw atoms extracted from 143 files (7,500 lines).
> Ground truth validation: PASS (60/60 pre-extracted atoms confirmed).
> Arabic degradation: 0 pipeline-introduced; 4 pre-existing source OCR artifacts.
> Full per-atom reports: `engines/excerpting/reference/G_SC_GROUND_TRUTH_PREEXTRACTION.md` + agent output files.

### L.1 — Batch Summary

| Batch | Question Topic | Raw Atoms | FP Candidates | Prompt-Affecting | DEFERRED | Duplicates of F-series |
|-------|---------------|-----------|---------------|------------------|----------|----------------------|
| G1 | Added benefit & excerpting objectivity | 18 | 1 (G1-004: OBJECTIVE rule) | 7 | 0 | G1-004 generalizes FP-4 |
| G2 | Hadith chunking & proof relationships | 24 | 4 (G2-005, G2-012, G2-018, G2-019) | 2 | 6 | G2-005 extends EE-1; G2-019 extends FP-4 |
| G3 | Multi-function excerpts & numbering | 18 | 3 (G3-015, G3-016, G3-017) | 5 | 0 | G3-005 reinforces FP-4; G3-012 extends EE-1 |
| G4 | Conditions excerpting & granularity | 20 | 0 | 8 | 3 | G4-004/005 strengthen FP-6 |
| SC1 | Teaching units & author flow | 32 | 0 (SC1-010 is SPEC-level teaching unit def) | 5 | 3 | SC1-007 strengthens FP-2; SC1-017 extends FP-10 |
| SC2 | Quality standards & explanation linkage | 20 | 1 (SC2-010: MAX EFFORT quality) | 4 | 2 | SC2-001 extends EE-1; SC2-002 extends FP-7 |
| SC3 | Zero-context & security gates | 25 | 1 (SC3-024: readability ≠ safety) | 5 | 0 | SC3-001 duplicates FP-19; SC3-005 extends C-SC-2 |
| **TOTAL** | | **157** | **10** | **36** | **14** | |

### L.2 — Cross-Bundle FP Candidates (require multi-coworker validation)

| # | Candidate | Source Bundles | Strengthens/Extends |
|---|-----------|---------------|---------------------|
| FP-C1 | Excerpting is OBJECTIVE — no outside factors | G1, G3 | Generalizes FP-4 |
| FP-C2 | Lost-potential principle (cross-topic placement) | G2 | New |
| FP-C3 | Zero-ambiguity for identifiers/labels | G2 | New |
| FP-C4 | Anti-hardening of statistical tendencies | G3 | New |
| FP-C5 | Excerpt = teaching unit (vocabulary shift) | SC1 | New (transformative) |
| FP-C6 | Quality = MAX EFFORT, not good enough | SC2 | Strengthens FP-5/FP-20 |
| FP-C7 | Local readability ≠ safe understanding | SC3 | New |
| FP-C8 | Post-excerpting reassembly verification gate | SC3 | New pipeline gate |
| FP-C9 | Author flow preservation (NEVER lost) | SC1 | New |
| FP-C10 | Anti-manhunt principle (self-containment operational) | SC1, SC2, SC3 | Strengthens C-SC rules |

### L.3 — Disposition Breakdown

| Disposition | Count | Notes |
|-------------|-------|-------|
| PROMPT | 36 | **BLOCKED by §4.11 refactor gate** (GROUP_SYSTEM_PROMPT at 1484/1500) |
| SPEC | 62 | Can proceed to SPEC §6 formalization |
| FP | 10 | Require multi-coworker validation before adoption |
| META | 24 | Documentation, vocabulary, study methodology |
| DEFERRED | 14 | Cross-engine or future feature work |
| Duplicate/overlap | 11 | Extend or strengthen existing F-series atoms |

### L.4 — Status

All 157 atoms are **PRELIMINARY (0/3 coworkers)**. Session 5 is CC-only extraction.
Next step: BCV (Session 6) + coworker validation before any atoms advance to IMPLEMENTED.

MAQ-ID assignment deferred to BCV session (Session 6) after deduplication pass across G/SC atoms themselves.

---

*End of Merged Atom Queue. Every idea from F1-F8 + G1-G4 + SC1-SC3 is accounted for. F-series: 250 ideas (88 actionable). G/SC-series: 157 raw atoms (pending dedup + BCV). Zero silent drops.*
