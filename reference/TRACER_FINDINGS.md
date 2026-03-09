# Tracer Bullet Findings — تقرير الرصاصة الكاشفة

**Date:** 2026-03-09
**Fixture:** `tests/fixtures/html_export_minimal` (Sharh Ibn Aqil — Shamela HTML)
**Result:** Pipeline SUCCESS — all 7 engines, 0 boundary errors after fixes

---

## Boundary Issues Found & Fixed

### 1. Source → Normalization (15 errors → 0)

| Field | Contract expects | Stub produced | Fix |
|-------|-----------------|---------------|-----|
| `author.name_arabic` | Required `str` | Missing (used `display_name`) | Renamed field to `name_arabic` |
| `author.source_of_identification` | Required `str` | Missing | Added identification source string |
| `muhaqiq.name_arabic` | Required `str` | Missing | Same as author fix |
| `muhaqiq.source_of_identification` | Required `str` | Missing | Same as author fix |
| `text_layers[].author` | `ScholarReference` object | Used flat `author_canonical_id` string | Changed to nested ScholarReference |
| `trust_factors[].name` | Required `str` | Used `factor` | Renamed to `name` |
| `trust_factors[].score` | Required `float` | Missing | Added score field |
| `trust_factors[].reason` | Required `str` | Used `evidence` | Renamed to `reason` |
| `confidence_scores.science_scope` | Required `float` | Missing | Added field |
| `confidence_scores.structural_format` | Required `float` | Missing | Added field |
| `confidence_scores.authority_level` | Required `float` | Missing | Added field |
| `metadata_history[].field` | Required `str` | Used `action` | Restructured MetadataHistoryEntry |
| `metadata_history[].new_value` | Required `str` | Missing | Added field |
| `metadata_history[].changed_by` | Required `str` | Missing | Added field |

**Root cause:** ScholarReference, TrustworthinessFactor, InferredFieldConfidence, and MetadataHistoryEntry contracts have more specific fields than what a naive "build from scratch" approach would guess. The contracts are well-designed but their field requirements only become apparent through Pydantic validation.

### 2. Normalization → Passaging (7 errors → 0)

| Field | Contract expects | Stub produced | Fix |
|-------|-----------------|---------------|-----|
| `manifest.layer_map[].detection_confidence` | Required `float` | Missing | Added field |
| `manifest.quality_report.overall_confidence` | `HeadingConfidence` enum | Used `float` (0.9) | Changed to `"high"` |
| `content_units[].footnotes[].secondary_types` | `list[SecondaryFootnoteType]` | `None` | Changed to `[]` |
| `content_units[].text_fidelity.score` | `TextFidelityLevel` enum | Used `float` (0.95) | Changed to `"high"` |

**Root cause:** Type mismatch between intuitive float-based confidence and enum-based confidence. The contracts use TextFidelityLevel and HeadingConfidence enums where a float might be expected. Also, `secondary_types` is a required list (not Optional), so it must be `[]` not `None`.

### 3. Passaging → Atomization (8 errors → 0)

| Field | Contract expects | Stub produced | Fix |
|-------|-----------------|---------------|-----|
| `passages[].footnotes[].source_unit_index` | Required `int` | Missing | Added unit_index from source content unit |
| `passages[].division_ids` | `list[str]` with `MinLen(1)` | Empty list `[]` | Added fallback `div_root_{source_id}` |
| `passages[].structural_format` | `PassageStructuralFormat` enum | `"commentary"` (wrong value) | Changed to `"commentary_unit"` |
| `passages[].text_fidelity.min_score` | `TextFidelityLevel` enum | Used `float` | Changed to `"high"` |
| `passages[].text_fidelity.mean_score` | `float` | Got `"high"` from upstream | Added `_fidelity_to_float()` converter |

**Root cause:** PassageStructuralFormat uses `commentary_unit` (not `commentary`) — subtle enum value mismatch between source engine's StructuralFormat and passaging engine's PassageStructuralFormat. The `division_ids` MinLen(1) constraint means every passage MUST have at least one division assignment, even at the root level.

**Cross-boundary type mismatch:** Normalization outputs `TextFidelityLevel` enum ("high") for `text_fidelity.score`, but the passaging engine's `mean_score` field expects a `float`. This required a converter function at the normalization→passaging boundary.

### 4. Atomization → Excerpting (0 errors)

Clean boundary. No issues.

### 5. Excerpting → Taxonomy (4 errors → 0)

| Field | Contract expects | Stub produced | Fix |
|-------|-----------------|---------------|-----|
| `excerpts[].physical_pages.start_page` | `Optional[str]` | `int` | Changed to `str()` |
| `excerpts[].physical_pages.end_page` | `Optional[str]` | `int` | Changed to `str()` |

**Root cause:** PhysicalPages in the excerpting contract uses string page numbers (to handle Arabic numerals and display formats like "١٥"), while the passaging contract uses integer `start_page_int`. The excerpting engine must convert.

### 6. Taxonomy → Synthesis (not validated by Pydantic)

The taxonomy and synthesis engines use custom output structures. Taxonomy outputs `{tree, placements, coverage}` which is not a single Pydantic model. The synthesis engine reads this JSON directly. No contract violations observed, but this boundary needs a formal contract model in Stage 1.

---

## Metadata Flow Analysis (D-023)

Tracked from source to entry:

| Metadata | Source | Normalization | Passaging | Atomization | Excerpting | Taxonomy | Synthesis |
|----------|--------|---------------|-----------|-------------|------------|----------|-----------|
| `source_id` | ✓ created | ✓ passed | ✓ passed | ✓ passed | ✓ passed | ✓ passed | ✓ in entry |
| `title_arabic` | ✓ extracted | — | — | — | — | — | ✓ in citation |
| `author.name_arabic` | ✓ extracted | — | — | — | — | — | ✓ in citation |
| `muhaqiq.name_arabic` | ✓ extracted | — | — | — | — | — | ✓ in citation |
| `publisher` | ✓ extracted | — | — | — | — | — | ✓ in citation |
| `volume/page` | ✓ in frozen | ✓ physical_page | ✓ physical_pages | — | ✓ physical_pages | — | ✓ in citation |
| `text_layers` | ✓ defined | ✓ per unit | ✓ per passage | ✓ source_layer | ✓ source_layer | — | — |
| `genre` | ✓ "sharh" | — | — | — | — | — | — |
| `science_scope` | ✓ ["nahw"] | — | — | — | ✓ science_id | ✓ (implicit) | ✓ science_id |

**Gaps identified:**
- `genre` and `structural_format` are not propagated beyond the source engine. Downstream engines don't need them directly, but the synthesis engine could use `genre` for narrative framing.
- `edition_number` and `publication_year` from source are not in the final citation. The synthesis engine should access these for complete bibliographic citations.
- Layer author attribution (`author_canonical_id` in text_layers) is set to `None` in normalization. The normalization engine should propagate author IDs from the source's layer_map.

---

## Arabic Text Integrity

The Alfiyyah verse with full tashkeel (كَلَامُنَا لَفْظٌ مُفِيدٌ كَاسْتَقِمْ) passes through all 7 engines with diacritics intact. JSON serialization with `ensure_ascii=False` preserves the text correctly. No Unicode normalization issues observed on this fixture.

---

## Statistics

- Total pipeline runtime: ~80ms
- Content units: 2 (from 2 pages)
- Passages: 2
- Atoms: 8
- Excerpts: 2
- Placed excerpts: 2
- Final entry: 1 (at `nahw/kalaam/definition`)
- Citations: 2

---

## Action Items for Stage 1

1. **Create formal contract models for taxonomy and synthesis output.** Currently these use ad-hoc JSON structures.
2. **Fix layer author propagation.** Normalization should carry `author_canonical_id` from source's `text_layers` into its own `text_layers` and `layer_map`.
3. **Add genre/format metadata to excerpts.** The excerpting engine should carry source-level metadata (genre, structural_format) for synthesis use.
4. **Standardize fidelity representation.** The TextFidelityLevel enum (string) vs. float confidence score inconsistency across normalization/passaging boundaries needs a clear convention.
5. **Validate taxonomy↔synthesis boundary formally.** Add PlacedExcerptAdditions validation once the taxonomy engine outputs per-excerpt placement records aligned with the contract.
