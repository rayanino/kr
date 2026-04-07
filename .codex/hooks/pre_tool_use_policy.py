#!/usr/bin/env python3
from __future__ import annotations

from hook_utils import (
    DESTRUCTIVE_COMMAND_PATTERNS,
    MUTATING_COMMAND_PATTERNS,
    active_authority_state,
    command_matches,
    command_targets_external_coworker_cli,
    command_uses_review_packet_path,
    command_references_only_safe_setup_paths,
    command_references_protected_area,
    command_text,
    emit_json,
    hook_enabled,
    load_event,
    repo_root,
)


def main() -> int:
    event = load_event()
    command = command_text(event)
    if not command:
        return 0

    warnings: list[str] = []
    root = repo_root(event)
    authority = active_authority_state(root)
    active = authority.get("active_authority", "unknown")

    if hook_enabled(root, "disableDestructiveCommandWarnings") and command_matches(DESTRUCTIVE_COMMAND_PATTERNS, command):
        warnings.append(
            "KR guardrail: destructive shell command detected. Prefer non-destructive inspection or an explicit, reversible workflow."
        )

    if hook_enabled(root, "disableProtectedAreaWarnings") and command_references_protected_area(command):
        warnings.append(
            "KR guardrail: this command references a protected area (.claude/, CLAUDE.md, NEXT.md, or docs/superpowers/). Those are outside the Codex setup lane."
        )

    if (
        hook_enabled(root, "disableAuthorityMutationWarnings")
        and active == "claude"
        and command_matches(MUTATING_COMMAND_PATTERNS, command)
    ):
        if not command_references_only_safe_setup_paths(command):
            warnings.append(
                "KR guardrail: active_authority is claude with shadow_setup rules. Shell-based mutations should stay inside .codex/, .agents/skills/, docs/codex/, overnight_codex/, and Codex runtime scripts."
            )

    if (
        hook_enabled(root, "disableCoworkerDispatchWarnings")
        and command_targets_external_coworker_cli(command)
        and not command_uses_review_packet_path(command)
    ):
        warnings.append(
            "KR guardrail: Claude/Gemini coworker dispatch should start from docs/codex/reviews/, docs/codex/dispatch-templates.md, or docs/codex/relay-prompts.md so the packet stays authority-aware and reproducible."
        )

    if warnings:
        emit_json({"systemMessage": " ".join(warnings)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
