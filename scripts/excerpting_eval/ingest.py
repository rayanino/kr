"""Artifact ingestion and canonical unit ledger construction.

Reads run directories and builds the normalized data structures
that all downstream analysis operates on.

No imports from engines/ or shared/.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

from .models import (
    CanonicalUnitKey,
    ChunkRecord,
    LLMTraceEntry,
    SemanticPhase,
    UnitLedgerEntry,
)

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Semantic phase inference from request content
# ---------------------------------------------------------------------------

# Each entry: (phase, signal_substrings).  Matched against the system message.
# Validated against actual data from integration_tests/run_20260328/:
#   enrich_0001 (taysir+ibn_aqil_v3) → "Classify each sentence" → CLASSIFICATION
#   enrich_0002 (taysir) → "group these classified segments" → GROUPING
#   enrich_0003 (taysir) → "enriching teaching units" → ENRICHMENT
#   verify_0001 (taysir) → "verifying metadata decisions" → VERIFICATION
_PHASE_SIGNALS: list[tuple[SemanticPhase, list[str]]] = [
    (SemanticPhase.CLASSIFICATION, [
        "Classify each sentence",
        "scholarly function",
    ]),
    (SemanticPhase.GROUPING, [
        "TEACHING UNITS",
        "group these classified segments",
    ]),
    (SemanticPhase.ENRICHMENT, [
        "enriching teaching units",
        "TOPIC KEYWORDS",
        "excerpt_topic",
    ]),
    (SemanticPhase.VERIFICATION, [
        "verifying metadata decisions",
        "VerificationItem",
    ]),
    (SemanticPhase.ESCALATION, [
        "adjudicate",
        "tiebreak",
    ]),
]

# Map client label prefix to the phase the runner *intended*.
# Used only for label_matches_content comparison, never for phase assignment.
_LABEL_TO_EXPECTED_PHASES: dict[str, set[SemanticPhase]] = {
    "enrich": {
        SemanticPhase.CLASSIFICATION,
        SemanticPhase.GROUPING,
        SemanticPhase.ENRICHMENT,
    },
    "verify": {SemanticPhase.VERIFICATION},
    "escalation": {SemanticPhase.ESCALATION},
}


def infer_semantic_phase(request: dict) -> SemanticPhase:
    """Infer semantic phase from request message content, not filename."""
    system_content = ""
    for msg in request.get("messages", []):
        if msg.get("role") == "system":
            system_content = msg.get("content", "")
            break

    if not system_content:
        return SemanticPhase.UNKNOWN

    scores: dict[SemanticPhase, int] = {}
    for phase, signals in _PHASE_SIGNALS:
        score = sum(1 for s in signals if s in system_content)
        if score > 0:
            scores[phase] = score

    if not scores:
        return SemanticPhase.UNKNOWN
    return max(scores, key=lambda p: scores[p])


def _extract_client_label(file_stem: str) -> str:
    """Extract client label from filename stem like 'enrich_0001'."""
    parts = file_stem.rsplit("_", 1)
    if len(parts) == 2 and parts[1].isdigit():
        return parts[0]
    return file_stem


def _label_matches(client_label: str, inferred: SemanticPhase) -> bool:
    """Check if the client label is consistent with inferred phase.

    The runner uses 'enrich' client for classification, grouping, AND
    enrichment calls.  So enrich + CLASSIFICATION is a valid match.
    """
    expected = _LABEL_TO_EXPECTED_PHASES.get(client_label, set())
    return inferred in expected or inferred == SemanticPhase.UNKNOWN


# ---------------------------------------------------------------------------
# File loading utilities
# ---------------------------------------------------------------------------

def load_json(path: Path) -> dict | list | None:
    """Load a JSON file. Returns None if file does not exist."""
    if not path.exists():
        return None
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return None
    return json.loads(text)


def load_jsonl(path: Path) -> list[dict]:
    """Load a JSONL file. Returns empty list if file does not exist."""
    if not path.exists():
        return []
    result = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            try:
                result.append(json.loads(line))
            except json.JSONDecodeError:
                logger.warning("Skipping malformed JSONL line in %s", path)
    return result


def load_processing_log(path: Path) -> dict:
    """Load processing_log.jsonl (which is actually a single JSON object)."""
    if not path.exists():
        return {}
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return {}
    # Runner writes a single JSON object on one line
    try:
        obj = json.loads(text)
        if isinstance(obj, dict):
            return obj
    except json.JSONDecodeError:
        pass
    # Fallback: try last line as JSONL
    for line in reversed(text.splitlines()):
        line = line.strip()
        if line:
            try:
                obj = json.loads(line)
                if isinstance(obj, dict):
                    return obj
            except json.JSONDecodeError:
                continue
    return {}


# ---------------------------------------------------------------------------
# Chunk index derivation
# ---------------------------------------------------------------------------

def build_chunk_index(
    chunks: list[dict],
) -> dict[str, tuple[str, str, int]]:
    """Map chunk_id → (source_id, div_id, chunk_index).

    For non-split chunks, chunk_index = 0.
    For split chunks, chunk_index = split_info.chunk_index.
    """
    result: dict[str, tuple[str, str, int]] = {}
    for chunk in chunks:
        cid = chunk["chunk_id"]
        sid = chunk["source_id"]
        did = chunk["div_id"]
        si = chunk.get("split_info")
        ci = si["chunk_index"] if si else 0
        result[cid] = (sid, did, ci)
    return result


# ---------------------------------------------------------------------------
# Unit ledger construction
# ---------------------------------------------------------------------------

def build_unit_ledger(
    run_dir: Path,
    chunks: list[dict],
    chunk_index_map: dict[str, tuple[str, str, int]],
) -> tuple[dict[CanonicalUnitKey, UnitLedgerEntry], list[ChunkRecord]]:
    """Build the canonical unit ledger from run directory artifacts.

    Returns (ledger, chunk_records).

    Four-pass algorithm:
      Pass 1: Phase 1 chunks → ChunkRecord list
      Pass 2: Phase 2a classifications → mark chunks
      Pass 3: Phase 2b groupings → create UnitLedgerEntry per unit
      Pass 4: excerpts.jsonl → match or create entries
    """
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry] = {}
    chunk_records: dict[str, ChunkRecord] = {}

    # --- Pass 1: Phase 1 chunks ---
    for chunk in chunks:
        cid = chunk["chunk_id"]
        sid, did, ci = chunk_index_map[cid]
        chunk_records[cid] = ChunkRecord(
            chunk_id=cid,
            source_id=sid,
            div_id=did,
            chunk_index=ci,
            word_count=chunk.get("word_count", 0),
            total_tokens=chunk.get("total_tokens", 0),
            phase1_present=True,
        )

    # --- Pass 2: Phase 2a classifications ---
    p2a_dir = run_dir / "phase2a_classifications"
    if p2a_dir.is_dir():
        for p2a_file in sorted(p2a_dir.glob("chunk_*.json")):
            cid = p2a_file.stem.removeprefix("chunk_")
            if cid in chunk_records:
                chunk_records[cid].phase2a_present = True
                segments = load_json(p2a_file)
                if isinstance(segments, list):
                    # Segment count stored for metrics
                    pass  # count available via len(segments)

    # --- Pass 3: Phase 2b groupings ---
    p2b_dir = run_dir / "phase2b_groupings"
    if p2b_dir.is_dir():
        for p2b_file in sorted(p2b_dir.glob("chunk_*.json")):
            cid = p2b_file.stem.removeprefix("chunk_")
            if cid not in chunk_index_map:
                logger.warning(
                    "Phase2b file %s references unknown chunk_id %s",
                    p2b_file.name, cid,
                )
                continue

            sid, did, ci = chunk_index_map[cid]
            units = load_json(p2b_file)
            if not isinstance(units, list):
                continue

            if cid in chunk_records:
                chunk_records[cid].phase2b_present = True
                chunk_records[cid].phase2b_unit_count = len(units)

            for unit in units:
                ui = unit["unit_index"]
                key = CanonicalUnitKey(
                    source_id=sid, div_id=did,
                    chunk_index=ci, unit_index=ui,
                )
                ledger[key] = UnitLedgerEntry(
                    key=key,
                    chunk_id=cid,
                    has_phase2b=True,
                    phase2b_data=unit,
                )

    # --- Pass 4: Excerpts ---
    excerpts = load_jsonl(run_dir / "excerpts.jsonl")
    # Track excerpt count per chunk
    chunk_excerpt_counts: dict[str, int] = {}

    for exc in excerpts:
        sid = exc["source_id"]
        did = exc["div_id"]
        ci = exc["chunk_index"]
        ui = exc["unit_index"]
        key = CanonicalUnitKey(
            source_id=sid, div_id=did,
            chunk_index=ci, unit_index=ui,
        )

        if key in ledger:
            ledger[key].has_excerpt = True
            ledger[key].excerpt_data = exc
        else:
            # Excerpt exists without a phase2b grouping entry —
            # possible lineage orphan or ledger construction gap.
            # Determine chunk_id from any matching chunk
            cid = _find_chunk_id(chunk_index_map, sid, did, ci)
            ledger[key] = UnitLedgerEntry(
                key=key,
                chunk_id=cid or f"unknown_{did}_{ci}",
                has_phase2b=False,
                has_excerpt=True,
                excerpt_data=exc,
            )

        # Count excerpts per chunk for ChunkRecord
        cid_for_count = _find_chunk_id(chunk_index_map, sid, did, ci)
        if cid_for_count:
            chunk_excerpt_counts[cid_for_count] = (
                chunk_excerpt_counts.get(cid_for_count, 0) + 1
            )

    # Update chunk records with excerpt counts
    for cid, count in chunk_excerpt_counts.items():
        if cid in chunk_records:
            chunk_records[cid].excerpt_count = count

    return ledger, list(chunk_records.values())


def _find_chunk_id(
    chunk_index_map: dict[str, tuple[str, str, int]],
    source_id: str,
    div_id: str,
    chunk_index: int,
) -> str | None:
    """Reverse lookup: find chunk_id from canonical key components."""
    for cid, (sid, did, ci) in chunk_index_map.items():
        if sid == source_id and did == div_id and ci == chunk_index:
            return cid
    return None


# ---------------------------------------------------------------------------
# LLM trace loading
# ---------------------------------------------------------------------------

def load_llm_traces(run_dir: Path) -> list[LLMTraceEntry]:
    """Load and annotate all raw LLM request/response pairs."""
    req_dir = run_dir / "raw_llm_requests"
    resp_dir = run_dir / "raw_llm_responses"
    traces: list[LLMTraceEntry] = []

    if not req_dir.is_dir():
        return traces

    for req_file in sorted(req_dir.glob("*.json")):
        stem = req_file.stem
        client_label = _extract_client_label(stem)

        # Load request — use explicit semantic_phase if present (C3),
        # fall back to content-based inference for old run directories
        request = load_json(req_file)
        if not isinstance(request, dict):
            continue
        explicit_phase = request.get("semantic_phase")
        if explicit_phase:
            try:
                inferred = SemanticPhase(explicit_phase)
            except ValueError:
                inferred = infer_semantic_phase(request)
        else:
            inferred = infer_semantic_phase(request)
        matches = _label_matches(client_label, inferred)

        # L-001: Read chunk_id when present (post-L-001 runs).
        explicit_chunk_id = request.get("chunk_id")

        # Load response
        resp_file = resp_dir / f"{stem}.json" if resp_dir.is_dir() else None
        response: dict | None = None
        if resp_file and resp_file.exists():
            response = load_json(resp_file)
            if not isinstance(response, dict):
                response = None

        # Load error file
        err_file = resp_dir / f"{stem}_error.json" if resp_dir.is_dir() else None
        error_data: dict | None = None
        if err_file and err_file.exists():
            error_data = load_json(err_file)
            if not isinstance(error_data, dict):
                error_data = None

        # Extract response fields
        finish_reason = None
        model = request.get("model")
        latency = None
        tokens_in = None
        tokens_out = None
        cost = None

        if response:
            finish_reason = response.get("finish_reason")
            latency = response.get("latency_seconds")
            usage = response.get("usage", {})
            if isinstance(usage, dict):
                tokens_in = usage.get("prompt_tokens") or usage.get("input_tokens")
                tokens_out = usage.get("completion_tokens") or usage.get("output_tokens")
                cost = usage.get("cost")

        traces.append(LLMTraceEntry(
            file_stem=stem,
            client_label=client_label,
            inferred_phase=inferred,
            label_matches_content=matches,
            finish_reason=finish_reason,
            model=model,
            latency_seconds=latency,
            tokens_in=tokens_in,
            tokens_out=tokens_out,
            cost=cost,
            has_error=error_data is not None,
            error_type=error_data.get("error_type") if error_data else None,
            chunk_id=explicit_chunk_id if isinstance(explicit_chunk_id, str) else None,
        ))

    return traces


# ---------------------------------------------------------------------------
# Full book run loader
# ---------------------------------------------------------------------------

def load_book_run(run_dir: Path) -> dict:
    """Load all artifacts from a single book run directory.

    Returns a dict with keys:
        book_name, source_id, chunks, chunk_index_map, ledger,
        chunk_records, traces, processing_log, timing, run_metadata,
        excerpts, raw_excerpt_count
    """
    run_dir = Path(run_dir)
    book_name = run_dir.name

    # Phase 1 chunks
    chunks_data = load_json(run_dir / "phase1_chunks.json")
    chunks: list[dict] = chunks_data if isinstance(chunks_data, list) else []

    # Derive source_id
    source_id = ""
    if chunks:
        source_id = chunks[0].get("source_id", "")

    # Processing log and metadata
    processing_log = load_processing_log(run_dir / "processing_log.jsonl")
    if not source_id and processing_log:
        source_id = processing_log.get("source_id", "")

    timing_data = load_json(run_dir / "timing.json")
    timing: dict = timing_data if isinstance(timing_data, dict) else {}
    # Merge timings from processing_log if timing.json is absent
    if not timing and processing_log.get("timings"):
        timing = processing_log["timings"]

    run_metadata_data = load_json(run_dir / "run_metadata.json")
    run_metadata: dict = (
        run_metadata_data if isinstance(run_metadata_data, dict) else {}
    )

    # Build chunk index and ledger
    chunk_index_map = build_chunk_index(chunks)
    ledger, chunk_records = build_unit_ledger(
        run_dir, chunks, chunk_index_map,
    )

    # Load traces
    traces = load_llm_traces(run_dir)

    # Load raw excerpts for count
    excerpts = load_jsonl(run_dir / "excerpts.jsonl")

    # C1: Load validation drops (if runner produced them)
    validation_drops = load_jsonl(run_dir / "validation_drops.jsonl")

    # C2: Load phase failure ledgers (if runner produced them)
    phase2a_failures = load_jsonl(run_dir / "phase2a_failures.jsonl")
    phase2b_failures = load_jsonl(run_dir / "phase2b_failures.jsonl")

    return {
        "book_name": book_name,
        "source_id": source_id,
        "run_dir": run_dir,
        "chunks": chunks,
        "chunk_index_map": chunk_index_map,
        "ledger": ledger,
        "chunk_records": chunk_records,
        "traces": traces,
        "processing_log": processing_log,
        "timing": timing,
        "run_metadata": run_metadata,
        "excerpts": excerpts,
        "raw_excerpt_count": len(excerpts),
        "validation_drops": validation_drops,
        "phase2a_failures": phase2a_failures,
        "phase2b_failures": phase2b_failures,
    }
