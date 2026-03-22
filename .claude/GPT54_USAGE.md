# GPT-5.4 Access Patterns for KR

## Available Tool: Codex CLI

```
codex-cli v0.116.0
Location: /c/Users/Rayane/AppData/Roaming/npm/codex
```

## Usage Patterns

### Direct CLI Query (recommended for quick lookups)
```bash
codex -q "Your prompt here"
```

### With Model Selection
```bash
codex --model o4-mini -q "Cheaper model for simple tasks"
codex --model gpt-5.4 -q "Full model for complex analysis"
```

### Non-Interactive Mode (for scripts)
```bash
echo "prompt" | codex -q
```

## NOT an MCP Server

`codex mcp` is a management command for MCP server administration.
It is NOT an MCP server endpoint. Do NOT configure it as `mcpServers` in settings.json.

## When to Use GPT-5.4 in KR

Per D-041 (multi-model consensus), content decisions should use multiple models.
GPT-5.4 via codex CLI can serve as a third opinion alongside:
- Claude Opus 4.6 (primary, via Anthropic API)
- Claude Command A (secondary, via OpenRouter)

### Good Use Cases
- Third-opinion verification on disputed classifications
- Cross-model consensus on genre, school, or scholar attribution
- Arabic text analysis from a different model family

### Bad Use Cases
- Routine processing (expensive, adds latency)
- Tasks where Claude alone has sufficient accuracy (92.3% consensus already proven)
- Batch processing (CLI overhead per call is high)

## Budget Considerations

Codex CLI uses your OpenAI API credits, separate from OpenRouter budget.
Track usage carefully. Prefer OpenRouter models for routine work.
