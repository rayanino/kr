"""Batch integration test runner for all 5 excerpting engine test packages.

Runs scripts/run_integration_test.py on each package sequentially (no
--max-chunks), aggregates results, and produces SUMMARY.json.

Usage:
    python scripts/run_full_integration.py
    python scripts/run_full_integration.py --output-dir path/to/output/
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Package configuration
# ---------------------------------------------------------------------------

PACKAGES: list[dict[str, Any]] = [
    {
        "name": "ibn_aqil_v1",
        "metadata": {
            "author_name": "ابن عقيل",
            "work_title": "شرح ابن عقيل على ألفية ابن مالك",
            "science": "نحو",
            "source_school": None,
        },
    },
    {
        "name": "ibn_aqil_v3",
        "metadata": {
            "author_name": "ابن عقيل",
            "work_title": "شرح ابن عقيل على ألفية ابن مالك",
            "science": "نحو",
            "source_school": None,
        },
    },
    {
        "name": "taysir",
        "metadata": {
            "author_name": "عبد الله البسام",
            "work_title": "تيسير العلام شرح عمدة الأحكام",
            "science": "فقه",
            "source_school": "حنبلي",
        },
    },
    {
        "name": "ext_39_masala",
        "metadata": {
            "author_name": None,
            "work_title": None,
            "science": None,
            "source_school": None,
        },
    },
    {
        "name": "ext_46_qa",
        "metadata": {
            "author_name": None,
            "work_title": None,
            "science": "أصول النحو",
            "source_school": None,
        },
    },
]

PACKAGES_DIR = Path("experiments/format_diversity_test/packages")
RUNNER_SCRIPT = Path("scripts/run_integration_test.py")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def format_duration(seconds: float) -> str:
    """Format seconds as Xm Ys."""
    m, s = divmod(int(seconds), 60)
    if m > 0:
        return f"{m}m {s}s"
    return f"{s}s"


def read_package_results(pkg_output_dir: Path) -> dict[str, Any]:
    """Read result files from a completed package run."""
    result: dict[str, Any] = {
        "excerpt_count": 0,
        "error_count": 0,
        "errors": [],
        "time_seconds": 0.0,
        "cost_estimate": 0.0,
    }

    # Read timing
    timing_path = pkg_output_dir / "timing.json"
    if timing_path.exists():
        timing = json.loads(timing_path.read_text(encoding="utf-8"))
        total = sum(v for v in timing.values() if isinstance(v, (int, float)))
        result["time_seconds"] = round(total, 2)

    # Count excerpts
    excerpts_path = pkg_output_dir / "excerpts.jsonl"
    if excerpts_path.exists():
        with open(excerpts_path, encoding="utf-8") as fh:
            result["excerpt_count"] = sum(1 for line in fh if line.strip())

    # Read errors from run_metadata
    meta_path = pkg_output_dir / "run_metadata.json"
    if meta_path.exists():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
        result["error_count"] = meta.get("error_count", 0)
        result["errors"] = meta.get("errors", [])

    # Aggregate cost from raw LLM responses
    resp_dir = pkg_output_dir / "raw_llm_responses"
    if resp_dir.exists():
        for resp_file in resp_dir.glob("*.json"):
            if resp_file.name.endswith("_error.json"):
                continue
            try:
                resp = json.loads(resp_file.read_text(encoding="utf-8"))
                usage = resp.get("usage") or {}
                cost = usage.get("cost", 0.0)
                if cost:
                    result["cost_estimate"] += cost
            except (json.JSONDecodeError, OSError):
                pass
        result["cost_estimate"] = round(result["cost_estimate"], 6)

    return result


# ---------------------------------------------------------------------------
# Batch execution
# ---------------------------------------------------------------------------


def run_batch(output_dir: Path, backend: str = "api") -> dict[str, Any]:
    """Run all packages sequentially and return aggregated results."""
    output_dir.mkdir(parents=True, exist_ok=True)
    results: dict[str, dict[str, Any]] = {}
    batch_start = time.monotonic()

    for i, pkg in enumerate(PACKAGES, start=1):
        name = pkg["name"]
        pkg_path = PACKAGES_DIR / name
        pkg_output = output_dir / name

        elapsed = time.monotonic() - batch_start
        print(f"\n{'=' * 60}")
        print(f"[{i}/{len(PACKAGES)}] {name} (elapsed: {format_duration(elapsed)})")
        print(f"{'=' * 60}\n")

        if not pkg_path.exists():
            print(f"  ERROR: Package directory not found: {pkg_path}")
            results[name] = {
                "status": "error",
                "excerpt_count": 0,
                "error_count": 1,
                "errors": [f"Package directory not found: {pkg_path}"],
                "time_seconds": 0.0,
                "cost_estimate": 0.0,
            }
            continue

        cmd = [
            sys.executable,
            str(RUNNER_SCRIPT),
            "--package-path", str(pkg_path),
            "--output-dir", str(pkg_output),
            "--source-metadata", json.dumps(pkg["metadata"], ensure_ascii=False),
            "--backend", backend,
        ]

        t0 = time.monotonic()
        try:
            proc = subprocess.run(cmd, timeout=3600)
            elapsed_pkg = time.monotonic() - t0

            if proc.returncode != 0:
                print(f"\n  FAILED (exit code {proc.returncode}, "
                      f"{format_duration(elapsed_pkg)})")
                pkg_result = read_package_results(pkg_output)
                pkg_result["status"] = "error"
                if not pkg_result["errors"]:
                    pkg_result["errors"] = [f"Exit code {proc.returncode}"]
                    pkg_result["error_count"] = max(pkg_result["error_count"], 1)
            else:
                print(f"\n  COMPLETED ({format_duration(elapsed_pkg)})")
                pkg_result = read_package_results(pkg_output)
                pkg_result["status"] = "success"

            pkg_result["time_seconds"] = round(elapsed_pkg, 2)

        except subprocess.TimeoutExpired:
            elapsed_pkg = time.monotonic() - t0
            print(f"\n  TIMEOUT after {format_duration(elapsed_pkg)}")
            pkg_result = {
                "status": "error",
                "excerpt_count": 0,
                "error_count": 1,
                "errors": ["Timeout after 3600s"],
                "time_seconds": round(elapsed_pkg, 2),
                "cost_estimate": 0.0,
            }
        except Exception as exc:
            elapsed_pkg = time.monotonic() - t0
            print(f"\n  CRASH: {exc}")
            pkg_result = {
                "status": "error",
                "excerpt_count": 0,
                "error_count": 1,
                "errors": [f"Subprocess crash: {exc}"],
                "time_seconds": round(elapsed_pkg, 2),
                "cost_estimate": 0.0,
            }

        results[name] = pkg_result

    total_time = time.monotonic() - batch_start

    succeeded = sum(1 for r in results.values() if r["status"] == "success")
    failed = sum(1 for r in results.values() if r["status"] == "error")

    return {
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "output_dir": str(output_dir),
        "packages": results,
        "totals": {
            "packages_run": len(PACKAGES),
            "packages_succeeded": succeeded,
            "packages_failed": failed,
            "total_excerpts": sum(r["excerpt_count"] for r in results.values()),
            "total_errors": sum(r["error_count"] for r in results.values()),
            "total_time_seconds": round(total_time, 2),
            "total_cost_estimate": round(
                sum(r["cost_estimate"] for r in results.values()), 6
            ),
        },
    }


# ---------------------------------------------------------------------------
# Summary display
# ---------------------------------------------------------------------------


def print_summary(summary: dict[str, Any]) -> None:
    """Print a human-readable summary table."""
    print(f"\n{'=' * 60}")
    print("FULL INTEGRATION TEST SUMMARY")
    print(f"{'=' * 60}\n")

    header = (f"  {'Package':<20} {'Status':<10} {'Excerpts':>10} "
              f"{'Errors':>8} {'Time':>10} {'Cost':>10}")
    divider = (f"  {'-' * 18:<20} {'-' * 8:<10} {'-' * 8:>10} "
               f"{'-' * 6:>8} {'-' * 8:>10} {'-' * 8:>10}")
    print(header)
    print(divider)

    for name, result in summary["packages"].items():
        status = "OK" if result["status"] == "success" else "FAIL"
        time_str = format_duration(result["time_seconds"])
        cost_str = f"\u20ac{result['cost_estimate']:.4f}"
        print(
            f"  {name:<20} {status:<10} {result['excerpt_count']:>10} "
            f"{result['error_count']:>8} {time_str:>10} {cost_str:>10}"
        )

    print(divider)
    totals = summary["totals"]
    time_str = format_duration(totals["total_time_seconds"])
    cost_str = f"\u20ac{totals['total_cost_estimate']:.4f}"
    ok_str = f"{totals['packages_succeeded']}/{totals['packages_run']}"
    print(
        f"  {'TOTAL':<20} {ok_str:<10} {totals['total_excerpts']:>10} "
        f"{totals['total_errors']:>8} {time_str:>10} {cost_str:>10}"
    )
    print()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run full integration tests on all 5 excerpting engine packages.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="Output directory (default: integration_tests/full_run_{YYYYMMDD}/)",
    )
    parser.add_argument(
        "--backend",
        choices=["cli", "api"],
        default="api",
        help="LLM backend passed to run_integration_test.py",
    )
    args = parser.parse_args()

    if args.output_dir is None:
        date_str = datetime.datetime.now().strftime("%Y%m%d")
        args.output_dir = Path("integration_tests") / f"full_run_{date_str}"

    if args.backend == "api":
        api_key = os.environ.get("OPENROUTER_API_KEY")
        if not api_key:
            print("ERROR: OPENROUTER_API_KEY environment variable not set")
            return 1
        api_key_display = f"{'*' * 8}...{api_key[-4:]}"
    else:
        api_key_display = "(CLI backend — no API key needed)"

    if not PACKAGES_DIR.exists():
        print(f"ERROR: Packages directory not found: {PACKAGES_DIR}")
        return 1

    print(f"Output directory: {args.output_dir.resolve()}")
    print(f"Packages:         {len(PACKAGES)}")
    print(f"Backend:          {args.backend}")
    print(f"API key:          {api_key_display}")

    summary = run_batch(args.output_dir, backend=args.backend)
    print_summary(summary)

    summary_path = args.output_dir / "SUMMARY.json"
    summary_path.write_text(
        json.dumps(summary, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Summary saved to: {summary_path}")

    return 0 if summary["totals"]["packages_failed"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
