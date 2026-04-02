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
from typing import TYPE_CHECKING, Optional

import instructor  # pyright: ignore[reportMissingImports]

from engines.excerpting.contracts import (
    AssembledChunk,
    BatchEscalationResult,
    ConsensusDecision,
    ConsensusRecord,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    SelfContainmentLevel,
    VerificationItem,
    VerificationResult,
)

if TYPE_CHECKING:
    from engines.excerpting.src.cache import CacheManager
    from engines.excerpting.src.progress import ProgressTracker

logger = logging.getLogger(__name__)

_SC_LEVEL_ORDER: dict[SelfContainmentLevel, int] = {
    SelfContainmentLevel.FULL: 2,
    SelfContainmentLevel.PARTIAL: 1,
    SelfContainmentLevel.DEPENDENT: 0,
}


# ═══════════════════════════════════════════════════════════════════
# §7.3.2 — Verification Prompt
# ═══════════════════════════════════════════════════════════════════

VERIFY_SYSTEM_PROMPT = """\
You are an expert in classical Islamic scholarly text analysis \
(تحليل النصوص العلمية الإسلامية), independently verifying metadata \
decisions made by another model.

For each verification item, you receive the original Arabic text, the \
decision made, and supporting context. Your task is to independently \
assess whether each decision is correct.

VERIFICATION METHODOLOGY:
- Read the Arabic text carefully before looking at the decision
- Form your own judgment, then compare with the stated decision
- For SCHOOL_ATTRIBUTION: check whether the position presented matches \
the attributed school. The source author's school is NOT necessarily the \
school of every position discussed — authors often present other schools' \
views for comparison or refutation.
- For AUTHOR_ATTRIBUTION: check whether the text content matches the \
attributed author/layer. Look for voice markers (قال, ذكر, المصنف), \
commentary indicators (أي, يعني, الشرح), and layer boundaries.
- For SELF_CONTAINMENT: evaluate against these criteria:
  * C-SC-1: Every technical term is defined or is standard terminology
  * C-SC-2: Every pronoun/demonstrative resolves within the unit
  * C-SC-3: Every evidence citation includes its text or is universally known
  * C-SC-4: The argument/ruling/teaching is complete, not a fragment
  * C-SC-5: If responding to another scholar, enough of that position is \
included

For each item, respond with:
- item_index: the index of the verification item
- agrees: true or false
- alternative_value: if you disagree, provide ONLY the corrected value \
as a bare string. For author attribution: the author name (e.g., \
"ابن عقيل"). For school attribution: the school name or "cross_school". \
For self-containment: "FULL", "PARTIAL", or "DEPENDENT". \
Do NOT include explanatory text — put all explanation in reasoning.
- confidence: your confidence from 0.0 to 1.0
- reasoning: brief reasoning for your assessment

WORKED EXAMPLES:

Example 1 — Author attribution (disagree, bare value):
  Source: شرح ابن عقيل على ألفية ابن مالك (science: نحو)
  Decision: author_attribution = "unknown"
  Text: "ولا تجر رب إلا نكرة نحو رب رجل عالم لقيت وهذا معنى قوله \
وبرب منكرا أي واخصص برب النكرة"
  Correct response:
    agrees: false
    alternative_value: "ابن عقيل"
    confidence: 0.92
    reasoning: "Text contains sharh markers: 'وهذا معنى قوله' (referring \
to ابن مالك's matn verse), 'أي واخصص برب النكرة' (explanatory gloss). \
This is ابن عقيل's commentary layer."
  NOTE: alternative_value is "ابن عقيل" — NOT "This should be \
attributed to ابن عقيل (layer sharh). The text contains..."

Example 2 — School attribution (disagree, bare value):
  Source: تيسير العلام شرح عمدة الأحكام (science: فقه, author school: حنبلي)
  Decision: school_attribution = "حنبلي"
  Text: "ما يؤخذ من الحديث:\\n1- النهي عن البول في الماء الذي لا يجرى \
وتحريمه"
  Correct response:
    agrees: false
    alternative_value: "cross_school"
    confidence: 0.75
    reasoning: "The passage presents general fiqh rulings derived from \
the hadith without attributing them to a specific school. The numbered \
items are universally applicable."
  NOTE: alternative_value is "cross_school" — NOT "cross_school أو عام \
(لا ينسب لمذهب بعينه)"."""


def _needs_consensus(excerpt: ExcerptRecord) -> list[dict[str, str]]:
    """Determine which decisions on this excerpt require consensus (§7.3.1).

    Returns list of verification items to include in the prompt.
    Each item has: verification_type, decision_text, unit_text.
    """
    items: list[dict[str, str]] = []

    # School attribution: school is non-null
    if excerpt.school is not None:
        item: dict[str, str] = {
            "verification_type": "SCHOOL_ATTRIBUTION",
            "decision_text": (
                f'School attributed as "{excerpt.school}". '
                f"Is this correct given the text content?"
            ),
            "unit_text": excerpt.primary_text[:1500],
        }
        if excerpt.primary_function is not None:
            item["scholarly_function"] = excerpt.primary_function.value
        if excerpt.school_confidence is not None:
            item["school_confidence"] = str(excerpt.school_confidence)
        items.append(item)

    # Author attribution: LA-3 (ambiguous)
    if excerpt.primary_author_layer.rule_applied == "LA-3":
        item = {
            "verification_type": "AUTHOR_ATTRIBUTION",
            "decision_text": (
                f"Unit attributed to {excerpt.primary_author_layer.author_id} "
                f"(layer {excerpt.primary_author_layer.layer_id}, "
                f"{excerpt.primary_author_layer.coverage_pct * 100:.0f}% coverage, "
                f"rule LA-3). Is this attribution correct, or should it be "
                f"attributed differently?"
            ),
            "unit_text": excerpt.primary_text[:1500],
        }
        if excerpt.primary_function is not None:
            item["scholarly_function"] = excerpt.primary_function.value
        items.append(item)

    # Self-containment: PARTIAL or DEPENDENT
    if excerpt.self_containment in (
        SelfContainmentLevel.PARTIAL,
        SelfContainmentLevel.DEPENDENT,
    ):
        item = {
            "verification_type": "SELF_CONTAINMENT",
            "decision_text": (
                f"Unit assessed as {excerpt.self_containment.value}. "
                f"Notes: {excerpt.self_containment_notes or 'none'}. "
                f"Is this assessment correct?"
            ),
            "unit_text": excerpt.primary_text[:1500],
        }
        if excerpt.primary_function is not None:
            item["scholarly_function"] = excerpt.primary_function.value
        items.append(item)

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
            if item.get("scholarly_function"):
                parts.append(f"Scholarly function: {item['scholarly_function']}")
            if item.get("school_confidence") is not None:
                parts.append(f"School confidence: {item['school_confidence']}")
            parts.append(f"Decision: {item['decision_text']}")
            parts.append(
                "Your assessment: agree or disagree, with brief reasoning "
                "in Arabic or English."
            )
            parts.append(
                "If you disagree, put ONLY the corrected value in "
                "alternative_value (bare string, no explanation)."
            )
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
    timeout_override: Optional[int] = None,
) -> Optional[tuple[VerificationResult, list[tuple[ExcerptRecord, list[dict[str, str]]]]]]:
    """Call verification model for attribution + school checks (§7.3.2).

    Uses VERIFY_MODEL (different provider family from ENRICH_MODEL).
    Returns None if no units in this chunk need verification.
    Otherwise returns (VerificationResult, items_map) for resolve_consensus.

    Args:
        timeout_override: If provided, overrides config.VERIFY_TIMEOUT (for retry escalation).
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

    timeout = timeout_override if timeout_override is not None else config.VERIFY_TIMEOUT

    result = client.chat.completions.create(
        model=config.VERIFY_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.VERIFY_MAX_TOKENS,
        max_retries=0,
        timeout=timeout,
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
    batch_escalation_result: Optional[dict[int, str]] = None,
) -> tuple[ExcerptRecord, Optional[ConsensusRecord], list[str]]:
    """Resolve disagreements between enrichment and verification (§7.3.3).

    Args:
        batch_escalation_result: If provided, maps item_index to author_id
            from a prior batch escalation call. Passed through to
            _resolve_attribution so it skips per-item _call_escalation.

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
                excerpt, vi, escalation_client, config, source_metadata,
                batch_escalation_result=batch_escalation_result,
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
            vi.alternative_value,
        )

        decision = ConsensusDecision(
            decision_type="school_attribution",
            enrichment_value=excerpt.school or "",
            verifier_value=vi.alternative_value,
            verifier_agrees=False,
            final_value=excerpt.school or "",
            resolution_method="enrichment_kept_flagged",
        )

        # Check EX-G-003: school conflicts with source metadata AND both models disagree
        source_school = source_metadata.get("source_school")
        if (
            source_school
            and source_school != excerpt.school
            and vi.alternative_value
            and vi.alternative_value != source_school
        ):
            gates.append(ExcerptingErrorCodes.EX_G_003)

    return decision, updates, flags, gates


def _resolve_attribution(
    excerpt: ExcerptRecord,
    vi: VerificationItem,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
    source_metadata: dict[str, str],
    batch_escalation_result: Optional[dict[int, str]] = None,
) -> tuple[ConsensusDecision, dict[str, object], list[str], list[str]]:
    """§7.3.3 Author attribution disagreement (LA-3 cases).

    Args:
        batch_escalation_result: If provided, maps item_index to author_id
            from a prior batch escalation call. Used instead of per-item
            _call_escalation when available.
    """
    updates: dict[str, object] = {}
    flags: list[str] = []
    gates: list[str] = []

    if vi.agrees:
        updates["attribution_confidence"] = 0.67
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

        # Prefer batch result if available; fall back to per-item call
        if batch_escalation_result is not None and vi.item_index in batch_escalation_result:
            escalation_value = batch_escalation_result[vi.item_index]
        elif escalation_client is not None:
            escalation_value = _call_escalation(
                excerpt, vi, escalation_client, config, source_metadata
            )

        enrichment_val = excerpt.primary_author_layer.author_id
        # H-1: use alternative_value directly (structured by schema)
        verifier_val = vi.alternative_value

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
                    resolution_method="no_majority_gate",
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
        f"Model 2 says: {vi.alternative_value or 'unknown'} "
        f"(reasoning: {vi.reasoning})\n\n"
        f"Which attribution is correct? Respond with just the author ID."
    )

    try:
        # Simple text response for escalation — we just need a string
        from pydantic import BaseModel, Field  # pyright: ignore[reportMissingImports]

        class EscalationResponse(BaseModel):
            author_id: str = Field(description="The correct author attribution")
            reasoning: str = Field(description="Brief explanation")

        result = escalation_client.chat.completions.create(
            model=config.ESCALATION_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=1024,
            max_retries=0,
            timeout=config.ESCALATION_TIMEOUT,
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


def _call_batch_escalation(
    disagreements: list[dict[str, object]],
    escalation_client: instructor.Instructor,
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> Optional[BatchEscalationResult]:
    """Batch-escalate multiple author attribution disagreements in one call.

    Args:
        disagreements: List of dicts, each with:
            - item_index: int
            - excerpt_id: str
            - primary_text: str (first 500 chars)
            - enrichment_author: str
            - verifier_author: str
            - verifier_reasoning: str
        escalation_client: The third-model client.
        config: Config with ESCALATION_MODEL and ESCALATION_TIMEOUT.
        source_metadata: Source metadata for context.

    Returns:
        BatchEscalationResult or None on failure.
    """
    if not disagreements:
        return None

    # Build context header
    meta = source_metadata or {}
    author = meta.get("author_name", "Unknown")
    title = meta.get("work_title", "Unknown")

    # Build per-item sections
    items_text: list[str] = []
    for d in disagreements:
        items_text.append(
            f"ITEM {d['item_index']}:\n"
            f"  Text: \"{str(d['primary_text'])[:500]}\"\n"
            f"  Model 1 (enrichment) says: {d['enrichment_author']}\n"
            f"  Model 2 (verification) says: {d['verifier_author']} "
            f"(reasoning: {d['verifier_reasoning']})\n"
        )

    prompt = (
        f"Two models disagree on author attributions for multiple excerpts "
        f"from the same source.\n\n"
        f"Source: {author} - {title}\n\n"
        f"For each item below, determine which attribution is correct.\n\n"
        + "\n".join(items_text) + "\n"
        f"Respond with your determination for each item."
    )

    try:
        result = escalation_client.chat.completions.create(
            model=config.ESCALATION_MODEL,
            temperature=config.LLM_TEMPERATURE,
            max_tokens=2048,
            max_retries=0,
            timeout=config.ESCALATION_TIMEOUT,
            response_model=BatchEscalationResult,
            messages=[{"role": "user", "content": prompt}],
        )
        return result
    except Exception as e:
        logger.warning("Batch escalation failed: %s", e)
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
        verifier_level = _parse_self_containment(vi.alternative_value)
        if verifier_level is None:
            verifier_level = enrichment_level

        # Use the more conservative (lower) level
        if _SC_LEVEL_ORDER.get(verifier_level, 1) < _SC_LEVEL_ORDER.get(enrichment_level, 1):
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
    text_upper = text.strip(" \t\n\r").upper()  # safe: English enum values only (FULL/PARTIAL/DEPENDENT)
    for level in SelfContainmentLevel:
        if text_upper == level.value:
            return level
    matches = [level for level in SelfContainmentLevel if level.value in text_upper]
    if matches:
        return min(matches, key=lambda l: _SC_LEVEL_ORDER.get(l, 1))
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
                if d.decision_type == "school_attribution":
                    if d.verifier_value:
                        verifier_also_conflicts = (d.verifier_value != source_school)
                    else:
                        verifier_also_conflicts = False
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
    verify_client: instructor.Instructor,
    escalation_client: Optional[instructor.Instructor],
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
    progress: Optional["ProgressTracker"] = None,
    cache: Optional["CacheManager"] = None,
    error_sink: Optional[list[str]] = None,
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
            # DD-PE-4: Defensive chunk ID fallback for split chunks.
            # Phase 1 may produce chunk_id as "div_id_chunk_N" for splits.
            split_id = f"{exc.div_id}_chunk_{exc.chunk_index}"
            if split_id in chunk_map:
                chunk_id = split_id
                logger.info(
                    "DD-PE-4: Using split_id fallback %s for %s.",
                    split_id, exc.excerpt_id,
                )
            else:
                alt_id = f"{exc.div_id}_{exc.chunk_index}"
                if alt_id in chunk_map:
                    chunk_id = alt_id
                    logger.warning(
                        "DD-PE-4: Using alt_id fallback %s for %s.",
                        alt_id, exc.excerpt_id,
                    )
        excerpts_by_chunk[chunk_id].append(exc)

    all_results: list[ExcerptRecord] = []
    all_gates: list[dict[str, object]] = []
    max_attempts = 1 + config.RETRY_COUNT

    for chunk_id, chunk_excerpts in excerpts_by_chunk.items():
        chunk = chunk_map.get(chunk_id)
        if chunk is None:
            degraded: list[ExcerptRecord] = []
            needs_consensus = False
            for exc in chunk_excerpts:
                if _needs_consensus(exc):
                    needs_consensus = True
                    flags = list(exc.review_flags)
                    if "verification_skipped" not in flags:
                        flags.append("verification_skipped")
                    degraded.append(exc.model_copy(update={"review_flags": flags}))
                else:
                    degraded.append(exc)
            if needs_consensus:
                if progress is not None:
                    progress.mark_failed(
                        chunk_id,
                        "phase3_consensus",
                        ExcerptingErrorCodes.EX_M_011,
                    )
                if error_sink is not None and ExcerptingErrorCodes.EX_M_011 not in error_sink:
                    error_sink.append(ExcerptingErrorCodes.EX_M_011)
                logger.error(
                    "%s: No chunk found for chunk_id=%s. "
                    "Passing through with verification_skipped for affected excerpts.",
                    ExcerptingErrorCodes.EX_M_011,
                    chunk_id,
                )
            all_results.extend(degraded)
            continue

        # Resume: if chunk is done, fall through to cache-based reconstruction.
        # Do NOT skip here — skipping loses the chunk from all_results/all_gates.
        is_consensus_resume = (
            progress is not None
            and progress.is_done(chunk_id, "phase3_consensus")
        )

        # Check if any units need consensus
        any_needs_consensus = any(
            _needs_consensus(exc) for exc in chunk_excerpts
        )
        if not any_needs_consensus:
            all_results.extend(chunk_excerpts)
            if progress is not None:
                progress.mark_done(chunk_id, "phase3_consensus")
            continue

        # Cache check for verification (first-attempt prompt only)
        cache_key = ""
        if cache is not None:
            from engines.excerpting.src.cache import compute_cache_key

            # Build the same items that verify_chunk would build
            excerpts_with_items_for_cache: list[tuple[ExcerptRecord, list[dict[str, str]]]] = []
            for exc in chunk_excerpts:
                items = _needs_consensus(exc)
                if items:
                    excerpts_with_items_for_cache.append((exc, items))

            if excerpts_with_items_for_cache:
                verify_user_message = _build_verification_user_message(
                    excerpts_with_items_for_cache, source_metadata,
                )
                cache_key = compute_cache_key(
                    "verify",
                    VERIFY_SYSTEM_PROMPT,
                    verify_user_message,
                    config.VERIFY_MODEL,
                    config.LLM_TEMPERATURE,
                    config.VERIFY_MAX_TOKENS,
                )

        # Cache-based skip (for resume or first-run cache reuse)
        cached_vr: VerificationResult | None = None
        if cache is not None and cache_key:
            cached_vr = cache.load("verify", cache_key, VerificationResult)

        if cached_vr is not None:
            logger.info(
                "Chunk %s phase3_consensus: cache hit%s",
                chunk_id,
                " (resume)" if is_consensus_resume else "",
            )
            verification_result = (cached_vr, excerpts_with_items_for_cache)
            loop_handled = True
        elif is_consensus_resume:
            # Done but cache miss — degrade visibly using the canonical failure code.
            if progress is not None:
                progress.mark_failed(
                    chunk_id,
                    "phase3_consensus",
                    ExcerptingErrorCodes.EX_M_011,
                )
            if error_sink is not None and ExcerptingErrorCodes.EX_M_011 not in error_sink:
                error_sink.append(ExcerptingErrorCodes.EX_M_011)
            logger.error(
                "%s: Chunk %s phase3_consensus was marked done but cache is missing. "
                "Passing through with verification_skipped.",
                ExcerptingErrorCodes.EX_M_011,
                chunk_id,
            )
            for exc in chunk_excerpts:
                flags = list(exc.review_flags)
                if "verification_skipped" not in flags:
                    flags.append("verification_skipped")
                all_results.append(
                    exc.model_copy(update={"review_flags": flags})
                )
            continue

        # Try verification call (skipped if cache hit above)
        verification_result = verification_result if cached_vr is not None else None
        loop_handled = cached_vr is not None
        current_timeout = config.VERIFY_TIMEOUT
        for attempt in range(max_attempts):
            if loop_handled:
                break
            try:
                start_time = time.monotonic()
                vr = verify_chunk(
                    chunk, chunk_excerpts, verify_client, config, source_metadata,
                    timeout_override=current_timeout,
                )
                latency = time.monotonic() - start_time

                if vr is None:
                    all_results.extend(chunk_excerpts)
                    loop_handled = True
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
                # Save to cache (all attempts — needed for resume reconstruction)
                if cache is not None and cache_key:
                    cache.save("verify", cache_key, chunk_id, config.VERIFY_MODEL, vr[0])
                loop_handled = True
                break

            except Exception as e:
                logger.warning(
                    "Phase 3 consensus attempt %d/%d failed for chunk %s: %s",
                    attempt + 1,
                    max_attempts,
                    chunk_id,
                    str(e),
                )
                current_timeout = min(
                    int(current_timeout * 1.5),
                    config.VERIFY_TIMEOUT * 2,
                )

        if not loop_handled:
            # All retry attempts failed — keep enrichment-only with flag
            if progress is not None:
                progress.mark_failed(
                    chunk_id,
                    "phase3_consensus",
                    ExcerptingErrorCodes.EX_M_011,
                )
            if error_sink is not None and ExcerptingErrorCodes.EX_M_011 not in error_sink:
                error_sink.append(ExcerptingErrorCodes.EX_M_011)
            for exc in chunk_excerpts:
                flags = list(exc.review_flags)
                if "verification_skipped" not in flags:
                    flags.append("verification_skipped")
                all_results.append(exc.model_copy(update={"review_flags": flags}))
            continue

        if verification_result is None:
            # verify_chunk returned None — already added in loop
            continue

        # Resolve per-unit consensus
        vr_result, excerpts_with_items = verification_result

        vi_by_index: dict[int, VerificationItem] = {
            vi.item_index: vi for vi in vr_result.items
        }

        excerpt_to_vi: dict[int, list[tuple[VerificationItem, str]]] = {}
        excerpt_expected_counts: dict[int, int] = {}
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
            excerpt_expected_counts[exc.unit_index] = len(items)

        units_needing_verification = {exc.unit_index for exc, _ in excerpts_with_items}

        chunk_had_verification_failure = False
        for exc in chunk_excerpts:
            vis_for_exc = excerpt_to_vi.get(exc.unit_index, [])
            expected_count = excerpt_expected_counts.get(exc.unit_index, 0)
            if not vis_for_exc or (expected_count and len(vis_for_exc) != expected_count):
                if exc.unit_index in units_needing_verification:
                    # Needed consensus but got no verification items — degrade visibly.
                    chunk_had_verification_failure = True
                    flags = list(exc.review_flags)
                    if "verification_skipped" not in flags:
                        flags.append("verification_skipped")
                    if progress is not None:
                        progress.mark_failed(
                            chunk_id,
                            "phase3_consensus",
                            ExcerptingErrorCodes.EX_M_011,
                        )
                    if error_sink is not None and ExcerptingErrorCodes.EX_M_011 not in error_sink:
                        error_sink.append(ExcerptingErrorCodes.EX_M_011)
                    all_results.append(exc.model_copy(update={"review_flags": flags}))
                else:
                    # Didn't need consensus — pass through normally
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

        # All excerpts in this chunk resolved successfully
        if progress is not None and not chunk_had_verification_failure:
            progress.mark_done(chunk_id, "phase3_consensus")

    return all_results, all_gates
