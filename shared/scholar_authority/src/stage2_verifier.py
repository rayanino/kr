"""Phase 5 Session 3 — REQ-SRC-0052 verifier cell + INV-SRC-0016 closure.

Implements the Stage-2 verifier orchestration layer of the scholar match
cell:

  - ``run_verifier_cell`` — REQ-SRC-0052 entry point. Hybrid round-0
    functional / round-1 adversarial-only-on-disagreement protocol with
    round cap = 2.
  - ``_apply_inv_src_0016_closure`` — INV-SRC-0016 chosen_id-closure check
    applied to EVERY verifier output BEFORE any routing decision reads.
    Hallucinated chosen_ids are marked ``f4_rejected=True`` and preserved
    for audit (Critical Rule 13 — all data is future training material).
  - ``VerifierSpec`` — Pydantic configuration for one Stage-2 verifier
    (verifier_id + model_id + seed + per-round prompt template hashes).
  - ``VerifierCellOrchestration`` — frozen dataclass bundling the
    orchestration substrate (registry snapshot + registry + call_verifier)
    so the public function signature stays at ≤4 parameters per
    ``.claude/rules/python-code.md``.
  - ``VerifierCallable`` — typed callable for dependency injection. Tests
    pass deterministic stubs; Session 4 production wires LiteLLM +
    Instructor multi-model consensus per
    ``.claude/skills/consensus-pattern/SKILL.md``.
  - ``VerifierUnavailableError`` — REQ-SRC-0052 AC-6 closure
    (SRC-E-TRUST-AGENT-COUNT, existing ErrorCode reused per ChatGPT DR
    citation discipline).
  - ``VerifierCallError`` — raised by a VerifierCallable when its LLM call
    fails permanently (after exhausting internal retries). Caught by
    ``run_verifier_cell`` to determine availability per AC-6.

Design boundaries:

  - The verifier cell does NOT make real LLM calls. The
    ``VerifierCallable`` parameter handles the call; tests pass
    deterministic stubs, Session 4 wires the production client.
  - Round-0 convergence check uses ``threshold_compounding.evaluate_compound
    _predicates`` for single-source-of-truth — the same predicate
    evaluator that REQ-SRC-0053 uses for terminal routing.
  - Round-1 adversarial scaffold is a prompt-template choice (verifier A
    defends its round-0 leader; verifier B attacks A's leader and defends
    B's). The orchestrator passes both round-0 emissions to the callable
    so the prompt template can construct the adversarial input.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import ErrorCode
from shared.scholar_authority.src.match_contracts import (
    RoundCount,
    ScholarEvidencePacket,
    VerifierEmission,
    VerifierRecord,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshot,
    validate_no_drift,
)
from shared.scholar_authority.src.stage1_narrowing import Registry


# ---------------------------------------------------------------------------
# Configuration types
# ---------------------------------------------------------------------------


class VerifierSpec(BaseModel):
    """Configuration for one Stage-2 verifier per REQ-SRC-0052 preconditions.

    Captures the four identity + routing fields the orchestrator needs to
    dispatch a verifier and audit the dispatch:

      - ``verifier_id`` — opaque identity (e.g. "verifier_a" / "anthropic_opus")
      - ``model_id`` — provider-qualified model identifier consumed by
        Session 4's LiteLLM dispatch (e.g. "anthropic/claude-opus-4-6")
      - ``seed`` — deterministic seed surfaced to the LLM provider when
        supported; recorded in VerifierRecord for reproducibility
      - ``round_0_prompt_template_hash`` / ``round_1_prompt_template_hash``
        — SHA-256 (or equivalent) hashes of the round-specific prompt
        templates. The hash that produced the FINAL emitted verdict is
        recorded in VerifierRecord; per-round per-verifier hashes are
        recoverable from the persisted ``list[VerifierEmission]`` audit
        trail (Critical Rule 13 — all data is future training material).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    verifier_id: str = Field(min_length=1)
    model_id: str = Field(min_length=1)
    seed: int
    round_0_prompt_template_hash: str = Field(min_length=1)
    round_1_prompt_template_hash: str = Field(min_length=1)


VerifierCallable = Callable[
    [
        VerifierSpec,
        ScholarEvidencePacket,
        Literal[0, 1],
        Optional[VerifierEmission],
        Optional[VerifierEmission],
    ],
    VerifierEmission,
]
"""Typed callable signature for the LLM-call boundary.

Parameters (positional):

  1. ``spec`` — VerifierSpec for this dispatch
  2. ``packet`` — locked CON-SRC-0009 evidence packet (immutable per round)
  3. ``round_index`` — 0 for round-0 functional / 1 for round-1 adversarial
  4. ``own_round_0`` — this verifier's own round-0 emission, OR None
     (None for round-0 dispatch; populated for round-1 dispatch so the
     adversarial prompt template can reference what this verifier said
     before)
  5. ``other_round_0`` — the OTHER verifier's round-0 emission, OR None
     (None for round-0; populated for round-1 so the adversarial scaffold
     can construct attacker / defender framing)

Returns the VerifierEmission produced by the LLM. INV-SRC-0016 closure is
applied AFTER return by the orchestrator; the callable does NOT need to
validate chosen_id ∈ candidate_set itself.

Raises ``VerifierCallError`` when the LLM call fails permanently after
exhausting internal retries. The orchestrator catches this specific
exception to determine availability per REQ-SRC-0052 AC-6.
"""


@dataclass(frozen=True)
class VerifierCellOrchestration:
    """Orchestration substrate for ``run_verifier_cell`` (DI bundle).

    Bundles the registry snapshot pin (REQ-SRC-0049 contract), the registry
    substrate (Session 2 ``Registry``; Session 4 wires production), and the
    LLM call boundary callable (test stubs / Session 4 production). Bundling
    keeps ``run_verifier_cell``'s public signature at 4 parameters per the
    ≤5-param rule in ``.claude/rules/python-code.md``.
    """

    registry_snapshot: RegistrySnapshot
    registry: Registry
    call_verifier: VerifierCallable


# ---------------------------------------------------------------------------
# Error types
# ---------------------------------------------------------------------------


class VerifierCallError(RuntimeError):
    """Raised by a VerifierCallable when an LLM call fails permanently.

    The callable is responsible for internal retry logic per
    ``.claude/rules/llm-call-optimization.md`` (exponential backoff, jitter,
    Retry-After honoring). After retries are exhausted, the callable raises
    this exception. The orchestrator (``run_verifier_cell``) catches it
    specifically to determine availability per REQ-SRC-0052 AC-6.
    """

    def __init__(self, verifier_id: str, message: str) -> None:
        super().__init__(f"Verifier {verifier_id!r} call failed permanently: {message}")
        self.verifier_id = verifier_id


class VerifierUnavailableError(RuntimeError):
    """SRC-E-TRUST-AGENT-COUNT — fewer than 2 independent verifiers returned.

    Raised by ``run_verifier_cell`` when fewer than 2 round-0 verifiers
    return non-VerifierCallError outputs. Per REQ-SRC-0052 AC-6 + Critical
    Rule 7 (D-041 multi-model consensus): a content classification decision
    requires ≥ 2 independent verifiers; the case aborts to disputed terminal
    (with the single-verifier output if any) or insufficient_evidence
    (if both unavailable). Reuses existing ErrorCode (contracts.py:572)
    per ChatGPT DR existing-error-citation discipline.
    """

    error_code: ErrorCode = ErrorCode.TRUST_AGENT_COUNT

    def __init__(self, returned_verifier_ids: list[str]) -> None:
        super().__init__(
            f"Fewer than 2 independent verifiers returned. "
            f"Available verifier ids: {returned_verifier_ids!r} "
            f"(SRC-E-TRUST-AGENT-COUNT; REQ-SRC-0052 AC-6 + D-041)."
        )
        self.returned_verifier_ids = returned_verifier_ids


# ---------------------------------------------------------------------------
# REQ-SRC-0052 entry point
# ---------------------------------------------------------------------------


def run_verifier_cell(
    packet: ScholarEvidencePacket,
    verifier_a_spec: VerifierSpec,
    verifier_b_spec: VerifierSpec,
    orchestration: VerifierCellOrchestration,
) -> tuple[VerifierRecord, list[VerifierEmission]]:
    """REQ-SRC-0052 — Stage-2 verifier cell with hybrid round-0 / round-1 protocol.

    Round-0 functional: each verifier independently scores candidates with
    no peeking. Round-0 convergence check (deterministic; uses the same
    predicate evaluator as REQ-SRC-0053): if all 5 conditions met (same
    chosen_id + 4 numerical predicates + ≥2-non-name floor) → DEFINITIVE
    with round_count=1. Otherwise → round-1 adversarial scaffold.

    Round-1 (only on round-0 non-convergence): each verifier sees the
    OTHER's round-0 emission. Verifier A defends its round-0 leader;
    verifier B attacks A's leader and defends B's. Packet is UNCHANGED
    per CON-SRC-0009 immutability + INV-SRC-0016 chosen_id closure.

    INV-SRC-0016 closure runs on EVERY verifier output (round-0 and
    round-1) BEFORE any routing or convergence check reads the output.
    F-4 hallucinations are marked ``f4_rejected=True`` and preserved for
    audit; the routing path treats them as structural disagreement.

    Round cap = ``VERIFIER_ROUND_CAP`` = 2; the case finalizes with
    whatever terminal applies after round-1.
    """
    if verifier_a_spec.verifier_id == verifier_b_spec.verifier_id:
        raise ValueError(
            "Verifier ids must be distinct for D-041 multi-model consensus "
            f"(REQ-SRC-0052 verifier diversity requirement). Got "
            f"verifier_a_id == verifier_b_id == {verifier_a_spec.verifier_id!r}."
        )
    validate_no_drift(orchestration.registry_snapshot, packet.registry_release_version)
    a_round_0, b_round_0 = _dispatch_round_0(
        verifier_a_spec, verifier_b_spec, packet, orchestration
    )
    emissions: list[VerifierEmission] = [a_round_0, b_round_0]
    if _evaluate_round_0_convergence(a_round_0, b_round_0, packet, orchestration.registry):
        record = _build_verifier_record(
            verifier_a_spec, verifier_b_spec, 1, a_round_0, b_round_0
        )
        return (record, emissions)
    a_round_1, b_round_1 = _dispatch_round_1(
        verifier_a_spec, verifier_b_spec, packet, orchestration, a_round_0, b_round_0
    )
    emissions.extend([a_round_1, b_round_1])
    record = _build_verifier_record(
        verifier_a_spec, verifier_b_spec, 2, a_round_1, b_round_1
    )
    return (record, emissions)


def _dispatch_round_0(
    verifier_a_spec: VerifierSpec,
    verifier_b_spec: VerifierSpec,
    packet: ScholarEvidencePacket,
    orchestration: VerifierCellOrchestration,
) -> tuple[VerifierEmission, VerifierEmission]:
    """Dispatch both round-0 verifiers (no peeking) and apply INV-SRC-0016 closure."""
    a_emission = _safe_call_round_0(verifier_a_spec, packet, orchestration)
    b_emission = _safe_call_round_0(verifier_b_spec, packet, orchestration)
    available = [e for e in (a_emission, b_emission) if e is not None]
    if len(available) < 2:
        returned_ids = [e.verifier_id for e in available]
        raise VerifierUnavailableError(returned_ids)
    assert a_emission is not None and b_emission is not None  # narrowing for pyright
    return (a_emission, b_emission)


def _safe_call_round_0(
    spec: VerifierSpec,
    packet: ScholarEvidencePacket,
    orchestration: VerifierCellOrchestration,
) -> Optional[VerifierEmission]:
    """Call a round-0 verifier; return None on permanent failure.

    Catches ``VerifierCallError`` specifically (NOT bare Exception) per
    ``.claude/rules/python-code.md`` "errors fail loud". Returned None
    signals the orchestrator to count the verifier as unavailable.
    """
    try:
        emission = orchestration.call_verifier(spec, packet, 0, None, None)
    except VerifierCallError:
        return None
    return _apply_inv_src_0016_closure(emission, packet)


def _dispatch_round_1(
    verifier_a_spec: VerifierSpec,
    verifier_b_spec: VerifierSpec,
    packet: ScholarEvidencePacket,
    orchestration: VerifierCellOrchestration,
    a_round_0: VerifierEmission,
    b_round_0: VerifierEmission,
) -> tuple[VerifierEmission, VerifierEmission]:
    """Dispatch both round-1 verifiers (adversarial scaffold) and apply closure.

    Verifier A's round-1 prompt receives ``own_round_0=a_round_0,
    other_round_0=b_round_0``. Verifier B's receives the inverse. The
    callable is responsible for constructing the adversarial framing
    inside the prompt template; the orchestrator only ensures the inputs
    are present.
    """
    a_emission = orchestration.call_verifier(verifier_a_spec, packet, 1, a_round_0, b_round_0)
    a_closed = _apply_inv_src_0016_closure(a_emission, packet)
    b_emission = orchestration.call_verifier(verifier_b_spec, packet, 1, b_round_0, a_round_0)
    b_closed = _apply_inv_src_0016_closure(b_emission, packet)
    return (a_closed, b_closed)


# ---------------------------------------------------------------------------
# INV-SRC-0016 chosen_id closure
# ---------------------------------------------------------------------------


def _apply_inv_src_0016_closure(
    emission: VerifierEmission, packet: ScholarEvidencePacket
) -> VerifierEmission:
    """INV-SRC-0016 chosen_id closure check.

    If the verifier's chosen_id is NOT in the locked packet's candidate_set,
    the emission is REJECTED (``f4_rejected`` flipped to True). The
    hallucinated chosen_id is preserved in ``chosen_id`` for audit
    (Critical Rule 13 — all data is future training material). Downstream
    routing (REQ-SRC-0053) treats f4_rejected emissions as structural
    disagreement; they cannot finalize as canonical_scholar_id.

    Idempotent: running the closure twice on the same emission has the
    same effect as running it once. An already-rejected emission is
    returned unchanged.

    Round-1 application: identical to round-0. The packet is immutable
    per CON-SRC-0009; round-1 cannot introduce new candidates per
    INV-SRC-0016 + REQ-SRC-0052 postcondition #3.
    """
    if emission.f4_rejected:
        return emission
    if packet.is_chosen_id_in_candidate_set(emission.chosen_id):
        return emission
    return emission.model_copy(update={"f4_rejected": True})


# ---------------------------------------------------------------------------
# VerifierRecord assembly
# ---------------------------------------------------------------------------


def _build_verifier_record(
    a_spec: VerifierSpec,
    b_spec: VerifierSpec,
    round_count: RoundCount,
    a_emission_for_record: VerifierEmission,
    b_emission_for_record: VerifierEmission,
) -> VerifierRecord:
    """Construct VerifierRecord with the headline (final-round) prompt hashes.

    The "headline" hash for each verifier is the prompt_template_hash of
    the final-round emission — round-0 if round_count==1, round-1 if
    round_count==2. Per-round per-verifier hashes are recoverable from
    the full ``list[VerifierEmission]`` audit trail returned alongside.

    Spec interpretation (REQ-SRC-0052 postcondition #7): the record
    captures the prompt template hashes that produced the EMITTED verdict.
    Audit data (round-0 hashes when round_count==2, etc.) lives outside
    the contract surface in the persisted emissions list per Critical
    Rule 13.
    """
    return VerifierRecord(
        verifier_a_id=a_spec.verifier_id,
        verifier_b_id=b_spec.verifier_id,
        verifier_a_seed=a_spec.seed,
        verifier_b_seed=b_spec.seed,
        verifier_a_prompt_template_hash=a_emission_for_record.prompt_template_hash,
        verifier_b_prompt_template_hash=b_emission_for_record.prompt_template_hash,
        round_count=round_count,
    )


# ---------------------------------------------------------------------------
# Round-0 convergence check (delegates to threshold_compounding for shared
# predicate logic)
# ---------------------------------------------------------------------------


def _evaluate_round_0_convergence(
    a_emission: VerifierEmission,
    b_emission: VerifierEmission,
    packet: ScholarEvidencePacket,
    registry: Registry,
) -> bool:
    """REQ-SRC-0052 round-0 convergence check.

    All 5 conditions per REQ-SRC-0052 postcondition #3:
      (a) both verifiers' top-ranked chosen_id is the same
      (b) mean confidence ≥ 0.92
      (c) each verifier's confidence ≥ 0.90
      (d) no rival candidate within 0.07 of leader confidence
      (e) ≥2 non-name attributes intersect per INV-SRC-0013

    Uses the SAME predicate evaluator as REQ-SRC-0053 routing
    (``evaluate_compound_predicates``) so that the round-0 convergence
    rule and the DEFINITIVE routing rule are bit-identical.
    """
    # Lazy import to break the runtime cycle: threshold_compounding imports
    # types from match_contracts (no cycle there); stage2_verifier imports
    # the predicate evaluator at call time (no cycle either, since
    # threshold_compounding does not import stage2_verifier).
    from shared.scholar_authority.src.threshold_compounding import (
        evaluate_compound_predicates,
    )
    predicates = evaluate_compound_predicates(a_emission, b_emission, packet, registry)
    return predicates.is_definitive


__all__ = [
    "VerifierSpec",
    "VerifierCallable",
    "VerifierCellOrchestration",
    "VerifierCallError",
    "VerifierUnavailableError",
    "run_verifier_cell",
]
