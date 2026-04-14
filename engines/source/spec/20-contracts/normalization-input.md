# NormalizationInput

Owned by:

- `60-source-admission-and-normalization-handoff`

Purpose:

- Bridge the source-owned SourceMetadata surface to the normalization-facing runtime input shape.

Core fields:

- `source_id`
- `source_format_legacy`
- `frozen_path`
- `frozen_hash`
- `page_count`
- `volume_count`
- `title_arabic`
- `author`
- `work_id`
- `structural_format`
- `is_multi_layer`
- `genre`
- `text_fidelity`
- `trust_tier`

Legacy source-format mapping:

- `shamela_html -> shamela_html`
- `plain_text -> plain_text`
- `pdf + pdf_text_layer_status=clean -> pdf_text`
- `pdf + pdf_text_layer_status in {absent, corrupt} -> pdf_scanned`

Rules:

- `NormalizationInput` is a bridge object inside the handoff bundle.
- It must be derivable from the source-engine outputs without redefining SourceMetadata as a downstream-owned contract.
