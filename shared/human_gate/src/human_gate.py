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
import os
import tempfile
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional

from engines.source.contracts import HumanGateCheckpoint, HumanGateTrigger


# Module-level configuration
_GATES_DIR = Path("library/gates")
_AUTO_APPROVE = True  # Set to False for production


def configure(gates_dir: Path = Path("library/gates"), auto_approve: bool = True) -> None:
    """Configure the human gate module."""
    global _GATES_DIR, _AUTO_APPROVE
    _GATES_DIR = gates_dir
    _AUTO_APPROVE = auto_approve


def _atomic_json_write(path: Path, data: Any) -> None:
    """Write JSON atomically: temp file → fsync → os.replace."""
    path.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(data, ensure_ascii=False, indent=2)

    fd = tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, suffix=".tmp",
        delete=False, encoding="utf-8",
    )
    try:
        fd.write(content)
        fd.flush()
        os.fsync(fd.fileno())
        fd.close()
        os.replace(fd.name, str(path))
    except BaseException:
        fd.close()
        try:
            os.unlink(fd.name)
        except OSError:
            pass
        raise


def _load_json(path: Path) -> Any:
    """Load JSON file, return empty list/dict for missing files."""
    if not path.exists():
        return None
    raw = path.read_text(encoding="utf-8")
    if not raw.strip():
        return None
    return json.loads(raw)


def _load_index() -> dict[str, str]:
    """Load index.json: checkpoint_id → source_id."""
    data = _load_json(_GATES_DIR / "index.json")
    return data if isinstance(data, dict) else {}


def _save_index(index: dict[str, str]) -> None:
    """Save index.json atomically."""
    _atomic_json_write(_GATES_DIR / "index.json", index)


def _load_pending_for_source(source_id: str) -> list[dict]:
    """Load pending checkpoints for a specific source."""
    path = _GATES_DIR / "pending" / f"{source_id}.json"
    data = _load_json(path)
    return data if isinstance(data, list) else []


def _save_pending_for_source(source_id: str, checkpoints: list[dict]) -> None:
    """Save pending checkpoints for a source."""
    path = _GATES_DIR / "pending" / f"{source_id}.json"
    if not checkpoints:
        if path.exists():
            path.unlink()
        return
    _atomic_json_write(path, checkpoints)


def _load_resolved_for_source(source_id: str) -> list[dict]:
    """Load resolved checkpoints for a source."""
    path = _GATES_DIR / "resolved" / f"{source_id}.json"
    data = _load_json(path)
    return data if isinstance(data, list) else []


def _save_resolved_for_source(source_id: str, checkpoints: list[dict]) -> None:
    """Save resolved checkpoints for a source."""
    path = _GATES_DIR / "resolved" / f"{source_id}.json"
    _atomic_json_write(path, checkpoints)


def create_checkpoint(
    source_id: str,
    trigger: HumanGateTrigger,
    trigger_detail: str,
    fields_to_review: list[str],
    current_values: dict[str, Any],
    alternatives: Optional[list[dict[str, Any]]] = None,
) -> HumanGateCheckpoint:
    """Create a human gate checkpoint.

    If auto_approve=True, creates the checkpoint with the full code path
    then immediately resolves it with decision='approve'.
    """
    checkpoint_id = f"hg_{uuid.uuid4().hex[:8]}"
    now = datetime.now(timezone.utc).isoformat()

    checkpoint = HumanGateCheckpoint(
        checkpoint_id=checkpoint_id,
        source_id=source_id,
        trigger=trigger,
        trigger_detail=trigger_detail,
        fields_to_review=fields_to_review,
        current_values=current_values,
        alternatives=alternatives,
        created_at=now,
        status="pending",
    )

    # Persist to pending
    pending = _load_pending_for_source(source_id)
    pending.append(checkpoint.model_dump(mode="json"))
    _save_pending_for_source(source_id, pending)

    # Update index
    index = _load_index()
    index[checkpoint_id] = source_id
    _save_index(index)

    # Auto-approve uses the SAME resolve() code path
    if _AUTO_APPROVE:
        checkpoint = resolve(checkpoint_id, "approve", notes="auto_approved")

    return checkpoint


def resolve(
    checkpoint_id: str,
    decision: Literal["approve", "reject", "unsure"],
    notes: Optional[str] = None,
) -> HumanGateCheckpoint:
    """Resolve a human gate checkpoint.

    - 'approve': moves checkpoint from pending/ to resolved/
    - 'reject': moves checkpoint from pending/ to resolved/
    - 'unsure': sets status to 'elevated' (Layer 3.5 placeholder)
    """
    index = _load_index()
    if checkpoint_id not in index:
        raise KeyError(f"Checkpoint {checkpoint_id} not found in index")

    source_id = index[checkpoint_id]
    now = datetime.now(timezone.utc).isoformat()

    # Find in pending
    pending = _load_pending_for_source(source_id)
    found_idx = None
    for i, cp in enumerate(pending):
        if cp["checkpoint_id"] == checkpoint_id:
            found_idx = i
            break

    if found_idx is None:
        raise KeyError(f"Checkpoint {checkpoint_id} not found in pending for {source_id}")

    cp_data = pending[found_idx]

    # Determine status based on decision
    if decision == "unsure":
        status = "elevated"
    elif notes == "auto_approved":
        status = "auto_approved"
    else:
        status = decision + ("d" if decision == "approve" else "ed")

    cp_data["status"] = status
    cp_data["resolution"] = notes
    cp_data["resolved_at"] = now

    checkpoint = HumanGateCheckpoint.model_validate(cp_data)

    # Remove from pending
    pending.pop(found_idx)
    _save_pending_for_source(source_id, pending)

    # Add to resolved
    resolved = _load_resolved_for_source(source_id)
    resolved.append(checkpoint.model_dump(mode="json"))
    _save_resolved_for_source(source_id, resolved)

    return checkpoint


def get_pending(source_id: Optional[str] = None) -> list[HumanGateCheckpoint]:
    """Get all pending checkpoints, optionally filtered by source_id."""
    if source_id is not None:
        data = _load_pending_for_source(source_id)
        return [HumanGateCheckpoint.model_validate(cp) for cp in data]

    # Scan all pending files
    pending_dir = _GATES_DIR / "pending"
    if not pending_dir.exists():
        return []

    result: list[HumanGateCheckpoint] = []
    for f in pending_dir.iterdir():
        if f.suffix == ".json":
            data = _load_json(f)
            if isinstance(data, list):
                for cp in data:
                    result.append(HumanGateCheckpoint.model_validate(cp))
    return result


def get_checkpoint(checkpoint_id: str) -> Optional[HumanGateCheckpoint]:
    """Retrieve a specific checkpoint by ID. Checks both pending and resolved."""
    index = _load_index()
    if checkpoint_id not in index:
        return None

    source_id = index[checkpoint_id]

    # Check pending first
    for cp in _load_pending_for_source(source_id):
        if cp["checkpoint_id"] == checkpoint_id:
            return HumanGateCheckpoint.model_validate(cp)

    # Check resolved
    for cp in _load_resolved_for_source(source_id):
        if cp["checkpoint_id"] == checkpoint_id:
            return HumanGateCheckpoint.model_validate(cp)

    return None


def get_pending_count() -> int:
    """Count total pending checkpoints. Alert trigger when > 20."""
    pending_dir = _GATES_DIR / "pending"
    if not pending_dir.exists():
        return 0

    count = 0
    for f in pending_dir.iterdir():
        if f.suffix == ".json":
            data = _load_json(f)
            if isinstance(data, list):
                count += len(data)
    return count
