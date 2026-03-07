"""Atomization Engine — Configuration.

Implements SPEC §8: Parameter loading with defaults and valid ranges.

Loads AtomizationConfig from contracts.py with per-science override support.
Per-science overrides (Level 3 / SCIENCE.md) can extend the scholarly function
enum, add science-specific pattern rules, and provide science-specific few-shot
examples for the LLM prompt.

Hardcoded (architectural) vs. configurable (operational) boundary defined in §8.
"""

from __future__ import annotations


def load_config(source_id: str | None = None,
                science: str | None = None) -> "AtomizationConfig":
    """Load atomization configuration with optional per-science overrides.

    Returns AtomizationConfig with defaults from SPEC §8.
    If science is provided, applies science-specific overrides.
    """
    raise NotImplementedError
