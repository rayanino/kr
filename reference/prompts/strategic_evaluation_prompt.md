# Prompt for Next Chat — Strategic Readiness Evaluation

Copy everything below the line into a new chat in this project.

---

Clone the repo using the Github_key file, then read these files in this exact order before responding:

1. `STEERING.md` — what this project is (short, read first)
2. `skills/shared/ENGINE_PROTOCOL.md` (331 lines) — the development process you are evaluating
3. `OPEN_PROBLEMS.md` — current status and roadmap
4. `KNOWLEDGE_INTEGRITY.md` — the 7 threats the process must prevent
5. `SILENT_FAILURES.md` — the 7 failure patterns the process must avoid
6. `reference/TESTING_FRAMEWORK.md` — test architecture (skim §1-§3 and §8, skip per-engine details)
7. `engines/source/CLAUDE.md` — the first engine to be built (read as a concrete example of state)

Do NOT read: VISION.md, SESSION_LOG.md, any SPEC.md, any contracts.py, reference/archive/. These are not relevant to this evaluation.

<context>
خزانة ريان (KR) is a personal Islamic scholarly library with a 7-engine pipeline. No engine code runs yet — all src/ files are pre-protocol stubs. All 7 engines have SPECs (918-2006 lines) and Pydantic contracts (491-825 lines). The repo just went through a thorough audit: 20+ stale files archived, all cross-references verified, ENGINE_PROTOCOL.md had 10 HIGH-severity defects fixed using the project's own integrity lenses, all 7 engine CLAUDE.md files rewritten, gold baseline timing corrected, failure states added.

SPEC defect counts (HIGH severity by check_spec_quality.py): excerpting 0, taxonomy 0, source 3, normalization 6, atomization 9, passaging 25, synthesis 6. These will be addressed during each engine's Step 1.

The current plan says: run a tracer bullet (Step 0) to validate all contract boundaries, then build engines one at a time through a 4-step cycle (SPEC → RESEARCH → BUILD → TEST).

The owner is an Islamic studies student with no technical background. He provides domain knowledge only. All technical and architectural decisions come from Claude.
</context>

<task>
Evaluate whether ENGINE_PROTOCOL.md is strategically sound and ready to execute. This is not a formatting review or a defect hunt — those were done last session. This is a strategic assessment: will this plan actually produce a working, reliable pipeline?

Investigate these specific concerns:

1. **Tracer bullet risk.** The protocol says the tracer bullet reconciles 7 contracts.py files that currently have mismatches at all 6 boundaries. But these contracts were written against full SPECs (including deferred features), and Step 1 will strip them to core-only. Is reconciling ALL fields before core extraction the right sequence? Or should core extraction happen first so the tracer bullet only reconciles what matters?

2. **SPEC depth vs. build speed.** The protocol went through 3 planning sessions and a meta-audit before any code runs. The earlier HONEST_PLAN.md (now archived) diagnosed the project as over-specifying and under-building. Has the new protocol actually solved this, or has it just created a more sophisticated version of the same trap? What's the minimum viable Step 1 that gets to running code fastest without compromising quality?

3. **The passaging problem.** Passaging has 25 HIGH-severity SPEC defects — the worst in the repo — despite multiple refinement passes. The protocol now correctly notes this, but doesn't address a deeper question: why did multiple passes leave it in worse shape than engines with fewer passes? Is there a structural problem with the passaging SPEC that more refinement won't fix?

4. **Shared component bootstrap.** The source engine must build minimum viable versions of 4 shared components (consensus, human_gate, scholar_authority, validation). ENGINE_PROTOCOL now lists specific method signatures. But building these during one engine's Step 3 means the shared component design is driven by one consumer's needs. Will this create problems when engine 2 (normalization) needs different behavior from the same components?

5. **The owner bottleneck.** The protocol requires owner domain review for source and synthesis engines (heavy), normalization (moderate), and has a 3-day timeout for light-review engines. But the owner is a student — his availability is unpredictable. If the source engine's Step 1 blocks for 2 weeks waiting on domain comments, and the protocol has no parallelism, the entire pipeline stalls. Is strict sequential ordering actually necessary for Step 1 across engines?

6. **What's missing.** What risks or gaps does the protocol not address that could cause failure? Think about: what happens when the first real Arabic text hits the pipeline and something unexpected occurs? What assumptions is the protocol making that haven't been questioned?

For each concern: state what you find, whether it's a real problem or an acceptable tradeoff, and if it's a problem, propose a concrete fix. If the protocol is ready to execute as-is, say so and explain why the concerns are manageable. If it needs changes before starting, say that directly — do not soften the assessment.
</task>

<output_format>
Structure your response as:
1. One-paragraph overall verdict (ready / ready with caveats / not ready)
2. Per-concern analysis (findings → judgment → fix if needed)
3. If changes are needed: produce the specific edits, not just recommendations
</output_format>
