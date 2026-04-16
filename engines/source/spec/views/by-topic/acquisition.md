# Source Spec Atoms by Topic: acquisition

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML and PDF are production formats | confirmed | high |
| CON-SRC-0007 | constraint | Source type extensibility | confirmed | high |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | confirmed | critical |
| DEC-SRC-0017 | decision | NFKC normalization allowed at PDF extraction boundary | confirmed | critical |
| INV-SRC-0001 | invariant | Owner hints never bias inference | confirmed | critical |
| OF-SRC-0001 | feedback | Collection unchanged for source intake | confirmed | high |
| OF-SRC-0002 | feedback | Drop-and-go intake with optional hints | confirmed | critical |
| REQ-SRC-0001 | requirement | Upload receipt and raw submission registration | confirmed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | confirmed | high |
| REQ-SRC-0017 | requirement | Multipart Shamela container classification | confirmed | critical |
| REQ-SRC-0020 | requirement | Plain text container classification | confirmed | medium |
| REQ-SRC-0021 | requirement | PDF intake analysis and text-layer quality classification | confirmed | critical |
| REQ-SRC-0041 | requirement | Format-agnostic multi-volume folder classification | confirmed | critical |

### CON-SRC-0001 — Shamela HTML and PDF are production formats
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001; amended per OWNER_SANITY_CHECK_ANSWERS.md Q10, reference/pdf_fixture_observations_2026-04-14.md, and owner cross-validation on 2026-04-14 that normalization owns PDF-to-text conversion
- Rule: Production source intake must support Shamela HTML and PDF inputs, while plain text remains a minimal-metadata test format rather than a production collection format.

### CON-SRC-0007 — Source type extensibility
- Type: constraint
- Layer: contracts
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview 2026-04-14 identifying YouTube transcripts as the third most valuable source type after Shamela and PDF, requiring the architecture to accommodate new formats without restructuring
- Rule: The container classification step (step 30) must be designed so that adding a new source format requires only registering a new classifier and normalization route, without modifying existing classifiers or restructuring the pipeline. Current formats are shamela_html, pdf, and plain_text. Future formats include but are not limited to lecture_transcript. Container classification routes each format to normalization via a configurable normalization_route field on the classification output, not via hardcoded format-specific branching.

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### DEC-SRC-0017 — NFKC normalization allowed at PDF extraction boundary
- Type: decision
- Layer: architecture
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Empirical finding from pdf_collection_characterization_2026-04-14.md. 10/10 sampled PDFs store Arabic text in Unicode Presentation Forms (U+FB50-FEFF), not standard Arabic (U+0600-06FF). NFKC normalization deterministically recovers standard Arabic from Presentation Forms without altering scholarly content.
- Chosen option: OPT-B — Allow NFKC at PDF extraction boundary only
- Decision rationale: Grounded in empirical evidence from 10 real PDFs. NFKC is not altering scholarly content — it is recovering actual characters from rendering-layer artifacts. The distinction between rendering normalization and content normalization is clear and documentable.

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Layer: quality
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

### OF-SRC-0001 — Collection unchanged for source intake
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 1 question 1
- Interview question: What changed about the source collection and intake formats?
- Owner answer: Collection unchanged. The source engine still targets the same ~2,519 Shamela HTML books, with no new production sources added.

### OF-SRC-0002 — Drop-and-go intake with optional hints
- Type: feedback
- Layer: evidence
- Step: n/a
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 2
- Interview question: How much manual structure should the owner provide at intake time?
- Owner answer: The owner wants drop-and-go intake. Optional fields such as author or science are allowed as hints only, never as primary data. Matching hints boost confidence; diverging hints trigger investigation.

### REQ-SRC-0001 — Upload receipt and raw submission registration
- Type: requirement
- Layer: pipeline
- Step: upload_receipt
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002; re-scoped on 2026-04-14 after owner correction that upload, intake analysis, and later source acceptance must be distinct stages.
- Trigger: The owner submits one filesystem path for source-engine processing.
- Postconditions:
  - A raw_upload_record is written with non-null submission_id, submitted_path, submitted_path_kind, intake_mode, and receipt_timestamp.
  - raw_upload_record.status is set to received.
  - Owner hints are preserved as raw_upload_record.owner_hint_payload without being used as primary inference at this step.
  - No source_id, source_sha256, frozen_blob_path, source_metadata, or normalization_handoff_bundle is emitted at this step.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When upload receipt executes; Then raw_upload_record.submission_id is non-empty, raw_upload_record.submitted_path_kind="file", raw_upload_record.status="received", and no source_id field exists in the upload-receipt output..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When upload receipt executes; Then raw_upload_record.submitted_path_kind="directory" and raw_upload_record.status="received"..
  - AC-3 [deterministic] Given Missing path tests/fixtures/shamela_real/does_not_exist/book.htm; When upload receipt executes; Then Upload receipt aborts with error_code=SRC-E-PATH-NOT-FOUND..
  - AC-4 [deterministic] Given A 0-byte HTML file at a valid temporary intake path; When upload receipt executes; Then Upload receipt aborts with error_code=SRC-E-EMPTY-FILE..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Layer: pipeline
- Step: metadata_deliberation
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml and adversary-review.yaml ADV-007
- Trigger: The owner submits optional intake hints together with a source path.
- Postconditions:
  - owner_hint_payload values are stored separately from inferred_metadata values.
  - Matching author_name hints may increase author_identification_confidence without changing inferred_metadata.author_name.
  - Matching genre hints may increase genre_confidence without changing inferred_metadata.genre.
  - Matching science_scope hints may increase science_scope_confidence without changing inferred_metadata.science_scope.
  - source_metadata.hint_comparison_results appends one record per compared hint with fields hint_field, hint_value, inferred_value, match, and confidence_delta.
  - Hint contradictions write hint_investigation with fields field, hint_value, inferred_value, status, and opened_reason.
- Acceptance criteria:
  - AC-1 [deterministic] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.author_name="عبد الله بن إبراهيم الزاحم"; When post-inference hint comparison executes; Then inferred_metadata.author_name remains "عبد الله بن إبراهيم الزاحم", author_identification_confidence increases, and source_metadata.hint_comparison_results contains a record with hint_field="author_name", hint_value="عبد الله بن إبراهيم الزاحم", inferred_value="عبد الله بن إبراهيم الزاحم", and match=true..
  - AC-2 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm with owner_hint_payload.genre="matn"; When post-inference hint comparison executes; Then hint_investigation.field="genre", hint_investigation.hint_value="matn", inferred_metadata.genre remains "risalah", and source_metadata.hint_comparison_results contains a record with hint_field="genre", hint_value="matn", inferred_value="risalah", and match=false..
  - AC-3 [deterministic] Given tests/fixtures/shamela_real/06_usul/book.htm with owner_hint_payload.publisher="دار الفكر"; When hint payload validation executes; Then The invalid hint key is rejected with error_code=SRC-E-HINT-FIELD and base inference still runs..

### REQ-SRC-0017 — Multipart Shamela container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-001 and tightened on 2026-04-14 to distinguish container classification from freezing and later metadata deliberation.
- Trigger: Container classification receives a frozen directory candidate whose members include .htm files.
- Postconditions:
  - container_classification.container_type is set to shamela_multi_volume_html when the manifest contains at least two numbered .htm members.
  - container_classification.container_type is set to multipart_with_supplementary when the manifest contains one or more numbered .htm members plus supplementary non-numbered .htm members.
  - container_classification.volume_manifest preserves numbered HTML members in integer-stem order.
  - container_classification.supplementary_members preserves non-numbered HTML members separately from numbered volumes.
  - container_classification.normalization_route is set to html_parse_primary.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small; When container classification executes; Then container_classification.container_type="shamela_multi_volume_html", len(container_classification.volume_manifest)=3, and container_classification.normalization_route="html_parse_primary"..
  - AC-2 [deterministic] Given A frozen directory manifest containing only appendix.htm and introduction.htm; When container classification executes; Then Classification aborts with error_code=SRC-E-EMPTY-DIRECTORY..
  - AC-3 [deterministic] Given A frozen directory manifest containing 001.htm and المقدمة.htm; When container classification executes; Then container_classification.container_type="multipart_with_supplementary", container_classification.volume_manifest[0].member_name="001.htm", and container_classification.supplementary_members[0].member_name="المقدمة.htm"..

### REQ-SRC-0020 — Plain text container classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: medium
- Confidence: high
- Source: Added from adversary-review.yaml ADV-011 and narrowed on 2026-04-14 so plain-text handling is classified and routed here, while later text interpretation belongs to later steps.
- Trigger: Container classification receives a frozen single-file candidate whose suffix is .txt.
- Postconditions:
  - container_classification.container_type is set to plain_text.
  - container_classification.normalization_route is set to plain_text_parse.
  - container_classification.text_encoding is set to utf-8.
  - intake analysis may later use the first non-empty line as title evidence, but that evidence is not finalized at this step.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When container classification executes; Then container_classification.container_type="plain_text", container_classification.normalization_route="plain_text_parse", and container_classification.text_encoding="utf-8"..

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

### REQ-SRC-0041 — Format-agnostic multi-volume folder classification
- Type: requirement
- Layer: pipeline
- Step: container_classification
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner correction 2026-04-15 that multi-volume handling should be format-agnostic. Single file = single volume, folder with files = multi-volume, regardless of format. PDF and plain text multi-volume folders were not covered by REQ-SRC-0017 (Shamela-only) or REQ-SRC-0020/0021 (single-file only).
- Trigger: Container classification receives a frozen directory candidate whose members are not .htm files.
- Postconditions:
  - A folder containing multiple .pdf files is classified as container_type=pdf_multi_volume. volume_manifest preserves the PDF files in filename order. normalization_route=pdf_ocr_primary or pdf_text_primary based on per-file text-layer assessment in REQ-SRC-0021.
  - A folder containing multiple .txt files is classified as container_type=plain_text_multi_volume. volume_manifest preserves the text files in filename order. normalization_route=plain_text_parse.
  - A folder containing mixed file formats is classified as container_type=mixed_format_directory with a warning. Each member's format is recorded individually.
  - The format-agnostic principle: single file submission = single-volume source. Folder submission = multi-volume source. The format of the files inside determines the processing route, but the folder-as-multi-volume pattern is universal across all formats.
  - Concatenated multi-volume PDFs (single PDF with internal volume boundaries marked by ToC entries) are detected at intake analysis (REQ-SRC-0019/REQ-SRC-0038), not at container classification. Container classification sees them as a single PDF file.
- Acceptance criteria:
  - AC-1 [deterministic] Given A frozen directory containing 3 PDF files named vol1.pdf, vol2.pdf, vol3.pdf; When container classification executes; Then container_type="pdf_multi_volume" and len(volume_manifest)=3 and volume_manifest is ordered by filename..
  - AC-2 [deterministic] Given A frozen directory containing 2 .txt files; When container classification executes; Then container_type="plain_text_multi_volume" and normalization_route="plain_text_parse"..
  - AC-3 [deterministic] Given A single PDF file submitted (not a folder); When container classification executes; Then container_type="pdf" (single-volume, not pdf_multi_volume)..
