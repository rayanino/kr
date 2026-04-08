> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Current session purpose
Pause excerpting engine builds at the Session 22 checkpoint and redirect the next serious sessions to repo cleanup plus owner-facing visual representations.

## Current state
- Active frontier now lives in `.kr/ACTIVE.md`
- Exact excerpting freeze state is recorded in `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`
- The owner may continue reviewing Session 22 excerpts; review collection remains live at `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`

## Current resume point
1. **For cleanup/visual sessions:** start from `.kr/ACTIVE.md` and `NEXT.md`
2. Keep excerpting implementation paused while cleanup/visual work is active
3. When returning to excerpting, start from `reference/handoffs/excerpting_pause_checkpoint_2026-04-08.md`

## Suggested branch discipline
- Keep `excerpting-foundations-hardening-20260404` as the frozen excerpting checkpoint
- Do cleanup/visual work on a separate branch such as `repo-cleanup-visual-maps-20260408`

## Historical note
The earlier foundations-hardening kickoff and session-2 handoff context remains archived in:
- `reference/handoffs/excerpting_foundations_session3_kickoff_2026-04-04.md`
- `reference/handoffs/excerpting_foundations_claude_hardening_takeover_2026-04-04.md`
