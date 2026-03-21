# NEXT — Weekend Task 4: Source Engine LLM Edge-Case Probes

## Current Position

- **Phase:** Source engine hardening — extending ground truth
- **Mode:** AUTONOMOUS LLM VALIDATION — architect unavailable
- **Previous:** Tasks 1-3 complete. Sweeps done, bugs fixed, calibration report produced.
- **Purpose:** Run 30 edge-case books through the full source engine pipeline with LLM inference. Extend ground truth beyond the 204 Phase D books.

## Rules for This Session

1. **You MAY run LLM API calls.** Budget: €15 maximum (~€0.10/book × 30 books + margin). Track actual spend.
2. **Follow RESULT_PRESERVATION.md strictly.** Every API call persists full structured output. Raw LLM responses saved per-model. No unsaved calls.
3. **Do NOT modify engine source code.** If a bug causes a book to fail, log it and continue. Do not fix it.
4. **Do NOT modify SPECs or contracts.**
5. **Use the source engine's existing pipeline** — `engines/source/src/engine.py` or the equivalent run script.
6. **Commit results to `tests/results/source_engine/phase_e/`** following the Phase D structure.

## API Configuration

```python
# Anthropic (primary — Claude Opus 4.6)
# Key: Read from /path/to/project/anthropic_api_key or environment variable

# OpenRouter (secondary — Command A, GPT-5.4 fallback)
# Key: Read from /path/to/project/openrouter_api_key or environment variable

# Use the same consensus pair as Phase D:
# Primary: Claude Opus 4.6 (Anthropic direct)
# Secondary: Command A (via OpenRouter)
# Fallback: GPT-5.4 (via OpenRouter)
```

Check the existing config in `engines/source/src/config.py` for model IDs and routing.

## What to Do

### Step 1: Select 30 Books

Select books from `shamela-export-samples/` using these criteria. Use the Task 1 sweep results (`results/source_sweep/PHASE_A_SUMMARY.json` or per-book JSONs) and normalization sweep results to identify candidates.

**Selection criteria (aim for exactly 30 books):**

| Category | Count | Selection Method |
|----------|-------|-----------------|
| Source extraction anomalies | 8 | Books where source sweep succeeded but had unusual extraction: missing author_name_raw, missing title_full, unusual card format, many extra_card_fields |
| Genre diversity gaps | 8 | Books from Shamela categories NOT well-represented in Phase D's 204 books. Check Phase D category distribution in `PHASE_D_SUMMARY.json` |
| Multi-layer candidates | 5 | Books that auto-upgraded to multi-layer in the normalization sweep (from CALIBRATION_REPORT.md section B.2 top list) |
| Extreme metrics | 5 | Largest books (most pages), smallest non-trivial books (3-10 pages), highest diacritic density |
| Previously unknown | 4 | Books with names/titles that don't appear in Phase D results at all |

**Important:** Do NOT select books that CRASHED in the source sweep (format detection failed). Those can't go through LLM inference because extraction didn't produce output.

Write the selection with rationale in `tests/results/source_engine/phase_e/PHASE_E_SELECTION.md`.

### Step 2: Run the Pipeline

For each selected book, run the full source engine pipeline:

```python
# Use the same entry point as Phase D
# Each book produces:
#   result.json — full SourceMetadata
#   extraction.json — raw extraction
#   llm_responses/opus_4_6.json — raw Opus response
#   llm_responses/command_a.json — raw Command A response
#   llm_responses/fallback.json — fallback response (if triggered)
#   consensus.json — per-field consensus details
#   prompt_sent.json — the exact prompt sent
```

Structure:
```
tests/results/source_engine/phase_e/
  PHASE_E_SELECTION.md
  PHASE_E_MANIFEST.json
  PHASE_E_SUMMARY.json
  PHASE_E_LESSONS.md
  {book_name}/
    result.json
    extraction.json
    consensus.json
    prompt_sent.json
    llm_responses/
      opus_4_6.json
      command_a.json
      fallback.json  (only if triggered)
```

If a book fails (gate_abort, error), still save all available artifacts. Record the failure in the manifest.

### Step 3: Track Budget

Maintain a running cost tracker:
```
tests/results/source_engine/phase_e/COST_LOG.json
{
  "books_processed": N,
  "total_cost_eur": X.XX,
  "per_book_avg": X.XX,
  "by_model": {
    "opus_4_6": {"calls": N, "tokens_in": N, "tokens_out": N, "cost_eur": X.XX},
    "command_a": {"calls": N, "tokens_in": N, "tokens_out": N, "cost_eur": X.XX},
    "fallback": {"calls": N, "tokens_in": N, "tokens_out": N, "cost_eur": X.XX}
  }
}
```

**STOP if total cost exceeds €15.** Process as many books as the budget allows, prioritizing the first categories in the selection table.

### Step 4: Write PHASE_E_LESSONS.md

Follow the same format as `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md`:
- Results summary (success rate, gate_abort rate, error rate)
- Patterns observed (new extraction patterns, inference quality, consensus disagreements)
- What worked / what to watch
- Field stability notes
- New findings not seen in Phase D

### Step 5: Build Manifest

Create `PHASE_E_MANIFEST.json`:
```json
{
  "phase": "E",
  "date": "2026-03-22",
  "pipeline_version": "<current commit hash>",
  "total_books": 30,
  "books": {
    "book_name": {
      "status": "success|gate_abort|error",
      "needs_rerun": false,
      "result_path": "tests/results/source_engine/phase_e/book_name/result.json",
      "selection_category": "genre_diversity|multi_layer|..."
    }
  }
}
```

### Step 6: Commit

```bash
# Check size first — raw LLM responses can be large
du -sh tests/results/source_engine/phase_e/

# If under 50MB total, commit everything
git add tests/results/source_engine/phase_e/
git commit -m "validate: Phase E — 30 edge-case LLM probes (€X.XX spent)"

# If over 50MB, commit only manifests, summaries, and lessons
# Keep raw LLM responses local
git add tests/results/source_engine/phase_e/PHASE_E_*.md
git add tests/results/source_engine/phase_e/PHASE_E_*.json
git add tests/results/source_engine/phase_e/COST_LOG.json
git commit -m "validate: Phase E summaries — 30 edge-case probes (€X.XX, raw responses local)"
```

## Read First

1. This file (NEXT.md)
2. `RESULT_PRESERVATION.md` — the preservation protocol (NON-NEGOTIABLE)
3. `engines/source/src/config.py` — API keys, model IDs, routing
4. `tests/results/source_engine/phase_d/PHASE_D_LESSONS.md` — what Phase D learned
5. `tests/results/source_engine/phase_d/PHASE_D_SUMMARY.json` — Phase D category distribution
6. `results/CALIBRATION_REPORT.md` — sweep baselines (for book selection)
7. `engines/source/src/engine.py` — the pipeline entry point

## Do NOT Do

1. **Do NOT modify engine source code.** Log bugs, don't fix them.
2. **Do NOT modify SPECs or contracts.**
3. **Do NOT exceed €15 in API spend.** Stop processing and commit what you have.
4. **Do NOT re-process books already in Phase D.** Check MASTER_MANIFEST.json.
5. **Do NOT discard any LLM response.** Every call is persisted per RESULT_PRESERVATION.md.

## Verification

- [ ] PHASE_E_SELECTION.md documents the 30 books with selection rationale
- [ ] PHASE_E_MANIFEST.json has entries for all processed books
- [ ] PHASE_E_SUMMARY.json has aggregate statistics
- [ ] PHASE_E_LESSONS.md follows Phase D format
- [ ] COST_LOG.json tracks actual spend (must be ≤€15)
- [ ] Every processed book has result.json + extraction.json + consensus.json + raw LLM responses
- [ ] No engine source code modified
- [ ] No books from Phase D re-processed (check against MASTER_MANIFEST.json)
