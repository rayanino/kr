"""Real-time pipeline monitoring dashboard.

Reads status.json from a running pipeline and displays formatted output.
Usage: python scripts/kr_pipeline_monitor.py <output_dir>
       Or: watch -n5 python scripts/kr_pipeline_monitor.py <output_dir>
"""
from __future__ import annotations

import json
import sys
from pathlib import Path


def main() -> None:
    """Read status.json and display a formatted monitoring dashboard."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/kr_pipeline_monitor.py <output_dir>")
        sys.exit(1)

    status_path = Path(sys.argv[1]) / "status.json"
    if not status_path.exists():
        print(f"No status file found at {status_path}")
        print("Is the pipeline running?")
        sys.exit(1)

    try:
        data = json.loads(status_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        print(f"Error reading status: {exc}")
        sys.exit(1)

    total = data.get("total_chunks", 0)
    completed = data.get("completed", 0)
    failed = data.get("failed", 0)
    pending = data.get("pending", 0)
    elapsed = data.get("elapsed_seconds", 0)
    eta = data.get("estimated_remaining_seconds")
    in_progress = data.get("in_progress", {})
    cache_hits = data.get("cache_hits", 0)
    cache_misses = data.get("cache_misses", 0)

    # Format
    pct = (completed / total * 100) if total > 0 else 0
    elapsed_h = elapsed / 3600
    eta_h = (eta / 3600) if eta else None

    print("=" * 50)
    print("  KR Excerpting Pipeline Monitor")
    print("=" * 50)
    print(f"  Updated: {data.get('updated', 'unknown')}")
    print(f"  Elapsed: {elapsed_h:.1f}h")
    if eta_h is not None:
        print(f"  ETA:     {eta_h:.1f}h remaining")
    print()
    print(f"  Progress: {completed}/{total} ({pct:.0f}%)")
    print(f"  Failed:   {failed}")
    print(f"  Pending:  {pending}")
    print()
    if in_progress:
        print("  Active phases:")
        for phase, count in sorted(in_progress.items()):
            if count > 0:
                print(f"    {phase}: {count}")
    print()
    print(f"  Cache: {cache_hits} hits, {cache_misses} misses")
    if cache_hits + cache_misses > 0:
        hit_rate = cache_hits / (cache_hits + cache_misses) * 100
        print(f"  Cache hit rate: {hit_rate:.0f}%")
    print("=" * 50)


if __name__ == "__main__":
    main()
