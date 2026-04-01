# Environment Hardening Session — Definitive Fix

## What This Session Must Accomplish

**Goal:** Make the KR development environment so robust that CC behavior failures NEVER happen again. Every recurring problem identified across 30+ sessions must be permanently fixed through enforcement hooks, automated checks, and structural constraints — NOT through prose rules that CC forgets.

**Why this matters:** The owner has corrected the same mistakes 4+ times. Each time, CC adds a memory entry or a rule file, but the correction doesn't stick because CC's context compacts, sessions change, and prose rules get forgotten. The pipeline produces Islamic scholarly knowledge — errors in CC's behavior propagate into the owner's understanding. An environment failure IS a knowledge integrity failure.

**Success criterion:** After this session, a BRAND NEW CC session that has NEVER seen the KR project should be able to read CLAUDE.md + NEXT.md + the rules directory and operate perfectly — dispatching coworkers, leading proactively, never asking the owner technical questions, never presenting single-model conclusions as final.

---

## The Problem: Evidence-Based Failure Catalog

### Failure Pattern 1: Multi-Model Dispatch (CRITICAL — 4 corrections in 2 days)

**What happens:** CC completes analysis solo and presents conclusions without dispatching coworkers. The owner catches gaps that coworkers would have found.

**Feedback entries:** `feedback_multi_model_review.md`, `feedback_full_team_always.md`, `feedback_always_max_dispatch.md`, `feedback_codex_reviewer.md`

**Current enforcement:** ZERO. Three rule files exist (`.claude/rules/mandatory-coworker-dispatch.md`, `.claude/rules/no-single-model-conclusion.md`, `.claude/rules/coworker-dispatch.md`) but they are prose. No hook, no automation, no CLI reminder.

**Required fix:** A mechanism that makes it IMPOSSIBLE to present a major conclusion without coworker dispatch. Options: pre-commit hook that checks dispatch_log.jsonl, session-start hook that reminds, stop-hook that blocks response if major analysis detected without dispatch evidence.

### Failure Pattern 2: Passive Leadership (CRITICAL — 3 corrections)

**What happens:** CC completes a task, reports results, then stops with "Want me to proceed?", "Ready when you are", or similar. The owner has to drive what happens next.

**Feedback entries:** `feedback_proactive_leadership.md`, role-definition.md rule

**Current enforcement:** `.claude/rules/post-milestone-protocol.md` exists (created this session) but is prose only.

**Required fix:** A session-level enforcement that CC's response after any major task MUST contain a "Next Steps" section with proposed actions. Possibly a stop-hook pattern that blocks responses ending without forward-looking content.

### Failure Pattern 3: DR Repo Access Confusion (HIGH — explicit "NEVER again")

**What happens:** CC writes relay prompts for ChatGPT DR or Claude DR that paste full file contents instead of giving file paths. Wastes the owner's time.

**Feedback entries:** `feedback_dr_repo_access.md`

**Current enforcement:** `.claude/rules/dr-dispatch-checklist.md` exists (created this session) but is prose only.

**Required fix:** The dispatch skill template itself should be self-documenting — when CC invokes the coworker-dispatch skill, the template should include the access note inline so CC sees it AT THE MOMENT of writing the prompt.

### Failure Pattern 4: Planning Gaps the Owner Catches (CRITICAL — this session)

**What happens:** CC produces a plan or workflow with missing steps, undefined transitions, or unassigned ownership. The owner — who has zero technical skills — catches the gap before CC does.

**Evidence:** This session's audit found 47 gaps in NEXT.md, including undefined phase transitions, missing exit conditions, no error handling, and unclear ownership.

**Required fix:** A "plan completeness checklist" that CC must run against any plan or NEXT.md update BEFORE committing. The checklist verifies: every phase has exit condition, every step has owner, every transition has a checklist, error handling exists for every failure mode.

### Failure Pattern 5: Stale References (MEDIUM — recurring)

**What happens:** File paths, SPEC section numbers, or agent configurations reference files that have been renamed or moved. Example: `engines/5_excerpting/SPEC.md` was stale in 4 files.

**Required fix:** A periodic audit hook or pre-commit check that validates all file path references in `.claude/` files actually exist.

---

## Scope of Work for This Session

### Phase 1: Deep Research (2-3 hours)

1. **Read ALL configuration files:**
   - Every file in `.claude/rules/` (currently ~20 files)
   - Every file in `.claude/agents/` (currently ~20 files)
   - Every file in `.claude/skills/` (currently ~15 skills)
   - Every file in `.claude/hooks/` (currently ~5 hooks)
   - Every file in `.claude/commands/` (currently ~15 commands)
   - `CLAUDE.md` (project rules)
   - `NEXT.md` (current plan)
   - `.claude/settings.json` (hook configuration)

2. **Read ALL feedback memory:**
   - Every `feedback_*.md` in memory directory
   - `principles.md` if it exists
   - Identify which corrections are STILL not enforced

3. **Research best practices:**
   - Dispatch to ChatGPT DR: "What are the best patterns for enforcing AI agent behavior in long-running projects? How do other projects handle agent compliance, role enforcement, and automated quality gates?"
   - Dispatch to Claude DR: "Read the KR .claude/ directory. What structural weaknesses exist in the current hook/rule/agent architecture? What patterns from other Claude Code projects would prevent the recurring failures?"
   - Dispatch to Gemini DR: "Analyze the KR project's .claude/ configuration for completeness and robustness. What is missing compared to a production-grade AI engineering project?"

4. **Audit every hook:**
   - What hooks exist in settings.json?
   - What do they check?
   - What gaps remain?
   - Which failure patterns have NO hook coverage?

### Phase 2: Design (2-3 hours)

5. **Design the enforcement architecture:**
   - For EACH of the 5 failure patterns: design a specific automated enforcement mechanism
   - Consider: hooks (PreToolUse, PostToolUse, stop_hook, pre-commit), rules (always loaded), skills (invoked on demand), commands (owner-triggered), agents (dispatched)
   - Each mechanism must be TESTED — describe how to verify it works

6. **Dispatch coworkers for design review:**
   - Codex: validate hook configurations are syntactically correct
   - Gemini CLI: review Arabic-specific checks in hooks
   - At least one DR: validate the overall architecture

### Phase 3: Implementation (3-4 hours)

7. **Implement ALL enforcement mechanisms**
8. **Test each mechanism** by triggering the failure pattern and verifying the hook catches it
9. **Update CLAUDE.md, NEXT.md, and all supporting docs** to reflect the new enforcement

### Phase 4: Verification (1-2 hours)

10. **Run the harness audit:** `/harness-audit` to check for orphaned hooks, broken references
11. **Dispatch ALL 6 coworkers** to review the final environment for gaps
12. **Produce a verification report** documenting: each failure pattern, the enforcement mechanism, the test result

---

## Files the New Session Must Read First

```
CLAUDE.md                                    — project rules (13 critical rules)
NEXT.md                                      — current plan with 47-gap audit context
.claude/settings.json                        — current hook configuration
.claude/rules/*.md                           — ALL rules (especially the 3 new enforcement rules)
.claude/hooks/*.sh                           — ALL hooks
.claude/agents/*.md                          — ALL agent definitions
.claude/skills/coworker-dispatch/SKILL.md    — dispatch protocol
docs/environment_hardening_session_handoff.md — THIS FILE
```

## Memory Files the New Session Must Read

```
feedback_full_team_always.md       — 6-source dispatch requirement
feedback_proactive_leadership.md   — leadership, not waiting
feedback_dr_repo_access.md         — DR access capabilities
feedback_codex_reviewer.md         — mandatory Codex+Gemini at every major point
```

---

## Coworker Prompts to Prepare

The new session should dispatch these prompts (via owner relay) BEFORE designing solutions:

### ChatGPT DR Prompt
> Read the `rayanino/kr` repository's `.claude/` directory (rules, hooks, agents, skills, settings.json, commands). Also read `CLAUDE.md` and `docs/environment_hardening_session_handoff.md`. The project has 5 recurring CC behavior failures documented in the handoff. Design an enforcement architecture that makes these failures IMPOSSIBLE through automated hooks, not prose rules. For each failure pattern, propose: (a) the specific hook type and trigger, (b) the check logic, (c) how to test it, (d) edge cases where it might false-positive. Output a complete enforcement architecture blueprint.

### Claude DR Prompt
> Read `rayanino/kr/.claude/` directory and `CLAUDE.md`. Focus on the gap between INTENDED behavior (what rules say) and ACTUAL behavior (what the feedback memory entries show CC actually does). For each gap: (a) why does the prose rule fail? (b) what structural change would make it succeed? (c) is the rule itself correct, or does it need revision? Also audit the agent definitions for role clarity — do any agents create ambiguity about who decides what?

### Gemini DR Prompt (file upload)
Upload: `.claude/settings.json`, `.claude/rules/mandatory-coworker-dispatch.md`, `.claude/rules/post-milestone-protocol.md`, `.claude/rules/dr-dispatch-checklist.md`, `CLAUDE.md`, all `.claude/hooks/*.sh` files, and this handoff document.
> Evaluate this AI agent environment configuration for production-grade robustness. Compare against best practices for long-running AI-assisted engineering projects. Identify: (a) what enforcement mechanisms are missing, (b) what hooks exist but are incomplete, (c) what new hook types should be added, (d) whether the rule/hook/agent/skill architecture is the right design or needs restructuring.

---

## Non-Negotiable Constraints for the New Session

1. **No prose-only solutions.** Every fix must have automated enforcement (hook, check, validation).
2. **Every change must be tested.** Show the test: trigger the failure, verify the hook catches it.
3. **Coworkers must review the design BEFORE implementation.** Minimum 3 sources agree.
4. **The owner is NEVER asked to validate technical correctness.** The owner can be asked: "Does this session's work feel complete to you?" — an experience question, not a technical one.
5. **All changes are committed and pushed before the session ends.**
6. **A verification report is produced as the final artifact.**
