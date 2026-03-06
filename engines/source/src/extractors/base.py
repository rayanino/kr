"""Base extractor interface — SPEC §4.A.3.

Every format-specific metadata extractor implements this interface.
Extractors are kept minimal: extract what the format provides,
then hand off to LLM inference (§4.A.4) for enrichment.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class ExtractedMetadata:
    """Raw metadata extracted from a source by a format-specific extractor.

    Fields may be None if the extractor couldn't determine them.
    The LLM inference step (§4.A.4) fills gaps and enriches.
    """
    title_arabic: str | None = None
    author_name_arabic: str | None = None
    publisher: str | None = None
    muhaqiq: str | None = None
    edition_number: int | None = None
    publication_year: int | None = None
    page_count: int | None = None
    volume_count: int | None = None

    # Text sample for LLM inference (first ~2000 chars of content)
    text_sample: str | None = None
    # Table of contents if available
    toc: list[str] = field(default_factory=list)

    # Format-specific metadata (not entered into pipeline schema)
    format_specific: dict = field(default_factory=dict)


class BaseExtractor(ABC):
    """Abstract base for format-specific metadata extractors."""

    @abstractmethod
    def extract(self, source_path: Path) -> ExtractedMetadata:
        """Extract metadata from a source file or directory.

        Args:
            source_path: Path to the frozen source file or directory.

        Returns:
            ExtractedMetadata with whatever the format provides.

        Raises:
            ExtractionError: If extraction fails critically.
        """
        ...

    @abstractmethod
    def supported_format(self) -> str:
        """Return the SourceFormat enum value this extractor handles."""
        ...


class ExtractionError(Exception):
    """Raised when metadata extraction fails."""
    pass
