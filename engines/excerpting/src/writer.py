"""Output Writer: excerpts.jsonl + gate_queue.jsonl (SPEC §2.2.1).

Writes final ExcerptRecords and human gate entries to disk.
Output directory: library/sources/{source_id}/excerpts/

DD-S5-2: JSONL via Pydantic model_dump(mode="json") + json.dumps(ensure_ascii=False).
DD-S5-3: Gate queue verification reads back the file (paranoid by design).
DD-S5-4: EX-M-008 halts processing (invisible uncertainty > visible stop).
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingErrorCodes,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Function 1: write_excerpts
# ═══════════════════════════════════════════════════════════════════


def write_excerpts(
    excerpts: list[ExcerptRecord],
    output_dir: Path,
) -> Path:
    """Write ExcerptRecords to excerpts.jsonl (§2.2.1).

    One JSON line per record. Records ordered by div_id, chunk_index,
    unit_index (preserves reading order).
    Encoding: UTF-8, no BOM, \\n line separator.
    ensure_ascii=False preserves Arabic characters without escaping.

    Returns the path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "excerpts.jsonl"

    # Sort by reading order: div_id (string), chunk_index (int), unit_index (int)
    sorted_excerpts = sorted(
        excerpts,
        key=lambda e: (e.div_id, e.chunk_index, e.unit_index),
    )

    with open(output_path, "w", encoding="utf-8") as f:
        for exc in sorted_excerpts:
            line = json.dumps(
                exc.model_dump(mode="json"),
                ensure_ascii=False,
            )
            f.write(line + "\n")

    logger.info(
        "Wrote %d excerpts to %s",
        len(sorted_excerpts),
        output_path,
    )
    return output_path


# ═══════════════════════════════════════════════════════════════════
# Function 2: write_gate_queue
# ═══════════════════════════════════════════════════════════════════


def write_gate_queue(
    gate_entries: list[dict[str, object]],
    output_dir: Path,
) -> Path:
    """Write human gate entries to gate_queue.jsonl (§2.2.1).

    One JSON line per gate entry. Present only if at least one gate
    was triggered.

    Returns the path to the written file.
    """
    if not gate_entries:
        logger.info("No gate entries — skipping gate_queue.jsonl creation.")
        return output_dir / "gate_queue.jsonl"

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "gate_queue.jsonl"

    with open(output_path, "w", encoding="utf-8") as f:
        for entry in gate_entries:
            line = json.dumps(entry, ensure_ascii=False)
            f.write(line + "\n")

    logger.info(
        "Wrote %d gate entries to %s",
        len(gate_entries),
        output_path,
    )
    return output_path


# ═══════════════════════════════════════════════════════════════════
# Function 3: verify_gate_queue (V-P3-7)
# ═══════════════════════════════════════════════════════════════════


class GateQueueVerificationError(Exception):
    """Raised when gate queue verification fails (EX-M-008).

    CRITICAL: This means uncertainty has become invisible.
    Processing MUST halt.
    """


def verify_gate_queue(
    gate_entries: list[dict[str, object]],
    gate_path: Path,
) -> list[str]:
    """V-P3-7: Read back gate_queue.jsonl and verify each expected entry exists.

    Paranoid verification: write → read back → compare.
    Catches filesystem failures, encoding issues, partial writes.

    Returns list of emitted error codes (empty if all good).
    Raises GateQueueVerificationError if any entry is missing (EX-M-008).
    """
    if not gate_entries:
        return []

    errors: list[str] = []

    # Read back the file
    if not gate_path.exists():
        logger.critical(
            "%s: Gate queue file does not exist at %s despite writing %d entries.",
            ExcerptingErrorCodes.EX_M_008,
            gate_path,
            len(gate_entries),
        )
        raise GateQueueVerificationError(
            f"{ExcerptingErrorCodes.EX_M_008}: Gate queue file missing at {gate_path}. "
            f"Expected {len(gate_entries)} entries. "
            "Invisible uncertainty — halting processing."
        )

    def _find_missing(path: Path) -> list[tuple[str, str]]:
        """Read gate_queue.jsonl and return (excerpt_id, gate_code) pairs not found."""
        written_entries: list[dict[str, object]] = []
        with open(path, "r", encoding="utf-8") as f:
            for line_num, raw_line in enumerate(f, 1):
                raw_line = raw_line.strip()
                if not raw_line:
                    continue
                try:
                    written_entries.append(json.loads(raw_line))
                except json.JSONDecodeError as e:
                    logger.error(
                        "Corrupt gate queue entry at line %d: %s",
                        line_num,
                        e,
                    )

        written_keys: set[tuple[str, str]] = set()
        for entry in written_entries:
            eid = str(entry.get("excerpt_id", ""))
            code = str(entry.get("gate_code", ""))
            if eid and code:
                written_keys.add((eid, code))

        result: list[tuple[str, str]] = []
        for entry in gate_entries:
            eid = str(entry.get("excerpt_id", ""))
            code = str(entry.get("gate_code", ""))
            if (eid, code) not in written_keys:
                result.append((eid, code))
        return result

    missing = _find_missing(gate_path)

    if missing:
        # SPEC §8.1 EX-M-008 recovery: "Retry write. If retry fails, halt."
        logger.warning(
            "V-P3-7: %d missing entries — retrying write + verify.",
            len(missing),
        )
        write_gate_queue(gate_entries, gate_path.parent)
        missing = _find_missing(gate_path)

    if missing:
        errors.append(ExcerptingErrorCodes.EX_M_008)
        logger.critical(
            "%s: %d gate entries missing after retry verification: %s",
            ExcerptingErrorCodes.EX_M_008,
            len(missing),
            missing,
        )
        raise GateQueueVerificationError(
            f"{ExcerptingErrorCodes.EX_M_008}: {len(missing)} gate entries "
            f"not found in {gate_path} after retry: {missing}. "
            "Invisible uncertainty — halting processing."
        )

    logger.info(
        "V-P3-7: Gate queue verified — all %d entries present in %s.",
        len(gate_entries),
        gate_path,
    )
    return errors
