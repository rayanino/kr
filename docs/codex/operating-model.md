# Codex Operating Model

## Canonical Sources

Codex does not get a separate truth system.

Read in this order:

1. `ACTIVE_AUTHORITY.md`
2. `CLAUDE.md`
3. `.kr/ACTIVE.md`
4. `.kr/HANDOFF.md`
5. `NEXT.md` when the work touches the active construction frontier
6. the relevant engine `CLAUDE.md`

## Authority Lanes

- When `active_authority: claude`, Codex may do setup work, runtime work, read-only review, and queued shadow analysis. It must not become a second active engineer on the same lane.
- When `active_authority: codex`, Codex owns the engineering lane for hardening, testing, audits, bounded features, and unattended execution.

## Session Start

1. Read `ACTIVE_AUTHORITY.md`.
2. Rebuild current context from `.kr/ACTIVE.md` and `.kr/HANDOFF.md`.
3. Read the relevant engine `CLAUDE.md`.
4. Select the quality-gate mode before editing anything.

## Quality-Gate Mapping

- `MODE=python`
  Run `pre_review_checks`, `pyright`, and targeted engine tests for changed Python files.
- `MODE=contracts`
  Run `scripts/verify_metadata_flow.py` and `tools/check_cross_engine_contracts.py`.
- `MODE=arabic`
  Run the Arabic safety and diacritic-preservation checks for changed source files.
- `MODE=spec`
  Run `scripts/check_spec_quality.py` on changed `SPEC.md` files.
- `MODE=integration`
  Run boundary checks plus an explicit bounded smoke command when one is safe and configured.
- `MODE=all`
  Infer the required checks from the changed paths.

## Blocked Work Policy

The unattended runtime must never stop and wait for the owner.

- If a task needs domain judgment, procurement, unavailable subscriptions, or access the runtime does not have, record it as blocked or deferred.
- Continue automatically to the next task.
- Never auto-approve human-gated scholarly decisions.

## Runtime Policy

- Preferred host: WSL runtime clone.
- Default pre-cutover mode: shadow, queue-only, no engine-code writes.
- Default post-cutover mode: bounded auto-apply inside approved write prefixes after the quality gate passes.
