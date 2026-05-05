"""Scholar Authority — public API.

Re-exports from scholar_authority.py (production implementation) and
name_matching.py (Arabic name comparison utilities) via PEP 562 lazy
attribute access. The lazy form avoids triggering scholar_authority.py's
``from engines.source.contracts import ...`` line at package import
time, which would create a circular dependency now that
``engines/source/contracts.py`` (Phase 5 Session 5) imports
``ScholarMatchResult`` from ``match_contracts.py`` to type the new
``MetadataDeliberationResult.scholar_match_results`` field.

Public surface (unchanged): consumers may continue to write ``from
shared.scholar_authority.src import lookup, register``; the lazy
``__getattr__`` resolves these on first access.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    # Static imports for type checkers — at runtime, the names are
    # resolved lazily by ``__getattr__`` below. The TYPE_CHECKING guard
    # ensures these eager imports never execute, preserving the
    # circular-import fix.
    from shared.scholar_authority.src.name_matching import (
        normalize_arabic_name,
        normalized_name_similarity,
    )
    from shared.scholar_authority.src.scholar_authority import (
        ScholarMatchResult,
        ScholarUpdateConflict,
        ScholarUpdateResult,
        compute_scholar_match_score,
        get_all,
        lookup,
        register,
        update,
    )

__all__ = [
    "ScholarMatchResult",
    "ScholarUpdateConflict",
    "ScholarUpdateResult",
    "compute_scholar_match_score",
    "get_all",
    "lookup",
    "register",
    "update",
    "normalize_arabic_name",
    "normalized_name_similarity",
]


def __getattr__(name: str) -> Any:
    """PEP 562 lazy attribute resolution.

    Avoids eager-loading ``scholar_authority.py`` (which imports from
    ``engines.source.contracts``) at package init. Without this guard,
    importing ``shared.scholar_authority.src.match_contracts`` from
    ``engines/source/contracts.py`` would trigger
    ``shared.scholar_authority.src.scholar_authority`` to load, which
    would re-enter ``engines/source/contracts.py`` mid-initialization.
    """
    if name in {"normalize_arabic_name", "normalized_name_similarity"}:
        from shared.scholar_authority.src import name_matching as _nm

        return getattr(_nm, name)
    if name in {
        "ScholarMatchResult",
        "ScholarUpdateConflict",
        "ScholarUpdateResult",
        "compute_scholar_match_score",
        "get_all",
        "lookup",
        "register",
        "update",
    }:
        from shared.scholar_authority.src import scholar_authority as _sa

        return getattr(_sa, name)
    raise AttributeError(
        f"module 'shared.scholar_authority.src' has no attribute {name!r}"
    )
