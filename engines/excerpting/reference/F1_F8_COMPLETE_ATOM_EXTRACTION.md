# F3-F8 Complete Atom Extraction

**Generated:** 2026-04-04
**Source:** chatgpt_f3_collection through chatgpt_f8_collection (excluding source_artifacts/)
**Purpose:** Exhaustive extraction of every actionable atom from owner feedback collections F3-F8 for excerpting engine hardening.

**Legend:**
- **Authority:** `owner_explicit` | `owner_consistent_inference` | `model_only`
- **Already in SPEC?:** References to FP-1 through FP-18 in SPEC.md section 1.1b
- **Impact surface:** SPEC / prompt / contracts / tests / Phase 1 / Phase 2 / Phase 3 / cross-engine / display-only / deferred-feature

---

## F3 — Multi-Function Chapter-Start Passage (باب المسح على الخفين)

### ATOM-F3-001
- **Source:** F3/01_questionnaire_answer.md, F3/04_decision_ladder.jsonl DL-001/DL-002
- **Authority:** owner_explicit
- **Content:** Surface chapter-intro language must not be treated as decisive for function classification; a passage that looks introductory may actually carry ruling, proof-overview, and refutation content.
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Not directly. FP-3 covers linking-word intelligence but not surface-function misread.

### ATOM-F3-002
- **Source:** F3/01_questionnaire_answer.md, F3/09_nonnegotiables.jsonl NN-002
- **Authority:** owner_explicit
- **Content:** A multi-function passage (introduction + ruling + proof-overview + refutation) must not be kept merged as one entry when all functions are substantively present.
- **Impact surface:** prompt / Phase 2 / SPEC
- **Already in SPEC?:** Partially. EE-1 (FP-1) addresses explained/explanation unity but not multi-function passages at chapter starts.

### ATOM-F3-003
- **Source:** F3/04_decision_ladder.jsonl DL-005, F3/06_linking_dependencies.jsonl LD-002
- **Authority:** owner_explicit
- **Content:** Small, strongly linked carryover material (e.g., a chapter-intro sentence) may remain attached inside a sub-excerpt when removing it would expose unsafe starts at causal continuations like "لأن".
- **Impact surface:** prompt / Phase 2 / SPEC
- **Already in SPEC?:** Partially in FP-3 (linking-word intelligence) but the forgiving-retention logic is not explicit.

### ATOM-F3-004
- **Source:** F3/06_linking_dependencies.jsonl LD-001, F3/09_nonnegotiables.jsonl NN-004
- **Authority:** owner_explicit
- **Content:** Chapter titles must be retained in excerpts when demonstrative references like "هذا الباب" depend on them; title retention is not always optional or always mandatory -- it is asymmetric per excerpt.
- **Impact surface:** prompt / Phase 2 / contracts
- **Already in SPEC?:** Not explicitly. The SPEC does not address title-retention asymmetry.

### ATOM-F3-005
- **Source:** F3/07_function_placement.jsonl FP-002, F3/09_nonnegotiables.jsonl NN-005
- **Authority:** owner_explicit
- **Content:** A chapter-specific introduction must be distinguished from a full-topic introduction; confusing the two creates source-scope mismatch risk where the reader inherits a distorted view of the topic.
- **Impact surface:** Phase 2 / taxonomy / cross-engine
- **Already in SPEC?:** No.

### ATOM-F3-006
- **Source:** F3/08_granularity_analysis.jsonl GA-003, GA-004
- **Authority:** owner_explicit
- **Content:** The forgiving rule (allowing negligible carryover) has a limit: once the overlap between functions reaches roughly equal proportions (e.g., 33/33/33), the forgiving rule no longer applies and real sub-excerpting must begin.
- **Impact surface:** prompt / Phase 2 / SPEC
- **Already in SPEC?:** Partially covered by MV-1 (minimum viability merge) but the quantitative threshold is not stated.

### ATOM-F3-007
- **Source:** F3/09_nonnegotiables.jsonl NN-008
- **Authority:** owner_explicit
- **Content:** Duplicating a whole large merged passage across multiple taxonomy leaves is not acceptable when careful sub-excerpting into function-specific excerpts is available.
- **Impact surface:** Phase 2 / taxonomy / cross-engine
- **Already in SPEC?:** No.

### ATOM-F3-008
- **Source:** F3/09_nonnegotiables.jsonl NN-009, F3/08_granularity_analysis.jsonl GA-005
- **Authority:** owner_explicit
- **Content:** When a short hukm-return phrase appears inside a refutation segment, it may remain there, but the hukm must also be represented in the hukm-focused excerpt to prevent knowledge scattering.
- **Impact surface:** Phase 2 / prompt
- **Already in SPEC?:** No.

### ATOM-F3-009
- **Source:** F3/09_nonnegotiables.jsonl NN-010, F3/14_hard_judgment.md
- **Authority:** owner_consistent_inference
- **Content:** Function classification, split decisions, and title retention must not be automated by one blunt heuristic; dependency analysis must precede all split/retain decisions.
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Partially in FP-3 and FP-6 (rules + intelligence) but not operationalized as a pre-split dependency check.

### ATOM-F3-010
- **Source:** F3/10_red_team_tests.jsonl RT-002
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Start a ruling excerpt directly at "لأن" with no retained upstream context and evaluate whether the excerpt remains safe.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F3-011
- **Source:** F3/10_red_team_tests.jsonl RT-005
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Classify the whole passage as introduction-only and verify what ruling/proof/refutation information becomes misplaced.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F3-012
- **Source:** F3/13_open_questions.jsonl OQ-002
- **Authority:** owner_explicit
- **Content:** OPEN QUESTION: How should the system mark a chapter-specific introduction so it is not mistaken for a full-topic introduction when surfaced at the topic leaf?
- **Impact surface:** deferred-feature / cross-engine
- **Already in SPEC?:** No.

---

## F4 — Khilaf-Tarjih Fusion (واختلف العلماء)

### ATOM-F4-001
- **Source:** F4/01_questionnaire_answer.md, F4/04_decision_ladder.jsonl DL-003/DL-004
- **Authority:** owner_explicit
- **Content:** An unbiased disagreement marker (واختلف العلماء ... على أقوال) and a scholar's tarjih (وأصحها ما ذهب إليه الجمهور) are distinct scholarly functions answering different questions and must not be fused into one excerpt.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Yes, captured in FP-8 (Khilaf-tarjih distinction).

### ATOM-F4-002
- **Source:** F4/01_questionnaire_answer.md, F4/09_nonnegotiables.jsonl NN-003
- **Authority:** owner_explicit
- **Content:** Tarjih is attribution-critical: it records what a specific scholar prefers. Clipping, flattening, or losing the tarjih is not a minor formatting issue -- it changes what the scholar is being recorded as saying.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Partially in FP-8 but the attribution-critical nature is not emphasized.

### ATOM-F4-003
- **Source:** F4/09_nonnegotiables.jsonl NN-005, F4/07_question_cluster_analysis.jsonl QC-004
- **Authority:** owner_explicit
- **Content:** A clipped tarjih lead-in (e.g., "وأصحها ما ذهب إليه الجمهور" without the completion of the preferred view) must not be accepted as a standalone excerpt -- the tarjih must be completed.
- **Impact surface:** prompt / Phase 2 / tests
- **Already in SPEC?:** No.

### ATOM-F4-004
- **Source:** F4/09_nonnegotiables.jsonl NN-004, F4/08_context_dependency_analysis.jsonl CD-001
- **Authority:** owner_explicit
- **Content:** Not every opening "و" indicates external dependency; some are local continuations. The system must diagnose intelligently rather than apply a rigid rule to all opening conjunctions.
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Yes, captured in FP-3 (Linking-word intelligence).

### ATOM-F4-005
- **Source:** F4/07_question_cluster_analysis.jsonl QC-002, F4/09_nonnegotiables.jsonl NN-006
- **Authority:** owner_explicit
- **Content:** A disagreement marker and a full unbiased opinion listing answer the same broader question and are too tightly linked to split; they should remain together as one disagreement-structure excerpt.
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Not explicitly.

### ATOM-F4-006
- **Source:** F4/04_decision_ladder.jsonl DL-008, F4/10_red_team_tests.jsonl RT-009
- **Authority:** owner_explicit
- **Content:** Question-cluster reasoning ("what question is each segment answering?") should be used as a methodology for determining split/keep decisions, not just surface segmentation.
- **Impact surface:** prompt / Phase 2 / SPEC
- **Already in SPEC?:** No.

### ATOM-F4-007
- **Source:** F4/09_nonnegotiables.jsonl NN-002, NN-009
- **Authority:** owner_explicit
- **Content:** Surrounding context may be used diagnostically and for engineering reconstruction but must never silently rescue the owner-facing verdict on a defective excerpt.
- **Impact surface:** SPEC / Phase 3 / prompt
- **Already in SPEC?:** Partially in FP-2 (context resolution hierarchy) but the prohibition on silent rescue is not stated.

### ATOM-F4-008
- **Source:** F4/10_red_team_tests.jsonl RT-006, RT-007
- **Authority:** model_only
- **Content:** RED-TEAM TEST: Classify the whole fused segment as pure disagreement material OR as pure tarjih and verify what attribution or disagreement signal is lost in each case.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

---

## F5 — Orphaned Explanation and Note Compensation

### ATOM-F5-001
- **Source:** F5/01_questionnaire_answer.md, F5/02_case_dossier.md
- **Authority:** owner_explicit
- **Content:** An explanation displayed without its explained text (e.g., a المعنى الإجمالي starting at the explanation with no hadith present) is an orphaned explanation; generated summary notes compensate for a structural defect, not a display preference.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Yes, captured in FP-1 (Explained-explanation unity, EE-1).

### ATOM-F5-002
- **Source:** F5/01_questionnaire_answer.md, F5/10_nonnegotiables.jsonl NN-001
- **Authority:** owner_explicit
- **Content:** Generated summary notes must not silently replace source-preserving context where source integrity materially matters; notes are secondary aids, not primary context mechanisms.
- **Impact surface:** SPEC / Phase 3 / display-only
- **Already in SPEC?:** Partially in FP-2 (context resolution hierarchy) but the prohibition on note-as-replacement is not stated.

### ATOM-F5-003
- **Source:** F5/02_case_dossier.md, F5/10_nonnegotiables.jsonl NN-002
- **Authority:** owner_explicit
- **Content:** Explanation and explained text must not be blindly separated; in hadith-heavy Islamic sciences, they are often too tightly linked due to wording variants, route variants, and grading sensitivity.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Yes, core of FP-1. The variant/grading sensitivity detail is not in SPEC.

### ATOM-F5-004
- **Source:** F5/08_proof_integrity_layers.jsonl PI-001/PI-002
- **Authority:** owner_explicit
- **Content:** Book-preserved proofs and authoritatively fetched proofs are both necessary layers; neither replaces the other. Book proofs preserve how the scholar handled the proof; fetched proofs provide confirmed wording for memorization.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** Yes, captured in FP-7 (Fetched proof vs book-preserved proof).

### ATOM-F5-005
- **Source:** F5/09_methodology_risk.jsonl MR-003/MR-004, F5/10_nonnegotiables.jsonl NN-005
- **Authority:** owner_explicit
- **Content:** Not all scholar methodologies fit prewritten rules; unseen patterns will appear. The system must have uncertainty gates and escalation paths for cases where rules do not cover the structure.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Yes, captured in FP-6 (Rules + intelligence).

### ATOM-F5-006
- **Source:** F5/07_explained_explanation_analysis.jsonl EE-002, F5/09_methodology_risk.jsonl MR-001
- **Authority:** owner_explicit
- **Content:** Hadith variant risk: scholars may explain different hadith wordings or routes while appearing to discuss the same proof. Blind separation can pair an explanation with the wrong proof instance.
- **Impact surface:** cross-engine / deferred-feature / SPEC
- **Already in SPEC?:** Not explicitly; FP-7 mentions the two layers but not the variant-mismatch risk.

### ATOM-F5-007
- **Source:** F5/10_nonnegotiables.jsonl NN-006
- **Authority:** owner_explicit
- **Content:** The note question must not cap the deeper diagnosis: when a pair is structurally malformed (explanation orphaned from its explained text), the note-visibility choice is a surface symptom, not the real issue.
- **Impact surface:** SPEC / Phase 3
- **Already in SPEC?:** No.

### ATOM-F5-008
- **Source:** F5/08_proof_integrity_layers.jsonl PI-003/PI-004
- **Authority:** owner_consistent_inference
- **Content:** An alignment layer is needed to link book-preserved proof wording to authoritative fetched proof wording and record whether they are exact matches, close variants, or materially different.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** No.

### ATOM-F5-009
- **Source:** F5/10_nonnegotiables.jsonl NN-009, F5/09_methodology_risk.jsonl MR-004
- **Authority:** owner_explicit
- **Content:** When the system cannot determine methodology fit with high certainty, it must not proceed with confident automated separation -- it must escalate via uncertainty gates.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Captured in FP-6 but the "do not proceed" directive is sharper here.

### ATOM-F5-010
- **Source:** F5/14_open_questions.jsonl OQ-001
- **Authority:** owner_explicit
- **Content:** OPEN QUESTION: Under what strict metadata and linkage conditions can explanation and explained text be safely separated in hadith-heavy materials?
- **Impact surface:** deferred-feature / cross-engine
- **Already in SPEC?:** No.

---

## F6 — Scholar-Book Proof Witness vs Memorization Source

### ATOM-F6-001
- **Source:** F6/01_questionnaire_answer.md, F6/04_decision_ladder.jsonl DL-001/DL-003
- **Authority:** owner_explicit
- **Content:** A proof as found in a science book is a scholar-book proof witness, not the final memorization source; the owner would not memorize hadith directly from this layer.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** Partially in FP-7 but the "not a memorization source" framing is not stated.

### ATOM-F6-002
- **Source:** F6/12_nonnegotiables.jsonl NN-002, F6/10_text_preservation_vs_study_structuring.jsonl TP-001
- **Authority:** owner_explicit
- **Content:** The original author's wording in the scholar-book layer must never be mutated for study convenience; help must sit beside the source as a parallel layer, not overwrite it.
- **Impact surface:** SPEC / cross-engine
- **Already in SPEC?:** Partially implied by primary-text immutability rules but not stated as a study-layer principle.

### ATOM-F6-003
- **Source:** F6/08_variant_difference_policy.jsonl VD-001/VD-002, F6/12_nonnegotiables.jsonl NN-009
- **Authority:** owner_explicit
- **Content:** Wording differences between proof variants must be classified as significant (affects meaning/ruling) or non-significant (does not change meaning); uncertain cases must be explicitly flagged as uncertain, not forced into either category.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** No.

### ATOM-F6-004
- **Source:** F6/11_data_analysis_opportunities.jsonl DA-001/DA-003
- **Authority:** owner_explicit
- **Content:** The library should map which scholars used which proof variants and show when wording differences correlate with different conclusions; this is a core unprecedented analytical advantage.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** No.

### ATOM-F6-005
- **Source:** F6/10_text_preservation_vs_study_structuring.jsonl TP-002, F6/09_memorization_policy.jsonl MP-005
- **Authority:** owner_explicit
- **Content:** Study-friendly chunking for memorization belongs to the authoritative fetched proof layer, not to the scholar-book witness layer.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** No.

### ATOM-F6-006
- **Source:** F6/12_nonnegotiables.jsonl NN-005
- **Authority:** owner_explicit
- **Content:** Scholar-book witness and authoritative fetched proof must not be collapsed into one undifferentiated proof layer; they serve different roles (witness vs certainty).
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** Yes, core of FP-7.

### ATOM-F6-007
- **Source:** F6/12_nonnegotiables.jsonl NN-007
- **Authority:** owner_explicit
- **Content:** Hard rules cannot cover all future scholarly methodologies; the system needs uncertainty gates and intelligent diagnosis, not only fixed rules.
- **Impact surface:** SPEC / prompt
- **Already in SPEC?:** Yes, captured in FP-6.

### ATOM-F6-008
- **Source:** F6/12_nonnegotiables.jsonl NN-010
- **Authority:** owner_explicit
- **Content:** Secondary help layers (comparisons, summaries, chunking) must never silently replace the preserved source layer.
- **Impact surface:** SPEC / cross-engine
- **Already in SPEC?:** No explicit prohibition.

### ATOM-F6-009
- **Source:** F6/13_red_team_tests.jsonl RT-004
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Apply study-friendly chunking directly to the scholar-book witness text and verify whether the layer boundary is lost.
- **Impact surface:** tests / cross-engine
- **Already in SPEC?:** No specific test.

---

## F7 — Trust Collapse and Failure Taxonomy

### ATOM-F7-001
- **Source:** F7/01_questionnaire_answer.md
- **Authority:** owner_explicit
- **Content:** One corrupted excerpt is enough to put all knowledge from the library in question because the reader cannot know where the corruption stops; knowledge corruption is the worst failure.
- **Impact surface:** SPEC
- **Already in SPEC?:** Yes, captured in FP-5 (Knowledge corruption is the worst failure).

### ATOM-F7-002
- **Source:** F7/01_questionnaire_answer.md, F7/02_failure_dossier.md
- **Authority:** owner_explicit
- **Content:** Silent errors are worse than loud ones because they are discovered only after trust, memorization, teaching, or practice have already been built on them.
- **Impact surface:** SPEC
- **Already in SPEC?:** Yes, captured in FP-5.

### ATOM-F7-003
- **Source:** F7/02_failure_dossier.md (severity ladder level 5)
- **Authority:** owner_explicit
- **Content:** Confirmed corruption, misattribution, wrongful excerpting, or any silent content failure in trusted study material triggers immediate stop-using threshold.
- **Impact surface:** SPEC / tests
- **Already in SPEC?:** Partially in FP-5 but not as an explicit threshold ladder.

### ATOM-F7-004
- **Source:** F7/08_nonnegotiables.jsonl NG-002
- **Authority:** owner_explicit
- **Content:** Every study-facing unit must remain auditably tied to source, version, and processing lineage (provenance); weak provenance makes blast-radius containment impossible.
- **Impact surface:** contracts / Phase 3 / cross-engine
- **Already in SPEC?:** Not as a stated nonnegotiable; D-023 covers metadata flow but not auditability.

### ATOM-F7-005
- **Source:** F7/08_nonnegotiables.jsonl NG-003
- **Authority:** owner_explicit
- **Content:** No unbounded content error may remain live without immediate containment, blast-radius assessment, and visible warning; local errors must be quarantinable.
- **Impact surface:** SPEC / Phase 3 / contracts
- **Already in SPEC?:** Not explicitly stated.

### ATOM-F7-006
- **Source:** F7/08_nonnegotiables.jsonl NG-004
- **Authority:** owner_explicit
- **Content:** The system must never present low-confidence or weakly verified knowledge with the same confidence profile as strongly verified knowledge.
- **Impact surface:** Phase 3 / contracts / display-only
- **Already in SPEC?:** Partially via self-containment levels but not as a confidence-display principle.

### ATOM-F7-007
- **Source:** F7/08_nonnegotiables.jsonl NG-005
- **Authority:** owner_explicit
- **Content:** Boundary decisions must not distort meaning, remove necessary anchoring, or atomize study units into unusable fragments.
- **Impact surface:** SPEC / Phase 1 / Phase 2
- **Already in SPEC?:** Partially across FP-1, FP-3, FP-9.

### ATOM-F7-008
- **Source:** F7/08_nonnegotiables.jsonl NG-006
- **Authority:** owner_consistent_inference
- **Content:** Attribution, quote-layer, and current-source function must never be flattened into a single undifferentiated authorship assumption.
- **Impact surface:** Phase 2 / prompt / SPEC
- **Already in SPEC?:** Yes, captured in FP-14 and FP-15.

### ATOM-F7-009
- **Source:** F7/08_nonnegotiables.jsonl NG-008
- **Authority:** owner_explicit
- **Content:** The system must not hide excerpting cuts in a way that makes the result look like uninterrupted source flow; omissions must be honest.
- **Impact surface:** Phase 3 / contracts / display-only
- **Already in SPEC?:** Not explicitly stated as an omission-honesty rule.

### ATOM-F7-010
- **Source:** F7/08_nonnegotiables.jsonl NG-009
- **Authority:** owner_explicit
- **Content:** Validation must prove hard cases, not merely pass polished easy-path examples; hollow evaluation is itself a failure.
- **Impact surface:** tests / SPEC
- **Already in SPEC?:** No.

### ATOM-F7-011
- **Source:** F7/08_nonnegotiables.jsonl NG-011
- **Authority:** owner_explicit
- **Content:** The economics and performance model must remain compatible with full-corpus ambition; local success on tiny slices is not evidence of viability.
- **Impact surface:** cross-engine / SPEC
- **Already in SPEC?:** No.

### ATOM-F7-012
- **Source:** F7/08_nonnegotiables.jsonl NG-012
- **Authority:** owner_explicit
- **Content:** Project memory must be durable: progress, artifacts, backups, exports, and datasets must survive failure and migration.
- **Impact surface:** cross-engine
- **Already in SPEC?:** No (project-level, not engine-level).

### ATOM-F7-013
- **Source:** F7/08_nonnegotiables.jsonl NG-013
- **Authority:** owner_explicit
- **Content:** All collected data must be structured for future reuse, audit, and local-model training; today's outputs cannot be disposable or schema-fragile.
- **Impact surface:** contracts / cross-engine
- **Already in SPEC?:** Partially via D-023 and CLAUDE.md rule 13 (all data is training material).

### ATOM-F7-014
- **Source:** F7/04_failure_taxonomy.jsonl FAM-003
- **Authority:** owner_explicit
- **Content:** Excerpting is where source text becomes study units; errors at this stage directly shape what is memorized and are therefore the highest-risk transformation.
- **Impact surface:** SPEC
- **Already in SPEC?:** Implied by FP-5 but not stated as an explicit risk-ranking of the excerpting stage.

### ATOM-F7-015
- **Source:** F7/07_damage_paths.jsonl DP-004
- **Authority:** owner_explicit
- **Content:** Hidden omission makes the user memorize a surgically cleaned artifact as though it were faithful source flow; deceptive cleanliness is a specific failure mode.
- **Impact surface:** SPEC / Phase 3 / prompt
- **Already in SPEC?:** No explicit rule against deceptive cleanliness.

### ATOM-F7-016
- **Source:** F7/09_red_team_tests.jsonl RT-001
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Inject a single-character or diacritic-altering corruption into Arabic source text and verify that frozen-source comparison and downstream lineage all fail loudly.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F7-017
- **Source:** F7/09_red_team_tests.jsonl RT-002
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Force alternative split/merge decisions on the same passage and check whether meaning, anchoring, omission honesty, and study usability are preserved or broken.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F7-018
- **Source:** F7/02_failure_dossier.md (section: long-horizon regret)
- **Authority:** owner_explicit
- **Content:** Suboptimality -- loose architecture, insufficient research, weak tools -- is itself a failure even if nothing is directly corrupt, because it permanently lowers the ceiling of scholarship.
- **Impact surface:** cross-engine
- **Already in SPEC?:** No.

### ATOM-F7-019
- **Source:** F7/07_damage_paths.jsonl DP-008
- **Authority:** owner_explicit
- **Content:** Bad preserved data becomes bad training substrate, multiplying defects through future local models; data quality is future cognition quality.
- **Impact surface:** cross-engine / contracts
- **Already in SPEC?:** No (project-level concern).

### ATOM-F7-020
- **Source:** F7/07_damage_paths.jsonl DP-010
- **Authority:** owner_consistent_inference
- **Content:** Polished presentation is a force multiplier for both good and bad systems; false confidence from polish magnifies the rate and depth of harmful study before detection.
- **Impact surface:** display-only / cross-engine
- **Already in SPEC?:** No.

---

## F8 — Taxonomy Independence and Overgranulation

### ATOM-F8-001
- **Source:** F8/01_questionnaire_answer.md, F8/04_decision_ladder.jsonl DL-001/DL-002
- **Authority:** owner_explicit
- **Content:** Excerpting must be source-governed, not taxonomy-governed; taxonomy-biased excerpting is the most dangerous single failure because it silently corrupts knowledge at the earliest decisive stage.
- **Impact surface:** SPEC
- **Already in SPEC?:** Yes, captured in FP-4 (Taxonomy independence).

### ATOM-F8-002
- **Source:** F8/04_decision_ladder.jsonl DL-003, F8/09_nonnegotiables.jsonl NN-002
- **Authority:** owner_explicit
- **Content:** Rightful excerpt output must remain invariant under changes in tree granulation; if excerpt output changes because the tree changed, the wrong stage has influenced excerpt truth.
- **Impact surface:** SPEC / tests
- **Already in SPEC?:** Yes, captured in FP-4.

### ATOM-F8-003
- **Source:** F8/04_decision_ladder.jsonl DL-006/DL-007
- **Authority:** owner_explicit
- **Content:** Overgranulated placement is more dangerous than undergranulated placement because reassembling fragments is harder than noticing a missing split; overgranulation creates common-denominator confusion.
- **Impact surface:** SPEC / taxonomy / cross-engine
- **Already in SPEC?:** Yes, captured in FP-9 (Overgranulation is worse than undergranulation).

### ATOM-F8-004
- **Source:** F8/05_guidance_boundaries.jsonl GB-002/GB-003
- **Authority:** owner_explicit
- **Content:** The current taxonomy tree must have ZERO influence on excerpt boundary formation or excerpt grouping/splitting decisions.
- **Impact surface:** SPEC / Phase 2 / prompt
- **Already in SPEC?:** Yes, captured in FP-4.

### ATOM-F8-005
- **Source:** F8/05_guidance_boundaries.jsonl GB-004/GB-006
- **Authority:** owner_consistent_inference
- **Content:** Guidance from the taxonomy tree is permitted for placement, ranking, navigation, and presentation -- but only after excerpt truth is already frozen.
- **Impact surface:** cross-engine / taxonomy
- **Already in SPEC?:** Implicit in FP-4 but the positive allowance for post-excerpting guidance is not stated.

### ATOM-F8-006
- **Source:** F8/05_guidance_boundaries.jsonl GB-005, F8/09_nonnegotiables.jsonl NN-007
- **Authority:** model_only
- **Content:** Placement validation must never silently reject or reshape excerpts merely because they fit the current tree badly; a validator must not become a covert second excerpting engine driven by taxonomy fit.
- **Impact surface:** Phase 3 / taxonomy / cross-engine
- **Already in SPEC?:** No.

### ATOM-F8-007
- **Source:** F8/05_guidance_boundaries.jsonl GB-007, F8/09_nonnegotiables.jsonl NN-008
- **Authority:** owner_explicit
- **Content:** Tree revision (re-granulation) must not retroactively rewrite already-frozen excerpt truth; placement changes are allowed, excerpt identity changes are not.
- **Impact surface:** cross-engine / SPEC
- **Already in SPEC?:** Implied by FP-4 but the retroactive prohibition is not stated.

### ATOM-F8-008
- **Source:** F8/05_guidance_boundaries.jsonl GB-008
- **Authority:** owner_consistent_inference
- **Content:** Cross-stage feedback from placement convenience back into excerpt truth is absolutely prohibited; stage contamination must be treated as a primary architectural invariant.
- **Impact surface:** SPEC / cross-engine
- **Already in SPEC?:** Yes, core of FP-4.

### ATOM-F8-009
- **Source:** F8/02_assessment_dossier.md (silent corruption vs visible misplacement)
- **Authority:** owner_explicit
- **Content:** Silent excerpt corruption and visible taxonomy misplacement are different severity classes and must be tracked separately; they must never be treated as equivalent.
- **Impact surface:** SPEC / contracts
- **Already in SPEC?:** Partially in FP-5 (silent corruption worse) but the severity-class separation is not formalized.

### ATOM-F8-010
- **Source:** F8/10_red_team_tests.jsonl RT-001
- **Authority:** owner_explicit
- **Content:** RED-TEAM TEST: Run the same source passage under correctly granulated, undergranulated, and overgranulated trees; compare excerpt outputs for invariance.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F8-011
- **Source:** F8/10_red_team_tests.jsonl RT-003
- **Authority:** owner_consistent_inference
- **Content:** RED-TEAM TEST: Inject a misleading prior doctrinal box and test whether the excerpter starts cutting or framing the passage to fit it.
- **Impact surface:** tests
- **Already in SPEC?:** No specific test.

### ATOM-F8-012
- **Source:** F8/09_nonnegotiables.jsonl NN-006
- **Authority:** owner_consistent_inference
- **Content:** Blind or weakly guided processing must be audited for boundary consistency across comparable passages; uneven excerpt families hiding inside superficially plausible outputs are a real danger.
- **Impact surface:** tests / SPEC
- **Already in SPEC?:** No.

### ATOM-F8-013
- **Source:** F8/09_nonnegotiables.jsonl NN-010
- **Authority:** owner_explicit
- **Content:** Any sign that the excerpting stage is configuration-sensitive rather than source-sensitive must trigger an audit, not normalization of the instability.
- **Impact surface:** SPEC / Phase 2
- **Already in SPEC?:** Not explicitly; FP-4 states invariance but not the audit response.

### ATOM-F8-014
- **Source:** F8/13_open_questions.jsonl OQ-001
- **Authority:** owner_explicit
- **Content:** OPEN QUESTION: At the excerpting stage, is there any non-taxonomic form of guidance that would be acceptable if it improved consistency without altering rightful excerpt output?
- **Impact surface:** SPEC / Phase 2
- **Already in SPEC?:** No.

### ATOM-F8-015
- **Source:** F8/07_scenarios.jsonl SC-012, SC-014
- **Authority:** owner_explicit
- **Content:** Overgranulated placement can create false contradictions between sibling leaves: related excerpts that are parts of one broader unit look like contradictory positions when placed in separate overcut leaves.
- **Impact surface:** taxonomy / cross-engine
- **Already in SPEC?:** Not explicitly; FP-9 covers the general principle but not the false-contradiction mechanism.

---

## Cross-Collection Atoms (patterns appearing across multiple Fs)

### ATOM-CROSS-001
- **Source:** F3/NN-010, F4/NN-008, F5/NN-005, F6/NN-007, F8/NN-010
- **Authority:** owner_explicit (repeated across 5 collections)
- **Content:** Function classification and split/merge decisions must never be automated by surface heuristics alone; intelligent diagnosis including dependency analysis, question-cluster reasoning, and methodology awareness is required.
- **Impact surface:** SPEC / prompt / Phase 2
- **Already in SPEC?:** Partially in FP-3 and FP-6; the cross-collection strength of this requirement warrants elevation.

### ATOM-CROSS-002
- **Source:** F5/NN-005, F5/MR-004, F6/NN-007, F7/NG-010
- **Authority:** owner_explicit (repeated across 4 collections)
- **Content:** Uncertainty gates are mandatory: when the system is not confident about structure, methodology fit, variant significance, or split safety, it must escalate rather than proceed with false confidence.
- **Impact surface:** SPEC / prompt / Phase 2 / Phase 3
- **Already in SPEC?:** Yes, captured in FP-6 but the operational mechanism is not defined.

### ATOM-CROSS-003
- **Source:** F3/NN-003, F4/NN-004, F5/NN-002
- **Authority:** owner_explicit (repeated across 3 collections)
- **Content:** Linking words (لأن, عليهما, غسلهما, فهو, و, وأصحها) must be evaluated case-by-case; some are causal continuations requiring retention, some are local continuations safe to cut, some are semantic carryovers needing context blocks.
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Yes, captured in FP-3.

### ATOM-CROSS-004
- **Source:** F5/PI-001, F5/PI-002, F6/PL-001, F6/PL-002
- **Authority:** owner_explicit (repeated across 2 collections)
- **Content:** The library requires at least three proof-related layers: (1) scholar-book proof witness, (2) authoritative fetched proof, (3) comparison/alignment layer that shows how they relate.
- **Impact surface:** cross-engine / deferred-feature
- **Already in SPEC?:** Partially in FP-7 (two layers mentioned); the alignment layer is not in SPEC.

### ATOM-CROSS-005
- **Source:** F7/NG-001, F7/NG-005, F8/NN-001
- **Authority:** owner_explicit (repeated across 2 collections)
- **Content:** Knowledge corruption through excerpting (wrong cuts, wrong merges, wrong grouping, silent omission) is existential; the engine must always assume an excerpt is wrongfully excerpted until proven otherwise.
- **Impact surface:** SPEC
- **Already in SPEC?:** Yes, captured in FP-5.

### ATOM-CROSS-006
- **Source:** F3/02_case_dossier.md, F4/02_case_dossier.md
- **Authority:** owner_explicit (repeated across 2 collections)
- **Content:** Surface appearance (chapter-intro language, short sentence fragments) must never override actual function analysis; the system must look past what text "looks like" to what it "does."
- **Impact surface:** prompt / Phase 2
- **Already in SPEC?:** Not as a standalone principle.

### ATOM-CROSS-007
- **Source:** F7/DP-004, F7/NG-008, F8/02_assessment_dossier.md
- **Authority:** owner_explicit
- **Content:** Excerpting cuts must be honest: the result must not look like uninterrupted source flow when material has been omitted. Deceptive cleanliness is a named failure mode.
- **Impact surface:** Phase 3 / contracts / display-only
- **Already in SPEC?:** No explicit omission-honesty rule in SPEC.

---

## Summary Statistics

| Collection | Atoms Extracted | owner_explicit | owner_consistent_inference | model_only |
|------------|----------------|----------------|---------------------------|------------|
| F3         | 12             | 10             | 1                         | 1          |
| F4         | 8              | 7              | 0                         | 1          |
| F5         | 10             | 8              | 1                         | 1          |
| F6         | 9              | 8              | 0                         | 1          |
| F7         | 20             | 16             | 2                         | 2          |
| F8         | 15             | 11             | 3                         | 1          |
| Cross      | 7              | 7              | 0                         | 0          |
| **Total**  | **81**         | **67**         | **7**                     | **7**      |

## Already-Captured vs New Atoms

| Status | Count | Examples |
|--------|-------|---------|
| Already in SPEC (fully captured) | 18 | FP-4, FP-5, FP-6, FP-7, FP-8, FP-9 atoms |
| Partially in SPEC (needs strengthening) | 16 | FP-1 detail on variants, FP-3 operationalization, FP-5 threshold ladder |
| Not in SPEC (new atoms) | 34 | Sub-excerpting rules, question-cluster method, omission honesty, title retention asymmetry, proof alignment layer, boundary consistency audit |
| Test atoms (red-team) | 9 | Invariance test, injection test, split-mutation tests |
| Open questions | 4 | Chapter-intro marking, non-taxonomic guidance, explanation separation conditions, overgranulation threshold |

## Highest-Priority New Atoms Not Yet in SPEC

1. **ATOM-F3-001** -- Surface-function misread prohibition (prompt-critical)
2. **ATOM-F3-004** -- Title-retention asymmetry (prompt-critical)
3. **ATOM-F3-006** -- Forgiving-rule quantitative limit (SPEC-critical)
4. **ATOM-F4-003** -- Clipped tarjih prohibition (SPEC-critical)
5. **ATOM-F4-006** -- Question-cluster methodology (SPEC-critical)
6. **ATOM-F7-009** -- Omission honesty / deceptive cleanliness prohibition (SPEC-critical)
7. **ATOM-F7-010** -- Hollow evaluation prohibition (test-critical)
8. **ATOM-F8-006** -- Validator must not be a covert second excerpter (Phase 3-critical)
9. **ATOM-F8-012** -- Boundary consistency audit requirement (test-critical)
10. **ATOM-CROSS-007** -- Deceptive cleanliness as a named failure mode (SPEC-critical)
