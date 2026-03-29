# LLM Call Pattern Analysis & Cost/Speed Optimization Proposals

**Date:** 2026-03-28
**Analyst:** Performance engineering research agent
**Scope:** Excerpting engine LLM call sites (Phase 2a, 2b, 3 enrichment, 3 consensus)
**Baseline:** 2 chunks in 262s (4m 22s). Projected 308 chunks: 3-4 hours.

---

## Current Call Architecture

### Call Sites (5 total, confirmed from source)

| Call Site | File | Model | When | per-Chunk? |
|-----------|------|-------|------|------------|
| `classify_chunk` | `phase2_classify.py:343` | `anthropic/claude-opus-4.6` | Every chunk | Yes |
| `group_chunk` | `phase2_group.py:178` | `anthropic/claude-opus-4.6` | Every chunk | Yes |
| `enrich_chunk` | `phase3_enrichment.py:270` | `anthropic/claude-opus-4.6` | Every chunk | Yes |
| `verify_chunk` | `phase3_consensus.py:211` | `openai/gpt-5.4` | Chunks needing consensus | Conditional |
| `_call_escalation` | `phase3_consensus.py:462` | `mistralai/mistral-large-2411` | Attribution disputes | Rare |

### Sequencing (from `pipeline.py` and `phase3_orchestrator.py`)

```
FOR EACH chunk (SEQUENTIAL):
  Phase 2a: classify_chunk(chunk)           ~46s via CLI
  Phase 2b: group_chunk(chunk, segments)    ~42s via CLI
THEN:
  Phase 3 deterministic                     ~instant
  FOR EACH chunk (SEQUENTIAL):
    Phase 3 enrichment: enrich_chunk(chunk) ~43s via CLI
    Phase 3 consensus: verify_chunk(chunk)  ~43s via CLI (conditional)
  Phase 3 validation                        ~instant
```

**Key finding: ALL LLM calls are strictly sequential.** Each chunk waits for the
previous chunk to finish, and each phase waits for the previous phase to finish.
There is zero parallelism anywhere in the pipeline.

### Token Economics per Chunk

| Phase | System Prompt | User Content (typical) | Max Output | Est. Total |
|-------|--------------|----------------------|------------|------------|
| Classify | ~445 tokens | 1000-3000 (chunk text) | 8192-32768 | 2K-4K |
| Group | ~1200 tokens | 1500-4000 (text + segments) | 16384 | 3K-6K |
| Enrich | ~1913 tokens | 2000-5000 (text + units + metadata) | 16384-32768 | 4K-8K |
| Verify | ~435 tokens | 500-2000 (selective text) | 8192 | 1K-3K |

**Per chunk total: 10K-21K tokens across 3-4 calls.**
**308 chunks total: 3M-6.5M tokens.**

### CLI Adapter Overhead

Each LLM call spawns a fresh subprocess via `subprocess.run()`:
- Claude backend: `claude -p [prompt] --bare --model opus`
- Codex backend: `codex exec [prompt] --output-schema [file]`
- Gemini backend: `gemini -p [prompt] -y`

Each subprocess invocation incurs:
- Process spawn overhead: ~1-3s (Windows is heavier than Linux)
- CLI initialization/auth: ~2-5s per call
- Actual LLM processing: ~30-40s per call
- JSON parsing: negligible

The CLI overhead is ~5-10s per call, or ~15-40s per chunk across 3-4 calls.
For 308 chunks, that is 75-200 minutes of pure subprocess overhead.

---

## Optimization 1: Batching Multiple Chunks per LLM Call

### Feasibility Assessment

**Classification (Phase 2a):** The system prompt asks to classify each sentence/group
in "this Arabic text." The user message wraps text in `<text>` tags. Multiple chunks
COULD be sent as `<text id="chunk_1">...</text> <text id="chunk_2">...</text>`. The
response model `ClassificationResult` would need to become a list of per-chunk results.

**Problem:** Chunk text ranges from 50-5000 words. Five chunks at 2000 words each =
10,000 words = ~15K-20K input tokens. With output at ~3K tokens per chunk, that's
15K output tokens. This is within Opus 4.6's 200K context but creates fragility:
- LLM may confuse segments across chunks (snippet anchoring would fail)
- A single bad chunk poisons the entire batch (retry logic becomes complex)
- Output truncation at max_tokens would lose ALL chunks, not just one

**Grouping (Phase 2b):** Even harder to batch because the user message includes both
the full chunk text AND the classified segments from 2a. The prompt is already large.
Batching 5 chunks would create 25K+ token prompts with complex interleaving.

**Enrichment (Phase 3):** The user message includes chunk text, teaching units with
their annotations, evidence refs, and footnotes. Batching would create enormous prompts
and the structured output schema (`EnrichmentResult`) already returns per-unit arrays.

**Verification (Phase 3 consensus):** Already semi-batched -- `verify_chunk` processes
all items within a chunk in one call. Cross-chunk batching is possible for small items.

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | 2-3x for classification, 1.5-2x for others |
| Implementation effort | L (Large) -- requires new response models, prompt redesign, retry logic rewrite |
| Accuracy risk | **HIGH** -- snippet anchoring breaks, cross-chunk confusion, cascading failures |
| Recommendation | **REJECT for Phase 2a/2b/3 enrichment. PROTOTYPE for verification.** |

**Rationale:** The snippet-based offset normalization in Phase 2a (lines 242-306 of
`phase2_classify.py`) is the most fragile part of the pipeline. It relies on exact
text_snippet matching within the chunk text. Multi-chunk prompts would make snippet
confusion likely. The SPEC's per-chunk isolation guarantee (D-011) is architecturally
important. The accuracy risk outweighs the speed gain.

However, Phase 3 verification (`verify_chunk`) already batches items within a chunk.
Cross-chunk batching for verification items (school attribution checks, self-containment
assessments) is lower risk because verification items are self-contained with their own
text excerpts. Worth prototyping.

---

## Optimization 2: Smart Skipping for "Easy" Chunks

### What Can Be Detected Without LLM?

Examining the prompt and the 16-type taxonomy in `CLASSIFY_SYSTEM_PROMPT`:

**Detectable patterns (regex/heuristic):**

1. **Pure structural transitions:** Chunks consisting only of chapter headings
   (كتاب, باب, فصل) with no substantive content. These would classify as
   `structural_transition` with high certainty.
   - Detection: chunk has <20 words AND matches heading regex
   - Skip: classification AND grouping (becomes 1 unit = 1 segment)
   - Estimated frequency: 5-10% of chunks

2. **Isnad-heavy narration chunks:** Chunks dominated by transmission formulas
   (حدثنا, أخبرنا, سمعت) are almost certainly `narration` or `evidence_hadith`.
   - Detection: >50% of sentences start with transmission formula
   - Skip: classification (pre-assign `narration`), still need grouping
   - Estimated frequency: 10-20% in hadith collections, <5% in fiqh texts

3. **Single-topic tiny chunks:** After Phase 1 merging, some chunks are near the
   TINY_DIVISION_WORDS threshold (50 words). These almost always form a single
   teaching unit.
   - Detection: chunk.word_count < 100
   - Skip: grouping (1 unit = all segments)
   - Estimated frequency: 10-15% of chunks

4. **Consensus skipping:** If ALL enrichment fields have high confidence (school_confidence
   > 0.9, all scholars resolved with confidence > 0.8, self_containment = FULL), the
   consensus verification call adds little value.
   - Detection: check enrichment result confidence fields
   - Skip: verify_chunk call entirely
   - Estimated frequency: 40-60% of chunks (most units are FULL self-containment)

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | 1.3-1.5x overall (saves 30-50% of calls for some phases) |
| Implementation effort | M (Medium) -- heuristic detectors + bypass logic |
| Accuracy risk | **LOW for structural skipping, MEDIUM for consensus skipping** |
| Recommendation | **IMPLEMENT NOW: consensus skip + tiny chunk skip. PROTOTYPE: structural detection.** |

**Priority items:**
1. **Consensus skip (biggest win):** `_needs_consensus` in `phase3_consensus.py` already
   filters which units need verification. Adding a confidence threshold to skip the
   entire verify_chunk call when no units qualify saves ~43s per chunk. Currently it
   does this at the chunk level, but the call still happens. Adding an early-out at
   the `run_consensus` level for chunks where zero units trigger `_needs_consensus`
   would eliminate the subprocess overhead.
   **Actually, reading the code more carefully: `run_consensus` already does this check
   at line 748-751.** If `any_needs_consensus` is false, chunks pass through without
   an LLM call. This is already implemented. The win is extending the skip criteria
   to include high-confidence enrichment results.

2. **Tiny chunk grouping skip:** Chunks under 100 words almost always produce 1-3
   segments that form a single teaching unit. A heuristic bypass would save ~42s per
   qualifying chunk.

---

## Optimization 3: Embedding Pre-Filter / Clustering

### Concept

Generate vector embeddings for chunk text, cluster similar chunks, run full LLM
pipeline on cluster representatives only, and apply the representative's results
to all members of the cluster.

### Arabic Embedding Models (Research)

Available options as of March 2026:
- **Cohere embed-multilingual-v3.0**: Supports Arabic, 1024-dim, good for semantic search
- **OpenAI text-embedding-3-large**: Supports Arabic, 3072-dim
- **BGE-M3 (BAAI)**: Open-source multilingual, supports Arabic
- **Jina embeddings v2**: Multilingual, Arabic support
- **CAMeL-Lab models**: Arabic-specific from NYU Abu Dhabi, fine-tuned for Arabic NLP

### Why This Does Not Work for KR

The critical flaw: **classification and enrichment are content-dependent, not
topic-dependent.** Two chunks about the same topic (e.g., "conditions of wudu")
from different authors, schools, or structural formats will have:
- Different segment boundaries (classification depends on sentence structure)
- Different teaching unit groupings (depends on argument flow)
- Different school attributions (Hanafi vs. Shafi'i perspective)
- Different scholar references (different authorities cited)
- Different self-containment assessments (depends on cross-references)

Clustering by topic similarity would group chunks that need DIFFERENT metadata.
The only safe use would be for the `excerpt_topic` field alone, which is 1 of 7
enrichment fields -- not worth the infrastructure.

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | Theoretical 3-5x, practical <1.5x |
| Implementation effort | L (Large) -- embedding pipeline + clustering + merging logic |
| Accuracy risk | **HIGH** -- fundamentally wrong assumption (topic similarity != metadata similarity) |
| Recommendation | **REJECT.** |

---

## Optimization 4: Prompt-Level Caching

### How Often Do Identical Prompts Occur?

**System prompts:** The 4 system prompts are identical across all chunks (only
`{structural_format}` varies for classify/group). With ~3 structural formats,
there are at most 3 unique classify system prompts and 3 unique group system prompts.

**User prompts:** Every chunk has unique text content. No two user prompts will ever
be identical. Prompt-level hash caching would have a 0% hit rate.

**Response pattern caching:** Different from exact caching. If we stored "for chunks
of structure X with N segments of types Y, the grouping pattern was Z," we could
skip the grouping call. But the grouping depends on the semantic content, not just
the structure. Two chunks with 8 segments of the same type distribution will group
differently based on what the segments actually say.

### What About LLM Provider Caching?

**Anthropic prompt caching:** Anthropic's API supports prompt caching where the system
prompt (if >1024 tokens) is cached server-side. Subsequent calls with the same system
prompt prefix get a cache hit, reducing input token costs by 90% and latency by ~40%.

**But we use CLI, not API.** The `claude -p --bare` CLI invocation creates a fresh
session each time (`--no-session-persistence`). There is no mechanism to pass cache
control headers or reuse a prompt prefix. The CLI backend does not expose Anthropic's
prompt caching feature.

**Codex (OpenAI):** Similarly, `codex exec` does not expose OpenAI's cached prompts.

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | 0x (0% cache hit rate for user prompts) |
| Implementation effort | S (Small) for hash check, but useless |
| Accuracy risk | None |
| Recommendation | **REJECT for prompt caching. RESEARCH FURTHER: API-level prompt caching requires switching from CLI to API calls for system prompt reuse.** |

**Important finding:** If the project ever switches back to direct API calls (OpenRouter
or Anthropic API), prompt caching on the system prompt would save significant tokens.
The ENRICH_SYSTEM_PROMPT alone is ~1900 tokens, repeated 308 times = 585K wasted input
tokens. With Anthropic's prompt caching, this drops to ~60K cached tokens total.

---

## Optimization 5: Parallel Execution

### Current State: Zero Parallelism

Reading the code confirms complete sequential execution:

1. `run_phase2a` (line 356-478 of `phase2_classify.py`): `for chunk in chunks:` --
   plain sequential loop over all chunks.
2. `run_phase2b` (line 272-391 of `phase2_group.py`): `for chunk in chunks:` --
   plain sequential loop, depends on Phase 2a results but only per-chunk dependency.
3. `run_phase3_enrichment` (line 412-522 of `phase3_enrichment.py`):
   `for chunk_id, chunk_excerpts in excerpts_by_chunk.items():` -- sequential.
4. `run_consensus` (line 696-877 of `phase3_consensus.py`):
   `for chunk_id, chunk_excerpts in excerpts_by_chunk.items():` -- sequential.

**Critical insight:** Phase 2a chunks are independent of each other. Phase 2b chunks
are independent of each other (they only depend on their own Phase 2a output). Phase 3
enrichment chunks are independent. Phase 3 consensus chunks are independent.

**Within each phase, all chunks can run in parallel.**

### CLI Adapter Parallelism

The `CLIInstructorAdapter._invoke_backend` uses `subprocess.run()` (blocking).
To parallelize, the options are:

1. **`concurrent.futures.ThreadPoolExecutor`:** Spawn N threads, each calling
   `classify_chunk` for a different chunk. The CLI adapter uses `subprocess.run`
   which is blocking but thread-safe (each thread gets its own subprocess).
   - Limit: how many CLI processes can run simultaneously?
   - `claude` CLI: Each instance loads its own context. 4-8 concurrent is feasible.
   - `codex` CLI: Each creates temp files. Thread-safe if tempfile names differ (they do).
   - System limit: Windows process limits, available RAM (~16GB), CPU cores.

2. **`asyncio` + `subprocess.create_subprocess_exec`:** Fully async approach.
   Would require rewriting the adapter's `_invoke_backend` methods to be async.
   More complex but more efficient for I/O-bound workloads (which LLM calls are).

3. **`multiprocessing.Pool`:** Heavier but avoids GIL. Probably overkill since
   the work is I/O-bound (waiting for LLM responses), not CPU-bound.

### Speedup Calculation

**With ThreadPoolExecutor (N=4 workers per phase):**

| Phase | Sequential (308 chunks) | Parallel (4 workers) | Speedup |
|-------|------------------------|---------------------|---------|
| Phase 2a classify | 308 * 46s = 14,168s | 14,168s / 4 = 3,542s | 4x |
| Phase 2b group | 308 * 42s = 12,936s | 12,936s / 4 = 3,234s | 4x |
| Phase 3 enrich | 308 * 43s = 13,244s | 13,244s / 4 = 3,311s | 4x |
| Phase 3 consensus | ~150 * 43s = 6,450s | 6,450s / 4 = 1,613s | 4x |
| **Total** | **~13 hours** | **~3.2 hours** | **~4x** |

**With higher parallelism (N=8):**
Total drops to ~1.6 hours. But 8 concurrent `claude` CLI processes may hit rate
limits or degrade response quality.

### Cross-Phase Pipelining

Even more aggressive: start Phase 2b for chunk 1 as soon as Phase 2a for chunk 1
finishes, while Phase 2a is still processing chunk 2.

```
Time: ------>
Chunk 1: [2a][2b][enrich][verify]
Chunk 2:   [2a][2b][enrich][verify]
Chunk 3:     [2a][2b][enrich][verify]
...
```

This pipeline parallelism gives near-Nx speedup where N is the number of phases (4),
without requiring multiple concurrent LLM calls. The bottleneck becomes the slowest
single call per chunk (~46s classify), not the sum of all calls (~170s).

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | **4x with ThreadPool(4), 4x with pipeline parallelism, 8-16x with both** |
| Implementation effort | M (Medium) for ThreadPool, L for full pipeline |
| Accuracy risk | **NONE** -- chunks are independent within each phase |
| Recommendation | **IMPLEMENT NOW -- highest impact, zero accuracy risk** |

**Implementation plan:**
1. (Quick win) `ThreadPoolExecutor(max_workers=4)` wrapping each phase's for-loop.
   Replace `for chunk in chunks: result[chunk.chunk_id] = process(chunk)` with
   `futures = {executor.submit(process, chunk): chunk for chunk in chunks}`.
2. (Second stage) Cross-phase pipelining with `asyncio` or producer-consumer queues.

---

## Optimization 6: Batch API Research

### Claude Batch API (Anthropic)

Anthropic offers a Message Batches API:
- **Pricing:** 50% discount vs. standard API pricing
- **Latency:** Results within 24 hours (not real-time)
- **Max batch size:** Up to 100,000 requests per batch
- **Format:** JSONL file with each line being a complete message request
- **Status:** Generally available

**KR applicability:** 308 classification calls could be a single batch. At 50% discount
this halves the token cost. But the 24-hour turnaround makes it unsuitable for
iterative development. Could work for "overnight run" mode.

**CLI access:** Not available via `claude -p`. Requires direct API calls with
`anthropic.Anthropic().messages.batches.create()`.

### OpenAI Batch API

OpenAI offers a Batch API:
- **Pricing:** 50% discount
- **Latency:** Results within 24 hours
- **Format:** JSONL upload
- **Status:** Available for GPT-4o, GPT-4o-mini, embeddings

**KR applicability:** The verification calls (Phase 3 consensus, `openai/gpt-5.4`)
could use this. But same 24-hour limitation.

### Gemini Batch Prediction

Google offers batch prediction via Vertex AI:
- **Pricing:** Varies, generally cheaper than online
- **Latency:** Hours to days depending on queue
- **Status:** Available for Gemini models

**KR applicability:** Escalation calls only (rare), not worth the integration effort.

### Codex Batch Mode

OpenAI's Codex CLI (`codex exec`):
- No native batch mode in the CLI
- Could batch via the API with Batch API endpoint
- Codex CLI is an agent wrapper; batch mode would bypass the agent loop

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | 0x (same total compute time) |
| Estimated cost savings | **50% on API calls** (but currently $0 via CLI) |
| Implementation effort | M (Medium) -- new batch submission + polling + result collection |
| Accuracy risk | None |
| Recommendation | **RESEARCH FURTHER -- only valuable if/when switching from $0 CLI to paid API calls. Currently irrelevant since all calls go through free CLI.** |

**Critical context:** The CLI adapter was built specifically because CLI calls are
free ($0) via existing Max/Pro subscriptions. Batch API requires paid API calls.
The 50% discount on paid calls is still infinitely more expensive than $0 CLI calls.
This optimization only becomes relevant if CLI backends become unavailable or too slow.

---

## Optimization 7: Model Size Optimization

### Current Model Assignment

| Task | Current Model | Reasoning |
|------|--------------|-----------|
| Classify | `anthropic/claude-opus-4.6` | Segment boundary detection in complex Arabic scholarly text |
| Group | `anthropic/claude-opus-4.6` | Teaching unit formation requires deep scholarly understanding |
| Enrich | `anthropic/claude-opus-4.6` | Scholar resolution, school attribution, takhrij extraction |
| Verify | `openai/gpt-5.4` | Cross-provider consensus (different from enrichment model) |
| Escalate | `mistralai/mistral-large-2411` | Third opinion for disagreements |

### Could Smaller Models Handle Some Tasks?

**Classification (REJECT smaller model):**
The 16-type scholarly function taxonomy (`definition`, `rule_statement`,
`evidence_quran`, `evidence_hadith`, etc.) requires deep understanding of Arabic
scholarly conventions. The snippet anchor requirement (first 50 characters copied
EXACTLY) fails more often with smaller models that paraphrase or truncate. The
offset normalization cascade (exact -> whitespace -> diacritic) would get more
fallback hits with lower-quality snippets.

**Grouping (REJECT smaller model):**
The decontextualization prevention rules are the hardest part of the pipeline.
A smaller model might group a refutation separately from its target position,
violating SPEC section 5.3.2 critical rules. This is the highest-stakes LLM
task -- wrong grouping creates misleading excerpts.

**Enrichment (PARTIALLY feasible for some fields):**

Fields by difficulty:
- `excerpt_topic` (keywords): M difficulty -- could use a smaller model
- `school` (attribution): H difficulty -- requires school-specific terminology detection
- `resolved_scholars` (scholar resolution): H difficulty -- epithet resolution is hard
- `takhrij_data` (hadith sourcing): H difficulty -- collection identification is specialized
- `terminology_variants`: M difficulty -- dictionary-level task
- `cross_references`: L difficulty -- pattern matching
- `context_hint`: M difficulty -- requires understanding what's missing

Only `excerpt_topic`, `terminology_variants`, and `cross_references` could potentially
use a smaller model. But splitting enrichment into two calls (small model for easy
fields, large model for hard fields) would INCREASE total calls, not decrease them.

**Verification (already optimized):**
GPT-5.4 is used specifically because it's faster than Opus (3-4x per CLAUDE.md) and
provides cross-provider diversity. Switching to a smaller OpenAI model would reduce
verification quality on the most safety-critical step.

### Rule-Based Alternatives

Some fields could be extracted without LLM at all:

1. **cross_references:** The Arabic cross-reference formulas are listed in
   `.claude/rules/arabic-scholarly-conventions.md`:
   كما تقدم, كما سبق, سيأتي, انظر, راجع. These could be detected with regex.
   Estimated coverage: 80% of cross-references are formulaic.

2. **terminology_variants:** A static dictionary of known Arabic scholarly term
   equivalences could handle common cases (القراض/المضاربة, الحدث/النجاسة الحكمية).
   But the dictionary would need continuous maintenance.

3. **page_range, word_count, div_path, evidence_refs:** Already deterministic
   (F-DET-1 through F-DET-9 in `phase3_deterministic.py`). These are computed
   without LLM. This is correctly implemented.

### Assessment

| Metric | Value |
|--------|-------|
| Estimated speedup | 0x (CLI calls are all the same cost/speed regardless of model) |
| Implementation effort | M for rule-based extractors |
| Accuracy risk | **HIGH for model downgrades, LOW for rule-based additions** |
| Recommendation | **IMPLEMENT NOW: rule-based cross_reference detection as a deterministic field (F-DET-10). REJECT: model downgrades for any classification/enrichment task.** |

**Critical insight for CLI mode:** When using CLI backends, model size does NOT affect
cost (all $0) and only marginally affects speed. The `claude -p --model opus` call
takes ~40-46s. Using `--model sonnet` would take ~25-30s -- a 40% improvement per
call but at significant accuracy cost. The 15s/call saving across 308 chunks * 3
calls = 4620s (~77 minutes) saved. This is less impactful than parallelism (which
saves hours, not minutes).

---

## Summary: Optimization Priority Matrix

| # | Optimization | Speedup | Effort | Risk | Verdict |
|---|-------------|---------|--------|------|---------|
| **5** | **Parallel execution (ThreadPool)** | **4-8x** | **M** | **None** | **IMPLEMENT NOW** |
| **2a** | **Consensus skip (confidence threshold)** | **1.2-1.4x** | **S** | **Low** | **IMPLEMENT NOW** |
| **2b** | **Tiny chunk grouping skip** | **1.1-1.2x** | **S** | **Low** | **IMPLEMENT NOW** |
| **7c** | **Rule-based cross-reference extraction** | **N/A (accuracy)** | **S** | **None** | **IMPLEMENT NOW** |
| **5b** | **Cross-phase pipelining** | **Additional 2-4x** | **L** | **None** | **PROTOTYPE** |
| **1d** | **Batch verification calls** | **1.1-1.3x** | **M** | **Low** | **PROTOTYPE** |
| 4 | Prompt-level caching | 0x | S | None | REJECT |
| 3 | Embedding pre-filter | <1.5x | L | High | REJECT |
| 1 | Multi-chunk batching (classify/group) | 2-3x | L | High | REJECT |
| 6 | Batch API (24h turnaround) | 0x speed | M | None | DEFER (costs $0 via CLI) |
| 7a | Smaller classify/group model | 1.4x | S | High | REJECT |
| 7b | Smaller enrichment model | 1.3x | M | High | REJECT |

---

## Recommended Implementation Roadmap

### Phase A: Parallelism (biggest win, zero risk)

**Estimated effort:** 2-3 hours implementation + 1 hour testing.
**Estimated impact:** 4x speedup (13h -> 3.2h for 308 chunks).

1. Add `concurrent.futures.ThreadPoolExecutor` to `run_phase2a`:
   ```python
   with ThreadPoolExecutor(max_workers=4) as executor:
       futures = {
           executor.submit(_process_chunk_2a, chunk, client, config): chunk
           for chunk in chunks
       }
       for future in as_completed(futures):
           chunk = futures[future]
           result[chunk.chunk_id] = future.result()
   ```
2. Same pattern for `run_phase2b`, `run_phase3_enrichment`, `run_consensus`.
3. Add `MAX_PARALLEL_LLM` config parameter (default 4, tunable).
4. Test: run on 10 chunks with parallelism=1 and parallelism=4, verify identical results.

**Risks to monitor:**
- Windows subprocess limits (test at N=8 to find ceiling)
- CLI tool rate limiting (unlikely for free-tier tools)
- Memory usage (4 concurrent Opus contexts ~4-8GB)
- Logging interleaving (use chunk_id prefixed log format)

### Phase B: Smart Skipping (small wins, low risk)

**Estimated effort:** 1-2 hours.
**Estimated impact:** 1.2-1.4x additional speedup.

1. Add confidence-based consensus skip threshold to `ExcerptingConfig`.
2. Add word_count < 100 single-unit bypass in `run_phase2b`.
3. Add structural-only chunk detection (heading-only) to skip Phase 2a.

### Phase C: Rule-Based Enrichment (accuracy improvement)

**Estimated effort:** 2-3 hours.
**Estimated impact:** Better cross-reference data, reduced LLM dependency.

1. Implement `detect_cross_references()` as F-DET-10 in `phase3_deterministic.py`.
2. Pass detected references to LLM as hints (reduces LLM work, improves accuracy).
3. Compare LLM-detected vs. rule-detected references for quality validation.

---

## Key Findings

1. **The single biggest bottleneck is sequential execution.** Every chunk waits for
   every other chunk, and chunks are independent within each phase. Parallelism is
   the only optimization that can deliver order-of-magnitude improvement with zero
   accuracy risk.

2. **The CLI adapter is inherently parallelizable.** Each `subprocess.run()` call is
   independent. `ThreadPoolExecutor` wrapping is straightforward and requires no
   changes to the adapter itself.

3. **Batching and caching are largely irrelevant in CLI mode.** The $0 cost model
   means token-saving optimizations have no cost benefit, and the per-call subprocess
   overhead dominates latency regardless of prompt size.

4. **Model downgrades are counterproductive in CLI mode.** When calls are free, the
   only reason to use a smaller model is speed. The 15s/call speedup from Sonnet vs
   Opus is dwarfed by the 4x+ speedup from parallelism, and comes with real accuracy
   risk on the pipeline's most critical tasks.

5. **The consensus skip is already partially implemented** in `run_consensus` at line
   748. The enhancement is to add enrichment-confidence-based skipping for additional
   chunks that technically trigger consensus but have high-confidence enrichment results.
