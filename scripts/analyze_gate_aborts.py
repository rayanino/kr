"""Step 3.1: Gate Abort Deep Dive.

Walks phase_c/, phase_d/, phase_e/ result directories.
Groups gate_abort books by error reason, checks extraction data.
Outputs results/GATE_ABORT_ANALYSIS.md.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    base = Path("tests/results/source_engine")
    phases = ["phase_c", "phase_d", "phase_e"]

    # Collect all gate abort data
    gate_aborts: list[dict] = []

    for phase in phases:
        phase_dir = base / phase
        if not phase_dir.exists():
            continue
        for book_dir in sorted(phase_dir.iterdir()):
            if not book_dir.is_dir() or book_dir.name.startswith("_"):
                continue
            result_file = book_dir / "result.json"
            if not result_file.exists():
                continue
            result = json.loads(result_file.read_text(encoding="utf-8"))
            status = result.get("status", "")
            if status != "gate_abort":
                continue

            # Extract gate error info
            gate_errors = result.get("gate_errors", [])
            error_code = result.get("error_code", "unknown")

            # Check extraction.json for author_name_raw
            ext_file = book_dir / "extraction.json"
            has_author_raw = False
            author_raw = ""
            if ext_file.exists():
                ext = json.loads(ext_file.read_text(encoding="utf-8"))
                author_raw = ext.get("author_name_raw", "") or ext.get("author_short", "") or ""
                has_author_raw = bool(author_raw)

            book_name = result.get("book", book_dir.name)

            gate_aborts.append({
                "book": book_name,
                "phase": phase,
                "error_code": error_code,
                "gate_errors": gate_errors,
                "has_author_raw": has_author_raw,
                "author_raw": author_raw,
                "cost": result.get("cost_estimate_eur", 0),
                "time": result.get("processing_time_seconds", 0),
            })

    # Group by primary gate error reason
    reason_groups: dict[str, list[dict]] = defaultdict(list)
    for ga in gate_aborts:
        if ga["gate_errors"]:
            # Use first error as primary reason
            reason = ga["gate_errors"][0]
            # Normalize common patterns
            if "don't overlap" in reason:
                key = "science_scope_mismatch"
            elif "death" in reason.lower() or "century" in reason.lower():
                key = "death_date_discrepancy"
            elif "author" in reason.lower() and "not found" in reason.lower():
                key = "author_not_found"
            elif "confidence" in reason.lower():
                key = "low_confidence"
            else:
                key = reason[:60]
        else:
            key = f"error_code:{ga['error_code']}"
        reason_groups[key].append(ga)

    # Build report
    lines: list[str] = []
    lines.append("# Gate Abort Deep Dive")
    lines.append("")
    lines.append(f"**Date:** 2026-03-22")
    lines.append(f"**Total gate aborts:** {len(gate_aborts)} across {len(phases)} phases")
    lines.append(f"**Cost of aborted processing:** {sum(ga['cost'] for ga in gate_aborts):.1f} EUR")
    lines.append("")

    # Overview table
    lines.append("## Overview by Phase")
    lines.append("")
    lines.append("| Phase | Gate Aborts | Total Books | Abort Rate |")
    lines.append("|-------|-----------|-------------|------------|")
    for phase in phases:
        phase_dir = base / phase
        total = len([d for d in phase_dir.iterdir() if d.is_dir() and not d.name.startswith("_") and (d / "result.json").exists()])
        aborts = sum(1 for ga in gate_aborts if ga["phase"] == phase)
        rate = aborts / max(1, total) * 100
        lines.append(f"| {phase} | {aborts} | {total} | {rate:.0f}% |")
    lines.append("")

    # Reason groups
    lines.append("## Gate Abort Reasons (Grouped)")
    lines.append("")

    for reason, books in sorted(reason_groups.items(), key=lambda x: -len(x[1])):
        lines.append(f"### {reason} ({len(books)} books)")
        lines.append("")

        # Phases breakdown
        phase_counts = defaultdict(int)
        for b in books:
            phase_counts[b["phase"]] += 1
        phase_str = ", ".join(f"{p}: {c}" for p, c in sorted(phase_counts.items()))
        lines.append(f"**Phases:** {phase_str}")
        lines.append("")

        # Has author data?
        with_author = sum(1 for b in books if b["has_author_raw"])
        lines.append(f"**Has author in extraction:** {with_author}/{len(books)}")
        lines.append("")

        # Sample gate errors
        lines.append("**Sample errors:**")
        seen_errors: set[str] = set()
        for b in books[:5]:
            for err in b["gate_errors"]:
                if err not in seen_errors:
                    lines.append(f"- {err}")
                    seen_errors.add(err)
        lines.append("")

        # Book list (first 10)
        lines.append("**Books:**")
        for b in books[:15]:
            author_info = f" (author: {b['author_raw'][:30]})" if b["has_author_raw"] else " (no author)"
            lines.append(f"- [{b['phase']}] {b['book']}{author_info}")
        if len(books) > 15:
            lines.append(f"- ... and {len(books) - 15} more")
        lines.append("")

    # Analysis: Is the gate correct?
    lines.append("## Analysis: Is the Gate Correct?")
    lines.append("")
    lines.append("### Science Scope Mismatch")
    if "science_scope_mismatch" in reason_groups:
        lines.append(f"**{len(reason_groups['science_scope_mismatch'])} books** failed because the LLM-inferred ")
        lines.append(f"science scope doesn't overlap with the scholar's known sciences in the authority DB.")
        lines.append("")
        lines.append("This is the **correct behavior** — the gate catches cases where the LLM may have ")
        lines.append("misidentified the science or where the scholar authority record is incomplete. ")
        lines.append("These books need human review to determine which is correct.")
        lines.append("")

    lines.append("### Threshold Adjustment Candidates")
    lines.append("")
    lines.append("Books where extraction data is rich but gate still triggers are candidates for ")
    lines.append("threshold tuning. Currently, the gate is conservative (any validation issue ")
    lines.append("triggers abort). Possible improvements:")
    lines.append("")
    lines.append("1. **Distinguish hard vs soft gate errors** — science scope mismatch could be soft")
    lines.append("2. **Author matching confidence** — books with high-confidence author matches could bypass some checks")
    lines.append("3. **Phase C had 70% abort rate** — the earliest probes hit the most obscure books")
    lines.append("")

    # Write report
    out = Path("results/GATE_ABORT_ANALYSIS.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {out}")
    print(f"Total gate aborts: {len(gate_aborts)}")
    print(f"Reason groups: {len(reason_groups)}")
    for reason, books in sorted(reason_groups.items(), key=lambda x: -len(x[1])):
        print(f"  {reason}: {len(books)}")


if __name__ == "__main__":
    main()
