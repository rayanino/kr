# NEXT — Probe 1: SPEC Team on Normalization SPEC

## Current position: Agent architecture committed → write SPEC team agents → run on normalization SPEC
## What to do: Write 6 SPEC team agent definitions, then run dual audit on normalization SPEC
## Context: Agent architecture is in reference/AGENT_ARCHITECTURE.md. Source engine is complete.
  Normalization engine is next. The SPEC team agents are being written AND tested simultaneously —
  their first real job IS the normalization SPEC audit.
## Owner action needed: NO — this is a Claude Code task.

---

## Read First (in this order)

1. `reference/AGENT_ARCHITECTURE.md` §2.1 — the 6 SPEC team agents and their workflow
2. `reference/ENGINE_BUILD_BLUEPRINT.md` §Step 1 — the proven SPEC design methodology
3. `SILENT_FAILURES.md` — the 7 patterns Auditor A checks (patterns 1-4) and Auditor B checks (5-7)
4. `KNOWLEDGE_INTEGRITY.md` — the 7 threats Auditor B checks (T1-T7)
5. `reference/DECISION_PLAYBOOK.md` §3-4 — genre and multi-layer rules (most relevant for normalization)
6. `engines/normalization/SPEC.md` — the 2,007-line SPEC to be audited
7. `.claude/agents/*.md` — existing agent definitions to understand the format

## What to Build

### Phase A: Write 6 Agent Definitions

Write these files in `.claude/agents/`:

1. **`spec-auditor-a.md`** (Opus)
   - Reads the full SPEC
   - Checks every section against silent failure patterns 1-4:
     (1) hollow examples, (2) circular definitions, (3) hand-waving technology, (4) phantom metadata
   - Produces a numbered defect inventory with CORRECTNESS vs STYLE severity
   - Self-review: 2 rounds per Blueprint Step 1a

2. **`spec-auditor-b.md`** (Opus)
   - Reads the full SPEC
   - Checks every section against patterns 5-7 + all 7 corruption threats:
     (5) untestable rules, (6) missing error paths, (7) scope creep, T1-T7
   - Produces a numbered defect inventory with CORRECTNESS vs STYLE severity
   - Self-review: 2 rounds per Blueprint Step 1a
   - CRITICAL: Auditor B does NOT communicate with Auditor A during audit

3. **`audit-comparator.md`** (Opus)
   - Reads BOTH auditor inventories
   - Classifies each finding: BOTH_FOUND (high confidence) / A_ONLY / B_ONLY
   - For each one-sided finding: investigates whether it is a real defect or false positive
   - Produces a merged, deduplicated defect list

4. **`deep-researcher.md`** (Opus) — rewrite of existing `researcher.md`
   - For each CORRECTNESS defect: runs 8+ web searches
   - Specifically checks: does the named technology work for Arabic?
   - Looks for competing approaches and evaluates tradeoffs
   - Must cite specific URLs, version numbers, benchmarks

5. **`spec-writer.md`** — keep existing, no changes needed

6. **`integrity-auditor.md`** (Opus)
   - Runs the kr-integrity checklist on the revised SPEC
   - Checks: ambiguous rules, missing error paths, corruption vectors, contract alignment
   - Produces MUST-FIX (blocks build) vs SHOULD-FIX (fix during build) classification

### Phase B: Run Dual Audit on Normalization SPEC

After writing the 6 agents, run them on `engines/normalization/SPEC.md`:

1. Invoke `spec-auditor-a` as a Task on the normalization SPEC
2. Invoke `spec-auditor-b` as a Task on the normalization SPEC (parallel if possible)
3. Invoke `audit-comparator` with both inventories
4. Invoke `deep-researcher` for each CORRECTNESS defect
5. Invoke `spec-writer` to rewrite defective sections
6. Invoke `integrity-auditor` on the revised SPEC

### Phase C: Measure Probe Results

After the audit completes, report:
- Total defects found by A only, B only, both
- CORRECTNESS vs STYLE ratio (expect >40% CORRECTNESS if audit is thorough)
- One-sided findings: how many were real vs false positives?
- Any defects that neither auditor found but are obvious in retrospect?

Write results to `reference/PROBE_1_RESULTS.md`.

## Do NOT Do

- Do NOT rewrite the normalization SPEC from scratch — audit and fix sections
- Do NOT read the full SPECs of other engines (normalization only)
- Do NOT implement any engine code — this is SPEC team only
- Do NOT skip the measurement phase (Phase C) — the probe metrics tell us
  whether dual audit adds value

## Verification

After Phase B:
- The audited normalization SPEC has 0 MUST-FIX findings
- Every section 4.A rule can be tested with a pass/fail criterion
- Every processing step has a defined error path
- PROBE_1_RESULTS.md documents the metrics

## After This

Architect (Claude Chat) reviews Probe 1 results and the audited SPEC.
If satisfactory: Probe 2 (Build team on normalization engine).
