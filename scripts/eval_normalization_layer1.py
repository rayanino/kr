#!/usr/bin/env python3
"""Normalization Engine — Layer 1 Programmatic Validation.

Runs normalize_source on all 63 repo fixtures and collects metrics
per NEXT.md Layer 1 specification.
"""

import json
import sys
import traceback
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from bs4 import BeautifulSoup

from engines.normalization.contracts import NormalizedPackage, LayerType
from engines.normalization.src.dispatcher import normalize_source
from engines.normalization.src.validation import validate_package
from engines.normalization.tests.conftest import _make_source_metadata

DIACRITICS = {chr(cp) for cp in range(0x064B, 0x0653)} | {"\u0670", "\u0640"}
ARABIC_RANGE = range(0x0600, 0x0700)
MULTI_LAYER = {"02_nahw_muhaqiq"}


def discover_fixtures():
    """Find all Shamela fixtures (real + extended)."""
    project_root = Path(__file__).parent.parent
    fixtures = []
    for base in [
        project_root / "tests" / "fixtures" / "shamela_real",
        project_root / "tests" / "fixtures" / "shamela_extended",
    ]:
        if not base.exists():
            continue
        for d in sorted(base.iterdir()):
            if not d.is_dir() or d.name.startswith("."):
                continue
            htms = list(d.glob("*.htm"))
            if htms:
                fixtures.append((d.name, htms[0]))
    return fixtures


def count_raw_pages(path: Path) -> int:
    """Count raw PageText divs in HTML."""
    raw = path.read_text(encoding="utf-8")
    return len(BeautifulSoup(raw, "lxml").find_all("div", class_="PageText"))


def collect_metrics(name: str, path: Path) -> dict:
    """Run normalize_source and collect all Layer 1 metrics."""
    is_multi = name in MULTI_LAYER
    meta = _make_source_metadata(is_multi_layer=is_multi)

    try:
        pkg = normalize_source(path, meta)
    except Exception as e:
        return {
            "name": name,
            "status": "FATAL_ERROR",
            "error": f"{type(e).__name__}: {e}",
            "traceback": traceback.format_exc(),
        }

    # Run validation
    val_result = validate_package(pkg, meta)
    warnings = val_result.warnings  # already strings
    fatals = [e.message for e in val_result.fatal_errors]

    # Raw page count
    raw_pages = count_raw_pages(path)

    # Content metrics
    total_chars = 0
    arabic_chars = 0
    diacritic_count = 0
    footnote_pages = 0
    multi_layer_units = 0
    has_hadith = 0
    has_quran = 0
    has_verse = 0
    bc_types = set()
    bc_non_none = 0

    for cu in pkg.content_units:
        text = cu.primary_text
        total_chars += len(text)
        for ch in text:
            if ord(ch) in ARABIC_RANGE:
                arabic_chars += 1
            if ch in DIACRITICS:
                diacritic_count += 1

        if cu.footnotes:
            footnote_pages += 1

        if len(cu.text_layers) >= 2:
            layer_types = {seg.layer_type for seg in cu.text_layers}
            if len(layer_types) >= 2:
                multi_layer_units += 1

        if cu.content_flags.has_hadith_citation:
            has_hadith += 1
        if cu.content_flags.has_quran_citation:
            has_quran += 1
        if cu.content_flags.has_verse:
            has_verse += 1

        if cu.boundary_continuity is not None:
            bc_non_none += 1
            bc_types.add(cu.boundary_continuity.type.value)

    n_units = len(pkg.content_units)
    arabic_ratio = arabic_chars / total_chars if total_chars > 0 else 0.0

    return {
        "name": name,
        "status": "OK",
        "content_units": n_units,
        "raw_page_divs": raw_pages,
        "page_loss": abs(n_units - raw_pages),
        "arabic_ratio": round(arabic_ratio, 4),
        "diacritic_count": diacritic_count,
        "footnote_pages": footnote_pages,
        "division_count": len(pkg.manifest.division_tree),
        "layer_count": len(pkg.manifest.layer_map),
        "multi_layer_units": multi_layer_units,
        "boundary_continuity_coverage": round(bc_non_none / n_units, 4) if n_units > 0 else 0.0,
        "boundary_types": sorted(bc_types),
        "has_hadith": has_hadith,
        "has_quran": has_quran,
        "has_verse": has_verse,
        "validation_warnings": warnings,
        "validation_fatals": fatals,
        "validation_passed": val_result.passed,
        "total_chars": total_chars,
        "arabic_chars": arabic_chars,
    }


def main():
    fixtures = discover_fixtures()
    print(f"Found {len(fixtures)} fixtures\n")

    results = []
    fatals_total = 0
    errors_total = 0

    for name, path in fixtures:
        print(f"  Processing {name}...", end=" ", flush=True)
        m = collect_metrics(name, path)
        results.append(m)

        if m["status"] == "FATAL_ERROR":
            errors_total += 1
            print(f"ERROR: {m['error']}")
        else:
            n_fatals = len(m["validation_fatals"])
            fatals_total += n_fatals
            n_warns = len(m["validation_warnings"])
            print(f"OK  units={m['content_units']}  loss={m['page_loss']}  "
                  f"arabic={m['arabic_ratio']:.2%}  diacritics={m['diacritic_count']}  "
                  f"divs={m['division_count']}  layers={m['layer_count']}  "
                  f"warns={n_warns}  fatals={n_fatals}")

    # Save full results
    output_path = Path(__file__).parent.parent / "engines" / "normalization" / "eval_layer1_results.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    # Print aggregate summary
    ok_results = [r for r in results if r["status"] == "OK"]
    print(f"\n{'='*80}")
    print(f"LAYER 1 AGGREGATE SUMMARY")
    print(f"{'='*80}")
    print(f"Total fixtures: {len(results)}")
    print(f"Errors (couldn't process): {errors_total}")
    print(f"Successfully processed: {len(ok_results)}")
    print(f"Total validation fatals: {fatals_total}")

    if ok_results:
        page_losses = [r["page_loss"] for r in ok_results]
        arabic_ratios = [r["arabic_ratio"] for r in ok_results]
        diacritic_counts = [r["diacritic_count"] for r in ok_results]
        
        print(f"\nPage loss: max={max(page_losses)}, mean={sum(page_losses)/len(page_losses):.1f}")
        print(f"  Over 5: {[r['name'] for r in ok_results if r['page_loss'] > 5]}")
        
        print(f"\nArabic ratio: min={min(arabic_ratios):.2%}, max={max(arabic_ratios):.2%}")
        low_arabic = [r for r in ok_results if r["arabic_ratio"] < 0.70]
        if low_arabic:
            items = [(r['name'], round(r['arabic_ratio'] * 100, 1)) for r in low_arabic]
            print(f"  Below 70%: {items}")
        
        print(f"\nDiacritics: min={min(diacritic_counts)}, max={max(diacritic_counts)}, "
              f"mean={sum(diacritic_counts)/len(diacritic_counts):.0f}")
        zero_diacritics = [r for r in ok_results if r["diacritic_count"] == 0]
        if zero_diacritics:
            print(f"  Zero diacritics: {[r['name'] for r in zero_diacritics]}")

        # Warning patterns
        from collections import Counter
        all_warns = []
        for r in ok_results:
            all_warns.extend(r["validation_warnings"])
        if all_warns:
            warn_counter = Counter()
            for w in all_warns:
                # Extract warning code if present
                code = w.split(":")[0] if ":" in w else w[:60]
                warn_counter[code] += 1
            print(f"\nWarning patterns ({len(all_warns)} total):")
            for code, count in warn_counter.most_common(10):
                print(f"  {count:3d}x  {code}")

        # Boundary continuity coverage
        bc_coverages = [r["boundary_continuity_coverage"] for r in ok_results]
        print(f"\nBoundary continuity coverage: min={min(bc_coverages):.2%}, "
              f"max={max(bc_coverages):.2%}, mean={sum(bc_coverages)/len(bc_coverages):.2%}")

        # Multi-layer
        multi = [r for r in ok_results if r["multi_layer_units"] > 0]
        print(f"\nMulti-layer fixtures: {len(multi)}")
        for r in multi:
            print(f"  {r['name']}: {r['multi_layer_units']} multi-layer units")

        # Content flags distribution
        had = sum(r["has_hadith"] for r in ok_results)
        qur = sum(r["has_quran"] for r in ok_results)
        ver = sum(r["has_verse"] for r in ok_results)
        print(f"\nContent flags: hadith_pages={had}, quran_pages={qur}, verse_pages={ver}")

    print(f"\nFull results saved to: {output_path}")


if __name__ == "__main__":
    main()
