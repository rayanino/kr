"""Format-specific metadata extractors (SPEC §4.A.3).

One extractor per SourceFormat. Each extracts what the format provides,
then hands off to metadata_inference.py for LLM enrichment.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.source.contracts import ErrorCode, SourceFormat
from engines.source.src.exceptions import make_error
from engines.source.src.extractors.plain_text import extract_plaintext_metadata
from engines.source.src.extractors.shamela_html import extract_shamela_metadata


def extract_metadata(source_path: Path, source_format: SourceFormat) -> dict[str, Any]:
    """Dispatch to format-specific extractor.

    Args:
        source_path: Path to the source file or directory.
        source_format: Detected format from format_detection.

    Returns:
        Extracted metadata dictionary.

    Raises:
        SourceEngineError: If format is not supported.
    """
    if source_format == SourceFormat.SHAMELA_HTML:
        return extract_shamela_metadata(source_path)
    elif source_format == SourceFormat.PLAIN_TEXT:
        return extract_plaintext_metadata(source_path)
    else:
        raise make_error(
            error_code=ErrorCode.UNSUPPORTED_FORMAT,
            message=f"No extractor for format: {source_format}",
            context={"source_format": source_format.value},
        )
