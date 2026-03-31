# Taxonomy Engine — Current State (2026-03-31)

> **Read this file at the start of every taxonomy-related session.**
> It captures the full state of the taxonomy engine work as of commit `97747d00`.

## Session 2 blocker status

### Blocker 1: Code fixes — ✅ CLEARED

All 6 fixes (F-1, F-3, F-4, F-6, F-7, F-8) implemented by CC in commit `635cae0b`.
Reviewed and ACCEPTED by architect. 145 tests passing (baseline was 119).

### Blocker 2: Gate G3 — Tree validation — ⏳ MERGE IN PROGRESS

**Phase 1 (architect synthesis) COMPLETE.** Draft tree at `reference/research/nahw_v2_0_draft.yaml` — 146 leaves, 9 branches, functional grouping. Produced via 11-step methodology with cross-stream confidence scoring. All supporting artifacts committed:
- `reference/research/nahw_v2_leaf_inventory.md` — per-leaf reasoning and confidence ratings
- `reference/research/nahw_v2_0_draft.yaml` — the draft YAML tree

**ChatGPT Pro independent synthesis:** Was given a 24-step parallel synthesis prompt (`reference/research/chatgpt_synthesis_prompt.md`). May or may not be complete. Owner will paste output when ready.

**Prompts hardened (commit `9f6a7432`):** Both merge-process prompts were rewritten in a fresh session after adversarial analysis found 10 significant gaps in each:
- `reference/research/chatgpt_comparison_prompt.md` — for ChatGPT to compare both trees
- `reference/research/fresh_claude_review_prompt.md` — for Fresh Claude adversarial review

**Taxonomy Tree Protocol written (commit `97747d00`):** Permanent governance doc at `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`. Covers the entire 4-researcher → 3-phase merge → quality gates process. Will be reused for the remaining 4 sciences.

### Remaining steps to clear G3 (exact sequence)

The NEXT session that handles the merge must follow this sequence:

1. **Check if ChatGPT's synthesis is available.** If yes, proceed. If not, wait — the dual-provider merge requires both trees.

2. **Fire the comparison prompt.** In the SAME ChatGPT conversation (so it retains synthesis context), paste the text of `reference/research/chatgpt_comparison_prompt.md`. ChatGPT's regular chat mode cannot access the repo, so **upload these 5 files** alongside the prompt:
   - `reference/research/nahw_v2_0_draft.yaml` (the architect's draft tree)
   - `reference/research/nahw_v2_leaf_inventory.md` (per-leaf reasoning)
   - `reference/research/codex_nahw_topic_frequency.json` (302-book corpus frequency)
   - `reference/research/codex_nahw_corpus_gaps.md` (399 uncaptured topics)
   - `reference/research/codex_nahw_content_analysis.md` (sub-topic analysis)
   
   Say "continue" after each of ChatGPT's 8 steps. ChatGPT produces a merged recommended tree.

3. **Fire the review prompt.** Open a NEW Fresh Claude Opus chat. Paste `reference/research/fresh_claude_review_prompt.md` with the merged tree from step 2. Fresh Claude conducts 8 adversarial checks and delivers READY/NOT READY.

4. **If READY:** The architect (in a fresh session) incorporates any minor findings, runs all quality gates from `reference/protocols/TAXONOMY_TREE_PROTOCOL.md` §9, then executes post-validation steps from §11 (archive old tree, install new tree, update registry, flag gold baseline for regeneration, run regression tests).

5. **If NOT READY:** Fix all blocking findings. Re-run Phase 3 with a NEW Fresh Claude instance (the original has lost its "fresh eyes" advantage). Repeat until READY.

6. **Commit:** `taxonomy: validated nahw tree v2.0 (4-researcher synthesis, 302 books)`

7. **Update this file:** Mark G3 as CLEARED. Update downstream impacts section.

### Researcher outputs (all in `reference/research/`)

| Researcher | Type | File | Leaves |
|---|---|---|---|
| ChatGPT Pro | Knowledge-based | `chatgpt_nahw_taxonomy.yaml` | 178 |
| Fresh Claude Opus | Knowledge-based | `claudechat_nahw_taxonomy.yaml` | 93 |
| CC (heading analysis) | Corpus-based (302 books) | `codex_nahw_corpus_tree.yaml` | 82 |
| Codex (content analysis) | Corpus-based (3 books deep) | `codex_nahw_content_analysis.md` | 587 max |
| **Architect synthesis** | **Merged draft** | **`nahw_v2_0_draft.yaml`** | **146** |

Additional data: `codex_nahw_topic_frequency.json`, `codex_nahw_corpus_gaps.md` (399 uncaptured topics), `chatgpt_nahw_justification_table.md`, `claude_nahw_topic_frequency.json`, heading/hierarchy/books JSONs.

## Downstream impacts (handle AFTER G3 clears)

- **Gold baseline invalidated:** Must be regenerated against new tree. Create CC task.
- **Session 2 NEXT.md outdated:** `reference/archive/NEXT_taxonomy_session2_deferred.md` needs new tree refs.
- **Review probes stale:** `reference/archive/review_probes/taxonomy_session1_probes.py` references nonexistent modules.
- **Other 4 science trees unvalidated:** sarf (226 leaves), balagha (335 leaves), aqidah (30 leaves), imlaa (105 leaves) all need the same validation process. Follow `reference/protocols/TAXONOMY_TREE_PROTOCOL.md`.

## Key files

| File | Purpose |
|------|---------|
| `reference/protocols/TAXONOMY_TREE_PROTOCOL.md` | **GOVERNANCE** — mandatory process for all tree validation |
| `reference/research/chatgpt_comparison_prompt.md` | Hardened prompt for Phase 2 (ChatGPT comparison) |
| `reference/research/fresh_claude_review_prompt.md` | Hardened prompt for Phase 3 (Fresh Claude review) |
| `reference/research/nahw_v2_0_draft.yaml` | Architect's draft tree (Phase 1 output) |
| `reference/research/nahw_v2_leaf_inventory.md` | Per-leaf reasoning for the draft |
| `reference/handoffs/nahw_tree_synthesis_session.md` | Original synthesis methodology (historical — protocol supersedes) |
| `engines/taxonomy/SPEC.md` | Authoritative specification |
| `reference/GOVERNANCE.md` | Review team rules |
| `library/sciences/nahw/tree.yaml` | Current UNVALIDATED tree (to be replaced) |
| `library/sciences/taxonomy_registry.yaml` | Tree version registry |
