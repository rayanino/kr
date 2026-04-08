# KR Migration Recovery Map — 2026-04-09

This document defines the safe recovery map after the pre-new-PC consolidation.

## Canonical branch

- `canonical/excerpting-clean-start-20260409`

This is the only branch intended as the fresh starting point on the new PC.

It includes:

- the current repo-cleanup / owner-visual frontier from `.kr/ACTIVE.md`
- the current handoff state from `.kr/HANDOFF.md`
- the current `NEXT.md`
- the excerpting pause checkpoint handoff
- the Windows Codex migration/bootstrap control-plane fixes

## Historical branches kept intact

These remain on the remote as historical lines and must not be used as the default base for new work:

- `main`
- `master`
- `excerpting-foundations-hardening-20260404`

## Remote archive namespace

These branches were preserved under `archive/*` so no local-only branch line is lost:

- `archive/branch/master-local-20260409`
- `archive/branch/migration-pause-2026-04-08`
- `archive/branch/migration-wsl-to-windows-main-20260405`
- `archive/branch/wsl-master-preserved-20260406`
- `archive/branch/codex-doctrine-reconcile-20260401_1015`
- `archive/branch/codex-mainline-proof-20260401_1818`
- `archive/branch/codex-windows-migration-setup-20260408`
- `archive/branch/taxonomy-sarf-review-packet-publish-20260406`
- `archive/detached/kr-taxonomy-k2-review-20260409`

Dirty local worktrees with meaningful uncommitted state were materialized as archive WIP branches:

- `archive/wip/excerpting-worktree-20260409`
- `archive/wip/codex-migration-worktree-20260409`
- `archive/wip/autonomous-taxonomy-pause-20260409`

Local stashes were preserved as archive refs:

- `archive/stash/00-events-log`
- `archive/stash/01-session-16-wip`
- `archive/stash/02-cli-adapter-max-turns-1-timeout-180s`
- `archive/stash/03-cli-adapter-cp1252-reduction`
- `archive/stash/04-cli-backend-spec-implementation-plan-a`
- `archive/stash/05-cli-backend-spec-implementation-plan-b`
- `archive/stash/06-master-session`
- `archive/stash/07-f03-corrected-scores`

## Preserved tags

These local-only tags were pushed to the remote as-is:

- `migration-preserve-20260405-kr-codex`
- `migration-preserve-20260405-proof3`
- `migration-preserve-20260405-unattended`
- `pause-2026-04-08-taxonomy-safe`

## Offline preservation assets

These are source-machine preservation artifacts and should be copied off the old PC before disposal:

- `kr-total-preservation-20260409_002649`
- `kr-preservation-20260409_000815`
- `kr-codex-setup-bundle-20260408_235052.zip`
- `kr_sync_recovery_20260401_082139`
- `kr_wsl_migration_20260405`
- `kr_wsl_retirement_20260406`

The `kr-total-preservation-20260409_002649` folder is the highest-priority offline snapshot. It contains:

- the repo preservation bundle and dirty-worktree snapshots
- stash patch exports
- raw home archives for `.codex`, `.agents`, `.claude`, and `.gemini`
- a manifest of Desktop preservation sources

## New-PC rule

On the new PC:

1. Clone the repo fresh.
2. Start from `canonical/excerpting-clean-start-20260409`.
3. Restore the clean Codex setup bundle into `%USERPROFILE%\\.codex` and `%USERPROFILE%\\.agents`.
4. Keep the raw offline preservation folder as disaster recovery, not as the day-to-day working copy.
5. Create all new branches from the canonical branch unless intentionally reviving an archived line.
