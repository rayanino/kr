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
- Source: Added from adversary-review.yaml ADV-002; amended per reference/ pdf_fixture_observations_2026-04-14.md, owner guidance on 2026-04-14 about exact source/work identification and staged source admission, and the architecture decision that normalization owns text extraction. Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication on DEC-SRC-0003: (a) added the mandatory `level_status` enum field per Gemini DR's middle- path proposal, which closes the null-conflation gap that Claude DR correctly identified without adopting OPT-C's shallow-signal level emission; (b) level_status provenance is the source engine at admission time, with values pending_taxonomy or non_applicable_reference, extended by downstream engines to assigned or unprocessable_error. See .kr/runtime/ adjudication_gemini_dr_20260417.md sections q5 and final_recommendation.
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
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-3. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR) and the R1/R2 reviewer wave: (a) nested Optional serialization rule added — when a preserved signal carries a nested structured field (e.g. muhaqiq_output, work_relationships, display_card), the nested object MUST itself honor D-023 and serialize absent sub-fields as explicit nulls rather than omitting keys; (b) genre_dispute signal added as required-preserved per R1 finding that disputed-genre payloads currently drop the secondary positions; (c) dedicated acceptance criteria now exercise the two signals most historically dropped at handoff (contains_isnad_chains and genre_dispute); (d) depends_on corrected to include DEC-SRC-0003 and INV-SRC-0011 because the evidence-preservation contract is the mechanism that makes the downstream content-only level classification (OPT-B) possible. Amended on 2026-04-21 per Phase 5b item 14 closing the Phase 5a Adversary ADV-011 finding ("positions[0].death_date unexercised"): AC-7 added to exercise depth-2 nested Optional serialization where the Optional sub-field is nested inside a list item (specifically muhaqiq_output.positions[0].death_date). AC-6 already covers depth-1 direct-child omission (muhaqiq_output.death_date); AC-7 closes the structurally distinct list-item sub-field omission case that Pydantic default serialization can silently drop when exclude_unset traverses list elements.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - D-023 metadata preservation — the governing rule — applies to every signal listed below AND recursively to every nested structured field within those signals. Absent top-level signals serialize as null-valued keys; absent sub-fields inside nested structures (e.g., muhaqiq_output.death_date, work_relationships[i].target_work_author) likewise serialize as null-valued keys, never omitted.
  - The required-preserved signal set is {title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute} on SourceMetadata and {contains_isnad_chains} on the intake_dossier surface — 16 signals total. Any change to this set must amend this atom's postconditions and acceptance_criteria in lock-step.
  - SourceMetadata.title_arabic is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.genre is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.science_scope is serialized in the handoff payload with the exact list populated upstream.
  - SourceMetadata.is_multi_layer is serialized in the handoff payload with the exact boolean populated upstream.
  - SourceMetadata.structural_format is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.edition_group_id is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.edition_info is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (edition_label, edition_year, imprint_city, tahqiq_version) honors the same rule.
  - SourceMetadata.publisher is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.muhaqiq_output is serialized in the handoff payload with recursive D-023 preservation; when not populated the key is present with value null; when populated, each of its nested sub-fields (name, status, positions, death_date, attribution_confidence) honors the same rule.
  - SourceMetadata.page_layout_hint is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.matn_embedding_style is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.pdf_text_layer_status is serialized in the handoff payload; when not populated (non-PDF source) the key is present with value null.
  - SourceMetadata.volume_count is serialized in the handoff payload with the exact value populated upstream.
  - SourceMetadata.holding_id is serialized in the handoff payload; when not populated the key is present with value null.
  - SourceMetadata.genre_dispute is serialized in the handoff payload with recursive D-023 preservation; when not populated (no disputed secondary genre) the key is present with value null; when populated, each alternate-genre position (genre_candidate, supporting_evidence, confidence) honors the same rule.
  - intake_dossier.contains_isnad_chains is propagated into the normalization handoff bundle unchanged; when not populated the key is present with value null.
  - No evidence signal listed above is omitted from the payload — absent values serialize as null per D-023 metadata preservation, at every structural depth.
- Acceptance criteria:
  - AC-1 [integration] Given A fully populated intake for tests/fixtures/shamela_real/06_usul/book.htm with title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute, and intake_dossier.contains_isnad_chains all populated; When source admission and normalization handoff packaging executes; Then The serialized payload contains every signal from the 16-signal required-preserved set with the exact values populated upstream, no signal is omitted, and every nested sub-field is either populated with its exact value or serialized as null..
  - AC-2 [deterministic] Given A source whose muhaqiq_output is legitimately absent (for example a Shamela source without a critical-edition muhaqqiq); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key muhaqiq_output with value null (not omitted)..
  - AC-3 [deterministic] Given A handoff packaging path that would have dropped the edition_info key entirely from the serialized payload; When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED and no partial bundle is emitted..
  - AC-4 [integration] Given A source whose metadata deliberation produced genre_dispute populated with two alternate-genre positions (genre_candidate_1 + supporting_evidence_1 + confidence_1; genre_candidate_2 + supporting_evidence_2 + confidence_2); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key genre_dispute with both alternate positions preserved intact — neither the top-level genre_dispute key nor any nested sub-field (genre_candidate, supporting_evidence, confidence) is omitted..
  - AC-5 [integration] Given A source whose intake_dossier.contains_isnad_chains was populated true during intake analysis (for example, a hadith collection processed through REQ-SRC-0019); When source admission and normalization handoff packaging executes; Then The serialized handoff bundle contains intake_dossier.contains_isnad_chains=true, propagated unchanged from the intake_dossier surface..
  - AC-6 [deterministic] Given A handoff packaging path that would have serialized muhaqiq_output as a nested object with its `death_date` sub-field KEY absent (rather than set to null) because the upstream deliberation did not populate it; When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED-NESTED identifying muhaqiq_output.death_date as the omitted sub-field and no partial bundle is emitted..
  - AC-7 [deterministic] Given A handoff packaging path where muhaqiq_output is populated with a non-empty positions list and the first position element has its `death_date` sub-field KEY absent (rather than set to null) because the upstream deliberation did not populate death_date for that position element — the depth-2 case where the Optional sub-field is nested inside a list item rather than nested directly as a scalar child of muhaqiq_output (AC-6 covers the direct-child scalar; AC-7 covers the list-item field that Pydantic exclude_unset can silently drop when iterating list elements); When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED-NESTED identifying muhaqiq_output.positions[0].death_date as the omitted sub-field and no partial bundle is emitted..
