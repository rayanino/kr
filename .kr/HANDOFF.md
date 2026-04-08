> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff — Autonomous System v1

## Session purpose
Complete the autonomous system's 3 missing data bridges and prepare v1 documentation for Codex continuation.

## What this session completed

### 3 Data Bridges (codex_kb_bridge.py)
All three wired into `ingest_codex_results()` so they run automatically:

1. **Creative -> Ideas bridge**: Scans `results/creative-*/creative.json`, creates `Idea` records in `knowledge_base/ideas.jsonl`. Dedup by idea_id. No creative results exist yet (bridge is ready, waiting for creative tasks to run).

2. **Gap Scanner -> Research Gaps bridge**: Greps SPEC files for `[OPEN:]` markers + parses `KNOWN_LIMITATIONS.md` for L-NNN entries. Creates `ResearchGap` records in `knowledge_base/research_gaps.jsonl`. **13 gaps created** on first run (all from normalization + excerpting_eval KNOWN_LIMITATIONS).

3. **Findings -> Backlog promotion bridge**: Reads CONFIRMED HIGH/CRITICAL findings with non-empty `action_required`. Auto-promotes to `overnight_codex/backlog.json` using existing backlog format. **0 promoted yet** because all 126 HIGH/CRITICAL findings are stuck at PRELIMINARY (verification bottleneck — see below).

### v1 Documentation
- `overnight_codex/README.md` — comprehensive v1 README (architecture, components, data layout, operating model, known issues)
- `docs/autonomous-system/SYSTEM_MAP.md` — updated with bridges + new KB data paths
- `docs/autonomous-system/QUICKSTART.md` — updated KB state + bridge documentation

### Pyright clean
`codex_kb_bridge.py` passes pyright with 0 errors.

## Known Issue: Verification Bottleneck

**All 126 HIGH/CRITICAL findings are PRELIMINARY.** The verification pipeline (`_run_cli_verify` in `codex_kb_bridge.py`) tries:
1. `claude --bare --model sonnet --max-budget-usd 0.05` — fails with "Not logged in" (subprocess doesn't inherit auth)
2. `gemini -p` — not found on PATH

**Impact:** Bridge 3 (findings -> backlog) has no input because nothing is CONFIRMED.

**Fix options (for Codex to implement):**
- Set `ANTHROPIC_API_KEY` environment variable so `claude --bare` works in subprocess mode
- Install and configure `gemini` CLI so it's on PATH
- Or: add a direct API-based verifier that uses the Anthropic Python SDK instead of subprocess CLI invocation

## Current state

| Metric | Value |
|--------|-------|
| KB findings | 244 (126 HIGH/CRITICAL PRELIMINARY) |
| Research gaps | 13 |
| Contradictions | 47 |
| Backlog items | 5 |
| Creative templates | 3 |
| Total autonomous code | ~9,000 lines / 16 Python files |
| Dashboard pages | 7 (relay, findings, contradictions, ideas, gaps, digestion, status) |

## What Codex should do next

### Priority 1: Fix verification so Bridge 3 activates
The single biggest gap. 126 findings are waiting. Options:
- Add an API-based verifier in `codex_kb_bridge.py` that calls Anthropic/OpenRouter directly instead of subprocess
- Or configure env vars for CLI auth

### Priority 2: Schedule creative tasks
No `creative-*` results exist yet. The task generator needs to schedule creative template tasks so Bridge 1 produces ideas. Check `overnight_codex_task_generator.py` for creative task scheduling logic.

### Priority 3: Add a `/gaps` route to the dashboard
`store.py` already has `load_research_gaps()` and `get_gaps_stats()`. But there's no `/gaps` route in `app.py` or `gaps.html` template. Wire it up — should be ~30 lines following the `ideas` page pattern.

### Priority 4: Run overnight with all bridges active
Once verification works, run `python scripts/launch_autonomous.py --hours 8` and verify the full loop: tasks -> results -> findings -> verification -> backlog promotion -> next tasks.

## Files modified this session

- `scripts/codex_kb_bridge.py` — 3 bridges + wiring + updated CLI output
- `overnight_codex/README.md` — comprehensive v1 rewrite
- `docs/autonomous-system/SYSTEM_MAP.md` — bridges + new data paths
- `docs/autonomous-system/QUICKSTART.md` — current state + bridge docs
- `.kr/HANDOFF.md` — this file

## Resume point

Codex should start with Priority 1 (fix verification). Read `codex_kb_bridge.py` lines 230-330 for the verification pipeline, then either add API-based verification or fix CLI auth.
