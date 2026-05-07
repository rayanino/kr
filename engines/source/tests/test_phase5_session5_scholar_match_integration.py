"""Phase 5 Session 5 — brownfield integration tests for scholar_match_cell wiring.

Exercises ``run_metadata_deliberation`` with the scholar_match orchestration
attached, validating each terminal disambiguation state through the
end-to-end pipeline:

  - DEFINITIVE: AuthorOutputPosition.canonical_id is bound to the
    matched scholar's canonical_id (al-Bukhārī fixture).
  - DISPUTED: HumanGateCheckpoint(AUTHOR_DISAMBIGUATION) is emitted +
    AuthorOutput.disambiguation_pending=True (Ibn Ḥajar pair).
  - INSUFFICIENT_EVIDENCE / new identity: ProvisionalScholarRegistration
    is emitted (REQ-SRC-0043 amendment).
  - INSUFFICIENT_EVIDENCE / hold: ScholarMatchHold is emitted
    (INV-SRC-0017 explicit-replay).

Plus regression coverage: legacy path with orchestration=None preserves
existing behavior (positions keep canonical_id=None).

Per ``.claude/rules/testing.md`` — real Arabic fixtures only; deterministic
stub VerifierCallable (no real LLM calls).
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal, Optional

import pytest

from engines.source.contracts import (
    AuthorityLevel,
    AuthorOutputPosition,
    Genre,
    HumanGateTrigger,
    MetadataDeliberationInput,
    ScholarAuthorityRecord,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TrustTier,
)
from engines.source.src.pipeline import SourcePipeline
from engines.source.src.scholar_match_integration import (
    build_orchestration_for_pipeline,
)
from engines.source.tests.conftest import FIXTURES_ROOT
from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    DossierContext,
    ScholarEvidencePacket,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
)
from shared.scholar_authority.src.scholar_match_cell import (
    ScholarMatchCellOrchestration,
)
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import VerifierCallable, VerifierSpec


# ---------------------------------------------------------------------------
# Test registry — 4 real Arabic scholars covering the four terminal states
# ---------------------------------------------------------------------------


_TEST_RELEASE_VERSION: str = "v_session5_test_2026_05_05"


def _bukhari_record() -> ScholarAuthorityRecord:
    """Imam al-Bukhārī — primary hadith, 3rd century."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00042",
        canonical_name_ar="محمد بن إسماعيل البخاري",
        display_name="الإمام البخاري",
        full_name_lineage="محمد بن إسماعيل بن إبراهيم البخاري",
        known_as=["البخاري", "الإمام البخاري", "صاحب الصحيح"],
        kunya="أبو عبد الله",
        nisba=["البخاري", "الجعفي"],
        birth_date_hijri=194,
        birth_date_ce=None,
        death_date_hijri=256,
        death_date_ce=None,
        era_century_hijri=3,
        geographic_origin="بخارى",
        geographic_active=["بخارى", "نيسابور"],
        school_affiliations={"hadith": "shafii"},
        teachers=[],
        students=[],
        known_works=["الجامع الصحيح", "التاريخ الكبير"],
        primary_science="hadith",
        scholarly_standing="إمام أهل الحديث",
        last_updated="2026-05-05T00:00:00Z",
        record_completeness=0.0,
        data_provenance_score=0.0,
    )


def _ibn_hajar_asqalani() -> ScholarAuthorityRecord:
    """Ibn Ḥajar al-ʿAsqalānī — 9th-century hadith scholar (al-Asqalānī)."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00200",
        canonical_name_ar="أحمد بن علي بن حجر العسقلاني",
        display_name="الحافظ ابن حجر العسقلاني",
        full_name_lineage="أحمد بن علي بن محمد بن حجر العسقلاني",
        known_as=["ابن حجر", "الحافظ ابن حجر", "ابن حجر العسقلاني"],
        kunya="أبو الفضل",
        nisba=["العسقلاني", "الكناني"],
        birth_date_hijri=773,
        birth_date_ce=None,
        death_date_hijri=852,
        death_date_ce=None,
        era_century_hijri=9,
        geographic_origin="عسقلان",
        geographic_active=["القاهرة"],
        school_affiliations={"hadith": "shafii", "fiqh": "shafii"},
        teachers=[],
        students=[],
        known_works=["فتح الباري", "تهذيب التهذيب", "الإصابة"],
        primary_science="hadith",
        scholarly_standing="حافظ العصر",
        last_updated="2026-05-05T00:00:00Z",
        record_completeness=0.0,
        data_provenance_score=0.0,
    )


def _ibn_hajar_haytami() -> ScholarAuthorityRecord:
    """Ibn Ḥajar al-Haytamī — 10th-century Shafi'i jurist (al-Haytamī)."""
    return ScholarAuthorityRecord(
        canonical_id="sch_00201",
        canonical_name_ar="أحمد بن محمد بن حجر الهيتمي",
        display_name="ابن حجر الهيتمي",
        full_name_lineage="أحمد بن محمد بن علي بن حجر الهيتمي",
        known_as=["ابن حجر", "ابن حجر الهيتمي", "الهيتمي"],
        kunya="أبو العباس",
        nisba=["الهيتمي", "السعدي"],
        birth_date_hijri=909,
        birth_date_ce=None,
        death_date_hijri=974,
        death_date_ce=None,
        era_century_hijri=10,
        geographic_origin="محلة أبي الهيتم",
        geographic_active=["مكة"],
        school_affiliations={"fiqh": "shafii"},
        teachers=[],
        students=[],
        known_works=["تحفة المحتاج", "الفتاوى الكبرى الفقهية", "الزواجر"],
        primary_science="fiqh",
        scholarly_standing="فقيه شافعي",
        last_updated="2026-05-05T00:00:00Z",
        record_completeness=0.0,
        data_provenance_score=0.0,
    )


def _build_test_registry() -> Registry:
    return Registry(
        release_version=_TEST_RELEASE_VERSION,
        scholars=[
            _bukhari_record(),
            _ibn_hajar_asqalani(),
            _ibn_hajar_haytami(),
        ],
    )


# ---------------------------------------------------------------------------
# Deterministic stub VerifierCallable (signal-alignment scoring)
# ---------------------------------------------------------------------------


_STUB_BREAKDOWN = ScoreBreakdown(
    name_match=0.5,
    death_date_proximity=0.0,
    school_affiliation_overlap=0.0,
    work_title_match=0.0,
    teacher_student_network_match=0.0,
    geographic_origin_match=0.0,
    century_active_match=0.0,
    primary_science_match=0.0,
    secondary_sciences_overlap=0.0,
)
_STUB_EVIDENCE = CitationRef(
    source_book_id="bk_session5_stub",
    evidence_type="title_page",
    raw_evidence="session 5 integration stub evidence",
)


def _alignment_count(record: ScholarAuthorityRecord, dossier: DossierContext) -> tuple[int, int]:
    """Count aligned non-name attribute classes (mirrors INV-SRC-0013 6-class set)."""
    aligned = 0
    evaluated = 0
    if dossier.primary_science is not None and record.primary_science is not None:
        evaluated += 1
        if record.primary_science == dossier.primary_science:
            aligned += 1
    if dossier.century_active_hijri_estimates and record.era_century_hijri is not None:
        evaluated += 1
        if record.era_century_hijri in dossier.century_active_hijri_estimates:
            aligned += 1
    if dossier.school_affiliation_hints:
        evaluated += 1
        for science, hint in dossier.school_affiliation_hints.items():
            if hint is not None and record.school_affiliations.get(science) == hint:
                aligned += 1
                break
    if dossier.attributed_works:
        evaluated += 1
        record_works = set(record.known_works)
        if any(work in record_works for work in dossier.attributed_works):
            aligned += 1
    if dossier.geographic_signals and (
        record.geographic_origin is not None or record.geographic_active
    ):
        evaluated += 1
        record_geo: set[str] = set(record.geographic_active)
        if record.geographic_origin is not None:
            record_geo.add(record.geographic_origin)
        if any(sig in record_geo for sig in dossier.geographic_signals):
            aligned += 1
    return aligned, evaluated


def _make_alignment_stub(registry: Registry):
    """VerifierCallable that scores by attribute alignment.

    confidence = 0.40 + (aligned/evaluated) * 0.55
    Empty dossier (evaluated=0) → 0.40 baseline (below 0.70 floor).
    """

    def stub(
        spec: VerifierSpec,
        packet: ScholarEvidencePacket,
        round_idx: Literal[0, 1],
        own_round_0: Optional[VerifierEmission],
        other_round_0: Optional[VerifierEmission],
    ) -> VerifierEmission:
        dossier = packet.dossier_context
        scored: list[tuple[float, ScoredCandidate]] = []
        for candidate in packet.candidate_set:
            record = registry.lookup_by_canonical_id(candidate.canonical_id)
            if record is None:
                continue
            aligned, evaluated = _alignment_count(record, dossier)
            conf = 0.40 + (aligned / evaluated) * 0.55 if evaluated else 0.40
            scored.append(
                (
                    conf,
                    ScoredCandidate(
                        canonical_id=candidate.canonical_id,
                        confidence=conf,
                        score_breakdown=_STUB_BREAKDOWN,
                        cited_evidence=[_STUB_EVIDENCE],
                    ),
                )
            )
        if not scored:
            raise RuntimeError(
                "stub invoked with empty candidate_set — Stage-1 should "
                "have returned empty narrowing terminal first"
            )
        scored.sort(key=lambda pair: (-pair[0], pair[1].canonical_id))
        chosen = scored[0][1]
        positions = [sc for _, sc in scored]
        prompt_hash = (
            spec.round_0_prompt_template_hash
            if round_idx == 0
            else spec.round_1_prompt_template_hash
        )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=chosen.canonical_id,
            positions=positions,
            reasoning="session 5 stub: alignment scoring",
            prompt_template_hash=prompt_hash,
        )

    return stub


_VERIFIER_A = VerifierSpec(
    verifier_id="session5_test_verifier_a",
    model_id="openrouter/anthropic/claude-opus-4.6",
    seed=20260505,
    round_0_prompt_template_hash="r0_a_session5_test",
    round_1_prompt_template_hash="r1_a_session5_test",
)
_VERIFIER_B = VerifierSpec(
    verifier_id="session5_test_verifier_b",
    model_id="openrouter/cohere/command-a",
    seed=20260506,
    round_0_prompt_template_hash="r0_b_session5_test",
    round_1_prompt_template_hash="r1_b_session5_test",
)


@pytest.fixture
def test_orchestration() -> ScholarMatchCellOrchestration:
    registry = _build_test_registry()
    stub = _make_alignment_stub(registry)
    return build_orchestration_for_pipeline(
        registry=registry,
        verifier_a_spec=_VERIFIER_A,
        verifier_b_spec=_VERIFIER_B,
        call_verifier=stub,
    )


# ---------------------------------------------------------------------------
# Session 7 — DISPUTED-path stub variant (equal-score forced disputed)
# ---------------------------------------------------------------------------


def _make_equal_score_stub(
    target_ids: tuple[str, str], confidence: float = 0.95
) -> VerifierCallable:
    """VerifierCallable that scores the two ``target_ids`` IDENTICALLY.

    Forces REQ-SRC-0053 condition (e) — convergent identity but
    no_rival_close=False — by stamping the same confidence on both
    designated candidates regardless of the dossier alignment count.
    Both verifiers (A and B) using this stub produce IDENTICAL output,
    converging on ``min(target_ids)`` after canonical_id-sort tiebreak.

    Other candidates that may have been produced by Stage-1 narrowing
    (e.g., the al-Bukhārī record co-narrowed by a fragment that also
    overlaps his known_as set) are deliberately NOT scored, so they
    cannot become the leader or rival in Stage-2.

    The 9-feature score_breakdown is set to all-``confidence`` so that
    HumanGateCheckpoint.alternatives surfaces non-zero per-feature
    breakdown values to the owner — a more truthful test fixture than
    the alignment-stub's mostly-zero breakdown.
    """
    scored_breakdown = ScoreBreakdown(
        name_match=confidence,
        death_date_proximity=confidence,
        school_affiliation_overlap=confidence,
        work_title_match=confidence,
        teacher_student_network_match=confidence,
        geographic_origin_match=confidence,
        century_active_match=confidence,
        primary_science_match=confidence,
        secondary_sciences_overlap=confidence,
    )
    cited_evidence = [
        CitationRef(
            source_book_id="bk_session7_disputed_stub",
            evidence_type="title_page",
            raw_evidence="session 7 disputed stub evidence",
        )
    ]

    def stub(
        spec: VerifierSpec,
        packet: ScholarEvidencePacket,
        round_idx: Literal[0, 1],
        own_round_0: Optional[VerifierEmission],
        other_round_0: Optional[VerifierEmission],
    ) -> VerifierEmission:
        scored: list[ScoredCandidate] = []
        for candidate in packet.candidate_set:
            if candidate.canonical_id in target_ids:
                scored.append(
                    ScoredCandidate(
                        canonical_id=candidate.canonical_id,
                        confidence=confidence,
                        score_breakdown=scored_breakdown,
                        cited_evidence=list(cited_evidence),
                    )
                )
        if len(scored) < 2:
            raise RuntimeError(
                f"_make_equal_score_stub requires Stage-1 to produce at least "
                f"2 candidates from target_ids={target_ids!r}; "
                f"got candidate_set canonical_ids="
                f"{[c.canonical_id for c in packet.candidate_set]!r}"
            )
        scored.sort(key=lambda sc: sc.canonical_id)
        chosen = scored[0]
        prompt_hash = (
            spec.round_0_prompt_template_hash
            if round_idx == 0
            else spec.round_1_prompt_template_hash
        )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=chosen.canonical_id,
            positions=scored,
            reasoning="session 7 stub: equal-score forced disputed",
            prompt_template_hash=prompt_hash,
        )

    return stub


@pytest.fixture
def disputed_orchestration() -> ScholarMatchCellOrchestration:
    """Orchestration with the equal-score stub forcing DISPUTED on the
    Ibn Ḥajar trap pair (sch_00200 al-ʿAsqalānī vs sch_00201 al-Haytamī).

    Used by the Phase 5 Session 7 DISPUTED-path integration tests.
    """
    registry = _build_test_registry()
    stub = _make_equal_score_stub(target_ids=("sch_00200", "sch_00201"))
    return build_orchestration_for_pipeline(
        registry=registry,
        verifier_a_spec=_VERIFIER_A,
        verifier_b_spec=_VERIFIER_B,
        call_verifier=stub,
    )


@pytest.fixture
def disputed_session5_pipeline(
    tmp_path: Path, disputed_orchestration: ScholarMatchCellOrchestration
) -> SourcePipeline:
    return SourcePipeline(
        workspace_root=tmp_path / "source_workspace_session7_disputed",
        scholar_match_orchestration=disputed_orchestration,
    )


# ---------------------------------------------------------------------------
# Test pipeline factory
# ---------------------------------------------------------------------------


@pytest.fixture
def session5_pipeline(
    tmp_path: Path, test_orchestration: ScholarMatchCellOrchestration
) -> SourcePipeline:
    return SourcePipeline(
        workspace_root=tmp_path / "source_workspace_session5",
        scholar_match_orchestration=test_orchestration,
    )


def _ingest_fixture(pipeline: SourcePipeline, fixture_subpath: str) -> str:
    """Ingest a fixture through steps 10-40, returning its source_id."""
    receipt = pipeline.upload_receipt(FIXTURES_ROOT / fixture_subpath)
    frozen = pipeline.freeze_and_manifest(receipt.submission_id)
    pipeline.classify_container(frozen.source_id)
    pipeline.intake_analysis(frozen.source_id)
    return frozen.source_id


def _make_deliberation_input(
    *,
    source_id: str,
    title_arabic: str,
    science_scope: list[str],
    genre: Genre,
    author_death_hijri: Optional[int],
    author_positions: list[AuthorOutputPosition],
    authority_level: AuthorityLevel = AuthorityLevel.REFERENCE,
) -> MetadataDeliberationInput:
    return MetadataDeliberationInput(
        source_id=source_id,
        title_arabic=title_arabic,
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path=f"library/sources/{source_id}/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="source_engine_accepted",
        science_scope=science_scope,
        genre=genre,
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        authority_level=authority_level,
        author_death_hijri=author_death_hijri,
        author_positions=author_positions,
        owner_hint_payload={},
        verification_agents=["agent_a", "agent_b"],
        research_source_types=["metadata_card", "title_page"],
    )


# ---------------------------------------------------------------------------
# Tests — terminal routing
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0008", "CON-SRC-0008", "AC-1")
def test_definitive_match_binds_canonical_id(session5_pipeline: SourcePipeline) -> None:
    """al-Bukhārī fixture: full dossier alignment → DEFINITIVE → canonical_id bound."""
    source_id = _ingest_fixture(session5_pipeline, "shamela_real/05_tafsir/book.htm")
    positions = [
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["title_page: الجامع الصحيح للإمام البخاري"],
            confidence=0.95,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["metadata_card: البخاري"],
            confidence=0.90,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="الجامع الصحيح",
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        author_death_hijri=256,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = session5_pipeline.metadata_deliberation(source_id, deliberation_input)

    assert len(result.scholar_match_results) >= 1
    author_output = result.source_metadata.author_output
    assert author_output is not None
    matched = author_output.positions[0]
    assert matched.canonical_id == "sch_00042"
    assert author_output.disambiguation_pending is False
    assert not result.human_gate_checkpoints
    assert not result.provisional_scholar_registrations
    assert not result.scholar_match_holds


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0043", "AC-1")
def test_insufficient_empty_candidates_emits_provisional_registration(
    session5_pipeline: SourcePipeline,
) -> None:
    """Author not in registry → Stage-1 empty narrowing → REQ-SRC-0043 provisional path."""
    source_id = _ingest_fixture(session5_pipeline, "shamela_real/05_tafsir/book.htm")
    positions = [
        AuthorOutputPosition(
            position="عبد الواحد بن سعيد المراكشي",
            display_name="عبد الواحد المراكشي",
            evidence=["title_page: تأليف عبد الواحد المراكشي"],
            confidence=0.85,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="عبد الواحد بن سعيد المراكشي",
            display_name="عبد الواحد المراكشي",
            evidence=["metadata_card"],
            confidence=0.80,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="المعجب في تلخيص أخبار المغرب",
        science_scope=["history"],
        genre=Genre.RISALAH,
        author_death_hijri=647,
        author_positions=positions,
    )
    result = session5_pipeline.metadata_deliberation(source_id, deliberation_input)

    # Stage-1 narrowing returns empty (no candidate matches the fragment) →
    # insufficient_evidence with empty stage_1_score_breakdown → REQ-SRC-0043.
    assert len(result.scholar_match_results) >= 1
    sm = result.scholar_match_results[0]
    assert sm.disambiguation_state == "insufficient_evidence"
    assert sm.canonical_scholar_id is None
    assert result.provisional_scholar_registrations, (
        "expected REQ-SRC-0043 provisional registration for empty-narrowing case"
    )
    reg = result.provisional_scholar_registrations[0]
    assert reg.display_name == "عبد الواحد المراكشي"
    assert reg.death_hijri is None  # position carries no death_hijri
    assert reg.primary_science == "history"
    assert not result.scholar_match_holds


@pytest.mark.spec("REQ-SRC-0028", "AC-1")
def test_legacy_no_orchestration_preserves_canonical_id_none(
    source_pipeline: SourcePipeline,
) -> None:
    """Backward-compat: orchestration=None means canonical_id stays None."""
    source_id = _ingest_fixture(source_pipeline, "shamela_real/05_tafsir/book.htm")
    positions = [
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["title_page: البخاري"],
            confidence=0.95,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["metadata_card: البخاري"],
            confidence=0.90,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="الجامع الصحيح",
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        author_death_hijri=256,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = source_pipeline.metadata_deliberation(source_id, deliberation_input)

    assert result.source_metadata.author_output is not None
    assert result.source_metadata.author_output.positions[0].canonical_id is None
    assert result.scholar_match_results == []
    assert result.human_gate_checkpoints == []
    assert result.provisional_scholar_registrations == []
    assert result.scholar_match_holds == []


@pytest.mark.spec("REQ-SRC-0028", "DEC-SRC-0013")
def test_resolve_scholar_identities_early_returns_on_agent_no_evidence(
    test_orchestration: ScholarMatchCellOrchestration,
) -> None:
    """``resolve_scholar_identities`` short-circuits on agent_no_evidence.

    Direct unit test of the integration adapter — the upstream pipeline
    cannot reach ``agent_no_evidence`` with verification_agents non-empty
    (it raises AUTHOR_AGENT_COUNT first), but the adapter's early-return
    is the contract that makes the wiring safe regardless of how the
    AuthorOutput was produced.
    """
    from engines.source.contracts import AuthorOutput
    from engines.source.src.scholar_match_integration import (
        resolve_scholar_identities,
    )
    from engines.source.contracts import IntakeDossier as _Dossier

    empty_output = AuthorOutput(status="agent_no_evidence", positions=[])
    dossier = _Dossier(dossier_id="dosr_test_session5")
    deliberation_input = MetadataDeliberationInput(
        source_id="src_unit",
        title_arabic="تجريبي",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path="library/sources/src_unit/frozen",
        frozen_hash="b" * 64,
        frozen_file_hashes={"book.htm": "b" * 64},
        status="source_engine_accepted",
        science_scope=["fiqh"],
        genre=Genre.RISALAH,
        author_positions=[],
        verification_agents=["agent_a", "agent_b"],
    )
    updated, results, checkpoints, registrations, holds = resolve_scholar_identities(
        source_id="src_unit",
        case_id="case_unit",
        author_output=empty_output,
        intake_dossier=dossier,
        deliberation_input=deliberation_input,
        orchestration=test_orchestration,
    )
    assert updated is empty_output
    assert results == []
    assert checkpoints == []
    assert registrations == []
    assert holds == []


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0008")
def test_variant_name_consensus_collapse_to_consensus(
    session5_pipeline: SourcePipeline,
) -> None:
    """Two variant-name positions resolving to same canonical_id collapse to agent_consensus.

    Adjacent-scope fix per system overrides: variant-name disagreement (e.g.,
    ``البخاري`` vs ``الإمام البخاري`` for the same scholar) is not a genuine
    scholarly dispute — both should resolve DEFINITIVELY to sch_00042.
    """
    source_id = _ingest_fixture(session5_pipeline, "shamela_real/05_tafsir/book.htm")
    positions = [
        AuthorOutputPosition(
            position="البخاري",
            display_name="البخاري",
            evidence=["agent_a evidence"],
            confidence=0.85,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="الإمام البخاري",
            display_name="الإمام البخاري",
            evidence=["agent_b evidence"],
            confidence=0.90,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="الجامع الصحيح",
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        author_death_hijri=256,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = session5_pipeline.metadata_deliberation(source_id, deliberation_input)

    output = result.source_metadata.author_output
    assert output is not None
    # Both positions resolve to sch_00042 → collapse to consensus
    assert output.status == "agent_consensus"
    assert len(output.positions) == 1
    assert output.positions[0].canonical_id == "sch_00042"
    assert output.disambiguation_pending is False
    # Both evidence strings preserved in the merged position
    assert "agent_a evidence" in output.positions[0].evidence
    assert "agent_b evidence" in output.positions[0].evidence
    # Both source_agents preserved
    assert "agent_a" in output.positions[0].source_agents
    assert "agent_b" in output.positions[0].source_agents


@pytest.mark.spec("DEC-SRC-0013")
def test_metadata_deliberation_result_carries_audit_trail(
    session5_pipeline: SourcePipeline,
) -> None:
    """MetadataDeliberationResult exposes the full Phase 5 audit trail."""
    source_id = _ingest_fixture(session5_pipeline, "shamela_real/05_tafsir/book.htm")
    positions = [
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["title_page"],
            confidence=0.95,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="محمد بن إسماعيل البخاري",
            display_name="الإمام البخاري",
            evidence=["metadata_card"],
            confidence=0.90,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="الجامع الصحيح",
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        author_death_hijri=256,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = session5_pipeline.metadata_deliberation(source_id, deliberation_input)

    assert hasattr(result, "scholar_match_results")
    assert hasattr(result, "human_gate_checkpoints")
    assert hasattr(result, "provisional_scholar_registrations")
    assert hasattr(result, "scholar_match_holds")
    # And per-result, the registry_release_version is preserved on the audit
    sm = result.scholar_match_results[0]
    assert sm.provenance.registry_release_version == _TEST_RELEASE_VERSION


# ---------------------------------------------------------------------------
# Phase 5 Session 7 — DISPUTED-path end-to-end coverage
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0008", "CON-SRC-0008", "AC-2", "REQ-SRC-0053")
def test_disputed_match_emits_author_disambiguation_checkpoint(
    disputed_session5_pipeline: SourcePipeline,
) -> None:
    """End-to-end DISPUTED via REQ-SRC-0053 condition (e) — convergent identity
    but no_rival_close=False — using the equal-score stub on the Ibn Ḥajar
    trap pair (sch_00200 al-ʿAsqalānī vs sch_00201 al-Haytamī).

    Validates the full DISPUTED routing chain through ``run_metadata_deliberation``:

      1. ``scholar_match_cell`` produces ``disambiguation_state == "disputed"``
         with ≥2 positions (the trap pair both at confidence 0.95).
      2. ``resolve_scholar_identities`` emits a ``HumanGateCheckpoint`` with
         ``trigger == HumanGateTrigger.AUTHOR_DISAMBIGUATION``.
      3. The checkpoint's ``alternatives`` surface BOTH disputed canonical_ids
         so the owner has the complete decision surface at gate review time.
      4. ``AuthorOutput.disambiguation_pending`` is set to True; the position's
         canonical_id stays None (DEFINITIVE binding is suppressed pending
         owner resolution).
      5. The provenance still pins ``registry_release_version`` per INV-SRC-0017.

    Real Arabic fixtures only — fragment ``ابن حجر`` with dossier signals
    aligned to al-ʿAsqalānī (primary_science=hadith, century=9, work
    ``فتح الباري``) so corroboration_count_ge_2 is True; the no_rival_close
    predicate is the SOLE failing predicate per condition (e).
    """
    source_id = _ingest_fixture(
        disputed_session5_pipeline, "shamela_real/05_tafsir/book.htm"
    )
    positions = [
        AuthorOutputPosition(
            position="ابن حجر",
            display_name="ابن حجر",
            evidence=["title_page: شرح صحيح البخاري المسمى فتح الباري لابن حجر"],
            confidence=0.95,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="ابن حجر",
            display_name="ابن حجر",
            evidence=["metadata_card: ابن حجر"],
            confidence=0.90,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="فتح الباري",
        science_scope=["hadith"],
        genre=Genre.SHARH,
        author_death_hijri=852,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = disputed_session5_pipeline.metadata_deliberation(
        source_id, deliberation_input
    )

    # variant-name collapse logic merges 2 positions w/ same display into 1
    # match call; we should see ≥1 scholar_match_result, all DISPUTED
    assert len(result.scholar_match_results) >= 1
    sm = result.scholar_match_results[0]
    assert sm.disambiguation_state == "disputed", (
        f"Expected disputed; got {sm.disambiguation_state!r}. "
        f"threshold_audit={sm.provenance.threshold_audit!r}"
    )
    # REQ-SRC-0053 condition (e): leader_confidence high, but rival within margin
    audit = sm.provenance.threshold_audit
    assert audit.mean_passes is True
    assert audit.both_pass is True
    assert audit.no_rival_close is False, (
        "Equal-score stub MUST trigger no_rival_close=False"
    )
    assert audit.corroboration_count_ge_2 is True, (
        "Dossier (primary_science=hadith, century=9, work=فتح الباري) MUST "
        "produce corroboration_count ≥ 2 against sch_00200 (al-ʿAsqalānī)"
    )
    # CON-SRC-0008 AC-2: disputed result MUST have ≥2 positions
    assert len(sm.positions) >= 2
    disputed_ids = {pos.canonical_id for pos in sm.positions}
    assert disputed_ids == {"sch_00200", "sch_00201"}, (
        f"Equal-score stub targets these two; got {disputed_ids!r}"
    )

    # AuthorOutput must carry disambiguation_pending=True; positions' canonical
    # ids stay None until owner resolution at the human gate
    author_output = result.source_metadata.author_output
    assert author_output is not None
    assert author_output.disambiguation_pending is True
    for pos in author_output.positions:
        assert pos.canonical_id is None, (
            "DISPUTED positions MUST NOT bind canonical_id pending owner resolution"
        )

    # Exactly one AUTHOR_DISAMBIGUATION checkpoint with both candidates surfaced
    auth_dis_checkpoints = [
        cp
        for cp in result.human_gate_checkpoints
        if cp.trigger == HumanGateTrigger.AUTHOR_DISAMBIGUATION
    ]
    assert len(auth_dis_checkpoints) >= 1, (
        f"Expected ≥1 AUTHOR_DISAMBIGUATION checkpoint; got "
        f"{[cp.trigger for cp in result.human_gate_checkpoints]!r}"
    )
    checkpoint = auth_dis_checkpoints[0]
    assert "author_output.canonical_id" in checkpoint.fields_to_review
    assert checkpoint.alternatives is not None
    alternative_ids = {
        alt["canonical_scholar_id"] for alt in checkpoint.alternatives
    }
    assert alternative_ids == {"sch_00200", "sch_00201"}, (
        f"Checkpoint alternatives MUST surface both disputed canonical_ids; "
        f"got {alternative_ids!r}"
    )
    # Each alternative carries cited_evidence so the owner sees provenance
    for alt in checkpoint.alternatives:
        assert isinstance(alt["cited_evidence"], list)
        assert len(alt["cited_evidence"]) >= 1

    # Provenance is fully populated even on the disputed terminal
    assert sm.provenance.registry_release_version == _TEST_RELEASE_VERSION
    # REQ-SRC-0052 round-0 convergence requires ALL 5 predicates of
    # is_definitive to pass (chosen_id agreement + 4 numerical predicates).
    # Equal-score rivals fail no_rival_close in round 0, so the protocol
    # routes to round-1 adversarial scaffold per the hybrid protocol —
    # round_count=2 is the correct audit trail (matches the prompt-template
    # hash in the verifier_record being the round-1 hash, not round-0).
    assert sm.provenance.stage_2_verifier_record.round_count == 2, (
        "Equal-score rivals trigger round-1 because no_rival_close fails "
        "round-0 convergence; final round_count=2 audits the round-1 emissions."
    )

    # No provisional registration, no hold (those are INSUFFICIENT branches)
    assert result.provisional_scholar_registrations == []
    assert result.scholar_match_holds == []


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0053")
def test_disputed_leader_is_alphabetically_first_canonical_id_with_equal_scores(
    disputed_session5_pipeline: SourcePipeline,
) -> None:
    """Asymmetric-validator-pattern lens (Sessions 1+3+4 generalized defect class):
    when two candidates score identically, leader/rival assignment MUST be
    deterministic — the alphabetically-first canonical_id becomes the leader.

    Locks in the equal-score stub's tie-break rule (canonical_id ascending)
    so that future stub refactors cannot silently flip leader/rival roles
    in DISPUTED outcomes. The leader_canonical_scholar_id surfaces in the
    checkpoint's current_values, so a flip would change what the owner
    sees as the "primary candidate" — a knowledge-integrity adjacent risk.
    """
    source_id = _ingest_fixture(
        disputed_session5_pipeline, "shamela_real/05_tafsir/book.htm"
    )
    # Both positions share the same display_name ("ابن حجر") to mirror
    # the expected behavior on a real input where two agents independently
    # propose the same fragment; AUTHOR_AGENT_COUNT requires ≥2 distinct
    # source_agents so the verification policy is satisfied.
    positions = [
        AuthorOutputPosition(
            position="ابن حجر",
            display_name="ابن حجر",
            evidence=["title_page: ابن حجر"],
            confidence=0.95,
            source_agent="agent_a",
        ),
        AuthorOutputPosition(
            position="ابن حجر",
            display_name="ابن حجر",
            evidence=["metadata_card: ابن حجر"],
            confidence=0.92,
            source_agent="agent_b",
        ),
    ]
    deliberation_input = _make_deliberation_input(
        source_id=source_id,
        title_arabic="فتح الباري",
        science_scope=["hadith"],
        genre=Genre.SHARH,
        author_death_hijri=852,
        author_positions=positions,
        authority_level=AuthorityLevel.PRIMARY,
    )
    result = disputed_session5_pipeline.metadata_deliberation(
        source_id, deliberation_input
    )

    # Every match call MUST yield the same deterministic leader
    assert all(sm.disambiguation_state == "disputed" for sm in result.scholar_match_results)
    for sm in result.scholar_match_results:
        # sch_00200 < sch_00201 lexicographically → sch_00200 is the leader
        assert sm.canonical_scholar_id == "sch_00200", (
            f"Tie-break must be canonical_id ascending; got "
            f"{sm.canonical_scholar_id!r}"
        )
        # Positions ordered by aggregated confidence desc; tie-break on canonical_id
        # The leader (positions[0]) is sch_00200; rival (positions[1]) is sch_00201
        assert sm.positions[0].canonical_id == "sch_00200"
        assert sm.positions[1].canonical_id == "sch_00201"
        # Both at the equal score (confirms the stub's invariant)
        assert sm.positions[0].confidence == sm.positions[1].confidence

    # Every AUTHOR_DISAMBIGUATION checkpoint surfaces the same deterministic
    # leader so the owner sees a stable "primary candidate" across runs.
    auth_dis_checkpoints = [
        cp
        for cp in result.human_gate_checkpoints
        if cp.trigger == HumanGateTrigger.AUTHOR_DISAMBIGUATION
    ]
    assert len(auth_dis_checkpoints) >= 1
    for checkpoint in auth_dis_checkpoints:
        assert (
            checkpoint.current_values["leader_canonical_scholar_id"]
            == "sch_00200"
        ), (
            "Determinism contract: leader_canonical_scholar_id MUST be the "
            "alphabetically-first canonical_id when verifier confidences tie. "
            "A flip would non-deterministically rotate which scholar the owner "
            "sees as the primary candidate at the human gate."
        )
