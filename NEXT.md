# NEXT SESSION

## Context
Full meta-audit completed (2026-03-08): Applied kr-integrity lenses, 7 silent failure
patterns, 7 knowledge integrity threats, and the Perfection Standard to the project's own
governance structure. Found and fixed: 10 HIGH-severity defects in ENGINE_PROTOCOL.md,
7 stale engine CLAUDE.md files, gold baseline timing impossibility, missing failure states,
missing cross-references between documents, 20+ stale/archived files.

The repo is now clean. Every active file references the correct protocol. Every engine
CLAUDE.md accurately describes current state. ENGINE_PROTOCOL.md has defined failure
states, concrete SPEC depth criteria, per-task accuracy thresholds, and implementation
guidance for the tracer bullet.

## What the Owner Should Do Now

1. **Setup** — follow OPEN_PROBLEMS.md §1:
   - Enable Code execution in Settings > Capabilities
   - Upload 6 skill zips from skills/ to Customize > Skills > Toggle ON
   - Create .env file from .env.template with API keys
   - Create source engine project using skills/engine-project-template/source.md

2. **Start tracer bullet** — in the source engine project, say:
   "We need to run Step 0 from ENGINE_PROTOCOL.md — the tracer bullet.
   Reconcile the existing 7 contracts.py files, stub the 4 shared components,
   build rough engine stubs with a process() entry point each, create
   scripts/run_pipeline.py, and run html_export_minimal through the full pipeline."

3. After tracer bullet → source engine Steps 1-4 per ENGINE_PROTOCOL.md

## Key Files (read these to orient)
- `OPEN_PROBLEMS.md` — roadmap and status
- `skills/shared/ENGINE_PROTOCOL.md` — the development process
- `reference/TESTING_FRAMEWORK.md` — test architecture
- `STEERING.md` — project overview
