from __future__ import annotations

from engines.source.contracts import (
    AuthorityLevel,
    Genre,
    InferredFieldConfidence,
    HadithSubgenre,
    LevelStatus,
    ScholarProfile,
    ScholarProfileSource,
    ScholarReference,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TextLayer,
    TrustworthinessFactor,
    TrustTier,
    WorkRelationship,
)


def test_source_contracts_support_normalization_boundary_defaults() -> None:
    metadata = SourceMetadata(
        source_id="src_test0001",
        work_id="wrk_test_test",
        human_label="Test Source",
        title_arabic="كتاب الاختبار",
        author=ScholarReference(
            canonical_id="sch_00001",
            name_arabic="المؤلف",
            confidence=0.95,
            source_of_identification="test",
        ),
        science_scope=["nahw"],
        genre=Genre.SHARH,
        source_format=SourceFormat.SHAMELA_HTML,
        authority_level=AuthorityLevel.PRIMARY,
        structural_format=StructuralFormat.PROSE,
        is_multi_layer=False,
        text_layers=[
            TextLayer(
                layer_type="matn",
                author=ScholarReference(
                    canonical_id="sch_00001",
                    name_arabic="المؤلف",
                    confidence=0.95,
                    source_of_identification="test",
                ),
            )
        ],
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.85,
        trust_factors=[
            TrustworthinessFactor(
                name="author_standing",
                weight=0.3,
                score=0.9,
                reason="test",
            )
        ],
        trust_reason="test",
        text_fidelity=TextFidelity.HIGH,
        text_fidelity_reason="test",
        confidence_scores=InferredFieldConfidence(
            genre=1.0,
            science_scope=1.0,
            level=None,
            structural_format=1.0,
            authority_level=1.0,
            multi_layer=None,
            genre_chain=None,
            author=None,
        ),
        status="acquired",
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_test0001/frozen/",
        frozen_hash="abc123",
        frozen_file_hashes={"test.htm": "abc123"},
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
        level_status=LevelStatus.PENDING_SYNTHESIS,
    )

    assert metadata.source_format is SourceFormat.SHAMELA_HTML
    assert metadata.page_count is None
    assert metadata.text_layers[0].author.canonical_id == "sch_00001"


def test_source_contracts_expose_additive_step_50_metadata_surfaces() -> None:
    metadata = SourceMetadata(
        source_id="src_test0002",
        title_arabic="صحيح البخاري",
        source_format=SourceFormat.SHAMELA_HTML,
        structural_format=StructuralFormat.REFERENCE_ENTRIES,
        intake_timestamp="2026-01-01T00:00:00Z",
        acquisition_path="manual",
        frozen_path="library/sources/src_test0002/frozen/",
        frozen_hash="def456",
        frozen_file_hashes={"book.htm": "def456"},
        status="acquired",
        science_scope=["hadith"],
        genre=Genre.HADITH_COLLECTION,
        is_multi_layer=True,
        text_fidelity=TextFidelity.HIGH,
        trust_tier=TrustTier.VERIFIED,
        trust_score=0.95,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
        death_date_hijri=None,
        level_status=LevelStatus.NON_APPLICABLE_REFERENCE,
        hadith_subgenre=HadithSubgenre.JAMI,
        candidate_subgenres=[HadithSubgenre.SUNAN],
        genre_dispute=["sharh", "hadith_collection"],
        multi_layer_evidence=["genre_auto_hint"],
        matn_embedding_style="interlinear",
        work_relationships=[
            WorkRelationship(
                relationship_type="is_commentary_on",
                target_work_title="متن الأصل",
                target_work_author="المؤلف",
                confidence="high",
            )
        ],
    )
    profile = ScholarProfile(
        full_name_lineage="أبو عبد الله محمد بن إسماعيل البخاري",
        scholarly_title="الإمام",
        madhab=None,
        primary_science="hadith",
        era_description="القرن الثالث الهجري",
        profile_source=ScholarProfileSource.SCHOLAR_AUTHORITY,
    )

    assert metadata.hadith_subgenre is HadithSubgenre.JAMI
    assert metadata.candidate_subgenres == [HadithSubgenre.SUNAN]
    assert metadata.multi_layer_evidence == ["genre_auto_hint"]
    assert metadata.work_relationships[0].relationship_type == "is_commentary_on"
    assert profile.profile_source is ScholarProfileSource.SCHOLAR_AUTHORITY
