# Step 40 — Intake Analysis

Purpose:

- Build the intake dossier for every upload before final metadata decisions.

Entry criteria:

- frozen source candidate is container-classified

Inputs and artifacts:

- frozen member manifest
- container classification
- raw-upload record

Flow:

- identify likely source/work candidates
- inspect completeness and partiality
- inspect integrity and corruption signs
- generate collection-match candidates

Recorded metadata:

- `source_format`
- `normalization_route`
- `title_evidence`
- `external_source_refs`
- `declared_vs_observed_counts`
- `completeness_status`
- `partiality_reasons`
- `integrity_status`
- `integrity_findings`
- `collection_match_candidates`
- `pdf_text_layer_status`
- `pdf_text_evidence`
- `page_layout_hint`

Agents:

- one intake-analysis team with fixed subroles for identification, completeness, integrity, and collection matching

Decision gates:

- structurally invalid uploads stop here
- readable but partial or suspicious uploads proceed with flags

Outputs and handoff:

- intake dossier

Failure modes:

- under-evidenced work/source identification
- partial uploads misclassified as complete
- corruption evidence dropped before metadata deliberation

Acceptance tests:

- must emit an intake dossier for every non-blocked upload
