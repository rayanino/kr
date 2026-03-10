"""Source Engine — محرك المصادر

Orchestrates the 13-step acquisition workflow (SPEC §4.A.2):
1. Config + Logger init → 2. stage_source → 3. extract_metadata →
4. infer_metadata → 5. check_exact_duplicate → 6. Register author →
7. Register muhaqiq → 8. freeze_source → 9. Assemble SourceMetadata →
10. evaluate_trust → 11. validate → 12. register_source → 13. Cleanup

Entry point: acquire_source(source_path, config) → SourceMetadata
Sync wrapper: acquire_source_sync(source_path, config) → SourceMetadata
Batch: acquire_batch(source_paths, config) → list[tuple[Path, SourceMetadata | SourceError]]
Startup: startup_cleanup(config) → list[str]
"""

from __future__ import annotations

import asyncio
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from engines.source.contracts import (
    AcquisitionPath,
    AttributionStatus,
    AuthorityLevel,
    ErrorCode,
    ErrorSeverity,
    Genre,
    GenreChain,
    GenreRelationType,
    InferredFieldConfidence,
    ProcessingStatus,
    ScholarlyContext,
    ScholarReference,
    SourceError,
    SourceFormat,
    SourceMetadata,
    StructuralFormat,
    TextFidelity,
    TextLayer,
    TrustTier,
    VolumeInfo,
    WorkLevel,
)
from engines.source.src.config import SourceEngineConfig, load_config
from engines.source.src.deduplication import check_exact_duplicate
from engines.source.src.exceptions import SourceEngineError, make_error
from engines.source.src.extractors import extract_metadata
from engines.source.src.freezer import freeze_source
from engines.source.src.human_gate import (
    gate_author_science_mismatch,
    gate_consensus_disagreement,
    gate_low_confidence,
    gate_trust_flagged,
)
from engines.source.src.logger import SourceEngineLogger
from engines.source.src.metadata_inference import MetadataInferenceResult, infer_metadata
from engines.source.src.registries import (
    check_orphaned_registrations,
    register_source,
)
from engines.source.src.registries import source_registry
from engines.source.src.registries import work_registry_store
from engines.source.src.registries.scholar_registry import (
    lookup_or_register_author,
    lookup_or_register_muhaqiq,
)
from engines.source.src.staging import (
    cleanup_orphaned_locks,
    remove_staging_lock,
    stage_source,
)
from engines.source.src.text_utils import generate_human_label, generate_work_id
from engines.source.src.trust_evaluator import evaluate_trust
from engines.source.src.validation import validate_source_metadata
from shared.scholar_authority.src.scholar_authority import get_all as get_all_scholars


# ──────────────────────────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────────────────────────


def _safe_remove_lock(lock_path: Path | None) -> None:
    """Remove staging lock if it exists. Never raises."""
    if lock_path is None:
        return
    try:
        remove_staging_lock(lock_path)
    except Exception:
        pass


def _compute_fidelity(
    source_format: SourceFormat,
    extracted: dict[str, Any],
) -> tuple[str, str]:
    """Determine TextFidelity from source format + quality issues."""
    if source_format == SourceFormat.SHAMELA_HTML:
        fidelity = TextFidelity.HIGH.value
        reason = "Shamela structured HTML text"
    elif source_format == SourceFormat.PLAIN_TEXT:
        fidelity = TextFidelity.MEDIUM.value
        reason = "Plain text file"
    elif source_format == SourceFormat.PDF_TEXT:
        fidelity = TextFidelity.HIGH.value
        reason = "Text-embedded PDF"
    elif source_format == SourceFormat.PDF_SCANNED:
        fidelity = TextFidelity.MEDIUM.value
        reason = "Scanned PDF"
    elif source_format == SourceFormat.IMAGE_SCAN:
        fidelity = TextFidelity.LOW.value
        reason = "Image scan"
    else:
        fidelity = TextFidelity.UNKNOWN.value
        reason = f"Unknown format: {source_format.value}"

    # Check for quality issues in extracted data (key uses underscore prefix)
    quality_issues = extracted.get("_quality_issues", [])
    for issue in quality_issues:
        check = issue.get("check", "") if isinstance(issue, dict) else str(issue)
        detail = issue.get("detail", check) if isinstance(issue, dict) else str(issue)

        if check == "page_count_mismatch":
            if fidelity == TextFidelity.HIGH.value:
                fidelity = TextFidelity.MEDIUM.value
            reason += f"; page count mismatch: {detail}"
        elif check == "encoding_suspect":
            fidelity = TextFidelity.LOW.value
            reason += f"; encoding suspect: {detail}"
        elif check == "high_empty_ratio":
            if fidelity == TextFidelity.HIGH.value:
                fidelity = TextFidelity.MEDIUM.value
            reason += f"; high empty ratio: {detail}"
        elif check == "content_minimal":
            reason += f"; minimal content: {detail}"

    return fidelity, reason


def _build_confidence_scores(inference: MetadataInferenceResult) -> InferredFieldConfidence:
    """Build InferredFieldConfidence from inference result."""
    scores = inference.confidence_scores or {}
    return InferredFieldConfidence(
        genre=scores.get("genre", 0.5),
        science_scope=scores.get("science_scope", 0.5),
        level=scores.get("level"),
        structural_format=scores.get("structural_format", 0.5),
        authority_level=scores.get("authority_level", 0.5),
        multi_layer=scores.get("multi_layer"),
        genre_chain=scores.get("genre_chain"),
    )


def _build_scholarly_context(inference: MetadataInferenceResult) -> ScholarlyContext | None:
    """Build ScholarlyContext from inference canonical output."""
    if inference.canonical_output is None:
        return None
    sc = inference.canonical_output.scholarly_context
    if sc is None:
        return None
    return ScholarlyContext(**sc.model_dump())


def _build_genre_chain(inference: MetadataInferenceResult) -> GenreChain | None:
    """Build GenreChain from inference canonical output."""
    if inference.canonical_output is None:
        return None
    gc = inference.canonical_output.genre_chain
    if gc is None:
        return None
    # Validate relation_type against enum
    try:
        relation_type = GenreRelationType(gc.relation_type)
    except ValueError:
        return None

    return GenreChain(
        relation_type=relation_type,
        base_work_title=gc.base_work_title,
        base_work_author=gc.base_work_author,
        confidence=inference.confidence_scores.get("genre_chain", 0.5)
        if inference.confidence_scores
        else 0.5,
    )


def _build_text_layers(
    inference: MetadataInferenceResult,
    source_id: str,
    config: SourceEngineConfig,
) -> list[TextLayer]:
    """Build TextLayer list from inference, registering each layer author."""
    layers: list[TextLayer] = []
    registry_path = config.library_root / "registries" / "scholars.json"

    for layer_dict in inference.text_layers:
        author_name = layer_dict.get("author_name", "")
        layer_type = layer_dict.get("layer_type", "matn")

        if author_name:
            ref = lookup_or_register_muhaqiq(
                author_name,
                source_id,
                registry_path=registry_path,
            )
        else:
            ref = lookup_or_register_muhaqiq(
                "مجهول",
                source_id,
                registry_path=registry_path,
            )

        layers.append(TextLayer(layer_type=layer_type, author=ref))

    return layers


def _build_needs_review(
    confidence_scores: InferredFieldConfidence,
    threshold: float = 0.70,
) -> list[str]:
    """Build list of fields needing review (confidence < threshold)."""
    fields: list[str] = []
    for field_name in ["genre", "science_scope", "structural_format", "authority_level"]:
        score = getattr(confidence_scores, field_name, None)
        if score is not None and score < threshold:
            fields.append(field_name)

    if confidence_scores.level is not None and confidence_scores.level < threshold:
        fields.append("level")
    if confidence_scores.multi_layer is not None and confidence_scores.multi_layer < threshold:
        fields.append("multi_layer")
    if confidence_scores.genre_chain is not None and confidence_scores.genre_chain < threshold:
        fields.append("genre_chain")

    return sorted(fields)


# ──────────────────────────────────────────────────────────────────
# Main Pipeline
# ──────────────────────────────────────────────────────────────────


async def acquire_source(
    source_path: Path,
    config: SourceEngineConfig | None = None,
) -> SourceMetadata:
    """Acquire a single source through the 13-step pipeline.

    Args:
        source_path: Path to source file or directory in staging area.
        config: Engine configuration. If None, loads defaults.

    Returns:
        Complete SourceMetadata record.

    Raises:
        SourceEngineError: On any pipeline failure.
    """
    # ── Step 1: Config + Logger ──
    if config is None:
        config = load_config()

    logger = SourceEngineLogger(config.library_root / "logs" / "source_engine.jsonl")
    lock_path: Path | None = None
    source_id: str | None = None

    try:
        # ── Step 2: Stage source ──
        logger.log_event("intake_start", None, f"Starting intake: {source_path}")

        src_reg = source_registry.load(
            registry_path=config.library_root / "registries" / "sources.json"
        )
        existing_ids = set(src_reg.keys())

        staging_result = stage_source(source_path, config, existing_ids)
        source_id = staging_result.source_id
        lock_path = staging_result.lock_path

        logger.log_event(
            "staging_complete", source_id,
            f"Format: {staging_result.source_format.value}, files: {len(staging_result.file_hashes)}",
        )

        try:
            # ── Step 3: Extract metadata ──
            extracted = extract_metadata(
                staging_result.source_path,
                staging_result.source_format,
            )
            logger.log_event("extraction_complete", source_id, "Metadata extracted")

            # ── Step 4: Infer metadata (async) ──
            inference = await infer_metadata(
                extracted,
                staging_result.source_format,
                registry_path=config.library_root / "registries" / "scholars.json",
            )
            logger.log_event("inference_complete", source_id, f"Consensus agreed: {inference.consensus_agreed}")

            # ── Step 5: Check exact duplicate ──
            src_reg_fresh = source_registry.load(
                registry_path=config.library_root / "registries" / "sources.json"
            )
            dup_source_id = check_exact_duplicate(staging_result.composite_hash, src_reg_fresh)
            if dup_source_id is not None:
                raise make_error(
                    ErrorCode.DUPLICATE_EXACT,
                    f"Exact duplicate of {dup_source_id}",
                    severity=ErrorSeverity.INFO,
                    source_id=source_id,
                    recovery_action="skipped",
                    context={"duplicate_of": dup_source_id},
                )

            # ── Step 6: Register author ──
            registry_path = config.library_root / "registries" / "scholars.json"
            author_name = ""
            death_date_hijri = None
            school = None

            if inference.author_reference:
                author_name = inference.author_reference.get("name_arabic", "")
                death_date_hijri = inference.author_reference.get("death_date_hijri")

            if not author_name:
                author_name = extracted.get("author_name_raw") or extracted.get("author_name", "مجهول")

            # Extract school from canonical output
            if (
                inference.canonical_output
                and inference.canonical_output.author_identification.school_affiliations
            ):
                schools = inference.canonical_output.author_identification.school_affiliations
                # school_affiliations is {science: school_name}, we want a school name
                school = next((v for v in schools.values() if v), None)

            author_ref, author_gate_id = lookup_or_register_author(
                author_name,
                death_date_hijri,
                school,
                source_id,
                registry_path=registry_path,
            )
            human_gates: list[str] = []
            if author_gate_id:
                human_gates.append(author_gate_id)

            logger.log_event("author_registered", source_id, f"Author: {author_ref.canonical_id}")

            # ── Step 7: Register muhaqiq ──
            muhaqiq_ref: ScholarReference | None = None
            muhaqiq_name = extracted.get("muhaqiq_name_clean") or extracted.get("muhaqiq_name_raw") or extracted.get("muhaqiq_name")
            if muhaqiq_name:
                muhaqiq_ref = lookup_or_register_muhaqiq(
                    muhaqiq_name,
                    source_id,
                    registry_path=registry_path,
                )
                logger.log_event("muhaqiq_registered", source_id, f"Muhaqiq: {muhaqiq_ref.canonical_id}")

            # ── Step 8: Freeze source ──
            freeze_result = freeze_source(
                staging_result.source_path,
                source_id,
                config.library_root,
                staging_result.file_hashes,
                staging_result.file_timestamps,
            )
            logger.log_event("freeze_complete", source_id, f"Frozen {freeze_result.file_count} files")

            # ── Step 9: Assemble SourceMetadata ──
            title_arabic = (
                extracted.get("title_full")
                or extracted.get("display_title")
                or extracted.get("title_arabic")
                or ""
            )
            work_id = generate_work_id(author_ref.name_arabic, title_arabic, config.transliteration)
            human_label = generate_human_label(title_arabic, config.transliteration)
            text_fidelity, text_fidelity_reason = _compute_fidelity(
                staging_result.source_format, extracted,
            )

            confidence_scores = _build_confidence_scores(inference)
            needs_review_fields = _build_needs_review(confidence_scores)
            scholarly_context = _build_scholarly_context(inference)
            genre_chain = _build_genre_chain(inference)
            text_layers = _build_text_layers(inference, source_id, config)

            # Resolve enums safely
            genre_val = inference.genre or "other"
            try:
                genre = Genre(genre_val)
            except ValueError:
                genre = Genre.OTHER

            structural_format_val = inference.structural_format or "prose"
            try:
                structural_format = StructuralFormat(structural_format_val)
            except ValueError:
                structural_format = StructuralFormat.PROSE

            authority_level_val = inference.authority_level or "modern_compilation"
            try:
                authority_level = AuthorityLevel(authority_level_val)
            except ValueError:
                authority_level = AuthorityLevel.MODERN_COMPILATION

            level = None
            if inference.level:
                try:
                    level = WorkLevel(inference.level)
                except ValueError:
                    level = None

            attribution_status_val = inference.attribution_status or "traditional"
            try:
                attribution_status = AttributionStatus(attribution_status_val)
            except ValueError:
                attribution_status = AttributionStatus.TRADITIONAL

            volumes: list[VolumeInfo] = []
            for v in extracted.get("volumes", []):
                if isinstance(v, dict):
                    volumes.append(VolumeInfo(**v))

            # Check work-level duplicate (info only, don't abort)
            work_reg = work_registry_store.load(
                registry_path=config.library_root / "registries" / "works.json"
            )
            if work_id in work_reg:
                logger.log_event(
                    "work_duplicate", source_id,
                    f"Work {work_id} already exists — acquiring as additional edition",
                )

            now_iso = datetime.now(timezone.utc).isoformat()

            metadata = SourceMetadata(
                source_id=source_id,
                work_id=work_id,
                human_label=human_label,
                title_arabic=title_arabic,
                title_transliterated=None,
                author=author_ref,
                attribution_status=attribution_status,
                attribution_notes=inference.canonical_output.attribution_notes
                if inference.canonical_output
                else None,
                muhaqiq=muhaqiq_ref,
                science_scope=inference.science_scope,
                genre=genre,
                genre_chain=genre_chain,
                level=level,
                publisher=extracted.get("publisher"),
                edition_number=extracted.get("edition_number"),
                publication_year_hijri=extracted.get("edition_year_hijri"),
                publication_year_miladi=extracted.get("edition_year_miladi"),
                source_format=staging_result.source_format,
                authority_level=authority_level,
                structural_format=structural_format,
                page_count=extracted.get("page_count"),
                is_multi_layer=inference.is_multi_layer,
                text_layers=text_layers,
                trust_tier=TrustTier.FLAGGED,  # Placeholder — updated in Step 10
                trust_score=0.0,
                trust_factors=[],
                trust_reason="",
                text_fidelity=TextFidelity(text_fidelity),
                text_fidelity_reason=text_fidelity_reason,
                confidence_scores=confidence_scores,
                needs_review_fields=needs_review_fields,
                volume_count=extracted.get("volume_count"),
                volumes=volumes,
                frozen_path=str(freeze_result.frozen_path),
                frozen_hash=freeze_result.frozen_hash,
                frozen_file_hashes=freeze_result.frozen_file_hashes,
                format_specific_metadata=extracted.get("format_specific_metadata", {}),
                scholarly_context=scholarly_context,
                status=ProcessingStatus.ACQUIRED,
                intake_timestamp=now_iso,
                acquisition_path=AcquisitionPath.MANUAL,
            )

            # ── Step 10: Evaluate trust ──
            all_scholars = get_all_scholars(
                registry_path=config.library_root / "registries" / "scholars.json"
            )
            author_record = all_scholars.get(author_ref.canonical_id)

            trust_tier, trust_score, trust_factors, trust_reason = evaluate_trust(
                author_ref,
                author_record,
                muhaqiq_name,
                extracted.get("publisher"),
                authority_level,
                TextFidelity(text_fidelity),
                source_id,
                recognized_muhaqiqs=config.recognized_muhaqiqs,
                known_publishers=config.known_publishers,
            )

            metadata.trust_tier = trust_tier
            metadata.trust_score = trust_score
            metadata.trust_factors = trust_factors
            metadata.trust_reason = trust_reason

            # Create human gates for flagged conditions
            if inference.needs_human_gate:
                model_ids = [
                    r.get("model_id", "unknown")
                    for r in inference.raw_model_responses
                ]
                model_a = model_ids[0] if len(model_ids) > 0 else "model_a"
                model_b = model_ids[1] if len(model_ids) > 1 else "model_b"
                for trigger in inference.human_gate_triggers:
                    if "consensus" in trigger.lower():
                        gate_consensus_disagreement(
                            source_id,
                            trigger,  # actual trigger reason, not generic "inference"
                            "disagreed",
                            "disagreed",
                            model_a,
                            model_b,
                        )

            # Low confidence gates
            if confidence_scores.genre < config.confidence_threshold_block:
                gate_low_confidence(source_id, "genre", genre.value, confidence_scores.genre)

            # Trust flagged gate
            if trust_tier == TrustTier.FLAGGED:
                gate_trust_flagged(
                    source_id, trust_score,
                    [f.model_dump(mode="json") for f in trust_factors],
                )

            logger.log_event("trust_evaluated", source_id, f"Trust: {trust_tier.value} ({trust_score:.3f})")

            # ── Step 11: Validate ──
            # Pre-populate registries with the entries that will be created in Step 12,
            # so referential integrity checks pass (work_id and author canonical_id
            # must exist in their respective registries).
            validation_works = dict(work_reg)
            if work_id not in validation_works:
                validation_works[work_id] = {
                    "work_id": work_id,
                    "canonical_title": title_arabic,
                    "author_canonical_id": author_ref.canonical_id,
                    "status": "active",
                }

            registries = {
                "scholars": {
                    cid: rec.model_dump(mode="json") for cid, rec in all_scholars.items()
                },
                "works": validation_works,
            }
            data_for_validation = metadata.model_dump(mode="json")
            validation_errors = validate_source_metadata(
                data_for_validation,
                registries=registries,
            )

            # Apply auto-corrections from validation back to metadata
            # (Checks 5e and 6b may auto-correct is_multi_layer in the dict)
            if data_for_validation.get("is_multi_layer") != metadata.is_multi_layer:
                metadata.is_multi_layer = data_for_validation["is_multi_layer"]

            fatal_errors = [e for e in validation_errors if e.severity == "fatal"]
            if fatal_errors:
                raise make_error(
                    ErrorCode.SCHEMA_VIOLATION,
                    f"Validation failed: {fatal_errors[0].message}",
                    source_id=source_id,
                    context={"errors": [e.message for e in fatal_errors]},
                )

            # Process gate-severity errors — create checkpoints then abort
            gate_errors = [e for e in validation_errors if e.severity == "gate"]
            if gate_errors:
                for gate_error in gate_errors:
                    if gate_error.check == "confidence_threshold":
                        gate_low_confidence(
                            source_id,
                            gate_error.field,
                            data_for_validation.get(gate_error.field, ""),
                            0.0,
                        )
                    elif gate_error.check == "consistency_author_science":
                        gate_author_science_mismatch(
                            source_id,
                            author_sciences=[],
                            source_sciences=[],
                            detail=gate_error.message,
                        )
                    elif gate_error.check == "multi_layer_empty_layers":
                        gate_low_confidence(
                            source_id,
                            "text_layers",
                            "[]",
                            0.0,
                        )
                raise make_error(
                    ErrorCode.LOW_CONFIDENCE,
                    f"Validation gate: {len(gate_errors)} issue(s) require human review",
                    source_id=source_id,
                    context={"gate_errors": [e.message for e in gate_errors]},
                )

            logger.log_event("validation_complete", source_id, f"Errors: {len(validation_errors)}")

            # ── Step 12: Register source ──
            register_source(
                metadata,
                library_root=config.library_root,
                config=config,
            )
            logger.log_event("registration_complete", source_id, "Registered in all registries")

            # ── Step 13: Cleanup ──
            processed_dir = config.staging_path / ".processed"
            processed_dir.mkdir(parents=True, exist_ok=True)
            try:
                shutil.move(str(staging_result.source_path), str(processed_dir / source_id))
            except Exception:
                pass  # Non-fatal if move fails

            _safe_remove_lock(lock_path)
            lock_path = None  # Prevent double-remove in finally

            logger.log_event("intake_success", source_id, "Source acquired successfully")

            return metadata

        except SourceEngineError:
            raise
        except Exception as exc:
            raise make_error(
                ErrorCode.INTERNAL_ERROR,
                f"Unexpected error during acquisition: {exc}",
                source_id=source_id,
            ) from exc

    except SourceEngineError as exc:
        if source_id:
            exc.error.source_id = source_id
        logger.log_error(exc.error)
        raise

    finally:
        _safe_remove_lock(lock_path)


def acquire_source_sync(
    source_path: Path,
    config: SourceEngineConfig | None = None,
) -> SourceMetadata:
    """Synchronous wrapper around acquire_source."""
    return asyncio.run(acquire_source(source_path, config))


def startup_cleanup(config: SourceEngineConfig | None = None) -> list[str]:
    """Clean up orphaned locks and interrupted registrations on startup.

    Returns list of messages describing what was cleaned.
    """
    if config is None:
        config = load_config()

    messages: list[str] = []

    # Clean orphaned locks
    removed_locks = cleanup_orphaned_locks(
        config.staging_path,
        timeout_seconds=config.staging_lock_timeout,
    )
    for lock in removed_locks:
        messages.append(f"Removed orphaned lock: {lock}")

    # Recover interrupted registrations
    recovered = check_orphaned_registrations(library_root=config.library_root)
    for source_id in recovered:
        messages.append(f"Recovered orphaned registration: {source_id}")

    return messages


async def acquire_batch(
    source_paths: list[Path],
    config: SourceEngineConfig | None = None,
) -> list[tuple[Path, SourceMetadata | SourceError]]:
    """Acquire multiple sources sequentially. Each source is independent.

    Returns list of (path, result) tuples. Result is SourceMetadata on
    success, SourceError on failure.
    """
    if config is None:
        config = load_config()

    results: list[tuple[Path, SourceMetadata | SourceError]] = []

    for path in source_paths:
        try:
            metadata = await acquire_source(path, config)
            results.append((path, metadata))
        except SourceEngineError as exc:
            results.append((path, exc.error))

    return results
