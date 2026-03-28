# KR Factory Execution Plan — خطة التنفيذ التفصيلية

**Authority:** Operational guide for executing FACTORY_ROADMAP_v2.md.
**Written:** 2026-03-28
**Principle:** Every micro-task gets its own dedicated chat session. Every build decision has a research gate. Every CC handoff has cross-provider consultation first.

---

## How to Read This Plan

Each roadmap session is decomposed into **micro-tasks (μ-tasks)**. Each μ-task is:
- Assigned to a specific tool (Claude Chat, CC, ChatGPT, Gemini CLI, Owner)
- Given a session type (Planning, Research, Build, Review, Owner-Action)
- Marked with dependencies (what must complete first)
- Given a research gate if it involves a build decision

**Naming convention:** `F1.2` = Factory Session 1, μ-task 2.

**Parallelism:** The "Track" column shows which work stream a μ-task belongs to.
Factory-track and Engine-track can run in parallel (different chat sessions).

---

## Current State (2026-03-28)

| Item | Status |
|------|--------|
| Excerpting NEXT.md | Model role research (Task 1) + 5-book test prep (Task 2) |
| Factory roadmap | v2 committed, adversarially reviewed by 3 sources |
| Paperclip evaluation | EVALUATE_FURTHER (Windows blocked; WSL2 test needed) |
| WSL2 on owner's PC | Unknown — need to check |
| Claude Chat skills | 3 new skills designed (this session), ready to upload |
| CC environment | 19 hooks, 21 agents, 13 skills, 15 rules |

---

## Pre-Flight: Environment Setup (Before Any Factory Session)

### μ-PF.1 — Upload New Claude Chat Skills
- **Tool:** Owner (manual)
- **Track:** Factory
- **Depends on:** This session completing
- **Action:** Upload 4 skill files to Claude project:
  1. `technology-landscape/SKILL.md`
  2. `factory-session/SKILL.md`
  3. `tool-evaluation/SKILL.md`
  4. `critical-review-update/SKILL.md` (replaces existing critical-review)
- **Verify:** `ls /mnt/skills/user/` in next session shows all 4 new skills
- **Duration:** 5 minutes

### μ-PF.2 — Check WSL2 Status
- **Tool:** Owner (check)
- **Track:** Factory
- **Depends on:** Nothing
- **Action:** Open PowerShell, run `wsl --status`. Report whether WSL2 is installed.
  If not installed: `wsl --install` (requires reboot).
- **Duration:** 2-10 minutes (or ~30 min if installing WSL2)

### μ-PF.3 — Excerpting Model Role Research (Parallel)
- **Tool:** Claude Chat (new session)
- **Track:** Engine
- **Depends on:** Nothing (can run NOW, parallel to factory work)
- **Skills:** kr-research, deep-research, thinking-frameworks
- **Action:** Execute NEXT.md Task 1 — research GPT-5.4 vs Gemini 3.1 Pro for verify/escalation roles. Design empirical probe. Produce CC prompt for the probe.
- **Research gate:** 10+ searches on Arabic scholarly text capability per model
- **ChatGPT prompt to prepare:**
  > "Which frontier LLM (Claude Opus 4.6, GPT-5.4, Gemini 3.1 Pro) is best at understanding classical Arabic Islamic scholarly text — specifically matn/sharh/hashiyah structures, isnad chains, tahqiq apparatus? I need evidence from benchmarks, published evaluations, or user reports, not marketing claims. Also: which is best at CATCHING errors in structured extraction (verifier role), vs GENERATING the extraction (primary role)?"
- **Duration:** 1 full session

---

## Phase 1: Foundation (Roadmap Sessions 1-3)

### Session 1 — Operational Truth + Document Reconciliation

#### μ-F1.1 — Technology Landscape Scan: Manifest/Config Management
- **Tool:** Claude Chat (this track's planning session)
- **Track:** Factory
- **Depends on:** μ-PF.1
- **Skills:** factory-session, technology-landscape
- **Research gate:** Are there existing tools for operational manifests / config-as-code for AI agent systems? (10 searches)
- **ChatGPT prompt:**
  > "I need a machine-readable single-source-of-truth file for an autonomous AI factory that tracks: which engine is active, current build phase, work queue, model routing, policy rules with expiration dates, benchmark scores, and human gate backlog. I'm planning to use a JSON file (ops_manifest.json) with a Python validation script. Before I build custom: is there an existing tool or framework for this kind of operational state management for AI agent systems? I'm on WSL2/Ubuntu, using Claude Code + Codex CLI + Gemini CLI."
- **Decision:** Build custom (likely — this is too domain-specific) or adopt.
- **Duration:** 30 min in a planning session

#### μ-F1.2 — Document Reconciliation Audit
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F1.1
- **Action:** Read every `reference/*.md` and `engines/*/CLAUDE.md`. List all stale references to "7 engines," "13 hooks," wrong test counts, or outdated pipeline descriptions. Produce the definitive list of corrections for CC.
- **Duration:** 30 min

#### μ-F1.3 — Prepare CC Handoff for Session 1
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F1.1, μ-F1.2
- **Skills:** kr-preparing-cc-handoffs, critical-review
- **Action:** Write the CC prompt from FACTORY_ROADMAP_v2.md Session 1, amended with:
  - Exact list of stale documents from μ-F1.2
  - ops_manifest.json schema (from μ-F1.1 decision)
  - Corrected hook count (19), agent count (21)
  - Scope control clause
- **Duration:** 30 min

#### μ-F1.4 — CC Builds Session 1
- **Tool:** CC (owner relays prompt)
- **Track:** Factory
- **Depends on:** μ-F1.3
- **Action:** CC creates ops_manifest.json, validate_manifest.py, reconciles documents
- **Duration:** 1 CC session

#### μ-F1.5 — Review CC Session 1 Output
- **Tool:** Claude Chat (NEW session — never review in same chat as handoff)
- **Track:** Factory
- **Depends on:** μ-F1.4
- **Skills:** kr-reviewing-cc-output, factory-session, critical-review
- **Action:** 3-round review per protocol. Factory-specific checks: does manifest schema cover all roadmap needs? Did CC actually fix all stale documents?
- **Exit criteria check:**
  - `python scripts/validate_manifest.py` exits 0
  - `grep -rn "7 engines\|6 remaining\|13 hooks" reference/ engines/ CLAUDE.md` returns nothing
  - Every Playbook rule has provenance fields
- **Duration:** 1 full session (3 rounds with "continue" breaks)

---

### Session 2 — CI/CD + Policies + Hook Fixes

#### μ-F2.1 — Technology Landscape Scan: CI/CD for AI Agent Projects
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F1.5 (Session 1 ACCEPTED)
- **Skills:** factory-session, technology-landscape
- **Research gate:** What CI/CD patterns exist for projects using Claude Code? GitHub Actions best practices for AI agent repos? Pre-commit hooks for Arabic text safety?
- **ChatGPT prompt:**
  > "I'm setting up CI/CD for a Python project that uses Claude Code, Codex CLI, and Gemini CLI as build tools. The project processes Arabic scholarly texts and needs: ruff + black + pyright in CI, test stratification (cheap vs expensive LLM tests), pre-commit hooks, and branch protection. What CI/CD patterns or GitHub Actions workflows exist for similar AI agent projects in 2026? Any gotchas for Arabic text in CI?"
- **Duration:** 20 min

#### μ-F2.2 — Prepare CC Handoff for Session 2
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F2.1
- **Skills:** kr-preparing-cc-handoffs, critical-review
- **Action:** Write CC prompt from roadmap Session 2, incorporating any landscape findings.
- **Duration:** 30 min

#### μ-F2.3 — CC Builds Session 2
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F2.2
- **Duration:** 1 CC session

#### μ-F2.4 — Review CC Session 2 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F2.3
- **Skills:** kr-reviewing-cc-output, factory-session, critical-review
- **Exit criteria check:**
  - CI workflow includes ruff + black + pyright + pytest + manifest + contracts
  - `.pre-commit-config.yaml` exists and works
  - Branch protection via `gh api`
  - All 4 hooks fixed with tests
  - Hook overhead documented
- **Duration:** 1 full session

---

### Session 2.5 — WSL2 + CLI Setup (Owner Action)

#### μ-F2.5.1 — Prepare Owner Setup Guide
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-PF.2 (WSL2 status known)
- **Skills:** factory-session
- **Action:** Write step-by-step guide with exact commands for:
  1. WSL2 setup (if not installed)
  2. Ubuntu setup inside WSL (nvm, Node.js LTS, Python 3.11+)
  3. Claude Code CLI install + auth
  4. Codex CLI install + auth
  5. Gemini CLI install + auth
  6. Verification commands with expected output
  7. factory_config.json template with version pins
  8. Test: `schtasks` triggering a WSL Python script
- **ChatGPT prompt:**
  > "I need to install Claude Code CLI, Codex CLI (OpenAI), and Gemini CLI (Google) inside WSL2 Ubuntu on Windows 11. All three need to run headless with JSON output. What's the exact install + authentication process for each in March 2026? Any known issues with these CLIs on WSL2? Any auth token persistence gotchas?"
- **Duration:** 1 session (research + guide writing)

#### μ-F2.5.2 — Owner Executes Setup
- **Tool:** Owner
- **Track:** Factory
- **Depends on:** μ-F2.5.1
- **Action:** Follow the guide. Report results at each step.
- **Duration:** 2-4 hours (with architect on standby in Claude Chat)

#### μ-F2.5.3 — Verify Setup
- **Tool:** Claude Chat + Owner
- **Track:** Factory
- **Depends on:** μ-F2.5.2
- **Action:** Owner runs verification commands, reports output. Architect confirms all 3 CLIs work.
- **Duration:** 15 min

---

### Session 3 — CLI Abstraction + Extend Orchestrator

#### μ-F3.1 — Technology Landscape Scan: CLI Orchestration Libraries
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F2.5.3 (all CLIs working)
- **Skills:** factory-session, technology-landscape
- **Research gate:** Are there libraries/frameworks that wrap Claude Code + Codex + Gemini CLIs with a unified interface? Dispatch libraries? Structured output parsers for multiple CLI tools?
- **ChatGPT prompt:**
  > "I need a Python abstraction layer that dispatches prompts to three different AI coding CLIs (Claude Code, Codex CLI, Gemini CLI), each with different flags and JSON output schemas. It should handle: timeout, retry, version validation, degraded modes (if one CLI is down), and artifact logging. Before I build custom: are there Python libraries or frameworks for multi-CLI AI agent dispatch in 2026?"
- **Duration:** 30 min

#### μ-F3.2 — Paperclip WSL2 Re-Test Decision
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F2.5.3
- **Decision point:** The Paperclip evaluation found Windows-specific blockers (WIN1252 encoding, symlink EPERM). Now that WSL2 is set up, should we re-test Paperclip on WSL2?
- **If YES:** Prepare a CC prompt to install and test Paperclip in WSL2 (use tool-evaluation skill). This would be μ-F3.2a.
- **If NO:** Proceed with custom build. Paperclip becomes a Session 8 integration candidate.
- **Recommendation:** DEFER. Build the orchestrator standalone with clean interfaces. Test Paperclip integration as an optional enhancement in Session 8. Reason: Paperclip is 3 weeks old, and our orchestrator already has 1,287 lines of battle-tested code.
- **Duration:** 15 min decision

#### μ-F3.3 — Prepare CC Handoff for Session 3
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F3.1, μ-F3.2
- **Skills:** kr-preparing-cc-handoffs, critical-review
- **Key decisions to make IN this session (not defer):**
  - AGENTS.md content (under 32 KiB — what to include, what to cut)
  - GEMINI.md content (what to exclude, how to structurally prevent Playbook access)
  - Agent Teams enablement (verify flag names against current CC docs)
  - Gemini CLI flag verification (--yolo, --output-format json — verify these are current)
- **CC empirical verification prompt (relay before finalizing handoff):**
  > "Run these commands and report exact output:
  > `claude --version && codex --version && gemini --version`
  > `claude -p 'echo test' --output-format json 2>&1 | head -20`
  > `codex exec 'echo test' --output-last-message /tmp/test.md 2>&1 | head -20`
  > `gemini -p 'echo test' --output-format json 2>&1 | head -20`
  > Report what flags each CLI accepts for headless + JSON mode."
- **Duration:** 1 full session

#### μ-F3.4 — CC Builds Session 3
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F3.3 + CC empirical verification
- **Duration:** 1-2 CC sessions (largest build session in Phase 1)

#### μ-F3.5 — Review CC Session 3 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F3.4
- **Skills:** kr-reviewing-cc-output, factory-session, critical-review
- **Factory-specific review checks:**
  - AGENTS.md under 32 KiB? (`wc -c AGENTS.md`)
  - GEMINI.md excludes Playbook? (`grep "Decision Playbook" GEMINI.md`)
  - Cross-provider test actually ran all 3 CLIs?
  - cli_health_check.py verifies auth, version, JSON output?
  - Agent Teams enabled and verified?
- **Duration:** 1 full session

---

## Phase 2: Benchmark (Roadmap Sessions 4-5)

### Session 4 — Benchmark Design + Construction

**CRITICAL PREREQUISITE:** Excerpting engine must have produced real output on ≥5 books.
This means the engine-track work (model role research → 5-book test → results) must complete
before the benchmark can use real excerpting output as test cases.

#### μ-F4.1 — Benchmark Task Taxonomy Design
- **Tool:** Claude Chat
- **Track:** Factory (but blocked on engine-track μ-PF.3 completing)
- **Depends on:** μ-F3.5 (Phase 1 ACCEPTED) + excerpting 5-book test completed
- **Skills:** factory-session, kr-research, thinking-frameworks
- **Action:** Design the 12-task benchmark taxonomy per roadmap. For each task:
  - Define input format, output format, scoring rubric
  - Define minimum case count (≥20 per task, ≥5 adversarial)
  - Design adversarial cases from known failure patterns (T-1 through T-7)
  - Identify which tasks require owner Arabic verification vs automated scoring
- **ChatGPT prompt:**
  > "I'm designing a benchmark for evaluating LLMs on Arabic Islamic scholarly text tasks. The 12 tasks include: layer attribution, school classification, author identification, genre detection, scholarly function classification, self-containment judgment, decontextualization detection, tahqiq discrimination, death date verification, synthesis disagreement preservation, synthesis quotation-vs-endorsement, and synthesis attribution accuracy. For each: what makes a good adversarial test case? What scoring metrics are appropriate? What existing Arabic NLP benchmarks can I learn from? I need ≥20 cases per task with ≥5 adversarial."
- **Duration:** 1 full session

#### μ-F4.2 — Test Case Selection from Real Output
- **Tool:** Claude Chat + Owner
- **Track:** Factory
- **Depends on:** μ-F4.1 + real excerpting output available
- **Action:** Owner + architect select test cases from real excerpting results. For synthesis tasks, architect constructs scenarios from actual excerpts.
- **Owner action:** Provide 5-book excerpting output for case selection.
- **Duration:** 1 session

#### μ-F4.3 — Codex Designs Adversarial Cases
- **Tool:** CC (dispatches Codex CLI)
- **Track:** Factory
- **Depends on:** μ-F4.2
- **Action:** Codex CLI generates adversarial cases per task. NOT Claude Code — CC is the evaluated subject.
- **CC prompt:** "Dispatch Codex CLI with benchmarks/TASK_SPEC.md to generate adversarial cases. Capture output."
- **Duration:** 1 CC session

#### μ-F4.4 — Gemini Reviews Adversarial Cases
- **Tool:** CC (dispatches Gemini CLI)
- **Track:** Factory
- **Depends on:** μ-F4.3
- **Action:** Gemini independently reviews and augments adversarial cases.
- **Duration:** 1 CC session (or combined with μ-F4.3)

#### μ-F4.5 — Owner Verifies Ground Truth
- **Tool:** Owner + Claude Chat
- **Track:** Factory
- **Depends on:** μ-F4.4
- **Action:** Owner reads actual Arabic text for each test case. "Is this ground truth correct?" Model-assisted web verification supplements but does not replace owner reading.
- **Duration:** 2-4 hours owner time (architect formats cases for readability)

#### μ-F4.6 — CC Builds Benchmark Infrastructure
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F4.5
- **Action:** CC builds scorer, runner, reporting. CC does NOT design cases or verify ground truth.
- **Duration:** 1 CC session

#### μ-F4.7 — Review Benchmark Infrastructure
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F4.6
- **Duration:** 1 review session

---

### Session 4.5 — Synthetic Adversarial Data Infrastructure

#### μ-F4.5.1 — Technology Landscape Scan: Synthetic Test Data Generation
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F4.7 (benchmark ACCEPTED)
- **Skills:** factory-session, technology-landscape
- **Research gate:** Existing tools for synthetic adversarial test generation? Mutation testing frameworks adaptable to NLP? Property-based testing for structured extraction?
- **ChatGPT prompt:**
  > "I need to generate synthetic adversarial Arabic scholarly texts that test specific failure modes (7 threat types: text corruption, attribution error, taxonomic misplacement, context loss, synthesis hallucination, metadata poisoning, duplication). Each synthetic text has known ground truth so I can compare pipeline output against it. Are there existing frameworks for synthetic adversarial data generation for NLP/extraction pipelines? Mutation testing frameworks that could be adapted? Property-based testing tools for structured output validation?"
- **Duration:** 30 min

#### μ-F4.5.2 — Prepare CC Handoff for Session 4.5
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F4.5.1
- **Skills:** kr-preparing-cc-handoffs
- **Duration:** 30 min

#### μ-F4.5.3 — CC Builds Synthetic Infrastructure
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F4.5.2
- **Duration:** 1-2 CC sessions

#### μ-F4.5.4 — Review Synthetic Infrastructure
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F4.5.3
- **Duration:** 1 review session

---

### Session 5 — Run Benchmark + Routing Table

#### μ-F5.1 — CC Runs Benchmark
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F4.5.4 (synthetic infra ACCEPTED) + μ-F4.7 (benchmark ACCEPTED)
- **Action:** Run benchmark against all 3 CLIs. Capture results.
- **Duration:** 1 CC session (may be long due to 3 × 240 = 720 benchmark cases)

#### μ-F5.2 — Analyze Benchmark Results
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F5.1
- **Skills:** kr-evaluate, thinking-frameworks, critical-review
- **Action:** Analyze per-task comparison. Compute confidence intervals. Identify correlated-agreement cases. Produce routing_table.json.
- **ChatGPT prompt:**
  > "Here are benchmark results for 3 LLMs on 12 Arabic scholarly tasks: [results summary]. Help me analyze: (1) are the differences statistically significant with ≥20 cases per task? (2) any correlated failures where all 3 gave the same wrong answer? (3) does CLI wrapping introduce confounds vs raw API?"
- **Duration:** 1 full session

#### μ-F5.3 — CC Commits Routing Table
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F5.2
- **Action:** Commit routing_table.json and RESULTS_ANALYSIS.md.
- **Duration:** Quick CC task

---

## Phase 3: Orchestration (Roadmap Sessions 6-7)

### Session 6 — Extend Orchestrator

#### μ-F6.1 — Technology Landscape Scan: Work-Unit Orchestration
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F5.3 (Phase 2 complete)
- **Skills:** factory-session, technology-landscape
- **Research gate:** Task queue systems (Celery, RQ, Dramatiq), workflow engines (Prefect, Dagster, Temporal), AI-specific orchestrators — anything that handles typed work units with dependencies, retries, and state persistence?
- **ChatGPT prompt:**
  > "I have a Python orchestrator (1,287 lines) that dispatches tasks to AI coding CLIs. I need to add: typed work units with dependencies, response contract validation, escalation queues for ambiguities, degraded operation modes (when CLIs are unavailable), and 6 operating modes (BUILD/HUNT/FIX/EVALUATE/CROSS-ENGINE/BENCHMARK). Should I extend my existing orchestrator or adopt a workflow engine like Prefect/Dagster/Temporal? Constraints: runs on WSL2, file-based state (no database), must integrate with 3 different CLI tools."
- **Duration:** 30 min

#### μ-F6.2 — Prepare CC Handoff for Session 6
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F6.1
- **Skills:** kr-preparing-cc-handoffs
- **Key decisions:** Whether to adopt a workflow engine or extend custom orchestrator.
- **Duration:** 1 session

#### μ-F6.3 — CC Builds Session 6
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F6.2
- **Duration:** 2 CC sessions (largest build)

#### μ-F6.4 — Review CC Session 6 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F6.3
- **Duration:** 1 full review session

---

### Session 7 — Scheduler + Recovery

#### μ-F7.1 — Prepare CC Handoff for Session 7
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F6.4 (Session 6 ACCEPTED)
- **Skills:** kr-preparing-cc-handoffs
- **No landscape scan needed:** Windows Task Scheduler + PID locks are well-understood. The existing orchestrator already has PID locking.
- **Duration:** 30 min

#### μ-F7.2 — CC Builds Session 7
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F7.1
- **Duration:** 1 CC session

#### μ-F7.3 — Review CC Session 7 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F7.2
- **Duration:** 1 review session

#### μ-F7.4 — Owner Starts the Factory
- **Tool:** Owner
- **Track:** Factory
- **Depends on:** μ-F7.3 (Session 7 ACCEPTED)
- **Action:** Run `wsl python3 ~/kr/scripts/factory_start.py` from Windows.
- **Verify:** `schtasks /query` shows the scheduled task. Factory wakes on schedule.
- **Duration:** 15 min

---

## Phase 4: Interface (Roadmap Session 8)

### Session 8 — Dashboard + Human Gate + Arabic Formatter

#### μ-F8.1 — Paperclip Re-Evaluation Decision
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F7.4 (factory running)
- **Decision point:** The factory is now running standalone. Should we integrate Paperclip for dashboard + governance + cost tracking, or build custom?
- **Skills:** tool-evaluation (if testing Paperclip), technology-landscape
- **If Paperclip:** Prepare CC prompt to install Paperclip in WSL2 and test.
- **If custom:** Prepare CC prompt for Session 8 as written in roadmap.
- **Duration:** 1 session (evaluation) or 15 min (decision to build custom)

#### μ-F8.2 — Technology Landscape Scan: Dashboard Frameworks
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F8.1
- **Research gate:** Static site generators for dashboards? GitHub Pages dashboard templates? Existing factory/CI dashboards that could be adapted?
- **Duration:** 20 min

#### μ-F8.3 — Prepare CC Handoff for Session 8
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F8.2
- **Duration:** 1 session

#### μ-F8.4 — CC Builds Session 8
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F8.3
- **Duration:** 2 CC sessions

#### μ-F8.5 — Review CC Session 8 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F8.4
- **Duration:** 1 review session

---

## Phase 5: Hardening (Roadmap Sessions 9-10)

### Session 9 — Factory Acceptance Test

#### μ-F9.1 — Design 15-Point Acceptance Test
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F8.5 (Session 8 ACCEPTED)
- **Skills:** factory-session, thinking-frameworks
- **Action:** For each of the 15 acceptance criteria from FACTORY_ROADMAP_v2.md, design: the specific test procedure, the pass/fail criteria, and the evidence to collect.
- **Gemini challenge prompt:**
  > "Here are 15 acceptance tests for an autonomous AI factory. For each: what could pass the test but still fail in production? What's the weakest test? What's missing?"
- **Duration:** 1 session

#### μ-F9.2 — CC Implements and Runs Acceptance Test
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F9.1
- **Duration:** 1-2 CC sessions

#### μ-F9.3 — Review Acceptance Results
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F9.2
- **Duration:** 1 review session

---

### Session 10 — Health Monitoring + Sustainability

#### μ-F10.1 — Prepare CC Handoff for Session 10
- **Tool:** Claude Chat
- **Track:** Factory
- **Depends on:** μ-F9.3 (acceptance PASSED)
- **Duration:** 30 min

#### μ-F10.2 — CC Builds Session 10
- **Tool:** CC
- **Track:** Factory
- **Depends on:** μ-F10.1
- **Duration:** 1 CC session

#### μ-F10.3 — Review CC Session 10 Output
- **Tool:** Claude Chat (NEW session)
- **Track:** Factory
- **Depends on:** μ-F10.2
- **Duration:** 1 review session

#### μ-F10.4 — Factory Operational Acceptance
- **Tool:** Claude Chat + Owner
- **Track:** Factory
- **Depends on:** μ-F10.3
- **Skills:** kr-gating-transitions
- **Action:** Full transition gate. The factory is either OPERATIONAL or BLOCKED.
- **Duration:** 1 session

---

## Parallel Engine Track (Running Alongside Factory)

These μ-tasks run on the engine track, independent of factory work.

### μ-E1 — Model Role Research
- **Depends on:** Nothing (START NOW)
- **Session:** Claude Chat
- **Skills:** kr-research, deep-research, thinking-frameworks
- **Action:** NEXT.md Task 1

### μ-E2 — 5-Book LLM Integration Test Prep
- **Depends on:** μ-E1 (model roles assigned)
- **Session:** Claude Chat
- **Skills:** kr-preparing-cc-handoffs
- **Action:** NEXT.md Task 2

### μ-E3 — CC Runs 5-Book Test
- **Depends on:** μ-E2
- **Session:** CC

### μ-E4 — Review 5-Book Results
- **Depends on:** μ-E3
- **Session:** Claude Chat (NEW session)
- **Skills:** kr-evaluate, kr-reviewing-cc-output

### μ-E5 — 30-Book Owner Probe Design
- **Depends on:** μ-E4 (5-book ACCEPTED)
- **Session:** Claude Chat

### μ-E6 — CC Runs 30-Book Pipeline
- **Depends on:** μ-E5
- **Session:** CC

### μ-E7 — Owner Reviews 30 Books (5 per session, 6 sessions)
- **Depends on:** μ-E6
- **Session:** Owner + Claude Chat (6 sessions)
- **This is the NON-NEGOTIABLE owner review gate**

### μ-E8 — Excerpting Completion Gate
- **Depends on:** μ-E7
- **Session:** Claude Chat
- **Skills:** kr-gating-transitions

---

## Session Count Summary

| Phase | Planning Sessions | CC Build Sessions | Review Sessions | Owner Sessions | Total |
|-------|-------------------|-------------------|-----------------|----------------|-------|
| Pre-flight | 1 | 0 | 0 | 1 | 2 |
| Phase 1 (F1-F3) | 4 | 4 | 3 | 1 (WSL setup) | 12 |
| Phase 2 (F4-F5) | 3 | 4 | 3 | 1 (ground truth) | 11 |
| Phase 3 (F6-F7) | 2 | 3 | 2 | 1 (start factory) | 8 |
| Phase 4 (F8) | 2 | 2 | 1 | 0 | 5 |
| Phase 5 (F9-F10) | 2 | 3 | 2 | 0 | 7 |
| **Factory total** | **14** | **16** | **11** | **4** | **45** |
| Engine (parallel) | 3 | 2 | 2 | 6 | 13 |
| **Grand total** | **17** | **18** | **13** | **10** | **58** |

**Note:** Many planning + review sessions can be combined when they're short (30 min planning tasks can be combined in one Claude Chat session). Actual calendar sessions will be fewer than 58 — likely 25-30 distinct sessions over 12-15 weeks.

---

## What To Do RIGHT NOW

**Immediate parallel actions (today/tomorrow):**

1. **Upload the 4 new skills** to Claude project (μ-PF.1)
2. **Check WSL2 status** — `wsl --status` in PowerShell (μ-PF.2)
3. **Start a NEW Claude Chat session for model role research** (μ-PF.3 / μ-E1)
   - This is engine-track work, independent of factory
   - Uses: kr-research, deep-research, thinking-frameworks
   - The NEXT.md is ready — just start the session

**Next factory step (after skills uploaded):**
4. **Start μ-F1.1** — technology landscape scan for manifest management
   - This can happen in the SAME session as μ-F1.2 and μ-F1.3
   - Then hand off to CC for μ-F1.4

---

## Rules for This Plan

1. **Every μ-task gets a NEW Claude Chat session** unless it's explicitly combinable (short planning tasks in the same phase).
2. **Every build decision has a research gate** — invoke `use technology-landscape`.
3. **Every CC handoff has cross-provider consultation** — ChatGPT prompt + CC empirical verification.
4. **Never review in the same session as the handoff.**
5. **The engine track and factory track run in parallel.** They share no dependencies until Phase 2 (benchmark needs real excerpting output).
6. **BLOCKED means BLOCKED.** If a review finds issues, fix them before proceeding. No "ACCEPT WITH FIXES."
7. **The owner says "continue" but does NOT check output.** The architect is the sole quality gate for every μ-task.
