"""Source Engine Logging — SPEC §7

Append-only log: library/logs/source_engine.jsonl
Every record is a SourceError model instance or event dict.

Logged: every intake attempt, duplicate detection, human gate creation,
enrichment write-back, registry update.

Alerts: fatal errors during batch, >10% same warning code, human gate queue > 20.
"""

from __future__ import annotations

import json
import logging
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engines.source.contracts import ErrorSeverity, SourceError
from shared.human_gate.src.human_gate import get_pending_count


class SourceEngineLogger:
    """Append-only JSONL writer with batch alert state.

    Each line in the log file is a JSON object with either:
    - {"type": "error", ...SourceError fields...}
    - {"type": "event", "timestamp": ..., "source_id": ..., "event": ..., "message": ...}
    """

    def __init__(self, log_path: Path | None = None) -> None:
        self._log_path = log_path or Path("library/logs/source_engine.jsonl")
        self._log_path.parent.mkdir(parents=True, exist_ok=True)

        # Batch alert state
        self._batch_error_codes: Counter[str] = Counter()
        self._batch_source_count: int = 0
        self._fatal_seen: bool = False
        self._batch_severity_counts: Counter[str] = Counter()

    def log_error(self, error: SourceError) -> None:
        """Log a SourceError to the JSONL file and update batch state."""
        record = {"type": "error"}
        record.update(error.model_dump(mode="json"))
        self._append(record)

        self._batch_error_codes[error.error_code.value] += 1
        self._batch_severity_counts[error.severity.value] += 1

        if error.severity == ErrorSeverity.FATAL:
            self._fatal_seen = True

    def log_event(
        self,
        event_type: str,
        source_id: str | None,
        message: str,
        context: dict[str, Any] | None = None,
    ) -> None:
        """Log a structured event to the JSONL file."""
        record: dict[str, Any] = {
            "type": "event",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "source_id": source_id,
            "event": event_type,
            "message": message,
        }
        if context:
            record["context"] = context

        self._append(record)

        if event_type == "intake_start":
            self._batch_source_count += 1

    def check_alerts(self) -> list[str]:
        """Check for alert conditions based on batch state."""
        alerts: list[str] = []

        if self._fatal_seen:
            alerts.append("ALERT: Fatal error during batch processing")

        if self._batch_source_count > 0:
            threshold = 0.10 * self._batch_source_count
            for code, count in self._batch_error_codes.items():
                if count > threshold:
                    alerts.append(f"ALERT: >10% of sources hit {code}")

        if get_pending_count() > 20:
            alerts.append("ALERT: Human gate queue exceeds 20")

        return alerts

    def get_batch_stats(self) -> dict[str, Any]:
        """Return current batch statistics."""
        return {
            "total_sources": self._batch_source_count,
            "fatal_seen": self._fatal_seen,
            "by_error_code": dict(self._batch_error_codes),
            "by_severity": dict(self._batch_severity_counts),
        }

    def reset_batch(self) -> None:
        """Reset all batch counters."""
        self._batch_error_codes = Counter()
        self._batch_source_count = 0
        self._fatal_seen = False
        self._batch_severity_counts = Counter()

    def _append(self, record: dict[str, Any]) -> None:
        """Append a JSON record as a single line. Never raises on I/O errors."""
        try:
            with self._log_path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
        except OSError as exc:
            # Logging should never crash the pipeline. Write to stderr as fallback.
            print(
                f"[SourceEngineLogger] Failed to write log: {exc}",
                file=sys.stderr,
            )
