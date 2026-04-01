## CLI Tool Verification Report (2026-03-28)

**Environment:** Windows 11 Home, tested from `C:\Users\Rayane\Desktop\kr`

### Results

| Tool | Version | Status | Default Model | Non-Interactive Syntax |
|------|---------|--------|---------------|----------------------|
| **Codex CLI** | 0.116.0 | **WORKS** | gpt-5.4 | `codex exec --full-auto "prompt"` |
| **Copilot CLI** | 1.0.12 | **WORKS** | gpt-4.1 | `copilot -p "prompt" --model gpt-4.1` |
| **Gemini CLI** | 0.35.3 | **WORKS** | gemini (default) | `gemini -p "prompt" -o text` |

### Codex CLI (OpenAI)
- **Invocation:** `codex exec --full-auto "prompt"`
- **Note:** `--full-auto` is a standalone flag (not `--approval-mode full-auto`). The `-p` flag selects a config profile, NOT a prompt — the prompt is a positional argument.
- **Model override:** `-c model="o3"` (uses TOML config syntax, not `--model`)
- **Output:** Verbose by default (shows session metadata, tool calls, then result)

### Copilot CLI (GitHub/OpenAI)
- **Invocation:** `copilot -p "prompt" --model gpt-4.1`
- **Syntax is exactly as expected.** `-p` is the prompt flag, `--model` selects the model.
- **Output:** Shows tool calls, then result, then usage summary
- **Token reporting:** 65.3k in, 35 out, 32.6k cached

### Gemini CLI (Google)
- **Invocation:** `gemini -p "prompt" -o text`
- **Auth:** Uses Google account login (cached credentials via `~/.gemini/settings.json`)
- **Auto-approve mode:** `--approval-mode yolo` or `-y` (equivalent to Codex `--full-auto`)
- **Output format options:** `-o text` (plain), `-o json`, `-o stream-json`
- **Model override:** `-m model-name`
- **Output:** Clean — just prints the response

### Quick Reference (copy-paste commands)
```bash
# Codex — full auto, custom model
codex exec --full-auto -c model="o3" "your prompt here"

# Copilot — specific model
copilot -p "your prompt here" --model gpt-4.1

# Gemini — non-interactive, plain text output, auto-approve
gemini -p "your prompt here" -o text -y
```
