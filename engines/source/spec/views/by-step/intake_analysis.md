# Source Spec Atoms by Step: intake_analysis

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0019 | requirement | Source-work identification and collection matching | confirmed | critical |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | confirmed | critical |
| REQ-SRC-0023 | requirement | PDF text-layer evidence is diagnostic only | confirmed | critical |
| REQ-SRC-0024 | requirement | PDF page-geometry hints for normalization | confirmed | high |
| REQ-SRC-0036 | requirement | Completeness analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0037 | requirement | Integrity analysis of frozen source candidate | confirmed | critical |
| REQ-SRC-0038 | requirement | Composite work (majmu‘) detection and decomposition | confirmed | critical |
| REQ-SRC-0047 | requirement | Owner override pathway for level at intake | confirmed | medium |

### REQ-SRC-0019 — Source-work identification and collection matching
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from owner correction on 2026-04-14. Narrowed to source-work identification and collection matching after contract-architect review found 4 sub-analyses in one atom is untestable. Completeness analysis moved to REQ-SRC-0036, integrity analysis moved to REQ-SRC-0037.
- Trigger: Intake analysis receives a frozen, container-classified source candidate.
- Postconditions:
  - An intake_dossier is written with non-null dossier_id, title_evidence, work_identity_proposal, and collection_match_candidates.
  - work_identity_proposal.candidates preserves one or more evidence-backed candidate work identities without declaring them authoritative yet.
  - collection_match_candidates records whether the work matches an existing admitted source, an edition group, or has no match.
  - title_evidence preserves all title signals (metadata card title, title page text, colophon title, filename-derived title) with provenance per INV-SRC-0009.
  - Completeness analysis is handled by REQ-SRC-0036. Integrity analysis is handled by REQ-SRC-0037. Metadata deliberation consumes the combined intake_dossier from all three sub-analyses.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When source-work identification executes; Then intake_dossier.dossier_id is non-empty, len(intake_dossier.title_evidence) >= 1, len(intake_dossier.work_identity_proposal.candidates) >= 1..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When source-work identification executes; Then len(intake_dossier.work_identity_proposal.candidates) >= 1 and collection_match_candidates is present..

### REQ-SRC-0021 — PDF intake analysis and text-layer quality classification
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, owner correction on text quality, and pdf_collection_characterization_2026-04-14.md which found 10/10 sampled PDFs use Unicode Presentation Forms (not scans), recoverable via NFKC normalization.
- Trigger: Intake analysis runs on a frozen source candidate whose container_type is pdf.
- Postconditions:
  - intake_dossier.source_format is set to pdf.
  - intake_dossier.declared_vs_observed_counts.physical_page_count is set from the PDF page count.
  - intake_dossier.pdf_text_layer_status is set to absent when sampled content pages yield no extractable visible text.
  - intake_dossier.pdf_text_layer_status is set to corrupt when sampled pages yield extractable text but the text-layer assessment rejects that text as unusable even after NFKC normalization.
  - intake_dossier.pdf_text_layer_status is set to presentation_forms when sampled pages yield text in Unicode Presentation Forms (U+FB50-FDFF, U+FE70-FEFF) that becomes intelligible standard Arabic after NFKC normalization.
  - intake_dossier.pdf_text_layer_status is set to clean when sampled pages yield extractable text already in standard Arabic (U+0600-06FF) that is intelligible without normalization.
  - intake_dossier.normalization_route is set to pdf_ocr_primary when pdf_text_layer_status in {absent, corrupt}. intake_dossier.normalization_route is set to pdf_text_primary when pdf_text_layer_status in {presentation_forms, clean}.
  - intake_dossier.pdf_text_encoding records the detected Unicode block profile: standard_arabic, presentation_forms, or mixed. This signals normalization whether NFKC is needed at the extraction boundary.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="absent", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=398..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="corrupt", intake_dossier.normalization_route="pdf_ocr_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=13..
  - AC-3 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When intake analysis executes; Then intake_dossier.source_format="pdf", intake_dossier.pdf_text_layer_status="clean", intake_dossier.normalization_route="pdf_text_primary", and intake_dossier.declared_vs_observed_counts.physical_page_count=1..
  - AC-4 [deterministic] Given A corrupted or password-protected PDF at a valid temporary intake path; When intake analysis executes; Then Intake analysis aborts with error_code=SRC-E-PDF-CORRUPT..

### REQ-SRC-0023 — PDF text-layer evidence is diagnostic only
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md, .claude/skills/arabic-text/SKILL.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Trigger: The source engine records sampled direct-extraction evidence from a PDF for text-layer classification.
- Postconditions:
  - intake_dossier.pdf_text_evidence preserves the literal extracted string and its physical page number.
  - No Unicode normalization in {NFC, NFD, NFKC, NFKD} is applied to sampled direct-extraction evidence.
  - Sampled direct-extraction evidence is diagnostic only and is never emitted as normalized handoff text by the source engine.
  - The presence of diacritics inside sampled direct-extraction evidence does not override intake_dossier.pdf_text_layer_status="corrupt" when the text-layer assessment rejects the text as unusable.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/waraqat_usul/waraqat.pdf; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "منت الورقات إلماـ احلرمني أيب ادلعايل اجلويين" with its physical page number and intake_dossier.pdf_text_layer_status="corrupt"..
  - AC-2 [deterministic] Given A temporary PDF generated during the test run with one Arabic page containing the literal string "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ" as embedded text; When sampled direct-extraction evidence is recorded; Then One preserved sampled string equals "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ", intake_dossier.pdf_text_layer_status="clean", and the handoff contains no normalized_text field..

### REQ-SRC-0024 — PDF page-geometry hints for normalization
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Added from reference/pdf_fixture_observations_2026-04-14.md and revised on 2026-04-14 after confirming that source-engine PDF handling must stay metadata-first and normalization-owned for text extraction
- Trigger: A PDF source is being processed.
- Postconditions:
  - intake_dossier.page_layout_hint is set to single_column, dual_column, marginal_notes, or mixed when the intake-time geometry is sufficient.
  - layout_analysis.main_text_stream_hint and layout_analysis.marginal_text_stream_hint are identified separately when intake_dossier.page_layout_hint=marginal_notes.
  - layout_analysis.reading_order_hint is set to rtl_columns when intake_dossier.page_layout_hint=dual_column.
  - intake_dossier.page_layout_hint remains optional and non-authoritative until normalization confirms page layout on extracted text.
- Acceptance criteria:
  - AC-1 [deterministic] Given A PDF page with visible حاشية blocks in the outer margin alongside the main sharh text; When layout detection runs; Then intake_dossier.page_layout_hint="marginal_notes"..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When layout detection runs; Then intake_dossier.page_layout_hint="single_column"..

### REQ-SRC-0036 — Completeness analysis of frozen source candidate
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Decomposed from REQ-SRC-0019 per contract-architect review finding that 4 sub-analyses in one atom is untestable.
- Trigger: Intake analysis assesses completeness of a frozen, container-classified source candidate.
- Postconditions:
  - completeness_status is written as one of: complete, partial, mixed, indeterminate.
  - self_containment_assessment is written as one of: self_contained, partially_self_contained, context_dependent.
  - cross_volume_dependency_assessment records whether missing volumes are: non_material, material, unknown.
  - parent_work_presence_model records whether the uploaded material appears to be part of a larger work, and which volumes are present or missing when that can be inferred.
  - declared_vs_observed_counts preserves any count comparison evidence (e.g. declared_volume_count vs observed_volume_count) used by completeness analysis.
  - holding_completeness_delta is an optional SourceMetadata field (CON-SRC-0004) that records what new volume coverage this source would add to a matching EditionHolding, if any. This is computed from comparing the source's volume_coverage against the existing holding's VolumeHolding states. If no matching holding exists, holding_completeness_delta is null. This field enables INV-SRC-0010 (computed holding completeness) by providing the incremental contribution signal.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small (3-volume directory); When completeness analysis executes; Then declared_vs_observed_counts.observed_volume_count=3 and completeness_status is one of {complete, indeterminate}..
  - AC-2 [deterministic] Given A frozen source candidate whose title page and file naming indicate 'الجزء الثاني' with no companion parts present; When completeness analysis executes; Then completeness_status=partial, self_containment_assessment is not self_contained, partiality_reasons includes single_part_without_companion_parts..
  - AC-3 [integration] Given A single-file Shamela book with no volume indicators (e.g. tests/fixtures/shamela_real/03_fiqh/book.htm); When completeness analysis executes; Then completeness_status=complete, self_containment_assessment=self_contained, cross_volume_dependency_assessment=non_material..

### REQ-SRC-0037 — Integrity analysis of frozen source candidate
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Decomposed from REQ-SRC-0019 per contract-architect review finding that 4 sub-analyses in one atom is untestable.
- Trigger: Intake analysis assesses structural integrity of a frozen, container-classified source candidate.
- Postconditions:
  - integrity_status is written as one of: sound, suspicious, corrupt.
  - study_quality_risk_flags is a list preserving every uncertainty that could materially affect study quality (e.g. encoding_anomaly, truncated_content, missing_basmala, garbled_diacritics).
  - contains_isnad_chains is a boolean set to true when transmission formulas (per INV-SRC-0006) are detected in the source text.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm (well-formed Shamela HTML); When integrity analysis executes; Then integrity_status=sound, study_quality_risk_flags is empty..
  - AC-2 [deterministic] Given A frozen PDF source with embedded null bytes and invalid UTF-8 sequences in text layer; When integrity analysis executes; Then integrity_status=corrupt, SRC-E-INTEGRITY-CORRUPT error is raised..
  - AC-3 [deterministic] Given A hadith fixture containing transmission formulas (حدثنا، أخبرنا، سمعت); When integrity analysis executes; Then contains_isnad_chains=true..

### REQ-SRC-0038 — Composite work (majmu‘) detection and decomposition
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Claude DR spec audit 2026-04-15 finding that majmu' collections (e.g. 37-volume compilations containing hundreds of independent risalahs) demand whole-part decomposition. Both Shamela and OpenITI treat the entire majmu' as a single entry. The source engine must detect and decompose.
- Trigger: Intake analysis examines a source candidate whose title, structure, or volume count suggests it is a composite collection (majmu').
- Postconditions:
  - intake_dossier.composite_work_type is set to one of: majmu, possible, or null.
  - When title evidence contains keywords indicating a composite collection (e.g. مجموع, فتاوى as collection title, رسائل as collection title) or structural signals indicate a composite work (high volume count with heterogeneous internal titles), composite_work_type is set to majmu.
  - For detected majmu' works, intake_dossier.sub_work_inventory is a list where each entry contains: sub_title (string), volume_number (int or null), page_start (int or null), page_end (int or null), and detection_method (one of toc_entry, volume_boundary, structural_signal).
  - The source engine creates a parent work record for the collection AND preserves sub_work_inventory for downstream engines to use during passaging and atomization.
  - Sub-work detection is best-effort from structural signals (table of contents, volume boundaries, internal bismillah/hamdala patterns). Complete decomposition may require normalization engine assistance.
  - Non-composite works have composite_work_type set to null and sub_work_inventory as an empty list.
- Acceptance criteria:
  - AC-1 [integration] Given A source with title "مجموع فتاوى ابن تيمية" spanning 37 volumes; When intake analysis runs composite detection; Then composite_work_type="majmu", sub_work_inventory is non-empty, each entry has sub_title and detection_method..
  - AC-2 [deterministic] Given A standard single-author monograph ("أحكام الاضطباع والرمل في الطواف") with 1 volume; When intake analysis runs composite detection; Then composite_work_type=null, sub_work_inventory is an empty list..
  - AC-3 [integration] Given A source titled "رسائل ابن رجب" with 1 volume but internal structural boundaries between distinct treatises; When intake analysis runs composite detection; Then composite_work_type="majmu" (detected via structural_signal), sub_work_inventory contains entries with detection_method="structural_signal"..
  - AC-4 [deterministic] Given A source titled "رسائل" with 1 volume and no detectable internal sub-work boundaries; When intake analysis runs composite detection; Then composite_work_type="possible", study_quality_risk_flags includes "ambiguous_composite_detection"..

### REQ-SRC-0047 — Owner override pathway for level at intake
- Type: requirement
- Layer: pipeline
- Step: intake_analysis
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Initial formulation on 2026-04-16 from dr-chatgpt-level-detection-20260416.yaml SEC-4. Amended on 2026-04-17 after the 3-of-3 unanimous OPT-B adjudication (Codex CLI, Gemini CLI runs 1 and 2, Gemini DR): (a) error severity downgraded fatal → blocking per reviewer finding that an invalid override should reject the override but not terminate intake (intake proceeds with level=null, level_status=pending_taxonomy); (b) three distinct error conditions now distinguish absent vs empty vs invalid override values (previously conflated); (c) audit-trail entry structure enriched to include the raw override token, the validation verdict, and the enum-value whitelist that was applied; (d) integrates with the CON-SRC-0004 middle-path level_status field.
- Trigger: The owner supplies an optional level override on a RawUploadRecord or equivalent intake surface when admitting a new source.
- Postconditions:
  - When owner_level_override is absent (the field is not present on the intake payload), SourceMetadata.level remains null and level_status is set per standard source-engine rules (pending_taxonomy for leveled genres, non_applicable_reference for non-applicable genres per INV-SRC-0012).
  - When owner_level_override is present AND the value passes the CON-SRC-0011 enum whitelist AND the genre is not in the INV-SRC-0012 non-applicable set, SourceMetadata.level is populated with the exact enum value and level_status is set to "assigned".
  - An audit-trail entry is written with provenance="owner_override", the raw override token received at intake, the validation verdict (accepted | rejected_invalid | rejected_nonapplicable | rejected_empty), the CON-SRC-0011 whitelist that was applied (enumerated snapshot), and an ISO 8601 timestamp of when the override was evaluated.
  - The override value, when accepted, survives through source admission and normalization handoff packaging unchanged (per REQ-SRC-0007 AC-3).
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm (genre="matn" or "sharh") submitted with owner_level_override="mutawassiṭ"; When intake analysis processes the raw upload; Then SourceMetadata.level="mutawassiṭ", SourceMetadata.level_status= "assigned", an audit-trail entry is recorded with provenance="owner_override", raw_token="mutawassiṭ", verdict="accepted", whitelist_applied=["mubtadiʾ", "mutawassiṭ", "muntahī"], and a non-null ISO 8601 timestamp, and the override survives normalization handoff unchanged..
  - AC-2 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm submitted with owner_level_override="expert" (not a CON-SRC-0011 WorkLevel enum value); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-INVALID, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_taxonomy", intake_analysis continues, and an audit-trail entry records raw_token="expert" and verdict="rejected_invalid"..
  - AC-3 [deterministic] Given A source with SourceMetadata.genre="mushaf" submitted with owner_level_override="mubtadiʾ"; When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE, SourceMetadata.level remains null, SourceMetadata.level_status= "non_applicable_reference", intake_analysis continues, and an audit-trail entry records verdict="rejected_nonapplicable"..
  - AC-4 [deterministic] Given A source submitted with owner_level_override="" (empty string) or owner_level_override="   " (whitespace only); When intake analysis processes the raw upload; Then The override is rejected with SRC-E-LEVEL-OVERRIDE-EMPTY, SourceMetadata.level remains null, SourceMetadata.level_status= "pending_taxonomy" (or "non_applicable_reference" per genre), and an audit-trail entry records verdict="rejected_empty"..
  - AC-5 [deterministic] Given A source submitted with no owner_level_override field present at all on the intake payload; When intake analysis processes the raw upload; Then No audit-trail entry is written for override evaluation, SourceMetadata.level remains null, SourceMetadata.level_status is set per standard source-engine rules (pending_taxonomy for leveled genres, non_applicable_reference for non-applicable genres), and intake_analysis completes without error..
