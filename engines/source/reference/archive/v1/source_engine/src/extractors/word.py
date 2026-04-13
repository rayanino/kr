"""Word Document Metadata Extractor — SPEC §4.A.3

Uses Docling for .doc/.docx text and metadata extraction.
Handles directories of Word files as single multi-part sources.
Critical: Arabic filenames in ZIP archives use CP1256 → normalize to UTF-8.
"""
