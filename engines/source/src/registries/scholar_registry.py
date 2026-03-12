"""Scholar Registry — Source Engine Wrapper (SPEC §4.A.5)

Thin wrapper around shared/scholar_authority that handles source-engine
specific concerns: human gate creation on ambiguous matches, muhaqiq
registration, progressive enrichment during intake.

The shared scholar_authority module does the heavy lifting (matching,
scoring, consistency checks). This wrapper translates the results into
source engine actions (gate creation, error logging).
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from engines.source.contracts import (
    HumanGateTrigger,
    ScholarAuthorityRecord,
    ScholarReference,
)
from shared.human_gate.src.human_gate import create_checkpoint
from shared.scholar_authority.src.scholar_authority import (
    ScholarMatchResult,
    lookup,
    register,
)


def lookup_or_register_author(
    name: str,
    death_date_hijri: Optional[int],
    school_affiliations: Optional[dict[str, Optional[str]]],
    source_id: str,
    *,
    death_date_source: Optional[str] = None,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> tuple[ScholarReference, Optional[str]]:
    """Look up an author; register if new; create human gate if ambiguous.

    Returns (ScholarReference, gate_checkpoint_id_or_None).

    SPEC §4.A.5 thresholds:
    - >= 0.85: auto-link, return existing record's canonical_id
    - 0.50-0.85: create AUTHOR_DISAMBIGUATION gate, return best match's id
    - < 0.50: register new, return new canonical_id
    """
    # Extract one school value for lookup() compatibility
    school: Optional[str] = None
    if school_affiliations:
        school = next((v for v in school_affiliations.values() if v), None)

    result: ScholarMatchResult = lookup(
        name,
        death_date_hijri=death_date_hijri,
        school=school,
        registry_path=registry_path,
    )

    if result.action == "auto_link" and result.record is not None:
        ref = ScholarReference(
            canonical_id=result.record.canonical_id,
            name_arabic=name,
            confidence=result.match_score,
            source_of_identification="extracted",
        )
        return ref, None

    if result.action == "human_gate" and result.record is not None:
        checkpoint = create_checkpoint(
            source_id=source_id,
            trigger=HumanGateTrigger.AUTHOR_DISAMBIGUATION,
            trigger_detail=(
                f"Author '{name}' matches '{result.record.canonical_name_ar}' "
                f"(score {result.match_score:.3f}), needs confirmation"
            ),
            fields_to_review=["author"],
            current_values={
                "inferred_name": name,
                "best_match_id": result.record.canonical_id,
                "best_match_name": result.record.canonical_name_ar,
                "match_score": result.match_score,
            },
            alternatives=[{
                "canonical_id": result.record.canonical_id,
                "name_arabic": result.record.canonical_name_ar,
                "match_score": result.match_score,
            }],
        )
        ref = ScholarReference(
            canonical_id=result.record.canonical_id,
            name_arabic=name,
            confidence=result.match_score,
            source_of_identification="extracted",
        )
        return ref, checkpoint.checkpoint_id

    # action == "new_record": register new scholar
    new_record = ScholarAuthorityRecord(
        canonical_id="",  # assigned by register()
        canonical_name_ar=name,
        death_date_hijri=death_date_hijri,
        sources_encountered_in=[source_id],
        last_updated="",  # set by register()
    )
    if school_affiliations:
        new_record.school_affiliations = school_affiliations
    if death_date_source:
        new_record.death_date_source = death_date_source

    registered = register(new_record, registry_path=registry_path)
    ref = ScholarReference(
        canonical_id=registered.canonical_id,
        name_arabic=name,
        confidence=1.0,
        source_of_identification="extracted",
    )
    return ref, None


def lookup_or_register_muhaqiq(
    muhaqiq_name: str,
    source_id: str,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarReference:
    """Register muhaqiq as a scholar (SPEC §4.A.5: 'Tahqiq editors are scholars').

    Muhaqiqs rarely have death dates or school affiliations in the metadata,
    so matching is primarily name-based. Auto-links above 0.85, otherwise
    registers new (no human gate for muhaqiqs — less critical than authors).
    """
    result: ScholarMatchResult = lookup(
        muhaqiq_name,
        registry_path=registry_path,
    )

    if result.action == "auto_link" and result.record is not None:
        return ScholarReference(
            canonical_id=result.record.canonical_id,
            name_arabic=muhaqiq_name,
            confidence=result.match_score,
            source_of_identification="extracted",
        )

    # Register new muhaqiq
    new_record = ScholarAuthorityRecord(
        canonical_id="",
        canonical_name_ar=muhaqiq_name,
        sources_encountered_in=[source_id],
        last_updated="",
    )
    registered = register(new_record, registry_path=registry_path)
    return ScholarReference(
        canonical_id=registered.canonical_id,
        name_arabic=muhaqiq_name,
        confidence=1.0,
        source_of_identification="extracted",
    )
