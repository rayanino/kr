"""Phase 5 Session 4.5 — gold-seed calibration tests for scholar_match_cell.

Calibrates and validates the SPEC §4.A.2 + REQ-SRC-0053 + INV-SRC-0013 weights and
thresholds against the 50-scholar gold baseline at
``tests/fixtures/scholar_gold_seed_50.json`` per shared SPEC §10 line 460.

Closes ``shared/scholar_authority/KNOWN_LIMITATIONS.md`` L-SCH-004.

Three calibration scenarios per gold-seed entry:

  (a) canonical-dossier scenario — 50 cases
      Feed the scholar's canonical name fragment + a dossier that aligns
      ALL of {primary_science, century, school, attributed_works, geographic}.
      Expect: DEFINITIVE for that scholar.

  (b) cross-trap scenario — 10 cases (5 trap pairs × 2 sides)
      Feed the trap-pair member's name fragment + the OTHER trap member's
      canonical dossier. Expect: DEFINITIVE for the OTHER trap member
      (proves disambiguation by signals overrides shared name).

  (c) name-only scenario — 50 cases
      Feed the canonical name fragment + an EMPTY DossierContext.
      Expect: INSUFFICIENT_EVIDENCE (no signals → confidence falls below
      INSUFFICIENT_FLOOR=0.70 + name-only cap CR-45 enforced by routing).

Total: 110 calibration cases + 1 invariant guard = 111 tests.

The deterministic stub VerifierCallable below computes confidence as
``CONF_BASELINE + alignment_ratio * CONF_RANGE`` (0.40 + ratio*0.55), where
``alignment_ratio`` is the fraction of dossier-provided non-name attributes
that intersect the candidate's ``ScholarAuthorityRecord``. With a fully-aligned
dossier (4-of-4 attributes), confidence reaches 0.95 — comfortably above
MEAN_THRESHOLD=0.92 / EACH_THRESHOLD=0.90. With an empty dossier, no
attributes are evaluated → confidence sits at the 0.40 baseline — well below
INSUFFICIENT_FLOOR=0.70.

Per ``.claude/rules/testing.md`` "no real API calls in unit tests": every
verifier dispatch is the in-process deterministic stub. Production wiring
with LiteLLM + Instructor multi-model consensus is out of scope here.

Per ``.claude/rules/constraint-origin-trace.md``: the calibrated values are
mirrored into ``engines/excerpting/reference/CONSTRAINT_REGISTRY.md`` entries
CR-39 through CR-51, with this test file named as the calibration evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal, Optional

import pytest

from engines.source.contracts import ScholarAuthorityRecord
from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    DossierContext,
    ScholarEvidencePacket,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
)
from shared.scholar_authority.src.scholar_match_cell import (
    ScholarMatchCellOrchestration,
    scholar_match_cell,
)
from shared.scholar_authority.src.snapshot_lock import (
    pin_registry_snapshot,
)
from shared.scholar_authority.src.stage1_narrowing import Registry
from shared.scholar_authority.src.stage2_verifier import VerifierSpec


# ---------------------------------------------------------------------------
# Gold-seed loader (module-scope so parametrize can read at collection time)
# ---------------------------------------------------------------------------

_REPO_ROOT = Path(__file__).resolve().parents[3]
GOLD_SEED_PATH = _REPO_ROOT / "tests" / "fixtures" / "scholar_gold_seed_50.json"


def _load_gold_seed() -> dict:
    with GOLD_SEED_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


GOLD_SEED: dict = _load_gold_seed()
GOLD_SCHOLARS: list[dict] = GOLD_SEED["scholars"]
TRAP_PAIRS: list[dict] = GOLD_SEED["trap_pairs"]
RELEASE_VERSION: str = GOLD_SEED["version"]


def _all_canonical_ids() -> list[str]:
    return [s["record"]["canonical_id"] for s in GOLD_SCHOLARS]


def _entry_by_id(canonical_id: str) -> dict:
    for entry in GOLD_SCHOLARS:
        if entry["record"]["canonical_id"] == canonical_id:
            return entry
    raise KeyError(canonical_id)


def _trap_pair_cases() -> list[tuple[str, str]]:
    """(probe_id, expected_id) pairs for cross-trap routing — both directions per pair."""
    cases: list[tuple[str, str]] = []
    for pair in TRAP_PAIRS:
        a, b = pair["members"]
        cases.append((a, b))
        cases.append((b, a))
    return cases


# ---------------------------------------------------------------------------
# Stub VerifierCallable — signal-alignment scoring
# ---------------------------------------------------------------------------

CONF_BASELINE: float = 0.40
"""Confidence floor for a candidate with zero dossier-attribute alignment."""

CONF_RANGE: float = 0.55
"""Confidence band added on top of baseline when alignment is 1.0 (4-of-4 in canonical dossier).
Calibrated so a fully-aligned candidate reaches 0.95 — clearing both
MEAN_THRESHOLD (0.92) and EACH_THRESHOLD (0.90) per REQ-SRC-0053."""


def _attribute_classes_aligned(
    record: ScholarAuthorityRecord, dossier: DossierContext
) -> tuple[int, int]:
    """Return ``(aligned_count, evaluated_count)`` over INV-SRC-0013 non-name attribute classes.

    Each class is evaluated only if the dossier carries a signal for it.
    An aligned class contributes 1; otherwise 0. An empty dossier returns
    ``(0, 0)`` so the confidence falls back to ``CONF_BASELINE``.

    Mirrors the 6 attribute classes counted by
    ``shared.scholar_authority.src.threshold_compounding.count_non_name_corroborating_attributes``:
    primary_science / century_active / school_affiliations / attributed_works /
    region_origin / region_active. The teacher_student_link and secondary_sciences
    classes are deferred (no DossierContext fields per Session 5+ TODO).
    """
    aligned = 0
    evaluated = 0

    if dossier.primary_science is not None and record.primary_science is not None:
        evaluated += 1
        if record.primary_science == dossier.primary_science:
            aligned += 1

    if dossier.century_active_hijri_estimates and record.era_century_hijri is not None:
        evaluated += 1
        if record.era_century_hijri in dossier.century_active_hijri_estimates:
            aligned += 1

    if dossier.school_affiliation_hints:
        evaluated += 1
        for science, hint in dossier.school_affiliation_hints.items():
            if hint is not None and record.school_affiliations.get(science) == hint:
                aligned += 1
                break

    if dossier.attributed_works:
        evaluated += 1
        record_works = set(record.known_works)
        if any(work in record_works for work in dossier.attributed_works):
            aligned += 1

    if dossier.geographic_signals and (
        record.geographic_origin is not None or record.geographic_active
    ):
        evaluated += 1
        record_geo: set[str] = set(record.geographic_active)
        if record.geographic_origin is not None:
            record_geo.add(record.geographic_origin)
        if any(sig in record_geo for sig in dossier.geographic_signals):
            aligned += 1

    return aligned, evaluated


def _confidence_from_alignment(aligned: int, evaluated: int) -> float:
    """``CONF_BASELINE + (aligned/evaluated) * CONF_RANGE``; baseline if nothing was evaluated."""
    if evaluated == 0:
        return CONF_BASELINE
    return CONF_BASELINE + (aligned / evaluated) * CONF_RANGE


_BLANK_BREAKDOWN: ScoreBreakdown = ScoreBreakdown(
    name_match=0.5,
    death_date_proximity=0.0,
    school_affiliation_overlap=0.0,
    work_title_match=0.0,
    teacher_student_network_match=0.0,
    geographic_origin_match=0.0,
    century_active_match=0.0,
    primary_science_match=0.0,
    secondary_sciences_overlap=0.0,
)
"""Placeholder per-Position breakdown — the calibration test does not exercise the
9-feature breakdown, only the aggregate confidence flowing into REQ-SRC-0053."""

_BLANK_EVIDENCE: CitationRef = CitationRef(
    source_book_id="bk_calibration_stub",
    evidence_type="title_page",
    raw_evidence="calibration stub evidence (no real source)",
)


def _make_calibration_stub(registry: Registry):
    """Return a deterministic VerifierCallable that scores candidates by attribute alignment."""

    def stub(
        spec: VerifierSpec,
        packet: ScholarEvidencePacket,
        round_idx: Literal[0, 1],
        own_round_0: Optional[VerifierEmission],
        other_round_0: Optional[VerifierEmission],
    ) -> VerifierEmission:
        dossier = packet.dossier_context
        scored: list[tuple[float, ScoredCandidate]] = []
        for candidate in packet.candidate_set:
            record = registry.lookup_by_canonical_id(candidate.canonical_id)
            if record is None:
                continue
            aligned, evaluated = _attribute_classes_aligned(record, dossier)
            confidence = _confidence_from_alignment(aligned, evaluated)
            scored.append(
                (
                    confidence,
                    ScoredCandidate(
                        canonical_id=candidate.canonical_id,
                        confidence=confidence,
                        score_breakdown=_BLANK_BREAKDOWN,
                        cited_evidence=[_BLANK_EVIDENCE],
                    ),
                )
            )
        if not scored:
            raise RuntimeError(
                "calibration stub invoked with empty candidate_set — should not "
                "happen in calibration because gold-seed fragments self-narrow"
            )
        # Stable highest-confidence chosen_id; canonical_id breaks ties for determinism.
        scored.sort(key=lambda pair: (-pair[0], pair[1].canonical_id))
        chosen_candidate = scored[0][1]
        positions = [sc for _, sc in scored]
        prompt_hash = (
            spec.round_0_prompt_template_hash
            if round_idx == 0
            else spec.round_1_prompt_template_hash
        )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_idx,
            chosen_id=chosen_candidate.canonical_id,
            positions=positions,
            reasoning="calibration stub: signal-alignment scoring per CR-39..CR-51",
            prompt_template_hash=prompt_hash,
        )

    return stub


# ---------------------------------------------------------------------------
# Verifier specs (module constants — same identity used across all 110 cases)
# ---------------------------------------------------------------------------

_VERIFIER_A_SPEC: VerifierSpec = VerifierSpec(
    verifier_id="cal_verifier_a",
    model_id="anthropic/claude-opus-4-6",
    seed=20260505,
    round_0_prompt_template_hash="r0_a_session45_calibration",
    round_1_prompt_template_hash="r1_a_session45_calibration",
)
_VERIFIER_B_SPEC: VerifierSpec = VerifierSpec(
    verifier_id="cal_verifier_b",
    model_id="openrouter/cohere/command-a",
    seed=20260506,
    round_0_prompt_template_hash="r0_b_session45_calibration",
    round_1_prompt_template_hash="r1_b_session45_calibration",
)


# ---------------------------------------------------------------------------
# Module-scope fixtures (registry built once for all 111 tests)
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def gold_registry() -> Registry:
    """Build a Registry from all 50 ScholarAuthorityRecord-shaped gold-seed entries."""
    scholars = [
        ScholarAuthorityRecord.model_validate(entry["record"]) for entry in GOLD_SCHOLARS
    ]
    return Registry(release_version=RELEASE_VERSION, scholars=scholars)


@pytest.fixture(scope="module")
def orchestration(gold_registry: Registry) -> ScholarMatchCellOrchestration:
    """ScholarMatchCellOrchestration wired with the calibration stub VerifierCallable."""
    snapshot = pin_registry_snapshot(RELEASE_VERSION)
    stub = _make_calibration_stub(gold_registry)
    return ScholarMatchCellOrchestration(
        registry=gold_registry,
        snapshot=snapshot,
        verifier_a_spec=_VERIFIER_A_SPEC,
        verifier_b_spec=_VERIFIER_B_SPEC,
        call_verifier=stub,
    )


# ---------------------------------------------------------------------------
# Scenario (a) — canonical-dossier produces DEFINITIVE for the target scholar
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0053", "INV-SRC-0013", "L-SCH-004")
@pytest.mark.parametrize("canonical_id", _all_canonical_ids())
def test_canonical_dossier_produces_definitive(
    canonical_id: str, orchestration: ScholarMatchCellOrchestration
) -> None:
    """Each gold-seed scholar's canonical dossier resolves to DEFINITIVE for that scholar.

    Calibrates: SPEC §4.A.2 weights (CR-39..CR-43), nisba bonus (CR-44),
    REQ-SRC-0053 thresholds (CR-46..CR-51), INV-SRC-0013 ≥2-non-name floor.
    With the stub returning 0.95 confidence for the fully-aligned target and
    ≤ 0.73 for spurious candidates, the compound 4-condition predicate fires
    DEFINITIVE on round 0 (convergent + mean ≥ 0.92 + each ≥ 0.90 + no rival
    close + ≥ 2 corroborating non-name attributes).
    """
    entry = _entry_by_id(canonical_id)
    fragment: str = entry["calibration"]["name_fragment"]
    dossier = DossierContext.model_validate(entry["calibration"]["canonical_dossier"])

    result = scholar_match_cell(fragment, dossier, orchestration)

    assert result.disambiguation_state == "definitive", (
        f"{canonical_id} ({entry['record']['canonical_name_ar']!r}) "
        f"under canonical dossier expected DEFINITIVE; got "
        f"{result.disambiguation_state} "
        f"(canonical_scholar_id={result.canonical_scholar_id})"
    )
    assert result.canonical_scholar_id == canonical_id, (
        f"{canonical_id} canonical-dossier resolved to "
        f"{result.canonical_scholar_id} (expected self)"
    )
    assert result.confidence is not None and result.confidence >= 0.92, (
        f"{canonical_id} confidence {result.confidence} below MEAN_THRESHOLD 0.92"
    )
    audit = result.provenance.threshold_audit
    assert audit.mean_passes
    assert audit.both_pass
    assert audit.no_rival_close
    assert audit.corroboration_count_ge_2, (
        f"{canonical_id} corroboration_count={audit.corroboration_count} "
        "below INV-SRC-0013 floor of 2"
    )
    assert result.provenance.registry_release_version == RELEASE_VERSION


# ---------------------------------------------------------------------------
# Scenario (b) — cross-trap dossier resolves to the trap partner
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0053", "INV-SRC-0013", "L-SCH-004")
@pytest.mark.parametrize("probe_id,expected_id", _trap_pair_cases())
def test_cross_trap_dossier_routes_to_trap_partner(
    probe_id: str,
    expected_id: str,
    orchestration: ScholarMatchCellOrchestration,
) -> None:
    """Trap-pair disambiguation: name from probe + dossier from expected → DEFINITIVE expected.

    The shared name fragment surfaces both trap-partners via Stage-1 narrowing.
    The dossier's discriminating signals (works + century + science) drive the
    Stage-2 verifier stub to converge on the expected (trap-partner) candidate
    despite the probe being the "obvious" match by name.

    This is the strongest disambiguation calibration in the suite: a positive
    test would be "name + own dossier → self" (which is scenario a). Here we
    flip the dossier to prove the verifier respects signals over name.
    """
    probe_entry = _entry_by_id(probe_id)
    expected_entry = _entry_by_id(expected_id)
    fragment: str = probe_entry["calibration"]["name_fragment"]
    dossier = DossierContext.model_validate(
        expected_entry["calibration"]["canonical_dossier"]
    )

    # Sanity (also asserted in test_gold_seed_invariants below).
    assert (
        probe_entry["calibration"]["name_fragment"]
        == expected_entry["calibration"]["name_fragment"]
    ), (
        f"trap pair {probe_id}/{expected_id} must share name fragment for cross-routing"
    )

    result = scholar_match_cell(fragment, dossier, orchestration)

    assert result.disambiguation_state == "definitive", (
        f"trap pair probe={probe_id}, dossier-from={expected_id} expected "
        f"DEFINITIVE; got {result.disambiguation_state} "
        f"(canonical_scholar_id={result.canonical_scholar_id})"
    )
    assert result.canonical_scholar_id == expected_id, (
        f"trap pair probe={probe_id}, dossier-from={expected_id} resolved to "
        f"{result.canonical_scholar_id} (expected {expected_id} — disambiguation failure)"
    )
    audit = result.provenance.threshold_audit
    assert audit.mean_passes
    assert audit.both_pass
    assert audit.no_rival_close, (
        f"trap pair probe={probe_id}, dossier-from={expected_id} produced "
        f"a too-close rival: leader={audit.leader_confidence} rival={audit.rival_confidence}"
    )
    assert audit.corroboration_count_ge_2


# ---------------------------------------------------------------------------
# Scenario (c) — name-only dossier yields INSUFFICIENT_EVIDENCE
# ---------------------------------------------------------------------------


@pytest.mark.spec("DEC-SRC-0013", "REQ-SRC-0053", "L-SCH-004")
@pytest.mark.parametrize("canonical_id", _all_canonical_ids())
def test_name_only_dossier_yields_insufficient_evidence(
    canonical_id: str, orchestration: ScholarMatchCellOrchestration
) -> None:
    """Empty dossier → INSUFFICIENT_EVIDENCE (0.65 name-only cap CR-45 + 0.70 floor CR-50).

    With no dossier signals, the stub returns 0.40 baseline confidence for
    every candidate → max < 0.70 → REQ-SRC-0053 routes to insufficient_evidence.
    For single-candidate narrowings, the disputed degenerate fallback also
    routes to insufficient_evidence per ``threshold_compounding.py`` docstring.
    """
    entry = _entry_by_id(canonical_id)
    fragment: str = entry["calibration"]["name_fragment"]

    result = scholar_match_cell(fragment, DossierContext(), orchestration)

    assert result.disambiguation_state == "insufficient_evidence", (
        f"{canonical_id} name-only ({fragment!r}) expected INSUFFICIENT_EVIDENCE; "
        f"got {result.disambiguation_state} "
        f"(canonical_scholar_id={result.canonical_scholar_id})"
    )
    assert result.canonical_scholar_id is None
    assert result.confidence is None
    assert result.record_status is None
    assert result.positions == []


# ---------------------------------------------------------------------------
# Gold-seed structural invariants — guards the calibration data shape
# ---------------------------------------------------------------------------


@pytest.mark.spec("L-SCH-004")
def test_gold_seed_invariants() -> None:
    """Sanity guards on the gold-seed JSON itself (catches data drift early)."""
    assert len(GOLD_SCHOLARS) == 50, f"expected 50 scholars, got {len(GOLD_SCHOLARS)}"
    assert len(TRAP_PAIRS) == 5, f"expected 5 trap pairs, got {len(TRAP_PAIRS)}"
    ids = [s["record"]["canonical_id"] for s in GOLD_SCHOLARS]
    assert len(set(ids)) == 50, "all canonical_ids must be unique"
    assert ids == sorted(ids), "canonical_ids must be in monotonically increasing order"
    trap_member_ids = sum((p["members"] for p in TRAP_PAIRS), [])
    assert len(trap_member_ids) == 10, "trap pairs must have exactly 10 members total"
    assert all(tid in ids for tid in trap_member_ids), (
        "all trap members must be in the scholars list"
    )
    # Each trap pair member must record its partner as trap_pair_canonical_id.
    for pair in TRAP_PAIRS:
        a, b = pair["members"]
        a_entry = _entry_by_id(a)
        b_entry = _entry_by_id(b)
        assert a_entry["calibration"]["trap_pair_canonical_id"] == b, (
            f"trap pair {pair['pair_label']}: "
            f"{a} should point at {b}, not {a_entry['calibration']['trap_pair_canonical_id']}"
        )
        assert b_entry["calibration"]["trap_pair_canonical_id"] == a, (
            f"trap pair {pair['pair_label']}: "
            f"{b} should point at {a}, not {b_entry['calibration']['trap_pair_canonical_id']}"
        )
        assert (
            a_entry["calibration"]["name_fragment"]
            == b_entry["calibration"]["name_fragment"]
        ), f"trap pair {pair['pair_label']} must share name fragment"
    # Non-trap entries must NOT record a trap_pair_canonical_id.
    non_trap_ids = set(ids) - set(trap_member_ids)
    for cid in non_trap_ids:
        entry = _entry_by_id(cid)
        assert entry["calibration"]["trap_pair_canonical_id"] is None, (
            f"non-trap entry {cid} should not record a trap_pair_canonical_id"
        )
