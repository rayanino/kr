"""Image/Photo Scan Metadata Extractor — SPEC §4.A.3

Uses Google Document AI or QARI-OCR for Arabic OCR on first image.
OCR confidence < 0.70 on title/author → SRC_OCR_LOW_QUALITY → human gate.
Required owner input: work title + author name (cannot auto-extract reliably).
"""
