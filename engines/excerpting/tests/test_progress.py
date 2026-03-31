"""Tests for WAL-based chunk-level progress tracking.

Covers: creation, mark_done, mark_failed, replay, last-entry-wins,
corrupt lines, unknown phase rejection, thread safety, summary, empty file.
"""
from __future__ import annotations

import json
import threading
from pathlib import Path

import pytest

from engines.excerpting.src.progress import TRACKED_PHASES, ProgressTracker


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def progress_file(tmp_path: Path) -> Path:
    """Return a fresh progress file path in a temp directory."""
    return tmp_path / "progress.jsonl"


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestProgressTrackerCreateEmpty:
    """test_progress_tracker_create_empty — new tracker with no file."""

    def test_no_file_exists(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        assert tracker.summary() == {"done": 0, "failed": 0, "total": 0}

    def test_is_done_returns_false_for_unknown(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        assert tracker.is_done("chunk_1", "phase2a") is False


class TestProgressTrackerMarkDone:
    """test_progress_tracker_mark_done — mark done, verify is_done returns True."""

    def test_mark_done_basic(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_done("chunk_1", "phase2a")
        assert tracker.is_done("chunk_1", "phase2a") is True

    def test_mark_done_other_phase_unaffected(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_done("chunk_1", "phase2a")
        assert tracker.is_done("chunk_1", "phase2b") is False

    def test_mark_done_other_chunk_unaffected(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_done("chunk_1", "phase2a")
        assert tracker.is_done("chunk_2", "phase2a") is False

    def test_mark_done_writes_to_file(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_done("chunk_1", "phase2a")
        assert progress_file.exists()
        lines = progress_file.read_text(encoding="utf-8").strip().splitlines()
        assert len(lines) == 1
        entry = json.loads(lines[0])
        assert entry["chunk_id"] == "chunk_1"
        assert entry["phase"] == "phase2a"
        assert entry["status"] == "done"
        assert "timestamp" in entry


class TestProgressTrackerMarkFailed:
    """test_progress_tracker_mark_failed — mark failed, verify is_done returns False."""

    def test_mark_failed_basic(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_failed("chunk_1", "phase2a", "EX-C-001")
        assert tracker.is_done("chunk_1", "phase2a") is False

    def test_mark_failed_records_error(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_failed("chunk_1", "phase2a", "EX-C-001")
        lines = progress_file.read_text(encoding="utf-8").strip().splitlines()
        entry = json.loads(lines[0])
        assert entry["status"] == "failed"
        assert entry["error"] == "EX-C-001"


class TestProgressTrackerReplay:
    """test_progress_tracker_replay — write entries, create new tracker from same file."""

    def test_replay_restores_state(self, progress_file: Path) -> None:
        # First tracker writes entries
        tracker1 = ProgressTracker(progress_file)
        tracker1.mark_done("chunk_1", "phase2a")
        tracker1.mark_done("chunk_2", "phase2b")
        tracker1.mark_failed("chunk_3", "phase3_enrich", "EX-M-002")

        # Second tracker replays from the same file
        tracker2 = ProgressTracker(progress_file)
        assert tracker2.is_done("chunk_1", "phase2a") is True
        assert tracker2.is_done("chunk_2", "phase2b") is True
        assert tracker2.is_done("chunk_3", "phase3_enrich") is False
        assert tracker2.summary() == {"done": 2, "failed": 1, "total": 3}


class TestProgressTrackerLastEntryWins:
    """test_progress_tracker_last_entry_wins — mark failed then done."""

    def test_failed_then_done(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_failed("chunk_1", "phase2a", "EX-C-001")
        assert tracker.is_done("chunk_1", "phase2a") is False
        tracker.mark_done("chunk_1", "phase2a")
        assert tracker.is_done("chunk_1", "phase2a") is True

    def test_replay_respects_last_entry(self, progress_file: Path) -> None:
        tracker1 = ProgressTracker(progress_file)
        tracker1.mark_failed("chunk_1", "phase2a", "EX-C-001")
        tracker1.mark_done("chunk_1", "phase2a")

        tracker2 = ProgressTracker(progress_file)
        assert tracker2.is_done("chunk_1", "phase2a") is True

    def test_done_then_failed_on_replay(self, progress_file: Path) -> None:
        tracker1 = ProgressTracker(progress_file)
        tracker1.mark_done("chunk_1", "phase2a")
        tracker1.mark_failed("chunk_1", "phase2a", "retry_failed")

        tracker2 = ProgressTracker(progress_file)
        assert tracker2.is_done("chunk_1", "phase2a") is False


class TestProgressTrackerCorruptLine:
    """test_progress_tracker_corrupt_line — inject corrupt JSON, verify skipped."""

    def test_corrupt_json_skipped(self, progress_file: Path) -> None:
        # Write a valid entry, then a corrupt line, then another valid entry
        progress_file.write_text(
            '{"chunk_id":"c1","phase":"phase2a","status":"done","timestamp":"T"}\n'
            "this is not json\n"
            '{"chunk_id":"c2","phase":"phase2b","status":"done","timestamp":"T"}\n',
            encoding="utf-8",
        )
        tracker = ProgressTracker(progress_file)
        assert tracker.is_done("c1", "phase2a") is True
        assert tracker.is_done("c2", "phase2b") is True
        assert tracker.summary()["done"] == 2

    def test_missing_key_skipped(self, progress_file: Path) -> None:
        # Missing 'status' key
        progress_file.write_text(
            '{"chunk_id":"c1","phase":"phase2a"}\n'
            '{"chunk_id":"c2","phase":"phase2b","status":"done","timestamp":"T"}\n',
            encoding="utf-8",
        )
        tracker = ProgressTracker(progress_file)
        assert tracker.is_done("c1", "phase2a") is False
        assert tracker.is_done("c2", "phase2b") is True
        assert tracker.summary()["total"] == 1


class TestProgressTrackerUnknownPhase:
    """test_progress_tracker_unknown_phase_rejected — invalid phase raises ValueError."""

    def test_mark_done_rejects_unknown(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        with pytest.raises(ValueError, match="Unknown phase"):
            tracker.mark_done("chunk_1", "bogus_phase")

    def test_mark_failed_rejects_unknown(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        with pytest.raises(ValueError, match="Unknown phase"):
            tracker.mark_failed("chunk_1", "bogus_phase", "err")

    def test_unknown_phase_in_file_skipped_on_replay(self, progress_file: Path) -> None:
        progress_file.write_text(
            '{"chunk_id":"c1","phase":"invalid_phase","status":"done","timestamp":"T"}\n'
            '{"chunk_id":"c2","phase":"phase2a","status":"done","timestamp":"T"}\n',
            encoding="utf-8",
        )
        tracker = ProgressTracker(progress_file)
        # Only the valid phase entry was loaded
        assert tracker.summary()["total"] == 1
        assert tracker.is_done("c2", "phase2a") is True

    def test_all_tracked_phases_accepted(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        for phase in TRACKED_PHASES:
            tracker.mark_done(f"chunk_{phase}", phase)
        assert tracker.summary()["done"] == len(TRACKED_PHASES)


class TestProgressTrackerThreadSafety:
    """test_progress_tracker_thread_safety — concurrent mark_done calls."""

    def test_concurrent_marks(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        errors: list[Exception] = []

        def mark_range(start: int, end: int) -> None:
            try:
                for i in range(start, end):
                    tracker.mark_done(f"chunk_{i}", "phase2a")
            except Exception as exc:
                errors.append(exc)

        threads = [
            threading.Thread(target=mark_range, args=(0, 50)),
            threading.Thread(target=mark_range, args=(50, 100)),
            threading.Thread(target=mark_range, args=(100, 150)),
            threading.Thread(target=mark_range, args=(150, 200)),
        ]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert len(errors) == 0
        assert tracker.summary()["done"] == 200

        # All entries are queryable
        for i in range(200):
            assert tracker.is_done(f"chunk_{i}", "phase2a") is True

    def test_concurrent_replay_consistent(self, progress_file: Path) -> None:
        """Verify that replaying a file written by concurrent threads is consistent."""
        tracker1 = ProgressTracker(progress_file)
        threads = []
        for i in range(50):
            t = threading.Thread(
                target=tracker1.mark_done,
                args=(f"chunk_{i}", "phase2a"),
            )
            threads.append(t)
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        # Replay from the same file
        tracker2 = ProgressTracker(progress_file)
        assert tracker2.summary()["done"] == 50


class TestProgressTrackerSummary:
    """test_progress_tracker_summary — verify summary counts."""

    def test_summary_mixed(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        tracker.mark_done("c1", "phase2a")
        tracker.mark_done("c2", "phase2a")
        tracker.mark_failed("c3", "phase2a", "err1")
        tracker.mark_done("c1", "phase2b")

        summary = tracker.summary()
        assert summary["done"] == 3
        assert summary["failed"] == 1
        assert summary["total"] == 4

    def test_summary_empty(self, progress_file: Path) -> None:
        tracker = ProgressTracker(progress_file)
        assert tracker.summary() == {"done": 0, "failed": 0, "total": 0}


class TestProgressTrackerEmptyFile:
    """test_progress_tracker_empty_file — tracker loads from empty file."""

    def test_empty_file(self, progress_file: Path) -> None:
        progress_file.write_text("", encoding="utf-8")
        tracker = ProgressTracker(progress_file)
        assert tracker.summary() == {"done": 0, "failed": 0, "total": 0}

    def test_whitespace_only_file(self, progress_file: Path) -> None:
        progress_file.write_text("\n\n  \n", encoding="utf-8")
        tracker = ProgressTracker(progress_file)
        assert tracker.summary() == {"done": 0, "failed": 0, "total": 0}
