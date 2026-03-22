# Excerpting SPEC Writing — Session 3 Handoff

**Date:** 2026-03-22
**Session scope:** §7 (Phase 3: Metadata Enrichment) + §2.2 (Output Contract) + §8 (Error Handling and Configuration)
**Commits:** `0bb9621` through `5ef27a5` (3 section commits + progress update)
**SPEC status:** 1970 lines, 9/12 sections complete

---

## What Was Done

| Section | Lines | Commit | Key Decision |
|---------|-------|--------|-------------|
| §7 Phase 3: Metadata Enrichment | 509 | `0bb9621` | Per-chunk LLM enrichment call; no proposed_leaf (topic keywords only); GPT-4.1 default verifier; 3-model escalation for LA-3 |
| §2.2 Output Contract | 153 | `40aace9` | 33 fields across 7 categories; 7 output invariants (I-ER-1–7); downstream consumer contract with required vs informational fields |
| §8 Error Handling and Configuration | 164 | `5ef27a5` | All 27 error codes cataloged; 20 config parameters; retry→degrade→skip→flag pattern; EX-M-008 halts on invisible uncertainty |

---

## Design Decisions Made

### Decision 1: Phase 3 LLM call granularity → Per-chunk

One enrichment call per AssembledChunk (not per-unit). Rationale: inter-unit context improves quality — when unit 5 references "as mentioned above," the LLM can see unit 3. School attribution is more consistent when the LLM sees all units from the same textual context. Per-chunk failure risk is mitigated by deterministic fallback (§7.1 fields survive LLM failure).

### Decision 2: No `proposed_leaf` → Topic keywords only

The old SPEC's `proposed_leaf` field (taxonomy tree path proposal) is removed. The excerpting engine produces `excerpt_topic` (1–3 Arabic topic keywords). The taxonomy engine maps topics to tree positions. Rationale: the taxonomy engine owns the tree and may restructure it — pre-proposed paths would be invalidated. Clean engine boundary: excerpting knows content, taxonomy knows structure.

### Decision 3: Consensus model providers → Configurable defaults

- Default enrichment model: `anthropic/claude-opus-4.6` (same as Phase 2)
- Default verification model: `openai/gpt-4.1` via OpenRouter (different provider family per Layer 3.5)
- Default escalation model: `cohere/command-a-03-2025` via OpenRouter (third provider for 3-way escalation)
- All model strings are configuration parameters in §8.3, updatable without SPEC changes.

### Decision 4: §2.3.5 → Summary pointing to §2.2

§2.3.5 (ExcerptRecord placeholder) updated to be a brief summary referencing §2.2 as the authoritative field specification. No field duplication across two locations.

---

## Accumulated ID Registries

All IDs verified programmatically against the SPEC (1970 lines, 9 sections).

**Invariants:**
- I-AC-1 through I-AC-7 (AssembledChunk, §2.3.2)
- I-CS-1 through I-CS-6 (ClassifiedSegment, §2.3.3)
- I-TU-1 through I-TU-9 (TeachingUnit, §2.3.4)
- I-ER-1 through I-ER-7 (ExcerptRecord output, §2.2.3) — **NEW in session 3**

**Verification checks:**
- V-P1-1 through V-P1-6 (Phase 1, §4.9)
- V-P2-1 through V-P2-19 (Phase 2, §5.4.2 and §5.4.3)
- V-P3-1 through V-P3-9 (Phase 3, §7.4) — **NEW in session 3**

**Error codes (27 total):**
- EX-A-002, 003, 004, 005, 006, 010, 011 (Phase 1 assembly)
- EX-C-001, 002, 003, 004, 005 (Phase 2 classification/grouping)
- EX-M-001, 002, 003, 004, 005, 006, 007, 008, 009, 010 (Phase 3 metadata) — **EX-M-002–010 NEW in session 3**
- EX-V-001, 002 (validation) — **EX-V-002 NEW in session 3**
- EX-G-001, 002, 003 (human gates) — **ALL NEW in session 3**

**Self-containment criteria:** C-SC-1 through C-SC-5 (§3.2)

**Domain rules (§6):**
- DP-1 through DP-6, LA-1 through LA-4, EV-1 through EV-3
- IR-1 through IR-3, VC-1 through VC-3, QM-1 through QM-3

**Deterministic enrichment fields:** F-DET-1 through F-DET-9 (§7.1) — **NEW in session 3**

**Configuration parameters:** 20 total in §8.3 — **NEW in session 3**

---

## What's Next — Session 4 Sections

From the progress tracker (3 remaining):

| Order | Section | Estimated Lines | Source Material | Complexity |
|-------|---------|----------------|-----------------|------------|
| 1 | §1 Purpose and Scope | ~80 | All existing sections | LOW — written last, summary |
| 2 | §9 Deferred Capabilities | ~100 | Old SPECs §4.B sections (all three engines) | LOW — table + hooks |
| 3 | §10 Test Requirements | ~150 | §4/§5/§6/§7, experiment fixtures, normalization test patterns | MEDIUM — adversarial cases |

After all 12 sections: final coherence review pass, then update contracts.py and CLAUDE.md.

**Chat allocation:** Session 4 should complete §1, §9, §10 + coherence review + contracts/CLAUDE update. If context degrades, prioritize §1 and §9 (low complexity) and defer §10 to session 5.

---

## §1 Reading Instructions

§1 is the easiest section — it summarizes everything above. Read:
1. **`engines/excerpting/SPEC.md` section headers** — `grep "^## §\|^### §" engines/excerpting/SPEC.md` for the complete structure
2. **`engines/excerpting/SPEC_OUTLINE.md` lines 52–70** — the outline's §1 section (Purpose and Scope)
3. **`experiments/architecture_test/ARCHITECTURE_DECISION.md`** — pipeline position and absorption rationale

No external source material needed. §1 introduces the engine's purpose, scope, and relationship to other engines.

## §9 Reading Instructions

§9 catalogs deferred capabilities from all three old SPECs.

1. **`engines/excerpting/SPEC_OUTLINE.md` lines 536–565** — the outline's §9 section with the deferred capabilities table
2. **`reference/archive/abd_code/excerpting/SPEC_old_original.md` lines 566–850** — old SPEC §4.B.1 through §4.B.8 (Transformative Capabilities)
3. **`engines/passaging/SPEC.md`** — search for "§4.B" sections
4. **`engines/atomization/SPEC.md`** — search for "§4.B" sections

The outline already has the complete deferred capabilities table. §9 mainly needs to specify extension hooks (which ExcerptRecord fields or processing steps to add) for each deferred capability.

## §10 Reading Instructions

§10 defines test requirements — what must be tested, at what level (unit/integration/evaluation), and with what fixtures.

1. **`engines/excerpting/SPEC_OUTLINE.md` lines 567–627** — the outline's §10 section (§10.1–§10.5 with test categories and adversarial cases)
2. **All verification checks:** V-P1-1–6, V-P2-1–19, V-P3-1–9 — these are the unit test targets
2. **All invariants:** I-AC-*, I-CS-*, I-TU-*, I-ER-* — structural constraints to verify
3. **All error codes:** 27 codes — each needs at least one test that triggers it
4. **`experiments/architecture_test/`** — experiment fixtures that become integration test inputs
5. **Normalization engine test patterns:** `engines/normalization/tests/` for conftest.py patterns, fixture organization, factory helpers
6. **Old excerpting SPEC §10:** `reference/archive/abd_code/excerpting/SPEC_old_original.md` line 986+ — old test requirements (adapt to new architecture)
7. **Old atomization SPEC §10:** `engines/atomization/SPEC.md` line 1148+ — atomization test requirements (relevant for Phase 2 classification testing)

---

## Traps to Avoid

1. **§10 should specify WHAT to test, not HOW.** Test requirements, not test implementations. The builder (CC) writes the actual test code. The SPEC specifies: which inputs to test, what outputs to verify, which error paths to exercise, and what fixtures to use.

2. **§9 should define extension hooks, not extension implementations.** Each deferred capability gets: a description, the ExcerptRecord field(s) it would add, and the processing step where it would plug in. No implementation detail.

3. **§1 should be short.** It's a summary, not a re-statement. Point to the relevant sections rather than repeating content.

4. **Don't forget the coherence review.** After all 12 sections are written, do a final pass checking: every §2.2 field traces to a §7 step, every §8 error code is defined in §4–§7, every §6 domain rule is referenced in §7, every §3 self-containment criterion appears in the §5.3.2 prompt.

---

## Session End Retrospective

**What went wrong:** Nothing major. The session completed all 3 planned sections without issues. The programmatic verification scripts caught no errors — all cross-references, ID sequences, and field traceabilities were correct on first write. This may indicate the verification is not adversarial enough, or it may indicate that the handoff document's field inventory (session 2) was thorough enough to prevent errors.

**Root cause analysis of smoothness:** The session 2 handoff was exceptionally well-structured — it contained a complete field inventory for §7, explicit reading instructions with line numbers, 4 pre-identified design decisions, and 6 traps to avoid. This pre-work meant §7 could be written directly from the inventory rather than requiring discovery during writing.

**Lesson:** The quality of a session is determined by the quality of the previous session's handoff. Investing time in handoff completeness (field inventories, pre-identified decisions, verified file paths) pays off in faster, more accurate writing.

**Stale memory entries:** The "KR EXCERPTING ENGINE STATE" memory entry references the old 16-finding review and says SPEC is BLOCKED. This is stale — the SPEC rewrite is in progress (9/12 sections complete). However, this memory entry serves as useful history, so no removal needed — it correctly records the starting state.

**Protocol changes to propose:** None. The section-by-section writing pattern + programmatic verification continues to work well. The handoff document structure (field inventory + design decisions + reading instructions + traps) should be replicated for session 4.

**What next session needs:** A new Claude Chat session. Start by cloning the repo, reading NEXT.md, reading this handoff file. Write §1, §9, §10 in order. Then do a final coherence review pass. Then update contracts.py and CLAUDE.md.
