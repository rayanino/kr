# Excerpting Engine — محرك الاقتطاف

**Position:** Source ✅ → Normalization ✅ → **Excerpting** → Taxonomy → Synthesis.
**Absorbs:** passaging (Phase 1) + atomization (Phase 2). Architecture rationale: `experiments/architecture_test/ARCHITECTURE_DECISION.md`.

## Commands

```bash
test:  python -m pytest engines/excerpting/tests/ -x -v
lint:  ruff check engines/excerpting/
check: python -c "from engines.excerpting.src.phase1_assembly import run_phase1"
```

## Architecture

Three-phase pipeline. One source at a time. See `engines/excerpting/docs/architecture.md` for full data flow.

```
NormalizedPackage → Phase 1 (deterministic) → Phase 2 (LLM) → Phase 3 (enrichment) → ExcerptRecords
```

**Phase 1** (`phase1_assembly.py`): §4. Walk division tree → assemble text → merge tiny → split oversized → aggregate metadata → rebase layers → validate. No LLM. Fully testable.

**Phase 2** (`phase2_classify.py` + `phase2_group.py`): §5. Classify segments by scholarly function (16-type taxonomy) → group into teaching units. Two LLM calls per chunk via Instructor + OpenRouter.

**Phase 3** (`phase3_deterministic.py` + `phase3_enrichment.py` + `phase3_consensus.py` + `phase3_validation.py`): §7. Nine deterministic fields (F-DET-1–9) → LLM enrichment (one call per chunk) → consensus verification (different-provider model) → human gates → output validation.

Output: `writer.py` → `excerpts.jsonl` + `gate_queue.jsonl`.

## Key Files

| File | Lines | Purpose |
|------|-------|---------|
| `SPEC.md` | 2387 | Behavioral authority (12 sections) |
| `contracts.py` | 1111 | All types: 2 enums, 12 sub-types, 4 main types, 7 LLM schemas, 28 error codes, 18 config params |
| `tests/conftest.py` | 184 | 4 factories: AssembledChunk, ClassifiedSegment, TeachingUnit, ExcerptRecord |
| `docs/architecture.md` | — | Module structure, data flow, build session plan |
| `docs/testing.md` | — | Test categories per file, fixture requirements |
| `docs/llm_trustworthiness_defenses.md` | — | **Sessions 4–6 MANDATORY.** Failure-mode matrix, Tier 1 deterministic defenses, empirical scan requirements |
| `docs/technology_survey.md` | — | Verified tool/library capabilities |
| `session-1-plan.md` | — | CC Session 1 directive (Phase 1 build) |

## Critical Constraints

- **Arabic diacritics:** Preserve byte-for-byte. No Unicode normalization (NFC/NFD/NFKC/NFKD).
- **Metadata:** Never delete upstream fields (D-023). Pass through everything from normalization.
- **Errors:** Fail loudly with SPEC §8 error codes. Never silently drop data.
- **OpenRouter only:** All LLM calls via OpenRouter. Pattern: `instructor.from_openai(openai.OpenAI(base_url="https://openrouter.ai/api/v1", api_key=KEY), mode=instructor.Mode.JSON)`.
- **D-011:** No excerpt spans a chunk boundary. Enforced by construction (LLM sees one chunk).
- **EX-M-008:** Gate write failure → HALT. Invisible uncertainty > visible stop.
- **Step ordering (§4.1):** Footnote renumbering (§4.7) BEFORE text layer rebasing (§4.6).

## Model Configuration

Model roles verified empirically on 2026-03-28 against actual KR Arabic scholarly text via OpenRouter.

| Role | Model | Provider | Purpose |
|------|-------|----------|---------|
| Primary (classify + enrich) | `openai/gpt-5.4` | OpenAI | Phase 2 classification, Phase 2 grouping, Phase 3 enrichment |
| Verify | `anthropic/claude-opus-4.6` | Anthropic | Phase 3 consensus verification |
| Escalation | `mistralai/mistral-large-2411` | Mistral | Phase 3 disagreement adjudication |

Three-provider diversity (Anthropic → OpenAI → Mistral) ensures no single-provider outage blocks the pipeline. Gemini 3.1 Pro was rejected (fails structured output). Command A was rejected (no tool-use on OpenRouter).

## Current State

- **SPEC:** COMPLETE (2387 lines)
- **Contracts:** COMPLETE (1111 lines, independently reviewed)
- **Phase 1:** COMPLETE (117 tests, 1,531 lines) — deterministic assembly + hardening
- **Phase 2:** COMPLETE (141 tests, 854 lines) — LLM classification + grouping + hardening
- **Phase 3.1:** COMPLETE (86 tests, 637 lines) — deterministic metadata assembly (10 functions, review + bugfix + hardening)
- **Phase 3.2:** COMPLETE (27 tests, ~300 impl lines) — LLM enrichment (enrich_chunk, apply_enrichment, run_phase3_enrichment, _merge_scholars)
- **Phase 3.3:** COMPLETE (33 tests, ~450 impl lines) — Consensus verification + human gates (verify_chunk, resolve_consensus, check_gate_triggers, run_consensus)
- **Phase 3.4:** COMPLETE (50 tests, ~350 impl lines) — validation (V-P3-1–9) + output writer (excerpts.jsonl, gate_queue.jsonl, V-P3-7 paranoid verification)
- **Phase 3 Orchestrator:** COMPLETE (25 integration tests, ~300 impl lines) — phase3_orchestrator.py + pipeline.py + end-to-end tests
- **Overnight Hardening:** 40+ additional edge case tests across all phases
- **Total:** 593 tests, ~4,860 impl lines, 0 failures

### Recent Sessions (post-overnight hardening)
- **Preamble gap fix:** `_complete_division_tree()` inserts synthetic leaf nodes for parent content gaps (2-29% content was silently lost). ACCEPTED.
- **compute_page_range fix:** Partition `physical_pages` alongside `join_points` in split chunks. Defensive guard in `compute_page_range`. ACCEPTED.
- **EX-V-002 fix:** Compare `text_snippet` at min(snippet_len, 80) instead of fixed 80 — LLMs produce 51-74 chars, not exactly 80.
- **--max-chunks:** CLI argument for `run_integration_test.py` to limit LLM phases to N chunks.
- **First real LLM call:** Smoke test passed — 5 excerpts from ibn_aqil_v1 preface, 0 errors, 88s total via OpenRouter/Opus 4.6.

## Build Metrics Target

| Session | Scope | Est. impl lines | Est. tests |
|---------|-------|-----------------|-----------|
| 1 | Phase 1 (§4) | 800–1200 | ≥55 |
| 2 | Phase 2 (§5) | 600–900 | ≥40 |
| 3 | Phase 3 deterministic (§7.1) | 400–600 | ≥30 |
| 4 | Phase 3 LLM + consensus (§7.2–3) | 600–800 | ≥30 |
| 5 | Pipeline + writer + validation (§7.4) | 300–500 | ≥25 |
| 6 | Integration + cross-engine | — | ≥20 |

## Test Patterns

Follow normalization conventions:
- `conftest.py` factories for all complex types (ContentUnit, DivisionNode, NormalizedPackage)
- Real Arabic text from Shamela for domain tests; synthetic only for structural tests
- Regression baselines from `experiments/` directories (do NOT modify)
- Adversarial cases: ADV-E-01 through ADV-E-12 (§10.6)
- Error code tests verify: (a) code emitted, (b) message context, (c) recovery per §8.2

## Required Reading

1. `NEXT.md` or `session-1-plan.md` — current task
2. `SPEC.md` — relevant section only (do NOT read all 2387 lines)
3. `contracts.py` — type signatures
4. `engines/normalization/contracts.py` — upstream types consumed
5. `experiments/architecture_test/extract_divisions.py` — validated reference implementations
6. `docs/llm_trustworthiness_defenses.md` — **MANDATORY for Sessions 4–6.** Deterministic defenses against LLM judgment errors. Contains failure-mode matrix, Tier 1 defenses to build, and empirical scans to run before each session.

## Claude Code Behaviour Guidelines

- **Ownership, not deflection:** When you encounter an issue, take responsibility and work towards a solution. Don't say "not caused by my changes" or "pre-existing issue." Don't give up with "known limitation" or defer to "future work." Fix it now.
- **Persistence through obstacles:** Don't stop at the first problem. Don't declare "good stopping point" or "natural checkpoint." Keep pushing until you have a complete, verified solution.
- **Initiative over permission-seeking:** If you have the knowledge and capability to solve a problem, act. Don't ask "should I continue?" or "want me to keep going?" Take initiative and drive towards the solution.
- **Plan before acting:** For multi-step work, plan which files to read, in what order, which tools to use, and what the expected outcome is — before touching anything.
- **Convention recall:** Always re-read and apply project-specific conventions from CLAUDE.md files. Don't rely on memory of what they say.
- **Self-correction loops:** Catch your own mistakes by applying reasoning loops and self-checks. Fix errors before committing or asking for help.
- **Verify, don't assume:** After reaching a conclusion or making a change, verify it against the actual state of the codebase. A conclusion you haven't verified is a guess. Run the test, read the output, check the file.
- **Trace root causes:** When something fails, trace the full causal chain. Don't patch symptoms — find and fix the underlying cause. A surface fix hides the real bug for later.

### Tool Use

- **Research-first, never edit-first:** Before using any tool, research the context and requirements. Read the relevant code, SPEC, and contracts before making changes. Understand before you act.
- **Surgical edits over rewrites:** Make targeted, minimal changes. Never rewrite whole files or make large sweeping changes when a focused edit achieves the goal.
- **Reasoning loops are mandatory:** Apply reasoning loops frequently. Don't skip them to save tokens. The cost of a wrong action far exceeds the cost of thinking.

### Thinking Depth

- Always apply the **highest level of thinking depth**. Shallow thinking leads to the cheapest available action, which is rarely the correct one. Spending more tokens on reasoning produces dramatically better outcomes.
- **Never reason from assumptions.** Always reason from actual data — read and understand the actual code, SPEC, or documentation before making decisions. Assumptions compound into errors.
