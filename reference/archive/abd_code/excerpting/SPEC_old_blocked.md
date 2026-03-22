# Excerpting Engine — محرك الاستخراج — Specification

## 1. Purpose and Scope

The excerpting engine is the third engine in the pipeline and the most complex. It receives normalized packages from the normalization engine and produces draft excerpts — self-contained teaching units enriched with scholarly metadata, ready for taxonomy placement and synthesis. Every knowledge product in the library — every taxonomy leaf, every synthesized entry, every study path recommendation — originates from an excerpt produced by this engine.

**What this engine does:**
- Assembles cross-page text from per-page content units using boundary continuity signals, producing processable chunks within division boundaries (Phase 1)
- Maps divisions to right-sized chunks: passes through divisions ≤5000 Arabic words, splits oversized divisions at structural markers, merges tiny adjacent divisions <50 words (Phase 1)
- Applies format-specific chunk strategies for verse-commentary, Q&A, masala-block, and dictionary sources (Phase 1)
- Classifies text segments within each chunk by scholarly function using a two-phase LLM approach validated on 23 divisions across 7 formats (Phase 2)
- Groups classified segments into self-contained teaching units — the smallest scholarly segments a student can learn from independently (Phase 2)
- Enriches each teaching unit with author attribution, school classification, topic proposal, evidence references, self-containment scoring, and human gate triggers (Phase 3)
- Produces a draft excerpt stream that the taxonomy engine consumes for placement

**What this engine absorbs from the original architecture:**
- **Passaging** (as Phase 1 deterministic preprocessing). The passaging engine's core responsibilities — cross-page text assembly, division-to-chunk mapping, format-specific boundary detection — are Phase 1 operations inside the excerpting engine. This absorption was validated by the Shamela division analysis (2,065,297 divisions: 96.8% ≤2000w, 99.1% ≤5000w — the deterministic preprocessing is ~500-800 lines of unit-testable code, not engine-worthy).
- **Atomization** (merged into Phase 2 LLM extraction). The Architecture C experiment validated that an LLM can directly identify teaching units from division-level text without a separate atomization step. The two-phase approach (classify segments by scholarly function, then group into teaching units) subsumes atomization's scholarly function classification.

**What is NOT this engine's responsibility:**
- Source acquisition, identification, metadata extraction — source engine
- Format-specific text normalization, structure discovery, layer detection — normalization engine
- Taxonomy tree management, excerpt placement, coverage analytics — taxonomy engine
- Entry generation, scholarly landscape construction, synthesis — synthesis engine
- Scholar authority management — source engine (primary); the excerpting engine enriches with per-excerpt attribution but does not manage the scholar registry

**Phase classification:** Phase 2 (source-agnostic, below the normalization boundary). The excerpting engine sees only the universal normalized schema — never raw source files, never format-specific markup. If a developer adds a new source type, they write a new normalizer; the excerpting engine requires zero changes.

**The three internal phases:**

| Phase | Nature | Primary responsibility | Validated by |
|-------|--------|----------------------|-------------|
| Phase 1 | Deterministic | Cross-page assembly, chunk creation, format-specific boundaries | Shamela division analysis (2M divisions) |
| Phase 2 | LLM-powered | Segment classification, teaching unit grouping | Architecture C (10 divisions, 5 genres) + Format diversity (13 divisions, 4 formats) |
| Phase 3 | LLM-powered + deterministic | Attribution, classification, evidence, topic, self-containment | To be validated during engine evaluation |

**D-011: Teaching units are contained within chunk boundaries.** A teaching unit never spans two chunks. This is STRONGER than the original design (excerpt within passage), because chunks derive from the author's own division structure — the most natural boundary in the text. D-011 was empirically validated: cross-boundary context (Approach C in the Architecture C experiment) showed no measurable improvement over boundary-respecting extraction (Approach B) on 10 divisions.

**Normalization boundary relationship:** The normalization engine provides structure discovery (division tree, heading hierarchy), per-page content with layer attribution, footnote apparatus, boundary continuity signals, and content flags. The excerpting engine uses that structure to create processing chunks and extract teaching units. The distinction: normalization discovers the source's OWN structure; the excerpting engine creates right-sized segments FOR learning. These often align (a small فصل becomes one chunk → one or more teaching units) but need not (a 10,000-word باب is split into multiple chunks; three tiny adjacent تنبيه sections are merged into one chunk).

**User scenarios served:**
- **Scenario 1 (Day 1 — New Source):** A new Shamela export is normalized → the excerpting engine processes the normalized package → produces draft excerpts → taxonomy engine places them → the source is searchable and browsable.
- **Scenario 2 (Day 30 — Study Session):** Every excerpt the owner reads exists because this engine extracted it as a self-contained teaching unit from a larger text. Excerpt quality directly determines study quality.
- **Scenario 7 (Science Map):** Coverage completeness depends on excerpts covering all topics in a source. Gaps in excerpting = gaps in knowledge.
- **Scenario 8 (Correction):** When an excerpt is wrong (misattributed, poorly bounded, incomplete), the correction traces back to this engine's decisions.

---

## 2. Input Contract

The excerpting engine receives a single input artifact per source: a normalized package at `library/sources/{source_id}/normalized/`.

**Manifest (`manifest.json`).** The excerpting engine reads these manifest fields:

- `source_id` — links to the source metadata record for all upstream metadata.
- `division_tree` — the structural hierarchy. Array of top-level `DivisionNode` objects, each with: `div_id`, `division_type`, `heading_text`, `heading_level`, `start_unit_index`, `end_unit_index` (inclusive), `detection_method`, `confidence`, `children` (nested array forming the tree). The excerpting engine traverses this tree recursively; leaf nodes (empty `children`) are the primary chunk candidates. **Empty division tree:** If the division tree is empty (no divisions at all), the engine treats the entire source as a single implicit division spanning all content units. This implicit division is processed through Phase 1 as an oversized chunk requiring splitting.
- `structural_format` — one of: `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`. Selects the Phase 1 chunk strategy (§4.A.4).
- `layer_map` — detected text layers for multi-layer sources. Each entry: `layer_type`, `author_canonical_id`, `author_name_arabic`, `confidence`, `markers`. Used by Phase 3 for author attribution.
- `total_content_units` — expected number of records in the content stream.
- `content_census` — (normalization SPEC §4.B.5) statistical profile of source content. If present, the excerpting engine uses it for adaptive processing: `text_density_profile` (chunk size calibration), `layer_complexity` (commentary strategy), `structural_depth` (division tree reliability), `footnote_density` (footnote handling complexity), `vocabulary_profile.technical_term_density` (topic proposal confidence). If absent, default configuration values are used.
- `quality_report` — normalization quality summary. The excerpting engine uses `overall_confidence` to adjust division tree trust. When `overall_confidence` is `low` or `minimal`, the engine treats the division tree as unreliable and runs supplementary boundary detection during Phase 1.
- `verse_detection` — whether versified text was found. When true, verse-aware Phase 1 processing is activated.
- `tahqiq_topology` — (normalization SPEC §4.B.7) manuscript witness network. If present, the excerpting engine records variant reading density per chunk, enabling the taxonomy engine to flag excerpts from high-variant regions.
- `layer_fingerprints` — (normalization SPEC §4.B.9) per-layer stylometric fingerprints. If present, used by Phase 3 for author attribution validation: if a teaching unit's text has statistical properties inconsistent with its attributed layer, the attribution confidence is reduced.

**Content stream (`content.jsonl`).** One record per physical page, ordered by `unit_index`. The excerpting engine reads all fields defined in the normalization engine SPEC §3. The following fields are particularly important:

- `primary_text` — the page's main text content. Phase 1 concatenates these across pages to produce assembled chunk text. Phase 2 operates on the assembled text. Phase 3 copies the teaching unit's text verbatim into the excerpt's `primary_text` field (D-004: primary text is never modified).
- `text_layers` — per-page layer attribution with character offsets and confidence. Phase 1 rebases these to chunk-level offsets during assembly. Phase 3 uses rebased layers for author attribution.
- `footnotes` — extracted footnotes with type classification and structured data. Phase 1 carries these through with source page tracking. Phase 3 extracts evidence references (hadith takhrij, Quran citations) from footnotes.
- `structural_markers` — heading detection results. Phase 1 uses these (in conjunction with the division tree) to validate chunk boundaries.
- `content_flags` — boolean flags (`has_verse`, `has_table`, `has_quran_citation`, `has_hadith_citation`, `is_toc_page`, `is_index_page`, `is_blank`). Phase 1 skips content units with `is_toc_page`, `is_index_page`, or `is_blank` true. Phase 3 uses citation flags for evidence reference detection.
- `text_fidelity` — per-page quality assessment. Phase 3 aggregates these into per-excerpt fidelity. Low-fidelity pages trigger review flags.
- `boundary_continuity` — (normalization §4.B.8) continuity signal for the boundary after each page. Phase 1 uses this as the primary signal for cross-page text assembly (§4.A.2): `mid_sentence` → join without separator; `mid_paragraph` → space join; `section_break`/`division_break` → paragraph break. When absent or low-confidence, Phase 1 falls back to character-level heuristics.
- `verse_info` — verse detection results. Phase 1 uses these for verse-aware chunk strategies.
- `discourse_flow` — (normalization §4.B.10) scholarly discourse segment annotation. **Currently NOT IMPLEMENTED in normalization engine.** When available in future, Phase 2 uses discourse_flow as optional prior information for segment classification: segments that normalization already classified with high confidence can be pre-labeled, reducing LLM work. The excerpting engine MUST work correctly without discourse_flow — it is an optimization, not a dependency.

**Source metadata (via `source_id` reference).** The excerpting engine accesses source metadata for:
- `science_scope` — science classification (array). Used by Phase 3 for `science_id` assignment.
- `genre` / `genre_chain` — work genre relationships. Used by Phase 3 for content type inference.
- `is_multi_layer` — whether the source has multiple text layers.
- `text_fidelity` — source-level fidelity baseline.
- `author` / `author_canonical_id` — primary author. Used as default for single-layer sources.

**Validation on input.** The excerpting engine validates before processing:

1. The manifest file exists and is valid JSON. Failure: `EXC_MANIFEST_INVALID` (fatal).
2. `schema_version` is a recognized version (`normalized_package_v2.0` or later). Failure: `EXC_SCHEMA_UNSUPPORTED` (fatal).
3. The content stream file exists. Failure: `EXC_CONTENT_MISSING` (fatal).
4. `total_content_units` matches the actual record count in the content stream. Mismatch: `EXC_CONTENT_COUNT_MISMATCH` (warning — process with actual count).
5. Content units are ordered by `unit_index` with no gaps. Out-of-order: `EXC_CONTENT_UNORDERED` (fatal). Gap: `EXC_CONTENT_GAP` (warning — skip missing indices, flag affected chunks).
6. The division tree, if non-empty, has consistent `start_unit_index`/`end_unit_index` ranges: for siblings A (preceding) and B (following), `B.start_unit_index > A.end_unit_index` (strictly greater, since `end_unit_index` is inclusive). Inconsistency: `EXC_DIVISION_INCONSISTENT` (warning — fall back to flat processing for affected regions).

Validation failures at `fatal` severity abort processing. Warnings are logged and processing continues with degraded behavior.

---

## 3. Output Contract

The excerpting engine produces one primary artifact per source: a draft excerpt stream.

**Primary artifact: the draft excerpt stream.**

Written to `library/sources/{source_id}/excerpts/excerpts.jsonl`. One JSONL record per excerpt. Each record conforms to the excerpt schema:

### 3.1 Excerpt Record Schema

**Identity fields:**

- `schema_version`: string, format `excerpt_v{major}.{minor}`. Current: `excerpt_v3.0`.
- `excerpt_id`: string, format `exc_{source_id}_{zero_padded_sequence}` (e.g., `exc_nahw_ibnaqil_sharh_001_0014`). Globally unique within the library. Monotonically increasing within a source, following document order.
- `source_id`: string. The source's canonical identifier. Primary link to all upstream metadata.
- `chunk_id`: string, format `chk_{source_id}_{zero_padded_sequence}` (e.g., `chk_nahw_ibnaqil_sharh_001_0003`). The Phase 1 chunk from which this excerpt was extracted. Multiple excerpts may share a `chunk_id` (a chunk typically produces 3-15 teaching units).
- `lifecycle_stage`: enum, always `draft` when produced by the excerpting engine. Transitions to `placed` by the taxonomy engine.

**Segment composition fields:**

- `segment_ids`: array of strings. All classified segment IDs from Phase 2a that compose this excerpt, in reading order. Format: `seg_{chunk_id}_{zero_padded_index}` (e.g., `seg_chk_nahw_ibnaqil_sharh_001_0003_005`). These are the atomic building blocks — each segment has a scholarly function classification.
- `core_segment_ids`: array of strings. Subset of `segment_ids` that substantively address the teaching topic. The distinction: core segments carry the excerpt's teaching content; context segments provide background needed for self-containment.
- `context_segments`: array of objects. Each: `segment_id` (string), `role` (one of: `prerequisite`, `evidence`, `classification_frame`, `transition`, `example`, `editorial`). These are segments included in the excerpt for self-containment but whose primary teaching content is a different topic.

**Text fields:**

- `primary_text`: string. The verbatim Arabic text of the teaching unit, assembled from the constituent segments' text. Preserves all diacritics exactly. Footnote reference markers (`⌜N⌝`) preserved inline. **D-004: This text is never modified after extraction.** It is a direct, contiguous substring of the Phase 1 chunk text, which is itself assembled from normalization's `primary_text` fields. No word is added, removed, or altered.
- `text_layers`: array of `TextLayerSegment` objects. Layer attribution segments covering this excerpt's text, with character offsets rebased to `primary_text` (not to the chunk or content unit). Each segment: `layer_type` (matn/sharh/hashiyah/tahqiq_note/uncertain), `author_canonical_id`, `start` (int), `end` (int), `confidence` (float 0.0-1.0). For single-layer sources, one segment covering the full text.

**Attribution fields:**

- `primary_author_id`: string or null. The canonical scholar ID (`sch_XXXXX`) of the excerpt's primary author — the scholar whose intellectual contribution this excerpt represents. For single-layer sources, this is the source's author. For multi-layer sources, this is determined by the dominant layer (§4.A.8). Null when attribution cannot be determined with confidence ≥ 0.5.
- `primary_author_name`: string or null. Arabic display name of the primary author.
- `quoted_scholars`: array of objects. Scholars quoted or referenced within the excerpt. Each: `canonical_id` (string or null), `name_text` (string — name as it appears in the text), `role` (one of: `quoted_opinion`, `cited_source`, `refuted_position`, `reported_consensus`, `teacher_reference`), `confidence` (float 0.0-1.0).
- `source_layer`: string. The dominant authorial layer of the excerpt: `matn`, `sharh`, `hashiyah`, `tahqiq`, or `single_layer`. Determined from `text_layers` by character count majority.

**Classification fields:**

- `excerpt_topic`: string. A concise Arabic topic description (10-30 words) of what this teaching unit teaches. Generated by Phase 3 LLM. Example: `"تعريف المبتدأ وشروطه وأنواعه عند النحويين"` (Definition of the subject, its conditions, and its types according to grammarians).
- `proposed_leaf`: string or null. Proposed taxonomy leaf path. Null by default — the excerpting engine generates the topic proposal but does not have access to taxonomy trees. May be populated by a future integration where tree awareness is available.
- `proposed_leaf_confidence`: float 0.0-1.0. Confidence in the proposed leaf assignment. 0.0 when `proposed_leaf` is null.
- `science_id`: string. The science this excerpt belongs to (e.g., `nahw`, `fiqh`, `usul_al_fiqh`, `aqidah`). Determined from source metadata `science_scope` — if the source has a single science, all excerpts inherit it; if multiple sciences, Phase 3 classifies per-excerpt.
- `school`: string or null. The scholarly school this excerpt represents (e.g., `حنبلي`, `شافعي`, `بصري`, `كوفي`). Null for school-independent content (definitions, universal rulings) or when school cannot be determined. **Multi-model consensus required** for school classification (§6).
- `school_confidence`: float or null. Confidence in school classification. Null when `school` is null.
- `content_types`: array of strings. Aggregated scholarly function values from the constituent segments. Drawn from the 16-value function enum: `definition`, `rule_statement`, `evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`, `opinion_statement`, `refutation`, `example`, `condition_exception`, `cross_reference`, `narration`, `editorial_note`, `structural_transition`, `unclassified`. Each type appears at most once.
- `excerpt_kind`: string, one of `teaching` (the primary kind — self-contained scholarly segments), `apparatus` (editorial/tahqiq content worth preserving), `structural` (transitional content between major sections). Default: `teaching`.

**Evidence and reference fields:**

- `evidence_refs`: array of objects. Evidence references detected within the excerpt. Each: `evidence_type` (one of: `quran`, `hadith`, `ijma`, `qiyas`, `companion_statement`, `rational`, `istishab`), `text_snippet` (string, ≤200 chars — the relevant Arabic text), `quran_detail` (object or null: `{surah, ayah_start, ayah_end}`), `hadith_detail` (object or null: `{collection, hadith_number, grade, grade_source}`), `source_segment_id` (string — which segment contains this evidence).
- `takhrij_data`: array of objects. Hadith source-tracing data from editor footnotes (normalization §4.B.4 `hadith_takhrij` footnotes that fall within this excerpt's page range). Each: `hadith_ref` (string), `collections` (array of strings), `numbers` (array of strings), `grade` (string or null), `grade_source` (string or null).
- `terminology_variants`: array of objects. Terms that may have alternative names across sources. Each: `term_in_text` (string — the term as it appears), `standard_term` (string or null — the canonical term if known), `confidence` (float 0.0-1.0).

**Quality fields:**

- `self_containment_score`: float 0.0-1.0. Phase 3's assessment of whether this teaching unit can be understood independently. 1.0 = completely self-contained; 0.0 = incomprehensible without surrounding context. Computed by LLM evaluation (§4.A.12). Excerpts scoring <0.5 trigger review flag `low_self_containment`.
- `self_containment_notes`: string or null. When `self_containment_score` < 0.7, a brief explanation of what context is missing.
- `excerpt_confidence`: float 0.0-1.0. Overall confidence in the excerpt's quality — a weighted aggregate of segment classification confidence (0.4), teaching unit grouping confidence (0.3), and metadata enrichment confidence (0.3).

**Source reference fields:**

- `physical_pages`: object. `volume` (int or null), `start_page` (string or null — Arabic-numeral display form), `end_page` (string or null), `start_page_int` (int or null), `end_page_int` (int or null). Derived from the constituent content units' `physical_page` fields.
- `verse_numbers`: object or null. For verse-format excerpts: `start_line` (int), `end_line` (int). Null for prose.
- `division_path`: array of objects. The path from the division tree root to this excerpt's position. Each object: `div_id` (string), `heading_text` (string), `heading_level` (int). Provides full hierarchical context.
- `unit_range`: object. `start` (int) and `end` (int, inclusive). The `unit_index` range of content units that contribute text to this excerpt's chunk.

**Footnote fields:**

- `footnotes`: array of objects. All footnotes from constituent content units that are referenced within this excerpt's text range. Each footnote: `ref_marker` (string — renumbered to be sequentially unique within the excerpt), `text` (string), `footnote_type` (FootnoteType enum), `confidence` (float), `source_unit_index` (int — which content unit the footnote originated from). Type-specific structured data (`variant_data`, `takhrij_data`, `bio_data`, `correction_data`) preserved from normalization.

**Review fields:**

- `review_flags`: array of strings. Machine-generated flags for human review. Possible values: `low_self_containment`, `low_confidence_boundary`, `low_fidelity_content`, `split_from_large`, `merged_siblings`, `uncertain_attribution`, `school_disagreement`, `format_detection_failed`, `marker_sparse_chunk`, `empty_division_tree`, `cross_topic_candidate`, `very_short_excerpt`, `oversized_excerpt`, `layer_attribution_anomaly`.

**Provenance fields:**

- `processing_metadata`: object. `engine_version` (string), `model_used` (string — the LLM model for Phase 2/3), `consensus_used` (bool — whether multi-model consensus was applied for attribution decisions), `processing_timestamp` (string — ISO 8601 datetime), `phase_1_strategy` (string — which chunk strategy was applied).

### 3.2 Segment Classification Record

In addition to the excerpt stream, the excerpting engine produces a segment classification stream — the intermediate output of Phase 2a. This is stored alongside the excerpt stream for debugging, quality analysis, and potential re-grouping.

Written to `library/sources/{source_id}/excerpts/segments.jsonl`. One record per classified segment:

- `segment_id`: string, format `seg_{chunk_id}_{zero_padded_index}`.
- `chunk_id`: string. The parent chunk.
- `start_word`: int. Approximate start word offset in assembled chunk text.
- `end_word`: int. Approximate end word offset in assembled chunk text.
- `start_char`: int. Exact start character offset in assembled chunk text.
- `end_char`: int. Exact end character offset in assembled chunk text.
- `text_snippet`: string. First 80 characters of this segment's text (copied exactly from chunk text).
- `scholarly_function`: enum. One of the 16 values: `definition`, `rule_statement`, `evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`, `opinion_statement`, `refutation`, `example`, `condition_exception`, `cross_reference`, `narration`, `editorial_note`, `structural_transition`, `unclassified`.
- `confidence`: float 0.0-1.0. LLM's confidence in the classification.
- `layer_attribution`: string or null. If the segment falls entirely within one text layer, the layer type is recorded here. Null for single-layer sources or segments spanning multiple layers.

### 3.3 Chunk Metadata Record

The Phase 1 chunk stream is stored for debugging and traceability.

Written to `library/sources/{source_id}/excerpts/chunks.jsonl`. One record per chunk:

- `chunk_id`: string, format `chk_{source_id}_{zero_padded_sequence}`.
- `source_id`: string.
- `division_ids`: array of strings. The `div_id`(s) of the leaf division(s) this chunk covers.
- `division_path`: array of objects. Path from root to this chunk's position.
- `heading_text`: string or null. Heading text for the primary division.
- `unit_range`: object. `start` (int) and `end` (int, inclusive).
- `assembled_text`: string. The full assembled text of this chunk.
- `text_layers`: array of `TextLayerSegment`. Layer attribution rebased to assembled text.
- `footnotes`: array of `Footnote`. All footnotes from constituent content units.
- `word_count`: int. Arabic word count of assembled text.
- `sizing_action`: string, one of `direct`, `merged`, `split`.
- `sizing_notes`: string or null.
- `strategy`: string. Which Phase 1 strategy was applied.
- `physical_pages`: object. Page range.
- `content_flags`: object. Aggregated flags from constituent content units.
- `text_fidelity_min`: string. Lowest fidelity score among constituent units.

### 3.4 Guarantees About the Excerpt Stream

- **Source-agnostic.** The excerpt schema is identical regardless of source type.
- **Ordering.** Excerpts are ordered by document order. `excerpt_id` sequence numbers are monotonically increasing within a source.
- **Complete text coverage.** Every word of substantive text (excluding TOC, index, and blank pages) in the normalized package appears in exactly one excerpt's `primary_text`. No substantive text is lost between chunks, between segments, or between excerpts. Verified by §5 check 1.
- **Non-overlapping.** No text region appears in more than one excerpt. Segment boundaries partition the chunk text without overlap. Excerpt boundaries partition the chunk's segments without overlap.
- **D-004 text preservation.** The `primary_text` field of every excerpt is a verbatim substring of the Phase 1 chunk text, which is itself assembled from normalization content units without modification. Diacritics preserved exactly. No character added, removed, or substituted.
- **D-011 chunk containment.** Every excerpt's text comes from exactly one chunk. No excerpt spans two chunks.
- **D-023 metadata pass-through.** Every excerpt carries `source_id` for upstream metadata access, `division_path` for structural context, `physical_pages` for citation, `text_layers` for authorship attribution, `content_flags` for downstream hints, and `text_fidelity` for quality awareness. The excerpting engine ADDS metadata; it NEVER strips upstream fields.
- **Excerpt self-sufficiency.** Each excerpt record contains all text and metadata needed for taxonomy placement and synthesis.

**Source registry update.** Upon successful excerpting, the source's processing status is updated from `normalized` to `excerpted`. The excerpt stream path is recorded.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Processing Overview

Excerpting proceeds in three sequential phases with 13 steps:

**Phase 1 — Deterministic Preprocessing**
1. Load and validate (§2)
2. Assemble text (§4.A.2)
3. Create chunks (§4.A.3)
4. Apply format-specific strategies (§4.A.4)

**Phase 2 — LLM Teaching Unit Extraction**
5. Classify segments (§4.A.5)
6. Group into teaching units (§4.A.6)
7. Post-process (§4.A.7)

**Phase 3 — Metadata Enrichment**
8. Author attribution (§4.A.8)
9. School classification (§4.A.9)
10. Evidence reference detection (§4.A.10)
11. Topic proposal and science classification (§4.A.11)
12. Self-containment evaluation (§4.A.12)
13. Output assembly and validation (§4.A.13)

The engine processes one source at a time.

**Example:** Processing شرح ابن عقيل (847 content units, multi-layer) → Phase 1: produce ~142 chunks → Phase 2: classify segments (~8-15 per chunk), group into teaching units (~5-12 per chunk, ~800-1200 total) → Phase 3: attribute, classify, detect evidence, generate topics → Output: ~800-1200 draft excerpts.

#### §4.A.2 — Phase 1: Cross-Page Text Assembly

The normalization engine outputs per-page content units. The excerpting engine joins these across pages to produce continuous text within division boundaries.

**Assembly scope.** For each leaf division in the division tree (identified by its `start_unit_index` and `end_unit_index`), the engine assembles text from all content units in that range. Content units with `is_toc_page`, `is_index_page`, or `is_blank` true are skipped — they produce no assembled text, but their `unit_index` is recorded for page range accuracy.

**Continuity-informed joining.** When content unit N has a `boundary_continuity` field (normalization §4.B.8), the engine uses it as the primary joining signal:

- `type == "mid_sentence"` with `confidence ≥ 0.7`: Join with a single space. No paragraph break.
- `type == "mid_paragraph"` with `confidence ≥ 0.7`: Join with a single space. Sentence boundary but same paragraph.
- `type == "section_break"` or `"division_break"` with `confidence ≥ 0.7`: Insert double newline (`\n\n`).
- `type == "mid_argument"` with `confidence ≥ 0.7`: Join with a single space. Record this boundary in chunk metadata as a `mid_argument_join` for Phase 2 awareness.
- `type == "unknown"` or `confidence < 0.7`: Fall back to character-level heuristics.

When `boundary_continuity` is absent (null), fall back entirely to character-level heuristics.

**Character-level joining heuristics (fallback).** Applied when continuity signals are unavailable:

1. **Mid-word join.** If the last character of unit N's `primary_text` is a non-final-form Arabic letter AND the first character of unit N+1's `primary_text` is an Arabic letter with no intervening whitespace — this is a mid-word page break. Join without separator. Word-final forms that prevent mid-word joining: taa marbuta `ة`, alif maqsura `ى`, tanwin diacritics (`ً` `ٌ` `ٍ`), standalone hamza `ء` when not preceded by a connecting letter.
2. **Sentence boundary.** If unit N's text ends with terminal punctuation (`.`, `؟`, `!`) followed by whitespace, and unit N+1 begins a new sentence — insert a single newline.
3. **Mid-sentence.** If unit N's text ends without terminal punctuation and unit N+1 continues the sentence — insert a single space.
4. **Clean paragraph break.** If both units end and start cleanly (sentence boundary to new sentence with paragraph-level whitespace in the source) — insert double newline.

**CRLF normalization.** All assembled text has `\r\n` and `\r` converted to `\n` before any further processing. The owner is on Windows; CRLF in source text is expected.

**Footnote renumbering.** When assembling text across pages, footnote reference markers (`⌜N⌝`) may collide (two pages both have `⌜1⌝`). The engine renumbers footnotes within the assembled chunk text to be sequentially unique, starting from 1, in order of appearance. The `footnotes` array in the chunk record uses the renumbered markers. The mapping is deterministic.

**Text layer rebasing.** `text_layers` segments from each content unit are rebased to the assembled chunk text. Character offsets are recalculated relative to the start of the assembled text. Adjacent segments from the same layer and author are merged. Before rebasing, the engine validates: if any segment's `end` exceeds its content unit's `primary_text` length, the segment is clamped and `EXC_ASSEMBLY_LAYER_MISMATCH` (warning) is logged.

**Quran citation integrity.** The engine tracks open Quran citation brackets (`﴿`). Within an open citation (between `﴿` and `﴾`), joining rules 1 and 3 apply unconditionally — Quran text is always joined directly regardless of character patterns. If `﴾` is never found, `EXC_ASSEMBLY_QURAN_UNCLOSED` (warning) is logged and subsequent text is treated normally.

#### §4.A.3 — Phase 1: Division-to-Chunk Mapping

After assembly, the engine maps divisions to processable chunks. This is the sizing logic that determines whether a division becomes a chunk directly, is merged with neighbors, or is split.

**Arabic word count method.** Word counting uses whitespace tokenization on the assembled text after stripping footnote reference markers (`⌜N⌝`). Split on Unicode whitespace (`\s+`), filter out empty tokens and tokens consisting entirely of punctuation, count remaining tokens.

**Step 1: Walk to leaf divisions.** Traverse the division tree to its leaf nodes (divisions with empty `children` array). Each leaf division is a candidate chunk. Non-digestible leaf divisions (every content unit in the division's range has `is_toc_page`, `is_index_page`, or `is_blank` true) are skipped entirely.

**Step 2: Size evaluation.** For each candidate:

- **Below minimum (<50 Arabic words):** Merge with the next sibling division. If this is the last sibling, merge with the previous sibling. `sizing_action: "merged"`. Continue merging if the result is still below 50w. If all siblings combined are still below 50w, emit as a single chunk with review flag `very_short_excerpt`. If the division has no siblings, merge with the parent's nearest sibling's adjacent child — and if no such child exists, emit as-is with `very_short_excerpt` flag. An undersized chunk is better than lost content.

- **In range (50-5000 Arabic words):** Accept as-is. `sizing_action: "direct"`. This covers 99.1% of the Shamela corpus.

- **Above standard maximum (>5000 Arabic words):** Split required. Proceed to Step 3. `sizing_action: "split"`. **Marker-sparse adjustment:** If the assembled text has fewer than 2 structural keyword matches per 1000 words (scanning for: `مسألة`, `فرع`, `تنبيه`, `فائدة`, `القول الأول`, `والدليل`, `والراجح`, `وأما`), the division is classified as "marker-sparse" and the split threshold drops to 3000w. This accounts for the untested gap: experiments validated up to 3100w on well-structured text, but marker-free text may degrade at lower sizes.

**Step 3: Splitting oversized divisions.** When a division must be split:

1. **Paragraph boundary scan.** Identify paragraph breaks (double newline patterns). These are the preferred split points.
2. **Scholarly keyword scan.** Within paragraphs, search for topic-transition markers:
   - **Ordinal markers:** `أولاً`, `ثانياً`, `ثالثاً`, `الأول` / `الثاني` / `الثالث`, `الوجه الأول`
   - **New-topic markers:** `وأما`, `ومن ذلك`, `فصل:` (inline), `ثم إن`
   - **Position markers:** `وذهب ... إلى`, `القول الأول` / `القول الثاني`, `والراجح`
   - **Evidence markers:** `والدليل على ذلك`, `لقوله تعالى`, `لقول النبي ﷺ`
   
   **Boundary placement:** When a keyword marker is a split point, the boundary is placed BEFORE the keyword (the keyword starts the new chunk). The preceding chunk ends at the last sentence boundary before the keyword.
   
   **Split point selection:** Among multiple candidates, prefer the one producing the most evenly-sized chunks. Among candidates with similar balance (within 10% ratio), prefer: ordinal markers > new-topic markers > position markers > evidence markers.

3. **LLM-assisted splitting (for divisions >8000w with no satisfactory paragraph/keyword split).** Send text in overlapping 4000-word windows to the LLM requesting sub-topic boundaries. Each LLM-identified boundary receives confidence 0.7 and review flag `low_confidence_boundary`.

4. **Fallback: fixed-interval splitting.** If all else fails, split at sentence boundaries at approximately 2000-word intervals. Review flag `low_confidence_boundary`.

**Sentence integrity rule.** No chunk boundary falls mid-sentence. When a boundary calculation lands within a sentence, the boundary moves to the nearest sentence end. Sentence boundaries are identified by terminal punctuation (`.`, `؟`, `!`) followed by whitespace, or paragraph breaks.

**Isnad chain integrity.** Isnad chains (`حدثنا X عن Y عن Z قال: [matn]`) plus their matn form atomic units. The engine detects isnad openings (`حدثنا`, `أخبرنا`, `أنبأنا`) and never places a chunk boundary between an isnad and its matn.

**Empty division tree handling.** When the division tree is empty, the engine treats the entire source as one implicit division. This implicit division is almost certainly oversized (a 500-page book as one division = ~100,000+ words). Step 3 splitting applies. The resulting chunks carry review flag `empty_division_tree` and `division_path` contains a single synthetic entry: `{div_id: "div_{source_id}_0_000", heading_text: "[no structure]", heading_level: 0}`.

#### §4.A.4 — Phase 1: Format-Specific Chunk Strategies

The manifest's `structural_format` selects the chunk strategy. Each strategy modifies how Step 2 (§4.A.3) evaluates boundaries.

**Prose strategy (default).** The standard division-guided strategy described in §4.A.3. Used for `structural_format: "prose"` and as the fallback when format-specific detection fails.

**Verse strategy.** For `structural_format: "verse"` or when `verse_detection` is true in the manifest.

- A بيت (verse couplet) is NEVER split across chunk boundaries. Both hemistichs always remain in the same chunk.
- For pure verse sources (single-layer): each division containing ≤30 verses is one chunk. Divisions with >30 verses are split at verse group boundaries where the topic shifts (detected from verse numbering gaps or thematic transitions).
- For commentary-on-verse (multi-layer, e.g., شرح ابن عقيل): the chunk unit is a **commentary unit** — one or more quoted verses plus all commentary explaining them. New verse quotation markers (`قوله:`, `ومنه قول الناظم:`, appearance of Layer 1 text after Layer 2) signal commentary unit boundaries.
- Size targets: minimum 100w (lower than prose because a single verse + brief commentary may be short but coherent), maximum same as prose.

**Q&A pair strategy.** For `structural_format: "qa_format"`.

- Detect Q&A pairs using markers: `سُئل عن`, `مسألة:`, `سؤال:`, `فأجاب`, `جواب:`, `الجواب:`, `قيل له:`.
- Each Q&A pair (question + answer) forms one chunk. The question marker starts a new chunk; the chunk extends through the answer until the next question marker.
- If a Q&A pair exceeds the split threshold, the answer is split at paragraph boundaries while keeping the question with the first split piece.
- If Q&A detection fails (<2 markers detected in a division classified as `qa_format`), fall back to prose strategy with review flag `format_detection_failed`.

**Masala-block strategy.** For `structural_format: "tabular_khilaf"`.

- Detect مسألة blocks using markers: `مسألة:`, `فرع:`, `تنبيه:` combined with position markers (`القول الأول`, `القول الثاني`).
- Each مسألة block is one chunk: the question formulation, all scholarly positions, evidence, and the author's conclusion (ترجيح) if present.
- Oversized مسائل: split at position boundaries (`القول الأول` / `القول الثاني`).
- Undersized مسائل (<50w): merge with the next مسألة.

**Dictionary entry strategy.** For `structural_format: "dictionary"`.

- Detect entry boundaries from: structural markers in the division tree matching root word patterns, alphabetical sequence transitions, or explicit entry markers.
- Each dictionary entry is one chunk. Oversized entries (rare): split at sub-entry boundaries.
- Fallback to prose strategy if entry detection finds fewer than 5 entries with review flag `format_detection_failed`.

**Commentary-unit strategy.** For `structural_format: "commentary"` with multi-layer text.

- A chunk is a **commentary unit**: one segment of commented-upon text (matn/sharh) plus all commentary explaining it.
- Detection uses `text_layers` transitions: each new matn segment (detected by layer transition from sharh→matn or by quotation markers like `قوله:`, `قال المصنف:`) starts a new commentary unit.
- Matn segments are NEVER split across chunks. The matn segment always appears in full in one chunk.
- Oversized commentary units: split the commentary portion at paragraph boundaries while keeping the matn segment with the first piece.
- Single-layer commentary sources (layer detection failed): fall back to prose strategy with review flag `format_detection_failed`.

**Mixed-format strategy.** For `structural_format: "mixed"`.

- Examine each leaf division individually. Apply a priority cascade:
  1. ≥80% of content units have `has_verse: true` → verse strategy
  2. ≥2 Q&A markers detected → Q&A strategy
  3. ≥2 مسألة markers detected → masala strategy
  4. Multi-layer with ≥2 distinct `layer_type` values → commentary strategy
  5. Default → prose strategy
- Each division is chunked independently using its assigned strategy.

#### §4.A.5 — Phase 2a: Segment Classification

For each chunk produced by Phase 1, the engine sends the assembled text to the LLM for segment classification. This is the first of two LLM calls per chunk (the validated Approach B).

**LLM call specification:**

- **Model:** `anthropic/claude-opus-4.6` via OpenRouter
- **Temperature:** 0 (deterministic)
- **MAX_TOKENS:** 8192 for chunks ≤2000 Arabic words. 32768 for chunks >2000 Arabic words. (Validated: longer divisions produce 125-166 segments, exceeding 8192 token limit.)
- **Structured output:** Via Instructor library, `mode=instructor.Mode.JSON`
- **Response model:** `ClassificationResult` (Pydantic schema defined in contracts)

**System prompt:**

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

Classify each sentence or closely bonded group of sentences in this Arabic text by scholarly function:
definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
condition_exception, cross_reference, narration, editorial_note,
structural_transition, unclassified

Rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Include text_snippet: the first 50 characters of each segment
- Segments must cover the ENTIRE input text with no gaps or overlaps
- Confidence reflects how certain you are of the classification (0.0-1.0)
```

**User message:** The chunk's `assembled_text`.

**Output:** Array of `ClassifiedSegment` objects: `segment_index`, `start_word`, `end_word`, `text_snippet`, `scholarly_function`, `confidence`.

**Coverage verification (immediate).** After receiving the classification result, the engine verifies that the union of segment word ranges covers the entire chunk text with no gaps. If coverage is <95%, log `EXC_CLASSIFICATION_COVERAGE_GAP` (warning), assign unclassified segments to the `unclassified` function to fill gaps, and proceed. If coverage is <80%, log `EXC_CLASSIFICATION_FAILED` (warning), retry once with a simplified prompt. If retry also fails, assign the entire chunk as one `unclassified` segment and proceed to Phase 2b with degraded quality.

**discourse_flow integration (future optimization).** When normalization's `discourse_flow` data is available on constituent content units, the engine constructs a pre-classification map: for each discourse segment with confidence ≥0.85, map its character range to the assembled chunk text and pre-assign the corresponding scholarly function. The LLM receives these pre-assignments as hints in the prompt: "The following regions have been pre-classified: [list]. Confirm or override these classifications, and classify the remaining text." This reduces LLM work and improves consistency — but the engine MUST produce correct results without this optimization.

#### §4.A.6 — Phase 2b: Teaching Unit Grouping

After classification, the engine sends the classified segments back to the LLM along with the original text, requesting grouping into self-contained teaching units.

**LLM call specification:**

- **Model:** `anthropic/claude-opus-4.6` via OpenRouter
- **Temperature:** 0
- **MAX_TOKENS:** 8192 for all chunks (grouping output is smaller than classification output)
- **Structured output:** Via Instructor, `mode=instructor.Mode.JSON`
- **Response model:** `ExtractionResult` (Pydantic schema: array of `TeachingUnit`)

**System prompt:**

```
You are an expert in classical Islamic scholarly text analysis.

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained scholarly
segments that each teach one distinct concept, ruling, or argument.

Rules:
- A position (opinion_statement) + its evidence + any counter-evidence + conclusion = one unit
- A definition + its examples = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- Each unit should be self-contained: a student can learn from it without the surrounding text
- Include text_snippet: the first 80 characters of each unit
- Include a brief Arabic description (10-30 words) of what the unit teaches
- Evaluate self-containment: can this unit be understood alone?
- Every segment must belong to exactly one teaching unit — no gaps, no overlaps
```

**User message:** Classified segments (JSON) followed by `\n\nOriginal text:\n` followed by the chunk's `assembled_text`.

**Output:** Array of `TeachingUnit` objects: `unit_index`, `start_word`, `end_word`, `text_snippet`, `description_arabic`, `primary_function`, `secondary_functions`, `self_contained`, `self_containment_notes`.

**D-011 enforcement.** Teaching units are produced within a single chunk's text. The LLM never sees text from adjacent chunks. This is the mechanism that enforces D-011 — the containment boundary is the chunk boundary, and the LLM operates within it.

#### §4.A.7 — Phase 2: Post-Processing

After Phase 2b, the engine post-processes the teaching units.

**Step 1: Merge undersized units.** Teaching units with fewer than 50 Arabic words are merged with their nearest thematic neighbor. "Nearest thematic" is determined by: (a) prefer merging with the adjacent unit that shares the most `secondary_functions`, (b) if tie, prefer the preceding unit (so the small unit acts as a conclusion to the preceding content rather than an introduction to the following). After merging, the merged unit's `primary_function` is the function of the larger constituent. The merge is logged in `sizing_notes`.

**Step 2: Verify complete text coverage.** Compute the character-level union of all teaching unit text spans. Compare against the total chunk text length. Requirements:
- Every character in the chunk text must be covered by exactly one teaching unit.
- No character may be uncovered (gap) or covered by two units (overlap).
- Tolerance: ±5 characters at boundaries (whitespace differences from word-to-character offset mapping).
If coverage fails: `EXC_GROUPING_COVERAGE_GAP` (warning). The engine assigns uncovered regions to the nearest teaching unit.

**Step 3: Assign IDs.** Each segment receives a `segment_id` in format `seg_{chunk_id}_{zero_padded_index}`. Each teaching unit receives an `excerpt_id` in format `exc_{source_id}_{zero_padded_sequence}`, with sequence numbers monotonically increasing across all chunks in document order.

**Step 4: Map segments to teaching units.** For each teaching unit, identify which classified segments fall within its word range. These become the unit's `segment_ids`. The core segments (those whose `scholarly_function` matches the unit's `primary_function` or `secondary_functions`) become `core_segment_ids`. The remainder become `context_segments` with roles inferred from their function (evidence_* → `evidence`, example → `example`, editorial_note → `editorial`, structural_transition → `transition`, etc.).

**Step 5: Extract primary_text.** For each teaching unit, extract the exact character range from the chunk's `assembled_text`. This becomes the excerpt's `primary_text`. Verify byte-level accuracy: the extracted text must match what the LLM's `text_snippet` describes.

**Step 6: Rebase text_layers.** The chunk's `text_layers` are rebased to each teaching unit's character range. Segments outside the range are dropped; segments partially inside are clamped to the range boundary. Every character in the teaching unit's text must be covered by exactly one layer segment.

#### §4.A.8 — Phase 3: Author Attribution

For each teaching unit, determine the primary author — the scholar whose intellectual contribution the excerpt represents.

**Single-layer sources.** `primary_author_id` = the source metadata's `author_canonical_id`. `source_layer` = `single_layer`. No LLM call needed.

**Multi-layer sources.** The primary author is determined by the dominant layer (by character count) in the teaching unit's `text_layers`:
- If sharh layer covers >60% of the text: `primary_author_id` = sharh author, `source_layer` = `sharh`.
- If matn layer covers >60% of the text: `primary_author_id` = matn author, `source_layer` = `matn`.
- If hashiyah layer covers >60%: `primary_author_id` = hashiyah author, `source_layer` = `hashiyah`.
- If no layer exceeds 60%: `source_layer` = the layer with the highest character count. `primary_author_id` = that layer's author. Review flag `uncertain_attribution` added.

**Layer fingerprint validation.** If `layer_fingerprints` are available in the manifest, the engine computes a local fingerprint for the teaching unit's text (sentence length, connective frequency) and compares against the global fingerprint for the attributed layer. If the local fingerprint diverges by >2.0 standard deviations (Mahalanobis distance), the attribution confidence is reduced by 0.15 and review flag `layer_attribution_anomaly` is added.

**Quoted scholar detection.** The engine detects scholars quoted or referenced within the excerpt using pattern matching:
- `قال X:` / `قال X رحمه الله:` — `role: quoted_opinion`
- `ذكره X` / `أخرجه X` — `role: cited_source`
- `ورد عليه X بأن` / `واعترض X` — `role: refuted_position`
- `أجمع العلماء` / `بالإجماع` — `role: reported_consensus`
Scholar names detected by pattern matching are resolved against the source metadata's known scholars (from `layer_map` and source metadata `author`). Unresolved names are recorded with `canonical_id: null`.

**Multi-model consensus for attribution.** When the dominant layer's character coverage is between 40% and 60% (ambiguous attribution), multi-model consensus is applied (§6). Both models must agree on the primary author. Disagreement escalates to human gate review with review flag `uncertain_attribution`.

#### §4.A.9 — Phase 3: School Classification

Determine the scholarly school of each excerpt. **Multi-model consensus required for all school assignments** (§6).

**School classification sources (in priority order):**

1. **Source metadata.** If the source is classified to a single school in source metadata, all excerpts inherit it. Confidence: 0.9.
2. **Explicit text markers.** Patterns like `وعند الحنابلة`, `ومذهب الشافعي`, `قال أبو حنيفة`. Confidence: 0.8-0.95 depending on marker specificity.
3. **Author's known school.** From the scholar authority registry via `primary_author_id`. Confidence: 0.7-0.85.
4. **LLM inference.** For excerpts where none of the above apply, the LLM infers school from content and terminology. Confidence: 0.5-0.7.

**School-independent excerpts.** Some content is inherently school-independent: definitions of Arabic grammatical terms, universal Quran/hadith citations, methodological discussions in usul al-fiqh. The engine classifies these as `school: null` with confidence null. Indicators: the excerpt's `content_types` are exclusively `definition`, `evidence_quran`, or `evidence_hadith` with no `opinion_statement` or `refutation`.

**Sciences without schools.** For sciences like Nahw (which has Basran/Kufan distinction, not madhhab schools) and Tajwid (no schools), the school field uses the science's own classification system as defined in SCIENCE.md files. If no SCIENCE.md exists for the science, `school` is null.

#### §4.A.10 — Phase 3: Evidence Reference Detection

Detect and structure scholarly evidence within each excerpt.

**Detection methods:**

- **Quran citations.** Detected by: curly-brace quotation `{...}`, `﴿...﴾` brackets, `قال تعالى` + quotation, surah/ayah references (`[سورة البقرة: ٢٣٤]`). Extract `quran_detail: {surah, ayah_start, ayah_end}` where identifiable. Surah identification uses a lookup table of all 114 surah names (Arabic).
- **Hadith citations.** Detected by: `قال النبي ﷺ` / `قال رسول الله ﷺ`, `عن X قال`, collection references (`رواه البخاري`, `أخرجه مسلم`), guillemet-quoted hadith text (`«...»`). Extract `hadith_detail: {collection, hadith_number, grade, grade_source}` where identifiable.
- **Hadith takhrij from footnotes.** All footnotes classified as `hadith_takhrij` by normalization (§4.B.4) that fall within the excerpt's page range are included in `takhrij_data`. This captures the editor's hadith tracing which may include collection names, hadith numbers, and scholarly grading not present in the main text.
- **Ijma references.** Detected by: `أجمع العلماء`, `بالإجماع`, `لا خلاف في`, `اتفقوا على`.
- **Qiyas references.** Detected by: `قياساً على`, `بجامع`, `ولأنه` (when in an evidential context).
- **Companion statements.** Detected by: `قال ابن عباس`, `عن عمر`, `روي عن X` where X is a known companion.
- **Rational arguments.** Detected by: `ولأن`, `إذ`, `بدليل أن` when not accompanied by textual evidence.

Each detected reference produces an `EvidenceRef` object with the segment it appears in (`source_segment_id`).

#### §4.A.11 — Phase 3: Topic Proposal and Science Classification

Generate a concise Arabic topic description for each excerpt and classify its science.

**Topic generation.** A batched LLM call processes 5-10 excerpts at a time. For each excerpt, the LLM receives: the `primary_text` (first 500 characters), the `content_types`, and the `division_path`. The LLM returns a concise Arabic topic description (10-30 words). The prompt:

```
For each scholarly excerpt below, generate a concise Arabic topic description (10-30 words) 
that captures WHAT the excerpt teaches. Focus on the specific scholarly content, not generic 
descriptions. Example: "تعريف المبتدأ وشروط الابتداء بالنكرة" not "نص في النحو".
```

**Science classification.** If the source metadata's `science_scope` contains a single science, all excerpts inherit it. If multiple sciences, the LLM classifies each excerpt's science based on its topic and content types. The valid science IDs are drawn from `library/sciences/taxonomy_registry.yaml`.

**`proposed_leaf` is null.** The excerpting engine does not have access to taxonomy trees during processing. The `proposed_leaf` field is set to null with `proposed_leaf_confidence: 0.0`. A future integration may allow the excerpting engine to query the taxonomy engine for leaf proposals — the schema supports this but the core does not implement it.

#### §4.A.12 — Phase 3: Self-Containment Evaluation

Score each excerpt's independent understandability.

**LLM evaluation.** A batched LLM call processes 5-10 excerpts at a time. For each excerpt, the LLM receives the `primary_text` and the `science_id`. The LLM returns a score (0.0-1.0) and notes.

**Prompt:**

```
For each Arabic scholarly excerpt below, evaluate self-containment: can a student with 
general familiarity of {science_name} understand what is being taught WITHOUT reading the 
surrounding text?

Score 0.0-1.0:
- 1.0: Completely self-contained. The excerpt defines all terms it uses and provides 
  sufficient context for understanding.
- 0.7-0.9: Mostly self-contained. Minor references to external context that a student 
  could infer.
- 0.4-0.6: Partially self-contained. Key terms or references are undefined. A student 
  would need to look up specific concepts.
- 0.0-0.3: Not self-contained. The excerpt assumes significant prior context (e.g., 
  "as mentioned above", "the ruling in the previous مسألة").

For scores below 0.7, explain what specific context is missing.
```

**Review flag trigger.** Excerpts scoring <0.5 receive review flag `low_self_containment`. These excerpts are valid — they represent real content that may lack context due to the author's writing style (e.g., a brief فائدة that assumes the reader has studied the preceding باب). The flag signals the taxonomy engine and synthesis engine to handle with care.

#### §4.A.13 — Output Assembly and Validation

After all Phase 3 enrichment steps, the engine assembles the final excerpt records and validates before writing.

**Assembly.** For each teaching unit, construct the `ExcerptRecord` by combining:
- Identity fields from Phase 2 post-processing (§4.A.7)
- Text fields from Phase 1 assembly + Phase 2 extraction
- Attribution fields from §4.A.8
- Classification fields from §4.A.9, §4.A.11
- Evidence fields from §4.A.10
- Quality fields from §4.A.12
- Source reference fields from Phase 1 chunk metadata
- Footnote fields from Phase 1 assembly
- Review flags accumulated from all phases
- Provenance from processing configuration

**Compute `excerpt_confidence`.** Weighted aggregate: segment classification confidence (mean of constituent segment confidences, weight 0.4) + teaching unit grouping confidence (from Phase 2b, weight 0.3) + metadata enrichment confidence (mean of attribution, school, and topic confidence, weight 0.3). Capped at 0.0-1.0.

**Self-validation checks (§5 Layer 1).** Before writing the excerpt stream:

1. **Text coverage.** The union of all excerpts' character ranges within each chunk must equal the chunk's total substantive text. No gaps, no overlaps. Tolerance: ±5 chars per excerpt boundary.
2. **Non-overlap.** No segment appears in two excerpts. No character position appears in two excerpts.
3. **Ordering.** `excerpt_id` sequence numbers are monotonically increasing. Excerpt document order matches chunk document order.
4. **Text preservation (D-004).** For a random sample of 10% of excerpts (minimum 5, maximum 50): compare `primary_text` byte-for-byte against the corresponding range of the chunk's `assembled_text`. Any discrepancy is fatal: `EXC_VALIDATION_TEXT_CORRUPTION`.
5. **Layer coverage (multi-layer sources).** For each excerpt, every character in `primary_text` is covered by exactly one `text_layers` segment. No gaps.
6. **Schema compliance.** Every excerpt record validates against the `ExcerptRecord` Pydantic schema. Any validation error is fatal.
7. **Footnote integrity.** Every `⌜N⌝` marker in `primary_text` has a corresponding entry in `footnotes`. Every footnote entry has a corresponding marker.
8. **Chunk containment (D-011).** Every excerpt's `unit_range` falls entirely within one chunk's `unit_range`.

Fatal check failures abort the write — the excerpt stream is not produced, and the source remains at `normalized` status. Warning-level failures are logged but allow the write.

**Atomic write.** The engine writes to a temporary directory first (`excerpts_tmp_{timestamp}/`), then atomically renames to `excerpts/`. If a previous `excerpts/` exists (reprocessing), it is renamed to `excerpts_prev_{timestamp}/` before the swap. The same atomic write pattern as the normalization engine (normalization SPEC §4.A.2).

### §4.B — Transformative Capabilities (Stage 2)

These capabilities extend the core but are not required for the engine's fundamental purpose. They are deferred to Stage 2. Each includes an extension hook.

#### §4.B.1 — Argument Discourse Mapping

Map the argumentative structure of each excerpt: claims, evidence, counter-arguments, and their relationships.

**Extension hook:** Core includes `content_types`. Stage 2 adds `argument_map: Optional[list[ArgumentMapSegment]]`. Core must not assume `argument_map` is present.

[NOT YET IMPLEMENTED]

#### §4.B.2 — Cross-Source Semantic Deduplication

Detect when 2+ sources quote the same hadith or paraphrase the same definition.

**Extension hook:** Core processes each source independently. Stage 2 adds `semantic_duplicates: Optional[list[SemanticDuplicateLink]]`.

[NOT YET IMPLEMENTED]

#### §4.B.3 — Evidence Chain Reconstruction

Reconstruct logical evidence structure: which claims are supported by which evidence, what reasoning connects them.

**Extension hook:** Core `evidence_refs` provides flat detection. Stage 2 adds `evidence_chain: Optional[EvidenceChain]` with argumentative structure.

[NOT YET IMPLEMENTED]

#### §4.B.4 — Masala Detection and Issue Formulation

Detect مسألة-bearing excerpts and extract the precise scholarly question.

**Extension hook:** Core `excerpt_topic` provides topic description. Stage 2 adds `masala_analysis: Optional[MasalaAnalysis]`.

[NOT YET IMPLEMENTED]

#### §4.B.5 — Self-Containment Repair

Automatically suggest or apply repairs for low-self-containment excerpts.

**Extension hook:** Core flags low-self-containment excerpts. Stage 2 adds `repair_suggestions: Optional[list[RepairSuggestion]]`.

[NOT YET IMPLEMENTED]

#### §4.B.6 — Scholarly Dialogue Links

Detect when one excerpt responds to, refines, or contradicts another.

**Extension hook:** Stage 2 adds `dialogue_links: Optional[list[DialogueLink]]`.

[NOT YET IMPLEMENTED]

#### §4.B.7 — Cross-Source Textual Resonance

Detect textual borrowing, structural mirroring, and terminological echoes across sources.

**Extension hook:** Stage 2 adds `resonance_links: Optional[list[ResonanceLink]]`.

[NOT YET IMPLEMENTED]

---

## 5. Validation and Quality

### 5.1 Self-Validation (Layer 1 — Every Run)

Eight self-validation checks defined in §4.A.13 run on every output. Checks 1-3 verify structural invariants (coverage, overlap, ordering). Check 4 verifies text preservation (D-004). Check 5 verifies layer coverage. Check 6 verifies schema compliance. Checks 7-8 verify footnote integrity and chunk containment. Fatal checks prevent the excerpt stream from being written.

### 5.2 Automated Quality Checks (Layer 2)

After excerpting completes:

1. **Size distribution.** Compute word count distribution across all excerpts. If >20% are below 50w or above 2000w, flag source: `EXC_SIZE_DISTRIBUTION_SKEWED`. May indicate Phase 1 chunking or Phase 2 grouping problems.
2. **Classification confidence.** Compute mean classification confidence across all segments. If mean <0.6, flag source: `EXC_LOW_CLASSIFICATION_CONFIDENCE`. May indicate the LLM struggled with the text.
3. **Self-containment distribution.** If >30% of excerpts score <0.5 on self-containment, flag source: `EXC_LOW_SELF_CONTAINMENT_RATE`. May indicate the source has a highly interconnected structure that resists self-contained extraction.
4. **Coverage gap check.** Recompute total character coverage from all excerpts and compare against total substantive text in the normalized package. If coverage <99%, flag: `EXC_COVERAGE_SHORTFALL`.

### 5.3 Human Gate Integration

The excerpting engine does not have its own dedicated human gate. Excerpts flagged with `review_flags` are surfaced at the taxonomy engine's human gate. The excerpting engine's contribution: producing clear review flags with descriptions, providing processing provenance, and scoring self-containment.

### 5.4 Threat Prevention (KNOWLEDGE_INTEGRITY.md)

**T-1 (Silent Text Corruption).** Mitigated by: D-004 text immutability — `primary_text` is never modified; §5.1 check 4 (byte-for-byte text preservation verification); CRLF normalization in Phase 1 (§4.A.2).

**T-2 (Attribution Error).** Mitigated by: multi-model consensus for author attribution in ambiguous cases (§4.A.8); layer fingerprint validation when available; multi-model consensus for school classification (§4.A.9); review flag `uncertain_attribution` for borderline cases.

**T-3 (Taxonomic Misplacement).** Mitigated at the taxonomy engine. The excerpting engine's contribution: high-quality `excerpt_topic` and `science_id` that give the taxonomy engine strong classification signals.

**T-4 (Context Loss).** Mitigated by: self-containment evaluation (§4.A.12) with LLM scoring; review flag `low_self_containment` for excerpts that may be incomplete; `context_segments` recording why certain segments were included.

**T-5 (Synthesis Hallucination).** Mitigated at the synthesis engine. The excerpting engine's contribution: every claim in `evidence_refs` is grounded in the source text (`text_snippet` + `source_segment_id`). No fabricated evidence.

**T-6 (Metadata Poisoning).** Mitigated by: `science_id` validation against `taxonomy_registry.yaml`; school classification with consensus; attribution from verified scholar registry data when available.

**T-7 (Duplication and Contradiction).** Deferred to Stage 2 (§4.B.2 cross-source deduplication). Core processes each source independently — no cross-source interaction.

---

## 6. Consensus Integration

The excerpting engine uses multi-model consensus for TWO decisions:

1. **School classification (§4.A.9).** All school assignments use two-model consensus. Provider 1: `anthropic/claude-opus-4.6` (via OpenRouter). Provider 2: a different provider model (e.g., `cohere/command-a-03-2025` via OpenRouter, or `openai/gpt-4o` via OpenRouter). Agreement: both models must assign the same school. Disagreement: the excerpt receives review flag `school_disagreement`, `school` is set to the primary model's assignment, `school_confidence` is reduced by 0.2.

2. **Author attribution in ambiguous cases (§4.A.8).** When the dominant layer covers 40-60% of the excerpt text, two-model consensus determines the primary author. Same provider configuration as school classification.

Consensus is NOT used for: segment classification (Phase 2a — single model with structured output is sufficient given validation checks), teaching unit grouping (Phase 2b — single model), topic proposal (taxonomy engine provides correction), evidence detection (pattern-based + single LLM), or self-containment scoring (advisory, not a gate decision).

**Provider fallback.** If the second provider is unavailable (API error after 3 retries with exponential backoff), the engine falls back to single-model with the primary provider. The excerpt's confidence is reduced by 0.1 and `consensus_used: false` is recorded. The excerpt is not blocked — degraded confidence is preferable to no excerpt.

---

## 7. Error Handling

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `EXC_MANIFEST_INVALID` | Fatal | Manifest missing or invalid JSON | Abort. Source stays at `normalized`. |
| `EXC_SCHEMA_UNSUPPORTED` | Fatal | Unrecognized schema version | Abort. |
| `EXC_CONTENT_MISSING` | Fatal | Content stream file missing | Abort. |
| `EXC_CONTENT_COUNT_MISMATCH` | Warning | Manifest count ≠ actual count | Process with actual count. |
| `EXC_CONTENT_UNORDERED` | Fatal | Content units not in unit_index order | Abort. Normalization corruption. |
| `EXC_CONTENT_GAP` | Warning | Gap in unit_index sequence | Skip missing indices. Flag chunks. |
| `EXC_DIVISION_INCONSISTENT` | Warning | Division tree ranges overlap or inconsistent | Fall back to flat processing. |
| `EXC_ASSEMBLY_LAYER_MISMATCH` | Warning | Layer segment exceeds content unit text length | Clamp. Log. |
| `EXC_ASSEMBLY_QURAN_UNCLOSED` | Warning | Open `﴿` bracket with no matching `﴾` | Treat as regular text. Log. |
| `EXC_CLASSIFICATION_COVERAGE_GAP` | Warning | Segment classification covers <95% of chunk text | Fill gaps with `unclassified`. |
| `EXC_CLASSIFICATION_FAILED` | Warning | Classification covers <80% even after retry | Assign entire chunk as one segment. |
| `EXC_GROUPING_COVERAGE_GAP` | Warning | Teaching unit grouping has text gaps | Assign uncovered regions to nearest unit. |
| `EXC_LLM_UNAVAILABLE` | Warning | LLM call fails (timeout, error) after retries | Retry 3x with exponential backoff. If still fails, skip chunk. |
| `EXC_LLM_PARSE_ERROR` | Warning | LLM returns invalid JSON / schema violation | Retry once. If fails, skip chunk. |
| `EXC_FORMAT_DETECTION_FAILED` | Warning | Format-specific strategy detected <2 markers | Fall back to prose strategy. Flag. |
| `EXC_VALIDATION_TEXT_CORRUPTION` | Fatal | Text preservation check failed (D-004) | Abort. Do not write. |
| `EXC_VALIDATION_COVERAGE` | Fatal | Excerpt coverage <99% of substantive text | Abort. Do not write. |
| `EXC_VALIDATION_OVERLAP` | Fatal | Text region appears in 2+ excerpts | Abort. Do not write. |
| `EXC_VALIDATION_SCHEMA` | Fatal | Excerpt fails Pydantic schema validation | Abort. Do not write. |
| `EXC_SIZE_DISTRIBUTION_SKEWED` | Warning | >20% of excerpts outside 50-2000w range | Log. Flag source. |
| `EXC_LOW_CLASSIFICATION_CONFIDENCE` | Warning | Mean segment confidence <0.6 | Log. Flag source. |
| `EXC_LOW_SELF_CONTAINMENT_RATE` | Warning | >30% of excerpts score <0.5 | Log. Flag source. |
| `EXC_COVERAGE_SHORTFALL` | Warning | Post-validation coverage <99% | Log. Flag source. |
| `EXC_CONSENSUS_DEGRADED` | Warning | Second provider unavailable for consensus | Single-model fallback. Reduce confidence. |
| `EXC_WRITE_FAILED` | Fatal | Atomic write failed (disk error) | Remove temp. Retry once. |

**Principle:** Never lose data silently. Every error is logged with: timestamp, source_id, error code, severity, affected chunk_id (if chunk-specific), and recovery action taken.

**Skipped chunks.** When a chunk is skipped due to LLM unavailability or parse errors, its text is NOT lost. The engine creates a synthetic excerpt covering the entire chunk text with: `content_types: ["unclassified"]`, `self_containment_score: 0.0`, `review_flags: ["llm_processing_failed"]`. This ensures complete text coverage even when LLM processing fails for specific chunks.

---

## 8. Configuration

| Parameter | Default | Valid Range | Description |
|-----------|---------|-------------|-------------|
| `min_chunk_words` | 50 | 20-200 | Minimum Arabic word count for a chunk |
| `max_chunk_words` | 5000 | 2000-10000 | Maximum for marker-rich divisions |
| `max_chunk_words_sparse` | 3000 | 1000-5000 | Maximum for marker-sparse divisions |
| `marker_sparse_threshold` | 2.0 | 0.5-5.0 | Markers per 1000w below which a division is "marker-sparse" |
| `min_excerpt_words` | 50 | 20-200 | Minimum teaching unit size before merge |
| `max_tokens_classify_small` | 8192 | 4096-32768 | MAX_TOKENS for classify on chunks ≤2000w |
| `max_tokens_classify_large` | 32768 | 16384-65536 | MAX_TOKENS for classify on chunks >2000w |
| `max_tokens_group` | 8192 | 4096-32768 | MAX_TOKENS for group step |
| `classification_coverage_warn` | 0.95 | 0.80-1.00 | Coverage below this triggers warning |
| `classification_coverage_fail` | 0.80 | 0.50-0.95 | Coverage below this triggers retry |
| `self_containment_warn_threshold` | 0.5 | 0.3-0.7 | Below this, review flag added |
| `attribution_ambiguity_range` | [0.40, 0.60] | — | Layer coverage range triggering consensus |
| `enrichment_batch_size` | 10 | 1-20 | Excerpts per LLM batch for Phase 3 |
| `text_preservation_sample_rate` | 0.10 | 0.05-1.00 | Proportion of excerpts checked for D-004 |
| `llm_model` | `anthropic/claude-opus-4.6` | any OpenRouter model | Primary LLM for Phase 2/3 |
| `consensus_model` | `cohere/command-a-03-2025` | any OpenRouter model | Second model for consensus |
| `llm_temperature` | 0 | 0-1.0 | Temperature for all LLM calls |
| `llm_max_retries` | 3 | 1-5 | Max retries per LLM call |

**Per-science configuration hooks (Level 3 / SCIENCE.md).** Each science may customize:
- School classification vocabulary and patterns
- Evidence detection patterns (which evidence types are common in this science)
- Self-containment expectations (heavily interconnected fiqh vs. self-contained definitions in tajwid)

**Hardcoded constraints:**
- D-004: `primary_text` is never modified. Not configurable.
- D-011: Excerpts within chunks. Not configurable.
- D-023: Metadata pass-through. Not configurable.
- 16-value scholarly function enum. Changes require SPEC update.
- Footnote marker format (`⌜N⌝`). Matches normalization engine.

---

## 9. Current Implementation State

### 9.1 Existing Code

**`engines/excerpting/SPEC.md`** (98KB). Original excerpting SPEC from the 7-engine pipeline. Assumed separate passaging engine input. Superseded by this SPEC_CORE.md.

**`engines/excerpting/contracts.py`** (21KB). Original atom-based schema. Key differences: `atom_ids` → `segment_ids`, `passage_id` → `chunk_id`, `derived_normalized_text` removed, argument/dialogue/resonance capabilities deferred to Stage 2.

**`engines/passaging/SPEC.md`** — absorbed. Format-specific strategies (§4.A.4-§4.A.9) and cross-page assembly (§4.A.2) are design inputs for Phase 1.

### 9.2 Validated Components

**`experiments/architecture_test/run_tests.py`** — LLM schemas (ClassifiedSegment, TeachingUnit) validated on 10 divisions, 5 genres. Zero errors.

**`experiments/format_diversity_test/run_tests.py`** — Extended validation on 13 divisions (verse-commentary, longer prose, masala, QA). Zero errors. MAX_TOKENS=32768 validated for >2000w.

### 9.3 Gap Analysis

All 13 SPEC sections require implementation. No production code exists.

### 9.4 External Dependencies

- **OpenRouter API** via Instructor — all LLM calls
- **Instructor** (MIT) — structured output
- **Pydantic** — schema validation
- **OpenAI SDK** — API client for OpenRouter

---

## 10. Test Requirements

### 10.1 Deterministic Tests (Phase 1)

1. **Cross-page assembly.** Mid-word join, mid-sentence join, paragraph break, footnote renumbering, layer rebasing, Quran citation spanning pages, CRLF normalization. Minimum 10 test cases.
2. **Chunk sizing.** Division exactly at minimum (50w), at maximum (5000w), above maximum (5001w), merge of tiny siblings, split of oversized division, marker-sparse detection. Minimum 10 test cases.
3. **Format-specific strategies.** Each format strategy (prose, verse, Q&A, masala, dictionary, commentary, mixed), including fallback when detection fails. Minimum 8 test cases.

### 10.2 LLM Tests (Phase 2)

4. **Segment classification quality.** Run on 5+ fixture divisions with known scholarly functions. Verify coverage ≥95%, verify known definitions/rulings/evidence classified correctly. These are expensive (real API calls).
5. **Teaching unit grouping quality.** Verify self-contained units, complete argument cycles, no split isnad chains.
6. **Post-processing.** Merge undersized units, coverage verification, ID assignment.

### 10.3 Metadata Enrichment Tests (Phase 3)

7. **Author attribution.** Single-layer source (trivial), multi-layer with clear dominant layer, multi-layer with ambiguous layer split.
8. **School classification.** Source with explicit school metadata, source with text markers, school-independent content.
9. **Evidence detection.** Known Quran citation, known hadith citation, takhrij from footnotes.
10. **Self-containment.** Self-contained definition, dependent excerpt ("as mentioned above").

### 10.4 Integration Tests

11. **Full pipeline.** Run all 3 phases on 3+ normalized packages from the test fixtures. Verify output passes all §5 checks.
12. **Taxonomy compatibility.** Read excerpt stream and verify all fields required by taxonomy SPEC §2.1 are present with correct types.

### 10.5 Gold Baselines

Required before engine evaluation:
- One prose source (simple fiqh or nahw) with hand-verified excerpts
- One commentary-on-verse source (ibn aqil fixture) with hand-verified excerpts
- One Q&A source with hand-verified Q&A pair boundaries
- One multi-layer source with hand-verified author attributions

### 10.6 Adversarial Tests

1. **Empty division tree.** Source with no divisions → verify chunks are created synthetically.
2. **Single-page division.** Division containing one content unit with 20 words → verify merge behavior.
3. **Monster division.** Division with 50,000 words → verify splitting produces reasonable chunks.
4. **Arabic text fidelity.** Excerpt with full tashkeel, hamzat wasl/qat', tatwil characters → verify D-004.
5. **LLM failure resilience.** Simulate LLM unavailability → verify synthetic fallback excerpt is produced.
