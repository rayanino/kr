"""Tests for file output (SPEC §3.1–3.4, §3.6).

Tests verify directory structure, D-023 provenance, Arabic text preservation,
and serialization invariants.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.taxonomy.contracts_core import (
    LifecycleStage,
    PlacementAdditions,
    PlacementRoute,
)
from engines.taxonomy.src.writer import (
    write_pending_excerpt,
    write_placed_excerpt,
    write_staged_excerpt,
    write_unplaced_excerpt,
)
from engines.taxonomy.tests.conftest import make_excerpt, make_placement_additions


# ── Placed Excerpt Writer ─────────────────────────────────────────


class TestWritePlacedExcerpt:
    def test_correct_output_path(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = make_placement_additions()
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)
        assert "content" in str(path)
        assert "excerpts" in str(path)
        assert exc["excerpt_id"] in path.name

    def test_d023_all_upstream_fields_preserved(
        self, tmp_output_dir: Path
    ) -> None:
        """D-023: All upstream fields must survive placement."""
        exc = make_excerpt(custom_upstream_field="test_value")
        adds = make_placement_additions()
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)

        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["custom_upstream_field"] == "test_value"
        assert data["excerpt_id"] == exc["excerpt_id"]
        assert data["primary_text"] == exc["primary_text"]
        assert data["excerpt_topic"] == exc["excerpt_topic"]

    def test_placement_additions_present(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = make_placement_additions()
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)

        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["lifecycle_stage"] == "placed"
        assert data["placement_route"] == "live"
        assert data["confirmed_leaf"] == adds.confirmed_leaf
        assert data["placement_confidence"] == adds.placement_confidence

    def test_arabic_text_byte_identical(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = make_placement_additions()
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)

        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["primary_text"] == exc["primary_text"]

    def test_ensure_ascii_false(self, tmp_output_dir: Path) -> None:
        """Arabic text must appear as Arabic, not \\uXXXX escapes."""
        exc = make_excerpt()
        adds = make_placement_additions()
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)

        raw = path.read_text(encoding="utf-8")
        assert "\\u0" not in raw  # No Unicode escapes for Arabic
        assert "حروف" in raw  # Arabic visible in file

    def test_creates_nested_directories(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = make_placement_additions(
            confirmed_leaf="deep/nested/leaf/path"
        )
        path = write_placed_excerpt(exc, adds, "nahw", tmp_output_dir)
        assert path.exists()


# ── Staged Excerpt Writer ─────────────────────────────────────────


class TestWriteStagedExcerpt:
    def test_staged_path_uses_staged_dir(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = make_placement_additions(
            lifecycle_stage=LifecycleStage.STAGED,
            placement_route=PlacementRoute.STAGED_LOW_CONFIDENCE,
        )
        path = write_staged_excerpt(exc, adds, "nahw", tmp_output_dir)
        assert "staged" in str(path)
        assert "content" not in str(path)


# ── Unplaced Excerpt Writer ───────────────────────────────────────


class TestWriteUnplacedExcerpt:
    def test_unplaced_path_no_leaf(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = PlacementAdditions(
            lifecycle_stage=LifecycleStage.UNPLACED,
            placement_route=PlacementRoute.UNPLACED,
            unplaced_reason="No candidate scored ≥0.5",
        )
        path = write_unplaced_excerpt(exc, adds, "nahw", tmp_output_dir)
        assert "unplaced" in str(path)
        assert exc["excerpt_id"] in path.name

    def test_unplaced_preserves_upstream(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = PlacementAdditions(
            lifecycle_stage=LifecycleStage.UNPLACED,
            placement_route=PlacementRoute.UNPLACED,
        )
        path = write_unplaced_excerpt(exc, adds, "nahw", tmp_output_dir)
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["source_id"] == exc["source_id"]


# ── Pending Excerpt Writer ────────────────────────────────────────


class TestWritePendingExcerpt:
    def test_pending_path_uses_pending_dir(self, tmp_output_dir: Path) -> None:
        exc = make_excerpt()
        adds = PlacementAdditions(
            lifecycle_stage=LifecycleStage.PENDING_NO_TREE,
            placement_route=PlacementRoute.PENDING_NO_TREE,
            declared_science_id="fiqh",
            pending_since_utc="2026-03-30T12:00:00+00:00",
        )
        path = write_pending_excerpt(exc, adds, "fiqh", tmp_output_dir)
        assert "pending_no_tree" in str(path)
        assert "fiqh" in str(path)
