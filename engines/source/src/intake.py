"""Source engine intake — SPEC §4.A.2.

The main entry point for acquiring sources into the library.
Orchestrates: format detection → metadata extraction → freezing → registration.
"""

import json
from datetime import datetime, timezone
from pathlib import Path

from .format_detector import detect_format
from .freezer import freeze_source, FreezeError
from .identity import generate_source_id, generate_work_id, generate_human_label
from .registry import SourceRegistry, RegistryError
from .extractors.base import ExtractedMetadata, ExtractionError
from .extractors.pdf_extractor import PdfExtractor, ScannedPdfExtractor
from .extractors.text_extractor import TextExtractor


class IntakeError(Exception):
    """Raised when source intake fails."""
    def __init__(self, message: str, error_code: str = "SRC_INTAKE_FAILED"):
        self.error_code = error_code
        super().__init__(f"{error_code}: {message}")


# Map source formats to their extractors
_EXTRACTORS = {
    "pdf_text": PdfExtractor(),
    "pdf_scanned": ScannedPdfExtractor(),
    "plain_text": TextExtractor(),
    # Future: shamela_html, word_doc, image_scan, epub, owner_authored
}


def intake_source(
    source_path: str | Path,
    library_root: str | Path = "library",
    owner_hints: dict | None = None,
) -> dict:
    """Ingest a source into the library.

    This is the source engine's primary function. It implements the
    acquisition workflow from SPEC §4.A.2:
    1. Format detection
    2. Metadata extraction
    3. Duplicate detection
    4. Freezing
    5. Registration

    Args:
        source_path: Path to the source file or directory.
        library_root: Root of the library directory.
        owner_hints: Optional metadata hints from the owner
            (title, author, science_scope, etc.)

    Returns:
        Dict with source_id, work_id, and metadata_path.

    Raises:
        IntakeError: On any intake failure.
    """
    source_path = Path(source_path)
    library_root = Path(library_root)
    owner_hints = owner_hints or {}

    # Validate input
    if not source_path.exists():
        raise IntakeError(f"Source path does not exist: {source_path}", "SRC_EMPTY_INPUT")

    if source_path.is_file() and source_path.stat().st_size == 0:
        raise IntakeError(f"Source file is empty: {source_path}", "SRC_EMPTY_INPUT")

    # Step 1: Format detection
    try:
        source_format = detect_format(source_path)
    except ValueError as e:
        raise IntakeError(str(e), "SRC_UNSUPPORTED_FORMAT") from e

    # Step 2: Freeze first (we need the hash for source_id)
    # Use a temporary location, then rename after we know the source_id
    staging_dir = library_root / "staging" / f"_intake_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    try:
        composite_hash, file_hashes = freeze_source(source_path, staging_dir)
    except FreezeError as e:
        raise IntakeError(str(e), "SRC_FREEZE_FAILED") from e

    # Generate source_id from hash
    source_id = generate_source_id(composite_hash)

    # Step 3: Duplicate detection
    registry_path = library_root / "registries" / "sources.json"
    registry = SourceRegistry(registry_path)

    existing = registry.find_by_hash(composite_hash)
    if existing is not None:
        # Clean up staging
        _cleanup_dir(staging_dir)
        raise IntakeError(
            f"Exact duplicate of existing source {existing}",
            "SRC_DUPLICATE_EXACT",
        )

    # Move frozen files to permanent location
    frozen_dir = library_root / "sources" / source_id / "frozen"
    frozen_dir.mkdir(parents=True, exist_ok=True)

    import shutil
    for f in staging_dir.iterdir():
        dest = frozen_dir / f.name
        shutil.move(str(f), str(dest))
        # Re-apply read-only after move
        import os
        os.chmod(dest, 0o444)

    _cleanup_dir(staging_dir)

    # Step 4: Metadata extraction
    extractor = _EXTRACTORS.get(source_format)
    if extractor is not None:
        try:
            extracted = extractor.extract(list(frozen_dir.iterdir())[0] if source_path.is_file() else frozen_dir)
        except ExtractionError:
            extracted = ExtractedMetadata()
    else:
        extracted = ExtractedMetadata()

    # Apply owner hints (override extracted metadata)
    if owner_hints.get("title"):
        extracted.title_arabic = owner_hints["title"]
    if owner_hints.get("author"):
        extracted.author_name_arabic = owner_hints["author"]

    # Generate work_id
    title = extracted.title_arabic or source_path.stem
    author = extracted.author_name_arabic or "unknown"
    work_id = generate_work_id(author, title)
    human_label = generate_human_label(title)

    # Step 5: Build metadata record
    now = datetime.now(timezone.utc).isoformat()
    metadata = _build_metadata(
        source_id=source_id,
        work_id=work_id,
        human_label=human_label,
        source_format=source_format,
        extracted=extracted,
        composite_hash=composite_hash,
        file_hashes=file_hashes,
        frozen_dir=str(frozen_dir),
        intake_timestamp=now,
    )

    # Write metadata.json
    metadata_path = library_root / "sources" / source_id / "metadata.json"
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    # Step 6: Register
    try:
        registry.register(
            source_id=source_id,
            work_id=work_id,
            title_arabic=metadata["title_arabic"],
            author_canonical_id=metadata["author"]["canonical_id"],
            trust_tier=metadata["trust_tier"],
            frozen_hash=composite_hash,
            acquisition_path="manual",
        )
    except RegistryError as e:
        raise IntakeError(str(e), "SRC_REGISTRY_CONFLICT") from e

    return {
        "source_id": source_id,
        "work_id": work_id,
        "metadata_path": str(metadata_path),
        "frozen_dir": str(frozen_dir),
        "source_format": source_format,
    }


def _build_metadata(
    source_id: str,
    work_id: str,
    human_label: str,
    source_format: str,
    extracted: ExtractedMetadata,
    composite_hash: str,
    file_hashes: dict[str, str],
    frozen_dir: str,
    intake_timestamp: str,
) -> dict:
    """Build the full SourceMetadata dict.

    Fields that require LLM inference are set to placeholder values
    with needs_review flags. The enrichment step fills these later.
    """
    return {
        # Identity
        "source_id": source_id,
        "work_id": work_id,
        "human_label": human_label,

        # Bibliographic
        "title_arabic": extracted.title_arabic or "عنوان غير معروف",  # Unknown title
        "title_transliterated": None,
        "author": {
            "canonical_id": "sch_unresolved",
            "name_arabic": extracted.author_name_arabic or "مؤلف غير معروف",  # Unknown author
            "confidence": 0.0 if not extracted.author_name_arabic else 0.5,
            "source_of_identification": "extracted" if extracted.author_name_arabic else "unknown",
        },
        "additional_authors": [],
        "science_scope": [],  # Needs LLM inference
        "genre": "unknown",  # Needs LLM inference
        "genre_chain": None,
        "level": None,  # Needs LLM inference

        # Source characteristics
        "source_format": source_format,
        "authority_level": "primary",  # Default; needs LLM inference
        "structural_format": "prose",  # Default; needs LLM inference
        "language": "ar",

        # Multi-layer
        "is_multi_layer": False,  # Default; needs LLM inference
        "text_layers": [],

        # Edition and trust
        "muhaqiq": extracted.muhaqiq,
        "publisher": extracted.publisher,
        "edition_number": extracted.edition_number,
        "publication_year_hijri": None,
        "publication_year_miladi": extracted.publication_year,
        "trust_tier": "flagged",
        "trust_score": 0.0,
        "trust_factors": [],
        "trust_reason": "Trust evaluation not yet implemented — all new sources default to flagged",

        # Text quality
        "text_fidelity": _default_fidelity(source_format),
        "text_fidelity_reason": f"Default fidelity for {source_format}",

        # Volumes
        "volume_count": extracted.volume_count,
        "volumes": [],
        "volumes_missing": [],

        # Frozen source
        "frozen_path": frozen_dir,
        "frozen_hash": composite_hash,
        "frozen_file_hashes": file_hashes,

        # Work relationships
        "work_relationships": [],

        # Processing state
        "status": "acquired",
        "intake_timestamp": intake_timestamp,
        "acquisition_path": "manual",

        # Progressive enrichment
        "metadata_history": [],
        "enrichment_sources": [],

        # Owner-authored
        "owner_authored_type": None,

        # Review flags
        "_needs_review": [
            "science_scope", "genre", "authority_level",
            "structural_format", "is_multi_layer", "trust_evaluation",
        ],
    }


def _default_fidelity(source_format: str) -> float:
    """Default text fidelity score by format (SPEC §4.A.4)."""
    fidelity_map = {
        "shamela_html": 0.90,
        "pdf_text": 0.85,
        "pdf_scanned": 0.50,
        "image_scan": 0.30,
        "plain_text": 0.80,
        "epub": 0.85,
        "word_doc": 0.85,
        "owner_authored": 1.0,
    }
    return fidelity_map.get(source_format, 0.50)


def _cleanup_dir(dirpath: Path) -> None:
    """Remove a directory and its contents."""
    import shutil
    try:
        # Need to make files writable before removal
        import os
        for f in dirpath.iterdir():
            os.chmod(f, 0o644)
        shutil.rmtree(dirpath)
    except Exception:
        pass  # Best effort cleanup
