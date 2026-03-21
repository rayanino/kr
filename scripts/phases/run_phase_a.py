"""Phase A: Deterministic sweep — format detection, extraction, hashing.

Runs Steps 1-3 of the source engine pipeline on every item in a collection
directory. No LLM calls, no staging locks, no filesystem side effects on
the collection. All output goes to the output directory.

Usage:
    python scripts/run_phase_a.py COLLECTION_DIR [--output-dir DIR] [--limit N] [--resume]
"""

from __future__ import annotations

import argparse
import json
import sys
import time
import traceback
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from engines.source.contracts import SourceFormat
from engines.source.src.exceptions import SourceEngineError
from engines.source.src.extractors import extract_metadata
from engines.source.src.format_detection import detect_format
from engines.source.src.staging import (
    _collect_source_files,
    compute_composite_hash,
    compute_file_hash,
)

# ──────────────────────────────────────────────────────────────────
# Filename sanitization
# ──────────────────────────────────────────────────────────────────

_INVALID_CHARS = set('<>:"/\\|?*')


def sanitize_filename(name: str, used_names: set[str]) -> str:
    """Sanitize a source name for use as a JSON output filename.

    Replaces Windows-invalid characters, truncates to 200 chars,
    and appends _2, _3, etc. on collision.
    """
    sanitized = "".join(c if c not in _INVALID_CHARS else "_" for c in name)
    sanitized = sanitized[:200]

    if sanitized not in used_names:
        used_names.add(sanitized)
        return sanitized

    suffix = 2
    while f"{sanitized}_{suffix}" in used_names:
        suffix += 1
    result = f"{sanitized}_{suffix}"
    used_names.add(result)
    return result


# ──────────────────────────────────────────────────────────────────
# Per-item processing
# ──────────────────────────────────────────────────────────────────


def _make_source_error(exc: SourceEngineError) -> dict[str, Any]:
    """Extract structured error info from a SourceEngineError."""
    return {
        "error_code": exc.error.error_code.value,
        "severity": exc.error.severity.value,
        "message": exc.error.message,
        "context": exc.error.context or {},
    }


def _make_internal_error(exc: Exception) -> dict[str, Any]:
    """Create error info for an unexpected (non-SourceEngineError) exception."""
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)
    tb_str = "".join(tb)[:500]
    return {
        "error_code": "SRC_INTERNAL_ERROR",
        "severity": "fatal",
        "message": f"{type(exc).__name__}: {exc}",
        "context": {"exception_type": type(exc).__name__, "traceback": tb_str},
    }


def process_item(item_path: Path, collection_dir: Path) -> dict[str, Any]:
    """Process a single collection item through format detection, hashing, extraction.

    Returns a result dict with all fields populated (or null on failure).
    """
    source_name = item_path.name
    source_path_relative = str(item_path.relative_to(collection_dir))
    start = time.perf_counter()

    source_format: str | None = None
    file_hashes: dict[str, str] | None = None
    composite_hash: str | None = None
    extracted_metadata: dict[str, Any] | None = None
    quality_issues: list[str] | None = None
    error: dict[str, Any] | None = None

    # Step 1: Format detection
    fmt: SourceFormat | None = None
    try:
        fmt = detect_format(item_path)
        source_format = fmt.value
    except SourceEngineError as exc:
        error = _make_source_error(exc)
    except Exception as exc:
        error = _make_internal_error(exc)

    if error is not None:
        elapsed_ms = round((time.perf_counter() - start) * 1000, 1)
        return {
            "source_name": source_name,
            "source_path_relative": source_path_relative,
            "status": "error",
            "source_format": source_format,
            "composite_hash": composite_hash,
            "file_hashes": file_hashes,
            "extracted_metadata": extracted_metadata,
            "quality_issues": quality_issues,
            "processing_time_ms": elapsed_ms,
            "error": error,
        }

    # Step 2: File collection + hashing (independent of step 3)
    hash_error: dict[str, Any] | None = None
    try:
        files = _collect_source_files(item_path)
        file_hashes = {f.name: compute_file_hash(f) for f in files}
        composite_hash = compute_composite_hash(file_hashes)
    except SourceEngineError as exc:
        hash_error = _make_source_error(exc)
    except Exception as exc:
        hash_error = _make_internal_error(exc)

    # Step 3: Metadata extraction (independent of step 2)
    extract_error: dict[str, Any] | None = None
    try:
        extracted_metadata = extract_metadata(item_path, fmt)
        # Pull quality issues from the assembled output
        fmt_meta = extracted_metadata.get("format_specific_metadata") or {}
        quality_issues = fmt_meta.get("quality_issues", [])
    except SourceEngineError as exc:
        extract_error = _make_source_error(exc)
    except Exception as exc:
        extract_error = _make_internal_error(exc)

    # Determine overall status and error
    if hash_error and extract_error:
        # Both failed — report extraction error as primary
        error = extract_error
    elif extract_error:
        error = extract_error
    elif hash_error:
        error = hash_error

    status = "error" if error else "success"
    elapsed_ms = round((time.perf_counter() - start) * 1000, 1)

    return {
        "source_name": source_name,
        "source_path_relative": source_path_relative,
        "status": status,
        "source_format": source_format,
        "composite_hash": composite_hash,
        "file_hashes": file_hashes,
        "extracted_metadata": extracted_metadata,
        "quality_issues": quality_issues,
        "processing_time_ms": elapsed_ms,
        "error": error,
    }


# ──────────────────────────────────────────────────────────────────
# Summary generation
# ──────────────────────────────────────────────────────────────────


def build_summary(
    results: list[dict[str, Any]],
    collection_path: str,
    total_items: int,
    total_seconds: float,
    duplicate_groups: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build the PHASE_A_SUMMARY.json aggregate."""
    successful = sum(1 for r in results if r["status"] == "success")
    errors = sum(1 for r in results if r["status"] == "error")

    # Errors by code
    errors_by_code: dict[str, int] = {}
    for r in results:
        if r["error"]:
            code = r["error"]["error_code"]
            errors_by_code[code] = errors_by_code.get(code, 0) + 1

    # Format counts
    format_counts: dict[str, int] = {}
    for r in results:
        if r["source_format"]:
            fmt = r["source_format"]
            format_counts[fmt] = format_counts.get(fmt, 0) + 1

    # Field coverage — dynamic, from successful extractions only
    field_counts: dict[str, int] = {}
    success_count = 0
    for r in results:
        if r["status"] == "success" and r["extracted_metadata"]:
            success_count += 1
            for key, val in r["extracted_metadata"].items():
                if key.startswith("_") or key == "format_specific_metadata":
                    continue
                if val is not None and val != "" and val != []:
                    field_counts[key] = field_counts.get(key, 0) + 1

    field_coverage = {}
    if success_count > 0:
        for field, count in sorted(field_counts.items(), key=lambda x: -x[1]):
            field_coverage[field] = {
                "count": count,
                "pct": round(count / success_count * 100, 1),
            }

    # Multi-volume vs single file
    multi_volume = 0
    single_file = 0
    for r in results:
        if r["source_format"] == "shamela_html" and r["extracted_metadata"]:
            if r["extracted_metadata"].get("is_multi_volume", False):
                multi_volume += 1
            else:
                single_file += 1

    # Quality issue counts
    quality_issue_counts: dict[str, int] = {}
    for r in results:
        if r["quality_issues"]:
            for issue in r["quality_issues"]:
                if isinstance(issue, dict):
                    issue_type = issue.get("check", "unknown")
                else:
                    issue_type = str(issue)
                quality_issue_counts[issue_type] = (
                    quality_issue_counts.get(issue_type, 0) + 1
                )

    # Timing
    slowest_book = {"name": "", "ms": 0.0}
    for r in results:
        if r["processing_time_ms"] > slowest_book["ms"]:
            slowest_book = {"name": r["source_name"], "ms": r["processing_time_ms"]}

    avg_ms = round(total_seconds * 1000 / len(results), 1) if results else 0.0

    return {
        "run_timestamp": datetime.now(timezone.utc).isoformat(),
        "collection_path": collection_path,
        "total_items": total_items,
        "processed": len(results),
        "successful": successful,
        "errors": errors,
        "errors_by_code": errors_by_code,
        "format_counts": format_counts,
        "field_coverage": field_coverage,
        "multi_volume_count": multi_volume,
        "single_file_count": single_file,
        "duplicate_groups": duplicate_groups,
        "quality_issue_counts": quality_issue_counts,
        "timing": {
            "total_seconds": round(total_seconds, 1),
            "avg_per_book_ms": avg_ms,
            "slowest_book": slowest_book,
        },
    }


# ──────────────────────────────────────────────────────────────────
# Main
# ──────────────────────────────────────────────────────────────────


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Phase A: deterministic sweep of source engine extraction pipeline"
    )
    parser.add_argument(
        "collection_dir",
        type=Path,
        help="Path to directory containing Shamela exports",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("tests/results/source_engine/phase_a"),
        help="Output directory for per-book JSON results",
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=None,
        help="Process only the first N items",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip items with existing result JSON (mutually exclusive with clean start)",
    )
    args = parser.parse_args()

    collection_dir: Path = args.collection_dir.resolve()
    output_dir: Path = args.output_dir.resolve()

    if not collection_dir.is_dir():
        print(f"ERROR: Collection directory does not exist: {collection_dir}")
        sys.exit(1)

    # Discover items — deterministic sort by name
    items = sorted(collection_dir.iterdir(), key=lambda p: p.name)
    total_items = len(items)

    if args.limit is not None:
        items = items[: args.limit]

    print(f"Phase A: {len(items)} items to process from {collection_dir}")

    # Prepare output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    if not args.resume:
        # Clear existing JSON files
        for existing in output_dir.glob("*.json"):
            existing.unlink()
        print(f"Cleared output directory: {output_dir}")
    else:
        print(f"Resume mode: keeping existing results in {output_dir}")

    # Build set of existing result filenames for resume + collision tracking
    used_names: set[str] = set()
    existing_results: set[str] = set()
    if args.resume:
        for f in output_dir.glob("*.json"):
            if f.name != "PHASE_A_SUMMARY.json":
                stem = f.stem
                used_names.add(stem)
                existing_results.add(stem)

    # Process items
    results: list[dict[str, Any]] = []
    hash_to_sources: dict[str, list[str]] = {}
    ok_count = 0
    err_count = 0
    skipped = 0
    run_start = time.perf_counter()

    for i, item_path in enumerate(items, 1):
        # For resume: check existing results before calling sanitize_filename
        # (sanitize_filename mutates used_names, which would cause collisions)
        if args.resume:
            raw_sanitized = "".join(
                c if c not in _INVALID_CHARS else "_" for c in item_path.name
            )[:200]
            if raw_sanitized in existing_results:
                sanitized = raw_sanitized
            else:
                sanitized = sanitize_filename(item_path.name, used_names)
        else:
            sanitized = sanitize_filename(item_path.name, used_names)

        # Resume: skip if result already exists
        if args.resume and sanitized in existing_results:
            skipped += 1
            # Load existing result for summary aggregation
            existing_path = output_dir / f"{sanitized}.json"
            try:
                with existing_path.open("r", encoding="utf-8") as f:
                    existing_result = json.load(f)
                results.append(existing_result)
                if existing_result.get("composite_hash"):
                    h = existing_result["composite_hash"]
                    hash_to_sources.setdefault(h, []).append(
                        existing_result["source_name"]
                    )
                if existing_result["status"] == "success":
                    ok_count += 1
                else:
                    err_count += 1
            except Exception:
                pass  # Skip corrupted existing results
            continue

        # Process the item — outer try/except ensures the script NEVER crashes mid-run
        try:
            result = process_item(item_path, collection_dir)
        except Exception as exc:
            result = {
                "source_name": item_path.name,
                "source_path_relative": str(item_path.name),
                "status": "error",
                "source_format": None,
                "composite_hash": None,
                "file_hashes": None,
                "extracted_metadata": None,
                "quality_issues": None,
                "processing_time_ms": 0,
                "error": _make_internal_error(exc),
            }

        results.append(result)

        # Track duplicates
        if result["composite_hash"]:
            hash_to_sources.setdefault(result["composite_hash"], []).append(
                result["source_name"]
            )

        # Write per-book JSON
        try:
            result_path = output_dir / f"{sanitized}.json"
            with result_path.open("w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
        except Exception:
            pass  # Last resort: skip writing, still count the result

        if result["status"] == "success":
            ok_count += 1
        else:
            err_count += 1

        # Progress every 100 items
        if i % 100 == 0:
            elapsed = time.perf_counter() - run_start
            print(f"[{i}/{len(items)}] {ok_count} ok, {err_count} errors ({elapsed:.1f}s)")

    total_seconds = time.perf_counter() - run_start

    # Duplicate groups
    duplicate_groups = [
        {"hash": h, "sources": sources}
        for h, sources in hash_to_sources.items()
        if len(sources) > 1
    ]

    # Build and write summary
    summary = build_summary(
        results=results,
        collection_path=str(collection_dir),
        total_items=total_items,
        total_seconds=total_seconds,
        duplicate_groups=duplicate_groups,
    )
    summary_path = output_dir / "PHASE_A_SUMMARY.json"
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    # Final summary line
    if skipped:
        print(
            f"Done: {ok_count} ok, {err_count} errors, {skipped} skipped "
            f"({total_seconds:.1f}s) -> {summary_path}"
        )
    else:
        print(
            f"Done: {ok_count} ok, {err_count} errors "
            f"({total_seconds:.1f}s) -> {summary_path}"
        )

    if duplicate_groups:
        print(f"  {len(duplicate_groups)} duplicate group(s) found")


if __name__ == "__main__":
    main()
