# Step 20 — Freeze and Manifest

Purpose:

- Freeze immutable bytes and produce a manifest for the uploaded artifact.

Entry criteria:

- a raw-upload record exists

Inputs and artifacts:

- raw-upload record
- submitted filesystem artifact

Flow:

- freeze bytes
- compute hashes
- enumerate members
- verify freeze integrity

Recorded metadata:

- `source_id`
- `source_sha256`
- `frozen_blob_path`
- `frozen_member_manifest`
- `freeze_verification_status`

Agents:

- deterministic freezer and manifest builder

Decision gates:

- reject exact duplicates
- reject unfreezable or structurally unreadable artifacts

Outputs and handoff:

- frozen source candidate
- immutable manifest

Failure modes:

- duplicate
- freeze verification mismatch
- container cannot be opened after freeze

Acceptance tests:

- must preserve immutable member manifests and verify the frozen copy before classification begins
