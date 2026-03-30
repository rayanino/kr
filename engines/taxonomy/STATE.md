# Taxonomy Engine — Current State (2026-03-30)

> **Read this file at the start of every taxonomy-related session.**
> It captures the full state of the taxonomy engine work as of commit `eeb5cb38`.

## Two blockers before Session 2 (LLM placement)

### Blocker 1: Code fixes (F-1, F-3, F-4, F-6)

Session 1 code review found 6 issues. Fix directive is at `NEXT.md`.
- **F-6 (CRITICAL):** `classify_excerpt_type` in `placer.py` treats unrecognized `primary_function` as TEACHING (threshold 0.80) instead of EDITORIAL (threshold 0.85). SPEC §4.A.3 says "not recognized → editorial." Upstream excerpting enum has `UNCLASSIFIED = "unclassified"` which triggers this.
- **F-1:** `_EXPECTED_FIELDS` in `engine.py` has 4/8 SPEC §2.1 fields.
- **F-4:** `compute_editorial_placement_rate` in `diagnostics.py` only counts `editorial_note`, not all editorial-classified excerpts.
- **F-3:** `test_real_data.py` missing; `real_excerpts` fixture orphaned.
- **F-7:** BOM-encoded JSONL files silently drop first excerpt (`encoding="utf-8"` → should be `"utf-8-sig"`).
- **F-8:** Duplicate `excerpt_id` silently overwrites output files with no warning.

**Status:** Fix directive ready at `NEXT.md`. Relay to CC.
**Review:** `reference/archive/sessions/reviews/review_taxonomy_session1.md`
**Providers who reviewed:** Architect, CC, ChatGPT Pro (deep research), Codex CLI.
**Test baseline:** 119 tests passing. After fixes: expect ≥127.

### Blocker 2: Gate G3 — Tree validation (NEVER EXECUTED)

`reference/ENGINE_FACTORY_PLAN.md` line 836:
> "The 5 existing tree.yaml files in library/sciences/ were created without owner validation. The nahw tree must be generated via multi-source AI research and owner-validated before taxonomy Step 3."

Gate G3 (line 912): "Before Taxonomy Step 3 | Oracle generates nahw tree via multi-source research | Owner confirms"

**Session 2 IS Step 3.** Gate G3 was planned during the atomization engine build (which was deferred). It was never executed.

**Status:** Deep research in progress — see § Tree Research below.

## Tree research — completed analysis (Aspects 1-4)

A thorough investigation was conducted in the review session. Key findings:

### Aspect 1: Provenance of existing trees
- All 5 trees originated in the ABD codebase (pre-KR migration, commit `7edc53b2`)
- No documentation of creation methodology exists
- Registry notes them as "Base superset taxonomy (granular, placement-safe)" — engineered for coverage, not scholarly accuracy
- Nahw and sarf both have exactly 226 leaves (suspicious — different sciences)
- Nahw tree has never been refined (v1_0 only), unlike aqidah (v0_1→v0_2 from الواسطية processing)

### Aspect 2: Sources of authority
Ground truth sources, ranked by relevance:
1. **The books themselves** — internal chapter structures (أبواب) are expert-authored taxonomies. Already extracted as `div_path` by normalization engine.
2. **Canonical organizational texts per science:**
   - Nahw: ألفية ابن مالك (~80 أبواب, standard for 750 years)
   - Balagha: تلخيص المفتاح of القزويني (معاني/بيان/بديع three-part division)
   - Aqidah: Multiple traditions (الواسطية for Hanbali, الطحاوية for Hanafi)
   - Sarf: شذا العرف في فن الصرف, also Alfiyyah sarf sections
   - Imlaa: Various treatises, less standardized
3. OpenITI/KITAB, Shamela classification — useful at book level, not sub-topic level

### Aspect 3: Corpus analysis
- Only 67 excerpts processed (5 books), of which only 25 are nahw (one chapter: حروف الجر)
- 0.4% coverage of the 226-leaf nahw tree
- Books use flat chapter headings (`div_path: "حروف الجر"`); tree sub-classifies into 4 leaves
- The current tree uses encyclopedic organization (group by grammatical case) not the Alfiyyah's pedagogical sequence
- Gold baseline (12 excerpts) was assigned by architect, marked PENDING owner validation

### Aspect 4: Evaluation criteria (proposed)
Hard requirements: scholarly terminology correctness, no fabricated divisions, leaf scope distinctness, no orphan branches, corpus viability.
Quality metrics: placement accuracy, excerpt distribution, canonical alignment, depth uniformity, LLM disambiguability.
Key design decision: tree should be **encyclopedic in structure** with **pedagogical navigation as metadata** (`study_order` field).

### Remaining aspects (not yet analyzed)
5. Research methodology (how to structure the actual tree investigation)
6. Prompt design (what to tell each researcher)
7. Synthesis process (how to combine findings)
8. Sequencing (when this happens relative to the engine build)

## Key files

| File | Purpose |
|------|---------|
| `NEXT.md` | Fix directive for CC (F-1/F-3/F-4/F-6) |
| `reference/archive/NEXT_taxonomy_session2_deferred.md` | Preserved Session 2 NEXT.md (blocked by G3 + fixes) |
| `reference/archive/sessions/reviews/review_taxonomy_session1.md` | Filled review checklist |
| `reference/ENGINE_FACTORY_PLAN.md` lines 836-912 | Gate G3 definition |
| `engines/taxonomy/SPEC.md` | Authoritative specification |
| `engines/taxonomy/src/placer.py` | Contains F-6 bug (classify_excerpt_type) |
| `engines/taxonomy/src/engine.py` | Contains F-1 bug (_EXPECTED_FIELDS) |
| `engines/taxonomy/src/diagnostics.py` | Contains F-4 bug (editorial rate) |
| `library/sciences/taxonomy_registry.yaml` | Tree version registry |
| `library/sciences/nahw/tree.yaml` | Nahw tree (226 leaves, unvalidated) |
| `reference/archive/review_probes/taxonomy_session1_probes.py` | Pre-written probes (stale module refs) |
