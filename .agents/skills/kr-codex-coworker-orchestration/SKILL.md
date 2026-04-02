---
name: kr-codex-coworker-orchestration
description: Use when KR Codex work needs explicit peer-review packets and degraded-mode logic for Claude Code, Gemini CLI, Codex reviewers, and deep-research relays.
---

# KR Codex Coworker Orchestration

Read these files first:

1. `docs/codex/coworker-policy.md`
2. `docs/codex/dispatch-templates.md`
3. `docs/codex/relay-prompts.md` when present

At each major milestone:

- request Claude Code review
- request Gemini CLI review
- request the narrowest Codex review agent or bounded Codex review pass

If a coworker fails because of auth, quota, missing dependencies, or tool failure:

- record the exact failure surface
- continue under degraded mode
- do not silently omit that coworker from the milestone summary
