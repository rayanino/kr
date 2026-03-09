"""Work Registry Store — library/registries/works.json (SPEC §3, §4.A.9)

CRUD operations for WorkRegistryEntry records.
Keyed by work_id. Provides: work matching queries, relationship edge creation,
preferred edition tracking.

§4.A.9: When LLM infers a genre_chain, the engine searches for the base work.
If found → creates WorkRelationshipEdge. If not → creates placeholder with
status 'referenced_not_acquired'.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from engines.source.contracts import (
    WorkRegistryEntry,
    WorkRelationshipEdge,
    GenreRelationType,
    SourceMetadata,
)


def build_entry(metadata: SourceMetadata) -> WorkRegistryEntry:
    """Construct a WorkRegistryEntry from a SourceMetadata record.
    
    Maps: work_id, canonical_title, author_canonical_id, genre, science_scope,
    source_ids, preferred_source_id, status='acquired'.
    """
    raise NotImplementedError


def build_placeholder(
    title: str,
    author_canonical_id: str,
    work_id: str,
) -> WorkRegistryEntry:
    """Create a placeholder WorkRegistryEntry for a referenced-but-not-acquired work.
    
    SPEC §4.A.9: 'creates a placeholder work record with
    status: "referenced_not_acquired"'
    
    Must conform to WorkRegistryEntry. author_canonical_id is required,
    so a scholar record must exist for the referenced author.
    """
    raise NotImplementedError


def create_relationship_edge(
    from_work_id: str,
    to_work_id: str,
    relation_type: GenreRelationType,
    confidence: float,
    discovered_by: str = "source_engine",
) -> WorkRelationshipEdge:
    """Create a WorkRelationshipEdge from genre chain inference.
    
    SPEC §4.A.9: Relationships discovered at intake through LLM inference.
    """
    raise NotImplementedError


def load(*, registry_path: Path = Path("library/registries/works.json")) -> dict[str, dict]:
    """Load the work registry from disk."""
    raise NotImplementedError


def find_by_title_author(
    title: str,
    author_canonical_id: str,
    registry: dict[str, dict],
) -> Optional[str]:
    """Find a work_id by title + author. Returns None if not found.
    Uses normalized_name_similarity for title comparison (threshold 0.80).
    """
    raise NotImplementedError
