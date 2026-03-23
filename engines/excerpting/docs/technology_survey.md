# Technology Survey — Excerpting Engine

Conducted 2026-03-23. All claims verified via web search and repo evidence.

## Use (existing tool handles it)

| Capability | Library | Arabic support evidence |
|-----------|---------|----------------------|
| Structured LLM output via Pydantic | `instructor` (≥1.8) | Validated in `experiments/architecture_test/run_tests.py` lines 157–170. Uses `instructor.from_openai()` with OpenRouter base_url, mode=JSON. Automatic validation retries built in. |
| OpenRouter API routing | `openai` SDK + OpenRouter base_url | All 3 SPEC models confirmed on OpenRouter: `anthropic/claude-opus-4.6` (1M ctx), `openai/gpt-4.1` (1M ctx), `cohere/command-a-03-2025` (256K ctx). Structured output support confirmed for all three. |
| Pydantic validation | `pydantic` v2 | Already used in `contracts.py` (1111 lines, 29 invariant checks). No Arabic-specific concerns — validation is schema-level. |

## Build (nothing suitable exists)

| Capability | Why build? | Closest alternative | Gap |
|-----------|-----------|-------------------|-----|
| Arabic word tokenization (I-AC-1) | SPEC defines `str.split()` as canonical tokenization. This is a coordinate system, not morphological analysis. Sophisticated tokenizers (CAMeL Tools, Farasa) would change the coordinate space and break LLM offset alignment. | `str.split()` (Python built-in) | No gap — `str.split()` IS the correct tool. `arabic_word_count()` filters for tokens with ≥1 Arabic char (U+0600–U+06FF). Validated in `extract_divisions.py:46`. |
| Quran verse pattern matching (F-DET-5) | Quran verses in Shamela use Unicode ornate parentheses: ﴿ (U+FD3F) and ﴾ (U+FD3E). Simple regex `r'﴿[^﴾]+﴾'` handles detection. No library needed. | N/A | N/A |
| Division tree traversal (§4.2) | Recursive tree walk on `DivisionNode.children`. Validated implementation: `find_leaf_divisions()` in `extract_divisions.py:83`. | N/A | N/A |
| Text layer rebasing (§4.6) | Pure character offset arithmetic. Validated implementation: `rebase_text_layers()` in `extract_divisions.py:137`. | N/A | N/A |
| Arabic noise stripping (§4.8) | Strip ZWNJ, ZWJ, diacritics, tatweel for comparison. Validated: `strip_arabic_noise()` in `extract_divisions.py:38`. | PyArabic has `strip_tashkeel()` | PyArabic strips only tashkeel. Our function also strips ZWNJ/ZWJ/tatweel. Custom is cleaner. |
| Footnote renumbering (§4.7) | Find `⌜N⌝` markers in text, renumber sequentially. Pure string manipulation. | N/A | N/A |
| Offset normalization (§5.4.1) | Remap LLM token offsets to canonical `str.split()` positions using `text_snippet` anchors. Custom algorithm validated in experiment (0 gaps across 162 boundaries). | N/A | N/A |
| Content flag aggregation (§4.7) | OR-aggregate boolean flags across content units. Validated: `aggregate_content_flags()` in `extract_divisions.py:169`. | N/A | N/A |
| Hadith collection name matching (§7.2.4) | Hardcoded list of canonical Arabic names for the 9+ major collections (صحيح البخاري, صحيح مسلم, etc.). Matching in scholarly text is fundamentally an LLM task (Phase 3). The engine needs a reference list for `TakhrijEntry.collection_name` validation. | Open datasets exist (mhashim6/Open-Hadith-Data) | Datasets provide names but not the fuzzy matching needed in running text. LLM handles matching; list is for validation only. |

## Needs testing

| Capability | Candidate | Concern | How to test |
|-----------|-----------|---------|-------------|
| `instructor` with `cohere/command-a-03-2025` via OpenRouter | `instructor.from_openai()` with mode=JSON | Cohere's structured output support confirmed on OpenRouter, but not tested in KR experiments. The escalation model (§7.3.3) uses this. | During Phase 3 build: make one test call with the enrichment schema. If JSON mode fails, fall back to `instructor.Mode.MD_JSON`. |
| MAX_TOKENS at 32768 for 4000+ word chunks | Opus 4.6 via OpenRouter | §5.5.1 notes this is untested — no experiment division exceeded 3111 words. Classify output may truncate. | During build evaluation: run classify on a 4500-word chunk. If output truncates, escalate to 65536. |

## Pattern to use

```python
import instructor
import openai

def create_client(api_key: str) -> instructor.Instructor:
    """Create Instructor-wrapped client for OpenRouter."""
    return instructor.from_openai(
        openai.OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        ),
        mode=instructor.Mode.JSON,
    )
```

This is the established KR pattern from `run_tests.py:157`. All three model providers (Anthropic, OpenAI, Cohere) work through the same OpenRouter endpoint — no provider-specific client code needed.

## Dependencies to install

```
instructor>=1.8
openai>=1.50
pydantic>=2.0
```

No additional dependencies for Phase 1 (fully deterministic, no LLM calls).
