"""Scholar authority stub — tracer bullet.

Stores and retrieves scholar records from an in-memory dict.
Real implementation will use persistent storage with cross-validation.
"""

from typing import Any, Optional


_SCHOLAR_REGISTRY: dict[str, dict] = {}


def lookup(name: str) -> Optional[dict]:
    """Look up a scholar by canonical name.
    
    Tracer bullet stub: searches in-memory registry.
    """
    # Exact match first
    if name in _SCHOLAR_REGISTRY:
        return _SCHOLAR_REGISTRY[name]
    # Substring match
    for key, record in _SCHOLAR_REGISTRY.items():
        if name in key or key in name:
            return record
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
