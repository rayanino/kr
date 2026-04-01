"""Tests for the taxonomy engine orchestrator (SPEC §2, §3, §6).

Tests verify input validation, pending-no-tree handling, stub/mock adapter
behavior, and end-to-end batch processing.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import pytest

from engines.taxonomy.contracts_core import (
    RunConfig,
)
from engines.taxonomy.src.engine import TaxonomyEngineError, _EXPECTED_FIELDS, run
from engines.taxonomy.tests.conftest import (
    MockPlacementAdapter,
    make_excerpt,
    make_ranking,
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

    def test_empty_excerpt_topic_without_flag_skips(self, tmp_path: Path) -> None:
        """Empty topics without llm_enrichment_failed flag → rejected."""
        exc = make_excerpt(excerpt_topic=[], review_flags=[])
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_empty_topic_no_flag",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 1  # Rejected but still counted as input

    def test_empty_excerpt_topic_with_enrichment_failed_accepted(
        self, tmp_path: Path,
    ) -> None:
        """Empty topics + llm_enrichment_failed flag → accepted (degraded placement)."""
        exc = make_excerpt(
            excerpt_topic=[],
            review_flags=["llm_enrichment_failed"],
        )
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_empty_topic_with_flag",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 1
        # NOT rejected — reaches a placement route (unplaced with stub adapter)
        placed_or_routed = (
            report.placed_count
            + report.staged_count
            + report.unplaced_count
            + report.pending_no_tree_count
        )
        assert placed_or_routed == 1, "Excerpt should reach a placement route, not be rejected"

    def test_empty_excerpt_topic_with_unrelated_flag_skips(
        self, tmp_path: Path,
    ) -> None:
        """Empty topics + unrelated flag → rejected (only llm_enrichment_failed allows it)."""
        exc = make_excerpt(
            excerpt_topic=[],
            review_flags=["some_other_flag"],
        )
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_empty_topic_wrong_flag",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 1  # Rejected but still counted

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

    def test_expected_fields_has_eight_entries(self) -> None:
        """F-1: _EXPECTED_FIELDS must have exactly 8 SPEC §2.1 fields."""
        assert len(_EXPECTED_FIELDS) == 8

    def test_missing_expected_field_still_proceeds(self, tmp_path: Path) -> None:
        """F-1: Missing expected field warns but does not reject."""
        exc = make_excerpt()
        del exc["description_arabic"]  # Expected but not required
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_expected_field",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )
        # Not rejected — still processed (unplaced due to stub)
        assert report.unplaced_count == 1
        assert report.total_excerpts == 1

    def test_school_null_with_key_present_no_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """F-1: school=None with key present does NOT trigger expected-field warning."""
        exc = make_excerpt(school=None)
        assert "school" in exc  # Key is present
        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_null_school",
        )
        with caplog.at_level(logging.WARNING):
            run(
                config,
                adapter=None,
                registry_path=_REGISTRY_PATH,
                base_path=tmp_path,
            )

        school_warnings = [
            r for r in caplog.records
            if "missing school" in r.message.lower()
            or ("MISSING_EXPECTED_FIELD" in r.message and "school" in r.message)
        ]
        assert len(school_warnings) == 0


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


# ── BOM-safe JSONL Reading (F-7) ────────────────────────────────


class TestBomSafeReading:
    def test_bom_jsonl_reads_all_excerpts(self, tmp_path: Path) -> None:
        """F-7: UTF-8 BOM must not cause first excerpt to be silently dropped."""
        exc1 = make_excerpt(excerpt_id="bom_test_001")
        exc2 = make_excerpt(excerpt_id="bom_test_002")

        jsonl = tmp_path / "bom_input.jsonl"
        bom = b"\xef\xbb\xbf"  # UTF-8 BOM
        lines = (
            json.dumps(exc1, ensure_ascii=False) + "\n"
            + json.dumps(exc2, ensure_ascii=False) + "\n"
        )
        jsonl.write_bytes(bom + lines.encode("utf-8"))

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_bom",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        assert report.total_excerpts == 2


# ── Duplicate Excerpt ID Warning (F-8) ──────────────────────────


class TestDuplicateExcerptId:
    def test_duplicate_id_still_processes_both(self, tmp_path: Path) -> None:
        """F-8: Duplicate excerpt_id warns but processes both (last-write-wins)."""
        exc1 = make_excerpt(excerpt_id="dup_001")
        exc2 = make_excerpt(excerpt_id="dup_001")  # Same ID

        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc1, exc2])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_dup",
        )
        report = run(
            config,
            adapter=None,
            registry_path=_REGISTRY_PATH,
            base_path=tmp_path,
        )

        # Both excerpts processed (not rejected)
        assert report.total_excerpts == 2
        assert report.unplaced_count == 2  # Both unplaced (stub adapter)

    def test_duplicate_id_logs_warning(
        self, tmp_path: Path, caplog: pytest.LogCaptureFixture
    ) -> None:
        """F-8: Duplicate excerpt_id must log TAX_DUPLICATE_EXCERPT_ID."""
        exc1 = make_excerpt(excerpt_id="dup_002")
        exc2 = make_excerpt(excerpt_id="dup_002")

        jsonl = tmp_path / "input.jsonl"
        _write_excerpts_jsonl(jsonl, [exc1, exc2])

        config = RunConfig(
            science_id="aqidah",
            input_path=str(jsonl),
            batch_id="test_dup_warn",
        )
        with caplog.at_level(logging.WARNING):
            run(
                config,
                adapter=None,
                registry_path=_REGISTRY_PATH,
                base_path=tmp_path,
            )

        dup_warnings = [
            r for r in caplog.records
            if "TAX_DUPLICATE_EXCERPT_ID" in r.message
        ]
        assert len(dup_warnings) == 1
        assert "dup_002" in dup_warnings[0].message
