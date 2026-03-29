# Contract Chain Verification Report

**Date:** 2026-03-28
**Scope:** Full field-by-field trace across all 5 engine contracts
**Pipeline:** Source -> Normalization -> (Passaging) -> Excerpting -> Taxonomy -> Synthesis

Note: The passaging engine exists in contracts but was architecturally absorbed into the excerpting engine. The excerpting engine imports directly from normalization contracts, bypassing passaging. This report traces the ACTUAL data flow: Source -> Normalization -> Excerpting -> Taxonomy -> Synthesis.

---

## 1. Boundary: Source -> Normalization

### Source Engine Output: `SourceMetadata`

The source engine's primary output is `SourceMetadata` (written to `library/sources/{source_id}/metadata.json`). Key fields consumed by normalization:

| # | Field | Type | Consumed by Normalization? |
|---|-------|------|---------------------------|
| 1 | `source_id` | str | YES - becomes `NormalizedManifest.source_id` |
| 2 | `work_id` | str | NO - not in normalization contracts |
| 3 | `human_label` | str | NO - not in normalization contracts |
| 4 | `title_arabic` | str | NO - not in normalization contracts |
| 5 | `title_transliterated` | Optional[str] | NO |
| 6 | `author` | ScholarReference | NO - not directly; layer_map uses `author_canonical_id` |
| 7 | `attribution_status` | AttributionStatus | NO |
| 8 | `attribution_notes` | Optional[str] | NO |
| 9 | `muhaqiq` | Optional[ScholarReference] | NO - not directly |
| 10 | `additional_authors` | list[ScholarReference] | NO |
| 11 | `science_scope` | list[str] | NO |
| 12 | `genre` | Genre | YES - used for processing decisions |
| 13 | `genre_chain` | Optional[GenreChain] | NO |
| 14 | `level` | Optional[WorkLevel] | NO |
| 15 | `publisher` | Optional[str] | NO |
| 16 | `edition_number` | Optional[int] | NO |
| 17 | `publication_year_hijri` | Optional[int] | NO |
| 18 | `publication_year_miladi` | Optional[int] | NO |
| 19 | `source_format` | SourceFormat | YES - dispatches to correct normalizer |
| 20 | `authority_level` | AuthorityLevel | NO |
| 21 | `structural_format` | StructuralFormat | YES - becomes `NormalizedManifest.structural_format` |
| 22 | `language` | str | NO |
| 23 | `page_count` | Optional[int] | YES - used for validation |
| 24 | `is_multi_layer` | bool | YES - triggers layer detection |
| 25 | `text_layers` | list[TextLayer] | YES - seeds layer detection |
| 26 | `trust_tier` | TrustTier | NO |
| 27 | `trust_score` | float | NO |
| 28 | `trust_factors` | list[TrustworthinessFactor] | NO |
| 29 | `trust_reason` | str | NO |
| 30 | `text_fidelity` | TextFidelity (enum) | YES - baseline for per-page fidelity |
| 31 | `text_fidelity_reason` | str | NO |
| 32 | `confidence_scores` | InferredFieldConfidence | NO |
| 33 | `needs_review_fields` | list[str] | NO |
| 34 | `volume_count` | Optional[int] | YES - multi-volume handling |
| 35 | `volumes` | list[VolumeInfo] | YES - volume file mapping |
| 36 | `volumes_missing` | list[int] | NO |
| 37 | `frozen_path` | str | YES - reads frozen source files |
| 38 | `frozen_hash` | str | NO |
| 39 | `frozen_file_hashes` | dict[str, str] | NO |
| 40 | `format_specific_metadata` | dict[str, Any] | YES - Shamela-specific fields |
| 41 | `scholarly_context` | Optional[ScholarlyContext] | NO |
| 42 | `work_relationships` | list[GenreChain] | NO |
| 43 | `status` | ProcessingStatus | NO |
| 44 | `intake_timestamp` | str | NO |
| 45 | `acquisition_path` | AcquisitionPath | NO |
| 46 | `metadata_history` | list[MetadataHistoryEntry] | NO |
| 47 | `enrichment_sources` | list[str] | NO |
| 48 | `enrichment_tracking` | Optional[dict] | NO |
| 49 | `owner_authored_type` | Optional[OwnerAuthoredType] | NO |
| 50 | `compositional_profile` | Optional[CompositionalProfile] | NO |
| 51 | `difficulty_prediction` | Optional[DifficultyPrediction] | NO |
| 52 | `tahqiq_fingerprint` | Optional[TahqiqFingerprint] | NO |

### Issues at Source -> Normalization Boundary

**ISSUE S-N-1: TYPE MISMATCH on `TextFidelity`**
- Source engine: `TextFidelity` is a 4-value enum: `high`, `medium`, `low`, `unknown`
- Normalization engine: `TextFidelityLevel` is a 5-value enum: `high`, `medium`, `low`, `very_low`, `unknown`
- **Severity: MEDIUM.** Normalization adds `very_low` which source never produces. This is intentional (per-page fidelity is finer-grained than source-level), but the type names differ (`TextFidelity` vs `TextFidelityLevel`), which could cause confusion.

**ISSUE S-N-2: TYPE MISMATCH on `StructuralFormat`**
- Source engine: `StructuralFormat` enum with 7 values: prose, verse, qa_format, tabular_khilaf, dictionary, commentary, mixed
- Normalization engine: `StructuralFormat` enum with identical 7 values
- **Severity: NONE.** Values match perfectly. However, both engines define the enum independently rather than sharing. Risk of drift.

**ISSUE S-N-3: TYPE MISMATCH on `TextLayer.layer_type`**
- Source engine: `TextLayer.layer_type` is `Literal["matn", "sharh", "hashiyah", "tahqiq_note"]` (4 values)
- Normalization engine: `LayerType` is an enum with 5 values including `uncertain`
- **Severity: LOW.** Normalization adds `uncertain` for cases where layer detection cannot determine the layer. Source never produces `uncertain`. This is by design.

**ISSUE S-N-4: NAME MISMATCH on author ID field**
- Source engine: `TextLayer.author` is a `ScholarReference` containing `canonical_id`, `name_arabic`, `confidence`, `source_of_identification`
- Normalization engine: `LayerMapEntry.author_canonical_id` is `Optional[str]` (just the ID), plus separate `author_name_arabic: Optional[str]` and `confidence: float`
- **Severity: MEDIUM.** The normalization engine destructures the `ScholarReference` into flat fields, losing `source_of_identification`. D-023 concern: the provenance of the author identification is dropped at this boundary.

**ISSUE S-N-5: DEAD DATA — many Source fields not consumed by Normalization**
- 30+ fields from SourceMetadata are not consumed by the normalization engine (work_id, title, publisher, trust fields, confidence scores, etc.)
- **Severity: LOW.** This is by design per D-023 -- metadata is passed through by reference (via `source_id`), not by value. All downstream engines can look up `metadata.json` by `source_id`. Not a true D-023 violation.

---

## 2. Boundary: Normalization -> Excerpting

### Normalization Output: `NormalizedPackage` = `NormalizedManifest` + `list[ContentUnit]`

The excerpting engine directly imports types from normalization contracts:
```python
from engines.normalization.contracts import (
    BoundaryContinuityType, ContentFlags, Footnote,
    PhysicalPage, StructuralFormat, TextLayerSegment,
)
```

### NormalizedManifest fields consumed by Excerpting

| # | Field | Type | Consumed? |
|---|-------|------|-----------|
| 1 | `schema_version` | str | NO |
| 2 | `source_id` | str | YES - flows to AssembledChunk.source_id |
| 3 | `normalizer_id` | str | NO |
| 4 | `normalization_utc` | str | NO |
| 5 | `division_tree` | list[DivisionNode] | YES - CRITICAL: drives Phase 1 chunk assembly |
| 6 | `layer_map` | list[LayerMapEntry] | YES - used for author attribution (LA-1/2/3/4) |
| 7 | `structural_format` | StructuralFormat | YES - flows to AssembledChunk.structural_format |
| 8 | `structural_format_proposed` | Optional[StructuralFormat] | NO |
| 9 | `text_fidelity_summary` | TextFidelitySummary | NO |
| 10 | `verse_detection` | bool | NO |
| 11 | `verse_numbering_scheme` | Optional[str] | NO |
| 12 | `total_content_units` | int | YES - validation |
| 13 | `quality_report` | QualityReport | NO |
| 14 | `normalization_warnings` | list[str] | NO |
| 15 | `content_census` | Optional[ContentCensus] | NO (deferred in normalization) |
| 16 | `tahqiq_topology` | Optional[TahqiqTopology] | NO (deferred in normalization) |
| 17 | `layer_fingerprints` | Optional[dict[str, LayerFingerprint]] | NO (deferred in normalization) |
| 18 | `discourse_flow_summary` | Optional[dict] | NO (deferred in normalization) |

### ContentUnit fields consumed by Excerpting

| # | Field | Type | Consumed? |
|---|-------|------|-----------|
| 1 | `schema_version` | str | NO |
| 2 | `source_id` | str | YES (implicit) |
| 3 | `unit_index` | int | YES - page ordering, assembly_metadata.constituent_unit_indices |
| 4 | `physical_page` | PhysicalPage | YES - flows to AssembledChunk.physical_pages |
| 5 | `primary_text` | str | YES - CRITICAL: assembled into AssembledChunk.assembled_text |
| 6 | `text_layers` | list[TextLayerSegment] | YES - rebased in AssembledChunk.text_layers |
| 7 | `footnotes` | list[Footnote] | YES - aggregated into AssembledChunk.footnotes |
| 8 | `structural_markers` | StructuralMarkers | YES - heading detection for division tree |
| 9 | `verse_info` | Optional[VerseInfo] | NO |
| 10 | `content_flags` | ContentFlags | YES - OR-aggregated into AssembledChunk.content_flags |
| 11 | `text_fidelity` | TextFidelity | NO - not consumed by excerpting |
| 12 | `boundary_continuity` | Optional[BoundaryContinuity] | YES - drives page joining in assembly |
| 13 | `discourse_flow` | Optional[DiscourseFlow] | NO (deferred in normalization) |

### Excerpting Output: `ExcerptRecord` (33 fields)

| # | Field | Type | Origin |
|---|-------|------|--------|
| 1 | `excerpt_id` | str | Generated: exc_{source_id}_{div_id}_{chunk}_{unit} |
| 2 | `source_id` | str | From NormalizedPackage via AssembledChunk |
| 3 | `div_id` | str | From DivisionNode |
| 4 | `chunk_index` | int | Phase 1 split tracking |
| 5 | `unit_index` | int | Phase 2b TeachingUnit index |
| 6 | `div_path` | list[str] | From division tree hierarchy |
| 7 | `primary_text` | str | Substring of AssembledChunk.assembled_text |
| 8 | `text_snippet` | str | First 80 chars of primary_text |
| 9 | `start_word` | int | Phase 2b word offsets |
| 10 | `end_word` | int | Phase 2b word offsets |
| 11 | `segment_indices` | list[int] | Phase 2a segment assignment |
| 12 | `physical_pages` | Optional[PageRange] | From PhysicalPage via compute_page_range |
| 13 | `primary_function` | ScholarlyFunction | Phase 2a LLM classification |
| 14 | `secondary_functions` | list[ScholarlyFunction] | Phase 2a LLM classification |
| 15 | `content_types` | list[ScholarlyFunction] | Deduplicated from all segments |
| 16 | `description_arabic` | str | Phase 2b LLM grouping |
| 17 | `self_containment` | SelfContainmentLevel | Phase 2b LLM assessment |
| 18 | `self_containment_notes` | Optional[str] | Phase 2b when PARTIAL/DEPENDENT |
| 19 | `context_hint` | Optional[str] | Phase 3 LLM enrichment |
| 20 | `primary_author_layer` | AuthorAttribution | Phase 3 deterministic F-DET-9 |
| 21 | `attribution_confidence` | Optional[float] | Phase 3 consensus (LA-3) |
| 22 | `quoted_scholars` | list[ScholarAttribution] | Phase 3 LLM enrichment |
| 23 | `school` | Optional[str] | Phase 3 LLM enrichment |
| 24 | `school_confidence` | Optional[float] | Phase 3 consensus verification |
| 25 | `excerpt_topic` | list[str] | Phase 3 LLM enrichment |
| 26 | `terminology_variants` | list[TermVariant] | Phase 3 LLM enrichment |
| 27 | `evidence_refs` | list[EvidenceRef] | Phase 3 deterministic F-DET-5 |
| 28 | `takhrij_data` | Optional[list[TakhrijEntry]] | Phase 3 LLM enrichment |
| 29 | `cross_references` | list[CrossReference] | Phase 3 LLM enrichment |
| 30 | `footnotes_relevant` | list[Footnote] | Phase 3 deterministic F-DET-8 |
| 31 | `consensus_metadata` | Optional[ConsensusRecord] | Phase 3 consensus |
| 32 | `gate_flags` | list[str] | Phase 3 human gate triggers |
| 33 | `review_flags` | list[str] | Phase 3 operational flags |

### Issues at Normalization -> Excerpting Boundary

**ISSUE N-E-1: DEAD DATA — `verse_info` not consumed**
- ContentUnit.verse_info (Optional[VerseInfo]) is produced by normalization but never consumed by excerpting.
- **Severity: LOW.** Verse info may be needed by later engines or for display. Not a data loss since it is in the normalized package on disk.

**ISSUE N-E-2: DEAD DATA — `text_fidelity` per-page not consumed**
- ContentUnit.text_fidelity (TextFidelity model with score, ocr_confidence, warnings) is produced but not consumed by excerpting.
- **Severity: LOW.** Could be useful for quality-aware excerpting (skipping low-fidelity pages) but is not currently used.

**ISSUE N-E-3: DEAD DATA — `discourse_flow` not consumed**
- ContentUnit.discourse_flow is always None (deferred in normalization) and not consumed by excerpting.
- **Severity: NONE.** Both sides agree it is deferred.

**ISSUE N-E-4: Shared type imports are correct**
- Excerpting imports `BoundaryContinuityType`, `ContentFlags`, `Footnote`, `PhysicalPage`, `StructuralFormat`, `TextLayerSegment` directly from normalization contracts. This is the correct D-023 pattern -- no re-definition, no drift risk.
- **Severity: NONE.** This is a positive finding.

**ISSUE N-E-5: POTENTIAL ISSUE — `StructuralFormat` enum redefined in passaging**
- Passaging engine defines `PassageStructuralFormat` with different values (e.g., `qa_pair` instead of `qa_format`, `tabular_masala` instead of `tabular_khilaf`). Since passaging was absorbed into excerpting and excerpting imports from normalization, this is currently inert. But if passaging is ever activated, there will be a type mismatch.
- **Severity: LOW.** Dormant risk.

---

## 3. Boundary: Excerpting -> Taxonomy

### Excerpting Output: `ExcerptRecord` (see above, 33 fields)

### Taxonomy Input Contract (from `contracts.py` section 2)

The taxonomy engine's input contract is NOT explicitly modeled as a Pydantic class in its contracts.py. Instead, the taxonomy SPEC (section 2) defines what it expects from the excerpt stream. The taxonomy contracts.py defines:

- `HumanGateDecisionRecord` (section 2.2 - owner feedback)
- `ExcerptRelocationRequest` (section 2.2, Scenario 8)

**CRITICAL FINDING:** There is NO formal input Pydantic model in taxonomy contracts.py that explicitly maps to ExcerptRecord. The taxonomy engine is expected to consume ExcerptRecord objects directly from the excerpting engine, but this is not formalized in the taxonomy contracts.

### Fields from ExcerptRecord consumed by Taxonomy

Based on taxonomy contracts.py output models and SPEC references:

| ExcerptRecord Field | Used by Taxonomy? | How? |
|---------------------|-------------------|------|
| `excerpt_id` | YES | Primary key in PlacedExcerptAdditions, LeafCoverage |
| `source_id` | YES | Source diversity analysis in LeafCoverage |
| `div_id` | UNKNOWN | Not referenced in taxonomy contracts |
| `chunk_index` | UNKNOWN | Not referenced |
| `unit_index` | UNKNOWN | Not referenced |
| `div_path` | YES | Structural context for placement |
| `primary_text` | YES | Text content for LLM placement analysis |
| `text_snippet` | UNKNOWN | Not referenced |
| `start_word` / `end_word` | NO | Word offsets not meaningful outside chunk context |
| `segment_indices` | NO | Internal excerpting bookkeeping |
| `physical_pages` | POSSIBLE | Citation generation in synthesis needs pages |
| `primary_function` | YES | Content type analysis |
| `secondary_functions` | YES | Content type analysis |
| `content_types` | YES | Maps to LeafCoverage.content_type_distribution |
| `description_arabic` | YES | LLM placement context |
| `self_containment` | YES | Maps to VerifiedFlaggedStatus |
| `self_containment_notes` | POSSIBLE | |
| `context_hint` | POSSIBLE | |
| `primary_author_layer` | YES | Author diversity in LeafCoverage |
| `attribution_confidence` | POSSIBLE | Quality signal |
| `quoted_scholars` | YES | Scholarly landscape reconstruction |
| `school` | YES | School coverage in LeafCoverage.school_coverage |
| `school_confidence` | POSSIBLE | Quality weighting |
| `excerpt_topic` | YES | CRITICAL for placement matching |
| `terminology_variants` | YES | TerminologySynonym in tree structure |
| `evidence_refs` | YES | Evidence type coverage in LeafCoverage |
| `takhrij_data` | POSSIBLE | Evidence detail |
| `cross_references` | POSSIBLE | Cross-science link detection |
| `footnotes_relevant` | NO | Not referenced in taxonomy |
| `consensus_metadata` | POSSIBLE | Quality signal |
| `gate_flags` | YES | Determines VerifiedFlaggedStatus |
| `review_flags` | POSSIBLE | Quality signal |

### Issues at Excerpting -> Taxonomy Boundary

**ISSUE E-T-1: MISSING DATA — no formal input model**
- Taxonomy contracts.py does not define an explicit input model that maps to ExcerptRecord. The contract is implicit -- taxonomy code will import and consume ExcerptRecord from excerpting contracts.
- **Severity: MEDIUM.** While this works, it creates a tight coupling. If excerpting changes ExcerptRecord fields, taxonomy has no schema-level guard. The normalization boundary is cleaner (NormalizedPackage is self-contained).

**ISSUE E-T-2: NAME MISMATCH — `school` field semantics**
- ExcerptRecord.school: `Optional[str]` -- the school attribution for this excerpt
- Taxonomy LeafCoverage.school_coverage: `dict[str, int]` -- school name -> count
- Taxonomy DisagreementPosition.schools: `list[str]`
- SchoolPositioningSummary.school: `str`
- **Severity: LOW.** The field names differ but this is expected -- taxonomy aggregates over excerpts. However, there is no shared enum or validation for school names. A typo in excerpting's school field would propagate silently.

**ISSUE E-T-3: NAME MISMATCH — `primary_author_layer.author_id` vs taxonomy's scholar references**
- ExcerptRecord: `primary_author_layer.author_id` (str, e.g., "sch_00042")
- Taxonomy ScholarNode: `scholar_id` (Optional[str])
- **Severity: LOW.** The field names differ (`author_id` vs `scholar_id`) but both reference the same `sch_XXXXX` format. Manageable but worth documenting.

**ISSUE E-T-4: DEAD DATA at this boundary**
- `segment_indices`, `start_word`, `end_word` -- internal excerpting positions meaningless to taxonomy
- `footnotes_relevant` -- not consumed by taxonomy
- **Severity: LOW.** These are carried as pass-through metadata per D-023. Not truly dead -- they flow to synthesis.

**ISSUE E-T-5: TYPE MISMATCH — TermVariant definitions**
- Excerpting: `TermVariant(term: str, variants: list[str])`
- Taxonomy: `TermVariant(term: str, context: str)` and `TerminologySynonym(canonical_term: str, variants: list[TermVariant])`
- **Severity: HIGH.** The TermVariant model is DEFINED DIFFERENTLY in excerpting vs taxonomy contracts. Excerpting's TermVariant has `variants: list[str]`. Taxonomy's TermVariant has `context: str` (singular) with no variants list. These are incompatible types with the same name.

**ISSUE E-T-6: MISSING DATA — death date for temporal analysis**
- Taxonomy's TemporalSpan needs `earliest_author_death` and `latest_author_death` (Hijri year int).
- ExcerptRecord does NOT carry author death dates. This data must come from the ScholarAuthorityRecord via `primary_author_layer.author_id` lookup.
- **Severity: MEDIUM.** Not a contract mismatch per se, but a dependency on the scholar registry that is not documented in the taxonomy input contract.

---

## 4. Boundary: Taxonomy -> Synthesis

### Taxonomy Output Models

The taxonomy engine produces:
1. `PlacedExcerptAdditions` -- fields added to excerpts at placement time
2. `TreeNode` hierarchy -- the science tree structure
3. `LeafCoverage` -- per-leaf analytics
4. `EvolutionProposal` -- tree changes
5. `DisagreementTopology` -- scholarly disagreement analysis
6. `ScholarlyLandscape` -- per-leaf scholarly timeline
7. `SourceEvolutionPredictions` -- proactive evolution

### Synthesis Input Contract (from `contracts.py` section 2)

The synthesis engine defines explicit input models:
- `StalenessSignal` -- notification of stale entries
- `RegenerationRequest` -- request to regenerate
- `OwnerCorrection` -- owner-identified errors

### Fields flowing from Taxonomy to Synthesis

| Taxonomy Output | Consumed by Synthesis? | How? |
|-----------------|----------------------|------|
| `PlacedExcerptAdditions.confirmed_leaf` | YES | Entry is generated per leaf_path |
| `PlacedExcerptAdditions.placement_confidence` | YES | Quality signal |
| `PlacedExcerptAdditions.placed_utc` | NO | Administrative |
| `PlacedExcerptAdditions.review_metadata` | POSSIBLE | Quality signal |
| `PlacedExcerptAdditions.verified_flagged_status` | YES | Separates verified vs flagged excerpts |
| `PlacedExcerptAdditions.taxonomy_version_at_placement` | YES | Entry.taxonomy_version |
| `PlacedExcerptAdditions.placement_reasoning` | NO | Diagnostic |
| `PlacedExcerptAdditions.proposed_leaf_override` | NO | Diagnostic |
| `PlacedExcerptAdditions.proposed_leaf_original` | NO | Diagnostic |
| `PlacedExcerptAdditions.override_reason` | NO | Diagnostic |
| TreeNode hierarchy | YES | Entry organization, prerequisite links |
| LeafCoverage.school_coverage | YES | School balance in entries |
| LeafCoverage.temporal_span | YES | Temporal ordering of positions |
| LeafCoverage.gaps | YES | GapNote generation |
| DisagreementTopology | YES | Scholarly analysis, consensus mapping |
| ScholarlyLandscape | YES | Influence graph, discourse transitions |

### Issues at Taxonomy -> Synthesis Boundary

**ISSUE T-S-1: MISSING DATA — no formal excerpt input model in synthesis**
- Like taxonomy, synthesis does not define a formal Pydantic model for its excerpt input. It consumes a "placed excerpt" which is ExcerptRecord + PlacedExcerptAdditions, but this combined type is not modeled.
- **Severity: MEDIUM.** Same concern as E-T-1 -- implicit contract.

**ISSUE T-S-2: NAME MISMATCH — `school` field across engines**
- ExcerptRecord.school: `Optional[str]`
- Taxonomy LeafCoverage.school_coverage: `dict[str, int]`
- Synthesis ScholarlyPositionEntry.mu_tamad_in_school: `Optional[str]`
- Synthesis ScholarlyAnalysis.school_ratio: `dict[str, int]`
- **Severity: LOW.** All use raw strings for school names with no shared enum. Risk of inconsistent naming.

**ISSUE T-S-3: TYPE MISMATCH — `GapType` enum defined in both taxonomy and synthesis**
- Taxonomy: `GapType` with values: school, source_diversity, temporal, evidence, prerequisite, empty
- Synthesis: `GapType` with values: school, temporal, source_diversity
- **Severity: HIGH.** Synthesis defines a SUBSET of taxonomy's GapType values. If taxonomy passes a gap with type `evidence`, `prerequisite`, or `empty` to synthesis, synthesis cannot represent it. This is a contract incompatibility.

**ISSUE T-S-4: NAME MISMATCH — `PositionHolder` vs taxonomy's scholar models**
- Synthesis: `PositionHolder(scholar_id, name, death_hijri, school)`
- Taxonomy: `ScholarNode(scholar_id, name, death_date_hijri, school)`
- **Severity: LOW.** The field `death_hijri` (synthesis) vs `death_date_hijri` (taxonomy) is a name mismatch for the same concept. Could cause bugs in data transfer.

**ISSUE T-S-5: POTENTIAL D-023 VIOLATION -- excerpt metadata passthrough**
- Synthesis Entry.source_excerpt_ids is `list[str]` -- only excerpt IDs, not full excerpt data.
- Synthesis must look up full excerpt data by ID. If any upstream field from excerpting was not persisted, it is lost.
- **Severity: LOW.** This is by-reference passing, which is the D-023 pattern used throughout.

**ISSUE T-S-6: DEAD DATA — taxonomy diagnostic fields**
- PlacedExcerptAdditions: `placement_reasoning`, `proposed_leaf_override`, `proposed_leaf_original`, `override_reason` -- not consumed by synthesis.
- **Severity: NONE.** Diagnostic data preserved per D-023 but not actively used downstream. This is correct behavior.

---

## 5. Summary of All Issues (Sorted by Severity)

### HIGH Severity (2 issues)

| ID | Boundary | Type | Description |
|----|----------|------|-------------|
| E-T-5 | Excerpting->Taxonomy | TYPE MISMATCH | `TermVariant` model defined differently: excerpting has `variants: list[str]`, taxonomy has `context: str`. Incompatible types with the same name. |
| T-S-3 | Taxonomy->Synthesis | TYPE MISMATCH | `GapType` enum: taxonomy has 6 values, synthesis has only 3. Synthesis cannot represent taxonomy's `evidence`, `prerequisite`, or `empty` gaps. |

### MEDIUM Severity (5 issues)

| ID | Boundary | Type | Description |
|----|----------|------|-------------|
| S-N-1 | Source->Normalization | TYPE MISMATCH | `TextFidelity` (4 values) vs `TextFidelityLevel` (5 values, adds `very_low`). Different type names for related concept. |
| S-N-4 | Source->Normalization | NAME MISMATCH | Source's `ScholarReference` destructured to flat fields in normalization's `LayerMapEntry`, losing `source_of_identification`. |
| E-T-1 | Excerpting->Taxonomy | MISSING DATA | No formal input Pydantic model in taxonomy for excerpt consumption. |
| E-T-6 | Excerpting->Taxonomy | MISSING DATA | Author death dates needed for temporal analysis not on ExcerptRecord; requires registry lookup. |
| T-S-1 | Taxonomy->Synthesis | MISSING DATA | No formal "placed excerpt" Pydantic model combining ExcerptRecord + PlacedExcerptAdditions. |

### LOW Severity (10 issues)

| ID | Boundary | Type | Description |
|----|----------|------|-------------|
| S-N-2 | Source->Normalization | DRIFT RISK | `StructuralFormat` defined independently in both engines. Values match now but could drift. |
| S-N-3 | Source->Normalization | TYPE MISMATCH | Source `TextLayer.layer_type` is Literal (4 values) vs normalization `LayerType` enum (5 values, adds `uncertain`). |
| S-N-5 | Source->Normalization | DEAD DATA | 30+ SourceMetadata fields not consumed by normalization. By design (reference via source_id). |
| N-E-1 | Norm->Excerpting | DEAD DATA | `verse_info` produced but not consumed. |
| N-E-2 | Norm->Excerpting | DEAD DATA | Per-page `text_fidelity` not consumed by excerpting. |
| N-E-5 | Norm->Excerpting | DRIFT RISK | Passaging's `PassageStructuralFormat` differs from normalization's `StructuralFormat`. Dormant. |
| E-T-2 | Excerpting->Taxonomy | NAME MISMATCH | No shared enum for school names. |
| E-T-3 | Excerpting->Taxonomy | NAME MISMATCH | `author_id` vs `scholar_id` for same concept. |
| E-T-4 | Excerpting->Taxonomy | DEAD DATA | `segment_indices`, `start_word`, `end_word` not consumed by taxonomy. |
| T-S-4 | Taxonomy->Synthesis | NAME MISMATCH | `death_hijri` vs `death_date_hijri` for same concept. |

### NONE Severity (4 issues -- positive findings or design-correct)

| ID | Boundary | Type | Description |
|----|----------|------|-------------|
| N-E-3 | Norm->Excerpting | ALIGNED | Both sides agree `discourse_flow` is deferred. |
| N-E-4 | Norm->Excerpting | POSITIVE | Excerpting imports types directly from normalization. Zero drift risk. |
| T-S-5 | Taxonomy->Synthesis | BY DESIGN | Reference-based passthrough via excerpt IDs. |
| T-S-6 | Taxonomy->Synthesis | BY DESIGN | Diagnostic fields preserved but not consumed. |

---

## 6. Metadata Pass-Through Trace (5 Fields)

### Trace 1: `source_id`

```
Source Engine:   SourceMetadata.source_id (str, "src_{hash}")
     |
Normalization:   NormalizedManifest.source_id (str) -- COPIED
                 ContentUnit.source_id (str) -- COPIED
     |
Excerpting:      AssembledChunk.source_id (str) -- COPIED
                 ExcerptRecord.source_id (str) -- COPIED
     |
Taxonomy:        PlacedExcerptAdditions has no source_id -- PASS-THROUGH via excerpt reference
     |
Synthesis:       Entry does not have source_id -- accessed via source_excerpt_ids -> ExcerptRecord.source_id
```

**Verdict: PASS.** source_id flows through every engine. Taxonomy and synthesis access it by reference.

### Trace 2: `author` (primary author identity)

```
Source Engine:   SourceMetadata.author = ScholarReference(canonical_id, name_arabic, confidence, source_of_identification)
     |
Normalization:   NormalizedManifest.layer_map[0].author_canonical_id (str, just the ID)
                 NormalizedManifest.layer_map[0].author_name_arabic (str)
                 ** source_of_identification DROPPED **
     |
Excerpting:      ExcerptRecord.primary_author_layer = AuthorAttribution(layer_id, author_id, coverage_pct, rule_applied)
                 ** author_name_arabic DROPPED from direct access -- must look up via author_id **
     |
Taxonomy:        Consumed via ExcerptRecord.primary_author_layer.author_id
                 ScholarNode.scholar_id in landscape
     |
Synthesis:       Entry.citations[].author_name (str) -- looked up from registry
                 PositionHolder.scholar_id (Optional[str])
```

**Verdict: WARNING.** The author identity flows through, but:
- `source_of_identification` is dropped at normalization boundary (D-023 concern)
- Author NAME requires registry lookup after excerpting (not on ExcerptRecord directly)
- Each engine uses different field names: `canonical_id` -> `author_canonical_id` -> `author_id` -> `scholar_id`

### Trace 3: `structural_format`

```
Source Engine:   SourceMetadata.structural_format = StructuralFormat (7-value enum)
     |
Normalization:   NormalizedManifest.structural_format = StructuralFormat (same 7 values, separate definition)
     |
Excerpting:      AssembledChunk.structural_format = StructuralFormat (imported from normalization)
                 ** Not on ExcerptRecord -- lost after Phase 1 **
     |
Taxonomy:        NOT consumed (not on ExcerptRecord)
     |
Synthesis:       NOT consumed
```

**Verdict: D-023 VIOLATION.** `structural_format` is present on AssembledChunk but NOT on ExcerptRecord. It is dropped at the Phase 1 -> Phase 3 transition within excerpting. Taxonomy and synthesis cannot access it without going back to the normalized manifest. This matters for commentary-format texts where synthesis needs to know the structural format for appropriate rendering.

### Trace 4: `school` (madhab attribution)

```
Source Engine:   Not on SourceMetadata (school is per-excerpt, not per-source)
     |
Normalization:   Not applicable
     |
Excerpting:      ExcerptRecord.school = Optional[str] (LLM-inferred per excerpt)
                 ExcerptRecord.school_confidence = Optional[float]
     |
Taxonomy:        LeafCoverage.school_coverage = dict[str, int] (aggregated)
                 DisagreementPosition.schools = list[str]
                 SchoolPositioningSummary.school = str
     |
Synthesis:       ScholarlyPositionEntry.mu_tamad_in_school = Optional[str]
                 ScholarlyAnalysis.school_ratio = dict[str, int]
```

**Verdict: PASS with caveat.** School flows through, but there is no shared enum or vocabulary control for school names. A school spelled differently in excerpting vs taxonomy would not be caught.

### Trace 5: `text_layers` (multi-layer attribution)

```
Source Engine:   SourceMetadata.text_layers = list[TextLayer(layer_type: Literal[4], author: ScholarReference)]
     |
Normalization:   NormalizedManifest.layer_map = list[LayerMapEntry(layer_type: LayerType[5], author_canonical_id, ...)]
                 ContentUnit.text_layers = list[TextLayerSegment(layer_type, author_canonical_id, start, end, confidence)]
     |
Excerpting:      AssembledChunk.text_layers = list[TextLayerSegment] (rebased offsets)
                 ExcerptRecord.primary_author_layer = AuthorAttribution(layer_id, author_id, coverage_pct, rule_applied)
                 ** Full text_layers NOT on ExcerptRecord -- only dominant layer **
     |
Taxonomy:        NOT consumed (text_layers detail not available)
     |
Synthesis:       NOT consumed
```

**Verdict: D-023 CONCERN.** Full text layer segments are reduced to a single `primary_author_layer` on ExcerptRecord. For multi-layer texts, the layer attribution detail (which characters belong to which author) is lost after excerpting. This may be intentional (the excerpt is attributed to the dominant author), but downstream engines cannot reconstruct per-character layer boundaries.

---

## 7. Recommendations

### HIGH Priority (fix before implementation)

1. **E-T-5: TermVariant incompatibility.** Either:
   - (a) Have taxonomy import TermVariant from excerpting contracts, OR
   - (b) Define a shared TermVariant in `shared/` contracts that both engines import, OR
   - (c) Rename taxonomy's model to avoid the collision (e.g., `TerminologyMapping`).

   **Recommended:** Option (b) -- shared definition in `shared/validation/` or a new `shared/contracts.py`.

2. **T-S-3: GapType enum mismatch.** Add the missing values (`evidence`, `prerequisite`, `empty`) to synthesis's GapType enum to match taxonomy's definition. Better yet, define GapType once in a shared location.

### MEDIUM Priority (fix during engine implementation)

3. **E-T-1 / T-S-1: Missing formal input models.** Define explicit input Pydantic models for taxonomy and synthesis that document exactly which ExcerptRecord fields they consume. This catches breaking changes at the schema level rather than at runtime.

4. **S-N-4: ScholarReference flattening.** Preserve `source_of_identification` in LayerMapEntry, or document explicitly that this field is intentionally dropped at the normalization boundary with rationale.

5. **Trace 3 finding: structural_format dropped from ExcerptRecord.** Add `structural_format: StructuralFormat` to ExcerptRecord so downstream engines can access it without manifest lookup.

### LOW Priority (track for future cleanup)

6. **S-N-2: StructuralFormat duplication.** Move StructuralFormat to a shared location so source and normalization import the same definition.

7. **E-T-2 / T-S-2: School name standardization.** Define a School enum or vocabulary file that all engines reference for madhab names.

8. **T-S-4: death_hijri vs death_date_hijri.** Standardize the field name across taxonomy and synthesis.

9. **Author ID field name standardization.** The same concept uses `canonical_id`, `author_canonical_id`, `author_id`, and `scholar_id` across engines. Consider standardizing to one name (e.g., `scholar_canonical_id`).

---

## 8. Passaging Engine Status

The passaging engine contracts.py (557 lines) defines a complete `PassageRecord` with 25+ fields, but this engine was architecturally absorbed into excerpting. Key observations:

- Passaging contracts import from normalization (`FootnoteType`, `HeadingConfidence`, `LayerType`, `TextFidelityLevel`)
- Excerpting does NOT import from passaging -- it imports directly from normalization
- PassageRecord fields are partially replicated in AssembledChunk (excerpting's Phase 1 output)
- The passaging contracts serve as dead code in the current architecture

**Recommendation:** Either (a) archive passaging contracts to prevent confusion, or (b) document clearly that they are dormant, or (c) if passaging may be reactivated, add a compatibility layer between PassageRecord and AssembledChunk.

---

## 9. Positive Findings

1. **Direct type imports at Norm->Excerpting boundary.** Excerpting imports 6 types directly from normalization contracts. This is the gold standard for contract alignment -- zero drift risk.

2. **D-023 by-reference pattern.** All engines use `source_id` as the reference key back to SourceMetadata. This means downstream engines can always access the full source metadata without it being copied through every boundary.

3. **ContentUnit is well-structured.** The per-page data model carries all necessary fields (text, layers, footnotes, flags, fidelity, continuity) in a clean, typed structure.

4. **ExcerptRecord is comprehensive.** At 33 fields across 7 categories, it captures classification, attribution, evidence, and metadata. The model validators (I-ER-1 through I-ER-7) provide runtime safety.

5. **NormalizedManifest + ContentUnit separation.** Source-level metadata (manifest) is cleanly separated from page-level data (content units), making it easy for downstream engines to access the right level of detail.
