"""Shared Validation Module — SPEC §5 Layer 1 (generic checks)

Provides reusable validation functions that every engine needs:
1. Schema compliance (Pydantic model validation)
2. Referential integrity (cross-reference resolution)
3. D-023 pass-through enforcement (no upstream field deletion)

Source-engine-specific checks (confidence thresholds, consistency cross-checks,
multi-layer coherence) are in engines/source/src/validation.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal, Optional

from pydantic import BaseModel, ValidationError as PydanticValidationError


@dataclass
class ValidationError:
    """A single validation failure.
    
    Severities (SPEC §5 Layer 1):
    - fatal: abort the write entirely.
    - gate: create human gate checkpoint, halt processing for this field.
    - warning: flag in needs_review_fields, continue processing.
    """
    check: str               # Which check failed: "schema_compliance", "referential_integrity", etc.
    severity: Literal["fatal", "gate", "warning"]
    field: Optional[str]     # Which field caused the failure, if applicable
    message: str             # Human-readable description
    error_code: Optional[str]  # SRC_* error code, if applicable
    recovery: str            # "abort" | "human_gate" | "flag_needs_review"


def validate_schema(
    data: dict[str, Any],
    schema: type[BaseModel],
) -> list[ValidationError]:
    """Check 1: Schema compliance via Pydantic model validation.
    
    SPEC §5 Layer 1 Check 1: 'Validate the metadata record against the
    Pydantic model. Missing required field, type mismatch, or constraint
    violation → abort with structured error.'
    
    severity: fatal
    recovery: abort
    """
    raise NotImplementedError


def validate_referential_integrity(
    data: dict[str, Any],
    registries: dict[str, dict],
    ref_fields: list[tuple[str, str]],
) -> list[ValidationError]:
    """Check 2: Referential integrity.
    
    SPEC §5 Layer 1 Check 2: Verify cross-references resolve.
    
    Args:
        data: The metadata record to validate.
        registries: Dict mapping registry name → registry data.
            e.g. {"scholars": {...}, "works": {...}}
        ref_fields: List of (field_path, registry_name) tuples.
            e.g. [("author.canonical_id", "scholars"), ("work_id", "works")]
    
    severity: fatal
    recovery: abort
    error_code: SRC_REGISTRY_CONFLICT
    """
    raise NotImplementedError


def validate_enrichment_passthrough(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[ValidationError]:
    """D-023 pass-through check: no upstream fields deleted during enrichment.
    
    SPEC §3.3: 'Downstream engines may ADD but never REMOVE or OVERWRITE
    fields added by upstream engines.'
    
    Checks that no existing non-null field was set to null or removed.
    Called during enrichment write-back processing, not during initial intake.
    
    severity: fatal
    recovery: abort
    error_code: SRC_INVALID_ENRICHMENT
    """
    raise NotImplementedError
