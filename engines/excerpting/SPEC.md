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

