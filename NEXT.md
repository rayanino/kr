# NEXT — Taxonomy Engine: Session 2 — LLM Placement Integration

## Context

Session 1 (commit `25368b28`) built the complete deterministic infrastructure:
- 6 source modules: tree_loader, placer, validator, writer, diagnostics, engine
- 119 tests, 0 failures, pyright clean
- All 5 science trees load correctly (922 leaves total)
- Two independent code reviews caught and fixed 3 bugs (silent data loss,
  reasoning mismatch, input undercounting)

The deterministic layer is proven. This session adds the LLM brain.

## What Session 2 Must Do

### Step 1: Implement `LLMPlacementAdapter`

Create `engines/taxonomy/src/llm_adapter.py` implementing the `PlacementAdapter` Protocol
from `engines/taxonomy/src/placer.py`.

**Two methods to implement:**

```python
class LLMPlacementAdapter:
    def __init__(self, adapter: CLIInstructorAdapter) -> None: ...
    def run_stage1(self, excerpt: dict, tree: LoadedTree) -> BranchSelection: ...
    def run_stage2(self, excerpt: dict, candidates: list[TreeNode]) -> PlacementRanking: ...
```

**LLM call pattern** (from `shared/llm/cli_adapter.py`):
```python
from shared.llm.cli_adapter import CLIInstructorAdapter

adapter = CLIInstructorAdapter()
result = adapter.chat.completions.create(
    model="anthropic/claude-opus-4",
    response_model=BranchSelection,  # or PlacementRanking
    messages=[{"role": "user", "content": prompt}],
)
```

**Configuration** (SPEC §7.1):
- Model: `anthropic/claude-opus-4`
- Timeout: 600s
- Retries: 2 (3 total attempts)

### Step 2: Build Stage 1 Prompt (Branch Selection)

For trees > 200 leaves (nahw, sarf, balagha). Shows:
- Excerpt topic and description (Arabic)
- Tree branch structure (from `build_branch_view()` in tree_loader.py)

Instructs LLM: "Select the 1-3 most likely branches. Set no_match=True if none fit."

**Key Arabic prompt rules** (from `.claude/rules/llm-call-optimization.md`):
- Include Arabic text directly, never transliteration
- Include domain terms in Arabic alongside English
- Temperature = 0 (classification task)
- Few-shot examples from real fixtures preferred

### Step 3: Build Stage 2 Prompt (Leaf Ranking)

For all candidate leaves. Shows:
- `excerpt_topic` (all topics joined by ` / `)
- `description_arabic`
- `primary_text` (full if < 3000 chars; first 3000 if longer)
- `primary_function`, `content_types`, `div_path`
- For each candidate: `leaf_path`, `leaf_title`, `parent_title`

Instructs LLM:
1. Score each candidate 0.0–1.0 on fit
2. Prefer specific leaves over broad ones
3. Score LOW for introductions/editorial that don't teach specific topic
4. Identify primary topic for placement

### Step 4: Gold Baseline Test

Test file: `engines/taxonomy/tests/test_llm_inference.py` (separate from deterministic tests)

Use the 12 gold baseline excerpts from `engines/taxonomy/tests/fixtures/gold_baseline_nahw.yaml`:
- Load real excerpts from `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl`
- Run LLM placement against the nahw tree
- Compare results to gold assignments
- Targets: ≥80% exact-leaf match, ≥95% correct-branch match

Mark with `@pytest.mark.skipif` for offline runs (needs LLM API).

### Step 5: Pilot Run (5 excerpts)

Run the full engine pipeline on 5 real excerpts from ibn_aqil_v3:
```bash
PYTHONPATH=. python -c "
from engines.taxonomy.src.engine import run
from engines.taxonomy.contracts_core import RunConfig
# ... create config, run, inspect report
"
```

Verify: placements make sense, reasoning is coherent, confidence distribution reasonable.

## Key Files

| File | Purpose | Action |
|------|---------|--------|
| `engines/taxonomy/src/placer.py` | PlacementAdapter Protocol | READ (don't modify) |
| `engines/taxonomy/src/llm_adapter.py` | LLM adapter implementation | CREATE |
| `engines/taxonomy/src/tree_loader.py` | `build_branch_view`, `build_leaf_view` | READ (use for prompts) |
| `engines/taxonomy/contracts_core.py` | BranchSelection, PlacementRanking | READ |
| `engines/taxonomy/SPEC.md` §4.A.2 | Prompt requirements | READ (authoritative) |
| `engines/taxonomy/tests/fixtures/gold_baseline_nahw.yaml` | 12 gold placements | READ |
| `shared/llm/cli_adapter.py` | CLIInstructorAdapter | READ (don't modify) |
| `integration_tests/smoke_fix_20260329/ibn_aqil_v3/excerpts.jsonl` | Real excerpts | READ |
| `.claude/rules/llm-call-optimization.md` | Arabic prompt rules | READ |

## Do NOT Do

- Do NOT modify the deterministic modules (tree_loader, validator, writer, diagnostics)
- Do NOT modify contracts_core.py (the models are finalized)
- Do NOT add multi-model consensus (v1 uses single-model placement, D-041 is Stage 2)
- Do NOT implement tree evolution, coverage, or cross-science features
- Do NOT skip the gold baseline test — it validates the entire placement chain
- Do NOT use temperature > 0 for classification (see llm-call-optimization rules)

## Budget

LLM calls for testing: estimate ~12 gold baseline calls + 5 pilot calls = ~17 calls.
At ~$0.10/call with Opus, budget ~$2 for this session.
