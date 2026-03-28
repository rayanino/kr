# NEXT — Timeout Fix + 5-Book Overnight Run Preparation

## Current Position

- **Baseline:** 800 tests passing, 2 skipped (766 excerpting + 34 adapter)
- **Commit:** `602964d8` (encoding fix) — HEAD is `87c2809b` (this NEXT.md)
- **Engine:** Excerpting — CLI adapter WORKING
- **Milestone:** First real CLI integration test succeeded: 23 excerpts, 0 errors, $0 cost (شرح ابن عقيل, 2 chunks)
- **Blocking issue:** Large chunks (4,936 words) timeout at 120s — must fix before 5-book run

## What Just Happened

The CLI adapter was implemented, reviewed (3-pass + CC concurrent), and fixed through 3 rounds:
1. **4 SPEC divergences** fixed (envelope extraction, extract_json return type, missing WARNING log, empty system prompt)
2. **Windows encoding** fixed (subprocess.run needs `encoding="utf-8"` — cp1252 crashes on Arabic)
3. **First real test** succeeded: 23 excerpts from شرح ابن عقيل at $0

The envelope extraction was CRITICAL — without it, 100% of Claude CLI calls fail. The encoding fix was equally critical on Windows. Both were invisible to mocked unit tests.

## What to Do (in order)

### Step 1: ChatGPT Deep Research — 5-Book Run Risk Analysis (MANDATORY)

**Before doing anything else**, send this to ChatGPT 5.4 (deep research mode):

> You have access to the GitHub repo rayanino/kr. I need a comprehensive risk analysis for the upcoming 5-book overnight integration run (~308 chunks through the excerpting engine via CLI adapter).
>
> Read these files:
> - `shared/llm/cli_adapter.py` — the CLI adapter
> - `shared/llm/CLI_ADAPTER_SPEC.md` — the adapter SPEC
> - `engines/excerpting/contracts.py` — the response schemas
> - `scripts/run_full_integration.py` — the batch runner
> - `scripts/run_integration_test.py` — the per-package runner
> - `integration_tests/run_20260328_173009/` — the first successful run artifacts
>
> Questions:
> 1. **Timeout risk:** Phase 2a classification on a 4,936-word chunk timed out at 120s. What timeout value is safe for Opus on chunks up to 5,000 words? What's the right design — increase default, or make it chunk-size-adaptive?
> 2. **Retry storm risk:** With max_retries=2 at the adapter level AND retry logic in Phase 2/3 orchestrators, how many total CLI calls can a single failing chunk trigger? Map the full retry cascade. Is there a risk of 18+ minute burns on a single chunk?
> 3. **Codex verify calls:** The test used 2 chunks. The verify model is `openai/gpt-5.4` routed to `codex exec`. Has this path been tested end-to-end? What happens if Codex's output-schema enforcement rejects a response that Claude accepted?
> 4. **Gemini escalation calls:** The escalation model is `google/gemini-2.5-pro` routed to `gemini -p`. Has this path been tested? What's the escalation trigger condition?
> 5. **Error recovery:** If the pipeline fails mid-run (e.g., machine sleeps, network drops), can it resume from where it left off, or does it restart from scratch?
> 6. **Cost tracking:** The envelope gives us `total_cost_usd` per call. Are we extracting this anywhere? Should we track cumulative cost in the overnight run?
> 7. **What else could go wrong** in a 10-hour overnight run that the 4-minute test didn't exercise?
>
> Write an extensive report with specific recommendations for each risk.

Wait for ChatGPT's report before proceeding. Use it to inform Steps 2-3.

### Step 2: Timeout Fix (CC task, ~15 minutes)

Based on ChatGPT's analysis, write a NEXT.md for CC to fix the timeout. The likely fix is:

- Increase default timeout from 120s to 300s for Claude/Gemini backends
- Or make timeout proportional to chunk word count (e.g., 60s + 0.05s/word)
- Add a `--timeout` flag to the integration test scripts

This is a CC task — write the directive, relay to CC.

### Step 3: 5-Book Overnight Run Preparation

After the timeout fix lands:
1. Verify the 5 test packages exist at `experiments/format_diversity_test/packages/` (ibn_aqil_v1, ibn_aqil_v3, taysir, ext_39_masala, ext_46_qa — all verified 2026-03-28)
2. Prepare the exact `run_full_integration.py --backend cli` command
3. Prepare a monitoring checklist (what to check in the morning)
4. Write the command for the owner to run overnight

## Do NOT Do

- Do NOT skip the ChatGPT deep research step. It MUST happen before the overnight run.
- Do NOT start the 5-book run without fixing the timeout.
- Do NOT prepare the overnight run in the same chat where you fix the timeout — use a fresh chat if context degrades.
- Do NOT implement the timeout fix yourself — delegate to CC via NEXT.md.

## Key Files

| File | Purpose |
|------|---------|
| `shared/llm/cli_adapter.py` | The CLI adapter (699 lines, all 3 backends) |
| `shared/llm/CLI_ADAPTER_SPEC.md` | Governing SPEC (14 sections, 7 invariants) |
| `scripts/run_full_integration.py` | Batch runner for all 5 packages |
| `scripts/run_integration_test.py` | Per-package runner |
| `integration_tests/run_20260328_173009/` | First successful run artifacts (23 excerpts) |
| `reference/archive/sessions/reviews/review_cli_adapter.md` | Completed review checklist |

## After This

After the 5-book overnight run:
1. Evaluate results (invoke `kr-evaluate`)
2. Owner 30-book review gate — the NON-NEGOTIABLE human review of real Arabic output
3. If excerpting is proven → Taxonomy engine design begins
