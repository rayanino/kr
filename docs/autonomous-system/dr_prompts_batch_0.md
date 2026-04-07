# DR Relay Prompts — Batch 0 (System Design)

**Generated:** 2026-04-07
**Status:** DRAFT — awaiting /prompt-architect optimization
**Context:** These 3 prompts validate the autonomous system DESIGN.md before implementation begins.

---

## DR-DESIGN-01: ChatGPT DR — System Architecture Feasibility + Dashboard Technology

**Target:** ChatGPT Deep Research
**Priority:** HIGH
**Unblocks:** DQ-001 (dashboard technology), DQ-004 (DR response processing), DQ-007 (creative idea frameworks)
**Estimated time:** 20-40 minutes

### Prompt (DRAFT — to be optimized by /prompt-architect)

```
CONTEXT: I'm building an autonomous system for a personal Islamic scholarly library project (KR — Khizanat Rayan). The system runs April 9 to July 1 (83 days) while I'm at university, and its primary mission is generating Deep Research prompts that I relay to ChatGPT/Claude/Gemini DR (10-20 per day = 830-1660 research sessions before summer).

The system design document is at: docs/autonomous-system/DESIGN.md
The existing overnight infrastructure is at: scripts/overnight_codex_orchestrator.py (2,714 lines), scripts/overnight_codex_task_generator.py (732 lines), and related files in scripts/overnight_codex_*.py
The safety governance document is at: docs/codex/autonomous-doctrine-2026-04-09-to-2026-07-01.md

QUESTIONS (please investigate each thoroughly):

1. DASHBOARD TECHNOLOGY
   The owner (me) needs a browser-based dashboard as the single interface for:
   - Viewing a prioritized DR relay queue (copy-pasteable prompts)
   - Reviewing findings from autonomous runs
   - Submitting ideas/feedback
   - Seeing pipeline health and research progress metrics
   
   The dashboard must be local-only (no cloud hosting), launchable from the system, and maintained by AI agents (not human developers). The data is stored as JSON/JSONL in the repo.
   
   Evaluate these options with pros/cons/recommendation:
   a) Static HTML generated from JSON (zero server dependency)
   b) Python-based local web app (Flask/FastAPI with HTMX or similar)
   c) Electron or Tauri app (desktop native)
   d) Something else I haven't considered
   
   Key constraint: the dashboard is built and maintained entirely by AI coding agents (Claude Code, Codex CLI). It must be simple enough that agents can reliably modify it.

2. DR RESPONSE PROCESSING
   When I relay a DR response (download the .md file, tell the system the path), the system needs to:
   - Parse the response and extract structured findings
   - Cross-reference against existing knowledge base
   - Update relevant SPEC sections and research gaps
   - Generate follow-up prompts
   
   How should the system process unstructured DR markdown responses into structured, machine-actionable findings? What parsing approach works best for varied DR output formats?

3. CREATIVE IDEA GENERATION FRAMEWORKS
   The system needs to generate big ideas that take days/weeks to develop (not quick improvements). These are the "what to build in summer" items. The existing creative evaluator uses an 8-dimension scoring system.
   
   What frameworks or methodologies produce the highest-value long-gestation ideas for software/research projects? How can an autonomous system generate ideas that a human + AI team would find genuinely novel?

Please provide specific, actionable recommendations for each question. Include technology names, library versions, and architecture patterns where relevant.
```

---

## DR-DESIGN-02: Claude DR — Research Prioritization Strategy

**Target:** Claude Deep Research
**Priority:** HIGH
**Unblocks:** DQ-002 (optimal DR topic distribution), DQ-005 (batch sizing), DQ-006 (research completeness detection)
**Estimated time:** 30-60 minutes

### Prompt (DRAFT — to be optimized by /prompt-architect)

```
CONTEXT: I'm building the KR (Khizanat Rayan) autonomous system — a personal Islamic scholarly library pipeline. The system's #1 mission: generate Deep Research prompts that I relay to ChatGPT/Claude/Gemini DR. I can relay 10-20 per day for 83 days = 830-1660 research sessions before summer 2026.

The pipeline processes Arabic Islamic scholarly texts through 7 engines:
Source → Normalization → Passaging → Atomization → Excerpting → Taxonomy → Synthesis

Current state:
- Source + Normalization: COMPLETE (proven correct)
- Excerpting: 942 tests, build complete, in hardening phase. SPEC at engines/excerpting/SPEC.md
- Taxonomy: parallel build, trees NOT yet trustworthy
- Passaging, Atomization, Synthesis: first-draft SPECs only

Key files for context:
- System design: docs/autonomous-system/DESIGN.md
- Excerpting SPEC: engines/excerpting/SPEC.md (the most mature SPEC)
- Project instructions: CLAUDE.md and AGENTS.md
- Current frontier: NEXT.md

QUESTIONS (please investigate each deeply):

1. RESEARCH TOPIC DISTRIBUTION
   With 830-1660 DR sessions available, how should I distribute research across:
   a) Engine-specific questions (excerpting hardening, taxonomy tree design, passaging rules, atomization edge cases, synthesis architecture)
   b) Cross-cutting concerns (Arabic text handling, multi-model consensus, metadata flow, error handling)
   c) Scholarly domain questions (Islamic sciences classification, madhab-specific handling, hadith methodology, Quranic citation handling)
   d) Architecture/design questions (pipeline optimization, data model refinement, test strategy)
   e) Creative/visionary questions (future capabilities, training data strategy, scholar interface concepts)
   
   Propose a percentage allocation with reasoning. Consider diminishing returns — at what point does more research on topic X stop being useful?

2. RESEARCH COMPLETENESS DETECTION
   How does the system know when research on a topic is "complete" vs needs more DRs? What signals indicate:
   - Sufficient depth (the DR responses are no longer adding new information)
   - Sufficient breadth (all angles have been explored)
   - Actionability (the findings are specific enough to implement from)
   
   Propose a framework for marking research topics as SATURATED vs ACTIVE.

3. BATCH OPTIMIZATION
   Should the system generate DR prompts in daily batches (10-20 at breakfast) or maintain a continuously refreshed queue? How should priority change as the 83-day period progresses? (Early: more exploration. Late: more gap-filling?)

4. RESEARCH DEPENDENCY MAPPING
   Some research depends on other research (e.g., taxonomy tree design depends on excerpting granularity decisions). How should the system model these dependencies to ensure prompts are generated in the right order?

Please provide a concrete framework I can implement, not abstract principles.
```

---

## DR-DESIGN-03: Gemini DR — Islamic Scholarly Workflow Mapping

**Target:** Gemini Deep Research
**Priority:** HIGH
**Unblocks:** DQ-003 (DR mapping to 18 sciences), DQ-008 (dangerous excerpting edge cases)
**Estimated time:** 30-60 minutes
**File bundle needed:** Owner must upload these files to the Gemini DR session:
- `docs/autonomous-system/DESIGN.md`
- `engines/excerpting/SPEC.md` (sections §4, §6)
- `.claude/rules/arabic-scholarly-conventions.md`
- `AGENTS.md` (Arabic Text Rules + Scholarly Convention Rules sections)

### Prompt (DRAFT — to be optimized by /prompt-architect)

```
CONTEXT: I'm building KR (Khizanat Rayan) — an intelligent personal Islamic scholarly library. The pipeline processes Arabic scholarly texts and extracts structured scholarly knowledge. I'm designing an autonomous system that will generate 830-1660 Deep Research prompts over 83 days (10-20 per day).

[Attached files provide the system design, excerpting SPEC, and Arabic scholarly convention rules.]

QUESTIONS (please investigate each with scholarly depth):

1. MAPPING DR RESEARCH TO THE 18 ISLAMIC SCIENCES
   The pipeline must handle texts from all major Islamic sciences. For EACH science, what are the specific research questions that Deep Research should answer before the summer build?
   
   Specifically, for each of these sciences, identify:
   a) Unique text structures that the pipeline must handle (e.g., isnad chains in hadith, verse-commentary interleaving in tafsir, legal case structures in fiqh)
   b) Classification challenges (how to distinguish sub-genres within the science)
   c) Excerpting boundary challenges (where should excerpts begin/end for scholarly coherence?)
   d) Cross-reference patterns (how do texts in this science reference other sciences?)
   e) The 2-3 most important DR questions for this science
   
   Sciences to cover: Tafsir, Hadith, Fiqh, Usul al-Fiqh, Aqidah, Tasawwuf, Sirah, Tarikh, Lugha (Arabic language), Nahw (grammar), Sarf (morphology), Balagha (rhetoric), Mantiq (logic), Falsafa, Ilm al-Kalam, Tabaqat (biographical dictionaries), Mustalahat (hadith terminology), Ilm al-Rijal (narrator criticism)

2. DANGEROUS EXCERPTING EDGE CASES FOR SCHOLARLY INTEGRITY
   Based on your knowledge of Islamic scholarly texts, what are the most dangerous edge cases where automated excerpting could corrupt scholarly meaning? I'm looking for cases where:
   - A boundary placed in the wrong position changes the legal ruling
   - An excerpt taken out of context reverses the author's intended meaning
   - A classification error attributes a view to the wrong scholar or school
   - A structural misread conflates the author's commentary with quoted source material
   
   For each edge case, provide:
   - A real example from Islamic scholarly literature
   - Why it's dangerous (what knowledge corruption it causes)
   - How the pipeline should detect and handle it

3. SCHOLARLY COMPLETENESS
   When the pipeline excerpts a section of an Islamic scholarly text, how does a traditional Islamic scholar determine if the excerpt is "complete" (self-contained for study)? What are the traditional criteria for:
   - A complete legal discussion (mas'ala)
   - A complete hadith commentary unit
   - A complete tafsir passage
   - A complete biographical entry
   
   These criteria should inform the excerpting engine's boundary detection.

Please provide specific examples with real Arabic text where relevant. Scholarly precision matters more than breadth.
```

---

## File Bundle for Gemini DR (DR-DESIGN-03)

Owner action: Create a zip or folder with these files to upload to Gemini DR:
1. `docs/autonomous-system/DESIGN.md`
2. `engines/excerpting/SPEC.md`
3. `.claude/rules/arabic-scholarly-conventions.md`
4. `AGENTS.md`
