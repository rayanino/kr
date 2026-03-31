# Excerpting Evaluation Layer — Known Limitations

## L-001: chunk_id not available in raw LLM traces

**Status:** fixed (2026-03-31)
**Affects:** `scripts/excerpting_eval/ingest.py` (semantic phase inference), review packet chunk attribution

**Resolution:** Threaded `trace_context` dict through `run_phase2a()` and `run_phase2b()` as an optional parameter. Each function sets `trace_context["chunk_id"]` before each Instructor call and resets to `None` after the loop. The runner passes `trace_contexts.get("enrich")` to both calls. The ingest module reads `chunk_id` from request JSON when present; for pre-fix run directories, chunk_id is `None` (semantic phase inference is unaffected).

**Files changed:**
- `engines/excerpting/src/phase2_classify.py` — `run_phase2a()` accepts `trace_context`
- `engines/excerpting/src/phase2_group.py` — `run_phase2b()` accepts `trace_context`
- `scripts/run_integration_test.py` — passes trace context to phase functions
- `scripts/excerpting_eval/models.py` — `LLMTraceEntry.chunk_id` field added
- `scripts/excerpting_eval/ingest.py` — reads `chunk_id` from request JSON
- `scripts/excerpting_eval/analysis.py` — limitation string updated

**Verification:** Raw trace request files now contain `"chunk_id": "div_src_..."` alongside `"semantic_phase"`. Regression tests in `test_phase2_classify.py` and `test_phase2_group.py` verify chunk_id is set during LLM calls and reset after.
