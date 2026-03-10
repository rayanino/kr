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

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from filelock import FileLock

from engines.source.contracts import (
    ErrorCode,
    RegistryPendingWrite,
    SourceMetadata,
)
from engines.source.src.config import SourceEngineConfig
from engines.source.src.registries import source_registry
from engines.source.src.registries import work_registry_store


_LOCK_TIMEOUT = 30  # seconds


def _atomic_json_write(path: Path, data: Any) -> None:
    """Write JSON atomically: temp file → fsync → os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)

    fd = tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, suffix=".tmp",
        delete=False, encoding="utf-8",
    )
    try:
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.replace(fd.name, str(path))
    except BaseException:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def register_source(
    metadata: SourceMetadata,
    *,
    library_root: Path = Path("library"),
    config: SourceEngineConfig | None = None,
) -> None:
    """Register a fully-validated source in all registries atomically.

    SPEC §4.A.2 Step 7 — atomic multi-registry write:
    1. Process genre chain (BEFORE locks — may register scholars)
    2. Write pending_registration_{source_id}.json (WAL)
    3. Acquire FileLock on sources.json & works.json (30s timeout)
    4. For each registry: create .bak → apply changes
    5. Write metadata.json to library/sources/{source_id}/
    6. Delete pending registration file
    """
    if config is None:
        from engines.source.src.config import load_config
        config = load_config(library_root)

    registries_dir = library_root / "registries"
    registries_dir.mkdir(parents=True, exist_ok=True)
    sources_path = registries_dir / "sources.json"
    works_path = registries_dir / "works.json"
    logs_dir = library_root / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)

    # Build source entry
    src_entry = source_registry.build_entry(metadata)

    # Build work entry
    transliteration = config.transliteration
    work_entry = work_registry_store.build_entry(metadata, transliteration)

    # Ensure source entry's work_id matches the generated work_id
    # (metadata.work_id may be a placeholder from upstream)
    actual_work_id = work_entry.work_id
    src_entry.work_id = actual_work_id

    # Process genre chain BEFORE acquiring locks (may register scholars)
    scholars_path = library_root / "registries" / "scholars.json"
    work_reg = work_registry_store.load(registry_path=works_path)
    edges = work_registry_store.process_genre_chain(
        metadata, work_reg, scholars_path, transliteration,
    )

    # Add edges to work entry
    work_entry.relationships = edges

    # 1. Write pending registration (WAL)
    pending_path = logs_dir / f"pending_registration_{metadata.source_id}.json"
    pending = RegistryPendingWrite(
        source_id=metadata.source_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        intended_changes={
            "sources.json": src_entry.model_dump(mode="json"),
            "works.json": work_entry.model_dump(mode="json"),
        },
        completed_files=[],
    )
    _atomic_json_write(pending_path, pending.model_dump(mode="json"))

    # 2. Acquire locks and apply changes
    sources_lock = FileLock(str(sources_path) + ".lock", timeout=_LOCK_TIMEOUT)
    works_lock = FileLock(str(works_path) + ".lock", timeout=_LOCK_TIMEOUT)

    try:
        sources_lock.acquire()
        works_lock.acquire()
    except Exception as exc:
        # Clean up any acquired locks
        try:
            sources_lock.release()
        except Exception:
            pass
        try:
            works_lock.release()
        except Exception:
            pass
        raise RuntimeError(
            f"Lock timeout during registration of {metadata.source_id}: "
            f"{ErrorCode.REGISTRATION_INTERRUPTED.value}"
        ) from exc

    try:
        # Update sources.json
        src_reg = source_registry.load(registry_path=sources_path)
        src_reg[metadata.source_id] = src_entry.model_dump(mode="json")
        source_registry.save(registry_path=sources_path, data=src_reg)

        # Mark sources.json as completed in pending
        pending.completed_files.append("sources.json")
        _atomic_json_write(pending_path, pending.model_dump(mode="json"))

        # Update works.json
        work_reg_data = work_registry_store.load(registry_path=works_path)
        if actual_work_id in work_reg_data:
            # Work exists — add source_id to source_ids
            existing = work_reg_data[actual_work_id]
            source_ids = existing.get("source_ids", [])
            if metadata.source_id not in source_ids:
                source_ids.append(metadata.source_id)
            existing["source_ids"] = source_ids
            # Add new relationship edges
            existing_rels = existing.get("relationships", [])
            for edge in edges:
                existing_rels.append(edge.model_dump(mode="json"))
            existing["relationships"] = existing_rels
        else:
            work_reg_data[actual_work_id] = work_entry.model_dump(mode="json")

        # Also add any placeholder works created by process_genre_chain
        for wid, wdata in work_reg.items():
            if wid not in work_reg_data:
                work_reg_data[wid] = wdata

        work_registry_store.save(registry_path=works_path, data=work_reg_data)

        pending.completed_files.append("works.json")
        _atomic_json_write(pending_path, pending.model_dump(mode="json"))

    finally:
        works_lock.release()
        sources_lock.release()

    # 3. Write metadata.json (with actual work_id, not placeholder)
    source_dir = library_root / "sources" / metadata.source_id
    source_dir.mkdir(parents=True, exist_ok=True)
    metadata_path = source_dir / "metadata.json"
    metadata_dict = metadata.model_dump(mode="json")
    metadata_dict["work_id"] = actual_work_id
    _atomic_json_write(metadata_path, metadata_dict)

    # 4. Delete pending registration
    if pending_path.exists():
        pending_path.unlink()


def check_orphaned_registrations(
    *,
    library_root: Path = Path("library"),
) -> list[str]:
    """Check for orphaned pending_registration files on startup.

    SPEC §4.A.2 Step 7: 'If one exists, the previous registration was
    interrupted: complete or roll back based on which files were already updated.'

    Three cases:
    - All registries updated → delete pending (completed ok)
    - No registries updated → delete pending (never started)
    - Partial → restore from .bak files, delete pending (rollback)

    Returns list of source_ids that were recovered.
    """
    logs_dir = library_root / "logs"
    if not logs_dir.exists():
        return []

    recovered: list[str] = []

    for pending_file in logs_dir.glob("pending_registration_*.json"):
        try:
            raw = pending_file.read_text(encoding="utf-8")
            pending_data = json.loads(raw)
        except (json.JSONDecodeError, OSError):
            # Corrupt pending file — check if we can restore from .bak
            _rollback_registries(library_root)
            pending_file.unlink(missing_ok=True)
            continue

        source_id = pending_data.get("source_id", "")
        completed = pending_data.get("completed_files", [])
        intended = pending_data.get("intended_changes", {})

        if not intended:
            # Empty or invalid — just clean up
            pending_file.unlink(missing_ok=True)
            continue

        all_files = list(intended.keys())
        completed_set = set(completed)
        all_set = set(all_files)

        if completed_set == all_set:
            # All completed — registration succeeded, just clean up pending
            pending_file.unlink(missing_ok=True)
            recovered.append(source_id)
        elif not completed_set:
            # None completed — never started, just clean up
            pending_file.unlink(missing_ok=True)
            recovered.append(source_id)
        else:
            # Partial — rollback completed files from .bak
            registries_dir = library_root / "registries"
            for filename in completed:
                registry_path = registries_dir / filename
                bak_path = registry_path.with_suffix(".json.bak")
                if bak_path.exists():
                    try:
                        os.replace(str(bak_path), str(registry_path))
                    except OSError as exc:
                        raise RuntimeError(
                            f"Cannot restore registry {registry_path} from backup during "
                            f"orphan recovery for {source_id}: {exc}. Manual recovery required."
                        ) from exc
            pending_file.unlink(missing_ok=True)
            recovered.append(source_id)

    return recovered


def _rollback_registries(library_root: Path) -> None:
    """Restore registries from .bak files if they exist."""
    registries_dir = library_root / "registries"
    if not registries_dir.exists():
        return

    for bak_file in registries_dir.glob("*.json.bak"):
        registry_path = bak_file.with_suffix("").with_suffix(".json")
        # Only restore if the registry file seems corrupt
        try:
            raw = registry_path.read_text(encoding="utf-8")
            json.loads(raw)
        except (json.JSONDecodeError, OSError):
            try:
                os.replace(str(bak_file), str(registry_path))
            except OSError as exc:
                raise RuntimeError(
                    f"Cannot restore registry {registry_path} from backup: {exc}. "
                    f"Manual recovery required."
                ) from exc
            # Validate restored content is valid JSON
            try:
                restored_raw = registry_path.read_text(encoding="utf-8")
                json.loads(restored_raw)
            except (json.JSONDecodeError, OSError) as exc:
                raise RuntimeError(
                    f"Registry {registry_path} restored from backup but backup is also corrupt. "
                    f"Manual recovery required."
                ) from exc
