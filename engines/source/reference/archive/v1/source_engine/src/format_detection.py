"""Format Detection — SPEC §4.A.2 Step 2.

Determines source format from file extension, content markers, and directory
structure. Returns a SourceFormat enum value.

Stage 1 supports two formats:
- SHAMELA_HTML: Shamela desktop .htm exports (single file or multi-volume directory)
- PLAIN_TEXT: Single .txt file with Arabic text

All other formats raise SRC_UNSUPPORTED_FORMAT.
"""

from __future__ import annotations

from pathlib import Path

from engines.source.contracts import ErrorCode, ErrorSeverity, SourceFormat
from engines.source.src.exceptions import SourceEngineError, make_error


def detect_format(path: Path) -> SourceFormat:
    """Determine source format from file or directory structure.

    Args:
        path: Path to a single file or directory in the staging area.

    Returns:
        SourceFormat enum value (SHAMELA_HTML or PLAIN_TEXT for Stage 1).

    Raises:
        SourceEngineError: EMPTY_INPUT if file is zero bytes or directory is empty.
        SourceEngineError: UNSUPPORTED_FORMAT if format cannot be determined.
    """
    if not path.exists():
        raise make_error(
            ErrorCode.UNSUPPORTED_FORMAT,
            f"Path does not exist: {path}",
        )

    if path.is_dir():
        return _detect_directory_format(path)

    if path.is_file():
        return _detect_file_format(path)

    raise make_error(
        ErrorCode.UNSUPPORTED_FORMAT,
        f"Path is neither a file nor a directory: {path}",
    )


def _detect_directory_format(path: Path) -> SourceFormat:
    """Detect format from a directory of files.

    Logic (SPEC §4.A.2):
    1. If directory is empty -> EMPTY_INPUT
    2. Collect sorted .htm/.html files; if any are Shamela -> SHAMELA_HTML
    3. Collect .txt files; if exactly one -> PLAIN_TEXT
    4. Otherwise -> UNSUPPORTED_FORMAT
    """
    children = list(path.iterdir())
    # Filter to actual content files (exclude lock files and hidden files)
    content_files = [f for f in children if f.is_file() and not f.name.startswith(".")]
    if not content_files:
        raise make_error(
            ErrorCode.EMPTY_INPUT,
            f"Directory is empty: {path}",
            severity=ErrorSeverity.FATAL,
        )

    htm_files = sorted(
        [f for f in content_files if f.suffix.lower() in (".htm", ".html")]
    )
    if htm_files and _is_shamela_html(htm_files[0]):
        return SourceFormat.SHAMELA_HTML

    txt_files = [f for f in content_files if f.suffix.lower() == ".txt"]
    if len(txt_files) == 1:
        return SourceFormat.PLAIN_TEXT

    raise make_error(
        ErrorCode.UNSUPPORTED_FORMAT,
        f"Cannot detect format of directory: {path}",
    )


def _detect_file_format(path: Path) -> SourceFormat:
    """Detect format from a single file.

    Logic (SPEC §4.A.2):
    1. If file is empty -> EMPTY_INPUT
    2. .txt -> PLAIN_TEXT
    3. .htm/.html + Shamela markers -> SHAMELA_HTML
    4. Otherwise -> UNSUPPORTED_FORMAT
    """
    if path.stat().st_size == 0:
        raise make_error(
            ErrorCode.EMPTY_INPUT,
            f"File is empty: {path}",
            severity=ErrorSeverity.FATAL,
        )

    suffix = path.suffix.lower()

    if suffix == ".txt":
        return SourceFormat.PLAIN_TEXT

    if suffix in (".htm", ".html"):
        if _is_shamela_html(path):
            return SourceFormat.SHAMELA_HTML
        raise make_error(
            ErrorCode.UNSUPPORTED_FORMAT,
            f"HTML file does not match Shamela format markers: {path}",
        )

    raise make_error(
        ErrorCode.UNSUPPORTED_FORMAT,
        f"Unsupported file extension '{suffix}': {path}",
    )


def _is_shamela_html(htm_file: Path) -> bool:
    """Check whether an .htm file is a Shamela desktop export.

    Detection markers (ALL must be present in first 3000 chars):
    1. <div class='PageText'> — Shamela page container
    2. <span class='title'> — Shamela metadata field label style
    3. <div class='Main'> — Shamela root container

    Args:
        htm_file: Path to an .htm or .html file.

    Returns:
        True if all three markers are present. False on read errors.
    """
    try:
        content = htm_file.read_text(encoding="utf-8")[:3000]
    except (UnicodeDecodeError, OSError):
        return False

    return (
        "<div class='PageText'>" in content
        and "<span class='title'>" in content
        and "<div class='Main'>" in content
    )
