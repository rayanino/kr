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

from shared.validation.src.validation import (
    ValidationError,
    validate_schema,
    validate_referential_integrity,
    validate_enrichment_passthrough,
)
from engines.source.contracts import SourceMetadata


def validate_source_metadata(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]] = None,
    prior_sources: Optional[list[dict]] = None,
) -> list[ValidationError]:
    """Run all 6 Layer 1 checks on a SourceMetadata record.
    
    SPEC §5 Layer 1: 'Six checks run in order. Any failure aborts the write.'
    
    Args:
        data: The SourceMetadata as a dict (pre-serialization).
        registries: Optional dict with keys "scholars" and "works" for
                    referential integrity checks. If None, skips checks 2, 5c, 6c.
        prior_sources: Other SourceMetadata records for the same work_id,
                       for attribution_status cross-check (5d).
    
    Returns:
        list[ValidationError] — empty means valid.
    """
    raise NotImplementedError


def _check_confidence_thresholds(data: dict[str, Any]) -> list[ValidationError]:
    """Check 3: Confidence threshold check.
    
    SPEC §5 Layer 1 Check 3: 'If any critical inferred field has confidence
    < 0.50 → abort write → create human gate checkpoint.'
    
    Fields checked:
    - confidence_scores.author (author identity)
    - confidence_scores.genre (genre classification)
    - confidence_scores.science_scope (science scope)
    
    < 0.50 → severity=gate, recovery=human_gate, error_code=SRC_LOW_CONFIDENCE
    """
    raise NotImplementedError


def _check_duplicates(data: dict[str, Any], registries: dict[str, dict]) -> list[ValidationError]:
    """Check 4: Post-inference duplicate re-check.
    
    SPEC §5 Layer 1 Check 4: 'After inference (which may have changed title
    or author), re-run deduplication.'
    
    severity: warning
    recovery: flag_needs_review
    """
    raise NotImplementedError


def _check_consistency(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]],
    prior_sources: Optional[list[dict]],
) -> list[ValidationError]:
    """Check 5: Consistency cross-checks (5a-5e).
    
    SPEC §5 Layer 1 Check 5:
    5a. Genre ↔ structural_format: nazm→verse, sharh→commentary|prose, hashiyah→commentary
    5b. Level ↔ genre: hashiyah should not be beginner
    5c. Author ↔ science scope: mismatch → HUMAN GATE (SRC_METADATA_INCONSISTENCY)
    5d. Attribution ↔ prior: definitive/traditional vs prior disputed/unknown → warning
    5e. Genre ↔ multi-layer: sharh/hashiyah must be multi-layer (auto-correct if false)
    """
    raise NotImplementedError


def _check_multi_layer_coherence(
    data: dict[str, Any],
    registries: Optional[dict[str, dict]],
) -> list[ValidationError]:
    """Check 6: Multi-layer metadata coherence (6a-6c).
    
    SPEC §5 Layer 1 Check 6: Prevents T-2 Attribution Error.
    6a. is_multi_layer=true → text_layers must be non-empty (else GATE)
    6b. is_multi_layer=false → text_layers must be empty (else auto-correct)
    6c. Every TextLayer.author.canonical_id resolves in scholars.json (else FATAL)
    """
    raise NotImplementedError
