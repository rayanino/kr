# Test Fixtures

Minimal test data for engine testing. Real Arabic text from actual scholarly sources.

## html_export_minimal/

A minimal HTML export source based on شرح ابن عقيل على ألفية ابن مالك (Ibn Aqil's Commentary on Ibn Malik's Alfiyyah). This is a multi-layer text: the ألفية (versified grammar) is the matn, and ابن عقيل's commentary is the sharh.

**Files:**
- `info.html` — Book metadata (title, author, muhaqiq, publisher, edition, volume count, genre)
- `content.html` — Two pages of actual text with: chapter heading, matn verses (CSS class `matn`), sharh paragraphs (CSS class `sharh`), footnotes, page/volume markers

**What this fixture tests:**
- Source engine: metadata extraction from structured HTML (title, author, muhaqiq, publisher, genre)
- Source engine: multi-layer detection (matn + sharh)
- Source engine: genre chain detection (sharh → base work "ألفية ابن مالك" by "ابن مالك")
- Normalization engine: HTML parsing, heading hierarchy, page break detection
- Normalization engine: matn/sharh layer separation
- Normalization engine: footnote extraction and marker normalization

Note: This happens to use a Shamela-like HTML structure, but the source engine and normalization engine handle ALL formats. Additional fixtures for PDF, plain text, and other formats should be added.

**Expected source metadata (for test assertions):**
- title_arabic: "شرح ابن عقيل على ألفية ابن مالك"
- author: ابن عقيل (commentator)
- is_multi_layer: true
- text_layers: [matn by ابن مالك, sharh by ابن عقيل]
- genre_chain: {type: sharh, base_work: "ألفية ابن مالك", base_author: "ابن مالك"}
- science_scope: ["nahw"] (Arabic grammar)
- muhaqiq: "محمد محيي الدين عبد الحميد"
- publisher: "دار التراث - القاهرة"
- volume_count: 4

## Adding New Fixtures

When adding test data:
1. Use REAL Arabic text from actual scholarly sources, never transliterated or placeholder text
2. Include both simple cases (single-layer, no footnotes) and complex cases (multi-layer, footnotes, poetry)
3. Document expected outputs in this README so tests can assert against them
4. Keep fixtures MINIMAL — just enough to test the behavior, not entire books
