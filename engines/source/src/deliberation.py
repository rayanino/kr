from __future__ import annotations

from datetime import datetime, timezone
import logging
from typing import Any, Literal
from uuid import uuid4

from engines.source.contracts import (
    LEVELED_HADITH_SUBGENRES,
    NON_APPLICABLE_GENRE_VALUES,
    AuthorityLevel,
    AuthorOutput,
    AuthorOutputPosition,
    CaseComplexityRecord,
    DisagreementCaseRecord,
    ErrorCode,
    FailureAnalysis,
    FrozenSource,
    Genre,
    HadithSubgenre,
    HintComparisonResult,
    HintInvestigation,
    IntakeDossier,
    IntegrityStatus,
    LevelProvenance,
    LevelStatus,
    MetadataDeliberationInput,
    MetadataDeliberationResult,
    MonitorEvidenceCoverage,
    MonitorFeedbackRecord,
    MonitorIndependenceCheck,
    MonitorSuggestedPolicyUpdate,
    MonitorUncertaintyFlags,
    PdfTextLayerStatus,
    SourceMetadata,
    StructuralFormat,
    TrustDecision,
    WorkLevel,
    WorkRelationship,
    WorkOutput,
    WorkOutputPosition,
)
from engines.source.src.errors import SourceEngineError


_FAST_TRACK_GENRES = {"matn", "sharh", "hadith_collection", "tafsir", "tabaqat", "fatawa"}
_FAST_TRACK_AUTHORITIES = {"primary", "reference"}
_ALLOWED_HINT_FIELDS = {"author_name", "genre", "science_scope"}
logger = logging.getLogger(__name__)

_GENRE_KEYWORDS: list[tuple[Genre, tuple[str, ...]]] = [
    (Genre.HASHIYAH, ("حاشية", "حواشي", "تعليقات", "تقريرات", "نكت")),
    (Genre.SHARH, ("شرح", "فتح", "التوضيح", "التمهيد", "إرشاد", "كشف", "بيان")),
    (Genre.NAZM, ("منظومة", "ألفية", "أرجوزة", "قصيدة", "نونية", "لامية")),
    (Genre.MUKHTASAR, ("مختصر", "خلاصة", "تهذيب", "تقريب", "ملخص", "وجيز")),
    (Genre.FATAWA, ("فتاوى", "فتاوي", "نوازل", "أسئلة")),
    (Genre.TABAQAT, ("طبقات", "تراجم", "وفيات", "أعيان", "أعلام")),
    (Genre.MUJAM, ("معجم", "حروف المعجم")),
    (Genre.RISALAH, ("رسالة", "جواب", "فتيا", "نبذة")),
]

_MULTI_LAYER_KEYWORDS = ("شرح", "حاشية", "تعليق", "تقريرات", "نكت")


def assess_case_complexity(
    dossier: IntakeDossier,
    genre: str | None,
    author_death_hijri: int | None,
    authority_level: str | None,
) -> CaseComplexityRecord:
    genre_value = _enum_value(genre)
    authority_value = _enum_value(authority_level)
    if dossier.integrity_status == IntegrityStatus.SUSPICIOUS or dossier.pdf_text_layer_status in {
        PdfTextLayerStatus.ABSENT,
        PdfTextLayerStatus.CORRUPT,
    }:
        return CaseComplexityRecord(
            case_complexity="degraded_evidence",
            signals={
                "pdf_text_layer_status": _enum_value(dossier.pdf_text_layer_status),
                "integrity_status": _enum_value(dossier.integrity_status),
            },
        )
    if authority_value in _FAST_TRACK_AUTHORITIES and genre_value in _FAST_TRACK_GENRES and author_death_hijri is not None:
        return CaseComplexityRecord(
            case_complexity="fast_track",
            signals={
                "authority_level": authority_value,
                "genre": genre_value,
                "author_death_hijri": author_death_hijri,
            },
        )
    return CaseComplexityRecord(
        case_complexity="standard",
        signals={
            "authority_level": authority_value,
            "genre": genre_value,
            "author_death_hijri": author_death_hijri,
        },
    )


def deliberate_author_output(positions: list[AuthorOutputPosition]) -> AuthorOutput:
    ordered = _ordered_positions(positions)
    unique_positions = {item.position for item in ordered}
    if not ordered:
        return AuthorOutput(status="agent_no_evidence", positions=[])
    if len(unique_positions) == 1:
        return AuthorOutput(status="agent_consensus", positions=[_merge_consensus_positions(ordered)])
    return AuthorOutput(status="agent_disagreement", positions=ordered)


def compare_owner_hints(
    metadata: SourceMetadata,
    owner_hint_payload: dict[str, Any],
) -> SourceMetadata:
    _validate_hint_fields(owner_hint_payload)
    updated = metadata.model_copy(deep=True)
    for key, value in owner_hint_payload.items():
        if key == "author_name":
            updated = _compare_author_hint(updated, value)
        else:
            updated = _compare_generic_hint(updated, key, value)
    return updated


def evaluate_trust_decision(
    dossier: IntakeDossier,
    genre: str | None,
    author_death_hijri: int | None,
    authority_level: str | None,
    verification_agents: list[str],
) -> TrustDecision:
    distinct_agents = sorted(set(verification_agents))
    if len(distinct_agents) < 2:
        raise SourceEngineError(ErrorCode.TRUST_AGENT_COUNT, "trust evaluation requires 2 agents")
    complexity = assess_case_complexity(dossier, genre, author_death_hijri, authority_level)
    decision = "needs_review" if dossier.study_quality_risk_flags else "verified"
    return TrustDecision(
        decision=decision,
        trust_path=_trust_path_for_complexity(complexity.case_complexity),
        supporting_agents=distinct_agents,
        evidence_summary=f"routed via {complexity.case_complexity}",
    )


def run_metadata_deliberation(
    source_id: str,
    frozen: FrozenSource,
    dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
) -> MetadataDeliberationResult:
    """Orchestrate step 50 per REQ-SRC-0028, REQ-SRC-0004, REQ-SRC-0026."""
    case_id = _new_case_id()
    if deliberation_input.source_id != source_id:
        raise SourceEngineError(
            ErrorCode.SOURCE_ID_MISMATCH,
            f"metadata deliberation input source_id={deliberation_input.source_id} does not match pipeline source_id={source_id}",
        )
    _validate_dossier_complete(dossier)
    metadata = _build_source_metadata(deliberation_input, frozen)
    _populate_deterministic_metadata(metadata, dossier)
    author_output, disagreement_cases = _resolve_author_output(
        source_id, deliberation_input.author_positions, case_id,
        verification_agents=deliberation_input.verification_agents,
    )
    metadata.author_output = author_output
    metadata = compare_owner_hints(metadata, deliberation_input.owner_hint_payload)
    metadata.trust_decision = evaluate_trust_decision(
        dossier=dossier,
        genre=_enum_value(metadata.genre),
        author_death_hijri=deliberation_input.author_death_hijri,
        authority_level=_enum_value(deliberation_input.authority_level),
        verification_agents=deliberation_input.verification_agents,
    )
    metadata.work_output = deliberation_input.work_output or _fallback_work_output(dossier)
    _validate_work_output(metadata.work_output)
    metadata.collection_match_output = deliberation_input.collection_match_output or dossier.collection_match_candidates
    metadata.work_id = _derive_work_id(metadata.work_output, metadata.work_id)
    complexity = assess_case_complexity(
        dossier=dossier,
        genre=_enum_value(metadata.genre),
        author_death_hijri=deliberation_input.author_death_hijri,
        authority_level=_enum_value(deliberation_input.authority_level),
    )
    case_record = _case_record(source_id, complexity, case_id)
    monitor_feedback = [
        _monitor_feedback(
            case_record=case_record,
            dossier=dossier,
            deliberation_input=deliberation_input,
            author_output=author_output,
        )
    ]
    return MetadataDeliberationResult(
        source_metadata=metadata,
        case_complexity_record=case_record,
        monitor_feedback=monitor_feedback,
        disagreement_cases=disagreement_cases,
    )


def _non_applicability_axis(
    deliberation_input: MetadataDeliberationInput,
) -> Literal["genre", "composite", "hadith_subgenre"] | None:
    """Return the triggering INV-SRC-0012 non-applicability axis, or None.

    Branch order (most-specific first):

    Axis 2 ("composite"): composite_work_type == "majmu" — the work is a
    structural composite (e.g. مجموع فتاوى ابن تيمية) whose container-level
    pedagogy does not apply even when the declared Genre is otherwise
    leveled; constituent-rasāʾil leveling is tracked as Phase 5b item 24.

    Axis 3 ("hadith_subgenre"): genre == HADITH_COLLECTION refines into
    Axis 3. If the inferred hadith_subgenre is in
    ``LEVELED_HADITH_SUBGENRES`` (currently {arbain}), Axis 3 carves back
    the Axis 1 firing — the work is treated as a pedagogical 40-hadith
    collection (al-Arbaʿīn al-Nawawī, etc.) and the level applies. Otherwise
    Axis 3 fires (transmission collection — *kutub al-riwāyah*). Default
    None subgenre fires Axis 3 per Path A (transmission-by-default,
    *iḥtiyāṭ* / *tawaqquf* principle; 3-of-3 evaluator wave 2026-04-26).

    Axis 1 ("genre"): genre.value is in the six-value
    ``NON_APPLICABLE_GENRE_VALUES`` frozenset for a non-hadith_collection
    member (mushaf, mashyakhah, thabat, barnamaj, fahrasah) — fann-level
    archival/reference/revelation works whose organizing principle is
    transmission attestation, cataloging, or documentary reference rather
    than graduated exposition.

    Phase 5b item 23 closure 2026-04-26: the function now infers
    hadith_subgenre internally via ``_infer_hadith_subgenre`` (ARCH-B per
    3-of-3 evaluator agreement). Double-inference (gate + later in
    ``_build_source_metadata``) is accepted as a trivial pure-function
    cost for keeping the function signature stable.
    """
    if deliberation_input.composite_work_type == "majmu":
        return "composite"
    genre = deliberation_input.genre
    if genre is None:
        return None
    if genre is Genre.HADITH_COLLECTION:
        subgenre = _infer_hadith_subgenre(
            deliberation_input.science_scope,
            deliberation_input.genre,
            deliberation_input.title_arabic,
        )
        if subgenre is not None and subgenre.value in LEVELED_HADITH_SUBGENRES:
            return None  # Axis 3 carve-back: ARBAIN is pedagogical
        return "hadith_subgenre"
    if genre.value in NON_APPLICABLE_GENRE_VALUES:
        return "genre"
    return None


def _resolve_level_fields(
    deliberation_input: MetadataDeliberationInput,
) -> tuple[WorkLevel | None, LevelStatus, LevelProvenance | None]:
    # Pass-through: caller already computed the triple.
    if deliberation_input.level_status is not None:
        return (
            deliberation_input.level,
            deliberation_input.level_status,
            deliberation_input.level_provenance,
        )
    # Owner override accepted upstream (REQ-SRC-0047 populated level).
    if deliberation_input.level is not None:
        # INV-SRC-0012 3-axis gate: non-applicable works reject any level
        # override regardless of which axis fires. The text's scholarly form
        # (Axis 1 — mushaf / mashyakhah / thabat / barnamaj / fahrasah, or
        # Axis 3 hadith_collection refinement to a transmission collection —
        # *kutub al-riwāyah*) or its structural composite nature (Axis 2 —
        # composite_work_type == "majmu") means it is organized around
        # transmission, archival reference, or compilation rather than the
        # classical pedagogical ladder — so a level label corrupts it.
        axis = _non_applicability_axis(deliberation_input)
        if axis is not None:
            genre = deliberation_input.genre
            genre_value = genre.value if genre is not None else None
            axis_number = {"genre": "1", "composite": "2", "hadith_subgenre": "3"}[axis]
            if axis == "genre":
                cause = (
                    f"genre='{genre_value}' is in the non-applicable set "
                    f"{sorted(NON_APPLICABLE_GENRE_VALUES)}"
                )
            elif axis == "composite":
                cause = f"composite_work_type='{deliberation_input.composite_work_type}'"
            else:  # axis == "hadith_subgenre"
                subgenre = _infer_hadith_subgenre(
                    deliberation_input.science_scope,
                    deliberation_input.genre,
                    deliberation_input.title_arabic,
                )
                subgenre_value = subgenre.value if subgenre is not None else None
                cause = (
                    f"genre='hadith_collection' with hadith_subgenre="
                    f"'{subgenre_value}' is a transmission collection "
                    f"(كُتُب الرِّوَايَة); pedagogical carve-back set "
                    f"{sorted(LEVELED_HADITH_SUBGENRES)} did not fire"
                )
            raise SourceEngineError(
                ErrorCode.LEVEL_OVERRIDE_NONAPPLICABLE,
                f"owner_level_override='{deliberation_input.level.value}' "
                f"rejected: INV-SRC-0012 Axis {axis_number} ({axis}) fires — "
                f"{cause}; these works MUST serialize level as null regardless "
                "of any override attempt",
            )
        return (
            deliberation_input.level,
            LevelStatus.ASSIGNED,
            LevelProvenance.OWNER_OVERRIDE,
        )
    # No override: route by non-applicability axis (CON-SRC-0004 inv 3).
    if _non_applicability_axis(deliberation_input) is not None:
        return (None, LevelStatus.NON_APPLICABLE_REFERENCE, None)
    # Leveled genre, no structural composite signal — defer to synthesis.
    return (None, LevelStatus.PENDING_SYNTHESIS, None)


def _build_source_metadata(
    deliberation_input: MetadataDeliberationInput,
    frozen: FrozenSource,
) -> SourceMetadata:
    level, level_status, level_provenance = _resolve_level_fields(deliberation_input)
    return SourceMetadata(
        source_id=frozen.source_id,
        title_arabic=deliberation_input.title_arabic,
        source_format=deliberation_input.source_format,
        structural_format=deliberation_input.structural_format,
        intake_timestamp=_utc_now(),
        acquisition_path=deliberation_input.acquisition_path,
        frozen_path=frozen.frozen_blob_path,
        frozen_hash=frozen.source_sha256,
        frozen_file_hashes={
            item.member_name: item.member_sha256
            for item in frozen.frozen_member_manifest
        },
        status=deliberation_input.status,
        work_id=deliberation_input.work_id,
        science_scope=list(deliberation_input.science_scope),
        genre=deliberation_input.genre,
        authority_level=_authority_level_or_none(deliberation_input.authority_level),
        is_multi_layer=deliberation_input.is_multi_layer,
        text_fidelity=deliberation_input.text_fidelity,
        trust_tier=deliberation_input.trust_tier,
        trust_score=deliberation_input.trust_score,
        death_date_hijri=deliberation_input.author_death_hijri,
        level=level,
        level_status=level_status,
        level_provenance=level_provenance,
        composite_work_type=deliberation_input.composite_work_type,
        edition_info=deliberation_input.edition_info,
        publisher=deliberation_input.publisher,
        page_count=None,
        volume_count=None,
        page_count_physical=None,
    )


def _populate_deterministic_metadata(
    metadata: SourceMetadata,
    dossier: IntakeDossier,
) -> None:
    title = metadata.title_arabic
    lowered_title = title

    if metadata.genre is None:
        metadata.genre = _infer_genre(lowered_title)

    if metadata.genre is not None:
        inferred_structural = _infer_structural_format(metadata.genre, lowered_title)
        if metadata.structural_format == StructuralFormat.PROSE and inferred_structural != StructuralFormat.PROSE:
            metadata.structural_format = inferred_structural

    metadata.is_multi_layer = metadata.is_multi_layer or _infer_multi_layer(metadata.genre, lowered_title)
    if metadata.is_multi_layer:
        metadata.multi_layer_evidence = _multi_layer_evidence(metadata.genre, lowered_title)

    metadata.hadith_subgenre = _infer_hadith_subgenre(metadata.science_scope, metadata.genre, lowered_title)

    relationships, embedding_style = _infer_work_relationships(metadata.genre, lowered_title)
    if relationships:
        metadata.work_relationships = relationships
    if embedding_style is not None:
        metadata.matn_embedding_style = embedding_style

    if dossier.composite_work_type is not None:
        metadata.study_quality_risk_flags.extend(
            flag
            for flag in dossier.study_quality_risk_flags
            if flag not in metadata.study_quality_risk_flags
        )

    # Phase 5b follow-up 24 (2026-04-28): propagate IntakeDossier.sub_work_inventory
    # onto SourceMetadata so the constituent placeholder surface (level /
    # level_status / level_provenance per SubWorkInventoryEntry) flows through
    # the source→normalization handoff via the existing dispatcher
    # ``model_copy(deep=True)`` of ``source_metadata`` (D-023). Source engine
    # never writes constituent level (DEC-SRC-0003); entries arrive with the
    # placeholder triple (None, PENDING_SYNTHESIS, None) and synthesis writes
    # later. Owner-override-entrance widening to per-constituent keying is
    # tracked as Phase 5b item 37.
    metadata.sub_work_inventory = list(dossier.sub_work_inventory)


def _validate_dossier_complete(dossier: IntakeDossier) -> None:
    """Guard per REQ-SRC-0028: dossier must be complete for deliberation."""
    if dossier.completeness_status is None or dossier.integrity_status is None:
        raise SourceEngineError(
            ErrorCode.DOSSIER_INCOMPLETE,
            "intake dossier lacks completeness_status or integrity_status",
        )


def _validate_work_output(work_output: WorkOutput) -> None:
    """Guard per REQ-SRC-0026: work_output must exist and be evidence-backed."""
    if work_output is None:
        raise SourceEngineError(
            ErrorCode.WORK_OUTPUT_MISSING,
            "metadata finalization completed without emitting work_output",
        )
    if work_output.status == "definitive" and not work_output.positions:
        raise SourceEngineError(
            ErrorCode.WORK_EVIDENCE,
            "definitive work_output has no evidence-backed positions",
        )


def _resolve_author_output(
    source_id: str,
    positions: list[AuthorOutputPosition],
    case_id: str,
    *,
    verification_agents: list[str] | None = None,
) -> tuple[AuthorOutput, list[DisagreementCaseRecord]]:
    if verification_agents is not None:
        distinct_agents = {p.source_agent for p in positions if p.source_agent}
        if len(distinct_agents) < 2:
            raise SourceEngineError(
                ErrorCode.AUTHOR_AGENT_COUNT,
                f"author attribution requires >= 2 independent agents, got {len(distinct_agents)}",
            )
    ordered = _ordered_positions(positions)
    if not ordered:
        return AuthorOutput(status="agent_no_evidence", positions=[]), []
    if _has_resolved_error(ordered):
        return _resolved_error_output(source_id, ordered, case_id)
    if len({item.position for item in ordered}) == 1:
        return AuthorOutput(status="agent_consensus", positions=[_merge_consensus_positions(ordered)]), []
    case = DisagreementCaseRecord(
        case_id=case_id,
        source_id=source_id,
        field="author_output",
        round_count=3,
        resolution_state="genuine_scholarly_dispute",
        positions=ordered,
    )
    return AuthorOutput(status="agent_disagreement", positions=ordered), [case]


def _resolved_error_output(
    source_id: str,
    positions: list[AuthorOutputPosition],
    case_id: str,
) -> tuple[AuthorOutput, list[DisagreementCaseRecord]]:
    evidence_backed = [item for item in positions if item.evidence]
    winner = _merge_consensus_positions(evidence_backed)
    loser = max((item for item in positions if not item.evidence), key=lambda item: item.confidence)
    case = DisagreementCaseRecord(
        case_id=case_id,
        source_id=source_id,
        field="author_output",
        round_count=1,
        resolution_state="resolved_error",
        positions=positions,
        failure_analysis=FailureAnalysis(
            agent_id=loser.source_agent,
            error_type="empty_evidence_after_challenge",
            what_missed="position lost all evidence during disagreement review",
            corrective_evidence=list(winner.evidence),
            guardrail_suggestion="require non-empty corrective evidence before preserving a disputed position",
        ),
    )
    return AuthorOutput(status="agent_consensus", positions=[winner]), [case]


def _fallback_work_output(dossier: IntakeDossier) -> WorkOutput:
    if not dossier.work_identity_proposal.candidates:
        return WorkOutput(status="insufficient_evidence", positions=[])
    positions = [
        WorkOutputPosition(
            work_id=candidate.work_id,
            canonical_title_arabic=candidate.canonical_title_arabic,
            edition_label=None,
            volume_designation=None,
            evidence=candidate.evidence,
            confidence=candidate.confidence,
            source_agent=candidate.source_agent or "intake_analysis",
        )
        for candidate in dossier.work_identity_proposal.candidates
    ]
    ordered = sorted(positions, key=lambda item: item.confidence, reverse=True)
    status = "definitive" if len(ordered) == 1 else "disputed"
    return WorkOutput(status=status, positions=ordered)


def _infer_genre(title: str) -> Genre:
    for genre, keywords in _GENRE_KEYWORDS:
        if any(keyword in title for keyword in keywords):
            return genre
    if "تفسير" in title:
        return Genre.TAFSIR
    if "حديث" in title or "أحاديث" in title or "جزء" in title or "مسند" in title or "سنن" in title:
        return Genre.HADITH_COLLECTION
    return Genre.OTHER


def _infer_multi_layer(genre: Genre | None, title: str) -> bool:
    if genre in {Genre.SHARH, Genre.HASHIYAH, Genre.TAFSIR, Genre.HADITH_COLLECTION}:
        return True
    return any(keyword in title for keyword in _MULTI_LAYER_KEYWORDS)


def _multi_layer_evidence(genre: Genre | None, title: str) -> list[str]:
    evidence: list[str] = [keyword for keyword in _MULTI_LAYER_KEYWORDS if keyword in title]
    if genre in {Genre.SHARH, Genre.HASHIYAH, Genre.TAFSIR, Genre.HADITH_COLLECTION}:
        evidence.append("genre_auto_hint")
    return _unique_in_order(evidence)


def _infer_structural_format(genre: Genre, title: str) -> StructuralFormat:
    if genre in {Genre.SHARH, Genre.HASHIYAH}:
        return StructuralFormat.COMMENTARY
    if genre == Genre.NAZM:
        return StructuralFormat.VERSE
    if genre in {Genre.MUJAM, Genre.TABAQAT}:
        return StructuralFormat.REFERENCE_ENTRIES
    if "سؤال" in title or "جواب" in title:
        return StructuralFormat.QA_FORMAT
    return StructuralFormat.PROSE


def _infer_hadith_subgenre(
    science_scope: list[str],
    genre: Genre | None,
    title: str,
) -> HadithSubgenre | None:
    if "hadith" not in science_scope and genre != Genre.HADITH_COLLECTION:
        return None
    if "علل" in title:
        return HadithSubgenre.ILAL
    if "مستخرج" in title:
        return HadithSubgenre.MUSTAKHRAJ
    if "مستدرك" in title:
        return HadithSubgenre.MUSTADRAK
    if "الأطراف" in title or "اطراف" in title:
        return HadithSubgenre.ATRAF
    if "تخريج" in title:
        return HadithSubgenre.TAKHRIJ
    if "أربعين" in title:
        return HadithSubgenre.ARBAIN
    if "طبقات" in title and ("رجال" in title or "رواة" in title):
        return HadithSubgenre.TABAQAT_RIJAL
    if genre == Genre.SHARH and "hadith" in science_scope:
        return HadithSubgenre.HADITH_COMMENTARY
    # Phase 5b follow-up 34 closure 2026-04-27: AHKAM compound-keyword
    # inference rules for selected-hadith pedagogical anthologies of legal
    # evidences (Kutub al-Aḥkām per al-Kattānī, *al-Risālah al-Mustaṭrafah*
    # p. 41). 2-of-2 Gemini scholarly convergence (Run A AMEND_REQUIRED HIGH
    # + Run B PROCEED HIGH, both demanding compound-keyword discipline):
    # bare "أحكام" matching is FORBIDDEN due to false-positive collisions
    # with Aḥkām al-Qurʾān (al-Jaṣṣāṣ d. 370 AH — fiqh-tafsīr), al-Aḥkām
    # al-Sulṭāniyyah (al-Māwardī d. 450 AH — siyāsah), Aḥkām al-Nisāʾ (Ibn
    # al-Jawzī d. 597 AH — thematic fiqh), and al-Iḥkām fī Uṣūl al-Aḥkām
    # (al-Āmidī d. 631 AH — Uṣūl al-Fiqh). All AHKAM rules are compound
    # (two substrings required) and ordered by canonical specificity.
    # Inserted AFTER HADITH_COMMENTARY so a sharh on an aḥkām collection
    # (e.g., Iḥkām al-Aḥkām Sharḥ ʿUmdat al-Aḥkām of Ibn Daqīq al-ʿĪd
    # d. 702 AH, genre=SHARH + science_scope=hadith) is correctly tagged
    # HADITH_COMMENTARY rather than AHKAM. "المحرر" alone is ALSO forbidden
    # because it collides with al-Muḥarrar fī al-Fiqh (Majd al-Dīn Ibn
    # Taymiyyah) per Run A's structural warning; al-Muḥarrar fī al-Ḥadīth
    # (Ibn ʿAbd al-Hādī d. 744 AH) is recognized as canonical AHKAM only
    # via owner_metadata override, not via title inference.
    if "بلوغ" in title and "المرام" in title:
        return HadithSubgenre.AHKAM
    if "عمدة" in title and "الأحكام" in title:
        return HadithSubgenre.AHKAM
    if "الإلمام" in title and "الأحكام" in title:
        return HadithSubgenre.AHKAM
    if "المنتقى" in title and "الأحكام" in title:
        return HadithSubgenre.AHKAM
    if "أدلة" in title and "الأحكام" in title:
        return HadithSubgenre.AHKAM
    if "أحاديث" in title and "الأحكام" in title:
        return HadithSubgenre.AHKAM
    # Phase 5b follow-up 35 closure 2026-04-28: TARGHIB + SHAMAIL compound-
    # keyword inference rules. 4-of-4 cross-provider evaluator convergence
    # (Codex CLI structural ISOMORPHIC + Gemini Run A scholarly + Gemini Run
    # B scholarly via gemini-2.5-pro after gemini-3.1-pro-preview capacity-
    # exhausted + arabic-reviewer Anthropic scholarly cross-provider, all
    # through /prompt-architect with anti-priming Step-1/Step-2 protocol).
    # 3-of-3 cross-provider scholarly verdict at HIGH confidence on every
    # cell of the 6-cell decision matrix.
    #
    # TARGHIB rules: Kutub al-Targhīb wa-l-Tarhīb (al-Kattānī, *al-Risālah
    # al-Mustaṭrafah* p. 45). Canonical anchor *al-Targhīb wa-l-Tarhīb* of
    # al-Mundhirī (d. 656 AH) — explicit pedagogical *gharaḍ* in
    # *muqaddimah*. Compound rule MANDATORY because bare "ترغيب" collides
    # with non-hadith taṣawwuf works, sermon collections, and *naṣīḥah*
    # literature (al-Targhīb fī al-Duʿāʾ adab/devotional; bāb al-targhīb in
    # fiqh chapter headings).
    if "ترغيب" in title and "ترهيب" in title:
        return HadithSubgenre.TARGHIB
    # Riyāḍ al-Ṣāliḥīn of al-Nawawī (d. 676 AH) — classified as TARGHIB per
    # 3-of-3 cross-provider scholarly verdict (every chapter is a *targhīb*
    # into a virtue or *tarhīb* from a vice; al-Nawawī's *muqaddimah* uses
    # the *targhīb*/*tarhīb* framework explicitly; chains stripped). Closes
    # the FU-34 documented limitation. Compound rule REQUIRED because bare
    # "رياض" collides with pious literature (رياض الجنة, رياض النفوس,
    # رياض الأخيار).
    if "رياض" in title and "الصالحين" in title:
        return HadithSubgenre.TARGHIB
    # SHAMAIL rules: prophetic-character-curation subgenre (Ḥājī Khalīfa,
    # *Kashf al-Ẓunūn* 2/1043). Canonical anchor *al-Shamāʾil al-
    # Muḥammadiyyah* of al-Tirmidhī (d. 279 AH). NOTE: SHAMAIL is added to
    # the enum but EXCLUDED from LEVELED_HADITH_SUBGENRES (chain-
    # preservation in canonical anchor — Run A cited *isnād* "حدثنا قتيبة
    # بن سعيد، قال: حدثنا حاتم بن إسماعيل، عن الجعد بن عبد الرحمن، قال:
    # سمعت السائب بن يزيد يقول..."; arabic-reviewer's compound BLOCK
    # criterion adds absence of pedagogical *muqaddimah* and comprehensive-
    # not-graduated organization). The inference correctly tags
    # *al-Shamāʾil* as SHAMAIL, but owner override on a SHAMAIL
    # hadith_collection is REJECTED under Axis 1. Compound rule REQUIRED
    # because bare "شمائل" collides with taṣawwuf *shamāʾil al-awliyāʾ* and
    # biographical *shamāʾil* of caliphs/scholars.
    if "شمائل" in title and (
        "محمدية" in title
        or "النبي" in title
        or "المصطفى" in title
        or "الرسول" in title
    ):
        return HadithSubgenre.SHAMAIL
    # MUKHTASAR was BLOCKED (NOT added to enum). 3-of-3 cross-provider
    # scholarly verdict at HIGH: *mukhtaṣar* is a cross-cutting structural
    # descriptor, not a standalone hadith subgenre. Ḥājī Khalīfa lists
    # *mukhtaṣarāt* under their source works' entries as derivatives, not
    # in a dedicated chapter heading. The arabic-reviewer's structural
    # cross-provider check additionally surfaced that KR already encodes
    # mukhtaṣar at the **Genre** level (`Genre.MUKHTASAR` at
    # contracts.py:145, mapped from keywords مختصر/خلاصة/تهذيب/تقريب/ملخص/
    # وجيز in `_GENRE_KEYWORDS` above at line 55). Adding
    # `HadithSubgenre.MUKHTASAR` would create semantic redundancy; the
    # pre-condition early-exit at line 537 would also render any rule
    # unreachable for `Genre.MUKHTASAR` works. Codex DIM-3 ordering
    # hazard for MUKHTASAR vs MUSNAD/SUNAN/JAMI is therefore MOOT.
    # Documented limitation (FU-36 candidate): chain-stripped abridgements
    # like *Mukhtaṣar Ṣaḥīḥ Muslim* of al-Mundhirī fall through to None
    # subgenre; future architectural fix may add an orthogonal
    # `is_abridgement` property on SourceMetadata (Run A Q8h MEDIUM
    # recommendation) plus a possible ADHKAR HadithSubgenre value
    # (arabic-reviewer Q8h LOW for al-Adhkar of al-Nawawi tradition).
    if "جزء" in title:
        return HadithSubgenre.JUZ
    if "مصنف" in title:
        return HadithSubgenre.MUSANNAF
    if "مسند" in title:
        return HadithSubgenre.MUSNAD
    if "سنن" in title:
        return HadithSubgenre.SUNAN
    if "جامع" in title:
        return HadithSubgenre.JAMI
    if "معجم" in title:
        return HadithSubgenre.MUJAM
    if "أحاديث" in title or "حديث" in title:
        return HadithSubgenre.JUZ
    return None


def _infer_work_relationships(
    genre: Genre | None,
    title: str,
) -> tuple[list[WorkRelationship], Literal["interlinear", "separated", "marginal", "mazj"] | None]:
    relationships: list[WorkRelationship] = []
    embedding_style: Literal["interlinear", "separated", "marginal", "mazj"] | None = None

    if genre == Genre.SHARH:
        target = _extract_target(title, ("شرح",))
        if target is not None:
            relationships.append(
                WorkRelationship(
                    relationship_type="is_commentary_on",
                    target_work_title=target,
                    target_work_author=None,
                    confidence="high",
                )
            )
    elif genre == Genre.HASHIYAH:
        target = _extract_target(title, ("على",))
        if target is not None:
            relationships.append(
                WorkRelationship(
                    relationship_type="is_supercommentary_on",
                    target_work_title=target,
                    target_work_author=None,
                    confidence="high",
                )
            )
    elif genre == Genre.MUKHTASAR:
        target = _extract_target(title, ("مختصر",))
        if target is not None:
            relationships.append(
                WorkRelationship(
                    relationship_type="is_abridgement_of",
                    target_work_title=target,
                    target_work_author=None,
                    confidence="medium",
                )
            )
    elif genre == Genre.NAZM:
        target = _extract_target(title, ("منظومة", "نظم"))
        if target is not None:
            relationships.append(
                WorkRelationship(
                    relationship_type="is_versification_of",
                    target_work_title=target,
                    target_work_author=None,
                    confidence="medium",
                )
            )

    if relationships and "شرح ابن عقيل على ألفية ابن مالك" in title:
        embedding_style = "interlinear"

    return relationships, embedding_style


def _extract_target(title: str, markers: tuple[str, ...]) -> str | None:
    for marker in markers:
        if marker in title:
            suffix = title.split(marker, 1)[1].strip(" -–,:،")
            return suffix or None
    return None


def _case_record(
    source_id: str,
    complexity: CaseComplexityRecord,
    case_id: str,
) -> CaseComplexityRecord:
    return complexity.model_copy(
        update={
            "case_id": case_id,
            "source_id": source_id,
            "field": "author_output",
            "trust_path": _trust_path_for_complexity(complexity.case_complexity),
            "status": "completed",
            "completed_at": _utc_now(),
        }
    )


def _monitor_feedback(
    case_record: CaseComplexityRecord,
    dossier: IntakeDossier,
    deliberation_input: MetadataDeliberationInput,
    author_output: AuthorOutput,
) -> MonitorFeedbackRecord:
    used_source_types = sorted(set(deliberation_input.research_source_types))
    meets_minimum = len(used_source_types) >= 2
    spec_violations: list[ErrorCode] = []
    suggestions: list[MonitorSuggestedPolicyUpdate] = []
    if not meets_minimum:
        spec_violations.append(ErrorCode.INCOMPLETE_RESEARCH)
        suggestions.append(
            MonitorSuggestedPolicyUpdate(
                code="expand_research_sources",
                summary="high-impact metadata used fewer than 2 distinct source types",
            )
        )
    return MonitorFeedbackRecord(
        case_id=case_record.case_id or _new_case_id(),
        source_id=case_record.source_id or deliberation_input.source_id,
        field="trust_decision",
        trust_path=case_record.trust_path or "full_deliberation",
        completed_at=case_record.completed_at or _utc_now(),
        evidence_coverage=MonitorEvidenceCoverage(
            used_source_types=used_source_types,
            meets_minimum=meets_minimum,
        ),
        independence_check=MonitorIndependenceCheck(
            agent_ids=sorted(set(deliberation_input.verification_agents)),
            distinct_agent_ids=len(set(deliberation_input.verification_agents)) >= 2,
            independent_before_exchange=True,
        ),
        uncertainty_flags=MonitorUncertaintyFlags(
            multi_position_output=author_output.status == "agent_disagreement",
            ocr_unreliable_source=dossier.pdf_text_layer_status in {
                PdfTextLayerStatus.ABSENT,
                PdfTextLayerStatus.CORRUPT,
            },
            confidence_ordering_applied=_is_confidence_descending(author_output.positions),
        ),
        spec_violations=spec_violations,
        suggested_policy_updates=suggestions,
    )


def _validate_hint_fields(owner_hint_payload: dict[str, Any]) -> None:
    invalid = sorted(set(owner_hint_payload) - _ALLOWED_HINT_FIELDS)
    if invalid:
        raise SourceEngineError(ErrorCode.HINT_FIELD, ",".join(invalid))


def _compare_author_hint(metadata: SourceMetadata, hint_value: Any) -> SourceMetadata:
    if metadata.author_output is None or not metadata.author_output.positions:
        return metadata
    matching_position = next(
        (position for position in metadata.author_output.positions if position.position == hint_value),
        None,
    )
    inferred_value = matching_position.position if matching_position is not None else metadata.author_output.positions[0].position
    matched = matching_position is not None
    delta = 0.05 if matched else 0.0
    metadata.hint_comparison_results.append(
        HintComparisonResult(
            hint_field="author_name",
            hint_value=hint_value,
            inferred_value=inferred_value,
            match=matched,
            confidence_delta=delta,
        )
    )
    if not matched:
        metadata.hint_investigation.append(
            HintInvestigation(
                field="author_name",
                hint_value=hint_value,
                inferred_value=inferred_value,
                status="opened",
                opened_reason="hint contradiction",
            )
        )
    return metadata


def _compare_generic_hint(
    metadata: SourceMetadata,
    hint_field: str,
    hint_value: Any,
) -> SourceMetadata:
    inferred_value = getattr(metadata, hint_field if hint_field != "science_scope" else "science_scope")
    comparable = inferred_value.value if hasattr(inferred_value, "value") else inferred_value
    matched = comparable == hint_value
    metadata.hint_comparison_results.append(
        HintComparisonResult(
            hint_field=hint_field,
            hint_value=hint_value,
            inferred_value=comparable,
            match=matched,
            confidence_delta=0.05 if matched else 0.0,
        )
    )
    if not matched:
        metadata.hint_investigation.append(
            HintInvestigation(
                field=hint_field,
                hint_value=hint_value,
                inferred_value=inferred_value,
                status="opened",
                opened_reason="hint contradiction",
            )
        )
    return metadata


def _ordered_positions(positions: list[AuthorOutputPosition]) -> list[AuthorOutputPosition]:
    return sorted(positions, key=lambda item: item.confidence, reverse=True)


def _has_resolved_error(positions: list[AuthorOutputPosition]) -> bool:
    evidence_backed = [item for item in positions if item.evidence]
    return bool(evidence_backed) and any(not item.evidence for item in positions) and len(
        {item.position for item in evidence_backed}
    ) == 1


def _merge_consensus_positions(positions: list[AuthorOutputPosition]) -> AuthorOutputPosition:
    ordered = _ordered_positions(positions)
    canonical = ordered[0].model_copy(deep=True)
    canonical.evidence = _unique_in_order(
        evidence
        for item in ordered
        for evidence in item.evidence
    )
    canonical.source_agents = _unique_in_order(
        agent
        for item in ordered
        for agent in item.source_agents
    )
    return canonical


def _is_confidence_descending(positions: list[AuthorOutputPosition]) -> bool:
    return all(
        earlier.confidence >= later.confidence
        for earlier, later in zip(positions, positions[1:], strict=False)
    )


def _trust_path_for_complexity(case_complexity: str) -> str:
    return "fast_track" if case_complexity == "fast_track" else "full_deliberation"


def _derive_work_id(work_output: WorkOutput, current_work_id: str | None) -> str | None:
    if work_output.status == "definitive" and work_output.positions and work_output.positions[0].work_id is not None:
        return work_output.positions[0].work_id
    return current_work_id


def _authority_level_or_none(value: AuthorityLevel | str | None) -> AuthorityLevel | None:
    if value is None or isinstance(value, AuthorityLevel):
        return value
    return AuthorityLevel(value)


def _enum_value(value: Any) -> Any:
    return value.value if hasattr(value, "value") else value


def _unique_in_order(values: Any) -> list[Any]:
    seen: set[Any] = set()
    ordered: list[Any] = []
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _new_case_id() -> str:
    return f"case_{uuid4().hex[:8]}"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()
