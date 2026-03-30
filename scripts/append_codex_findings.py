"""Append validated creative findings from overnight_codex into its own tracker."""

from __future__ import annotations

import argparse
import json
import re
from datetime import date

try:
    from scripts.overnight_codex_common import (
        FINDINGS_REGISTRY_FILE,
        FINDINGS_TRACKER,
        RESULTS_DIR,
        repo_rel,
        write_json,
    )
except ImportError:
    from overnight_codex_common import (
        FINDINGS_REGISTRY_FILE,
        FINDINGS_TRACKER,
        RESULTS_DIR,
        repo_rel,
        write_json,
    )


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


def _load_registry() -> dict[str, dict[str, object]]:
    """Load the structured findings registry."""
    if not FINDINGS_REGISTRY_FILE.exists():
        return {}
    try:
        payload = json.loads(FINDINGS_REGISTRY_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    items = payload.get("items", {})
    return items if isinstance(items, dict) else {}


def _coerce_occurrences(value: object) -> int:
    """Return a safe occurrence count from a JSON-loaded value."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value)
        except ValueError:
            return 1
    return 1


def append_findings() -> int:
    """Append new creative findings and return how many were added."""
    existing_ids = _existing_ids()
    registry = _load_registry()
    today = date.today().isoformat()
    additions: list[str] = []
    registry_changed = False
    seen_this_run: set[str] = set()
    for actionable in sorted(RESULTS_DIR.glob("creative-*/actionable.json")):
        try:
            items = json.loads(actionable.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(items, list):
            continue
        source = repo_rel(actionable)
        source_signature = f"{source}:{actionable.stat().st_mtime_ns}"
        for item in items:
            if not isinstance(item, dict):
                continue
            item_id = str(item.get("id", "")).strip()
            if not item_id:
                continue
            summary = _escape_markdown(str(item.get("summary", "")))
            category = _escape_markdown(str(item.get("category", "")))
            effort = _escape_markdown(str(item.get("effort", "")))
            priority = _escape_markdown(str(item.get("priority", "")))
            if not all((summary, category, effort, priority)):
                continue
            if item_id not in seen_this_run:
                existing = registry.get(item_id)
                if isinstance(existing, dict):
                    existing["summary"] = summary
                    existing["category"] = category
                    existing["source"] = source
                    if existing.get("source_signature") != source_signature:
                        existing["last_seen"] = today
                        existing["occurrences"] = _coerce_occurrences(existing.get("occurrences", 1)) + 1
                    existing["source_signature"] = source_signature
                else:
                    registry[item_id] = {
                        "id": item_id,
                        "summary": summary,
                        "category": category,
                        "source": source,
                        "first_seen": today,
                        "last_seen": today,
                        "occurrences": 1,
                        "source_signature": source_signature,
                    }
                registry_changed = True
                seen_this_run.add(item_id)
            if item_id in existing_ids:
                continue
            additions.append(
                f"- [ ] {item_id} [{category}] {summary} ({effort}, {priority}) "
                f"[source: {source}]"
            )
            existing_ids.add(item_id)

    if not additions:
        if registry_changed:
            write_json(FINDINGS_REGISTRY_FILE, {"items": registry})
        return 0

    if FINDINGS_TRACKER.exists():
        content = FINDINGS_TRACKER.read_text(encoding="utf-8").rstrip() + "\n"
    else:
        content = "# Overnight Codex Findings Tracker\n"
    content += f"\n## {date.today().isoformat()}\n"
    content += "\n".join(additions) + "\n"
    FINDINGS_TRACKER.write_text(content, encoding="utf-8")
    if registry_changed:
        write_json(FINDINGS_REGISTRY_FILE, {"items": registry})
    return len(additions)


def main() -> None:
    """CLI entrypoint."""
    parser = argparse.ArgumentParser(description="Append overnight_codex findings")
    parser.parse_args()
    count = append_findings()
    print(f"Appended {count} findings to {repo_rel(FINDINGS_TRACKER)}")


if __name__ == "__main__":
    main()
