"""Trustworthiness Evaluation — SPEC §4.A.8

Five weighted factors:
- author_standing (0.30): classical ≤1000AH → 0.90; post-classical >1000 → 0.70; no death date → 0.30
- tahqiq_quality (0.25): recognized muhaqiq → 0.90; unknown → 0.50; no muhaqiq → 0.30-0.40
- publisher_reputation (0.15): known publisher → configured score; unknown → 0.40
- source_authority (0.15): primary → 0.85; reference → 0.60; modern_compilation → 0.40
- text_fidelity (0.15): high → 0.90; medium → 0.60; low → 0.30; unknown → 0.40

Combined >= 0.65 → verified. < 0.65 → flagged.
Conservative bias: uncertain → flagged.

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

from typing import Optional

from engines.source.contracts import (
    AuthorityLevel,
    ScholarAuthorityRecord,
    ScholarReference,
    TextFidelity,
    TrustTier,
    TrustworthinessFactor,
)
from shared.scholar_authority.src.name_matching import normalized_name_similarity


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

    Returns (trust_tier, trust_score, trust_factors, trust_reason).
    """
    death_date = author_record.death_date_hijri if author_record else None

    author_score, author_reason = _score_author_standing(author_record, source_id)
    tahqiq_score, tahqiq_reason = _score_tahqiq_quality(
        muhaqiq_name, death_date, recognized_muhaqiqs,
    )
    pub_score, pub_reason = _score_publisher_reputation(publisher, known_publishers)
    auth_score, auth_reason = _score_source_authority(authority_level)
    fid_score, fid_reason = _score_text_fidelity(text_fidelity)

    factors = [
        TrustworthinessFactor(name="author_standing", weight=0.30, score=author_score, reason=author_reason),
        TrustworthinessFactor(name="tahqiq_quality", weight=0.25, score=tahqiq_score, reason=tahqiq_reason),
        TrustworthinessFactor(name="publisher_reputation", weight=0.15, score=pub_score, reason=pub_reason),
        TrustworthinessFactor(name="source_authority", weight=0.15, score=auth_score, reason=auth_reason),
        TrustworthinessFactor(name="text_fidelity", weight=0.15, score=fid_score, reason=fid_reason),
    ]

    trust_score = sum(f.weight * f.score for f in factors)

    # Tier determination
    critical_low = author_score < 0.30 and tahqiq_score < 0.40
    if trust_score >= 0.65 and not critical_low:
        tier = TrustTier.VERIFIED
        reason = f"Trust score {trust_score:.3f} >= 0.65 threshold"
    else:
        tier = TrustTier.FLAGGED
        if critical_low:
            reason = (
                f"Critical low: author_standing={author_score:.2f} < 0.30 "
                f"AND tahqiq_quality={tahqiq_score:.2f} < 0.40"
            )
        else:
            reason = f"Trust score {trust_score:.3f} < 0.65 threshold"

    return tier, trust_score, factors, reason


def _score_author_standing(
    author_record: Optional[ScholarAuthorityRecord],
    source_id: str,
) -> tuple[float, str]:
    """Score author scholarly standing — VALIDATED first-intake formula.

    death_date_hijri ≤ 1000 → 0.90 (classical)
    death_date_hijri > 1000 → 0.70 (post-classical)
    death_date_hijri is None → 0.30 (unknown/contemporary)
    """
    if author_record is None or author_record.death_date_hijri is None:
        return 0.30, "Unknown/contemporary author (no death date)"

    if author_record.death_date_hijri <= 1000:
        return 0.90, f"Classical scholar (d. {author_record.death_date_hijri} AH, ≤ 1000)"

    return 0.70, f"Post-classical scholar (d. {author_record.death_date_hijri} AH, > 1000)"


def _score_tahqiq_quality(
    muhaqiq_name: Optional[str],
    author_death_hijri: Optional[int],
    recognized_muhaqiqs: list[str],
) -> tuple[float, str]:
    """Score tahqiq quality factor.

    Recognized muhaqiq: 0.90. Unknown muhaqiq: 0.50.
    No muhaqiq, pre-modern (≤1300): 0.40. No muhaqiq, unknown date: 0.35.
    No muhaqiq, modern (>1300): 0.30.
    """
    if muhaqiq_name:
        # Check against recognized list using name similarity
        for recognized in recognized_muhaqiqs:
            sim = normalized_name_similarity(muhaqiq_name, recognized)
            if sim >= 0.85:
                return 0.90, f"Recognized muhaqiq: {muhaqiq_name} (matched {recognized})"
        return 0.50, f"Unknown muhaqiq: {muhaqiq_name}"

    # No muhaqiq
    if author_death_hijri is None:
        return 0.35, "No muhaqiq, author death date unknown"
    if author_death_hijri <= 1300:
        return 0.40, f"No muhaqiq, pre-modern author (d. {author_death_hijri} AH)"
    return 0.30, f"No muhaqiq, modern author (d. {author_death_hijri} AH)"


def _score_publisher_reputation(
    publisher: Optional[str],
    known_publishers: dict[str, dict],
) -> tuple[float, str]:
    """Score publisher reputation — substring matching against name + variants."""
    if not publisher:
        return 0.40, "No publisher information"

    for canonical_name, info in known_publishers.items():
        # Check canonical name via substring
        if canonical_name in publisher or publisher in canonical_name:
            score = info.get("score", 0.40)
            return score, f"Known publisher: {canonical_name} (score {score})"
        # Check variants
        for variant in info.get("variants", []):
            if variant in publisher or publisher in variant:
                score = info.get("score", 0.40)
                return score, f"Known publisher variant: {variant} → {canonical_name} (score {score})"

    return 0.40, f"Unknown publisher: {publisher}"


def _score_source_authority(authority_level: AuthorityLevel) -> tuple[float, str]:
    """primary→0.85, reference→0.60, modern_compilation→0.40."""
    scores = {
        AuthorityLevel.PRIMARY: (0.85, "Primary source"),
        AuthorityLevel.REFERENCE: (0.60, "Reference work"),
        AuthorityLevel.MODERN_COMPILATION: (0.40, "Modern compilation"),
    }
    return scores.get(authority_level, (0.40, f"Unknown authority: {authority_level}"))


def _score_text_fidelity(text_fidelity: TextFidelity) -> tuple[float, str]:
    """high→0.90, medium→0.60, low→0.30, unknown→0.40."""
    scores = {
        TextFidelity.HIGH: (0.90, "High text fidelity"),
        TextFidelity.MEDIUM: (0.60, "Medium text fidelity"),
        TextFidelity.LOW: (0.30, "Low text fidelity"),
        TextFidelity.UNKNOWN: (0.40, "Unknown text fidelity"),
    }
    return scores.get(text_fidelity, (0.40, f"Unknown fidelity: {text_fidelity}"))
