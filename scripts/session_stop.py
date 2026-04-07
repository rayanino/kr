"""Auto-save session state on exit.

Captures active engine, modified files, test status, and uncommitted changes
to `.claude/session_state.json` for recovery by /catchup.

Usage:
    python scripts/session_stop.py
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def run_git(args: list[str], cwd: Path) -> str:
    """Run a git command and return stdout, empty string on failure."""
    try:
        result = subprocess.run(
            ["git"] + args,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(cwd),
        )
        return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return ""


def detect_active_engine(cwd: Path) -> str | None:
    """Detect which engine was most recently modified from uncommitted changes."""
    diff_files = run_git(["diff", "--name-only", "HEAD"], cwd)
    staged_files = run_git(["diff", "--cached", "--name-only"], cwd)
    all_files = (diff_files + "\n" + staged_files).strip().split("\n")

    engine_counts: dict[str, int] = {}
    for f in all_files:
        if f.startswith("engines/"):
            parts = f.split("/")
            if len(parts) >= 2:
                engine_counts[parts[1]] = engine_counts.get(parts[1], 0) + 1

    if engine_counts:
        return max(engine_counts, key=lambda k: engine_counts[k])

    # Fall back to recent commits
    log = run_git(["log", "--oneline", "-5", "--name-only"], cwd)
    for line in log.split("\n"):
        if line.startswith("engines/"):
            parts = line.split("/")
            if len(parts) >= 2:
                return parts[1]

    return None


def get_uncommitted_summary(cwd: Path) -> str:
    """Get git diff --stat for uncommitted changes."""
    return run_git(["diff", "--stat"], cwd)


def get_modified_files(cwd: Path) -> list[str]:
    """Get list of modified files (staged + unstaged)."""
    diff = run_git(["diff", "--name-only", "HEAD"], cwd)
    staged = run_git(["diff", "--cached", "--name-only"], cwd)
    combined = set(filter(None, (diff + "\n" + staged).split("\n")))
    return sorted(combined)


def read_next_md_head(cwd: Path, lines: int = 15) -> str:
    """Read first N lines of NEXT.md."""
    next_file = cwd / "NEXT.md"
    if not next_file.exists():
        return ""
    try:
        content = next_file.read_text(encoding="utf-8", errors="ignore")
        return "\n".join(content.split("\n")[:lines])
    except OSError:
        return ""


def detect_active_spec_section(project_dir: Path) -> str | None:
    """Detect which SPEC section was last modified from recent commits."""
    log = run_git(["log", "--oneline", "-10"], project_dir)
    for line in log.split("\n"):
        line_lower = line.lower()
        if "spec" in line_lower and "§" in line:
            # Extract section reference like "§7" or "§2.3"
            import re
            match = re.search(r"§[0-9]+(?:\.[0-9]+)?", line)
            if match:
                return match.group(0)
    return None


def get_last_committed_file(project_dir: Path) -> str | None:
    """Get the most recently committed file from the last commit."""
    files = run_git(["diff-tree", "--no-commit-id", "--name-only", "-r", "HEAD"], project_dir)
    if files:
        file_list = files.strip().split("\n")
        return file_list[0] if file_list else None
    return None


def get_pending_decisions(project_dir: Path) -> list[str]:
    """Read pending decisions log if it exists."""
    log_file = project_dir / ".claude" / "pending_decisions.log"
    if not log_file.exists():
        return []
    try:
        lines = log_file.read_text(encoding="utf-8", errors="ignore").strip().split("\n")
        return lines[-5:]  # Last 5 entries
    except OSError:
        return []


def get_plan_file(project_dir: Path) -> str | None:
    """Find the active plan file if one exists."""
    plans_dir = project_dir / ".claude" / "plans"
    if not plans_dir.exists():
        return None
    plan_files = sorted(plans_dir.glob("*.md"), key=lambda p: p.stat().st_mtime, reverse=True)
    if plan_files:
        return str(plan_files[0].relative_to(project_dir))
    return None


def main() -> int:
    cwd = Path.cwd()
    git_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not git_root:
        return 1

    project_dir = Path(git_root)

    # Cost tracking — parse COST_LOG.json for budget status
    cost_summary: dict[str, float] | None = None
    cost_log_path = project_dir / "tests" / "results" / "source_engine" / "COST_LOG.json"
    if cost_log_path.exists():
        try:
            cost_data = json.loads(cost_log_path.read_text(encoding="utf-8"))
            total = sum(
                phase.get("cost_eur", 0)
                for phase in cost_data.values()
                if isinstance(phase, dict)
            )
            budget = float(os.environ.get("KR_BUDGET_LIMIT", "100"))
            cost_summary = {
                "total_eur": round(total, 2),
                "budget_eur": budget,
                "remaining_eur": round(budget - total, 2),
            }
        except (json.JSONDecodeError, OSError, ValueError):
            pass

    # Circuit breaker history — last 5 triggers
    cb_triggers: list[str] = []
    cb_log = project_dir / ".claude" / "circuit_breaker.log"
    if cb_log.exists():
        try:
            lines = cb_log.read_text(encoding="utf-8", errors="ignore").strip().split("\n")
            cb_triggers = [line for line in lines[-5:] if line.strip()]
        except OSError:
            pass

    # Print detection — find leftover print() in modified engine/shared source
    modified = get_modified_files(project_dir)
    print_warnings: list[str] = []
    for f in modified:
        if f.endswith(".py") and ("/src/" in f) and ("engines/" in f or "shared/" in f):
            fpath = project_dir / f
            if fpath.exists():
                try:
                    for i, line in enumerate(
                        fpath.read_text(encoding="utf-8", errors="ignore").split("\n"),
                        1,
                    ):
                        stripped = line.lstrip()
                        if stripped.startswith("print(") and "# safe:" not in line:
                            print_warnings.append(f"{f}:{i}")
                            if len(print_warnings) >= 10:
                                break
                except OSError:
                    pass
            if len(print_warnings) >= 10:
                break

    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": run_git(["branch", "--show-current"], project_dir),
        "active_engine": detect_active_engine(project_dir),
        "active_spec_section": detect_active_spec_section(project_dir),
        "last_committed_file": get_last_committed_file(project_dir),
        "active_plan": get_plan_file(project_dir),
        "modified_files": modified,
        "uncommitted_summary": get_uncommitted_summary(project_dir),
        "next_md_head": read_next_md_head(project_dir),
        "recent_commits": run_git(["log", "--oneline", "-5"], project_dir),
        "pending_decisions": get_pending_decisions(project_dir),
        "cost_summary": cost_summary,
        "circuit_breaker_triggers": cb_triggers,
        "print_warnings": print_warnings,
    }

    output_path = project_dir / ".claude" / "session_state.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    # Layer 3: Append-only event log (Sanad principle — provenance for every session)
    append_session_event(project_dir, state)

    return 0


def append_session_event(project_dir: Path, state: dict) -> None:
    """Append a structured event to the session event log.

    Events are append-only JSONL — never overwritten, never deleted.
    Each event carries provenance (which agent, which branch, what changed).
    This is Layer 3 of the KR memory architecture (DR25-DR27 investigation).
    """
    events_dir = project_dir / "memory" / "events"
    events_dir.mkdir(parents=True, exist_ok=True)

    now = datetime.now(timezone.utc)
    log_file = events_dir / f"sessions_{now.strftime('%Y_%m')}.jsonl"

    # Determine agent identity from environment
    agent = "claude_code"
    if os.environ.get("CODEX_CLI"):
        agent = "codex_cli"
    elif os.environ.get("GEMINI_CLI"):
        agent = "gemini_cli"

    event = {
        "event_type": "session_end",
        "timestamp": now.isoformat(),
        "agent": agent,
        "branch": state.get("branch", ""),
        "active_engine": state.get("active_engine"),
        "active_spec_section": state.get("active_spec_section"),
        "modified_file_count": len(state.get("modified_files", [])),
        "recent_commits": state.get("recent_commits", ""),
        "cost_summary": state.get("cost_summary"),
        "print_warnings_count": len(state.get("print_warnings", [])),
    }

    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except OSError:
        pass  # Non-blocking — event log failure must not break session stop


if __name__ == "__main__":
    sys.exit(main())
