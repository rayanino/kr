# Engine Protocol — المسار لكل محرك

This is YOUR guide. Follow it top to bottom for each engine. Don't skip steps. Don't mix steps.

---

## The Principle

**Depth over breadth. Reliability over features. Every block proven before building on it.**

Each engine has a core — the fundamental thing it does, the reason it exists. A source engine ingests and registers sources. A normalization engine transforms raw formats into a single clean structure. A passaging engine divides text into coherent units. That core must be specified in exhaustive detail, tested against reality, built, and made bulletproof — before anything else.

Features that extend the core (more input formats, advanced detection, clever optimizations) come later. They build ON the core. If the core is unreliable, features built on it are unreliable. If the core is solid, features are straightforward additions.

---

## Two Stages

### Stage 1: Core Pipeline (v0.0.1)

Build all 7 engines, one at a time in pipeline order, each focused only on its core architecture. The goal: a narrow but reliable pipeline where data flows from source intake to knowledge entry. Every engine does its fundamental job well on a small number of supported inputs.

### Stage 2: Expansion

Go back engine by engine and add capabilities. More input formats, advanced features, §4.B transformative capabilities. Each addition is a scoped project built on a proven foundation, informed by real evidence from Stage 1.

**This document governs Stage 1.** Stage 2 gets its own protocol when Stage 1 is complete.

---

## Stage 1: Per-Engine Process

Each engine goes through 4 steps. You are always in exactly ONE step.

### Step 1: SPEC — Core Architecture

**Goal:** Produce a SPEC that describes the core engine in such exhaustive detail that Claude Code's only job is translating it into code. No ambiguity. No gaps. Every data structure, every decision point, every error path, every LLM call — specified precisely.

**What "core" means:**

The core is the engine's identity — what makes it THIS engine and not something else. It is the minimum set of behaviors that, if any were removed, the engine would no longer fulfill its purpose in the pipeline.

For the source engine: format detection, metadata extraction, metadata inference (LLM), freezing, deduplication, registration, trust evaluation. On TWO formats: Shamela HTML and plain text. That's the core.

NOT core: audio transcription, OCR from phone photos, citation network discovery, tahqiq apparatus fingerprinting, source difficulty prediction. These are extensions that build on a working core.

**What happens in this step:**

1. **Identify core vs. deferred.** Read the current SPEC. Draw the line: what is the engine's fundamental job? What is an extension? Everything deferred gets a single line: "Deferred to Stage 2 expansion." The SPEC's depth budget goes entirely toward the core.

2. **Owner domain review.** You read the core sections of the SPEC. Write comments about anything that's wrong, confusing, or missing from the core behavior. Focus on: "Is this how the domain actually works?" and "Would this produce correct results for my real sources?"

3. **Claude investigates your comments.** Research-heavy. Claude uses web search, Exa, Scholar Gateway, Tavily — whatever tools help find the best approach. For every core design decision, Claude researches how similar systems handle it, what the tradeoffs are, what the state of the art is. This is not a quick review — it's deep architectural research grounded in your domain feedback.

4. **Write the core SPEC to implementation depth.** The final SPEC should read almost like pseudocode for the entire engine. Every data structure: exact field names, types, constraints, and why. Every LLM call: what goes in, what prompt, what structured output, what model, what fallback. Every error: code, severity, recovery. Every decision point: exact threshold, exact logic. A developer reading this SPEC should have zero questions.

**Skills used:** `kr-core-extract` for the classification and rewrite. `kr-spec-review` for comment resolution. `kr-research` when deep research is needed. `kr-integrity` as the final quality gate — audits the SPEC for technical defects that domain review can't catch (ambiguous rules, missing error paths, knowledge corruption risks, untested assumptions).

**Rules:**
- Do comments in batches of 3-5 per chat. Fresh chat when things get long.
- Claude may disagree with your comments. Listen on technical matters. Push back on domain matters — you're the authority.
- If a design question can't be resolved by discussion alone, it becomes a research question for Step 2.

**You're done when:** The core SPEC has passed kr-integrity's technical audit with all HIGH-severity defects fixed. Every sentence in §4.A is either a binding rule with enough detail for implementation, or a marked assumption that Step 2 will answer through testing. All §4.B content and non-core features are explicitly deferred.

---

### Step 2: RESEARCH — Validate Assumptions

**Goal:** Every assumption the core SPEC rests on gets tested BEFORE building. If an assumption fails, the SPEC changes. The SPEC drives the build, so the SPEC must be grounded in evidence.

**What gets tested:**

Any part of the SPEC where the design depends on something unproven. Common categories:

- **LLM reliability.** The SPEC says "use an LLM to identify the author." Can it? Run the actual call on your actual fixtures. Measure accuracy. If it's unreliable, the SPEC changes — maybe to a different prompt, a two-stage approach, a lookup table, or a human gate.

- **Data structure fitness.** The SPEC defines output schemas. Do they carry enough information for the next engine? Mock up realistic data in the schema format and manually verify the downstream engine could work with it.

- **Tool capabilities.** The SPEC says "use X library for Y." Does it actually handle Arabic text correctly? Does it handle your specific formats? Run it on your fixtures.

- **Architectural questions.** Should this be one LLM call or two? Should consensus require 2 models or 3? What confidence threshold separates "accept" from "human review"? These are empirical questions with testable answers.

**How it works:**

Claude designs and runs targeted experiments. Not building the engine — running isolated tests of specific assumptions. Each experiment:
1. States the assumption being tested
2. Describes the test (input, method, expected output)
3. Shows the actual results
4. Recommends a SPEC change if the assumption failed

Results are documented in the engine directory as `engines/{engine}/research/`. Every finding feeds back into the SPEC. The SPEC is updated before moving to Step 3.

**Tools:** This is where you use everything — Exa for finding similar architectures, Scholar Gateway for academic approaches, Tavily for comprehensive research, web search for tool comparisons, actual API calls to test LLM reliability. Assume infinite budget.

**You're done when:** Every marked assumption in the SPEC has been tested. The SPEC has been updated with findings. There are no open questions that would change the architecture.

---

### Step 3: BUILD

**Goal:** Turn the SPEC into a working, testable engine.

**What happens:**

1. **Build prep** (first session). Set up the Claude Code environment: CLAUDE.md, architecture doc, testing infrastructure, session plan. This is one session of build prep, not a separate phase.

2. **Incremental build.** Each session adds one capability with its tests. 5a deterministic tests run continuously. 5b LLM-worker tests run as each LLM-dependent feature is added. No session ends with untested code.

3. **Core formats only.** The engine supports exactly the formats specified in the core SPEC. No scope creep.

**You're done when:** The engine runs on all specified input formats, all 5a tests pass, 5b tests show ≥90% accuracy.

---

### Step 4: TEST — Prove Reliability

**Goal:** Subject the engine to ruthless testing until it is bulletproof. Find core gaps — not nice-to-haves, but things that would corrupt the pipeline if left unfixed.

**What happens:**

1. **Full 5a/5b/5c evaluation** across all test fixtures appropriate for the core formats.

2. **You review output.** Not "does this look OK?" but specific questions: "Is this author identification correct?" "Is this science classification right?" "Does this metadata capture everything a downstream engine needs?"

3. **Every finding is categorized:**
   - **Core gap:** Something fundamental is wrong or missing. Metadata that downstream engines need but isn't captured. A failure mode that corrupts data. An unreliable LLM task. **These get fixed before moving on.**
   - **Extension opportunity:** Something that would improve the engine but isn't required for the pipeline to work. Audio support, better OCR, advanced features. **These get documented for Stage 2.**
   - **Lesson learned:** An insight about LLM reliability, data structure design, testing approaches, or anything else. **These feed forward to the next engine.**

4. **Fix core gaps → re-test → repeat** until no core gaps remain.

5. **Document everything.** Findings, lessons, extension opportunities. This documentation is as valuable as the code — it's the knowledge that informs every subsequent engine and all of Stage 2.

**You're done when:**
- All 5a deterministic checks pass
- 5b LLM-worker accuracy ≥90%
- 5c independent review finds no errors that self-validation missed
- You have reviewed and approved the output on your real sources
- All core gaps are fixed
- Lessons and extension opportunities are documented

Then you start Step 1 for the NEXT engine in the pipeline.

---

## Engine Order

Pipeline order. Each engine's core must be reliable before starting the next.

```
1. Source engine       (محرك المصادر)     ← start here
2. Normalization engine (محرك التسوية)
3. Passaging engine    (محرك التقطيع)
4. Atomization engine  (محرك التذرية)
5. Excerpting engine   (محرك الاستخراج)
6. Taxonomy engine     (محرك التصنيف)
7. Synthesis engine    (محرك التركيب)
```

After engine 7's core is proven: **Stage 1 is complete.** You have v0.0.1 — a narrow, reliable pipeline. Data flows from a Shamela HTML file to a knowledge entry. Every engine does its fundamental job. Every block is proven.

---

## What Gets Documented Per Engine

At the end of each engine's Step 4, produce:

```
engines/{engine}/LESSONS.md
```

Contents:
- What LLM tasks worked reliably, and what didn't
- What data structures worked, and what needed changing
- What testing approaches were effective
- Architectural decisions that affected downstream engines
- Extension opportunities identified (for Stage 2)
- Anything the next engine should know

These lessons accumulate. By engine 7, you have a comprehensive understanding of the pipeline's strengths and weaknesses — real evidence, not theory.

---

## Rules

1. **One engine at a time.** Don't start normalization until source is proven.
2. **Core only in Stage 1.** Every feature request gets asked: "Is this core, or is this an extension?" If extension, it goes in LESSONS.md for Stage 2.
3. **Test assumptions before building.** If the SPEC says "use an LLM for X," test whether an LLM can actually do X reliably. Before writing engine code.
4. **Fresh chats when context gets long.** 30+ turns or sluggish responses = time for a handoff.
5. **Always invoke skills by name.** "Use kr-spec-review" not "handle my comment."
6. **Document everything.** Lessons are as valuable as code.
7. **Quality over speed.** A narrow engine that works is worth infinitely more than a wide engine that doesn't.
8. **If Step 4 reveals a core design problem, go back to Step 1.** Write a new comment, resolve it, update the SPEC, rebuild. Don't patch.
