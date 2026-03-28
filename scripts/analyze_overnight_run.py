"""Post-overnight analysis script for excerpting integration runs.

Reads output from run_full_integration.py and produces a clean summary of
excerpts, errors, flags, timing, retries, and chunk size distribution.

Usage:
    python scripts/analyze_overnight_run.py --output-dir path/to/run/output
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


def load_json(path: Path) -> dict | list | None:
    """Load JSON file, returning None if missing or malformed."""
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"  WARNING: Could not read {path}: {exc}", file=sys.stderr)
        return None


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file, returning list of parsed dicts."""
    if not path.exists():
        return []
    entries = []
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                try:
                    entries.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return entries


def analyze_package(pkg_dir: Path) -> dict:
    """Analyze a single package output directory."""
    result: dict = {"name": pkg_dir.name}

    # Excerpts
    excerpts = load_jsonl(pkg_dir / "excerpts.jsonl")
    result["excerpt_count"] = len(excerpts)

    # Flag distribution
    flag_counter: Counter[str] = Counter()
    for exc in excerpts:
        for flag in exc.get("review_flags", []):
            flag_counter[flag] += 1
    result["flag_counts"] = dict(flag_counter)
    result["verification_skipped"] = flag_counter.get("verification_skipped", 0)
    result["llm_enrichment_failed"] = flag_counter.get("llm_enrichment_failed", 0)

    # Gate entries
    gates = load_jsonl(pkg_dir / "gate_queue.jsonl")
    result["gate_count"] = len(gates)

    # Errors from run_metadata
    meta = load_json(pkg_dir / "run_metadata.json")
    if meta and isinstance(meta, dict):
        result["error_count"] = meta.get("error_count", 0)
        result["errors"] = meta.get("errors", [])
    else:
        result["error_count"] = 0
        result["errors"] = []

    # Timing per phase
    timing = load_json(pkg_dir / "timing.json")
    if timing and isinstance(timing, dict):
        result["timing"] = timing
        result["total_time_seconds"] = round(
            sum(v for v in timing.values() if isinstance(v, (int, float))), 2
        )
    else:
        result["timing"] = {}
        result["total_time_seconds"] = 0.0

    # Retry analysis from raw_llm_requests/
    req_dir = pkg_dir / "raw_llm_requests"
    retry_count = 0
    timeout_errors = 0
    if req_dir.exists():
        call_ids: Counter[str] = Counter()
        for req_file in sorted(req_dir.glob("*.json")):
            req = load_json(req_file)
            if req and isinstance(req, dict):
                cid = req.get("call_id", "")
                if cid:
                    # Strip trailing _attempt_N to get base call_id
                    base = cid.rsplit("_attempt_", 1)[0]
                    call_ids[base] += 1
        retry_count = sum(c - 1 for c in call_ids.values() if c > 1)

    # Also check raw_llm_responses for timeout errors
    resp_dir = pkg_dir / "raw_llm_responses"
    if resp_dir.exists():
        for resp_file in resp_dir.glob("*_error.json"):
            resp = load_json(resp_file)
            if resp and isinstance(resp, dict):
                err_msg = str(resp.get("error", "")).lower()
                if "timeout" in err_msg or "timed out" in err_msg:
                    timeout_errors += 1

    result["retry_count"] = retry_count
    result["timeout_errors"] = timeout_errors

    # Phase 1 chunk stats
    chunks = load_json(pkg_dir / "phase1_chunks.json")
    if chunks and isinstance(chunks, list):
        word_counts = [
            c.get("word_count", 0) for c in chunks if isinstance(c, dict)
        ]
        if word_counts:
            result["chunk_count"] = len(word_counts)
            result["max_chunk_words"] = max(word_counts)
            result["min_chunk_words"] = min(word_counts)
            result["mean_chunk_words"] = round(
                sum(word_counts) / len(word_counts)
            )
        else:
            result["chunk_count"] = 0
    else:
        result["chunk_count"] = 0

    return result


def format_duration(seconds: float) -> str:
    """Format seconds as HH:MM:SS."""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    if h > 0:
        return f"{h}h{m:02d}m{s:02d}s"
    if m > 0:
        return f"{m}m{s:02d}s"
    return f"{s}s"


def print_summary(
    packages: list[dict],
    summary_data: dict | None,
) -> None:
    """Print a clean human-readable analysis."""
    print("=" * 70)
    print("OVERNIGHT RUN ANALYSIS")
    print("=" * 70)

    if summary_data and isinstance(summary_data, dict):
        ts = summary_data.get("timestamp", "unknown")
        print(f"\nRun timestamp: {ts}")

    # Per-package table
    print(f"\n{'Package':<20} {'Excerpts':>8} {'Errors':>7} {'Gates':>6} "
          f"{'Retries':>8} {'Timeouts':>9} {'Time':>10}")
    print(f"{'-' * 18:<20} {'-' * 6:>8} {'-' * 5:>7} {'-' * 4:>6} "
          f"{'-' * 6:>8} {'-' * 7:>9} {'-' * 8:>10}")

    total_excerpts = 0
    total_errors = 0
    total_gates = 0
    total_retries = 0
    total_timeouts = 0
    total_time = 0.0

    for pkg in packages:
        name = pkg["name"]
        exc_count = pkg["excerpt_count"]
        err_count = pkg["error_count"]
        gate_count = pkg["gate_count"]
        retries = pkg["retry_count"]
        timeouts = pkg["timeout_errors"]
        time_s = pkg["total_time_seconds"]

        total_excerpts += exc_count
        total_errors += err_count
        total_gates += gate_count
        total_retries += retries
        total_timeouts += timeouts
        total_time += time_s

        print(f"{name:<20} {exc_count:>8} {err_count:>7} {gate_count:>6} "
              f"{retries:>8} {timeouts:>9} {format_duration(time_s):>10}")

    print(f"{'-' * 18:<20} {'-' * 6:>8} {'-' * 5:>7} {'-' * 4:>6} "
          f"{'-' * 6:>8} {'-' * 7:>9} {'-' * 8:>10}")
    print(f"{'TOTAL':<20} {total_excerpts:>8} {total_errors:>7} "
          f"{total_gates:>6} {total_retries:>8} {total_timeouts:>9} "
          f"{format_duration(total_time):>10}")

    # Flag distribution
    all_flags: Counter[str] = Counter()
    for pkg in packages:
        for flag, count in pkg.get("flag_counts", {}).items():
            all_flags[flag] += count

    if all_flags:
        print(f"\n{'FLAG DISTRIBUTION':=^70}")
        print(f"  {'Flag':<40} {'Count':>8}")
        print(f"  {'-' * 38:<40} {'-' * 6:>8}")
        for flag, count in all_flags.most_common():
            print(f"  {flag:<40} {count:>8}")
    else:
        print("\nNo review flags set on any excerpt.")

    # Chunk size distribution
    chunk_pkgs = [p for p in packages if p.get("chunk_count", 0) > 0]
    if chunk_pkgs:
        print(f"\n{'CHUNK SIZE DISTRIBUTION':=^70}")
        print(f"  {'Package':<20} {'Chunks':>7} {'Min':>7} {'Mean':>7} "
              f"{'Max':>7}")
        print(f"  {'-' * 18:<20} {'-' * 5:>7} {'-' * 5:>7} {'-' * 5:>7} "
              f"{'-' * 5:>7}")
        for pkg in chunk_pkgs:
            print(f"  {pkg['name']:<20} {pkg['chunk_count']:>7} "
                  f"{pkg.get('min_chunk_words', 0):>7} "
                  f"{pkg.get('mean_chunk_words', 0):>7} "
                  f"{pkg.get('max_chunk_words', 0):>7}")

    # Timing breakdown (show per-phase if available)
    timing_pkgs = [p for p in packages if p.get("timing")]
    if timing_pkgs:
        print(f"\n{'TIMING BREAKDOWN (seconds)':=^70}")
        # Collect all phase names
        all_phases: set[str] = set()
        for pkg in timing_pkgs:
            all_phases.update(pkg["timing"].keys())
        phases = sorted(all_phases)

        header = f"  {'Package':<20}"
        for phase in phases:
            header += f" {phase:>12}"
        print(header)

        for pkg in timing_pkgs:
            row = f"  {pkg['name']:<20}"
            for phase in phases:
                val = pkg["timing"].get(phase)
                if val is not None:
                    row += f" {val:>12.1f}"
                else:
                    row += f" {'—':>12}"
            print(row)

    # Timeout warnings
    if total_timeouts > 0:
        print(f"\n*** WARNING: {total_timeouts} timeout error(s) detected! ***")
        for pkg in packages:
            if pkg["timeout_errors"] > 0:
                print(f"  {pkg['name']}: {pkg['timeout_errors']} timeout(s)")

    print(f"\n{'=' * 70}")


def main() -> int:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze overnight excerpting run output.",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        required=True,
        help="Path to the overnight run output directory",
    )
    args = parser.parse_args()

    output_dir: Path = args.output_dir
    if not output_dir.exists():
        print(f"ERROR: Output directory not found: {output_dir}", file=sys.stderr)
        return 1

    # Read top-level SUMMARY.json
    summary_data = load_json(output_dir / "SUMMARY.json")

    # Discover package directories
    pkg_dirs = sorted(
        d for d in output_dir.iterdir()
        if d.is_dir() and not d.name.startswith(".")
    )

    if not pkg_dirs:
        print(f"ERROR: No package directories found in {output_dir}",
              file=sys.stderr)
        return 1

    print(f"Analyzing {len(pkg_dirs)} packages in {output_dir}...\n")

    packages = []
    for pkg_dir in pkg_dirs:
        pkg_result = analyze_package(pkg_dir)
        packages.append(pkg_result)

    print_summary(packages, summary_data)

    # Save machine-readable analysis
    analysis_path = output_dir / "ANALYSIS.json"
    analysis = {
        "packages": packages,
        "totals": {
            "excerpt_count": sum(p["excerpt_count"] for p in packages),
            "error_count": sum(p["error_count"] for p in packages),
            "gate_count": sum(p["gate_count"] for p in packages),
            "retry_count": sum(p["retry_count"] for p in packages),
            "timeout_errors": sum(p["timeout_errors"] for p in packages),
            "total_time_seconds": round(
                sum(p["total_time_seconds"] for p in packages), 2
            ),
        },
    }
    analysis_path.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"\nMachine-readable analysis saved to: {analysis_path}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
