"""Anomaly detection, metric computation, and structural status determination.

All anomaly detectors operate on the canonical unit ledger and trace data.
Only decision-grade structural anomalies can set STRUCTURAL_FAIL/CONCERN.
Review-risk and descriptive metrics NEVER determine structural status.
"""
from __future__ import annotations

import logging
from collections import Counter
from typing import Any

from .models import (
    Anomaly,
    BookAnalysisResult,
    CanonicalUnitKey,
    ChunkRecord,
    EvidenceBasis,
    LLMTraceEntry,
    MetricTier,
    ReviewCandidate,
    StructuralStatus,
    TieredMetric,
    UnitLedgerEntry,
)

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Anomaly detection
# ---------------------------------------------------------------------------

def detect_unit_loss(
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
    processing_log: dict,
    run_dir_str: str,
    validation_drops: list[dict] | None = None,
) -> list[Anomaly]:
    """Detect grouped units that did not survive into final excerpts."""
    lost = [
        entry for entry in ledger.values()
        if entry.has_phase2b and not entry.has_excerpt
    ]
    if not lost:
        return []

    errors = processing_log.get("errors", [])
    v002_count = errors.count("EX-V-002") if isinstance(errors, list) else 0

    lost_indices = sorted(e.key.unit_index for e in lost)
    facts = [
        f"{len(lost)} grouped unit(s) missing from final excerpts",
        f"Missing unit indices: {lost_indices}",
    ]

    severity = "structural_fail"

    # C1: When validation_drops.jsonl is available, we know exactly which
    # units were dropped — upgrade evidence from inferred to observed.
    if validation_drops:
        dropped_unit_indices = {
            idx for idx in (d.get("unit_index") for d in validation_drops)
            if idx is not None
        }
        if all(e.key.unit_index in dropped_unit_indices for e in lost):
            evidence_basis = EvidenceBasis.OBSERVED
            interpretation = (
                f"All {len(lost)} lost unit(s) confirmed in "
                f"validation_drops.jsonl. Dropped unit indices: "
                f"{sorted(dropped_unit_indices)}."
            )
            facts.append(
                f"validation_drops.jsonl confirms {len(validation_drops)} "
                f"drop(s) with per-unit identity"
            )
        else:
            evidence_basis = EvidenceBasis.OBSERVED
            interpretation = (
                f"validation_drops.jsonl present but does not account "
                f"for all {len(lost)} lost unit(s). "
                f"Drops: {sorted(dropped_unit_indices)}, "
                f"Lost: {lost_indices}."
            )
    elif v002_count > 0 and len(lost) <= v002_count:
        evidence_basis = EvidenceBasis.INFERRED_MODERATE_CONFIDENCE
        interpretation = (
            f"{v002_count} EX-V-002 validation error(s) logged, "
            f"count matches {len(lost)} lost unit(s). "
            f"Loss is plausibly explained by validation rejection, "
            f"but processing_log does not record which specific "
            f"unit_indices were affected."
        )
        facts.append(f"{v002_count} EX-V-002 error(s) in processing_log")
    else:
        evidence_basis = EvidenceBasis.OBSERVED
        interpretation = (
            f"{len(lost)} unit(s) lost with only {v002_count} "
            f"EX-V-002 error(s) — loss exceeds known validation drops."
        )

    return [Anomaly(
        anomaly_id="ANO-UNIT-LOSS",
        category="grouped_unit_loss",
        severity=severity,
        evidence_basis=evidence_basis,
        summary=f"{len(lost)} grouped unit(s) lost between Phase 2b and final excerpts",
        observed_facts=facts,
        inferred_interpretation=interpretation,
        affected_keys=[e.key for e in lost],
        evidence_paths=[
            f"{run_dir_str}/phase2b_groupings/",
            f"{run_dir_str}/excerpts.jsonl",
            f"{run_dir_str}/processing_log.jsonl",
        ],
    )]


def detect_zero_output(
    excerpts: list[dict],
    chunks: list[dict],
    timing: dict,
    traces: list[LLMTraceEntry],
    run_dir_str: str,
) -> list[Anomaly]:
    """Detect zero final excerpts despite upstream processing activity."""
    if len(excerpts) > 0:
        return []

    phase2a_time = timing.get("phase2a", 0)
    has_traces = len(traces) > 0
    has_chunks = len(chunks) > 0

    if not (phase2a_time > 10 or has_traces or has_chunks):
        return []

    facts = [
        f"Final excerpt count: 0",
        f"Phase 1 chunk count: {len(chunks)}",
        f"Phase 2a time: {phase2a_time:.1f}s",
        f"LLM trace count: {len(traces)}",
    ]

    error_count = 0
    # Check if errors were logged as zero despite activity
    for t in traces:
        if t.has_error:
            error_count += 1

    anomalies = [Anomaly(
        anomaly_id="ANO-ZERO-OUTPUT",
        category="zero_excerpt_run_with_upstream_activity",
        severity="structural_fail",
        evidence_basis=EvidenceBasis.OBSERVED,
        summary="Zero excerpts produced despite upstream processing activity",
        observed_facts=facts,
        inferred_interpretation=(
            f"Run consumed {phase2a_time:.1f}s in phase2a and made "
            f"{len(traces)} LLM call(s) but produced zero excerpts. "
            f"{error_count} call-level error(s) detected."
        ),
        affected_keys=[],
        evidence_paths=[
            f"{run_dir_str}/excerpts.jsonl",
            f"{run_dir_str}/timing.json",
            f"{run_dir_str}/raw_llm_responses/",
        ],
    )]

    return anomalies


def detect_truncation(
    traces: list[LLMTraceEntry],
    run_dir_str: str,
) -> list[Anomaly]:
    """Detect LLM responses truncated by finish_reason=length."""
    truncated = [t for t in traces if t.finish_reason == "length"]
    if not truncated:
        return []

    facts = [
        f"{len(truncated)} response(s) with finish_reason=length",
    ]
    for t in truncated:
        facts.append(
            f"  {t.file_stem}: model={t.model}, "
            f"tokens_out={t.tokens_out}, "
            f"inferred_phase={t.inferred_phase.value}"
        )

    return [Anomaly(
        anomaly_id="ANO-TRUNCATION",
        category="truncated_llm_response",
        severity="structural_fail",
        evidence_basis=EvidenceBasis.OBSERVED,
        summary=f"{len(truncated)} LLM response(s) truncated (finish_reason=length)",
        observed_facts=facts,
        inferred_interpretation=(
            "Truncated responses produce incomplete JSON that cannot be "
            "parsed into valid classification/grouping output. This "
            "directly causes downstream phase failure."
        ),
        affected_keys=[],
        evidence_paths=[
            f"{run_dir_str}/raw_llm_responses/{t.file_stem}.json"
            for t in truncated
        ],
    )]


def detect_artifact_log_contradiction(
    excerpts: list[dict],
    processing_log: dict,
    timing: dict,
    run_dir_str: str,
) -> list[Anomaly]:
    """Detect contradictory success state: zero output + zero errors + activity."""
    excerpt_count = len(excerpts)
    error_count = processing_log.get("error_count", 0)
    phase2a_time = timing.get("phase2a", 0)

    if not (excerpt_count == 0 and error_count == 0 and phase2a_time > 10):
        return []

    return [Anomaly(
        anomaly_id="ANO-CONTRADICTION",
        category="artifact_log_contradiction",
        severity="structural_fail",
        evidence_basis=EvidenceBasis.INFERRED_HIGH_CONFIDENCE,
        summary="Zero output + zero logged errors despite substantial activity",
        observed_facts=[
            f"excerpt_count: {excerpt_count}",
            f"error_count: {error_count}",
            f"phase2a_time: {phase2a_time:.1f}s",
        ],
        inferred_interpretation=(
            "The run reports zero errors but also produced zero excerpts "
            "after spending significant time in phase2a. This is a "
            "contradictory success state — the run appears clean but "
            "clearly failed silently."
        ),
        affected_keys=[],
        evidence_paths=[
            f"{run_dir_str}/processing_log.jsonl",
            f"{run_dir_str}/run_metadata.json",
        ],
    )]


def detect_phase_failures(
    phase2a_failures: list[dict],
    phase2b_failures: list[dict],
    run_dir_str: str,
) -> list[Anomaly]:
    """Detect chunk-level phase failures from failure ledgers (C2)."""
    anomalies: list[Anomaly] = []

    if phase2a_failures:
        chunk_ids = [f.get("chunk_id", "?") for f in phase2a_failures]
        anomalies.append(Anomaly(
            anomaly_id="ANO-P2A-FAILURES",
            category="phase2a_chunk_failures",
            severity="structural_fail",
            evidence_basis=EvidenceBasis.OBSERVED,
            summary=(
                f"{len(phase2a_failures)} chunk(s) failed "
                f"Phase 2a classification"
            ),
            observed_facts=[
                f"Failed chunk_ids: {chunk_ids}",
                "Confirmed by phase2a_failures.jsonl (runner-emitted ledger)",
            ],
            inferred_interpretation=(
                "These chunks were attempted but classification failed "
                "after all retries. No segments or units were produced."
            ),
            affected_keys=[],
            evidence_paths=[f"{run_dir_str}/phase2a_failures.jsonl"],
        ))

    if phase2b_failures:
        chunk_ids = [f.get("chunk_id", "?") for f in phase2b_failures]
        anomalies.append(Anomaly(
            anomaly_id="ANO-P2B-FAILURES",
            category="phase2b_chunk_failures",
            severity="structural_fail",
            evidence_basis=EvidenceBasis.OBSERVED,
            summary=(
                f"{len(phase2b_failures)} chunk(s) failed "
                f"Phase 2b grouping"
            ),
            observed_facts=[
                f"Failed chunk_ids: {chunk_ids}",
                "Confirmed by phase2b_failures.jsonl (runner-emitted ledger)",
            ],
            inferred_interpretation=(
                "These chunks passed classification but grouping failed "
                "after all retries. No teaching units were produced."
            ),
            affected_keys=[],
            evidence_paths=[f"{run_dir_str}/phase2b_failures.jsonl"],
        ))

    return anomalies


def detect_all_anomalies(
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
    excerpts: list[dict],
    chunks: list[dict],
    traces: list[LLMTraceEntry],
    processing_log: dict,
    timing: dict,
    run_dir_str: str,
    validation_drops: list[dict] | None = None,
    phase2a_failures: list[dict] | None = None,
    phase2b_failures: list[dict] | None = None,
) -> list[Anomaly]:
    """Run all anomaly detectors and return combined results."""
    anomalies: list[Anomaly] = []
    anomalies.extend(detect_unit_loss(
        ledger, processing_log, run_dir_str, validation_drops,
    ))
    anomalies.extend(detect_zero_output(
        excerpts, chunks, timing, traces, run_dir_str,
    ))
    anomalies.extend(detect_truncation(traces, run_dir_str))
    anomalies.extend(detect_artifact_log_contradiction(
        excerpts, processing_log, timing, run_dir_str,
    ))
    # C2: Phase failure ledgers (when runner provides them)
    anomalies.extend(detect_phase_failures(
        phase2a_failures or [], phase2b_failures or [], run_dir_str,
    ))
    return anomalies


# ---------------------------------------------------------------------------
# Structural status determination
# ---------------------------------------------------------------------------

def determine_status(anomalies: list[Anomaly]) -> StructuralStatus:
    """Determine machine structural status from anomalies.

    Only decision-grade anomalies (unit_loss, zero_output, truncation,
    artifact_log_contradiction) can produce structural_fail/concern.
    """
    if any(a.severity == "structural_fail" for a in anomalies):
        return StructuralStatus.STRUCTURAL_FAIL
    if any(a.severity == "structural_concern" for a in anomalies):
        return StructuralStatus.STRUCTURAL_CONCERN
    return StructuralStatus.STRUCTURALLY_CLEAN


# ---------------------------------------------------------------------------
# Metric computation
# ---------------------------------------------------------------------------

def compute_metrics(
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
    chunk_records: list[ChunkRecord],
    traces: list[LLMTraceEntry],
    processing_log: dict,
    timing: dict,
    excerpts: list[dict],
    run_metadata: dict | None = None,
) -> list[TieredMetric]:
    """Compute all tiered metrics from the canonical ledger and traces."""
    metrics: list[TieredMetric] = []
    run_metadata = run_metadata or {}

    # Counts
    phase2b_count = sum(1 for e in ledger.values() if e.has_phase2b)
    excerpt_count = len(excerpts)
    grouped_only = sum(
        1 for e in ledger.values()
        if e.has_phase2b and not e.has_excerpt
    )

    # --- Decision-grade structural ---
    metrics.append(TieredMetric(
        name="unit_yield_ratio",
        value=round(excerpt_count / phase2b_count, 4) if phase2b_count > 0 else None,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))
    metrics.append(TieredMetric(
        name="phase1_chunk_count",
        value=len(chunk_records),
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))
    metrics.append(TieredMetric(
        name="phase2b_unit_count",
        value=phase2b_count,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))
    metrics.append(TieredMetric(
        name="final_excerpt_count",
        value=excerpt_count,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))
    metrics.append(TieredMetric(
        name="unit_loss_count",
        value=grouped_only,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))

    chunks_with_p2b = sum(1 for c in chunk_records if c.phase2b_present)
    total_chunks = len(chunk_records)
    metrics.append(TieredMetric(
        name="chunk_coverage_ratio",
        value=round(chunks_with_p2b / total_chunks, 4) if total_chunks > 0 else None,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))

    truncation_count = sum(1 for t in traces if t.finish_reason == "length")
    metrics.append(TieredMetric(
        name="truncation_count",
        value=truncation_count,
        tier=MetricTier.DECISION_GRADE,
        provenance="deterministic_structural",
    ))

    zero_output = excerpt_count == 0 and (
        timing.get("phase2a", 0) > 10 or len(traces) > 0
    )
    metrics.append(TieredMetric(
        name="zero_output_with_activity",
        value=zero_output,
        tier=MetricTier.DECISION_GRADE,
        provenance="deterministic_structural",
    ))

    error_count = int(
        processing_log.get("error_count", 0)
        or run_metadata.get("error_count", 0)
        or 0
    )
    metrics.append(TieredMetric(
        name="error_count",
        value=error_count,
        tier=MetricTier.DECISION_GRADE,
        provenance="artifact_accounting",
    ))

    # --- Operational ---
    total_time = sum(
        timing.get(k, 0)
        for k in ("load_package", "phase1", "phase2a", "phase2b", "phase3")
    )
    if total_time == 0:
        total_time = float(run_metadata.get("batch_elapsed_seconds", 0.0) or 0.0)
    metrics.append(TieredMetric(
        name="total_time_seconds",
        value=round(total_time, 2),
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))
    for phase_key in ("phase1", "phase2a", "phase2b", "phase3"):
        metrics.append(TieredMetric(
            name=f"{phase_key}_time_seconds",
            value=round(timing.get(phase_key, 0), 2),
            tier=MetricTier.OPERATIONAL,
            provenance="derived_operational",
        ))

    total_cost = sum(t.cost or 0 for t in traces)
    metrics.append(TieredMetric(
        name="total_llm_cost",
        value=round(total_cost, 6),
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))

    total_tokens_in = sum(t.tokens_in or 0 for t in traces)
    total_tokens_out = sum(t.tokens_out or 0 for t in traces)
    metrics.append(TieredMetric(
        name="total_tokens_in",
        value=total_tokens_in,
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))
    metrics.append(TieredMetric(
        name="total_tokens_out",
        value=total_tokens_out,
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))

    phase_counts: dict[str, int] = Counter()
    for t in traces:
        phase_counts[t.inferred_phase.value] += 1
    metrics.append(TieredMetric(
        name="call_count_by_inferred_phase",
        value=dict(phase_counts),
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))

    model_counts: dict[str, int] = Counter()
    for t in traces:
        if t.model:
            model_counts[t.model] += 1
    metrics.append(TieredMetric(
        name="call_count_by_model",
        value=dict(model_counts),
        tier=MetricTier.OPERATIONAL,
        provenance="derived_operational",
    ))

    # --- Review-risk ---
    if excerpt_count > 0:
        sc_counts = Counter(
            e.get("self_containment", "UNKNOWN") for e in excerpts
        )
        partial_count = sc_counts.get("PARTIAL", 0)
        dependent_count = sc_counts.get("DEPENDENT", 0)
        metrics.append(TieredMetric(
            name="partial_rate",
            value=round(partial_count / excerpt_count, 4),
            tier=MetricTier.REVIEW_RISK,
            provenance="heuristic_extracted",
        ))
        metrics.append(TieredMetric(
            name="dependent_count",
            value=dependent_count,
            tier=MetricTier.REVIEW_RISK,
            provenance="heuristic_extracted",
        ))

        rf_count = sum(
            len(e.get("review_flags", [])) for e in excerpts
        )
        metrics.append(TieredMetric(
            name="review_flag_count",
            value=rf_count,
            tier=MetricTier.REVIEW_RISK,
            provenance="heuristic_extracted",
        ))

        gf_count = sum(
            len(e.get("gate_flags", [])) for e in excerpts
        )
        metrics.append(TieredMetric(
            name="gate_flag_count",
            value=gf_count,
            tier=MetricTier.REVIEW_RISK,
            provenance="heuristic_extracted",
        ))

    # --- Descriptive ---
    if excerpt_count > 0:
        func_dist = Counter(
            e.get("primary_function", "unknown") for e in excerpts
        )
        metrics.append(TieredMetric(
            name="function_distribution",
            value=dict(func_dist),
            tier=MetricTier.DESCRIPTIVE,
            provenance="heuristic_extracted",
        ))

        sc_dist = Counter(
            e.get("self_containment", "UNKNOWN") for e in excerpts
        )
        metrics.append(TieredMetric(
            name="self_containment_distribution",
            value=dict(sc_dist),
            tier=MetricTier.DESCRIPTIVE,
            provenance="heuristic_extracted",
        ))

        word_counts = []
        for e in excerpts:
            pt = e.get("primary_text", "")
            if pt:
                word_counts.append(len(pt.split()))
        if word_counts:
            metrics.append(TieredMetric(
                name="mean_excerpt_word_count",
                value=round(sum(word_counts) / len(word_counts), 1),
                tier=MetricTier.DESCRIPTIVE,
                provenance="heuristic_extracted",
            ))

        school_count = sum(
            1 for e in excerpts if e.get("school") is not None
        )
        metrics.append(TieredMetric(
            name="school_attribution_rate",
            value=round(school_count / excerpt_count, 4),
            tier=MetricTier.DESCRIPTIVE,
            provenance="heuristic_extracted",
        ))

        scholars_count = sum(
            1 for e in excerpts if e.get("quoted_scholars")
        )
        metrics.append(TieredMetric(
            name="quoted_scholars_rate",
            value=round(scholars_count / excerpt_count, 4),
            tier=MetricTier.DESCRIPTIVE,
            provenance="heuristic_extracted",
        ))

    return metrics


# ---------------------------------------------------------------------------
# Review candidate generation
# ---------------------------------------------------------------------------

def generate_review_candidates(
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
    anomalies: list[Anomaly],
    run_dir_str: str,
) -> list[ReviewCandidate]:
    """Generate review candidates from the ledger and anomaly list."""
    candidates: list[ReviewCandidate] = []
    anomaly_affected: dict[CanonicalUnitKey, list[str]] = {}

    for ano in anomalies:
        for key in ano.affected_keys:
            anomaly_affected.setdefault(key, []).append(ano.anomaly_id)

    for key, entry in sorted(ledger.items(), key=lambda x: x[0].to_tuple()):
        bucket_tags: list[str] = []
        review_questions: list[str] = []
        observed_facts: list[str] = []
        artifact_pointers: list[str] = []

        # Lane 1/2: anomaly-associated
        if key in anomaly_affected:
            bucket_tags.append("anomaly_associated")

        # Lane 3: self-containment risk
        sc = None
        if entry.excerpt_data:
            sc = entry.excerpt_data.get("self_containment")
        elif entry.phase2b_data:
            sc = entry.phase2b_data.get("self_containment")

        if sc == "DEPENDENT":
            bucket_tags.append("dependent")
            review_questions.append(
                "Can this unit be understood without adjacent context?"
            )
        elif sc == "PARTIAL":
            bucket_tags.append("partial_self_containment")

        # Lane 6: ambiguity / consensus disagreement
        if entry.excerpt_data:
            cm = entry.excerpt_data.get("consensus_metadata")
            if cm and isinstance(cm, dict):
                decisions = cm.get("decisions", [])
                if isinstance(decisions, list):
                    disagreements = [
                        d for d in decisions
                        if isinstance(d, dict) and not d.get("verifier_agrees", True)
                    ]
                    if disagreements:
                        bucket_tags.append("consensus_disagreement")
                        review_questions.append(
                            "Consensus verification disagreed on some fields. "
                            "Are the final values correct?"
                        )

            # Context hint present → near-threshold PARTIAL
            if sc == "PARTIAL" and entry.excerpt_data.get("context_hint"):
                bucket_tags.append("near_threshold")

        # Build primary text and context
        primary_text = None
        if entry.excerpt_data:
            primary_text = entry.excerpt_data.get("primary_text")
        elif entry.phase2b_data:
            primary_text = entry.phase2b_data.get("text_snippet")

        # Observed facts
        observed_facts.append(f"stage_state: {entry.stage_state}")
        if sc:
            observed_facts.append(f"self_containment: {sc}")
        if entry.has_phase2b and not entry.has_excerpt:
            observed_facts.append("Unit present in Phase 2b but absent from final excerpts")

        # Artifact pointers
        if entry.has_phase2b:
            artifact_pointers.append(
                f"{run_dir_str}/phase2b_groupings/chunk_{entry.chunk_id}.json"
            )
        if entry.has_excerpt:
            artifact_pointers.append(f"{run_dir_str}/excerpts.jsonl")

        # Determine evidence basis
        evidence_basis = EvidenceBasis.OBSERVED
        if key in anomaly_affected:
            # Use the strongest anomaly's evidence basis
            for ano in anomalies:
                if key in ano.affected_keys:
                    evidence_basis = ano.evidence_basis
                    break

        # Only generate candidates with at least one bucket tag
        if bucket_tags:
            # Build context (adjacent unit snippets)
            context = _build_unit_context(key, ledger)

            candidates.append(ReviewCandidate(
                key=key,
                bucket_tags=bucket_tags,
                stage_state=entry.stage_state,
                evidence_basis=evidence_basis,
                primary_text=primary_text,
                context=context,
                observed_facts=observed_facts,
                inferred_interpretation=None,
                artifact_pointers=artifact_pointers,
                review_questions=review_questions,
                anomaly_ids=anomaly_affected.get(key, []),
            ))

    return candidates


def _build_unit_context(
    key: CanonicalUnitKey,
    ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
) -> dict[str, Any]:
    """Build prev/next unit context for a review card."""
    context: dict[str, Any] = {}

    prev_key = CanonicalUnitKey(
        key.source_id, key.div_id, key.chunk_index,
        key.unit_index - 1,
    )
    next_key = CanonicalUnitKey(
        key.source_id, key.div_id, key.chunk_index,
        key.unit_index + 1,
    )

    prev_entry = ledger.get(prev_key)
    if prev_entry:
        snippet = None
        if prev_entry.excerpt_data:
            snippet = prev_entry.excerpt_data.get("text_snippet")
        elif prev_entry.phase2b_data:
            snippet = prev_entry.phase2b_data.get("text_snippet")
        context["prev_unit"] = {
            "unit_index": prev_key.unit_index,
            "text_snippet": snippet,
        }

    next_entry = ledger.get(next_key)
    if next_entry:
        snippet = None
        if next_entry.excerpt_data:
            snippet = next_entry.excerpt_data.get("text_snippet")
        elif next_entry.phase2b_data:
            snippet = next_entry.phase2b_data.get("text_snippet")
        context["next_unit"] = {
            "unit_index": next_key.unit_index,
            "text_snippet": snippet,
        }

    return context


# ---------------------------------------------------------------------------
# Observability limitations
# ---------------------------------------------------------------------------

OBSERVABILITY_LIMITATIONS = [
    (
        "EX-V-002 dropped unit identity unknown: processing_log records "
        "error codes but not affected unit indices. The analyzer correlates "
        "by count but cannot confirm the specific unit-to-error mapping."
    ),
    (
        "Failed Phase 2a/2b chunks may be absent, not logged: if a chunk's "
        "classification fails, no output file is written. The analyzer "
        "detects absence but cannot distinguish 'not attempted' "
        "(--max-chunks) from 'attempted and failed silently'."
    ),
    (
        "Validation drops are not first-class artifacts: dropped units have "
        "no dedicated artifact. The analyzer infers drops from the gap "
        "between phase2b unit set and excerpt set."
    ),
    (
        "gate_queue verification not invoked by runner: gate_queue.jsonl "
        "is empty in all test books despite GATE_ON_* flags being true. "
        "The analyzer notes gate_count=0 but cannot determine if gates "
        "should have fired."
    ),
    (
        "Pre-L-001 runs lack chunk_id in raw traces: the analyzer reads "
        "chunk_id from request JSON when present (post-L-001); for older "
        "run directories chunk_id is None (semantic phase inference unaffected)."
    ),
]


# ---------------------------------------------------------------------------
# Full book analysis
# ---------------------------------------------------------------------------

def analyze_book(run_data: dict) -> BookAnalysisResult:
    """Run complete analysis on a loaded book run."""
    ledger = run_data["ledger"]
    chunk_records = run_data["chunk_records"]
    traces = run_data["traces"]
    processing_log = run_data["processing_log"]
    timing = run_data["timing"]
    run_metadata = run_data["run_metadata"]
    excerpts = run_data["excerpts"]
    run_dir_str = str(run_data["run_dir"])

    anomalies = detect_all_anomalies(
        ledger, excerpts, run_data["chunks"], traces,
        processing_log, timing, run_dir_str,
        validation_drops=run_data.get("validation_drops"),
        phase2a_failures=run_data.get("phase2a_failures"),
        phase2b_failures=run_data.get("phase2b_failures"),
    )
    status = determine_status(anomalies)
    metrics = compute_metrics(
        ledger, chunk_records, traces,
        processing_log, timing, excerpts, run_metadata=run_metadata,
    )
    candidates = generate_review_candidates(ledger, anomalies, run_dir_str)

    total_cost = sum(t.cost or 0 for t in traces)
    total_time = sum(
        timing.get(k, 0)
        for k in ("load_package", "phase1", "phase2a", "phase2b", "phase3")
    )
    if total_time == 0:
        total_time = float(run_metadata.get("batch_elapsed_seconds", 0.0) or 0.0)
    error_count = int(
        processing_log.get("error_count", 0)
        or run_metadata.get("error_count", 0)
        or 0
    )

    return BookAnalysisResult(
        book_name=run_data["book_name"],
        source_id=run_data["source_id"],
        structural_status=status,
        metrics=metrics,
        anomalies=anomalies,
        review_candidates=candidates,
        traces=traces,
        chunk_records=chunk_records,
        observability_limitations=list(OBSERVABILITY_LIMITATIONS),
        phase1_chunk_count=len(run_data["chunks"]),
        phase2b_unit_count=sum(
            1 for e in ledger.values() if e.has_phase2b
        ),
        excerpt_count=len(excerpts),
        error_count=error_count,
        total_time_seconds=total_time,
        total_cost=total_cost,
    )
