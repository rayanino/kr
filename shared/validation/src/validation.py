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
    check: str
    severity: Literal["fatal", "gate", "warning"]
    field: Optional[str]
    message: str
    error_code: Optional[str]
    recovery: str  # "abort" | "human_gate" | "flag_needs_review"


def validate_schema(
    data: dict[str, Any],
    schema: type[BaseModel],
) -> list[ValidationError]:
    """Check 1: Schema compliance via Pydantic model validation.

    severity: fatal, recovery: abort.
    """
    try:
        schema.model_validate(data)
        return []
    except PydanticValidationError as exc:
        errors: list[ValidationError] = []
        for err in exc.errors():
            field_path = ".".join(str(loc) for loc in err["loc"]) if err["loc"] else None
            errors.append(ValidationError(
                check="schema_compliance",
                severity="fatal",
                field=field_path,
                message=err["msg"],
                error_code="SRC_SCHEMA_VIOLATION",
                recovery="abort",
            ))
        return errors


def _resolve_nested_field(data: dict[str, Any], field_path: str) -> Any:
    """Resolve a dotted field path like 'author.canonical_id' in a nested dict."""
    parts = field_path.split(".")
    current: Any = data
    for part in parts:
        if isinstance(current, dict):
            current = current.get(part)
        elif hasattr(current, part):
            current = getattr(current, part)
        else:
            return None
        if current is None:
            return None
    return current


def validate_referential_integrity(
    data: dict[str, Any],
    registries: dict[str, dict],
    ref_fields: list[tuple[str, str]],
) -> list[ValidationError]:
    """Check 2: Referential integrity — verify cross-references resolve.

    severity: fatal, recovery: abort, error_code: SRC_REGISTRY_CONFLICT.
    """
    errors: list[ValidationError] = []

    for field_path, registry_name in ref_fields:
        ref_value = _resolve_nested_field(data, field_path)
        if ref_value is None:
            continue  # Optional reference, not present

        registry = registries.get(registry_name, {})
        if ref_value not in registry:
            errors.append(ValidationError(
                check="referential_integrity",
                severity="fatal",
                field=field_path,
                message=(
                    f"Reference '{ref_value}' in field '{field_path}' "
                    f"not found in registry '{registry_name}'"
                ),
                error_code="SRC_REGISTRY_CONFLICT",
                recovery="abort",
            ))

    return errors


def validate_enrichment_passthrough(
    before: dict[str, Any],
    after: dict[str, Any],
) -> list[ValidationError]:
    """D-023 pass-through check: no upstream fields deleted during enrichment.

    Any key in `before` that was non-null and is now null or missing in `after`
    → SRC_INVALID_ENRICHMENT.

    severity: fatal, recovery: abort.
    """
    errors: list[ValidationError] = []

    for key, old_value in before.items():
        if old_value is None:
            continue  # Was null before, so deletion is acceptable

        new_value = after.get(key)
        if new_value is None:
            errors.append(ValidationError(
                check="enrichment_passthrough",
                severity="fatal",
                field=key,
                message=(
                    f"D-023 violation: field '{key}' was '{old_value}' "
                    f"but is now null/missing after enrichment"
                ),
                error_code="SRC_INVALID_ENRICHMENT",
                recovery="abort",
            ))

    return errors
