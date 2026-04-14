# Step 30 — Container Classification

Purpose:

- Determine what kind of uploaded container the frozen artifact is, without normalizing its text.

Entry criteria:

- frozen source candidate exists

Inputs and artifacts:

- frozen member manifest
- frozen container bytes

Flow:

- classify source container
- identify ordered members and roles
- choose a provisional normalization route

Recorded metadata:

- `source_format`
- `normalization_route`
- `volume_manifest`
- `supplementary_file_decision`

Agents:

- deterministic container classifier

Decision gates:

- classify multipart and supplementary cases explicitly

Outputs and handoff:

- container-classified source candidate
- provisional normalization route, subject to PDF-specific confirmation in step 40

Failure modes:

- unsupported container type
- ambiguous member-role assignment without recorded uncertainty

Acceptance tests:

- must distinguish file type, multipart structure, and routing without emitting normalized text
