# Factory Hardening Session Briefing

**Purpose:** This document carries forward ALL findings from the roadmap revision session (2026-03-28) so the hardening session starts with full context.
**Read by:** The next Claude Chat session that does the deep factory review.
**Committed by:** Previous session's architect after completing 8 decisions + adversarial self-review.

---

## What Was Decided (8 Decisions — All Accepted)

See `reference/FACTORY_ROADMAP_v3_OUTLINE.md` for the full outline. Summary:

| # | Decision | Verdict |
|---|----------|---------|
| 1 | Factory identity | Quality guardian. BUILD mode removed. |
| 2 | WIP/TESTED boundary | `ops_manifest.json` factory_scope + per-engine `FACTORY_SCOPE.md` |
| 3 | Source engine | LLM validation COMPLETE (365 books). Owner metadata review pending. |
| 4 | Day 1 scope | Source + Normalization + Excerpting Phase 1 |
| 5 | FIX autonomy | Severity-graduated: CRITICAL/HIGH = architect, MEDIUM = auto, LOW = auto |
| 6 | PDF scans | Source engine format path extension (D-F013). Phase 3. |
| 7 | Interleaving | WSL2 first, then excerpting review is absolute priority |
| 8 | Paperclip | Smoke test during WSL2, defer to Session 8 |

Additional: D-F014 (synthesis deferred until Phase 1 Quality Level 4+), D-F015 (factory = quality guardian), D-F016 (severity-graduated FIX).

---

## Critical Findings From Self-Review (7 Findings — ALL Must Be Addressed)

### Finding 1: CRITICAL — "Codex CLI" Does Not Exist

The entire factory roadmap (v1, v2, v3 outline) references "Codex CLI" with `codex exec` commands. **This tool is wrong.** The owner has **GitHub Copilot CLI** (`copilot -p`), which is a fundamentally different and more powerful product.

**What Copilot CLI actually offers:**
- Programmatic mode: `copilot -p "prompt" --model gpt-5.3-codex --allow-all-tools`
- Custom agents: `.agent.md` files invoked with `--agent` flag (or auto-delegated)
- Model switching: `--model` flag selects from the full catalog per-prompt
- JSON output: `--output-format json` for structured parsing
- Subagents: `/fleet` coordinates parallel subagents
- AGENTS.md support: project-level instructions read automatically
- Copilot SDK: JSON-RPC programmatic integration for embedding in Python
- GitHub MCP server: native access to repos, issues, PRs
- Plan mode and Autopilot mode for different levels of oversight

**Impact:** Every reference to "Codex CLI," `codex exec`, "AGENTS.md (for Codex)" must be rewritten. Session 3's CLI setup section is based on wrong assumptions. The `cli_dispatch.py` design assumed three independent CLI tools — the actual architecture can use Copilot CLI's built-in model switching and custom agents instead.

**Architectural implication:** Cross-provider diversity (D-F002) can potentially be implemented WITHIN Copilot CLI by switching models per prompt (GPT for review, Claude for adversarial, etc.). This might simplify three CLIs to two (Claude Code as builder + Copilot CLI as multi-model reviewer/adversary).

### Finding 2: CRITICAL — Quota Limits Invalidate "$0/Call" Assumption

**Subscription strategy (owner decision):** NOT buying Copilot Pro+. Instead: individual subscriptions per provider (Claude Max already owned, Codex CLI already available, Gemini subscription if needed). This gives higher per-provider limits and genuine cross-provider diversity. The hardening session must determine exactly which subscriptions to buy based on benchmark evidence. The owner has budget for anything needed.

At 1,500/month: if factory uses GPT-5.3-Codex (1x) for reviews, that's 1,500 review interactions. If it uses Opus 4.5 (3x), that's only 500. Factory orchestrator MUST be quota-aware and route by task importance.

**Gemini CLI:** Free tier restricted to Flash models only since March 25, 2026 (Pro requires paid Google AI subscription). Flash models are weaker for complex scholarly reasoning but adequate for surface-level adversarial challenges.

**Impact:** The factory needs:
- Premium request budget tracker in the orchestrator
- Smart model routing: use 0x models (GPT-4.1) for low-stakes tasks, 1x models for reviews, 3x models only for critical scholarly judgments
- Monthly quota awareness with graceful degradation if approaching limit

### Finding 3: HIGH — Severity Classifier Has No Design

Decision 5 defines four severity levels but never specifies WHO classifies. If an LLM classifies, it's subject to same-model bias. If classification is wrong (CRITICAL → MEDIUM), the factory auto-fixes a knowledge corruption bug.

**Proposed solution: Deterministic field-level rules.**

| Finding affects... | Auto-classification |
|---|---|
| `author`, `attribution`, `school`, `genre`, `multi_layer`, `self_containment` | **CRITICAL** |
| Crash, contract violation, data loss, validation bypass | **HIGH** |
| Edge case handling, defensive code, missing validation | **MEDIUM** |
| Logging, naming, formatting, dead code | **LOW** |

This makes the most important classification entirely deterministic — no LLM judgment needed for CRITICAL (scholarly content fields).

### Finding 4: HIGH — Scholar Registry Is Empty

`library/registries/scholars.json` contains `{}` — zero entries. Phase D achieved 100% success by "populating science_scope data for major scholars before the run" but this data wasn't persisted to the canonical registry.

If the factory runs the source engine on new books, the empty registry will cause the same 70% gate_abort rate that Phase C had. This is a data initialization gap, not a code bug.

**Must be resolved in Session 1** (or before factory hunts source engine).

### Finding 5: HIGH — Copilot SDK Could Replace Custom CLI Dispatch

The Copilot SDK (Technical Preview) provides a production-tested agent runtime via JSON-RPC. Could replace `cli_dispatch.py` subprocess calls. BUT: it's preview software, and the factory needs KR-specific orchestration logic (work queues, severity, scope) that the SDK doesn't cover.

**Recommendation:** Evaluate SDK in Session 3 as dispatch layer. Keep custom orchestrator for control plane.

### Finding 6: MEDIUM — v3 Outline Still References "Codex" Throughout

The committed outline says "Codex reviews" and "Codex CLI" in multiple places. Must be corrected before the outline is used to rewrite governing documents.

### Finding 7: MEDIUM — Cross-Provider Diversity Needs Redesign

**Revised tool architecture for actual tools:**

| Role | Tool | Model | Cost per interaction |
|---|---|---|---|
| Builder | Claude Code | Opus 4.6 | $0 (Max sub, unlimited) |
| Reviewer | Copilot CLI | GPT-5.3-Codex | 1 premium request |
| Adversary (strong) | Copilot CLI | Claude Opus 4.5 | 3 premium requests |
| Adversary (cheap) | Gemini CLI | Flash | Free |
| Adversary (free) | Copilot CLI | GPT-4.1 | 0 premium requests |
| Fallback API | OpenRouter | Any model | Per-token |

Copilot CLI custom agents can encode review vs. adversary behavior. Model selection per-agent means cross-provider diversity within one tool.

---

## Owner's Actual Tool & Resource Inventory (Verified)

### Available NOW
- **Claude Code** — Opus 4.6, Max subscription, unlimited usage
- **Claude Chat** — Opus 4.6 (this tool, the architect)
- **ChatGPT** — Available for relay, has deep research mode, strong reasoning
- **Copilot CLI** — Currently Student plan (300 requests). NOT upgrading to Pro+ — individual per-provider subscriptions preferred. Hardening session decides which.
- **Gemini CLI** — Free tier (Flash models only, 60 RPM / 1,000 RPD)
- **OpenRouter API key** — In repo, per-token access to any model
- **GitHub Pro** — Free via student pack
- **$100 Azure credits** — Available for API fallback or cloud services
- **OpenAI API key** — In repo project files
- **Anthropic API key** — In repo project files  
- **Mistral API key** — In repo project files
- **2,519 Shamela exports** — Local on owner's Windows PC
- **Windows PC** — 24/7 available for factory operation

### Available models via Copilot CLI (from owner's screenshot)
- Claude Sonnet 4.5 (default, 1x)
- Claude Haiku 4.5 (0.33x)
- Claude Opus 4.5 (3x)
- Claude Sonnet 4 (1x)
- GPT-5.3-Codex (1x)
- GPT-5.2-Codex (1x)
- GPT-5.2 (1x)
- GPT-5.1-Codex-Max (1x)
- GPT-5.1-Codex (1x)
- GPT-5.1 (1x)
- GPT-5.4 mini (0.33x)
- GPT-5.1-Codex-Mini Preview (0.33x)
- GPT-5 mini (0x — unlimited)
- GPT-4.1 (0x — unlimited)

### Owner's stated principles
- **Budget: UNLIMITED.** Will buy any subscription, tool, or resource needed.
- **Time: UNLIMITED.** Quality is the only metric.
- **Willingness:** Will relay prompts to ChatGPT, CC, Gemini on demand.
- **Platform:** Windows (WSL2 for factory), no macOS.

---

## What the Hardening Session Must Do

### Focus: Tools and Technology

The owner explicitly asked for heavy hammering on tools and technology integration. "There is so many tools, CLIs, LLMs that we can integrate into this factory to make it even more bulletproof." Specific angles to investigate:

1. **Arabic/Islamic scholarly tools** — Are there specialized models, APIs, or databases for classical Arabic text analysis? (e.g., OpenITI corpus tools, KITAB text reuse detection, Shamela's own API if any, Arabic NLP libraries like CAMeL Tools, arabert models, arabic-stopwords, etc.)

2. **Testing frameworks** — Beyond pytest: property-based testing (Hypothesis), mutation testing, fuzzing for Arabic text edge cases, snapshot testing for pipeline output stability.

3. **Evaluation methodologies** — How do other scholarly digital library projects evaluate extraction quality? What can we learn from OpenITI's evaluation methodology, HathiTrust's Arabic collection QA, or academic NER evaluation practices?

4. **CI/CD tools** — GitHub Actions marketplace for Arabic text processing, code quality tools that understand Python + Arabic strings, etc.

5. **Model evaluation harnesses** — Tools designed for evaluating LLM output quality on structured extraction tasks (not just chat). OpenAI Evals, Anthropic's eval framework, custom harnesses.

6. **Monitoring and observability** — For a factory running 24/7: structured logging, alerting (Telegram/Discord bots), dashboard options beyond custom HTML.

### Critical timing insight

By the time the factory is operational (Sessions 7-8, ~week 8-10), the excerpting engine will likely be COMPLETE (the owner is working on it in parallel). This means:

- The factory's Day 1 scope should be planned for ALL of Phase 1, not just "Source + Norm + Excerpting Phase 1"
- The benchmark (Session 4-5) should include excerpting tasks, not just source engine tasks
- The synthetic data system (Session 4.5) should generate adversarial data for excerpting too
- The WIP/TESTED boundary for excerpting should plan for rapid expansion from "Phase 1 only" to "all phases"

### Work methodology

Work in small focused steps:
1. Pick one aspect (e.g., "Arabic scholarly tools landscape")
2. Do your research and analysis
3. Prepare relay prompts for ChatGPT (deep research) and Claude Code (hands-on verification)
4. Owner relays, brings back results
5. Architect integrates findings
6. Move to next aspect
7. Repeat until every aspect of the roadmap is bulletproof

The owner also has Gemini available for relay.

---

## Repo State (as of 2026-03-28)

```
Latest commits:
60238bcf docs(excerpting): sync SPEC.md stale model + threshold values (613 pass)
6fb26a65 overnight: boundary-exhaustive hardening — 16 new threshold tests (613 pass)
4e41c4da overnight: initialize overnight session
40ef2e00 fix: correct test counts in v3 outline
9ad6f4b7 docs: FACTORY_ROADMAP_v3 outline — 8 decisions

Test counts (verified by grep):
- Source engine: 398 test functions
- Normalization: 404 test functions
- Excerpting: 584+ test functions (613 now per latest commit)

Source engine: Transition gate APPROVED (a21aab9a)
- 365 books LLM-validated (Phases C/D/E)
- Phase D: 204/204 success (100%)
- Owner metadata review: PENDING

Excerpting engine:
- Phase 1: deterministic, proven
- Phase 2-3: LLM phases, model roles recently updated
- 5-book integration run complete (41 excerpts)
- 30-book owner probe: NOT YET STARTED

Factory infrastructure:
- overnight_orchestrator.py: 1,405 lines, battle-tested
- 19 hooks, 13 skills, 15 rules in CC environment
- CI/CD: pytest + metadata flow + contract validation on push
```

---

## Documents to Read in the New Session

1. `reference/FACTORY_ROADMAP_v3_OUTLINE.md` — the 8 decisions (this session's output)
2. `reference/FACTORY_HARDENING_BRIEFING.md` — THIS FILE (carries forward findings)
3. `reference/FACTORY_ROADMAP_v2.md` — current governing roadmap (to be superseded)
4. `reference/AUTONOMOUS_QUALITY_SYSTEM.md` — current AQS (needs BUILD removal + FIX redesign)
5. `reference/TEAM_ARCHITECTURE.md` — current teams (needs BUILD team removal)
6. `scripts/overnight_orchestrator.py` — existing 1,405-line orchestrator to extend
7. `engines/source/VALIDATION_PLAN.md` — source engine validation state (partially stale)
8. `NEXT.md` — current active task (excerpting model role research)
