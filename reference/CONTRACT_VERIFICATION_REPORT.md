# Contract Verification Report: Source Engine → Normalization Engine

**Date:** 2026-03-16
**Step:** Pre-Batch Hardening, Step 3
**Author:** Claude Chat (Architect)
**Commits reviewed:** up to 73547f9

---

## 1. Executive Summary

The source engine produces output that is structurally compatible with the
normalization engine's input expectations. No blocking gaps exist. However,
five defects need correction before the normalization engine is built:

- **2 field name mismatches** in the normalization SPEC (low risk — typed API
  catches these, but SPEC text would mislead Claude Code)
- **1 enum value mismatch** between TextFidelity definitions (medium risk —
  runtime crash if normalization parses source's "unknown" as its own enum)
- **1 undeclared dependency** (page_count needed for §5 check 2 but not in
  SPEC §2 input list)
- **1 stale field count** in ScholarAuthorityRecord docstring (cosmetic)

All defects are correctable with SPEC text edits. No code changes needed in
the source engine. No re-run of pipeline results required.

---

## 2. Methodology

**Subtask 3A** mapped all 15 source engine output artifacts by reading
`contracts.py` (1048 lines), `engine.py`, `registries/__init__.py`,
`run_phase_c.py`, and actual Phase D result files (204 books). Every field
was verified against Pydantic model definitions and real JSON output.

**Subtask 3B** mapped normalization input expectations by reading the
normalization SPEC §2 (explicit field list), `contracts.py` (697 lines),
`dispatcher.py`, `normalizers/base.py`, `normalizers/shamela.py`,
`validation.py`, `tracer.py`, and all other `src/` files. Two access
patterns were identified: typed attribute access (production API) and dict
access (tracer implementation).

**Subtask 3C** cross-referenced every normalization-consumed field against
source engine output, verified type compatibility, and resolved three
specific questions from the verification plan.

---

## 3. Contract Boundary Definition

The normalization engine consumes source engine output at two points:

1. **Frozen source files**: `library/sources/{source_id}/frozen/`
   Read-only files copied and hashed by the source engine's freeze step.

2. **Source metadata record**: `library/sources/{source_id}/metadata.json`
   A serialized `SourceMetadata` Pydantic model (56 fields).

**NOT the contract boundary**: `tests/results/.../result.json` files from
pipeline runs. These contain runner-injected fields (`status: "success"`,
`processing_time_seconds`, `is_rerun`, `original_phase`) and may have a
different `work_id` than the library's `metadata.json` (due to
`register_source()` regeneration). The normalization engine must never read
from test result files.

**Processing trigger**: Source registry (`library/registries/sources.json`)
entries with `processing_status: "acquired"`.

---

## 4. Field-by-Field Cross-Reference

### 4.1 Declared dependencies (normalization SPEC §2)

| # | Norm SPEC name | Source field | Produced? | Name match | Type match | Notes |
|---|---|---|---|---|---|---|
| 1 | `source_id` | `source_id` | ✅ | ✅ | ✅ str | Primary key |
| 2 | `source_format` | `source_format` | ✅ | ✅ | ✅ SourceFormat | Dispatcher routing |
| 3 | `work_id` | `work_id` | ✅ | ✅ | ✅ str | Zero code refs in norm |
| 4 | `text_fidelity` | `text_fidelity` | ✅ | ✅ | ⚠️ ENUM GAP | See §5.1 |
| 5 | `structural_format` | `structural_format` | ✅ | ✅ | ✅ exact enum match | May be overridden |
| 6 | `multi_layer` | `is_multi_layer` | ✅ | ❌ NAME GAP | ✅ bool | See §5.2 |
| 7 | `layers` | `text_layers` | ✅ | ❌ NAME GAP | ✅ list[TextLayer] | See §5.2 |
| 8 | `genre` | `genre` | ✅ | ✅ | ✅ Genre enum | Zero code refs in norm |
| 9 | `volume_count` | `volume_count` | ✅ | ✅ | ✅ Optional[int] | Multi-vol processing |

### 4.2 Undeclared dependencies (found in code/SPEC behavior)

| # | Field | Source field | How discovered | Notes |
|---|---|---|---|---|
| 10 | `frozen_path` | `frozen_path` | tracer.py L30 | Production API takes as arg; tracer reads from JSON |
| 11 | `text_layers` (nested) | `text_layers[].author` | tracer.py L439-451 | Layer→author backfill needs ScholarReference structure |
| 12 | `page_count` | `page_count` | SPEC §5 check 2 | Coverage validation: unit count vs page count ±10% |

### 4.3 Explicitly NOT consumed (confirmed)

These source metadata fields are NOT read by the normalization engine and
pass through untouched via the `source_id` reference (D-023):

`scholarly_context`, `trust_tier`, `trust_score`, `trust_factors`,
`confidence_scores`, `needs_review_fields`, `attribution_status`,
`attribution_notes`, `genre_chain`, `work_relationships`, `muhaqiq`,
`publisher`, `edition_number`, `publication_year_*`, `authority_level`,
`metadata_history`, `enrichment_sources`, `enrichment_tracking`,
`format_specific_metadata`, `frozen_hash`, `frozen_file_hashes`,
`owner_authored_type`, `compositional_profile`, `difficulty_prediction`,
`tahqiq_fingerprint`.

---

## 5. Defects Found

### 5.1 DEFECT: TextFidelity enum value mismatch

**Severity:** Medium (runtime crash risk)
**Location:** Source: `engines/source/contracts.py` TextFidelity enum.
Normalization: `engines/normalization/contracts.py` TextFidelityLevel enum.

**Problem:** Source engine has values `{high, medium, low, unknown}`.
Normalization engine has values `{high, medium, low, very_low}`. If
normalization code attempts `TextFidelityLevel(metadata.text_fidelity.value)`
on a source with `text_fidelity: "unknown"`, it will crash with a ValueError.

**Impact:** Any source with `text_fidelity: "unknown"` would fail
normalization. Currently all Shamela sources get `high`, so this is latent.
It would trigger when PDF scanned or image sources are processed.

**Fix:** Two options:
- (A) Add `UNKNOWN = "unknown"` to normalization's `TextFidelityLevel`.
  Pros: direct compatibility. Cons: `unknown` is semantically different from
  the per-page quality levels (it means "source-level quality not assessed").
- (B) Map `unknown` → `medium` at the normalization boundary (conservative
  default). Document the mapping.
- **Recommended: (A)** — preserving the source signal is better than lossy
  mapping. The normalization engine already refines to page-level; `unknown`
  as a source-level baseline just means "no prior information."

### 5.2 DEFECT: Field name mismatches in normalization SPEC §2

**Severity:** Low (typed API catches this; SPEC text misleads Claude Code)
**Location:** `engines/normalization/SPEC.md` §2, lines 52-53.

**Problem:** SPEC says `multi_layer` and `layers`. Source engine's
SourceMetadata model uses `is_multi_layer` and `text_layers`. The typed
dispatcher API (`metadata: SourceMetadata`) accesses correct names via
Python attribute resolution. But if Claude Code reads the SPEC text and
implements dict-access patterns (as the tracer does), it would use wrong
field names.

**Fix:** Update normalization SPEC §2 line 52:
- `multi_layer` → `is_multi_layer`
- "the `layers` field" → "the `text_layers` field"

### 5.3 DEFECT: Unlisted page_count dependency

**Severity:** Low (field exists and is populated; just missing from SPEC §2)
**Location:** `engines/normalization/SPEC.md` §2 (input field list) and §5
check 2 (coverage validation).

**Problem:** SPEC §5 check 2 says "the number of content units must match
the expected page count from the source metadata (±10%)." But `page_count`
is not listed in §2's declared input fields. Claude Code implementing
§5 check 2 would need to discover this dependency independently.

**Fix:** Add `page_count` to the §2 input field list:
"`page_count`: the source engine's page count estimate. Used by §5 check 2
(coverage validation) to verify content unit count matches expected pages."

### 5.4 DEFECT: Stale field count in ScholarAuthorityRecord

**Severity:** Cosmetic
**Location:** `engines/source/contracts.py` line 596.

**Problem:** Docstring says "24 defined fields" but the model has 33 fields.
This was likely accurate at an earlier point and not updated.

**Fix:** Update docstring: "24 defined fields" → "33 defined fields".

---

## 6. Resolved Questions

### 6.1 Death dates — where, how?

The normalization engine does NOT consume death dates from source metadata.
Death dates live in `ScholarAuthorityRecord` in the scholar registry
(`library/registries/scholars.json`). Phase 2 engines access them via the
chain: `source_id → metadata.json → author.canonical_id → scholars.json →
death_date_hijri/death_date_ce`. No contract gap exists.

The normalization engine only encounters death dates incidentally within
footnote text (`BiographicalNoteData.death_date_ah`), which it extracts
from content, not from source metadata.

### 6.2 Genre — string or enum, new values?

Genre is a `Genre` enum with 20 values in the source engine. The
normalization engine does not define its own Genre enum — it reads the
source's. No new values are needed. Genre-dependent processing strategies
(nazm→verse-aware, mujam→dictionary-entry) are normalization-internal
decisions that use the source enum value as input. The exhaustive enum
ensures no surprise values cross the boundary.

### 6.3 Fix 3 fields — propagation needed?

No. Fix 3 adds `death_date_hijri` to `needs_review_fields` and introduces
validation check 5g (death date warning). The `needs_review_fields` field is
source-engine-internal — the normalization engine does NOT read it (confirmed
in §4.3). Fix 3's changes stay entirely within the source engine boundary.

---

## 7. Enrichment Write-Back Interface

The normalization SPEC §2 specifies four enrichment write-back types:
1. Volume structure corrections
2. Structural format overrides
3. Multi-layer discovery
4. Encoding anomalies

These use the source engine's `EnrichmentRequest` model (`engines/source/
contracts.py`). Currently zero implementation exists in normalization code
(only a docstring reference in `base.py`). This is expected for stubs.

When Claude Code implements enrichment write-backs, it must import and use
`EnrichmentRequest` with `verification_context` for critical field updates
(genre, structural_format per source SPEC §2 invariant #9).

---

## 8. Type Safety Assessment

Two access patterns exist in the normalization codebase:

**Production API (dispatcher.py, base.py, shamela.py, validation.py):**
Takes `metadata: SourceMetadata` — typed attribute access. Field name
mismatches caught at attribute access time. Enum mismatches caught at
assignment. This is the safe path.

**Tracer (tracer.py):** Loads metadata via `json.loads()` → plain dict.
Uses `source_meta["field_name"]` and `source_meta.get("field_name")`.
Field name errors pass silently (returns None or KeyError). The tracer
happens to use correct field names (`text_layers`, `structural_format`)
but this is accidental — it was written by reading the code, not the SPEC.

**Recommendation:** When Claude Code implements the Shamela normalizer, it
must use the typed `SourceMetadata` parameter from `base.py`'s interface,
NOT the tracer's dict-access pattern. The typed path provides compile-time-
equivalent safety that the dict path lacks.

---

## 9. status Field Discrepancy

Source engine's `SourceMetadata.status` field uses `ProcessingStatus` enum
(`acquired`, `normalizing`, `normalized`, etc.). The pipeline runner
overwrites this to `"success"` in `result.json`. The library's
`metadata.json` retains the correct `"acquired"` value.

The normalization engine's processing trigger checks for `status: "acquired"`
in the source registry (`sources.json`), which uses `ProcessingStatus`
values — not the runner's string. No gap, but this discrepancy must be
documented to prevent confusion during debugging.

---

## 10. Recommendations

### Immediate (before normalization engine build)

1. Fix normalization SPEC §2: `multi_layer` → `is_multi_layer`,
   `layers` → `text_layers` (§5.2)
2. Fix normalization SPEC §2: add `page_count` to input field list (§5.3)
3. Add `UNKNOWN = "unknown"` to normalization `TextFidelityLevel` (§5.1)
4. Fix source contracts.py docstring: "24" → "33" fields (§5.4)

### During normalization engine build

5. Claude Code must use typed `SourceMetadata` attributes, not dict access
6. Claude Code must import `EnrichmentRequest` for write-backs
7. Normalization CLAUDE.md should reference this report for contract details

### Deferred (post-build)

8. Consider whether `work_id` should be removed from normalization SPEC §2
   (listed but unused) or documented with its actual purpose
