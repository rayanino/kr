"""Source Engine Configuration — SPEC §8

Core parameters with defaults and valid ranges.
See SPEC §8 for the full parameter table.

Hardcoded (not configurable):
- SHA-256 hash algorithm
- source_id format (src_{8_char_hash})
- Trust tier names (verified, flagged, owner_override)
- Freeze-before-process invariant
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class SourceEngineConfig(BaseModel):
    """Configuration for the source engine."""

    staging_path: Path = Field(description="Root directory for staging sources.")
    library_root: Path = Field(
        default=Path("library"), description="Root directory for frozen library."
    )
    inference_timeout: float = Field(
        default=60.0, description="Timeout in seconds for LLM inference calls."
    )

    model_config = {"arbitrary_types_allowed": True}
