# Deep Research — Claude Chat Optimization for KR

Date: 2026-03-07
Researcher: Claude (via Claude Chat with computer use)
Purpose: Investigate all 6 research areas from the handoff document before the owner starts real SPEC review work.

---

## FINDING 1: Claude.ai Has a Native GitHub Integration — Our Clone Approach May Be Redundant

**Source:** Anthropic Help Center, Claude docs

**What exists:**
- Claude.ai projects support **direct GitHub repo syncing** via a built-in integration.
- You connect your GitHub account, select a repo, and choose specific files/folders to include in project knowledge.
- A "Sync now" button fetches the latest changes from the repo at any time.
- A "Configure files" option lets you select which files Claude sees.
- Supports private repos (requires GitHub App installation).
- Multiple repos can be added to one project.
- Only files and contents on a specific branch are synced — no commit history, no PRs, no other metadata.

**Implications for KR:**
Our current approach clones the repo via `git clone --depth 1` at the start of every chat. This works but has drawbacks:
- Consumes ~4 seconds per chat start
- Requires the GitHub token in project knowledge
- Requires the STARTUP PROCEDURE in custom instructions (uses instruction budget)
- If clone fails (outage, token expiry), the chat is crippled
- Claude can read but pushing changes back is fragile in Claude Chat (no git identity configured)

The native GitHub integration would:
- Eliminate the clone step entirely
- Eliminate the GitHub token from project knowledge
- Automatically load selected files into project knowledge
- Allow manual sync when the repo changes
- Be more reliable (Anthropic-managed infra vs. our bash clone)
- Work with RAG if file count gets large

**BUT there are known issues:**
- A bug report from Oct 2025 described GitHub sync being broken for ~2 weeks (files not accessible despite "Connected" status). The issue was eventually resolved.
- Sync is one-way read-only. Claude Chat cannot push changes back to GitHub. (Our clone approach has the same limitation in practice — Claude Chat's git push is unreliable.)
- The integration syncs file CONTENTS only — no commit history, no issue tracking.

**Recommendation:** 
SWITCH to native GitHub integration for reading repo files. Keep the clone command as a FALLBACK in custom instructions, only used when the owner says "clone the repo" or when GitHub sync is down. This simplifies the startup procedure significantly.

**What the owner needs to do:**
1. Go to Claude.ai project settings
2. Click "+" in project knowledge → Add from GitHub
3. Authenticate with GitHub if not already
4. Select `rayanino/kr` repo
5. Configure files: select the specific files/folders needed per engine project (e.g., for source engine: `engines/source/`, `reference/DOMAIN.md`, `reference/ENTRY_EXAMPLE.md`, `STEERING.md`, `KNOWLEDGE_INTEGRITY.md`, `skills/shared/`, `NEXT.md`)
6. Keep GitHub_key in project knowledge as fallback only

---

## FINDING 2: Project Knowledge — RAG vs. In-Context Loading

**Source:** Anthropic Help Center, multiple blog analyses

**How it actually works (confirmed by Anthropic docs):**
- For **small** projects (knowledge fits in context window): files are loaded in full, directly into context. Claude sees every word.
- For **larger** projects (approaching ~200K token limit): Claude **automatically switches to RAG mode**. In RAG mode, Claude uses a "project knowledge search" tool to retrieve only the most relevant sections.
- RAG provides ~10x effective capacity compared to in-context loading.
- There is a visual indicator when RAG is enabled.
- If project knowledge drops below the context threshold, it switches back to in-context processing.

**Implications for KR:**
- With the GitHub integration, if we selectively sync only the files needed for one engine, we stay well within in-context limits. This is BETTER than RAG because Claude sees everything.
- STEERING.md (~4K tokens) + one engine SPEC (~15-25K tokens) + KNOWLEDGE_INTEGRITY.md (~10K) + reference files (~30-50K) = roughly 60-90K tokens of project knowledge. This leaves 110-140K tokens for conversation — excellent.
- If we dump the entire repo into project knowledge, it would trigger RAG mode. This is WORSE for our use case because Claude might miss relevant sections during retrieval.

**Recommendation:**
Keep project knowledge LEAN. Use selective file sync from GitHub. One project per engine, each syncing only the files that engine needs. This keeps us in in-context mode (no RAG), maximizing Claude's comprehension.

---

## FINDING 3: Skills in Claude.ai — How They Actually Work

**Source:** Anthropic Help Center (official docs, updated 2026)

**Key facts confirmed:**
- Skills are available on free, Pro, Max, Team, and Enterprise plans.
- Skills **require code execution to be enabled** in Settings > Capabilities.
- Skills are uploaded as `.zip` files containing at minimum a `SKILL.md` file.
- The SKILL.md MUST start with YAML frontmatter containing `name` and `description` fields.
- `description` has a **200 character maximum** — this is what Claude uses to decide whether to activate the skill.
- Skills use **progressive disclosure**: Claude reads metadata first (name + description), then loads the full SKILL.md body only if the skill appears relevant.
- Additional reference files can be included in the zip alongside SKILL.md.
- Skills work **everywhere** — in regular chats AND inside Projects.
- Claude shows "Using [skill name]" in its thinking when a skill activates.

**Skills-related outage (Feb 17-24, 2026):**
- Anthropic's status page shows a 7-day incident: "Intermittent errors in skills-related functionality" affecting claude.ai, Claude Desktop, and API.
- Identified Feb 17, resolved Feb 24. This is recent and suggests skills infrastructure is still maturing.

**Triggering reliability:**
- Multiple independent sources (Vercel research, community reports, blog analyses) confirm skills trigger unreliably — estimates range from 44-60% auto-activation rate.
- The official Anthropic skill-creator tool now includes **description tuning** to improve trigger accuracy.
- Best practices for reliable triggering:
  1. Description must be "stupidly specific" — use exact keywords, phrases, and context
  2. Add explicit activation reinforcement in description (e.g., "Always activate when...")
  3. Keep descriptions laser-focused on WHEN to trigger, not what the skill does
  4. Can also explicitly invoke by name: "use kr-spec-review" in the prompt
  
**Impact on KR skills:**
Our 6 skills have descriptions that are good but could be more aggressive. The 200-char limit is tight. Let me check our current descriptions:

| Skill | Current Description | Chars |
|-------|-------------------|-------|
| kr-spec-review | "Handle owner comments on KR engine SPECs — treat each comment as a research hypothesis requiring deep investigation. Use for "handle comment", "comment #N", domain feedback, or any SPEC discussion." | ~195 |
| kr-finalize | (need to check) | — |
| kr-build-prep | (need to check) | — |
| kr-evaluate | (need to check) | — |
| kr-research | (need to check) | — |
| kr-integrity | (need to check) | — |

**Recommendation:**
1. Verify all 6 skill descriptions are within 200 chars and use the most trigger-reliable language
2. The owner should always explicitly invoke skills by name when possible ("use kr-spec-review for comment #3") rather than relying on auto-activation
3. Add activation reinforcement phrases where possible
4. Consider adding reference files for progressive disclosure in complex skills

---

## FINDING 4: Context Management Strategies

**Source:** Multiple (Anthropic best practices, community patterns, blog analyses)

**Key principles for Claude Chat projects:**
1. **Keep project instructions concise.** Anthropic explicitly says Claude performs best with concise project instructions focused on: general context, key guidelines, Claude's role.
2. **Context quality > context quantity.** Research consistently shows performance degrades as context fills. The "lost in the middle" problem means information in the middle of a large context gets overlooked.
3. **Automatic context management exists.** When conversations get long, Claude Chat automatically compacts earlier portions (~85% payload reduction at ~83.5% context usage). This triggers only with code execution enabled. Trade-off: specific details, exact numbers, and precise wording can be lost.
4. **Project-scoped memory.** Since late 2025, each Claude project maintains its own memory summary that auto-synthesizes roughly every 24 hours. This is separate from account-level memory.

**Implications for KR:**
- Our custom instructions (~150 lines) are within good practice range.
- The STARTUP PROCEDURE section can be significantly shortened if we use native GitHub sync.
- The skills mentioned in custom instructions are good — they remind Claude what tools are available.
- For long SPEC review sessions, the owner should proactively handoff (using our HANDOFF_PROTOCOL) BEFORE context degradation, not after.
- Code execution MUST be enabled for automatic context management and for skills to work.

**Revised custom instructions strategy:**
```
Current: ~150 lines including STARTUP PROCEDURE (clone repo, read files)
Proposed: ~100 lines. Remove clone procedure. Add: "Your project knowledge 
includes files synced from the GitHub repo. If you need a file not in project 
knowledge, ask the owner to sync it, or use the fallback clone command."
```

---

## FINDING 5: MCP Servers for Claude Chat

**Source:** GitHub MCP docs, Anthropic docs, community resources

**Critical distinction: Claude Chat vs Claude Code MCPs.**
- **Claude Code** supports arbitrary MCP servers via `claude mcp add` (local stdio or remote HTTP).
- **Claude Chat** (claude.ai web) supports MCPs via "connectors" in Settings. The available connectors are more limited and curated.
- The GitHub MCP server exists and is official (github/github-mcp-server on GitHub), but it's primarily designed for Claude Code and Claude Desktop, not Claude Chat web.
- Claude Chat's GitHub integration (Finding 1) is the web-equivalent — it's not MCP-based, it's a native integration.

**MCPs that could matter for KR in Claude Code (future building phase):**
- **GitHub MCP** — full repo management (create PRs, manage issues, read files)
- **Filesystem MCP** — read/write local files (already available via Claude Code natively)
- **Desktop Commander MCP** — terminal control + file editing (useful for autonomous loops)

**MCPs that matter for Claude Chat (current SPEC review phase):**
- **Honestly: none.** The native GitHub integration + skills cover our needs.
- The GitHub MCP would be overkill for Claude Chat — it's designed for programmatic repo manipulation, which we don't need during SPEC review.

**What about DesktopCommander MCP?**
- Impressive capabilities (terminal, file system, remote access from web)
- But: "context hogs" — the GitHub MCP alone can consume hundreds of thousands of tokens
- For SPEC review work, this overhead isn't justified

**Recommendation:**
- For the current phase (SPEC review via Claude Chat): use native GitHub integration, no MCPs needed.
- For the building phase (Claude Code): configure GitHub MCP for automated PR creation and issue management. This is where MCP becomes valuable.

---

## FINDING 6: Claude Chat → Claude Code Transition

**Source:** Community practices, Anthropic docs, blog posts

**The current state of the art:**
- Claude Chat and Claude Code are separate tools with no automatic state transfer.
- The community pattern is: use Claude Chat for planning/design, use Claude Code for implementation.
- The bridge between them is **files in the repo** — Chat produces docs, Code reads them.
- Our `kr-build-prep` skill already handles this correctly: it produces CLAUDE.md, plan.md, context.md, tasks.md that Claude Code reads.

**Best practices gathered:**
1. **CLAUDE.md is the bridge.** Both Chat and Code read it. Keep it under 200 lines (confirmed by multiple sources including HumanLayer research). Claude Code's system prompt uses ~50 lines, so CLAUDE.md gets ~150 lines of real estate.
2. **Session docs pattern.** Each Claude Code session should have its own plan.md/context.md/tasks.md. This prevents context pollution across sessions.
3. **Branch-based handoff.** Chat works on a branch, Code picks it up. This gives clean separation.
4. **Git worktrees** for parallel Claude Code sessions (discovered: `claude -w feature-name` creates isolated worktrees automatically in Claude Code).

**What this means for KR:**
Our `kr-build-prep` skill already follows best practices. The gap is:
- We don't specify a branch workflow. Recommendation: Chat pushes to `spec-review/{engine-name}`, Code works on `build/{engine-name}`, both merge to `main`.
- We should ensure CLAUDE.md in the repo stays concise. Current CLAUDE.md is 2.5K — need to check line count.

---

## FINDING 7: Known Issues and Risks

### 7a: Skills outage history
The Feb 17-24, 2026 skills outage (7 days!) is concerning. Skills-related functionality had "intermittent errors" across claude.ai, Desktop, and API. This means our skills could become unavailable at any time.

**Mitigation:** The custom instructions should contain the ESSENTIAL behavioral rules (anti-sycophancy, research mandate, domain deference) that skills reinforce. Skills add detailed procedures; custom instructions set the baseline that works even if skills are down.

### 7b: GitHub sync reliability
At least one significant bug report (Oct 2025) showed GitHub sync breaking for weeks. Files showed "Connected" but content was inaccessible.

**Mitigation:** Keep the manual clone fallback in custom instructions. If the owner notices Claude can't access repo files, they can say "clone the repo" to trigger the fallback.

### 7c: Context rot in long conversations
Multiple sources confirm accuracy degrades as conversations lengthen. Automatic compaction helps but loses detail.

**Mitigation:** Our HANDOFF_PROTOCOL already addresses this. The owner should be briefed: "When responses start getting less precise, or after ~15 substantive exchanges, start a new chat."

### 7d: Claude Chat rate limits  
Pro plan has a usage multiplier (5x free tier). During peak times, limits can be hit quickly. The March 2, 2026 outage (~12 hours) shows Claude.ai itself can go down.

**Mitigation:** No technical fix. The owner should know that peak hours (US business hours) may have slower responses or limits. Evening/night work (Belgium time) typically has better availability.

---

## FINDING 8: Skills Description Optimization

Based on the research, here are optimized descriptions for our 6 skills (max 200 chars):

**Current kr-spec-review:**
> Handle owner comments on KR engine SPECs — treat each comment as a research hypothesis requiring deep investigation. Use for "handle comment", "comment #N", domain feedback, or any SPEC discussion.

This is good but could be more trigger-aggressive. Revised:

> ALWAYS activate for owner SPEC comments. Treat comments as research hypotheses. Triggers: "comment #", "handle comment", domain feedback, SPEC review, owner feedback, "investigate this".

**Assessment of all 6 skills — revision needed?**
The skills were well-written in the last session. The main improvement is ensuring descriptions are maximally trigger-reliable. This can be done in a focused 15-minute pass — not a priority blocker.

---

## SYNTHESIS: Concrete Improvements to Make

### Priority 1 — Switch to Native GitHub Integration (HIGH IMPACT, LOW EFFORT)
- Owner adds rayanino/kr repo to each Claude Chat project via GitHub integration
- Selectively sync relevant files per engine
- Simplify custom instructions (remove clone procedure)
- Keep clone as fallback only

### Priority 2 — Slim Down Custom Instructions (MEDIUM IMPACT, LOW EFFORT)
- Remove STARTUP PROCEDURE section (replaced by GitHub sync)
- Remove GitHub token mention (no longer needed in instructions)
- Net savings: ~20-30 lines of instruction budget
- Reinvest some of that budget into stronger behavioral mandates

### Priority 3 — Verify Skills Setup (MEDIUM IMPACT, LOW EFFORT)
- Ensure code execution is enabled in Settings > Capabilities
- Verify all 6 .zip files uploaded correctly in Customize > Skills
- Test each skill triggers by explicitly invoking it once
- Optimize descriptions if needed (200 char limit)

### Priority 4 — Owner Briefing Document (MEDIUM IMPACT, LOW EFFORT)
- Create a brief "How to Use Your KR Projects" doc explaining:
  - How to sync GitHub files
  - When to start a new chat (context degradation signs)
  - How to explicitly invoke skills
  - Fallback procedure if GitHub sync fails
  - Best hours for Claude availability

### Priority 5 — Branch Workflow for Chat→Code Handoff (LOW IMPACT NOW, HIGH IMPACT LATER)
- Define branch naming convention
- Add to kr-build-prep skill
- Not urgent until building phase begins

---

## DECISION LOG

| Decision | Rationale | Status |
|----------|-----------|--------|
| Use native GitHub sync instead of clone-at-start | More reliable, simpler, no token needed in instructions | RECOMMENDED — needs owner action |
| Keep clone as fallback, not primary | GitHub sync had a multi-week outage in 2025 | RECOMMENDED |
| One project per engine (not per workflow phase) | Each engine needs different files; keeps context lean | CONFIRMED (was already decided) |
| Skills require code execution enabled | Official Anthropic requirement, not optional | CONFIRMED — owner must verify |
| No MCPs needed for SPEC review phase | Native GitHub integration covers our needs | DECIDED |
| GitHub MCP for Claude Code building phase | Enables automated PR creation and issue management | DEFERRED to building phase |
| Owner should explicitly invoke skills by name | Auto-triggering is unreliable (44-60% hit rate) | RECOMMENDED |
| Handoff after ~15 substantive exchanges | Context rot is real and documented | RECOMMENDED |
