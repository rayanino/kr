# Agent Team Architecture — New Chat Handoff

Open a new Claude Chat session in this same project. Paste everything below the line as your first message. Add "Take all your time." at the end.

---

<role>
You are a senior systems architect specializing in AI-agent orchestration for knowledge-critical pipelines. You have deep experience with multi-agent systems where correctness matters more than speed — medical records, legal discovery, scholarly publishing. You understand that the hardest problem in autonomous AI systems is not capability but verification: how do you know the output is right when no human is checking every step?

Your background includes designing agent teams where builder agents and verification agents have separate concerns, building quality gates that catch errors without creating bottlenecks, scaling human-in-the-loop systems so the human's attention goes only where it's needed, and working with Arabic text processing pipelines where encoding, diacritics, and normalization create silent failure modes.
</role>

<context>
## What KR Is

خزانة ريان (KR) is a personal Islamic scholarly library built from a 7-engine pipeline. Each engine processes Arabic scholarly texts from the Shamela digital library. The pipeline flows: Source → Normalization → Passaging → Atomization → Excerpting → Taxonomy → Synthesis. Errors cascade — a wrong author attribution in the source engine becomes a wrong belief in the owner's knowledge.

## What's Been Built

The source engine is COMPLETE. It took:
- €30.60 of API budget (of €100 total)
- ~118 commits to the source engine directory
- 589 passing tests (381 test functions, some parametrized)
- 204 books processed and evaluated with per-book web-search verification
- 5 confirmed bugs found and fixed through evaluation
- Multiple manual Claude Chat sessions for per-book evaluation (the bottleneck)

The build produced institutional memory:
- `reference/ENGINE_BUILD_BLUEPRINT.md` (1,173 lines) — concrete step-by-step build recipe
- `reference/DECISION_PLAYBOOK.md` (867 lines) — domain decision heuristics as trigger→action pairs
- `SILENT_FAILURES.md` — 7 patterns where AI produces output that looks correct but isn't
- `KNOWLEDGE_INTEGRITY.md` — 7 corruption threats with mitigation chains

## What Remains

6 engines, each with a draft SPEC:
- Normalization (2,007 lines) — format detection, text normalization, multi-layer processing
- Passaging (1,037 lines) — text segmentation into passage units
- Atomization (1,205 lines) — scholarly function classification (first engine where LLM does primary work)
- Excerpting (1,038 lines) — extracting self-contained scholarly positions
- Taxonomy (945 lines) — classification into Islamic science tree
- Synthesis (930 lines) — generating study entries from excerpts

## Existing Agent Definitions (in `.claude/agents/`)

8 Claude Code subagent definitions already exist but haven't been tested autonomously:
- `scholarly-verifier.md` (Opus) — verifies author/genre/metadata against web sources
- `researcher.md` (Opus) — deep web research for tools and techniques
- `code-reviewer.md` (Opus) — reviews code against SPEC
- `spec-writer.md` (Opus) — writes SPEC sections to implementation quality
- `boundary-validator.md` (Sonnet) — checks data flow between engines
- `integrity-checker.md` (Sonnet) — library data integrity verification
- `result-analyst.md` (Sonnet) — aggregates and analyzes pipeline test results
- `test-engineer.md` (Sonnet) — writes pytest suites from SPEC rules

## Tools Available

- **Claude Chat** (this interface) — planning, evaluation, architecture, web search
- **Claude Code** (`claude` CLI) — implementation, test execution, pipeline runs. Has ~1M context. Can invoke subagents. Claude Max 20x subscription.
- **GitHub** — shared artifact store, token-based HTTPS auth
- **LLM APIs** — Claude Opus 4.6, Cohere Command A (via OpenRouter), GPT-5.4 (fallback)

## The Owner

An Islamic studies student with zero technical background. He makes domain decisions (which books to study, which edition to prefer) but CANNOT validate domain correctness (author attributions, genre classifications, death dates). Domain verification is done by Claude Chat via web research. The owner's role is decision authority, not domain researcher.
</context>

<evidence_base>
## What the Source Engine Taught Us

These lessons are verified — each has specific commits, book counts, and error instances behind it.

### Where Time Actually Goes

The source engine build had 4 phases of work:
1. **SPEC design** (Claude Chat) — ~4 sessions. Produced the governing specification.
2. **Code build** (Claude Code) — ~7 sessions. Wrote 5,142 lines of engine code + tests.
3. **Per-book evaluation** (Claude Chat) — ~8 sessions. THIS WAS THE BOTTLENECK. Each session: read pipeline data for 10-15 books, web-search each book's author/genre/metadata, write structured verdicts, 5-round self-review.
4. **Bug fixes + hardening** (Claude Code + Claude Chat) — ~4 sessions. Fix specs, patch code, verify fixes.

The evaluation phase consumed more sessions than the build phase. And most of what evaluation does is mechanical: read pipeline JSON, search the web for the author name, compare, write a verdict. A human researcher would do this identically.

### What Unsupervised AI Gets Wrong

7 silent failure patterns (from SILENT_FAILURES.md):
1. Hollow examples — examples that don't test the rule they claim to illustrate
2. Circular definitions — rules that reference themselves
3. Hand-waving technology — naming tools that don't actually work for Arabic
4. Phantom metadata — fields consumed but never produced
5. Untestable rules — subjective language masquerading as precision
6. Missing error paths — no defined behavior when things fail
7. Scope creep — capabilities that belong to a different engine

And 7 knowledge corruption threats (from KNOWLEDGE_INTEGRITY.md):
T-1 Silent text corruption, T-2 Attribution error, T-3 Taxonomic misplacement, T-4 Context loss, T-5 Synthesis hallucination, T-6 Metadata poisoning, T-7 Duplication/contradiction

### What Verification Actually Catches

The 4-layer evaluation methodology:
- Layer 1 (programmatic, €0): automated consistency checks on ALL books
- Layer 2 (pattern analysis, 1 session): cohort analysis of disagreements
- Layer 3 (per-book web search, 3-5 sessions): individual verification — THE BOTTLENECK
- Layer 4 (aggregation + adversarial review, 1-2 sessions): GO/NO-GO decision

Layer 3 found: 1 author misattribution (ERR-02), 3 wrong death-date source labels, 1 consensus module bug, 12 instances of Opus tahqiq-note bias. Layer 1 (programmatic) found the patterns; Layer 3 (per-book) confirmed them. Neither alone was sufficient.

### The Self-Review Discovery

The source engine's evaluation sessions used 5-round self-review. Rounds 3-5 consistently caught errors that Rounds 1-2 missed:
- Round 3 caught a protocol violation where ALL verdicts were based on search snippets, not fetched pages
- Round 4 caught 3 wrong death-date source labels
- Round 5 applied corrections that changed 6 books' data

Without rounds 3-5, the evaluation would have contained 3 wrong source labels, 1 wrong verdict, and 1 undisclosed protocol violation — each of which would have propagated as institutional memory.

### The Playbook Enables Autonomy

The Decision Playbook captures 90%+ of the domain judgment calls as trigger→action pairs:
- "IF author_raw is empty but muhaqiq_name_raw is present → THEN check if muhaqiq is functional author"
- "IF both models agree but consensus reports disagreement → THEN cosmetic disagreement, check canonical_name_ar"
- "IF genre=hashiyah AND is_multi_layer=false → THEN internal contradiction, investigate"

These are currently read by Claude Chat. An autonomous agent could follow them mechanically.
</evidence_base>

<design_problem>
## The Core Tension

The source engine methodology (Blueprint) produces high-quality, verified output. But it requires ~8 manual Claude Chat evaluation sessions per engine. For 6 remaining engines, that's ~48 sessions of manual per-book evaluation. This doesn't scale.

The owner wants autonomous speed without sacrificing verification rigor. The question is NOT "should we use agents?" — it's "how do we decompose the work so that builder agents and researcher agents can operate autonomously while maintaining the verification quality that caught real bugs in the source engine?"

## Specific Sub-Problems to Resolve

1. **Verification without manual sessions.** Layer 3 (per-book web search) is the bottleneck. The scholarly-verifier agent definition already exists. Can it run autonomously? What supervision does it need? What error rate is acceptable? How do you detect when it's drifting (the mid-session quality gate problem)?

2. **SPEC quality at agent speed.** The Blueprint's Step 1 (SPEC design) involves reading the existing SPEC, finding defects, researching resolutions, and doing an integrity audit. Can spec-writer + researcher agents handle this, or does SPEC design fundamentally require the architect's judgment?

3. **Build session coordination.** The Blueprint's Step 2 splits the build into focused Claude Code sessions with handoff prompts. Can this be automated? The risk: Claude Code sessions that improvise when the SPEC is ambiguous (the G-2 gap from the adversarial review).

4. **Cross-engine consistency.** The source engine was built in isolation. The remaining 6 engines share contracts, shared modules, and the science tree. Agent work on one engine could break another. How do you prevent this?

5. **Budget discipline at scale.** €69.40 remains. 6 engines at €10-15 each for LLM pipeline runs alone = €60-90. Agent orchestration overhead (extra LLM calls for verification, self-review, coordination) could blow the budget. How do you keep costs bounded?

6. **The Playbook gap.** The Decision Playbook covers source engine domain knowledge. Each new engine will generate NEW domain patterns. How do those get captured when there's no manual Claude Chat session to discover them?
</design_problem>

<constraints>
- Budget: €69.40 remaining of €100 ceiling
- Owner has zero technical background — cannot debug agent failures
- Arabic text fragility: diacritics, NFC normalization, punctuation cause silent failures
- SPEC_CORE.md is behavioral authority — agents cannot override it
- Every API call must persist full output (RESULT_PRESERVATION.md)
- Human gates cannot be auto-approved (KNOWLEDGE_INTEGRITY.md Invariant 5)
- Errors must fail loudly — no silent defaults (CLAUDE.md Rule 4)
- The 2,519 books are a TEST SAMPLE, not the library — never frame work as "populating the library"
</constraints>

<instructions>
## What to Do

Clone the repo first (read the GitHub token from the `github_token` project file):
```
git clone https://<token>@github.com/rayanino/kr.git
```

Then read these files IN THIS ORDER before proposing anything:
1. `NEXT.md` — current state
2. `reference/ENGINE_BUILD_BLUEPRINT.md` — the proven methodology you're optimizing
3. `reference/DECISION_PLAYBOOK.md` §1-4 and §8-9 — the domain knowledge that enables autonomy
4. `SILENT_FAILURES.md` — what autonomous AI gets wrong
5. `KNOWLEDGE_INTEGRITY.md` — what verification must catch
6. `.claude/agents/*.md` — all 8 existing agent definitions (scan headers and workflows)
7. `skills/shared/ENGINE_PROTOCOL.md` — the governing 4-step framework

Do NOT read the full SPECs for all 6 engines. Scan the first 50 lines of each to understand scope, then go deep only where needed.

## Deliverable

A concrete agent team architecture that specifies:

1. **Agent roles** — who does what, which model, what tools, what authority level
2. **Workflow** — how agents coordinate for each Blueprint step (SPEC → Build → Evaluate → Harden)
3. **Verification architecture** — how autonomous verification maintains the quality the manual process achieved, with specific quality gates and drift detection
4. **Supervision model** — what requires human (owner or Claude Chat) attention vs. what runs autonomously, with escalation triggers
5. **Budget model** — estimated cost per engine under this architecture
6. **Playbook growth** — how new domain patterns get captured without manual sessions
7. **Risk analysis** — what could go wrong with this architecture and how to detect/recover

The deliverable should be implementation-ready — specific enough that a Claude Code session could set up the orchestration. Not a vision document. Not a framework. A concrete operational plan.

## How to Think About This

The source engine proved that rigorous methodology works. The question is not whether to follow the Blueprint — it's how to execute the Blueprint's steps with agents instead of manual sessions, without losing the rigor that makes the Blueprint valuable.

The most dangerous failure mode is building a system that looks autonomous but produces subtly wrong output that nobody catches until it corrupts the library. The source engine's evaluation found real bugs — 1 author misattribution, 3 wrong source labels, 1 consensus module bug. An autonomous system that misses those bugs is worse than a slow manual system that catches them.

Think about this the way you'd think about designing a quality assurance system for a pharmaceutical company: the goal is speed AND safety, and the correct answer is never "skip the safety checks to go faster."
</instructions>

<anti_patterns>
## What NOT to Propose

- **"Just run the agents and review the output."** This is the current system with extra steps. The owner can't review domain output.
- **"Use a supervisor agent to coordinate."** Supervisor agents are another layer of unsupervised AI. Who verifies the supervisor?
- **"Start with a simple version and iterate."** The source engine already iterated. The methodology is proven. The question is parallelizing it, not simplifying it.
- **"Build all 6 engines simultaneously."** Contract boundaries between adjacent engines must be verified sequentially. Engines share infrastructure.
- **"Skip evaluation for simple engines."** The Blueprint explicitly says evaluation rigor never decreases, even when build complexity does. The simplest engine can still have the subtlest bugs.
- **Abstract framework proposals without concrete implementation details.** The previous ENGINE_FACTORY_PLAN.md (~1,260 lines) was rejected as "too abstract and over-engineered." This is a concrete operational plan, not a framework.
</anti_patterns>
