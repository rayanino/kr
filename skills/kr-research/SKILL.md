---
name: kr-research
description: Conducts deep architectural research for KR engine design decisions. Activate when exploring how to solve a design problem, when validating SPEC assumptions, when searching for tools and techniques, or when the owner asks "what's possible" or "how do others handle this." Researches thoroughly before proposing any approach — minimum 8 searches across multiple angles.
---

# KR Research — البحث المعمّق

You are conducting deep research to inform KR engine design. This is not a search skill — it's the skill that discovers the best approach to a problem by understanding the problem space deeply enough to see solutions that aren't obvious.

Research in KR serves two purposes. During Step 1 (SPEC), it informs design decisions with evidence from similar systems and state-of-the-art techniques. During Step 2 (RESEARCH), it validates assumptions by testing tools, LLMs, and approaches on actual fixtures before the SPEC is committed to code.

---

## When This Skill Adds Value

- Before committing to any design decision in a core SPEC
- When the owner asks "what tools exist for X?"
- When investigating a SPEC comment that raises a design question
- When you suspect there's a better approach than the one currently in the SPEC
- When validating whether an LLM can reliably perform a task the SPEC depends on
- When comparing tools or libraries for Arabic text processing

---

## Research Protocol

### Phase 1: Map the Problem Space (3-5 searches)

Understand what exists and what doesn't.

Search for: what tools and systems already exist for this domain? What have similar projects (OpenITI, KITAB, Perseus, GATE, CLARIN, Shamela, HathiTrust Arabic) achieved? What are known limitations? What do academic papers say?

Use all available research tools — Exa for finding similar architectures, Scholar Gateway for academic literature, Tavily for comprehensive web research, standard web search for tool documentation and benchmarks. Different tools surface different results; use them in combination.

Deliverable: a map of existing capabilities and known gaps, with sources.

### Phase 2: Explore Possibilities (3-5 searches)

Discover what's technically feasible.

The cross-tradition approach: other scholarly traditions have solved related problems. Latin corpus tools (Perseus, CLARIN), Chinese classical text NLP, Hebrew Talmud analysis, Sanskrit digital humanities — what features do these have that could be adapted for Arabic Islamic texts?

Technical feasibility: what can current LLMs do for this type of analysis? What can Arabic NLP tools handle? (CAMeL Tools, Farasa, Stanza — but verify Arabic performance with benchmarks, not just README claims.)

Deliverable: feasible approaches with named technologies.

### Phase 3: Validate (2-3 searches)

Verify that proposed approaches actually work.

For each approach: does the tool actually support this use case? (Read the docs, not just the tagline.) Has anyone published results on Arabic text? What accuracy/quality for Arabic specifically? What are failure modes?

For LLM-dependent approaches: what evidence exists that the LLM can perform this task reliably? If no evidence, flag this as an assumption that needs empirical testing in Step 2 of the engine protocol.

Deliverable: each proposed approach has evidence it works, AND named limitations.

### Minimum: 8 searches across the three phases.

---

## Output Format

```
# Research Report — [Topic]

## Problem Space
[What exists, what doesn't, key gaps — with sources]

## Approaches Found
[Feasible approaches with named technologies and evidence]

## Validation
[For each approach: evidence it works on Arabic, limitations, accuracy data]

## Recommendation
[Which approach to use and why, with explicit tradeoffs]

## Assumptions That Need Empirical Testing
[Things the research couldn't confirm — these become Step 2 experiments]

## Open Questions
[What needs the owner's domain input to resolve]
```

---

## Research Integrity

Name your sources — every claim needs a URL or paper reference. Distinguish tested from theoretical: "this library claims Arabic support" is different from "benchmarked at 0.85 F1 on Arabic NER." Flag uncertainty explicitly. If a capability works at 70% accuracy on Arabic, say so — don't present it as solved.

If you find a tool not in `reference/RESOURCES.md`, note it for addition.
