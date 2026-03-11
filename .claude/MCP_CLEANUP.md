# MCP Server Cleanup — Manual Action Required

These MCP servers are configured at the global level and cannot be removed from the project config. The user should disable them in the Claude desktop app or global settings.

## Remove (dead weight for KR)

| MCP Server | Tools | Why Remove |
|-----------|-------|-----------|
| DeepGraph Next.js | 6 (nodes-semantic-search, find-direct-connections, folder-tree-structure, get-code, get-usage-dependency-links, docs-semantic-search) | KR is a Python pipeline. Next.js graph tools are never used. |
| DeepGraph React | 6 (same tools) | Same reason — React graph tools irrelevant to Arabic scholarly pipeline. |
| playwright-server | ~25 (browser_click, browser_navigate, browser_snapshot, etc.) | Redundant. Keep executeautomation-playwright-server only (has code generation). |
| automatalabs-playwright-server | ~10 (browser_click, browser_fill, browser_navigate, etc.) | Redundant. Keep executeautomation-playwright-server only. |
| chrome-devtools | ~25 (click, evaluate_script, lighthouse_audit, etc.) | Redundant. Performance tracing useful but not needed for pipeline work. |
| Exa search (claude_ai_exa) | 2 (web_search_exa, get_code_context_exa) | Redundant with Tavily, which is better for scholarly content. |

**Total impact:** ~74 fewer deferred tools in the selection space.

## Keep (actively useful)

| MCP Server | Why Keep |
|-----------|---------|
| Serena | Symbolic code navigation and editing — core development tool |
| claude-mem | Cross-session memory and smart-explore |
| Context7 | Python library API documentation lookup |
| Tavily (both namespaces) | Web search for scholarly verification |
| Scholar Gateway | Academic literature search (integrate into evaluation workflow) |
| GitHub | Repository management |
| memory (knowledge graph) | Available for future scholar authority tracking |
| executeautomation-playwright | Browser automation if Scholar Interface testing starts |

## Integrate Better (available but underused)

- **Scholar Gateway** (`mcp__claude_ai_Scholar_Gateway__semanticSearch`): Use as secondary source in scholarly-verifier agent for modern academic analysis of classical texts. Not primary for death dates.
- **Context7** (`mcp__context7__resolve-library-id` + `query-docs`): Use in `/research` command for Python library API docs (pydantic, instructor, pytest) before falling back to web search.
