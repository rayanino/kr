"""Source Engine — محرك المصادر (SPEC: engines/source/SPEC.md)

Pipeline entry point. Accepts raw knowledge material, establishes identity models,
captures metadata, freezes original files, maintains registries.

Usage:
    from engines.source.src.engine import acquire_source
    result = acquire_source(staging_path, owner_hints)
"""