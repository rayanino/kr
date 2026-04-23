# Source Spec Atoms by Topic: handoff

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0003 | constraint | No existing pipeline contract is binding on the rebuild | confirmed | critical |
| CON-SRC-0004 | constraint | Complete SourceMetadata output schema | confirmed | critical |
| CON-SRC-0005 | constraint | Normalization handoff bundle includes a bridge input contract | confirmed | high |
| DEC-SRC-0014 | decision | Separate raw-upload tracking from official source admission | confirmed | critical |
| DEC-SRC-0015 | decision | Normalization consumes a bridge input model, not raw SourceMetadata | confirmed | high |
| DEC-SRC-0016 | decision | Owner-submission risk gate blocks admission and downstream progression | confirmed | critical |
| OF-SRC-0014 | feedback | Legacy contracts do not cap the rebuild | confirmed | critical |
| OF-SRC-0015 | feedback | Build source-engine teams inside the source-engine scope first | confirmed | medium |
| REQ-SRC-0025 | requirement | Two-stage source admission and normalization handoff packaging | confirmed | critical |
| REQ-SRC-0027 | requirement | Owner-submission risk gate for study-quality threats | confirmed | critical |
| REQ-SRC-0033 | requirement | Volume count and intake timestamp derivation | confirmed | high |
| REQ-SRC-0046 | requirement | Evidence preservation for downstream level inference | confirmed | critical |

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
- Source: Added from adversary-review.yaml ADV-002; amended per reference/ pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction. Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003: (a) added the mandatory `level_status` enum field per Gemini DR's middle- path proposal, which closes the null-conflation gap that Claude DR correctly identified without adopting OPT-C's shallow-signal level emission; (b) level_status provenance is the source engine at admission time, with values pending_synthesis or non_applicable_reference, extended by the synthesis engine to assigned or unprocessable_error. Amended on 2026-04-23 (Phase 5b item 4, Option E-prime-final) to reconcile the non-applicable genre set to a six-value frozenset {mushaf, hadith_collection, mashyakhah, thabat, barnamaj, fahrasah} and to cite the 3-axis gate defined by INV-SRC-0012 (genre + composite_work_type + deferred HadithSubgenre). Non-applicable fatwa_compilation / lexicon / biographical_dictionary / rijal_dictionary / majmu entries were removed as scholarly category errors per 2026-04-22 unanimous 2-run Gemini CLI BLOCKER_PRESENT findings; AC-3 continues to assume Axis 1 firing (genre="mushaf") while AC-4 covers the leveled-genre-no-override-no-composite default (composite_work_type is assumed null unless set by REQ-SRC-0038). See .kr/runtime/adjudication_gemini_dr_20260417.md sections q5 and final_recommendation, and follow-ups 21-26. Amended on 2026-04-23 (Phase 5b item 7, ownership story closure) for the 3-of-3 UNANIMOUS_OWN_SYNTHESIS HIGH-confidence verdict from Codex CLI (gpt-5.4, architectural-fit axis) plus Gemini CLI 2-run (gemini-3.1-pro-preview Run A and gemini-2.5-pro Run B, classical-scholarly-defensibility axis) on the synthesis-vs- taxonomy paper-reconciliation that Phase 5a reviewer wave flagged (Codex CAF-2 + CC-adversary ADV-003). Implementation edits: (a) enum value `pending_taxonomy` renamed to `pending_synthesis` throughout (rule.statement, rule.implication, acceptance_criteria, cross-field invariant 2, source-field narrative); (b) per Gemini Run B unique catch, the generic wording "a downstream engine" in rule.implication lines 74-78 (the `assigned` definition and `unprocessable_error` definition) tightened to "the synthesis engine" for single-writer discipline (Codex architectural test 1); (c) "reserved for downstream engines" tightened to "reserved for the synthesis engine"; (d) the 2026-04-17 source-narrative line "extended by downstream engines to" tightened to "extended by the synthesis engine to". Classical scholarly grounding (Gemini Run A + Run B cross-confirmed): al-Fihrist of Ibn al-Nadīm and Kashf al-Ẓunūn of Ḥājjī Khalīfa classify by fann + nawʿ but systematically omit martaba — martaba is pedagogical not bibliographic; Ibn Khaldūn's Muqaddima Book VI on taʿlīm al- ʿulūm anchors martaba in content density and tadarruj; al- Zarnūjī's Taʿlīm al-Mutaʿallim Chapter IV distinguishes reader- level from text-level. Al-Kattānī's al-Risāla al-Mustaṭrafah nawʿ-classification of ḥadīth books was considered by Gemini Run B as an OWN_TAXONOMY counter-argument but weighed down by the bibliographic-vs-pedagogical distinction. New Phase 5b follow-up item 28 opened for the architectural unreachability of LevelProvenance.TAXONOMY_ENGINE under OWN_SYNTHESIS (not in 3-evaluator reading list, deferred to a separate dispatch). Reviewer outputs: .kr/runtime/structural_audit_codex_cli_item7_retry_20260423.md, .kr/runtime/domain_validation_gemini_cli_item7_run_A_20260423.md, .kr/runtime/domain_validation_gemini_cli_item7_run_B_20260423.md.
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

### DEC-SRC-0014 — Separate raw-upload tracking from official source admission
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that uploaded artifacts must not pollute the official source collection before source-engine acceptance.
- Chosen option: OPT-B — Two registries with staged admission
- Decision rationale: This preserves full upload traceability without polluting the official source collection before the source engine genuinely accepts the source.

### DEC-SRC-0015 — Normalization consumes a bridge input model, not raw SourceMetadata
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added on 2026-04-14 after contract-auditor review found that the redesigned SourceMetadata surface no longer matches the live normalization boundary.
- Chosen option: OPT-B — Emit a NormalizationInput bridge inside the handoff bundle
- Decision rationale: This preserves source-engine clarity while giving normalization a concrete boundary contract that can evolve independently later.

### DEC-SRC-0016 — Owner-submission risk gate blocks admission and downstream progression
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that any uncertainty materially affecting study quality should trigger a human gate before valuable downstream work proceeds.
- Chosen option: OPT-B — Emit provisional output and block progression
- Decision rationale: This preserves pipeline-quality analysis while protecting the collection and downstream work from materially risky owner submissions.

### OF-SRC-0014 — Legacy contracts do not cap the rebuild
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 4 question 2
- Interview question: How much authority do existing pipeline contracts keep during the rebuild?
- Owner answer: All engines will be rebuilt. No existing contract is binding, and the source engine should be engineered to the best possible quality without being capped by old infrastructure.

### OF-SRC-0015 — Build source-engine teams inside the source-engine scope first
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Owner interview batch 4 question 3
- Interview question: Where should the first agent infrastructure land?
- Owner answer: The immediate focus is the source engine. The best spec, build, and agent-team design should be created inside source-engine scope first, while reusable questions can be lifted later when downstream engines are built.

### REQ-SRC-0025 — Two-stage source admission and normalization handoff packaging
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that raw uploads must not pollute the official source collection and that structurally valid but partial sources may still proceed with explicit flags.
- Trigger: Source-engine finalization runs after metadata deliberation completes for a source candidate.
- Postconditions:
  - raw_upload_record.status is set to awaiting_owner_ack, source_engine_accepted, or rejected_at_source based on the source-engine result and any live owner_submission_risk_case.
  - The official source_collection is written only when the source engine completes successfully and no live owner_submission_risk_case remains unacknowledged.
  - Structurally valid sources with completeness_status in {partial, mixed, indeterminate} may still enter the source_collection with explicit admission_reason and preserved flags.
  - Structurally invalid uploads do not create source_collection records.
  - normalization_handoff_bundle is written only for source_engine_accepted sources whose owner_submission_risk_case is absent or acknowledged, and contains SourceMetadata, NormalizationInput, FrozenMemberManifest, and preserved intake_dossier completeness and integrity verdicts.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after successful metadata deliberation; When source admission and normalization handoff packaging execute; Then raw_upload_record.status="source_engine_accepted", exactly one source_collection record is written, and normalization_handoff_bundle.SourceMetadata.registry_entry_id is non-empty..
  - AC-2 [deterministic] Given A structurally valid upload whose intake_dossier.completeness_status="partial"; When source admission and normalization handoff packaging execute; Then one source_collection record is written with admission_reason="accepted_with_flags" and the handoff preserves completeness_status="partial"..
  - AC-3 [deterministic] Given A raw upload rejected earlier with error_code=SRC-E-EMPTY-FILE; When source admission and normalization handoff packaging would otherwise execute; Then no source_collection record is written for that submission..
  - AC-4 [deterministic] Given A source candidate with a live owner_submission_risk_case awaiting acknowledgment; When source admission and normalization handoff packaging execute; Then raw_upload_record.status="awaiting_owner_ack", no source_collection record is written, and no normalization_handoff_bundle is emitted..

### REQ-SRC-0027 — Owner-submission risk gate for study-quality threats
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner guidance on 2026-04-14 that any uncertainty materially affecting study quality should trigger a human gate before official admission or downstream work proceeds.
- Trigger: Source-engine finalization evaluates whether the candidate carries any uncertainty that could materially affect study quality.
- Postconditions:
  - When study_quality_risk_flags is empty, no owner_submission_risk_case is written and normal source admission may continue.
  - When study_quality_risk_flags is non-empty, owner_submission_risk_case is written with owner_ack_required=true.
  - A live owner_submission_risk_case blocks official source_collection admission and blocks normalization_handoff_bundle emission until the owner acknowledges or annotates the case.
  - The source engine may still preserve provisional analysis outputs for review while the gate remains open.
- Acceptance criteria:
  - AC-1 [deterministic] Given A source candidate whose intake_dossier.study_quality_risk_flags is empty; When the owner-submission risk gate executes; Then no owner_submission_risk_case is written..
  - AC-2 [deterministic] Given A source candidate identified as one volume of a larger work with material dependency on missing volumes; When the owner-submission risk gate executes; Then owner_submission_risk_case.owner_ack_required=true, source_collection admission is blocked, and normalization handoff is blocked..
  - AC-3 [deterministic] Given A readable but suspicious source whose trust or integrity uncertainty could materially mislead study; When the owner-submission risk gate executes; Then owner_submission_risk_case.risk_flags is non-empty and owner_submission_risk_case.gate_status="awaiting_owner_ack"..

### REQ-SRC-0033 — Volume count and intake timestamp derivation
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added after contract-architect review found volume_count and intake_timestamp are mandatory in CON-SRC-0004 but no requirement atom produces them.
- Trigger: Source admission finalizes the SourceMetadata record for an accepted source.
- Postconditions:
  - source_metadata.volume_count is set to the observed volume count from intake_dossier.declared_vs_observed_counts.observed_volume_count for multi-volume sources, or 1 for single-file sources.
  - source_metadata.intake_timestamp is set to the UTC ISO 8601 timestamp at the moment SourceMetadata finalization completes.
  - source_metadata.registry_entry_id is assigned as a unique identifier linking this SourceMetadata to its entry in the official source_collection registry.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after source-engine acceptance; When SourceMetadata finalization runs; Then source_metadata.volume_count=1 and source_metadata.intake_timestamp is a valid ISO 8601 UTC timestamp..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small after source-engine acceptance; When SourceMetadata finalization runs; Then source_metadata.volume_count=3 and source_metadata.registry_entry_id is non-empty..

### REQ-SRC-0046 — Evidence preservation for downstream level inference
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-3. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR) and the R1/R2 reviewer wave: (a) nested Optional serialization rule added — when a preserved signal carries a nested structured field (e.g. muhaqiq_output, work_relationships, display_card), the nested object MUST itself honor D-023 and serialize absent sub-fields as explicit nulls rather than omitting keys; (b) genre_dispute signal added as required-preserved per R1 finding that disputed-genre payloads currently drop the secondary positions; (c) dedicated acceptance criteria now exercise the two signals most historically dropped at handoff (contains_isnad_chains and genre_dispute); (d) depends_on corrected to include DEC-SRC-0003 and INV-SRC-0011 because the evidence-preservation contract is the mechanism that makes the downstream content-only level classification (OPT-B) possible. Amended on 2026-04-21 per Phase 5b item 14 closing the Phase 5a Adversary ADV-011 finding ("positions[0].death_date unexercised"): AC-7 added to exercise depth-2 nested Optional serialization where the Optional sub-field is nested inside a list item. AC-6 already covers depth-1 direct-child omission; AC-7 closes the structurally distinct list-item sub-field omission case that Pydantic default serialization can silently drop when exclude_unset traverses list elements. Same-day retroactive reviewer wave on commit bf4354399 (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way AMEND consensus that the originally-committed path muhaqiq_output.positions[0].death_date was both structurally aspirational (MuhaqiqAssessment in contracts.py has no positions field) and scholarly-incorrect (muhaqqiqs unify on the title page of a critical edition and do not carry multi-position attributions in classical tahqiq practice; authorship disputes across نُسَخ produce the multi-position structure, not editorial attribution). AC-7 realigned to author_output.positions[0].death_hijri — structurally grounded (AuthorOutputPosition at contracts.py:676-712 declares death_hijri as Optional[int]) and scholarly-grounded (multi-position attribution is the canonical disputed-authorship shape in Dar Ibn Hazm / Muʾassasat al-Risāla critical-edition practice). The required-preserved signal set is correspondingly expanded from 16 signals to 17 by adding author_output; its inclusion is justified by the fact that author_output is already a mandatory SourceMetadata field per CON-SRC-0004, so preservation at handoff was always implicit — this amendment makes it explicit and subjects it to the recursive D-023 rule. Also amended on 2026-04-21 per Phase 5b item 16 closing a paper-reconciliation gap between the atom and contracts.py ErrorCode enum. Yesterday's retroactive Codex S6-DIM6A BLOCKER flagged that SRC-E-EVIDENCE-DROPPED and SRC-E-EVIDENCE-DROPPED- NESTED were cited in error_conditions and AC-3/AC-6/AC-7 but absent from contracts.py::ErrorCode. Item 16 pre-commit dispatch (Codex CLI structural + Gemini CLI 2 independent scholarly runs, all optimized through /prompt-architect) reached 3-way unanimous PREFER_B verdict: rename to SRC-E-HANDOFF-EVIDENCE-DROPPED and SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED per the standing 2026-04-16 ChatGPT Deep Research advisory (dr-chatgpt-level-detection- 20260416.yaml:950) disambiguating step-60 handoff packaging omission from the step-40 intake code SRC-E-PDF-TEXT-EVIDENCE- DROPPED (PyMuPDF text-layer eviction). Scholarly rationale from both Gemini runs: step 60 omission maps to T-2 Attribution Error and T-6 Metadata Poisoning in reference/KNOWLEDGE_INTEGRITY.md, distinct from step 40's T-1 Silent Text Corruption; the HANDOFF_ prefix prevents Arabic-localization conflation of the error with hadith-science proof rejection (دليل شرعي / شاهد / قرينة) when surfaced to the owner as إسقاط دليل التسليم rather than the ambiguous إسقاط الدليل. Both enum entries added to engines/source/contracts.py ErrorCode step-60 block. All five normative reference sites (behavior.error_conditions @113/@116, AC-3 then-clause, AC-6 then-clause, AC-7 then-clause) updated in lock-step. Reviewer outputs at .kr/runtime/structural_audit_codex_cli_item16_precommit_ 20260421.md and .kr/runtime/domain_validation_gemini_cli_item16_ run_A_20260421.md and .kr/runtime/domain_validation_gemini_cli_ item16_run_B_20260421.md (gitignored). A follow-up Phase 5b item tracks severity reclassification (both Gemini runs flagged as AMEND that CON-SRC-0012 places "missing required-preserved evidence that upstream can re-emit" in the blocking tier, not fatal) and raise-site wiring in engines/source/src/admission.py _build_handoff_bundle (Codex DIM4 AMEND). Amended on 2026-04-23 (Phase 5b item 9 bundled with follow-up 19) to land the severity reclassification fatal → blocking on both SRC-E-HANDOFF-EVIDENCE-DROPPED and SRC-E-HANDOFF-EVIDENCE-DROPPED- NESTED error conditions. Per CON-SRC-0012 operational taxonomy, "fatal" is reserved for unrecoverable data corruption whereas "blocking" covers recoverable rejection with a correction path. Handoff-layer evidence omissions fit the blocking tier — upstream can re-emit the absent signals by re-running intake analysis (REQ-SRC-0037) on the already-frozen source, so the condition is recoverable. Gemini Run B DIM2 rationale verbatim: "Option B's HANDOFF_ prefix makes it clear this is a recoverable boundary transmission failure rather than source corruption, making it easier to correctly reason about and downgrade the severity to blocking." The HANDOFF_ prefix established in item 16 already isolated the failure mode from step-40 primary-text corruption; this amendment completes that isolation by aligning severity with CON-SRC-0012. Also amended 2026-04-23 (Phase 5b item 9) to close the ADV-010 Shamela happy-path concern: the atom's existing postconditions (when not populated the key is present with value null, recursive D-023 preservation) already protect the Shamela mushaf case where edition_info, muhaqiq_output, publisher, and matn_embedding_style are legitimately absent — Pydantic v2's default model_dump(mode="json") without exclude_none=True serializes Optional=None fields as null-valued JSON keys, not omissions. AC-8 added to provide the missing spec-linked proof that the Shamela happy-path actually satisfies the null-key contract today: a deterministic test constructs a SourceMetadata with all Shamela-legitimately-absent signals set to None, calls the admission flow, and asserts the JSON surface contains every one of the 17 required-preserved signal keys with null values for the absent ones. Without AC-8, a future exclude_none=True added to a model_dump call would silently break the contract and no spec-linked test would catch it. The raise-site wiring in admission.py _build_handoff_bundle for the positive error-raise path remains tracked as follow-up item 20 — this amendment lands the severity change and the Shamela happy-path assertion only. Closure-wave amendment 2026-04-23 (Codex CAF-7 + CAF-8, Run A DVF-4, closure of follow-up 31 on path a): (a) narrowed the required-preserved signal set from 17 to 15 by removing the edition_group_id and holding_id entries — those linkage IDs live on the EditionGroup (contracts.py:880) and EditionHolding (contracts.py:893) models and the NormalizationHandoffBundle (contracts.py:1082) does not carry either model; admission constructs the bundle BEFORE reconcile_holdings runs, so those IDs are unpopulated at the surface this atom governs. Their D-023 preservation is governed by DEC-SRC-0018 EditionHolding and DEC-SRC-0020 supersession, not here. The previous 17-signal wording was paper-reconciliation drift — surfaced by the AC-8 Shamela null-key test when the bundle JSON came back without edition_group_id / holding_id keys. Follow-up 31 is CLOSED by this amendment on the structurally-preferred path (a). (b) Documented that the CON-SRC-0012 "blocking" severity applies at the atom-semantics layer only for now — the runtime ErrorSeverity enum at contracts.py:290-293 still carries only {FATAL, WARNING, INFO}. Handoff-evidence conditions remain exception-only at the code surface until follow-up 20 adds the raise-site wiring in admission.py _build_handoff_bundle and either extends the ErrorSeverity enum to include BLOCKING or documents why the exception path suffices. Codex CAF-7 noted this runtime-vs-atom gap; Phase 5b closes without addressing it operationally because no raise-site exists yet. (c) Added the Arabic-localization constraint for "blocking" — إيقاف مؤقت (īqāf muʾaqqat) is the required translation of the pipeline-pause semantics; رد (radd) is forbidden because it carries hadith-science substantive-rejection meaning (cf. Ibn al-Ṣalāḥ Muqaddima on inqiṭāʿ vs temporal delays). The HANDOFF_ prefix + إيقاف مؤقت localization together preserve the scholarly boundary between pipeline logistics and hadith- science إعلال / جرح / تضعيف (Run A DVF-4 closure).
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - D-023 metadata preservation — the governing rule — applies to every signal listed below AND recursively to every nested structured field within those signals. Absent top-level signals serialize as null-valued keys; absent sub-fields inside nested structures (e.g., muhaqiq_output.death_date, work_relationships[i].target_work_author) likewise serialize as null-valued keys, never omitted.
  - The required-preserved signal set on SourceMetadata is {title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, genre_dispute, author_output} — 14 signals — plus {contains_isnad_chains} on the intake_dossier surface, for 15 signals total on surfaces this atom governs. Any change to this set must amend this atom's postconditions and acceptance_criteria in lock-step. author_output was added on 2026-04-21 per 3-way AMEND consensus (Codex CLI + Gemini CLI 2 runs) after the retroactive review of commit bf4354399 — author_output.positions is the canonical depth-2 list-item Optional structure in the classical tahqiq domain, so AC-7's list-item D-023 recursion test targets it rather than muhaqiq_output.positions (aspirational, see source field). The edition_group_id and holding_id linkage signals — listed in earlier drafts of this atom — are NOT SourceMetadata fields in the current typed data model (contracts.py:880 EditionGroup.edition_group_id, contracts.py:893 EditionHolding.holding_id) and the NormalizationHandoffBundle (contracts.py:1082) does not carry EditionGroup or EditionHolding objects. Admission constructs the handoff bundle BEFORE reconcile_holdings runs, so those IDs are not yet populated at the surface this atom governs. Their D-023 preservation is delegated to the registry/reconciliation surface (DEC-SRC-0018 EditionHolding, DEC-SRC-0020 supersession). Closure-wave amendment 2026-04-23 (Codex CAF-8, follow-up 31 resolved on path a) narrowed the signal set from 17 to 15 to match the actual handoff surface; the previous 17-signal phrasing was paper-reconciliation drift surfaced by the AC-8 Shamela null-key test.
  - SourceMetadata.title_arabic is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.genre is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.science_scope is serialized in the handoff payload with the exact list populated upstream.
  - SourceMetadata.is_multi_layer is serialized in the handoff payload with the exact boolean populated upstream.
  - SourceMetadata.structural_format is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.edition_info is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (edition_label, edition_year, imprint_city, tahqiq_version) honors the same rule.
  - SourceMetadata.publisher is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.muhaqiq_output is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (name, status, positions, death_date, attribution_confidence) honors the same rule.
  - SourceMetadata.page_layout_hint is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.matn_embedding_style is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.pdf_text_layer_status is serialized in the handoff payload; when not populated (non-PDF source) the key is present with value null.
  - SourceMetadata.volume_count is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.genre_dispute is serialized in the handoff payload with recursive D-023 preservation; when not populated (no disputed secondary genre) the key is present with value null; when populated, each alternate-genre position (genre_candidate, supporting_evidence, confidence) honors the same rule.
  - SourceMetadata.author_output is serialized in the handoff payload with recursive D-023 preservation; author_output is a mandatory SourceMetadata field per CON-SRC-0004 so the top-level key is always present with a populated object; each entry in author_output.positions (AuthorOutputPosition per contracts.py:676-712) is a structured object whose Optional sub-fields (canonical_id, canonical_match_name, full_name_lineage, ism, kunya, death_hijri, death_hijri_verification, among others) honor the same recursive rule — absent sub-fields serialize as null-valued keys at the list-item level, never omitted. This is the depth-2 list-item D-023 recursion case exercised by AC-7.
  - intake_dossier.contains_isnad_chains is propagated into the normalization handoff bundle unchanged; when not populated the key is present with value null.
  - No evidence signal listed above is omitted from the payload — absent values serialize as null per D-023 metadata preservation, at every structural depth.
- Acceptance criteria:
  - AC-1 [integration] Given A fully populated intake for tests/fixtures/shamela_real/06_usul/book.htm with title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, genre_dispute, author_output, and intake_dossier.contains_isnad_chains all populated; When source admission and normalization handoff packaging executes; Then The serialized payload contains every signal from the 15-signal required-preserved set with the exact values populated upstream, no signal is omitted, and every nested sub-field is either populated with its exact value or serialized as null..
  - AC-2 [deterministic] Given A source whose muhaqiq_output is legitimately absent (for example a Shamela source without a critical-edition muhaqqiq); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key muhaqiq_output with value null (not omitted)..
  - AC-3 [deterministic] Given A handoff packaging path that would have dropped the edition_info key entirely from the serialized payload; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED and no partial bundle is emitted..
  - AC-4 [integration] Given A source whose metadata deliberation produced genre_dispute populated with two alternate-genre positions (genre_candidate_1 + supporting_evidence_1 + confidence_1; genre_candidate_2 + supporting_evidence_2 + confidence_2); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key genre_dispute with both alternate positions preserved intact — neither the top-level genre_dispute key nor any nested sub-field (genre_candidate, supporting_evidence, confidence) is omitted..
  - AC-5 [integration] Given A source whose intake_dossier.contains_isnad_chains was populated true during intake analysis (for example, a hadith collection processed through REQ-SRC-0019); When source admission and normalization handoff packaging executes; Then The serialized handoff bundle contains intake_dossier.contains_isnad_chains=true, propagated unchanged from the intake_dossier surface..
  - AC-6 [deterministic] Given A handoff packaging path that would have serialized muhaqiq_output as a nested object with its `death_date` sub-field KEY absent (rather than set to null) because the upstream deliberation did not populate it; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED identifying muhaqiq_output.death_date as the omitted sub-field and no partial bundle is emitted..
  - AC-7 [deterministic] Given A handoff packaging path where author_output.positions is a non- empty list of AuthorOutputPosition entries (the canonical multi- position attribution shape established at contracts.py:676-712 for disputed authorship across نُسَخ / manuscript witnesses) and the first position element has its `death_hijri` sub-field KEY absent (rather than set to null) because the upstream multi-model consensus did not populate a death-date for that candidate-author position — the depth-2 case where the Optional sub-field is nested inside a list item rather than nested directly as a scalar child of a top-level signal (AC-6 covers the direct-child scalar case; AC-7 covers the list-item field that Pydantic exclude_unset can silently drop when iterating list elements). Path choice rationale: all three retroactive-review evaluators (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way consensus that author_output.positions[].death_ hijri is the scholarly- and structurally-correct depth-2 list- item path — authorship disputes across manuscripts produce competing multi-position attributions with per-position death dates in classical tahqiq practice, whereas muhaqqiqs act as a unified entity on the title page of a critical edition and do not carry multi-position attributions.; When handoff packaging executes; Then The packaging is aborted with SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED identifying author_output.positions[0].death_hijri as the omitted sub-field and no partial bundle is emitted..
  - AC-8 [deterministic] Given A Shamela mushaf-style SourceMetadata where the four signals Shamela legitimately lacks — edition_info, muhaqiq_output, publisher, matn_embedding_style — are all set to None, along with the other Optional SourceMetadata signals page_layout_hint, pdf_text_layer_status (non-PDF source), and genre_dispute that may also be legitimately absent for a Shamela intake. Every mandatory signal on SourceMetadata is populated normally (title_arabic, genre, science_scope, is_multi_layer, structural_format, volume_count, author_output, and the intake_dossier contains_isnad_chains surface); When source admission and normalization handoff packaging executes and the resulting bundle is serialized via Pydantic model_dump(mode="json") — the default serialization mode used by admission.py _build_handoff_bundle without exclude_none or exclude_unset overrides; Then The serialized JSON payload contains every key from the 15-signal required-preserved set (14 SourceMetadata fields + 1 intake_dossier field). Legitimately-absent Optional signals (edition_info, muhaqiq_output, publisher, matn_embedding_style, page_layout_hint, pdf_text_layer_status) appear as keys with value null; genre_dispute appears as an empty list. The null-key contract from REQ-SRC-0046 postconditions is satisfied by Pydantic v2 default serialization of Optional= None fields as JSON null. No SRC-E-HANDOFF-EVIDENCE-DROPPED or SRC-E-HANDOFF-EVIDENCE-DROPPED-NESTED error is raised. (edition_group_id and holding_id are NOT asserted on the SourceMetadata surface — they live on EditionGroup and EditionHolding models governed by DEC-SRC-0018/DEC-SRC-0020; the 17→15 signal-set narrowing per closure-wave 2026-04-23 Codex CAF-8 removes them from this atom's scope.) This AC closes the ADV-010 Shamela happy-path concern by providing the spec-linked proof that the null-key contract is operational on Shamela mushaf intakes — and it guards against a future exclude_none=True argument silently breaking the contract in a model_dump call..
