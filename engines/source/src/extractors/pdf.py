"""PDF Metadata Extractor — SPEC §4.A.3

Uses Docling for PDF parsing.
Text-embedded PDFs: extract metadata from PDF properties + TOC from bookmarks.
Scanned PDFs: limited OCR on first 1-3 pages for title/author.
"""
