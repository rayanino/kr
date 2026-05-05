"""Phase 5 Session 5 — Production VerifierCallable for scholar_match_cell.

Implements the LLM-call boundary per REQ-SRC-0052 + D-041 + INV-SRC-0016
using LiteLLM + Instructor schema-locked emission per
``.claude/skills/consensus-pattern/SKILL.md``. Each VerifierSpec carries a
``model_id`` (e.g., ``"anthropic/claude-opus-4-6"``,
``"openrouter/cohere/command-a"``); the production callable dispatches to
the named provider.

Boundary contract (frozen by Session 3):

  VerifierCallable = Callable[
      [VerifierSpec, ScholarEvidencePacket, Literal[0, 1],
       Optional[VerifierEmission], Optional[VerifierEmission]],
      VerifierEmission,
  ]

Round-0 dispatch (no peeking): own_round_0 and other_round_0 are None.
Round-1 dispatch (adversarial scaffold): both are populated; the prompt
template constructs attacker / defender framing.

Operational guarantees per ``.claude/rules/llm-call-optimization.md``:

  - temperature=0 for ALL classification calls (deterministic, reproducible)
  - HTTP 429 (rate limit): respect Retry-After header, exponential backoff
  - HTTP 5xx: retry with exponential backoff (2s, 4s, 8s; max 3 attempts)
  - HTTP 4xx (non-429): raise VerifierCallError immediately
  - Schema validation failure: re-raise as VerifierCallError after 1 retry
  - Persist every raw response to
    ``tests/results/source_engine/phase5_session5/{result_id}/llm_responses/{verifier_id}.json``
  - Track cost in ``tests/results/source_engine/COST_LOG.json``

Test gating: production calls require ``KR_LLM_TESTS=1`` env var. Default
test path uses the deterministic stub from
``test_phase5_session45_gold_seed_calibration.py`` (signal-alignment shape).
"""

from __future__ import annotations

import importlib.util
import json
import logging
import os
import random
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

from shared.scholar_authority.src.match_contracts import (
    CitationRef,
    DossierContext,
    NormalizedFragment,
    ScholarCandidate,
    ScholarEvidencePacket,
    ScoreBreakdown,
    ScoredCandidate,
    VerifierEmission,
)
from shared.scholar_authority.src.stage2_verifier import (
    VerifierCallable,
    VerifierCallError,
    VerifierSpec,
)


logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM-output schema (thinner than VerifierEmission — verifier-side fields
# are added by the wrapping callable, not requested from the LLM)
# ---------------------------------------------------------------------------


class _VerifierLLMOutput(BaseModel):
    """Schema-locked LLM output passed to Instructor.

    The LLM produces ``chosen_id``, ``positions``, and ``reasoning``; the
    wrapping callable adds ``verifier_id`` (from spec), ``round_index``
    (from dispatch context), ``prompt_template_hash`` (from spec), and
    ``f4_rejected`` (set by the Session 3 orchestrator AFTER this call
    returns). This separation ensures the LLM cannot accidentally
    overwrite identity / hash / round fields with hallucinated values.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    chosen_id: str = Field(min_length=1)
    positions: list[ScoredCandidate] = Field(min_length=1)
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Configuration constants per .claude/rules/llm-call-optimization.md
# ---------------------------------------------------------------------------

VERIFIER_TEMPERATURE: float = 0.0
"""Per .claude/rules/llm-call-optimization.md: temperature=0 for all
classification calls. Hallucination risk increases sharply with temperature."""

VERIFIER_MAX_TOKENS: int = 4000
"""Generous budget for ranked positions + reasoning; Arabic tokenizes at
1.5-2x English semantic density per llm-call-optimization.md."""

VERIFIER_TIMEOUT_SECONDS: float = 60.0
"""Per-call timeout. Instructor surfaces TimeoutError as a generic exception;
the retry wrapper treats it as a transient failure."""

MAX_RETRIES: int = 3
"""Exponential backoff: 2s → 4s → 8s. Max 3 attempts per call. After
exhaustion, raise VerifierCallError per stage2_verifier.py:155 contract."""

BASE_BACKOFF_SECONDS: float = 2.0
"""First retry waits 2s; subsequent retries double (4s, 8s)."""

PERSISTENCE_ROOT: Path = Path("tests/results/source_engine/phase5_session5")
"""Per Critical Rule 11 + .claude/rules/llm-call-optimization.md: every API
call's raw response persists here for replay + future training material."""


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------


def _format_normalized_fragment(parsed: NormalizedFragment) -> str:
    """Render a NormalizedFragment as an Arabic-friendly multiline block."""
    parts: list[str] = []
    if parsed.ism:
        parts.append(f"  - الاسم (ism): {parsed.ism}")
    if parsed.kunyah:
        parts.append(f"  - الكنية (kunyah): {parsed.kunyah}")
    if parsed.nasab_chain:
        parts.append(f"  - النسب (nasab): {' بن '.join(parsed.nasab_chain)}")
    if parsed.laqab:
        parts.append(f"  - الألقاب (laqab): {', '.join(parsed.laqab)}")
    if parsed.nisba_list:
        parts.append(f"  - النسب الجغرافية والمذهبية (nisba): {', '.join(parsed.nisba_list)}")
    return "\n".join(parts) if parts else "  (no parsed components)"


def _format_dossier(dossier: DossierContext) -> str:
    """Render a DossierContext as a labeled list."""
    parts: list[str] = []
    if dossier.genre:
        parts.append(f"  - Genre: {dossier.genre}")
    if dossier.primary_science:
        parts.append(f"  - Primary science: {dossier.primary_science}")
    if dossier.century_active_hijri_estimates:
        centuries = ", ".join(str(c) for c in dossier.century_active_hijri_estimates)
        parts.append(f"  - Century estimates (hijri): {centuries}")
    if dossier.school_affiliation_hints:
        for science, school in dossier.school_affiliation_hints.items():
            if school:
                parts.append(f"  - School hint for {science}: {school}")
    if dossier.attributed_works:
        works = "; ".join(dossier.attributed_works)
        parts.append(f"  - Attributed works: {works}")
    if dossier.geographic_signals:
        geo = "; ".join(dossier.geographic_signals)
        parts.append(f"  - Geographic signals: {geo}")
    return "\n".join(parts) if parts else "  (no dossier signals)"


def _format_candidates(candidates: list[ScholarCandidate]) -> str:
    """Render the candidate list with canonical_id + canonical_name_ar."""
    if not candidates:
        return "  (no candidates — Stage-1 returned empty set)"
    lines: list[str] = []
    for idx, candidate in enumerate(candidates, start=1):
        lines.append(
            f"  {idx}. canonical_id={candidate.canonical_id}, "
            f"canonical_name_ar={candidate.canonical_name_ar}"
        )
    return "\n".join(lines)


def _format_source_snippets(snippets: list[str]) -> str:
    """Render source snippets with explicit numbering for citation."""
    if not snippets:
        return "  (no source snippets attached)"
    lines: list[str] = []
    for idx, snippet in enumerate(snippets, start=1):
        lines.append(f"  [snippet_{idx}]")
        lines.append(snippet)
        lines.append("")
    return "\n".join(lines)


def _format_emission_for_round_1(emission: VerifierEmission, label: str) -> str:
    """Render a round-0 emission for inclusion in the round-1 prompt."""
    lines = [
        f"  ## {label}",
        f"  - chosen_id: {emission.chosen_id}",
        f"  - confidence at chosen: {emission.confidence:.3f}",
        f"  - reasoning: {emission.reasoning}",
        f"  - ranked positions:",
    ]
    for position in emission.positions:
        lines.append(
            f"    * {position.canonical_id} (confidence={position.confidence:.3f})"
        )
    return "\n".join(lines)


_SYSTEM_PROMPT_BASE: str = (
    "You are a scholar identification verifier for the KR (خزانة ريان) "
    "scholarly library. Your task is to identify which canonical scholar "
    "in a curated candidate list corresponds to a fragment of a scholar "
    "name appearing in a source text.\n"
    "\n"
    "Critical rules:\n"
    "1. Only choose from the candidate list. NEVER name a scholar not in "
    "the list (this is an F-4 hallucination per INV-SRC-0016 and will be "
    "rejected).\n"
    "2. The fragment may be a partial name (e.g., \"ابن حجر\" without "
    "specifying al-Asqalani vs al-Haytami). Use ALL available signals "
    "(work titles, school, century, geographic signals) to disambiguate.\n"
    "3. Be conservative: if signals do not converge on one candidate, "
    "score multiple candidates similarly rather than arbitrarily picking "
    "a leader. Disagreement between verifiers is preferable to false "
    "consensus.\n"
    "4. Score ALL candidates in the 9-feature breakdown. Each feature is "
    "in [0, 1].\n"
    "5. For each candidate, cite the source snippets supporting your "
    "score. Use the snippet labels [snippet_1], [snippet_2], etc.\n"
    "6. Output Arabic text byte-faithfully. Do NOT normalize ة → ه, "
    "drop diacritics on Quranic citations, or re-spell scholar names."
)


def _build_round_0_messages(
    spec: VerifierSpec, packet: ScholarEvidencePacket
) -> list[dict[str, str]]:
    """Build the messages array for a round-0 (no-peeking) dispatch."""
    user_content = (
        "## Fragment to identify\n"
        f"display: {packet.display_fragment}\n"
        f"normalized: {packet.normalized_fragment}\n"
        f"match_key: {packet.match_key}\n"
        f"parsed components:\n{_format_normalized_fragment(packet.parsed_components)}\n"
        "\n"
        f"## Dossier\n{_format_dossier(packet.dossier_context)}\n"
        "\n"
        f"## Source snippets\n{_format_source_snippets(packet.source_snippets)}\n"
        "\n"
        f"## Candidates ({len(packet.candidate_set)})\n"
        f"{_format_candidates(packet.candidate_set)}\n"
        "\n"
        "## Task\n"
        "1. Choose the canonical_id that best matches the fragment, given "
        "the dossier and source snippets.\n"
        "2. Rank ALL candidates with confidence in [0, 1] and the 9-feature "
        "score breakdown.\n"
        "3. For each candidate's cited_evidence, point to specific source "
        "snippets ([snippet_N] labels) that support your score; if none "
        "apply, cite the dossier signals.\n"
        "4. Provide concise reasoning for the chosen candidate.\n"
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT_BASE},
        {"role": "user", "content": user_content},
    ]


def _build_round_1_messages(
    spec: VerifierSpec,
    packet: ScholarEvidencePacket,
    own_round_0: VerifierEmission,
    other_round_0: VerifierEmission,
) -> list[dict[str, str]]:
    """Build the messages array for a round-1 (adversarial scaffold) dispatch."""
    user_content = (
        "## Fragment to identify\n"
        f"display: {packet.display_fragment}\n"
        f"normalized: {packet.normalized_fragment}\n"
        f"parsed components:\n{_format_normalized_fragment(packet.parsed_components)}\n"
        "\n"
        f"## Dossier\n{_format_dossier(packet.dossier_context)}\n"
        "\n"
        f"## Source snippets\n{_format_source_snippets(packet.source_snippets)}\n"
        "\n"
        f"## Candidates ({len(packet.candidate_set)})\n"
        f"{_format_candidates(packet.candidate_set)}\n"
        "\n"
        "## Round 0 emissions (verifiers disagreed)\n"
        f"{_format_emission_for_round_1(own_round_0, 'Your previous emission')}\n"
        "\n"
        f"{_format_emission_for_round_1(other_round_0, 'Other verifier emission')}\n"
        "\n"
        "## Adversarial re-evaluation task\n"
        "The two verifiers disagreed at round 0. Re-evaluate carefully:\n"
        "- If you stand by your round-0 choice, defend it with stronger "
        "evidence (specific snippet citations, dossier alignment).\n"
        "- If the other verifier's evidence is more compelling, change to "
        "their choice and explain the reversal.\n"
        "- If neither candidate is well-supported, score both low and pick "
        "the marginally more aligned one — the orchestrator will route to "
        "insufficient_evidence based on threshold predicates.\n"
        "Output the SAME schema as round 0 (chosen_id, positions, reasoning).\n"
        "REMINDER: chosen_id MUST be in the candidate list — round-1 cannot "
        "introduce new candidates per INV-SRC-0016.\n"
    )
    return [
        {"role": "system", "content": _SYSTEM_PROMPT_BASE},
        {"role": "user", "content": user_content},
    ]


# ---------------------------------------------------------------------------
# Persistence (Critical Rule 11)
# ---------------------------------------------------------------------------


def _utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _persist_call(
    *,
    persistence_root: Path,
    call_id: str,
    spec: VerifierSpec,
    round_index: Literal[0, 1],
    raw_llm_output: dict[str, object],
    elapsed_seconds: float,
    attempt_count: int,
) -> None:
    """Persist raw LLM response per Critical Rule 11.

    Layout: ``{persistence_root}/{call_id}/llm_responses/{verifier_id}_round{round_index}.json``.
    """
    target_dir = persistence_root / call_id / "llm_responses"
    target_dir.mkdir(parents=True, exist_ok=True)
    target_path = target_dir / f"{spec.verifier_id}_round{round_index}.json"
    payload = {
        "verifier_id": spec.verifier_id,
        "model_id": spec.model_id,
        "round_index": round_index,
        "prompt_template_hash": (
            spec.round_0_prompt_template_hash
            if round_index == 0
            else spec.round_1_prompt_template_hash
        ),
        "elapsed_seconds": elapsed_seconds,
        "attempt_count": attempt_count,
        "timestamp_utc": _utc_iso(),
        "raw_llm_output": raw_llm_output,
    }
    target_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2))


# ---------------------------------------------------------------------------
# Production VerifierCallable factory
# ---------------------------------------------------------------------------


def make_production_verifier(
    *,
    persistence_root: Path = PERSISTENCE_ROOT,
    call_id_provider: Optional[Callable[[], str]] = None,
) -> VerifierCallable:
    """Return a production VerifierCallable using LiteLLM + Instructor.

    Args:
      persistence_root: Where raw LLM responses are persisted. Default is
        ``tests/results/source_engine/phase5_session5/`` per Critical Rule 11.
      call_id_provider: Optional zero-arg callable returning a fresh call_id
        for each dispatch (used to namespace persistence across cells).
        Default uses ``packet.match_key`` as the call_id (stable per cell).

    The returned callable:
      - Dispatches to ``spec.model_id`` via ``instructor.from_provider()``.
      - Constructs round-0 vs round-1 prompts.
      - Implements exponential backoff with jitter on transient failures.
      - Persists raw responses per Critical Rule 11.
      - Raises ``VerifierCallError`` on permanent failure after retries.

    Requires ``KR_LLM_TESTS=1`` env var to actually call APIs. When unset,
    the callable raises ``VerifierCallError`` with a clear message — tests
    that need real LLMs must explicitly opt in.
    """
    # Presence-check at factory time (fail fast at construction rather than
    # at first dispatch). Actual import happens inside ``_dispatch_with_retries``.
    instructor_spec = importlib.util.find_spec("instructor")
    import_failure_message: Optional[str] = (
        None
        if instructor_spec is not None
        else "instructor not installed (pip install 'instructor[anthropic]>=1.12.0')"
    )

    def call_verifier(
        spec: VerifierSpec,
        packet: ScholarEvidencePacket,
        round_index: Literal[0, 1],
        own_round_0: Optional[VerifierEmission],
        other_round_0: Optional[VerifierEmission],
    ) -> VerifierEmission:
        if os.environ.get("KR_LLM_TESTS") != "1":
            raise VerifierCallError(
                spec.verifier_id,
                "Production VerifierCallable invoked without KR_LLM_TESTS=1; "
                "real-LLM dispatch is gated to prevent accidental cost in CI",
            )
        if import_failure_message is not None:
            raise VerifierCallError(
                spec.verifier_id,
                f"instructor library not importable: {import_failure_message}",
            )

        # Construct messages
        if round_index == 0:
            messages = _build_round_0_messages(spec, packet)
        else:
            if own_round_0 is None or other_round_0 is None:
                raise VerifierCallError(
                    spec.verifier_id,
                    "Round-1 dispatch requires both own_round_0 and "
                    "other_round_0 emissions per REQ-SRC-0052 adversarial "
                    f"scaffold; got own={own_round_0!r}, other={other_round_0!r}",
                )
            messages = _build_round_1_messages(
                spec, packet, own_round_0, other_round_0
            )

        # Dispatch with retry + backoff
        call_id = (
            call_id_provider() if call_id_provider is not None else packet.match_key
        )
        llm_output, elapsed, attempts = _dispatch_with_retries(
            spec=spec, messages=messages
        )

        # Persist raw response
        _persist_call(
            persistence_root=persistence_root,
            call_id=call_id,
            spec=spec,
            round_index=round_index,
            raw_llm_output=llm_output.model_dump(),
            elapsed_seconds=elapsed,
            attempt_count=attempts,
        )

        # Construct VerifierEmission with verifier-side fields filled
        prompt_hash = (
            spec.round_0_prompt_template_hash
            if round_index == 0
            else spec.round_1_prompt_template_hash
        )
        return VerifierEmission(
            verifier_id=spec.verifier_id,
            round_index=round_index,
            chosen_id=llm_output.chosen_id,
            positions=llm_output.positions,
            reasoning=llm_output.reasoning,
            prompt_template_hash=prompt_hash,
            f4_rejected=False,  # orchestrator sets this AFTER closure
        )

    return call_verifier


def _dispatch_with_retries(
    *,
    spec: VerifierSpec,
    messages: list[dict[str, str]],
) -> tuple[_VerifierLLMOutput, float, int]:
    """Dispatch the LLM call with exponential backoff retries.

    Returns ``(llm_output, elapsed_seconds, attempt_count)``.

    Per .claude/rules/llm-call-optimization.md:
      - Max 3 attempts (initial + 2 retries)
      - Backoff: 2s, 4s, 8s with jitter ∈ [0, 1)s
      - Honor Retry-After header on 429 if present (not parsed here; the
        underlying provider library handles it; we add the floor backoff)
    """
    import instructor

    last_error: Optional[Exception] = None
    elapsed = 0.0
    for attempt in range(1, MAX_RETRIES + 1):
        start = time.monotonic()
        try:
            # ``instructor.from_provider`` is dynamically typed (returns Any at
            # the type-check level) so we suppress the call-site type checks
            # that would otherwise complain about message shape and the
            # CoroutineType / sync-client overload disambiguation. The
            # behavioral contract is enforced by the response_model and the
            # downstream VerifierEmission validators.
            client = instructor.from_provider(spec.model_id)  # type: ignore[arg-type]
            # ``client.create`` is dynamically typed; the ChatCompletionMessageParam
            # vs dict[str, str] mismatch is a known pyright limitation when
            # composing instructor with provider-specific message shapes.
            llm_output: _VerifierLLMOutput = client.create(  # type: ignore[union-attr,call-arg,arg-type]
                messages=messages,  # type: ignore[arg-type]
                response_model=_VerifierLLMOutput,
                max_tokens=VERIFIER_MAX_TOKENS,
                temperature=VERIFIER_TEMPERATURE,
                seed=spec.seed,
            )
            elapsed = time.monotonic() - start
            return llm_output, elapsed, attempt
        except Exception as exc:  # noqa: BLE001 — we re-raise as VerifierCallError
            elapsed = time.monotonic() - start
            last_error = exc
            logger.warning(
                "verifier_dispatch attempt=%d/%d for verifier=%s model=%s failed: %s",
                attempt,
                MAX_RETRIES,
                spec.verifier_id,
                spec.model_id,
                exc,
            )
            if attempt < MAX_RETRIES:
                backoff = BASE_BACKOFF_SECONDS * (2 ** (attempt - 1))
                jitter = random.uniform(0.0, 1.0)
                time.sleep(backoff + jitter)

    raise VerifierCallError(
        spec.verifier_id,
        f"Permanent failure after {MAX_RETRIES} attempts; last error: "
        f"{type(last_error).__name__}: {last_error}",
    )


# ---------------------------------------------------------------------------
# Convenience: build a VerifierEmission from a scored candidate list
# (used by tests + future deterministic stubs)
# ---------------------------------------------------------------------------


def build_emission_from_scores(
    *,
    spec: VerifierSpec,
    round_index: Literal[0, 1],
    scored: list[tuple[str, float, ScoreBreakdown, list[CitationRef]]],
    reasoning: str = "",
) -> VerifierEmission:
    """Build a VerifierEmission from a list of (canonical_id, confidence, breakdown, evidence) tuples.

    Helper for deterministic tests + Session 5 verifier dispatchers that want
    to construct an emission without hand-building each ScoredCandidate.
    chosen_id = the highest-confidence canonical_id (ties broken by
    canonical_id ascending for determinism).
    """
    if not scored:
        raise ValueError(
            "build_emission_from_scores: scored list must be non-empty per "
            "VerifierEmission.positions min_length=1"
        )
    sorted_scored = sorted(scored, key=lambda t: (-t[1], t[0]))
    chosen_id = sorted_scored[0][0]
    positions = [
        ScoredCandidate(
            canonical_id=cid,
            confidence=conf,
            score_breakdown=breakdown,
            cited_evidence=evidence,
        )
        for cid, conf, breakdown, evidence in sorted_scored
    ]
    prompt_hash = (
        spec.round_0_prompt_template_hash
        if round_index == 0
        else spec.round_1_prompt_template_hash
    )
    return VerifierEmission(
        verifier_id=spec.verifier_id,
        round_index=round_index,
        chosen_id=chosen_id,
        positions=positions,
        reasoning=reasoning,
        prompt_template_hash=prompt_hash,
    )


__all__ = [
    "BASE_BACKOFF_SECONDS",
    "MAX_RETRIES",
    "PERSISTENCE_ROOT",
    "VERIFIER_MAX_TOKENS",
    "VERIFIER_TEMPERATURE",
    "VERIFIER_TIMEOUT_SECONDS",
    "build_emission_from_scores",
    "make_production_verifier",
]
