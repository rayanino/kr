"""WAL-based progress tracking for chunk-level resume.

Uses append-only JSONL for crash-safe, reader-safe progress tracking on Windows NTFS.
Each line records a chunk completing (or failing) a phase.
On startup, replay the log to build in-memory state -- last entry per (chunk_id, phase) wins.
"""
from __future__ import annotations

import datetime
import json
import logging
import threading
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Valid phase names for tracking
TRACKED_PHASES = frozenset({"phase2a", "phase2b", "phase3_enrich", "phase3_consensus"})


class ProgressTracker:
    """Track per-chunk, per-phase completion via append-only JSONL.

    Thread-safe: uses a lock for in-memory state and file appends.
    """

    def __init__(self, progress_file: Path) -> None:
        self._path = progress_file
        self._lock = threading.Lock()
        # In-memory state: {(chunk_id, phase): status}
        self._state: dict[tuple[str, str], str] = {}
        self._replay()

    def _replay(self) -> None:
        """Replay JSONL log to rebuild in-memory state. Last entry per key wins."""
        if not self._path.exists():
            return
        try:
            text = self._path.read_text(encoding="utf-8")
        except OSError as exc:
            logger.warning("Could not read progress file %s: %s", self._path, exc)
            return
        for line_no, line in enumerate(text.splitlines(), 1):
            line = line.strip()
            if not line:
                continue
            try:
                entry = json.loads(line)
                chunk_id = entry["chunk_id"]
                phase = entry["phase"]
                status = entry["status"]
                if phase not in TRACKED_PHASES:
                    logger.warning(
                        "Unknown phase %r in progress line %d, skipping",
                        phase,
                        line_no,
                    )
                    continue
                self._state[(chunk_id, phase)] = status
            except (json.JSONDecodeError, KeyError) as exc:
                logger.warning("Corrupt progress line %d: %s", line_no, exc)
                continue
        logger.info(
            "Progress replay: %d entries loaded from %s",
            len(self._state),
            self._path,
        )

    def _append(
        self,
        chunk_id: str,
        phase: str,
        status: str,
        error: Optional[str] = None,
    ) -> None:
        """Append a single entry to the JSONL file."""
        entry: dict[str, str] = {
            "chunk_id": chunk_id,
            "phase": phase,
            "status": status,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        }
        if error is not None:
            entry["error"] = error
        line = json.dumps(entry, ensure_ascii=False) + "\n"
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "a", encoding="utf-8") as f:
                f.write(line)
        except OSError as exc:
            logger.warning("Could not append to progress file: %s", exc)

    def is_done(self, chunk_id: str, phase: str) -> bool:
        """Check if a chunk has completed a phase successfully."""
        with self._lock:
            return self._state.get((chunk_id, phase)) == "done"

    def mark_done(self, chunk_id: str, phase: str) -> None:
        """Record successful completion of a phase for a chunk."""
        if phase not in TRACKED_PHASES:
            raise ValueError(f"Unknown phase: {phase!r}")
        with self._lock:
            self._state[(chunk_id, phase)] = "done"
            self._append(chunk_id, phase, "done")

    def mark_failed(self, chunk_id: str, phase: str, error: str) -> None:
        """Record failure of a phase for a chunk."""
        if phase not in TRACKED_PHASES:
            raise ValueError(f"Unknown phase: {phase!r}")
        with self._lock:
            self._state[(chunk_id, phase)] = "failed"
            self._append(chunk_id, phase, "failed", error=error)

    def summary(self) -> dict[str, int]:
        """Return counts of done/failed entries."""
        with self._lock:
            done = sum(1 for s in self._state.values() if s == "done")
            failed = sum(1 for s in self._state.values() if s == "failed")
            return {"done": done, "failed": failed, "total": len(self._state)}
