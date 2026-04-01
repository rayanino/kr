---
name: coworker-dispatch
description: Standardized dispatch patterns for the 5 KR coworkers (Codex CLI, Gemini CLI, ChatGPT DR, Claude DR, Gemini DR). Use when dispatching any coworker for excerpting evaluation, questionnaire design, or quality assessment.
---

# Coworker Dispatch Skill

## When To Use
- Before any major milestone in the excerpting hardening operation (OPS-DEC-006)
- When designing the owner Q&A questionnaire (Phase 0)
- When analyzing smoke run or full run output (Phase 1, Phase 3)
- When making content quality decisions that require multi-model confirmation

## Dispatch Patterns

### 1. Codex CLI

**Access:** Direct repo access via `codex exec`
**Strengths:** Schema validation, cross-prompt consistency, statistical analysis, deterministic checks
**Limitations:** No Arabic text understanding, no web access, no scholarly reasoning

**Dispatch template:**
```
codex exec "
TASK: [Specific validation task]
SCOPE: [File paths to examine]
CHECKS:
1. [Specific check 1]
2. [Specific check 2]
3. [Specific check 3]
OUTPUT FORMAT: Structured checklist with PASS/FAIL per check and evidence for each failure.
"
```

**Best used for:**
- Validate JSON schema conformance of excerpt output
- Cross-check prompt templates for consistency (same field names, same expected output format)
- Count-based analysis (excerpt distribution per book, classification frequency, field coverage)
- Verify metadata pass-through (D-023) across pipeline stages
- Detect structural anomalies (empty fields, unexpected nulls, duplicate IDs)

**See also:** `docs/codex/dispatch-templates.md` for specialized Codex dispatch templates (code review, regression hunting, contract audit, Arabic-risk structural review, backend probing).

---

### 2. Gemini CLI

**Access:** Direct repo access via `gemini -p`
**Model:** Gemini 3.1 Pro (major coworker — deep Arabic capability)
**Strengths:** Arabic scholarly accuracy, convention compliance, real-time code analysis
**Limitations:** Structured output reliability (rejected as consensus model for pipeline)

**Dispatch template:**
```
gemini -p "
TASK: [Arabic scholarly review task]
CONTEXT: Read [specific files] for background.
EXCERPTS TO REVIEW: [file path to excerpts.jsonl or specific excerpt IDs]
CHECK AGAINST:
- .claude/rules/arabic-scholarly-conventions.md
- engines/excerpting/SPEC.md §4 [specific section]
OUTPUT FORMAT: Per-excerpt review with:
  - Arabic text fidelity: [PASS/FLAG with specific issue]
  - Scholarly convention compliance: [PASS/FLAG with rule citation]
  - Diacritic preservation: [PASS/FLAG]
  - Honorific handling: [PASS/FLAG]
  - Isnad integrity: [PASS/FLAG if applicable]
"
```

**Best used for:**
- Review Arabic text fidelity in excerpts (diacritics, honorifics, transmission formulas)
- Verify scholarly convention compliance (bismillah handling, colophon patterns, madhab signals)
- Check that excerpt boundaries don't split Arabic structural units (isnad chains, ayat, scholarly formulas)
- Validate genre-specific patterns (fiqh ruling structure, nahw example format, hadith narration chains)

---

### 3. ChatGPT Deep Research

**Access:** Deep Research mode (relay prompt to owner)
**Strengths:** Error pattern analysis, architectural analysis, Q&A design, comparative research
**Limitations:** No direct code execution, no live repo access during DR session

**Relay prompt template (give this to the owner to paste):**
```
I'm working on the KR excerpting engine hardening. Here is the context:

[PASTE: relevant file contents, excerpt examples, or error patterns]

TASK: [Specific analysis or design task]

SPECIFIC QUESTIONS:
1. [Question 1]
2. [Question 2]
3. [Question 3]

Please provide your analysis as a structured report with:
- FINDINGS: numbered list of observations
- PATTERNS: recurring issues or themes
- RECOMMENDATIONS: specific, actionable changes (reference file paths where possible)
- CONFIDENCE: HIGH/MEDIUM/LOW for each recommendation
```

**Best used for:**
- Design the owner Q&A questionnaire structure (question formats, ordering, scoring)
- Analyze error patterns across excerpt runs (what types of errors cluster together?)
- Architectural analysis (is the prompt structure optimal for the model's capabilities?)
- Comparative research (how do other scholarly text extraction systems handle similar problems?)

---

### 4. Claude Deep Research

**Access:** Deep Research mode (relay prompt to owner)
**Strengths:** Scholarly reasoning, boundary quality assessment, edge case identification, Arabic linguistic analysis
**Limitations:** No direct code execution, no live repo access during DR session

**Relay prompt template (give this to the owner to paste):**
```
I'm working on the KR excerpting engine. Here is the context:

[PASTE: relevant SPEC sections, excerpt examples with boundaries, edge cases]

TASK: [Specific scholarly reasoning or boundary analysis task]

FOCUS AREAS:
1. [Area 1 — e.g., "Are these excerpt boundaries at natural scholarly break points?"]
2. [Area 2 — e.g., "Does this excerpt preserve enough context for self-containment?"]
3. [Area 3 — e.g., "Would a student of this Islamic science find this excerpt useful as a standalone unit?"]

Please provide:
- PER-EXCERPT ASSESSMENT: For each example, assess boundary quality and self-containment
- EDGE CASES: Identify cases where the boundary could reasonably be drawn differently
- SCHOLARLY RATIONALE: Explain why each boundary works or doesn't from an Islamic sciences perspective
- RECOMMENDATIONS: Specific prompt or SPEC changes to address any issues
```

**Best used for:**
- Assess whether excerpt boundaries align with natural scholarly structure (kitab/bab/fasl divisions)
- Evaluate self-containment: can a reader understand the excerpt without surrounding context?
- Identify edge cases where khilaf passages, definition pairs, or evidence chains should stay together or be split
- Deep reasoning about scholarly function classification (is this truly a ta'rif, or a qawa'id with embedded definitions?)

---

### 5. Gemini Deep Research

**Access:** Deep Research mode (relay prompt to owner)
**Strengths:** Islamic study methodology, scholarly pedagogy, educational framing
**Limitations:** No repo access, purely advisory on methodology

**Relay prompt template (give this to the owner to paste):**
```
I'm building a personal Islamic scholarly library (KR project) that extracts teaching units from classical texts. Here are sample excerpts:

[PASTE: 3-5 representative excerpts with their classifications and boundaries]

TASK: [Specific methodology or pedagogy question]

QUESTIONS:
1. As an Islamic studies student, would these excerpts be useful as standalone study units?
2. What context would you need alongside each excerpt to make it productive for learning?
3. Are there genre-specific expectations for how content should be chunked? (e.g., fiqh vs hadith vs nahw)
4. What would an ideal "study card" or "knowledge unit" look like for each Islamic science?

Please provide:
- PEDAGOGICAL ASSESSMENT: How well do these excerpts serve as learning units?
- GENRE-SPECIFIC FEEDBACK: Different sciences have different "natural units" — identify these
- STUDY WORKFLOW: How would a student typically navigate between these excerpts?
- RECOMMENDATIONS: How should excerpting adapt for different Islamic sciences?
```

**Best used for:**
- Validate that excerpts serve as effective study units (pedagogical, not just structural)
- Genre-specific feedback: what's the natural "atom" of knowledge in fiqh vs nahw vs hadith vs tafsir?
- Study workflow design: after reading one excerpt, what does the student want next?
- Islamic studies methodology context that neither code analysis nor Arabic NLP can provide

---

## Dispatch Log

After every dispatch, append to `.kr/runtime/dispatch_log.jsonl`:
```json
{"timestamp": "2026-04-01T12:00:00Z", "coworker": "codex", "phase": 0, "task": "schema validation of campaign excerpts", "status": "dispatched"}
```

After receiving results, update:
```json
{"timestamp": "2026-04-01T12:30:00Z", "coworker": "codex", "phase": 0, "task": "schema validation of campaign excerpts", "status": "completed", "result_summary": "23 schema violations found, 5 critical", "findings_file": "path/to/report.md"}
```

## Synthesis Protocol

After all coworkers return for a milestone:
1. Collect all reports
2. Cross-reference: do findings agree? Where do coworkers disagree?
3. For disagreements: investigate the specific excerpt — which coworker is right?
4. Produce a synthesis report: confirmed findings (2+ coworkers agree), disputed findings (disagreement), novel findings (only one coworker noticed)
5. Confirmed findings become action items. Disputed findings go to owner review. Novel findings are investigated further.
