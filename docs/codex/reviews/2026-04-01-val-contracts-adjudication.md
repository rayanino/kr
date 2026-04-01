# KR `val-contracts` Adjudication Log

Date: 2026-04-01
Authority: `active_authority: claude`
Runtime mode: `shadow_setup`
Packet under review:

- `docs/codex/reviews/2026-04-01-val-contracts-claude-packet.md`

## Coworker Results

### Claude Code CLI

- Status: degraded
- Notes:
  - first `--print` review attempt exited `0` with no usable output
  - second simplified attempt exited `1` with `Error: Input must be provided either through stdin or as a prompt argument when using --print`
  - no substantive packet findings were recovered from Claude Code CLI in this session

### Gemini CLI

- Status: degraded
- Notes:
  - keychain fell back to file-backed storage successfully
  - review attempt failed repeatedly with `429 RESOURCE_EXHAUSTED`
  - server error reported `MODEL_CAPACITY_EXHAUSTED` for `gemini-3.1-pro-preview`
  - no substantive packet findings were recovered from Gemini CLI in this session

## Adjudication Outcome

- Status: completed under degraded-mode review
- Working rule:
  - preserve disagreements explicitly
  - do not smooth disagreement into a synthetic consensus

## Outcome

- Packet status: unchanged after coworker attempts
- Reason:
  - no coworker returned actionable packet-level contradictions or downgrade requests
  - local sanity review found the packet internally consistent with the `val-contracts` artifact ordering and evidence
- Operational note:
  - this review satisfies the coworker-attempt requirement, but not the stronger dual-coworker substantive-review ideal

## Post-Patch Review

### Codex Direct Review

- Status: completed
- Source:
  - direct read-only `codex exec` review of stable branch head `46b46f81`
- Result:
  - `A3` closed
  - `A2` closed
  - `A1` still internally inconsistent because executable validators and boundary tooling still point at deprecated or legacy taxonomy shapes
  - highest-value next fix is the validation/tooling layer:
    - `scripts/run_pipeline.py`
    - `tools/check_cross_engine_contracts.py`
    - `scripts/verify_metadata_flow.py`

### Claude Code CLI

- Status: degraded
- Notes:
  - later direct commit review attempts again produced no usable packet-level output

### Gemini CLI

- Status: degraded
- Notes:
  - quota exhausted during commit-review attempts

## Current Decision

- Active next handoff belongs to Claude Code CLI
- Scope:
  - executable boundary validation and checker alignment only
- Reference packet:
  - `docs/codex/reviews/2026-04-01-post-patch-val-contracts-followup.md`
