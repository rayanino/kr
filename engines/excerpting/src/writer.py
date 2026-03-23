"""Output Writer: excerpts.jsonl + gate_queue.jsonl (SPEC §2.2.1).

Writes final ExcerptRecords and human gate entries to disk.
Output directory: library/sources/{source_id}/excerpts/
"""

from __future__ import annotations

import logging
from pathlib import Path

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingErrorCodes,
)

logger = logging.getLogger(__name__)


def write_excerpts(
    excerpts: list[ExcerptRecord],
    output_dir: Path,
) -> Path:
    """Write ExcerptRecords to excerpts.jsonl (§2.2.1).

    One ExcerptRecord per line, JSON-serialized with ensure_ascii=False
    to preserve Arabic text exactly.

    Returns the path to the written file.
    """
    raise NotImplementedError


def write_gate_queue(
    gate_entries: list[dict],
    output_dir: Path,
) -> Path:
    """Write human gate entries to gate_queue.jsonl (§2.2.1).

    Gate codes: EX-G-001 (attribution), EX-G-002 (dependent SC),
    EX-G-003 (school conflict).

    CRITICAL: If this write fails, emit EX-M-008 and HALT processing.
    Invisible uncertainty is more dangerous than a visible stop.

    Returns the path to the written file.
    """
    raise NotImplementedError


def write_processing_log(
    telemetry: dict,
    validation_results: list[dict],
    output_dir: Path,
) -> Path:
    """Write processing log with telemetry and validation results.

    Includes per-phase timing, token usage, error counts, and
    validation check results.
    """
    raise NotImplementedError
