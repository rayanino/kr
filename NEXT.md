# NEXT — Large-Work Division Size Analysis

## Context

Architecture decision in progress. The Architect needs empirical data on division sizes in large multi-volume Islamic scholarly works to finalize the architecture for remaining engines. The hypothesis: most divisions in the Shamela collection are ≤ 2000 Arabic words, making a separate passaging engine unnecessary. But this has only been tested on 5 small books (228 divisions). We need to verify on the full 20K+ collection, especially the largest reference works.

**This is a data-gathering task, not a build task.** No engine code, no SPEC changes. Just analysis and output.

## What To Do

Write and run `experiments/architecture_test/analyze_shamela_divisions.py` that:

### Step 1: Scan all .htm files in `shamela-export-samples/`

For each `.htm` file:
1. Count pages: `<div class='PageText'>` or `<div class="PageText">` occurrences
2. Find headings: `<span class='title'>` or `<span class="title">` content, filtering OUT:
   - Metadata fields: spans containing الكتاب, المؤلف, الناشر, الطبعة, عدد الصفحات, القسم, تاريخ النشر بالشاملة
   - Book title: spans containing `&nbsp;` (the first title span is usually the book title with trailing spaces)
   - Very short spans (< 3 chars after cleaning)
3. Clean heading text: strip HTML tags, replace `&#8204;` and `\u200c` (ZWNJ) with empty string, strip whitespace
4. Extract text between headings (primary_text from PageText divs, stripped of HTML tags)
5. Count Arabic words per division: split on whitespace, count tokens with at least one char in `\u0600-\u06FF`

### Step 2: Compute per-book statistics

For each book with ≥ 5 headings (books with fewer headings aren't structurally divided):
- Book identifier: filename or first heading text
- Total pages (PageText count)
- Total headings found
- Total Arabic words
- Division sizes: min, max, median, mean
- Count of divisions in each bucket: <50w, 50-299w, 300-800w, 801-2000w, 2001-5000w, >5000w
- File size in bytes

### Step 3: Compute collection-wide statistics

- Total books scanned
- Total books with ≥ 5 headings
- Total divisions across all books
- Collection-wide division size distribution (same buckets)
- % of divisions that need no splitting at 2000w ceiling
- % of divisions that need no splitting at 5000w ceiling
- List ALL divisions > 5000w with book name and heading text

### Step 4: Focus analysis on the 20 largest books

Sort by file size descending. For the top 20:
- Full per-book statistics (Step 2)
- Count of divisions > 2000w and > 5000w
- Largest single division (word count + heading text)

### Step 5: Output

Write results to `experiments/architecture_test/SHAMELA_DIVISION_ANALYSIS.md`:

```markdown
# Shamela Division Size Analysis — [date]

## Collection Summary
[Total books, total divisions, distribution table]

## Division Size Distribution (all books with ≥5 headings)
[Bucket counts and percentages]
[% needing no splitting at 2000w / 5000w ceilings]

## Top 20 Largest Books
[Per-book table with key metrics]

## Oversized Divisions (>5000w)
[List with book name, heading, word count]

## Format Observations
[Any notable patterns: verse books, Q&A books, etc.]
```

Also write the raw data as `experiments/architecture_test/shamela_division_data.json` — a JSON array with one entry per book containing all computed metrics.

## Technical Notes

### Shamela HTML Structure
- Pages: `<div class='PageText'>` or `<div class="PageText">`
- Headings: `<span class='title'>` or `<span class="title">` (content may start with ZWNJ `&#8204;` / `\u200c`)
- Page headers: `<div class='PageHead'>` — ignore these, they're running headers not content
- Footnotes: `<div class='footnote'>` — exclude from word counts
- The first PageText div is usually metadata (book title, author, publisher) — skip it

### Path
- `shamela-export-samples/` in the repo root (gitignored, local only)
- Files may be directly in the folder or in subdirectories
- Find all `.htm` files recursively

### Encoding
- Most Shamela files are UTF-8, but some older exports may be Windows-1256
- Try UTF-8 first, fall back to `cp1256`, fall back to `utf-8` with `errors='replace'`
- Log which encoding was used if not UTF-8

### Performance
- 20K+ files, some very large (multi-MB)
- Use streaming HTML parsing, not loading entire files into memory for regex
- Show progress every 500 files
- If a file fails to parse, log and skip — don't crash

## Do NOT Do

1. Do NOT modify any engine code
2. Do NOT run the normalization pipeline
3. Do NOT make any LLM calls
4. Do NOT commit the raw shamela-export-samples data
5. Do NOT spend time on edge cases in HTML parsing — approximate word counts are fine. We need distribution data, not exact numbers.

## Verification

Run the script. Check the output makes sense:
- Total books should be ~20,000+
- Largest books should be recognizable Islamic reference works
- Division sizes should mostly be in the hundreds-to-low-thousands range
- The SHAMELA_DIVISION_ANALYSIS.md should be readable and complete

Commit the script AND the output files. Push.

## Read First

1. This file (NEXT.md)
2. `experiments/architecture_test/extract_divisions.py` — reference for how division extraction works on normalized packages (different input format, but same concepts)
3. `tests/fixtures/shamela_extended/ext_01/book.htm` — example of Shamela HTML format
