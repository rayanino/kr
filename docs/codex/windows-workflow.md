# KR Codex Windows Workflow

Use this as the short operator guide for day-to-day Codex work in KR.

## Start

- Launch normally: `powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1`
- Audit only: `powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1 -NoLaunch`
- Audit plus backend health: `powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1 -RunAuthPreflight -NoLaunch`

## Profiles

- `kr_interactive` for normal work in the current checkout
- `kr_peer_review` for read-only review packets
- `kr_research` for docs or web verification
- `kr_shadow` for queue-only shadow work

## High-Value KR Habits

- Start every serious session by reading `ACTIVE_AUTHORITY.md`, `CLAUDE.md`, `docs/codex/operating-model.md`, `.kr/ACTIVE.md`, and `.kr/HANDOFF.md`.
- If the task touches Arabic text, scholarly metadata, or regex over Arabic, use `kr-codex-arabic-integrity` and bridge to `.claude/skills/arabic-text/SKILL.md`.
- If the task changes Codex control-plane files, rerun `python scripts/check_codex_kr_setup.py --auth-preflight` before closing out.
- For major conclusions, prepare coworker packets from `docs/codex/reviews/` and dispatch Claude Code plus Gemini CLI.
- Before declaring completion, run the narrowest `make quality-gate MODE=<mode> PATHS="<paths>"` implied by the changed files.

## Shadow Work

- Bounded loop: `powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1`
- Backend proof: `bash scripts/run_codex_backend_proof_smoke.sh`
- Keep shadow runs queue-only while `active_authority: claude`.

## Fallback

Do not switch back to WSL just because it exists.

Only use the legacy WSL scripts if a concrete Windows-specific blocker is documented and cannot be fixed in the intended checkout.
