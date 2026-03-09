"""Source Deduplication — SPEC §4.A.7

Two levels of deduplication:
1. Source-level (exact duplicate): composite SHA-256 hash match in source registry.
2. Work-level (same work, different edition): title similarity + same author.

Source duplicates are rejected. Work duplicates are acquired and linked.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

from shared.scholar_authority.src.name_matching import normalized_name_similarity

logger = logging.getLogger(__name__)


def check_exact_duplicate(
    composite_hash: str,
    source_registry: dict[str, dict[str, Any]],
) -> Optional[str]:
    """Check if a source with the same composite hash already exists.

    SPEC §4.A.7 source-level deduplication.

    Args:
        composite_hash: SHA-256 composite hash of the new source.
        source_registry: Dict of source_id → registry entry dicts.
            Each entry must have a 'frozen_hash' key.

    Returns:
        Existing source_id if an exact duplicate is found, None otherwise.
    """
    for source_id, entry in source_registry.items():
        if entry.get("frozen_hash") == composite_hash:
            logger.info(
                "Exact duplicate found: hash %s matches source %s",
                composite_hash[:16],
                source_id,
            )
            return source_id
    return None


def check_work_duplicate(
    title: str,
    author_id: str,
    work_registry: dict[str, dict[str, Any]],
) -> Optional[str]:
    """Check if a work with the same title and author already exists.

    SPEC §4.A.7 work-level matching.
    Uses normalized_name_similarity() for title comparison with threshold >= 0.90.

    Args:
        title: Arabic title of the new work.
        author_id: Canonical author ID (e.g., "sch_00042") or canonical name.
        work_registry: Dict of work_id → registry entry dicts.
            Each entry must have 'canonical_title' and 'author_canonical_id' keys.

    Returns:
        Existing work_id if a work-level duplicate is found, None otherwise.
    """
    for work_id, entry in work_registry.items():
        existing_title = entry.get("canonical_title", "")
        existing_author = entry.get("author_canonical_id", "")

        # Author must match exactly (by ID)
        if existing_author != author_id:
            continue

        # Title similarity >= 0.90
        title_sim = normalized_name_similarity(title, existing_title)
        if title_sim >= 0.90:
            logger.info(
                "Work duplicate found: '%s' matches work %s (sim=%.3f)",
                title[:50],
                work_id,
                title_sim,
            )
            return work_id

    return None
