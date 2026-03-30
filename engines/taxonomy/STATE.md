# Taxonomy Engine — Current State (2026-03-30)

> **Read this file at the start of every taxonomy-related session.**
> It captures the full state of the taxonomy engine work as of commit `3447a24c`.

## Session 2 blocker status

### Blocker 1: Code fixes — ✅ CLEARED

All 6 fixes (F-1, F-3, F-4, F-6, F-7, F-8) implemented by CC in commit `635cae0b`.
Reviewed and ACCEPTED by architect. 145 tests passing (baseline was 119).

- **F-6:** `classify_excerpt_type` now defaults unknown `primary_function` to EDITORIAL. Explicit `_TEACHING_FUNCTIONS` frozenset matches ScholarlyFunction enum.
- **F-1:** `_EXPECTED_FIELDS` has 8 entries matching SPEC §2.1. Field-check distinguishes absent (warn) vs null (no warn).
- **F-4:** `compute_editorial_placement_rate` uses `classify_excerpt_type` — null/missing correctly counted as editorial.
- **F-3:** `test_real_data.py` created with 4 tests using `real_excerpts` fixture.
- **F-7:** `_read_excerpts` uses `encoding="utf-8-sig"` — BOM handled transparently.
- **F-8:** Duplicate `excerpt_id` logs `TAX_DUPLICATE_EXCERPT_ID` warning. Last-write-wins per directive.

### Blocker 2: Gate G3 — Tree validation — ⏳ SYNTHESIS PENDING

The 4-researcher investigation is complete. Synthesis remains.

**What's done:**
- Aspects 1-8 research complete (Aspects 1-4 in previous session, 5-8 in this session)
- 4 independent researchers commissioned (2 knowledge-based, 2 corpus-based)
- Corpus-based results IN REPO: `reference/research/` (CC + Codex)
- Knowledge-based results PENDING: ChatGPT Pro and Fresh Claude Opus (owner relaying)

**What's next:**
1. Save ChatGPT and Fresh Claude outputs to `reference/research/`
2. Fire ChatGPT Pro synthesis prompt (comparing all 4 trees)
3. Save synthesis to `reference/research/`
4. NEW CHAT: architect reviews synthesis, review team validates
5. Commit validated tree as `library/sciences/nahw/tree.yaml` (v2.0)

## 4-researcher methodology (Aspects 5-8)

### Research design (Aspect 5)

Two evidence streams, each with two independent researchers:

| | Knowledge-based | Corpus-based |
|---|---|---|
| **Provider A** | Fresh Claude Opus (Research mode) | CC (local filesystem) |
| **Provider B** | ChatGPT Pro (Deep Research) | Codex CLI (local filesystem) |

Knowledge-based researchers build trees from canonical texts (Alfiyyah, shuruh, modern references). Corpus-based researchers build trees from actual book headings and content in `shamela_export_samples/`. None see the current `tree.yaml`.

Cross-stream convergence (knowledge + corpus agree) is the gold signal.

### Corpus research results (in repo)

**CC (commit 3447a24c):**
- 302 nahw books identified in `shamela_export_samples/`
- 70,001 headings extracted
- 462 unique topics in 5+ books, 175 in 10+ books
- Corpus-derived tree: 82 leaves (but 399 topics in 5+ books NOT captured)
- Files: `reference/research/nahw_books_identified.json`, `nahw_headings_by_book.json`, `nahw_topic_frequency.json`, `nahw_corpus_tree.yaml`, `nahw_corpus_gaps.md`
- Scripts: `scripts/nahw_research/step1-6`
- CC respected FORBIDDEN rules (verified: no references to existing tree.yaml)

**Codex (commit 3447a24c):**
- Deep analysis of 3 largest books: شرح المفصل لابن يعيش (970 headings, 10MB), النحو الوافي (193 headings, 9MB), ضياء السالك (187 headings, 5.5MB)
- Sub-topic analysis within major chapters with evidence quotes
- 587 potential leaves at maximum granularity
- Average 4.52 sub-topics per chapter
- File: `reference/research/nahw_content_analysis.md`

### Synthesis process (Aspect 7)

Three-phase synthesis led by ChatGPT Pro + architect review:
1. **Branch alignment:** Map Level-1 branches across all 4 trees
2. **Leaf comparison:** Cross-stream scoring matrix (knowledge x corpus)
3. **Review team validation:** ChatGPT synthesizes, Fresh Claude cold-reads, architect reviews

### Sequencing (Aspect 8)

- Nahw first (most data, strongest canonical framework)
- Other sciences follow: sarf → balagha → aqidah → imlaa
- Tree v2.0 is source-validated; v2.1+ refined empirically after excerpt placement

## Downstream impacts (handle AFTER tree validation)

- **Gold baseline invalidated:** 12-excerpt gold baseline assigned against unvalidated tree. Must be redone after v2.0.
- **Session 2 NEXT.md outdated:** `reference/archive/NEXT_taxonomy_session2_deferred.md` references old tree. Must update after v2.0.
- **Review probes stale:** `reference/archive/review_probes/taxonomy_session1_probes.py` references nonexistent modules.

## Key files

| File | Purpose |
|------|---------|
| `engines/taxonomy/SPEC.md` | Authoritative specification |
| `reference/ENGINE_FACTORY_PLAN.md` lines 836-912 | Gate G3 definition |
| `reference/archive/NEXT_taxonomy_session2_deferred.md` | Preserved Session 2 NEXT.md (blocked by G3) |
| `reference/archive/sessions/reviews/review_taxonomy_session1.md` | Session 1 review checklist |
| `library/sciences/taxonomy_registry.yaml` | Tree version registry |
| `library/sciences/nahw/tree.yaml` | Current nahw tree (226 leaves, UNVALIDATED — to be replaced by v2.0) |
| `reference/research/nahw_corpus_tree.yaml` | CC's corpus-derived tree (82 leaves) |
| `reference/research/nahw_content_analysis.md` | Codex's deep content analysis |
| `reference/research/nahw_topic_frequency.json` | CC's topic frequency data (302 books) |
| `reference/research/nahw_corpus_gaps.md` | CC's gap analysis |
