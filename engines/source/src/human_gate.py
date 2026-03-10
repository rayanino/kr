"""Source Engine Human Gate Wrapper — SPEC §5 Layer 2

Thin wrapper around shared/human_gate that maps source-engine-specific
triggers and context to the generic human gate interface.

Batches checkpoints per source. Provides convenience functions for
6 source-engine trigger types (remaining 3 are created by other modules).
"""

from __future__ import annotations

from typing import Any

from engines.source.contracts import HumanGateCheckpoint, HumanGateTrigger
from shared.human_gate.src.human_gate import create_checkpoint


def gate_author_disambiguation(
    source_id: str,
    candidates: list[dict[str, Any]],
    match_score: float,
    inferred_name: str,
) -> HumanGateCheckpoint:
    """Create AUTHOR_DISAMBIGUATION gate.

    SPEC §5 Layer 2: 'Author disambiguation with confidence < 0.80'
    """
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.AUTHOR_DISAMBIGUATION,
        trigger_detail=(
            f"Author '{inferred_name}' has ambiguous matches "
            f"(best score: {match_score:.3f})"
        ),
        fields_to_review=["author"],
        current_values={
            "inferred_name": inferred_name,
            "match_score": match_score,
        },
        alternatives=candidates,
    )


def gate_consensus_disagreement(
    source_id: str,
    field: str,
    model_a_value: Any,
    model_b_value: Any,
    model_a_name: str,
    model_b_name: str,
) -> HumanGateCheckpoint:
    """Create CONSENSUS_DISAGREEMENT gate.

    SPEC §5 Layer 2: 'Multi-model consensus disagreement on author
    identification, work matching, or attribution status'
    """
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.CONSENSUS_DISAGREEMENT,
        trigger_detail=(
            f"Models disagree on '{field}': "
            f"{model_a_name}='{model_a_value}' vs {model_b_name}='{model_b_value}'"
        ),
        fields_to_review=[field],
        current_values={
            "field": field,
            f"{model_a_name}_value": model_a_value,
            f"{model_b_name}_value": model_b_value,
        },
    )


def gate_low_confidence(
    source_id: str,
    field: str,
    value: Any,
    confidence: float,
) -> HumanGateCheckpoint:
    """Create LOW_CONFIDENCE_FIELD gate.

    SPEC §5 Layer 2: 'Any critical field with confidence < 0.70'
    """
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.LOW_CONFIDENCE_FIELD,
        trigger_detail=(
            f"Field '{field}' has low confidence: {confidence:.3f}"
        ),
        fields_to_review=[field],
        current_values={
            "field": field,
            "value": value,
            "confidence": confidence,
        },
    )


def gate_trust_flagged(
    source_id: str,
    trust_score: float,
    trust_factors: list[dict],
) -> HumanGateCheckpoint:
    """Create TRUST_FLAGGED gate.

    SPEC §5 Layer 2: 'Trust evaluation resulting in flagged (owner may override)'
    """
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.TRUST_FLAGGED,
        trigger_detail=(
            f"Source flagged with trust score {trust_score:.3f} (< 0.65)"
        ),
        fields_to_review=["trust_tier", "trust_score"],
        current_values={
            "trust_score": trust_score,
            "trust_factors": trust_factors,
        },
    )


def gate_author_science_mismatch(
    source_id: str,
    author_sciences: list[str],
    source_sciences: list[str],
    detail: str,
) -> HumanGateCheckpoint:
    """Create AUTHOR_SCIENCE_MISMATCH gate."""
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.AUTHOR_SCIENCE_MISMATCH,
        trigger_detail=detail,
        fields_to_review=["science_scope", "author"],
        current_values={
            "author_sciences": author_sciences,
            "source_sciences": source_sciences,
        },
    )


def gate_scholar_conflict(
    source_id: str,
    canonical_id: str,
    conflict_type: str,
    existing_value: Any,
    proposed_value: Any,
) -> HumanGateCheckpoint:
    """Create SCHOLAR_CONFLICT gate.

    SPEC §4.A.5: Scholar record consistency check violations
    (death date drift, school affiliation change, temporal inconsistency)
    """
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.SCHOLAR_CONFLICT,
        trigger_detail=(
            f"Scholar {canonical_id} conflict: {conflict_type} — "
            f"existing='{existing_value}', proposed='{proposed_value}'"
        ),
        fields_to_review=[conflict_type],
        current_values={
            "canonical_id": canonical_id,
            "conflict_type": conflict_type,
            "existing_value": existing_value,
            "proposed_value": proposed_value,
        },
    )
