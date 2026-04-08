"""Unified launcher for the KR autonomous system.

Starts the dashboard, runs the Codex orchestrator, and bridges results
into the knowledge base — all with one command.

Usage:
    python scripts/launch_autonomous.py                 # 4h, dashboard on :8000
    python scripts/launch_autonomous.py --hours 8       # 8h overnight
    python scripts/launch_autonomous.py --dashboard-only  # just view dashboard
    python scripts/launch_autonomous.py --ingest-only   # bridge existing results
    python scripts/launch_autonomous.py --no-dashboard  # headless, no web UI

See docs/autonomous-system/SYSTEM_MAP.md for full documentation.
"""
from __future__ import annotations

import argparse
import logging
import sys
import threading
import time
from pathlib import Path

# Ensure project root is on sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)

# Shared shutdown event for clean Ctrl+C on Windows
_shutdown = threading.Event()


def _start_dashboard(port: int, no_browser: bool) -> threading.Thread:
    """Launch dashboard in a background daemon thread."""
    def _run() -> None:
        import uvicorn
        from scripts.autonomous_dashboard.app import app
        uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")

    thread = threading.Thread(target=_run, name="dashboard", daemon=True)
    thread.start()

    if not no_browser:
        import webbrowser
        url = f"http://localhost:{port}"
        threading.Timer(2.0, lambda: webbrowser.open(url)).start()

    return thread


def _run_orchestrator(
    hours: float,
    dry_run: bool,
    skip_preflight: bool,
) -> None:
    """Run the Codex orchestrator in the main thread."""
    from scripts.overnight_codex_orchestrator import run_overnight
    run_overnight(
        hours=hours,
        manifest_path=None,
        single_task=None,
        dry_run=dry_run,
        resume=False,
        skip_lock=False,
        skip_preflight=skip_preflight,
    )


def _run_bridge(run_id: str | None = None) -> dict[str, int]:
    """Ingest Codex results into the KB."""
    from scripts.codex_kb_bridge import ingest_codex_results
    return ingest_codex_results(run_id=run_id)


def _print_summary(
    stats: dict[str, int],
    port: int,
    dashboard_running: bool,
    errors: list[str],
) -> None:
    """Print final summary using KB totals (not per-call deltas)."""
    print()
    print("=" * 50)
    if errors:
        print("  KR Autonomous System — COMPLETED WITH ERRORS")
    else:
        print("  KR Autonomous System — Run Complete")
    print("=" * 50)
    if errors:
        for err in errors:
            print(f"  ERROR: {err}")
        print()

    # Show KB totals (cumulative) — avoids the 0-stat problem when
    # the orchestrator hook already ingested before this bridge call
    kb_tasks = stats.get("kb_total_tasks", 0)
    kb_findings = stats.get("kb_total_findings", 0)
    kb_confirmed = stats.get("kb_total_confirmed", 0)
    kb_disputed = stats.get("kb_total_disputed", 0)
    kb_preliminary = kb_findings - kb_confirmed - kb_disputed

    # Per-run stats (what this run added)
    new_tasks = stats.get("tasks_processed", 0)
    new_findings = stats.get("findings_created", 0)

    print(f"  This run:")
    print(f"    Tasks ingested:    {new_tasks}")
    print(f"    Findings created:  {new_findings}")
    print(f"    Verified:          {stats.get('verified', 0)} ({stats.get('confirmed', 0)} confirmed, {stats.get('disputed', 0)} disputed)")
    print(f"    Follow-up prompts: {stats.get('followup_prompts', 0)}")
    print()
    print(f"  KB totals:")
    print(f"    Tasks:    {kb_tasks}")
    print(f"    Findings: {kb_findings} ({kb_confirmed} confirmed, {kb_disputed} disputed, {kb_preliminary} preliminary)")

    if dashboard_running:
        print(f"\n  Dashboard: http://localhost:{port}")
        print("  (Refresh to see new findings. Press Ctrl+C to stop.)")
    print("=" * 50)


def _wait_forever() -> None:
    """Block until Ctrl+C. Uses polling loop for reliable Windows interrupts."""
    try:
        while not _shutdown.is_set():
            _shutdown.wait(timeout=1.0)
    except KeyboardInterrupt:
        pass


def _parse_args() -> argparse.Namespace:
    """Parse and validate CLI arguments."""
    parser = argparse.ArgumentParser(
        description="KR Autonomous System — unified launcher",
    )
    parser.add_argument("--hours", type=float, default=4.0,
                        help="How long to run the orchestrator (default: 4)")
    parser.add_argument("--port", type=int, default=8000,
                        help="Dashboard port (default: 8000)")
    parser.add_argument("--no-dashboard", action="store_true",
                        help="Don't start the web dashboard")
    parser.add_argument("--no-browser", action="store_true",
                        help="Don't auto-open browser")
    parser.add_argument("--dashboard-only", action="store_true",
                        help="Only start the dashboard (no tasks, no bridge)")
    parser.add_argument("--ingest-only", action="store_true",
                        help="Only run the bridge on existing results (no new tasks)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Orchestrator dry-run (generate manifest, don't execute)")
    parser.add_argument("--skip-preflight", action="store_true",
                        help="Skip orchestrator preflight checks")
    args = parser.parse_args()

    if args.dashboard_only and args.ingest_only:
        parser.error("--dashboard-only and --ingest-only are mutually exclusive")

    return args


def main() -> None:
    """Single-command launcher for the full autonomous system."""
    args = _parse_args()

    print("=" * 50)
    print("  KR Autonomous System")
    print("=" * 50)

    dashboard_running = False

    # Start dashboard
    if not args.no_dashboard:
        logger.info("Starting dashboard on port %d...", args.port)
        _start_dashboard(args.port, args.no_browser)
        dashboard_running = True
        time.sleep(0.5)  # let uvicorn bind

    if args.dashboard_only:
        print(f"\n  Dashboard running at http://localhost:{args.port}")
        print("  Press Ctrl+C to stop.\n")
        _wait_forever()
        return

    errors: list[str] = []

    # Run orchestrator (unless ingest-only)
    if not args.ingest_only:
        logger.info("Starting orchestrator for %.1f hours...", args.hours)
        try:
            _run_orchestrator(args.hours, args.dry_run, args.skip_preflight)
        except KeyboardInterrupt:
            logger.info("Orchestrator interrupted by user")
        except Exception as exc:
            logger.exception("Orchestrator failed")
            errors.append(f"Orchestrator crashed: {type(exc).__name__}: {str(exc)[:200]}")

    # Run bridge (always — catches anything the orchestrator hook missed)
    logger.info("Running KB bridge...")
    try:
        stats = _run_bridge()
    except Exception as exc:
        logger.exception("Bridge failed")
        errors.append(f"Bridge crashed: {type(exc).__name__}: {str(exc)[:200]}")
        stats = {}

    _print_summary(stats, args.port, dashboard_running, errors)

    # If dashboard is running, keep alive
    if dashboard_running and not args.ingest_only:
        _wait_forever()


if __name__ == "__main__":
    main()
