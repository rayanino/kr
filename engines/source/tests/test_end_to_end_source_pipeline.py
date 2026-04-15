from __future__ import annotations

from engines.source.contracts import (
    AuthorOutputPosition,
    Genre,
    MetadataDeliberationInput,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TrustTier,
)
from engines.source.src.pipeline import SourcePipeline
from engines.source.tests.conftest import FIXTURES_ROOT


def test_source_pipeline_smoke_runs_all_six_steps(source_pipeline: SourcePipeline) -> None:
    receipt = source_pipeline.upload_receipt(FIXTURES_ROOT / "shamela_real" / "03_fiqh" / "book.htm")
    frozen = source_pipeline.freeze_and_manifest(receipt.submission_id)
    classification = source_pipeline.classify_container(frozen.source_id)
    dossier = source_pipeline.intake_analysis(frozen.source_id)

    deliberation_input = MetadataDeliberationInput(
        source_id=frozen.source_id,
        title_arabic="أحكام الاضطباع والرمل في الطواف",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.PROSE,
        acquisition_path="manual",
        frozen_path=frozen.frozen_blob_path,
        frozen_hash=frozen.source_sha256,
        frozen_file_hashes={"book.htm": frozen.frozen_member_manifest[0].member_sha256},
        status="accepted",
        genre=Genre.RISALAH,
        science_scope=["fiqh"],
        is_multi_layer=False,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.0,
        author_positions=[
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
        ],
        owner_hint_payload={"author_name": "عبد الله بن إبراهيم الزاحم"},
        verification_agents=["agent_a", "agent_b"],
        author_death_hijri=None,
        authority_level="modern_compilation",
        work_id="wrk_fiqh_test",
        research_source_types=["metadata_card", "title_page"],
    )
    deliberation_result = source_pipeline.metadata_deliberation(
        source_id=frozen.source_id,
        deliberation_input=deliberation_input,
    )

    result = source_pipeline.source_admission_and_normalization_handoff(
        source_id=frozen.source_id,
        deliberation_result=deliberation_result,
        owner_acknowledged=True,
    )

    assert receipt.status == "received"
    assert frozen.freeze_verification_status == "verified"
    assert classification.container_type == "shamela_single_html"
    assert dossier.completeness_status == "complete"
    assert deliberation_result.source_metadata.author_output is not None
    assert deliberation_result.source_metadata.author_output.status == "agent_consensus"
    assert deliberation_result.case_complexity_record.case_id
    assert deliberation_result.monitor_feedback
    assert result.handoff_bundle is not None
