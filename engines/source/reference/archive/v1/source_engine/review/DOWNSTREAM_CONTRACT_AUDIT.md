# Downstream Contract Audit — Source Engine Output Completeness

**Audit date:** 2026-03-09
**Auditor scope:** Verify that every field consumed by downstream engines from source engine output exists in SPEC_CORE.md and contracts.py. Identify gaps, partial matches, and path errors.

**Method:** For each downstream engine, opened its SPEC and searched for every reference to source engine output (metadata.json, registries, frozen files). For each consumption point, traced the field back to `SourceMetadata`, `SourceRegistryEntry`, `WorkRegistryEntry`, or `ScholarAuthorityRecord` in contracts.py.

---

## 1. Normalization Engine (engines/normalization/SPEC.md §2)

The normalization engine has the most precisely defined input contract of all downstream engines. The source SPEC_CORE §3.3 already contains a verified field mapping table. This audit re-verifies that mapping against the current state of both SPECs and contracts.py.

### 1.1 — `source_id`

**Downstream need:** "the canonical identifier for this source. Becomes the primary key linking the normalized package to its source." (normalization SPEC §2, line 47)
**Source provides:** `SourceMetadata.source_id` — `str`, format `src_{8_char_hash}` (contracts.py line 689)
**Status: SATISFIED**

### 1.2 — `source_format`

**Downstream need:** "determines which normalizer processes this source. Values: `shamela_html`, `pdf_text`, `pdf_scanned`, `image_scan`, `epub`, `plain_text`, `owner_authored`." (normalization SPEC §2, line 48)
**Source provides:** `SourceMetadata.source_format` — `SourceFormat` enum (contracts.py lines 46–56). Values: `shamela_html`, `pdf_text`, `pdf_scanned`, `image_scan`, `plain_text`, `epub`, `word_doc`, `owner_authored`.
**Status: SATISFIED** — The normalization SPEC's inline list on line 48 omits `word_doc`, but its type map table (line 175) includes `word_doc` as a recognized format. The enum is a superset — acceptable.

### 1.3 — `work_id`

**Downstream need:** "used for output file naming and cross-referencing." (normalization SPEC §2, line 49)
**Source provides:** `SourceMetadata.work_id` — `str`, format `wrk_{author_slug}_{title_slug}` (contracts.py line 690)
**Status: SATISFIED**

### 1.4 — `text_fidelity`

**Downstream need:** "the source-level fidelity signal from the source engine. The normalization engine uses this as a baseline and may refine it to page-level granularity." (normalization SPEC §2, line 50)
**Source provides:** `SourceMetadata.text_fidelity` — `TextFidelity` enum (`high`/`medium`/`low`/`unknown`) (contracts.py lines 77–91)
**Source SPEC_CORE §3.3 note:** Source enum adds no `very_low`; normalization's page-level enum adds `very_low`. Acknowledged.
**Status: SATISFIED**

### 1.5 — `structural_format`

**Downstream need:** "the source engine's initial classification. Valid values: `prose`, `verse`, `qa_format`, `tabular_khilaf`, `dictionary`, `commentary`, `mixed`." (normalization SPEC §2, line 51)
**Source provides:** `SourceMetadata.structural_format` — `StructuralFormat` enum with exactly those 7 values (contracts.py lines 100–112)
**Status: SATISFIED**

### 1.6 — `multi_layer` / `is_multi_layer`

**Downstream need:** "`multi_layer`: boolean indicating whether this source contains text from 2 or more authors. When true, the `layers` field specifies which layers are present and who authored each." (normalization SPEC §2, line 52)
**Source provides:** `SourceMetadata.is_multi_layer` — `bool` (contracts.py line 729). `SourceMetadata.text_layers` — `list[TextLayer]` (contracts.py line 730).
**Status: SATISFIED** — The field name mismatch (`multi_layer` in normalization prose vs `is_multi_layer` in contracts.py, and `layers` in normalization prose vs `text_layers` in contracts.py) is already documented and resolved in SPEC_CORE §3.3 (line 127–128): "the normalization SPEC prose uses `multi_layer` but the actual JSON field is `is_multi_layer`" and "the normalization SPEC prose uses `layers` but the actual JSON field is `text_layers`."

### 1.7 — `genre`

**Downstream need:** "affects normalization strategy (a `nazm` triggers verse-aware processing; a `mu'jam` triggers dictionary-entry-aware processing)." (normalization SPEC §2, line 53)
**Source provides:** `SourceMetadata.genre` — `Genre` enum (contracts.py lines 115–137)
**Status: SATISFIED**

### 1.8 — `volume_count` and volume metadata

**Downstream need:** "`volume_count` and volume metadata: for multi-volume sources." (normalization SPEC §2, line 54)
**Source provides:** `SourceMetadata.volume_count` — `Optional[int]` (contracts.py line 747). `SourceMetadata.volumes` — `list[VolumeInfo]` (contracts.py line 748). Each `VolumeInfo` contains `volume_number`, `file_path`, `page_range`.
**Status: SATISFIED**

### 1.9 — Frozen source files

**Downstream need:** "Located at `library/sources/{source_id}/frozen/`. These files are immutable." (normalization SPEC §2, line 43)
**Source provides:** `SourceMetadata.frozen_path` — `str` pointing to `library/sources/{source_id}/frozen/` (contracts.py line 752). `SourceMetadata.frozen_hash` and `frozen_file_hashes` for integrity verification.
**Status: SATISFIED**

### Normalization Summary

All 9 consumption points SATISFIED. The field name mismatches are documented. No gaps.

---

## 2. Excerpting Engine (engines/excerpting/SPEC.md §2)

The excerpting engine's primary input is the atom stream from atomization, not source metadata directly. However, it accesses source metadata via `source_id` reference for enrichment during Phase 3.

### 2.1 — Source metadata via `source_id` reference (general)

**Downstream need:** "Source metadata via `source_id` reference: author biography, school affiliations, work genre, trust tier, text fidelity, work relationships. Accessed from `library/registries/sources.json` and `library/registries/scholars.json`." (excerpting SPEC §2, line 61)
**Source provides:** This statement references TWO registries. Let me trace each extracted field:

### 2.1.1 — Author biography / school affiliations

**Downstream need:** Used for implicit reference resolution (§4.A.5): "In a Shafi'i text, 'الإمام' usually means al-Shafi'i" (line 431). Used for school attribution (§4.A Phase 3): "the author's known school affiliation from source metadata" (line 256).
**Source provides:** `ScholarAuthorityRecord` in `library/registries/scholars.json` — `canonical_name_ar`, `school_affiliations`, `death_date_hijri`, `teachers`, `students`, `scholarly_standing` (contracts.py lines 555–626). Accessed via `SourceMetadata.author.canonical_id`.
**Status: SATISFIED**

### 2.1.2 — Work genre

**Downstream need:** Used during self-containment evaluation: "Given this text and the source metadata (author, work, science)" (line 230). Used in metadata enrichment Phase 3.
**Source provides:** `SourceMetadata.genre` — `Genre` enum.
**Status: PARTIAL** — The excerpting SPEC says it reads from `library/registries/sources.json`, but `SourceRegistryEntry` (contracts.py lines 652–668) does NOT contain `genre`. The `genre` field exists only in the full `SourceMetadata` (contracts.py line 713). The excerpting engine must read from `library/sources/{source_id}/metadata.json`, not from `library/registries/sources.json`.

**Severity:** Medium. This is a path error in the excerpting SPEC, not a missing field. The data exists in `metadata.json`. If the implementation follows the path literally (`sources.json`), the field lookup will fail.

### 2.1.3 — Trust tier

**Downstream need:** Referenced indirectly for verified/flagged propagation (taxonomy §4.A.4 line 208, which reads trust_tier from source; the excerpting engine itself doesn't seem to directly read trust_tier but it's listed in §2 line 61).
**Source provides:** `SourceRegistryEntry.trust_tier` — `TrustTier` enum. Also in `SourceMetadata.trust_tier`.
**Status: SATISFIED** — Trust tier IS in the source registry.

### 2.1.4 — Text fidelity

**Downstream need:** Listed in §2 line 61 as accessed metadata. Not directly referenced in excerpting processing logic, but may inform confidence calibration.
**Source provides:** `SourceMetadata.text_fidelity` — `TextFidelity` enum. NOT in `SourceRegistryEntry`.
**Status: PARTIAL** — Same path error as 2.1.2. Field exists in `metadata.json` but not in `sources.json`.

### 2.1.5 — Work relationships

**Downstream need:** "Work relationship data. If the source is a sharh, 'صاحب الكتاب' refers to the matn author (from work relationships in source metadata)." (line 432)
**Source provides:** `SourceMetadata.genre_chain` — `Optional[GenreChain]` with `base_work_title`, `base_work_author`, `base_work_id`. Also `SourceMetadata.work_relationships` — `list[GenreChain]`. Also `WorkRegistryEntry.relationships` — `list[WorkRelationshipEdge]`.
**Status: SATISFIED** — Genre chain and work relationships are in metadata.json. The excerpting engine's implicit reference resolution can access the matn author's identity via `genre_chain.base_work_author` and `genre_chain.base_work_id`.

### 2.1.6 — `science_id` / `science_scope`

**Downstream need:** "Inherited from source metadata `science_scope`." (line 110, describing the excerpt's `science_id` field)
**Source provides:** `SourceMetadata.science_scope` — `list[str]` (contracts.py line 712).
**Status: SATISFIED**

### 2.1.7 — Source school cross-validation

**Downstream need:** "If ≥30% of excerpts' `school` values disagree with the source metadata's expected school, this signals possible upstream metadata error." (line 848)
**Source provides:** The "expected school" comes from the author's `school_affiliations` in `ScholarAuthorityRecord`. The author is accessed via `SourceMetadata.author.canonical_id`.
**Status: SATISFIED** — Via the scholar authority registry chain.

### Excerpting Summary

6 consumption points SATISFIED. 2 consumption points PARTIAL (genre and text_fidelity referenced via `sources.json` registry path, but they exist only in `metadata.json`). The excerpting SPEC has a path error — it names `library/registries/sources.json` as the access point but several fields it needs (genre, text_fidelity, authority_level) exist only in the full `SourceMetadata` at `library/sources/{source_id}/metadata.json`.

---

## 3. Synthesis Engine — §4.A.1 Metadata Chain Resolution

### 3.1 — Source metadata resolution path

**Downstream need:** "Source metadata via `source_id` → `library/registries/sources.json`. Extracts: work title, genre, source authority level, trust tier, text fidelity." (synthesis SPEC §4.A.1, line 207)
**Source provides:** `SourceRegistryEntry` in `sources.json` contains: `source_id`, `work_id`, `human_label`, `title_arabic`, `author_canonical_id`, `trust_tier`, `processing_status`, `frozen_hash`, `intake_timestamp`, `acquisition_path`.

Tracing each extracted field against the source registry:

| Synthesis needs | In SourceRegistryEntry? | In SourceMetadata? |
|---|---|---|
| work title (`title_arabic`) | YES | YES |
| genre | **NO** | YES (line 713) |
| source authority level (`authority_level`) | **NO** | YES (line 723) |
| trust tier | YES | YES |
| text fidelity | **NO** | YES (line 737) |

**Status: GAP — path error with field absence.** Three of five fields the synthesis engine extracts (`genre`, `authority_level`, `text_fidelity`) do NOT exist in `SourceRegistryEntry`. They exist only in the full `SourceMetadata` at `library/sources/{source_id}/metadata.json`.

**Severity: HIGH.** The synthesis engine's metadata chain resolution is foundational to entry generation. If implementation reads from `sources.json` (the registry), three critical fields will be absent. This affects:
- Semantic deduplication (§4.A.2) which prefers highest `authority_level` and `text_fidelity`
- Factual layer construction which uses `genre` for direct quotation policy (matn genre → verbatim quote)
- Quality self-assessment which uses `text_fidelity_distribution`

**Resolution options:**
1. **(Recommended)** Correct the synthesis SPEC: change `library/registries/sources.json` to `library/sources/{source_id}/metadata.json` for fields not in the registry. This is consistent with D-023's design — the full metadata record is the canonical chain source.
2. Expand `SourceRegistryEntry` to include `genre`, `authority_level`, and `text_fidelity`. This adds redundancy but avoids full metadata reads during synthesis.

### 3.2 — Scholar authority resolution

**Downstream need:** "Scholar authority via `primary_author_id` → `library/registries/scholars.json`. Extracts: full name, death dates (hijri + CE), school affiliations, teachers, students, scholarly standing." (synthesis SPEC §4.A.1, line 208)
**Source provides:** `ScholarAuthorityRecord` — `canonical_name_ar`, `death_date_hijri`, `death_date_ce`, `school_affiliations`, `teachers`, `students`, `scholarly_standing` (contracts.py lines 555–626).
**Status: SATISFIED** — All extracted fields exist in the scholar authority record.

### 3.3 — Work relationships

**Downstream need:** "Work relationships via source metadata → work registry. Extracts: genre chain, relationships to other works." (synthesis SPEC §4.A.1, line 211)
**Source provides:** `SourceMetadata.genre_chain` — `Optional[GenreChain]`. `SourceMetadata.work_relationships` — `list[GenreChain]`. `WorkRegistryEntry.relationships` — `list[WorkRelationshipEdge]`.
**Status: SATISFIED**

### 3.4 — Physical citation assembly

**Downstream need:** "Citation includes: source title, author name, tahqiq editor (if known), publisher (if known), volume (if multi-volume), page numbers." (synthesis SPEC §4.A.4.1, line 340)
**Source provides:**
- `source title` → `SourceMetadata.title_arabic` ✓
- `author name` → `ScholarAuthorityRecord.canonical_name_ar` ✓
- `tahqiq editor` → `SourceMetadata.muhaqiq` → `ScholarReference.name_arabic` ✓
- `publisher` → `SourceMetadata.publisher` ✓
- `volume` → from excerpt/passage metadata (not source engine) ✓
- `page numbers` → from excerpt `physical_pages` (not source engine) ✓

**Status: SATISFIED** — All citation fields exist. Note that `publisher` and `muhaqiq` are only in `SourceMetadata`, not in `SourceRegistryEntry` — reinforcing finding 3.1 that synthesis must read from metadata.json.

---

## 4. Synthesis Engine — §4.A.3 Step 4: `composition_date` / Intra-Author Contradiction

**Downstream need:** "Retraction detection requires comparing source metadata `composition_date` fields; when unavailable, author death dates provide a rough proxy (works from the same author with no date disambiguation are flagged as `undatable`)." (synthesis SPEC §4.A.3, line 264)

**Source provides:** There is NO field named `composition_date` anywhere in source engine contracts.py or SPEC_CORE.md.

The closest field is `ScholarlyContext.composition_period` — `Optional[str]` (contracts.py lines 392–399). This is a narrative string like "Late comprehensive synthesis, reflecting the author's mature methodology" or "Early work, may not represent final positions." It is NOT a date or date range.

**Status: GAP — field name mismatch with semantic mismatch.**

**Analysis:** The synthesis SPEC says `composition_date` (implying a date or date range). The source engine provides `scholarly_context.composition_period` (a narrative string). These serve different purposes:

- `composition_date` would be a structured field (e.g., `{hijri: 670, circa: true}`) enabling chronological comparison: "Work A was written before Work B."
- `composition_period` is an LLM-inferred narrative assessment: "This is a late work." It cannot be computationally compared across works.

The synthesis SPEC's fallback — "when unavailable, author death dates provide a rough proxy" — shows the engine expects `composition_date` to sometimes be null. When it IS available, however, the engine wants to compute chronological ordering ("later work supersedes earlier"), which requires a comparable value, not a narrative string.

**Severity: MEDIUM.** The fallback (author death dates) handles the majority case — an author with works in the library usually has a single death date, so the proxy is useless for ordering works by the SAME author. The only case where `composition_date` adds value is: same author, multiple works, different composition periods. The narrative `composition_period` partially serves this need — a human could read "early work" vs "late work" and infer chronological ordering. But a machine cannot reliably extract chronological order from free-text narrative descriptions.

**Resolution options:**
1. **(Recommended)** Add a structured field `composition_date_hijri: Optional[int]` to `SourceMetadata` (or `ScholarlyContext`). The LLM inference prompt already attempts to characterize chronological placement — extracting a date or approximate date is a small extension. When the LLM is uncertain, the field remains null and the fallback engages.
2. Accept the current `composition_period` narrative string and have the synthesis engine use LLM analysis to parse chronological ordering from the narrative. This is fragile and adds an LLM call.
3. Document that intra-author contradiction detection relies solely on the "author death date" proxy (which provides no ordering for same-author works) and accept this as a known limitation.

---

## 5. Synthesis Engine — §4.A.4.2: Temporal Narrative and Teacher-Student Chains

### 5.1 — Temporal narrative construction

**Downstream need:** "Using author death dates from scholar authority records, the engine arranges positions chronologically and constructs a narrative showing scholarly evolution." (synthesis SPEC §4.A.4.2, line 348)
**Source provides:** `ScholarAuthorityRecord.death_date_hijri` — `Optional[int]`. `ScholarAuthorityRecord.death_date_ce` — `Optional[int]`. `ScholarAuthorityRecord.death_date_approximate` — `bool`.
**Status: SATISFIED** — Death dates exist in the scholar authority model. The `death_date_approximate` flag allows the synthesis engine to qualify temporal claims.

### 5.2 — Teacher-student chain discovery

**Downstream need:** "The engine traverses the scholar authority graph to find chains connecting scholars at this leaf." (synthesis SPEC §4.A.4.2, line 350)
**Source provides:** `ScholarAuthorityRecord.teachers` — `list[str]` (canonical_ids). `ScholarAuthorityRecord.students` — `list[str]` (canonical_ids).
**Status: SATISFIED** — Teacher/student links exist as canonical_id lists. The synthesis engine can build a directed graph from these fields using NetworkX (as documented in §4.B.2).

### 5.3 — Scholarly standing for authority weighting

**Downstream need:** Used implicitly for analytical layer narrative depth. The synthesis SPEC references "scholarly standing" in §4.A.1 metadata chain resolution (line 208).
**Source provides:** `ScholarAuthorityRecord.scholarly_standing` — `Optional[str]`. Also `ScholarlyContext.tradition_position` — `Optional[str]` (a work-level position assessment).
**Status: SATISFIED** — Both scholar-level standing and work-level tradition position exist.

### 5.4 — `methodological_stance` for authority weighting

**Downstream need:** The `ScholarlyContext` model in contracts.py documents that `tradition_position` is "Used by synthesis for authority weighting" (line 405) and `methodological_stance` in `ScholarAuthorityRecord` is "Used by synthesis for authority weighting when evaluating positions from this scholar" (line 607).
**Source provides:** `ScholarAuthorityRecord.methodological_stance` — `Optional[str]`. `ScholarlyContext.tradition_position` — `Optional[str]`.
**Status: SATISFIED** — Fields exist. Both are Optional; downstream handles null gracefully per ScholarlyContext docstring.

### 5.5 — `sectarian_tradition` for cross-tradition contamination prevention

**Downstream need:** The `ScholarAuthorityRecord.sectarian_tradition` field (contracts.py line 589) is documented as preventing "silent mixing of traditions from different sectarian contexts in synthesis." This is consumed by the synthesis engine's school isolation check (§4.A.5 Check 3).
**Source provides:** `ScholarAuthorityRecord.sectarian_tradition` — `Optional[str]`.
**Status: SATISFIED** — Field exists. Note: the synthesis SPEC does not explicitly mention `sectarian_tradition` in its school isolation check — it checks that excerpts' `school` values match the entry's school-group. The `sectarian_tradition` guard is an additional safety layer that would need to be verified during implementation, but the data is available.

### Temporal/Chain Summary

All 5 consumption points SATISFIED. The scholar authority model provides everything needed for temporal narrative construction and teacher-student chain discovery.

---

## 6. Taxonomy Engine (engines/taxonomy/SPEC.md)

The taxonomy engine's primary input is draft excerpts from the excerpting engine, not source metadata directly. However, it reads source metadata for specific operations.

### 6.1 — `trust_tier` for verified/flagged assignment

**Downstream need:** "If the excerpt's source has a `trust_tier` that maps to `flagged`, the excerpt receives `verified_flagged_status: flagged`." (taxonomy SPEC §4.A.4, line 208)
**Source provides:** `SourceRegistryEntry.trust_tier` — `TrustTier` enum. Also `SourceMetadata.trust_tier`.
**Status: SATISFIED** — `trust_tier` exists in both the registry and the full metadata. The taxonomy engine can read it from the registry (which it would access via `source_id`).

### 6.2 — `temporal_span` from scholar authority

**Downstream need:** "temporal_span: object. `earliest_author_death` and `latest_author_death` (hijri years) from scholar authority data." (taxonomy SPEC §3.3, line 99)
**Source provides:** `ScholarAuthorityRecord.death_date_hijri` — `Optional[int]`. Accessed via `primary_author_id` on each excerpt → scholar registry lookup.
**Status: SATISFIED** — The taxonomy engine computes temporal_span from death dates of excerpt authors. The data chain is: excerpt.primary_author_id → scholars.json → death_date_hijri.

### 6.3 — `school_coverage` from excerpt metadata

**Downstream need:** "school_coverage: object mapping school names to excerpt counts." (taxonomy SPEC §3.3, line 96)
**Source provides:** The `school` field on excerpts (produced by the excerpting engine, not the source engine). The taxonomy engine aggregates these — no direct source engine consumption.
**Status: SATISFIED** (not a source engine dependency)

### 6.4 — `source_id` for one-excerpt-per-source-per-leaf diagnostic

**Downstream need:** "If another excerpt from the same `source_id` is already placed at the same leaf, the diagnostic fires." (taxonomy SPEC §5.5/§4.A.4, line 206)
**Source provides:** `source_id` flows from source metadata through normalization → passaging → atomization → excerpting → taxonomy.
**Status: SATISFIED**

### 6.5 — `science_scope` for cross-science routing validation

**Downstream need:** "if a source that is expected to contribute to 2+ sciences (based on the source's `science_scope` metadata) has all excerpts routed to a single science, this is suspicious." (taxonomy SPEC §7 T-6, line 718)
**Source provides:** `SourceMetadata.science_scope` — `list[str]`.
**Status: SATISFIED** — The taxonomy engine can read `science_scope` from metadata.json via `source_id`.

### 6.6 — Scholar authority for scholarly landscape (§4.B.6)

**Downstream need:** "all placed verified excerpts, their full upstream metadata (source metadata, author metadata from the scholar authority registry, school affiliations, evidence types, content types, quoted scholars, implicit references)" (taxonomy SPEC §4.B.6, line 608). Specifically needs `death_date_hijri`, `school_affiliations`, `teachers`, `students` for influence chains and temporal analysis.
**Source provides:** All these fields exist in `ScholarAuthorityRecord`.
**Status: SATISFIED**

### 6.7 — Work registry for tree genesis (§4.A.3)

**Downstream need:** "The research phase also queries the scholar authority registry for the science's known scholarly tradition: which schools exist, which are the foundational works, what organizational conventions are standard." (taxonomy SPEC §4.A.3, line 225)
**Source provides:** `WorkRegistryEntry` in `library/registries/works.json` — `canonical_title`, `author_canonical_id`, `genre`, `science_scope`, `relationships`. `ScholarAuthorityRecord` — `school_affiliations`, `known_works`.
**Status: SATISFIED** — Work registry and scholar authority provide the needed data.

### Taxonomy Summary

All 7 consumption points SATISFIED. The taxonomy engine's source engine dependencies are well-served.

---

## 7. Passaging Engine (engines/passaging/SPEC.md §2)

The passaging engine reads from the normalized package (not source metadata directly), but also accesses source metadata via `source_id` for 4 specific fields.

### 7.1 — `science_scope`

**Downstream need:** "science_scope — science classification (array). For multi-science sources, passages may carry per-passage science hints." (passaging SPEC §2, line 45)
**Source provides:** `SourceMetadata.science_scope` — `list[str]`.
**Status: SATISFIED**

### 7.2 — `genre` / `genre_chain`

**Downstream need:** "genre / genre_chain — work genre relationships" (passaging SPEC §2, line 46)
**Source provides:** `SourceMetadata.genre` — `Genre` enum. `SourceMetadata.genre_chain` — `Optional[GenreChain]`.
**Status: SATISFIED**

### 7.3 — `structural_format`

**Downstream need:** "structural_format — source-level classification (the normalization engine's may override this)." (passaging SPEC §2, line 47)
**Source provides:** `SourceMetadata.structural_format` — `StructuralFormat` enum.
**Status: SATISFIED** — Note: the passaging engine reads both the source-level `structural_format` (from source metadata) and the normalization-level `structural_format` (from manifest.json). The normalization engine's value may override.

### 7.4 — `multi_layer`

**Downstream need:** "multi_layer — whether the source has multiple text layers." (passaging SPEC §2, line 48)
**Source provides:** `SourceMetadata.is_multi_layer` — `bool`.
**Status: SATISFIED** — Same field name mismatch as normalization (prose says `multi_layer`, field is `is_multi_layer`). The passaging engine primarily uses the normalized package's `layer_map` rather than the source metadata's `is_multi_layer`, so this is low risk.

### Passaging Summary

All 4 consumption points SATISFIED. No gaps.

---

## 8. Atomization Engine (engines/atomization/SPEC.md)

The atomization engine's primary input is the passage stream. It has minimal direct source metadata access.

### 8.1 — `science_scope` for concordance entries

**Downstream need:** "science_scope (string, the science this term belongs to, derived from source metadata)." (atomization SPEC §2 output schema, line 132)
**Source provides:** `SourceMetadata.science_scope` — `list[str]`.
**Status: SATISFIED** — Note: the atomization contracts say `science_scope: string` (singular) while source provides `list[str]` (array). The atomization engine selects the primary science from the list. This is a minor type mismatch handled at the implementation level.

### 8.2 — Multi-layer plausibility check

**Downstream need:** "If the source metadata declares the source as multi-layer (commentary), verify that at least one passage produced atoms with source_layer values from two or more distinct layers." (atomization SPEC §7 validation, line 878)
**Source provides:** `SourceMetadata.is_multi_layer` — `bool`.
**Status: SATISFIED**

### 8.3 — `source_id` pass-through

**Downstream need:** "source_id: string. The source's canonical identifier. Passed through unchanged from the passage record." (atomization SPEC §2 output schema, line 75)
**Source provides:** `SourceMetadata.source_id`.
**Status: SATISFIED**

### Atomization Summary

All 3 consumption points SATISFIED. No gaps.

---

## Consolidated Gap List

### GAP 1: Source Registry Missing Fields for Synthesis (HIGH)

**Location:** Synthesis SPEC §4.A.1 (line 207), Excerpting SPEC §2 (line 61)
**Nature:** Both the synthesis and excerpting engines claim to read from `library/registries/sources.json`, but extract fields (`genre`, `authority_level`, `text_fidelity`) that exist only in the full `SourceMetadata` at `library/sources/{source_id}/metadata.json`.

`SourceRegistryEntry` in contracts.py contains:
- `source_id` ✓, `work_id` ✓, `human_label` ✓, `title_arabic` ✓, `author_canonical_id` ✓, `trust_tier` ✓, `processing_status` ✓, `frozen_hash` ✓, `intake_timestamp` ✓, `acquisition_path` ✓

`SourceRegistryEntry` does NOT contain:
- `genre` ✗ (needed by synthesis for direct quotation policy, deduplication, quality assessment)
- `authority_level` ✗ (needed by synthesis for deduplication ranking: primary > reference > compilation)
- `text_fidelity` ✗ (needed by synthesis for deduplication ranking and quality assessment)
- `publisher` ✗ (needed by synthesis for citation assembly)
- `muhaqiq` ✗ (needed by synthesis for citation assembly)

**Impact:** If Claude Code implements the path as written in the synthesis SPEC (`sources.json`), five field lookups will fail or return null.

**Recommended resolution:** Correct both downstream SPECs to read from `library/sources/{source_id}/metadata.json` for these fields. The source registry is a lightweight index for status lookups and quick filtering; the full metadata record is the authoritative source for bibliographic fields. This is consistent with D-023's design intent ("Every downstream engine accesses the full source metadata via this reference [source_id]"). Do NOT expand the registry — that creates redundancy and staleness risk.

### GAP 2: `composition_date` Does Not Exist (MEDIUM)

**Location:** Synthesis SPEC §4.A.3 Step 4 (line 264)
**Nature:** The synthesis SPEC references `composition_date` for intra-author contradiction resolution ("Retraction detection requires comparing source metadata `composition_date` fields"). No such field exists in source engine output. The closest analog is `ScholarlyContext.composition_period`, a narrative string that cannot be computationally compared.

**Impact:** Intra-author contradiction detection falls back to "author death dates provide a rough proxy" in all cases. For same-author works, death dates provide zero ordering information. The retraction detection path (`later work supersedes earlier`) is effectively dead code unless the narrative string is parsed.

**Recommended resolution:** Add `composition_date_hijri: Optional[int]` to `ScholarlyContext` (or directly to `SourceMetadata`). The LLM inference prompt should extract an approximate hijri date when it has knowledge of when a work was composed. When unknown, the field remains null and the existing fallback engages. Also update the synthesis SPEC to reference the correct field path: `scholarly_context.composition_date_hijri` rather than bare `composition_date`.

### GAP 3: ScholarlyContext Orphaned — Source Produces, Synthesis Never Consumes (HIGH)

**Location:** Source engine contracts.py `ScholarlyContext` model (10 fields), synthesis SPEC.md (entire document)
**Nature:** The source engine produces `ScholarlyContext` with extensive docstrings claiming traced synthesis consumers (e.g., "Used by synthesis engine for intra-author contradiction resolution"). However, a search across ALL 6 downstream SPECs reveals zero references to `scholarly_context`, `composition_period`, `tradition_position`, `known_textual_issues`, `historical_significance`, `context_richness`, `uncertain_dimensions`, `edition_known_issues`, `tahqiq_methodology_note`, or `muhaqiq_reputation`. The only downstream reference is the normalization SPEC explicitly noting it does NOT read `scholarly_context`.

**Impact:** The synthesis engine's analytical layer (§4.A.4.2) describes generating context via its own LLM research (`grounding_type: "llm_research"`), but never mentions reading pre-computed context from source metadata. If Claude Code implements the synthesis SPEC as written, 10 source-engine-produced fields are generated, stored, and never consumed — wasted computation and missed narrative enrichment.

**Resolution:** Added explicit scholarly_context consumption to synthesis SPEC: §4.A.2 (metadata chain resolution step 6 with context_richness gating and uncertain_dimensions veto), §4.A.3 Step 4 (composition_date_hijri for retraction detection), §4.A.4.2 (new "Source scholarly context integration" paragraph covering all fields). Updated contracts.py docstring to mark consumer traces as verified.

---

## Secondary Findings (Non-Gap)

### Finding S-1: Normalization SPEC inline list omits `word_doc`

The normalization SPEC line 48 lists recognized `source_format` values as "shamela_html, pdf_text, pdf_scanned, image_scan, epub, plain_text, owner_authored" — omitting `word_doc`. However, the type map table at line 175 correctly includes `word_doc`. This is a prose inconsistency, not a contract gap, since the type map is authoritative.

### Finding S-2: `multi_layer` / `is_multi_layer` naming inconsistency persists in prose

Three downstream SPECs (normalization, passaging, atomization) use `multi_layer` in their prose while the source contracts.py field is `is_multi_layer`. This is already documented in SPEC_CORE §3.3 but has not been corrected in the downstream SPECs themselves. Not a gap (the mapping table resolves it), but a readability issue that could confuse Claude Code during implementation.

### Finding S-3: Atomization `science_scope` type mismatch

The atomization engine's concordance entry defines `science_scope: string` (singular) while the source engine provides `science_scope: list[str]` (array). The atomization engine must select the primary science from the list. This is a minor type adaptation, not a gap — the data exists.

### Finding S-4 (REVISED): `scholarly_context` was orphaned, now integrated

**Original finding (incorrect):** Praised `ScholarlyContext` as "well-designed" with "all downstream engines documented to handle null gracefully."

**Self-review correction:** This was wrong. The model's design IS good (Optional, context_richness gating, uncertain_dimensions veto), but no downstream SPEC actually referenced it. "Documented to handle null gracefully" was based on the source-side docstring's claim, not verified against downstream SPECs. The self-review identified this as the audit's most serious error — trusting source-side consumer claims without independent verification of downstream SPECs.

**Resolution (implemented):** Reclassified as GAP 3 (HIGH). Added explicit scholarly_context consumption to synthesis SPEC. The contracts.py docstring's consumer traces are now verified.

### Finding S-5 (RESOLVED): `sectarian_tradition` now referenced in synthesis SPEC

**Original finding:** The `ScholarAuthorityRecord.sectarian_tradition` field was not referenced in synthesis §4.A.5 Check 3.

**Resolution (implemented):** Added `sectarian_tradition` guard to Check 3, preventing cross-tradition contamination that school-level isolation alone would miss.

### Finding S-6 (NEW): Excerpting SPEC `source_authority` naming mismatch

The excerpting SPEC §4.B.2 line 636 used `source_authority` to refer to the authority ranking of sources. The contracts.py field is `authority_level` (enum `AuthorityLevel` with values `primary`, `reference`, `modern_compilation`). Corrected in excerpting SPEC.

### Finding S-7 (NEW): Synthesis `text_fidelity_distribution` absent from contracts

The synthesis SPEC §4.B.4 lists `text_fidelity_distribution` as a quality assessment dimension, but the synthesis `contracts.py` `QualityAssessment` model does not include this field. Similarly, `confidence_summary` is listed in §3.1 `generation_metadata` but absent from `GenerationMetadata` in contracts.py. Both are synthesis-internal contract gaps, not source engine gaps, but they affect how source engine data (`text_fidelity`, `confidence_scores`) flows into synthesis output. Flagged for synthesis engine build-prep.

---

## Implementation Status

All three gaps and findings S-5, S-6 resolved in this session:
- `contracts.py`: Added `composition_date_hijri: Optional[int]` to `ScholarlyContext`. Updated docstring with verified consumer traces.
- Source `SPEC_CORE.md`: Documented `composition_date_hijri` in field semantics, output example, prompt design. Added CHANGELOG entry.
- Synthesis `SPEC.md`: Fixed metadata chain resolution path (metadata.json, not sources.json). Added scholarly_context as resolution step 6. Fixed Step 4 composition_date reference with three-level fallback. Added "Source scholarly context integration" paragraph to §4.A.4.2. Added sectarian_tradition to Check 3.
- Excerpting `SPEC.md`: Fixed metadata access path (metadata.json for bibliographic fields, scholars.json for biographical). Fixed `source_authority` → `authority_level`.
