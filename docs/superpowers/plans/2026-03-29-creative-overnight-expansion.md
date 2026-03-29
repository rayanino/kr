# Creative Overnight Expansion — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add creative research tasks (innovation, adversarial generation, cross-provider SPEC challenges) to the overnight system alongside existing hardening work.

**Architecture:** New `creative_scanner()` function in the task generator reads JSON templates from `overnight/creative_templates/`, checks cooldown + applicability, instantiates tasks for current project context, and adds them to the manifest at priority 2. The orchestrator dispatches them to Claude/Codex/Gemini via existing execution backends. A post-run script auto-appends actionable findings to FINDINGS_TRACKER.md.

**Tech Stack:** Python 3.11+, JSON templates, existing overnight orchestrator infrastructure

**Spec:** `docs/superpowers/specs/2026-03-29-creative-overnight-expansion-design.md`

---

### Task 1: Add "creative" to ALLOWED_CATEGORIES and safety prompt

**Files:**
- Modify: `scripts/overnight_task_generator.py:811`
- Modify: `scripts/overnight_orchestrator.py:690` (add creative category branch)
- Modify: `scripts/overnight_orchestrator.py` (add OVERNIGHT_CREATIVE_PROMPT after line 133)

- [ ] **Step 1: Add "creative" to ALLOWED_CATEGORIES in task generator**

In `scripts/overnight_task_generator.py`, line 811, change:
```python
ALLOWED_CATEGORIES = {"review", "test", "validation", "spec", "doc", "code_quality", "verification", "research"}
```
to:
```python
ALLOWED_CATEGORIES = {"review", "test", "validation", "spec", "doc", "code_quality", "verification", "research", "creative"}
```

- [ ] **Step 2: Add OVERNIGHT_CREATIVE_PROMPT to orchestrator**

In `scripts/overnight_orchestrator.py`, after line 133 (after the OVERNIGHT_RESEARCH_PROMPT closing `"""`), add:

```python
OVERNIGHT_CREATIVE_PROMPT = """OVERNIGHT AUTONOMOUS MODE — KR Pipeline Project — CREATIVE RESEARCH TASK.
You are executing a creative research task in the overnight autonomous system.

ABSOLUTE RULES — SAFETY:
- NEVER modify any source code files (engines/*/src/, shared/*/src/)
- NEVER create new files under engines/ or shared/
- NEVER modify .claude/settings.json or .claude/rules/
- NEVER run git push or git commit
- NEVER delete any file or directory
- There is no human present — do not ask questions
- Write ALL output to overnight/results/{TASK_ID}/

CREATIVE RESEARCH RULES:
- Your job is to produce research reports, adversarial test data, or architectural analysis
- You may generate JSON data files (adversarial test cases, structured findings)
- You may write markdown reports with analysis and recommendations
- Use web search extensively for innovation/cross-pollination tasks
- Cite specific URLs, version numbers, and benchmarks for every claim
- Be bold and creative — challenge assumptions, propose alternatives
- If you find actionable items, write them to overnight/results/{TASK_ID}/actionable.json as:
  [{"id": "CREATIVE-{date}-NNN", "category": "BUG|IMP|EXT|ARCH|DOM", "summary": "...", "source_report": "...", "effort": "S|M|L", "priority": "HIGH|MEDIUM|LOW"}]

Read CLAUDE.md and .claude/rules/*.
"""
```

- [ ] **Step 3: Route creative category to creative prompt in orchestrator**

In `scripts/overnight_orchestrator.py`, at line 690, change:

```python
    if task.category == "research":
        safety_prompt = OVERNIGHT_RESEARCH_PROMPT.replace("{TASK_ID}", task.task_id)
```

to:

```python
    if task.category == "creative":
        safety_prompt = OVERNIGHT_CREATIVE_PROMPT.replace("{TASK_ID}", task.task_id)
    elif task.category == "research":
        safety_prompt = OVERNIGHT_RESEARCH_PROMPT.replace("{TASK_ID}", task.task_id)
```

- [ ] **Step 4: Verify no syntax errors**

Run:
```bash
python -c "import scripts.overnight_orchestrator; print('OK')"
python -c "import scripts.overnight_task_generator; print('OK')"
```
Expected: Both print `OK`.

- [ ] **Step 5: Commit**

```bash
git add scripts/overnight_orchestrator.py scripts/overnight_task_generator.py
git commit -m "feat(overnight): add creative task category with dedicated safety prompt"
```

---

### Task 2: Create creative template loader and scanner

**Files:**
- Modify: `scripts/overnight_task_generator.py` (add creative_scanner function + register in scanners list)
- Create: `overnight/creative_run_log.json`

- [ ] **Step 1: Add imports at top of task generator**

In `scripts/overnight_task_generator.py`, after existing imports, add:

```python
from datetime import date as date_type
```

(Already has `json`, `Path`, `dataclass`, `subprocess` — verify before adding duplicates.)

- [ ] **Step 2: Add template loading and scanner functions**

In `scripts/overnight_task_generator.py`, before the `generate_manifest()` function (before line 775), add:

```python
# ---------------------------------------------------------------------------
# Creative task scanner (#10)
# ---------------------------------------------------------------------------

CREATIVE_TEMPLATES_DIR = Path("overnight/creative_templates")
CREATIVE_RUN_LOG = Path("overnight/creative_run_log.json")
PIPELINE_ORDER = ["source", "normalization", "excerpting", "taxonomy", "synthesis"]
GEMINI_MAX_PER_RUN = 10


def _load_creative_run_log() -> dict[str, str]:
    """Load the creative run log (template_id:target → last_run_date)."""
    if CREATIVE_RUN_LOG.exists():
        data = json.loads(CREATIVE_RUN_LOG.read_text(encoding="utf-8"))
        return data.get("runs", {})
    return {}


def _detect_active_engine() -> str:
    """Parse NEXT.md for the active engine name."""
    next_md = Path("NEXT.md")
    if next_md.exists():
        text = next_md.read_text(encoding="utf-8")
        for engine in PIPELINE_ORDER:
            if engine.lower() in text[:500].lower():
                return engine
    return "excerpting"  # fallback


def _load_creative_templates() -> list[dict]:
    """Load all JSON templates from overnight/creative_templates/."""
    templates = []
    if not CREATIVE_TEMPLATES_DIR.exists():
        return templates
    for f in sorted(CREATIVE_TEMPLATES_DIR.rglob("*.json")):
        try:
            tmpl = json.loads(f.read_text(encoding="utf-8"))
            templates.append(tmpl)
        except (json.JSONDecodeError, OSError) as e:
            print(f"  WARNING: Failed to load template {f}: {e}")
    return templates


def _days_since(date_str: str) -> int:
    """Days since a YYYY-MM-DD date string."""
    last = date_type.fromisoformat(date_str)
    return (date_type.today() - last).days


def _resolve_variable(var_def: dict, active_engine: str) -> str:
    """Resolve a single template variable."""
    source = var_def.get("source", "literal")
    if source == "active_engine":
        return active_engine
    if source == "literal":
        return var_def.get("value", "")
    if source == "run_date":
        return date_type.today().isoformat()
    return var_def.get("fallback", "unknown")


def _instantiate_prompt(prompt_template: str, variables: dict[str, str]) -> str:
    """Fill template variables in prompt."""
    result = prompt_template
    for key, value in variables.items():
        result = result.replace(f"{{{key}}}", value)
    # Always fill run_date
    result = result.replace("{run_date}", date_type.today().isoformat())
    return result


def scan_creative() -> list[TaskDef]:
    """Scanner #10: Generate creative research tasks from templates."""
    templates = _load_creative_templates()
    if not templates:
        return []

    run_log = _load_creative_run_log()
    active_engine = _detect_active_engine()
    today = date_type.today().isoformat()
    tasks: list[TaskDef] = []
    gemini_count = 0

    for tmpl in templates:
        template_id = tmpl["template_id"]
        cooldown = tmpl.get("cooldown_days", 14)

        # Check cooldown
        log_key = f"{template_id}:{active_engine}"
        last_run = run_log.get(log_key)
        if last_run and _days_since(last_run) < cooldown:
            continue

        # Gemini quota guard
        exec_mode = tmpl.get("execution_mode", "cli")
        if exec_mode == "gemini":
            if gemini_count >= GEMINI_MAX_PER_RUN:
                continue
            gemini_count += 1

        # Resolve variables
        var_defs = tmpl.get("variables", {})
        resolved = {k: _resolve_variable(v, active_engine) for k, v in var_defs.items()}
        resolved["run_date"] = today
        resolved["task_id"] = template_id.replace("/", "-") + "-" + active_engine

        # Instantiate prompt
        prompt = _instantiate_prompt(tmpl["prompt_template"], resolved)

        # Build task ID
        task_id = f"creative-{resolved['task_id']}"

        tasks.append(TaskDef(
            task_id=task_id,
            name=tmpl["name"].replace("{target}", active_engine),
            category="creative",
            prompt=prompt,
            safety_level=tmpl.get("safety_level", "readonly"),
            execution_mode=exec_mode,
            model=tmpl.get("model", "opus"),
            max_budget_usd=tmpl.get("max_budget_usd", 5.0),
            timeout_minutes=tmpl.get("timeout_minutes", 30),
            max_turns=tmpl.get("max_turns", 50),
            priority=2,  # Between critical hardening (1) and nice-to-have (3)
        ))

    return tasks
```

- [ ] **Step 3: Register creative scanner in the scanners list**

In `scripts/overnight_task_generator.py`, in the `generate_manifest()` function, add to the scanners list (after line 798):

```python
        ("Creative Research", scan_creative),
```

So the list becomes:
```python
    scanners = [
        ("Knowledge Integrity", scan_knowledge_integrity),
        ("Recent Changes", scan_recent_changes),
        ("Test Health", scan_test_health),
        ("SPEC Quality", scan_spec_quality),
        ("Code Quality", scan_code_quality),
        ("Corpus Integrity", scan_corpus_integrity),
        ("Contract Boundaries", scan_contract_boundaries),
        ("Known Limitations", scan_known_limitations),
        ("Documentation", scan_documentation),
        ("Empirical Validations", scan_empirical_validations),
        ("Model Research", scan_model_research),
        ("Creative Research", scan_creative),
    ]
```

- [ ] **Step 4: Initialize the creative run log**

```bash
echo '{"runs": {}}' > overnight/creative_run_log.json
```

- [ ] **Step 5: Verify scanner loads and produces 0 tasks (no templates yet)**

```bash
python -c "
from scripts.overnight_task_generator import scan_creative
tasks = scan_creative()
print(f'Creative tasks: {len(tasks)}')
assert len(tasks) == 0, 'Expected 0 tasks (no templates exist yet)'
print('OK')
"
```
Expected: `Creative tasks: 0` then `OK`.

- [ ] **Step 6: Commit**

```bash
git add scripts/overnight_task_generator.py overnight/creative_run_log.json
git commit -m "feat(overnight): add creative scanner with template loading and cooldown logic"
```

---

### Task 3: Create the first 3 creative templates (innovation)

**Files:**
- Create: `overnight/creative_templates/innovation/technology_survey.json`
- Create: `overnight/creative_templates/innovation/architecture_challenge.json`
- Create: `overnight/creative_templates/innovation/cost_efficiency.json`

These are the highest-value templates from the manual sprint. Each contains the full prompt that was proven to work.

- [ ] **Step 1: Create directory structure**

```bash
mkdir -p overnight/creative_templates/innovation
mkdir -p overnight/creative_templates/adversarial
mkdir -p overnight/creative_templates/spec_challenge
mkdir -p overnight/creative_templates/edge_testing
```

- [ ] **Step 2: Create technology_survey.json**

Write to `overnight/creative_templates/innovation/technology_survey.json`:
```json
{
  "template_id": "innovation/technology_survey",
  "name": "Technology Survey for {target}",
  "description": "Research Arabic NLP tools and libraries for the {target} engine",
  "category": "creative",
  "subcategory": "innovation",
  "execution_mode": "cli",
  "preferred_provider": "claude",
  "safety_level": "readonly",
  "model": "opus",
  "timeout_minutes": 35,
  "max_turns": 50,
  "max_budget_usd": 5.0,
  "cooldown_days": 14,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "You are researching Arabic NLP tools and technologies for the KR project's {target} engine.\n\nCONTEXT: KR processes Islamic scholarly Arabic texts through a 5-engine pipeline. The {target} engine is currently active.\n\nRead CLAUDE.md for pipeline overview, then engines/{target}/SPEC.md for this engine's behavioral rules.\n\nRESEARCH (use web search extensively, minimum 8 searches):\n1. What Arabic NLP libraries exist (2024-2026) that this project is NOT using? Check: CAMeL Tools, Farasa, AraBERT, Stanza Arabic, any new libraries.\n2. Pre-trained models for Islamic scholarly text (genre classification, hadith detection, Quranic citation).\n3. Arabic text segmentation tools better than structural-boundary chunking.\n4. Competing projects: OpenITI, Usul.ai, Quranic Arabic Corpus, Shamela internals.\n5. Arabic embedding models for pre-filtering or clustering.\n\nFor each tool: what it does, integration path with {target}, effort (S/M/L), value (1-5).\n\nWrite findings to overnight/results/{task_id}/report.md with a summary table ranked by value-to-effort.\n\nIf you find actionable items, also write overnight/results/{task_id}/actionable.json as:\n[{\"id\": \"CREATIVE-{run_date}-NNN\", \"category\": \"EXT\", \"summary\": \"...\", \"source_report\": \"report.md\", \"effort\": \"S|M|L\", \"priority\": \"HIGH|MEDIUM|LOW\"}]"
}
```

- [ ] **Step 3: Create architecture_challenge.json**

Write to `overnight/creative_templates/innovation/architecture_challenge.json`:
```json
{
  "template_id": "innovation/architecture_challenge",
  "name": "Architecture Challenge for {target}",
  "description": "Devil's advocate review of {target} engine architecture",
  "category": "creative",
  "subcategory": "innovation",
  "execution_mode": "cli",
  "preferred_provider": "claude",
  "safety_level": "readonly",
  "model": "opus",
  "timeout_minutes": 35,
  "max_turns": 50,
  "max_budget_usd": 5.0,
  "cooldown_days": 21,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "You are an architecture reviewer challenging the KR pipeline's {target} engine.\n\nRead CLAUDE.md (pipeline overview), engines/{target}/contracts.py, and engines/{target}/SPEC.md.\nAlso read any adjacent engine contracts (upstream and downstream).\n\nThen play devil's advocate:\n1. What is OVER-ENGINEERED? Could this be simpler?\n2. What is the WEAKEST ASSUMPTION that will break first?\n3. Where are LLM calls doing work that embeddings or rules could do cheaper?\n4. What would a 10x simpler version look like?\n5. What capability is MISSING that a scholarly library needs?\n6. Are there dead/unused contract fields?\n\nBe specific. Quote contract fields. Reference file:line. Sacred cows should be questioned.\n\nWrite to overnight/results/{task_id}/report.md\nWrite actionable items to overnight/results/{task_id}/actionable.json"
}
```

- [ ] **Step 4: Create cost_efficiency.json**

Write to `overnight/creative_templates/innovation/cost_efficiency.json`:
```json
{
  "template_id": "innovation/cost_efficiency",
  "name": "Cost Efficiency Analysis for {target}",
  "description": "Find speed and cost optimizations in {target} engine LLM calls",
  "category": "creative",
  "subcategory": "innovation",
  "execution_mode": "cli",
  "preferred_provider": "claude",
  "safety_level": "readonly",
  "model": "opus",
  "timeout_minutes": 30,
  "max_turns": 40,
  "max_budget_usd": 5.0,
  "cooldown_days": 21,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "You are a performance engineer analyzing the KR pipeline's {target} engine for speed and cost optimizations.\n\nRead all LLM call sites in engines/{target}/src/ and shared/llm/cli_adapter.py.\n\nAnalyze and propose:\n1. Parallel execution — can chunk processing be parallelized? What's the speedup?\n2. Smart skipping — can we skip LLM calls for 'easy' cases?\n3. Batching — can multiple items share one LLM call?\n4. Caching — any prompt-level or response-level caching opportunities?\n5. Model size — can smaller/faster models handle some tasks?\n6. Rule-based extraction — can any LLM field be computed deterministically?\n\nFor each optimization: estimated speedup (Nx), effort (S/M/L), accuracy risk (none/low/medium/high), recommendation.\n\nWrite to overnight/results/{task_id}/report.md\nWrite actionable items to overnight/results/{task_id}/actionable.json"
}
```

- [ ] **Step 5: Verify scanner now finds 3 templates**

```bash
python -c "
from scripts.overnight_task_generator import scan_creative
tasks = scan_creative()
print(f'Creative tasks: {len(tasks)}')
for t in tasks:
    print(f'  {t.task_id}: {t.name} [{t.execution_mode}]')
assert len(tasks) == 3, f'Expected 3 tasks, got {len(tasks)}'
print('OK')
"
```
Expected: 3 tasks listed, then `OK`.

- [ ] **Step 6: Commit**

```bash
git add overnight/creative_templates/innovation/
git commit -m "feat(overnight): add 3 innovation templates (technology survey, architecture challenge, cost efficiency)"
```

---

### Task 4: Create adversarial + spec_challenge + edge_testing templates

**Files:**
- Create: `overnight/creative_templates/adversarial/t1_text_corruption.json`
- Create: `overnight/creative_templates/adversarial/t2_attribution_error.json`
- Create: `overnight/creative_templates/spec_challenge/cross_provider_review.json`
- Create: `overnight/creative_templates/edge_testing/arabic_extremes.json`

- [ ] **Step 1: Create t1_text_corruption.json (Codex)**

Write to `overnight/creative_templates/adversarial/t1_text_corruption.json`:
```json
{
  "template_id": "adversarial/t1_text_corruption",
  "name": "T-1 Silent Text Corruption Samples for {target}",
  "description": "Generate adversarial Arabic text where a single diacritic change reverses meaning",
  "category": "creative",
  "subcategory": "adversarial",
  "execution_mode": "codex",
  "preferred_provider": "codex",
  "safety_level": "readonly",
  "model": "gpt-5.4",
  "timeout_minutes": 20,
  "max_turns": 30,
  "max_budget_usd": 0,
  "cooldown_days": 14,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "Generate 5 synthetic Arabic scholarly text samples for threat T-1: Silent Text Corruption.\n\nEach sample: a realistic Arabic scholarly passage (fiqh, hadith, or tafsir) where a SINGLE diacritic change reverses the meaning of a legal ruling. Both original and corrupted must be grammatically correct Arabic.\n\nExamples of diacritic-sensitive pairs:\n- عَلِمَ (he knew) vs عُلِمَ (it was known)\n- حَرَّمَ (he forbade) vs حَرُمَ (it became sacred)\n- فَرَضَ (he obligated) vs فُرِضَ (it was obligated)\n\nFor each sample, output valid JSON:\n{\"id\": \"T1-001\", \"threat\": \"T-1\", \"genre\": \"fiqh|hadith|tafsir\", \"original_text\": \"...\", \"corrupted_text\": \"...\", \"changed_word_original\": \"...\", \"changed_word_corrupted\": \"...\", \"original_meaning\": \"...\", \"corrupted_meaning\": \"...\", \"corruption_type\": \"...\", \"ground_truth\": \"Pipeline must preserve exact diacritics from frozen source.\"}\n\nOutput ONLY a JSON array of 5 objects. Real Arabic scholarly text only."
}
```

- [ ] **Step 2: Create t2_attribution_error.json (Codex)**

Write to `overnight/creative_templates/adversarial/t2_attribution_error.json`:
```json
{
  "template_id": "adversarial/t2_attribution_error",
  "name": "T-2 Attribution Error Samples for {target}",
  "description": "Generate multi-layer Arabic texts where quote-refutation splitting causes attribution errors",
  "category": "creative",
  "subcategory": "adversarial",
  "execution_mode": "codex",
  "preferred_provider": "codex",
  "safety_level": "readonly",
  "model": "gpt-5.4",
  "timeout_minutes": 20,
  "max_turns": 30,
  "max_budget_usd": 0,
  "cooldown_days": 14,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "Generate 5 synthetic multi-layer Arabic scholarly texts for threat T-2: Attribution Error.\n\nEach: Scholar A quotes Scholar B's position to REFUTE it. The quote and refutation are separated by editorial content. If split into separate excerpts, Scholar A appears to HOLD Scholar B's position.\n\nUse real Islamic scholarly patterns:\n- قال الشافعي رحمه الله: ... then والصحيح عندنا أن... (refuting)\n- وذهب أبو حنيفة إلى أن... then وهذا مردود لأن... (rejecting)\n\nFor each, output valid JSON:\n{\"id\": \"T2-001\", \"threat\": \"T-2\", \"scholar_a\": \"...\", \"scholar_b\": \"...\", \"full_text\": \"...\", \"quote_paragraph\": 1, \"refutation_paragraph\": 3, \"separation_type\": \"footnote|editorial|tangent\", \"correct_behavior\": \"Keep quote and refutation in same teaching unit\", \"failure_behavior\": \"Two separate excerpts with wrong attribution\"}\n\nOutput ONLY a JSON array of 5 objects."
}
```

- [ ] **Step 3: Create cross_provider_review.json (Gemini)**

Write to `overnight/creative_templates/spec_challenge/cross_provider_review.json`:
```json
{
  "template_id": "spec_challenge/cross_provider_review",
  "name": "Cross-Provider SPEC Review for {target}",
  "description": "Have Gemini adversarially review {target} engine SPEC for flaws",
  "category": "creative",
  "subcategory": "spec_challenge",
  "execution_mode": "gemini",
  "preferred_provider": "gemini",
  "safety_level": "readonly",
  "model": "gemini",
  "timeout_minutes": 15,
  "max_turns": 20,
  "max_budget_usd": 0,
  "cooldown_days": 21,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "taxonomy" }
  },
  "prompt_template": "You are an expert in Islamic scholarly text processing and software architecture. Critically review this engine SPEC for a pipeline that processes Arabic scholarly texts.\n\nRead engines/{target}/SPEC.md and identify:\n1. Rules that are IMPOSSIBLE to implement as written\n2. Rules that CONTRADICT each other\n3. Arabic text handling assumptions that are WRONG or incomplete\n4. Missing edge cases for Islamic scholarly texts\n5. Contract mismatches with upstream/downstream engines\n\nBe brutal and specific. Quote the problematic text. Write findings to overnight/results/{task_id}/report.md"
}
```

- [ ] **Step 4: Create arabic_extremes.json (Claude)**

Write to `overnight/creative_templates/edge_testing/arabic_extremes.json`:
```json
{
  "template_id": "edge_testing/arabic_extremes",
  "name": "Arabic Extreme Edge Case Tests for {target}",
  "description": "Generate extreme Arabic text edge case tests for {target} engine",
  "category": "creative",
  "subcategory": "edge_testing",
  "execution_mode": "cli",
  "preferred_provider": "claude",
  "safety_level": "readonly",
  "model": "opus",
  "timeout_minutes": 35,
  "max_turns": 50,
  "max_budget_usd": 5.0,
  "cooldown_days": 21,
  "applicable_when": {
    "engine_exists": true
  },
  "variables": {
    "target": { "source": "active_engine", "fallback": "excerpting" }
  },
  "prompt_template": "Generate EXTREME Arabic text edge case tests for the KR pipeline's {target} engine.\n\nRead .claude/rules/arabic-scholarly-conventions.md and .claude/rules/regex-arabic-digits.md for domain knowledge. Then read engines/{target}/src/ to understand what functions process Arabic text.\n\nWrite a comprehensive pytest test file to overnight/results/{task_id}/test_arabic_extremes.py covering:\n1. Unicode boundary cases (diacritics-only, hamza variants, tatweel, presentation forms)\n2. Scholarly edge cases (50-narrator isnad, nested quotations, entire-verse excerpts)\n3. Encoding edge cases (BOM, ZWNJ, mixed RTL/LTR, dangerous invisible characters)\n4. Size extremes (empty, 1 char, 100K chars)\n5. Regex traps (Arabic-Indic digits, word boundaries with clitics)\n\nUse real Arabic text. Run the tests and report which pass/fail. Failures are GOOD — they found edge cases.\n\nWrite actionable items to overnight/results/{task_id}/actionable.json"
}
```

- [ ] **Step 5: Verify scanner finds all templates**

```bash
python -c "
from scripts.overnight_task_generator import scan_creative
tasks = scan_creative()
print(f'Creative tasks: {len(tasks)}')
for t in tasks:
    print(f'  [{t.execution_mode:6s}] {t.task_id}: {t.name}')
assert len(tasks) >= 7, f'Expected >=7 tasks, got {len(tasks)}'
print('OK')
"
```
Expected: 7 tasks (3 innovation + 2 adversarial + 1 spec_challenge + 1 edge_testing).

- [ ] **Step 6: Commit**

```bash
git add overnight/creative_templates/
git commit -m "feat(overnight): add 4 more templates (adversarial T-1/T-2, spec challenge, edge testing)"
```

---

### Task 5: Add run log update to orchestrator

**Files:**
- Modify: `scripts/overnight_orchestrator.py` (update creative_run_log.json after creative tasks)

- [ ] **Step 1: Add run log update function**

In `scripts/overnight_orchestrator.py`, after the `_check_partial_success()` function (after line 747), add:

```python
def _update_creative_run_log(task_id: str) -> None:
    """Record that a creative task ran (for cooldown tracking)."""
    log_path = OVERNIGHT_DIR / "creative_run_log.json"
    log_data: dict[str, Any] = {"runs": {}}
    if log_path.exists():
        try:
            log_data = json.loads(log_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            pass

    # Extract template_id:engine from task_id like "creative-innovation-technology_survey-excerpting"
    # Remove "creative-" prefix and use the rest as the key
    key = task_id.removeprefix("creative-")
    log_data.setdefault("runs", {})[key] = date.today().isoformat()

    _atomic_write(log_path, json.dumps(log_data, indent=2, ensure_ascii=False))
```

- [ ] **Step 2: Add `from datetime import date` import**

Verify the import exists. If not, add at the top of the file:
```python
from datetime import date
```

- [ ] **Step 3: Call run log update after creative task execution**

In the main execution loop (after the result is recorded, around line 733), add:

```python
    # Update creative run log for cooldown tracking
    if task.category == "creative":
        _update_creative_run_log(task.task_id)
```

This goes right after `result_file` is written (line 733) and before `return result` (line 735).

- [ ] **Step 4: Verify no syntax errors**

```bash
python -c "import scripts.overnight_orchestrator; print('OK')"
```

- [ ] **Step 5: Commit**

```bash
git add scripts/overnight_orchestrator.py
git commit -m "feat(overnight): update creative run log after task completion for cooldown tracking"
```

---

### Task 6: Create the post-run findings appender

**Files:**
- Create: `scripts/append_creative_findings.py`
- Modify: `scripts/start_overnight.sh` (call appender after orchestrator)

- [ ] **Step 1: Create append_creative_findings.py**

Write to `scripts/append_creative_findings.py`:
```python
"""Append actionable findings from creative overnight tasks to FINDINGS_TRACKER.md.

Reads all actionable.json files from overnight/results/creative-*/*/
and appends new items to FINDINGS_TRACKER.md under the appropriate section.
Deduplicates by exact summary match.
"""
from __future__ import annotations

import json
import re
from pathlib import Path


FINDINGS_TRACKER = Path("FINDINGS_TRACKER.md")
OVERNIGHT_RESULTS = Path("overnight/results")

# Map creative categories to FINDINGS_TRACKER sections
SECTION_MAP = {
    "BUG": "## BUGS (fix immediately)",
    "IMP": "## READY TO IMPLEMENT (next 1-2 sessions)",
    "EXT": "## EXTERNAL INTEGRATIONS (high value, low effort)",
    "ARCH": "## ARCHITECTURE (design sessions needed)",
    "DOM": "## DOMAIN KNOWLEDGE (expert review needed)",
    "TAX": "## INTEGRATE BEFORE TAXONOMY BUILD (blocks next engine)",
}


def load_existing_summaries(tracker_text: str) -> set[str]:
    """Extract existing item summaries to avoid duplicates."""
    summaries: set[str] = set()
    for line in tracker_text.splitlines():
        # Match "- [ ] XXX-NNN: summary" or "- [x] XXX-NNN: summary"
        m = re.match(r"^- \[[ x]\] \w+-[0-9]+: (.+)$", line)
        if m:
            summaries.add(m.group(1).strip())
    return summaries


def collect_actionable_items() -> list[dict]:
    """Find all actionable.json files from creative runs."""
    items: list[dict] = []
    for f in OVERNIGHT_RESULTS.rglob("actionable.json"):
        if "creative" in str(f):
            try:
                data = json.loads(f.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    items.extend(data)
            except (json.JSONDecodeError, OSError):
                continue
    return items


def append_to_tracker(items: list[dict]) -> int:
    """Append new actionable items to FINDINGS_TRACKER.md. Returns count added."""
    if not FINDINGS_TRACKER.exists():
        print("FINDINGS_TRACKER.md not found — skipping")
        return 0

    tracker_text = FINDINGS_TRACKER.read_text(encoding="utf-8")
    existing = load_existing_summaries(tracker_text)
    added = 0

    for item in items:
        summary = item.get("summary", "").strip()
        if not summary or summary in existing:
            continue

        category = item.get("category", "IMP")
        item_id = item.get("id", f"CREATIVE-{added:03d}")
        effort = item.get("effort", "M")
        priority = item.get("priority", "MEDIUM")
        source = item.get("source_report", "")

        section_header = SECTION_MAP.get(category, SECTION_MAP["IMP"])
        line = f"- [ ] {item_id}: {summary} ({effort} effort, {priority}) [{source}]"

        # Find the section and append after last item in it
        idx = tracker_text.find(section_header)
        if idx == -1:
            # Append to end if section not found
            tracker_text += f"\n{line}\n"
        else:
            # Find next section header or end of file
            next_section = tracker_text.find("\n## ", idx + len(section_header))
            if next_section == -1:
                insert_pos = len(tracker_text)
            else:
                insert_pos = next_section
            tracker_text = tracker_text[:insert_pos].rstrip() + "\n" + line + "\n" + tracker_text[insert_pos:]

        existing.add(summary)
        added += 1

    if added > 0:
        FINDINGS_TRACKER.write_text(tracker_text, encoding="utf-8")
        print(f"Appended {added} new items to FINDINGS_TRACKER.md")
    else:
        print("No new actionable items to append")

    return added


if __name__ == "__main__":
    items = collect_actionable_items()
    print(f"Found {len(items)} actionable items in creative results")
    append_to_tracker(items)
```

- [ ] **Step 2: Add call to start_overnight.sh**

In `scripts/start_overnight.sh`, after the orchestrator call, add:

```bash
# Append creative findings to tracker
echo "Appending creative findings to FINDINGS_TRACKER.md..."
python scripts/append_creative_findings.py
```

- [ ] **Step 3: Test the appender with no data**

```bash
python scripts/append_creative_findings.py
```
Expected: `Found 0 actionable items in creative results` and `No new actionable items to append`.

- [ ] **Step 4: Commit**

```bash
git add scripts/append_creative_findings.py scripts/start_overnight.sh
git commit -m "feat(overnight): add post-run findings appender for creative task tracking"
```

---

### Task 7: End-to-end verification

- [ ] **Step 1: Generate manifest with creative tasks (dry run)**

```bash
python scripts/overnight_task_generator.py --dry-run
```
Expected: Output includes both hardening tasks AND creative tasks (labeled `[cli]`, `[codex]`, `[gemini]`).

- [ ] **Step 2: Verify creative tasks appear in generated manifest**

```bash
python scripts/overnight_task_generator.py --output overnight/test_manifest.json
python -c "
import json
data = json.loads(open('overnight/test_manifest.json').read())
creative = [t for t in data['tasks'] if t['category'] == 'creative']
hardening = [t for t in data['tasks'] if t['category'] != 'creative']
print(f'Hardening: {len(hardening)}, Creative: {len(creative)}')
for t in creative:
    print(f'  [{t[\"execution_mode\"]:6s}] {t[\"task_id\"]}')
"
```
Expected: Mix of hardening and creative tasks.

- [ ] **Step 3: Run a single creative task manually to verify dispatch**

Pick the technology_survey task from the manifest and run it:
```bash
claude -p "$(python -c "
import json
data = json.loads(open('overnight/test_manifest.json').read())
for t in data['tasks']:
    if 'technology_survey' in t['task_id']:
        print(t['prompt'][:500])
        break
")" --output-format json --max-turns 10 --max-budget-usd 2
```
Expected: Task runs and produces output (even if truncated by budget).

- [ ] **Step 4: Verify cooldown by regenerating**

```bash
# Manually set a run log entry
python -c "
import json
from datetime import date
data = {'runs': {'innovation-technology_survey-excerpting': date.today().isoformat()}}
open('overnight/creative_run_log.json', 'w').write(json.dumps(data, indent=2))
"
# Regenerate — technology_survey should be skipped
python -c "
from scripts.overnight_task_generator import scan_creative
tasks = scan_creative()
ids = [t.task_id for t in tasks]
assert 'creative-innovation-technology_survey-excerpting' not in ids, 'Cooldown failed!'
print(f'Tasks after cooldown: {len(tasks)} (technology_survey correctly skipped)')
print('OK')
"
```

- [ ] **Step 5: Clean up test manifest and reset run log**

```bash
rm -f overnight/test_manifest.json
echo '{"runs": {}}' > overnight/creative_run_log.json
```

- [ ] **Step 6: Final commit**

```bash
git add -A
git commit -m "chore(overnight): verify creative expansion end-to-end"
```
