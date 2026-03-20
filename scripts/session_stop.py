"""Auto-save session state on exit.

Captures active engine, modified files, test status, and uncommitted changes
to `.claude/session_state.json` for recovery by /catchup.

Usage:
    python scripts/session_stop.py
"""
from __future__ import annotations

import json
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


def main() -> int:
    cwd = Path.cwd()
    git_root = run_git(["rev-parse", "--show-toplevel"], cwd)
    if not git_root:
        return 1

    project_dir = Path(git_root)

    state = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "branch": run_git(["branch", "--show-current"], project_dir),
        "active_engine": detect_active_engine(project_dir),
        "modified_files": get_modified_files(project_dir),
        "uncommitted_summary": get_uncommitted_summary(project_dir),
        "next_md_head": read_next_md_head(project_dir),
        "recent_commits": run_git(["log", "--oneline", "-5"], project_dir),
    }

    output_path = project_dir / ".claude" / "session_state.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(state, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
