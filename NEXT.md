# NEXT — Write Session 2 handoff (Architect session)

## Current position: Normalization engine Build Session 1 COMPLETE (commit e2d6043). Contracts aligned (MF-1, MF-2), 31 error codes, 40 tests passing. Architect reviewed and ACCEPTED.
## What to do: Write Build Session 2 NEXT.md for Claude Code — Shamela normalizer Passes 1–3 (HTML parsing → footnote separation → text cleaning).
## Context: Session 2 is the most complex build session. It implements the core text extraction pipeline that every other session builds on. The ABD reference code (1,123 lines) provides behavioral insight but must be rebuilt to match SPEC.md. Careful handoff is critical.
## Owner action needed: YES after — to give the Session 2 handoff to CC.

---

## Read First (in this order)

1. `engines/normalization/CLAUDE.md` (104L) — Engine orientation, module map, build session plan.
2. `engines/normalization/SPEC.md` §4.A.2 (lines 183–280) — Shamela normalizer specification, all 6 passes. Focus on Passes 1–3 for this session.
3. `engines/normalization/SPEC.md` §4.A.8 (lines 655–663) — Diacritics and Arabic text handling rules. Critical for Pass 3.
4. `reference/archive/abd_code/normalization/normalize_shamela.py` (1,123L) — ABD-era Shamela normalizer. REFERENCE ONLY — build fresh code matching SPEC.md.
5. `engines/normalization/reference/SHAMELA_HTML_REFERENCE.md` — Shamela HTML format documentation.
6. `engines/normalization/reference/structural_patterns.yaml` (340L) — The quote-style differentiator (line 12) is critical for Pass 1: single-quote `class='title'` = metadata page, double-quote `class="title"` = content heading.
7. `engines/normalization/contracts.py` (now ~720L) — Updated Pydantic models from Session 1. Session 2 code must produce data matching these schemas.
8. `engines/normalization/src/normalizers/shamela.py` (80L) — Existing stub. Session 2 fills in Passes 1–3.
9. `engines/normalization/src/errors.py` (130L) — Error codes available for Session 2 to raise.
10. `tests/fixtures/shamela_real/` — 11 real Shamela book fixtures for testing.
11. `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` — Multi-layer commentary fixture.
12. `reference/SPEC_ADVERSARY_NORMALIZATION.md` — Adversarial test cases. ADV-001 through ADV-010 target Passes 1–3.

## Pre-Session Fix

Before writing the Session 2 handoff, update `engines/normalization/SPEC.md` §9.1 (lines 2041–2042): mark M-13 and M-14 as RESOLVED with commit reference e2d6043. They currently still say "Rename..." and "[OPEN]" — this is stale after Session 1.

## Handoff Writing Guidance

Use `kr-preparing-cc-handoffs` skill. Key considerations for Session 2:

1. **Scope boundary.** Passes 1–3 produce INTERMEDIATE data structures (parsed pages, separated footnotes, cleaned text). They do NOT produce the final ContentUnit output — that's Pass 6 (Session 5). Session 2's output is internal data that Passes 4–6 consume.

2. **ABD code relationship.** The ABD `normalize_shamela.py` handles Passes 1–3 in ~800 lines. CC should read it for Shamela HTML quirk awareness (the metadata page detection, the footnote separator regex, the whitespace rules) but implement fresh code matching SPEC.md's upgraded rules.

3. **Test fixtures are real.** The 11 books in `tests/fixtures/shamela_real/` are actual Shamela exports. Tests should parse these and verify extraction correctness against known content.

4. **Context budget.** SPEC.md is 2,049 lines — CC cannot read all of it. The handoff must specify EXACTLY which SPEC sections to read (§4.A.2 Passes 1–3, §4.A.8, relevant §7 error codes) and which to skip.

5. **Intermediate data structures.** Session 2 needs to define what Passes 1–3 produce internally — likely a list of `RawPage` objects (page number, raw HTML, separated primary text, separated footnotes, volume info) that later passes consume. These are internal to the Shamela normalizer, not part of the public contracts.

## Do NOT Do

- Do NOT implement Passes 4–6. Those are Sessions 3–5.
- Do NOT implement the plain text normalizer. That's Session 6.
- Do NOT modify contracts.py or errors.py (unless a genuine gap is found — document it, don't improvise).

## After Writing

Commit the Session 2 NEXT.md. Owner gives it to CC.
