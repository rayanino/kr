# NEXT SESSION

## Session Type
PRECISION (see SESSION_TYPES.md for full framework)

## Immediate Task

**Atomization engine PRECISION session.** The atomization SPEC now has 5 §4.B capabilities (3 from previous draft, 2 added this session: §4.B.4 Scholarly Attribution Chain Resolution, §4.B.5 Atom-Level Semantic Fingerprinting). The contracts.py is created. This session: audit the SPEC for machine-readability, fix defects, ensure every §4.A rule is implementable by Claude Code with zero clarifying questions, and run check_spec_quality.py.

## What to Read

1. `engines/atomization/SPEC.md` — the full SPEC to audit. **Read this entire document.**
2. `engines/atomization/contracts.py` — verify contracts match §3 exactly.
3. `engines/passaging/SPEC.md` §3 — verify input contract consistency.
4. `engines/passaging/contracts.py` — verify atomization input types import correctly.
5. `reference/DOMAIN.md` §"What Failure Looks Like" → atomization failure section — ensure every failure mode listed there is covered in the SPEC.

**Do NOT read:** VISION.md, kr_decisions.md, source/normalization SPECs (except by reference from passaging contracts).

## The PRECISION Work

### Audit Checklist
1. Every sentence in §4.A: is it a binding rule or a marked open question? Flag filler.
2. Every §4.A rule: can Claude Code write a function for it without asking questions? If not, add specificity.
3. §3 output contract vs. contracts.py: are they byte-for-byte consistent? Fix any drift.
4. §7 error handling: are the 2 new capabilities (§4.B.4, §4.B.5) covered? Add error codes if missing.
5. §10 test requirements: add test cases for attribution detection and fingerprinting.
6. The scholarly function type taxonomy (§4.A.3): are all 16 types adequately distinguished? Can the LLM tell them apart with the definitions given?
7. The attribution pattern markers (§4.B.4): is the Arabic marker list exhaustive for common patterns? Cross-check with DOMAIN.md.
8. Cross-reference: does every field in §3 appear in contracts.py? Does every field in contracts.py appear in §3?

### Run Quality Scripts
- `python3 scripts/check_spec_quality.py engines/atomization/SPEC.md`
- Fix every defect found.

## Definition of Done

1. All defects found by check_spec_quality.py fixed
2. §3 and contracts.py are perfectly synchronized
3. Error codes added for §4.B.4 and §4.B.5 failure modes
4. Test cases added for attribution detection and fingerprinting
5. Self-audit completed (minimum 4 structural/semantic defects found and fixed)
6. NEXT.md written (for atomization HARDENING session)
7. SESSION_LOG.md updated
8. Committed and pushed

## What the Previous Sessions Did

Source engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Normalization engine: CREATIVE → PRECISION → HARDENING → IMPL_PREP (complete).
Passaging engine: CREATIVE → PRECISION → HARDENING (complete).
Atomization engine: **CREATIVE (this session)**: 2 new §4.B capabilities (§4.B.4 Scholarly Attribution Chain Resolution, §4.B.5 Atom-Level Semantic Fingerprinting), contracts.py created, RESOURCES.md updated with Arabic NLP research findings (IslamicLegalBench 2026, hadith segmentation accuracy).

## Pending Owner Questions

- **API keys:** Will be needed when Claude Code starts implementation. Not blocking.
