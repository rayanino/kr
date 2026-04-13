"""Tests for SourceEngineLogger — SPEC §7 structured logging.

7 tests verifying JSONL format, append-only behavior, and batch alerts.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from engines.source.contracts import ErrorCode, ErrorSeverity, SourceError
from engines.source.src.logger import SourceEngineLogger


@pytest.fixture
def logger(tmp_path: Path) -> SourceEngineLogger:
    log_path = tmp_path / "logs" / "source_engine.jsonl"
    return SourceEngineLogger(log_path=log_path)


def _make_error(
    code: ErrorCode = ErrorCode.EMPTY_INPUT,
    severity: ErrorSeverity = ErrorSeverity.FATAL,
    source_id: str | None = "src_test1234",
    message: str = "test error",
) -> SourceError:
    return SourceError(
        timestamp="2026-03-10T10:00:00+00:00",
        source_id=source_id,
        error_code=code,
        severity=severity,
        message=message,
        recovery_action="rejected",
    )


def test_log_error_jsonl_format(logger: SourceEngineLogger, tmp_path: Path) -> None:
    """Log a SourceError, read back, verify JSON structure."""
    error = _make_error()
    logger.log_error(error)

    log_path = tmp_path / "logs" / "source_engine.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["type"] == "error"
    assert record["error_code"] == "SRC_EMPTY_INPUT"
    assert record["severity"] == "fatal"
    assert record["source_id"] == "src_test1234"
    assert record["message"] == "test error"


def test_log_event_jsonl_format(logger: SourceEngineLogger, tmp_path: Path) -> None:
    """Log an event, verify format."""
    logger.log_event("intake_start", "src_abc12345", "Starting intake", {"path": "/tmp/test"})

    log_path = tmp_path / "logs" / "source_engine.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 1

    record = json.loads(lines[0])
    assert record["type"] == "event"
    assert record["event"] == "intake_start"
    assert record["source_id"] == "src_abc12345"
    assert record["message"] == "Starting intake"
    assert record["context"]["path"] == "/tmp/test"
    assert "timestamp" in record


def test_append_only(logger: SourceEngineLogger, tmp_path: Path) -> None:
    """3 writes produce 3 lines."""
    logger.log_error(_make_error())
    logger.log_event("test_event", "src_1", "msg1")
    logger.log_error(_make_error(code=ErrorCode.DUPLICATE_EXACT))

    log_path = tmp_path / "logs" / "source_engine.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().split("\n")
    assert len(lines) == 3


def test_alert_fatal_during_batch(logger: SourceEngineLogger) -> None:
    """Fatal error triggers alert."""
    logger.log_event("intake_start", "src_1", "start")
    logger.log_error(_make_error(severity=ErrorSeverity.FATAL))

    with patch("engines.source.src.logger.get_pending_count", return_value=0):
        alerts = logger.check_alerts()

    assert any("Fatal error" in a for a in alerts)


def test_alert_same_warning_threshold(logger: SourceEngineLogger) -> None:
    """>10% of sources hitting the same error code triggers alert."""
    # Simulate 10 sources, 2 with same warning code (20% > 10%)
    for i in range(10):
        logger.log_event("intake_start", f"src_{i}", f"start {i}")

    logger.log_error(_make_error(code=ErrorCode.LOW_CONFIDENCE, severity=ErrorSeverity.WARNING))
    logger.log_error(_make_error(code=ErrorCode.LOW_CONFIDENCE, severity=ErrorSeverity.WARNING))

    with patch("engines.source.src.logger.get_pending_count", return_value=0):
        alerts = logger.check_alerts()

    assert any("SRC_LOW_CONFIDENCE" in a for a in alerts)


def test_alert_gate_queue_threshold(logger: SourceEngineLogger) -> None:
    """Mock get_pending_count → 25 triggers alert."""
    with patch("engines.source.src.logger.get_pending_count", return_value=25):
        alerts = logger.check_alerts()

    assert any("Human gate queue exceeds 20" in a for a in alerts)


def test_no_alerts_normal_operation(logger: SourceEngineLogger) -> None:
    """Normal batch → empty alerts."""
    for i in range(5):
        logger.log_event("intake_start", f"src_{i}", f"start {i}")

    with patch("engines.source.src.logger.get_pending_count", return_value=3):
        alerts = logger.check_alerts()

    assert alerts == []


def test_get_batch_stats(logger: SourceEngineLogger) -> None:
    """Verify batch stats tracking."""
    logger.log_event("intake_start", "src_1", "start")
    logger.log_event("intake_start", "src_2", "start")
    logger.log_error(_make_error(code=ErrorCode.LOW_CONFIDENCE, severity=ErrorSeverity.WARNING))

    stats = logger.get_batch_stats()
    assert stats["total_sources"] == 2
    assert stats["fatal_seen"] is False
    assert stats["by_error_code"]["SRC_LOW_CONFIDENCE"] == 1
    assert stats["by_severity"]["warning"] == 1


def test_reset_batch(logger: SourceEngineLogger) -> None:
    """Reset clears all counters."""
    logger.log_event("intake_start", "src_1", "start")
    logger.log_error(_make_error(severity=ErrorSeverity.FATAL))
    logger.reset_batch()

    stats = logger.get_batch_stats()
    assert stats["total_sources"] == 0
    assert stats["fatal_seen"] is False
    assert stats["by_error_code"] == {}
