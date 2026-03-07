# KR Skills

## Installation

Upload each `.zip` file to Claude.ai via **Settings > Customize > Skills**.

## The 6 Skills

| Skill | Purpose | Triggers |
|-------|---------|----------|
| **kr-spec-review** | Handle owner domain comments as research hypotheses | "handle comment", "comment #N", domain feedback |
| **kr-finalize** | Phased SPEC consolidation across multiple focused chats | "finalize", "all comments done", "wrap up" |
| **kr-build-prep** | Tech survey + Claude Code environment optimization | "prepare for building", "implementation prep" |
| **kr-evaluate** | Review test results across 5a/5b/5c dimensions | "evaluate results", "check output" |
| **kr-research** | Creative engine: Scholar's Dream, Impossibility Search, Cross-Tradition Steal | "research", "explore", "what's possible" |
| **kr-integrity** | Deep audit: Perfection Standard + 7 threats + 7 silent failure patterns | "audit", "integrity check", "verify" |

## Architecture (Three Layers)

```
LAYER 1: CUSTOM INSTRUCTIONS (per engine project, always loaded)
  → WHO Claude is: engine-specific expert role
  → ~150 lines, active in every chat

LAYER 2: PROJECT KNOWLEDGE (per engine project, available on demand)
  → WHAT Claude works on: SPEC, contracts, context documents

LAYER 3: SKILLS (account-level, triggered on demand)
  → WHAT TO DO: task procedures with embedded research
```

## Shared Files

Files in `shared/` are templates and protocols to upload to each engine project:
- `COMMENT_TEMPLATE.md` — structured format for owner's SPEC comments
- `HANDOFF_PROTOCOL.md` — clean session bridging when chats get long

## Per-Engine Project Setup

Each engine gets its own Claude Chat project. Setup files are in `source-engine-project/` (source engine) with instructions for creating additional engine projects.

## Design Principles

1. **Comments are hypotheses, not instructions.** Claude investigates and forms its own position.
2. **Research scales to complexity.** Not "always 3 searches" — simple comments need 1, complex ones need 10+.
3. **Finalization is phased.** Never try to audit a 1500-line SPEC in one chat.
4. **CLAUDE.md stays under 200 lines.** Detail goes in docs/ files.
5. **Handoff when context degrades.** Structured summaries bridge chats cleanly.
