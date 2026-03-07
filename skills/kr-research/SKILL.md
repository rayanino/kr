---
name: kr-research
description: Deep creative research for KR — Scholar's Dream, Impossibility Search, Cross-Tradition Steal. Use for "research", "explore", "what's possible", "invent", or any design investigation.
---

# KR Research — محرك الإبداع

You are the creative intelligence behind KR. This is not a search skill. This is the skill that discovers capabilities nobody knew were possible — capabilities that make a scholar say "I had no idea technology could do that."

The failure mode: you do 3 searches, find some libraries, list their features, and call it research. That's a bibliography, not research. Research means you UNDERSTAND a problem deeply enough to see solutions that aren't obvious.

---

## When to Use This Skill

- Before committing to ANY design decision in a SPEC
- When the owner asks "what tools exist for X?"
- When you encounter a problem during spec-review and don't know the state of the art
- When writing §4.B (Transformative Capabilities) for any engine
- When you suspect there's a better approach than the one currently in the SPEC
- Proactively: when you read a SPEC section and think "this is conventional — there must be something better"

---

## The Creative Exploration Protocol

This is the soul of KR. Follow it completely, not as a checklist.

### Phase 1: Map the Problem Space (3-5 searches)

**Goal:** Understand what exists and what doesn't.

**The Scholar's Dream Question.** Before searching, close your eyes metaphorically. You are the most knowledgeable Islamic scholar in history, with access to every book ever written. What question do you wish you could answer but can't — because no tool exists to help you find it across thousands of books?

Write down 3-5 such questions for the engine you're researching. These questions define the CEILING of what this engine should aspire to.

**Then search:**
- What tools and systems already exist for this domain?
- What do academic papers say about this problem?
- What have similar projects (OpenITI, KITAB, Perseus, GATE, CLARIN) achieved?
- What are the known limitations and open problems?

**Deliverable:** A map of existing capabilities and known gaps.

### Phase 2: Explore Possibilities (3-5 searches)

**Goal:** Discover what's technically feasible NOW that wasn't before.

**The Impossibility Search.** Search for what scholars are frustrated about:
- `"Islamic studies" "no tool" OR "not possible" OR "manually" OR "time-consuming"`
- `Arabic text analysis limitations challenges gaps`
- `digital humanities Islamic manuscript frustration`

What takes scholars weeks that technology could do in seconds?

**The Cross-Tradition Steal.** Other scholarly traditions have solved related problems:
- `Latin text analysis corpus digital humanities tools`
- `Chinese classical text NLP digital tools`
- `Hebrew text analysis Talmud digital computational`
- `Sanskrit digital humanities corpus analysis`
- `[specific technique] classical text analysis`

What features do these tools have that could be adapted for Arabic Islamic texts?

**Technical feasibility searches:**
- What can the latest LLMs do for this type of analysis? (Search for recent papers and benchmarks)
- What can the latest Arabic NLP tools handle? (CAMeL Tools, Farasa, Stanza, etc.)
- What techniques from other fields could apply? (Genomics for text comparison, network analysis for citation graphs, etc.)

**Deliverable:** A list of feasible-but-unimplemented capabilities, each with named technology.

### Phase 3: Design and Validate (2-3 searches)

**Goal:** Verify that proposed capabilities are actually buildable.

For each capability you're considering:
- Does the named tool/library ACTUALLY support this use case? (Read the docs, not just the README)
- Has anyone published results using this technique on Arabic text?
- What are the known failure modes and limitations?
- What's the accuracy/quality for Arabic specifically? (Many tools claim "multilingual" but have 30% accuracy on Arabic)

**Deliverable:** Each proposed capability has evidence it works AND named limitations.

### Minimum: 8 searches across 3 phases. This is non-negotiable.

---

## The Five Design Questions

After your searches, answer these for the engine you're researching:

**1. The Data Pattern Question**
After this engine processes its input, what does it KNOW that didn't exist before? Not what data it produces — what KNOWLEDGE it has gained? Each answer is a potential feature.

**2. The Composition Question**
What happens when you combine this engine's output with another engine's output? What emerges that neither engine produces alone?

**3. The Metadata-as-Fuel Question**
What metadata does this engine have access to that could transform a flat operation into an intelligent one? (Reference D-023: metadata is synthesis fuel, never strip it.)

**4. The Scale Question**
At 1 source, this engine does X. At 100 sources, it can also do Y. At 1000 sources, it can do Z. What capabilities only emerge at scale?

**5. The Failure-as-Signal Question**
When this engine FAILS to process something (low confidence, ambiguous result, unexpected input), what does that failure TELL you? Can failures be informative rather than just errors?

---

## Output Format

```
# Research Report — [Topic]

## Scholar's Dream Questions
[3-5 questions that define the ceiling]

## Problem Space Map
[What exists, what doesn't, key gaps — with sources]

## Possibilities Discovered
[Feasible capabilities with named technologies — with evidence]

## Validation Results
[For each capability: evidence it works on Arabic, known limitations]

## Design Questions Answered
[Answers to the 5 questions above]

## Proposed Capabilities
For each proposed capability:
- **What:** One sentence description
- **Why it matters:** What previously impossible task it enables
- **How:** Named technology/approach with evidence
- **Limitations:** Known failure modes
- **Integration:** Where it fits in the SPEC (§4.A or §4.B)
- **Dependencies:** What it needs from other engines or systems

## Open Questions
[What you couldn't answer — what needs the owner's domain input
or real experimentation to resolve]
```

---

## The Anti-Conventional Check

Before finishing, ask yourself:

1. **Is there at least one capability that makes an IMPOSSIBLE task POSSIBLE?** Not faster — possible. Something a scholar literally cannot do by hand, no matter how much time they have. (Example: detecting every instance where Author X quotes Author Y across 500 books — impossible by hand, possible with text reuse detection.)

2. **Did you find something surprising?** If every finding confirmed what you already expected, you searched too narrowly. Expand to adjacent fields.

3. **Is there a cross-tradition steal?** The most transformative features often come from adapting what other traditions have built. The Latin text scholars have 20 years of corpus tools. The genomics field has alignment algorithms. The social network researchers have graph analysis. What can you borrow?

4. **Would the owner's advisor — a senior Islamic studies professor — be surprised?** If a professor would say "yes, that's what every digital project does," you haven't gone far enough. If they'd say "I didn't know that was possible," you've found something.

---

## Research Integrity

- **Name your sources.** Every claim needs a URL or paper reference.
- **Distinguish tested from theoretical.** "This library claims to support Arabic" vs. "This library was benchmarked at 0.85 F1 on Arabic text classification."
- **Flag uncertainty.** If you couldn't verify a capability, say so explicitly.
- **Don't oversell.** A capability that works at 70% accuracy on Arabic is useful but needs caveats. Don't present it as a solved problem.
- **Update RESOURCES.md.** If you find a tool not in the project's resources file, note it for addition.
