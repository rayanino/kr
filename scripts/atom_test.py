"""Empirical validation harness for excerpting doctrine atoms.

Runs Phase 2 (classify + group) on a specific chunk from the v2 smoke data,
then checks teaching unit boundaries against expected patterns.

Usage:
    python scripts/atom_test.py --package taysir --chunk 5
    python scripts/atom_test.py --package ibn_aqil_v1 --chunk 0 --expected-units 8

Requires OPENROUTER_API_KEY in environment.
"""
from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

import instructor
import openai

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from engines.excerpting.contracts import (
    AssembledChunk,
    ContentFlags,
    AssemblyMetadata,
    ExcerptingConfig,
    SplitInfo,
)
from engines.normalization.contracts import TextLayerSegment
from engines.excerpting.src.phase2_classify import classify_chunk, normalize_offsets
from engines.excerpting.src.phase2_group import group_chunk

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger(__name__)


def load_chunk(package: str, chunk_index: int) -> AssembledChunk:
    """Load a specific chunk from v2 smoke data."""
    path = Path(f"integration_tests/smoke_api_v2/{package}/phase1_chunks.json")
    if not path.exists():
        raise FileNotFoundError(f"No phase1_chunks.json for package: {package}")

    with open(path) as f:
        chunks = json.load(f)

    if chunk_index >= len(chunks):
        raise IndexError(f"Chunk {chunk_index} out of range (max: {len(chunks) - 1})")

    cd = chunks[chunk_index]
    return AssembledChunk(
        chunk_id=cd["chunk_id"],
        source_id=cd["source_id"],
        div_id=cd["div_id"],
        div_path=cd["div_path"],
        assembled_text=cd["assembled_text"],
        word_count=cd["word_count"],
        total_tokens=cd["total_tokens"],
        text_layers=[TextLayerSegment(**l) for l in cd["text_layers"]],
        footnotes=cd["footnotes"],
        content_flags=ContentFlags(**cd["content_flags"]),
        physical_pages=cd["physical_pages"],
        structural_format=cd["structural_format"],
        heading_alignment_ok=cd["heading_alignment_ok"],
        assembly_metadata=AssemblyMetadata(**cd["assembly_metadata"]),
        merge_history=cd["merge_history"],
        split_info=SplitInfo(**cd["split_info"]) if cd.get("split_info") else None,
    )


def run_phase2(chunk: AssembledChunk) -> tuple[list, list]:
    """Run Phase 2a + 2b on a chunk. Returns (segments, teaching_units)."""
    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise EnvironmentError("OPENROUTER_API_KEY not set")

    client = instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON,
    )
    config = ExcerptingConfig()

    log.info("Phase 2a: Classifying...")
    raw_cls = classify_chunk(chunk, client, config)
    segments = normalize_offsets(
        raw_cls.segments, chunk.assembled_text, chunk.total_tokens
    )
    log.info(f"  {len(segments)} segments classified")

    log.info("Phase 2b: Grouping...")
    result = group_chunk(chunk, segments, client, config)
    units = result.teaching_units
    log.info(f"  {len(units)} teaching units formed")

    return segments, units


def analyze_units(
    chunk: AssembledChunk,
    segments: list,
    units: list,
) -> list[dict]:
    """Analyze each teaching unit for doctrine compliance."""
    words = chunk.assembled_text.split()
    results = []

    for i, unit in enumerate(units):
        unit_words = []
        for s in unit.segment_indices:
            if s < len(segments):
                unit_words.extend(
                    words[segments[s].start_word : segments[s].end_word + 1]
                )
        ut = " ".join(unit_words)
        funcs = [
            segments[s].scholarly_function.value
            for s in unit.segment_indices
            if s < len(segments)
        ]

        # Detect markers
        markers = []
        if any(x in ut for x in ["الحديث الأول", "الحديث الثاني", "الحديث الثالث"]):
            markers.append("HADITH_HEADER")
        if "غريب الحديث" in ut or "غريب" in ut[:50]:
            markers.append("GHARIB")
        if "المعنى الإجمالي" in ut:
            markers.append("MAANA")
        if "ما يؤخذ من الحديث" in ut or "فوائد" in ut[:30]:
            markers.append("FAWAID")
        if "اختلاف العلماء" in ut or "اختلف" in ut[:30]:
            markers.append("KHILAF")

        # EE-1 check
        ee1_status = None
        has_hadith = "HADITH_HEADER" in markers
        has_maana = "MAANA" in markers
        if has_hadith and has_maana:
            ee1_status = "PASS"
        elif has_maana and not has_hadith:
            ee1_status = "FAIL_ORPHANED_EXPLANATION"
        elif has_hadith and not has_maana:
            ee1_status = "CHECK_HADITH_WITHOUT_MAANA"

        results.append(
            {
                "tu_index": i,
                "segment_indices": unit.segment_indices,
                "functions": funcs,
                "self_containment": unit.self_containment.value,
                "primary_function": unit.primary_function.value,
                "word_count": len(unit_words),
                "text_preview": ut[:100],
                "markers": markers,
                "ee1_status": ee1_status,
                "notes": unit.self_containment_notes,
            }
        )

    return results


def main() -> None:
    parser = argparse.ArgumentParser(description="Excerpting atom empirical test")
    parser.add_argument("--package", required=True, help="Package name (e.g., taysir)")
    parser.add_argument("--chunk", type=int, required=True, help="Chunk index")
    parser.add_argument(
        "--expected-units", type=int, default=None, help="Expected unit count"
    )
    args = parser.parse_args()

    log.info(f"=== ATOM TEST: {args.package} chunk {args.chunk} ===\n")

    chunk = load_chunk(args.package, args.chunk)
    log.info(f"Chunk: {chunk.div_id}, {chunk.word_count} words\n")

    segments, units = run_phase2(chunk)
    results = analyze_units(chunk, segments, units)

    log.info(f"\n=== {len(results)} TEACHING UNITS ===\n")
    ee1_pass = 0
    ee1_fail = 0
    for r in results:
        log.info(
            f"TU-{r['tu_index']}: segs={r['segment_indices']} "
            f"funcs={r['functions']}"
        )
        log.info(
            f"  sc={r['self_containment']} primary={r['primary_function']} "
            f"words={r['word_count']}"
        )
        log.info(f"  text: {r['text_preview'][:80]}...")
        if r["markers"]:
            log.info(f"  markers: {r['markers']}")
        if r["ee1_status"]:
            status = r["ee1_status"]
            log.info(f"  EE-1: {status}")
            if status == "PASS":
                ee1_pass += 1
            elif "FAIL" in status:
                ee1_fail += 1
        if r["notes"]:
            log.info(f"  notes: {r['notes'][:80]}")
        log.info("")

    # Summary
    log.info("=== SUMMARY ===")
    log.info(f"Teaching units: {len(results)}")
    if args.expected_units:
        match = len(results) == args.expected_units
        log.info(
            f"Expected units: {args.expected_units} — {'MATCH' if match else 'MISMATCH'}"
        )
    log.info(f"EE-1: {ee1_pass} PASS, {ee1_fail} FAIL")

    sc_counts = {}
    for r in results:
        sc = r["self_containment"]
        sc_counts[sc] = sc_counts.get(sc, 0) + 1
    log.info(f"Self-containment: {sc_counts}")

    # Write results to JSON for comparison
    out_path = Path(
        f"integration_tests/smoke_api_v2/{args.package}/"
        f"atom_test_chunk{args.chunk}.json"
    )
    with open(out_path, "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    log.info(f"\nResults written to: {out_path}")


if __name__ == "__main__":
    main()
