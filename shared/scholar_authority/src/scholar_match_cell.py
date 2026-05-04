"""Phase 5 Session 4 — scholar_match_cell orchestrator (DEC-SRC-0013).

Wires the Phase 5 chain end-to-end into a single deterministic-orchestrator
entry point per DEC-SRC-0013's "scholar_match_cell" named cell pattern:

    parse_fragment (Session 2)
        → narrow_candidates (Session 2)
        → run_verifier_cell (Session 3)
        → compound_threshold_decision (Session 3)
        → ScholarMatchResult (CON-SRC-0008, Session 1)

Orchestrator semantics (deterministic, NOT LLM):

  - The orchestrator runs the Stage-1 narrowing then the Stage-2 verifier
    cell unconditionally. It never makes a content decision.
  - All LLM calls are dispatched through the injected ``VerifierCallable``
    boundary (REQ-SRC-0042 amendment + INV-SRC-0017): no runtime external
    calls are issued by the orchestrator itself.
  - Snapshot drift propagates: ``RegistrySnapshotDriftError`` raised by
    ``narrow_candidates`` or ``run_verifier_cell`` is NOT caught — per
    INV-SRC-0017 the case aborts, the higher-level pipeline retries
    explicitly per REQ-SRC-0049 EXPLICIT REPLAY semantics.
  - Verifier unavailability (REQ-SRC-0052 AC-6) is caught and routed to
    ``insufficient_evidence`` with degenerate provenance — the conservative
    path. The 1-verifier-disputed branch from AC-6 is intentionally not
    implemented in Session 4 because ``run_verifier_cell`` does not expose
    partial state on ``VerifierUnavailableError`` (Session 5 enhancement).
  - Empty candidate_set after Stage-1 narrowing also routes to
    ``insufficient_evidence``. SPEC §10 SCHOLAR_NO_MATCH error code is
    reserved for callers that want fail-loud semantics; the orchestrator
    surfaces the empty-narrowing case as a structured result with
    threshold_audit zeros (mean_passes=False, mean_confidence=0.0, etc.)
    so the "nothing happened" signal is auditable rather than swallowed.

Asymmetric-validator pattern lens (Sessions 1+3 generalized defect class):
the two degenerate-case insufficient_evidence constructors
(``_build_no_candidates_insufficient_evidence`` and
``_build_verifier_unavailable_insufficient_evidence``) construct
threshold_audit and verifier_record with IDENTICAL discipline — same
fields populated, same zero/False shape. Any future change must update
both constructors symmetrically.
"""

from __future__ import annotations

from dataclasses import dataclass

from shared.scholar_authority.src.fragment_parser import (
    parse_fragment,
)
from shared.scholar_authority.src.match_contracts import (
    DossierContext,
    ScholarEvidencePacket,
    ScholarMatchProvenance,
    ScholarMatchResult,
    ThresholdAudit,
    VerifierRecord,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshot,
)
from shared.scholar_authority.src.stage1_narrowing import (
    CaseComplexity,
    Registry,
    narrow_candidates,
)
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallable,
    VerifierCellOrchestration,
    VerifierSpec,
    VerifierUnavailableError,
    run_verifier_cell,
)
from shared.scholar_authority.src.threshold_compounding import (
    compound_threshold_decision,
)


# ---------------------------------------------------------------------------
# Orchestration bundle — DI substrate per DEC-SRC-0013
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScholarMatchCellOrchestration:
    """Dependency-injection bundle for ``scholar_match_cell`` (DEC-SRC-0013).

    Bundles everything ``scholar_match_cell`` needs to wire the four-stage
    chain so the public function signature stays at three parameters per
    ``.claude/rules/python-code.md`` ≤5-param rule:

      - ``registry`` — Stage-1 narrowing substrate (Session 2 ``Registry``;
        Session 4+ wires the production interface).
      - ``snapshot`` — REQ-SRC-0049 pinned-snapshot identity. Drift
        detection is per-stage (narrowing + verifier cell each call
        ``validate_no_drift``); the orchestrator does NOT poll.
      - ``verifier_a_spec`` / ``verifier_b_spec`` — REQ-SRC-0052 verifier
        identity + prompt-template hashes + seeds.
      - ``call_verifier`` — typed ``VerifierCallable`` boundary for the
        Stage-2 LLM dispatch. Tests pass deterministic stubs; production
        Session 4+ wires LiteLLM + Instructor multi-model consensus per
        ``.claude/skills/consensus-pattern/SKILL.md``.
      - ``case_complexity`` — REQ-SRC-0051 K-cap selector (8 standard /
        12 degraded). Defaults to "standard".

    Frozen + ``arbitrary_types_allowed=False`` (the dataclass-level
    immutability ensures the orchestration substrate cannot be mutated
    mid-case; this is a soft mirror of CON-SRC-0009's hard
    immutability for the evidence packet).
    """

    registry: Registry
    snapshot: RegistrySnapshot
    verifier_a_spec: VerifierSpec
    verifier_b_spec: VerifierSpec
    call_verifier: VerifierCallable
    case_complexity: CaseComplexity = "standard"


# ---------------------------------------------------------------------------
# scholar_match_cell entry point (DEC-SRC-0013)
# ---------------------------------------------------------------------------


def scholar_match_cell(
    fragment: str,
    dossier: DossierContext,
    orchestration: ScholarMatchCellOrchestration,
) -> ScholarMatchResult:
    """DEC-SRC-0013 — wire the Phase 5 scholar match chain end-to-end.

    Always returns a ``ScholarMatchResult`` (CON-SRC-0008). Three terminal
    paths inside the orchestrator:

      1. Normal path: Stage-1 produces ≥1 candidate → Stage-2 verifier
         cell runs → ``compound_threshold_decision`` routes to
         definitive / disputed / insufficient_evidence per REQ-SRC-0053.
      2. Empty narrowing: Stage-1 produces 0 candidates →
         insufficient_evidence with degenerate provenance.
      3. Verifier unavailable: ``run_verifier_cell`` raises
         ``VerifierUnavailableError`` (REQ-SRC-0052 AC-6) →
         insufficient_evidence with degenerate provenance.

    Errors that propagate (NOT caught by the orchestrator):

      - ``FragmentNotArabicError`` / ``HonorificOnlyNameError`` /
        ``CompoundNameSplitError`` — input-shape errors from
        ``parse_fragment``. Caller must validate fragment before
        invoking the cell.
      - ``RegistrySnapshotDriftError`` — INV-SRC-0017 contract: case
        aborts with EXPLICIT REPLAY at the higher-level pipeline.
        Catching here would mask the drift signal.
      - ``RuntimeExternalCallError`` — REQ-SRC-0042 amendment: runtime
        external calls are FORBIDDEN. Catching here would let the
        forbidden call's downstream effects pollute the audit trail.

    Asymmetric-validator-pattern audit (Sessions 1+3 generalized defect
    class): the two degenerate-case constructors below build
    ``ThresholdAudit`` + ``VerifierRecord`` identically. Any future
    behavioral change must update BOTH constructors symmetrically.
    """
    parse_result = parse_fragment(fragment)

    packet = narrow_candidates(
        parse_result,
        dossier,
        orchestration.snapshot,
        orchestration.registry,
        case_complexity=orchestration.case_complexity,
    )

    if not packet.candidate_set:
        return _build_no_candidates_insufficient_evidence(packet, orchestration)

    cell_orchestration = VerifierCellOrchestration(
        registry_snapshot=orchestration.snapshot,
        registry=orchestration.registry,
        call_verifier=orchestration.call_verifier,
    )

    try:
        verifier_record, emissions = run_verifier_cell(
            packet,
            orchestration.verifier_a_spec,
            orchestration.verifier_b_spec,
            cell_orchestration,
        )
    except VerifierUnavailableError:
        return _build_verifier_unavailable_insufficient_evidence(
            packet, orchestration
        )

    return compound_threshold_decision(
        verifier_record, emissions, packet, orchestration.registry
    )


# ---------------------------------------------------------------------------
# Degenerate-case insufficient_evidence constructors (asymmetric-validator
# pattern: keep these constructors symmetric).
# ---------------------------------------------------------------------------


def _build_no_candidates_insufficient_evidence(
    packet: ScholarEvidencePacket,
    orchestration: ScholarMatchCellOrchestration,
) -> ScholarMatchResult:
    """Stage-1 produced 0 candidates → insufficient_evidence terminal.

    Per CON-SRC-0008 AC-3 + INV-SRC-0015 AC-2: insufficient_evidence
    results may have empty evidence_sources, but provenance must be
    populated with the verifiers the orchestrator HAD AVAILABLE plus a
    threshold_audit recording WHY the case fell to insufficient_evidence.

    Round_count = 1 is the minimum-truthful value per the ``Literal[1, 2]``
    type. The threshold_audit (all ``False``, all ``0.0``) carries the
    actual "no verifier ran" signal — round_count is the floor, not the
    count.
    """
    threshold_audit = _build_zero_threshold_audit()
    verifier_record = _build_zero_invocation_verifier_record(orchestration)
    provenance = _build_provenance(packet, verifier_record, threshold_audit)
    return ScholarMatchResult(
        canonical_scholar_id=None,
        confidence=None,
        disambiguation_state="insufficient_evidence",
        record_status=None,
        evidence_sources=[],
        positions=[],
        provenance=provenance,
    )


def _build_verifier_unavailable_insufficient_evidence(
    packet: ScholarEvidencePacket,
    orchestration: ScholarMatchCellOrchestration,
) -> ScholarMatchResult:
    """REQ-SRC-0052 AC-6 — fewer than 2 verifiers returned → insufficient_evidence.

    Conservative routing: the 1-verifier-disputed branch from AC-6
    requires ``run_verifier_cell`` to expose partial state on
    ``VerifierUnavailableError``, which Session 3 does not currently do.
    Session 5 may extend the partial-state plumbing; for now the cell
    routes to insufficient_evidence on any verifier-unavailable signal.

    Identical threshold_audit + verifier_record discipline as
    ``_build_no_candidates_insufficient_evidence`` to preserve the
    asymmetric-validator-pattern symmetry between degenerate paths.
    """
    threshold_audit = _build_zero_threshold_audit()
    verifier_record = _build_zero_invocation_verifier_record(orchestration)
    provenance = _build_provenance(packet, verifier_record, threshold_audit)
    return ScholarMatchResult(
        canonical_scholar_id=None,
        confidence=None,
        disambiguation_state="insufficient_evidence",
        record_status=None,
        evidence_sources=[],
        positions=[],
        provenance=provenance,
    )


def _build_zero_threshold_audit() -> ThresholdAudit:
    """Build the all-zero / all-False ThresholdAudit for degenerate paths.

    Used by both ``_build_no_candidates_insufficient_evidence`` and
    ``_build_verifier_unavailable_insufficient_evidence``. Symmetry
    between the two paths is enforced by sharing this builder.
    """
    return ThresholdAudit(
        mean_passes=False,
        both_pass=False,
        no_rival_close=False,
        corroboration_count_ge_2=False,
        mean_confidence=0.0,
        leader_confidence=0.0,
        rival_confidence=None,
        corroboration_count=0,
    )


def _build_zero_invocation_verifier_record(
    orchestration: ScholarMatchCellOrchestration,
) -> VerifierRecord:
    """Build a VerifierRecord for the no-invocation degenerate paths.

    Records the verifier specs the orchestrator HAD AVAILABLE so the
    audit trail names which verifiers WOULD HAVE RUN. round_count=1 is
    the minimum value allowed by the ``Literal[1, 2]`` type; the
    accompanying threshold_audit's all-False / all-0.0 shape carries the
    actual "no rounds ran" signal.

    Both prompt_template_hashes record the round-0 hash from the spec
    (the round that WOULD have run first if the verifier had been
    invoked). Round-1 hashes are not surfaced because round-1 is
    conditional on round-0 non-convergence — recording it here would
    mis-attribute the state.
    """
    return VerifierRecord(
        verifier_a_id=orchestration.verifier_a_spec.verifier_id,
        verifier_b_id=orchestration.verifier_b_spec.verifier_id,
        verifier_a_seed=orchestration.verifier_a_spec.seed,
        verifier_b_seed=orchestration.verifier_b_spec.seed,
        verifier_a_prompt_template_hash=(
            orchestration.verifier_a_spec.round_0_prompt_template_hash
        ),
        verifier_b_prompt_template_hash=(
            orchestration.verifier_b_spec.round_0_prompt_template_hash
        ),
        round_count=1,
    )


def _build_provenance(
    packet: ScholarEvidencePacket,
    verifier_record: VerifierRecord,
    threshold_audit: ThresholdAudit,
) -> ScholarMatchProvenance:
    """Build a ScholarMatchProvenance for the degenerate-path results.

    INV-SRC-0015 requires ``registry_release_version`` non-null; sourced
    from the locked packet (which inherits it from the snapshot at
    Stage-1 time, so this is the byte-faithful pinned identifier).

    ``stage_1_score_breakdown`` is built from the packet's candidate_set
    (empty for the no-candidates path; whatever Stage-1 produced for the
    verifier-unavailable path).
    """
    stage_1: dict[str, dict[str, float]] = {
        candidate.canonical_id: dict(candidate.score_breakdown)
        for candidate in packet.candidate_set
    }
    return ScholarMatchProvenance(
        stage_1_score_breakdown=stage_1,
        stage_2_verifier_record=verifier_record,
        threshold_audit=threshold_audit,
        registry_release_version=packet.registry_release_version,
        matched_phase=None,
    )


__all__ = [
    "ScholarMatchCellOrchestration",
    "scholar_match_cell",
]
