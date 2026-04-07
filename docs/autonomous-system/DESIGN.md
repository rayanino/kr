# KR Autonomous System — Design Document

**Version:** 1.0-draft
**Date:** 2026-04-07
**Status:** DESIGN — awaiting coworker review + DR validation
**Authority:** Supplements `docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md` (safety governance). This document defines WHAT the system does; the doctrine defines HOW SAFELY it operates.

---

## 1. Mission Statement

> "THE MAIN FOCUS IS ON NOT LOSING TIME IN THE SUMMER. LONG TEDIOUS TASKS ELIMINATED RIGHT NOW."
> — Owner directive, 2026-04-07

The autonomous system operates from April 9 to July 1, 2026 (83 days). Its sole purpose: **eliminate every task that would consume the owner's time during summer full-build sessions.**

Time economics:
- **Now (autonomous period):** Speed is free. Quality is unlimited. 3 months is plenty.
- **Summer (owner sessions):** Every hour counts. Owner runs CC/Codex 24/7. Any "we need to research this first" blocker is catastrophic.

### Three Pillars (Priority Order)

| Pillar | Priority | Goal | Metric |
|--------|----------|------|--------|
| **1. Deep Research** | HIGHEST | All research done before July | 830+ DRs processed, zero unresolved blockers |
| **2. Pipeline Hardening** | EQUAL | Excerpting + taxonomy engines reliable | Zero silent failures, edge cases covered, 95%+ test coverage |
| **3. Creative Ideas** | IMPORTANT | Summer to-do list of big ideas | Ideas that take days/weeks to develop, fully researched |

### Governing Principle

Everything SLOW goes into the autonomous period. Everything FAST stays for summer.

| Slow (do NOW) | Fast (save for SUMMER) |
|---|---|
| Deep Research prompts (10-60 min each) | CC/Codex sessions (interactive, instant) |
| Edge case discovery and hardening | Feature implementation on solid foundations |
| Long-gestation creative ideas | Quick ideas and small improvements |
| Test suite expansion | Running tests on new code |
| SPEC refinement and gap-filling | Building from finalized SPECs |

---

## 2. Owner Interaction Model

### 2.1 Owner Role Definition

The owner is the **CLIENT**, not a developer. He does NOT code, does NOT read code, does NOT make architecture decisions. LLMs and agents do ALL technical work.

Owner provides exactly 4 things:
1. **DR relay** — pasting prompts into ChatGPT/Claude/Gemini DR windows
2. **User-experience feedback** — "this excerpt is too broad", "I want to compare these"
3. **Gate approvals** — phase transitions, protocol amendments
4. **New materials** — collection bundles, source files

### 2.2 Daily Rhythm

```
07:00-08:00  BREAKFAST
             Owner opens browser dashboard
             Reviews: what system did yesterday, any findings needing input
             Leaves: ideas, feedback, comments
             Starts: relay queue (processes top DR prompts)

08:00-12:00  UNIVERSITY STUDY
             Owner works on university degree (slides, lectures)
             Laptop open but owner is NOT monitoring KR
             System runs SILENTLY in background
             System ONLY interrupts if it NEEDS owner action

12:00-13:00  MIDDAY CHECK (optional)
             Quick relay of remaining DR prompts
             Check if system flagged anything

17:00-19:00  EVENING REVIEW
             Review system findings
             Leave comments on insights
             Process any remaining DR relay items
```

### 2.3 Notification Model

**Default: SILENT.** No progress notifications. No "task X completed" alerts.

Interrupt the owner ONLY for:
- DR prompts ready for relay (queued, owner processes at his pace)
- A question ONLY the owner can answer (user-experience, never technical)
- A gate decision requiring explicit approval
- A critical error that blocks all work

**Never interrupt for:** Progress updates, technical decisions, coworker results, test outcomes, implementation choices.

### 2.4 Owner Question Protocol

Before asking the owner ANY question, apply this filter:

| ASK | DO NOT ASK |
|-----|-----------|
| "When you read this excerpt, what's your reaction?" | "Should we modify DP-4?" |
| "Is this too much information or too little?" | "What launch method for the system?" |
| "What would you do next after reading this?" | "How should we handle lid-close?" |
| "Does this insight about your library surprise you?" | "What data format for the queue?" |

The owner **loves being asked questions** — ask freely about his experience. Never ask about architecture.

### 2.5 Idea Processing Pipeline

Owner ideas are **INSPIRATION, not instructions.** The owner explicitly warned: "I MAY AS WELL DIG MY OWN GRAVE WITH AN IDEA."

```
Owner submits idea
    |
    v
[RECEIVED] — Acknowledged, logged with timestamp
    |
    v
[RESEARCHED] — Deploy DR: ChatGPT (feasibility), Claude (scholarly impact), Gemini (pedagogical)
    |
    v
[VALIDATED] — Coworker consensus: implement / adapt / reject
    |
    v
[IMPLEMENTED] or [REJECTED with explanation]
```

Every idea triggers DR research. No idea is implemented without validation.

---

## 3. System Architecture

### 3.1 Component Overview

```
+------------------------------------------------------------------+
|                    AUTONOMOUS SYSTEM                              |
|                                                                   |
|  +------------------+  +------------------+  +-----------------+  |
|  | DR RELAY ENGINE  |  | HARDENING ENGINE |  | CREATIVE ENGINE |  |
|  |                  |  |                  |  |                 |  |
|  | - Gap scanner    |  | - Edge case      |  | - Big idea      |  |
|  | - Prompt gen     |  |   discovery      |  |   generation    |  |
|  | - /prompt-arch   |  | - Test gen       |  | - DR-backed     |  |
|  | - Queue manager  |  | - Bug fix        |  |   research      |  |
|  | - Response proc  |  | - SPEC refine    |  | - Long gestation|  |
|  +--------+---------+  +--------+---------+  +--------+--------+  |
|           |                     |                      |          |
|  +--------+---------------------+----------------------+--------+ |
|  |                    KNOWLEDGE BASE                            | |
|  |  Persistent JSON/JSONL store — all insights, DR results,     | |
|  |  findings, metrics, ideas. Dashboard reads from here.        | |
|  +------------------------------+-------------------------------+ |
|                                 |                                 |
|  +------------------------------+-------------------------------+ |
|  |                    DASHBOARD (browser)                       | |
|  |  Owner's ONLY interface. Read-only view + input forms.       | |
|  |  DR relay queue, findings, ideas, status, insights.          | |
|  +--------------------------------------------------------------+ |
+------------------------------------------------------------------+
```

### 3.2 Existing Infrastructure (5,543 lines — REUSE, do not rewrite)

| Component | Lines | Role in New System |
|-----------|-------|-------------------|
| `overnight_codex_orchestrator.py` | 2,714 | Core execution loop — extend with DR relay engine |
| `overnight_codex_task_generator.py` | 732 | Task discovery — add research-gap scanner |
| `overnight_codex_backlog.py` | 709 | Backlog management — integrate with idea pipeline |
| `overnight_codex_evaluator.py` | 737 | Quality evaluator — reuse for creative idea scoring |
| `overnight_codex_common.py` | 586 | Shared utilities — extend with DR queue data models |
| `overnight_codex_ideation.py` | 65 | Ideation scoring — extend with long-gestation framework |

### 3.3 Branching Model

The system operates on a **dedicated persistent branch**: `autonomous/nightly`

- All system work happens on this branch or worktrees from it
- Owner's work on other branches is NEVER affected
- Changes merge to master through validated PRs only
- The "repo clean" check applies only to the system's own branch
- System has full autonomy within its branch — "it's your branch, you choose"

### 3.4 Persistence Model

**Every insight is backed by persistent data.** The dashboard is a VIEW onto stored state, never a generator of ephemeral content.

```
overnight_codex/autonomous/
  knowledge_base/
    dr_prompts/           # Generated DR prompts (JSONL)
    dr_responses/         # Processed DR responses (JSONL)
    dr_index.json         # Master index: prompt_id, target, status, findings
    research_gaps.json    # Identified gaps with priority + source
    findings.jsonl        # All system findings (persistent, append-only)
    ideas.jsonl           # Owner ideas + research status + verdicts
    insights.jsonl        # System insights about the library/pipeline
    metrics.json          # Daily metrics snapshot
  relay_queue.json        # Single state file (atomic), not directory-based
  dashboard/
    state.json            # Current dashboard state
    history.jsonl         # Dashboard interaction log
```

> **AMENDMENT (Codex review):** Moved from `.kr/autonomous/` to `overnight_codex/autonomous/`.
> Reason: `.kr/` is in `FORBIDDEN_EDIT_PREFIXES` (common.py line 60) — Codex tasks
> writing to `.kr/` are blocked by the safety layer. `overnight_codex/` is already in
> `codex_write_prefixes.txt`. Relay queue changed from directory-based state machine to
> single JSON file with status fields (matches existing orchestrator pattern for atomicity).

All data structures are **machine-first** — optimized for agent consumption, not human readability.

---

## 4. Pillar 1: DR Relay Engine (HIGHEST PRIORITY)

### 4.1 The Transformative Idea

The owner relays 10-20 DR prompts per day. Over 83 days, this is **830-1,660 research sessions** — all free (subscription-based). The system's job: ensure the queue is NEVER empty and every prompt produces actionable findings.

### 4.2 Research Gap Scanner

The system continuously scans for unresolved research questions from:

| Source | Scan Method | Example Gap |
|--------|-------------|-------------|
| SPEC `[OPEN]` markers | Grep for `[OPEN:` in all SPEC.md files | OQ-001: school-specific distinction threshold |
| SPEC sections without examples | Parse §4 rules, check for Arabic examples | §6.21 SSB-1 needs real-world test cases |
| Engine KNOWN_LIMITATIONS.md | Parse L-XXX entries needing research | L-012: colophon date extraction accuracy |
| Test coverage gaps | Compare SPEC rules vs test files | §4.A.7 untested edge case |
| Coworker disagreements | Scan consensus logs for unresolved splits | Genre classification split on hashiyah vs ta'liq |
| Owner feedback | Parse ideas.jsonl for unresearched items | Owner said "excerpts feel too broad" |
| Cross-engine boundaries | Check contract compatibility gaps | Passaging→Atomization metadata flow |
| D-041 consensus failures | Items flagged for human review | Author attribution disagreement |
| Arabic text edge cases | Known Arabic processing challenges | Taa marbuta handling in edge contexts |
| Taxonomy tree gaps | Science nodes without scholarly grounding | Fiqh subdivision tree incomplete |

### 4.3 Prompt Generation Pipeline

```
Gap identified
    |
    v
[Classify] — Which DR source is best?
    |
    +-- Architecture/feasibility/patterns → ChatGPT DR
    +-- Scholarly reasoning/boundaries/quality → Claude DR
    +-- Islamic methodology/pedagogy/18 sciences → Gemini DR
    |
    v
[Draft] — Write initial prompt with:
    - Clear question
    - Relevant context (file paths for ChatGPT/Claude DR; file bundle for Gemini DR)
    - What the answer will unblock
    - Expected output format
    |
    v
[Optimize] — /prompt-architect pass (MANDATORY, Rule 14)
    |
    v
[Queue] — Add to relay_queue/pending/ with metadata:
    - prompt_id, target_dr, priority, estimated_value
    - what_it_unblocks, dedup_hash, created_at
    |
    v
[Dashboard] — Appears in owner's relay queue
```

### 4.4 DR Source Capabilities

| Source | Access | Strength | File Protocol |
|--------|--------|----------|--------------|
| ChatGPT DR | HAS repo access | Architecture, patterns, feasibility, error analysis | Give FILE PATHS — never paste content |
| Claude DR | HAS repo access | Scholarly reasoning, boundary quality, edge cases | Give FILE PATHS — never paste content |
| Gemini DR | NO repo access | Islamic methodology, pedagogy, 18 sciences, Arabic analysis | Prepare FILE BUNDLE for upload |

**CRITICAL:** Never paste file contents into ChatGPT DR or Claude DR prompts. They read the repo directly.

### 4.5 Response Processing

When the owner provides a DR response file path:

1. Parse and structure the response
2. Extract actionable findings (tagged by category)
3. Cross-reference against existing knowledge base (dedup)
4. Update relevant SPEC sections, research gaps, or backlog items
5. Generate follow-up DR prompts if the response reveals new gaps
6. Persist everything to knowledge_base/

### 4.6 Queue Management

- Queue always has prompts ready. **Empty queue = system failure.**
- Priority ordering: blockers > gaps > improvements > exploration
- Daily target: 10-20 prompts ready at breakfast
- Deduplication: never re-ask what a previous DR already answered
- Prompt freshness: re-evaluate queued prompts weekly (context may have changed)

---

## 5. Pillar 2: Pipeline Hardening Engine

### 5.1 Focus Areas

Priority engines: **excerpting** (primary) and **taxonomy** (secondary).

The owner's 10x wish: "Anything related to getting the engines to work reliably and accurately. Discovering edge cases."

### 5.2 Hardening Activities

| Activity | Method | Output |
|----------|--------|--------|
| Edge case discovery | Adversarial input generation, boundary testing | New test cases in `engines/<n>/tests/` |
| Test coverage expansion | SPEC rule → test mapping, gap analysis | Tests targeting uncovered SPEC rules |
| Error handling audit | Trace all error paths, verify fail-loud | Fixes for silent failures |
| SPEC consistency check | Cross-reference SPEC vs code vs tests | SPEC amendments, code fixes |
| Arabic text safety | Arabic-specific edge cases (diacritics, normalization) | Arabic safety tests |
| D-023 metadata flow | Verify metadata pass-through at every boundary | Metadata flow tests |
| Consensus reliability | Test multi-model agreement patterns | Consensus edge case tests |
| Regression detection | Compare test results across commits | Regression alerts |

### 5.3 Integration with Existing Overnight System

The existing orchestrator + task generator already handles:
- Worktree isolation per task
- Quality gate (5 levels)
- Morning report generation
- Allowlist enforcement
- Bookend tasks (regression always runs last)

**Extend, don't replace:** Add hardening scanners to the task generator. The orchestrator's execution loop is proven.

### 5.4 Hardening Budget

Per the autonomous doctrine: **85% hardening, 15% evaluation prep.**

This is a zero-feature period. No new engine capabilities. Only making existing capabilities reliable.

---

## 6. Pillar 3: Creative Ideas Engine

### 6.1 What "Creative Ideas" Means Here

NOT quick improvements (those happen in summer). The value is in ideas that need **days or weeks of development** — architecture proposals, novel approaches, cross-engine innovations that an interactive session cannot produce because they require:
- Deep research across multiple DR sources
- Cross-referencing scholarly traditions
- Prototype evaluation
- Multi-coworker validation

### 6.2 Idea Generation Sources

| Source | Example |
|--------|---------|
| Cross-engine pattern analysis | "Taxonomy trees could feed back into excerpting for context-aware boundaries" |
| Scholarly tradition research | "The ijazah system maps to a trust graph — can we model scholar authority this way?" |
| Pipeline performance analysis | "Batch processing at the passaging level could enable parallel atomization" |
| Technology landscape monitoring | "New LLM release enables 1M-token scholarly analysis — implications for excerpting" |
| Owner feedback patterns | "Owner consistently says excerpts are 'too broad' — is there a deeper granularity model?" |

### 6.3 Idea Lifecycle

```
[GENERATED] — System produces idea with initial analysis
    |
    v
[DR-RESEARCHED] — 1-3 DR prompts dispatched for deep evaluation
    |
    v
[COWORKER-VALIDATED] — Codex + Gemini review for feasibility + scholarly alignment
    |
    v
[SCORED] — 8-dimension evaluation (existing evaluator framework)
    |
    v
[QUEUED FOR SUMMER] — Added to summer to-do list with:
    - Full research backing
    - Implementation sketch
    - Dependencies and prerequisites
    - Estimated effort
    - What it enables
```

### 6.4 Quality Bar

An idea is "summer-ready" when:
- At least 2 DR reports support it
- At least 2 coworkers have validated it
- It has a concrete implementation sketch (not just "we should do X")
- Dependencies are identified and either resolved or flagged
- The owner has been briefed (brief-before model, not approval-gate)

---

## 7. Dashboard

### 7.1 Design Principles

- **Owner's ONLY interface** — he never touches the terminal, repo, or code
- **View onto persistent state** — every metric derived from stored data
- **Machine-first data, human-friendly display** — data structures optimized for agents; dashboard renders them for the owner
- **Silent by default** — owner checks at his pace (breakfast + evening)
- **Input-capable** — owner can leave ideas, feedback, comments

### 7.2 Dashboard Sections

| Section | Content | Update Frequency |
|---------|---------|-----------------|
| **DR Relay Queue** | Prioritized list of prompts to relay. Target DR, estimated value, copy-pasteable text. | Continuous (as system generates) |
| **Yesterday's Findings** | What the system discovered, built, or improved since last check. | Daily |
| **Pipeline Health** | Test counts, coverage %, last run status, known issues. | After each run |
| **Research Progress** | How many DRs completed, gaps remaining, % of research done. | After each DR processed |
| **Ideas** | Creative ideas with status (generated/researched/validated/queued). | As ideas progress |
| **Owner Input** | Form for submitting ideas, feedback, comments. | Always available |
| **Insights** | "Teach me" section — things the system learned about the owner's library/pipeline. | Weekly |

### 7.3 Technology Decision

**[OPEN — needs DR investigation]**

Options to evaluate:
1. Static HTML + JSON (simplest, no server needed)
2. Local web app (Flask/FastAPI, more interactive)
3. Existing tool (Paperclip was evaluated as EVALUATE_FURTHER)
4. Markdown-based (GitHub renders, but limited interactivity)

DR prompt needed: ChatGPT DR for dashboard technology feasibility.

### 7.4 DR Relay Queue UX

The relay queue is the dashboard's most important section. Each item shows:

```
[Priority: HIGH]  [Target: ChatGPT DR]  [Estimated: 20 min]
Topic: School-specific branching threshold calibration
Unblocks: SPEC §6.21 SSB-1 finalization, 3 downstream tests
Copy this prompt: [expandable text block with the full prompt]
```

Owner workflow: read topic → decide to relay now or later → copy prompt → paste into DR → download response → tell system the file path.

---

## 8. Implementation Phases

### Phase 0: Foundation (Week 1 — April 9-15)
- Create `autonomous/nightly` branch
- Extend `overnight_codex_common.py` with DR queue data models
- Add research-gap scanner to task generator
- Set up `.kr/autonomous/` directory structure
- First 20 DR prompts generated and queued

### Phase 1: DR Relay Engine (Weeks 2-3 — April 16-29)
- Full prompt generation pipeline operational
- Response processing implemented
- Queue management with deduplication
- Owner can relay and receive results

### Phase 2: Dashboard MVP (Weeks 3-4 — April 23 - May 6)
- DR relay queue visible and copy-pasteable
- Findings display
- Owner input form (ideas, feedback)
- Technology choice informed by DR research

### Phase 3: Hardening Integration (Weeks 4-6 — May 1-20)
- Hardening scanners integrated with task generator
- Edge case discovery automated
- Test generation pipeline
- SPEC consistency checking automated

### Phase 4: Creative Engine (Weeks 6-8 — May 15 - June 3)
- Big idea generation operational
- DR-backed research for each idea
- Summer to-do list accumulating
- 8-dimension evaluation scoring

### Phase 5: Maturation (Weeks 8-12 — June 1 - July 1)
- System running at full capacity
- DR queue consistently populated
- Hardening catching real edge cases
- Creative ideas fully researched
- Summer readiness assessment

---

## 9. Summer Readiness Criteria (Definition of Done)

The autonomous period succeeds if, by July 1:

| Criterion | Target | Measurement |
|-----------|--------|-------------|
| DR research completed | 500+ DRs processed | Count of processed DR responses |
| Zero research blockers | 0 unresolved gaps marked CRITICAL | research_gaps.json scan |
| Excerpting test coverage | 95%+ line coverage | pytest --cov |
| Taxonomy test coverage | 90%+ line coverage | pytest --cov |
| Zero silent failures | All error paths fail loud | Error path audit |
| Creative ideas ready | 20+ summer-ready ideas | ideas.jsonl with status=queued |
| D-023 metadata flow | 100% pass | verify_metadata_flow.py |
| Arabic text safety | Zero known violations | Arabic safety audit |
| SPEC consistency | All SPECs internally consistent | check_spec_quality.py |
| Owner briefed | Owner understands summer plan | Dashboard insight history |

---

## 10. Autonomy Model

### 10.1 Brief-Before / Notify-After

The owner does NOT gate every change. The model is **opt-out, not opt-in:**

```
System: "Improvement X ready. [Brief description]. Implementing in next run unless you object."
  [Owner does nothing → implementation proceeds]
  [Owner objects → implementation deferred, logged]
System: "Improvement X implemented successfully. [What changed]."
```

### 10.2 What Requires Owner

| Requires Owner | System Decides |
|----------------|----------------|
| DR relay (physical action) | Which DR prompts to generate |
| User-experience feedback | Technical implementation choices |
| Phase transition gates | Bug fixes, edge case handling |
| New material provision | Test generation, SPEC refinement |
| Idea submission | Idea validation and scoring |

### 10.3 Safety Boundaries (from Autonomous Doctrine)

- **Stagnation over corruption** — a delayed run is acceptable; silent corruption is not
- Protected areas: no SPEC modification, no engine-source auto-apply, no scholarly arbitration
- Engine-source changes generated as reviewed queued patches only
- 3 rollback events in 24h → halted state
- Silence from owner is NEVER approval

---

## 11. Integration Points

### 11.1 With Autonomous Doctrine

This DESIGN.md defines **what** the system does. The doctrine (`docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md`) defines:
- Gate model (Gate 0, Gate A, Gate B)
- Runtime state model (authority mode x health state)
- Coworker rule (Claude Code + Gemini CLI at every major milestone)
- Quota doctrine (L/M/H call classification)
- Stop and rollback conditions
- Daily owner contract (MORNING_REPORT.md)

### 11.2 With Existing Overnight System

| Existing | Integration |
|----------|-------------|
| Orchestrator execution loop | Prompt generation runs as task type; response processing is a SEPARATE script (see Amendment A2) |
| Task generator scanners | Add research-gap scanner, hardening scanner |
| Backlog management | Ideas pipeline feeds into backlog |
| Quality evaluator | Reuse for creative idea scoring |
| WSL bootstrap | Dashboard may run as a separate process |
| Morning report | Extend with DR queue status + research progress |

### 11.3 With Memory System

The autonomous system's knowledge base complements the existing memory system:
- Memory files: cross-session context for CC sessions
- Knowledge base: persistent store for autonomous system findings
- Both are machine-readable, both persist, both are training data (Rule 13)

---

## 12. Open Questions (Require DR Investigation)

| ID | Question | Best DR Source | Priority |
|----|----------|---------------|----------|
| DQ-001 | Dashboard technology: static HTML vs local web app vs existing tool? | ChatGPT DR | HIGH |
| DQ-002 | What should 830+ DRs cover? Optimal research topic distribution across engines? | Claude DR | HIGH |
| DQ-003 | How does DR research map to the 18 Islamic sciences? What gaps exist? | Gemini DR | HIGH |
| DQ-004 | DR response processing: structured extraction vs full-text analysis? | ChatGPT DR | MEDIUM |
| DQ-005 | Optimal batch size for DR relay queue (daily refresh vs continuous)? | Claude DR | MEDIUM |
| DQ-006 | How to detect when research on a topic is "complete" vs needs more DRs? | Claude DR | MEDIUM |
| DQ-007 | Creative idea generation: what frameworks produce the highest-value long-gestation ideas? | ChatGPT DR | MEDIUM |
| DQ-008 | Hardening priority: which excerpting edge cases are most dangerous for scholarly integrity? | Gemini DR | HIGH |

---

## 13. Risk Register

| Risk | Impact | Mitigation |
|------|--------|-----------|
| DR prompts are low quality → wasted relay effort | HIGH | /prompt-architect mandatory, quality scoring |
| Research gaps not identified → summer blockers remain | CRITICAL | Multiple gap scanners, coworker cross-validation |
| Dashboard too complex → owner doesn't use it | HIGH | MVP first, owner feedback drives iteration |
| Hardening misses critical edge cases | HIGH | Adversarial testing, multi-coworker review |
| System generates too many prompts → owner overwhelmed | MEDIUM | Priority queue, daily cap, owner can defer |
| Creative ideas lack scholarly grounding | MEDIUM | Gemini DR validation mandatory |
| Knowledge base grows unwieldy | LOW | Structured indexing, automated summarization |

---

## Appendix A: Memory File Sources

This design synthesizes requirements from these memory files (all created/updated 2026-04-07):

1. `project_autonomous_system_mission.md` — The 3 pillars (GOVERNING)
2. `project_dr_relay_queue.md` — The transformative DR relay idea
3. `project_dr_relay_capacity.md` — 10-20 relays/day capacity
4. `project_dr_turnaround.md` — 10min-1hr turnaround, owner is pure relay
5. `project_daily_rhythm.md` — Breakfast dashboard, university study
6. `project_summer_vision.md` — Summer 24/7 sessions, agents build
7. `feedback_own_branch_playground.md` — System's own branch
8. `feedback_not_a_bottleneck.md` — Brief-before / notify-after model
9. `feedback_owner_is_client_not_developer.md` — Machine-first design
10. `feedback_dr_is_the_investment.md` — DR is #1 investment priority
11. `feedback_ideas_are_inspiration.md` — Ideas need research before implementation
12. `feedback_user_not_architect.md` — Never ask architecture questions
13. `feedback_dashboard_reflects_data.md` — Dashboard = view onto persistent state
14. `feedback_shamela_not_library.md` — Pipeline output IS the library
15. `feedback_loves_being_asked.md` — Owner loves UX questions

## Appendix B: Existing Infrastructure Inventory

```
scripts/overnight_codex_orchestrator.py   2,714 lines  Core execution
scripts/overnight_codex_task_generator.py   732 lines  Task discovery
scripts/overnight_codex_evaluator.py        737 lines  Quality scoring
scripts/overnight_codex_backlog.py          709 lines  Backlog management
scripts/overnight_codex_common.py           586 lines  Shared utilities
scripts/overnight_codex_ideation.py          65 lines  Ideation scoring
scripts/overnight_codex_wsl_bootstrap.sh     ---        WSL launcher
scripts/overnight_codex_wsl_resume.ps1       ---        Windows resume
docs/codex/autonomous-doctrine-*.md          316 lines  Safety governance
```

Total: ~5,543 lines of Python + governance documentation.

---

## Appendix C: Coworker Review Amendments (2026-04-07)

Reviews: `docs/autonomous-system/reviews/codex_feasibility_review.md`, `docs/autonomous-system/reviews/gemini_scholarly_review.md`

### A1. Persistence Path (Codex — CRITICAL)

**Change:** `.kr/autonomous/` -> `overnight_codex/autonomous/`
**Reason:** `.kr/` is in `FORBIDDEN_EDIT_PREFIXES`. Codex tasks would be blocked on day 1.
**Status:** APPLIED to Section 3.4 above.

### A2. DR Relay Architecture Split (Codex — CRITICAL)

**Change:** DR relay engine split into two decoupled processes:
- (a) **Prompt generation scanner** — runs as a Codex task within the orchestrator, produces prompt artifacts
- (b) **Response ingestion script** — `scripts/process_dr_response.py <path>`, triggered by owner separately

**Reason:** Orchestrator's synchronous execution loop cannot accommodate async human-relay step. Trying to force it requires rewriting the core loop.
**Status:** APPLIED to Section 11.2 integration table. Full design pending.

### A3. Relay Queue Atomicity (Codex — HIGH)

**Change:** `relay_queue/` directory-based state machine replaced with single `relay_queue.json` file with status fields.
**Reason:** Moving files between directories is not atomic. Existing orchestrator uses `state.json` pattern.
**Status:** APPLIED to Section 3.4 above.

### A4. ACTIVE_AUTHORITY.md Interaction (Codex — HIGH)

**Issue:** Current state is `active_authority: claude`. Orchestrator forces `queue_only` when authority is not `codex`. System won't function without resolution.
**Resolution:** The `autonomous/nightly` branch model exempts the system from authority checks. The system's own branch IS its authority boundary — it never writes to master directly. Authority governs master commits, not branch-local work.
**Status:** DESIGN DECISION — add to Section 3.3 (Branching Model).

### A5. JSONL Record Schemas (Codex — HIGH)

**Issue:** No formal schemas defined for knowledge_base files. 3 months of autonomous operation risks schema drift.
**Action:** Define Pydantic models for each JSONL record type before Phase 1. Schemas live in `overnight_codex/autonomous/schemas/`.
**Status:** PENDING — Phase 0 deliverable.

### A6. Phase Timeline Adjustments (Codex — MEDIUM)

**Changes:**
- Phase 1: Extended from 2 weeks to 3-4 weeks (prompt-architect automation + response format variation)
- Phase 5: Add measurable milestones (DR queue depth >= 10 for 14 days, zero stale prompts > 7 days, hardening >= 3 new edge cases/week)
**Status:** PENDING — update Section 8.

### A7. Circuit Breaker for DR Relay (Codex — MEDIUM)

**Issue:** No degradation logic when owner stops relaying or DR responses are unusable.
**Design:** After 5 consecutive days with zero DR responses processed, shift 100% of capacity to Pillar 2 (hardening). Resume DR mode when owner relays again. Log stall in knowledge_base.
**Status:** PENDING — add to Section 4.6.

### A8. Scholarly Edge Case Gap Scanner (Gemini — CRITICAL)

**Change:** Add new gap scanner mining SPEC's 22 foundational principles (FP-1 through FP-22), 22 adversarial tests (ADV-E-01 through ADV-E-22), and 23 domain rules (§6.1-6.23).
**Reason:** Current [OPEN] marker scanner catches 4 gaps. The FP/ADV/domain rules encode 50-100 additional high-value research questions that current scanners miss entirely.
**Status:** PENDING — add to Section 4.2 gap sources.

### A9. Arabic Text Safety in DR Data Flows (Gemini — CRITICAL)

**Change:** Mandate Arabic text safety in prompt generation (Section 4.3) and response processing (Section 4.5):
- No Unicode normalization on Arabic text
- Byte-for-byte diacritic preservation
- UTF-8 validation on Gemini DR file bundles
- Same `\d`/`\b`/`.strip()` prohibitions from AGENTS.md
**Status:** PENDING — add to Sections 4.3 and 4.5.

### A10. Genre-Prioritized Hardening (Gemini — HIGH)

**Change:** Replace generic hardening activities (Section 5.2) with genre-prioritized plan:
1. Hadith texts (isnad errors = existential, Class A)
2. Fiqh texts (school misattribution = existential)
3. Multi-layer texts (layer conflation = existential)
4. Nahw/usul texts (terminological polysemy)
**Status:** PENDING — restructure Section 5.2.

### A11. Deferred Capabilities as Pillar 3 Source (Gemini — HIGH)

**Change:** SPEC catalogs DC-01 through DC-16. Each deferred capability should generate 2-3 DR prompts evaluating feasibility, scholarly impact, and implementation sketch for summer.
**Status:** PENDING — add to Section 6.2 idea sources.

### A12. Dashboard Scholarly Learning Content (Gemini — MEDIUM)

**Change:** Add 6 learning dimensions to dashboard Insights:
1. Science discovery ("Your library now contains X units from عقيدة")
2. Scholar network visualization (who cites whom)
3. Madhab distribution
4. Scholarly disagreement highlights
5. Evidence type awareness (quran/hadith/ijma/qiyas distribution)
6. Self-containment quality as learning signal
**Status:** PENDING — expand Section 7.2.
