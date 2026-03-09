"""Source Registry — library/registries/sources.json (SPEC §3)

CRUD operations for SourceRegistryEntry records.
Keyed by source_id. Provides: duplicate detection lookups,
status tracking.

All writes go through the atomic write-ahead log in registries/__init__.py.
This module provides read operations and entry construction.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from engines.source.contracts import SourceRegistryEntry, SourceMetadata


def build_entry(metadata: SourceMetadata) -> SourceRegistryEntry:
    """Construct a SourceRegistryEntry from a SourceMetadata record.
    
    Maps: source_id, work_id, human_label, title_arabic, author_canonical_id,
    trust_tier, processing_status, frozen_hash, intake_timestamp, acquisition_path.
    """
    raise NotImplementedError


def load(*, registry_path: Path = Path("library/registries/sources.json")) -> dict[str, dict]:
    """Load the source registry from disk."""
    raise NotImplementedError


def find_by_hash(frozen_hash: str, registry: dict[str, dict]) -> Optional[str]:
    """Find a source_id by its frozen_hash. Returns None if not found.
    Used by deduplication (§4.A.7).
    """
    raise NotImplementedError
