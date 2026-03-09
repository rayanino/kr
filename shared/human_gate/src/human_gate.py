"""Human gate stub — tracer bullet.

Auto-approves all checkpoints. Real implementation will present
decisions to the owner and block until resolved.
"""

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


_CHECKPOINT_LOG: list[dict] = []


def create_checkpoint(
    source_id: str,
    reason: str,
    context: Optional[dict[str, Any]] = None,
    gate_type: str = "general",
) -> str:
    """Create a human gate checkpoint.
    
    Tracer bullet stub: logs the checkpoint and auto-approves.
    Returns a checkpoint_id.
    """
    checkpoint_id = f"hg_{uuid.uuid4().hex[:8]}"
    record = {
        "checkpoint_id": checkpoint_id,
        "source_id": source_id,
        "reason": reason,
        "gate_type": gate_type,
        "context": context or {},
        "created_utc": datetime.now(timezone.utc).isoformat(),
        "status": "auto_approved",
        "decision": "approve",
    }
    _CHECKPOINT_LOG.append(record)
    return checkpoint_id


def get_log() -> list[dict]:
    """Return all checkpoint records (for debugging)."""
    return list(_CHECKPOINT_LOG)


def clear_log() -> None:
    """Clear the checkpoint log."""
    _CHECKPOINT_LOG.clear()
