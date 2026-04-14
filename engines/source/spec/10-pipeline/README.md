# 10 Pipeline

Canonical ordered steps:

1. `10-upload-receipt`
2. `20-freeze-and-manifest`
3. `30-container-classification`
4. `40-intake-analysis`
5. `50-metadata-deliberation`
6. `60-source-admission-and-normalization-handoff`

Rules:

- Each step owns one clear boundary in the source-engine flow.
- Each step folder must contain a fixed structured step description.
- Normative atoms for that step live with that step instead of being scattered by atom type.
