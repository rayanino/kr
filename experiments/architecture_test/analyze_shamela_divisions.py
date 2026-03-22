"""Shamela Division Size Analysis — scan full collection for architecture decision.

Analyzes division sizes across 20K+ Shamela .htm exports to determine
whether a separate passaging engine is needed for the KR pipeline.
Measures Arabic word counts between heading spans to build collection-wide
distribution statistics.

Output:
  - SHAMELA_DIVISION_ANALYSIS.md: human-readable summary
  - shamela_division_data.json: raw per-book data
"""
from __future__ import annotations

import html as html_mod
import json
import re
import statistics
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# --- Constants ---

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
SHAMELA_DIR = PROJECT_ROOT / "shamela-export-samples"
OUTPUT_DIR = Path(__file__).resolve().parent

# Regex patterns for Shamela HTML structure
PAGE_TEXT_SPLIT = re.compile(r"""<div\s+class=['"]PageText['"]>""", re.IGNORECASE)
TITLE_SPAN_RE = re.compile(
    r"""<span\s+class=['"]title['"]>(.*?)</span>""",
    re.IGNORECASE | re.DOTALL,
)
FOOTNOTE_RE = re.compile(
    r"""<div\s+class=['"]footnote['"]>.*?</div>""",
    re.IGNORECASE | re.DOTALL,
)
PAGEHEAD_RE = re.compile(
    r"""<div\s+class=['"]PageHead['"]>.*?</div>""",
    re.IGNORECASE | re.DOTALL,
)
HTML_TAG_RE = re.compile(r"<[^>]+>")

METADATA_KEYWORDS = [
    "الكتاب",
    "المؤلف",
    "الناشر",
    "الطبعة",
    "عدد الصفحات",
    "القسم",
    "تاريخ النشر بالشاملة",
]

BUCKET_NAMES = ["<50w", "50-299w", "300-800w", "801-2000w", "2001-5000w", ">5000w"]


# --- Utility Functions ---


def read_file(path: Path) -> tuple[str, str]:
    """Read file with encoding fallback. Returns (content, encoding_used)."""
    for enc in ["utf-8", "cp1256"]:
        try:
            return path.read_text(encoding=enc), enc
        except (UnicodeDecodeError, ValueError):
            continue
    return path.read_text(encoding="utf-8", errors="replace"), "utf-8-replace"


def clean_heading(raw: str) -> str:
    """Strip HTML tags, unescape entities, remove ZWNJ."""
    text = HTML_TAG_RE.sub("", raw)
    text = html_mod.unescape(text)
    text = text.replace("\u200c", "")  # ZWNJ
    return text.strip()


def count_arabic_words(text: str) -> int:
    """Count whitespace-separated tokens containing at least one Arabic char."""
    return sum(1 for w in text.split() if any("\u0600" <= c <= "\u06FF" for c in w))


def classify_bucket(wc: int) -> str:
    """Classify a word count into a distribution bucket."""
    if wc < 50:
        return "<50w"
    if wc < 300:
        return "50-299w"
    if wc <= 800:
        return "300-800w"
    if wc <= 2000:
        return "801-2000w"
    if wc <= 5000:
        return "2001-5000w"
    return ">5000w"


# --- Core Analysis ---


def analyze_book(path: Path) -> dict[str, Any] | None:
    """Analyze one Shamela .htm file for division sizes.

    Returns None if the book has fewer than 5 content headings.
    Returns dict with 'error' key if parsing fails.
    """
    try:
        content, encoding = read_file(path)
    except Exception as e:
        return {"error": str(e), "filename": path.name}

    # Split on PageText div boundaries
    pages = PAGE_TEXT_SPLIT.split(content)
    if len(pages) < 3:
        # Need: pre-HTML (0) + metadata page (1) + at least 1 content page (2+)
        return None

    page_count = len(pages) - 1

    # Build content stream: skip pre-HTML (0) and metadata page (1)
    parts: list[str] = []
    for p in pages[2:]:
        p = PAGEHEAD_RE.sub("", p)
        p = FOOTNOTE_RE.sub("", p)
        parts.append(p)
    stream = " ".join(parts)

    # Find content headings (filter out metadata fields and book titles)
    headings: list[tuple[int, int, str]] = []  # (match_start, match_end, cleaned)
    for m in TITLE_SPAN_RE.finditer(stream):
        raw = m.group(1)
        # Book title spans have trailing &nbsp;
        if "&nbsp;" in raw:
            continue
        cleaned = clean_heading(raw)
        if len(cleaned) < 3:
            continue
        if any(kw in cleaned for kw in METADATA_KEYWORDS):
            continue
        headings.append((m.start(), m.end(), cleaned))

    if len(headings) < 5:
        return None

    # Extract divisions: text between consecutive heading spans
    divisions: list[dict[str, Any]] = []
    for i, (_, h_end, heading) in enumerate(headings):
        text_end = headings[i + 1][0] if i + 1 < len(headings) else len(stream)
        div_text = HTML_TAG_RE.sub("", stream[h_end:text_end])
        div_text = html_mod.unescape(div_text)
        wc = count_arabic_words(div_text)
        divisions.append({"heading": heading, "word_count": wc})

    if not divisions:
        return None

    wcs = [d["word_count"] for d in divisions]
    buckets: dict[str, int] = {b: 0 for b in BUCKET_NAMES}
    for wc in wcs:
        buckets[classify_bucket(wc)] += 1

    return {
        "filename": path.name,
        "file_size_bytes": path.stat().st_size,
        "page_count": page_count,
        "heading_count": len(headings),
        "division_count": len(divisions),
        "total_arabic_words": sum(wcs),
        "division_min_words": min(wcs),
        "division_max_words": max(wcs),
        "division_median_words": statistics.median(wcs),
        "division_mean_words": round(statistics.mean(wcs), 1),
        "buckets": buckets,
        "encoding": encoding,
        "divisions": divisions,
    }


# --- Collection Statistics ---


def compute_collection_stats(results: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute collection-wide aggregate statistics."""
    agg: dict[str, int] = {b: 0 for b in BUCKET_NAMES}
    all_wcs: list[int] = []
    oversized: list[dict[str, Any]] = []

    for r in results:
        for b in BUCKET_NAMES:
            agg[b] += r["buckets"][b]
        for d in r["divisions"]:
            all_wcs.append(d["word_count"])
            if d["word_count"] > 5000:
                oversized.append({
                    "book": r["filename"],
                    "heading": d["heading"][:100],
                    "word_count": d["word_count"],
                })

    oversized.sort(key=lambda x: x["word_count"], reverse=True)
    n = len(all_wcs) or 1

    return {
        "total_divisions": sum(r["division_count"] for r in results),
        "agg_buckets": agg,
        "pct_no_split_2000w": round(
            sum(1 for w in all_wcs if w <= 2000) / n * 100, 2
        ),
        "pct_no_split_5000w": round(
            sum(1 for w in all_wcs if w <= 5000) / n * 100, 2
        ),
        "oversized_divisions": oversized,
        "median_words": statistics.median(all_wcs) if all_wcs else 0,
        "mean_words": round(statistics.mean(all_wcs), 1) if all_wcs else 0,
    }


# --- Output ---


def write_report(
    stats: dict[str, Any],
    results: list[dict[str, Any]],
    total_scanned: int,
    skipped: int,
    error_count: int,
    path: Path,
) -> None:
    """Write the human-readable markdown analysis report."""
    now = datetime.now().strftime("%Y-%m-%d %H:%M")
    top20 = sorted(results, key=lambda r: r["file_size_bytes"], reverse=True)[:20]
    td = stats["total_divisions"]

    lines: list[str] = []
    w = lines.append

    w(f"# Shamela Division Size Analysis — {now}\n")

    # --- Collection Summary ---
    w("## Collection Summary\n")
    w(f"- **Total .htm files scanned:** {total_scanned:,}")
    w(f"- **Books with ≥5 headings (analyzed):** {len(results):,}")
    w(f"- **Books skipped (<5 headings):** {skipped:,}")
    w(f"- **Parse errors:** {error_count}")
    w(f"- **Total divisions:** {td:,}")
    w(f"- **Median division size:** {stats['median_words']:.0f} words")
    w(f"- **Mean division size:** {stats['mean_words']:.1f} words\n")

    # --- Distribution ---
    w("## Division Size Distribution (all books with ≥5 headings)\n")
    w("| Bucket | Count | % |")
    w("|--------|------:|----:|")
    for b in BUCKET_NAMES:
        c = stats["agg_buckets"][b]
        pct = c / td * 100 if td else 0
        w(f"| {b} | {c:,} | {pct:.1f}% |")

    w(
        f"\n- **% needing no split at 2000w ceiling:** "
        f"{stats['pct_no_split_2000w']:.1f}%"
    )
    w(
        f"- **% needing no split at 5000w ceiling:** "
        f"{stats['pct_no_split_5000w']:.1f}%\n"
    )

    # --- Top 20 ---
    w("## Top 20 Largest Books\n")
    w(
        "| # | Filename | MB | Pages | Hdgs | Divs "
        "| Min | Med | Max | >2Kw | >5Kw |"
    )
    w("|---|----------|---:|------:|-----:|-----:|----:|----:|----:|-----:|-----:|")
    for i, r in enumerate(top20, 1):
        mb = r["file_size_bytes"] / 1048576
        gt2k = r["buckets"]["2001-5000w"] + r["buckets"][">5000w"]
        gt5k = r["buckets"][">5000w"]
        fn = r["filename"][:45]
        w(
            f"| {i} | {fn} | {mb:.1f} | {r['page_count']:,} | "
            f"{r['heading_count']:,} | {r['division_count']:,} | "
            f"{r['division_min_words']} | {r['division_median_words']:.0f} | "
            f"{r['division_max_words']:,} | {gt2k} | {gt5k} |"
        )

    w("\n### Largest Division per Top-20 Book\n")
    for i, r in enumerate(top20, 1):
        big = max(r["divisions"], key=lambda d: d["word_count"])
        w(
            f"{i}. **{r['filename'][:55]}** — "
            f"{big['word_count']:,}w: {big['heading'][:80]}\n"
        )

    # --- Oversized ---
    w("## Oversized Divisions (>5000w)\n")
    ov = stats["oversized_divisions"]
    if ov:
        w(f"Total: {len(ov)} divisions\n")
        w("| Book | Heading | Words |")
        w("|------|---------|------:|")
        for o in ov[:100]:
            w(f"| {o['book'][:40]} | {o['heading'][:60]} | {o['word_count']:,} |")
        if len(ov) > 100:
            w(f"\n... and {len(ov) - 100} more (see JSON data).")
    else:
        w("None found.")

    # --- Observations ---
    w("\n## Format Observations\n")
    p2 = stats["pct_no_split_2000w"]
    p5 = stats["pct_no_split_5000w"]
    if p2 > 90:
        w(
            f"- **Strong support for 2000w ceiling:** "
            f"{p2:.1f}% of divisions fit without splitting."
        )
    elif p2 > 75:
        w(
            f"- **Moderate support for 2000w ceiling:** "
            f"{p2:.1f}% fit; {100 - p2:.1f}% need splitting."
        )
    else:
        w(f"- **Weak support for 2000w ceiling:** Only {p2:.1f}% fit.")

    if p5 > 95:
        w(
            f"- **5000w ceiling covers nearly all:** "
            f"{p5:.1f}% need no splitting."
        )

    extreme = [r for r in results if r["division_max_words"] > 10000]
    if extreme:
        w(f"- **Extreme divisions (>10Kw):** Found in {len(extreme)} books.")

    tiny = [r for r in results if r["division_median_words"] < 30]
    if tiny:
        w(
            f"- **Very small divisions (median <30w):** "
            f"Found in {len(tiny)} books — likely verse/hadith collections."
        )

    # Books where ALL divisions fit under 2000w
    all_fit = sum(1 for r in results if r["division_max_words"] <= 2000)
    n_results = len(results) or 1
    w(
        f"- **Books with ALL divisions \u22642000w:** "
        f"{all_fit:,}/{len(results):,} ({all_fit / n_results * 100:.1f}%)"
    )

    w("\n---\n*Generated by `analyze_shamela_divisions.py`*")

    path.write_text("\n".join(lines), encoding="utf-8")


def write_json(results: list[dict[str, Any]], path: Path) -> None:
    """Write compact JSON — word count lists instead of full division objects."""
    compact: list[dict[str, Any]] = []
    for r in results:
        entry = {k: v for k, v in r.items() if k != "divisions"}
        entry["division_word_counts"] = [d["word_count"] for d in r["divisions"]]
        # Keep top 5 largest division headings for reference
        top_divs = sorted(
            r["divisions"], key=lambda d: d["word_count"], reverse=True
        )[:5]
        entry["largest_divisions"] = [
            {"heading": d["heading"][:100], "word_count": d["word_count"]}
            for d in top_divs
        ]
        compact.append(entry)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(compact, f, ensure_ascii=False, indent=1)


# --- Main ---


def main() -> None:
    if not SHAMELA_DIR.exists():
        print(f"ERROR: {SHAMELA_DIR} not found")
        sys.exit(1)

    print(f"Scanning {SHAMELA_DIR} ...")
    htm_files = sorted(SHAMELA_DIR.rglob("*.htm"))
    total = len(htm_files)
    print(f"Found {total:,} .htm files\n")

    results: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    skipped = 0
    t0 = time.time()

    for i, path in enumerate(htm_files):
        if (i + 1) % 500 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            eta = (total - i - 1) / rate
            print(f"  {i + 1:,}/{total:,} ({rate:.0f}/s, ETA {eta:.0f}s)")

        r = analyze_book(path)
        if r is None:
            skipped += 1
        elif "error" in r:
            errors.append(r)
        else:
            results.append(r)

    elapsed = time.time() - t0
    print(f"\nDone in {elapsed:.1f}s ({total / elapsed:.0f}/s)")
    print(f"  Analyzed: {len(results):,}")
    print(f"  Skipped: {skipped:,}")
    print(f"  Errors: {len(errors)}")

    if not results:
        print("ERROR: No books analyzed. Check shamela-export-samples/ content.")
        sys.exit(1)

    stats = compute_collection_stats(results)

    # Summary to stdout
    td = stats["total_divisions"]
    print(f"\n{'=' * 50}")
    print(f"DIVISIONS: {td:,}")
    print(f"{'=' * 50}")
    for b in BUCKET_NAMES:
        c = stats["agg_buckets"][b]
        pct = c / td * 100 if td else 0
        print(f"  {b:>10}: {c:>7,} ({pct:5.1f}%)")
    print(f"\n  \u22642000w: {stats['pct_no_split_2000w']:.1f}%")
    print(f"  \u22645000w: {stats['pct_no_split_5000w']:.1f}%")
    print(f"  >5000w: {len(stats['oversized_divisions']):,}")

    # Write outputs
    json_path = OUTPUT_DIR / "shamela_division_data.json"
    write_json(results, json_path)
    print(f"\nJSON: {json_path}")

    md_path = OUTPUT_DIR / "SHAMELA_DIVISION_ANALYSIS.md"
    write_report(stats, results, total, skipped, len(errors), md_path)
    print(f"Report: {md_path}")


if __name__ == "__main__":
    main()
