# Source Spec Atoms by Topic: freezing

| ID | Type | Title | Status | Priority |
| --- | --- | --- | --- | --- |
| REQ-SRC-0018 | requirement | Freeze and manifest verification | proposed | critical |

### REQ-SRC-0018 — Freeze and manifest verification
- Type: requirement
- Layer: pipeline
- Step: freeze_and_manifest
- Status: proposed
- Priority: critical
- Confidence: high
- Source: Derived from reference/archive/v1/source_engine/reference/ABD_INTAKE_SPEC.md and archive freezer/integrity behavior, then adapted to the new raw-upload registry boundary on 2026-04-14.
- Trigger: A raw_upload_record with status=received is promoted into freeze processing.
- Postconditions:
  - A frozen_source record is written with non-null source_id, source_sha256, frozen_blob_path, and freeze_verification_status.
  - frozen_source.frozen_member_manifest records every frozen member with member_name, member_sha256, member_size_bytes, and member_kind.
  - raw_upload_record.status is set to frozen when freeze_verification_status="verified".
  - Exact duplicate detection is evaluated against frozen_source.source_sha256 before later container classification begins.
- Acceptance criteria:
  - AC-1 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm; When freeze and manifest executes; Then frozen_source.source_id is non-empty, frozen_source.source_sha256 is a 64-character SHA-256 hex digest, frozen_source.freeze_verification_status="verified", and len(frozen_source.frozen_member_manifest)=1..
  - AC-2 [integration] Given tests/fixtures/shamela_real/11_multi_small; When freeze and manifest executes; Then frozen_source.freeze_verification_status="verified" and len(frozen_source.frozen_member_manifest)=3..
  - AC-3 [integration] Given tests/fixtures/shamela_real/03_fiqh/book.htm after the same file has already been frozen once; When freeze and manifest executes again; Then Freezing aborts with error_code=SRC-E-DUPLICATE-INGEST..
