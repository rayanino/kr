# NEXT — Model Role Assignment Research + 5-Book LLM Integration Test Prep

## Current Position

- **Baseline:** 593 tests passing, 2 skipped, 0 failed
- **Commit:** `8e5fb12b` (master HEAD)
- **Engine:** Excerpting
- **Milestone:** First real LLM call PASSED — 5 excerpts from ibn_aqil_v1 preface, 0 errors, via OpenRouter/Opus 4.6

## What Just Happened

The excerpting engine's deterministic infrastructure is complete and the first real LLM smoke test succeeded:
- compute_page_range crash on split chunks: FIXED + ACCEPTED (3-pass review, 7 probes)
- EX-V-002 false positive (text_snippet length mismatch): FIXED
- Mock integration: all 5 packages pass
- Real LLM call: 1 chunk → 5 teaching units, correct descriptions, correct page ranges, 0 validation errors

## Task 1: Model Role Assignment Research (BLOCKING — do before Task 2)

The excerpting engine uses 3 LLM roles in a multi-model consensus architecture:

| Role | Current Model | Purpose |
|------|---------------|---------|
| Primary (classify, group, enrich) | `anthropic/claude-opus-4.6` | Generate structured scholarly extraction |
| Verify | `openai/gpt-4.1` ← **STALE** | Independently verify high-stakes fields (attribution, school) |
| Escalation (tiebreaker) | `cohere/command-a-03-2025` ← **STALE** | Break ties when primary and verifier disagree |

**Problem:** GPT-4.1 is legacy (GPT-5.4 exists). Command A is no longer frontier-tier. The model strings in `engines/excerpting/contracts.py` lines 749-761 need updating.

**Candidate frontier models (all available on OpenRouter as of March 2026):**
- `anthropic/claude-opus-4.6` — Opus 4.6
- `openai/gpt-5.4` — GPT-5.4 ($2.50/$15 per 1M tokens)
- `google/gemini-3.1-pro-preview` — Gemini 3.1 Pro ($2/$12 per 1M tokens)

**Research questions (answer with evidence, not intuition):**

1. **Which model is best at understanding classical Arabic scholarly text?** Not general Arabic — specifically matn/sharh/hashiyah structures, isnad chains, tahqiq apparatus, classical terminology. MMLU multilingual doesn't test this. Design a concrete probe.

2. **Which model is best at *catching errors it didn't make*?** The verifier sees the primary's output and must spot wrong attributions, wrong school classifications, decontextualized excerpts. This is a different skill from generation. Research whether any model has demonstrated superior error-detection in structured extraction tasks.

3. **Which model is best at adjudicating disagreements?** The escalation model sees "Model A says X, Model B says Y" and must reason about which is correct. This requires strong comparative reasoning on Arabic scholarly content.

4. **Does role assignment matter empirically?** Run the same 3 chunks through all 3 models as primary, compare output quality. This gives real data on classical Arabic capability, not benchmark proxies.

**Design an empirical probe:**
- Pick 3 chunks from different packages (1 single-layer prose, 1 multi-layer matn/sharh, 1 with footnotes)
- Run each through all 3 frontier models as primary (classify + group + enrich)
- Compare: segment boundary quality, teaching unit coherence, attribution accuracy, description quality
- Use this to assign roles based on actual KR performance, not general benchmarks

**Output:** Updated model strings in `contracts.py` with documented rationale. Commit as a design decision.

## Task 2: Prepare 5-Book LLM Integration Test

After Task 1 resolves the model config, prepare for the full 5-book test per `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md`.

This involves:
- Confirming the 5 test packages cover sufficient genre/format diversity
- Writing a CC handoff to run the full pipeline on all 5 packages with real LLM calls
- Designing the owner review protocol (which excerpts to spot-check, what to look for)

## Read First

1. `engines/excerpting/contracts.py:749-761` — current model config
2. `engines/excerpting/SPEC.md` §7.3 — consensus verification design
3. `reference/protocols/LLM_INTEGRATION_TEST_PROTOCOL.md` — full test protocol
4. `reference/AGENT_ARCHITECTURE.md` §1.2 P1 — knowledge diversity principle
5. `experiments/format_diversity_test/packages/` — the 5 test packages

## Session Start Protocol

1. Clone/pull repo
2. Read this NEXT.md
3. `git log --oneline -5`
4. `ls /mnt/skills/user/` — pick relevant skills (kr-research, thinking-frameworks, deep-research)
5. Read `reference/protocols/QUALITY_AXIOM.md`
6. DRIFT CHECK
