"""Excerpting engine — tracer bullet entry point.

Groups atoms into self-contained scholarly excerpts.
Simple strategy: group all atoms from same passage into one excerpt.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Extract excerpts from atom stream.

    Args:
        input_path: Path to AtomStream JSON.
        output_path: Path to write ExcerptStream JSON.
        config: Engine configuration (should include source_metadata_path).
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    atom_stream = json.loads(input_path.read_text(encoding="utf-8"))
    source_id = atom_stream["source_id"]
    atoms = atom_stream["atoms"]

    # Load passage data if available for page info
    passage_path = config.get("passage_stream_path")
    passage_map = {}
    if passage_path and Path(passage_path).exists():
        ps = json.loads(Path(passage_path).read_text(encoding="utf-8"))
        for p in ps.get("passages", []):
            passage_map[p["passage_id"]] = p

    # Group atoms by passage_id
    passage_atoms: dict[str, list[dict]] = {}
    for atom in atoms:
        pid = atom["passage_id"]
        passage_atoms.setdefault(pid, []).append(atom)

    now_utc = datetime.now(timezone.utc).isoformat()
    excerpts = []
    for i, (passage_id, p_atoms) in enumerate(passage_atoms.items()):
        excerpt_id = f"{source_id}_e{i:04d}"

        # Combine atom texts
        primary_text = " ".join(a["atom_text"] for a in p_atoms)
        atom_ids = [a["atom_id"] for a in p_atoms]

        # Determine primary layer
        layers = [a["source_layer"] for a in p_atoms]
        primary_layer = max(set(layers), key=layers.count) if layers else "sharh"

        # Get passage info for page numbers
        passage_info = passage_map.get(passage_id, {})
        phys = passage_info.get("physical_pages", {})

        # Guess topic from first atom or heading
        topic = "General"
        for a in p_atoms:
            if a.get("scholarly_function") == "definition":
                topic = f"Definition: {a['atom_text'][:50]}"
                break
            if a.get("scholarly_function") == "rule_statement":
                topic = f"Rule: {a['atom_text'][:50]}"
                break
        if topic == "General" and passage_info.get("heading_text"):
            topic = passage_info["heading_text"]

        excerpt = {
            "schema_version": "0.1.0",
            "excerpt_id": excerpt_id,
            "source_id": source_id,
            "passage_id": passage_id,
            "lifecycle_stage": "draft",
            "atom_ids": atom_ids,
            "core_atom_ids": atom_ids,
            "context_atom_ids": [],
            "primary_text": primary_text,
            "derived_normalized_text": primary_text,
            "primary_author_id": None,
            "primary_author_name": None,
            "quoted_scholars": [],
            "source_layer": primary_layer,
            "excerpt_topic": topic,
            "proposed_leaf": "nahw/kalaam",  # Hardcoded for tracer
            "proposed_leaf_confidence": 0.5,
            "science_id": "nahw",
            "school": None,
            "school_confidence": None,
            "content_types": ["teaching"],
            "excerpt_kind": "teaching",
            "evidence_refs": [],
            "takhrij_data": [],
            "terminology_variants": [],
            "self_containment_score": 0.7,
            "self_containment_notes": "Tracer bullet: passage-level grouping",
            "excerpt_confidence": 0.6,
            "physical_pages": {
                "volume": phys.get("volume", 1),
                "start_page": str(phys.get("start_page_int", 1)),
                "end_page": str(phys.get("end_page_int", 1)),
            },
            "verse_numbers": None,
            "division_path": passage_info.get("division_ids", []),
            "review_flags": ["tracer_bullet_stub"],
            "processing_metadata": {
                "engine_version": "tracer_v0",
                "model_used": "none",
                "consensus_used": False,
                "processing_timestamp": now_utc,
            },
            # Deferred fields — null
            "argument_role": None,
            "argument_role_confidence": None,
            "argument_map": None,
            "semantic_duplicates": None,
            "argument_completeness": None,
            "dialogue_links": None,
            "repair_suggestions": None,
            "masala_analysis": None,
            "evidence_chain": None,
            "resonance_links": None,
        }
        excerpts.append(excerpt)

    excerpt_stream = {
        "source_id": source_id,
        "excerpts": excerpts,
    }

    output_path.write_text(
        json.dumps(excerpt_stream, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
