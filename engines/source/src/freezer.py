"""Source Freezing — SPEC §4.A.2 Steps 5-6

Freezes raw source files by copying them to the library's frozen directory
and verifying integrity via SHA-256 hash comparison.

Steps:
1. Verify staging hashes match file content (TOCTOU detection)
2. Create frozen directory: library/sources/{source_id}/frozen/
3. Copy all files from staging to frozen
4. Re-hash frozen files, verify they match staging hashes
5. Set frozen files read-only (chmod 0444)

Uses compute_file_hash, compute_composite_hash from staging.py.
"""

from __future__ import annotations

import logging
import shutil
import stat
from dataclasses import dataclass, field
from pathlib import Path

from engines.source.contracts import ErrorCode
from engines.source.src.exceptions import make_error
from engines.source.src.staging import (
    compute_composite_hash,
    compute_file_hash,
)

logger = logging.getLogger(__name__)


@dataclass
class FreezeResult:
    """Result of a freeze operation."""

    source_id: str
    frozen_path: Path
    frozen_hash: str
    frozen_file_hashes: dict[str, str]
    file_count: int


# ──────────────────────────────────────────────────────────────────
# TOCTOU Integrity Check
# ──────────────────────────────────────────────────────────────────


def verify_staging_integrity(
    staged_path: Path,
    recorded_hashes: dict[str, str],
    recorded_timestamps: dict[str, float],
) -> None:
    """Verify staged files haven't changed since staging (TOCTOU detection).

    Compares file modification times against recorded values.
    If any file was modified after staging, raises SRC_STAGING_MODIFIED.

    Args:
        staged_path: Path to the staged source directory or file.
        recorded_hashes: Filename -> SHA-256 from staging.
        recorded_timestamps: Filename -> mtime from staging.

    Raises:
        SourceEngineError: SRC_STAGING_MODIFIED if any file changed or is missing.
    """
    for filename, recorded_mtime in recorded_timestamps.items():
        if staged_path.is_dir():
            file_path = staged_path / filename
        else:
            file_path = staged_path

        if not file_path.exists():
            raise make_error(
                error_code=ErrorCode.STAGING_MODIFIED,
                message=f"Staged file disappeared: {filename}",
                context={"filename": filename},
            )

        current_mtime = file_path.stat().st_mtime
        if current_mtime != recorded_mtime:
            raise make_error(
                error_code=ErrorCode.STAGING_MODIFIED,
                message=f"Staged file modified after staging: {filename}",
                context={
                    "filename": filename,
                    "recorded_mtime": recorded_mtime,
                    "current_mtime": current_mtime,
                },
            )


# ──────────────────────────────────────────────────────────────────
# Main Freeze Function
# ──────────────────────────────────────────────────────────────────


def freeze_source(
    staged_path: Path,
    source_id: str,
    library_root: Path,
    staging_hashes: dict[str, str],
    staging_timestamps: dict[str, float] | None = None,
) -> FreezeResult:
    """Freeze staged files to the library.

    Copies source files to library/sources/{source_id}/frozen/, verifies
    each copy is byte-identical to its origin via SHA-256, then sets each
    frozen file read-only (0o444). On Windows, chmod may silently fail —
    a warning is logged but no error is raised.

    Args:
        staged_path: Path to staged source (file or directory).
        source_id: Already-derived source_id (e.g. 'src_a1b2c3d4').
        library_root: Root library path (e.g. Path("library")).
        staging_hashes: Filename -> SHA-256 from staging.
        staging_timestamps: Filename -> mtime from staging (enables TOCTOU check).

    Returns:
        FreezeResult with frozen path, composite hash, per-file hashes, and count.

    Raises:
        SourceEngineError: SRC_STAGING_MODIFIED on TOCTOU violation.
        SourceEngineError: SRC_FREEZE_COPY_CORRUPT on hash mismatch after copy.
    """
    # Step 1: TOCTOU check (only when timestamps were recorded at staging time)
    if staging_timestamps:
        verify_staging_integrity(staged_path, staging_hashes, staging_timestamps)

    # Step 2: Create frozen directory
    frozen_dir = library_root / "sources" / source_id / "frozen"
    frozen_dir.mkdir(parents=True, exist_ok=True)

    # Step 3: Collect source files (sorted for determinism)
    if staged_path.is_dir():
        source_files: list[Path] = sorted(
            f
            for f in staged_path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        )
    else:
        source_files = [staged_path]

    # Steps 3-5: Copy, verify, set read-only
    frozen_hashes: dict[str, str] = {}

    for src_file in source_files:
        dst_file = frozen_dir / src_file.name

        shutil.copy2(src_file, dst_file)

        # Step 4: Re-hash the frozen copy and compare against staging hash
        frozen_hash = compute_file_hash(dst_file)
        frozen_hashes[src_file.name] = frozen_hash

        expected_hash = staging_hashes.get(src_file.name)
        if expected_hash is not None and frozen_hash != expected_hash:
            # Corruption detected — attempt cleanup, then fail loudly
            try:
                shutil.rmtree(frozen_dir)
            except OSError as cleanup_err:
                logger.error(
                    "Failed to clean up corrupt freeze directory %s: %s",
                    frozen_dir,
                    cleanup_err,
                )
            raise make_error(
                error_code=ErrorCode.FREEZE_COPY_CORRUPT,
                message=f"Frozen file hash mismatch for {src_file.name}",
                source_id=source_id,
                context={
                    "filename": src_file.name,
                    "staging_hash": expected_hash,
                    "frozen_hash": frozen_hash,
                },
            )

        # Step 5: Set read-only — Windows may silently ignore this, log if it fails
        try:
            dst_file.chmod(stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)  # 0o444
        except OSError as chmod_err:
            logger.warning(
                "chmod 0444 failed for %s (expected on Windows): %s",
                dst_file,
                chmod_err,
            )

    composite_hash = compute_composite_hash(frozen_hashes)

    logger.info(
        "Frozen %d file(s) for %s → %s (composite: %s...)",
        len(frozen_hashes),
        source_id,
        frozen_dir,
        composite_hash[:16],
    )

    return FreezeResult(
        source_id=source_id,
        frozen_path=frozen_dir,
        frozen_hash=composite_hash,
        frozen_file_hashes=frozen_hashes,
        file_count=len(frozen_hashes),
    )
