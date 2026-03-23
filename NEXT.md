# NEXT — Excerpting Engine: Rewrite contracts.py from Scratch

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Excerpting SPEC: ✅ COMPLETE (2387 lines, 28 error codes, 29 invariants)
- kr-integrity audit: ✅ PASS (11 HIGH, 15 MEDIUM, 2 LOW — all fixed)
- Post-audit deep review: ✅ PASS (1 HIGH, 3 MEDIUM — all fixed)
- HEAD commit: `452edcd` (start prompt for independent handoff audit session)
- **Excerpting contracts.py: STALE — 557 lines, old 7-engine architecture. DELETE AND REWRITE.**
- Excerpting tests: 0 existing tests passing (no build work done yet)

## What to Do

Delete `engines/excerpting/contracts.py` and write it from scratch. The new file defines ALL Pydantic models for the excerpting engine's data pipeline:

```
NormalizedPackage (input — from engines/normalization/contracts.py, DO NOT redefine)
  → AssembledChunk (Phase 1 output)
    → ClassifiedSegment (Phase 2a output)
      → TeachingUnit (Phase 2b output)
        → ExcerptRecord (Phase 3 output / engine output)
```

Plus: enumerations, sub-types, LLM response schemas, error codes, invariant validators, configuration constants, and test factory helpers.

## Context

The old `contracts.py` defines types like `LifecycleStage`, `ContextAtomRole`, `ExcerptStatus` that no longer exist. The new SPEC uses a completely different data model (3 intermediate types + 1 output type instead of the old single-ExcerptRecord model). A patch would be more work than a rewrite and would leave dead code.

The integrity audit (commits `10537ce` + `2ae92ac`) and a follow-up cleanup (`073f078`) introduced 12 new artifacts that must appear in the new contracts.py. These are listed explicitly in the Critical Audit Artifacts table below.

## Owner Action Needed

None — this is a CC-only task.

## Read First (in this order)

1. **`engines/excerpting/CLAUDE.md`** — engine orientation (109 lines)
2. **`engines/excerpting/SPEC.md` §2.3** (lines 79–278) — internal data model: enumerations, AssembledChunk, ClassifiedSegment, TeachingUnit, ExcerptRecord summary, design constraints
3. **`engines/excerpting/SPEC.md` §2.2** (lines 365–521) — output contract: ExcerptRecord (33 fields, 7 categories), sub-type definitions (PageRange, AuthorAttribution, ScholarAttribution, EvidenceRef, TakhrijEntry, CrossReference, TermVariant, ConsensusRecord, ConsensusDecision), output invariants I-ER-1 through I-ER-7
4. **`engines/excerpting/SPEC.md` §3.2** (lines 539–558) — self-containment formal criteria (C-SC-1 through C-SC-5), referenced by invariants
5. **`engines/excerpting/SPEC.md` §8.1** (lines 1915–1986) — error code catalog (28 codes in 5 categories)
6. **`engines/excerpting/SPEC.md` §8.3** (lines 2018–2074) — configuration parameters (19 total: 18 static in ExcerptingConfig + 1 dynamic CLASSIFY_MAX_TOKENS)
7. **`engines/excerpting/SPEC.md` §7.2.4** (lines 1669–1728) — LLM enrichment response schema (EnrichmentResult, UnitEnrichment, ResolvedScholar, TakhrijEntry, TermVariant, CrossReference)
8. **`engines/excerpting/SPEC.md` §7.3.2** (lines 1765–1824) — verification response schema (VerificationResult, VerificationItem)
9. **`engines/excerpting/SPEC.md` §5.2.4** (lines 874–887) — Phase 2a classification response schema (ClassificationResult wrapping ClassifiedSegment)
10. **`engines/excerpting/SPEC.md` §5.3.4** (lines 1019–1031) — Phase 2b grouping response schema (ExtractionResult wrapping TeachingUnit)
11. **`engines/normalization/contracts.py`** — reference implementation for Pydantic patterns (725 lines). Follow the same style: `str, Enum` for enums, `BaseModel` for models, `Field(...)` with descriptions, `model_validator` for cross-field checks, sectioned with `# ═══` comment blocks
12. **`engines/normalization/tests/conftest.py`** (lines 1–120) — factory helper patterns: `_make_source_metadata(**overrides)` as the template for `_make_assembled_chunk(**overrides)`, `_make_teaching_unit(**overrides)`, `_make_excerpt_record(**overrides)` factories

Do NOT read the entire SPEC. The SPEC is 2387 lines; the sections listed above contain everything contracts.py needs. Sections §4–§7 contain implementation logic (algorithms, prompts, processing steps) that belongs in the engine code, not in contracts.

## What to Build

### 1. Enumerations (from §2.3.1)

**`ScholarlyFunction`** — 16 values: `definition`, `rule_statement`, `evidence_quran`, `evidence_hadith`, `evidence_ijma`, `evidence_qiyas`, `evidence_rational`, `opinion_statement`, `refutation`, `example`, `condition_exception`, `cross_reference`, `narration`, `editorial_note`, `structural_transition`, `unclassified`.

**`SelfContainmentLevel`** — 3 values: `FULL`, `PARTIAL`, `DEPENDENT`.

**`StructuralFormat`** — 7 values. **DO NOT redefine.** Import from `engines.normalization.contracts`. The excerpting engine inherits this enum, it does not own it.

### 2. Sub-types (from §2.2.2 and §2.3.2)

These are referenced by the main types. Define them first.

**`PageRange`** (new from integrity audit):
```
volume: int | null
start_page: int
end_page: int
```

**`AuthorAttribution`**:
```
layer_id: str
author_id: str
coverage_pct: float  # 0.0–1.0
rule_applied: str    # one of "LA-1", "LA-2", "LA-3", "LA-4"
```

**`ScholarAttribution`**:
```
mention_text: str
resolved_name: str | null
role: str            # one of "quoted_opinion", "classification_frame", "refuted_position"
confidence: float    # 0.0–1.0
source: str          # one of "layer_overlap", "llm_enrichment"
```

**`EvidenceRef`**:
```
type: str            # one of "quran", "hadith", "ijma"
surah: int | null
ayah_start: int | null
ayah_end: int | null
text_snippet: str
marker_text: str | null
scope: str | null
```

**`TakhrijEntry`**:
```
hadith_text_snippet: str
collections: list[str]
hadith_numbers: list[str]    # may be empty
grade: str | null
grade_source: str | null
```

**`CrossReference`**:
```
reference_text: str
target_description: str | null
target_div_id: str | null = None    # MUST default to None — see note below
resolved: bool
```

**IMPORTANT:** `target_div_id` must have a default of `None` (not just nullable without a default). Reason: this type is shared between the ExcerptRecord (§2.2.2, which has `target_div_id`) and the LLM response schema (§7.2.4, which does NOT produce `target_div_id`). Phase 3 deterministic processing (division tree heading search) populates `target_div_id` after LLM enrichment. If `target_div_id` is required-without-default, `instructor` will reject the LLM response for the missing field.

**`TermVariant`**:
```
term: str
variants: list[str]
```

**`ConsensusDecision`**:
```
decision_type: str
enrichment_value: str
verifier_value: str | null
verifier_agrees: bool | null
escalation_value: str | null
final_value: str
resolution_method: str
```

**`ConsensusRecord`**:
```
decisions: list[ConsensusDecision]
```

**`JoinPoint`** (sub-type of AssemblyMetadata):
```
after_unit_index: int
before_unit_index: int
boundary_type: BoundaryContinuityType  # imported from normalization contracts
separator_used: str
char_offset_in_assembled: int
```

**`AssemblyMetadata`**:
```
constituent_unit_indices: list[int]
join_points: list[JoinPoint]
layer_split_points: list[int]           # NEW from audit — empty for unsplit
footnote_renumber_map: dict[str, str] | null  # NEW from audit — null when no renumbering
```

**`SplitInfo`**:
```
original_div_id: str
chunk_index: int    # 0-based
total_chunks: int
split_method: str   # one of "heading_marker", "section_break", "paragraph_break", "sentence_boundary"
```

### 3. Intermediate Types (from §2.3.2–§2.3.4)

**`AssembledChunk`** (Phase 1 output, §2.3.2, 16 fields):
```
chunk_id: str
source_id: str
div_id: str
div_path: list[str]
assembled_text: str
word_count: int
total_tokens: int
text_layers: list[TextLayerSegment]       # imported from normalization contracts
footnotes: list[Footnote]                 # imported from normalization contracts
content_flags: ContentFlags               # imported from normalization contracts
physical_pages: list[PhysicalPage]        # imported from normalization contracts
structural_format: StructuralFormat       # imported from normalization contracts
heading_alignment_ok: bool
assembly_metadata: AssemblyMetadata
merge_history: list[str] | null           # present only when merged
split_info: SplitInfo | null              # present only when split
```

Validators on AssembledChunk:
- I-AC-1: `word_count` and `total_tokens` consistent with `assembled_text`
  - word_count = count of whitespace-delimited tokens containing ≥1 Arabic char (U+0600–U+06FF)
  - total_tokens = `len(assembled_text.split())`
- I-AC-5: if `split_info` present, `chunk_id` must end with `_chunk_{split_info.chunk_index}`
- I-AC-6: if `merge_history` present, len ≥ 2 and first element == `div_id`
- I-AC-7: `merge_history` and `split_info` are mutually exclusive (not both non-None)

**`ClassifiedSegment`** (Phase 2a output, §2.3.3, 6 fields):
```
segment_index: int
start_word: int       # 0-based, inclusive
end_word: int         # 0-based, inclusive
text_snippet: str     # first 50 chars from assembled_text
scholarly_function: ScholarlyFunction
confidence: float     # 0.0–1.0
```

Validators on ClassifiedSegment:
- I-CS-6: confidence in [0.0, 1.0]

**`TeachingUnit`** (Phase 2b output, §2.3.4, 10 fields):
```
unit_index: int
segment_indices: list[int]
start_word: int       # 0-based, inclusive
end_word: int         # 0-based, inclusive
text_snippet: str     # first 80 chars from assembled_text
primary_function: ScholarlyFunction
secondary_functions: list[ScholarlyFunction]
description_arabic: str
self_containment: SelfContainmentLevel
self_containment_notes: str | null
```

Validators on TeachingUnit:
- I-TU-6: if `self_containment` is FULL, `self_containment_notes` must be None
- I-TU-7: if `self_containment` is PARTIAL or DEPENDENT, `self_containment_notes` must be present and non-empty

### 4. Output Type (from §2.2.2, 33 fields across 7 categories)

**`ExcerptRecord`** — the engine's final output. See §2.2.2 for the complete specification. All fields listed there.

Key fields by category:

**Identification (6):** `excerpt_id`, `source_id`, `div_id`, `chunk_index`, `unit_index`, `div_path`

**Text (6):** `primary_text`, `text_snippet`, `start_word`, `end_word`, `segment_indices`, `physical_pages` (PageRange | null)

**Classification (4):** `primary_function`, `secondary_functions`, `content_types`, `description_arabic`

**Self-containment (3):** `self_containment`, `self_containment_notes`, `context_hint`

**Attribution (5):** `primary_author_layer`, `attribution_confidence`, `quoted_scholars`, `school`, `school_confidence`

`attribution_confidence` semantics (from §2.2.2): `null` for deterministic attribution (LA-1/LA-2/LA-4), `0.67` for 2-of-3 consensus (LA-3), `0.0` for all-3-disagree (EX-G-001). Document these in the field description.

**Topic/taxonomy (2):** `excerpt_topic`, `terminology_variants`

**Evidence/references (4):** `evidence_refs`, `takhrij_data`, `cross_references`, `footnotes_relevant`

**Metadata/flags (3):** `consensus_metadata`, `gate_flags`, `review_flags`

Validators on ExcerptRecord:
- I-ER-4: self-containment consistency (FULL → no notes, no context_hint; PARTIAL → notes present, context_hint if LLM succeeded; DEPENDENT → notes present, no context_hint)
- I-ER-5: `primary_author_layer` must have non-null `layer_id` and `author_id`

### 5. LLM Response Schemas (from §5.2.4, §5.3.4, §7.2.4, §7.3.2)

These are used for structured output parsing via `instructor` + Pydantic. Define them in a separate section of contracts.py (after the main types).

**From §5.2.4 (Phase 2a classification):**
- `ClassificationResult` (2 fields: `segments: list[ClassifiedSegment]`, `total_segments: int`)

**From §5.3.4 (Phase 2b grouping):**
- `ExtractionResult` (3 fields: `teaching_units: list[TeachingUnit]`, `total_units: int`, `notes: Optional[str] = None`)

**From §7.2.4 (enrichment):**

`ResolvedScholar` (4 fields):
```
mention_text: str
resolved_name: str | null
role: str              # one of "quoted_opinion", "classification_frame", "refuted_position"
confidence: float      # 0.0–1.0
```

`UnitEnrichment` (9 fields):
```
unit_index: int
excerpt_topic: list[str]                       # 1–3 Arabic keywords
school: str | null                             # required=yes, nullable (same DD8 pattern 1 as ExcerptRecord)
school_confidence: float | null                # required=yes, nullable (differs from ExcerptRecord which is required=no)
resolved_scholars: list[ResolvedScholar]       # may be empty
takhrij_data: list[TakhrijEntry] = []          # required=no, NOT nullable — empty list default, NOT None
terminology_variants: list[TermVariant]        # may be empty
cross_references: list[CrossReference]         # may be empty
context_hint: str | null                       # non-null only when self_containment is PARTIAL
```

**CRITICAL optionality note:** `UnitEnrichment.takhrij_data` is `list[TakhrijEntry]` with default `[]` (non-nullable, optional field). This DIFFERS from `ExcerptRecord.takhrij_data` which is `list[TakhrijEntry] | null` with default `None` (nullable). The LLM returns an empty list (not null) when no hadith content exists. The engine code maps UnitEnrichment's empty list → ExcerptRecord's null when appropriate.

**CRITICAL optionality note:** `UnitEnrichment.school_confidence` is required=**yes** with nullable type (SPEC §7.2.4 line 1687: `float | null, required=yes`). This means `Optional[float]` with NO default — the LLM must always produce this field. This differs from `ExcerptRecord.school_confidence` which is required=**no** (`Optional[float] = None`).

`EnrichmentResult` (2 fields):
```
enrichments: list[UnitEnrichment]
total_units: int
```

**From §7.3.2 (verification):**

`VerificationItem` (5 fields):
```
item_index: int
agrees: bool
alternative: str | null
confidence: float       # 0.0–1.0 — NEW from audit
reasoning: str
```

`VerificationResult` (1 field):
```
items: list[VerificationItem]
```

### 6. Error Codes (from §8.1)

Define as a class with string constants (not an enum — error codes are logged as strings, not used as field types):

```python
class ExcerptingErrorCodes:
    """All 28 error codes from SPEC §8.1."""
    # Phase 1 — Assembly
    EX_A_002 = "EX-A-002"  # Empty content unit range
    EX_A_003 = "EX-A-003"  # Layer rebasing gap
    EX_A_004 = "EX-A-004"  # Layer segment overflow
    EX_A_005 = "EX-A-005"  # Duplicate footnote ref_marker
    EX_A_006 = "EX-A-006"  # Heading misalignment
    EX_A_010 = "EX-A-010"  # Empty division tree
    EX_A_011 = "EX-A-011"  # Content unit not found
    EX_A_012 = "EX-A-012"  # Diacritic-mismatched snippet (NEW from audit)
    # Phase 2 — Classification and Grouping
    EX_C_001 = "EX-C-001"  # Classification LLM failed
    EX_C_002 = "EX-C-002"  # Grouping LLM failed
    EX_C_003 = "EX-C-003"  # Offset normalization failed
    EX_C_004 = "EX-C-004"  # Segment coverage violated
    EX_C_005 = "EX-C-005"  # Unit coverage violated
    # Phase 3 — Metadata Enrichment
    EX_M_001 = "EX-M-001"  # Attribution ambiguous (LA-3)
    EX_M_002 = "EX-M-002"  # LLM enrichment failed
    EX_M_003 = "EX-M-003"  # School disagreement
    EX_M_004 = "EX-M-004"  # Null primary_author after Phase 3
    EX_M_005 = "EX-M-005"  # Topic count outside 1–3
    EX_M_006 = "EX-M-006"  # Self-containment metadata inconsistency
    EX_M_007 = "EX-M-007"  # Invalid Quran reference
    EX_M_008 = "EX-M-008"  # Gate entry not written (CRITICAL)
    EX_M_009 = "EX-M-009"  # Footnote offset outside excerpt range
    EX_M_010 = "EX-M-010"  # Unknown content type
    # Validation
    EX_V_001 = "EX-V-001"  # Phase 1 self-validation failed
    EX_V_002 = "EX-V-002"  # Primary text integrity check failed
    # Human Gate Triggers
    EX_G_001 = "EX-G-001"  # 3 models all disagree on attribution
    EX_G_002 = "EX-G-002"  # DEPENDENT self-containment
    EX_G_003 = "EX-G-003"  # School conflict with source metadata
```

### 7. Invariant Validator Functions

Write standalone validator functions called by the engine at phase boundaries. Each function takes the relevant objects and raises `ValueError` with the invariant code if violated. Group by phase:

**AssembledChunk validators (I-AC-*):**
- `validate_ac_invariants(chunk: AssembledChunk)` — checks I-AC-1, I-AC-5, I-AC-6, I-AC-7
- `validate_layer_coverage(text_layers: list, assembled_text_len: int)` — checks I-AC-2 (layer coverage exactness)

See SPEC §2.3.2 lines 188–194 for full invariant definitions:
- I-AC-1: `word_count` = Arabic tokens count, `total_tokens` = `len(assembled_text.split())`
- I-AC-2: `text_layers` character ranges cover `[0, len(assembled_text))` exactly
- I-AC-5: if `split_info`, `chunk_id` ends with `_chunk_{split_info.chunk_index}`
- I-AC-6: if `merge_history`, len ≥ 2 and first element == `div_id`
- I-AC-7: `merge_history` and `split_info` mutually exclusive

**ClassifiedSegment validators (I-CS-*):**
- `validate_cs_invariants(segments: list[ClassifiedSegment], total_tokens: int)` — checks I-CS-1 through I-CS-6

See SPEC §2.3.3 lines 216–221 for full invariant definitions:
- I-CS-1: `segment_index` values equal list positions (0, 1, 2, ...)
- I-CS-2: contiguous — `s[i+1].start_word == s[i].end_word + 1`
- I-CS-3: first segment starts at word 0
- I-CS-4: last segment ends at `total_tokens - 1`
- I-CS-5: full coverage — union of word ranges = `[0, total_tokens - 1]`
- I-CS-6: `confidence` in `[0.0, 1.0]`

**TeachingUnit validators (I-TU-*):**
- `validate_tu_invariants(units: list[TeachingUnit], segments: list[ClassifiedSegment], total_tokens: int)` — checks I-TU-1 through I-TU-9
- **Important:** I-TU-8 (description_arabic word count 5–35) is a WARNING per SPEC §2.3.4 line 250, NOT a rejection. Use `logging.getLogger(__name__).warning(...)` (same pattern as normalization engine). All other I-TU invariants are hard failures that raise `ValueError`.

See SPEC §2.3.4 lines 243–251 for full invariant definitions:
- I-TU-1: `unit_index` values equal list positions (0, 1, 2, ...)
- I-TU-2: `segment_indices` is contiguous ascending (e.g., `[3, 4, 5]`)
- I-TU-3: every segment assigned to exactly one unit — union of all `segment_indices` = `{0, ..., total_segments - 1}`
- I-TU-4: units contiguous in word space — `u[i+1].start_word == u[i].end_word + 1`
- I-TU-5: `start_word == segments[segment_indices[0]].start_word` and `end_word == segments[segment_indices[-1]].end_word`
- I-TU-6: FULL → `self_containment_notes` must be None
- I-TU-7: PARTIAL or DEPENDENT → `self_containment_notes` must be present and non-empty
- I-TU-8: `description_arabic` 5–35 Arabic words (WARNING only, not rejection)
- I-TU-9: `primary_function` must be one of the constituent segments' functions

**ExcerptRecord validators (I-ER-*):**
- `validate_er_invariants(record: ExcerptRecord)` — checks I-ER-4, I-ER-5
- `validate_er_collection_invariants(records: list[ExcerptRecord])` — checks I-ER-1 (uniqueness) and I-ER-3 (ordering)

See SPEC §2.2.3 lines 493–505 for full invariant definitions:
- I-ER-1: no duplicate `excerpt_id` values
- I-ER-3: records ordered by `div_id`, then `chunk_index`, then `unit_index`
- I-ER-4: self-containment consistency. FULL → no notes, no context_hint. PARTIAL → notes present; context_hint present **unless** `"llm_enrichment_failed" in record.review_flags` (in which case context_hint may be None). DEPENDENT → notes present, no context_hint.
- I-ER-5: `primary_author_layer.layer_id` and `primary_author_layer.author_id` must be non-null

**Excluded from contracts validators (checked at runtime):**
- I-AC-3 (footnote ref_marker in assembled_text) and I-AC-4 (constituent_unit_indices contiguous ascending) — require access to the assembled text and division tree, which validators do not have. Checked during Phase 1.
- I-ER-2 (primary text immutability) — runtime guarantee, requires access to assembled_text at extraction time. Checked in Phase 3.
- I-ER-6 (no orphan fields) — SPEC structural property verified by design, not by code.
- I-ER-7 (D-023 compliance) — runtime check requiring input data for comparison. Checked in Phase 3.

### 8. Configuration Constants (from §8.3)

Define as a Pydantic model with defaults matching §8.3:

```python
class ExcerptingConfig(BaseModel):
    # Phase 1
    TINY_DIVISION_WORDS: int = 50
    OVERSIZED_DIVISION_WORDS: int = 5000
    # Phase 2
    CLASSIFY_MODEL: str = "anthropic/claude-opus-4.6"
    GROUP_MODEL: str = "anthropic/claude-opus-4.6"
    LLM_TEMPERATURE: float = 0.0
    GROUP_MAX_TOKENS: int = 16384
    RETRY_COUNT: int = 2
    TIMEOUT_SECONDS: int = 120
    # Phase 3
    ENRICH_MODEL: str = "anthropic/claude-opus-4.6"
    ENRICH_MAX_TOKENS: int = 16384
    VERIFY_MODEL: str = "openai/gpt-4.1"
    VERIFY_MAX_TOKENS: int = 8192
    ESCALATION_MODEL: str = "cohere/command-a-03-2025"
    # Human gates
    GATE_ON_DEPENDENT: bool = True
    GATE_ON_ATTRIBUTION_DISAGREEMENT: bool = True
    GATE_ON_SCHOOL_CONFLICT: bool = True
    # Telemetry
    LOG_LEVEL: str = "INFO"
    TELEMETRY_ENABLED: bool = True
```

Note: `CLASSIFY_MAX_TOKENS` is dynamic (scales with input word count per §5.5.1) and is NOT a static config value. Do not include it.

### 9. Factory Helpers for Tests

Create `engines/excerpting/tests/conftest.py`:

```python
def _make_assembled_chunk(**overrides) -> AssembledChunk: ...
def _make_classified_segment(**overrides) -> ClassifiedSegment: ...
def _make_teaching_unit(**overrides) -> TeachingUnit: ...
def _make_excerpt_record(**overrides) -> ExcerptRecord: ...
```

Each factory returns a valid instance with all required fields populated with sensible test defaults. Tests pass only the fields they care about via `**overrides`. Follow the exact pattern in `engines/normalization/tests/conftest.py` lines 59–120 (`defaults` dict + `defaults.update(overrides)` + `return Model(**defaults)`).

The `_make_assembled_chunk` factory must produce a chunk where:
- `assembled_text` is a real Arabic sentence (e.g., `"بسم الله الرحمن الرحيم الحمد لله رب العالمين"`)
- `word_count` and `total_tokens` are computed from that text (I-AC-1 consistency)
- `text_layers` covers [0, len(assembled_text)) with a single segment (I-AC-2 consistency). Use `LayerType.MATN` as the default layer type.
- `physical_pages` has at least one PhysicalPage entry
- `assembly_metadata` has valid `constituent_unit_indices`, empty `join_points`, empty `layer_split_points`, null `footnote_renumber_map`
- `merge_history` and `split_info` are both None (I-AC-7)

The `_make_classified_segment` factory defaults:
- `segment_index=0`, `start_word=0`, `end_word=4`, `text_snippet="بسم الله الرحمن الرحيم الحمد"[:50]`
- `scholarly_function=ScholarlyFunction.DEFINITION`, `confidence=0.9`

The `_make_teaching_unit` factory defaults:
- `unit_index=0`, `segment_indices=[0]`, `start_word=0`, `end_word=4`
- `text_snippet="بسم الله الرحمن الرحيم الحمد لله رب العالمين"[:80]`
- `primary_function=ScholarlyFunction.DEFINITION`, `secondary_functions=[]`
- `description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات"` (≥5 Arabic words for I-TU-8)
- `self_containment=SelfContainmentLevel.FULL`, `self_containment_notes=None` (I-TU-6 satisfied)

The `_make_excerpt_record` factory defaults (**CRITICAL — must satisfy I-ER-4, I-ER-5, DD8**):
- **Identification:** `excerpt_id="exc_src_test_div_test_0_0"`, `source_id="src_test"`, `div_id="div_test"`, `chunk_index=0`, `unit_index=0`, `div_path=["باب الاختبار"]`
- **Text:** `primary_text="بسم الله الرحمن الرحيم"`, `text_snippet="بسم الله الرحمن الرحيم"[:80]`, `start_word=0`, `end_word=3`, `segment_indices=[0]`, `physical_pages=None` (DD8 pattern 2)
- **Classification:** `primary_function=ScholarlyFunction.DEFINITION`, `secondary_functions=[]`, `content_types=[ScholarlyFunction.DEFINITION]`, `description_arabic="وصف عربي قصير للاختبار يتضمن عدة كلمات"`
- **Self-containment:** `self_containment=SelfContainmentLevel.FULL`, `self_containment_notes=None`, `context_hint=None` (I-ER-4: FULL → no notes, no hint)
- **Attribution:** `primary_author_layer=AuthorAttribution(layer_id="layer_matn", author_id="sch_test", coverage_pct=1.0, rule_applied="LA-1")` (I-ER-5), `attribution_confidence=None` (DD8 pattern 2), `quoted_scholars=[]`, `school=None` (**DD8 pattern 1 — must be explicitly passed, no default**), `school_confidence=None` (DD8 pattern 2)
- **Topic:** `excerpt_topic=["اختبار"]`, `terminology_variants=[]`
- **Evidence:** `evidence_refs=[]`, `takhrij_data=None` (DD8 pattern 2), `cross_references=[]`, `footnotes_relevant=[]`
- **Metadata:** `consensus_metadata=None` (DD8 pattern 2), `gate_flags=[]`, `review_flags=[]`

## Design Decisions (pre-resolved — CC does not need to decide these)

1. **Normalization types are imported, not redefined.** `StructuralFormat`, `TextLayerSegment`, `Footnote`, `ContentFlags`, `PhysicalPage`, `BoundaryContinuityType`, `LayerType` — all imported from `engines.normalization.contracts`. If CC needs a type that exists in normalization contracts, import it.

2. **Error codes as a class with string constants, not an Enum.** Error codes are logged as string values ("EX-A-002"), compared as strings, and never used as Pydantic field types. A class with string constants is simpler than an Enum for this use case.

3. **Invariant validators are standalone functions, not model validators.** Some invariants require cross-object checks (e.g., I-TU-3 requires all segments and all units). These cannot be `model_validator` methods on a single model. Standalone functions called at phase boundaries are the right pattern. Per-instance validators (I-TU-6, I-TU-7, I-AC-5, I-AC-6, I-AC-7) CAN be `model_validator` methods AND also checked in the standalone function — defense in depth.

4. **LLM response schemas are separate from engine data types.** `UnitEnrichment` (the LLM response) has different fields than the `ExcerptRecord` (the engine output). Do not conflate them. The engine code maps from response schemas to engine types.

5. **`rule_applied` on AuthorAttribution is a plain string, not an enum.** The values ("LA-1" through "LA-4") are documented in §6.2 and are unlikely to change. An enum would create coupling between contracts.py and the domain rules.

6. **`review_flags` and `gate_flags` are `list[str]`, not enums.** The known flags are documented in §2.2.2, but new flags may be added during build. String lists are extensible without contract changes.

7. **PageRange is a Pydantic model, not a TypedDict.** Consistency with the rest of the file. All structured types are Pydantic models.

8. **Nullable field Pydantic mapping (CRITICAL).** The SPEC §2.2.2 "Required" column has three distinct patterns for nullable types. Map them to Pydantic exactly as follows:

   | SPEC Pattern | Pydantic Code | Fields |
   |---|---|---|
   | `type \| null`, required=**yes** | `field: Optional[type]` — no default, field must be explicitly passed even if value is None | `school` |
   | `type \| null`, required=**no** | `field: Optional[type] = None` — field may be omitted entirely, defaults to None | `physical_pages`, `attribution_confidence`, `school_confidence`, `takhrij_data`, `consensus_metadata` |
   | `type \| null`, **conditional** | `field: Optional[type] = None` + model_validator enforcing when it must be non-null | `self_containment_notes` (non-null when PARTIAL/DEPENDENT), `context_hint` (non-null when PARTIAL + LLM succeeded) |

   Getting these wrong breaks JSON round-tripping: a required=yes field with a default allows silently omitting it; a required=no field without a default forces callers to always specify it.

## Do NOT Do

- **No implementation logic.** contracts.py defines types, validators, and constants. No Phase 1/2/3 processing code. No text assembly. No LLM calls. No offset normalization.
- **No LLM prompt text.** Prompts stay in the SPEC and will be implemented in engine code, not in contracts.
- **No test files beyond conftest.py.** Test files for the actual engine come in build prep (Step 3c). The conftest.py factories are created now because they validate that the Pydantic models are instantiable.
- **No changes to normalization contracts.** If a type is needed from normalization, import it. Do not modify `engines/normalization/contracts.py`.
- **No changes to the SPEC.** If you find something in the SPEC that seems wrong, note it in a comment. Do not modify `engines/excerpting/SPEC.md`.
- **Do not invent fields not in the SPEC.** Every field on every model must trace to a specific SPEC section. If the SPEC does not define it, do not add it.

## Verification

Run these commands before committing:

```bash
# 1. Contracts import cleanly
python -c "from engines.excerpting.contracts import *; print('imports OK')"

# 2. All types are instantiable AND factories produce invariant-valid objects
python -c "
from engines.excerpting.contracts import (
    validate_ac_invariants, validate_cs_invariants,
    validate_tu_invariants, validate_er_invariants,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk, _make_classified_segment,
    _make_teaching_unit, _make_excerpt_record,
)
ac = _make_assembled_chunk()
cs = _make_classified_segment()
tu = _make_teaching_unit()
er = _make_excerpt_record()
# Validate factory outputs pass their own invariants
validate_ac_invariants(ac)
validate_er_invariants(er)
print(f'factories + validators OK: AC={type(ac).__name__}, CS={type(cs).__name__}, TU={type(tu).__name__}, ER={type(er).__name__}')
"

# 3. ALL 4 validator families work on valid data
python -c "
from engines.excerpting.contracts import (
    validate_ac_invariants, validate_layer_coverage,
    validate_cs_invariants, validate_tu_invariants,
    validate_er_invariants, validate_er_collection_invariants,
)
from engines.excerpting.tests.conftest import (
    _make_assembled_chunk, _make_classified_segment,
    _make_teaching_unit, _make_excerpt_record,
)
ac = _make_assembled_chunk()
validate_ac_invariants(ac)
validate_layer_coverage(ac.text_layers, len(ac.assembled_text))
cs = _make_classified_segment(start_word=0, end_word=ac.total_tokens - 1)
validate_cs_invariants([cs], ac.total_tokens)
tu = _make_teaching_unit(start_word=0, end_word=ac.total_tokens - 1, segment_indices=[0])
validate_tu_invariants([tu], [cs], ac.total_tokens)
er = _make_excerpt_record()
validate_er_invariants(er)
validate_er_collection_invariants([er])
print('all 6 validator functions pass on valid data')
"

# 4. Error code count AND string values match SPEC
python -c "
from engines.excerpting.contracts import ExcerptingErrorCodes
codes = {v for k, v in vars(ExcerptingErrorCodes).items() if k.startswith('EX_')}
expected = {
    'EX-A-002','EX-A-003','EX-A-004','EX-A-005','EX-A-006','EX-A-010','EX-A-011','EX-A-012',
    'EX-C-001','EX-C-002','EX-C-003','EX-C-004','EX-C-005',
    'EX-M-001','EX-M-002','EX-M-003','EX-M-004','EX-M-005','EX-M-006','EX-M-007','EX-M-008','EX-M-009','EX-M-010',
    'EX-V-001','EX-V-002',
    'EX-G-001','EX-G-002','EX-G-003',
}
missing = expected - codes
extra = codes - expected
assert not missing, f'Missing error codes: {missing}'
assert not extra, f'Extra error codes: {extra}'
assert len(codes) == 28
print('all 28 error code strings match SPEC exactly')
"

# 5. Enum values match SPEC exactly (both enums)
python -c "
from engines.excerpting.contracts import ScholarlyFunction, SelfContainmentLevel
# ScholarlyFunction
sf_expected = {'definition', 'rule_statement', 'evidence_quran', 'evidence_hadith',
    'evidence_ijma', 'evidence_qiyas', 'evidence_rational', 'opinion_statement',
    'refutation', 'example', 'condition_exception', 'cross_reference',
    'narration', 'editorial_note', 'structural_transition', 'unclassified'}
sf_actual = {sf.value for sf in ScholarlyFunction}
assert sf_expected == sf_actual, f'ScholarlyFunction mismatch: missing={sf_expected-sf_actual}, extra={sf_actual-sf_expected}'
# SelfContainmentLevel
sc_expected = {'FULL', 'PARTIAL', 'DEPENDENT'}
sc_actual = {sc.value for sc in SelfContainmentLevel}
assert sc_expected == sc_actual, f'SelfContainmentLevel mismatch: missing={sc_expected-sc_actual}, extra={sc_actual-sc_expected}'
print('both enum value sets match SPEC exactly')
"

# 6. Cross-engine imports resolve AND field types are correct
python -c "
from engines.excerpting.contracts import AssembledChunk
from engines.normalization.contracts import TextLayerSegment, PhysicalPage
import typing
hints = typing.get_type_hints(AssembledChunk)
assert len(hints) == 16, f'AssembledChunk: expected 16 fields, got {len(hints)}'
# Verify key field types reference normalization types
tl_hint = str(hints.get('text_layers', ''))
pp_hint = str(hints.get('physical_pages', ''))
assert 'TextLayerSegment' in tl_hint, f'text_layers type wrong: {tl_hint}'
assert 'PhysicalPage' in pp_hint, f'physical_pages type wrong: {pp_hint}'
print('cross-engine imports resolve with correct types')
"

# 7. Invariant validators reject invalid data (I-AC-7 AND I-AC-1)
python -c "
from engines.excerpting.contracts import validate_ac_invariants, SplitInfo
from engines.excerpting.tests.conftest import _make_assembled_chunk
# I-AC-7: merge + split mutually exclusive
try:
    ac = _make_assembled_chunk(
        merge_history=['div_test_1_0', 'div_test_1_1'],
        split_info=SplitInfo(original_div_id='div_test_1_0', chunk_index=0, total_chunks=2, split_method='paragraph_break'),
    )
    validate_ac_invariants(ac)
    print('FAIL: I-AC-7 not enforced')
except (ValueError, Exception) as e:
    print(f'I-AC-7 correctly rejects: {type(e).__name__}')
# I-AC-1: word_count mismatch
try:
    ac = _make_assembled_chunk(word_count=999)
    validate_ac_invariants(ac)
    print('FAIL: I-AC-1 not enforced')
except (ValueError, Exception) as e:
    print(f'I-AC-1 correctly rejects: {type(e).__name__}')
"

# 8. ExcerptRecord field names match SPEC exactly
python -c "
from engines.excerpting.contracts import ExcerptRecord
expected_fields = {
    'excerpt_id', 'source_id', 'div_id', 'chunk_index', 'unit_index', 'div_path',
    'primary_text', 'text_snippet', 'start_word', 'end_word', 'segment_indices', 'physical_pages',
    'primary_function', 'secondary_functions', 'content_types', 'description_arabic',
    'self_containment', 'self_containment_notes', 'context_hint',
    'primary_author_layer', 'attribution_confidence', 'quoted_scholars', 'school', 'school_confidence',
    'excerpt_topic', 'terminology_variants',
    'evidence_refs', 'takhrij_data', 'cross_references', 'footnotes_relevant',
    'consensus_metadata', 'gate_flags', 'review_flags',
}
actual_fields = set(ExcerptRecord.model_fields.keys())
missing = expected_fields - actual_fields
extra = actual_fields - expected_fields
assert not missing, f'Missing ExcerptRecord fields: {missing}'
assert not extra, f'Extra ExcerptRecord fields: {extra}'
assert len(actual_fields) == 33
print('ExcerptRecord: all 33 field names match SPEC exactly')
"

# 9. I-TU-6 AND I-TU-7 both enforced
python -c "
from engines.excerpting.contracts import TeachingUnit, SelfContainmentLevel, ScholarlyFunction
# I-TU-6: FULL with notes should fail
try:
    tu = TeachingUnit(
        unit_index=0, segment_indices=[0], start_word=0, end_word=5,
        text_snippet='test', primary_function=ScholarlyFunction.DEFINITION,
        secondary_functions=[], description_arabic='وصف عربي قصير للاختبار يتضمن عدة كلمات',
        self_containment=SelfContainmentLevel.FULL,
        self_containment_notes='should not be here',
    )
    print('FAIL: I-TU-6 not enforced')
except (ValueError, Exception) as e:
    print(f'I-TU-6 correctly rejects: {type(e).__name__}')
# I-TU-7: PARTIAL without notes should fail
try:
    tu = TeachingUnit(
        unit_index=0, segment_indices=[0], start_word=0, end_word=5,
        text_snippet='test', primary_function=ScholarlyFunction.DEFINITION,
        secondary_functions=[], description_arabic='وصف عربي قصير للاختبار يتضمن عدة كلمات',
        self_containment=SelfContainmentLevel.PARTIAL,
        self_containment_notes=None,
    )
    print('FAIL: I-TU-7 not enforced')
except (ValueError, Exception) as e:
    print(f'I-TU-7 correctly rejects: {type(e).__name__}')
"

# 10. ScholarlyFunction enum values match SPEC exactly (dedicated check)
python -c "
from engines.excerpting.contracts import ScholarlyFunction
expected = {'definition', 'rule_statement', 'evidence_quran', 'evidence_hadith',
            'evidence_ijma', 'evidence_qiyas', 'evidence_rational', 'opinion_statement',
            'refutation', 'example', 'condition_exception', 'cross_reference',
            'narration', 'editorial_note', 'structural_transition', 'unclassified'}
actual = {sf.value for sf in ScholarlyFunction}
missing = expected - actual
extra = actual - expected
assert not missing, f'Missing ScholarlyFunction values: {missing}'
assert not extra, f'Extra ScholarlyFunction values: {extra}'
print('ScholarlyFunction values match SPEC exactly')
"

# 11. Sub-type field counts AND key field names
python -c "
from engines.excerpting.contracts import (
    PageRange, AuthorAttribution, ScholarAttribution, EvidenceRef,
    AssemblyMetadata, SplitInfo, JoinPoint, CrossReference,
)
checks = [
    ('PageRange', PageRange, 3, {'volume', 'start_page', 'end_page'}),
    ('AuthorAttribution', AuthorAttribution, 4, {'layer_id', 'author_id', 'coverage_pct', 'rule_applied'}),
    ('ScholarAttribution', ScholarAttribution, 5, {'mention_text', 'resolved_name', 'role', 'confidence', 'source'}),
    ('EvidenceRef', EvidenceRef, 7, {'type', 'surah', 'ayah_start', 'ayah_end', 'text_snippet', 'marker_text', 'scope'}),
    ('AssemblyMetadata', AssemblyMetadata, 4, None),
    ('SplitInfo', SplitInfo, 4, None),
    ('JoinPoint', JoinPoint, 5, None),
    ('CrossReference', CrossReference, 4, {'reference_text', 'target_description', 'target_div_id', 'resolved'}),
]
for name, cls, expected_count, expected_names in checks:
    actual = set(cls.model_fields.keys())
    assert len(actual) == expected_count, f'{name}: expected {expected_count} fields, got {len(actual)}: {actual}'
    if expected_names:
        assert actual == expected_names, f'{name}: field names mismatch. Missing={expected_names-actual}, Extra={actual-expected_names}'
print('All sub-type field counts and names correct')
"

# 12. DD8 nullable/optionality correctness (CRITICAL)
python -c "
from engines.excerpting.contracts import ExcerptRecord
from pydantic import ValidationError
# DD8 pattern 1: school is required=yes (no default) — omitting must fail
try:
    # Build with all required fields EXCEPT school
    ExcerptRecord(
        excerpt_id='exc_test_div_test_0_0', source_id='src_test', div_id='div_test',
        chunk_index=0, unit_index=0, div_path=['test'],
        primary_text='test', text_snippet='test', start_word=0, end_word=0,
        segment_indices=[0],
        primary_function='definition', secondary_functions=[], content_types=['definition'],
        description_arabic='وصف عربي قصير للاختبار يتضمن عدة كلمات',
        self_containment='FULL',
        primary_author_layer={'layer_id': 'l', 'author_id': 'a', 'coverage_pct': 1.0, 'rule_applied': 'LA-1'},
        quoted_scholars=[], excerpt_topic=['test'], terminology_variants=[],
        evidence_refs=[], cross_references=[], footnotes_relevant=[],
        gate_flags=[], review_flags=[],
        # school intentionally OMITTED — should fail
    )
    print('FAIL: DD8 pattern 1 not enforced — school has a default when it should not')
except (ValidationError, TypeError) as e:
    print(f'DD8 pattern 1 correct: school is required (no default)')
"

# 13. CrossReference.target_div_id defaults to None (shared with LLM schema)
python -c "
from engines.excerpting.contracts import CrossReference
# target_div_id omitted — should default to None, not raise
cr = CrossReference(reference_text='كما تقدم', target_description=None, resolved=False)
assert cr.target_div_id is None, f'target_div_id should default to None, got {cr.target_div_id}'
print('CrossReference.target_div_id correctly defaults to None')
"

# 14. LLM response schema field counts
python -c "
from engines.excerpting.contracts import (
    ClassificationResult, ExtractionResult,
    EnrichmentResult, UnitEnrichment, ResolvedScholar,
    VerificationResult, VerificationItem,
)
checks = [
    ('ClassificationResult', ClassificationResult, 2),
    ('ExtractionResult', ExtractionResult, 3),
    ('EnrichmentResult', EnrichmentResult, 2),
    ('UnitEnrichment', UnitEnrichment, 9),
    ('ResolvedScholar', ResolvedScholar, 4),
    ('VerificationResult', VerificationResult, 1),
    ('VerificationItem', VerificationItem, 5),
]
for name, cls, expected in checks:
    actual = len(cls.model_fields)
    assert actual == expected, f'{name}: expected {expected} fields, got {actual}: {sorted(cls.model_fields.keys())}'
print('All 7 LLM schema field counts correct')
"

# 15. Config default sentinel values
python -c "
from engines.excerpting.contracts import ExcerptingConfig
cfg = ExcerptingConfig()
assert cfg.RETRY_COUNT == 2, f'RETRY_COUNT: expected 2, got {cfg.RETRY_COUNT}'
assert cfg.LLM_TEMPERATURE == 0.0, f'LLM_TEMPERATURE: expected 0.0, got {cfg.LLM_TEMPERATURE}'
assert cfg.VERIFY_MODEL == 'openai/gpt-4.1', f'VERIFY_MODEL: expected openai/gpt-4.1, got {cfg.VERIFY_MODEL}'
assert cfg.TIMEOUT_SECONDS == 120, f'TIMEOUT_SECONDS: expected 120, got {cfg.TIMEOUT_SECONDS}'
assert cfg.GATE_ON_DEPENDENT is True, f'GATE_ON_DEPENDENT: expected True, got {cfg.GATE_ON_DEPENDENT}'
print('config default sentinel values match SPEC')
"
```

All 15 checks must pass. If any fail, fix before committing.

**Additional verification (run manually, not scripted):**

After all 15 checks pass, open `contracts.py` and visually verify:
- Every error code string matches the SPEC dash format (e.g., "EX-A-002" not "EX-A-2" or "EXA002") — spot-check 5 codes
- DD8 pattern 1 fields: `school` has no default. DD8 pattern 2 fields: `physical_pages`, `attribution_confidence`, `school_confidence`, `takhrij_data`, `consensus_metadata` all have `= None`
- Review the `_make_excerpt_record` factory defaults satisfy I-ER-4 (FULL → no notes/hint) and I-ER-5 (primary_author_layer has non-null layer_id/author_id)

## Critical Audit Artifacts

The integrity audit and deep review introduced these items that the new contracts.py MUST include:

| # | Artifact | Where in contracts.py | SPEC Reference |
|---|----------|----------------------|----------------|
| 1 | `chunk_index` in `excerpt_id` format | ExcerptRecord.excerpt_id docstring | §7.1 line 1397 |
| 2 | `chunk_index` derivation (0 unsplit, split_info.chunk_index split) | ExcerptRecord.chunk_index field description | §2.2.2 line 395 |
| 3 | `PageRange` type definition | New model class | §2.2.2 line 410 |
| 4 | `layer_split_points` on AssemblyMetadata | AssemblyMetadata.layer_split_points field | §2.3.2 line 165 |
| 5 | `footnote_renumber_map` on AssemblyMetadata | AssemblyMetadata.footnote_renumber_map field | §2.3.2 line 166 |
| 6 | `school_confidence` on UnitEnrichment | UnitEnrichment.school_confidence field | §7.2.4 line 1687 |
| 7 | `confidence` on VerificationItem | VerificationItem.confidence field | §7.3.2 line 1814 |
| 8 | `decontextualization_risk` review flag | ExcerptRecord.review_flags docstring | §2.2.2 line 489 |
| 9 | `verification_skipped` review flag | ExcerptRecord.review_flags docstring | §2.2.2 line 489 |
| 10 | `EX-A-012` error code | ExcerptingErrorCodes.EX_A_012 | §8.1 line 1939 |
| 11 | F-DET-2 substring extraction note | ExcerptRecord.primary_text docstring | §7.1 lines 1412–1414 |
| 12 | F-DET-9 ScholarAttribution `source` field | ScholarAttribution.source field | §7.1 line 1507 |

## After This

After CC pushes the contracts.py rewrite:
1. **Architect reviews** via `kr-reviewing-cc-output` (1 session)
2. **Step 3c: Build prep** — technology survey, architecture stubs, test skeleton, CLAUDE.md update
3. **Build phase** — implementation sessions (Phase 1 → Phase 2 → Phase 3 → integration)

## Commit Message

```
rewrite excerpting contracts.py: all types from SPEC §2.2/§2.3/§5/§7/§8

Delete old 7-engine-era contracts.py (557 lines) and rewrite from scratch.
New contracts define the 5-engine architecture data model:

- 2 enums (ScholarlyFunction 16 values, SelfContainmentLevel 3 values)
- 12 sub-types (PageRange, AuthorAttribution, ScholarAttribution, etc.)
- 4 main types (AssembledChunk 16 fields, ClassifiedSegment 6 fields,
  TeachingUnit 10 fields, ExcerptRecord 33 fields)
- 7 LLM response schemas (ClassificationResult, ExtractionResult,
  EnrichmentResult, UnitEnrichment, ResolvedScholar, VerificationResult,
  VerificationItem)
- 28 error codes (EX-A/C/M/V/G)
- Invariant validators for 29 invariants (I-AC/CS/TU/ER)
- 18 static configuration parameters
- 4 test factory helpers in conftest.py
```

## Skills to Invoke

For next steps after this CC task:
- For architect review: `kr-reviewing-cc-output` + `critical-review`
- For build prep: `kr-build-prep` + `kr-research` + `thinking-frameworks`

## Session History

- Session 0: SPEC_OUTLINE.md evaluation
- Session 1–4: Write all 12 SPEC sections (2387 lines)
- Session 5: kr-integrity audit (11 HIGH, 15 MEDIUM, 2 LOW — all fixed)
- Session 6: Deep review (1 HIGH, 3 MEDIUM — all fixed) + SPEC cleanup
- **Session 7 (this): contracts.py rewrite handoff**

## Progress Tracker

- [x] Step 0: Evaluate SPEC_OUTLINE.md
- [x] Step 1: Write SPEC_OUTLINE.md
- [x] Step 2: Write all 12 SPEC sections + coherence review
- [x] Step 2 bonus: Update CLAUDE.md
- [x] Step 3a: kr-integrity audit (28 error codes after fix)
- [ ] **Step 3b: Rewrite contracts.py (CC task — THIS HANDOFF)**
- [ ] Step 3c: Build prep (architecture stubs, test skeleton)
- [ ] Step 4+: Build (Phase 1 → Phase 2 → Phase 3 → integration)
