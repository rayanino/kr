KR Factory Setup — Building the autonomous environment for خزانة ريان

<purpose>
This is not a KR engine-building session. This is the meta-project: building the factory that builds the product. Before we build another engine, we're building the infrastructure, tools, processes, and environment that will let this project run autonomously for months or years — with the owner only doing what a human genuinely must do (reading Arabic output, making domain judgments, providing resources).

Budget: unlimited. Time: unlimited. Quality: the only metric.
The goal is an environment where the owner can focus on his Islamic studies while the factory builds his future study companion.
</purpose>

<current_state>
WHAT EXISTS (the raw materials):
- KR repo at github.com/rayanino/kr with 2 completed engines (source, normalization) and 1 in-progress (excerpting — 593 tests, first real LLM call succeeded, ready for 5-book integration test after model config update)
- 9 KR-specific skills in /mnt/skills/user/ (kr-build-prep, kr-core-extract, kr-evaluate, kr-gating-transitions, kr-integrity, kr-preparing-cc-handoffs, kr-research, kr-reviewing-cc-output, kr-spec-review)
- 8 general skills (critical-review, deep-research, thinking-frameworks, prompt-engineer, brainstorming, content-research-writer, article-extractor, ship-learn-next)
- 8 protocols in reference/protocols/ (HANDOFF_PROTOCOL.md, REVIEW_PROTOCOL.md, QUALITY_AXIOM.md, HANDOFF_CHECKLIST_TEMPLATE.md, REVIEW_CHECKLIST_TEMPLATE.md, LLM_INTEGRATION_TEST_PROTOCOL.md, DECISION_DISCIPLINE.md, AGENT_HANDOFF_FORMAT.md)
- reference/ENGINE_FACTORY_PLAN.md (1261 lines, written earlier — may be partially stale)
- reference/ENGINE_BUILD_BLUEPRINT.md, reference/AGENT_ARCHITECTURE.md
- 20,000+ Shamela .htm exports available locally
- MCP servers available: GitHub, Google Drive, Filesystem, Desktop Commander, Context7, Scholar Gateway, exa, tavily
- Claude Chat (Opus 4.6) as architect, Claude Code (Opus 4.6, 1M context, max thinking) as builder
- OpenRouter for multi-model LLM calls (Anthropic, OpenAI, Google, Cohere, etc.)
- Owner is on Windows, has zero technical background, is an Islamic studies student

WHAT'S BROKEN (known pain points from 30+ sessions):
1. Owner is a human copy-paste relay between Claude Chat and Claude Code. Every handoff requires manual message passing.
2. Skills were written reactively as problems appeared. Some are stale, some conflict, some overlap.
3. No domain reviewer exists. The architect (Claude Chat) makes domain judgments about Arabic scholarly text without being a domain expert. No second opinion.
4. No project dashboard. Owner has to ask the architect "where are we?" every session.
5. Protocols depend on the architect remembering to invoke them. Failed multiple times (Sessions 5, 6, 7 all had protocol-skip failures).
6. Memory entries accumulate and go stale. No systematic cleanup.
7. Context degradation across long chats causes quality to drop. Known problem, manually managed by starting new chats.
8. No systematic decision log the owner can read independently.
9. Quality enforcement is entirely the architect's discipline. If the architect has a bad day, errors reach the pipeline.
10. No automated regression testing across engines when changes are made.
11. External knowledge sources (KITAB/OpenITI corpus metadata, Arabic scholarly databases) not integrated.
12. No CI/CD — tests only run when someone remembers to run them.
13. No structured way for the owner to review Arabic output (excerpts, teaching units) — just raw JSON.
</current_state>

<vision>
The end state is a system where:
- The owner opens a status page and sees: which engine is being built, what phase it's in, what needs his attention, what's blocked
- Engine building follows a proven, automated pipeline: SPEC → build → test → evaluate → harden → complete
- CC receives handoffs that are automatically validated before delivery
- CC's output is automatically tested before the architect reviews it
- Domain review of Arabic output happens through a structured workflow with multiple independent LLM reviewers
- The architect's protocol compliance is enforced structurally, not by willpower
- Decisions are logged with rationale, searchable, and permanent
- Skills are versioned, tested, and maintained like code
- The owner only intervenes for: reading Arabic excerpts, making final domain judgments, providing resources (API keys, files, access), and approving major transitions
- The factory can run for months, producing incrementally better output, without the owner needing to manage the process
</vision>

<your_task>
This first chat is the STRATEGIC PLANNING session. Do not start building anything yet.

1. AUDIT: Read the existing factory plan (reference/ENGINE_FACTORY_PLAN.md), the agent architecture (reference/AGENT_ARCHITECTURE.md), the build blueprint (reference/ENGINE_BUILD_BLUEPRINT.md), every protocol in reference/protocols/, and every KR skill. Assess what works, what's stale, what's missing, what conflicts.

2. RESEARCH: Investigate what tools, MCP servers, automation approaches, and collaboration patterns exist that could solve the pain points listed above. Think broadly — CI/CD for LLM pipelines, MCP-based agent coordination, structured review workflows, project management for AI-driven development, Arabic NLP tools and datasets.

3. DESIGN: Produce a master plan with:
   - Every workstream that needs to happen (agent coordination, skill library, quality infrastructure, project management, domain review pipeline, owner interface, model strategy, external knowledge integration, sustainability/maintenance)
   - For each workstream: what it is, why it matters, what the deliverables are, estimated effort, dependencies on other workstreams
   - A recommended execution order (what to build first because other things depend on it)
   - For each workstream: whether it needs its own dedicated chat or can be done inline

4. VALIDATE: Before presenting the plan, stress-test it. What's the weakest link? What would cause the factory to degrade after 3 months? What am I overengineering? What am I missing?

Use kr-research, thinking-frameworks, deep-research, brainstorming, and critical-review skills. Take all your time. This plan governs the next 6-12 months of the project.
</your_task>

<constraints>
- Do not touch the KR repo or any engine code in this session. This is planning only.
- Do not assume any tool or approach works with Arabic until verified with evidence.
- Do not optimize for speed. Optimize for: correctness, sustainability, and owner autonomy.
- The owner has zero technical background. Every owner-facing interface must be simple and non-technical.
- The owner is an Islamic studies student at a Belgian university. His time is limited and valuable. Every minute of his time the factory requires must be genuinely irreplaceable by an LLM.
</constraints>
