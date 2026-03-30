# Taxonomy Engine — Module Architecture

## Data Flow

```
excerpts.jsonl ──→ engine.py ──→ tree_loader.py (load tree)
                      │
                      ├──→ placer.py (Stage 1: branch selection for large trees)
                      │         │
                      │         └──→ placer.py (Stage 2: leaf ranking)
                      │                   │
                      │                   └──→ routing (type-based threshold check)
                      │
                      ├──→ validator.py (leaf exists? write + verify byte-identical)
                      │
                      ├──→ writer.py (write to content/ or staged/ or unplaced/)
                      │
                      └──→ diagnostics.py (batch report + warnings)
```

## Modules

### engine.py — Orchestrator
- Entry point: `run(config: RunConfig) -> BatchReport`
- Loads tree via tree_loader
- Iterates excerpts from JSONL
- Calls placer for each excerpt
- Calls validator + writer for each result
- Calls diagnostics at end of batch
- Handles TAX_INVALID_SCIENCE (routes all to pending_no_tree)

### tree_loader.py — Tree Loading and Normalization
- `load_tree(science_id, registry_path, override_path?) -> LoadedTree`
- `detect_yaml_format(data) -> "v0" | "v1"`
- `normalize_v0(data) -> list[TreeNode]` — nested dict (_label/_leaf) to TreeNode
- `normalize_v1(data) -> list[TreeNode]` — nodes list to TreeNode
- `collect_leaves(nodes) -> list[TreeNode]`
- `build_branch_view(nodes) -> str` — formatted branch list for Stage 1 prompt
- `build_leaf_view(leaves) -> str` — formatted leaf list for Stage 2 prompt

### placer.py — Placement Algorithm
- `place_excerpt(excerpt, tree, adapter) -> PlacementResult`
- `run_stage1(excerpt, tree, adapter) -> list[TreeNode]` — candidate generation
- `run_stage2(excerpt, candidates, adapter) -> PlacementRanking` — candidate ranking
- `route_excerpt(ranking, excerpt_type) -> (PlacementRoute, leaf_id, confidence)`
- `classify_excerpt_type(excerpt) -> ExcerptType` — editorial vs teaching
- `build_stage1_prompt(excerpt, tree) -> list[dict]` — messages for CLI adapter
- `build_stage2_prompt(excerpt, candidates) -> list[dict]` — messages for CLI adapter

### validator.py — Placement Validation
- `validate_placement(leaf_path, tree) -> bool` — leaf exists check
- `verify_written_file(path, original_primary_text) -> bool` — byte-identical check

### writer.py — File Output
- `write_placed_excerpt(excerpt, additions, science_id, base_path) -> Path`
- `write_staged_excerpt(excerpt, additions, science_id, base_path) -> Path`
- `write_unplaced_excerpt(excerpt, additions, science_id, base_path) -> Path`
- `write_pending_excerpt(excerpt, additions, science_id, base_path) -> Path`
- All writers: create directories, UTF-8 encoding, return written path

### diagnostics.py — Batch Diagnostics
- `compute_batch_report(results, config, tree) -> BatchReport`
- `check_warnings(report) -> list[TaxonomyWarning]`
- `compute_median_confidence(confidences) -> float`
- `compute_editorial_placement_rate(results) -> float`

## Key Design Rules

1. **engine.py is the only entry point.** No module calls another module except through engine.py's orchestration.
2. **placer.py never writes files.** It returns placement decisions; writer.py executes them.
3. **All LLM calls go through the CLI adapter.** No direct subprocess calls.
4. **Every file write is followed by a read-back verification** (validator.py).
5. **All modules use contracts_core.py models.** No ad-hoc dicts for structured data.
