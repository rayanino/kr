# Step 10 — Upload Receipt

Purpose:

- Receive one submission and create a raw-upload record without interpreting content.

Entry criteria:

- Owner provides a filesystem path.

Inputs and artifacts:

- submitted path
- owner hints payload
- intake mode

Flow:

- validate path existence and readability
- classify path kind as file or directory
- create raw-upload record

Recorded metadata:

- `submission_id`
- `submitted_path`
- `submitted_path_kind`
- `owner_hint_payload`
- `intake_mode`

Agents:

- deterministic intake receiver only

Decision gates:

- reject unreadable or missing paths

Outputs and handoff:

- raw-upload record for freeze and manifest

Failure modes:

- missing path
- unreadable path

Acceptance tests:

- must produce a raw-upload record before any freeze or parsing work starts
