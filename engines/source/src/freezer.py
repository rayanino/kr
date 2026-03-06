"""Source freezer — SPEC §4.A.2 Step 6.

Copies raw source files to the frozen directory, sets them read-only,
and computes SHA-256 hashes. After freezing, files are immutable.
"""

import os
import shutil
from pathlib import Path

from .identity import compute_file_hash, compute_composite_hash


class FreezeError(Exception):
    """Raised when freezing fails."""
    pass


def freeze_source(
    source_path: Path,
    frozen_dir: Path,
) -> tuple[str, dict[str, str]]:
    """Freeze a source file or directory.

    Args:
        source_path: Path to the source file or directory to freeze.
        frozen_dir: Target directory for frozen files (e.g., library/sources/{source_id}/frozen/).

    Returns:
        Tuple of (composite_hash, file_hashes_dict).

    Raises:
        FreezeError: If source doesn't exist, copy fails, or hash computation fails.
    """
    source_path = Path(source_path)
    frozen_dir = Path(frozen_dir)

    if not source_path.exists():
        raise FreezeError(f"Source path does not exist: {source_path}")

    # Create frozen directory
    frozen_dir.mkdir(parents=True, exist_ok=True)

    file_hashes: dict[str, str] = {}

    if source_path.is_file():
        # Single file source
        dest = frozen_dir / source_path.name
        _copy_and_protect(source_path, dest)
        file_hashes[source_path.name] = compute_file_hash(str(dest))

    elif source_path.is_dir():
        # Directory source (multi-file: Shamela export, photo set, Word doc collection)
        files = sorted(
            f for f in source_path.iterdir()
            if f.is_file() and not f.name.startswith(".")
        )
        if not files:
            raise FreezeError(f"Source directory is empty: {source_path}")

        for src_file in files:
            dest = frozen_dir / src_file.name
            _copy_and_protect(src_file, dest)
            file_hashes[src_file.name] = compute_file_hash(str(dest))
    else:
        raise FreezeError(f"Source path is neither file nor directory: {source_path}")

    composite_hash = compute_composite_hash(file_hashes)
    return composite_hash, file_hashes


def _copy_and_protect(src: Path, dest: Path) -> None:
    """Copy a file and set it read-only."""
    try:
        shutil.copy2(src, dest)
        # Set read-only (remove write permission)
        os.chmod(dest, 0o444)
    except OSError as e:
        raise FreezeError(f"Failed to freeze {src.name}: {e}") from e


def verify_frozen_integrity(frozen_dir: Path, expected_hashes: dict[str, str]) -> list[str]:
    """Verify that frozen files match their recorded hashes.

    Returns a list of error messages (empty if all OK).
    """
    errors = []
    frozen_dir = Path(frozen_dir)

    for filename, expected_hash in expected_hashes.items():
        filepath = frozen_dir / filename
        if not filepath.exists():
            errors.append(f"Missing frozen file: {filename}")
            continue

        actual_hash = compute_file_hash(str(filepath))
        if actual_hash != expected_hash:
            errors.append(
                f"Hash mismatch for {filename}: expected {expected_hash[:16]}..., "
                f"got {actual_hash[:16]}..."
            )

    # Check for unexpected files
    frozen_files = {f.name for f in frozen_dir.iterdir() if f.is_file()}
    expected_files = set(expected_hashes.keys())
    extra = frozen_files - expected_files
    if extra:
        errors.append(f"Unexpected files in frozen directory: {extra}")

    return errors
