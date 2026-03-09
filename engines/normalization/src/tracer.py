"""Normalization engine — tracer bullet entry point.

Parses Shamela HTML content.html into NormalizedPackage JSON.
This stub produces REAL normalized output — actual Arabic text
with layer separation, page boundaries, and structural markers.
"""

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Normalize a source into a NormalizedPackage JSON.

    Args:
        input_path: Path to the SourceMetadata JSON from the source engine.
        output_path: Path to write the NormalizedPackage JSON.
        config: Engine configuration.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Read source metadata to find frozen files
    source_meta = json.loads(input_path.read_text(encoding="utf-8"))
    source_id = source_meta["source_id"]
    frozen_path = Path(source_meta["frozen_path"])

    # Parse content.html
    content_html = (frozen_path / "content.html").read_text(encoding="utf-8")
    content_units = _parse_content_html(content_html, source_id)

    # Build division tree from chapter headings
    division_tree = _build_division_tree(content_units)

    # Build layer map
    layer_map = _build_layer_map(content_units, source_meta)

    # Build manifest
    now_utc = datetime.now(timezone.utc).isoformat()
    manifest = {
        "schema_version": "0.1.0",
        "source_id": source_id,
        "normalizer_id": "shamela_html_tracer_v0",
        "normalization_utc": now_utc,
        "division_tree": division_tree,
        "layer_map": layer_map,
        "structural_format": source_meta.get("structural_format", "commentary"),
        "text_fidelity_summary": {
            "mean_ocr_confidence": 0.95,
            "character_level_fidelity_estimate": 0.98,
            "pages_with_warnings": 0,
            "total_pages": len(content_units),
        },
        "verse_detection": any(
            u.get("content_flags", {}).get("has_verse", False)
            for u in content_units
        ),
        "verse_numbering_scheme": None,
        "total_content_units": len(content_units),
        "quality_report": {
            "division_count_by_tier": {"confirmed": len(division_tree)},
            "layer_transition_count": sum(
                len(u.get("text_layers", [])) for u in content_units
            ),
            "pages_with_warnings": 0,
            "high_fidelity_pct": 1.0,
            "unclassified_footnote_count": 0,
            "overall_confidence": "high",
        },
        "normalization_warnings": [],
        "content_census": None,
        "tahqiq_topology": None,
        "layer_fingerprints": None,
        "discourse_flow_summary": None,
    }

    package = {
        "manifest": manifest,
        "content_units": content_units,
    }

    output_path.write_text(
        json.dumps(package, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _parse_content_html(html: str, source_id: str) -> list[dict]:
    """Parse Shamela-style content.html into ContentUnit dicts."""
    content_units = []
    unit_index = 0

    # Find all page divs
    page_pattern = re.compile(
        r'<div\s+class="page"\s+id="(v\d+p\d+)">(.*?)</div>\s*(?=<div\s+class="page"|</div>\s*</div>)',
        re.DOTALL,
    )

    for page_match in page_pattern.finditer(html):
        page_id = page_match.group(1)
        page_content = page_match.group(2)

        # Extract volume and page number
        vol_match = re.search(r'<span class="vol">(\d+)</span>', page_content)
        pg_match = re.search(r'<span class="pg">(\d+)</span>', page_content)
        volume = int(vol_match.group(1)) if vol_match else 1
        page_num = int(pg_match.group(1)) if pg_match else unit_index + 1

        # Extract text segments by class
        matn_texts = _extract_class_texts(page_content, "matn")
        sharh_texts = _extract_class_texts(page_content, "sharh")
        footnote_texts = _extract_class_texts(page_content, "footnote")

        # Build primary text (all text in reading order)
        all_texts = matn_texts + sharh_texts
        primary_text = "\n".join(all_texts)

        # Build text layer segments
        text_layers = []
        char_offset = 0
        for mt in matn_texts:
            text_layers.append({
                "layer_type": "matn",
                "author_canonical_id": None,  # Will be inferred
                "start": char_offset,
                "end": char_offset + len(mt),
                "confidence": 0.95,
            })
            char_offset += len(mt) + 1  # +1 for newline

        for st in sharh_texts:
            text_layers.append({
                "layer_type": "sharh",
                "author_canonical_id": None,
                "start": char_offset,
                "end": char_offset + len(st),
                "confidence": 0.95,
            })
            char_offset += len(st) + 1

        # Build footnotes
        footnotes = []
        for i, ft in enumerate(footnote_texts):
            # Extract footnote number if present
            fn_match = re.match(r"<sup>(\d+)</sup>\s*(.*)", ft, re.DOTALL)
            if fn_match:
                ref_marker = fn_match.group(1)
                fn_text = _strip_tags(fn_match.group(2)).strip()
            else:
                ref_marker = str(i + 1)
                fn_text = _strip_tags(ft).strip()

            footnotes.append({
                "ref_marker": ref_marker,
                "text": fn_text,
                "footnote_type": "tahqiq_editor",
                "confidence": 0.85,
                "secondary_types": [],
                "variant_data": None,
                "takhrij_data": None,
                "bio_data": None,
                "correction_data": None,
            })

        # Detect heading
        heading_match = re.search(r"<h\d>(.*?)</h\d>", page_content, re.DOTALL)
        heading_text = _strip_tags(heading_match.group(1)).strip() if heading_match else None

        # Check for verse (matn class with prosodic pattern)
        has_verse = any("…" in t or re.search(r"[\u064B-\u065F]{2,}", t) for t in matn_texts)

        content_unit = {
            "schema_version": "0.1.0",
            "source_id": source_id,
            "unit_index": unit_index,
            "physical_page": {
                "volume": volume,
                "page_number_display": str(page_num),
                "page_number_int": page_num,
            },
            "primary_text": primary_text,
            "text_layers": text_layers,
            "footnotes": footnotes,
            "structural_markers": {
                "heading_detected": heading_text is not None,
                "heading_text": heading_text,
                "heading_level": 2 if heading_text else None,
                "heading_detection_method": "html_tagged" if heading_text else None,
                "heading_confidence": "confirmed" if heading_text else None,
            },
            "verse_info": None,
            "content_flags": {
                "has_verse": has_verse,
                "has_table": False,
                "has_quran_citation": False,
                "has_hadith_citation": False,
                "is_toc_page": False,
                "is_index_page": False,
                "is_blank": len(primary_text.strip()) == 0,
            },
            "text_fidelity": {
                "score": "high",
                "ocr_confidence": None,
                "warnings": [],
            },
            "boundary_continuity": None,
            "discourse_flow": None,
        }
        content_units.append(content_unit)
        unit_index += 1

    # If regex found no pages, try a simpler approach
    if not content_units:
        content_units = _fallback_parse(html, source_id)

    return content_units


def _fallback_parse(html: str, source_id: str) -> list[dict]:
    """Simpler parsing when the page regex doesn't match."""
    # Split on page div openings
    parts = re.split(r'<div\s+class="page"[^>]*>', html)
    content_units = []

    for i, part in enumerate(parts[1:], start=0):  # skip before first page
        # Close the div
        end_idx = part.rfind("</div>")
        if end_idx > 0:
            part = part[:end_idx]

        # Extract vol/pg
        vol_match = re.search(r'<span class="vol">(\d+)</span>', part)
        pg_match = re.search(r'<span class="pg">(\d+)</span>', part)
        volume = int(vol_match.group(1)) if vol_match else 1
        page_num = int(pg_match.group(1)) if pg_match else i + 1

        matn_texts = _extract_class_texts(part, "matn")
        sharh_texts = _extract_class_texts(part, "sharh")
        footnote_texts = _extract_class_texts(part, "footnote")

        primary_text = "\n".join(matn_texts + sharh_texts)

        text_layers = []
        offset = 0
        for mt in matn_texts:
            text_layers.append({
                "layer_type": "matn",
                "author_canonical_id": None,
                "start": offset,
                "end": offset + len(mt),
                "confidence": 0.95,
            })
            offset += len(mt) + 1
        for st in sharh_texts:
            text_layers.append({
                "layer_type": "sharh",
                "author_canonical_id": None,
                "start": offset,
                "end": offset + len(st),
                "confidence": 0.95,
            })
            offset += len(st) + 1

        footnotes = []
        for j, ft in enumerate(footnote_texts):
            fn_match = re.match(r"<sup>(\d+)</sup>\s*(.*)", ft, re.DOTALL)
            if fn_match:
                footnotes.append({
                    "ref_marker": fn_match.group(1),
                    "text": _strip_tags(fn_match.group(2)).strip(),
                    "footnote_type": "tahqiq_editor",
                    "confidence": 0.85,
                    "secondary_types": [], "variant_data": None,
                    "takhrij_data": None, "bio_data": None, "correction_data": None,
                })
            else:
                footnotes.append({
                    "ref_marker": str(j + 1),
                    "text": _strip_tags(ft).strip(),
                    "footnote_type": "tahqiq_editor",
                    "confidence": 0.85,
                    "secondary_types": [], "variant_data": None,
                    "takhrij_data": None, "bio_data": None, "correction_data": None,
                })

        heading_match = re.search(r"<h\d>(.*?)</h\d>", part, re.DOTALL)
        heading_text = _strip_tags(heading_match.group(1)).strip() if heading_match else None

        content_units.append({
            "schema_version": "0.1.0",
            "source_id": source_id,
            "unit_index": i,
            "physical_page": {
                "volume": volume,
                "page_number_display": str(page_num),
                "page_number_int": page_num,
            },
            "primary_text": primary_text,
            "text_layers": text_layers,
            "footnotes": footnotes,
            "structural_markers": {
                "heading_detected": heading_text is not None,
                "heading_text": heading_text,
                "heading_level": 2 if heading_text else None,
                "heading_detection_method": "html_tagged" if heading_text else None,
                "heading_confidence": "confirmed" if heading_text else None,
            },
            "verse_info": None,
            "content_flags": {
                "has_verse": False,
                "has_table": False,
                "has_quran_citation": False,
                "has_hadith_citation": False,
                "is_toc_page": False,
                "is_index_page": False,
                "is_blank": len(primary_text.strip()) == 0,
            },
            "text_fidelity": {
                "score": "high",
                "ocr_confidence": None,
                "warnings": [],
            },
            "boundary_continuity": None,
            "discourse_flow": None,
        })

    return content_units


def _extract_class_texts(html: str, css_class: str) -> list[str]:
    """Extract text content from all elements with a given CSS class."""
    pattern = re.compile(
        rf'<p\s+class="{css_class}">(.*?)</p>',
        re.DOTALL,
    )
    results = []
    for m in pattern.finditer(html):
        text = _strip_tags(m.group(1)).strip()
        if text:
            results.append(text)
    # Also check raw content inside the tag (for footnotes with sup tags)
    if not results:
        pattern2 = re.compile(
            rf'<p\s+class="{css_class}">(.*?)</p>',
            re.DOTALL,
        )
        for m in pattern2.finditer(html):
            raw = m.group(1).strip()
            if raw:
                results.append(raw)  # Keep HTML for footnote processing
    return results


def _build_division_tree(content_units: list[dict]) -> list[dict]:
    """Build a division tree from headings found in content units."""
    divisions = []
    for unit in content_units:
        markers = unit.get("structural_markers", {})
        if markers.get("heading_detected"):
            divisions.append({
                "heading_text": markers["heading_text"],
                "heading_level": markers.get("heading_level", 2),
                "start_unit_index": unit["unit_index"],
                "end_unit_index": unit["unit_index"],  # Updated below
                "detection_method": markers.get("heading_detection_method", "html_tagged"),
                "confidence": markers.get("heading_confidence", "confirmed"),
                "children": [],
            })

    # Update end_unit_index to span to next heading
    for i, div in enumerate(divisions):
        if i + 1 < len(divisions):
            div["end_unit_index"] = divisions[i + 1]["start_unit_index"] - 1
        else:
            div["end_unit_index"] = len(content_units) - 1

    return divisions


def _build_layer_map(content_units: list[dict], source_meta: dict) -> list[dict]:
    """Build a layer map from detected text layers."""
    layer_types_seen = set()
    for unit in content_units:
        for layer in unit.get("text_layers", []):
            layer_types_seen.add(layer["layer_type"])

    layer_map = []
    source_layers = source_meta.get("text_layers", [])
    for lt in sorted(layer_types_seen):
        author_id = None
        for sl in source_layers:
            if sl.get("layer_type") == lt:
                author_id = sl.get("author_canonical_id")
                break
        layer_map.append({
            "layer_type": lt,
            "author_canonical_id": author_id,
            "author_name_arabic": None,
            "detection_confidence": 0.95,
        })

    return layer_map


def _strip_tags(html: str) -> str:
    """Remove HTML tags from a string."""
    return re.sub(r"<[^>]+>", "", html)
