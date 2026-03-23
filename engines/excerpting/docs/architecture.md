# Module Architecture — Excerpting Engine

## Data Flow

```
NormalizedPackage (input from normalization engine)
    │
    ▼
phase1_assembly.py  ── §4: 7 deterministic steps ──▶  list[AssembledChunk]
    │
    ▼
phase2_classify.py  ── §5.2 + §5.4.1–2: LLM classify + normalize ──▶  dict[chunk_id → list[ClassifiedSegment]]
    │
    ▼
phase2_group.py     ── §5.3 + §5.4.3: LLM group + verify ──▶  dict[chunk_id → list[TeachingUnit]]
    │
    ▼
phase3_deterministic.py ── §7.1: 9 fields from data model ──▶  list[ExcerptRecord] (partial)
    │
    ▼
phase3_enrichment.py ── §7.2: LLM enrichment per chunk ──▶  list[ExcerptRecord] (enriched)
    │
    ▼
phase3_consensus.py ── §7.3: cross-provider verification + gates ──▶  list[ExcerptRecord] (final)
    │
    ▼
phase3_validation.py ── §7.4: V-P3-1 through V-P3-9 ──▶  validation results
    │
    ▼
writer.py           ── output: excerpts.jsonl + gate_queue.jsonl
```

## Module Specifications

### `phase1_assembly.py` — §4 Deterministic Preprocessing

**Purpose:** Transform a `NormalizedPackage` into `list[AssembledChunk]`.

**SPEC sections:** §4.1–§4.9 (7 sequential steps + heading alignment + validation).

**Input:** `NormalizedPackage` (from `engines/normalization/contracts.py`).

**Output:** `list[AssembledChunk]` (from `engines/excerpting/contracts.py`).

**Key functions:**
- `find_leaf_divisions()` — §4.2: recursive tree walk, skip criteria, heading paths
- `assemble_text()` — §4.3: cross-page joining with boundary_continuity separators
- `merge_tiny_divisions()` — §4.4: merge siblings under TINY_DIVISION_WORDS threshold
- `split_oversized_division()` — §4.5: split at structural markers, recursive
- `aggregate_metadata()` — §4.7: OR-aggregate flags, collect footnotes, renumber if needed
- `rebase_text_layers()` — §4.6: translate per-page offsets to assembled-text coordinates
- `check_heading_alignment()` — §4.8: quality flag, does not gate processing
- `validate_phase1()` — §4.9: V-P1-1 through V-P1-6
- `run_phase1()` — top-level orchestrator for all 7 steps

**No LLM calls.** Fully unit-testable. This is CC Session 1's build target.

### `phase2_classify.py` — §5.2 + §5.4.1–2 Classification and Normalization

**Purpose:** Classify each chunk's text into segments, normalize offsets.

**SPEC sections:** §5.2 (classify), §5.4.1 (offset normalization), §5.4.2 (segment verification).

**Input:** `list[AssembledChunk]`, `ExcerptingConfig`.

**Output:** `dict[str, list[ClassifiedSegment]]` — keyed by `chunk_id`.

**Key functions:**
- `classify_chunk()` — §5.2: one LLM call per chunk → `ClassificationResult`
- `normalize_offsets()` — §5.4.1: snippet-anchored remapping to canonical tokens
- `verify_segments()` — §5.4.2: V-P2-1 through V-P2-9
- `run_phase2a()` — orchestrator with retry logic per §5.5.2

**Design note:** Offset normalization is in the same file as classification because they share a retry loop — if normalization fails, the classify call is retried.

### `phase2_group.py` — §5.3 + §5.4.3 Teaching Unit Grouping

**Purpose:** Group classified segments into teaching units.

**SPEC sections:** §5.3 (group), §5.4.3 (unit verification).

**Input:** `list[AssembledChunk]`, `dict[str, list[ClassifiedSegment]]`, `ExcerptingConfig`.

**Output:** `dict[str, list[TeachingUnit]]` — keyed by `chunk_id`.

**Key functions:**
- `group_chunk()` — §5.3: one LLM call per chunk → `ExtractionResult`
- `verify_units()` — §5.4.3: V-P2-10 through V-P2-19
- `run_phase2b()` — orchestrator with retry logic

### `phase3_deterministic.py` — §7.1 Deterministic Fields + Layer Attribution

**Purpose:** Compute 9 deterministic fields (F-DET-1 through F-DET-9) and layer attribution rules (LA-1 through LA-4).

**SPEC sections:** §7.1, §6.2 (multi-layer handling).

**Input:** `list[AssembledChunk]`, `dict[str, list[TeachingUnit]]`, `NormalizedManifest`.

**Output:** `list[ExcerptRecord]` — with all deterministic fields populated, LLM fields as `None`.

**Key functions:**
- `compute_excerpt_id()` — F-DET-1
- `extract_primary_text()` — F-DET-2: substring extraction preserving whitespace
- `compute_layer_attribution()` — F-DET-3 + LA-1 through LA-4
- `compute_content_types()` — F-DET-4
- `detect_quran_verses()` — F-DET-5: regex pattern for ﴿...﴾
- `compute_page_range()` — F-DET-6
- `compute_word_offsets()` — F-DET-7
- `filter_relevant_footnotes()` — F-DET-8
- `compute_segment_indices()` — F-DET-9
- `build_deterministic_excerpts()` — assemble all fields into ExcerptRecord

### `phase3_enrichment.py` — §7.2 LLM Enrichment

**Purpose:** Add topic, school, evidence, cross-refs via one LLM call per chunk.

**SPEC sections:** §7.2.

**Input:** `list[ExcerptRecord]` (deterministic), `list[AssembledChunk]`, `ExcerptingConfig`.

**Output:** `list[ExcerptRecord]` — with LLM-enriched fields populated.

**Key functions:**
- `enrich_chunk()` — §7.2: one LLM call per chunk → `EnrichmentResult`
- `apply_enrichment()` — merge LLM results into ExcerptRecords
- `run_phase3_enrichment()` — orchestrator with retry + deterministic fallback

### `phase3_consensus.py` — §7.3 Verification and Gates

**Purpose:** Cross-provider verification, consensus resolution, human gate triggers.

**SPEC sections:** §7.3.

**Input:** `list[ExcerptRecord]` (enriched), `list[AssembledChunk]`, `ExcerptingConfig`.

**Output:** `list[ExcerptRecord]` (final) + `list[GateEntry]`.

**Key functions:**
- `verify_chunk()` — §7.3.2: call verification model for attribution + school
- `resolve_consensus()` — §7.3.3: 2-of-3 majority or 3-way escalation
- `check_gate_triggers()` — §7.3.4: EX-G-001, EX-G-002, EX-G-003
- `run_consensus()` — orchestrator

### `phase3_validation.py` — §7.4 Output Validation

**Purpose:** Final self-validation before output.

**SPEC sections:** §7.4.

**Input:** `list[ExcerptRecord]`.

**Output:** `list[ValidationResult]` — pass/fail per check.

**Key functions:**
- `validate_phase3()` — V-P3-1 through V-P3-9

### `pipeline.py` — Orchestrator

**Purpose:** Run Phase 1 → Phase 2 → Phase 3 for one source.

**Input:** `NormalizedPackage`, `ExcerptingConfig`.

**Output:** `list[ExcerptRecord]` + `list[GateEntry]` + telemetry.

**Key functions:**
- `process_source()` — top-level pipeline entry point
- `load_config()` — §8.3 config loading (defaults → engine yaml → per-source yaml)

### `writer.py` — Output Writer

**Purpose:** Write `excerpts.jsonl` and `gate_queue.jsonl`.

**SPEC sections:** §2.2.1.

**Input:** `list[ExcerptRecord]`, `list[GateEntry]`, output directory path.

**Output:** Files written to `library/sources/{source_id}/excerpts/`.

**Key functions:**
- `write_excerpts()` — one ExcerptRecord per JSONL line
- `write_gate_queue()` — gate entries
- `write_processing_log()` — telemetry + error log

## Build Session Plan

| Session | Scope | Dependencies |
|---------|-------|-------------|
| 1 | `phase1_assembly.py` | None (fully deterministic) |
| 2 | `phase2_classify.py` + `phase2_group.py` | Session 1 output types |
| 3 | `phase3_deterministic.py` | Sessions 1–2 output types |
| 4 | `phase3_enrichment.py` + `phase3_consensus.py` | Session 3 output types |
| 5 | `phase3_validation.py` + `pipeline.py` + `writer.py` | All prior sessions |
| 6 | Integration testing + cross-engine contract tests | All modules |
