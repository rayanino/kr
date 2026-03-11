---
globs: ["scripts/run_phase_*.py", "engines/*/src/**/*.py", "shared/*/src/**/*.py"]
---
- Every LLM API call MUST persist its full output to `tests/results/source_engine/{phase}/`. Never discard raw responses.
- Before making an API call, check PHASE_X_MANIFEST.json for existing results. If `needs_rerun: false`, SKIP the call and reuse existing output.
- Per-book result structure: result.json, extraction.json, llm_responses/{model}.json, consensus.json, sanity_checks.json.
- After each phase run: produce PHASE_X_SUMMARY.json, PHASE_X_MANIFEST.json, PHASE_X_LESSONS.md.
- Bug fixes between phases: set `needs_rerun: true` ONLY for affected books — never blanket re-run all books.
- Update `tests/results/source_engine/COST_LOG.json` after every script that makes API calls.
