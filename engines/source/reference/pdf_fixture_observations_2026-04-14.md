# PDF Fixture Observations — 2026-04-14

Method: PyMuPDF (`fitz`) direct text extraction via `page.get_text("text")`, page-image counting via `page.get_images(full=True)`, and page-count inspection on the two source-engine PDF fixtures.

## Fixture 1 — `tests/fixtures/waraqat_usul/waraqat.pdf`

- Physical pages: `13`
- Pages with extractable visible text: `13 / 13`
- Total visible extracted characters: `18,458`
- Arabic-script characters: `18,121` (`98.17%` of visible characters)
- Extracted diacritic code points: `2,820` (`15.56%` of Arabic-script characters)
- Sample direct-extraction output from page 1:
  - `منت الورقات إلماـ احلرمني أيب ادلعايل اجلويين`
  - `نسخة زلققة كمشكلة كهبا سندنا للمؤلف`
- Sample direct-extraction output from page 2:
  - `احلمد هلل الذل أرسل رسولو باذلدل كدين احلق`

Observed reality:

- The PDF has a text layer across the whole document.
- Raw extraction looks "Arabic enough" by character ratio and even preserves many diacritics.
- The extracted text is still corrupt at the word level. Recurrent corruption patterns include glyph-order damage (`احلرمني` for `الحرمين`) and wrong character mapping (`الذل` for `الذي`, `كدين` for `ودين`).
- Conclusion: text presence and Arabic-character ratio are not sufficient to trust a PDF text layer. This fixture must route through a text-quality check and then to OCR, not to direct downstream use.

## Fixture 2 — `tests/fixtures/ibn_aqil_alfiyyah/vol6.pdf`

- Physical pages: `398`
- Pages with extractable visible text: `0 / 398`
- Total visible extracted characters: `0`
- Pages with image content but no extractable text: `398 / 398`

Observed reality:

- The PDF is a pure scanned-image volume with no usable text layer.
- Conclusion: this fixture is the "absent text layer" case and must route directly to OCR.

## Design Implications

The fixtures establish three real routing cases for source-engine PDF intake:

1. `absent` text layer: no usable extracted text, OCR required.
2. `corrupt` text layer: extractable text exists but fails quality review, OCR still required.
3. `clean` text layer: extractable text exists and passes quality review, direct extraction allowed.

Additional constraints derived from the fixtures:

- `waraqat.pdf` proves that extracted-text presence, extracted-text area, Arabic-character ratio, and raw diacritic count can all look healthy while the text remains unusable.
- PDF routing must therefore run a text-quality assessment, not a text-presence check.
- Diacritic fidelity must be assessed after the chosen extraction path. A corrupt direct text layer can preserve many diacritics while still corrupting the words that carry them.
