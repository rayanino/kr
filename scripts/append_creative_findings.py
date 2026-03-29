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


def _sanitize_markdown(text: str) -> str:
    """Strip newlines and markdown-breaking characters from a string."""
    return text.replace("\n", " ").replace("\r", "").replace("[", "(").replace("]", ")").replace("#", "").strip()


def load_existing_ids(tracker_text: str) -> set[str]:
    """Extract existing item IDs to avoid duplicates (by ID, not summary text)."""
    ids: set[str] = set()
    for line in tracker_text.splitlines():
        # Match any ID format: BUG-001, IMP-001, CREATIVE-2026-03-29-001, etc.
        m = re.match(r"^- \[[ x]\] ([A-Za-z][\w-]+):", line)
        if m:
            ids.add(m.group(1).strip())
    return ids


def collect_actionable_items() -> list[dict]:
    """Find actionable.json files from creative task outputs."""
    items: list[dict] = []
    for f in sorted(OVERNIGHT_RESULTS.rglob("actionable.json")):
        # Only process creative task outputs (skip hardening task dirs)
        if "creative" not in f.parent.name and "creative" not in str(f.parent.parent.name):
            continue
        # Size guard: skip oversized files (LLM could hallucinate huge output)
        if f.stat().st_size > 1_000_000:
            print(f"  WARNING: Skipping oversized {f} ({f.stat().st_size} bytes)")
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
            if isinstance(data, list):
                for item in data:
                    # Normalize: accept summary/action/finding as the description
                    if isinstance(item, dict):
                        summary = (
                            item.get("summary")
                            or item.get("action")
                            or item.get("finding")
                            or item.get("description")
                        )
                        if summary:
                            item["summary"] = summary
                            items.append(item)
        except (json.JSONDecodeError, OSError):
            continue
    return items


def append_to_tracker(items: list[dict]) -> int:
    """Append new actionable items to FINDINGS_TRACKER.md. Returns count added."""
    if not FINDINGS_TRACKER.exists():
        print("FINDINGS_TRACKER.md not found — skipping")
        return 0

    tracker_text = FINDINGS_TRACKER.read_text(encoding="utf-8")
    existing_ids = load_existing_ids(tracker_text)
    added = 0

    for item in items:
        summary = _sanitize_markdown(item.get("summary", ""))
        if not summary:
            continue

        category = item.get("category", "IMP")
        item_id = _sanitize_markdown(item.get("id", f"CREATIVE-{added + 1:03d}"))
        # Deduplicate by ID (not summary text — avoids re-append on summary format changes)
        if item_id in existing_ids:
            continue

        effort = _sanitize_markdown(item.get("effort", "M"))
        priority = _sanitize_markdown(item.get("priority", "MEDIUM"))
        source = _sanitize_markdown(item.get("source_report", ""))

        section_header = SECTION_MAP.get(category, SECTION_MAP["IMP"])
        line = f"- [ ] {item_id}: {summary} ({effort} effort, {priority}) {source}"

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

        existing_ids.add(item_id)
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
