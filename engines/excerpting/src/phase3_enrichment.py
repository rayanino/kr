"""Phase 3: LLM-Driven Metadata Enrichment (SPEC §7.2).

Adds topic classification, school attribution, scholar resolution,
takhrij extraction, terminology variants, cross-references, and
context hints via one LLM enrichment call per chunk.

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict
from typing import TYPE_CHECKING, Optional

import instructor

from engines.excerpting.contracts import (
    AssembledChunk,
    EnrichmentResult,
    ExcerptRecord,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ScholarAttribution,
    SelfContainmentLevel,
    UnitEnrichment,
)

if TYPE_CHECKING:
    from engines.excerpting.contracts import ResolvedScholar

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# §7.2.2 — System Prompt (exact text from SPEC)
# ═══════════════════════════════════════════════════════════════════

ENRICH_SYSTEM_PROMPT = """\
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You are enriching teaching units extracted from this Arabic text with semantic
metadata. Each teaching unit has already been identified, classified, and
partially annotated. Your task is to add inferred metadata that requires
scholarly understanding of the text.

For EACH teaching unit listed in the input, provide these fields:

1. TOPIC KEYWORDS (excerpt_topic): 1 to 3 Arabic keywords or short phrases
   identifying the specific topic taught in this unit. Use standard Arabic
   terminology from the science of this text.
   Examples: "شروط الوضوء", "حكم الربا", "إعراب المبتدأ والخبر"
   Choose keywords that distinguish this unit's topic from other units in the
   same chapter. Avoid overly broad terms (e.g., "فقه" alone is too broad).

2. SCHOOL ATTRIBUTION (school, school_confidence): If this unit presents a
   position from a specific madhhab or school, identify it. Values:
   - A school name: "حنفي", "مالكي", "شافعي", "حنبلي", "ظاهري"
   - "cross_school" if the unit compares multiple schools' positions
   - null if no school attribution is identifiable (grammar, tafsir, etc.)
   Also provide school_confidence (0.0 to 1.0) for your attribution. Set to
   null when school is null.
   CRITICAL DISTINCTION: The author's own school (provided in source metadata)
   is not necessarily the school of the position being presented. An author from
   the Hanbali school may present the Shafi'i position for comparison. Attribute
   the POSITION, not the AUTHOR, unless the author is presenting their own
   school's view.

3. QUOTED SCHOLAR RESOLUTION (resolved_scholars): For each scholar mentioned
   by name or epithet in the unit's text, provide:
   - mention_text: the exact Arabic text used to refer to the scholar
   - resolved_name: the scholar's full conventional name (الاسم المشهور)
     if you can identify them. Use standard scholarly naming (e.g.,
     "أحمد بن حنبل" not just "أحمد").
   - role: one of:
     * "quoted_opinion" — the unit quotes this scholar's view as content
     * "classification_frame" — the unit quotes this scholar's text as the
       frame being commented on (matn author in a sharh excerpt)
     * "refuted_position" — the unit quotes this scholar to refute their view
   - confidence: 0.0 to 1.0

   EPITHET RESOLUTION: Common epithets are context-dependent:
   - "الإمام" → in Hanbali texts usually Ahmad ibn Hanbal; in Shafi'i texts
     usually al-Shafi'i; in Hanafi texts usually Abu Hanifa; in Maliki texts
     usually Malik
   - "الشيخ" → varies by author and era; use source metadata for context
   - "صاحب الكتاب" / "المصنف" → the author of the current work
   Use the source school metadata provided to resolve ambiguous epithets.
   If resolution is uncertain, set confidence < 0.5 and provide your best guess.
   Never silently drop an unresolvable mention — include it with low confidence.

4. TAKHRIJ DATA (takhrij_data): For teaching units containing hadith citations,
   extract from the text AND from the footnotes provided:
   - hadith_text_snippet: first 30 characters of the hadith matn
   - collections: list of hadith collection names mentioned (e.g., "صحيح البخاري",
     "سنن أبي داود")
   - hadith_numbers: list of hadith numbers if mentioned (may be empty)
   - grade: the stated authenticity grade ("صحيح", "حسن", "ضعيف", etc.) or null
   - grade_source: who stated the grade ("المؤلف", "المحقق", "الألباني", etc.)
     or null
   Do NOT invent or infer grades. Record ONLY what the text or footnotes
   explicitly state. If no grade is mentioned, set grade and grade_source to null.
   Omit this field entirely for units with no hadith content.

5. TERMINOLOGY VARIANTS (terminology_variants): Arabic technical terms in this
   unit that are known to have alternative names in other scholarly traditions.
   - term: the term as used in this text
   - variants: list of known alternative Arabic terms for the same concept
   Example: {"term": "القراض", "variants": ["المضاربة"]}
   Example: {"term": "الحدث", "variants": ["النجاسة الحكمية"]}
   Only include genuine terminology equivalences. Empty list is acceptable
   for units with no notable term variants.

6. CROSS-REFERENCES (cross_references): If the unit contains references to
   other parts of the same work ("كما تقدم", "المذكور آنفاً", "ما سيأتي في باب"),
   provide:
   - reference_text: the exact reference phrase in the unit
   - target_description: what the reference points to, if determinable
   - resolved: true if you can identify the target from the division path
     and text context, false otherwise
   When the reference cannot be resolved (IR-3 from §6.4), set resolved to false.
   Unresolved references support self-containment assessment (the unit stays at
   PARTIAL) and downstream linking.

7. CONTEXT HINT (context_hint): For units with self_containment = PARTIAL,
   provide a brief Arabic phrase (10 to 30 Arabic words) that supplies the
   missing context identified in self_containment_notes. This hint will be
   displayed alongside the excerpt to help the reader.
   Provide ONLY for units where self_containment is PARTIAL.
   Set to null for FULL and DEPENDENT units.

Respond with a JSON array containing one enrichment object per teaching unit,
in the same order as the input units."""


# ═══════════════════════════════════════════════════════════════════
# §7.2.3 — User Message Builder
# ═══════════════════════════════════════════════════════════════════


def _build_enrichment_user_message(
    chunk: AssembledChunk,
    excerpts: list[ExcerptRecord],
    source_metadata: dict[str, str],
) -> str:
    """Build the user message for enrichment per §7.2.3 template."""
    parts: list[str] = []

    # Source metadata block
    parts.append("<source_metadata>")
    parts.append(f"Author: {source_metadata.get('author_name', 'unknown')}")
    parts.append(f"Work: {source_metadata.get('work_title', 'unknown')}")
    parts.append(f"Science: {source_metadata.get('science', 'unknown')}")
    parts.append(f"School: {source_metadata.get('source_school', 'unknown')}")
    parts.append("</source_metadata>")
    parts.append("")

    # Full text
    parts.append("<text>")
    parts.append(chunk.assembled_text)
    parts.append("</text>")
    parts.append("")

    # Teaching units with deterministic annotations
    parts.append("<teaching_units>")
    for exc in excerpts:
        parts.append(
            f"Unit {exc.unit_index}: words {exc.start_word}–{exc.end_word}"
        )
        parts.append(f'  snippet: "{exc.text_snippet}"')
        parts.append(f"  function: {exc.primary_function.value}")
        parts.append(f"  self_containment: {exc.self_containment.value}")
        parts.append(
            f"  self_containment_notes: "
            f"{exc.self_containment_notes or 'none'}"
        )

        # Evidence summary (F-DET-5)
        if exc.evidence_refs:
            ev_summary = ", ".join(
                f"{er.type}({er.text_snippet[:30]}...)" for er in exc.evidence_refs
            )
            parts.append(f"  evidence_detected: {ev_summary}")
        else:
            parts.append("  evidence_detected: none")

        # Footnotes (F-DET-8)
        if exc.footnotes_relevant:
            fn_texts = "; ".join(
                f"[{fn.ref_marker}] {fn.text}" for fn in exc.footnotes_relevant
            )
            parts.append(f"  footnotes: {fn_texts}")
        else:
            parts.append("  footnotes: none")

    parts.append("</teaching_units>")

    return "\n".join(parts)


# ═══════════════════════════════════════════════════════════════════
# Function 1: enrich_chunk
# ═══════════════════════════════════════════════════════════════════


def enrich_chunk(
    chunk: AssembledChunk,
    excerpts: list[ExcerptRecord],
    client: instructor.Instructor,
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> EnrichmentResult:
    """Send chunk + its teaching units to LLM for enrichment (§7.2).

    One LLM call per chunk (not per-unit). Inter-unit context improves
    quality — references like "as mentioned above" can be resolved.

    Uses system prompt from §7.2.2 and user message from §7.2.3.
    Returns EnrichmentResult with per-unit enrichments.
    """
    if source_metadata is None:
        source_metadata = {}

    user_message = _build_enrichment_user_message(
        chunk, excerpts, source_metadata
    )

    return client.chat.completions.create(
        model=config.ENRICH_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.ENRICH_MAX_TOKENS,
        max_retries=0,
        response_model=EnrichmentResult,
        messages=[
            {"role": "system", "content": ENRICH_SYSTEM_PROMPT},
            {"role": "user", "content": user_message},
        ],
    )


# ═══════════════════════════════════════════════════════════════════
# Function 2: apply_enrichment
# ═══════════════════════════════════════════════════════════════════


def apply_enrichment(
    excerpts: list[ExcerptRecord],
    enrichment: EnrichmentResult,
) -> list[ExcerptRecord]:
    """Merge LLM enrichment results into ExcerptRecords (§7.2).

    Match each UnitEnrichment to its ExcerptRecord by unit_index.
    Updates: excerpt_topic, school, school_confidence, takhrij_data,
    terminology_variants, cross_references, context_hint.
    Merges resolved_scholars into quoted_scholars (DD-S4-4).
    """
    # Build lookup by unit_index
    enrichment_map: dict[int, UnitEnrichment] = {
        ue.unit_index: ue for ue in enrichment.enrichments
    }

    result: list[ExcerptRecord] = []
    for exc in excerpts:
        ue = enrichment_map.get(exc.unit_index)
        if ue is None:
            logger.warning(
                "No enrichment found for unit_index=%d in chunk %s. "
                "Keeping deterministic-only fields.",
                exc.unit_index,
                exc.div_id,
            )
            result.append(exc)
            continue

        # Merge LLM resolved_scholars with structural quoted_scholars (DD-S4-4)
        merged_scholars = _merge_scholars(exc.quoted_scholars, ue.resolved_scholars)

        # Determine context_hint: only for PARTIAL (I-ER-4)
        context_hint: Optional[str] = None
        if exc.self_containment == SelfContainmentLevel.PARTIAL:
            context_hint = ue.context_hint

        # Remove llm_enrichment_failed flag since enrichment succeeded
        review_flags = [
            f for f in exc.review_flags if f != "llm_enrichment_failed"
        ]

        # Build updated record via model_copy
        updated = exc.model_copy(
            update={
                "excerpt_topic": ue.excerpt_topic,
                "school": ue.school,
                "school_confidence": ue.school_confidence,
                "quoted_scholars": merged_scholars,
                "takhrij_data": ue.takhrij_data if ue.takhrij_data else None,
                "terminology_variants": ue.terminology_variants,
                "cross_references": ue.cross_references,
                "context_hint": context_hint,
                "review_flags": review_flags,
            }
        )
        result.append(updated)

    return result


def _merge_scholars(
    structural: list[ScholarAttribution],
    llm_resolved: list["ResolvedScholar"],
) -> list[ScholarAttribution]:
    """Merge structural (F-DET-9) and LLM-resolved scholars (DD-S4-4).

    LLM scholars augment (not replace) structural ones.
    If both identify the same layer's author, prefer the LLM's resolved_name
    but keep the structural entry's confidence=1.0 and source="layer_overlap".
    """
    # Start with structural scholars
    result = list(structural)
    structural_ids = {
        s.resolved_name for s in structural if s.resolved_name
    }

    for rs in llm_resolved:
        # Check if this LLM scholar matches a structural one
        if rs.resolved_name and rs.resolved_name in structural_ids:
            # Update structural entry's resolved_name if LLM has a richer one
            for i, s in enumerate(result):
                if s.resolved_name == rs.resolved_name and s.source == "layer_overlap":
                    result[i] = s.model_copy(
                        update={"mention_text": rs.mention_text}
                    )
                    break
        else:
            # New scholar from LLM — add with llm_enrichment source
            result.append(
                ScholarAttribution(
                    mention_text=rs.mention_text,
                    resolved_name=rs.resolved_name,
                    role=rs.role,
                    confidence=rs.confidence,
                    source="llm_enrichment",
                )
            )

    return result


# ═══════════════════════════════════════════════════════════════════
# Function 3: run_phase3_enrichment
# ═══════════════════════════════════════════════════════════════════


def run_phase3_enrichment(
    excerpts: list[ExcerptRecord],
    chunks: list[AssembledChunk],
    client: instructor.Instructor,
    config: ExcerptingConfig,
    source_metadata: Optional[dict[str, str]] = None,
) -> list[ExcerptRecord]:
    """Execute LLM enrichment for all chunks (§7.2).

    Groups excerpts by chunk_id (div_id), calls enrich_chunk once per group.
    On LLM failure: deterministic fields survive. LLM fields stay None.
    Emits EX-M-002 on failure. Retries per §5.5.2.
    """
    if source_metadata is None:
        source_metadata = {}

    # Group excerpts by div_id (chunk identifier)
    chunk_map: dict[str, AssembledChunk] = {c.chunk_id: c for c in chunks}
    excerpts_by_chunk: dict[str, list[ExcerptRecord]] = defaultdict(list)
    for exc in excerpts:
        # Try to find the matching chunk
        chunk_id = exc.div_id
        for cid in chunk_map:
            if cid.startswith(exc.div_id):
                chunk_id = cid
                break
        excerpts_by_chunk[chunk_id].append(exc)

    all_results: list[ExcerptRecord] = []
    max_attempts = 1 + config.RETRY_COUNT

    for chunk_id, chunk_excerpts in excerpts_by_chunk.items():
        chunk = chunk_map.get(chunk_id)
        if chunk is None:
            logger.error(
                "No chunk found for chunk_id=%s. Keeping deterministic-only.",
                chunk_id,
            )
            all_results.extend(chunk_excerpts)
            continue

        success = False
        for attempt in range(max_attempts):
            try:
                start_time = time.monotonic()
                enrichment = enrich_chunk(
                    chunk, chunk_excerpts, client, config, source_metadata
                )
                latency = time.monotonic() - start_time

                logger.info(
                    "Phase 3 enrichment: chunk_id=%s latency=%.1fs "
                    "attempt=%d units=%d",
                    chunk_id,
                    latency,
                    attempt + 1,
                    len(enrichment.enrichments),
                )

                enriched = apply_enrichment(chunk_excerpts, enrichment)
                all_results.extend(enriched)
                success = True
                break

            except Exception as e:
                logger.warning(
                    "Phase 3 enrichment attempt %d/%d failed for chunk %s: %s",
                    attempt + 1,
                    max_attempts,
                    chunk_id,
                    str(e),
                )

        if not success:
            logger.error(
                "%s: LLM enrichment failed after %d attempts for chunk %s. "
                "Keeping deterministic-only fields.",
                ExcerptingErrorCodes.EX_M_002,
                max_attempts,
                chunk_id,
            )
            # Mark all excerpts in this chunk with enrichment failure
            for exc in chunk_excerpts:
                flags = list(exc.review_flags)
                if "llm_enrichment_failed" not in flags:
                    flags.append("llm_enrichment_failed")
                all_results.append(exc.model_copy(update={"review_flags": flags}))

    return all_results
