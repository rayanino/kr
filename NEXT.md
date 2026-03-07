# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Normalization engine PRECISION session.** The normalization SPEC has completed its CREATIVE session — 10 §4.B capabilities now exist (7 from initial draft + 3 new: cross-page continuity intelligence, authorial voice fingerprint, scholarly discourse flow annotation). The SPEC is now 1419 lines. This session makes every rule machine-implementable.

## What to Read

1. `engines/normalization/SPEC.md` — The full SPEC. Focus on defect resolution.
2. Run `python3 scripts/check_spec_quality.py engines/normalization/SPEC.md` — Currently 4 HIGH defects (all MISSING_EXAMPLE in §4.A.3, §4.A.7, §4.B.2, §4.B.3). Resolve all HIGH defects to reach 0.
3. `reference/DOMAIN.md` §236-248 (Arabic as a Processing Language) — For Arabic text handling precision.
4. `engines/source/SPEC.md` §3 — Verify input contract alignment.

**Do NOT read:** VISION.md whole, kr_decisions.md, other engine SPECs beyond source §3. Keep context for precision work.

## Definition of Done

1. `check_spec_quality.py` shows 0 HIGH defects
2. All 4 missing examples added (§4.A.3, §4.A.7, §4.B.2, §4.B.3) with Arabic text worked examples
3. §4.A sections reviewed for machine-implementability — every rule yields a function signature + pseudocode mentally
4. Missing §4.A normalizer specifications noted: EPUB, Word doc, plain text, owner-authored normalizers need at least behavioral outlines (not full specs — they're [NOT YET IMPLEMENTED])
5. Cross-reference consistency: every field mentioned in §3 output contract appears in §4 processing and §5 validation
6. New error codes added for any new failure modes discovered during precision review
7. Self-audit performed per DEEP_REASONING_PROTOCOL: ≥3 structural/semantic defects found and fixed (cosmetic-only audits indicate superficial review)
8. `session_quality_gate.py` passes
9. NEXT.md written (for normalization engine HARDENING session)
10. SESSION_LOG.md updated
11. Committed and pushed

## Notes for Next Architect

- The 3 new §4.B capabilities (§4.B.8-10) have full worked examples but their interaction with existing capabilities needs cross-checking: §4.B.8 (continuity) feeds §4.B.10 (discourse flow) via cross-page argument cycle detection — verify the data flow is consistent.
- §4.B.9 (fingerprint) depends on §4.B.5 (census) for verse_ratio — verify the dependency is bidirectional-safe (census computes before fingerprint).
- The content unit schema in §3 now has 2 new fields (boundary_continuity, discourse_flow). Verify the Pydantic model in contracts.py will need updating during implementation.
- Pre-existing §4.A gaps: §4.A.3 (PDF text) and §4.A.4 (scanned PDF) have full specs but no examples. §4.A.7 (page boundaries) is thin. §4.B.2 (structural format auto-detection) and §4.B.3 (fine-grained fidelity mapping) lack examples.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
