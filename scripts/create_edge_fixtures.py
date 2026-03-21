"""Create edge case test fixtures from sweep analysis.

Selects 10 books representing unique edge cases not covered by existing
fixtures. Creates .htm files + companion .json metadata.
"""

from __future__ import annotations

import json
import re
import shutil
from pathlib import Path


def main() -> None:
    samples = Path("shamela-export-samples")
    dest = Path("tests/fixtures/shamela_edge_cases")
    dest.mkdir(parents=True, exist_ok=True)

    fixtures: list[dict[str, str]] = []

    # 1. Extreme small (2KB single volume)
    src = samples / "بحوث لبعض النوازل الفقهية المعاصرة" / "001.htm"
    name = "edge_extreme_small_2kb.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "بحوث لبعض النوازل الفقهية المعاصرة (volume 1)",
        "category": "extreme",
        "description": "Extremely small book volume (2KB, ~2 pages). Tests minimum viable input.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Tests pipeline behavior with minimal input - only 1-2 content units expected",
        "expected_behavior": "Pipeline completes without crash, produces 1-2 content units",
    })

    # 2. Tiny 3-page book with zero diacritics
    src = samples / "أسامي الضعفاء - أبو زرعة الرازي - ت الهاشمي" / "001.htm"
    name = "edge_tiny_zero_diacritics.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "أسامي الضعفاء - أبو زرعة الرازي - ت الهاشمي (volume 1)",
        "category": "extreme",
        "description": "Tiny book (3 pages) with zero diacritical marks. Double edge case.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Zero diacritics combined with extreme small size",
        "expected_behavior": "Pipeline completes, diacritics check passes (0 diacritics is valid)",
    })

    # 3. Zero diacritics + hadith content
    src = samples / "الأربعون المختارة من حديث الإمام أبي حنيفة.htm"
    name = "edge_zero_diacritics_hadith.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "الأربعون المختارة من حديث الإمام أبي حنيفة",
        "category": "extreme",
        "description": "Hadith collection with zero diacritical marks. 52 content units.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Zero diacritics in hadith text - tests content flag detection without diacritics",
        "expected_behavior": "Pipeline produces ~52 units, has_hadith detected, diacritics check passes",
    })

    # 4. Zero content flags (pure grammar)
    src = samples / "البرعومة في النحو.htm"
    name = "edge_zero_flags_nahw.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "البرعومة في النحو",
        "category": "extreme",
        "description": "Pure grammar text with zero content flags (no hadith, quran, or verse).",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Tests pipeline handles books with no content flag triggers gracefully",
        "expected_behavior": "Pipeline completes, content flags all false, validation passes",
    })

    # 5. Low Arabic ratio (55.4%)
    src_name = "تخريج أحاديث شواهد التوضيح وملاحظات على طبعة فؤاد عبد الباقي - ضمن \u00abآثار المعلمي\u00bb.htm"
    src = samples / src_name
    name = "edge_low_arabic_ratio.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": src_name.replace(".htm", ""),
        "category": "extreme",
        "description": "Book with very low Arabic ratio (55.4%). High proportion of isnad chains and numbers.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Tests Arabic ratio validation at the threshold boundary",
        "expected_behavior": "Pipeline completes with low_arabic_ratio warnings on many pages",
    })

    # 6. High page loss (13 pages)
    src = samples / "أدب الاختلاف في الإسلام.htm"
    name = "edge_high_page_loss.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "أدب الاختلاف في الإسلام",
        "category": "extreme",
        "description": "Book with high page loss (13 pages lost between raw divs and content units).",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Tests page loss tolerance - 157 raw pages to 144 content units",
        "expected_behavior": "Pipeline completes, validation notes page loss in warnings",
    })

    # 7. Zero diacritics large (148KB, 361 units)
    src = samples / "أحوال الرجال.htm"
    name = "edge_zero_diacritics_large.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "أحوال الرجال",
        "category": "extreme",
        "description": "Large book (361 units) with zero diacritical marks. Rijal text.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Zero diacritics at scale - tests diacritics check with large corpus",
        "expected_behavior": "Pipeline produces ~361 units, diacritics check passes",
    })

    # 8. Multi-layer 99%+ (extract first 20 pages)
    src = samples / "إعراب القرآن العظيم المنسوب لزكريا الانصارى.htm"
    html = src.read_text(encoding="utf-8")
    pages = list(re.finditer(r"<div class=['\"]PageText['\"]>", html))
    if len(pages) > 20:
        cutoff = pages[20].start()
        extracted = html[:cutoff] + "</body></html>"
    else:
        extracted = html
    name = "edge_multi_layer_99pct.htm"
    (dest / name).write_text(extracted, encoding="utf-8")
    fixtures.append({
        "file": name,
        "original_book": "إعراب القرآن العظيم المنسوب لزكريا الانصارى",
        "category": "multi_layer",
        "description": "Extract of first 20 pages from a 99.3% multi-layer book.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Nearly all content units are multi-layer - tests layer detection at extreme ratio",
        "expected_behavior": "Pipeline produces ~20 units with very high multi-layer detection rate",
    })

    # 9. Grammar text (25 units, zero flags)
    src = samples / "الأنشوطة في النحو.htm"
    name = "edge_nahw_grammar.htm"
    shutil.copy2(src, dest / name)
    fixtures.append({
        "file": name,
        "original_book": "الأنشوطة في النحو",
        "category": "extreme",
        "description": "Medium grammar text (25 units). No content flags.",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "Pure grammar with no triggering patterns - tests baseline pipeline behavior",
        "expected_behavior": "Pipeline completes, all content flags false, validation passes",
    })

    # 10. Warning-heavy extract (first 30 pages from ديوان الضعفاء)
    src = samples / "ديوان الضعفاء.htm"
    html = src.read_text(encoding="utf-8")
    pages = list(re.finditer(r"<div class=['\"]PageText['\"]>", html))
    if len(pages) > 30:
        cutoff = pages[30].start()
        extracted = html[:cutoff] + "</body></html>"
    else:
        extracted = html
    name = "edge_warning_heavy.htm"
    (dest / name).write_text(extracted, encoding="utf-8")
    fixtures.append({
        "file": name,
        "original_book": "ديوان الضعفاء",
        "category": "warning",
        "description": "Extract of first 30 pages from the most warning-heavy book (393 total warnings).",
        "discovered_in": "weekend_sweep_task1",
        "key_feature": "High warning density - tests validation warning handling at scale",
        "expected_behavior": "Pipeline completes with many warnings but no fatals",
    })

    # Write companion JSON files
    for fix in fixtures:
        json_name = fix["file"].replace(".htm", ".json")
        (dest / json_name).write_text(
            json.dumps(fix, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        size_kb = (dest / fix["file"]).stat().st_size / 1024
        print(f"Created: {fix['file']} ({size_kb:.0f}KB) + {json_name}")

    print(f"\nTotal: {len(fixtures)} fixtures created")


if __name__ == "__main__":
    main()
