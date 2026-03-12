"""Work Registry Store — library/registries/works.json (SPEC §3, §4.A.9)

CRUD operations for WorkRegistryEntry records.
Keyed by work_id. Provides: work matching queries, relationship edge creation,
preferred edition tracking.

§4.A.9: When LLM infers a genre_chain, the engine searches for the base work.
If found → creates WorkRelationshipEdge. If not → creates placeholder with
status 'referenced_not_acquired'.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from engines.source.contracts import (
    GenreChain,
    GenreRelationType,
    SourceMetadata,
    WorkRegistryEntry,
    WorkRelationshipEdge,
)
from engines.source.src.registries.scholar_registry import lookup_or_register_author
from engines.source.src.text_utils import generate_work_id
from shared.scholar_authority.src.name_matching import normalized_name_similarity


def build_entry(
    metadata: SourceMetadata,
    transliteration_table: dict[str, dict[str, str]],
) -> WorkRegistryEntry:
    """Construct a WorkRegistryEntry from a SourceMetadata record.

    Generates work_id via text_utils.generate_work_id().
    """
    work_id = generate_work_id(
        metadata.author.name_arabic,
        metadata.title_arabic,
        transliteration_table,
    )
    return WorkRegistryEntry(
        work_id=work_id,
        canonical_title=metadata.title_arabic,
        canonical_title_transliterated=metadata.title_transliterated,
        author_canonical_id=metadata.author.canonical_id,
        genre=metadata.genre,
        science_scope=list(metadata.science_scope),
        source_ids=[metadata.source_id],
        preferred_source_id=metadata.source_id,
        status="active",
    )


def build_placeholder(
    title: str,
    author_canonical_id: str,
    work_id: str,
) -> WorkRegistryEntry:
    """Create a placeholder WorkRegistryEntry for a referenced-but-not-acquired work.

    SPEC §4.A.9: 'creates a placeholder work record with
    status: "referenced_not_acquired"'
    """
    return WorkRegistryEntry(
        work_id=work_id,
        canonical_title=title,
        author_canonical_id=author_canonical_id,
        source_ids=[],
        preferred_source_id=None,
        status="referenced_not_acquired",
    )


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
    return WorkRelationshipEdge(
        from_work_id=from_work_id,
        to_work_id=to_work_id,
        relation_type=relation_type,
        confidence=confidence,
        discovered_by=discovered_by,
    )


def process_genre_chain(
    metadata: SourceMetadata,
    work_registry: dict[str, dict],
    scholar_registry_path: Path,
    transliteration_table: dict[str, dict[str, str]],
) -> list[WorkRelationshipEdge]:
    """Process genre chain relationships from SourceMetadata.

    For each genre chain entry:
    - Search work_registry for existing base work
    - Found → create edge to existing work
    - Not found → create sparse scholar record, placeholder work, edge
    """
    edges: list[WorkRelationshipEdge] = []

    chains: list[GenreChain] = metadata.work_relationships
    if metadata.genre_chain is not None:
        chains = [metadata.genre_chain] + [c for c in chains if c != metadata.genre_chain]

    for chain in chains:
        # Resolve author name to canonical_id first (needed for work lookup)
        author_ref, _ = lookup_or_register_author(
            name=chain.base_work_author,
            death_date_hijri=None,
            school_affiliations=None,
            source_id=metadata.source_id,
            registry_path=scholar_registry_path,
        )

        # Search for existing base work using resolved canonical_id
        existing_work_id = find_by_title_author(
            chain.base_work_title,
            author_ref.canonical_id,
            work_registry,
        )

        if existing_work_id is not None:
            edge = create_relationship_edge(
                from_work_id=metadata.work_id,
                to_work_id=existing_work_id,
                relation_type=chain.relation_type,
                confidence=chain.confidence,
            )
            edges.append(edge)
        else:
            # Generate work_id for placeholder
            placeholder_work_id = generate_work_id(
                chain.base_work_author,
                chain.base_work_title,
                transliteration_table,
            )

            # Create placeholder work
            placeholder = build_placeholder(
                title=chain.base_work_title,
                author_canonical_id=author_ref.canonical_id,
                work_id=placeholder_work_id,
            )
            work_registry[placeholder_work_id] = placeholder.model_dump(mode="json")

            edge = create_relationship_edge(
                from_work_id=metadata.work_id,
                to_work_id=placeholder_work_id,
                relation_type=chain.relation_type,
                confidence=chain.confidence,
            )
            edges.append(edge)

    return edges


def load(*, registry_path: Path = Path("library/registries/works.json")) -> dict[str, dict]:
    """Load the work registry from disk. Returns empty dict if file missing."""
    if not registry_path.exists():
        return {}
    raw = registry_path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def save(*, registry_path: Path, data: dict[str, dict]) -> None:
    """Save the work registry atomically: .bak → temp → fsync → os.replace."""
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)

    fd = tempfile.NamedTemporaryFile(
        mode="w",
        dir=registry_path.parent,
        suffix=".tmp",
        delete=False,
        encoding="utf-8",
    )
    try:
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()

        if registry_path.exists():
            bak = registry_path.with_suffix(".json.bak")
            shutil.copy2(str(registry_path), str(bak))

        os.replace(fd.name, str(registry_path))
    except BaseException:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def find_by_title_author(
    title: str,
    author_canonical_id: str,
    registry: dict[str, dict],
) -> Optional[str]:
    """Find a work_id by title + author canonical_id. Returns None if not found.

    Uses normalized_name_similarity for title comparison (threshold 0.80).
    Author match is exact on canonical_id (sch_XXXXX format).

    Note: genre chain lookups must resolve author names to canonical_ids
    BEFORE calling this function. Comparing Arabic names against sch_ IDs
    would always fail.
    """
    for work_id, entry in registry.items():
        entry_author = entry.get("author_canonical_id", "")
        if entry_author != author_canonical_id:
            continue

        entry_title = entry.get("canonical_title", "")
        sim = normalized_name_similarity(title, entry_title)
        if sim >= 0.80:
            return work_id

    return None
