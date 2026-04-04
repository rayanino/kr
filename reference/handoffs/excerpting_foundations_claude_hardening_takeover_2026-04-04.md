# Excerpting Foundations Hardening Takeover — 2026-04-04

Status: PRE-STAGED takeover brief for a fresh Claude Code / Claude Chat control-tower session that starts **after `F-6` is preserved**.

This note is the authoritative handoff for the **post-F6 foundations hardening lane**.

It does not replace:
- `.kr/ACTIVE.md`
- `.kr/HANDOFF.md`
- `engines/excerpting/CLAUDE.md`
- `engines/excerpting/reference/excerpt_definition_canon/`
- `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`
- `integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md`

It does supersede:
- any chat-memory-only summary of what the owner meant by `F1`–`F8`
- any assumption that foundations work should be digested in one giant synthesis pass
- any assumption that owner answers should be translated directly into implementation

## Session Type

- Session type: new Claude control-tower session for **excerpting foundations hardening**
- Authority expectation: Claude is the active engineering authority; Codex is in shadow/setup only
- Lane type: bounded side-lane that turns `F1`–`F8` into challenge-tested doctrine, implementation decisions, tests, and hardened behavior
- Duration expectation: **multi-day**, high-intensity, owner-in-the-loop hardening program

## Governing Reality

The owner took a week of concentrated work to sit in the loop full-time instead of letting agents run autonomously.

This is the highest-value owner-input window in the excerpting project.

Claude must treat this as:
- not “questionnaire cleanup”
- not “summarize what the owner said”
- not “apply the owner’s preferences literally”
- but rather:
  - the best chance the project will get to extract, pressure-test, and operationalize the owner’s actual standards before the hardening/build phase closes around them

The owner’s answers are **high-value signal** and **zero-authority directives**.
Claude must take over, widen the frame, identify blind spots, deploy coworkers, challenge owner-local reasoning where needed, and drive every aspect to a real engineering conclusion.

## Read Order For Claude

Read in this order:
1. `ACTIVE_AUTHORITY.md`
2. `CLAUDE.md`
3. `docs/codex/operating-model.md`
4. `.kr/ACTIVE.md`
5. `.kr/HANDOFF.md`
6. `engines/excerpting/CLAUDE.md`
7. `engines/excerpting/reference/excerpt_definition_canon/README.md`
8. `engines/excerpting/reference/excerpt_definition_canon/01_dossier.md`
9. `integration_tests/questionnaire/OWNER_FEEDBACK_GUARDRAIL.md`
10. `integration_tests/questionnaire/TEAM_TRANSLATION_GUIDE.md`
11. `integration_tests/questionnaire/CRITICAL_EVALUATION_GUIDE.md`
12. `integration_tests/questionnaire/evaluation_reports/OWNER_RESPONSE_SUMMARY.md`
13. `integration_tests/questionnaire/evaluation_reports/QUESTIONNAIRE_AUDIT.md`
14. `integration_tests/questionnaire/external_questionnaire_responses.json`

## Exact Scope

This hardening lane is **foundations-only**.

Treat these as the current foundations evidence set:
- `F-1`
- `F-2`
- `F-3`
- `F-4`
- `F-5`
- `F-7`
- `F-8`

`F-6` is the final pending foundations item and must be preserved in the same external-response structure before substantive synthesis begins.

This lane must not yet digest:
- `G-*`
- `SC-*`
- `D-*`
- `E-*`
- `K-*`
- `GN-*`
- `L-*`
- `QA-*`
- `CJ-*`
- `S-*`

The owner wants the foundations lane to be handled **aspect by aspect**, not item by item and not all at once.

## Mandatory Evidence Corpus

### F1
- `engines/excerpting/reference/excerpt_definition_canon/`
- `engines/excerpting/chatgpt_f1_collection/manifest.yaml`
- `engines/excerpting/chatgpt_f1_collection/source_artifacts/f1_owner_original_notes_2026_04_03.txt`

### F2
- `engines/excerpting/chatgpt_f2_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f2_collection/01_owner_answer.md`
- `engines/excerpting/chatgpt_f2_collection/02_workflow_notes.yaml`
- `engines/excerpting/chatgpt_f2_collection/source_artifacts/f2_owner_raw_draft_and_followups_2026_04_03.txt`

### F3
- `engines/excerpting/chatgpt_f3_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f3_collection/02_case_dossier.md`
- `engines/excerpting/chatgpt_f3_collection/source_artifacts/f3_full_user_input_2026_04_04.txt`
- `engines/excerpting/chatgpt_f3_collection/source_artifacts/f3_owner_raw_reaction_2026_04_04.txt`

### F4
- `engines/excerpting/chatgpt_f4_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f4_collection/02_case_dossier.md`
- `engines/excerpting/chatgpt_f4_collection/source_artifacts/f4_full_user_input_2026_04_04.txt`
- `engines/excerpting/chatgpt_f4_collection/source_artifacts/f4_owner_raw_reaction_2026_04_04.txt`

### F5
- `engines/excerpting/chatgpt_f5_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f5_collection/02_case_dossier.md`
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_full_user_input_2026_04_04.txt`
- `engines/excerpting/chatgpt_f5_collection/source_artifacts/f5_owner_raw_reaction_2026_04_04.txt`

### F7
- `engines/excerpting/chatgpt_f7_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f7_collection/02_failure_dossier.md`
- `engines/excerpting/chatgpt_f7_collection/source_artifacts/f7_owner_raw_draft_2026_04_04.txt`

### F8
- `engines/excerpting/chatgpt_f8_collection/00_manifest.yaml`
- `engines/excerpting/chatgpt_f8_collection/02_assessment_dossier.md`
- `engines/excerpting/chatgpt_f8_collection/source_artifacts/f8_owner_raw_draft_2026_04_04.txt`

## Core Operating Doctrine For This Lane

Claude must treat every foundation item as:
- raw owner signal
- local example-bound judgment
- partial view of a much larger engine/system

Therefore Claude must never assume:
- the owner’s local reaction sees the whole architecture
- the owner’s preferred split or rule is globally safe
- the owner’s answer is sufficient without challenge
- an aspect is finished because it was phrased elegantly

Instead Claude must:
- reconstruct the real problem behind each answer
- identify the narrowness of the owner’s local evidence window
- use broader repo knowledge and research to widen the frame
- actively search for hidden costs, blind spots, and counterexamples
- decide whether the owner is reacting to:
  - boundary
  - display
  - workflow
  - proof integrity
  - taxonomy pressure
  - quote-layer ambiguity
  - evaluation blind spot
  - or something deeper behind the literal complaint

## Unit Of Work

Do **not** process one whole questionnaire answer per prompt.

The unit of work is:
- one aspect
- one doctrine knot
- one failure family
- one structural rule
- one contradiction
- one red-team concern

Examples:
- explained + explanation should stay together
- rule/proof split without losing scholar linkage
- note-compensation vs source-preserving context
- quote-layer function preservation
- taxonomy must not bias excerpting
- overgranulation vs undergranulation
- linking-word preservation
- disagreement mention vs tarjih separation
- unseen scholar methodologies and uncertainty gates
- authoritative fetched proof vs book-preserved proof
- global trust poisoning from one local error

## Required Loop Per Aspect

For each aspect, Claude must execute this full loop:

1. **Select exactly one aspect**
2. **Gather the owner evidence**
   - raw artifact first
   - cleaned owner-answer layer second
   - machine-friendly collection files third
3. **Reconstruct the owner’s real concern**
4. **Identify local-narrowness risk**
   - what is the owner reacting to only because of the examples shown?
   - what system-wide implications is the owner not in position to see directly?
5. **Interrogate the owner deeply**
   - ask many narrow, concrete, non-technical questions if needed
   - use examples
   - do not ask him to solve architecture
6. **Deploy coworkers deliberately**
   - deep research where needed
   - fresh pair of eyes where needed
   - contradiction finding
   - scholarly-risk checking
   - implementation-risk checking
7. **Pressure-test the theory**
   - strongest case for
   - strongest case against
   - hidden tradeoffs
   - edge cases
   - failure modes
8. **Classify the impact**
   - owner-model only
   - workflow/display only
   - prompt behavior
   - SPEC doctrine
   - validation rules
   - tests
   - cross-engine contract
9. **Implement bounded changes where warranted**
10. **Review the build**
11. **Harden the build**
12. **Run the mapped tests**
13. **Record the result**
14. **Only then mark the aspect finalized**

## Aspect Finalization Standard

Claude must not say “this aspect is finalized” unless all of the following are true:

- the owner signal was reconstructed from raw evidence
- counterarguments were surfaced
- owner-local blind spots were corrected for
- coworkers were used where useful
- implementation consequences were decided
- the relevant patch/spec/prompt/test changes were made or explicitly deferred
- review was performed
- hardening was performed
- tests passed or a blocker was explicitly logged
- remaining uncertainty is either closed or explicitly carried forward

Anything less than that is not “finalized.”

## Explicit Anti-Failure Rules

Claude must not:
- collapse `F1`–`F8` into one giant summary
- treat owner answers as direct implementation commands
- process too many aspects at once
- jump into coding before the aspect theory is pressure-tested
- hide a boundary problem behind a display fix
- hide a display problem behind a boundary rewrite
- assume rules/protocols are sufficient to cover all future scholar methodologies
- assume known edge cases are exhaustive
- assume excerpting is safe once it looks clean
- mark a tension closed just because it has a nice wording

## Branch / Workspace Rule

Do **not** run this hardening program on the taxonomy review branch.

Before any implementation work begins, Claude should move the actual hardening lane to a clean excerpting-focused branch, for example:
- `excerpting-foundations-hardening-20260404`

The current questionnaire preservation artifacts are evidence inputs, not the build lane itself.

## Current Preconditions

As of now:
- `F1`, `F2`, `F3`, `F4`, `F5`, `F7`, and `F8` are preserved and registered as external questionnaire answers
- `F6` is still pending and must be ingested before this hardening loop starts for real
- current questionnaire summary shows foundations as `7 / 8` answered

The first operational step for Claude is therefore:
1. verify that `F6` has been preserved in the same structure
2. confirm foundations are `8 / 8`
3. only then start the multi-day aspect-hardening loop

## Deliverable Claude Must Produce

Claude should create and maintain a living foundations-hardening ledger that tracks, for each aspect:
- aspect name
- evidence files used
- owner tensions
- coworker findings
- adopted doctrine
- implementation consequence
- tests added or run
- unresolved risks
- final disposition

This ledger should become the backbone of the multi-day session.

The main objective is not speed.
The main objective is to be able to say, aspect by aspect:

**This has been challenged, researched, built, reviewed, hardened, tested, and finalized.**
