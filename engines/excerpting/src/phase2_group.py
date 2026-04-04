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

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    ExtractionResult,
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

# System prompt copied VERBATIM from SPEC §5.3.2.
# Only {structural_format} is substituted at call time (DD-S2-1).
GROUP_SYSTEM_PROMPT = """\
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

You previously classified segments of this Arabic text by scholarly function.
Now group these classified segments into TEACHING UNITS — self-contained
scholarly segments that each teach one distinct concept, ruling, or argument.
A teaching unit is the smallest segment a student could study and learn
something complete from.

GROUPING RULES:
- GENERAL PRINCIPLE (EE-1): An explained object and its immediately \
following explanation form one teaching unit by default. The explained \
text is context for the explanation — separating them orphans the \
explanation. This applies to: hadith + sharh, verse (matn) + commentary, \
definition + examples, principle + reasoning, ruling + evidence. Split \
only when a different scholarly function boundary begins.
- A position (opinion_statement) + its evidence + any counter-evidence
  + conclusion = one unit
- A definition + its examples = one unit
- A hadith + its chain + commentary = one unit (for hadith citations \
within broader discussions — NOT for derived benefits sections)
- A question and its answer belong in the same unit
- A rule_statement + its condition_exception(s) = one unit
- Never group unrelated content (e.g., two different مسائل) into one unit
- structural_transition segments may be grouped with the content they introduce,
  or stand alone if they serve as section markers
- ANTI-SURFACE CLASSIFICATION: Do not classify by surface language alone. \
A passage starting with "الأصل" or "اعلم" or even labeled "مقدمة" may carry \
core rulings (أحكام), definitions (حدود), or evidence — not introductory filler. \
Analyze what scholarly FUNCTION the passage performs, not how it reads at first glance.
- FORGIVING RETENTION: When a small linked sentence (≤15% of the unit) would \
need removal to avoid function mixing, but removing it would start the next \
unit at an unsafe causal continuation (لأن, فإن, ولأنه, فإنه), RETAIN the \
carryover. The harm of orphaned causal particles exceeds the harm of minor \
function mixing.
- TITLE RETENTION: Retain the chapter/section title in the teaching unit when: \
(a) a demonstrative (هذا الباب, في هذا الفصل) points to it, OR \
(b) the title carries jurisprudential content the text does not repeat (common \
in hadith collections with fiqhi tarajim like Sahih al-Bukhari, where the \
title IS the author's ruling and the text is raw evidence). Title retention \
is per-unit, not global — some units need it, others do not.
- MULTI-FUNCTION SPLIT: A passage substantively containing introduction + \
ruling + proof-overview + refutation must NOT remain as one unit. Split at \
function boundaries. A chapter-intro sentence that merely touches on the \
ruling (1% of text) may stay via FORGIVING RETENTION; but when each function \
is substantive (>20% of text), they are separate teaching units.
- INTRODUCTION SCOPE: Distinguish chapter-specific introductions ("هذا الباب \
يذكر فيه...") from full-topic introductions that define the science or \
subject. A chapter-specific intro applies only to this source's chapter; \
treating it as a universal topic introduction creates scope mismatch.
- PROOF STRUCTURE: Scholars present proofs in 3 phases: (1) cite the proof, \
(2) explain it, (3) defend/refute objections. Phases 1+2 belong together per \
EE-1 (proof + explanation = one unit). Phase 3 (refutations/ردود) MAY be a \
separate unit when it answers a different question than phases 1+2.
- MENTION IS NOT EXCERPT: A topic being briefly mentioned in passing does NOT \
make it an excerpt. Only create a teaching unit when the text substantively \
discusses the topic (explains, rules on, or proves something about it). Brief \
mentions in unrelated passages must not generate forced or empty excerpt units.
- DEPENDENCY-FIRST SPLITS: Before splitting segments, ask what QUESTION each \
segment answers. If two segments answer the same question (e.g., objection + \
refutation both answer "what is the debate?"), they cannot be split regardless \
of surface segmentation signals.

DERIVED BENEFITS RULE:
- Sections opening with "ما يؤخذ من الحديث:" or "فوائد:" are derived \
benefits from the preceding hadith.
- Default: split per numbered item. Each item is a separate teaching unit.
- Exception: consecutive items that are fragments of one immediate ruling \
cluster AND are individually under 20 words may be grouped into one excerpt.
- If uncertain whether items are same-topic or different-topic, SPLIT.
  (This split-on-uncertainty rule is specific to derived benefits and \
numbered items. For general grouping, prefer keeping related content \
together per EE-1 rather than splitting aggressively — overgranulation \
is more harmful than undergranulation, FP-9.)
- The hadith text + gharib + المعنى الإجمالي form the inseparable core \
of a hadith commentary unit. Fawa'id/ما يؤخذ points may be separate.

NUMBERED ITEM BOUNDARIES:
- Numbered items (1-, 2-, 3-... or فائدة/مسألة + number) are unit \
boundary signals. Default: each numbered item is a separate unit.
- Two numbered items covering different topics MUST NOT be merged \
(e.g., items about void bequests and burial are separate units).
- Exception: consecutive sub-20-word items in the same ruling cluster \
may be grouped. If uncertain, split.

CONFLICT RESOLUTION (when grouping rules conflict):
If keeping a unit together (EE-1 unity) conflicts with granularity goals, \
apply this precedence:
1. Speaker-role correctness — who endorses what — highest priority
2. Dialogue completeness — objection + response must stay together
3. Textual/grammatical integrity — no mid-sentence Arabic fragments
4. Self-containment — the unit teaches a complete thought
5. Granularity — lowest priority; optimize post-grouping, not here

DECONTEXTUALIZATION PREVENTION (critical):
- A reported position ("قال أبو حنيفة...") and its refutation
  ("ورد عليه بأن...") MUST be in the same unit
- A counter-argument MUST include enough of the original argument to be
  understood on its own
- Evidence cited for a ruling MUST stay with the ruling
- A condition and its exception (rule + إلا clause) belong together
- A verdict/tarjīḥ phrase (والصواب، الراجح، الأصح، المعتمد، الأقوى) that
  selects among competing positions should remain with the alternatives it
  judges when the alternatives are only briefly mentioned. However, when a
  long dispute section extensively lists multiple opinions with evidence,
  the tarjīḥ conclusion MAY be a separate teaching unit (see FP-8).
  Default: keep together unless the dispute section is substantial enough
  to stand alone as a distinct teaching unit.
- Qualifications and disclaimers (لكن، غير أن، إلا أن، على خلاف) MUST
  remain with the statement they qualify. A rule without its qualification
  is actively misleading.
- A question (فإن قيل، سؤال، اعترض) and its answer (قلنا، الجواب، وأجيب)
  MUST be in the same unit — even when multiple question-answer cycles
  appear in sequence

SELF-CONTAINMENT EVALUATION:
For each teaching unit, evaluate self-containment against these criteria:

C-SC-1 (Term Resolution): Every technical term is either defined within the
  unit, is standard terminology any student of the science would know, or is
  flagged as requiring external knowledge.

C-SC-2 (Reference Resolution): Every pronoun, demonstrative, anaphoric
  reference, or IMPLIED dependency resolves within the unit. No dangling
  references to text outside the unit. Watch for:
  - Visible: هذا/هذه/هؤلاء, المذكور/ما تقدم/ما سبق, pronoun suffixes
    (ـه/ـها/ـهم/ـهما), opening conjunctions (لأن/فإن)
  - Invisible (taqdir): implied subjects in قال/ذهب/رأى where the speaker
    is determined from prior context, not stated in this unit
  Note: opening و does NOT always indicate a dangling reference — it may
  simply continue within the same topic. Reason about whether each referent
  (visible or implied) resolves inside the unit. Do not flag blindly.

C-SC-3 (Evidence Completeness): Every evidence citation either includes its
  text, is a universally known citation identifiable by its opening words
  (e.g., حديث "إنما الأعمال بالنيات"), or is flagged.

C-SC-4 (Argument Completeness): The unit's argument, ruling, or teaching is
  complete — not a fragment whose premise or conclusion is elsewhere.

C-SC-5 (Dialogue Completeness): If the unit responds to another scholar's
  position, enough of that position is included to understand the response.

Assign self_containment as:
- FULL: All five criteria met. The unit stands alone.
- PARTIAL: Most criteria met, but some context would help. Populate
  self_containment_notes describing what's missing.
- DEPENDENT: Cannot be understood alone. Populate self_containment_notes
  explaining the dependency.

For each teaching unit, provide:
- unit_index: 0-based position in the sequence
- segment_indices: list of segment_index values composing this unit
  (must be a contiguous ascending sequence, e.g. [3, 4, 5])
- start_word: the start_word of the first constituent segment
- end_word: the end_word of the last constituent segment
- text_snippet: the FIRST 80 CHARACTERS of this unit's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace.
  COPY FIDELITY: text_snippet MUST be an exact character-for-character \
copy from the input text. Preserve all newlines (\\n) exactly as they \
appear. Do NOT reflow whitespace or collapse \\n to space.
- primary_function: the dominant scholarly function (must be a function present
  in the constituent segments)
- secondary_functions: other functions present in the unit (may be empty)
- description_arabic: a brief Arabic description of what this unit teaches,
  5 to 35 Arabic words. Write it as a student-facing summary.
- self_containment: FULL, PARTIAL, or DEPENDENT
- self_containment_notes: present and non-empty for PARTIAL/DEPENDENT;
  absent or null for FULL

The text format is: {structural_format}"""


# ═══════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════


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

    Uses the system prompt from §5.3.2 and user message from §5.3.3.
    Returns raw ExtractionResult.

    Args:
        error_feedback: Optional text appended to user message on retry (DD-S2-5).
        timeout_override: If provided, overrides config.GROUP_TIMEOUT (for retry escalation).
    """
    system_prompt = GROUP_SYSTEM_PROMPT.format(
        structural_format=chunk.structural_format.value,
    )

    segment_summary = _build_segment_summary(segments)
    user_message = (
        f"<text>\n{chunk.assembled_text}\n</text>\n\n"
        f"<classified_segments>\n{segment_summary}\n</classified_segments>"
    )
    if error_feedback:
        user_message += error_feedback

    timeout = timeout_override if timeout_override is not None else config.GROUP_TIMEOUT

    return client.chat.completions.create(
        model=config.GROUP_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=config.GROUP_MAX_TOKENS,
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

            system_prompt = GROUP_SYSTEM_PROMPT.format(
                structural_format=chunk.structural_format.value,
            )
            segment_summary = _build_segment_summary(segments)
            first_user_message = (
                f"<text>\n{chunk.assembled_text}\n</text>\n\n"
                f"<classified_segments>\n{segment_summary}\n</classified_segments>"
            )
            cache_key = compute_cache_key(
                "group",
                system_prompt,
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
