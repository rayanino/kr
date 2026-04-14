# SourceMetadata

Owned by:

- `50-metadata-deliberation`
- finalized by `60-source-admission-and-normalization-handoff`

Mandatory fields:

- `source_id`
- `source_sha256`
- `frozen_blob_path`
- `registry_entry_id`
- `title_arabic`
- `author_output`
- `work_output`
- `genre`
- `science_scope`
- `is_multi_layer`
- `structural_format`
- `trust_decision`
- `completeness_status`
- `integrity_status`
- `volume_count`
- `intake_timestamp`

Selected optional fields:

- `source_format`
- `normalization_route`
- `pdf_text_layer_status`
- `page_count_physical`
- `page_layout_hint`
- `muhaqiq_output`
- `death_date_hijri`
- `level`
- `edition_info`
- `publisher`
- `text_fidelity`
- `hint_comparison_results`
- `admission_reason`

Rules:

- SourceMetadata exists only for source-engine accepted sources.
- It must never exist for rejected raw uploads.
