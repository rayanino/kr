"""Bundle intake automation for KR feedback collection.

Handles: unzip → validate → inventory → report.
Does NOT extract atoms (requires CC semantic understanding).

Usage:
    python scripts/bundle_intake.py <zip_path> --engine excerpting
    python scripts/bundle_intake.py <zip_path> --engine excerpting --target-dir custom/path
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

REPO_ROOT = Path(__file__).resolve().parent.parent


def validate_manifest(manifest_path: Path) -> tuple[dict, list[str]]:
    """Validate and parse a bundle manifest.yaml.

    Returns (manifest_dict, list_of_errors).
    """
    errors: list[str] = []
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = yaml.safe_load(f)
    except yaml.YAMLError as e:
        return {}, [f"manifest.yaml is invalid YAML: {e}"]

    if not isinstance(manifest, dict):
        return {}, ["manifest.yaml root is not a mapping"]

    required_fields = [
        "question_id",
        "bundle_id",
        "version",
        "status",
        "files_emitted",
    ]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"manifest.yaml missing required field: {field}")

    return manifest, errors


def validate_jsonl_file(file_path: Path) -> list[str]:
    """Validate that a .jsonl file contains valid line-delimited JSON."""
    errors: list[str] = []
    try:
        with open(file_path, encoding="utf-8") as f:
            lines = f.readlines()
    except Exception as e:
        return [f"Cannot read {file_path.name}: {e}"]

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            json.loads(stripped)
        except json.JSONDecodeError as e:
            errors.append(f"{file_path.name} line {i}: invalid JSON — {e}")

    return errors


def validate_yaml_file(file_path: Path) -> list[str]:
    """Validate that a .yaml/.yml file is parseable."""
    try:
        with open(file_path, encoding="utf-8") as f:
            yaml.safe_load(f)
    except yaml.YAMLError as e:
        return [f"{file_path.name}: invalid YAML — {e}"]
    return []


def create_inventory(
    bundle_dir: Path, manifest: dict, validation_errors: list[str]
) -> dict:
    """Create an inventory.json for the bundle."""
    files_list = []
    for item in sorted(bundle_dir.rglob("*")):
        if item.is_file() and item.name != "inventory.json":
            rel = item.relative_to(bundle_dir)
            record_count = 0
            if item.suffix == ".jsonl":
                with open(item, encoding="utf-8") as f:
                    record_count = sum(
                        1 for line in f if line.strip()
                    )
            files_list.append(
                {
                    "name": str(rel).replace("\\", "/"),
                    "size_bytes": item.stat().st_size,
                    "type": item.suffix.lstrip("."),
                    "records": record_count if item.suffix == ".jsonl" else None,
                }
            )

    # Count source_basis distribution from manifest
    source_basis_dist: dict[str, int] = {}
    if "source_basis" in manifest and isinstance(
        manifest["source_basis"], dict
    ):
        mix = manifest["source_basis"].get("engineering_layers_mix", [])
        for basis in mix:
            source_basis_dist[basis] = source_basis_dist.get(basis, 0) + 1

    inventory = {
        "bundle_id": manifest.get("bundle_id", bundle_dir.name),
        "question_id": manifest.get("question_id", "UNKNOWN"),
        "question_topic": "extracted from bundle",
        "inventory_date": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "status": manifest.get("status", "unknown"),
        "file_count": len(files_list),
        "total_size_bytes": sum(f["size_bytes"] for f in files_list),
        "source_basis_distribution": source_basis_dist,
        "validation_errors": validation_errors,
        "validation_passed": len(validation_errors) == 0,
        "files": files_list,
    }
    return inventory


def intake_bundle(
    zip_path: Path,
    engine: str,
    target_dir: Path | None = None,
) -> tuple[bool, dict]:
    """Run full intake: unzip → validate → inventory → report.

    Returns (success, inventory_dict).
    """
    if not zip_path.exists():
        logger.error("ZIP file not found: %s", zip_path)
        return False, {"error": f"ZIP not found: {zip_path}"}

    if not zipfile.is_zipfile(zip_path):
        logger.error("Not a valid ZIP file: %s", zip_path)
        return False, {"error": f"Not a valid ZIP: {zip_path}"}

    # Determine extraction target
    engine_dir = REPO_ROOT / "engines" / engine
    if not engine_dir.exists():
        logger.error("Engine directory not found: %s", engine_dir)
        return False, {"error": f"Engine dir not found: {engine_dir}"}

    # Extract ZIP
    with zipfile.ZipFile(zip_path, "r") as zf:
        members = zf.namelist()
        logger.info("ZIP contains %d entries", len(members))

        # Detect bundle directory name from ZIP contents
        # Handle both flat (files at root) and nested (engines/excerpting/name/) structures
        zf.extractall(REPO_ROOT if target_dir is None else target_dir)

    # Find the bundle directory
    # Convention: bundle_id from ZIP name (strip _bundle.zip suffix)
    zip_stem = zip_path.stem
    if zip_stem.endswith("_bundle"):
        zip_stem = zip_stem[: -len("_bundle")]

    # Search for the manifest in common locations
    candidate_dirs = [
        engine_dir / zip_stem,
        engine_dir / f"{zip_stem}_collection",
        REPO_ROOT / f"engines/{engine}/{zip_stem}",
    ]

    # Also check nested extraction pattern (engines/excerpting/name/)
    for member in members:
        if member.endswith("00_manifest.yaml"):
            manifest_parent = (REPO_ROOT / member).parent
            if manifest_parent not in candidate_dirs:
                candidate_dirs.insert(0, manifest_parent)

    bundle_dir: Path | None = None
    for candidate in candidate_dirs:
        if candidate.exists() and (candidate / "00_manifest.yaml").exists():
            bundle_dir = candidate
            break

    if bundle_dir is None:
        logger.error("Cannot find bundle directory with 00_manifest.yaml")
        return False, {
            "error": "No 00_manifest.yaml found after extraction",
            "searched": [str(c) for c in candidate_dirs],
        }

    logger.info("Bundle directory: %s", bundle_dir)

    # Validate
    all_errors: list[str] = []

    # 1. Manifest
    manifest, manifest_errors = validate_manifest(bundle_dir / "00_manifest.yaml")
    all_errors.extend(manifest_errors)

    # 2. Source artifacts
    source_dir = bundle_dir / "source_artifacts"
    if not source_dir.exists():
        all_errors.append("Missing source_artifacts/ directory")

    # 3. JSONL files
    for jsonl_file in bundle_dir.glob("*.jsonl"):
        all_errors.extend(validate_jsonl_file(jsonl_file))

    # 4. YAML files
    for yaml_file in bundle_dir.glob("*.yaml"):
        if yaml_file.name == "inventory.json":
            continue
        all_errors.extend(validate_yaml_file(yaml_file))

    # 5. File count check
    if "files_emitted" in manifest:
        expected_count = len(manifest["files_emitted"])
        actual_files = [
            f
            for f in bundle_dir.rglob("*")
            if f.is_file()
            and f.name != "inventory.json"
            and f.suffix != ".zip"
        ]
        actual_count = len(actual_files)
        if actual_count != expected_count:
            all_errors.append(
                f"File count mismatch: manifest says {expected_count}, found {actual_count}"
            )

    # Create inventory
    inventory = create_inventory(bundle_dir, manifest, all_errors)

    # Write inventory.json
    inventory_path = bundle_dir / "inventory.json"
    with open(inventory_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    logger.info("Inventory written to %s", inventory_path)

    # Archive ZIP to source_artifacts
    if source_dir.exists():
        archive_dest = source_dir / zip_path.name
        if not archive_dest.exists():
            import shutil

            shutil.copy2(zip_path, archive_dest)
            logger.info("ZIP archived to %s", archive_dest)

    # Report
    success = len(all_errors) == 0
    status = "PASS" if success else "FAIL"
    logger.info("Intake %s — %d errors", status, len(all_errors))
    for err in all_errors:
        logger.warning("  - %s", err)

    return success, inventory


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="KR bundle intake: unzip → validate → inventory → report"
    )
    parser.add_argument("zip_path", type=Path, help="Path to the bundle ZIP file")
    parser.add_argument(
        "--engine",
        required=True,
        help="Target engine name (e.g., excerpting)",
    )
    parser.add_argument(
        "--target-dir",
        type=Path,
        default=None,
        help="Override extraction target directory",
    )

    args = parser.parse_args()

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    success, inventory = intake_bundle(args.zip_path, args.engine, args.target_dir)

    # Print summary
    print(f"\n{'='*60}")
    print(f"Bundle: {inventory.get('bundle_id', 'UNKNOWN')}")
    print(f"Question: {inventory.get('question_id', 'UNKNOWN')}")
    print(f"Files: {inventory.get('file_count', 0)}")
    print(f"Size: {inventory.get('total_size_bytes', 0):,} bytes")
    print(f"Validation: {'PASS' if inventory.get('validation_passed') else 'FAIL'}")
    if not inventory.get("validation_passed"):
        for err in inventory.get("validation_errors", []):
            print(f"  ERROR: {err}")
    print(f"{'='*60}\n")

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
