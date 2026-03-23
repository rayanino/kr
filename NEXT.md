# NEXT — Excerpting Engine: Build Preparation (Step 3c)

## Current Position

- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Excerpting SPEC: ✅ COMPLETE (2387 lines, 12 sections)
- kr-integrity audit: ✅ PASS (11 HIGH, 15 MEDIUM, 2 LOW — all fixed)
- Post-audit deep review: ✅ PASS (1 HIGH, 3 MEDIUM — all fixed)
- Contracts.py: ✅ REWRITTEN (1111 lines, independently reviewed, F-1 fixed)
  - 2 enums, 12 sub-types, 4 main types, 7 LLM schemas
  - 29 invariant checks (6 model_validators + 7 standalone functions)
  - 28 error codes, 18 config parameters
  - 4 test factory helpers in conftest.py (184 lines)
- HEAD commit: `57615a38` (independent review ACCEPT + F-1 fix)
- **Excerpting engine code: NONE. Next step is build preparation.**
- Excerpting tests: conftest.py factories only (no test files yet)

## What to Do

This is a Claude Chat (Architect) session. Produce the build preparation package per `reference/ENGINE_BUILD_BLUEPRINT.md` §2a.

**Five deliverables:**

### 1. Technology Survey

For each excerpting engine capability that involves external tools or libraries, verify it exists, works for Arabic, and has the specific API the SPEC assumes. Per the build-prep skill: technology survey FIRST, architecture SECOND.

**Capabilities to survey:**

| Capability | SPEC Section | Key Question |
|-----------|-------------|--------------|
| Structured LLM output via Pydantic | §5.2, §5.3, §7.2 | Does `instructor` work with OpenRouter + Opus 4.6? Schema validation + retry? |
| OpenRouter API routing | §8.3 | Confirm `instructor.from_openai(openai.OpenAI(base_url=...))` pattern works for all 3 model providers |
| Arabic word tokenization | §2.3.2 I-AC-1 | Is Python `str.split()` the right tokenizer for Arabic scholarly text? Any edge cases with diacritics? |
| Quran verse pattern matching | §7.1 F-DET-5 | What regex patterns detect ﴿...﴾ delimiters reliably in Shamela HTML exports? |
| Division tree traversal | §4.2 | Does the normalization engine's `DivisionNode` support the tree walk Phase 1 needs? |
| Text layer rebasing | §4.6 | Character offset arithmetic — any library, or pure Python? |
| Hadith collection name matching | §7.2.4 TakhrijEntry | Are there reference datasets of Arabic hadith collection names? |

Minimum 8 searches. For any claim about a tool working with Arabic: verify with actual documentation or benchmarks, not README taglines.

### 2. Module Architecture

Define the file structure for `engines/excerpting/src/`. For each module: purpose, inputs/outputs, SPEC sections it implements, which contracts types it consumes/produces.

Proposed starting point (adjust based on survey):

```
engines/excerpting/src/
├── __init__.py
├── phase1_assembly.py     — §4: deterministic preprocessing
├── phase2_classify.py     — §5.2: LLM segment classification
├── phase2_group.py        — §5.3: LLM teaching unit grouping
├── phase2_normalize.py    — §5.4: offset normalization + coverage verification
├── phase3_deterministic.py — §7.1: 9 deterministic fields (F-DET-1–9)
├── phase3_enrichment.py   — §7.2: LLM enrichment call
├── phase3_consensus.py    — §7.3: verification + consensus resolution
├── phase3_validation.py   — §7.4: output validation (V-P3-1–9)
├── domain_rules.py        — §6: 22 domain-specific rules
├── pipeline.py            — Orchestrator: Phase 1 → Phase 2 → Phase 3
└── writer.py              — JSONL output + gate queue writing
```

### 3. Stub Files

Write module stubs with complete type signatures, docstrings referencing SPEC sections, and `raise NotImplementedError` bodies. Every stub references contracts types by import.

### 4. Test Infrastructure

Define test file structure and for each file: list test categories, fixture requirements, SPEC invariants verified.

### 5. First CC Build Session NEXT.md

Write a focused NEXT.md for CC Session 1, following `kr-preparing-cc-handoffs` protocol (9 steps). Recommended scope: Phase 1 (deterministic preprocessing).

### 6. Update CLAUDE.md

Reflect current state. Keep under 200 lines.

## Read First (in this order)

1. **`NEXT.md`** — this file (current directive)
2. **`engines/excerpting/CLAUDE.md`** — engine orientation (109 lines, needs update)
3. **`engines/excerpting/SPEC.md` §4** (lines 601–764) — Phase 1 (first build target)
4. **`engines/excerpting/SPEC.md` §2.3.2`** (lines 143–200) — AssembledChunk (Phase 1 output)
5. **`engines/excerpting/contracts.py`** — all types (1111 lines, skim for type signatures)
6. **`engines/normalization/contracts.py`** — upstream types consumed by Phase 1 (725 lines, focus on NormalizedPackage, DivisionNode, ContentUnit)
7. **`reference/ENGINE_BUILD_BLUEPRINT.md` §2a** (lines 206–280) — build preparation requirements
8. **`experiments/architecture_test/run_tests.py`** — validated LLM approach + prompts

Do NOT read the entire SPEC upfront. Read §4 for the first build target, skim §5/§7 headers for module architecture, and refer to specific sections as needed.

## Design Decisions (pre-resolved)

1. **All LLM calls go through OpenRouter.** Pattern: `instructor.from_openai(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=OPENROUTER_KEY))`.
2. **Normalization types imported, never redefined.** Already done in contracts.py.
3. **`tracer.py` is a historical artifact.** Do NOT extend — start fresh with stubs.
4. **Experiment prompts are reference, not production.** Adapt for the full engine context.
5. **Phase 1 is the first build target.** Fully deterministic, no LLM, clear invariants.

## Do NOT Do

- No implementation code. Stubs only. Implementation is CC's job.
- No SPEC modifications. Note issues, don't fix them.
- No contracts.py modifications. It was independently reviewed and accepted.
- No test assertions. Test stubs list categories and fixtures, not actual test code.
- No scoping beyond CC Session 1. Later sessions scoped after Session 1 review.

## Verification

Before committing:
1. Every stub file imports correctly: `python -c "from engines.excerpting.src.phase1_assembly import *"`
2. Every type reference in stubs resolves to a real contracts type
3. CLAUDE.md is under 200 lines
4. CC Session 1 NEXT.md follows the 9-step handoff protocol

## After This

1. CC Session 1: Phase 1 implementation
2. Architect reviews CC Session 1 output
3. CC Session 2: Phase 2 implementation
4. ... iterate until all phases built
5. Integration testing
6. 3-probe evaluation

## Progress Tracker

- [x] Step 0: Evaluate SPEC_OUTLINE.md
- [x] Step 1: Write SPEC_OUTLINE.md
- [x] Step 2: Write all 12 SPEC sections + coherence review
- [x] Step 2 bonus: Update CLAUDE.md
- [x] Step 3a: kr-integrity audit (28 error codes after fix)
- [x] Step 3b: Rewrite contracts.py (CC task) + independent review
- [ ] **Step 3c: Build prep (THIS SESSION)**
- [ ] Step 4+: Build (Phase 1 → Phase 2 → Phase 3 → integration)

## Session History

- Session 0: SPEC_OUTLINE.md evaluation
- Session 1–4: Write all 12 SPEC sections (2387 lines)
- Session 5: kr-integrity audit (11 HIGH, 15 MEDIUM, 2 LOW — all fixed)
- Session 6: Deep review (1 HIGH, 3 MEDIUM — all fixed) + SPEC cleanup
- Session 7: contracts.py rewrite handoff → CC
- Session 8: Independent contracts.py review (F-1 fixed)
- **Session 9 (next): Build preparation**

## Skills to Invoke

- `kr-build-prep` — primary skill (technology survey → architecture → stubs → tests → CLAUDE.md)
- `kr-research` — deep research for technology survey (8+ searches per capability)
- `thinking-frameworks` — multi-angle analysis on module architecture
- `critical-review` — self-verify every deliverable before committing
- `kr-preparing-cc-handoffs` — for writing CC Session 1 NEXT.md (9-step protocol)
