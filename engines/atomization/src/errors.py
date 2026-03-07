"""Atomization Engine — Error Handling.

Implements SPEC §7: Error codes, severity levels, logging.

Uses contracts.py AtomizationErrorCode enum (22 codes) and ERROR_SEVERITY map.
All errors logged to library/sources/{source_id}/atoms/atomization_log.jsonl
with: timestamp, error_code, passage_id, atom_id (if applicable), details,
and recovery action taken.

Fatal errors additionally update the source's processing status.
Principle: never lose data silently (D-033).
"""

from __future__ import annotations


def log_error(source_id: str, error_code: str, passage_id: str,
              atom_id: str | None, details: str, recovery: str) -> None:
    """Append a structured error record to the atomization log.

    Every error, warning, and info message goes through this function.
    Fatal errors also trigger a source processing status update.
    """
    raise NotImplementedError


def log_warning(source_id: str, error_code: str, passage_id: str,
                details: str) -> None:
    """Convenience wrapper for warning-severity errors."""
    raise NotImplementedError
