# DR Relay Prompts — Batch 0 (System Design) — OPTIMIZED

**Generated:** 2026-04-07
**Status:** OPTIMIZED via /prompt-architect — ready for owner relay
**Context:** These 3 prompts validate the autonomous system DESIGN.md before implementation begins.

---

## DR-DESIGN-01: ChatGPT DR — System Architecture + Dashboard + Creative Frameworks

**Target:** ChatGPT Deep Research
**Priority:** HIGH
**Unblocks:** DQ-001 (dashboard tech), DQ-004 (DR response processing), DQ-007 (creative frameworks)
**Estimated time:** 20-40 minutes

### RELAY PROMPT (copy-paste as-is into ChatGPT Deep Research)

```
You are a systems architect specializing in AI-agent-maintained infrastructure and local-first developer tools. You have access to the private GitHub repository for this project — read files directly from the repo when referenced below. Do not ask me to paste file contents.

Repository: github.com/rayanino/kr
Branch: excerpting-foundations-hardening-20260404

Read these files before answering:
- docs/autonomous-system/DESIGN.md (the full system design — your primary reference)
- scripts/overnight_codex_orchestrator.py (existing execution engine, 2,714 lines)
- scripts/overnight_codex_task_generator.py (task discovery system, 732 lines)
- scripts/overnight_codex_common.py (shared utilities and data models, 586 lines)
- docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md (safety governance constraints)

The project is KR (Khizanat Rayan) — a personal Islamic scholarly library built entirely by AI agents (Claude Code, Codex CLI, Gemini CLI). I am the owner/client, not a developer. I relay prompts and provide feedback. The autonomous system runs April 9 to July 1 (83 days) while I study at university. Its primary mission: generate Deep Research prompts for me to relay (10-20 per day, 830-1660 total).

Investigate these three questions. For each, provide a specific recommendation with justification, not a list of options for me to choose from.

QUESTION 1: DASHBOARD TECHNOLOGY

I need a browser-based dashboard as my only interface to the system. It must support:
- A prioritized DR relay queue where I copy-paste prompts into DR tools
- A findings feed showing what the system discovered overnight
- An input form where I submit ideas and feedback
- Pipeline health metrics and research progress charts

Score each candidate technology against these five criteria (1-5 scale), then recommend the winner:

| Criteria | Weight |
|----------|--------|
| Agent maintainability: Can Claude Code and Codex CLI reliably create and modify this? | 30% |
| Zero-config launch: Does it work by opening a file or running one command? | 25% |
| Interactivity: Can I submit forms, expand/collapse sections, copy text? | 20% |
| Offline/local: No cloud, no accounts, no network dependency? | 15% |
| Data binding: How naturally does it read from JSON/JSONL files in the repo? | 10% |

Candidates to evaluate:
a) Static HTML + vanilla JS generated from JSON (open index.html)
b) Python local server (Flask/FastAPI with HTMX)
c) Single-file HTML app with embedded JS (like TiddlyWiki approach)
d) Any other approach you discover that fits better

Deliver: a scored comparison table, your top recommendation, and a 5-file sketch of the recommended architecture (file names, responsibilities, data flow).

QUESTION 2: DR RESPONSE PROCESSING PIPELINE

When I relay a DR response, I download it as a .md file and tell the system the file path. The system must:
- Parse the markdown and extract structured findings
- Classify each finding by type (architecture decision, edge case, scholarly insight, technology recommendation, risk, open question)
- Cross-reference against the existing knowledge base at .kr/autonomous/knowledge_base/
- Update research_gaps.json to close resolved gaps and open new ones
- Generate follow-up DR prompts when the response reveals new questions

The challenge: DR responses have no consistent format. ChatGPT DR, Claude DR, and Gemini DR each produce different markdown structures (headers, lists, tables, prose paragraphs, code blocks).

Deliver: a processing pipeline design with these stages clearly defined — ingestion, parsing, classification, cross-referencing, gap-update, follow-up generation. For the parsing stage, recommend a specific approach that handles format variation without brittle regex. Include error handling for malformed or empty responses.

QUESTION 3: CREATIVE IDEA GENERATION FOR LONG-GESTATION PROJECTS

The system must generate ideas that take days or weeks to fully develop — architecture proposals, novel cross-engine approaches, scholarly methodology innovations. Quick improvements are excluded (those happen in summer).

The existing 8-dimension scoring system is in scripts/overnight_codex_evaluator.py. Read it for context.

Deliver: a recommended framework for systematic idea generation that an autonomous AI system can execute without human guidance. The framework must:
- Produce ideas grounded in the actual codebase and SPEC files (not generic software advice)
- Include a research phase where each idea triggers 1-3 DR prompts for validation
- Define when an idea is "summer-ready" (fully researched, validated, implementation-sketched)
- Integrate with the existing 8-dimension evaluator rather than replacing it

Do not suggest generic brainstorming techniques. Ground every recommendation in what you observe in the actual codebase.

For all three questions: cite specific files, line numbers, or code patterns from the repo when justifying your recommendations. Generic advice without repo grounding is not useful.
```

---

## DR-DESIGN-02: Claude DR — Research Prioritization Strategy

**Target:** Claude Deep Research
**Priority:** HIGH
**Unblocks:** DQ-002 (topic distribution), DQ-005 (batch sizing), DQ-006 (completeness detection)
**Estimated time:** 30-60 minutes

### RELAY PROMPT (copy-paste as-is into Claude Deep Research)

```
You are a research strategy director for a large-scale software project that processes Arabic Islamic scholarly texts. Your task: design the research prioritization framework for an autonomous system that will generate 830-1660 Deep Research prompts over 83 days (April 9 to July 1, 2026).

You have access to the private GitHub repository. Read these files in order before answering:

1. docs/autonomous-system/DESIGN.md — the system design (read first for full context)
2. CLAUDE.md and AGENTS.md — project governance and rules
3. NEXT.md — current project frontier and recent accomplishments
4. engines/excerpting/SPEC.md — the most mature engine SPEC (read sections 1-4 for scope, section 6 for recent hardening)
5. engines/taxonomy/SPEC.md — taxonomy engine (less mature, read sections 1-2 for scope)
6. engines/passaging/SPEC.md, engines/atomization/SPEC.md, engines/synthesis/SPEC.md — early-draft SPECs

Repository: github.com/rayanino/kr
Branch: excerpting-foundations-hardening-20260404

The pipeline processes Arabic Islamic scholarly texts through 7 engines: Source, Normalization, Passaging, Atomization, Excerpting, Taxonomy, Synthesis. Source and Normalization are complete. Excerpting has 942 tests and is in hardening. Taxonomy is under construction. The other three have first-draft SPECs only.

The owner relays 10-20 DR prompts per day to three targets: ChatGPT DR (architecture, feasibility), Claude DR (scholarly reasoning, quality), and Gemini DR (Islamic methodology, pedagogy). Each DR session takes 10-60 minutes and produces a markdown report. The goal: by July 1, all research needed for the summer full-build is complete. Zero "we need to research this first" blockers remain.

Answer these four questions. Every answer must be specific enough to implement as a Python data structure (dict, enum, list of rules). Do not provide general project management advice.

QUESTION 1: RESEARCH TOPIC DISTRIBUTION

Propose a percentage allocation of DR sessions across these five categories:

a) Engine-specific: excerpting hardening, taxonomy tree design, passaging rules, atomization edge cases, synthesis architecture
b) Cross-cutting: Arabic text handling, multi-model consensus (D-041), metadata flow (D-023), error handling patterns
c) Scholarly domain: Islamic sciences classification, madhab-specific text handling, hadith methodology, Quranic citation detection, tafsir commentary structure
d) Architecture/design: pipeline optimization, data model refinement, test strategy, performance
e) Creative/visionary: future capabilities, local LLM training data strategy, scholar interface concepts, cross-engine innovations

For each category, state:
- The percentage allocation and absolute session count (at 10/day baseline = 830 total)
- The top 3 specific research questions to answer first
- The diminishing-returns threshold: after how many DRs does additional research in this category stop producing actionable new information? What signal indicates saturation?
- Which DR target (ChatGPT/Claude/Gemini) is primary for this category and why

Deliver as a table with these columns: Category, Allocation %, Sessions (of 830), Top 3 Questions, Saturation Signal, Primary DR Target.

QUESTION 2: RESEARCH COMPLETENESS FRAMEWORK

Design a state machine for research topics. Each topic moves through states based on observable signals.

Define these states with concrete transition rules:
- IDENTIFIED: a gap exists but no DR has been sent
- ACTIVE: at least one DR dispatched, findings arriving
- DEEP: multiple DRs dispatched, findings are refining rather than discovering
- SATURATED: additional DRs produce no new actionable information
- BLOCKED: research depends on another topic that is not yet SATURATED

For each transition (e.g., ACTIVE to DEEP), define the exact signal that triggers it. Signals must be measurable by code, not by human judgment. Examples of measurable signals:
- Number of DR responses received on this topic
- Percentage of findings that overlap with previous findings on the same topic
- Number of new SPEC sections or code changes triggered by the latest DR
- Number of follow-up questions generated vs. questions resolved

Deliver as a state transition table: From State, To State, Trigger Signal, Measurement Method.

QUESTION 3: TEMPORAL PHASING STRATEGY

The 83-day period has different strategic needs at different phases. Design a three-phase strategy:

- Phase 1 (Days 1-28, April 9 to May 6): What should the DR distribution look like? What is the strategic priority?
- Phase 2 (Days 29-56, May 7 to June 3): How does the distribution shift? What signals trigger the shift?
- Phase 3 (Days 57-83, June 4 to July 1): Final push. What changes? How does the system ensure zero blockers remain?

For each phase, specify: category distribution percentages, daily prompt generation target, queue management strategy (batch at breakfast vs. continuous refresh), and the criteria for transitioning to the next phase.

Deliver as three phase blocks with these fields: Phase Name, Date Range, Distribution (% per category), Daily Target, Queue Strategy, Transition Criteria.

QUESTION 4: RESEARCH DEPENDENCY GRAPH

Some research topics depend on others. For example, taxonomy tree design depends on excerpting granularity decisions (you cannot classify what you have not defined how to extract).

Analyze the project files and identify:
- The 15-20 most important research topics across all categories
- The dependency relationships between them (which must be researched first)
- The critical path: the longest chain of dependent topics that determines the minimum calendar time needed
- Parallelizable clusters: groups of topics with no dependencies between them that can be researched simultaneously

Deliver as: a dependency list (topic A must precede topic B, with reason), the critical path sequence, and 3-5 parallel clusters.

Ground every recommendation in specific files, SPEC sections, or code patterns from the repository. If you recommend prioritizing "taxonomy tree design," cite the specific SPEC section or code gap that makes it urgent.
```

---

## DR-DESIGN-03: Gemini DR — Islamic Scholarly Workflow Mapping

**Target:** Gemini Deep Research
**Priority:** HIGH
**Unblocks:** DQ-003 (18 sciences mapping), DQ-008 (dangerous excerpting edge cases)
**Estimated time:** 30-60 minutes
**IMPORTANT:** Gemini DR CANNOT access the repo. Owner must upload file bundle.

### FILE BUNDLE TO UPLOAD

Before pasting the prompt, upload these 4 files to the Gemini DR session:
1. `docs/autonomous-system/DESIGN.md`
2. `engines/excerpting/SPEC.md`
3. `.claude/rules/arabic-scholarly-conventions.md`
4. `AGENTS.md`

### RELAY PROMPT (copy-paste as-is into Gemini Deep Research, AFTER uploading files)

```
You are a senior Islamic studies methodologist with deep expertise in the classical Islamic sciences tradition (ulum al-islamiyya) and modern digital humanities approaches to Islamic scholarly texts. I have uploaded 4 files from my project — read all of them before answering.

The project is KR (Khizanat Rayan) — an intelligent personal Islamic scholarly library. The pipeline processes Arabic scholarly texts and extracts structured scholarly knowledge through 7 engines. I am designing an autonomous system that will generate 830-1660 Deep Research prompts over 83 days (10-20 per day, relayed to ChatGPT DR, Claude DR, and Gemini DR). The goal: all research needed for the summer full-build is complete by July 1, 2026.

The uploaded files are:
- DESIGN.md: the autonomous system design (full context)
- SPEC.md: the excerpting engine specification (the most mature engine, 942 tests)
- arabic-scholarly-conventions.md: rules for handling Arabic scholarly text
- AGENTS.md: project governance including Arabic text rules and scholarly conventions

Answer these three questions with scholarly depth and precision. Use real Arabic examples where relevant.

QUESTION 1: MAPPING DR RESEARCH TO THE 18 ISLAMIC SCIENCES

The pipeline must handle texts from all major Islamic sciences. For EACH of these 18 sciences, identify what Deep Research should investigate before the summer build:

a) Unique text structures the pipeline must handle (e.g., isnad chains in hadith, verse-commentary interleaving in tafsir, legal case structures in fiqh)
b) Classification challenges specific to this science (how to distinguish sub-genres)
c) Excerpting boundary challenges (where should excerpts begin and end for scholarly coherence?)
d) Cross-reference patterns (how do texts in this science reference other sciences?)
e) The 2-3 most important DR questions for this science

Sciences to cover:
1. Tafsir (Quranic exegesis)
2. Hadith (Prophetic traditions)
3. Fiqh (jurisprudence)
4. Usul al-Fiqh (principles of jurisprudence)
5. Aqidah (creed/theology)
6. Tasawwuf (spirituality/Sufism)
7. Sirah (Prophetic biography)
8. Tarikh (Islamic history)
9. Lugha (Arabic language/lexicography)
10. Nahw (Arabic grammar)
11. Sarf (Arabic morphology)
12. Balagha (Arabic rhetoric)
13. Mantiq (logic)
14. Falsafa (philosophy)
15. Ilm al-Kalam (dialectical theology)
16. Tabaqat (biographical dictionaries)
17. Mustalahat al-Hadith (hadith terminology)
18. Ilm al-Rijal (narrator criticism)

For each science, deliver a structured block: Science Name (Arabic + English), Unique Structures, Classification Challenges, Boundary Challenges, Cross-References, Top DR Questions.

QUESTION 2: DANGEROUS EXCERPTING EDGE CASES FOR SCHOLARLY INTEGRITY

Based on your knowledge of Islamic scholarly texts, what are the most dangerous edge cases where automated excerpting could corrupt scholarly meaning? I need cases where:

- A boundary placed in the wrong position changes the legal ruling (e.g., cutting before a taqyid/restriction that limits a general ruling)
- An excerpt taken out of context reverses the author's intended meaning (e.g., quoting the opponent's view as the author's view)
- A classification error attributes a view to the wrong scholar or school (e.g., confusing the muallif's view with the muhaqqiq's commentary)
- A structural misread conflates the author's commentary with quoted source material (e.g., not detecting the boundary between matn and sharh layers)

For each edge case, provide:
- A real example from Islamic scholarly literature (with Arabic text)
- Why it is dangerous (what knowledge corruption it causes)
- How the pipeline should detect and handle it
- Which SPEC rule from the uploaded SPEC.md relates to this case (or which rule is missing)

Provide at least 10 edge cases, ordered by danger level (most dangerous first).

QUESTION 3: SCHOLARLY COMPLETENESS CRITERIA

When the pipeline excerpts a section of an Islamic scholarly text, how does a traditional Islamic scholar determine if the excerpt is "complete" (self-contained for study)? What are the traditional criteria for:

a) A complete legal discussion (mas'ala) — what are the minimum components? (statement of the issue, evidence, madhab positions, tarjih/weighing, ruling)
b) A complete hadith commentary unit — when does a hadith commentary begin and end? (hadith text, takhrij, sharh al-gharib, extraction of rulings, reconciliation with other hadiths)
c) A complete tafsir passage — what constitutes a self-contained tafsir unit? (ayah range, sabab al-nuzul, linguistic analysis, legal extraction, intertextual references)
d) A complete biographical entry (tarjama) — minimum components? (name, nasab, birth/death, teachers, students, works, scholarly assessment)

For each type, provide:
- The traditional scholarly criteria (citing classical methodology sources where possible)
- How these criteria translate into machine-detectable signals (what patterns in the text indicate completeness?)
- What the SPEC.md's current boundary detection approach handles and what it misses

Scholarly precision matters more than breadth. Cite classical sources (e.g., al-Suyuti's Tadrib al-Rawi for hadith methodology, al-Zarkashi's al-Burhan for tafsir methodology) where relevant.
```

---

## Relay Order

| Step | Action | Target |
|------|--------|--------|
| 1 | Copy-paste DR-DESIGN-01 prompt | ChatGPT Deep Research |
| 2 | Copy-paste DR-DESIGN-02 prompt | Claude Deep Research |
| 3 | Upload 4 files, THEN copy-paste DR-DESIGN-03 prompt | Gemini Deep Research |

All 3 can be relayed in parallel — no dependencies between them.
