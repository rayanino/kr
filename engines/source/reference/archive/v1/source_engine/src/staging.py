"""Staging Pipeline — SPEC §4.A.2 Steps 1, 2, and partial Step 5.

Handles file staging, SHA-256 hashing, composite hash derivation,
source_id generation, staging locks, and TOCTOU timestamp verification.

The stage_source() function orchestrates the staging workflow:
validate → detect format → lock → record timestamps → hash → derive source_id.
"""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field

from engines.source.contracts import ErrorCode, ErrorSeverity, SourceFormat
from engines.source.src.config import SourceEngineConfig
from engines.source.src.exceptions import SourceEngineError, make_error
from engines.source.src.format_detection import detect_format

_HASH_CHUNK_SIZE = 65536  # 64 KB


class StagingResult(BaseModel):
    """Result of staging a source through Steps 1-2 and partial Step 5.

    Internal intermediate result — not persisted to disk. Used to pass
    staging artifacts to downstream pipeline steps (freezing, registration).
    """

    source_path: Path
    source_format: SourceFormat
    file_hashes: dict[str, str] = Field(
        description="Filename → SHA-256 hex digest for each staged file."
    )
    composite_hash: str = Field(
        description="SHA-256 of sorted JSON of file_hashes."
    )
    source_id: str = Field(
        description="Unique identifier: src_{8_hex_chars} with collision suffix."
    )
    file_timestamps: dict[str, float] = Field(
        description="Filename → mtime at staging time, for TOCTOU detection."
    )
    lock_path: Path = Field(
        description="Path to .kr_processing lock file."
    )

    model_config = {"arbitrary_types_allowed": True}


# ──────────────────────────────────────────────────────────────────
# Hashing
# ──────────────────────────────────────────────────────────────────


def compute_file_hash(file_path: Path) -> str:
    """Compute SHA-256 hex digest of a single file.

    Reads in 64 KB chunks to handle large files without loading
    the entire file into memory.

    Args:
        file_path: Path to a file.

    Returns:
        Lowercase 64-character hex string of SHA-256 hash.
    """
    h = hashlib.sha256()
    with file_path.open("rb") as f:
        while True:
            chunk = f.read(_HASH_CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def compute_composite_hash(file_hashes: dict[str, str]) -> str:
    """Derive composite hash from individual file hashes.

    Computes SHA-256 of the sorted JSON serialization of the file_hashes
    dict. sort_keys=True ensures determinism regardless of insertion order.

    Args:
        file_hashes: Dict mapping filename → SHA-256 hex digest.

    Returns:
        Lowercase 64-character hex string of composite SHA-256 hash.
    """
    payload = json.dumps(file_hashes, sort_keys=True).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ──────────────────────────────────────────────────────────────────
# Source ID
# ──────────────────────────────────────────────────────────────────


def derive_source_id(
    composite_hash: str,
    existing_ids: set[str] | None = None,
) -> str:
    """Derive source_id from composite hash with collision detection.

    Format: src_{first_8_hex_chars_of_composite_hash}
    On collision with existing_ids: append _2, _3, etc.

    Args:
        composite_hash: Full 64-character composite SHA-256 hex string.
        existing_ids: Set of existing source_ids to check for collisions.

    Returns:
        Unique source_id string.
    """
    base = f"src_{composite_hash[:8]}"

    if existing_ids is None or base not in existing_ids:
        return base

    suffix = 2
    while f"{base}_{suffix}" in existing_ids:
        suffix += 1
    return f"{base}_{suffix}"


# ──────────────────────────────────────────────────────────────────
# Staging Locks
# ──────────────────────────────────────────────────────────────────


def create_staging_lock(source_path: Path) -> Path:
    """Create .kr_processing lock file for a staged source.

    For directories, the lock is placed inside the directory.
    For single files, the lock is placed in the file's parent directory.

    The lock file contains JSON: {"created_at": ISO8601, "pid": int}.
    Uses exclusive file creation to prevent race conditions.

    Args:
        source_path: The staged source path (file or directory).

    Returns:
        Path to the created lock file.

    Raises:
        SourceEngineError: If lock already exists (source already being processed).
    """
    if source_path.is_dir():
        lock_path = source_path / ".kr_processing"
    else:
        lock_path = source_path.parent / ".kr_processing"

    lock_data = json.dumps(
        {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "pid": os.getpid(),
        }
    )

    try:
        with lock_path.open("x", encoding="utf-8") as f:
            f.write(lock_data)
    except FileExistsError:
        raise make_error(
            ErrorCode.STAGING_MODIFIED,
            f"Source is already being processed (lock exists): {lock_path}",
            recovery_action="rejected",
        )

    return lock_path


def remove_staging_lock(lock_path: Path) -> None:
    """Remove .kr_processing lock file.

    Idempotent: does not raise if the lock file is already gone.

    Args:
        lock_path: Path to the lock file.
    """
    try:
        lock_path.unlink()
    except FileNotFoundError:
        pass


def cleanup_orphaned_locks(
    staging_dir: Path,
    timeout_seconds: int = 3600,
) -> list[Path]:
    """Clean up .kr_processing locks older than timeout.

    Called on engine startup to remove locks from interrupted processing.

    Args:
        staging_dir: The library/staging/ directory to scan.
        timeout_seconds: Max age in seconds before a lock is orphaned.

    Returns:
        List of removed lock file paths.
    """
    removed: list[Path] = []
    now = datetime.now(timezone.utc)

    for lock_path in staging_dir.rglob(".kr_processing"):
        try:
            lock_data = json.loads(lock_path.read_text(encoding="utf-8"))
            created_at = datetime.fromisoformat(lock_data["created_at"])
            age_seconds = (now - created_at).total_seconds()
            if age_seconds > timeout_seconds:
                lock_path.unlink()
                removed.append(lock_path)
        except (json.JSONDecodeError, KeyError, ValueError, OSError):
            # Corrupt or unreadable lock — remove it
            try:
                lock_path.unlink()
                removed.append(lock_path)
            except OSError:
                pass

    return removed


# ──────────────────────────────────────────────────────────────────
# Timestamp Recording (TOCTOU detection)
# ──────────────────────────────────────────────────────────────────


def record_file_timestamps(source_path: Path) -> dict[str, float]:
    """Record modification timestamps for all files in a source.

    Used for TOCTOU detection: at freeze time, compare current timestamps
    against these recorded values to detect concurrent modifications.

    Args:
        source_path: File or directory path.

    Returns:
        Dict mapping filename → modification time (float, seconds since epoch).
    """
    timestamps: dict[str, float] = {}

    if source_path.is_file():
        timestamps[source_path.name] = source_path.stat().st_mtime
    elif source_path.is_dir():
        for f in sorted(source_path.iterdir()):
            if f.is_file() and not f.name.startswith("."):
                timestamps[f.name] = f.stat().st_mtime

    return timestamps


def verify_timestamps_unchanged(
    source_path: Path,
    recorded_timestamps: dict[str, float],
) -> None:
    """Verify no files were modified since staging.

    Args:
        source_path: File or directory path.
        recorded_timestamps: Timestamps captured at staging time.

    Raises:
        SourceEngineError: STAGING_MODIFIED if any file's mtime changed.
    """
    current = record_file_timestamps(source_path)

    for filename, original_mtime in recorded_timestamps.items():
        current_mtime = current.get(filename)
        if current_mtime is None:
            raise make_error(
                ErrorCode.STAGING_MODIFIED,
                f"File disappeared since staging: {filename}",
                recovery_action="rejected",
            )
        if current_mtime != original_mtime:
            raise make_error(
                ErrorCode.STAGING_MODIFIED,
                f"File modified since staging: {filename}",
                recovery_action="rejected",
            )


# ──────────────────────────────────────────────────────────────────
# File Collection
# ──────────────────────────────────────────────────────────────────


def _collect_source_files(source_path: Path) -> list[Path]:
    """Collect all content files from a source path.

    For directories: all non-hidden files, sorted by name.
    For single files: just that file.

    Args:
        source_path: File or directory path.

    Returns:
        Sorted list of file paths.
    """
    if source_path.is_file():
        return [source_path]

    return sorted(
        f
        for f in source_path.iterdir()
        if f.is_file() and not f.name.startswith(".")
    )


# ──────────────────────────────────────────────────────────────────
# Main Orchestrator
# ──────────────────────────────────────────────────────────────────


def stage_source(
    source_path: Path,
    config: SourceEngineConfig,
    existing_source_ids: set[str] | None = None,
) -> StagingResult:
    """Stage a source: validate, detect format, hash, assign source_id.

    Orchestrates SPEC §4.A.2 Steps 1, 2, and partial Step 5:
    1. Validate input exists
    2. Detect format (also validates non-empty)
    3. Create staging lock
    4. Record file timestamps for TOCTOU detection
    5. Compute per-file SHA-256 hashes
    6. Derive composite hash
    7. Generate source_id with collision detection

    Args:
        source_path: Path to file or directory in staging area.
        config: Engine configuration.
        existing_source_ids: Set of existing source_ids for collision detection.

    Returns:
        StagingResult with all staging artifacts.

    Raises:
        SourceEngineError: On validation failure, format detection failure,
            or lock contention.
    """
    if not source_path.exists():
        raise make_error(
            ErrorCode.UNSUPPORTED_FORMAT,
            f"Source path does not exist: {source_path}",
        )

    # Step 2: Format detection (also validates non-empty)
    source_format = detect_format(source_path)

    # Create staging lock
    lock_path = create_staging_lock(source_path)

    try:
        # Record timestamps for TOCTOU detection at freeze time
        file_timestamps = record_file_timestamps(source_path)

        # Collect and hash all files
        files = _collect_source_files(source_path)
        file_hashes: dict[str, str] = {}
        for f in files:
            file_hashes[f.name] = compute_file_hash(f)

        # Derive composite hash and source_id
        composite_hash = compute_composite_hash(file_hashes)
        source_id = derive_source_id(composite_hash, existing_source_ids)

    except Exception:
        # Clean up lock on any failure
        remove_staging_lock(lock_path)
        raise

    return StagingResult(
        source_path=source_path,
        source_format=source_format,
        file_hashes=file_hashes,
        composite_hash=composite_hash,
        source_id=source_id,
        file_timestamps=file_timestamps,
        lock_path=lock_path,
    )
