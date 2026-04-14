# Source Spec Atoms by Step: upload_receipt

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0001 | requirement | Upload receipt and raw submission registration | proposed | critical |

### REQ-SRC-0001 — Upload receipt and raw submission registration
- Type: requirement
- Layer: pipeline
- Step: upload_receipt
- Status: proposed
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
