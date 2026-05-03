"""Phase 5 scholar-matching data contracts.

CON-SRC-0008 ScholarMatchResult and CON-SRC-0009 ScholarEvidencePacket
plus supporting types. New OPT-4 architecture surface introduced by the
Phase 5 Stage 4 atom set (commit ``e91c142cc``).

Naming collision warning
------------------------
The legacy ``ScholarMatchResult`` dataclass at
``shared/scholar_authority/src/scholar_authority.py:31`` and re-exported via
``shared/scholar_authority/src/__init__.py:14`` describes the older
SPEC §4.A.5 single-threshold matching surface (``found / record /
match_score / match_detail / action``). It remains in place to preserve
the existing scholar_authority test suite and ``lookup()`` consumers
until Session 4 rewires ``compute_scholar_match_score`` to emit the new
contract defined here. Phase 5 implementation code MUST import the new
contracts directly from this module:

    from shared.scholar_authority.src.match_contracts import ScholarMatchResult

Forbidden field name
--------------------
``snapshot_version`` is FORBIDDEN as a Pydantic field name everywhere
``registry_release_version`` is the canonical pinned-snapshot identifier
per Codex Stage-3 Defect 2 (see REQ-SRC-0049 + CON-SRC-0008 +
INV-SRC-0015 + INV-SRC-0017). Two enforcement layers ship together:
``extra='forbid'`` rejects unknown fields generically, and a
``mode='before'`` validator raises an explicit
``snapshot_version is FORBIDDEN`` error pointing to the canonical name.
"""

from __future__ import annotations

import uuid
from typing import Any, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ---------------------------------------------------------------------------
# Constants — sourced from CON-SRC-0009 (K caps; snippet bounds) and
# REQ-SRC-0052 (verifier round cap). Calibration of K caps and snippet bounds
# happens in Session 5 against the 50-scholar gold seed (SPEC §10 line 460).
# ---------------------------------------------------------------------------

K_CAP_STANDARD: int = 8
K_CAP_DEGRADED: int = 12
SOURCE_SNIPPETS_MAX: int = 5
SOURCE_SNIPPET_MAX_BYTES: int = 2048
VERIFIER_ROUND_CAP: int = 2

# ---------------------------------------------------------------------------
# Type literals
# ---------------------------------------------------------------------------

DisambiguationState = Literal["definitive", "disputed", "insufficient_evidence"]

RecordStatus = Literal[
    "provisional",
    "confirmed",
    "merged_into",
    "split_disputed",
    "deprecated",
]

EvidenceType = Literal[
    "metadata_card",
    "title_page",
    "colophon",
    "agent_inference",
    "work_title_match",
    "teacher_student_link",
    "external_anchor",
]

# RoundCount uses Literal[1, 2] to bind to the round-cap-2 protocol of
# REQ-SRC-0052. Round 0 (functional) and round 1 (adversarial-on-disagreement)
# happen within a single match-call; this field records HOW MANY rounds ran,
# not WHICH round emitted the verdict.
RoundCount = Literal[1, 2]


_FORBIDDEN_FIELD_ERROR = (
    "Field name 'snapshot_version' is FORBIDDEN. Use canonical name "
    "'registry_release_version' (Phase 5 canonical pinned-snapshot "
    "identifier; see REQ-SRC-0049 + CON-SRC-0008 + INV-SRC-0015 + "
    "INV-SRC-0017)."
)


def _reject_snapshot_version(data: Any) -> Any:
    """Mode='before' helper: raise if 'snapshot_version' appears at top level.

    Called from ScholarMatchProvenance and ScholarEvidencePacket validators.
    Pydantic ``extra='forbid'`` would also catch this, but with a generic
    error; this raises an explicit message pointing to the canonical name.
    """
    if isinstance(data, dict) and "snapshot_version" in data:
        raise ValueError(_FORBIDDEN_FIELD_ERROR)
    return data


# ---------------------------------------------------------------------------
# Supporting types — leaves first
# ---------------------------------------------------------------------------


class CitationRef(BaseModel):
    """A single piece of evidence cited by a verifier or aggregator."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_book_id: str = Field(min_length=1)
    evidence_type: EvidenceType
    raw_evidence: str = Field(min_length=1)


class ScoreBreakdown(BaseModel):
    """The 9 sub-scores per Position from ChatGPT DR §3b.

    Used inside CON-SRC-0008 Position.score_breakdown. Each sub-score is a
    [0.0, 1.0] float describing one dimension of the scholar-fragment match.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    name_match: float = Field(ge=0.0, le=1.0)
    death_date_proximity: float = Field(ge=0.0, le=1.0)
    school_affiliation_overlap: float = Field(ge=0.0, le=1.0)
    work_title_match: float = Field(ge=0.0, le=1.0)
    teacher_student_network_match: float = Field(ge=0.0, le=1.0)
    geographic_origin_match: float = Field(ge=0.0, le=1.0)
    century_active_match: float = Field(ge=0.0, le=1.0)
    primary_science_match: float = Field(ge=0.0, le=1.0)
    secondary_sciences_overlap: float = Field(ge=0.0, le=1.0)


class VerifierRecord(BaseModel):
    """Stage-2 verifier orchestration record per REQ-SRC-0052."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    verifier_a_id: str = Field(min_length=1)
    verifier_b_id: str = Field(min_length=1)
    verifier_a_seed: int
    verifier_b_seed: int
    verifier_a_prompt_template_hash: str = Field(min_length=1)
    verifier_b_prompt_template_hash: str = Field(min_length=1)
    round_count: RoundCount


class ThresholdAudit(BaseModel):
    """The 4 compound-threshold predicates per REQ-SRC-0053 plus backing values.

    Required on every ScholarMatchResult.provenance per CON-SRC-0008 +
    INV-SRC-0015. The 4 booleans collectively determine whether the result
    is definitive, disputed, or insufficient_evidence; the numeric backing
    fields make the verdict reproducible against the original snapshot.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    mean_passes: bool
    both_pass: bool
    no_rival_close: bool
    corroboration_count_ge_2: bool

    mean_confidence: float = Field(ge=0.0, le=1.0)
    leader_confidence: float = Field(ge=0.0, le=1.0)
    rival_confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    corroboration_count: int = Field(ge=0)


class CareerPhaseRef(BaseModel):
    """Reference to a scholar career phase per shared SPEC §4.A.7.

    Career-phase modeling (al-Shafiʿi qadim/jadid pattern) is out of scope
    for Session 1; this placeholder holds enough structure for the
    matched_phase field of ScholarMatchProvenance to round-trip without
    forcing the eventual §4.A.7 implementation into a particular shape.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    phase_id: str = Field(min_length=1)
    phase_label: Optional[str] = None


class Position(BaseModel):
    """One competing identity in a disputed terminal.

    Per CON-SRC-0008 line 88-97: each Position carries the candidate's id,
    the per-verifier and aggregated confidences, the 9-feature score
    breakdown, the qualitative argument against any close rival, and the
    cited evidence used by Stage-2 verifiers to support this candidate.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_id: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    per_verifier_confidence: dict[str, float] = Field(default_factory=dict)
    score_breakdown: ScoreBreakdown
    why_not_other_candidate: Optional[str] = None
    cited_evidence: list[CitationRef] = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_per_verifier_confidence_range(self) -> "Position":
        """Per-verifier confidences must each be in [0, 1]."""
        for vid, conf in self.per_verifier_confidence.items():
            if not 0.0 <= conf <= 1.0:
                raise ValueError(
                    f"Position.per_verifier_confidence[{vid!r}]={conf} "
                    "is outside [0.0, 1.0]"
                )
        return self


class RevisionHistoryEntry(BaseModel):
    """One prior result_id + registry_release_version pair preserved on replay.

    Per INV-SRC-0017 AC-2: when a fragment is re-attributed against a newer
    registry release, the new ScholarMatchResult records the prior result_id
    and its registry_release_version in revision_history. Critical Rule 13
    (all data is future training material) requires preservation, not
    overwriting, of prior verdicts.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    prior_result_id: str = Field(min_length=1)
    prior_registry_release_version: str = Field(min_length=1)
    revised_at: str = Field(min_length=1)


# ---------------------------------------------------------------------------
# Stage-2 verifier emission types — Session 3 contract surface (REQ-SRC-0052)
# ---------------------------------------------------------------------------


class ScoredCandidate(BaseModel):
    """One ranked candidate within a VerifierEmission per REQ-SRC-0052.

    The Stage-2 verifier scores ALL candidates in the locked CON-SRC-0009
    evidence packet. Each scored entry carries the candidate's id, its
    confidence in [0, 1], the 9-feature score_breakdown per ChatGPT DR §3b,
    and the cited_evidence supporting this candidate.

    Distinct from CON-SRC-0008.Position which is the RESULT-LEVEL aggregated
    shape (per_verifier_confidence, why_not_other_candidate, etc.). A
    ScoredCandidate is the per-verifier per-candidate intermediate emitted
    BEFORE aggregation across both verifiers.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_id: str = Field(min_length=1)
    confidence: float = Field(ge=0.0, le=1.0)
    score_breakdown: ScoreBreakdown
    cited_evidence: list[CitationRef] = Field(min_length=1)


class VerifierEmission(BaseModel):
    """One verifier's output for one round per REQ-SRC-0052.

    Round-0 emissions are produced under no-peeking (each verifier reasons
    over the locked packet without seeing the other's output). Round-1
    emissions are produced under the adversarial scaffold (each verifier
    sees the OTHER's round-0 emission). Validated by INV-SRC-0016 closure
    before any routing decision reads the verdict.

    Audit semantics (Critical Rule 13 — all data is future training material):
    every emission is preserved, including emissions where INV-SRC-0016
    closure rejected the chosen_id (``f4_rejected=True``). The hallucinated
    chosen_id survives in ``chosen_id`` for audit; the routing path uses the
    legitimate in-packet candidates only.

    Confidence semantics: ``.confidence`` is a derived property (NOT a
    stored field) returning ``positions[chosen_id].confidence``. If
    chosen_id is not in positions (f4_rejected with hallucinated id NOT
    scored), the derived confidence is 0.0. Single-source-of-truth: the
    confidence value lives in ``positions``; the property prevents
    construction-time inconsistency.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    verifier_id: str = Field(min_length=1)
    round_index: Literal[0, 1]
    chosen_id: str = Field(min_length=1)
    positions: list[ScoredCandidate] = Field(min_length=1)
    reasoning: str = ""
    prompt_template_hash: str = Field(min_length=1)
    f4_rejected: bool = False

    @model_validator(mode="after")
    def _validate_emission_integrity(self) -> "VerifierEmission":
        """Validate per-emission integrity: ``positions[]`` canonical_ids are unique.

        Each candidate appears at most once in positions[] so that
        ``per_candidate_confidences`` and ``confidence`` derive
        unambiguously. The validator does NOT require chosen_id to appear
        in positions: an LLM may name a chosen_id without including it in
        its own ranked positions list (the closure-relevant case from
        INV-SRC-0016 AC-1 where the verifier hallucinates an id and the
        orchestrator must still process the emission to mark it
        ``f4_rejected``). The ``.confidence`` property returns 0.0 in that
        case; downstream predicate evaluators treat ``f4_rejected``
        emissions as "no signal" regardless.
        """
        ids = [p.canonical_id for p in self.positions]
        if len(ids) != len(set(ids)):
            raise ValueError(
                "VerifierEmission.positions[] contains duplicate canonical_ids; "
                f"each candidate must appear at most once (canonical_ids={ids})"
            )
        return self

    @property
    def confidence(self) -> float:
        """Derived: confidence the verifier gave to chosen_id.

        Returns ``positions[chosen_id].confidence`` if chosen_id is ranked,
        else 0.0. The 0.0 fallback applies to f4_rejected emissions where the
        LLM hallucinated an id without including it in its own ranked
        positions. Downstream predicate evaluators MUST treat f4_rejected
        emissions as "no signal" regardless of this property's value.
        """
        for position in self.positions:
            if position.canonical_id == self.chosen_id:
                return position.confidence
        return 0.0

    @property
    def per_candidate_confidences(self) -> dict[str, float]:
        """Derived: map of canonical_id → confidence from positions[].

        Convenience accessor for downstream predicate evaluation. Uniqueness
        of canonical_ids in positions[] is enforced by
        ``_validate_emission_integrity``; the dict comprehension is
        unambiguous.
        """
        return {p.canonical_id: p.confidence for p in self.positions}


class ScholarMatchProvenance(BaseModel):
    """Full audit surface for one match call.

    Required on every CON-SRC-0008 ScholarMatchResult per INV-SRC-0015.
    Includes Stage-1 channel scoring (which channels surfaced which
    candidates with what scores), Stage-2 verifier identity record (who
    ran with what prompt hashes and seeds across how many rounds), the
    4 compound-threshold predicates with full numeric backing, and the
    canonical pinned-snapshot identifier (``registry_release_version``;
    ``snapshot_version`` is FORBIDDEN).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    stage_1_score_breakdown: dict[str, dict[str, float]] = Field(
        default_factory=dict
    )
    stage_2_verifier_record: VerifierRecord
    threshold_audit: ThresholdAudit
    registry_release_version: str = Field(min_length=1)
    matched_phase: Optional[CareerPhaseRef] = None

    @model_validator(mode="before")
    @classmethod
    def _reject_forbidden_field_names(cls, data: Any) -> Any:
        """Reject snapshot_version per Codex Stage-3 Defect 2."""
        return _reject_snapshot_version(data)


# ---------------------------------------------------------------------------
# Top-level contract: CON-SRC-0008 ScholarMatchResult
# ---------------------------------------------------------------------------


class ScholarMatchResult(BaseModel):
    """Output of one scholar match call (CON-SRC-0008).

    Dual-state surface:
      - ``disambiguation_state`` (3-state) is THIS call's outcome
      - ``record_status`` (5-state) is the lifecycle status of the
        referenced ScholarAuthorityRecord at call time

    The two surfaces are orthogonal: a definitive match against a
    provisional record is valid (call conclusive, registry record still
    being enriched). Flattening the two would silently drop information.

    Cross-field invariants (enforced by ``_validate_state_consistency``):
      - definitive: canonical_scholar_id present, confidence present,
        record_status present, evidence_sources non-empty, positions empty,
        threshold_audit shows all 4 predicates true
      - disputed: canonical_scholar_id is positions[0].canonical_id (the
        leader), record_status reflects the leader, evidence_sources
        non-empty, positions has length ≥ 2, threshold_audit shows ≥1
        predicate false
      - insufficient_evidence: canonical_scholar_id null, confidence null,
        record_status null, positions empty, evidence_sources may be empty
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    result_id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    canonical_scholar_id: Optional[str] = None
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    disambiguation_state: DisambiguationState
    record_status: Optional[RecordStatus] = None
    evidence_sources: list[CitationRef] = Field(default_factory=list)
    positions: list[Position] = Field(default_factory=list)
    provenance: ScholarMatchProvenance
    revision_history: list[RevisionHistoryEntry] = Field(default_factory=list)

    @model_validator(mode="before")
    @classmethod
    def _reject_forbidden_field_names(cls, data: Any) -> Any:
        """Reject snapshot_version even at top level for defense in depth."""
        return _reject_snapshot_version(data)

    @model_validator(mode="after")
    def _validate_state_consistency(self) -> "ScholarMatchResult":
        """Enforce CON-SRC-0008 cross-field state-transition invariants."""
        state = self.disambiguation_state
        if state == "definitive":
            self._validate_definitive()
        elif state == "disputed":
            self._validate_disputed()
        elif state == "insufficient_evidence":
            self._validate_insufficient_evidence()
        return self

    def _validate_definitive(self) -> None:
        if self.canonical_scholar_id is None:
            raise ValueError(
                "definitive disambiguation_state requires "
                "canonical_scholar_id to be non-null (CON-SRC-0008 AC-1)"
            )
        if self.confidence is None:
            raise ValueError(
                "definitive disambiguation_state requires confidence "
                "(mean across Stage-2 verifiers) to be populated "
                "(CON-SRC-0008 AC-1)"
            )
        if self.record_status is None:
            raise ValueError(
                "definitive disambiguation_state requires record_status "
                "(5-state lifecycle of the referenced record) to be "
                "populated (CON-SRC-0008 AC-1)"
            )
        if not self.evidence_sources:
            raise ValueError(
                "definitive disambiguation_state requires evidence_sources "
                "non-empty (CON-SRC-0008 + INV-SRC-0015 AC-1)"
            )
        if self.positions:
            raise ValueError(
                "definitive disambiguation_state requires positions to be "
                "empty (CON-SRC-0008 AC-1: 'definitive does not populate "
                "positions')"
            )
        audit = self.provenance.threshold_audit
        if not (
            audit.mean_passes
            and audit.both_pass
            and audit.no_rival_close
            and audit.corroboration_count_ge_2
        ):
            raise ValueError(
                "definitive disambiguation_state requires all 4 "
                "compound-threshold predicates to be true "
                "(REQ-SRC-0053 + CON-SRC-0008 AC-1)"
            )

    def _validate_disputed(self) -> None:
        if len(self.positions) < 2:
            raise ValueError(
                "disputed disambiguation_state requires positions length "
                "≥ 2 (CON-SRC-0008 AC-2)"
            )
        if self.canonical_scholar_id is None:
            raise ValueError(
                "disputed disambiguation_state requires canonical_scholar_id "
                "(the leader's id, top of positions[0]) (CON-SRC-0008 AC-2)"
            )
        leader_id = self.positions[0].canonical_id
        if self.canonical_scholar_id != leader_id:
            raise ValueError(
                f"disputed disambiguation_state requires canonical_scholar_id "
                f"({self.canonical_scholar_id!r}) to equal positions[0]."
                f"canonical_id ({leader_id!r}) (CON-SRC-0008 AC-2)"
            )
        if self.confidence is None:
            raise ValueError(
                "disputed disambiguation_state requires confidence "
                "(leader aggregated confidence) to be populated "
                "(CON-SRC-0008 AC-2)"
            )
        if self.record_status is None:
            raise ValueError(
                "disputed disambiguation_state requires record_status "
                "(5-state lifecycle of the leader's record) to be "
                "populated; record_status is null only when "
                "canonical_scholar_id is null (CON-SRC-0008 AC-2 + "
                "field spec line 73-81)"
            )
        if not self.evidence_sources:
            raise ValueError(
                "disputed disambiguation_state requires evidence_sources "
                "non-empty (CON-SRC-0008 + INV-SRC-0015 AC-5)"
            )
        audit = self.provenance.threshold_audit
        if (
            audit.mean_passes
            and audit.both_pass
            and audit.no_rival_close
            and audit.corroboration_count_ge_2
        ):
            raise ValueError(
                "disputed disambiguation_state requires at least one "
                "compound-threshold predicate to be false "
                "(REQ-SRC-0053 + CON-SRC-0008 AC-2)"
            )

    def _validate_insufficient_evidence(self) -> None:
        if self.canonical_scholar_id is not None:
            raise ValueError(
                "insufficient_evidence disambiguation_state requires "
                "canonical_scholar_id to be null (CON-SRC-0008 AC-3)"
            )
        if self.confidence is not None:
            raise ValueError(
                "insufficient_evidence disambiguation_state requires "
                "confidence to be null (CON-SRC-0008 AC-3)"
            )
        if self.record_status is not None:
            raise ValueError(
                "insufficient_evidence disambiguation_state requires "
                "record_status to be null (canonical_scholar_id null) "
                "(CON-SRC-0008 AC-3)"
            )
        if self.positions:
            raise ValueError(
                "insufficient_evidence disambiguation_state requires "
                "positions to be empty (CON-SRC-0008 AC-3)"
            )


# ---------------------------------------------------------------------------
# Stage-1 evidence packet types
# ---------------------------------------------------------------------------


class NormalizedFragment(BaseModel):
    """5-component name parse per REQ-SRC-0050.

    The structured 5-tuple of an Arabic scholarly name fragment after
    bidi-strip + honorific normalization (INV-SRC-0014 strict ordering).
    REQ-SRC-0050 implementation in Session 2 will populate this; for
    Session 1 we only need the data shape to round-trip through the
    evidence packet contract.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ism: Optional[str] = None
    kunyah: Optional[str] = None
    nasab_chain: list[str] = Field(default_factory=list)
    laqab: list[str] = Field(default_factory=list)
    nisba_list: list[str] = Field(default_factory=list)


class ScholarCandidate(BaseModel):
    """One Stage-1 narrowed candidate inside the evidence packet.

    Per CON-SRC-0009 line 67-70: candidates carry their canonical id, the
    canonical Arabic name, a per-channel score breakdown (dict[channel →
    score]; channel set tightened in Session 2 with REQ-SRC-0051), and a
    provenance label naming which Stage-1 channel surfaced this candidate.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    canonical_id: str = Field(min_length=1)
    canonical_name_ar: str = Field(min_length=1)
    score_breakdown: dict[str, float] = Field(default_factory=dict)
    provenance_for_inclusion: str = Field(min_length=1)

    @model_validator(mode="after")
    def _validate_score_breakdown_range(self) -> "ScholarCandidate":
        """Each Stage-1 channel score must be in [0, 1]."""
        for channel, score in self.score_breakdown.items():
            if not 0.0 <= score <= 1.0:
                raise ValueError(
                    f"ScholarCandidate.score_breakdown[{channel!r}]={score} "
                    "is outside [0.0, 1.0]"
                )
        return self


class DossierContext(BaseModel):
    """Upstream context bundle attached to the evidence packet.

    Per CON-SRC-0009 line 60-66: genre + primary_science + century estimates +
    school hints + attributed works + geographic signals + work-title
    extracts. All fields optional/empty-default — different sources surface
    different evidence; the packet captures whatever the dossier had.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    genre: Optional[str] = None
    primary_science: Optional[str] = None
    century_active_hijri_estimates: list[int] = Field(default_factory=list)
    school_affiliation_hints: dict[str, Optional[str]] = Field(
        default_factory=dict
    )
    attributed_works: list[str] = Field(default_factory=list)
    geographic_signals: list[str] = Field(default_factory=list)
    work_title_extracts: list[str] = Field(default_factory=list)


# ---------------------------------------------------------------------------
# Top-level contract: CON-SRC-0009 ScholarEvidencePacket
# ---------------------------------------------------------------------------


class ScholarEvidencePacket(BaseModel):
    """Immutable Stage-1 evidence bundle (CON-SRC-0009).

    Locked at the end of REQ-SRC-0051 deterministic candidate generation.
    Round-0 and round-1 verifiers receive THE SAME packet byte-identically
    (round-1 cannot introduce new candidates per INV-SRC-0016 chosen_id
    closure).

    Source-snippet bounds:
      - At most ``SOURCE_SNIPPETS_MAX`` (5) snippets
      - Each snippet at most ``SOURCE_SNIPPET_MAX_BYTES`` (2048) UTF-8 bytes
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    normalized_fragment: str = Field(min_length=1)
    display_fragment: str = Field(min_length=1)
    match_key: str = Field(min_length=1)
    parsed_components: NormalizedFragment
    dossier_context: DossierContext
    candidate_set: list[ScholarCandidate] = Field(default_factory=list)
    source_snippets: list[str] = Field(default_factory=list)
    registry_release_version: str = Field(min_length=1)

    @model_validator(mode="before")
    @classmethod
    def _reject_forbidden_field_names(cls, data: Any) -> Any:
        """Reject snapshot_version per Codex Stage-3 Defect 2."""
        return _reject_snapshot_version(data)

    @model_validator(mode="after")
    def _validate_packet_bounds(self) -> "ScholarEvidencePacket":
        """Enforce CON-SRC-0009 bounded-size invariants."""
        if len(self.candidate_set) > K_CAP_DEGRADED:
            raise ValueError(
                f"ScholarEvidencePacket.candidate_set length "
                f"{len(self.candidate_set)} exceeds K_CAP_DEGRADED="
                f"{K_CAP_DEGRADED} (REQ-SRC-0051 K cap = 8 standard / "
                "12 degraded)"
            )
        if len(self.source_snippets) > SOURCE_SNIPPETS_MAX:
            raise ValueError(
                f"ScholarEvidencePacket.source_snippets length "
                f"{len(self.source_snippets)} exceeds SOURCE_SNIPPETS_MAX="
                f"{SOURCE_SNIPPETS_MAX} (CON-SRC-0009)"
            )
        for idx, snippet in enumerate(self.source_snippets):
            byte_len = len(snippet.encode("utf-8"))
            if byte_len > SOURCE_SNIPPET_MAX_BYTES:
                raise ValueError(
                    f"ScholarEvidencePacket.source_snippets[{idx}] is "
                    f"{byte_len} UTF-8 bytes; max is "
                    f"{SOURCE_SNIPPET_MAX_BYTES} (CON-SRC-0009)"
                )
        # Detect duplicate canonical_ids in candidate_set — the packet must
        # uniquely identify each candidate so INV-SRC-0016 chosen_id closure
        # against the set is unambiguous at round-1.
        ids = [c.canonical_id for c in self.candidate_set]
        if len(ids) != len(set(ids)):
            raise ValueError(
                "ScholarEvidencePacket.candidate_set contains duplicate "
                "canonical_id values; each candidate must be unique "
                "(INV-SRC-0016 chosen_id closure requires unambiguous "
                "membership)"
            )
        return self

    def is_chosen_id_in_candidate_set(self, chosen_id: str) -> bool:
        """INV-SRC-0016 closure check: is the chosen id within this packet?

        Round-1 verifier outputs are validated against the locked packet's
        candidate_set. An out-of-set chosen_id is an F-4 hallucination
        (model "remembered" a scholar from training data outside the
        deterministic Stage-1 narrowing) and must be rejected by the
        orchestrator.
        """
        return any(c.canonical_id == chosen_id for c in self.candidate_set)


__all__ = [
    "K_CAP_STANDARD",
    "K_CAP_DEGRADED",
    "SOURCE_SNIPPETS_MAX",
    "SOURCE_SNIPPET_MAX_BYTES",
    "VERIFIER_ROUND_CAP",
    "DisambiguationState",
    "RecordStatus",
    "EvidenceType",
    "RoundCount",
    "CitationRef",
    "ScoreBreakdown",
    "VerifierRecord",
    "ThresholdAudit",
    "CareerPhaseRef",
    "Position",
    "RevisionHistoryEntry",
    "ScholarMatchProvenance",
    "ScholarMatchResult",
    "NormalizedFragment",
    "ScholarCandidate",
    "DossierContext",
    "ScholarEvidencePacket",
    "ScoredCandidate",
    "VerifierEmission",
]
