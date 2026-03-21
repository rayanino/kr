"""Atomic write procedure — SPEC §4.A.2 Pass 6.

Guarantees that library/sources/{source_id}/normalized/ either contains
a complete, validated package or does not exist — no partial state is possible.

Procedure:
  1. Write to temporary directory (normalized_tmp_{timestamp}/)
  2. Write and flush manifest.json + content.jsonl
  3. Verify both files (existence, non-zero size, valid JSON/JSONL parse)
  4. If previous normalized/ exists, rename to normalized_prev_{timestamp}/
  5. Atomically rename temp directory to normalized/
  6. Delete prev directory only after new package passes verification
  7. On any failure: remove temp directory, raise NORM_WRITE_FAILED
"""

from __future__ import annotations

import json
import logging
import os
import shutil
from datetime import datetime, timezone
from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode

logger = logging.getLogger(__name__)


def _flush_and_sync(f: object) -> None:
    """Flush file buffer and fsync the file descriptor."""
    # typing: f is a file object with flush() and fileno()
    flush_fn = getattr(f, "flush", None)
    fileno_fn = getattr(f, "fileno", None)
    if flush_fn:
        flush_fn()
    if fileno_fn:
        try:
            os.fsync(fileno_fn())
        except OSError:
            pass  # fsync may not be available on all platforms


def _timestamp() -> str:
    """UTC timestamp for directory naming."""
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")


def _verify_written_files(directory: Path) -> bool:
    """Verify manifest.json and content.jsonl exist, are non-zero, parse as JSON/JSONL."""
    manifest_path = directory / "manifest.json"
    content_path = directory / "content.jsonl"

    if not manifest_path.exists() or manifest_path.stat().st_size == 0:
        return False
    if not content_path.exists() or content_path.stat().st_size == 0:
        return False

    try:
        with open(manifest_path, encoding="utf-8") as f:
            json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    try:
        with open(content_path, encoding="utf-8") as f:
            lines = f.readlines()
            if not lines:
                return False
            # Verify first and last lines parse as JSON
            json.loads(lines[0])
            json.loads(lines[-1])
    except (json.JSONDecodeError, OSError, IndexError):
        return False

    return True


def _parse_timestamp_from_dirname(dirname: str, prefix: str) -> str:
    """Extract timestamp string from a directory name like 'normalized_prev_20260317T115500'."""
    if dirname.startswith(prefix):
        return dirname[len(prefix):]
    return ""


def _cleanup_dirs(base_dir: Path, pattern: str) -> None:
    """Remove all directories matching a glob pattern."""
    for d in sorted(base_dir.glob(pattern)):
        if d.is_dir():
            shutil.rmtree(d, ignore_errors=True)


def write_normalized_package(
    package: NormalizedPackage,
    source_id: str,
    library_root: Path,
) -> Path:
    """Write a validated normalized package to disk atomically.

    Args:
        package: The validated normalized package.
        source_id: The source identifier.
        library_root: Root path of the library (contains sources/ directory).

    Returns:
        Path to the written normalized/ directory.

    Raises:
        NormalizationError(NORM_WRITE_FAILED): On any write or verification failure.
    """
    base_dir = library_root / "sources" / source_id
    final_dir = base_dir / "normalized"
    ts = _timestamp()
    temp_dir = base_dir / f"normalized_tmp_{ts}"

    try:
        # Create parent + temp directory
        temp_dir.mkdir(parents=True, exist_ok=True)

        # Write manifest.json
        manifest_path = temp_dir / "manifest.json"
        with open(manifest_path, "w", encoding="utf-8") as f:
            f.write(package.manifest.model_dump_json(indent=2))
            _flush_and_sync(f)

        # Write content.jsonl
        content_path = temp_dir / "content.jsonl"
        with open(content_path, "w", encoding="utf-8") as f:
            for cu in package.content_units:
                f.write(cu.model_dump_json())
                f.write("\n")
            _flush_and_sync(f)

        # Verify written files
        if not _verify_written_files(temp_dir):
            raise OSError("Written files failed verification")

        # Clean up old normalized_prev_* directories
        _cleanup_dirs(base_dir, "normalized_prev_*")

        # If previous normalized/ exists, rename to normalized_prev_*
        if final_dir.exists():
            prev_dir = base_dir / f"normalized_prev_{ts}"
            final_dir.rename(prev_dir)

        # Atomic rename: temp → final
        try:
            temp_dir.rename(final_dir)
        except OSError:
            # Fallback for cross-device or Windows
            shutil.move(str(temp_dir), str(final_dir))

        # Delete all normalized_prev_* directories
        _cleanup_dirs(base_dir, "normalized_prev_*")

        return final_dir

    except NormalizationError:
        raise
    except Exception as e:
        # Clean up temp on failure
        if temp_dir.exists():
            shutil.rmtree(temp_dir, ignore_errors=True)
        raise NormalizationError(
            code=NormErrorCode.WRITE_FAILED,
            message=f"Atomic write failed: {e}",
            source_id=source_id,
            recovery="Investigate the write failure and retry.",
        ) from e


def recover_interrupted_write(
    source_id: str,
    library_root: Path,
) -> bool:
    """Recover from an interrupted atomic write.

    SPEC §4.A.2 line 237: check for orphaned state at startup.

    Returns:
        True if any recovery action was taken, False otherwise.
    """
    base_dir = library_root / "sources" / source_id
    if not base_dir.exists():
        return False

    final_dir = base_dir / "normalized"
    temp_dirs = sorted(base_dir.glob("normalized_tmp_*"))
    prev_dirs = sorted(base_dir.glob("normalized_prev_*"))

    if not temp_dirs:
        # L-011: prev-only orphan state — final_dir was renamed to prev but
        # temp→final rename failed and exception handler cleaned up temp.
        if not final_dir.exists() and prev_dirs:
            latest_prev = max(
                prev_dirs,
                key=lambda p: _parse_timestamp_from_dirname(
                    p.name, "normalized_prev_"
                ),
            )
            try:
                latest_prev.rename(final_dir)
            except OSError:
                shutil.move(str(latest_prev), str(final_dir))
            # Clean up remaining prevs
            for pd in prev_dirs:
                if pd.exists():
                    shutil.rmtree(pd, ignore_errors=True)
            logger.info(
                "[%s] NORM_WRITE_RECOVERY: restored from orphaned prev '%s'",
                source_id,
                latest_prev.name,
            )
            return True
        return False

    # Case: temp exists but normalized/ already exists → orphaned temp
    if final_dir.exists():
        for td in temp_dirs:
            shutil.rmtree(td, ignore_errors=True)
        logger.info(
            "[%s] NORM_WRITE_RECOVERY: cleaned up orphaned temp dir(s)", source_id
        )
        return True

    # Case: temp exists, no normalized/, prev dir(s) exist
    if prev_dirs:
        # Try to validate the temp dir
        temp = temp_dirs[0]
        if _verify_written_files(temp):
            # Valid temp → promote to normalized/
            try:
                temp.rename(final_dir)
            except OSError:
                shutil.move(str(temp), str(final_dir))
            # Clean up remaining temps and all prevs
            for td in temp_dirs[1:]:
                shutil.rmtree(td, ignore_errors=True)
            for pd in prev_dirs:
                shutil.rmtree(pd, ignore_errors=True)
            logger.info(
                "[%s] NORM_WRITE_RECOVERY: promoted valid temp to normalized/",
                source_id,
            )
        else:
            # Invalid temp → restore from LATEST prev (ADV-047)
            latest_prev = max(
                prev_dirs,
                key=lambda p: _parse_timestamp_from_dirname(p.name, "normalized_prev_"),
            )
            try:
                latest_prev.rename(final_dir)
            except OSError:
                shutil.move(str(latest_prev), str(final_dir))
            # Clean up all temps and remaining prevs
            for td in temp_dirs:
                shutil.rmtree(td, ignore_errors=True)
            for pd in prev_dirs:
                if pd.exists():
                    shutil.rmtree(pd, ignore_errors=True)
            logger.info(
                "[%s] NORM_WRITE_RECOVERY: restored from latest prev '%s'",
                source_id,
                latest_prev.name,
            )
        return True

    # Case: temp exists, no normalized/, no prev dirs
    # Orphaned temp with no backup — just clean up
    for td in temp_dirs:
        shutil.rmtree(td, ignore_errors=True)
    logger.info(
        "[%s] NORM_WRITE_RECOVERY: cleaned up orphaned temp (no prev available)",
        source_id,
    )
    return True
