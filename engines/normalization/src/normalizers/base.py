"""Base normalizer interface — SPEC §4.A.1.

Every normalizer implements this interface. The dispatcher selects the correct
normalizer based on source_format and invokes it. Normalizers are arbitrarily
complex internally but expose this uniform interface to the dispatcher.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from engines.normalization.contracts import NormalizedPackage
from engines.source.contracts import SourceMetadata


class BaseNormalizer(ABC):
    """Interface that every format-specific normalizer must implement.

    Input: frozen source directory path + source metadata record.
    Output: a NormalizedPackage conforming to the universal schema.
    Side effects: optional enrichment write-backs, log entries.
    """

    @abstractmethod
    def normalize(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> NormalizedPackage:
        """Transform a frozen source into a normalized package.

        SPEC §4.A.1: The normalizer may be arbitrarily complex internally.
        Its complexity is self-contained: no other normalizer and no Phase 2
        engine is affected by its internal design.

        Raises:
            NormalizationError: On any fatal error (see errors.py for codes).
        """
        ...

    @abstractmethod
    def validate_input(
        self,
        frozen_path: Path,
        metadata: SourceMetadata,
    ) -> None:
        """SPEC §5 check 9: Validate input matches expected format BEFORE processing.

        Each normalizer validates that its input is in the expected format.
        This catches wrong-normalizer-selected scenarios early.

        Raises:
            NormalizationError: With format-specific error code.
        """
        ...
