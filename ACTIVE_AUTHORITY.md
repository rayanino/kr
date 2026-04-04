# Active Authority

active_authority: claude
effective_date: 2026-04-04
planned_codex_cutover: 2026-04-02
autonomous_period_end: 2026-07-01
runtime_mode: shadow_setup
owner_interaction: resource_only
frontier_file: .kr/ACTIVE.md
rollback_authority: codex
autonomy_doctrine_file: docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md
current_scope: Claude is the active engineering authority for the post-F6 excerpting foundations hardening lane on local master. Start from the staged takeover brief at `reference/handoffs/excerpting_foundations_claude_hardening_takeover_2026-04-04.md`, move implementation to a clean excerpting-focused branch before hardening work, and treat Codex as setup/runtime/read-only shadow support.
codex_scope_after_cutover: Hardening, regression growth, audits, queued patch generation, and unattended runtime operation.
blocked_after_claude_expiry: The referenced doctrine file is currently missing from `docs/codex`. Until that control-plane gap is repaired, keep operation conservative: queue-only starts, explicit blocker logging, and no policy expansion inferred from the missing doctrine file.

## Interpretation

- `claude` means Claude is the active engineering authority. Codex may work only in repo-neutral setup lanes or read-only shadow lanes.
- `codex` means Codex is the active engineering authority for post-v1 execution.
- `runtime_mode: shadow_setup` means unattended Codex runs must stay queue-only and must not edit engine code paths owned by the active Claude lane.
- `runtime_mode: autonomous_codex` means unattended Codex runs may auto-apply bounded changes inside approved prefixes after the quality gate passes.

## Cutover Checklist

- Early owner-approved cutover took effect on April 2, 2026.
- Formal handoff to Claude for excerpting foundations hardening takes effect on April 4, 2026.
- Start from `shadow_setup` discipline and use the staged excerpting takeover brief before any hardening implementation begins.
- Move hardening work to a clean excerpting branch rather than running it on the taxonomy branch.
- Record Claude Code quota limits explicitly at major milestones and continue under degraded coworker capacity when needed.
- Restore or replace `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md` before relying on doctrine-governed promotions or degraded-mode assumptions beyond the conservative starting lane.

## Rollback

If the Claude-led foundations hardening lane becomes unstable, switch `active_authority` back to `codex`, restore `runtime_mode` to `autonomous_codex` only when Codex is intentionally re-promoted, and resume from `.kr/ACTIVE.md`.
