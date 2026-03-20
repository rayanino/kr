"""Extract structured data from markdown tables in SPEC files.

Parses pipe-delimited markdown tables into JSON for programmatic access.
Useful for validating code markers, classifications, and constants against
SPEC-defined tables.

Usage:
    python scripts/extract_spec_tables.py <spec_file> [--section <header>] [--json]
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path


def extract_tables(text: str) -> list[dict[str, object]]:
    """Extract all pipe-delimited tables from markdown text."""
    lines = text.split("\n")
    tables: list[dict[str, object]] = []
    current_section = ""
    i = 0

    while i < len(lines):
        sec = re.match(r"^(#{1,4})\s+(.+)", lines[i])
        if sec:
            current_section = sec.group(2).strip()

        # Table start: pipe row followed by separator row
        if (
            "|" in lines[i]
            and i + 1 < len(lines)
            and re.match(r"^\s*\|[\s:|-]+\|", lines[i + 1])
        ):
            headers = _parse_row(lines[i])
            i += 2  # skip header + separator

            rows: list[dict[str, str]] = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                values = _parse_row(lines[i])
                if len(values) == len(headers):
                    rows.append(dict(zip(headers, values)))
                i += 1

            tables.append({
                "section": current_section,
                "headers": headers,
                "rows": rows,
                "row_count": len(rows),
            })
        else:
            i += 1

    return tables


def _parse_row(line: str) -> list[str]:
    """Parse a pipe-delimited table row into cells."""
    cells = line.split("|")
    if cells and not cells[0].strip():
        cells = cells[1:]
    if cells and not cells[-1].strip():
        cells = cells[:-1]
    return [c.strip() for c in cells]


def extract_marker_table(
    tables: list[dict[str, object]],
) -> dict[str, list[str]]:
    """Extract marker tables into {category: [markers]} structure."""
    markers: dict[str, list[str]] = {}

    for table in tables:
        headers = table.get("headers", [])
        rows = table.get("rows", [])
        if not isinstance(headers, list) or not isinstance(rows, list):
            continue

        cat_col = None
        marker_col = None
        for h in headers:
            hl = h.lower()
            if any(k in hl for k in ("category", "type", "class", "signal")):
                cat_col = h
            if any(k in hl for k in ("marker", "pattern", "keyword", "value", "text")):
                marker_col = h

        if cat_col and marker_col:
            for row in rows:
                if not isinstance(row, dict):
                    continue
                cat = row.get(cat_col, "unknown")
                marker = row.get(marker_col, "")
                if cat and marker:
                    markers.setdefault(cat, []).append(marker)

    return markers


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[attr-defined]

    if len(sys.argv) < 2:
        print("Usage: extract_spec_tables.py <spec_file> [--section <header>] [--json]")
        return 1

    spec_path = Path(sys.argv[1])
    if not spec_path.exists():
        print(f"File not found: {spec_path}", file=sys.stderr)
        return 1

    section_filter = None
    if "--section" in sys.argv:
        idx = sys.argv.index("--section")
        if idx + 1 < len(sys.argv):
            section_filter = sys.argv[idx + 1]

    output_json = "--json" in sys.argv

    text = spec_path.read_text(encoding="utf-8", errors="ignore")
    tables = extract_tables(text)

    if section_filter:
        tables = [
            t for t in tables
            if section_filter.lower() in str(t.get("section", "")).lower()
        ]

    if output_json:
        output = {"tables": tables}
        markers = extract_marker_table(tables)
        if markers:
            output["markers"] = markers
        print(json.dumps(output, indent=2, ensure_ascii=False))
    else:
        for table in tables:
            section = table.get("section", "Unknown")
            rows = table.get("rows", [])
            headers = table.get("headers", [])
            if not isinstance(rows, list):
                continue
            print(f"\n=== {section} ({len(rows)} rows) ===")
            if isinstance(headers, list):
                print("  Columns: " + " | ".join(headers))
            for row in rows[:5]:
                if isinstance(row, dict):
                    print("  " + " | ".join(str(v) for v in row.values()))
            if len(rows) > 5:
                print(f"  ... and {len(rows) - 5} more rows")

        markers = extract_marker_table(tables)
        if markers:
            print("\n=== Extracted Markers ===")
            for cat, items in markers.items():
                print(f"  {cat}: {', '.join(items[:10])}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
