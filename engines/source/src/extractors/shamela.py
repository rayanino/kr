"""Shamela HTML Metadata Extractor — SPEC §4.A.3

Parses info.html and PageText divs from Shamela HTML exports.
Extracts: title, author, publisher, muhaqiq, page_count, volume_structure.
Preserves shamela_book_id and shamela_category in format_specific_metadata.

Edge case: info.html absent → SRC_FORMAT_STRUCTURE_MISSING,
fall back to first PageText div content extraction.
"""
