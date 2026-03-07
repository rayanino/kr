"""§4.B.8 — Passage Scholarly Completeness Forecast (تقدير اكتمال المقطع العلمي).

After initial passage boundaries are set, forecasts whether each passage
contains a scholarly complete unit by analyzing discourse_flow data.

Forecast levels:
  complete → at least one full argument cycle
  partial_opening → opens with content from previous passage
  partial_closing → closes with incomplete argument
  fragment → discourse segments that don't form a scholarly unit
  unknown → discourse_flow unavailable

Corrective merge: if forecast detects a fragment that can be merged with
its successor without exceeding hard_max, the merge is applied (max 2
corrective merges per fragment, PSG_COMPLETENESS_MERGE_REPAIR).

Distinguishes structural_incompleteness (passaging error, fixable) from
authorial_incompleteness (source text is inherently incomplete, not fixable).
"""

from __future__ import annotations


def forecast_completeness(passage_text: str, discourse_segments: list) -> dict:
    """Forecast scholarly completeness of a passage.

    Returns CompletenessForecast dict.
    """
    raise NotImplementedError


def apply_corrective_merges(passages: list, forecasts: list, config) -> list:
    """Merge fragment passages with successors when possible.

    Max 2 corrective merges per fragment. Hard max never exceeded.
    """
    raise NotImplementedError
