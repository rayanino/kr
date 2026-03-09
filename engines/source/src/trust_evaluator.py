"""Trustworthiness Evaluation — SPEC §4.A.8

Five weighted factors:
- author_standing (0.30): classical ≤1000AH → 0.90; post-classical >1000 → 0.70; no death date → 0.30
- tahqiq_quality (0.25): recognized muhaqiq → 0.90; unknown → 0.50; no muhaqiq → 0.30-0.40
- publisher_reputation (0.15): known publisher → configured score; unknown → 0.40
- source_authority (0.15): primary → 0.85; reference → 0.60; modern_compilation → 0.40
- text_fidelity (0.15): high → 0.90; medium → 0.60; low → 0.30; unknown → 0.40

Combined >= 0.65 → verified. < 0.65 → flagged.
Conservative bias: uncertain → flagged.
Special cases: owner-authored → verified; Quran/canonical hadith → verified.

[VALIDATED — Step 2 Phase 0]: 13/13 correct at threshold 0.65 (uniquely optimal 0.55-0.75).
[RESOLVED]: Classical cutpoint 1000 AH (not 900).

IMPORTANT — Author Standing First-Intake Fix (Session 5a build-prep finding):
The SPEC §4.A.8 adds conditions "scholarly_standing non-null AND sources_encountered_in
contains at least one source_id other than the current source" for the 0.90 classical tier.
These conditions were added during HARDENING but never re-validated. On first intake, every
author has 0 prior sources, causing 6/13 fixtures to produce INCORRECT trust tiers.

The validated formula (Phase 0, 13/13 correct) uses ONLY the death date:
- death_date_hijri ≤ 1000 → 0.90 (classical)
- death_date_hijri > 1000 → 0.70 (post-classical with known date)
- death_date_hijri is None → 0.30 (unknown)

The "prior sources" check belongs in trust RE-EVALUATION (§4.A.8 last paragraph),
not in initial evaluation. On re-evaluation after enrichment, the full conditions apply.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Optional

from engines.source.contracts import (
    TrustTier,
    TrustworthinessFactor,
    AuthorityLevel,
    TextFidelity,
    ScholarAuthorityRecord,
    ScholarReference,
)


def evaluate_trust(
    author_ref: ScholarReference,
    author_record: Optional[ScholarAuthorityRecord],
    muhaqiq_name: Optional[str],
    publisher: Optional[str],
    authority_level: AuthorityLevel,
    text_fidelity: TextFidelity,
    source_id: str,
    *,
    recognized_muhaqiqs: list[str],
    known_publishers: dict[str, dict],
) -> tuple[TrustTier, float, list[TrustworthinessFactor], str]:
    """Compute 5-factor weighted trust score.
    
    SPEC §4.A.8 full algorithm.
    
    Args:
        author_ref: ScholarReference for the author.
        author_record: Full ScholarAuthorityRecord if available (for death_date,
                       sources_encountered_in, scholarly_standing).
        muhaqiq_name: Raw muhaqiq name from extraction, or None.
        publisher: Publisher name from extraction, or None.
        authority_level: AuthorityLevel enum from inference.
        text_fidelity: TextFidelity enum from format/quality assessment.
        source_id: Current source_id (for checking if author has prior sources).
        recognized_muhaqiqs: List of recognized muhaqiq names from config.
        known_publishers: Dict from config: publisher name → {score, variants}.
    
    Returns:
        (trust_tier, trust_score, trust_factors, trust_reason)
        
    trust_tier: TrustTier.VERIFIED if score >= 0.65, TrustTier.FLAGGED otherwise.
    Also FLAGGED if author_standing < 0.30 AND tahqiq_quality < 0.40 (critical low).
    """
    raise NotImplementedError


def _score_author_standing(
    author_record: Optional[ScholarAuthorityRecord],
    source_id: str,
) -> tuple[float, str]:
    """Score author scholarly standing factor.
    
    VALIDATED formula (Phase 0, 13/13 correct):
    - death_date_hijri ≤ 1000 → 0.90 (classical scholar)
    - death_date_hijri > 1000 → 0.70 (post-classical, known date)
    - death_date_hijri is None → 0.30 (unknown/contemporary)
    
    NOTE: The SPEC §4.A.8 text adds "scholarly_standing non-null AND
    sources_encountered_in contains at least one OTHER source_id" for the
    0.90 tier. These conditions apply to trust RE-EVALUATION only, not
    first intake. See module docstring for full explanation.
    
    For trust re-evaluation (enrichment path): use the full SPEC formula
    including prior-sources check.
    
    Returns (score, reason).
    """
    raise NotImplementedError


def _score_tahqiq_quality(
    muhaqiq_name: Optional[str],
    author_death_hijri: Optional[int],
    recognized_muhaqiqs: list[str],
) -> tuple[float, str]:
    """Score tahqiq quality factor.
    
    SPEC §4.A.8:
    - Recognized muhaqiq (in config list): → 0.90
    - Unknown muhaqiq: → 0.50
    - No muhaqiq, pre-modern (death <= 1300): → 0.40
    - No muhaqiq, death date unknown: → 0.35
    - No muhaqiq, modern (death > 1300 or contemporary): → 0.30
    
    Muhaqiq matching: check if muhaqiq_name matches any recognized muhaqiq
    using normalized_name_similarity >= 0.85 from name_matching.py.
    
    Returns (score, reason).
    """
    raise NotImplementedError


def _score_publisher_reputation(
    publisher: Optional[str],
    known_publishers: dict[str, dict],
) -> tuple[float, str]:
    """Score publisher reputation factor.
    
    SPEC §4.A.8:
    - Known publisher: use configured score (0.55-0.80).
    - Unknown/absent: → 0.40.
    
    Matching: check canonical name AND all variants using substring matching.
    
    Returns (score, reason).
    """
    raise NotImplementedError


def _score_source_authority(authority_level: AuthorityLevel) -> tuple[float, str]:
    """Score source authority factor.
    
    SPEC §4.A.8: primary→0.85, reference→0.60, modern_compilation→0.40.
    """
    raise NotImplementedError


def _score_text_fidelity(text_fidelity: TextFidelity) -> tuple[float, str]:
    """Score text fidelity factor.
    
    SPEC §4.A.8: high→0.90, medium→0.60, low→0.30, unknown→0.40.
    """
    raise NotImplementedError
