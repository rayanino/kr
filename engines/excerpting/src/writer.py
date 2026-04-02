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

from collections.abc import Mapping, Sequence
from pathlib import Path

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingErrorCodes,
)

logger = logging.getLogger(__name__)


class ResumeMergeError(RuntimeError):
    """Raised when an existing JSONL file is corrupt during resume merge."""


def _validate_gate_entry(
    entry: object,
    *,
    source_desc: str,
) -> dict[str, object]:
    """Validate the gate_queue.jsonl schema required by SPEC §7.3.4."""
    if not isinstance(entry, Mapping):
        raise ResumeMergeError(f"{source_desc}: entry must be a JSON object.")

    try:
        excerpt_id = str(entry["excerpt_id"])
        gate_code = str(entry["gate_code"])
        timestamp = str(entry["timestamp"])
        context = entry["context"]
        status = entry["status"]
    except KeyError as exc:
        raise ResumeMergeError(
            f"{source_desc}: missing required field {exc.args[0]!r}."
        ) from exc

    if not excerpt_id or not gate_code:
        raise ResumeMergeError(
            f"{source_desc}: excerpt_id and gate_code must be non-empty."
        )
    if not timestamp:
        raise ResumeMergeError(f"{source_desc}: timestamp must be non-empty.")
    if not isinstance(context, Mapping) or not context:
        raise ResumeMergeError(
            f"{source_desc}: context must be a non-empty object."
        )
    if status != "pending":
        raise ResumeMergeError(
            f"{source_desc}: status must be 'pending'."
        )

    normalized = dict(entry)
    normalized["excerpt_id"] = excerpt_id
    normalized["gate_code"] = gate_code
    normalized["timestamp"] = timestamp
    normalized["context"] = dict(context)
    normalized["status"] = "pending"
    return normalized


def _gate_entry_key(entry: Mapping[str, object]) -> str:
    """Deduplicate gate entries by excerpt_id + gate_code."""
    return f"{entry['excerpt_id']}:{entry['gate_code']}"


# ═══════════════════════════════════════════════════════════════════
# Function 1: write_excerpts
# ═══════════════════════════════════════════════════════════════════


def write_excerpts(
    excerpts: list[ExcerptRecord],
    output_dir: Path,
) -> Path:
    """Write ExcerptRecords to excerpts.jsonl (§2.2.1).

    On resume, merges with existing file: new excerpts overwrite old
    entries with the same excerpt_id. Atomic via temp file + rename.

    One JSON line per record. Records ordered by div_id, chunk_index,
    unit_index (preserves reading order).
    Encoding: UTF-8, no BOM, \\n line separator.
    ensure_ascii=False preserves Arabic characters without escaping.

    Returns the path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "excerpts.jsonl"

    # Load existing excerpts for resume merge (keyed by excerpt_id)
    merged: dict[str, str] = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.rstrip("\n")
                if not stripped:
                    continue
                try:
                    existing = ExcerptRecord.model_validate_json(stripped)
                except (json.JSONDecodeError, ValueError) as exc:
                    raise ResumeMergeError(
                        f"Corrupt existing excerpts.jsonl at line {line_num}: {exc}"
                    ) from exc
                if existing.excerpt_id in merged:
                    raise ResumeMergeError(
                        "Corrupt existing excerpts.jsonl at line "
                        f"{line_num}: duplicate excerpt_id {existing.excerpt_id!r}."
                    )
                merged[existing.excerpt_id] = json.dumps(
                    existing.model_dump(mode="json"),
                    ensure_ascii=False,
                )

    existing_count = len(merged)

    # New excerpts overwrite existing entries with same ID
    sorted_excerpts = sorted(
        excerpts,
        key=lambda e: (e.div_id, e.chunk_index, e.unit_index),
    )
    for exc in sorted_excerpts:
        data = exc.model_dump(mode="json")
        merged[exc.excerpt_id] = json.dumps(
            data,
            ensure_ascii=False,
        )

    # Sort merged excerpts by reading order before writing
    def _sort_key(json_line: str) -> tuple[str, int, int]:
        try:
            obj = json.loads(json_line)
            return (obj.get("div_id", ""), obj.get("chunk_index", 0), obj.get("unit_index", 0))
        except (json.JSONDecodeError, KeyError):
            return ("", 0, 0)

    sorted_lines = sorted(merged.values(), key=_sort_key)

    # Atomic write: temp file + rename
    temp_path = output_path.with_suffix(".jsonl.tmp")
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        for line in sorted_lines:
            f.write(line + "\n")
    temp_path.replace(output_path)

    new_count = len(merged) - existing_count
    logger.info(
        "Wrote %d excerpts to %s (%d new, %d preserved)",
        len(merged),
        output_path,
        max(0, new_count),
        existing_count,
    )
    return output_path


# ═══════════════════════════════════════════════════════════════════
# Function 2: write_gate_queue
# ═══════════════════════════════════════════════════════════════════


def write_gate_queue(
    gate_entries: Sequence[dict[str, object]],
    output_dir: Path,
) -> Path:
    """Write human gate entries to gate_queue.jsonl (§2.2.1).

    On resume, merges with existing file: deduplicates by
    (excerpt_id, gate_code). Atomic via temp file + rename.

    One JSON line per gate entry. Present only if at least one gate
    was triggered.

    Returns the path to the written file.
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "gate_queue.jsonl"

    # Load existing gates for resume merge (keyed by excerpt_id + gate_code)
    merged: dict[str, str] = {}
    if output_path.exists():
        with open(output_path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                stripped = line.rstrip("\n")
                if not stripped:
                    continue
                try:
                    obj = _validate_gate_entry(
                        json.loads(stripped),
                        source_desc=f"Corrupt existing gate_queue.jsonl at line {line_num}",
                    )
                    merged[_gate_entry_key(obj)] = json.dumps(obj, ensure_ascii=False)
                except (json.JSONDecodeError, ResumeMergeError) as exc:
                    raise ResumeMergeError(
                        f"Corrupt existing gate_queue.jsonl at line {line_num}: {exc}"
                    ) from exc

    if not gate_entries and not merged:
        logger.info("No gate entries — skipping gate_queue.jsonl creation.")
        return output_path

    existing_count = len(merged)

    # New entries overwrite existing with same key
    for entry in gate_entries:
        normalized = _validate_gate_entry(
            entry,
            source_desc="Gate entry",
        )
        merged[_gate_entry_key(normalized)] = json.dumps(normalized, ensure_ascii=False)

    # Atomic write
    temp_path = output_path.with_suffix(".jsonl.tmp")
    with open(temp_path, "w", encoding="utf-8", newline="\n") as f:
        for line in merged.values():
            f.write(line + "\n")
    temp_path.replace(output_path)

    new_count = len(merged) - existing_count
    logger.info(
        "Wrote %d gate entries to %s (%d new, %d preserved)",
        len(merged),
        output_path,
        max(0, new_count),
        existing_count,
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
    gate_entries: Sequence[dict[str, object]],
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
                    written_entries.append(
                        _validate_gate_entry(
                            json.loads(raw_line),
                            source_desc=f"Corrupt gate_queue.jsonl at line {line_num}",
                        )
                    )
                except (json.JSONDecodeError, ResumeMergeError) as exc:
                    raise ResumeMergeError(
                        f"Corrupt gate_queue.jsonl at line {line_num}: {exc}"
                    ) from exc

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

    try:
        missing = _find_missing(gate_path)

        if missing:
            # SPEC §8.1 EX-M-008 recovery: "Retry write. If retry fails, halt."
            logger.warning(
                "V-P3-7: %d missing entries — retrying write + verify.",
                len(missing),
            )
            write_gate_queue(gate_entries, gate_path.parent)
            missing = _find_missing(gate_path)
    except ResumeMergeError as exc:
        logger.critical(
            "%s: Gate queue verification encountered corruption: %s",
            ExcerptingErrorCodes.EX_M_008,
            exc,
        )
        raise GateQueueVerificationError(
            f"{ExcerptingErrorCodes.EX_M_008}: {exc}. "
            "Invisible uncertainty — halting processing."
        ) from exc

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


# ═══════════════════════════════════════════════════════════════════
# Function 4: write_processing_log (§2.2.1)
# ═══════════════════════════════════════════════════════════════════


def write_processing_log(
    source_id: str,
    errors: list[str],
    timings: dict[str, float],
    excerpt_count: int,
    gate_count: int,
    output_dir: Path,
) -> Path:
    """Write processing log to processing_log.jsonl (§2.2.1).

    Single JSON line with run metadata for debugging and telemetry.
    """
    import datetime

    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "processing_log.jsonl"

    entry = {
        "source_id": source_id,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "excerpt_count": excerpt_count,
        "gate_count": gate_count,
        "error_count": len(errors),
        "errors": errors,
        "timings": timings,
    }

    with open(output_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

    logger.info("Wrote processing log to %s", output_path)
    return output_path
