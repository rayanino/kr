Pull the repo and read NEXT.md. This is the excerpting engine build preparation session (Step 3c). Run `git log --oneline -5` to see current state. Before any work, scan `ls /mnt/skills/user/` to confirm available skills, then read `reference/ENGINE_BUILD_BLUEPRINT.md` §2a (lines 206–280).

<session_context>
The excerpting SPEC is COMPLETE — 2387 lines, 12 sections. contracts.py is COMPLETE — 1111 lines, independently reviewed (3 rounds, 67+ adversarial probes), one finding fixed (F-1: OOB IndexError in validate_tu_invariants).

The engine has types and validators but ZERO implementation code. This session produces the build preparation package: technology survey, module architecture, stubs, test infrastructure, CLAUDE.md update, and the first CC build session NEXT.md.

HEAD commit: `57615a38` (independent review ACCEPT + F-1 fix). Working tree should be clean.
</session_context>

<task>
Produce the 6 deliverables listed in NEXT.md, in this order:

**1. Technology Survey (research-heavy, do first):**
Use `kr-research` — minimum 8 searches. For the 7 capabilities in the NEXT.md table, verify each tool/library actually works for Arabic scholarly text. The most important verification: does `instructor` work with OpenRouter for all 3 model providers (Anthropic via OpenRouter, OpenAI via OpenRouter, Cohere via OpenRouter)? This is the foundation of Phase 2 and Phase 3.

**2. Module Architecture:**
Use `thinking-frameworks` — analyze from multiple angles before committing to a structure. The proposed structure in NEXT.md is a starting point, not a mandate. Consider: should domain_rules.py be separate or inlined into phase2/phase3? Should phase3 be 3 files or 2? Should the pipeline orchestrator be a class or a function?

**3. Stub Files:**
Write every stub with exact type signatures from contracts.py. Every function signature must import real types — no `Any` or `dict` placeholders. Include SPEC section references in docstrings.

**4. Test Infrastructure:**
Define test categories per file. Reference the normalization engine's test patterns (conftest.py factories, fixture-based testing, adversarial cases from SPEC §10.6).

**5. CC Session 1 NEXT.md:**
Use `kr-preparing-cc-handoffs` — follow the 9-step protocol literally. Scope: Phase 1 (deterministic preprocessing). This is the most important deliverable because it directly controls what CC builds.

**6. Update CLAUDE.md:**
Keep under 200 lines. Reflect that contracts are complete, build metrics, module architecture.

After all 6 deliverables, use `critical-review` to self-verify before committing.
</task>

<what_to_read>
In this order:
1. `NEXT.md` — current task directive (153 lines)
2. `engines/excerpting/CLAUDE.md` — engine orientation (109 lines, you'll update this)
3. `engines/excerpting/SPEC.md` §4 (lines 601–764) — Phase 1 deterministic preprocessing
4. `engines/excerpting/SPEC.md` §2.3.2 (lines 143–200) — AssembledChunk fields + invariants
5. `engines/excerpting/contracts.py` — all types (1111 lines, skim for signatures)
6. `engines/normalization/contracts.py` — upstream types: NormalizedPackage, DivisionNode, ContentUnit (725 lines)
7. `reference/ENGINE_BUILD_BLUEPRINT.md` §2a (lines 206–280) — build prep requirements
8. `experiments/architecture_test/run_tests.py` — validated LLM prompts (reference only)

Do NOT read the entire 2387-line SPEC upfront. Read §4 for Phase 1, skim §5/§7 headers for module architecture, and refer to specific sections when writing stubs.
</what_to_read>

<skills>
Invoke ALL of these explicitly at session start:
- `kr-build-prep` — the primary skill for this task
- `kr-research` — for technology survey (8+ searches)
- `thinking-frameworks` — for module architecture decisions
- `critical-review` — self-verify all deliverables before committing
- `kr-preparing-cc-handoffs` — for writing the CC Session 1 NEXT.md
</skills>

<quality>
Take all your time. The build preparation is the bridge between design and implementation. Every stub type mismatch, every missing module, every under-scoped test file becomes a CC implementation bug. The technology survey prevents building custom code for something a library handles. The stubs prevent CC from improvising type signatures. The CC Session 1 NEXT.md prevents CC from building the wrong thing.

Technology survey is non-negotiable. The source engine's initial SPEC assumed sentence-transformers worked for Arabic — it didn't. Catching this before build saved a redesign. Verify every tool claim with actual documentation.
</quality>
