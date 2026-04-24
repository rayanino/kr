from __future__ import annotations

from pathlib import Path
from typing import Literal, TypedDict, cast

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = PROJECT_ROOT / "engines" / "source" / "spec"

Severity = Literal["fatal", "blocking", "warning"]
RecoveryContract = Literal[
    "unrecoverable_corruption",
    "recoverable_rejection",
    "advisory",
]


class ErrorCondition(TypedDict):
    condition: str
    action: str
    severity: Severity


def _load_atom(atom_id: str) -> dict[str, object]:
    matches = [
        path
        for path in SPEC_ROOT.rglob(f"{atom_id}.yaml")
        if "views" not in path.parts
    ]
    assert len(matches) == 1, f"expected one atom file for {atom_id}, found {matches}"
    raw = yaml.safe_load(matches[0].read_text(encoding="utf-8"))
    assert isinstance(raw, dict)
    return cast(dict[str, object], raw)


def _acceptance_criterion(atom_id: str, ac_id: str) -> dict[str, object]:
    atom = _load_atom(atom_id)
    criteria = atom.get("acceptance_criteria")
    assert isinstance(criteria, list)
    for criterion in criteria:
        assert isinstance(criterion, dict)
        if criterion.get("id") == ac_id:
            return cast(dict[str, object], criterion)
    raise AssertionError(f"{atom_id} {ac_id} not found")


def _error_condition(atom_id: str, error_code: str) -> ErrorCondition:
    atom = _load_atom(atom_id)
    behavior = atom.get("behavior")
    assert isinstance(behavior, dict)
    conditions = behavior.get("error_conditions")
    assert isinstance(conditions, list)
    for item in conditions:
        assert isinstance(item, dict)
        condition = item.get("condition")
        action = item.get("action")
        severity = item.get("severity")
        assert isinstance(condition, str)
        assert isinstance(action, str)
        if error_code not in f"{condition} {action}":
            continue
        assert severity in ("fatal", "blocking", "warning")
        return {
            "condition": condition,
            "action": action,
            "severity": cast(Severity, severity),
        }
    raise AssertionError(f"{atom_id} does not define {error_code}")


def _expected_severity(contract: RecoveryContract) -> Severity:
    if contract == "unrecoverable_corruption":
        return "fatal"
    if contract == "recoverable_rejection":
        return "blocking"
    return "warning"


def _taxonomy_accepts(authored: Severity, contract: RecoveryContract) -> bool:
    return authored == _expected_severity(contract)


@pytest.mark.spec("CON-SRC-0012", "AC-1")
def test_con_src_0012_ac1_accepts_fatal_for_unrecoverable_corruption() -> None:
    """Fatal is accepted for unrecoverable corruption examples."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-1")
    assert criterion["test_type"] == "deterministic"

    examples = (
        ("REQ-SRC-0023", "SRC-E-PDF-TEXT-EVIDENCE-MUTATED"),
        ("REQ-SRC-0018", "SRC-E-FREEZE-VERIFY"),
    )
    for atom_id, error_code in examples:
        error = _error_condition(atom_id, error_code)
        assert error["action"].startswith("Abort")
        assert _taxonomy_accepts(error["severity"], "unrecoverable_corruption")


@pytest.mark.spec("CON-SRC-0012", "AC-2")
def test_con_src_0012_ac2_accepts_blocking_for_correction_path() -> None:
    """Blocking is accepted for a recoverable owner-correction path."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-2")
    assert criterion["test_type"] == "deterministic"

    error = _error_condition("REQ-SRC-0047", "SRC-E-LEVEL-OVERRIDE-NONAPPLICABLE")

    assert error["action"].startswith("Reject the override")
    assert "intake_analysis continues" in error["action"]
    assert _taxonomy_accepts(error["severity"], "recoverable_rejection")


@pytest.mark.spec("CON-SRC-0012", "AC-3")
def test_con_src_0012_ac3_accepts_warning_for_advisory_condition() -> None:
    """Warning is accepted for a non-halting advisory condition."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-3")
    assert criterion["test_type"] == "deterministic"

    error = _error_condition("REQ-SRC-0041", "SRC-W-MIXED-FORMAT")

    assert error["action"] == (
        "Classify as mixed_format_directory and emit warning SRC-W-MIXED-FORMAT."
    )
    assert _taxonomy_accepts(error["severity"], "advisory")


@pytest.mark.spec("CON-SRC-0012", "AC-4")
def test_con_src_0012_ac4_rejects_fatal_when_owner_correction_exists() -> None:
    """Fatal is rejected when the action has a clear correction path."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-4")
    assert criterion["test_type"] == "deterministic"

    authored: Severity = "fatal"
    expected = _expected_severity("recoverable_rejection")

    assert expected == "blocking"
    assert not _taxonomy_accepts(authored, "recoverable_rejection")


@pytest.mark.spec("CON-SRC-0012", "AC-5")
def test_con_src_0012_ac5_rejects_blocking_for_log_and_continue() -> None:
    """Blocking is rejected for non-halting log-and-continue actions."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-5")
    assert criterion["test_type"] == "deterministic"

    authored: Severity = "blocking"
    expected = _expected_severity("advisory")

    assert expected == "warning"
    assert not _taxonomy_accepts(authored, "advisory")


@pytest.mark.spec("CON-SRC-0012", "AC-6")
def test_con_src_0012_ac6_rejects_warning_for_primary_text_mutation() -> None:
    """Warning is rejected for byte-level primary-text mutation."""
    criterion = _acceptance_criterion("CON-SRC-0012", "AC-6")
    assert criterion["test_type"] == "deterministic"

    canonical = _error_condition("REQ-SRC-0023", "SRC-E-PDF-TEXT-EVIDENCE-MUTATED")
    authored: Severity = "warning"
    expected = _expected_severity("unrecoverable_corruption")

    assert canonical["severity"] == "fatal"
    assert expected == "fatal"
    assert not _taxonomy_accepts(authored, "unrecoverable_corruption")
