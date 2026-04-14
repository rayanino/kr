# Source Spec Atoms by Topic: acquisition

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| CON-SRC-0001 | constraint | Shamela HTML and PDF are production formats | confirmed | high |
| DEC-SRC-0001 | decision | Owner hints are cross-validation, not primary data | proposed | critical |
| INV-SRC-0001 | invariant | Owner hints never bias inference | proposed | critical |
| OF-SRC-0001 | feedback | Collection unchanged for source intake | confirmed | high |
| OF-SRC-0002 | feedback | Drop-and-go intake with optional hints | confirmed | critical |
| REQ-SRC-0001 | requirement | Autonomous source acquisition | proposed | critical |
| REQ-SRC-0002 | requirement | Optional owner hints as cross-validation | proposed | high |
| REQ-SRC-0017 | requirement | Multi-volume directory intake | proposed | critical |
| REQ-SRC-0020 | requirement | Plain text source intake | proposed | medium |
| REQ-SRC-0021 | requirement | PDF format detection and routing | proposed | critical |

### CON-SRC-0001 — Shamela HTML and PDF are production formats
- Type: constraint
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Derived from OF-SRC-0001; amended per OWNER_SANITY_CHECK_ANSWERS.md Q10 and 2026-04-14 PDF format directive
- Rule: Production source intake must support Shamela HTML and PDF inputs, while plain text remains a minimal-metadata test format rather than a production collection format.

### DEC-SRC-0001 — Owner hints are cross-validation, not primary data
- Type: decision
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002
- Chosen option: OPT-B — Hints as cross-validation signals
- Decision rationale: This matches the owner's drop-and-go workflow and preserves inference independence.

### INV-SRC-0001 — Owner hints never bias inference
- Type: invariant
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002 and OF-SRC-0005; amended per contract-architect-review.yaml
- Rule: Hint comparison may inspect only inferred_metadata.author_name, inferred_metadata.genre, and inferred_metadata.science_scope after base inference finishes.

### OF-SRC-0001 — Collection unchanged for source intake
- Type: feedback
- Status: confirmed
- Priority: high
- Confidence: high
- Source: Owner interview batch 1 question 1
- Interview question: What changed about the source collection and intake formats?
- Owner answer: Collection unchanged. The source engine still targets the same ~2,519 Shamela HTML books, with no new production sources added.

### OF-SRC-0002 — Drop-and-go intake with optional hints
- Type: feedback
- Status: confirmed
- Priority: critical
- Confidence: high
- Source: Owner interview batch 1 question 2
- Interview question: How much manual structure should the owner provide at intake time?
- Owner answer: The owner wants drop-and-go intake. Optional fields such as author or science are allowed as hints only, never as primary data. Matching hints boost confidence; diverging hints trigger investigation.

### REQ-SRC-0001 — Autonomous source acquisition
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OF-SRC-0002; amended per contract-architect-review.yaml, adversary-review.yaml ADV-001, and 2026-04-14 PDF format directive
- Trigger: Owner submits a single filesystem path for source intake.
- Postconditions:
  - File input writes source_metadata.source_id, source_metadata.source_sha256, source_metadata.frozen_blob_path, source_metadata.registry_entry_id, and source_metadata.source_format.
  - .htm or .html file input sets source_metadata.source_format=shamela_html.
  - .pdf file input sets source_metadata.source_format=pdf_scanned when extracted_text_area_ratio < 0.10 and sets source_metadata.source_format=pdf_text_embedded when extracted_text_area_ratio >= 0.10.
  - .txt file input sets source_metadata.source_format=plain_text.
  - Directory input routes to REQ-SRC-0017 and never emits SRC-E-DIRECTORY-INPUT.
  - The written source_metadata.source_sha256 is linked to source_metadata.registry_entry_id for duplicate detection.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When source engine intake executes; Then source_metadata.source_id is non-empty, source_metadata.source_sha256 is a 64-character SHA-256 hex digest, source_metadata.frozen_blob_path is non-empty, source_metadata.registry_entry_id is non-empty, and source_metadata.source_format="shamela_html"..
  - AC-2 [deterministic] Given Missing path tests/fixtures/shamela_real/does_not_exist/book.htm; When source engine intake executes; Then Intake aborts with error_code=SRC-E-PATH-NOT-FOUND..
  - AC-3 [deterministic] Given Directory path tests/fixtures/shamela_real/11_multi_small; When source engine intake executes; Then The request routes to REQ-SRC-0017 and does not emit error_code=SRC-E-DIRECTORY-INPUT..
  - AC-4 [deterministic] Given A 0-byte HTML file at a valid temporary intake path; When source engine intake executes; Then Intake aborts with error_code=SRC-E-EMPTY-FILE..
  - AC-5 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after the same file has already been frozen once; When source engine intake executes again; Then Intake aborts with error_code=SRC-E-DUPLICATE-INGEST..
  - AC-6 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When source engine intake executes; Then The request routes to REQ-SRC-0021 and source_metadata.source_format="pdf_text_embedded"..
  - AC-7 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When source engine intake executes; Then The request routes to REQ-SRC-0020 and source_metadata.source_format="plain_text"..

### REQ-SRC-0002 — Optional owner hints as cross-validation
- Type: requirement
- Status: proposed
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

### REQ-SRC-0017 — Multi-volume directory intake
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Added from adversary-review.yaml ADV-001
- Trigger: Owner submits a directory path containing numbered .htm volume files for intake.
- Postconditions:
  - All numbered volume files are frozen under one source_metadata.source_id and one source_metadata.registry_entry_id.
  - source_metadata.volume_count equals the number of frozen numbered volume files and is at least 2.
  - source_metadata.source_sha256 stores the composite hash of the numbered volume files.
  - source_metadata.frozen_blob_path points to the immutable frozen directory for the shared source_id.
  - When non-numbered .htm files are present, interactive intake prompts for supplementary inclusion and non-interactive intake auto-skips those files while recording supplementary_file_decision.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/11_multi_small; When intake executes; Then All .htm volumes are frozen under one source_metadata.source_id, source_metadata.volume_count=3, and exactly one source_metadata.registry_entry_id is written..
  - AC-2 [deterministic] Given A directory containing only non-numbered .htm files; When intake executes; Then Intake aborts with error_code=SRC-E-EMPTY-DIRECTORY..
  - AC-3 [deterministic] Given A directory containing 001.htm, 002.htm, and appendix.htm while interaction is unavailable; When intake executes; Then source_metadata.volume_count=2 and supplementary_file_decision.mode="auto_skip"..

### REQ-SRC-0020 — Plain text source intake
- Type: requirement
- Status: proposed
- Priority: medium
- Confidence: high
- Source: Added from adversary-review.yaml ADV-011
- Trigger: Owner submits a .txt file path.
- Postconditions:
  - source_metadata.source_id, source_metadata.source_sha256, source_metadata.frozen_blob_path, and source_metadata.registry_entry_id are written from the submitted file bytes.
  - source_metadata.title_arabic equals the first non-empty line of the file.
  - The full file content, including the title line, is passed to metadata inference as plain_text_content.
  - source_metadata.source_sha256 is computed from the submitted .txt file bytes.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/alfiyyah_versified/alfiyyah.txt; When intake executes; Then source_metadata.title_arabic="متن الفية ابن مالك فى علم النحو والصرف"..

### REQ-SRC-0021 — PDF format detection and routing
- Type: requirement
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from OWNER_SANITY_CHECK_ANSWERS.md Q10 and the 2026-04-14 PDF format directive
- Trigger: A .pdf file is submitted for intake.
- Postconditions:
  - source_metadata.source_format is set to pdf_scanned when extracted_text_area_ratio < 0.10.
  - source_metadata.source_format is set to pdf_text_embedded when extracted_text_area_ratio >= 0.10.
  - source_metadata.text_extraction_method is set to direct_text_extraction when source_metadata.source_format=pdf_text_embedded.
  - OCR routing is triggered when source_metadata.source_format=pdf_scanned.
  - source_metadata.page_count_physical is set from the PDF page count.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf; When PDF format detection runs; Then source_metadata.source_format="pdf_scanned" and source_metadata.page_count_physical=398..
  - AC-2 [integration] Given tests/fixtures/waraqat_usul/waraqat.pdf; When PDF format detection runs; Then source_metadata.source_format="pdf_text_embedded", source_metadata.text_extraction_method="direct_text_extraction", and source_metadata.page_count_physical=13..
  - AC-3 [deterministic] Given A corrupted or password-protected PDF at a valid temporary intake path; When PDF format detection runs; Then Intake aborts with error_code=SRC-E-PDF-CORRUPT..
