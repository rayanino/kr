> Purpose: Leave the next serious session with enough state to resume work without re-deriving the project situation.
> Authority: Context and resume aid. It can summarize and point, but it cannot override `ACTIVE.md`.
> Update when: A session materially advances work, changes the recommended resume point, or discovers a meaningful new risk.
> Must not contain: Duplicate durable law from `CHARTER.md`, multiple conflicting next steps, or broad backlog lists.

# KR Handoff

## Session purpose
Interpret the active frontier exactly and decide whether the next highest-leverage move before the 5-book excerpting campaign is deeper reasoning, deep research, or bounded implementation design.

## What this session completed
Completed the active frontier by writing `reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md`.

That brief locks in:
- an analyzer-first evaluation workflow;
- the analyzer's required inputs, lineage/accounting model, metrics, flags, and per-book/campaign outputs;
- the review-packet exporter's required anomaly buckets and card structure; and
- the formal full-book testing protocol that turns those outputs into `PASS` / `CONCERN` / `FAIL` interpretation.

## Key findings from the historical run
The current historical artifacts already show why the evaluation layer cannot be postponed:

1. `taysir` has a real accounting failure:
   - Phase 2b grouping produced 11 teaching units;
   - final `excerpts.jsonl` contains 9 excerpts; and
   - the run logged two `EX-V-002` errors.
   The analyzer must therefore reconcile grouped units against final excerpts and treat grouped-unit loss as a first-class failure.

2. `ibn_aqil_v3` has a silent failure signature:
   - long Phase 2a runtime;
   - zero final excerpts;
   - zero logged errors in `processing_log.jsonl` and `run_metadata.json`.
   The analyzer must therefore detect impossible or contradictory success states rather than trusting run logs blindly.

3. `ibn_aqil_v3/raw_llm_responses/enrich_0001.json` ends with `finish_reason = length` and contains classification-shaped content despite the `enrich_` filename.
   The analyzer must therefore inspect call structure and finish reasons rather than infer semantic phase from filenames alone.

## Decisions made this session
- The evaluation architecture is now analyzer-first rather than artifact-browser-first.
- This is durable enough to record as `OPS-DEC-005`.
- The strategic question is no longer whether KR needs an evaluation layer before the 5-book campaign. It does.
- The next question is implementation: build analyzer v1 and the first review-packet exporter, then prove them on `integration_tests/run_20260328/`.

## What did *not* happen
- No deep research was needed.
- No Codex or Claude Code implementation was needed for the design brief itself.
- No prompt tuning or engine redesign was reopened.
- No dashboard/UI work was started.

## Current resume point
Resume from `ACTIVE.md`.

The correct next session should be a bounded implementation session that:
1. builds analyzer ingestion and lineage/accounting;
2. builds per-book metrics and anomaly flags;
3. builds campaign aggregation;
4. builds the first review-packet exporter; and
5. proves the implementation on `integration_tests/run_20260328/`.

## Recommended first checks in the next session
- Use `reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md` as the implementation contract.
- Treat `taysir` grouped-unit loss and `ibn_aqil_v3` silent-zero/truncation as mandatory regression checks.
- Keep the implementation tightly scoped to evaluation infrastructure; do not drift into prompt changes or new excerpting features unless the analyzer itself proves a structural need.

## Known caution
Root-level or non-`.kr/` documents may still exist that look operational. Do not let them become shadow control surfaces. `ACTIVE.md` remains the only authoritative next-session task file.
