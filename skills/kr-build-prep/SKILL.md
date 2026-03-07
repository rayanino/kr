---
name: kr-build-prep
description: Prepare engine for Claude Code with tech survey, contracts, stubs, CLAUDE.md. Use for "prepare for building", "implementation prep", or when a SPEC is finalized.
---

# KR Build Prep — تحضير البناء

You are preparing a finalized KR engine SPEC for Claude Code implementation. Claude Code is powerful but context-limited — it needs a focused, actionable brief with contracts, stubs, and a clear NEXT.md. Your job is to produce everything Claude Code needs to build correctly on the first attempt.

**The cardinal rule:** Technology survey FIRST. Before designing module stubs, search for existing libraries that do 80% of the work. Claude Code should not reinvent what PyPI already provides.

---

## Procedure

### Step 1: Technology Survey (MANDATORY — DO THIS FIRST)

For every significant processing capability in the SPEC, search for existing tools:

**Search pattern for each capability:**
1. Search: `python library [capability] arabic` (e.g., "python library arabic text segmentation")
2. Search: `[capability] NLP tool 2025 2026` (for recent developments)
3. Search: `[specific tool from RESOURCES.md] [capability]` (verify tools mentioned in SPEC)

**For each tool found, evaluate:**
- Does it support Arabic text? (Many NLP tools don't)
- Does it handle diacritics correctly? (Many Arabic tools strip tashkeel)
- Is it maintained? (Check last commit date, open issues)
- What's the license? (Must be compatible with KR)
- What does it actually do vs. what its README claims? (Read the docs, not just the tagline)

**Produce a Technology Inventory:**

```
## Technology Inventory — [Engine Name]

### Available Libraries
| Capability | Library | Arabic Support | Diacritics | Status | Notes |
|-----------|---------|---------------|-----------|--------|-------|
| PDF text extraction | PyMuPDF | Yes | Preserves | Active | Best for machine-readable PDFs |
| OCR | Mistral OCR API | Yes | Good | Active | Primary OCR per STEERING.md |

### Build vs. Use Decision
| Capability | Decision | Rationale |
|-----------|----------|-----------|
| Shamela HTML parsing | BUILD | No existing parser; format is Shamela-specific |
| PDF metadata extraction | USE PyMuPDF | Handles Arabic PDF metadata well |
| Arabic author name normalization | BUILD on CAMeL | CAMeL does morphology; name normalization is KR-specific |

### Gaps — No Good Tool Exists
| Capability | What's needed | Closest available | Why it's not enough |
|-----------|--------------|-------------------|-------------------|
| Multi-layer text detection | Detect sharh/matn/hashiya layers | Nothing found | Unique to Islamic scholarly texts |
```

### Step 2: Contracts Audit

Verify the Pydantic contracts match the finalized SPEC:

1. **Read the existing contracts.py** for this engine (in `engines/{engine}/contracts.py`)
2. **Compare every field** against the SPEC's §2 (input) and §3 (output) contracts
3. **Check types** — is the SPEC's "list of authors" actually `list[AuthorAttribution]` or `list[str]`?
4. **Check optionality** — fields the SPEC marks as "if available" must be `Optional[T]` in the contract
5. **Check enums** — if the SPEC says "one of: relevant, partially_relevant, not_relevant," there should be a `Literal` or `Enum`
6. **Check metadata pass-through** — every metadata field from upstream must appear in output (D-023)

Produce a contracts diff: what needs to change, what's correct, what's missing.

### Step 3: Module Architecture

Based on the technology survey and SPEC, design the module structure:

```
engines/{engine}/
├── __init__.py
├── contracts.py        # Pydantic models (input/output/internal)
├── engine.py           # Main engine entry point
├── [module_1].py       # First processing module
├── [module_2].py       # Second processing module
└── tests/
    ├── test_[module_1].py
    ├── test_[module_2].py
    └── test_integration.py
```

For each module:
- **Purpose:** One sentence
- **Input/Output:** What it receives and produces
- **External dependencies:** Which libraries from the technology survey
- **SPEC sections:** Which §4 rules it implements
- **Complexity estimate:** Simple (pure logic) / Medium (uses libraries) / Complex (LLM calls)

### Step 4: Stub Files

Write stub files with:
- Correct imports (from the technology survey)
- Function signatures with type hints matching contracts
- Docstrings that quote the relevant SPEC rule
- `raise NotImplementedError("Implements SPEC §X.Y.Z")` as body
- NO function bodies. That is Claude Code's job.

Example:
```python
def detect_text_layers(
    content: NormalizedContent,
    config: LayerDetectionConfig,
) -> list[TextLayer]:
    """Detect sharh/matn/hashiya layers in normalized content.

    SPEC §4.A.5: "The engine identifies text layers by analyzing
    structural markers (font size changes, indentation patterns,
    parenthetical markers) and content markers (قال المصنف, قال الشارح)."

    Returns one TextLayer per detected layer, ordered by nesting depth.
    Single-layer texts return [TextLayer(type='primary', author=source_author)].
    """
    raise NotImplementedError("Implements SPEC §4.A.5")
```

### Step 5: Test Infrastructure

Design the test setup Claude Code needs:

**5a — Deterministic tests:** List specific property checks with pass/fail criteria.
```
- Schema validation: output matches contract (automated via Pydantic)
- Text integrity: no Arabic character loss (compare bytes)
- Metadata preservation: all upstream fields present (D-023 check)
- Required field coverage: no None in required fields
```

**5b — LLM-worker tests:** For each LLM call in the engine, define:
```
- What the LLM is asked to do (e.g., "classify this source's science")
- What correct output looks like (e.g., "nahw" for an Arabic grammar book)
- What test fixtures to use (reference specific files in tests/fixtures/)
- How to judge correctness (exact match? acceptable set? human review?)
```

**5c — LLM-evaluator tests:** For each output type, define:
```
- What an independent LLM should check (e.g., "Is this author attribution correct?")
- The evaluation prompt template
- The scoring rubric (e.g., 1-5 scale with anchor descriptions)
- Which models to use as judges (reference RESEARCH_LOG.md Finding 09)
```

### Step 6: Write CLAUDE.md

Write the engine-specific `CLAUDE.md` file that Claude Code reads at session start:

```markdown
# [Engine Name] — Claude Code Brief

## What You're Building
[One paragraph: what this engine does, what its output feeds into]

## Architecture
[Module list from Step 3, with one-line descriptions]

## Key Constraints
- Arabic text fidelity: diacritics must be preserved byte-for-byte
- Metadata flows forward, never deleted (D-023)
- Errors fail loudly — no silent data loss
- Consensus required for all content decisions
- [Engine-specific constraints from the SPEC]

## Implementation Order
[Which module to build first, second, etc. — based on dependencies]

## Test Fixtures Available
[List the test fixture files in tests/fixtures/ that this engine uses]

## Technology Stack
[From the technology survey: which libraries to install and use]

## What NOT To Do
- Do not modify contracts.py without explicit approval
- Do not implement §4.B capabilities yet — start with §4.A
- Do not optimize for speed — optimize for correctness
- Do not write clever code — write obvious code with clear error messages
```

### Step 7: Write NEXT.md

Write the session-specific `NEXT.md` directive:

```markdown
# NEXT SESSION — [Engine Name] Build [Session N]

## Context
[What was built in previous sessions, if any]

## Task
[Specific modules to build in this session]

## Definition of Done
- [ ] [Module] passes all deterministic tests
- [ ] [Module] handles all error paths in SPEC §7
- [ ] [Module] preserves metadata (D-023 verified)
- [ ] Integration test with [upstream] passes
- [ ] No new warnings from type checker

## Files to Read
[Specific files Claude Code should read before starting]

## Files to Modify
[Specific files Claude Code will work on]
```

---

## Output Summary

When you finish, you should have produced:

1. **Technology Inventory** — what to use, what to build, what's missing
2. **Contracts Diff** — what needs updating in contracts.py
3. **Module Architecture** — the directory structure and module responsibilities
4. **Stub Files** — ready for Claude Code to fill in
5. **Test Infrastructure** — 5a/5b/5c test plans with specific fixtures
6. **CLAUDE.md** — Claude Code's orientation document
7. **NEXT.md** — the first build session's directive

All of these should be written as actual files ready to commit to the repo, not described in prose.

---

## Anti-Patterns

**Building without surveying.** If you design a custom Arabic tokenizer before checking whether CAMeL Tools already does it, you've wasted Claude Code's time and the owner's money.

**Vague stubs.** `def process(input): pass` tells Claude Code nothing. Every stub needs the exact function signature, type hints, and a docstring quoting the SPEC rule it implements.

**Missing test fixtures.** If the test plan references "a Shamela HTML export" but no such fixture exists in tests/fixtures/, Claude Code can't test. Flag missing fixtures explicitly.

**Over-scoping the first session.** The first NEXT.md should target the simplest possible end-to-end path. For the source engine: one format (Shamela HTML), one fixture, schema validation passing. Not all 6 formats.
