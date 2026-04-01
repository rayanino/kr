# Taxonomy Engine — Current State (2026-04-01)

> **Read this file at the start of every taxonomy-related session.**
> It captures the full state of the taxonomy engine work.

## Session 2 blocker status

### Blocker 1: Code fixes — ✅ CLEARED

All 6 fixes (F-1, F-3, F-4, F-6, F-7, F-8) implemented by CC in commit `635cae0b`.
Reviewed and ACCEPTED by architect. 145 tests passing (baseline was 119).

### Blocker 2: Gate G3 — Tree validation — ✅ CLEARED (2026-04-01)

**Nahw v2.0 validated and installed.** 183 leaves, 9 L1 branches, 56 L2 topics.

**Process completed:**
1. Phase 1 (architect synthesis): 146-leaf draft from 4-researcher inputs
2. Phase 2 (ChatGPT comparison): 173-leaf merged tree + 182-leaf independent synthesis
3. Phase 3 (Fresh Claude adversarial review): NOT READY verdict with 3 blocking findings
4. Finding resolution: 3 fixes applied (F-1 renames, F-3 metadata, F-5 new leaf)
5. Quality gates: ALL 14 gates PASS (M-1 through M-8, S-1 through S-6)
6. Post-validation: old tree archived, new tree installed, registry updated, tests pass (146)

**Decision log:**
- Base tree: ChatGPT's 182-leaf synthesis (NOT the 173-leaf comparison), because Fresh Claude reviewed it with 40+ tool calls
- F-1: 3 _nizaman leaves renamed using comparison tree's scholarly terms (web-verified)
- F-3: language/policy/id_policy metadata added from v1.0 (engine doesn't consume them yet; forward-compatible)
- F-5: law/lawla/lawma/amma leaf added (9/302 books in corpus; non-jazm conditionals were missing)
- F-2 (non-blocking): 2 single-child nodes documented as intentional structural choice

**Key files:**
- Active tree: `library/sciences/nahw/tree.yaml` (v2.0, 183 leaves)
- Archived tree: `library/sciences/nahw/tree_history/nahw_v1_0.yaml` (v1.0, 226 leaves)
- Final tree source: `reference/research/nahw_v2_0_final.yaml`
- Fresh Claude review: `reference/research/fresh_claude_nahw_review.md`
- ChatGPT synthesis: `reference/research/chatgpt_nahw_v2_synthesis.yaml`
- ChatGPT comparison: `reference/research/chatgpt_nahw_comparison.yaml`

## Session 2 — UNBLOCKED

Both blockers cleared. Session 2 (LLM placement engine build) can proceed.
The deferred NEXT.md is at `reference/archive/NEXT_taxonomy_session2_deferred.md` — needs updating with v2.0 tree references before use.

## Outstanding items

### Gold baseline — INVALID, needs regeneration

`engines/taxonomy/tests/fixtures/gold_baseline_nahw.yaml` references v1.0 leaf paths that don't exist in v2.0. CC must regenerate by running the placement engine on known excerpts against the new tree. Include in the Session 2 NEXT.md.

### Other 4 science trees — unvalidated

sarf (226 leaves), balagha (335 leaves), aqidah (30 leaves), imlaa (105 leaves) all need the same validation process. Follow `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`. Prioritize sarf (closest to nahw, likely the most structural work needed).

### Stale review artifacts

- `reference/archive/review_probes/taxonomy_session1_probes.py` references nonexistent modules
- `reference/archive/NEXT_taxonomy_session2_deferred.md` needs v2.0 tree refs

## Researcher outputs (all in `reference/research/`)

| Researcher | Type | File | Leaves |
|---|---|---|---|
| ChatGPT Pro | Knowledge-based | `chatgpt_nahw_taxonomy.yaml` | 178 |
| ChatGPT Pro | Independent synthesis | `chatgpt_nahw_v2_synthesis.yaml` | 182 |
| ChatGPT Pro | Comparison merge | `chatgpt_nahw_comparison.yaml` | 173 |
| Fresh Claude Opus | Knowledge-based | `claudechat_nahw_taxonomy.yaml` | 93 |
| Fresh Claude Opus | Adversarial review | `fresh_claude_nahw_review.md` | — |
| CC (heading analysis) | Corpus-based (302 books) | `codex_nahw_corpus_tree.yaml` | 82 |
| Codex (content analysis) | Corpus-based (3 books deep) | `codex_nahw_content_analysis.md` | 587 max |
| **Architect synthesis** | **Draft** | **`nahw_v2_0_draft.yaml`** | **146** |
| **Final (validated)** | **Installed** | **`nahw_v2_0_final.yaml`** | **183** |

## Test state

146 tests passing. Tests updated to reference v2.0 tree structure:
- `test_tree_loader.py`: version, leaf count, known paths updated
- `test_validator.py`: valid/branch paths updated
- `test_routing.py`: nahw now skips Stage 1 (183 <= 200); balagha used for large-tree test
- `conftest.py`: docstring updated

## Key files

| File | Purpose |
|------|---------|
| `reference/protocols/TAXONOMY_TREE_PROTOCOL.md` | **GOVERNING** — mandatory process for all tree validation |
| `library/sciences/nahw/tree.yaml` | Active validated nahw tree (v2.0, 183 leaves) |
| `library/sciences/taxonomy_registry.yaml` | Tree version registry |
| `engines/taxonomy/SPEC.md` | Authoritative specification |
| `reference/GOVERNANCE.md` | Review team rules |
