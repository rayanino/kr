"""Deliverable 4: Generate EVALUATION_WORKBOOK.md from division data + LLM results.

Reads division JSONs from D2 and result JSONs from D3 to produce the architect's
primary evaluation input. Contains FULL Arabic text — no truncation.

Only Approach A and B (no Approach C).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

DIVISIONS_DIR = Path(__file__).resolve().parent / "divisions"
RESULTS_DIR = Path(__file__).resolve().parent / "results"
OUTPUT_PATH = Path(__file__).resolve().parent / "EVALUATION_WORKBOOK.md"


def load_all_divisions() -> list[dict]:
    """Load all division JSON files."""
    divisions: list[dict] = []
    for fixture_dir in sorted(DIVISIONS_DIR.iterdir()):
        if not fixture_dir.is_dir():
            continue
        for json_file in sorted(fixture_dir.glob("div_*.json")):
            if "_text" in json_file.name:
                continue
            with open(json_file, "r", encoding="utf-8") as f:
                divisions.append(json.load(f))
    return divisions


def load_result(fixture: str, div_start: int, approach: str) -> dict | None:
    """Load a result JSON, or None if missing/error."""
    path = RESULTS_DIR / fixture / f"div_{div_start}_approach_{approach}.json"
    if not path.exists():
        return None
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if "error" in data:
        return None
    return data


def format_teaching_units_table(result: dict) -> str:
    """Format teaching units as a markdown table."""
    units = result.get("teaching_units", [])
    if not units:
        return "*No teaching units found.*\n"

    lines: list[str] = []
    lines.append("| # | Words | Function | Self-contained | Snippet |")
    lines.append("|---|-------|----------|----------------|---------|")

    for u in units:
        sc = "+" if u.get("self_contained", False) else "-"
        snippet = u.get("text_snippet", "")[:60].replace("|", "\\|")
        func = u.get("primary_function", "?")
        lines.append(
            f"| {u.get('unit_index', '?')} "
            f"| {u.get('start_word', '?')}-{u.get('end_word', '?')} "
            f"| {func} "
            f"| {sc} "
            f"| {snippet} |"
        )

    lines.append("")

    # Description per unit
    lines.append("**Description per unit:**")
    for u in units:
        desc = u.get("description_arabic", "")
        sc_notes = u.get("self_containment_notes", "")
        line = f"- Unit {u.get('unit_index', '?')}: {desc}"
        if sc_notes:
            line += f" — *{sc_notes}*"
        lines.append(line)

    return "\n".join(lines)


def generate_workbook(divisions: list[dict]) -> str:
    """Generate the full evaluation workbook markdown."""
    sections: list[str] = []

    sections.append("# Format Diversity — Evaluation Workbook\n")
    sections.append(
        "This workbook contains the complete results of the format diversity experiment.\n"
        "For each of the test divisions: full Arabic text, and results from Approach A and B.\n\n"
        "**Purpose:** Validate LLM teaching-unit extraction on (1) verse-commentary text "
        "and (2) longer prose divisions (2000-4000w).\n\n"
        "**Architect:** Read the Arabic text, then judge whether the LLM's teaching unit "
        "identification makes sense.\n"
    )
    sections.append("---\n")

    for div in divisions:
        fixture = div["fixture_name"]
        div_start = div["div_start_unit"]
        div_end = div["div_end_unit"]
        heading = div["heading_text"]
        wc = div["arabic_word_count"]

        bc_last = div.get("boundary_continuity_last_unit") or {}
        bc_type = bc_last.get("type", "N/A")
        bc_conf = bc_last.get("confidence", "N/A")

        verse_tag = " | **VERSE-COMMENTARY**" if div.get("has_verse_content") else ""

        sections.append(f"## Division: {heading}\n")
        sections.append(
            f"**Fixture:** {fixture} | "
            f"**Words:** {wc} | "
            f"**Units:** {div_start}-{div_end} | "
            f"**BC last:** {bc_type} ({bc_conf})"
            f"{verse_tag}\n"
        )

        # Full Arabic text
        sections.append("### Full Arabic Text\n")
        sections.append(div["assembled_text"])
        sections.append("")

        # Approach A
        result_a = load_result(fixture, div_start, "a")
        if result_a:
            n_a = result_a.get("total_units", len(result_a.get("teaching_units", [])))
            sections.append(f"### Approach A Results ({n_a} teaching units)\n")
            sections.append(format_teaching_units_table(result_a))
        else:
            sections.append("### Approach A Results\n")
            sections.append("*Error or not available.*\n")

        sections.append("")

        # Approach B
        result_b = load_result(fixture, div_start, "b")
        if result_b:
            n_b = result_b.get("total_units", len(result_b.get("teaching_units", [])))
            sections.append(f"### Approach B Results ({n_b} teaching units)\n")
            sections.append(format_teaching_units_table(result_b))
        else:
            sections.append("### Approach B Results\n")
            sections.append("*Error or not available.*\n")

        sections.append("")

        # Comparison notes
        sections.append("### Comparison Notes\n")
        notes: list[str] = []

        if result_a and result_b:
            n_a = result_a.get("total_units", 0)
            n_b = result_b.get("total_units", 0)
            notes.append(f"- A produced {n_a} units, B produced {n_b} units")
            if n_a != n_b:
                notes.append(f"- Unit count difference: {abs(n_a - n_b)}")

        if not notes:
            notes.append("- Insufficient data for comparison")

        sections.append("\n".join(notes))
        sections.append("\n---\n")

    return "\n".join(sections)


def main() -> None:
    divisions = load_all_divisions()
    print(f"Loaded {len(divisions)} divisions")

    workbook = generate_workbook(divisions)

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write(workbook)

    print(f"Workbook written to: {OUTPUT_PATH}")
    print(f"Size: {len(workbook):,} characters")

    # Quick stats
    result_count = 0
    for fixture_dir in RESULTS_DIR.iterdir():
        if fixture_dir.is_dir():
            result_count += len(list(fixture_dir.glob("div_*_approach_*.json")))
    print(f"Total result files found: {result_count}")


if __name__ == "__main__":
    main()
