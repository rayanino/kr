"""Phase 5 Session 2 — Stage-1 deterministic candidate narrowing (REQ-SRC-0051).

Implements the Stage-1 channel-based candidate generator that runs BEFORE the
Stage-2 LLM verifier cell (REQ-SRC-0052, Session 3) in the scholar match
pipeline. The function consumes a parsed fragment + dossier context + locked
registry snapshot, queries deterministic channels against the locked
snapshot, applies the work-title channel guards (list-size + compound-title
decomposition), enforces the K cap (8 standard / 12 degraded), and emits an
immutable :class:`ScholarEvidencePacket`.

Channels (per REQ-SRC-0051 postconditions):
  - name_channel — similarity over canonical_name_ar + known_as + name_variants
  - kunyah_channel — exact match on registry kunya field
  - nisba_channel — intersection of fragment nisba_list with registry nisba
  - work_title_channel — exact-normalized match against registry known_works
  - death_date_channel — registry era_century_hijri ∈ dossier century estimates

Work-title channel applies:
  - Compound-title decomposition: شرح / حاشية / تهذيب / مختصر + base → both authors
  - List-size guard: > N=3 canonical_ids per title → channel reverts to Stage-2
    scoring signal only (does NOT contribute to Stage-1 narrowing)
  - FORBIDDEN normalizations: taa-marbuta (ة → ه), Persian/Urdu/Kurdish (پ
    U+067E, چ U+0686, گ U+06AF, ژ U+0698), Unicode NFC/NFD/NFKC/NFKD on
    stored titles (Critical Rule 2 + arabic-scholarly-conventions.md)
  - ALLOWED normalizations: tashkeel strip, tatweel strip, alef-variant
    unification (ا → آ / إ / أ unified) — for the matching key ONLY

K cap is applied AFTER all channel contributions are merged and de-duplicated
by canonical_id. Standard: 8 (REQ-SRC-0051 line 130). Degraded: 12 (used
when REQ-SRC-0028 case-complexity assessment flags the case as harder).
"""

from __future__ import annotations

import re
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.fragment_parser import FragmentParseResult
from shared.scholar_authority.src.match_contracts import (
    K_CAP_DEGRADED,
    K_CAP_STANDARD,
    DossierContext,
    ScholarCandidate,
    ScholarEvidencePacket,
)
from shared.scholar_authority.src.name_matching import normalized_name_similarity
from shared.scholar_authority.src.snapshot_lock import (
    RegistrySnapshot,
    RegistrySnapshotDriftError,
)


# ---------------------------------------------------------------------------
# Tunables — calibrated at Session 5 against the 50-scholar gold seed
# (SPEC §10 line 460). Session 2 uses the synthesis-ratified placeholder
# values per arabic-reviewer Stage-3 finding.
# ---------------------------------------------------------------------------

WORK_TITLE_LIST_SIZE_GUARD: int = 3
"""REQ-SRC-0051 N=3 — list-size guard threshold above which the work-title
channel reverts to a Stage-2 scoring signal (does not contribute Stage-1
candidates). arabic-reviewer Stage-3 Defect 5 placeholder; calibrated at
implementation phase (L-SCH-004 closure surface)."""


# Compound-title decomposition prefixes per REQ-SRC-0051 line 111-118 +
# arabic-reviewer Stage-3 Novel Finding 3.
_COMPOUND_TITLE_PREFIXES: tuple[str, ...] = (
    "شرح",
    "حاشية",
    "تهذيب",
    "مختصر",
)

# Match-key normalization for work-title index lookups. ALLOWED per
# REQ-SRC-0051: alef-variant unification (ا → آ / إ / أ / ٱ unified) +
# tashkeel strip + tatweel strip. FORBIDDEN: taa-marbuta normalization,
# Persian/Urdu/Kurdish character normalization, Unicode NFC/NFD/NFKC/NFKD.
_WORK_TITLE_ALEF_TRANSLATION = str.maketrans(
    {
        "أ": "ا",
        "إ": "ا",
        "آ": "ا",
        "ٱ": "ا",
    }
)
_WORK_TITLE_TASHKEEL_RE = re.compile(
    "["
    + chr(0x0610) + "-" + chr(0x061A)  # Arabic signs
    + chr(0x064B) + "-" + chr(0x065F)  # tashkeel marks
    + chr(0x0670)                       # superscript alef
    + "]"
)
_WORK_TITLE_TATWEEL = "ـ"
_WORK_TITLE_WHITESPACE_RE = re.compile(r"\s+")


CaseComplexity = Literal["standard", "degraded"]


class _ChannelHit(BaseModel):
    """Internal type — one (channel, score) contribution for a candidate."""

    model_config = ConfigDict(frozen=True, extra="forbid")
    channel: str = Field(min_length=1)
    score: float = Field(ge=0.0, le=1.0)


def normalize_work_title_for_index(title: str) -> str:
    """REQ-SRC-0051 work-title match-key normalization.

    Applied to BOTH the dossier's attributed_works AND the registry's
    known_works on lookup. The function is idempotent: running it twice
    produces the same output as running it once.

    ALLOWED normalizations:
      - tashkeel strip
      - tatweel strip
      - alef-variant unification (ا → آ / إ / أ / ٱ unified)
      - whitespace collapse

    FORBIDDEN normalizations:
      - taa-marbuta (ة → ه) — preserves الهداية vs الهدايه distinction
      - Persian/Urdu/Kurdish characters (پ U+067E / چ U+0686 / گ U+06AF /
        ژ U+0698) — preserves Central/South Asian scholar attribution chains
      - Unicode NFC/NFD/NFKC/NFKD on stored titles
    """
    result = _WORK_TITLE_TASHKEEL_RE.sub("", title)
    result = result.replace(_WORK_TITLE_TATWEEL, "")
    result = result.translate(_WORK_TITLE_ALEF_TRANSLATION)
    result = _WORK_TITLE_WHITESPACE_RE.sub(" ", result).strip()
    return result


def decompose_compound_title(
    normalized_title: str,
) -> Optional[tuple[str, str]]:
    """REQ-SRC-0051 compound-title decomposition (شرح / حاشية / تهذيب / مختصر).

    Returns ``(prefix, base_title)`` if the normalized title begins with one
    of the four compound-title prefixes followed by whitespace and a non-
    empty base title; otherwise returns ``None``. The base title is itself
    suitable for a separate work-title channel input (the base-work author
    becomes a candidate alongside the compound-work author).
    """
    for prefix in _COMPOUND_TITLE_PREFIXES:
        if normalized_title.startswith(prefix + " "):
            base = normalized_title[len(prefix) + 1 :].strip()
            if base:
                return prefix, base
    return None


# ---------------------------------------------------------------------------
# Registry — Session-2 testing substrate. Session 4 will replace this with a
# production interface backed by ``library/registries/scholars.json`` plus
# computed indexes (trigram, work-title-to-id, kunyah-to-id).
# ---------------------------------------------------------------------------


class Registry(BaseModel):
    """In-memory scholar registry for Stage-1 narrowing.

    For Session 2 this is the testing substrate; Session 4 wires the
    production registry interface backed by the shared ``ScholarAuthorityRegistry``
    + computed indexes. Both share the ``release_version`` discipline so the
    snapshot-drift contract from Session 1 (REQ-SRC-0049) flows through.
    """

    model_config = ConfigDict(arbitrary_types_allowed=True)

    release_version: str = Field(min_length=1)
    scholars: list[ScholarAuthorityRecord] = Field(default_factory=list)

    def lookup_by_canonical_id(
        self, canonical_id: str
    ) -> Optional[ScholarAuthorityRecord]:
        """Direct id lookup."""
        for record in self.scholars:
            if record.canonical_id == canonical_id:
                return record
        return None

    def lookup_by_kunya_exact(self, kunya: str) -> list[str]:
        """Find all canonical_ids whose registry kunya field matches exactly."""
        return [r.canonical_id for r in self.scholars if r.kunya == kunya]

    def lookup_by_nisba_intersection(self, nisbas: list[str]) -> list[str]:
        """Find canonical_ids whose registry nisba list intersects ``nisbas``."""
        if not nisbas:
            return []
        seen: set[str] = set()
        result: list[str] = []
        nisba_set = set(nisbas)
        for record in self.scholars:
            if record.canonical_id in seen:
                continue
            if any(n in nisba_set for n in record.nisba):
                result.append(record.canonical_id)
                seen.add(record.canonical_id)
        return result

    def lookup_by_work_title_normalized(
        self, normalized_title: str
    ) -> list[str]:
        """Find canonical_ids whose known_works contain a title that
        normalizes to ``normalized_title``."""
        if not normalized_title:
            return []
        seen: set[str] = set()
        result: list[str] = []
        for record in self.scholars:
            if record.canonical_id in seen:
                continue
            for work in record.known_works:
                if normalize_work_title_for_index(work) == normalized_title:
                    result.append(record.canonical_id)
                    seen.add(record.canonical_id)
                    break
        return result

    def lookup_by_century_active(self, centuries: list[int]) -> list[str]:
        """Find canonical_ids whose registry era_century_hijri ∈ ``centuries``."""
        if not centuries:
            return []
        century_set = set(centuries)
        return [
            r.canonical_id
            for r in self.scholars
            if r.era_century_hijri is not None
            and r.era_century_hijri in century_set
        ]

    def name_similarity_search(
        self, query: str, *, top_k: int
    ) -> list[tuple[str, float]]:
        """Compute name similarity over canonical_name_ar + known_as + name_variants.

        Returns ``[(canonical_id, best_similarity), ...]`` sorted descending
        by similarity, truncated to ``top_k``.
        """
        if top_k <= 0:
            return []
        scored: list[tuple[str, float]] = []
        for record in self.scholars:
            best = normalized_name_similarity(query, record.canonical_name_ar)
            for alt in record.known_as:
                sim = normalized_name_similarity(query, alt)
                if sim > best:
                    best = sim
            for variant in record.name_variants:
                sim = normalized_name_similarity(query, variant)
                if sim > best:
                    best = sim
            if best > 0.0:
                scored.append((record.canonical_id, best))
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]


# ---------------------------------------------------------------------------
# narrow_candidates — REQ-SRC-0051 entry point
# ---------------------------------------------------------------------------


def narrow_candidates(
    parse_result: FragmentParseResult,
    dossier: DossierContext,
    snapshot: RegistrySnapshot,
    registry: Registry,
    *,
    case_complexity: CaseComplexity = "standard",
) -> ScholarEvidencePacket:
    """REQ-SRC-0051 — Stage-1 deterministic candidate narrowing.

    Queries 5 channels (name / kunyah / nisba / work_title / death_date)
    against the locked registry snapshot, applies the work-title channel
    guards (list-size + compound decomposition), merges + de-duplicates by
    canonical_id, and truncates to K (8 standard / 12 degraded) sorted by
    aggregated channel score. Returns an immutable
    :class:`ScholarEvidencePacket` ready for Stage-2 verifier feed.

    Raises :class:`RegistrySnapshotDriftError` if ``registry.release_version``
    differs from ``snapshot.registry_release_version`` (REQ-SRC-0049 +
    INV-SRC-0017 contract).
    """
    if registry.release_version != snapshot.registry_release_version:
        raise RegistrySnapshotDriftError(
            pinned_version=snapshot.registry_release_version,
            observed_version=registry.release_version,
        )

    k_cap = K_CAP_STANDARD if case_complexity == "standard" else K_CAP_DEGRADED

    # Per-candidate channel hits — keyed by canonical_id.
    hits_by_id: dict[str, list[_ChannelHit]] = {}

    # Channel 1 — name (similarity over canonical_name + known_as + name_variants).
    _run_name_channel(
        parse_result=parse_result,
        registry=registry,
        hits_by_id=hits_by_id,
        top_k=k_cap * 2,  # over-fetch; merge with other channels then truncate.
    )

    # Channel 2 — kunyah (exact match on registry.kunya).
    _run_kunyah_channel(
        parsed_kunyah=parse_result.parsed_components.kunyah,
        registry=registry,
        hits_by_id=hits_by_id,
    )

    # Channel 3 — nisba (intersection of fragment nisba_list with registry.nisba).
    _run_nisba_channel(
        parsed_nisbas=parse_result.parsed_components.nisba_list,
        registry=registry,
        hits_by_id=hits_by_id,
    )

    # Channel 4 — work_title (per-title with N=3 list-size guard + compound
    # decomposition). Reads from dossier.attributed_works.
    _run_work_title_channel(
        attributed_works=dossier.attributed_works,
        work_title_extracts=dossier.work_title_extracts,
        registry=registry,
        hits_by_id=hits_by_id,
    )

    # Channel 5 — death_date (registry.era_century_hijri ∈ dossier centuries).
    _run_death_date_channel(
        dossier=dossier,
        registry=registry,
        hits_by_id=hits_by_id,
    )

    # Merge → dedup → sort by aggregated score → truncate to K cap.
    candidates = _build_candidate_set(
        hits_by_id=hits_by_id,
        registry=registry,
        k_cap=k_cap,
    )

    return ScholarEvidencePacket(
        normalized_fragment=parse_result.normalized_fragment,
        display_fragment=parse_result.display_fragment,
        match_key=parse_result.match_key,
        parsed_components=parse_result.parsed_components,
        dossier_context=dossier,
        candidate_set=candidates,
        source_snippets=[],
        registry_release_version=snapshot.registry_release_version,
    )


# ---------------------------------------------------------------------------
# Channel implementations
# ---------------------------------------------------------------------------


def _run_name_channel(
    *,
    parse_result: FragmentParseResult,
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
    top_k: int,
) -> None:
    """Trigram-similarity name channel over canonical_name + known_as + variants."""
    # Use the display_fragment for similarity search — name_matching's
    # normalize_arabic_name is destructive of hamza but consistent across both
    # sides of the comparison.
    matches = registry.name_similarity_search(
        parse_result.display_fragment, top_k=top_k
    )
    for canonical_id, similarity in matches:
        if similarity <= 0.0:
            continue
        hits_by_id.setdefault(canonical_id, []).append(
            _ChannelHit(channel="name", score=similarity)
        )


def _run_kunyah_channel(
    *,
    parsed_kunyah: Optional[str],
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
) -> None:
    """Exact-match kunyah channel."""
    if not parsed_kunyah:
        return
    for canonical_id in registry.lookup_by_kunya_exact(parsed_kunyah):
        hits_by_id.setdefault(canonical_id, []).append(
            _ChannelHit(channel="kunyah", score=1.0)
        )


def _run_nisba_channel(
    *,
    parsed_nisbas: list[str],
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
) -> None:
    """Nisba-intersection channel."""
    if not parsed_nisbas:
        return
    for canonical_id in registry.lookup_by_nisba_intersection(parsed_nisbas):
        hits_by_id.setdefault(canonical_id, []).append(
            _ChannelHit(channel="nisba", score=1.0)
        )


def _run_work_title_channel(
    *,
    attributed_works: list[str],
    work_title_extracts: list[str],
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
) -> None:
    """Work-title channel with N=3 list-size guard + compound decomposition.

    Per REQ-SRC-0051 line 102-109 + 111-118: each title is normalized via
    ``normalize_work_title_for_index``; if a title resolves to >N=3
    canonical_ids the channel reverts to Stage-2 scoring signal only (no
    candidates added from THAT title). Compound titles (شرح + base /
    حاشية + base / تهذيب + base / مختصر + base) emit BOTH the compound
    title AND the base title as separate channel inputs — both authors
    become candidates.
    """
    titles = list(attributed_works) + [
        t for t in work_title_extracts if t not in attributed_works
    ]

    for raw_title in titles:
        normalized = normalize_work_title_for_index(raw_title)
        if not normalized:
            continue

        # Compound decomposition emits TWO channel inputs (commentator + base).
        decomposition = decompose_compound_title(normalized)
        if decomposition is not None:
            _, base_title = decomposition
            _resolve_work_title_with_guard(
                normalized_title=normalized,
                channel_label="work_title",
                registry=registry,
                hits_by_id=hits_by_id,
            )
            _resolve_work_title_with_guard(
                normalized_title=base_title,
                channel_label="work_title_base",
                registry=registry,
                hits_by_id=hits_by_id,
            )
        else:
            _resolve_work_title_with_guard(
                normalized_title=normalized,
                channel_label="work_title",
                registry=registry,
                hits_by_id=hits_by_id,
            )


def _resolve_work_title_with_guard(
    *,
    normalized_title: str,
    channel_label: str,
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
) -> None:
    """Apply REQ-SRC-0051 N=3 list-size guard for a single normalized title.

    If the title resolves to >N=3 canonical_ids in the registry, the channel
    reverts to "Stage-2 scoring signal only" (no candidates added from this
    title) per REQ-SRC-0051 line 102-109. arabic-reviewer Stage-3 Defect 5
    closure surface.
    """
    canonical_ids = registry.lookup_by_work_title_normalized(normalized_title)
    if len(canonical_ids) > WORK_TITLE_LIST_SIZE_GUARD:
        # Channel reverts — title is preserved in the dossier_context (caller
        # supplied) for Stage-2 verifier reasoning, but does NOT contribute
        # to Stage-1 deterministic narrowing here.
        return
    for canonical_id in canonical_ids:
        hits_by_id.setdefault(canonical_id, []).append(
            _ChannelHit(channel=channel_label, score=1.0)
        )


def _run_death_date_channel(
    *,
    dossier: DossierContext,
    registry: Registry,
    hits_by_id: dict[str, list[_ChannelHit]],
) -> None:
    """Century-active intersection channel."""
    centuries = dossier.century_active_hijri_estimates
    if not centuries:
        return
    for canonical_id in registry.lookup_by_century_active(centuries):
        hits_by_id.setdefault(canonical_id, []).append(
            _ChannelHit(channel="century_active", score=1.0)
        )


# ---------------------------------------------------------------------------
# Candidate set assembly
# ---------------------------------------------------------------------------


def _build_candidate_set(
    *,
    hits_by_id: dict[str, list[_ChannelHit]],
    registry: Registry,
    k_cap: int,
) -> list[ScholarCandidate]:
    """Merge per-id channel hits into candidates, sort by total, truncate to K."""
    candidates_with_total: list[tuple[float, ScholarCandidate]] = []
    for canonical_id, channel_hits in hits_by_id.items():
        record = registry.lookup_by_canonical_id(canonical_id)
        if record is None:
            # Defensive — every canonical_id surfaced by a channel should
            # exist in the registry the channel queried. Skip with no
            # silent corruption (next channel adds the candidate; if all
            # channels miss, the candidate is never emitted).
            continue
        # Per-channel score breakdown — collapse multiple hits per channel
        # into the maximum score for that channel.
        score_breakdown: dict[str, float] = {}
        for hit in channel_hits:
            existing = score_breakdown.get(hit.channel, 0.0)
            if hit.score > existing:
                score_breakdown[hit.channel] = hit.score
        total_score = sum(score_breakdown.values())
        provenance = ",".join(sorted(score_breakdown.keys()))
        candidates_with_total.append(
            (
                total_score,
                ScholarCandidate(
                    canonical_id=canonical_id,
                    canonical_name_ar=record.canonical_name_ar,
                    score_breakdown=score_breakdown,
                    provenance_for_inclusion=provenance,
                ),
            )
        )

    candidates_with_total.sort(key=lambda x: x[0], reverse=True)
    return [c for _, c in candidates_with_total[:k_cap]]


__all__ = [
    "WORK_TITLE_LIST_SIZE_GUARD",
    "CaseComplexity",
    "Registry",
    "decompose_compound_title",
    "narrow_candidates",
    "normalize_work_title_for_index",
]
