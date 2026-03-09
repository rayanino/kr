"""Registry Management — SPEC §3, §4.A.2 Step 7

Atomic writes via write-ahead log pattern:
1. Write pending_registration_{source_id}.json to library/logs/
2. Apply changes to each registry file (with .bak copies)
3. Delete pending registration file

Startup recovery: check for orphaned pending files → complete or rollback.

All three registries (sources, works, scholars) are updated in a single
atomic transaction. filelock ensures exclusive access during writes.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.source.contracts import (
    SourceMetadata,
    SourceRegistryEntry,
    WorkRegistryEntry,
    ScholarAuthorityRecord,
    RegistryPendingWrite,
)


def register_source(
    metadata: SourceMetadata,
    *,
    library_root: Path = Path("library"),
) -> None:
    """Register a fully-validated source in all three registries atomically.
    
    SPEC §4.A.2 Step 7 — atomic multi-registry write:
    1. Write pending_registration_{source_id}.json (WAL)
    2. Update scholars.json (author + muhaqiq records)
    3. Update works.json (work record + relationship edges)
    4. Update sources.json (source entry)
    5. Write metadata.json to library/sources/{source_id}/
    6. Delete pending registration file
    
    Each registry write:
    - Acquires file lock (timeout 30s)
    - Creates .bak copy of current file
    - Writes atomically (temp file → fsync → os.replace)
    
    On startup, check_orphaned_registrations() should be called.
    """
    raise NotImplementedError


def check_orphaned_registrations(
    *,
    library_root: Path = Path("library"),
) -> list[str]:
    """Check for orphaned pending_registration files on startup.
    
    SPEC §4.A.2 Step 7: 'If one exists, the previous registration was
    interrupted: complete or roll back based on which files were already updated.'
    
    Returns list of source_ids that were recovered.
    """
    raise NotImplementedError
