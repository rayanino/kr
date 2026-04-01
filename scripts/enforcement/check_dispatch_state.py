"""F1 enforcement: Check if coworker dispatch has occurred recently.

Used by the Stop hook and UserPromptSubmit hook to detect when CC is
making major conclusions without multi-model validation.

Exit codes:
  0 = dispatch recent (OK) or no conclusion signals detected
  1 = no recent dispatch AND conclusion signals present
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


def get_last_dispatch_time(project_dir: Path) -> datetime | None:
    """Read the most recent dispatch timestamp from dispatch_log.jsonl."""
    log_path = project_dir / ".kr" / "runtime" / "dispatch_log.jsonl"
    if not log_path.exists():
        return None

    last_ts = None
    for line in log_path.read_text(encoding="utf-8").strip().splitlines():
        try:
            entry = json.loads(line)
            ts_str = entry.get("timestamp", "")
            if ts_str:
                ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                if last_ts is None or ts > last_ts:
                    last_ts = ts
        except (json.JSONDecodeError, ValueError):
            continue
    return last_ts


def has_recent_dispatch(project_dir: Path, max_age_hours: float = 4.0) -> bool:
    """Check if there was a dispatch within the last N hours."""
    last = get_last_dispatch_time(project_dir)
    if last is None:
        return False
    now = datetime.now(timezone.utc)
    return (now - last) < timedelta(hours=max_age_hours)


def check_modified_analysis_files(project_dir: Path) -> list[str]:
    """Check git for modified files that look like analysis/report artifacts."""
    import subprocess

    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, timeout=5,
            cwd=str(project_dir),
        )
        if result.returncode != 0:
            return []
        analysis_patterns = ("report", "findings", "evaluation", "analysis", "assessment")
        return [
            f for f in result.stdout.strip().splitlines()
            if any(p in f.lower() for p in analysis_patterns) and f.endswith(".md")
        ]
    except Exception:
        return []


def main() -> int:
    project_dir = Path.cwd()
    if len(sys.argv) > 1:
        project_dir = Path(sys.argv[1])

    analysis_files = check_modified_analysis_files(project_dir)
    if not analysis_files:
        return 0  # No analysis files modified — no enforcement needed

    if has_recent_dispatch(project_dir):
        return 0  # Recent dispatch exists — OK

    print(f"DISPATCH REQUIRED: {len(analysis_files)} analysis file(s) modified "
          f"without recent coworker dispatch.", file=sys.stderr)
    for f in analysis_files:
        print(f"  - {f}", file=sys.stderr)
    print("\nDispatch coworkers before presenting conclusions. "
          "Mark as [PRELIMINARY] if dispatch is not yet complete.", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
