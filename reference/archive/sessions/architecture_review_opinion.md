# Previous Architect's Analysis — Pipeline Architecture Review

This is the analysis from a prior Claude Chat session (the KR Architect who built both completed engines). Share this AFTER forming your own independent view.

---

## The Core Problem

The current remaining pipeline (passaging → atomization → excerpting → taxonomy → synthesis) artificially decomposes a single intellectual task into three mechanical stages followed by two knowledge operations.

Consider a فصل in a fiqh book about the conditions of prayer, running 15 pages. The normalization engine has already given us those 15 pages as structured content units with a division tree, layer detection, boundary continuity, and content flags. What needs to happen next?

In the current design:
1. **Passaging** chops those 15 pages into ~8 passages of 200-800 words — a boundary-placement exercise optimized for a downstream LLM that can only see 800 words at a time.
2. **Atomization** takes each passage and classifies every sentence: "this is a definition," "this is evidence," "this is a position statement."
3. **Excerpting** looks at those classified atoms and says "atoms 3-7 form a self-contained teaching unit about the first condition of prayer."

This decomposition fights the text's natural structure. A human scholar reading that فصل doesn't first split it into chunks, then classify each sentence, then reassemble. They read the section and identify the scholarly positions directly. Modern LLMs can do exactly that — Claude Opus 4.6 with 1M context can process those entire 15 pages in a single call and identify the self-contained scholarly units, their authors, their evidence, and their topics all at once.

**The 200-800 word passaging target was designed for a world where LLM context windows were small.** With 1M tokens, we can fit an entire book section — sometimes an entire book — in a single call.

The atomization engine is solving a problem that doesn't need to exist. It's doing fine-grained sentence classification that the excerpting engine then has to reassemble. The knowledge extraction research literature confirms this trend — the field has moved from pipelined specialized classifiers toward end-to-end LLM extraction because pipelines suffer from error propagation and context loss at each boundary.

## Proposed Architecture: 4 Engines Total (2 Remaining)

**Engine 1: Source** ✅ COMPLETE
**Engine 2: Normalization** ✅ COMPLETE
**Engine 3: Excerpting Engine** (NEW — replaces passaging + atomization + excerpting)
**Engine 4: Knowledge Assembly Engine** (NEW — replaces taxonomy + synthesis)

### Engine 3: Excerpting

Does ONE thing: given a normalized book, produce accurate, self-contained scholarly excerpts with full metadata.

How it works:
- Reads the division tree from normalization output
- For each division leaf (or group of related leaves), assembles the cross-page text — the deterministic preprocessing that passaging was supposed to do, but as a module within the engine, not a separate engine
- Sends the assembled section text to the LLM: "identify every self-contained scholarly teaching unit in this text, with author attribution, school, evidence references, topic classification, and self-containment assessment"
- Uses multi-model consensus (same infrastructure from the source engine)
- Outputs excerpt records with all metadata

What this eliminates:
- The entire passaging engine (SPEC, contracts, implementation, evaluation)
- The entire atomization engine (SPEC, contracts, implementation, evaluation)
- Two contract boundaries where data could be corrupted
- The artificial chunking that breaks the text's natural structure

What this preserves:
- Cross-page text assembly (footnote renumbering, boundary-aware joining)
- Multi-model consensus, confidence scoring, human gates, T-1 through T-7 mitigations
- Self-containment verification
- All excerpt metadata that downstream needs

### Engine 4: Knowledge Assembly

Takes all excerpts and produces the final knowledge products:
- Taxonomy management — building/evolving science trees, placing excerpts at leaves
- Entry synthesis — generating encyclopedic entries from placed excerpts
- Lifecycle — staleness detection, regeneration, correction propagation

Merged because taxonomy and synthesis share a conceptual loop: place excerpt → synthesize entry → entry reveals misplacement → relocate → re-synthesize.

## Steelman: The Case FOR 7 Engines

**"Each engine can be tested independently."** True, but each boundary is also a corruption point. The source→normalization boundary had 5 contract defects. Multiply by 5 more boundaries and corruption probability rises.

**"Atomization classifications have independent value."** An argument for producing atom-level data, not for a separate engine. The excerpting engine can output atom classifications as secondary output.

**"Smaller units are easier to verify."** But we verify excerpts, not atoms. Excerpt verification is the same regardless of extraction method.

**"Error recovery granularity."** If atomization misclassifies one sentence, you re-run excerpting for that passage. If direct extraction makes one bad excerpt, you re-run the section. Recovery granularity is section-level either way.

## Cost of the 7-Engine Approach

Per the ENGINE_BUILD_BLUEPRINT, each engine requires: SPEC design (2-4 sessions), build (3-6 sessions), code audit (1 session), evaluation (4-8 sessions), hardening (2-4 sessions). That's 12-23 sessions per engine, times 5 remaining engines = 60-115 sessions.

The 2-engine approach: 2 × 12-23 = 24-46 sessions. Savings: 36-69 sessions.

## Confidence Levels

**High confidence:** Atomization is unnecessary as a separate engine. Passaging's 200-800 word chunking optimizes for a constraint that no longer exists.

**Moderate confidence:** Merging taxonomy and synthesis. There's a case for keeping them separate — taxonomy is partially deterministic while synthesis is fully LLM-powered. I lean toward merging because their lifecycle operations are tightly coupled.

**Genuine uncertainty:** Whether excerpting should process one division leaf at a time or larger sections. This is a SPEC design question, not an architecture question.
