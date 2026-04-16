from __future__ import annotations

import logging
from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.errors import NormalizationError, NormErrorCode
from engines.normalization.src.normalizers.base import BaseNormalizer
from engines.source.contracts import SourceMetadata


logger = logging.getLogger(__name__)


class DeferredPdfNormalizer(BaseNormalizer):
    """Fail-loud placeholder until PDF normalization is implemented."""

    def validate_input(self, frozen_path: Path, metadata: SourceMetadata) -> None:
        if not frozen_path.exists():
            raise NormalizationError(
                code=NormErrorCode.MISSING_FROZEN,
                message=f"Frozen path does not exist: {frozen_path}",
                source_id=metadata.source_id,
                recovery="Provide a valid frozen PDF path.",
            )

    def normalize(self, frozen_path: Path, metadata: SourceMetadata) -> NormalizedPackage:
        raise NormalizationError(
            code=NormErrorCode.UNKNOWN_SOURCE_FORMAT,
            message=f"PDF normalization is not implemented for {metadata.source_format.value}",
            source_id=metadata.source_id,
            recovery="Implement the PDF normalizer before consuming PDF handoff bundles.",
        )
