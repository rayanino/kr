# ChatGPT 5.4 Deep Research Prompt — Cross-Provider Audit

**Fire this immediately. It takes 15-30 minutes to complete.**

---

You have access to the GitHub repo `rayanino/kr` (public). This is a personal Islamic scholarly study companion that processes classical Arabic texts into structured excerpts. I need you to conduct a **comprehensive pre-overnight-run audit** of the excerpting engine.

## Context

We're about to run a 10-hour overnight batch that processes 280 Arabic text chunks through a 3-phase LLM pipeline:
- Phase 1: Deterministic text assembly (no LLM calls)
- Phase 2a: LLM-based segment classification (1 call per chunk)
- Phase 2b: LLM-based teaching unit grouping (1 call per chunk)
- Phase 3: LLM enrichment + cross-model consensus verification

The pipeline uses **CLI backends** — subprocess calls to `claude`, `codex`, and `gemini` CLI tools instead of API calls. The adapter is at `shared/llm/cli_adapter.py`.

A first integration test (2 chunks, ibn_aqil package) succeeded: 23 excerpts, 0 errors, $0 cost. But we've identified several concerns that need independent review.

## Files to Read (in priority order)

1. `shared/llm/cli_adapter.py` — The CLI adapter (699 lines). Focus on retry logic, error handling, timeout behavior, and the three backend invocation methods (_invoke_claude, _invoke_codex, _invoke_gemini).

2. `scripts/run_full_integration.py` — Batch runner for 5 packages. Focus on the sequential execution model, per-package timeout handling, and error aggregation.

3. `scripts/run_integration_test.py` — Per-package runner (~1040 lines). Focus on: how clients are created (lines 506-548), Phase 2a/2b/3 error handling, the --max-chunks flag, and artifact serialization.

4. `engines/excerpting/src/phase2_classify.py` — Phase 2a. Focus on the retry loop at line 378 (phase-level retries AROUND adapter-level retries).

5. `engines/excerpting/src/phase3_orchestrator.py` — Phase 3 orchestrator (192 lines). Focus on graceful degradation for enrichment and consensus failures.

6. `engines/excerpting/src/phase3_consensus.py` — Consensus verification. Focus on `run_consensus` (line 696+) and the `_needs_consensus` trigger logic.

7. `engines/excerpting/src/phase3_enrichment.py` — Enrichment. Focus on `run_phase3_enrichment` (line 412+) and its retry loop.

8. `engines/excerpting/contracts.py` — `ExcerptingConfig` at line 737. Check the default model routing and timeout values.

9. `shared/llm/CLI_ADAPTER_SPEC.md` — Governing SPEC for the adapter.

10. `integration_tests/run_20260328_173009/` — First successful run artifacts. Check the excerpts.jsonl (all have `verification_skipped`), timing.json, and raw_llm_requests/verify_*.json (6 requests with 0 responses).

## Specific Questions

### Q1: Retry Cascade — Map the full worst case

The adapter has `max_retries=2` (3 attempts). Phase 2a and 2b ALSO have `max_attempts = 1 + config.RETRY_COUNT = 3` (phase-level retry loops). Phase 3 enrichment and consensus have the same pattern.

**Map the complete retry cascade for a single chunk that consistently fails.** How many total CLI subprocess invocations? How many seconds worst case at 300s timeout each? Is there any interaction between the two retry levels that makes behavior unpredictable?

### Q2: Codex Verify Path — Why did it fail?

The first test logged 6 verify requests (`raw_llm_requests/verify_*.json`) using model `openai/gpt-5.4` (routes to `codex` backend) but logged 0 verify responses. All 23 excerpts have `verification_skipped` flag.

**Trace the failure path.** Is `codex exec` likely to be available on a Windows 11 machine? Does the Codex CLI support `--output-schema` for structured JSON? Could the subprocess call be failing because of a missing tool, wrong command syntax, or output format mismatch?

### Q3: Gemini Escalation — Has it been tested?

Escalation model is `google/gemini-2.5-pro` (overridden from `mistralai/mistral-large-2411` for CLI backend in `run_integration_test.py` line 503). Escalation triggers only when enrichment and verification disagree.

**Can escalation even trigger if verification is broken?** If all verify calls fail, does the escalation path ever execute? What happens to the consensus decisions?

### Q4: Large Chunk Risk — 26 chunks >2500 words

The 5 packages contain 26 chunks with >2500 words (max 4,936 words). The previous timeout was 120s (caused at least 1 timeout). Now 300s.

**Is 300s enough for Opus on a 5000-word Arabic text?** Consider: the system prompt includes the full JSON schema, the user prompt includes the full text, and the model must produce structured JSON output. Estimate the expected latency based on token counts.

### Q5: Error Isolation Completeness

If Phase 2a classification fails for chunk 150 of 184 (in the Taysir package), what happens? Walk through the code path. Does the run continue to chunk 151? Does Phase 2b process the remaining chunks? Does Phase 3 still run on the chunks that succeeded?

### Q6: Resume and Recovery

If the Windows machine sleeps, the network drops, or Python crashes at chunk 150:
- Can we resume from chunk 150?
- Are chunks 1-149's results preserved?
- For the batch runner (run_full_integration.py), if Package 3 (taysir) crashes, are Packages 1-2 results preserved?

### Q7: What Else Could Go Wrong?

The first test ran for 4.4 minutes on 2 chunks. The overnight run will be 280 chunks over ~10 hours. What failure modes exist at scale that the 2-chunk test didn't exercise?

Think about: memory accumulation, file descriptor leaks, Windows-specific issues (CRLF, code page, sleep behavior), rate limiting, token window overflow for large chunks, prompt template edge cases with unusual Arabic content.

## Deliverable

Write an extensive report with:
1. Each question answered with specific code references
2. A severity classification for each finding (BLOCKING / HIGH / MEDIUM / LOW)
3. Specific fix recommendations where applicable
4. An overall GO / NO-GO recommendation for the overnight run
5. A monitoring checklist — what to check in the morning to assess run health

Be specific. Reference file names, line numbers, function names. Don't be generic.
