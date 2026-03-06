# Creative Mandate — ميثاق الإبداع

> **NOTE:** This document contains the detailed reference material. The session workflow is now driven by `SESSION_TYPES.md` and self-contained `NEXT.md` playbooks. Read this file only if NEXT.md explicitly tells you to.


Claude is the creative intelligence behind KR, not its secretary. This protocol ensures every session produces ORIGINAL THINKING before it produces corrections.

The failure mode to avoid: a session that reads a SPEC, nods approvingly, fixes some grammar, adds a few examples, and calls it refined. That's a secretary. The architect looks at a SPEC and asks: "What should this engine do that nobody has thought of? What would make a scholar weep with joy?"

---

## The Invention-First Rule

**Before any review, correction, or refinement: spend the first portion of every SPEC session on CREATIVE EXPLORATION.** This is not optional. This is not a nice-to-have step. This is the reason the application exists.

### Creative Exploration Protocol

For each engine being refined, before touching the SPEC text:

**1. The Scholar's Dream Question**
Close your eyes (metaphorically). You are the most knowledgeable Islamic scholar in history. You have every book ever written. What question do you wish you could answer but can't — because no tool exists to help you find the answer across thousands of books?

Write down 5 such questions. For each: what capability would answer it?

**2. The Impossibility Search**
Search the web for what DOESN'T exist in Islamic studies tools:
- `"Islamic studies" "no tool" OR "not possible" OR "manually" scholarly`
- `Arabic text analysis limitations challenges`
- `digital humanities Islamic manuscript gap`

What are scholars frustrated about? What takes them weeks that technology could do in seconds?

**3. The Cross-Tradition Steal**
Other scholarly traditions have solved problems that Islamic studies hasn't:
- `Latin text analysis corpus tools digital humanities`
- `Chinese classical text digital tools NLP`
- `Hebrew text analysis Talmud digital tools`
- `Sanskrit digital humanities text analysis`

What features do these tools have that could be adapted for Arabic Islamic texts?

**4. The Data Pattern Question**
After this engine processes its input, what does it KNOW that didn't exist before? Not what data it produces — what KNOWLEDGE it has gained? 

Example: After the source engine processes 500 sources, it knows:
- Which scholars are most cited (from citation network data)
- Which topics have the most coverage and which have gaps
- Which editions are most reliable (from trustworthiness scores)
- Which time periods are over/under-represented

Each of these is a potential feature. Is the SPEC capturing them?

**5. The Composition Question**
What happens when you combine this engine's output with another engine's output? What emerges that neither engine produces alone?

Example: Taxonomy placement + synthesis = "How did the scholarly position on Topic X evolve?" Neither engine alone can answer this. But together, with the right metadata, they can construct a temporal narrative.

### Output: Invention Notes

Before proceeding to review, write down:
- At least 3 capabilities this engine SHOULD have that it currently DOESN'T
- For each: the specific technology or approach that makes it feasible
- For each: a concrete example of what the output would look like

These notes go into the SPEC's §4.B during refinement. They don't go into a separate document — they become part of the specification.

---

## The Anti-Secretary Test

After completing any SPEC refinement, ask:

1. **Did I add anything that wasn't already there?** If the SPEC is only CLEANER but not RICHER, the session was secretarial. Go back and do the Creative Exploration Protocol.

2. **Did I originate at least one capability?** Not adapted from VISION.md, not requested by the owner, not obvious from the SPEC template — something I conceived because I understood this engine's potential deeply enough.

3. **Would this engine surprise an expert?** Show the §4.B section to an imaginary world-class Islamic studies professor. Would they say "I had no idea technology could do that"? If not, think harder.

4. **Is there a feature here that makes an impossible scholarly task possible?** Not faster — POSSIBLE. Something a human scholar literally cannot do, no matter how much time they have.

---

## Creative Research Methodology

"Do 3 web searches" is not research. Research is a structured investigation.

### Phase 1: Map the Problem Space (3-5 searches)
Goal: Understand what exists and what doesn't.
- What tools exist for this engine's domain?
- What academic papers address this problem?
- What have similar projects achieved?
Deliverable: A list of existing capabilities and known gaps.

### Phase 2: Explore Possibilities (3-5 searches)
Goal: Discover what's technically feasible NOW that wasn't before.
- What can the latest LLMs do for this type of text analysis?
- What can the latest Arabic NLP tools handle?
- What techniques from other domains could apply?
Deliverable: A list of feasible-but-unimplemented capabilities.

### Phase 3: Design and Validate (2-3 searches)
Goal: Verify that the capabilities you designed are actually buildable.
- Does the named tool/library actually support this use case?
- Has anyone published results using this technique on Arabic text?
- What are the known limitations?
Deliverable: Each proposed capability has a named technology AND evidence it works.

Minimum total: 8-13 searches per engine. Not 3. This is non-negotiable.

---

## Integration with SPEC Refinement

The Creative Mandate integrates with SPEC_REFINEMENT.md as follows:

**Before Step 1 (Cold Read):** Do the Creative Exploration Protocol. Write Invention Notes.

**During Step 3 (Example Audit):** The examples should showcase TRANSFORMATIVE capabilities, not just basic processing. If the examples only show "input goes in, output comes out," they're too pedestrian.

**During Step 4 (Technology Review):** This is where you verify the inventions from the Creative Exploration. Name the specific tools. Find evidence they work.

**During Step 6 (Scholarly Value Check):** This is where you evaluate whether your inventions actually help Rayane. Not all technically cool things are scholarly valuable.

**During Step 8 (Research Round 2):** This is a SECOND creative pass. After fixing defects and deepening your understanding, what NEW capabilities can you see?
