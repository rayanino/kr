#!/usr/bin/env python3
"""Layer 3 — Manual Structural Inspection.

For each selected fixture, runs normalize_source and prints diagnostic output
for human reading: primary text, footnotes, headings, layer segments, and
boundary continuity signals.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.normalization.contracts import NormalizedPackage, LayerType
from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.tests.conftest import _make_source_metadata, FIXTURES_REAL

# Extended fixtures path
FIXTURES_EXT = Path("tests/fixtures/shamela_extended")

INSPECTIONS = [
    ("02_nahw_muhaqiq", FIXTURES_REAL / "02_nahw_muhaqiq" / "book.htm", True),
    ("03_fiqh", FIXTURES_REAL / "03_fiqh" / "book.htm", False),
    ("04_hadith", FIXTURES_REAL / "04_hadith" / "book.htm", False),
    ("06_usul", FIXTURES_REAL / "06_usul" / "book.htm", False),
    ("ext_50", FIXTURES_EXT / "ext_50" / "book.htm", False),
]

DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670", "\u0640"}


def count_diacritics(text: str) -> int:
    return sum(1 for c in text if c in DIACRITICS)


def inspect_fixture(name: str, path: Path, is_multi: bool):
    print(f"\n{'='*80}")
    print(f"FIXTURE: {name}  (multi_layer={is_multi})")
    print(f"{'='*80}")

    meta = _make_source_metadata(is_multi_layer=is_multi)
    pkg = normalize_source(path, meta)

    units = pkg.content_units
    print(f"Content units: {len(units)}")
    print(f"Division tree: {len(pkg.manifest.division_tree)} top-level nodes")
    print(f"Layer map: {len(pkg.manifest.layer_map)} entries")

    # ── Inspection 1: First 3 pages — full primary_text ──
    print(f"\n--- First 3 pages: primary_text ---")
    for cu in units[:3]:
        diac = count_diacritics(cu.primary_text)
        print(f"\n  [unit_index={cu.unit_index}] ({len(cu.primary_text)} chars, {diac} diacritics)")
        # Print first 500 chars to keep output manageable
        text = cu.primary_text[:500]
        if len(cu.primary_text) > 500:
            text += " [...]"
        print(f"  {text}")

    # ── Inspection 2: Footnote pages ──
    fn_pages = [cu for cu in units if cu.footnotes]
    if fn_pages:
        print(f"\n--- Footnote pages: {len(fn_pages)} pages have footnotes ---")
        for cu in fn_pages[:3]:
            print(f"\n  [unit_index={cu.unit_index}] {len(cu.footnotes)} footnotes")
            print(f"  Primary text (last 200 chars): ...{cu.primary_text[-200:]}")
            for fn in cu.footnotes[:3]:
                print(f"    Footnote {fn.ref_marker}: {fn.text[:100]}...")
    else:
        print(f"\n--- No footnote pages ---")

    # ── Inspection 3: Division headings ──
    print(f"\n--- Division tree (table of contents) ---")
    def print_tree(nodes, depth=0):
        for node in nodes:
            indent = "  " * (depth + 1)
            print(f"{indent}[L{node.heading_level}] {node.heading_text}  "
                  f"(pages {node.start_unit_index}-{node.end_unit_index}, "
                  f"method={node.detection_method}, conf={node.confidence})")
            if node.children:
                print_tree(node.children, depth + 1)
    print_tree(pkg.manifest.division_tree)

    # ── Inspection 4: Layer segments (multi-layer only) ──
    multi_units = [cu for cu in units if len({seg.layer_type for seg in cu.text_layers}) >= 2]
    if multi_units:
        print(f"\n--- Multi-layer pages: {len(multi_units)} ---")
        for cu in multi_units[:2]:
            print(f"\n  [unit_index={cu.unit_index}]")
            for seg in cu.text_layers:
                seg_text = cu.primary_text[seg.start:seg.end]
                preview = seg_text[:150].replace('\n', '↵')
                if len(seg_text) > 150:
                    preview += "..."
                print(f"    {seg.layer_type.value} [{seg.start}:{seg.end}] conf={seg.confidence}  "
                      f"→ {preview}")
    else:
        # Show single-layer segments for first 2 pages
        print(f"\n--- Single-layer pages (first 2) ---")
        for cu in units[:2]:
            print(f"\n  [unit_index={cu.unit_index}]")
            for seg in cu.text_layers:
                print(f"    {seg.layer_type.value} [{seg.start}:{seg.end}] conf={seg.confidence}")

    # ── Inspection 5: Boundary continuity (5 consecutive pages) ──
    print(f"\n--- Boundary continuity (pages 5-9) ---")
    for cu in units[5:10]:
        bc = cu.boundary_continuity
        last_30 = cu.primary_text[-30:].replace('\n', '↵')
        if bc:
            print(f"  [unit_index={cu.unit_index}] type={bc.type.value}  conf={bc.confidence:.2f}  "
                  f"method={bc.detection_method.value}")
            print(f"    Last 30 chars: «{last_30}»")
        else:
            print(f"  [unit_index={cu.unit_index}] BC=None")
            print(f"    Last 30 chars: «{last_30}»")

    # ── Inspection 6: Content flags summary ──
    hadith_pages = sum(1 for cu in units if cu.content_flags.has_hadith_citation)
    quran_pages = sum(1 for cu in units if cu.content_flags.has_quran_citation)
    verse_pages = sum(1 for cu in units if cu.content_flags.has_verse)
    blank_pages = sum(1 for cu in units if cu.content_flags.is_blank)
    print(f"\n--- Content flags ---")
    print(f"  Hadith: {hadith_pages}/{len(units)} pages")
    print(f"  Quran: {quran_pages}/{len(units)} pages")
    print(f"  Verse: {verse_pages}/{len(units)} pages")
    print(f"  Blank: {blank_pages}/{len(units)} pages")


def main():
    fixture = sys.argv[1] if len(sys.argv) > 1 else None
    for name, path, is_multi in INSPECTIONS:
        if fixture and name != fixture:
            continue
        inspect_fixture(name, path, is_multi)


if __name__ == "__main__":
    main()
