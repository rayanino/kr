---
name: kr-codex-review-dispatch
description: Use when KR work needs the right Codex review or probing agent selected deliberately instead of generic delegation. This skill maps task shapes to the repo-local Codex agents.
---

# KR Codex Review Dispatch

Read `docs/codex/dispatch-templates.md` before dispatching review work.

Choose the narrowest repo-local Codex agent:

- `kr_repo_mapper` for repo topology, ownership, and allowed-surface mapping
- `kr_boundary_validator` for engine-boundary and D-023 checks
- `kr_code_reviewer` for correctness, regressions, and missing tests
- `kr_arabic_reviewer` for Arabic-risk and scholarly metadata structure
- `kr_build_prober` for cumulative session-diff vs SPEC checks
- `kr_runtime_prober` for WSL, auth, runtime, and backend-proof paths
- `kr_coworker_brief_writer` for Claude/Gemini/DR review packets
- `kr_quick_check` for fast pyright/pytest/grep sanity passes

If `active_authority` is still `claude`, dispatch only review, runtime, and setup-lane work. Do not use Codex agents to become a second active engineer on engine code.
