#!/usr/bin/env python3
"""Phase D Post-Processing: rename files, tag reruns, generate auto-screening report."""

from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
PHASE_D_DIR = PROJECT_ROOT / "tests" / "results" / "source_engine" / "phase_d"
PHASE_C_DIR = PROJECT_ROOT / "tests" / "results" / "source_engine" / "phase_c"
COST_LOG_PATH = PROJECT_ROOT / "tests" / "results" / "source_engine" / "COST_LOG.json"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, data: Any) -> None:
    path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )


# ── Task 1: Rename and fix output files ──


def task1_rename_and_fix() -> None:
    print("Task 1: Rename and fix output files...")

    # Rename PHASE_C_MANIFEST.json → PHASE_D_MANIFEST.json
    c_manifest = PHASE_D_DIR / "PHASE_C_MANIFEST.json"
    d_manifest = PHASE_D_DIR / "PHASE_D_MANIFEST.json"
    if c_manifest.exists():
        data = load_json(c_manifest)
        data["phase"] = "D"
        for entry in data.get("books", {}).values():
            if "result_path" in entry:
                entry["result_path"] = entry["result_path"].replace(
                    "phase_c/", "phase_d/"
                )
        save_json(d_manifest, data)
        c_manifest.unlink()
        n = len(data.get("books", {}))
        print(f"  Renamed manifest: phase -> D, fixed {n} result_path entries")
    elif d_manifest.exists():
        print("  Manifest already renamed")
    else:
        print("  WARNING: No manifest found!")

    # Rename PHASE_C_SUMMARY.json → PHASE_D_SUMMARY.json
    c_summary = PHASE_D_DIR / "PHASE_C_SUMMARY.json"
    d_summary = PHASE_D_DIR / "PHASE_D_SUMMARY.json"
    if c_summary.exists():
        data = load_json(c_summary)
        data["phase"] = "D"
        save_json(d_summary, data)
        c_summary.unlink()
        print("  Renamed summary: phase -> D")
    elif d_summary.exists():
        print("  Summary already renamed")
    else:
        print("  WARNING: No summary found!")

    # Fix COST_LOG.json — add D entry, leave C as-is (inaccurate but historical)
    cost_log = load_json(COST_LOG_PATH)
    phases = cost_log.setdefault("phases", {})
    c_phase = phases.get("C", {})
    phases["D"] = {
        "books": c_phase.get("books", 204),
        "cost_eur": c_phase.get("cost_eur", 20.4),
        "status": "complete",
    }
    save_json(COST_LOG_PATH, cost_log)
    print(
        f"  Updated COST_LOG: D entry added "
        f"({phases['D']['books']} books, {phases['D']['cost_eur']} EUR)"
    )


# ── Task 2: Tag rerun books ──


def task2_tag_reruns() -> set[str]:
    print("\nTask 2: Tag rerun books...")

    rerun_data = load_json(PHASE_D_DIR / "RERUN_BOOKS.json")
    rerun_books = set(rerun_data.get("books", []))

    tagged = 0
    rerun_count = 0
    for book_dir in sorted(PHASE_D_DIR.iterdir()):
        if not book_dir.is_dir():
            continue
        result_path = book_dir / "result.json"
        if not result_path.exists():
            continue
        result = load_json(result_path)
        is_rerun = book_dir.name in rerun_books
        result["is_rerun"] = is_rerun
        result["original_phase"] = "C" if is_rerun else None
        save_json(result_path, result)
        tagged += 1
        if is_rerun:
            rerun_count += 1

    print(f"  Tagged {tagged} books ({rerun_count} reruns, {tagged - rerun_count} new)")
    return rerun_books


# ── Task 3: Auto-screening report ──


def _get_book_dirs() -> list[Path]:
    return sorted(
        d
        for d in PHASE_D_DIR.iterdir()
        if d.is_dir() and (d / "result.json").exists()
    )


def _safe_get(data: Any, *keys: str, default: Any = None) -> Any:
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key, default)
        else:
            return default
    return data


def task3_auto_screening(rerun_books: set[str]) -> None:
    print("\nTask 3: Generate auto-screening report...")

    book_dirs = _get_book_dirs()

    # Load all Phase D results
    d_results: dict[str, dict] = {}
    for d in book_dirs:
        d_results[d.name] = load_json(d / "result.json")

    # Load Phase C manifest and results for regression comparison
    c_manifest_path = PHASE_C_DIR / "PHASE_C_MANIFEST.json"
    c_manifest_books: dict[str, dict] = {}
    if c_manifest_path.exists():
        c_manifest_books = load_json(c_manifest_path).get("books", {})

    c_results: dict[str, dict] = {}
    for name in rerun_books:
        c_result_path = PHASE_C_DIR / name / "result.json"
        if c_result_path.exists():
            c_results[name] = load_json(c_result_path)

    lines: list[str] = []
    lines.append("# Phase D Auto-Screening Report")
    lines.append("")
    lines.append(f"Generated: {datetime.now(timezone.utc).isoformat()}")
    lines.append("")

    # ── 3a: Regression comparison ──
    lines.append("## 3a. Regression Comparison (Rerun Books)")
    lines.append("")

    gate_to_success: list[str] = []
    success_to_success: list[str] = []
    success_to_gate: list[str] = []
    gate_to_gate: list[str] = []
    other_changes: list[tuple[str, str, str]] = []
    no_c_data: list[str] = []

    for name in sorted(rerun_books):
        d_status = d_results.get(name, {}).get("status", "unknown")

        c_data = c_results.get(name)
        if c_data:
            c_status = c_data.get("status", "unknown")
        elif name in c_manifest_books:
            c_status = c_manifest_books[name].get("status", "unknown")
        else:
            no_c_data.append(name)
            continue

        if c_status == "gate_abort" and d_status == "success":
            gate_to_success.append(name)
        elif c_status == "success" and d_status == "success":
            success_to_success.append(name)
        elif c_status == "success" and d_status == "gate_abort":
            success_to_gate.append(name)
        elif c_status == "gate_abort" and d_status == "gate_abort":
            gate_to_gate.append(name)
        else:
            other_changes.append((name, c_status, d_status))

    lines.append(f"**Total rerun books:** {len(rerun_books)}")
    lines.append("")
    lines.append(
        f"- gate_abort -> success (expected improvement): **{len(gate_to_success)}**"
    )
    lines.append(f"- success -> success (stable): **{len(success_to_success)}**")
    lines.append(
        f"- success -> gate_abort (REGRESSION): **{len(success_to_gate)}**"
    )
    lines.append(
        f"- gate_abort -> gate_abort (unchanged): **{len(gate_to_gate)}**"
    )
    if other_changes:
        lines.append(f"- Other changes: **{len(other_changes)}**")
    if no_c_data:
        lines.append(f"- No Phase C data available: **{len(no_c_data)}**")
    lines.append("")

    if success_to_gate:
        lines.append("### REGRESSIONS (success -> gate_abort)")
        lines.append("")
        lines.append("| Book | Phase C Status | Phase D Status |")
        lines.append("|------|---------------|---------------|")
        for name in success_to_gate:
            lines.append(f"| {name} | success | gate_abort |")
        lines.append("")

    if other_changes:
        lines.append("### Unexpected Status Changes")
        lines.append("")
        lines.append("| Book | Phase C | Phase D |")
        lines.append("|------|---------|---------|")
        for name, c_s, d_s in other_changes:
            lines.append(f"| {name} | {c_s} | {d_s} |")
        lines.append("")

    # Field comparison for success->success books
    if success_to_success:
        lines.append("### Field Comparison (success in both phases)")
        lines.append("")
        field_changes: list[tuple[str, list[tuple[str, str, str]]]] = []
        for name in success_to_success:
            c = c_results.get(name, {})
            d = d_results.get(name, {})
            changes: list[tuple[str, str, str]] = []

            c_author = _safe_get(c, "author", "name_arabic", default="")
            d_author = _safe_get(d, "author", "name_arabic", default="")
            if c_author != d_author:
                changes.append(("author", str(c_author), str(d_author)))

            c_genre = c.get("genre", "")
            d_genre = d.get("genre", "")
            if c_genre != d_genre:
                changes.append(("genre", c_genre, d_genre))

            c_ml = c.get("is_multi_layer")
            d_ml = d.get("is_multi_layer")
            if c_ml != d_ml:
                changes.append(("is_multi_layer", str(c_ml), str(d_ml)))

            c_trust = c.get("trust_tier", "")
            d_trust = d.get("trust_tier", "")
            if c_trust != d_trust:
                changes.append(("trust_tier", c_trust, d_trust))

            c_score = c.get("trust_score")
            d_score = d.get("trust_score")
            if c_score != d_score:
                c_s = f"{c_score:.4f}" if c_score is not None else "N/A"
                d_s = f"{d_score:.4f}" if d_score is not None else "N/A"
                changes.append(("trust_score", c_s, d_s))

            c_sci = sorted(c.get("science_scope", []))
            d_sci = sorted(d.get("science_scope", []))
            if c_sci != d_sci:
                changes.append(("science_scope", str(c_sci), str(d_sci)))

            if changes:
                field_changes.append((name, changes))

        if field_changes:
            lines.append("| Book | Field | Phase C | Phase D |")
            lines.append("|------|-------|---------|---------|")
            for name, changes in field_changes:
                for field, old, new in changes:
                    lines.append(f"| {name} | {field} | {old} | {new} |")
            lines.append("")
        else:
            lines.append(
                "All success->success books have identical output. "
                "No field-level regressions."
            )
            lines.append("")

    if no_c_data:
        lines.append("### Books With No Phase C Comparison Data")
        lines.append("")
        for name in no_c_data:
            lines.append(f"- {name}")
        lines.append("")

    # ── 3b: Statistical summary ──
    lines.append("## 3b. Statistical Summary")
    lines.append("")
    statuses = Counter(r.get("status", "unknown") for r in d_results.values())
    total = len(d_results)
    success = statuses.get("success", 0)
    gate_abort = statuses.get("gate_abort", 0)
    error = statuses.get("error", 0)

    lines.append(f"- **Total books:** {total}")
    lines.append(f"- **Success:** {success} ({100 * success / max(total, 1):.1f}%)")
    lines.append(f"- **Gate abort:** {gate_abort}")
    lines.append(f"- **Error:** {error}")
    lines.append(
        f"- **Success rate:** {100 * success / max(total, 1):.1f}%"
    )
    lines.append("")

    rerun_success = sum(
        1
        for n in rerun_books
        if d_results.get(n, {}).get("status") == "success"
    )
    rerun_gate = sum(
        1
        for n in rerun_books
        if d_results.get(n, {}).get("status") == "gate_abort"
    )
    new_books = [n for n in d_results if n not in rerun_books]
    new_success = sum(1 for n in new_books if d_results[n].get("status") == "success")
    new_gate = sum(
        1 for n in new_books if d_results[n].get("status") == "gate_abort"
    )

    c_success_count = len(success_to_success) + len(success_to_gate)
    c_gate_count = len(gate_to_success) + len(gate_to_gate)
    lines.append(
        f"- **Rerun books:** {len(rerun_books)} "
        f"({rerun_success} success, {rerun_gate} gate_abort)"
    )
    lines.append(
        f"  - Phase C had: {c_success_count + c_gate_count} comparable books "
        f"({c_success_count} success, {c_gate_count} gate_abort)"
    )
    lines.append(
        f"- **New books:** {len(new_books)} "
        f"({new_success} success, {new_gate} gate_abort)"
    )
    lines.append("")

    # ── 3c: Confidence outliers ──
    lines.append("## 3c. Confidence Outliers (any score < 0.75)")
    lines.append("")
    outliers: list[tuple[str, dict[str, float], float]] = []
    for name, r in d_results.items():
        if r.get("status") != "success":
            continue
        scores = r.get("confidence_scores", {})
        if isinstance(scores, dict):
            low = {
                k: v
                for k, v in scores.items()
                if isinstance(v, (int, float)) and v < 0.75
            }
            if low:
                min_score = min(low.values())
                outliers.append((name, low, min_score))

    outliers.sort(key=lambda x: x[2])
    if outliers:
        lines.append("| Book | Low Fields | Lowest Score |")
        lines.append("|------|-----------|-------------|")
        for name, low, min_s in outliers:
            fields = ", ".join(
                f"{k}={v:.2f}" for k, v in sorted(low.items(), key=lambda x: x[1])
            )
            lines.append(f"| {name} | {fields} | {min_s:.2f} |")
    else:
        lines.append("No books with any confidence score below 0.75.")
    lines.append("")

    # ── 3d: Consensus disagreements ──
    lines.append("## 3d. Consensus Disagreements")
    lines.append("")
    disagreements: list[tuple[str, dict]] = []
    for d in book_dirs:
        cons_path = d / "consensus.json"
        if cons_path.exists():
            cons = load_json(cons_path)
            if not cons.get("agreed", True):
                disagreements.append((d.name, cons))

    if disagreements:
        lines.append("| Book | Human Gate Trigger | Canonical Model |")
        lines.append("|------|-------------------|----------------|")
        for name, cons in disagreements:
            trigger = cons.get("human_gate_trigger", "N/A")
            canonical = cons.get("canonical_result_model", "unknown")
            lines.append(f"| {name} | {trigger} | {canonical} |")
    else:
        lines.append("All books show consensus agreement between models.")
    lines.append("")

    # ── 3e: Trust anomalies ──
    lines.append("## 3e. Trust Anomalies")
    lines.append("")
    flagged_success = [
        (n, r)
        for n, r in d_results.items()
        if r.get("trust_tier") == "flagged" and r.get("status") == "success"
    ]
    low_trust = [
        (n, r)
        for n, r in d_results.items()
        if isinstance(r.get("trust_score"), (int, float)) and r["trust_score"] < 0.5
    ]

    if flagged_success:
        lines.append("### Flagged + Success")
        lines.append("")
        lines.append("| Book | Trust Score |")
        lines.append("|------|------------|")
        for name, r in sorted(
            flagged_success, key=lambda x: x[1].get("trust_score", 0)
        ):
            lines.append(f"| {name} | {r.get('trust_score', 'N/A')} |")
        lines.append("")

    if low_trust:
        lines.append("### Trust Score < 0.5")
        lines.append("")
        lines.append("| Book | Trust Tier | Trust Score |")
        lines.append("|------|-----------|------------|")
        for name, r in sorted(low_trust, key=lambda x: x[1].get("trust_score", 0)):
            lines.append(
                f"| {name} | {r.get('trust_tier', 'N/A')} | {r.get('trust_score', 'N/A')} |"
            )
        lines.append("")

    if not flagged_success and not low_trust:
        lines.append("No trust anomalies detected.")
        lines.append("")

    # ── 3f: Multi-layer books ──
    lines.append("## 3f. Multi-Layer Books")
    lines.append("")
    multi_layer = [
        (n, r)
        for n, r in d_results.items()
        if r.get("is_multi_layer") is True and r.get("status") == "success"
    ]

    if multi_layer:
        lines.append("| Book | Text Layers |")
        lines.append("|------|------------|")
        for name, r in sorted(multi_layer):
            layers = r.get("text_layers", [])
            if layers:
                layer_names = []
                for layer in layers:
                    if isinstance(layer, dict):
                        layer_names.append(layer.get("layer_type", str(layer)))
                    else:
                        layer_names.append(str(layer))
                layer_str = ", ".join(layer_names)
            else:
                layer_str = "(empty)"
            lines.append(f"| {name} | {layer_str} |")
    else:
        lines.append("No multi-layer books detected.")
    lines.append("")

    # ── 3g: Remaining gate_aborts ──
    lines.append("## 3g. Remaining Gate Aborts")
    lines.append("")
    gate_aborts = [
        (n, r)
        for n, r in d_results.items()
        if r.get("status") == "gate_abort"
    ]

    if gate_aborts:
        lines.append("| Book | Error Code | Gate Errors |")
        lines.append("|------|-----------|------------|")
        for name, r in sorted(gate_aborts):
            code = r.get("error_code", "N/A")
            errors = r.get("gate_errors", [])
            err_str = "; ".join(str(e) for e in errors[:3]) if errors else "N/A"
            lines.append(f"| {name} | {code} | {err_str} |")
    else:
        lines.append(
            "**No gate aborts.** All books processed successfully."
        )
    lines.append("")

    # ── 3h: Category coverage ──
    lines.append("## 3h. Category Coverage")
    lines.append("")
    categories: Counter[str] = Counter()
    for d in book_dirs:
        ext_path = d / "extraction.json"
        if ext_path.exists():
            ext = load_json(ext_path)
            cat = ext.get("shamela_category", "unknown") or "unknown"
            categories[cat] += 1

    lines.append("| Category | Count |")
    lines.append("|----------|-------|")
    for cat, count in categories.most_common():
        lines.append(f"| {cat} | {count} |")
    lines.append(f"\n**Total categories:** {len(categories)}")
    lines.append("")

    # Write report
    report = "\n".join(lines)
    output_path = PHASE_D_DIR / "PHASE_D_AUTO_SCREENING.md"
    output_path.write_text(report, encoding="utf-8")
    print(f"  Generated {output_path.name} ({len(lines)} lines)")


# ── Main ──


def main() -> None:
    print("=" * 60)
    print("Phase D Post-Processing")
    print("=" * 60)

    if not PHASE_D_DIR.exists():
        print(f"ERROR: Phase D directory not found: {PHASE_D_DIR}")
        sys.exit(1)

    task1_rename_and_fix()
    rerun_books = task2_tag_reruns()
    task3_auto_screening(rerun_books)

    print("\n" + "=" * 60)
    print("Post-processing complete!")


if __name__ == "__main__":
    main()
