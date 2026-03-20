"""Normalization engine dispatcher — SPEC §4.A.1.

Routes frozen sources to the correct normalizer based on source_format.
The dispatcher knows nothing about any format — it only maps source_format
strings to normalizer instances.

Also provides normalize_and_write() for end-to-end flow (D6-2):
  normalize → validate → write atomically.
"""

from __future__ import annotations

import logging
from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.normalization.src.normalizers.plain_text import PlainTextNormalizer
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
from engines.source.contracts import SourceFormat, SourceMetadata

logger = logging.getLogger(__name__)

# D6-7: Registry populated at module level via dict literal.
_NORMALIZER_REGISTRY: dict[SourceFormat, type[BaseNormalizer]] = {
    SourceFormat.SHAMELA_HTML: ShamelaNormalizer,
    SourceFormat.PLAIN_TEXT: PlainTextNormalizer,
}


def normalize_source(
    frozen_path: Path,
    metadata: SourceMetadata,
) -> NormalizedPackage:
    """Entry point for the normalization engine.

    SPEC §4.A.1: Read source_format from metadata, select matching normalizer,
    invoke it. If source_format is not in the registry, raise NORM_UNKNOWN_SOURCE_FORMAT.

    Args:
        frozen_path: Path to the frozen source directory.
        metadata: The source metadata record from the source engine.

    Returns:
        A NormalizedPackage conforming to the universal schema.

    Raises:
        NormalizationError: On any fatal error.
    """
    normalizer_cls = _NORMALIZER_REGISTRY.get(metadata.source_format)
    if normalizer_cls is None:
        raise NormalizationError(
            code=NormErrorCode.UNKNOWN_SOURCE_FORMAT,
            message=f"No normalizer registered for source_format={metadata.source_format.value}",
            source_id=metadata.source_id,
            recovery="Register a normalizer or correct the source_format in metadata.",
        )

    normalizer = normalizer_cls()
    normalizer.validate_input(frozen_path, metadata)
    return normalizer.normalize(frozen_path, metadata)


def normalize_and_write(
    frozen_path: Path,
    metadata: SourceMetadata,
    library_root: Path,
) -> Path:
    """Full pipeline: normalize → validate → write atomically (D6-2).

    Returns path to the written normalized/ directory.
    Raises NormalizationError on validation failure or write failure.
    """
    from engines.normalization.src.validation import validate_package
    from engines.normalization.src.writer import (
        recover_interrupted_write,
        write_normalized_package,
    )

    # Recovery check before processing
    recover_interrupted_write(metadata.source_id, library_root)

    # Normalize (includes format-specific input validation via validate_input)
    package = normalize_source(frozen_path, metadata)

    # §5 Layer 1 validation
    result = validate_package(package, metadata)

    # Log warnings (they're non-fatal but must not be silently discarded)
    for warning in result.warnings:
        logger.warning("[%s] §5 validation warning: %s", metadata.source_id, warning)

    # Propagate warnings into manifest.normalization_warnings for persistence
    package.manifest.normalization_warnings.extend(result.warnings)

    if not result.passed:
        # Collect error messages for diagnostics
        error_msgs = "; ".join(e.message for e in result.fatal_errors)
        raise NormalizationError(
            code=NormErrorCode.SCHEMA_VIOLATION,
            message=f"§5 validation failed with {len(result.fatal_errors)} fatal error(s): {error_msgs}",
            source_id=metadata.source_id,
            recovery="Fix the normalization bug indicated by the validation errors.",
        )

    # Atomic write
    return write_normalized_package(package, metadata.source_id, library_root)


def register_normalizer(
    source_format: SourceFormat,
    normalizer_cls: type[BaseNormalizer],
) -> None:
    """Register a normalizer for a source format.

    SPEC §4.A.1: Adding a new normalizer requires only registering it here.
    No Phase 2 code changes. No schema changes.
    """
    _NORMALIZER_REGISTRY[source_format] = normalizer_cls
