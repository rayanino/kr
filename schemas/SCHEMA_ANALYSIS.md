# KR Inter-Engine Schema Analysis

**Date:** 2026-03-03
**Source codebase analyzed:** ABD (`abd_post_stage0_v1.5`)
**Target:** KR `schemas/` directory — inter-engine data contracts per VISION.md §13.4

**⚠ ABD Legacy (D-019):** These schemas were designed for ABD's Shamela-only pipeline. They use `book_id` (KR may use `source_id`), have Shamela-specific enums, and lack fields for multi-format source types. Each schema will be redesigned when the corresponding engine SPEC is written. Until then, they describe what currently exists, not what KR needs.

**⚠ Metadata Pass-Through (D-023):** Metadata is synthesis fuel. Every schema in the chain must carry ALL metadata from upstream engines plus anything the current engine adds. The synthesizing engine is the ultimate consumer — it uses author biography, dates, school affiliations, teacher-student chains, work genres, and historical context to produce scholarly narratives (not flat compilations). When redesigning any schema, the question is not "what does this engine need?" but "what must flow through this engine to the synthesizer?" No metadata may be stripped because an intermediate engine doesn't use it.

---

## 1. Complete Data Flow

```
Source Engine (محرك المصادر)
    │
    │  ── schemas/source_metadata.json ──
    ▼
Normalization Engine (محرك التطبيع)
    │
    │  ══ schemas/normalized_package.json ══  ← NORMALIZATION BOUNDARY (حد التطبيع)
    ▼
Passaging Engine (محرك التقطيع)
    │
    │  ── schemas/passage.json ──
    ▼
Atomization Engine (محرك التذرير)
    │
    │  ── schemas/atoms.json ──
    ▼
Excerpting Engine (محرك الاقتطاف)
    │
    │  ── schemas/excerpt.json ──  (draft excerpts)
    ▼
Taxonomy Engine (محرك التصنيف)  ←→  Human Gate (§9)
    │
    │  ── schemas/placed_excerpt.json ──  (placed in library)
    ▼
Library Storage
    │
    ▼
Synthesizing Engine (محرك التوليف)
    │
    │  ── schemas/entry.json ──  (terminal product)
    ▼
Library (owner reads and studies)
```

Double-line (`══`) marks the normalization boundary. Everything above is source-format-specific; everything below is source-agnostic.

---

## 2. Per-Schema Analysis

### 2.1 `source_metadata.json`

**Boundary:** Source engine → Normalization engine (Phase 1 internal)

**ABD files analyzed:**
- `schemas/intake_metadata_schema.json` (v0.2)
- `books/imla/intake_metadata.json` (sample data)

**Fields kept from ABD (source-agnostic):**
- `book_id`, `title`, `title_formal`, `author`, `muhaqiq`, `publisher`, `publication_year`
- `volume_count`, `total_actual_pages`, `source_files` (with sha256 hashes)
- `book_category`, `science_parts`, `scholarly_context` (full sub-object)
- `language`, `intake_utc`, `taxonomy_at_intake`
- `edition_notes`, `unrecognized_metadata_lines`

**Fields excluded (Shamela-specific):**
- `shamela_book_id` — Shamela Library numeric ID
- `shamela_author_short` — Short author name from Shamela title span
- `shamela_page_count` — Shamela-reported page count (69% mismatch rate observed)
- `shamela_edition` — Edition info from Shamela الطبعة field
- `shamela_volume_count` — Shamela-declared volume count
- `shamela_pub_date` — Shamela platform publication date
- `html_qism_field` — Raw القسم field from Shamela metadata card

These fields are documented as `x-shamela-extension` in the schema's `additionalProperties` note. The Shamela normalizer's SPEC.md should produce these as additional properties in the source metadata record.

**Fields added for KR:**
- `source_type` (enum) — Identifies which normalizer processes the source. Values: `shamela`, `pdf`, `manual_input`, `ketab_online`, `web_article`, `audio_transcript`, `other`. Per §7.5 and §2.5.
- `science_scope` (array, minItems: 1) — Replaces the more limited `primary_science` field. Array of science identifiers per §7.3. At least one entry required.
- `frozen_source_hash` (SHA-256) — Integrity verification hash per §7.2.
- `schema_version` pattern updated to `source_metadata_v*` (was `intake_metadata_v*`).

**Key design decisions:**
- `additionalProperties: true` allows normalizer-specific extensions without schema violations.
- `primary_science` from ABD was an enum of 4 sciences; KR's `science_scope` is an open array to support the full inventory of primary and supporting sciences per §1.2.
- The `source_files` sub-schema is preserved verbatim from ABD — it is already source-agnostic.

---

### 2.2 `normalized_package.json`

**Boundary:** Normalization engine → Passaging engine (THE NORMALIZATION BOUNDARY)

**ABD files analyzed:**
- `books/imla/stage1_output/pages.jsonl` (3 sample records)
- `tools/normalize_shamela.py` (output dict structure)
- `tools/discover_structure.py` (structure discovery output)
- `schemas/divisions_schema_v0.1.json` (full schema)

**COMPOSITE structure:**
The schema defines two sub-schemas via `$defs`:
1. **Manifest** (`manifest`): metadata + divisions + structure_confidence as a single JSON doc
2. **Page Record** (`page_record`): one record per line in JSONL, for streaming large books

**Page record fields kept from ABD (source-agnostic):**
- `seq_index`, `book_id`, `matn_text`, `footnotes`, `footnote_ref_numbers`
- `footnote_preamble`, `page_number_int`, `page_number_arabic` (display-only)
- `volume`, `has_verse`, `has_table`, `warnings`, `content_type`
- `schema_version`, `record_type`

**Page record fields excluded (Shamela-specific):**
- `raw_matn_html` — Raw HTML of main text (Shamela format artifact)
- `raw_fn_html` — Raw HTML of footnotes (Shamela format artifact)
- `footnote_section_format` — Shamela-specific footnote formatting info
- `starts_with_zwnj_heading` — ZWNJ heading detection (Shamela HTML convention)

**Division node fields kept from ABD:**
All fields from `divisions_schema_v0.1.json` are source-agnostic and kept:
- `id`, `type`, `title`, `level`, `detection_method`, `confidence`, `digestible`
- `content_type`, `start_seq_index`, `end_seq_index`, `page_hint_start`, `page_hint_end`
- `parent_id`, `child_ids`, `page_count`, `ordinal`, `editor_inserted`
- `review_flags`, `detection_notes`

**Division node fields excluded:**
- `heading_in_html` — Whether heading has `<span class='title'>` tag (Shamela HTML specific)
- `inline_heading` — Shamela HTML inline heading detection
- `heading_text_boundary` — Character offset for inline heading (tied to Shamela format)
- `human_override` — Kept in divisions_schema but omitted from normalized package node (overrides are applied before output)

**Manifest fields added for KR:**
- `metadata` sub-object carrying source identity and science_scope through the pipeline
- `normalization_tool` — Which normalizer produced this package
- `normalization_utc` — When normalization was performed

**Schema-level annotations:**
- `x-normalization-boundary: true` — Signals architectural significance per task instructions

---

### 2.3 `passage.json`

**Boundary:** Passaging engine → Atomization engine

**ABD files analyzed:**
- `schemas/passages_schema_v0.1.json` (full schema)
- `books/imla/stage2_output/passages.jsonl` (3 sample records)
- `tools/extract_passages.py` (`get_passage_text()` function)

**Fields kept from ABD (all source-agnostic):**
- `passage_id`, `book_id`, `division_ids`, `title`, `heading_path`
- `start_seq_index`, `end_seq_index`, `page_hint_start`, `page_hint_end`
- `page_count`, `volume`, `digestible`, `content_type`
- `sizing_action`, `sizing_notes`, `split_info`, `merge_info`
- `review_flags`, `science_id`
- `predecessor_passage_id`, `successor_passage_id`

**Fields added for KR:**
- `passage_text` — Complete concatenated text content. In ABD, `extract_passages.py` reconstructs this at runtime via `get_passage_text()` from page records. In KR, the passaging engine includes it directly so downstream engines don't need page-level access.
- `passage_footnotes` — Array of footnotes with source page attribution. Same rationale: downstream engines shouldn't need to access the normalized package's pages.

**Key design decisions:**
- `content_type` enum expanded to include `"introduction"` (seen in ABD sample data but not in ABD schema enum).
- The passage carries `science_id` from the source's science scope, enabling downstream routing.

---

### 2.4 `atoms.json`

**Boundary:** Atomization engine → Excerpting engine

**ABD files analyzed:**
- `schemas/gold_standard_schema_v0.3.3.json` → `definitions/atom_record`

**Fields kept from ABD:**
- `atom_id` (same pattern: `{book_id}:{layer}:{six_digit_sequence}`)
- `atom_type` (same enum: heading, prose_sentence, bonded_cluster, verse_evidence, quran_quote_standalone, list_item)
- `source_layer` (same enum: matn, footnote, sharh, hashiya, tahqiq_3ilmi)
- `atom_text` (was `text` in ABD — renamed for clarity)
- `anchor_span` (was `source_anchor` in ABD — renamed; same start/end structure)
- `page_hint`, `bonded_cluster_trigger`, `atomization_notes`
- `internal_tags`, `footnote_refs`

**Field renames from ABD:**
- `text` → `atom_text` (clarity in multi-schema context)
- `source_anchor` → `anchor_span` (task specification term)
- `char_offset_start`/`char_offset_end` → `start`/`end` (simplified)

**Fields added for KR:**
- `passage_id` — Links atom to its parent passage for pipeline traceability
- `book_id` — Already existed in ABD atom_record; confirmed as required
- `science_id` — Inherited from passage; carries science identity per §7.3
- `context_role` — Pre-annotation of the atom's role if used as context in an excerpt
- `relation` — Optional typed relation to another atom

**Fields from ABD not carried forward:**
- `canonical_text_sha256` — Replaced by passage-level integrity in KR's architecture

---

### 2.5 `excerpt.json`

**Boundary:** Excerpting engine → Taxonomy engine (draft excerpts)

**ABD files analyzed:**
- `schemas/gold_standard_schema_v0.3.3.json` → `definitions/excerpt_record`

**Fields kept from ABD:**
- `excerpt_id` (same pattern), `book_id`, `source_layer`, `excerpt_kind`
- `excerpt_title`, `excerpt_title_reason`
- `taxonomy_version`, `taxonomy_path`
- `heading_path`, `boundary_reasoning`, `case_types`
- `relations`, `cross_science_context`, `related_science`
- `interwoven_group_id`

**Field mappings from ABD:**
- `taxonomy_node_id` → `proposed_leaf` (renamed: at draft stage, placement is a proposal)
- `core_atoms` + `context_atoms` → `atom_ids` + `core_atom_ids` + `context_atom_ids` (restructured for clarity)

**Fields added for KR:**
- `passage_id` — Links excerpt to its source passage
- `science_id` — Which science tree this excerpt targets (required, per §7.3)
- `lifecycle_stage` — Enum with value `"draft"` at this boundary. Becomes `"reviewed"` after human gate, `"placed"` after taxonomy writes to library, per §2.4.
- `primary_text` — Complete verbatim text of the excerpt. Text integrity invariant target per §5.1.
- `self_containment_score` — Quantifies self-containment per §5.1
- `school` — Scholarly school (مذهب) if applicable per §2.4
- `metadata_extensions` — Open object for science-specific metadata per §5.4

**ABD fields not carried forward:**
- `status` (gold/gold_migrated/superseded) — ABD-specific gold standard lifecycle; replaced by KR's lifecycle_stage
- `taxonomy_change_triggered` — ABD-specific gold standard tracking
- `supersedes_excerpt_id` — ABD gold standard revision tracking
- `annotator_notes` — ABD gold standard annotation; KR uses review_flags + review_metadata in placed_excerpt
- `source_spans` — ABD internal tracking not needed at this boundary

---

### 2.6 `placed_excerpt.json`

**Boundary:** Taxonomy engine → Library → Synthesizing engine

**ABD files analyzed:**
- No direct ABD equivalent (ABD doesn't have this lifecycle stage)

**Schema design:**
Uses `allOf` + `$ref` to extend `excerpt.json` with placement-specific fields.

**Fields added beyond excerpt.json:**
- `lifecycle_stage` — Overridden to const `"placed"`
- `confirmed_leaf` — Actual leaf path (taxonomy engine may adjust from proposed_leaf)
- `placement_confidence` — Float confidence score
- `placed_utc` — Placement timestamp
- `review_metadata` — Human gate review outcome (reviewer notes, approval timestamp, modifications)
- `verified_flagged_status` — Content classification per §2.4 and §3.2
- `flag_reason` — Explanation for flagged excerpts
- `taxonomy_version_at_placement` — Tree version at placement time

---

### 2.7 `entry.json`

**Boundary:** Synthesizing engine → Library (terminal product)

**ABD files analyzed:**
- No direct ABD equivalent (synthesizing engine doesn't exist in ABD)

**Schema designed from VISION.md §6:**
- `entry_id`, `leaf_path`, `science_id`, `school_group`
- `generated_utc`, `generator_model`, `source_excerpt_ids`
- `factual_layer` — Main entry text per §6.1
- `analytical_layer` — Synthesized reasoning per §6.1 (marked `x-provisional: true`)
- `critical_analysis` — Flagged content analysis per §6.2 (marked `x-provisional: true`)
- `staleness_hash` — Hash for detecting regeneration need per §6.3
- `version` — Regeneration version counter
- `is_stale` — Staleness flag per §6.3
- `entry_metadata` — Statistics (source count, author count, etc.)

**Provisional fields:**
`analytical_layer` and `critical_analysis` are marked with `"x-provisional": true` because the OPEN QUESTION in §6.4 (analytical layer boundary) is unresolved.

---

## 3. Shamela-Specific Fields Excluded

The following fields were found in ABD schemas and are Shamela-specific. They are listed here so that the normalization engine's Shamela normalizer SPEC.md knows what to produce as extensions.

### Source metadata level:
| Field | ABD Source | Purpose |
|-------|-----------|---------|
| `shamela_book_id` | `intake_metadata_schema.json` | Shamela numeric book ID |
| `shamela_author_short` | `intake_metadata_schema.json` | Short author from title span |
| `shamela_page_count` | `intake_metadata_schema.json` | Shamela-reported page count |
| `shamela_edition` | `intake_metadata_schema.json` | Shamela الطبعة field |
| `shamela_volume_count` | `intake_metadata_schema.json` | Shamela-declared volume count |
| `shamela_pub_date` | `intake_metadata_schema.json` | Shamela platform pub date |
| `html_qism_field` | `intake_metadata_schema.json` | Raw القسم field |

### Page record level:
| Field | ABD Source | Purpose |
|-------|-----------|---------|
| `raw_matn_html` | `pages.jsonl` sample | Raw HTML main text |
| `raw_fn_html` | `pages.jsonl` sample | Raw HTML footnotes |
| `footnote_section_format` | `pages.jsonl` sample | Footnote format type |
| `starts_with_zwnj_heading` | `pages.jsonl` sample | ZWNJ heading flag |

### Division node level:
| Field | ABD Source | Purpose |
|-------|-----------|---------|
| `heading_in_html` | `divisions_schema_v0.1.json` | HTML `<span class='title'>` presence |
| `inline_heading` | `divisions_schema_v0.1.json` | Inline heading detection |
| `heading_text_boundary` | `divisions_schema_v0.1.json` | Character offset for inline heading |

---

## 4. Open Questions and Ambiguities

1. **Analytical layer boundary (§6.4 OPEN QUESTION).** The extent to which the synthesizing engine's analytical layer may include knowledge not directly from source excerpts is unresolved. The `analytical_layer` and `critical_analysis` fields in `entry.json` are marked `x-provisional: true`.

2. **Science identifier vocabulary.** ABD uses a closed enum of 4 sciences (`balagha`, `sarf`, `nahw`, `imlaa`). KR's `science_scope` uses open strings to support the full inventory of primary and supporting sciences per §1.2. The canonical science identifier vocabulary needs to be established when science trees are created.

3. **Atom anchor reference frame.** ABD's atom offsets reference a "canonical text file" per source layer. KR's atoms reference the `passage_text` field. If a passage is re-generated (e.g., due to normalization corrections), existing atom offsets would be invalidated. The passaging engine's SPEC.md should address this.

4. **Footnote structure uniformity.** The footnote object structure varies slightly between ABD's pages.jsonl (implicit object) and the formalized schema. KR's schema normalizes this to `{ref_number, text}` objects. Normalizers must produce this uniform structure.

5. **`content_type` at page vs. passage level.** ABD pages use free-form content_type strings (e.g., `"text"`), while passages use an enum. The normalization boundary should define the canonical set of page-level content types.

6. **Division node `human_override`.** ABD's divisions schema includes a `human_override` sub-object. KR's normalized package omits it (overrides should be applied before output). If the normalization engine needs to track override provenance in the output, this field should be reconsidered.

7. **Excerpt `source_spans`.** ABD's excerpt_record includes a `source_spans` object tracking the physical text coverage. KR's excerpt schema relies on `primary_text` + `atom_ids` for this purpose. If physical span tracking is needed for the synthesizing engine, `source_spans` should be added.
