"""LLM-Assisted Metadata Inference — SPEC §4.A.4

Fills metadata gaps, validates extracted data, enriches with scholarly context.
Uses multi-model consensus for author_id and work_id (SPEC §6).

Flow:
1. Build prompt_context from extracted metadata
2. Send through consensus evaluate() (2 models, single call)
3. Run three local comparisons on model responses
4. Validate enums with synonym fallback
5. Map InferenceOutput → SourceMetadata fields
6. Apply confidence caps
7. Set text_fidelity deterministically
8. Build needs_review_fields list
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from engines.source.contracts import (
    AttributionStatus,
    AuthorityLevel,
    Genre,
    HumanGateTrigger,
    InferredFieldConfidence,
    ScholarReference,
    SourceFormat,
    StructuralFormat,
    TextFidelity,
    TextLayer,
    WorkLevel,
)
from engines.source.prompts.inference_v1 import SYSTEM_MESSAGE, USER_MESSAGE_TEMPLATE
from engines.source.src.consensus import (
    check_work_agreement,
    compare_attribution_status,
    make_author_agreement_fn,
    select_canonical_result,
)
from engines.source.src.inference_models import InferenceOutput
from shared.consensus.src.consensus import ConsensusResult, evaluate
import shared.scholar_authority.src as scholar_authority

logger = logging.getLogger(__name__)

# ── Genre synonyms loaded at module level ──

_GENRE_SYNONYMS: dict[str, str] = {}
_SYNONYMS_PATH = Path("library/config/genre_synonyms.json")
if _SYNONYMS_PATH.exists():
    _GENRE_SYNONYMS = json.loads(_SYNONYMS_PATH.read_text(encoding="utf-8"))


@dataclass
class MetadataInferenceResult:
    """Result of LLM metadata inference.

    Attributes:
        consensus_agreed: Whether both models agreed.
        canonical_output: The selected InferenceOutput after consensus.
        work_agreed: Whether both models agreed on work identity.
        work_human_gate_trigger: Gate trigger reason from work comparison, or None.
        attribution_status: Resolved attribution status string.
        attribution_needs_gate: Whether attribution disagreement requires human review.
        genre: Validated genre string (enum value).
        structural_format: Validated structural_format string (enum value).
        authority_level: Validated authority_level string (enum value).
        level: Validated level string (enum value), or None.
        science_scope: List of science scope strings.
        is_multi_layer: Whether the source is multi-layer.
        text_layers: List of layer dicts ready for TextLayer construction.
        author_reference: Dict of author fields ready for ScholarReference construction.
        confidence_scores: Dict of field name → confidence float (post-caps).
        text_fidelity: Deterministic fidelity string based on source format.
        needs_review_fields: Sorted list of field names needing human review.
        needs_human_gate: Whether any gate has been triggered.
        human_gate_triggers: List of human gate trigger reason strings.
        raw_model_responses: Diagnostic-only list of model response summaries.
    """

    # From consensus
    consensus_agreed: bool = False
    canonical_output: Optional[InferenceOutput] = None

    # After local comparisons
    work_agreed: bool = False
    work_human_gate_trigger: Optional[str] = None
    attribution_status: str = "traditional"
    attribution_needs_gate: bool = False

    # Mapped fields (ready for SourceMetadata)
    genre: Optional[str] = None
    structural_format: Optional[str] = None
    authority_level: Optional[str] = None
    level: Optional[str] = None
    science_scope: list[str] = field(default_factory=list)
    is_multi_layer: bool = False
    text_layers: list[dict] = field(default_factory=list)
    author_reference: Optional[dict] = None  # Ready for ScholarReference construction
    death_date_source: Optional[str] = None  # extraction, author_raw_text, inference, absent
    death_date_single_model: bool = False  # True when only one model provided a death date

    # Confidence
    confidence_scores: Optional[dict] = None

    # Quality
    text_fidelity: str = "medium"
    needs_review_fields: list[str] = field(default_factory=list)
    needs_human_gate: bool = False
    human_gate_triggers: list[str] = field(default_factory=list)

    # Diagnostics
    raw_model_responses: list[dict] = field(default_factory=list)
    _full_consensus_result: Optional[Any] = None  # ConsensusResult for diagnostic capture


def build_prompt_context(extracted: dict[str, Any]) -> str:
    """Build the prompt context string from extracted metadata.

    Assembles a structured multi-line string from the extracted metadata dict.
    Only includes fields that are present and non-empty. The output matches
    the expected format of USER_MESSAGE_TEMPLATE's {prompt_context} placeholder.

    Args:
        extracted: Dict of metadata fields from a Shamela or plain text extractor.

    Returns:
        Multi-line string with one field per line, or empty string if nothing present.
    """
    lines: list[str] = []

    # Title — prefer display_title, fall back through alternatives
    title = (
        extracted.get("display_title")
        or extracted.get("title_full")
        or extracted.get("title_arabic", "")
    )
    if title:
        lines.append(f"Title: {title}")

    # Author
    author = extracted.get("author_name_raw") or extracted.get("author_name", "")
    if author:
        lines.append(f"Author: {author}")

    # Publisher
    publisher = extracted.get("publisher", "")
    if publisher:
        lines.append(f"Publisher: {publisher}")

    # Muhaqiq / editor — check actual field name from Shamela extraction
    muhaqiq = extracted.get("muhaqiq_name_raw") or extracted.get("muhaqiq_name") or extracted.get("muhaqiq", "")
    if muhaqiq:
        lines.append(f"Muhaqiq/Editor: {muhaqiq}")

    # Category (Shamela-specific)
    category = extracted.get("shamela_category") or extracted.get("category", "")
    if category:
        lines.append(f"Category: {category}")

    # Edition — check actual field name from Shamela extraction
    edition = extracted.get("edition_raw") or extracted.get("edition", "")
    if edition:
        lines.append(f"Edition: {edition}")

    # Compiler
    compiler = extracted.get("compiler_name_raw", "")
    if compiler:
        lines.append(f"Compiler: {compiler}")

    # Commentator
    commentator = extracted.get("commentator_name_raw", "")
    if commentator:
        lines.append(f"Commentator: {commentator}")

    # Riwayah / transmission
    riwayah = extracted.get("riwayah", "")
    if riwayah:
        lines.append(f"Riwayah/Transmission: {riwayah}")

    # Edition year
    edition_year_h = extracted.get("edition_year_hijri")
    edition_year_m = extracted.get("edition_year_miladi")
    if edition_year_h:
        lines.append(f"Edition year (Hijri): {edition_year_h}")
    if edition_year_m:
        lines.append(f"Edition year (Miladi): {edition_year_m}")

    # Page count
    page_count = extracted.get("page_count")
    if page_count:
        lines.append(f"Page count: {page_count}")

    # Volume info
    volume_count = extracted.get("volume_count")
    if volume_count:
        lines.append(f"Volume count: {volume_count}")

    # Source format
    source_format = extracted.get("source_format", "")
    if source_format:
        lines.append(f"Source format: {source_format}")

    return "\n".join(lines)


def validate_enum_value(
    value: str,
    enum_class: type,
    synonyms: dict[str, str],
    default: Optional[str],
) -> tuple[str, bool]:
    """Validate a string against an enum, with synonym fallback.

    Attempt order:
    1. Direct enum membership check.
    2. Synonym mapping — if the value maps to something, try that.
    3. Conservative default — if default is None and no match, returns (None, True).

    Args:
        value: The string to validate.
        enum_class: The Enum class to validate against.
        synonyms: Dict of synonym → canonical enum value strings.
        default: Default enum value string to use if no match found.
            Pass None for optional fields like ``level`` where None is a valid outcome.

    Returns:
        Tuple of (validated_value, was_fallback). was_fallback is True when a synonym
        or default was used instead of a direct match.
    """
    # Try direct enum match
    try:
        enum_class(value)
        return value, False
    except ValueError:
        pass

    # Try synonym mapping
    if value in synonyms:
        mapped = synonyms[value]
        try:
            enum_class(mapped)
            return mapped, True
        except ValueError:
            pass

    # Conservative default (may be None for optional fields)
    logger.warning(
        "Enum fallback: value '%s' not in %s and no synonym match — using default '%s'",
        value, enum_class.__name__, default,
    )
    return default, True  # type: ignore[return-value]


def apply_confidence_caps(
    output: InferenceOutput,
    attribution_status: str,
) -> dict[str, float | None]:
    """Apply confidence caps based on attribution status.

    SPEC §6 rule: single-LLM biographical inference is always capped at 0.85.
    Additional caps apply when attribution is disputed or unknown.

    Cap ladder (applied in order, each cap is cumulative if lower):
    - All attribution statuses: author_confidence <= 0.85 (biographical inference cap)
    - disputed:  author_confidence <= 0.70
    - unknown:   author_confidence = 0.0

    Non-author fields are returned at face value.

    Args:
        output: InferenceOutput with raw (uncapped) confidence scores.
        attribution_status: Resolved attribution status string from compare_attribution_status().

    Returns:
        Dict of field name → capped float confidence score.
    """
    author_conf = output.author_identification_confidence

    # Biographical inference cap — applies regardless of attribution status
    author_conf = min(author_conf, 0.85)

    # Attribution-based caps
    if attribution_status == AttributionStatus.DISPUTED.value:
        author_conf = min(author_conf, 0.70)
    elif attribution_status == AttributionStatus.UNKNOWN.value:
        author_conf = 0.0

    return {
        "genre": output.genre_confidence,
        "science_scope": output.science_scope_confidence,
        "level": output.level_confidence,
        "structural_format": output.structural_format_confidence,
        "authority_level": output.authority_level_confidence,
        "multi_layer": output.multi_layer_confidence,
        "genre_chain": output.genre_chain_confidence,
        "author": author_conf,
    }


def set_text_fidelity(source_format: SourceFormat) -> str:
    """Set text_fidelity deterministically based on source format.

    SPEC §4.A.4 rule: text_fidelity is NOT inferred by LLM — it is a
    deterministic property of the source format.

    Mapping:
    - SHAMELA_HTML → "high"  (structured digital text with consistent encoding)
    - All others   → "medium" (default; downgrade on quality issues later)

    Args:
        source_format: The detected SourceFormat enum value.

    Returns:
        One of "high", "medium" (TextFidelity enum values as strings).
    """
    if source_format == SourceFormat.SHAMELA_HTML:
        return TextFidelity.HIGH.value
    return TextFidelity.MEDIUM.value


def _determine_death_date_source(
    death_date: Optional[int],
    extracted: dict[str, Any],
) -> str:
    """Determine the provenance of a death date value.

    Returns one of: 'absent', 'author_raw_text', 'extraction', 'inference'.
    Checks extraction fields for the death date value before classifying as LLM inference.
    """
    if death_date is None:
        return "absent"

    date_str = str(death_date)

    # Check author_name_raw first (most common source: "السيوطي ت 911هـ")
    author_raw = extracted.get("author_name_raw")
    if author_raw and date_str in str(author_raw):
        return "author_raw_text"

    # Check other structured extraction fields
    for field in ("author_name", "shamela_category", "edition_raw", "publisher_raw"):
        val = extracted.get(field)
        if val is not None and date_str in str(val):
            return "extraction"

    return "inference"


def build_needs_review(
    confidence_scores: dict[str, float | None],
    extracted: dict[str, Any],
    threshold: float = 0.70,
) -> list[str]:
    """Build list of fields needing human review.

    A field needs review when:
    1. Its confidence score is below ``threshold`` (0.70 by default per SPEC §5 Layer 2).
    2. The "author" field: always needs review when no author_name_raw was extracted
       (meaning the author identity is entirely LLM-inferred).

    None confidence values (e.g. level=None for non-pedagogical works) are skipped.

    Args:
        confidence_scores: Dict of field name → float confidence (post-caps).
        extracted: Original extracted metadata dict.
        threshold: Confidence below this triggers review inclusion.

    Returns:
        Sorted list of field name strings.
    """
    needs_review: list[str] = []

    for field_name, score in confidence_scores.items():
        if score is not None and score < threshold:
            needs_review.append(field_name)

    # Author entirely LLM-inferred — no extracted anchor
    author_raw = extracted.get("author_name_raw") or extracted.get("author_name", "")
    if not author_raw:
        if "author" not in needs_review:
            needs_review.append("author")

    return sorted(needs_review)


async def infer_metadata(
    extracted: dict[str, Any],
    source_format: SourceFormat,
    staging_context: dict[str, Any] | None = None,
    *,
    registry_path: Path | None = None,
) -> MetadataInferenceResult:
    """Run LLM metadata inference with multi-model consensus.

    The full pipeline (SPEC §4.A.4):
    1. Build prompt context from extracted fields.
    2. Send messages through consensus evaluate() (two models, concurrent).
    3. Run three local comparisons: work agreement, attribution status comparison.
    4. Validate enum fields with synonym fallback.
    5. Map InferenceOutput fields to MetadataInferenceResult.
    6. Apply confidence caps (SPEC §6).
    7. Set text_fidelity deterministically from source_format.
    8. Build needs_review_fields list.

    When both models fail, returns an empty result with needs_human_gate=True.
    When consensus disagrees on author_identification, needs_human_gate=True.

    Args:
        extracted: Dict from Shamela/plain text extractor containing metadata fields.
        source_format: Detected source format (SourceFormat enum).
        staging_context: Optional supplementary context (volume info, file paths, etc.).

    Returns:
        MetadataInferenceResult with mapped fields, confidence scores, and diagnostics.
    """
    result = MetadataInferenceResult()

    # 1. Build prompt context
    prompt_context = build_prompt_context(extracted)

    # 2. Get text sample — truncated to 2000 chars to stay within prompt budget
    text_sample = extracted.get("text_sample", "")[:2000]

    # 3. Build full messages
    messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {
            "role": "user",
            "content": USER_MESSAGE_TEMPLATE.format(
                prompt_context=prompt_context,
                text_sample=text_sample,
            ),
        },
    ]

    # 4. Build simplified messages (strip library context markers if present)
    simplified_context = prompt_context.split("=== LIBRARY CONTEXT ===")[0].strip()
    simplified_messages = [
        {"role": "system", "content": SYSTEM_MESSAGE},
        {
            "role": "user",
            "content": USER_MESSAGE_TEMPLATE.format(
                prompt_context=simplified_context,
                text_sample=text_sample,
            ),
        },
    ]

    # 5. Single consensus call — author_identification task triggers fallback logic
    # Wrap scholar_authority.lookup to match make_author_agreement_fn's expected
    # Callable[[str], Optional[dict]] signature. The raw lookup returns
    # ScholarMatchResult (dataclass), not a dict.
    _registry_path = registry_path or Path("library/registries/scholars.json")

    def _scholar_lookup_adapter(name: str) -> Optional[dict]:
        result = scholar_authority.lookup(name, registry_path=_registry_path)
        if result.found and result.record is not None:
            return {
                "canonical_id": result.record.canonical_id,
                "canonical_name_ar": result.record.canonical_name_ar,
            }
        return None

    agreement_fn = make_author_agreement_fn(_scholar_lookup_adapter)
    consensus_result: ConsensusResult = await evaluate(
        task="author_identification",
        messages=messages,
        response_model=InferenceOutput,
        agreement_fn=agreement_fn,  # type: ignore[arg-type]  # InferenceOutput is BaseModel; variance is safe
        simplified_messages=simplified_messages,
    )

    result.consensus_agreed = consensus_result.agreed
    result.needs_human_gate = consensus_result.needs_human_gate

    if consensus_result.needs_human_gate and consensus_result.human_gate_trigger:
        result.human_gate_triggers.append(consensus_result.human_gate_trigger)

    # Store raw responses for diagnostics (no content — model IDs and status only)
    result.raw_model_responses = [
        {
            "model_id": r.model_id,
            "parse_success": r.parse_success,
            "error": r.error,
        }
        for r in consensus_result.model_responses
    ]
    result._full_consensus_result = consensus_result

    # 6. Get canonical output — bail early if both models failed
    successful = [r for r in consensus_result.model_responses if r.parse_success]
    if not successful:
        result.needs_human_gate = True
        if "consensus_disagreement" not in result.human_gate_triggers:
            result.human_gate_triggers.append("consensus_disagreement")
        return result

    if consensus_result.canonical_result is not None:
        canonical: InferenceOutput = consensus_result.canonical_result
    else:
        canonical = select_canonical_result(consensus_result.model_responses)

    result.canonical_output = canonical

    # 7. Three local comparisons on model responses (only meaningful with 2 successes)
    if len(successful) >= 2:
        resp_a_parsed: InferenceOutput = successful[0].parsed
        resp_b_parsed: InferenceOutput = successful[1].parsed

        # Work matching — SPEC §6.2
        work_agreed, work_trigger = check_work_agreement(resp_a_parsed, resp_b_parsed)
        result.work_agreed = work_agreed
        result.work_human_gate_trigger = work_trigger
        if work_trigger and work_trigger not in result.human_gate_triggers:
            result.human_gate_triggers.append(work_trigger)

        # Attribution status — SPEC §6.3
        attr_status, attr_gate = compare_attribution_status(
            resp_a_parsed.attribution_status,
            resp_b_parsed.attribution_status,
        )
        result.attribution_status = attr_status
        result.attribution_needs_gate = attr_gate
        if attr_gate:
            result.needs_human_gate = True
            if "consensus_disagreement" not in result.human_gate_triggers:
                result.human_gate_triggers.append("consensus_disagreement")
    else:
        # Single successful model — accept its attribution status at face value
        result.attribution_status = canonical.attribution_status

    # 8. Enum validation with synonym fallback
    genre_val, genre_fallback = validate_enum_value(
        canonical.genre, Genre, _GENRE_SYNONYMS, Genre.OTHER.value
    )
    result.genre = genre_val

    fmt_val, fmt_fallback = validate_enum_value(
        canonical.structural_format, StructuralFormat, {}, StructuralFormat.MIXED.value
    )
    result.structural_format = fmt_val

    auth_val, auth_fallback = validate_enum_value(
        canonical.authority_level,
        AuthorityLevel,
        {},
        AuthorityLevel.MODERN_COMPILATION.value,
    )
    result.authority_level = auth_val

    level_fallback = False
    if canonical.level is not None:
        level_val, level_fallback = validate_enum_value(
            canonical.level, WorkLevel, {}, None
        )
        result.level = level_val
    # level remains None when canonical.level is None (non-pedagogical works)

    result.science_scope = canonical.science_scope
    result.is_multi_layer = canonical.is_multi_layer

    # 9. Map layers — only populated when is_multi_layer is True
    if canonical.layers:
        result.text_layers = [
            {"layer_type": layer.layer_type, "author_name": layer.author_name}
            for layer in canonical.layers
        ]

    # 10. Map author identification fields
    author_id = canonical.author_identification
    result.author_reference = {
        "name_arabic": author_id.canonical_name_ar,
        "death_date_hijri": author_id.death_date_hijri,
        "known_as": author_id.known_as,
        "source_of_identification": (
            "consensus" if len(successful) >= 2 else "inferred"
        ),
    }

    # 10b. Determine death_date_source provenance
    result.death_date_source = _determine_death_date_source(
        author_id.death_date_hijri, extracted
    )

    # 10c. Flag single-model death dates (ERR-03 pattern)
    # When one model provides a death_date and the other says None,
    # the date is higher-risk for hallucination.
    if len(successful) >= 2:
        death_a = successful[0].parsed.author_identification.death_date_hijri
        death_b = successful[1].parsed.author_identification.death_date_hijri
        if (death_a is None) != (death_b is None):
            result.death_date_single_model = True
    else:
        # Single model = treat death date as unverified if inferred
        result.death_date_single_model = True

    # 11. Apply confidence caps — SPEC §6
    confidence = apply_confidence_caps(canonical, result.attribution_status)
    result.confidence_scores = confidence

    # 12. Set text_fidelity deterministically — NEVER from LLM
    result.text_fidelity = set_text_fidelity(source_format)

    # 13. Build needs_review_fields
    needs_review = build_needs_review(confidence, extracted)

    # Also flag fields where enum validation fell back to a default
    if genre_fallback and "genre" not in needs_review:
        needs_review.append("genre")
    if fmt_fallback and "structural_format" not in needs_review:
        needs_review.append("structural_format")
    if auth_fallback and "authority_level" not in needs_review:
        needs_review.append("authority_level")
    if level_fallback and "level" not in needs_review:
        needs_review.append("level")

    # Flag single-model inferred death dates for owner review (ERR-03)
    if result.death_date_single_model and result.death_date_source == "inference":
        if "death_date_hijri" not in needs_review:
            needs_review.append("death_date_hijri")

    result.needs_review_fields = sorted(needs_review)

    return result
