"""PDF metadata extractor — SPEC §4.A.3.

Extracts metadata from PDF files using PyMuPDF.
For text-embedded PDFs: document properties + first pages.
For scanned PDFs: limited to document properties (OCR deferred to normalization).
"""

from pathlib import Path

from .base import BaseExtractor, ExtractedMetadata, ExtractionError


class PdfExtractor(BaseExtractor):
    """Extract metadata from PDF files."""

    def supported_format(self) -> str:
        return "pdf_text"  # Also handles pdf_scanned with reduced extraction

    def extract(self, source_path: Path) -> ExtractedMetadata:
        try:
            import fitz
        except ImportError:
            raise ExtractionError(
                "PyMuPDF (fitz) is required for PDF extraction. "
                "Install with: pip install pymupdf"
            )

        source_path = Path(source_path)
        if not source_path.exists():
            raise ExtractionError(f"PDF file not found: {source_path}")

        try:
            doc = fitz.open(str(source_path))
        except Exception as e:
            raise ExtractionError(f"Failed to open PDF: {e}") from e

        metadata = ExtractedMetadata()

        # Extract from PDF document properties
        pdf_meta = doc.metadata or {}
        metadata.title_arabic = pdf_meta.get("title") or None
        metadata.author_name_arabic = pdf_meta.get("author") or None
        metadata.page_count = len(doc)

        # Clean up empty strings
        if metadata.title_arabic and not metadata.title_arabic.strip():
            metadata.title_arabic = None
        if metadata.author_name_arabic and not metadata.author_name_arabic.strip():
            metadata.author_name_arabic = None

        # Extract text sample from first pages for LLM inference
        text_sample_parts = []
        for i in range(min(3, len(doc))):
            page = doc[i]
            text = page.get_text().strip()
            if text:
                text_sample_parts.append(text)

        metadata.text_sample = "\n---\n".join(text_sample_parts)[:2000] if text_sample_parts else None

        # Extract TOC (table of contents / bookmarks)
        toc = doc.get_toc()
        if toc:
            metadata.toc = [entry[1] for entry in toc]  # entry = [level, title, page]

        # Try to infer title from first page text if not in PDF properties
        if not metadata.title_arabic and metadata.text_sample:
            metadata.title_arabic = _infer_title_from_text(metadata.text_sample)

        # Store format-specific data
        metadata.format_specific = {
            "pdf_producer": pdf_meta.get("producer"),
            "pdf_creator": pdf_meta.get("creator"),
            "pdf_creation_date": pdf_meta.get("creationDate"),
            "has_toc_bookmarks": bool(toc),
            "has_embedded_text": bool(metadata.text_sample),
        }

        doc.close()
        return metadata


class ScannedPdfExtractor(BaseExtractor):
    """Extract metadata from scanned PDFs (limited — OCR is normalization's job)."""

    def supported_format(self) -> str:
        return "pdf_scanned"

    def extract(self, source_path: Path) -> ExtractedMetadata:
        # For scanned PDFs, we can only get document properties
        # OCR for title page extraction is deferred to normalization engine
        try:
            import fitz
        except ImportError:
            raise ExtractionError("PyMuPDF required for PDF handling")

        doc = fitz.open(str(source_path))
        pdf_meta = doc.metadata or {}

        metadata = ExtractedMetadata()
        metadata.title_arabic = pdf_meta.get("title") or None
        metadata.author_name_arabic = pdf_meta.get("author") or None
        metadata.page_count = len(doc)
        metadata.format_specific = {
            "pdf_producer": pdf_meta.get("producer"),
            "needs_ocr": True,
        }

        doc.close()
        return metadata


def _infer_title_from_text(text: str) -> str | None:
    """Try to infer an Arabic title from the first page text.

    Heuristic: the first substantial Arabic line on the first page
    is often the title.
    """
    lines = text.split("\n")
    for line in lines[:20]:  # Check first 20 lines
        line = line.strip()
        # Skip empty lines and very short lines
        if len(line) < 3:
            continue
        # Skip lines that are mostly non-Arabic (page numbers, URLs, etc.)
        arabic_chars = sum(1 for c in line if "\u0600" <= c <= "\u06FF" or "\u0750" <= c <= "\u077F")
        if arabic_chars > len(line) * 0.5 and arabic_chars >= 3:
            return line[:200]  # Cap at 200 chars

    return None
