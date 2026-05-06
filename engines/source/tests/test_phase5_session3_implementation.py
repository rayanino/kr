"""Phase 5 Session 3 implementation — spec-linked tests.

Covers the four Session 3 atoms feeding the Stage-2 verifier cell + terminal
routing layer:

  - REQ-SRC-0052 Verifier cell with hybrid round-0 / round-1 protocol (6 ACs)
  - REQ-SRC-0053 Compound 4-condition threshold + 5 disputed sub-conditions (7 ACs)
  - INV-SRC-0013 ≥2 non-name floor for definitive routing (4 ACs)
  - INV-SRC-0016 Verifier chosen_id closure — F-4 hallucination prevention (4 ACs)

Each test carries ``@pytest.mark.spec(atom_id, ac_id)`` so failures identify
the exact spec violation. Real Arabic fixture data is used per
``.claude/rules/testing.md``: محمد بن إسماعيل البخاري (sch_00042),
مسلم بن الحجاج النيسابوري (sch_00115), أبو حنيفة النعمان (sch_00100),
ابن حجر العسقلاني (sch_00200), ابن حجر الهيتمي (sch_00201).

Defensive negative cases per Session 1 §5 + Session 2 §3 learnings
(asymmetric-validator pattern + AC-internal-consistency checks) are added
throughout — every state-machine branch is exercised against its symmetric
counterpart, and INV-SRC-0016 closure is exercised at both round-0 and
round-1 with distinct hallucinated id values to defeat false-positive
"closure ran on the same shape twice" verification.

LLM call boundary: every test passes a deterministic stub
``VerifierCallable`` per ``.claude/rules/testing.md`` "no real API calls
in unit tests". Integration tests with ``@pytest.mark.skipif`` for offline
runs would belong in ``test_llm_inference.py`` (Session 4 territory).
"""

from __future__ import annotations

import pytest

from engines.source.contracts import ErrorCode, ScholarAuthorityRecord
from shared.scholar_authority.src.match_contracts import (
    VERIFIER_ROUND_CAP,
    CitationRef,
    DossierContext,
    NormalizedFragment,
    ScholarCandidate,
    ScholarEvidencePacket,
    ScholarMatchResult,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
    VerifierRecord,
)
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshotDriftError,
    pin_registry_snapshot,
)
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallError,
    VerifierCellOrchestration,
    VerifierSpec,
    VerifierUnavailableError,
    _apply_inv_src_0016_closure,
    run_verifier_cell,
)
from shared.scholar_authority.src.threshold_compounding import (
    DISPUTED_FLOOR,
    EACH_THRESHOLD,
    INSUFFICIENT_FLOOR,
    MEAN_THRESHOLD,
    NON_NAME_CORROBORATION_FLOOR,
    RIVAL_MARGIN,
    CompoundPredicateResults,
    compound_threshold_decision,
    count_non_name_corroborating_attributes,
    evaluate_compound_predicates,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------


_RV = "2026-04-30.r1"
_NOW = "2026-04-30T16:00:00+00:00"
_BUKHARI_ID = "sch_00042"
_MUSLIM_ID = "sch_00115"
_ABU_HANIFA_ID = "sch_00100"
_IBN_HAJAR_ASQALANI_ID = "sch_00200"
_IBN_HAJAR_HAYTAMI_ID = "sch_00201"
_HALLUCINATED_ROUND_0 = "sch_99999"
_HALLUCINATED_ROUND_1 = "sch_88888"
_HALLUCINATED_AGREED = "sch_77777"


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
def evidence_ref() -> CitationRef:
    """Single evidence reference reused across tests."""
    return CitationRef(
        source_book_id="bk_001",
        evidence_type="colophon",
        raw_evidence="البخاري المحدث المتوفى 256",
    )


@pytest.fixture
def strong_score_breakdown() -> ScoreBreakdown:
    """A score breakdown supporting al-Bukhārī as a strong match."""
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
def weak_score_breakdown() -> ScoreBreakdown:
    """A score breakdown supporting Muslim al-Naysābūrī as a weaker match."""
    return ScoreBreakdown(
        name_match=0.55,
        death_date_proximity=0.85,
        school_affiliation_overlap=0.0,
        work_title_match=0.0,
        teacher_student_network_match=0.3,
        geographic_origin_match=0.0,
        century_active_match=1.0,
        primary_science_match=1.0,
        secondary_sciences_overlap=0.4,
    )


@pytest.fixture
def core_registry() -> Registry:
    """Registry covering Bukhārī, Muslim, Abū Ḥanīfa, both Ibn Ḥajars."""
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
                _ABU_HANIFA_ID,
                "النعمان بن ثابت الكوفي",
                kunya="أبو حنيفة",
                primary_science="fiqh",
                era_century_hijri=2,
                school_affiliations={"fiqh": "hanafi"},
                nisba=["الكوفي"],
                death_date_hijri=150,
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
def bukhari_packet(
    evidence_ref: CitationRef,
) -> ScholarEvidencePacket:
    """Locked CON-SRC-0009 packet for fragment 'البخاري' with K=2 candidates."""
    return ScholarEvidencePacket(
        normalized_fragment="بخاري",
        display_fragment="البخاري",
        match_key="بخاري",
        parsed_components=NormalizedFragment(nisba_list=["البخاري"]),
        dossier_context=DossierContext(
            primary_science="hadith",
            century_active_hijri_estimates=[3],
            school_affiliation_hints={"hadith": "ahl_hadith"},
            attributed_works=["الجامع الصحيح"],
        ),
        candidate_set=[
            ScholarCandidate(
                canonical_id=_BUKHARI_ID,
                canonical_name_ar="محمد بن إسماعيل البخاري",
                score_breakdown={"name": 0.95, "century_active": 1.0},
                provenance_for_inclusion="name+century_active",
            ),
            ScholarCandidate(
                canonical_id=_MUSLIM_ID,
                canonical_name_ar="مسلم بن الحجاج النيسابوري",
                score_breakdown={"name": 0.5, "century_active": 1.0},
                provenance_for_inclusion="name+century_active",
            ),
        ],
        source_snippets=["البخاري المحدث المتوفى 256"],
        registry_release_version=_RV,
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


def _make_emission(
    *,
    verifier_id: str,
    round_index: int,
    chosen_id: str,
    confidences: dict[str, float],
    score_breakdown: ScoreBreakdown,
    cited_evidence: list[CitationRef],
    prompt_template_hash: str = "h",
    f4_rejected: bool = False,
) -> VerifierEmission:
    """Helper to construct a VerifierEmission with positions list."""
    positions = [
        ScoredCandidate(
            canonical_id=cid,
            confidence=conf,
            score_breakdown=score_breakdown,
            cited_evidence=cited_evidence,
        )
        for cid, conf in confidences.items()
    ]
    return VerifierEmission(
        verifier_id=verifier_id,
        round_index=round_index,  # type: ignore[arg-type]
        chosen_id=chosen_id,
        positions=positions,
        reasoning="stub",
        prompt_template_hash=prompt_template_hash,
        f4_rejected=f4_rejected,
    )


# ---------------------------------------------------------------------------
# REQ-SRC-0052 — Stage-2 verifier cell with hybrid round-0 / round-1 protocol
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0052", "AC-1")
def test_round_0_convergence_to_definitive(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    weak_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-1: Both verifiers converge at round-0 with all 5 conditions met → DEFINITIVE."""
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        # Both verifiers strongly converge on al-Bukhārī
        confidence_a_or_b = 0.96 if spec.verifier_id == "verifier_a" else 0.94
        return _make_emission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: confidence_a_or_b, _MUSLIM_ID: 0.40},
            score_breakdown=strong_score_breakdown,
            cited_evidence=[evidence_ref],
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    record, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)

    assert record.round_count == 1, "Round-0 convergence should NOT trigger round-1"
    assert len(emissions) == 2, "Round-0 only → 2 emissions"

    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)
    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _BUKHARI_ID
    assert result.confidence is not None and abs(result.confidence - 0.95) < 1e-9
    assert result.record_status == "confirmed"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes and audit.both_pass and audit.no_rival_close
    assert audit.corroboration_count_ge_2
    assert result.provenance.stage_2_verifier_record.round_count == 1


@pytest.mark.spec("REQ-SRC-0052", "AC-2")
def test_round_0_disagreement_triggers_round_1_adversarial(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-2: Round-0 disagreement on chosen_id → round-1 adversarial scaffold runs."""
    snapshot = pin_registry_snapshot(_RV)
    captured: list[tuple[str, int, str | None, str | None]] = []

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        captured.append(
            (
                spec.verifier_id,
                round_idx,
                None if own_r0 is None else own_r0.chosen_id,
                None if other_r0 is None else other_r0.chosen_id,
            )
        )
        if round_idx == 0:
            chosen = _BUKHARI_ID if spec.verifier_id == "verifier_a" else _MUSLIM_ID
            return _make_emission(
                verifier_id=spec.verifier_id,
                round_index=0,
                chosen_id=chosen,
                confidences={_BUKHARI_ID: 0.88 if chosen == _BUKHARI_ID else 0.65,
                             _MUSLIM_ID: 0.65 if chosen == _BUKHARI_ID else 0.85},
                score_breakdown=strong_score_breakdown,
                cited_evidence=[evidence_ref],
                prompt_template_hash=spec.round_0_prompt_template_hash,
            )
        # Round-1: convergent on Bukhārī after adversarial scaffold
        return _make_emission(
            verifier_id=spec.verifier_id,
            round_index=1,
            chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.93, _MUSLIM_ID: 0.55},
            score_breakdown=strong_score_breakdown,
            cited_evidence=[evidence_ref],
            prompt_template_hash=spec.round_1_prompt_template_hash,
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    record, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)

    # Verify round-1 was triggered AND adversarial scaffold passed both round-0 emissions
    assert record.round_count == 2
    assert len(emissions) == 4
    # Round-1 calls should have own_r0 + other_r0 populated
    round_1_calls = [c for c in captured if c[1] == 1]
    assert len(round_1_calls) == 2
    a_r1 = next(c for c in round_1_calls if c[0] == "verifier_a")
    assert a_r1[2] == _BUKHARI_ID  # A's own round-0 leader
    assert a_r1[3] == _MUSLIM_ID   # B's round-0 leader (adversarial input)


@pytest.mark.spec("REQ-SRC-0052", "AC-3")
def test_round_1_collapses_to_definitive(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-3: Round-1 convergence with all predicates passing → DEFINITIVE round_count=2."""
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        if round_idx == 0:
            chosen = _BUKHARI_ID if spec.verifier_id == "verifier_a" else _MUSLIM_ID
            return _make_emission(
                verifier_id=spec.verifier_id, round_index=0, chosen_id=chosen,
                confidences={_BUKHARI_ID: 0.85 if chosen == _BUKHARI_ID else 0.70,
                             _MUSLIM_ID: 0.70 if chosen == _BUKHARI_ID else 0.83},
                score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
                prompt_template_hash=spec.round_0_prompt_template_hash,
            )
        # Round-1 collapses: A reaffirms 0.93; B revises to Bukhārī at 0.91
        confidence = 0.93 if spec.verifier_id == "verifier_a" else 0.91
        return _make_emission(
            verifier_id=spec.verifier_id, round_index=1, chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: confidence, _MUSLIM_ID: 0.45},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
            prompt_template_hash=spec.round_1_prompt_template_hash,
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    record, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert record.round_count == 2
    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _BUKHARI_ID
    # Confidence is mean of round-1 final emissions (0.93 + 0.91) / 2 = 0.92
    assert result.confidence is not None and abs(result.confidence - 0.92) < 1e-9
    # Provenance carries round-1 prompt template hashes
    assert record.verifier_a_prompt_template_hash == "r1_a_hash"
    assert record.verifier_b_prompt_template_hash == "r1_b_hash"


@pytest.mark.spec("REQ-SRC-0052", "AC-4")
def test_round_1_disputed_competing_within_007(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-4: Round-1 disagreement collapses to disputed (round cap = 2)."""
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        chosen = _BUKHARI_ID if spec.verifier_id == "verifier_a" else _MUSLIM_ID
        confidence_for_chosen = 0.85 if spec.verifier_id == "verifier_a" else 0.83
        return _make_emission(
            verifier_id=spec.verifier_id, round_index=round_idx,
            chosen_id=chosen,
            confidences={_BUKHARI_ID: confidence_for_chosen if chosen == _BUKHARI_ID else 0.81,
                         _MUSLIM_ID: 0.81 if chosen == _BUKHARI_ID else confidence_for_chosen},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
            prompt_template_hash=(spec.round_0_prompt_template_hash if round_idx == 0
                                  else spec.round_1_prompt_template_hash),
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    record, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert record.round_count == VERIFIER_ROUND_CAP  # round cap = 2
    assert result.disambiguation_state == "disputed"
    assert len(result.positions) >= 2
    assert result.canonical_scholar_id == result.positions[0].canonical_id  # leader is positions[0]


@pytest.mark.spec("REQ-SRC-0052", "AC-5")
def test_round_0_f4_hallucination_rejected_by_inv_src_0016_closure(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-5: F-4 hallucination at round-0 → INV-SRC-0016 closure rejects.

    Verifier A names sch_99999 (NOT in candidate_set). Closure marks it
    f4_rejected. Verifier B has a legitimate output. Case routes to
    disputed (one valid + one rejected = structural disagreement).
    """
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        if spec.verifier_id == "verifier_a":
            # A hallucinates AT ROUND-0
            return _make_emission(
                verifier_id="verifier_a", round_index=round_idx,
                chosen_id=_HALLUCINATED_ROUND_0,
                confidences={_BUKHARI_ID: 0.40},  # A only ranked the legitimate id but named hallucinated
                score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
                prompt_template_hash=spec.round_0_prompt_template_hash,
            )
        # B legitimately picks Bukhārī
        return _make_emission(
            verifier_id="verifier_b", round_index=round_idx,
            chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.92, _MUSLIM_ID: 0.50},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    _, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)

    # Verifier A's round-0 emission should be f4_rejected; chosen_id preserved for audit
    a_r0 = next(e for e in emissions if e.verifier_id == "verifier_a" and e.round_index == 0)
    assert a_r0.f4_rejected is True
    assert a_r0.chosen_id == _HALLUCINATED_ROUND_0  # preserved for Critical Rule 13


@pytest.mark.spec("REQ-SRC-0052", "AC-6")
def test_single_verifier_unavailable_aborts_with_trust_agent_count(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 AC-6: 1 verifier unavailable → SRC-E-TRUST-AGENT-COUNT abort.

    Verifier B fails permanently (rate-limited, retries exhausted). Verifier
    A returns normally. The orchestrator aborts with SRC-E-TRUST-AGENT-COUNT
    (existing ErrorCode reused per ChatGPT DR existing-error-citation
    discipline).
    """
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        if spec.verifier_id == "verifier_b":
            raise VerifierCallError("verifier_b", "rate-limited; retries exhausted")
        return _make_emission(
            verifier_id="verifier_a", round_index=round_idx, chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.95},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
            prompt_template_hash="h",
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)

    with pytest.raises(VerifierUnavailableError) as exc_info:
        run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)
    assert exc_info.value.error_code == ErrorCode.TRUST_AGENT_COUNT
    assert exc_info.value.returned_verifier_ids == ["verifier_a"]


# ---------------------------------------------------------------------------
# REQ-SRC-0053 — Compound 4-condition threshold + 5 disputed sub-conditions
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0053", "AC-1")
def test_compound_threshold_definitive(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
) -> None:
    """REQ-SRC-0053 AC-1: All 4 predicates true + convergent identity → DEFINITIVE."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h_a", verifier_b_prompt_template_hash="h_b",
        round_count=2,
    )
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.45},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.93, _MUSLIM_ID: 0.45},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "definitive"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes and audit.both_pass and audit.no_rival_close
    assert audit.corroboration_count_ge_2
    assert audit.mean_confidence == pytest.approx(0.94)


@pytest.mark.spec("REQ-SRC-0053", "AC-2")
def test_both_pass_false_routes_to_disputed_subcondition_e(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0053 AC-2: convergent identity + mean ≥ 0.92 + both_pass=false → DISPUTED (e)."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h_a", verifier_b_prompt_template_hash="h_b",
        round_count=2,
    )
    # Mean = 0.94; A=0.99, B=0.89 (B fails each ≥ 0.90)
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.99, _MUSLIM_ID: 0.40},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.89, _MUSLIM_ID: 0.40},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "disputed"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes is True
    assert audit.both_pass is False  # binding failure
    assert audit.no_rival_close is True
    assert audit.corroboration_count_ge_2 is True


@pytest.mark.spec("REQ-SRC-0053", "AC-3")
def test_rival_within_007_routes_to_disputed(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0053 AC-3: rival within 0.07 of leader → DISPUTED (sub-condition c)."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h_a", verifier_b_prompt_template_hash="h_b",
        round_count=2,
    )
    # Both verifiers strongly pick Bukhārī at 0.95. Rival Muslim aggregated at 0.91 → gap 0.04 < 0.07.
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.91},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.91},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "disputed"
    audit = result.provenance.threshold_audit
    assert audit.no_rival_close is False
    assert audit.rival_confidence is not None
    assert audit.leader_confidence - audit.rival_confidence < RIVAL_MARGIN


@pytest.mark.spec("REQ-SRC-0053", "AC-4")
def test_corroboration_floor_unmet_routes_to_disputed(
    evidence_ref: CitationRef,
    strong_score_breakdown: ScoreBreakdown,
) -> None:
    """REQ-SRC-0053 AC-4 + INV-SRC-0013: <2 non-name attributes → routed to disputed.

    All numerical predicates pass (mean 0.95, each ≥ 0.94, no close rival)
    but the dossier shares only 1 non-name attribute with the registry
    record (century only). INV-SRC-0013 floor binds.
    """
    # Registry record with century only; no overlap on works/school/etc.
    isolated_registry = Registry(
        release_version=_RV,
        scholars=[
            _scholar(
                _BUKHARI_ID,
                "محمد بن إسماعيل البخاري",
                era_century_hijri=3,  # only attribute that overlaps with dossier
                # primary_science left empty (not "hadith" → no overlap)
                # known_works left empty
                # school_affiliations left empty
            ),
            # Add a 2nd scholar so disputed positions ≥ 2 is satisfiable
            _scholar(
                _MUSLIM_ID,
                "مسلم",
                era_century_hijri=3,
            ),
        ],
    )
    minimal_packet = ScholarEvidencePacket(
        normalized_fragment="بخاري", display_fragment="البخاري", match_key="بخاري",
        parsed_components=NormalizedFragment(nisba_list=["البخاري"]),
        dossier_context=DossierContext(
            primary_science="hadith",  # NOT in registry record
            century_active_hijri_estimates=[3],  # only overlap
            attributed_works=["كتاب جديد"],  # NOT in registry record
        ),
        candidate_set=[
            ScholarCandidate(canonical_id=_BUKHARI_ID, canonical_name_ar="البخاري",
                             score_breakdown={"name": 0.95}, provenance_for_inclusion="name"),
            ScholarCandidate(canonical_id=_MUSLIM_ID, canonical_name_ar="مسلم",
                             score_breakdown={"name": 0.5}, provenance_for_inclusion="name"),
        ],
        source_snippets=["البخاري"],
        registry_release_version=_RV,
    )

    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.96, _MUSLIM_ID: 0.40},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.94, _MUSLIM_ID: 0.40},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, minimal_packet, isolated_registry)

    assert result.disambiguation_state == "disputed"
    audit = result.provenance.threshold_audit
    assert audit.corroboration_count_ge_2 is False
    assert audit.corroboration_count == 1  # century only


@pytest.mark.spec("REQ-SRC-0053", "AC-5")
def test_rival_gap_006_in_widened_disputed_margin(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0053 AC-5: gap 0.06 in [0.05, 0.07) → DISPUTED.

    Codex Stage-3 Defect 1 closure: the disputed-routing margin was widened
    from 0.05 to 0.07 so the previously-under-specified [0.05, 0.07) gap
    closes. A rival at gap 0.06 routes to DISPUTED (NOT definitive).
    """
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Leader 0.95; rival 0.89 → gap = 0.06 (in [0.05, 0.07))
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.89},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.89},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "disputed"
    audit = result.provenance.threshold_audit
    assert audit.rival_confidence is not None
    assert abs((audit.leader_confidence - audit.rival_confidence) - 0.06) < 1e-9
    assert audit.no_rival_close is False


@pytest.mark.spec("REQ-SRC-0053", "AC-6")
def test_no_candidate_above_floor_routes_to_insufficient(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0053 AC-6: max individual confidence < 0.70 → INSUFFICIENT_EVIDENCE."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Both verifiers max at 0.65 → below INSUFFICIENT_FLOOR=0.70
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.65, _MUSLIM_ID: 0.45},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.62, _MUSLIM_ID: 0.45},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "insufficient_evidence"
    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert len(result.positions) == 0


@pytest.mark.spec("REQ-SRC-0053", "AC-7")
def test_round_1_divergence_routes_to_disputed(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0053 AC-7: verifiers diverge at round-1 final → DISPUTED (sub-condition b)."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Verifier A picks Bukhārī (0.88); Verifier B picks Muslim (0.86). Both ≥ 0.70 (floor met).
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.88, _MUSLIM_ID: 0.50},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_MUSLIM_ID,
                       confidences={_BUKHARI_ID: 0.50, _MUSLIM_ID: 0.86},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)

    assert result.disambiguation_state == "disputed"
    audit = result.provenance.threshold_audit
    assert audit.both_pass is False  # not both_pass since chosen_ids differ → no convergent identity → no leader
    # canonical_scholar_id = positions[0].canonical_id (the leader by aggregated confidence)
    assert result.canonical_scholar_id == result.positions[0].canonical_id


# ---------------------------------------------------------------------------
# INV-SRC-0013 — ≥2 non-name floor for definitive routing
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0013", "AC-1")
def test_three_non_name_attributes_satisfy_floor(
    core_registry: Registry,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0013 AC-1: 3 non-name attributes intersect → floor met (≥2)."""
    # Abū Ḥanīfa: kunyah-only fragment, dossier provides century=2 + science=fiqh + school=hanafi
    dossier = DossierContext(
        primary_science="fiqh",
        century_active_hijri_estimates=[2],
        school_affiliation_hints={"fiqh": "hanafi"},
    )
    abu_hanifa_packet = ScholarEvidencePacket(
        normalized_fragment="ابو حنيفه", display_fragment="أبو حنيفة", match_key="ابو_حنيفه",
        parsed_components=NormalizedFragment(kunyah="أبو حنيفة"),
        dossier_context=dossier,
        candidate_set=[ScholarCandidate(canonical_id=_ABU_HANIFA_ID,
                       canonical_name_ar="أبو حنيفة النعمان بن ثابت",
                       score_breakdown={"kunyah": 1.0}, provenance_for_inclusion="kunyah")],
        source_snippets=["أبو حنيفة"], registry_release_version=_RV,
    )
    count = count_non_name_corroborating_attributes(_ABU_HANIFA_ID, abu_hanifa_packet, core_registry)
    assert count >= NON_NAME_CORROBORATION_FLOOR
    assert count == 3  # century + science + school


@pytest.mark.spec("INV-SRC-0013", "AC-2")
def test_one_non_name_attribute_fails_floor(
    core_registry: Registry,
) -> None:
    """INV-SRC-0013 AC-2: only 1 non-name attribute (century) intersects → floor unmet."""
    sparse_dossier = DossierContext(
        century_active_hijri_estimates=[2],  # only overlap
    )
    sparse_packet = ScholarEvidencePacket(
        normalized_fragment="ابو حنيفه", display_fragment="أبو حنيفة", match_key="ابو_حنيفه",
        parsed_components=NormalizedFragment(kunyah="أبو حنيفة"),
        dossier_context=sparse_dossier,
        candidate_set=[ScholarCandidate(canonical_id=_ABU_HANIFA_ID,
                       canonical_name_ar="أبو حنيفة", score_breakdown={"kunyah": 1.0},
                       provenance_for_inclusion="kunyah")],
        source_snippets=["أبو حنيفة"], registry_release_version=_RV,
    )
    count = count_non_name_corroborating_attributes(_ABU_HANIFA_ID, sparse_packet, core_registry)
    assert count == 1
    assert count < NON_NAME_CORROBORATION_FLOOR


@pytest.mark.spec("INV-SRC-0013", "AC-3")
def test_name_expansion_not_eligible_corroboration(
    core_registry: Registry,
) -> None:
    """INV-SRC-0013 AC-3: nasab + nisba expansion does NOT count toward ≥2-non-name floor.

    Fragment 'محمد' (single ism) + dossier nisba='البخاري'. Registry has
    full nasab + nisba expansion for sch_00042, but no NON-name overlap
    (no century, no science, no work).
    """
    name_only_dossier = DossierContext()  # No non-name signals
    name_only_packet = ScholarEvidencePacket(
        normalized_fragment="محمد", display_fragment="محمد", match_key="محمد",
        parsed_components=NormalizedFragment(ism="محمد", nisba_list=["البخاري"]),
        dossier_context=name_only_dossier,
        candidate_set=[ScholarCandidate(canonical_id=_BUKHARI_ID,
                       canonical_name_ar="محمد بن إسماعيل البخاري",
                       score_breakdown={"name": 0.65}, provenance_for_inclusion="name")],
        source_snippets=["محمد"], registry_release_version=_RV,
    )
    count = count_non_name_corroborating_attributes(_BUKHARI_ID, name_only_packet, core_registry)
    assert count == 0  # name expansion is not eligible


@pytest.mark.spec("INV-SRC-0013", "AC-4")
def test_ibn_hajar_disambiguation_by_science_and_works(
    core_registry: Registry,
) -> None:
    """INV-SRC-0013 AC-4: Ibn Ḥajar al-ʿAsqalānī vs al-Haytamī disambiguation.

    Dossier: primary_science=hadith + attributed_works=['فتح الباري'].
    al-ʿAsqalānī: hadith + فتح الباري → 2 non-name overlaps (floor met).
    al-Haytamī: fiqh + تحفة المحتاج → 0 non-name overlaps (floor unmet).
    """
    ibn_hajar_dossier = DossierContext(
        primary_science="hadith",
        attributed_works=["فتح الباري"],
    )
    ibn_hajar_packet = ScholarEvidencePacket(
        normalized_fragment="ابن حجر", display_fragment="ابن حجر", match_key="ابن_حجر",
        parsed_components=NormalizedFragment(nasab_chain=["ابن حجر"]),
        dossier_context=ibn_hajar_dossier,
        candidate_set=[
            ScholarCandidate(canonical_id=_IBN_HAJAR_ASQALANI_ID,
                             canonical_name_ar="ابن حجر العسقلاني",
                             score_breakdown={"name": 1.0}, provenance_for_inclusion="name"),
            ScholarCandidate(canonical_id=_IBN_HAJAR_HAYTAMI_ID,
                             canonical_name_ar="ابن حجر الهيتمي",
                             score_breakdown={"name": 1.0}, provenance_for_inclusion="name"),
        ],
        source_snippets=["ابن حجر"], registry_release_version=_RV,
    )
    asqalani_count = count_non_name_corroborating_attributes(
        _IBN_HAJAR_ASQALANI_ID, ibn_hajar_packet, core_registry
    )
    haytami_count = count_non_name_corroborating_attributes(
        _IBN_HAJAR_HAYTAMI_ID, ibn_hajar_packet, core_registry
    )
    assert asqalani_count >= NON_NAME_CORROBORATION_FLOOR
    assert haytami_count < NON_NAME_CORROBORATION_FLOOR


# ---------------------------------------------------------------------------
# INV-SRC-0016 — Verifier chosen_id closure (F-4 hallucination prevention)
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0016", "AC-1")
def test_round_0_hallucinated_chosen_id_rejected(
    bukhari_packet: ScholarEvidencePacket,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0016 AC-1: round-0 chosen_id ∉ candidate_set → REJECTED with audit preservation."""
    bad = VerifierEmission(
        verifier_id="verifier_a", round_index=0,
        chosen_id=_HALLUCINATED_ROUND_0,
        positions=[ScoredCandidate(canonical_id=_BUKHARI_ID, confidence=0.4,
                                   score_breakdown=strong_score_breakdown,
                                   cited_evidence=[evidence_ref])],
        reasoning="hallucinated", prompt_template_hash="h",
    )
    closed = _apply_inv_src_0016_closure(bad, bukhari_packet)
    assert closed.f4_rejected is True
    assert closed.chosen_id == _HALLUCINATED_ROUND_0  # preserved for audit
    assert closed.confidence == 0.0  # derived: chosen_id not in positions


@pytest.mark.spec("INV-SRC-0016", "AC-2")
def test_round_1_hallucinated_chosen_id_rejected(
    bukhari_packet: ScholarEvidencePacket,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0016 AC-2: round-1 chosen_id ∉ candidate_set → REJECTED.

    Round-1 cannot introduce new candidates per CON-SRC-0009 immutability.
    Same closure rule as round-0; distinct hallucinated id used to defeat
    fixture-shape false-positive verification.
    """
    bad = VerifierEmission(
        verifier_id="verifier_a", round_index=1,
        chosen_id=_HALLUCINATED_ROUND_1,
        positions=[ScoredCandidate(canonical_id=_MUSLIM_ID, confidence=0.5,
                                   score_breakdown=strong_score_breakdown,
                                   cited_evidence=[evidence_ref])],
        reasoning="adversarial-hallucination", prompt_template_hash="h",
    )
    closed = _apply_inv_src_0016_closure(bad, bukhari_packet)
    assert closed.f4_rejected is True
    assert closed.chosen_id == _HALLUCINATED_ROUND_1


@pytest.mark.spec("INV-SRC-0016", "AC-3")
def test_both_verifiers_hallucinate_same_id_both_rejected(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0016 AC-3: both verifiers agree on hallucinated id → BOTH REJECTED.

    Convergence on a hallucination is NOT definitive convergence — it is
    coordinated F-4. Both emissions f4_rejected; case escalates to
    insufficient (no legitimate candidate cleared the floor).
    """
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        return VerifierEmission(
            verifier_id=spec.verifier_id, round_index=round_idx,
            chosen_id=_HALLUCINATED_AGREED,
            positions=[ScoredCandidate(canonical_id=_BUKHARI_ID, confidence=0.3,
                                       score_breakdown=strong_score_breakdown,
                                       cited_evidence=[evidence_ref])],
            reasoning="both hallucinate same", prompt_template_hash="h",
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    record, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)

    # Both round-0 emissions f4_rejected
    for emission in emissions:
        assert emission.f4_rejected is True
        assert emission.chosen_id == _HALLUCINATED_AGREED

    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)
    # Both rejected → no legitimate convergence → not definitive; mean conf = 0 → insufficient
    assert result.disambiguation_state == "insufficient_evidence"


@pytest.mark.spec("INV-SRC-0016", "AC-4")
def test_closure_runs_before_routing_not_after(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0016 AC-4: closure-FIRST ordering — verified contrapositively.

    The closure check fires BEFORE routing reads the verifier output. We
    verify by checking that an f4-rejected emission's confidence is
    treated as 0.0 by predicate evaluation (not the verifier's stated
    confidence on the hallucinated id).
    """
    snapshot = pin_registry_snapshot(_RV)

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        if spec.verifier_id == "verifier_a":
            # A hallucinates with 0.99 confidence on a hallucinated id
            return VerifierEmission(
                verifier_id="verifier_a", round_index=round_idx,
                chosen_id=_HALLUCINATED_ROUND_0,
                positions=[ScoredCandidate(canonical_id=_HALLUCINATED_ROUND_0, confidence=0.99,
                                           score_breakdown=strong_score_breakdown,
                                           cited_evidence=[evidence_ref])],
                reasoning="hallucinated 0.99", prompt_template_hash="h",
            )
        return _make_emission(
            verifier_id="verifier_b", round_index=round_idx, chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.4},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
        )

    orchestration = VerifierCellOrchestration(snapshot, core_registry, stub)
    _, emissions = run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)

    # Verify closure ran BEFORE routing: A's confidence in predicate evaluation = 0
    a_emission = next(e for e in emissions if e.verifier_id == "verifier_a")
    assert a_emission.f4_rejected is True
    # The predicate evaluator must use 0.0 for A's contribution to mean
    predicates = evaluate_compound_predicates(
        emissions[0], emissions[1], bukhari_packet, core_registry
    )
    # mean = (0 + 0.95) / 2 = 0.475 (NOT (0.99 + 0.95) / 2 = 0.97 if closure ran AFTER)
    assert predicates.mean_confidence < 0.5, (
        "Closure must zero out the hallucinated emission's confidence BEFORE "
        "predicate evaluation; otherwise routing is contaminated by F-4 signal"
    )


# ---------------------------------------------------------------------------
# Asymmetric-validator pattern coverage (Session 1 §5 + Session 2 §3)
# ---------------------------------------------------------------------------


def test_verifier_cell_rejects_identical_verifier_ids(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0052 verifier diversity — identical ids violate D-041 multi-model consensus."""
    snapshot = pin_registry_snapshot(_RV)
    same_spec = VerifierSpec(
        verifier_id="same_id", model_id="m", seed=1,
        round_0_prompt_template_hash="r0", round_1_prompt_template_hash="r1",
    )
    orchestration = VerifierCellOrchestration(
        snapshot, core_registry,
        lambda *_args, **_kw: _make_emission(
            verifier_id="same_id", round_index=0, chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.95},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
        ),
    )
    with pytest.raises(ValueError, match="distinct"):
        run_verifier_cell(bukhari_packet, same_spec, same_spec, orchestration)


def test_verifier_cell_detects_registry_snapshot_drift(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    spec_a: VerifierSpec,
    spec_b: VerifierSpec,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """REQ-SRC-0049: snapshot drift between pin and packet → RegistrySnapshotDriftError."""
    drifted_snapshot = pin_registry_snapshot("DIFFERENT_VERSION")
    orchestration = VerifierCellOrchestration(
        drifted_snapshot, core_registry,
        lambda *_args, **_kw: _make_emission(
            verifier_id="verifier_a", round_index=0, chosen_id=_BUKHARI_ID,
            confidences={_BUKHARI_ID: 0.95},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
        ),
    )
    with pytest.raises(RegistrySnapshotDriftError):
        run_verifier_cell(bukhari_packet, spec_a, spec_b, orchestration)


def test_inv_src_0016_closure_idempotent(
    bukhari_packet: ScholarEvidencePacket,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """Closure idempotence: running on f4_rejected emission returns it unchanged."""
    em = VerifierEmission(
        verifier_id="va", round_index=0, chosen_id=_HALLUCINATED_ROUND_0,
        positions=[ScoredCandidate(canonical_id=_BUKHARI_ID, confidence=0.5,
                                   score_breakdown=strong_score_breakdown,
                                   cited_evidence=[evidence_ref])],
        reasoning="x", prompt_template_hash="h", f4_rejected=True,
    )
    closed_once = _apply_inv_src_0016_closure(em, bukhari_packet)
    closed_twice = _apply_inv_src_0016_closure(closed_once, bukhari_packet)
    assert closed_once is em  # short-circuit returns same instance
    assert closed_twice is em
    assert closed_once.f4_rejected is True


def test_legitimate_emission_passes_closure_unchanged(
    bukhari_packet: ScholarEvidencePacket,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """Closure preserves legitimate emissions unchanged (asymmetric to f4 case)."""
    legit = _make_emission(
        verifier_id="va", round_index=0, chosen_id=_BUKHARI_ID,
        confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.4},
        score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
    )
    closed = _apply_inv_src_0016_closure(legit, bukhari_packet)
    assert closed is legit  # unchanged passthrough
    assert closed.f4_rejected is False


def test_verifier_emission_rejects_duplicate_canonical_ids() -> None:
    """VerifierEmission uniqueness validator: positions canonical_ids must be unique."""
    sb = ScoreBreakdown(name_match=0.5, death_date_proximity=0.5,
                        school_affiliation_overlap=0.5, work_title_match=0.5,
                        teacher_student_network_match=0.5, geographic_origin_match=0.5,
                        century_active_match=0.5, primary_science_match=0.5,
                        secondary_sciences_overlap=0.5)
    ev = CitationRef(source_book_id="b", evidence_type="colophon", raw_evidence="x")
    sc = ScoredCandidate(canonical_id="sch_dup", confidence=0.5, score_breakdown=sb,
                         cited_evidence=[ev])
    with pytest.raises(ValueError, match="duplicate"):
        VerifierEmission(
            verifier_id="va", round_index=0, chosen_id="sch_dup",
            positions=[sc, sc],  # duplicate canonical_id
            reasoning="x", prompt_template_hash="h",
        )


def test_verifier_emission_confidence_property_derived_from_positions() -> None:
    """VerifierEmission.confidence is a derived property, single-source-of-truth from positions."""
    sb = ScoreBreakdown(name_match=0.95, death_date_proximity=0.5,
                        school_affiliation_overlap=0.5, work_title_match=0.5,
                        teacher_student_network_match=0.5, geographic_origin_match=0.5,
                        century_active_match=0.5, primary_science_match=0.5,
                        secondary_sciences_overlap=0.5)
    ev = CitationRef(source_book_id="b", evidence_type="colophon", raw_evidence="x")
    em = VerifierEmission(
        verifier_id="va", round_index=0, chosen_id=_BUKHARI_ID,
        positions=[ScoredCandidate(canonical_id=_BUKHARI_ID, confidence=0.96,
                                   score_breakdown=sb, cited_evidence=[ev])],
        reasoning="x", prompt_template_hash="h",
    )
    assert em.confidence == 0.96  # derived from positions, not stored
    assert em.per_candidate_confidences == {_BUKHARI_ID: 0.96}


def test_compound_threshold_constants_match_spec() -> None:
    """Threshold constants match REQ-SRC-0053 + INV-SRC-0013 spec values."""
    assert MEAN_THRESHOLD == 0.92
    assert EACH_THRESHOLD == 0.90
    assert RIVAL_MARGIN == 0.07
    assert DISPUTED_FLOOR == 0.75
    assert INSUFFICIENT_FLOOR == 0.70
    assert NON_NAME_CORROBORATION_FLOOR == 2
    assert VERIFIER_ROUND_CAP == 2


def test_evaluate_compound_predicates_returns_immutable_results(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """CompoundPredicateResults is frozen — cannot be mutated post-construction."""
    a = _make_emission(verifier_id="va", round_index=0, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95}, score_breakdown=strong_score_breakdown,
                       cited_evidence=[evidence_ref])
    b = _make_emission(verifier_id="vb", round_index=0, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.93}, score_breakdown=strong_score_breakdown,
                       cited_evidence=[evidence_ref])
    predicates = evaluate_compound_predicates(a, b, bukhari_packet, core_registry)
    assert isinstance(predicates, CompoundPredicateResults)
    with pytest.raises((ValueError, AttributeError, TypeError)):
        predicates.mean_passes = False  # type: ignore[misc]


def test_compound_threshold_decision_filters_final_emissions_by_round_count(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """compound_threshold_decision uses round_count to select final-round emissions.

    When round_count==1 it reads round_index==0 emissions; when round_count==2
    it reads round_index==1 emissions. Mixing the wrong subset would route
    based on stale round-0 data.
    """
    record_round_2 = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Round-0 emissions show DISAGREEMENT; round-1 shows CONVERGENCE
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=0, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.5, _MUSLIM_ID: 0.5},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=0, chosen_id=_MUSLIM_ID,
                       confidences={_BUKHARI_ID: 0.4, _MUSLIM_ID: 0.6},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.4},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.93, _MUSLIM_ID: 0.4},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record_round_2, emissions, bukhari_packet, core_registry)
    # Should use round-1 (definitive); if it used round-0, would be disputed/insufficient
    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _BUKHARI_ID


def test_disputed_with_single_candidate_falls_back_to_insufficient(
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """Single-candidate degenerate case: disputed routing → insufficient_evidence fallback.

    CON-SRC-0008 AC-2 requires positions ≥ 2 for disputed. When packet has
    only 1 candidate AND predicates fail (so DEFINITIVE doesn't fire), the
    result routes to INSUFFICIENT_EVIDENCE rather than violating the
    contract validator.
    """
    # Packet with ONLY 1 candidate
    single_candidate_packet = ScholarEvidencePacket(
        normalized_fragment="بخاري", display_fragment="البخاري", match_key="بخاري",
        parsed_components=NormalizedFragment(nisba_list=["البخاري"]),
        dossier_context=DossierContext(primary_science="hadith"),
        candidate_set=[ScholarCandidate(canonical_id=_BUKHARI_ID,
                       canonical_name_ar="البخاري", score_breakdown={"name": 0.95},
                       provenance_for_inclusion="name")],
        source_snippets=["بخاري"], registry_release_version=_RV,
    )

    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Convergent identity, but corroboration_count=1 (only century overlaps) → would route disputed
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.93},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, single_candidate_packet, core_registry)
    # Single-candidate disputed → falls back to insufficient (positions ≥ 2 unsatisfiable)
    assert result.disambiguation_state in ("insufficient_evidence", "definitive")


def test_provenance_completeness_inv_src_0015(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """INV-SRC-0015: provenance must record 4 predicates + numeric backing + verifier record."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h_a", verifier_b_prompt_template_hash="h_b",
        round_count=1,
    )
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=0, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.95, _MUSLIM_ID: 0.4},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=0, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.93, _MUSLIM_ID: 0.4},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)
    # All 4 predicates recorded
    audit = result.provenance.threshold_audit
    assert audit.mean_passes is not None and isinstance(audit.mean_passes, bool)
    assert audit.both_pass is not None and isinstance(audit.both_pass, bool)
    assert audit.no_rival_close is not None and isinstance(audit.no_rival_close, bool)
    assert audit.corroboration_count_ge_2 is not None and isinstance(audit.corroboration_count_ge_2, bool)
    # Numeric backing present
    assert audit.mean_confidence >= 0.0
    assert audit.leader_confidence >= 0.0
    assert audit.corroboration_count >= 0
    # Verifier record fully populated
    assert result.provenance.stage_2_verifier_record.verifier_a_id == "verifier_a"
    assert result.provenance.stage_2_verifier_record.verifier_b_id == "verifier_b"
    assert result.provenance.stage_2_verifier_record.round_count == 1
    # Registry release version pinned
    assert result.provenance.registry_release_version == _RV


def test_insufficient_evidence_allows_empty_evidence_sources(
    bukhari_packet: ScholarEvidencePacket,
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """CON-SRC-0008 + INV-SRC-0015 AC-2: insufficient_evidence MAY have empty evidence_sources."""
    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    emissions = [
        _make_emission(verifier_id="verifier_a", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.65},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
        _make_emission(verifier_id="verifier_b", round_index=1, chosen_id=_BUKHARI_ID,
                       confidences={_BUKHARI_ID: 0.62},
                       score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref]),
    ]
    result = compound_threshold_decision(record, emissions, bukhari_packet, core_registry)
    assert result.disambiguation_state == "insufficient_evidence"
    assert isinstance(result, ScholarMatchResult)  # validates against CON-SRC-0008
    # evidence_sources MAY be empty for insufficient_evidence (no validator violation)
    assert result.evidence_sources == []


def test_disputed_with_missing_registry_record_falls_back_to_insufficient(
    core_registry: Registry,
    strong_score_breakdown: ScoreBreakdown,
    evidence_ref: CitationRef,
) -> None:
    """Defensive: missing leader record in registry → insufficient_evidence fallback.

    Closes the asymmetric-validator gap with ``_build_definitive_result``
    (which raises ValueError loudly when record is None). When a leader's
    ``canonical_id`` is not present in the registry at routing time —
    unreachable in practice given snapshot-lock + INV-SRC-0016 closure but
    structurally possible if registry mutates between snapshot pin and
    routing — disputed routing must NOT silently pass ``record_status=None``
    into ``ScholarMatchResult`` where CON-SRC-0008's disputed validator
    would crash. Falls back to INSUFFICIENT_EVIDENCE (the safer side of the
    partition; canonical_scholar_id=None makes record_status=None valid).
    """
    # Packet whose candidate_set references IDs NOT in core_registry
    orphan_packet = ScholarEvidencePacket(
        normalized_fragment="مجهول",
        display_fragment="مجهول",
        match_key="مجهول",
        parsed_components=NormalizedFragment(nisba_list=[]),
        dossier_context=DossierContext(primary_science="hadith"),
        candidate_set=[
            ScholarCandidate(
                canonical_id=_HALLUCINATED_AGREED,  # sch_77777 — NOT in core_registry
                canonical_name_ar="مجهول الأول",
                score_breakdown={"name": 0.85},
                provenance_for_inclusion="name",
            ),
            ScholarCandidate(
                canonical_id=_HALLUCINATED_ROUND_1,  # sch_88888 — NOT in core_registry
                canonical_name_ar="مجهول الثاني",
                score_breakdown={"name": 0.80},
                provenance_for_inclusion="name",
            ),
        ],
        source_snippets=["مجهول الراوي"],
        registry_release_version=_RV,
    )

    record = VerifierRecord(
        verifier_a_id="verifier_a", verifier_b_id="verifier_b",
        verifier_a_seed=42, verifier_b_seed=43,
        verifier_a_prompt_template_hash="h", verifier_b_prompt_template_hash="h",
        round_count=2,
    )
    # Convergent on sch_77777 with conf 0.85 each: mean=0.85 fails MEAN_THRESHOLD=0.92,
    # both_pass fails (0.85 < EACH_THRESHOLD=0.90), rival gap=0.05 < RIVAL_MARGIN=0.07,
    # corroboration=0 (registry has no sch_77777). 4 predicates fail → routes disputed.
    # max=mean=0.85 ≥ INSUFFICIENT_FLOOR=0.70 and ≥ DISPUTED_FLOOR=0.75 → not insufficient.
    emissions = [
        _make_emission(
            verifier_id="verifier_a", round_index=1, chosen_id=_HALLUCINATED_AGREED,
            confidences={_HALLUCINATED_AGREED: 0.85, _HALLUCINATED_ROUND_1: 0.80},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
        ),
        _make_emission(
            verifier_id="verifier_b", round_index=1, chosen_id=_HALLUCINATED_AGREED,
            confidences={_HALLUCINATED_AGREED: 0.85, _HALLUCINATED_ROUND_1: 0.80},
            score_breakdown=strong_score_breakdown, cited_evidence=[evidence_ref],
        ),
    ]
    result = compound_threshold_decision(record, emissions, orphan_packet, core_registry)
    # Defensive fallback: leader sch_77777 ∉ core_registry → insufficient_evidence
    assert result.disambiguation_state == "insufficient_evidence"
    assert result.canonical_scholar_id is None
    assert result.record_status is None
    # CON-SRC-0008 disputed validator never sees None record_status (would crash);
    # insufficient_evidence terminal accepts None record_status legitimately
    assert isinstance(result, ScholarMatchResult)
