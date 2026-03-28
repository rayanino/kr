"""Empirical back-reference pattern scanner for Defense 1A evaluation.

Scans all HTM fixture files for Arabic back-reference, forward-reference,
and cross-reference patterns. Produces data needed to decide whether to
build the dangling reference detector (Defense 1A).

Zero LLM cost — pure string counting against local fixture data.

Usage:
  python scripts/empirical_backrefs.py --output overnight/results/empirical-backrefs/scan.json
  python scripts/empirical_backrefs.py --dry-run
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent

# ---------------------------------------------------------------------------
# Arabic back-reference patterns from llm_trustworthiness_defenses.md §1A
# ---------------------------------------------------------------------------

PATTERNS: dict[str, dict[str, str]] = {
    # Back-references (text depends on prior context)
    "كما تقدم": {"type": "back_reference", "meaning": "as previously mentioned"},
    "كما سبق": {"type": "back_reference", "meaning": "as preceded"},
    "تقدم أن": {"type": "back_reference", "meaning": "it preceded that"},
    "ما تقدم": {"type": "back_reference", "meaning": "what preceded"},
    "كما مر": {"type": "back_reference", "meaning": "as passed"},
    "المذكور آنفاً": {"type": "back_reference", "meaning": "the aforementioned"},
    "ما سبق ذكره": {"type": "back_reference", "meaning": "what was previously mentioned"},
    "تقدم ذكره": {"type": "back_reference", "meaning": "its mention preceded"},
    # Forward-references
    "سيأتي": {"type": "forward_reference", "meaning": "will come later"},
    "كما سيأتي": {"type": "forward_reference", "meaning": "as will come"},
    "يأتي بيانه": {"type": "forward_reference", "meaning": "its explanation will come"},
    "سيأتي تفصيله": {"type": "forward_reference", "meaning": "its detail will come"},
    # Cross-references
    "انظر": {"type": "cross_reference", "meaning": "see/refer to"},
    "راجع": {"type": "cross_reference", "meaning": "refer back to"},
    "ارجع إلى": {"type": "cross_reference", "meaning": "return to"},
    # Section-references
    "في الباب السابق": {"type": "section_reference", "meaning": "in the previous chapter"},
    "في الفصل الآتي": {"type": "section_reference", "meaning": "in the coming section"},
}


# ---------------------------------------------------------------------------
# HTML text extraction (stdlib only, no BeautifulSoup dependency)
# ---------------------------------------------------------------------------


class _TextExtractor(HTMLParser):
    """Extract visible text from HTML, stripping tags."""

    def __init__(self) -> None:
        super().__init__()
        self._chunks: list[str] = []

    def handle_data(self, data: str) -> None:
        self._chunks.append(data)

    def get_text(self) -> str:
        return "".join(self._chunks)


def extract_text_from_htm(path: Path) -> str:
    """Read an HTM file and return its visible text content."""
    raw = path.read_text(encoding="utf-8", errors="replace")
    extractor = _TextExtractor()
    extractor.feed(raw)
    return extractor.get_text()


# ---------------------------------------------------------------------------
# Pattern counting
# ---------------------------------------------------------------------------


def count_patterns(text: str) -> dict[str, int]:
    """Count occurrences of each back-reference pattern in text."""
    return {pattern: text.count(pattern) for pattern in PATTERNS}


# ---------------------------------------------------------------------------
# File discovery
# ---------------------------------------------------------------------------


def discover_htm_files() -> list[Path]:
    """Find all HTM fixture files in the project."""
    search_dirs = [
        PROJECT_DIR / "tests" / "fixtures",
        PROJECT_DIR / "experiments" / "format_diversity_test" / "fixtures",
    ]
    files: list[Path] = []
    for d in search_dirs:
        if d.exists():
            files.extend(sorted(d.rglob("*.htm")))
    return files


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------


def generate_report(
    files: list[Path],
    all_counts: list[dict[str, int]],
    all_texts: list[str],
) -> dict:
    """Produce the structured scan report with decision recommendation."""
    total_chars = sum(len(t) for t in all_texts)
    chars_per_million = total_chars / 1_000_000 if total_chars > 0 else 1.0

    pattern_stats: dict[str, dict] = {}
    for pattern in PATTERNS:
        total_hits = sum(c[pattern] for c in all_counts)
        files_with_hits = sum(1 for c in all_counts if c[pattern] > 0)
        hit_rate = total_hits / chars_per_million if chars_per_million > 0 else 0
        pattern_stats[pattern] = {
            "type": PATTERNS[pattern]["type"],
            "meaning": PATTERNS[pattern]["meaning"],
            "total_hits": total_hits,
            "files_with_hits": files_with_hits,
            "hit_rate_per_million_chars": round(hit_rate, 2),
        }

    # Per-file summary (top 20 by hit count)
    per_file: list[dict] = []
    for i, (f, counts, text) in enumerate(zip(files, all_counts, all_texts)):
        total = sum(counts.values())
        if total > 0:
            patterns_found = [p for p, c in counts.items() if c > 0]
            per_file.append({
                "file": str(f.relative_to(PROJECT_DIR)),
                "total_hits": total,
                "chars": len(text),
                "patterns_found": patterns_found,
            })
    per_file.sort(key=lambda x: x["total_hits"], reverse=True)

    # Decision: PROCEED if any pattern has substantial presence
    # Threshold: > 1 hit/M chars AND present in 10+ files
    proceed_patterns = [
        p for p, s in pattern_stats.items()
        if s["hit_rate_per_million_chars"] > 1.0 and s["files_with_hits"] >= 10
    ]
    decision = "PROCEED" if proceed_patterns else "SKIP"

    # Type-level aggregation
    by_type: dict[str, dict[str, int]] = {}
    for pattern, stats in pattern_stats.items():
        ptype = stats["type"]
        if ptype not in by_type:
            by_type[ptype] = {"total_hits": 0, "patterns": 0}
        by_type[ptype]["total_hits"] += stats["total_hits"]
        by_type[ptype]["patterns"] += 1

    return {
        "scan_date": datetime.now(timezone.utc).isoformat(),
        "files_scanned": len(files),
        "total_chars": total_chars,
        "total_chars_millions": round(chars_per_million, 2),
        "decision": decision,
        "proceed_patterns": proceed_patterns,
        "by_type": by_type,
        "patterns": pattern_stats,
        "per_file_top20": per_file[:20],
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Scan HTM fixtures for Arabic back-reference patterns (Defense 1A)",
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output path for JSON report",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print summary without writing output file",
    )
    args = parser.parse_args()

    print("Discovering HTM fixture files...")
    files = discover_htm_files()
    if not files:
        print("ERROR: No HTM files found in tests/fixtures/ or experiments/")
        sys.exit(1)
    print(f"  Found {len(files)} HTM files")

    print("Extracting text and counting patterns...")
    all_texts: list[str] = []
    all_counts: list[dict[str, int]] = []
    for f in files:
        text = extract_text_from_htm(f)
        counts = count_patterns(text)
        all_texts.append(text)
        all_counts.append(counts)

    total_chars = sum(len(t) for t in all_texts)
    print(f"  Total text: {total_chars:,} chars ({total_chars / 1_000_000:.1f}M)")

    report = generate_report(files, all_counts, all_texts)

    # Print summary
    print(f"\n=== Pattern Summary ===")
    print(f"Decision: {report['decision']}")
    print(f"\nBy type:")
    for ptype, stats in report["by_type"].items():
        print(f"  {ptype}: {stats['total_hits']} total hits across {stats['patterns']} patterns")
    print(f"\nTop patterns:")
    sorted_patterns = sorted(
        report["patterns"].items(),
        key=lambda x: x[1]["total_hits"],
        reverse=True,
    )
    for pattern, stats in sorted_patterns[:10]:
        if stats["total_hits"] > 0:
            line = (
                f"  {pattern} ({stats['meaning']}): "
                f"{stats['total_hits']} hits in {stats['files_with_hits']} files "
                f"({stats['hit_rate_per_million_chars']}/M chars)"
            )
            try:
                print(line)
            except UnicodeEncodeError:
                # Windows console may not support Arabic — fall back to ASCII-safe
                print(
                    f"  [{stats['meaning']}]: "
                    f"{stats['total_hits']} hits in {stats['files_with_hits']} files "
                    f"({stats['hit_rate_per_million_chars']}/M chars)"
                )

    if args.dry_run:
        print("\n[dry-run] No output file written.")
        return

    if args.output:
        output_path = Path(args.output)
    else:
        output_path = PROJECT_DIR / "overnight" / "results" / "empirical-backrefs" / "scan.json"

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(report, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    print(f"\nReport written to {output_path}")


if __name__ == "__main__":
    main()
