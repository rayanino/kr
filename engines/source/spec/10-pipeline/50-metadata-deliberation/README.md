# Step 50 — Metadata Deliberation

Purpose:

- Convert intake evidence into authoritative source-engine metadata decisions.

Entry criteria:

- intake dossier exists

Inputs and artifacts:

- intake dossier
- registries
- specialized research evidence

Flow:

- confirm work identity
- resolve authorship, genre, science, layer, and trust outputs
- preserve genuine disputes instead of flattening them

Recorded metadata:

- `author_output`
- `work_output`
- `genre`
- `science_scope`
- `is_multi_layer`
- `structural_format`
- `trust_decision`
- `collection_match_output`

Agents:

- attribution, research, verifier, and disagreement-resolution agents as defined by the architecture layer

Decision gates:

- high-impact metadata must satisfy multi-agent evidence rules

Outputs and handoff:

- source-engine metadata package ready for admission and handoff packaging

Failure modes:

- single-model author decisions
- disputed work identity flattened to one value
- trust finalization without required agent coverage

Acceptance tests:

- must consume the intake dossier rather than re-deriving from raw upload state
