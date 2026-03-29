"""Review packet construction with 6 required lanes.

Consumes analysis results (not raw run directories) and produces
bounded human-review packets.
"""
from __future__ import annotations

import json
import random
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .models import (
    Anomaly,
    BookAnalysisResult,
    CanonicalUnitKey,
    EvidenceBasis,
    ReviewCandidate,
    UnitLedgerEntry,
)

# ---------------------------------------------------------------------------
# Lane assignment
# ---------------------------------------------------------------------------


def assign_lanes(
    results: list[BookAnalysisResult],
    all_candidates: list[ReviewCandidate],
    all_ledger: dict[CanonicalUnitKey, UnitLedgerEntry],
    all_excerpts: list[dict],
) -> dict[str, list[ReviewCandidate]]:
    """Assign review candidates into the 6 required lanes.

    Lane 1: mandatory observed failures
    Lane 2: inferred diagnostics
    Lane 3: self-containment / boundary risk
    Lane 4: sentinel audit sample (independent of anomaly ranking)
    Lane 5: stratified positive controls
    Lane 6: ambiguity / near-threshold cases
    """
    lanes: dict[str, list[ReviewCandidate]] = {
        "lane_1_observed_failures": [],
        "lane_2_inferred_diagnostics": [],
        "lane_3_self_containment_risk": [],
        "lane_4_sentinel_audit": [],
        "lane_5_positive_controls": [],
        "lane_6_ambiguity": [],
    }
    assigned_keys: set[CanonicalUnitKey] = set()

    # Build anomaly index
    all_anomalies: list[Anomaly] = []
    for r in results:
        all_anomalies.extend(r.anomalies)

    anomaly_map: dict[str, Anomaly] = {
        a.anomaly_id: a for a in all_anomalies
    }

    # --- Lane 1: Mandatory observed failures ---
    for cand in all_candidates:
        if cand.anomaly_ids:
            has_observed_fail = any(
                anomaly_map.get(aid) is not None
                and anomaly_map[aid].evidence_basis == EvidenceBasis.OBSERVED
                and anomaly_map[aid].severity == "structural_fail"
                for aid in cand.anomaly_ids
            )
            if has_observed_fail:
                lanes["lane_1_observed_failures"].append(cand)
                assigned_keys.add(cand.key)

    # Also add book-level failure cards for zero-output books
    for r in results:
        for ano in r.anomalies:
            if (
                ano.category == "zero_excerpt_run_with_upstream_activity"
                and ano.evidence_basis == EvidenceBasis.OBSERVED
            ):
                # Create a synthetic candidate for the book-level failure
                book_key = CanonicalUnitKey(
                    source_id=r.source_id,
                    div_id=f"(book-level:{r.book_name})",
                    chunk_index=0,
                    unit_index=0,
                )
                if book_key not in assigned_keys:
                    lanes["lane_1_observed_failures"].append(
                        ReviewCandidate(
                            key=book_key,
                            bucket_tags=["zero_output", "book_level_failure"],
                            stage_state="absent",
                            evidence_basis=EvidenceBasis.OBSERVED,
                            primary_text=None,
                            context={"book_name": r.book_name},
                            observed_facts=ano.observed_facts,
                            inferred_interpretation=ano.inferred_interpretation,
                            artifact_pointers=ano.evidence_paths,
                            review_questions=[
                                "Why did this book produce zero excerpts "
                                "despite upstream activity?",
                                "Is the root cause truncation, timeout, "
                                "or a parsing failure?",
                            ],
                            anomaly_ids=[ano.anomaly_id],
                        )
                    )
                    assigned_keys.add(book_key)

    # --- Lane 2: Inferred diagnostics ---
    for cand in all_candidates:
        if cand.key in assigned_keys:
            continue
        if cand.anomaly_ids:
            has_inferred = any(
                anomaly_map.get(aid) is not None
                and anomaly_map[aid].evidence_basis in (
                    EvidenceBasis.INFERRED_HIGH_CONFIDENCE,
                    EvidenceBasis.INFERRED_MODERATE_CONFIDENCE,
                )
                for aid in cand.anomaly_ids
            )
            if has_inferred:
                lanes["lane_2_inferred_diagnostics"].append(cand)
                assigned_keys.add(cand.key)

    # --- Lane 3: Self-containment / boundary risk ---
    partial_per_book: dict[str, int] = {}
    for cand in all_candidates:
        if cand.key in assigned_keys:
            continue
        if "dependent" in cand.bucket_tags:
            lanes["lane_3_self_containment_risk"].append(cand)
            assigned_keys.add(cand.key)
        elif "partial_self_containment" in cand.bucket_tags:
            book = cand.key.source_id
            count = partial_per_book.get(book, 0)
            if count < 5:
                lanes["lane_3_self_containment_risk"].append(cand)
                assigned_keys.add(cand.key)
                partial_per_book[book] = count + 1

    # --- Lane 4: Sentinel audit sample ---
    # Independent of anomaly ranking, deterministic
    random.seed(42)
    sentinel_pool = [
        e for e in all_excerpts
        if _excerpt_key(e) not in assigned_keys
    ]
    target = max(3, len(all_excerpts) // 10)

    # Stratified: at least 1 per book
    books_seen: set[str] = set()
    sentinel_selected: list[dict] = []
    random.shuffle(sentinel_pool)
    for exc in sentinel_pool:
        book = exc.get("source_id", "")
        if book not in books_seen:
            sentinel_selected.append(exc)
            books_seen.add(book)
            if len(sentinel_selected) >= target:
                break

    # Fill remaining
    for exc in sentinel_pool:
        if len(sentinel_selected) >= target:
            break
        if exc not in sentinel_selected:
            sentinel_selected.append(exc)

    for exc in sentinel_selected:
        key = _excerpt_key(exc)
        if key not in assigned_keys:
            lanes["lane_4_sentinel_audit"].append(
                _excerpt_to_candidate(exc, ["sentinel_audit"])
            )
            assigned_keys.add(key)

    # --- Lane 5: Stratified positive controls ---
    # Cleanest excerpts: FULL, no review_flags, no gate_flags
    controls_per_book: dict[str, int] = {}
    funcs_seen: set[str] = set()

    clean_excerpts = [
        e for e in all_excerpts
        if (
            e.get("self_containment") == "FULL"
            and not e.get("review_flags")
            and not e.get("gate_flags")
            and _excerpt_key(e) not in assigned_keys
        )
    ]
    # Shuffle for variety
    random.shuffle(clean_excerpts)

    for exc in clean_excerpts:
        book = exc.get("source_id", "")
        func = exc.get("primary_function", "")
        count = controls_per_book.get(book, 0)
        # 2 per book max, prefer diverse functions
        if count < 2:
            if func not in funcs_seen or count == 0:
                key = _excerpt_key(exc)
                lanes["lane_5_positive_controls"].append(
                    _excerpt_to_candidate(exc, ["positive_control"])
                )
                assigned_keys.add(key)
                controls_per_book[book] = count + 1
                funcs_seen.add(func)

    # --- Lane 6: Ambiguity / near-threshold ---
    ambig_per_book: dict[str, int] = {}
    for cand in all_candidates:
        if cand.key in assigned_keys:
            continue
        if (
            "consensus_disagreement" in cand.bucket_tags
            or "near_threshold" in cand.bucket_tags
        ):
            book = cand.key.source_id
            count = ambig_per_book.get(book, 0)
            if count < 3:
                lanes["lane_6_ambiguity"].append(cand)
                assigned_keys.add(cand.key)
                ambig_per_book[book] = count + 1

    return lanes


def _excerpt_key(exc: dict) -> CanonicalUnitKey:
    """Extract canonical key from an excerpt dict."""
    return CanonicalUnitKey(
        source_id=exc.get("source_id", ""),
        div_id=exc.get("div_id", ""),
        chunk_index=exc.get("chunk_index", 0),
        unit_index=exc.get("unit_index", 0),
    )


def _excerpt_to_candidate(
    exc: dict,
    bucket_tags: list[str],
) -> ReviewCandidate:
    """Convert a raw excerpt dict to a ReviewCandidate."""
    key = _excerpt_key(exc)
    return ReviewCandidate(
        key=key,
        bucket_tags=bucket_tags,
        stage_state="final_excerpt",
        evidence_basis=EvidenceBasis.OBSERVED,
        primary_text=exc.get("primary_text"),
        context={
            "primary_function": exc.get("primary_function"),
            "self_containment": exc.get("self_containment"),
            "div_path": exc.get("div_path"),
        },
        observed_facts=[
            f"primary_function: {exc.get('primary_function')}",
            f"self_containment: {exc.get('self_containment')}",
            f"word_count: {len((exc.get('primary_text') or '').split())}",
        ],
        inferred_interpretation=None,
        artifact_pointers=[],
        review_questions=[
            "Is this excerpt a genuinely useful teaching unit?",
            "Is the self-containment assessment correct?",
        ],
    )


# ---------------------------------------------------------------------------
# Card formatting
# ---------------------------------------------------------------------------

def format_card_md(
    cand: ReviewCandidate,
    card_number: int,
) -> str:
    """Format one review card as markdown."""
    lines = [f"### Card {card_number}"]
    lines.append("")
    lines.append(f"**Canonical Key:** `{cand.key}`")
    lines.append(f"**Bucket Tags:** {', '.join(cand.bucket_tags)}")
    lines.append(f"**Stage State:** {cand.stage_state}")
    lines.append(f"**Evidence Basis:** {cand.evidence_basis.value}")
    lines.append("")

    if cand.primary_text:
        # Show first 300 chars of primary text
        text_preview = cand.primary_text[:300]
        if len(cand.primary_text) > 300:
            text_preview += "..."
        lines.append(f"**Primary Text:**")
        lines.append(f"> {text_preview}")
        lines.append("")

    if cand.context:
        lines.append("**Context:**")
        for k, v in cand.context.items():
            if isinstance(v, dict):
                lines.append(f"- {k}: {json.dumps(v, ensure_ascii=False)[:200]}")
            else:
                lines.append(f"- {k}: {v}")
        lines.append("")

    lines.append("**Observed Facts:**")
    for fact in cand.observed_facts:
        lines.append(f"- {fact}")
    lines.append("")

    if cand.inferred_interpretation:
        lines.append(f"**Inferred Interpretation:** {cand.inferred_interpretation}")
        lines.append("")

    if cand.artifact_pointers:
        lines.append("**Artifact Pointers:**")
        for ap in cand.artifact_pointers:
            lines.append(f"- `{ap}`")
        lines.append("")

    if cand.review_questions:
        lines.append("**Review Questions:**")
        for rq in cand.review_questions:
            lines.append(f"- {rq}")
        lines.append("")

    if cand.anomaly_ids:
        lines.append(f"**Anomaly IDs:** {', '.join(cand.anomaly_ids)}")
        lines.append("")

    lines.append("---")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Packet output generation
# ---------------------------------------------------------------------------

_LANE_DESCRIPTIONS = {
    "lane_1_observed_failures": {
        "title": "Lane 1: Mandatory Observed Failures",
        "selection_rule": "All candidates with observed structural_fail anomalies. No sampling — all included.",
    },
    "lane_2_inferred_diagnostics": {
        "title": "Lane 2: Inferred Diagnostics",
        "selection_rule": "All candidates with inferred (high/moderate confidence) anomalies. No sampling.",
    },
    "lane_3_self_containment_risk": {
        "title": "Lane 3: Self-Containment / Boundary Risk",
        "selection_rule": "All DEPENDENT units + up to 5 PARTIAL units per book (boundary cases prioritized).",
    },
    "lane_4_sentinel_audit": {
        "title": "Lane 4: Sentinel Audit Sample",
        "selection_rule": "Random sample independent of anomaly ranking. seed=42. "
                          "At least 1 per book, total = max(3, 10% of excerpts).",
    },
    "lane_5_positive_controls": {
        "title": "Lane 5: Stratified Positive Controls",
        "selection_rule": "Cleanest FULL excerpts with no flags. Up to 2 per book, diverse functions.",
    },
    "lane_6_ambiguity": {
        "title": "Lane 6: Ambiguity / Near-Threshold Cases",
        "selection_rule": "Consensus disagreement or PARTIAL with context_hint. Up to 3 per book.",
    },
}


def build_packet_md(
    lanes: dict[str, list[ReviewCandidate]],
    results: list[BookAnalysisResult],
    total_units: int,
    total_excerpts: int,
) -> str:
    """Build the complete review packet as markdown."""
    lines = [
        "# Excerpting Evaluation Review Packet",
        "",
        f"Generated: {datetime.now(timezone.utc).isoformat()}",
        "",
        "## Campaign Summary",
        "",
    ]

    # Status table
    lines.append("| Book | Status | Excerpts | Anomalies |")
    lines.append("|------|--------|----------|-----------|")
    for r in results:
        lines.append(
            f"| {r.book_name} | {r.structural_status.value} | "
            f"{r.excerpt_count} | {len(r.anomalies)} |"
        )
    lines.append("")

    total_cards = sum(len(v) for v in lanes.values())
    lines.append(f"**Total units in ledger:** {total_units}")
    lines.append(f"**Total excerpts:** {total_excerpts}")
    lines.append(f"**Total review cards:** {total_cards}")
    lines.append("")

    # Lane sections
    card_number = 0
    for lane_id, lane_info in _LANE_DESCRIPTIONS.items():
        cards = lanes.get(lane_id, [])
        lines.append(f"## {lane_info['title']}")
        lines.append("")
        lines.append(f"**Denominator:** {total_units} units in ledger")
        lines.append(f"**Selected:** {len(cards)}")
        lines.append(f"**Selection Rule:** {lane_info['selection_rule']}")
        lines.append("")

        if not cards:
            lines.append("*No candidates in this lane.*")
            lines.append("")
        else:
            for cand in cards:
                card_number += 1
                lines.append(format_card_md(cand, card_number))
                lines.append("")

    return "\n".join(lines)


def build_packet_json(
    lanes: dict[str, list[ReviewCandidate]],
    results: list[BookAnalysisResult],
    total_units: int,
    total_excerpts: int,
) -> dict[str, Any]:
    """Build the review packet as a JSON-serializable dict."""
    packet: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "total_units": total_units,
        "total_excerpts": total_excerpts,
        "total_cards": sum(len(v) for v in lanes.values()),
        "books": [
            {
                "book_name": r.book_name,
                "source_id": r.source_id,
                "structural_status": r.structural_status.value,
                "excerpt_count": r.excerpt_count,
                "anomaly_count": len(r.anomalies),
            }
            for r in results
        ],
        "lanes": {},
    }

    for lane_id, lane_info in _LANE_DESCRIPTIONS.items():
        cards = lanes.get(lane_id, [])
        packet["lanes"][lane_id] = {
            "title": lane_info["title"],
            "selection_rule": lane_info["selection_rule"],
            "denominator": total_units,
            "selected": len(cards),
            "cards": [c.to_dict() for c in cards],
        }

    return packet


def build_manifest(
    lanes: dict[str, list[ReviewCandidate]],
    results: list[BookAnalysisResult],
    total_units: int,
    total_excerpts: int,
) -> dict[str, Any]:
    """Build the review manifest (summary metadata)."""
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "books_included": [r.book_name for r in results],
        "total_units": total_units,
        "total_excerpts": total_excerpts,
        "total_cards": sum(len(v) for v in lanes.values()),
        "lane_summary": {
            lane_id: {
                "title": lane_info["title"],
                "denominator": total_units,
                "selected": len(lanes.get(lane_id, [])),
                "selection_rule": lane_info["selection_rule"],
            }
            for lane_id, lane_info in _LANE_DESCRIPTIONS.items()
        },
        "observability_limitations": list(
            results[0].observability_limitations
        ) if results else [],
    }
