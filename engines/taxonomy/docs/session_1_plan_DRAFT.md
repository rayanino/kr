# DRAFT — Taxonomy Build Session 1 (pending ChatGPT SPEC review)

## DO NOT DEPLOY AS NEXT.md UNTIL CHECKPOINT #3 IS COMPLETE

## Task: Foundation — Tree Loading + Routing + I/O

Build the deterministic skeleton of the taxonomy engine. After this session,
the engine can load trees, validate input, route excerpts based on scores,
and write output files — everything except the LLM calls.

## Scope

### 1. Tree Loader (`engines/taxonomy/src/tree_loader.py`)
- `detect_yaml_format(data) -> "v0" | "v1"`
- `normalize_v0(data) -> list[TreeNode]` — aqidah format
- `normalize_v1(data) -> list[TreeNode]` — nahw/sarf/balagha/imlaa format
- `load_tree(science_id, registry_path, override?) -> LoadedTree`
- `build_branch_view(tree) -> str` — formatted for Stage 1 prompt
- `build_leaf_view(leaves) -> str` — formatted for Stage 2 prompt
- Reads `taxonomy_registry.yaml` to find active tree
- Handles both v0 and v1 YAML formats

### 2. Input Validator (`engines/taxonomy/src/input_validator.py`)
- `validate_excerpt(excerpt_dict) -> (bool, list[str])` — checks required/expected fields
- `classify_excerpt_type(excerpt) -> ExcerptType` — editorial vs teaching
- Error codes: TAX_MISSING_REQUIRED_FIELD, TAX_MISSING_EXPECTED_FIELD

### 3. Routing Logic (`engines/taxonomy/src/router.py`)
- `route_excerpt(top_score, excerpt_type, config) -> PlacementRoute`
- Implements the threshold matrix from SPEC §4.A.3
- Teaching: ≥0.80 live, 0.50-0.79 staged, <0.50 unplaced
- Editorial: ≥0.85 live, 0.50-0.84 staged, <0.50 unplaced
- `detect_tie(top_score, second_score, threshold) -> bool`

### 4. Writer (`engines/taxonomy/src/writer.py`)
- `write_placed(excerpt, additions, science_id, base_path) -> Path`
- `write_staged(excerpt, additions, science_id, base_path) -> Path`
- `write_unplaced(excerpt, additions, science_id, base_path) -> Path`
- `write_pending(excerpt, additions, science_id, base_path) -> Path`
- All: UTF-8, create dirs, return path

### 5. Validator (`engines/taxonomy/src/validator.py`)
- `validate_leaf_exists(leaf_path, tree) -> bool`
- `verify_written_file(path, original_primary_text) -> bool`

### 6. Diagnostics (`engines/taxonomy/src/diagnostics.py`)
- `compute_batch_report(results, config, tree) -> BatchReport`
- `check_warnings(report) -> list[TaxonomyWarning]`

### 7. Tests
- Tree loading: all 5 trees parse, correct leaf counts, v0 format handled
- Input validation: missing required → error, missing expected → warning
- Routing: all 8 cells of the routing matrix tested
- Writer: files created in correct directories, UTF-8, primary_text byte-identical
- Diagnostics: warnings fire at correct thresholds
- Real data: ibn_aqil_v3 excerpts.jsonl parses without crash

## NOT In Scope (Session 2)
- LLM calls (Stage 1 and Stage 2)
- Prompt construction
- CLI adapter integration
- Gold baseline test
- End-to-end placement

## Done When
- [ ] All 5 tree YAML files load correctly (v0 + v1 formats)
- [ ] Leaf counts verified: 226, 226, 335, 30, 105
- [ ] Input validation handles missing required/expected fields
- [ ] Routing matrix produces correct route for all threshold combinations
- [ ] Writer creates files in correct directories with correct encoding
- [ ] Post-write validation catches byte-mismatch on primary_text
- [ ] Batch report computes correct statistics
- [ ] Warnings fire at correct thresholds
- [ ] Real ibn_aqil_v3 excerpts parse without crash
- [ ] All tests pass: `PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -x -q --tb=short`

## Files to Create
```
engines/taxonomy/
├── src/
│   ├── __init__.py
│   ├── tree_loader.py
│   ├── input_validator.py
│   ├── router.py
│   ├── writer.py
│   ├── validator.py
│   ├── diagnostics.py
│   └── engine.py          (skeleton only — calls placer in Session 2)
├── tests/
│   ├── __init__.py
│   ├── test_tree_loader.py
│   ├── test_input_validator.py
│   ├── test_router.py
│   ├── test_writer.py
│   ├── test_validator.py
│   ├── test_diagnostics.py
│   └── fixtures/
│       └── gold_baseline_nahw.yaml  (already created)
├── contracts_core.py       (already created)
├── CLAUDE.md              (already created)
├── SPEC.md                (already created)
└── docs/
    └── architecture.md    (already created)
```

## Do NOT
- Do NOT implement LLM calls or prompt construction
- Do NOT implement the placer module beyond a stub
- Do NOT implement anything beyond what is specified here
- After completing, commit, push, and STOP
- Do NOT proceed to Session 2
