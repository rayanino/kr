"""Enrichment Write-Back Handler — SPEC §2 enrichment invariants

Processes EnrichmentRequest from downstream engines.
Validates all 7 enrichment invariants before applying:
1. Frozen file immutability
2. Identity immutability (source_id never; work_id/author need human gate)
3. No field deletion
4. History preservation
5. Trust tier protection
6. Schema compliance
7. Referential integrity

Critical field gate: author, work_id, genre, science_scope changes
→ human gate + stale-marking cascade.
"""
