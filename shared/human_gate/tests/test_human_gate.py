"""Tests for human gate checkpoint system — SPEC §5 Layer 2.

Tests 51–58 from session5-test-plan.md.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from engines.source.contracts import HumanGateTrigger
from shared.human_gate.src.human_gate import (
    configure,
    create_checkpoint,
    get_checkpoint,
    get_pending,
    get_pending_count,
    resolve,
)


@pytest.fixture(autouse=True)
def _setup_gates(tmp_path: Path) -> None:
    """Configure human gate with temp directory for each test."""
    gates_dir = tmp_path / "gates"
    gates_dir.mkdir()
    (gates_dir / "pending").mkdir()
    (gates_dir / "resolved").mkdir()
    configure(gates_dir=gates_dir, auto_approve=False)


def _create_test_checkpoint(source_id: str = "src_abc12345"):
    """Helper to create a checkpoint for testing."""
    return create_checkpoint(
        source_id=source_id,
        trigger=HumanGateTrigger.AUTHOR_DISAMBIGUATION,
        trigger_detail="Author 'ابن حجر' matches multiple scholars",
        fields_to_review=["author.canonical_id"],
        current_values={"author.canonical_id": "sch_00001"},
        alternatives=[{"author.canonical_id": "sch_00042"}],
    )


class TestHumanGate:
    """Tests 51–58: Human gate checkpoint CRUD."""

    def test_51_create_checkpoint_persists(self) -> None:
        """Test 51: Created checkpoint is persisted and retrievable."""
        cp = _create_test_checkpoint()
        assert cp.checkpoint_id.startswith("hg_")
        assert len(cp.checkpoint_id) == 11  # "hg_" + 8 hex chars
        assert cp.status == "pending"

        retrieved = get_checkpoint(cp.checkpoint_id)
        assert retrieved is not None
        assert retrieved.checkpoint_id == cp.checkpoint_id

    def test_52_auto_approve_sets_status(self, tmp_path: Path) -> None:
        """Test 52: Auto-approve mode sets status=auto_approved."""
        gates_dir = tmp_path / "gates_auto"
        gates_dir.mkdir()
        (gates_dir / "pending").mkdir()
        (gates_dir / "resolved").mkdir()
        configure(gates_dir=gates_dir, auto_approve=True)

        cp = _create_test_checkpoint()
        assert cp.status == "auto_approved"

        # Verify it went through the full code path — now in resolved/
        retrieved = get_checkpoint(cp.checkpoint_id)
        assert retrieved is not None
        assert retrieved.status == "auto_approved"

    def test_53_approved_moves_to_resolved(self) -> None:
        """Test 53: Approved checkpoint moves from pending/ to resolved/."""
        cp = _create_test_checkpoint()
        assert get_pending_count() == 1

        resolved_cp = resolve(cp.checkpoint_id, "approve", notes="Looks correct")
        assert resolved_cp.status == "approved"
        assert resolved_cp.resolved_at is not None

        # No longer pending
        assert get_pending_count() == 0

        # Still retrievable via get_checkpoint (now from resolved/)
        retrieved = get_checkpoint(cp.checkpoint_id)
        assert retrieved is not None
        assert retrieved.status == "approved"

    def test_54_rejected_marked(self) -> None:
        """Test 54: Rejected checkpoint marked correctly."""
        cp = _create_test_checkpoint()
        resolved_cp = resolve(cp.checkpoint_id, "reject", notes="Wrong author")
        assert resolved_cp.status == "rejected"
        assert get_pending_count() == 0

    def test_55_filters_by_source_id(self) -> None:
        """Test 55: get_pending filters by source_id."""
        _create_test_checkpoint("src_aaa11111")
        _create_test_checkpoint("src_aaa11111")
        _create_test_checkpoint("src_bbb22222")

        pending_a = get_pending("src_aaa11111")
        assert len(pending_a) == 2

        pending_b = get_pending("src_bbb22222")
        assert len(pending_b) == 1

    def test_56_count_accuracy(self) -> None:
        """Test 56: Pending count is accurate across sources."""
        _create_test_checkpoint("src_aaa11111")
        _create_test_checkpoint("src_bbb22222")
        _create_test_checkpoint("src_bbb22222")

        assert get_pending_count() == 3

    def test_57_index_json_mapping(self) -> None:
        """Test 57: index.json maps checkpoint_id → source_id."""
        cp = _create_test_checkpoint("src_xyz99999")

        # Verify we can find it by ID
        retrieved = get_checkpoint(cp.checkpoint_id)
        assert retrieved is not None
        assert retrieved.source_id == "src_xyz99999"

    def test_58_multiple_gates_per_source(self) -> None:
        """Test 58: Multiple gates for same source stored in same file."""
        cp1 = create_checkpoint(
            source_id="src_multi",
            trigger=HumanGateTrigger.AUTHOR_DISAMBIGUATION,
            trigger_detail="Author ambiguous",
            fields_to_review=["author.canonical_id"],
            current_values={"author.canonical_id": "sch_00001"},
        )
        cp2 = create_checkpoint(
            source_id="src_multi",
            trigger=HumanGateTrigger.LOW_CONFIDENCE_FIELD,
            trigger_detail="Genre confidence low",
            fields_to_review=["genre"],
            current_values={"genre": "risalah"},
        )

        pending = get_pending("src_multi")
        assert len(pending) == 2
        ids = {p.checkpoint_id for p in pending}
        assert cp1.checkpoint_id in ids
        assert cp2.checkpoint_id in ids


class TestUnsureElevation:
    """Unsure → elevated (Layer 3.5 placeholder)."""

    def test_unsure_sets_elevated_status(self) -> None:
        """'Unsure' decision sets status to 'elevated', not auto-approved."""
        cp = _create_test_checkpoint()
        elevated = resolve(cp.checkpoint_id, "unsure", notes="Not sure about this")
        assert elevated.status == "elevated"
