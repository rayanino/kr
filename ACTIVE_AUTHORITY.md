# Active Authority

active_authority: codex
effective_date: 2026-04-02
planned_codex_cutover: 2026-04-02
autonomous_period_end: 2026-07-01
runtime_mode: autonomous_codex
owner_interaction: resource_only
frontier_file: .kr/ACTIVE.md
rollback_authority: claude
autonomy_doctrine_file: docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md
current_scope: Codex is the active engineering authority for the owner-led April 2-6 execution window. Operate from the clean WSL canonical unattended lane, start in `queue_only`, and treat Claude Code quota pressure as degraded coworker capacity rather than a blocker to owned work.
codex_scope_after_cutover: Hardening, regression growth, audits, queued patch generation, and unattended runtime operation.
blocked_after_claude_expiry: The restored doctrine file still encodes an April 9 cutover assumption. Until doctrine and authority dates are reconciled, keep operation conservative: queue-only starts, explicit blocker logging, and no promotion or write-scope expansion inferred from the doctrine alone.

## Interpretation

- `claude` means Claude is the active engineering authority. Codex may work only in repo-neutral setup lanes or read-only shadow lanes.
- `codex` means Codex is the active engineering authority for post-v1 execution.
- `runtime_mode: shadow_setup` means unattended Codex runs must stay queue-only and must not edit engine code paths owned by the active Claude lane.
- `runtime_mode: autonomous_codex` means unattended Codex runs may auto-apply bounded changes inside approved prefixes after the quality gate passes.

## Cutover Checklist

- Early owner-approved cutover took effect on April 2, 2026.
- Start from `autonomous_codex` with `queue_only` operational discipline.
- Record Claude Code quota limits explicitly at major milestones and continue under degraded coworker capacity when needed.
- Reconcile the restored doctrine with the April 2 authority state before relying on doctrine-governed promotions or degraded-mode assumptions beyond the conservative starting lane.

## Rollback

If Codex becomes unstable, switch `active_authority` back to `claude`, set `runtime_mode` back to `shadow_setup`, and resume from `.kr/ACTIVE.md`.
