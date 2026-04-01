# Codex Handoff

## Session goal

- Reconcile the July 1 autonomy doctrine work off dirty `master`
- Harden the WSL shadow-runtime wrapper/bootstrap path
- Prove the bounded `-RunCycle` path and then the actual repeating-loop entrypoint on a clean mainline proof worktree

## Use This Checkout

For the next Codex chat, use this worktree as the primary repo lane:

- repo path: `C:\Users\Rayane\Desktop\kr-mainline-proof`
- branch: `codex/mainline-proof-20260401_1818`

Do **not** resume from:

- `C:\Users\Rayane\Desktop\kr` for implementation work
  - it is dirty and ahead of origin
- `C:\Users\Rayane\Desktop\kr-doctrine-reconcile`
  - it served as an intermediate reconciliation/proof branch only
  - preserve it until landing is confirmed, then it can be deleted

## What changed

### Mainline-proof commits

- `63bd839f` `codex: reconcile doctrine and harden WSL shadow runtime`
- `52b79204` `docs(codex): record successful proof-worktree shadow loop evidence`

### Files added or updated

- `ACTIVE_AUTHORITY.md`
- `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`
- `docs/codex/backend-proof-status.md`
- `docs/codex/coworker-policy.md`
- `docs/codex/operating-model.md`
- `docs/codex/runtime-policy.md`
- `docs/codex/shadow-24x7-runbook.md`
- `.kr/codex_write_prefixes.txt`
- `scripts/overnight_codex_wsl_bootstrap.sh`
- `scripts/overnight_codex_wsl_resume.ps1`
- `scripts/run_overnight_codex_shadow_loop.ps1`
- `tests/test_overnight_codex_runtime.py`

### What the runtime fixes do

- strip CR before `bash -lc`
- pipe bootstrap via `tr -d '\r' | bash`
- add `-RunCycle` to the PowerShell wrapper
- add a loop wrapper for repeated bounded cycles
- support Windows Git worktrees when bootstrapping a WSL runtime clone
- preserve local dirty worktree changes by rebuilding a clean runtime clone at the same `HEAD` and overlaying only the actual modified/untracked files

## What was verified

### Local tests

- `python -m pytest tests/test_overnight_codex_runtime.py -q`
  - passed on the proof worktrees

### Coworker review

- Claude CLI reviewed:
  - reconciliation doctrine/runtime diff
  - wrapper/bootstrap diff
  - applied mainline-proof diff
  - final wording updates
  - final verdict: no blocking contradictions
- Gemini CLI reviewed multiple major checkpoints successfully earlier in the session and found the important bootstrap and protection issues that were fixed.
- Gemini CLI was quota-exhausted at the very end, so the last wording-only handoff review was not available from Gemini.

### Runtime proof evidence

#### Fresh bounded-cycle proof

Runtime dir:

- `~/kr-mainline-proof-runtime`

Observed successful single bounded proof:

- snapshot: `overnight_codex/run_snapshots/2026-04-01T18-53-32.795707_00-00.json`
- status: `completed`
- task: `val-contracts`
- result: `success`

#### Fresh repeating-loop proof

Runtime dir:

- `~/kr-mainline-proof-loop`

Observed successful repeating-loop snapshots:

- `2026-04-01T19-18-35.561378+00:00`
- `2026-04-01T19-41-06.843518+00:00`
- `2026-04-01T20-04-20.093228+00:00`

For those snapshots:

- status: `completed`
- `val-contracts`: `success`
- no failure classes recorded
- `MORNING_REPORT.md` updated with current-run data

## Current state

- active authority: `claude`
- runtime mode: `shadow_setup`
- frontier file: `.kr/ACTIVE.md`
- doctrine file: `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`

### Important repo topology

- original checkout: `C:\Users\Rayane\Desktop\kr`
  - branch: `master`
  - still dirty / not the place to continue implementation directly
- proof checkout: `C:\Users\Rayane\Desktop\kr-mainline-proof`
  - branch: `codex/mainline-proof-20260401_1818`
  - this is the correct continuation lane

### Incidental dirty file

Ignore this if present:

- `.claude/session_state.json`

It was touched by coworker CLI usage and is not part of the intended work.

## Open risks

- The actual runtime logic is now proven on proof worktrees and fresh runtime dirs, but it is not yet landed onto the canonical owner-facing checkout.
- The original checkout at `C:\Users\Rayane\Desktop\kr` still has unrelated dirty/untracked state, so landing must be deliberate.
- The reused runtime dir `~/kr-codex` showed stale/dirty behavior earlier in the session. Fresh runtime dirs were the reliable proof surface.
- Gemini CLI is currently quota-limited for another final review pass.

## Exact next step

- Decide the landing path for the proven commit set:
  - either move `63bd839f` and `52b79204` onto the canonical owner-facing checkout safely
  - or designate a clean canonical worktree as the unattended runtime lane

Decision criteria:

- the original checkout at `C:\Users\Rayane\Desktop\kr` is still dirty and ahead of origin, so direct application there risks trampling unrelated owner/local state
- the mainline-proof worktree is clean except for incidental `.claude/session_state.json`
- if preserving the original dirty checkout intact matters more than keeping `master` as the unattended lane, prefer adopting a clean canonical worktree
- if the owner explicitly wants the original checkout itself to become canonical, land the two proof commits there carefully and rerun one final confirmation proof

After that choice, run one final confirmation proof from the chosen canonical unattended lane.

## Fresh Chat Bootstrap

Paste this into the new Codex chat:

```text
You are taking over an in-progress KR control-plane session.

Use this exact repo/worktree as your primary lane:
- C:\Users\Rayane\Desktop\kr-mainline-proof
- branch: codex/mainline-proof-20260401_1818

Do not treat C:\Users\Rayane\Desktop\kr as your implementation lane unless you explicitly decide a landing strategy first. It is dirty.

Read in this order:
1. AGENTS.md
2. NEXT.md
3. ACTIVE_AUTHORITY.md
4. CLAUDE.md
5. docs/codex/operating-model.md
6. docs/codex/runtime-policy.md
7. docs/codex/coworker-policy.md
8. docs/codex/shadow-24x7-runbook.md
9. docs/codex/backend-proof-status.md
10. docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md
11. docs/codex/handoff-2026-04-01-mainline-proof.md

Then verify:
- git status --short --branch
- git log --oneline -2

Current proven facts:
- mainline-proof commits:
  - 63bd839f codex: reconcile doctrine and harden WSL shadow runtime
  - 52b79204 docs(codex): record successful proof-worktree shadow loop evidence
- fresh bounded-cycle proof succeeded in ~/kr-mainline-proof-runtime
- fresh repeating-loop proof succeeded in ~/kr-mainline-proof-loop
- original dirty checkout at C:\Users\Rayane\Desktop\kr is not yet the canonical implementation lane

Your first task is to decide and execute the safest landing path from the proven mainline-proof branch to the canonical unattended lane, without losing or trampling the dirty original checkout.

Use Claude CLI and Gemini CLI as coworkers at every major point. If Gemini CLI is quota-exhausted, record that explicitly.
```
