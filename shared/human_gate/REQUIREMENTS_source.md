# Human Gate — Source Engine Requirements

**Component:** `shared/human_gate/`
**Consumer:** Source engine (Session 5), all downstream engines
**SPEC authority:** `engines/source/SPEC_CORE.md` §5 Layer 2, §7; `reference/KNOWLEDGE_INTEGRITY.md` Layer 4

---

## Purpose

The human gate system creates checkpoints when the pipeline encounters low-confidence decisions that require owner judgment. It captures the decision context, persists it for owner review, and records the owner's response. The owner has three options: "approve", "reject", or "unsure" — where "unsure" triggers elevated consensus (Layer 3.5: 3+ models must agree).

---

## Interface

### `create_checkpoint()`

```python
from dataclasses import dataclass, field
from typing import Any, Optional, Literal
from datetime import datetime, timezone


@dataclass
class HumanGateCheckpoint:
    """A checkpoint requiring owner review."""
    checkpoint_id: str          # Format: "hg_{8_hex_chars}" (UUID-derived)
    source_id: str              # Which source triggered this gate
    reason: str                 # Human-readable explanation of why review is needed
    gate_type: str              # HumanGateTrigger enum value (from contracts.py)
    context: dict[str, Any]     # All information the owner needs to make a decision
    created_utc: str            # ISO 8601 timestamp
    status: Literal["pending", "approved", "rejected", "unsure", "elevated", "auto_approved"]
    decision: Optional[str]     # Owner's decision once resolved
    resolved_utc: Optional[str] # When the owner resolved it
    elevated_result: Optional[dict] = None  # Layer 3.5 result if status was "unsure"


def create_checkpoint(
    source_id: str,
    reason: str,
    context: dict[str, Any],
    gate_type: str,
) -> str:
    """Create a human gate checkpoint.

    Parameters
    ----------
    source_id : str
        The source_id this checkpoint relates to. Used for batching
        (owner reviews all checkpoints for a source at once).
    reason : str
        Human-readable explanation. Examples:
        - "Author disambiguation: 'ابن حجر' could be al-Asqalani (d.852) or al-Haytami (d.974)"
        - "Consensus disagreement on author identification"
        - "Genre confidence 0.48 (below 0.50 threshold) — blocks metadata write"
    context : dict
        Decision context presented to the owner. Must include all information
        needed to make an informed decision. For consensus disagreements:
        {"model_a": {...}, "model_b": {...}, "fields_disagreed": [...]}
        For low-confidence fields:
        {"field": "genre", "value": "sharh", "confidence": 0.48, "alternatives": [...]}
    gate_type : str
        One of the 9 HumanGateTrigger enum values from contracts.py:
        AUTHOR_DISAMBIGUATION, WORK_MATCH_UNCERTAIN, LOW_CONFIDENCE_FIELD,
        TRUST_FLAGGED, CONSENSUS_DISAGREEMENT, GENRE_CHAIN_UNRESOLVED,
        AUTHOR_SCIENCE_MISMATCH, ENRICHMENT_CRITICAL_FIELD, SCHOLAR_CONFLICT

    Returns
    -------
    str
        The checkpoint_id. Format: "hg_{8_hex_chars}".

    Side Effects
    ------------
    Writes the checkpoint to the persistence store (JSON file).
    Logs the checkpoint creation to library/logs/source_engine.jsonl.
    """
```

### `resolve()`

```python
def resolve(
    checkpoint_id: str,
    decision: Literal["approve", "reject", "unsure"],
    notes: Optional[str] = None,
) -> HumanGateCheckpoint:
    """Resolve a human gate checkpoint.

    Parameters
    ----------
    checkpoint_id : str
        The checkpoint to resolve.
    decision : str
        One of three valid decisions:
        - "approve": Accept the inferred value. Processing continues.
        - "reject": Reject the inferred value. Source marked as needs_manual_classification.
          The owner can provide a corrected value in the notes field.
        - "unsure": Owner cannot verify. Triggers Layer 3.5 elevated consensus
          (3+ models must agree). See reference/KNOWLEDGE_INTEGRITY.md Layer 4.
    notes : str, optional
        Owner's notes. For "reject", may contain the corrected value.
        For "unsure", records why the owner couldn't verify.

    Returns
    -------
    HumanGateCheckpoint
        The updated checkpoint record.

    Behavior on "unsure"
    --------------------
    1. Checkpoint status → "elevated".
    2. Trigger Layer 3.5: re-run inference with 3+ models (add GPT-5.4 to the
       existing pair). Agreement requires all 3 to agree (same rules as §6).
    3. If 3-model consensus succeeds: checkpoint status → "approved" with
       elevated_result containing the consensus output. Processing continues.
    4. If 3-model consensus fails: checkpoint remains "elevated" with
       elevated_result containing the disagreement details.
       Owner is notified again with the new evidence.
    """
```

### `get_pending()`

```python
def get_pending(source_id: Optional[str] = None) -> list[HumanGateCheckpoint]:
    """Get all pending checkpoints, optionally filtered by source_id.

    Human gate reviews are batched: the owner reviews all pending checkpoints
    for a source at once, not one field at a time (SPEC §5 Layer 2).
    """
```

### `get_checkpoint()`

```python
def get_checkpoint(checkpoint_id: str) -> Optional[HumanGateCheckpoint]:
    """Retrieve a specific checkpoint by ID."""
```

---

## Persistence

**Storage format:** JSON files in `library/gates/`.

- `library/gates/pending/` — Unresolved checkpoints. One file per source: `{source_id}.json` containing a list of checkpoints for that source.
- `library/gates/resolved/` — Resolved checkpoints. Moved from pending/ after resolution.
- `library/gates/index.json` — Quick-lookup index: `{checkpoint_id: source_id}`.

**File format for pending/{source_id}.json:**
```json
{
  "source_id": "src_a7c3e91f",
  "checkpoints": [
    {
      "checkpoint_id": "hg_1a2b3c4d",
      "reason": "Author disambiguation confidence 0.72 (< 0.80)",
      "gate_type": "AUTHOR_DISAMBIGUATION",
      "context": { ... },
      "created_utc": "2026-03-09T12:00:00Z",
      "status": "pending",
      "decision": null,
      "resolved_utc": null,
      "elevated_result": null
    }
  ]
}
```

---

## Owner Interaction (MVP)

For the MVP build, the human gate operates in two modes:

**Mode 1: Auto-approve with logging (build/test phase).**
All checkpoints are created with full context but immediately auto-approved (`status: "auto_approved"`). This allows the pipeline to run end-to-end during testing. The auto-approval is logged so the owner can review retroactively.

**Mode 2: CLI review script (production).**
A CLI script (`scripts/review_gates.py`) presents pending checkpoints to the owner:
```
$ python scripts/review_gates.py

Source: src_a7c3e91f (أحكام الاضطباع والرمل في الطواف)
  Gate 1/2: AUTHOR_DISAMBIGUATION
    Reason: Author 'ابن حجر' could be:
      A) ابن حجر العسقلاني (d. 852 AH) — hadith scholar
      B) ابن حجر الهيتمي (d. 974 AH) — Shafi'i faqih
    [a]pprove A  [b]pprove B  [r]eject  [u]nsure  [s]kip > 
```

The interface must present: the inferred metadata with confidence scores, specific fields needing review, alternatives considered, and which model(s) produced which result.

**Critical design constraint:** The auto-approve mode must use the SAME code path as real review — only the decision source changes (automatic vs owner input). This ensures the real review workflow is tested during development.

---

## What the Owner CAN and CANNOT Verify

From reference/KNOWLEDGE_INTEGRITY.md Layer 4:

**CAN verify (experiential validation):**
- Is this the right book? (recognition)
- Is this the right author? (for well-known scholars)
- Coarse science classification (grammar vs fiqh vs aqidah)
- Utility check (does this make sense for study?)
- Preference decisions (edition choice, curriculum ordering)

**CANNOT verify (scholarly audit):**
- Precise death dates for lesser-known scholars
- Specific attribution disputes
- Isnad chain correctness
- Subtle taxonomic distinctions within a science

**Gate design implication:** Gates for content verification that exceed owner expertise should be pre-verified by Layer 3.5 (elevated consensus) before reaching the owner. The owner sees the automated verification result alongside the question.

---

## Cross-Engine Reuse

All downstream engines need human gates for their own uncertainty boundaries. The interface is generic:
- `source_id` can be reinterpreted as a general record identifier.
- `gate_type` uses strings (not a source-engine-specific enum), allowing each engine to define its own trigger types.
- `context` is a free-form dict, adaptable to any engine's decision context.

The normalization engine will need gates for: layer attribution uncertainty, ambiguous structural boundaries, and text corruption decisions.

---

## Invariants

1. **Human gates are not optional.** No automated process may auto-approve in production mode. Auto-approve is ONLY for build/test (reference/KNOWLEDGE_INTEGRITY.md Invariant 5).
2. **"Unsure" triggers elevation, not auto-approval.** The owner saying "unsure" never means "accept the default" — it means "I need more evidence" (reference/KNOWLEDGE_INTEGRITY.md Layer 4).
3. **Every checkpoint is persisted before processing continues.** If the process crashes between checkpoint creation and resolution, the checkpoint exists on disk for recovery.
4. **Resolved checkpoints are never deleted.** They move to `resolved/` for audit trail.
