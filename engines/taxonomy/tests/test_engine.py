"""Tests for the taxonomy engine orchestrator (SPEC §2, §3, §6).

Tests verify input validation, pending-no-tree handling, stub/mock adapter
behavior, and end-to-end batch processing.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from engines.taxonomy.contracts_core import (
    PlacementRoute,
    RunConfig,
)
from engines.taxonomy.src.engine import TaxonomyEngineError, run
from engines.taxonomy.tests.conftest import (
    MockPlacementAdapter,
    make_excerpt,
    make_ranking,
    make_run_config,
)

_PROJECT_ROOT = Path(__file__).resolve().parents[3]
_REGISTRY_PATH = _PROJECT_ROOT / "library" / "sciences" / "taxonomy_registry.yaml"


def _write_excerpts_jsonl(path: Path, excerpts: list[dict]) -> None:
    """Write a list of excerpt dicts to a JSONL file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for exc in excerpts:
            f.write(json.dumps(exc, ensure_ascii=False) + "\n")


# ── Config Validation ─────────────────────────────────────────────


class TestConfigValidation:
    def test_empty_science_id_raises(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "test.jsonl"
        jsonl.write_text("", encoding="utf-8")
        config = RunConfig(science_id="", input_path=str(jsonl), batch_id="b1")
        with pytest.raises(TaxonomyEngineError, match="science_id"):
            run(config, registry_path=_REGISTRY_PATH, base_path=tmp_path)

    def test_nonexistent_input_raises(self, tmp_path: Path) -> None:
        config = RunConfig(
            science_id="nahw",
            input_path=str(tmp_path / "nonexistent.jsonl"),
            batch_id="b1",
        )
        with pytest.raises(TaxonomyEngineError, match="input_path"):
            run(config, registry_path=_REGISTRY_PATH, base_path=tmp_path)


# ── Pending-No-Tree ───────────────────────────────────────────────


class TestPendingNoTree:
    def test_unknown_science_routes_to_pending(self, tmp_path: Path) -> None:
        exc = make_excerpt()
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="fiqh",  # Not in registry
            input_path=str(jsonl),
            batch_id="test_pending",
        )
        report = run(
            config,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.pending_no_tree_count == 1
        assert report.placed_count == 0

        # Verify file written to pending_no_tree/
        pending_dir = tmp_path / "pending_no_tree" / "fiqh"
        files = list(pending_dir.glob("*.json"))
        assert len(files) == 1


# ── Stub Adapter (Session 1) ─────────────────────────────────────


class TestStubAdapter:
    def test_stub_routes_all_to_unplaced(self, tmp_path: Path) -> None:
        """With no LLM adapter, all excerpts go to unplaced."""
        exc = make_excerpt()
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_stub",
        )
        report = run(
            config,
            adapter=None,  # Uses StubPlacementAdapter
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.unplaced_count == 1
        assert report.placed_count == 0


# ── Mock Adapter (Placement) ──────────────────────────────────────


class TestMockAdapter:
    def test_high_score_routes_to_live(self, tmp_path: Path) -> None:
        exc = make_excerpt(primary_function="rule_statement")
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        # Mock that returns a high score for a known aqidah leaf
        ranking = make_ranking([
            ("al_iman_billah/asma_wa_sifat/manhaj_ahl_al_sunna_fi_al_sifat", 0.92),
        ])
        adapter = MockPlacementAdapter(stage2_result=ranking)

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_mock_live",
        )
        report = run(
            config,
            adapter=adapter,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.placed_count == 1
        assert report.unplaced_count == 0

        # Verify file exists in content dir
        content_dir = tmp_path / "aqidah" / "content"
        json_files = list(content_dir.rglob("*.json"))
        assert len(json_files) == 1

    def test_low_score_routes_to_unplaced(self, tmp_path: Path) -> None:
        exc = make_excerpt(primary_function="rule_statement")
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        ranking = make_ranking([
            ("al_iman_billah/asma_wa_sifat/manhaj_ahl_al_sunna_fi_al_sifat", 0.20),
        ])
        adapter = MockPlacementAdapter(stage2_result=ranking)

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_mock_unplaced",
        )
        report = run(
            config,
            adapter=adapter,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.unplaced_count == 1
        assert report.placed_count == 0


# ── Input Validation ──────────────────────────────────────────────


class TestInputValidation:
    def test_missing_required_field_skips_excerpt(self, tmp_path: Path) -> None:
        good = make_excerpt()
        bad = make_excerpt()
        del bad["primary_text"]  # Required field missing

        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [good, bad])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_validation",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        # Good excerpt processed (unplaced due to stub), bad excerpt rejected
        # total_excerpts includes rejected (H-2 fix: true input count)
        assert report.total_excerpts == 2
        assert report.unplaced_count == 1

    def test_empty_excerpt_topic_skips(self, tmp_path: Path) -> None:
        exc = make_excerpt(excerpt_topic=[])
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_empty_topic",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 1  # Rejected but still counted as input

    def test_empty_jsonl_produces_empty_report(self, tmp_path: Path) -> None:
        jsonl = tmp_path / "empty.jsonl"
        jsonl.write_text("", encoding="utf-8")

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_empty",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 0
        assert report.placed_count == 0


# ── Batch Report ──────────────────────────────────────────────────


class TestBatchReport:
    def test_batch_report_written(self, tmp_path: Path) -> None:
        exc = make_excerpt()
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="report_test",
        )
        run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        report_path = tmp_path / "aqidah" / "batch_reports" / "report_test.json"
        assert report_path.exists()

        data = json.loads(report_path.read_text(encoding="utf-8"))
        assert data["batch_id"] == "report_test"
        assert data["science_id"] == "aqidah"
        assert data["total_excerpts"] == 1
