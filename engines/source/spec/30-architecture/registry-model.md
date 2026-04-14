# Registry Model

The source engine uses two registries:

1. `raw_upload_registry`
2. `source_collection`

Rules:

- `raw_upload_registry` records every submission.
- `source_collection` records only source-engine accepted sources.
- A rejected upload remains traceable in `raw_upload_registry` but must not create a `source_collection` record.
- An accepted source must remain linkable back to its originating raw upload.
