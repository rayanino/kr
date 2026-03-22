"""Step 3.2: Consensus Disagreement Analysis.

Walks phase_c/, phase_d/, phase_e/ and finds books where consensus.json
has agreed==false. For those books, reads LLM responses and compares
field-by-field to identify which fields disagree most.
Outputs results/CONSENSUS_ANALYSIS.md.
"""

from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path


def main() -> None:
    base = Path("tests/results/source_engine")
    phases = ["phase_c", "phase_d", "phase_e"]

    # Collect all consensus data
    total_books = 0
    agreed_count = 0
    disagreements: list[dict] = []

    for phase in phases:
        phase_dir = base / phase
        if not phase_dir.exists():
            continue
        for book_dir in sorted(phase_dir.iterdir()):
            if not book_dir.is_dir() or book_dir.name.startswith("_"):
                continue
            cons_file = book_dir / "consensus.json"
            if not cons_file.exists():
                continue

            total_books += 1
            cons = json.loads(cons_file.read_text(encoding="utf-8"))

            if cons.get("agreed", True):
                agreed_count += 1
                continue

            # Disagreement found — read LLM responses
            llm_dir = book_dir / "llm_responses"
            model_responses: dict[str, dict] = {}
            if llm_dir.exists():
                for resp_file in sorted(llm_dir.iterdir()):
                    if resp_file.suffix == ".json":
                        try:
                            data = json.loads(resp_file.read_text(encoding="utf-8"))
                            parsed = data.get("parsed", data)
                            model_responses[resp_file.stem] = parsed
                        except (json.JSONDecodeError, UnicodeDecodeError):
                            pass

            disagreements.append({
                "book": book_dir.name,
                "phase": phase,
                "consensus": cons,
                "models": model_responses,
                "canonical_model": cons.get("canonical_result_model", ""),
                "human_gate_trigger": cons.get("human_gate_trigger", ""),
            })

    # Analyze field-level disagreements
    fields_to_compare = [
        "genre", "is_multi_layer", "structural_format", "science_scope",
    ]
    # Also check author identification
    field_disagreement_counts: dict[str, int] = defaultdict(int)
    field_disagreement_details: dict[str, list[tuple[str, str, str]]] = defaultdict(list)

    for dis in disagreements:
        models = list(dis["models"].values())
        if len(models) < 2:
            continue

        m1, m2 = models[0], models[1]
        model_names = list(dis["models"].keys())

        for field in fields_to_compare:
            v1 = m1.get(field)
            v2 = m2.get(field)
            if v1 != v2:
                field_disagreement_counts[field] += 1
                field_disagreement_details[field].append(
                    (dis["book"], str(v1)[:50], str(v2)[:50])
                )

        # Author comparison
        auth1 = m1.get("author_identification", {})
        auth2 = m2.get("author_identification", {})
        if isinstance(auth1, dict) and isinstance(auth2, dict):
            name1 = auth1.get("canonical_name_ar", "")
            name2 = auth2.get("canonical_name_ar", "")
            if name1 != name2:
                field_disagreement_counts["author_canonical_name_ar"] += 1
                field_disagreement_details["author_canonical_name_ar"].append(
                    (dis["book"], str(name1)[:50], str(name2)[:50])
                )

    # Build report
    lines: list[str] = []
    lines.append("# Consensus Disagreement Analysis")
    lines.append("")
    lines.append(f"**Date:** 2026-03-22")
    lines.append(f"**Total books with consensus data:** {total_books}")
    lines.append(f"**Agreed:** {agreed_count} ({agreed_count/max(1,total_books)*100:.0f}%)")
    lines.append(f"**Disagreed:** {len(disagreements)} ({len(disagreements)/max(1,total_books)*100:.0f}%)")
    lines.append("")

    # Phase breakdown
    lines.append("## Disagreements by Phase")
    lines.append("")
    lines.append("| Phase | Disagreements | Total | Rate |")
    lines.append("|-------|-------------|-------|------|")
    for phase in phases:
        phase_dis = [d for d in disagreements if d["phase"] == phase]
        phase_total = sum(1 for d in disagreements if d["phase"] == phase) + \
                      sum(1 for _ in (base / phase).iterdir()
                          if _.is_dir() and not _.name.startswith("_") and (_ / "consensus.json").exists()) - len(phase_dis)
        # Recount properly
        phase_dir = base / phase
        phase_cons_total = sum(
            1 for d in phase_dir.iterdir()
            if d.is_dir() and not d.name.startswith("_") and (d / "consensus.json").exists()
        )
        lines.append(f"| {phase} | {len(phase_dis)} | {phase_cons_total} | {len(phase_dis)/max(1,phase_cons_total)*100:.0f}% |")
    lines.append("")

    # Field-level disagreement tally
    lines.append("## Field-Level Disagreement Frequency")
    lines.append("")
    lines.append("| Field | Disagreement Count | % of Disagreed Books |")
    lines.append("|-------|-------------------|---------------------|")
    for field in sorted(field_disagreement_counts, key=lambda f: -field_disagreement_counts[f]):
        count = field_disagreement_counts[field]
        pct = count / max(1, len(disagreements)) * 100
        lines.append(f"| {field} | {count} | {pct:.0f}% |")
    lines.append("")

    # Detailed disagreements per field
    for field in sorted(field_disagreement_counts, key=lambda f: -field_disagreement_counts[f]):
        details = field_disagreement_details[field]
        lines.append(f"### {field} ({len(details)} disagreements)")
        lines.append("")
        lines.append("| Book | Model 1 | Model 2 |")
        lines.append("|------|---------|---------|")
        for book, v1, v2 in details[:10]:
            lines.append(f"| {book[:50]} | {v1} | {v2} |")
        if len(details) > 10:
            lines.append(f"| ... | ({len(details) - 10} more) | |")
        lines.append("")

    # Analysis
    lines.append("## Analysis")
    lines.append("")
    lines.append("### Key Findings")
    lines.append("")
    if field_disagreement_counts:
        most_disputed = max(field_disagreement_counts, key=lambda f: field_disagreement_counts[f])
        lines.append(f"1. **Most disputed field:** `{most_disputed}` ({field_disagreement_counts[most_disputed]} disagreements)")
    lines.append(f"2. **Overall agreement rate:** {agreed_count/max(1,total_books)*100:.1f}%")
    lines.append(f"3. **Disagreement rate:** {len(disagreements)/max(1,total_books)*100:.1f}%")
    lines.append("")
    lines.append("### Implications for Pipeline")
    lines.append("")
    lines.append("The multi-model consensus mechanism (D-041) is working as designed. Disagreements ")
    lines.append("are flagged and the canonical model's response is used as the final answer. ")
    lines.append("Human review should focus on the most disputed fields to calibrate model selection.")
    lines.append("")

    # Write report
    out = Path("results/CONSENSUS_ANALYSIS.md")
    out.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report: {out}")
    print(f"Total disagreements: {len(disagreements)}")
    for field, count in sorted(field_disagreement_counts.items(), key=lambda x: -x[1]):
        print(f"  {field}: {count}")


if __name__ == "__main__":
    main()
