"""Atomization Engine — Argument Completeness Scoring.

Implements SPEC §4.B.6: Detecting structural gaps in scholarly argument patterns.

Depends on §4.B.1 rhetorical pattern detection. For each detected pattern,
computes a completeness_ratio = |required_present| / |required_present ∪ required_missing|.

Example: a khilaf pattern with two opinions but evidence for only one
scores < 1.0 with gap_description identifying the missing evidence.

Sets incomplete_argument review flag on all atoms in a passage when
completeness_ratio < 1.0.
"""

from __future__ import annotations


def score_argument_completeness(atoms: list[dict],
                                rhetorical_pattern: dict | None,
                                config: "AtomizationConfig") -> "ArgumentCompletenessScore | None":
    """Score the argument completeness of a passage.

    Returns ArgumentCompletenessScore or None if no pattern detected
    or completeness scoring is disabled.
    """
    raise NotImplementedError
