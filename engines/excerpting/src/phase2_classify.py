"""Phase 2a: Segment Classification + Offset Normalization (SPEC §5.2, §5.4.1–2).

Classifies each AssembledChunk's text into ClassifiedSegment objects using
one LLM call per chunk. Normalizes LLM-produced word offsets to canonical
tokenization using text_snippet anchors. Verifies segment coverage invariants.

All LLM calls go through OpenRouter via Instructor.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

import instructor
from pydantic import ValidationError

from engines.excerpting.contracts import (
    AssembledChunk,
    ClassificationResult,
    ClassifiedSegment,
    ExcerptingConfig,
    ExcerptingErrorCodes,
    validate_cs_invariants,
)

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════
# Constants
# ═══════════════════════════════════════════════════════════════════

# System prompt copied VERBATIM from SPEC §5.2.2 (lines 826–855).
# Only {structural_format} is substituted at call time (DD-S2-1).
CLASSIFY_SYSTEM_PROMPT = """\
You are an expert in classical Islamic scholarly text analysis (تحليل النصوص العلمية الإسلامية).

Classify each sentence or closely bonded group of sentences in this Arabic text
by scholarly function. The scholarly function types are:

  definition, rule_statement, evidence_quran, evidence_hadith, evidence_ijma,
  evidence_qiyas, evidence_rational, opinion_statement, refutation, example,
  condition_exception, cross_reference, narration, editorial_note,
  structural_transition, unclassified

Segment boundary rules:
- An isnad chain + its matn = one segment (narration or evidence_hadith)
- A position marker ("قال X") + the stated position = one segment
- Each Quran citation with its introduction = one segment
- A condition + its result ("إذا ... فـ") = one segment
- Each distinct sentence or bonded group gets exactly one classification
- Consecutive sentences serving the same function may form one segment
  if they are tightly bonded (e.g., a two-sentence definition)

For each segment, provide:
- segment_index: 0-based position in the sequence
- start_word: approximate start word offset in the text
- end_word: approximate end word offset in the text (inclusive)
- text_snippet: the FIRST 50 CHARACTERS of this segment's text, copied EXACTLY
  from the input — preserve all diacritics, punctuation, and whitespace precisely.
  This field is used for alignment; exact copying is critical.
- scholarly_function: one of the 16 types listed above
- confidence: your classification confidence from 0.0 to 1.0

The text format is: {structural_format}"""

# Arabic diacritics stripped in fallback matching (U+064B–U+0652, U+0670).
# Explicit set — NOT regex \p{Mn} which would strip non-Arabic combining marks.
_ARABIC_DIACRITICS = frozenset(
    "\u064B\u064C\u064D\u064E\u064F\u0650\u0651\u0652\u0670"
)

# Error feedback appended to user message on snippet-not-found retry (DD-S2-5).
_SNIPPET_NOT_FOUND_FEEDBACK = (
    "\n\nNote: The previous classification produced a text_snippet that "
    "could not be located in the source text. Ensure each text_snippet is "
    "copied exactly from the input."
)


# ═══════════════════════════════════════════════════════════════════
# Internal Helpers
# ═══════════════════════════════════════════════════════════════════


def _compute_classify_max_tokens(word_count: int) -> int:
    """Compute MAX_TOKENS for classification call based on input size (§5.5.1).

    ≤1500 words → 8192.  >1500 words → 32768.
    >4000 words → 32768 (provisional — untested, log warning).

    Threshold empirically adjusted from 2000 to 1500 (2026-03-28):
    ibn_aqil_v3 حروف الجر chunk (1987 words, 15 layers) exceeded 8192
    tokens on classification output. Dense multi-layer text needs margin.
    """
    if word_count > 4000:
        logger.warning(
            "Untested word count range: %d > 4000. Using MAX_TOKENS=32768 "
            "(provisional §5.5.1). Monitor for output truncation.",
            word_count,
        )
    if word_count > 1500:
        return 32768
    return 8192


def _build_token_char_map(assembled_text: str) -> list[tuple[int, int]]:
    """Map each token to its (char_start, char_end) span in assembled_text.

    Canonical tokenization: ``assembled_text.split()`` (Python whitespace split).
    Tracks position by skipping whitespace directly rather than using
    ``str.index()`` (avoids substring-match ambiguity on pathological inputs).
    """
    spans: list[tuple[int, int]] = []
    pos = 0
    text_len = len(assembled_text)
    for token in assembled_text.split():
        # Skip whitespace to find where this token starts
        while pos < text_len and assembled_text[pos] in " \t\n\r\v\f":
            pos += 1
        start = pos
        end = start + len(token)
        spans.append((start, end))
        pos = end
    return spans


def _char_to_token_index(
    char_pos: int, token_spans: list[tuple[int, int]]
) -> int:
    """Find the token index whose span contains or immediately follows *char_pos*.

    If *char_pos* falls in whitespace between tokens, returns the next token.
    """
    for i, (start, end) in enumerate(token_spans):
        if start <= char_pos < end:
            return i
        if start > char_pos:
            return i
    return len(token_spans) - 1


def _strip_text(
    text: str,
    *,
    collapse_ws: bool = False,
    strip_diacritics: bool = False,
) -> tuple[str, list[int]]:
    """Transform text while building a position map (transformed → original).

    Args:
        collapse_ws: Collapse whitespace runs to a single space.
        strip_diacritics: Remove Arabic diacritics (U+064B–U+0652, U+0670).

    Returns:
        ``(transformed_text, pos_map)`` where ``pos_map[i]`` is the original
        character index for transformed position *i*.
    """
    result: list[str] = []
    pos_map: list[int] = []
    prev_was_ws = False

    for i, ch in enumerate(text):
        if strip_diacritics and ch in _ARABIC_DIACRITICS:
            continue

        if collapse_ws and ch in " \t\n\r\v\f":
            if not prev_was_ws:
                result.append(" ")
                pos_map.append(i)
                prev_was_ws = True
            continue

        prev_was_ws = False
        result.append(ch)
        pos_map.append(i)

    return "".join(result), pos_map


def _find_snippet_position(
    snippet: str,
    assembled_text: str,
    search_start: int,
) -> tuple[int, bool]:
    """Find *snippet* in *assembled_text* starting from *search_start*.

    Matching cascade (§5.4.1):
      1. Exact match
      2. Whitespace-normalized (collapse runs → single space)
      3. Diacritic-stripped (U+064B–U+0652, U+0670)

    Returns:
        ``(char_position_in_original, diacritic_fallback_used)``

    Raises:
        ValueError: If snippet cannot be found after all three attempts.
    """
    # Attempt 1: Exact match
    pos = assembled_text.find(snippet, search_start)
    if pos >= 0:
        return pos, False

    search_region = assembled_text[search_start:]

    # Attempt 2: Whitespace-normalized
    ws_snippet, _ = _strip_text(snippet, collapse_ws=True)
    ws_region, ws_map = _strip_text(search_region, collapse_ws=True)
    ws_pos = ws_region.find(ws_snippet)
    if ws_pos >= 0 and ws_map:
        original_offset = ws_map[ws_pos]
        return search_start + original_offset, False

    # Attempt 3: Diacritic-stripped
    ds_snippet, _ = _strip_text(snippet, strip_diacritics=True)
    ds_region, ds_map = _strip_text(search_region, strip_diacritics=True)
    ds_pos = ds_region.find(ds_snippet)
    if ds_pos >= 0 and ds_map:
        original_offset = ds_map[ds_pos]
        logger.warning(
            "%s: text_snippet matched only after diacritic stripping. "
            "Snippet: %.50s",
            ExcerptingErrorCodes.EX_A_012,
            snippet,
        )
        return search_start + original_offset, True

    raise ValueError(
        f"Snippet not found after all matching attempts "
        f"(exact, whitespace-normalized, diacritic-stripped). "
        f"Snippet ({len(snippet)} chars): {snippet[:80]!r}"
    )


# ═══════════════════════════════════════════════════════════════════
# Public Functions
# ═══════════════════════════════════════════════════════════════════


def normalize_offsets(
    segments: list[ClassifiedSegment],
    assembled_text: str,
    total_tokens: int,
) -> list[ClassifiedSegment]:
    """Remap LLM-produced word offsets to canonical tokenization (§5.4.1).

    Uses ``text_snippet`` fields as alignment anchors.  Left-to-right search
    prevents misalignment from duplicate snippets.

    Matching cascade: exact → whitespace-normalized → diacritic-stripped.

    Returns a **new** list of ClassifiedSegment with canonical offsets
    (DD-S2-3: no mutation of originals).

    Raises:
        ValueError: If any snippet cannot be located after all attempts.
    """
    if not segments:
        return []

    # Step 1: Build token-to-character mapping
    token_spans = _build_token_char_map(assembled_text)

    # Step 2: Anchor each segment via text_snippet (left-to-right)
    anchored_starts: list[int] = []
    search_start_char = 0

    for seg in segments:
        char_pos, _diacritic_used = _find_snippet_position(
            seg.text_snippet, assembled_text, search_start_char
        )
        token_idx = _char_to_token_index(char_pos, token_spans)
        anchored_starts.append(token_idx)
        search_start_char = char_pos + 1

    # Step 3: Infer boundaries from contiguity
    canonical: list[ClassifiedSegment] = []
    for i, seg in enumerate(segments):
        start_word = anchored_starts[i]

        if i < len(segments) - 1:
            end_word = anchored_starts[i + 1] - 1
        else:
            end_word = total_tokens - 1

        if end_word < start_word:
            raise ValueError(
                f"Segment {seg.segment_index}: negative word range after "
                f"boundary inference (start={start_word}, end={end_word}). "
                f"Adjacent anchor at token {anchored_starts[i + 1] if i + 1 < len(anchored_starts) else 'N/A'}."
            )

        canonical.append(
            ClassifiedSegment(
                segment_index=seg.segment_index,
                start_word=start_word,
                end_word=end_word,
                text_snippet=seg.text_snippet,
                scholarly_function=seg.scholarly_function,
                confidence=seg.confidence,
            )
        )

    return canonical


def verify_segments(
    segments: list[ClassifiedSegment],
    total_tokens: int,
) -> None:
    """Verify segment coverage invariants V-P2-1 through V-P2-9 (§5.4.2).

    Delegates to ``validate_cs_invariants()`` in contracts.py.
    Raises ValueError on any fatal violation.
    """
    validate_cs_invariants(segments, total_tokens)


def classify_chunk(
    chunk: AssembledChunk,
    client: instructor.Instructor,
    config: ExcerptingConfig,
    error_feedback: Optional[str] = None,
) -> ClassificationResult:
    """Send chunk's assembled_text to LLM for segment classification (§5.2).

    Uses the system prompt from §5.2.2 and user message from §5.2.3.
    Returns raw ClassificationResult (offsets not yet normalized).

    Args:
        error_feedback: Optional text appended to user message on retry (DD-S2-5).
            System prompt stays constant across retries.
    """
    system_prompt = CLASSIFY_SYSTEM_PROMPT.format(
        structural_format=chunk.structural_format.value,
    )
    user_message = f"<text>\n{chunk.assembled_text}\n</text>"
    if error_feedback:
        user_message += error_feedback

    return client.chat.completions.create(
        model=config.CLASSIFY_MODEL,
        temperature=config.LLM_TEMPERATURE,
        max_tokens=_compute_classify_max_tokens(chunk.word_count),
        max_retries=0,
        timeout=config.TIMEOUT_SECONDS,
        response_model=ClassificationResult,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
    )


def run_phase2a(
    chunks: list[AssembledChunk],
    client: instructor.Instructor,
    config: ExcerptingConfig,
) -> dict[str, list[ClassifiedSegment]]:
    """Execute Phase 2a for all chunks: classify → normalize → verify (§5.1 steps 1–3).

    Retries per §5.5.2 (max ``1 + config.RETRY_COUNT`` attempts per chunk).
    Flags failed chunks with EX-C-001 / EX-C-003 / EX-C-004.

    Returns:
        ``dict[chunk_id → list[ClassifiedSegment]]``.
        Failed chunks are **absent** (logged, never silently dropped).
    """
    result: dict[str, list[ClassifiedSegment]] = {}
    max_attempts = 1 + config.RETRY_COUNT

    for chunk in chunks:
        error_feedback: Optional[str] = None
        last_error_code: Optional[str] = None
        success = False

        for attempt in range(max_attempts):
            phase = "classify"
            try:
                # Step 1: Classify (LLM call)
                start_time = time.monotonic()
                cr = classify_chunk(chunk, client, config, error_feedback)
                latency = time.monotonic() - start_time

                logger.info(
                    "Phase 2a classify: source_id=%s chunk_id=%s "
                    "latency=%.1fs attempt=%d segments=%d",
                    chunk.source_id,
                    chunk.chunk_id,
                    latency,
                    attempt + 1,
                    len(cr.segments),
                )

                # V-P2-9: total_segments consistency (warning only)
                if cr.total_segments != len(cr.segments):
                    logger.warning(
                        "V-P2-9: total_segments %d != len(segments) %d "
                        "for chunk %s. Using actual count.",
                        cr.total_segments,
                        len(cr.segments),
                        chunk.chunk_id,
                    )

                # Step 2: Normalize offsets
                phase = "normalize"
                canonical = normalize_offsets(
                    cr.segments, chunk.assembled_text, chunk.total_tokens
                )

                # Step 3: Verify segment coverage
                phase = "verify"
                verify_segments(canonical, chunk.total_tokens)

                result[chunk.chunk_id] = canonical
                success = True
                break

            except ValidationError as e:
                # ValidationError is a subclass of ValueError —
                # must be caught first (DD-S2-8: catch instructor
                # validation errors and retry).
                last_error_code = ExcerptingErrorCodes.EX_C_001
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
                if phase == "normalize":
                    last_error_code = ExcerptingErrorCodes.EX_C_003
                    error_feedback = _SNIPPET_NOT_FOUND_FEEDBACK
                else:
                    last_error_code = ExcerptingErrorCodes.EX_C_004
                    error_feedback = (
                        f"\n\nPrevious output violated coverage invariant: "
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
                last_error_code = ExcerptingErrorCodes.EX_C_001
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

        if not success:
            logger.error(
                "Phase 2a FAILED for chunk %s after %d attempts. "
                "Error code: %s. Chunk excluded from Phase 2b.",
                chunk.chunk_id,
                max_attempts,
                last_error_code,
            )

    return result
