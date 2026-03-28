# NEXT — Full 5-Book LLM Integration Run + Post-Run Review

## Current Position

- **Baseline:** 737 tests passing, 2 skipped, 0 failed
- **Commit:** `94972b74` (master HEAD after pre-flight hardening)
- **Engine:** Excerpting
- **Milestone:** Pre-flight gate PASSED. All prompts hardened, all blocking bugs fixed. Ready for full integration run.

## What Just Happened (Pre-Flight Hardening Session)

9 findings identified during pre-flight review. 8 fixed, 1 accepted (no checkpoint/resume — mitigated by per-package isolation):

1. **source_school key mismatch** — FIXED. Batch script used `"school"` but engine reads `"source_school"`. Taysir's Hanbali school was invisible to enrichment/consensus.
2. **Verifier prompt too thin** — FIXED. Enhanced from 2 sentences to full methodology with C-SC-1–5 criteria, voice markers, school attribution guidance.
3. **Response log truncation** — FIXED. Increased from 2000→50000 chars (response) and 500→2000 chars (request).
4. **ENRICH_MAX_TOKENS overflow** — FIXED. 23 chunks would have exceeded 16384 token budget. Added dynamic scaling (≤1500 words→16384, >1500→32768).
5. **Tarjīḥ orphaning risk** — FIXED. Added DP bullet: verdict phrases (والصواب, الراجح, الأصح) must stay with alternatives.
6. **Non-إلا qualifier splitting** — FIXED. Added DP bullet: لكن, غير أن, إلا أن qualifiers must stay with qualified statement.
7. **Epithet coverage gap** — FIXED. Added guidance for شيخ الإسلام, الحافظ, القاضي, الشيخان, متفق عليه, collectives. 48% of taysir chunks contain شيخ الإسلام.
8. **"Best guess" instruction** — FIXED. Changed to conservatism rule: prefer null with conf<0.3 over wrong attribution.
9. **Q&A reinforcement** — FIXED. Added DP bullet reinforcing Q&A grouping for dense objection cycles.

**Sources:** CC investigation (findings 1-3), architect analysis (finding 4), ChatGPT 5.4 deep research (findings 5-9, validated against codebase and test data).

## Task 1: Execute the Full Integration Run

### Run Command

```bash
cd /path/to/kr
export OPENROUTER_API_KEY=sk-or-v1-...
python scripts/run_full_integration.py
```

### Expected Parameters

| Parameter | Value |
|-----------|-------|
| Total chunks | 308 |
| Packages | 5 (ibn_aqil_v1, ibn_aqil_v3, taysir, ext_39_masala, ext_46_qa) |
| Estimated time | 8–12 hours |
| Estimated cost | $97–112 (OpenRouter credits) |
| LLM calls | ~1200–1400 (with retries) |
| Primary model | anthropic/claude-opus-4.6 ($5/$25 per 1M tokens) |
| Verify model | openai/gpt-5.4 ($2.50/$15 per 1M tokens) |
| Escalation model | mistralai/mistral-large-2411 (~$2/$6 per 1M tokens) |
| Output directory | integration_tests/full_run_{date}/ |

### Monitoring During Run

- The batch script prints per-package progress (1/5, 2/5, etc.)
- Taysir (package 3/5) takes ~6–7 hours — the longest by far (184 chunks)
- Within a package, progress is logged to stderr (Phase 2a/2b/3 per chunk)
- If a package fails, the script continues to the next one
- SUMMARY.json is written at the end with per-package stats

### Known Risks

- 5 chunks >4000 words (untested range) — warnings logged, 32768 token budget should suffice
- 17 chunks have ⌜⌝ footnote markers in first 50 chars — may cause EX-C-003 snippet-not-found
- ibn_aqil_v1 is densest (64.3% chunks above 1500-word threshold)

## Task 2: Post-Run Review (next session)

Follow `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` — Phase C.

### Session Start

1. Clone/pull repo
2. Read this NEXT.md
3. Read SUMMARY.json from the run output
4. Read the protocol: `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`
5. `ls /mnt/skills/user/` — use kr-evaluate + critical-review

### Review Sequence

**Step 1: Structural Integrity (C.1)** — automated checks, all 5 packages:
- Pipeline completion (any crashes?)
- Excerpt count sanity (expected: ~800–1500 total)
- Offset alignment (V-P3-2)
- Field completeness
- Error code audit
- Gate queue consistency

**Step 2: Per-Excerpt Review (C.2)** — manual, exhaustive for first 3 packages:
- Boundary quality (DP-1 through DP-9)
- Classification quality
- Attribution quality (especially epithet resolution with new conservatism rule)
- Enrichment quality (topic, school, takhrij, terminology)
- Self-containment assessment accuracy

**Step 3: Findings Taxonomy (Phase D)** — categorize every finding:
- CRITICAL: Wrong belief in owner's mind
- HIGH: Systematic quality gap
- MEDIUM: Isolated inaccuracy
- LOW: Suboptimal but not wrong

### Expected Outcomes

This is Round 1 — the first full run. Expect findings. The goal is not zero-defect output; it's discovering the failure modes that unit tests couldn't catch and fixing them before Round 2.

## Do NOT Do

- Do NOT run the batch script in Claude Code — it takes 8–12 hours and must run locally
- Do NOT modify prompts, code, or SPEC during the run — the run must match the committed code
- Do NOT skip the post-run structural integrity checks — they catch crashes the summary misses
