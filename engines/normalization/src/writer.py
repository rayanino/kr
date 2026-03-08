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

Implementation order: See SPEC.md for processing rules.
"""

from __future__ import annotations

from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode


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
    # TODO (Claude Code): Implement atomic write per SPEC §4.A.2.
    raise NotImplementedError("write_normalized_package")
