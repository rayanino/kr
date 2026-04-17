---
globs: ["engines/*/src/**/*.py", "shared/*/src/**/*.py"]
---
- External text sources (Shamela HTML, PDFs, EPUB, user uploads) are UNTRUSTED. Validate encoding and strip invisible Unicode BEFORE any processing.
- Dangerous invisible characters to detect/strip at ingestion boundary: U+200B (zero-width space), U+200C/D (zero-width non-joiner/joiner), U+200E/F (LTR/RTL marks), U+202A-202E (bidi overrides), U+FEFF (BOM), U+2060 (word joiner), U+00AD (soft hyphen).
- U+200D (zero-width joiner) is NOT required for standard Arabic ligatures — lam-alef (لا) and all other mandatory Arabic ligatures are produced automatically by the rendering engine from the base characters (Lam + Alef → لا), without an explicit ZWJ. In standard Arabic scholarly text, U+200D is almost always formatting noise from HTML exports, OCR artifacts, or non-standard copy-paste sources and should be stripped at ingestion. PRESERVE U+200D only when: (a) the source is Persian/Urdu/Kurdish where ZWJ genuinely controls compound-letter shaping, or (b) the document explicitly requires zero-width formatting for a non-rendering purpose documented by the source. When stripping, log every occurrence with byte offset for audit (invisible characters are a T-1 corruption vector).
- EXCEPTION: U+200C (zero-width non-joiner) is VALID in Persian/Urdu text. Preserve in manuscripts identified as Persian-origin.
- Always validate UTF-8 encoding at file read boundary. Reject latin-1, windows-1256, or mixed encoding without explicit conversion.
- Never trust external metadata (page counts, chapter counts, author names) without cross-validation against content-derived signals.
- Log all sanitization actions with before/after character counts for audit trail (knowledge integrity principle).
