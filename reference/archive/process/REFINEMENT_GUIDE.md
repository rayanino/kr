# SPEC Refinement — Quick Reference

This replaces reading 5 separate docs. Refer to the full docs only when you need deep detail.

---

## Session Flow (do this, in this order)

### Phase 1: INVENT (40% of session — do this while context is fresh)

**Step 0: Creative Exploration** — Before any review.

Ask 5 questions a world-class Islamic scholar would dream of answering but can't:
- "If I had every book ever written, what question is still impossible to answer?"
- "What takes a scholar weeks that technology could do in seconds?"
- "What do Latin/Chinese/Hebrew digital humanities tools have that Arabic tools don't?"

Then search the web. Minimum 8 searches, structured:
- 3 searches: map what exists for this engine's domain
- 3 searches: explore what's technically possible NOW (latest LLMs, Arabic NLP, digital humanities)
- 2 searches: validate your proposed capabilities work on Arabic text

Deliverable: 3+ new capabilities for §4.B, each with: named tool/technique, concrete output example.

### Phase 2: ANALYZE (30% of session)

**Step 1: Cold Read** — Read the SPEC as a fresh implementer. Can you build this without clarifying questions?

**Step 1.5: Quality Scan** — Run `python3 scripts/check_spec_quality.py engines/<n>/SPEC.md --verbose`. Record baseline.

**Step 2: Corruption Risks** — For each output field: if wrong, does the user learn something false? Map every SILENT corruption path to a specific validation in §5.

7 threats (from KNOWLEDGE_INTEGRITY.md): text corruption, attribution error, taxonomic misplacement, context stripping, false consensus representation, coverage blind spots, cascading errors.

**Step 3: Machine-Readability** — For each §4.A rule: write mental function signature + pseudocode. Can't? → defect.

**Step 4: Technology** — For each processing step: is there a better tool now? Search: `[capability] Arabic 2025 2026`.

### Phase 3: FIX and VERIFY (30% of session)

**Step 5: Fix all defects.** Apply fixes. Run quality scanner again. High-severity must drop ≥50%.

**Step 6: Self-Review** — Read fixed SPEC top to bottom. Anti-sycophancy gate: pick the section you're MOST confident about and find 3 defects.

**Step 7: Pre-commit** — Run `python3 scripts/session_quality_gate.py` and `python3 scripts/creative_verification.py engines/<n>/SPEC.md`.

---

## 7 Silent Failure Patterns (check EVERY §4 rule)

1. **Hollow Example** — Example exists but wouldn't catch a wrong implementation
2. **Circular Definition** — "X is done by doing X" after expanding terms
3. **Hand-waving Technology** — "using NLP" without naming the tool
4. **Phantom Metadata** — References a field that no upstream engine produces
5. **Untestable Rule** — No pass/fail condition exists
6. **Missing Error Path** — Happy path defined, failure undefined
7. **Scope Creep Disguise** — Rule that looks specific but actually requires unbounded work

---

## 3 Challenges (run mentally before every commit)

1. **Hostile Implementer** — Read as if someone exploits every ambiguity
2. **Skeptical Scholar** — Could any output mislead a scholar?
3. **Technology Maximalist** — Is there a tool that does this better?

Each must find ≥1 issue. If they don't, you're not looking hard enough.
