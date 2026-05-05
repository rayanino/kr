"""Phase 5 Session 5 — DossierContext builder (engine-agnostic primitives layer).

Builds a ``DossierContext`` from primitive inputs (str/int/Iterable) so that
the shared module does NOT import engine-specific contract types. Each
engine writes its own adapter that extracts the primitives from its own
state types and calls this builder.

Design choices (Session 5 integration):

  - Engine-agnostic by construction. ``shared/scholar_authority/`` never
    imports from ``engines/*/contracts.py`` (would invert the layering).
    Engines call this with primitives extracted from their own types.

  - Hijri century derivation lives here because the formula is
    domain-shared (every engine that builds a dossier needs the same
    Hijri-year → century conversion). Per CON-SRC-0009 line 60-66 and
    INV-SRC-0013 attribute classes the dossier surfaces
    ``century_active_hijri_estimates`` as a list[int]; for source-engine
    Step 50 the only available signal is ``author_death_hijri`` → death
    century. Future engines (atomization, taxonomy) may pass richer
    estimates (born+died centuries) when career-phase data is available.

  - All inputs are optional/Iterable so callers can pass partial signal
    sets — the dossier captures whatever the upstream had per CON-SRC-0009
    line 60-66 ("All fields optional/empty-default — different sources
    surface different evidence; the packet captures whatever the dossier
    had").

  - Title-string deduplication preserves order of first occurrence so
    audit trails remain stable across re-runs (D-023 metadata pass-through
    spirit applied to lists).
"""

from __future__ import annotations

from typing import Iterable, Optional

from shared.scholar_authority.src.match_contracts import DossierContext


def hijri_century_of_year(death_year_hijri: int) -> int:
    """Hijri century containing ``death_year_hijri`` (1-indexed).

    Examples:
      - AH 1   → century 1
      - AH 100 → century 1
      - AH 101 → century 2
      - AH 728 (Ibn Taymiyya) → century 8
      - AH 852 (Ibn Hajar al-Asqalani) → century 9
      - AH 974 (Ibn Hajar al-Haytami) → century 10

    Formula: ``((year - 1) // 100) + 1``. The off-by-one against naive
    ``year // 100`` is what makes AH 100 belong to century 1, not century
    0 or 1-with-fractional-spillover. Matches the convention used in the
    50-scholar gold seed (Session 4.5) and the
    ``ScholarAuthorityRecord.era_century_hijri`` field semantics
    (contracts.py:722).

    Raises:
      ValueError: if ``death_year_hijri`` is negative. Year 0 is allowed
        (some early records use 0 as "unknown"; the resulting century 0
        will simply never align against any populated registry record's
        ``era_century_hijri``).
    """
    if death_year_hijri < 0:
        raise ValueError(
            f"hijri_century_of_year: death_year_hijri must be >= 0, "
            f"got {death_year_hijri}"
        )
    if death_year_hijri == 0:
        return 0
    return ((death_year_hijri - 1) // 100) + 1


def _dedupe_preserve_order(items: Iterable[str]) -> list[str]:
    """Deduplicate while preserving order of first occurrence.

    Empty strings and pure-whitespace strings are dropped (they carry no
    signal and would pollute the alignment scoring).
    """
    seen: set[str] = set()
    out: list[str] = []
    for item in items:
        if not item or not item.strip():
            continue
        if item in seen:
            continue
        seen.add(item)
        out.append(item)
    return out


def build_dossier_context(
    *,
    genre: Optional[str] = None,
    primary_science: Optional[str] = None,
    death_year_hijri: Optional[int] = None,
    school_affiliation_hints: Optional[dict[str, Optional[str]]] = None,
    title_strings: Iterable[str] = (),
    geographic_origin: Optional[str] = None,
    geographic_active: Iterable[str] = (),
    work_title_extracts: Optional[Iterable[str]] = None,
) -> DossierContext:
    """Build a ``DossierContext`` from primitive inputs.

    Per CON-SRC-0009 line 60-66 the DossierContext fields are:
    ``genre``, ``primary_science``, ``century_active_hijri_estimates``,
    ``school_affiliation_hints``, ``attributed_works``,
    ``geographic_signals``, ``work_title_extracts``. All optional with
    empty-default semantics.

    Mapping rules:
      - ``genre`` and ``primary_science`` pass through unchanged
      - ``century_active_hijri_estimates``: ``[hijri_century_of_year(death_year_hijri)]``
        when ``death_year_hijri`` is non-null; empty list otherwise.
        Single-element list because Step 50 only has one death-year
        signal; richer engines may pass a wider span.
      - ``school_affiliation_hints``: passes through (or empty dict).
        Per-science map: each key is a science name, each value is the
        hinted school or ``None`` for "unknown for this science".
      - ``attributed_works``: deduplicated ``title_strings`` preserving
        insertion order.
      - ``geographic_signals``: ``geographic_origin`` (if not None)
        prepended to ``geographic_active``, deduplicated.
      - ``work_title_extracts``: defaults to the same list as
        ``attributed_works`` when caller does not pass a separate list
        (work_title_extracts is the verbatim title strings from the
        source; for the source engine they ARE the attributed works at
        Step 50 — atomization may later separate quoted-from titles
        from authored-by titles).

    Args:
      genre: Source genre signal ("matn", "sharh", etc.) or None.
      primary_science: Primary Islamic science ("fiqh", "hadith", "tafsir",
        ...) or None.
      death_year_hijri: Author's Hijri death year, used to derive the
        single-element century estimate. None means no temporal signal.
      school_affiliation_hints: Per-science school hints. None → {}.
      title_strings: Work titles attributed to the author by the source
        engine (e.g., from ``IntakeDossier.work_identity_proposal``).
      geographic_origin: The author's place of origin signal, if known.
      geographic_active: Iterable of places where the author was active.
      work_title_extracts: Optional override for the
        ``work_title_extracts`` field. When None (default), the same
        deduplicated list as ``attributed_works`` is used.

    Returns:
      A frozen ``DossierContext`` ready for ``ScholarEvidencePacket``
      construction.
    """
    century_estimates: list[int] = (
        [hijri_century_of_year(death_year_hijri)]
        if death_year_hijri is not None
        else []
    )

    works = _dedupe_preserve_order(title_strings)

    geo_signals_unmerged: list[str] = []
    if geographic_origin is not None:
        geo_signals_unmerged.append(geographic_origin)
    geo_signals_unmerged.extend(geographic_active)
    geo_signals = _dedupe_preserve_order(geo_signals_unmerged)

    extracts = (
        _dedupe_preserve_order(work_title_extracts)
        if work_title_extracts is not None
        else list(works)
    )

    return DossierContext(
        genre=genre,
        primary_science=primary_science,
        century_active_hijri_estimates=century_estimates,
        school_affiliation_hints=school_affiliation_hints or {},
        attributed_works=works,
        geographic_signals=geo_signals,
        work_title_extracts=extracts,
    )


__all__ = [
    "build_dossier_context",
    "hijri_century_of_year",
]
