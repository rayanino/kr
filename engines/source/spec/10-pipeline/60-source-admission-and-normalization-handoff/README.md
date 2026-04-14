# Step 60 — Source Admission and Normalization Handoff

Purpose:

- Decide official source-engine acceptance and emit the normalization handoff bundle.

Entry criteria:

- metadata deliberation completed

Inputs and artifacts:

- metadata package
- intake dossier
- registry state

Flow:

- evaluate owner-submission risk
- apply source-engine acceptance rules
- write official source-collection record
- emit normalization handoff bundle

Recorded metadata:

- `owner_submission_risk_case`
- `admission_state`
- `admission_reason`
- `normalization_handoff_bundle`

Agents:

- deterministic admission writer plus any required final verification agents

Decision gates:

- only structurally invalid uploads are blocked from source-engine acceptance
- official registration happens only after source-engine completion
- any uncertainty that could materially affect study quality opens owner_submission_risk_case and blocks official admission plus downstream progression until owner acknowledgment

Outputs and handoff:

- admitted source collection record
- normalization handoff bundle

Failure modes:

- raw uploads polluting the official collection
- accepted source missing intake evidence in handoff

Acceptance tests:

- must distinguish raw-upload tracking from official source-collection admission
