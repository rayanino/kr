# Source Spec Atoms by Layer: contracts

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML and PDF are production formats | confirmed | high |
| CON-SRC-0002 | constraint | Hadith literature dominates source-engine benchmark quality | confirmed | high |
| CON-SRC-0003 | constraint | No existing pipeline contract is binding on the rebuild | confirmed | critical |
| CON-SRC-0004 | constraint | Complete SourceMetadata output schema | confirmed | critical |
| CON-SRC-0005 | constraint | Normalization handoff bundle includes a bridge input contract | confirmed | high |
| CON-SRC-0006 | constraint | Per-book processing cost and time ceiling | confirmed | high |
| CON-SRC-0007 | constraint | Source type extensibility | confirmed | high |
| CON-SRC-0011 | constraint | WorkLevel enum — classical pedagogical-level vocabulary | confirmed | high |
| CON-SRC-0012 | constraint | Error severity taxonomy | confirmed | high |

### CON-SRC-0001 — Shamela HTML and PDF are production formats
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001; amended per OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Rule: Production source intake must support Shamela HTML and PDF inputs, while plain text remains a minimal-metadata test format rather than a production collection format.

### CON-SRC-0002 — Hadith literature dominates source-engine benchmark quality
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0012; amended per contract-architect-review.yaml
- Rule: At least 40 percent of source-engine benchmark fixtures must be hadith literature or hadith-adjacent works.

### CON-SRC-0003 — No existing pipeline contract is binding on the rebuild
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0014
- Rule: Archived and legacy source-engine contracts are reference material only and cannot overrule the current atom set.

### CON-SRC-0004 — Complete SourceMetadata output schema
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-002; amended per reference/ pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction. Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003: (a) added the mandatory `level_status` enum field per Gemini DR's middle- path proposal, which closes the null-conflation gap that Claude DR correctly identified without adopting OPT-C's shallow-signal level emission; (b) level_status provenance is the source engine at admission time, with values pending_synthesis or non_applicable_reference, extended by the synthesis engine to assigned or unprocessable_error. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) to reconcile the non-applicable genre set to a six-value frozenset {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} and to cite the 3-axis gate defined by INV-SRC-0012 (genre + composite_work_type + deferred HadithSubgenre). Non-applicable fatwa_compilation / lexicon / biographical_dictionary / rijal_dictionary / majmu entries were removed as scholarly category errors per 2026-04-22 unanimous 2-run Gemini CLI BLOCKER_PRESENT findings; AC-3 continues to assume Axis 1 firing (genre="mushaf") while AC-4 covers the leveled-genre-no-override-no-composite default (composite_work_type is assumed null unless set by REQ-SRC-0038). See .kr/runtime/adjudication_gemini_dr_20260417.md sections q5 and final_recommendation, and follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the 3-of-3 UNANIMOUS_OWN_SYNTHESIS HIGH-confidence verdict from Codex CLI (gpt-5.4, architectural-fit axis) plus Gemini CLI 2-run (gemini-3.1-pro-preview Run A and gemini-2.5-pro Run B, classical-scholarly-defensibility axis) on the synthesis-vs- taxonomy paper-reconciliation that Phase 5a reviewer wave flagged (Codex CAF-2 + CC-adversary ADV-003). Implementation edits: (a) enum value `pending_taxonomy` renamed to `pending_synthesis` throughout (rule.statement, rule.implication, acceptance_criteria, cross-field invariant 2, source-field narrative); (b) per Gemini Run B unique catch, the generic wording "a downstream engine" in rule.implication lines 74-78 (the `assigned` definition and `unprocessable_error` definition) tightened to "the synthesis engine" for single-writer discipline (Codex architectural test 1); (c) "reserved for downstream engines" tightened to "reserved for the synthesis engine"; (d) the 2026-04-17 source-narrative line "extended by downstream engines to" tightened to "extended by the synthesis engine to". Classical scholarly grounding (Gemini Run A + Run B cross-confirmed): al-Fihrist of Ibn al-Nadīm and Kashf al-Ẓunūn of Ḥājjī Khalīfa classify by fann + nawʿ but systematically omit martaba — martaba is pedagogical not bibliographic; Ibn Khaldūn's Muqaddima Book VI on taʿlīm al- ʿulūm anchors martaba in content density and tadarruj; al- Zarnūjī's Taʿlīm al-Mutaʿallim Chapter IV distinguishes reader- level from text-level. Al-Kattānī's al-Risāla al-Mustaṭrafah nawʿ-classification of ḥadīth books was considered by Gemini Run B as an OWN_TAXONOMY counter-argument but weighed down by the bibliographic-vs-pedagogical distinction. New Phase 5b follow-up item 28 opened for the architectural unreachability of LevelProvenance.TAXONOMY_ENGINE under OWN_SYNTHESIS (not in 3-evaluator reading list, deferred to a separate dispatch). Reviewer outputs: .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md, .kr/runtime/domain_validation_gemini_cli_item7_run_A_20260423.md, .kr/runtime/domain_validation_gemini_cli_item7_run_B_20260423.md. Follow-up 32 amendment on 2026-04-24 resolves atom-vs-contract nested-shape drift for REQ-SRC-0046: genre_dispute is explicitly an optional evidence-bearing list of alternate genre positions (genre_candidate, supporting_evidence, confidence, source_agents), ordered by descending confidence and preserved recursively at handoff. muhaqiq_output remains the live MuhaqiqAssessment shape; edition_info remains a flexible Optional[dict[str, Any]] surface.
- Rule: Every source-engine accepted source emits one SourceMetadata record with non-null mandatory fields source_id, source_sha256, frozen_blob_path, registry_entry_id, title_arabic, author_output, work_output, genre, science_scope, is_multi_layer, structural_format, trust_decision, completeness_status, integrity_status, volume_count, intake_timestamp, AND level_status. The author_output field must always contain status (one of agent_consensus, agent_disagreement, agent_no_evidence, co_authored) and positions. The level_status field must always contain one of the four enum values defined below.

### CON-SRC-0005 — Normalization handoff bundle includes a bridge input contract
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract review found that SourceMetadata alone no longer defines a runnable source→normalization boundary in the live repo.
- Rule: Every source-engine accepted source must emit a NormalizationHandoffBundle containing non-null SourceMetadata, NormalizationInput, FrozenMemberManifest, completeness_status, and integrity_status.

### CON-SRC-0006 — Per-book processing cost and time ceiling
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: medium
- Source: adversary-review-2 ADV2-010 (no atom specifies timeout or cost ceiling for agent operations)
- Rule: Every source candidate has a maximum wall-clock processing time of 300 seconds and a maximum per-book API cost ceiling (initial default EUR 0.50). When either ceiling is reached, processing halts gracefully, the book is flagged with processing_timeout or processing_budget_exceeded in study_quality_risk_flags, and it is routed through the risk gate rather than consuming unbounded resources. Partial results obtained before the ceiling are preserved, not discarded.

### CON-SRC-0007 — Source type extensibility
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview 2026-04-14 identifying YouTube transcripts as the third most valuable source type after Shamela and PDF, requiring the architecture to accommodate new formats without restructuring
- Rule: The container classification step (step 30) must be designed so that adding a new source format requires only registering a new classifier and normalization route, without modifying existing classifiers or restructuring the pipeline. Current formats are shamela_html, pdf, and plain_text. Future formats include but are not limited to lecture_transcript. Container classification routes each format to normalization via a configurable normalization_route field on the classification output, not via hardcoded format-specific branching.

### CON-SRC-0011 — WorkLevel enum — classical pedagogical-level vocabulary
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-17 following the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003. The enum values derive from Gemini CLI run 2 classical-defensibility review (R2 finding) which identified that the ChatGPT DR amendment set used `mutaqaddim` as the "advanced" level value — incorrect classical usage. Mutaqaddim (متقدم) denotes chronological priority (an earlier-generation scholar relative to a later one), NOT pedagogical advancement. The correct classical pedagogical ladder is mubtadiʾ (beginner) → mutawassiṭ (intermediate) → muntahī (terminal / advanced), documented in al-Zarnūjī's Taʿlīm al-Mutaʿallim, Ibn Khaldūn's Muqaddima Book VI (faṣl fī wajh al-ṣawāb fī taʿlīm al-ʿulūm), and the standard curriculum language of Dār al-Muṣṭafā and al- Qarawiyyīn ḥadīth tracks. See .kr/runtime/ adjudication_gemini_cli_run1_20260417.md (R2 terminology finding) and run2_20260417.md (independent confirmation). Amended 2026-04-23 (Phase 5b item 5) to break 3 producer-consumer cycles: the original depends_on list named INV-SRC-0011, CON-SRC-0004, and REQ-SRC-0047 — all of which CONSUME this enum and themselves declare CON-SRC-0011 as a producer, creating cycles that break scoped atom injection per Codex CAF-1. The corrected ordering is strictly producer-before- consumer: CON-SRC-0011 defines the WorkLevel vocabulary, so it depends only on the architectural decision (DEC-SRC-0003) that authorized having a level vocabulary at all; every atom that uses the enum (INV-SRC-0011, INV-SRC-0012, CON-SRC-0004, REQ-SRC-0047, REQ-SRC-0007) declares CON-SRC-0011 as an upstream producer. Further amended 2026-04-23 (Phase 5b item 11) to add the C7 multi-layer scope clause: the single scalar SourceMetadata.level, when populated for a multi-layer work (matn + sharḥ, sharḥ + ḥāshiya, or deeper nestings), refers to the TARGET READERSHIP of the composite work as a whole — the pedagogical state of the student for whom the work is intended — NOT the level of any contained layer, the author's own scholarly stature, or the matn's intrinsic density. Per Gemini CLI Run B C7 verdict CONFIRM (interpretation_measured: target_readership, `.kr/runtime/domain_validation_gemini_cli_run_B_20260417.md`:95-102) and Adversary finding ADV-007 (severity: HIGH; affected_atoms: REQ-SRC-0046, CON-SRC-0011, CON-SRC-0004; `.kr/runtime/ adversary_phase5a_20260417.md`:242-252). Classical-defensibility reasoning: all four madhāhib use the mubtadiʾ/mutawassiṭ/muntahī terminology to describe the student-state at which the work is pitched, not the author's own rank (al-Zarnūjī Taʿlīm al-Mutaʿallim IV; Ibn Khaldūn Muqaddima VI, faṣl fī wajh al-ṣawāb fī taʿlīm al- ʿulūm). The scope is the owner's own question — "what student can read this?" — so the library ladder matches his actual progression. A sharḥ authored by a muntahī but composed to teach mubtadiʾ students is assigned level="mubtadiʾ"; a ḥāshiya composed for muntahī-level Ḥanafī specialists is assigned level="muntahī" regardless of the underlying matn's native level. This interpretation is strictly stronger than the Adversary's proposed "outer author's work only" alternative fix — it refuses the author-rank proxy in favor of the pedagogical-fit question the owner actually asks of the library. Closure-wave amendment 2026-04-23 (Codex CAF-5 + 2-of-2 Gemini DIM1/DIM2 convergent): (a) replaced residual "taxonomy engine" wording in rationale with "synthesis engine" per DEC-SRC-0003 synthesis-owns-level (closes Codex CAF-5); (b) anchored the multi-layer scope clause in rule.statement to the classical Arabic istiʿdād al-mutaʿallim (استعداد المتعلم) per Ibn Khaldūn Muqaddima VI, with al-qāriʾ al-maqṣūd (القارئ المقصود) as equivalent gloss (closes 2-of-2 Gemini DIM1 — Run A proposed istiʿdād, Run B proposed al-qāriʾ al-maqṣūd; both kept, classical primacy to Ibn Khaldūn's exact phrasing); (c) augmented AC-7 from a single Hanbali exemplar (Ibn ʿUthaymīn) to a four-madhhab exemplar set (Maḥallī Sharḥ al-Waraqāt for Shafiʿi, al-Shurunbulālī Nūr al- Īḍāḥ for Hanafi, Zarrūq Sharḥ al-Risālah for Maliki, original Ibn ʿUthaymīn retained for Hanbali), avoiding perceived madhhab bias and demonstrating that the istiʿdād al-mutaʿallim scope rule is universally institutionalized across the Sunni schools (closes 2-of-2 Gemini DIM2 convergent finding). Reviewer outputs at `.kr/runtime/closure_wave_codex_cli_20260423.md` and `.kr/runtime/closure_wave_gemini_cli_run_{A,B}_20260423.md`.
- Rule: The WorkLevel enum is the canonical vocabulary for the SourceMetadata.level field and any downstream field that stores an authoritative pedagogical-level assignment. It has exactly three permitted values: "mubtadiʾ" (beginner / pre-malakah student), "mutawassiṭ" (intermediate / foundational-malakah student), and "muntahī" (terminal / curriculum-completing student). No other string values are valid for a SourceMetadata .level assignment. The historiographic term "mutaqaddim" and its counterpart "mutaʾakhkhirūn" are REJECTED as WorkLevel values — they denote chronological / generational priority among scholars, not pedagogical level. For a multi-layer work (matn + sharḥ, sharḥ + ḥāshiya, or deeper nestings), the single scalar SourceMetadata.level refers to the TARGET READERSHIP of the composite work as a whole — the pedagogical state of the student for whom the work is intended — NOT the level of any contained layer, the author's own scholarly stature, or the matn's intrinsic density. The classical Arabic anchor for this scope is istiʿdād al-mutaʿallim (استعداد المتعلم) per Ibn Khaldūn Muqaddima VI, faṣl fī wajh al-ṣawāb fī taʿlīm al-ʿulūm — "wa-muraʿāt istiʿdād al-mutaʿallim wa-qabūlihi" — the readiness and receptivity of the learner for whom the work is pitched; al-qāriʾ al-maqṣūd (القارئ المقصود) is an acceptable equivalent gloss. A sharḥ composed by a muntahī to teach mubtadiʾ students is assigned level="mubtadiʾ"; a ḥāshiya composed for muntahī-level Ḥanafī specialists is assigned level="muntahī" regardless of the underlying matn's native level.

### CON-SRC-0012 — Error severity taxonomy
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Established on 2026-04-21 per Phase 5b item 13 closing Codex CLI's Phase 5a reviewer-wave finding S7 ("schema enum {fatal, blocking, warning} has no operational definition anywhere"). The JSON Schema at engines/source/spec/schema.json $defs/severity pins the three permitted values but provides no semantic guidance. With 75+ behavior.error_conditions severity assignments across the atom corpus (24 fatal, 21 blocking, 30 warning as of this atom's creation date), the absence of operational semantics means each atom author has been free to interpret the values differently, silently corrupting the pipeline's error-recovery contract. This atom fixes the semantics once and authoritatively. Amended same day (2026-04-21) per the retroactive reviewer wave on commit bf4354399: Codex CLI finding S3-DIM3 BLOCKER flagged AC-1's example citation of SRC-E-AUTHOR-COPYIST-CONFLATION per REQ-SRC- 0014 as an unreachable reference — REQ-SRC-0014 actually declares attribution_role_conflict, not that error code. The S6-DIM6A paper-reconciliation audit flagged AC-6's example citation of SRC-E-ARABIC-TEXT-BYTES-MUTATED as absent from both the ErrorCode enum and the spec atoms. Both ACs realigned to existing real error codes: AC-1 now cites SRC-E-PDF-TEXT-EVIDENCE-MUTATED (REQ-SRC-0023) and SRC-E-FREEZE-VERIFY (REQ-SRC-0018); AC-6 now cites SRC-E-PDF-TEXT-EVIDENCE-MUTATED, which is the canonical existing declaration for byte-level upstream mutation of primary text. The scholarly semantics of AC-6 (byte-level primary-text mutation must be fatal per T-1) are unchanged — only the example citation is realigned. Gemini CLI 2-run scholarly review (AMEND on taxonomy collapse of tahqiq / hamza / agent-disagree / owner-override nuances) is logged as a follow-up Phase 5b item for taxonomy expansion, not a blocker on this atom.
- Rule: Every behavior.error_conditions[].severity value in any source- engine spec atom carries a defined operational semantic. "fatal" means unrecoverable data corruption — the condition indicates that scholarly metadata or primary text has been damaged in a way that cannot be reconstructed from the inputs available to the pipeline, and no downstream engine may proceed with the affected record. "blocking" means recoverable rejection — the condition prevents the current operation from completing but a specific correction path exists (owner resubmits with a valid override, upstream re-emits missing evidence, transient dependency recovers). "warning" means advisory — the condition is logged and the operation continues; suitable for observability signals that must not halt the pipeline. These three values are mutually exclusive and collectively exhaustive for the severity enum.
