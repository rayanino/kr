# NEXT — First Real LLM Evaluation Call (Excerpting Engine)

## Current Position

- **Baseline:** 595 tests passing, 2 skipped, 0 failed
- **Commit:** `e8f32250` (master HEAD)
- **Engine:** Excerpting
- **Phase:** First real LLM integration test
- **Budget:** ~EUR 63 remaining of EUR 100

## What Happened

All three critical bugs are fixed and reviewed:
1. Preamble gap fix (commit `1705ca5a`)
2. compute_page_range crash fix (commit `a5a148f5`, reviewed `5c29d708`)
3. EX-V-002 false positive fix (commit `8e5fb12b`)

Environment overhaul Sessions 1 & 2 committed (`c3655d22`, `56088fb6`). Session 3/4 items captured in `SESSION_3_4_BACKLOG.md`.

## What To Do

Run the first real LLM call on the excerpting engine. This is the single highest-value action for pipeline progress.

### Step 1: Pre-flight check

Dispatch the `evaluation-prep` agent for excerpting, or manually verify:
- Tests pass: `python -m pytest engines/excerpting/tests/ -x -q`
- No uncommitted engine changes: `git status --short`
- API key set: `echo $OPENROUTER_API_KEY | head -c 10` (should show prefix)
- Packages exist: `ls experiments/format_diversity_test/packages/`

### Step 2: Smoke test (1 chunk, real LLM)

```bash
PYTHONPATH=. python scripts/run_integration_test.py \
  --real \
  --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 \
  --max-chunks 1 \
  --output-dir integration_tests/smoke_001
```

Goal: Does OpenRouter connect? Does the model respond? Does Instructor parsing work? Does output validate? Cost: ~EUR 0.10-0.30.

### Step 3: Full run on ibn_aqil_v1

If smoke passes, remove `--max-chunks 1`:

```bash
PYTHONPATH=. python scripts/run_integration_test.py \
  --real \
  --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 \
  --output-dir integration_tests/run_001
```

### Step 4: Review results

Follow `engines/excerpting/docs/LLM_INTEGRATION_TEST_PROTOCOL.md` Phase C:
- C.1: Structural checks (automated)
- C.2: Scholarly checks (manual per-excerpt review, stratified sampling)
- C.3: Attribution checks

### Step 5: Expand to more packages

Run 2-3 more packages for format diversity:
- `taysir` (hadith-heavy, longest text)
- `ext_39_masala` (fiqh format)
- `ext_46_qa` (Q&A structure)

## Read First

| # | File | What |
|---|------|------|
| 1 | `engines/excerpting/CLAUDE.md` | Engine state and architecture |
| 2 | `engines/excerpting/docs/LLM_INTEGRATION_TEST_PROTOCOL.md` | Evaluation protocol |
| 3 | `engines/excerpting/docs/llm_trustworthiness_defenses.md` | Known LLM failure modes |
| 4 | `scripts/run_integration_test.py` | The integration test runner |
| 5 | `SESSION_3_4_BACKLOG.md` | Deferred environment items with trigger conditions |

## Do NOT Do

- Do NOT implement Session 3/4 environment items before the first LLM call — they need real data to calibrate.
- Do NOT run all 5 packages at once — start with 1, verify, then expand.
- Do NOT skip the manual review phase (C.2) — Round 1 needs exhaustive review.

## After This

Document findings. Check SESSION_3_4_BACKLOG.md trigger conditions against actual results. Implement what the data says is needed.
