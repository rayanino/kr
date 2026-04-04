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

This is not a normal feedback pass.
This is not a convenience refinement pass.
This is not a "make it a bit better" pass.

This is one of the few moments in the entire project where the team has direct, repeated, high-bandwidth access to the owner while the excerpting engine is still plastic enough to be hardened correctly.

Claude must therefore optimize for:
- maximum correctness
- maximum pressure-testing
- maximum rigor
- maximum blind-spot discovery
- maximum quality of doctrine before implementation
- maximum implementation quality after doctrine stabilizes

Claude must explicitly **not** optimize for:
- speed
- short chats
- quick closure
- lightweight synthesis
- "good enough for now"
- moving on before the atom is truly closed

Claude must treat this as:
- not “questionnaire cleanup”
- not “summarize what the owner said”
- not “apply the owner’s preferences literally”
- but rather:
  - the best chance the project will get to extract, pressure-test, and operationalize the owner’s actual standards before the hardening/build phase closes around them

The owner’s answers are **high-value signal** and **zero-authority directives**.
Claude must take over, widen the frame, identify blind spots, deploy coworkers, challenge owner-local reasoning where needed, and drive every aspect to a real engineering conclusion.

Claude must assume the owner is often answering correctly **inside the local frame of the shown examples** while still lacking visibility into:
- the rest of the repo
- adjacent engines
- contract consequences
- hidden edge cases
- future corpus diversity
- long-horizon architecture costs

That is not a flaw in the owner. It is the expected division of labor.
The burden is on Claude to correct for that narrowness through research, cross-checking, counterexample search, and explicit challenge.

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

The correct granularity is **one atom at a time**.

An atom is:
- one doctrine knot
- one edge-case family
- one structural rule
- one failure family
- one hidden dependency rule
- one tension that can be challenged and either closed or explicitly carried forward

If Claude is solving more than one real atom at once, the granularity is too coarse.

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

Claude must act as the **main orchestrator**.
That means:
- the owner provides signal and pressure
- Codex provides shadow audits, repo-state challenge, and contract/boundary pressure
- Gemini provides deep research, adversarial reframing, and external-style blind-spot challenge
- Claude owns the synthesis, the decisions, the pacing, the implementation calls, and the closure standard

No major aspect should move from theory to implementation without fresh challenge from outside Claude’s own immediate reasoning.

Claude must also explicitly investigate whether its own **agent teams** feature can materially improve this lane.

That investigation is mandatory, not optional.
Claude must decide early:
- whether agent teams genuinely increase quality here
- which roles they should serve
- which roles they must **not** replace

Agent teams may be used to strengthen the lane only if they improve:
- research breadth
- adversarial pressure
- implementation review depth
- regression/risk surfacing

Agent teams must **not** become a lazy substitute for:
- owner interrogation
- Codex shadow challenge
- Gemini deep research
- explicit closure discipline

If Claude decides not to use agent teams, it must record:
- why they are not beneficial here
- what risk is not reduced by them

If Claude decides to use them, it must record:
- exact role split
- how they map onto the per-atom workflow
- how their outputs are reviewed before closure

## Unit Of Work

Do **not** process one whole questionnaire answer per prompt.

The unit of work is:
- one aspect atom
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

Claude must literally open each atom with wording of this shape:

- `The next atom we are handling is: ...`
- `This atom is not finished until theory, challenge, implementation, review, hardening, and tests are all closed.`

This must become the rhythm of the session, not an occasional pattern.

## Hard Redlines

The following count as **failed execution**, not merely weak execution:

1. Claude skips the raw owner-source artifacts and reasons only from cleaned summaries.
2. Claude treats one local owner answer as global truth without counterexample search.
3. Claude closes an atom without explicit coworker challenge or an explicit blocker log explaining why that challenge could not happen.
4. Claude builds before the theory for that atom has been pressure-tested.
5. Claude says an atom is finalized while implementation, validation, or residual-risk accounting is still vague.
6. Claude processes multiple atoms together because they feel “related.”
7. Claude leaves the owner believing an issue is settled when the repo, tests, or edge-case surface have not actually proven that.

If any of those happen, the lane is drifting into mediocre execution and must be corrected immediately.

## Mandatory Research Minimum Per Atom

For every atom, Claude must complete a real research floor before theory closure:

1. Search the repo for all directly relevant prior artifacts, specs, tests, prompts, and collection files.
2. Search for counterexamples that pressure the owner’s local formulation.
3. Search for adjacent engine or contract consequences.
4. Identify at least one corpus-diversity or methodology-diversity risk.
5. Produce an explicit list of what the current evidence still does **not** prove.

If that floor is not met, the atom is not ready for doctrine synthesis.

## Mandatory Coworker Minimum Per Atom

At every major atom, Claude must deliberately involve coworkers.

Default expectation:
- **Codex**: read-only shadow challenge on repo consequences, contracts, validation surface, and regression risk
- **Gemini**: deep-research or external-blind-spot challenge on missing patterns, unseen methodologies, or alternative framings
- **Claude agent teams**: optional internal force multiplier only after explicit evaluation and only when they materially improve per-atom rigor

At minimum, before finalizing any major atom, Claude must have:
- one non-Claude challenge on the theory shape
- one non-Claude challenge on the implementation/risk shape

If a coworker cannot be used, Claude must log:
- who was unavailable
- why
- what risk remains because that challenge did not occur

No silent skipping.

If Claude agent teams are available, Claude must evaluate them near the beginning of the lane and either:
- integrate them deliberately into the per-atom workflow
- or explicitly reject them with reasons

## Required Loop Per Aspect

For each aspect, Claude must execute this full loop:

1. **Select exactly one atom**
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
6. **Run the research minimum**
7. **Deploy coworkers deliberately**
   - deep research where needed
   - fresh pair of eyes where needed
   - contradiction finding
   - scholarly-risk checking
   - implementation-risk checking
   - agent teams if and only if they materially strengthen this specific atom
8. **Pressure-test the theory**
   - strongest case for
   - strongest case against
   - hidden tradeoffs
   - edge cases
   - failure modes
9. **Check cross-atom regression risk**
   - does this atom collide with anything previously finalized?
   - if yes, reopen the earlier atom explicitly rather than hand-waving the conflict away
10. **Classify the impact**
   - owner-model only
   - workflow/display only
   - prompt behavior
   - SPEC doctrine
   - validation rules
   - tests
   - cross-engine contract
11. **Implement bounded changes where warranted**
12. **Review the build**
13. **Harden the build**
14. **Run the mapped tests**
15. **Record the result**
16. **Only then mark the atom finalized**

## Aspect Finalization Standard

Claude must not say “this atom is finalized” unless all of the following are true:

- the owner signal was reconstructed from raw evidence
- counterarguments were surfaced
- owner-local blind spots were corrected for
- the research minimum was completed
- coworkers were used or their absence was explicitly logged
- implementation consequences were decided
- the relevant patch/spec/prompt/test changes were made, or the atom was explicitly classified as non-implementation and that classification was defended
- review was performed
- hardening was performed
- tests passed or a blocker was explicitly logged
- remaining uncertainty is either closed or explicitly carried forward
- cross-atom regression risk was checked
- residual risks were written down explicitly
- the closure statement is strong enough that another engineer could not reasonably ask “what decision is still missing?”

Anything less than that is not “finalized.”

There is no “soft finalized.”
There is no “good enough finalized.”
There is no “we’ll remember to come back later” finalized.

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
- reduce the owner’s week of live input into lightweight synthesis sludge
- let a coworker be consulted only occasionally when the atom is high-stakes
- quietly defer difficult engineering consequences without tagging them as real unresolved risk

## Branch / Workspace Rule

Do **not** run this hardening program on the taxonomy review branch.

Before any implementation work begins, Claude should move the actual hardening lane to a clean excerpting-focused branch, for example:
- `excerpting-foundations-hardening-20260404`

The current questionnaire preservation artifacts are evidence inputs, not the build lane itself.

## Immediate Start Rule

Claude must not start with a broad overview speech.
Claude must not start with “here is my synthesis of everything.”

Claude must start with:
1. confirming `F6` preservation state
2. confirming foundations are `8 / 8`
3. opening the first atom explicitly
4. saying why that atom is first
5. beginning the questioning / research cycle immediately

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
- atom name
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
The main objective is not elegance of summary.
The main objective is not lightness of process.

The main objective is to be able to say, atom by atom:

**This has been challenged, researched, built, reviewed, hardened, tested, and finalized.**
