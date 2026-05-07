"""Phase 5 Session 4 — scholar_match_cell orchestrator tests (DEC-SRC-0013).

Covers the four-stage orchestrator wiring per DEC-SRC-0013:

    parse_fragment → narrow_candidates → run_verifier_cell →
    compound_threshold_decision → ScholarMatchResult

Three terminal paths inside the orchestrator:

  1. Normal — verifier cell runs and routes per REQ-SRC-0053
  2. Empty candidate_set after Stage-1 → insufficient_evidence (degenerate)
  3. VerifierUnavailableError caught → insufficient_evidence (degenerate)

Plus the propagation contract:

  - FragmentNotArabicError / HonorificOnlyNameError / CompoundNameSplitError
    propagate from parse_fragment without being caught.
  - RegistrySnapshotDriftError propagates per INV-SRC-0017 — catching
    here would mask the drift signal.

Asymmetric-validator-pattern audit (Sessions 1+3 generalized defect class):
the two degenerate-case insufficient_evidence constructors must construct
threshold_audit and verifier_record with IDENTICAL discipline. This file
includes a dedicated test asserting byte-equality of the threshold_audit
and verifier_record produced by the two paths under the same orchestration
spec.

LLM call boundary: every test passes a deterministic stub VerifierCallable
per ``.claude/rules/testing.md``. End-to-end tests with the real chain
through parse_fragment + narrow_candidates live in
``test_phase5_session4_integration.py`` (sub-task 5).
"""

from __future__ import annotations

import pytest

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.fragment_parser import (
    FragmentNotArabicError,
)
from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    DossierContext,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
    VerifierRecord,
)
from shared.scholar_authority.src.scholar_match_cell import (
    ScholarMatchCellOrchestration,
    scholar_match_cell,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshotDriftError,
    pin_registry_snapshot,
)
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallError,
    VerifierSpec,
)


# ---------------------------------------------------------------------------
# Fixture constants — shared with Session 3 tests for cross-session sanity.
# ---------------------------------------------------------------------------

_RV = "2026-05-04.r1"
_NOW = "2026-05-04T16:00:00+00:00"
_BUKHARI_ID = "sch_00042"
_MUSLIM_ID = "sch_00115"
_IBN_HAJAR_ASQALANI_ID = "sch_00200"
_IBN_HAJAR_HAYTAMI_ID = "sch_00201"


def _scholar(
    canonical_id: str, name: str, **kwargs: object
) -> ScholarAuthorityRecord:
    """Build a ScholarAuthorityRecord with sane Phase-5 defaults."""
    return ScholarAuthorityRecord(
        canonical_id=canonical_id,
        canonical_name_ar=name,
        last_updated=_NOW,
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.fixture
def core_registry() -> Registry:
    """Registry covering Bukhārī, Muslim, both Ibn Ḥajars."""
    return Registry(
        release_version=_RV,
        scholars=[
            _scholar(
                _BUKHARI_ID,
                "محمد بن إسماعيل البخاري",
                primary_science="hadith",
                era_century_hijri=3,
                nisba=["البخاري"],
                known_works=["الجامع الصحيح", "التاريخ الكبير"],
                school_affiliations={"hadith": "ahl_hadith"},
                death_date_hijri=256,
            ),
            _scholar(
                _MUSLIM_ID,
                "مسلم بن الحجاج النيسابوري",
                primary_science="hadith",
                era_century_hijri=3,
                nisba=["النيسابوري"],
                known_works=["صحيح مسلم"],
                death_date_hijri=261,
            ),
            _scholar(
                _IBN_HAJAR_ASQALANI_ID,
                "أحمد بن علي بن حجر العسقلاني",
                primary_science="hadith",
                era_century_hijri=9,
                nisba=["العسقلاني"],
                known_works=["فتح الباري"],
                school_affiliations={"fiqh": "shafii", "hadith": "ahl_hadith"},
                death_date_hijri=852,
            ),
            _scholar(
                _IBN_HAJAR_HAYTAMI_ID,
                "أحمد بن محمد بن حجر الهيتمي",
                primary_science="fiqh",
                era_century_hijri=10,
                nisba=["الهيتمي"],
                known_works=["تحفة المحتاج"],
                school_affiliations={"fiqh": "shafii"},
                death_date_hijri=974,
            ),
        ],
    )


@pytest.fixture
def evidence_ref() -> CitationRef:
    return CitationRef(
        source_book_id="bk_001",
        evidence_type="colophon",
        raw_evidence="البخاري المحدث المتوفى 256",
    )


@pytest.fixture
def strong_score_breakdown() -> ScoreBreakdown:
    return ScoreBreakdown(
        name_match=0.95,
        death_date_proximity=0.9,
        school_affiliation_overlap=0.85,
        work_title_match=1.0,
        teacher_student_network_match=0.6,
        geographic_origin_match=0.7,
        century_active_match=1.0,
        primary_science_match=1.0,
        secondary_sciences_overlap=0.65,
    )


@pytest.fixture
def spec_a() -> VerifierSpec:
    return VerifierSpec(
        verifier_id="verifier_a",
        model_id="openrouter/anthropic/claude-opus-4.6",
        seed=42,
        round_0_prompt_template_hash="r0_a_hash",
        round_1_prompt_template_hash="r1_a_hash",
    )


@pytest.fixture
def spec_b() -> VerifierSpec:
    return VerifierSpec(
        verifier_id="verifier_b",
        model_id="openrouter/cohere/command-a",
        seed=43,
        round_0_prompt_template_hash="r0_b_hash",
        round_1_prompt_template_hash="r1_b_hash",
    )


# ---------------------------------------------------------------------------
# DEC-SRC-0013 — orchestrator wiring tests
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013")
def test_normal_path_produces_definitive(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """End-to-end through scholar_match_cell with convergent stub verifiers → DEFINITIVE.

    This test runs the orchestrator on a fragment + dossier that the Stage-1
    narrowing can resolve to ≥1 candidates. The deterministic stub verifiers
    converge at round-0 with all 5 conditions met — the cell routes to
    DEFINITIVE per REQ-SRC-0053 + REQ-SRC-0052 AC-1.
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        confidence = 0.96 if spec.verifier_id == "verifier_a" else 0.94
        positions = [
            ScoredCandidate(
                canonical_id=_BUKHARI_ID,
                confidence=confidence,
                score_breakdown=strong_score_breakdown,
                cited_evidence=[evidence_ref],
            ),
        ]
        if any(c.canonical_id == _MUSLIM_ID for c in pkt.candidate_set):
            positions.append(
                ScoredCandidate(
                    canonical_id=_MUSLIM_ID,
                    confidence=0.4,
                    score_breakdown=strong_score_breakdown,
                    cited_evidence=[evidence_ref],
                )
            )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_BUKHARI_ID,
            positions=positions,
            reasoning="stub",
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    snapshot = pin_registry_snapshot(_RV)
    orchestration = ScholarMatchCellOrchestration(
        registry=core_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext(
        primary_science="hadith",
        century_active_hijri_estimates=[3],
        school_affiliation_hints={"hadith": "ahl_hadith"},
        attributed_works=["الجامع الصحيح"],
    )

    result = scholar_match_cell("البخاري", dossier, orchestration)

    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _BUKHARI_ID
    assert result.confidence is not None
    assert result.record_status == "confirmed"
    assert result.provenance.registry_release_version == _RV
    assert result.provenance.stage_2_verifier_record.round_count == 1


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-3")
def test_empty_candidate_set_routes_to_insufficient_evidence(
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """Stage-1 produces 0 candidates → insufficient_evidence with degenerate provenance.

    The registry intentionally has no scholars matching the fragment + dossier;
    Stage-1 narrowing produces an empty candidate_set. The orchestrator
    short-circuits BEFORE invoking the verifier cell and emits
    insufficient_evidence with the degenerate provenance shape per
    INV-SRC-0015 AC-2.
    """
    empty_registry = Registry(release_version=_RV, scholars=[])
    snapshot = pin_registry_snapshot(_RV)

    invocation_log: list[str] = []

    def stub_should_not_run(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        invocation_log.append(spec.verifier_id)
        raise AssertionError("Verifier must not run when candidate_set is empty")

    orchestration = ScholarMatchCellOrchestration(
        registry=empty_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub_should_not_run,
    )

    dossier = DossierContext()
    result = scholar_match_cell("البخاري", dossier, orchestration)

    assert invocation_log == [], "Verifier must not be invoked on empty narrowing"
    assert result.disambiguation_state == "insufficient_evidence"
    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert result.evidence_sources == []
    assert result.positions == []
    assert result.provenance.registry_release_version == _RV
    audit = result.provenance.threshold_audit
    assert not audit.mean_passes
    assert not audit.both_pass
    assert not audit.no_rival_close
    assert not audit.corroboration_count_ge_2
    assert audit.mean_confidence == 0.0
    assert audit.leader_confidence == 0.0
    assert audit.rival_confidence is None
    assert audit.corroboration_count == 0
    record = result.provenance.stage_2_verifier_record
    assert record.verifier_a_id == "verifier_a"
    assert record.verifier_b_id == "verifier_b"
    assert record.verifier_a_seed == 42
    assert record.verifier_b_seed == 43
    assert record.round_count == 0  # Session 7: zero-invocation path; no verifier ran


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0052", "AC-6")
def test_verifier_unavailable_routes_to_insufficient_evidence(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """REQ-SRC-0052 AC-6 — both verifier callbacks fail → VerifierUnavailableError caught.

    The orchestrator catches the VerifierUnavailableError raised by
    run_verifier_cell when fewer than 2 verifiers return non-VerifierCallError
    outputs. It then emits insufficient_evidence with the same degenerate
    provenance shape used by the empty-candidate-set path
    (asymmetric-validator-pattern symmetry).
    """

    def stub_always_fails(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        raise VerifierCallError(
            verifier_id=spec.verifier_id,
            message="LLM call failed permanently after exhausting retries",
        )

    snapshot = pin_registry_snapshot(_RV)
    orchestration = ScholarMatchCellOrchestration(
        registry=core_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub_always_fails,
    )

    dossier = DossierContext(
        primary_science="hadith",
        century_active_hijri_estimates=[3],
        attributed_works=["الجامع الصحيح"],
    )
    result = scholar_match_cell("البخاري", dossier, orchestration)

    assert result.disambiguation_state == "insufficient_evidence"
    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert result.positions == []
    assert result.provenance.registry_release_version == _RV
    audit = result.provenance.threshold_audit
    assert not audit.mean_passes
    assert not audit.corroboration_count_ge_2
    assert audit.mean_confidence == 0.0
    assert result.provenance.stage_2_verifier_record.round_count == 0  # Session 7: zero-invocation


@pytest.mark.spec("DEC-SRC-0013", "INV-SRC-0017")
def test_snapshot_drift_propagates_unmasked(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """INV-SRC-0017 — snapshot drift raised by narrow_candidates is NOT caught.

    The orchestrator must never mask a snapshot drift signal: per INV-SRC-0017
    the case aborts with EXPLICIT REPLAY at the higher-level pipeline.
    Catching here would corrupt the audit trail.
    """
    snapshot = pin_registry_snapshot("2026-01-01.r0")  # ≠ core_registry.release_version

    def stub_should_not_run(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        raise AssertionError("Verifier must not run when drift is detected")

    orchestration = ScholarMatchCellOrchestration(
        registry=core_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub_should_not_run,
    )

    dossier = DossierContext()
    with pytest.raises(RegistrySnapshotDriftError) as exc_info:
        scholar_match_cell("البخاري", dossier, orchestration)
    assert exc_info.value.pinned_version == "2026-01-01.r0"
    assert exc_info.value.observed_version == _RV


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0050")
def test_fragment_not_arabic_propagates_unmasked(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """REQ-SRC-0050 — non-Arabic fragment raises FragmentNotArabicError unmasked.

    Input-shape errors from parse_fragment must propagate so callers can
    handle them upstream. The orchestrator does not attempt recovery;
    callers must validate fragment shape before invoking the cell.
    """
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        raise AssertionError("Verifier must not run when fragment is non-Arabic")

    orchestration = ScholarMatchCellOrchestration(
        registry=core_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    with pytest.raises(FragmentNotArabicError):
        scholar_match_cell("Bukhari", DossierContext(), orchestration)


@pytest.mark.spec("DEC-SRC-0013", "INV-SRC-0015")
def test_provenance_completeness_on_definitive_path(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0015 AC-1 — definitive results carry all 4 provenance predicates populated."""

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        confidence = 0.96 if spec.verifier_id == "verifier_a" else 0.94
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_BUKHARI_ID,
            positions=[
                ScoredCandidate(
                    canonical_id=_BUKHARI_ID,
                    confidence=confidence,
                    score_breakdown=strong_score_breakdown,
                    cited_evidence=[evidence_ref],
                ),
            ],
            reasoning="stub",
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    snapshot = pin_registry_snapshot(_RV)
    orchestration = ScholarMatchCellOrchestration(
        registry=core_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext(
        primary_science="hadith",
        century_active_hijri_estimates=[3],
        school_affiliation_hints={"hadith": "ahl_hadith"},
        attributed_works=["الجامع الصحيح"],
    )
    result = scholar_match_cell("البخاري", dossier, orchestration)

    audit = result.provenance.threshold_audit
    assert audit.mean_passes
    assert audit.both_pass
    assert audit.no_rival_close
    assert audit.corroboration_count_ge_2
    assert audit.mean_confidence > 0.0
    assert audit.leader_confidence > 0.0
    assert audit.corroboration_count >= 2
    record = result.provenance.stage_2_verifier_record
    assert record.verifier_a_id == "verifier_a"
    assert record.verifier_b_id == "verifier_b"
    assert record.verifier_a_seed == 42
    assert record.verifier_b_seed == 43
    assert record.verifier_a_prompt_template_hash == "r0_a_hash"
    assert record.verifier_b_prompt_template_hash == "r0_b_hash"
    assert record.round_count == 1
    assert result.provenance.registry_release_version == _RV


@pytest.mark.spec("DEC-SRC-0013")
def test_asymmetric_validator_audit_degenerate_paths_share_discipline(
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """Asymmetric-validator-pattern audit: the two degenerate insufficient_evidence
    paths produce IDENTICAL threshold_audit AND verifier_record under the same
    orchestration spec.

    Sessions 1+3 surfaced this defect class twice: state-machine constructors
    diverging in subtle ways between branches that should be symmetric. This
    test locks in symmetry so any future change to one constructor must update
    the other.

    Different inputs:
      - Path A: empty registry → empty candidate_set → no-candidates path
      - Path B: populated registry + always-failing verifier → unavailable path

    What MUST match: threshold_audit (all-False / 0.0); verifier_record
    (round_count=0 per Session 7 RoundCount Literal[0, 1, 2] cleanup,
    ids/seeds/hashes from specs); audit-trail completeness.

    What MAY differ: stage_1_score_breakdown (empty for path A; populated for
    path B); registry_release_version (must be the snapshot's value in both).
    """
    snapshot = pin_registry_snapshot(_RV)

    # Path A — empty registry → empty candidate_set
    empty_registry = Registry(release_version=_RV, scholars=[])

    def stub_no_run(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        raise AssertionError("Verifier must not run on empty narrowing")

    result_a = scholar_match_cell(
        "البخاري",
        DossierContext(),
        ScholarMatchCellOrchestration(
            registry=empty_registry,
            snapshot=snapshot,
            verifier_a_spec=spec_a,
            verifier_b_spec=spec_b,
            call_verifier=stub_no_run,
        ),
    )

    # Path B — populated registry but verifier always fails
    def stub_always_fails(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        raise VerifierCallError(
            verifier_id=spec.verifier_id, message="permanent failure"
        )

    result_b = scholar_match_cell(
        "البخاري",
        DossierContext(
            primary_science="hadith",
            century_active_hijri_estimates=[3],
            attributed_works=["الجامع الصحيح"],
        ),
        ScholarMatchCellOrchestration(
            registry=core_registry,
            snapshot=snapshot,
            verifier_a_spec=spec_a,
            verifier_b_spec=spec_b,
            call_verifier=stub_always_fails,
        ),
    )

    # Both must reach the same insufficient_evidence terminal.
    assert result_a.disambiguation_state == "insufficient_evidence"
    assert result_b.disambiguation_state == "insufficient_evidence"

    # threshold_audit MUST be byte-identical (all False / 0.0 / None / 0).
    assert result_a.provenance.threshold_audit == result_b.provenance.threshold_audit

    # verifier_record MUST be byte-identical under the same orchestration spec.
    assert (
        result_a.provenance.stage_2_verifier_record
        == result_b.provenance.stage_2_verifier_record
    )

    # registry_release_version MUST be the pinned snapshot value in both.
    assert (
        result_a.provenance.registry_release_version
        == result_b.provenance.registry_release_version
        == _RV
    )

    # stage_1_score_breakdown MAY differ — empty registry produces no candidates
    # so the stage-1 surface is empty; populated registry produces ≥1 candidate
    # so the stage-1 surface is non-empty. The asymmetry is correct.
    assert result_a.provenance.stage_1_score_breakdown == {}
    assert result_b.provenance.stage_1_score_breakdown != {}


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008")
def test_round_count_literal_accepts_zero() -> None:
    """RoundCount Literal[0, 1, 2] accepts 0 for the zero-invocation degenerate path.

    Phase 5 Session 7 cleanup (2026-05-07): RoundCount was widened from
    Literal[1, 2] to Literal[0, 1, 2] so degenerate verifier_records can
    record round_count=0 byte-faithfully (no verifier ran) instead of the
    prior "round_count=1 with all-False threshold_audit" floor workaround.

    This defensive test exercises Pydantic validation directly against
    each value of the Literal so that any future narrowing of the type
    immediately surfaces a test failure.
    """
    for round_count_value in (0, 1, 2):
        record = VerifierRecord(
            verifier_a_id="verifier_a",
            verifier_b_id="verifier_b",
            verifier_a_seed=42,
            verifier_b_seed=43,
            verifier_a_prompt_template_hash="r0_a_hash",
            verifier_b_prompt_template_hash="r0_b_hash",
            round_count=round_count_value,  # type: ignore[arg-type]
        )
        assert record.round_count == round_count_value


@pytest.mark.spec("DEC-SRC-0013")
def test_orchestration_bundle_keeps_signature_at_three_params() -> None:
    """python-code.md ≤5-param rule — orchestration bundle keeps public sig small.

    Defensive structural test: the public scholar_match_cell function takes
    exactly 3 parameters (fragment, dossier, orchestration). All other
    dependencies are folded into the orchestration bundle. Future enhancements
    must extend the bundle, NOT add positional parameters.
    """
    import inspect

    sig = inspect.signature(scholar_match_cell)
    assert list(sig.parameters.keys()) == ["fragment", "dossier", "orchestration"]


@pytest.mark.spec("DEC-SRC-0013")
def test_orchestration_bundle_is_frozen() -> None:
    """The DI bundle is frozen — case state cannot be mutated mid-orchestration.

    Soft mirror of CON-SRC-0009's hard immutability for the evidence packet.
    Mutability of the bundle would let a verifier or test stub silently change
    snapshot identity mid-case, breaking INV-SRC-0017.
    """
    import dataclasses

    assert dataclasses.is_dataclass(ScholarMatchCellOrchestration)
    fields = dataclasses.fields(ScholarMatchCellOrchestration)
    assert len(fields) == 6
    # Frozen dataclasses raise FrozenInstanceError on attribute write.
    snapshot = pin_registry_snapshot(_RV)
    spec = VerifierSpec(
        verifier_id="v",
        model_id="m",
        seed=0,
        round_0_prompt_template_hash="h",
        round_1_prompt_template_hash="h1",
    )
    spec_other = VerifierSpec(
        verifier_id="v_other",
        model_id="m",
        seed=0,
        round_0_prompt_template_hash="h",
        round_1_prompt_template_hash="h1",
    )
    bundle = ScholarMatchCellOrchestration(
        registry=Registry(release_version=_RV, scholars=[]),
        snapshot=snapshot,
        verifier_a_spec=spec,
        verifier_b_spec=spec_other,
        call_verifier=lambda *args, **kwargs: None,  # type: ignore[arg-type, return-value]
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        bundle.snapshot = snapshot  # type: ignore[misc]
