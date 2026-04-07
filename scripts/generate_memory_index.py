"""Generate MEMORY.md index from memory file frontmatter.

Scans all memory files, validates frontmatter, and generates a compact
index sorted by type and relevance. Replaces manual MEMORY.md curation.

Solves: 200-line ceiling, manual curation bottleneck, staleness detection.

Usage:
    python scripts/generate_memory_index.py [--check] [--fix-missing]

    --check       Validate only, don't write. Exit 1 if issues found.
    --fix-missing Add missing optional fields with defaults (non-destructive).
"""

from __future__ import annotations

import argparse
import logging
import re
import sys
from datetime import datetime
from pathlib import Path

import yaml

logger = logging.getLogger(__name__)

# Schema definition
REQUIRED_FIELDS = {"name", "description", "type"}
VALID_TYPES = {"user", "feedback", "project", "reference", "kunnash"}
VALID_STATUSES = {"active", "superseded", "archived"}
OPTIONAL_FIELDS = {
    "created_at": None,
    "scope": None,
    "status": "active",
    "supersedes": None,
    "source_agent": None,
    "confirmed_by": None,
}

MEMORY_DIR = Path.home() / ".claude" / "projects" / "C--Users-Rayane-Desktop-kr" / "memory"
INDEX_FILE = MEMORY_DIR / "MEMORY.md"


def parse_frontmatter(path: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\s*\n(.*?)\n---", text, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError as e:
        logger.warning("YAML parse error in %s: %s", path.name, e)
        return None


def validate_memory(path: Path, fm: dict) -> list[str]:
    """Validate frontmatter against schema. Returns list of issues."""
    issues = []

    for field in REQUIRED_FIELDS:
        if field not in fm:
            issues.append(f"missing required field: {field}")

    if "type" in fm and fm["type"] not in VALID_TYPES:
        issues.append(f"invalid type '{fm['type']}' (valid: {', '.join(sorted(VALID_TYPES))})")

    if "status" in fm and fm["status"] not in VALID_STATUSES:
        issues.append(f"invalid status '{fm['status']}' (valid: {', '.join(sorted(VALID_STATUSES))})")

    desc = fm.get("description", "")
    if desc and len(desc) > 200:
        issues.append(f"description too long ({len(desc)} chars, max 200)")

    return issues


def scan_memories(memory_dir: Path) -> list[dict]:
    """Scan all memory files and return validated entries."""
    entries = []

    for path in sorted(memory_dir.glob("*.md")):
        if path.name == "MEMORY.md":
            continue

        fm = parse_frontmatter(path)
        if fm is None:
            logger.warning("SKIP %s — no frontmatter", path.name)
            continue

        issues = validate_memory(path, fm)
        if issues:
            for issue in issues:
                logger.warning("ISSUE %s: %s", path.name, issue)

        entries.append({
            "filename": path.name,
            "name": fm.get("name", path.stem),
            "description": fm.get("description", ""),
            "type": fm.get("type", "unknown"),
            "status": fm.get("status", "active"),
            "scope": fm.get("scope"),
            "supersedes": fm.get("supersedes"),
        })

    return entries


def group_by_type(entries: list[dict]) -> dict[str, list[dict]]:
    """Group entries by type, active first within each group."""
    groups: dict[str, list[dict]] = {}
    for entry in entries:
        t = entry["type"]
        groups.setdefault(t, []).append(entry)

    for t in groups:
        groups[t].sort(key=lambda e: (0 if e["status"] == "active" else 1, e["name"]))

    return groups


TYPE_LABELS = {
    "feedback": "Feedback (Behavioral Corrections)",
    "project": "Project State & Decisions",
    "user": "User Profile",
    "reference": "External References",
    "kunnash": "Kunnash (Student Learning Notes)",
}

TYPE_ORDER = ["feedback", "project", "user", "reference", "kunnash"]


def generate_index(entries: list[dict]) -> str:
    """Generate the MEMORY.md index content."""
    groups = group_by_type(entries)

    lines = [
        "# KR Project Memory",
        "",
        f"Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M')} "
        f"from {len(entries)} memory files. Do not edit manually.",
        "",
        "**ROLE: Claude is the SENIOR ENGINEER + PRODUCT LEAD. The owner is the CLIENT.**",
        "",
    ]

    # Stats line
    type_counts = {t: len(g) for t, g in groups.items()}
    stats = " | ".join(f"{TYPE_LABELS.get(t, t)}: {c}" for t, c in sorted(type_counts.items()) if c > 0)
    lines.append(f"Totals: {len(entries)} memories — {stats}")
    lines.append("")

    active_count = sum(1 for e in entries if e["status"] == "active")
    archived_count = sum(1 for e in entries if e["status"] != "active")
    lines.append(f"Active: {active_count} | Archived/Superseded: {archived_count}")
    lines.append("")

    # Generate sections by type
    for t in TYPE_ORDER:
        if t not in groups:
            continue
        active = [e for e in groups[t] if e["status"] == "active"]
        inactive = [e for e in groups[t] if e["status"] != "active"]

        lines.append(f"## {TYPE_LABELS.get(t, t)}")
        lines.append("")

        for entry in active:
            desc = entry["description"]
            if len(desc) > 120:
                desc = desc[:117] + "..."
            supersede_note = ""
            if entry["supersedes"]:
                supersede_note = f" (supersedes {entry['supersedes']})"
            lines.append(f"- [{entry['name']}]({entry['filename']}) — {desc}{supersede_note}")

        if inactive:
            lines.append("")
            lines.append(f"<details><summary>{len(inactive)} archived/superseded</summary>")
            lines.append("")
            for entry in inactive:
                desc = entry["description"]
                if len(desc) > 80:
                    desc = desc[:77] + "..."
                lines.append(f"- ~~[{entry['name']}]({entry['filename']})~~ — {desc} [{entry['status']}]")
            lines.append("")
            lines.append("</details>")

        lines.append("")

    # Handle unknown types
    for t, group in groups.items():
        if t not in TYPE_ORDER:
            lines.append(f"## {t} (unrecognized type)")
            lines.append("")
            for entry in group:
                lines.append(f"- [{entry['name']}]({entry['filename']}) — {entry['description'][:120]}")
            lines.append("")

    return "\n".join(lines)


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Generate MEMORY.md from memory files")
    parser.add_argument("--check", action="store_true", help="Validate only, don't write")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    if not MEMORY_DIR.exists():
        logger.error("Memory directory not found: %s", MEMORY_DIR)
        return 1

    entries = scan_memories(MEMORY_DIR)
    logger.info("Scanned %d memory files", len(entries))

    # Count issues
    issue_count = 0
    for path in sorted(MEMORY_DIR.glob("*.md")):
        if path.name == "MEMORY.md":
            continue
        fm = parse_frontmatter(path)
        if fm is None:
            issue_count += 1
            continue
        issues = validate_memory(path, fm)
        issue_count += len(issues)

    if args.check:
        if issue_count > 0:
            logger.warning("%d issues found across memory files", issue_count)
            return 1
        logger.info("All memory files valid")
        return 0

    index_content = generate_index(entries)
    line_count = len(index_content.strip().split("\n"))

    INDEX_FILE.write_text(index_content, encoding="utf-8")
    logger.info("Wrote MEMORY.md: %d entries, %d lines", len(entries), line_count)

    if line_count > 200:
        logger.warning(
            "Index is %d lines (200 limit). Consider archiving stale memories.", line_count
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
