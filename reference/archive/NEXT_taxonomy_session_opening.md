# NEXT — Taxonomy Engine: Core SPEC Rewrite + Build Prep

## Context

The excerpting engine is running. CC is completing model comparison (codex vs claude)
and will execute the 5-book integration run. That work is independent — results will be
evaluated in a future session (estimated 2-3 days from now).

**This session starts the taxonomy engine** — the last piece before v1 E2E pipeline.

## What the Taxonomy Engine Does (v1)

Takes excerpts from the excerpting engine and places each one at the correct leaf
in the existing science trees. Five sciences exist with 922 total leaves:
- nahw (226 leaves), sarf (226), balagha (335), aqidah (30), imlaa (105)

After taxonomy, excerpts are browsable by science and topic. That's the v1 milestone.

## What's Already Done

1. **Full SPEC exists:** `engines/taxonomy/SPEC.md` (945 lines, very ambitious)
2. **Core extraction (Part 1) done:** `engines/taxonomy/CORE_EXTRACTION.md`
   - 24 core / 42 deferred capabilities classified
   - Critical contract gap identified (5 fields taxonomy expects but excerpting doesn't produce)
   - Three uncertain classification calls documented
3. **Science trees exist:** `library/sciences/{science_id}/tree.yaml`
4. **Contracts exist:** `engines/taxonomy/contracts.py` (491 lines, needs trimming to match core)
5. **Reference taxonomy:** `engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md`

## What This Session Must Do

### Phase 1: Review + Approve Core Extraction
- Read `engines/taxonomy/CORE_EXTRACTION.md`
- Resolve the 3 uncertain items and the contract gap decision
- ChatGPT Pro MUST review the classification (deep research prompt below)

### Phase 2: Core SPEC Rewrite
- Rewrite `engines/taxonomy/SPEC.md` to core-only v1
- Replace deferred sections with `[DEFERRED TO STAGE 2]` stubs
- Fix the input contract to match actual excerpting output
- ChatGPT Pro reviews the rewritten SPEC

### Phase 3: Build Prep
- Use `kr-build-prep` skill
- Trim contracts.py to core-only models
- Produce CLAUDE.md, stubs, test plan for CC
- ChatGPT Pro reviews build prep before CC handoff

## Governance: ChatGPT Pro at Every Decision Point

ChatGPT Pro (deep research mode) MUST be consulted at every major decision.
The architect prepares targeted prompts. The owner fires them. ChatGPT catches
what the architect missed. This is the same governance model from the excerpting
engine (Session 28 proof: ChatGPT + fresh Claude caught bugs the architect missed).

Minimum ChatGPT checkpoints this session:
1. Core extraction review (is the core/deferred split right?)
2. Contract gap resolution (how to handle missing fields?)
3. Core SPEC review (before declaring implementation-ready)
4. Build prep review (before CC handoff)

## Key Files

| File | Purpose |
|------|---------|
| `engines/taxonomy/SPEC.md` | Full SPEC (to be rewritten as core-only) |
| `engines/taxonomy/CORE_EXTRACTION.md` | Classification table (Part 1 done) |
| `engines/taxonomy/contracts.py` | Pydantic models (needs core trimming) |
| `engines/taxonomy/reference/ABD_TAXONOMY_SPEC.md` | Domain reference |
| `library/sciences/*/tree.yaml` | Existing science trees (922 leaves) |
| `integration_tests/smoke_fix_20260329/*/excerpts.jsonl` | Real excerpts (actual format) |
| `reference/GOVERNANCE.md` | Review team rules |

## Parked Work (Do Not Touch)

- **Excerpting engine evaluation:** CC is running model comparison + 5-book run.
  Results will be evaluated in a separate session ~2-3 days from now.
- **Synthesis engine:** Explicitly out of scope. Not thinking about it.
- **Factory infrastructure:** D-H001-H011 all finalized, deployed after engines complete.

## Do NOT Do

- Do NOT evaluate excerpting output (that's a future session)
- Do NOT touch the synthesis engine
- Do NOT build without ChatGPT Pro review at every checkpoint
- Do NOT let momentum override quality — the taxonomy SPEC must be right before CC builds
