# Build Prep Audit — Critical Review Before Session 3

**Date:** 2026-03-09
**Scope:** All 11 build prep artifacts reviewed against SPEC_CORE.md, contracts.py, inference_v1.py, and real-world API documentation.
**Method:** Line-by-line comparison of every function signature, data type, and behavioral claim against the SPEC authority. Web research to verify Instructor/OpenRouter integration claims.

---

## Defects Found: 3 Critical, 5 Important, 4 Minor

*Round 1 found and fixed 12 defects. Round 2 found 4 additional gaps.*

### Round 2 Findings (gaps that would block or slow Claude Code)

**G-1 (HIGH): `InferenceOutput` Pydantic model referenced but never defined.**

NEXT.md, session-3-plan, and consensus requirements all reference `InferenceOutput` as the `response_model` for Instructor, but no Pydantic model with this name exists anywhere in the codebase. Claude Code would have to reverse-engineer the model from the §4.A.4 JSON schema in the prompt template.

*Impact:* Claude Code spends 30+ minutes building a complex Pydantic model (~100 lines, 5 sub-models, constrained types) from a JSON example. Risk of field name mismatches with the prompt template or contracts.py.

*Fix:* Created `engines/source/src/inference_models.py` with the complete model: `InferenceOutput`, `InferredAuthorIdentification`, `InferredGenreChain`, `InferredLayer`, `InferredScholarlyContext`. Added to NEXT.md read list, session-3 module table, and architecture doc.

**G-2 (HIGH): `prompt_context` construction format undefined.**

inference_v1.py has `{prompt_context}` as a template variable. Neither NEXT.md nor the session plan specifies what goes into it. SPEC §4.A.4 describes the inputs conceptually ("Extracted metadata... Library context...") but not the exact string format that fills this variable.

*Impact:* Claude Code guesses the format. The library context section (existing scholars/works) may be omitted entirely or formatted incompatibly.

*Fix:* Added explicit `prompt_context` format specification to NEXT.md Module 4, including the exact template with field references. Defined the "=== LIBRARY CONTEXT ===" section boundary that gets removed in `simplified_messages`.

**G-3 (MEDIUM): `ConsensusResult.canonical_result` typed as `Optional[dict]` — loses Pydantic types.**

Instructor returns typed `InferenceOutput` objects, but `ModelResponse.raw_response: dict` and `ConsensusResult.canonical_result: Optional[dict]` convert them to dicts. The agreement_fn receives typed objects, but the caller (metadata_inference.py) gets back dicts and must re-parse or index manually.

*Fix:* Added `ModelResponse.parsed: Any` (stores the typed Pydantic object) alongside `raw_response: dict` (for serialization). Changed `ConsensusResult.canonical_result` to `Any`.

**G-4 (LOW): API key auto-detection for `from_provider("openrouter/...")` assumed but unverified.**

The smoke test will catch this, but Claude Code might waste time if `from_provider()` doesn't auto-detect `OPENROUTER_API_KEY`.

*Fix:* Added explicit fallback to NEXT.md API Keys section: pass `api_key=os.environ["OPENROUTER_API_KEY"]` if auto-detection fails.

**M-5: Consensus skill `check_agreement()` imports from `tests.eval_harness` instead of production location.**

Fixed — now imports from `shared.scholar_authority.src.name_matching`.

### CRITICAL (would cause build failure or incorrect implementation)

**C-1: `evaluate()` takes `prompt: str` but LLMs need `messages: list[dict]`.**

The inference template (inference_v1.py) has separate `SYSTEM_MESSAGE` and `USER_MESSAGE_TEMPLATE`. Instructor's `client.create()` requires a `messages` list with role/content dicts. The consensus `evaluate()` function accepted a single `prompt: str`, which cannot represent the system+user message structure.

*Impact:* Claude Code would have to invent how to merge system+user into one string, or split a string back into messages. Either approach introduces a fragile, undocumented transformation.

*Fix:* Changed `evaluate()` parameter from `prompt: str` to `messages: list[dict[str, str]]`. Added `simplified_messages: Optional[list[dict]]` for retry.

**C-2: Consensus-pattern skill contradicts NEXT.md on API pattern.**

The `.claude/skills/consensus-pattern/SKILL.md` used `instructor.from_litellm(litellm.acompletion)` — the Step 2 testing pattern. NEXT.md and the technology inventory recommend `instructor.from_provider()`. Claude Code treats `.claude/skills/` as authoritative implementation guides, so it would likely follow the skill over NEXT.md.

*Impact:* Claude Code builds with `from_litellm()`, which requires LiteLLM as an intermediary and doesn't match the from_provider() model identifiers in the config.

*Fix:* Updated the consensus-pattern skill to use `from_provider()` with `async_client=True` and `asyncio.gather()` for concurrent dispatch.

**C-3: Model identifier format inconsistency between config and `from_provider()`.**

The consensus config had `"model": "cohere/command-a"` with `"provider": "openrouter"` as separate fields. But `from_provider()` needs the full provider-prefixed string: `"openrouter/cohere/command-a"`. The consensus module would need to construct this string from two separate fields — an undocumented transformation.

*Impact:* Claude Code guesses how to assemble the `from_provider()` identifier, potentially getting it wrong for the Anthropic model (which uses `"anthropic/claude-opus-4-6"`, not `"openrouter/anthropic/claude-opus-4-6"`).

*Fix:* Replaced `"model"` + `"provider"` with single `"provider_model"` field containing the exact string `from_provider()` expects.

### IMPORTANT (would cause confusion or incorrect edge case handling)

**I-1: `agreement_fn` receives typed Pydantic objects or dicts — undocumented.**

`evaluate()` takes `response_model: type[BaseModel]` (Instructor returns Pydantic objects), but `ModelResponse` stores `raw_response: dict`. The agreement function's input types were not specified.

*Fix:* Documented that `agreement_fn` receives typed Pydantic model instances. `ModelResponse.raw_response` stores the dict form (via `.model_dump()`).

**I-2: `register()` canonical_id ownership contradiction.**

Scholar authority `register()` said both "canonical_id: assigned by this function" and record "Must have: canonical_id" — contradictory.

*Fix:* Clarified that the caller provides all fields EXCEPT canonical_id, which the function assigns.

**I-3: "Simplified prompt" for retry was undefined.**

Requirements said "remove library context to reduce tokens" but didn't specify what constitutes library context in the prompt.

*Fix:* Defined explicitly: the existing_scholars and existing_works lists are removed from the user message, keeping extracted metadata and text sample. Added `simplified_messages` parameter to `evaluate()`.

**I-4: "Call evaluate() twice" ambiguity — wastes API calls and money.**

SPEC §6 says "calls evaluate twice during Step 4: once for author identification, once for work matching." If taken literally, this sends the same prompt to both models twice (4 total LLM calls), doubling cost (~$0.20→$0.40 per source) with no accuracy benefit since both calls see identical input.

*Fix:* Added explicit "Call Pattern" section to consensus requirements: one consensus call, three local comparisons on the same response pair. NEXT.md Module 4 rewritten to describe this flow.

**I-5: Session 5 overloaded with 10 modules.**

Scholar authority + human gate + validation (shared + source) + trust evaluator + 3 registries + human gate wrapper = 10 modules in one session, roughly double the complexity of Sessions 3–4.

*Fix:* Added scope risk warning with recommended split strategy.

### MINOR (won't block build but reduce clarity)

**M-1: Timeout mechanism unspecified.**
*Fix:* Specified `asyncio.wait_for(coro, timeout=60.0)` in retry logic.

**M-2: `agreement_fn` type hint was `callable` instead of `Callable[[BaseModel, BaseModel], bool]`.**
*Fix:* Updated to proper `Callable` type with imports.

**M-3: Validation Check 4 depends on deduplication module (Session 4) — implicit dependency.**
*Status:* Documented but not fixed. The validation module will import from deduplication when it's built in Session 5. Not blocking for Session 3.

**M-4: Architecture doc had `name_matching.py` assigned to Session 5 instead of Session 3.**
*Fix:* Corrected in prior commit (pre-audit).

---

## Other Fixes Applied

- `requirements.txt`: Updated `instructor>=1.12.0` (from_provider support), `litellm>=1.40.0`, added `anthropic>=0.30.0` and `charset-normalizer>=3.0`.
- `shared/CLAUDE.md`: Updated consensus description from "LiteLLM + Instructor" to "Instructor from_provider()".
- `session-3-plan.md`: Aligned build steps with updated evaluate() interface and messages format.

---

## Verified (no issues found)

- All 6 Layer 1 validation checks in validation requirements match SPEC §5.
- Directed attribution_status comparison code in consensus requirements matches SPEC §6.3.
- Scholar authority name matching correctly specifies token-based approach (not SequenceMatcher).
- Session plans reference exact fixture paths.
- NEXT.md "Done When" checklist covers all Session 3 deliverables.
- GROUND_TRUTH.json exists with expected values for all 13 fixtures.
- Inference prompt template (inference_v1.py) includes all required fields.
- Web research confirms Instructor `from_provider("openrouter/...")` works with Cohere Command A via OpenRouter.
