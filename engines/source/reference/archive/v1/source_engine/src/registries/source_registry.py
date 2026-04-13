"""Source Registry — library/registries/sources.json (SPEC §3)

CRUD operations for SourceRegistryEntry records.
Keyed by source_id. Provides: duplicate detection lookups,
status tracking.

All writes go through the atomic write-ahead log in registries/__init__.py.
This module provides read operations and entry construction.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional

from engines.source.contracts import SourceRegistryEntry, SourceMetadata


def build_entry(metadata: SourceMetadata) -> SourceRegistryEntry:
    """Construct a SourceRegistryEntry from a SourceMetadata record.

    Maps: source_id, work_id, human_label, title_arabic, author_canonical_id,
    trust_tier, processing_status, frozen_hash, intake_timestamp, acquisition_path.
    """
    return SourceRegistryEntry(
        source_id=metadata.source_id,
        work_id=metadata.work_id,
        human_label=metadata.human_label,
        title_arabic=metadata.title_arabic,
        author_canonical_id=metadata.author.canonical_id,
        trust_tier=metadata.trust_tier,
        processing_status=metadata.status,
        frozen_hash=metadata.frozen_hash,
        intake_timestamp=metadata.intake_timestamp,
        acquisition_path=metadata.acquisition_path,
    )


def load(*, registry_path: Path = Path("library/registries/sources.json")) -> dict[str, dict]:
    """Load the source registry from disk. Returns empty dict if file missing."""
    if not registry_path.exists():
        return {}
    raw = registry_path.read_text(encoding="utf-8")
    if not raw.strip():
        return {}
    return json.loads(raw)


def save(*, registry_path: Path, data: dict[str, dict]) -> None:
    """Save the source registry atomically: .bak → temp → fsync → os.replace."""
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


def find_by_hash(frozen_hash: str, registry: dict[str, dict]) -> Optional[str]:
    """Find a source_id by its frozen_hash. Returns None if not found.
    Used by deduplication (§4.A.7).
    """
    for source_id, entry in registry.items():
        if entry.get("frozen_hash") == frozen_hash:
            return source_id
    return None
