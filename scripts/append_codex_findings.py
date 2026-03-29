"""Append validated creative findings from overnight_codex into its own tracker."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date
from pathlib import Path

try:
    from scripts.overnight_codex_common import FINDINGS_TRACKER, RESULTS_DIR, repo_rel
except ImportError:
    from overnight_codex_common import FINDINGS_TRACKER, RESULTS_DIR, repo_rel


TRACKER_ID_RE = re.compile(r"- \[.\] ([^ ]+) ")


def _escape_markdown(value: str) -> str:
    """Keep tracker lines single-line and markdown-safe enough."""
    cleaned = value.replace("\r", " ").replace("\n", " ").strip()
    for char in "[]()#":
        cleaned = cleaned.replace(char, f"\\{char}")
    return cleaned


def _existing_ids() -> set[str]:
    """Read ids already present in the tracker."""
    if not FINDINGS_TRACKER.exists():
        return set()
    ids: set[str] = set()
    for line in FINDINGS_TRACKER.read_text(encoding="utf-8").splitlines():
        match = TRACKER_ID_RE.match(line)
        if match:
            ids.add(match.group(1))
    return ids


def append_findings() -> int:
    """Append new creative findings and return how many were added."""
    existing_ids = _existing_ids()
    additions: list[str] = []
    for actionable in sorted(RESULTS_DIR.glob("creative-*/actionable.json")):
        try:
            items = json.loads(actionable.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(items, list):
            continue
        source = repo_rel(actionable)
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            if not item_id or item_id in existing_ids:
                continue
            summary = _escape_markdown(str(item.get("summary", "")))
            category = _escape_markdown(str(item.get("category", "")))
            effort = _escape_markdown(str(item.get("effort", "")))
            priority = _escape_markdown(str(item.get("priority", "")))
            if not all((summary, category, effort, priority)):
                continue
            additions.append(
                f"- [ ] {item_id} [{category}] {summary} ({effort}, {priority}) "
                f"[source: {source}]"
            )
            existing_ids.add(item_id)

    if not additions:
        return 0

    if FINDINGS_TRACKER.exists():
        content = FINDINGS_TRACKER.read_text(encoding="utf-8").rstrip() + "\n"
    else:
        content = "# Overnight Codex Findings Tracker\n"
    content += f"\n## {date.today().isoformat()}\n"
    content += "\n".join(additions) + "\n"
    FINDINGS_TRACKER.write_text(content, encoding="utf-8")
    return len(additions)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Append overnight_codex findings")
    parser.parse_args()
    count = append_findings()
    print(f"Appended {count} findings to {repo_rel(FINDINGS_TRACKER)}")


if __name__ == "__main__":
    main()
