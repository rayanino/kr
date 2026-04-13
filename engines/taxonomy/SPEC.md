# Taxonomy Engine — محرك التصنيف — Core v1 Specification

**Status:** Implementation-ready (ChatGPT checkpoints #1 and #3 incorporated)
**Scope:** Core placement only — 24 capabilities. 42 deferred to Stage 2.
**Governing documents:** `CORE_EXTRACTION.md` (classification), `REWRITE_ANALYSIS.md` (design decisions), `SPEC_FULL_ORIGINAL.md` (full SPEC archive)

---

## 1. Purpose and Scope

The taxonomy engine places excerpts at leaves in existing science trees. That is its only v1 responsibility.

**What v1 does:**
1. Reads existing science trees from `library/sciences/{science_id}/tree.yaml`
2. Receives excerpts as JSONL from the excerpting engine
3. Classifies each excerpt to a candidate leaf via LLM topic matching
4. Ranks candidate leaves via LLM scoring
5. Routes each excerpt to one of: **live placement**, **staged** (low confidence or front-matter), **unplaced**, or **pending-no-tree**
6. Validates each placement (leaf exists, file written, primary_text byte-identical)
7. Logs placement reasoning, confidence, and batch diagnostics

**What v1 does NOT do (all deferred to Stage 2):**
- Tree construction, evolution, rollback, or modification
- Coverage analytics or gap detection
- Cross-science link management
- Prerequisite edge management
- Terminology synonym management
- Embedding-based candidate generation
- Multi-model consensus placement
- Human gate queue infrastructure
- Scholarly landscape or disagreement topology

**Phase classification:** Phase 2 (source-agnostic, below the normalization boundary). The taxonomy engine receives excerpts that carry no trace of their original source format.

---

## 2. Input Contract

### 2.1 Excerpt Input

Excerpts arrive as **JSONL files** — one JSON object per line, matching the excerpting engine's output format. No wrapper object.

**Required fields — rejection on absence (`TAX_MISSING_REQUIRED_FIELD`):**

| Field | Type | Description |
|-------|------|-------------|
| `excerpt_id` | `str` | Non-empty, format `exc_{source_id}_{...}` |
| `source_id` | `str` | Non-empty |
| `primary_text` | `str` | Non-empty — the actual excerpt text |
| `excerpt_topic` | `list[str]` | Non-empty — topic labels from excerpting engine |

**Expected fields — warning on absence (`TAX_MISSING_EXPECTED_FIELD`), excerpt proceeds with degraded placement quality:**

| Field | Type | Used by |
|-------|------|---------|
| `description_arabic` | `str` | Placement prompt — richest semantic signal |
| `primary_function` | `str` | Type-based routing (editorial vs teaching) |
| `content_types` | `list[str]` | Placement context |
| `div_path` | `list[str]` | Structural heading path — disambiguation context |
| `terminology_variants` | `list[dict]` | Additional search terms |
| `primary_author_layer` | `dict` | Provenance passthrough |
| `quoted_scholars` | `list[dict]` | Provenance passthrough |
| `school` | `str or null` | Provenance passthrough |

**Fields intentionally NOT required (engines not built):**
- `passage_id` — passaging engine not built
- `atom_ids` — atomization engine not built
- `lifecycle_stage` — taxonomy assumes all incoming excerpts are drafts
- `science_id` — comes from run configuration (§2.2), not per-excerpt
- `proposed_leaf` — excerpting engine doesn't produce this; if present, accepted as first candidate

### 2.2 Run Configuration

Each taxonomy run is parameterized by a configuration object:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `science_id` | `str` | Yes | Which science tree to place against. Must match a registered science in `taxonomy_registry.yaml`. |
| `input_path` | `Path` | Yes | Path to the excerpts JSONL file |
| `batch_id` | `str` | Yes | Unique identifier for this run (for diagnostics) |
| `tree_override_path` | `Path or None` | No | Override the registry's active tree with a specific tree file. For testing. |

The taxonomy engine processes **one science at a time**. All excerpts in a batch are placed against the same tree.

[EXTENSION HOOK] — When books spanning multiple sciences are common, add a per-excerpt science classification stage. Core must not assume science_id is always correct — the batch diagnostic (§4.A.6) detects systematic mismatches.

### 2.3 Science Tree Files

Trees are stored as YAML at `library/sciences/{science_id}/tree.yaml`. The `taxonomy_registry.yaml` maps science IDs to active tree versions.

**Two YAML schemas exist in the repo:**

**v1 format** (nahw, sarf, balagha, imlaa):
```yaml
taxonomy:
  id: nahw_v1_0
  title: علم النحو
  nodes:
  - id: muqaddimat
    title: مقدمات علم النحو
    children:
    - id: ta3rif_alnahw
      title: تعريف النحو
      leaf: true
```

**v0 format** (aqidah):
```yaml
aqidah:
  al_iman_billah:
    _label: "الإيمان بالله"
    manhaj:
      _label: "المنهج"
      _leaf: true
```

The taxonomy engine's `TreeLoader` (§4.A.1) normalizes both formats into a single internal representation at load time. **The source YAML files are never modified.**

---

## 3. Output Contract

The taxonomy engine produces five categories of output. All are written under `library/sciences/{science_id}/`.

### 3.1 Placed Excerpts (Live)

**Condition:** Placement confidence ≥ 0.80 for teaching content, or ≥ 0.85 for editorial/structural content (§4.A.3).

**Location:** `content/{leaf_path}/excerpts/{excerpt_id}.json`

Each placed excerpt is the **complete original excerpt object** (all upstream fields preserved per D-023) extended with:

| Field | Type | Description |
|-------|------|-------------|
| `lifecycle_stage` | `str` | `"placed"` — immutable once written |
| `confirmed_leaf` | `str` | Leaf path in the tree (e.g., `almajrurat/huruf_aljar/ma3ani_huruf_aljar`) |
| `placement_confidence` | `float` | 0.0–1.0, from Stage 2 ranking |
| `placed_utc` | `str` | ISO datetime of placement |
| `taxonomy_version_at_placement` | `str` | Tree version from registry (e.g., `nahw_v1_0`) |
| `placement_reasoning` | `str` | LLM-generated explanation of leaf choice |
| `primary_topic_used` | `str` | Which of the excerpt's topics drove the placement |
| `review_metadata` | `dict` | `{"review_outcome": "auto_approved"}` for v1 |
| `placement_route` | `str` | `"live"` |
| `tie_detected` | `bool` | True if top two candidates scored within 0.10 |

### 3.2 Staged Excerpts (Low Confidence or Front Matter)

**Condition:** Confidence 0.50–0.79 for teaching content, or 0.50–0.84 for editorial/structural content.

**Location:** `staged/{leaf_path}/excerpts/{excerpt_id}.json`

Same fields as placed excerpts, except:
- `lifecycle_stage`: `"staged"`
- `placement_route`: `"staged_low_confidence"` or `"staged_front_matter"`

Staged excerpts are NOT in the live content tree. They are held for evaluation-phase review. Correct ones are promoted to live placement; incorrect ones are reclassified or moved to unplaced.

### 3.3 Unplaced Excerpts

**Condition:** No candidate scores ≥ 0.50.

**Location:** `unplaced/{excerpt_id}.json`

Contains the complete original excerpt object extended with:

| Field | Type | Description |
|-------|------|-------------|
| `lifecycle_stage` | `str` | `"unplaced"` |
| `unplaced_reason` | `str` | E.g., "No candidate scored ≥0.5" or "Stage 1: no matching branch" |
| `best_candidates` | `list[dict]` | Top 3 candidates with leaf_path, score, reasoning. Empty list `[]` if Stage 1 returned no_match. |
| `placement_route` | `str` | `"unplaced"` |

### 3.4 Pending-No-Tree Excerpts

**Condition:** The `science_id` from run configuration does not have an active tree in the registry.

**Location:** `pending_no_tree/{science_id}/{excerpt_id}.json`

Contains the complete original excerpt object extended with:
- `lifecycle_stage`: `"pending_no_tree"`
- `declared_science_id`: the science_id that was requested
- `pending_since_utc`: ISO datetime

These excerpts are re-processable once a tree is created. They are NOT lumped with unplaced excerpts — that distinction preserves diagnostic clarity and the clean re-run path.

### 3.5 Batch Report

**Location:** `batch_reports/{batch_id}.json`

| Field | Type | Description |
|-------|------|-------------|
| `batch_id` | `str` | Run identifier |
| `science_id` | `str` | Science processed |
| `tree_version` | `str` | Active tree version used |
| `timestamp_utc` | `str` | When the batch ran |
| `total_excerpts` | `int` | Input count |
| `placed_count` | `int` | Live placements |
| `staged_count` | `int` | Staged placements (low confidence + front matter) |
| `unplaced_count` | `int` | Unplaced excerpts |
| `pending_no_tree_count` | `int` | Pending (should be 0 if tree exists) |
| `confidence_distribution` | `dict` | Histogram of placement confidences |
| `median_confidence` | `float` | Batch median — science mismatch signal |
| `leaf_distribution` | `dict[str, int]` | Excerpts per leaf (live + staged) |
| `editorial_placement_rate` | `float` | Fraction of editorial excerpts that reached live tree |
| `warnings` | `list[str]` | Batch-level warnings (see §4.A.6) |

### 3.6 Provenance Preservation (D-023)

The taxonomy engine **adds** fields to excerpts; it **never strips** upstream fields. The placed/staged/unplaced excerpt JSON contains every field from the original input JSONL line, plus the taxonomy-added fields. Implementation: `{**original_excerpt, **placement_additions}`.

**Collision policy:** If the original excerpt already contains a key that taxonomy adds (e.g., `lifecycle_stage`), the taxonomy value **overwrites** the upstream value. This is correct because upstream excerpts should not have taxonomy-specific fields; their presence indicates a pipeline error or re-processing scenario where the latest taxonomy result is authoritative.

**Serialization invariants:** All output JSON files must be written with:
- `ensure_ascii=False` — Arabic text must appear as readable Arabic, not `\uXXXX` escapes
- `indent=2` — human-readable for review and debugging
- `encoding="utf-8"` — mandatory, no fallback to system default

---

## 4. Processing Specification

### §4.A.1 — Tree Loading

The `TreeLoader` reads a tree YAML file and produces a uniform in-memory structure.

**Format detection:** If the top-level key is `"taxonomy"` with a `"nodes"` array, it is v1 format. Otherwise, it is v0 format (nested dict with `_label`/`_leaf` keys). This logic matches the detection in the archived ABD code (`reference/archive/abd_code/taxonomy/evolve_taxonomy.py`, function `_detect_yaml_format`).

**Internal representation:**
```python
@dataclass
class TreeNode:
    id: str           # ASCII slug, unique within tree
    title: str        # Arabic display name
    children: list[TreeNode]
    is_leaf: bool
    path: str         # Full path from root (e.g., "almajrurat/huruf_aljar/ma3ani_huruf_aljar")
    parent_title: str # Parent node's Arabic title (for placement context)
```

**v0 normalization rules:**
- The top-level YAML key (e.g., `aqidah`) is an **envelope**, not a tree node. It is NOT included in leaf paths. Paths begin at its children. Example: the leaf at `aqidah → al_iman_billah → asma_wa_sifat → manhaj...` gets path `al_iman_billah/asma_wa_sifat/manhaj_ahl_al_sunna_fi_al_sifat`.
- Each dict key becomes the node `id`
- `_label` value becomes the node `title`
- `_leaf: true` marks the node as a leaf
- Keys starting with `_` (except `_label`, `_leaf`) are metadata, not child nodes
- Keys starting with `__` (e.g., `__overview`) ARE child nodes — the double underscore is a naming convention, not a skip signal
- All other non-underscore keys are child nodes

**Leaf path uniqueness invariant:** After loading, every leaf must have a unique `path`. The TreeLoader asserts this at load time — duplicate paths indicate a tree authoring error and raise `TAX_TREE_LOAD_ERROR`.

**TreeLoader outputs:**
- `tree_version: str` — from YAML header (v1: `taxonomy.id`) or registry
- `all_leaves: list[TreeNode]` — flat list of all leaf nodes with paths
- `branches: list[TreeNode]` — top-level nodes (for hierarchical search)
- `leaf_count: int`
- `leaf_by_path: dict[str, TreeNode]` — path-to-node lookup for validation

**Error:** If the YAML fails to parse or contains zero leaves, raise `TAX_TREE_LOAD_ERROR` (fatal for the batch).

### §4.A.2 — Placement Algorithm

Placement uses a two-stage LLM approach: candidate generation, then candidate ranking.

#### Stage 1: Candidate Generation

**For trees with ≤ 200 leaves** (aqidah: 30, imlaa: 105): Skip Stage 1. All leaves go directly to Stage 2 as candidates.

**For trees with > 200 leaves** (nahw: 226, sarf: 226, balagha: 335): Hierarchical search — select top branches, then search leaves within.

**Stage 1 LLM call:**

The prompt shows the excerpt's topic and description alongside the tree's branch-level structure (top-level nodes with their first-level children for context). The LLM selects the 3 most likely branches.

**Stage 1 response model:**
```python
class BranchSelection(BaseModel):
    selected_branches: list[str]  # 1-3 branch IDs, ranked by likelihood
    no_match: bool = False        # True if no branch fits at all
```

If `no_match` is True, the excerpt goes directly to unplaced with reason `"Stage 1: no matching branch"`.

**Candidate set construction:** All leaves within the selected branches become Stage 2 candidates. If `proposed_leaf` is present on the excerpt and valid, it is added to the candidate set regardless of branch selection (ensures the excerpting engine's hint is always evaluated).

[EXTENSION HOOK] — Embedding similarity adds candidates from a pluggable source. Core's candidate set must accept additional candidates via a simple `extend()` interface.

#### Stage 2: Candidate Ranking

All candidates from Stage 1 (or all leaves for small trees) are scored in a single LLM call.

**Stage 2 input context includes:**
- `excerpt_topic` (all topics, joined by ` / `)
- `description_arabic`
- `primary_text` — full text if shorter than `primary_text_char_limit` (default 3000 chars); first `primary_text_char_limit` characters if longer
- `primary_function`
- `content_types`
- `div_path` (structural heading path from the source book)
- For each candidate leaf: `leaf_path` (full path from root), `leaf_title`, `parent_title`

**The prompt instructs the LLM to:**
1. Score each candidate leaf 0.0–1.0 on how well the excerpt fits
2. Prefer specific leaves over broad ones when the excerpt's content justifies specificity
3. Score LOW for book introductions and editorial notes that do not teach a specific science topic
4. Identify which of the excerpt's topics is primary for placement

**Stage 2 response model:**
```python
class LeafScore(BaseModel):
    leaf_path: str  # Full path from root (e.g., "almajrurat/huruf_aljar/ma3ani_huruf_aljar")
    score: float  # 0.0-1.0
    reasoning: str

class PlacementRanking(BaseModel):
    rankings: list[LeafScore]
    primary_topic_used: str  # Which topic drove the placement decision
```

The highest-scoring candidate is selected.

**LLM routing:** All calls go through the CLI adapter (`shared/llm/cli_adapter.py`). Model: `anthropic/claude-opus-4` (per project axiom: always use the best model). Timeout: 600 seconds. Retries: 2 (3 total attempts).

### §4.A.3 — Placement Routing

After Stage 2 produces a scored candidate list, the excerpt is routed based on the top score and the excerpt type.

**Type detection:** An excerpt's routing category is determined by `primary_function`:
- **Always-staged types:** `structural_transition` and `cross_reference` — these are navigation/structural text, not knowledge content. They always go to staged regardless of score.
- **Editorial type:** `editorial_note` — eligible for live at ≥ 0.85, staged below.
- **Teaching type:** All other known values (e.g., `rule_statement`, `opinion_statement`, `definition`, `evidence_hadith`, `condition_exception`).
- **Missing/null/unknown:** If `primary_function` is absent, null, or not recognized, the excerpt is treated as **editorial** (stricter threshold). This is a safe default — it prevents unclassified excerpts from entering the live tree at the lower teaching threshold.

**Routing matrix:**

| Excerpt Type | Top Score | Route | Output Directory |
|---|---|---|---|
| Teaching | ≥ 0.80 | **Live** | `content/{leaf}/excerpts/` |
| Teaching | 0.50–0.79 | **Staged** (low confidence) | `staged/{leaf}/excerpts/` |
| Teaching | < 0.50 | **Unplaced** | `unplaced/` |
| Editorial (editorial_note) | ≥ 0.85 | **Live** | `content/{leaf}/excerpts/` |
| Editorial (editorial_note) | 0.50–0.84 | **Staged** (front matter) | `staged/{leaf}/excerpts/` |
| Editorial (editorial_note) | < 0.50 | **Unplaced** | `unplaced/` |
| Always-staged (structural_transition, cross_reference) | Any | **Staged** (front matter) | `staged/{leaf}/excerpts/` |
| Always-staged | < 0.50 | **Unplaced** | `unplaced/` |

**Tie handling:** If the top two candidates score within 0.10 of each other and both score ≥ 0.50, the excerpt is **forced to staged** regardless of the score or type. Ties are a canonical uncertainty signal. `tie_detected: true` is recorded in the metadata.

### §4.A.4 — Placement Validation

After routing determines the target leaf, before writing the file:

1. **Leaf existence check:** Verify `confirmed_leaf` resolves to a real leaf in `leaf_by_path`. If not: `TAX_PLACEMENT_INTEGRITY_ERROR` (fatal for this excerpt).

2. **File write:** Write the placed/staged excerpt JSON to the target path. Create parent directories as needed. Encoding: **UTF-8** (mandatory — cp1252 silent failures are a known risk on Windows/WSL2).

3. **Post-write fidelity check:** Re-read the written file, parse the JSON, and verify `primary_text` is **byte-identical** to the input. If not: `TAX_PLACEMENT_INTEGRITY_ERROR` (fatal — delete the written file, log the error, move excerpt to unplaced).

This three-step validation prevents T-1 (Arabic text corruption). A placement that corrupts the text is worse than no placement.

### §4.A.5 — Primary Topic Determination

When an excerpt has multiple topics in `excerpt_topic`, the placement algorithm uses ALL topics as context in both Stage 1 and Stage 2 prompts. The LLM naturally focuses on the most relevant topic for the target tree.

The Stage 2 response includes `primary_topic_used` — which topic the LLM actually used for placement. This supports auditability.

No explicit "primary topic extraction" step is needed because:
- Empirical analysis of the 67 real excerpts shows most multi-topic entries have topics converging on the same tree area (sub-topics within one main topic)
- The `description_arabic` field provides strong disambiguation
- The Stage 2 prompt explicitly asks the LLM to consider specificity

### §4.A.6 — Batch Diagnostics

After all excerpts in a batch are processed, the engine computes the batch report (§3.5) and evaluates these warning conditions:

| Warning | Condition | Likely Cause |
|---|---|---|
| `TAX_POSSIBLE_SCIENCE_MISMATCH` | Median placement confidence < 0.65 | Wrong science_id for this batch |
| `TAX_HIGH_UNPLACEMENT_RATE` | > 40% of excerpts unplaced | Wrong science, tree gaps, or excerpting issues |
| `TAX_LEAF_CONCENTRATION` | Any leaf received > 25% of all placements | Tree granularity issue — leaf may be too broad |
| `TAX_HIGH_EDITORIAL_PLACEMENT` | > 50% of editorial excerpts reached live tree | Editorial threshold may be too permissive |

---

## 5. Validation and Quality

### 5.1 Self-Validation

Every placement undergoes the three-step validation in §4.A.4. No file is left in an inconsistent state — if any step fails, the excerpt is routed to unplaced with the failure recorded.

### 5.2 Threat Prevention (from reference/KNOWLEDGE_INTEGRITY.md)

**T-1 (Arabic text corruption):** Prevented by the post-write byte-identical check on `primary_text`. The taxonomy engine never modifies `primary_text` — it copies the field verbatim.

**T-3 (Misplacement — excerpt at wrong leaf):** Mitigated by:
- Two-stage LLM placement with ranked candidates
- Confidence thresholds with staging gate (uncertain placements don't enter live tree)
- Type-based routing (editorial excerpts face higher threshold)
- Batch diagnostics detecting systematic problems
- Placement reasoning logged for every excerpt (auditability)

**T-6 (Wrong science assignment):** Mitigated by:
- Batch median confidence diagnostic (TAX_POSSIBLE_SCIENCE_MISMATCH)
- TAX_PENDING_NO_TREE for unregistered sciences
- [EXTENSION HOOK]: Per-excerpt science classification stage

Note: T-3 and T-6 are **mitigated, not eliminated** in v1. The owner review gate (reviewing real Arabic output on diverse books) is the final quality gate. Automated tests check structure; only a human reader catches scholarly meaning errors.

---

## 6. Error Handling

| Error Code | Severity | Trigger | Recovery |
|---|---|---|---|
| `TAX_MISSING_REQUIRED_FIELD` | Fatal (per excerpt) | Excerpt missing a required field from §2.1 | Excerpt rejected, logged with field name and excerpt_id |
| `TAX_MISSING_EXPECTED_FIELD` | Warning | Excerpt missing an expected field | Proceeds with degraded quality, warning logged |
| `TAX_INVALID_SCIENCE` | Fatal to placement | science_id not in registry or no active tree | Batch produces pending_no_tree artifacts + batch report. No placement/staging attempted. |
| `TAX_TREE_LOAD_ERROR` | Fatal (batch) | Tree YAML fails to parse or has 0 leaves | Batch aborted, error logged |
| `TAX_UNPLACEABLE` | Info | No candidate scored ≥ 0.50 | Excerpt routed to unplaced/ with candidates |
| `TAX_LLM_FAILURE` | Warning | LLM call fails after 3 attempts (exhausted retries) | Excerpt queued for retry; if still failing, routed to unplaced |
| `TAX_PLACEMENT_INTEGRITY_ERROR` | Fatal (per excerpt) | Post-write validation fails (byte mismatch or leaf not found) | Written file deleted, excerpt routed to unplaced |

**Principle (D-033):** A visible failure that stops processing is always preferable to an invisible error that enters the library. Every error is logged with: timestamp, error code, severity, excerpt_id, and recovery action taken.

---

## 7. Configuration

### 7.1 Global Parameters

| Parameter | Default | Description |
|---|---|---|
| `live_threshold_teaching` | 0.80 | Min confidence for live placement (teaching content) |
| `live_threshold_editorial` | 0.85 | Min confidence for live placement (editorial/structural) |
| `staging_threshold` | 0.50 | Below this, excerpt is unplaced |
| `tie_threshold` | 0.10 | Score difference that constitutes a tie |
| `hierarchical_search_leaf_limit` | 200 | Tree size above which search uses hierarchical mode |
| `stage1_branch_count` | 3 | Number of branches selected in hierarchical search |
| `primary_text_char_limit` | 3000 | Max chars of primary_text in Stage 2 prompt (full text if shorter) |
| `llm_timeout_seconds` | 600 | Timeout per LLM call |
| `llm_max_retries` | 2 | Retries per LLM call (3 total attempts) |

### 7.2 Per-Science Configuration

Derived from `taxonomy_registry.yaml`:
- `science_id` → tree file path
- `display_name_ar` → used in LLM prompts
- `active_tree_version` → recorded on every placement

No per-science parameter overrides for v1.

[EXTENSION HOOK] — Per-science evolution sensitivity, school lists, and narrative ordering authority are Stage 2.

### 7.3 Hardcoded Constraints

- Excerpts are placed only at leaves, never at branch nodes.
- Trees branch by topic, never by school.
- Placed excerpts are never deleted by the taxonomy engine (they may be relocated in Stage 2).
- All upstream excerpt fields are preserved through placement (D-023).
- All output files use UTF-8 encoding.

---

## 8. Current Implementation State

### 8.1 Existing Code

| File | Status | Notes |
|---|---|---|
| `engines/taxonomy/src/tracer.py` | Placeholder | Places all at hardcoded leaf. Replace entirely. |
| `engines/taxonomy/contracts.py` | Overscoped (491 lines) | Models for evolution, coverage, landscape. Trim to core models. |
| `engines/taxonomy/tests/` | Empty | All tests must be built. |
| `reference/archive/abd_code/taxonomy/evolve_taxonomy.py` | Reference | `_detect_yaml_format()` — reuse format detection logic. |

### 8.2 External Dependencies

| Dependency | Purpose | In repo? |
|---|---|---|
| `shared/llm/cli_adapter.py` | LLM calls via CLI backend | Yes — 45 tests, hardened |
| `pyyaml` | Tree YAML parsing | Yes |
| `pydantic` v2 | Contract models, LLM response validation | Yes |

### 8.3 Pre-Build Prerequisites

1. Verify all 5 tree YAML files parse correctly (both v0 and v1 format)
2. Verify `taxonomy_registry.yaml` entries resolve to actual tree files with correct leaf counts
3. Verify CLI adapter produces structured output for `BranchSelection` and `PlacementRanking` models
4. Create test fixtures: mock excerpts with known correct placements for nahw

---

## 9. Test Requirements

### 9.1 Unit Tests

**Tree loading:**
- v1 format loads correctly (nahw, sarf, balagha, imlaa)
- v0 format loads correctly (aqidah)
- Leaf counts: 226, 226, 335, 30, 105
- `__overview` nodes in v0 format are parsed as leaves (not skipped)
- Invalid YAML raises `TAX_TREE_LOAD_ERROR`
- `leaf_by_path` lookup works for every leaf in every tree

**Placement routing:**
- Teaching content at scores 0.9, 0.7, 0.3 → live, staged, unplaced
- Editorial content at scores 0.9, 0.8, 0.6, 0.3 → live, staged, staged, unplaced
- Tie detection fires at score difference 0.08 (below threshold)
- Tie detection does NOT fire at score difference 0.15 (above threshold)

**Provenance preservation:**
- All original excerpt fields present in output
- `primary_text` byte-identical after round-trip (write + read)
- Taxonomy-added fields present and correctly typed

**Input validation:**
- Missing `excerpt_id` → TAX_MISSING_REQUIRED_FIELD, excerpt rejected
- Missing `description_arabic` → TAX_MISSING_EXPECTED_FIELD, excerpt proceeds
- Nonexistent science_id → TAX_INVALID_SCIENCE, batch to pending_no_tree

### 9.2 Integration Tests

**Real excerpt format compatibility:**
- Read `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl` (25 real excerpts)
- Verify all required fields present
- Verify no crash on real data shapes (null fields, empty lists, Arabic text)

**End-to-end with mock LLM:**
- Feed 10 excerpts through the full pipeline with a mock LLM returning deterministic scores
- Verify correct routing: some to live, some to staged, some to unplaced
- Verify batch report statistics match actual outputs
- Verify all output files are valid JSON with correct fields

### 9.3 Gold Baseline Test

**10–15 manually placed excerpts from ibn_aqil_v3** with known correct leaves (assigned by architect + owner). Run with real LLM calls and measure:
- Exact-leaf accuracy (target: ≥ 80% for this topically clear subset)
- Branch-level accuracy (target: ≥ 95%)
- Correct routing: are low-confidence and editorial excerpts staged, not live?

The gold baseline is built during the implementation phase.

### 9.4 Adversarial Tests

**Arabic text fidelity (T-1):** Excerpts with diacritics (تَشْكِيل), ZWNJ (‌), kashida (ـ), rare Unicode. Verify `primary_text` byte-identical after placement.

**Broad-leaf bias detection:** Excerpts with specific topics; verify the system prefers specific leaves over `__overview` or general leaves.

**Editorial routing:** Feed `primary_function: editorial_note` excerpts; verify they face the 0.85 threshold, not 0.80.

**Always-staged routing:** Feed `primary_function: cross_reference` excerpt with mock score 0.95; verify it goes to `staged/` NOT `content/`, regardless of score. Same for `structural_transition`.

**Systematic bias (§10.5.1 from original SPEC):** Run 20+ diverse excerpts and verify no single leaf receives more than the batch's fair-share proportion without justification.

**Leaf path uniqueness invariant:** Load all 5 tree YAML files and assert every leaf has a unique `path` within its tree. This catches tree authoring errors that would cause output path collisions.

**Stage 1 no-match pathway:** Force Stage 1 to return `no_match: true`; verify the unplaced output has `best_candidates: []` and a valid schema.

**Intersection topic (كي):** The real excerpt about "كي حرف جر" should go to `almajrurat/huruf_aljar/ma3ani_huruf_aljar` (كي as preposition), NOT to `alaf3al/nawasiib_almudari3/kay` (كي as nasb particle). Both leaves exist in the nahw tree. Test with real LLM and verify correct branch selection.

**Pending-no-tree isolation:** Run a batch with a nonexistent science_id; verify no files are written under `content/` or `staged/`, only under `pending_no_tree/{science_id}/`.

**Tie forces staging:** Feed an excerpt where mock LLM returns two candidates within 0.10 of each other, both scoring ≥0.80; verify the excerpt goes to `staged/` not `content/` because of the tie.

---

## 10. Extension Hooks (Deferred to Stage 2)

| Deferred Capability | Core Architectural Constraint |
|---|---|
| Tree evolution | Core records `taxonomy_version_at_placement` on every placement |
| Embedding similarity | Core's candidate set accepts additional candidates via `extend()` |
| Coverage analytics | File-per-excerpt layout enables post-hoc counting |
| Human gate queue | Core records `placement_confidence`, `tie_detected`, `placement_route` |
| Cross-science links | Core does not merge trees or assume science isolation |
| Proposed_leaf from excerpting | Core accepts `proposed_leaf` if present (as first candidate) |
| Multi-model consensus | Core uses CLI adapter's model routing, not hardcoded model |
| Per-excerpt science classification | Core records batch diagnostics; extension adds per-excerpt check |
| Terminology synonyms | Core relies on LLM's implicit synonym handling |
| Leaf ambiguity scoring | Core uses uniform thresholds; extension can vary by leaf complexity |
