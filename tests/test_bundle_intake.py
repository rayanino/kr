"""Tests for bundle_intake.py — KR feedback collection intake automation."""
from __future__ import annotations

import json
import zipfile
from pathlib import Path

import pytest
import yaml

from scripts.bundle_intake import (
    create_inventory,
    intake_bundle,
    validate_jsonl_file,
    validate_manifest,
    validate_yaml_file,
)


@pytest.fixture
def tmp_bundle(tmp_path: Path) -> Path:
    """Create a minimal valid bundle ZIP for testing."""
    bundle_dir = tmp_path / "engines" / "excerpting" / "chatgpt_test_collection"
    bundle_dir.mkdir(parents=True)
    source_dir = bundle_dir / "source_artifacts"
    source_dir.mkdir()

    # Manifest
    manifest = {
        "question_id": "T-1",
        "bundle_id": "chatgpt_test_collection",
        "version": "0.1.0",
        "status": "collection_bundle",
        "source_basis": {
            "owner_answer_primary": "explicit_draft",
            "engineering_layers_mix": ["explicit_draft", "inferred_from_prior_chat"],
        },
        "files_emitted": [
            "00_manifest.yaml",
            "01_answer.md",
            "02_decisions.jsonl",
            "README.md",
            "source_artifacts/raw_input.txt",
        ],
    }
    with open(bundle_dir / "00_manifest.yaml", "w", encoding="utf-8") as f:
        yaml.dump(manifest, f, allow_unicode=True)

    # Answer file
    (bundle_dir / "01_answer.md").write_text("# Test answer\n\nRanking: A > B > C\n", encoding="utf-8")

    # JSONL file
    decisions = [
        {"id": "DL-001", "question": "Is A first?", "answer": "Yes"},
        {"id": "DL-002", "question": "Is B second?", "answer": "Yes"},
    ]
    with open(bundle_dir / "02_decisions.jsonl", "w", encoding="utf-8") as f:
        for record in decisions:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # README
    (bundle_dir / "README.md").write_text("# Test bundle\n", encoding="utf-8")

    # Source artifact
    (source_dir / "raw_input.txt").write_text("Owner raw reaction here\n", encoding="utf-8")

    # Create ZIP
    zip_path = tmp_path / "chatgpt_test_collection_bundle.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        for file in bundle_dir.rglob("*"):
            if file.is_file():
                arcname = file.relative_to(tmp_path)
                zf.write(file, arcname)

    return zip_path


class TestValidateManifest:
    """Tests for manifest validation."""

    def test_valid_manifest(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "00_manifest.yaml"
        manifest_path.write_text(
            yaml.dump({
                "question_id": "S-1",
                "bundle_id": "test",
                "version": "0.1.0",
                "status": "collection_bundle",
                "files_emitted": ["00_manifest.yaml"],
            }),
            encoding="utf-8",
        )
        manifest, errors = validate_manifest(manifest_path)
        assert len(errors) == 0
        assert manifest["question_id"] == "S-1"

    def test_missing_required_field(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "00_manifest.yaml"
        manifest_path.write_text(
            yaml.dump({"question_id": "S-1"}),
            encoding="utf-8",
        )
        _, errors = validate_manifest(manifest_path)
        assert any("bundle_id" in e for e in errors)

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        manifest_path = tmp_path / "00_manifest.yaml"
        manifest_path.write_text("invalid: yaml: content: [", encoding="utf-8")
        _, errors = validate_manifest(manifest_path)
        assert len(errors) > 0
        assert any("invalid YAML" in e for e in errors)


class TestValidateJsonl:
    """Tests for JSONL validation."""

    def test_valid_jsonl(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "test.jsonl"
        jsonl_path.write_text(
            '{"id": 1}\n{"id": 2}\n',
            encoding="utf-8",
        )
        errors = validate_jsonl_file(jsonl_path)
        assert len(errors) == 0

    def test_invalid_jsonl_line(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "test.jsonl"
        jsonl_path.write_text(
            '{"id": 1}\nnot json\n{"id": 3}\n',
            encoding="utf-8",
        )
        errors = validate_jsonl_file(jsonl_path)
        assert len(errors) == 1
        assert "line 2" in errors[0]

    def test_empty_lines_skipped(self, tmp_path: Path) -> None:
        jsonl_path = tmp_path / "test.jsonl"
        jsonl_path.write_text(
            '{"id": 1}\n\n{"id": 2}\n\n',
            encoding="utf-8",
        )
        errors = validate_jsonl_file(jsonl_path)
        assert len(errors) == 0


class TestValidateYaml:
    """Tests for YAML validation."""

    def test_valid_yaml(self, tmp_path: Path) -> None:
        yaml_path = tmp_path / "test.yaml"
        yaml_path.write_text("key: value\n", encoding="utf-8")
        errors = validate_yaml_file(yaml_path)
        assert len(errors) == 0

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        yaml_path = tmp_path / "test.yaml"
        yaml_path.write_text("invalid: yaml: [unclosed", encoding="utf-8")
        errors = validate_yaml_file(yaml_path)
        assert len(errors) > 0


class TestIntakeBundle:
    """Integration tests for the full intake pipeline."""

    def test_valid_bundle_intake(self, tmp_bundle: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Happy path: valid bundle ZIP → inventory created, validation passes."""
        import scripts.bundle_intake as module

        monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

        # Create engine directory
        engine_dir = tmp_path / "engines" / "excerpting"
        engine_dir.mkdir(parents=True, exist_ok=True)

        success, inventory = intake_bundle(tmp_bundle, "excerpting", target_dir=tmp_path)
        assert success is True
        assert inventory["validation_passed"] is True
        assert inventory["question_id"] == "T-1"
        assert inventory["file_count"] > 0

    def test_missing_zip(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Error path: ZIP file not found → clear error."""
        import scripts.bundle_intake as module

        monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

        success, inventory = intake_bundle(
            tmp_path / "nonexistent.zip", "excerpting"
        )
        assert success is False
        assert "error" in inventory

    def test_missing_engine_dir(self, tmp_bundle: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """Error path: engine directory doesn't exist → clear error."""
        import scripts.bundle_intake as module

        monkeypatch.setattr(module, "REPO_ROOT", tmp_path)

        success, inventory = intake_bundle(tmp_bundle, "nonexistent_engine")
        assert success is False
        assert "Engine dir not found" in inventory.get("error", "")


class TestCreateInventory:
    """Tests for inventory creation."""

    def test_inventory_structure(self, tmp_path: Path) -> None:
        """Inventory has all required fields."""
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()
        (bundle_dir / "test.jsonl").write_text('{"a": 1}\n', encoding="utf-8")

        manifest = {"bundle_id": "test", "question_id": "Q-1", "status": "done"}
        inventory = create_inventory(bundle_dir, manifest, [])

        assert "bundle_id" in inventory
        assert "question_id" in inventory
        assert "file_count" in inventory
        assert "validation_passed" in inventory
        assert inventory["validation_passed"] is True

    def test_inventory_records_errors(self, tmp_path: Path) -> None:
        """Inventory captures validation errors."""
        bundle_dir = tmp_path / "bundle"
        bundle_dir.mkdir()

        errors = ["missing field X", "invalid JSONL"]
        inventory = create_inventory(bundle_dir, {}, errors)

        assert inventory["validation_passed"] is False
        assert len(inventory["validation_errors"]) == 2
