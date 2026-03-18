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
- `structural_format`: the source engine's initial classification. Valid values: `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`. The normalization engine may override this if content analysis reveals a different format.
- `is_multi_layer`: boolean indicating whether this source contains text from 2 or more authors (e.g., a sharh contains both the matn author's and commentator's text). When true, the `text_layers` field specifies which layers are present and who authored each.
- `genre`: affects normalization strategy (a `nazm` triggers verse-aware processing; a `mu'jam` triggers dictionary-entry-aware processing).
- `page_count`: the source engine's page count estimate. Used by §5 check 2 (coverage validation) to verify content unit count matches expected pages.
- `volume_count` and volume metadata: for multi-volume sources.

The normalization engine does NOT read: scholarly_context, trust_tier, genre_chain, or other metadata fields that are irrelevant to format transformation. These fields pass through untouched in the normalized package via the source_id reference.

**Validation on input.** The normalization engine validates before processing:
1. The frozen directory exists and contains at least one file.
2. The source metadata record exists and contains the required fields listed above.
3. The `source_format` is one of the recognized values.
4. For multi-volume sources: the volume files are present as described in the metadata.

If validation fails, the source is rejected with a specific error code: missing frozen directory → `NORM_MISSING_FROZEN`, missing/invalid metadata → `NORM_MISSING_METADATA`, unrecognized source format → `NORM_UNKNOWN_SOURCE_FORMAT`, missing volume files → `NORM_MISSING_FROZEN` (see §7 for full error table). The processing status is set to `error`. The normalization engine never proceeds with a source that fails input validation — partial normalization is worse than no normalization because downstream engines would process corrupt data.

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
   - `structural_format_proposed`: string or null. When §4.B.2 auto-detection disagrees with the source engine's classification, this field contains the normalizer's proposed format. Null when there is no disagreement. The `structural_format` field retains the source engine's consensus-validated classification until a human gate resolves the disagreement. [AUDIT FIX M-31 completion]
   - `text_fidelity_summary`: aggregate text fidelity metrics for the entire source (mean OCR confidence if applicable, character-level fidelity estimate, pages with warnings).
   - `verse_detection`: whether versified text was found, and if so, the detected verse numbering scheme.
   - `total_content_units`: the number of content unit records in the accompanying JSONL.
   - `quality_report`: a structured summary of normalization quality containing: `division_count_by_tier` (object mapping tier names to counts), `layer_transition_count` (int), `pages_with_warnings` (int), `high_fidelity_pct` (float, 0.0–1.0), `unclassified_footnote_count` (int), `overall_confidence` (one of: `high`, `medium`, `low`, `minimal`).
   - `normalization_warnings`: array of engine-level warnings (not per-page warnings, which are on the content units).
   - `layer_fingerprints`: object or null. For multi-layer sources, per-layer stylometric fingerprints used for layer attribution validation (see §4.B.9). Contains one entry per detected layer with sentence length distribution, vocabulary richness, connective frequency, and other quantitative writing characteristics. Null for single-layer sources.
   - `discourse_flow_summary`: object. Aggregate discourse flow statistics across all content units (see §4.B.10): `dominant_discourse_type` for the source as a whole, `argument_cycle_count` (total complete argument cycles detected), `evidence_type_distribution` (object mapping evidence types to their frequency), `discourse_segment_distribution` (object mapping segment types to page counts).

2. **Content stream** (`content.jsonl`): a JSONL file with one record per content unit. A content unit corresponds to one physical page of the source. Each record conforms to the content unit schema:

   - `schema_version`: string.
   - `source_id`: string.
   - `unit_index`: zero-based sequential integer, globally unique within this source. THE authoritative positional identifier.
   - `physical_page`: object with `volume` (int or null), `page_number_display` (string or null, Arabic-numeral form for citations), `page_number_int` (int or null).
   - `primary_text`: string. The main text content of this page, cleaned of all format-specific markup. All diacritics preserved exactly.
   - `text_layers`: array. For multi-layer sources, segments attributed to specific layers. Each segment: `layer_type` (matn/sharh/hashiyah/tahqiq_note/uncertain), `author_canonical_id`, `start` and `end` character offsets in `primary_text`, `confidence` (0.0–1.0). For single-layer sources, one segment covering the entire text.
   - `footnotes`: array of objects. Each: `ref_marker` (string), `text` (string), `footnote_type` (one of: `tahqiq_editor`, `author_original`, `unknown_footnote_type` for coarse classification; or refined by §4.B.4 to: `variant_reading`, `hadith_takhrij`, `cross_reference`, `biographical_note`, `linguistic_note`, `correction_note`, `general_commentary`), `confidence` (0.0–1.0). When §4.B.4 classification succeeds, the footnote also carries type-specific structured data (variant_data, takhrij_data, bio_data, or correction_data).
   - `structural_markers`: object. If a heading is detected on this page: `heading_detected` (bool), `heading_text` (string), `heading_level` (int), `heading_detection_method` (html_tagged/layout_detected/keyword_heuristic/llm_discovered/toc_inferred/human_override), `heading_confidence` (confirmed/high/medium/low).
   - `verse_info`: object or null. If verse is detected: `verse_lines` (array of verse line objects with hemistich markers and verse numbers if available).
   - `content_flags`: object. Boolean flags: `has_verse`, `has_table`, `has_quran_citation`, `has_hadith_citation`, `is_toc_page`, `is_index_page`, `is_blank`.
   - `text_fidelity`: object. `score` (high/medium/low/very_low), `ocr_confidence` (float or null), `warnings` (array of strings).
   - `boundary_continuity`: object or null. Present on all content units except the last. Classifies the boundary between this unit and the next: `type` (mid_sentence/mid_paragraph/mid_argument/section_break/division_break/unknown), `confidence` (0.0–1.0), `detection_method`, `continuation_hint` (string or null). See §4.B.8.
   - `discourse_flow`: object or null. Scholarly discourse segment annotation for this content unit: `segments` (array of labeled discourse segments with character offsets and confidence), `dominant_discourse_type` (argumentative/definitional/evidential/narrative/enumerative/insufficient_text), `argument_cycle_complete` (bool), `argument_cycle_started_at_segment` (int or null), `cycle_missing_elements` (array of strings). See §4.B.10. Null for pages with <100 characters of text.

**Guarantees about the normalized package:**

- **Source-agnostic.** The content stream schema is identical regardless of which normalizer produced it. No field name, enum value, or structural convention depends on the source type. A Shamela normalizer and a PDF normalizer produce records with the same schema.
- **Ordering.** Content units are ordered by document order (volume ascending, then page ascending within volume). The `unit_index` field is zero-based and monotonically increasing.
- **Completeness.** Every physical page in the source that contains extractable text produces a content unit. Pages that are blank, TOC-only, or image-only with no OCR still produce a content unit with the corresponding `content_flags` set (`is_blank`, `is_toc_page`, or empty `primary_text` with `text_fidelity.score: "very_low"`).
- **Text fidelity.** Every content unit carries its own fidelity assessment. Downstream engines can filter or flag based on per-page fidelity, not just source-level.
- **Layer annotation coverage.** For multi-layer sources, every character in `primary_text` is covered by exactly one segment in `text_layers`. No character is unattributed. If the normalizer cannot determine the layer for a region, it assigns `layer_type: "uncertain"` with confidence ≤ 0.30.
- **Diacritics.** The `primary_text` field preserves all diacritical marks exactly as they appear in the source. No Unicode normalization of tashkeel is applied.
- **Footnote separation.** Footnotes are cleanly separated from primary text. Footnote reference markers in the primary text are replaced with inline markers in a universal format (`⌜1⌝` — using Unicode half-brackets, not format-specific conventions).
- **Division tree consistency.** Every heading detected in the content stream has a corresponding node in the manifest's division tree. The tree's page ranges are consistent with the content stream's unit_index values.

**Metadata pass-through (D-023).** The normalized package carries the `source_id` as its primary link to upstream metadata. Phase 2 engines access the full source metadata record via this reference. The normalization engine does NOT duplicate source metadata into the normalized package — it references it. This prevents metadata staleness: if the source engine enriches the metadata after normalization, Phase 2 engines see the enriched version automatically.

The normalization engine ADDS the following metadata that did not exist before normalization:
- Division tree (structural hierarchy)
- Per-page text fidelity scores
- Layer annotations with character-level segments
- Footnote type classification (author-original vs. tahqiq-editor, and fine-grained types per §4.B.4)
- Structural format classification (may refine source engine's initial guess)
- Verse detection and numbering
- Content flags (TOC, index, blank, Quran/hadith citations)
- Content census (statistical profile of source characteristics, §4.B.5)
- Tahqiq apparatus topology (manuscript witness network, §4.B.7)
- Cross-page boundary continuity signals (§4.B.8)
- Layer fingerprints for multi-layer validation (§4.B.9)
- Scholarly discourse flow annotations (§4.B.10)

**Source registry update.** Upon successful normalization, the source's processing status is updated from `acquired` to `normalized`. The normalized package path is recorded in the source registry.
The registry update occurs ONLY after all §5 Layer 1 validation checks (1–6) pass and the normalized package is fully verified on disk. If any validation check fails, the status remains `acquired` and no partial package is visible to downstream engines.

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

The normalization engine follows a dispatcher-normalizer pattern. A central dispatcher reads the `source_format` from the source metadata, selects the matching normalizer module from the type map (§4.A.1 table), and invokes it. Each normalizer encapsulates ALL format-specific logic for one source type. The dispatcher knows nothing about any format.

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

**Pass 2 — Content/footnote separation.** Within each page, split at any `<hr>` tag whose `width` attribute has a numeric value between 80 and 100 (inclusive). The match is case-insensitive, tolerates single/double/no quotes, and permits additional attributes (e.g., `align='right'`). Regex: `<hr\s+[^>]*width\s*=\s*['"]?(\d{2,3})['"]?[^>]*>` where captured group is 80-100. Self-closing variants (`/>`) are also matched. [AUDIT FIX M-30] This separates primary text from footnotes. If the separator is absent on a page, the entire page content is treated as primary text with no footnotes; the normalizer logs `NORM_FOOTNOTE_SEPARATOR_ABSENT` (info) for that page. If >30% of pages in the source lack the separator, the source-level flag `no_footnote_apparatus` is set in the quality report — this distinguishes "source has no footnotes" from "separator detection failed." Parse footnotes into individual entries using the `(N)` marker pattern. Classify footnote sections as `numbered_parens`, `bare_number`, `unnumbered`, or `none`. Capture footnote preamble text. Strip footnote reference markers from primary text only when a matching footnote exists on the same page. This pass follows ABD rules §4.5–§4.6, upgraded to classify footnote type:
- If the footnote contains tahqiq markers (hadith grading, manuscript variant notation like "في نسخة:", bibliographic references to collections), classify as `tahqiq_editor`.
- If the footnote appears to be the author's own note (matches the main text's writing style, no tahqiq markers), classify as `author_original`.
- If uncertain, classify as `unknown_footnote_type` with a confidence score.

**Pass 3 — HTML stripping and text cleaning.** Remove all HTML tags (preserving text content). Decode HTML entities. HTML parsing uses BeautifulSoup with the `lxml` backend. The `lxml` backend is chosen for: (1) conservative entity resolution that does not aggressively resolve unterminated entities, (2) fast parsing speed for batch processing, (3) sufficient leniency for machine-generated Shamela HTML. If `lxml` parsing fails (malformed HTML beyond lxml tolerance), fall back to `html5lib` backend with `resolve_entities=True`. Post-parse validation: compare diacritic positions between raw HTML text nodes and parsed output. If any diacritic at a known position is absent or substituted, raise `NORM_DIACRITICS_ENTITY_CORRUPTION` (Fatal, affects T-1). [AUDIT FIX M-22] Normalize line endings and whitespace per ABD rules §4.7–§4.9. Preserve asterisks, ZWNJ characters, and all other source data markers. Preserve all diacritics exactly.

**Pass 4 — Structure discovery.** This is a major expansion from ABD. The existing `discover_structure.py` (2896 lines) implements a 4-tier confidence architecture for heading detection. The KR upgrade integrates structure discovery into the normalizer's pipeline:

- **Tier 1 (HTML-tagged headings):** Extract `<span class="title">` elements from the frozen HTML (not from cleaned text — tags are needed). These are confirmed headings.
- **Tier 1.5 (TOC parsing):** If a TOC page is detected, parse it for cross-referencing against discovered headings.
- **Tier 2 (Keyword heuristics):** Scan cleaned text for structural keywords (باب, فصل, مبحث, فائدة, تنبيه, قاعدة, خاتمة, مقدمة) at line beginnings, using patterns from `structural_patterns.yaml`. Apply ordinal detection for sequential headings. ZWNJ heading detection (double ZWNJ at line start) provides a high-confidence signal validated across 9.5% of the Shamela corpus.
- **Tier 3 (LLM semantic judgment):** For headings that Tier 2 detects with confidence below `medium`, or for sources where Tiers 1 and 2 find fewer than `structure_llm_threshold` (default 3) headings in a source of ≥`structure_min_pages_for_llm` (default 50) pages, invoke an LLM to examine candidate boundaries. The LLM receives the source's known genre, the headings found so far, and a window of text around candidate boundaries. LLM-discovered headings carry confidence `medium` if the LLM states high certainty, `low` otherwise.

The output is a division tree stored in the manifest's `division_tree` field, and each content unit records detected headings in `structural_markers`.

**Pass 5 — Multi-layer detection.** For sources where `is_multi_layer` is true in the source metadata (or where the normalizer detects layer signals even when the source engine didn't flag it), identify which portions of each page's text belong to which layer.

Shamela-specific layer signals:
- **Bold text** (detected from `<b>` tags in HTML before stripping in Pass 1): In approximately 75% of Shamela commentary exports, matn text is bold. The normalizer records bold spans and their character offsets during Pass 1.
- **Bracket markers:** Matn text enclosed in brackets: `[ المبتدأ هو الاسم المرفوع ]`.
- **Transition phrases:** "قال المصنف" (the author said), "قوله" (his saying), "قال الشارح" (the commentator said). Detected by pattern matching.
- **Font size differences:** A minority of Shamela exports use `<font size>` tags for layer distinction. Detected before stripping.

For each page, the normalizer produces a `text_layers` array segmenting primary text into attributed regions with layer types, author canonical_ids, character offsets, and confidence scores.

**Pass 6 — Output generation and §4.B enrichment.** After Passes 1-5 produce the raw content units, Pass 6 enriches them with §4.B capabilities and assembles the final output. The §4.B capabilities execute in dependency order:

1. **Content flagging** (§4.A.9): compute `content_flags` for each content unit.
2. **Structural format auto-detection** (§4.B.2): analyze first 20 units to classify format.
3. **Footnote apparatus classification** (§4.B.4): classify footnote types.
4. **Content census** (§4.B.5): aggregate statistics from all content units (needs content_flags from step 1).
5. **Tahqiq apparatus topology** (§4.B.7): extract manuscript witness network from classified footnotes (needs §4.B.4 from step 3).
6. **Authorial voice fingerprint** (§4.B.9): build per-layer fingerprints and validate attributions (needs census `verse_ratio` from step 4 for verse-aware fingerprinting).
7. **Cross-page continuity** (§4.B.8): classify every page boundary.
8. **Scholarly discourse flow** (§4.B.10): annotate discourse segments per content unit (needs continuity from step 7 for cross-page argument cycle detection).
9. **Cross-validation:** if a content unit has `boundary_continuity.type: "mid_argument"` but the same unit's `discourse_flow.argument_cycle_complete: true`, the continuity signal takes precedence — the discourse flow's `argument_cycle_complete` is set to `false` and `cycle_missing_elements` is populated with the expected continuation. This prevents contradictory signals reaching the passaging engine. Conversely, if `discourse_flow.argument_cycle_complete: false` (cycle incomplete with missing elements) but `boundary_continuity.type` is `section_break` or `division_break`, the continuity signal takes precedence — the discourse flow's `cycle_missing_elements` is preserved as-is (it is genuine information about what the author omitted or what was lost at a structural boundary), but the content unit is annotated with `discourse_flow.cycle_truncated_by_structure: true` to distinguish a structurally interrupted cycle from one that continues on the next page.
10. **Fine-grained fidelity mapping** (§4.B.3): for OCR sources only, compute character-level fidelity maps.
11. **Scholarly text layer intelligence** (§4.B.1): for sources with multi-layer signals missed by Pass 5.

After all enrichments, assemble the manifest (including `content_census`, `tahqiq_topology`, `layer_fingerprints`, `discourse_flow_summary`) and content JSONL. Run all §5 Layer 1 validation checks (schema compliance, coverage, text extraction, layer consistency, division tree validity, unit_index integrity, continuity/discourse/fingerprint consistency) on the assembled output. Only after all checks pass, write the package to disk.

**Atomic write procedure.** The normalizer writes to a temporary directory (`library/sources/{source_id}/normalized_tmp_{timestamp}/`) first. Both `manifest.json` and `content.jsonl` are written and flushed to disk in the temporary directory. After both files are verified (existence, non-zero size, valid JSON/JSONL parse), the normalizer atomically renames the temporary directory to the final path (`library/sources/{source_id}/normalized/`). If a previous `normalized/` directory exists (reprocessing), it is renamed to `normalized_prev_{timestamp}/` before the swap, then deleted only after the new package passes verification. If any step fails (write error, verification failure, rename failure), the temporary directory is removed and normalization fails with `NORM_WRITE_FAILED`. This guarantees that `normalized/` either contains a complete, validated package or does not exist — no partial state is possible.

**Interrupted write recovery.** At normalizer startup (before processing any source), check for orphaned state: if a `normalized_tmp_*` directory exists but no `normalized/` directory, AND one or more `normalized_prev_*` directories exist, then a previous write was interrupted mid-swap. If multiple `normalized_prev_*` directories exist, select the one with the LATEST timestamp (most recent backup is closest to the interrupted state). [AUDIT FIX M-32] Clean up older `normalized_prev_*` directories before creating new ones during the atomic write procedure. Recovery: (a) attempt to validate the temp directory (JSON parse, schema check on both files), (b) if valid, complete the interrupted rename (temp → `normalized/`, delete all `normalized_prev_*`), (c) if invalid, restore from the latest `normalized_prev_*` (rename to `normalized/`) and delete all temp and remaining prev directories. Log the recovery action as `NORM_WRITE_RECOVERY` (info).

Any §5 check failure aborts the write — the assert prevents corrupt packages from reaching disk. Compute the quality report as the final manifest field.

**Verse detection.** ABD rules §4.8 detect verse markers (asterisks, hemistich separators). KR extends this: for `nazm` sources, verse-aware processing identifies each بيت, normalizes hemistich separators, and captures verse numbers as metadata. Verse numbers are critical scholarly references (e.g., "ألفية line 75").

**Concrete example (Shamela normalizer, single page from sharh ibn 'aqil):**

Input HTML (from frozen Shamela export):
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 45)</span>
<span class='PageHead'>باب المبتدأ والخبر</span>
<b>المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية</b>
<br>أي المبتدأ في اصطلاح النحويين هو الاسم المجرد عن العوامل اللفظية مرفوعا. وقوله المرفوع يخرج المنصوب والمجرور.
(1) قال ابن مالك رحمه الله في التسهيل ما يدل على هذا.
<hr width='95'>
(1) انظر: التسهيل ص ٤٥. والحديث أخرجه البخاري (٢٣٤٥) وصححه الألباني.
</div>
```

Output content unit (content.jsonl record):
```json
{
  "schema_version": "normalized_package_v2.0",
  "source_id": "nahw_ibnaqil_sharh_alfiyyah_a1b2",
  "unit_index": 44,
  "physical_page": {"volume": 1, "page_number_display": "٤٥", "page_number_int": 45},
  "primary_text": "المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية\nأي المبتدأ في اصطلاح النحويين هو الاسم المجرد عن العوامل اللفظية مرفوعا. وقوله المرفوع يخرج المنصوب والمجرور.\n⌜1⌝ قال ابن مالك رحمه الله في التسهيل ما يدل على هذا.",
  "text_layers": [
    {"layer_type": "matn", "author_canonical_id": "ibn_malik_672", "start": 0, "end": 51, "confidence": 0.92},
    {"layer_type": "sharh", "author_canonical_id": "ibn_aqil_769", "start": 52, "end": 217, "confidence": 0.88}
  ],
  "footnotes": [
    {"ref_marker": "1", "text": "انظر: التسهيل ص ٤٥. والحديث أخرجه البخاري (٢٣٤٥) وصححه الألباني.", "footnote_type": "cross_reference", "confidence": 0.85,
     "secondary_types": [{"type": "hadith_takhrij", "char_range": [22, 70]}],
     "takhrij_data": {"collections": [{"name": "البخاري", "number": "2345"}], "grading": {"grader": "الألباني", "grade": "صحيح"}}}
  ],
  "structural_markers": {"heading_detected": true, "heading_text": "باب المبتدأ والخبر", "heading_level": 2, "heading_detection_method": "html_tagged", "heading_confidence": "confirmed"},
  "verse_info": null,
  "content_flags": {"has_verse": false, "has_table": false, "has_quran_citation": false, "has_hadith_citation": true, "is_toc_page": false, "is_index_page": false, "is_blank": false},
  "text_fidelity": {"score": "high", "ocr_confidence": null, "warnings": []}
}
```

#### §4.A.3 — PDF Normalizer (Text-Embedded)

For PDFs with embedded text (digital-native PDFs, PDFs with a usable text layer), the text PDF normalizer extracts content without OCR.

**Technical approach:** PDF parsing uses a two-path strategy [AUDIT FIX M-21]:
- **Path A (text-layer PDFs):** Extract text using PyMuPDF (fitz) with python-bidi post-processing for RTL reordering. Validate extracted text using Arabic character ratio (§5 check 3). If ratio <0.70 for a source classified as Arabic, fall back to Path B.
- **Path B (scanned PDFs or failed Path A):** Route page images to OCR pipeline (§4.A.4).
- **Docling** may be used for structural analysis (layout detection, table extraction, reading order) but NOT for primary text extraction from Arabic PDFs due to known RTL text reversal issues (docling-project/docling#1938, #2179). Docling's layout analysis model (DocLayNet) identifies document elements; Docling's table structure model (TableFormer) handles tables.

Error codes: `NORM_PDF_PARSE_FAILED` (Fatal) — PDF library returns error. `NORM_PDF_ARABIC_GARBLED` (Fatal) — Text extracted but Arabic character ratio <0.30 for Arabic-classified source, indicating text reversal/garbling.

**Processing pipeline:**

1. **PDF text extraction (Path A).** Extract text using PyMuPDF (fitz) with python-bidi post-processing for RTL reordering. Validate Arabic character ratio per §5 check 3. If ratio <0.70, fall back to OCR (Path B). For structural analysis (layout detection, table extraction), Docling may be used separately. [AUDIT FIX M-21]
2. **Text extraction.** Extract text content per page in reading order. PyMuPDF extracts raw text; python-bidi reorders RTL runs. Preserve paragraph boundaries detected by whitespace analysis or Docling structural analysis.
3. **Footnote detection.** Elements classified as footnotes or marginalia by Docling are separated from main text. The normalizer applies footnote type classification (tahqiq_editor vs. author_original) using the pattern-matching rules defined in §4.B.4 (tahqiq markers, hadith grading phrases, variant notation patterns), with LLM fallback for footnotes that match no pattern.
4. **Structure discovery.** Docling detects headers and section structure from PDF formatting. The normalizer maps Docling's elements to the KR division tree format, augmented with Arabic keyword heuristic detection for structural keywords Docling may not recognize.
5. **Page boundary capture.** PDF pages map directly to physical pages. Page numbers extracted from Docling's detected elements or from the PDF page index.
6. **Multi-layer detection.** For commentary PDFs, layers are detected via font analysis: different layers often use different font sizes or weights. Docling's layout analysis provides font metadata. Supplemented with transition phrase detection.
7. **Diacritics.** Text extracted from text-layer PDFs preserves diacritics as encoded. No normalization applied.
8. **Output.** Standard normalized package.

**Text fidelity:** Text-embedded PDFs default to `high`. If Docling reports extraction issues, fidelity is downgraded per page.

**Concrete example (text-embedded PDF normalizer, single page from a tahqiq edition of زاد المستقنع):**

Input: A digital-native PDF page. Docling's layout analysis detects: one main text block (RTL), two footnotes at bottom, one header (`باب صفة الصلاة`), page number `١٢٣` in footer.

Docling extracted text (main block, in reading order):
```
باب صفة الصلاة
يسن أن يقرأ بعد الفاتحة سورة. ويجهر الإمام في صلاة الفجر والجمعة والعيدين وأولتي المغرب والعشاء (1). ويسر فيما سوى ذلك (2).
```

Docling extracted footnotes (from bottom of page):
```
(1) لحديث أبي قتادة في الصحيحين أن النبي ﷺ كان يجهر في الركعتين الأوليين. والجهر هنا سنة عند الجمهور.
(2) انظر: المغني ٢/١٤٥.
```

Output content unit:
```json
{
  "schema_version": "normalized_package_v2.0",
  "source_id": "src_b4f1d82c",
  "unit_index": 122,
  "physical_page": {"volume": 1, "page_number_display": "١٢٣", "page_number_int": 123},
  "primary_text": "باب صفة الصلاة\nيسن أن يقرأ بعد الفاتحة سورة. ويجهر الإمام في صلاة الفجر والجمعة والعيدين وأولتي المغرب والعشاء ⌜1⌝. ويسر فيما سوى ذلك ⌜2⌝.",
  "text_layers": [
    {"layer_type": "matn", "author_canonical_id": "hajjawi_968", "start": 0, "end": 152, "confidence": 1.0}
  ],
  "footnotes": [
    {"ref_marker": "1", "text": "لحديث أبي قتادة في الصحيحين أن النبي ﷺ كان يجهر في الركعتين الأوليين. والجهر هنا سنة عند الجمهور.", "footnote_type": "hadith_takhrij", "confidence": 0.93,
     "takhrij_data": {"collections": [{"name": "البخاري"}, {"name": "مسلم"}], "grading": null}},
    {"ref_marker": "2", "text": "انظر: المغني ٢/١٤٥.", "footnote_type": "cross_reference", "confidence": 0.96}
  ],
  "structural_markers": {"heading_detected": true, "heading_text": "باب صفة الصلاة", "heading_level": 2, "heading_detection_method": "layout_detected", "heading_confidence": "confirmed"},
  "verse_info": null,
  "content_flags": {"has_verse": false, "has_table": false, "has_quran_citation": false, "has_hadith_citation": true, "is_toc_page": false, "is_index_page": false, "is_blank": false},
  "text_fidelity": {"score": "high", "ocr_confidence": null, "warnings": []}
}
```

Processing: Docling detected the header element as a section heading → mapped to `heading_level: 2` (باب). The heading text IS included in `primary_text` (it is part of the page content in PDFs, unlike Shamela's `PageHead` elements which are separate navigation metadata). The heading is ALSO recorded in `structural_markers` for structure discovery. Footnotes identified by Docling's layout analysis as bottom-of-page elements, matched to `(N)` markers in the main text. Footnote (1) matched "لحديث" + "الصحيحين" → `hadith_takhrij`. Footnote (2) matched "انظر:" → `cross_reference`. Single-layer source (matn only, no commentary), so one `text_layers` entry covering the full text.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on Docling installation and Arabic RTL configuration.

#### §4.A.4 — Scanned PDF and Image Normalizer

For scanned PDFs (pages are images with no usable text layer) and image-based sources (iPhone photos), the normalizer performs OCR.

**OCR strategy — tiered approach:**

1. **Primary: Mistral OCR 3** (`mistral-ocr-latest`). Commercial API with best multilingual document understanding. Processes PDF pages or images, returns Markdown with layout preservation. Strong Arabic support. Cost: $1–2 per 1000 pages.

2. **Specialized: Qari-OCR** (open-source, Arabic-specific). For pages where Mistral OCR's output has low confidence on diacritically-heavy text, the normalizer falls back to Qari-OCR v0.2, fine-tuned specifically for Arabic tashkeel. CER 0.061 on diacritically-rich texts. Runs locally on GPU.

3. **Validation: dual-OCR comparison.** For sources with `text_fidelity: "low"` (iPhone photos) or critical scholarly texts, run BOTH Mistral OCR and Qari-OCR on the same page and compare. Agreement increases confidence; disagreement triggers character-level alignment to produce merged output with per-character confidence. High-disagreement pages are flagged for human review.

**Processing pipeline:**

1. **Page rendering.** For PDFs: render each page at 300+ DPI (600 DPI for scholarly texts with small print). For images: use as-is with pre-processing.
2. **Pre-processing (images).** Auto-detect page orientation using a two-stage approach [AUDIT FIX M-26]:
   1. **Stage 1 (OSD):** Use Tesseract OSD mode to detect script and rotation angle. For 90/270-degree rotations, apply correction directly. For 0/180-degree ambiguity (common with Arabic RTL), proceed to Stage 2.
   2. **Stage 2 (page-level validation):** Check for page numbers (should increase sequentially), running headers (should be at page top), and paragraph indent direction (Arabic paragraphs indent right). If signals are contradictory, flag  (Warning) and process with both orientations, comparing OCR confidence scores. Use the higher-confidence result.
   NOTE: VLM-based OCR engines (§4.B.6 selection matrix: QARI-OCR, Baseer, Mistral OCR) handle orientation implicitly and do not require pre-rotation.
   Perspective correction for angled photos. Brightness/contrast adjustment. For scanned PDFs: skew correction, noise reduction.
3. **OCR execution.** Send to Mistral OCR 3 via API. Parse returned Markdown to extract main text, footnotes (from layout position), headers/footers, page numbers.
4. **Arabic-specific post-processing.**
   - **ب/ت/ث/ن disambiguation:** These letters differ only in dots — the most common OCR confusion. Flag potential confusions using CAMeL Tools morphological analysis (CamelMorph MSA database). NOTE: CAMeL Tools's MSA database has incomplete coverage of classical Arabic vocabulary (documented in Minaei-Bidgoli et al., 2026). Terms not found in the lexicon receive `analysis_status: "unknown"` — they are NOT flagged as OCR errors. Only terms that are morphologically impossible (no valid Arabic root pattern) are flagged as potential OCR confusions. Do NOT auto-correct — flag for downstream review. [AUDIT FIX M-16]
   - **Semantic confusion hazard:** OCR errors can produce valid Arabic words with different meanings (e.g., حَرَّمَ "he prohibited" → حَرَمَ "he deprived"; عِلْم "knowledge" → عَلَم "flag"). Morphological validation cannot catch these because both readings are valid. The normalizer flags words where: (a) the OCR confidence for any character is below 0.90, AND (b) substituting a visually similar letter (from the Arabic visual-similarity matrix: ب↔ت↔ث↔ن, ح↔خ↔ج, ر↔ز, د↔ذ, ص↔ض, ط↔ظ, ع↔غ, س↔ش) produces a different valid Arabic word. These are recorded in the fidelity map (§4.B.3) as `semantic_confusion_risk` entries with both possible readings. The downstream excerpting engine and synthesizer treat text containing `semantic_confusion_risk` flags as requiring human verification before use in knowledge claims.
   - **Hamza normalization check:** Flag pages with unusual hamza patterns.
   - **Diacritics validation:** Flag impossible diacritic sequences as likely OCR errors.
5. **Structure discovery.** Less reliable for OCR text. Uses layout-based detection from Mistral OCR's Markdown formatting, keyword heuristics, and LLM assistance. Confidence levels are typically lower than for structured text.
6. **Multi-layer detection.** Based on visual font size differences from OCR spatial output. Less reliable than HTML-based detection. Confidence typically `medium` or `low`.
7. **Page boundaries.** Scanned PDFs: one page per PDF page. Images: one page per image file. Ordering precedence for image sets: (1) filename numeric sort is the default and authoritative ordering. (2) If OCR detects page numbers on ≥80% of images, the OCR-detected page numbers are compared against filename order. If they agree, confidence is high. If they disagree, filename order is used as authoritative, a `NORM_PAGE_ORDER_CONFLICT` warning is logged with both orderings, and a human gate is triggered to let the owner choose the correct order. Filename sort is preferred because it reflects the owner's capture sequence, which is more reliable than OCR page number detection on potentially degraded images.
8. **Text fidelity.** Per-page based on OCR confidence, dual-OCR agreement, and character-level statistics. Levels: `high` (>0.95 confidence), `medium` (0.80–0.95), `low` (0.60–0.80), `very_low` (<0.60, flag for human review).

**iPhone photo-specific handling:** Variable lighting → adaptive thresholding. Perspective distortion → edge detection and correction. Partial pages → detected and flagged as `partial_page`. Finger obstruction → cannot recover; flag occluded regions. Sequential ordering → by filename numeric sort (authoritative), cross-referenced with OCR-detected page numbers when available (see page boundary rule above).

**Concrete example (iPhone photo OCR of a page from الورقات للجويني):**

Input: iPhone photo `IMG_0042.jpg`. Pre-processing detects slight clockwise rotation (2.3°) and applies correction. Brightness is adequate (no adjustment needed).

Mistral OCR 3 output (Markdown):
```
# فصل في الأوامر والنواهي
الأمر استدعاء الفعل بالقول ممن هو دونه على سبيل الوجوب.
والأمر المطلق لا يقتضي التكرار(1) ولا يقتضي الفور على الصحيح.

---
(1) وقال بعضهم: يقتضي التكرار. والأول أصح.
```

Arabic-specific post-processing:
- No ب/ت/ث/ن confusions detected (clean OCR output).
- Diacritics: none present in source (unvocalized text) → no diacritics validation needed.
- Morphological check: all words are valid Arabic morphemes.

Output content unit:
```json
{
  "schema_version": "normalized_package_v2.0",
  "source_id": "src_f3e91a7c",
  "unit_index": 41,
  "physical_page": {"volume": null, "page_number_display": null, "page_number_int": null},
  "primary_text": "فصل في الأوامر والنواهي\nالأمر استدعاء الفعل بالقول ممن هو دونه على سبيل الوجوب.\nوالأمر المطلق لا يقتضي التكرار⌜1⌝ ولا يقتضي الفور على الصحيح.",
  "text_layers": [
    {"layer_type": "matn", "author_canonical_id": "juwayni_478", "start": 0, "end": 157, "confidence": 1.0}
  ],
  "footnotes": [
    {"ref_marker": "1", "text": "وقال بعضهم: يقتضي التكرار. والأول أصح.", "footnote_type": "general_commentary", "confidence": 0.78}
  ],
  "structural_markers": {"heading_detected": true, "heading_text": "فصل في الأوامر والنواهي", "heading_level": 3, "heading_detection_method": "keyword_heuristic", "heading_confidence": "high"},
  "verse_info": null,
  "content_flags": {"has_verse": false, "has_table": false, "has_quran_citation": false, "has_hadith_citation": false, "is_toc_page": false, "is_index_page": false, "is_blank": false},
  "text_fidelity": {"score": "medium", "ocr_confidence": 0.89, "warnings": ["single_ocr_only"]}
}
```

Processing: Heading "فصل في الأوامر والنواهي" detected from Mistral OCR's Markdown `#` heading + keyword heuristic (فصل). No physical page numbers available (iPhone photos lack page metadata) — `physical_page` fields are null; `unit_index: 41` is the authoritative positional identifier (this is the 42nd photo in filename order). Footnote detected from `(1)` marker + `---` separator in OCR output. Single-layer source (matn only). Text fidelity `medium` (0.89 OCR confidence, single-OCR mode — dual-OCR was not triggered because fidelity exceeds `low` threshold).

[NOT YET IMPLEMENTED] — Full specification provided. Depends on Mistral OCR API access, Qari-OCR local installation, image pre-processing library.

#### §4.A.4a — EPUB Normalizer (Behavioral Outline)

For EPUB format sources (.epub files). EPUB is structured XHTML with a spine (reading order) and navigation document.

**Technical approach:** Use Docling or ebooklib for EPUB parsing. EPUB's XHTML chapters provide natural structure. The spine defines reading order across chapter files.

**Key behavioral rules:**
- Each XHTML chapter file is processed in spine order. Content units are created at page-equivalent boundaries (approximately 2000 characters or at chapter boundaries, whichever is shorter).
- Physical page numbers: EPUBs typically lack physical page references. If the EPUB contains `<span epub:type="pagebreak">` elements (common in publisher EPUBs), these are used as page boundaries. Otherwise, `physical_page.page_number_int` and `physical_page.page_number_display` are null; only `unit_index` is meaningful.
- Structure discovery: EPUB's `<nav>` table of contents provides a pre-built division tree with Tier 1 (confirmed) confidence. Chapter `<h1>`–`<h6>` headings supplement.
- Footnotes: EPUB footnotes use `<aside epub:type="footnote">` or hyperlinked endnotes. Both are detected and separated.
- Multi-layer: Detected from CSS styling (different classes for matn vs. sharh) or explicit `epub:type` annotations if present.
- Text fidelity: Default `high` (digital text, no OCR).

**Example (brief):** Input: EPUB with 3 XHTML chapters and a `<nav>` TOC → Output: Content units at chapter boundaries with Tier 1 division tree from `<nav>`, `text_fidelity: "high"`, headings from `<h2>` elements with `heading_detection_method: "layout_detected"`.

[NOT YET IMPLEMENTED] — Behavioral outline only. Full specification to be written when EPUB sources enter the library.

#### §4.A.4b — Word Document Normalizer (Behavioral Outline)

For .doc and .docx files. Common for modern scholarly publications and owner-received documents.

**Technical approach:** Use Docling for Word document parsing. Docling extracts text, headings, tables, footnotes, and reading order from Word documents.

**Key behavioral rules:**
- Content units created at page breaks when present in the document, or at ~2000-character intervals when the document has no page breaks.
- Structure discovery: Word heading styles (Heading 1–6) provide Tier 1 structure. Arabic keyword heuristics supplement for unstyled headings.
- Footnotes: Word's native footnote/endnote system is parsed directly. Footnote text and reference markers are cleanly extractable.
- Multi-layer: Detected from text styling (different fonts or colors for matn vs. sharh) or from explicit section markers.
- Text fidelity: Default `high` (digital text).
- Track changes and comments: Ignored during normalization (the accepted text is the primary text). A warning is logged if tracked changes are detected: `NORM_TRACK_CHANGES_DETECTED` (info).

**Example (brief):** Input: .docx with Heading 1/2 styles and native footnotes → Output: Content units at page breaks, division tree from heading styles (Tier 1 `layout_detected`), footnotes parsed from Word's footnote system, `text_fidelity: "high"`.

[NOT YET IMPLEMENTED] — Behavioral outline only. Full specification to be written when Word document sources enter the library.

#### §4.A.4c — Plain Text Normalizer (Behavioral Outline)

For raw .txt files with minimal or no formatting. Common for manually digitized texts, copy-pasted content from websites, or text extracted by external tools.

**Key behavioral rules:**
- Content units created at paragraph boundaries or ~2000-character intervals (whichever produces units closer to the median size of 1500–2500 characters).
- Physical page numbers: null for all fields. `unit_index` is the sole positional identifier.
- Structure discovery relies entirely on Tier 2 (keyword heuristics) and Tier 3 (LLM). No HTML or formatting signals are available. Structure confidence is typically `low` or `minimal`.
- Footnotes: Detected by pattern matching only — `(N)` markers followed by matching text at the paragraph end or document end. If no footnote pattern is detected, all text is treated as primary text.
- Multi-layer: Cannot be detected from formatting. Relies on content-based inference only (§4.B.1 Scholarly Text Layer Intelligence). Confidence is low. If the source metadata specifies `is_multi_layer: true`, the normalizer attempts detection; otherwise, the source is treated as single-layer.
- Text fidelity: Default `high` (digital text, though content quality depends on the digitization source). If encoding errors are detected during conversion, fidelity is downgraded.

**Example (brief):** Input: 15KB .txt file with باب/فصل headings but no formatting → Output: ~8 content units at paragraph boundaries, division tree from keyword heuristics (Tier 2, confidence `medium`), `physical_page` fields null, `text_fidelity: "high"`.

[NOT YET IMPLEMENTED] — Behavioral outline only.

#### §4.A.4d — Owner Content Normalizer (Behavioral Outline)

For the owner's study notes, tarjih documents, research drafts, and lesson transcriptions. These are distinct from scholarly sources: they are the owner's OWN intellectual production, not texts being studied.

**Key behavioral rules:**
- Input type identifier (from manual input interface): `typed_passage`, `lesson_transcription`, `study_note`, `external_reference`. Each type affects normalization strategy.
- Content units: for short inputs (<2000 characters), one content unit. For longer inputs, split at paragraph boundaries.
- Physical page numbers: null. `unit_index` only.
- Structure discovery: minimal. The owner's notes may use informal headings; keyword heuristics are applied but with lower expectations. LLM structure detection is skipped unless the text exceeds 20 content units.
- Footnotes: the owner's own reference notes. Detected by standard patterns. Not classified into tahqiq categories (the owner is not a tahqiq editor).
- Multi-layer: always single-layer (the owner is the sole author). `text_layers` contains one entry with `layer_type: "owner_content"` and the owner's identifier.
- Text fidelity: `high` for `typed_passage` and `study_note`. `medium` for `lesson_transcription` (the owner may have transcription errors). `variable` for `external_reference` (depends on the external source quality).
- Content flagging: standard flags apply. The owner's notes may contain Quran/hadith citations worth flagging.
- Embedded scholarly quotation detection: the owner's notes frequently contain quotations from scholars (e.g., "قال ابن قدامة: يجوز المسح على الخفين"). The normalizer scans for explicit quotation patterns ("قال فلان:", scholar name followed by ":" or "أن" and content) and marks detected quotations in content_flags as `has_embedded_scholarly_quotation: true`. This flag tells the excerpting engine to trace the quotation to the referenced scholar rather than attributing the content to the owner.

**Example (brief):** Input: `typed_passage` of 800 characters (owner's study note on conditions of prayer) → Output: 1 content unit, `layer_type: "owner_content"`, `physical_page` null, structure discovery skipped (<20 units), `text_fidelity: "high"`, `has_hadith_citation: true` (owner cites a hadith).

[NOT YET IMPLEMENTED] — Behavioral outline only.

#### §4.A.5 — Multi-Layer Text Detection

Multi-layer text detection is the highest-integrity-risk operation in the normalization engine. If it fails, downstream engines attribute text to the wrong author — a scholarly integrity violation (see DOMAIN.md "The Multi-Layer Text Problem").

**The layer model.** A multi-layer source contains text from up to four layers:

| Layer | Type | Author | Typical markers |
|---|---|---|---|
| 1 | `matn` | Original author | Bold, brackets, explicit markers |
| 2 | `sharh` | Commentator | Main body text |
| 3 | `hashiyah` | Marginal annotator | Smaller text, marginal notes |
| 4 | `tahqiq_note` | Modern editor | Footnotes, variant readings |

Not all layers are present in every multi-layer source. The source metadata's `text_layers` field specifies which are present.

**Layer detection signals (by reliability):**

1. **Explicit transition markers** (confidence ≥ 0.90):
   - "قال المصنف:" → transition to Layer 1
   - "قال الشارح:" → transition to Layer 2 (in hashiyah context)
   - "قوله:" → typically introduces Layer 1 text within Layer 2
   - "أقول:" → confirms current layer's author speaking

2. **Typographic signals** (reliability varies by source type):
   - Shamela HTML: bold tags → Layer 1 (reliable in ~75% of commentary exports). However, bold is sometimes used for emphasis within sharh text (e.g., the commentator bolds a hadith or Quran quote). The normalizer distinguishes layer-indicating bold from emphasis-bold using two heuristics: (a) bold spans are classified using a two-factor test: character count >=80 AND the span does not contain a transition marker from the §4.A.5 marker list. Both conditions must be met for layer-indicator classification. Single condition met → `uncertain`. Threshold 80 chars is provisional — calibrate against KR test fixtures. [AUDIT FIX M-03]; (b) if the source metadata indicates `is_multi_layer: true` and bold text constitutes <5% or >60% of primary text on a page, the bold signal is treated as emphasis rather than layer indicator (too little or too much bold to be a matn/sharh boundary). Font size. Brackets.
   - PDF text: font size/weight differences from Docling output.
   - Scanned PDF/image: visual font size from OCR spatial output (less reliable).

3. **Content-based inference** (lowest reliability, ADVISORY ONLY) [AUDIT FIX M-04]:
   Content-based layer inference signals are NEVER sufficient alone for layer classification. They may increase or decrease confidence of a typographic-based classification:
   - Average sentence length <15 words + high formulaic density → +0.1 confidence for matn classification
   - `قال المصنف`/`قال الشيخ` → +0.1 confidence for sharh classification (referring to matn)
   - `قال أبو حنيفة`/`قال مالك` → AMBIGUOUS (appears in both layers), no confidence adjustment
   - These adjustments require multi-model consensus per D-041 since they are attribution decisions

**Detection algorithm:**
1. Start with the source metadata's layer specification.
2. Scan for explicit transition markers → high-confidence boundaries.
3. Scan for typographic signals → confidence 0.60–0.85 boundaries.
4. Infer layer for regions between boundaries from surrounding context.
5. For regions with no signals, assign the default layer (Layer 2 in sharh, Layer 3 in hashiyah).
6. Validate: Layer 1 text should be a minority of total text in commentaries. If Layer 1 exceeds 40%, flag for review.
7. **Hashiyah quotation detection (3-layer sources only).** In hashiyah sources, the hashiyah author frequently quotes the sharh author's text before commenting on it. When the hashiyah text contains explicit quotation markers ("قال الشارح:", "وعبارته:", "ونصه:", "قال في الشرح:"), the text following these markers until the next hashiyah-author signal (first-person assertion, explanatory "أي:", or a new quotation marker) is attributed to the sharh layer (Layer 2), not the hashiyah layer (Layer 3). This pattern-based quotation detection runs after the initial layer assignment (steps 1-5) and may reassign segments from Layer 3 to Layer 2. Confidence for pattern-detected quotations is 0.80-0.90; regions without explicit markers remain at their initial attribution.

**Conservative default:** When confidence for a text region is below 0.50, attribute to the commentary author (Layer 2 in sharh, Layer 3 in hashiyah), not the matn author. Misattributing commentary to the commentator is less harmful than attributing verbose explanation to an author known for terseness.

**Concrete example (multi-layer detection in a Shamela sharh):**

Input text (after HTML stripping, from a page of حاشية ابن قاسم on الروض المربع):
```
قوله: ويصح الوضوء بماء البحر.
لحديث: «هو الطَّهُورُ مَاؤُهُ الحِلُّ مَيْتَتُهُ». رواه الترمذي وصححه.
أي: ماء البحر طاهر في نفسه مطهر لغيره.
```

Layer detection output (`text_layers` for this segment):
```json
[
  {"layer_type": "sharh", "author_canonical_id": "buhuti_1051", "start": 0, "end": 5, "confidence": 0.70},
  {"layer_type": "matn", "author_canonical_id": "ibn_muflih_884", "start": 6, "end": 35, "confidence": 0.90},
  {"layer_type": "sharh", "author_canonical_id": "buhuti_1051", "start": 36, "end": 94, "confidence": 0.85},
  {"layer_type": "hashiyah", "author_canonical_id": "ibn_qasim_1392", "start": 95, "end": 143, "confidence": 0.80}
]
```

Detection reasoning: "قوله:" (marker, confidence ≥ 0.90 → transition to matn). Hadith citation + explanation → sharh. "أي:" (explanatory marker → hashiyah, since the source's outer layer is hashiyah).

#### §4.A.6 — Structure Discovery

Structure discovery identifies the source's internal organizational hierarchy — headings, chapters, divisions. This is the normalization engine's job because structural signals are format-specific and are lost after normalization.

**The division tree.** Output is a tree of division nodes. Each node: `div_id` (format: `div_{source_id}_{depth}_{index}`), `division_type` (one of: `كتاب`, `باب`, `فصل`, `مبحث`, `مطلب`, `فائدة`, `تنبيه`, `قاعدة`, `خاتمة`, `مقدمة`, `implicit`, `volume`, `root`; null if heading doesn't match a known keyword), `heading_text`, `heading_level` (1–10), `start_unit_index`, `end_unit_index` (inclusive), `detection_method`, `confidence`, `children` (nested `DivisionNode` array forming the tree).

**Heading text in primary_text.** Whether heading text appears in `primary_text` depends on the source type:
- **Shamela HTML:** `PageHead` elements are Shamela's navigation metadata (the current chapter label), NOT part of the author's text. They are recorded in `structural_markers` but EXCLUDED from `primary_text`. Inline headings detected by keyword heuristics within the page text ARE part of the text and remain in `primary_text`.
- **All other source types (PDF, OCR, EPUB, plain text, owner-authored):** Headings are part of the page content. They appear in `primary_text` AND are recorded in `structural_markers`. The `structural_markers.heading_text` is recorded for structure discovery; the same text remains in `primary_text` because removing it would alter the author's text.

**The four-tier confidence architecture:**

- **Tier 1 (confirmed):** Headings from explicit structural markup. Shamela: `<span class="title">` tags → `heading_detection_method: "html_tagged"`. PDFs: heading elements from Docling with confidence ≥ 0.90 → `heading_detection_method: "layout_detected"`. EPUB: navigation document entries and `<hN>` elements → `heading_detection_method: "layout_detected"`.
- **Tier 2 (high/medium):** Keyword heuristic detection. Lines starting with باب, فصل, مبحث, مطلب, فائدة, تنبيه, قاعدة, خاتمة, مقدمة, كتاب at paragraph beginnings, with ordinal patterns (الباب الأول, الفصل الثاني). ZWNJ heading markers (double ZWNJ at line start, 9.5% of Shamela corpus).
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

**Concrete example (structure discovery from Shamela HTML):**

Input signals detected across pages of كتاب المغني لابن قدامة:
- Page 1: `<span class="title">كتاب الطهارة</span>` → Tier 1, confirmed
- Page 12: Line starts with `باب الوضوء` (keyword heuristic) → Tier 2, confidence `high`
- Page 25: Line starts with `فصل في المسح على الخفين` → Tier 2, confidence `high`
- Page 38: No structural markup; Tier 3 LLM detects topic shift → confidence `medium`

Output division tree (excerpt):
```json
{
  "div_id": "div_fiqh_mughni_001_1_000",
  "division_type": "كتاب",
  "heading_text": "كتاب الطهارة",
  "heading_level": 1,
  "start_unit_index": 0,
  "end_unit_index": 142,
  "detection_method": "html_tagged",
  "confidence": "confirmed",
  "children": ["..."]
}
```

#### §4.A.7 — Page Boundary Preservation

Scholars cite by volume and page: "المغني vol.3 p.245." The normalization engine preserves page boundaries so this citation chain is never broken.

**Per content unit:** `volume` (int or null), `page_number_display` (Arabic-Indic form for citations), `page_number_int` (integer for sorting), `unit_index` (authoritative positional identifier).

**Critical rule:** `unit_index` is the ONLY positional identifier Phase 2 engines may use. `page_number_int` is display metadata only. 29.8% of Shamela corpus sources have duplicate page numbers, non-sequential numbering, or unnumbered pages.

**Non-page-based sources.** Plain text and owner-authored content create content units at paragraph boundaries or ~2000-character intervals. Physical page fields are null; only `unit_index` is meaningful.

**Cross-page text.** The normalization engine does NOT join text across page boundaries. Each content unit contains exactly the text on that physical page. The passaging engine handles cross-page continuity using `unit_index` adjacency. Joining would lose citation boundary information.

**Concrete example (page boundary preservation in a multi-volume Shamela source with non-sequential numbering):**

Input: المغني لابن قدامة, volume 3. The Shamela export has a common anomaly: after page 244, the numbering jumps to 246 (page 245 is missing in the export, possibly an empty page in the print edition). Additionally, page 12 of volume 3 has the same `page_number_int` as page 12 of volume 2 — different volumes, same page number.

Content units produced (excerpt):

```json
[
  {"unit_index": 487, "physical_page": {"volume": 3, "page_number_display": "٢٤٤", "page_number_int": 244}},
  {"unit_index": 488, "physical_page": {"volume": 3, "page_number_display": "٢٤٦", "page_number_int": 246}},
  {"unit_index": 489, "physical_page": {"volume": 3, "page_number_display": "٢٤٧", "page_number_int": 247}}
]
```

Key behaviors:
- `unit_index` is 487, 488, 489 — contiguous and monotonic regardless of the page number gap. Phase 2 engines use `unit_index` adjacency (488 follows 487) and never see the missing 245.
- The gap in `page_number_int` (244 → 246) is preserved as-is. No synthetic page 245 is inserted. The quality report logs `NORM_DUPLICATE_PAGES` (info) noting the non-sequential numbering.
- Volume 2 page 12 (`unit_index`: 11) and volume 3 page 12 (`unit_index`: 476) have the same `page_number_int: 12` but different `volume` values and different `unit_index` values. There is no collision — `unit_index` is the sole authoritative positional identifier.
- For a citation "المغني ج٣ ص٢٤٤", the scholar interface searches for `volume: 3, page_number_int: 244` and finds `unit_index: 487`. For a passage boundary computation, the passaging engine uses `unit_index` 487 and 488 as adjacent, never consulting `page_number_int`.

#### §4.A.8 — Diacritics and Arabic Text Handling

**Diacritics preservation is absolute.** Every diacritical mark preserved exactly: harakat (fatha, damma, kasra), tanwin, sukun, shadda, superscript alef, maddah. No stripping, no modification.

**No Unicode normalization.** NFC, NFD, NFKC, NFKD normalization is NOT applied to Arabic text. Different Unicode representations of the same visual character are preserved as-is.

**Encoding handling.** All output is UTF-8. Source encoding conversion logged. Mojibake flagged with `text_fidelity: "low"`.

**Whitespace normalization (conservative):** `\r\n`/`\r` → `\n`. Unicode whitespace normalization: U+00A0 (NBSP) → regular space; U+202F (narrow NBSP) → regular space; U+2000–U+200A (typographic spaces: en quad through hair space) → regular space; U+FEFF (BOM) → stripped at file start only, preserved elsewhere; U+200C (ZWNJ) → PRESERVED (used for heading detection in 9.5% of Shamela corpus); U+200B (ZWSP) → PRESERVED; U+200D (ZWJ) → PRESERVED. 2+ consecutive spaces → single space. Three+ blank lines → one blank line. Leading/trailing line whitespace trimmed. No other text transformation: no spelling correction, no punctuation changes, no reordering. [AUDIT FIX M-01]

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

**Concrete example (content flagging on a page with mixed signals):**

Input text (cleaned, from a fiqh source):
```
قال تعالى: {وَأَقِيمُوا الصَّلَاةَ وَآتُوا الزَّكَاةَ}
وعن ابن عمر رضي الله عنهما قال: قال رسول الله ﷺ: «بُنِيَ الإِسْلَامُ عَلَى خَمْسٍ»
رواه البخاري (٨) ومسلم (١٦).
```

Output `content_flags`:
```json
{
  "has_verse": false,
  "has_table": false,
  "has_quran_citation": true,
  "has_hadith_citation": true,
  "is_toc_page": false,
  "is_index_page": false,
  "is_blank": false
}
```

Detection: "قال تعالى:" followed by curly-brace Quran text → `has_quran_citation`. "عن ... قال: قال رسول الله ﷺ" + "رواه البخاري" → `has_hadith_citation`.

### §4.B — Transformative Capabilities

#### §4.B.1 — Scholarly Text Layer Intelligence

**Capability:** Beyond basic multi-layer detection (§4.A.5), the normalization engine infers layer boundaries in sources where explicit typographic or verbal markers are absent or inconsistent. Scholarly commentaries from older prints without tahqiq — particularly pre-20th-century editions — often have no bold formatting, no brackets, and irregular use of "قال المصنف." In these sources, the layer structure must be inferred from content patterns.

**Technical approach:** The normalization engine uses an LLM-based layer classifier via in-context learning, operating on a sliding window of text. [AUDIT FIX M-05] The classifier receives: a ~500-word window, the source's known layer composition (from metadata), the commentary genre (sharh/hashiyah), and examples of each layer's writing style from the same source (bootstrapped from high-confidence detections in earlier pages).

The classifier distinguishes layers using these content signals:
- **Terseness ratio:** Matn texts are characteristically dense — more technical terms per sentence, fewer connective particles, shorter sentences. The classifier measures information density per sentence and flags dense regions as likely matn.
- **Pronoun reference patterns:** In a sharh, the commentator uses third-person pronouns to refer to the matn author ("قال", "أراد", "يعني") and first-person for their own analysis ("أقول", "والصحيح عندي"). The classifier tracks pronoun patterns to detect layer shifts.
- **Temporal markers:** The commentator often references the matn author as historical ("وعند المصنف" — "according to the author"), while the matn author writes in the present tense of scholarly assertion. These temporal frames differ between layers.
- **Citation patterns:** The matn author rarely cites themselves; the commentator frequently cites the matn author and other scholars. Citation density signals which layer is active.

**What this enables:** Sources that would otherwise be processed as single-layer (because no typographic markers exist) can be correctly segmented. This prevents the most common form of layer misattribution — treating the entire text as the commentary author's words, which erases the matn author's contributions from the library. For the synthesizer, this means the definition "المبتدأ هو الاسم المرفوع" can be correctly attributed to ابن مالك (d. 672 AH) rather than ابن عقيل (d. 769 AH) even when the printed edition uses no bold or bracket formatting.

**Confidence and validation:** Content-inferred layer boundaries carry confidence `medium` at best. The normalization engine cross-validates inferred boundaries against any typographic signals that exist (even partial ones) and against the expected layer proportion (matn should be a minority). Pages where content inference disagrees with typographic signals are flagged with confidence `low` for human review.

**Concrete example (content-based layer inference in an old print without formatting):**

Input text (from a pre-tahqiq print of شرح الورقات, no bold, no brackets):
```
الحكم خطاب الله المتعلق بأفعال المكلفين بالاقتضاء أو التخيير
يعني بالحكم هنا الحكم الشرعي وهو ما ثبت بخطاب الله تعالى. وقوله المتعلق بأفعال المكلفين أخرج به ما يتعلق بذاته سبحانه نحو لا إله إلا الله. وأراد بالاقتضاء الطلب سواء كان طلب فعل أو طلب ترك. وأراد بالتخيير الإباحة وهي تسوية الطرفين.
```

Layer detection output:
```json
[
  {"layer_type": "matn", "author_canonical_id": "juwayni_478", "start": 0, "end": 65, "confidence": 0.72},
  {"layer_type": "sharh", "author_canonical_id": "mahalli_864", "start": 66, "end": 355, "confidence": 0.68}
]
```

Detection reasoning: The first sentence is characteristically terse and definitional ("الحكم خطاب الله المتعلق بأفعال المكلفين بالاقتضاء أو التخيير" — a single dense statement with no explanation). The second section begins with "يعني بالحكم هنا" (explanatory marker — "he means by 'ruling' here..."), uses third-person reference to the author ("وقوله" — "and his saying"), and provides discursive explanation with 4 clauses. The terseness ratio shifts sharply: 13 words in the first sentence convey a complete definition; the next 60+ words explain it. The LLM classifier detects this density shift and the third-person pronoun pattern as strong layer-boundary signals. Confidence is `medium` (0.68–0.72) because no typographic confirmation exists — content signals alone.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: LLM prompt engineering for Arabic layer classification, bootstrapping system for per-source style examples.

#### §4.B.2 — Structural Format Auto-Detection

**Capability:** The normalization engine automatically detects the source's structural format from content analysis, even when the source metadata does not specify it or specifies it incorrectly. This goes beyond genre classification (which the source engine handles at intake) to detect the actual TEXT STRUCTURE within a source.

**Technical approach:** The normalizer analyzes the first 20 content units (or all units for short sources) to detect structural patterns:

- **Q&A format detection:** Pattern: "مسألة:" or "سُئل عن" or "سؤال:" followed by a question, then "الجواب:" or "فأجاب:" followed by an answer. When Q&A patterns appear on >30% of analyzed pages, classify as `qa_format`. This is common in fatwa collections (مجموع الفتاوى) and مسائل books.
- **Tabular khilaf detection:** Pattern: "المسألة:" followed by "القول الأول:" / "القول الثاني:" / "الراجح:" structures. These map almost directly to taxonomy entries. When this pattern appears on >20% of analyzed pages, classify as `tabular_khilaf`.
- **Dictionary detection:** Pattern: root-organized entries (entries starting with Arabic root letters in a systematic sequence), or alphabetically organized entries. Short self-contained entries separated by clear markers. Classify as `dictionary`.
- **Verse detection:** When >50% of content lines match verse patterns (hemistich separators, line-level structure, consistent rhyme scheme at line ends), classify as `verse`. For mixed sources (a prose sharh containing quoted verse), the verse portions are flagged per-page without changing the overall classification.
- **Mixed format detection:** When 2 or more structural patterns are detected in the same source (e.g., a commentary with embedded Q&A sections and quoted verse), classify as `mixed` with a breakdown of which format appears in which divisions.

**What this enables:** The passaging engine and excerpting engine can apply format-specific strategies without source-format-specific code. A Q&A-format source produces natural passage boundaries at question-answer pairs. A dictionary produces passage boundaries at entries. A verse source produces passages respecting بيت boundaries. This information flows through the normalized package as metadata — the passaging engine reads `structural_format` and applies the right strategy without knowing anything about the source format.

**Validation [AUDIT FIX M-31]:** Auto-detection results are compared against the source engine's initial genre classification. If they disagree (e.g., source engine says `prose` but normalizer detects `qa_format`), both are recorded: the normalizer's detection in the manifest's `structural_format_proposed` field, with a note that it PROPOSES (not overrides) an alternative to the source metadata's classification. The source metadata's `structural_format` is NOT overwritten without human gate approval — the source engine's classification was produced by multi-model consensus and should not be unilaterally overridden by a single-engine heuristic analyzing only the first 20 pages. If the normalizer's proposed format differs, a human gate is created with both classifications and the evidence (pattern frequency, sample pages). The normalized package uses the source engine's classification until the human gate is resolved. Support `mixed` classification with per-division format breakdown.

**Concrete example (auto-detecting Q&A format in مجموع الفتاوى لابن تيمية):**

Input: First 20 content units of a Shamela export. Source metadata classifies `structural_format: "prose"` (the source engine's default for fiqh sources when no explicit format signal is available).

Detected patterns across 20 analyzed pages:
```
Page 3:  "سُئل شيخ الإسلام رحمه الله عن رجل حلف بالطلاق..." → "فأجاب: الحمد لله..."
Page 5:  "وسُئل رحمه الله عن من نذر أن يصوم..." → "فأجاب: هذا النذر..."
Page 8:  "مسألة: في رجل طلق امرأته ثلاثاً في مجلس واحد..." → "الجواب: الطلاق الثلاث..."
Page 9:  (continuation of answer from page 8, no Q&A pattern)
Page 12: "وسُئل عن امرأة تزوجت..." → "فأجاب: إذا كان..."
Page 14: "سُئل رحمه الله تعالى عن الحلف بالطلاق..." → "فأجاب: أما الحلف..."
...
```

Detection result: Q&A pattern markers ("سُئل" + "فأجاب" or "مسألة" + "الجواب") found on 8 of 20 pages (40%). Threshold is 30% → classified as `qa_format`.

Output in manifest:
```json
{
  "structural_format": "qa_format",
  "structural_format_detection": {
    "method": "content_analysis",
    "confidence": 0.88,
    "pattern_frequency": 0.40,
    "source_metadata_original": "prose",
    "proposed_override": true,
    "human_gate_required": true,
    "proposal_reason": "Q&A markers (سُئل/فأجاب, مسألة/الجواب) detected on 40% of sampled pages, exceeding 30% threshold"
  }
}
```

Enrichment write-back [AUDIT FIX M-31]: The source metadata's `structural_format` is NOT updated. A human gate is created with the proposed override. The original value remains authoritative until the human gate is resolved. `NORM_FORMAT_MISMATCH` (info) is logged.

What this means for downstream: The passaging engine will create passage boundaries at question-answer pairs (each "سُئل...فأجاب..." block becomes one passage). The excerpting engine knows each passage is a self-contained fatwa and extracts it as a single excerpt with question + answer preserved together.

#### §4.B.3 — Fine-Grained Text Fidelity Mapping

**Capability:** Instead of a single fidelity score per source or per page, the normalization engine produces a character-level fidelity map for OCR-processed sources. This map identifies exactly WHICH portions of a page are reliable and which are uncertain.

**Technical approach:** When dual-OCR comparison is active (§4.A.4), character-level alignment between Mistral OCR and Qari-OCR outputs produces an agreement map. Characters where both engines agree have high fidelity. Characters where they disagree are flagged with the alternatives and a confidence estimate. This produces a fidelity heat map per page.

Even with single-OCR processing, the normalizer computes a fidelity map from:
- OCR engine's per-character or per-word confidence scores (Mistral OCR 3 provides these in detailed output mode)
- Known OCR confusion patterns for Arabic (ب/ت/ث/ن, ح/خ/ج, ر/ز, similar-looking letter pairs)
- Morphological validation using CamelMorph MSA (Khairallah et al., 2024, integrated via CAMeL Tools). Words with zero analyses receive `morphological_status: "unknown"` and are excluded from fidelity scoring. Only words whose character sequences violate fundamental Arabic morphological constraints (no valid root extraction possible) contribute negatively to fidelity. RATIONALE: Classical Arabic scholarly vocabulary has systematically higher OOV rates in MSA lexicons (documented in Minaei-Bidgoli et al., 2026). [AUDIT FIX M-27]
- Diacritics confidence: diacritics on unusual positions receive lower confidence

**What this enables:** The excerpting engine can flag excerpts that contain low-fidelity regions rather than flagging entire pages. An excerpt where 95% of characters are high-fidelity and 5% are uncertain gets a nuanced fidelity score rather than being marked as uniformly unreliable. The synthesizer can weight high-fidelity excerpts more heavily and can note uncertainty at the character level: "The text reads عِلْم (knowledge), though the OCR confidence for the diacritics is moderate."

The scholar interface can display the fidelity heat map overlaid on the source text, letting the owner see exactly where OCR was confident and where it wasn't. This supports the owner's ability to verify KR's claims against the physical book.

**Concrete example (dual-OCR fidelity mapping on a scanned page of المحلى لابن حزم):**

Input: A scanned page processed by both Mistral OCR 3 and Qari-OCR. The page contains a partially faded line with diacritically dense text.

Mistral OCR output (excerpt, characters 45-90):
```
وَالصَّلَاةُ فَرْضٌ عَلَى كُلِّ مُسْلِمٍ بَالِغٍ عَاقِلٍ
```

Qari-OCR output (same region):
```
وَالصَّلَاةُ فَرْضٌ عَلَى كُلِّ مُسْلِمٍ بَالِعٍ عَاقِلٍ
```

Character-level alignment reveals one disagreement: position 72, Mistral reads `غ` (ghayn), Qari reads `ع` (ayn). The word is بَالِغٍ vs بَالِعٍ. Morphological validation: "بالغ" (mature/reaching puberty) is a valid Arabic word in this fiqh context; "بالع" (swallower) is morphologically valid but semantically nonsensical here. Resolution: Mistral's reading `بَالِغٍ` is accepted (morphological + contextual match), confidence 0.91.

Fidelity map output (excerpt for this region):
```json
{
  "fidelity_map": [
    {"char_range": [45, 71], "fidelity": "high", "confidence": 0.98, "method": "dual_ocr_agreement"},
    {"char_range": [72, 72], "fidelity": "medium", "confidence": 0.91, "method": "dual_ocr_disagreement_resolved",
     "alternatives": [{"text": "ع", "source": "qari_ocr", "confidence": 0.45}],
     "resolution": "morphological_validation"},
    {"char_range": [73, 90], "fidelity": "high", "confidence": 0.97, "method": "dual_ocr_agreement"}
  ]
}
```

Page-level fidelity summary: 94% of characters are `high` fidelity (dual-OCR agreement), 5% are `medium` (disagreement resolved by morphological validation or single-engine confidence), 1% are `low` (unresolved disagreements, flagged for review). The page's overall `text_fidelity.score` is `high` (since >90% of characters are high-confidence).

What this means for downstream: When the excerpting engine extracts the phrase "فرض على كل مسلم بالغ عاقل," it can report to the synthesizer that the excerpt is high-fidelity overall, with one character (`غ` in بالغ) at confidence 0.91. The synthesizer can present this without qualification, noting the uncertainty only if the disputed character changes meaning.

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

**Mixed-type footnotes.** A single footnote may contain content from ≥2 taxonomy types (e.g., "انظر: التسهيل ص ٤٥. والحديث أخرجه البخاري (٢٣٤٥)" contains both `cross_reference` and `hadith_takhrij`). When pattern matching detects markers for ≥2 types within one footnote, the footnote receives the type of its PRIMARY content (determined by which type's markers appear first, or which covers more of the footnote text). Additionally, a `secondary_types` field records the other detected types with their character ranges, so structured data extraction operates on each sub-section independently. The footnote's `footnote_type` is never `unknown_footnote_type` when any sub-section matches a known type.

**What this enables:** The excerpting engine can route hadith takhrij data to hadith metadata fields. The synthesizer can produce evidence-aware entries: "The Hanafi position rests on a hadith narrated by Abu Dawud (graded hasan by the editor), while the Shafi'i position cites a hadith in Bukhari (sahih)." Variant readings feed the source engine's edition comparison capability. Biographical notes enrich the scholar authority model. All of this metadata is extracted from the footnote apparatus during normalization — if it isn't captured here, it's lost.

**Concrete example (classifying 4 footnotes from a single page of a tahqiq edition of المغني لابن قدامة):**

Input footnotes (from Pass 2 separation):
```
(1) في نسخة (أ) و(ج): «يجوز» بدل «يجب». والمثبت من (ب) وهو الأصح لموافقته لما في المقنع.
(2) أخرجه البخاري في الطهارة (١٣٥) ومسلم (٢٢٥) واللفظ لمسلم. وصححه الألباني في الإرواء (١/١٢٣).
(3) هو: أبو عبد الله أحمد بن محمد بن حنبل الشيباني (ت ٢٤١هـ)، إمام أهل السنة. انظر: سير أعلام النبلاء (١١/١٧٧).
(4) الصواب: «المتيمم» بدل «المتوضئ» كما في نسخة (أ) و(ب)، ولعل ما في المطبوعة تصحيف.
```

Output classified footnotes:
```json
[
  {"ref_marker": "1", "text": "في نسخة (أ) و(ج): «يجوز» بدل «يجب». والمثبت من (ب) وهو الأصح لموافقته لما في المقنع.", "footnote_type": "variant_reading", "confidence": 0.95,
   "variant_data": {"sigla_cited": ["أ", "ج", "ب"], "variant_text": "يجوز", "main_text_reading": "يجب", "editor_preferred": "ب"}},
  {"ref_marker": "2", "text": "أخرجه البخاري في الطهارة (١٣٥) ومسلم (٢٢٥) واللفظ لمسلم. وصححه الألباني في الإرواء (١/١٢٣).", "footnote_type": "hadith_takhrij", "confidence": 0.97,
   "takhrij_data": {"collections": [{"name": "البخاري", "book": "الطهارة", "number": "135"}, {"name": "مسلم", "number": "225"}], "grading": {"grader": "الألباني", "grade": "صحيح", "reference": "الإرواء ١/١٢٣"}}},
  {"ref_marker": "3", "text": "هو: أبو عبد الله أحمد بن محمد بن حنبل الشيباني (ت ٢٤١هـ)، إمام أهل السنة. انظر: سير أعلام النبلاء (١١/١٧٧).", "footnote_type": "biographical_note", "confidence": 0.93,
   "bio_data": {"scholar_name": "أحمد بن محمد بن حنبل", "death_date_ah": 241, "description": "إمام أهل السنة"}},
  {"ref_marker": "4", "text": "الصواب: «المتيمم» بدل «المتوضئ» كما في نسخة (أ) و(ب)، ولعل ما في المطبوعة تصحيف.", "footnote_type": "correction_note", "confidence": 0.91,
   "correction_data": {"corrected_text": "المتيمم", "original_text": "المتوضئ", "basis": "نسخة (أ) و(ب)"}}
]
```

Detection: Footnote (1) matches `في نسخة (X):` pattern → `variant_reading`. Footnote (2) matches `أخرجه البخاري` + collection references → `hadith_takhrij`. Footnote (3) matches `هو:` + death date + biographical reference → `biographical_note`. Footnote (4) matches `الصواب:` correction marker → `correction_note`. All four are pattern-matched (no LLM needed), hence confidence ≥ 0.91 (pattern-match baseline). Note: the `variant_data`, `takhrij_data`, `bio_data`, and `correction_data` fields are type-specific structured extractions stored alongside the base footnote fields — they provide the machine-readable data that the synthesizer and scholar authority model consume.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: LLM footnote classifier, pattern library for Arabic scholarly footnote conventions.

#### §4.B.5 — Content Census and Downstream Adaptation Signals

**Capability:** Before any downstream engine touches the normalized package, the normalization engine produces a **content census** — a structured statistical profile of what the source contains, how it is organized, and how its content distributes across categories. This census travels with the normalized package as manifest metadata, enabling every downstream engine to adapt its processing strategy to THIS source's specific characteristics without reading the entire content stream first.

No existing scholarly text processing tool produces this kind of metadata. Current systems treat all 500-page books identically regardless of whether the book is 80% legal rulings or 80% hadith narration. The census changes that.

**Census fields (written to `manifest.json` under `content_census`):**

- `total_pages`: integer. Number of content units.
- `text_density_profile`: object. `mean_chars_per_page` (int), `median_chars_per_page` (int), `std_dev` (float), `sparse_page_count` (int, pages with <200 chars), `dense_page_count` (int, pages with >3000 chars). Downstream use: the passaging engine uses density distribution to calibrate target passage length — a dense fiqh reference needs smaller passages than a sparse devotional text.
- `verse_ratio`: float (0.0–1.0). Proportion of content units with `has_verse: true`. When >0.30, the passaging engine activates verse-aware boundary detection across all pages (not just flagged ones).
- `table_ratio`: float (0.0–1.0). Proportion of content units with `has_table: true`. When >0.10, the excerpting engine expects structured tabular knowledge (comparative rulings, conjugation tables).
- `quran_citation_ratio`: float (0.0–1.0). Proportion of content units with `has_quran_citation: true`. High ratios (>0.20) signal a tafsir-adjacent or usul-heavy source; the excerpting engine adjusts to extract evidence chains.
- `hadith_citation_ratio`: float (0.0–1.0). Proportion of content units with `has_hadith_citation: true`. High ratios (>0.15) signal a hadith-driven source; the excerpting engine prioritizes hadith takhrij extraction.
- `layer_complexity`: object. For multi-layer sources: `layer_count` (int), `transition_density` (float, mean layer transitions per page), `matn_ratio` (float, proportion of text attributed to Layer 1). Downstream use: high transition density (>5 per page) warns the excerpting engine that excerpt boundaries must respect layer transitions.
- `structural_depth`: object. `division_count` (int), `max_depth` (int, deepest level in the division tree), `mean_pages_per_leaf_division` (float). Downstream use: the passaging engine uses leaf division size to decide whether divisions alone provide adequate passage granularity (leaf division ≤ 15 pages) or whether sub-division splitting is needed.
- `footnote_density`: object. `mean_footnotes_per_page` (float), `max_footnotes_on_single_page` (int), `footnote_text_ratio` (float, proportion of total text that is footnotes). High footnote density (>5 per page) signals a heavily annotated tahqiq edition — the excerpting engine expects rich editorial metadata.
- `vocabulary_profile`: object. `estimated_unique_terms` (int, computed via HyperLogLog over ALL content units — no sampling. HLL processes sequentially with O(1) memory (~12KB). Standard error ~0.8% from HLL sketch precision with 2^14 registers) [AUDIT FIX M-15], `technical_term_density` (float, proportion of words matching the KR technical glossary for this source's science classification), `diacritics_density` (float, proportion of characters that are diacritical marks). High diacritics density (>0.08) signals a vocalized scholarly text, increasing downstream confidence in precise grammatical analysis.
- `fidelity_distribution`: object. `high_pct` (float), `medium_pct` (float), `low_pct` (float), `very_low_pct` (float). Downstream use: if `low_pct + very_low_pct > 0.25`, the excerpting engine applies conservative extraction thresholds and flags uncertain regions.

**Computation method:** The census is computed as a post-processing step after all content units are generated (Pass 6 in the Shamela normalizer, equivalent final pass in other normalizers). It iterates over the content JSONL once, accumulating statistics. For `vocabulary_profile.estimated_unique_terms`, a HyperLogLog sketch (precision 14, standard error ~0.8%) processes word tokens from ALL content units sequentially. HLL's O(1) memory (~12KB) and O(n) time make full-corpus processing trivial even for 1000+ page sources — no sampling is needed. [AUDIT FIX M-15] For `technical_term_density`, the normalizer loads the KR technical glossary for the source's science classification (a pre-built set of ~500–2000 terms per science) and measures the proportion of content words that appear in it.

**Concrete output example (for شرح ابن عقيل على ألفية ابن مالك, a Shamela export):**

```json
{
  "content_census": {
    "total_pages": 847,
    "text_density_profile": {
      "mean_chars_per_page": 1842,
      "median_chars_per_page": 1920,
      "std_dev": 412.3,
      "sparse_page_count": 23,
      "dense_page_count": 89
    },
    "verse_ratio": 0.38,
    "table_ratio": 0.01,
    "quran_citation_ratio": 0.12,
    "hadith_citation_ratio": 0.04,
    "layer_complexity": {
      "layer_count": 2,
      "transition_density": 3.7,
      "matn_ratio": 0.18
    },
    "structural_depth": {
      "division_count": 142,
      "max_depth": 3,
      "mean_pages_per_leaf_division": 5.2
    },
    "footnote_density": {
      "mean_footnotes_per_page": 4.1,
      "max_footnotes_on_single_page": 14,
      "footnote_text_ratio": 0.22
    },
    "vocabulary_profile": {
      "estimated_unique_terms": 8420,
      "technical_term_density": 0.14,
      "diacritics_density": 0.11
    },
    "fidelity_distribution": {
      "high_pct": 0.97,
      "medium_pct": 0.02,
      "low_pct": 0.01,
      "very_low_pct": 0.0
    }
  }
}
```

This census tells downstream engines: this is a 2-layer commentary (sharh on matn) with frequent verse quotation (38% of pages — the Alfiyyah lines), heavy footnotes (tahqiq edition), high vocabulary density (nahw technical terms), and excellent fidelity (Shamela digital text). The passaging engine knows to respect verse boundaries, the excerpting engine knows to expect nahw terminology and hadith citations, and the synthesizer knows this source's metadata is rich enough for narrative construction.

**What this enables that was previously impossible:** A scholar studying 50 books on nahw cannot quickly know "which of these books has the most hadith evidence?" or "which is the most footnote-dense tahqiq?" The census answers these questions before any human reads a page. It also enables the application to PRIORITIZE processing: sources with high technical term density in the owner's focus sciences get processed first.

[NOT YET IMPLEMENTED] — Full specification provided. No external dependencies beyond content flags already computed in §4.A.9.

#### §4.B.6 — Adaptive Multi-Engine OCR Orchestration

**Capability:** Instead of routing all scanned/image pages through a single OCR engine, the normalization engine implements an **adaptive orchestrator** that selects the optimal OCR engine (or engine combination) for each page based on that page's visual characteristics. Different pages within the same source may be processed by different engines.

This matters because the 2025 Arabic OCR landscape has specialized tools with complementary strengths:

| Engine | Strength | Weakness | Cost |
|--------|----------|----------|------|
| Mistral OCR 3 (API, `mistral-ocr-latest`) | Best layout understanding, good Arabic | Weaker on dense diacritics, API cost | ~$1-2/1000 pages |
| QARI-OCR v0.2 (local, Qwen2-VL-2B fine-tuned) | Best diacritics handling (CER 0.061), open-source | Weaker on complex multi-column layouts | GPU time only |
| Baseer (local/API, Qwen2.5-VL-3B fine-tuned) | Best Arabic document-to-markdown structural fidelity (WER 0.25) | Less tested on heavily diacritized classical texts | GPU time only |
| PaddleOCR-VL 1.5 (local, 0.9B) | Fastest, lightest, 90.67 OmniDocBench composite. CER 0.79 on Arabic multi-domain benchmark (ACL 2025). NOT recommended for Arabic scholarly text — retain only as fallback for non-Arabic content pages or as layout pre-analyzer | Arabic support poor for classical text | CPU/GPU, minimal |

**Benchmark caveat [AUDIT FIX M-17]:** All CER/WER figures above are from the respective models' own evaluations or general benchmarks. No standardized benchmark for classical Arabic scholarly text with full diacritization currently exists. Before production use, each engine MUST be evaluated on KR test fixtures (tests/fixtures/) using position-aligned CER on diacritized text. Routing decisions in the selection matrix below are provisional until KR-internal benchmarking is complete.

No single engine is best for all pages. A page of clean modern Arabic print → PaddleOCR-VL (fast, cheap, accurate enough). A page of densely diacritized classical nahw → QARI-OCR (best tashkeel handling). A complex multi-column layout with tables and footnotes → Baseer or Mistral OCR (best structural understanding). A degraded smartphone photo → Mistral OCR (best at noisy input interpretation).

**Page classification algorithm:**

For each page image, the orchestrator runs a lightweight pre-analysis (before full OCR):

1. **Layout complexity assessment.** Using PaddleOCR-VL's PP-DocLayoutV2 layout analysis model (runs in <0.5s per page), classify the page into: `single_column`, `multi_column`, `table_heavy`, `mixed_layout`. This model detects text blocks, tables, figures, and reading order without performing full OCR.

2. **Diacritics density estimation.** Run PaddleOCR-VL 1.5 (fast, lightweight) on the page. Analyze the output text for diacritics density: count tashkeel characters (U+064B–U+0652, U+0670) as a proportion of total characters. If diacritics_density > 0.08, the page is classified as `diacritics_heavy`.

3. **Image quality assessment.** Compute: resolution (DPI or equivalent pixel density), contrast ratio, blur metric (Laplacian variance), and skew angle. Pages with blur_metric < 100 or contrast_ratio < 1.5 are classified as `degraded`.

4. **Engine selection matrix:**

| Layout | Diacritics | Quality | Primary Engine | Fallback |
|--------|-----------|---------|----------------|----------|
| `single_column` | normal | good | PaddleOCR-VL 1.5 | — |
| `single_column` | heavy | good | QARI-OCR v0.2 | Baseer |
| `multi_column` | any | good | Baseer | Mistral OCR 3 |
| `table_heavy` | any | good | Mistral OCR 3 | Baseer |
| `mixed_layout` | any | good | Baseer | Mistral OCR 3 |
| any | any | degraded | Mistral OCR 3 | QARI-OCR v0.2 |
| any | heavy | degraded | QARI-OCR v0.2 + Mistral OCR 3 (dual) | — |

5. **Fallback trigger.** After primary OCR, compute page-level confidence. If confidence < `fidelity_medium_threshold` (default 0.80), re-process with the fallback engine. If both primary and fallback produce confidence below `fidelity_medium_threshold`, flag for human review.

6. **Dual-OCR mode.** When the matrix specifies dual processing (heavily diacritized + degraded), both engines process the page independently. Character-level alignment merges the outputs: agreement → confidence ≥ 0.95, disagreement → flag with both alternatives and confidence ≤ 0.70.

**Engine availability handling.** The orchestrator degrades gracefully based on available engines:
- All engines available → full adaptive routing (optimal).
- No QARI-OCR (no local GPU) → PaddleOCR-VL handles all single-column; Mistral OCR handles diacritics-heavy.
- No Baseer (not installed) → Mistral OCR handles multi-column/mixed.
- No Mistral OCR (no API key) → QARI-OCR and PaddleOCR-VL share all work; complex layouts get PaddleOCR-VL with lower confidence thresholds.
- Only PaddleOCR-VL available → all pages processed by PaddleOCR-VL; fidelity scores reflect the single-engine limitation.

The orchestrator logs which engine processed each page in the content unit's metadata: `ocr_engine` field in `TextFidelity` (must be added to contracts.py — see §9.1 M-18) [AUDIT FIX M-18]. This enables quality analysis: "pages processed by QARI-OCR had mean confidence 0.94; pages processed by PaddleOCR-VL had mean confidence 0.87 for this source."

**Concrete example (processing a scanned copy of المغني لابن قدامة):**

Page 1 (title page): `single_column`, normal diacritics, good quality → PaddleOCR-VL 1.5. Result: confidence 0.96.
Page 45 (dense fiqh text with heavy tashkeel): `single_column`, diacritics_heavy, good quality → QARI-OCR v0.2. Result: confidence 0.93.
Page 200 (comparative table of madhahib positions): `table_heavy`, normal, good → Mistral OCR 3. Result: confidence 0.91.
Page 347 (two-column layout with footnotes): `multi_column`, normal, good → Baseer. Result: confidence 0.89.
Page 500 (blurry smartphone photo): any, normal, degraded → Mistral OCR 3. Result: confidence 0.72 → fallback to QARI-OCR → merged confidence 0.78.

**What this enables that was previously impossible:** A scholar scanning 15 volumes of al-Mughni from different sources (5 clean PDFs, 6 phone photos, 4 old scans) gets the best possible OCR for EACH page without manual intervention. The system automatically adapts to page characteristics, maximizing accuracy while minimizing cost (PaddleOCR-VL is free and fast for easy pages; expensive API calls are reserved for pages that need them).

**Cost optimization.** The orchestrator tracks cumulative API costs per source. If a source's estimated total Mistral OCR cost exceeds a configurable threshold (`max_api_cost_per_source`, default $50), the orchestrator switches remaining pages to the best available local engine and logs a cost-limit warning.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: PaddleOCR-VL 1.5 (Apache 2.0, local), QARI-OCR v0.2 (Qwen2-VL-2B fine-tuned, open-source, local GPU), Baseer (Qwen2.5-VL-3B fine-tuned, open weights, local GPU), Mistral OCR 3 (commercial API). PP-DocLayoutV2 for layout pre-analysis (PaddlePaddle, Apache 2.0).

#### §4.B.7 — Tahqiq Apparatus Topology Extraction

**Capability:** The normalization engine extracts from the footnote apparatus a **manuscript witness network** — a structured graph of which manuscripts and editions the tahqiq editor consulted, how frequently each is cited, and where textual disagreements occur. This transforms the footnote apparatus from flat text into scholarly intelligence about the QUALITY AND RELIABILITY of the edition itself.

**Why this matters for KR:** When the synthesizer produces an entry citing "ابن قدامة in المغني says X," the reliability of that attribution depends on HOW GOOD the tahqiq edition is. An edition based on 6 manuscripts with careful collation is more reliable than one based on 1 manuscript with the editor's guesses. Currently, no tool extracts this information — a scholar must manually read through hundreds of footnotes to assess edition quality. The normalization engine sees every footnote and can build this picture automatically.

**Extraction algorithm:**

1. **Manuscript witness identification.** Scan all footnotes classified as `variant_reading` (by §4.B.4). Extract manuscript sigla — the abbreviations editors use to reference manuscripts. Common patterns:
   - Single-letter or abbreviated sigla: `(أ)`, `(ب)`, `(ج)`, `(م)`, `(ظ)`, or latin letters `(A)`, `(B)`, `(C)`.
   - Descriptive sigla: `نسخة الأزهرية`, `نسخة دار الكتب`, `الأصل`, `المطبوعة`.
   - The editor's introduction (typically first 10-20 pages) usually lists all manuscripts with their sigla. The normalizer parses this introduction for the manuscript register.

2. **Witness citation mapping.** For each variant reading footnote, record: `page_unit_index`, `siglum` (which manuscript), `variant_text` (the alternative reading), `editor_preference` (which reading the editor chose for the main text). Build a per-witness citation frequency map.

3. **Disagreement density mapping.** Compute per-division (from the division tree) the number of variant readings. Divisions with high variant density indicate textual instability — the manuscripts disagree more in those sections. This is stored in the manifest under `tahqiq_topology.disagreement_by_division`.

4. **Edition reliability signal.** Aggregate the witness network into an edition reliability score based on:
   - `witness_count`: The number of manuscripts the editor consulted. More witnesses → higher reliability.
   - `witness_coverage`: What proportion of the text has support from ≥2 witnesses. Higher coverage → more reliable.
   - `editor_transparency`: What proportion of variant readings include the editor's reasoning for their choice. Higher transparency → more trustworthy tahqiq.
   - `variant_density`: Total variant readings per 100 pages. Very low density (<0.5) in a tahqiq edition may indicate the editor didn't collate carefully; moderate density (2-10) is typical of careful collation; very high density (>20) indicates substantial textual instability across manuscripts.

**Output schema (stored in `manifest.json` under `tahqiq_topology`):**

```json
{
  "tahqiq_topology": {
    "has_tahqiq_apparatus": true,
    "manuscript_witnesses": [
      {
        "siglum": "أ",
        "description": "نسخة الأزهرية رقم ٣٤٥ حديث",
        "citation_count": 234,
        "first_cited_unit": 15,
        "last_cited_unit": 832
      },
      {
        "siglum": "ب",
        "description": "نسخة دار الكتب المصرية",
        "citation_count": 189,
        "first_cited_unit": 15,
        "last_cited_unit": 830
      },
      {
        "siglum": "الأصل",
        "description": "النسخة المعتمدة عند المحقق",
        "citation_count": 312,
        "first_cited_unit": 1,
        "last_cited_unit": 847
      }
    ],
    "total_variant_readings": 423,
    "variant_density_per_100_pages": 49.9,
    "disagreement_by_division": [
      {"div_id": "bab_mubtada", "variant_count": 12, "pages": 18},
      {"div_id": "bab_khabar", "variant_count": 8, "pages": 15}
    ],
    "edition_reliability": {
      "witness_count": 3,
      "witness_coverage": 0.92,
      "editor_transparency": 0.67,
      "reliability_signal": "moderate",
      "reliability_rationale": "3 manuscripts with 92% coverage; editor states preference in 67% of variants."
    },
    "extraction_confidence": "medium",
    "extraction_method": "pattern_matching_with_llm_fallback",
    "topology_confidence": 0.72,
    "topology_reliability": "uncertain"
  }
}
```

**Siglum detection patterns:**
- `في نسخة (X):` → siglum X, variant follows
- `في (X) و(Y):` → sigla X and Y agree on the variant
- `والمثبت من (X):` → editor chose reading from manuscript X
- `في الأصل: ... والصواب:` → editor corrected the base manuscript
- `كذا في جميع النسخ` → all witnesses agree (no variant)
- `سقط من (X)` → text missing from manuscript X (lacuna)
- `زيادة في (X)` → extra text in manuscript X

When patterns are insufficient (e.g., the editor uses non-standard notation), the normalizer invokes an LLM with the footnote text, the detected sigla register, and a description of standard tahqiq notation, requesting structured extraction. LLM-extracted variants carry confidence `medium`; pattern-matched variants carry confidence `high`.

**Topology confidence [AUDIT FIX M-29].** The topology extraction depends entirely on §4.B.4 footnote classification quality. A misclassified footnote creates a phantom manuscript disagreement. The manifest includes `topology_confidence` (float, 0.0-1.0): the mean classification confidence of all constituent `variant_reading` footnotes. When `topology_confidence < 0.85`, set `topology_reliability: "uncertain"` to warn downstream engines that the topology may contain errors from upstream classification. When `topology_confidence >= 0.85`, set `topology_reliability: "reliable"`.

**What this enables that was previously impossible:**

1. **Edition comparison at scale.** The source engine's edition comparison capability (§4.B.3 of source SPEC) can now be enriched: when two editions of the same work exist in the library, the normalizer's topology data reveals which edition consulted more manuscripts, which has more transparent editorial practice, and where the editions disagree because their editors had different manuscript witnesses.

2. **Textual stability signals for synthesis.** The synthesizer, when compiling an entry on a topic, can weight excerpts from textually stable sections (low variant density) more heavily than excerpts from unstable sections. If the entry cites a passage where 3 manuscripts disagree, the synthesizer can note: "This passage has textual variation across manuscripts (3+ witnesses diverge); the reading adopted here follows manuscript أ as preferred by the editor."

3. **Scholarly apparatus browsing.** The owner can query: "Show me all sections of al-Mughni where the manuscripts disagree on >5 readings per division." This is a question no existing tool answers without manual footnote reading across hundreds of pages.

**Edge cases:**
- Source has no tahqiq apparatus (e.g., a non-tahqiq reprint): `has_tahqiq_apparatus: false`. No topology extracted.
- Editor uses the apparatus but never names manuscripts (e.g., "في بعض النسخ" — "in certain copies"): Extractable as anonymous witnesses. `witness_count` reflects named witnesses only; anonymous references are counted separately under `anonymous_variant_count`.
- 2+ tahqiq editors on different volumes: Each volume's topology is tracked separately under `per_volume_topology`, with a merged summary in the top-level `tahqiq_topology`.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: §4.B.4 footnote classification (provides `variant_reading` footnotes as input), LLM for non-standard notation parsing, siglum pattern library.

#### §4.B.8 — Cross-Page Continuity Intelligence

**Capability:** The normalization engine annotates every page boundary with a **continuity signal** — a structured classification of whether the content flowing across that boundary is mid-sentence, mid-paragraph, mid-argument, or at a natural break point. After normalization, pages become abstract content units and this boundary intelligence is lost. The passaging engine needs exactly this signal to avoid creating passage boundaries that fracture scholarly arguments, and the excerpting engine needs it to know when consecutive content units form an inseparable logical block.

No existing Islamic text tool provides this. Current systems treat every page break as a potential split point, leading to passages that start mid-sentence or excerpts that capture half an evidence chain.

**Why this belongs in normalization, not passaging:** The signals for continuity are format-specific. In Shamela HTML, a sentence that runs to the end of a `<div class='PageText'>` and continues in the next div produces specific textual patterns (no terminal punctuation, no structural marker). In PDFs, Docling's reading order model detects text flow across pages. In OCR sources, the last line of one image and the first line of the next may form a continuous sentence detectable only from line geometry and text flow. After normalization strips these format-specific cues, only the text remains — and text-only continuity detection is far less reliable than format-aware detection.

**Continuity signal schema.** Each content unit (except the last) carries a `boundary_continuity` field in the content stream:

```json
{
  "boundary_continuity": {
    "type": "mid_sentence" | "mid_paragraph" | "mid_argument" | "section_break" | "division_break" | "unknown",
    "confidence": 0.0-1.0,
    "detection_method": "punctuation_analysis" | "structural_marker" | "argument_flow" | "format_specific" | "llm_inferred",
    "continuation_hint": "string or null"
  }
}
```

- `mid_sentence`: The page ends without terminal punctuation (period/full stop `.`/`۔`, question mark, or Arabic sentence terminator). The next page begins with a word that continues the syntactic structure. Confidence ≥ 0.90 when both conditions hold.
- `mid_paragraph`: The page ends at a sentence boundary (terminal punctuation present) but within the same paragraph — no heading, no structural keyword, no blank line follows. The next page continues the same topic. Confidence 0.70–0.85.
- `mid_argument`: The page ends during a scholarly argument cycle. Detected when the text within the last 200 characters of the page contains an argument-opening marker (see marker list below) whose corresponding argument-closing marker has not appeared, OR when the first 200 characters of the next page contain an argument continuation marker. Confidence 0.60–0.80 (depends on marker reliability).
- `section_break`: A structural heading is detected at or near the boundary (within 100 characters of the page end or page start). Corresponds to a division tree node boundary. Confidence ≥ 0.85 when heading detection is Tier 1 or high-confidence Tier 2.
- `division_break`: The boundary coincides with a volume boundary or a major structural division (كتاب-level). Confidence ≥ 0.95.
- `unknown`: Insufficient signal to determine boundary type. The normalizer logs this as `NORM_CONTINUITY_UNKNOWN` (info severity).

**Argument flow markers for mid-argument detection:**

| Marker Category | Opening Patterns | Closing/Continuation Patterns |
|---|---|---|
| Evidence chain | `والدليل`, `لقوله تعالى`, `ودليله`, `واحتجوا بـ`, `واستدلوا بـ` | `ونوقش بأن`, `ورُدّ بأن`, `والجواب` |
| Position statement | `وذهب ... إلى`, `والمذهب أن`, `القول الأول` | `القول الثاني`, `والراجح`, `والصحيح` |
| Objection-response | `واعترض عليه بأن`, `وأُشكل عليه`, `فإن قيل` | `فالجواب`, `قلنا`, `والجواب عنه` |
| Conditional reasoning | `إذا`, `ولو أن`, `فإن كان` | `وإلا`, `فحينئذ`, `فالحكم` |

When an opening marker appears in the last 200 characters of a page and no matching closing marker has appeared on that page, the boundary is classified as `mid_argument`. The `continuation_hint` field records the detected marker text (e.g., `"واستدلوا بـ — evidence chain opened, not closed"`).

**Format-specific continuity signals:**

- **Shamela HTML:** Sentence-ending analysis on cleaned text. The last character before the page boundary is checked: Arabic full stop (.) or other terminal punctuation → sentence boundary. No terminal punctuation → `mid_sentence`. Additionally, the next page's first content (after any heading) is checked: if it begins with a lowercase connective (و, ف, ثم) without a new sentence structure, this confirms mid-sentence or mid-paragraph continuity.
- **PDF (text-embedded):** Docling's reading order analysis detects text flow across pages. If the last text block on page N and the first text block on page N+1 form a continuous paragraph in Docling's model, the boundary is `mid_paragraph` or `mid_sentence` (refined by punctuation analysis).
- **OCR (scanned/image):** The last text line of one page and the first text line of the next are analyzed for syntactic continuity. OCR-detected page footers and headers are excluded. A word hyphenated across pages (rare in Arabic but occurs in narrow-column prints) is detected and the boundary is `mid_sentence` with confidence ≥ 0.95.

**Signal priority rule.** When ≥2 signals conflict, the resolution order is: (1) Structural heading detection at the boundary ALWAYS overrides punctuation-based or argument-based continuity analysis, regardless of heading confidence level. A heading at a boundary — even a `low`-confidence Tier 3 heading — produces `section_break` at the heading's confidence, never `mid_sentence`. Classical Arabic authors commonly omit terminal punctuation before chapter headings, and treating these as mid-sentence would systematically break passage boundaries at chapter transitions. (2) Argument flow markers override punctuation analysis: `mid_argument` subsumes `mid_sentence` when both are detected. (3) Punctuation analysis is the fallback when no structural or argument signals are present.

**What this enables that was previously impossible:**

1. **Zero-fracture passage boundaries.** The passaging engine reads `boundary_continuity` for every page and NEVER creates a passage boundary at a `mid_sentence` or `mid_argument` point. This eliminates the most common passage defect in Islamic text processing — splitting a definition from its explanation, or an evidence from its response.

2. **Argument-aware excerpt construction.** The excerpting engine, when constructing an excerpt that starts near a page boundary, checks continuity to ensure the excerpt includes the complete argument cycle. If page 45 ends with "واستدلوا بحديث" and page 46 has the hadith text and the response, the excerpting engine knows these pages form an inseparable block.

3. **Study flow intelligence.** The scholar interface can show the owner: "This argument spans pages 45-47 — read all three together." No existing tool provides this reading guidance.

**Concrete example (from a Shamela export of كتاب المغني, pages 234-235):**

Page 234 ends:
```
ولنا حديث ابن عباس رضي الله عنهما أن النبي ﷺ قال:
```

Page 235 begins:
```
«لا تُنكح الأيم حتى تُستأمر ولا تُنكح البكر حتى تُستأذن» متفق عليه.
والأيم هي الثيب. وهذا يدل على اشتراط إذنها.
```

Continuity analysis:
- Page 234 last text: ends with colon (`:`) after "قال:" — introducing a quotation that hasn't appeared yet. No terminal punctuation. → `mid_sentence`, confidence 0.95, detection_method: `punctuation_analysis`.
- Additionally: "ولنا حديث" is an evidence-chain opening marker → confirms `mid_argument`, confidence 0.85, detection_method: `argument_flow`.
- Final classification: `mid_argument` (higher semantic level subsumes `mid_sentence`), confidence 0.90.
- `continuation_hint`: `"Evidence chain: 'ولنا حديث' — hadith quotation started, not completed"`

Output:
```json
{
  "boundary_continuity": {
    "type": "mid_argument",
    "confidence": 0.90,
    "detection_method": "argument_flow",
    "continuation_hint": "Evidence chain: 'ولنا حديث' — hadith quotation started, not completed"
  }
}
```

**Edge cases:**
- Page ends with terminal punctuation but the next page immediately continues the same argument (e.g., "والدليل الأول..." ends with period, next page starts "والدليل الثاني..."): classified as `mid_argument` based on argument markers, even though sentence-level analysis says `section_break`. Argument flow markers override punctuation analysis.
- Page ends mid-word (rare, occurs in OCR page-split errors or corrupt Shamela exports where a PageText div boundary falls inside a word): classified as `mid_sentence` with confidence 1.0. The normalizer also logs `NORM_MIDWORD_BREAK` (warning).
- Source is non-paginated (plain text, owner-authored): `boundary_continuity` is null for all content units (boundaries are artificial). The passaging engine is informed via the `structural_format` metadata.
- Single-page source: no boundary to classify. Field absent from the sole content unit.

[NOT YET IMPLEMENTED] — Full specification provided. No external dependencies beyond existing normalization pipeline.

#### §4.B.9 — Authorial Voice Fingerprint for Multi-Layer Validation

**Capability:** The normalization engine builds a **stylometric fingerprint** for each text layer in a multi-layer source and uses cross-layer fingerprint comparison to validate — and flag for correction — layer attribution decisions. The fingerprint captures the quantitative writing characteristics that distinguish a terse matn author from a discursive commentator, independent of any typographic or verbal markers. This transforms layer detection from a single-pass classification into a statistically validated attribution.

**Why this is transformative:** Layer misattribution is the highest-integrity-risk error the normalization engine can make (§4.A.5). Current layer detection (§4.A.5 + §4.B.1) relies on typographic signals and content-based inference. Both can fail: typographic signals are absent in 25% of Shamela commentary exports, and content-based inference operates on short windows. The fingerprint operates on the AGGREGATE statistical properties of all text attributed to each layer across the entire source. If the layer detection made 90% correct attributions and 10% errors, the aggregate fingerprint for each layer will be dominated by the 90% correct text — and the 10% errors will show as statistical outliers.

No existing Islamic text tool validates layer attributions using author-level stylometric comparison. Research on Arabic stylometry (Ouamour & Sayoud 2016, Howedi et al. 2020) has shown that character n-grams and lexical features achieve 80-90% accuracy on Arabic authorship attribution even with short texts. KR applies this to the specific problem of validating matn/sharh/hashiyah layer boundaries, where the author differences are especially pronounced (matn authors write in fundamentally different registers than commentators).

**Fingerprint construction.**

After layer detection is complete for the entire source (Pass 5 in the Shamela normalizer), the engine builds one fingerprint per detected layer from all text attributed to that layer. The fingerprint contains:

- **Sentence length distribution:** mean, median, standard deviation of sentence lengths (in words). Matn texts have characteristically shorter sentences (mean 8-15 words) than sharh texts (mean 20-40 words). Computed by splitting on terminal punctuation and Arabic sentence-boundary heuristics.
- **Vocabulary richness (type-token ratio):** computed over a sliding window of 500 words. Matn texts have higher type-token ratios (more unique terms per window, less repetition) because they are definitional and dense. Sharh texts have lower ratios because they repeat and explain.
- **Connective particle frequency:** the proportion of tokens that are connective particles (و, ف, ثم, أو, لكن, بل, حتى, إذ, لأن, حيث). Sharh texts use more connectives (0.08-0.12 of all tokens) than matn texts (0.04-0.07) because explanation requires linking ideas.
- **Technical term density:** proportion of content words matching the KR technical glossary for this source's science. Both layers share a science, but matn texts have HIGHER technical density because definitions pack more terms per sentence.
- **Pronoun reference pattern:** frequency of third-person reference phrases ("قال", "أراد", "يعني", "وقوله") that indicate quoting or referencing the matn author. These should appear almost exclusively in Layer 2, not Layer 1.
- **Self-reference pattern:** frequency of first-person scholarly assertion phrases ("أقول", "والصحيح عندي", "والذي يظهر لي"). These belong to the layer's own author.
- **Citation density:** proportion of sentences containing explicit citations to other scholars or works. Commentary layers cite more frequently than matn layers.
- **Information density:** ratio of content words (nouns, verbs, adjectives after stop-word removal) to total words. Matn texts are denser (0.65-0.75) than sharh texts (0.50-0.60).

**Fingerprint schema (stored in manifest under `layer_fingerprints`):**

```json
{
  "layer_fingerprints": {
    "matn": {
      "author_canonical_id": "ibn_malik_672",
      "total_words_attributed": 12340,
      "sentence_length": {"mean": 11.2, "median": 9, "std_dev": 5.8},
      "type_token_ratio": 0.72,
      "connective_frequency": 0.052,
      "technical_term_density": 0.18,
      "pronoun_reference_frequency": 0.003,
      "self_reference_frequency": 0.001,
      "citation_density": 0.02,
      "information_density": 0.71
    },
    "sharh": {
      "author_canonical_id": "ibn_aqil_769",
      "total_words_attributed": 58920,
      "sentence_length": {"mean": 28.4, "median": 25, "std_dev": 12.1},
      "type_token_ratio": 0.48,
      "connective_frequency": 0.094,
      "technical_term_density": 0.11,
      "pronoun_reference_frequency": 0.041,
      "self_reference_frequency": 0.008,
      "citation_density": 0.09,
      "information_density": 0.54
    }
  }
}
```

**Validation algorithm.** After building fingerprints, the engine validates each page's layer attributions:

1. **Layer-level plausibility check.** Compare the two layer fingerprints against expected ranges for matn/sharh. If the "matn" fingerprint has sentence length mean > 25 and connective frequency > 0.09, it statistically resembles sharh — flag the entire layer detection as potentially inverted (`NORM_LAYER_FINGERPRINT_INVERSION`, warning severity). This catches the catastrophic failure where ALL matn text was attributed as sharh and vice versa. Specific inversion detection thresholds: if the "matn" layer has sentence_length.mean > 22 AND connective_frequency > 0.08 AND the "sharh" layer has sentence_length.mean < 16 AND connective_frequency < 0.06, the inversion signal is strong — trigger human gate review. Do not auto-correct — the human decides whether the labels should be swapped.

2. **Page-level outlier detection.** For each page, compute a local fingerprint from the text attributed to each layer on that page (minimum 50 words per layer on that page required; pages below this threshold are skipped). Compare the local fingerprint against the global fingerprint for that layer using Mahalanobis distance. Pages where the local fingerprint diverges by >2.0 standard deviations from the global fingerprint are flagged as potential misattribution (configurable, see §8, default 2.0). NOTE: This is a WEAK validation that detects only gross misattribution (>30% layer confusion). Moderate misattribution (5-15%) will not be detected by fingerprint alone. The fingerprint validation serves as a sanity check, not a proof of correct attribution. Minimum corpus requirement: 5,000 words per layer for meaningful fingerprint computation. Below this threshold, fingerprint validation is skipped and `fingerprint_status: "insufficient_data"` is set. [AUDIT FIX M-06] The flagged page's `text_layers` entries receive a `fingerprint_anomaly: true` field and their confidence scores are reduced by 0.15 (capped at minimum 0.10). For sources with >50 pages, per-segment fingerprinting is enabled by default: local fingerprints are computed per LAYER SEGMENT on each page rather than per page aggregate. This catches partial misattribution where a single short segment is wrong but the page overall appears correct. Per-segment fingerprinting increases computation by ~5x; it may be disabled via configuration for batch processing of low-priority sources.

3. **Cross-source fingerprint comparison.** [AUDIT FIX M-34: DEFERRED to Layer 3 library-wide validation] Cross-source fingerprint comparison requires reading OTHER sources' normalized packages, which exceeds the normalization engine's per-source format-transformation scope. The normalization engine computes and stores per-source fingerprints (steps 1-2 above). A separate library-wide validation service (not part of the normalization engine) compares fingerprints across sources when >=2 independent sources exist for the same matn author. The minimum-sources rule, single-layer precedence, and feedback loop described here remain valid requirements for that validation service. Until the library-wide validator is built, fingerprint validation is limited to within-source consistency (steps 1-2).

**Concrete example (validation catching a misattribution in شرح ابن عقيل):**

Global fingerprints (computed across 847 pages):
- Matn (ابن مالك): sentence_length mean = 10.8, connective_frequency = 0.048, information_density = 0.73
- Sharh (ابن عقيل): sentence_length mean = 27.1, connective_frequency = 0.091, information_density = 0.55

Page 312 local fingerprint (text attributed to matn on this page):
- sentence_length mean = 31.5, connective_frequency = 0.102, information_density = 0.51

This page's "matn" text looks statistically like sharh (long sentences, high connective frequency, low information density). Mahalanobis distance from global matn fingerprint: 3.8 standard deviations. → Flag: `fingerprint_anomaly: true`. The page is likely misattributed — perhaps a section where ابن عقيل's paraphrase was detected as matn because it began with a phrase similar to a verse.

The engine logs: `"Page 312: text attributed to matn (ابن مالك) has sharh-like statistical profile. Layer attribution confidence reduced from 0.75 to 0.60. Manual review recommended."` The quality report includes this page in the `layer_anomaly_pages` list.

**What this enables that was previously impossible:**

1. **Statistical validation of layer detection.** Instead of trusting layer boundaries based on a single classification pass, the engine produces a measurable consistency metric: "Layer detection for this source is statistically consistent across 94% of pages." This number is more informative than the per-page confidence scores alone.

2. **Automatic detection of systematic layer errors.** If the Shamela export's bold formatting is inconsistent (bold for matn on pages 1-200, no bold on pages 201-400 due to a formatting bug in the export), the fingerprint catches the pattern: pages 201-400 will show "matn" text with sharh-like fingerprints.

3. **Cross-source author voice verification.** When the library has ابن مالك's الألفية as a single-layer source AND as Layer 1 in five different commentaries, the engine can verify: "The text attributed to ابن مالك across all five commentaries has consistent stylometric properties, and those properties match his standalone work." This is unprecedented validation depth.

**Edge cases:**
- Very short matn texts (e.g., a matn with only 500 total words across 400 pages of commentary): insufficient data for reliable fingerprint. The engine marks `fingerprint_reliability: "insufficient_data"` when any layer has fewer than 2000 attributed words. Validation is skipped for that layer.
- Matn text is verse (نظم) while sharh is prose: the fingerprint metrics are computed separately for verse and prose text types. Verse text has different sentence length distributions (constrained by meter) that would confound the comparison. The `verse_ratio` from the content census (§4.B.5) triggers verse-aware fingerprinting.
- Hashiyah sources with 3 layers: each layer gets its own fingerprint. The hashiyah author's fingerprint is compared against both the sharh and matn fingerprints to verify it is distinct from both.
- Single-layer source: no fingerprint validation needed. The fingerprint is still computed (as a single-entry `layer_fingerprints` with one layer) for future cross-source comparison.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: completed layer detection (§4.A.5 + §4.B.1), content census (§4.B.5) for verse_ratio, KR technical glossary per science.

#### §4.B.10 — Scholarly Discourse Flow Annotation

**Capability:** The normalization engine annotates each content unit with a **discourse flow map** — a sequence of labeled discourse segments that identify the rhetorical function of each portion of the text. Where §4.A.6 (Structure Discovery) finds the source's HEADING hierarchy and §4.B.2 (Structural Format Auto-Detection) classifies the source's overall format, discourse flow annotation operates at a FINER granularity: within a single page, it identifies the sequence of scholarly discourse moves — claim, evidence, counter-evidence, objection, response, conclusion, example, definition, condition, exception.

This is not general-purpose discourse analysis. It is a domain-specific annotation system designed for the specific patterns of classical Islamic scholarly reasoning, which follows highly conventionalized structures. A fiqh discussion of a مسألة typically follows: statement of the ruling → evidence from Quran/Hadith → scholarly positions → objections → responses → preferred ruling. A nahw discussion follows: grammatical rule → شواهد (attestations) → exceptions → scholarly disagreements. These patterns are detectable from Arabic discourse markers that are remarkably consistent across centuries of scholarly production.

**Why this is transformative:** The synthesizer's target quality (ENTRY_EXAMPLE.md) requires entries that present "the core rule/definition, the evidence, the different scholarly positions, the reasoning behind each position, the edge cases, and the practical implications." Today, these must be manually identified within raw text. The discourse flow map pre-labels them during normalization: the excerpting engine can extract a complete argument cycle as a single excerpt because the normalization engine has already identified where the cycle starts and ends. No existing Islamic text tool provides this level of discourse structure annotation.

**Discourse segment taxonomy:**

| Segment Type | Arabic Markers | Description |
|---|---|---|
| `definition` | `هو/هي + noun phrase`, `يُعرَّف بأنه`, `المراد به`, `اصطلاحاً` | Definitional statement of a concept |
| `ruling` | `يجوز`, `لا يجوز`, `يجب`, `يُستحب`, `يُكره`, `يحرم`, `الحكم` | Statement of a legal/grammatical ruling |
| `evidence_quran` | `لقوله تعالى`, `قال تعالى`, `{...}` (Quran brackets) | Quranic evidence |
| `evidence_hadith` | `لقول النبي ﷺ`, `لحديث`, `روى ... عن`, `«...»` (hadith brackets) | Prophetic tradition evidence |
| `evidence_ijma` | `وقد أجمعوا على`, `بالإجماع`, `لا خلاف في` | Consensus evidence |
| `evidence_qiyas` | `قياساً على`, `ولأنه`, `بجامع` | Analogical reasoning |
| `evidence_athar` | `قال ابن عباس`, `عن عمر`, companion statement patterns | Companion statement evidence |
| `position` | `وذهب ... إلى`, `والمذهب`, `القول الأول/الثاني`, `ومذهب الشافعي` | Statement of a scholarly position |
| `objection` | `واعترض`, `وأُشكل`, `فإن قيل`, `ونُوقش`, `ولا يصح أن` | Objection to a position |
| `response` | `فالجواب`, `قلنا`, `وأُجيب`, `ورُدّ بأن`, `والجواب عن هذا` | Response to an objection |
| `preferred` | `والراجح`, `والصحيح`, `والمختار`, `والأظهر`, `والمعتمد` | Author's preferred conclusion |
| `example` | `نحو`, `كقولك`, `مثاله`, `ومن ذلك` | Illustrative example |
| `condition` | `بشرط`, `إذا`, `ويُشترط`, `ما لم` | Condition or prerequisite |
| `exception` | `إلا`, `ويُستثنى`, `ما عدا`, `سوى` | Exception to a rule |
| `elaboration` | `أي`, `يعني`, `والمعنى`, `توضيحه` | Explanatory elaboration |
| `narration` | discursive text with no specific markers | Default: narrative/expository text |

**Detection algorithm:**

1. **Marker scan.** For each content unit, scan the primary text for discourse markers from the taxonomy. A marker is detected when its pattern matches at a sentence or clause boundary (not embedded within a quotation). Each marker produces a candidate discourse segment starting at the marker position.

2. **Segment boundary inference.** Candidate segments extend from one marker to the next marker (or to the end of the page if no subsequent marker). When two markers appear in the same sentence (e.g., "والراجح لقوله تعالى" — preferred + Quran evidence in one phrase), the more specific marker takes priority for the segment type, and the other is recorded as a secondary annotation.

3. **LLM refinement.** For pages where marker-based detection produces fewer than 2 segments (i.e., the text is largely unmarked scholarly prose), invoke an LLM to classify paragraphs by discourse function. The LLM receives: the page text, the source's science and genre, and a description of the discourse segment taxonomy. LLM-classified segments carry confidence 0.50–0.70 (lower than marker-based, which carry 0.80–0.95).

4. **Cross-page argument cycle detection.** When a page's last discourse segment is an incomplete argument cycle (e.g., `position` without a subsequent `evidence` or `preferred`), the engine checks the next page for continuation. If the next page begins with a segment that completes the cycle, the boundary_continuity (§4.B.8) is updated to `mid_argument` if not already set, and the `continuation_hint` records the discourse flow context.

**Output schema (per content unit, in `discourse_flow` field):**

```json
{
  "discourse_flow": {
    "segments": [
      {
        "type": "definition",
        "start_char": 0,
        "end_char": 67,
        "confidence": 0.92,
        "detection_method": "marker",
        "marker_text": "المبتدأ هو"
      },
      {
        "type": "position",
        "start_char": 68,
        "end_char": 145,
        "confidence": 0.88,
        "detection_method": "marker",
        "marker_text": "وذهب الكوفيون إلى"
      },
      {
        "type": "evidence_hadith",
        "start_char": 146,
        "end_char": 234,
        "confidence": 0.95,
        "detection_method": "marker",
        "marker_text": "لحديث"
      }
    ],
    "dominant_discourse_type": "argumentative",
    "argument_cycle_complete": false,
    "argument_cycle_started_at_segment": 1,
    "cycle_missing_elements": ["preferred"]
  }
}
```

The `dominant_discourse_type` field classifies the page's overall discourse character:
- `argumentative`: 2+ positions, evidence, objections/responses (typical of fiqh, usul, aqidah discussions)
- `definitional`: primarily definitions and elaborations (typical of textbook introductions, grammar mutun)
- `evidential`: primarily evidence chains with minimal argumentation (typical of hadith-focused discussions)
- `narrative`: expository prose without clear scholarly argument structure (typical of biographical entries, historical context)
- `enumerative`: list-like content (conditions, categories, exceptions) (typical of furu' al-fiqh details)

**Concrete example (from a page of المغني لابن قدامة, vol. 1 p. 245, on the topic of wiping over socks):**

Input text (cleaned):
```
مسألة: ويجوز المسح على الخفين في الحضر والسفر.
وهذا قول أكثر أهل العلم. حُكي عن مالك أنه يجوز للمسافر دون المقيم.
والدليل على جوازه للمقيم حديث المغيرة بن شعبة «أنه صبّ على النبي ﷺ الماء فمسح على خفيه» متفق عليه. وكان ذلك في الحضر.
ولأن الرخصة ثبتت بالسنة المتواترة فلا تُقيَّد بالسفر.
واعترض من منعه في الحضر بأن أحاديث المسح وردت في السفر غالباً.
والجواب أن حديث المغيرة صريح في الحضر. ولو سُلّم أن الغالب في السفر فلا يقتضي التخصيص.
والصحيح: جوازه مطلقاً.
```

Discourse flow output:
```json
{
  "discourse_flow": {
    "segments": [
      {"type": "ruling", "start_char": 0, "end_char": 50, "confidence": 0.93, "detection_method": "marker", "marker_text": "يجوز"},
      {"type": "position", "start_char": 51, "end_char": 116, "confidence": 0.85, "detection_method": "marker", "marker_text": "قول أكثر أهل العلم"},
      {"type": "position", "start_char": 117, "end_char": 170, "confidence": 0.88, "detection_method": "marker", "marker_text": "حُكي عن مالك"},
      {"type": "evidence_hadith", "start_char": 171, "end_char": 302, "confidence": 0.95, "detection_method": "marker", "marker_text": "حديث المغيرة"},
      {"type": "evidence_qiyas", "start_char": 303, "end_char": 365, "confidence": 0.82, "detection_method": "marker", "marker_text": "ولأن"},
      {"type": "objection", "start_char": 366, "end_char": 437, "confidence": 0.91, "detection_method": "marker", "marker_text": "واعترض"},
      {"type": "response", "start_char": 438, "end_char": 540, "confidence": 0.93, "detection_method": "marker", "marker_text": "والجواب"},
      {"type": "preferred", "start_char": 541, "end_char": 570, "confidence": 0.96, "detection_method": "marker", "marker_text": "والصحيح"}
    ],
    "dominant_discourse_type": "argumentative",
    "argument_cycle_complete": true,
    "argument_cycle_started_at_segment": 0,
    "cycle_missing_elements": []
  }
}
```

This page contains a COMPLETE argument cycle: ruling → positions → evidence → objection → response → conclusion. The passaging engine knows: this page is a self-contained scholarly argument — it's an ideal passage boundary candidate at both ends. The excerpting engine knows: this is a complete مسألة discussion that should be extracted as a single excerpt with all discourse elements intact.

**What this enables that was previously impossible:**

1. **Automatic مسألة extraction.** The most valuable unit in fiqh scholarship is the complete مسألة — ruling + positions + evidence + resolution. The discourse flow map identifies exactly where each مسألة starts and ends. The excerpting engine can extract complete مسائل without human annotation.

2. **Evidence-type statistics per source.** The content census (§4.B.5) reports page-level content flags. Discourse flow goes deeper: "This source uses Quranic evidence in 45% of its arguments, hadith evidence in 78%, and qiyas in 23%." This tells the synthesizer what kind of evidence this source provides.

3. **Scholarly methodology profiling.** By analyzing discourse flow patterns across the entire source, the engine characterizes the author's reasoning style: "Ibn Qudamah in al-Mughni follows a consistent pattern: position → evidence → objection → response → preferred, with evidence_hadith appearing in 82% of argument cycles." This is a scholarly insight that no tool currently produces.

4. **Argument completeness signals for the passaging engine.** The `argument_cycle_complete` field tells the passaging engine: "this content unit is a self-contained argument" or "this argument continues on the next page." The passaging engine uses this to create passages that respect argument boundaries, not just heading boundaries.

5. **Position hints for the excerpting engine.** [AUDIT FIX M-08] The `position_metadata` fields (`school_hint`, `attribution_hint`) are REMOVED from discourse flow output. School attribution and scholar attribution are downstream decisions belonging to the excerpting and taxonomy engines, not the normalization engine. The normalization engine's discourse flow is limited to structural annotation (segment boundaries and types). Discourse flow annotations carry `discourse_annotation_authority: "advisory"` — downstream engines may override any classification.

**Edge cases:**
- Source with no recognizable discourse markers (e.g., a purely historical narrative or biographical dictionary): all text is classified as `narration`. `dominant_discourse_type: "narrative"`. This is valid — not all sources contain structured scholarly argumentation.
- Source where discourse markers appear inside quotations (e.g., the author quotes another scholar's full argument): the detection algorithm uses quotation detection (guillemets «», explicit "قال فلان:" introductions) to suppress marker detection within quoted passages. Markers inside quotes have `is_quoted: true` set on the `DiscourseSegment` (see §9.1 M-20 for contract alignment), retaining their original `detection_method` but indicating they are not the source author's own argument flow. [AUDIT FIX M-20]
- Mixed-format pages where the author switches between definitional and argumentative discourse within a single page: both segment types are recorded. The `dominant_discourse_type` is determined by which type covers more characters.
- Very short pages (<100 characters): insufficient text for meaningful discourse annotation. `discourse_flow.segments` is empty; `dominant_discourse_type: "insufficient_text"`.
- Verse (nazm) source: each بيت often encodes a single rule. Discourse segments align with verse lines rather than prose sentence boundaries. The engine uses the verse_info from §4.A for segment boundaries in versified text.

**Per-science calibration (Level 3 / SCIENCE.md hooks):**
- **Fiqh:** full argument cycle detection with all marker types. [AUDIT FIX M-08] School attribution is deferred to downstream engines.
- **Nahw:** definitional segments are primary. Evidence segments map to شواهد (attestations from Quran, hadith, poetry). School attribution (Basran/Kufan) deferred to downstream engines.
- **Usul al-fiqh:** meta-level argument cycles ("evidence for the evidence rule") use the same taxonomy but with additional markers for أصولي reasoning (istishab, istihsan, maslaha).
- **Hadith methodology:** discourse focuses on `evidence_athar` and narrator evaluation. Argument cycles center on hadith authenticity rather than legal rulings.
- **Tajwid:** primarily definitional and enumerative (rules and conditions). Minimal argumentation.

[NOT YET IMPLEMENTED] — Full specification provided. Depends on: discourse marker pattern library (per science), LLM prompt for unmarked discourse classification, §4.B.8 cross-page continuity for argument cycle spanning.

---

## 5. Validation and Quality

The normalization engine's output determines the quality ceiling for every downstream knowledge product. An error here cascades: footnotes mixed into main text → wrong excerpts → wrong entries → wrong knowledge in the owner's mind.

**Layer 1: Self-validation (automated, at normalization time).**

1. **Schema compliance.** Every content unit is validated against the content unit schema before writing. The manifest is validated against the manifest schema. Any schema violation aborts normalization with a structured error.

2. **Coverage check.** The number of content units must match the expected page count from the source metadata (±10% tolerance for skipped metadata/blank pages). A mismatch exceeding 10% triggers warning `NORM_PAGE_COUNT_MISMATCH` and requires human review. For deterministic source types (Shamela HTML, text PDFs) where the normalizer can count the exact number of pages from the source structure (PageText divs, PDF page count), a tighter check applies: the normalizer counts input pages in Pass 1, and the final content unit count must equal the input page count minus explicitly skipped pages (metadata pages, confirmed duplicates). Any discrepancy triggers `NORM_PAGE_COUNT_MISMATCH`. This catches even single-page loss in Shamela sources, where a malformed PageText div might be silently skipped by the HTML parser.

3. **Text extraction verification.** For each content unit:
   - `primary_text` must be non-empty (except for `is_blank` pages).
   - Character distribution must be plausible for Arabic text: ≥70% Arabic characters (excluding whitespace and punctuation). A page with <70% Arabic characters is flagged as potentially corrupted.
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
   - Footnote reference markers in primary text have corresponding footnote entries. Orphan references (markers with no matching footnote) trigger `NORM_ORPHAN_FOOTNOTE_REF` (info): the marker is preserved as literal text in `primary_text` (NOT converted to the universal ⌜N⌝ format), and the orphan is logged. Only markers with a confirmed matching footnote are replaced with the universal format.
   - Conversely, footnotes with no corresponding reference marker in primary text are preserved in the `footnotes` array (they may be page-bottom annotations without inline references).

7. **Unit index integrity.** The `unit_index` values across all content units must form a contiguous zero-based sequence: 0, 1, 2, ..., N-1 where N = `total_content_units`. Any gap (e.g., 0, 1, 3 — missing 2) or duplicate triggers `NORM_UNIT_INDEX_VIOLATION` (fatal). This check is critical because Phase 2 engines use unit_index adjacency for cross-page continuity — a gap would cause the passaging engine to treat consecutive pages as non-adjacent.

8. **Diacritics preservation verification.** For format types where the source text is available as digital text (Shamela HTML, text PDFs, EPUB, plain text — NOT OCR sources), the normalizer performs a character-class comparison between the source's Arabic text and the output `primary_text`. Specifically: extract all Unicode characters in the Arabic diacritics range (U+064B–U+0652, U+0670, U+0640) from both source and output for each page. If the diacritic character counts differ by even one character, the page fails with `NORM_DIACRITICS_DRIFT` (fatal). This detects the scenario where a Python library or string operation silently applies Unicode normalization or strips diacritics. For OCR sources, this check is not applicable — OCR output is the baseline, not the image.

9. **Format-specific input validation.** Each normalizer validates that its input matches the expected format BEFORE processing begins. The text PDF normalizer verifies the PDF contains an extractable text layer (at least 100 characters of text extractable by Docling from the first 5 pages); if no text layer is found, it rejects with `NORM_NO_TEXT_LAYER`. The Shamela normalizer verifies at least one `<div class='PageText'>` element exists. The image normalizer verifies at least one image file exists with a recognized image format. This prevents the wrong-normalizer-selected scenario: a scanned PDF routed to the text PDF normalizer is caught immediately rather than producing garbage output.

10. **Boundary continuity consistency (§4.B.8).** For every content unit except the last: if `boundary_continuity` is present, verify: (a) `type` is one of the valid enum values, (b) `confidence` is in range 0.0–1.0, (c) if `type` is `mid_sentence`, the `primary_text` does not end with terminal punctuation (period, question mark, exclamation mark — a contradiction would indicate a detection bug), (d) the last content unit has no `boundary_continuity` field (there is no boundary after the last page). Failures produce `NORM_CONTINUITY_INCONSISTENT` (warning, non-fatal — continuity is advisory metadata).

11. **Discourse flow consistency (§4.B.10).** For content units with `discourse_flow` present: verify (a) `segments` array character ranges are non-overlapping and within `primary_text` bounds, (b) if `argument_cycle_complete` is `true`, then `cycle_missing_elements` is empty (a complete cycle cannot have missing elements), (c) `dominant_discourse_type` is one of the valid enum values, (d) if `primary_text` has fewer than 100 characters, `discourse_flow` is null (per the <100 character rule in §4.B.10). Failures produce `NORM_DISCOURSE_INCONSISTENT` (warning, non-fatal).

12. **Layer fingerprint plausibility (§4.B.9).** For multi-layer sources with `layer_fingerprints` in the manifest: verify (a) every layer listed in `layer_map` has a corresponding entry in `layer_fingerprints` (or is marked `fingerprint_reliability: "insufficient_data"`), (b) `sentence_length.mean` is positive, (c) `type_token_ratio`, `connective_frequency`, and `information_density` are in range 0.0–1.0, (d) `total_words_attributed` is positive. Failures produce `NORM_FINGERPRINT_INVALID` (warning, non-fatal).

13. **OCR coherence check (OCR sources only).** For pages processed via OCR where both engines agree (dual-OCR confidence ≥ 0.90), perform a sentence-level coherence spot check: sample 3 random sentences per page and verify each is syntactically plausible Arabic using morphological analysis (all words should parse as valid Arabic morphemes in at least one reading). Pages where >50% of sampled sentences fail coherence are flagged as `NORM_OCR_COHERENCE_FAILURE` (warning) and their `text_fidelity.score` is downgraded to `low` regardless of OCR agreement. This catches the "confident garbage" scenario where both OCR engines produce real Arabic words in incoherent sequences from severely degraded pages.

14. **OCR diacritics hallucination check (OCR sources only).** Compare the diacritics density of the OCR output against the source metadata's expected diacritization level. If the source is classified as `unvocalized` or `partially_vocalized` in the source metadata, but the OCR output has diacritics density >0.06, trigger `NORM_OCR_DIACRITICS_HALLUCINATION` (warning). This signals that diacritics may be OCR-generated rather than author-placed.

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
- **Footnote classification (§4.B.4):** Two-tier classification [AUDIT FIX M-24]: (1) Pattern matching against known tahqiq footnote patterns. If pattern confidence >= 0.85, accept classification without consensus. (2) For ambiguous footnotes (pattern confidence < 0.85), require multi-model consensus per D-041 — footnote classification is a content decision that affects downstream attribution and synthesis. A `correction_note` misclassified as `variant_reading` tells the synthesizer manuscripts disagree when in fact the editor asserts an error. Add `classification_method: "pattern"|"consensus"` and `classification_confidence: float` to each classified footnote.
- **Dual-OCR comparison (§4.A.4):** This IS a form of consensus — two independent OCR engines process the same input. Agreement means confidence ≥ 0.95; disagreement is resolved by character-level analysis. This is more effective than multi-model LLM consensus for text extraction because the disagreement signals are character-level rather than semantic.

If future experience shows that LLM-assisted operations in this engine have unacceptable error rates, multi-model consensus can be added to specific operations without architectural changes — each LLM call is already a well-defined function with structured inputs and outputs.

---

## 7. Error Handling

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `NORM_UNKNOWN_SOURCE_FORMAT` | Fatal | `source_format` not recognized | Reject. Owner or source engine must correct the metadata. |
| `NORM_MISSING_FROZEN` | Fatal | Frozen directory empty or missing | Reject. Source engine must re-freeze. |
| `NORM_MISSING_METADATA` | Fatal | Source metadata record missing or invalid | Reject. Source engine must recreate metadata. |
| `NORM_SCHEMA_VIOLATION` | Fatal | Output fails schema validation | Abort normalization. Log the violation. This is a normalizer bug. |
| `NORM_OCR_FAILED` | Fatal | OCR engine returns error, OR OCR returns HTTP 200 but output text is empty or <10 characters for a page whose image contains visible content (empty-success case) | Retry once with the fallback engine from §4.B.6 selection matrix. If still failed, reject with the OCR error message. The empty-success case is detected by checking: (a) OCR returned successfully, (b) extracted text length <10 chars, (c) page image is not blank (pixel variance >threshold). [AUDIT FIX M-33] |
| `NORM_ENCODING_ERROR` | Warning | Source uses unrecognized or corrupted encoding | Convert what is possible. Flag affected pages as `text_fidelity: "low"`. |
| `NORM_LOW_FIDELITY` | Warning | >25% of pages have fidelity below `medium` | Normalization completes. Human gate triggered. |
| `NORM_LAYER_UNCERTAIN` | Warning | Layer detection confidence below threshold for >30% of pages | Normalization completes. Human gate triggered. Downstream engines see confidence scores. |
| `NORM_SPARSE_STRUCTURE` | Warning | Fewer than 3 divisions in 50+ pages | Normalization completes. Human gate triggered. Passaging engine warned. |
| `NORM_FORMAT_MISMATCH` | Info | Detected structural format differs from source metadata | Write-back enrichment to source metadata. Log. |
| `NORM_PAGE_COUNT_MISMATCH` | Warning | Content unit count differs >10% from expected page count | Log. May indicate skipped pages or extra content. |
| `NORM_DUPLICATE_PAGES` | Info | Duplicate page numbers detected | Log. Use `unit_index` as authoritative reference. |
| `NORM_PARTIAL_PAGE` | Warning | Image source: page appears truncated | Flag content unit. |
| `NORM_OCR_API_RATE_LIMIT` | Warning | Mistral OCR API rate limited | Implement exponential backoff. Retry. |
| `NORM_WRITE_FAILED` | Fatal | Atomic write procedure failed (disk error, rename failure) | Remove temp directory. Retry once. If still failed, reject source. |
| `NORM_UNIT_INDEX_VIOLATION` | Fatal | unit_index values are not monotonically increasing starting from 0, or contain duplicates | Abort normalization. This is a normalizer bug — unit_index generation must be deterministic. |
| `NORM_NO_TEXT_LAYER` | Fatal | Text PDF normalizer found no extractable text layer in PDF | Reject. Reclassify source as `pdf_scanned` and re-route to scanned PDF normalizer. |
| `NORM_PAGE_ORDER_CONFLICT` | Warning | Image set: filename sort order disagrees with OCR-detected page numbers | Use filename sort as authoritative. Log both orderings. Human gate triggered. |
| `NORM_FOOTNOTE_SEPARATOR_ABSENT` | Info (Warning for tahqiq editions) | Shamela page has no `<hr>` tag with width 80-100 (per §4.A.2 Pass 2 regex) | Treat entire page content as primary text. Log. If >30% of pages have this, flag source as `no_footnote_apparatus`. For tahqiq editions (source metadata indicates tahqiq editor): if >10% of pages have this, trigger human gate — the separator pattern may be non-standard and needs manual identification. |
| `NORM_DIACRITICS_DRIFT` | Fatal | Post-normalization byte comparison detects diacritics were modified during processing | Abort normalization. This indicates a code bug (likely a library applying Unicode normalization). |
| `NORM_CONTINUITY_INCONSISTENT` | Warning | Boundary continuity field contradicts text content (e.g., `mid_sentence` but text ends with period) | Log. Set `boundary_continuity.confidence` to 0.0 for affected content unit. Downstream engines will treat as `unknown`. |
| `NORM_DISCOURSE_INCONSISTENT` | Warning | Discourse flow field fails internal consistency (overlapping segments, complete cycle with missing elements) | Log. Set `discourse_flow` to null for affected content unit. Downstream engines proceed without discourse data for that page. |
| `NORM_FOOTNOTE_CLASSIFICATION_FAILED` | Info | LLM fallback for footnote classification (§4.B.4) returns error, timeout, or unparseable response | Footnote retains coarse classification (`tahqiq_editor`/`author_original`/`unknown_footnote_type`). Log the LLM error. Classification method recorded as `"pattern_only"`. Does not block normalization — footnote is usable with coarse type. [INTEGRITY AUDIT FIX] |
| `NORM_FINGERPRINT_INVALID` | Warning | Layer fingerprint values are out of valid range or missing for a declared layer | Log. Set `layer_fingerprints` to null in manifest. Fingerprint validation (§4.B.9) is skipped for this source. |
| `NORM_ORPHAN_FOOTNOTE_REF` | Info | Footnote reference marker in primary text has no corresponding footnote entry | Preserve the marker as literal text (e.g., "(3)" remains as-is). Do NOT replace with universal ⌜N⌝ format. Log the orphan reference with page unit_index and marker text. |
| `NORM_SUSPICIOUS_PAGEHEAD` | Warning | Shamela PageHead content does not match heading patterns AND exceeds 100 characters | Treat as misplaced primary text. Include in primary_text. Flag for human review. |
| `NORM_ORDERING_UNCERTAIN` | Warning | Image-sourced source: >30% of page boundaries have `unknown` or low-confidence continuity | May indicate misordered pages. Human gate triggered. |
| `NORM_OCR_DIACRITICS_HALLUCINATION` | Warning | OCR output diacritics density >0.06 for a source classified as unvocalized or partially_vocalized | Diacritics may be OCR-generated, not author-placed. Flag for downstream engines: these diacritics are not authoritative vocalization. |
| `NORM_TABLE_STRUCTURE_LOST` | Warning | Layout analysis detects a table but OCR linearization loses column-row associations | Set `content_flags.table_structure_preserved: false`. Downstream engines must not extract structured knowledge from this page's table. |
| `NORM_PDF_PARSE_FAILED` | Fatal | PDF library (PyMuPDF) returns error: corrupted PDF, password-protected, unsupported version | Reject source. Log the PDF library error message. [AUDIT FIX M-21] |
| `NORM_PDF_ARABIC_GARBLED` | Fatal | Text extracted from PDF but Arabic character ratio <0.30 for a source classified as Arabic, indicating text reversal or garbling | Fall back to OCR pipeline (Path B). If OCR also fails, reject source. [AUDIT FIX M-21] |
| `NORM_ENRICHMENT_WRITEBACK_FAILED` | Warning | Write-back to source metadata fails (file locked, corrupted, interface rejects update) | Normalization completes — the normalized package is valid without the write-back. Log the failure. A reconciliation check runs at next normalization of any source to retry failed write-backs. [AUDIT FIX M-23] |
| `NORM_VOLUME_NUMBER_UNPARSEABLE` | Warning | Filename stem cannot be parsed as a volume number (e.g., `المجلد_الأول.htm`, non-numeric stems) | Assign volume numbers sequentially by filename sort order. Log the unparseable filename. Human gate triggered to confirm volume assignment. [AUDIT FIX M-25] |
| `NORM_VOLUME_MISMATCH` | Warning | Duplicate volume numbers derived from filenames, or volume count disagrees with source metadata | Log both the derived and expected volume numbers. Human gate triggered. [AUDIT FIX M-25] |
| `NORM_ORIENTATION_UNCERTAIN` | Warning | Page orientation detection cannot distinguish 0-degree from 180-degree rotation (contradictory page-level signals) | Process with both orientations, compare OCR confidence scores, use the higher-confidence result. Log both results. If confidence difference <0.05, flag for human review. [AUDIT FIX M-26] |
| `NORM_DIACRITICS_ENTITY_CORRUPTION` | Fatal | Post-parse diacritic position comparison detects diacritics absent or substituted after HTML entity decoding | Abort normalization for this source. This indicates the HTML parser corrupted diacritical marks during entity resolution — a T-1 threat. [AUDIT FIX M-22] |

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
| `fingerprint_sd_threshold` | 2.0 | 1.0–4.0 | Standard deviation threshold for fingerprint outlier detection (§4.B.9). Lower = more sensitive. [AUDIT FIX M-06] |
| `fingerprint_min_words` | 5000 | 1000–20000 | Minimum words per layer for fingerprint validation. Below this, validation is skipped. [AUDIT FIX M-06] |

**Per-science configuration hooks (Level 3 / SCIENCE.md):**

Each science may customize:
- Structure discovery keyword weights (sciences like fiqh and usul use different heading conventions than nahw or sarf).
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

3. **Footnote type classification.** Code separates footnotes but does not classify them (tahqiq_editor/author_original/variant_reading/hadith_takhrij/cross_reference/biographical_note/linguistic_note/correction_note/general_commentary/unknown_footnote_type). [NOT YET IMPLEMENTED]

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

8. **Content flag correctness.** Verify that `has_verse` is true for known verse pages, `has_table` for known table pages, `has_quran_citation` for pages with Quran citations, `has_hadith_citation` for pages with hadith citations, `is_toc_page` for table of contents pages, `is_index_page` for index pages, and `is_blank` for blank pages.

9. **Error handling.** Test every error code in §7: provide unsupported format → `NORM_UNKNOWN_SOURCE_FORMAT`. Provide empty source → `NORM_MISSING_FROZEN`. Provide missing metadata → `NORM_MISSING_METADATA`. Provide output that fails schema → `NORM_SCHEMA_VIOLATION`. Simulate OCR failure → `NORM_OCR_FAILED`. Provide corrupted encoding → `NORM_ENCODING_ERROR`.

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

---

## Appendix A — Hardening Analysis

This appendix documents adversarial scenario testing, error cascade analysis, and invariant verification performed during the normalization engine hardening session. Each scenario identifies a concrete corruption path, evaluates existing defenses, and specifies any SPEC fixes applied.

### A.1 — Adversarial Scenarios

**Scenario 1: Bold-for-emphasis misinterpreted as layer boundary.**
Attack vector: A Shamela commentary export where the commentator (sharh author) uses `<b>` tags to emphasize hadith quotations or Quran verses within their own commentary text. The normalizer's Pass 5 interprets all bold spans as Layer 1 (matn) text.
What breaks: Hadith text and Quran citations within the sharh layer are misattributed to the matn author. The library records "ابن مالك said: «بُنِيَ الإِسْلَامُ عَلَى خَمْسٍ»" when this hadith quotation belongs to ابن عقيل's commentary.
Existing defenses: §4.A.5 step 6 checks that Layer 1 text is <40% of total — this catches bulk misattribution but not page-level emphasis-bold confusion.
SPEC fix applied: Added disambiguation rule to §4.A.5 typographic signals — bold spans covering individual words/phrases within longer sentences are treated as emphasis, not layer indicators. Added <5% and >60% bold-per-page thresholds.
Residual risk: LOW. The combination of span-length heuristic + page-level proportion check + fingerprint validation (§4.B.9) provides three independent defenses.

**Scenario 2: OCR produces valid but semantically wrong Arabic word.**
Attack vector: A scanned page contains the word حَرَّمَ (he prohibited). OCR reads it as حَرَمَ (he deprived/he was forbidden from) — both are valid Arabic morphemes. Dual-OCR mode may produce the same wrong reading because both engines share similar Arabic language models.
What breaks: The excerpting engine extracts "حَرَمَ X" (he was deprived of X) instead of "حَرَّمَ X" (he prohibited X). The synthesizer produces a fiqh entry with an inverted ruling. The owner learns the wrong legal opinion.
Existing defenses: §4.B.3 fidelity mapping flags low-confidence characters, but if both OCR engines agree on the wrong reading, confidence appears high. Morphological validation passes because both words are valid.
SPEC fix applied: Added "semantic confusion hazard" rule to §4.A.4 step 4 — when OCR confidence for any character is <0.90 AND substituting a visually similar letter produces a different valid Arabic word, the word is flagged as `semantic_confusion_risk` with both readings.
Residual risk: MEDIUM. The visual-similarity matrix catches the most dangerous confusions, but novel confusion patterns may exist. The fingerprint validation and downstream excerpting engine's context analysis provide additional but imperfect defense.

**Scenario 3: Shamela PageHead heading text injected into primary_text.**
Attack vector: A Shamela export where the PageHead element contains not just the chapter title but also authorial text (this occurs in approximately 3% of Shamela exports where the export engine incorrectly splits the text). If the normalizer includes PageHead text in primary_text, it duplicates text; if it excludes it, it loses the author's text.
What breaks: Either duplicate text (inflating the source) or lost text (silent data loss).
Existing defenses: §4.A.6 explicitly states PageHead is excluded from primary_text. §5 check 2 (coverage check) catches missing pages but not duplicated text within pages.
SPEC fix needed: None — the existing rule correctly excludes PageHead. However, the edge case of authorial text in PageHead is not addressed. Adding clarification: if PageHead text does NOT match any heading pattern (باب, فصل, etc.) and exceeds 100 characters, it should be logged as `NORM_SUSPICIOUS_PAGEHEAD` (warning) and treated as primary text that was incorrectly placed in the PageHead element, with the page flagged for human review.
Status: FIX APPLIED (see §7 error code addition below).

**Scenario 4: Division tree covers source but with overlapping ranges.**
Attack vector: The structure discovery algorithm detects two sibling divisions where Division A ends at unit_index 50 and Division B starts at unit_index 48 — overlapping by 2 units. This happens when Tier 2 keyword heuristics detect "باب" headings that are actually cross-references ("كما في باب كذا") rather than structural headings.
What breaks: The passaging engine, which uses division boundaries for passage creation, produces passages that belong to two divisions simultaneously. The taxonomy engine receives an excerpt with ambiguous division context.
Existing defenses: §5 check 5 explicitly validates "sibling divisions do not overlap in their page ranges." This catches the error at validation time.
Residual risk: LOW. The validation catches this before any corrupt data reaches disk.

**Scenario 5: Footnote reference marker in text with no corresponding footnote.**
Attack vector: A Shamela page contains "(3)" in the main text as part of a mathematical or classification pattern (e.g., listing three conditions: "(1) ... (2) ... (3) ..."), not as a footnote reference. There are only 2 actual footnotes on the page.
What breaks: Without the orphan reference rule, the normalizer might convert "(3)" to "⌜3⌝" and generate an empty or ghost footnote entry, confusing downstream engines.
Existing defenses: §4.A.2 Pass 2 strips footnote reference markers "only when a matching footnote exists on the same page." §5 check 6 handles orphan references. The `NORM_ORPHAN_FOOTNOTE_REF` error code preserves the marker as literal text.
Residual risk: LOW. The design correctly handles this case.

**Scenario 6: Unicode normalization silently strips diacritics.**
Attack vector: A Python string operation or library (e.g., `unicodedata.normalize('NFKD', text)`) is inadvertently applied during HTML parsing or text cleaning. This decomposes Arabic characters and may strip combining diacritical marks, changing "عِلْمٌ" to "علم" — silently destroying semantic information.
What breaks: The entire source loses diacritical marks. For vocalized scholarly texts (mutun), this destroys the primary scholarly value — the precise vocalization IS the knowledge.
Existing defenses: §4.A.8 states "No Unicode normalization. NFC, NFD, NFKC, NFKD normalization is NOT applied." §5 check 8 (diacritics preservation verification) performs character-class comparison and triggers `NORM_DIACRITICS_DRIFT` (fatal) if even one diacritic is lost.
Residual risk: VERY LOW. The fatal error on any diacritic loss is a strong defense. The check is per-page, catching the issue at the earliest possible point.

**Scenario 7: Atomic write procedure interrupted mid-swap.**
Attack vector: The normalizer completes writing to the temporary directory and begins the rename to the final path. The process crashes (OOM, disk full, power loss) after renaming the old `normalized/` to `normalized_prev_*` but before renaming the temp to `normalized/`.
What breaks: The source has no `normalized/` directory. Both `normalized_prev_*` and `normalized_tmp_*` exist. The source appears un-normalized. Re-running normalization would work, but if the system doesn't detect this state, the source is stuck.
Existing defenses: §4.A.2 defines the atomic write procedure with temp directory → verify → rename. The `NORM_WRITE_FAILED` error code covers rename failures.
SPEC fix needed: Add a recovery rule: at normalizer startup, if a `normalized_tmp_*` directory exists but no `normalized/` directory, AND a `normalized_prev_*` exists, the engine should: (a) attempt to validate the temp directory (JSON parse, schema check), (b) if valid, complete the interrupted rename, (c) if invalid, restore from `normalized_prev_*` and log the recovery. This ensures interrupted writes are recoverable.
Status: RECOVERY RULE ADDED to §4.A.2.

**Scenario 8: Layer detection inversion — all matn classified as sharh and vice versa.**
Attack vector: A Shamela commentary where the export convention is inverted — the sharh text is bold and the matn text is regular (this occurs in some older Shamela versions where the export template is wrong). The normalizer's Pass 5 applies the standard "bold = matn" heuristic and inverts ALL layer attributions.
What breaks: Every character in the source has the wrong author_canonical_id. The entire source's knowledge is misattributed. This is the highest-impact single failure the normalizer can produce.
Existing defenses: §4.A.5 step 6 checks that Layer 1 is <40% — catches inversion because the sharh (now labeled matn) would be >60%. §4.B.9 fingerprint validation catches the inversion at a statistical level — the "matn" fingerprint would have sharh-like properties.
SPEC fix needed: Add a SPECIFIC inversion detection rule to §4.B.9 validation step 1: if the "matn" layer fingerprint has sentence_length.mean > 22 AND connective_frequency > 0.08 AND the "sharh" layer fingerprint has sentence_length.mean < 16 AND connective_frequency < 0.06, flag `NORM_LAYER_FINGERPRINT_INVERSION` (warning severity) and trigger human gate review. Do not auto-correct — the human decides whether the labels should be swapped.
Status: INVERSION THRESHOLDS ADDED to §4.B.9 validation.

**Scenario 9: Continuity detection falsely claims mid_sentence at chapter boundary.**
Attack vector: A page ends with a sentence that has no terminal punctuation because the author uses a literary style without periods (common in classical Arabic). The next page begins a new chapter (باب). The continuity detector sees no terminal punctuation → classifies as `mid_sentence`.
What breaks: The passaging engine refuses to create a passage boundary at this chapter boundary because it believes the sentence continues. Passages span chapter boundaries incorrectly.
Existing defenses: §4.B.8 detection algorithm checks structural markers: if a heading is detected at or near the boundary, the classification is `section_break` (confidence ≥ 0.85). This overrides the punctuation-based `mid_sentence` signal.
Residual risk: LOW — but only if structure discovery successfully detects the heading. If the heading is a Tier 3 (LLM-detected) heading with confidence `low`, the override may not trigger reliably.
SPEC fix needed: Add explicit priority rule — structural heading detection at a boundary always overrides punctuation-based continuity analysis, regardless of heading confidence level. Even a `low`-confidence heading at a boundary should produce `section_break` with the heading's confidence, not `mid_sentence`.
Status: PRIORITY RULE ADDED to §4.B.8.

**Scenario 10: Discourse flow markers inside quotations produce false argument structure.**
Attack vector: The text reads "قال الشافعي: والصحيح أنه يجب الوضوء، واعترض عليه بعض أصحابنا بأن..." — the author is QUOTING another scholar who made an argument. The discourse markers "والصحيح" and "واعترض" appear inside the quotation, but the detector interprets them as the source author's own argument.
What breaks: The discourse flow map shows a `preferred` segment and an `objection` segment that are actually quoted content. The excerpting engine may treat the quoted argument as a standalone scholarly position.
Existing defenses: §4.B.10 edge cases mention "markers inside quotations... annotated as `quoted_discourse`" — quotation detection using guillemets and "قال فلان:" patterns.
Residual risk: MEDIUM. Quotation detection relies on explicit markers (guillemets, "قال"). Implicit quotation (where the author paraphrases another scholar's argument without explicit markers) is not detectable by patterns alone. LLM refinement (step 3) may catch some implicit quotations.

**Scenario 11: Owner's study note processed as scholarly source.**
Attack vector: The owner submits a typed study note that contains "قال ابن قدامة: يجوز المسح على الخفين" — the owner is taking notes about what a scholar said. The normalizer treats this as the owner's original content, but the excerpting engine later extracts it as the owner's opinion rather than a quote from Ibn Qudamah.
What breaks: The library attributes a scholarly position to the owner instead of the original scholar.
Existing defenses: §4.A.4d specifies `layer_type: "owner_content"` for all owner-authored input. The excerpting engine should recognize this layer type and handle quotations within owner notes differently. However, the SPEC does not explicitly require the owner content normalizer to detect embedded scholarly quotations.
SPEC fix needed: Add a behavioral rule to §4.A.4d: owner content normalizer MUST scan for embedded scholarly quotation patterns ("قال فلان:", explicit scholar attribution followed by content) and mark these as `quoted_scholarly_content` in content_flags. The excerpting engine uses this flag to trace the quotation to the referenced scholar rather than attributing it to the owner.
Status: FLAG ADDED to §4.A.4d.

**Scenario 12: Dual-OCR produces aligned garbage on a severely degraded page.**
Attack vector: A page is so degraded (faded ink, paper damage) that BOTH OCR engines produce plausible-looking but completely wrong Arabic text (real Arabic words in wrong order, or real words from a different context). Character-level alignment shows agreement → high fidelity score.
What breaks: A page of essentially random Arabic text enters the library with `text_fidelity: "high"` — the worst possible outcome, because high fidelity means downstream engines trust it completely.
Existing defenses: §4.A.4 step 8 computes fidelity from OCR confidence, but if both engines are confidently wrong, fidelity is high. §5 check 3 flags pages with <70% Arabic characters, but the text IS Arabic — just wrong.
SPEC fix needed: Add a coherence check to §5: for OCR-processed pages, compute a sentence-level coherence score using an LLM (prompt: "Is this Arabic text coherent? Rate 1-5."). Pages scoring ≤2 receive fidelity downgrade to `low` regardless of OCR agreement. This catches the "confident garbage" scenario.
Status: COHERENCE CHECK ADDED to §5.

### A.2 — Error Cascade Traces

**Cascade 1: Footnote separator misdetection → footnote text injected into primary_text → false scholarly claims.**

Step 1: The Shamela export uses a non-standard footnote separator (e.g., `<hr width='90'>` instead of `<hr width='95'>`). The normalizer's Pass 2 fails to detect the separator.
Step 2: The entire page content (including footnote text) is treated as primary text. `NORM_FOOTNOTE_SEPARATOR_ABSENT` (info) is logged.
Step 3: The footnote text — which contains the editor's scholarly commentary — is now part of the primary text. It is attributed to the source author's layer (matn or sharh based on surrounding context).
Step 4: The excerpting engine extracts the editor's commentary as the original author's opinion: "ابن قدامة said: 'الصواب: المتيمم بدل المتوضئ'" — but this is the EDITOR's correction note, not ابن قدامة's text.
Step 5: The synthesizer produces an entry attributing the correction to ابن قدامة. The owner learns a false scholarly position.

Cascade defense analysis:
- Step 1 detection: `NORM_FOOTNOTE_SEPARATOR_ABSENT` is logged but at `info` severity. If >30% of pages trigger this, the `no_footnote_apparatus` flag is set.
- Step 3 defense: The text_layers attribution would be based on content inference. The editor's correction text has a different register from the author's text (modern scholarly language vs. classical). §4.B.9 fingerprint validation should flag this as an anomaly IF the editor's text is long enough.
- Step 4 defense: The excerpting engine should notice that the "author's" text contains modern scholarly language inconsistent with the author's period.
- SPEC fix: Elevate `NORM_FOOTNOTE_SEPARATOR_ABSENT` from `info` to `warning` when the source metadata indicates a tahqiq edition (tahqiq editions ALWAYS have footnotes). If the source is a tahqiq edition AND >10% of pages have no separator, trigger human gate: the separator pattern may be non-standard and needs manual identification.
Status: ERROR SEVERITY UPGRADED for tahqiq editions.

**Cascade 2: Page order conflict in image set → wrong unit_index sequence → cross-page continuity errors → broken passage boundaries.**

Step 1: The owner photographs a book but accidentally photographs page 45, then 43, then 44, then 46. Filenames are sequential: IMG_001 through IMG_004.
Step 2: The normalizer uses filename order as authoritative (§4.A.4 rule). Content units are: unit_index 0 = page 45, unit_index 1 = page 43, unit_index 2 = page 44, unit_index 3 = page 46.
Step 3: The OCR detects page numbers on the images: 45, 43, 44, 46. This disagrees with filename order. `NORM_PAGE_ORDER_CONFLICT` is triggered, and a human gate is created.
Step 4: BUT if OCR fails to detect page numbers (e.g., the page numbers are in a faded footer), the conflict is never detected. Filename order is used silently.
Step 5: Cross-page continuity at unit_index 0→1 (page 45→43) detects `mid_sentence` because the text on page 43 begins with a lowercase connective that continues from page 42, not page 45. The continuity signal is wrong — these pages are NOT adjacent.
Step 6: The passaging engine treats pages 45, 43, 44, 46 as a continuous sequence and creates a passage spanning all four — producing nonsensical text.

Cascade defense analysis:
- Step 3 is the primary defense: human gate review of page order conflict.
- Step 4 is the gap: if OCR can't read page numbers, the conflict is invisible.
- SPEC fix: Add a secondary ordering check: when continuity analysis (§4.B.8) produces `unknown` or low-confidence results for >30% of boundaries in an image-sourced source, log `NORM_ORDERING_UNCERTAIN` (warning) and flag for human review. High rates of continuity uncertainty in image sources may indicate misordered pages.
Status: SECONDARY ORDERING CHECK ADDED.

### A.3 — KNOWLEDGE_INTEGRITY.md Invariant Verification

**Invariant 1: Frozen sources are immutable.**
SPEC guarantee: The normalization engine reads from `library/sources/{source_id}/frozen/` and never writes to it. §4.A.2 specifies "frozen source directory path" as input. The atomic write procedure writes ONLY to `normalized/` and `normalized_tmp_*/` directories. No SPEC rule ever references writing to the frozen directory.
Verification: PASS. No code path in the normalization SPEC can modify frozen files.

**Invariant 2: Primary text is never modified.**
SPEC guarantee: §4.A.8 states "Diacritics preservation is absolute" and "No Unicode normalization." §5 check 8 performs character-class comparison between source text and output primary_text for non-OCR sources, triggering `NORM_DIACRITICS_DRIFT` (fatal) on any discrepancy.
Adversarial test: If a Python library applies NFKD normalization during HTML parsing, diacritics (combining characters) would be decomposed and potentially lost. §5 check 8 catches this because the diacritic character counts would differ.
Verification: PASS. The fatal check on diacritic loss is the strongest defense.
Note: For OCR sources, the "primary text" IS the OCR output — there is no pre-OCR digital text to compare against. The frozen source is the image, and the OCR output is the normalizer's best reconstruction. This is inherent to OCR processing and is captured in the text_fidelity score.

**Invariant 3: Every claim is traceable.**
SPEC guarantee: Every content unit carries `source_id`, `unit_index`, and `physical_page` — together forming a citation chain back to the frozen source. Every text_layer segment carries `author_canonical_id`. Every footnote carries `footnote_type` and type-specific structured data. Discourse flow segments carry `detection_method` and `marker_text` showing how they were detected.
Verification: PASS. The metadata chain is complete from the normalization engine's perspective.

**Invariant 4: Errors fail loudly.**
SPEC guarantee: §7 defines 22 error codes with explicit severity levels. Fatal errors abort normalization. Warning errors log and may trigger human gates. Info errors log. No error code has a "silently ignore" recovery action. §5 check 7 (unit_index integrity) is fatal, catching even single-unit data loss.
Adversarial test: What if the HTML parser silently skips a malformed `<div class='PageText'>` that doesn't close properly? §5 check 2 (coverage check) catches this: for Shamela sources, the normalizer counts input PageText divs in Pass 1, and the final content unit count must match (minus explicitly skipped pages).
Verification: PASS. The coverage check for deterministic source types is the key defense against silent data loss.

**Invariant 5: Human gates are not optional.**
SPEC guarantee: §5 Layer 3 defines 5 specific conditions triggering human gate review. These are triggered by validation failures, not by configuration. The atomic write procedure does not bypass human gates — it ensures the normalized package is valid, but human gates are separate checkpoints that prevent further processing.
Verification: PASS. No SPEC rule allows bypassing human gate conditions.

**Invariant 6: Metadata flows forward, never backward-deleted.**
SPEC guarantee: §3 output contract lists specific metadata fields. The manifest schema includes ALL upstream metadata via `source_id` reference. Enrichment write-backs (§4.B.2 format override, §4.B.5 census) ADD metadata to the source record — they never remove existing fields. §7 has no error code whose recovery action is "delete metadata."
SPEC fix applied: Added `metadata_history` preservation rule to Pass 6 enrichment write-backs — when a normalizer-discovered value overrides a source engine value (e.g., structural_format), the original value is preserved in `metadata_history`, not deleted.
Verification: PASS after fix.

### A.4 — Multi-Layer Misattribution Attack Vectors

These scenarios target §4.A.5 (layer detection) and §4.B.9 (fingerprint validation) — the highest-integrity-risk operations.

**Attack 1: Gradual layer signal degradation across a source.**
Vector: A Shamela commentary export where bold formatting is present on pages 1-300 (properly marking matn) but absent on pages 301-600 (due to a formatting bug in the Shamela export for later volumes). The normalizer's Pass 5 uses bold for high-confidence layer detection on early pages but falls back to content-based inference on later pages. Content-based inference (§4.B.1) produces lower-confidence boundaries with some errors.
What breaks: Pages 1-300 have correct layer attribution (confidence 0.85-0.92). Pages 301-600 have degraded attribution (confidence 0.55-0.70) with ~15% error rate. The overall source appears mostly correct, so no aggregate alarm triggers.
§4.B.9 defense: The fingerprint validation computes a GLOBAL fingerprint from all 600 pages. If pages 301-600 have 15% misattribution, the global fingerprint is diluted but still dominated by the 85% correct text. The page-level outlier detection (step 2) should catch the specific pages where misattribution occurs — the local fingerprint for misattributed pages diverges from the global.
Assessment: The fingerprint's Mahalanobis distance threshold (>2.5 std dev) may not catch pages where the misattribution is partial (e.g., one short matn segment attributed to sharh on a page where the rest is correct). These pages would have a mixed local fingerprint that might not diverge enough.
SPEC fix: Add to §4.B.9 validation step 2: when computing local fingerprints, compute them PER LAYER SEGMENT on each page, not per page aggregate. A single misattributed segment of 50 words within a 500-word page would be diluted in a page-aggregate fingerprint but detectable in a per-segment fingerprint. However, this increases computation by ~5x — mark as configurable, default ON for sources with >50 pages.
Status: PER-SEGMENT FINGERPRINT OPTION ADDED.

**Attack 2: Cross-source fingerprint poisoning.**
Vector: The first commentary entered into the library for a given matn author has ~25% layer detection errors (25% of matn text is actually sharh). The global fingerprint for this matn author is computed from this error-contaminated data. When a second commentary by the same matn author is processed, the cross-source comparison (§4.B.9 step 3) compares against the contaminated reference fingerprint — and the contamination propagates. The second source's layer detection is validated against wrong baselines.
What breaks: A systematic bias enters the library's author fingerprint database. All future sources by this matn author are validated against contaminated fingerprints, potentially confirming wrong attributions.
§4.B.9 defense: Step 3 says "Agreement increases confidence; disagreement triggers a warning." But if the reference fingerprint is itself wrong, agreement is a false positive.
SPEC fix: Add a minimum-sources rule: cross-source fingerprint comparison (step 3) is only activated when ≥2 independent sources exist for the same matn author. For the first source, the fingerprint is stored but NOT used as a reference baseline. Only after a second source confirms the fingerprint (within statistical bounds) does the author-level baseline become authoritative. Additionally, single-layer works by the same author (where layer detection is trivially correct) always take precedence as reference fingerprints over multi-layer works.
Status: MINIMUM-SOURCES RULE ADDED.

**Attack 3: Hashiyah-on-sharh triple layer misattribution.**
Vector: A three-layer source (matn + sharh + hashiyah) where the hashiyah author extensively quotes the sharh author's explanations before adding their own marginalia. The layer detection correctly identifies matn (bold text) but cannot distinguish sharh quotations within the hashiyah from the hashiyah author's own commentary — both are non-bold prose at the same visual level.
What breaks: The hashiyah layer absorbs quoted sharh text. The sharh author's explanations are attributed to the hashiyah author. The synthesizer cites "قال ابن قاسم:" (hashiyah author) for text that was actually written by البهوتي (sharh author).
§4.B.9 defense: With 3 layers, the fingerprint validation computes 3 fingerprints. If quoted sharh text is attributed to the hashiyah layer, the hashiyah fingerprint would contain text with sharh-like properties (shorter sentences? no — the quoted text has sharh properties). However, if the hashiyah author's own style is different from the sharh author's style, the mixed fingerprint would show anomalies.
Assessment: This is the hardest multi-layer case. The fingerprint provides some defense, but quotation within the hashiyah may be extensive enough that the hashiyah fingerprint genuinely reflects a mix of styles.
SPEC fix: Add to §4.A.5: for hashiyah sources with 3 layers, the normalizer explicitly tracks quotation markers within the hashiyah layer. When the hashiyah text contains "قال الشارح:" or "وعبارته:" (quotation of the sharh author), the text following these markers until the next hashiyah author signal is attributed to the sharh layer, not the hashiyah layer. This pattern-based quotation detection supplements the style-based inference.
Status: QUOTATION DETECTION RULE ADDED for hashiyah layers.

### A.5 — OCR Corruption Scenarios

**OCR Scenario 1: Diacritic hallucination in unvocalized text.**
Vector: A scanned page of an unvocalized fiqh text is processed by Mistral OCR 3. The OCR engine, trained on mixed vocalized/unvocalized Arabic, "hallucinates" diacritics that don't exist in the source image — adding fatha, kasra, or damma to words that the original printing left unvocalized. The hallucinated diacritics happen to be plausible Arabic but may not match the correct vocalization.
Propagation: The normalizer records the hallucinated diacritics in primary_text. For the excerpting engine and synthesizer, the text appears vocalized. If the hallucinated diacritics are wrong (e.g., يَحرُمُ instead of يُحَرِّمُ — wrong verb form), the owner learns incorrect Arabic grammar for a legal ruling.
Detection: §5 check 8 (diacritics preservation) only applies to digital sources where the source text is available. For OCR sources, the OCR output IS the baseline.
SPEC fix: Add a diacritics consistency check for OCR sources: compare the diacritics density of the OCR output against the source metadata's expected diacritization level. If the source is classified as `unvocalized` or `partially_vocalized` in the source metadata, but the OCR output has diacritics density >0.06, flag `NORM_OCR_DIACRITICS_HALLUCINATION` (warning). The flag tells downstream engines: these diacritics may be OCR-generated, not author-placed, and should not be treated as authoritative vocalization.
Status: NEW ERROR CODE AND CHECK ADDED.

**OCR Scenario 2: Table structure destroyed by OCR linearization.**
Vector: A scanned page contains a table of madhahib positions (common in comparative fiqh works):

```
| المسألة | الحنفي | المالكي | الشافعي | الحنبلي |
| طهارة الماء | يجوز | لا يجوز | يجوز بشرط | يجوز |
```

Mistral OCR 3 linearizes this as: "المسألة الحنفي المالكي الشافعي الحنبلي طهارة الماء يجوز لا يجوز يجوز بشرط يجوز" — losing the column-to-row associations.
Propagation: The normalizer's content flag detects `has_table: true` (from layout analysis), but the linearized text in primary_text has lost the structural relationships. The excerpting engine extracts "يجوز" and "لا يجوز" without knowing WHICH school said what. The synthesizer may randomly associate rulings with schools.
Detection: §4.B.2 (structural format auto-detection) detects `tabular_khilaf` from patterns — but the OCR linearized text may not preserve the patterns if columns are merged.
SPEC fix: Add to §4.A.4: when Mistral OCR or Baseer detects table elements in the layout analysis, the normalizer extracts the table as structured data (`table_data` field in the content unit) in addition to the linearized text. The structured data preserves row/column associations. If structural extraction fails (OCR can't determine column boundaries), the page is flagged as `NORM_TABLE_STRUCTURE_LOST` (warning) and the content unit's `content_flags.table_structure_preserved` is set to `false`, telling downstream engines not to extract structured knowledge from this page's table.
Status: TABLE STRUCTURE PRESERVATION RULE ADDED.

### A.6 — §4.B.8/§4.B.10 Interaction Verification

**Test case: Continuity says mid_argument, discourse says argument_cycle_complete.**
Scenario: Page 45 ends with "ولنا حديث ابن عباس:" (evidence chain opening). The continuity detector correctly identifies `mid_argument`. However, the discourse flow annotation on page 45 happens to detect a complete argument cycle in the FIRST part of the page (ruling → evidence → preferred), and then the final evidence chain starts a NEW argument cycle. The `argument_cycle_complete` field reports `true` for the completed first cycle.
Resolution: The cross-validation rule (Pass 6 step 9) correctly resolves this: continuity says `mid_argument` for the page boundary, so the discourse flow's `argument_cycle_complete` is set to `false` for the page as a whole. The completed first cycle is still detectable from the segment array (the `preferred` segment closing the first cycle appears before the final evidence segment that opens the second).
Verification: PASS. The cross-validation rule handles multi-cycle pages correctly because continuity applies to the PAGE BOUNDARY, and any open cycle at the boundary overrides the overall `argument_cycle_complete`.

**Test case: Discourse says incomplete, continuity says section_break.**
Scenario: Page 90 contains the start of an argument (ruling + evidence, no preferred/conclusion yet). But page 91 begins a new chapter (باب). The author left the argument unresolved at the chapter boundary.
Resolution: The updated cross-validation rule (Fix 5) handles this: continuity's `section_break` takes precedence for the BOUNDARY, while discourse's `cycle_missing_elements: ["preferred"]` is preserved. The new `cycle_truncated_by_structure: true` flag distinguishes this from a cycle that continues on the next page. The passaging engine correctly creates a passage boundary at the chapter heading. The excerpting engine knows this is an incomplete argument and can note in the excerpt metadata that the author's conclusion is absent.
Verification: PASS after fix.

**Test case: Both signals are unknown/absent.**
Scenario: A very short page (80 characters) near a volume boundary. Discourse flow is null (<100 characters rule). Continuity is `division_break` (volume boundary).
Resolution: No conflict. Discourse is simply absent. Continuity correctly marks the volume boundary.
Verification: PASS. No interaction to validate.

### A.7 — Pass 6 Processing Order Verification

The 11 steps in Pass 6 must execute in dependency order with no circular dependencies.

Dependency graph:
1. Content flagging (§4.A.9) → no dependencies
2. Structural format auto-detection (§4.B.2) → depends on content units (Pass 1-5 output)
3. Footnote apparatus classification (§4.B.4) → depends on footnotes from Pass 2
4. Content census (§4.B.5) → depends on content_flags from step 1
5. Tahqiq apparatus topology (§4.B.7) → depends on footnote classification from step 3
6. Authorial voice fingerprint (§4.B.9) → depends on census verse_ratio from step 4
7. Cross-page continuity (§4.B.8) → depends on content units (Pass 1-5 output)
8. Scholarly discourse flow (§4.B.10) → depends on continuity from step 7
9. Cross-validation → depends on continuity (step 7) and discourse (step 8)
10. Fine-grained fidelity mapping (§4.B.3) → depends on OCR output (Pass 1-5)
11. Scholarly text layer intelligence (§4.B.1) → depends on Pass 5 layer detection

Circular dependency check:
- Step 6 (fingerprint) depends on step 4 (census). Step 4 depends on step 1 (flags). No cycle.
- Step 8 (discourse) depends on step 7 (continuity). Step 7 has no dependency on step 8. No cycle.
- Step 9 (cross-validation) depends on steps 7 and 8. Neither depends on step 9. No cycle.
- Step 5 (topology) depends on step 3 (footnotes). Step 3 has no dependency on step 5. No cycle.

Verification: PASS. No circular dependencies. The ordering is valid.

Note: Steps 7 and 10 could execute in parallel (no mutual dependencies). Steps 1 and 2 and 3 could execute in parallel. This is an implementation optimization, not a SPEC requirement.

### A.8 — Error Code Trigger Verification

Every §7 error code must have a concrete trigger scenario — no theoretical-only codes.

| Code | Concrete Trigger | Verified |
|------|-----------------|----------|
| `NORM_UNKNOWN_SOURCE_FORMAT` | Source metadata says `source_format: "latex"` — not in type map | ✓ |
| `NORM_MISSING_FROZEN` | Frozen directory exists but is empty (all files deleted) | ✓ |
| `NORM_MISSING_METADATA` | metadata.json has invalid JSON (syntax error) | ✓ |
| `NORM_SCHEMA_VIOLATION` | Content unit has `unit_index: -1` (fails ge=0 constraint) | ✓ |
| `NORM_OCR_FAILED` | Mistral OCR API returns 500 error on degraded page | ✓ |
| `NORM_ENCODING_ERROR` | Shamela export saved in Windows-1256, not UTF-8 | ✓ |
| `NORM_LOW_FIDELITY` | iPhone photos of a faded manuscript: 30% of pages score <0.80 | ✓ |
| `NORM_LAYER_UNCERTAIN` | Pre-tahqiq print with no bold/brackets: 40% of pages below medium | ✓ |
| `NORM_SPARSE_STRUCTURE` | A 200-page tabular fatwa collection with no باب/فصل headings | ✓ |
| `NORM_FORMAT_MISMATCH` | Source engine says "prose" but normalizer detects Q&A (40% match) | ✓ |
| `NORM_PAGE_COUNT_MISMATCH` | Shamela export has 500 PageText divs but normalizer produces 482 units | ✓ |
| `NORM_DUPLICATE_PAGES` | Shamela export: vol 3 page 12 and vol 2 page 12 have same page_number_int | ✓ |
| `NORM_PARTIAL_PAGE` | iPhone photo captures only top 60% of a page (finger visible at bottom) | ✓ |
| `NORM_OCR_API_RATE_LIMIT` | Mistral OCR returns 429 during batch processing of 1000 pages | ✓ |
| `NORM_WRITE_FAILED` | Disk full during atomic write to temp directory | ✓ |
| `NORM_UNIT_INDEX_VIOLATION` | Bug in page numbering logic produces [0, 1, 1, 3] (duplicate 1, missing 2) | ✓ |
| `NORM_NO_TEXT_LAYER` | PDF is a scanned image with no embedded text; Docling extracts <100 chars | ✓ |
| `NORM_PAGE_ORDER_CONFLICT` | Image filenames: 001→045, 002→043, 003→044 (OCR disagrees with filenames) | ✓ |
| `NORM_FOOTNOTE_SEPARATOR_ABSENT` | Shamela page uses non-standard `<hr width='80'>` separator | ✓ |
| `NORM_DIACRITICS_DRIFT` | Python library applies NFC normalization during HTML entity decoding | ✓ |
| `NORM_CONTINUITY_INCONSISTENT` | `mid_sentence` but text ends with period `.` | ✓ |
| `NORM_DISCOURSE_INCONSISTENT` | Discourse segments [0-50] and [40-100] overlap | ✓ |
| `NORM_FINGERPRINT_INVALID` | `total_words_attributed: 0` but `fingerprint_reliability: "normal"` | ✓ |
| `NORM_ORPHAN_FOOTNOTE_REF` | Text contains "(3)" but only 2 footnotes on page | ✓ |

All 24 error codes have concrete trigger scenarios. No theoretical-only codes.

### A.9 — Self-Audit Results

**Defect 1 (Structural — Criterion #1 Zero Ambiguity).** §4.A.5 conservative default said "when confidence is low" without a numeric threshold. An implementing agent would need to decide what "low" means.
Fix: Replaced with "when confidence for a text region is below 0.50."

**Defect 2 (Completeness — Criterion #10 Full Input Coverage).** §4.B.4 footnote classification assumed each footnote has exactly one type. Mixed-type footnotes (containing both cross_reference and hadith_takhrij content) had no defined behavior.
Fix: Added mixed-type footnote rule with `secondary_types` field. Updated contracts.py with `SecondaryFootnoteType` model. Updated concrete example to show mixed-type classification.

**Defect 3 (Completeness — Criterion #12 Enumerated Edge Cases).** §4.B.8/§4.B.10 cross-validation rule specified what happens when continuity overrides discourse, but not the reverse case (discourse incomplete at a structural boundary). The reverse case IS a real scenario — authors do leave arguments unresolved at chapter boundaries.
Fix: Added reverse interaction rule with `cycle_truncated_by_structure` flag. Updated contracts.py.

**Defect 4 (Design — Criterion #15 Best-Known Design).** §4.A.5 typographic signals treated all `<b>` tags as layer indicators, ignoring the common use of bold for emphasis within commentary text (e.g., bolding hadith text, Quran quotes, or important terms).
Fix: Added bold-for-emphasis disambiguation rule with span-length heuristic and per-page proportion thresholds.

**Defect 5 (Completeness — Criterion #11 Exhaustive Error Handling).** OCR-processed text could contain valid Arabic words that are semantically wrong (visually similar letter substitutions). No error handling existed for this scenario.
Fix: Added "semantic confusion hazard" rule to §4.A.4 with visual-similarity matrix and `semantic_confusion_risk` fidelity map entries.

**Defect 6 (Structural — Criterion #8 Accurate State).** The `DiscourseSegmentType` enum in contracts.py was missing the `ELABORATION` value defined in the SPEC §4.B.10 taxonomy table. The `detection_method` field in `DiscourseSegment` was an untyped string instead of an enum, and `fingerprint_reliability` in `LayerFingerprint` was similarly untyped.
Fix: Added `ELABORATION` to enum. Created `DiscourseDetectionMethod` and `FingerprintReliability` enums. Added `model_validator` constraints to `DiscourseFlow` and `LayerFingerprint`.

---

## 9.1 Contract Alignment Required

[AUDIT FIX — Category 2: Phantom Metadata]

The following fields are referenced in the SPEC but do not exist in `contracts.py` or upstream contracts. Before implementing the sections that reference them, either add the fields to contracts.py or simplify the SPEC to use existing fields. Each item lists the SPEC section, the phantom field, and the recommended resolution.

| # | Defect | SPEC Reference | Phantom Field | Recommended Resolution |
|---|--------|---------------|---------------|----------------------|
| M-09 | §5 check 14 | `unvocalized` / `partially_vocalized` classification | `vocalization_level` on source engine `SourceMetadata` | Add `vocalization_level: Literal["fully_vocalized", "partially_vocalized", "unvocalized", "unknown"] = "unknown"` to `SourceMetadata`. Alternatively, infer vocalization from the first N pages of OCR output during normalization and remove the upstream dependency. |
| M-10 | §4.A.4d | `has_embedded_scholarly_quotation` in `content_flags` | `has_embedded_scholarly_quotation: bool` on `ContentFlags` | Add `has_embedded_scholarly_quotation: bool = False` to `ContentFlags`. |
| M-11 | §7 + §4.A.6 | `table_structure_preserved` in `content_flags`, `table_data` in content unit | `table_structure_preserved: bool` on `ContentFlags`, `table_data: Optional[list]` on `ContentUnit` | Add both fields to their respective models in contracts.py. |
| M-12 | §4.A.4d | `layer_type: 'owner_content'` | `OWNER_CONTENT` value in `LayerType` enum | Add `OWNER_CONTENT = "owner_content"` to `LayerType`. |
| M-13 | §4.B.6 / passaging §2 | `markers` and `confidence` vs `detection_confidence` | `LayerMapEntry` field name alignment | Rename `detection_confidence` to `confidence` in `LayerMapEntry`. Add `markers: list[str] = []` field. Coordinate with passaging engine SPEC. |
| M-14 | §4.A.6 | 14 fields in SPEC example vs 7 fields in `DivisionNode` | `div_id`, `type`, `digestible`, `editor_inserted`, `page_hint_start`, `page_hint_end`, `child_div_ids` missing from model | [OPEN: Expand `DivisionNode` to 14 fields (matching SPEC example at line 593) OR simplify SPEC to 7 fields? Decide during implementation — the SPEC example is more expressive but the model is simpler. Recommended: expand the model.] |
| M-18 | §4.B.6 | `ocr_engine` field claimed as "already present in fidelity data" | `ocr_engine: Optional[str]` on `TextFidelity` | Add `ocr_engine: Optional[str] = None` to `TextFidelity`. Remove the phrase "already present" from line 1002. |
| M-20 | §4.B.10 | `quoted_discourse` annotation for markers inside quotations | `QUOTED_DISCOURSE` in `DiscourseDetectionMethod` OR `is_quoted: bool` on `DiscourseSegment` | Add `is_quoted: bool = False` to `DiscourseSegment`. Markers inside quotations set `is_quoted: True` and retain their original `detection_method`. This is simpler than a new enum value and preserves the detection method information. |
