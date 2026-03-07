# Research Agenda: Claude Chat as Engine Production Guide

**Created:** 2026-03-07
**Purpose:** Continuous improvement of the skills and workflow that drive KR engine production
**Status:** ACTIVE — pick up in next Claude Chat session

---

## What We Know So Far

### Confirmed Facts
- Claude Chat can clone the repo in 4 seconds (shallow clone) and push changes
- Context window is 200K tokens (all plans)
- Project knowledge uses RAG — it doesn't dump all files into context, it retrieves relevant content on demand (THIS CHANGES OUR ASSUMPTIONS about minimal project knowledge)
- Claude Code's system prompt uses ~50 instruction slots; models follow ~150-200 total
- Skills trigger unreliably (Vercel found 56% miss rate in their evals)
- CLAUDE.md should be under 200 lines for Claude Code
- Rate limits: Pro ~45 messages/5hr, Opus uses 3x more tokens than Sonnet
- Claude Chat and Claude Code share the same message quota
- Fresh conversations every 20-30 messages is recommended

### Architecture Decisions Made (don't re-debate)
- 6 skills, account-level, same across all engines
- Per-engine customization via custom instructions + project knowledge
- Repo-first workflow: Claude clones at chat start
- Owner comments as hypotheses, not instructions
- Phased finalization across multiple chats

### Open Questions (from this session)
1. If project knowledge uses RAG, should we upload MORE files (SPECs, contracts, etc.) since they don't all consume context simultaneously?
2. How does the RAG retrieval actually work? Does it chunk files? What's the retrieval quality for technical specs?
3. What's the actual context budget breakdown? (custom instructions + skills metadata + tools + RAG retrieval + conversation)

---

## Research Tracks

### Track 1: Claude Chat Mechanics Deep Dive
**Goal:** Understand exactly how Claude Chat Projects work under the hood.

Research questions:
- How does RAG work for project knowledge files? Chunking strategy? Retrieval quality?
- What's the actual context budget? Custom instructions take how many tokens? Skills metadata? Web search tool?
- How does "automatic context management" (conversation summarization) work in practice?
- What triggers skill activation reliably vs unreliably? How to maximize trigger rate?
- Extended thinking: when does it help? When does it hurt (token usage)?
- Optimal conversation length before quality degrades — is 20-30 messages the real limit?

Sources to check:
- Anthropic docs on Projects: https://support.claude.com (search for "projects" and "knowledge")
- HumanLayer blog on CLAUDE.md: already found, but has more on instruction following
- Community experiments on context usage and skill triggering
- r/ClaudeAI threads on project knowledge optimization

### Track 2: Skill Optimization
**Goal:** Make the 6 skills trigger more reliably and produce better outputs.

Research questions:
- What description patterns maximize trigger rate? (Anthropic says "pushy" — how pushy?)
- Should skills be shorter? Research says "under 500 lines" but is shorter better?
- Can we add validation scripts to skills? (The skill format supports scripts/)
- Should we add example outputs to skills? (Progressive disclosure: examples/ directory)
- How do other complex skill setups structure their progressive disclosure?

Sources to check:
- Anthropic skill-creator skill: https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md
- Trail of Bits claude-code-config: https://github.com/trailofbits/claude-code-config
- Vercel's agent evals findings on skill triggering
- Community skill repositories and marketplace patterns

### Track 3: Claude Code Environment Optimization
**Goal:** Give Claude Code the best possible environment for building KR engines.

Research questions:
- What does the optimal CLAUDE.md look like for a Python pipeline project?
- How to structure test infrastructure so Claude Code gets fast feedback?
- Should we use hooks (pre-commit, pre-push) to enforce quality automatically?
- How to use /batch for running tests across multiple modules?
- Agent teams: viable for KR? What topology? (builder + tester + reviewer?)
- Faber: worth installing? Or overkill for our use case?
- What patterns do successful Claude Code projects use? (dev docs, plan mode, etc.)

Sources to check:
- Anthropic best practices: https://code.claude.com/docs/en/best-practices
- Boris Cherny workflow (Claude Code creator): https://github.com/shanraisshan/claude-code-best-practice
- The C compiler case study: https://www.anthropic.com/engineering/building-c-compiler
- ClaudeFast code kit: patterns for team orchestration
- r/ClaudeCode community patterns and success stories
- Arize CLAUDE.md optimization research

### Track 4: MCP Possibilities
**Goal:** Identify MCPs that could enhance the Claude Chat workflow.

Research questions:
- Can we use a GitHub MCP so Claude Chat can interact with the repo without cloning? (Would this be faster/better than the clone approach?)
- Are there MCPs for test runners, linters, or code quality that Claude Chat could use?
- Scholar Gateway MCP is available — what does it do? Could it help with Islamic studies research?
- Gmail/Calendar MCPs — any use for tracking engine progress or notifications?

Sources to check:
- Anthropic MCP directory
- Scholar Gateway docs
- GitHub MCP servers
- Community MCP recommendations for development workflows

### Track 5: Rate Limit and Cost Management
**Goal:** Ensure the workflow doesn't burn through rate limits.

Research questions:
- What plan is the owner on? Pro? Max? This determines message budget.
- Opus vs Sonnet for different tasks: when is Opus worth the 3x cost?
- How to structure conversations to minimize token consumption?
- Should we use Sonnet for routine spec-review and Opus only for finalization/integrity audits?
- What's the actual token cost of a typical comment-handling session?

Sources to check:
- Anthropic pricing and limits docs
- Community reports on actual usage patterns
- Token counting experiments

### Track 6: Learning From Others
**Goal:** Find production-grade Claude workflows people have shared.

Sources to search:
- r/ClaudeCode: search for "workflow", "production", "pipeline", "architecture"
- r/ClaudeAI: search for "projects", "skills", "custom instructions", "workflow"
- GitHub: repositories with sophisticated CLAUDE.md and skill setups
- Blog posts from teams using Claude for large-scale projects
- The "awesome-claude" lists and community resources

Specific things to look for:
- How do people handle multi-session continuity?
- What patterns exist for owner/architect → Claude workflow (our exact use case)?
- How do teams manage quality across multiple Claude sessions?
- What mistakes do people commonly make with Claude projects?

---

## Research Process

Each track should produce:
1. **Findings document** committed to `skills/research/track-N-findings.md`
2. **Skill updates** if findings suggest changes to any skill
3. **Architecture updates** if findings suggest workflow changes
4. **Open questions** that need owner input or experimentation

**Priority order:** Track 1 (understand the tool) → Track 2 (improve the skills) → Track 3 (prepare for building) → Track 6 (learn from others) → Track 4 (MCPs) → Track 5 (costs)

Track 1 is highest priority because it may change assumptions that affect everything else (e.g., if RAG means we should upload more project knowledge files, that changes the whole setup).

---

## How to Continue This Research

Start a new Claude Chat in the KR project (or this project). Say something like:

"Clone the repo and read skills/RESEARCH_AGENDA.md. Let's work on Track 1: Claude Chat mechanics."

Claude will clone, read the agenda, and continue the research. Each track can be one or more chat sessions. Findings get committed to the repo for continuity.
