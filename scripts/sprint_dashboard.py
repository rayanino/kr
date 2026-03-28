"""Live dashboard for the weekend sprint. Run: watch -n 10 python scripts/sprint_dashboard.py"""
from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
OVERNIGHT = PROJECT / "overnight"
RESULTS = OVERNIGHT / "results"


def load_json(path: Path) -> dict | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def fmt_duration(seconds: float) -> str:
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    return f"{h}h{m:02d}m" if h else f"{m}m{s:02d}s"


def status_icon(status: str) -> str:
    return {"success": "+", "failed": "X", "timeout": "T", "skipped": "-"}.get(status, "?")


def main() -> None:
    now = datetime.now(timezone.utc)

    # Load states
    ro_state = load_json(OVERNIGHT / "weekend_state.json") or {}
    wr_state = load_json(OVERNIGHT / "state.json") or {}

    # Elapsed time
    started = ro_state.get("started_at")
    if started:
        elapsed = (now - datetime.fromisoformat(started)).total_seconds()
    else:
        elapsed = 0

    # Manifest counts
    manifest = load_json(OVERNIGHT / "sprint_manifest.json") or {"tasks": []}
    total_tasks = len(manifest["tasks"])
    ro_total = sum(1 for t in manifest["tasks"] if t.get("category") == "sprint_analysis")
    wr_total = total_tasks - ro_total

    # Readonly stats
    ro_done = ro_state.get("readonly_completed", 0)
    ro_fail = ro_state.get("readonly_failed", 0)
    ro_active = ro_state.get("active_workers", {})

    # Write stats
    wr_done = wr_state.get("tasks_completed", 0)
    wr_fail = wr_state.get("tasks_failed", 0)
    wr_cost = wr_state.get("total_cost_usd", 0)
    wr_status = wr_state.get("status", "unknown")

    # Combined
    done = ro_done + ro_fail + wr_done + wr_fail
    pct = (done / total_tasks * 100) if total_tasks else 0

    # Header
    print("=" * 62)
    print("  KR WEEKEND SPRINT DASHBOARD")
    print("=" * 62)
    print(f"  Elapsed: {fmt_duration(elapsed)}    "
          f"Progress: {done}/{total_tasks} ({pct:.0f}%)")
    print()

    # Progress bar
    bar_width = 50
    filled = int(bar_width * pct / 100)
    bar = "█" * filled + "░" * (bar_width - filled)
    print(f"  [{bar}] {pct:.0f}%")
    print()

    # Worker status
    print("  READONLY POOL" + " " * 20 + "WRITE ORCHESTRATOR")
    print(f"  Done: {ro_done}/{ro_total}" + " " * 22 + f"Done: {wr_done}/{wr_total}")
    print(f"  Fail: {ro_fail}" + " " * 27 + f"Fail: {wr_fail}")
    print(f"  Active: {len(ro_active)}" + " " * 24 + f"Status: {wr_status}")
    print(" " * 38 + f"Cost: ${wr_cost:.2f}")
    print()

    # Active workers
    if ro_active:
        print("  ACTIVE NOW:")
        for wid, tid in ro_active.items():
            print(f"    {wid}: {tid}")
        print()

    # Recent completions (last 8)
    all_results = []

    # Readonly results
    for r in ro_state.get("results", []):
        all_results.append(r)

    # Write results
    for tid, r in wr_state.get("results", {}).items():
        all_results.append({
            "task_id": r.get("task_id", tid),
            "status": r.get("status", "?"),
            "duration_s": r.get("duration_s", 0),
            "end_time": r.get("end_time", ""),
            "worker": "write",
            "cost_usd": r.get("cost_usd", 0),
        })

    # Sort by end time
    all_results.sort(key=lambda x: x.get("end_time", ""), reverse=True)

    print("  RECENT COMPLETIONS:")
    print(f"  {'Status':<6} {'Task':<42} {'Duration':<10} {'Cost':<8}")
    print("  " + "-" * 58)
    for r in all_results[:10]:
        icon = status_icon(r["status"])
        tid = r["task_id"][:40]
        dur = fmt_duration(r.get("duration_s", 0))
        cost = f"${r.get('cost_usd', 0):.2f}" if r.get("cost_usd") else ""
        print(f"  [{icon}]   {tid:<42} {dur:<10} {cost}")

    print()

    # Scan for findings
    findings_count = 0
    bugs_found = 0
    tests_added = 0
    for d in RESULTS.iterdir():
        if not d.is_dir():
            continue
        fj = d / "findings.json"
        if fj.exists():
            findings_count += 1
            try:
                fdata = json.loads(fj.read_text(encoding="utf-8"))
                bugs_found += fdata.get("bugs_found", 0) + fdata.get("critical", 0) + fdata.get("high", 0)
                tests_added += fdata.get("tests_added", 0)
            except Exception:
                pass

    print(f"  FINDINGS: {findings_count} tasks produced reports")
    if bugs_found:
        print(f"  BUGS FOUND: {bugs_found}")
    if tests_added:
        print(f"  TESTS ADDED: {tests_added}")

    # Git commits since sprint start
    git_start = wr_state.get("git_start_hash", "")
    if git_start:
        import subprocess
        result = subprocess.run(
            ["git", "log", "--oneline", f"{git_start}..HEAD"],
            capture_output=True, text=True, cwd=str(PROJECT),
        )
        commits = [l for l in result.stdout.strip().split("\n") if l.strip()]
        if commits:
            print(f"\n  GIT COMMITS ({len(commits)}):")
            for c in commits[:5]:
                print(f"    {c}")
            if len(commits) > 5:
                print(f"    ... and {len(commits) - 5} more")

    print()
    print("=" * 62)
    print(f"  Last updated: {now.strftime('%H:%M:%S UTC')}")
    print("  Refresh: watch -n 10 python scripts/sprint_dashboard.py")


if __name__ == "__main__":
    main()
