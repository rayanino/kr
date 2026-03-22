# MCP Action Plan — Manual Steps for Owner

Generated 2026-03-23 by overnight hardening session.
These changes require manual action in Claude Desktop or global settings.

## Step 1: Remove Dead-Weight MCP Servers

These servers waste context with irrelevant deferred tools (~74 tools total).
Remove them from your Claude Desktop MCP configuration or `~/.claude/settings.json` mcpServers section.

| Server | Tools | Why Remove |
|--------|-------|-----------|
| DeepGraph Next.js | 6 | KR is Python. Next.js graph tools never used. |
| DeepGraph React | 6 | Same — React tools irrelevant to Arabic scholarly pipeline. |
| playwright-server | ~25 | Redundant with executeautomation-playwright. |
| automatalabs-playwright-server | ~10 | Redundant with executeautomation-playwright. |
| chrome-devtools | ~25 | Performance tracing not needed for pipeline work. |
| Exa search (claude_ai_exa) | 2 | Redundant with Tavily. Tavily better for scholarly content. |

## Step 2: Remove Duplicate MCP Instances

| Duplicate | Keep | Remove |
|-----------|------|--------|
| Context7 (3 instances) | `plugin:context7:context7` | standalone `context7` MCP. `claude_ai_Context7` is built-in, can't remove. |
| Tavily (2 instances) | `claude.ai tavily` (claude_ai_tavily) | standalone `tavily` MCP |

## Step 3: Remove Irrelevant Plugin

| Plugin | Why Remove |
|--------|-----------|
| `gopls-lsp@claude-plugins-official` | Go language server. KR is 100% Python. Wastes startup time. |

**How:** In `~/.claude/settings.json`, set `"gopls-lsp@claude-plugins-official": false` in enabledPlugins.

## Step 4: Verify Firecrawl

Firecrawl is enabled in settings (`"firecrawl@claude-plugins-official": true`) but was NOT
visible in the deferred tools list during the current session. This may indicate:
- A startup failure (restart may fix)
- Missing API key or configuration
- Plugin installation issue

**Action:** After restart, check if `mcp__firecrawl` tools appear. If not, reinstall the plugin.

## Step 5: QuranHub MCP (Future — Taxonomy Phase)

QuranHub MCP is a free, production-ready Quran cross-referencing tool:
- Search Quranic text, retrieve ayahs by reference
- Tajweed rules, multiple editions
- Mutashabihat (similar verses)

**Do NOT install now.** Defer to taxonomy engine phase where Quran cross-referencing
becomes relevant. Logged in `.claude/pending_decisions.log`.

## Impact

After completing Steps 1-3:
- ~90 fewer deferred tools in the selection space
- Faster tool resolution
- Cleaner context (no duplicate tool names causing confusion)
- Marginally faster session startup
