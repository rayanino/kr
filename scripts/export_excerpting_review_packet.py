#!/usr/bin/env python3
"""Review packet exporter for excerpting evaluation.

Reads per-book analysis outputs and produces:
  analysis/review_packet.md
  analysis/review_packet.json
  analysis/review_manifest.json

Usage:
  python scripts/export_excerpting_review_packet.py <campaign_dir>
  python scripts/export_excerpting_review_packet.py <campaign_dir> --output-dir <dir>
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

_SCRIPTS_DIR = Path(__file__).resolve().parent
if str(_SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS_DIR))

from excerpting_eval.analysis import analyze_book
from excerpting_eval.ingest import load_book_run
from excerpting_eval.models import (
    BookAnalysisResult,
    CanonicalUnitKey,
    UnitLedgerEntry,
)
from excerpting_eval.packet import (
    assign_lanes,
    build_manifest,
    build_packet_json,
    build_packet_md,
)

logging.basicConfig(
    level=logging.INFO,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Export review packets from excerpting analysis.",
    )
    parser.add_argument(
        "campaign_dir",
        type=Path,
        help="Path to the campaign directory (contains book subdirs)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: <campaign_dir>/analysis/)",
    )
    args = parser.parse_args()

    campaign_dir = args.campaign_dir.resolve()
    output_dir = args.output_dir or (campaign_dir / "analysis")

    # Discover and analyze books
    from analyze_excerpting_campaign import discover_books
    book_dirs = discover_books(campaign_dir)
    if not book_dirs:
        logger.error("No book directories found in %s", campaign_dir)
        sys.exit(1)

    results: list[BookAnalysisResult] = []
    all_candidates = []
    all_ledger: dict[CanonicalUnitKey, UnitLedgerEntry] = {}
    all_excerpts: list[dict] = []

    for book_dir in book_dirs:
        run_data = load_book_run(book_dir)
        result = analyze_book(run_data)
        results.append(result)
        all_candidates.extend(result.review_candidates)
        all_ledger.update(run_data["ledger"])
        all_excerpts.extend(run_data["excerpts"])

    total_units = len(all_ledger)
    total_excerpts = len(all_excerpts)

    logger.info(
        "Loaded %d book(s): %d units, %d excerpts, %d candidates",
        len(results), total_units, total_excerpts, len(all_candidates),
    )

    # Assign to lanes
    lanes = assign_lanes(results, all_candidates, all_ledger, all_excerpts)

    for lane_id, cards in lanes.items():
        logger.info("  %s: %d cards", lane_id, len(cards))

    # Write outputs
    output_dir.mkdir(parents=True, exist_ok=True)

    # review_packet.md
    md = build_packet_md(lanes, results, total_units, total_excerpts)
    (output_dir / "review_packet.md").write_text(md, encoding="utf-8")

    # review_packet.json
    packet_json = build_packet_json(
        lanes, results, total_units, total_excerpts,
    )
    _write_json(output_dir / "review_packet.json", packet_json)

    # review_manifest.json
    manifest = build_manifest(lanes, results, total_units, total_excerpts)
    _write_json(output_dir / "review_manifest.json", manifest)

    total_cards = sum(len(v) for v in lanes.values())
    logger.info(
        "Review packet exported: %d total cards → %s",
        total_cards, output_dir,
    )


def _write_json(path: Path, data: object) -> None:
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
