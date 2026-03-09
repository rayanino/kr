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

from engines.source.contracts import ScholarAuthorityRecord, ScholarReference


def lookup_or_register_author(
    name: str,
    death_date_hijri: Optional[int],
    school: Optional[str],
    source_id: str,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> tuple[ScholarReference, Optional[str]]:
    """Look up an author; register if new; create human gate if ambiguous.
    
    Returns (ScholarReference, gate_checkpoint_id_or_None).
    
    SPEC §4.A.5 thresholds:
    - >= 0.85: auto-link, return existing record's canonical_id
    - 0.50-0.85: create AUTHOR_DISAMBIGUATION gate, return best match's id
    - < 0.50: register new, return new canonical_id
    """
    raise NotImplementedError


def lookup_or_register_muhaqiq(
    muhaqiq_name: str,
    source_id: str,
    *,
    registry_path: Path = Path("library/registries/scholars.json"),
) -> ScholarReference:
    """Register muhaqiq as a scholar (SPEC §4.A.5: 'Tahqiq editors are scholars').
    
    Muhaqiqs rarely have death dates or school affiliations in the metadata,
    so matching is primarily name-based. Uses a lower gate threshold since
    muhaqiq disambiguation is less critical than author disambiguation.
    """
    raise NotImplementedError
