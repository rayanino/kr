#!/usr/bin/env python3
"""Analyze normalization sweep results and produce a calibration report.

Reads corpus_sweep.jsonl (one JSON object per book) and generates
CALIBRATION_REPORT.md with 9 analysis sections (B.1-B.9) for the
normalization transition gate.

Usage:
    python scripts/analyze_sweep_results.py \
        --input results/normalization_sweep_v2/corpus_sweep.jsonl \
        --output results/CALIBRATION_REPORT.md
"""

from __future__ import annotations

import argparse
import io
import json
import statistics
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Fix Windows console encoding
if sys.stdout.encoding != "utf-8":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


# -- Types --

Entry = dict[str, Any]


# -- Data Loading --


def load_jsonl(path: Path) -> list[Entry]:
    """Load all JSON lines from a JSONL file."""
    entries: list[Entry] = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                entries.append(json.loads(line))
            except json.JSONDecodeError as exc:
                print(f"WARNING: Skipping malformed line {i}: {exc}", file=sys.stderr)
    return entries


def partition(
    entries: list[Entry],
) -> tuple[list[Entry], list[Entry]]:
    """Split entries into (ok_books, crash_books).

    OK and VALIDATION_FAILED both have full content metrics.
    CRASH entries lack content fields.
    """
    ok: list[Entry] = []
    crashes: list[Entry] = []
    for e in entries:
        if e.get("status") == "CRASH":
            crashes.append(e)
        else:
            ok.append(e)
    return ok, crashes


# -- Helpers --


def safe_percentile(data: list[float | int], p: int) -> float:
    """Return the p-th percentile (1-based). Handles small datasets."""
    if not data:
        return 0.0
    if len(data) == 1:
        return float(data[0])
    qs = statistics.quantiles(data, n=100)
    idx = max(0, min(p - 1, len(qs) - 1))
    return float(qs[idx])


def safe_mean(data: list[float | int]) -> float:
    """Return mean, or 0.0 for empty data."""
    return statistics.mean(data) if data else 0.0


def safe_median(data: list[float | int]) -> float:
    """Return median, or 0.0 for empty data."""
    return statistics.median(data) if data else 0.0


def fmt(value: float | int | str, decimals: int = 2) -> str:
    """Format a numeric value for display."""
    if isinstance(value, str):
        return value
    if isinstance(value, int):
        return f"{value:,}"
    return f"{value:,.{decimals}f}"


def fmt_pct(value: float, decimals: int = 1) -> str:
    """Format a float (0-1 scale) as percentage."""
    return f"{value * 100:.{decimals}f}%"


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    """Build a Markdown table."""
    sep = ["-" * max(3, len(h)) for h in headers]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join(sep) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


# -- Section Functions --


def section_b1(
    ok: list[Entry], crashes: list[Entry], all_entries: list[Entry]
) -> str:
    """B.1: Corpus Statistics."""
    total = len(all_entries)
    ok_count = len(ok)
    crash_count = len(crashes)

    # Processing time
    elapsed = [e.get("elapsed_seconds", 0.0) for e in all_entries]
    total_time = sum(elapsed)

    # Book sizes (content units)
    sizes = [e.get("content_units", 0) for e in ok]
    total_pages = sum(e.get("raw_page_divs", 0) for e in ok if e.get("raw_page_divs", -1) >= 0)
    total_content_units = sum(sizes)

    lines = [
        "## B.1: Corpus Statistics\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Total books processed", fmt(total, 0)],
                ["OK", f"{fmt(ok_count, 0)} ({ok_count / total * 100:.1f}%)" if total else "0"],
                ["CRASH", f"{fmt(crash_count, 0)} ({crash_count / total * 100:.1f}%)" if total else "0"],
                ["Total content units", fmt(total_content_units, 0)],
                ["Total raw pages", fmt(total_pages, 0)],
            ],
        ),
        "",
        "**Processing time:**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Total", f"{total_time:.0f}s ({total_time / 60:.1f} min)"],
                ["Mean per-book", f"{safe_mean(elapsed):.2f}s"],
                ["Median", f"{safe_median(elapsed):.2f}s"],
                ["P95", f"{safe_percentile(elapsed, 95):.2f}s"],
                ["Max", f"{max(elapsed):.2f}s" if elapsed else "N/A"],
            ],
        ),
        "",
        "**Book size (content units):**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Mean", fmt(safe_mean(sizes))],
                ["Median", fmt(safe_median(sizes))],
                ["P95", fmt(safe_percentile(sizes, 95))],
                ["Max", fmt(max(sizes)) if sizes else "N/A"],
            ],
        ),
    ]
    return "\n".join(lines)


def section_b2(ok: list[Entry]) -> str:
    """B.2: Multi-Layer Detection at Scale."""
    auto_upgraded = [e for e in ok if e.get("auto_upgraded_multi")]
    auto_count = len(auto_upgraded)
    auto_pct = auto_count / len(ok) * 100 if ok else 0.0

    # Multi-layer units distribution for auto-upgraded books
    multi_units = [e.get("multi_layer_units", 0) for e in auto_upgraded]

    # False positive heuristic: multi_layer_units > 50% of content_units
    suspect_fp = [
        e
        for e in auto_upgraded
        if e.get("content_units", 0) > 0
        and e.get("multi_layer_units", 0) / e["content_units"] > 0.5
    ]

    # Top 20 by multi_layer_units
    top20 = sorted(auto_upgraded, key=lambda e: e.get("multi_layer_units", 0), reverse=True)[:20]

    lines = [
        "## B.2: Multi-Layer Detection at Scale\n",
        f"Books with `auto_upgraded_multi == true`: **{auto_count}** ({auto_pct:.1f}%)\n",
        "> Note: `auto_upgraded_multi` is set when `multi_layer_units > 0` — it indicates",
        "> the presence of any multi-layer content units, not necessarily a metadata upgrade.\n",
    ]

    if multi_units:
        lines.extend([
            "**Multi-layer units distribution (auto-upgraded books):**\n",
            md_table(
                ["Metric", "Value"],
                [
                    ["Mean", fmt(safe_mean(multi_units))],
                    ["Median", fmt(safe_median(multi_units))],
                    ["P95", fmt(safe_percentile(multi_units, 95))],
                    ["Max", fmt(max(multi_units))],
                ],
            ),
            "",
        ])

    lines.extend([
        f"**Suspected false positives** (multi_layer_units > 50% of content_units): "
        f"**{len(suspect_fp)}** ({len(suspect_fp) / auto_count * 100:.1f}% of auto-upgraded)"
        if auto_count
        else "**Suspected false positives**: N/A (no auto-upgraded books)",
        "",
        "> Caveat: The JSONL does not record per-unit detection method. The bracket-detection",
        "> filter from NEXT.md could not be applied. This heuristic uses the 50% threshold only.\n",
    ])

    if top20:
        lines.extend([
            "**Top 20 auto-upgraded books by multi_layer_units:**\n",
            md_table(
                ["Book", "Multi-layer units", "Total units", "Ratio"],
                [
                    [
                        e.get("name", "?"),
                        fmt(e.get("multi_layer_units", 0), 0),
                        fmt(e.get("content_units", 0), 0),
                        fmt_pct(
                            e.get("multi_layer_units", 0) / e["content_units"]
                            if e.get("content_units", 0) > 0
                            else 0.0
                        ),
                    ]
                    for e in top20
                ],
            ),
        ])

    return "\n".join(lines)


def section_b3(ok: list[Entry]) -> str:
    """B.3: Division Tree."""
    divs = [e.get("division_count", 0) for e in ok]
    zero_div = [e for e in ok if e.get("division_count", 0) == 0]
    overlap_books = [
        e for e in ok if e.get("warn_categories", {}).get("division_overlap", 0) > 0
    ]
    overlap_pct = len(overlap_books) / len(ok) * 100 if ok else 0.0

    lines = [
        "## B.3: Division Tree\n",
        "**Division count distribution:**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Mean", fmt(safe_mean(divs))],
                ["Median", fmt(safe_median(divs))],
                ["P95", fmt(safe_percentile(divs, 95))],
                ["Max", fmt(max(divs)) if divs else "N/A"],
            ],
        ),
        "",
        f"**Books with zero divisions:** {len(zero_div)} ({len(zero_div) / len(ok) * 100:.1f}%)\n"
        if ok
        else "",
        f"**Books with division overlap warnings:** {len(overlap_books)} ({overlap_pct:.1f}%)\n",
        md_table(
            ["Source", "Overlap rate"],
            [
                ["63-fixture evaluation", "14.0%"],
                ["Full corpus (this report)", f"{overlap_pct:.1f}%"],
            ],
        ),
    ]
    return "\n".join(lines)


def section_b4(ok: list[Entry]) -> str:
    """B.4: Boundary Continuity."""
    coverages = [e.get("bc_coverage", 0.0) for e in ok]
    mean_bc = safe_mean(coverages)

    # Aggregate bc_types
    agg_types: Counter[str] = Counter()
    for e in ok:
        for bc_type, count in e.get("bc_types", {}).items():
            agg_types[bc_type] += count
    total_bc = sum(agg_types.values())

    zero_bc = [e for e in ok if e.get("bc_coverage", 0.0) == 0.0]

    lines = [
        "## B.4: Boundary Continuity\n",
        f"**Mean BC coverage:** {fmt_pct(mean_bc)}\n",
        "**Aggregate BC type distribution:**\n",
    ]

    if total_bc > 0:
        rows = [
            [bc_type, fmt(count, 0), f"{count / total_bc * 100:.1f}%"]
            for bc_type, count in agg_types.most_common()
        ]
        lines.append(md_table(["Type", "Count", "Percentage"], rows))
    else:
        lines.append("No boundary continuity signals recorded.")

    lines.extend([
        "",
        f"**Books with 0% BC coverage:** {len(zero_bc)} ({len(zero_bc) / len(ok) * 100:.1f}%)"
        if ok
        else "",
    ])
    return "\n".join(lines)


def section_b5(ok: list[Entry]) -> str:
    """B.5: Content Flags."""
    total_hadith = sum(e.get("has_hadith", 0) for e in ok)
    total_quran = sum(e.get("has_quran", 0) for e in ok)
    total_verse = sum(e.get("has_verse", 0) for e in ok)
    total_pages = sum(e.get("content_units", 0) for e in ok)

    zero_flag = [
        e
        for e in ok
        if e.get("has_hadith", 0) == 0
        and e.get("has_quran", 0) == 0
        and e.get("has_verse", 0) == 0
    ]

    lines = [
        "## B.5: Content Flags\n",
        md_table(
            ["Flag", "Total pages", "% of corpus pages"],
            [
                ["has_hadith", fmt(total_hadith, 0), f"{total_hadith / total_pages * 100:.1f}%" if total_pages else "N/A"],
                ["has_quran", fmt(total_quran, 0), f"{total_quran / total_pages * 100:.1f}%" if total_pages else "N/A"],
                ["has_verse", fmt(total_verse, 0), f"{total_verse / total_pages * 100:.1f}%" if total_pages else "N/A"],
            ],
        ),
        "",
        f"**Books with zero content flags:** {len(zero_flag)} ({len(zero_flag) / len(ok) * 100:.1f}%)"
        if ok
        else "",
    ]
    return "\n".join(lines)


def section_b6(ok: list[Entry]) -> str:
    """B.6: Arabic Text Quality."""
    ratios = [e.get("arabic_ratio", 0.0) for e in ok]

    # Books below 70%
    low_arabic = sorted(
        [e for e in ok if e.get("arabic_ratio", 0.0) < 0.70],
        key=lambda e: e.get("arabic_ratio", 0.0),
    )

    # Diacritic density (per 1000 chars)
    densities = [
        e.get("diacritic_count", 0) / e["total_chars"] * 1000
        for e in ok
        if e.get("total_chars", 0) > 0
    ]
    zero_diacritics = [e for e in ok if e.get("diacritic_count", 0) == 0]

    lines = [
        "## B.6: Arabic Text Quality\n",
        "**Arabic ratio distribution:**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Mean", fmt_pct(safe_mean(ratios))],
                ["Median", fmt_pct(safe_median(ratios))],
                ["P5 (bottom 5%)", fmt_pct(safe_percentile(ratios, 5))],
                ["Min", fmt_pct(min(ratios)) if ratios else "N/A"],
            ],
        ),
        "",
        f"**Books with arabic_ratio < 70%:** {len(low_arabic)} ({len(low_arabic) / len(ok) * 100:.1f}%)\n"
        if ok
        else "",
    ]

    if low_arabic:
        top20_low = low_arabic[:20]
        lines.extend([
            "Top 20 by lowest ratio:\n",
            md_table(
                ["Book", "Arabic ratio"],
                [[e.get("name", "?"), fmt_pct(e.get("arabic_ratio", 0.0))] for e in top20_low],
            ),
            "",
        ])

    lines.extend([
        "**Diacritic density (diacritics per 1,000 chars):**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Mean", fmt(safe_mean(densities))],
                ["Median", fmt(safe_median(densities))],
                ["P95", fmt(safe_percentile(densities, 95))],
            ],
        )
        if densities
        else "No diacritic data available.",
        "",
        f"**Books with zero diacritics:** {len(zero_diacritics)} ({len(zero_diacritics) / len(ok) * 100:.1f}%)"
        if ok
        else "",
    ])
    return "\n".join(lines)


def section_b7(ok: list[Entry]) -> str:
    """B.7: Warning Patterns at Scale."""
    agg_warns: Counter[str] = Counter()
    per_book_warns: list[tuple[str, int]] = []
    for e in ok:
        book_total = e.get("validation_warnings", 0)
        per_book_warns.append((e.get("name", "?"), book_total))
        for cat, count in e.get("warn_categories", {}).items():
            agg_warns[cat] += count

    total_warnings = sum(agg_warns.values())
    top10 = sorted(per_book_warns, key=lambda x: x[1], reverse=True)[:10]

    lines = [
        "## B.7: Warning Patterns at Scale\n",
        f"**Total warnings across corpus:** {fmt(total_warnings, 0)}\n",
        "**Warning type distribution:**\n",
        md_table(
            ["Warning type", "Count", "Percentage"],
            [
                [cat, fmt(count, 0), f"{count / total_warnings * 100:.1f}%" if total_warnings else "N/A"]
                for cat, count in agg_warns.most_common()
            ],
        )
        if agg_warns
        else "No warnings recorded.",
        "",
        "**Top 10 most-warned books:**\n",
        md_table(
            ["Book", "Warning count"],
            [[name, fmt(count, 0)] for name, count in top10],
        )
        if top10
        else "No warnings.",
    ]
    return "\n".join(lines)


def section_b8(ok: list[Entry]) -> str:
    """B.8: Passaging Contract Alignment."""
    check4_fail = [
        e
        for e in ok
        if not e.get("psg_contract_checks", {}).get("check4_count_match", True)
    ]
    check5_ordered_fail = [
        e
        for e in ok
        if not e.get("psg_contract_checks", {}).get("check5_ordered", True)
    ]
    check5_gaps_fail = [
        e
        for e in ok
        if not e.get("psg_contract_checks", {}).get("check5_no_gaps", True)
    ]
    check5_fail = list({e["name"]: e for e in check5_ordered_fail + check5_gaps_fail}.values())
    check6_fail = [
        e
        for e in ok
        if not e.get("psg_contract_checks", {}).get("check6_division_consistent", True)
    ]
    all_pass = [
        e
        for e in ok
        if all(e.get("psg_contract_checks", {}).values())
    ]

    lines = [
        "## B.8: Passaging Contract Alignment\n",
        md_table(
            ["Check", "Failures", "Percentage"],
            [
                ["check4_count_match", fmt(len(check4_fail), 0), f"{len(check4_fail) / len(ok) * 100:.1f}%" if ok else "N/A"],
                ["check5 (ordered + no_gaps)", fmt(len(check5_fail), 0), f"{len(check5_fail) / len(ok) * 100:.1f}%" if ok else "N/A"],
                ["check6_division_consistent", fmt(len(check6_fail), 0), f"{len(check6_fail) / len(ok) * 100:.1f}%" if ok else "N/A"],
            ],
        ),
        "",
        f"**Books passing ALL checks:** {len(all_pass)} ({len(all_pass) / len(ok) * 100:.1f}%)\n"
        if ok
        else "",
    ]

    # List check4 and check5 failures by name (potential engine bugs)
    if check4_fail:
        lines.append(f"**check4_count_match failures (potential engine bug) — {len(check4_fail)} books:**\n")
        for e in sorted(check4_fail, key=lambda x: x.get("name", "")):
            lines.append(f"- {e.get('name', '?')}")
        lines.append("")

    if check5_fail:
        lines.append(f"**check5 failures (potential engine bug) — {len(check5_fail)} books:**\n")
        for e in sorted(check5_fail, key=lambda x: x.get("name", "")):
            lines.append(f"- {e.get('name', '?')}")
        lines.append("")

    return "\n".join(lines)


def section_b9(ok: list[Entry]) -> str:
    """B.9: Page Loss."""
    losses = [e.get("page_loss", -1) for e in ok if e.get("page_loss", -1) >= 0]
    high_loss = sorted(
        [(e.get("name", "?"), e.get("page_loss", 0)) for e in ok if e.get("page_loss", 0) > 5],
        key=lambda x: x[1],
        reverse=True,
    )
    zero_loss = [e for e in ok if e.get("page_loss", -1) == 0]
    near_perfect = [e for e in ok if e.get("page_loss", -1) in (0, 1)]

    lines = [
        "## B.9: Page Loss\n",
        "> Note: `page_loss = abs(content_units - raw_page_divs)`. A value of 1 typically",
        "> represents the Shamela table-of-contents page (expected, not data loss).\n",
        "**Page loss distribution:**\n",
        md_table(
            ["Metric", "Value"],
            [
                ["Mean", fmt(safe_mean(losses))],
                ["Median", fmt(safe_median(losses))],
                ["P95", fmt(safe_percentile(losses, 95))],
                ["Max", fmt(max(losses)) if losses else "N/A"],
            ],
        ),
        "",
        f"**Books with page_loss == 0:** {len(zero_loss)} ({len(zero_loss) / len(ok) * 100:.1f}%)\n"
        if ok
        else "",
        f"**Books with page_loss <= 1 (near-perfect):** {len(near_perfect)} ({len(near_perfect) / len(ok) * 100:.1f}%)\n"
        if ok
        else "",
    ]

    if high_loss:
        lines.extend([
            f"**Books with page_loss > 5:** {len(high_loss)}\n",
            md_table(
                ["Book", "Page loss"],
                [[name, fmt(loss, 0)] for name, loss in high_loss],
            ),
        ])

    return "\n".join(lines)


# -- Report Assembly --


def assemble_report(
    ok: list[Entry],
    crashes: list[Entry],
    all_entries: list[Entry],
    input_path: Path,
) -> str:
    """Assemble the full calibration report."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    header = f"""# Normalization Calibration Report

**Generated:** {now}
**Input:** `{input_path}`
**Total entries:** {len(all_entries)}
**OK books:** {len(ok)} | **Crashes:** {len(crashes)}

---
"""

    sections = [
        section_b1(ok, crashes, all_entries),
        section_b2(ok),
        section_b3(ok),
        section_b4(ok),
        section_b5(ok),
        section_b6(ok),
        section_b7(ok),
        section_b8(ok),
        section_b9(ok),
    ]

    return header + "\n\n".join(sections) + "\n"


# -- CLI --


def main() -> None:
    """Entry point."""
    parser = argparse.ArgumentParser(
        description="Analyze normalization sweep results and produce calibration report"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Path to corpus_sweep.jsonl",
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Path to output CALIBRATION_REPORT.md",
    )
    args = parser.parse_args()

    input_path = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"ERROR: Input file not found: {input_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Loading {input_path}...")
    entries = load_jsonl(input_path)
    if not entries:
        output_path.write_text(
            "# Normalization Calibration Report\n\nNo data to analyze.\n",
            encoding="utf-8",
        )
        print("WARNING: No entries found. Empty report written.")
        return

    ok, crashes = partition(entries)
    print(f"  {len(entries)} entries: {len(ok)} OK, {len(crashes)} CRASH")

    print("Generating report...")
    report = assemble_report(ok, crashes, entries, input_path)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report, encoding="utf-8")
    print(f"Report written to {output_path}")


if __name__ == "__main__":
    main()
