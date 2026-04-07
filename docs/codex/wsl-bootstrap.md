# Codex Windows Bootstrap

This file keeps the historical path name, but the canonical KR Codex bootstrap is now Windows-first.

## Default Startup

From `C:\Users\Rayane\Desktop\kr`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1
```

That launcher:

- prints `active_authority` and `runtime_mode`
- runs the repo-local Codex setup audit unless you skip it
- optionally runs auth preflight for `codex`, `claude`, and `gemini`
- starts Codex with the requested KR profile from the current Windows checkout

## Recommended Windows Commands

Setup audit only:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1 -NoLaunch
```

Setup + auth preflight:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1 -RunAuthPreflight -NoLaunch
```

Queue-only shadow loop:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1
```

## KR Profiles

Recommended Codex profiles on Windows:

- `codex -p kr_interactive`
- `codex -p kr_shadow`
- `codex -p kr_peer_review`
- `codex -p kr_research`

## Legacy WSL Fallback

The WSL bootstrap and resume scripts remain in the repo for diagnostics or historical fallback, but they are no longer the default KR Codex path.

Only revisit them if a concrete Windows blocker is documented and cannot be resolved in the current checkout.
