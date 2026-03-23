# NEXT — Excerpting Engine Session 2: Phase 2 (LLM Classification + Grouping)

## Current Position

- **Excerpting Phase 1:** ACCEPTED (commit `28a188ad`), all errata resolved
- **HEAD:** `83ea23ef` on `master`
- **Test baseline:** 77 passed (excerpting), 503 passed (normalization)
- **Open SPEC errata:** None (SPEC-NOTE-4–7 all resolved)
- **Phase 1 output:** `run_phase1()` produces `list[AssembledChunk]` with validated coverage, offsets, and layer attribution

## What to Do

Implement Phase 2: LLM Teaching Unit Extraction (SPEC §5). This fills the stubs in `phase2_classify.py` and `phase2_group.py`. Phase 2 is the engine's inference core — the only phase that calls an LLM.

**Processing flow (§5.1):**
1. Phase 2a — Segment Classification: LLM classifies chunk text into `ClassifiedSegment` objects
2. Offset Normalization: Remap LLM word offsets to canonical tokenization using `text_snippet` anchors
3. Coverage Verification — Segments: Verify invariants I-CS-1 through I-CS-6
4. Phase 2b — Teaching Unit Grouping: LLM groups segments into `TeachingUnit` objects
5. Coverage Verification — Units: Verify invariants I-TU-1 through I-TU-9

Steps 1–3 must succeed before step 4. Failed chunks are flagged and excluded.

## Context

Phase 2 is LLM-driven, so testing is fundamentally different from Phase 1. The architecture was validated experimentally: the experiment in `experiments/architecture_test/run_tests.py` tested Approach B (classify-then-group) on 23 divisions across 7 genres with real LLM calls. All 23 passed. The SPEC prompts (§5.2.2, §5.3.2) are production-adapted versions of the experiment prompts.

**The hardest algorithm is offset normalization (§5.4.1).** The LLM produces internally consistent word offsets but using its own tokenization (which differs from Python's `text.split()` by ~14.5%). The normalization uses `text_snippet` fields as alignment anchors to remap to canonical offsets. This algorithm is fully deterministic and thoroughly testable without LLM calls.

## Owner Action Needed

None. This is a pure implementation session.

## Read First

| File | Lines | What |
|------|-------|------|
| `engines/excerpting/SPEC.md` | §5 (785–1226) | **Governing spec for Phase 2.** Read ALL of §5. |
| `engines/excerpting/SPEC.md` | §2.3.3 (196–223) | ClassifiedSegment contract + invariants I-CS-1–6 |
| `engines/excerpting/SPEC.md` | §2.3.4 (225–251) | TeachingUnit contract + invariants I-TU-1–9 |
| `engines/excerpting/SPEC.md` | §6.1 (1237–1259) | Decontextualization Prevention rules DP-1–6 |
| `engines/excerpting/contracts.py` | 359–427 | ClassifiedSegment, TeachingUnit models |
| `engines/excerpting/contracts.py` | 634–647 | ClassificationResult, ExtractionResult LLM response schemas |
| `engines/excerpting/contracts.py` | 726–759 | ExcerptingConfig (Phase 2 parameters) |
| `engines/excerpting/contracts.py` | 860–1033 | validate_cs_invariants (860), validate_tu_invariants (919) — already implemented |
| `engines/excerpting/src/phase2_classify.py` | all | Stubs to fill (5 functions) |
| `engines/excerpting/src/phase2_group.py` | all | Stubs to fill (3 functions) |
| `engines/excerpting/tests/conftest.py` | all | Existing factory helpers |
| `experiments/architecture_test/run_tests.py` | 109–135 | Experiment prompts (APPROACH_B_CLASSIFY_SYSTEM, APPROACH_B_GROUP_SYSTEM) |
| `experiments/architecture_test/run_tests.py` | 157–171 | Instructor + OpenRouter client setup pattern |

## What to Build

### Module 1: `phase2_classify.py` — Classification + Offset Normalization (§5.2, §5.4.1–2)

**Function 1: `classify_chunk(chunk, client, config) → ClassificationResult`**
- Construct system prompt from §5.2.2 (SPEC lines 825–856). The prompt text is a constant string with one format variable: `{structural_format}`. Copy the SPEC prompt VERBATIM — do not rewrite or "improve" it.
- Construct user message from §5.2.3 (SPEC lines 870–878): `<text>\n{assembled_text}\n</text>`
- Call LLM via `client.chat.completions.create()` with `response_model=ClassificationResult`, model from `config.CLASSIFY_MODEL`, temperature from `config.LLM_TEMPERATURE`, max_tokens from `_compute_classify_max_tokens(chunk.word_count)`, `max_retries=0` (DD-S2-8: all retries handled in outer loop).
- Return the raw ClassificationResult (offsets are in LLM tokenization, not canonical yet).

**Function 2: `normalize_offsets(segments, assembled_text, total_tokens) → list[ClassifiedSegment]`**
This is the most complex function. Implements §5.4.1 exactly:

Step 1 — Build token-to-character mapping:
- `tokens = assembled_text.split()` → canonical tokenization
- For each token, record its character start position in the original string. Build a list `token_char_starts` where `token_char_starts[i]` is the character index where token `i` starts.

Step 2 — Anchor each segment using text_snippet:
For each segment in order (by segment_index):
- (a) Take `segment.text_snippet` (first 50 chars of segment text, as copied by LLM)
- (b) Search for snippet in `assembled_text` starting from `search_start_char`
- (c) If found at `match_char`: find the token whose character range contains `match_char` → that's the segment's canonical `start_word`. Update `search_start_char = match_char + 1`.
- (d) If exact match fails: try whitespace-normalized matching (collapse whitespace runs to single space in both snippet and search region). If this succeeds, map the match position back to the original text's character position.
- (d2) If whitespace match fails: try diacritic-stripped matching (strip U+064B–U+0652, U+0670 from both). If this succeeds, emit warning `EX-A-012`. Map match position back to original text.
- (e) If all three matching attempts fail: raise ValueError (caller handles retry).

**Critical implementation detail for fallback matching:** When matching in normalized/stripped space, you must map the match position back to the original text's character position. Build a mapping array during normalization: for each position in the normalized string, store the corresponding position in the original string. Use this to convert `normalized_match_pos → original_char_pos → token_index`.

Step 3 — Infer boundaries from contiguity:
- `segment[0].start_word` = its anchor position (must be 0 — validated in step 4)
- For each consecutive pair: `segment[i].end_word = segment[i+1].start_word - 1`
- `segment[-1].end_word = total_tokens - 1`

Return a NEW list of ClassifiedSegment objects with canonical offsets. Do not mutate the originals.

**Function 3: `verify_segments(segments, total_tokens) → None`**
Thin wrapper around `validate_cs_invariants()` from contracts.py. Raises ValueError on any fatal violation.

**Function 4: `_compute_classify_max_tokens(word_count) → int`**
From §5.5.1:
- `word_count <= 2000` → 8192
- `word_count > 2000` → 32768
- `word_count > 4000` → 32768 (provisional; log a warning that this threshold is untested)

**Function 5: `run_phase2a(chunks, client, config) → dict[str, list[ClassifiedSegment]]`**
Orchestrator: for each chunk, classify → normalize → verify, with retry logic per §5.5.2:
- Up to 2 retries (3 total attempts) per chunk, controlled by `config.RETRY_COUNT`
- On offset normalization failure: retry the classify call with error feedback appended to user message: `"\n\nNote: The previous classification produced a text_snippet that could not be located in the source text. Ensure each text_snippet is copied exactly from the input."`
- On coverage verification failure: retry with message describing which invariant failed
- On API error: exponential backoff (2^attempt seconds)
- After all retries exhausted: flag with appropriate error code (EX-C-001, EX-C-003, EX-C-004), log diagnostic info (chunk_id, error code, assembled_text length, raw LLM response), exclude chunk from result
- Return: `dict[chunk_id → list[ClassifiedSegment]]` for chunks that succeeded. Failed chunks are absent (logged, not silently dropped).

### Module 2: `phase2_group.py` — Teaching Unit Grouping (§5.3, §5.4.3)

**Function 1: `group_chunk(chunk, segments, client, config) → ExtractionResult`**
- Construct system prompt from §5.3.2 (SPEC lines 920–993). Copy verbatim with `{structural_format}` format variable.
- Construct user message from §5.3.3 (SPEC lines 1011–1021): text wrapped in `<text>` tags + segment summary in `<classified_segments>` tags. The segment summary uses POST-NORMALIZATION offsets and snippets. Format each segment as: `Segment {segment_index}: words {start_word}–{end_word}, function={scholarly_function.value}, snippet="{text_snippet}"`
- Call LLM via `client.chat.completions.create()` with `response_model=ExtractionResult`, max_tokens from `config.GROUP_MAX_TOKENS`.

**Function 2: `verify_units(units, segments, total_tokens) → list[TeachingUnit]`**
This is NOT just a thin wrapper — it does auto-repairs before calling `validate_tu_invariants`:
- **V-P2-14 auto-derivation:** For each unit, DERIVE `start_word` from `segments[unit.segment_indices[0]].start_word` and `end_word` from `segments[unit.segment_indices[-1]].end_word`. If the LLM's values differ, log the discrepancy as a warning but ALWAYS use the derived values. Replace in the unit before validation.
- **V-P2-15 auto-repair:** If `self_containment == FULL` and `self_containment_notes` is not None, set notes to None. If `self_containment` is PARTIAL/DEPENDENT and notes is missing/empty, set to `"No notes provided"`. Log both as warnings.
- After auto-repairs, delegate to `validate_tu_invariants()`. Raises ValueError on any fatal violation.
- Return the (possibly repaired) list of TeachingUnit objects.

**Function 3: `run_phase2b(chunks, classified, client, config) → dict[str, list[TeachingUnit]]`**
Orchestrator: for each chunk_id in `classified` dict, group → verify, with retry logic:
- Same retry policy as Phase 2a (config.RETRY_COUNT retries)
- On unit coverage failure: retry Phase 2b only (reuse existing classification)
- On API error: exponential backoff
- After retries exhausted: flag with EX-C-002 or EX-C-005
- Return: `dict[chunk_id → list[TeachingUnit]]`

### Module 3: Tests

**File: `tests/test_phase2_normalize.py`** — Offset normalization tests (pure algorithm, no LLM):
- Happy path: 3 segments with findable snippets → correct canonical offsets
- Whitespace fallback: snippet with collapsed whitespace → still anchors correctly
- Diacritic fallback: snippet missing a diacritic → anchors with EX-A-012 warning
- Duplicate snippet: two identical substrings → left-to-right search picks correct one
- Snippet not found: snippet absent → raises ValueError
- Single segment: one segment covering all text
- First segment not at position 0: snippet anchors to non-zero → should still produce start_word=0 if that's where it matches, or fail V-P2-3 if it doesn't
- Token-to-char mapping edge cases: ZWNJ characters, multiple consecutive spaces
- Target: ≥10 test functions

**File: `tests/test_phase2_classify.py`** — Classification LLM call + retry tests:
- Prompt construction: verify system prompt text, user message format, MAX_TOKENS
- Mock client returns valid ClassificationResult → verify flow
- Mock raises on first call, succeeds on second → retry works
- Mock raises on all attempts → correct error code flagged
- Coverage verification failure → retry with error feedback
- _compute_classify_max_tokens: parametrized (500→8192, 2000→8192, 2001→32768, 4001→32768)
- Target: ≥10 test functions

**File: `tests/test_phase2_group.py`** — Grouping LLM call + verify_units tests:
- Prompt construction: verify segment summary format
- Mock client returns valid ExtractionResult → verify flow
- V-P2-14: LLM produces wrong word offsets → verify derivation from segments
- V-P2-15: FULL with notes → notes set to None; PARTIAL without notes → fallback string
- Retry on grouping failure
- Target: ≥10 test functions

**File: `tests/test_phase2_integration.py`** — Real LLM integration tests (gated):
- `@pytest.mark.skipif(not os.environ.get("OPENROUTER_API_KEY"), reason="No API key")`
- Classify small Arabic text (~100 words), verify offset normalization produces valid canonical segments
- Classify + group small text, verify teaching units pass all invariants
- Target: 2 test functions

**Conftest additions:**
```python
def _make_mock_instructor_client(return_value=None, side_effect=None):
    """Returns a MagicMock configured as an instructor client."""
    ...

def _make_classification_result(assembled_text, n_segments=3):
    """Build ClassificationResult with N segments having valid snippets from text."""
    ...
```

**Expected total: 77 + ≥36 = ≥113 passed tests.**

## Design Decisions (Pre-Resolved)

**DD-S2-1: Prompt text is SPEC-owned, not CC-owned.**
The system prompts in §5.2.2 and §5.3.2 are copied as string constants (with `{structural_format}` as the only format variable). CC does NOT rewrite, condense, or "improve" prompt text. If a prompt issue is found during testing, it is escalated to the architect.

**DD-S2-2: LLM client creation is the caller's responsibility.**
Functions accept `client: instructor.Instructor` as a parameter. Client creation pattern (from experiment code):
```python
import instructor, openai
client = instructor.from_openai(
    openai.OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    ),
    mode=instructor.Mode.JSON,
)
```

**DD-S2-3: Offset normalization returns NEW objects, does not mutate.**
`normalize_offsets()` creates new `ClassifiedSegment` objects with canonical offsets. The originals are not modified.

**DD-S2-4: verify_units does auto-repairs BEFORE delegating to validate_tu_invariants.**
V-P2-14 (derive word ranges) and V-P2-15 (fix notes consistency) are repairs. The function modifies TeachingUnit objects, then validates. Returns the repaired list.

**DD-S2-5: Retry error feedback goes in user message, not system prompt.**
When retrying after offset normalization or coverage failure, append the error feedback to the user message (after the text block). The system prompt stays constant across retries.

**DD-S2-6: Telemetry via standard logging.**
Each LLM call logs (per §5.5.4): source_id, chunk_id, call_type, latency, retry_count, success/failure. Use `logging.getLogger(__name__)` at INFO level.

**DD-S2-7: Mock testing strategy.**
Tests mock `client.chat.completions.create` directly. The mock returns pre-built Pydantic model instances. Integration tests with real LLM are gated behind `OPENROUTER_API_KEY`.

**DD-S2-8: Retry architecture — single outer loop, no instructor automatic retries.**
Set `max_retries=0` in the `client.chat.completions.create()` call to disable Instructor's automatic schema validation retries. ALL retries (schema failure, offset normalization failure, coverage failure, API error) are handled in the outer loop in `run_phase2a`/`run_phase2b`. This gives precise control over the total attempt count: exactly `1 + config.RETRY_COUNT` attempts per chunk (3 total with default RETRY_COUNT=2). If instructor raises a validation error, catch it and retry just like any other failure. The error message from the validation error is useful for logging but NOT appended to the next attempt's prompt (schema errors are structural, not content-related — the LLM needs a fresh attempt, not error feedback).

## Do NOT Do

1. **Do NOT modify prompt text.** Prompts in §5.2.2 and §5.3.2 are architect-designed.
2. **Do NOT implement Phase 3** (enrichment, consensus, deterministic fields).
3. **Do NOT modify `contracts.py`** unless you find a bug.
4. **Do NOT modify `phase1_assembly.py`**. Phase 1 is frozen.
5. **Do NOT use direct Anthropic/OpenAI API.** ALL LLM calls go through OpenRouter via the passed-in client.
6. **Do NOT call the real LLM in unit tests.** Mock the instructor client.
7. **Do NOT invent error codes.** Use only codes from `ExcerptingErrorCodes`.
8. **Do NOT implement `pipeline.py` or `load_config()`**.

## Verification

1. `python -m pytest engines/excerpting/tests/ -v --tb=short` → **≥113 passed** (77 + ≥36 new), 0 failed
2. `grep -r "raise NotImplementedError" engines/excerpting/src/phase2_classify.py engines/excerpting/src/phase2_group.py` → empty output
3. Offset normalization has ≥8 test functions (verify: `grep -c "def test_" engines/excerpting/tests/test_phase2_normalize.py`)
4. Retry logic has ≥5 test functions across classify and group test files
5. System prompt constants match SPEC §5.2.2 and §5.3.2 text (spot-check first 100 chars)
6. `grep -r "import anthropic" engines/excerpting/src/` → empty (no direct API imports)
7. All new test files import factory helpers from conftest (no duplicate factories)
8. `pip install instructor openai --break-system-packages` before running tests (add to requirements if not present)

## After This

Session 3 will implement Phase 3 (deterministic fields + LLM enrichment + consensus verification). That is the final implementation session before integration testing.
