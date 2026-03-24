"""Pipeline Orchestrator: Phase 1 → Phase 2 → Phase 3 → Writer (SPEC §1.2).

Processes one source at a time. Loads config with cascade:
defaults → engine config.yaml → per-source overrides (§8.3).
"""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import instructor

from engines.excerpting.contracts import (
    ExcerptRecord,
    ExcerptingConfig,
)
from engines.excerpting.src.phase1_assembly import run_phase1
from engines.excerpting.src.phase2_classify import run_phase2a
from engines.excerpting.src.phase2_group import run_phase2b
from engines.excerpting.src.phase3_orchestrator import Phase3Result, run_phase3
from engines.excerpting.src.writer import (
    verify_gate_queue,
    write_excerpts,
    write_gate_queue,
)
from engines.normalization.contracts import NormalizedPackage

logger = logging.getLogger(__name__)


@dataclass
class ExcerptingResult:
    """Complete result of the excerpting pipeline.

    Attributes:
        excerpts: Final ExcerptRecords.
        gate_entries: Human gate entries written to gate_queue.jsonl.
        errors: All error codes emitted across all phases.
        timings: Per-phase timing in seconds.
        output_paths: Paths to written output files.
    """

    excerpts: list[ExcerptRecord] = field(default_factory=list)
    gate_entries: list[dict[str, object]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    timings: dict[str, float] = field(default_factory=dict)
    output_paths: dict[str, Path] = field(default_factory=dict)


def load_config(
    source_id: Optional[str] = None,
    engine_config_path: Optional[Path] = None,
) -> ExcerptingConfig:
    """Load configuration with cascade (§8.3).

    1. Built-in defaults (ExcerptingConfig field defaults).
    2. Engine config file (engines/excerpting/config.yaml).
    3. Per-source overrides (library/sources/{source_id}/excerpting_config.yaml).
    """
    # For now, return defaults. Config file loading is a later concern.
    return ExcerptingConfig()


def run_excerpting(
    package: NormalizedPackage,
    config: Optional[ExcerptingConfig] = None,
    output_dir: Optional[Path] = None,
    enrich_client: Optional[instructor.Instructor] = None,
    verify_client: Optional[instructor.Instructor] = None,
    escalation_client: Optional[instructor.Instructor] = None,
) -> ExcerptingResult:
    """Run the full excerpting pipeline on one source.

    Phase 1: Deterministic preprocessing → list[AssembledChunk]
    Phase 2: LLM classification + grouping → teaching units (requires enrich_client)
    Phase 3: Deterministic fields + LLM enrichment + consensus → ExcerptRecords
    Output: Write excerpts.jsonl + gate_queue.jsonl

    Args:
        package: NormalizedPackage from the normalization engine.
        config: Engine configuration (defaults if None).
        output_dir: Directory for output files. Defaults to tmp dir.
        enrich_client: Instructor client for Phase 2 + Phase 3 LLM calls.
        verify_client: Instructor client for Phase 3 consensus verification.
        escalation_client: Instructor client for 3-model escalation.

    Returns:
        ExcerptingResult with excerpts, gate entries, errors, and output paths.
    """
    if config is None:
        config = ExcerptingConfig()

    result = ExcerptingResult()
    source_id = package.manifest.source_id
    source_metadata: dict[str, str] = {"source_id": source_id}

    # ── Phase 1: Deterministic preprocessing ──────────────────────
    t0 = time.monotonic()
    try:
        chunks, _p1_validation = run_phase1(package, config)
    except Exception as exc:
        logger.error("Phase 1 failed for %s: %s", source_id, exc)
        result.errors.append(f"PHASE1_FATAL: {exc}")
        return result
    result.timings["phase1"] = time.monotonic() - t0
    logger.info(
        "Phase 1: %d chunks from %d content units (%.2fs).",
        len(chunks),
        len(package.content_units),
        result.timings["phase1"],
    )

    if not chunks:
        logger.warning("Phase 1 produced no chunks for %s.", source_id)
        return result

    # ── Phase 2: LLM classification + grouping ────────────────────
    if enrich_client is not None:
        t1 = time.monotonic()
        try:
            classified = run_phase2a(chunks, enrich_client, config)
            grouped = run_phase2b(chunks, classified, enrich_client, config)
        except Exception as exc:
            logger.error("Phase 2 failed for %s: %s", source_id, exc)
            result.errors.append(f"PHASE2_FATAL: {exc}")
            return result
        result.timings["phase2"] = time.monotonic() - t1
        logger.info(
            "Phase 2: %d chunks classified, %d grouped (%.2fs).",
            len(classified),
            len(grouped),
            result.timings["phase2"],
        )
    else:
        logger.warning(
            "No LLM client — Phase 2 skipped. Cannot produce teaching units."
        )
        result.errors.append("PHASE2_SKIPPED: no LLM client")
        return result

    # ── Phase 3: Enrichment pipeline ──────────────────────────────
    t2 = time.monotonic()
    phase3_result: Phase3Result = run_phase3(
        chunks=chunks,
        teaching_units=grouped,
        classified=classified,
        config=config,
        enrich_client=enrich_client,
        verify_client=verify_client,
        escalation_client=escalation_client,
        source_metadata=source_metadata,
    )
    result.excerpts = phase3_result.excerpts
    result.gate_entries = phase3_result.gate_entries
    result.errors.extend(phase3_result.errors)
    result.timings["phase3"] = time.monotonic() - t2
    result.timings.update(
        {f"phase3_{k}": v for k, v in phase3_result.timings.items()}
    )

    # ── Output: Write files ───────────────────────────────────────
    if output_dir is not None and result.excerpts:
        t3 = time.monotonic()

        excerpts_path = write_excerpts(result.excerpts, output_dir)
        result.output_paths["excerpts"] = excerpts_path

        if result.gate_entries:
            gate_path = write_gate_queue(result.gate_entries, output_dir)
            result.output_paths["gate_queue"] = gate_path

            # V-P3-7: Paranoid verification
            verify_gate_queue(result.gate_entries, gate_path)
        else:
            logger.info("No gate entries — skipping gate_queue.jsonl write.")

        result.timings["writer"] = time.monotonic() - t3

    logger.info(
        "Excerpting complete for %s: %d excerpts, %d gate entries, %d errors.",
        source_id,
        len(result.excerpts),
        len(result.gate_entries),
        len(result.errors),
    )
    return result


# Keep backward-compatible alias
process_source = run_excerpting
