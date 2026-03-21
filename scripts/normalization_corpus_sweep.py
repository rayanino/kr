#!/usr/bin/env python3
"""Normalization Corpus Sweep — Run normalize_source on the full Shamela collection.

Processes every .htm file in the shamela-export-samples/ directory (20K+ books).
Collects per-book metrics and produces an aggregate report.

This is a DATA COLLECTION script — it does NOT modify any engine code.

Usage:
    python scripts/normalization_corpus_sweep.py [--collection-dir DIR] [--limit N] [--resume]

Output:
    results/normalization_sweep/corpus_sweep.jsonl  — one JSON line per book
    results/normalization_sweep/CORPUS_SWEEP_SUMMARY.md — aggregate report
    results/normalization_sweep/errors.jsonl — detailed error info for crashes
"""

from __future__ import annotations

import argparse
import io
import json
import sys
import time
import traceback
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from bs4 import BeautifulSoup

from engines.normalization.contracts import NormalizedPackage
from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.src.validation import validate_package
from engines.source.contracts import (
    InferredFieldConfidence,
    ScholarReference,
    SourceMetadata,
    TrustworthinessFactor,
)

DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670", "\u0640"}
ARABIC_RANGE = range(0x0600, 0x0700)


def _make_sweep_metadata(source_id: str, is_multi_layer: bool = False) -> SourceMetadata:
    """Build SourceMetadata with sensible defaults for sweep testing."""
    return SourceMetadata(
        source_id=source_id,
        work_id=f"wrk_{source_id}",
        human_label=f"Corpus sweep: {source_id}",
        title_arabic="كتاب",
        author=ScholarReference(
            canonical_id="sch_00001",
            name_arabic="المؤلف",
            confidence=1.0,
            source_of_identification="sweep",
        ),
        science_scope=["unknown"],
        genre="other",
        source_format="shamela_html",
        authority_level="primary",
        structural_format="prose",
        is_multi_layer=is_multi_layer,
        text_layers=[],
        trust_tier="verified",
        trust_score=0.5,
        trust_factors=[
            TrustworthinessFactor(
                name="sweep", weight=1.0, score=0.5, reason="corpus sweep default"
            ),
        ],
        trust_reason="corpus sweep default",
        text_fidelity="unknown",
        text_fidelity_reason="not assessed",
        confidence_scores=InferredFieldConfidence(
            genre=0.5, science_scope=0.5, structural_format=0.5, authority_level=0.5,
        ),
        status="acquired",
        intake_timestamp=datetime.now(timezone.utc).isoformat(),
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen/",
        frozen_hash="sweep",
        frozen_file_hashes={},
    )


def discover_books(collection_dir: Path) -> list[tuple[str, Path]]:
    """Find all Shamela .htm books in the collection directory.

    Handles both single-file books (dir/book.htm) and multi-volume
    books (dir/001.htm, dir/002.htm — takes the first .htm).
    """
    books: list[tuple[str, Path]] = []
    if not collection_dir.exists():
        print(f"ERROR: Collection directory not found: {collection_dir}")
        return books

    for item in sorted(collection_dir.iterdir()):
        if item.is_dir() and not item.name.startswith("."):
            htms = sorted(item.glob("*.htm"))
            if htms:
                books.append((item.name, htms[0]))
        elif item.suffix == ".htm":
            books.append((item.stem, item))

    return books


def count_raw_pages(path: Path) -> int:
    """Count raw PageText divs in HTML."""
    try:
        raw = path.read_text(encoding="utf-8")
        return len(BeautifulSoup(raw, "lxml").find_all("div", class_="PageText"))
    except Exception:
        return -1


def process_book(name: str, path: Path) -> dict[str, Any]:
    """Process one book through normalize_source and collect metrics."""
    source_id = f"sweep_{name[:50]}"
    meta = _make_sweep_metadata(source_id, is_multi_layer=False)
    start_time = time.time()

    try:
        pkg = normalize_source(path, meta)
    except Exception as e:
        elapsed = time.time() - start_time
        return {
            "name": name,
            "path": str(path),
            "status": "CRASH",
            "error_type": type(e).__name__,
            "error_message": str(e)[:500],
            "elapsed_seconds": round(elapsed, 2),
        }

    elapsed = time.time() - start_time

    # Run validation
    try:
        val_result = validate_package(pkg, meta)
        warnings = val_result.warnings
        fatals = [e.message for e in val_result.fatal_errors]
        validation_passed = val_result.passed
    except Exception as e:
        warnings = []
        fatals = [f"Validation crashed: {e}"]
        validation_passed = False

    # Raw page count
    raw_pages = count_raw_pages(path)

    # Content metrics
    total_chars = 0
    arabic_chars = 0
    diacritic_count = 0
    footnote_pages = 0
    multi_layer_units = 0
    has_hadith = 0
    has_quran = 0
    has_verse = 0
    blank_pages = 0
    bc_types: Counter = Counter()
    bc_non_none = 0

    for cu in pkg.content_units:
        text = cu.primary_text
        total_chars += len(text)
        for ch in text:
            if ord(ch) in ARABIC_RANGE:
                arabic_chars += 1
            if ch in DIACRITICS:
                diacritic_count += 1

        if cu.footnotes:
            footnote_pages += 1

        if len(cu.text_layers) >= 2:
            layer_types = {seg.layer_type for seg in cu.text_layers}
            if len(layer_types) >= 2:
                multi_layer_units += 1

        if cu.content_flags.has_hadith_citation:
            has_hadith += 1
        if cu.content_flags.has_quran_citation:
            has_quran += 1
        if cu.content_flags.has_verse:
            has_verse += 1
        if cu.content_flags.is_blank:
            blank_pages += 1

        if cu.boundary_continuity is not None:
            bc_non_none += 1
            bc_types[cu.boundary_continuity.type.value] += 1

    n_units = len(pkg.content_units)
    arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0.0

    # Passaging contract checks (4, 5, 6 from loader.py)
    psg_checks = {
        "check4_count_match": n_units == pkg.manifest.total_content_units,
        "check5_ordered": True,
        "check5_no_gaps": True,
        "check6_division_consistent": True,
    }

    # Check 5: ordered by unit_index, no gaps
    indices = [cu.unit_index for cu in pkg.content_units]
    if indices != sorted(indices):
        psg_checks["check5_ordered"] = False
    if indices != list(range(len(indices))):
        psg_checks["check5_no_gaps"] = False

    # Check 6: division ranges non-overlapping (simplified check)
    def check_siblings(nodes):
        for i in range(1, len(nodes)):
            if nodes[i].start_unit_index <= nodes[i - 1].end_unit_index:
                return False
            if nodes[i].children and not check_siblings(nodes[i].children):
                return False
        if nodes and nodes[0].children and not check_siblings(nodes[0].children):
            return False
        return True

    if pkg.manifest.division_tree:
        psg_checks["check6_division_consistent"] = check_siblings(pkg.manifest.division_tree)

    # Warning categorization
    warn_categories: Counter = Counter()
    for w in warnings:
        if "Division overlap" in w or "overlap" in w.lower():
            warn_categories["division_overlap"] += 1
        elif "Arabic ratio" in w:
            warn_categories["low_arabic_ratio"] += 1
        elif "character run" in w:
            warn_categories["char_run"] += 1
        elif "diacrit" in w.lower():
            warn_categories["diacritics"] += 1
        else:
            warn_categories["other"] += 1

    return {
        "name": name,
        "path": str(path),
        "status": "OK" if validation_passed else "VALIDATION_FAILED",
        "elapsed_seconds": round(elapsed, 2),
        "content_units": n_units,
        "raw_page_divs": raw_pages,
        "page_loss": abs(n_units - raw_pages) if raw_pages >= 0 else -1,
        "arabic_ratio": round(arabic_ratio, 4),
        "diacritic_count": diacritic_count,
        "total_chars": total_chars,
        "footnote_pages": footnote_pages,
        "division_count": len(pkg.manifest.division_tree),
        "layer_count": len(pkg.manifest.layer_map),
        "multi_layer_units": multi_layer_units,
        "blank_pages": blank_pages,
        "bc_coverage": round(bc_non_none / n_units, 4) if n_units > 0 else 0.0,
        "bc_types": dict(bc_types),
        "has_hadith": has_hadith,
        "has_quran": has_quran,
        "has_verse": has_verse,
        "validation_warnings": len(warnings),
        "validation_fatals": len(fatals),
        "warn_categories": dict(warn_categories),
        "psg_contract_checks": psg_checks,
        "auto_upgraded_multi": multi_layer_units > 0,
    }


def write_summary(results: list[dict], output_dir: Path, elapsed_total: float):
    """Write the aggregate summary report."""
    ok = [r for r in results if r["status"] == "OK"]
    crashes = [r for r in results if r["status"] == "CRASH"]
    val_fails = [r for r in results if r["status"] == "VALIDATION_FAILED"]

    report = f"""# Normalization Corpus Sweep — Summary Report

**Date:** {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}
**Total books:** {len(results)}
**Processing time:** {elapsed_total:.0f} seconds ({elapsed_total/60:.1f} minutes)
**Mean per-book:** {elapsed_total/len(results):.2f}s

## Status Distribution

| Status | Count | Percentage |
|--------|-------|-----------|
| OK | {len(ok)} | {len(ok)/len(results)*100:.1f}% |
| CRASH | {len(crashes)} | {len(crashes)/len(results)*100:.1f}% |
| VALIDATION_FAILED | {len(val_fails)} | {len(val_fails)/len(results)*100:.1f}% |

## Crash Analysis

"""
    if crashes:
        error_types = Counter(r["error_type"] for r in crashes)
        report += "| Error Type | Count | Example |\n|---|---|---|\n"
        for etype, count in error_types.most_common(20):
            example = next(r for r in crashes if r["error_type"] == etype)
            msg = example["error_message"][:100].replace("|", "\\|")
            report += f"| {etype} | {count} | {msg} |\n"
    else:
        report += "No crashes.\n"

    if ok:
        page_losses = [r["page_loss"] for r in ok if r["page_loss"] >= 0]
        arabic_ratios = [r["arabic_ratio"] for r in ok]
        diacritics = [r["diacritic_count"] for r in ok]
        units = [r["content_units"] for r in ok]

        pl_min = min(page_losses) if page_losses else "N/A"
        pl_max = max(page_losses) if page_losses else "N/A"
        pl_mean = f"{sum(page_losses)/len(page_losses):.1f}" if page_losses else "N/A"

        report += f"""
## Content Unit Statistics

| Metric | Min | Max | Mean | Median |
|--------|-----|-----|------|--------|
| Content units | {min(units)} | {max(units)} | {sum(units)/len(units):.0f} | {sorted(units)[len(units)//2]} |
| Page loss | {pl_min} | {pl_max} | {pl_mean} | — |
| Arabic ratio | {min(arabic_ratios):.2%} | {max(arabic_ratios):.2%} | {sum(arabic_ratios)/len(arabic_ratios):.2%} | — |
| Diacritics/book | {min(diacritics)} | {max(diacritics)} | {sum(diacritics)/len(diacritics):.0f} | — |

## Page Loss Distribution

| Page Loss | Count | Percentage |
|-----------|-------|-----------|
"""
        loss_dist = Counter(r["page_loss"] for r in ok if r["page_loss"] >= 0)
        for loss in sorted(loss_dist.keys()):
            report += f"| {loss} | {loss_dist[loss]} | {loss_dist[loss]/len(ok)*100:.1f}% |\n"

        high_loss = [r for r in ok if r.get("page_loss", 0) > 5]
        if high_loss:
            report += f"\n**Books with page loss > 5:** {len(high_loss)}\n"
            for r in high_loss[:20]:
                report += f"- {r['name']}: loss={r['page_loss']} (raw={r['raw_page_divs']}, units={r['content_units']})\n"

        low_arabic = [r for r in ok if r["arabic_ratio"] < 0.70]
        report += f"\n## Arabic Ratio\n\nBooks below 70%: {len(low_arabic)} ({len(low_arabic)/len(ok)*100:.1f}%)\n"
        if low_arabic:
            for r in sorted(low_arabic, key=lambda x: x["arabic_ratio"])[:20]:
                report += f"- {r['name']}: {r['arabic_ratio']:.2%}\n"

        # Warning patterns
        all_warns = Counter()
        for r in ok:
            for cat, count in r.get("warn_categories", {}).items():
                all_warns[cat] += count
        total_warns = sum(all_warns.values())
        report += f"\n## Warning Patterns ({total_warns} total)\n\n"
        for cat, count in all_warns.most_common():
            report += f"- {cat}: {count}\n"

        # Multi-layer detection
        auto_multi = [r for r in ok if r.get("auto_upgraded_multi", False)]
        report += f"\n## Multi-Layer Detection\n\n"
        report += f"Books with multi-layer segments: {len(auto_multi)} ({len(auto_multi)/len(ok)*100:.1f}%)\n"

        # Passaging contract
        psg_fail_count = sum(
            1 for r in ok
            if not all(r.get("psg_contract_checks", {}).values())
        )
        report += f"\n## Passaging Contract Alignment\n\n"
        report += f"Books failing any passaging input check: {psg_fail_count}/{len(ok)}\n"

        # Boundary continuity
        bc_coverages = [r["bc_coverage"] for r in ok]
        report += f"\n## Boundary Continuity\n\n"
        report += f"Mean coverage: {sum(bc_coverages)/len(bc_coverages):.2%}\n"
        report += f"Books with 0% BC: {sum(1 for c in bc_coverages if c == 0)}\n"

        # Content flags
        report += f"\n## Content Flags (aggregate)\n\n"
        report += f"- Hadith pages: {sum(r['has_hadith'] for r in ok)}\n"
        report += f"- Quran pages: {sum(r['has_quran'] for r in ok)}\n"
        report += f"- Verse pages: {sum(r['has_verse'] for r in ok)}\n"

    with open(output_dir / "CORPUS_SWEEP_SUMMARY.md", "w", encoding="utf-8") as f:
        f.write(report)


def main():
    parser = argparse.ArgumentParser(description="Normalization corpus sweep")
    parser.add_argument(
        "--collection-dir",
        type=Path,
        default=Path("shamela-export-samples"),
        help="Path to the collection directory (default: shamela-export-samples/)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/normalization_sweep"),
        help="Output directory for results",
    )
    parser.add_argument("--limit", type=int, default=0, help="Max books to process (0=all)")
    parser.add_argument("--resume", action="store_true", help="Skip books already in results")
    args = parser.parse_args()

    # Discover books
    books = discover_books(args.collection_dir)
    if not books:
        print(f"No books found in {args.collection_dir}")
        sys.exit(1)

    if args.limit > 0:
        books = books[:args.limit]

    print(f"Found {len(books)} books in {args.collection_dir}")

    # Setup output
    args.output_dir.mkdir(parents=True, exist_ok=True)
    results_path = args.output_dir / "corpus_sweep.jsonl"
    errors_path = args.output_dir / "errors.jsonl"

    # Resume support
    processed: set[str] = set()
    if args.resume and results_path.exists():
        with open(results_path, encoding="utf-8") as f:
            for line in f:
                try:
                    r = json.loads(line)
                    processed.add(r["name"])
                except json.JSONDecodeError:
                    pass
        print(f"Resuming: {len(processed)} books already processed")

    # Process
    results: list[dict] = []
    start_total = time.time()
    ok_count = 0
    crash_count = 0

    with open(results_path, "a", encoding="utf-8") as f_results, \
         open(errors_path, "a", encoding="utf-8") as f_errors:

        for i, (name, path) in enumerate(books):
            if name in processed:
                continue

            if (i + 1) % 100 == 0 or i == 0:
                elapsed = time.time() - start_total
                rate = (i + 1 - len(processed)) / elapsed if elapsed > 0 else 0
                eta = (len(books) - i - 1) / rate / 60 if rate > 0 else 0
                print(f"  [{i+1}/{len(books)}] {name}  "
                      f"({ok_count} ok, {crash_count} crash, "
                      f"{rate:.1f} books/sec, ETA {eta:.0f}min)")

            result = process_book(name, path)
            results.append(result)

            # Write immediately (streaming)
            f_results.write(json.dumps(result, ensure_ascii=False) + "\n")
            f_results.flush()

            if result["status"] == "CRASH":
                crash_count += 1
                f_errors.write(json.dumps(result, ensure_ascii=False) + "\n")
                f_errors.flush()
            else:
                ok_count += 1

    elapsed_total = time.time() - start_total

    # Load all results (including from resume)
    all_results = []
    with open(results_path, encoding="utf-8") as f:
        for line in f:
            try:
                all_results.append(json.loads(line))
            except json.JSONDecodeError:
                pass

    # Write summary
    write_summary(all_results, args.output_dir, elapsed_total)

    print(f"\n{'='*60}")
    print(f"CORPUS SWEEP COMPLETE")
    print(f"{'='*60}")
    print(f"Total: {len(all_results)} books")
    print(f"OK: {sum(1 for r in all_results if r['status'] == 'OK')}")
    print(f"Crashes: {sum(1 for r in all_results if r['status'] == 'CRASH')}")
    print(f"Validation failed: {sum(1 for r in all_results if r['status'] == 'VALIDATION_FAILED')}")
    print(f"Time: {elapsed_total:.0f}s ({elapsed_total/60:.1f}min)")
    print(f"\nResults: {results_path}")
    print(f"Summary: {args.output_dir / 'CORPUS_SWEEP_SUMMARY.md'}")
    if crash_count > 0:
        print(f"Errors: {errors_path}")


if __name__ == "__main__":
    main()
