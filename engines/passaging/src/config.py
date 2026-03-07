"""Passaging Engine — Configuration Loading.

Implements SPEC §8 configuration with per-science overrides.

Loads configuration from:
  1. Default values (hardcoded in PassagingConfig)
  2. Application config file (if present)
  3. Per-science SCIENCE.md overrides (Level 3)

Per-science overrides can change: passage size parameters,
format-specific detection patterns, LLM prompts for implicit
structure discovery.

Self-validation checks are hardcoded and NOT configurable.
"""

from __future__ import annotations

from engines.passaging.contracts import PassagingConfig


def load_config(science_scope: list[str] | None = None) -> PassagingConfig:
    """Load passaging configuration with optional per-science overrides.

    Args:
        science_scope: Science classification(s) for the source.
            Used to look up per-science overrides in SCIENCE.md files.

    Returns:
        PassagingConfig with defaults merged with any applicable overrides.
    """
    raise NotImplementedError
