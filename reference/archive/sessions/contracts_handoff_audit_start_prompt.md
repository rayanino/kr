Pull the repo and read NEXT.md. Your task is an independent cold-read audit of the CC handoff before it goes to Claude Code. Run `git log --oneline -5` to see current state. Before any work, read `reference/protocols/QUALITY_AXIOM.md` and scan `ls /mnt/skills/user/` for available skills.

<session_context>
The excerpting engine's SPEC is COMPLETE (2387 lines, 28 error codes, 29 invariants). It passed a kr-integrity 8-lens audit (28 defects found and fixed across 2 commits) and a deep post-audit review (4 more defects fixed). The SPEC is implementation-ready.

The current `NEXT.md` (654 lines, commit `4b71897`) is a CC handoff that instructs Claude Code to delete the stale `engines/excerpting/contracts.py` and rewrite it from scratch — defining all Pydantic types, sub-types, LLM response schemas, error codes, invariant validators, configuration constants, and test factory helpers.

**Why this audit matters:** The contracts.py is the type foundation for 5–7 build sessions. Every wrong field type, missing sub-model, or incorrect optionality silently propagates downstream. A bug in contracts.py doesn't surface until the build session that uses that type — potentially 3-4 sessions later. This is the cheapest moment to catch errors and the most expensive moment to miss them.

**Why a fresh session:** The same architect wrote the handoff AND reviewed it in the same chat. That violates standing order 8 of QUALITY_AXIOM.md ("never review your own output in the same chat"). The deep review caught 6 defects, but the question is what it missed because of anchoring bias.

HEAD commit: `c8ee74e`. Working tree is clean.

**What happens after this session:** The owner goes directly to a CC session. No intermediate review. Whatever NEXT.md you push is what CC builds from. You are the last human-in-the-loop before implementation starts.
</session_context>

<task>
Cold-read audit the CC handoff (`NEXT.md`) against the excerpting SPEC, then fix every defect you find. Your job: deliver a CC-ready NEXT.md. You are the last quality gate before Claude Code starts building.

**Work in 5 phases. I will say "continue" between phases.**

### Phase 1: Cold Read (no SPEC yet)

Read ONLY `NEXT.md`. Do NOT open the SPEC yet. As a fresh reader:
- List every place where you would need to guess, assume, or look something up
- List every internal inconsistency within the handoff itself
- List every place where "CC could follow this literally and still get it wrong"
- Note which field specifications feel under-specified (missing types, defaults, or constraints)

Deliver Phase 1 findings. Stop.

### Phase 2: Field-by-Field SPEC Verification

Now open the SPEC sections the handoff references. For each major type definition in the handoff, do a **field-by-field comparison** against the SPEC:

**Types to verify (11 groups):**
1. `AssembledChunk` — handoff §3 vs SPEC §2.3.2 (lines 136–195)
2. `ClassifiedSegment` — handoff §3 vs SPEC §2.3.3 (lines 196–223)
3. `TeachingUnit` — handoff §3 vs SPEC §2.3.4 (lines 225–252)
4. `ExcerptRecord` — handoff §4 vs SPEC §2.2.2 (lines 384–490)
5. All sub-types — handoff §2 vs SPEC §2.2.2 inline definitions + §2.3.2 sub-types
6. `UnitEnrichment` — handoff §5 vs SPEC §7.2.4 (lines 1669–1728)
7. `VerificationItem` — handoff §5 vs SPEC §7.3.2 (lines 1801–1815)
8. `ClassificationResult` — handoff §5 vs SPEC §5.2.4 (lines 874–887)
9. `ExtractionResult` — handoff §5 vs SPEC §5.3.4 (lines 1019–1031)
10. Error codes — handoff §6 vs SPEC §8.1 (lines 1915–1986)
11. Configuration constants — handoff §8 vs SPEC §8.3 (lines 2018–2074). Verify every default value.

**For each field, verify with tool calls (grep/view):**
- Name: exact match?
- Type: exact match (including Optional, list[], etc.)?
- Required/Optional: does the handoff's Pydantic mapping match SPEC's "Required" column?
- Default value: if specified, does it match?
- Description: does the handoff omit anything CC needs to know?

**Also verify cross-engine imports:**
Open `engines/normalization/contracts.py` and verify that every type the handoff says to import actually exists with the field structure the excerpting SPEC assumes.

**Also verify invariant-to-validator mapping:**
The SPEC defines 29 invariants (I-AC-1 through I-AC-7, I-CS-1 through I-CS-6, I-TU-1 through I-TU-9, I-ER-1 through I-ER-7). The handoff assigns each to a validator function. Verify: does every invariant have a home? Are any invariants assigned to the wrong validator? Are any invariants that should be model_validators (per-instance) vs standalone validators (cross-object) assigned to the wrong category?

Deliver Phase 2 findings. Stop.

### Phase 3: Verification Check Stress Test

The handoff has 11 verification checks that CC must pass. For each check:
1. Read the check
2. Attempt to construct a **concrete wrong implementation** that would pass it
3. If you can construct one, the check is insufficient — report as a finding

Also: are there verification checks that SHOULD exist but don't?

Deliver Phase 3 findings. Stop.

### Phase 4: CC Simulation

Re-read NEXT.md one final time as Claude Code about to build.
- Walk through the build mentally: "I define ScholarlyFunction... I define PageRange... I define AssembledChunk..." At each step, ask: "Do I have everything I need from the handoff? Am I guessing anything?"
- Check: are there normalization types CC needs to import that the handoff doesn't mention?
- Check: do the factory helper instructions give CC enough to create valid default objects?
- Check: do the Design Decisions cover every judgment call, or would CC need to make decisions?

Deliver Phase 4 findings. Stop.

### Phase 5: Fix and Finalize

You have full authority to fix every finding from Phases 1–4 directly. Do NOT report findings back for someone else to fix — you fix them.

**For each finding:**
1. Open NEXT.md
2. Apply the fix (correct field name, add missing type, fix optionality, add missing verification check, etc.)
3. Verify the fix against the SPEC with a tool call

**Constraints on fixes:**
- Design decisions in NEXT.md §"Design Decisions" are FINAL. Do not change them. If you believe a design decision is wrong, note it as an observation but do not modify it.
- Do not add implementation logic. The handoff is for type definitions and validators only.
- Do not modify the SPEC. If the SPEC and handoff disagree, fix the handoff to match the SPEC.
- Every fix must be grounded: "SPEC line N says X, handoff said Y, fixed to X."

**After all fixes are applied:**
1. Re-read the entire NEXT.md one final time for internal consistency
2. Commit with a message listing every finding and fix
3. Push to the repo

**Then deliver your verdict:**
- **APPROVED** — NEXT.md is fixed, committed, and CC-ready. State the commit hash.
- **BLOCKED** — you found issues you cannot fix within the constraints above. List them with reasoning. (This should be rare — most findings are fixable.)

Every finding blocks until fixed. The session ends only when NEXT.md is CC-ready or explicitly blocked on something unfixable.
</task>

<what_to_read>
In this order — Phase 1 reads only item 1. Phase 2 adds the rest.

1. `NEXT.md` — the artifact being audited (654 lines). Read in FULL.
2. `reference/protocols/QUALITY_AXIOM.md` — the quality standard (102 lines)
3. `engines/excerpting/SPEC.md` §2.3 (lines 79–278) — internal data model
4. `engines/excerpting/SPEC.md` §2.2 (lines 365–521) — output contract
5. `engines/excerpting/SPEC.md` §8.1 (lines 1915–1986) — error codes
6. `engines/excerpting/SPEC.md` §7.2.4 (lines 1669–1728) — enrichment response schema
7. `engines/excerpting/SPEC.md` §7.3.2 (lines 1765–1824) — verification response schema
8. `engines/excerpting/SPEC.md` §5.2.4 (lines 874–887) — classification response schema
9. `engines/excerpting/SPEC.md` §5.3.4 (lines 1019–1031) — grouping response schema
10. `engines/excerpting/SPEC.md` §8.3 (lines 2018–2074) — configuration parameters
11. `engines/normalization/contracts.py` — cross-engine types (725 lines). Verify imports.

Do NOT read the entire SPEC. Do NOT read the SPEC before Phase 1 — the cold read must be unbiased.
</what_to_read>

<what_NOT_to_do>
- Do NOT audit the SPEC itself. The SPEC passed a kr-integrity audit and a deep review. This session audits the HANDOFF, not the SPEC. If you find something in the SPEC that seems wrong, note it — but the primary task is verifying the handoff accurately reflects the SPEC.
- Do NOT change design decisions. The design decisions in the handoff (§"Design Decisions") are final. If you believe one is wrong, note it as an observation but do not modify it. Your job is to verify the handoff correctly implements those decisions.
- Do NOT re-examine the architecture. The 5-engine pipeline and 3-phase excerpting design are committed.
- Do NOT write engine implementation code. Editing NEXT.md to fix findings IS your job. Writing Python engine code is NOT.
- Do NOT skip Phase 1 or merge phases. The cold read before opening the SPEC is the highest-value step — it catches what a fresh reader sees that the author cannot.
- Do NOT modify the SPEC. If the SPEC and handoff disagree, fix the handoff to match the SPEC.
</what_NOT_to_do>

<skills>
Invoke ALL of these explicitly at session start:
- `critical-review` — the primary skill for verification work
- `thinking-frameworks` — multi-angle analysis on ambiguous findings

Do NOT invoke kr-integrity (that's for SPEC audits, not handoff audits).
</skills>

<quality>
Take all your time. No rush. This is the last quality gate before the most significant engine starts building.

**The standard:** After this session, NEXT.md is CC-ready. CC receives it and builds contracts.py with zero clarifying questions. Every type is right, every field is right, every optionality is right, every verification check catches what it should. If CC has to guess anything, this session failed.

**You own the outcome.** You are not a reviewer who reports findings — you are the final quality gate who delivers a CC-ready artifact. Find issues, fix them, verify the fixes, commit. The owner says "continue" and starts the CC session with whatever you push.

**Ground every finding in tools.** Don't say "I think field X might be wrong" — open the SPEC, read the line, compare against the handoff, state the exact discrepancy. Grep counts, view line ranges, compare character by character.

**The most dangerous pattern:** Finding something that seems wrong, then talking yourself out of it because "the architect probably already checked this." The architect checked it in the same context where they wrote it. You are here specifically because that check is insufficient.

Every finding blocks until fixed. There is no "probably fine" category.
</quality>
