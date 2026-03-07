# Repo Inventory — What Everything Is

## The Short Version

Your repo has **23 root markdown files**, **6 shared component directories**, **10 directories**, and a bunch of support files. Most of the root markdown files are process governance that was generated during the autonomous prep sessions. You need about 8 of them. The rest are either redundant, superseded, or only relevant to a workflow you're no longer following.

---

## ROOT FILES — What Each One Is

### Files You Need (keep, reference during build)

| File | Lines | What It Is | When You Use It |
|------|-------|------------|-----------------|
| **VISION.md** | 1613 | The complete architectural vision. Master document. | Never read whole (too big). Use `scripts/extract_vision_sections.py` for specific sections. |
| **STEERING.md** | 78 | Concise project context — product, architecture, data flow, key decisions, tech stack. | Quick orientation for any new session. The "cheat sheet" version of VISION.md. |
| **MILESTONES.md** | 262 | Task decomposition for building. M1 (source+norm), M2 (pass+atom+exc), M3 (tax+synth), etc. | Claude Code reads this to know what to build next. |
| **KNOWLEDGE_INTEGRITY.md** | 168 | Threat model — 7 ways the library can be corrupted and how to prevent each one. | Referenced during engine building. Core rule: errors in the library = errors in your mind. |
| **STATUS.md** | 115 | Current state of every component, cross-SPEC consistency, what remains. | Check before any session to know where things stand. |
| **NEXT.md** | 47 | The task directive for the next session. Currently stale (points to atomization, should point to source engine). | Read at the start of every session. We'll rewrite this. |
| **CLAUDE.md** | 48 | Root-level instructions for Claude Code. Implementation-focused, <60 lines. | Claude Code reads this automatically. |
| **HONEST_PLAN.md** | 347 | The plan we're writing right now. | Your roadmap. |

### Files That Are Useful But Not Essential Day-to-Day

| File | Lines | What It Is | Honest Assessment |
|------|-------|------------|-------------------|
| **ORCHESTRATOR.md** | 251 | Governs how Claude Code sessions run — orient, plan, build, verify, handoff. | Good document. Claude Code should read it. But it's operational, not something you need to track. |
| **IMPLEMENTATION_GATE.md** | 117 | Checklist of conditions before Claude Code starts building an engine. | Useful checklist. Some gates are already met, some aren't. Worth keeping. |
| **SILENT_FAILURES.md** | 176 | 7 patterns of "looks right but isn't" — specific to Islamic scholarly text processing. | Valuable domain-specific knowledge. Referenced during SPEC review. |
| **Makefile** | — | `make install`, `make test`, `make vision`. | Standard dev tooling. Fine. |

### Files That Were for the Autonomous Prep Workflow (largely done with)

These governed the SPEC refinement cycle that the autonomous Claude Chat sessions followed. Since you're switching to a simpler per-engine cycle (your review → build → test), most of this process machinery is no longer the active workflow.

| File | Lines | What It Is | Honest Assessment |
|------|-------|------------|-------------------|
| **SPEC_REFINEMENT.md** | 301 | The 10-step refinement cycle (cold read → threat analysis → example audit → ...). | This is the 4-session cycle we're killing. The quality checks inside it are good, but the full cycle is overkill going forward. |
| **SESSION_TYPES.md** | 217 | Defines CREATIVE, PRECISION, HARDENING, IMPL_PREP session types. | These session types drove the autonomous system. You don't need to manage session types manually. |
| **SESSION_LOG.md** | 1198 | Log of every autonomous session — what was done, decisions made, metrics. | Historical record. Useful if you need to understand why a decision was made. Not needed day-to-day. |
| **SESSION_CONTINUITY.md** | 148 | How sessions hand off to each other. | Operational for the autonomous system. Not needed for your per-engine cycle. |
| **CREATIVE_MANDATE.md** | 124 | Rules for the CREATIVE session type — invent before review, minimum 8 web searches, etc. | Drove the autonomous creative sessions. The inventions are already in the SPECs. |
| **CHALLENGE_PROTOCOL.md** | 142 | Three adversarial challenges (hostile implementer, skeptical scholar, technology maximalist). | Good self-review practice. Referenced in ORCHESTRATOR.md. Not something you manage. |
| **REVIEW_PROTOCOL.md** | 220 | How design reviews work. | Process document for the autonomous system. |
| **REFINEMENT_GUIDE.md** | 67 | Short guide to the refinement cycle. | Redundant with SPEC_REFINEMENT.md. |
| **CONTEXT_BUDGET.md** | 140 | Token budget planning for Claude Chat sessions. | Operational for Claude Chat. Not something you manage. |
| **PREPARATORY_ROADMAP.md** | 147 | The original plan for the preparatory phase. | Superseded by HONEST_PLAN.md. Historical. |
| **STRESS_TESTING.md** | 269 | Design for stress testing the pipeline at scale. | Premature — relevant at Phase 5, not now. |
| **IMPLEMENTATION_GUIDE.md** | 158 | Guide for implementation sessions. | Overlaps with ORCHESTRATOR.md. |

---

## DIRECTORIES — What Each One Is

### `/reference` — Domain knowledge and research (keep all, read selectively)

| File | What It Is | When You Use It |
|------|------------|-----------------|
| **DOMAIN.md** (750L) | Islamic scholarly domain knowledge — evidence hierarchy, integrity risks, design implications. | Claude reads during engine design. Core domain reference. |
| **ENTRY_EXAMPLE.md** (170L) | Target quality for synthesis output. The "this is what done looks like" document. | Essential. The benchmark for the synthesis engine. |
| **PIPELINE_TRACE.md** (165L) | Full 7-stage trace showing how metadata accumulates through the pipeline. | Good for understanding the data flow. |
| **USER_SCENARIOS.md** (300L+) | 8 scenarios (Day 1 through Year 3 + book briefing + science map + error correction). | Defines what the application needs to support. Relevant at Phase 5+. |
| **RESOURCES.md** (320L+) | Catalog of tools, libraries, APIs for Arabic NLP, OCR, etc. | Claude Code checks this before building custom code. |
| **kr_decisions.md** | 42 architectural decisions (D-001 through D-042). | The authority on "why was this decided this way?" |
| **PROJECT_INSTRUCTIONS.md** | The Claude Chat system prompt — identity, authority, core rules, session protocol. | Governs Claude Chat behavior. You don't read this, Claude does. |
| **RESEARCH_LOG.md** | 11 research findings from the deep research session. | Already in your project knowledge file. Reference material. |
| **POST_PREP_PLAN.md** | The previous plan (standalone experiments, phases). | Superseded by HONEST_PLAN.md. Keep for reference. |
| **JUDGE_PANEL_ARCHITECTURE.md** | Theoretical evaluation design (3-tier, rubrics, autonomous loop). | Theoretical. Parts will be used when we reach evaluation design per engine. |
| **DEEP_REASONING_PROTOCOL.md** | SPEC template, perfection standard, examples of good SPECs. | Claude reads this when writing/reviewing SPECs. Quality standard. |
| **HOW_TO_START.md** | Onboarding guide for new sessions. | Operational. |
| **SESSION_LOG.md** (reference copy) | Older session log. | Historical. |

### `/shared` — 6 shared components (draft SPECs, no code)

| Component | SPEC | Contracts | What It Is |
|-----------|------|-----------|------------|
| consensus | 405L | missing | Multi-model LLM agreement. Used by source, excerpting, taxonomy, synthesis. |
| validation | 406L | missing | Shared validation patterns. |
| human_gate | 413L | missing | Owner approval checkpoints. |
| feedback | 461L | missing | Correction storage, pattern analysis. |
| scholar_authority | 462L | missing | Scholar registry (names, dates, schools, teacher-student chains). |
| user_model | 368L | missing | Tracks what the owner has studied. |

**Honest assessment:** consensus and human_gate are needed during engine building (consensus from M1.3, human_gate from M3.4). The rest are application-layer concerns. Build incrementally as the plan says.

### `/scripts` — 9 utility scripts

| Script | What It Does |
|--------|-------------|
| orient.py | Project status overview. Run at session start. |
| check_spec_quality.py | Automated SPEC defect detection. |
| creative_verification.py | Checks §4.B creative capabilities. |
| verify_metadata_flow.py | Checks cross-engine metadata consistency. |
| session_quality_gate.py | Pre-commit quality check. |
| check_compliance.py | Compliance overview per engine. |
| refinement_status.py | Tracks refinement cycle progress (currently broken — doesn't reflect actual status). |
| extract_vision_sections.py | Read specific VISION.md sections without loading the whole file. |
| decompose_spec.py | Break a SPEC into sections for focused reading. |

**Honest assessment:** orient.py, check_spec_quality.py, and verify_metadata_flow.py are the most useful. The rest are refinement-cycle tooling.

### `/tests` — Test fixtures (44MB)

7 real source fixtures: waraqat (PDF), mughni (DOC), html_export (Shamela HTML), ibn_aqil (PDF), alfiyyah (TXT), owner_note (TXT), photo_scan (JPG). This is real test data you provided. Essential.

### `/library` — The library structure (mostly empty)

Science directories (aqidah, balagha, nahw, etc.) with taxonomy trees in YAML and empty content directories. This is where engine output will go.

### `/schemas` — Superseded

Old JSON schemas from the ABD era. Archived. The authoritative schemas are now in each engine's contracts.py (Pydantic models).

### `/interface` — GUI spec (not yet built)

GUI.md + scholar interface SPEC. Relevant at Phase 5 (application), not now.

### `/gold` — Empty

Where hand-verified baselines will go. Currently empty.

### `/experiments` — 1 script

The Arabic evaluation experiment script. Will be adapted for per-engine step 5c testing.

### `/.claude` — Claude Code environment

Settings, agents, commands, hooks, skills. Claude Code reads these automatically. You don't manage them directly.

---

## What I'd Recommend

The root has 23 markdown files. For YOUR purposes going forward, the ones you actually interact with are:

1. **HONEST_PLAN.md** — the roadmap
2. **NEXT.md** — what happens next (needs rewriting)
3. **STATUS.md** — where things stand
4. **MILESTONES.md** — the build sequence
5. **STEERING.md** — quick project context

Everything else is either for Claude (ORCHESTRATOR, CLAUDE.md, IMPLEMENTATION_GATE, KNOWLEDGE_INTEGRITY, the scripts, the .claude directory) or historical/superseded (the 10+ process governance files from the autonomous prep sessions).

The 10+ process governance files aren't hurting anything by existing — Claude reads them when relevant and ignores them otherwise. But if the clutter bothers you, they could be moved to a `reference/process/` directory to clean up the root. That's a cosmetic decision, not an architectural one.
