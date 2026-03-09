"""Source Engine Configuration — SPEC §8

Loads all configuration from library/config/:
- recognized_muhaqiqs.json: list of recognized tahqiq editor names
- known_publishers.json: publisher name → {score, variants}
- transliteration.json: Arabic → Latin slug mapping tables
- genre_synonyms.json: non-standard genre values → Genre enum values

Also provides typed access to core parameters (§8):
- confidence thresholds (auto_accept: 0.70, block: 0.50)
- trust evaluation threshold (0.65)
- consensus configuration (models, fallback)
- staging/enrichment timeouts
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class SourceEngineConfig:
    """Typed configuration for the source engine.
    
    All fields have defaults matching SPEC §8.
    Config files override defaults when loaded.
    """
    # Paths
    library_root: Path = Path("library")
    staging_path: Path = Path("library/staging")
    
    # Confidence thresholds (§8)
    confidence_threshold_auto_accept: float = 0.70
    confidence_threshold_block: float = 0.50
    
    # Trust evaluation (§8)
    trust_score_verified_threshold: float = 0.65
    
    # Timeouts (§8)
    staging_lock_timeout: int = 3600  # seconds
    enrichment_cycle_timeout: int = 3600  # seconds
    human_gate_batch_size: int = 20  # max pending before alert
    
    # Loaded config data
    recognized_muhaqiqs: list[str] = field(default_factory=list)
    known_publishers: dict[str, dict] = field(default_factory=dict)
    transliteration: dict[str, dict[str, str]] = field(default_factory=dict)
    genre_synonyms: dict[str, str] = field(default_factory=dict)


def load_config(
    library_root: Path = Path("library"),
) -> SourceEngineConfig:
    """Load all configuration files and return a typed config object.
    
    SPEC §8: Config files are in library/config/.
    Missing files produce empty defaults (not errors).
    Malformed JSON files raise with clear error messages.
    """
    raise NotImplementedError
