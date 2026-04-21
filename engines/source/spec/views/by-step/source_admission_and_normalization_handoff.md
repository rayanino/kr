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
| REQ-SRC-0046 | requirement | Evidence preservation for downstream level inference | confirmed | critical |

### REQ-SRC-0007 — Level field preservation across source-engine handoff
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Derived from OF-SRC-0007; moved to step 60 on 2026-04-14 because the rule governs handoff packaging rather than metadata deliberation itself. Amended on 2026-04-16 per dr-chatgpt-level-detection-20260416.yaml (SEC-5). Further amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) explicit precondition that owner_level_override passed the CON-SRC-0011 enum-value whitelist before reaching handoff packaging; (b) new level_status (CON-SRC-0004 middle-path) must serialize alongside level — preservation contract extends to both fields. Amended on 2026-04-17 (Phase 5b item 2) to rewrite AC-1 (intermediate → mutawassiṭ), AC-3 (advanced → muntahī), and AC-5 (beginner → mubtadiʾ) in the CON-SRC-0011 classical WorkLevel vocabulary. Behaviour, preconditions, postconditions, and error conditions unchanged; the Phase-5a reviewer wave identified the English placeholders as structurally untestable because REQ-SRC-0047 now rejects them at intake against the enum whitelist.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - The handoff payload always includes the level key.
  - The handoff payload always includes the level_status key with a non-null enum value.
  - A populated level value is passed through unchanged.
  - An unknown level is serialized as null rather than omitted, paired with a non-null level_status.
  - A level value populated via owner_level_override is passed through unchanged with the same string value received at intake, paired with level_status="assigned".
  - The level_status value is passed through unchanged — handoff packaging never rewrites, defaults, or reinterprets it.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with SourceMetadata.level="mutawassiṭ" and level_status="assigned" (populated via valid owner_level_override, the classical pedagogical CON-SRC-0011 WorkLevel value equivalent to intermediate); When source-to-normalization handoff packaging executes; Then The serialized payload contains level="mutawassiṭ" and level_status="assigned", both unchanged from the upstream emission. The level value serializes as the exact CON-SRC-0011 enum string — no coercion, no translation, no case folding..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/12_multi_muq/001.htm with SourceMetadata.level=null and level_status="pending_taxonomy"; When source-to-normalization handoff packaging executes; Then The serialized payload contains the key level with value null AND the key level_status with value "pending_taxonomy", both present and neither omitted..
  - AC-3 [deterministic] Given A source whose SourceMetadata.level was populated via owner_level_override="muntahī" at intake (validated against CON-SRC-0011 WorkLevel whitelist per REQ-SRC-0047 AC-1 — the classical pedagogical WorkLevel value for the terminal / curriculum-completing student, the enum position that the earlier English placeholder "advanced" mapped to), with level_status="assigned"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level="muntahī" with the override value unchanged and level_status="assigned" unchanged..
  - AC-4 [deterministic] Given A source with genre="mushaf" (non-applicable per INV-SRC-0012), SourceMetadata.level=null, level_status="non_applicable_reference"; When source-to-normalization handoff packaging executes; Then The serialized payload contains level=null and level_status="non_applicable_reference"..
  - AC-5 [deterministic] Given A handoff packaging path that would have emitted level="mubtadiʾ" (a valid CON-SRC-0011 WorkLevel string — the classical pedagogical label for pre-malakah beginner) with level_status="pending_taxonomy" — a cross-field invariant violation per CON-SRC-0004 because a populated level requires level_status="assigned"; When handoff packaging executes; Then Packaging is rejected with SRC-E-LEVEL-STATUS-INVARIANT-VIOLATION and no partial bundle is emitted. The error surfaces the cross- field rule (populated level requires assigned status), not a validation error on the WorkLevel string itself — the level value is a valid CON-SRC-0011 enum member..

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

### REQ-SRC-0046 — Evidence preservation for downstream level inference
- Type: requirement
- Layer: pipeline
- Step: source_admission_and_normalization_handoff
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-3. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR) and the R1/R2 reviewer wave: (a) nested Optional serialization rule added — when a preserved signal carries a nested structured field (e.g. muhaqiq_output, work_relationships, display_card), the nested object MUST itself honor D-023 and serialize absent sub-fields as explicit nulls rather than omitting keys; (b) genre_dispute signal added as required-preserved per R1 finding that disputed-genre payloads currently drop the secondary positions; (c) dedicated acceptance criteria now exercise the two signals most historically dropped at handoff (contains_isnad_chains and genre_dispute); (d) depends_on corrected to include DEC-SRC-0003 and INV-SRC-0011 because the evidence-preservation contract is the mechanism that makes the downstream content-only level classification (OPT-B) possible. Amended on 2026-04-21 per Phase 5b item 14 closing the Phase 5a Adversary ADV-011 finding ("positions[0].death_date unexercised"): AC-7 added to exercise depth-2 nested Optional serialization where the Optional sub-field is nested inside a list item. AC-6 already covers depth-1 direct-child omission; AC-7 closes the structurally distinct list-item sub-field omission case that Pydantic default serialization can silently drop when exclude_unset traverses list elements. Same-day retroactive reviewer wave on commit bf4354399 (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way AMEND consensus that the originally-committed path muhaqiq_output.positions[0].death_date was both structurally aspirational (MuhaqiqAssessment in contracts.py has no positions field) and scholarly-incorrect (muhaqqiqs unify on the title page of a critical edition and do not carry multi-position attributions in classical tahqiq practice; authorship disputes across نُسَخ produce the multi-position structure, not editorial attribution). AC-7 realigned to author_output.positions[0].death_hijri — structurally grounded (AuthorOutputPosition at contracts.py:676-712 declares death_hijri as Optional[int]) and scholarly-grounded (multi-position attribution is the canonical disputed-authorship shape in Dar Ibn Hazm / Muʾassasat al-Risāla critical-edition practice). The required-preserved signal set is correspondingly expanded from 16 signals to 17 by adding author_output; its inclusion is justified by the fact that author_output is already a mandatory SourceMetadata field per CON-SRC-0004, so preservation at handoff was always implicit — this amendment makes it explicit and subjects it to the recursive D-023 rule.
- Trigger: The source engine packages SourceMetadata for the normalization handoff bundle.
- Postconditions:
  - D-023 metadata preservation — the governing rule — applies to every signal listed below AND recursively to every nested structured field within those signals. Absent top-level signals serialize as null-valued keys; absent sub-fields inside nested structures (e.g., muhaqiq_output.death_date, work_relationships[i].target_work_author) likewise serialize as null-valued keys, never omitted.
  - The required-preserved signal set is {title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute, author_output} on SourceMetadata and {contains_isnad_chains} on the intake_dossier surface — 17 signals total. Any change to this set must amend this atom's postconditions and acceptance_criteria in lock-step. author_output was added on 2026-04-21 per 3-way AMEND consensus (Codex CLI + Gemini CLI 2 runs) after the retroactive review of commit bf4354399 — author_output.positions is the canonical depth-2 list-item Optional structure in the classical tahqiq domain, so AC-7's list-item D-023 recursion test targets it rather than muhaqiq_output.positions (aspirational, see source field).
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
  - SourceMetadata.author_output is serialized in the handoff payload with recursive D-023 preservation; author_output is a mandatory SourceMetadata field per CON-SRC-0004 so the top-level key is always present with a populated object; each entry in author_output.positions (AuthorOutputPosition per contracts.py:676-712) is a structured object whose Optional sub-fields (canonical_id, canonical_match_name, full_name_lineage, ism, kunya, death_hijri, death_hijri_verification, among others) honor the same recursive rule — absent sub-fields serialize as null-valued keys at the list-item level, never omitted. This is the depth-2 list-item D-023 recursion case exercised by AC-7.
  - intake_dossier.contains_isnad_chains is propagated into the normalization handoff bundle unchanged; when not populated the key is present with value null.
  - No evidence signal listed above is omitted from the payload — absent values serialize as null per D-023 metadata preservation, at every structural depth.
- Acceptance criteria:
  - AC-1 [integration] Given A fully populated intake for tests/fixtures/shamela_real/06_usul/book.htm with title_arabic, genre, science_scope, is_multi_layer, structural_format, edition_group_id, edition_info, publisher, muhaqiq_output, page_layout_hint, matn_embedding_style, pdf_text_layer_status, volume_count, holding_id, genre_dispute, and intake_dossier.contains_isnad_chains all populated; When source admission and normalization handoff packaging executes; Then The serialized payload contains every signal from the 17-signal required-preserved set with the exact values populated upstream, no signal is omitted, and every nested sub-field is either populated with its exact value or serialized as null..
  - AC-2 [deterministic] Given A source whose muhaqiq_output is legitimately absent (for example a Shamela source without a critical-edition muhaqqiq); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key muhaqiq_output with value null (not omitted)..
  - AC-3 [deterministic] Given A handoff packaging path that would have dropped the edition_info key entirely from the serialized payload; When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED and no partial bundle is emitted..
  - AC-4 [integration] Given A source whose metadata deliberation produced genre_dispute populated with two alternate-genre positions (genre_candidate_1 + supporting_evidence_1 + confidence_1; genre_candidate_2 + supporting_evidence_2 + confidence_2); When source admission and normalization handoff packaging executes; Then The serialized payload contains the key genre_dispute with both alternate positions preserved intact — neither the top-level genre_dispute key nor any nested sub-field (genre_candidate, supporting_evidence, confidence) is omitted..
  - AC-5 [integration] Given A source whose intake_dossier.contains_isnad_chains was populated true during intake analysis (for example, a hadith collection processed through REQ-SRC-0019); When source admission and normalization handoff packaging executes; Then The serialized handoff bundle contains intake_dossier.contains_isnad_chains=true, propagated unchanged from the intake_dossier surface..
  - AC-6 [deterministic] Given A handoff packaging path that would have serialized muhaqiq_output as a nested object with its `death_date` sub-field KEY absent (rather than set to null) because the upstream deliberation did not populate it; When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED-NESTED identifying muhaqiq_output.death_date as the omitted sub-field and no partial bundle is emitted..
  - AC-7 [deterministic] Given A handoff packaging path where author_output.positions is a non- empty list of AuthorOutputPosition entries (the canonical multi- position attribution shape established at contracts.py:676-712 for disputed authorship across نُسَخ / manuscript witnesses) and the first position element has its `death_hijri` sub-field KEY absent (rather than set to null) because the upstream multi-model consensus did not populate a death-date for that candidate-author position — the depth-2 case where the Optional sub-field is nested inside a list item rather than nested directly as a scalar child of a top-level signal (AC-6 covers the direct-child scalar case; AC-7 covers the list-item field that Pydantic exclude_unset can silently drop when iterating list elements). Path choice rationale: all three retroactive-review evaluators (Codex CLI structural + Gemini CLI 2 independent scholarly runs) reached 3-way consensus that author_output.positions[].death_ hijri is the scholarly- and structurally-correct depth-2 list- item path — authorship disputes across manuscripts produce competing multi-position attributions with per-position death dates in classical tahqiq practice, whereas muhaqqiqs act as a unified entity on the title page of a critical edition and do not carry multi-position attributions.; When handoff packaging executes; Then The packaging is aborted with SRC-E-EVIDENCE-DROPPED-NESTED identifying author_output.positions[0].death_hijri as the omitted sub-field and no partial bundle is emitted..
