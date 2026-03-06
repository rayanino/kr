# Pipeline Testing Architecture — هندسة اختبار الأنبوب

Based on: Anthropic's C compiler case study (16 agents, 2000 sessions), Claude Code non-interactive mode, Agent Teams, Claude-Autopilot, and the core insight that **the test environment determines autonomous quality, not the agent**.

---

## The Core Insight

From Anthropic's own engineering blog on building a C compiler with parallel Claude agents:

> "Most of my effort went into designing the environment around Claude — the tests, the environment, the feedback — so that it could orient itself without me."

The implication for KR: **don't build a test framework. Build a test environment so well-designed that Claude Code can process 500 sources, evaluate its own output, fix its own bugs, and keep going — overnight, unattended.**

---

## Architecture: The Self-Testing Pipeline

```
┌─────────────────────────────────────────────────────────┐
│                    TEST HARNESS                          │
│                                                         │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐          │
│  │ Pipeline │───▶│ Evaluator│───▶│ Reporter │          │
│  │ Runner   │    │ (rubrics)│    │ (metrics)│          │
│  └──────────┘    └──────────┘    └──────────┘          │
│       │                │               │                │
│       ▼                ▼               ▼                │
│  pipeline_output/  findings/       metrics/             │
│                                                         │
│  ┌──────────┐                                          │
│  │ Fixer    │◀── reads findings, patches engines        │
│  │          │──▶ re-runs source to verify fix           │
│  └──────────┘                                          │
│                                                         │
│  ┌──────────┐                                          │
│  │ Owner    │◀── NEEDS_OWNER.md (flagged 10%)          │
│  │ Review   │──▶ owner responds, finding resolved       │
│  └──────────┘                                          │
└─────────────────────────────────────────────────────────┘
```

### Component 1: Pipeline Runner

The pipeline itself, built as a CLI:

```bash
kr-pipeline run sources/ibn_aqil/ --output results/ibn_aqil/
kr-pipeline run-batch sources/ --output results/ --parallel 3
kr-pipeline check  # health check: all engines respond, deps present
```

This is what Claude Code builds in Phase 2. Nothing special — it's just the 7 engines wired together as a callable tool.

### Component 2: Evaluator (THIS is the hard part)

The evaluator is NOT generic quality checking. It's a set of **structured rubrics** — specific questions with defined correct-answer criteria that Claude Code can evaluate autonomously.

```python
# evaluation/rubrics/source_rubric.py

RUBRICS = [
    {
        "id": "SRC-001",
        "name": "Author identification accuracy",
        "check": "Does source_metadata.author match the actual author of this work?",
        "method": "llm_verify",  # Claude evaluates using its training knowledge
        "prompt": """
            The pipeline identified the author of "{title}" as "{author}".
            Is this correct? Respond with:
            - CORRECT if this is the right author
            - WRONG: [correct author] if this is wrong
            - UNCERTAIN if you cannot determine
        """,
        "severity": "CRITICAL",  # wrong author = knowledge corruption
        "auto_fixable": False,   # needs SPEC/code change, not data fix
    },
    {
        "id": "SRC-002", 
        "name": "Genre classification",
        "check": "Is the genre (sharh/matn/hashiyah/mukhtasar/...) correct?",
        "method": "llm_verify",
        "prompt": """
            The pipeline classified "{title}" by "{author}" as genre: "{genre}".
            Is this correct? The actual genre of this work is:
        """,
        "severity": "HIGH",
    },
    {
        "id": "SRC-003",
        "name": "Death date accuracy",
        "check": "Is the author death date within ±5 years of the actual date?",
        "method": "llm_verify",
        "prompt": """
            The pipeline recorded death date {death_date} AH for scholar {author}.
            The accepted death date for this scholar is:
        """,
        "severity": "HIGH",
    },
    # ... 20+ rubrics per engine
]
```

```python
# evaluation/rubrics/excerpting_rubric.py

RUBRICS = [
    {
        "id": "EXC-001",
        "name": "Self-containment",
        "check": "Can a reader understand this excerpt without reading what comes before/after?",
        "method": "llm_verify",
        "prompt": """
            Read this excerpt from an Islamic scholarly text:
            
            "{excerpt_text}"
            
            Can a reader understand the main point WITHOUT reading the surrounding context?
            
            - PASS: The excerpt is self-contained. The topic and argument are clear.
            - FAIL: [reason] — e.g., "starts with 'والقسم الثاني' referencing unnamed first type"
            - BORDERLINE: Understandable but would benefit from context.
        """,
        "severity": "HIGH",
    },
    {
        "id": "EXC-002",
        "name": "Attribution accuracy",
        "check": "Is each opinion attributed to the correct scholar/school?",
        "method": "llm_verify",
        "prompt": """
            This excerpt attributes the following position to {scholar} ({school} school):
            "{position_text}"
            
            Based on your knowledge of Islamic jurisprudence:
            - CORRECT: This is a known position of this scholar/school
            - WRONG: [correct attribution]
            - UNCERTAIN: Cannot verify from training knowledge
        """,
        "severity": "CRITICAL",
    },
    {
        "id": "EXC-003",
        "name": "Isnad integrity",
        "check": "If the excerpt contains a hadith, is the isnad chain intact?",
        "method": "pattern_check",  # deterministic, not LLM
        "pattern": "If text contains حدثنا/أخبرنا/عن, verify the chain is not split across excerpt boundary",
        "severity": "CRITICAL",
    },
]
```

**Key design decision:** The evaluator uses Claude (via API) for scholarly judgments, but with STRUCTURED prompts that produce PARSEABLE responses (CORRECT/WRONG/UNCERTAIN). Not "tell me if this is good" — specific yes/no/maybe questions.

### Component 3: The Autonomous Test Loop

This is a script that Claude Code runs. It can also run unattended via `claude -p`:

```bash
#!/bin/bash
# test_harness/run_full_test.sh
# Processes all sources, evaluates, logs findings, reports metrics

SOURCES_DIR="test_corpus/sources"
RESULTS_DIR="test_corpus/results"
FINDINGS="test_corpus/findings/OPEN.md"
METRICS="test_corpus/metrics"

for source_dir in "$SOURCES_DIR"/*/; do
    source_name=$(basename "$source_dir")
    echo "=== Processing: $source_name ==="
    
    # 1. Run pipeline
    kr-pipeline run "$source_dir" --output "$RESULTS_DIR/$source_name/"
    
    # 2. Run mechanical property tests (deterministic)
    python3 test_harness/check_properties.py "$RESULTS_DIR/$source_name/" \
        >> "$METRICS/${source_name}_properties.json"
    
    # 3. Run scholarly evaluation rubrics (LLM-based)
    python3 test_harness/evaluate_rubrics.py "$RESULTS_DIR/$source_name/" \
        --rubrics evaluation/rubrics/*.py \
        >> "$METRICS/${source_name}_rubrics.json"
    
    # 4. Extract findings
    python3 test_harness/extract_findings.py \
        "$METRICS/${source_name}_properties.json" \
        "$METRICS/${source_name}_rubrics.json" \
        >> "$FINDINGS"
    
    # 5. Generate summary
    python3 test_harness/summarize.py "$METRICS/${source_name}_*.json" \
        > "$METRICS/${source_name}_summary.txt"
done

# 6. Generate overall report
python3 test_harness/overall_report.py "$METRICS/" \
    > "test_corpus/REPORT.md"
```

### Component 4: The Fix Loop

When Claude Code finds failures, it fixes them. This is the tight feedback loop:

```bash
# Claude Code (interactive session or -p mode):
# 1. Read findings
# 2. Fix engine code
# 3. Re-run failed source
# 4. Verify fix
# 5. Run regression on all previous sources

claude -p "
  Read test_corpus/findings/OPEN.md.
  For each CRITICAL finding:
    1. Read the engine SPEC section referenced
    2. Fix the code to match the SPEC
    3. Re-run the pipeline on the failing source
    4. Verify the finding is resolved
    5. Run property tests on ALL previously-tested sources (regression check)
  Mark fixed findings as RESOLVED in OPEN.md.
  If a fix requires a SPEC change (not just code), log it in NEEDS_SPEC_UPDATE.md.
" --dangerously-skip-permissions --max-turns 50
```

### Component 5: Owner Review Interface

The owner sees only what needs human judgment:

```markdown
# test_corpus/findings/NEEDS_OWNER.md

## F-089 (UNCERTAIN — needs your expertise)
Source: حاشية ابن عابدين
Excerpt #34 attributes this position to the Hanafi school:
  "يجوز تقديم الخبر على المبتدأ مطلقاً"
Claude evaluation: UNCERTAIN — this could be a Hanafi-specific position 
or a general grammatical consensus. Cannot determine from training knowledge.

**Your judgment needed:** Is this attribution correct?
Reply in a Claude Chat session or edit this file directly.
```

---

## How It Runs at Scale (500+ Sources)

### Overnight Batch Mode

```bash
# Start before bed. Check results in the morning.
nohup bash test_harness/run_full_test.sh > test_corpus/logs/batch_$(date +%Y%m%d).log 2>&1 &
```

The pipeline processes sources sequentially. Each source takes ~2-5 minutes (engines 1-4 are fast; engines 5-7 need LLM calls). 500 sources ≈ 20-40 hours. Split across 2-3 nights, or use `--parallel 3` to run 3 sources simultaneously.

**Cost estimate (API calls for LLM engines + evaluation):**
- Per source: ~50K tokens for pipeline LLM calls + ~20K for evaluation rubrics = ~70K tokens
- 500 sources × 70K = 35M tokens
- At Claude Sonnet rates (~$3/M input, $15/M output): ~$200-400 total
- Spread across weeks of iterative testing: trivial

### Claude Code Fix Sessions

After each batch run, Claude Code reads the findings and fixes issues:

```
Morning routine:
1. Owner: "Continue the project" (Claude Code session)
2. Claude Code: reads REPORT.md → sees 12 new CRITICAL findings
3. Claude Code: fixes engine code for each finding
4. Claude Code: re-runs failing sources → verifies fixes
5. Claude Code: runs regression on all previous sources
6. Claude Code: updates REPORT.md with new metrics
7. Owner: reviews NEEDS_OWNER.md (5-10 items), responds
```

This can also be fully automated with Claude-Autopilot or `claude -p` in a loop:

```bash
# Auto-fix loop: run until no CRITICAL findings remain
while grep -q "CRITICAL.*OPEN" test_corpus/findings/OPEN.md; do
    claude -p "Read OPEN.md. Fix all CRITICAL findings. Re-run affected sources. 
              Update findings status." \
        --dangerously-skip-permissions --max-turns 100
    sleep 60  # rate limit buffer
done
```

### Agent Teams for Parallel Investigation

When multiple engines have issues simultaneously, use Agent Teams:

```
Create a team to investigate pipeline failures:
- Teammate 1: Fix normalization layer detection issues (findings F-034, F-041, F-055)
- Teammate 2: Fix excerpting self-containment failures (findings F-067, F-072)  
- Teammate 3: Run regression tests on all fixed sources

Coordinate: teammate 3 waits for 1 and 2 to push, then tests.
```

---

## What Claude Code Builds (Phase 2, Revised)

Instead of just "build the pipeline," Claude Code builds:

1. **The pipeline CLI** (`kr-pipeline run/run-batch/check`)
2. **The evaluation framework** (`evaluation/rubrics/*.py` + `test_harness/*.py`)
3. **Property test suite** (`tests/properties/`)
4. **The test runner script** (`test_harness/run_full_test.sh`)
5. **The reporting tools** (`test_harness/summarize.py`, `overall_report.py`)

The pipeline and its test harness are built together. TDD-style: write the rubric, then make the engine pass it.

---

## Trust Graduation

```
Level 0: Pipeline runs without crashing                    → basic
Level 1: Property tests pass on 10 sources                 → functional  
Level 2: Rubric evaluation >90% CORRECT on 50 sources      → reliable
Level 3: Owner spot-checks 50 entries, approves all         → scholar-trusted
Level 4: 500 sources, zero CRITICAL open, owner approves    → production-ready
Level 5: Adversarial sources (bad OCR, ambiguous authors)   → robust
```

Each level is a concrete milestone. Claude Code can self-assess levels 0-2. Levels 3-5 need owner involvement.

---

## Why NOT Paperclip / Complex Orchestration

Paperclip is for "zero-human companies" with org charts and budgets. KR has one pipeline with one user. The complexity doesn't justify:
- Running a Node.js server + PostgreSQL for task management
- Learning a new orchestration framework
- Managing multi-agent coordination overhead

The simpler approach (bash scripts + `claude -p` + structured rubrics) is:
- Debuggable (it's just files and scripts)
- Reproducible (no server state)
- Cheap (no infrastructure cost)
- Reliable (fewer moving parts = fewer failure modes)

If the bash approach hits limits (e.g., need 20 parallel agents), THEN consider Paperclip. Start simple, escalate only when needed.

---

## What Changes in the Post-Prep Plan

The previous POST_PREP_PLAN.md assumed Claude Chat does testing. This revision:

1. **Claude Code builds pipeline + test harness together** (not separately)
2. **Evaluation rubrics replace generic "check quality"** — specific, parseable questions
3. **Batch processing runs overnight** — no human needed for 90% of evaluation  
4. **Owner reviews only NEEDS_OWNER.md** — 5-10 items per batch, not per source
5. **Fix loop is Claude Code → Claude Code** — not Claude Chat → Claude Code
6. **Scale is achievable** — 500 sources × $0.50/source = $250 total evaluation cost
