"""Phase 2b: Teaching Unit Grouping (SPEC §5.3, §5.4.3).

Groups classified segments into TeachingUnit objects using one LLM call
per chunk.  Verifies unit coverage invariants with auto-repair for
V-P2-14 (word range derivation) and V-P2-15 (notes consistency).

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging
import time
from typing import TYPE_CHECKING, Any, Optional

import instructor
from pydantic import ValidationError

from engines.excerpting.src.prompts import (
    CONSTITUTION,
    GROUP_CORE_RULES,
    GROUP_CRITICAL_REMINDERS,
    GROUP_DIALECTICAL_RULES,
    GROUP_FIQH_RULES,
    GROUP_HADITH_RULES,
    GROUP_INTRO_RULES,
    GROUP_OUTPUT_FORMAT,
    GROUP_VERSE_RULES,
)
from engines.excerpting.contracts import (
    AssembledChunk,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExtractionResult,
    ScholarlyFunction,
    SelfContainmentLevel,
    TeachingUnit,
    validate_tu_invariants,
)

if TYPE_CHECKING:
    from engines.excerpting.src.cache import CacheManager
    from engines.excerpting.src.progress import ProgressTracker

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

# All GROUP rule modules loaded; IU-5 will make this dynamic per chunk flags.
# Only {structural_format} (in GROUP_OUTPUT_FORMAT) is substituted at call time.
_GROUP_RULES = "\n\n".join([
    GROUP_CORE_RULES,
    GROUP_HADITH_RULES,
    GROUP_VERSE_RULES,
    GROUP_FIQH_RULES,
    GROUP_DIALECTICAL_RULES,
    GROUP_INTRO_RULES,
    GROUP_OUTPUT_FORMAT,
])

GROUP_SYSTEM_PROMPT = CONSTITUTION + "\n\n" + _GROUP_RULES


# ═══════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════


def compute_active_modules(segments: list[ClassifiedSegment]) -> list[str]:
    """Determine which conditional GROUP rule modules to load (DR28 IU-4).

    Analyzes classified segment functions to select genre-specific rule
    modules. CORE and OUTPUT_FORMAT are always loaded; this function
    returns only the conditional modules relevant to this chunk's content.
    """
    functions = {seg.scholarly_function for seg in segments}
    modules: list[str] = []

    if functions & {ScholarlyFunction.EVIDENCE_HADITH, ScholarlyFunction.NARRATION}:
        modules.append(GROUP_HADITH_RULES)
    if ScholarlyFunction.EVIDENCE_QURAN in functions:
        modules.append(GROUP_VERSE_RULES)
    if functions & {
        ScholarlyFunction.RULE_STATEMENT,
        ScholarlyFunction.CONDITION_EXCEPTION,
        ScholarlyFunction.EVIDENCE_IJMA,
        ScholarlyFunction.EVIDENCE_QIYAS,
    }:
        modules.append(GROUP_FIQH_RULES)
    if ScholarlyFunction.REFUTATION in functions:
        modules.append(GROUP_DIALECTICAL_RULES)
    if ScholarlyFunction.STRUCTURAL_TRANSITION in functions:
        modules.append(GROUP_INTRO_RULES)

    return modules


def _compute_group_max_tokens(word_count: int) -> int:
    """Compute MAX_TOKENS for grouping call based on input size.

    ≤1500 words → 8192.  1501-4000 → 16384.  >4000 → 32768.
    Matches the dynamic scaling pattern of CLASSIFY and ENRICH.

    Grouping output is smaller than classification (fewer objects with
    more fields each), so the base tier starts at 8192 rather than
    CLASSIFY's 8192 or ENRICH's 16384.  The largest validated grouping
    output was 41 units from 3111 words (Taysir div_661), well within
    16384 tokens.
    """
    if word_count > 4000:
        logger.warning(
            "Untested word count range: %d > 4000. Using MAX_TOKENS=32768 "
            "(provisional). Monitor for output truncation.",
            word_count,
        )
        return 32768
    if word_count > 1500:
        return 16384
    return 8192


def _build_group_user_message(
    chunk: AssembledChunk,
    segments: list[ClassifiedSegment],
) -> str:
    """Build DR28 user message: <active_rules> + <input> + <critical_reminders>.

    Progressive disclosure: only loads rule modules relevant to this chunk's
    classified content. CORE and OUTPUT_FORMAT are always included.
    """
    active_modules = compute_active_modules(segments)
    output_format = GROUP_OUTPUT_FORMAT.format(
        structural_format=chunk.structural_format.value,
    )
    rules_parts = [GROUP_CORE_RULES] + active_modules + [output_format]
    active_rules = "\n\n".join(rules_parts)

    segment_summary = _build_segment_summary(segments)

    return (
        f"<active_rules>\n{active_rules}\n</active_rules>\n\n"
        f"<input>\n"
        f"<text>\n{chunk.assembled_text}\n</text>\n\n"
        f"<classified_segments>\n{segment_summary}\n</classified_segments>\n"
        f"</input>\n\n"
        f"<critical_reminders>\n{GROUP_CRITICAL_REMINDERS}\n</critical_reminders>"
    )


def _build_segment_summary(segments: list[ClassifiedSegment]) -> str:
    """Build the <classified_segments> block for the user message (§5.3.3).

    Uses **post-normalization** canonical offsets.
    Format: ``Segment {idx}: words {start}–{end}, function={fn}, snippet="{snippet}"``
    """
    lines: list[str] = []
    for seg in segments:
        lines.append(
            f'Segment {seg.segment_index}: words {seg.start_word}\u2013'
            f'{seg.end_word}, function={seg.scholarly_function.value}, '
            f'snippet="{seg.text_snippet}"'
        )
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════════
# Public Functions
# ═══════════════════════════════════════════════════════════════════


def group_chunk(
    chunk: AssembledChunk,
    segments: list[ClassifiedSegment],
    client: instructor.Instructor,
    config: ExcerptingConfig,
    error_feedback: Optional[str] = None,
    timeout_override: Optional[int] = None,
) -> ExtractionResult:
    """Send chunk + classified segments to LLM for grouping (§5.3).

    DR28 architecture: system=CONSTITUTION (stable, cacheable),
    user=<active_rules>+<input>+<critical_reminders> (dynamic per chunk).

    Args:
        error_feedback: Optional text appended to user message on retry (DD-S2-5).
        timeout_override: If provided, overrides config.GROUP_TIMEOUT (for retry escalation).
    """
    system_prompt = CONSTITUTION

    user_message = _build_group_user_message(chunk, segments)
    if error_feedback:
        user_message += error_feedback

    timeout = timeout_override if timeout_override is not None else config.GROUP_TIMEOUT

    max_tokens = _compute_group_max_tokens(chunk.total_tokens)

    return client.chat.completions.create(
        model=config.GROUP_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=max_tokens,
        max_retries=0,
        timeout=timeout,
        response_model=ExtractionResult,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )


def verify_units(
    units: list[TeachingUnit],
    segments: list[ClassifiedSegment],
    total_tokens: int,
) -> list[TeachingUnit]:
    """Verify teaching unit invariants V-P2-10 through V-P2-19 (§5.4.3).

    **Auto-repairs before validation:**
      - V-P2-14: Derives ``start_word`` / ``end_word`` from constituent segments.
        If LLM values differ, logs warning and overwrites with derived values.
      - V-P2-15: Fixes ``self_containment_notes`` consistency.
        FULL with notes → set notes to None.
        PARTIAL/DEPENDENT without notes → set to ``"No notes provided"``.

    Delegates to ``validate_tu_invariants()`` after repairs.

    Returns:
        The (possibly repaired) list of TeachingUnit objects.

    Raises:
        ValueError: On any fatal invariant violation.
    """
    for unit in units:
        # V-P2-14: Derive word ranges from constituent segments
        if unit.segment_indices:
            try:
                derived_start = segments[unit.segment_indices[0]].start_word
                derived_end = segments[unit.segment_indices[-1]].end_word
            except IndexError:
                raise ValueError(
                    f"V-P2-14: unit {unit.unit_index} references segment index "
                    f"{unit.segment_indices[0]} or {unit.segment_indices[-1]}, "
                    f"but only {len(segments)} segments exist"
                )
            if unit.start_word != derived_start:
                logger.warning(
                    "V-P2-14: unit %d start_word %d != derived %d "
                    "(from segment %d). Using derived.",
                    unit.unit_index,
                    unit.start_word,
                    derived_start,
                    unit.segment_indices[0],
                )
                unit.start_word = derived_start
            if unit.end_word != derived_end:
                logger.warning(
                    "V-P2-14: unit %d end_word %d != derived %d "
                    "(from segment %d). Using derived.",
                    unit.unit_index,
                    unit.end_word,
                    derived_end,
                    unit.segment_indices[-1],
                )
                unit.end_word = derived_end

        # V-P2-15: Notes consistency auto-repair (defense-in-depth).
        # In normal flow the model_validator prevents invalid combos,
        # but this catches edge cases (e.g. model_construct bypass).
        if unit.self_containment == SelfContainmentLevel.FULL:
            if unit.self_containment_notes is not None:
                logger.warning(
                    "V-P2-15: unit %d is FULL but has notes. "
                    "Setting notes to None.",
                    unit.unit_index,
                )
                unit.self_containment_notes = None
        else:
            if not unit.self_containment_notes:
                logger.warning(
                    "V-P2-15: unit %d is %s but missing notes. "
                    'Setting to "No notes provided".',
                    unit.unit_index,
                    unit.self_containment.value,
                )
                unit.self_containment_notes = "No notes provided"

    # V-P2-18: total_units consistency handled by caller (warning only)
    validate_tu_invariants(units, segments, total_tokens)
    return units


def run_phase2b(
    chunks: list[AssembledChunk],
    classified: dict[str, list[ClassifiedSegment]],
    client: instructor.Instructor,
    config: ExcerptingConfig,
    progress: Optional["ProgressTracker"] = None,
    cache: Optional["CacheManager"] = None,
    trace_context: Optional[dict[str, Any]] = None,
) -> dict[str, list[TeachingUnit]]:
    """Execute Phase 2b for all chunks: group → verify (§5.1 steps 4–5).

    Only processes chunks that succeeded Phase 2a (present in *classified* dict).
    Retries per §5.5.2 (max ``1 + config.RETRY_COUNT`` attempts per chunk).
    Classification results are **reused** across retries — only grouping is retried.

    Args:
        progress: Optional WAL-based tracker. When provided, completed chunks
            are skipped on resume and newly completed chunks are recorded.

    Returns:
        ``dict[chunk_id → list[TeachingUnit]]``.
        Failed chunks are **absent** (logged, never silently dropped).
    """
    result: dict[str, list[TeachingUnit]] = {}
    max_attempts = 1 + config.RETRY_COUNT

    for chunk in chunks:
        # L-001: Set chunk_id on trace context so Instructor hooks can
        # attribute this LLM call to the correct chunk.
        if trace_context is not None:
            trace_context["chunk_id"] = chunk.chunk_id

        segments = classified.get(chunk.chunk_id)
        if segments is None:
            continue  # Phase 2a failed for this chunk

        # Resume check: skip chunks already completed in a prior run
        if progress is not None and progress.is_done(chunk.chunk_id, "phase2b"):
            logger.info(
                "Chunk %s phase2b: skipping (already done)", chunk.chunk_id
            )
            continue

        # Cache check (first-attempt prompt only, no error_feedback)
        cache_key = ""
        if cache is not None:
            from engines.excerpting.src.cache import compute_cache_key

            first_user_message = _build_group_user_message(chunk, segments)
            cache_key = compute_cache_key(
                "group",
                CONSTITUTION,
                first_user_message,
                config.GROUP_MODEL,
                config.LLM_TEMPERATURE,
                config.GROUP_MAX_TOKENS,
            )
            cached = cache.load("group", cache_key, ExtractionResult)
            if cached is not None:
                logger.info(
                    "Chunk %s phase2b: cache hit, skipping LLM call",
                    chunk.chunk_id,
                )
                try:
                    repaired = verify_units(
                        cached.teaching_units, segments, chunk.total_tokens
                    )
                    result[chunk.chunk_id] = repaired
                    if progress is not None:
                        progress.mark_done(chunk.chunk_id, "phase2b")
                    continue  # Skip to next chunk
                except (ValueError, ValidationError):
                    logger.warning(
                        "Cached result for %s failed validation, re-processing",
                        chunk.chunk_id,
                    )

        error_feedback: Optional[str] = None
        last_error_code: Optional[str] = None
        success = False
        current_timeout = config.GROUP_TIMEOUT

        for attempt in range(max_attempts):
            phase = "group"
            try:
                # Step 4: Group (LLM call)
                start_time = time.monotonic()
                er = group_chunk(chunk, segments, client, config, error_feedback, timeout_override=current_timeout)
                latency = time.monotonic() - start_time

                logger.info(
                    "Phase 2b group: source_id=%s chunk_id=%s "
                    "latency=%.1fs attempt=%d units=%d",
                    chunk.source_id,
                    chunk.chunk_id,
                    latency,
                    attempt + 1,
                    len(er.teaching_units),
                )

                # V-P2-18: total_units consistency (warning only)
                if er.total_units != len(er.teaching_units):
                    logger.warning(
                        "V-P2-18: total_units %d != len(teaching_units) %d "
                        "for chunk %s. Using actual count.",
                        er.total_units,
                        len(er.teaching_units),
                        chunk.chunk_id,
                    )

                # Step 5: Verify + auto-repair
                phase = "verify"
                repaired = verify_units(
                    er.teaching_units, segments, chunk.total_tokens
                )

                result[chunk.chunk_id] = repaired
                success = True
                # Save to cache (only first attempt with no error_feedback)
                if cache is not None and attempt == 0:
                    cache.save("group", cache_key, chunk.chunk_id, config.GROUP_MODEL, er)
                if progress is not None:
                    progress.mark_done(chunk.chunk_id, "phase2b")
                break

            except ValidationError as e:
                # ValidationError is subclass of ValueError — catch first.
                last_error_code = ExcerptingErrorCodes.EX_C_002
                error_feedback = None  # DD-S2-8: schema errors are structural, not content
                logger.warning(
                    "Chunk %s attempt %d/%d validation error: %s",
                    chunk.chunk_id,
                    attempt + 1,
                    max_attempts,
                    e,
                )

            except ValueError as e:
                error_msg = str(e)
                last_error_code = ExcerptingErrorCodes.EX_C_005
                error_feedback = (
                    f"\n\nPrevious output violated unit coverage invariant: "
                    f"{error_msg}"
                )
                logger.warning(
                    "Chunk %s attempt %d/%d %s failure: %s",
                    chunk.chunk_id,
                    attempt + 1,
                    max_attempts,
                    phase,
                    error_msg,
                )

            except Exception as e:
                last_error_code = ExcerptingErrorCodes.EX_C_002
                error_feedback = None
                wait_seconds = 2**attempt
                logger.warning(
                    "Chunk %s attempt %d/%d API error: %s. "
                    "Backing off %ds.",
                    chunk.chunk_id,
                    attempt + 1,
                    max_attempts,
                    e,
                    wait_seconds,
                )
                time.sleep(wait_seconds)
                current_timeout = min(
                    int(current_timeout * 1.5),
                    config.GROUP_TIMEOUT * 2,
                )

        if not success:
            if progress is not None:
                progress.mark_failed(
                    chunk.chunk_id,
                    "phase2b",
                    last_error_code or "unknown",
                )
            logger.error(
                "Phase 2b FAILED for chunk %s after %d attempts. "
                "Error code: %s. Chunk excluded from Phase 3.",
                chunk.chunk_id,
                max_attempts,
                last_error_code,
            )

    # L-001: Reset chunk_id after all chunks processed.
    if trace_context is not None:
        trace_context["chunk_id"] = None

    return result
