"""Format Detection — SPEC §4.A.2 Step 2

Determines source type from file extension, content inspection, and directory structure.
Returns a SourceFormat enum value.

Detection rules:
- Numbered .htm files + info.html → SHAMELA_HTML
- PDF magic bytes → PDF_TEXT or PDF_SCANNED (determined by text extraction test)
- JPEG/PNG/TIFF/HEIC files → IMAGE_SCAN
- .doc/.docx → WORD_DOC
- .epub → EPUB
- .txt → PLAIN_TEXT (or OWNER_AUTHORED if input_type provided)
- Unrecognized → SRC_UNSUPPORTED_FORMAT error
"""
