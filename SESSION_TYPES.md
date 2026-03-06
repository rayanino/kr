# Session Types — أنواع الجلسات

Each SPEC refinement is split into 2-3 focused sessions. Each session type has a specific goal, reads specific files, and produces specific output. This replaces the monolithic "do everything in one session" approach.

**Why split?** Claude Chat's creative output is highest when context is fresh and focused. A single session that reads 11 files and follows 10 steps produces mediocre work on all of them. Three focused sessions produce excellent work on each.

---

## Type C: CREATIVE Session (First session for each SPEC)

**Goal:** Invent transformative capabilities. This is the session that makes the application extraordinary.

**Context budget:** ~60% of tokens go to web search results and creative thinking. Only ~15% on reading existing content.

**Reads ONLY:**
1. The SPEC itself (§4.B and §1 only — skip §2-§3, §5-§10)
2. `reference/ENTRY_EXAMPLE.md` (quality target)
3. `reference/USER_SCENARIOS.md` (who benefits and how)

**Does NOT read:** Protocol documents, contracts.py, other SPECs, KNOWLEDGE_INTEGRITY.md, SILENT_FAILURES.md. These are for later sessions.

**Work (in this order):**

1. **Research the problem space** (3-5 web searches)
   - What tools exist for this engine's domain?
   - What do scholars wish they could do but can't?
   - What have digital humanities projects built for similar languages?
   
2. **Research the possibilities** (3-5 web searches)
   - What can LLMs do NOW for Arabic text analysis that they couldn't 2 years ago?
   - What techniques from Latin/Chinese/Hebrew DH could be adapted?
   - What open-source tools handle part of this engine's job?

3. **Invent capabilities** (the core creative work)
   For each capability: name it, name the technology, give a concrete output example with real Arabic text, explain why a scholar would weep with joy.
   
   Minimum: 3 new capabilities per engine. Aim for 5.
   
   Ask yourself:
   - After this engine processes 500 sources, what does it KNOW that didn't exist before?
   - What question can a scholar now answer that was literally impossible before?
   - What would take a human scholar 6 months that this engine does in 6 seconds?

4. **Write §4.B** — Full specification of each capability. Not vague aspirations. Inputs, outputs, triggers, algorithms, edge cases. Every capability specified precisely enough for Claude Code to implement.

5. **Update RESOURCES.md** with every tool discovered.

**Output:** Updated SPEC §4.B (scored ≥80/100 by creative_verification.py), updated RESOURCES.md.

**Anti-pattern to watch for:** Starting to review/correct §4.A rules. STOP. That's the next session's job. This session is for INVENTION only.

---

## Type P: PRECISION Session (Second session for each SPEC)

**Goal:** Make every rule machine-implementable. Claude Code should build from this with zero questions.

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

**Goal:** Prepare everything Claude Code needs to build this engine.

**When:** After the SPEC passes CREATIVE + PRECISION (+ optional HARDENING).

**Work:**
1. Create or update `contracts.py` — machine-readable Pydantic models matching SPEC §2/§3
2. Verify test fixtures exist in `tests/fixtures/`
3. Write the engine's CLAUDE.md with accurate implementation state
4. Update MILESTONES.md task decomposition for this engine
5. Write NEXT.md targeting Claude Code's first implementation task
6. Verify all dependencies in requirements.txt

**Output:** Engine directory ready for Claude Code to build in.

---

## Session Sequencing (per SPEC, pipeline order)

```
Source engine:     C → P → H → I   (critical engine, needs hardening)
Normalization:     C → P → H → I   (critical engine, needs hardening)
Passaging:         C → P → I       (simpler engine)
Atomization:       C → P → I
Excerpting:        C → P → H → I   (critical — self-containment judgment)
Taxonomy:          C → P → I
Synthesis:         C → P → H → I   (critical — produces user-facing content)
Shared components: P → I            (already have §4.B; need precision + prep)
Scholar interface: C → P → H → I   (critical — user-facing)
```

Estimated total: ~35-40 sessions. At 1-2 sessions per day, this is 3-5 weeks of preparatory work before implementation begins.
