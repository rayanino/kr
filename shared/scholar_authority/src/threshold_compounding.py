"""Phase 5 Session 3 — REQ-SRC-0053 compound threshold + INV-SRC-0013 floor.

Implements the terminal-routing layer of the scholar match cell:

  - ``evaluate_compound_predicates`` — pure predicate evaluator (4 booleans
    + convergent identity + numeric backing). Shared between REQ-SRC-0052
    round-0 convergence check (called from ``stage2_verifier``) and
    REQ-SRC-0053 routing (called from ``compound_threshold_decision``).
  - ``count_non_name_corroborating_attributes`` — INV-SRC-0013 ≥2-non-name
    floor evaluation against the locked registry snapshot.
  - ``compound_threshold_decision`` — REQ-SRC-0053 entry point. Reads the
    Stage-2 verifier outputs, evaluates predicates against the packet's
    dossier_context + the registry's eligible non-name attributes, and
    routes to DEFINITIVE / DISPUTED / INSUFFICIENT_EVIDENCE.

Threshold constants (REQ-SRC-0053 + INV-SRC-0013):

  - ``MEAN_THRESHOLD = 0.92`` (mean confidence ≥ 0.92 for definitive)
  - ``EACH_THRESHOLD = 0.90`` (each verifier ≥ 0.90 for definitive)
  - ``RIVAL_MARGIN = 0.07`` (no rival within 0.07 of leader; widened from
    Codex Stage-3 Defect 1's [0.05, 0.07) partition gap)
  - ``DISPUTED_FLOOR = 0.75`` (mean ≥ 0.75 for disputed positions; below →
    insufficient_evidence)
  - ``INSUFFICIENT_FLOOR = 0.70`` (max individual confidence ≥ 0.70 for any
    terminal other than insufficient_evidence)
  - ``NON_NAME_CORROBORATION_FLOOR = 2`` (INV-SRC-0013 ≥2-non-name floor)

Eligible non-name attributes per INV-SRC-0013 (8 attribute classes):

  - ``century_active_hijri`` (compared dossier ↔ record.era_century_hijri)
  - ``school_affiliations[science]`` (any per-science overlap counts as 1)
  - ``primary_science`` (record.primary_science == dossier.primary_science)
  - ``attributed_works`` (any work-title overlap after normalization)
  - ``region_origin`` (record.geographic_origin in dossier.geographic_signals)
  - ``region_active`` (any record.geographic_active in geographic_signals)
  - ``secondary_sciences`` (DEFERRED — no DossierContext field; Session 5)
  - ``teacher_student_link`` (DEFERRED — no DossierContext field; Session 5)

Two attributes are conservatively under-counted (deferred) rather than
over-counted; the ≥2-non-name floor remains a strict gate.

Single-candidate disputed degenerate case: when REQ-SRC-0053 routing would
emit DISPUTED but only 1 candidate is in the packet (positions count would
be < 2), the implementation routes to INSUFFICIENT_EVIDENCE to satisfy
CON-SRC-0008 AC-2's ``len(positions) ≥ 2`` validator. Consistent with
REQ-SRC-0053 INSUFFICIENT (b) "ambiguity remains; no candidate cleared the
disputed floor".
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    Position,
    ScholarEvidencePacket,
    ScholarMatchProvenance,
    ScholarMatchResult,
    ScoreBreakdown,
    ScoredCandidate,
    ThresholdAudit,
    VerifierEmission,
    VerifierRecord,
)
from shared.scholar_authority.src.stage1_narrowing import (
    Registry,
    normalize_work_title_for_index,
)


# ---------------------------------------------------------------------------
# Threshold constants — REQ-SRC-0053 + INV-SRC-0013
# ---------------------------------------------------------------------------

MEAN_THRESHOLD: float = 0.92
EACH_THRESHOLD: float = 0.90
RIVAL_MARGIN: float = 0.07
DISPUTED_FLOOR: float = 0.75
INSUFFICIENT_FLOOR: float = 0.70
NON_NAME_CORROBORATION_FLOOR: int = 2


# ---------------------------------------------------------------------------
# CompoundPredicateResults — shared between REQ-SRC-0052 and REQ-SRC-0053
# ---------------------------------------------------------------------------


class CompoundPredicateResults(BaseModel):
    """REQ-SRC-0053 compound 4-condition threshold predicate results.

    All 4 booleans plus convergent-identity flag and numeric backing values.
    Used by both REQ-SRC-0052 round-0 convergence check (single boolean
    ``is_definitive``) and REQ-SRC-0053 terminal routing (full audit).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    convergent_identity: bool
    mean_passes: bool
    both_pass: bool
    no_rival_close: bool
    corroboration_count_ge_2: bool

    mean_confidence: float = Field(ge=0.0, le=1.0)
    leader_confidence: float = Field(ge=0.0, le=1.0)
    rival_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    corroboration_count: int = Field(ge=0)

    leader_id: Optional[str] = None

    @property
    def is_definitive(self) -> bool:
        """All 5 conditions for DEFINITIVE per REQ-SRC-0053 + REQ-SRC-0052."""
        return (
            self.convergent_identity
            and self.mean_passes
            and self.both_pass
            and self.no_rival_close
            and self.corroboration_count_ge_2
        )


# ---------------------------------------------------------------------------
# Predicate evaluator
# ---------------------------------------------------------------------------


def evaluate_compound_predicates(
    a_emission: VerifierEmission,
    b_emission: VerifierEmission,
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> CompoundPredicateResults:
    """Evaluate REQ-SRC-0053 compound 4-condition threshold predicates.

    Used by REQ-SRC-0052 round-0 convergence check (via ``is_definitive``)
    and by REQ-SRC-0053 terminal routing (full ThresholdAudit construction).
    F-4 hallucination handling: ``f4_rejected`` emissions are treated as
    "no signal" — convergent_identity becomes False, and the rejected
    emission contributes 0 to mean confidence calculation.
    """
    a_rejected = a_emission.f4_rejected
    b_rejected = b_emission.f4_rejected

    if a_rejected or b_rejected:
        convergent_identity = False
    else:
        convergent_identity = a_emission.chosen_id == b_emission.chosen_id

    leader_id = a_emission.chosen_id if convergent_identity else None

    a_conf = 0.0 if a_rejected else a_emission.confidence
    b_conf = 0.0 if b_rejected else b_emission.confidence
    mean_conf = (a_conf + b_conf) / 2.0
    leader_conf = max(a_conf, b_conf)

    if leader_id is None or a_rejected or b_rejected:
        rival_conf: Optional[float] = None
    else:
        rival_conf = _compute_rival_aggregated_confidence(
            a_emission, b_emission, leader_id=leader_id
        )

    mean_passes = mean_conf >= MEAN_THRESHOLD
    both_pass = (
        not a_rejected and not b_rejected and a_conf >= EACH_THRESHOLD and b_conf >= EACH_THRESHOLD
    )
    no_rival_close = rival_conf is None or (leader_conf - rival_conf) >= RIVAL_MARGIN

    corroboration_count = (
        count_non_name_corroborating_attributes(leader_id, packet, registry)
        if leader_id is not None
        else 0
    )

    return CompoundPredicateResults(
        convergent_identity=convergent_identity,
        mean_passes=mean_passes,
        both_pass=both_pass,
        no_rival_close=no_rival_close,
        corroboration_count_ge_2=corroboration_count >= NON_NAME_CORROBORATION_FLOOR,
        mean_confidence=mean_conf,
        leader_confidence=leader_conf,
        rival_confidence=rival_conf,
        corroboration_count=corroboration_count,
        leader_id=leader_id,
    )


def _compute_rival_aggregated_confidence(
    a_emission: VerifierEmission,
    b_emission: VerifierEmission,
    *,
    leader_id: str,
) -> Optional[float]:
    """Second-place candidate's aggregated confidence, or None if no rival.

    Aggregated confidence per candidate = mean of A's and B's
    per_candidate_confidences for that candidate. Missing entries default
    to 0.0. Rival = candidate with second-highest aggregated confidence
    (excluding leader).
    """
    all_ids = (
        set(a_emission.per_candidate_confidences.keys())
        | set(b_emission.per_candidate_confidences.keys())
    )
    all_ids.discard(leader_id)
    if not all_ids:
        return None
    aggregated = {
        cid: (
            a_emission.per_candidate_confidences.get(cid, 0.0)
            + b_emission.per_candidate_confidences.get(cid, 0.0)
        )
        / 2.0
        for cid in all_ids
    }
    return max(aggregated.values())


# ---------------------------------------------------------------------------
# INV-SRC-0013 ≥2-non-name floor evaluation
# ---------------------------------------------------------------------------


def count_non_name_corroborating_attributes(
    chosen_id: str,
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> int:
    """INV-SRC-0013 ≥2-non-name floor evaluation.

    Counts the number of distinct non-name attribute classes where the
    dossier_context overlaps the registry record for ``chosen_id``. Each
    eligible attribute class contributes 0 or 1 (multi-value overlaps still
    count as 1 per class). Name expansion (nasab, nisba, kunyah, laqab) is
    NOT eligible corroboration per INV-SRC-0013 rule.statement.

    Returns 0 when ``chosen_id`` is not in the registry (treated as F-4
    hallucination: no record means no corroboration).
    """
    record = registry.lookup_by_canonical_id(chosen_id)
    if record is None:
        return 0
    dossier = packet.dossier_context
    count = 0
    if _century_intersects(record.era_century_hijri, dossier.century_active_hijri_estimates):
        count += 1
    if _school_affiliation_intersects(record.school_affiliations, dossier.school_affiliation_hints):
        count += 1
    if _primary_science_intersects(record.primary_science, dossier.primary_science):
        count += 1
    if _attributed_works_intersect(record.known_works, dossier.attributed_works):
        count += 1
    if _region_origin_intersects(record.geographic_origin, dossier.geographic_signals):
        count += 1
    if _region_active_intersects(record.geographic_active, dossier.geographic_signals):
        count += 1
    return count


def _century_intersects(record_century: Optional[int], dossier_estimates: list[int]) -> bool:
    """century_active_hijri intersection (1 if record century ∈ estimates)."""
    return record_century is not None and record_century in set(dossier_estimates)


def _school_affiliation_intersects(
    record_schools: dict[str, Optional[str]],
    dossier_hints: dict[str, Optional[str]],
) -> bool:
    """school_affiliations[science] intersection — any per-science overlap counts."""
    if not record_schools or not dossier_hints:
        return False
    for science, hint_school in dossier_hints.items():
        if hint_school is None:
            continue
        if record_schools.get(science) == hint_school:
            return True
    return False


def _primary_science_intersects(
    record_science: Optional[str], dossier_science: Optional[str]
) -> bool:
    """primary_science exact-match intersection."""
    return (
        record_science is not None
        and dossier_science is not None
        and record_science == dossier_science
    )


def _attributed_works_intersect(
    record_works: list[str], dossier_works: list[str]
) -> bool:
    """attributed_works intersection after normalize_work_title_for_index.

    Reuses Session 2's normalization (alef-translation + tashkeel + tatweel
    strip) for byte-faithful registry-vs-dossier comparison.
    """
    if not record_works or not dossier_works:
        return False
    norm_record = {normalize_work_title_for_index(w) for w in record_works}
    norm_dossier = {normalize_work_title_for_index(w) for w in dossier_works}
    return bool(norm_record & norm_dossier)


def _region_origin_intersects(
    record_origin: Optional[str], dossier_signals: list[str]
) -> bool:
    """region_origin intersection (1 if record_origin in signals list)."""
    return record_origin is not None and record_origin in set(dossier_signals)


def _region_active_intersects(
    record_active: list[str], dossier_signals: list[str]
) -> bool:
    """region_active intersection — any overlap counts as 1 attribute class."""
    if not record_active or not dossier_signals:
        return False
    return bool(set(record_active) & set(dossier_signals))


# ---------------------------------------------------------------------------
# REQ-SRC-0053 compound_threshold_decision entry point
# ---------------------------------------------------------------------------


def compound_threshold_decision(
    verifier_record: VerifierRecord,
    emissions: list[VerifierEmission],
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> ScholarMatchResult:
    """REQ-SRC-0053 — terminal routing with compound 4-condition threshold.

    Selects the final-round emissions per ``verifier_record.round_count``,
    evaluates the compound predicates, builds the full provenance audit,
    and routes to DEFINITIVE / DISPUTED / INSUFFICIENT_EVIDENCE per the
    REQ-SRC-0053 partition.

    Single-candidate disputed degenerate case (positions count would be < 2):
    routed to INSUFFICIENT_EVIDENCE per CON-SRC-0008 AC-2's ``len(positions)
    ≥ 2`` validator. Consistent with REQ-SRC-0053 INSUFFICIENT (b).
    """
    a_final, b_final = _select_final_emissions(emissions, verifier_record)
    predicates = evaluate_compound_predicates(a_final, b_final, packet, registry)
    threshold_audit = _build_threshold_audit(predicates)
    provenance = _build_provenance(verifier_record, threshold_audit, packet)

    if predicates.is_definitive:
        return _build_definitive_result(a_final, b_final, predicates, provenance, registry)
    if _is_insufficient_evidence(a_final, b_final, predicates):
        return _build_insufficient_evidence_result(provenance)
    return _build_disputed_or_fallback_result(
        a_final, b_final, predicates, provenance, packet, registry
    )


def _select_final_emissions(
    emissions: list[VerifierEmission], verifier_record: VerifierRecord
) -> tuple[VerifierEmission, VerifierEmission]:
    """Select the final-round emissions for the two verifiers.

    round_count == 1 → final = round_index 0 emissions.
    round_count == 2 → final = round_index 1 emissions.
    round_count == 0 → degenerate "no verifier ran" path; this function
        is NEVER called for round_count == 0 because
        ``compound_threshold_decision`` is bypassed by the cell's
        zero-invocation short-circuit (no_candidates /
        verifier_unavailable). If somehow reached, the empty emissions
        would raise ValueError below — which is the correct semantics
        (no emissions to select).
    """
    target_round = 1 if verifier_record.round_count == 2 else 0
    a_emission: Optional[VerifierEmission] = None
    b_emission: Optional[VerifierEmission] = None
    for emission in emissions:
        if emission.round_index != target_round:
            continue
        if emission.verifier_id == verifier_record.verifier_a_id and a_emission is None:
            a_emission = emission
        elif emission.verifier_id == verifier_record.verifier_b_id and b_emission is None:
            b_emission = emission
    if a_emission is None or b_emission is None:
        raise ValueError(
            f"Could not find final-round emissions for "
            f"{verifier_record.verifier_a_id!r} and {verifier_record.verifier_b_id!r} "
            f"at round_index={target_round} (round_count={verifier_record.round_count}; "
            f"emissions count={len(emissions)})"
        )
    return (a_emission, b_emission)


def _is_insufficient_evidence(
    a: VerifierEmission, b: VerifierEmission, predicates: CompoundPredicateResults
) -> bool:
    """REQ-SRC-0053 INSUFFICIENT_EVIDENCE predicate.

    (a) no candidate scores ≥ 0.70 across both verifiers (max individual
        confidence < INSUFFICIENT_FLOOR).
    (b) ambiguity remains; mean < 0.75 (no candidate cleared the
        disputed floor).
    """
    if a.f4_rejected and b.f4_rejected:
        return True
    a_conf = 0.0 if a.f4_rejected else a.confidence
    b_conf = 0.0 if b.f4_rejected else b.confidence
    max_individual = max(a_conf, b_conf)
    if max_individual < INSUFFICIENT_FLOOR:
        return True
    if predicates.mean_confidence < DISPUTED_FLOOR:
        return True
    return False


def _build_definitive_result(
    a: VerifierEmission,
    b: VerifierEmission,
    predicates: CompoundPredicateResults,
    provenance: ScholarMatchProvenance,
    registry: Registry,
) -> ScholarMatchResult:
    """Construct DEFINITIVE ScholarMatchResult per CON-SRC-0008 AC-1."""
    chosen_id = a.chosen_id  # convergent_identity guaranteed by is_definitive
    record = registry.lookup_by_canonical_id(chosen_id)
    if record is None:
        raise ValueError(
            f"DEFINITIVE result requires a registry record for chosen_id={chosen_id!r} "
            "but registry.lookup_by_canonical_id returned None. INV-SRC-0013 "
            "corroboration_count was ≥ 2, which implies the lookup must have "
            "succeeded — registry mutation between predicate evaluation and "
            "result construction violates the snapshot-lock contract."
        )
    return ScholarMatchResult(
        canonical_scholar_id=chosen_id,
        confidence=predicates.mean_confidence,
        disambiguation_state="definitive",
        record_status=record.status,
        evidence_sources=_collect_evidence_for_chosen(a, b, chosen_id),
        positions=[],
        provenance=provenance,
    )


def _build_disputed_or_fallback_result(
    a: VerifierEmission,
    b: VerifierEmission,
    predicates: CompoundPredicateResults,
    provenance: ScholarMatchProvenance,
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> ScholarMatchResult:
    """Construct DISPUTED result (with positions ≥ 2) or fall back to insufficient.

    Builds positions[] from all candidates ranked by either verifier (after
    f4-rejection filtering). When positions count < 2 (single-candidate
    packet with predicate failure), routes to INSUFFICIENT_EVIDENCE to
    satisfy CON-SRC-0008 AC-2's ≥2-positions validator.
    """
    positions = _build_positions_for_disputed(a, b, packet, registry)
    if len(positions) < 2:
        return _build_insufficient_evidence_result(provenance)
    leader = positions[0]
    leader_record = registry.lookup_by_canonical_id(leader.canonical_id)
    if leader_record is None:
        return _build_insufficient_evidence_result(provenance)
    record_status = leader_record.status
    return ScholarMatchResult(
        canonical_scholar_id=leader.canonical_id,
        confidence=leader.confidence,
        disambiguation_state="disputed",
        record_status=record_status,
        evidence_sources=list(leader.cited_evidence),
        positions=positions,
        provenance=provenance,
    )


def _build_insufficient_evidence_result(
    provenance: ScholarMatchProvenance,
) -> ScholarMatchResult:
    """Construct INSUFFICIENT_EVIDENCE ScholarMatchResult per CON-SRC-0008 AC-3."""
    return ScholarMatchResult(
        canonical_scholar_id=None,
        confidence=None,
        disambiguation_state="insufficient_evidence",
        record_status=None,
        evidence_sources=[],
        positions=[],
        provenance=provenance,
    )


def _build_positions_for_disputed(
    a: VerifierEmission,
    b: VerifierEmission,
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> list[Position]:
    """Build per-candidate Position list for DISPUTED, ordered by aggregated confidence.

    Iterates over the union of positions canonical_ids from both emissions
    (excluding f4-rejected emissions' chosen_ids), aggregates confidence as
    mean across both verifiers (missing entries default to 0.0), and
    constructs Position with per_verifier_confidence + aggregated
    score_breakdown + deduplicated cited_evidence.
    """
    candidate_ids = _collect_candidate_ids_for_disputed(a, b)
    positions: list[Position] = []
    for cid in candidate_ids:
        a_score = _find_scored_candidate(a, cid)
        b_score = _find_scored_candidate(b, cid)
        if a_score is None and b_score is None:
            continue
        agg_confidence, per_verifier = _aggregate_confidences(a, b, cid)
        score_breakdown = _aggregate_score_breakdowns(a_score, b_score)
        cited_evidence = _aggregate_cited_evidence(a_score, b_score)
        positions.append(
            Position(
                canonical_id=cid,
                confidence=agg_confidence,
                per_verifier_confidence=per_verifier,
                score_breakdown=score_breakdown,
                cited_evidence=cited_evidence,
            )
        )
    # Sort by aggregated confidence DESC, with canonical_id ASC as a
    # deterministic tiebreaker. Ties matter: the equal-score-rivals case
    # (REQ-SRC-0053 condition (e)) produces identical confidences, and
    # without an explicit tiebreaker the candidate union (set-typed in
    # _collect_candidate_ids_for_disputed) iterates in PYTHONHASHSEED-
    # dependent order — a non-deterministic leader assignment that would
    # randomize the HumanGateCheckpoint's "leader_canonical_scholar_id"
    # current_value across runs and break replay reproducibility.
    positions.sort(key=lambda p: (-p.confidence, p.canonical_id))
    return positions


def _collect_candidate_ids_for_disputed(
    a: VerifierEmission, b: VerifierEmission
) -> set[str]:
    """Union of ranked canonical_ids excluding f4-rejected chosen_ids."""
    ids = set(a.per_candidate_confidences.keys()) | set(b.per_candidate_confidences.keys())
    if a.f4_rejected:
        ids.discard(a.chosen_id)
    if b.f4_rejected:
        ids.discard(b.chosen_id)
    return ids


def _find_scored_candidate(
    emission: VerifierEmission, canonical_id: str
) -> Optional[ScoredCandidate]:
    """Locate the ScoredCandidate for ``canonical_id`` within ``emission.positions``."""
    for position in emission.positions:
        if position.canonical_id == canonical_id:
            return position
    return None


def _aggregate_confidences(
    a: VerifierEmission, b: VerifierEmission, canonical_id: str
) -> tuple[float, dict[str, float]]:
    """Mean-aggregate per-candidate confidence + record per-verifier breakdown."""
    a_conf = a.per_candidate_confidences.get(canonical_id, 0.0) if not a.f4_rejected else 0.0
    b_conf = b.per_candidate_confidences.get(canonical_id, 0.0) if not b.f4_rejected else 0.0
    return (a_conf + b_conf) / 2.0, {a.verifier_id: a_conf, b.verifier_id: b_conf}


def _aggregate_score_breakdowns(
    a_score: Optional[ScoredCandidate], b_score: Optional[ScoredCandidate]
) -> ScoreBreakdown:
    """Mean-aggregate two ScoreBreakdown objects (or pass through one if other is None).

    When neither verifier scored the candidate (defensive — caller filters
    these), returns an all-zero ScoreBreakdown.
    """
    if a_score is not None and b_score is not None:
        a_dict = a_score.score_breakdown.model_dump()
        b_dict = b_score.score_breakdown.model_dump()
        return ScoreBreakdown(**{k: (a_dict[k] + b_dict[k]) / 2.0 for k in a_dict})
    if a_score is not None:
        return a_score.score_breakdown
    if b_score is not None:
        return b_score.score_breakdown
    return ScoreBreakdown(
        name_match=0.0,
        death_date_proximity=0.0,
        school_affiliation_overlap=0.0,
        work_title_match=0.0,
        teacher_student_network_match=0.0,
        geographic_origin_match=0.0,
        century_active_match=0.0,
        primary_science_match=0.0,
        secondary_sciences_overlap=0.0,
    )


def _aggregate_cited_evidence(
    a_score: Optional[ScoredCandidate], b_score: Optional[ScoredCandidate]
) -> list[CitationRef]:
    """Union of cited_evidence from both ScoredCandidate, deduplicated by content."""
    seen_keys: set[tuple[str, str, str]] = set()
    aggregated: list[CitationRef] = []
    for source in (a_score, b_score):
        if source is None:
            continue
        for ev in source.cited_evidence:
            key = (ev.source_book_id, ev.evidence_type, ev.raw_evidence)
            if key in seen_keys:
                continue
            seen_keys.add(key)
            aggregated.append(ev)
    if not aggregated:
        raise ValueError(
            "Position.cited_evidence must be non-empty (CON-SRC-0008 + INV-SRC-0015 AC-5); "
            "neither verifier provided cited_evidence for this candidate"
        )
    return aggregated


def _collect_evidence_for_chosen(
    a: VerifierEmission, b: VerifierEmission, chosen_id: str
) -> list[CitationRef]:
    """Aggregate cited_evidence from both emissions for the chosen candidate."""
    a_score = _find_scored_candidate(a, chosen_id)
    b_score = _find_scored_candidate(b, chosen_id)
    return _aggregate_cited_evidence(a_score, b_score)


def _build_threshold_audit(predicates: CompoundPredicateResults) -> ThresholdAudit:
    """Construct ThresholdAudit from CompoundPredicateResults."""
    return ThresholdAudit(
        mean_passes=predicates.mean_passes,
        both_pass=predicates.both_pass,
        no_rival_close=predicates.no_rival_close,
        corroboration_count_ge_2=predicates.corroboration_count_ge_2,
        mean_confidence=predicates.mean_confidence,
        leader_confidence=predicates.leader_confidence,
        rival_confidence=predicates.rival_confidence,
        corroboration_count=predicates.corroboration_count,
    )


def _build_provenance(
    verifier_record: VerifierRecord,
    threshold_audit: ThresholdAudit,
    packet: ScholarEvidencePacket,
) -> ScholarMatchProvenance:
    """Construct ScholarMatchProvenance per INV-SRC-0015 completeness."""
    return ScholarMatchProvenance(
        stage_1_score_breakdown=_extract_stage_1_breakdown(packet),
        stage_2_verifier_record=verifier_record,
        threshold_audit=threshold_audit,
        registry_release_version=packet.registry_release_version,
        matched_phase=None,
    )


def _extract_stage_1_breakdown(
    packet: ScholarEvidencePacket,
) -> dict[str, dict[str, float]]:
    """Extract per-candidate Stage-1 channel scores from packet.candidate_set."""
    return {c.canonical_id: dict(c.score_breakdown) for c in packet.candidate_set}


__all__ = [
    "MEAN_THRESHOLD",
    "EACH_THRESHOLD",
    "RIVAL_MARGIN",
    "DISPUTED_FLOOR",
    "INSUFFICIENT_FLOOR",
    "NON_NAME_CORROBORATION_FLOOR",
    "CompoundPredicateResults",
    "evaluate_compound_predicates",
    "count_non_name_corroborating_attributes",
    "compound_threshold_decision",
]
