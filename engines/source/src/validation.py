"""Self-Validation (Layer 1) — SPEC §5

Validates SourceMetadata before every write to disk:
1. Schema compliance (Pydantic model validation)
2. Referential integrity (author → scholars.json, work_id → works.json)
3. Confidence threshold (critical fields < 0.50 → block write)
4. Duplicate re-check (after inference may change title/author)
5. Consistency cross-check (genre vs structural_format, level vs genre)

Returns list of ValidationError; empty = record is valid.
"""
