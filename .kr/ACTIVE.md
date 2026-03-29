> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

# KR Active Frontier

Status: active

## Frontier
Design the evaluation layer around the upcoming 5-book excerpting campaign so that the run produces decision-grade evidence instead of an impressionistic pile of artifacts.

## Why this is the frontier now
Excerpting has reached the point where more speculative tuning is lower leverage than sharper measurement. The repo already produces rich run artifacts, and the next major execution step is a full-book campaign. Without a disciplined evaluation layer, that campaign will generate outputs but not enough structured insight about coverage, yield quality, redundancy, failure patterns, and next architectural moves. The highest-value near-term work is therefore to specify how a completed run will be measured, surfaced, and reviewed.

## Exact deliverable
Produce a design-grade evaluation brief centered on an analyzer-first workflow. The brief should define:
1. the run analyzer’s required metrics, flags, and per-book / cross-book outputs;
2. the review-packet exporter’s required samples and anomaly buckets for human inspection; and
3. the formal full-book testing protocol that interprets those outputs.

The output should be tight enough that a later implementation session can hand bounded coding tasks to Codex or Claude Code without re-deciding the architecture.

## Required inputs
- `engines/excerpting/SPEC.md`
- `scripts/run_integration_test.py`
- `scripts/run_full_integration.py`
- the most recent excerpting integration artifacts already present under `integration_tests/`
- relevant decision entries in `.kr/DECISIONS.md`

## Constraints and out of scope
- Do not spend this session on prompt micro-tuning or engine feature additions.
- Do not broaden into taxonomy or synthesis design.
- Do not treat raw specialist output as project law without primary-session synthesis.
- Keep one live frontier only; other plausible improvements may be mentioned briefly as deferred, not made co-equal.

## Completion criteria
This frontier is complete only when there is a single coherent evaluation brief that:
- defines the analyzer inputs, outputs, and metrics clearly;
- defines the review-packet exporter’s sampling and anomaly logic clearly;
- defines pass / concern / fail style interpretation for the upcoming full-book campaign; and
- leaves no ambiguity about which parts are next suited for bounded implementation versus further reasoning.

## Relevant decisions
- OPS-DEC-001
- OPS-DEC-002
- OPS-DEC-003
- OPS-DEC-004

## If the session cannot complete the deliverable
Do not drift into general brainstorming. Instead, isolate the blocker precisely, record which part of the evaluation layer remains unresolved, and leave behind a narrowed follow-up brief that makes the next serious session cheaper and sharper.
