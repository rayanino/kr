# Validation — Source Engine Requirements

**Component:** `shared/validation/`
**Consumer:** Source engine (Session 5), all downstream engines
**SPEC authority:** `engines/source/SPEC_CORE.md` §5 Layer 1

---

## Purpose

The validation module runs self-checks before every metadata write. It catches schema violations, referential integrity breaks, confidence threshold violations, consistency contradictions, and multi-layer coherence issues. Any failure aborts the write — invalid data never reaches disk.

---

## Interface

### `validate_output()`

```python
from dataclasses import dataclass
from typing import Any, Optional, Literal
from pydantic import BaseModel


@dataclass
class ValidationError:
    """A single validation failure."""
    check: str               # Which of the 6 checks failed (e.g., "schema_compliance")
    severity: Literal["fatal", "gate", "warning"]
    field: Optional[str]     # Which field caused the failure, if applicable
    message: str             # Human-readable description
    error_code: Optional[str]  # SRC_* error code from contracts.py, if applicable
    recovery: str            # What should happen: "abort", "human_gate", "flag_needs_review"


def validate_output(
    data: dict[str, Any],
    schema: type[BaseModel],
    registries: Optional[dict[str, Any]] = None,
    prior_sources: Optional[list[dict]] = None,
) -> list[ValidationError]:
    """Validate engine output before writing to disk.

    Runs all 6 Layer 1 checks in order. Returns a list of validation errors.
    An empty list means validation passed.

    Parameters
    ----------
    data : dict
        The metadata record to validate (will be validated against schema).
    schema : type[BaseModel]
        The Pydantic model to validate against (e.g., SourceMetadata).
    registries : dict, optional
        Registry data for referential integrity checks. Keys:
        - "scholars": dict mapping canonical_id → ScholarAuthorityRecord
        - "works": dict mapping work_id → WorkRegistryEntry
        Required for checks 2, 5, and 6. If None, referential integrity
        checks are skipped (useful for unit testing).
    prior_sources : list[dict], optional
        Other SourceMetadata records for the same work_id, if any.
        Used for the attribution_status cross-check in check 5.

    Returns
    -------
    list[ValidationError]
        Empty list = valid. Any entries = invalid.
        Check the severity and recovery fields to determine the action:
        - severity="fatal", recovery="abort": stop processing entirely.
        - severity="gate", recovery="human_gate": create a human gate checkpoint.
        - severity="warning", recovery="flag_needs_review": add to needs_review_fields.
    """
```

---

## The 6 Layer 1 Checks (SPEC §5)

### Check 1: Schema Compliance

Validate `data` against the Pydantic `schema` model. Catches: missing required fields, type mismatches, constraint violations.

```python
def _check_schema_compliance(data: dict, schema: type[BaseModel]) -> list[ValidationError]:
    """Pydantic model validation.
    
    severity: fatal
    recovery: abort
    error_code: None (Pydantic provides its own error detail)
    """
```

### Check 2: Referential Integrity

- `author.canonical_id` must resolve in `scholars.json`.
- `work_id` must resolve in `works.json`.
- Genre chain work references must resolve (or exist as placeholder records).
- Every `TextLayer.author.canonical_id` must resolve in `scholars.json`.

```python
def _check_referential_integrity(data: dict, registries: dict) -> list[ValidationError]:
    """Verify all cross-references resolve.
    
    severity: fatal
    recovery: abort
    error_code: SRC_REGISTRY_CONFLICT
    """
```

### Check 3: Confidence Threshold Check

If any critical inferred field has confidence < 0.50 → abort write → create human gate.

**Fields checked:**
- `author.confidence` (author identity confidence)
- `confidence_scores.genre` (genre classification)
- `confidence_scores.science_scope` (science scope)

Note: `work_id` confidence is NOT checked here — work matching with confidence < 0.50 creates a new work record during Step 4, so by the time validation runs, `work_id` is already resolved.

**Threshold behavior:**
- confidence < 0.50 → `severity="gate"`, `recovery="human_gate"` (blocks write)
- confidence 0.50–0.70 → field added to `needs_review_fields` (does not block write, but this is handled by the engine during field mapping, not by this check)

```python
def _check_confidence_thresholds(data: dict) -> list[ValidationError]:
    """Verify critical field confidences meet the 0.50 minimum.
    
    severity: gate (creates human gate checkpoint)
    recovery: human_gate
    error_code: SRC_LOW_CONFIDENCE
    """
```

### Check 4: Duplicate Re-Check

After inference (which may have changed title or author), re-run deduplication. Catches cases where raw metadata didn't match but inferred metadata does.

```python
def _check_duplicates(data: dict, registries: dict) -> list[ValidationError]:
    """Post-inference deduplication check.
    
    Uses the inferred title + author to check against existing work records.
    This is distinct from the hash-based dedup in Step 5 — this catches
    semantic duplicates (same work, different file).
    
    severity: warning
    recovery: flag_needs_review (SRC_DUPLICATE_WORK is Info, not blocking)
    """
```

### Check 5: Consistency Cross-Check

Inferred fields are checked for mutual consistency. Six sub-checks:

**5a. Genre vs structural_format:**
- `nazm` → structural_format should be `verse`
- `sharh` → structural_format should be `commentary` or `prose` (running prose commentary is valid)
- `hashiyah` → structural_format should be `commentary`
- Mismatch → `severity="warning"`, `recovery="flag_needs_review"`, `error_code="SRC_METADATA_INCONSISTENCY"`

**5b. Level vs genre:**
- `hashiyah` should not be `beginner`
- Mismatch → warning, flag

**5c. Author vs science scope:**
- If `science_scope` doesn't overlap with the author's known specializations (from `school_affiliations` in the scholar registry) → `severity="gate"`, `recovery="human_gate"`, `error_code="SRC_METADATA_INCONSISTENCY"`, `human_gate_trigger="AUTHOR_SCIENCE_MISMATCH"`. This is the ONLY consistency sub-check that triggers a human gate — author-science mismatch often indicates a misidentified author.

**5d. Attribution status vs prior sources:**
- If `attribution_status` is `definitive` or `traditional` but an existing source of the same `work_id` has `attribution_status` = `disputed` or `unknown` → `severity="warning"`, `recovery="flag_needs_review"`. Not blocking — creates `needs_review` on `attribution_status`.

**5e. Genre vs multi-layer (CRITICAL — prevents T-2 Attribution Error):**
- If `genre` is `sharh` or `hashiyah`, `is_multi_layer` MUST be true.
- If `is_multi_layer` is false → auto-correct to true, log `SRC_METADATA_INCONSISTENCY`.
- Then check 6 will verify `text_layers` is non-empty.

**5f. (Placeholder for additional consistency rules added in later sessions.)**

```python
def _check_consistency(data: dict, registries: dict, prior_sources: list) -> list[ValidationError]:
    """Mutual consistency of inferred fields.
    
    Most sub-checks: severity="warning", recovery="flag_needs_review"
    Exception: author-science mismatch: severity="gate", recovery="human_gate"
    """
```

### Check 6: Multi-Layer Coherence

Three sub-checks enforce multi-layer metadata is internally consistent:

**6a.** If `is_multi_layer` is true, `text_layers` must be non-empty. Empty list → `severity="gate"`, `recovery="human_gate"`, `error_code="SRC_LOW_CONFIDENCE"`, field `"text_layers"`.

**6b.** If `is_multi_layer` is false, `text_layers` must be empty. Non-empty list with `is_multi_layer=false` → auto-correct `is_multi_layer` to true, log warning.

**6c.** Every `TextLayer.author.canonical_id` must resolve in `scholars.json`. Broken reference → `severity="fatal"`, `recovery="abort"`.

```python
def _check_multi_layer_coherence(data: dict, registries: dict) -> list[ValidationError]:
    """Multi-layer metadata internal consistency.
    
    Prevents T-2 (Attribution Error) where a sharh/hashiyah is treated
    as single-author text, causing every excerpt from the embedded matn
    to be attributed to the commentator.
    """
```

---

## D-023 Pass-Through Check

While not one of the 6 numbered Layer 1 checks, validation also enforces the metadata pass-through invariant (SPEC §3.3): no upstream fields may be deleted during enrichment.

```python
def validate_enrichment_passthrough(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[ValidationError]:
    """Verify that no existing non-null fields were set to null or deleted.
    
    Called during enrichment write-back processing, not during initial intake.
    
    severity: fatal
    recovery: abort (reject the enrichment)
    error_code: SRC_INVALID_ENRICHMENT
    """
```

---

## Which Checks Block vs Flag vs Gate

| Check | Blocking (abort write) | Human Gate | Warning (flag) |
|-------|----------------------|------------|----------------|
| 1. Schema compliance | YES | — | — |
| 2. Referential integrity | YES | — | — |
| 3. Confidence < 0.50 | — | YES | — |
| 4. Duplicate re-check | — | — | YES (Info) |
| 5a. Genre↔format | — | — | YES |
| 5b. Level↔genre | — | — | YES |
| 5c. Author↔science | — | YES | — |
| 5d. Attribution↔prior | — | — | YES |
| 5e. Genre↔multi-layer | — | (auto-correct, then check 6 may gate) | — |
| 6a. Multi-layer + empty layers | — | YES | — |
| 6b. Not multi-layer + has layers | — | — | (auto-correct) |
| 6c. Layer author refs | YES | — | — |
| D-023 pass-through | YES | — | — |

---

## Cross-Engine Reuse

The normalization engine uses validation for its own Layer 1 checks. The `validate_output()` interface is designed for reuse:

- `schema` parameter accepts any Pydantic model (not just SourceMetadata).
- `registries` parameter is optional, allowing normalized output validation without requiring source registries.
- The normalization engine will define its own additional checks (e.g., page-level fidelity validation) and compose them with the shared checks.

The validation module does NOT import from `engines/source/` for the generic checks (schema, referential integrity). Source-engine-specific logic (the 6 checks above) is implemented in the source engine's validation integration code, which calls the shared module's generic functions plus source-specific checks.

**Architectural split:**
- `shared/validation/src/validation.py` — Generic: schema validation, referential integrity, D-023 pass-through.
- `engines/source/src/validation.py` — Source-specific: confidence thresholds, consistency cross-checks, multi-layer coherence. Imports and uses the shared module.
