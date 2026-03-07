"""Passaging Engine — Error Handling Utilities.

Implements SPEC §7 error handling patterns.

All errors logged with: error code, severity, source_id, timestamp,
affected passage_ids, human-readable description.

Principle: never lose data silently. An unhandled error that corrupts
the library is worse than a visible failure that stops processing.
"""

from __future__ import annotations

from engines.passaging.contracts import ErrorSeverity, PassagingErrorCode, ERROR_SEVERITY


class PassagingError(Exception):
    """Base exception for passaging engine errors."""

    def __init__(self, code: PassagingErrorCode, message: str, source_id: str = "",
                 passage_ids: list[str] | None = None):
        self.code = code
        self.severity = ERROR_SEVERITY[code]
        self.message = message
        self.source_id = source_id
        self.passage_ids = passage_ids or []
        super().__init__(f"[{code.value}] {message}")


class PassagingFatalError(PassagingError):
    """Fatal error — processing must abort, passage stream not written."""
    pass


class PassagingWarning(PassagingError):
    """Warning — processing continues, issue logged and flagged."""
    pass
