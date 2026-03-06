"""LLM-Assisted Metadata Inference — SPEC §4.A.4

Fills metadata gaps, validates extracted data, enriches with scholarly context.
Uses multi-model consensus for author_id and work_id (SPEC §6).

Infers: genre, genre_chain, structural_format, multi_layer, source_authority,
science_scope, level, author identification, text_fidelity, tahqiq_quality.

Every inferred field carries a confidence score (0.0-1.0).
Single-LLM biographical inference capped at 0.85 (SPEC §6).
"""
