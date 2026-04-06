#!/usr/bin/env python3
"""S-02: Initialize verification session for a batch.

Creates verification_status.json with all files from inventory.json set
to UNVERIFIED, and generates a unique batch_verification_run_id.

Usage:
    python scripts/batch_verification_init.py --batch-dir path/to/bundle
    python scripts/batch_verification_init.py --batch-dir path/to/bundle --inventory custom_inventory.json
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)


def load_inventory(path: Path) -> dict:
    """Load and validate inventory.json structure."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    if "files" not in data or not isinstance(data["files"], list):
        raise ValueError(f"Invalid inventory.json: missing 'files' array in {path}")
    if "batch_id" not in data:
        raise ValueError(f"Invalid inventory.json: missing 'batch_id' in {path}")
    return data


def build_verification_status(inventory: dict) -> dict:
    """Build verification_status.json from inventory data."""
    run_id = str(uuid.uuid4())
    entries = []
    for file_entry in inventory["files"]:
        entries.append({
            "path": file_entry["path"],
            "sha256": file_entry["sha256"],
            "status": "UNVERIFIED",
            "verified_at": None,
            "verified_by": None,
            "notes": None,
        })
    return {
        "batch_verification_run_id": run_id,
        "batch_id": inventory["batch_id"],
        "created_at": datetime.now(timezone.utc).isoformat(),
        "total_files": len(entries),
        "verified_count": 0,
        "entries": entries,
    }


def main() -> int:
    """Entry point: load inventory, create verification_status.json."""
    parser = argparse.ArgumentParser(
        description="S-02: Initialize verification session for a batch.",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Path to the batch collection directory.",
    )
    parser.add_argument(
        "--inventory",
        type=Path,
        default=None,
        help="Path to inventory.json (default: <batch-dir>/inventory.json).",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path (default: <batch-dir>/verification_status.json).",
    )
    args = parser.parse_args()

    batch_dir: Path = args.batch_dir.resolve()
    if not batch_dir.is_dir():
        log.error("Batch directory does not exist: %s", batch_dir)
        return 1

    inventory_path: Path = (args.inventory or batch_dir / "inventory.json").resolve()
    if not inventory_path.is_file():
        log.error("Inventory file not found: %s", inventory_path)
        return 1

    output_path: Path = (
        args.output or batch_dir / "verification_status.json"
    ).resolve()

    log.info("Loading inventory from %s", inventory_path)
    try:
        inventory = load_inventory(inventory_path)
    except (json.JSONDecodeError, ValueError) as e:
        log.error("Failed to load inventory: %s", e)
        return 1

    status = build_verification_status(inventory)
    log.info(
        "Initialized verification run %s with %d files (all UNVERIFIED)",
        status["batch_verification_run_id"],
        status["total_files"],
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)
    log.info("Verification status written to %s", output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
