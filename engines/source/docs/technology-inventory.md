# Source Engine — Technology Inventory

**Purpose:** Verify stack decisions before Claude Code begins Session 3 (LLM inference + consensus).

---

## Use (existing tool handles it)

| Capability | Library | Version | Evidence of Arabic support |
|-----------|---------|---------|---------------------------|
| HTML parsing | BeautifulSoup4 + lxml | bs4 latest, lxml latest | Sessions 1–2 validated on all 12 Shamela real fixtures. Unicode-safe. |
| SHA-256 hashing | hashlib (stdlib) | Python 3.10+ | No Arabic-specific needs — byte-level operation. |
| Schema validation | Pydantic v2 | ≥2.0 | contracts.py (~1020 lines) fully validated in tracer bullet and Sessions 1–2. |
| File encoding detection | charset_normalizer | ≥3.0 | Detects CP1256 and ISO-8859-6 for plain text (SPEC §4.A.2 Step 3). Preferred over chardet (faster, maintained). |
| Structured LLM output | Instructor | ≥1.12.0 | Supports Pydantic response_model with automatic validation and retry. Direct Cohere, Anthropic, and OpenRouter integration. See RQ-1 below. |
| Multi-provider LLM calls | LiteLLM | ≥1.40.0 | Routes to OpenRouter (Cohere Command A) and Anthropic API (Opus 4.6). Alternative: Instructor's `from_provider()` can handle routing directly without LiteLLM. |
| Async HTTP | httpx (via Instructor) | — | Instructor handles async internally. No separate httpx dependency needed. |

## Build (nothing suitable exists)

| Capability | Why build | Closest alternative | Gap |
|-----------|-----------|-------------------|-----|
| Scholar name matching | Domain-specific: must handle patronymic particles (بن/ابن), short-vs-long form matching (النووي vs أبو زكريا يحيى بن شرف النووي), token-based overlap scoring | PyArabic (`normalize_hamza`, `strip_diacritics`), CAMeL Tools NER | Neither provides scholarly name comparison. PyArabic is character-level normalization only. CAMeL Tools is heavyweight (PyTorch, large data downloads, Rust compiler) and focuses on NER/morphology, not identity matching. |
| Consensus evaluation | KR-specific agreement rules: directed attribution_status comparison, asymmetric failure handling by cascade risk, scholar registry integration | Generic multi-model comparison tools | No existing tool encodes SPEC §6 rules (name similarity ≥ 0.90 + death date ±10 years for agreement, conservative-value-wins for attribution). |
| Trust evaluation | 5-factor weighted algorithm with domain-specific scoring rules for tahqiq quality, publisher reputation, classical scholar thresholds | — | Entirely domain-specific. No existing tool. |
| Human gate checkpoint system | Owner interaction for low-confidence decisions with three-option response (approve/reject/unsure) and elevated consensus on "unsure" | — | No existing tool matches the SPEC §5 Layer 2 + KNOWLEDGE_INTEGRITY Layer 4 design. |

## Needs Testing (before committing)

| Capability | Candidate | Concern | How to test |
|-----------|-----------|---------|------------|
| Instructor + Command A via OpenRouter | `instructor.from_provider("openrouter/cohere/command-a")` | Step 2 used raw LiteLLM calls. Instructor's structured output mode may behave differently with Cohere's tool-calling implementation through OpenRouter. | Session 3 smoke test: send the inference_v1 prompt for fixture `01_nahw_simple` through Instructor with `response_model=InferenceOutput` (a Pydantic model matching the §4.A.4 schema). Verify JSON parses and enum values validate. Run for both consensus models. Budget: ~$0.05. |
| Instructor + Opus 4.6 via direct API | `instructor.from_provider("anthropic/claude-opus-4-6")` | Same concern as above — Step 2 tested raw API calls, not Instructor-wrapped calls. | Same smoke test as above, using the Anthropic model. |
| GPT-5.4 fallback via OpenRouter | `instructor.from_provider("openrouter/openai/gpt-5.4")` | Fallback model must also work with Instructor if Command A fails after retries. | Same smoke test, one call only. Budget: ~$0.03. |

---

## Research Question 1: Instructor + Command A via LiteLLM/OpenRouter

**Question:** Does Instructor's structured output mode work with Cohere Command A via LiteLLM through OpenRouter?

**Answer: YES — confirmed via documentation, with two viable paths.**

**Path A (recommended): Instructor native OpenRouter support.**
```python
client = instructor.from_provider(
    "openrouter/cohere/command-a",
    base_url="https://openrouter.ai/api/v1",
    async_client=True,
)
response = await client.create(
    response_model=InferenceOutput,
    messages=[...],
)
```
Instructor v1.12.0+ has direct OpenRouter integration via `from_provider("openrouter/...")`. OpenRouter lists Command A with tool calling and structured output support. Instructor's OpenRouter docs confirm Pydantic response_model works through this path.

**Path B (alternative): Instructor via LiteLLM.**
```python
client = instructor.from_litellm(litellm.acompletion)
response = await client.chat.completions.create(
    model="cohere/command-a",
    api_base="https://openrouter.ai/api/v1",
    response_model=InferenceOutput,
    messages=[...],
)
```
This is the pattern shown in the consensus-pattern skill. LiteLLM routes Cohere models through OpenRouter when api_base is set. Instructor wraps LiteLLM's completion function.

**Recommendation:** Use Path A for Session 3. It's simpler (no LiteLLM intermediary), and Instructor handles retry/validation internally. For the Anthropic model, use `instructor.from_provider("anthropic/claude-opus-4-6")` with the direct API key.

**Evidence sources:** Instructor OpenRouter integration docs (python.useinstructor.com/integrations/openrouter), Instructor Cohere integration docs (shows `command-a-03-2025` model), OpenRouter Command A model page (confirms tool calling support), LiteLLM Cohere provider docs.

**Risk:** Step 2 validated JSON reliability using raw LiteLLM calls, not Instructor-wrapped calls. Instructor adds tool-calling schema to the request, which changes the prompt structure. Session 3 must run a smoke test before committing to this approach. If Instructor's tool-calling mode produces parse failures on Command A, fall back to Path B or raw JSON mode (`mode=instructor.Mode.JSON`) which matches Step 2's behavior more closely.

---

## Research Question 2: Arabic Name Normalization

**Question:** PyArabic vs CAMeL Tools vs the custom token-based approach in eval_harness.py?

**Answer: Use the custom token-based approach. It is production-quality for this domain.**

### Analysis of each option

**PyArabic** provides character-level Arabic text utilities: `strip_diacritics()`, `normalize_hamza()`, `strip_tatweel()`, `normalize_ligature()`, tokenization. It handles the normalization step (diacritics, hamza forms, taa marbuta) well, but provides NO name comparison, NO patronymic parsing, and NO token-based matching. It would only replace the inner normalization logic of `normalize_arabic_name()` — about 8 lines of code.

**CAMeL Tools** is a comprehensive Arabic NLP toolkit from NYU Abu Dhabi: morphological analysis, Named Entity Recognition, dialect identification, sentiment analysis. It requires PyTorch, large downloaded data packages (multi-GB), a Rust compiler for installation, and Python 3.8–3.12. It is dramatically overweight for name normalization. Its NER could theoretically help identify name components, but it is trained on modern Arabic news text, not classical Islamic scholarly name formats (kunya + ism + nasab + nisba chains).

**Custom token-based approach (eval_harness.py)** already implements the complete pipeline:
1. **Normalization:** Strip diacritics (comprehensive Unicode range), normalize hamza (أ إ آ → ا), normalize taa marbuta (ة → ه), strip definite article (ال), collapse whitespace.
2. **Token extraction:** Split into tokens, remove patronymic particles (بن, ابن) which are structural connectors not identifying components.
3. **Comparison:** Token-set overlap relative to the shorter name. If all tokens of the shorter name appear in the longer → score ≥ 0.85 (auto-link). Substring fallback for compound-word mismatches.

This directly addresses the A3-1 problem: "النووي" (1 token: {نووي}) vs "أبو زكريا يحيى بن شرف النووي" (5 tokens: {ابو, زكريا, يحيى, شرف, نووي}). The shorter name's token set {نووي} is a subset of the longer name's tokens → score ≥ 0.85 → auto-link. SequenceMatcher would score this at 0.267 (character-level overlap), creating a false duplicate.

### Decision

**Keep the custom approach.** The eval_harness implementation is correct for the domain. Neither PyArabic nor CAMeL Tools solves the actual problem (scholarly name identity matching). The token-based approach handles short-vs-long forms, patronymic chains, and nisba comparison — which are domain-specific to Islamic scholarly names.

**Minor improvement (optional):** Replace the manual diacritics Unicode range in `normalize_arabic_name()` with PyArabic's `strip_diacritics()` for maintainability. This is a one-line change that doesn't affect behavior but uses a well-tested library for the normalization step. Not blocking.

**Action for Claude Code:** Copy `_extract_name_tokens()` and `normalized_name_similarity()` from `tests/eval_harness.py` into the production codebase (`shared/scholar_authority/src/name_matching.py`). Do NOT use `difflib.SequenceMatcher` — the SPEC's §4.A.1 still shows SequenceMatcher in the function docstring, but the eval_harness token-based implementation supersedes it (STEP2_EVALUATION Decision, A3-1 fix).
