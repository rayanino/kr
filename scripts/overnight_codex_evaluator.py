"""Deterministic quality evaluator for autonomous creative output.

Evaluates creative ideation output against the golden example quality bar
using repo-grounded checks, not self-reported scores. This is the measurement
instrument that answers: 'can the autonomous system originate ideas at the
golden example level?'

Hardened per ChatGPT DR audit (2026-04-06): added evidence fidelity dimension,
expanded shallow detection, tightened inflation check, eliminated provisional
verdict, raised PASS thresholds. Doctrine: stagnation over corruption.

Reference: docs/codex/2026-04-03-golden-example-multiresolution-digester.md
"""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    from scripts.overnight_codex_common import (
        CUMULATIVE_FINDINGS,
        OVERNIGHT_CODEX_DIR,
        PIPELINE_ORDER,
        PROJECT_DIR,
        atomic_write,
    )
    from scripts.overnight_codex_ideation import (
        classify_idea,
        normalize_benchmark_scores,
    )
except ImportError:
    from overnight_codex_common import (
        CUMULATIVE_FINDINGS,
        OVERNIGHT_CODEX_DIR,
        PIPELINE_ORDER,
        PROJECT_DIR,
        atomic_write,
    )
    from overnight_codex_ideation import (
        classify_idea,
        normalize_benchmark_scores,
    )


# Quality dimensions derived from the golden example's characteristics.
# Each maps to a deterministic check function.
# v2: added evidence_fidelity per DR audit (6 dimensions, max 24).
GOLDEN_DIMENSIONS = [
    "repo_grounding",
    "structural_completeness",
    "strategic_depth",
    "concreteness",
    "evidence_fidelity",
    "inflation_check",
]

# Known engine boundary patterns that indicate architectural awareness.
KNOWN_BOUNDARIES = [
    r"source\s*(?:→|->|to)\s*normalization",
    r"normalization\s*(?:→|->|to)\s*passaging",
    r"passaging\s*(?:→|->|to)\s*atomization",
    r"atomization\s*(?:→|->|to)\s*excerpting",
    r"excerpting\s*(?:→|->|to)\s*taxonomy",
    r"taxonomy\s*(?:→|->|to)\s*synthesis",
    r"excerpting\s+phase\s+[0-9]+[a-z]?\s*(?:→|->|to)\s*(?:phase\s+)?[0-9]+",
    r"(?:contracts|contracts\.py|SPEC\.md|output)\s+boundary",
]

# Patterns that indicate dressed-up cleanup rather than strategic reframing.
# v2: expanded from 5 to 11 patterns per DR adversarial bypass analysis.
SHALLOW_PATTERNS = [
    # Original 5 patterns.
    r"^use\s+(?:library|package|tool)\s+\w+\s+instead\s+of",
    r"^add\s+(?:a\s+)?field\s+\w+\s+to\s+(?:the\s+)?contract",
    r"^rename\s+\w+\s+to\s+\w+",
    r"^(?:move|extract|refactor)\s+\w+\s+(?:into|to)\s+",
    r"^replace\s+\w+\s+with\s+\w+$",
    # DR bypass A: contract field + propagation dressed as reframe.
    r"^introduce\s+(?:a\s+)?(?:new\s+)?\w*\s*(?:field|annotation|tag|marker|flag)\b",
    r"(?:propagat|pass.through|carr(?:y|ied)\s+alongside)",
    # DR bypass B: observability/hashing dressed as study feature.
    r"^(?:build|create|implement)\s+.*(?:cache|memoiz|fingerprint|hash|ledger)\b",
    r"^(?:add|introduce|build)\s+.*(?:observability|monitoring|tracing|logging|audit)\b",
    # DR bypass C: optimization/caching dressed as transformation.
    r"^(?:optimize|accelerat|speed.up|improv.+performance)",
    r"^transform\s+\w+\s+into\s+.*(?:router|dispatcher|filter|cache)\b",
]

# Minimum word counts for substantive text fields.
MIN_WORDS = {
    "current_system_limit": 15,
    "proposed_reframe": 20,
    "primary_insertion_boundary": 8,
    "owner_value_statement": 10,
}

# v2: tightened from 8 to 4 per DR inflation audit.
MAX_INFLATION_DELTA = 4

# Static symbol registry for evidence fidelity verification.
# Maps repo-relative file paths to known class/enum names from contracts.
# Built from exhaustive exploration of all 5 engine contracts (2026-04-06).
SYMBOL_REGISTRY: dict[str, set[str]] = {
    "engines/source/contracts.py": {
        "SourceMetadata", "SourceRegistryEntry", "WorkRegistryEntry",
        "ScholarAuthorityRecord", "ScholarReference", "TextLayer",
        "GenreChain", "Genre", "StructuralFormat", "TrustTier",
        "AuthorityLevel", "AttributionStatus", "ProcessingStatus",
        "TextFidelity", "SourceFormat", "WorkLevel", "ErrorCode",
        "CompositionalProfile", "ScholarlyContext", "IntertextualMetrics",
    },
    "engines/normalization/contracts.py": {
        "ContentUnit", "DivisionNode", "NormalizedManifest", "NormalizedPackage",
        "TextLayerSegment", "Footnote", "StructuralMarkers", "ContentFlags",
        "BoundaryContinuity", "DiscourseFlow", "DiscourseSegment",
        "LayerType", "DivisionType", "FootnoteType", "HeadingConfidence",
        "LayerFingerprint", "QualityReport", "ContentCensus",
        "TahqiqTopology", "EditionReliability",
    },
    "engines/excerpting/contracts.py": {
        "ExcerptRecord", "TeachingUnit", "AssembledChunk", "ClassifiedSegment",
        "ConsensusRecord", "ConsensusDecision", "ScholarlyFunction",
        "SelfContainmentLevel", "JoinPoint", "AssemblyMetadata",
        "SplitInfo", "AuthorAttribution", "ScholarAttribution",
        "EvidenceRef", "TakhrijEntry", "CrossReference",
        "PageRange", "TermVariant",
    },
    "engines/taxonomy/contracts.py": {
        "TreeNode", "LeafCoverage", "PlacedExcerptAdditions",
        "EvolutionProposal", "CoverageGap", "ScholarlyLandscape",
        "DisagreementTopology", "LeafDisagreementClassification",
        "TreeNodeType", "PlacementReviewOutcome", "GapType",
        "PrerequisiteEdge", "CrossScienceLink", "SourceEvolutionPredictions",
    },
    "engines/synthesis/contracts.py": {
        "Entry", "EntryContent", "TaxonomyPlacedExcerpt",
        "GenerationMetadata", "ScholarlyAnalysis", "ScholarlyPosition",
        "KhilafClassification", "QualityAssessment", "Citation",
        "ConsensusMapping", "GenealogyChain", "GapNote",
        "SelfVerificationResult", "AssessmentSet", "ChangeSummary",
        "RegenerationRequest", "StalenessSignal",
    },
}

# Dimension cross-check mapping: self-reported dimension → evaluator dimension.
# Used by inflation check to detect per-dimension gaming.
DIMENSION_CROSSCHECK: dict[str, str] = {
    "product_reframing": "strategic_depth",
    "primary_boundary_accuracy": "repo_grounding",
    "owner_value": "strategic_depth",
}


@dataclass
class DimensionResult:
    """Result of evaluating one quality dimension."""

    dimension: str
    score: int  # 0-4
    passed: bool
    details: str


@dataclass
class EvaluationResult:
    """Complete evaluation of a creative output payload."""

    task_id: str
    dimension_results: list[DimensionResult] = field(default_factory=list)
    evaluator_total: int = 0
    self_reported_total: int = 0
    inflation_delta: int = 0
    idea_class_evaluator: str = "non_major"
    idea_class_self: str = ""
    verdict: str = "reject"  # reject | pass (v2: provisional eliminated)
    rejection_reasons: list[str] = field(default_factory=list)
    timestamp: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize for JSON output."""
        return {
            "task_id": self.task_id,
            "dimension_results": [
                {
                    "dimension": d.dimension,
                    "score": d.score,
                    "passed": d.passed,
                    "details": d.details,
                }
                for d in self.dimension_results
            ],
            "evaluator_total": self.evaluator_total,
            "self_reported_total": self.self_reported_total,
            "inflation_delta": self.inflation_delta,
            "idea_class_evaluator": self.idea_class_evaluator,
            "idea_class_self": self.idea_class_self,
            "verdict": self.verdict,
            "rejection_reasons": self.rejection_reasons,
            "timestamp": self.timestamp,
        }


def _word_count(text: str) -> int:
    """Count words in a text string."""
    return len(text.split())


def _resolve_boundary_to_path(boundary: str) -> Path | None:
    """Attempt to resolve a boundary description to a real repo path."""
    for engine in PIPELINE_ORDER:
        if engine in boundary.lower():
            contracts = PROJECT_DIR / "engines" / engine / "contracts.py"
            if contracts.exists():
                return contracts
            spec = PROJECT_DIR / "engines" / engine / "SPEC.md"
            if spec.exists():
                return spec
    return None


def _matches_known_boundary(boundary: str) -> bool:
    """Check if the boundary description matches known architectural patterns."""
    lower = boundary.lower()
    for pattern in KNOWN_BOUNDARIES:
        if re.search(pattern, lower):
            return True
    return False


def _is_shallow(text: str) -> bool:
    """Check if the text matches a shallow/cleanup pattern."""
    lower = text.lower().strip()
    for pattern in SHALLOW_PATTERNS:
        if re.search(pattern, lower):
            return True
    return False


def _references_real_files(items: list[str]) -> tuple[int, int]:
    """Count how many items reference real repo paths. Returns (real, total)."""
    real = 0
    for item in items:
        paths = re.findall(r'(?:engines|shared|scripts|reference)/[a-zA-Z0-9_/.-]+', item)
        for path_str in paths:
            if (PROJECT_DIR / path_str).exists():
                real += 1
                break
    return real, len(items)


def _verify_symbols_in_text(text: str, file_path: str) -> list[str]:
    """Check which registry symbols for a file appear in the text."""
    registry_key = file_path.replace("\\", "/")
    known_symbols = SYMBOL_REGISTRY.get(registry_key, set())
    if not known_symbols:
        return []
    found: list[str] = []
    for symbol in known_symbols:
        if symbol in text:
            found.append(symbol)
    return found


def check_repo_grounding(payload: dict[str, Any]) -> DimensionResult:
    """Check if the idea is grounded in the actual repo structure."""
    score = 0
    details_parts: list[str] = []

    boundary = str(payload.get("primary_insertion_boundary", ""))
    boundary_path = _resolve_boundary_to_path(boundary)
    boundary_matches = _matches_known_boundary(boundary)

    if boundary_path and boundary_path.exists():
        score += 2
        details_parts.append(f"boundary resolves to {boundary_path.name}")
    elif boundary_matches:
        score += 1
        details_parts.append("boundary matches known pattern")
    else:
        details_parts.append("boundary does not resolve to any known file or pattern")

    changes = payload.get("secondary_required_changes", [])
    if isinstance(changes, list) and changes:
        real, total = _references_real_files([str(c) for c in changes])
        if real > 0:
            score += 1
            details_parts.append(f"{real}/{total} secondary changes reference real files")
        else:
            details_parts.append("no secondary changes reference real files")

    limit_text = str(payload.get("current_system_limit", "")).lower()
    engine_refs = [e for e in PIPELINE_ORDER if e in limit_text]
    if engine_refs:
        score += 1
        details_parts.append(f"system limit references engines: {', '.join(engine_refs)}")
    else:
        details_parts.append("system limit does not reference any pipeline engine")

    return DimensionResult(
        dimension="repo_grounding",
        score=min(score, 4),
        passed=score >= 3,  # v2: raised from 2 to 3
        details="; ".join(details_parts),
    )


def check_structural_completeness(payload: dict[str, Any]) -> DimensionResult:
    """Check if all required fields are present and substantive."""
    score = 0
    details_parts: list[str] = []
    missing: list[str] = []

    for field_name, min_words in MIN_WORDS.items():
        text = str(payload.get(field_name, "")).strip()
        wc = _word_count(text)
        if wc >= min_words:
            score += 1
        else:
            missing.append(f"{field_name} ({wc}/{min_words} words)")

    if missing:
        details_parts.append(f"thin fields: {', '.join(missing)}")
    else:
        details_parts.append("all text fields meet minimum depth")

    for list_field, min_items in [("benefits", 3), ("risks", 3), ("secondary_required_changes", 1)]:
        items = payload.get(list_field, [])
        if not (isinstance(items, list) and len(items) >= min_items):
            details_parts.append(f"{list_field}: missing or insufficient items")

    return DimensionResult(
        dimension="structural_completeness",
        score=min(score, 4),
        passed=score >= 3,
        details="; ".join(details_parts),
    )


def check_strategic_depth(payload: dict[str, Any]) -> DimensionResult:
    """Check if the idea is genuinely strategic vs a dressed-up cleanup."""
    score = 0
    details_parts: list[str] = []

    reframe = str(payload.get("proposed_reframe", ""))
    limit = str(payload.get("current_system_limit", ""))
    owner_value = str(payload.get("owner_value_statement", ""))

    # Shallow pattern detection (v2: expanded from 5 to 11 patterns).
    if _is_shallow(reframe):
        details_parts.append("proposed_reframe matches shallow cleanup pattern")
        # v2: shallow match caps score — cannot earn first point.
    else:
        score += 1
        details_parts.append("proposed_reframe is not a shallow cleanup")

    # Word count as a proxy for depth.
    if _word_count(reframe) >= 30:
        score += 1
        details_parts.append("reframe has substantial depth")

    # Owner value should reference the study/learning experience.
    study_keywords = ["study", "learn", "review", "navigate", "understand", "knowledge",
                      "scholar", "read", "explore", "discover", "digest"]
    owner_lower = owner_value.lower()
    matches = [kw for kw in study_keywords if kw in owner_lower]
    if matches:
        score += 1
        details_parts.append(f"owner value references study experience: {', '.join(matches[:3])}")
    else:
        details_parts.append("owner value does not reference the study experience")

    # v2: cross-engine scope with single-engine penalty.
    all_text = f"{reframe} {limit} {owner_value}".lower()
    engines_mentioned = [e for e in PIPELINE_ORDER if e in all_text]
    if len(engines_mentioned) >= 2:
        score += 1
        details_parts.append(f"spans {len(engines_mentioned)} engines: {', '.join(engines_mentioned)}")
    else:
        details_parts.append("limited to single engine scope")
        # v2: single-engine ideas cannot pass strategic_depth.
        score = min(score, 2)

    return DimensionResult(
        dimension="strategic_depth",
        score=min(score, 4),
        passed=score >= 3,  # v2: raised from 2 to 3
        details="; ".join(details_parts),
    )


def check_concreteness(payload: dict[str, Any]) -> DimensionResult:
    """Check if benefits, risks, and changes are concrete vs vague."""
    score = 0
    details_parts: list[str] = []

    benefits = payload.get("benefits", [])
    if isinstance(benefits, list):
        specific_benefits = sum(
            1 for b in benefits
            if isinstance(b, str) and _word_count(b) >= 8
        )
        if specific_benefits >= 3:
            score += 1
            details_parts.append(f"{specific_benefits} specific benefits")
        else:
            details_parts.append(f"only {specific_benefits} specific benefits (need 3+)")

    # v2: expanded from 4 to 9 vague risk patterns per DR audit.
    risks = payload.get("risks", [])
    vague_risk_patterns = [
        # Original 4 patterns.
        r"^may\s+require\s+(?:some\s+)?refactoring",
        r"^could\s+be\s+complex",
        r"^might\s+(?:need|require)\s+(?:more\s+)?(?:work|effort|time)",
        r"^performance\s+(?:may|might|could)",
        # v2: 5 new patterns from DR adversarial bypass analysis.
        r"^this\s+(?:introduces|creates|adds)\s+(?:backward|compat|migration)",
        r"^(?:storage|memory|disk)\s+(?:footprint|usage|cost)\s+(?:grows|increases|may)",
        r"^(?:could|may|might)\s+complicate\s+downstream",
        r"^(?:requires?|needs?)\s+careful\s+(?:planning|consideration|migration|testing)",
        r"^this\s+(?:could|may|might)\s+(?:affect|impact|change)\s+(?:existing|current)",
    ]
    if isinstance(risks, list):
        concrete_risks = 0
        for risk in risks:
            if not isinstance(risk, str):
                continue
            is_vague = any(re.search(p, risk.lower().strip()) for p in vague_risk_patterns)
            if not is_vague and _word_count(risk) >= 8:
                concrete_risks += 1
        if concrete_risks >= 2:
            score += 2
            details_parts.append(f"{concrete_risks} concrete risks")
        elif concrete_risks >= 1:
            score += 1
            details_parts.append(f"{concrete_risks} concrete risk(s)")
        else:
            details_parts.append("risks are vague or too short")

    boundary = str(payload.get("primary_insertion_boundary", ""))
    has_specific_ref = bool(re.search(
        r'(?:contracts\.py|SPEC\.md|phase\s*[0-9]|§[0-9]|ExcerptRecord|TeachingUnit)',
        boundary,
    ))
    if has_specific_ref:
        score += 1
        details_parts.append("boundary references specific contract/type")
    else:
        details_parts.append("boundary lacks specific contract/type reference")

    return DimensionResult(
        dimension="concreteness",
        score=min(score, 4),
        passed=score >= 3,  # v2: raised from 2 to 3
        details="; ".join(details_parts),
    )


def check_evidence_fidelity(payload: dict[str, Any]) -> DimensionResult:
    """Verify that claimed symbols actually exist in the referenced files.

    v2: new dimension per DR audit — the most dangerous false positives are
    hallucinated repo grounding (claiming a class exists when it doesn't).
    """
    score = 0
    details_parts: list[str] = []
    verified_symbols: list[str] = []
    files_with_verified: set[str] = set()

    # Combine all text fields that may contain repo claims.
    combined_text = " ".join([
        str(payload.get("current_system_limit", "")),
        str(payload.get("proposed_reframe", "")),
        str(payload.get("primary_insertion_boundary", "")),
        str(payload.get("owner_value_statement", "")),
    ])

    # Also check secondary_required_changes.
    changes = payload.get("secondary_required_changes", [])
    if isinstance(changes, list):
        combined_text += " " + " ".join(str(c) for c in changes)

    # For each registry file, check if its symbols appear in the combined text.
    for file_path in SYMBOL_REGISTRY:
        found = _verify_symbols_in_text(combined_text, file_path)
        if found:
            verified_symbols.extend(found)
            files_with_verified.add(file_path)

    # Score based on verified symbol count and file coverage.
    n_symbols = len(verified_symbols)
    n_files = len(files_with_verified)

    if n_symbols >= 3 and n_files >= 2:
        score = 4
        details_parts.append(
            f"{n_symbols} symbols verified across {n_files} files: "
            f"{', '.join(verified_symbols[:5])}"
        )
    elif n_symbols >= 2:
        score = 3
        details_parts.append(f"{n_symbols} symbols verified: {', '.join(verified_symbols[:4])}")
    elif n_symbols >= 1:
        score = 2
        details_parts.append(f"{n_symbols} symbol verified: {', '.join(verified_symbols[:2])}")
    elif combined_text.strip():
        score = 1
        details_parts.append("text references files but no registry symbols verified")
    else:
        score = 0
        details_parts.append("no verifiable claims found")

    return DimensionResult(
        dimension="evidence_fidelity",
        score=score,
        passed=score >= 3,  # At least 2 verified symbols
        details="; ".join(details_parts),
    )


def check_inflation(
    payload: dict[str, Any],
    evaluator_total: int,
    dimension_scores: dict[str, int] | None = None,
) -> DimensionResult:
    """Check if self-reported benchmark scores are inflated vs evaluator.

    v2: tightened delta 8→4, added per-dimension cross-check penalty.
    """
    scores, errors = normalize_benchmark_scores(payload)
    if errors:
        return DimensionResult(
            dimension="inflation_check",
            score=0,
            passed=False,
            details=f"self-reported scores invalid: {'; '.join(errors)}",
        )

    self_total = sum(scores.values())
    # v2: scale for 6 evaluator dimensions (was 5).
    scaled_evaluator = int(evaluator_total * (32 / 24)) if evaluator_total > 0 else 0
    delta = self_total - scaled_evaluator

    # v2: per-dimension cross-check penalty.
    penalty = 0
    if dimension_scores:
        for self_dim, eval_dim in DIMENSION_CROSSCHECK.items():
            self_score = scores.get(self_dim, 0)
            eval_score = dimension_scores.get(eval_dim, 0)
            if self_score >= 4 and eval_score <= 1:
                penalty += 4
    delta += penalty

    if delta <= 2:
        score = 4
        details = f"self-reported ({self_total}) ≈ scaled evaluator ({scaled_evaluator})"
    elif delta <= MAX_INFLATION_DELTA:
        score = 2
        details = f"self-reported ({self_total}) > scaled evaluator ({scaled_evaluator}) by {delta}"
    else:
        score = 0
        details = (
            f"INFLATED: self-reported ({self_total}) > scaled evaluator "
            f"({scaled_evaluator}) by {delta} (threshold: {MAX_INFLATION_DELTA})"
        )

    if penalty > 0:
        details += f" [+{penalty} per-dimension penalty]"

    return DimensionResult(
        dimension="inflation_check",
        score=score,
        passed=delta <= MAX_INFLATION_DELTA,
        details=details,
    )


def evaluate_creative_output(
    payload: dict[str, Any],
    task_id: str = "",
) -> EvaluationResult:
    """Run all quality checks on a creative output payload."""
    result = EvaluationResult(
        task_id=task_id or str(payload.get("task_id", "unknown")),
        timestamp=datetime.now(timezone.utc).isoformat(),
    )

    # Run the five content checks first (v2: added evidence_fidelity).
    grounding = check_repo_grounding(payload)
    completeness = check_structural_completeness(payload)
    depth = check_strategic_depth(payload)
    concreteness = check_concreteness(payload)
    fidelity = check_evidence_fidelity(payload)

    content_total = (
        grounding.score + completeness.score + depth.score
        + concreteness.score + fidelity.score
    )

    # Build dimension score map for inflation cross-check.
    dimension_scores = {
        "repo_grounding": grounding.score,
        "structural_completeness": completeness.score,
        "strategic_depth": depth.score,
        "concreteness": concreteness.score,
        "evidence_fidelity": fidelity.score,
    }

    # Run inflation check with per-dimension cross-check.
    inflation = check_inflation(payload, content_total, dimension_scores)

    result.dimension_results = [
        grounding, completeness, depth, concreteness, fidelity, inflation,
    ]
    result.evaluator_total = content_total + inflation.score

    # Self-reported scores.
    scores, _ = normalize_benchmark_scores(payload)
    result.self_reported_total = sum(scores.values())
    result.idea_class_self, _ = classify_idea(scores) if scores else ("unknown", 0)

    # Scaled evaluator total for classification comparison.
    scaled = int(content_total * (32 / 24)) if content_total > 0 else 0
    result.inflation_delta = result.self_reported_total - scaled

    # v2: classify based on 6-dimension evaluator (max 24).
    if content_total >= 20:
        result.idea_class_evaluator = "benchmark_grade"
    elif content_total >= 15:
        result.idea_class_evaluator = "major"
    else:
        result.idea_class_evaluator = "non_major"

    # v2: binary verdict — no provisional. Stagnation over corruption.
    rejection_reasons: list[str] = []
    for dim in result.dimension_results:
        if not dim.passed:
            rejection_reasons.append(f"{dim.dimension}: {dim.details}")

    if not rejection_reasons:
        result.verdict = "pass"
    else:
        result.verdict = "reject"
        result.rejection_reasons = rejection_reasons

    return result


def format_findings_entry(
    result: EvaluationResult,
    payload: dict[str, Any],
) -> str:
    """Format an evaluation result as a CUMULATIVE_FINDINGS.md entry."""
    lines: list[str] = []
    lines.append(f"## {result.task_id} — {result.verdict.upper()}")
    lines.append(f"**Date:** {result.timestamp[:10]}")
    lines.append(f"**Evaluator class:** {result.idea_class_evaluator}")
    lines.append(f"**Self-reported class:** {result.idea_class_self}")
    lines.append(f"**Evaluator total:** {result.evaluator_total}/24")
    lines.append(f"**Self-reported total:** {result.self_reported_total}/32")
    lines.append(f"**Inflation delta:** {result.inflation_delta}")
    lines.append("")

    reframe = str(payload.get("proposed_reframe", "")).strip()
    if reframe:
        lines.append(f"**Proposed reframe:** {reframe}")
        lines.append("")

    boundary = str(payload.get("primary_insertion_boundary", "")).strip()
    if boundary:
        lines.append(f"**Primary boundary:** {boundary}")
        lines.append("")

    owner_value = str(payload.get("owner_value_statement", "")).strip()
    if owner_value:
        lines.append(f"**Owner value:** {owner_value}")
        lines.append("")

    lines.append("### Dimension Scores")
    lines.append("")
    for dim in result.dimension_results:
        status = "PASS" if dim.passed else "FAIL"
        lines.append(f"- **{dim.dimension}**: {dim.score}/4 [{status}] — {dim.details}")
    lines.append("")

    if result.rejection_reasons:
        lines.append("### Rejection Reasons")
        lines.append("")
        for reason in result.rejection_reasons:
            lines.append(f"- {reason}")
        lines.append("")

    lines.append("---")
    lines.append("")
    return "\n".join(lines)


def route_to_findings(
    result: EvaluationResult,
    payload: dict[str, Any],
) -> bool:
    """Write passing results to CUMULATIVE_FINDINGS.md.

    v2: only "pass" routes — "provisional" eliminated.
    """
    if result.verdict != "pass":
        return False

    entry = format_findings_entry(result, payload)
    current = ""
    if CUMULATIVE_FINDINGS.exists():
        current = CUMULATIVE_FINDINGS.read_text(encoding="utf-8")

    if not current.strip():
        current = "# Overnight Codex Cumulative Findings\n\n"

    updated = current.rstrip() + "\n\n" + entry
    atomic_write(CUMULATIVE_FINDINGS, updated)
    return True


def save_evaluation_result(
    result: EvaluationResult,
    output_dir: Path | None = None,
) -> Path:
    """Persist the full evaluation result to disk."""
    target_dir = output_dir or (OVERNIGHT_CODEX_DIR / "evaluations")
    target_dir.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r'[^a-z0-9_-]', '-', result.task_id.lower())
    output_path = target_dir / f"{slug}_eval.json"
    atomic_write(output_path, json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    return output_path
