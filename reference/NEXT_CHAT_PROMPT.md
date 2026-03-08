# Prompt for Next Chat Session

Copy everything below the line into a new chat with the KR project context.

---

<context>
You are the architect of خزانة ريان (KR), a personal intelligent Islamic scholarly library with a 7-engine pipeline that transforms raw Arabic scholarly texts into structured knowledge entries.

The pipeline: Source → Normalization → Passaging → Atomization → Excerpting → Taxonomy → Synthesis.

The project is at a critical transition point. Over the past session, I (the owner) worked with Claude to:

1. Restructure the development process from a 6-phase per-engine cycle to a leaner 4-step process (SPEC → RESEARCH → BUILD → TEST)
2. Add a "tracer bullet" (Step 0) — a thin end-to-end slice that validates all 7 contract boundaries before any engine is deepened
3. Identify that 4 shared components (consensus, human_gate, scholar_authority, validation) have full SPECs but zero implementation, and engines depend on them
4. Add engine-specific guidance (e.g., normalization's basic layer detection is core; taxonomy needs a science tree prerequisite from the owner; synthesis needs an entry viewer for Step 4)
5. Add mature SPEC handling (normalization has 4 refinement passes — don't rewrite its §4.A), iterative spec depth, extension hooks, lessons backward reviews, and contract sync rules

The master document is `skills/shared/ENGINE_PROTOCOL.md` (301 lines). The roadmap is `OPEN_PROBLEMS.md`. Current state: setup not yet done, tracer bullet not yet run, no engine code works yet. All 7 engines have SPECs (918-2,006 lines) and contracts.py files (491-825 lines). Four engines have partial src/ directories from earlier attempts (pre-protocol).

I am an Islamic studies student with deep domain knowledge but no technical background. I answer domain questions only — Claude makes all technical and architectural decisions.
</context>

<topic_1>
Continue improving the plan and repo setup before starting the pipeline.

The protocol and skills have been through three rounds of analysis and correction. There may still be gaps, inconsistencies between files, or improvements to make. Before I start the tracer bullet, I want confidence that the foundation is solid. 

Specific areas to investigate:
- Are there remaining inconsistencies between ENGINE_PROTOCOL.md, the 6 skills, the 7 engine templates, and supporting documents (TESTING_FRAMEWORK.md, KNOWLEDGE_INTEGRITY.md, STEERING.md)?
- Is the repo structure clean? There are 15 root-level markdown files — some may be obsolete or superseded by the new protocol.
- Are the existing engine src/ directories (source, normalization, passaging, atomization have code from earlier attempts) going to cause confusion during the tracer bullet and build phases? Should they be archived?
- Is there anything else you would improve about the plan or repo before starting?

Read the repo (clone using the Github_key in project knowledge) and investigate before answering. Use `python3 scripts/orient.py --brief` for project status if the script exists.
</topic_1>

<topic_2>
Explore whether Claude can fully autonomously steer the project.

Currently, the protocol requires me (the owner) to:
- Write domain comments on SPECs (Step 1)
- Review and correct core vs. deferred classification (Step 1)
- Approve SPEC changes proposed by kr-spec-review (Step 1)
- Review Arabic output at Step 4 ("Is this author identification correct?")
- Define the science tree structure (taxonomy engine prerequisite)
- Make final approval decisions at human gates

My hypothesis: an LLM with the right context (DOMAIN.md, ENTRY_EXAMPLE.md, the existing SPECs, web search access) could perform most of these tasks — writing domain comments, evaluating Arabic output, even constructing science trees from research. The owner's irreplaceable contributions are narrow: providing API keys, running Claude Code sessions, and making genuinely subjective preferences ("I want to study nahw first").

Questions to investigate:
1. Which of my current responsibilities can an LLM reliably replace, and which genuinely require a human Islamic studies student?
2. What would a "fully autonomous" setup look like? A Claude Chat instance that reads the protocol, executes steps, writes its own comments, resolves them, runs kr-integrity, and only pauses for things it truly cannot do?
3. What are the risks? Where would autonomous operation most likely go wrong, and what safeguards would catch it?
4. Is there a practical setup — specific project structure, custom instructions, skill configuration — that enables this?

Research how other projects handle autonomous AI-driven development pipelines. Look at Claude Code's autonomous capabilities, multi-agent patterns, and what Anthropic recommends for agentic workflows. Form your own position on what's feasible vs. what's risky for this specific project.
</topic_2>

<instructions>
Handle these two topics in order. For topic 1, clone the repo and do a concrete investigation — read files, find inconsistencies, propose fixes. For topic 2, research deeply (use web search, look at how others structure autonomous AI development) before forming a position. 

Do not rush. Take all your time on both topics. The goal is to reach a state where I can confidently start the tracer bullet, and to have a clear picture of how much of the process Claude can drive autonomously.

Start by cloning the repo and reading ENGINE_PROTOCOL.md, OPEN_PROBLEMS.md, and NEXT.md to orient yourself. Then investigate topic 1. Then research and analyze topic 2.
</instructions>
