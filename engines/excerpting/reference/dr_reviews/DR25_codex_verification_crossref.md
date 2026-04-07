# DR25 Memory-System Claims — Codex Verification Cross-Reference

**Source:** `DR25_claude_memory_system_critical_audit.md`  
**Verified by:** Codex direct inspection + official docs + local machine state  
**Date:** 2026-04-07

## Verification Summary

- **0/5 claims fully CONFIRMED as written**
- **5/5 claims are PARTIALLY TRUE with important corrections**
- The largest DR25 pattern is **overstatement of defaults as hard limits** and **overstatement of present-state behavior as already active on this machine**

## Verification Results

| Claim | Verdict | Evidence | KR Impact |
|-------|---------|----------|-----------|
| 1. AGENTS.md is the cross-tool standard; Codex does not read `CLAUDE.md`; Claude Code does not read `AGENTS.md` | **PARTIALLY TRUE** | Codex official docs: Codex reads `AGENTS.md` before work and discovers it hierarchically. Codex source defaults to `AGENTS.override.md`, then `AGENTS.md`, then configured fallback filenames. Anthropic docs: Claude Code reads `CLAUDE.md`, not `AGENTS.md`, but explicitly supports `@AGENTS.md` import from `CLAUDE.md`. | KR currently exposes [AGENTS.md](C:/Users/Rayane/Desktop/kr/AGENTS.md) to Codex natively and [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md) to Claude Code natively. Cross-tool sharing is possible, but only if `CLAUDE.md` imports `AGENTS.md` or Codex fallback filenames are configured. |
| 2. Codex has a 32 KiB AGENTS.md size cap | **PARTIALLY TRUE** | OpenAI config reference documents `project_doc_max_bytes`. Codex guide states the default combined instruction-chain limit is 32 KiB. Codex source sets `PROJECT_DOC_MAX_BYTES = 32 * 1024` and truncates excess bytes. This is a configurable default, not a fixed hard cap. | KR should treat 32 KiB as the default budget unless [config.toml](C:/Users/Rayane/.codex/config.toml) raises it. Overflow causes truncation of guidance, not a loud failure. |
| 3. KR must move core conventions into AGENTS.md because CLAUDE.md is too large for Codex | **PARTIALLY TRUE** | Local sizes: [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md) = **8,135 bytes**; `.claude/rules/` total = **47,710 bytes**; [AGENTS.md](C:/Users/Rayane/Desktop/kr/AGENTS.md) = **1,724 bytes**. `AGENTS.md + CLAUDE.md = 9,859 bytes`, which fits. A curated high-signal subset of rules also fits under 32 KiB; the full `.claude/rules/` corpus does not. | KR can fit a serious Codex-facing AGENTS doc under the default budget if it is curated. The full Claude rule corpus should remain external and be referenced, not copied wholesale. |
| 4. `codex-mcp-memory` and Basic Memory are viable cross-tool MCP memory options | **PARTIALLY TRUE** | `codex-mcp-memory` is a real GitHub repo with PostgreSQL + pgvector and README instructions for both Codex `config.toml` and Claude CLI MCP setup, but no exact npm or PyPI package was found. Basic Memory is clearly real: real repo, real PyPI package (`basic-memory`), official Claude Code integration docs, and official Codex integration docs. | Basic Memory is the stronger, better-documented real option for KR today. `codex-mcp-memory` is not vaporware, but it is materially thinner as an ecosystem artifact and needs more vetting before being treated as production-grade. |
| 5. Codex autonomous memory is backed by `~/.codex/state_<version>.sqlite` and uses a two-phase memory pipeline | **PARTIALLY TRUE** | Local machine has [state_5.sqlite](C:/Users/Rayane/.codex/state_5.sqlite) and [logs_1.sqlite](C:/Users/Rayane/.codex/logs_1.sqlite). Codex source defines `STATE_DB_VERSION = 5`, so `state_5.sqlite` is keyed to DB schema version, not CLI version. Source also explicitly defines a two-phase memory pipeline: phase 1 extracts `raw_memory`/`rollout_summary` into `stage1_outputs`; phase 2 consolidates into `raw_memories.md`, `rollout_summaries/`, and potentially `MEMORY.md`/`memory_summary.md`/`skills/`. On this machine, however, `stage1_outputs` count is **0** and jobs count is **0**. | The architecture exists, but KR should not assume Codex already has a populated autonomous memory corpus. The drift risk is future and local-machine-specific, not currently realized in this checkout. |

## What Actually Fits in AGENTS.md Under the Default 32 KiB Budget

### Fits comfortably

- Current [AGENTS.md](C:/Users/Rayane/Desktop/kr/AGENTS.md): **1,724 bytes**
- Current [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md): **8,135 bytes**
- Combined `AGENTS.md + CLAUDE.md`: **9,859 bytes**

### Fits if curated

- `AGENTS.md`
- `.claude/rules/arabic-scholarly-conventions.md` (**8,962 bytes**)
- `.claude/rules/quality-workflow.md` (**4,526 bytes**)
- `.claude/rules/testing.md` (**2,166 bytes**)
- `.claude/rules/python-code.md` (**2,154 bytes**)
- `.claude/rules/no-single-model-conclusion.md` (**4,514 bytes**)
- `.claude/rules/mandatory-coworker-dispatch.md` (**1,834 bytes**)

This subset totals **25,880 bytes** with current [AGENTS.md](C:/Users/Rayane/Desktop/kr/AGENTS.md), leaving headroom.

### Does not fit under default budget if copied wholesale

- Full [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md) plus the high-signal rule subset above: **37,278 bytes**
- Full `.claude/rules/` corpus: **47,710 bytes** before adding [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md)

## Key Corrections to DR25

### Correction 1: 32 KiB is a default, not a hard cap

DR25 presents the AGENTS budget as if Codex has a fixed architectural ceiling. The Codex docs and source show this is the default value of `project_doc_max_bytes`, and it can be raised in config.

### Correction 2: Overflow behavior is truncation, not failure

DR25 is directionally right that large docs are risky, but the precise behavior matters. Codex truncates when the combined project-doc budget is exceeded; it does not error out or drop the file wholesale by default.

### Correction 3: Cross-tool blindness is real, but only by default

Codex does not read `CLAUDE.md` by default, and Claude Code does not read `AGENTS.md` by default. But Anthropic explicitly documents the bridge pattern:

```md
@AGENTS.md

## Claude Code
...Claude-specific additions...
```

So the incompatibility is operational default behavior, not an unavoidable tool boundary.

### Correction 4: The SQLite claim needs a present-state qualifier

DR25 describes Codex as if it is already accumulating a conflicting shadow memory. The local state DB exists, and the source pipeline exists, but the live database on this machine currently has:

- `threads`: **328**
- `stage1_outputs`: **0**
- `jobs`: **0**

So the claimed memory divergence risk is prospective, not currently instantiated.

## Recommended KR Interpretation

1. **Do not treat DR25 as wrong overall.** The architectural concern is real.
2. **Do treat DR25 as overstated in key implementation details.** The defaults are softer and more configurable than the report implies.
3. **Near-term minimum fix:** keep a curated root [AGENTS.md](C:/Users/Rayane/Desktop/kr/AGENTS.md) for Codex and import it from [CLAUDE.md](C:/Users/Rayane/Desktop/kr/CLAUDE.md) if cross-tool convergence becomes a priority.
4. **If KR wants shared cross-tool memory soon:** Basic Memory is the most substantiated real option found in this verification pass.
5. **Do not assume Codex's local SQLite memory is already protecting overnight runs.** On this machine, it is not populated.

## Primary Sources Checked

- OpenAI Codex AGENTS guide: `https://developers.openai.com/codex/guides/agents-md`
- OpenAI Codex config reference: `https://developers.openai.com/codex/config-reference`
- OpenAI Codex source: `openai/codex`
- Anthropic Claude Code memory docs: `https://code.claude.com/docs/en/memory`
- Basic Memory docs: `https://docs.basicmemory.com/integrations/claude-code/`, `https://docs.basicmemory.com/integrations/codex`
- `geranton93/codex-mcp-memory` GitHub repo
