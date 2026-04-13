> Purpose: Record the exact excerpting state at the moment engine builds were paused so later sessions can resume without re-deriving context.
> Authority: Resume aid for the paused excerpting lane. Does not override `.kr/ACTIVE.md`.

# Excerpting Pause Checkpoint — 2026-04-08

## Reason for pause
Pause engine builds and excerpting implementation work while separate sessions focus on repo cleanup and owner-facing visual representations.

## Frozen state
- Branch: `excerpting-foundations-hardening-20260404`
- Test state: `1008` pass, `0` fail, `4` xfail
- Budget state: `EUR 36.70 / 100.00`
- Review artifact under active owner review: `integration_tests/review_session22/eval_session22_talaq/`
- Feedback path: `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`

## What had just completed before the pause
- Session 22 smoke output existed at `integration_tests/eval_session22_talaq/`
- Review UI was live for Session 22 output
- Owner had started reviewing the talaq excerpts in the UI

## Feedback analysis completed before pause
### First verdict analyzed
- Feedback entry: excerpt `exc_src_test0001_div_src_test0001_1_002_pre_0_0`
- Verdict: `needs_work`
- Pattern: the pipeline already split `تعريف الطلاق لغة` from `تعريف الطلاق شرعا`, but still fused the lexical definition with the derivational/etymological sentence (`مشتق من الإطلاق...`)
- Phase-level diagnosis:
  - proximate cause: Phase 2a classification granularity
  - current classifier rule still allows consecutive same-function sentences to remain one segment
  - the resulting grouped unit then flowed unchanged through Phase 2b and Phase 3
- Deeper constraint:
  - the current `TeachingUnit` model assumes a non-overlapping partition of segment spans
  - the owner's stronger suggestion, allowing two excerpt records over the same short span, would require a spec/contract change rather than a prompt-only fix

## Deferred excerpting work
- Continue reading and analyzing new owner feedback entries one by one
- For each `needs_work` or `reject`, trace the issue to the responsible pipeline phase and accumulate a fix brief
- Only after the pause ends, decide whether to:
  - add a Phase 2a lexical-definition vs derivation split rule
  - or change the excerpt model to permit overlapping short-span excerpts

## Preselected generalization candidates
- `div_src_test0001_7_006` — hadith-heavy plus another `لغة/شرعا` definition surface
- `div_src_test0001_4_000` — explicit cross-madhab dispute structure
- `div_src_test0001_6_076` — different kitab/domain with definition plus multi-type evidence

## Resume protocol
1. Read `.kr/ACTIVE.md` and confirm the frontier has returned to excerpting.
2. Read any new entries in `integration_tests/review_session22/eval_session22_talaq/owner_feedback.jsonl`.
3. Consolidate the full pause-period feedback into a single implementation brief before editing excerpting code.
4. Resume on the frozen branch or a fresh excerpting-focused branch, not on a cleanup/docs branch.
