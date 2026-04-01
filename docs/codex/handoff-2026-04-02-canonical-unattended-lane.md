# Codex Handoff

## Canonical unattended lane

- Repo path: `/home/rayane/kr-canonical-unattended`
- Branch: `codex/canonical-unattended-20260402`
- Authority: `active_authority: codex`
- Runtime mode: `autonomous_codex`
- Starting discipline: conservative `queue_only`

## What this lane contains

- The clean WSL landing of the proven mainline-proof control-plane commits
- A repo-local `.venv` created and verified via `scripts/run_codex_wsl_preflight.sh`
- Live coworker/backend auth confirmation for `codex`, `claude`, and `gemini`
- One successful bounded canonical-lane `overnight_codex` proof for `val-contracts`

## Important cautions

- `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md` is restored here, but it still encodes an April 9 cutover assumption.
- `docs/codex/shadow-24x7-runbook.md` is still a pre-cutover shadow document.
- Do not infer promotion beyond conservative `queue_only` from those files until they are deliberately reconciled to the April 2 `codex` authority state.

## Immediate next steps

1. Keep this lane as the canonical unattended base; leave the dirty Windows checkout untouched.
2. Keep retrying Claude Code and Gemini CLI at major milestones; record degraded mode explicitly when capacity drops.
3. Reconcile the doctrine/runbook date assumptions in a deliberate follow-up instead of silently expanding runtime scope.
