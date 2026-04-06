#!/usr/bin/env python3
"""S-01: Hash-bound file inventory with SHA-256 per file.

Scans a batch collection directory and produces inventory.json containing
every file's path, SHA-256 hash, size in bytes, line count, and layer
classification (A = source_artifacts/*, B = numbered files 01_*..14_*).

Usage:
    python scripts/batch_inventory.py --batch-dir engines/excerpting/chatgpt_g1_collection_bundle
    python scripts/batch_inventory.py --batch-dir path/to/bundle --output custom_inventory.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
log = logging.getLogger(__name__)

LAYER_A_DIR = "source_artifacts"
LAYER_B_PATTERN = re.compile(r"^[0-9]{2}_")


def sha256_of_file(path: Path) -> str:
    """Compute SHA-256 hex digest of a file."""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def count_lines(path: Path) -> int:
    """Count lines in a text file, returning 0 for binary/unreadable."""
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return sum(1 for _ in f)
    except Exception:
        return 0


def classify_layer(relative_path: Path) -> str:
    """Classify a file as layer A (source_artifacts) or B (numbered)."""
    parts = relative_path.parts
    if parts and parts[0] == LAYER_A_DIR:
        return "A"
    if parts and LAYER_B_PATTERN.match(parts[0]):
        return "B"
    return "UNKNOWN"


def scan_directory(batch_dir: Path) -> list[dict[str, str | int]]:
    """Scan batch directory and return file inventory entries."""
    entries: list[dict[str, str | int]] = []
    for file_path in sorted(batch_dir.rglob("*")):
        if not file_path.is_file():
            continue
        relative = file_path.relative_to(batch_dir)
        entry = {
            "path": str(relative),
            "sha256": sha256_of_file(file_path),
            "size_bytes": file_path.stat().st_size,
            "line_count": count_lines(file_path),
            "layer": classify_layer(relative),
        }
        entries.append(entry)
        log.debug("Inventoried: %s (layer %s)", relative, entry["layer"])
    return entries


def build_inventory(batch_dir: Path) -> dict:
    """Build the full inventory document."""
    files = scan_directory(batch_dir)
    return {
        "batch_id": str(uuid.uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "batch_dir": str(batch_dir.resolve()),
        "file_count": len(files),
        "files": files,
    }


def main() -> int:
    """Entry point: parse args, scan, write inventory.json."""
    parser = argparse.ArgumentParser(
        description="S-01: Hash-bound file inventory with SHA-256 per file.",
    )
    parser.add_argument(
        "--batch-dir",
        type=Path,
        required=True,
        help="Path to the batch collection directory to inventory.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Output path for inventory.json (default: <batch-dir>/inventory.json).",
    )
    args = parser.parse_args()

    batch_dir: Path = args.batch_dir.resolve()
    if not batch_dir.is_dir():
        log.error("Batch directory does not exist: %s", batch_dir)
        return 1

    output_path: Path = (args.output or batch_dir / "inventory.json").resolve()

    log.info("Scanning batch directory: %s", batch_dir)
    inventory = build_inventory(batch_dir)
    log.info("Found %d files", inventory["file_count"])

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(inventory, f, indent=2, ensure_ascii=False)
    log.info("Inventory written to %s", output_path)

    return 0


if __name__ == "__main__":
    sys.exit(main())
