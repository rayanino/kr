"""Scholar Authority — public API.

Re-exports from scholar_authority.py (production implementation)
and name_matching.py (Arabic name comparison utilities).
"""

from __future__ import annotations

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
