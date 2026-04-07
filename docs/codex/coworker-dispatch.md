# Codex Coworker Dispatch

Use this document when KR control-plane work needs coordinated peer review.

## Required Milestones

Request coworker review at:

- the initial audit checkpoint
- after substantive setup or runtime-control-plane changes
- before final close-out

If a coworker fails, log the failure explicitly and continue in degraded mode.

## Claude Code CLI

Preferred Windows pattern:

```powershell
$packet = Get-Content -Raw docs/codex/reviews/coworker-packet-template.md
claude -p $packet --permission-mode plan --add-dir C:\Users\Rayane\Desktop\kr
```

Notes:

- keep the packet path-specific and authority-aware
- if the packet grows large, write it to a temp file rather than improvising the prompt inline

## Gemini CLI

Preferred Windows pattern on this machine:

```powershell
$packet = Get-Content -Raw docs/codex/reviews/coworker-packet-template.md
gemini --approval-mode plan --include-directories C:\Users\Rayane\Desktop\kr -p $packet
```

Notes:

- do not add `--sandbox` unless Docker or Podman is explicitly configured
- keep the prompt bounded to setup/runtime/shadow surfaces while `active_authority: claude`

## Codex Subagents

Use the repo-local agents deliberately:

- `kr_repo_mapper`
- `kr_runtime_prober`
- `kr_code_reviewer`
- `kr_boundary_validator`
- `kr_arabic_reviewer`
- `kr_quick_check`
- `kr_coworker_brief_writer`

## Minimal Packet Contents

- task goal
- authority and protected-area constraints
- exact files or prefixes in scope
- current audit findings
- specific challenge requested from the coworker
