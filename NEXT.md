# NEXT SESSION

## Context
Repo audit completed (2026-03-08): 6 obsolete protocol files archived, all stale
references fixed across CLAUDE.md, orient.py, .claude/commands, .claude/settings.json,
shared/CLAUDE.md, CONTEXT_BUDGET.md, and quality scripts. Root is now clean: only
active governance files remain.

Autonomy analysis completed: ~70% of owner responsibilities can be delegated to LLM.
Tracer bullet (Step 0) requires zero domain knowledge and is fully autonomous.

## What the Owner Should Do Now

1. **Setup** — follow OPEN_PROBLEMS.md §1 (enable capabilities, upload 6 skill zips,
   create source engine project, create .env with API keys from project knowledge files)
2. **Start tracer bullet** — in the source engine project:
   "We need to run Step 0 from ENGINE_PROTOCOL.md — the tracer bullet. Reconcile the
   existing 7 contracts.py files against each other, stub the 4 shared components
   (consensus, human_gate, scholar_authority, validation), build rough engine stubs,
   create scripts/run_pipeline.py, and run html_export_minimal through the full pipeline."
3. Claude reconciles contracts, stubs shared components, builds engine stubs, runs fixture
4. Boundary issues documented in `reference/TRACER_FINDINGS.md`
5. Then source engine Step 1 → Step 4 per ENGINE_PROTOCOL.md

## MINOR Audit Findings (pending owner approval)
These were identified but not implemented. Say "implement minor fixes" to apply them:
- M1: CONTEXT_BUDGET.md line counts already updated (done in audit)
- M2: Engine CLAUDE.md files reference old artifacts (IMPLEMENTATION_ORDER.md, TEST_PLAN.md,
  HARDENING_RESULTS.md). Propose: add deprecation notes or remove old-protocol references.
- M3: Missing __init__.py in 9 test/src directories. Propose: create empty files.
- M4: Pre-existing engine stubs (2,242 lines across 4 engines) written to full SPECs,
  not core-only. Tracer bullet should use them as starting points but expect drift.
- M5: Empty normalizers __init__.py. Low priority.
