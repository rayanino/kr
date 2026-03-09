# Shamela Desktop Export — Structural Analysis

**Date:** 2026-03-09
**Source:** Owner's Shamela desktop app v4 exports (2,519 books, a large subset of the full Shamela library)
**Survey method:** Automated analysis of ALL 2,519 first-files (100% coverage of exports, zero errors)

This document is the ground truth for Shamela HTML extraction rules. Every claim is derived from observation of real exports, not from documentation or guesswork. All exports are from Shamela desktop app v4; other Shamela versions (v3, online shamela.ws) may use different HTML structures. The owner's 2,519 exports are a large subset of the full Shamela library, which contains thousands more books — additional exports may reveal field labels or patterns not documented here.

---

## 1. File Structure

### Single-Volume Books (1,932 books = 76.7%)
A single `.htm` file in the export root directory. The filename IS the book title in Arabic.

Example: `آداب الحوار من خلال سيرة مصعب بن عمير رضي الله عنه.htm`

### Multi-Volume Books (587 books = 23.3%)
A directory containing numbered `.htm` files: `001.htm`, `002.htm`, etc. The directory name IS the book title in Arabic. Each `.htm` file represents one volume/part (جزء).

Example:
```
شرح ألفية ابن مالك للحازمي/
├── 001.htm     (جـ ١)
├── 002.htm     (جـ ٢)
├── ...
└── 138.htm     (جـ ١٣٨)
```

**Volume counts:** min=2, max=510, median=4

**Special file:** 68 multi-volume books (11.6%) have a `المقدمة.htm` file alongside the numbered files. This file contains the same metadata card as `001.htm` plus introductory content. The numbered files start from `001.htm`.

**No `info.html` file exists.** The synthetic fixture's assumption of a separate metadata file was completely wrong. Metadata is embedded in the content files.

### Key Finding: Every `.htm` File Has the Metadata Card
In multi-volume books, EVERY volume file (not just the first) contains the full metadata card as its first `PageText` div. This means the extractor can read metadata from any file in the directory — it doesn't need to find a specific file.

---

## 2. HTML Structure

### Document Template (100% uniform across all 2,519 exports)

```html
<!DOCTYPE html><html lang='ar' dir='rtl'>
<head>
  <meta content='text/html; charset=UTF-8' http-equiv='Content-Type'>
  <style>
    /* Standard Shamela CSS — identical across all exports */
    .Main {text-align:right; margin: 0 auto; max-width: 780px;}
    .PageText { /* Page container with beige background, border */ }
    .PageHead { /* Volume/page header bar */ }
    .PartName {float:right;}    /* Volume/book name — right-aligned */
    .PageNumber {float:left;}   /* Page number — left-aligned */
    .title {color: #800000;}    /* Dark red for field labels and section headings */
    .footnote, .PageHead {font: bold 16pt "Traditional Naskh"; color: #464646;}
  </style>
  <title>BOOK_TITLE - جـ N</title>   <!-- N = volume number for multi-vol -->
</head>
<body><div class='Main'>

  <!-- FIRST PageText = Metadata Card (always present) -->
  <div class='PageText'>...</div>

  <!-- SUBSEQUENT PageTexts = Book Pages -->
  <div class='PageText'>
    <div class='PageHead'>
      <span class='PartName'>BOOK_TITLE - جـ N</span>
      <span class='PageNumber'>(ص: ١٥)</span>
      <hr/>
    </div>
    BODY_TEXT
    <hr width='95' align='right'>
    <div class='footnote'>FOOTNOTE_TEXT</div>
  </div>

</div></body></html>
```

### CSS Classes (exhaustive list — no others exist)

| Class | Element | Purpose | Frequency |
|-------|---------|---------|-----------|
| `Main` | `div` | Root container | 100% |
| `PageText` | `div` | Page container (metadata card or body page) | 100% |
| `PageHead` | `div` | Volume/page header bar within a page | 100% |
| `PartName` | `span` | Book title + volume number (right-aligned) | 100% |
| `PageNumber` | `span` | Page number like `(ص: ١٥)` (left-aligned) | 98.2% |
| `title` | `span` | Metadata field labels AND section headings in body | 100% |
| `footnote` | `span` | Short author name in metadata card header | 100%* |
| `footnote` | `div` | Footnote block at bottom of a page | 47.5% |

*The `footnote` class serves TWO purposes: (1) the author's short name in the metadata card header `<span class='footnote'>(AuthorShort)</span>`, and (2) footnote text blocks `<div class='footnote'>...</div>` within body pages. These are distinguishable by element type (span vs div) and position (metadata card vs body page).

**CRITICAL: No `matn`, `sharh`, `hashiyah`, or `tahqiq` CSS classes exist.** Confirmed across 200 randomly sampled files with zero hits. Multi-layer detection CANNOT use CSS classes — it must rely entirely on LLM inference from content and genre.

---

## 3. Metadata Card Structure

The first `<div class='PageText'>` in every file is the metadata card. It has a fixed structure:

### Card Header (title + short author)
```html
<span class='title'>BOOK_DISPLAY_TITLE&nbsp;&nbsp;&nbsp;</span>
<span class='footnote'>(AUTHOR_SHORT_NAME)</span>
```

The display title and short author name are ALWAYS present in this header element. The short author name is in parentheses inside a `<span class='footnote'>`.

### Category Line (always present, 99.9%)
```html
<p><span class='title'>القسم:</span> CATEGORY_NAME<hr>
```

The `<hr>` separator separates the category line from the bibliographic fields below.

### Bibliographic Fields
Each field follows the pattern:
```html
<p><span class='title'>FIELD_LABEL<font color=#be0000>:</font></span> FIELD_VALUE
```

The colon `:` is wrapped in a `<font color=#be0000>` tag (dark red). Some fields omit this color wrapper and just have `:` directly.

### Field Inventory (frequency across 2,519 books)

**Primary fields (>70% of books):**

| Field Label | Arabic | Frequency | Notes |
|------------|--------|-----------|-------|
| Book title | الكتاب | 97.2% | Full title. 2.8% use `اسم الكتاب` instead |
| Author | المؤلف | 93.4% | Full author name, often with death date |
| Publisher | الناشر | 87.0% | Publisher name, sometimes with city |
| Edition | الطبعة | 73.2% | Edition number + year, e.g. "الأولى، 1435 هـ" |
| Page count | عدد الصفحات | 73.0% | Integer |
| Category | القسم | 99.9% | Science classification from Shamela |

**Secondary fields (20-50%):**

| Field Label | Arabic | Frequency | Notes |
|------------|--------|-----------|-------|
| Muhaqiq | المحقق | 31.5% | Editor name, sometimes with death date |
| Volume count | عدد الأجزاء | 20.6% | Integer |

**Tertiary fields (1-20%):**

| Field Label | Arabic | Frequency | Notes |
|------------|--------|-----------|-------|
| Preparer | أعده للشاملة | 17.4% | Who digitized for Shamela |
| Tahqiq (alt) | تحقيق | 7.0% | Alternative to المحقق |
| Publication year | عام النشر | 3.4% | Separate from الطبعة |
| Alert/Note | تنبيه | 2.2% | Editorial notes about the digital edition |
| Pages (print) | عدد صفحات (الكتاب الورقي) | 2.1% | Physical book page count |
| Study+Tahqiq | دراسة وتحقيق | 2.1% | Combined study and editing |
| Submitted by | قدمه للشاملة | 1.9% | Who submitted to Shamela |
| Reviewer | راجعه | 1.8% | Reviewer name |
| Source | مصدر الكتاب | 1.5% | Source of the digital text |
| Riwayah | رواية | 1.1% | Hadith transmission chain info |
| Thesis | رسالة | 1.1% | Academic thesis details |
| Author (alt) | إعداد | 1.0% | Alternative to المؤلف for thesis authors |

### Author Name Format

65% of author fields contain a death date in the format:
```
FULL_NAME (المتوفى: NNN هـ)
```
or (more common):
```
FULL_NAME (ت NNN هـ)
```

The `ت` abbreviation is used 64 times more frequently than `المتوفى`.

24% have plain names with no parenthetical information.
5% have parenthetical information other than death dates (e.g., roles, titles).

### Muhaqiq Name Format

Muhaqiq names sometimes include death dates in square brackets:
```
محمد محيي الدين عبد الحميد [ت ١٣٩٢ هـ]
```

The square bracket `[ت NNN هـ]` format distinguishes muhaqiq death dates from author death dates (which use parentheses).

### Multiple Muhaqiq-Like Fields

The "editor" role is expressed through SIX different field labels:
- `المحقق` (31.5%) — primary muhaqiq field
- `تحقيق` (7.0%) — alternative
- `دراسة وتحقيق` (2.1%) — study + editing
- `راجعه` (1.8%) — reviewer
- `تحقيق وتعليق` (0.8%) — editing + annotation
- `تحقيق ودراسة` (1.0%) — editing + study
- `راجعه ودققه` (rare) — reviewed and verified

All of these should be treated as muhaqiq-equivalent for trust evaluation.

### Category Values (القسم)

The top categories across the collection:
- كتب السنة (Hadith books) — most common
- التفسير (Quranic exegesis)
- النحو والصرف (Grammar & morphology)
- الفقه العام (General fiqh)
- كتب عامة (General books)
- كتب اللغة (Language books)
- أصول الفقه (Usul al-fiqh)
- البلاغة (Rhetoric)
- الفتاوى (Fatawa/legal opinions)

---

## 4. Body Page Structure

### Page Container
```html
<div class='PageText'>
  <div class='PageHead'>
    <span class='PartName'>BOOK_TITLE - جـ N</span>
    <span class='PageNumber'>(ص: ١٥)</span>
    <hr/>
  </div>
  <!-- Body text with <p> tags, <span class="title"> headings -->
  
  <!-- Optional: footnotes after <hr> separator -->
  <hr width='95' align='right'>
  <div class='footnote'>(1) FOOTNOTE_TEXT</div>
</div>
```

### Page Numbers
Format: `(ص: N)` where N is in Eastern Arabic numerals (١٢٣...). Present in 98.2% of books.

### Volume Indicator
The `PartName` span contains the book title followed by ` - جـ N` (volume number). For single-volume books, no volume suffix is present.

### Section Headings in Body
Section headings use `<span class="title">` (note: double quotes, vs single quotes in the metadata card). They are often preceded by a zero-width non-joiner character `&#8204;`:

```html
&#8204;<span class="title">&#8204;HEADING_TEXT</span>
```

Found in 82.7% of books (2,084 out of 2,519).

### Footnotes
Structure: `<hr width='95' align='right'>` separator followed by `<div class='footnote'>` block. Footnote references in body text use `(N)` numbering pattern.

### Color Markup
100% of books use `color=#be0000` (dark red) for punctuation in the metadata card. This color is NOT used to distinguish text layers — it's purely decorative for colons, brackets, and diacritical marks in the metadata card.

---

## 5. What the Synthetic Fixture Got Wrong

| Aspect | Synthetic (`html_export_minimal`) | Real Shamela Export |
|--------|----------------------------------|-------------------|
| Separate metadata file | `info.html` with `<table>` rows | No separate file; metadata in first `PageText` div |
| Metadata format | `<tr><td>key</td><td>value</td></tr>` | `<span class='title'>key:</span> value` |
| Page markers | `<span class="pg">15</span>` | `<span class='PageNumber'>(ص: ١٥)</span>` |
| Volume markers | `<span class="vol">1</span>` | `<span class='PartName'>Title - جـ ١</span>` |
| Layer CSS classes | `class="matn"`, `class="sharh"` | **Do not exist** |
| Footnotes | `<p class="footnote"><sup>1</sup>` | `<div class='footnote'>(1) text</div>` |
| Chapter headings | `<h2>` inside `<div class="chapter">` | `<span class="title">heading</span>` |
| Quote style | Double quotes in classes | Single quotes everywhere |
| File structure | `info.html` + `content.html` | Single `.htm` per volume with embedded metadata |
| Title extraction | From `<h1>` in info.html | From first `<span class='title'>` in card header |
| Author extraction | From `المؤلف` table row | From `<span class='footnote'>(AuthorShort)</span>` AND `المؤلف` field |

**Every single extraction rule in the SPEC was based on wrong assumptions.** The survey prevented building an engine that would fail on 100% of real sources.

---

## 6. Implications for the Source Engine SPEC

### §4.A.2 Format Detection
Detection criteria must change:
- Single `.htm` file → check for `<div class='PageText'>` and `<span class='title'>` pattern
- Directory of numbered `.htm` files → check first file for same markers
- No `info.html` to look for

### §4.A.3 Extraction Rules
Complete rewrite needed. The extractor must:
1. Parse the first `PageText` div as the metadata card
2. Extract display title from `<span class='title'>TITLE&nbsp;</span>` header
3. Extract short author from `<span class='footnote'>(AUTHOR)</span>` header
4. Parse category from `القسم` field after `<hr>`
5. Parse bibliographic fields using `<span class='title'>LABEL:</span> VALUE` pattern
6. Handle ALL muhaqiq-equivalent fields (6 variants)
7. Handle `اسم الكتاب` as alternative to `الكتاب` for the title field
8. Parse death dates from author field: `(ت NNN هـ)` pattern
9. Extract page count from `عدد الصفحات` field
10. Count `PageText` divs minus 1 as body page count

### §4.A.4 Multi-Layer Detection
**Cannot use CSS classes.** Must rely entirely on:
- Genre inference (sharh → always multi-layer)
- Title analysis (titles containing "شرح" + "على" imply matn+sharh)
- Content analysis (quoted verses in a prose commentary)
- This is now a harder problem than the SPEC assumed

### §4.A.7 Deduplication
SHA-256 hashing must account for the metadata card being present in every volume file of multi-volume books. Two different volumes of the same book will have different hashes — this is correct behavior (they ARE different files). But the work_id must be the same.

---

## 7. Test Fixture Selection Criteria

Based on this survey, the permanent test fixtures should cover:

1. **Single-file book, simple** — one author, one science, no muhaqiq
2. **Single-file book, with muhaqiq** — has المحقق field, known publisher
3. **Multi-volume book, small** — 2-5 volumes, numbered files
4. **Multi-volume book with المقدمة** — has المقدمة.htm file
5. **Book with death date in author field** — `(ت NNN هـ)` pattern
6. **Book with alternative muhaqiq field** — `تحقيق` or `دراسة وتحقيق`
7. **Book with alternative title field** — `اسم الكتاب` instead of `الكتاب`
8. **Book WITHOUT المؤلف field** — uses `إعداد` or is a thesis
9. **Nahw book (grammar)** — for science scope testing
10. **Fiqh book** — for science scope testing
11. **Hadith collection** — for special trust handling
12. **Tafsir book** — for science scope testing

---

## Appendix: Raw Survey Statistics

```
Total books: 2,519
Single-file: 1,932 (76.7%)
Multi-volume: 587 (23.3%)

File sizes (per first-file):
  Min: 5,069 bytes
  Max: 20,583,592 bytes (20 MB)
  Median: 210,794 bytes (206 KB)
  Mean: 599,284 bytes (585 KB)

Encoding: 100% UTF-8, zero encoding issues
Parse errors: zero across all 2,519 files

Page structure:
  PageText div: 100%
  PageHead div: 100%
  PartName span: 100%
  PageNumber span: 98.2%

Metadata card:
  span.title format: 100% (no tables, no other format)

Color markup: 100% of books use #be0000
Section headings in body: 82.7%
ZWNJ before heading spans: 92.9%
Footnotes (div.footnote): 47.5%
```
