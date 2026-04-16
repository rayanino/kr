> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Current session purpose
Source engine build is active. Resume from the DR-1 dispatch in flight on 2026-04-16. The stop-hook quality gate loop is closed (115/115 tests pass, pyright clean, tree clean, remote current through `173ddec82`).

## Current state
- Active frontier: source engine build (see `.kr/ACTIVE.md` and `NEXT.md`)
- DR-1 in flight: level detection (OQ-SRC-0001 + DEC-SRC-0003), relayed to ChatGPT DR + Claude DR
- DR-2 queued but deferred until DR-1 returns (monitor placement may depend on DR-1 recommendation)
- Repo pollution cleanup in progress: MCP planning docs removed, Context7 plugin duplicate disabled; session-snapshot handoffs to be removed next
- Excerpting frozen at Session 22 checkpoint (1008 pass / 0 fail / 4 xfail, EUR 36.70 / 100.00)

## Current resume point
1. Check for DR-1 results. When they arrive, synthesize findings into a SPEC amendment for `DEC-SRC-0003` (chosen option + rationale) and resolve `OQ-SRC-0001` (open → answered).
2. After DR-1 closes, draft DR-2 (OQ-SRC-0005 agent monitoring scope) via `/prompt-architect` informed by DR-1 outcome.
3. Continue source engine build; do not resume excerpting work until source engine Phase 5 readiness is reached.

## Suggested branch discipline
- Continue direct commits to `main` per `ACTIVE_AUTHORITY.md` shared-authority model.
- Excerpting work would resume on the frozen `excerpting-foundations-hardening-20260404` branch if reactivated.

## Historical note
Archived hardening/handoff context lives in `reference/archive/handoffs/` and `reference/archive/sessions/`. Do not create new handoff snapshot files at the repo top level — per Rule 17 (no-repo-pollution), handoff state lives here in `.kr/HANDOFF.md` (short, current) or in the agent's memory system, not as disposable snapshot docs.
