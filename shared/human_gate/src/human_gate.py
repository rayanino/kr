"""Human Gate Checkpoint System — SPEC §5 Layer 2, KNOWLEDGE_INTEGRITY.md Layer 4

Creates, persists, retrieves, and resolves human gate checkpoints.
Checkpoints are batched per source for owner review.

Storage:
- library/gates/pending/{source_id}.json — unresolved checkpoints
- library/gates/resolved/{source_id}.json — resolved checkpoints (audit trail)
- library/gates/index.json — quick-lookup: checkpoint_id → source_id

Two modes:
- auto_approve=True (build/test): checkpoints are created with full context
  but immediately auto-approved. Uses the SAME code path as real review.
- auto_approve=False (production): checkpoints stay pending until owner resolves.

Invariants (KNOWLEDGE_INTEGRITY.md):
1. Human gates are not optional in production.
2. 'Unsure' triggers elevation, not auto-approval.
3. Every checkpoint is persisted before processing continues.
4. Resolved checkpoints are never deleted — moved to resolved/.
"""

from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

from engines.source.contracts import HumanGateCheckpoint, HumanGateTrigger


# Module-level configuration
_GATES_DIR = Path("library/gates")
_AUTO_APPROVE = True  # Set to False for production


def configure(gates_dir: Path = Path("library/gates"), auto_approve: bool = True) -> None:
    """Configure the human gate module.
    
    Args:
        gates_dir: Base directory for gate persistence.
        auto_approve: If True, all checkpoints are immediately auto-approved.
                      ONLY for build/test. Production requires False.
    """
    raise NotImplementedError


def create_checkpoint(
    source_id: str,
    trigger: HumanGateTrigger,
    trigger_detail: str,
    fields_to_review: list[str],
    current_values: dict[str, Any],
    alternatives: Optional[list[dict[str, Any]]] = None,
) -> HumanGateCheckpoint:
    """Create a human gate checkpoint.
    
    SPEC §5 Layer 2: creates a checkpoint when the pipeline encounters
    a low-confidence decision requiring owner judgment.
    
    Args:
        source_id: Which source triggered this gate. Used for batching.
        trigger: One of the 9 HumanGateTrigger enum values.
        trigger_detail: Human-readable explanation.
        fields_to_review: List of field names needing review.
        current_values: Field name → current inferred value.
        alternatives: Optional list of alternative value dicts considered.
    
    Returns:
        HumanGateCheckpoint with checkpoint_id assigned (format: hg_{8_hex_chars}).
        
    Side effects:
        - Persists checkpoint to library/gates/pending/{source_id}.json.
        - Updates library/gates/index.json.
        - If auto_approve=True: immediately sets status='auto_approved'.
    """
    raise NotImplementedError


def resolve(
    checkpoint_id: str,
    decision: Literal["approve", "reject", "unsure"],
    notes: Optional[str] = None,
) -> HumanGateCheckpoint:
    """Resolve a human gate checkpoint.
    
    Args:
        checkpoint_id: The checkpoint to resolve.
        decision:
            - 'approve': Accept the inferred value. Processing continues.
            - 'reject': Reject. Source marked needs_manual_classification.
            - 'unsure': Triggers Layer 3.5 elevated consensus (3+ models).
        notes: Owner's notes. For 'reject', may contain corrected value.
    
    Returns:
        Updated HumanGateCheckpoint.
    """
    raise NotImplementedError


def get_pending(source_id: Optional[str] = None) -> list[HumanGateCheckpoint]:
    """Get all pending checkpoints, optionally filtered by source_id."""
    raise NotImplementedError


def get_checkpoint(checkpoint_id: str) -> Optional[HumanGateCheckpoint]:
    """Retrieve a specific checkpoint by ID. Checks both pending and resolved."""
    raise NotImplementedError


def get_pending_count() -> int:
    """Count total pending checkpoints. Alert trigger when > 20."""
    raise NotImplementedError
