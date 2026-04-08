# KR Codex Windows Migration

Use this when moving KR Codex work to another Windows PC.

## Default Mode

Use a clean bootstrap.

That means:

- clone the KR repo normally from GitHub
- copy only your home-level Codex settings and skills
- reinstall toolchains on the new machine
- sign in again for Codex, Claude, and Gemini
- recreate secrets instead of copying auth/session state blindly

## What GitHub Already Gives You

The repo already tracks the KR-specific control plane:

- `.codex/`
- `.agents/skills/`
- `docs/codex/`
- `scripts/check_codex_kr_setup.py`
- `scripts/check_runtime_cli_auth.py`
- `scripts/start_codex_kr.ps1`
- `scripts/run_overnight_codex_shadow_loop.ps1`

Pulling the repo restores those surfaces automatically.

## What You Still Need To Migrate

Move these home-level paths from the source machine:

- `%USERPROFILE%\.codex\config.toml`
- `%USERPROFILE%\.codex\AGENTS.md`
- `%USERPROFILE%\.codex\skills\`
- `%USERPROFILE%\.codex\superpowers\`
- `%USERPROFILE%\.agents\skills\`
- `%USERPROFILE%\.agents\.skill-lock.json`

Optional:

- `%USERPROFILE%\.codex\plugins\cache\`

Do not copy by default:

- `%USERPROFILE%\.codex\auth.json`
- `%USERPROFILE%\.codex\history.jsonl`
- `%USERPROFILE%\.codex\session_index.jsonl`
- `%USERPROFILE%\.codex\state_*.sqlite*`
- `%USERPROFILE%\.codex\logs_*.sqlite*`
- caches, sandboxes, temp directories

## Export A Clean Bundle On The Source PC

From the KR repo root:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\export_codex_windows_setup.ps1
```

Optional plugin cache:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\export_codex_windows_setup.ps1 -IncludePluginCache
```

The script creates a bundle on the Desktop with:

- `home\.codex\`
- `home\.agents\`
- `manifest.json`
- `README.md`

## Target Machine Bootstrap

1. Install the machine prerequisites:
   - `codex`
   - Python
   - Git
   - Node.js / `npx`
   - `claude`
   - `gemini`
2. Restore the exported `home\.codex\*` into `%USERPROFILE%\.codex\`.
3. Restore the exported `home\.agents\*` into `%USERPROFILE%\.agents\`.
4. Clone KR from GitHub.
5. Recreate secrets with environment variables or a fresh `.env`.
6. Update `%USERPROFILE%\.codex\config.toml` if the new repo path differs from the old trusted project path.

## Verification On The Target PC

From the KR repo root:

```powershell
python scripts/check_codex_kr_setup.py
python scripts/check_codex_kr_setup.py --auth-preflight
```

Then launch normally:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\start_codex_kr.ps1
```

For queue-only shadow work:

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\run_overnight_codex_shadow_loop.ps1
```
