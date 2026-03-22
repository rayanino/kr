"""Deliverable 2: Extract high-quality divisions for LLM testing.

Loads normalized packages from D1, selects divisions per fixture with
format-specific criteria, and writes JSON + readable MD files.

Key differences from architecture_test version:
  - Per-fixture word ranges and target counts
  - L-003 relaxation for ibn_aqil (strict → moderate if >80% rejected)
  - Verse-commentary detection for ibn_aqil
  - 200-word context windows (not 3 units)
  - masala/QA marker detection for optional fixtures
  - EXTRACTION_REPORT.md generation
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

PACKAGES_DIR = Path(__file__).resolve().parent / "packages"
DIVISIONS_DIR = Path(__file__).resolve().parent / "divisions"
REPORT_PATH = Path(__file__).resolve().parent / "EXTRACTION_REPORT.md"

# Non-scholarly heading keywords to exclude
EXCLUDE_KEYWORDS = ["مصادر", "مراجع", "فهرس", "ثبت المصادر", "المراجع"]

# BoundaryContinuityType → join separator mapping
BC_JOIN_MAP: dict[Optional[str], str] = {
    "mid_sentence": "",
    "mid_paragraph": "\n",
    "mid_argument": "\n",
    "section_break": "\n\n",
    "division_break": "\n\n",
    "unknown": "\n",
    None: "\n",
}

# Per-fixture configuration
FIXTURE_CONFIG: dict[str, dict[str, Any]] = {
    "ibn_aqil_v1": {
        "min_words": 300,
        "max_words": 2000,
        "target_count": 3,
        "require_verse": True,
        "priority": "PRIMARY",
    },
    "ibn_aqil_v3": {
        "min_words": 300,
        "max_words": 2000,
        "target_count": 3,
        "require_verse": True,
        "priority": "PRIMARY",
    },
    "taysir": {
        "min_words": 2000,
        "max_words": 4000,
        "target_count": 4,
        "require_verse": False,
        "priority": "PRIMARY",
    },
    "ext_39_masala": {
        "min_words": 300,
        "max_words": 2000,
        "target_count": 2,
        "require_verse": False,
        "require_masala": 2,
        "priority": "OPTIONAL",
    },
    "ext_46_qa": {
        "min_words": 300,
        "max_words": 2000,
        "target_count": 2,
        "require_verse": False,
        "require_qa": 2,
        "priority": "OPTIONAL",
    },
}

# Verse-commentary detection markers
VERSE_MARKERS = [
    "قال ابن مالك",
    "ومنه قوله",
    "قال المصنف",
    "وقوله",
    "قوله",
    "وشاهده",
    "البيت",
]


# ──────────────────────────────────────────────────────────────────
# Utility functions (reused from architecture_test)
# ──────────────────────────────────────────────────────────────────


def strip_arabic_noise(text: str) -> str:
    """Strip ZWNJ, ZWJ, diacritics, tatweel for comparison."""
    text = text.replace("\u200c", "").replace("\u200d", "")
    text = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def arabic_word_count(text: str) -> int:
    """Count words containing at least one Arabic character."""
    return len([w for w in text.split() if any("\u0600" <= c <= "\u06FF" for c in w)])


def get_bc_type(cu: dict[str, Any]) -> Optional[str]:
    """Get boundary_continuity.type from a content unit dict, or None."""
    bc = cu.get("boundary_continuity")
    if bc is None:
        return None
    return bc.get("type")


def get_bc_separator(cu: dict[str, Any]) -> str:
    """Get the join separator for this content unit based on its boundary_continuity."""
    return BC_JOIN_MAP.get(get_bc_type(cu), "\n")


def load_package(fixture_name: str) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load manifest and content units for a fixture."""
    pkg_dir = PACKAGES_DIR / fixture_name

    with open(pkg_dir / "manifest.json", "r", encoding="utf-8") as f:
        manifest = json.load(f)

    content_units: list[dict[str, Any]] = []
    with open(pkg_dir / "content.jsonl", "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                content_units.append(json.loads(line))

    content_units.sort(key=lambda cu: cu["unit_index"])
    return manifest, content_units


def find_leaf_divisions(
    nodes: list[dict[str, Any]], path: Optional[list[str]] = None
) -> list[dict[str, Any]]:
    """Walk division tree and return leaf divisions with heading_path attached."""
    if path is None:
        path = []

    leaves: list[dict[str, Any]] = []
    for node in nodes:
        current_path = path + [node["heading_text"]]
        if not node.get("children", []):
            node_copy = dict(node)
            node_copy["heading_path"] = current_path
            leaves.append(node_copy)
        else:
            leaves.extend(find_leaf_divisions(node["children"], current_path))
    return leaves


def assemble_text(
    content_units: list[dict[str, Any]],
    start_idx: int,
    end_idx: int,
) -> tuple[str, list[tuple[int, str]]]:
    """Assemble text from content units in [start_idx, end_idx] (inclusive)."""
    parts: list[str] = []
    offsets: list[tuple[int, str]] = []
    cumulative = 0

    for i, cu in enumerate(content_units):
        idx = cu["unit_index"]
        if idx < start_idx or idx > end_idx:
            continue

        if parts:
            prev_cu = content_units[i - 1] if i > 0 else cu
            sep = get_bc_separator(prev_cu)
            parts.append(sep)
            cumulative += len(sep)

        offsets.append((cumulative, ""))
        text = cu.get("primary_text", "")
        parts.append(text)
        cumulative += len(text)

    return "".join(parts), offsets


def rebase_text_layers(
    content_units: list[dict[str, Any]],
    start_idx: int,
    end_idx: int,
    char_offsets: list[tuple[int, str]],
) -> list[dict[str, Any]]:
    """Rebase text_layers from per-unit offsets to assembled-text offsets."""
    rebased: list[dict[str, Any]] = []
    offset_idx = 0

    for cu in content_units:
        idx = cu["unit_index"]
        if idx < start_idx or idx > end_idx:
            continue
        if offset_idx >= len(char_offsets):
            break

        base_offset = char_offsets[offset_idx][0]
        for layer in cu.get("text_layers", []):
            rebased.append({
                "layer_type": layer.get("layer_type"),
                "author_canonical_id": layer.get("author_canonical_id"),
                "start_char": layer.get("start", 0) + base_offset,
                "end_char": layer.get("end", 0) + base_offset,
                "confidence": layer.get("confidence"),
            })
        offset_idx += 1

    return rebased


def aggregate_content_flags(
    content_units: list[dict[str, Any]],
    start_idx: int,
    end_idx: int,
) -> dict[str, bool]:
    """OR-aggregate content_flags across all constituent units."""
    agg: dict[str, bool] = {
        "has_verse": False,
        "has_table": False,
        "has_quran_citation": False,
        "has_hadith_citation": False,
        "is_toc_page": False,
        "is_index_page": False,
        "is_blank": False,
    }
    for cu in content_units:
        idx = cu["unit_index"]
        if idx < start_idx or idx > end_idx:
            continue
        flags = cu.get("content_flags", {})
        for key in agg:
            if flags.get(key, False):
                agg[key] = True
    return agg


def has_multi_layer_units(
    content_units: list[dict[str, Any]],
    start_idx: int,
    end_idx: int,
) -> bool:
    """Check if any content unit in range has >1 text layers."""
    for cu in content_units:
        idx = cu["unit_index"]
        if idx < start_idx or idx > end_idx:
            continue
        if len(cu.get("text_layers", [])) > 1:
            return True
    return False


# ──────────────────────────────────────────────────────────────────
# New functions for format diversity
# ──────────────────────────────────────────────────────────────────


def has_verse_commentary(text: str) -> bool:
    """Detect verse-commentary interleaving in text.

    Looks for:
    1. Short lines (<=20 Arabic words) surrounded by longer prose paragraphs
    2. Verse quotation markers (قال ابن مالك, ومنه قوله, etc.)
    """
    # Check for verse markers
    for marker in VERSE_MARKERS:
        if marker in text:
            return True

    # Check for short-line pattern: lines with <=20 Arabic words
    # surrounded by longer lines (>=30 words)
    lines = text.split("\n")
    short_lines = 0
    long_lines = 0
    for line in lines:
        wc = arabic_word_count(line.strip())
        if 3 <= wc <= 20:
            short_lines += 1
        elif wc >= 30:
            long_lines += 1

    # Verse-commentary pattern: mix of short verse lines and long commentary
    return short_lines >= 2 and long_lines >= 1


def has_masala_markers(text: str, min_count: int = 2) -> bool:
    """Check for masala (مسألة) markers in text."""
    count = text.count("مسألة")
    return count >= min_count


def has_qa_markers(text: str, min_count: int = 2) -> bool:
    """Check for QA markers (سؤال/فأجاب/سُئل) in text."""
    count = 0
    for marker in ["سؤال", "فأجاب", "سُئل", "سئل"]:
        count += text.count(marker)
    return count >= min_count


def extract_word_context(
    content_units: list[dict[str, Any]],
    boundary_idx: int,
    direction: str,
    word_limit: int = 200,
) -> str:
    """Extract approximately `word_limit` Arabic words of context before/after a boundary.

    direction: "before" (units before boundary_idx) or "after" (units after boundary_idx)
    """
    collected_parts: list[str] = []
    total_words = 0

    if direction == "before":
        # Walk backward from boundary_idx - 1
        candidates = [
            cu for cu in content_units if cu["unit_index"] < boundary_idx
        ]
        candidates.sort(key=lambda cu: cu["unit_index"], reverse=True)
    else:
        # Walk forward from boundary_idx + 1
        candidates = [
            cu for cu in content_units if cu["unit_index"] > boundary_idx
        ]
        candidates.sort(key=lambda cu: cu["unit_index"])

    for cu in candidates:
        text = cu.get("primary_text", "")
        wc = arabic_word_count(text)
        collected_parts.append(text)
        total_words += wc
        if total_words >= word_limit:
            break

    if direction == "before":
        collected_parts.reverse()

    return "\n".join(collected_parts)


def check_alignment(
    heading: str, text: str, mode: str = "strict"
) -> bool:
    """Check L-003 heading-text alignment.

    strict: first 15 stripped heading chars in first 100 stripped text chars
    moderate: first 30 stripped heading chars in first 200 stripped text chars
    """
    heading_clean = strip_arabic_noise(heading)
    text_clean = strip_arabic_noise(text)

    if mode == "strict":
        h_prefix = heading_clean[:15]
        t_prefix = text_clean[:100]
    else:  # moderate
        h_prefix = heading_clean[:30]
        t_prefix = text_clean[:200]

    if not h_prefix:
        return False
    return h_prefix in t_prefix


# ──────────────────────────────────────────────────────────────────
# Selection logic
# ──────────────────────────────────────────────────────────────────


def select_divisions_for_fixture(
    candidates: list[dict[str, Any]],
    fixture_name: str,
    config: dict[str, Any],
) -> list[dict[str, Any]]:
    """Select divisions based on per-fixture criteria."""
    target = config["target_count"]

    if len(candidates) <= target:
        for c in candidates:
            if "selection_reason" not in c:
                c["selection_reason"] = "only candidate available"
        return candidates

    # For ibn_aqil: prioritize divisions with verse-commentary content
    if config.get("require_verse"):
        verse_candidates = [c for c in candidates if c.get("has_verse_content")]
        non_verse = [c for c in candidates if not c.get("has_verse_content")]

        selected: list[dict[str, Any]] = []

        # Take verse candidates first (sorted by distance from midpoint of range)
        midpoint = (config["min_words"] + config["max_words"]) / 2
        verse_sorted = sorted(
            verse_candidates, key=lambda d: abs(d["arabic_word_count"] - midpoint)
        )
        for c in verse_sorted:
            if len(selected) >= target:
                break
            c["selection_reason"] = "verse-commentary content detected"
            selected.append(c)

        # Fill remaining from non-verse if needed
        non_verse_sorted = sorted(
            non_verse, key=lambda d: abs(d["arabic_word_count"] - midpoint)
        )
        for c in non_verse_sorted:
            if len(selected) >= target:
                break
            c["selection_reason"] = "prose division (no verse detected)"
            selected.append(c)

        return selected[:target]

    # For taysir: select from different heading paths for genre diversity
    if fixture_name == "taysir":
        # Group by top-level heading (kitab section)
        by_section: dict[str, list[dict[str, Any]]] = {}
        for c in candidates:
            top = c["heading_path"][0] if c["heading_path"] else "unknown"
            by_section.setdefault(top, []).append(c)

        selected = []
        # Round-robin across sections, pick closest to 3000w from each
        sections = list(by_section.values())
        for section_list in sections:
            section_list.sort(key=lambda d: abs(d["arabic_word_count"] - 3000))

        section_idx = 0
        while len(selected) < target and any(sections):
            section_list = sections[section_idx % len(sections)]
            if section_list:
                c = section_list.pop(0)
                c["selection_reason"] = (
                    f"diverse section: {c['heading_path'][0][:30] if c['heading_path'] else '?'}"
                )
                selected.append(c)
            section_idx += 1
            # Remove empty sections
            sections = [s for s in sections if s]

        return selected[:target]

    # For masala/QA fixtures: just take closest to midpoint
    midpoint = (config["min_words"] + config["max_words"]) / 2
    sorted_candidates = sorted(
        candidates, key=lambda d: abs(d["arabic_word_count"] - midpoint)
    )
    for c in sorted_candidates[:target]:
        if "selection_reason" not in c:
            c["selection_reason"] = f"closest to {int(midpoint)}w target"
    return sorted_candidates[:target]


# ──────────────────────────────────────────────────────────────────
# Main processing
# ──────────────────────────────────────────────────────────────────

# Report data collected during processing
report_data: list[dict[str, Any]] = []


def process_fixture(fixture_name: str) -> list[dict[str, Any]]:
    """Process a single fixture: load, filter, select, extract."""
    config = FIXTURE_CONFIG[fixture_name]
    min_w = config["min_words"]
    max_w = config["max_words"]

    print(f"\n--- {fixture_name} (target: {config['target_count']}, range: {min_w}-{max_w}w) ---")

    pkg_dir = PACKAGES_DIR / fixture_name
    if not pkg_dir.exists():
        print(f"  SKIPPED — package not found at {pkg_dir}")
        return []

    manifest, content_units = load_package(fixture_name)
    cu_by_index: dict[int, dict[str, Any]] = {cu["unit_index"]: cu for cu in content_units}
    total_units = len(content_units)

    leaves = find_leaf_divisions(manifest.get("division_tree", []))
    print(f"  Leaf divisions: {len(leaves)}")

    # Determine alignment mode
    is_ibn_aqil = fixture_name.startswith("ibn_aqil")
    alignment_mode = "strict"

    # For ibn_aqil: test strict first, relax if >80% rejected
    if is_ibn_aqil:
        strict_pass = 0
        strict_total = 0
        for leaf in leaves:
            start = leaf["start_unit_index"]
            end = leaf["end_unit_index"]
            assembled, _ = assemble_text(content_units, start, end)
            wc = arabic_word_count(assembled)
            if min_w <= wc <= max_w:
                strict_total += 1
                if check_alignment(leaf["heading_text"], assembled, "strict"):
                    strict_pass += 1

        if strict_total > 0:
            reject_rate = 1.0 - (strict_pass / strict_total)
            print(f"  L-003 strict: {strict_pass}/{strict_total} pass ({reject_rate:.0%} rejected)")
            if reject_rate > 0.80:
                alignment_mode = "moderate"
                print(f"  → Relaxing to MODERATE alignment (first 30 in first 200)")
        else:
            print(f"  L-003: no candidates in word range to test alignment")

    # Filter candidates
    candidates: list[dict[str, Any]] = []
    for leaf_idx, leaf in enumerate(leaves):
        start = leaf["start_unit_index"]
        end = leaf["end_unit_index"]
        heading = leaf["heading_text"]

        assembled, char_offsets = assemble_text(content_units, start, end)
        wc = arabic_word_count(assembled)

        # Word count filter
        if wc < min_w or wc > max_w:
            continue

        # Alignment check
        if not check_alignment(heading, assembled, alignment_mode):
            continue

        # Exclude non-scholarly
        if any(kw in heading for kw in EXCLUDE_KEYWORDS):
            continue

        # Skip tree index 0 (introductions)
        if leaf_idx == 0:
            continue

        # Format-specific checks
        verse_content = has_verse_commentary(assembled) if is_ibn_aqil else False

        if config.get("require_masala"):
            if not has_masala_markers(assembled, config["require_masala"]):
                continue

        if config.get("require_qa"):
            if not has_qa_markers(assembled, config["require_qa"]):
                continue

        # Get last unit's BC
        last_cu = cu_by_index.get(end, {})
        bc_last = last_cu.get("boundary_continuity")
        bc_last_type = bc_last.get("type") if bc_last else None

        candidates.append({
            "leaf": leaf,
            "assembled_text": assembled,
            "char_offsets": char_offsets,
            "arabic_word_count": wc,
            "start_unit_index": start,
            "end_unit_index": end,
            "heading_text": heading,
            "heading_path": leaf["heading_path"],
            "bc_last_type": bc_last_type,
            "bc_last": bc_last,
            "has_multi_layer": has_multi_layer_units(content_units, start, end),
            "has_verse_content": verse_content,
        })

    print(f"  Aligned candidates ({min_w}-{max_w}w): {len(candidates)}")

    # Record report data
    fixture_report = {
        "fixture_name": fixture_name,
        "total_leaves": len(leaves),
        "total_in_range": sum(
            1 for leaf in leaves
            if min_w <= arabic_word_count(
                assemble_text(content_units, leaf["start_unit_index"], leaf["end_unit_index"])[0]
            ) <= max_w
        ),
        "aligned_candidates": len(candidates),
        "alignment_mode": alignment_mode,
        "config": config,
        "selected": [],
    }

    if not candidates:
        print(f"  WARNING: No aligned candidates for {fixture_name}")
        report_data.append(fixture_report)
        return []

    # Select divisions
    selected = select_divisions_for_fixture(candidates, fixture_name, config)
    print(f"  Selected: {len(selected)}")

    results: list[dict[str, Any]] = []
    for div in selected:
        start = div["start_unit_index"]
        end = div["end_unit_index"]

        # Extract 200-word context
        ctx_before = extract_word_context(content_units, start, "before", 200)
        ctx_after = extract_word_context(content_units, end, "after", 200)

        # Rebase text layers
        rebased_layers = rebase_text_layers(content_units, start, end, div["char_offsets"])

        # Aggregate content flags
        agg_flags = aggregate_content_flags(content_units, start, end)

        result = {
            "fixture_name": fixture_name,
            "div_start_unit": start,
            "div_end_unit": end,
            "heading_text": div["heading_text"],
            "heading_path": div["heading_path"],
            "assembled_text": div["assembled_text"],
            "arabic_word_count": div["arabic_word_count"],
            "text_layers": rebased_layers,
            "content_flags_aggregated": agg_flags,
            "boundary_continuity_last_unit": div["bc_last"],
            "context_before": ctx_before,
            "context_after": ctx_after,
            "selection_reason": div.get("selection_reason", "selected"),
            "has_verse_content": div.get("has_verse_content", False),
        }
        results.append(result)

        fixture_report["selected"].append({
            "div_start": start,
            "heading": div["heading_text"],
            "words": div["arabic_word_count"],
            "reason": div.get("selection_reason", ""),
            "has_verse": div.get("has_verse_content", False),
        })

    report_data.append(fixture_report)
    return results


def write_division_json(div: dict[str, Any]) -> Path:
    """Write division JSON file."""
    out_dir = DIVISIONS_DIR / div["fixture_name"]
    out_dir.mkdir(parents=True, exist_ok=True)

    path = out_dir / f"div_{div['div_start_unit']}.json"
    with open(path, "w", encoding="utf-8") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return path


def write_division_md(div: dict[str, Any]) -> Path:
    """Write readable markdown file for the division."""
    out_dir = DIVISIONS_DIR / div["fixture_name"]
    out_dir.mkdir(parents=True, exist_ok=True)

    bc_last = div.get("boundary_continuity_last_unit") or {}
    bc_type = bc_last.get("type", "N/A")
    bc_conf = bc_last.get("confidence", "N/A")

    path = out_dir / f"div_{div['div_start_unit']}_text.md"
    with open(path, "w", encoding="utf-8") as f:
        f.write(f"# Division: {div['heading_text']}\n")
        f.write(f"**Fixture:** {div['fixture_name']} | "
                f"**Words:** {div['arabic_word_count']} | "
                f"**Units:** {div['div_start_unit']}-{div['div_end_unit']}\n")
        f.write(f"**Selection reason:** {div['selection_reason']}\n")
        f.write(f"**BC last unit:** {bc_type} ({bc_conf})\n")
        if div.get("has_verse_content"):
            f.write("**Verse content:** YES\n")
        f.write("\n---\n\n")
        f.write(div["assembled_text"])
        f.write("\n\n---\n\n")
        f.write("## Context Before (~200 words)\n")
        f.write(div.get("context_before", "") or "(none)")
        f.write("\n\n")
        f.write("## Context After (~200 words)\n")
        f.write(div.get("context_after", "") or "(none)")
        f.write("\n")
    return path


def generate_extraction_report() -> None:
    """Write EXTRACTION_REPORT.md with detailed per-fixture analysis."""
    lines: list[str] = []
    lines.append("# Format Diversity — Extraction Report\n")
    lines.append("## Summary\n")

    total_selected = sum(len(r["selected"]) for r in report_data)
    lines.append(f"**Total divisions extracted:** {total_selected}\n")

    lines.append("| Fixture | Leaf Divs | In Range | Aligned | Selected | Alignment Mode |")
    lines.append("|---------|-----------|----------|---------|----------|----------------|")

    for r in report_data:
        lines.append(
            f"| {r['fixture_name']} | {r['total_leaves']} | {r['total_in_range']} "
            f"| {r['aligned_candidates']} | {len(r['selected'])} | {r['alignment_mode']} |"
        )

    lines.append("")

    # Per-fixture details
    for r in report_data:
        lines.append(f"## {r['fixture_name']}\n")
        cfg = r["config"]
        lines.append(f"- **Word range:** {cfg['min_words']}-{cfg['max_words']}")
        lines.append(f"- **Target count:** {cfg['target_count']}")
        lines.append(f"- **Priority:** {cfg['priority']}")
        lines.append(f"- **Alignment mode:** {r['alignment_mode']}")
        lines.append(f"- **Total leaf divisions:** {r['total_leaves']}")
        lines.append(f"- **In word range:** {r['total_in_range']}")
        lines.append(f"- **Passed alignment:** {r['aligned_candidates']}")
        lines.append("")

        if r["selected"]:
            lines.append("### Selected Divisions\n")
            lines.append("| Div Start | Heading | Words | Verse | Reason |")
            lines.append("|-----------|---------|-------|-------|--------|")
            for s in r["selected"]:
                verse_mark = "YES" if s.get("has_verse") else "no"
                heading_short = s["heading"][:50]
                lines.append(
                    f"| {s['div_start']} | {heading_short} | {s['words']} "
                    f"| {verse_mark} | {s['reason']} |"
                )
            lines.append("")
        else:
            lines.append("*No divisions selected.*\n")

        # Ibn aqil specific note
        if r["fixture_name"].startswith("ibn_aqil"):
            verse_count = sum(1 for s in r["selected"] if s.get("has_verse"))
            lines.append(
                f"**Verse-commentary note:** {verse_count}/{len(r['selected'])} "
                f"selected divisions contain visible verse content.\n"
            )

    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"\nExtraction report written to: {REPORT_PATH}")


def main() -> None:
    all_divisions: list[dict[str, Any]] = []

    for fixture_name in FIXTURE_CONFIG:
        divs = process_fixture(fixture_name)
        for div in divs:
            write_division_json(div)
            write_division_md(div)
        all_divisions.extend(divs)

    # Generate extraction report
    generate_extraction_report()

    # Verification summary
    print("\n" + "=" * 120)
    print("DIVISION EXTRACTION SUMMARY")
    print("=" * 120)
    print(
        f"\n{'Fixture':<20} {'Start':>6} {'Heading (50 chars)':<52} "
        f"{'Words':>6} {'Verse':>6} {'Reason'}"
    )
    print("-" * 130)

    for div in all_divisions:
        heading_short = div["heading_text"][:50]
        verse = "YES" if div.get("has_verse_content") else ""
        print(
            f"{div['fixture_name']:<20} {div['div_start_unit']:>6} {heading_short:<52} "
            f"{div['arabic_word_count']:>6} {verse:>6} {div['selection_reason']}"
        )

    print(f"\nTotal divisions selected: {len(all_divisions)}")

    # Visual alignment confirmation
    print("\n--- Alignment Confirmation (first 60 stripped chars) ---")
    for div in all_divisions:
        heading_stripped = strip_arabic_noise(div["heading_text"])[:30]
        text_stripped = strip_arabic_noise(div["assembled_text"])[:60]
        print(f"\n  [{div['fixture_name']} div_{div['div_start_unit']}]")
        print(f"  Heading: {heading_stripped}")
        print(f"  Text:    {text_stripped}")

    print(f"\nDivisions written to: {DIVISIONS_DIR}")


if __name__ == "__main__":
    main()
