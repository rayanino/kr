# NEXT — Excerpting Engine: Fix Division Tree Preamble Gaps (Phase 1 Blocker)

## Current Position

- **Baseline:** 570 tests passing (2 skipped), 0 failed
- **Commit:** `449d9754` (hardening review ACCEPTED — 9 bug fixes, integration test infrastructure)
- **Blocker:** ALL 5 experimental packages in `experiments/format_diversity_test/packages/` fail Phase 1 validation (EX-V-001: uncovered unit indices). No real LLM integration testing can proceed until this is fixed.

## Root Cause

The division tree from the normalization engine legitimately produces parent nodes whose `[start_unit_index, end_unit_index]` range is NOT fully covered by their children's ranges. This is the standard Arabic scholarly text pattern: a chapter (باب) starts with introductory text before its sub-sections (فصول). The normalization SPEC guarantees containment ("child divisions are contained within their parent's page range") but NOT full coverage.

Example from ibn_aqil_v1:
```
div_src_test0001_2_009: units [258..389]  "كان وأخواتها"
  div_src_test0001_3_000: units [298..389]  "فصل في ما ولا..."
    div_src_test0001_4_000: units [319..341]  "أفعال المقاربة"
    div_src_test0001_4_001: units [342..389]  "إن وأخواتها"
```

Units 258–297 (40 units, **3,255 Arabic words** — the chapter introduction to كان وأخواتها) are in the parent but NOT in any child. `find_leaf_divisions()` only returns nodes with empty `children` lists, so these units are never assembled into chunks. V-P1-2 then correctly rejects them as "uncovered."

**Scope across all 5 packages:**

| Package | Total Units | Gap Units | % Lost |
|---------|------------|-----------|--------|
| ext_39_masala | 90 | 6 | 6.7% |
| ext_46_qa | 405 | 119 | 29.4% |
| ibn_aqil_v1 | 390 | 61 | 15.6% |
| ibn_aqil_v3 | 328 | 7 | 2.1% |
| taysir | 741 | 89 | 12.0% |

**Every gap is a "preamble"** — content before the first child's start_unit_index. Verified: zero inter-child gaps and zero trailing gaps across all 5 packages. But the fix handles all gap types defensively.

## Read First

1. `engines/excerpting/src/phase1_assembly.py` — `find_leaf_divisions()` (line 180), `_build_parent_map()` (line 1281), `validate_phase1()` (line 1132), `run_phase1()` (line 1338)
2. `engines/excerpting/tests/conftest.py` — `_make_division_node()` (line 312), `_make_division_tree()` (line 400)
3. `engines/excerpting/tests/test_phase1_tree_walk.py` — existing find_leaf_divisions tests
4. `engines/excerpting/tests/test_phase1_validation.py` — existing validate_phase1 tests
5. `engines/normalization/contracts.py` — `DivisionNode` (line 484), `DivisionType` enum (line 467), `HeadingDetectionMethod` (line 51), `HeadingConfidence` (line 42)

## What to Do

### PART A: Implement `_complete_division_tree()`

**File:** `engines/excerpting/src/phase1_assembly.py`
**Location:** New private function. Insert after the existing `find_leaf_divisions()` function (after line ~206), before `should_skip_division()`.

```python
def _complete_division_tree(
    nodes: list[DivisionNode],
) -> list[DivisionNode]:
    """Insert synthetic leaf nodes for parent content not covered by children.

    When a parent DivisionNode has children, the children may not cover the
    parent's full [start_unit_index, end_unit_index] range. This is normal
    in Arabic scholarly texts — a chapter (باب) often starts with introductory
    text before its sub-sections (فصول). These uncovered units would cause
    EX-V-001 (uncovered unit indices) in validation.

    This function recursively walks the tree and inserts synthetic leaf nodes
    to fill three types of gap:
    - Preamble: units in [parent.start, first_child.start - 1]
    - Inter-child: units in [child_n.end + 1, child_n+1.start - 1]
    - Trailing: units in [last_child.end + 1, parent.end]

    Empirically, all 5 test packages have ONLY preamble gaps (zero inter-child,
    zero trailing), but inter-child and trailing are handled defensively.

    Synthetic nodes use div_id suffixes (_pre, _gap_N, _post) that cannot
    collide with normalization-generated IDs (format: div_{source_id}_{depth}_{index}).

    Returns a NEW tree. Input nodes are not mutated.
    """
```

**Algorithm (implement exactly):**

```
function _complete_division_tree(nodes):
    result = []
    for node in nodes:
        if node has no children:
            result.append(node)  # Leaf — no change needed
            continue

        # Recursively complete children first
        completed_children = _complete_division_tree(node.children)

        # Sort children by start_unit_index (defensive — should already be sorted)
        sorted_children = sorted(completed_children, key=lambda c: c.start_unit_index)

        # Determine heading_level for synthetic leaves (same as first child)
        child_level = sorted_children[0].heading_level

        new_children = []

        # 1. Preamble gap: [parent.start, first_child.start - 1]
        first_child_start = sorted_children[0].start_unit_index
        if node.start_unit_index < first_child_start:
            synthetic = DivisionNode(
                div_id=f"{node.div_id}_pre",
                division_type=DivisionType.MUQADDIMAH,
                heading_text="مقدمة",
                heading_level=child_level,
                start_unit_index=node.start_unit_index,
                end_unit_index=first_child_start - 1,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
                children=[],
            )
            new_children.append(synthetic)

        # 2. Walk through children, inserting inter-child gap synthetics
        for i, child in enumerate(sorted_children):
            new_children.append(child)
            if i < len(sorted_children) - 1:
                next_child = sorted_children[i + 1]
                gap_start = child.end_unit_index + 1
                gap_end = next_child.start_unit_index - 1
                if gap_start <= gap_end:
                    synthetic = DivisionNode(
                        div_id=f"{node.div_id}_gap_{i}",
                        division_type=None,
                        heading_text=node.heading_text,
                        heading_level=child_level,
                        start_unit_index=gap_start,
                        end_unit_index=gap_end,
                        detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                        confidence=HeadingConfidence.HIGH,
                        children=[],
                    )
                    new_children.append(synthetic)

        # 3. Trailing gap: [last_child.end + 1, parent.end]
        last_child_end = sorted_children[-1].end_unit_index
        if last_child_end < node.end_unit_index:
            synthetic = DivisionNode(
                div_id=f"{node.div_id}_post",
                division_type=None,
                heading_text=node.heading_text,
                heading_level=child_level,
                start_unit_index=last_child_end + 1,
                end_unit_index=node.end_unit_index,
                detection_method=HeadingDetectionMethod.KEYWORD_HEURISTIC,
                confidence=HeadingConfidence.HIGH,
                children=[],
            )
            new_children.append(synthetic)

        # Create new node with updated children (do NOT mutate original)
        result.append(node.model_copy(update={"children": new_children}))

    return result
```

**Imports required:** `DivisionType`, `HeadingDetectionMethod`, and `HeadingConfidence` are NOT currently imported in this file. Add them to the existing `from engines.normalization.contracts import (...)` block (lines 37-49). The updated import block should include:

```python
from engines.normalization.contracts import (
    BoundaryContinuity,
    BoundaryContinuityType,
    ContentFlags,
    ContentUnit,
    DivisionNode,
    DivisionType,
    Footnote,
    HeadingConfidence,
    HeadingDetectionMethod,
    LayerType,
    NormalizedManifest,
    NormalizedPackage,
    PhysicalPage,
    TextLayerSegment,
)
```

### PART B: Wire into `run_phase1()`

**File:** `engines/excerpting/src/phase1_assembly.py`
**Location:** `run_phase1()` function (line 1338)

Four changes:

**Change 1 (line 1362–1363):** Complete the tree before walking.

Replace:
```python
    # ── Step 1: Walk division tree ────────────────────────────────
    leaves = find_leaf_divisions(manifest.division_tree)
```

With:
```python
    # ── Step 0: Complete division tree (handle preamble gaps) ─────
    completed_tree = _complete_division_tree(manifest.division_tree)

    # ── Step 1: Walk division tree ────────────────────────────────
    leaves = find_leaf_divisions(completed_tree)
```

**Change 2 (line 1435):** Pass completed_tree to the early-return validate_phase1 call.

Replace:
```python
        return [], validate_phase1([], manifest, skipped_divisions, config)
```

With:
```python
        return [], validate_phase1([], manifest, skipped_divisions, config, completed_tree=completed_tree)
```

**Change 3 (line 1438):** Use completed_tree for parent map.

Replace:
```python
    parent_map = _build_parent_map(manifest.division_tree)
```

With:
```python
    parent_map = _build_parent_map(completed_tree)
```

**Change 4 (line 1568):** Pass completed_tree to the final validate_phase1 call.

Replace:
```python
    validation_results = validate_phase1(
        split_results, manifest, skipped_divisions, config
    )
```

With:
```python
    validation_results = validate_phase1(
        split_results, manifest, skipped_divisions, config,
        completed_tree=completed_tree,
    )
```

### PART C: Update `validate_phase1()` signature

**File:** `engines/excerpting/src/phase1_assembly.py`
**Location:** `validate_phase1()` function (line 1132)

**Change 1:** Add optional parameter.

Replace:
```python
def validate_phase1(
    chunks: list[AssembledChunk],
    manifest: NormalizedManifest,
    skipped_divisions: dict[str, str],
    config: ExcerptingConfig,
) -> list[dict]:
```

With:
```python
def validate_phase1(
    chunks: list[AssembledChunk],
    manifest: NormalizedManifest,
    skipped_divisions: dict[str, str],
    config: ExcerptingConfig,
    completed_tree: list[DivisionNode] | None = None,
) -> list[dict]:
```

**Change 2 (line 1154):** Use completed_tree when provided.

Replace:
```python
    all_leaves = find_leaf_divisions(manifest.division_tree)
```

With:
```python
    tree = completed_tree if completed_tree is not None else _complete_division_tree(manifest.division_tree)
    all_leaves = find_leaf_divisions(tree)
```

This is backward-compatible — existing test calls with 4 positional args still work (completed_tree defaults to None, and the function computes it internally).

### PART D: New tests

**File:** `engines/excerpting/tests/test_phase1_preamble.py` (NEW FILE)

Test class: `TestCompleteDivisionTree`

Use `_make_division_node` from conftest. Import `_complete_division_tree` from `engines.excerpting.src.phase1_assembly`.

**Test 1: `test_preamble_gap_creates_synthetic_leaf`**
- Create parent [0..9] with one child [5..9]. Gap = [0..4].
- Call `_complete_division_tree([parent])`.
- Assert result has 1 node, with 2 children: synthetic preamble [0..4] + original child [5..9].
- Assert synthetic leaf: div_id ends with `_pre`, division_type is MUQADDIMAH, heading_text is "مقدمة", children is empty, start=0, end=4.

**Test 2: `test_no_gap_no_change`**
- Create parent [0..9] with two children [0..4] and [5..9]. No gap.
- Call `_complete_division_tree([parent])`.
- Assert result has 1 node with exactly 2 children (no synthetic added).

**Test 3: `test_flat_tree_no_change`**
- Create 3 leaf nodes (no children). Call `_complete_division_tree(leaves)`.
- Assert output has 3 nodes, all with empty children.

**Test 4: `test_inter_child_gap_creates_synthetic_leaf`**
- Create parent [0..19] with two children [0..4] and [10..19]. Gap at [5..9].
- Call `_complete_division_tree([parent])`.
- Assert 3 children: original [0..4], synthetic gap [5..9], original [10..19].
- Assert synthetic: div_id ends with `_gap_0`, division_type is None.

**Test 5: `test_trailing_gap_creates_synthetic_leaf`**
- Create parent [0..19] with one child [0..9]. Trailing gap [10..19].
- Call `_complete_division_tree([parent])`.
- Assert 2 children: original [0..9], synthetic [10..19].
- Assert synthetic: div_id ends with `_post`, division_type is None.

**Test 6: `test_nested_preamble_gaps`**
- Create: grandparent [0..29] → parent [10..29] (preamble gap [0..9]) → child [20..29] (preamble gap [10..19]).
- Call `_complete_division_tree([grandparent])`.
- Assert grandparent has synthetic preamble [0..9] + completed parent.
- Assert completed parent has synthetic preamble [10..19] + original child [20..29].
- Verify all synthetic leaves have `children == []`.

**Test 7: `test_original_tree_not_mutated`**
- Create parent [0..9] with one child [5..9].
- Save `len(parent.children)`.
- Call `_complete_division_tree([parent])`.
- Assert original parent still has exactly 1 child (not mutated).

**Test 8: `test_synthetic_leaf_heading_level_matches_siblings`**
- Create parent (heading_level=2) with child (heading_level=3) starting at unit 5. Parent starts at 0.
- Call `_complete_division_tree`.
- Assert synthetic preamble has heading_level=3 (same as sibling, not parent).

**Test 9: `test_preamble_combined_with_trailing`**
- Create parent [0..29] with one child [10..19]. Gaps: preamble [0..9], trailing [20..29].
- Call `_complete_division_tree`.
- Assert 3 children: synthetic preamble [0..9], original [10..19], synthetic trailing [20..29].

**Test 10: `test_run_phase1_ibn_aqil_v1_passes`**
Integration test — load the actual package and run Phase 1.
- Load package from `experiments/format_diversity_test/packages/ibn_aqil_v1/` using the `load_package()` pattern from `scripts/run_integration_test.py` (lines 169-203): read manifest.json with `NormalizedManifest.model_validate_json()`, read content.jsonl line by line with `ContentUnit.model_validate_json()`, construct `NormalizedPackage(manifest=manifest, content_units=units)`.
- Call `run_phase1(pkg, ExcerptingConfig())`.
- Assert no ValueError raised.
- Assert `len(chunks) > 0`.
- Assert all validation checks have status "pass" or "warning" (no "fail").

**Test 11: `test_run_phase1_all_packages_pass`**
Parametrized integration test — run all 5 packages.
- Use `@pytest.mark.parametrize` with the 5 package directory names: `["ext_39_masala", "ext_46_qa", "ibn_aqil_v1", "ibn_aqil_v3", "taysir"]`.
- For each: load package (same pattern as Test 10), run `run_phase1`, assert no ValueError, assert `len(chunks) > 0`.

**Test 12: `test_empty_children_list_treated_as_leaf`**
Edge case: node with `children=[]` (explicit empty) is a leaf, not a parent with missing children.
- Create node with children=[]. Call `_complete_division_tree([node])`.
- Assert output is 1 node with children=[] (unchanged).

### PART E: SPEC Errata Note

**File:** `engines/excerpting/SPEC.md`
**Location:** §4.2 — Division Tree Walking, after the "Leaf identification" paragraph (around line 635).

Add a new paragraph after the existing leaf identification text:

```
**Parent preamble content (tree completion):** The normalization engine produces division trees where parent nodes may have content units not covered by any child. This is the standard Arabic scholarly text pattern: a chapter (باب) starts with introductory text before its sub-sections (فصول). Before walking the tree, the engine calls `_complete_division_tree()` which inserts synthetic leaf nodes for uncovered ranges. Three gap types are handled: preamble (content before the first child), inter-child (content between consecutive children), and trailing (content after the last child). Synthetic preamble leaves use `DivisionType.MUQADDIMAH` with `heading_text="مقدمة"`. Synthetic div_ids use `{parent_div_id}_pre`, `_gap_{N}`, or `_post` suffixes. Empirically, all 5 test packages exhibit only preamble gaps (zero inter-child, zero trailing). Without tree completion, 2–29% of content units per source would be silently lost.
```

## Design Decisions

- **DD-P-1:** Synthetic leaves use `DivisionType.MUQADDIMAH` ("مقدمة") for preamble gaps. This is semantically accurate — the preamble content IS the chapter introduction. The LLM will see "مقدمة" in div_path and understand context. Inter-child and trailing gaps use `None` (rare defensive cases with no clear semantic label).

- **DD-P-2:** The function creates new nodes via `model_copy(update=...)` to avoid mutating the original manifest.division_tree. The normalization manifest is read-only from the excerpting engine's perspective (D-023: never modify upstream metadata).

- **DD-P-3:** Synthetic div_ids use `{parent_div_id}_pre` / `_gap_{n}` / `_post` suffixes. These cannot collide with normalization IDs which follow `div_{source_id}_{depth}_{index}` format (always ends with an integer).

- **DD-P-4:** `validate_phase1` gets an optional `completed_tree` parameter (default None) for backward compatibility. When None, it computes the completed tree internally. In `run_phase1`, the tree is completed once and passed explicitly to avoid redundant computation.

- **DD-P-5:** Synthetic leaves use the first child's `heading_level`, not the parent's. They are siblings of the children (same tree depth), so they should share the children's heading level for correct heading path construction.

- **DD-P-6:** The `detection_method` is `KEYWORD_HEURISTIC` and `confidence` is `HIGH` for synthetic nodes. These are metadata fields not used by any excerpting engine processing decision — they are informational only.

## Do NOT Do

- Do NOT modify `find_leaf_divisions()`. Its definition ("leaf = node with empty children list") is correct and unchanged. The fix is upstream — completing the tree before walking it.
- Do NOT modify the normalization engine or its contracts. The normalization output is correct — it represents the book's actual structure. The excerpting engine must handle the reality that parents have preamble content.
- Do NOT modify any existing test file. The new optional parameter on `validate_phase1` is backward-compatible.
- Do NOT modify LLM prompts, Phase 2 code, or Phase 3 code. This fix is Phase 1 only.
- Do NOT implement anything beyond what is specified here. After completing all changes, commit and push. Do NOT proceed to the next session.

Stop after this task. Do not continue to the next session.

## Verification

After all changes:

1. `python -m pytest engines/excerpting/tests/ -q --tb=short` → **570 + N new tests** passing (N ≈ 12 from PART D), 0 failed

2. Verify `_complete_division_tree` exists:
   ```
   grep -n 'def _complete_division_tree' engines/excerpting/src/phase1_assembly.py
   ```

3. Verify `run_phase1` uses completed tree:
   ```
   grep 'completed_tree' engines/excerpting/src/phase1_assembly.py
   ```
   Should show at least 5 occurrences (function def + 4 usage sites in run_phase1).

4. Integration test on ALL 5 packages — run this script and paste output:
   ```python
   import sys
   sys.path.insert(0, '.')
   from pathlib import Path
   from engines.normalization.contracts import ContentUnit, NormalizedManifest, NormalizedPackage
   from engines.excerpting.src.phase1_assembly import run_phase1
   from engines.excerpting.contracts import ExcerptingConfig

   packages_dir = Path('experiments/format_diversity_test/packages')
   config = ExcerptingConfig()

   for pkg_path in sorted(packages_dir.iterdir()):
       if not pkg_path.is_dir():
           continue
       manifest = NormalizedManifest.model_validate_json(
           (pkg_path / 'manifest.json').read_text(encoding='utf-8')
       )
       units = []
       with open(pkg_path / 'content.jsonl', encoding='utf-8') as fh:
           for line in fh:
               stripped = line.strip()
               if stripped:
                   units.append(ContentUnit.model_validate_json(stripped))
       pkg = NormalizedPackage(manifest=manifest, content_units=units)

       try:
           chunks, validation = run_phase1(pkg, config)
           statuses = {r['check']: r['status'] for r in validation}
           total_words = sum(c.word_count for c in chunks)
           print(f"{pkg_path.name:20s} PASS {len(chunks):3d} chunks, {total_words:6d} words, {statuses}")
       except ValueError as e:
           print(f"{pkg_path.name:20s} FAIL {str(e)[:120]}")
   ```
   **Expected:** All 5 packages show PASS with zero fatal checks.

5. Verify mock integration test still works:
   ```bash
   python scripts/run_integration_test.py \
     --mock \
     --package-path experiments/format_diversity_test/packages/ibn_aqil_v1 \
     --output-dir /tmp/preamble_test_run
   ```
   **Expected:** Completes without Phase 1 validation error. Output has phase1_chunks.json.

6. Verify no existing test broke:
   ```
   python -m pytest engines/excerpting/tests/ -q --tb=short 2>&1 | tail -3
   ```

## After This

- Architect reviews changes (3-pass review per REVIEW_PROTOCOL.md) in a NEW chat
- If ACCEPTED: run integration test script with ONE real LLM call to verify client wiring
- Then: Round 1 of LLM Integration Test Protocol (5 books, exhaustive review)
