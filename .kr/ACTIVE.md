> Purpose: Define the single current frontier and the exact deliverable expected from the next serious work session.
> Authority: The only authoritative next-session task file.
> Update when: The active frontier changes, the deliverable changes, or the success criteria change.
> Must not contain: Session diary, multiple parallel frontiers, broad backlog, durable project law.

# KR Active Frontier

Status: active

## Frontier
Implement analyzer v1 and the first review-packet exporter for the excerpting evaluation layer, using the completed evaluation brief and the historical run artifacts as the proving ground.

## Why this is the frontier now
The strategic question has been decided: KR should use an analyzer-first evaluation workflow for the upcoming 5-book excerpting campaign. The highest-leverage next move is no longer reasoning about whether to have such a layer, but building the bounded implementation that makes the layer real. The historical artifacts under `integration_tests/run_20260328/` already contain enough signal to validate whether the analyzer catches structural failures, silent failures, truncation, and review-worthy cases before the real campaign is run.

## Exact deliverable
Produce a bounded implementation result that includes:
1. analyzer v1 that ingests excerpting run directories and produces per-book metrics, accounting, anomaly flags, and book-level statuses;
2. campaign-level aggregation across the available historical 5-book run; and
3. a first review-packet exporter that emits bounded human-review packets from analyzer output rather than from ad hoc folder browsing.

The implementation is successful only if it proves itself on `integration_tests/run_20260328/`.

## Required inputs
- `reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md`
- `engines/excerpting/SPEC.md`
- `scripts/run_integration_test.py`
- `scripts/run_full_integration.py`
- `integration_tests/run_20260328/`
- relevant decision entries in `.kr/DECISIONS.md`

## Constraints and out of scope
- Do not reopen prompt-tuning or excerpt-boundary strategy unless the analyzer directly proves a structural need.
- Do not expand into taxonomy or synthesis evaluation.
- Do not build a dashboard or UI surface before analyzer accounting and review packets exist.
- Keep implementation bounded: analyzer first, exporter second, orchestration glue third.

## Completion criteria
This frontier is complete only when:
- analyzer v1 runs on `integration_tests/run_20260328/`;
- it explicitly catches the already observed `taysir` grouped-unit loss and `ibn_aqil_v3` silent-zero/truncation failure;
- it produces per-book and campaign summaries with clear statuses; and
- the review-packet exporter emits usable packets for bounded human inspection.

## Relevant decisions
- OPS-DEC-001
- OPS-DEC-002
- OPS-DEC-003
- OPS-DEC-004
- OPS-DEC-005

## If the session cannot complete the deliverable
Do not drift back into broad evaluation architecture discussion. Instead, isolate which implementation layer failed to land: ingestion/accounting, anomaly logic, campaign aggregation, or review-packet export. Leave behind a narrowed implementation brief for the next session.