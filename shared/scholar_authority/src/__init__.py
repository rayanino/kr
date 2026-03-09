"""Scholar authority stub — tracer bullet.

Stores and retrieves scholar records from an in-memory dict.
Real implementation will use persistent storage with cross-validation.
"""

from __future__ import annotations

from typing import Optional

from shared.scholar_authority.src.name_matching import normalized_name_similarity


_SCHOLAR_REGISTRY: dict[str, dict] = {}


def lookup(
    name: str, death_date: int | None = None
) -> Optional[dict]:
    """Look up a scholar by canonical name using token-based matching.

    Args:
        name: Arabic name to search for.
        death_date: Optional Hijri death date for disambiguation.

    Returns:
        Scholar record dict if found with similarity >= 0.85, else None.
    """
    # Exact match first
    if name in _SCHOLAR_REGISTRY:
        return _SCHOLAR_REGISTRY[name]
    # Token-based similarity matching
    best_match: Optional[tuple[str, dict, float]] = None
    for key, record in _SCHOLAR_REGISTRY.items():
        sim = normalized_name_similarity(name, key)
        if sim >= 0.85:
            if best_match is None or sim > best_match[2]:
                best_match = (key, record, sim)
    if best_match is not None:
        return best_match[1]
    return None


def register(canonical_name: str, record: dict) -> str:
    """Register a scholar record.

    Returns the canonical_name as the scholar_id.
    """
    _SCHOLAR_REGISTRY[canonical_name] = {
        "canonical_name": canonical_name,
        **record,
    }
    return canonical_name


def get_all() -> dict[str, dict]:
    """Return all registered scholars."""
    return dict(_SCHOLAR_REGISTRY)


def clear() -> None:
    """Clear the registry."""
    _SCHOLAR_REGISTRY.clear()
