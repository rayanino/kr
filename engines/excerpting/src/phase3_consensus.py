"""Phase 3: Consensus Verification and Human Gates (SPEC §7.3).

Cross-provider verification for high-epistemic-impact decisions
(attribution, school). Triggers human gates for unresolvable uncertainty.

Uses a different-provider model (openai/gpt-4.1 by default) for
structural independence from the enrichment model (Opus 4.6).
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import Optional

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    ConsensusDecision,
    ConsensusRecord,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    SelfContainmentLevel,
    VerificationItem,
    VerificationResult,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# §7.3.2 — Verification Prompt
# ═══════════════════════════════════════════════════════════════════

VERIFY_SYSTEM_PROMPT = """\
You are verifying metadata decisions made by another model on Arabic Islamic
scholarly text. For each item below, independently assess whether the decision
is correct."""


def _needs_consensus(excerpt: ExcerptRecord) -> list[dict[str, str]]:
    """Determine which decisions on this excerpt require consensus (§7.3.1).

    Returns list of verification items to include in the prompt.
    Each item has: verification_type, decision_text, unit_text.
    """
    items: list[dict[str, str]] = []

    # School attribution: school is non-null
    if excerpt.school is not None:
        items.append({
            "verification_type": "SCHOOL_ATTRIBUTION",
            "decision_text": (
                f'School attributed as "{excerpt.school}". '
                f"Is this correct given the text content?"
            ),
            "unit_text": excerpt.primary_text[:500],
        })

    # Author attribution: LA-3 (ambiguous)
    if excerpt.primary_author_layer.rule_applied == "LA-3":
        items.append({
            "verification_type": "AUTHOR_ATTRIBUTION",
            "decision_text": (
                f"Unit attributed to {excerpt.primary_author_layer.author_id} "
                f"(layer {excerpt.primary_author_layer.layer_id}, "
                f"{excerpt.primary_author_layer.coverage_pct * 100:.0f}% coverage, "
                f"rule LA-3). Is this attribution correct, or should it be "
                f"attributed differently?"
            ),
            "unit_text": excerpt.primary_text[:500],
        })

    # Self-containment: PARTIAL or DEPENDENT
    if excerpt.self_containment in (
        SelfContainmentLevel.PARTIAL,
        SelfContainmentLevel.DEPENDENT,
    ):
        items.append({
            "verification_type": "SELF_CONTAINMENT",
            "decision_text": (
                f"Unit assessed as {excerpt.self_containment.value}. "
                f"Notes: {excerpt.self_containment_notes or 'none'}. "
                f"Is this assessment correct?"
            ),
            "unit_text": excerpt.primary_text[:500],
        })

    return items


def _build_verification_user_message(
    excerpts_with_items: list[tuple[ExcerptRecord, list[dict[str, str]]]],
    source_metadata: dict[str, str],
) -> str:
    """Build verification prompt per §7.3.2 template."""
    parts: list[str] = []

    parts.append("Source context:")
    parts.append(f"- Author: {source_metadata.get('author_name', 'unknown')}")
    parts.append(f"- Work: {source_metadata.get('work_title', 'unknown')}")
    parts.append(f"- Science: {source_metadata.get('science', 'unknown')}")
    parts.append(f"- School: {source_metadata.get('source_school', 'unknown')}")
    parts.append("")

    item_index = 0
    for _exc, items in excerpts_with_items:
        for item in items:
            parts.append(f"ITEM {item_index}: {item['verification_type']}")
            parts.append(f'Text: "{item["unit_text"]}"')
            parts.append(f"Decision: {item['decision_text']}")
            parts.append(
                "Your assessment: agree or disagree, with brief reasoning "
                "in Arabic or English."
            )
            parts.append("If you disagree, provide your alternative.")
            parts.append(
                "Provide your confidence (0.0 to 1.0) in your own assessment."
            )
            parts.append("")
            item_index += 1

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════
# Function 1: verify_chunk
# ═══════════════════════════════════════════════════════════════════


def verify_chunk(
    chunk: AssembledChunk,
    excerpts: list[ExcerptRecord],
    client: instructor.Instructor,
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> Optional[tuple[VerificationResult, list[tuple[ExcerptRecord, list[dict[str, str]]]]]]:
    """Call verification model for attribution + school checks (§7.3.2).

    Uses VERIFY_MODEL (different provider family from ENRICH_MODEL).
    Returns None if no units in this chunk need verification.
    Otherwise returns (VerificationResult, items_map) for resolve_consensus.
    """
    if source_metadata is None:
        source_metadata = {}

    # Collect units needing verification
    excerpts_with_items: list[tuple[ExcerptRecord, list[dict[str, str]]]] = []
    for exc in excerpts:
        items = _needs_consensus(exc)
        if items:
            excerpts_with_items.append((exc, items))

    if not excerpts_with_items:
        return None

    user_message = _build_verification_user_message(
        excerpts_with_items, source_metadata
    )

    result = client.chat.completions.create(
        model=config.VERIFY_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.VERIFY_MAX_TOKENS,
        max_retries=0,
        response_model=VerificationResult,
        messages=[
            {"role": "system", "content": VERIFY_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )

    return result, excerpts_with_items


# ═══════════════════════════════════════════════════════════════════
# Function 2: resolve_consensus
# ═══════════════════════════════════════════════════════════════════


def resolve_consensus(
    excerpt: ExcerptRecord,
    verification_items: list[VerificationItem],
    item_types: list[str],
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> tuple[ExcerptRecord, Optional[ConsensusRecord], list[str]]:
    """Resolve disagreements between enrichment and verification (§7.3.3).

    Returns:
        (updated_excerpt, consensus_record, gate_codes)
    """
    if source_metadata is None:
        source_metadata = {}

    decisions: list[ConsensusDecision] = []
    gate_codes: list[str] = []
    updates: dict[str, object] = {}
    review_flags = list(excerpt.review_flags)

    for vi, vtype in zip(verification_items, item_types):
        if vtype == "SCHOOL_ATTRIBUTION":
            decision, new_updates, new_flags, new_gates = _resolve_school(
                excerpt, vi, source_metadata
            )
        elif vtype == "AUTHOR_ATTRIBUTION":
            decision, new_updates, new_flags, new_gates = _resolve_attribution(
                excerpt, vi, escalation_client, config, source_metadata
            )
        elif vtype == "SELF_CONTAINMENT":
            decision, new_updates, new_flags, new_gates = _resolve_self_containment(
                excerpt, vi
            )
        else:
            continue

        decisions.append(decision)
        updates.update(new_updates)
        review_flags.extend(new_flags)
        gate_codes.extend(new_gates)

    # Set consensus_metadata FIRST — _repair_context_hint reads it
    if decisions:
        updates["consensus_metadata"] = ConsensusRecord(decisions=decisions)

    # Apply context_hint repair after all consensus decisions
    updates = _repair_context_hint(excerpt, updates)

    updates["review_flags"] = review_flags

    updated = excerpt.model_copy(update=updates)
    # consensus_record already in updates; return None for backward compat
    return updated, None, gate_codes


def _resolve_school(
    excerpt: ExcerptRecord,
    vi: VerificationItem,
    source_metadata: dict[str, str],
) -> tuple[ConsensusDecision, dict[str, object], list[str], list[str]]:
    """§7.3.3 School attribution disagreement resolution."""
    updates: dict[str, object] = {}
    flags: list[str] = []
    gates: list[str] = []

    if vi.agrees:
        decision = ConsensusDecision(
            decision_type="school_attribution",
            enrichment_value=excerpt.school or "",
            verifier_value=excerpt.school or "",
            verifier_agrees=True,
            final_value=excerpt.school or "",
            resolution_method="consensus_agree",
        )
    else:
        # Disagreement: keep enrichment school, lower confidence, flag
        lower_confidence = min(
            excerpt.school_confidence or 0.0,
            vi.confidence,
        )
        updates["school_confidence"] = lower_confidence
        flags.append("school_consensus_disagreement")

        logger.warning(
            "%s: School disagreement for %s — enrichment=%s, verifier=%s",
            ExcerptingErrorCodes.EX_M_003,
            excerpt.excerpt_id,
            excerpt.school,
            vi.alternative,
        )

        decision = ConsensusDecision(
            decision_type="school_attribution",
            enrichment_value=excerpt.school or "",
            verifier_value=vi.alternative or "",
            verifier_agrees=False,
            final_value=excerpt.school or "",
            resolution_method="enrichment_kept_flagged",
        )

        # Check EX-G-003: school conflicts with source metadata AND both models disagree
        source_school = source_metadata.get("source_school")
        if (
            source_school
            and source_school != excerpt.school
            and vi.alternative
            and vi.alternative != source_school
        ):
            gates.append(ExcerptingErrorCodes.EX_G_003)

    return decision, updates, flags, gates


def _resolve_attribution(
    excerpt: ExcerptRecord,
    vi: VerificationItem,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
    source_metadata: dict[str, str],
) -> tuple[ConsensusDecision, dict[str, object], list[str], list[str]]:
    """§7.3.3 Author attribution disagreement (LA-3 cases)."""
    updates: dict[str, object] = {}
    flags: list[str] = []
    gates: list[str] = []

    if vi.agrees:
        updates["attribution_confidence"] = 1.0
        decision = ConsensusDecision(
            decision_type="author_attribution",
            enrichment_value=excerpt.primary_author_layer.author_id,
            verifier_value=excerpt.primary_author_layer.author_id,
            verifier_agrees=True,
            final_value=excerpt.primary_author_layer.author_id,
            resolution_method="consensus_agree",
        )
    else:
        # Escalate to 3rd model
        flags.append("attribution_consensus_escalated")
        escalation_value: Optional[str] = None

        if escalation_client is not None:
            escalation_value = _call_escalation(
                excerpt, vi, escalation_client, config, source_metadata
            )

        enrichment_val = excerpt.primary_author_layer.author_id
        verifier_val = vi.alternative  # None if no alternative provided

        if escalation_value is not None:
            # Filter out None votes for majority calculation
            real_votes = [v for v in [enrichment_val, verifier_val, escalation_value] if v is not None]
            if len(real_votes) >= 2:
                majority = _find_majority_flexible(real_votes)
            else:
                majority = None

            if majority is not None:
                updates["attribution_confidence"] = 0.67
                if majority != enrichment_val:
                    updates["primary_author_layer"] = excerpt.primary_author_layer.model_copy(
                        update={
                            "author_id": majority,
                            "rule_applied": "LA-3_consensus",
                        }
                    )
                decision = ConsensusDecision(
                    decision_type="author_attribution",
                    enrichment_value=enrichment_val,
                    verifier_value=verifier_val or "abstained",
                    verifier_agrees=False,
                    escalation_value=escalation_value,
                    final_value=majority,
                    resolution_method="majority_2_of_3",
                )
            else:
                # All 3 disagree → EX-G-001
                updates["attribution_confidence"] = 0.0
                gates.append(ExcerptingErrorCodes.EX_G_001)
                decision = ConsensusDecision(
                    decision_type="author_attribution",
                    enrichment_value=enrichment_val,
                    verifier_value=verifier_val or "abstained",
                    verifier_agrees=False,
                    escalation_value=escalation_value,
                    final_value=enrichment_val,
                    resolution_method="all_3_disagree_gate",
                )
        else:
            # No escalation client — treat as 2-model disagreement, use enrichment
            updates["attribution_confidence"] = 0.5
            decision = ConsensusDecision(
                decision_type="author_attribution",
                enrichment_value=enrichment_val,
                verifier_value=verifier_val or "abstained",
                verifier_agrees=False,
                final_value=enrichment_val,
                resolution_method="no_escalation_enrichment_kept",
            )

    return decision, updates, flags, gates


def _call_escalation(
    excerpt: ExcerptRecord,
    vi: VerificationItem,
    escalation_client: instructor.Instructor,
    config: ExcerptingConfig,
    source_metadata: dict[str, str],
) -> Optional[str]:
    """Call 3rd model for author attribution escalation (§7.3.3)."""
    prompt = (
        f"Two models disagree on the author attribution of this Arabic text.\n\n"
        f"Text: \"{excerpt.primary_text[:500]}\"\n\n"
        f"Source: {source_metadata.get('author_name', 'unknown')} - "
        f"{source_metadata.get('work_title', 'unknown')}\n\n"
        f"Model 1 says: {excerpt.primary_author_layer.author_id} "
        f"(layer: {excerpt.primary_author_layer.layer_id})\n"
        f"Model 2 says: {vi.alternative or 'unknown'} "
        f"(reasoning: {vi.reasoning})\n\n"
        f"Which attribution is correct? Respond with just the author ID."
    )

    try:
        # Simple text response for escalation — we just need a string
        from pydantic import BaseModel, Field

        class EscalationResponse(BaseModel):
            author_id: str = Field(description="The correct author attribution")
            reasoning: str = Field(description="Brief explanation")

        result = escalation_client.chat.completions.create(
            model=config.ESCALATION_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=1024,
            max_retries=0,
            response_model=EscalationResponse,
            messages=[
                {"role": "user", "content": prompt},
            ],
        )
        return result.author_id
    except Exception as e:
        logger.warning(
            "Escalation call failed for %s: %s", excerpt.excerpt_id, str(e)
        )
        return None


def _find_majority(votes: list[str]) -> Optional[str]:
    """Find 2-of-3 majority. Returns None if all 3 differ."""
    if votes[0] == votes[1]:
        return votes[0]
    if votes[0] == votes[2]:
        return votes[0]
    if votes[1] == votes[2]:
        return votes[1]
    return None


def _find_majority_flexible(votes: list[str]) -> Optional[str]:
    """Find majority among 2 or 3 real votes. Returns None if no majority."""
    from collections import Counter
    counts = Counter(votes)
    for val, count in counts.most_common():
        if count >= 2:
            return val
    return None


def _resolve_self_containment(
    excerpt: ExcerptRecord,
    vi: VerificationItem,
) -> tuple[ConsensusDecision, dict[str, object], list[str], list[str]]:
    """§7.3.3 Self-containment disagreement: use more conservative (lower) level."""
    updates: dict[str, object] = {}
    flags: list[str] = []
    gates: list[str] = []

    _LEVEL_ORDER = {
        SelfContainmentLevel.FULL: 2,
        SelfContainmentLevel.PARTIAL: 1,
        SelfContainmentLevel.DEPENDENT: 0,
    }

    enrichment_level = excerpt.self_containment

    if vi.agrees:
        decision = ConsensusDecision(
            decision_type="self_containment",
            enrichment_value=enrichment_level.value,
            verifier_value=enrichment_level.value,
            verifier_agrees=True,
            final_value=enrichment_level.value,
            resolution_method="consensus_agree",
        )
    else:
        # Parse verifier's alternative
        verifier_level = _parse_self_containment(vi.alternative)
        if verifier_level is None:
            verifier_level = enrichment_level

        # Use the more conservative (lower) level
        if _LEVEL_ORDER.get(verifier_level, 1) < _LEVEL_ORDER.get(enrichment_level, 1):
            final_level = verifier_level
        else:
            final_level = enrichment_level

        if final_level != enrichment_level:
            updates["self_containment"] = final_level

        # DEPENDENT after consensus → EX-G-002
        if final_level == SelfContainmentLevel.DEPENDENT:
            gates.append(ExcerptingErrorCodes.EX_G_002)

        decision = ConsensusDecision(
            decision_type="self_containment",
            enrichment_value=enrichment_level.value,
            verifier_value=verifier_level.value,
            verifier_agrees=False,
            final_value=final_level.value,
            resolution_method="conservative_lower",
        )

    return decision, updates, flags, gates


def _parse_self_containment(text: Optional[str]) -> Optional[SelfContainmentLevel]:
    """Parse a self-containment level from verifier text."""
    if text is None:
        return None
    text_upper = text.strip().upper()
    for level in SelfContainmentLevel:
        if text_upper == level.value:
            return level
    _LEVEL_ORDER = {
        SelfContainmentLevel.FULL: 2,
        SelfContainmentLevel.PARTIAL: 1,
        SelfContainmentLevel.DEPENDENT: 0,
    }
    matches = [level for level in SelfContainmentLevel if level.value in text_upper]
    if matches:
        return min(matches, key=lambda l: _LEVEL_ORDER.get(l, 1))
    return None


def _repair_context_hint(
    excerpt: ExcerptRecord,
    updates: dict[str, object],
) -> dict[str, object]:
    """Post-consensus context_hint repair (§7.3.3 — critical).

    - FULL → PARTIAL: generate hint from self_containment_notes
    - Any → DEPENDENT: set hint to null
    - Consensus keeps level: no repair
    """
    new_level = updates.get("self_containment", excerpt.self_containment)

    if new_level == SelfContainmentLevel.DEPENDENT:
        updates["context_hint"] = None
    elif (
        new_level == SelfContainmentLevel.PARTIAL
        and excerpt.self_containment == SelfContainmentLevel.FULL
    ):
        # FULL→PARTIAL: enrichment LLM didn't produce a hint (saw FULL)
        # Repair: use self_containment_notes or a fallback
        if excerpt.self_containment_notes:
            updates["context_hint"] = excerpt.self_containment_notes
        else:
            # Get verifier reasoning from consensus decisions if available
            consensus = updates.get("consensus_metadata")
            if isinstance(consensus, ConsensusRecord):
                for d in consensus.decisions:
                    if d.decision_type == "self_containment" and d.verifier_value:
                        updates["context_hint"] = (
                            f"تم تعديل التقييم من مكتفٍ ذاتياً إلى جزئي"
                        )
                        break
            if "context_hint" not in updates:
                updates["context_hint"] = "يحتاج سياقاً إضافياً"

    return updates


# ═══════════════════════════════════════════════════════════════════
# Function 3: check_gate_triggers
# ═══════════════════════════════════════════════════════════════════


def check_gate_triggers(
    excerpt: ExcerptRecord,
    manifest_metadata: dict[str, str],
    config: ExcerptingConfig,
) -> list[str]:
    """Check human gate trigger conditions (§7.3.4).

    EX-G-001: All 3 models disagree on attribution (checked in resolve_consensus).
    EX-G-002: DEPENDENT self-containment after consensus.
    EX-G-003: School attribution conflicts with source metadata AND both models disagree.
    """
    gates: list[str] = []

    # EX-G-001: already checked during resolve_consensus,
    # but also catch any 0.0 attribution_confidence
    if (
        config.GATE_ON_ATTRIBUTION_DISAGREEMENT
        and excerpt.attribution_confidence == 0.0
        and excerpt.primary_author_layer.rule_applied == "LA-3"
    ):
        if ExcerptingErrorCodes.EX_G_001 not in excerpt.gate_flags:
            gates.append(ExcerptingErrorCodes.EX_G_001)

    # EX-G-002: DEPENDENT after consensus
    if (
        config.GATE_ON_DEPENDENT
        and excerpt.self_containment == SelfContainmentLevel.DEPENDENT
    ):
        if ExcerptingErrorCodes.EX_G_002 not in excerpt.gate_flags:
            gates.append(ExcerptingErrorCodes.EX_G_002)

    # EX-G-003: School conflicts with source metadata
    source_school = manifest_metadata.get("source_school")
    if (
        config.GATE_ON_SCHOOL_CONFLICT
        and source_school
        and excerpt.school is not None
        and excerpt.school != source_school
        and "school_consensus_disagreement" in excerpt.review_flags
    ):
        verifier_also_conflicts = True  # Conservative default
        if excerpt.consensus_metadata:
            for d in excerpt.consensus_metadata.decisions:
                if d.decision_type == "school_attribution" and d.verifier_value is not None:
                    verifier_also_conflicts = (d.verifier_value != source_school)
                    break
        if verifier_also_conflicts:
            if ExcerptingErrorCodes.EX_G_003 not in excerpt.gate_flags:
                gates.append(ExcerptingErrorCodes.EX_G_003)

    return gates


# ═══════════════════════════════════════════════════════════════════
# Function 4: run_consensus
# ═══════════════════════════════════════════════════════════════════


def _build_gate_entry(
    excerpt: ExcerptRecord,
    gate_code: str,
    source_metadata: dict[str, str],
) -> dict[str, object]:
    """Build a gate queue entry per §7.3.4 format."""
    import datetime

    assessments: list[dict[str, str]] = []
    if excerpt.consensus_metadata:
        for d in excerpt.consensus_metadata.decisions:
            assessments.append({
                "decision_type": d.decision_type,
                "enrichment_value": d.enrichment_value,
                "verifier_value": d.verifier_value or "",
                "escalation_value": d.escalation_value or "",
                "final_value": d.final_value,
                "resolution_method": d.resolution_method,
            })

    return {
        "excerpt_id": excerpt.excerpt_id,
        "gate_code": gate_code,
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "context": {
            "primary_text_snippet": excerpt.primary_text[:200],
            "assessments": assessments,
            "source_metadata": source_metadata,
            "self_containment": excerpt.self_containment.value,
            "school": excerpt.school,
            "attribution": {
                "layer_id": excerpt.primary_author_layer.layer_id,
                "author_id": excerpt.primary_author_layer.author_id,
                "rule_applied": excerpt.primary_author_layer.rule_applied,
            },
        },
        "status": "pending",
    }


def run_consensus(
    excerpts: list[ExcerptRecord],
    chunks: list[AssembledChunk],
    enrich_client: instructor.Instructor,
    verify_client: instructor.Instructor,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> tuple[list[ExcerptRecord], list[dict[str, object]]]:
    """Execute consensus verification for all excerpts (§7.3).

    Returns:
        excerpts: Updated ExcerptRecords with consensus metadata.
        gate_entries: Human gate entries to write (EX-G-001/002/003).
    """
    if source_metadata is None:
        source_metadata = {}

    chunk_map: dict[str, AssembledChunk] = {c.chunk_id: c for c in chunks}
    excerpts_by_chunk: dict[str, list[ExcerptRecord]] = defaultdict(list)
    for exc in excerpts:
        chunk_id = exc.div_id
        if chunk_id not in chunk_map:
            split_id = f"{exc.div_id}_chunk_{exc.chunk_index}"
            if split_id in chunk_map:
                chunk_id = split_id
            else:
                alt_id = f"{exc.div_id}_{exc.chunk_index}"
                if alt_id in chunk_map:
                    chunk_id = alt_id
        excerpts_by_chunk[chunk_id].append(exc)

    all_results: list[ExcerptRecord] = []
    all_gates: list[dict[str, object]] = []
    max_attempts = 1 + config.RETRY_COUNT

    for chunk_id, chunk_excerpts in excerpts_by_chunk.items():
        chunk = chunk_map.get(chunk_id)
        if chunk is None:
            all_results.extend(chunk_excerpts)
            continue

        # Check if any units need consensus
        any_needs_consensus = any(
            _needs_consensus(exc) for exc in chunk_excerpts
        )
        if not any_needs_consensus:
            all_results.extend(chunk_excerpts)
            continue

        # Try verification call
        verification_result = None
        for attempt in range(max_attempts):
            try:
                start_time = time.monotonic()
                vr = verify_chunk(
                    chunk, chunk_excerpts, verify_client, config, source_metadata
                )
                latency = time.monotonic() - start_time

                if vr is None:
                    # No units needed verification
                    all_results.extend(chunk_excerpts)
                    break

                verification_result = vr
                logger.info(
                    "Phase 3 consensus: chunk_id=%s latency=%.1fs "
                    "attempt=%d items=%d",
                    chunk_id,
                    latency,
                    attempt + 1,
                    len(vr[0].items),
                )
                break

            except Exception as e:
                logger.warning(
                    "Phase 3 consensus attempt %d/%d failed for chunk %s: %s",
                    attempt + 1,
                    max_attempts,
                    chunk_id,
                    str(e),
                )

        if verification_result is None:
            # Verification failed — add flag and keep enrichment values
            for exc in chunk_excerpts:
                flags = list(exc.review_flags)
                if "verification_skipped" not in flags:
                    flags.append("verification_skipped")
                all_results.append(exc.model_copy(update={"review_flags": flags}))
            continue

        # Resolve per-unit consensus
        vr_result, excerpts_with_items = verification_result

        vi_by_index: dict[int, VerificationItem] = {
            vi.item_index: vi for vi in vr_result.items
        }

        excerpt_to_vi: dict[int, list[tuple[VerificationItem, str]]] = {}
        item_index = 0
        for exc, items in excerpts_with_items:
            vis: list[tuple[VerificationItem, str]] = []
            for item in items:
                vi = vi_by_index.get(item_index)
                if vi is not None:
                    vis.append((vi, item["verification_type"]))
                else:
                    logger.warning(
                        "Missing verification item %d for excerpt %s",
                        item_index, exc.excerpt_id,
                    )
                item_index += 1
            excerpt_to_vi[exc.unit_index] = vis

        for exc in chunk_excerpts:
            vis_for_exc = excerpt_to_vi.get(exc.unit_index, [])
            if not vis_for_exc:
                all_results.append(exc)
                continue

            vi_list = [v[0] for v in vis_for_exc]
            type_list = [v[1] for v in vis_for_exc]

            updated, _cr, gate_codes = resolve_consensus(
                exc, vi_list, type_list, escalation_client, config, source_metadata
            )

            # Apply gate flags
            if gate_codes:
                gate_flags = list(updated.gate_flags) + gate_codes
                updated = updated.model_copy(update={"gate_flags": gate_flags})

                # Build gate entries
                for gc in gate_codes:
                    all_gates.append(
                        _build_gate_entry(updated, gc, source_metadata)
                    )

            # Final gate check (catches edge cases not from resolve_consensus)
            additional_gates = check_gate_triggers(
                updated, source_metadata, config
            )
            for gc in additional_gates:
                if gc not in (updated.gate_flags or []):
                    updated = updated.model_copy(
                        update={"gate_flags": list(updated.gate_flags) + [gc]}
                    )
                    all_gates.append(
                        _build_gate_entry(updated, gc, source_metadata)
                    )

            all_results.append(updated)

    return all_results, all_gates
