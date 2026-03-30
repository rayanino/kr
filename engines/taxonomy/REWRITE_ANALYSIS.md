# Taxonomy Engine — Pre-Rewrite Analysis

> **⚠️ SUPERSEDED:** The authoritative specification is now `engines/taxonomy/SPEC.md`.
> This document preserves the empirical analysis and original reasoning. Some decisions
> below were revised after two ChatGPT adversarial reviews. Where this document
> contradicts the SPEC, **the SPEC wins**. Key changes:
> - D-TAX-004: changed from "convert aqidah file" to "runtime normalization" (SPEC §4.A.1)
> - D-TAX-005: threshold reverted from 100 to 200 (SPEC §4.A.2)
> - D-TAX-009: staging gate added — 0.5-0.79 goes to staged/, not live (SPEC §4.A.3)
> - D-TAX-002: type split — cross_reference/structural_transition always staged (SPEC §4.A.3)

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

### D-TAX-003: Unplaceable Excerpt Storage ⚠️ REVISED in §6.2 — now four-category routing

**Decision:** Unplaceable excerpts are written to `library/sciences/{science_id}/unplaced/{excerpt_id}.json` with full original data plus:
- `lifecycle_stage`: "unplaced"
- `unplaced_reason`: str (e.g., "No candidate scored ≥0.5")
- `best_candidates`: list of top 3 candidates with scores

**Reasoning:**
- Must never silently drop data (Knowledge Integrity Axiom)
- Must be visible and auditable
- Must be relocatable when trees evolve or correct science is assigned
- File-per-excerpt matches the placed excerpt storage pattern

**Post-ChatGPT revision:** Now four categories — see §6.2 D-TAX-003 (REVISED).

### D-TAX-004: Tree Format Standardization ⚠️ REVISED in §6.2 — now load-time normalization, not file conversion

**Decision:** All 5 trees must use the standard `taxonomy→nodes` format (id/title/children/leaf) before the taxonomy engine runs. The aqidah tree must be converted.

**Reasoning:**
- Supporting two formats adds parser complexity with zero benefit
- 4 of 5 trees already use the standard format
- Conversion is a one-time mechanical task
- The taxonomy engine should have ONE code path for tree parsing

**Action:** Add aqidah conversion to build prep as a prerequisite task for CC.

**TRAP:** The aqidah v0 format uses `_label` and `_leaf` as metadata keys (prefixed with single `_`). But it also has `__overview` nodes (double underscore) that are REAL leaf nodes, not metadata. A naive converter that skips all `_`-prefixed keys will lose 2 leaves (28 instead of 30). The converter must only skip the specific metadata keys `_label` and `_leaf`, not all underscore-prefixed keys. Verified: grep finds 30 `_leaf: true`, correct count is 30.

### D-TAX-005: Hierarchical Search Threshold ⚠️ REVISED in §6.2 — reverted to 200

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

### D-TAX-009: Placement Confidence Thresholds ⚠️ REVISED in §6.2 — now three-tier with staging gate

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

1. **Verify tree integrity** — every tree file parses, leaf counts match registry
2. **Create gold baseline** — manually place 10-15 excerpts from ibn_aqil_v3 to validate placement accuracy
3. **Verify CLI adapter works** for structured output extraction
4. **Create test fixtures** — mock excerpts with known correct placements

---

## 6. ChatGPT Pro Adversarial Review — Synthesis (2026-03-30)

ChatGPT Pro (deep research mode) reviewed CORE_EXTRACTION.md and REWRITE_ANALYSIS.md
with access to the full repo. Report: `taxonomy-chatgpt-deep-report.md`.

### 6.1 Verdicts on Each Finding

| # | Finding | Verdict | Impact on Design |
|---|---------|---------|-----------------|
| 1 | Per-excerpt science sanity check | MODIFY → batch preflight | New D-TAX-013 |
| 2 | Distinguish PENDING_NO_TREE from UNPLACEABLE | ACCEPT | Updated D-TAX-003 |
| 3 | Type-based threshold for editorial excerpts | ACCEPT | New D-TAX-014 |
| 4 | Tree normalization at load time (not file conversion) | ACCEPT | Revised D-TAX-004 |
| 5 | Keep 200 hierarchical threshold | ACCEPT | Revised D-TAX-005 |
| 6 | Recall backstop for hierarchical search | ACCEPT | New D-TAX-015 |
| 7 | Stage 0.5-0.79 placements (don't write to live tree) | ACCEPT | Revised D-TAX-009 |
| 8 | Tie detection (top1-top2 < δ) → staging | ACCEPT | Added to D-TAX-009 |
| 9 | Increase primary_text to 800 chars + add div_path | ACCEPT | Updated §3 prompts |
| 10 | Per-excerpt science classifier | REJECT | Batch preflight is sufficient for v1 |
| 11 | Leaf ambiguity scoring | REJECT for v1 | Evaluation data will show where needed |
| 12 | Cheap consensus for staged cases | REJECT for v1 | Evaluation phase serves this function |

**Convergence: 9/12 accepted.** High confidence in the overall design.

### 6.2 New and Revised Design Decisions

#### D-TAX-003 (REVISED): Three-Category Excerpt Routing

Original: unplaceable excerpts go to `unplaced/` directory.
Revised: four distinct output categories:

| Category | Condition | Storage Path |
|----------|-----------|-------------|
| **Placed (high confidence)** | Score ≥0.8 | `library/sciences/{sid}/content/{leaf}/excerpts/{eid}.json` |
| **Staged (low confidence)** | Score 0.5-0.79, or tie (top1-top2 < 0.15) | `library/sciences/{sid}/staged/{leaf}/excerpts/{eid}.json` |
| **Unplaced** | Score <0.5 (tree exists, no good leaf) | `library/sciences/{sid}/unplaced/{eid}.json` |
| **Pending (no tree)** | Science recognized but no tree | `library/pending/{sid}/{eid}.json` |

ChatGPT correctly identified that lumping "no tree" into "unplaceable" collapses
two states: "tree gap" vs "awaiting tree creation." The four-category model
preserves clean re-processing when trees are built.

#### D-TAX-004 (REVISED): Tree Normalization at Load Time

Original: convert aqidah YAML file to standard format on disk.
Revised: implement a tree loader that normalizes both YAML schemas into a single
internal `TreeNode` structure at load time. Don't alter source-of-truth files.

ChatGPT argued (correctly) that file conversion risks ID drift, ordering drift,
or subtle structural changes with no regression suite to catch them. The ABD code
at `reference/archive/abd_code/taxonomy/evolve_taxonomy.py` already includes
`_detect_yaml_format()` and dual-format parsing, proving this is solved.

The tree loader returns a uniform `List[TreeNode]` regardless of the YAML format.
All downstream code works with TreeNode objects, never raw YAML.

#### D-TAX-005 (REVISED): Hierarchical Search Threshold

Original: lowered to 100.
Revised: restored to 200 (matching the SPEC default).

My 100 threshold had an internal inconsistency (claimed imlaa should be "shown
directly" but 105 > 100 would trigger hierarchical). ChatGPT identified the
deeper issue: hierarchical search introduces **recall loss** — if Stage 1 misses
the correct branch, Stage 2 can never recover. This is the "silent, high-confidence
wrong placement" pattern that is the engine's primary threat.

Trees affected:
- ≤200 leaves (aqidah: 30, imlaa: 105): full leaf list → direct placement
- >200 leaves (nahw: 226, sarf: 226, balagha: 335): hierarchical search

#### D-TAX-009 (REVISED): Confidence Thresholds with Staging

Original: auto-place everything ≥0.5.
Revised: three-tier with staging gate:

| Score Range | Action | Additional Conditions |
|-------------|--------|-----------------------|
| ≥0.8 | Auto-place to content/ | — |
| 0.5-0.79 | Stage to staged/ | Also stage if tie (top1-top2 < 0.15) |
| <0.5 | Route to unplaced/ | — |

ChatGPT's core argument: LLM self-scoring is uncalibrated. A score of 0.55 has
no stable meaning. Writing it to the live content directory makes it "official"
even when wrong. The staging directory preserves the excerpt for evaluation
without polluting the content tree.

#### D-TAX-013 (NEW): Batch-Level Science Preflight

Before processing a batch, sample 5 representative excerpts (positions: 1st,
25th percentile, 50th, 75th, last). For each, ask the LLM:

"Which of these sciences does this excerpt belong to: nahw, sarf, balagha,
aqidah, imlaa, or none of these?"

If ≥3 of 5 disagree with the declared science_id, halt with `TAX_SCIENCE_MISMATCH`
and report the detected science. Cost: 5 LLM calls per batch (negligible).

ChatGPT demonstrated this is necessary with concrete data: balagha's tree has
"الأمر" leaves (rhetoric of command) that would plausibly accept fiqh excerpts
about "الأمر يقتضي الوجوب" (command implies legal obligation). The >50%
unplaceable diagnostic does NOT catch this — wrong-science excerpts can score
above 0.5 due to cross-domain vocabulary overlap.

#### D-TAX-014 (NEW): Type-Sensitive Placement Thresholds

For excerpts with `primary_function ∈ {editorial_note, structural_transition}`:
- Require ≥0.85 to auto-place (content/)
- 0.5-0.84 → staged/ (same staging mechanism as low-confidence)
- <0.5 → unplaced/

ChatGPT showed that editorial content (ibn_aqil_v1 introductions about tahqiq
methodology, author biographies) contains rich scholarly language that plausibly
scores 0.55-0.70 against muqaddimat-type leaves. The placement prompt incentivizes
"find something" rather than "refuse." A higher threshold for editorial types
biases toward false negatives (safer in a knowledge library).

#### D-TAX-015 (NEW): Recall Backstop for Hierarchical Search

After Stage 1 selects 3 branches, add "wildcard candidates" via keyword matching:
scan ALL leaf titles for words that appear in the excerpt's `excerpt_topic` list.
Any leaf with ≥2 matching keywords (min 3 chars each) is added as a wildcard
candidate for Stage 2, even if its branch was not selected by Stage 1.

This is pure string matching — zero extra LLM calls. It prevents the catastrophic
"Stage 1 missed the branch → guaranteed wrong placement" failure mode.

### 6.3 Updated Placement Algorithm

**Input to Stage 2 now includes:**
- `excerpt_topic` (list of strings)
- `description_arabic` (full Arabic description)
- `primary_text` (first **800** chars, up from 500)
- `primary_function` and `content_types`
- `div_path` (structural heading path from source book) — **NEW**

div_path provides the book's own organizational signal, which is a free and
often-strong indicator of the correct branch.

### 6.4 Expected Placement Accuracy (Calibrated by ChatGPT Estimate)

ChatGPT estimates 70-80% exact-leaf accuracy for v1 (LLM-only, no embeddings,
no synonyms) on the "right science" portion. This is realistic and acceptable
for v1 because:

1. The evaluation phase measures actual accuracy
2. The staging mechanism captures uncertain placements
3. Most errors will be "neighbor leaf" (right branch, adjacent leaf), not random
4. The gold baseline test provides calibration data

Systematic patterns to watch for in evaluation:
- Overproduction of __overview and muqaddimat leaves (broad-leaf bias)
- Editorial excerpts in topical leaves at 0.5-0.85 confidence
- Methodology excerpts (usul-al-nahw) concentrating into generic leaves
- Low unplaceable rate when science assignment is wrong (the D-TAX-013 preflight
  should catch this, but verify)

### 6.5 Remaining Risk After All Changes

The residual risk after these 15 design decisions is:

**Within-batch cross-science excerpts.** If a nahw book has 3 sarf excerpts out
of 200, the batch preflight (5 samples) may not catch them. Those 3 excerpts
could get plausibly wrong placements in the nahw tree. This is accepted for v1 —
the evaluation phase catches these via manual review of staged placements.

**Uncalibrated confidence in the 0.8+ range.** Even "high confidence" placements
may be wrong. The staging gate only protects the <0.8 range. For v1, the owner's
manual review of a sample of content/ placements is the quality gate.

**Leaf title ambiguity in particle-heavy sciences.** Nahw leaf titles like
"حروف الجر الزائدة وشبه الزائدة" may confuse the LLM when the excerpt discusses
one specific particle. This is a granularity issue in the tree, not a design flaw.
The evaluation phase will measure where this matters.
