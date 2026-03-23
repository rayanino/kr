"""Pipeline Orchestrator: Phase 1 → Phase 2 → Phase 3 (SPEC §1.2).

Processes one source at a time. Loads config with cascade:
defaults → engine config.yaml → per-source overrides (§8.3).
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from engines.excerpting.contracts import (
    AssembledChunk,
    ExcerptRecord,
    ExcerptingConfig,
)
from engines.normalization.contracts import NormalizedPackage

logger = logging.getLogger(__name__)


def load_config(
    source_id: Optional[str] = None,
    engine_config_path: Optional[Path] = None,
) -> ExcerptingConfig:
    """Load configuration with cascade (§8.3).

    1. Built-in defaults (ExcerptingConfig field defaults).
    2. Engine config file (engines/excerpting/config.yaml).
    3. Per-source overrides (library/sources/{source_id}/excerpting_config.yaml).
    """
    raise NotImplementedError


def process_source(
    package: NormalizedPackage,
    config: Optional[ExcerptingConfig] = None,
    output_dir: Optional[Path] = None,
) -> tuple[list[ExcerptRecord], list[dict], dict]:
    """Run the full excerpting pipeline on one source.

    Phase 1: Deterministic preprocessing → list[AssembledChunk]
    Phase 2: LLM classification + grouping → teaching units
    Phase 3: Deterministic fields + LLM enrichment + consensus → ExcerptRecords
    Output: Write excerpts.jsonl + gate_queue.jsonl

    Returns:
        excerpts: Final ExcerptRecord list.
        gate_entries: Human gate entries.
        telemetry: Per-phase timing and statistics.
    """
    raise NotImplementedError
