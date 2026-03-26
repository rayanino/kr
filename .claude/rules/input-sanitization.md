---
globs: ["engines/*/src/**/*.py", "shared/*/src/**/*.py"]
---
- External text sources (Shamela HTML, PDFs, EPUB, user uploads) are UNTRUSTED. Validate encoding and strip invisible Unicode BEFORE any processing.
- Dangerous invisible characters to detect/strip at ingestion boundary: U+200B (zero-width space), U+200C/D (zero-width non-joiner/joiner), U+200E/F (LTR/RTL marks), U+202A-202E (bidi overrides), U+FEFF (BOM), U+2060 (word joiner), U+00AD (soft hyphen).
- EXCEPTION: U+200D (zero-width joiner) is VALID in Arabic ligature contexts (lam-alef لا). Strip only when outside Arabic character sequences.
- EXCEPTION: U+200C (zero-width non-joiner) is VALID in Persian/Urdu text. Preserve in manuscripts identified as Persian-origin.
- Always validate UTF-8 encoding at file read boundary. Reject latin-1, windows-1256, or mixed encoding without explicit conversion.
- Never trust external metadata (page counts, chapter counts, author names) without cross-validation against content-derived signals.
- Log all sanitization actions with before/after character counts for audit trail (knowledge integrity principle).
