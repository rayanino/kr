# Architect Audit — Cross-Provider Pre-Overnight-Run Review

**Date:** 2026-03-28
**Auditor:** Claude Chat (Architect)
**Scope:** Excerpting engine readiness for 280-chunk overnight integration run
**Commit:** 7cf348d5 (HEAD)

---

## Methodology

Read the following files in full (no truncation):
- `shared/llm/cli_adapter.py` (699 lines)
- `scripts/run_full_integration.py` (376 lines)
- `scripts/run_integration_test.py` (1039 lines)
- `engines/excerpting/src/phase2_classify.py` (479 lines)
- `engines/excerpting/src/phase2_group.py` (390 lines, grep-verified)
- `engines/excerpting/src/phase3_orchestrator.py` (192 lines)
- `engines/excerpting/src/phase3_enrichment.py` (522 lines)
- `engines/excerpting/src/phase3_consensus.py` (878 lines)
- `engines/excerpting/contracts.py` — ExcerptingConfig (lines 737-770)
- `integration_tests/run_20260328_173009/` — all artifacts from first successful run

Cross-referenced: ExcerptingConfig defaults, PROVIDER_MAP routing, retry parameters at both adapter and phase levels, all raw LLM request/response logs from the first run.

---

## Findings

### F-1: CODEX VERIFY PATH IS BROKEN (HIGH)

**Evidence:**
- `integration_tests/run_20260328_173009/raw_llm_requests/`: 6 verify request files exist (verify_0001 through verify_0006)
- `integration_tests/run_20260328_173009/raw_llm_responses/`: 0 verify response files exist
- All 23 excerpts in `excerpts.jsonl` have `review_flags: ["verification_skipped"]`
- Verify requests use `model: "openai/gpt-5.4"` which routes to `codex` backend via `_PROVIDER_MAP`

**Impact:** The cross-model consensus verification (§7.3) is completely non-functional. Every excerpt produced by the overnight run will have `verification_skipped`. This means:
- No cross-model quality validation on school attribution, author attribution, or self-containment
- No human gate entries will be generated from consensus disagreements
- Enrichment output goes through without independent challenge

**Severity assessment:** HIGH for production quality, but NOT BLOCKING for the first overnight run. Rationale:
- The overnight run's primary goal is to validate the full pipeline at scale
- Excerpts are still produced with deterministic + enrichment metadata — only the verification layer is missing
- The owner's 30-book review gate (NON-NEGOTIABLE) will catch quality issues regardless
- Fixing Codex CLI integration mid-audit introduces risk of new bugs

**Recommendation:** Run overnight WITHOUT fixing this. Track `verification_skipped` in the morning assessment. Fix Codex path before the second run. If Codex CLI is fundamentally unavailable on Windows, consider routing verify through Gemini CLI instead.

### F-2: RETRY CASCADE — 2+ HOURS PER PATHOLOGICAL CHUNK (HIGH AWARENESS)

**Full retry map for a single consistently-failing chunk:**

| Phase | Phase-level retries | Adapter-level retries per attempt | Total CLI invocations | Time at 300s each |
|-------|-------|-------|-------|-------|
| 2a (classify) | 3 | 3 | 9 | 45 min |
| 2b (group) | 3 | 3 | 9 | 45 min |
| 3 (enrich) | 3 | 3 | 9 | 45 min |
| 3 (verify) | 3 | 3 | 9 | 45 min (but currently broken) |
| 3 (escalate) | 1 | 3 | 3 | 15 min |
| **Total** | | | **39** | **~3.25 hours** |

**Evidence:**
- Phase 2a `run_phase2a`: `max_attempts = 1 + config.RETRY_COUNT` = 3 (line 372)
- Phase 2b `run_phase2b`: same pattern (line 289)
- Phase 3 enrichment `run_phase3_enrichment`: same (line 454)
- Phase 3 consensus `run_consensus`: same (line 758)
- All `create()` calls pass `max_retries=2` to the adapter (lines 347, 182, 270, 211, 462)
- Adapter retry loop at line 306: `for attempt in range(max_retries + 1)` = 3

**Mitigating factors:**
- Failed chunks are excluded from downstream phases (not run-killing)
- In practice, most chunks will succeed on first attempt (first test: 2 chunks, 0 retries)
- Exponential backoff exists (`time.sleep(2**attempt)`)

**Recommendation:** No code change. Monitor retry patterns in logs. If >5 chunks hit max retries on Phase 2a, abort and investigate. Add retry tracking to morning checklist.

### F-3: NO RESUME CAPABILITY WITHIN A PACKAGE (MEDIUM)

**Evidence:**
- `run_integration_test.py` processes chunks sequentially in a single run
- No checkpoint file is written after each chunk
- A crash at chunk 150/184 (Taysir) loses all in-progress work for that package

**Mitigating factors:**
- Per-PACKAGE isolation exists: `run_full_integration.py` writes each package's results independently
- Packages 1-4 survive if package 5 crashes
- Package ordering is: ibn_aqil_v1, ibn_aqil_v3, taysir, ext_39_masala, ext_46_qa
- Taysir (66% of workload) is package 3. If it crashes, packages 1-2 are saved.

**Recommendation:** Accept for first run. If Taysir fails mid-run, we still have ibn_aqil results to evaluate. Add checkpointing before second run.

### F-4: GEMINI ESCALATION PATH UNREACHABLE (MEDIUM)

**Evidence:**
- Escalation triggers ONLY when enrichment and verification disagree on a decision
- Verification is currently broken (F-1)
- With verification_skipped on all excerpts, the consensus resolution code (phase3_consensus.py line 847: `resolve_consensus`) never runs
- Therefore `escalation_client.chat.completions.create()` (line 462) is never reached

**Impact:** The entire 3-model escalation path is dead code during this run. No Gemini CLI calls will be made.

**Recommendation:** Not a problem for the first run. Both Codex and Gemini paths need end-to-end testing before the second run.

### F-5: COST TRACKING INOPERATIVE ON CLI BACKEND (LOW)

**Evidence:**
- `CLIResponse` always creates empty `_CLIUsage()` (cli_adapter.py line 342-346)
- Claude CLI JSON envelope contains `"usage"` and `"total_cost_usd"` fields, but the adapter doesn't extract them
- `read_package_results` in run_full_integration.py looks for `usage.cost` in response logs — will always find 0

**Impact:** Cost column in the summary will show €0.0000. Correct for Max plan but uninformative for future OpenRouter fallback.

**Recommendation:** Accept. Fix when implementing cost tracking.

### F-6: TIMEOUT NOT THREADED FROM CONFIG TO ADAPTER (LOW)

**Evidence:**
- `ExcerptingConfig.TIMEOUT_SECONDS = 300` (contracts.py line 754)
- No phase function passes `timeout` as a kwarg to `create()`
- Adapter defaults independently: `kwargs.get("timeout", 300)` (cli_adapter.py line 262)
- Values match by coincidence, not by wiring

**Impact:** If someone changes `ExcerptingConfig.TIMEOUT_SECONDS`, the adapter won't notice. No impact now.

**Recommendation:** Note for future. Config is cosmetically correct but not actually wired.

### F-7: SPEC TIMEOUT VALUES ALREADY UPDATED (RESOLVED)

**Evidence:** Commit 7cf348d5 updated:
- `CLI_ADAPTER_SPEC.md`: 120→300 (lines 444, 446)
- `SPEC.md`: 120→300, range 30–300→30–600 (line 2049)
- `run_full_integration.py`: per_package_timeout 7200→28800 (line 150, 329)

---

## Overnight Run Time Estimate

Based on first test data (2 chunks, 262s total):
- Per-chunk: ~46s (Phase 2a) + ~42s (Phase 2b) + ~43s (Phase 3) ≈ **131s/chunk**
- 280 chunks × 131s ≈ **36,680s ≈ 10.2 hours**
- Large chunks (26 × >2500 words) will take longer — estimate +30% = ~40-50s extra each
- **Realistic estimate: 10-12 hours**

Package-level breakdown:
| Package | Est. chunks | Est. time |
|---------|-------------|-----------|
| ibn_aqil_v1 | ~30 | ~1.1h |
| ibn_aqil_v3 | ~25 | ~0.9h |
| taysir | ~184 | ~6.7h |
| ext_39_masala | ~20 | ~0.7h |
| ext_46_qa | ~21 | ~0.8h |
| **Total** | **~280** | **~10.2h** |

---

## Overall Assessment

**GO for overnight run** with the following conditions:
1. Acknowledge that verification is skipped (F-1) — acceptable for first run
2. Monitor retry patterns in morning (F-2)
3. Run --max-chunks 2 smoke test on ALL 5 packages first (10-minute validation)
4. Check machine sleep settings (Windows must not sleep)

---

## Morning Checklist

After the overnight run completes, check:

1. **Did it finish?** Check SUMMARY.json exists and all 5 packages have results
2. **Package status:** How many succeeded vs failed?
3. **Excerpt count:** Total excerpts across all packages (expect 2000-3000)
4. **Error count:** Total errors. Check processing_log.jsonl for each package
5. **verification_skipped rate:** Expected 100% (Codex path broken). Confirm.
6. **Retry patterns:** Grep logs for "attempt 2/3" and "attempt 3/3". Count how many chunks needed retries.
7. **Large chunk behavior:** Did any chunks timeout at 300s? Grep for "timeout" in logs.
8. **Phase timing:** Check timing.json per package. Any phase taking >2x expected?
9. **Output quality spot-check:** Open excerpts.jsonl for ibn_aqil_v1. Read 3 Arabic excerpts. Do they look like coherent teaching units?
10. **Disk space:** How large is the output directory? (expect 50-200MB with all artifacts)
