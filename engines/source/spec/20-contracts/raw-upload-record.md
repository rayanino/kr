# RawUploadRecord

Owned by:

- `10-upload-receipt`

Purpose:

- Track every submission before any source-engine acceptance decision exists.

Core fields:

- `submission_id`
- `submitted_path`
- `submitted_path_kind`
- `intake_mode`
- `owner_hint_payload`
- `receipt_timestamp`
- `status`

Status progression:

- `received`
- `frozen`
- `awaiting_owner_ack`
- `source_engine_accepted`
- `rejected_at_source`

Rules:

- Every submission gets one raw-upload record.
- A raw-upload record may exist without any admitted source.
