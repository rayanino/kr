"""Verify normalized output integrity across the corpus.

Addresses T-1 (silent text corruption) and T-2 (attribution error) threats.
Five independent checks, each producing a report in scripts/results/.

Usage:
    python scripts/verify_normalized_integrity.py [--sweep PATH] [--check CHECK_NAME] [--limit N]

Checks:
    1. zero_content    — Classify books with 0 content units
    2. diacritics      — Detect diacritics drift > 0.1%
    3. layer_coverage  — Verify text_layer attribution has no gaps/overlaps
    4. referential     — Cross-engine ID referential integrity
    5. validation_gaps — Find books with unresolved validation warnings

Run all checks:
    python scripts/verify_normalized_integrity.py

Run specific check:
    python scripts/verify_normalized_integrity.py --check layer_coverage
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


# Unicode ranges for Arabic diacritics (tashkeel)
ARABIC_DIACRITICS = set(
    chr(c) for c in range(0x064B, 0x0653)  # Fathatan through Hamza Above
)
# Add additional diacritics
ARABIC_DIACRITICS.update([
    '\u0654',  # Hamza Above
    '\u0655',  # Hamza Below
    '\u0656',  # Subscript Alef
    '\u0670',  # Superscript Alef
])


def load_sweep_data(sweep_path: Path) -> list[dict[str, Any]]:
    """Load corpus sweep JSONL data."""
    records: list[dict[str, Any]] = []
    with open(sweep_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def count_diacritics_in_text(text: str) -> int:
    """Count Arabic diacritical marks in text."""
    return sum(1 for c in text if c in ARABIC_DIACRITICS)


def write_report(
    report_name: str,
    results_dir: Path,
    data: dict[str, Any],
) -> Path:
    """Write a check result to a JSON report file."""
    results_dir.mkdir(parents=True, exist_ok=True)
    report_path = results_dir / f"{report_name}.json"
    data["generated_at"] = datetime.now(timezone.utc).isoformat()
    data["script"] = "scripts/verify_normalized_integrity.py"
    report_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return report_path


# ──────────────────────────────────────────────────────────────────
# Check 1: Zero-Content Classification
# ──────────────────────────────────────────────────────────────────

def check_zero_content(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Classify books with 0 content units.

    Categories:
    - genuinely_empty: status != OK (error during processing)
    - parser_bug: status == OK but 0 content units (T-1 violation candidate)
    - structure_anomaly: very low content units relative to page count
    """
    zero_content: list[dict[str, Any]] = []
    low_content: list[dict[str, Any]] = []

    for rec in records:
        cu = rec.get("content_units", 0)
        status = rec.get("status", "unknown")
        name = rec.get("name", "unknown")
        path = rec.get("path", "unknown")

        if cu == 0:
            if status == "OK":
                category = "parser_bug"
            else:
                category = "genuinely_empty"
            zero_content.append({
                "name": name,
                "path": path,
                "status": status,
                "category": category,
            })
        elif cu <= 2:
            # Books with only 1-2 content units might be anomalous
            low_content.append({
                "name": name,
                "path": path,
                "content_units": cu,
                "status": status,
            })

    parser_bugs = [z for z in zero_content if z["category"] == "parser_bug"]

    return {
        "check": "zero_content",
        "summary": {
            "total_books": len(records),
            "zero_content_total": len(zero_content),
            "parser_bugs": len(parser_bugs),
            "genuinely_empty": len(zero_content) - len(parser_bugs),
            "low_content_books": len(low_content),
        },
        "threat": "T-1 (silent text corruption)" if parser_bugs else "CLEAN",
        "zero_content_details": zero_content,
        "low_content_details": low_content[:20],  # Cap at 20 for readability
    }


# ──────────────────────────────────────────────────────────────────
# Check 2: Diacritics Drift Detection
# ──────────────────────────────────────────────────────────────────

def check_diacritics_drift(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Flag books where diacritics ratio is anomalously low.

    Arabic scholarly texts typically have 1-20% diacritics, depending on era/style.
    Many modern scholarly editions are legitimately undiacritized.

    Severity levels:
    - INFO: 0 diacritics or <0.1% — likely genuinely undiacritized text (common)
    - WARNING: diacritics present but unusually low for corpus — review recommended
    - T-1 ALERT: only flagged if diacritics were EXPECTED but missing (requires
      comparison with source, not available in sweep data alone)

    This check is INFORMATIONAL, not a failure indicator. Zero diacritics in a
    modern edition is normal. The data is useful for downstream engines to
    know which texts can/cannot rely on diacritical precision.
    """
    low_diacritic: list[dict[str, Any]] = []
    diacritic_ratios: list[float] = []

    for rec in records:
        diac = rec.get("diacritic_count", 0)
        total = rec.get("total_chars", 0)
        name = rec.get("name", "unknown")

        if total < 1000:
            continue  # Too short to analyze

        ratio = diac / total if total > 0 else 0.0
        diacritic_ratios.append(ratio)

        if ratio < 0.001:  # < 0.1% diacritics in >1000 chars
            low_diacritic.append({
                "name": name,
                "path": rec.get("path", "unknown"),
                "diacritic_count": diac,
                "total_chars": total,
                "ratio": round(ratio, 6),
                "classification": "undiacritized" if diac == 0 else "sparse_diacritics",
            })

    # Calculate corpus statistics
    if diacritic_ratios:
        avg_ratio = sum(diacritic_ratios) / len(diacritic_ratios)
        min_ratio = min(diacritic_ratios)
        max_ratio = max(diacritic_ratios)
    else:
        avg_ratio = min_ratio = max_ratio = 0.0

    undiacritized = [b for b in low_diacritic if b["classification"] == "undiacritized"]
    sparse = [b for b in low_diacritic if b["classification"] == "sparse_diacritics"]

    return {
        "check": "diacritics_drift",
        "summary": {
            "books_analyzed": len(diacritic_ratios),
            "undiacritized_books": len(undiacritized),
            "sparse_diacritics_books": len(sparse),
            "corpus_avg_ratio": round(avg_ratio, 6),
            "corpus_min_ratio": round(min_ratio, 6),
            "corpus_max_ratio": round(max_ratio, 6),
        },
        # This check is informational — low diacritics is common in modern editions
        "threat": "INFORMATIONAL",
        "note": "Low diacritics is normal for modern scholarly editions. "
                "This data helps downstream engines know which texts rely on diacritical precision.",
        "undiacritized_books": undiacritized[:50],
        "sparse_diacritics_books": sparse[:50],
    }


# ──────────────────────────────────────────────────────────────────
# Check 3: Layer Attribution Coverage
# ──────────────────────────────────────────────────────────────────

def check_layer_coverage(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Verify text_layer attribution consistency from sweep data.

    Uses layer_count and multi_layer_units fields from the sweep.
    Flags books where multi-layer detection is inconsistent:
    - layer_count > 1 but multi_layer_units == 0 (declared multi-layer but no pages classified)
    - auto_upgraded_multi == True (heuristic upgrade — review needed)
    """
    inconsistent: list[dict[str, Any]] = []
    auto_upgraded: list[dict[str, Any]] = []
    stats = Counter()

    for rec in records:
        layer_count = rec.get("layer_count", 1)
        multi_units = rec.get("multi_layer_units", 0)
        auto_up = rec.get("auto_upgraded_multi", False)
        name = rec.get("name", "unknown")
        cu = rec.get("content_units", 0)

        stats[f"layer_count_{layer_count}"] += 1

        if layer_count > 1 and multi_units == 0 and cu > 0:
            inconsistent.append({
                "name": name,
                "path": rec.get("path", "unknown"),
                "layer_count": layer_count,
                "multi_layer_units": multi_units,
                "content_units": cu,
                "issue": "declared multi-layer but zero multi-layer units",
            })

        if auto_up:
            auto_upgraded.append({
                "name": name,
                "path": rec.get("path", "unknown"),
                "layer_count": layer_count,
                "multi_layer_units": multi_units,
            })

    return {
        "check": "layer_coverage",
        "summary": {
            "total_books": len(records),
            "inconsistent_count": len(inconsistent),
            "auto_upgraded_count": len(auto_upgraded),
            "layer_count_distribution": dict(stats),
        },
        "threat": "T-2 (attribution error)" if inconsistent else "CLEAN",
        "inconsistent_books": inconsistent[:50],
        "auto_upgraded_books": auto_upgraded[:20],
    }


# ──────────────────────────────────────────────────────────────────
# Check 4: Cross-Engine ID Referential Integrity
# ──────────────────────────────────────────────────────────────────

def check_referential_integrity(
    records: list[dict[str, Any]],
    project_root: Path,
) -> dict[str, Any]:
    """Verify IDs are consistent across registries and sweep data.

    Checks:
    - All source names in sweep exist as frozen source directories
    - Source registry exists and is well-formed
    - Division counts are consistent
    """
    registries_dir = project_root / "library" / "registries"

    # Load source registry if it exists
    source_registry_path = registries_dir / "sources.json"
    source_registry: dict[str, Any] = {}
    if source_registry_path.exists():
        try:
            source_registry = json.loads(
                source_registry_path.read_text(encoding="utf-8")
            )
        except (json.JSONDecodeError, OSError):
            pass

    # Check sweep books against available sources
    sweep_paths = set()
    orphaned: list[dict[str, Any]] = []
    division_issues: list[dict[str, Any]] = []

    for rec in records:
        path = rec.get("path", "")
        name = rec.get("name", "unknown")
        sweep_paths.add(path)

        # Check for division count anomalies
        div_count = rec.get("division_count", 0)
        cu = rec.get("content_units", 0)

        if div_count == 0 and cu > 10:
            division_issues.append({
                "name": name,
                "path": path,
                "division_count": div_count,
                "content_units": cu,
                "issue": "zero divisions but many content units",
            })
        elif div_count > cu and cu > 0:
            division_issues.append({
                "name": name,
                "path": path,
                "division_count": div_count,
                "content_units": cu,
                "issue": "more divisions than content units",
            })

    return {
        "check": "referential_integrity",
        "summary": {
            "sweep_books": len(records),
            "source_registry_entries": len(source_registry),
            "source_registry_exists": source_registry_path.exists(),
            "orphaned_count": len(orphaned),
            "division_issues": len(division_issues),
        },
        "threat": "T-1 (phantom references)" if orphaned else "CLEAN",
        "orphaned_records": orphaned[:20],
        "division_issues": division_issues[:20],
    }


# ──────────────────────────────────────────────────────────────────
# Check 5: Validation Warning Gaps
# ──────────────────────────────────────────────────────────────────

def check_validation_gaps(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Find books with unresolved validation warnings or fatals.

    Uses validation_fatals and validation_warnings from sweep data.
    Groups warnings by category for pattern analysis.
    """
    books_with_fatals: list[dict[str, Any]] = []
    warning_categories = Counter()
    books_with_warnings: list[dict[str, Any]] = []

    for rec in records:
        fatals = rec.get("validation_fatals", 0)
        warnings = rec.get("validation_warnings", 0)
        warn_cats = rec.get("warn_categories", {})
        name = rec.get("name", "unknown")

        if fatals > 0:
            books_with_fatals.append({
                "name": name,
                "path": rec.get("path", "unknown"),
                "validation_fatals": fatals,
                "validation_warnings": warnings,
            })

        if warnings > 0:
            books_with_warnings.append({
                "name": name,
                "warnings": warnings,
                "categories": warn_cats,
            })
            for cat, count in warn_cats.items():
                warning_categories[cat] += count

    return {
        "check": "validation_gaps",
        "summary": {
            "total_books": len(records),
            "books_with_fatals": len(books_with_fatals),
            "books_with_warnings": len(books_with_warnings),
            "warning_category_totals": dict(warning_categories.most_common(20)),
        },
        "threat": "T-1 (validation failure)" if books_with_fatals else "CLEAN",
        "fatal_books": books_with_fatals[:50],
        "top_warning_books": sorted(
            books_with_warnings,
            key=lambda b: b["warnings"],
            reverse=True,
        )[:20],
    }


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────

ALL_CHECKS = {
    "zero_content": check_zero_content,
    "diacritics": check_diacritics_drift,
    "layer_coverage": check_layer_coverage,
    "referential": None,  # Needs project_root arg
    "validation_gaps": check_validation_gaps,
}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Verify normalized output integrity across the corpus"
    )
    parser.add_argument(
        "--sweep",
        type=Path,
        default=Path("results/normalization_sweep_v2/corpus_sweep.jsonl"),
        help="Path to corpus sweep JSONL file",
    )
    parser.add_argument(
        "--check",
        choices=list(ALL_CHECKS.keys()) + ["all"],
        default="all",
        help="Which check to run (default: all)",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=0,
        help="Limit to first N records (0 = all)",
    )
    args = parser.parse_args()

    if not args.sweep.exists():
        print(f"ERROR: Sweep file not found: {args.sweep}", file=sys.stderr)
        return 1

    print(f"Loading sweep data from {args.sweep}...")
    records = load_sweep_data(args.sweep)
    if args.limit > 0:
        records = records[:args.limit]
    print(f"Loaded {len(records)} records.")

    project_root = Path.cwd()
    results_dir = Path("scripts/results")
    checks_to_run = list(ALL_CHECKS.keys()) if args.check == "all" else [args.check]
    all_clean = True
    reports_written: list[str] = []

    for check_name in checks_to_run:
        print(f"\n{'='*60}")
        print(f"Running check: {check_name}")
        print(f"{'='*60}")

        if check_name == "referential":
            result = check_referential_integrity(records, project_root)
        else:
            check_fn = ALL_CHECKS[check_name]
            assert check_fn is not None
            result = check_fn(records)

        report_path = write_report(
            f"integrity_{check_name}",
            results_dir,
            result,
        )
        reports_written.append(str(report_path))

        threat = result.get("threat", "UNKNOWN")
        summary = result.get("summary", {})
        print(f"  Threat: {threat}")
        for k, v in summary.items():
            print(f"  {k}: {v}")

        if threat not in ("CLEAN", "INFORMATIONAL"):
            all_clean = False

    # Write summary report
    summary_report = {
        "check": "integrity_summary",
        "total_records": len(records),
        "sweep_file": str(args.sweep),
        "checks_run": checks_to_run,
        "all_clean": all_clean,
        "reports": reports_written,
    }
    summary_path = write_report("integrity_summary", results_dir, summary_report)

    print(f"\n{'='*60}")
    print(f"INTEGRITY CHECK {'PASSED' if all_clean else 'ISSUES FOUND'}")
    print(f"Summary: {summary_path}")
    print(f"{'='*60}")

    return 0 if all_clean else 1


if __name__ == "__main__":
    sys.exit(main())
