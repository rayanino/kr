# Source Spec Atoms by Step: source_admission_and_normalization_handoff

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0007 | requirement | Level field preservation across source-engine handoff | confirmed | medium |
| REQ-SRC-0022 | requirement | PDF handoff preserves intake verdicts | confirmed | critical |
| REQ-SRC-0025 | requirement | Two-stage source admission and normalization handoff packaging | confirmed | critical |
| REQ-SRC-0027 | requirement | Owner-submission risk gate for study-quality threats | confirmed | critical |
| REQ-SRC-0033 | requirement | Volume count and intake timestamp derivation | confirmed | high |
| REQ-SRC-0044 | requirement | Edition-group and holding reconciliation on source admission | confirmed | critical |
| REQ-SRC-0045 | requirement | Supersession signal emission on source admission | confirmed | high |

### REQ-SRC-0007 — Level field preservation across source-engine handoff
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: medium
- Confidence: medium
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - The handoff payload always includes the level key.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with SourceMetadata.level="intermediate"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level="intermediate"..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with SourceMetadata.level=null; When source-to-normalization handoff packaging executes; Then The serialized payload contains the key level with value null..

### REQ-SRC-0022 — PDF handoff preserves intake verdicts
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and revised on 2026-04-14 so the handoff step propagates intake-analysis verdicts without performing normalization itself.
- Trigger: Source admission and normalization handoff finalize a source whose intake dossier source_format is pdf.
- Postconditions:
  - SourceMetadata.normalization_route is set to pdf_ocr_primary.
  - SourceMetadata.pdf_text_layer_status and SourceMetadata.page_count_physical are copied from the intake dossier.
  - NormalizationInput.source_format_legacy is set from SourceMetadata.source_format and SourceMetadata.pdf_text_layer_status according to the bridge contract.
  - The normalization_handoff_bundle preserves the intake dossier evidence needed to explain the PDF verdict downstream.
  - The source engine emits no normalized_text field for a PDF handoff.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="absent", SourceMetadata.page_count_physical=398, NormalizationInput.source_format_legacy="pdf_scanned", and normalization_handoff_bundle contains no normalized_text field..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="corrupt", SourceMetadata.page_count_physical=13, NormalizationInput.source_format_legacy="pdf_scanned", and normalization_handoff_bundle contains no normalized_text field..
  - AC-3 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing clean embedded text; When normalization handoff packaging executes; Then SourceMetadata.normalization_route="pdf_ocr_primary", SourceMetadata.pdf_text_layer_status="clean", NormalizationInput.source_format_legacy="pdf_text", and normalization_handoff_bundle contains no normalized_text field..

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

### REQ-SRC-0044 — Edition-group and holding reconciliation on source admission
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15). The DR identifies that the spec needs a reconciliation mechanism in step 60 (admission) that runs whenever a new source is accepted. This mechanism creates or updates EditionGroup and EditionHolding entities based on work_output and collection_match_output from metadata deliberation, enabling progressive completeness, duplicate handling, and supersession without mutating sources.
- Trigger: A source is admitted into the source_collection (REQ-SRC-0025 completes successfully with status=source_engine_accepted).
- Postconditions:
  - If collection_match_output.matched_edition_group_id exists with high confidence, attach the new source's volume slice(s) to the matching EditionHolding's VolumeHolding(s). Update VolumeHolding presence_state accordingly.
  - If no matching edition group exists or confidence is insufficient, create a new EditionGroup and EditionHolding from the source's work_output and completeness signals.
  - If the new source's edition fingerprint conflicts with the existing holding's edition fingerprint on a shared volume, do NOT silently merge. Either create a separate EditionHolding (DEC-SRC-0019) or set the conflicted VolumeHolding to presence_state=conflict.
  - EditionHolding completeness_state is recomputed after every attachment (INV-SRC-0010).
  - When a volume slot already has a present_primary source and a new source claims the same volume of the same edition, attach the new source as present_alternate, not as a replacement.
  - All reconciliation decisions (attach, create, conflict) are logged with evidence and confidence for auditability (INV-SRC-0009).
- Acceptance criteria:
  - AC-1 [deterministic] Given Volume 1 of a 3-volume work is already admitted with an EditionHolding (completeness_state=active_partial, expected_volume_count=3). A new source is admitted containing volumes 2 and 3 with matching edition fingerprint.; When Reconciliation executes after source admission.; Then The existing EditionHolding gains VolumeHolding entries for volumes 2 and 3 with presence_state=present_primary, and completeness_state transitions from active_partial to active_complete..
  - AC-2 [deterministic] Given A complete EditionHolding exists for a work. A new source is admitted containing volume 5 of the same work but from a different edition (different muhaqqiq, different publisher).; When Reconciliation executes after source admission.; Then A new EditionGroup and EditionHolding are created for the second edition, with only volume 5 present (completeness_state=active_partial). The original EditionHolding is unchanged..
  - AC-3 [deterministic] Given An EditionHolding exists with volume 1 present_primary. A new source is admitted claiming the same volume 1 of the same edition with matching fingerprint.; When Reconciliation executes after source admission.; Then The new source is attached as present_alternate for volume 1. The existing present_primary source remains primary. No data is overwritten..
  - AC-4 [deterministic] Given No existing work or edition matches exist in the collection. A new source is admitted with work_output.status=definitive.; When Reconciliation executes after source admission.; Then A new EditionGroup and EditionHolding are created from the work_output and completeness signals. The source's volume slices are attached as present_primary..
  - AC-5 [deterministic] Given A source admitted with work_output.status=insufficient_evidence (no evidence-backed work identity could be determined).; When Reconciliation executes after source admission.; Then A standalone EditionGroup and EditionHolding are created with completeness_state=indeterminate. Log entry includes unresolved_work_identity..
  - AC-6 [deterministic] Given A source with two files both labeled 'volume 1' containing different content, admitted to an existing EditionHolding.; When Reconciliation executes after source admission.; Then Both files are attached as present_alternate for volume 1. A study_quality_risk_flag with risk_type=ambiguous_volume_numbering is emitted..

### REQ-SRC-0045 — Supersession signal emission on source admission
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: high
- Confidence: high
- Source: ChatGPT DR on collection-evolution model (2026-04-15), Edge Case 4. When a better edition of an already-held work arrives, the source engine must emit supersession signals so downstream engines know which holding is preferred. This implements the pointer-based supersession model from DEC-SRC-0020.
- Trigger: Reconciliation (REQ-SRC-0044) determines that a newly admitted source represents a potentially superior edition of an already-held work.
- Postconditions:
  - If the new edition is judged superior by the deliberation agents, new_holding.preferred_rank is set to primary and old_holding.superseded_by is set to new_holding.holding_id.
  - old_holding.holding_state transitions to superseded.
  - old_holding's sources and downstream artifacts remain addressable by ID. Nothing is deleted or overwritten.
  - new_holding.supersession_policy is set based on the nature of the quality difference. For works where text quality materially affects atomization (e.g. hadith corpora where OCR errors destroy isnad parsing), supersession_policy=regen_required. For works where differences are mostly footnotes and the core matn is stable, supersession_policy=regen_optional.
  - If agents cannot determine which edition is superior, no supersession is applied. Both holdings remain active. A study_quality_risk_flag is emitted with risk_type=unresolved_edition_preference.
- Acceptance criteria:
  - AC-1 [deterministic] Given A complete EditionHolding for a hadith work exists with text_fidelity=low_ocr. A new source is admitted as a different edition of the same work with text_fidelity=high_verified, also complete.; When Supersession signal emission executes.; Then old_holding.superseded_by=new_holding_id, old_holding.holding_state=superseded, new_holding.preferred_rank=primary, new_holding.supersession_policy=regen_required..
  - AC-2 [deterministic] Given A complete EditionHolding exists. A new source is admitted as a partial holding of a potentially better edition (only 1 of 5 volumes).; When Supersession signal emission evaluates.; Then No supersession is applied. The new EditionHolding is created with completeness_state=active_partial and no preferred_rank. Advisory flag supersession_blocked_by_completeness is emitted..
  - AC-3 [deterministic] Given Two editions of the same work exist. No quality comparison evidence is available (text_fidelity signals are identical, no owner hints exist, no edition reputation signals differ).; When Supersession signal emission evaluates.; Then Neither holding is superseded. Both remain active. A study_quality_risk_flag with risk_type=unresolved_edition_preference is emitted..
