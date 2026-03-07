# NEXT SESSION

## Session Type
CREATIVE (see SESSION_TYPES.md for full framework)

## Immediate Task

**Passaging engine CREATIVE session.** The passaging engine has contracts defined but no SPEC. This session designs the passaging engine from scratch — what it does, how it creates passage boundaries, and what transformative capabilities make it more than a text splitter.

## What to Read

1. `engines/passaging/contracts.py` — The existing Pydantic models define the output schema.
2. `reference/DOMAIN.md` §242-277 — Arabic text properties and book structures that affect passage design.
3. `engines/normalization/SPEC.md` §3 (output contract) — What the passaging engine receives as input.
4. `reference/ENTRY_EXAMPLE.md` — What the final knowledge product looks like. Work backward: what passage quality does the synthesizer need?
5. `reference/USER_SCENARIOS.md` — Which user scenarios the passaging engine serves.
6. `DEEP_REASONING_PROTOCOL.md` — SPEC template and perfection standard.

**Do NOT read:** VISION.md whole (use extract_vision_sections.py for §8 passaging section if needed), kr_decisions.md, other engine SPECs beyond normalization §3.

## Definition of Done

1. Complete SPEC draft for the passaging engine following the SPEC template (§1-§10)
2. §4.A rules precise enough for Claude Code to implement
3. §4.B with ≥2 architect-originated transformative capabilities (not from VISION.md)
4. Concrete examples for every non-trivial rule
5. `check_spec_quality.py` shows 0 HIGH defects
6. `creative_verification.py` shows ≥2 invention signals
7. Self-audit performed per DEEP_REASONING_PROTOCOL: ≥3 defects found and fixed
8. `session_quality_gate.py` passes
9. NEXT.md written (for passaging PRECISION session)
10. SESSION_LOG.md updated
11. Committed and pushed

## Notes for Next Architect

- The normalization engine's output contract is rich: `boundary_continuity` (§4.B.8), `discourse_flow` (§4.B.10), `content_census` (§4.B.5), `structural_format` (§4.B.2), and the division tree all provide signals for intelligent passage boundaries. Use them.
- The key insight from DOMAIN.md: passage size should be calibrated by SEMANTIC density, not word count. Arabic is morphologically dense.
- The content census's `verse_ratio` field triggers verse-aware boundary detection. `structural_format` (qa_format, tabular_khilaf, dictionary, verse) each demand format-specific passage strategies.
- The normalization SPEC's §4.B.10 discourse flow annotation identifies argument cycles. The passaging engine's most transformative capability would be: NEVER split a complete argument cycle across passages, and NEVER create a passage that starts mid-argument unless the argument cycle spans >N pages (configurable).
- The passaging engine is the last engine before excerpting — passage quality determines excerpt quality.
- Hardening tightened the normalization contracts: `DiscourseFlow` now has validators (cycle_complete implies no missing, segments non-overlapping), `LayerFingerprint` enforces insufficient_data threshold, `DiscourseSegment.detection_method` is now an enum. The passaging engine contracts should be similarly rigorous.

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
