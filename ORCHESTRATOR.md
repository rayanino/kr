# KR Implementation Orchestrator

**THIS DOCUMENT IS FOR CLAUDE CODE ONLY.** Claude Chat does not do implementation. If you are Claude Chat reading this: STOP — your process is in `skills/shared/ENGINE_PROTOCOL.md`, your task is in NEXT.md.

This document governs how Claude Code sessions execute implementation work autonomously.
It replaces the SPEC-writing workflow with an implementation-phase workflow.

## ⚠ BUILD GOAL: TESTABLE PIPELINE, NOT THE APPLICATION

The goal of implementation is to build a **testable pipeline CLI** — all 7 engines wired together as a command-line tool that processes real Arabic scholarly sources and produces inspectable output at every stage. This pipeline exists for **stress testing**: running hundreds of sources through it, evaluating output quality, finding bugs, and fixing them iteratively.

**You are NOT building the application** (no GUI, no scholar interface, no FastAPI, no frontend). The application comes LATER, after the pipeline is proven trustworthy through extensive testing. Build every engine so it can:
1. Run from the command line on a real source file
2. Produce human-readable output alongside machine output
3. Be tested independently and as part of the full pipeline chain
4. Report clear metrics (counts, scores, flags) without requiring full output reading

---

## Session Lifecycle

Every Claude Code session follows this lifecycle:

### Phase 1: Orient (≤5 minutes of context)

1. Read `NEXT.md` — the task, context, and files to read.
2. Read the target engine's `CLAUDE.md` for current state.
3. Read the target engine's `SPEC.md` sections relevant to the task.
4. Run `/impl-status` to see what's built across the project.
5. Run existing tests for the target engine.

Do NOT read VISION.md, DOMAIN.md, kr_decisions.md, or other engines' SPECs unless NEXT.md explicitly lists them. Context is finite — spend it on building, not reading.

### Phase 2: Plan (output a task list before coding)

Before writing any code, output a numbered task list:

```
Implementation Plan — [engine/component name]
Task from NEXT.md: [quoted]

1. [Concrete implementation step] → [file to create/modify]
2. [Concrete implementation step] → [file to create/modify]
...
N. Run tests → verify [specific assertions]

Dependencies: [any external needs — API keys, test data, etc.]
Blocked by: [anything that can't proceed — or "nothing"]
```

This plan is ephemeral — it does not get committed. It structures the session.

### Phase 3: Build (the work)

Execute the plan. For each task:

1. Write the code.
2. Run the relevant tests immediately (not at the end).
3. If a test fails, fix it before moving to the next task.
4. If the SPEC is ambiguous about a behavior, check SPEC.md again. If still ambiguous, implement the most conservative interpretation and add a `# SPEC-AMBIGUITY: [description]` comment.

**Before writing any code that processes Arabic text:** Read `.claude/skills/arabic-text/SKILL.md`. Arabic text handling has critical pitfalls that can silently corrupt the library.

**Before building custom code for any capability:** Check `.claude/skills/technology-survey/SKILL.md`. Search for existing tools first. The owner has infinite budget for tools.

**Knowledge integrity rules (from KNOWLEDGE_INTEGRITY.md):**
- Every engine output must pass Layer 1 self-validation before writing to disk.
- Primary text is NEVER modified. No corrections, no cleanup, no normalization beyond what the SPEC explicitly allows.
- Every attribution decision (author, school, date) must use multi-model consensus.
- Every low-confidence decision creates a human gate checkpoint.
- Metadata flows forward, never backward-deleted.

Code standards (from SPEC §4 behavioral rules, not style preferences):
- Every function that can fail returns structured errors, never bare exceptions.
- Every LLM call goes through the consensus module (shared/consensus).
- Every irreversible library change goes through human gate (shared/human_gate).
- Metadata is never stripped — pass through everything from upstream (D-023).
- Log at INFO for normal operations, WARNING for recoverable issues, ERROR for failures.

### Phase 4: Verify (before committing)

After all tasks complete:

1. Run the full engine test suite: `cd engines/<name> && python -m pytest tests/ -v --tb=short`
2. If this engine has upstream/downstream engines with tests, run boundary tests.
3. Run `/check-spec <engine>` to verify implementation matches SPEC.
4. Verify no `# TODO` or `# FIXME` without a linked SPEC section reference.
5. **Run the Three Challenges from CHALLENGE_PROTOCOL.md:**
   - Hostile Implementer: find ambiguities or shortcuts in the code
   - Skeptical Scholar: could any output mislead a scholar?
   - Technology Maximalist: am I using the best available tools?
6. **Knowledge integrity spot-check (KNOWLEDGE_INTEGRITY.md):**
   - Arabic text preserved byte-for-byte where required?
   - Attribution decisions consensus-based?
   - Errors fail loudly? Metadata passed through without loss?
7. Run `python3 scripts/verify_metadata_flow.py` if data models were touched.
8. Run `python3 scripts/check_compliance.py engines/<n>` for compliance overview.

### Phase 5: Handoff (commit and prepare next session)

1. `git add` changed files. Commit with a descriptive message.
2. Update the engine's `CLAUDE.md` §Current State with accurate file counts and what works.
3. Write `NEXT.md` for the next session (see NEXT.md protocol below).
4. Run `python3 scripts/orient.py --brief` to verify project state.
5. `git push`.

---

## NEXT.md Protocol (Implementation Phase)

NEXT.md drives every session. Write it as if the next session is a different person with no memory of this session.

```markdown
# NEXT SESSION

**Written by:** Session [date] ([brief description])
**Date:** [date]

## Immediate Task

[Specific: "Implement source engine §4.A.2 metadata extraction for HTML export format"
 Not vague: "Work on source engine"]

**Definition of done:**
1. [Testable criterion]
2. [Testable criterion]
3. Tests passing: [specific test names or patterns]

## Context

[Why this task. What was completed before. What decisions affect this task.]

## Files to Read — IN THIS ORDER

1. [Engine CLAUDE.md — always first]
2. [Engine SPEC.md — always second, with §section if partial read suffices]
3. [Any schemas, shared components, or other files needed]

**Do NOT read:** [Files that are NOT needed — prevent context waste]

## Implementation Notes

[Anything the next session needs to know that isn't in the SPEC:
 - Gotchas discovered during this session
 - Design choices made during implementation (not in SPEC)
 - Test data locations or setup requirements]

## Blocked Items

[Anything that can't proceed and why. API keys, test data, owner questions, etc.]

## What This Session Did

[2-3 sentences. Factual, not aspirational.]
```

---

## Task Decomposition Rules

When NEXT.md says "implement engine X," decompose into atomic tasks:

### Ordering principle: Input → Processing → Output → Tests

1. **Data models first.** Define the Python dataclasses/TypedDicts that represent the engine's input and output schemas (from SPEC §2 and §3).
2. **Core processing second.** Implement §4.A rules one subsection at a time.
3. **Error handling third.** Implement §7 error codes and recovery.
4. **Validation fourth.** Implement §5 self-validation checks.
5. **Integration last.** Wire up shared components (consensus, human gate, validation).

### Size principle: One session = one SPEC subsection

A single session should complete ONE §4.A subsection (e.g., §4.A.1 Source Identification, or §4.A.2 Metadata Extraction for one format). If a subsection is too large, split it — but each session must produce a testable, committable unit.

### Test principle: Tests are not optional

Every implementation task includes tests. Not "write tests later" — write them in the same session. Test structure mirrors SPEC structure:
- `test_4a1_source_identification.py` for §4.A.1
- `test_4a2_metadata_extraction.py` for §4.A.2 (format-agnostic)
- etc.

---

## Milestone Checkpoints

After completing a milestone (defined in MILESTONES.md):

1. Run ALL tests across all completed engines.
2. Run `/trace-pipeline` with test data to verify end-to-end flow.
3. Run the integrity-checker agent.
4. Run `python3 scripts/orient.py --brief` to verify project state.
5. Write a milestone summary in SESSION_LOG.md.

---

## Error Escalation

When Claude Code encounters a problem it cannot resolve:

| Problem | Action |
|---------|--------|
| SPEC is ambiguous | Implement conservatively, add `# SPEC-AMBIGUITY` comment, note in NEXT.md |
| SPEC seems wrong | Do NOT silently deviate. Note in NEXT.md under "SPEC Issues Found." Next architect session reviews. |
| Test data missing | Note in NEXT.md under "Blocked Items." Implement what can be tested without it. |
| API key missing | Note in NEXT.md under "Blocked Items." Mock the LLM calls for now. |
| Dependency broken | Fix if trivial. If not, note in NEXT.md and work on non-blocked tasks. |
| Context running low | Finish current task, write detailed NEXT.md, commit, push. Do NOT start new tasks. |

---

## Integration Testing Protocol

When two adjacent engines are both implemented:

1. Create an integration test in `tests/integration/test_{upstream}_{downstream}.py`.
2. The test feeds real (or realistic) data through the upstream engine, captures output, feeds it to the downstream engine.
3. Verify: all fields the downstream engine expects are present in the upstream output.
4. Verify: metadata accumulation — downstream output has ALL metadata from upstream, plus its own additions.
5. Verify: schema conformance at the boundary.

Integration tests live in the repo root `tests/integration/` directory, not inside individual engine directories.

---

## Shared Component Usage

Every engine uses shared components. Integration patterns:

### Consensus (shared/consensus)
```python
from shared.consensus.src.consensus import run_consensus
result = run_consensus(prompt, config)  # Returns ConsensusResult
```
Use for: any content decision where LLM judgment is involved (extraction, classification, placement).
Do NOT use for: deterministic operations (parsing, validation, ID generation).

### Human Gate (shared/human_gate)
```python
from shared.human_gate.src.human_gate import create_checkpoint
checkpoint = create_checkpoint(decision_type, context, options)
```
Use for: any irreversible library change, any low-confidence decision, any new source acquisition.

### Validation (shared/validation)
```python
from shared.validation.src.run_all_validations import validate_output
issues = validate_output(engine_name, output_data)
```
Use for: every engine output before it's written to the library.

If a shared component's API doesn't match what the SPEC expects, update the shared component — the SPEC is authoritative.
