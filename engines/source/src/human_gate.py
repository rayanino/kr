"""Source Engine Human Gate Wrapper — SPEC §5 Layer 2

Thin wrapper around shared/human_gate that maps source-engine-specific
triggers and context to the generic human gate interface.

Batches checkpoints per source. Provides convenience functions for
the 9 source-engine trigger types.
"""

from __future__ import annotations

from typing import Any, Optional

from engines.source.contracts import HumanGateCheckpoint, HumanGateTrigger


def gate_author_disambiguation(
    source_id: str,
    candidates: list[dict[str, Any]],
    match_score: float,
    inferred_name: str,
) -> HumanGateCheckpoint:
    """Create AUTHOR_DISAMBIGUATION gate.
    
    SPEC §5 Layer 2: 'Author disambiguation with confidence < 0.80'
    """
    raise NotImplementedError


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
    raise NotImplementedError


def gate_low_confidence(
    source_id: str,
    field: str,
    value: Any,
    confidence: float,
) -> HumanGateCheckpoint:
    """Create LOW_CONFIDENCE_FIELD gate.
    
    SPEC §5 Layer 2: 'Any critical field with confidence < 0.70'
    """
    raise NotImplementedError


def gate_trust_flagged(
    source_id: str,
    trust_score: float,
    trust_factors: list[dict],
) -> HumanGateCheckpoint:
    """Create TRUST_FLAGGED gate.
    
    SPEC §5 Layer 2: 'Trust evaluation resulting in flagged (owner may override)'
    """
    raise NotImplementedError


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
    raise NotImplementedError
