#!/usr/bin/env python3
from __future__ import annotations

from hook_utils import (
    changed_paths,
    detect_drift,
    emit_json,
    hook_enabled,
    infer_quality_gate_mode,
    load_event,
    needs_setup_audit,
    paths_look_like_major_conclusions,
    paths_touch_planning_surface,
    repo_root,
)


def main() -> int:
    event = load_event()
    root = repo_root(event)
    paths = changed_paths(root)
    if not paths:
        return 0

    messages: list[str] = []
    mode = infer_quality_gate_mode(paths)
    if mode and hook_enabled(root, "disableStopQualityGateReminder"):
        joined = " ".join(paths)
        messages.append(f'Run before finishing: make quality-gate MODE={mode} PATHS="{joined}"')

    if needs_setup_audit(paths) and hook_enabled(root, "disableStopSetupAuditReminder"):
        messages.append(
            "Codex control-plane changes detected. Run: python scripts/check_codex_kr_setup.py --auth-preflight"
        )

    if paths_look_like_major_conclusions(paths) and hook_enabled(root, "disableStopDispatchReminder"):
        messages.append(
            "Major conclusion/report surface changed. Re-check coworker coverage or run: python scripts/enforcement/check_dispatch_state.py"
        )

    if paths_touch_planning_surface(paths) and hook_enabled(root, "disableStopPlanReminder"):
        messages.append(
            "Planning/frontier surface changed. Re-check completeness or run: python scripts/enforcement/validate_plan_completeness.py"
        )

    if hook_enabled(root, "disableDriftDetection"):
        drift_warning = detect_drift(root, paths)
        if drift_warning:
            messages.append(drift_warning)

    if messages:
        emit_json({"systemMessage": " ".join(messages)})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
