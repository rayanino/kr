# Excerpting Evaluation Layer — Known Limitations

## L-001: chunk_id not available in raw LLM traces

**Status:** deferred
**Affects:** `scripts/excerpting_eval/ingest.py` (semantic phase inference), review packet chunk attribution
**Root cause:** The runner sets `semantic_phase` on trace context before each phase call, but `chunk_id` cannot be set from the runner because `run_phase2a` and `run_phase2b` iterate over chunks internally. The Instructor hook fires per-call, but the hook has no access to which chunk triggered the call.

**Current workaround:** The analyzer infers chunk association from call sequence ordering and request content similarity. This works for the current test data but is fragile if two chunks have identical text or if retry ordering changes.

**Fix required:** Thread a `trace_context` dict through `run_phase2a` → `classify_chunk` and `run_phase2b` → `group_chunk`, setting `trace_context["chunk_id"]` before each Instructor call. This touches:
- `engines/excerpting/src/phase2_classify.py` — `classify_chunk()` and `run_phase2a()`
- `engines/excerpting/src/phase2_group.py` — `group_chunk()` and `run_phase2b()`
- `scripts/run_integration_test.py` — pass trace contexts to phase functions

**When to fix:** Before the first campaign with >1 chunk per book processed (the current test data processes 1 chunk per book, so the limitation is dormant). Fix when scaling to full-book processing.

**Verification:** After fixing, raw trace request files should contain `"chunk_id": "div_src_..."` alongside the existing `"semantic_phase"` field. The analyzer in `ingest.py` should read `chunk_id` from the request JSON when present and skip sequence-based inference.
