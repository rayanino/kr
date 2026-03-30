# NEXT — Taxonomy Engine Build Session 1: Deterministic Skeleton

## Current Position

- **Engine:** Taxonomy (محرك التصنيف)
- **Phase:** BUILD — first session
- **Test baseline:** 0 tests (empty test directory)
- **SPEC status:** Finalized after 2 ChatGPT adversarial reviews (551 lines, core-only)
- **What exists:** `contracts_core.py`, `docs/architecture.md`, `CLAUDE.md`, `SPEC.md`, `tests/fixtures/gold_baseline_nahw.yaml`, placeholder `src/tracer.py`

## What to Do

Build the deterministic skeleton of the taxonomy engine. After this session, the engine can load trees, validate input, route excerpts based on scores, write output files, and compute batch diagnostics — **everything except the LLM calls**.

Session 2 (separate handoff) will add LLM integration.

## Context

Read `engines/taxonomy/CLAUDE.md` for build constraints (Arabic text handling, D-023 provenance, error codes, encoding rules). Read `engines/taxonomy/SPEC.md` for the authoritative specification. Read `engines/taxonomy/docs/architecture.md` for module structure.

## Read First (in order)

1. `engines/taxonomy/CLAUDE.md` — build guide, constraints, key files
2. `engines/taxonomy/SPEC.md` — §2 (input), §3 (output), §4.A.1 (tree loading), §4.A.3 (routing), §4.A.4 (validation), §4.A.6 (diagnostics), §6 (errors), §7 (config)
3. `engines/taxonomy/contracts_core.py` — Pydantic models and dataclasses
4. `engines/taxonomy/docs/architecture.md` — module structure and data flow
5. `library/sciences/taxonomy_registry.yaml` — registry format
6. `library/sciences/nahw/tree.yaml` — v1 tree format example (lines 1–80)
7. `library/sciences/aqidah/tree.yaml` — v0 tree format example (lines 1–40)
8. `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl` — real excerpt format (line 1)
9. `reference/archive/abd_code/taxonomy/evolve_taxonomy.py` — function `_detect_yaml_format` (line ~1454) for format detection reference

## What to Build

### Module 1: `engines/taxonomy/src/tree_loader.py`

**Purpose:** Load tree YAML files and produce a normalized internal representation.

Functions:
- `detect_yaml_format(data: dict) -> str` — returns `"v0"` or `"v1"`. Rule: if top-level key is `"taxonomy"` with a `"nodes"` array, it's v1; else v0.
- `_normalize_v0(data: dict) -> tuple[str, list[TreeNode]]` — parses aqidah-style nested dict. The top-level key (e.g., `aqidah`) is an envelope — NOT included in paths. `_label` → title, `_leaf: true` → leaf. Keys starting with `_` (except `_label`, `_leaf`) are metadata. Keys starting with `__` (e.g., `__overview`) ARE child nodes.
- `_normalize_v1(data: dict) -> tuple[str, list[TreeNode]]` — parses nahw/sarf/balagha/imlaa style. Key mapping: YAML `leaf: true` → TreeNode `is_leaf=True`. **Non-leaf nodes omit the `leaf` field entirely** — use `node.get("leaf", False)`. YAML `id` → TreeNode `id`. YAML `title` → TreeNode `title`.
- `load_tree(science_id: str, registry_path: Path, override_path: Path | None = None) -> LoadedTree` — reads registry, finds active tree, loads YAML, normalizes, collects leaves, builds `leaf_by_path`, asserts leaf path uniqueness.
- `build_branch_view(tree: LoadedTree) -> str` — formatted branch-level text for Stage 1 LLM prompt (used in Session 2).
- `build_leaf_view(leaves: list[TreeNode]) -> str` — formatted leaf list for Stage 2 LLM prompt (used in Session 2).

Use `TreeNode` and `LoadedTree` from `contracts_core.py`.

**Critical edge cases:**
- v0 `__overview` keys must be parsed as real leaf nodes (not skipped as metadata)
- v0 root key is envelope, not included in paths
- Leaf path uniqueness: assert after loading, raise `TAX_TREE_LOAD_ERROR` if duplicate paths found
- Expected leaf counts: nahw=226, sarf=226, balagha=335, aqidah=30, imlaa=105

### Module 2: `engines/taxonomy/src/input_validator.py`

**Purpose:** Validate incoming excerpts and classify their type.

Functions:
- `validate_excerpt(excerpt: dict) -> tuple[bool, list[str], list[str]]` — returns (is_valid, errors, warnings). Checks required fields: `excerpt_id`, `source_id`, `primary_text`, `excerpt_topic` (must be non-empty list). Checks expected fields: `description_arabic`, `primary_function`, `content_types`, `div_path`, `terminology_variants`, `primary_author_layer`, `quoted_scholars`, `school`.
- `classify_excerpt_type(excerpt: dict) -> ExcerptType` — returns `ALWAYS_STAGED` if primary_function ∈ {`structural_transition`, `cross_reference`}; `EDITORIAL` if primary_function == `editorial_note` or if primary_function is absent/null/unknown; `TEACHING` otherwise.

Use `ExcerptType` from `contracts_core.py`.

### Module 3: `engines/taxonomy/src/router.py`

**Purpose:** Route excerpts based on placement score and type.

Functions:
- `route_excerpt(top_score: float, second_score: float | None, excerpt_type: ExcerptType, config: dict) -> PlacementRoute` — implements the routing matrix from SPEC §4.A.3:
  - `ALWAYS_STAGED` type: if score ≥ 0.50 → `STAGED_FRONT_MATTER`; if < 0.50 → `UNPLACED`
  - `EDITORIAL` type: if score ≥ 0.85 → `LIVE`; if 0.50–0.84 → `STAGED_FRONT_MATTER`; if < 0.50 → `UNPLACED`
  - `TEACHING` type: if score ≥ 0.80 → `LIVE`; if 0.50–0.79 → `STAGED_LOW_CONFIDENCE`; if < 0.50 → `UNPLACED`
  - **Tie override:** if second_score is not None AND `top_score - second_score < tie_threshold (0.10)` AND `top_score >= 0.50` → force `STAGED_LOW_CONFIDENCE` or `STAGED_FRONT_MATTER` (based on type) regardless of score.

Use `PlacementRoute` and `ExcerptType` from `contracts_core.py`.

### Module 4: `engines/taxonomy/src/writer.py`

**Purpose:** Write output files in correct directories.

Functions:
- `write_output(excerpt: dict, additions: dict, route: PlacementRoute, science_id: str, base_path: Path) -> Path` — merges `{**excerpt, **additions}`, writes to the correct directory based on route:
  - `LIVE` → `{base_path}/content/{leaf_path}/excerpts/{excerpt_id}.json`
  - `STAGED_LOW_CONFIDENCE` or `STAGED_FRONT_MATTER` → `{base_path}/staged/{leaf_path}/excerpts/{excerpt_id}.json`
  - `UNPLACED` → `{base_path}/unplaced/{excerpt_id}.json`
  - `PENDING_NO_TREE` → `{base_path}/pending_no_tree/{science_id}/{excerpt_id}.json`
- `leaf_path` contains `/` separators (e.g., `almajrurat/huruf_aljar/ma3ani_huruf_aljar`) — these become nested directories. Use `Path(base_path) / "content" / leaf_path / "excerpts" / f"{excerpt_id}.json"` for correct cross-platform path construction.
- Creates parent directories as needed (`parents=True, exist_ok=True`). All files: `encoding="utf-8"`, `ensure_ascii=False`, `indent=2`.
- Returns the path of the written file.

**Collision policy:** additions overwrite any pre-existing keys in the excerpt dict (SPEC §3.6).

### Module 5: `engines/taxonomy/src/validator.py`

**Purpose:** Post-placement validation.

Functions:
- `validate_leaf_exists(leaf_path: str, tree: LoadedTree) -> bool` — checks `leaf_by_path`.
- `verify_written_file(written_path: Path, original_primary_text: str) -> bool` — reads the written file back, parses JSON, checks `primary_text` is byte-identical. Returns False if any step fails.

### Module 6: `engines/taxonomy/src/diagnostics.py`

**Purpose:** Batch report and warnings.

Functions:
- `compute_batch_report(results: list[dict], config: RunConfig, tree: LoadedTree | None) -> BatchReport` — computes all batch report fields from SPEC §3.5.
- `check_warnings(report: BatchReport) -> list[str]` — evaluates 4 warning conditions:
  - `TAX_POSSIBLE_SCIENCE_MISMATCH`: median confidence < 0.65
  - `TAX_HIGH_UNPLACEMENT_RATE`: > 40% unplaced
  - `TAX_LEAF_CONCENTRATION`: any leaf > 25% of placements
  - `TAX_HIGH_EDITORIAL_PLACEMENT`: > 50% of editorial excerpts in live tree

Use `BatchReport`, `TaxonomyWarning` from `contracts_core.py`.

### Module 7: `engines/taxonomy/src/engine.py` (skeleton only)

**Purpose:** Main entry point. Full implementation in Session 2.

Functions:
- `run(config: RunConfig) -> BatchReport` — skeleton that:
  1. Loads tree via tree_loader (or routes to pending_no_tree if invalid science)
  2. Reads JSONL line by line
  3. Validates each excerpt via input_validator
  4. **Placeholder:** calls a `place_excerpt()` stub that raises `NotImplementedError` (LLM integration in Session 2)
  5. Routes via router
  6. Writes via writer
  7. Validates via validator
  8. Computes batch report via diagnostics

The `place_excerpt()` stub in Session 1 accepts a mock placement result for testing. Interface: `place_excerpt(excerpt: dict, tree: LoadedTree, placer=None) -> dict` where the return dict has `{"leaf_path": str, "score": float, "second_score": float|None, "reasoning": str, "primary_topic_used": str}`. In Session 1, `placer` is a callable mock that returns this dict. In Session 2, `placer` calls the real LLM via CLI adapter.

### Tests: `engines/taxonomy/tests/`

Create these test files:

**`test_tree_loader.py`:**
- v1 format: load nahw, verify 226 leaves
- v1 format: load sarf, verify 226 leaves
- v1 format: load balagha, verify 335 leaves
- v1 format: load imlaa, verify 105 leaves
- v0 format: load aqidah, verify 30 leaves
- v0 `__overview` nodes parsed as leaves (not skipped)
- v0 root key excluded from paths (path starts at children of root)
- Leaf path uniqueness enforced across all 5 trees
- Spot-check known paths exist: `leaf_by_path["almajrurat/huruf_aljar/ma3ani_huruf_aljar"]` in nahw, `leaf_by_path["al_iman_billah/asma_wa_sifat/sifat_dhatiyyah/__overview"]` in aqidah
- Registry relpath resolution: `taxonomy_registry.yaml` stores relpaths relative to `library/sciences/` (e.g., `nahw/tree.yaml` → `library/sciences/nahw/tree.yaml`)
- Invalid YAML raises TAX_TREE_LOAD_ERROR
- `leaf_by_path` lookup works for spot-checked leaves
- `build_branch_view` and `build_leaf_view` produce non-empty strings

**`test_input_validator.py`:**
- Missing `excerpt_id` → error, invalid
- Missing `primary_text` → error, invalid
- Missing `excerpt_topic` → error, invalid
- Empty `excerpt_topic: []` → error, invalid
- Missing `description_arabic` → warning, valid
- All fields present → no errors, no warnings
- `primary_function: editorial_note` → ExcerptType.EDITORIAL
- `primary_function: structural_transition` → ExcerptType.ALWAYS_STAGED
- `primary_function: cross_reference` → ExcerptType.ALWAYS_STAGED
- `primary_function: rule_statement` → ExcerptType.TEACHING
- `primary_function: None` → ExcerptType.EDITORIAL (safe default)
- `primary_function` absent → ExcerptType.EDITORIAL (safe default)

**`test_router.py`:**
- Teaching, score 0.90 → LIVE
- Teaching, score 0.70 → STAGED_LOW_CONFIDENCE
- Teaching, score 0.40 → UNPLACED
- Editorial, score 0.90 → LIVE
- Editorial, score 0.80 → STAGED_FRONT_MATTER
- Editorial, score 0.40 → UNPLACED
- Always-staged, score 0.95 → STAGED_FRONT_MATTER (never live!)
- Always-staged, score 0.40 → UNPLACED
- Teaching, score 0.85 with tie (second=0.82) → STAGED (tie override)
- Teaching, score 0.85 no tie (second=0.60) → LIVE (no tie)
- Boundary: teaching score exactly 0.80 → LIVE
- Boundary: editorial score exactly 0.85 → LIVE
- Boundary: teaching score exactly 0.50 → STAGED

**`test_writer.py`:**
- LIVE route writes to `content/{leaf}/excerpts/{id}.json`
- STAGED writes to `staged/{leaf}/excerpts/{id}.json`
- UNPLACED writes to `unplaced/{id}.json`
- PENDING_NO_TREE writes to `pending_no_tree/{science_id}/{id}.json`
- Written file is valid JSON
- `primary_text` byte-identical after write+read (use Arabic text with diacritics: `"بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"`)
- `ensure_ascii=False` verified (Arabic readable, not escaped)
- Original excerpt fields preserved (D-023)
- Taxonomy additions present in output
- Collision: if excerpt has `lifecycle_stage`, taxonomy value overwrites

**`test_validator.py`:**
- Known leaf path → validates
- Unknown leaf path → fails
- Byte-identical primary_text → passes
- Corrupted primary_text → fails

**`test_diagnostics.py`:**
- Median confidence < 0.65 triggers TAX_POSSIBLE_SCIENCE_MISMATCH
- Unplacement > 40% triggers TAX_HIGH_UNPLACEMENT_RATE
- Leaf > 25% triggers TAX_LEAF_CONCENTRATION
- Editorial live > 50% triggers TAX_HIGH_EDITORIAL_PLACEMENT
- All thresholds just below → no warning
- Batch report counts match input data

**`test_real_data.py`:**
- Load `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl`
- All 25 excerpts pass validation (required fields present)
- No crash on real data shapes (null fields, empty lists, Arabic text)

## Design Decisions (CC must follow, not improvise)

1. **Tree format detection:** `"taxonomy"` key with `"nodes"` → v1. Everything else → v0. (SPEC §4.A.1)
2. **v0 root key:** Envelope only. NOT in paths. Paths start at children. (SPEC §4.A.1)
3. **v0 underscore handling:** `_label` and `_leaf` are metadata. `__overview` is a real node. All other `_`-prefixed keys are metadata. (SPEC §4.A.1)
4. **Missing primary_function:** Defaults to EDITORIAL type, not TEACHING. (SPEC §4.A.3)
5. **Ties force staging:** If top two scores within 0.10 AND both ≥ 0.50 → always staged. (SPEC §4.A.3)
6. **Always-staged types:** `structural_transition` and `cross_reference` are NEVER routed to live. (SPEC §4.A.3)
7. **Serialization:** `json.dumps(..., ensure_ascii=False, indent=2)` with `encoding="utf-8"`. (SPEC §3.6)
8. **Collision on merge:** `{**original_excerpt, **taxonomy_additions}` — taxonomy wins on key conflicts. (SPEC §3.6)

## Do NOT Do

- Do NOT implement LLM calls, prompt construction, or the `placer.py` module (Session 2)
- Do NOT implement the CLI adapter integration (Session 2)
- Do NOT modify any files in `library/sciences/` or `shared/llm/`
- Do NOT implement anything beyond what is specified here
- Do NOT rename or restructure the existing `contracts_core.py` (use it as-is)
- Do NOT import from `engines/taxonomy/contracts.py` — that is the old overscoped file (491 lines). Use ONLY `contracts_core.py` for all models and types.
- After completing, commit, push, and STOP. Do NOT proceed to Session 2.

## Verification (Definition of Done)

- [ ] All 5 tree YAML files load correctly (v0 and v1 formats)
- [ ] Leaf counts verified: nahw=226, sarf=226, balagha=335, aqidah=30, imlaa=105
- [ ] v0 `__overview` nodes parsed as leaves
- [ ] v0 root key excluded from paths
- [ ] Input validation handles all required/expected field combinations
- [ ] Type classification matches SPEC §4.A.3 for all primary_function values
- [ ] Routing matrix produces correct route for all 13 test cases in test_router.py
- [ ] Writer creates files in correct directories with correct encoding
- [ ] Post-write validation catches byte-mismatch on Arabic primary_text
- [ ] Batch diagnostics compute correctly and warnings fire at thresholds
- [ ] Real ibn_aqil_v3 excerpts parse without crash
- [ ] All tests pass: `PYTHONPATH=. python -m pytest engines/taxonomy/tests/ -x -q --tb=short`
- [ ] Test count: ≥ 50 tests passing (0 baseline → 50+ target)

## After This

Session 2 will add: `placer.py` (Stage 1 + Stage 2 LLM calls), CLI adapter integration, prompt construction, end-to-end placement with mock LLM, gold baseline test with real LLM.
