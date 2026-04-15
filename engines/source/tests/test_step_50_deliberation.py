from __future__ import annotations

import logging
import pytest

from engines.source.contracts import (
    AuthorityLevel,
    AuthorOutputPosition,
    ErrorCode,
    Genre,
    MetadataDeliberationInput,
    SourceMetadata,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TrustTier,
)
from engines.source.src.deliberation import (
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
        )
    ]

    result = source_pipeline.metadata_deliberation(
        source_id=source_id,
        deliberation_input=request,
    )

    assert result.case_complexity_record.case_complexity == "degraded_evidence"
    assert result.monitor_feedback[0].evidence_coverage.meets_minimum is False
    assert ErrorCode.INCOMPLETE_RESEARCH in result.monitor_feedback[0].spec_violations
