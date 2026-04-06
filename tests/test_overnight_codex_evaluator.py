"""Tests for the deterministic creative output evaluator.

v2: hardened per ChatGPT DR audit (2026-04-06). Includes 3 adversarial bypass
payloads from the DR report that must REJECT, plus updated assertions for
eliminated provisional verdict and raised PASS thresholds.

Reference: docs/codex/2026-04-03-golden-example-multiresolution-digester.md
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts import overnight_codex_evaluator as evaluator
from scripts.overnight_codex_evaluator import (
    DimensionResult,
    EvaluationResult,
    check_concreteness,
    check_evidence_fidelity,
    check_inflation,
    check_repo_grounding,
    check_strategic_depth,
    check_structural_completeness,
    evaluate_creative_output,
    format_findings_entry,
    route_to_findings,
    save_evaluation_result,
)


# ---------------------------------------------------------------------------
# Synthetic payloads
# ---------------------------------------------------------------------------

def golden_grade_payload() -> dict:
    """A payload modeled on the golden multiresolution digester example.

    v2: fixed TaxonomyNode → TreeNode (actual class name per contracts.py).
    """
    return {
        "current_system_limit": (
            "The excerpting engine emits only terminal-leaf ExcerptRecord objects. "
            "Taxonomy places these at leaf nodes only. Coarser structural units "
            "(chapters, sections) from normalization are discarded after excerpting "
            "flattens them into fine-grained teaching units. The owner cannot "
            "navigate from a high-level topic overview down to a specific excerpt "
            "because intermediate levels do not retain content."
        ),
        "proposed_reframe": (
            "Build a multiresolution book digester instead of a book excerpter. "
            "Every level of the knowledge tree retains content at progressively "
            "finer granularity. Science-level nodes retain full books, lower nodes "
            "retain chapters, deeper nodes retain subchapters, and terminal leaves "
            "retain the finest-grained excerpts. This transforms KR from a "
            "flat excerpt store into a zoomable scholarly knowledge surface where "
            "the owner can study at any resolution level."
        ),
        "primary_insertion_boundary": (
            "excerpting Phase 2b → Phase 3/output boundary, where semantic "
            "granularity is chosen before it is flattened into ExcerptRecord"
        ),
        "secondary_required_changes": [
            "engines/taxonomy/contracts.py — extend TreeNode to hold content at branch nodes",
            "engines/synthesis/contracts.py — consume multi-resolution content instead of leaf-only",
            "engines/normalization/SPEC.md — preserve division-tree depth in output for downstream use",
        ],
        "owner_value_statement": (
            "The owner can study any topic at the resolution that matches his "
            "current need — a quick overview, a chapter-level read, or a deep "
            "dive into specific scholarly points — all from the same knowledge tree."
        ),
        "benefits": [
            "Transforms KR from excerpt-only retrieval to full scholarly navigation with zoom",
            "Preserves normalization's structural richness instead of flattening it away",
            "Makes the taxonomy tree useful for browsing at every level, not just routing to leaves",
            "Enables study workflows that match how Islamic scholars traditionally organize knowledge",
        ],
        "risks": [
            "Taxonomy contract change requires rethinking branch-node placement logic which currently assumes content-free routing",
            "Storage footprint grows because every tree level retains content instead of only leaves",
            "Deduplication complexity increases when the same text appears at multiple resolution levels with different granularity",
        ],
        "benchmark_scores": {
            "product_reframing": 4,
            "live_system_contrast": 4,
            "primary_boundary_accuracy": 4,
            "latent_ingredient_leverage": 3,
            "invariant_coverage": 3,
            "owner_value": 4,
            "autonomous_originality": 3,
            "evaluability": 3,
        },
        "coworker_verdicts": [],
    }


def weak_payload() -> dict:
    """A payload that looks structured but is shallow."""
    return {
        "current_system_limit": "The system uses JSON for storage.",
        "proposed_reframe": "Use YAML instead of JSON for better readability.",
        "primary_insertion_boundary": "the storage layer",
        "secondary_required_changes": ["change file extension"],
        "owner_value_statement": "Files will be easier to read.",
        "benefits": [
            "YAML is more readable",
            "YAML supports comments",
            "YAML is widely used",
        ],
        "risks": [
            "May require refactoring",
            "Could be complex",
            "Might need more work",
        ],
        "benchmark_scores": {
            "product_reframing": 4,
            "live_system_contrast": 4,
            "primary_boundary_accuracy": 4,
            "latent_ingredient_leverage": 4,
            "invariant_coverage": 4,
            "owner_value": 4,
            "autonomous_originality": 4,
            "evaluability": 4,
        },
        "coworker_verdicts": [],
    }


def partial_payload() -> dict:
    """A payload that has some depth but fails on grounding."""
    return {
        "current_system_limit": (
            "The excerpting engine produces fine-grained teaching units but "
            "loses the surrounding scholarly context that would help the owner "
            "understand why an excerpt matters."
        ),
        "proposed_reframe": (
            "Attach contextual metadata to every excerpt that preserves the "
            "surrounding scholarly argument structure — what came before, what "
            "the author is responding to, and what follows. This transforms "
            "isolated excerpts into positioned knowledge fragments."
        ),
        "primary_insertion_boundary": "somewhere in the enrichment phase",
        "secondary_required_changes": [
            "update the output format",
        ],
        "owner_value_statement": (
            "The owner can study each excerpt in the context of its scholarly "
            "argument, not as an isolated fragment."
        ),
        "benefits": [
            "Excerpts become self-contextualizing for study purposes",
            "The owner understands not just what the author said but why",
            "Cross-references between related excerpts become navigable",
        ],
        "risks": [
            "Context window limits may prevent capturing full surrounding argument in LLM calls",
            "Defining the boundary of relevant context is a domain judgment call",
            "Storage footprint increases with contextual metadata per excerpt",
        ],
        "benchmark_scores": {
            "product_reframing": 3,
            "live_system_contrast": 3,
            "primary_boundary_accuracy": 2,
            "latent_ingredient_leverage": 3,
            "invariant_coverage": 2,
            "owner_value": 3,
            "autonomous_originality": 3,
            "evaluability": 2,
        },
        "coworker_verdicts": [],
    }


# ---------------------------------------------------------------------------
# DR adversarial bypass payloads (must all REJECT after hardening)
# ---------------------------------------------------------------------------

def bypass_a_payload() -> dict:
    """DR Bypass A: 'Granularity Tagging Layer' — contract field + propagation."""
    return {
        "current_system_limit": (
            "Excerpting currently collapses rich structural context into "
            "ExcerptRecord, making it hard to represent what level of structural "
            "unit this excerpt came from across taxonomy and synthesis."
        ),
        "proposed_reframe": (
            "Introduce a granularity annotation carried alongside TeachingUnit "
            "to ExcerptRecord so that downstream engines treat excerpts differently "
            "based on their structural origin level."
        ),
        "primary_insertion_boundary": (
            "engines/excerpting/contracts.py at the Phase 2b to Phase 3/output "
            "boundary where TeachingUnit flattens to ExcerptRecord"
        ),
        "secondary_required_changes": [
            "engines/excerpting/contracts.py — carry granularity hint from Phase 2b into Phase 3 output",
            "engines/taxonomy/contracts.py — read hint to adjust placement confidence",
            "engines/synthesis/contracts.py — treat coarser excerpts as overview candidates",
        ],
        "owner_value_statement": (
            "The owner can study and navigate more efficiently because the system "
            "signals the right resolution level for each excerpt."
        ),
        "benefits": [
            "Enables multi-resolution readiness without a full architecture change right now",
            "Preserves structural origin information that is currently lost during flattening",
            "Allows taxonomy to make smarter placement decisions based on granularity hints",
        ],
        "risks": [
            "This introduces backward-compat concerns for stored excerpt JSON and downstream consumers",
            "Storage footprint grows slightly from additional metadata per excerpt record",
            "Requires careful migration planning for existing processed books in the pipeline",
        ],
        "benchmark_scores": {
            "product_reframing": 3,
            "live_system_contrast": 3,
            "primary_boundary_accuracy": 3,
            "latent_ingredient_leverage": 3,
            "invariant_coverage": 3,
            "owner_value": 3,
            "autonomous_originality": 3,
            "evaluability": 3,
        },
        "coworker_verdicts": [],
    }


def bypass_b_payload() -> dict:
    """DR Bypass B: 'Provenance Ledger Unification' — observability + hashing."""
    return {
        "current_system_limit": (
            "Cross-engine provenance of excerpt placements is not consistently "
            "inspectable across excerpting to taxonomy to synthesis, causing study "
            "trust issues when something looks wrong."
        ),
        "proposed_reframe": (
            "Build a scholarly provenance ledger with content hashes, lineage ids, "
            "and stage stamps that flows across engine boundaries so the owner "
            "can audit any excerpt's journey through the pipeline."
        ),
        "primary_insertion_boundary": (
            "normalization to excerpting contract boundary and excerpting "
            "Phase 3/output boundary"
        ),
        "secondary_required_changes": [
            "engines/excerpting/contracts.py — add lineage hash to ExcerptRecord output",
            "engines/taxonomy/contracts.py — preserve and validate lineage through placement",
            "shared/validation/src/ — add cross-engine provenance validation helper",
        ],
        "owner_value_statement": (
            "The owner can study with full trust because every excerpt's scholarly "
            "journey is auditable and transparent from normalization to final entry."
        ),
        "benefits": [
            "Every excerpt carries verifiable provenance from source through final placement",
            "The owner gains confidence in excerpt integrity through transparent audit trails",
            "Cross-engine bugs become traceable to the exact pipeline stage where corruption occurred",
        ],
        "risks": [
            "This introduces backward-compat concerns for existing stored excerpt data formats",
            "Storage footprint grows from additional provenance metadata per excerpt and placement",
            "Requires careful migration planning for the existing pipeline output archives",
        ],
        "benchmark_scores": {
            "product_reframing": 3,
            "live_system_contrast": 3,
            "primary_boundary_accuracy": 3,
            "latent_ingredient_leverage": 3,
            "invariant_coverage": 3,
            "owner_value": 3,
            "autonomous_originality": 3,
            "evaluability": 3,
        },
        "coworker_verdicts": [],
    }


def bypass_c_payload() -> dict:
    """DR Bypass C: 'Taxonomy Placement Accelerator' — caching + heuristics."""
    return {
        "current_system_limit": (
            "Taxonomy placement latency and inconsistency slows the study experience "
            "when the owner navigates between excerpting output and taxonomy tree "
            "placement across different science domains."
        ),
        "proposed_reframe": (
            "Transform taxonomy into an interactive study router by introducing a "
            "two-stage placement cache: deterministic pre-filter plus memoized leaf "
            "scoring that lets the owner study faster through instant navigation."
        ),
        "primary_insertion_boundary": (
            "engines/taxonomy/contracts.py at the placement routing boundary "
            "where excerpts are matched to TreeNode leaves"
        ),
        "secondary_required_changes": [
            "engines/taxonomy/contracts.py — add caching layer to placement logic",
            "engines/excerpting/contracts.py — pre-compute placement hints during enrichment",
        ],
        "owner_value_statement": (
            "The owner can study and navigate the knowledge tree instantly without "
            "waiting for placement computation to complete."
        ),
        "benefits": [
            "Placement latency drops from seconds to milliseconds through deterministic caching",
            "The owner gets instant feedback when navigating between topics and sciences",
            "Repeated placement queries for the same leaf path are memoized across sessions",
        ],
        "risks": [
            "This introduces backward-compat concerns for existing taxonomy placement state",
            "Storage footprint grows from the persistent cache layer and memoization tables",
            "Requires careful migration planning for cached state invalidation on tree evolution",
        ],
        "benchmark_scores": {
            "product_reframing": 3,
            "live_system_contrast": 3,
            "primary_boundary_accuracy": 3,
            "latent_ingredient_leverage": 3,
            "invariant_coverage": 3,
            "owner_value": 3,
            "autonomous_originality": 3,
            "evaluability": 3,
        },
        "coworker_verdicts": [],
    }


# ---------------------------------------------------------------------------
# Tests: check_repo_grounding (v2: threshold raised to 3)
# ---------------------------------------------------------------------------

class TestRepoGrounding:
    def test_golden_payload_grounds_to_real_engines(self) -> None:
        result = check_repo_grounding(golden_grade_payload())
        assert result.passed
        assert result.score >= 3

    def test_weak_payload_fails_grounding(self) -> None:
        result = check_repo_grounding(weak_payload())
        assert not result.passed
        assert result.score <= 1

    def test_boundary_with_known_pattern(self) -> None:
        payload = {"primary_insertion_boundary": "excerpting Phase 2b -> Phase 3",
                   "secondary_required_changes": [], "current_system_limit": ""}
        result = check_repo_grounding(payload)
        assert "matches known pattern" in result.details or "resolves" in result.details


# ---------------------------------------------------------------------------
# Tests: check_structural_completeness
# ---------------------------------------------------------------------------

class TestStructuralCompleteness:
    def test_golden_payload_passes(self) -> None:
        result = check_structural_completeness(golden_grade_payload())
        assert result.passed
        assert result.score >= 3

    def test_weak_payload_fails(self) -> None:
        result = check_structural_completeness(weak_payload())
        assert not result.passed

    def test_empty_payload_fails(self) -> None:
        result = check_structural_completeness({})
        assert not result.passed
        assert result.score == 0


# ---------------------------------------------------------------------------
# Tests: check_strategic_depth (v2: threshold raised to 3)
# ---------------------------------------------------------------------------

class TestStrategicDepth:
    def test_golden_payload_is_deep(self) -> None:
        result = check_strategic_depth(golden_grade_payload())
        assert result.passed
        assert result.score >= 3

    def test_weak_payload_is_shallow(self) -> None:
        result = check_strategic_depth(weak_payload())
        assert result.score <= 2
        assert not result.passed

    def test_shallow_reframe_detected(self) -> None:
        payload = {
            "proposed_reframe": "Use library pydantic instead of dataclasses",
            "current_system_limit": "something",
            "owner_value_statement": "better validation",
        }
        result = check_strategic_depth(payload)
        assert "shallow cleanup" in result.details.lower()

    def test_bypass_a_reframe_detected_as_shallow(self) -> None:
        """DR bypass A: 'Introduce a granularity annotation carried alongside'."""
        payload = {
            "proposed_reframe": "Introduce a granularity annotation carried alongside TeachingUnit",
            "current_system_limit": "excerpting taxonomy",
            "owner_value_statement": "study navigate",
        }
        result = check_strategic_depth(payload)
        assert "shallow cleanup" in result.details.lower()

    def test_bypass_b_reframe_detected_as_shallow(self) -> None:
        """DR bypass B: 'Build a scholarly provenance ledger with content hashes'."""
        payload = {
            "proposed_reframe": "Build a scholarly provenance ledger with content hashes and lineage ids",
            "current_system_limit": "excerpting taxonomy",
            "owner_value_statement": "study trust",
        }
        result = check_strategic_depth(payload)
        assert "shallow cleanup" in result.details.lower()

    def test_bypass_c_reframe_detected_as_shallow(self) -> None:
        """DR bypass C: 'Transform taxonomy into an interactive study router'."""
        payload = {
            "proposed_reframe": "Transform taxonomy into an interactive study router with a two-stage placement cache",
            "current_system_limit": "taxonomy excerpting",
            "owner_value_statement": "study faster",
        }
        result = check_strategic_depth(payload)
        assert "shallow cleanup" in result.details.lower()

    def test_golden_reframe_not_flagged_as_shallow(self) -> None:
        """Golden example must NOT be flagged as shallow."""
        payload = {
            "proposed_reframe": "Build a multiresolution book digester instead of a book excerpter",
            "current_system_limit": "excerpting taxonomy normalization",
            "owner_value_statement": "study at any resolution level",
        }
        result = check_strategic_depth(payload)
        assert "is not a shallow cleanup" in result.details.lower()


# ---------------------------------------------------------------------------
# Tests: check_concreteness (v2: threshold raised to 3)
# ---------------------------------------------------------------------------

class TestConcreteness:
    def test_golden_payload_is_concrete(self) -> None:
        result = check_concreteness(golden_grade_payload())
        assert result.passed
        assert result.score >= 3

    def test_vague_risks_detected(self) -> None:
        result = check_concreteness(weak_payload())
        assert "vague" in result.details.lower()

    def test_new_vague_risk_patterns(self) -> None:
        """DR-identified bypass risks must be detected as vague."""
        payload = {
            "benefits": ["a" * 80, "b" * 80, "c" * 80],
            "risks": [
                "This introduces backward-compat concerns for stored excerpt JSON",
                "Storage footprint grows from additional metadata per excerpt",
                "Requires careful migration planning for existing processed books",
            ],
            "primary_insertion_boundary": "somewhere",
        }
        result = check_concreteness(payload)
        assert result.score <= 1


# ---------------------------------------------------------------------------
# Tests: check_evidence_fidelity (v2: new dimension)
# ---------------------------------------------------------------------------

class TestEvidenceFidelity:
    def test_golden_payload_has_verified_symbols(self) -> None:
        result = check_evidence_fidelity(golden_grade_payload())
        assert result.passed
        assert result.score >= 3
        assert "ExcerptRecord" in result.details

    def test_weak_payload_has_no_symbols(self) -> None:
        result = check_evidence_fidelity(weak_payload())
        assert not result.passed
        assert result.score <= 1

    def test_fabricated_symbol_not_verified(self) -> None:
        payload = {
            "current_system_limit": "The BranchNodeContent type in taxonomy doesn't exist",
            "proposed_reframe": "Add MultiResolutionDigest to the FlatLeafStore",
            "primary_insertion_boundary": "engines/taxonomy/contracts.py boundary",
            "secondary_required_changes": ["engines/taxonomy/contracts.py — add BranchNodeContent"],
        }
        result = check_evidence_fidelity(payload)
        # TreeNode is in the registry for taxonomy, but BranchNodeContent/MultiResolutionDigest
        # are not. Score depends on what other symbols happen to match.
        assert result.score <= 2


# ---------------------------------------------------------------------------
# Tests: check_inflation (v2: delta 8→4, per-dimension penalty)
# ---------------------------------------------------------------------------

class TestInflation:
    def test_golden_payload_not_inflated(self) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-golden-inf")
        inflation_dim = next(d for d in result.dimension_results if d.dimension == "inflation_check")
        assert inflation_dim.passed

    def test_weak_payload_is_inflated(self) -> None:
        result = check_inflation(weak_payload(), evaluator_total=4)
        assert not result.passed
        assert "INFLATED" in result.details

    def test_per_dimension_penalty_applied(self) -> None:
        """Self-reported product_reframing=4 with evaluator strategic_depth=0 → penalty."""
        payload = {
            "benchmark_scores": {
                "product_reframing": 4, "live_system_contrast": 2,
                "primary_boundary_accuracy": 2, "latent_ingredient_leverage": 2,
                "invariant_coverage": 2, "owner_value": 2,
                "autonomous_originality": 2, "evaluability": 2,
            },
            "coworker_verdicts": [],
        }
        dimension_scores = {"strategic_depth": 0, "repo_grounding": 2}
        result = check_inflation(payload, evaluator_total=12, dimension_scores=dimension_scores)
        assert "per-dimension penalty" in result.details


# ---------------------------------------------------------------------------
# Tests: evaluate_creative_output (v2: no provisional, 6 dimensions)
# ---------------------------------------------------------------------------

class TestEvaluateCreativeOutput:
    def test_golden_payload_passes(self) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-golden")
        assert result.verdict == "pass"
        assert result.idea_class_evaluator in ("major", "benchmark_grade")

    def test_weak_payload_rejected(self) -> None:
        result = evaluate_creative_output(weak_payload(), "test-weak")
        assert result.verdict == "reject"
        assert len(result.rejection_reasons) >= 2

    def test_partial_payload_rejected(self) -> None:
        """v2: no provisional — partial payloads are rejected."""
        result = evaluate_creative_output(partial_payload(), "test-partial")
        assert result.verdict == "reject"

    def test_result_has_all_six_dimensions(self) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-dims")
        dimensions = {d.dimension for d in result.dimension_results}
        assert dimensions == set(evaluator.GOLDEN_DIMENSIONS)
        assert len(dimensions) == 6

    def test_timestamp_is_set(self) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-ts")
        assert result.timestamp
        assert "T" in result.timestamp


# ---------------------------------------------------------------------------
# Tests: adversarial bypass (v2: DR audit test cases)
# ---------------------------------------------------------------------------

class TestAdversarialBypass:
    """All 3 DR adversarial bypass examples must REJECT.
    Golden must still PASS. This is the core DR hardening test.
    """

    def test_bypass_a_rejected(self) -> None:
        """DR Bypass A: 'Granularity Tagging Layer' — add field + propagation."""
        result = evaluate_creative_output(bypass_a_payload(), "bypass-a")
        assert result.verdict == "reject", (
            f"Bypass A should be REJECTED but got {result.verdict}. "
            f"Reasons: {result.rejection_reasons}"
        )

    def test_bypass_b_rejected(self) -> None:
        """DR Bypass B: 'Provenance Ledger Unification' — observability + hashing."""
        result = evaluate_creative_output(bypass_b_payload(), "bypass-b")
        assert result.verdict == "reject", (
            f"Bypass B should be REJECTED but got {result.verdict}. "
            f"Reasons: {result.rejection_reasons}"
        )

    def test_bypass_c_rejected(self) -> None:
        """DR Bypass C: 'Taxonomy Placement Accelerator' — caching + heuristics."""
        result = evaluate_creative_output(bypass_c_payload(), "bypass-c")
        assert result.verdict == "reject", (
            f"Bypass C should be REJECTED but got {result.verdict}. "
            f"Reasons: {result.rejection_reasons}"
        )

    def test_golden_still_passes_after_hardening(self) -> None:
        """The golden example IS the quality bar — it must always pass."""
        result = evaluate_creative_output(golden_grade_payload(), "golden-hardened")
        assert result.verdict == "pass", (
            f"Golden payload should PASS but got {result.verdict}. "
            f"Reasons: {result.rejection_reasons}"
        )


# ---------------------------------------------------------------------------
# Tests: findings routing (v2: only "pass" routes)
# ---------------------------------------------------------------------------

class TestFindingsRouting:
    def test_passing_result_writes_to_findings(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        findings_file = tmp_path / "CUMULATIVE_FINDINGS.md"
        monkeypatch.setattr(evaluator, "CUMULATIVE_FINDINGS", findings_file)

        result = evaluate_creative_output(golden_grade_payload(), "test-route")
        result.verdict = "pass"
        written = route_to_findings(result, golden_grade_payload())
        assert written
        content = findings_file.read_text(encoding="utf-8")
        assert "test-route" in content
        assert "PASS" in content

    def test_rejected_result_not_written(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        findings_file = tmp_path / "CUMULATIVE_FINDINGS.md"
        monkeypatch.setattr(evaluator, "CUMULATIVE_FINDINGS", findings_file)

        result = evaluate_creative_output(weak_payload(), "test-reject")
        written = route_to_findings(result, weak_payload())
        assert not written
        assert not findings_file.exists()


# ---------------------------------------------------------------------------
# Tests: save_evaluation_result
# ---------------------------------------------------------------------------

class TestSaveResult:
    def test_saves_json(self, tmp_path: Path) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-save")
        path = save_evaluation_result(result, tmp_path)
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert data["task_id"] == "test-save"
        assert "dimension_results" in data
        assert len(data["dimension_results"]) == 6  # v2: 6 dimensions

    def test_format_findings_entry(self) -> None:
        result = evaluate_creative_output(golden_grade_payload(), "test-format")
        entry = format_findings_entry(result, golden_grade_payload())
        assert "## test-format" in entry
        assert "Evaluator total" in entry
        assert "Dimension Scores" in entry
        assert "/24" in entry  # v2: max is now 24, not 20
