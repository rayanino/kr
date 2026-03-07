# Open Problems — المشاكل المفتوحة

These are the problems that must be solved before engine building begins. Each task is scoped for ONE chat session. Do them in order within each workstream. Workstream A should be done first.

---

## Workstream A: Repo Cleanup (do this FIRST — everything else depends on it)

The repo has 38+ markdown files. Many are artifacts from autonomous sessions that over-planned (HONEST_PLAN.md calls this out directly). You've lost track of what's what. Before optimizing anything, we need a clean foundation.

### Task A1: Full Repo Audit

**Goal:** Produce a definitive inventory of every file, what it does, whether it's still needed, and what's redundant.

**What to do in this chat:**
1. Clone the repo
2. Read every root-level .md file (22 files, ~6000 lines) and every reference/ .md file (16 files, ~5500 lines)
3. For each file: what is it, is it current, does it duplicate another file, is it still needed
4. Identify groups of files that overlap (e.g., IMPLEMENTATION_GUIDE + IMPLEMENTATION_GATE + REVIEW_PROTOCOL all seem to govern the same thing)
5. Produce a verdict per file: KEEP / ARCHIVE / MERGE INTO X / DELETE
6. Identify what's MISSING (e.g., the testing architecture has no dedicated document)

**Output:** A `REPO_AUDIT.md` with the file-by-file verdict and a proposed clean structure.

**Key context:** Read `reference/HONEST_PLAN.md` first — it already criticizes the over-planning. Read `reference/REPO_INVENTORY.md` for a previous attempt at inventory (may be outdated).

---

### Task A2: Execute the Cleanup

**Goal:** Reorganize the repo based on the audit.

**What to do in this chat:**
1. Read the REPO_AUDIT.md from Task A1
2. Move archived files to `reference/archive/`
3. Merge overlapping files where the audit recommends it
4. Update cross-references in surviving files
5. Verify nothing is broken (no dead links, no missing references)
6. Update STEERING.md if the file map changed
7. Update skills/README.md and ENGINE_PROTOCOL.md if paths changed

**Output:** Clean repo. Updated STEERING.md with current file map.

**Depends on:** Task A1 completed.

---

## Workstream B: Claude Chat Environment

How to set up each engine's Claude Chat project for maximum effectiveness.

### Task B1: Research Claude Chat Project Optimization

**Goal:** Deep research into how people run complex multi-session Claude Chat projects.

**What to do in this chat:**
1. Research Reddit (r/ClaudeAI, r/ClaudeCode), blogs, and Anthropic docs for:
   - Optimal project knowledge strategies (what to include, what hurts)
   - Custom instruction patterns that work vs. fail
   - How people manage state across sessions in projects
   - Context degradation patterns and how to delay them
   - Memory features in projects (auto-synthesized memory summaries)
   - Skill interaction with project context
2. Test: does GitHub integration + skills + custom instructions actually work smoothly together?
3. Identify any conflicts or limitations not in the official docs

**Output:** Research findings document with concrete recommendations for KR project setup.

**Key context:** Read `skills/handoffs/claude-chat-research-2026-03-07.md` for research already done. This task goes DEEPER on the project setup specifically.

---

### Task B2: Design the Per-Engine Project Template

**Goal:** Define exactly what goes into each engine's Claude Chat project — files, instructions, knowledge.

**What to do in this chat:**
1. Based on B1 research, design the template:
   - Custom instructions (exact text, optimized for the role)
   - Which repo files to sync via GitHub integration per engine
   - What NOT to include (and why)
   - How to configure skills for the project
   - When to sync, when to handoff, when to start fresh
2. Create the template for the source engine (first real test case)
3. Produce a setup checklist the owner can follow in 10 minutes

**Output:** `skills/shared/PROJECT_TEMPLATE.md` + source engine setup checklist.

**Depends on:** Task A2 (clean repo) + Task B1 (research).

---

## Workstream C: Claude Code Environment

How to set up Claude Code for maximum build quality. Agent teams, memory, orchestration.

### Task C1: Research Claude Code Setups for Complex Projects

**Goal:** Deep research into how people configure Claude Code for serious multi-session building.

**What to do in this chat:**
1. Research extensively:
   - Agent team architectures people actually use in production (not demos)
   - CLAUDE.md patterns that work at scale (the 200-line limit, what to put in vs. out)
   - Memory and context persistence tools (memory MCPs, CLAUDE.md patterns, session handoff)
   - Hooks that improve quality (pre-commit validation, test-on-save, lint-on-change)
   - How people handle the "Claude Code forgets the plan mid-session" problem
   - Cost management strategies (when to use Opus vs. Sonnet, token budgeting)
   - The /compact command, auto-compaction, and context management
   - Custom slash commands that help
2. Look at real repos: claude-code-tips (ykdojo), ClaudeFast, awesome-claude-code
3. Find patterns specific to Python + Pydantic + pytest projects (our stack)

**Output:** Research findings with ranked recommendations for KR.

**Key context:** Read `reference/RESEARCH_LOG.md` findings 01, 05, 08 for existing research. This task goes much deeper on the Claude Code side specifically.

---

### Task C2: Design the KR Claude Code Environment

**Goal:** Define the exact CLAUDE.md, commands, hooks, and agent team templates for KR engine building.

**What to do in this chat:**
1. Based on C1 research, design:
   - The CLAUDE.md template for KR engines (under 200 lines, with what goes in docs/)
   - Custom slash commands (/test, /check-spec, /handoff, etc.)
   - Hooks for quality (run tests after file changes, lint on save, etc.)
   - Agent team compositions for different build phases
   - Session management strategy (when to /compact, when to start fresh)
   - The dev docs pattern (plan.md, context.md, tasks.md per session)
2. Produce a concrete, ready-to-use setup for the source engine

**Output:** `engines/source/CLAUDE.md` + `engines/source/docs/` + slash commands + hooks config.

**Depends on:** Task A2 (clean repo) + Task C1 (research).

---

### Task C3: Design the Agent Team Strategy for KR

**Goal:** Define when and how to use agent teams vs. single sessions vs. worktrees for each engine.

**What to do in this chat:**
1. For each of the 7 engines, assess:
   - How complex is the build? (source engine: high. passaging: medium. etc.)
   - What's the natural team composition? (builder/tester/reviewer? format specialists?)
   - At what session number does parallelism become valuable?
   - What's the cost estimate per engine?
2. Design team templates that can be copy-pasted into Claude Code
3. Define the escalation path: single session → worktrees → agent teams
4. Address the "agent teams are ephemeral" problem — how to carry state between team sessions

**Output:** Agent team playbook as part of kr-build-prep skill or standalone doc.

**Depends on:** Task C1 (research).

---

## Workstream D: Testing Architecture

The most critical workstream. How engines get tested, how results are stored, how trust is established.

### Task D1: Research Testing Architectures for LLM Pipelines

**Goal:** Deep research into how people test LLM-based pipelines, specifically multi-stage ones.

**What to do in this chat:**
1. Research:
   - RAGAS framework (faithfulness, context relevance, answer relevancy) — how to apply to KR
   - How people test LLM calls in isolation (5b: is THIS specific LLM call reliable?)
   - How people test LLM-as-judge reliability (5c: can you trust the evaluator?)
   - Inter-stage validation patterns (output of stage N validated before entering stage N+1)
   - Test result storage formats that enable both automated analysis and human review
   - Regression testing strategies for LLM-based systems (outputs aren't deterministic)
   - Gold baseline / ground truth creation for Arabic scholarly content
   - Cost-effective testing (cascaded: cheap model first, expensive only for uncertain cases)
2. Look at: RAGAS, DeepEval, Phoenix (Arize), LangSmith, and any Arabic-specific evaluation tools
3. Find examples of real multi-stage pipeline testing (not just single-model evaluation)

**Output:** Research findings with framework recommendation for KR.

**Key context:** Read `reference/RESEARCH_LOG.md` findings 02, 03, 11 for existing research. Read `reference/JUDGE_PANEL_ARCHITECTURE.md` for the multi-model panel design. Read `reference/HONEST_PLAN.md` for the 5a/5b/5c framework.

---

### Task D2: Design the 5a Deterministic Test Framework

**Goal:** Define exactly what deterministic tests each engine needs and how they're structured.

**What to do in this chat:**
1. For each of the 7 engines, enumerate:
   - What schema checks apply (Pydantic validation against contracts.py)
   - What text integrity checks apply (Arabic preservation, diacritics)
   - What metadata checks apply (D-023 pass-through, completeness)
   - What referential integrity checks apply (ID resolution, cross-references)
   - What boundary contract checks apply (output matches downstream's input)
2. Design the test runner: how tests are invoked, how results are stored, what the report format looks like
3. Define the fixtures strategy: what test sources exist, what's missing, what ground truth the owner needs to provide

**Output:** `reference/TESTING_5A.md` with per-engine test specifications.

**Depends on:** Task D1 (research) + Task A2 (clean repo).

---

### Task D3: Design the 5b LLM-as-Worker Isolation Testing

**Goal:** Define how to test each engine's internal LLM calls in isolation.

**What to do in this chat:**
1. For each engine, identify every LLM call:
   - Source: science classification, author identification, school detection, trust scoring
   - Normalization: format detection, structure inference
   - Passaging: boundary evaluation
   - Atomization: boundary detection, scholarly function classification
   - Excerpting: self-containment evaluation, attribution detection, implicit reference resolution
   - Taxonomy: placement scoring
   - Synthesis: entry generation (this IS the LLM call)
2. For each LLM call, define:
   - What is the correct answer? (ground truth source — owner, known fixture, or consensus)
   - How to test it in isolation (input/output, without running the full engine)
   - What accuracy threshold is acceptable
   - What to do when the LLM fails (retry? different model? escalate to human?)
3. Design the isolated LLM test harness

**Output:** `reference/TESTING_5B.md` with per-engine, per-LLM-call test specifications.

**Depends on:** Task D1 (research).

---

### Task D4: Design the 5c LLM-as-Evaluator and Inter-Engine Gate

**Goal:** Define how independent LLM evaluation works and whether it becomes a production gate.

**What to do in this chat:**
1. Design the evaluation protocol:
   - Which model(s) serve as independent evaluators (different from the engine's own models)
   - What prompts/rubrics the evaluator uses per engine
   - How to measure evaluator reliability (does it agree with human judgment?)
   - How to handle evaluator disagreement with the engine (who's right?)
2. Design the inter-engine gate experiment:
   - For each engine pair: what does the gate check before passing output downstream?
   - How to measure whether the gate catches errors self-validation missed
   - Cost/benefit framework: is the gate worth its token cost?
3. Design the multi-model panel for synthesis (the only engine where full panel is needed from day 1)
4. Define how evaluation results are stored for Claude Chat consumption

**Output:** `reference/TESTING_5C.md` with evaluation protocol and inter-engine gate design.

**Depends on:** Task D1 (research) + Task D3 (know what LLM calls exist).

---

### Task D5: Design the Test Result Storage and Reporting Format

**Goal:** Define how test results flow from Claude Code to Claude Chat to the owner.

**What to do in this chat:**
1. Design the storage format:
   - Directory structure: `engines/{engine}/test-results/{run-id}/`
   - File format for 5a results (structured, machine-readable)
   - File format for 5b results (per-LLM-call accuracy reports)
   - File format for 5c results (evaluator findings with severity)
   - Summary file format (what Claude Chat reads first)
2. Design the reporting flow:
   - Claude Code writes results → owner opens Claude Chat → "use kr-evaluate"
   - What does Claude Chat need to see to produce the error categorization?
   - What does the owner need to see for spot-checking?
   - How are results tracked across multiple test runs? (improvement tracking)
3. Define the trust graduation criteria in concrete, measurable terms

**Output:** `reference/TESTING_RESULTS.md` with storage format and reporting design.

**Depends on:** Tasks D2, D3, D4 (know what results exist).

---

## Suggested Order

```
WEEK 1: Foundation
  A1 → A2          (repo cleanup — clears the ground)

WEEK 2: Research
  B1, C1, D1        (can be done in parallel — all are research)

WEEK 3: Design
  B2, C2, D2, D3    (can be partially parallel)

WEEK 4: Design continued
  C3, D4, D5        (depends on earlier design tasks)
```

This is a suggestion, not a mandate. The owner sets the pace. The only hard rule: A1 and A2 must come first.

---

## How to Start Each Chat

Open a new chat in this project. Say:

> "Clone the repo. Read `OPEN_PROBLEMS.md`. I'm working on Task [X]. Read the task description and the files it references, then let's begin."

Claude will clone the repo, read this file, read the referenced context files, and start working on the task.

When a task is complete, update this file: change the task status to DONE and note the output file produced.

---

## Task Status Tracker

| Task | Status | Output | Date |
|------|--------|--------|------|
| A1 | TODO | — | — |
| A2 | TODO | — | — |
| B1 | PARTIAL | `skills/handoffs/claude-chat-research-2026-03-07.md` | 2026-03-07 |
| B2 | TODO | — | — |
| C1 | TODO | — | — |
| C2 | TODO | — | — |
| C3 | TODO | — | — |
| D1 | TODO | — | — |
| D2 | TODO | — | — |
| D3 | TODO | — | — |
| D4 | TODO | — | — |
| D5 | TODO | — | — |
