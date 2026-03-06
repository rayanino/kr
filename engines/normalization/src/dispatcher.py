"""Normalization engine dispatcher — SPEC §4.A.1.

Routes frozen sources to the correct normalizer based on source_format.
The dispatcher knows nothing about any format — it only maps source_format
strings to normalizer instances.

Implementation order: Step 1 (after output schema upgrade).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.source.contracts import SourceFormat, SourceMetadata

# TODO (Claude Code): Populate this map as normalizers are built.
# First entry: SourceFormat.SHAMELA_HTML → ShamelaNormalizer
_NORMALIZER_REGISTRY: dict[SourceFormat, type[BaseNormalizer]] = {}


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


def register_normalizer(
    source_format: SourceFormat,
    normalizer_cls: type[BaseNormalizer],
) -> None:
    """Register a normalizer for a source format.

    SPEC §4.A.1: Adding a new normalizer requires only registering it here.
    No Phase 2 code changes. No schema changes.
    """
    _NORMALIZER_REGISTRY[source_format] = normalizer_cls
