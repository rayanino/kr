# Result Preservation Protocol — بروتوكول حفظ النتائج

**Status:** GOVERNING — applies to every validation phase and every future engine  
**Authority:** Owner directive, elevated to project-level rule  
**Date:** 2026-03-10

---

## The Rule

**Every API call, every test run, every pipeline execution produces persisted artifacts structured for maximum downstream reuse.** Results are not disposable validation waste. They are the first real outputs of the engine. A book successfully processed in Step 3 is a finished source engine product — later phases must not re-process it. A lesson learned in Phase A must be readable by any future agent in any future session.

This rule exists because:
- LLM API calls cost real money. Re-running the pipeline on books already processed is burning budget for zero new information.
- Every engine downstream of the source engine consumes source engine output. If we save structured results from validation phases, the normalization engine can begin development using real data from the source engine's validation runs — it does not need to wait for a separate "production run."
- Bugs found in one phase teach lessons that prevent wasted runs in the next phase. If those lessons aren't documented, the next session's agent will repeat the same mistakes.

**Violation of this rule** means: an API call was made whose output was not persisted, or was persisted in a format that requires re-running the call to extract the information downstream engines need. This is always wrong, regardless of phase or context.

---

## What "Save Everything" Means Concretely

### Layer 1: Raw Artifacts (never discard)

For every book processed through any pipeline step that involves an LLM call:

| Artifact | What | Why |
|----------|------|-----|
| Raw LLM responses | The exact JSON returned by each model (Opus 4.6, Command A, fallback) | Re-evaluate quality, debug hallucinations, calibrate prompts — without re-calling |
| Extraction intermediates | Full dict from `extract_metadata()` including `_` prefixed internal fields | Debug extraction bugs, compare extraction vs inference, normalization engine input |
| Full SourceMetadata | The complete Pydantic model output, not a summary | This IS the source engine product — downstream engines consume this directly |
| Confidence scores | Per-field confidence from each model, not just the consensus | Calibrate thresholds, identify which model is weak on which field |
| Consensus details | Which model said what, agreement/disagreement on each field | Debug consensus failures without re-running |
| Human gate checkpoints | Every gate triggered, with the diagnostic values that triggered it | Understand gate rate, calibrate thresholds |
| Hashes | Per-file SHA-256 and composite hash | Duplicate detection across phases without re-hashing |

### Layer 2: Aggregate Analysis (computed from Layer 1)

| Artifact | What | Why |
|----------|------|-----|
| Phase summary JSON | Counts, distributions, error rates, timing | Quick phase-level review |
| Field coverage report | Which metadata fields were present/absent across all books | Normalization engine knows what to expect |
| Error taxonomy | Every error code with affected books listed | Fix prioritization |
| Lessons learned | What bugs were found, what was fixed, what to watch for | Future agents read this before starting |
| Ground truth growth | Which books were owner-validated and added to GROUND_TRUTH.json | Regression testing across phases |

### Layer 3: Reusability Index (the key efficiency mechanism)

After each phase, produce a manifest listing every book processed, with:
- `book_name`: original filename/directory name
- `phase`: which phase produced this result (A, C, D)
- `pipeline_version`: git commit hash of the engine code that produced it
- `status`: success / error / gate_pending
- `needs_rerun`: boolean — set to true if a bug fix between phases invalidates this result
- `result_path`: path to the per-book JSON

**Later phases read this manifest.** For each book to be processed:
1. If the book has `status: success` and `needs_rerun: false` from a prior phase → **skip it**. The result is already a finished product.
2. If `needs_rerun: true` → re-process with the fixed pipeline.
3. If no prior result exists → process for the first time.

This means each phase's cost is only: `(new_books + rerun_books) × cost_per_book`.

---

## Per-Phase Result Structure

All results go to `tests/results/source_engine/{phase_name}/`.

### Phase A (Step 2) — Extraction only, €0

```
tests/results/source_engine/phase_a/
  PHASE_A_SUMMARY.json          # Aggregate statistics
  PHASE_A_LESSONS.md            # Bugs found, patterns observed
  {book_name}.json              # Per-book extraction + hashes
```

Per-book JSON contains: `extracted_metadata` (full dict), `file_hashes`, `composite_hash`, `quality_issues`, `source_format`. No LLM fields.

**Downstream value:** The normalization engine can read these to understand field distributions across 2,519 books. Phase C's pipeline can optionally read extraction results instead of re-parsing HTML (though extraction is cheap enough that re-parsing is acceptable).

### Phase C (Step 3) — 73 books with LLM, €10–15

```
tests/results/source_engine/phase_c/
  PHASE_C_SUMMARY.json          # Aggregate statistics
  PHASE_C_LESSONS.md            # Bugs found, LLM quality patterns
  PHASE_C_MANIFEST.json         # Reusability index for all 73 books
  {book_name}/
    result.json                 # Full pipeline output (SourceMetadata-compatible)
    extraction.json             # Raw extraction result (same as Phase A format)
    llm_responses/
      opus_4_6.json             # Raw Opus 4.6 response
      command_a.json            # Raw Command A response
      fallback.json             # Fallback model response (if triggered)
    consensus.json              # Per-field consensus details
    ground_truth_comparison.json # Comparison with owner validation
```

**Downstream value:** These 73 books are FINISHED source engine products. Step 4 includes them as regression checks (skipping re-processing unless `needs_rerun` is set). The normalization engine can start development against these 73 real results immediately.

### Phase D (Step 4) — ~200 books with LLM, €20–30

Same structure as Phase C, in `phase_d/`. The manifest covers all ~200 books. Phase C's 73 books are included as regression checks (re-run and compared, but their results were already saved).

**This is the final validation step for the source engine.** After Step 4 results are verified:
- The source engine is validated — proven correct and reliable on ~273 diverse books across two independent runs.
- A `tests/results/source_engine/MASTER_MANIFEST.json` maps every processed book to its result, regardless of which phase produced it.
- The verified results become the normalization engine's development input. The normalization engine builds and tests against real source engine output — not synthetic data, not a separate "production run."
- The source engine code is ready to process any Shamela book reliably. Actual library population happens later, after all 7 engines are proven end-to-end.

---

## Lessons Learned Format

Each `PHASE_X_LESSONS.md` follows this structure:

```markdown
# Phase X Lessons Learned

## Bugs Found
- **[BUG-001] Description**: What happened, which books affected, fix commit
- **[BUG-002] Description**: ...

## Patterns Observed
- Pattern: description of a recurring behavior across multiple books
- Implication: what this means for downstream engines

## What Went Wrong
- Anything that wasted time, money, or produced misleading results

## What Worked
- Approaches or tools that performed better than expected

## Recommendations for Next Phase
- Specific things the next session's agent should do differently

## Impact on Downstream Engines
- What the normalization engine needs to know from these results
- Field distributions, quality patterns, structural variants discovered
```

**This is not optional.** Every phase produces a lessons document. The agent running the next phase reads it before starting. This is how institutional memory works across sessions.

---

## Bug Fix Invalidation Protocol

When a bug is found between phases:

1. **Assess scope:** Which books could the bug have affected? Not all bugs affect all books — a regex fix for a rare metadata label might only affect 20 books.
2. **Mark affected results:** Set `needs_rerun: true` in the manifest for affected books only.
3. **Document in lessons:** Record the bug, the fix commit, and the list of affected books.
4. **Next phase re-processes:** Only the affected books, not the entire phase.

This prevents the wasteful pattern of "found 1 bug, re-run 150 books."

---

## Applying This to Future Engines

This protocol is not source-engine-specific. When the normalization engine begins validation:

1. Its test results are structured for the passaging engine to consume.
2. Its targeted testing results are reusable by its final validation run.
3. Its lessons learned are readable by the next engine's first session.

The chain is: **Source → Normalization → Passaging → ... → Synthesis**. Each engine's test results feed the next engine's development. No engine starts from scratch when real data from the previous engine already exists.

---

## Retroactive Note on Step 0

Step 0 (13-fixture integration) was run before this protocol existed. Its results in `tests/results/source_engine/session6/` save only summaries — not raw LLM responses, not full SourceMetadata output. Those 13 books will be re-processed in Phase C (they're included in the 73-book set), so this is not a critical loss. But it illustrates why this protocol exists: €1.80 of API calls produced results we can't fully reuse.
