# Questionnaire External Report Adjudication — 2026-04-02

Purpose:

- preserve the substantive output of owner-relayed browser research
- separate grounded improvements from stale-remote drift and generic/hallucinated claims
- record which local commits already implemented accepted findings

Scope:

- questionnaire packet
- owner-feedback guardrails
- post-questionnaire evaluation/synthesis flow

## Report 1 — ChatGPT Remote Packet Audit

Source mode:

- remote-only repo review
- explicitly stale relative to the current local packet

Reliability judgment:

- useful for pressure-testing
- not reliable on current file state

Accepted findings:

1. residual authority-shaped wording needed further cleanup
2. the packet needed a minimum viable high-signal subset for time-limited review
3. `F-8` was too architecture-shaped
4. `GN-2` needed framing that made it answerable for non-grammar users

Rejected or already-fixed findings:

1. `40` vs `~35` mismatch — already fixed locally before the report was reviewed
2. `CJ-2` / `CJ-3` blocked-state incoherence — already fixed locally
3. missing supplementals / guardrail docs — stale remote issue, not a current local issue

Implemented via:

- `751a649a` `fix(questionnaire): incorporate remote audit feedback`

## Report 2 — ChatGPT Evaluation Doctrine Review

Source mode:

- methodology / doctrine review
- not tightly bound to the exact local file state

Reliability judgment:

- high conceptual value
- required local grounding before implementation

Accepted findings:

1. stakeholder expectations are not validated requirements
2. scholarly invariants must outrank owner preference
3. owner confidence is metadata, not evidence
4. owner signal must become bounded rules, not absolute laws
5. separation of duties / anti-self-confirming-loop language needed to be explicit
6. the synthesis flow needed `LOCAL_PREFERENCE` and `DEEPER_NEED` categories

Implemented via:

- `033d512c` `docs(questionnaire): strengthen evaluation doctrine`

## Report 3 — Gemini Packet Audit

Source mode:

- uploaded local files
- partially grounded in the current packet

Reliability judgment:

- mixed
- contained some strong local observations but also generic or partially hallucinated framing

Accepted findings:

1. the packet needed explicit layer triage between:
   - excerpt boundary
   - display / presentation
   - workflow / study mode
2. readability or workflow complaints should not auto-translate into boundary edits

Rejected or heavily discounted findings:

1. generic claims about nonexistent local files
2. generic “not ready” framing that did not match the already-hardened local packet
3. broad survey-structure prescriptions that were not well grounded in the actual local files

Implemented via:

- `ea8967cf` `docs(questionnaire): add layer triage discipline`

## Report 4 — Adversarial Hardening Review

Source mode:

- remote-only repo review
- explicitly stale relative to current local state

Reliability judgment:

- useful as a final authority-drift pressure test
- mixed on exact current file state

Accepted findings:

1. a few owner-facing and evaluator-facing authority-drift phrases still remained locally
2. approval-shaped language still needed softening
3. the owner clarification path needed to be tightened so clarification could not overrule invariants

Rejected or already-fixed findings:

1. stale remote claims about wording that had already been fixed locally
2. generic concerns already addressed by the guardrail and synthesis changes

Implemented via:

- `58c77daa` `fix(questionnaire): remove residual authority drift`

## Resulting Local Hardening Sequence

The external reports materially contributed to this local change sequence:

- `8b148527` questionnaire packet hardening
- `df7f0fed` owner-feedback guardrail
- `94600137` post-review synthesis flow
- `ab4fe05f` response summary helper
- `d0a855d6` browser DR bundle builder
- `033d512c` doctrine strengthening
- `ea8967cf` layer triage discipline
- `58c77daa` final authority-drift cleanup

## Standing Rule For Future External Reports

1. Remote-only browser reports are never treated as current-local file review.
2. Uploaded-file browser reports are stronger, but still require local adjudication before patching.
3. No external report is implemented wholesale.
4. Every accepted point must be:
   - grounded in the local packet
   - logged
   - linked to a local commit or explicit rejection reason

## Current Verdict

The external reports were worth using, but only after strict adjudication.

The questionnaire lane is now substantially stronger because of them, not because
their claims were accepted wholesale, but because the grounded parts were
translated into bounded local improvements.
