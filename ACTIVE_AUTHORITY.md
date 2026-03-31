# Active Authority

active_authority: claude
effective_date: 2026-03-30
planned_codex_cutover: 2026-04-05
runtime_mode: shadow_setup
owner_interaction: resource_only
frontier_file: .kr/ACTIVE.md
rollback_authority: claude
current_scope: Claude finishes excerpting and taxonomy while Codex builds the takeover environment.
codex_scope_after_cutover: Hardening, regression growth, audits, bounded feature work, and unattended runtime operation.
blocked_after_claude_expiry: Primary Claude-backed excerpting calls remain blocked unless an alternative backend is proven.

## Interpretation

- `claude` means Claude is the active engineering authority. Codex may work only in repo-neutral setup lanes or read-only shadow lanes.
- `codex` means Codex is the active engineering authority for post-v1 execution.
- `runtime_mode: shadow_setup` means unattended Codex runs must stay queue-only and must not edit engine code paths owned by the active Claude lane.
- `runtime_mode: autonomous_codex` means unattended Codex runs may auto-apply bounded changes inside approved prefixes after the quality gate passes.

## Sunday Cutover Checklist

- Excerpting and taxonomy are finished or explicitly frozen.
- Codex WSL runtime is verified.
- `overnight_codex` unattended rehearsal has passed.
- The Claude-backed excerpting CLI path has a scheduled validation window on April 6-9, 2026.

## Rollback

If Codex becomes unstable, switch `active_authority` back to `claude`, set `runtime_mode` back to `shadow_setup`, and resume from `.kr/ACTIVE.md`.
