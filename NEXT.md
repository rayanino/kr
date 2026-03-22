# NEXT — Excerpting Engine SPEC Review (Adversarial)

## Current Position

- Source engine: validation in progress (Step 2 — deterministic sweep)
- Normalization engine: ✅ COMPLETE (420 tests, 7797 impl lines)
- Architecture: COMMITTED (5 engines: Source → Normalization → **Excerpting** → Taxonomy → Synthesis)
- Architecture C experiment: ✅ PASS (10 prose divisions, 5 genres)
- Format diversity experiment: ✅ PASS (13 divisions: verse-commentary + longer prose + masala + QA)
- **Excerpting engine SPEC_CORE.md: DRAFTED (77.6KB, all 10 sections complete)**
- **This session: Adversarial review of the SPEC before build**

## Session Start Protocol

1. Clone or pull the repo
2. Read this file (NEXT.md)
3. `git log --oneline -5`
4. Read the protocol file: `reference/protocols/QUALITY_AXIOM.md` (this is a review/design task)
5. **Scan skills:** Run `ls /mnt/skills/user/` and choose ALL relevant skills by name. Key skills for this task: `kr-integrity`, `critical-review`, `thinking-frameworks`. Do NOT rely on memory for skill names.

## What to Do

Review `engines/excerpting/SPEC_CORE.md` — the governing specification for the excerpting engine. This SPEC was written in a prior session and MUST be reviewed in a fresh context per QUALITY_AXIOM.md.

**This is a SPEC review session, not a design or build session.**

The review must be adversarial — the goal is to find what's wrong, not to confirm what's right. The SPEC author flagged 5 concerns (see §3 of the handoff file). The reviewer must investigate those AND find concerns the author missed.

## Read First (in this exact order)

1. `reference/protocols/QUALITY_AXIOM.md` — the quality standard this review must meet
2. `reference/archive/sessions/excerpting_spec_handoff.md` — **THE HANDOFF FROM THE DESIGN SESSION** (contains: what was done, 8 design decisions with reasoning + challenge angles, 5 flagged concerns, 6 standard review checks, session retrospective)
3. `engines/excerpting/SPEC_CORE.md` — **THE SPEC TO REVIEW** (all 10 sections, 77.6KB)
4. `engines/normalization/SPEC.md` §3 — the input contract (does the SPEC consume it correctly?)
5. `engines/normalization/contracts.py` — the Pydantic models (does the SPEC reference fields that exist?)
6. `engines/taxonomy/SPEC.md` §2 — the output contract (does the SPEC produce what taxonomy expects?)
7. `engines/excerpting/contracts.py` — the OLD schema (was the migration done correctly?)
8. `KNOWLEDGE_INTEGRITY.md` — corruption threats (does the SPEC defend against all 7?)
9. `experiments/architecture_test/run_tests.py` — the validated LLM schemas (does the SPEC match?)

## Review Protocol

Use `kr-integrity` for the review. The review has three rounds:

**Round 1 — Structural audit (one response).** Read the full SPEC. For each section, check:
- Every field the SPEC consumes from upstream: does it exist in normalization contracts.py?
- Every field the SPEC produces for downstream: does taxonomy SPEC §2.1 expect it?
- **Internal consistency: do the §3.4 guarantees, §5 validation checks, and §7 error codes all reference the same fields that §3.1 defines?** A guarantee that promises a field not in the schema is a phantom guarantee.
- Every error code: does it have a concrete trigger scenario?
- Every processing rule: can a pass/fail test be written for it?
- Every numerical threshold: is it justified by evidence or is it a guess?
- Deliver findings. End the response.

**Round 2 — Adversarial probes (separate response, after owner says continue).** For each of the 5 flagged concerns in the handoff, investigate independently:
- Concern 1 (taxonomy contract mismatch): grep taxonomy SPEC for `atom_ids`, determine scope of update
- Concern 2 (old contracts.py still exists): check if any code imports from it
- Concern 3 (Phase 3 prompts untested): compare against experiment prompts, identify risk
- Concern 4 (evidence detection patterns): check Arabic marker patterns against normalization's known false positive lessons
- Concern 5 (concrete example untraced): trace the §4.A.1 example through the SPEC rules step by step

Then: run the unconstrained adversarial pass (QUALITY_AXIOM standing order 7). Ask: "What is the review NOT checking?" Find at least 2 concerns the author did not flag.

**Round 3 — Verdict (separate response, after owner says continue).**
- Verify every factual claim from Rounds 1-2 with a tool call
- Fill severity for each finding: MUST-FIX (blocks build) or SHOULD-FIX (fix during build)
- Deliver verdict: ACCEPT (zero MUST-FIX findings) or BLOCKED (any MUST-FIX findings)
- If BLOCKED: list the MUST-FIX items with specific resolution guidance

## Skills to Use

- `kr-integrity` — 8-lens SPEC audit including T-1–T-7, silent failures, phantom metadata
- `critical-review` — self-review with KR-specific verification questions
- `thinking-frameworks` — multi-angle analysis for adversarial probes

## Do NOT Do

1. Do NOT write implementation code
2. Do NOT redesign the SPEC — identify problems, don't solve them (the design session solves them)
3. Do NOT approve the SPEC in Round 1 or Round 2 — verdict is ONLY in Round 3
4. Do NOT use "ACCEPT WITH FIXES" — that verdict does not exist
5. Do NOT trust the author's self-assessment — review independently
6. Do NOT skip reading the handoff file — it contains the author's flagged concerns AND the reasoning behind every design decision (which you need to challenge)

## After This

If ACCEPT: proceed to build prep (kr-build-prep) in the same or next session.
If BLOCKED: return to a design session to fix MUST-FIX items, then re-review.
