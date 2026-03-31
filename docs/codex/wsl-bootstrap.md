# Codex WSL Bootstrap

Status captured on 2026-03-30:

- `Microsoft-Windows-Subsystem-Linux` is enabled.
- `VirtualMachinePlatform` is enabled.
- `wsl --status` still reports WSL as not installed.
- The remaining host-side blocker is a Windows reboot so the WSL feature becomes active.

## Exact Next Step

1. Reboot Windows.
2. From `C:\Users\Rayane\Desktop\kr`, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1
```

If Ubuntu asks for its first Linux user, create `rayane`, close the Ubuntu window, and run the same command again.

## What The Launcher Does

- installs Ubuntu if it is still missing
- runs the WSL bootstrap script at `scripts/overnight_codex_wsl_bootstrap.sh`
- installs the runtime prerequisites inside WSL, including `make`
- syncs the current Windows working tree into `~/kr-codex` so the local dirty takeover-layer changes are preserved
- verifies:
  - `git`
  - `python`
  - `uv`
  - `node`
  - `npm`
  - `codex`
  - `claude`
  - `gemini`
  - `pytest`
  - `rg`
  - `jq`

## First Shadow Rehearsal

After bootstrap succeeds, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\overnight_codex_wsl_resume.ps1 -RunShadowRehearsal
```

That launches the safest valid rehearsal for the current authority state:

- `active_authority: claude`
- `runtime_mode: shadow_setup`
- queue-only behavior
- one bounded read-only task: `val-contracts`
