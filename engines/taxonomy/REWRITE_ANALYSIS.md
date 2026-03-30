# Taxonomy Engine — Pre-Rewrite Analysis

**Date:** 2026-03-30
**Purpose:** Empirical findings and design decisions that feed the core SPEC rewrite.
**Evidence basis:** 67 real excerpts from 5 books, 5 science trees (922 leaves), existing SPEC + contracts.

---

## 1. Empirical Findings from Real Data

### 1.1 Excerpt Distribution by Placement Difficulty

| Category | Count | Books | Challenge |
|----------|-------|-------|-----------|
| Clear nahw content | 25 | ibn_aqil_v3 | Easy — topics like "حروف الجر" map directly to nahw leaves |
| Editorial/introductory | 15 | ibn_aqil_v1 (7), ext_39_masala (2), ext_46_qa (3), taysir (1) | No natural leaf — these are ABOUT the book, not about a science topic |
| Usul al-nahw content | 12 | ext_46_qa | Borderline — meta-nahw (methodology of grammar) with some placeable topics |
| Fiqh content (no tree) | 14 | ext_39_masala (14) | UNPLACEABLE — janaza/wasiyya rules have no tree in the 5 sciences |
| Hadith/fiqh content (no tree) | 5 | taysir (5) | UNPLACEABLE — niyyah/taharah content has no tree |
| Structural transitions | ~4 | mixed | Borderline — chapter headers, structural markers |

**Key finding:** ~28% of the test excerpts (19/67) cannot be placed in ANY existing tree because they belong to sciences (fiqh, hadith) that don't have trees yet. The taxonomy engine MUST handle this gracefully.

### 1.2 Tree Format Inconsistency (BLOCKING)

| Science | Format | Leaf Count |
|---------|--------|------------|
| nahw | `taxonomy→nodes` (id/title/children/leaf) | 226 |
| sarf | `taxonomy→nodes` (id/title/children/leaf) | 226 |
| balagha | `taxonomy→nodes` (id/title/children/leaf) | 335 |
| imlaa | `taxonomy→nodes` (id/title/children/leaf) | 105 |
| **aqidah** | **Nested dict** (`_label`/`_leaf`) | **30** |

**The aqidah tree uses a completely different YAML schema.** The taxonomy engine must parse tree files. Supporting two formats adds unnecessary complexity.

**Decision:** Convert aqidah to the standard format as a pre-build task. The taxonomy engine reads ONE format only.

### 1.3 Nahw Tree Structure for Hierarchical Search

The nahw tree has 12 top-level branches with 3–50 leaves each:

| Branch | Title | Leaves |
|--------|-------|--------|
| muqaddimat | مقدمات علم النحو | 34 |
| ali3rab_walbina | الإعراب والبناء | 15 |
| alasmaa | مباحث الاسم | 27 |
| alaf3al | مباحث الفعل | 30 |
| almarfu3at | المرفوعات | 15 |
| almansubat | المنصوبات | 50 |
| almajrurat | المجرورات | 10 |
| attawabi3 | التوابع | 16 |
| masail_al3amil | مسائل العامل | 3 |
| annawasiikh | النواسخ | 17 |
| aljumal_walmawaqi3 | الجمل ومواقعها | 4 |
| asaleeb | أساليب ومسائل جامعة | 5 |

For hierarchical search: Stage 1 picks 3 branches → Stage 2 searches leaves within each. The branch titles are distinctive enough for an LLM to route correctly.

### 1.4 Leaf Clustering Pattern

All 20 ibn_aqil_v3 "rule_statement" excerpts about huruf al-jarr would go to the same branch (`almajrurat/huruf_aljar`) with only 4 leaves. Most would cluster at `ma3ani_huruf_aljar` (individual preposition meanings). This is correct behavior — the leaf IS the right topic. The high concentration would trigger a leaf-capacity diagnostic (deferred) suggesting future tree evolution.

### 1.5 Actual Excerpt Fields Available for Placement

From the real data, the taxonomy engine has these fields to work with:

**Primary placement inputs:**
- `excerpt_topic`: list[str] — e.g. `["حروف الجر", "تعداد حروف الجر"]`
- `description_arabic`: str — detailed Arabic description
- `primary_text`: str — full excerpt text

**Supporting context:**
- `primary_function`: str — e.g. "rule_statement", "editorial_note"
- `content_types`: list[str] — e.g. ["rule_statement", "evidence_hadith"]
- `terminology_variants`: list[dict] — variant terms
- `div_path`: list[str] — structural heading path in the source book

**NOT available (confirming contract gap):**
- No `science_id` on excerpts
- No `proposed_leaf`
- No `lifecycle_stage`
- No `passage_id` or `atom_ids`

---

## 2. Design Decisions for Core v1

### D-TAX-001: Science Assignment Mechanism

**Decision:** science_id is a REQUIRED parameter to the taxonomy engine's run configuration, NOT a per-excerpt field. The operator specifies which science a batch of excerpts belongs to.

**Reasoning:**
- No source registry with science metadata exists yet
- The excerpting engine doesn't produce science_id
- For v1 with 5 books, the owner knows which science each book covers
- Automated science classification is a separate capability (deferred)

**Format:** Run config specifies `science_id: "nahw"` and the taxonomy engine processes all excerpts in the batch against the nahw tree.

**Edge case — wrong science assignment:** If the operator assigns the wrong science (e.g., runs fiqh excerpts against nahw), most excerpts will score below 0.5 and become TAX_UNPLACEABLE. The engine logs a batch-level warning if >50% of excerpts are unplaceable.

### D-TAX-002: Editorial/Introductory Excerpt Handling

**Decision:** No special-case handling. The placement algorithm runs on ALL excerpts regardless of `primary_function`. If the LLM can find a leaf with confidence ≥0.5, it gets placed. If not, TAX_UNPLACEABLE.

**Reasoning:**
- Some editorial excerpts ARE placeable: "ترجمة ابن مالك" could go under muqaddimat
- Some are genuinely unplaceable: "مقدمة الطبعة الثانية" is about the book, not the science
- Letting the LLM decide is more robust than hard-coded function filters
- The evaluation phase will reveal if editorial excerpts cause systematic problems

**Risk:** The LLM might hallucinate a match for an editorial excerpt, placing it at a topically wrong leaf with moderate confidence. Mitigation: `primary_function` is included in the placement context, giving the LLM information to make good judgments.

### D-TAX-003: Unplaceable Excerpt Storage

**Decision:** Unplaceable excerpts are written to `library/sciences/{science_id}/unplaced/{excerpt_id}.json` with full original data plus:
- `lifecycle_stage`: "unplaced"
- `unplaced_reason`: str (e.g., "No candidate scored ≥0.5")
- `best_candidates`: list of top 3 candidates with scores

**Reasoning:**
- Must never silently drop data (Knowledge Integrity Axiom)
- Must be visible and auditable
- Must be relocatable when trees evolve or correct science is assigned
- File-per-excerpt matches the placed excerpt storage pattern

### D-TAX-004: Tree Format Standardization (PREREQUISITE)

**Decision:** All 5 trees must use the standard `taxonomy→nodes` format (id/title/children/leaf) before the taxonomy engine runs. The aqidah tree must be converted.

**Reasoning:**
- Supporting two formats adds parser complexity with zero benefit
- 4 of 5 trees already use the standard format
- Conversion is a one-time mechanical task
- The taxonomy engine should have ONE code path for tree parsing

**Action:** Add aqidah conversion to build prep as a prerequisite task for CC.

**TRAP:** The aqidah v0 format uses `_label` and `_leaf` as metadata keys (prefixed with single `_`). But it also has `__overview` nodes (double underscore) that are REAL leaf nodes, not metadata. A naive converter that skips all `_`-prefixed keys will lose 2 leaves (28 instead of 30). The converter must only skip the specific metadata keys `_label` and `_leaf`, not all underscore-prefixed keys. Verified: grep finds 30 `_leaf: true`, correct count is 30.

### D-TAX-005: Hierarchical Search Threshold

**Decision:** Trees with >100 leaves use hierarchical search (branch-first, then leaf). Trees with ≤100 leaves show all leaves to the LLM directly.

**Changed from SPEC's 200 threshold.** Reasoning:
- Even 150 leaves in a single prompt is a lot of context for accurate matching
- imlaa (105) is close to the boundary — best to show it directly
- aqidah (30) definitely gets direct matching
- The penalty for hierarchical search on medium trees is one extra LLM call, which is low cost

**Hierarchical search process:**
1. Show the LLM the branch-level view (top-level nodes with first-level children)
2. LLM picks top 3 branches
3. Show all leaves within those 3 branches
4. LLM picks top 3-5 candidate leaves

### D-TAX-006: Input Format

**Decision:** The taxonomy engine reads excerpts as JSONL files — one JSON object per line, matching the excerpting engine's output format. No wrapper object.

**Reasoning:**
- The excerpting engine outputs `excerpts.jsonl`
- The tracer's ExcerptStream wrapper doesn't match the real data
- JSONL is streamable (can process line-by-line) which matters for large batches

### D-TAX-007: Output Format — File-per-Excerpt

**Decision:** Placed excerpts are written as individual JSON files at `library/sciences/{science_id}/content/{leaf_path}/excerpts/{excerpt_id}.json`.

**Reasoning:**
- Makes individual excerpt inspection trivial
- Enables future relocation by file move
- Matches the reference taxonomy's directory-as-tree pattern
- Trade-off: many small files, but for v1 scale (hundreds, not millions) this is fine

### D-TAX-008: LLM Routing via CLI Adapter

**Decision:** Use the existing CLI adapter (shared/llm/) for all LLM calls. Don't specify a model name in the SPEC — specify capability requirements.

**Reasoning:**
- The CLI adapter handles authentication, retries, encoding, and model routing
- The adapter was hardened across multiple sessions with 45 tests
- Model choice (Opus vs Sonnet) can be tuned later based on placement accuracy
- For v1, use Opus (per project axiom: always use the best model)

### D-TAX-009: Placement Confidence Thresholds

**Decision:** Keep the SPEC's three-tier system:
- ≥0.8: auto-place (logged for future review)
- 0.5–0.79: auto-place but flagged as low-confidence (prominent in logs)
- <0.5: TAX_UNPLACEABLE

**Changed from SPEC:** The 0.5–0.8 range no longer escalates to human gate (deferred). Instead, it auto-places with a low_confidence flag. The evaluation phase serves as the human review for v1.

**Reasoning:**
- Human gate infrastructure is deferred
- The evaluation phase (owner reviews real output) IS the quality gate
- Logging confidence enables post-hoc filtering: "show me all placements with confidence <0.8"

### D-TAX-010: Provenance Preservation (D-023)

**Decision:** The placed excerpt JSON contains ALL fields from the original excerpt, plus the taxonomy-added fields. The taxonomy engine copies the entire excerpt object and adds fields — it never selects a subset.

**Reasoning:**
- Knowledge Integrity Axiom: stripping any upstream field is a provenance loss
- Simple to implement: `{**original_excerpt, **placement_additions}`
- Downstream engines may need any field

### D-TAX-011: Taxonomy Version Recording

**Decision:** Every placed excerpt records `taxonomy_version_at_placement` even though the tree is static for v1.

**Reasoning:**
- Extension hook for tree evolution
- When evolution is added later, existing placements can be audited against the tree version
- Trivial to implement (read from tree YAML header or registry)
- Omitting it now would require backfilling later

### D-TAX-012: Batch-Level Diagnostics

**Decision:** After processing a batch, the taxonomy engine writes a batch report with:
- Total excerpts processed
- Placed count (with confidence distribution)
- Unplaced count
- Leaf distribution (how many excerpts per leaf)
- Warning if >50% unplaced (possible wrong science)
- Warning if any leaf has >20 excerpts (possible granularity issue)

**Reasoning:**
- Gives the operator/evaluator a quick quality signal
- Catches systematic problems (wrong science, tree gaps) early
- Cheap to compute after placement

---

## 3. Placement Algorithm — Detailed Design

### Stage 1: Candidate Generation (Branch Selection for Large Trees)

**Input to LLM:**
```
You are placing an Arabic Islamic scholarly excerpt into a science tree.

Science: {science_display_name}
Excerpt topic: {excerpt_topic joined by ' / '}
Excerpt description: {description_arabic}
Excerpt type: {primary_function}

Here are the top-level branches of the {science_display_name} tree.
Each branch is shown with its immediate children for context.

{formatted branch list with children}

Which 3 branches are most likely to contain the correct leaf for this excerpt?
Return ONLY the branch IDs, ranked by likelihood.
```

**Output format:** Structured — list of 3 branch IDs.

For trees with ≤100 leaves, skip this stage — go directly to Stage 2 with all leaves.

### Stage 2: Candidate Ranking (Leaf Selection)

**Input to LLM:**
```
You are placing an Arabic Islamic scholarly excerpt at the correct leaf.

Excerpt topic: {excerpt_topic joined by ' / '}
Excerpt description: {description_arabic}
Excerpt text (first 500 chars): {primary_text[:500]}
Excerpt type: {primary_function}
Content types: {content_types}

Candidate leaves:
{for each leaf in candidate branches:}
  - ID: {leaf_id}
    Title: {leaf_title}
    Parent: {parent_branch_title}
    Path: {full path from root}

For each candidate leaf, score how well this excerpt fits (0.0-1.0) and explain why.
Consider:
1. Does the excerpt's teaching content match the leaf's declared topic?
2. Is there a more specific leaf that would be a better fit?
3. Is the leaf too general or too specific for this excerpt?

If NO candidate fits well (all scores <0.5), say so — the excerpt may not belong in this science tree.
```

**Output format:** Structured — list of {leaf_id, score, reasoning} objects.

### Key Design Note: What the LLM Does NOT See

The LLM does NOT see:
- Existing excerpts at candidate leaves (no "neighbor" context for v1 — would require pre-loading placed excerpts)
- The full tree structure (only relevant branches/leaves)
- Other excerpts in the same batch (no batch-awareness)

These are all extension points. Neighbor context improves accuracy but requires reading existing placed files. Batch awareness could detect that 20 excerpts all want the same leaf. Both are deferred.

---

## 4. Risks and Mitigations

### Risk 1: LLM Misclassification of Arabic Scholarly Terminology

The LLM might not understand that "معاني مِن" is about the preposition مِن specifically, not about meanings in general.

**Mitigation:** The `description_arabic` field provides rich context. For the مِن example: "بيان معاني حرف الجر مِن وهي ابتداء الغاية والتبعيض وبيان الجنس مع شواهد" — this explicitly says "the meanings of the preposition مِن."

**Severity if fails:** Medium — excerpt goes to a neighboring leaf (still in the right branch), not catastrophically wrong.

### Risk 2: Systematic Bias Toward Broad Leaves

The LLM might consistently prefer broader leaves (e.g., `huruf_aljar__overview`) over specific ones (e.g., `ma3ani_huruf_aljar`) because the broad leaf title seems to "contain" more topics.

**Mitigation:** The ranking prompt explicitly asks "is there a MORE SPECIFIC leaf?" This nudges the LLM toward precision. The gold baseline test (§10.2 in SPEC) specifically checks for this pattern.

### Risk 3: Editorial Excerpts Placed at Weakly Matching Leaves

An excerpt about "مقدمة الطبعة الثانية" might get placed at a muqaddimat leaf with confidence 0.55, which is technically above the 0.5 threshold but meaningfully wrong.

**Mitigation:** The `primary_function: editorial_note` is visible to the LLM, and the prompt asks about "teaching content" — editorial notes don't teach a specific topic. If the LLM correctly interprets this, it will score low. If not, the evaluation phase catches it.

### Risk 4: Token Limit on Large Branch Sets

For balagha (335 leaves), even with hierarchical search, the 3 selected branches could have 70+ leaves each (3ilm_alma3ani has 129 leaves). That's a lot of context for Stage 2.

**Mitigation:** If a selected branch has >50 leaves, do a second round of hierarchical search within the branch (sub-branch selection). This adds one more LLM call but keeps context windows manageable. Only balagha's 3ilm_alma3ani triggers this.

---

## 5. Pre-Build Prerequisites

Before CC starts building:

1. **Convert aqidah tree** to standard format (taxonomy→nodes with id/title/children/leaf)
2. **Verify tree integrity** — every tree file parses, leaf counts match registry
3. **Create gold baseline** — manually place 10-15 excerpts from ibn_aqil_v3 to validate placement accuracy
4. **Verify CLI adapter works** for structured output extraction
5. **Create test fixtures** — mock excerpts with known correct placements
