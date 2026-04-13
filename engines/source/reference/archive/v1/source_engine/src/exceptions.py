"""Source Engine Exceptions — structured error handling.

All source engine modules raise SourceEngineError, which wraps the
SourceError Pydantic model from contracts.py. This provides both
Python exception semantics (try/except) and structured error data
(error code, severity, recovery action) for logging and reporting.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from engines.source.contracts import ErrorCode, ErrorSeverity, SourceError


class SourceEngineError(Exception):
    """Exception wrapping a structured SourceError Pydantic model.

    Raised by all source engine modules. The .error attribute contains
    the full SourceError record for logging to source_engine.jsonl.
    """

    def __init__(self, error: SourceError) -> None:
        self.error = error
        super().__init__(error.message)


def make_error(
    error_code: ErrorCode,
    message: str,
    severity: ErrorSeverity = ErrorSeverity.FATAL,
    source_id: str | None = None,
    recovery_action: Literal[
        "rejected",
        "human_gate_created",
        "field_flagged",
        "skipped",
        "retry_scheduled",
    ] = "rejected",
    context: dict[str, Any] | None = None,
) -> SourceEngineError:
    """Create a SourceEngineError with timestamp and structured metadata.

    Args:
        error_code: One of the ErrorCode enum values.
        message: Human-readable error description.
        severity: FATAL, WARNING, or INFO.
        source_id: Source being processed, if known.
        recovery_action: What the engine did in response.
        context: Additional structured data for debugging.

    Returns:
        A SourceEngineError ready to raise.
    """
    error = SourceError(
        timestamp=datetime.now(timezone.utc).isoformat(),
        source_id=source_id,
        error_code=error_code,
        severity=severity,
        message=message,
        recovery_action=recovery_action,
        context=context,
    )
    return SourceEngineError(error)
