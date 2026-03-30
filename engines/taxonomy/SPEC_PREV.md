# Taxonomy Engine — محرك التصنيف — Core v1 Specification

**Status:** DRAFT — pending ChatGPT Pro review (checkpoint #3) before declaring implementation-ready
**Scope:** Core placement only. See `SPEC_FULL_ORIGINAL.md` for the full vision including evolution, coverage, knowledge graph.
**Design basis:** `REWRITE_ANALYSIS.md` (15 design decisions, D-TAX-001 through D-TAX-015, reviewed by ChatGPT Pro)
**Governing axiom:** Every placement error is a wrong belief. A wrong leaf is not a cosmetic bug — it changes the context in which the owner encounters a scholarly claim. There are no low-severity placement errors.

---

## §1 Purpose and Scope

The taxonomy engine places excerpts at the correct leaf in existing science trees. That is its only job for v1.

**What it does:**
1. Reads existing science trees from `library/sciences/{science_id}/tree.yaml`
2. Receives batches of excerpts from the excerpting engine (JSONL format)
3. Validates the declared science_id against excerpt content (batch preflight)
4. Classifies each excerpt to a leaf via LLM topic matching
5. Ranks candidate leaves via LLM scoring
6. Routes excerpts to four categories: placed (high confidence), staged (low confidence), unplaced, or pending
7. Validates placement integrity (leaf exists, file written, primary_text byte-identical)
8. Logs placement reasoning, confidence, and batch diagnostics

**What it does NOT do (deferred to Stage 2):**
- Tree construction, evolution, or modification
- Coverage analytics
- Knowledge graph (prerequisites, cross-science links, synonyms)
- Scholarly landscape or disagreement topology
- Human gate queue infrastructure
- Multi-model consensus
- Embedding-based similarity search

**Phase classification:** Phase 2 (source-agnostic, below the normalization boundary). The taxonomy engine receives excerpts that carry no trace of their original source format.

---

## §2 Input Contract

### §2.1 Excerpt Input

Each excerpt arrives as one JSON object per line in a JSONL file — the direct output of the excerpting engine. The taxonomy engine reads lines sequentially.

**Required fields — rejection on absence:**

| Field | Type | Source |
|-------|------|--------|
| `excerpt_id` | string, non-empty | Excerpting engine |
| `source_id` | string, non-empty | Excerpting engine |
| `primary_text` | string, non-empty | Excerpting engine |
| `excerpt_topic` | list[string], non-empty | Excerpting engine |

Absence of any required field → reject with `TAX_MISSING_REQUIRED_FIELD`. The excerpt is not processed.

**Expected fields — warning on absence, degraded placement:**

| Field | Type | Used For |
|-------|------|----------|
| `description_arabic` | string | Primary placement signal (rich topic description) |
| `primary_function` | string | Type-sensitive threshold (D-TAX-014) |
| `content_types` | list[string] | Placement context |
| `div_path` | list[string] | Book structural context for placement |
| `terminology_variants` | list[dict] | Synonym context for LLM |
| `school` | string or null | Preserved in output |
| `primary_author_layer` | dict | Preserved in output |
| `quoted_scholars` | list[dict] | Preserved in output |

Absence of expected fields → warn with `TAX_MISSING_EXPECTED_FIELD`. The excerpt proceeds.

**Fields NOT required (resolved by other means):**

| Field | Resolution |
|-------|-----------|
| `science_id` | Run configuration parameter (D-TAX-001) |
| `proposed_leaf` | Not expected. If present, used as first candidate. Not required. |
| `lifecycle_stage` | Assumed `draft` for all incoming excerpts |
| `passage_id` | Not used (passaging engine not built). Not expected. |
| `atom_ids` | Not used (atomization engine not built). Not expected. |

### §2.2 Run Configuration

Each taxonomy run is configured with:

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `science_id` | string | Yes | The science this batch belongs to. Must match taxonomy_registry.yaml. |
| `input_path` | path | Yes | Path to the excerpts JSONL file |
| `output_base` | path | Yes | Base path for output (default: `library/sciences/{science_id}/`) |

The `science_id` determines which tree to load. The taxonomy engine processes one science at a time.

### §2.3 Tree Input

Trees are located via `library/sciences/taxonomy_registry.yaml`, which maps `science_id` → active tree file path.

Tree files exist in two YAML formats:
- **v1 format:** `taxonomy → nodes → [{id, title, children, leaf}, ...]` (nahw, sarf, balagha, imlaa)
- **v0 format:** nested dict with `_label` and `_leaf` keys (aqidah)

The tree loader normalizes both formats into a single internal `TreeNode` structure at load time (D-TAX-004). All downstream code works with `TreeNode` objects. Tree files on disk are never modified by the taxonomy engine.

---

## §3 Output Contract

The taxonomy engine produces four categories of output (D-TAX-003).

### §3.1 Placed Excerpts (High Confidence)

Written to `{output_base}/content/{leaf_path}/excerpts/{excerpt_id}.json`.

Each placed excerpt is the **complete original excerpt** (all fields preserved per D-023) plus:

| Field | Type | Description |
|-------|------|-------------|
| `lifecycle_stage` | `"placed"` | Immutable once written |
| `confirmed_leaf` | string | The leaf path where placed |
| `placement_confidence` | float 0.0-1.0 | LLM's confidence score |
| `placement_tier` | `"high"` | ≥ auto-place threshold |
| `placed_utc` | ISO datetime | Timestamp of placement |
| `taxonomy_version_at_placement` | string | Tree version from registry |
| `placement_reasoning` | string | LLM-generated explanation of leaf choice |
| `review_metadata` | `{"review_outcome": "auto_approved"}` | Simplified for v1 |
| `proposed_leaf_override` | bool | True if taxonomy chose differently from proposed_leaf |
| `proposed_leaf_original` | string or null | The original proposed_leaf if overridden |
| `override_reason` | string or null | Why the override occurred |

**Guarantees:**
- `confirmed_leaf` resolves to a real leaf in the tree at `taxonomy_version_at_placement`
- `primary_text` is byte-identical to input (T-1 prevention)
- No two files share the same `excerpt_id`
- All upstream fields pass through untouched

### §3.2 Staged Excerpts (Low Confidence)

Written to `{output_base}/staged/{leaf_path}/excerpts/{excerpt_id}.json`.

Same schema as §3.1, except:
- `placement_tier`: `"staged"`
- `staged_reason`: string — e.g. "confidence 0.67 < 0.8 threshold", "tie: top1-top2 = 0.12 < δ 0.15", "editorial_note with confidence 0.71 < editorial threshold 0.85"

Staged excerpts are NOT in the live content tree. Downstream consumers (future synthesis) read only from `content/`. The evaluation phase reviews staged excerpts.

### §3.3 Unplaced Excerpts

Written to `{output_base}/unplaced/{excerpt_id}.json`.

Contains the full original excerpt plus:
- `lifecycle_stage`: `"unplaced"`
- `unplaced_reason`: string
- `best_candidates`: list of top 3 candidates with scores and reasoning

### §3.4 Pending Excerpts (No Tree)

Written to `library/pending/{science_id}/{excerpt_id}.json`.

If the declared `science_id` has no active tree in the registry → all excerpts go here. They are not unplaceable — they are awaiting a tree. When the tree is created, they can be re-processed.

Contains the full original excerpt plus:
- `lifecycle_stage`: `"pending_no_tree"`
- `declared_science_id`: the science declared but lacking a tree

### §3.5 Batch Report

Written to `{output_base}/batch_report_{timestamp}.json`.

| Field | Type | Description |
|-------|------|-------------|
| `run_id` | string | Unique run identifier |
| `science_id` | string | Declared science |
| `tree_version` | string | Active tree version used |
| `timestamp` | ISO datetime | Run completion time |
| `total_excerpts` | int | Total in input |
| `placed_count` | int | → content/ |
| `staged_count` | int | → staged/ |
| `unplaced_count` | int | → unplaced/ |
| `pending_count` | int | → pending/ |
| `rejected_count` | int | Missing required fields |
| `preflight_result` | object | Science preflight results |
| `confidence_distribution` | object | Histogram of confidence scores |
| `leaf_distribution` | object | leaf_path → excerpt count |
| `warnings` | list[string] | Batch-level warnings |

**Warnings trigger when:**
- Preflight science mismatch detected
- Any leaf has >20 excerpts
- staged + unplaced > placed

---

## §4 Processing Specification

### §4.A Core Processing

#### §4.A.1 — Batch-Level Science Preflight (D-TAX-013)

Before processing excerpts:

1. Load tree for `science_id`. If no tree exists → route all excerpts to `pending/`, write batch report, halt.
2. Sample 5 excerpts from the batch (1st, 25%, 50%, 75%, last by position).
3. For each, call LLM:

```
Which of these Islamic sciences does this excerpt belong to?
Options: nahw (النحو), sarf (الصرف), balagha (البلاغة), aqidah (العقيدة),
         imlaa (الإملاء), none_of_these (ليس من هذه العلوم)

Excerpt topic: {excerpt_topic}
Excerpt description: {description_arabic}
Excerpt type: {primary_function}

Return the science_id and your confidence.
```

**Response model:** `SciencePreflightResult {science_id: str, confidence: float}`

4. If ≥3 of 5 disagree with declared `science_id` → halt with `TAX_SCIENCE_MISMATCH`.
5. If ≤2 disagree → proceed. Log disagreements.

Cost: 5 LLM calls per batch.

#### §4.A.2 — Placement Algorithm

Two stages: candidate generation, then candidate ranking.

**Stage 1: Candidate Generation**

For trees with **≤200 leaves** (aqidah: 30, imlaa: 105):
- All leaves are candidates. Skip to Stage 2.

For trees with **>200 leaves** (nahw: 226, sarf: 226, balagha: 335):

*Step 1a — Hierarchical branch selection.* Call LLM:

```
You are placing an Arabic Islamic scholarly excerpt into a taxonomy tree.

Science: {science_display_name}
Excerpt topic: {' / '.join(excerpt_topic)}
Excerpt description: {description_arabic}
Book structural path: {' > '.join(div_path)}
Excerpt type: {primary_function}

Here are the top-level branches of the tree, each with immediate sub-branches:

{for each top-level node:}
{i}. {node.id}: {node.title} ({leaf_count} leaves)
{for each child (first 5):}
   └─ {child.title} {'[LEAF]' if leaf else f'({child_leaf_count} leaves)'}

Which 3 branches most likely contain the correct leaf?
If the excerpt does not belong in this science, return an empty list.
```

**Response model:** `BranchSelectionResult {branches: list[str], reasoning: str}`

*Step 1b — Recall backstop (D-TAX-015).* After branch selection, scan ALL leaf titles. For each leaf, count how many words from `excerpt_topic` (min 3 chars each) appear in the leaf title. If ≥2 match → add as wildcard candidate.

*Step 1c — Combine candidates.* Collect all leaves from the 3 selected branches + wildcard candidates. Cap at `stage2_max_candidates` (default 15). If `proposed_leaf` is present and valid, include it.

**Stage 2: Candidate Ranking**

Call LLM with candidates:

```
You are placing an Arabic Islamic scholarly excerpt at the correct leaf.

Excerpt topic: {' / '.join(excerpt_topic)}
Excerpt description: {description_arabic}
Excerpt text (first 800 chars): {primary_text[:800]}
Excerpt type: {primary_function}
Content types: {content_types}
Book structural path: {' > '.join(div_path)}

Candidate leaves:
{for each candidate:}
  - ID: {leaf_id}
    Title: {leaf_title}
    Full path: {root > branch > ... > leaf}

Score each candidate 0.0-1.0 and explain briefly.

Scoring criteria:
1. Does the excerpt's teaching content match this leaf's topic?
2. Is there a more specific leaf that fits better?
3. If this is an editorial/introductory passage (not teaching a specific topic),
   score LOW unless it explicitly defines or argues a science topic.

If NO candidate is appropriate (all <0.5), say so.
```

**Response model:** `LeafRankingResult {rankings: list[LeafScore]}`
where `LeafScore {leaf_id: str, score: float, reasoning: str}`

#### §4.A.3 — Placement Decision

1. Select top candidate (highest score from Stage 2).
2. Check tie: top1.score - top2.score < `tie_delta` (0.15) → tie.
3. Apply type-sensitive thresholds (D-TAX-014):

| primary_function | Auto-place threshold | Staging range |
|-----------------|---------------------|---------------|
| `editorial_note` | ≥ `editorial_auto_threshold` (0.85) | 0.50 – 0.84 |
| `structural_transition` | ≥ `editorial_auto_threshold` (0.85) | 0.50 – 0.84 |
| All others | ≥ `placement_auto_threshold` (0.80) | 0.50 – 0.79 |

4. Route:

| Condition | Action | Directory |
|-----------|--------|-----------|
| Score ≥ threshold AND no tie | Place | `content/{leaf}/excerpts/` |
| Score ≥ 0.50 AND (below threshold OR tie) | Stage | `staged/{leaf}/excerpts/` |
| Score < 0.50 | Unplace | `unplaced/` |

5. Record metadata: `placement_reasoning`, `taxonomy_version_at_placement`, override info if applicable.

#### §4.A.4 — Primary Topic Determination

Multi-topic excerpts are handled implicitly by Stage 2's scoring. The LLM evaluates all candidate leaves against the full excerpt context (topic list, description, text snippet, div_path). The prompt's criterion #2 ("more specific leaf?") steers toward precision.

No separate determination call is needed for v1. The real data shows multi-topic excerpts' topics converge on the same tree area (sub-topics within one main topic). If evaluation reveals systematic multi-topic misplacements, a dedicated determination stage can be added.

#### §4.A.5 — Placement Validation

After routing each excerpt, before writing:

1. **Leaf existence:** `confirmed_leaf` resolves to a real leaf. If not → `TAX_PLACEMENT_INTEGRITY_ERROR`.
2. **Write file:** JSON with `encoding="utf-8"`, `ensure_ascii=False`.
3. **Fidelity check:** Read back, parse, verify `primary_text` byte-identical. If not → `TAX_PLACEMENT_INTEGRITY_ERROR`.
4. **Uniqueness:** No file with same `excerpt_id` at target. If duplicate → `TAX_DUPLICATE_EXCERPT`.

[DEFERRED TO STAGE 2] — One-excerpt-per-source diagnostic, verified/flagged consistency.
[EXTENSION HOOK] — Core records source_id and preserves trust fields on every placement.

---

### §4.B Transformative Capabilities

[DEFERRED TO STAGE 2] — §4.B.1 Topic Significance Scoring. Hook: excerpts stored per-leaf.
[DEFERRED TO STAGE 2] — §4.B.2 Difficulty Estimation. Hook: div_path preserved.
[DEFERRED TO STAGE 2] — §4.B.3 Corpus-Driven Tree Construction. Hook: tree loader is read-only.
[DEFERRED TO STAGE 2] — §4.B.4 Disagreement Topology. Hook: school/quoted_scholars preserved.
[DEFERRED TO STAGE 2] — §4.B.5 Evolution Prediction. Hook: unplaced excerpts are signal data.
[DEFERRED TO STAGE 2] — §4.B.6 Scholarly Landscape. Hook: attribution metadata preserved.

---

## §5 Validation and Quality

### §5.1 Self-Validation (per placement)

1. File written successfully
2. File content parses as valid JSON
3. `primary_text` byte-identical to input (T-1)
4. `confirmed_leaf` resolves to real leaf
5. No duplicate `excerpt_id`

### §5.2 Threat Prevention

| Threat | Prevention |
|--------|-----------|
| T-1 (text corruption) | Byte-identical check on every write |
| T-2 (attribution error) | All attribution fields pass through (D-023) |
| T-3 (misplacement) | Two-stage LLM + type thresholds + staging gate |
| T-4 (context loss) | div_path preserved; reasoning recorded |
| T-5 (hallucination) | [DEFERRED — no landscape] |
| T-6 (wrong science) | Batch preflight (D-TAX-013) |
| T-7 (silent data loss) | Four-category routing; nothing dropped |

### §5.3 Human Gate

[DEFERRED TO STAGE 2] — Queue infrastructure.
[EXTENSION HOOK] — `staged/` directory is the v1 review queue.

---

## §6 Consensus Integration

[DEFERRED TO STAGE 2] — Multi-model consensus.
[EXTENSION HOOK] — CLI adapter model routing supports adding consensus as a wrapper.

---

## §7 Error Handling

### §7.1 Input Errors

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `TAX_MISSING_REQUIRED_FIELD` | Fatal | Missing excerpt_id/source_id/primary_text/excerpt_topic | Reject, log, skip |
| `TAX_MISSING_EXPECTED_FIELD` | Warning | Missing description_arabic, primary_function, etc. | Proceed degraded |
| `TAX_INVALID_SCIENCE` | Fatal | science_id not in registry | Halt batch |
| `TAX_SCIENCE_MISMATCH` | Fatal | Preflight ≥3/5 disagree | Halt batch |

### §7.2 Processing Errors

| Code | Severity | Trigger | Recovery |
|------|----------|---------|----------|
| `TAX_UNPLACEABLE` | Warning | All candidates < 0.5 | → unplaced/ |
| `TAX_PLACEMENT_TIE` | Info | top1-top2 < 0.15 | → staged/ |
| `TAX_LLM_FAILURE` | Warning | LLM call fails | Retry 3× backoff; if all fail → queue |
| `TAX_PLACEMENT_INTEGRITY_ERROR` | Fatal | Validation fails | Revert, alert |
| `TAX_DUPLICATE_EXCERPT` | Fatal | excerpt_id exists | Block, alert |
| `TAX_TREE_LOAD_ERROR` | Fatal | YAML parse failure | Halt batch |

### §7.3 Principle

Every error logged with: timestamp, code, severity, excerpt_id, recovery. No silent swallowing. A visible failure is always preferable to an invisible error entering the library.

---

## §8 Configuration

### §8.1 Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `placement_auto_threshold` | 0.80 | Auto-place to content/ |
| `editorial_auto_threshold` | 0.85 | Auto-place for editorial/structural types |
| `placement_min_threshold` | 0.50 | Below → unplaceable |
| `tie_delta` | 0.15 | Tie if top1-top2 < this |
| `hierarchical_search_threshold` | 200 | Leaf count triggering hierarchical search |
| `preflight_sample_count` | 5 | Excerpts sampled for science preflight |
| `preflight_mismatch_threshold` | 3 | Disagreements to halt batch |
| `primary_text_snippet_length` | 800 | Chars of primary_text in Stage 2 |
| `stage1_branch_count` | 3 | Branches selected in hierarchical search |
| `stage2_max_candidates` | 15 | Max candidates sent to Stage 2 |
| `recall_backstop_min_keywords` | 2 | Min keyword matches for wildcard inclusion |

### §8.2 Hardcoded Constraints

- Excerpts placed only at leaves.
- Trees are read-only.
- Placed/staged excerpts never deleted by taxonomy engine.
- All upstream metadata passes through (D-023).
- `encoding="utf-8"` on all I/O. `ensure_ascii=False` on all JSON writes.

---

## §9 Implementation

### §9.1 Existing Code

| File | Description | Action |
|------|-------------|--------|
| `engines/taxonomy/src/tracer.py` | Stub — places all at one leaf | Replace entirely |
| `engines/taxonomy/contracts.py` | 491 lines, full SPEC models | Trim to core models |
| `reference/archive/abd_code/taxonomy/evolve_taxonomy.py` | Has `_detect_yaml_format()` | Reference for tree loader |
| `library/sciences/` | 5 trees, registry | Read-only input |
| `shared/llm/cli_adapter.py` | LLM adapter, 45 tests | Use for all LLM calls |

### §9.2 Dependencies

| Dependency | Purpose | Status |
|------------|---------|--------|
| `pydantic` v2 | Contracts, response models | Available |
| `pyyaml` | Tree YAML parsing | Available |
| `shared/llm/cli_adapter.py` | LLM calls | Available |

No new external dependencies.

### §9.3 Core Models

```python
# LLM response models
class SciencePreflightResult(BaseModel):
    science_id: str
    confidence: float

class BranchSelectionResult(BaseModel):
    branches: list[str]
    reasoning: str

class LeafScore(BaseModel):
    leaf_id: str
    score: float = Field(ge=0.0, le=1.0)
    reasoning: str

class LeafRankingResult(BaseModel):
    rankings: list[LeafScore]

# Tree model (internal, from loader)
class TreeNode(BaseModel):
    id: str
    title: str
    children: list['TreeNode'] = []
    leaf: bool = False

# Placement output additions
class PlacementAdditions(BaseModel):
    lifecycle_stage: str   # placed | staged | unplaced | pending_no_tree
    confirmed_leaf: Optional[str] = None
    placement_confidence: Optional[float] = None
    placement_tier: Optional[str] = None  # high | staged
    placed_utc: str
    taxonomy_version_at_placement: str
    placement_reasoning: Optional[str] = None
    review_metadata: dict = Field(default_factory=lambda: {"review_outcome": "auto_approved"})
    proposed_leaf_override: bool = False
    proposed_leaf_original: Optional[str] = None
    override_reason: Optional[str] = None
    staged_reason: Optional[str] = None
    unplaced_reason: Optional[str] = None
    best_candidates: Optional[list[dict]] = None

class BatchReport(BaseModel):
    run_id: str
    science_id: str
    tree_version: str
    timestamp: str
    total_excerpts: int
    placed_count: int
    staged_count: int
    unplaced_count: int
    pending_count: int
    rejected_count: int
    preflight_result: dict
    confidence_distribution: dict
    leaf_distribution: dict
    warnings: list[str]
```

---

## §10 Test Requirements

### §10.1 Categories

| Category | Tests | Min Cases |
|----------|-------|-----------|
| Placement accuracy | Correct leaf | 15 gold baseline |
| Staging gate | Low-confidence → staged/ | 5 borderline |
| Unplacement | No match → unplaced/ | 3 wrong-science |
| Science preflight | Wrong science detected | 1 batch |
| Editorial handling | Type threshold applied | 5 editorial excerpts |
| Hierarchical search | Branch selection | 5 across branches |
| Recall backstop | Wildcard prevents miss | 1 edge case |
| Tree normalization | Both formats load | All 5 trees |
| Provenance (D-023) | All fields preserved | 3 excerpts |
| T-1 fidelity | primary_text identical | All tests |
| Batch report | Counts match files | All tests |

### §10.2 Gold Baseline

15 manually-placed excerpts from `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl` against nahw tree. Each records: `excerpt_id`, `correct_leaf`, `acceptable_leaves` (legitimate alternatives), `reasoning`.

### §10.3 Integration Test

Full run: ibn_aqil_v3 (25 excerpts) vs nahw. Verify: all 25 produce output, batch report totals match, ≥15/25 match gold baseline.

### §10.4 Adversarial Tests

| Test | Catches |
|------|---------|
| Wrong-science batch | Preflight halts fiqh vs nahw |
| All-editorial batch | Most staged, not placed |
| Tie detection | Ambiguous excerpt → staged with reason |
| Tree load failure | TAX_TREE_LOAD_ERROR, not silent |
| Missing-field robustness | Processes with required fields only |
| Broad-leaf bias | No leaf gets >60% of placements |

---

## Appendix: Deferred Index

| Capability | Original Section | Extension Hook |
|-----------|-----------------|----------------|
| Tree evolution | §4.A.3, §4.A.5, §4.A.7 | taxonomy_version_at_placement recorded |
| Coverage | §3.3, §4.A.6 | File-per-excerpt enables counting |
| Knowledge graph | §3.2 | No science isolation assumption |
| Human gate | §5.3 | staged/ is v1 review queue |
| Embeddings | §4.A.1c | Candidate generation is pluggable |
| Consensus | §6 | CLI adapter supports model routing |
| Landscape | §4.B.4, §4.B.6 | Attribution metadata preserved |
| Relocation | §2.2 | File-per-excerpt enables mv |
| Pre-approval | §4.A.1 | All decisions logged |
