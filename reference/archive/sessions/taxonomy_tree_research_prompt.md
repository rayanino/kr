# New Chat Prompt — Taxonomy Tree Validation Research

Paste everything below the line into a fresh Claude Chat session.

---

This is a KR (خزانة ريان) session focused on taxonomy tree validation research. You are continuing work from a previous session that was getting long.

## Immediate orientation

After cloning the repo, read these files in this order:
1. `engines/taxonomy/STATE.md` — **READ THIS FIRST.** Full state of the taxonomy engine, including what was already researched and what remains.
2. `reference/ENGINE_FACTORY_PLAN.md` lines 836-912 — Gate G3 definition (tree validation requirement)
3. `library/sciences/taxonomy_registry.yaml` — current tree registry
4. `library/sciences/nahw/tree.yaml` lines 1-50 — sample of current nahw tree structure

## What the previous session accomplished

The previous session did two things:

### 1. Code review (COMPLETE — verdict: BLOCKED)
Session 1 taxonomy build was reviewed by 4 providers (architect, CC, ChatGPT Pro, Codex). Found 4 bugs. Fix directive is at `NEXT.md`. **This is ready for CC — the owner will relay NEXT.md to CC in parallel.** You do NOT need to work on this.

### 2. Tree validation research (Aspects 1-4 COMPLETE, Aspects 5-8 PENDING)
The previous session discovered that Gate G3 (tree validation) was never executed — the trees are unvalidated AI-generated structures. A deep investigation established:

- **Aspect 1 (Provenance):** Trees originated in ABD codebase, no documentation, registry says "placement-safe" not "scholarly." ENGINE_FACTORY_PLAN.md explicitly says "created without owner validation."
- **Aspect 2 (Sources of authority):** Ground truth is the books' own heading structures (div_path) + canonical organizational texts per science (Alfiyyah for nahw, تلخيص المفتاح for balagha). AI generation should be secondary.
- **Aspect 3 (Corpus analysis):** Only 67 excerpts processed (25 nahw, from one chapter). Books use flat headings; tree sub-classifies into fine-grained leaves. Current tree uses encyclopedic organization, not the Alfiyyah's pedagogical sequence.
- **Aspect 4 (Evaluation criteria):** Proposed encyclopedic structure + pedagogical metadata. Hard requirements: scholarly terminology, no fabricated divisions, leaf distinctness, corpus viability. Quality metrics: placement accuracy, distribution, canonical alignment.

## What THIS session should do

Complete the tree validation research — Aspects 5-8:

**Aspect 5: Research methodology.** How should the tree investigation be structured? The owner's proposed methodology: independent research by separate Claude and ChatGPT sessions per science (unbiased, no anchoring on current trees), then compare and synthesize. But this methodology needs fleshing out — what exactly does each researcher do? What data do they analyze? How do they avoid producing plausible-sounding trees that don't reflect actual scholarly tradition? The key insight from the previous session: the books' own heading structures (div_path) are the primary ground truth, not abstract AI knowledge.

**Aspect 6: Prompt design.** What exact prompts do we give to each independent researcher? These prompts must prevent anchoring on any specific organizational framework, require reference to specific authoritative sources, and produce output in a format that enables comparison.

**Aspect 7: Synthesis process.** How do we combine findings from multiple independent researchers into one validated tree? What happens when they disagree? What role does the owner play?

**Aspect 8: Sequencing.** When does this happen relative to the engine build? How do we handle the bootstrapping problem (trees need to match the corpus, but the corpus hasn't been fully processed yet)? Should we start with nahw (most test data) and validate others later?

**Work aspect by aspect, deeply.** The owner values depth over speed. Use thinking-frameworks for each aspect. Use deep-research where external evidence is needed. Use critical-review on your own output. The owner will say "continue" between aspects.

## Key constraints

- The 4-provider review team is mandatory for major decisions (reference/GOVERNANCE.md)
- Quality is the ONLY metric — no time/budget constraints
- The owner has zero technical background but is an Islamic studies student
- The owner has 2,519 Shamela .htm books locally (not in repo)
- Session 2 (LLM placement) is BLOCKED until both the code fixes AND tree validation are complete
