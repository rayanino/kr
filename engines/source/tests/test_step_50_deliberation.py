from __future__ import annotations

import logging
import pytest

from engines.source.contracts import (
    AuthorityLevel,
    AuthorOutputPosition,
    ErrorCode,
    Genre,
    HadithSubgenre,
    IntakeDossier,
    LevelStatus,
    MetadataDeliberationInput,
    SourceMetadata,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TrustTier,
    WorkIdentityCandidate,
    WorkIdentityProposal,
)
from engines.source.src.deliberation import (
    _fallback_work_output,
    _infer_hadith_subgenre,
    assess_case_complexity,
    compare_owner_hints,
    deliberate_author_output,
    evaluate_trust_decision,
)
from engines.source.src.errors import SourceEngineError
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


logger = logging.getLogger(__name__)


def _base_request(source_id: str = "src_test") -> MetadataDeliberationInput:
    return MetadataDeliberationInput(
        source_id=source_id,
        title_arabic="كتاب الاختبار",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path="library/sources/src_test/frozen",
        frozen_hash="a" * 64,
        frozen_file_hashes={"book.htm": "a" * 64},
        status="source_engine_accepted",
        science_scope=["fiqh"],
        genre=Genre.RISALAH,
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        author_positions=[],
        owner_hint_payload={},
        verification_agents=["agent_a", "agent_b"],
        research_source_types=["metadata_card", "title_page"],
        author_death_hijri=None,
    )


def _base_metadata() -> SourceMetadata:
    request = _base_request()
    return SourceMetadata(
        source_id=request.source_id,
        title_arabic=request.title_arabic,
        source_format=request.source_format,
        structural_format=request.structural_format,
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path=request.acquisition_path,
        frozen_path=request.frozen_path,
        frozen_hash=request.frozen_hash,
        frozen_file_hashes=request.frozen_file_hashes,
        status=request.status,
        science_scope=request.science_scope,
        genre=request.genre,
        is_multi_layer=request.is_multi_layer,
        text_fidelity=request.text_fidelity,
        trust_tier=request.trust_tier,
        trust_score=request.trust_score,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
        level_status=LevelStatus.PENDING_SYNTHESIS,
    )


@pytest.mark.spec("REQ-SRC-0028", "AC-1")
def test_case_complexity_fast_track_for_primary_tafsir(source_pipeline: SourcePipeline) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "05_tafsir" / "book.htm").submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    complexity = assess_case_complexity(
        dossier=dossier,
        genre="tafsir",
        author_death_hijri=774,
        authority_level="primary",
    )

    assert complexity.case_complexity == "fast_track"


def test_metadata_deliberation_preserves_fast_track_with_genre_enum(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "05_tafsir" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.genre = Genre.TAFSIR
    request.authority_level = AuthorityLevel.PRIMARY
    request.author_positions = [
        AuthorOutputPosition(
            position="مفسر",
            display_name="مفسر",
            evidence=["x"],
            confidence=0.8,
            source_agent="agent_a",
            death_hijri=774,
        ),
        AuthorOutputPosition(
            position="مفسر",
            display_name="مفسر",
            evidence=["y"],
            confidence=0.81,
            source_agent="agent_b",
            death_hijri=774,
        ),
    ]
    request.author_death_hijri = 774

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.trust_decision is not None
    assert result.source_metadata.trust_decision.trust_path == "fast_track"
    assert result.case_complexity_record.case_complexity == "fast_track"
    assert result.case_complexity_record.case_id
    assert result.monitor_feedback[0].trust_path == "fast_track"
    assert source_pipeline.store.get_case_complexity_record(source_id).case_id == result.case_complexity_record.case_id
    assert source_pipeline.store.get_monitor_feedback(source_id)[0].case_id == result.case_complexity_record.case_id


@pytest.mark.spec("REQ-SRC-0028", "AC-2")
def test_case_complexity_standard_for_modern_risalah(source_pipeline: SourcePipeline) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm").submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    complexity = assess_case_complexity(
        dossier=dossier,
        genre="risalah",
        author_death_hijri=None,
        authority_level="modern_compilation",
    )

    assert complexity.case_complexity == "standard"


@pytest.mark.spec("REQ-SRC-0028", "AC-3")
def test_case_complexity_degraded_for_corrupt_pdf(source_pipeline: SourcePipeline) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(FIXTURES_ROOT / "waraqat_usul" / "waraqat.pdf").submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    complexity = assess_case_complexity(
        dossier=dossier,
        genre="risalah",
        author_death_hijri=676,
        authority_level="primary",
    )

    assert complexity.case_complexity == "degraded_evidence"


@pytest.mark.spec("REQ-SRC-0002", "AC-1")
def test_hint_comparison_records_matching_author_without_mutating_metadata() -> None:
    metadata = _base_metadata()
    metadata.author_output = deliberate_author_output(
        [
            AuthorOutputPosition(
                position="عبد الله بن إبراهيم الزاحم",
                display_name="عبد الله بن إبراهيم الزاحم",
                evidence=["metadata_card"],
                confidence=0.8,
                source_agent="agent_a",
                death_hijri=None,
            ),
            AuthorOutputPosition(
                position="عبد الله بن إبراهيم الزاحم",
                display_name="عبد الله بن إبراهيم الزاحم",
                evidence=["title_page"],
                confidence=0.82,
                source_agent="agent_b",
                death_hijri=None,
            ),
        ]
    )

    updated = compare_owner_hints(metadata, {"author_name": "عبد الله بن إبراهيم الزاحم"})

    assert updated.author_output is not None
    assert updated.author_output.positions[0].position == "عبد الله بن إبراهيم الزاحم"
    assert updated.hint_comparison_results[0].match is True
    assert updated.hint_comparison_results[0].confidence_delta > 0


@pytest.mark.spec("REQ-SRC-0004", "AC-1")
def test_author_deliberation_emits_agent_consensus_when_agents_agree() -> None:
    result = deliberate_author_output(
        [
            AuthorOutputPosition(
                position="عبد الله بن إبراهيم الزاحم",
                display_name="عبد الله بن إبراهيم الزاحم",
                evidence=["metadata_card"],
                confidence=0.8,
                source_agent="agent_a",
                death_hijri=None,
            ),
            AuthorOutputPosition(
                position="عبد الله بن إبراهيم الزاحم",
                display_name="عبد الله بن إبراهيم الزاحم",
                evidence=["title_page"],
                confidence=0.82,
                source_agent="agent_b",
                death_hijri=None,
            ),
        ]
    )

    assert result.status == "agent_consensus"
    assert result.positions[0].position == "عبد الله بن إبراهيم الزاحم"
    assert set(result.positions[0].source_agents) == {"agent_a", "agent_b"}
    assert result.positions[0].evidence == ["title_page", "metadata_card"]


@pytest.mark.spec("REQ-SRC-0004", "AC-2")
def test_author_deliberation_preserves_disputed_positions() -> None:
    result = deliberate_author_output(
        [
            AuthorOutputPosition(
                position="أحمد بن عبد الحليم بن تيمية الحراني",
                display_name="ابن تيمية",
                death_hijri=728,
                evidence=["nisba: الحراني"],
                confidence=0.91,
                source_agent="agent_a",
            ),
            AuthorOutputPosition(
                position="عبد السلام بن عبد الله بن تيمية",
                display_name="ابن تيمية",
                death_hijri=652,
                evidence=["family_name_only"],
                confidence=0.62,
                source_agent="agent_b",
            ),
        ]
    )

    assert result.status == "agent_disagreement"
    assert len(result.positions) == 2
    assert result.positions[0].confidence >= result.positions[1].confidence


@pytest.mark.spec("REQ-SRC-0008", "AC-3")
def test_trust_evaluation_requires_two_verification_agents(source_pipeline: SourcePipeline) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm").submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    with pytest.raises(SourceEngineError) as exc:
        evaluate_trust_decision(
            dossier=dossier,
            genre="risalah",
            author_death_hijri=None,
            authority_level="modern_compilation",
            verification_agents=["agent_a"],
        )

    assert exc.value.error_code == ErrorCode.TRUST_AGENT_COUNT


def test_trust_evaluation_requires_distinct_verification_agents(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)

    with pytest.raises(SourceEngineError):
        evaluate_trust_decision(
            dossier=dossier,
            genre="risalah",
            author_death_hijri=None,
            authority_level="modern_compilation",
            verification_agents=["agent_a", "agent_a"],
        )


def test_metadata_deliberation_records_resolved_error_disagreement_case(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.author_positions = [
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=[],
            confidence=0.4,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["title_page"],
            confidence=0.85,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.author_output is not None
    assert result.source_metadata.author_output.status == "agent_consensus"
    assert len(result.disagreement_cases) == 1
    disagreement_case = result.disagreement_cases[0]
    assert disagreement_case.resolution_state == "resolved_error"
    assert disagreement_case.failure_analysis is not None
    assert disagreement_case.failure_analysis.agent_id == "agent_a"
    assert source_pipeline.store.get_disagreement_cases(source_id)[0].case_id == disagreement_case.case_id


def test_metadata_deliberation_records_genuine_dispute_with_full_positions(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.author_positions = [
        AuthorOutputPosition(
            position="أحمد بن عبد الحليم بن تيمية الحراني",
            display_name="ابن تيمية",
            evidence=["nisba: الحراني"],
            confidence=0.91,
            source_agent="agent_a",
            death_hijri=728,
        ),
        AuthorOutputPosition(
            position="عبد السلام بن عبد الله بن تيمية",
            display_name="ابن تيمية",
            evidence=["family_name_only"],
            confidence=0.62,
            source_agent="agent_b",
            death_hijri=652,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.author_output is not None
    assert result.source_metadata.author_output.status == "agent_disagreement"
    assert all(position.source_agents for position in result.source_metadata.author_output.positions)
    assert len(result.disagreement_cases) == 1
    disagreement_case = result.disagreement_cases[0]
    assert disagreement_case.resolution_state == "genuine_scholarly_dispute"
    assert disagreement_case.round_count == 3
    assert result.monitor_feedback[0].uncertainty_flags.multi_position_output is True


def test_metadata_deliberation_does_not_collapse_real_dispute_when_third_position_loses_evidence(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.author_positions = [
        AuthorOutputPosition(
            position="أحمد بن عبد الحليم بن تيمية الحراني",
            display_name="ابن تيمية",
            evidence=["nisba: الحراني"],
            confidence=0.91,
            source_agent="agent_a",
            death_hijri=728,
        ),
        AuthorOutputPosition(
            position="عبد السلام بن عبد الله بن تيمية",
            display_name="ابن تيمية",
            evidence=["family_name_only"],
            confidence=0.73,
            source_agent="agent_b",
            death_hijri=652,
        ),
        AuthorOutputPosition(
            position="أحمد بن عبد الحليم بن تيمية الحراني",
            display_name="ابن تيمية",
            evidence=[],
            confidence=0.4,
            source_agent="agent_c",
            death_hijri=728,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.author_output is not None
    assert result.source_metadata.author_output.status == "agent_disagreement"
    assert len(result.disagreement_cases) == 1
    assert result.disagreement_cases[0].resolution_state == "genuine_scholarly_dispute"


def test_hint_comparison_treats_matching_lower_ranked_disputed_author_as_match() -> None:
    metadata = _base_metadata()
    metadata.author_output = deliberate_author_output(
        [
            AuthorOutputPosition(
                position="أحمد بن عبد الحليم بن تيمية الحراني",
                display_name="ابن تيمية",
                evidence=["nisba: الحراني"],
                confidence=0.91,
                source_agent="agent_a",
                death_hijri=728,
            ),
            AuthorOutputPosition(
                position="عبد السلام بن عبد الله بن تيمية",
                display_name="ابن تيمية",
                evidence=["family_name_only"],
                confidence=0.62,
                source_agent="agent_b",
                death_hijri=652,
            ),
        ]
    )

    updated = compare_owner_hints(metadata, {"author_name": "عبد السلام بن عبد الله بن تيمية"})

    assert updated.hint_comparison_results[0].match is True
    assert updated.hint_investigation == []


def test_metadata_deliberation_rejects_mismatched_source_id(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id="src_fake")
    request.author_positions = [
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["metadata_card"],
            confidence=0.88,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["title_page"],
            confidence=0.85,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]

    with pytest.raises(SourceEngineError) as exc:
        source_pipeline.metadata_deliberation(
            source_id=source_id,
            deliberation_input=request,
        )

    assert exc.value.error_code == ErrorCode.SOURCE_ID_MISMATCH


def test_metadata_deliberation_uses_frozen_source_provenance_not_caller_scaffold(
    source_pipeline: SourcePipeline,
) -> None:
    frozen = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    )
    source_pipeline.classify_container(frozen.source_id)
    source_pipeline.intake_analysis(frozen.source_id)
    request = _base_request(source_id=frozen.source_id)
    request.frozen_path = "library/sources/fake/frozen"
    request.frozen_hash = "b" * 64
    request.frozen_file_hashes = {"book.htm": "c" * 64}
    request.author_positions = [
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["metadata_card"],
            confidence=0.88,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["title_page"],
            confidence=0.85,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=frozen.source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.frozen_path == frozen.frozen_blob_path
    assert result.source_metadata.frozen_hash == frozen.source_sha256
    assert result.source_metadata.frozen_file_hashes["book.htm"] == frozen.frozen_member_manifest[0].member_sha256


def test_metadata_deliberation_derives_work_id_from_definitive_work_output(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.work_id = None
    request.author_positions = [
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["metadata_card"],
            confidence=0.88,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["title_page"],
            confidence=0.85,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.work_output is not None
    assert result.source_metadata.work_output.positions
    assert result.source_metadata.work_id == result.source_metadata.work_output.positions[0].work_id


def test_fallback_work_output_preserves_multiple_candidates_as_disputed() -> None:
    dossier = IntakeDossier(
        dossier_id="dos_test",
        work_identity_proposal=WorkIdentityProposal(
            candidates=[
                WorkIdentityCandidate(
                    canonical_title_arabic="العمل الأول",
                    work_id="wrk_1",
                    evidence=["title_page"],
                    confidence=0.72,
                    source_agent="agent_a",
                ),
                WorkIdentityCandidate(
                    canonical_title_arabic="العمل الثاني",
                    work_id="wrk_2",
                    evidence=["metadata_card"],
                    confidence=0.68,
                    source_agent="agent_b",
                ),
            ]
        ),
    )

    result = _fallback_work_output(dossier)

    assert result.status == "disputed"
    assert len(result.positions) == 2


def test_metadata_deliberation_getters_return_latest_run_only(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    first_request = _base_request(source_id=source_id)
    first_request.author_positions = [
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["metadata_card"],
            confidence=0.88,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="عبد الله بن إبراهيم الزاحم",
            display_name="عبد الله بن إبراهيم الزاحم",
            evidence=["title_page"],
            confidence=0.85,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]
    second_request = _base_request(source_id=source_id)
    second_request.author_positions = [
        AuthorOutputPosition(
            position="أحمد بن عبد الحليم بن تيمية الحراني",
            display_name="ابن تيمية",
            evidence=["nisba: الحراني"],
            confidence=0.91,
            source_agent="agent_a",
            death_hijri=728,
        ),
        AuthorOutputPosition(
            position="عبد السلام بن عبد الله بن تيمية",
            display_name="ابن تيمية",
            evidence=["family_name_only"],
            confidence=0.62,
            source_agent="agent_b",
            death_hijri=652,
        ),
    ]

    first_result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=first_request,
    )
    second_result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=second_request,
    )

    assert source_pipeline.store.get_case_complexity_record(source_id).case_id == second_result.case_complexity_record.case_id
    assert len(source_pipeline.store.get_monitor_feedback(source_id)) == 1
    assert source_pipeline.store.get_monitor_feedback(source_id)[0].case_id == second_result.case_complexity_record.case_id
    assert source_pipeline.store.get_case_complexity_history(source_id)[0].case_id == first_result.case_complexity_record.case_id
    assert source_pipeline.store.get_case_complexity_history(source_id)[1].case_id == second_result.case_complexity_record.case_id


def test_metadata_deliberation_inferrs_sharh_metadata_from_real_fixture(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "11_multi_small"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    dossier = source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.title_arabic = dossier.title_evidence[0].title_text
    request.science_scope = ["nahw"]
    request.genre = None
    request.structural_format = StructuralFormat.PROSE
    request.author_positions = [
        AuthorOutputPosition(
            position="عبد الرحمن بن أبي بكر جلال الدين السيوطي",
            display_name="السيوطي",
            evidence=["metadata_card"],
            confidence=0.9,
            source_agent="agent_a",
            death_hijri=911,
        ),
        AuthorOutputPosition(
            position="عبد الرحمن بن أبي بكر جلال الدين السيوطي",
            display_name="السيوطي",
            evidence=["title_page"],
            confidence=0.88,
            source_agent="agent_b",
            death_hijri=911,
        ),
    ]
    request.author_death_hijri = 911

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.genre == Genre.SHARH
    assert result.source_metadata.is_multi_layer is True
    assert "شرح" in result.source_metadata.multi_layer_evidence
    assert result.source_metadata.structural_format == StructuralFormat.COMMENTARY
    assert result.source_metadata.work_relationships
    assert result.source_metadata.work_relationships[0].relationship_type == "is_commentary_on"
    assert "جمع الجوامع" in result.source_metadata.work_relationships[0].target_work_title


def test_metadata_deliberation_inferrs_hadith_subgenre_from_real_fixture(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "shamela_real" / "04_hadith" / "book.htm"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.title_arabic = "جزء فيه من أحاديث الإمام أيوب السختياني"
    request.science_scope = ["hadith"]
    request.genre = Genre.HADITH_COLLECTION
    request.structural_format = StructuralFormat.PROSE
    request.author_positions = [
        AuthorOutputPosition(
            position="إسماعيل بن إسحاق القاضي",
            display_name="القاضي إسماعيل",
            evidence=["metadata_card"],
            confidence=0.9,
            source_agent="agent_a",
            death_hijri=282,
        ),
        AuthorOutputPosition(
            position="إسماعيل بن إسحاق القاضي",
            display_name="القاضي إسماعيل",
            evidence=["title_page"],
            confidence=0.88,
            source_agent="agent_b",
            death_hijri=282,
        ),
    ]
    request.author_death_hijri = 282

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.source_metadata.hadith_subgenre is not None
    assert result.source_metadata.hadith_subgenre.value == "juz"


def test_metadata_deliberation_flags_incomplete_research_in_monitor_feedback(
    source_pipeline: SourcePipeline,
) -> None:
    source_id = source_pipeline.freeze_and_manifest(
        source_pipeline.upload_receipt(
            FIXTURES_ROOT / "waraqat_usul" / "waraqat.pdf"
        ).submission_id
    ).source_id
    source_pipeline.classify_container(source_id)
    source_pipeline.intake_analysis(source_id)
    request = _base_request(source_id=source_id)
    request.source_format = SourceFormat.PDF
    request.research_source_types = ["metadata_card"]
    request.author_positions = [
        AuthorOutputPosition(
            position="مؤلف مجهول",
            display_name="مؤلف مجهول",
            evidence=["metadata_card"],
            confidence=0.51,
            source_agent="agent_a",
            death_hijri=None,
        ),
        AuthorOutputPosition(
            position="مؤلف مجهول",
            display_name="مؤلف مجهول",
            evidence=["title_page"],
            confidence=0.48,
            source_agent="agent_b",
            death_hijri=None,
        ),
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.case_complexity_record.case_complexity == "degraded_evidence"
    assert result.monitor_feedback[0].evidence_coverage.meets_minimum is False
    assert ErrorCode.INCOMPLETE_RESEARCH in result.monitor_feedback[0].spec_violations


@pytest.mark.parametrize(
    "title,science_scope,genre,expected",
    [
        ("كتاب الفقه", ["fiqh"], Genre.MATN, None),
        ("علل الترمذي الكبير", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.ILAL),
        ("المستخرج لأبي عوانة", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.MUSTAKHRAJ),
        ("المستدرك على الصحيحين", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.MUSTADRAK),
        ("كتاب الأطراف للمزي", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.ATRAF),
        ("اطراف الصحيحين للواسطي", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.ATRAF),
        ("تخريج أحاديث الإحياء للعراقي", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.TAKHRIJ),
        ("الأربعين النووية", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.ARBAIN),
        ("طبقات رجال الحديث", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.TABAQAT_RIJAL),
        ("طبقات رواة الحديث", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.TABAQAT_RIJAL),
        ("شرح صحيح البخاري", ["hadith"], Genre.SHARH, HadithSubgenre.HADITH_COMMENTARY),
        ("جزء فيه من حديث الإمام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.JUZ),
        # Phase 5b item 23 closure 2026-04-26: Codex CRITICAL DIM4 fix —
        # bundle "مصنف" → MUSANNAF inference (al-Muṣannaf of ʿAbd al-Razzāq,
        # al-Muṣannaf of Ibn Abī Shaybah; al-Kattānī, *al-Risālah al-
        # Mustaṭrafah* p. 36 *Kutub al-Muṣannafāt*).
        ("مصنف عبد الرزاق", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.MUSANNAF),
        ("مسند الإمام أحمد", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.MUSNAD),
        ("سنن أبي داود", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.SUNAN),
        ("الجامع الصغير", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.JAMI),
        ("المعجم الكبير للطبراني", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.MUJAM),
        # Phase 5b follow-up 34 closure 2026-04-27: AHKAM activated as
        # leveled hadith_subgenre per 2-of-2 Gemini scholarly convergence
        # at HIGH confidence (Run A AMEND_REQUIRED + Run B PROCEED, both
        # demanding compound-keyword discipline). Bulūgh al-Marām now
        # classifies as AHKAM via the compound rule "بلوغ" + "المرام";
        # ʿUmdat al-Aḥkām, al-Muntaqā fī al-Aḥkām, al-Ilmām bi-Aḥādīth
        # al-Aḥkām likewise classify as AHKAM via their respective
        # compound rules. Bare "أحكام" matching is FORBIDDEN due to
        # false-positive collisions with Aḥkām al-Qurʾān (al-Jaṣṣāṣ d.
        # 370 AH — fiqh-tafsīr), al-Aḥkām al-Sulṭāniyyah (al-Māwardī
        # d. 450 AH — siyāsah), al-Iḥkām fī Uṣūl al-Aḥkām (al-Āmidī
        # d. 631 AH — Uṣūl al-Fiqh).
        # MUKHTARAT was BLOCKED 2-of-2 HIGH by both Geminis on the basis
        # that *Mukhtārāt* is a cross-cutting descriptor (al-Ḍiyāʾ
        # al-Maqdisī's al-Aḥādīth al-Mukhtārah d. 643 AH is primary
        # transmission with full isnāds despite the name). Riyāḍ
        # al-Ṣāliḥīn therefore stays None subgenre — its correct
        # classification (TARGHIB / pedagogical jāmiʿ-of-adab per Run A
        # Q3c, MUKHTARAT-but-architecturally-jāmiʿ per Run B Q2b) is
        # deferred to NEW follow-up 35 (TARGHIB + MUKHTASAR + SHAMAIL
        # enum addition). Documented limitation: owner override on
        # Riyāḍ al-Ṣāliḥīn remains wrongly rejected under Path A until
        # FU-35 closure.
        ("رياض الصالحين", ["hadith"], Genre.HADITH_COLLECTION, None),
        ("بلوغ المرام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.AHKAM),
        # FU-34 new positive cases for AHKAM (one per compound rule):
        ("بلوغ المرام من أدلة الأحكام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.AHKAM),
        ("عمدة الأحكام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.AHKAM),
        ("الإلمام بأحاديث الأحكام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.AHKAM),
        ("المنتقى في الأحكام", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.AHKAM),
        # FU-34 false-positive guards for bare "أحكام":
        # Aḥkām al-Qurʾān (al-Jaṣṣāṣ d. 370 AH) — fiqh-tafsīr; the
        # pre-condition guard at _infer_hadith_subgenre exits early
        # because science_scope does not contain "hadith" and the genre
        # is not HADITH_COLLECTION.
        ("أحكام القرآن", ["tafsir"], Genre.TAFSIR, None),
        # al-Aḥkām al-Sulṭāniyyah (al-Māwardī d. 450 AH) — siyāsah;
        # same pre-condition exit.
        ("الأحكام السلطانية", ["fiqh"], Genre.MATN, None),
        # FU-34 sharḥ-on-aḥkām-collection guard: Iḥkām al-Aḥkām Sharḥ
        # ʿUmdat al-Aḥkām (Ibn Daqīq al-ʿĪd d. 702 AH) — even though the
        # title contains "عمدة" + "الأحكام", the HADITH_COMMENTARY branch
        # fires FIRST (genre=SHARH + science_scope=hadith) so the work
        # is correctly classified as a sharḥ on a hadith collection,
        # not as the primary AHKAM work. AHKAM compound rules are
        # ordered AFTER HADITH_COMMENTARY for exactly this reason.
        ("إحكام الأحكام شرح عمدة الأحكام", ["hadith"], Genre.SHARH, HadithSubgenre.HADITH_COMMENTARY),
        ("أحاديث متفرقة", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.JUZ),
        ("حديث الجمعة", ["hadith"], Genre.HADITH_COLLECTION, HadithSubgenre.JUZ),
        ("كتاب الأذكار", ["hadith"], Genre.MATN, None),
    ],
)
def test_infer_hadith_subgenre_arabic_keyword_mapping(
    title: str,
    science_scope: list[str],
    genre: Genre,
    expected: HadithSubgenre | None,
) -> None:
    assert _infer_hadith_subgenre(science_scope, genre, title) == expected
