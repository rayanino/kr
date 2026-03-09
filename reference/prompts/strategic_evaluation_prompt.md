# Prompt for Next Chat — Strategic Readiness Discussion

Copy everything below the line into a new chat in this project.

---

Before responding, read these files from the repo:

1. `skills/shared/ENGINE_PROTOCOL.md` — the development process we need to evaluate
2. `OPEN_PROBLEMS.md` — current status and roadmap
3. `KNOWLEDGE_INTEGRITY.md` — the 7 corruption threats
4. `engines/source/CLAUDE.md` — the first engine (concrete example of current state)

Then skim these for context (don't deep-read):
- `reference/TESTING_FRAMEWORK.md` §1-§3 and §8
- `engines/source/SPEC.md` §1-§4 (first 200 lines — enough to see the SPEC style)
- `engines/source/contracts.py` (first 100 lines — enough to see the contract style)

Read anything else in the repo you think is relevant. Use your judgment.

<context>
The repo just went through a deep audit. ENGINE_PROTOCOL.md had 10 HIGH-severity defects fixed against the project's own integrity lenses. 20+ stale files were archived. All 7 engine CLAUDE.md files were rewritten. Cross-references were verified clean. No engine code runs — all src/ is pre-protocol stubs.

SPEC quality varies sharply: excerpting and taxonomy have 0 HIGH defects, source has 3, but passaging has 25 (worst in the repo despite multiple refinement passes). All 6 contract boundaries show field mismatches per verify_metadata_flow.py.

The plan says: tracer bullet first (reconcile contracts, stub everything, run one fixture end-to-end), then build engines sequentially through a 4-step cycle.
</context>

<what_I_want>
A genuine discussion about whether ENGINE_PROTOCOL.md is strategically ready to execute, or whether there are problems that need fixing before we start.

I'm NOT looking for a report or a structured verdict. I want to think through this together. Push back on the plan where you see problems. Ask me questions where my input matters. Tell me if you think something looks wrong that I haven't considered.

Some concerns from the last session that may or may not be real problems (investigate them if they seem important, ignore them if they don't):

- The tracer bullet reconciles full contracts before Step 1 strips them to core-only. Wrong sequence?
- The project has spent 3+ planning sessions and zero building sessions. Is the new protocol just a more sophisticated version of the same over-planning trap?
- Passaging has the most defects despite the most refinement. Why? Structural problem?
- Shared components get designed around the source engine's needs. Will that break for later engines?
- Owner availability is unpredictable. Does strict sequential ordering create an unnecessary bottleneck?
- What am I not seeing?

But these are starting points, not the agenda. If you find bigger issues, lead with those.
</what_I_want>
