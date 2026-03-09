# Session 3 Plan: LLM Inference + Consensus

**Pipeline steps:** Step 4 (Metadata Inference)
**Depends on:** Sessions 1–2 (staging + format detection + extraction — complete)

---

## Read First

1. `engines/source/SPEC_CORE.md` §4.A.4 (LLM-Assisted Metadata Inference — full section)
2. `engines/source/SPEC_CORE.md` §6 (Consensus Integration — full section)
3. `engines/source/prompts/inference_v1.py` (validated prompt template)
4. `engines/source/contracts.py` — `InferredFieldConfidence`, `ScholarReference`, `TextLayer`, `ScholarlyContext`, `AttributionStatus`, `GenreChain`
5. `shared/consensus/REQUIREMENTS_source.md` (consensus interface spec)
6. `.claude/skills/consensus-pattern/SKILL.md` (implementation pattern)
7. `engines/source/docs/technology-inventory.md` (Instructor configuration — RQ-1)
8. `tests/fixtures/GROUND_TRUTH.json` (expected answers for all 13 fixtures)

## Modules to Build

| File | Purpose |
|------|---------|
| `engines/source/src/inference_models.py` | **Already created** — `InferenceOutput` Pydantic model and sub-models. Import it, do not recreate. This is the `response_model` for Instructor. |
| `engines/source/src/metadata_inference.py` | Prompt construction, LLM call via Instructor, response parsing, field mapping (InferenceOutput → SourceMetadata), confidence scoring, attribution status caps |
| `shared/consensus/src/consensus.py` | Replace tracer stub. Implement `evaluate()` with per-model async calls, retry logic, timeout handling, fallback model swap |
| `engines/source/src/consensus.py` | Source-engine consensus integration: author identification agreement fn, work matching agreement fn, directed attribution_status comparison |
| `shared/scholar_authority/src/name_matching.py` | Copy `normalize_arabic_name()`, `_extract_name_tokens()`, `normalized_name_similarity()` from `tests/eval_harness.py` into production location |

## Fixtures to Test Against

All fixtures are in `tests/fixtures/` (in `.claudeignore` — must reference exact paths):

**Primary fixtures (diverse coverage):**
- `tests/fixtures/shamela_real/01_nahw_simple/book.htm` — single-volume, simple case
- `tests/fixtures/shamela_real/06_usul/book.htm` — single-volume, different science
- `tests/fixtures/shamela_real/11_multi_small/` — multi-volume (3 files: 001.htm, 002.htm, 003.htm), multi-layer sharh

**Secondary fixtures (edge cases):**
- `tests/fixtures/shamela_real/03_fiqh/book.htm` — modern author, no death date → flagged trust
- `tests/fixtures/shamela_real/10_no_author/book.htm` — no المؤلف field → author entirely LLM-inferred
- `tests/fixtures/alfiyyah_versified/` — plain text, verse format

**Expected outputs:** `tests/fixtures/GROUND_TRUTH.json` — field-by-field expected values for all 13 fixtures.

## Carry-Forward Tasks (from Step 2)

1. **Confidence calibration analysis.** Extract confidence scores from Step 2 results (if they exist at `tests/results/phase1_*.json`, `phase2_*.json`). Check correlation with accuracy: if models produce > 0.90 confidence on wrong answers, raise thresholds. **DATA RISK:** Results files are gitignored. If not present, re-run `tests/test_llm_inference.py --phase 2` to regenerate ($2–5 API cost). If regeneration is not feasible, document that calibration was deferred and current thresholds (0.70/0.50) are maintained provisionally.

2. **Author-specific consensus complementarity check.** The consensus pair (Command A + Opus 4.6) was selected using a metric that treats all 7 fields equally. But consensus is only used for author identification and work matching. Before implementing consensus, re-run `tests/consensus_analysis.py` filtered to `author_identification` field only. If a different pair ranks higher, update the consensus pair in config. If results files don't exist, the check must be done with live API calls during this session.

## Build Steps

1. **Smoke test Instructor integration.** Before writing production code, verify that Instructor's `from_provider()` works with both consensus models:
   - `instructor.from_provider("openrouter/cohere/command-a")` with response_model
   - `instructor.from_provider("anthropic/claude-opus-4-6")` with response_model
   Send the inference_v1 prompt for fixture 01 and verify JSON parse + enum validation. Budget: ~$0.10.

2. **Implement `metadata_inference.py`.** Core inference flow:
   - Build `messages` list from extractor output + inference_v1 template (SYSTEM_MESSAGE + filled USER_MESSAGE_TEMPLATE)
   - Also build `simplified_messages` (same but with library context — scholar/work lists — removed from user message)
   - Call LLM via consensus `evaluate()` with `response_model=InferenceOutput` (Pydantic model matching §4.A.4 schema)
   - One consensus call, three local comparisons on the same response pair (author ID, work matching, attribution_status)
   - Map response to SourceMetadata fields (§4.A.4 field name mapping)
   - Apply biographical inference cap (0.85) to author confidence
   - Apply attribution status caps (disputed → 0.70, unknown → 0.0)
   - Construct `confidence_scores: InferredFieldConfidence`
   - Construct `needs_review_fields` (fields with confidence < 0.70)
   - Set `text_fidelity` deterministically from format + quality issues (NOT from LLM)

3. **Implement `shared/consensus/src/consensus.py`.** Replace the tracer stub:
   - `evaluate()` takes `messages: list[dict]` (NOT a prompt string) plus `simplified_messages` for retry
   - Dispatches both model calls concurrently via `asyncio.gather()`
   - Each model call: `instructor.from_provider(model_config["provider_model"], async_client=True)`
   - Per-model retry (2 retries: fresh request, then simplified_messages)
   - Timeout: 60s via `asyncio.wait_for()`
   - Fallback swap (Command A fails → GPT-5.4)
   - Returns `ConsensusResult` with full typed model responses

4. **Implement `engines/source/src/consensus.py`.** Source-engine integration:
   - Author identification agreement function (§6.1 rules): receives two InferenceOutput Pydantic objects
   - Work matching agreement function (§6.2 rules): runs locally on the same response pair
   - Directed attribution_status comparison (§6.3 — conservative value wins): runs locally
   - Wire to metadata_inference.py: one consensus call → three comparisons

5. **Copy name matching to production location.** Move from eval_harness to `shared/scholar_authority/src/name_matching.py`.

6. **Run carry-forward tasks.** Confidence calibration + author-specific complementarity.

## Done When

- [ ] Instructor smoke test passes for both consensus models
- [ ] `metadata_inference.py` produces valid SourceMetadata fields for fixtures 01, 06, 11
- [ ] LLM output field mapping correct: `layers` → `text_layers`, `author_identification` → `ScholarReference`
- [ ] Confidence scores populate `InferredFieldConfidence` correctly
- [ ] Attribution status caps applied: disputed → 0.70, unknown → 0.0
- [ ] `text_fidelity` set deterministically (not from LLM)
- [ ] Consensus `evaluate()` dispatches both models concurrently and compares
- [ ] Author identification agreement function works (name similarity ≥ 0.90 + death date ±10)
- [ ] Directed attribution_status comparison implemented (conservative value wins)
- [ ] Consensus failure handling: author ID → human gate, work matching → provisional
- [ ] Name matching functions in production location (`shared/scholar_authority/src/name_matching.py`)
- [ ] Confidence calibration analysis complete (or documented as deferred with rationale)
- [ ] Author-specific consensus complementarity verified (or pair updated)
- [ ] Tests pass for all implemented functionality
