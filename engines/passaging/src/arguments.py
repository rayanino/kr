"""§4.B.6 — Scholarly Argument Boundary Detection (حفظ حدود الحجج).

Detects scholarly argument spans (مسألة, دليل, اعتراض, جواب, ترجيح)
and prevents passage boundaries from splitting them.

Two detection signals:
  PRIMARY: discourse_flow from normalization engine §4.B.10
  FALLBACK: keyword-based state machine (when discourse_flow absent)

When both signals are available, cross-validate: if they agree,
detection_source = 'cross_validated'. If they disagree, use the
signal with higher text coverage (ties: discourse_flow).

Argument nesting depth capped at 3. Oversized arguments (>150% of
hard_max) are split at sub-argument boundaries (فرع, تنبيه).

Gated by config.enable_argument_detection (default: true).
"""

from __future__ import annotations


def build_argument_map(content_units: list, division_tree: list) -> list:
    """Build cross-page argument map from discourse_flow data.

    Returns list of argument spans with their boundaries, types,
    and completeness status.
    """
    raise NotImplementedError


def detect_arguments_keyword(text: str) -> list:
    """Fallback: detect arguments using keyword state machine.

    Used when discourse_flow data is absent (PSG_DISCOURSE_FLOW_ABSENT).
    """
    raise NotImplementedError
