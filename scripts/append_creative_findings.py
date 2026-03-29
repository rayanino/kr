"""Append actionable findings from creative overnight tasks to FINDINGS_TRACKER.md.

Reads all actionable.json files from overnight/results/ directories
that contain 'creative' in their path, and appends new items to
FINDINGS_TRACKER.md under the appropriate section.
Deduplicates by exact summary match.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


FINDINGS_TRACKER = Path("FINDINGS_TRACKER.md")
OVERNIGHT_RESULTS = Path("overnight/results")

SECTION_MAP = {
    "BUG": "## BUGS (fix immediately)",
    "IMP": "## READY TO IMPLEMENT (next 1-2 sessions)",
    "EXT": "## EXTERNAL INTEGRATIONS (high value, low effort)",
    "ARCH": "## ARCHITECTURE (design sessions needed)",
    "DOM": "## DOMAIN KNOWLEDGE (expert review needed)",
    "TAX": "## INTEGRATE BEFORE TAXONOMY BUILD (blocks next engine)",
}


def load_existing_summaries(tracker_text: str) -> set[str]:
    """Extract existing item summaries to avoid duplicates."""
    summaries: set[str] = set()
    for line in tracker_text.splitlines():
        m = re.match(r"^- \[[ x]\] \w+-[0-9]+: (.+)$", line)
        if m:
            summaries.add(m.group(1).strip())
    return summaries


def collect_actionable_items() -> list[dict]:
    """Find all actionable.json files from creative runs."""
    items: list[dict] = []
    for f in sorted(OVERNIGHT_RESULTS.rglob("actionable.json")):
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                items.extend(data)
        except (json.JSONDecodeError, OSError):
            continue
    return items


def append_to_tracker(items: list[dict]) -> int:
    """Append new actionable items to FINDINGS_TRACKER.md. Returns count added."""
    if not FINDINGS_TRACKER.exists():
        print("FINDINGS_TRACKER.md not found — skipping")
        return 0

    tracker_text = FINDINGS_TRACKER.read_text(encoding="utf-8")
    existing = load_existing_summaries(tracker_text)
    added = 0

    for item in items:
        summary = item.get("summary", "").strip()
        if not summary or summary in existing:
            continue

        category = item.get("category", "IMP")
        item_id = item.get("id", f"CREATIVE-{added + 1:03d}")
        effort = item.get("effort", "M")
        priority = item.get("priority", "MEDIUM")
        source = item.get("source_report", "")

        section_header = SECTION_MAP.get(category, SECTION_MAP["IMP"])
        line = f"- [ ] {item_id}: {summary} ({effort} effort, {priority}) [{source}]"

        idx = tracker_text.find(section_header)
        if idx == -1:
            tracker_text = tracker_text.rstrip() + "\n" + line + "\n"
        else:
            next_section = tracker_text.find("\n## ", idx + len(section_header))
            if next_section == -1:
                insert_pos = len(tracker_text)
            else:
                insert_pos = next_section
            tracker_text = (
                tracker_text[:insert_pos].rstrip()
                + "\n" + line + "\n"
                + tracker_text[insert_pos:]
            )

        existing.add(summary)
        added += 1

    if added > 0:
        FINDINGS_TRACKER.write_text(tracker_text, encoding="utf-8")
        print(f"Appended {added} new items to FINDINGS_TRACKER.md")
    else:
        print("No new actionable items to append")

    return added


if __name__ == "__main__":
    items = collect_actionable_items()
    print(f"Found {len(items)} actionable items in overnight results")
    append_to_tracker(items)
