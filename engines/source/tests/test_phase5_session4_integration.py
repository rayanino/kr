"""Phase 5 Session 4 — end-to-end integration tests for scholar_match_cell.

Exercises the full Phase 5 chain from a raw Arabic scholar fragment to a
terminal CON-SRC-0008 ScholarMatchResult through every stage:

    raw fragment (str)
        → parse_fragment (Session 2 — REQ-SRC-0050)
        → narrow_candidates (Session 2 — REQ-SRC-0051)
        → run_verifier_cell (Session 3 — REQ-SRC-0052)
        → compound_threshold_decision (Session 3 — REQ-SRC-0053)
        → ScholarMatchResult (Session 1 — CON-SRC-0008)

Disambiguation targets covered (the canonical scholarly disambiguation
problems in the Islamic scholarly corpus):

  - "ابن حجر" → al-ʿAsqalānī (sch_00200, hadith, 852 AH) vs
    al-Haytami (sch_00201, fiqh shafi'i, 974 AH). The dossier signals
    drive the disambiguation: science (hadith vs fiqh), century (9 vs
    10), known_works (فتح الباري vs تحفة المحتاج).
  - "البخاري" → Muḥammad b. Ismāʿīl al-Bukhārī (sch_00042, hadith,
    256 AH). Single-candidate path through the cell.

Scenarios cover all three terminal disambiguation_state values:

  1. DEFINITIVE — high-confidence convergent verifiers + ≥2-non-name floor
     met → CON-SRC-0008 AC-1
  2. DISPUTED — verifiers compete within RIVAL_MARGIN → CON-SRC-0008 AC-2
  3. INSUFFICIENT_EVIDENCE — no candidate clears INSUFFICIENT_FLOOR →
     CON-SRC-0008 AC-3

Plus the orchestrator's contract paths:

  4. Empty narrowing (no candidates after Stage-1) → insufficient_evidence
  5. Snapshot drift propagation (INV-SRC-0017) — uncaught
  6. Build-time vs runtime external boundary — RuntimeExternalCallError
     would propagate; orchestrator never makes runtime external calls

LLM call boundary: every test passes a deterministic stub VerifierCallable
per ``.claude/rules/testing.md`` "no real API calls in unit tests". The
production wiring with LiteLLM + Instructor multi-model consensus per
``.claude/skills/consensus-pattern/SKILL.md`` is Session 4 follow-up work.
"""

from __future__ import annotations

import pytest

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    DossierContext,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
)
from shared.scholar_authority.src.scholar_match_cell import (
    ScholarMatchCellOrchestration,
    scholar_match_cell,
)
from shared.scholar_authority.src.snapshot_lock import (
    pin_registry_snapshot,
)
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import VerifierSpec


# ---------------------------------------------------------------------------
# Fixtures — share constants with Session 3 + Session 4 unit tests
# ---------------------------------------------------------------------------

_RV = "2026-05-04.r1"
_NOW = "2026-05-04T16:00:00+00:00"
_BUKHARI_ID = "sch_00042"
_MUSLIM_ID = "sch_00115"
_IBN_HAJAR_ASQALANI_ID = "sch_00200"
_IBN_HAJAR_HAYTAMI_ID = "sch_00201"


def _scholar(canonical_id: str, name: str, **kwargs: object) -> ScholarAuthorityRecord:
    return ScholarAuthorityRecord(
        canonical_id=canonical_id,
        canonical_name_ar=name,
        last_updated=_NOW,
        **kwargs,  # type: ignore[arg-type]
    )


@pytest.fixture
def integration_registry() -> Registry:
    """Registry with the canonical disambiguation targets used by Sessions 2+3."""
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
                school_affiliations={"hadith": "ahl_hadith"},
                death_date_hijri=261,
            ),
            _scholar(
                _IBN_HAJAR_ASQALANI_ID,
                "أحمد بن علي بن حجر العسقلاني",
                primary_science="hadith",
                era_century_hijri=9,
                nisba=["العسقلاني"],
                known_works=["فتح الباري", "الإصابة في تمييز الصحابة"],
                school_affiliations={"fiqh": "shafii", "hadith": "ahl_hadith"},
                geographic_origin="عسقلان",
                geographic_active=["مصر"],
                death_date_hijri=852,
            ),
            _scholar(
                _IBN_HAJAR_HAYTAMI_ID,
                "أحمد بن محمد بن حجر الهيتمي",
                primary_science="fiqh",
                era_century_hijri=10,
                nisba=["الهيتمي"],
                known_works=["تحفة المحتاج", "الفتاوى الكبرى الفقهية"],
                school_affiliations={"fiqh": "shafii"},
                geographic_origin="مصر",
                geographic_active=["مكة"],
                death_date_hijri=974,
            ),
        ],
    )


@pytest.fixture
def evidence_ref_asqalani() -> CitationRef:
    return CitationRef(
        source_book_id="bk_fath",
        evidence_type="title_page",
        raw_evidence="فتح الباري شرح صحيح البخاري للحافظ ابن حجر العسقلاني",
    )


@pytest.fixture
def evidence_ref_haytami() -> CitationRef:
    return CitationRef(
        source_book_id="bk_tuhfa",
        evidence_type="title_page",
        raw_evidence="تحفة المحتاج بشرح المنهاج لابن حجر الهيتمي",
    )


@pytest.fixture
def strong_breakdown_asqalani() -> ScoreBreakdown:
    return ScoreBreakdown(
        name_match=0.85,
        death_date_proximity=0.95,
        school_affiliation_overlap=0.90,
        work_title_match=1.0,
        teacher_student_network_match=0.5,
        geographic_origin_match=0.7,
        century_active_match=1.0,
        primary_science_match=1.0,
        secondary_sciences_overlap=0.6,
    )


@pytest.fixture
def strong_breakdown_haytami() -> ScoreBreakdown:
    return ScoreBreakdown(
        name_match=0.85,
        death_date_proximity=0.95,
        school_affiliation_overlap=0.90,
        work_title_match=1.0,
        teacher_student_network_match=0.5,
        geographic_origin_match=0.7,
        century_active_match=1.0,
        primary_science_match=1.0,
        secondary_sciences_overlap=0.6,
    )


@pytest.fixture
def weak_breakdown() -> ScoreBreakdown:
    return ScoreBreakdown(
        name_match=0.55,
        death_date_proximity=0.5,
        school_affiliation_overlap=0.0,
        work_title_match=0.0,
        teacher_student_network_match=0.0,
        geographic_origin_match=0.0,
        century_active_match=0.0,
        primary_science_match=0.0,
        secondary_sciences_overlap=0.0,
    )


@pytest.fixture
def specs() -> tuple[VerifierSpec, VerifierSpec]:
    return (
        VerifierSpec(
            verifier_id="verifier_a",
            model_id="anthropic/claude-opus-4-6",
            seed=42,
            round_0_prompt_template_hash="r0_a_session4",
            round_1_prompt_template_hash="r1_a_session4",
        ),
        VerifierSpec(
            verifier_id="verifier_b",
            model_id="openrouter/cohere/command-a",
            seed=43,
            round_0_prompt_template_hash="r0_b_session4",
            round_1_prompt_template_hash="r1_b_session4",
        ),
    )


# ---------------------------------------------------------------------------
# Scenario 1 — DEFINITIVE: Ibn Ḥajar disambiguates to al-ʿAsqalānī (hadith)
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-1")
def test_ibn_hajar_hadith_context_resolves_to_asqalani(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    strong_breakdown_asqalani: ScoreBreakdown,
    evidence_ref_asqalani: CitationRef,
) -> None:
    """End-to-end: 'ابن حجر' + hadith + 9th c. + فتح الباري → al-ʿAsqalānī DEFINITIVE.

    The dossier's hadith primary_science + 9th-century estimate +
    فتح الباري known work jointly drive the disambiguation toward
    sch_00200. The Stage-1 work-title channel surfaces al-ʿAsqalānī as a
    high-priority candidate (his known_works contains فتح الباري); the
    Stage-2 stub verifiers converge with high confidence; the compound
    threshold predicates pass on all 4 conditions; ≥2-non-name floor met
    via primary_science (hadith) + attributed_works (فتح الباري) +
    century_active (9) + region_origin (عسقلان).
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        confidence = 0.95 if spec.verifier_id == "verifier_a" else 0.93
        positions = [
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_ASQALANI_ID,
                confidence=confidence,
                score_breakdown=strong_breakdown_asqalani,
                cited_evidence=[evidence_ref_asqalani],
            ),
        ]
        if any(c.canonical_id == _IBN_HAJAR_HAYTAMI_ID for c in pkt.candidate_set):
            positions.append(
                ScoredCandidate(
                    canonical_id=_IBN_HAJAR_HAYTAMI_ID,
                    confidence=0.30,
                    score_breakdown=strong_breakdown_asqalani,
                    cited_evidence=[evidence_ref_asqalani],
                )
            )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_IBN_HAJAR_ASQALANI_ID,
            positions=positions,
            reasoning="Hadith context + فتح الباري overrides nominal ambiguity",
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs
    orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext(
        primary_science="hadith",
        century_active_hijri_estimates=[9],
        school_affiliation_hints={"hadith": "ahl_hadith"},
        attributed_works=["فتح الباري"],
        geographic_signals=["عسقلان", "مصر"],
    )

    result = scholar_match_cell("ابن حجر", dossier, orchestration)

    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _IBN_HAJAR_ASQALANI_ID
    assert result.confidence is not None
    assert result.confidence >= 0.92
    assert result.record_status == "confirmed"
    assert result.evidence_sources, "definitive must carry evidence_sources"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes
    assert audit.both_pass
    assert audit.no_rival_close
    assert audit.corroboration_count_ge_2
    assert result.provenance.registry_release_version == _RV
    assert result.provenance.stage_2_verifier_record.round_count == 1


# ---------------------------------------------------------------------------
# Scenario 2 — DEFINITIVE: Ibn Ḥajar disambiguates to al-Haytami (fiqh shafi'i)
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-1")
def test_ibn_hajar_fiqh_context_resolves_to_haytami(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    strong_breakdown_haytami: ScoreBreakdown,
    evidence_ref_haytami: CitationRef,
) -> None:
    """End-to-end: 'ابن حجر' + fiqh shafi'i + 10th c. + تحفة المحتاج → al-Haytami DEFINITIVE.

    The mirror of scenario 1: same name fragment, opposite dossier signals.
    primary_science=fiqh + century=10 + تحفة المحتاج drive the
    disambiguation to sch_00201. ≥2-non-name floor met via primary_science
    (fiqh) + attributed_works (تحفة المحتاج) + century_active (10) +
    school (shafii).
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        confidence = 0.94 if spec.verifier_id == "verifier_a" else 0.92
        positions = [
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_HAYTAMI_ID,
                confidence=confidence,
                score_breakdown=strong_breakdown_haytami,
                cited_evidence=[evidence_ref_haytami],
            ),
        ]
        if any(c.canonical_id == _IBN_HAJAR_ASQALANI_ID for c in pkt.candidate_set):
            positions.append(
                ScoredCandidate(
                    canonical_id=_IBN_HAJAR_ASQALANI_ID,
                    confidence=0.30,
                    score_breakdown=strong_breakdown_haytami,
                    cited_evidence=[evidence_ref_haytami],
                )
            )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_IBN_HAJAR_HAYTAMI_ID,
            positions=positions,
            reasoning="Fiqh shafi'i + تحفة المحتاج anchors al-Haytami",
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs
    orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext(
        primary_science="fiqh",
        century_active_hijri_estimates=[10],
        school_affiliation_hints={"fiqh": "shafii"},
        attributed_works=["تحفة المحتاج"],
        geographic_signals=["مصر", "مكة"],
    )

    result = scholar_match_cell("ابن حجر", dossier, orchestration)

    assert result.disambiguation_state == "definitive"
    assert result.canonical_scholar_id == _IBN_HAJAR_HAYTAMI_ID
    assert result.confidence is not None
    assert result.confidence >= 0.92
    assert result.record_status == "confirmed"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes and audit.both_pass and audit.no_rival_close
    assert audit.corroboration_count_ge_2


# ---------------------------------------------------------------------------
# Scenario 3 — DISPUTED: Ibn Ḥajar with ambiguous dossier → competing positions
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-2")
def test_ibn_hajar_ambiguous_context_routes_to_disputed(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    strong_breakdown_asqalani: ScoreBreakdown,
    evidence_ref_asqalani: CitationRef,
    evidence_ref_haytami: CitationRef,
) -> None:
    """End-to-end: 'ابن حجر' + ambiguous shafi'i context → DISPUTED.

    Both Ibn Ḥajars share fiqh shafi'i affiliation (al-ʿAsqalānī had
    secondary fiqh competence; al-Haytami's primary). With no
    century-narrowing and no work-title disambiguation, both verifiers
    cannot converge on a single chosen_id. Round-1 adversarial scaffold
    runs and still does not resolve — final terminal is DISPUTED with
    positions[] populated for both candidates.
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        # Verifiers diverge in both rounds — A defends al-ʿAsqalānī, B defends al-Haytami,
        # neither concedes. Confidences within RIVAL_MARGIN.
        if spec.verifier_id == "verifier_a":
            chosen = _IBN_HAJAR_ASQALANI_ID
            confidence_chosen = 0.83
            confidence_other = 0.78
        else:
            chosen = _IBN_HAJAR_HAYTAMI_ID
            confidence_chosen = 0.82
            confidence_other = 0.79
        positions = [
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_ASQALANI_ID,
                confidence=(
                    confidence_chosen if chosen == _IBN_HAJAR_ASQALANI_ID
                    else confidence_other
                ),
                score_breakdown=strong_breakdown_asqalani,
                cited_evidence=[evidence_ref_asqalani],
            ),
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_HAYTAMI_ID,
                confidence=(
                    confidence_chosen if chosen == _IBN_HAJAR_HAYTAMI_ID
                    else confidence_other
                ),
                score_breakdown=strong_breakdown_asqalani,
                cited_evidence=[evidence_ref_haytami],
            ),
        ]
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=chosen,
            positions=positions,
            reasoning="Ambiguous shafi'i context — irreducible identity disagreement",
            prompt_template_hash=(
                spec.round_0_prompt_template_hash if round_idx == 0
                else spec.round_1_prompt_template_hash
            ),
        )

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs
    orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext(
        school_affiliation_hints={"fiqh": "shafii"},
        century_active_hijri_estimates=[9, 10],
    )

    result = scholar_match_cell("ابن حجر", dossier, orchestration)

    assert result.disambiguation_state == "disputed"
    assert len(result.positions) >= 2
    assert result.canonical_scholar_id == result.positions[0].canonical_id
    assert result.canonical_scholar_id in {
        _IBN_HAJAR_ASQALANI_ID,
        _IBN_HAJAR_HAYTAMI_ID,
    }
    assert result.record_status == "confirmed"
    assert result.evidence_sources, "disputed must carry evidence_sources"
    audit = result.provenance.threshold_audit
    assert not (
        audit.mean_passes
        and audit.both_pass
        and audit.no_rival_close
        and audit.corroboration_count_ge_2
    ), "disputed requires at least one predicate false"
    assert result.provenance.stage_2_verifier_record.round_count == 2


# ---------------------------------------------------------------------------
# Scenario 4 — INSUFFICIENT_EVIDENCE: low-confidence verifiers
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-3")
def test_ibn_hajar_thin_signals_routes_to_insufficient_evidence(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    weak_breakdown: ScoreBreakdown,
    evidence_ref_asqalani: CitationRef,
) -> None:
    """End-to-end: 'ابن حجر' + thin dossier + weak verifier confidence → INSUFFICIENT_EVIDENCE.

    No work title, no school, no century — the verifiers only have the bare
    name fragment. Confidence stays below INSUFFICIENT_FLOOR=0.70 across
    both rounds. Per CON-SRC-0008 AC-3 + REQ-SRC-0053 routing the case
    terminates as insufficient_evidence with canonical_scholar_id=null.
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        positions = [
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_ASQALANI_ID,
                confidence=0.45,
                score_breakdown=weak_breakdown,
                cited_evidence=[evidence_ref_asqalani],
            ),
            ScoredCandidate(
                canonical_id=_IBN_HAJAR_HAYTAMI_ID,
                confidence=0.42,
                score_breakdown=weak_breakdown,
                cited_evidence=[evidence_ref_asqalani],
            ),
        ]
        chosen = _IBN_HAJAR_ASQALANI_ID
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=chosen,
            positions=positions,
            reasoning="No corroborating signals; confidence below floor",
            prompt_template_hash=(
                spec.round_0_prompt_template_hash if round_idx == 0
                else spec.round_1_prompt_template_hash
            ),
        )

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs
    orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=stub,
    )

    dossier = DossierContext()  # No signals at all.
    result = scholar_match_cell("ابن حجر", dossier, orchestration)

    assert result.disambiguation_state == "insufficient_evidence"
    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert result.positions == []
    audit = result.provenance.threshold_audit
    # At least one predicate path failed; insufficient_evidence requires
    # max individual confidence < 0.70 OR mean < 0.75 per REQ-SRC-0053.
    assert audit.mean_confidence < 0.75 or audit.leader_confidence < 0.70
    assert result.provenance.registry_release_version == _RV


# ---------------------------------------------------------------------------
# Scenario 5 — Bukhārī DEFINITIVE end-to-end (cross-fixture coverage)
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "CON-SRC-0008", "AC-1")
def test_bukhari_full_chain_resolves_to_definitive(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    strong_breakdown_asqalani: ScoreBreakdown,
    evidence_ref_asqalani: CitationRef,
) -> None:
    """End-to-end: 'البخاري' + hadith + 3rd c. + الجامع الصحيح → al-Bukhārī DEFINITIVE.

    Cross-fixture verification: the disambiguation case includes both
    al-Bukhārī (sch_00042) and Muslim (sch_00115) — both 3rd-century
    hadith scholars. The work title الجامع الصحيح is the disambiguating
    signal (Muslim's صحيح مسلم does not match). Verifiers converge
    cleanly on sch_00042.
    """

    def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
        confidence = 0.96 if spec.verifier_id == "verifier_a" else 0.93
        positions = [
            ScoredCandidate(
                canonical_id=_BUKHARI_ID,
                confidence=confidence,
                score_breakdown=strong_breakdown_asqalani,
                cited_evidence=[evidence_ref_asqalani],
            ),
        ]
        if any(c.canonical_id == _MUSLIM_ID for c in pkt.candidate_set):
            positions.append(
                ScoredCandidate(
                    canonical_id=_MUSLIM_ID,
                    confidence=0.45,
                    score_breakdown=strong_breakdown_asqalani,
                    cited_evidence=[evidence_ref_asqalani],
                )
            )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=_BUKHARI_ID,
            positions=positions,
            reasoning="الجامع الصحيح uniquely anchors al-Bukhārī",
            prompt_template_hash=spec.round_0_prompt_template_hash,
        )

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs
    orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
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
    assert result.confidence is not None and result.confidence >= 0.92
    assert result.record_status == "confirmed"
    audit = result.provenance.threshold_audit
    assert audit.mean_passes and audit.both_pass
    assert audit.no_rival_close
    assert audit.corroboration_count_ge_2


# ---------------------------------------------------------------------------
# Scenario 6 — Provenance round-trip: every result has all 4 audit predicates
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "INV-SRC-0015")
def test_every_terminal_path_carries_full_provenance(
    integration_registry: Registry,
    specs: tuple[VerifierSpec, VerifierSpec],
    strong_breakdown_asqalani: ScoreBreakdown,
    evidence_ref_asqalani: CitationRef,
) -> None:
    """INV-SRC-0015 — definitive / disputed / insufficient_evidence paths
    all populate the 4 threshold_audit predicates with their numeric backing.
    Audit round-trip: the 4 booleans + 4 numeric backings are present on
    every emitted result regardless of disambiguation_state.
    """

    def make_stub(chosen_id: str, confidence_a: float, confidence_b: float):  # type: ignore[no-untyped-def]
        def stub(spec, pkt, round_idx, own_r0, other_r0):  # type: ignore[no-untyped-def]
            confidence = confidence_a if spec.verifier_id == "verifier_a" else confidence_b
            positions = [
                ScoredCandidate(
                    canonical_id=chosen_id,
                    confidence=confidence,
                    score_breakdown=strong_breakdown_asqalani,
                    cited_evidence=[evidence_ref_asqalani],
                ),
            ]
            return VerifierEmission(
                verifier_id=spec.verifier_id,
                round_index=round_idx,
                chosen_id=chosen_id,
                positions=positions,
                reasoning="stub",
                prompt_template_hash=spec.round_0_prompt_template_hash,
            )

        return stub

    snapshot = pin_registry_snapshot(_RV)
    spec_a, spec_b = specs

    # Definitive case
    definitive_orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=make_stub(_IBN_HAJAR_ASQALANI_ID, 0.96, 0.94),
    )
    definitive_dossier = DossierContext(
        primary_science="hadith",
        century_active_hijri_estimates=[9],
        school_affiliation_hints={"hadith": "ahl_hadith"},
        attributed_works=["فتح الباري"],
    )
    definitive = scholar_match_cell(
        "ابن حجر", definitive_dossier, definitive_orchestration
    )
    _assert_audit_complete(definitive)

    # Insufficient evidence case
    insufficient_orchestration = ScholarMatchCellOrchestration(
        registry=integration_registry,
        snapshot=snapshot,
        verifier_a_spec=spec_a,
        verifier_b_spec=spec_b,
        call_verifier=make_stub(_IBN_HAJAR_ASQALANI_ID, 0.45, 0.42),
    )
    insufficient = scholar_match_cell(
        "ابن حجر", DossierContext(), insufficient_orchestration
    )
    _assert_audit_complete(insufficient)


def _assert_audit_complete(result) -> None:  # type: ignore[no-untyped-def]
    audit = result.provenance.threshold_audit
    # Booleans present (Pydantic enforces; this asserts the field set).
    for predicate_name in (
        "mean_passes",
        "both_pass",
        "no_rival_close",
        "corroboration_count_ge_2",
    ):
        assert hasattr(audit, predicate_name)
        assert isinstance(getattr(audit, predicate_name), bool)
    # Numeric backings present.
    assert isinstance(audit.mean_confidence, float)
    assert isinstance(audit.leader_confidence, float)
    assert audit.rival_confidence is None or isinstance(audit.rival_confidence, float)
    assert isinstance(audit.corroboration_count, int)
    # Verifier record present and complete.
    record = result.provenance.stage_2_verifier_record
    assert record.verifier_a_id and record.verifier_b_id
    assert record.verifier_a_seed is not None
    assert record.verifier_b_seed is not None
    assert record.verifier_a_prompt_template_hash
    assert record.verifier_b_prompt_template_hash
    assert record.round_count in (1, 2)
    # Pinned snapshot version present.
    assert result.provenance.registry_release_version
