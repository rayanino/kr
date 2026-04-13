"""LLM Inference Output Models — Pydantic models for Instructor response_model.

These models match the §4.A.4 inference output schema EXACTLY. Instructor
uses them to parse and validate LLM JSON responses. The consensus module
passes them as the response_model type parameter.

IMPORTANT: These are INTERMEDIATE models — they represent the LLM's raw output.
They are NOT the same as SourceMetadata (the final output). metadata_inference.py
maps from these models to SourceMetadata fields, applying caps, resolving
scholar identity, and constructing the needs_review_fields list.

Field names here match the LLM output schema (inference_v1.py), which differs
from SourceMetadata in two places:
  - LLM "layers" → SourceMetadata "text_layers"
  - LLM "author_identification" → SourceMetadata "author" (ScholarReference)

WHY ENUM FIELDS ARE `str` NOT THE ACTUAL ENUM: Instructor parses the LLM's
raw JSON. If the LLM returns "منظومة" instead of "nazm", Pydantic enum
validation would reject it immediately. Using `str` lets the engine apply
synonym normalization first (§4.A.4 LLM response validation,
library/config/genre_synonyms.json), THEN validate against the enum.
The engine validates enums after synonym mapping, not during parsing.
"""

from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field


class AuthorIdentificationOutput(BaseModel):
    """Author identification from LLM output — used to construct ScholarReference."""
    canonical_name_ar: str
    known_as: list[str] = []
    death_date_hijri: Optional[int] = None
    school_affiliations: Optional[dict[str, Optional[str]]] = None
    sectarian_tradition: Optional[str] = None
    scholarly_standing: Optional[str] = None
    methodological_stance: Optional[str] = None


class LayerOutput(BaseModel):
    """A text layer from LLM output — maps to TextLayer in contracts.py."""
    layer_type: Literal["matn", "sharh", "hashiyah", "tahqiq_note"]
    author_name: str  # Arabic name — resolved to ScholarReference AFTER inference


class GenreChainOutput(BaseModel):
    """Genre chain from LLM output — maps to GenreChain in contracts.py."""
    relation_type: str  # "sharh_of", "hashiyah_on", etc.
    base_work_title: str
    base_work_author: str


class ScholarlyContextOutput(BaseModel):
    """Scholarly context from LLM output — maps to ScholarlyContext in contracts.py."""
    composition_period: Optional[str] = None
    composition_date_hijri: Optional[int] = None
    tradition_position: Optional[str] = None
    known_textual_issues: list[str] = []
    historical_significance: Optional[str] = None
    muhaqiq_reputation: Optional[str] = None
    tahqiq_methodology_note: Optional[str] = None
    edition_known_issues: list[str] = []
    context_richness: Literal["rich", "partial", "minimal"] = "minimal"
    uncertain_dimensions: list[str] = []


class InferenceOutput(BaseModel):
    """The Pydantic model Instructor parses LLM responses into.

    Matches SPEC §4.A.4 inference output schema.

    Usage:
        result = await client.create(
            messages=messages,
            response_model=InferenceOutput,
        )
    """

    # Genre
    genre: str  # Validated against Genre enum AFTER synonym mapping
    genre_confidence: float = Field(ge=0.0, le=1.0)
    genre_chain: Optional[GenreChainOutput] = None
    genre_chain_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)

    # Structure
    structural_format: str  # Validated against StructuralFormat enum after parsing
    structural_format_confidence: float = Field(ge=0.0, le=1.0)
    is_multi_layer: bool
    multi_layer_confidence: float = Field(ge=0.0, le=1.0)
    layers: Optional[list[LayerOutput]] = None

    # Classification
    science_scope: list[str]
    science_scope_confidence: float = Field(ge=0.0, le=1.0)
    level: Optional[str] = None  # Validated against WorkLevel enum after parsing
    level_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    authority_level: str  # Validated against AuthorityLevel enum after parsing
    authority_level_confidence: float = Field(ge=0.0, le=1.0)

    # Author
    author_identification: AuthorIdentificationOutput
    author_identification_confidence: float = Field(ge=0.0, le=1.0)
    attribution_status: str = "traditional"  # Default per §4.A.4: "default to traditional"
    attribution_notes: Optional[str] = None

    # Scholarly context — Optional because inference may fail on this section
    scholarly_context: Optional[ScholarlyContextOutput] = None
