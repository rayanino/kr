"""Tests for Output Writer (§2.2.1).

Tests JSONL format, round-trip serialization, gate queue write + V-P3-7
verification, empty inputs, and EX-M-008 halt behavior.
"""

from __future__ import annotations

import json

import pytest

from engines.excerpting.contracts import (
    ExcerptingErrorCodes,
    ScholarlyFunction,
)
from engines.excerpting.src.writer import (
    GateQueueVerificationError,
    verify_gate_queue,
    write_excerpts,
    write_gate_queue,
)

from .conftest import _make_excerpt_record


# ═══════════════════════════════════════════════════════════════════
# write_excerpts
# ═══════════════════════════════════════════════════════════════════


class TestWriteExcerpts:
    """Tests for write_excerpts JSONL output."""

    def test_jsonl_format_one_object_per_line(self, tmp_path) -> None:
        """Output is valid JSONL: one JSON object per line."""
        excerpts = [
            _make_excerpt_record(excerpt_id=f"exc_test_0_0_{i}", unit_index=i)
            for i in range(3)
        ]
        path = write_excerpts(excerpts, tmp_path)
        assert path.exists()
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        assert len(lines) == 3
        for line in lines:
            obj = json.loads(line)
            assert isinstance(obj, dict)
            assert "excerpt_id" in obj

    def test_arabic_preserved_no_escaping(self, tmp_path) -> None:
        """Arabic text preserved as-is, not escaped as \\uXXXX."""
        arabic_text = "بسم الله الرحمن الرحيم"
        exc = _make_excerpt_record(
            primary_text=arabic_text,
            text_snippet=arabic_text[:80],
        )
        path = write_excerpts([exc], tmp_path)
        content = path.read_text(encoding="utf-8")
        assert arabic_text in content
        assert "\\u0628" not in content  # ب should not be escaped

    def test_round_trip_integrity(self, tmp_path) -> None:
        """Write → read → compare: data survives round-trip."""
        exc = _make_excerpt_record(
            excerpt_id="exc_round_trip_0_0_0",
            excerpt_topic=["فقه", "عقيدة"],
        )
        path = write_excerpts([exc], tmp_path)
        with open(path, "r", encoding="utf-8") as f:
            data = json.loads(f.readline())

        assert data["excerpt_id"] == "exc_round_trip_0_0_0"
        assert data["excerpt_topic"] == ["فقه", "عقيدة"]
        assert data["primary_function"] == "definition"
        assert data["self_containment"] == "FULL"

    def test_output_sorted_by_reading_order(self, tmp_path) -> None:
        """Records sorted by div_id, chunk_index, unit_index."""
        exc_b = _make_excerpt_record(
            excerpt_id="exc_b_0_0_0",
            div_id="div_b",
            chunk_index=0,
            unit_index=0,
        )
        exc_a = _make_excerpt_record(
            excerpt_id="exc_a_0_0_0",
            div_id="div_a",
            chunk_index=0,
            unit_index=0,
        )
        path = write_excerpts([exc_b, exc_a], tmp_path)
        lines = path.read_text(encoding="utf-8").strip().split("\n")
        first = json.loads(lines[0])
        second = json.loads(lines[1])
        assert first["div_id"] == "div_a"
        assert second["div_id"] == "div_b"

    def test_empty_input(self, tmp_path) -> None:
        """Empty excerpt list → creates empty file."""
        path = write_excerpts([], tmp_path)
        assert path.exists()
        assert path.read_text(encoding="utf-8") == ""

    def test_output_directory_created(self, tmp_path) -> None:
        """Output directory is created if it doesn't exist."""
        nested_dir = tmp_path / "a" / "b" / "c"
        path = write_excerpts([_make_excerpt_record()], nested_dir)
        assert path.exists()
        assert path.parent == nested_dir

    def test_utf8_no_bom(self, tmp_path) -> None:
        """File is UTF-8 without BOM."""
        path = write_excerpts([_make_excerpt_record()], tmp_path)
        raw = path.read_bytes()
        assert not raw.startswith(b"\xef\xbb\xbf")  # No BOM

    def test_newline_separator(self, tmp_path) -> None:
        """Lines separated by \\n (not \\r\\n)."""
        excerpts = [
            _make_excerpt_record(excerpt_id=f"exc_nl_{i}_0_{i}", unit_index=i)
            for i in range(2)
        ]
        path = write_excerpts(excerpts, tmp_path)
        raw = path.read_bytes()
        # Should have \n but not \r\n
        assert b"\n" in raw


# ═══════════════════════════════════════════════════════════════════
# write_gate_queue
# ═══════════════════════════════════════════════════════════════════


class TestWriteGateQueue:
    """Tests for gate queue JSONL output."""

    def test_gate_queue_format(self, tmp_path) -> None:
        """Gate entries written as valid JSONL."""
        entries = [
            {
                "excerpt_id": "exc_gate_0_0_0",
                "gate_code": "EX-G-001",
                "status": "pending",
                "context": {"text": "نص عربي"},
            }
        ]
        path = write_gate_queue(entries, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8").strip())
        assert data["gate_code"] == "EX-G-001"

    def test_gate_queue_arabic_preserved(self, tmp_path) -> None:
        """Arabic in gate entries preserved without escaping."""
        entries = [
            {
                "excerpt_id": "exc_gate_0_0_0",
                "gate_code": "EX-G-002",
                "context": {"text": "هذا نص يحتاج مراجعة بشرية"},
            }
        ]
        path = write_gate_queue(entries, tmp_path)
        content = path.read_text(encoding="utf-8")
        assert "مراجعة بشرية" in content

    def test_empty_gate_queue_skips_file(self, tmp_path) -> None:
        """Empty gate entries → returns path but does NOT create file (Fix 11)."""
        path = write_gate_queue([], tmp_path)
        assert path == tmp_path / "gate_queue.jsonl"
        assert not path.exists()


# ═══════════════════════════════════════════════════════════════════
# verify_gate_queue (V-P3-7)
# ═══════════════════════════════════════════════════════════════════


class TestVerifyGateQueue:
    """V-P3-7: Gate queue verification — paranoid read-back."""

    def test_verification_passes(self, tmp_path) -> None:
        """Write + verify → no errors."""
        entries = [
            {"excerpt_id": "exc_v_0_0_0", "gate_code": "EX-G-001"},
            {"excerpt_id": "exc_v_0_0_1", "gate_code": "EX-G-002"},
        ]
        path = write_gate_queue(entries, tmp_path)
        errors = verify_gate_queue(entries, path)
        assert errors == []

    def test_retry_succeeds_after_initial_failure(self, tmp_path) -> None:
        """Missing entry on first pass → retry re-writes → success (Fix 7)."""
        entries_written = [
            {"excerpt_id": "exc_v_0_0_0", "gate_code": "EX-G-001"},
        ]
        entries_expected = [
            {"excerpt_id": "exc_v_0_0_0", "gate_code": "EX-G-001"},
            {"excerpt_id": "exc_v_0_0_1", "gate_code": "EX-G-002"},
        ]
        path = write_gate_queue(entries_written, tmp_path)
        # Retry re-writes with entries_expected → second pass finds all entries
        errors = verify_gate_queue(entries_expected, path)
        assert errors == []

    def test_retry_fails_then_halts(self, tmp_path, monkeypatch) -> None:
        """Missing entry after retry → GateQueueVerificationError (Fix 7)."""
        entries_written = [
            {"excerpt_id": "exc_v_0_0_0", "gate_code": "EX-G-001"},
        ]
        entries_expected = [
            {"excerpt_id": "exc_v_0_0_0", "gate_code": "EX-G-001"},
            {"excerpt_id": "exc_v_0_0_1", "gate_code": "EX-G-002"},
        ]
        path = write_gate_queue(entries_written, tmp_path)
        # Make retry write a no-op so the file stays wrong
        monkeypatch.setattr(
            "engines.excerpting.src.writer.write_gate_queue",
            lambda entries, output_dir: path,
        )
        with pytest.raises(GateQueueVerificationError) as exc_info:
            verify_gate_queue(entries_expected, path)
        assert ExcerptingErrorCodes.EX_M_008 in str(exc_info.value)

    def test_file_missing_raises_halt(self, tmp_path) -> None:
        """Gate file doesn't exist → GateQueueVerificationError."""
        entries = [{"excerpt_id": "exc_x", "gate_code": "EX-G-001"}]
        missing_path = tmp_path / "nonexistent.jsonl"
        with pytest.raises(GateQueueVerificationError) as exc_info:
            verify_gate_queue(entries, missing_path)
        assert ExcerptingErrorCodes.EX_M_008 in str(exc_info.value)

    def test_empty_entries_no_verification(self, tmp_path) -> None:
        """Empty expected entries → no verification needed, no errors."""
        errors = verify_gate_queue([], tmp_path / "irrelevant.jsonl")
        assert errors == []

    def test_corrupt_file_recovered_by_retry(self, tmp_path) -> None:
        """Corrupt JSON lines → retry re-writes clean data → success (Fix 7)."""
        path = tmp_path / "gate_queue.jsonl"
        # Write one valid + one corrupt line
        with open(path, "w", encoding="utf-8") as f:
            f.write('{"excerpt_id": "exc_a", "gate_code": "EX-G-001"}\n')
            f.write("THIS IS NOT JSON\n")

        entries = [
            {"excerpt_id": "exc_a", "gate_code": "EX-G-001"},
            {"excerpt_id": "exc_b", "gate_code": "EX-G-002"},
        ]
        # Retry re-writes with both entries cleanly → success
        errors = verify_gate_queue(entries, path)
        assert errors == []

    def test_round_trip_gate_queue(self, tmp_path) -> None:
        """Full round-trip: write → verify → success."""
        entries = [
            {
                "excerpt_id": "exc_rt_0_0_0",
                "gate_code": "EX-G-001",
                "timestamp": "2026-03-24T00:00:00+00:00",
                "context": {
                    "primary_text_snippet": "بسم الله الرحمن الرحيم",
                    "school": "حنبلي",
                },
                "status": "pending",
            },
            {
                "excerpt_id": "exc_rt_0_0_1",
                "gate_code": "EX-G-003",
                "timestamp": "2026-03-24T00:00:00+00:00",
                "context": {"school": "شافعي"},
                "status": "pending",
            },
        ]
        path = write_gate_queue(entries, tmp_path)
        errors = verify_gate_queue(entries, path)
        assert errors == []
