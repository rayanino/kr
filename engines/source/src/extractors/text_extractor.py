"""Plain text metadata extractor — SPEC §4.A.3.

Minimal extraction: title from filename or first line,
page count from character count estimation.
"""

from pathlib import Path

from .base import BaseExtractor, ExtractedMetadata, ExtractionError


class TextExtractor(BaseExtractor):
    """Extract metadata from plain text files."""

    def supported_format(self) -> str:
        return "plain_text"

    def extract(self, source_path: Path) -> ExtractedMetadata:
        source_path = Path(source_path)
        if not source_path.exists():
            raise ExtractionError(f"Text file not found: {source_path}")

        try:
            text = source_path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            try:
                text = source_path.read_text(encoding="utf-8-sig")
            except UnicodeDecodeError:
                text = source_path.read_text(encoding="cp1256")

        metadata = ExtractedMetadata()

        # Title from first non-empty line
        lines = text.split("\n")
        for line in lines[:5]:
            line = line.strip()
            if len(line) >= 3:
                metadata.title_arabic = line[:200]
                break

        # If no title from content, use filename
        if not metadata.title_arabic:
            stem = source_path.stem
            # Convert filename to something readable
            metadata.title_arabic = stem.replace("_", " ").replace("-", " ")

        # Text sample (first 2000 chars)
        metadata.text_sample = text[:2000] if text else None

        # Estimate page count (~250 words per page, ~5 chars per Arabic word)
        char_count = len(text)
        metadata.page_count = max(1, char_count // 1250)

        metadata.format_specific = {
            "encoding_detected": "utf-8",
            "character_count": char_count,
            "line_count": len(lines),
        }

        return metadata
