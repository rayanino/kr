# Normalization Engine — محرك التطبيع — Specification

## 1. Purpose and Scope

The normalization engine is the final Phase 1 engine and the guardian of the normalization boundary. It receives frozen source files and source metadata from the source engine, transforms them from their native format into the universal normalized format, and produces a normalized package that crosses the normalization boundary into Phase 2. Every downstream engine — passaging, atomization, excerpting, taxonomy, and synthesizing — sees only normalized packages, never raw sources. The quality of every knowledge product in the library depends on how faithfully this engine preserves content, structure, and scholarly apparatus during transformation.

**What this engine does:**
- Transforms source content from format-specific markup into a universal, source-agnostic representation
- Discovers the source's internal structure (headings, chapters, divisions) from format-specific signals before those signals are stripped
- Identifies text layers in multi-layer compositions (matn/sharh/hashiyah/tahqiq) using format-specific typography and layout cues
- Separates primary text from editorial apparatus (footnotes, variant readings, tahqiq notes)
- Preserves page boundaries as metadata for downstream citation generation
- Detects and tags verse structure in versified texts (منظومات)
- Produces a text fidelity signal at page-level granularity based on actual processing quality
- Preserves all diacritics (tashkeel) exactly as they appear in the source — stripping diacritics is information destruction
- Classifies structural format (prose, verse, Q&A, tabular, dictionary, commentary, mixed) from content analysis
- Passes through ALL source metadata unchanged (D-023)
- Produces a normalization quality report documenting what was found, what was uncertain, and what needs human review

**What is NOT this engine's responsibility:**
- Source acquisition, identification, metadata extraction — source engine
- Passage segmentation — passaging engine. The normalization engine discovers the source's OWN structure (its heading hierarchy); the passaging engine creates processing units from that structure.
- Content understanding: atom typing, excerpt grouping, topic classification, school attribution — Phase 2 engines
- Scholar authority management — source engine (primary), excerpting engine (enrichment)
- Taxonomy placement — taxonomy engine

**Phase classification:** Phase 1 (source-format-specific, above the normalization boundary). The normalization engine is the LAST component to touch source-format-specific data. Its output must be completely source-agnostic.

**Normalization boundary relationship:** The normalization engine produces the artifact that CROSSES the boundary. The normalized package is the single schema that all Phase 2 engines consume. The strictest test of the boundary is: if a developer adds a new source type, they write a new normalizer in this engine and nothing else changes in the entire application. If any Phase 2 engine would need modification to handle a new source type, the boundary has been violated.

**User scenarios served:**
- **Scenario 2 (Day 30):** A new Shamela source is acquired → the Shamela normalizer transforms it into a normalized package → passaging and downstream engines process it identically to any other source.
- **Scenario 6 (New Book Briefing):** Owner uploads iPhone photos → the image normalizer OCRs them, discovers what structure it can, and produces a normalized package. Text fidelity signal is `variable`, triggering more conservative downstream processing.
- **Scenario 8 (Correction):** A normalization error is discovered (footnotes mixed into main text, wrong layer attribution) → the normalization engine reprocesses the source with corrected rules → a new normalized package replaces the old one → downstream engines reprocess from the new package.
- **All scenarios:** Every excerpt, entry, and knowledge product in the library originates from a normalized package. Normalization quality determines knowledge quality.

---

## 2. Input Contract

The normalization engine receives two inputs per source.

**Frozen source file(s).** Located at `library/sources/{source_id}/frozen/`. These files are immutable (set read-only at freeze time by the source engine). The normalization engine reads them but never modifies them. For multi-file sources (multi-volume Shamela directories, photo sets), all files in the frozen directory are processed.

**Source metadata record.** Located at `library/sources/{source_id}/metadata.json`. The normalization engine reads the following fields from the source metadata:

- `source_id`: the canonical identifier for this source. Becomes the primary key linking the normalized package to its source.
- `source_format`: determines which normalizer processes this source. Values: `shamela_html`, `pdf_text`, `pdf_scanned`, `image_scan`, `epub`, `plain_text`, `owner_authored`. The source engine detects the source type during intake (§4.A.2 of source SPEC). If `source_format` is unrecognized, the normalization engine rejects with `NORM_UNKNOWN_SOURCE_FORMAT`.
- `work_id`: used for output file naming and cross-referencing.
- `text_fidelity`: the source-level fidelity signal from the source engine. The normalization engine uses this as a baseline and may refine it to page-level granularity based on actual processing quality (e.g., OCR confidence scores per page).
- `structural_format`: the source engine's initial classification (prose, verse, commentary, etc.). The normalization engine may override this if content analysis reveals a different format.
- `multi_layer`: boolean indicating whether this source contains text from multiple authors. When true, the `layers` field specifies which layers are present and who authored each.
- `genre`: affects normalization strategy (a `nazm` triggers verse-aware processing; a `mu'jam` triggers dictionary-entry-aware processing).
- `volume_count` and volume metadata: for multi-volume sources.

The normalization engine does NOT read: scholarly_context, trust_tier, genre_chain, or other metadata fields that are irrelevant to format transformation. These fields pass through untouched in the normalized package via the source_id reference.

**Validation on input.** The normalization engine validates before processing:
1. The frozen directory exists and contains at least one file.
2. The source metadata record exists and contains the required fields listed above.
3. The `source_format` is one of the recognized values.
4. For multi-volume sources: the volume files are present as described in the metadata.

If validation fails, the source is rejected with the appropriate error code (§7) and its processing status is set to `error`. The normalization engine never proceeds with a source that fails input validation — partial normalization is worse than no normalization because downstream engines would process corrupt data.

**Processing trigger.** The normalization engine picks up sources with `status: "acquired"` from the source registry. Processing is triggered either by a new source entering `acquired` status or by an explicit reprocessing request (after a normalization error correction or normalizer upgrade).

---

## 3. Output Contract

The normalization engine produces one primary artifact per source: the normalized package. It also updates the source registry and may write enrichments back to the source metadata record.

**Primary artifact: the normalized package.**

The normalized package is a directory at `library/sources/{source_id}/normalized/` containing two files:

1. **Manifest** (`manifest.json`): a single JSON document containing:
   - `schema_version`: string, format `normalized_package_v{major}.{minor}`. Current: `normalized_package_v2.0`.
   - `source_id`: the source's canonical identifier.
   - `normalizer_id`: which normalizer produced this package (e.g., `kr.normalization.shamela_v2`).
   - `normalization_utc`: ISO 8601 timestamp of normalization.
   - `division_tree`: the discovered structural hierarchy (see §4.A.6).
   - `layer_map`: for multi-layer sources, the detected text layers with their markers and authorship (see §4.A.5). For single-layer sources, this contains a single entry for the primary author.
   - `structural_format`: the engine's classification of the source's format (prose, verse, qa_format, tabular_khilaf, dictionary, commentary, mixed). May differ from the source metadata's initial classification.
   - `text_fidelity_summary`: aggregate text fidelity metrics for the entire source (mean OCR confidence if applicable, character-level fidelity estimate, pages with warnings).
   - `verse_detection`: whether versified text was found, and if so, the detected verse numbering scheme.
   - `total_content_units`: the number of content unit records in the accompanying JSONL.
   - `quality_report`: a structured summary of normalization quality — how many divisions were discovered with what confidence, how many layer transitions were detected, how many pages had warnings, what percentage of text is high-fidelity.
   - `normalization_warnings`: array of engine-level warnings (not per-page warnings, which are on the content units).

2. **Content stream** (`content.jsonl`): a JSONL file with one record per content unit. A content unit corresponds to one physical page of the source. Each record conforms to the content unit schema:

   - `schema_version`: string.
   - `source_id`: string.
   - `unit_index`: zero-based sequential integer, globally unique within this source. THE authoritative positional identifier.
   - `physical_page`: object with `volume` (int or null), `page_number_display` (string or null, Arabic-numeral form for citations), `page_number_int` (int or null).
   - `primary_text`: string. The main text content of this page, cleaned of all format-specific markup. All diacritics preserved exactly.
   - `text_layers`: array. For multi-layer sources, segments attributed to specific layers. Each segment: `layer_type` (matn/sharh/hashiyah/tahqiq_note/uncertain), `author_canonical_id`, `start` and `end` character offsets in `primary_text`, `confidence` (0.0–1.0). For single-layer sources, one segment covering the entire text.
   - `footnotes`: array of objects. Each: `ref_marker` (string), `text` (string), `footnote_type` (tahqiq_editor/author_original/unknown), `confidence` (0.0–1.0).
   - `structural_markers`: object. If a heading is detected on this page: `heading_detected` (bool), `heading_text` (string), `heading_level` (int), `heading_detection_method` (html_tagged/keyword_heuristic/llm_discovered/toc_inferred/human_override), `heading_confidence` (confirmed/high/medium/low).
   - `verse_info`: object or null. If verse is detected: `verse_lines` (array of verse line objects with hemistich markers and verse numbers if available).
   - `content_flags`: object. Boolean flags: `has_verse`, `has_table`, `has_quran_citation`, `has_hadith_citation`, `is_toc_page`, `is_index_page`, `is_blank`.
   - `text_fidelity`: object. `score` (high/medium/low/very_low), `ocr_confidence` (float or null), `warnings` (array of strings).

**Guarantees about the normalized package:**

- **Source-agnostic.** The content stream schema is identical regardless of which normalizer produced it. No field name, enum value, or structural convention depends on the source type. A Shamela normalizer and a PDF normalizer produce records with the same schema.
- **Ordering.** Content units are ordered by document order (volume ascending, then page ascending within volume). The `unit_index` field is zero-based and monotonically increasing.
- **Completeness.** Every physical page in the source that contains extractable text produces a content unit. Pages that are blank, TOC-only, or image-only with no OCR still produce a content unit with appropriate flags.
- **Text fidelity.** Every content unit carries its own fidelity assessment. Downstream engines can filter or flag based on per-page fidelity, not just source-level.
- **Layer annotation coverage.** For multi-layer sources, every character in `primary_text` is covered by exactly one segment in `text_layers`. No character is unattributed. If the normalizer cannot determine the layer for a region, it assigns `layer_type: "uncertain"` with a low confidence score.
- **Diacritics.** The `primary_text` field preserves all diacritical marks exactly as they appear in the source. No Unicode normalization of tashkeel is applied.
- **Footnote separation.** Footnotes are cleanly separated from primary text. Footnote reference markers in the primary text are replaced with inline markers in a universal format (`⌜1⌝` — using Unicode half-brackets, not format-specific conventions).
- **Division tree consistency.** Every heading detected in the content stream has a corresponding node in the manifest's division tree. The tree's page ranges are consistent with the content stream's unit_index values.

**Metadata pass-through (D-023).** The normalized package carries the `source_id` as its primary link to upstream metadata. Phase 2 engines access the full source metadata record via this reference. The normalization engine does NOT duplicate source metadata into the normalized package — it references it. This prevents metadata staleness: if the source engine enriches the metadata after normalization, Phase 2 engines see the enriched version automatically.

The normalization engine ADDS the following metadata that did not exist before normalization:
- Division tree (structural hierarchy)
- Per-page text fidelity scores
- Layer annotations with character-level segments
- Footnote type classification (author-original vs. tahqiq-editor)
- Structural format classification (may refine source engine's initial guess)
- Verse detection and numbering
- Content flags (TOC, index, blank, Quran/hadith citations)

**Source registry update.** Upon successful normalization, the source's processing status is updated from `acquired` to `normalized`. The normalized package path is recorded in the source registry.

**Enrichment write-back.** During normalization, the engine may discover information that should be recorded in the source metadata:
- Volume structure corrections (the source metadata says 4 volumes but only 3 have content)
- Structural format override (the source engine classified as prose but the normalizer detected verse)
- Multi-layer discovery (the source metadata said single-layer but the normalizer detected sharh markers)
- Encoding anomalies or quality issues

These discoveries are written back to the source metadata record through the enrichment interface defined in the source engine SPEC §2.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Normalizer Architecture

The normalization engine follows a dispatcher-normalizer pattern. A central dispatcher reads the `source_format` from the source metadata, selects the appropriate normalizer module, and invokes it. Each normalizer encapsulates ALL format-specific logic for one source type. The dispatcher knows nothing about any format.

**Normalizer interface.** Every normalizer implements the same interface:

- **Input:** a frozen source directory path and the source metadata record.
- **Output:** a normalized package (manifest + content JSONL) conforming to the universal schema.
- **Side effects:** enrichment write-backs to source metadata (optional), log entries.

The normalizer may be arbitrarily complex internally — thousands of lines, multi-pass, LLM-assisted. Its complexity is self-contained: no other normalizer and no Phase 2 engine is affected by its internal design. This is the normalization boundary's practical consequence for normalizer authors.

**Currently defined normalizers:**

| Source type | Normalizer | Status | Notes |
|---|---|---|---|
| `shamela_html` | Shamela normalizer | Existing code (1123L), needs upgrade | Most mature; ABD-era code handles basic content/footnote separation |
| `pdf_text` | Text PDF normalizer | [NOT YET IMPLEMENTED] | For PDFs with embedded text (digital-native or good text-layer) |
| `pdf_scanned` | Scanned PDF normalizer | [NOT YET IMPLEMENTED] | For scanned PDFs requiring OCR |
| `image_scan` | Image normalizer | [NOT YET IMPLEMENTED] | For iPhone photos and other image-based sources |
| `epub` | EPUB normalizer | [NOT YET IMPLEMENTED] | For EPUB format sources |
| `word_doc` | Word document normalizer | [NOT YET IMPLEMENTED] | For .doc/.docx files; uses Docling for extraction |
| `plain_text` | Plain text normalizer | [NOT YET IMPLEMENTED] | For raw text files with minimal structure |
| `owner_authored` | Owner content normalizer | [NOT YET IMPLEMENTED] | For owner's study notes, tarjih, research drafts |

**Adding a new normalizer.** To support a new source type: (1) create a normalizer module implementing the interface, (2) register the source type in the dispatcher's type map, (3) update the source engine to detect and classify the new type during intake. No Phase 2 code changes. No schema changes. No other normalizer changes.

#### §4.A.2 — Shamela Normalizer

The Shamela normalizer transforms Shamela desktop HTML exports into normalized packages. This is the most mature normalizer with existing code (1123 lines) and a validated specification (ABD_NORMALIZATION_SPEC.md). The existing code handles the v0.5 ABD specification; the KR upgrade adds layer detection, structure discovery integration, and the new output schema.

**Input:** One or more `.htm` files in Shamela export format. The format is validated against the corpus assumptions in ABD_NORMALIZATION_SPEC.md §6: PageText divs, PageHead headers, PageNumber spans, footnote separators, and the full set of structural markers documented in the Shamela HTML reference.

**Processing pipeline (6 passes):**

**Pass 1 — HTML parsing and page extraction.** Split the HTML at `<div class='PageText'>` boundaries. Extract page numbers from `<span class='PageNumber'>(ص: N)</span>`. Skip metadata pages (first PageText div with metadata labels). For multi-volume sources, process each file with its volume number derived from the filename stem. Assign monotonically increasing `unit_index` values across all volumes. This pass is deterministic and follows the existing ABD rules (§4.1–§4.4 of ABD_NORMALIZATION_SPEC.md).

**Pass 2 — Content/footnote separation.** Within each page, split at `<hr width='95'>` to separate primary text from footnotes. Parse footnotes into individual entries using the `(N)` marker pattern. Classify footnote sections as `numbered_parens`, `bare_number`, `unnumbered`, or `none`. Capture footnote preamble text. Strip footnote reference markers from primary text only when a matching footnote exists on the same page. This pass follows ABD rules §4.5–§4.6, upgraded to classify footnote type:
- If the footnote contains tahqiq markers (hadith grading, manuscript variant notation like "في نسخة:", bibliographic references to collections), classify as `tahqiq_editor`.
- If the footnote appears to be the author's own note (matches the main text's writing style, no tahqiq markers), classify as `author_original`.
- If uncertain, classify as `unknown_footnote_type` with a confidence score.

**Pass 3 — HTML stripping and text cleaning.** Remove all HTML tags (preserving text content). Decode HTML entities. Normalize line endings and whitespace per ABD rules §4.7–§4.9. Preserve asterisks, ZWNJ characters, and all other source data markers. Preserve all diacritics exactly.

**Pass 4 — Structure discovery.** This is a major expansion from ABD. The existing `discover_structure.py` (2896 lines) implements a 4-tier confidence architecture for heading detection. The KR upgrade integrates structure discovery into the normalizer's pipeline:

- **Tier 1 (HTML-tagged headings):** Extract `<span class="title">` elements from the frozen HTML (not from cleaned text — tags are needed). These are confirmed headings.
- **Tier 1.5 (TOC parsing):** If a TOC page is detected, parse it for cross-referencing against discovered headings.
- **Tier 2 (Keyword heuristics):** Scan cleaned text for structural keywords (باب, فصل, مبحث, فائدة, تنبيه, قاعدة, خاتمة, مقدمة) at line beginnings, using patterns from `structural_patterns.yaml`. Apply ordinal detection for sequential headings. ZWNJ heading detection (double ZWNJ at line start) provides a high-confidence signal validated across 9.5% of the Shamela corpus.
- **Tier 3 (LLM semantic judgment):** For headings that Tier 2 detects with low confidence, or for sources where Tiers 1 and 2 find very few headings, invoke an LLM to examine candidate boundaries. The LLM receives the source's known genre, the headings found so far, and a window of text around candidate boundaries. LLM-discovered headings carry confidence based on the LLM's stated certainty.

The output is a division tree stored in the manifest's `division_tree` field, and each content unit records detected headings in `structural_markers`.

**Pass 5 — Multi-layer detection.** For sources where `multi_layer` is true in the source metadata (or where the normalizer detects layer signals even when the source engine didn't flag it), identify which portions of each page's text belong to which layer.

Shamela-specific layer signals:
- **Bold text** (detected from `<b>` tags in HTML before stripping in Pass 1): In many Shamela commentary exports, matn text is bold. The normalizer records bold spans and their character offsets during Pass 1.
- **Bracket markers:** Matn text enclosed in brackets: `[ المبتدأ هو الاسم المرفوع ]`.
- **Transition phrases:** "قال المصنف" (the author said), "قوله" (his saying), "قال الشارح" (the commentator said). Detected by pattern matching.
- **Font size differences:** Some exports use `<font size>` tags for layer distinction. Detected before stripping.

For each page, the normalizer produces a `text_layers` array segmenting primary text into attributed regions with layer types, author canonical_ids, character offsets, and confidence scores.

**Pass 6 — Output generation.** Assemble the manifest and content JSONL. Validate against the schema. Compute the quality report. Write to `library/sources/{source_id}/normalized/`.

**Verse detection.** ABD rules §4.8 detect verse markers (asterisks, hemistich separators). KR extends this: for `nazm` sources, verse-aware processing identifies each بيت, normalizes hemistich separators, and captures verse numbers as metadata. Verse numbers are critical scholarly references (e.g., "ألفية line 75").

#### §4.A.3 — PDF Normalizer (Text-Embedded)

For PDFs with embedded text (digital-native PDFs, PDFs with a usable text layer), the text PDF normalizer extracts content without OCR.

**Technical approach:** Use Docling (IBM, Apache 2.0) as the primary PDF parsing backend. Docling's layout analysis model (DocLayNet) identifies document elements; Docling's table structure model (TableFormer) handles tables. Docling produces a structured `DoclingDocument` representation with reading order, hierarchy, and element types.

**Processing pipeline:**

1. **PDF parsing via Docling.** Convert the frozen PDF using Docling's `DocumentConverter`. This produces a structured document with per-page layout analysis, reading order detection, and element classification.
2. **Text extraction.** Extract text content per page in reading order. Docling handles RTL reading order for Arabic. Preserve paragraph boundaries as detected by the layout model.
3. **Footnote detection.** Elements classified as footnotes or marginalia by Docling are separated from main text. The normalizer applies footnote type classification (tahqiq_editor vs. author_original) using content analysis.
4. **Structure discovery.** Docling detects headers and section structure from PDF formatting. The normalizer maps Docling's elements to the KR division tree format, augmented with Arabic keyword heuristic detection for structural keywords Docling may not recognize.
5. **Page boundary capture.** PDF pages map directly to physical pages. Page numbers extracted from Docling's detected elements or from the PDF page index.
6. **Multi-layer detection.** For commentary PDFs, layers are detected via font analysis: different layers often use different font sizes or weights. Docling's layout analysis provides font metadata. Supplemented with transition phrase detection.
7. **Diacritics.** Text extracted from text-layer PDFs preserves diacritics as encoded. No normalization applied.
8. **Output.** Standard normalized package.

**Text fidelity:** Text-embedded PDFs default to `high`. If Docling reports extraction issues, fidelity is downgraded per page.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on Docling installation and Arabic RTL configuration.

#### §4.A.4 — Scanned PDF and Image Normalizer

For scanned PDFs (pages are images with no usable text layer) and image-based sources (iPhone photos), the normalizer performs OCR.

**OCR strategy — tiered approach:**

1. **Primary: Mistral OCR 3** (`mistral-ocr-latest`). Commercial API with best multilingual document understanding. Processes PDF pages or images, returns Markdown with layout preservation. Strong Arabic support. Cost: $1–2 per 1000 pages.

2. **Specialized: Qari-OCR** (open-source, Arabic-specific). For pages where Mistral OCR's output has low confidence on diacritically-heavy text, the normalizer falls back to Qari-OCR v0.2, fine-tuned specifically for Arabic tashkeel. CER 0.061 on diacritically-rich texts. Runs locally on GPU.

3. **Validation: dual-OCR comparison.** For sources with `text_fidelity: "low"` (iPhone photos) or critical scholarly texts, run BOTH Mistral OCR and Qari-OCR on the same page and compare. Agreement increases confidence; disagreement triggers character-level alignment to produce merged output with per-character confidence. High-disagreement pages are flagged for human review.

**Processing pipeline:**

1. **Page rendering.** For PDFs: render each page at 300+ DPI (600 DPI for scholarly texts with small print). For images: use as-is with pre-processing.
2. **Pre-processing (images).** Auto-detect orientation and rotate. Perspective correction for angled photos. Brightness/contrast adjustment. For scanned PDFs: skew correction, noise reduction.
3. **OCR execution.** Send to Mistral OCR 3 via API. Parse returned Markdown to extract main text, footnotes (from layout position), headers/footers, page numbers.
4. **Arabic-specific post-processing.**
   - **ب/ت/ث/ن disambiguation:** These letters differ only in dots — the most common OCR confusion. Flag potential confusions using CAMeL Tools morphological analysis (do NOT auto-correct — flag for downstream review).
   - **Hamza normalization check:** Flag pages with unusual hamza patterns.
   - **Diacritics validation:** Flag impossible diacritic sequences as likely OCR errors.
5. **Structure discovery.** Less reliable for OCR text. Uses layout-based detection from Mistral OCR's Markdown formatting, keyword heuristics, and LLM assistance. Confidence levels are typically lower than for structured text.
6. **Multi-layer detection.** Based on visual font size differences from OCR spatial output. Less reliable than HTML-based detection. Confidence typically `medium` or `low`.
7. **Page boundaries.** Scanned PDFs: one page per PDF page. Images: one page per image file, ordered by filename (numeric sort) or OCR-detected page numbers.
8. **Text fidelity.** Per-page based on OCR confidence, dual-OCR agreement, and character-level statistics. Levels: `high` (>0.95 confidence), `medium` (0.80–0.95), `low` (0.60–0.80), `very_low` (<0.60, flag for human review).

**iPhone photo-specific handling:** Variable lighting → adaptive thresholding. Perspective distortion → edge detection and correction. Partial pages → detected and flagged as `partial_page`. Finger obstruction → cannot recover; flag occluded regions. Sequential ordering → by filename or OCR-detected page numbers.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on Mistral OCR API access, Qari-OCR local installation, image pre-processing library.

#### §4.A.5 — Multi-Layer Text Detection

Multi-layer text detection is the highest-integrity-risk operation in the normalization engine. If it fails, downstream engines attribute text to the wrong author — a scholarly integrity violation (see DOMAIN.md "The Multi-Layer Text Problem").

**The layer model.** A multi-layer source contains text from up to four layers:

| Layer | Type | Author | Typical markers |
|---|---|---|---|
| 1 | `matn` | Original author | Bold, brackets, explicit markers |
| 2 | `sharh` | Commentator | Main body text |
| 3 | `hashiyah` | Marginal annotator | Smaller text, marginal notes |
| 4 | `tahqiq_note` | Modern editor | Footnotes, variant readings |

Not all layers are present in every multi-layer source. The source metadata's `layers` field specifies which are present.

**Layer detection signals (by reliability):**

1. **Explicit transition markers** (confidence ≥ 0.90):
   - "قال المصنف:" → transition to Layer 1
   - "قال الشارح:" → transition to Layer 2 (in hashiyah context)
   - "قوله:" → typically introduces Layer 1 text within Layer 2
   - "أقول:" → confirms current layer's author speaking

2. **Typographic signals** (reliability varies by source type):
   - Shamela HTML: bold tags → Layer 1 (reliable in ~75% of commentary exports). Font size. Brackets.
   - PDF text: font size/weight differences from Docling output.
   - Scanned PDF/image: visual font size from OCR spatial output (less reliable).

3. **Content-based inference** (lowest reliability):
   - Terse, definitional text → likely Layer 1 (matn)
   - Explanatory, discursive text → likely Layer 2 (sharh)
   - Opinion reporting verbs (قال, ذهب, يرى) → likely Layer 2

**Detection algorithm:**
1. Start with the source metadata's layer specification.
2. Scan for explicit transition markers → high-confidence boundaries.
3. Scan for typographic signals → medium-high confidence boundaries.
4. Infer layer for regions between boundaries from surrounding context.
5. For regions with no signals, assign the default layer (Layer 2 in sharh, Layer 3 in hashiyah).
6. Validate: Layer 1 text should be a minority of total text in commentaries. If Layer 1 exceeds 40%, flag for review.

**Conservative default:** When confidence is low, attribute to the commentary author (Layer 2), not the matn author. Misattributing commentary to the commentator is less harmful than attributing verbose explanation to an author known for terseness.

#### §4.A.6 — Structure Discovery

Structure discovery identifies the source's internal organizational hierarchy — headings, chapters, divisions. This is the normalization engine's job because structural signals are format-specific and are lost after normalization.

**The division tree.** Output is a tree of division nodes. Each node: `div_id`, `type` (باب/فصل/مبحث/etc./implicit/volume/root), `title`, `level`, `detection_method`, `confidence`, `start_unit_index`, `end_unit_index`, `parent_div_id`, `child_div_ids`, `page_hint_start`, `page_hint_end`, `digestible` (whether content is extractable), `editor_inserted` (whether heading was added by an editor, not the original author).

**The four-tier confidence architecture:**

- **Tier 1 (confirmed):** Headings from explicit structural markup. Shamela: `<span class="title">` tags. PDFs: heading elements from Docling with high confidence.
- **Tier 2 (high/medium):** Keyword heuristic detection. Lines starting with باب, فصل, مبحث, etc. at paragraph beginnings, with ordinal patterns (الباب الأول, الفصل الثاني). ZWNJ heading markers (double ZWNJ at line start, 9.5% of Shamela corpus).
- **Tier 3 (LLM-assisted):** When Tiers 1–2 find insufficient structure (<3 divisions in 100+ pages), LLM examines candidate boundaries. Receives genre, existing headings, text windows. Confidence `medium` or `low`.
- **Tier 4 (human gate):** Low-confidence divisions flagged for owner review.

**TOC cross-referencing.** If a table of contents is found (فهرس, فهرس الموضوعات, المحتويات), parse it for title-to-page mappings. TOC entries validate Tier 1/2/3 discoveries (matching entries promote to `high` confidence) and trigger targeted search for missing headings.

**Hierarchy inference rules:**
1. `كتاب` > `باب` > `فصل` > `مبحث` > `مطلب` > `فائدة/تنبيه/قاعدة` (standard Arabic scholarly hierarchy).
2. Ordinal sequences are siblings at the same level.
3. Ambiguous levels resolved by keyword type, ordinal position, nesting context, and LLM assistance.
4. Volume boundaries at level 0 (children of root).

**Structure confidence scoring** (manifest-level):
- `high`: >80% of divisions at Tier 1 or high-confidence Tier 2.
- `medium`: 50-80% high-confidence.
- `low`: <50% high-confidence.
- `minimal`: <3 divisions in 50+ pages. Passaging engine creates its own boundaries.

#### §4.A.7 — Page Boundary Preservation

Scholars cite by volume and page: "المغني vol.3 p.245." The normalization engine preserves page boundaries so this citation chain is never broken.

**Per content unit:** `volume` (int or null), `page_number_display` (Arabic-Indic form for citations), `page_number_int` (integer for sorting), `unit_index` (authoritative positional identifier).

**Critical rule:** `unit_index` is the ONLY positional identifier Phase 2 engines may use. `page_number_int` is display metadata only. Some sources have duplicate page numbers (29.8% of Shamela corpus), non-sequential numbering, or unnumbered pages.

**Non-page-based sources.** Plain text and owner-authored content create content units at paragraph boundaries or ~2000-character intervals. Physical page fields are null; only `unit_index` is meaningful.

**Cross-page text.** The normalization engine does NOT join text across page boundaries. Each content unit contains exactly the text on that physical page. The passaging engine handles cross-page continuity using `unit_index` adjacency. Joining would lose citation boundary information.

#### §4.A.8 — Diacritics and Arabic Text Handling

**Diacritics preservation is absolute.** Every diacritical mark preserved exactly: harakat (fatha, damma, kasra), tanwin, sukun, shadda, superscript alef, maddah. No stripping, no modification.

**No Unicode normalization.** NFC, NFD, NFKC, NFKD normalization is NOT applied to Arabic text. Different Unicode representations of the same visual character are preserved as-is.

**Encoding handling.** All output is UTF-8. Source encoding conversion logged. Mojibake flagged with `text_fidelity: "low"`.

**Whitespace normalization (conservative):** `\r\n`/`\r` → `\n`. Non-breaking spaces → regular spaces. Multiple consecutive spaces → single space. Three+ blank lines → one blank line. Leading/trailing line whitespace trimmed. No other text transformation: no spelling correction, no punctuation changes, no reordering.

#### §4.A.9 — Content Flagging

Each content unit carries `content_flags` providing hints to downstream engines:

- `has_verse`: verse patterns detected (asterisks, hemistich separators, or `nazm` genre with verse structure).
- `has_table`: tabular content detected. Shamela: `<table>` tags. PDF: Docling table detection. OCR: layout-based detection.
- `has_quran_citation`: Quran citation markers detected ({verse text}, "قال تعالى", surah/ayah references).
- `has_hadith_citation`: hadith citation patterns detected ("قال النبي ﷺ", "عن ... قال", collection references).
- `is_toc_page`: page is part of table of contents.
- `is_index_page`: page is part of an index (فهرس الأعلام, فهرس الأحاديث).
- `is_blank`: no extractable text content.

Flags are advisory. Downstream engines may override based on deeper analysis. The normalization engine uses surface-level signals only.

[CONTINUES NEXT SESSION]

### §4.B — Transformative Capabilities

#### §4.B.1 — Scholarly Text Layer Intelligence

**Capability:** Beyond basic multi-layer detection (§4.A.5), the normalization engine infers layer boundaries in sources where explicit typographic or verbal markers are absent or inconsistent. Many scholarly commentaries, especially older prints without tahqiq, have no bold formatting, no brackets, and irregular use of "قال المصنف." In these sources, the layer structure must be inferred from content patterns.

**Technical approach:** The normalization engine trains an LLM-based layer classifier that operates on a sliding window of text. The classifier receives: a ~500-word window, the source's known layer composition (from metadata), the commentary genre (sharh/hashiyah), and examples of each layer's writing style from the same source (bootstrapped from high-confidence detections in earlier pages).

The classifier distinguishes layers using these content signals:
- **Terseness ratio:** Matn texts are characteristically dense — more technical terms per sentence, fewer connective particles, shorter sentences. The classifier measures information density per sentence and flags dense regions as likely matn.
- **Pronoun reference patterns:** In a sharh, the commentator uses third-person pronouns to refer to the matn author ("قال", "أراد", "يعني") and first-person for their own analysis ("أقول", "والصحيح عندي"). The classifier tracks pronoun patterns to detect layer shifts.
- **Temporal markers:** The commentator often references the matn author as historical ("وعند المصنف" — "according to the author"), while the matn author writes in the present tense of scholarly assertion. These temporal frames differ between layers.
- **Citation patterns:** The matn author rarely cites themselves; the commentator frequently cites the matn author and other scholars. Citation density signals which layer is active.

**What this enables:** Sources that would otherwise be processed as single-layer (because no typographic markers exist) can be correctly segmented. This prevents the most common form of layer misattribution — treating the entire text as the commentary author's words, which erases the matn author's contributions from the library. For the synthesizer, this means the definition "المبتدأ هو الاسم المرفوع" can be correctly attributed to ابن مالك (d. 672 AH) rather than ابن عقيل (d. 769 AH) even when the printed edition uses no bold or bracket formatting.

**Confidence and validation:** Content-inferred layer boundaries carry confidence `medium` at best. The normalization engine cross-validates inferred boundaries against any typographic signals that exist (even partial ones) and against the expected layer proportion (matn should be a minority). Pages where content inference disagrees with typographic signals are flagged with confidence `low` for human review.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: LLM prompt engineering for Arabic layer classification, bootstrapping system for per-source style examples.

#### §4.B.2 — Structural Format Auto-Detection

**Capability:** The normalization engine automatically detects the source's structural format from content analysis, even when the source metadata does not specify it or specifies it incorrectly. This goes beyond genre classification (which the source engine handles at intake) to detect the actual TEXT STRUCTURE within a source.

**Technical approach:** The normalizer analyzes the first 20 content units (or all units for short sources) to detect structural patterns:

- **Q&A format detection:** Pattern: "مسألة:" or "سُئل عن" or "سؤال:" followed by a question, then "الجواب:" or "فأجاب:" followed by an answer. When Q&A patterns appear on >30% of analyzed pages, classify as `qa_format`. This is common in fatwa collections (مجموع الفتاوى) and مسائل books.
- **Tabular khilaf detection:** Pattern: "المسألة:" followed by "القول الأول:" / "القول الثاني:" / "الراجح:" structures. These map almost directly to taxonomy entries. When this pattern appears on >20% of analyzed pages, classify as `tabular_khilaf`.
- **Dictionary detection:** Pattern: root-organized entries (entries starting with Arabic root letters in a systematic sequence), or alphabetically organized entries. Short self-contained entries separated by clear markers. Classify as `dictionary`.
- **Verse detection:** When >50% of content lines match verse patterns (hemistich separators, line-level structure, consistent rhyme scheme at line ends), classify as `verse`. For mixed sources (a prose sharh containing quoted verse), the verse portions are flagged per-page without changing the overall classification.
- **Mixed format detection:** When multiple structural patterns are detected (e.g., a commentary with embedded Q&A sections and quoted verse), classify as `mixed` with a breakdown of which format appears in which divisions.

**What this enables:** The passaging engine and excerpting engine can apply format-appropriate strategies without format-specific code. A Q&A-format source produces natural passage boundaries at question-answer pairs. A dictionary produces passage boundaries at entries. A verse source produces passages respecting بيت boundaries. This information flows through the normalized package as metadata — the passaging engine reads `structural_format` and applies the right strategy without knowing anything about the source format.

**Validation:** Auto-detection results are compared against the source engine's initial genre classification. If they disagree (e.g., source engine says `prose` but normalizer detects `qa_format`), both are recorded: the normalizer's detection in the manifest's `structural_format` field, with a note that it overrides the source metadata's classification. An enrichment write-back updates the source metadata.

#### §4.B.3 — Fine-Grained Text Fidelity Mapping

**Capability:** Instead of a single fidelity score per source or per page, the normalization engine produces a character-level fidelity map for OCR-processed sources. This map identifies exactly WHICH portions of a page are reliable and which are uncertain.

**Technical approach:** When dual-OCR comparison is active (§4.A.4), character-level alignment between Mistral OCR and Qari-OCR outputs produces an agreement map. Characters where both engines agree have high fidelity. Characters where they disagree are flagged with the alternatives and a confidence estimate. This produces a fidelity heat map per page.

Even with single-OCR processing, the normalizer computes a fidelity map from:
- OCR engine's per-character or per-word confidence scores (Mistral OCR 3 provides these in detailed output mode)
- Known OCR confusion patterns for Arabic (ب/ت/ث/ن, ح/خ/ج, ر/ز, similar-looking letter pairs)
- Morphological validation: words that don't exist in the Arabic lexicon are lower-fidelity than valid words
- Diacritics confidence: diacritics on unusual positions receive lower confidence

**What this enables:** The excerpting engine can flag excerpts that contain low-fidelity regions rather than flagging entire pages. An excerpt where 95% of characters are high-fidelity and 5% are uncertain gets a nuanced fidelity score rather than being marked as uniformly unreliable. The synthesizer can weight high-fidelity excerpts more heavily and can note uncertainty at the character level: "The text reads عِلْم (knowledge), though the OCR confidence for the diacritics is moderate."

The scholar interface can display the fidelity heat map overlaid on the source text, letting the owner see exactly where OCR was confident and where it wasn't. This supports the owner's ability to verify KR's claims against the physical book.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: Mistral OCR detailed output mode, Qari-OCR local processing, CAMeL Tools morphological analysis.

#### §4.B.4 — Footnote Apparatus Classification

**Capability:** The normalization engine classifies each footnote not just as "author-original" vs. "tahqiq-editor" but into a fine-grained taxonomy that the synthesizer uses to extract maximum scholarly intelligence from the editorial apparatus.

**Footnote taxonomy:**
- `variant_reading`: the editor notes a textual difference between manuscripts. Pattern: "في نسخة:", "في الأصل:", "كذا في ج", variant markers. Contains: the variant text, which manuscripts show which reading, which reading the editor preferred.
- `hadith_takhrij`: the editor traces a hadith to its original collection(s). Pattern: "رواه البخاري", "أخرجه مسلم", collection/book/chapter/number references. Contains: hadith collection, book, number, grading. This is CRITICAL for the synthesizer's evidence-aware entries (D-023).
- `cross_reference`: the editor points to where the same topic is discussed elsewhere. Pattern: "انظر:", "تقدم في:", "سيأتي في:". Contains: the referenced location (volume/page or chapter).
- `biographical_note`: the editor identifies a scholar mentioned in the text. Pattern: "هو:", biographical data, birth/death dates. Contains: scholar identification data that enriches the scholar authority model.
- `linguistic_note`: the editor explains an unusual word or grammatical construction. Pattern: "اللغة:", "لغة:", grammatical analysis.
- `correction_note`: the editor corrects what they believe is an error in the text. Pattern: "الصواب:", "لعل الصواب:", correction markers.
- `general_commentary`: the editor's own scholarly opinion or additional information.

**Technical approach:** Each footnote is classified using pattern matching (for structured markers like "رواه البخاري") and LLM classification (for footnotes without clear markers). The LLM receives the footnote text, the main text it references, and a description of each footnote type. Classification confidence accompanies each assignment.

**What this enables:** The excerpting engine can route hadith takhrij data to hadith metadata fields. The synthesizer can produce evidence-aware entries: "The Hanafi position rests on a hadith narrated by Abu Dawud (graded hasan by the editor), while the Shafi'i position cites a hadith in Bukhari (sahih)." Variant readings feed the source engine's edition comparison capability. Biographical notes enrich the scholar authority model. All of this metadata is extracted from the footnote apparatus during normalization — if it isn't captured here, it's lost.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: LLM footnote classifier, pattern library for Arabic scholarly footnote conventions.

---

## 5. Validation and Quality

The normalization engine's output determines the quality ceiling for every downstream knowledge product. An error here cascades: footnotes mixed into main text → wrong excerpts → wrong entries → wrong knowledge in the owner's mind.

**Layer 1: Self-validation (automated, at normalization time).**

1. **Schema compliance.** Every content unit is validated against the content unit schema before writing. The manifest is validated against the manifest schema. Any schema violation aborts normalization with a structured error.

2. **Coverage check.** The number of content units must match the expected page count from the source metadata (±10% tolerance for skipped metadata/blank pages). A significant mismatch (>10%) triggers a warning and requires human review.

3. **Text extraction verification.** For each content unit:
   - `primary_text` must be non-empty (except for `is_blank` pages).
   - Character distribution must be plausible for Arabic text: >70% Arabic characters (excluding whitespace and punctuation). A page with <70% Arabic characters is flagged as potentially corrupted.
   - No runs of >20 identical characters (suggests OCR garbage).
   - No mojibake patterns (common UTF-8 decoding errors for Arabic).

4. **Layer consistency check.** For multi-layer sources:
   - Every character in `primary_text` is covered by exactly one `text_layers` segment.
   - Layer proportions are plausible: Layer 1 (matn) should be <40% of text in a sharh. Layer 2 (sharh) should be the majority in a sharh.
   - Layer transitions are not excessive: >20 transitions per page suggests misdetection.
   - Layer `author_canonical_id` values match the source metadata's layer specification.

5. **Division tree validity.**
   - Every division node has valid `start_unit_index` ≤ `end_unit_index`.
   - Sibling divisions do not overlap in their page ranges.
   - Child divisions are contained within their parent's page range.
   - The tree covers the entire source: no content units are outside all divisions (except root).

6. **Footnote integrity.**
   - Footnote text is non-empty for parsed footnotes.
   - Footnote reference markers in primary text have corresponding footnote entries (orphan references trigger warnings).

**Layer 2: Quality report review.**

The manifest's `quality_report` field provides a dashboard for human review:
- Total content units, broken down by fidelity level (high/medium/low/very_low).
- Layer detection summary: pages with detected layers, pages uncertain, pages with no layer signals.
- Structure discovery summary: divisions found by tier, overall confidence.
- Footnote summary: classified footnotes by type, unclassified footnotes.
- Warnings: total count, most common warning types.

The quality report enables targeted human review: instead of reviewing every page, the owner (or a future automated quality reviewer) focuses on low-fidelity pages, uncertain layer attributions, and low-confidence divisions.

**Layer 3: Human gate integration.**

Conditions triggering human gate review for normalization:
- Source-level text fidelity is `low` or `very_low` (>25% of pages are low-fidelity).
- Multi-layer detection confidence is below `medium` for >30% of pages.
- Structure discovery confidence is `minimal` (fewer than 3 divisions in 50+ pages).
- The normalizer detects a structural format that contradicts the source metadata's classification.
- More than 10% of footnotes are unclassified.

The human gate presents: sample pages from the normalized output with the original source side-by-side (for visual comparison), the quality report, and specific items requiring decision (uncertain layers, low-confidence divisions, format classification disagreement).

**Scholarly integrity guarantee:** No normalized package enters the pipeline without: (1) validated schema compliance, (2) plausible text extraction verified, (3) known fidelity levels per page, (4) layer attributions with confidence scores. These guarantees ensure that downstream engines process data with known quality characteristics — they can trust high-fidelity content and flag low-fidelity content, rather than blindly trusting all text equally.

---

## 6. Consensus Integration

The normalization engine does NOT use multi-model consensus for its core operations.

**Rationale:** Normalization is primarily deterministic (HTML parsing, text extraction, whitespace normalization) or uses specialized tools (OCR engines, layout analysis models) rather than general-purpose LLMs. The LLM-assisted components (Tier 3 structure discovery, layer inference, footnote classification) are supplementary rather than primary, and their outputs carry explicit confidence scores that downstream engines can evaluate.

Where the normalization engine does use LLMs:
- **Tier 3 structure discovery:** Single-model LLM judgment with confidence scoring. Consensus would add cost without proportionate quality gain because structure discovery is cross-validated against Tier 1/2 evidence and the TOC.
- **Content-based layer inference (§4.B.1):** Single-model with bootstrapped examples. Cross-validated against typographic signals.
- **Footnote classification (§4.B.4):** Single-model with pattern matching as primary, LLM as fallback.
- **Dual-OCR comparison (§4.A.4):** This IS a form of consensus — two independent OCR engines process the same input. Agreement means high confidence; disagreement is resolved by character-level analysis. This is more effective than multi-model LLM consensus for text extraction because the disagreement signals are character-level rather than semantic.

If future experience shows that LLM-assisted operations in this engine have unacceptable error rates, multi-model consensus can be added to specific operations without architectural changes — each LLM call is already a well-defined function with structured inputs and outputs.

---

## 7. Error Handling

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `NORM_UNKNOWN_SOURCE_FORMAT` | Fatal | `source_format` not recognized | Reject. Owner or source engine must correct the metadata. |
| `NORM_MISSING_FROZEN` | Fatal | Frozen directory empty or missing | Reject. Source engine must re-freeze. |
| `NORM_MISSING_METADATA` | Fatal | Source metadata record missing or invalid | Reject. Source engine must recreate metadata. |
| `NORM_SCHEMA_VIOLATION` | Fatal | Output fails schema validation | Abort normalization. Log the violation. This is a normalizer bug. |
| `NORM_OCR_FAILED` | Fatal | OCR engine returns error or empty result | Retry once. If still failed, reject with the OCR error message. |
| `NORM_ENCODING_ERROR` | Warning | Source uses unrecognized or corrupted encoding | Convert what is possible. Flag affected pages as `text_fidelity: "low"`. |
| `NORM_LOW_FIDELITY` | Warning | >25% of pages have fidelity below `medium` | Normalization completes. Human gate triggered. |
| `NORM_LAYER_UNCERTAIN` | Warning | Layer detection confidence below threshold for >30% of pages | Normalization completes. Human gate triggered. Downstream engines see confidence scores. |
| `NORM_SPARSE_STRUCTURE` | Warning | Fewer than 3 divisions in 50+ pages | Normalization completes. Human gate triggered. Passaging engine warned. |
| `NORM_FORMAT_MISMATCH` | Info | Detected structural format differs from source metadata | Write-back enrichment to source metadata. Log. |
| `NORM_PAGE_COUNT_MISMATCH` | Warning | Content unit count differs >10% from expected page count | Log. May indicate skipped pages or extra content. |
| `NORM_DUPLICATE_PAGES` | Info | Duplicate page numbers detected | Log. Use `unit_index` as authoritative reference. |
| `NORM_PARTIAL_PAGE` | Warning | Image source: page appears truncated | Flag content unit. |
| `NORM_OCR_API_RATE_LIMIT` | Warning | Mistral OCR API rate limited | Implement exponential backoff. Retry. |

**Principle:** Never lose data silently. Every error is logged with: timestamp, source_id, error code, severity, human-readable message, affected unit_index (if page-specific), and recovery action taken.

**Logging:** All normalization events logged to `library/logs/normalization_engine.jsonl`. Each log entry: timestamp, source_id, event type, details. The log is append-only.

**Alerting:** Fatal errors during batch processing, >20% of sources in a batch hitting warnings, OCR API availability issues.

---

## 8. Configuration

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| `ocr_primary_engine` | `mistral_ocr_3` | `mistral_ocr_3`, `qari_ocr`, `google_doc_ai` | Primary OCR engine for scanned/image sources |
| `ocr_dpi_standard` | 300 | 200–600 | DPI for rendering scanned PDF pages |
| `ocr_dpi_scholarly` | 600 | 300–1200 | DPI for small-print scholarly texts |
| `dual_ocr_enabled` | `false` | boolean | Whether to run dual-OCR comparison |
| `dual_ocr_threshold` | `low` | `low`, `very_low`, `all` | Which fidelity levels trigger dual-OCR |
| `layer_detection_enabled` | `true` | boolean | Whether to perform multi-layer detection |
| `layer_matn_max_ratio` | 0.40 | 0.10–0.60 | Maximum expected Layer 1 proportion in commentaries |
| `structure_llm_threshold` | 3 | 1–20 | Minimum divisions before Tier 3 LLM is skipped |
| `structure_min_pages_for_llm` | 50 | 10–500 | Minimum source pages to trigger Tier 3 LLM |
| `fidelity_high_threshold` | 0.95 | 0.85–0.99 | OCR confidence threshold for `high` fidelity |
| `fidelity_medium_threshold` | 0.80 | 0.60–0.95 | OCR confidence threshold for `medium` fidelity |
| `fidelity_low_threshold` | 0.60 | 0.40–0.80 | OCR confidence threshold for `low` fidelity |
| `human_gate_fidelity_trigger` | 0.25 | 0.10–0.50 | Proportion of low-fidelity pages triggering human gate |
| `mistral_ocr_api_key` | env: `MISTRAL_API_KEY` | string | Mistral OCR API key |
| `mistral_ocr_batch_mode` | `true` | boolean | Use batch API for cost savings |
| `max_pages_per_batch` | 100 | 10–1000 | Maximum pages per OCR batch request |

**Per-science configuration hooks (Level 3 / SCIENCE.md):**

Each science may customize:
- Structure discovery keyword weights (some sciences use different heading conventions).
- Layer detection expectations (not all sciences have multi-layer sources).
- Content flag patterns (science-specific citation patterns for Quran/hadith detection).
- Expected structural depth (fiqh books typically have deeper hierarchies than nahw books).

**What is hardcoded and why:**
- The normalized package schema version format (`normalized_package_v{major}.{minor}`) — changing this would break Phase 2 engines' schema validation.
- The content unit schema structure — this IS the normalization boundary contract; changing it requires coordinated updates across all Phase 2 engines.
- The universal footnote reference marker format (`⌜N⌝`) — Phase 2 engines parse this; changing it breaks footnote reference resolution.
- The `unit_index` as authoritative positional identifier — all Phase 2 engines depend on this contract.

---

## 9. Current Implementation State

**Existing files:**
- `engines/normalization/src/normalizers/normalize_shamela.py` (1123 lines): ABD-era Shamela normalizer. Implements: HTML page extraction, content/footnote separation, footnote parsing (numbered_parens, bare_number, unnumbered), HTML tag stripping, text cleaning, verse detection, table extraction, image-only page detection, ZWNJ heading detection. Outputs ABD-era JSONL format (not KR normalized package format).
- `engines/normalization/src/discover_structure.py` (2896 lines): Structure discovery. Implements: 4-tier heading detection (HTML-tagged, TOC parsing, keyword heuristics, LLM semantic judgment), hierarchy inference, division tree construction, confidence scoring. Outputs ABD-era division format.
- `engines/normalization/src/validate_structure.py` (333 lines): Validates structure discovery output.
- `engines/normalization/tests/` — 292 tests covering Shamela normalization and structure discovery.
- `engines/normalization/reference/` — 15 ABD-era reference documents including detailed Shamela HTML format documentation, structural patterns, and edge cases.

**What works today:**
- Shamela HTML normalization with content/footnote separation, all text cleaning rules, verse/table detection.
- Structure discovery with 4-tier confidence architecture for Shamela sources.
- Structure validation.
- 292 passing tests.

**Known gaps between current code and this SPEC:**

1. **Output schema.** Code produces ABD-era JSONL (`book_id`, `matn_text`, `footnotes` list). SPEC requires KR normalized package format (`source_id`, `primary_text`, `text_layers`, `text_fidelity`, `content_flags`, manifest + content JSONL). [NOT YET IMPLEMENTED]

2. **Multi-layer detection.** Code has no layer detection. SPEC requires per-page layer segmentation with character offsets and confidence scores. The bold/bracket/transition-phrase detection logic does not exist. [NOT YET IMPLEMENTED]

3. **Footnote type classification.** Code separates footnotes but does not classify them (tahqiq_editor/author_original/variant_reading/hadith_takhrij/etc.). [NOT YET IMPLEMENTED]

4. **Non-Shamela normalizers.** No PDF, image, EPUB, plain text, or owner-authored normalizers exist. [NOT YET IMPLEMENTED]

5. **OCR pipeline.** No OCR integration exists. SPEC requires Mistral OCR 3 + Qari-OCR with dual-OCR comparison. [NOT YET IMPLEMENTED]

6. **Per-page text fidelity.** Code has no fidelity scoring. SPEC requires per-content-unit fidelity assessment. [NOT YET IMPLEMENTED]

7. **Content flagging.** Code detects `has_verse` and `has_table` but not Quran/hadith citations, TOC pages, or index pages. [NOT YET IMPLEMENTED]

8. **Structural format auto-detection.** Code does not detect Q&A format, tabular khilaf, or dictionary structures. [NOT YET IMPLEMENTED]

9. **Enrichment write-back.** Code does not write corrections back to source metadata. [NOT YET IMPLEMENTED]

10. **Schema validation.** Code does not validate its own output against a schema. [NOT YET IMPLEMENTED]

**External tools and libraries:**
- **Docling** (IBM, Apache 2.0): PDF parsing backend for text-embedded PDFs. Layout analysis (DocLayNet) and table structure (TableFormer). Experimental Arabic support.
- **Mistral OCR 3** (Mistral AI, commercial API): Primary OCR for scanned PDFs and images. Strong Arabic support with layout preservation.
- **Qari-OCR** (open-source): Specialized Arabic OCR with best-in-class diacritics handling. CER 0.061 on diacritically-rich texts.
- **CAMeL Tools** (NYU Abu Dhabi, MIT): Arabic text normalization, morphological analysis for OCR post-processing.
- **BeautifulSoup / lxml**: HTML parsing for Shamela normalizer (existing dependency).

---

## 10. Test Requirements

**What MUST be tested:**

1. **Shamela normalizer output schema compliance.** Given a known Shamela export, the normalizer produces a valid normalized package (manifest validates against manifest schema, every content unit validates against content unit schema). Test with single-volume and multi-volume sources.

2. **Content preservation fidelity.** The normalized `primary_text` for each page must contain exactly the text content from the source page, with HTML markup removed and whitespace normalized, but NO text content lost or added. Verify against gold baseline sources.

3. **Footnote separation correctness.** Footnotes are correctly separated from main text. No footnote content appears in `primary_text`. No main text content appears in footnotes. Footnote reference markers are correctly replaced with universal markers. Test all footnote formats: numbered_parens, bare_number, unnumbered.

4. **Multi-layer detection accuracy.** For known multi-layer sources (sharh on matn), verify that layer boundaries are detected. Layer 1 text is attributed to the matn author. Layer 2 text is attributed to the sharh author. Gold baselines needed for multi-layer detection testing.

5. **Structure discovery regression.** After any change to structure discovery rules, re-run on gold baseline sources and verify that discovered divisions match expected output. The existing 292 tests cover ABD-era structure discovery; these must be preserved and extended for KR.

6. **Diacritics preservation.** Verify that diacritically-rich text (from vocalized scholarly sources) is preserved exactly through normalization. Test: provide a page with known diacritics → verify character-by-character match in output. No diacritic may be lost, modified, or added.

7. **Page boundary accuracy.** Verify that `unit_index` values are monotonically increasing, that `physical_page` fields match source page numbers, and that no pages are skipped or duplicated.

8. **Content flag correctness.** Verify that `has_verse` is true for known verse pages, `has_table` for known table pages, `has_quran_citation` for pages with Quran citations, etc.

9. **Error handling.** Test every error code: provide unsupported format → `NORM_UNKNOWN_SOURCE_FORMAT`. Provide empty source → `NORM_MISSING_FROZEN`. Etc.

10. **OCR quality (when implemented).** For scanned sources: compare OCR output against manually transcribed gold baselines. Measure CER and WER per page. Verify that dual-OCR comparison produces higher-confidence output than single-OCR.

**Gold baseline requirements:**
- One Shamela single-volume source with manually verified normalization output (content, footnotes, structure).
- One Shamela multi-volume source with manually verified structure discovery.
- One Shamela commentary source (sharh on matn) with manually verified layer detection.
- One scanned PDF with manually transcribed text (for OCR testing, when implemented).
- One vocalized text (with diacritics) with character-level verification of diacritics preservation.

**Regression testing strategy:** After any change to normalization rules, footnote parsing, structure discovery, or layer detection, re-run normalization on all gold baseline sources and verify output matches expected results. After any normalizer upgrade, compare output against the previous version's output for the same source — differences must be reviewed and approved.

**Integration test requirements:**
- Normalization engine → passaging engine: verify that the passaging engine can read and process the normalized package correctly. The division tree is usable for passage boundary guidance. Content units are correctly ordered and referenced.
- Source engine → normalization engine: verify that the normalization engine correctly reads frozen files and source metadata produced by the source engine. source_id references resolve correctly.
- Enrichment write-back: verify that normalizer-discovered metadata (format override, volume corrections) is correctly written back to the source metadata record.
