"""Cross-reference findings across DR responses (Component C).

Detects:
- Related findings: same spec_sections, affected_files, or text overlap
- Contradictions: related findings from different providers with opposing conclusions
- Agreements: related findings from different providers that reinforce each other

Populates related_finding_ids on Finding records and creates Contradiction
records in contradictions.jsonl.

Usage:
    python scripts/cross_reference_findings.py
    python scripts/cross_reference_findings.py --min-similarity 0.25 --dry-run
"""
from __future__ import annotations

import argparse
import hashlib
import logging
import re
import sys
import unicodedata
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    Contradiction,
    Finding,
    FindingSeverity,
    read_jsonl,
)

logger = logging.getLogger(__name__)

PROJECT_DIR = Path(__file__).resolve().parent.parent
KB_DIR = PROJECT_DIR / "overnight_codex" / "autonomous" / "knowledge_base"
FINDINGS_JSONL = KB_DIR / "findings.jsonl"
CONTRADICTIONS_JSONL = KB_DIR / "contradictions.jsonl"

# ═══════════════════════════════════════════════════════════════════
# Text similarity — Jaccard on word trigrams (no LLM, deterministic)
# ═══════════════════════════════════════════════════════════════════

# Gemini review finding #1: include Arabic presentation forms
_WORD_RE = re.compile(
    r"[a-zA-Z\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF]{3,}",
    re.UNICODE,
)


def _tokenize(text: str) -> list[str]:
    """Extract lowercase words (3+ chars, Latin + Arabic + presentation forms).

    NFC-normalizes first to ensure composed diacritics match (Gemini finding #4).
    """
    normalized = unicodedata.normalize("NFC", text)
    return [m.group().lower() for m in _WORD_RE.finditer(normalized)]


def _trigrams(tokens: list[str]) -> set[tuple[str, str, str]]:
    """Build word trigram set for Jaccard comparison."""
    if len(tokens) < 3:
        return {(t, "", "") for t in tokens}
    return {(tokens[i], tokens[i + 1], tokens[i + 2]) for i in range(len(tokens) - 2)}


def text_similarity(text_a: str, text_b: str) -> float:
    """Jaccard similarity on word trigrams. Returns 0.0-1.0."""
    tg_a = _trigrams(_tokenize(text_a))
    tg_b = _trigrams(_tokenize(text_b))
    if not tg_a or not tg_b:
        return 0.0
    intersection = len(tg_a & tg_b)
    union = len(tg_a | tg_b)
    return intersection / union if union > 0 else 0.0


# ═══════════════════════════════════════════════════════════════════
# Structural overlap — spec_sections and affected_files
# ═══════════════════════════════════════════════════════════════════


def spec_overlap(a: Finding, b: Finding) -> float:
    """Fraction of shared spec_sections. 0.0-1.0."""
    if not a.spec_sections or not b.spec_sections:
        return 0.0
    shared = set(a.spec_sections) & set(b.spec_sections)
    total = set(a.spec_sections) | set(b.spec_sections)
    return len(shared) / len(total)


def file_overlap(a: Finding, b: Finding) -> float:
    """Fraction of shared affected_files. 0.0-1.0."""
    if not a.affected_files or not b.affected_files:
        return 0.0
    shared = set(a.affected_files) & set(b.affected_files)
    total = set(a.affected_files) | set(b.affected_files)
    return len(shared) / len(total)


# ═══════════════════════════════════════════════════════════════════
# Contradiction detection — opposing sentiment heuristics
# ═══════════════════════════════════════════════════════════════════

_POSITIVE_SIGNALS = [
    "should", "must", "implement", "add", "create", "enable",
    "recommend", "adopt", "use", "include", "keep",
    # Arabic scholarly positive signals (Gemini finding #7)
    "\u064a\u062c\u0628",       # يجب (must/obligatory)
    "\u064a\u0646\u0628\u063a\u064a",  # ينبغي (should)
    "\u064a\u062c\u0648\u0632",  # يجوز (permissible)
    "\u064a\u0633\u062a\u062d\u0628",  # يستحب (recommended)
    "\u0645\u0634\u0631\u0648\u0639",  # مشروع (legislated/valid)
]

_NEGATIVE_SIGNALS = [
    "should not", "must not", "remove", "avoid", "drop",
    "do not", "don't", "unnecessary", "reject", "skip",
    "instead of", "rather than", "not recommended",
    # Arabic scholarly negative signals (Gemini finding #7)
    "\u0644\u0627 \u064a\u062c\u0648\u0632",  # لا يجوز (impermissible)
    "\u064a\u062d\u0631\u0645",  # يحرم (prohibited)
    "\u064a\u0643\u0631\u0647",  # يكره (disliked)
    "\u0628\u0627\u0637\u0644",  # باطل (invalid/void)
    "\u0641\u0627\u0633\u062f",  # فاسد (corrupt/defective)
    "\u062a\u062c\u0646\u0628",  # تجنب (avoid)
]


def _sentiment_vector(text: str) -> tuple[int, int]:
    """Count positive and negative action signals."""
    lower = text.lower()
    pos = sum(1 for s in _POSITIVE_SIGNALS if s in lower)
    neg = sum(1 for s in _NEGATIVE_SIGNALS if s in lower)
    return pos, neg


def is_contradictory(a: Finding, b: Finding) -> tuple[bool, str]:
    """Detect if two related findings contradict each other.

    Returns (is_contradiction, reason).
    """
    pos_a, neg_a = _sentiment_vector(a.description)
    pos_b, neg_b = _sentiment_vector(b.description)

    # One is predominantly positive, the other negative (require strong signal)
    a_positive = pos_a > neg_a and pos_a >= 3
    a_negative = neg_a > pos_a and neg_a >= 2
    b_positive = pos_b > neg_b and pos_b >= 3
    b_negative = neg_b > pos_b and neg_b >= 2

    if a_positive and b_negative:
        return True, f"A recommends action ({pos_a} pos signals), B recommends against ({neg_b} neg signals)"
    if a_negative and b_positive:
        return True, f"A recommends against ({neg_a} neg signals), B recommends action ({pos_b} pos signals)"

    # Different severity on the same topic suggests disagreement (only extreme gaps)
    severity_order = {
        FindingSeverity.CRITICAL: 4,
        FindingSeverity.HIGH: 3,
        FindingSeverity.MEDIUM: 2,
        FindingSeverity.LOW: 1,
        FindingSeverity.INFORMATIONAL: 0,
    }
    sev_diff = abs(severity_order[a.severity] - severity_order[b.severity])
    if sev_diff >= 3:
        return True, f"Severity gap: {a.severity.value} vs {b.severity.value} (diff={sev_diff})"

    return False, ""


# ═══════════════════════════════════════════════════════════════════
# Main cross-referencing logic
# ═══════════════════════════════════════════════════════════════════


def compute_relatedness(
    a: Finding, b: Finding,
    tg_a: set[tuple[str, str, str]],
    tg_b: set[tuple[str, str, str]],
) -> float:
    """Compute combined relatedness score between two findings.

    Weighted combination:
    - spec_sections overlap: 0.4
    - affected_files overlap: 0.3
    - text similarity (precomputed trigrams): 0.3

    Returns score 0.0-1.0.
    """
    spec = spec_overlap(a, b)
    files = file_overlap(a, b)
    # Use precomputed trigrams (Gemini finding #5: avoid O(n²) recomputation)
    if not tg_a or not tg_b:
        text_sim = 0.0
    else:
        intersection = len(tg_a & tg_b)
        union = len(tg_a | tg_b)
        text_sim = intersection / union if union > 0 else 0.0
    return 0.4 * spec + 0.3 * files + 0.3 * text_sim


def cross_reference(
    findings: list[Finding],
    min_similarity: float = 0.20,
) -> tuple[dict[str, list[str]], list[Contradiction]]:
    """Cross-reference all findings. Returns (related_map, contradictions).

    related_map: finding_id -> list of related finding_ids
    contradictions: list of detected Contradiction records
    """
    related_map: dict[str, list[str]] = defaultdict(list)
    contradictions: list[Contradiction] = []
    seen_contra_pairs: set[str] = set()

    # Precompute trigrams once per finding (Gemini finding #5: O(n) instead of O(n²))
    trigram_map: dict[str, set[tuple[str, str, str]]] = {}
    for f in findings:
        trigram_map[f.finding_id] = _trigrams(_tokenize(f.title + " " + f.description))

    n = len(findings)
    pairs_checked = 0
    related_found = 0

    for i in range(n):
        for j in range(i + 1, n):
            a, b = findings[i], findings[j]
            pairs_checked += 1

            # Skip same-source pairs (cross-referencing is about CROSS-DR links)
            if a.source_id == b.source_id:
                continue

            score = compute_relatedness(
                a, b, trigram_map[a.finding_id], trigram_map[b.finding_id],
            )
            if score < min_similarity:
                continue

            related_found += 1
            related_map[a.finding_id].append(b.finding_id)
            related_map[b.finding_id].append(a.finding_id)

            # Check for contradiction (only in strongly related pairs, same category)
            if score < 0.35:
                continue
            # Skip cross-domain pairs — scholarly vs engineering contradictions are noise
            if a.category != b.category:
                continue
            is_contra, reason = is_contradictory(a, b)
            if is_contra:
                pair_key = ":".join(sorted([a.finding_id, b.finding_id]))
                if pair_key not in seen_contra_pairs:
                    seen_contra_pairs.add(pair_key)

                    # Build topic from shared spec sections or titles
                    shared_specs = set(a.spec_sections) & set(b.spec_sections)
                    topic = ", ".join(sorted(shared_specs)) if shared_specs else f"{a.title[:50]} vs {b.title[:50]}"

                    contra_id = f"CONTRA-{hashlib.sha256(f'{a.finding_id}:{b.finding_id}'.encode()).hexdigest()[:8]}"
                    contradictions.append(Contradiction(
                        contradiction_id=contra_id,
                        finding_id_a=a.finding_id,
                        finding_id_b=b.finding_id,
                        dr_id_a=a.source_id,
                        dr_id_b=b.source_id,
                        topic=topic,
                        description=reason,
                        resolution_status="unresolved",
                        resolution_notes="",
                    ))

    logger.info(
        "Cross-reference: %d pairs checked, %d related found, %d contradictions",
        pairs_checked, related_found, len(contradictions),
    )
    return dict(related_map), contradictions


# ═══════════════════════════════════════════════════════════════════
# Persistence — update findings with related_finding_ids
# ═══════════════════════════════════════════════════════════════════


def persist_cross_references(
    findings: list[Finding],
    related_map: dict[str, list[str]],
    contradictions: list[Contradiction],
) -> None:
    """Rewrite findings.jsonl with updated related_finding_ids + write contradictions."""
    # Update findings in place
    updated_count = 0
    for f in findings:
        if f.finding_id in related_map:
            f.related_finding_ids = sorted(set(related_map[f.finding_id]))
            updated_count += 1

    # Rewrite findings.jsonl (atomic: write tmp then rename)
    # Codex finding #3: Windows NTFS .replace() can fail if dashboard has file open.
    # Retry with backoff to handle concurrent reader PermissionError.
    import time
    tmp_path = FINDINGS_JSONL.with_suffix(".jsonl.tmp")
    with open(tmp_path, "w", encoding="utf-8") as fh:
        for f in findings:
            fh.write(f.model_dump_json() + "\n")
    for attempt in range(5):
        try:
            tmp_path.replace(FINDINGS_JSONL)
            break
        except PermissionError:
            if attempt < 4:
                time.sleep(0.2 * (attempt + 1))
            else:
                raise
    logger.info("Updated %d findings with cross-references in %s", updated_count, FINDINGS_JSONL)

    # Rewrite contradictions.jsonl atomically (not append — prevents duplication)
    if contradictions:
        tmp_contra = CONTRADICTIONS_JSONL.with_suffix(".jsonl.tmp")
        with open(tmp_contra, "w", encoding="utf-8") as fh:
            for c in contradictions:
                fh.write(c.model_dump_json() + "\n")
        for attempt in range(5):
            try:
                tmp_contra.replace(CONTRADICTIONS_JSONL)
                break
            except PermissionError:
                if attempt < 4:
                    time.sleep(0.2 * (attempt + 1))
                else:
                    raise
        logger.info("Wrote %d contradictions to %s", len(contradictions), CONTRADICTIONS_JSONL)


# ═══════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Cross-reference findings across DR responses")
    parser.add_argument("--min-similarity", type=float, default=0.20, help="Minimum relatedness score (0.0-1.0)")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    findings: list[Finding] = [f for f in findings_raw if isinstance(f, Finding)]

    if not findings:
        logger.info("No findings to cross-reference.")
        return

    logger.info("Loaded %d findings from %s", len(findings), FINDINGS_JSONL)

    related_map, contradictions = cross_reference(findings, args.min_similarity)

    # Summary
    print(f"\n{'=' * 60}")
    print("CROSS-REFERENCE RESULTS")
    print(f"{'=' * 60}")
    print(f"  Findings analyzed:  {len(findings)}")
    print(f"  With cross-refs:    {len(related_map)}")
    print(f"  Contradictions:     {len(contradictions)}")

    if contradictions:
        print(f"\n  Contradictions detected:")
        for c in contradictions:
            print(f"    {c.contradiction_id}: {c.topic}")
            print(f"      {c.finding_id_a} vs {c.finding_id_b}")
            print(f"      Reason: {c.description}")

    # DR-level summary
    dr_ids = {f.source_id for f in findings}
    print(f"\n  DR sources involved: {', '.join(sorted(dr_ids))}")

    if not args.dry_run:
        persist_cross_references(findings, related_map, contradictions)
        print(f"\n  Persisted to: {KB_DIR}")
    else:
        print(f"\n  [DRY RUN — no files written]")


if __name__ == "__main__":
    main()
