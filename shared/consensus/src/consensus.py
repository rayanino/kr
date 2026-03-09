"""Consensus stub — tracer bullet.

Returns hardcoded agreement for all tasks. Real implementation
will use multi-model evaluation with configurable thresholds.
"""

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class ConsensusResult:
    agreed: bool
    value: Any
    agreement_ratio: float
    model_responses: list[dict]
    dissenting_models: list[str]


def evaluate(
    task: str,
    prompt: str,
    candidates: Optional[list[Any]] = None,
    models: Optional[list[str]] = None,
    threshold: float = 0.67,
) -> ConsensusResult:
    """Evaluate a task with multi-model consensus.
    
    Tracer bullet stub: returns hardcoded agreement with the first
    candidate (or a placeholder value).
    """
    value = candidates[0] if candidates else "consensus_placeholder"
    return ConsensusResult(
        agreed=True,
        value=value,
        agreement_ratio=1.0,
        model_responses=[{"model": "stub", "response": value}],
        dissenting_models=[],
    )
