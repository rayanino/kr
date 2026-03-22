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
- `proposed_leaf`: string or null. Proposed taxonomy leaf path (e.g., `nahw/المرفوعات/المبتدأ_والخبر/تعريف_المبتدأ`). Null by default — the excerpting engine generates the topic proposal but does not have access to taxonomy trees. May be populated by a future integration where tree awareness is available.
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

- `review_flags`: array of strings. Machine-generated flags for human review. Possible values:
  - `low_self_containment` — self-containment score < 0.5
  - `low_confidence_boundary` — chunk boundary placed by heuristic with low confidence
  - `low_fidelity_content` — any constituent page has fidelity `low` or `very_low`
  - `split_from_large` — chunk was created by splitting an oversized division
  - `merged_siblings` — chunk merges multiple small divisions
  - `uncertain_attribution` — primary author attribution confidence < 0.6
  - `school_disagreement` — multi-model consensus disagreed on school classification
  - `format_detection_failed` — format-specific strategy failed, fell back to prose
  - `marker_sparse_chunk` — chunk text has fewer than 2 structural markers per 1000w
  - `empty_division_tree` — source had no division tree; chunk boundaries are synthetic
  - `cross_topic_candidate` — excerpt may address multiple topics; taxonomy should evaluate
  - `very_short_excerpt` — excerpt is < 50 Arabic words after Phase 2 post-processing
  - `oversized_excerpt` — excerpt exceeds 2000 Arabic words (Phase 2 grouping produced unusually large unit)
  - `layer_attribution_anomaly` — text_layers fingerprint inconsistent with attributed layer

**Provenance fields:**

- `processing_metadata`: object. `engine_version` (string), `model_used` (string — the LLM model for Phase 2/3), `consensus_used` (bool — whether multi-model consensus was applied for attribution decisions), `processing_timestamp` (string — ISO 8601 datetime), `phase_1_strategy` (string — which chunk strategy was applied: `prose`, `verse`, `qa_pair`, `masala_block`, `dictionary_entry`, `commentary_unit`, `flat`).

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
- `division_ids`: array of strings. The `div_id`(s) of the leaf division(s) this chunk covers. Multiple if small sibling divisions were merged.
- `division_path`: array of objects. Path from root to this chunk's position.
- `heading_text`: string or null. Heading text for the primary division. Null for split chunks (except the first piece).
- `unit_range`: object. `start` (int) and `end` (int, inclusive). Content unit index range.
- `assembled_text`: string. The full assembled text of this chunk (cross-page joined).
- `text_layers`: array of `TextLayerSegment`. Layer attribution rebased to assembled text.
- `footnotes`: array of `Footnote`. All footnotes from constituent content units.
- `word_count`: int. Arabic word count of assembled text.
- `sizing_action`: string, one of `direct` (division used as-is), `merged` (tiny divisions merged), `split` (oversized division split).
- `sizing_notes`: string or null. Explanation of merge/split.
- `strategy`: string. Which Phase 1 strategy was applied.
- `physical_pages`: object. Page range.
- `content_flags`: object. Aggregated flags from constituent content units.
- `text_fidelity_min`: string. Lowest fidelity score among constituent units.

### 3.4 Guarantees About the Excerpt Stream

- **Source-agnostic.** The excerpt schema is identical regardless of source type. No field, enum, or convention depends on the source format.
- **Ordering.** Excerpts are ordered by document order. `excerpt_id` sequence numbers are monotonically increasing within a source.
- **Complete text coverage.** Every word of substantive text (excluding TOC, index, and blank pages) in the normalized package appears in exactly one excerpt's `primary_text`. No substantive text is lost between chunks, between segments, or between excerpts. The text coverage invariant is verified by §5 check 1.
- **Non-overlapping.** No text region appears in more than one excerpt. Segment boundaries partition the chunk text without overlap. Excerpt boundaries partition the chunk's segments without overlap.
- **D-004 text preservation.** The `primary_text` field of every excerpt is a verbatim substring of the Phase 1 chunk text, which is itself assembled from normalization content units without modification. Diacritics preserved exactly. No character added, removed, or substituted.
- **D-011 chunk containment.** Every excerpt's text comes from exactly one chunk. No excerpt spans two chunks. The chunk boundary is the containment boundary.
- **D-023 metadata pass-through.** Every excerpt carries `source_id` for upstream metadata access, `division_path` for structural context, `physical_pages` for citation, `text_layers` for authorship attribution, `content_flags` for downstream hints, and `text_fidelity` for quality awareness. The excerpting engine ADDS metadata (segment classification, teaching unit grouping, attribution, topic, school, evidence); it NEVER strips upstream metadata fields.
- **Excerpt self-sufficiency.** Each excerpt record contains all text and metadata needed for taxonomy placement and synthesis. Downstream engines do not need to access the normalized package or the chunk/segment streams — only the excerpt stream and the source metadata record (via `source_id`).

**Metadata pass-through (D-023).** The excerpting engine preserves all upstream metadata by reference (`source_id`) and adds:
- Chunk boundaries, segment classification, teaching unit grouping
- Rebased text layer segments
- Author attribution with primary/quoted scholar distinction
- School classification with confidence
- Topic proposal for taxonomy placement
- Evidence reference detection with structured data
- Self-containment scoring
- Content type aggregation from scholarly function classification
- Review flags for quality gating
- Processing provenance

**Source registry update.** Upon successful excerpting, the source's processing status is updated from `normalized` to `excerpted`. The excerpt stream path is recorded.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Processing Overview

Excerpting proceeds in three sequential phases:

**Phase 1 — Deterministic Preprocessing (absorbs passaging)**
1. Load and validate (§2): Read manifest and content stream, validate input contract.
2. Assemble text (§4.A.2): Join cross-page text using `boundary_continuity` signals, produce continuous text blocks aligned to division boundaries.
3. Create chunks (§4.A.3): Map divisions to right-sized chunks: pass-through, merge, or split based on Arabic word count.
4. Apply format-specific strategies (§4.A.4): For verse, Q&A, masala, dictionary, and commentary sources, apply specialized chunk boundary logic.

**Phase 2 — LLM Teaching Unit Extraction (validated by experiments)**
5. Classify segments (§4.A.5): For each chunk, send assembled text to LLM. Receive classified segments — each sentence or bonded group of sentences labeled by scholarly function.
6. Group into teaching units (§4.A.6): Send classified segments + original text to LLM. Receive teaching unit groupings — each a self-contained scholarly segment.
7. Post-process (§4.A.7): Merge undersized units, verify complete text coverage, assign segment and excerpt IDs.

**Phase 3 — Metadata Enrichment**
8. Author attribution (§4.A.8): Determine primary author and quoted scholars.
9. School classification (§4.A.9): Determine scholarly school with multi-model consensus.
10. Evidence reference detection (§4.A.10): Detect and structure Quran, hadith, ijma, qiyas references.
11. Topic proposal and science classification (§4.A.11): Generate `excerpt_topic` and `science_id`.
12. Self-containment evaluation (§4.A.12): Score each excerpt's independent understandability.
13. Output assembly and validation (§4.A.13): Assemble final excerpt records, run self-validation, write to disk.

The engine processes one source at a time. Batch processing of multiple sources is an orchestration concern outside this SPEC.

**Example:** Processing شرح ابن عقيل على الألفية (source_id `nahw_ibnaqil_sharh_alfiyyah_a1b2`, structural_format `commentary`, 847 content units, multi-layer) → Phase 1: validate manifest, load 847 units, assemble text within 142 leaf divisions, produce ~142 chunks (most pass-through; a few tiny divisions merged, a few large ones split) → Phase 2: classify segments in each chunk (yielding ~8-15 segments per chunk), group segments into teaching units (yielding ~5-12 teaching units per chunk, totaling ~800-1200 across the source) → Phase 3: attribute each unit to ابن مالك (matn) or ابن عقيل (sharh) based on text_layers, classify school (not applicable for nahw), detect evidence references, generate topics, score self-containment → Output: ~800-1200 draft excerpts in excerpts.jsonl.

**Processing budget.** For a typical 500-page Shamela source with ~100 leaf divisions:
- Phase 1: 0 API calls (deterministic)
- Phase 2: ~200 API calls (100 classify + 100 group), each processing 200-800 words of Arabic text
- Phase 3: ~100-200 API calls (attribution + topic + self-containment per teaching unit batch)
- Total: ~300-400 API calls per source

For the full 2,519-book Shamela collection: ~750K-1M API calls. At current Opus 4.6 pricing via OpenRouter, this is the largest cost center in the pipeline. All calls go through OpenRouter ONLY (model: `anthropic/claude-opus-4.6`).

[§4.A.2 through §4.A.13 — CONTINUED IN NEXT SECTION]

### §4.B — Transformative Capabilities (Stage 2)

These capabilities extend the core but are not required for the engine's fundamental purpose. They are deferred to Stage 2 to maintain build focus. Each includes an extension hook documenting what the core must not assume.

#### §4.B.1 — Argument Discourse Mapping

**Capability:** Beyond Phase 2's per-segment scholarly function classification, map the argumentative structure of each excerpt: which segments form claims, which provide evidence, which are counter-arguments, and how they relate. Produces a structured argument map that the synthesis engine uses to generate entries with proper argumentative flow.

**Extension hook:** The core excerpt schema includes `content_types` (aggregated from segments). Stage 2 adds `argument_map: Optional[list[ArgumentMapSegment]]` with per-segment argumentative roles and relationships. The core must not assume `argument_map` is present.

[NOT YET IMPLEMENTED]

#### §4.B.2 — Cross-Source Semantic Deduplication

**Capability:** When 2+ sources quote the same hadith, or paraphrase the same well-known definition, detect the semantic overlap and signal it to the taxonomy engine. Prevents redundant entries.

**Extension hook:** The core processes each source independently. Stage 2 adds `semantic_duplicates: Optional[list[SemanticDuplicateLink]]` to the excerpt schema. The core must not assume cross-source data is available.

[NOT YET IMPLEMENTED]

#### §4.B.3 — Evidence Chain Reconstruction

**Capability:** Reconstruct the logical structure of evidence chains within excerpts: which claims are supported by which evidence, what type of reasoning connects them, and whether the argument is logically complete.

**Extension hook:** Stage 2 adds `evidence_chain: Optional[EvidenceChain]` to the excerpt schema. The core's `evidence_refs` provides flat evidence detection; Stage 2 adds the argumentative structure.

[NOT YET IMPLEMENTED]

#### §4.B.4 — Masala Detection and Issue Formulation

**Capability:** Detect مسألة-bearing excerpts and extract the precise scholarly question being debated, enabling the taxonomy engine to match excerpts from different sources that address the same مسألة.

**Extension hook:** Stage 2 adds `masala_analysis: Optional[MasalaAnalysis]` to the excerpt schema. The core's `excerpt_topic` provides a topic description; Stage 2 adds structured مسألة identification.

[NOT YET IMPLEMENTED]

#### §4.B.5 — Self-Containment Repair

**Capability:** When an excerpt scores low on self-containment, automatically suggest or apply repairs: adding context segments from adjacent text, generating a brief context note, or flagging a passaging error.

**Extension hook:** Stage 2 adds `repair_suggestions: Optional[list[RepairSuggestion]]` to the excerpt schema. The core flags low-self-containment excerpts; Stage 2 attempts repair.

[NOT YET IMPLEMENTED]

#### §4.B.6 — Scholarly Dialogue Links

**Capability:** Detect when one excerpt responds to, refines, or contradicts another excerpt — either within the same source or across sources. Builds a scholarly dialogue graph.

**Extension hook:** Stage 2 adds `dialogue_links: Optional[list[DialogueLink]]` to the excerpt schema. Populated during incremental processing.

[NOT YET IMPLEMENTED]

#### §4.B.7 — Cross-Source Textual Resonance

**Capability:** Detect textual borrowing, structural mirroring, and terminological echoes between excerpts across different sources. Identifies the scholarly transmission network.

**Extension hook:** Stage 2 adds `resonance_links: Optional[list[ResonanceLink]]` to the excerpt schema. Populated during incremental processing.

[NOT YET IMPLEMENTED]

---

## 5. Validation and Quality

[TO BE COMPLETED — will include Layer 1 self-validation checks, Layer 2 automated quality checks, Layer 3 human gate integration, and threat prevention mapping]

---

## 6. Consensus Integration

[TO BE COMPLETED — will define which decisions use multi-model consensus: school classification and author attribution]

---

## 7. Error Handling

[TO BE COMPLETED — will define all error codes with severity, trigger, and recovery]

---

## 8. Configuration

[TO BE COMPLETED — will list all configurable parameters with defaults and valid ranges]

---

## 9. Current Implementation State

### 9.1 Existing Code

**`engines/excerpting/SPEC.md`** (98,180 bytes). The original excerpting engine SPEC from the 7-engine pipeline design. This SPEC assumed a separate passaging engine provided passage-level input. The new SPEC_CORE.md supersedes it — the excerpting engine now handles passaging internally.

**`engines/excerpting/contracts.py`** (21,720 bytes). The original excerpt record schema with 40+ fields. Designed for the atom-based architecture where a separate atomization engine classified scholarly functions. Key differences from the new schema:
- `atom_ids` / `core_atom_ids` / `context_atom_ids` → replaced by `segment_ids` / `core_segment_ids` / `context_segments`
- `passage_id` → replaced by `chunk_id` (Phase 1 produces chunks, not passages)
- `derived_normalized_text` → removed (search indexing is a downstream concern)
- `argument_role` / `argument_map` → deferred to Stage 2 (§4.B.1)
- `semantic_duplicates` / `dialogue_links` / `resonance_links` → deferred to Stage 2

**`engines/excerpting/src/`** — contains ABD-era excerpt extraction code. No longer applicable to the KR architecture.

**`engines/passaging/SPEC.md`** — the passaging engine SPEC that is now absorbed. Its format-specific strategies (§4.A.4-§4.A.9) and cross-page assembly logic (§4.A.2) are the primary design inputs for Phase 1.

### 9.2 Validated Components

**`experiments/architecture_test/run_tests.py`** — the LLM extraction test runner with validated schemas (ClassifiedSegment, TeachingUnit, ExtractionResult, ClassificationResult). These Pydantic schemas are the starting point for Phase 2's LLM interface. Validated on 10 divisions, 5 genres, zero errors.

**`experiments/format_diversity_test/run_tests.py`** — extended test runner with MAX_TOKENS=32768 for larger divisions. Validated on 13 divisions (6 verse-commentary, 4 longer prose 2500-3100w, 2 masala, 1 QA), zero errors.

### 9.3 Gaps Between Current Code and This SPEC

| SPEC Feature | Current State | Gap |
|---|---|---|
| Phase 1: Cross-page assembly (§4.A.2) | Not implemented | Full implementation needed |
| Phase 1: Division-to-chunk mapping (§4.A.3) | Not implemented | Full implementation needed |
| Phase 1: Format-specific strategies (§4.A.4) | Passaging SPEC has detailed strategies; no code | Implement adapted strategies |
| Phase 2: Segment classification (§4.A.5) | Experiment schemas validated | Formalize into production schemas |
| Phase 2: Teaching unit grouping (§4.A.6) | Experiment schemas validated | Formalize into production schemas |
| Phase 2: Post-processing (§4.A.7) | Not implemented | Full implementation needed |
| Phase 3: All enrichment steps (§4.A.8-§4.A.12) | Old SPEC has designs; no code | Full implementation needed |
| Output assembly (§4.A.13) | Not implemented | Full implementation needed |
| New contracts.py | Old contracts exist (atom-based) | Rewrite for segment-based architecture |
| Self-validation (§5) | Not implemented | Full implementation needed |

### 9.4 External Dependencies

- **OpenRouter API** (via `instructor` library) — all LLM calls for Phase 2 and Phase 3. Model: `anthropic/claude-opus-4.6`. Temperature: 0 for deterministic classification; 0 for grouping.
- **Instructor** (MIT license) — structured LLM output with Pydantic validation. Used in both experiments.
- **Pydantic** — schema definition and validation.
- **OpenAI SDK** (via Instructor) — API client for OpenRouter.
- No document parsing libraries needed — the engine operates on already-normalized JSON data.
- No sentence embedding models needed for core (Stage 1). Stage 2 deduplication (§4.B.2) may require `intfloat/multilingual-e5-large`.

---

## 10. Test Requirements

[TO BE COMPLETED — will define test categories, gold baselines, regression testing, and adversarial test cases]
