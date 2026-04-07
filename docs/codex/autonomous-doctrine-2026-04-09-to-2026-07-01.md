# KR Autonomous Doctrine: April 9 to July 1, 2026

**Authority:** Governing for KR Codex unattended control-plane operation during the April 9, 2026 to July 1, 2026 period. When this file conflicts with older Codex runtime notes, this file wins for this period.

**Council inputs synthesized:**
- `docs/codex/reviews/2026-04-01-july-doctrine/claude-chat.md`
- `docs/codex/reviews/2026-04-01-july-doctrine/chatgpt-dr.md`
- `docs/codex/reviews/2026-04-01-july-doctrine/gemini-cli.md`
- `docs/codex/reviews/2026-04-01-july-doctrine/gemini-chat.md`
- `docs/codex/reviews/2026-04-01-july-doctrine/claude-code.md`
- `docs/codex/reviews/2026-04-01-july-doctrine/codex-fresh.md`

## 1. Governing Stance

The operating bias for this period is:

**Stagnation over corruption.**

The system is a hardening-first control plane, not a feature factory. A delayed or stalled run is acceptable. Silent epistemic corruption is not.

During this period:

- Codex is the control-plane authority starting on **April 9, 2026**, not before.
- The owner is interrupted only for:
  - major architecture or scope changes
  - resources, purchases, credentials, or access
  - domain judgment that must not be auto-decided
- Control-plane progress is measured by:
  - stable bounded cycles
  - clean runtime recovery
  - reliable coworker review
  - verified backend proof
  - disciplined reporting
  - regression and hardening growth

## 2. Scope

### Before April 9, 2026

Authority remains `claude`. Codex stays in `shadow_setup` and `queue_only`.

Allowed:

- read-only audits
- validation and regression checks
- control-plane documentation
- runtime setup and parity work
- backlog shaping
- backend-proof smoke runs

Not allowed:

- engine-source implementation in Claude-owned lanes
- auto-apply into engine paths
- SPEC changes
- protected-area writes

### April 9 to July 1, 2026

Codex may own:

- control-plane operation
- runtime hardening
- regression growth
- read-only audits and bounded runtime-artifact writes inside the approved allowlist
- review-packet preparation
- queued patch generation for engine-source hardening

Codex may not autonomously own:

- taxonomy build
- synthesis build
- SPEC modification
- protected areas
- engine-source auto-apply
- scholarly arbitration

For this period, engine-source changes may be generated only as reviewed queued patches. They do not auto-apply.

## 3. Runtime Shape

Use bounded Windows cycles from the intended checkout, not a single long-lived daemon.

Default cycle:

- duration: `1.5h`
- cadence: every `2h`
- host: current Windows checkout at `C:\Users\Rayane\Desktop\kr`
- overlap rule: never start a new instance while one is running

Every cycle must:

1. load `ACTIVE_AUTHORITY.md`
2. verify runtime mode and setup/parity state
3. classify provider health
4. pick exactly one primary work mode
5. leave visible artifacts

Same-run discovery must not create same-run implementation.

## 4. Runtime State Model

Use two orthogonal dimensions, not one flat state enum.

### Authority mode

- `shadow_setup`
  - pre-cutover only
  - `queue_only`
  - read-only, setup, validation, backlog shaping
- `autonomous_codex`
  - post-cutover only
  - starts in `queue_only`
  - may later promote only within the explicit write-prefix allowlist in `.kr/codex_write_prefixes.txt`

### Health state

- `full`
  - Codex, Claude Code, and Gemini healthy
- `reduced`
  - Codex healthy, exactly one peer coworker healthy
  - no gate promotion
  - no auto-apply
  - outputs marked `reduced_confidence: true`
- `solo`
  - Codex healthy, no peer coworker healthy
  - read-only audits, report generation, state repair, backlog shaping only
- `halted`
  - Codex unavailable
  - setup/parity audit failed
  - protected-area write attempt
  - repeated rollback or circuit-breaker threshold

The effective runtime state is the pair:

`authority_mode x health_state`

## 5. Coworker Rule

Peer major coworkers for this period:

- `Claude Code`
- `Gemini CLI (Pro 3.1)`

At every major milestone, request both when available.

Major milestone means:

- doctrine or control-plane policy changes
- runtime-state or cutover decisions
- backend-proof interpretation
- hook or enforcement changes
- owner-facing packet decisions
- any `HIGH` or `CRITICAL` finding

If one coworker is unavailable:

- record it explicitly
- do not silently downgrade its role
- continue only under the degraded-mode rules above

If coworkers disagree:

- use the more conservative severity
- escalate if the disagreement touches scope, doctrine, or domain-sensitive truth

## 6. Work Budget

For the autonomous period, use this budget:

- `85%` hardening, proof, regression, runtime reliability
- `15%` evaluation prep and owner packet formatting

This is a zero-feature period.

No autonomous BUILD authorization exists for new engines between **April 9, 2026** and **July 1, 2026**.

## 7. Quota Doctrine

Treat provider capacity as a schedulable resource.

Rules:

- classify calls as `L`, `M`, or `H`
- concurrency is `1` per provider
- one retry only for transient transport failure
- no retry on explicit auth or rate-limit reset responses
- use exponential backoff with jitter
- the moment a cycle enters `reduced` or `solo`, autonomous auto-apply is disabled
- after `3` consecutive `reduced` or `solo` cycles, gate promotion remains locked until a `full` cycle succeeds again

Provider role bias:

- Codex: primary for control-plane reasoning, audit, and review
- Claude Code: primary builder and structured repo coworker
- Gemini CLI: adversarial challenger, especially on doctrine and risk

If both peer coworkers are unavailable for more than `24h`, create an owner-visible resource/access item in the next morning report.

## 8. Daily Owner Contract

The owner gets exactly one frozen daily report after the first successful cycle of the day.

`MORNING_REPORT.md` must fit within:

- `25` lines or
- `400` words

Required sections:

1. `Current state`
2. `Changes since yesterday`
3. `Needs owner`
4. `Blocked by resources`
5. `Next 24 hours`

`Needs owner` may contain at most `3` items.

Every owner item must include:

- item id
- why blocked
- decision needed
- default if no reply

Default on silence is always:

`defer_and_continue`

Meaning:

- the item remains blocked
- the runtime proceeds only to unrelated work
- no deferred item is treated as approved

Silence is never approval.

## 9. Gate 0 Before April 9, 2026

Cutover does not happen unless all of these are true:

1. The repo-local Codex control-plane surface is restored and in sync.
2. Windows setup audit passes.
3. Windows auth preflight passes for `codex`, `claude`, and `gemini`.
4. Two consecutive bounded shadow cycles pass from the intended Windows checkout.
5. Backend proof is green enough for the path Codex will own.
6. Blocking hook enforcement is installed, peer-reviewed, and reads `.kr/codex_write_prefixes.txt`.
7. Rollback procedure is rehearsed.
8. `ACTIVE_AUTHORITY.md` is updated for the April 9, 2026 cutover and points at this doctrine.

If any Gate 0 item is red on **April 9, 2026**, cutover delays.

## 10. Gate Model After Cutover

### Gate A

Start in:

- `active_authority: codex`
- `runtime_mode: autonomous_codex`
- `apply_mode: queue_only`

### Gate B

Promotion beyond queue-only requires:

- `7` consecutive clean cycles immediately preceding the promotion attempt
- zero protected-area violations
- zero rollback-guard events
- peer coworker availability `>= 80%` measured across those same `7` cycles
- no open `CRITICAL` control-plane findings

Even after Gate B, auto-apply is restricted to `.kr/codex_write_prefixes.txt`. For this period, that allowlist is runtime-artifact-only. It does not extend to control-plane source files or engine source.

## 11. Stop and Rollback

Immediate stop conditions:

- authority mismatch
- Windows setup or auth audit failure
- unreadable state schema
- protected-area write attempt
- Codex unavailability
- repeated rollback or circuit-breaker threshold

Rollback rules:

- failed quality gate means rollback to the pre-apply snapshot
- any protected-area write attempt forces `halted`
- `3` rollback events in `24h` force `halted`

When Codex halts, it does not rewrite `ACTIVE_AUTHORITY.md` itself. The next owner action or interactive Claude session performs the formal authority rollback.

## 12. Shadow Restart Decision For Today

Restart the shadow loop today only if this sequence passes in order:

1. restore the recovered Codex control-plane surface from `codex/control-plane-sync-20260401_082139`
2. run Windows setup audit successfully
3. run Windows auth preflight successfully
4. verify the current checkout contains the live `.codex/` hook surface and Windows launcher files
5. run one bounded shadow cycle successfully from the intended checkout
6. run a second bounded shadow cycle successfully after a fresh Windows relaunch

If either bounded cycle fails, do not restart the repeating loop today.

## 13. Exact Next Steps Before April 9, 2026

1. Restore the recovered repo-local Codex runtime surface from `codex/control-plane-sync-20260401_082139` into a clean recovery branch or worktree.
2. Keep `.claude/`, `CLAUDE.md`, `NEXT.md`, and the external review inputs read-only.
3. Install the canonical doctrine and point the live control-plane docs at it.
4. Run peer doctrine review through Claude Code and Gemini CLI and incorporate findings.
5. Run targeted runtime verification on the changed control-plane files.
6. Rehearse rollback and bounded-cycle restart.
7. Delay cutover if Gate 0 is not fully green by **April 9, 2026**.
