---
description: Dashboard for the excerpting hardening operation. Shows current phase (0-3), questionnaire status, smoke run results, campaign baseline, budget, and coworker dispatch count.
allowed-tools: Bash(ls:*), Bash(find:*), Bash(wc:*), Bash(cat:*), Bash(grep:*), Bash(python3:*), Read, Glob, Grep
---
Show a compact dashboard of the excerpting hardening operation status. Do ALL of these:

1. **Determine current phase** based on directory existence:
   - Phase 0 (Q&A): `integration_tests/questionnaire/` exists but no `COMPLETE` marker
   - Phase 1 (Smoke): `integration_tests/smoke_api_v2/` has excerpt data
   - Phase 2 (Hardening): smoke_api_v2 analyzed, iterating on fixes
   - Phase 3 (Full Run): `integration_tests/v2_final/` exists
   - If none: "Phase 0 not started"

2. **Questionnaire status**: Does `integration_tests/questionnaire/QUESTIONNAIRE_TEMPLATE.md` exist? Is it filled in?

3. **Smoke run status**: Count files in `integration_tests/smoke_api_v2/`. Count excerpts (grep for excerpt entries in any .jsonl files).

4. **Campaign baseline**: Count excerpts at `integration_tests/campaign_20260331/` (should be 2,303).

5. **Budget**: Read `tests/results/source_engine/COST_LOG.json` and report EUR spent / EUR 100 limit.

6. **Coworker dispatches**: Count lines in `.kr/runtime/dispatch_log.jsonl` if it exists.

7. **Analysis teams**: Check if any team reports exist (A-F from NEXT.md).

8. **Engine test status**: `python -m pytest engines/excerpting/tests/ -q --tb=no 2>&1 | tail -1`

Format as a compact ASCII table:
```
╔══════════════════════════════════════════════════╗
║  EXCERPTING HARDENING STATUS                     ║
╠══════════════════════════════════════════════════╣
║  Phase:        [0/1/2/3] — [description]         ║
║  Q&A:          [not started / in progress / done] ║
║  Smoke Run:    [N excerpts / not run]             ║
║  Baseline:     2,303 excerpts (campaign)          ║
║  Budget:       EUR X.XX / 100.00 (Y% used)        ║
║  Dispatches:   N coworker dispatches logged        ║
║  Teams:        [A B C D E F] — status each         ║
║  Tests:        N pass, M fail                      ║
╚══════════════════════════════════════════════════╝
```
