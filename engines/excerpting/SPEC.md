# Excerpting Engine — SPEC

**Engine:** Excerpting (محرك الاقتباس)
**Version:** 2.0.0
**Date:** 2026-03-22
**Author:** Claude Chat (Architect)
**Status:** DRAFT — writing section by section per SPEC_OUTLINE.md dependency order

**Supersedes:** `reference/archive/abd_code/excerpting/SPEC_old_original.md` (1038 lines, 7-engine architecture — BLOCKED)
and `reference/archive/abd_code/excerpting/SPEC_old_blocked.md` (868 lines, rewrite attempt — BLOCKED, 16 findings)

**Governing documents:** `KNOWLEDGE_INTEGRITY.md`, `SPEC_OUTLINE.md`, `ARCHITECTURE_DECISION.md`

---

## §2.3 — Internal Data Model

The excerpting engine transforms a `NormalizedPackage` (from `engines/normalization/contracts.py`) into a stream of `ExcerptRecord` objects. Three intermediate representations flow between the engine's internal phases:

```
NormalizedPackage (input — normalization contracts)
  → Phase 1 (deterministic) → AssembledChunk[]
    → Phase 2a (LLM classify) → ClassifiedSegment[]
      → Phase 2b (LLM group) → TeachingUnit[]
        → Phase 3 (enrich) → ExcerptRecord[] (output — §2.2)
```

Each intermediate is simpler than its successor. Phase 1 output is fully deterministic and independently unit-testable. Phase 2 output is LLM-driven with structural constraints. Phase 3 adds semantic richness. This separation means Phase 1 bugs are caught without any LLM cost, and Phase 2 bugs are isolated from metadata enrichment logic.

**Design decision (Option C — Hybrid):** The experiment (`experiments/architecture_test/run_tests.py`) validated `ClassifiedSegment` and `TeachingUnit` as sufficient intermediate types for LLM extraction. Phase 3 enrichment (attribution, topics, evidence references) is added after extraction, not embedded in the LLM call. This avoids the complexity of the old atomization SPEC's pre-computed relations and bonds, which were never empirically validated.

### §2.3.1 — Enumerations

#### ScholarlyFunction

The 16-type flat taxonomy for segment classification. Validated across 23 divisions in 7 formats (experiments `run_tests.py` and `format_diversity_test`). Replaces the old atomization SPEC's separate 7 structural types + 16 scholarly functions with a single classification.

| Value | Description | Arabic marker examples |
|-------|-------------|----------------------|
| `definition` | Term definition with explanation | تعريف، معنى، حقيقة |
| `rule_statement` | Legal ruling or grammatical rule | يجب، يحرم، لا يجوز، حكمه |
| `evidence_quran` | Quranic citation with introduction | قال تعالى، لقوله تعالى |
| `evidence_hadith` | Hadith with chain or reference | روى، عن النبي ﷺ، أخرجه |
| `evidence_ijma` | Consensus citation | أجمع العلماء، بالإجماع |
| `evidence_qiyas` | Analogical reasoning | قياساً على، بالقياس، والعلة |
| `evidence_rational` | Rational/logical argument | لأن، ولأنه، والدليل العقلي |
| `opinion_statement` | Scholar's named position | قال أبو حنيفة، ذهب الشافعي، وعند مالك |
| `refutation` | Counter-argument or objection | ورد عليه بأن، واعترض، ونوقش |
| `example` | Illustrative example | نحو، مثال ذلك، كقولك، كأن يقول |
| `condition_exception` | Conditional or exception to a rule | إلا، ما لم، بشرط، إن كان |
| `cross_reference` | Reference to another section or work | كما تقدم، انظر، سيأتي |
| `narration` | Historical narration or isnad | روي أن، أخبرنا، حدثنا |
| `editorial_note` | Editor's or commentator's insertion | قال المحقق، في بعض النسخ، كذا في الأصل |
| `structural_transition` | Chapter heading, basmala, transition | باب، فصل، بسم الله الرحمن الرحيم |
| `unclassified` | Cannot determine scholarly function | — |

The Arabic markers listed are non-exhaustive examples to aid human understanding. The LLM classifies based on semantic analysis of the text, not marker matching. Marker-based pre-classification was considered (old atomization SPEC §4.A.4) and rejected: the experiment showed the LLM handles classification reliably without it, and marker-based approaches produce false positives on conjugated Arabic verb forms (normalization engine lesson: `وذهب` matches `وذهبت`/`وذهبوا`).

#### SelfContainmentLevel

The self-containment assessment for a teaching unit. Defined formally in §3; used in the data model here.

| Value | Meaning | Phase 3 action |
|-------|---------|---------------|
| `FULL` | All §3 criteria met. Excerpt stands alone. | No repair needed. |
| `PARTIAL` | Most criteria met, but some context would help. | Phase 3 adds `context_hint`. |
| `DEPENDENT` | Cannot be understood alone. Requires connection to adjacent content. | Flagged for human gate review. |

**Design extension note:** The experiment used a binary `self_contained` boolean. The 3-level system extends this: `PARTIAL` captures cases where the experiment's `self_containment_notes` field was populated but the excerpt was still marked `self_contained=true`. This provides actionable information for Phase 3 repair and human gates. The mapping is: experiment `true` with no notes → `FULL`; experiment `true` with notes → `PARTIAL`; experiment `false` → `DEPENDENT`. Must be validated during build evaluation.

**T-4 defense:** A `DEPENDENT` excerpt reaching the taxonomy engine without its dependency resolved is a knowledge integrity violation — the owner would study an incomplete argument.

### §2.3.2 — AssembledChunk (Phase 1 Output)

One `AssembledChunk` represents a processable unit of text: one leaf division (or a merged/split portion thereof) with all cross-page text assembled into a single continuous string. Phase 1 is fully deterministic — no LLM calls.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chunk_id` | `str` | yes | Unique identifier. Format: `{div_id}` for unsplit divisions; `{div_id}_chunk_{N}` for split divisions (N is 0-based). |
| `source_id` | `str` | yes | Inherited from manifest. |
| `div_id` | `str` | yes | The leaf division this chunk derives from. Format per normalization: `div_{source_id}_{depth}_{index}`. |
| `div_path` | `list[str]` | yes | Heading hierarchy from root to this division. Each element is the `heading_text` of an ancestor `DivisionNode`, ordered root-first. Example: `["كتاب الصلاة", "باب صفة الصلاة", "فصل في الركوع"]`. |
| `assembled_text` | `str` | yes | The full text of this chunk, assembled from constituent `ContentUnit.primary_text` values joined per boundary continuity rules (§4.3). All diacritics preserved exactly — no Unicode normalization. Footnote reference markers (`⌜N⌝`) preserved inline. |
| `word_count` | `int` | yes | Arabic word count of `assembled_text`. Counts whitespace-delimited tokens containing ≥1 Arabic character (U+0600–U+06FF). Used for merge/split threshold decisions (§4.4, §4.5). |
| `total_tokens` | `int` | yes | Total whitespace-delimited token count: `len(assembled_text.split())`. Includes all tokens (Arabic, numbers, markers). Used as the coordinate space for word offsets in Phase 2. |
| `text_layers` | `list[TextLayerSegment]` | yes | Layer attribution segments rebased to `assembled_text` character offsets (§4.6). Every character in `assembled_text` is covered by exactly one segment. Types from `engines/normalization/contracts.py::TextLayerSegment`. |
| `footnotes` | `list[Footnote]` | yes | All footnotes from constituent content units, deduplicated by `ref_marker`, order preserved. Types from `engines/normalization/contracts.py::Footnote`. |
| `content_flags` | `ContentFlags` | yes | OR-aggregate across all constituent content units. If any unit has `has_verse=true`, the chunk has `has_verse=true`. Type from `engines/normalization/contracts.py::ContentFlags`. |
| `physical_pages` | `list[PhysicalPage]` | yes | Physical page records from all constituent content units, in order. Type from `engines/normalization/contracts.py::PhysicalPage`. |
| `structural_format` | `StructuralFormat` | yes | Inherited from manifest `structural_format`. Type from `engines/normalization/contracts.py::StructuralFormat`. |
| `heading_alignment_ok` | `bool` | yes | Whether the division heading aligns with the assembled text per §4.8 heading alignment filter. `false` flags a potential misalignment for human review. |
| `assembly_metadata` | `AssemblyMetadata` | yes | Provenance record for how this chunk was assembled. See below. |
| `merge_history` | `list[str]` | no | Present only when tiny divisions were merged (§4.4). List of original `div_id` values that were merged to form this chunk. Absent (null) for unmerged chunks. |
| `split_info` | `SplitInfo` | no | Present only when an oversized division was split (§4.5). Absent (null) for unsplit chunks. See below. |

**AssemblyMetadata** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `constituent_unit_indices` | `list[int]` | The `unit_index` values of all `ContentUnit` objects that were assembled into this chunk, in order. |
| `join_points` | `list[JoinPoint]` | One entry per page boundary within this chunk. |

**JoinPoint** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `after_unit_index` | `int` | The `unit_index` of the page before this join. |
| `before_unit_index` | `int` | The `unit_index` of the page after this join. |
| `boundary_type` | `BoundaryContinuityType` | The boundary continuity type used for joining. Type from normalization contracts. |
| `separator_used` | `str` | The actual separator string inserted: `""` for mid_sentence, `"\n"` for mid_paragraph/mid_argument/unknown, `"\n\n"` for section_break/division_break. |
| `char_offset_in_assembled` | `int` | Character offset in `assembled_text` where this join occurs. |

**SplitInfo** (sub-type):

| Field | Type | Description |
|-------|------|-------------|
| `original_div_id` | `str` | The `div_id` of the division before splitting. |
| `chunk_index` | `int` | 0-based index of this chunk within the split result. |
| `total_chunks` | `int` | Total number of chunks the division was split into. |
| `split_method` | `str` | One of: `"heading_marker"`, `"section_break"`, `"paragraph_break"`, `"sentence_boundary"`. |

**Invariants:**
- I-AC-1: `word_count` equals the count of whitespace-delimited tokens in `assembled_text` that contain ≥1 Arabic character. `total_tokens` equals `len(assembled_text.split())`. Both are computed from `assembled_text` — never set independently.
- I-AC-2: The union of character ranges in `text_layers` exactly covers `[0, len(assembled_text))`. No gaps, no overlaps.
- I-AC-3: Every `ref_marker` in `footnotes` appears in `assembled_text` as `⌜{ref_marker}⌝`.
- I-AC-4: `constituent_unit_indices` is a contiguous ascending sequence. For unmerged, unsplit chunks: it matches the `DivisionNode`'s `[start_unit_index, end_unit_index]` range (inclusive). For merged chunks: it spans the union of all merged divisions' content unit ranges. For split chunks: all chunks from the same split share the same `constituent_unit_indices` (the original division's full range), because splitting occurs on the assembled text, not on content units.
- I-AC-5: If `split_info` is present, `chunk_id` ends with `_chunk_{split_info.chunk_index}`.
- I-AC-6: If `merge_history` is present, it contains ≥2 `div_id` values, and the first element equals `div_id`.
- I-AC-7: `merge_history` and `split_info` are mutually exclusive. A chunk is either merged, split, or neither — never both.

### §2.3.3 — ClassifiedSegment (Phase 2a Output)

One `ClassifiedSegment` represents a contiguous span of text within an `AssembledChunk` that serves a single scholarly function. Produced by the Phase 2a LLM classification call (§5.2).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `segment_index` | `int` | yes | 0-based index within this chunk's classification result. |
| `start_word` | `int` | yes | Start word offset in `assembled_text` (0-based, inclusive). |
| `end_word` | `int` | yes | End word offset in `assembled_text` (0-based, inclusive). |
| `text_snippet` | `str` | yes | First 50 characters of this segment's text, copied exactly from `assembled_text`. |
| `scholarly_function` | `ScholarlyFunction` | yes | The segment's classified scholarly function from the 16-type taxonomy. |
| `confidence` | `float` | yes | Classification confidence, range [0.0, 1.0]. |

**Word offset convention and normalization:** The canonical tokenization is `assembled_text.split()` (Python whitespace split). Both `start_word` and `end_word` are **inclusive** indices into this token list. The text of segment `s` is: `" ".join(assembled_text.split()[s.start_word : s.end_word + 1])`.

**LLM offset alignment (critical implementation detail):** The experiment revealed that the LLM produces internally consistent word offsets (perfectly contiguous — 0 gaps across 162 boundaries in the Taysir div_661 test) but uses its own tokenization that does not match Python `text.split()`. Example: a 3643-token text produced segments ending at word 4172. The LLM's offsets are self-consistent but not directly usable for text extraction.

Therefore, §5.4 (coverage verification) includes a mandatory **offset normalization step** that maps LLM-produced offsets to canonical token positions. The normalization uses the `text_snippet` fields as alignment anchors — each segment's `text_snippet` (copied from the actual text by the LLM) is located in the token stream, and the segment's boundaries are adjusted to match. The invariants below describe the **post-normalization** state — what downstream phases can rely on.

**Invariants (post-normalization):**
- I-CS-1: Segments are ordered by `segment_index` which equals their position in the list (0, 1, 2, ...).
- I-CS-2: Segments are contiguous: for consecutive segments `s[i]` and `s[i+1]`, `s[i+1].start_word == s[i].end_word + 1`.
- I-CS-3: First segment starts at word 0: `segments[0].start_word == 0`.
- I-CS-4: Last segment ends at the last token: `segments[-1].end_word == chunk.total_tokens - 1`.
- I-CS-5: Full coverage: the union of all segment word ranges equals `[0, chunk.total_tokens - 1]`. No gaps, no overlaps.
- I-CS-6: `confidence` is in range `[0.0, 1.0]`.

These invariants are enforced by §5.4 (coverage verification). If the LLM output cannot be normalized to satisfy these invariants (e.g., `text_snippet` cannot be located in the token stream), the result is rejected and retried per §8.2.

### §2.3.4 — TeachingUnit (Phase 2b Output)

One `TeachingUnit` represents the smallest segment of text a student can study and learn something complete from. It groups one or more `ClassifiedSegment` objects into a pedagogically coherent unit. Produced by the Phase 2b LLM grouping call (§5.3).

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `unit_index` | `int` | yes | 0-based index within this chunk's grouping result. |
| `segment_indices` | `list[int]` | yes | The `segment_index` values of the `ClassifiedSegment` objects composing this unit. Must be a contiguous ascending sequence (no interleaving). |
| `start_word` | `int` | yes | Start word offset in `assembled_text` (0-based, inclusive). Equals the `start_word` of the first constituent segment. |
| `end_word` | `int` | yes | End word offset in `assembled_text` (0-based, inclusive). Equals the `end_word` of the last constituent segment. |
| `text_snippet` | `str` | yes | First 80 characters of this unit's text, copied exactly from `assembled_text`. |
| `primary_function` | `ScholarlyFunction` | yes | The dominant scholarly function of this unit, determined by the LLM from the constituent segments' functions. |
| `secondary_functions` | `list[ScholarlyFunction]` | yes | Additional scholarly functions present in this unit (may be empty). |
| `description_arabic` | `str` | yes | Brief Arabic description of what this unit teaches. Target range: 5–35 Arabic words. Written by the LLM. |
| `self_containment` | `SelfContainmentLevel` | yes | The unit's self-containment assessment per §3. |
| `self_containment_notes` | `str` | no | Present when `self_containment` is `PARTIAL` or `DEPENDENT`. Describes what context is missing. Written by the LLM. Must be null/absent when `self_containment` is `FULL`. |

**Invariants:**
- I-TU-1: Units are ordered by `unit_index` which equals their position in the list (0, 1, 2, ...).
- I-TU-2: `segment_indices` is a contiguous ascending sequence (e.g., `[3, 4, 5]`, never `[3, 5]` or `[5, 3]`).
- I-TU-3: Every `ClassifiedSegment` is assigned to exactly one `TeachingUnit`. The union of all `segment_indices` across all units equals `{0, 1, ..., total_segments - 1}`.
- I-TU-4: Units are contiguous in word space: for consecutive units `u[i]` and `u[i+1]`, `u[i+1].start_word == u[i].end_word + 1`.
- I-TU-5: `start_word` equals `segments[segment_indices[0]].start_word` and `end_word` equals `segments[segment_indices[-1]].end_word`.
- I-TU-6: If `self_containment` is `FULL`, then `self_containment_notes` must be null/absent.
- I-TU-7: If `self_containment` is `PARTIAL` or `DEPENDENT`, then `self_containment_notes` must be present and non-empty.
- I-TU-8: `description_arabic` contains between 5 and 35 Arabic words (same word-counting rule as `word_count`). Descriptions outside this range trigger a warning but do not reject the unit — the field is informational, not structural.
- I-TU-9: `primary_function` is one of the functions present in the constituent segments (not invented).

### §2.3.5 — ExcerptRecord (Phase 3 Output)

One `ExcerptRecord` is the engine's final output: a `TeachingUnit` enriched with attribution, topic classification, evidence references, and cross-reference metadata. Fully specified in §2.2 (Output Contract). Defined here in summary to complete the data flow.

An `ExcerptRecord` contains all `TeachingUnit` fields plus Phase 3 enrichment:

- `excerpt_id`: globally unique identifier (`exc_{source_id}_{div_id}_{unit_index}`)
- Attribution metadata: author layer(s), school, confidence
- Topic classification: 1–3 topic keywords for taxonomy placement
- Evidence references: structured Quran/hadith citations extracted from the text
- Cross-references: resolved implicit references (كما تقدم → target div_id)
- Context hint: added text for `PARTIAL` self-containment cases
- Human gate flags: which decisions need owner review

The full field specification is in §2.2, written after all processing phases are defined.

### §2.3.6 — Design Constraints

**D-011 (Division/Chunk Containment):** No intermediate type spans a chunk boundary. `AssembledChunk` is the unit of LLM processing — the LLM receives one chunk's `assembled_text` and cannot reference text from another chunk. This is structurally enforced: the Phase 2 prompt receives only one chunk at a time. Cross-chunk teaching units are impossible by construction, not by validation.

**D-023 (Metadata Passthrough):** No normalization metadata field is dropped. `source_id` flows through every intermediate. `text_layers` are rebased but never discarded. `footnotes` are aggregated but never filtered (filtering to relevant footnotes happens in Phase 3 per-excerpt). `content_flags` are aggregated, never reduced. The `AssembledChunk` carries everything downstream phases might need.

**Word offset coordinate system:** All word offsets across all intermediate types use the same coordinate system — words of `assembled_text` split on whitespace, 0-based, inclusive on both ends. This means a `TeachingUnit`'s `start_word`/`end_word` can be directly used to extract text from the `AssembledChunk`'s `assembled_text` without any offset translation. This guarantee holds because §5.4 normalizes LLM-produced offsets to this canonical tokenization before any downstream use.

**Immutability:** `assembled_text` is write-once at Phase 1 and never modified by subsequent phases. Phase 2 and Phase 3 add metadata — they never alter the text. This defends against T-1 (Silent Text Corruption): the text the owner reads in a final excerpt is exactly the text that was assembled from the normalized content units.

---

## §2.1 — Input Contract

The excerpting engine consumes one `NormalizedPackage` at a time — the output of the normalization engine for a single source. The authoritative schema is `engines/normalization/contracts.py`. This section specifies which fields the excerpting engine reads, which it passes through, and what pre-conditions must hold.

### §2.1.1 — Input Files

For each source with `source_id`:

| File | Schema | Description |
|------|--------|-------------|
| `library/sources/{source_id}/normalized/manifest.json` | `NormalizedManifest` | Source-level metadata, division tree, layer map, quality report. |
| `library/sources/{source_id}/normalized/content.jsonl` | `ContentUnit` (one per line) | Page-level content. One record per physical page, ordered by `unit_index`. |

The engine reads both files at startup for the source being processed. The manifest is loaded fully into memory. Content units are loaded on demand per division (by `unit_index` range).

### §2.1.2 — Manifest Fields Used

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `source_id` | `str` | All phases | Propagated to every intermediate and output type. |
| `division_tree` | `list[DivisionNode]` | Phase 1 (§4.2) | Walked to identify leaf divisions. Each `DivisionNode` provides `div_id`, `heading_text`, `heading_level`, `start_unit_index`, `end_unit_index` (inclusive), `children`, `division_type`, `confidence`. |
| `layer_map` | `list[LayerMapEntry]` | Phase 3 (§7.1) | Maps layer types to authors. Used for attribution: `layer_type` → `author_canonical_id` / `author_name_arabic`. Single-layer sources have one entry. |
| `structural_format` | `StructuralFormat` | Phase 1 (§4.1) | Inherited by every `AssembledChunk`. Informs domain-specific handling in §6. The confirmed format, not `structural_format_proposed`. |
| `total_content_units` | `int` | Phase 1 validation (§4.9) | Used by V-P1-2 to verify full coverage: union of all chunks' content units must equal `{0, ..., total_content_units - 1}`. |
| `verse_detection` | `bool` | Phase 1 (§4) | Informational flag. When `true`, the source contains versified text. Does not change Phase 1 behavior (verse-commentary handling is LLM-driven in Phase 2, not structural in Phase 1). |
| `quality_report` | `QualityReport` | Logging | `overall_confidence` logged at start. Sources with `MINIMAL` heading confidence are flagged for potential quality issues (few divisions → large chunks). Not a processing gate. |
| `text_fidelity_summary` | `TextFidelitySummary` | Logging | `high_fidelity_pct` logged. Not a processing gate — the excerpting engine processes all sources regardless of fidelity. |

**Manifest fields consulted when present (optional):**

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `content_census` | `ContentCensus` (nullable) | Phase 1 (§4.5) | When present, `structural_depth.division_count` informs splitting threshold adjustment for books with minimal division trees. Absent for sources where §4.B.5 was not run. |
| `discourse_flow_summary` | `dict` (nullable) | Phase 3 (§7.2) | When present, `dominant_discourse_type` provides a hint for topic classification. Absent for sources where §4.B.10 was not run. |

**Manifest fields passed through (D-023):**

Every manifest field not listed above is passed through to the output untouched. The excerpting engine never modifies or drops manifest-level metadata. Specifically: `schema_version`, `normalizer_id`, `normalization_utc`, `structural_format_proposed`, `verse_numbering_scheme`, `normalization_warnings`, `tahqiq_topology`, `layer_fingerprints` — all preserved in the per-source output summary for downstream engines.

### §2.1.3 — ContentUnit Fields Used

Each `ContentUnit` corresponds to one physical page. The excerpting engine reads these fields during Phase 1 assembly:

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `unit_index` | `int` | Phase 1 (§4.3) | Identifies which units belong to a division. Units are selected by `[start_unit_index, end_unit_index]` range from the `DivisionNode`. |
| `primary_text` | `str` | Phase 1 (§4.3) | Concatenated across pages to form `assembled_text`. All diacritics preserved exactly. No Unicode normalization applied. |
| `text_layers` | `list[TextLayerSegment]` | Phase 1 (§4.6) | Rebased from per-page character offsets to assembled-text character offsets. Each segment's `layer_type`, `author_canonical_id`, `start`, `end`, `confidence` are preserved. |
| `footnotes` | `list[Footnote]` | Phase 1 (§4.7) | Collected from all constituent pages, deduplicated by `ref_marker`. All fields preserved: `ref_marker`, `text`, `footnote_type`, `confidence`, plus type-specific data when present. |
| `structural_markers` | `StructuralMarkers` | Phase 1 (§4.5, §4.8) | `heading_detected`, `heading_text` used for split-point detection in oversized divisions. `heading_text` used for heading alignment verification. |
| `boundary_continuity` | `BoundaryContinuity` (nullable) | Phase 1 (§4.3) | Determines separator between consecutive pages during assembly. `type` field maps to separator string. Null on last unit and non-paginated sources — treated as `"\n"` separator. |
| `content_flags` | `ContentFlags` | Phase 1 (§4.7) | OR-aggregated across pages into chunk-level flags. `is_toc_page` and `is_index_page` used by §4.2 to skip non-content divisions. |
| `physical_page` | `PhysicalPage` | Phase 1 (§4.7) | Collected into chunk's `physical_pages` list for citation support. |
| `verse_info` | `VerseInfo` (nullable) | Accessible | Not carried on `AssembledChunk` directly. Accessible by re-reading the constituent `ContentUnit` records via `assembly_metadata.constituent_unit_indices`. Reserved for deferred §6.5 verse-commentary alignment. |
| `text_fidelity` | `TextFidelity` | Logging | Per-page fidelity logged. Not a processing gate. |

**ContentUnit fields consulted when present (optional):**

| Field | Type | Used By | How |
|-------|------|---------|-----|
| `discourse_flow` | `DiscourseFlow` (nullable) | Phase 1 (§4.5) | When present, `section_break` boundaries in discourse segments provide split-point candidates for oversized divisions (second preference after heading markers). Absent for pages with <100 characters. |

### §2.1.4 — Pre-conditions

The excerpting engine does **not** re-validate the normalization output against its schema. The normalization engine is responsible for producing valid output (Layer 1 self-validation per `KNOWLEDGE_INTEGRITY.md`). The excerpting engine trusts that:

1. `manifest.json` conforms to the `NormalizedManifest` schema.
2. Every line in `content.jsonl` conforms to the `ContentUnit` schema.
3. `unit_index` values are contiguous from 0 to `total_content_units - 1`.
4. `text_layers` on every `ContentUnit` cover `[0, len(primary_text))` with no gaps and no overlaps.
5. `DivisionNode.start_unit_index` and `end_unit_index` refer to valid `unit_index` values.
6. `DivisionNode` ranges do not overlap at the same tree level.

If any of these pre-conditions is violated, the excerpting engine will produce incorrect output or crash. This is by design — the normalization boundary guarantees validity, and re-validating 725 lines of schema on every excerpting run would be wasteful. Boundary violations are caught by `tools/check_cross_engine_contracts.py` during integration testing, not at runtime.

**Exception:** The excerpting engine does perform lightweight defensive checks at the point of use:
- Empty `division_tree` → emit `EX-A-010` (no divisions to process), skip source.
- `ContentUnit` not found for a `unit_index` in the declared range → emit `EX-A-011`, skip division.
- `boundary_continuity` is null on a non-terminal unit → treat as `unknown` type, emit warning.

These are defensive checks against data corruption, not schema re-validation.

---

## §3 — Self-Containment Standard

Self-containment is the excerpting engine's primary quality criterion. An excerpt that fails self-containment delivers an incomplete piece of knowledge to the owner — a fragment that looks like a complete teaching but is actually missing its premise, its evidence, or its conclusion. This is T-4 (Context Loss) from `KNOWLEDGE_INTEGRITY.md`: the owner reads something that appears self-sufficient but silently depends on context that was stripped during extraction.

This section defines the standard formally. It is referenced by Phase 2b (§5.3, which evaluates it), Phase 3 (§7, which repairs `PARTIAL` cases), §6 (domain rules that defend it), and §10 (tests that verify it).

### §3.1 — Definition

An excerpt is **self-contained** if a student with general familiarity of the Islamic science (عِلم) covered by the source — but no familiarity with this specific source or its surrounding text — can understand:

1. **What** is being taught (the concept, ruling, argument, or narration).
2. **Whose** position this represents (which scholar, school, or the author themselves).
3. **Why** this position is held (what evidence or reasoning supports it, if the excerpt presents a justified claim).

"General familiarity" means the student knows the basic terminology and structure of the science. For example: a student of fiqh knows what a حكم (ruling) is, what the مذاهب (schools) are, and what constitutes دليل (evidence). The student does NOT know the specific topic being discussed, the arguments made earlier in the book, or the scholarly debates surrounding this particular issue — those must be contained within the excerpt or explicitly flagged as missing.

### §3.2 — Formal Criteria

Five criteria must all hold for an excerpt to be `FULL` self-contained. These are evaluated by the LLM during Phase 2b (§5.3) and re-checked during Phase 3 (§7.3).

**C-SC-1 (Term Resolution):** Every technical term used in the excerpt is either:
  - (a) defined within the excerpt,
  - (b) a standard term of the science that any student of that science would know (e.g., واجب in fiqh, مبتدأ in nahw), or
  - (c) flagged in `self_containment_notes` as requiring external knowledge.

**C-SC-2 (Reference Resolution):** Every pronoun, demonstrative, or anaphoric reference resolves within the excerpt. No dangling هذا, المذكور, ما تقدم, or similar references pointing to text outside the excerpt. If the LLM detects an unresolvable reference, the excerpt cannot be `FULL`.

**C-SC-3 (Evidence Completeness):** Every evidence citation (Quran, hadith, athar, scholarly precedent) either:
  - (a) includes its text within the excerpt, or
  - (b) is a well-known citation identifiable by its opening words alone (e.g., حديث "إنما الأعمال بالنيات" — any student would recognize it), or
  - (c) is flagged in `self_containment_notes`.

**C-SC-4 (Argument Completeness):** The excerpt's argument, ruling, or teaching is complete — not a fragment of a larger argument whose premise or conclusion is elsewhere. An excerpt that states "ورد عليه بأن..." (and it was countered with...) without the original position being countered cannot be `FULL`. An excerpt that presents evidence without stating what it is evidence for cannot be `FULL`.

**C-SC-5 (Dialogue Completeness):** If the excerpt quotes or responds to another scholar's position, enough of that position is included to understand the response. An excerpt that says "وأما قول الشافعي فليس بصحيح لأن..." must include enough of al-Shafi'i's stated position to understand why it is being rejected. The position need not be quoted in full — a sufficient summary within the excerpt satisfies this criterion.

### §3.3 — Self-Containment Levels

Each `TeachingUnit` (§2.3.4) receives one of three self-containment levels:

**FULL** — All five criteria (C-SC-1 through C-SC-5) are met. The excerpt stands alone. No repair, no flagging, no human gate. This is the target state for every excerpt.

**PARTIAL** — Most criteria are met, but the excerpt would benefit from additional context. Specifically: the excerpt teaches something coherent, but a reference, term, or piece of evidence is not fully resolved. This corresponds to the experiment's `self_contained=true` with `self_containment_notes` populated — the excerpt is usable but not perfect.

Phase 3 action: Add `context_hint` — a brief note explaining what context is missing and where to find it (e.g., "References a position stated in the باب preceding this one"). The taxonomy engine receives the excerpt with the hint attached; the synthesis engine can incorporate the hint when building entries.

Phase 3 also attempts to resolve the gap:
- If C-SC-2 fails (dangling reference) and the reference points to a known division, add a `cross_reference` linking to that division.
- If C-SC-3 fails (evidence not included) and the evidence is identifiable (e.g., a known hadith), add the reference in `evidence_refs`.

After Phase 3 repair, the level may be upgraded from `PARTIAL` to `FULL` if all criteria are now satisfied. If repair fails, the level stays `PARTIAL`.

**DEPENDENT** — The excerpt cannot be understood alone. It depends on adjacent content in a way that no context hint can repair. This typically means C-SC-4 fails (argument is a fragment) or C-SC-5 fails (response to an unknown position).

Phase 3 action: Flag for human gate review. Write to `gate_queue.jsonl` with the full context (the excerpt, its adjacent teaching units in the same chunk, and the specific criteria that failed). The owner decides: accept with a note, merge with an adjacent excerpt, or reject.

**Gate design:** Per `KNOWLEDGE_INTEGRITY.md` Layer 4, the owner may respond "yes" (accept), "no" (reject), or "I'm not sure" (triggers elevated Layer 3.5 cross-provider verification with 3+ models). A `DEPENDENT` excerpt never auto-promotes to `FULL` — it either stays `DEPENDENT` with an owner-accepted note, gets merged into an adjacent unit, or is rejected.

### §3.4 — Relationship to Domain Rules

The domain rules in §6 are enforcement mechanisms for self-containment:

- §6.1 (Decontextualization Prevention) defends C-SC-4 and C-SC-5: a position and its refutation must stay together, a question and its answer must stay together.
- §6.2 (Multi-Layer Handling) defends the "whose position" requirement: correct attribution prevents the owner from studying a sharh author's opinion thinking it is the matn author's.
- §6.3 (Evidence Handling) defends C-SC-3: hadith and evidence grouped with their rulings.
- §6.4 (Implicit Reference Resolution) defends C-SC-2: كما تقدم references are flagged or resolved.

Self-containment is not a separate evaluation pass — it is embedded in the Phase 2b grouping decision. When the LLM groups segments into teaching units, it evaluates self-containment simultaneously. The domain rules (§6) are encoded in the Phase 2b prompt as explicit grouping constraints.

### §3.5 — Measurement and Calibration

The old excerpting SPEC used a continuous 0.0–1.0 `self_containment_score`. The new design uses a 3-level enum. The rationale:

- A continuous score creates false precision. The LLM cannot reliably distinguish 0.65 from 0.72 — both mean "probably fine but something might be missing."
- The 3-level system maps directly to actions: no action (`FULL`), automated repair (`PARTIAL`), human gate (`DEPENDENT`). Every level has a defined response.
- The experiment's binary flag plus notes naturally maps to this 3-level system (see §2.3 `SelfContainmentLevel` design extension note).

**Calibration during build:** The boundary between `PARTIAL` and `DEPENDENT` is the critical calibration point. Too strict (many `DEPENDENT`) overwhelms the human gate queue. Too lenient (many `PARTIAL` that should be `DEPENDENT`) lets incomplete arguments through. The 30-book probe (source engine roadmap Step 3) calibrates this boundary empirically. The SPEC defines the criteria; the build determines the prompt calibration that maps criteria to levels.

**Same-model evaluation bias (C-7 mitigation):** Opus 4.6 both extracts teaching units and evaluates self-containment. Structural mitigations:
- Mechanical checks (C-SC-2 can be partially verified by searching for unresolved demonstratives; C-SC-3 can be partially verified by checking evidence segment presence).
- Cross-model spot checks: during the 30-book probe, a different model evaluates 10% of self-containment assessments.
- Owner spot-checks: the owner reviews 5 excerpts per session during the probe, with specific attention to "does this make sense on its own?"

---

## §4 — Phase 1: Deterministic Preprocessing

Phase 1 transforms a `NormalizedPackage` into a list of `AssembledChunk` objects (§2.3.2). It is fully deterministic — no LLM calls, no randomness, no external dependencies beyond the input files. Every behavior is independently unit-testable. This phase absorbs the core of the old passaging engine (cross-page assembly, text joining, validation) but eliminates format-specific passaging strategies — those are handled by the LLM in Phase 2.

### §4.1 — Processing Overview

Phase 1 proceeds in seven sequential steps:

1. **Walk division tree** (§4.2): Identify leaf divisions from `manifest.division_tree`. Skip non-content divisions.
2. **Assemble text** (§4.3): For each leaf division, join `primary_text` across content units using `boundary_continuity` separator mapping.
3. **Merge tiny divisions** (§4.4): Merge adjacent leaf divisions with <50 Arabic words.
4. **Split oversized divisions** (§4.5): Split divisions with >5000 Arabic words at structural boundaries.
5. **Rebase text layers** (§4.6): Translate per-page `text_layers` character offsets to assembled-text coordinates.
6. **Aggregate metadata** (§4.7): OR-aggregate content flags, collect footnotes and physical pages.
7. **Validate** (§4.9): Run self-validation checks (V-P1-1 through V-P1-6).

The heading alignment filter (§4.8) runs during step 2 as a quality flag but does not gate processing.

The engine processes one source at a time. Each leaf division (or merged/split result) produces one `AssembledChunk`. The output is a list of chunks ready for Phase 2.

**No format-specific strategies.** Unlike the old passaging SPEC, Phase 1 does not apply different strategies for prose, verse, Q&A, or masala formats. The `structural_format` field is inherited by each chunk for Phase 2's reference, but Phase 1 treats all text identically: assemble, merge/split, validate. Format-aware processing happens in Phase 2 (the LLM understands format natively) and §6 (domain-specific rules).

### §4.2 — Division Tree Walking

**Input:** `manifest.division_tree` — a list of `DivisionNode` objects forming a tree.

**Leaf identification:** A leaf division is a `DivisionNode` with an empty `children` list. The engine recursively walks the tree and collects all leaves with their heading path (the list of `heading_text` values from root to leaf). Validated implementation: `find_leaf_divisions()` in `experiments/architecture_test/extract_divisions.py`.

**Skip criteria:** A leaf division is skipped (produces no chunk) if ANY of the following hold:
- All content units in its range have `content_flags.is_toc_page == true`.
- All content units in its range have `content_flags.is_index_page == true`.
- All content units in its range have `content_flags.is_blank == true`.
- Its `heading_text` matches any of the bibliography/index exclusion keywords: مصادر, مراجع, فهرس, ثبت المصادر, المراجع (match is substring, case-insensitive after Arabic noise stripping).
- Its content unit range is empty: `start_unit_index > end_unit_index` or no content units exist in the range. Emit `EX-A-002` (empty division), log, and skip.

Skipped divisions are logged with reason codes. They are NOT errors — TOC and index pages are expected.

**Multi-volume sources:** Division nodes with `division_type == "volume"` are structural containers, not content divisions. The engine walks through them to reach leaf divisions. Volume nodes never produce chunks themselves.

**Minimal division trees (C-8):** Sources with <5 leaf divisions after filtering produce very large chunks. This is handled naturally by §4.5 (oversized splitting). Sources with zero leaf divisions after filtering: emit `EX-A-010`, skip entire source.

**Single-root sources:** Sources where `division_tree` contains a single root node with no children: the entire source text is one leaf division. It becomes one chunk (or multiple chunks if oversized per §4.5).

### §4.3 — Cross-Page Text Assembly

For each leaf division, assemble the full text by joining `ContentUnit.primary_text` across pages.

**Content unit selection:** Select all content units with `unit_index` in the range `[division.start_unit_index, division.end_unit_index]` (both inclusive). Content units with `is_toc_page`, `is_index_page`, or `is_blank` true within this range are skipped during assembly — their `unit_index` is still recorded in `assembly_metadata.constituent_unit_indices` for coverage tracking, but their text is not included.

**Separator mapping:** Between consecutive content units N and N+1, the separator is determined by unit N's `boundary_continuity.type`:

| `boundary_continuity.type` | Separator | Rationale |
|---------------------------|-----------|-----------|
| `mid_sentence` | `""` (empty) | Text continues mid-word or mid-sentence across page boundary. |
| `mid_paragraph` | `"\n"` | New sentence within same paragraph. |
| `mid_argument` | `"\n"` | Argument continues but new logical segment. |
| `section_break` | `"\n\n"` | Major topic transition. |
| `division_break` | `"\n\n"` | Division-level break (should not occur within a leaf division's range, but handled defensively). |
| `unknown` | `"\n"` | Conservative default. |
| null (absent) | `"\n"` | Boundary continuity not computed. |

This mapping is validated in the prototype (`BC_JOIN_MAP` in `extract_divisions.py`).

**Boundary continuity is on unit N:** The `boundary_continuity` field on unit N describes the boundary AFTER unit N (between N and N+1). When joining unit N and unit N+1, read `boundary_continuity` from unit N.

**Arabic word joining at mid_sentence:** When `boundary_continuity.type == "mid_sentence"`, the last character of unit N and the first character of unit N+1 may form parts of the same Arabic word. In this case, the empty separator produces correct joining. If the last character of unit N is a word-final form (taa marbuta ة, alif maqsura ى, tanwin diacritics ً/ٌ/ٍ) AND the first character of unit N+1 is a word-initial character, insert a single space instead of empty — the word boundary was at the page break. This refinement applies only when `boundary_continuity.type == "mid_sentence"` and the character analysis suggests word-final + word-initial rather than a word split across pages.

**Diacritics preservation:** All Arabic diacritics (U+064B–U+0652, U+0670) are preserved exactly. No Unicode normalization (NFC/NFD/NFKC/NFKD) is applied at any point. This is an absolute rule — violating it risks T-1 (Silent Text Corruption), since a single diacritic change can reverse meaning (حَرَّمَ "forbade" vs حَرَمَ "deprived").

**Footnote reference markers:** The `⌜N⌝` markers in `primary_text` are preserved inline during assembly. Footnote renumbering (if `ref_marker` values collide across pages) is handled in §4.7.

**Assembly output:** The assembled text, plus an `AssemblyMetadata` record containing `constituent_unit_indices` and `join_points` (one `JoinPoint` per page boundary, recording the units, separator, and character offset).

### §4.4 — Tiny Division Merging

Divisions with very few words produce low-quality LLM inputs — the model lacks sufficient context for meaningful classification. These are merged with adjacent siblings.

**Threshold:** `TINY_DIVISION_WORDS = 50` Arabic words (configurable, §8.3). This captures 29.1% of raw Shamela divisions per the division size analysis.

**Merge algorithm:**
1. After assembling all leaf divisions under the same parent node, identify those with `word_count < TINY_DIVISION_WORDS`.
2. For each tiny division, merge with the **next sibling** under the same parent. If no next sibling exists, merge with the **previous sibling**.
3. If the division is an only child (no siblings), process as-is regardless of size — there is nothing to merge with.
4. Merging combines the assembled texts with a `"\n\n"` separator between them (they are separate divisions, so a section break is appropriate).
5. The merged chunk's `div_id` is the first division's `div_id`. The merged chunk's `merge_history` records all merged `div_id` values.
6. The merged chunk's `div_path` is the first division's path (the heading hierarchy).
7. Repeat merging: if the result of a merge is still below threshold, merge again with the next sibling. This is recursive but bounded by the finite number of siblings.

**Invariant preserved:** I-AC-6 requires `merge_history` to contain ≥2 entries with the first being `div_id`. The merge algorithm guarantees this.

### §4.5 — Oversized Division Splitting

Divisions with too many words produce LLM inputs that exceed token limits or degrade classification quality. These are split at structural boundaries.

**Threshold:** `OVERSIZED_DIVISION_WORDS = 5000` Arabic words (configurable, §8.3). This affects ~0.9% of Shamela divisions per division size analysis.

**Split point selection (priority order):**
1. **Heading markers within the division:** If any content unit in the range has `structural_markers.heading_detected == true`, split at that unit. The heading starts a new chunk. This is the highest-quality split because the heading indicates a natural topic boundary.
2. **Discourse section breaks:** If `discourse_flow` data is available on content units and contains segments with type boundaries corresponding to `section_break`, split at those boundaries. Second preference because discourse flow is a normalization §4.B feature that may not be present.
3. **Paragraph breaks:** Find the `"\n\n"` nearest the midpoint of the assembled text. Split there. This is reliable because paragraph breaks exist in almost all texts.
4. **Sentence boundary:** Find the sentence boundary (terminal punctuation `.` `؟` `!` followed by whitespace) nearest the midpoint. Last resort.

**Splitting produces:** Multiple chunks from one division, each with `split_info` populated (§2.3.2 `SplitInfo`). Chunk IDs: `{div_id}_chunk_0`, `{div_id}_chunk_1`, etc.

**Recursive splitting:** If a split result still exceeds the threshold, split again. Bounded by text length — eventually each chunk will be below threshold.

**Text layer and footnote handling for split chunks:** Each chunk gets the text layers and footnotes corresponding to its text range only. Text layers are sliced at the split point character offset — a layer segment that spans the split point is divided into two segments, one per chunk. Footnotes are assigned to the chunk that contains their `⌜N⌝` marker.

**Content unit assignment for split chunks:** All chunks from the same split share the same `constituent_unit_indices` (the original division's full range) because splitting operates on the assembled text, not on content units. The `assembled_text` of each chunk is a substring of the original assembly. Per I-AC-4, this is the correct behavior.

### §4.6 — Text Layer Rebasing

Normalization provides `text_layers` per content unit with character offsets relative to that unit's `primary_text`. After cross-page assembly, these offsets must be translated to the assembled-text coordinate system.

**Rebasing algorithm:** For each content unit in the assembly order, add the cumulative character offset (including separators) to each layer segment's `start` and `end` values. Validated implementation: `rebase_text_layers()` in `extract_divisions.py`.

**Layer segment merging:** After rebasing, if two adjacent segments (from consecutive content units) have the same `layer_type` and `author_canonical_id`, merge them into a single segment spanning both ranges. This reduces segment count and simplifies downstream processing.

**Validation (I-AC-2):** After rebasing, verify that the union of all segment character ranges exactly covers `[0, len(assembled_text))`. No gaps, no overlaps. If this invariant fails, emit `EX-A-003` (layer coverage failure) — this indicates a bug in rebasing or a malformed normalization output.

**Clamping:** If a layer segment's `end` exceeds its content unit's `primary_text` length, clamp to the text length and emit `EX-A-004` (layer segment overflow, warning). This handles edge cases where normalization produced slightly off offsets.

### §4.7 — Content Flag and Footnote Aggregation

**Content flags:** OR-aggregate across all constituent content units. If any unit in the chunk has `has_verse == true`, the chunk has `has_verse == true`. Same for all boolean flags. Validated implementation: `aggregate_content_flags()` in `extract_divisions.py`.

**Footnotes:** Collect all `Footnote` objects from constituent content units in order. Deduplicate by `ref_marker` — if two units have a footnote with the same `ref_marker`, keep the first occurrence and emit `EX-A-005` (duplicate footnote marker, warning).

**Footnote renumbering:** When assembling text across pages, footnote reference markers may collide (two pages both have `⌜1⌝`). If collisions exist, renumber footnotes sequentially by order of first appearance in the assembled text. Update both the `⌜N⌝` markers in `assembled_text` and the `ref_marker` fields in the `footnotes` list. Record the old→new mapping in `assembly_metadata` for traceability.

**Physical pages:** Collect `PhysicalPage` records from all constituent content units in `unit_index` order. No deduplication — each page contributes one record.

### §4.8 — Heading Alignment Filter

From the experiment: heading-content misalignment (where a division's heading does not match its actual content) produces garbage LLM results. The heading alignment filter detects this.

**Algorithm:** Strip Arabic noise (ZWNJ, ZWJ, diacritics, tatweel) from both the division's `heading_text` and the first 200 characters of `assembled_text`. Check if the first 30 stripped characters of the heading appear within the first 200 stripped characters of the assembled text. Validated implementation: `strip_arabic_noise()` in `extract_divisions.py`.

**Result:** Sets `heading_alignment_ok` on the `AssembledChunk`:
- `true`: heading aligns with content.
- `false`: heading does not align. Emit `EX-A-006` (heading misalignment, warning). The chunk is still processed — this is a quality flag, not a gate. Phase 2 may produce lower-quality results for misaligned chunks, but skipping them would mean data loss.

**Threshold note:** The experiment found 40–60% rejection rates with strict alignment (15 chars in first 100 chars). The relaxed check (30 chars in first 200 chars) is used here to avoid excessive flagging. The threshold may be calibrated during build evaluation.

### §4.9 — Phase 1 Self-Validation

After all chunks are produced, run these validation checks before passing to Phase 2. Validation failures are categorized as fatal (processing stops) or warning (processing continues with flags).

**V-P1-1 (Division coverage):** Every leaf division in the division tree maps to ≥1 `AssembledChunk`, or is explicitly listed as skipped with a reason code. Fatal if a division is neither processed nor skipped — indicates a bug in tree walking.

**V-P1-2 (Content unit coverage):** The union of all chunks' `constituent_unit_indices` covers all non-skipped content units. Specifically: for every `unit_index` from 0 to `total_content_units - 1`, the unit is either (a) in at least one chunk's `constituent_unit_indices`, or (b) belongs to a skipped division, or (c) its content flags indicate it should be skipped (`is_toc_page`, `is_index_page`, `is_blank`). Fatal if any content unit is silently lost — this is data loss.

**V-P1-3 (No empty chunks):** Every `AssembledChunk` has `word_count > 0`. Warning if violated (indicates a merge/split edge case).

**V-P1-4 (No oversized chunks):** Every `AssembledChunk` has `word_count <= OVERSIZED_DIVISION_WORDS`. Warning if violated (indicates a splitting failure).

**V-P1-5 (Layer coverage):** For every `AssembledChunk`, the text layer invariant I-AC-2 holds: every character in `assembled_text` is covered by exactly one `text_layers` segment. Fatal if violated — downstream phases depend on layer attribution.

**V-P1-6 (Word count consistency):** For every `AssembledChunk`, `word_count` equals the Arabic word counter applied to `assembled_text`, and `total_tokens` equals `len(assembled_text.split())`. Fatal if violated — indicates a computation bug.

**Validation output:** A list of validation results (pass/fail/warning per check) written to the source's processing log. If any fatal check fails, Phase 1 output is not passed to Phase 2. The source is flagged with `EX-V-001` for investigation.

---

## §5 — Phase 2: LLM Teaching Unit Extraction

Phase 2 transforms each `AssembledChunk` (§2.3.2) into a list of `TeachingUnit` objects (§2.3.4) via two sequential LLM calls. This is the engine's inference core — the only phase that calls an LLM. Every other phase is fully deterministic.

The approach is **Approach B (classify-then-group)**, validated across 23 divisions in 7 formats (experiments `run_tests.py` and `format_diversity_test`). Approach A (single-call extraction) was also validated but rejected because Approach B provides more architectural control points: classification results can be validated independently before grouping, and the two-step design enables targeted retries (retry classification without re-doing grouping, or vice versa).

**D-011 enforcement (structural):** Phase 2 processes one `AssembledChunk` at a time. The LLM receives only that chunk's `assembled_text` — it has no access to text from other chunks. Cross-chunk teaching units are therefore impossible by construction, not by validation. This is the primary defense against T-4 (Context Loss) at the structural level.

### §5.1 — Processing Overview

For each `AssembledChunk` produced by Phase 1, Phase 2 executes:

1. **Phase 2a — Segment Classification (§5.2):** The LLM classifies the chunk's text into `ClassifiedSegment` objects, each spanning a contiguous run of words serving a single scholarly function.

2. **Offset Normalization (§5.4.1):** The raw LLM-produced word offsets are remapped to the canonical tokenization (`assembled_text.split()`), using `text_snippet` fields as alignment anchors.

3. **Coverage Verification — Segments (§5.4.2):** Verify that the normalized segments satisfy invariants I-CS-1 through I-CS-6.

4. **Phase 2b — Teaching Unit Grouping (§5.3):** The LLM groups the classified segments into `TeachingUnit` objects — self-contained pedagogical units that each teach one distinct concept, ruling, or argument.

5. **Coverage Verification — Units (§5.4.3):** Verify that the teaching units satisfy invariants I-TU-1 through I-TU-9.

Steps 1–3 must succeed before step 4 begins. If classification fails after retries, the chunk is flagged with `EX-C-001` and excluded from further processing. If grouping fails after retries, the chunk is flagged with `EX-C-002`.

**Per-source ordering:** Chunks from the same source are processed sequentially (by `div_id` order). Chunks from different sources may be processed in parallel.

### §5.2 — Phase 2a: Segment Classification

Phase 2a sends the chunk's assembled text to the LLM and receives back a list of classified segments covering the full text.

#### §5.2.1 — Input

The LLM receives:
- The full `assembled_text` of the `AssembledChunk`
- The chunk's `structural_format` (for contextual awareness — the LLM adapts its segmentation granularity to the format)

#### §5.2.2 — LLM System Prompt

The classification prompt is adapted from the experiment's `APPROACH_B_CLASSIFY_SYSTEM`, with production additions marked. The full prompt text:

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

Classify each sentence or closely bonded group of sentences in this Arabic text
by scholarly function. The scholarly function types are:

  definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
  evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
  condition_exception, cross_reference, narration, editorial_note,
  structural_transition, unclassified

Segment boundary rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- A condition + its result ("إذا ... فـ") = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Consecutive sentences serving the same function may form one segment
  if they are tightly bonded (e.g., a two-sentence definition)

For each segment, provide:
- segment_index: 0-based position in the sequence
- start_word: approximate start word offset in the text
- end_word: approximate end word offset in the text (inclusive)
- text_snippet: the FIRST 50 CHARACTERS of this segment's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace precisely.
  This field is used for alignment; exact copying is critical.
- scholarly_function: one of the 16 types listed above
- confidence: your classification confidence from 0.0 to 1.0

The text format is: {structural_format}
```

**Adaptation notes (differences from experiment prompt):**
- Added: `confidence` field instruction (experiment schema had it but prompt didn't explicitly request it)
- Added: condition + result bonded rule (from atomization SPEC §4.A.2 AB-2; experiment relied on implicit LLM understanding)
- Added: consecutive-sentences-same-function rule (clarifies that segments can span multiple sentences)
- Added: structural_format context (the experiment tested per-division; production includes format as context)
- Preserved: all original experiment boundary rules exactly
- Removed: nothing from experiment prompt

#### §5.2.3 — User Message

The user message contains only the assembled text, wrapped for clarity:

```
<text>
{assembled_text}
</text>
```

No additional context is provided. The system prompt carries all instructions. The text is the sole input.

#### §5.2.4 — Response Schema

The LLM returns structured output enforced via a Pydantic model (using the Instructor library or equivalent structured output enforcement). The schema:

**ClassificationResult:**

| Field | Type | Description |
|-------|------|-------------|
| `segments` | `list[ClassifiedSegment]` | The classified segments, ordered by position. |
| `total_segments` | `int` | Count of segments (must equal `len(segments)`). |

**ClassifiedSegment** fields match §2.3.3. The LLM produces raw offsets in its own tokenization; these become canonical after offset normalization (§5.4.1).

On schema validation failure (missing fields, wrong types, values outside enum), the structured output library retries automatically with the validation error message appended. Up to 2 retries per chunk (§5.5).

#### §5.2.5 — Model and Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `anthropic/claude-opus-4.6` via OpenRouter | Highest classification accuracy. Validated in experiment. |
| Temperature | `0` | Deterministic classification. |
| MAX_TOKENS | Dynamic — see §5.5.1 | Classification output scales with input length. |

### §5.3 — Phase 2b: Teaching Unit Grouping

Phase 2b receives the classified segments (post-normalization) and the original text, then groups segments into self-contained teaching units.

#### §5.3.1 — Input

The LLM receives:
- The full `assembled_text` of the `AssembledChunk`
- The classification result: a summary of each segment (index, word range, function, snippet)
- The chunk's `structural_format`

The classification summary is formatted as a structured list in the user message (§5.3.3), not embedded in the system prompt. This keeps the system prompt stable across chunks.

#### §5.3.2 — LLM System Prompt

The grouping prompt is adapted from the experiment's `APPROACH_B_GROUP_SYSTEM`, with production additions for self-containment evaluation, segment index tracking, and decontextualization prevention. The full prompt text:

```
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained
scholarly segments that each teach one distinct concept, ruling, or argument.
A teaching unit is the smallest segment a student could study and learn
something complete from.

GROUPING RULES:
- A position (opinion_statement) + its evidence + any counter-evidence
  + conclusion = one unit
- A definition + its examples = one unit
- A hadith + its chain + commentary = one unit
- A question and its answer belong in the same unit
- A rule_statement + its condition_exception(s) = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- structural_transition segments may be grouped with the content they introduce,
  or stand alone if they serve as section markers

DECONTEXTUALIZATION PREVENTION (critical):
- A reported position ("قال أبو حنيفة...") and its refutation
  ("ورد عليه بأن...") MUST be in the same unit
- A counter-argument MUST include enough of the original argument to be
  understood on its own
- Evidence cited for a ruling MUST stay with the ruling
- A condition and its exception (rule + إلا clause) belong together

SELF-CONTAINMENT EVALUATION:
For each teaching unit, evaluate self-containment against these criteria:

C-SC-1 (Term Resolution): Every technical term is either defined within the
  unit, is standard terminology any student of the science would know, or is
  flagged as requiring external knowledge.

C-SC-2 (Reference Resolution): Every pronoun, demonstrative, or anaphoric
  reference (هذا، المذكور، ما تقدم) resolves within the unit. No dangling
  references to text outside the unit.

C-SC-3 (Evidence Completeness): Every evidence citation either includes its
  text, is a universally known citation identifiable by its opening words
  (e.g., حديث "إنما الأعمال بالنيات"), or is flagged.

C-SC-4 (Argument Completeness): The unit's argument, ruling, or teaching is
  complete — not a fragment whose premise or conclusion is elsewhere.

C-SC-5 (Dialogue Completeness): If the unit responds to another scholar's
  position, enough of that position is included to understand the response.

Assign self_containment as:
- FULL: All five criteria met. The unit stands alone.
- PARTIAL: Most criteria met, but some context would help. Populate
  self_containment_notes describing what's missing.
- DEPENDENT: Cannot be understood alone. Populate self_containment_notes
  explaining the dependency.

For each teaching unit, provide:
- unit_index: 0-based position in the sequence
- segment_indices: list of segment_index values composing this unit
  (must be a contiguous ascending sequence, e.g. [3, 4, 5])
- start_word: the start_word of the first constituent segment
- end_word: the end_word of the last constituent segment
- text_snippet: the FIRST 80 CHARACTERS of this unit's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace.
- primary_function: the dominant scholarly function (must be a function present
  in the constituent segments)
- secondary_functions: other functions present in the unit (may be empty)
- description_arabic: a brief Arabic description of what this unit teaches,
  5 to 35 Arabic words. Write it as a student-facing summary.
- self_containment: FULL, PARTIAL, or DEPENDENT
- self_containment_notes: present and non-empty for PARTIAL/DEPENDENT;
  absent or null for FULL

The text format is: {structural_format}
```

**Adaptation notes (differences from experiment prompt):**
- Added: `segment_indices` field instruction (new field — experiment had only word ranges)
- Added: full self-containment criteria C-SC-1–5 (experiment had one-sentence instruction; production embeds the formal criteria)
- Added: `self_containment` 3-level enum (experiment used binary `self_contained`)
- Added: `description_arabic` target range 5–35 words (experiment said "10-30"; relaxed per §2.3 Finding 2)
- Added: decontextualization prevention rules (from §6.1, embedded here because the LLM needs them during grouping)
- Added: structural_transition grouping guidance
- Added: structural_format context
- Changed: self_containment_notes requirement aligned with I-TU-6/I-TU-7 (must be absent for FULL)
- Preserved: all original experiment grouping rules

#### §5.3.3 — User Message

The user message contains the text and the classification summary:

```
<text>
{assembled_text}
</text>

<classified_segments>
{for each segment:}
Segment {segment_index}: words {start_word}–{end_word}, function={scholarly_function}, snippet="{text_snippet}"
{end for}
</classified_segments>
```

The segment summary uses the **post-normalization** word offsets (canonical tokenization). The LLM sees the segments anchored to the actual text via both word ranges and snippets.

#### §5.3.4 — Response Schema

**ExtractionResult:**

| Field | Type | Description |
|-------|------|-------------|
| `teaching_units` | `list[TeachingUnit]` | The grouped teaching units, ordered by position. |
| `total_units` | `int` | Count of units (must equal `len(teaching_units)`). |
| `notes` | `str` (optional) | LLM notes on grouping decisions, if any. |

**TeachingUnit** fields match §2.3.4. The `start_word` and `end_word` are derived from the constituent segments' normalized offsets — the LLM references the segments by index and the engine computes the word ranges from the segment data.

On schema validation failure, same retry policy as §5.2.4.

#### §5.3.5 — Model and Parameters

| Parameter | Value | Rationale |
|-----------|-------|-----------|
| Model | `anthropic/claude-opus-4.6` via OpenRouter | Consistent with classification. Grouping requires understanding scholarly argument structure. |
| Temperature | `0` | Deterministic grouping. |
| MAX_TOKENS | `16384` | Grouping output is smaller than classification (fewer objects, each with more fields). 16384 is sufficient for the largest validated case (41 units at 3111 words). |

### §5.4 — Coverage Verification and Offset Normalization

This section specifies how the raw LLM output is validated and transformed into the canonical representation that downstream phases depend on. It has three parts: offset normalization (§5.4.1), segment verification (§5.4.2), and unit verification (§5.4.3).

#### §5.4.1 — Offset Normalization

**The problem:** The experiment revealed that the LLM produces word offsets using its own internal tokenization, which does not match Python's `text.split()`. The offsets are internally consistent — across 162 segment boundaries in the Taysir div_661 test (3111 words), there were 0 gaps between consecutive segment boundaries. But the LLM's final offset (4172) exceeded the Python token count (3643) by 14.5%. The LLM's offsets are self-consistent but not directly usable for text extraction.

**The solution:** Use `text_snippet` fields as alignment anchors to remap LLM offsets to the canonical tokenization.

**Canonical tokenization:** `assembled_text.split()` — Python whitespace split. This produces a list of tokens indexed 0 through `total_tokens - 1`. All word offsets in `ClassifiedSegment` and `TeachingUnit` (§2.3.3, §2.3.4) use this coordinate system after normalization.

**Algorithm:**

The normalization processes the segments in order (by `segment_index`) and maps each segment's start position to a canonical token index using its `text_snippet` as an anchor.

**Step 1 — Build token-to-character mapping.** Split `assembled_text` by whitespace. For each token, record its character start and end offset in the original string. This creates a lookup from character position to token index.

**Step 2 — Anchor each segment.** For each segment `s` in order (0, 1, 2, ...):

(a) Take `s.text_snippet` (the first 50 characters of the segment's text, as copied by the LLM from the input).

(b) Search for `s.text_snippet` in `assembled_text` starting from `search_start_char` (initially 0, updated after each successful match). The search must find the snippet at or after the previous segment's matched position. This left-to-right constraint prevents misalignment from duplicate snippets.

(c) If the snippet is found at character position `match_char`:
   - Find the token whose character range contains `match_char`. That token's index is the segment's canonical `start_word`.
   - Update `search_start_char` to `match_char + 1` for the next segment.

(d) If the snippet is not found with exact matching, attempt **whitespace-normalized matching**: collapse runs of whitespace in both the snippet and the search region to single spaces, then retry. Arabic text may have inconsistent whitespace around diacritics or punctuation.

(e) If the snippet is still not found, the normalization has failed for this segment. See failure handling below.

**Step 3 — Infer boundaries from contiguity.** After all segments are anchored:
- `segment[0].start_word` is set from its anchor (must be 0 — validated in §5.4.2).
- For each pair of consecutive segments `s[i]` and `s[i+1]`: `s[i].end_word = s[i+1].start_word - 1`.
- `segment[-1].end_word = total_tokens - 1`.

This leverages the LLM's internal contiguity (verified empirically) to infer exact boundaries from anchor positions. The anchor locates the start; contiguity determines the end.

**Step 4 — Validate invariants.** Run the checks in §5.4.2. If any invariant is violated, the normalization result is rejected.

**Failure handling:**
- If any segment's snippet cannot be located (step 2e), the entire classification result is rejected. The chunk is retried with the classification prompt (up to 2 retries total per §5.5). The retry includes an error feedback message: "The previous classification produced a text_snippet that could not be located in the source text. Ensure each text_snippet is copied exactly from the input."
- If step 3 produces a negative word range (a segment's end_word < start_word), the result is rejected and retried.
- If all retries are exhausted, the chunk is flagged with `EX-C-003` (offset normalization failure) and excluded from Phase 2b.

**Design rationale:** This algorithm assumes the LLM's segment ordering matches the text's reading order (left-to-right, top-to-bottom). The experiment confirmed this: across all 23 validated divisions, the LLM always produced segments in text order with monotonically increasing offsets. The left-to-right search constraint (step 2b) is both a correctness guarantee and a disambiguation mechanism for duplicate snippets.

#### §5.4.2 — Segment Coverage Verification

After offset normalization, verify the invariants from §2.3.3:

**V-P2-1 (Segment ordering):** `segment_index` values form the sequence 0, 1, 2, ..., N-1 (I-CS-1). Fatal if violated.

**V-P2-2 (Segment contiguity):** For every consecutive pair `s[i]`, `s[i+1]`: `s[i+1].start_word == s[i].end_word + 1` (I-CS-2). Fatal if violated. (Note: this is guaranteed by the step 3 boundary inference, but verified explicitly as a consistency check.)

**V-P2-3 (First segment starts at 0):** `segments[0].start_word == 0` (I-CS-3). If the first segment's anchor resolves to a token other than 0, the text before the anchor is unclassified — this is a classification gap. Fatal.

**V-P2-4 (Last segment covers end):** `segments[-1].end_word == total_tokens - 1` (I-CS-4). Guaranteed by step 3 but verified explicitly. Fatal if violated.

**V-P2-5 (Full coverage):** The union of all segment word ranges covers `[0, total_tokens - 1]` (I-CS-5). This is a logical consequence of V-P2-2 + V-P2-3 + V-P2-4 but verified explicitly as the master check. Fatal if violated.

**V-P2-6 (Confidence range):** Every segment's `confidence` is in `[0.0, 1.0]` (I-CS-6). Enforced by schema validation. Warning if violated (clamp to range).

**V-P2-7 (Non-empty segments):** Every segment's `end_word >= start_word` (at least one token). Fatal if violated.

**V-P2-8 (Scholarly function validity):** Every segment's `scholarly_function` is a valid `ScholarlyFunction` enum value. Enforced by schema validation. Fatal if violated.

**V-P2-9 (Total segments consistency):** `total_segments == len(segments)`. Warning if mismatched (use actual list length).

On any fatal violation: reject the classification result, retry per §5.5.

#### §5.4.3 — Teaching Unit Coverage Verification

After Phase 2b produces teaching units, verify the invariants from §2.3.4:

**V-P2-10 (Unit ordering):** `unit_index` values form the sequence 0, 1, 2, ..., M-1 (I-TU-1). Fatal if violated.

**V-P2-11 (Segment indices contiguous):** Each unit's `segment_indices` is a contiguous ascending sequence (I-TU-2). No gaps (e.g., `[3, 5]` is invalid) and no reversals. Fatal if violated.

**V-P2-12 (Complete segment assignment):** The union of all `segment_indices` across all units equals `{0, 1, ..., total_segments - 1}` (I-TU-3). Every segment is assigned to exactly one unit. Fatal if violated.

**V-P2-13 (Unit contiguity):** For consecutive units `u[i]`, `u[i+1]`: `u[i+1].start_word == u[i].end_word + 1` (I-TU-4). Fatal if violated.

**V-P2-14 (Word range consistency):** Each unit's `start_word` equals the `start_word` of its first constituent segment, and its `end_word` equals the `end_word` of its last constituent segment (I-TU-5). Fatal if violated. The implementation should derive these from the segment data rather than trusting the LLM's values.

**V-P2-15 (Self-containment notes consistency):** If `self_containment` is `FULL`, then `self_containment_notes` must be null/absent (I-TU-6). If `self_containment` is `PARTIAL` or `DEPENDENT`, then `self_containment_notes` must be present and non-empty (I-TU-7). Warning if violated (auto-repair: set notes to null for FULL; set to "No notes provided" for PARTIAL/DEPENDENT — but flag for review).

**V-P2-16 (Description range):** `description_arabic` contains 5–35 Arabic words (I-TU-8). Warning if outside range (do not reject — the field is informational).

**V-P2-17 (Primary function grounding):** The unit's `primary_function` is one of the `scholarly_function` values present in its constituent segments (I-TU-9). Warning if violated (the LLM may have synthesized a higher-level function; log but do not reject).

**V-P2-18 (Total units consistency):** `total_units == len(teaching_units)`. Warning if mismatched (use actual list length).

**V-P2-19 (Non-empty units):** Every unit has at least one segment in `segment_indices`. Fatal if violated.

On any fatal violation: reject the grouping result, retry Phase 2b per §5.5. Classification results are reused — only the grouping call is retried.

### §5.5 — Operational Constraints

#### §5.5.1 — MAX_TOKENS Scaling

The classification call's output size scales with input length (more text → more segments). The experiment validated:

| Input words | Classify segments | Teaching units (group) | MAX_TOKENS needed |
|-------------|-------------------|----------------------|-------------------|
| 451–1270 | Not measured (< classify for 2500w range) | 8–21 | < 8192 (classify fits in default) |
| 2513–3111 | 125–166 | 19–41 | ≥ 32768 (classify output requires it) |

The classify call produces significantly more objects than the group call (125–166 segments vs. 19–41 units for the 2500–3100w range). The MAX_TOKENS constraint is driven by the classify call, not the group call.

**Scaling rule:**
- Chunks with `word_count <= 2000`: MAX_TOKENS = `8192`
- Chunks with `word_count > 2000`: MAX_TOKENS = `32768`
- Chunks with `word_count > 4000`: MAX_TOKENS = `32768` (provisionally — must be tested during build; if classify output truncates at this size, escalate to `65536`)

The grouping call uses a fixed MAX_TOKENS of `16384`. The largest validated grouping output was 41 units (Taysir div_661 at 3111 words), well within this limit.

**Design extension note:** The `word_count > 4000` threshold is untested — no experiment division exceeded 3111 words. Phase 1 splits divisions at 5000 Arabic words (§4.5), so chunks of 4000–5000 words are possible. Build evaluation must test MAX_TOKENS sufficiency for these cases.

#### §5.5.2 — Retry Policy

Each LLM call (classify and group, independently) is retried up to **2 times** on failure, for a maximum of 3 attempts per call per chunk.

**Retry triggers:**
- Schema validation failure (structured output library handles automatically)
- Offset normalization failure (§5.4.1 step 2e — snippet not found)
- Coverage verification failure (§5.4.2 or §5.4.3 fatal checks)
- API error (timeout, rate limit, server error)

**Retry behavior:**
- Schema failure: the structured output library appends the validation error to the next attempt's prompt automatically.
- Offset normalization failure: append the error feedback message specified in §5.4.1.
- Coverage failure: append a message describing which invariant was violated (e.g., "Previous output had a gap between segments 4 and 5 — ensure all text is covered").
- API error: exponential backoff — wait 2^attempt seconds (2s, 4s) before retrying.

**After all retries exhausted:**
- Classification failure: flag chunk with `EX-C-001` (classification failed). No Phase 2b attempted.
- Offset normalization failure: flag chunk with `EX-C-003` (normalization failed). No Phase 2b attempted.
- Segment coverage failure: flag chunk with `EX-C-004` (segment coverage invariant violated after retries).
- Grouping failure: flag chunk with `EX-C-002` (grouping failed). Classification result is preserved (it may be useful for diagnostics).
- Unit coverage failure: flag chunk with `EX-C-005` (unit coverage invariant violated after retries).

Flagged chunks are logged with full diagnostic information (the raw LLM responses, the specific invariant that failed, the chunk's assembled_text length) and excluded from Phase 3.

#### §5.5.3 — API Configuration

| Parameter | Value |
|-----------|-------|
| Provider | OpenRouter |
| API key | From environment variable (`OPENROUTER_API_KEY`) |
| Model string | `anthropic/claude-opus-4.6` |
| Temperature | `0` (both calls) |
| Timeout | `120` seconds per call |
| Rate limiting | Respect OpenRouter rate limits; back off on 429 responses |

#### §5.5.4 — Telemetry

Each LLM call logs (for monitoring, not for behavioral decisions):
- `source_id`, `chunk_id`
- Call type (`classify` or `group`)
- Input token count, output token count
- Latency (seconds)
- Retry count (0 if first attempt succeeded)
- Success/failure status

This data enables cost tracking and performance monitoring but does not affect processing logic. No behavioral decisions are made based on telemetry.

#### §5.5.5 — Over-Segmentation Awareness

The experiment revealed that Approach B's two-step design can over-segment compared to Approach A, particularly for longer texts with structural repetition. The most extreme case: Taysir div_661 (3111 words) produced 41 B-units vs. 24 A-units (ratio 1.71x), driven by a repeated hadith-benefits pattern.

The average teaching unit size across all 13 validated divisions ranged from 45 words (Q&A format, 451w input) to 126 words (fiqh prose, 2513w input). The median was approximately 80–90 words per unit.

**The SPEC does not commit a minimum teaching unit size.** The appropriate threshold depends on the downstream taxonomy and synthesis engines' needs, which are not yet specified. The concern is documented here; the threshold is calibrated during build evaluation (the 30-book probe, source engine roadmap Step 3). During build, the implementation should log unit size distribution statistics per chunk to enable calibration.

**What the SPEC does commit:** If a future minimum threshold is established, it will be enforced as a **post-grouping merge** step (merging adjacent small units) rather than as a constraint in the LLM prompt. Modifying the grouping prompt to enforce minimum sizes risks degrading self-containment assessment quality — the LLM should group by scholarly structure, and size optimization is a separate concern.

---

