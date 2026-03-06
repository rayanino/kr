# Session Types — أنواع الجلسات

Each SPEC refinement is split into 2-3 focused sessions. Each session type has a specific goal, reads specific files, and produces specific output. This replaces the monolithic "do everything in one session" approach.

**Why split?** Claude Chat's creative output is highest when context is fresh and focused. A single session that reads 11 files and follows 10 steps produces mediocre work on all of them. Three focused sessions produce excellent work on each.

---

## Type C: CREATIVE Session (First session for each SPEC)

**Goal:** Understand what exists, evaluate its soundness, then invent transformative capabilities that build on a verified foundation.

**Context budget:** ~10% on grounding (reading + quality check), ~50% on research and creative thinking, ~30% on writing, ~10% on handoff.

**Reads:**
1. The SPEC itself — **ALL sections** (this is the foundation you're building on — you must know it)
2. `reference/ENTRY_EXAMPLE.md` (quality target)
3. `reference/USER_SCENARIOS.md` (who benefits and how)
4. `engines/<n>/contracts.py` if it exists (the machine-readable truth)

**Does NOT read:** Other SPECs, protocol documents, KNOWLEDGE_INTEGRITY.md, SILENT_FAILURES.md. Those are for the PRECISION/HARDENING sessions.

**Work (in this order):**

### Phase 0: GROUND (before any creative work)

You cannot build on a foundation you haven't inspected.

1. **Read the full SPEC.** As you read, note:
   - What does this engine ACTUALLY do today? (Not aspirationally — what do the §4.A rules specify?)
   - What feels vague, hand-wavy, or under-specified? (Don't fix it now — just note it)
   - What §4.B capabilities already exist? Are they well-specified or hollow?
   - What metadata does this engine produce (§3) that downstream engines consume?

2. **Run the quality checker:** `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md --verbose`
   Record the baseline: "X high, Y medium defects. Categories: ..."
   
3. **Run creative verification:** `python3 scripts/creative_verification.py engines/<n>/SPEC.md`
   Record: "§4.B score: X/100. Capabilities: N."

4. **Write a 5-line assessment** (for your own reference, not committed):
   - "Core processing (§4.A) is [solid/adequate/weak] because [reason]"
   - "Main quality gaps: [list top 3]"
   - "Existing §4.B capabilities: [list them, are they real or hollow?]"
   - "This engine's unique data advantage: [what does it know that nothing else does?]"
   - "Biggest opportunity: [what's missing that would be transformative?]"

This assessment FEEDS the creative work. A vague §4.A rule isn't just a defect — it's an opportunity to replace it with something transformative. A missing §4.B capability isn't just a gap — it's a design space to explore.

### Phase 1: Research the Problem Space (3-5 web searches)

NOW that you understand what the engine does and where it's weak:
- What tools exist for this engine's specific domain?
- What do scholars wish they could do but can't?
- What have digital humanities projects built for similar languages?

### Phase 2: Research the Possibilities (3-5 web searches)

- What can LLMs do NOW for Arabic text analysis that they couldn't 2 years ago?
- What techniques from Latin/Chinese/Hebrew DH could be adapted?
- What open-source tools handle part of this engine's job?
- For any VAGUE §4.A rules you noted: is there a specific tool that could make them precise?

### Phase 3: Invent Capabilities (the core creative work)

For each capability: name it, name the technology, give a concrete output example with real Arabic text, explain why a scholar would weep with joy.

Minimum: 3 new capabilities per engine. Aim for 5.

Ask yourself:
- After this engine processes 500 sources, what does it KNOW that didn't exist before?
- What question can a scholar now answer that was literally impossible before?
- What would take a human scholar 6 months that this engine does in 6 seconds?
- Which vague §4.A rules could be REPLACED by something transformative?

### Phase 4: Write §4.B

Full specification of each capability. Not vague aspirations. Inputs, outputs, triggers, algorithms, edge cases. Every capability specified precisely enough for Claude Code to implement.

### Phase 5: Update RESOURCES.md

For every tool, library, or dataset discovered during research.

**Output:** Updated SPEC (§4.B at minimum, and optionally §4.A where vague rules can be replaced with precise transformative ones), updated RESOURCES.md, quality baseline recorded.

**Anti-pattern to watch for:** Doing cosmetic corrections to §4.A without adding substance. If you touch §4.A, it should be to REPLACE something vague with something transformative — not to reword it slightly.

---

## Type P: PRECISION Session (Second session for each SPEC)

**Goal:** Make every rule machine-implementable. Claude Code should build from this with zero questions.

**Prerequisite:** CREATIVE session completed. The NEXT.md written by that session includes the assessment (quality baseline, gaps identified, capabilities added). Read it carefully — it tells you what the CREATIVE session found and what needs precision work.

**Context budget:** ~70% on the SPEC text and examples. ~20% on verification. ~10% on searching for better approaches.

**Reads ONLY:**
1. The SPEC (full — all sections)
2. `engines/<n>/contracts.py` (if it exists)
3. Downstream engine's SPEC §2 (input contract only)

**Does NOT read:** ENTRY_EXAMPLE.md, USER_SCENARIOS.md, protocol documents, RESOURCES.md.

**Work (in this order):**

1. **Run quality baseline:** `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md --verbose`
   Record: "Baseline: X high, Y medium defects"

2. **Machine-readability pass (§4.A only):**
   For each rule: Can you write a function signature? Can you write 5-15 lines of pseudocode? Can you write a test assertion?
   If NO to any → the rule needs rewriting.

3. **Example audit:** Every §4.A subsection needs ONE worked example with real Arabic text showing input → processing → output.

4. **Corruption risk assessment:** For each output field (§3):
   - If this field is wrong, does the user notice? (SILENT vs VISIBLE corruption)
   - For SILENT paths: what validation in §5 prevents it?
   - Add validation rules for any unprotected field.

5. **Contracts.py alignment:** Cross-check every field in Pydantic models against SPEC prose. Fix mismatches.

6. **Boundary verification:** Does every field this engine produces match what the downstream engine expects?

7. **Run quality check again:** `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md`
   Target: high-severity defects reduced by ≥50%.

**Output:** Refined SPEC with concrete examples, machine-readable rules, validated contracts, verified boundaries.

**Anti-pattern to watch for:** Inventing new capabilities. STOP. That was the previous session. This session is for PRECISION only.

---

## Type H: HARDENING Session (Third session, only if needed)

**Goal:** Ensure the SPEC can't produce corrupted knowledge under any circumstance.

**Trigger:** Run this session if the PRECISION session left >5 high-severity defects, or if the engine has complex failure modes (source engine, excerpting engine, synthesis engine).

**Reads ONLY:**
1. The SPEC (full)
2. A condensed threat checklist (embedded in NEXT.md — not a separate file)

**Work:**

1. **7 Knowledge Integrity Threats** — for each, does this SPEC address it?
   - T-1: Silent text corruption (OCR, encoding, normalization)
   - T-2: Attribution error (wrong author, school, date)
   - T-3: Taxonomic misplacement (wrong topic)
   - T-4: Consensus failure (LLM hallucination accepted)
   - T-5: Metadata loss (upstream field stripped)
   - T-6: Stale knowledge (outdated entry not refreshed)
   - T-7: Scope leak (non-scholarly content entering library)

2. **7 Silent Failure Patterns** — for each rule in §4, does it exhibit?
   - #1: Hollow example (passes even with wrong implementation)
   - #2: Circular definition (X defined as X)
   - #3: Hand-waving technology ("using NLP")
   - #4: Phantom metadata (field referenced but never produced)
   - #5: Untestable rule (no pass/fail criteria)
   - #6: Missing error path (what happens when this fails?)
   - #7: Scope creep disguise (feature that doesn't belong here)

3. **Three Challenges** (mental exercise, not a file read):
   - Hostile Implementer: what would a malicious implementation exploit?
   - Skeptical Scholar: what would make a scholar distrust this?
   - Technology Maximalist: what tool are we missing?

4. **Final quality gate:** All scripts pass, all defects addressed.

**Output:** Hardened SPEC marked as implementation-ready.

---

## Type I: IMPLEMENTATION_PREP Session

**Goal:** Prepare everything Claude Code needs to build this engine. This is the LAST Claude Chat session for each engine.

**When:** After the SPEC passes CREATIVE + PRECISION (+ optional HARDENING).

**Work:**
1. Create or update `contracts.py` — machine-readable Pydantic models matching SPEC §2/§3
2. Verify test fixtures exist in `tests/fixtures/`
3. Write the engine's CLAUDE.md with accurate implementation state
4. Update MILESTONES.md task decomposition for this engine
5. Create module stubs with SPEC-referencing docstrings (directory skeleton for Claude Code)
6. Write `IMPLEMENTATION_ORDER.md` — the build plan Claude Code follows
7. Write `TEST_PLAN.md` — test cases mapped to fixtures
8. Verify all dependencies in requirements.txt

**Output:** Engine directory fully ready for Claude Code.

**NEXT.md must point to the NEXT ENGINE's CREATIVE session** (or, if all engines are done, to a global verification session). Claude Chat does NOT do implementation — that is Claude Code's job. The preparatory phase ends when all engines have completed IMPL_PREP.

---

## Session Sequencing (per SPEC, pipeline order)

Each engine's IMPL_PREP session writes NEXT.md pointing to the NEXT engine's CREATIVE session. Claude Chat never does implementation — that's Claude Code's job.

```
Source engine:     C → P → H → I → [next engine]
Normalization:     C → P → H → I → [next engine]
Passaging:         C → P → I → [next engine]
Atomization:       C → P → I → [next engine]
Excerpting:        C → P → H → I → [next engine]
Taxonomy:          C → P → I → [next engine]
Synthesis:         C → P → H → I → [next engine]
Shared components: P → I each → [next component]
Scholar interface: C → P → H → I → [global verification]
```

After the LAST component's IMPL_PREP, NEXT.md points to a GLOBAL_VERIFICATION session (cross-SPEC coherence, implementation gate check, Claude Code environment final setup).

After global verification, the final Claude Chat task is: **PIPELINE_HARNESS_DESIGN** — design the `kr-pipeline` CLI tool that chains all 7 engines into a testable pipeline, generates human-readable reports (with Arabic content preserved), and supports regression testing. This is what Claude Code builds BEFORE individual engines. See `STRESS_TESTING.md` for the full testing phase architecture.

Estimated total: ~35-40 sessions. At 1-2 sessions per day, this is 3-5 weeks of preparatory work. After that, the repo is 100% ready for Claude Code to take over implementation.
