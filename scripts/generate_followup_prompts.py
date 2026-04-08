"""Generate follow-up DR prompts from findings and contradictions (Component D).

Reads:
- Findings with action_required containing "follow-up" or "research needed"
- Findings classified as role="question" during parsing
- Unresolved contradictions that need clarification

Generates DRPrompt records targeting the appropriate provider (routes away from
the original source for cross-model confirmation per no-single-model-conclusion).

Usage:
    python scripts/generate_followup_prompts.py
    python scripts/generate_followup_prompts.py --batch batch_3 --dry-run
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.autonomous_schemas import (
    CONTRADICTIONS_JSONL,
    FINDINGS_JSONL,
    PROMPTS_DIR,
    Contradiction,
    DRPrompt,
    DRTarget,
    Finding,
    Priority,
    ResearchCategory,
    VerificationStatus,
    append_jsonl,
    load_dr_index,
    read_jsonl,
)

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════════
# Provider routing — cross-model for independent confirmation
# ═══════════════════════════════════════════════════════════════════

# Route to a different provider than the original source.
# CODEX is never a valid follow-up target (it runs code, not research).
# Codex findings route to Claude for DR cross-validation.
_CROSSMODEL_ROUTES: dict[DRTarget, DRTarget] = {
    DRTarget.CHATGPT: DRTarget.CLAUDE,
    DRTarget.CLAUDE: DRTarget.GEMINI,
    DRTarget.GEMINI: DRTarget.CHATGPT,
    DRTarget.CODEX: DRTarget.CLAUDE,
}

# Category-based preferred targets (override cross-model when strong signal)
_CATEGORY_PREFERENCE: dict[ResearchCategory, DRTarget] = {
    ResearchCategory.SCHOLARLY_DOMAIN: DRTarget.GEMINI,
    ResearchCategory.ARCHITECTURE: DRTarget.CHATGPT,
    ResearchCategory.ENGINE_SPECIFIC: DRTarget.CLAUDE,
}


def route_provider(
    original_source: DRTarget | None, category: ResearchCategory,
) -> DRTarget:
    """Pick the best provider for a follow-up prompt.

    Uses category preference but NEVER routes back to the original source
    (Gemini finding #6: enforce cross-model confirmation).
    """
    preferred = _CATEGORY_PREFERENCE.get(category, DRTarget.GEMINI)

    # If preferred == original source, use cross-model route instead
    if original_source is not None and preferred == original_source:
        return _CROSSMODEL_ROUTES.get(original_source, DRTarget.CLAUDE)

    return preferred


def route_contradiction(
    dr_id_a: str, dr_id_b: str,
    provider_map: dict[str, DRTarget],
) -> DRTarget:
    """Pick a third-party provider to resolve a contradiction.

    SFH finding #11: avoids providers involved in either side.
    """
    involved = {provider_map.get(dr_id_a), provider_map.get(dr_id_b)}
    all_targets = {DRTarget.CHATGPT, DRTarget.CLAUDE, DRTarget.GEMINI}
    available = all_targets - involved - {None}
    if available:
        # Prefer Gemini for scholarly tiebreaking
        if DRTarget.GEMINI in available:
            return DRTarget.GEMINI
        return available.pop()
    logger.warning("All providers involved in contradiction %s vs %s", dr_id_a, dr_id_b)
    return DRTarget.GEMINI


# ═══════════════════════════════════════════════════════════════════
# Prompt generation from findings
# ═══════════════════════════════════════════════════════════════════

_FOLLOWUP_TRIGGERS = [
    "follow-up", "research needed", "further research",
    "generate follow-up", "unclear", "needs clarification",
]


def needs_followup(finding: Finding) -> bool:
    """Check if a finding needs a follow-up DR prompt.

    PRELIMINARY findings are gated: single-model findings must not
    drive follow-up prompt generation (D-041 / OPS-DEC-006).
    """
    if finding.resolved:
        return False
    if finding.verification_status == VerificationStatus.PRELIMINARY:
        return False
    if finding.verification_status == VerificationStatus.DISPUTED:
        return False
    action_lower = finding.action_required.lower()
    return any(trigger in action_lower for trigger in _FOLLOWUP_TRIGGERS)


def finding_to_prompt(
    finding: Finding, batch: str, prompt_counter: int,
    original_provider: DRTarget | None = None,
) -> DRPrompt:
    """Convert a finding into a follow-up DR prompt."""
    target = route_provider(original_provider, finding.category)

    # Build the prompt text
    context_parts = [
        f"CONTEXT: A previous DR analysis ({finding.source_id}) produced the following finding:",
        f"",
        f"Title: {finding.title}",
        f"Severity: {finding.severity.value}",
    ]
    if finding.spec_sections:
        context_parts.append(f"SPEC sections: {', '.join(finding.spec_sections)}")
    if finding.affected_files:
        context_parts.append(f"Affected files: {', '.join(finding.affected_files)}")

    context_parts.extend([
        f"",
        f"Finding description:",
        f"{finding.description[:1500]}",
        f"",
        f"QUESTION: {finding.action_required}",
        f"",
        f"Please provide:",
        f"1. Your independent assessment of this finding",
        f"2. Concrete recommendations with specific file/section references",
        f"3. Any risks or trade-offs the original analysis may have missed",
    ])

    prompt_text = "\n".join(context_parts)

    # Map finding severity to prompt priority
    severity_to_priority = {
        "critical": Priority.CRITICAL,
        "high": Priority.HIGH,
        "medium": Priority.MEDIUM,
        "low": Priority.LOW,
        "informational": Priority.LOW,
    }
    priority = severity_to_priority.get(finding.severity.value, Priority.MEDIUM)

    prompt_id = f"RQ-{batch.upper()}-{prompt_counter:03d}"

    return DRPrompt(
        prompt_id=prompt_id,
        target=target,
        category=finding.category,
        priority=priority,
        topic=f"Follow-up: {finding.title[:80]}",
        prompt_text=prompt_text,
        unblocks=f"Resolution of {finding.finding_id}",
        file_bundle=None,
        estimated_minutes=20,
        dedup_hash="",
        batch=batch,
    )


# ═══════════════════════════════════════════════════════════════════
# Prompt generation from contradictions
# ═══════════════════════════════════════════════════════════════════


def contradiction_to_prompt(
    contradiction: Contradiction,
    finding_a: Finding | None,
    finding_b: Finding | None,
    batch: str,
    prompt_counter: int,
    provider_map: dict[str, DRTarget] | None = None,
) -> DRPrompt:
    """Convert an unresolved contradiction into a resolution prompt."""
    target = route_contradiction(
        contradiction.dr_id_a, contradiction.dr_id_b,
        provider_map or {},
    )

    parts = [
        f"CONTEXT: Two independent DR analyses produced contradictory findings on the same topic.",
        f"",
        f"Topic: {contradiction.topic}",
        f"",
        f"Finding A ({contradiction.dr_id_a}):",
    ]
    if finding_a:
        parts.append(f"  Title: {finding_a.title}")
        parts.append(f"  Severity: {finding_a.severity.value}")
        parts.append(f"  Description: {finding_a.description[:800]}")
    else:
        parts.append(f"  [Finding {contradiction.finding_id_a} not loaded]")

    parts.extend([
        f"",
        f"Finding B ({contradiction.dr_id_b}):",
    ])
    if finding_b:
        parts.append(f"  Title: {finding_b.title}")
        parts.append(f"  Severity: {finding_b.severity.value}")
        parts.append(f"  Description: {finding_b.description[:800]}")
    else:
        parts.append(f"  [Finding {contradiction.finding_id_b} not loaded]")

    parts.extend([
        f"",
        f"Contradiction: {contradiction.description}",
        f"",
        f"QUESTION: As an independent third party, please:",
        f"1. Assess which finding is more correct, with reasoning",
        f"2. Identify any nuance both sides missed",
        f"3. Provide a recommended resolution",
    ])

    prompt_id = f"RQ-{batch.upper()}-{prompt_counter:03d}"

    return DRPrompt(
        prompt_id=prompt_id,
        target=target,
        category=ResearchCategory.CROSS_CUTTING,
        priority=Priority.HIGH,
        topic=f"Resolve contradiction: {contradiction.topic[:60]}",
        prompt_text="\n".join(parts),
        file_bundle=None,
        dedup_hash="",
        unblocks=f"Resolution of {contradiction.contradiction_id}",
        estimated_minutes=25,
        batch=batch,
    )


# ═══════════════════════════════════════════════════════════════════
# Deduplication
# ═══════════════════════════════════════════════════════════════════


def dedup_prompts(
    new_prompts: list[DRPrompt], existing_hashes: set[str],
) -> list[DRPrompt]:
    """Remove prompts whose dedup_hash already exists."""
    unique: list[DRPrompt] = []
    for p in new_prompts:
        if p.dedup_hash in existing_hashes:
            logger.debug("Skipping duplicate prompt: %s (hash %s)", p.prompt_id, p.dedup_hash)
            continue
        existing_hashes.add(p.dedup_hash)
        unique.append(p)
    return unique


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════


def generate_followups(
    batch: str = "auto",
) -> list[DRPrompt]:
    """Generate follow-up prompts from findings and contradictions."""
    # Load existing prompts for dedup (by hash AND by unblocks target)
    # Codex finding #11: dedup must prevent re-generation for already-prompted items
    existing_hashes: set[str] = set()
    existing_unblocks: set[str] = set()
    for jsonl_file in sorted(PROMPTS_DIR.glob("*.jsonl")) if PROMPTS_DIR.exists() else []:
        index = load_dr_index(jsonl_file)
        for p in index.values():
            existing_hashes.add(p.dedup_hash)
            existing_unblocks.add(p.unblocks)

    logger.info("Loaded %d existing prompt hashes for dedup", len(existing_hashes))

    # Load findings
    findings_raw = read_jsonl(FINDINGS_JSONL, Finding)
    findings: list[Finding] = [f for f in findings_raw if isinstance(f, Finding)]
    findings_by_id = {f.finding_id: f for f in findings}

    # Load DR responses to resolve finding -> provider mapping
    # SFH finding #6: log when missing — cross-model routing degrades silently
    from scripts.autonomous_schemas import DR_RESPONSES_JSONL, DRResponse
    dr_provider_map: dict[str, DRTarget] = {}
    if DR_RESPONSES_JSONL.exists():
        resp_raw = read_jsonl(DR_RESPONSES_JSONL, DRResponse)
        for r in resp_raw:
            if isinstance(r, DRResponse):
                dr_provider_map[r.response_id] = r.source
    else:
        logger.warning(
            "dr_responses.jsonl not found — cross-model routing DISABLED, "
            "follow-ups will use category preference only (may route back to same provider)"
        )

    # Load contradictions
    contras_raw = read_jsonl(CONTRADICTIONS_JSONL, Contradiction)
    contradictions: list[Contradiction] = [
        c for c in contras_raw
        if isinstance(c, Contradiction) and c.resolution_status == "unresolved"
    ]

    new_prompts: list[DRPrompt] = []
    counter = 1

    # From findings needing follow-up (skip if already prompted)
    for f in findings:
        if needs_followup(f):
            unblocks_key = f"Resolution of {f.finding_id}"
            if unblocks_key in existing_unblocks:
                continue
            original_provider = dr_provider_map.get(f.source_id)
            new_prompts.append(finding_to_prompt(f, batch, counter, original_provider))
            counter += 1

    # From unresolved contradictions (skip if already prompted)
    for c in contradictions:
        unblocks_key = f"Resolution of {c.contradiction_id}"
        if unblocks_key in existing_unblocks:
            continue
        finding_a = findings_by_id.get(c.finding_id_a)
        finding_b = findings_by_id.get(c.finding_id_b)
        new_prompts.append(contradiction_to_prompt(
            c, finding_a, finding_b, batch, counter, dr_provider_map,
        ))
        counter += 1

    # Dedup against existing
    unique = dedup_prompts(new_prompts, existing_hashes)
    logger.info(
        "Generated %d prompts (%d after dedup, %d from findings, %d from contradictions)",
        len(new_prompts), len(unique),
        sum(1 for f in findings if needs_followup(f)),
        len(contradictions),
    )

    return unique


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Generate follow-up DR prompts")
    parser.add_argument("--batch", default="auto", help="Batch name for new prompts")
    parser.add_argument("--dry-run", action="store_true", help="Report without writing")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")

    prompts = generate_followups(batch=args.batch)

    print(f"\n{'=' * 60}")
    print("FOLLOW-UP PROMPT GENERATION")
    print(f"{'=' * 60}")
    print(f"  Prompts generated: {len(prompts)}")

    for p in prompts:
        print(f"    {p.prompt_id}: [{p.target.value}] {p.topic[:60]}")

    if prompts and not args.dry_run:
        batch_file = PROMPTS_DIR / f"{args.batch}.jsonl"
        PROMPTS_DIR.mkdir(parents=True, exist_ok=True)
        for p in prompts:
            append_jsonl(batch_file, p)
        print(f"\n  Persisted to: {batch_file}")
    elif args.dry_run:
        print(f"\n  [DRY RUN — no files written]")
    else:
        print(f"\n  No follow-up prompts needed.")


if __name__ == "__main__":
    main()
