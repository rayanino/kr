# Codex CLI — Structural Feasibility Review of DESIGN.md

**Reviewer:** CC Agent (Codex-style structural review)
**Date:** 2026-04-07
**Verdict:** FEASIBLE_WITH_CHANGES

## Top 5 Recommendations (Priority Order)

1. **Move persistence from `.kr/autonomous/` to `overnight_codex/autonomous/`** — `.kr/` is in FORBIDDEN_EDIT_PREFIXES (common.py line 60). Any Codex task writing DR data will be blocked.

2. **Split DR relay engine into two decoupled processes:** (a) prompt generation scanner for task generator (sync, produces artifacts), (b) separate response ingestion script triggered by owner (`python scripts/process_dr_response.py <path>`). Orchestrator's synchronous loop can't handle async human relay.

3. **Define JSONL record schemas** for every knowledge_base file — without formal contracts, 3 months of autonomous operation produces unusable schema drift.

4. **Add concrete exit criteria for Phase 5** — currently 4-week bucket with no measurable milestones.

5. **Address ACTIVE_AUTHORITY.md interaction** — current state is `active_authority: claude`, which forces `queue_only` mode. System won't function without authority change or branch-aware bypass.

## Additional Findings

- relay_queue/ directory model needs atomic state (use state.json, not directory moves)
- Phase 1 underestimated: 3-4 weeks needed, not 2
- Phase 4 cascades if Phase 1 slips
- No circuit breaker for DR relay stalls (what if owner stops relaying for a week?)
- No cost/quota model for DR response processing LLM calls
- No WSL/Windows interaction model for dashboard
- No worktree cleanup strategy for 83-day runs
- Missing creative_run_log equivalent for DR prompt deduplication
- Doctrine conflict: MORNING_REPORT.md (push) vs dashboard (pull) — reconcile explicitly
- Queue-only constraints not applied to new DR/dashboard components
