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
5. `engines/source/src/inference_models.py` — The `InferenceOutput` Pydantic model (and sub-models) used as Instructor's `response_model`. **Created in Module 0** of this session — build it first, then Modules 2–4 import from it.
6. `shared/consensus/REQUIREMENTS_source.md` — Consensus interface specification (function signatures, agreement rules, failure handling)
7. `engines/source/docs/technology-inventory.md` — Instructor configuration (use `from_provider()`, see RQ-1)
8. `.claude/skills/consensus-pattern/SKILL.md` — Implementation pattern for multi-model calls
9. `tests/fixtures/GROUND_TRUTH.json` — Expected answers for all 13 fixtures
10. `tests/eval_harness.py` lines 22–95 — Name matching functions to copy to production

---

## What to Build

### Module 0: `engines/source/src/inference_models.py` (ALREADY CREATED — verify it matches below)
The `InferenceOutput` Pydantic model that Instructor parses LLM responses into. This model matches the §4.A.4 inference output schema exactly. Without it, nothing else works — it is the `response_model` passed to `evaluate()`. The file is already created and should match this specification:

```python
from pydantic import BaseModel, Field
from typing import Optional, Literal
from engines.source.contracts import (
    Genre, StructuralFormat, WorkLevel, AuthorityLevel, AttributionStatus
)

class AuthorIdentificationOutput(BaseModel):
    canonical_name_ar: str
    known_as: list[str] = []
    death_date_hijri: Optional[int] = None
    school_affiliations: Optional[dict[str, Optional[str]]] = None
    sectarian_tradition: Optional[str] = None
    scholarly_standing: Optional[str] = None
    methodological_stance: Optional[str] = None

class LayerOutput(BaseModel):
    layer_type: Literal["matn", "sharh", "hashiyah", "tahqiq_note"]
    author_name: str  # Arabic name — resolved to ScholarReference AFTER inference

class GenreChainOutput(BaseModel):
    relation_type: str  # "sharh_of", "hashiyah_on", etc.
    base_work_title: str
    base_work_author: str

class ScholarlyContextOutput(BaseModel):
    composition_period: Optional[str] = None
    composition_date_hijri: Optional[int] = None
    tradition_position: Optional[str] = None
    known_textual_issues: list[str] = []
    historical_significance: Optional[str] = None
    muhaqiq_reputation: Optional[str] = None
    tahqiq_methodology_note: Optional[str] = None
    edition_known_issues: list[str] = []
    context_richness: Literal["rich", "partial", "minimal"] = "minimal"
    uncertain_dimensions: list[str] = []

class InferenceOutput(BaseModel):
    """The Pydantic model Instructor parses LLM responses into.
    Matches SPEC §4.A.4 inference output schema."""
    genre: str  # Will be validated against Genre enum after parsing
    genre_confidence: float = Field(ge=0.0, le=1.0)
    genre_chain: Optional[GenreChainOutput] = None
    genre_chain_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    structural_format: str
    structural_format_confidence: float = Field(ge=0.0, le=1.0)
    is_multi_layer: bool
    multi_layer_confidence: float = Field(ge=0.0, le=1.0)
    layers: Optional[list[LayerOutput]] = None
    science_scope: list[str]
    science_scope_confidence: float = Field(ge=0.0, le=1.0)
    level: Optional[str] = None
    level_confidence: Optional[float] = Field(None, ge=0.0, le=1.0)
    authority_level: str
    authority_level_confidence: float = Field(ge=0.0, le=1.0)
    author_identification: AuthorIdentificationOutput
    author_identification_confidence: float = Field(ge=0.0, le=1.0)
    attribution_status: str = "traditional"  # Validated against AttributionStatus after
    attribution_notes: Optional[str] = None
    scholarly_context: Optional[ScholarlyContextOutput] = None
```

**Why enum fields are `str` not the actual enum:** Instructor parses the LLM's raw JSON. If the LLM returns `"منظومة"` instead of `"nazm"`, Pydantic enum validation would reject it immediately. Using `str` lets the engine apply synonym normalization first (§4.A.4 LLM response validation, `library/config/genre_synonyms.json`), THEN validate against the enum. The engine validates enums after synonym mapping, not during parsing.

**Use single-call inference** (scholarly_context in same prompt as classification fields). Step 2 achieved 100% JSON parse rate across all models — above the 95% threshold for single-call.

### Module 1: `shared/scholar_authority/src/name_matching.py`
Copy from `tests/eval_harness.py` (lines 22–95):
- `normalize_arabic_name(name: str) -> str`
- `_extract_name_tokens(name: str) -> set`
- `normalized_name_similarity(a: str, b: str) -> float`

These are the production name matching functions. The token-based approach handles the A3-1 edge case (short-vs-long name forms). Do NOT use `difflib.SequenceMatcher`.

**WARNING:** SPEC §4.A.1 (lines ~292–312) still shows the OLD SequenceMatcher-based `normalized_name_similarity()` in its code. That version is SUPERSEDED. The eval_harness.py token-based version is authoritative (confirmed in STEP2_EVALUATION.md, A3-1 finding).

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
- **Client lifecycle:** Create Instructor clients once at module level (not inside every evaluate() call). Store them as module-level variables initialized on first use:
  ```python
  # Module-level — initialized once
  # Model A: Cohere Command A via OpenRouter
  client_a = instructor.from_provider("openrouter/cohere/command-a", async_client=True)
  
  # Model B: Opus 4.6 via Anthropic direct API
  client_b = instructor.from_provider("anthropic/claude-opus-4-6", async_client=True)
  ```
- API keys from environment: `OPENROUTER_API_KEY`, `ANTHROPIC_API_KEY`
- **Important:** The `.claude/skills/consensus-pattern/SKILL.md` uses `from_provider()` (correct). Do NOT use `from_litellm()` — that was the Step 2 testing pattern, not the production pattern.

### Module 3: `engines/source/src/consensus.py`
Source-engine consensus integration. This module defines the agreement functions that are passed to `evaluate()`.

**Author identification agreement function (SPEC §6.1):**
- The function is a **closure** that captures the scholar registry (the tracer stub at `shared/scholar_authority/src/__init__.py`):
  ```python
  def make_author_agreement_fn(scholar_lookup_fn):
      """Create an agreement function that uses the scholar registry.
      
      The LLM does NOT return canonical_ids — it returns names and dates.
      The ENGINE looks up each model's author in the registry to determine
      whether they resolve to the same scholar or are both new.
      """
      def author_agreement(response_a: InferenceOutput, response_b: InferenceOutput) -> bool:
          # Look up model A's author in registry
          match_a = scholar_lookup_fn(
              response_a.author_identification.canonical_name_ar,
              response_a.author_identification.death_date_hijri,
          )
          # Look up model B's author in registry
          match_b = scholar_lookup_fn(
              response_b.author_identification.canonical_name_ar,
              response_b.author_identification.death_date_hijri,
          )
          
          # Case A: Both match the same existing record
          if match_a and match_b and match_a.canonical_id == match_b.canonical_id:
              return True
          # Case B: Both say "new" (no registry match)
          if not match_a and not match_b:
              name_sim = normalized_name_similarity(
                  response_a.author_identification.canonical_name_ar,
                  response_b.author_identification.canonical_name_ar,
              )
              death_a = response_a.author_identification.death_date_hijri
              death_b = response_b.author_identification.death_date_hijri
              dates_agree = (death_a is None and death_b is None) or \
                            (death_a is not None and death_b is not None and abs(death_a - death_b) <= 10)
              return name_sim >= 0.90 and dates_agree
          # All other cases: disagreement
          return False
      return author_agreement
  ```
- **Scholar registry in Session 3:** The full `scholar_authority.py` is built in Session 5. For Session 3, use the tracer stub (`shared/scholar_authority/src/__init__.py`) which has in-memory lookup/register. Wire `name_matching.py` into the lookup by importing and using `normalized_name_similarity()` for comparison. The stub's substring matching is NOT sufficient — replace its lookup logic with token-based matching.
- Work matching agreement function (SPEC §6.2): compares inferred title and author. Both models producing the same genre_chain base work (if present) or similar titles → agree.
- Directed attribution_status comparison (SPEC §6.3):
  - disputed/unknown beats definitive/traditional (conservative wins)
  - traditional vs definitive → use traditional, no gate
  - disputed/unknown vs definitive/traditional → use conservative + human gate

### Module 4: `engines/source/src/metadata_inference.py`

**Prerequisites:**
- `engines/source/src/inference_models.py` — Created in Module 0 above. Contains the `InferenceOutput` Pydantic model that Instructor uses as `response_model`. Import it:
  ```python
  from engines.source.src.inference_models import InferenceOutput
  ```

**Constructing `prompt_context`** (fills the `{prompt_context}` variable in inference_v1.py):
```
Title: {extracted.get('display_title') or extracted.get('title_arabic', 'Unknown')}
Author: {extracted.get('author_name_raw', 'Not specified')}
Publisher: {extracted.get('publisher', 'Not specified')}
Shamela category: {extracted.get('shamela_category', 'N/A')}
Edition: {extracted.get('edition_raw', 'Not specified')}
Source format: {source_format.value}
Multi-volume: {'yes' if extracted.get('is_multi_volume') else 'no'}
Volume count: {extracted.get('volume_count', 1)}
Muhaqiq/Editor: {extracted.get('muhaqiq_name_raw', 'Not specified')}
Death date in metadata: {extracted.get('author_death_hijri', 'Not specified')}

=== LIBRARY CONTEXT ===
Existing scholars in library:
{newline-separated list of "sch_XXXXX: canonical_name_ar (d. death_date_hijri)" for each scholar in scholars.json}

Existing works in library:
{newline-separated list of "work_id: canonical_title (by author_canonical_id)" for each work in works.json}
```
If the library is empty (first intake), the LIBRARY CONTEXT section says "No existing scholars or works." The library context is what gets REMOVED in `simplified_messages` for retry — keep everything above the "=== LIBRARY CONTEXT ===" line.

**Core inference flow:**
1. Build `messages` from extractor output + inference_v1.py template (SYSTEM_MESSAGE + filled USER_MESSAGE_TEMPLATE)
2. Build `simplified_messages` — same but with LIBRARY CONTEXT section removed from user message
3. Call consensus ONCE: `evaluate(task="author_identification", messages=messages, response_model=InferenceOutput, ...)` with the author identification agreement function. This dispatches both models concurrently on the SAME prompt.
4. From the returned `ConsensusResult.model_responses`, each `ModelResponse.parsed` is an `InferenceOutput` object. Run TWO additional local comparisons on the same response pair:
   - Work matching agreement check (engines/source/src/consensus.py)
   - Directed attribution_status comparison (engines/source/src/consensus.py)
   This avoids calling the models 4 times — one consensus call, three comparisons.
5. Use `ConsensusResult.canonical_result` (an `InferenceOutput` object) for ALL fields.
6. **Enum validation with synonym fallback** (§4.A.4): Before mapping to SourceMetadata, validate each enum-constrained field (`genre`, `structural_format`, `authority_level`, `level`, `attribution_status`) against its Pydantic enum. If a value is not in the enum (e.g., `"منظومة"` for genre), check `library/config/genre_synonyms.json`. If no synonym match, set field to conservative default (`"other"` for genre, `"mixed"` for structural_format) with confidence 0.50 and add to `needs_review_fields`. Log a WARNING with the invalid value.
7. Map InferenceOutput → SourceMetadata fields:
   - `layers` → `text_layers` (resolve each layer `author_name` to a `ScholarReference` via scholar name matching)
   - `author_identification` → `ScholarReference`. **The `canonical_id` field is required.** For Session 3, use the tracer stub's `register()` to assign one (it returns the canonical_name as a placeholder ID — acceptable for Session 3 testing; Session 5 builds the real sequential ID generator). If the scholar was found by lookup, use the existing canonical_id.
   - Confidence fields → `InferredFieldConfidence`
8. Apply caps:
   - Biographical inference cap: author confidence ≤ 0.85 (single-LLM cap)
   - Attribution disputed: author confidence ≤ 0.70
   - Attribution unknown: author confidence = 0.0
9. Set `text_fidelity` deterministically:
   - `shamela_html` → baseline `high`; downgrade on quality issues
   - `plain_text` → baseline `medium`
10. Construct `needs_review_fields`: fields with confidence < 0.70

   Also add `"author"` if no `author_name_raw` in extractor output (§4.A.4).

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

- [ ] **InferenceOutput Pydantic model** created in `engines/source/src/inference_models.py` matching §4.A.4 schema
- [ ] Instructor smoke test passes for Command A (OpenRouter) and Opus 4.6 (Anthropic)
- [ ] `metadata_inference.py` produces valid SourceMetadata fields for fixtures 01, 06, 11
- [ ] LLM output field mapping correct: `layers` → `text_layers`, `author_identification` → `ScholarReference`
- [ ] Enum fields validated after synonym normalization (genre_synonyms.json fallback for non-standard values)
- [ ] Confidence scores populate `InferredFieldConfidence` correctly
- [ ] Biographical inference cap applied (author confidence ≤ 0.85)
- [ ] Attribution status caps applied (disputed → 0.70, unknown → 0.0)
- [ ] `text_fidelity` set deterministically from format + quality issues
- [ ] `needs_review_fields` populated for fields with confidence < 0.70
- [ ] `scholarly_context` fields populate correctly (or null when LLM returns minimal context)
- [ ] Consensus `evaluate()` dispatches both models concurrently
- [ ] Consensus `evaluate()` takes `messages: list[dict]` (NOT a prompt string)
- [ ] Single consensus call → three local comparisons (author, work, attribution) on same response pair
- [ ] Author identification agreement function implements §6.1 rules (including scholar registry lookup)
- [ ] Work matching agreement function implements §6.2 rules
- [ ] Work matching DISAGREEMENT (both models respond, disagree) → human gate
- [ ] Directed attribution_status comparison implements §6.3 (conservative value wins)
- [ ] Attribution status safety disagreement (disputed/unknown vs definitive/traditional) → creates human gate with CONSENSUS_DISAGREEMENT trigger
- [ ] Consensus failure: author ID → human gate; work matching failure (one model down) → provisional accept
- [ ] Fallback: Command A failure → GPT-5.4 swap → retry
- [ ] Name matching in production location: `shared/scholar_authority/src/name_matching.py`
- [ ] Tracer stub scholar_authority lookup updated to use token-based name matching (not substring)
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

**How `from_provider()` discovers keys:**
- `instructor.from_provider("anthropic/claude-opus-4-6")` → auto-reads `ANTHROPIC_API_KEY` from environment
- `instructor.from_provider("openrouter/cohere/command-a")` → auto-reads `OPENROUTER_API_KEY` from environment (uses OpenAI client internally with OpenRouter base URL)

**If auto-detection fails during smoke test:** Pass the key explicitly:
```python
import os
client = instructor.from_provider(
    "openrouter/cohere/command-a",
    api_key=os.environ["OPENROUTER_API_KEY"],
    async_client=True,
)
```
