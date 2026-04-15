from __future__ import annotations

from engines.source.contracts import (
    AuthorityLevel,
    Genre,
    InferredFieldConfidence,
    ScholarReference,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TextLayer,
    TrustworthinessFactor,
    TrustTier,
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
    )

    assert metadata.source_format is SourceFormat.SHAMELA_HTML
    assert metadata.page_count is None
    assert metadata.text_layers[0].author.canonical_id == "sch_00001"
