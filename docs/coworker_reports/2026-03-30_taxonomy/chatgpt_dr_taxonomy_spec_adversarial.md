# KR Taxonomy Engine Core v1 SPEC Adversarial Review

## Executive summary

The new core v1 SPEC is close to “implementation-ready,” but it is not yet at the level where an implementation agent could produce the correct architecture with **zero clarifying questions**. The remaining risks are mostly *not* about the high-level design; they are about **underspecified interfaces** (LLM structured output, leaf identifiers, registry semantics) and **type/routing edge-cases** that can create silent misbehavior (wrong file paths, front-matter leaking into live content, stage routing inconsistencies). fileciteturn28file0L1-L1

The architect’s five accepted checkpoint findings are visibly incorporated in the SPEC: (i) staging gate, (ii) type-based thresholds, (iii) runtime tree normalization (dual-format load), (iv) hierarchical threshold restored to 200, and (v) `TAX_PENDING_NO_TREE` distinct from unplaceable. fileciteturn28file0L1-L1 The weakest part is not whether these appear, but whether the SPEC makes their *boundary conditions and invariants* unambiguous, and whether the supporting docs still contain contradictory instructions that will mislead an implementer. fileciteturn29file0L1-L1

**My single biggest “production-bug bet”:** a mismatch between what Stage 2 returns (`leaf_id`) and what file writing needs (a **unique leaf path**), causing either wrong output paths or mis-validation; second place is structured-output parsing failures (Stage 1 and Stage 2) because the SPEC describes Pydantic models but does not fully pin down JSON-only prompt obligations and adapter behavior. fileciteturn28file0L1-L1

## Implementation readiness

### Ambiguities that will force clarifying questions

The SPEC is strong on “what” and medium on “how.” A coding agent will likely get stuck on these specifics unless they are explicitly pinned down.

**Leaf identifier semantics are ambiguous (high risk).** Stage 2’s response model returns `leaf_id: str`, while the output contract expects `confirmed_leaf` to be a “leaf path” like `almajrurat/huruf_aljar/ma3ani_huruf_aljar`. fileciteturn28file0L1-L1 The prompt context for each candidate includes both `leaf_id` and `full_path`. fileciteturn28file0L1-L1 But the SPEC never states whether:
- `leaf_id` in Stage 2 output must equal the **candidate’s node ID** (e.g., `ma3ani_huruf_aljar`), or
- `leaf_id` must equal the **unique full path**, or
- Stage 2 must output both.

This matters because file writing is path-based (“`content/{leaf_path}/excerpts/…`”), and correctness depends on unambiguous routing. fileciteturn28file0L1-L1 Even if node IDs are intended to be unique, the SPEC does not require or test that uniqueness invariant at load time.

**Registry semantics are referenced but not specified (medium–high risk).** The SPEC asserts `science_id` must match a registered science in `taxonomy_registry.yaml`, and that the registry maps science IDs to active tree versions. fileciteturn28file0L1-L1 But the registry file schema is not included or exemplified, and error handling is contradictory: `TAX_INVALID_SCIENCE` is labeled “Fatal (batch)” while also saying the “Entire batch routed to pending_no_tree.” fileciteturn28file0L1-L1 An implementer will have to guess which behavior is authoritative (abort vs produce pending artifacts + batch report), and how to treat “unregistered science” vs “registered but no active tree.”

**LLM structured-output contract is not fully pinned (high risk).** The SPEC defines Pydantic response models (`BranchSelection`, `PlacementRanking`) and says calls route through `shared/llm/cli_adapter.py`. fileciteturn28file0L1-L1 It does not fully specify:
- Whether the adapter enforces JSON mode / schema constraints, or merely parses best-effort.
- What exact prompting guarantees JSON-only output (especially for Stage 1, which is described but not templated as strictly as “Respond with valid JSON only”).
- What the adapter returns on parse failure, and how retries are triggered.

In practice, “structured output” failures tend to be *the* early failure mode in LLM pipelines unless the prompt and adapter behavior are extremely explicit.

**Stage 1 “no_match” behavior conflicts with the unplaced schema (medium risk).** If Stage 1 returns `no_match: true`, the excerpt goes to unplaced with reason “Stage 1: no matching branch.” fileciteturn28file0L1-L1 But the unplaced output schema says it contains `best_candidates` (top 3 with leaf_id/score/reasoning). fileciteturn28file0L1-L1 A Stage-1 termination produces no leaf candidates unless you define a fallback (e.g., store branch-level candidates, or store empty list). The SPEC should specify what `best_candidates` becomes in that pathway; otherwise different implementations will diverge.

**Text truncation limits are internally inconsistent (medium risk).** The Stage 2 spec says: full `primary_text` if ≤ 3000 characters; first 1500 characters if longer. fileciteturn28file0L1-L1 Later config defines `primary_text_char_limit: 3000` as “Max chars of primary_text in Stage 2 prompt (full text if shorter).” fileciteturn28file0L1-L1 An implementation will ask: if the limit is 3000, why truncate to 1500 instead of 3000? This matters because the disambiguating evidence in Arabic commentaries can easily appear after the first 1500 chars.

### What is clear enough to implement as-is

Despite the issues above, several critical elements are well specified:

- The engine’s v1 scope (“placement only,” deferred list, and core responsibilities). fileciteturn28file0L1-L1  
- Input requirements and “warn vs reject” logic at a high level. fileciteturn28file0L1-L1  
- The four routing categories: live, staged, unplaced, pending-no-tree, and their directories. fileciteturn28file0L1-L1  
- UTF-8 write + read-back fidelity checks to prevent Arabic text corruption. fileciteturn28file0L1-L1  
- Hierarchical vs direct mode threshold at 200 leaves, with specific per-science examples. fileciteturn28file0L1-L1  

## Checkpoint #1 findings incorporated and remaining edge cases

### Staging gate

The SPEC implements a staging gate: teaching content is live at ≥0.80, staged at 0.50–0.79, unplaced below 0.50; editorial/structural is live at ≥0.85, staged at 0.50–0.84, unplaced below 0.50. fileciteturn28file0L1-L1 This is directionally correct and matches the safety intent (“uncertain placements don’t enter live tree”). fileciteturn28file0L1-L1

Edge-case risk: the SPEC records ties (`top1 - top2 ≤ 0.10`) but explicitly continues placement rather than forcing staging. fileciteturn28file0L1-L1 If you want staged to be the “uncertainty sink,” ties are a canonical uncertainty signal. (This wasn’t listed among the five accepted findings, but it is a safety gap given how often near-ties occur with semantically adjacent leaves in nahw.)

### Type-based editorial handling

The SPEC’s type detection is: editorial/structural if `primary_function ∈ {editorial_note, structural_transition, cross_reference}`, otherwise teaching. fileciteturn28file0L1-L1

Two adversarial issues:

1. **Conflating “editorial_note” with “cross_reference/structural_transition.”** In the real nahw excerpts, there is a `primary_function: cross_reference` excerpt that is explicitly non-teaching (“وسيأتي الكلام…”). fileciteturn31file0L1-L1 Under the SPEC, if Stage 2 scores it ≥0.85 (plausible because its topic is still within حروف الجر), it can enter the live content tree—despite being navigation text rather than knowledge content. fileciteturn28file0L1-L1  
   **Action:** split the category. Recommended v1 rule: `cross_reference` and `structural_transition` are **never eligible for live** (always staged) regardless of score; only `editorial_note` can go live at a higher threshold.

2. **Defaulting missing/unknown `primary_function` to “teaching.”** The SPEC treats absent/null as teaching. fileciteturn28file0L1-L1 That is an unsafe default in a pipeline where upstream metadata may be partial. A safer default is: “if `primary_function` missing, treat as `unknown` and use the stricter threshold (or stage-by-default).”

### `TAX_PENDING_NO_TREE` vs `TAX_UNPLACEABLE`

The SPEC cleanly defines pending-no-tree as the case where the requested `science_id` has no active tree in the registry, and explicitly states it is not lumped with unplaced because it preserves re-processing clarity. fileciteturn28file0L1-L1 This is correct.

But the output layout and error handling need one more tightening: the SPEC first claims “all outputs are written under `library/sciences/{science_id}/`” yet pending-no-tree location includes another `{science_id}` segment (`pending_no_tree/{science_id}/{excerpt_id}.json`). fileciteturn28file0L1-L1 For v1, this is survivable, but it’s easy to implement inconsistently. The simplest correction is to define a single canonical root for pending artifacts (e.g., `library/pending_no_tree/{science_id}/…`) independent of whether `library/sciences/{science_id}` exists yet.

### Runtime tree normalization (dual-format load)

The SPEC implements runtime normalization and explicitly says source YAML files are never modified; it supports both v1 (`taxonomy→nodes`) and v0 (nested dict, `_label`/`_leaf`) formats. fileciteturn28file0L1-L1 It also explicitly treats `__overview` keys as real nodes, not metadata, which is the critical trap. fileciteturn28file0L1-L1

The detection rule (“if `taxonomy` key with a `nodes` array => v1 else v0”) matches the archived reference implementation’s `_detect_yaml_format`. fileciteturn28file0L1-L1 fileciteturn33file0L1-L1

One remaining underspecification: for v0 files, the SPEC does not state how to handle the **top-level container key** (e.g., `aqidah:`). Should it become a real root node in paths, or should it be treated as an envelope? This matters because Stage 2 candidates include `full_path` and output paths are built from leaf paths.

### Hierarchical threshold at 200

The SPEC confirms the 200-leaf threshold and documents which sciences trigger hierarchical mode (nahw/sarf/balagha) vs direct mode (aqidah/imlaa). fileciteturn28file0L1-L1 This resolves the earlier inconsistency noted in the pre-rewrite analysis. fileciteturn29file0L1-L1

One caution: top-down/hierarchical classification has a known “error propagation” failure mode—if the coarse selection is wrong, finer ranking cannot recover. This is a general property of top-down hierarchical classification approaches. citeturn2search0turn2search1 Your design mitigates this by selecting 3 branches, but the SPEC does not include a recall-backstop (e.g., wildcard candidates) as a core requirement.

## Contract correctness against the repo’s real excerpt format

### Input contract vs `ibn_aqil_v3/excerpts.jsonl`

The SPEC requires `excerpt_id`, `source_id`, `primary_text`, and a non-empty `excerpt_topic: list[str]`, rejecting on absence. fileciteturn28file0L1-L1 The real excerpt JSONL lines include all these fields, with `excerpt_topic` consistently represented as a list of Arabic strings. fileciteturn31file0L1-L1

The SPEC’s “expected fields” include `description_arabic`, `primary_function`, `content_types`, and `div_path` as warning-only if absent. fileciteturn28file0L1-L1 The real excerpts include these fields and they are nontrivial: `description_arabic` is richly descriptive, `div_path` maintains heading context (“حروف الجر”), and `primary_function` includes types like `rule_statement`, `opinion_statement`, and `cross_reference`. fileciteturn31file0L1-L1

A subtle mismatch to address proactively: the real data contains structural types as **secondary** functions and inside `content_types`, not only in `primary_function`. fileciteturn31file0L1-L1 If v1 routing depends only on `primary_function`, it will miss “mixed” excerpts.

### Output contract completeness and internal consistency

The output contract is conceptually complete (live/staged/unplaced/pending + batch report). fileciteturn28file0L1-L1 The biggest consistency risk is the earlier “leaf_id vs leaf_path” ambiguity because output path construction depends on it. fileciteturn28file0L1-L1

D‑023 provenance preservation is clearly stated: taxonomy adds fields but never strips upstream fields, implemented as merging the full original excerpt object with additions. fileciteturn28file0L1-L1 This matches what the pipeline needs, given the excerpt objects carry important upstream provenance structures (`physical_pages`, `quoted_scholars`, etc.). fileciteturn31file0L1-L1

Two missing enforcement details for “contract correctness”:

- **Collision policy:** what if the original excerpt already has a key that taxonomy adds (`lifecycle_stage`, `confirmed_leaf`, etc.)? The merge order implies taxonomy overwrites; SPEC should explicitly state overwrite behavior to avoid accidental preservation of upstream wrong values. fileciteturn28file0L1-L1  
- **Serialization invariants:** the SPEC mandates UTF‑8 and a fidelity check on `primary_text`, but it does not mandate `ensure_ascii=False` (to avoid hideous escaping) nor does it specify stable ordering/indent (useful for diffs and review). fileciteturn28file0L1-L1

## What will break first

If I had to bet on the first production bug (or first “silent wrongness”), I would rank them:

### Leaf selection output not matching file routing semantics

The failure mode: Stage 2 returns an identifier that the writer interprets as a path when it is really an ID (or vice versa), so excerpts end up written to malformed directories, fail validation, or worse—are written “successfully” to the wrong place. This is plausibly the #1 risk because the SPEC currently names `leaf_id` in Stage 2 output, but names `confirmed_leaf` as a path and uses leaf paths in output locations. fileciteturn28file0L1-L1

### Structured output parsing failures in the CLI adapter integration

The SPEC relies on structured responses validated by Pydantic, but does not fully enforce JSON-only output in the prompt specifications (especially Stage 1), nor fully specify adapter behavior under partial/invalid outputs. fileciteturn28file0L1-L1 This is classically where early implementations degrade into “best-effort parsing,” which produces heisenbugs.

### v0 tree normalization root-key and underscore edge cases

The normalization rules are mostly correct and even reference a known-good `_detect_yaml_format`, but they remain underspecified about root handling and multi-top-level-key YAML. fileciteturn28file0L1-L1 fileciteturn33file0L1-L1 The risk is not a crash; it’s a subtly wrong `full_path` computation that changes output directory structure and breaks reprocessing/versioning expectations.

### Cross-reference and structural content leaking into live

The real excerpt set includes `cross_reference` as a primary function. fileciteturn31file0L1-L1 Your type-based thresholds help, but they still allow `cross_reference` into live if score ≥ 0.85. fileciteturn28file0L1-L1 This is a “silent semantic corruption” risk: the excerpt is on-topic but functionally non-content.

### Arabic encoding through write → read → verify

This is less likely to break first because the SPEC strongly specifies UTF‑8 and a post-write verification check that treats corruption as worse than no placement. fileciteturn28file0L1-L1 The risk is mostly in OS edge cases (Windows default encodings) and in accidentally comparing normalized Unicode rather than preserving exact codepoints.

One broader caution: LLM “confidence” is not reliably calibrated to correctness in general, and recent empirical studies find that self-reported confidence can remain high even when answers are wrong. citeturn0search0turn0search3 This supports the staging gate as a safety mechanism, but it also means “≥0.80” does not guarantee safety—so your evaluation plan and gold baselines remain essential. fileciteturn28file0L1-L1

## Missing tests and concrete additions to the SPEC

The SPEC already includes unit tests for routing thresholds, tree loading, and a “gold baseline” concept. fileciteturn28file0L1-L1 The missing pieces are tests that catch *silent failures* (the engine “succeeds” but the library becomes wrong).

### Tests to add that target silent corruption

**Leaf-identifier invariant test (must-have).** Load `nahw/tree.yaml` and assert:
- Every leaf has a unique `full_path`.
- Either every node `id` is unique globally, or Stage 2 must return `full_path` (and you forbid returning plain `id`). fileciteturn28file0L1-L1 fileciteturn32file0L1-L1

**Stage 1 no-match pathway schema test.** Force Stage 1 to return `{no_match: true}` and verify the unplaced output schema is still valid: define whether `best_candidates=[]` or contains branch-level candidates. fileciteturn28file0L1-L1

**Cross-reference “never-live” test (must-have if you accept my critique).** Use the real excerpt with `primary_function: cross_reference` (“وسيأتي الكلام…”) and a mock ranking score of 0.95; assert it does **not** go to `content/` even at high score, and lands in staged front-matter. fileciteturn31file0L1-L1

**Intersection-topic adversarial placement test (high value).** In the real data, the excerpt about “كي” contains both “كي حرف جر” and “فعل مضارع منصوب بأن بعد كي” language. fileciteturn31file0L1-L1 In the nahw tree, there is a leaf for `huruf_aljar` meanings and also a leaf `kay` under `nawasiib_almudari3`. fileciteturn32file0L1-L1 Add a gold test that forces the correct placement policy (whatever you decide) and detects wrong-branch routing.

**Pending-no-tree isolation test.** Run a batch with a fake `science_id` and ensure:
- No attempt is made to write under `content/` or `staged/`.
- Output paths are deterministic and do not pollute `library/sciences/{sid}` unless you explicitly want them to. fileciteturn28file0L1-L1

### SPEC edits to remove ambiguity (minimal, concrete)

To make the SPEC truly “zero clarifying questions,” I recommend these specific edits:

1. **Define Stage 2 output identifier unambiguously:**  
   Replace `leaf_id` in `LeafScore` with `leaf_path` (must equal candidate `full_path`). Or require both. Then define `confirmed_leaf` = `leaf_path`. fileciteturn28file0L1-L1

2. **Pin JSON-only structured output rules in prompts:**  
   For both Stage 1 and Stage 2, include explicit “Respond with valid JSON only, matching this schema” instructions and embed a minimal example. (You already do this style in the archived taxonomy evolution tool prompts, which insist on JSON-only in system prompts.) fileciteturn33file0L1-L1

3. **Split editorial types:**  
   Change type handling to:
   - `structural_transition` and `cross_reference`: always staged (never live), regardless of score.  
   - `editorial_note`: eligible for live at ≥0.85. fileciteturn28file0L1-L1

4. **Resolve `primary_text` truncation inconsistency:**  
   Make `primary_text_char_limit` authoritative: “include first `min(len(primary_text), primary_text_char_limit)` characters,” and delete the 1500 special-case. fileciteturn28file0L1-L1

5. **Specify v0 root handling:**  
   Add one paragraph: “For v0 trees, if the YAML has a single top-level key, treat it as a root container and do not include it in paths; path begins at its children.” (Or the opposite—just make it explicit.) fileciteturn28file0L1-L1

6. **Unify “fatal vs recoverable” language in error table:**  
   If `TAX_INVALID_SCIENCE` routes a batch to pending, it is not “fatal” in the same sense as parse errors. Clarify severity taxonomy as “fatal to placement, but recoverable via pending artifacts.” fileciteturn28file0L1-L1

A final meta-risk: the supporting docs are still partially contradictory. `REWRITE_ANALYSIS.md` contains both the older “convert aqidah to one format” decision and the revised “normalize at load-time” direction within the same document. fileciteturn29file0L1-L1 Even if the SPEC is correct, that contradiction increases the odds that an implementation agent follows the wrong thread. Tighten `REWRITE_ANALYSIS.md` to clearly mark superseded decisions as deprecated.

```mermaid
flowchart TD
  A[Read JSONL excerpts] --> B[Validate required fields]
  B -->|science_id has no active tree| P[Write pending-no-tree artifact]
  B --> C[Load tree.yaml]
  C --> D[Normalize tree format to internal TreeNode]
  D --> E{leaf_count > 200?}
  E -->|No| H[Stage 2: rank all leaves]
  E -->|Yes| F[Stage 1: select branches]
  F -->|no_match| U[Write unplaced artifact]
  F --> G[Collect candidate leaves in selected branches]
  G --> H[Stage 2: rank candidates]
  H --> I{route by type + score}
  I -->|live| L[Write content/{leaf_path}/excerpts/{id}.json]
  I -->|staged| S[Write staged/{leaf_path}/excerpts/{id}.json]
  I -->|unplaced| U[Write unplaced/{id}.json]
  L --> V[Post-write validation: leaf exists + primary_text fidelity]
  S --> V
  U --> R[Append to batch report]
  V --> R[Append to batch report]
```

