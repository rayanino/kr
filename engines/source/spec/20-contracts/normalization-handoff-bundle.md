# NormalizationHandoffBundle

Owned by:

- `60-source-admission-and-normalization-handoff`

Purpose:

- Package everything normalization needs without losing source-engine evidence.

Required contents:

- `SourceMetadata`
- `NormalizationInput`
- relevant `FrozenMemberManifest`
- `completeness_status`
- `integrity_status`
- `declared_vs_observed_counts`
- `pdf_text_layer_status` when relevant
- `page_layout_hint` when relevant
- unresolved disputes that normalization must preserve

Rules:

- The source engine emits metadata and evidence, not normalized text.
- The handoff bundle must preserve enough evidence for normalization to understand why the source-engine made its intake decisions.
