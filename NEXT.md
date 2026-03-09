# NEXT — Source Engine Session 3: LLM Inference + Consensus

**Session type:** BUILD — implement LLM metadata inference and multi-model consensus
**Pipeline steps:** Step 4 (Metadata Inference)
**Depends on:** Sessions 1–2 (staging + format detection + extraction — 217 tests passing)

---

## What to Read

Read these files in order before writing any code:

1. `engines/source/SPEC_CORE.md` §4.A.4 — LLM-Assisted Metadata Inference (the behavioral authority for this session)
2. `engines/source/SPEC_CORE.md` §6 — Consensus Integration (agreement rules, failure handling, directed attribution_status comparison)
3. `engines/source/prompts/inference_v1.py` — The validated prompt template (draft-3, final). This is the exact prompt to use.
4. `engines/source/contracts.py` — Data models: `InferredFieldConfidence`, `ScholarReference`, `TextLayer`, `ScholarlyContext`, `AttributionStatus`, `GenreChain`
5. `shared/consensus/REQUIREMENTS_source.md` — Consensus interface specification (function signatures, agreement rules, failure handling)
6. `engines/source/docs/technology-inventory.md` — Instructor configuration (use `from_provider()`, see RQ-1)
7. `.claude/skills/consensus-pattern/SKILL.md` — Implementation pattern for multi-model calls
8. `tests/fixtures/GROUND_TRUTH.json` — Expected answers for all 13 fixtures
9. `tests/eval_harness.py` lines 22–95 — Name matching functions to copy to production

---

## What to Build

### Module 1: `shared/scholar_authority/src/name_matching.py`
Copy from `tests/eval_harness.py` (lines 22–95):
- `normalize_arabic_name(name: str) -> str`
- `_extract_name_tokens(name: str) -> set`
- `normalized_name_similarity(a: str, b: str) -> float`

These are the production name matching functions. The token-based approach handles the A3-1 edge case (short-vs-long name forms). Do NOT use `difflib.SequenceMatcher`.

### Module 2: `shared/consensus/src/consensus.py`
Replace the tracer stub. Implement:
- `evaluate(task, messages, response_model, models, agreement_fn, simplified_messages) -> ConsensusResult`
- `messages` is a `list[dict]` — NOT a single string. Constructed from inference_v1.py's SYSTEM_MESSAGE + USER_MESSAGE_TEMPLATE:
  ```python
  messages = [
      {"role": "system", "content": SYSTEM_MESSAGE},
      {"role": "user", "content": user_prompt},  # filled from template
  ]
  ```
- Both model calls dispatched concurrently via `asyncio.gather()`
- Per-model retry: 2 retries (fresh request, then simplified_messages which removes library context)
- Fallback: if Command A fails → swap for GPT-5.4, retry consensus
- Timeout: 60s per model call via `asyncio.wait_for()`
- Use Instructor's `from_provider()`:
  ```python
  # Model A: Cohere Command A via OpenRouter
  client_a = instructor.from_provider("openrouter/cohere/command-a", async_client=True)
  
  # Model B: Opus 4.6 via Anthropic direct API
  client_b = instructor.from_provider("anthropic/claude-opus-4-6", async_client=True)
  ```
- API keys from environment: `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`
- **Important:** The `.claude/skills/consensus-pattern/SKILL.md` has been updated to use `from_provider()`. Do NOT use `from_litellm()` — that was the Step 2 testing pattern, not the production pattern.

### Module 3: `engines/source/src/consensus.py`
Source-engine consensus integration:
- Author identification agreement function (SPEC §6.1):
  - Both match same canonical_id → agree
  - Both say "new" + name similarity ≥ 0.90 + death date ±10 years → agree
  - Otherwise → disagree → human gate
- Work matching agreement function (SPEC §6.2)
- Directed attribution_status comparison (SPEC §6.3):
  - disputed/unknown beats definitive/traditional (conservative wins)
  - traditional vs definitive → use traditional, no gate
  - disputed/unknown vs definitive/traditional → use conservative + human gate

### Module 4: `engines/source/src/metadata_inference.py`
Core inference flow:
1. Build messages from extractor output using `inference_v1.py` template:
   - `messages = [{"role": "system", "content": SYSTEM_MESSAGE}, {"role": "user", "content": filled_template}]`
   - Also build `simplified_messages` with library context (existing scholars/works lists) removed from the user message
2. Call consensus ONCE: `evaluate(task="author_identification", messages=messages, ...)` with the author identification agreement function. This dispatches both models concurrently on the SAME prompt.
3. From the returned `ConsensusResult.model_responses`, run TWO additional local comparisons on the same response pair:
   - Work matching agreement check (engines/source/src/consensus.py)
   - Directed attribution_status comparison (engines/source/src/consensus.py)
   This avoids calling the models 4 times — one consensus call, three comparisons.
4. Use the canonical_result for ALL non-consensus fields (genre, science, format, level, scholarly_context, etc.)
5. Map LLM output → SourceMetadata fields:
   - `layers` → `text_layers` (resolve each layer author via scholar name matching)
   - `author_identification` → `ScholarReference` (canonical_name_ar, known_as, death_date_hijri, confidence)
   - Confidence fields → `InferredFieldConfidence`
6. Apply caps:
   - Biographical inference cap: author confidence ≤ 0.85 (single-LLM cap)
   - Attribution disputed: author confidence ≤ 0.70
   - Attribution unknown: author confidence = 0.0
7. Set `text_fidelity` deterministically:
   - `shamela_html` → baseline `high`; downgrade on quality issues
   - `plain_text` → baseline `medium`
8. Construct `needs_review_fields`: fields with confidence < 0.70

---

## What to Test

### Fixtures (in `.claudeignore` — use exact paths)

**Primary (run full inference):**
- `tests/fixtures/shamela_real/01_nahw_simple/book.htm`
- `tests/fixtures/shamela_real/06_usul/book.htm`
- `tests/fixtures/shamela_real/11_multi_small/` (3 files: 001.htm, 002.htm, 003.htm)

**Secondary (edge cases):**
- `tests/fixtures/shamela_real/03_fiqh/book.htm` (modern, no death date)
- `tests/fixtures/shamela_real/10_no_author/book.htm` (no المؤلف field)
- `tests/fixtures/alfiyyah_versified/` (plain text)

**Expected values:** `tests/fixtures/GROUND_TRUTH.json`

### Smoke test (run FIRST, before writing production code)

Verify Instructor works with both consensus models:
```python
# Quick test: send inference prompt for fixture 01 through each model
# Check: JSON parses, enum values validate, no timeout
```
Budget: ~$0.10. If either model fails with Instructor, fall back to raw LiteLLM calls with manual JSON parsing.

---

## Carry-Forward Tasks for This Session

### 1. Confidence Calibration Analysis (from Step 2 CG-1)
Extract confidence scores from Step 2 results at `tests/results/phase1_*.json`, `phase2_*.json`. Check: do models produce > 0.90 confidence on wrong answers? If so, raise thresholds above 0.70/0.50.

**If results files don't exist** (they're gitignored — may have been lost if environment was reset): re-run `tests/test_llm_inference.py --phase 2` to regenerate ($2–5 API cost). If not feasible, document that calibration is deferred and thresholds are maintained provisionally.

### 2. Author-Specific Consensus Complementarity (from Step 2 CG-5)
The consensus pair was selected on all 7 fields equally. Verify that Command A + Opus 4.6 is still the best pair when filtered to `author_identification` only.

Run `tests/consensus_analysis.py` filtered to author_identification. If a different pair ranks higher, update the consensus configuration.

**If results files don't exist:** Perform this check with live API calls during the Instructor smoke test — compare 3 models on 3 fixtures ($0.50–$1.00).

---

## Done When

- [ ] Instructor smoke test passes for Command A (OpenRouter) and Opus 4.6 (Anthropic)
- [ ] `metadata_inference.py` produces valid SourceMetadata fields for fixtures 01, 06, 11
- [ ] LLM output field mapping correct: `layers` → `text_layers`, `author_identification` → `ScholarReference`
- [ ] Confidence scores populate `InferredFieldConfidence` correctly
- [ ] Biographical inference cap applied (author confidence ≤ 0.85)
- [ ] Attribution status caps applied (disputed → 0.70, unknown → 0.0)
- [ ] `text_fidelity` set deterministically from format + quality issues
- [ ] `needs_review_fields` populated for fields with confidence < 0.70
- [ ] Consensus `evaluate()` dispatches both models concurrently
- [ ] Consensus `evaluate()` takes `messages: list[dict]` (NOT a prompt string)
- [ ] Single consensus call → three local comparisons (author, work, attribution) on same response pair
- [ ] Author identification agreement function implements §6.1 rules
- [ ] Work matching agreement function implements §6.2 rules
- [ ] Directed attribution_status comparison implements §6.3 (conservative value wins)
- [ ] Consensus failure: author ID → human gate; work matching → provisional accept
- [ ] Fallback: Command A failure → GPT-5.4 swap → retry
- [ ] Name matching in production location: `shared/scholar_authority/src/name_matching.py`
- [ ] Confidence calibration analysis complete OR documented as deferred with rationale
- [ ] Author-specific complementarity verified OR pair updated
- [ ] All new tests pass

---

## API Keys

Set these environment variables before running tests:
```bash
export ANTHROPIC_API_KEY="..."   # From project knowledge
export OPENROUTER_API_KEY="..."  # From project knowledge
```

Do NOT hardcode keys in source files. Read from environment at runtime.
