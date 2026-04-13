"""Plain Text Metadata Extractor — SPEC §4.A.3

Minimal extraction from .txt files. Title from first non-preamble line.
Most metadata comes from LLM inference (§4.A.4).
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from engines.source.contracts import ErrorCode
from engines.source.src.exceptions import make_error

# Common Islamic preamble lines that precede the actual title.
_PREAMBLE_PREFIXES: tuple[str, ...] = ("بسم الله", "الحمد لله")


def extract_plaintext_metadata(
    file_path: Path, detected_encoding: str = "utf-8"
) -> dict[str, Any]:
    """Extract metadata from a plain text file.

    Title is taken from the first non-preamble line. Everything else
    (author, genre, science, structural format) comes from LLM inference.

    Args:
        file_path: Path to the .txt file.
        detected_encoding: Encoding detected in Step 3 (§4.A.2).

    Returns:
        Dict of extracted metadata fields.

    Raises:
        SourceEngineError: UNSUPPORTED_FORMAT if the file cannot be decoded.
    """
    try:
        text = file_path.read_text(encoding=detected_encoding)
    except (UnicodeDecodeError, LookupError) as exc:
        raise make_error(
            ErrorCode.UNSUPPORTED_FORMAT,
            f"Cannot decode {file_path.name} with encoding '{detected_encoding}'",
            context={"file": str(file_path), "encoding": detected_encoding},
        ) from exc

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    # Skip common Islamic preamble lines to find the actual title.
    title_line = lines[0] if lines else file_path.stem
    if any(title_line.startswith(p) for p in _PREAMBLE_PREFIXES) and len(lines) > 1:
        title_line = lines[1]

    return {
        "title_arabic": title_line,
        "page_count": None,
        "text_sample": text[:2000],
        "format_specific_metadata": {
            "char_count": len(text),
            "line_count": len(lines),
            "detected_encoding": detected_encoding,
        },
    }
