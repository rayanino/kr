"""Format detection — SPEC §4.A.2 Step 2.

Determines source format from file extension, content inspection,
and directory structure.
"""

from pathlib import Path

# Use string literals matching SourceFormat enum values
_EXTENSION_MAP: dict[str, str] = {
    ".htm": "shamela_html",
    ".html": "shamela_html",  # May need content inspection to confirm
    ".pdf": "_pdf",           # Needs further inspection (text vs scanned)
    ".epub": "epub",
    ".txt": "plain_text",
    ".doc": "word_doc",
    ".docx": "word_doc",
    ".jpg": "image_scan",
    ".jpeg": "image_scan",
    ".png": "image_scan",
    ".tiff": "image_scan",
    ".tif": "image_scan",
    ".heic": "image_scan",
}


def detect_format(source_path: Path) -> str:
    """Detect the source format.

    Args:
        source_path: Path to the source file or directory.

    Returns:
        A SourceFormat enum value string.

    Raises:
        ValueError: If format cannot be determined (SRC_UNSUPPORTED_FORMAT).
    """
    source_path = Path(source_path)

    if source_path.is_file():
        return _detect_single_file(source_path)

    if source_path.is_dir():
        return _detect_directory(source_path)

    raise ValueError(f"SRC_UNSUPPORTED_FORMAT: Path does not exist: {source_path}")


def _detect_single_file(filepath: Path) -> str:
    """Detect format of a single file."""
    ext = filepath.suffix.lower()

    if ext not in _EXTENSION_MAP:
        raise ValueError(
            f"SRC_UNSUPPORTED_FORMAT: Unrecognized file type '{ext}'. "
            f"Supported: {', '.join(sorted(set(_EXTENSION_MAP.keys())))}"
        )

    format_hint = _EXTENSION_MAP[ext]

    if format_hint == "_pdf":
        return _classify_pdf(filepath)

    if format_hint == "shamela_html":
        # Verify it's actually a Shamela export by checking content
        return _verify_shamela_html(filepath)

    return format_hint


def _detect_directory(dirpath: Path) -> str:
    """Detect format of a directory of files."""
    files = [f for f in dirpath.iterdir() if f.is_file() and not f.name.startswith(".")]

    if not files:
        raise ValueError(f"SRC_UNSUPPORTED_FORMAT: Directory is empty: {dirpath}")

    extensions = {f.suffix.lower() for f in files}

    # All images → image scan
    image_exts = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".heic"}
    if extensions.issubset(image_exts):
        return "image_scan"

    # All HTM/HTML → Shamela directory export
    html_exts = {".htm", ".html"}
    if extensions.issubset(html_exts | {".css", ".js"}):
        return "shamela_html"

    # All Word docs → word_doc collection
    doc_exts = {".doc", ".docx"}
    if extensions.issubset(doc_exts):
        return "word_doc"

    # Mixed or unrecognized
    raise ValueError(
        f"SRC_UNSUPPORTED_FORMAT: Cannot determine format for directory with "
        f"mixed file types: {extensions}"
    )


def _classify_pdf(filepath: Path) -> str:
    """Determine if a PDF has embedded text or is scanned.

    Uses PyMuPDF to check for extractable text on the first few pages.
    """
    try:
        import fitz
    except ImportError:
        # If PyMuPDF not available, default to text PDF
        return "pdf_text"

    try:
        doc = fitz.open(str(filepath))
        # Check first 3 pages for text content
        text_pages = 0
        check_pages = min(3, len(doc))
        for i in range(check_pages):
            page = doc[i]
            text = page.get_text().strip()
            if len(text) > 50:  # More than trivial text
                text_pages += 1
        doc.close()

        # If majority of checked pages have text, it's text-embedded
        if text_pages >= check_pages / 2:
            return "pdf_text"
        else:
            return "pdf_scanned"

    except Exception:
        # On any error, assume text PDF (safer default)
        return "pdf_text"


def _verify_shamela_html(filepath: Path) -> str:
    """Check if an HTML file is actually a Shamela export."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            # Read first 2000 chars to check for Shamela markers
            head = f.read(2000)

        shamela_markers = ["PageText", "PageNumber", "PageHead"]
        if any(marker in head for marker in shamela_markers):
            return "shamela_html"

        # It's HTML but not Shamela format — still treat as HTML
        return "plain_text"  # Fallback: treat as plain text with HTML markup
    except Exception:
        return "shamela_html"  # If we can't read it, assume Shamela based on extension
