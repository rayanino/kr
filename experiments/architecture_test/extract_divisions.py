"""Deliverable 2: Extract high-quality divisions for LLM testing.

Loads normalized packages from D1, selects 2 aligned divisions per fixture,
and writes JSON + readable MD files for each selected division.

Key: STRICT alignment check (L-003 filter) rejects 40-60% of leaf divisions
where heading-content misalignment would produce garbage LLM results.
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

# Non-scholarly heading keywords to exclude (bibliography/index)
EXCLUDE_KEYWORDS = ["مصادر", "مراجع", "فهرس", "ثبت المصادر", "المراجع"]

# BoundaryContinuityType → join separator mapping
BC_JOIN_MAP: dict[Optional[str], str] = {
    "mid_sentence": " ",        # space (SPEC-NOTE-4: Arabic pages never split words)
    "mid_paragraph": "\n",     # single newline
    "mid_argument": "\n",      # single newline
    "section_break": "\n\n",   # double newline
    "division_break": "\n\n",  # double newline
    "unknown": "\n",           # conservative
    None: "\n",                # absent → conservative
}


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

    # Index by unit_index for fast lookup
    content_units.sort(key=lambda cu: cu["unit_index"])
    return manifest, content_units


def find_leaf_divisions(nodes: list[dict[str, Any]], path: Optional[list[str]] = None) -> list[dict[str, Any]]:
    """Walk division tree and return leaf divisions with heading_path attached."""
    if path is None:
        path = []

    leaves: list[dict[str, Any]] = []
    for node in nodes:
        current_path = path + [node["heading_text"]]
        if not node.get("children", []):
            # Leaf node — attach heading_path
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
    """Assemble text from content units in [start_idx, end_idx] (inclusive).

    Returns (assembled_text, offsets) where offsets is a list of
    (char_offset, separator) per unit for text_layers rebasing.
    """
    parts: list[str] = []
    offsets: list[tuple[int, str]] = []  # (cumulative_char_offset, separator_before)
    cumulative = 0

    for i, cu in enumerate(content_units):
        idx = cu["unit_index"]
        if idx < start_idx or idx > end_idx:
            continue

        if parts:
            # Use the PREVIOUS unit's boundary_continuity to decide separator
            prev_cu = content_units[i - 1] if i > 0 else cu
            # Actually, BC is on the unit whose boundary we're crossing
            # BC on unit N describes what happens AFTER unit N (between N and N+1)
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


def extract_context(
    content_units: list[dict[str, Any]],
    start_idx: int,
    end_idx: int,
    total_units: int,
    direction: str,
) -> str:
    """Extract context_before or context_after using 3 adjacent units."""
    if direction == "before":
        ctx_start = max(0, start_idx - 3)
        ctx_end = start_idx - 1
    else:  # "after"
        ctx_start = end_idx + 1
        ctx_end = min(total_units - 1, end_idx + 3)

    if ctx_start > ctx_end:
        return ""

    text, _ = assemble_text(content_units, ctx_start, ctx_end)
    return text


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


def select_divisions(
    candidates: list[dict[str, Any]],
    fixture_name: str,
    content_units: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Select 2 divisions per fixture from aligned candidates.

    Selection priority: closest to 700 words.
    Special cases for 03_fiqh (mid_argument BC) and 02_nahw_muhaqiq (multi-layer).
    """
    if len(candidates) <= 2:
        return candidates

    # Sort by distance from 700 words
    sorted_candidates = sorted(candidates, key=lambda d: abs(d["arabic_word_count"] - 700))

    selected: list[dict[str, Any]] = []

    # Exception for 03_fiqh: prefer mid_argument BC for D-011 test
    if fixture_name == "03_fiqh":
        for c in sorted_candidates:
            if c.get("bc_last_type") == "mid_argument" and c not in selected:
                selected.append(c)
                c["selection_reason"] = "mid_argument BC (D-011 test)"
                break

    # Exception for 02_nahw_muhaqiq: prefer multi-layer division
    if fixture_name == "02_nahw_muhaqiq":
        for c in sorted_candidates:
            if c.get("has_multi_layer") and c not in selected:
                selected.append(c)
                c["selection_reason"] = "multi-layer division"
                break

    # Fill remaining slots from sorted candidates
    for c in sorted_candidates:
        if len(selected) >= 2:
            break
        if c not in selected:
            if "selection_reason" not in c:
                c["selection_reason"] = "closest to 700w target"
            selected.append(c)

    return selected[:2]


def process_fixture(fixture_name: str) -> list[dict[str, Any]]:
    """Process a single fixture: load, filter, select, extract."""
    print(f"\n--- {fixture_name} ---")
    manifest, content_units = load_package(fixture_name)

    # Build unit index map for fast lookup
    cu_by_index: dict[int, dict[str, Any]] = {cu["unit_index"]: cu for cu in content_units}
    total_units = len(content_units)

    # Find leaf divisions
    leaves = find_leaf_divisions(manifest.get("division_tree", []))
    print(f"  Leaf divisions: {len(leaves)}")

    # Process each leaf
    candidates: list[dict[str, Any]] = []
    for leaf_idx, leaf in enumerate(leaves):
        start = leaf["start_unit_index"]
        end = leaf["end_unit_index"]
        heading = leaf["heading_text"]

        # Assemble text
        assembled, char_offsets = assemble_text(content_units, start, end)
        wc = arabic_word_count(assembled)

        # Step 5: Filter by word count
        if wc < 300 or wc > 2000:
            continue

        # Step 6: STRICT alignment check
        heading_clean = strip_arabic_noise(heading)[:15]
        text_clean = strip_arabic_noise(assembled)[:100]
        aligned = heading_clean in text_clean if heading_clean else False
        if not aligned:
            continue

        # Step 7: Exclude non-scholarly
        if any(kw in heading for kw in EXCLUDE_KEYWORDS):
            continue

        # Skip tree index 0 (introductions)
        if leaf_idx == 0:
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
        })

    print(f"  Aligned candidates (300-2000w): {len(candidates)}")

    if not candidates:
        print(f"  WARNING: No aligned candidates for {fixture_name}")
        return []

    # Select 2
    selected = select_divisions(candidates, fixture_name, content_units)
    print(f"  Selected: {len(selected)}")

    results: list[dict[str, Any]] = []
    for div in selected:
        start = div["start_unit_index"]
        end = div["end_unit_index"]

        # Extract context
        ctx_before = extract_context(content_units, start, end, total_units, "before")
        ctx_after = extract_context(content_units, start, end, total_units, "after")

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
            "selection_reason": div.get("selection_reason", "closest to 700w target"),
        }
        results.append(result)

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
        f.write("\n---\n\n")
        f.write(div["assembled_text"])
        f.write("\n\n---\n\n")
        f.write("## Context Before (previous 3 units)\n")
        f.write(div.get("context_before", "") or "(none)")
        f.write("\n\n")
        f.write("## Context After (next 3 units)\n")
        f.write(div.get("context_after", "") or "(none)")
        f.write("\n")
    return path


def main() -> None:
    all_divisions: list[dict[str, Any]] = []

    fixtures = ["03_fiqh", "07_balagha", "06_usul", "02_nahw_muhaqiq", "10_no_author"]
    for fixture_name in fixtures:
        divs = process_fixture(fixture_name)
        for div in divs:
            write_division_json(div)
            write_division_md(div)
        all_divisions.extend(divs)

    # Verification summary
    print("\n" + "=" * 100)
    print("DIVISION EXTRACTION SUMMARY")
    print("=" * 100)
    print(f"\n{'Fixture':<20} {'Start':>6} {'Heading (50 chars)':<52} {'Words':>6} {'Reason'}")
    print("-" * 120)

    for div in all_divisions:
        heading_short = div["heading_text"][:50]
        print(f"{div['fixture_name']:<20} {div['div_start_unit']:>6} {heading_short:<52} "
              f"{div['arabic_word_count']:>6} {div['selection_reason']}")

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
