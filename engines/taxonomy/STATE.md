# Taxonomy Engine — Current State (2026-03-31)

> **Read this file at the start of every taxonomy-related session.**
> It captures the full state of the taxonomy engine work as of commit `6674ef1c`.

## Session 2 blocker status

### Blocker 1: Code fixes — ✅ CLEARED

All 6 fixes (F-1, F-3, F-4, F-6, F-7, F-8) implemented by CC in commit `635cae0b`.
Reviewed and ACCEPTED by architect. 145 tests passing (baseline was 119).

### Blocker 2: Gate G3 — Tree validation — ⏳ SYNTHESIS IN PROGRESS

**All 4 researchers delivered.** Synthesis session handoff ready.

Researcher outputs (all in `reference/research/`):

| Researcher | Type | File | Leaves |
|---|---|---|---|
| ChatGPT Pro | Knowledge-based | `chatgpt_nahw_taxonomy.yaml` | 178 |
| Fresh Claude Opus | Knowledge-based | `claudechat_nahw_taxonomy.yaml` | 93 |
| CC (heading analysis) | Corpus-based (302 books) | `codex_nahw_corpus_tree.yaml` | 82 |
| Codex (content analysis) | Corpus-based (3 books deep) | `codex_nahw_content_analysis.md` | 587 max |

Additional data: `codex_nahw_topic_frequency.json`, `codex_nahw_corpus_gaps.md` (399 uncaptured topics), `chatgpt_nahw_justification_table.md`, `claude_nahw_topic_frequency.json`, heading/hierarchy/books JSONs.

**ChatGPT synthesis:** May or may not be in repo. The synthesis session handles both cases.

**Next action:** Start new Claude Chat session using handoff at `reference/handoffs/nahw_tree_synthesis_session.md`. The session produces the validated `nahw_v2_0` tree through an 11-step methodology.

## Downstream impacts (handle AFTER tree validation)

- **Gold baseline invalidated:** Must be regenerated against new tree.
- **Session 2 NEXT.md outdated:** `reference/archive/NEXT_taxonomy_session2_deferred.md` needs new tree refs.
- **Review probes stale:** `reference/archive/review_probes/taxonomy_session1_probes.py` references nonexistent modules.

## Key files

| File | Purpose |
|------|---------|
| `reference/handoffs/nahw_tree_synthesis_session.md` | **START HERE** — synthesis session handoff |
| `engines/taxonomy/SPEC.md` | Authoritative specification |
| `reference/GOVERNANCE.md` | Review team rules |
| `reference/research/` | All 4 researcher outputs + supporting data |
| `library/sciences/nahw/tree.yaml` | Current UNVALIDATED tree (to be replaced) |
| `library/sciences/taxonomy_registry.yaml` | Tree version registry |
