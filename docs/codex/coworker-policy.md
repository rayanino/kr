# Codex Coworker Policy

Date: 2026-04-01

This file governs Codex coworker usage for the April 9, 2026 to July 1, 2026 doctrine period.

## Peer Major Coworkers

Treat these as peer major coworkers:

- `Claude Code`
- `Gemini CLI (Pro 3.1)`

Neither is opportunistic or optional by default for major review.

## Working Rule

At every major milestone, request both:

- Claude review
- Gemini review

Major milestone means:

- doctrine or control-plane policy changes
- runtime-state or cutover decisions
- backend-proof interpretation
- hook or enforcement changes
- any `HIGH` or `CRITICAL` finding
- owner-facing packet decisions

If one is unavailable because of quota, capacity, auth, or tool failure:

- record that explicitly
- do not silently downgrade its role
- continue only under the degraded-mode rules in the canonical doctrine

## Backup Channels

These are useful adjudication or backup channels, not the primary repo-native coworker pair:

- ChatGPT deep research
- Claude Chat deep research
- Gemini Chat

These channels require owner relay or interactive follow-up, which is incompatible with unattended routine operation.

## Current Interpretation

- Codex is the control-plane orchestrator
- Claude Code and Gemini CLI are peer review coworkers
- disagreement between them is a signal, not noise to smooth over
