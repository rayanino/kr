# How One Book Moves Through KR

This page follows one book from the moment the owner adds it to the moment it appears in the library under the right subject.

```mermaid
flowchart TD
    owner["Owner adds a book<br/>Example: Shamela HTML export"]
    raw["Raw book file<br/>Title, author field, publisher field, page text"]
    frozen["Frozen original + source record<br/>The original file is preserved exactly as it arrived"]
    normalized["Normalized reading package<br/>Same text, but now with clear pages, structure, footnotes, and text layers"]
    passages["Passages<br/>The book is cut into manageable reading sections"]
    atoms["Small meaning units<br/>Statements, definitions, evidence, explanations, transitions"]
    excerpts["Teaching excerpts<br/>The system groups the right units together into one study-worthy excerpt"]
    reviewed["Checked and flagged<br/>Clear cases continue, uncertain cases can be sent to review"]
    placed["Placed in a science tree<br/>Example: العقيدة / Aqidah -> الأسماء والصفات"]
    entry["Readable library result<br/>Teaching unit appears in the library under the right science tree"]

    owner --> raw --> frozen --> normalized --> passages --> atoms --> excerpts --> reviewed --> placed --> entry
```

## What each step means in normal language

1. The owner adds a book, usually a source file exported from Shamela.
2. KR preserves the original file exactly, so nothing important is silently changed.
3. KR turns the raw format into a clean internal book package with pages, headings, footnotes, and text layers.
4. The book is broken into reading-sized parts.
5. Those parts are broken further into the smallest meaningful scholarly units.
6. KR groups the right units together into one teaching excerpt that can stand on its own.
7. If something is uncertain, KR can stop and ask for review instead of pretending it is sure.
8. The excerpt is placed into the right subject tree.
9. The library can then show that teaching unit in the right place, ready for later synthesis and study.

## Example journey

- `كتاب التوحيد / Kitab al-Tawhid` enters as an HTML file.
- KR preserves the file, reads its structure, and identifies its internal sections.
- A section about `القدر / Divine Decree` becomes passages, then smaller meaning units.
- KR turns those units into a teaching excerpt.
- That excerpt is placed under `العقيدة / Aqidah`.
- The owner eventually sees it in the library where it belongs.

## Important note

This page uses the owner-facing 7-stage journey. In the current implementation, some passaging and atomization work happens inside the excerpting engine, but the owner-facing flow is still the same journey shown above.
