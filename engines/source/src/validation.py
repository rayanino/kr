"""Source Engine Self-Validation (Layer 1) — SPEC §5

Six checks run in order before every metadata write. Any fatal failure aborts.

Check 1: Schema compliance (delegated to shared/validation)
Check 2: Referential integrity (delegated to shared/validation)
Check 3: Confidence threshold — critical fields < 0.50 → human gate
Check 4: Duplicate re-check — post-inference dedup
Check 5: Consistency cross-check (5a-5e):
    5a. Genre ↔ structural_format
    5b. Level ↔ genre
    5c. Author ↔ science scope (HUMAN GATE — only consistency check that gates)
    5d. Attribution status ↔ prior sources
    5e. Genre ↔ multi-layer (auto-corrects, then Check 6 verifies)
Check 6: Multi-layer coherence (6a-6c):
    6a. is_multi_layer=true → text_layers non-empty (else GATE)
    6b. is_multi_layer=false → text_layers empty (else auto-correct)
    6c. Every TextLayer.author.canonical_id resolves in scholars.json

Returns list[ValidationError]; empty = valid.
"""

from __future__ import annotations

from typing import Any, Optional

from engines.source.contracts import SourceMetadata
from shared.validation.src.validation import (
    ValidationError,
    validate_enrichment_passthrough,
    validate_referential_integrity,
    validate_schema,
)


def validate_source_metadata(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]] = None,
    prior_sources: Optional[list[dict]] = None,
) -> list[ValidationError]:
    """Run all 6 Layer 1 checks on a SourceMetadata record.

    Returns list[ValidationError] — empty means valid.
    """
    errors: list[ValidationError] = []

    # Check 1: Schema compliance
    schema_errors = validate_schema(data, SourceMetadata)
    if schema_errors:
        return schema_errors  # Fatal — abort immediately

    # Check 2: Referential integrity
    if registries:
        ref_fields = []
        if "scholars" in registries:
            ref_fields.append(("author.canonical_id", "scholars"))
        if "works" in registries:
            ref_fields.append(("work_id", "works"))
        ri_errors = validate_referential_integrity(data, registries, ref_fields)
        errors.extend(ri_errors)

    # Check 3: Confidence thresholds
    errors.extend(_check_confidence_thresholds(data))

    # Check 4: Duplicate re-check (warning only)
    if registries:
        errors.extend(_check_duplicates(data, registries))

    # Check 5: Consistency cross-checks (5a-5e)
    # NOTE: Check 5e may auto-correct is_multi_layer in data dict
    errors.extend(_check_consistency(data, registries, prior_sources))

    # Check 6: Multi-layer coherence (6a-6c)
    # Runs AFTER Check 5e which may have auto-corrected is_multi_layer
    errors.extend(_check_multi_layer_coherence(data, registries))

    return errors


def _check_confidence_thresholds(data: dict[str, Any]) -> list[ValidationError]:
    """Check 3: Critical fields with confidence < 0.50 → human gate."""
    errors: list[ValidationError] = []
    confidence = data.get("confidence_scores", {})

    # Author confidence: check both ScholarReference and LLM inference
    author = data.get("author", {})
    author_conf = author.get("confidence") if isinstance(author, dict) else None

    checks = [
        ("author.confidence", author_conf),
        ("confidence_scores.author", confidence.get("author")),
        ("confidence_scores.genre", confidence.get("genre")),
        ("confidence_scores.science_scope", confidence.get("science_scope")),
    ]

    for field_path, value in checks:
        if value is not None and value < 0.50:
            errors.append(ValidationError(
                check="confidence_threshold",
                severity="gate",
                field=field_path,
                message=f"Critical field {field_path} has confidence {value:.2f} < 0.50",
                error_code="SRC_LOW_CONFIDENCE",
                recovery="human_gate",
            ))

    return errors


def _check_duplicates(data: dict[str, Any], registries: dict[str, dict]) -> list[ValidationError]:
    """Check 4: Post-inference duplicate re-check (warning only)."""
    errors: list[ValidationError] = []
    work_id = data.get("work_id")
    source_id = data.get("source_id")

    if not work_id or not registries.get("sources"):
        return errors

    # Check if another source already has the same work_id
    for sid, source_data in registries["sources"].items():
        if sid != source_id and source_data.get("work_id") == work_id:
            errors.append(ValidationError(
                check="duplicate_recheck",
                severity="warning",
                field="work_id",
                message=(
                    f"Source {source_id} shares work_id '{work_id}' "
                    f"with existing source {sid}"
                ),
                error_code="SRC_DUPLICATE_WORK",
                recovery="flag_needs_review",
            ))
            break

    return errors


def _check_consistency(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]],
    prior_sources: Optional[list[dict]],
) -> list[ValidationError]:
    """Check 5: Consistency cross-checks (5a-5e)."""
    errors: list[ValidationError] = []
    genre = data.get("genre")
    structural_format = data.get("structural_format")
    level = data.get("level")
    is_multi_layer = data.get("is_multi_layer", False)

    # 5a: Genre ↔ structural_format
    genre_format_rules = {
        "nazm": ["verse"],
        "sharh": ["commentary", "prose"],
        "hashiyah": ["commentary"],
    }
    if genre in genre_format_rules:
        valid_formats = genre_format_rules[genre]
        if structural_format and structural_format not in valid_formats:
            errors.append(ValidationError(
                check="consistency_genre_format",
                severity="warning",
                field="structural_format",
                message=(
                    f"Genre '{genre}' expects format {valid_formats}, "
                    f"got '{structural_format}'"
                ),
                error_code="SRC_METADATA_INCONSISTENCY",
                recovery="flag_needs_review",
            ))

    # 5b: Level ↔ genre: hashiyah should not be beginner
    if genre == "hashiyah" and level == "beginner":
        errors.append(ValidationError(
            check="consistency_level_genre",
            severity="warning",
            field="level",
            message="Hashiyah (marginalia) should not be beginner level",
            error_code="SRC_METADATA_INCONSISTENCY",
            recovery="flag_needs_review",
        ))

    # 5c: Author ↔ science scope → HUMAN GATE (only consistency check that gates)
    if registries and "scholars" in registries:
        author = data.get("author", {})
        canonical_id = author.get("canonical_id") if isinstance(author, dict) else None
        science_scope = data.get("science_scope", [])

        if canonical_id and canonical_id in registries["scholars"]:
            scholar = registries["scholars"][canonical_id]
            school_affiliations = scholar.get("school_affiliations", {})
            if school_affiliations and science_scope:
                known_sciences = set(school_affiliations.keys())
                source_sciences = set(science_scope)
                if not known_sciences.intersection(source_sciences):
                    errors.append(ValidationError(
                        check="consistency_author_science",
                        severity="gate",
                        field="science_scope",
                        message=(
                            f"Author's known sciences {known_sciences} "
                            f"don't overlap with source sciences {source_sciences}"
                        ),
                        error_code="SRC_METADATA_INCONSISTENCY",
                        recovery="human_gate",
                    ))

    # 5d: Attribution ↔ prior sources
    # NOTE: prior_sources is not yet passed by engine.py — deferred to Phase D/E
    # when the library accumulates multiple sources per work. The check logic is
    # correct but has no callers yet.
    attribution = data.get("attribution_status")
    if (
        prior_sources
        and attribution in ("definitive", "traditional")
    ):
        for prior in prior_sources:
            prior_attr = prior.get("attribution_status")
            if prior_attr in ("disputed", "unknown"):
                errors.append(ValidationError(
                    check="consistency_attribution_prior",
                    severity="warning",
                    field="attribution_status",
                    message=(
                        f"Attribution '{attribution}' conflicts with "
                        f"prior source's '{prior_attr}' for same work"
                    ),
                    error_code="SRC_METADATA_INCONSISTENCY",
                    recovery="flag_needs_review",
                ))
                break

    # 5e: Genre ↔ multi-layer: sharh/hashiyah must be multi-layer
    if genre in ("sharh", "hashiyah") and not is_multi_layer:
        data["is_multi_layer"] = True  # Auto-correct in-place
        errors.append(ValidationError(
            check="consistency_genre_multi_layer",
            severity="warning",
            field="is_multi_layer",
            message=(
                f"Genre '{genre}' requires is_multi_layer=true — auto-corrected"
            ),
            error_code="SRC_METADATA_INCONSISTENCY",
            recovery="flag_needs_review",
        ))

    return errors


def _check_multi_layer_coherence(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]],
) -> list[ValidationError]:
    """Check 6: Multi-layer metadata coherence (6a-6c)."""
    errors: list[ValidationError] = []
    is_multi_layer = data.get("is_multi_layer", False)
    text_layers = data.get("text_layers", [])

    # 6a: is_multi_layer=true → text_layers must be non-empty
    if is_multi_layer and not text_layers:
        errors.append(ValidationError(
            check="multi_layer_empty_layers",
            severity="gate",
            field="text_layers",
            message=(
                "is_multi_layer=true but text_layers is empty — "
                "cannot determine layer attribution (T-2 prevention)"
            ),
            error_code="SRC_MULTI_LAYER_VIOLATION",
            recovery="human_gate",
        ))

    # 6b: is_multi_layer=false → text_layers must be empty
    if not is_multi_layer and text_layers:
        data["is_multi_layer"] = True  # Auto-correct
        errors.append(ValidationError(
            check="multi_layer_unexpected_layers",
            severity="warning",
            field="is_multi_layer",
            message="is_multi_layer=false but text_layers is non-empty — auto-corrected",
            error_code="SRC_METADATA_INCONSISTENCY",
            recovery="flag_needs_review",
        ))

    # 6c: Every TextLayer.author.canonical_id must resolve
    if registries and "scholars" in registries and text_layers:
        for i, layer in enumerate(text_layers):
            author = layer.get("author", {}) if isinstance(layer, dict) else {}
            layer_author_id = author.get("canonical_id") if isinstance(author, dict) else None
            if layer_author_id and layer_author_id not in registries["scholars"]:
                errors.append(ValidationError(
                    check="multi_layer_author_ref",
                    severity="fatal",
                    field=f"text_layers[{i}].author.canonical_id",
                    message=(
                        f"Layer {i} author '{layer_author_id}' "
                        f"not found in scholars registry"
                    ),
                    error_code="SRC_REGISTRY_CONFLICT",
                    recovery="abort",
                ))

    return errors
