# Active Authority

active_authority: claude
effective_date: 2026-03-30
planned_codex_cutover: 2026-04-09
autonomous_period_end: 2026-07-01
runtime_mode: shadow_setup
owner_interaction: resource_only
frontier_file: .kr/ACTIVE.md
rollback_authority: claude
autonomy_doctrine_file: docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md
current_scope: Claude remains active authority while Codex restores and proves the takeover control plane in shadow mode.
codex_scope_after_cutover: Hardening, regression growth, audits, bounded feature work, and unattended runtime operation.
blocked_after_claude_expiry: Primary Claude-backed excerpting calls remain blocked unless an alternative backend is proven.

## Interpretation

- `claude` means Claude is the active engineering authority. Codex may work only in repo-neutral setup lanes or read-only shadow lanes.
- `codex` means Codex is the active engineering authority for post-v1 execution.
- `runtime_mode: shadow_setup` means unattended Codex runs must stay queue-only and must not edit engine code paths owned by the active Claude lane.
- `runtime_mode: autonomous_codex` means unattended Codex runs may auto-apply bounded changes inside approved prefixes after the quality gate passes.

## Cutover Checklist

- Follow `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`.
- Do not cut over before April 9, 2026.
- Gate 0 in the doctrine must be fully green before authority flips.
- Until then, Codex remains in `shadow_setup` and `queue_only`.

## Rollback

If Codex becomes unstable, switch `active_authority` back to `claude`, set `runtime_mode` back to `shadow_setup`, and resume from `.kr/ACTIVE.md`.
