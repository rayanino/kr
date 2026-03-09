"""Passaging engine — tracer bullet entry point.

Groups content units from NormalizedPackage into passages.
Simple strategy: one content unit = one passage.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


_FIDELITY_SCORES = {"high": 0.95, "medium": 0.75, "low": 0.50, "very_low": 0.25}


def _fidelity_to_float(val) -> float:
    """Convert TextFidelityLevel string or float to float."""
    if isinstance(val, (int, float)):
        return float(val)
    return _FIDELITY_SCORES.get(str(val), 0.75)


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Split normalized content into passages.

    Args:
        input_path: Path to NormalizedPackage JSON.
        output_path: Path to write PassageStream JSON.
        config: Engine configuration.
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    package = json.loads(input_path.read_text(encoding="utf-8"))
    manifest = package["manifest"]
    content_units = package["content_units"]
    source_id = manifest["source_id"]

    passages = []
    for i, unit in enumerate(content_units):
        passage_id = f"{source_id}_p{i:04d}"
        page = unit["physical_page"]

        # Combine all text layers into passage text
        passage_text = unit["primary_text"]

        # Convert text layers
        text_layers = []
        for tl in unit.get("text_layers", []):
            text_layers.append({
                "layer_type": tl["layer_type"],
                "author_canonical_id": tl.get("author_canonical_id"),
                "start": tl["start"],
                "end": tl["end"],
                "confidence": tl.get("confidence", 0.9),
            })

        # Convert footnotes
        footnotes = []
        for fn in unit.get("footnotes", []):
            footnotes.append({
                "ref_marker": fn["ref_marker"],
                "text": fn["text"],
                "footnote_type": fn.get("footnote_type", "tahqiq_editor"),
                "confidence": fn.get("confidence", 0.85),
                "source_unit_index": unit["unit_index"],
            })

        # Build division path from division_tree in manifest
        division_path = []
        for div in manifest.get("division_tree", []):
            if div["start_unit_index"] <= i <= div["end_unit_index"]:
                division_path.append({
                    "div_id": f"div_{div['start_unit_index']}",
                    "heading_text": div["heading_text"],
                    "heading_level": div["heading_level"],
                })

        markers = unit.get("structural_markers", {})
        content_flags = unit.get("content_flags", {})
        fidelity = unit.get("text_fidelity", {})

        word_count = len(passage_text.split())
        char_count = len(passage_text)

        passage = {
            "schema_version": "0.1.0",
            "passage_id": passage_id,
            "source_id": source_id,
            "sequence_index": i,
            "passage_text": passage_text,
            "text_layers": text_layers,
            "footnotes": footnotes,
            "division_path": division_path,
            "division_ids": [dp["div_id"] for dp in division_path] if division_path else [f"div_root_{source_id}"],
            "heading_text": markers.get("heading_text"),
            "heading_source": "division_tree" if markers.get("heading_detected") else None,
            "unit_range": {
                "start": unit["unit_index"],
                "end": unit["unit_index"],
            },
            "physical_pages": {
                "volume": page["volume"],
                "start_page_display": page["page_number_display"],
                "end_page_display": page["page_number_display"],
                "start_page_int": page["page_number_int"],
                "end_page_int": page["page_number_int"],
                "page_count": 1,
            },
            "structural_format": "commentary_unit" if text_layers and any(
                tl["layer_type"] == "sharh" for tl in text_layers
            ) else "prose",
            "verse_info": None,
            "content_flags": {
                "has_verse": content_flags.get("has_verse", False),
                "has_table": content_flags.get("has_table", False),
                "has_quran_citation": content_flags.get("has_quran_citation", False),
                "has_hadith_citation": content_flags.get("has_hadith_citation", False),
            },
            "text_fidelity": {
                "min_score": "high",
                "mean_score": _fidelity_to_float(fidelity.get("score", "high")),
                "pages_with_warnings": 0,
            },
            "sizing": {
                "action": "direct",
                "word_count": word_count,
                "char_count": char_count,
                "notes": None,
            },
            "predecessor_id": f"{source_id}_p{i - 1:04d}" if i > 0 else None,
            "successor_id": f"{source_id}_p{i + 1:04d}" if i < len(content_units) - 1 else None,
            "review_flags": [],
            "quality_prediction": None,
            "commentary_alignment": None,
            "adaptive_params": None,
            "argument_structure": None,
            "completeness_forecast": None,
        }
        passages.append(passage)

    stream = {
        "source_id": source_id,
        "passages": passages,
    }

    output_path.write_text(
        json.dumps(stream, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
