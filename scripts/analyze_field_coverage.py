"""Step 3.3: Field Coverage and Quality Matrix.

Walks phase_c/, phase_d/, phase_e/ and for each book:
- Reads extraction.json (deterministic fields)
- Reads result.json (final metadata with LLM-inferred fields)
- Computes per-field coverage from extraction vs final result
- Outputs results/FIELD_QUALITY_MATRIX.md
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


# Fields to track
EXTRACTION_FIELDS = [
    "title_full", "author_name_raw", "author_short", "shamela_category",
    "publisher", "edition", "muhaqiq", "is_multi_volume", "volume_count",
    "has_muqaddima", "death_date_raw",
]

RESULT_FIELDS = [
    "title_arabic", "genre", "science_scope", "is_multi_layer",
    "structural_format", "authority_level", "trust_tier", "trust_score",
    "text_fidelity", "page_count", "volume_count", "publisher",
]


def is_present(value: object) -> bool:
    """Check if a field value is meaningfully present (not None/empty/default)."""
    if value is None:
        return False
    if isinstance(value, str) and not value.strip():
        return False
    if isinstance(value, list) and len(value) == 0:
        return False
    return True


def main() -> None:
    base = Path("tests/results/source_engine")
    phases = ["phase_c", "phase_d", "phase_e"]

    extraction_coverage: dict[str, int] = defaultdict(int)
    result_coverage: dict[str, int] = defaultdict(int)
    total_books = 0
    success_books = 0

    # Per-phase stats
    phase_stats: dict[str, dict[str, int]] = {}

    for phase in phases:
        phase_dir = base / phase
        if not phase_dir.exists():
            continue

        phase_total = 0
        phase_success = 0
        phase_ext: dict[str, int] = defaultdict(int)
        phase_res: dict[str, int] = defaultdict(int)

        for book_dir in sorted(phase_dir.iterdir()):
            if not book_dir.is_dir() or book_dir.name.startswith("_"):
                continue

            result_file = book_dir / "result.json"
            ext_file = book_dir / "extraction.json"

            if not result_file.exists():
                continue

            total_books += 1
            phase_total += 1

            result = json.loads(result_file.read_text(encoding="utf-8"))
            status = result.get("status", "")

            # Check extraction fields
            if ext_file.exists():
                ext = json.loads(ext_file.read_text(encoding="utf-8"))
                for field in EXTRACTION_FIELDS:
                    if is_present(ext.get(field)):
                        extraction_coverage[field] += 1
                        phase_ext[field] += 1

            # Check result fields (only for success books)
            if status == "success":
                success_books += 1
                phase_success += 1
                for field in RESULT_FIELDS:
                    val = result.get(field)
                    # Handle nested author object
                    if field == "title_arabic" and is_present(val):
                        result_coverage[field] += 1
                        phase_res[field] += 1
                    elif is_present(val):
                        result_coverage[field] += 1
                        phase_res[field] += 1

        phase_stats[phase] = {
            "total": phase_total,
            "success": phase_success,
            "ext": dict(phase_ext),
            "res": dict(phase_res),
        }

    # Build report
    lines: list[str] = []
    lines.append("# Field Coverage and Quality Matrix")
    lines.append("")
    lines.append(f"**Date:** 2026-03-22")
    lines.append(f"**Total books analyzed:** {total_books}")
    lines.append(f"**Successful (full metadata):** {success_books}")
    lines.append(f"**Gate abort (partial):** {total_books - success_books}")
    lines.append("")

    # Per-phase overview
    lines.append("## Phase Overview")
    lines.append("")
    lines.append("| Phase | Total | Success | Gate Abort | Success Rate |")
    lines.append("|-------|-------|---------|------------|-------------|")
    for phase in phases:
        ps = phase_stats.get(phase, {"total": 0, "success": 0})
        ga = ps["total"] - ps["success"]
        rate = ps["success"] / max(1, ps["total"]) * 100
        lines.append(f"| {phase} | {ps['total']} | {ps['success']} | {ga} | {rate:.0f}% |")
    lines.append("")

    # Extraction field coverage
    lines.append("## Extraction Field Coverage (Deterministic)")
    lines.append("")
    lines.append("These fields are extracted from Shamela HTML markup without LLM inference.")
    lines.append("")
    lines.append("| Field | Present | Total | Coverage |")
    lines.append("|-------|---------|-------|----------|")
    for field in EXTRACTION_FIELDS:
        count = extraction_coverage.get(field, 0)
        pct = count / max(1, total_books) * 100
        lines.append(f"| {field} | {count} | {total_books} | {pct:.1f}% |")
    lines.append("")

    # Result field coverage (success books only)
    lines.append("## Result Field Coverage (After LLM Inference)")
    lines.append("")
    lines.append("These fields include LLM-inferred values. Only success books counted.")
    lines.append("")
    lines.append("| Field | Present | Success Books | Coverage |")
    lines.append("|-------|---------|--------------|----------|")
    for field in RESULT_FIELDS:
        count = result_coverage.get(field, 0)
        pct = count / max(1, success_books) * 100
        lines.append(f"| {field} | {count} | {success_books} | {pct:.1f}% |")
    lines.append("")

    # Extraction → Inference improvement
    lines.append("## Extraction → Inference Improvement")
    lines.append("")
    lines.append("Fields where LLM inference improves coverage over deterministic extraction.")
    lines.append("")

    # Map extraction fields to their result equivalents
    field_mapping = {
        "title_full": "title_arabic",
        "volume_count": "volume_count",
        "publisher": "publisher",
    }

    lines.append("| Field | Extraction % | Result % | Improvement |")
    lines.append("|-------|-------------|---------|-------------|")
    for ext_field, res_field in field_mapping.items():
        ext_pct = extraction_coverage.get(ext_field, 0) / max(1, total_books) * 100
        res_pct = result_coverage.get(res_field, 0) / max(1, success_books) * 100
        improvement = res_pct - ext_pct
        sign = "+" if improvement > 0 else ""
        lines.append(f"| {ext_field} → {res_field} | {ext_pct:.1f}% | {res_pct:.1f}% | {sign}{improvement:.1f}pp |")
    lines.append("")

    # Fields only available from LLM
    lines.append("## LLM-Only Fields")
    lines.append("")
    lines.append("These fields have no deterministic extraction source — they require LLM inference.")
    lines.append("")
    llm_only = ["genre", "science_scope", "is_multi_layer", "structural_format",
                 "authority_level", "trust_tier", "trust_score", "text_fidelity"]
    lines.append("| Field | Coverage (success books) |")
    lines.append("|-------|------------------------|")
    for field in llm_only:
        count = result_coverage.get(field, 0)
        pct = count / max(1, success_books) * 100
        lines.append(f"| {field} | {pct:.1f}% |")
    lines.append("")

    # Per-phase extraction details
    lines.append("## Per-Phase Extraction Coverage")
    lines.append("")
    for phase in phases:
        ps = phase_stats.get(phase, {"total": 0, "ext": {}})
        if ps["total"] == 0:
            continue
        lines.append(f"### {phase} ({ps['total']} books)")
        lines.append("")
        lines.append("| Field | Coverage |")
        lines.append("|-------|----------|")
        for field in EXTRACTION_FIELDS:
            count = ps["ext"].get(field, 0)
            pct = count / max(1, ps["total"]) * 100
            lines.append(f"| {field} | {pct:.0f}% |")
        lines.append("")

    # Write report
    out = Path("results/FIELD_QUALITY_MATRIX.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {out}")
    print(f"Total: {total_books}, Success: {success_books}")
    for field in EXTRACTION_FIELDS:
        print(f"  ext.{field}: {extraction_coverage.get(field, 0)}/{total_books}")


if __name__ == "__main__":
    main()
