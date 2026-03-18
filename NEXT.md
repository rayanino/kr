# NEXT — Build Session 2: Shamela Normalizer Passes 1–3

## Current position: Session 1 COMPLETE (commit e2d6043). Contracts aligned (MF-1, MF-2), 31 error codes, 40 tests. Architect ACCEPTED. SPEC §9.1 staleness fixed (M-13, M-14 marked RESOLVED).
## What to do: Implement Passes 1–3 of the Shamela HTML normalizer — the core text extraction pipeline that every later pass builds on.
## Context: This is the most complex build session. Passes 1–3 transform raw Shamela HTML into clean, separated text with preserved diacritics. The ABD reference code (1,123 lines) handles this in ~600 lines. CC rebuilds fresh code matching SPEC.md, using ABD code for Shamela HTML quirk awareness. Output is INTERMEDIATE internal data structures — NOT the final ContentUnit (that is Pass 6, Session 5).
## Owner action needed: NO (Claude Code executes autonomously, owner relays to CC).

---

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (105L) — Engine orientation, module map, build session plan, critical rules. Read ALL of it.

2. `engines/normalization/SPEC.md` lines 183–199 — §4.A.2 Passes 1–3 specification. These 17 lines are the behavioral authority for everything you build. Read them VERY carefully — every clause matters.

3. `engines/normalization/SPEC.md` lines 209–217 — §4.A.5 layer detection signals. You do NOT implement layer detection, but Pass 1 MUST record bold spans (`<b>` tag positions + character offsets) and font-size spans (`<font size>`) from the raw HTML BEFORE stripping. Pass 5 (Session 4) consumes these. Line 212 explicitly says "The normalizer records bold spans and their character offsets during Pass 1."

4. `engines/normalization/SPEC.md` lines 200–207 — §4.A.6 Pass 4 structure discovery, specifically Tier 1: "Extract `<span class=\"title\">` elements from the frozen HTML (not from cleaned text — tags are needed)." Pass 1 MUST extract `<span class="title">` elements (with double quotes — the content headings) from HTML before stripping, so Pass 4 (Session 3) can consume them. See also `engines/normalization/reference/structural_patterns.yaml` lines 12–26 for the critical quote-style differentiator: single-quote `class='title'` = metadata page labels, double-quote `class="title"` = content headings.

5. `engines/normalization/SPEC.md` lines 655–658 — §4.A.8 whitespace/encoding rules. Authoritative whitespace normalization rules. Pay close attention to which Unicode characters are PRESERVED (ZWNJ U+200C, ZWSP U+200B, ZWJ U+200D) vs normalized (NBSP → space, typographic spaces → space).

6. `engines/normalization/SPEC.md` lines 115–121 — §3 output format overview. Key: "Footnote reference markers in the primary text are replaced with inline markers in a universal format (`⌜1⌝` — using Unicode half-brackets U+231C and U+231D)." This replacement happens during Pass 2/3 text cleaning.

7. `engines/normalization/SPEC.md` lines 1559–1597 — §7 error code table. Session 2 uses these codes: `NORM_FOOTNOTE_SEPARATOR_ABSENT`, `NORM_DIACRITICS_ENTITY_CORRUPTION`, `NORM_DIACRITICS_DRIFT`, `NORM_ORPHAN_FOOTNOTE_REF`, `NORM_ENCODING_ERROR`, `NORM_DUPLICATE_PAGES`, `NORM_UNIT_INDEX_VIOLATION`, `NORM_PAGE_COUNT_MISMATCH`, `NORM_VOLUME_NUMBER_UNPARSEABLE`, `NORM_VOLUME_MISMATCH`, `NORM_SUSPICIOUS_PAGEHEAD`.

8. `engines/normalization/reference/SHAMELA_HTML_REFERENCE.md` (803L) — **Critical reference.** Complete Shamela format documentation: page blocks (§2), running header (§3), HR tag distinctions (§4), matn structure (§5), footnotes (§6), multi-volume (§9), step-by-step algorithm (§10). Read §1–§7 and §9–§10 thoroughly. §8 (edge cases) is also valuable.

9. `reference/archive/abd_code/normalization/normalize_shamela.py` (1,123L) — ABD reference implementation. Read the data classes (lines 114–166), regex patterns (lines 47–95), and the `normalize_page()` function (lines 465–583). The parsing approach is battle-tested against 1,046 books. Key patterns to learn from: footnote boundary regex with monotonic merge (lines 362–406), footnote ref stripping with `known_fn_numbers` guard (lines 217–267), verse detection with hemistich balance check (lines 275–302), image-only page detection (lines 450–462). REBUILD fresh code — do not copy-paste — but learn from these patterns.

10. `engines/normalization/contracts.py` (725L) — The output schema. Session 2 does NOT produce `ContentUnit` or `NormalizedPackage` directly (that's Pass 6). But understand the final shape: `Footnote` model (lines 167–186), `ContentFlags` (lines 215–223), `FootnoteType` enum (lines 60–81), `PhysicalPage` (lines 100–106). Your intermediate data must contain everything needed to populate these later.

11. `engines/normalization/src/errors.py` (131L) — Error codes and `NormalizationError` exception class. Use these codes directly — do not invent new ones.

12. `engines/normalization/src/normalizers/shamela.py` (80L) — Current stub. This is where you fill in Passes 1–3.

13. `engines/normalization/src/normalizers/base.py` (57L) — Abstract interface your normalizer implements.

14. `reference/SPEC_ADVERSARY_NORMALIZATION.md` lines 17–212 — ADV-001 through ADV-010 target Passes 1–3. These are MANDATORY test inputs. Each adversarial case describes a specific input, correct behavior, wrong behavior, and detection assertion. Implement tests for ALL 10.

15. Test fixtures:
    - `tests/fixtures/shamela_real/` — 13 real Shamela books (each in its own subdirectory with `book.htm` or numbered volume files like `001.htm`, `002.htm`). Fixture 11 (`11_multi_small`) has 3 volumes; fixture 12 (`12_multi_muq`) has 2 volumes; fixture 13 (`13_format_b`) tests superscripted footnote refs.
    - `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` — Hand-crafted multi-layer commentary fixture with metadata page, bold matn, footnotes, verse, diacritics.

---

## What to Build

### A. Intermediate data structures (internal to shamela.py)

Define these as dataclasses or Pydantic models INSIDE `engines/normalization/src/normalizers/shamela.py`. They are internal to the Shamela normalizer — not part of the public `contracts.py`.

**`RawPage`** — Output of Pass 1 (one per page block):
- `unit_index: int` — Monotonically increasing from 0, across all volumes.
- `volume: int` — Volume number (1 for single-volume books).
- `page_number_display: Optional[str]` — Arabic-Indic numeral string (e.g., "٤٥"). None for pages without page numbers.
- `page_number_int: Optional[int]` — Western integer. None for pages without page numbers.
- `raw_html: str` — The full PageText div content (minus the outer `<div class='PageText'>` wrapper).
- `is_metadata_page: bool` — True if this is a metadata/title page (no page number, per SHAMELA_HTML_REFERENCE §2.3).
- `is_image_only: bool` — True if page is an embedded scan with <10 chars of text content.
- `bold_spans: list[tuple[int, int, str]]` — `(start_char, end_char, text)` of `<b>...</b>` regions in the matn HTML, measured BEFORE tag stripping. For Pass 5 (layer detection). Record these from the matn HTML (after header removal, before footnote separator).
- `font_size_spans: list[tuple[int, int, str, str]]` — `(start_char, end_char, text, size_value)` of `<font size=N>` regions. For Pass 5.
- `title_spans: list[str]` — Text content of `<span class="title">` elements (double-quote variant ONLY). For Pass 4 (structure discovery). Exclude single-quote `class='title'` which are metadata labels.
- `pagehead_text: Optional[str]` — Text extracted from `<div class='PageHead'>` for structural marker recording. Includes the heading text from `<span class='PartName'>` or `<span class='title'>` inside PageHead.
- `warnings: list[str]` — Any warnings generated during parsing.

**`SeparatedPage`** — Output of Pass 2 (one per non-metadata, non-image page):
- `unit_index: int` — Carried from RawPage.
- `volume: int`
- `page_number_display: Optional[str]`
- `page_number_int: Optional[int]`
- `primary_html: str` — HTML content above the footnote separator (matn layer).
- `footnote_html: str` — HTML content below the footnote separator (may be empty).
- `footnotes: list[ParsedFootnote]` — Parsed footnote entries.
- `footnote_format: str` — One of: "numbered_parens", "bare_number", "unnumbered", "none".
- `footnote_preamble: str` — Text before first `(N)` marker in footnote section.
- `known_fn_numbers: set[int]` — Set of footnote numbers found, for reference stripping guard.
- `has_footnote_separator: bool` — Whether `<hr width=80-100>` was found on this page.
- `bold_spans: list[tuple[int, int, str]]` — Carried from RawPage.
- `font_size_spans: list[tuple[int, int, str, str]]` — Carried from RawPage.
- `title_spans: list[str]` — Carried from RawPage.
- `pagehead_text: Optional[str]` — Carried from RawPage.
- `warnings: list[str]`

**`ParsedFootnote`** — One footnote entry:
- `number: int` — The `(N)` number.
- `text: str` — Cleaned footnote text.
- `raw_text: str` — Original text before cleaning.
- `footnote_type: str` — Coarse classification: "tahqiq_editor", "author_original", "unknown_footnote_type".
- `classification_confidence: float` — 0.0–1.0.

**`CleanedPage`** — Output of Pass 3 (one per non-metadata, non-image page):
- `unit_index: int`
- `volume: int`
- `page_number_display: Optional[str]`
- `page_number_int: Optional[int]`
- `primary_text: str` — Cleaned text. All HTML removed. Diacritics preserved. Footnote refs replaced with `⌜N⌝` (only for matching footnotes). Whitespace normalized per §4.A.8.
- `footnotes: list[ParsedFootnote]` — From Pass 2.
- `footnote_format: str` — From Pass 2.
- `footnote_preamble: str` — From Pass 2.
- `footnote_ref_numbers: list[int]` — Unique sorted list of footnote ref numbers found and replaced in primary text.
- `orphan_refs: list[int]` — Refs in text with no matching footnote (kept as literal "(N)").
- `orphan_footnotes: list[int]` — Footnotes with no matching ref in text.
- `has_verse: bool` — Verse/poetry detected (hemistich separator or star markers).
- `has_tables: bool` — HTML tables found and converted to text.
- `is_blank: bool` — No extractable text content after cleaning.
- `starts_with_zwnj_heading: bool` — Text starts with double ZWNJ (U+200C U+200C).
- `bold_spans: list[tuple[int, int, str]]` — Carried through for Pass 5.
- `font_size_spans: list[tuple[int, int, str, str]]` — Carried through for Pass 5.
- `title_spans: list[str]` — Carried through for Pass 4.
- `pagehead_text: Optional[str]` — Carried through for Pass 4.
- `warnings: list[str]` — Accumulated from all passes.

### B. Pass 1 — HTML Parsing and Page Extraction

Implement as a method `_pass1_parse(self, html_text: str, volume: int, seq_offset: int) -> list[RawPage]` on `ShamelaNormalizer`.

**Behavioral rules (SPEC §4.A.2 Pass 1 + SHAMELA_HTML_REFERENCE §10):**

1. Split HTML at `<div class='PageText'>` start positions (string find, NOT regex on the full div — nested `<div class='footnote'>` breaks regex matching). See SHAMELA_HTML_REFERENCE §2.1.

2. For each page block, search for page number `(ص: N)` with Arabic-Indic digits. Regex: `\(ص:\s*([٠-٩]+)\s*\)`. Convert Arabic-Indic → integer using the mapping in SHAMELA_HTML_REFERENCE §3.3.

3. Pages with no page number → metadata pages. Set `is_metadata_page = True`. Do NOT create a content unit for these — skip them. Record in warnings.

4. ADV-008/ADV-009 exception: pages WITH a page number but no extractable text → blank pages. These DO produce content units. Set `is_blank` downstream.

5. Detect image-only pages: remove PageHead, remove `<img>` tags, strip HTML tags — if <10 chars remain, it's image-only. Set `is_image_only = True`.

6. Extract bold spans from matn HTML (after PageHead removal, before footnote separator): find all `<b>...</b>` regions and record their text and positions. These positions are relative to the matn HTML string (pre-stripping) — Pass 5 will need to map these to cleaned text positions. Record even if `is_multi_layer` is false in source metadata — the normalizer detects layer signals independently.

7. Extract `<font size=N>` spans similarly.

8. Extract `<span class="title">` elements (DOUBLE-QUOTE `class="title"` ONLY, NOT single-quote `class='title'`). This is the quote-style differentiator from `structural_patterns.yaml` line 12.

9. Extract PageHead text content for structural markers.

10. Assign `unit_index` = `seq_offset + counter` monotonically. Skip metadata pages (they don't get unit_index values). Image-only and blank pages DO get unit_index values.

11. For multi-volume: caller processes each `.htm` file in filename-stem numeric order (`001.htm` → vol 1, `002.htm` → vol 2, ...), passing `seq_offset` = cumulative page count from prior volumes.

12. Volume number derivation: integer value of filename stem. Non-numeric stems → `NORM_VOLUME_NUMBER_UNPARSEABLE` warning, assign sequentially. Duplicate volume numbers → `NORM_VOLUME_MISMATCH` warning.

### C. Pass 2 — Content/Footnote Separation

Implement as `_pass2_separate(self, pages: list[RawPage]) -> list[SeparatedPage]` on `ShamelaNormalizer`.

**Behavioral rules (SPEC §4.A.2 Pass 2):**

1. Skip metadata pages and image-only pages from Pass 1.

2. For each remaining page, search for footnote separator. SPEC regex: `<hr\s+[^>]*width\s*=\s*['"]?(\d{2,3})['"]?[^>]*>` where captured group is 80–100 (inclusive). The ABD code uses the simpler `<hr\s+width='95'[^>]*>` — you MUST use the SPEC regex which is more general and handles: no quotes, double quotes, extra attributes, self-closing, percentage values. See ADV-001 through ADV-004 for edge cases.

3. If separator found: everything before it = primary HTML, everything after = footnote HTML. If not found: entire content = primary HTML, footnote HTML = "". Log `NORM_FOOTNOTE_SEPARATOR_ABSENT` for pages without separator. If >30% of pages lack it, set `no_footnote_apparatus` flag.

4. Parse footnotes from footnote HTML:
   - Extract `<div class='footnote'>` content.
   - Unwrap `<font color=#be0000>` tags (keep text, remove tag).
   - Strip all remaining HTML tags, decode entities.
   - Classify format: `numbered_parens` (has `(N)` markers), `bare_number`, `unnumbered`, `none`.
   - Split at `(N)` boundaries. Each `(N)` at text start or after newline marks a new footnote. Strip optional dash separator after `(N)`.
   - **Monotonic merge:** If a `(N)` would break monotonic sequence (e.g., `(1)` appearing after `(2)`), merge it into the previous footnote as a sub-reference. See ABD code lines 388–404.
   - Record preamble text (content before first `(N)` marker).

5. **Coarse footnote type classification (SPEC §4.A.2 Pass 2):**
   - `tahqiq_editor`: Contains tahqiq markers — hadith grading terms (صحيح, حسن, ضعيف, أخرجه), manuscript variant notation ("في نسخة:", "في الأصل:"), bibliographic references to collections (البخاري, مسلم, أبو داود, الترمذي, الحاكم, البيهقي, ابن حبان).
   - `author_original`: No tahqiq markers AND contains strong positive evidence of author's own voice (e.g., starts with "قلت:" or "أقول:", self-referential notes). Set `classification_confidence` = 0.7.
   - `unknown_footnote_type`: Cannot determine — no tahqiq markers AND no strong author-voice evidence. This is the SAFE DEFAULT for uncertain cases. Set `classification_confidence` = 0.5.
   - This is COARSE classification. The fine-grained sub-types (variant_reading, hadith_takhrij, etc.) are §4.B.4 — DEFERRED to Session 5 or later. When in doubt, classify as `unknown_footnote_type` — false certainty is worse than acknowledged uncertainty.

6. Collect `known_fn_numbers` = set of all footnote entry numbers. This is critical for Pass 3's safe reference stripping.

### D. Pass 3 — HTML Stripping and Text Cleaning

Implement as `_pass3_clean(self, pages: list[SeparatedPage]) -> list[CleanedPage]` on `ShamelaNormalizer`.

**Behavioral rules (SPEC §4.A.2 Pass 3 + §4.A.8):**

1. **HTML parsing approach.** The SPEC mandates BeautifulSoup with `lxml` backend for HTML entity resolution safety. However, for Shamela's machine-generated HTML, the ABD regex-based approach is proven reliable across 1,046 books. Use this pragmatic approach:
   - Use BeautifulSoup + `lxml` for HTML entity decoding (the primary concern for diacritics safety).
   - If `lxml` parsing fails, fall back to `html5lib`.
   - For tag stripping and text extraction, the ABD regex approach is acceptable — it's simpler and battle-tested. The critical requirement is that entity decoding does not corrupt diacritics.

2. **Processing order for primary HTML** (adapted from SHAMELA_HTML_REFERENCE §10, steps 5–8):
   a. Remove running header: `<div class='PageHead'>...</div>` (regex with DOTALL).
   b. Replace `<table>...</table>` blocks with extracted cell text (row by row, cells joined with ` | `). Set `has_tables = True` if any found.
   c. Remove `<img>` tags.
   d. Detect verse BEFORE stripping: check for hemistich separator `…` (U+2026) with balanced text (≥5 chars on each side, excluding prose "إلخ" patterns) or star markers `* text *`. Set `has_verse`.
   e. Unwrap `<font color=#be0000>` tags (keep text).
   f. Convert block-level breaks: `</p>` → `\n`, `<br>` / `<br/>` → `\n`.
   g. Strip all remaining HTML tags.
   h. Decode HTML entities via BeautifulSoup or `html.unescape()`.
   i. Clean verse markers: strip asterisks from `* text *`.
   j. **Replace footnote references with universal markers:** For each `(N)` in the text where N is in `known_fn_numbers`, replace with `⌜N⌝` (U+231C + number + U+231D). Refs where N is NOT in `known_fn_numbers` are kept as literal `(N)` — they are exercise numbers, verse references, or commentary-layer notes, NOT footnote refs. Log `NORM_ORPHAN_FOOTNOTE_REF` for refs that match the pattern but have no matching footnote. See ADV-005.
   k. **Whitespace normalization (§4.A.8):** `\r\n`/`\r` → `\n`. U+00A0 → space. U+202F → space. U+2000–U+200A → space. U+FEFF → strip at file start only. **PRESERVE:** U+200C (ZWNJ), U+200B (ZWSP), U+200D (ZWJ). Collapse 2+ spaces → 1. Collapse 3+ blank lines → 1. Trim lines. Trim result.

3. **Diacritics preservation verification (SPEC §4.A.2 Pass 3):** After HTML parsing/entity decoding, compare diacritic character positions between the raw HTML text nodes and the parsed output. This is a POSITIONAL check, not just presence-based — a diacritic that exists in the output but at the wrong position (shifted by entity resolution) is a corruption. Arabic diacritical marks to check: U+064B–U+0652 (fathatan through sukun), U+0670 (superscript alef), U+0656–U+065F (additional marks). Implementation: extract Arabic text from raw HTML (strip tags only, keep entities unresolved), then extract Arabic text from BS4-parsed output. Compare diacritic character indices. If any diacritic at a known position is absent or substituted → raise `NORM_DIACRITICS_ENTITY_CORRUPTION` (Fatal). See ADV-006. NOTE: This check is computationally inexpensive — only compare the first 500 characters of the first content page per source as a canary. If that passes, the parser is safe for the entire source (since it uses the same code path for all pages).

4. **Blank page detection:** After cleaning, if `primary_text` is empty or all whitespace → `is_blank = True`.

5. **ZWNJ heading detection:** If cleaned text starts with `\u200c\u200c` (double ZWNJ) → `starts_with_zwnj_heading = True`. See ADV-007.

6. **Cross-reference validation:** Compare `footnote_ref_numbers` (from step 2j) against `known_fn_numbers`. Record orphan refs and orphan footnotes as warnings.

### E. Top-level orchestration

The public `normalize()` method on `ShamelaNormalizer` (currently raising `NotImplementedError`) should be partially implemented:

```python
def normalize(self, frozen_path: Path, metadata: SourceMetadata) -> NormalizedPackage:
    # Resolve input files
    htm_files = self._resolve_input_files(frozen_path)

    # Pass 1: Parse all volumes
    all_raw_pages: list[RawPage] = []
    seq_offset = 0
    for volume_num, htm_file in htm_files:
        html_text = self._read_html(htm_file)
        raw_pages = self._pass1_parse(html_text, volume_num, seq_offset)
        content_pages = [p for p in raw_pages if not p.is_metadata_page]
        seq_offset += len(content_pages)
        all_raw_pages.extend(raw_pages)

    # Pass 2: Separate content from footnotes
    separated = self._pass2_separate(all_raw_pages)

    # Pass 3: Clean HTML and produce text
    cleaned = self._pass3_clean(separated)

    # Passes 4–6: NOT YET IMPLEMENTED (Sessions 3–5)
    raise NotImplementedError(
        "Passes 4–6 not yet implemented. "
        f"Pass 1–3 produced {len(cleaned)} cleaned pages from {len(htm_files)} file(s)."
    )
```

Also implement `validate_input()` — verify frozen_path exists, contains `.htm`/`.html` files, files are valid UTF-8, at least one `PageText` div exists. Raise `NORM_MISSING_FROZEN` or `NORM_SCHEMA_VIOLATION` on failure.

Also implement `_resolve_input_files()` — handle both single-file and multi-volume directory inputs. Return list of `(volume_number, path)` tuples sorted by volume number. The `frozen_path` can be:
- A **directory with numbered files** (e.g., `001.htm`, `002.htm`) → multi-volume book. Volume number = int(filename stem).
- A **directory with a single `book.htm`** → single-volume book. Volume = 1. (This is the test fixture pattern.)
- A **directory with a single `.htm` file of any name** → single-volume book. Volume = 1.
- A **single `.htm` file path** → single-volume book. Volume = 1.
Detection logic: if `frozen_path.is_dir()`, list `.htm`/`.html` files. If all filenames are numeric stems (e.g., `001.htm`), treat as multi-volume. Otherwise, treat as single-volume. If `frozen_path.is_file()`, treat as single-volume.

Also implement `_read_html()` — UTF-8 with Windows-1256 fallback. Log `NORM_ENCODING_ERROR` on fallback.

### F. Tests

Write tests in `engines/normalization/tests/test_shamela_passes.py`.

**Mandatory test categories:**

1. **ADV-001 through ADV-010** (10 adversarial tests): Construct the exact HTML inputs from `reference/SPEC_ADVERSARY_NORMALIZATION.md` and verify the exact assertions described. These test: footnote separator boundary values (001, 002), percentage width (003), extra attributes (004), orphan footnote ref preservation (005), diacritics entity preservation (006), ZWNJ preservation (007), missing page number (008), empty page (009), PageHead content exclusion (010).

2. **Real fixture parsing** (13 tests, one per `tests/fixtures/shamela_real/` fixture): Parse each fixture through Passes 1–3. Verify:
   - Correct page count (metadata pages skipped).
   - First content page has expected page number.
   - Footnotes correctly separated where present.
   - No crashes.

3. **Multi-volume handling** (2 tests): Parse fixtures 11 (3 volumes) and 12 (2 volumes). Verify:
   - `unit_index` is contiguous across all volumes.
   - Volume numbers correctly derived from filenames.
   - Total page count = sum of per-volume counts.

4. **Ibn Aqil fixture** (detailed test): Parse `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` through Passes 1–3. Verify:
   - Metadata page (page 1) skipped.
   - Page 2: bold spans recorded, footnote (1) extracted, `⌜1⌝` in primary_text, "(1)" NOT in primary_text, heading "باب الكلام وما يتألف منه" in title_spans.
   - Page 3: two footnotes parsed, both cross-referenced.
   - Diacritics preserved exactly (check specific diacritical marks like kasra, fatha, damma, shadda in كَلَامُنَا لَفْظٌ مُفِيدٌ).

5. **Footnote type classification** (3+ tests): Verify coarse classification:
   - Footnote containing "أخرجه البخاري" → `tahqiq_editor`.
   - Footnote containing "في نسخة" → `tahqiq_editor`.
   - Footnote with no tahqiq markers → `author_original` or `unknown_footnote_type`.

6. **Whitespace normalization** (test): Construct HTML with NBSP, typographic spaces, ZWNJ, ZWSP, multiple blank lines. Verify NBSP → space, typographic → space, ZWNJ preserved, blank line collapse.

7. **Verse detection** (2 tests): Verify hemistich separator detection (balanced text ≥5 chars each side) and star marker detection. Verify prose "إلخ" pattern does NOT trigger verse detection.

8. **Table extraction** (test): Construct page with `<table>` block. Verify table converted to `cell | cell` text format and `has_tables = True`.

9. **Error code usage** (3+ tests): Verify correct error codes raised: `NORM_FOOTNOTE_SEPARATOR_ABSENT` when no separator, `NORM_ORPHAN_FOOTNOTE_REF` for orphan refs, `NORM_ENCODING_ERROR` on non-UTF-8 input.

---

## Do NOT Do

- **Do NOT implement Passes 4–6.** Structure discovery (Pass 4) is Session 3. Layer detection (Pass 5) is Session 4. Output assembly (Pass 6) is Session 5. Leave the `NotImplementedError` in `normalize()` after Pass 3.

- **Do NOT implement the plain text normalizer.** That is `normalizers/plain_text.py`, Session 6.

- **Do NOT modify `contracts.py`.** The intermediate data structures are INTERNAL to `shamela.py`. If you find a genuine gap in contracts.py, document it in a comment — do not modify the file.

- **Do NOT modify `errors.py`.** All needed error codes already exist (31 codes from Session 1).

- **Do NOT implement fine-grained footnote classification** (§4.B.4). Only implement COARSE classification: `tahqiq_editor` / `author_original` / `unknown_footnote_type`. Fine-grained sub-types (variant_reading, hadith_takhrij, etc.) are deferred.

- **Do NOT implement the dispatcher** (`src/dispatcher.py`). That is Session 6 or 7.

- **Do NOT install new dependencies** beyond what is available (BeautifulSoup4, lxml, html5lib should already be available or installable via pip). If lxml is not installed, install it: `pip install lxml beautifulsoup4 html5lib --break-system-packages`.

- **Do NOT copy-paste from ABD code.** Read the ABD patterns, understand the Shamela quirks they handle, then write fresh code matching the SPEC. The SPEC has upgrades the ABD code lacks (e.g., universal `⌜N⌝` footnote markers, BS4 entity parsing, diacritics verification, SPEC-compliant footnote separator regex).

---

## Verification

Run these commands before committing. ALL must pass.

```bash
# 1. All tests pass
cd /path/to/kr
python -m pytest engines/normalization/tests/ -v --tb=short

# 2. Existing Session 1 tests still pass (no regression)
python -m pytest engines/normalization/tests/test_contracts.py -v --tb=short

# 3. Type check (informational — not blocking but should have no major issues)
python -m mypy engines/normalization/src/normalizers/shamela.py --ignore-missing-imports 2>&1 | head -20

# 4. Quick smoke test — parse the ibn_aqil fixture
python -c "
from pathlib import Path
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
n = ShamelaNormalizer()
# Pass 1
html = Path('engines/normalization/tests/fixtures/shamela_ibn_aqil.htm').read_text()
raw = n._pass1_parse(html, volume=1, seq_offset=0)
print(f'Pass 1: {len(raw)} pages ({sum(1 for p in raw if p.is_metadata_page)} metadata, {sum(1 for p in raw if not p.is_metadata_page)} content)')
# Pass 2
sep = n._pass2_separate(raw)
print(f'Pass 2: {len(sep)} separated pages, {sum(len(p.footnotes) for p in sep)} total footnotes')
# Pass 3
clean = n._pass3_clean(sep)
print(f'Pass 3: {len(clean)} cleaned pages')
for p in clean[:2]:
    print(f'  Page {p.page_number_int}: {len(p.primary_text)} chars, {len(p.footnotes)} footnotes, verse={p.has_verse}')
    if p.primary_text:
        print(f'    First 100 chars: {p.primary_text[:100]}')
"

# 5. Parse a real fixture (multi-volume)
python -c "
from pathlib import Path
from engines.normalization.src.normalizers.shamela import ShamelaNormalizer
n = ShamelaNormalizer()
# Multi-volume fixture (3 files)
fixture_dir = Path('tests/fixtures/shamela_real/11_multi_small')
files = sorted(fixture_dir.glob('*.htm'))
all_clean = []
offset = 0
for f in files:
    vol = int(f.stem)
    raw = n._pass1_parse(f.read_text(), volume=vol, seq_offset=offset)
    content = [p for p in raw if not p.is_metadata_page]
    offset += len(content)
    sep = n._pass2_separate(raw)
    clean = n._pass3_clean(sep)
    all_clean.extend(clean)
    print(f'Vol {vol}: {len(content)} content pages')
print(f'Total: {len(all_clean)} pages, unit_index range: {all_clean[0].unit_index}–{all_clean[-1].unit_index}')
assert all_clean[-1].unit_index == len(all_clean) - 1, 'unit_index not contiguous!'
print('unit_index contiguity: OK')
"
```

**Expected outcome:** 60+ tests passing. Zero regressions on Session 1 tests. Both smoke tests produce reasonable output. All 10 adversarial test cases pass.

---

## After This

Owner relays results to Architect (Claude Chat). Architect uses `kr-reviewing-cc-output` to review the commit: cross-references against SPEC §4.A.2, §4.A.8, §7, SHAMELA_HTML_REFERENCE, and all 10 adversarial cases. If ACCEPT → write Session 3 handoff (structure discovery). If BLOCKED → fix directive back to CC.
