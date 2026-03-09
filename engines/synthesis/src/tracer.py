"""Synthesis engine — tracer bullet entry point.

Generates a knowledge entry from placed excerpts.
Simple strategy: concatenate excerpts into entry sections
with basic structure.
"""

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path


def process(input_path: Path, output_path: Path, config: dict) -> None:
    """Synthesize a knowledge entry from taxonomy placements.

    Args:
        input_path: Path to taxonomy output JSON (tree + placements).
        output_path: Path to write Entry JSON.
        config: Engine configuration (should include excerpt_stream_path,
                source_metadata_path).
    """
    input_path = Path(input_path)
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    taxonomy_out = json.loads(input_path.read_text(encoding="utf-8"))
    source_id = taxonomy_out["source_id"]
    placements = taxonomy_out["placements"]
    tree = taxonomy_out["tree"]

    # Load excerpts for content
    excerpt_path = config.get("excerpt_stream_path")
    excerpts_by_id = {}
    if excerpt_path and Path(excerpt_path).exists():
        es = json.loads(Path(excerpt_path).read_text(encoding="utf-8"))
        for e in es.get("excerpts", []):
            excerpts_by_id[e["excerpt_id"]] = e

    # Load source metadata for citation info
    source_meta_path = config.get("source_metadata_path")
    source_meta = {}
    if source_meta_path and Path(source_meta_path).exists():
        source_meta = json.loads(Path(source_meta_path).read_text(encoding="utf-8"))

    now_utc = datetime.now(timezone.utc).isoformat()

    # Group placements by leaf
    leaf_excerpts: dict[str, list[dict]] = {}
    for p in placements:
        leaf_id = p["confirmed_leaf"]
        excerpt = excerpts_by_id.get(p["excerpt_id"])
        if excerpt:
            leaf_excerpts.setdefault(leaf_id, []).append(excerpt)

    # Generate one entry per leaf
    entries = []
    for leaf_id, excerpts in leaf_excerpts.items():
        entry_id = f"entry_{hashlib.md5(leaf_id.encode()).hexdigest()[:8]}"

        # Build entry content
        all_texts = [e["primary_text"] for e in excerpts]
        definitions = [e for e in excerpts
                       if any(a_id for a_id in e.get("atom_ids", []) if "a000" in a_id)]

        # Core treatment: combine excerpt texts with basic structure
        core_parts = []
        for e in excerpts:
            core_parts.append(e["primary_text"])
        core_treatment = "\n\n".join(core_parts)

        # Build citations
        citations = []
        for i, e in enumerate(excerpts):
            phys = e.get("physical_pages", {})
            citations.append({
                "citation_id": f"cite_{i:03d}",
                "excerpt_id": e["excerpt_id"],
                "source_title": source_meta.get("title_arabic", "Unknown"),
                "author_name": source_meta.get("author", {}).get("name_arabic", "Unknown"),
                "tahqiq_editor": (source_meta.get("muhaqiq", {}) or {}).get("name_arabic"),
                "publisher": source_meta.get("publisher"),
                "volume": phys.get("volume", 1),
                "page_start": phys.get("start_page"),
                "page_end": phys.get("end_page"),
                "grounding_type": "library_excerpt",
                "formatted_citation": _format_citation(source_meta, phys),
            })

        # Scholarly positions (stub: one position from the commentary author)
        scholarly_positions = [{
            "position_id": "pos_001",
            "position_summary": f"Position of {source_meta.get('author', {}).get('name_arabic', 'the author')} on this topic as presented in the commentary.",
            "holders": [{
                "scholar_id": source_meta.get("author", {}).get("canonical_id"),
                "name": source_meta.get("author", {}).get("name_arabic", "Unknown"),
                "death_hijri": None,
                "school": None,
            }],
            "evidence_types": ["rational"],
            "evidence_refs": [],
            "mu_tamad_in_school": None,
            "is_consensus": False,
            "consensus_strength": None,
            "confidence": 0.5,
        }]

        # Staleness hash: hash of all excerpt IDs
        staleness_input = json.dumps(sorted(e["excerpt_id"] for e in excerpts))
        staleness_hash = hashlib.sha256(staleness_input.encode()).hexdigest()[:16]

        entry = {
            "entry_id": entry_id,
            "leaf_path": leaf_id,
            "science_id": "nahw",
            "school_group": None,
            "generated_utc": now_utc,
            "generator_config": {"engine": "synthesis_tracer_v0", "model": "none"},
            "source_excerpt_ids": [e["excerpt_id"] for e in excerpts],
            "content": {
                "prerequisites": "Knowledge of Arabic morphology basics.",
                "topic_situation": f"This entry covers the topic at {leaf_id} based on {len(excerpts)} excerpt(s) from {source_meta.get('title_arabic', 'the source')}.",
                "core_treatment": core_treatment,
                "scholarly_positions": scholarly_positions,
                "edge_cases": None,
                "common_misunderstandings": None,
                "khilaf_analysis": None,
                "temporal_narrative": None,
                "what_next": None,
                "analytical_layer": None,
                "critical_analysis": None,
            },
            "citations": citations,
            "staleness_hash": staleness_hash,
            "version": 1,
            "previous_version_id": None,
            "owner_constraints": [],
            "is_stale": False,
            "taxonomy_version": "tracer_v0",
            "generation_metadata": {
                "duration_seconds": 0.0,
                "total_excerpts_used": len(excerpts),
                "verified_excerpts": 0,
                "flagged_excerpts_referenced": 0,
                "unique_authors": 1,
                "unique_sources": 1,
                "temporal_span_hijri": None,
                "library_grounded_claim_count": len(excerpts),
                "llm_contributed_claim_count": 0,
                "deduplication_clusters_found": 0,
                "quality_assessment": {
                    "source_diversity": 0.0,
                    "temporal_coverage": 0.0,
                    "school_balance": 0.0,
                    "evidence_completeness": 0.3,
                    "citation_density": 1.0,
                    "confidence_floor": 0.5,
                    "overall_quality": 0.3,
                    "quality_narrative": "Tracer bullet output — single source, no LLM synthesis.",
                },
                "self_verification": None,
                "khilaf_disambiguation": None,
                "genealogy_chains": None,
                "gap_notes": None,
                "consensus_mappings": None,
            },
        }
        entries.append(entry)

    # Write the first entry (or all if multiple leaves)
    if len(entries) == 1:
        output_data = entries[0]
    else:
        output_data = {"entries": entries}

    output_path.write_text(
        json.dumps(output_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _format_citation(source_meta: dict, phys: dict) -> str:
    """Format a basic Arabic-style citation."""
    author = source_meta.get("author", {}).get("name_arabic", "")
    title = source_meta.get("title_arabic", "")
    muhaqiq = (source_meta.get("muhaqiq", {}) or {}).get("name_arabic", "")
    vol = phys.get("volume", "")
    page = phys.get("start_page", "")

    parts = []
    if author:
        parts.append(author)
    if title:
        parts.append(title)
    if muhaqiq:
        parts.append(f"تحقيق: {muhaqiq}")
    if vol and page:
        parts.append(f"{vol}/{page}")
    elif page:
        parts.append(str(page))

    return "، ".join(parts) if parts else "Unknown source"
