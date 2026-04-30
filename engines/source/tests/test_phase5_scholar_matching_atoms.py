"""Spec-content tests for Phase 5 scholar-matching atoms.

Phase 5 (cross-provider DR synthesis 2026-04-30) introduces the OPT-4
scholar-matching architecture. Stage 4 (this Stage) writes 12 new atoms +
6 amendments to existing atoms. Implementation lands in a separate
session per compaction discipline.

These tests validate the SPEC-LAYER content — every AC declared in the
synthesis lands in a YAML atom and the load-bearing semantics are
preserved. Phase 5 implementation (next session) will extend these tests
with behavior-layer assertions that exercise scholar-matching code.

Test naming convention: each test function carries
`@pytest.mark.spec("ATOM-ID", "AC-N")` so future implementation tests
extend the same surface.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
import yaml


PROJECT_ROOT = Path(__file__).resolve().parents[3]
SPEC_ROOT = PROJECT_ROOT / "engines" / "source" / "spec"


def _load(rel: str) -> dict[str, Any]:
    """Load a YAML atom by repo-relative path under the source spec tree."""
    text = (SPEC_ROOT / rel).read_text(encoding="utf-8")
    data = yaml.safe_load(text)
    assert isinstance(data, dict), f"{rel} did not load as a dict"
    return data


def _ac(atom: dict[str, Any], ac_id: str) -> dict[str, Any]:
    """Find an acceptance criterion by id within an atom."""
    for criterion in atom.get("acceptance_criteria", []):
        if criterion.get("id") == ac_id:
            return criterion
    raise AssertionError(
        f"Atom {atom.get('id')} has no acceptance criterion with id={ac_id}"
    )


# ---------------------------------------------------------------------------
# 12 new atoms — load-bearing content tests
# ---------------------------------------------------------------------------


@pytest.mark.spec("INV-SRC-0013", "AC-1")
def test_inv_0013_two_non_name_floor_pass() -> None:
    """≥2 non-name attributes intersecting → definitive permitted."""
    atom = _load("40-quality/invariants/INV-SRC-0013.yaml")
    assert atom["id"] == "INV-SRC-0013"
    assert atom["type"] == "invariant"
    assert atom["rule"]["violation_severity"] == "critical"
    ac1 = _ac(atom, "AC-1")
    assert "أبو حنيفة" in ac1["given"]
    assert "≥2" in ac1["then"] or "3 non-name" in ac1["then"]


@pytest.mark.spec("INV-SRC-0013", "AC-2")
def test_inv_0013_two_non_name_floor_fail() -> None:
    """1 non-name attribute → definitive REJECTED."""
    atom = _load("40-quality/invariants/INV-SRC-0013.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "REJECTED" in ac2["then"]
    assert "corroboration_count_ge_2 = false" in ac2["then"]


@pytest.mark.spec("INV-SRC-0013", "AC-3")
def test_inv_0013_name_expansion_not_corroboration() -> None:
    """Name expansion (full nasab + nisba) does NOT count toward ≥2 floor."""
    atom = _load("40-quality/invariants/INV-SRC-0013.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "Name expansion" in ac3["then"]
    assert "NOT eligible corroboration" in ac3["then"]


@pytest.mark.spec("INV-SRC-0014", "AC-2")
def test_inv_0014_bidi_strip_ordering() -> None:
    """Bidi-mark contamination handled by strip ordering BEFORE honorific."""
    atom = _load("40-quality/invariants/INV-SRC-0014.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "U+200E" in ac2["given"]
    assert "Stage 1 strips U+200E" in ac2["then"]
    # Ordering: bidi-strip → honorific → match-key
    statement = atom["rule"]["statement"]
    assert "U+200E" in statement
    assert "U+200F" in statement
    # Carve-outs documented
    assert "Persian/Urdu/Kurdish" in statement


@pytest.mark.spec("INV-SRC-0014", "AC-3")
def test_inv_0014_honorific_only_aborts() -> None:
    """Honorific-shell input aborts with existing SRC-E-HONORIFIC-ONLY-NAME."""
    atom = _load("40-quality/invariants/INV-SRC-0014.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "SRC-E-HONORIFIC-ONLY-NAME" in ac3["then"]
    assert "F-6" in ac3["then"]


@pytest.mark.spec("REQ-SRC-0049", "AC-3")
def test_req_0049_snapshot_drift_explicit_replay() -> None:
    """Mid-pipeline snapshot drift triggers EXPLICIT REPLAY, not silent reroll."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0049.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "EXPLICIT REPLAY" in ac3["then"]
    assert "SRC-E-REGISTRY-SNAPSHOT-DRIFT" in ac3["then"]
    # Codex Defect 2 fix: registry_release_version is canonical name
    assert "registry_release_version" in atom["source"]


@pytest.mark.spec("REQ-SRC-0049", "AC-4")
def test_req_0049_runtime_external_rejected() -> None:
    """Runtime external call attempt during locked case is REJECTED."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0049.yaml")
    ac4 = _ac(atom, "AC-4")
    assert "SRC-E-RUNTIME-EXTERNAL" in ac4["then"]


@pytest.mark.spec("REQ-SRC-0050", "AC-2")
def test_req_0050_compound_name_preservation() -> None:
    """عبد + divine attribute preserved as single token (F-5 closure)."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0050.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "عبد الله" in ac2["given"]
    assert "compound preserved" in ac2["then"]
    assert "SRC-E-COMPOUND-NAME-SPLIT" in ac2["then"]


@pytest.mark.spec("REQ-SRC-0050", "AC-4")
def test_req_0050_honorific_only_routes_to_existing_error() -> None:
    """Honorific-shell input aborts with existing SRC-E-HONORIFIC-ONLY-NAME."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0050.yaml")
    ac4 = _ac(atom, "AC-4")
    assert "SRC-E-HONORIFIC-ONLY-NAME" in ac4["then"]


@pytest.mark.spec("CON-SRC-0009", "AC-3")
def test_con_0009_f4_closure_via_packet_immutability() -> None:
    """A round-1 chosen_id outside the locked candidate_set is rejected."""
    atom = _load("20-contracts/constraints/CON-SRC-0009.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "INV-SRC-0016" in ac3["then"]
    assert "REJECTED" in ac3["then"] or "rejected" in ac3["then"]
    assert "Hallucinated" in ac3["then"] or "hallucination" in ac3["then"].lower()


@pytest.mark.spec("CON-SRC-0009", "AC-4")
def test_con_0009_snapshot_version_field_forbidden() -> None:
    """snapshot_version field name is REJECTED at contract layer."""
    atom = _load("20-contracts/constraints/CON-SRC-0009.yaml")
    ac4 = _ac(atom, "AC-4")
    assert "snapshot_version" in ac4["given"]
    assert "REJECTED" in ac4["then"]
    assert "registry_release_version" in ac4["then"]


@pytest.mark.spec("REQ-SRC-0051", "AC-1")
def test_req_0051_work_title_channel_promotes_when_unique() -> None:
    """List-size 1 (≤N=3) promotes work-title to Stage-1 deterministic narrowing."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0051.yaml")
    ac1 = _ac(atom, "AC-1")
    assert "بدائع الصنائع" in ac1["given"]
    assert "list size = 1" in ac1["then"]
    assert "Stage-1 deterministic narrowing" in ac1["then"]


@pytest.mark.spec("REQ-SRC-0051", "AC-2")
def test_req_0051_work_title_list_size_guard_n3() -> None:
    """List-size > N=3 reverts work-title channel to Stage-2 scoring only.

    arabic-reviewer Stage-3 Defect 5 (list-size guard).
    """
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0051.yaml")
    ac2 = _ac(atom, "AC-2")
    # Polysemic work-title token surfaces > N=3 candidates
    assert "مختصر" in ac2["given"]
    assert "size 7" in ac2["then"]
    assert "REVERTS to Stage-2" in ac2["then"]
    # Confirm guard semantics in atom postconditions
    postconditions = atom["behavior"]["postconditions"]
    found_guard = any(
        "list-size guard" in p and "N = 3" in p for p in postconditions
    )
    assert found_guard, "work-title list-size guard N=3 missing from postconditions"


@pytest.mark.spec("REQ-SRC-0051", "AC-3")
def test_req_0051_compound_title_decomposition() -> None:
    """شرح صحيح مسلم → narrows on both sharh author AND base-work author.

    arabic-reviewer Stage-3 Novel Finding 3 (compound-title decomposition).
    """
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0051.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "شرح صحيح مسلم" in ac3["given"]
    assert "Compound-title decomposition" in ac3["then"]
    assert "al-Nawawī" in ac3["then"]
    assert "Muslim ibn al-Hajjāj" in ac3["then"]


@pytest.mark.spec("REQ-SRC-0051", "AC-4")
def test_req_0051_taa_marbuta_persian_preservation() -> None:
    """taa-marbuta + Persian/Urdu chars PRESERVED in work-title normalization.

    arabic-reviewer Stage-3 Novel Finding 2 (work-title normalization spec).
    """
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0051.yaml")
    ac4 = _ac(atom, "AC-4")
    # Persian گ (U+06AF) preserved
    assert "U+06AF" in ac4["then"] or "Persian گ" in ac4["then"]
    # taa-marbuta preserved
    assert "taa-marbuta is\n        also preserved" in ac4["then"] or (
        "الفتوحات stays الفتوحات" in ac4["then"]
    )
    # Confirm FORBIDDEN normalizations in postconditions
    postconditions = atom["behavior"]["postconditions"]
    found_forbidden = any(
        "FORBIDDEN taa-marbuta normalization" in p
        for p in postconditions
    )
    assert found_forbidden, (
        "FORBIDDEN taa-marbuta normalization clause missing"
    )
    found_persian = any(
        "U+067E" in p and "U+06AF" in p
        for p in postconditions
    )
    assert found_persian, (
        "FORBIDDEN Persian/Urdu/Kurdish character normalization clause missing"
    )


@pytest.mark.spec("CON-SRC-0008", "AC-4")
def test_con_0008_dual_state_surface() -> None:
    """definitive (3-state) against provisional (5-state) record both surface."""
    atom = _load("20-contracts/constraints/CON-SRC-0008.yaml")
    ac4 = _ac(atom, "AC-4")
    assert "أحمد بن حنبل" in ac4["given"]
    assert 'disambiguation_state="definitive"' in ac4["then"]
    assert 'record_status=\n        "provisional"' in ac4["then"] or (
        '"provisional"' in ac4["then"]
    )


@pytest.mark.spec("CON-SRC-0008", "AC-5")
def test_con_0008_snapshot_version_forbidden_at_result() -> None:
    """snapshot_version field is REJECTED at the result contract layer."""
    atom = _load("20-contracts/constraints/CON-SRC-0008.yaml")
    ac5 = _ac(atom, "AC-5")
    assert "snapshot_version" in ac5["given"]
    assert "REJECTED" in ac5["then"]


@pytest.mark.spec("INV-SRC-0016", "AC-3")
def test_inv_0016_coordinated_hallucination_rejected() -> None:
    """Both verifiers agreeing on hallucinated id is NOT definitive."""
    atom = _load("40-quality/invariants/INV-SRC-0016.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "BOTH outputs are REJECTED" in ac3["then"]
    assert "agreement on hallucination" in ac3["then"]


@pytest.mark.spec("REQ-SRC-0052", "AC-1")
def test_req_0052_round_0_convergence_definitive() -> None:
    """Round-0 5-condition convergence triggers DEFINITIVE without round-1."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0052.yaml")
    ac1 = _ac(atom, "AC-1")
    assert "DEFINITIVE" in ac1["then"]
    assert "Round-1 is NOT triggered" in ac1["then"]
    assert "round_count=1" in ac1["then"]


@pytest.mark.spec("REQ-SRC-0052", "AC-2")
def test_req_0052_round_1_adversarial_scaffold() -> None:
    """Round-1 uses adversarial scaffold (defend / attack) on UNCHANGED packet."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0052.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "defend" in ac2["then"].lower()
    assert "attack" in ac2["then"].lower()
    assert "UNCHANGED CON-SRC-0009 packet" in ac2["then"]


@pytest.mark.spec("INV-SRC-0015", "AC-3")
def test_inv_0015_snapshot_version_forbidden_in_provenance() -> None:
    """snapshot_version forbidden in provenance per Codex Defect 2 fix."""
    atom = _load("40-quality/invariants/INV-SRC-0015.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "snapshot_version" in ac3["given"]
    assert "registry_release_version" in ac3["then"]


@pytest.mark.spec("INV-SRC-0017", "AC-2")
def test_inv_0017_re_attribution_explicit_replay() -> None:
    """Re-attribution against newer release is EXPLICIT REPLAY, preserves prior verdict."""
    atom = _load("40-quality/invariants/INV-SRC-0017.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "revision_history" in ac2["then"]
    assert "Critical Rule 13" in ac2["then"]


@pytest.mark.spec("REQ-SRC-0053", "AC-2")
def test_req_0053_each_ge_090_guard() -> None:
    """One strong verifier cannot carry a weak verifier across the line."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0053.yaml")
    ac2 = _ac(atom, "AC-2")
    assert "(0.99, 0.89)" in ac2["given"]
    assert "DISPUTED" in ac2["then"]
    assert "both_pass=false" in ac2["then"]


@pytest.mark.spec("REQ-SRC-0053", "AC-3")
def test_req_0053_no_rival_within_007_guard() -> None:
    """Rival within 0.07 of leader → DISPUTED (textbook ambiguous case)."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0053.yaml")
    ac3 = _ac(atom, "AC-3")
    assert "DISPUTED" in ac3["then"]
    assert "no_rival_close=false" in ac3["then"]


@pytest.mark.spec("REQ-SRC-0053", "AC-5")
def test_req_0053_partition_gap_closed() -> None:
    """The previously-under-specified [0.05, 0.07) gap is now closed.

    Codex Stage-3 Defect 1 reconciliation: disputed routing widened to 0.07.
    """
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0053.yaml")
    ac5 = _ac(atom, "AC-5")
    assert "[0.05, 0.07)" in ac5["given"] or "[0.05, 0.07)" in ac5["then"]
    assert "DISPUTED" in ac5["then"]
    assert "Codex Defect 1 reconciliation" in ac5["then"]


@pytest.mark.spec("REQ-SRC-0053", "AC-7")
def test_req_0053_round_1_disagreement_routes_disputed() -> None:
    """verifiers diverge after round-1 → DISPUTED (round cap = 2 holds)."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0053.yaml")
    ac7 = _ac(atom, "AC-7")
    assert "DISPUTED" in ac7["then"]
    assert "verifier_disagreement=true" in ac7["then"]


# ---------------------------------------------------------------------------
# 6 amendments to existing atoms — verify Phase 5 amendment language landed
# ---------------------------------------------------------------------------


@pytest.mark.spec("REQ-SRC-0008", "AC-amendment")
def test_req_0008_phase5_scholar_match_cell_specialization() -> None:
    """REQ-SRC-0008 amended with scholar_match_cell specialization clause."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0008.yaml")
    assert atom["updated"] == "2026-04-30"
    # New depends_on for Phase 5
    assert "CON-SRC-0008" in atom["depends_on"]
    assert "CON-SRC-0009" in atom["depends_on"]
    assert "INV-SRC-0016" in atom["depends_on"]
    # Postconditions carry scholar_match_cell specialization
    postconditions = atom["behavior"]["postconditions"]
    found = any(
        "scholar_match_cell" in p and "round-cap = 2" in p
        for p in postconditions
    )
    assert found, "scholar_match_cell specialization missing"


@pytest.mark.spec("REQ-SRC-0028", "AC-amendment")
def test_req_0028_phase5_partial_fragment_routing() -> None:
    """REQ-SRC-0028 amended with partial_fragment_author_identity routing."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0028.yaml")
    assert atom["updated"] == "2026-04-30"
    assert "INV-SRC-0013" in atom["depends_on"]
    assert "REQ-SRC-0049" in atom["depends_on"]
    postconditions = atom["behavior"]["postconditions"]
    found = any(
        "partial_fragment_author_identity" in p
        for p in postconditions
    )
    assert found, "partial_fragment_author_identity routing missing"


@pytest.mark.spec("REQ-SRC-0035", "AC-amendment")
def test_req_0035_phase5_dispute_panel_tightened() -> None:
    """REQ-SRC-0035 amended with TIGHTENED dispute_panel binding to scholar_match_result."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0035.yaml")
    assert atom["updated"] == "2026-04-30"
    assert "CON-SRC-0008" in atom["depends_on"]
    postconditions = atom["behavior"]["postconditions"]
    found = any(
        "scholar_match_result" in p
        and "scholar-dependent display fields" in p
        for p in postconditions
    )
    assert found, "TIGHTENED dispute_panel binding missing"


@pytest.mark.spec("REQ-SRC-0042", "AC-amendment-LOAD-BEARING")
def test_req_0042_phase5_runtime_external_removed() -> None:
    """REQ-SRC-0042 LOAD-BEARING amendment: tier-2 RUNTIME lookup REMOVED."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0042.yaml")
    assert atom["updated"] == "2026-04-30"
    assert "REQ-SRC-0049" in atom["depends_on"]
    postconditions = atom["behavior"]["postconditions"]
    # Tier-2 runtime lookup forbidden
    found_removed = any(
        "REMOVED" in p and "runtime external lookup is FORBIDDEN" in p
        for p in postconditions
    )
    assert found_removed, "Tier-2 RUNTIME lookup NOT marked REMOVED"
    # Build-time enrichment lane authorized
    found_buildtime = any(
        "Build-time enrichment lane" in p and "OpenITI metadata (offline TSV" in p
        for p in postconditions
    )
    assert found_buildtime, "Build-time enrichment lane missing"


@pytest.mark.spec("REQ-SRC-0043", "AC-amendment")
def test_req_0043_phase5_provisional_only_on_no_match() -> None:
    """REQ-SRC-0043 amended: provisional registration ONLY after match cell concludes new-scholar."""
    atom = _load("10-pipeline/50-metadata-deliberation/REQ-SRC-0043.yaml")
    assert atom["updated"] == "2026-04-30"
    assert "CON-SRC-0008" in atom["depends_on"]
    assert "INV-SRC-0013" in atom["depends_on"]
    preconditions = atom["behavior"]["preconditions"]
    found = any(
        "disambiguation_state=insufficient_evidence" in p
        and "disputed terminal does NOT permit provisional registration" in p
        for p in preconditions
    )
    assert found, "Provisional-only-on-no-match precondition missing"


@pytest.mark.spec("DEC-SRC-0013", "AC-amendment")
def test_dec_0013_phase5_named_cell_pattern() -> None:
    """DEC-SRC-0013 amended: scholar_match_cell as second NAMED cell pattern."""
    atom = _load("30-architecture/decisions/DEC-SRC-0013.yaml")
    assert atom["updated"] == "2026-04-30"
    chosen = next(
        opt for opt in atom["options"] if opt["status"] == "chosen"
    )
    assert "scholar_match_cell" in chosen["description"]
    assert "scholar_match_cell" in chosen["chosen_reason"]
    assert "EXTENSIBLE" in chosen["chosen_reason"]


# ---------------------------------------------------------------------------
# Cross-cutting structural tests — INDEX consistency + dependency graph
# ---------------------------------------------------------------------------


def test_phase5_atoms_in_index() -> None:
    """All 12 new Phase 5 atoms are registered in INDEX.yaml."""
    index = yaml.safe_load(
        (SPEC_ROOT / "INDEX.yaml").read_text(encoding="utf-8")
    )
    ids = {entry["id"] for entry in index["atoms"]}
    expected = {
        "INV-SRC-0013", "INV-SRC-0014", "INV-SRC-0015", "INV-SRC-0016",
        "INV-SRC-0017", "REQ-SRC-0049", "REQ-SRC-0050", "REQ-SRC-0051",
        "REQ-SRC-0052", "REQ-SRC-0053", "CON-SRC-0008", "CON-SRC-0009",
    }
    missing = expected - ids
    assert not missing, f"Phase 5 atoms missing from INDEX: {missing}"


def test_phase5_atom_dependency_graph_acyclic() -> None:
    """The Phase 5 12-atom dependency subgraph is acyclic (producer-before-consumer)."""
    phase5 = [
        "INV-SRC-0013", "INV-SRC-0014", "INV-SRC-0015", "INV-SRC-0016",
        "INV-SRC-0017", "REQ-SRC-0049", "REQ-SRC-0050", "REQ-SRC-0051",
        "REQ-SRC-0052", "REQ-SRC-0053", "CON-SRC-0008", "CON-SRC-0009",
    ]
    deps: dict[str, set[str]] = {}
    for atom_id in phase5:
        index = yaml.safe_load(
            (SPEC_ROOT / "INDEX.yaml").read_text(encoding="utf-8")
        )
        entry = next(e for e in index["atoms"] if e["id"] == atom_id)
        atom = _load(entry["file"])
        deps[atom_id] = {d for d in atom.get("depends_on", []) if d in phase5}

    visited: set[str] = set()
    visiting: set[str] = set()

    def dfs(node: str) -> None:
        if node in visited:
            return
        if node in visiting:
            raise AssertionError(
                f"Cycle detected in Phase 5 dependency graph at {node}"
            )
        visiting.add(node)
        for dep in deps.get(node, set()):
            dfs(dep)
        visiting.remove(node)
        visited.add(node)

    for node in phase5:
        dfs(node)


def test_phase5_canonical_field_naming_uniform() -> None:
    """registry_release_version is the canonical field name across all Phase 5 atoms.

    Codex Stage-3 Defect 2 fix: snapshot_version is FORBIDDEN as a field name
    everywhere it could appear (REQ-SRC-0049 + CON-SRC-0008 + CON-SRC-0009 +
    INV-SRC-0015 + INV-SRC-0017). This test verifies the canonical name is
    referenced uniformly and that snapshot_version appears only in
    rejection-context (the FORBIDDEN clauses).
    """
    files = [
        "10-pipeline/50-metadata-deliberation/REQ-SRC-0049.yaml",
        "20-contracts/constraints/CON-SRC-0008.yaml",
        "20-contracts/constraints/CON-SRC-0009.yaml",
        "40-quality/invariants/INV-SRC-0015.yaml",
        "40-quality/invariants/INV-SRC-0017.yaml",
    ]
    for rel in files:
        text = (SPEC_ROOT / rel).read_text(encoding="utf-8")
        # Canonical name appears
        assert "registry_release_version" in text, (
            f"{rel} does not reference canonical registry_release_version"
        )
        # snapshot_version, if present, appears only in FORBIDDEN context
        if "snapshot_version" in text:
            assert "FORBIDDEN" in text, (
                f"{rel} mentions snapshot_version outside FORBIDDEN context"
            )
