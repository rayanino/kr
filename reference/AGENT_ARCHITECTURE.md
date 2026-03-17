# Agent Team Architecture — بنية فريق الوكلاء

**Status:** GOVERNING — defines how all remaining engines are built
**Authority:** Approved by Architect (Claude Chat), March 2026
**Companion to:** ENGINE_BUILD_BLUEPRINT.md (the methodology this architecture executes)

---

## 1. Core Design

### 1.1 The Problem

The source engine took ~25 sessions. ~14 of those were evaluation (per-book
web-search verification). If every remaining engine needed the same evaluation
intensity, that's ~84 more sessions. The architecture automates evaluation
while maintaining the verification quality that caught real bugs (1 author
misattribution, 3 wrong source labels, 1 consensus module bug, 12 tahqiq-note
bias instances).

### 1.2 Six Governing Principles

**P1: Knowledge diversity over search diversity.** Verifier A uses the
Decision Playbook; Verifier B works from first principles + web research
only, with NO Playbook access. Agreement between a guided and an unguided
verifier is stronger evidence than agreement between two guided verifiers.
When they disagree AND Verifier A used a Playbook rule, that rule is flagged
for Architect review. This catches the BUG-03 class of errors — wrong
assumptions baked into institutional memory.

**P2: Disk is the boundary, never memory.** No single Claude Code context
holds all state. Each verification batch processes 20 items, writes verdicts
to disk, updates ENGINE_STATE.json, and commits to git. Any session can
resume from the last checkpoint. This scales from 50 books to 50,000.

**P3: Probe before deploy.** Every agent team is tested on real work (the
normalization engine) before being trusted on subsequent engines. Each probe
simultaneously tests the architecture AND produces a real deliverable.

**P4: Match rigor to risk.** Three verification profiles:
- **Deterministic** (passaging): single structural inspector, no N-version
- **LLM-light** (normalization, taxonomy): knowledge-diverse N-version
- **LLM-heavy** (atomization, excerpting, synthesis): full N-version + enhanced Red Team

**P5: 18 focused agents, not 41 diluted ones.** Each agent has a role no
existing agent or hook already fills. Pre-commit hooks (Arabic safety, SPEC
check, boundary validation) are infrastructure, not agents.

**P6: Architect stays in the loop at 5 points per engine.** SPEC approval,
code audit, pilot verify, GO/NO-GO, completion review. Everything between
these checkpoints runs autonomously.

### 1.3 Three-Tier Scale Model

| Tier | Books | When | Verification |
|------|-------|------|-------------|
| Development | 50 | During BUILD | 100% N-version |
| Validation | 500 | During EVALUATE | Risk-tiered N-version |
| Production | Full Shamela | After all 7 engines proven | 100% Layer 1 + 10% N-version sample |

Owner has offered the full Shamela library for Tier 3. Download and make
available at a known path before reaching Tier 3 (after all 7 engines proven
at Tier 2).

---

## 2. Agent Census — 18 Definitions

### 2.1 SPEC Team (6 agents, all Opus)

| Agent | File | Role |
|-------|------|------|
| Auditor A | `spec-auditor-a.md` | Cold reads SPEC against silent failure patterns 1-4 |
| Auditor B | `spec-auditor-b.md` | Cold reads SPEC against patterns 5-7 + T1-T7 threats |
| Comparator | `audit-comparator.md` | Merges dual inventories, investigates one-sided findings |
| Researcher | `deep-researcher.md` | 8+ web searches per CORRECTNESS defect (rewrite of existing) |
| SPEC Writer | `spec-writer.md` | Rewrites defective sections (existing, keep) |
| Integrity Auditor | `integrity-auditor.md` | kr-integrity: ambiguity, corruption paths, missing errors |

**Workflow:** Auditors A and B run in parallel with NO communication →
Comparator merges → Researcher investigates each CORRECTNESS defect →
SPEC Writer rewrites → Integrity Auditor runs final check → Architect
approves.

### 2.2 Build Team (3 subagents + Claude Code main)

| Agent | File | Role |
|-------|------|------|
| Test Engineer | `test-engineer.md` | SPEC-driven pytest suites (existing, keep) |
| Code Reviewer | `code-reviewer.md` | Reviews code vs SPEC (existing, keep) |
| Boundary Validator | `boundary-validator.md` | Contract compatibility (existing, keep) |
| Claude Code main | (not an agent file) | The builder — implements modules |

**Workflow:** Architecture Planner function (in the main CC session) reads
SPEC + stubs → produces session sequence → each session runs: builder
implements → test engineer writes tests alongside → code reviewer checks
at session end → boundary validator runs on contracts changes.

### 2.3 Verification Team (4 agents)

| Agent | File | Model | Role |
|-------|------|-------|------|
| Triage Analyst | `triage-analyst.md` | Sonnet | Automated checks on ALL items (€0) |
| Verifier A | `verifier-a.md` | Opus | Playbook-guided verification |
| Verifier B | `verifier-b.md` | Opus | First-principles verification (NO Playbook) |
| Consolidator | `consolidator.md` | Opus | Compares A vs B, resolves disagreements, 5-round self-review |

**Workflow (per batch of 20 items):**
1. Triage Analyst runs automated checks → produces risk tiers
2. For each item: Verifier A produces verdict, Verifier B produces verdict
3. Consolidator compares, investigates disagreements, produces final verdict
4. Quality gate checks (every 20 items): format, sources, distribution, drift
5. Write 20 verdicts to disk, update ENGINE_STATE.json, commit

**Knowledge diversity (P1):**
- Verifier A reads: Playbook §relevant-sections, pipeline output, source text
- Verifier B reads: pipeline output, source text, web research results ONLY
- Verifier B NEVER reads the Playbook — this is enforced in the agent prompt
- When A agrees and B disagrees → Playbook rule flagged for review
- When A disagrees and B agrees → Playbook may be overly cautious
- When both disagree → genuine problem, escalate

**Adaptation per engine type:**
- **Knowledge engines** (source, synthesis): Verifiers do web search
- **Structural engines** (normalization, passaging): Verifiers inspect output vs raw source
- **Hybrid engines** (atomization, excerpting, taxonomy): Both web search and structural inspection

### 2.4 Red Team (3 agents, all Opus)

| Agent | File | When Active | Role |
|-------|------|-------------|------|
| SPEC Adversary | `spec-adversary.md` | After SPEC finalized | Writes adversarial test cases from SPEC |
| Build Prober | `build-prober.md` | After each build session | Reviews cumulative diff vs SPEC |
| Verdict Adversary | `verdict-adversary.md` | During evaluation | Re-probes VERIFIED items with different strategy |

**Red Team is NOT post-hoc.** It runs at every stage:
- SPEC adversary during SPEC_DESIGN (before build starts)
- Build prober at session boundaries during BUILD (not per-commit)
- Verdict adversary during EVALUATE (probes 20-30% of VERIFIED items)

### 2.5 Infrastructure (hooks, not agents)

These already exist in `.claude/settings.json` and cost €0:
- Arabic safety hook (blocks .lower()/.upper() on Arabic text)
- Pre-commit SPEC quality check
- Boundary validator trigger on contracts.py changes
- Budget tracker (COST_LOG.json)
- Post-compaction recovery from NEXT.md

---

## 3. Orchestration — ENGINE_STATE.json

No monolithic orchestrator. State persists to disk.

```json
{
  "engine": "normalization",
  "phase": "EVALUATE",
  "tier": 1,
  "items_total": 50,
  "items_verified": 20,
  "items_remaining": 30,
  "current_batch": 2,
  "batch_size": 20,
  "quality_gate_results": [
    {"batch": 1, "pass": true, "checks": {"format": true, "sources": true, "drift": 0.02}}
  ],
  "drift_baseline": 0.04,
  "novel_patterns_pending": 1,
  "escalations_pending": 0,
  "verifier_agreement_rate": 0.85,
  "verdict_distribution": {"VERIFIED": 16, "PLAUSIBLE": 3, "FLAG": 1}
}
```

**Recovery:** If a session crashes, the next session reads ENGINE_STATE.json
and resumes from the last committed batch. Max data loss: 20 items (1 batch),
re-processable.

**State transitions (same as Blueprint steps):**

IDLE → SPEC_DESIGN → BUILD → CODE_AUDIT → PILOT_VERIFY → EVALUATE → GO_NO_GO → HARDEN → COMPLETE → IDLE

Each transition requires exit conditions (documented in Blueprint). NO-GO
rolls back to the appropriate earlier state.

---

## 4. Quality Gates

### 4.1 Verification Quality Gate (every 20 items)

| Check | Pass condition | Fail action |
|-------|---------------|-------------|
| Format | All verdicts have 14 required fields | Halt, fix verifier prompt |
| Sources | Verifier B: web_fetch count ≥ 1 per item | Halt, escalate to Architect |
| Distribution | Not >90% VERIFIED (suspicious) | Flag for Architect review |
| A-B agreement | 60-95% agreement rate | <60%: something wrong. >95%: checking same thing |
| Drift | Error rate vs pilot baseline ±15% | Halt, recalibrate |
| Novel patterns | Count of CANDIDATE_PATTERN flags | Batch for Architect review |

### 4.2 Playbook Growth (per engine)

1. Verifier B's first-principles work naturally produces novel observations
2. Consolidator captures disagreements as CANDIDATE_PATTERN when B's reasoning
   differs from A's Playbook-guided reasoning
3. Architect validates candidates at PILOT_VERIFY and GO/NO-GO checkpoints
4. Validated patterns promoted to new Playbook sections (§11+)

This works because Verifier B's investigation is already done — the Architect
only needs to validate (quick), not investigate (slow).

---

## 5. Bootstrap — Three Probes on the Normalization Engine

The normalization engine is both the first deliverable AND the architecture
test. Each probe tests a team AND produces a real deliverable.

### Probe 1: SPEC Team

**Write:** 6 agent definitions in `.claude/agents/`
**Run:** Dual audit of normalization SPEC (2,007 lines)
**Deliverable:** Audited + rewritten normalization SPEC
**Measure:** Did dual audit find defects Architect didn't? How many one-sided
findings? Were the one-sided findings real or false positives?
**Adjust:** If dual audit adds <20% more findings than single audit, consider
merging auditors into one with expanded checklist.

### Probe 2: Build Team

**Write:** 3 agent definitions (test engineer, code reviewer, boundary
validator already exist — may need updates)
**Run:** Build the normalization engine (5-7 sessions)
**Deliverable:** Built normalization engine with tests
**Measure:** Did code reviewer catch bugs tests missed? How many improvisation
flags from Build Prober? Were handoff prompts sufficient?
**Adjust:** If code reviewer adds <2 findings per session, it may not justify
the overhead — consider running only at session boundaries.

### Probe 3: Verification Team

**Write:** 4 agent definitions
**Run:** N-version verification on 50 development books (Tier 1)
**Deliverable:** 50 verified normalization outputs
**Measure:** How many A≠B disagreements? What fraction were Playbook errors
(P-03 defense)? Did quality gates fire? Were they accurate?
**Adjust:** If A-B agreement is >95% with no Playbook-triggered disagreements,
knowledge diversity may not add value for structural engines — consider
single verifier for passaging.

---

## 6. Engine-Specific Notes

### Normalization (next — full Blueprint, LLM-light profile)

- Input: 279 real SourceMetadata records
- Key risk: T-1 (silent text corruption) — text fidelity scoring is critical
- Verification type: structural inspection (compare normalized vs raw HTML)
- Playbook growth: new §11 (layer detection heuristics, fidelity scoring)
- Contract boundary: 12 fields verified in CONTRACT_VERIFICATION_REPORT.md

### Passaging (deterministic profile)

- Mostly heuristic boundary detection, minimal LLM
- Verification: single structural inspector (passage boundaries are checkable)
- Compressed Blueprint: Steps 1-2 can merge, Layer 3 uses smaller sample

### Atomization (LLM-heavy profile — first LLM-primary engine)

- LLM does the PRIMARY work (scholarly function classification)
- Highest risk of new domain patterns (scholarly function boundaries)
- Playbook growth: new §12 (scholarly function edge cases)
- Red Team enhanced: Build Prober + Verdict Adversary at full cadence

### Excerpting (LLM-heavy profile)

- Self-containment verification is the core challenge (T-4)
- Benefits from atomization patterns (similar LLM classification work)
- Playbook growth: new §13 (self-containment edge cases)

### Taxonomy (LLM-light profile)

- Needs parsed science tree BEFORE build (prerequisite artifact)
- Placement confidence is the key quality metric
- Verification: structural (does the placement make sense in the tree?)

### Synthesis (LLM-heavy profile + dedicated grounding checker)

- Highest hallucination risk (T-5) — the Red Team doubles its effort
- Grounding check: every factual claim must trace to a specific excerpt ID
- The only engine where the Red Team's Verdict Adversary checks CONTENT
  (not just metadata) — it reads synthesized entries and verifies claims
  against cited excerpts

---

## 7. Owner Interaction Model

The owner has zero technical background. Three touchpoints per engine:

1. **Human gate queue** — batched at engine completion, reviewed via GUI
2. **Preference decisions** — edition choice, curriculum ordering (blocks until answered)
3. **Engine completion acknowledgment** — "looks good, proceed"

The owner does NOT review agent output, debug failures, or validate domain
correctness. Domain validation is done by the Verification Team (via web
research) and the Architect (at 5 checkpoints per engine).

---

## 8. Risk Registry

| Risk | Severity | Detection | Mitigation |
|------|----------|-----------|------------|
| Playbook common-mode failure | CRITICAL | A≠B disagreement where A used Playbook | Verifier B has NO Playbook access (P1) |
| Context overflow | CRITICAL | SESSION_STATE tracking | 20-item batches, disk boundary (P2) |
| Agent drift (gradual quality decline) | HIGH | Quality gate every 20 items | Drift detection vs pilot baseline ±15% |
| Build improvisation (G-2 gap) | HIGH | Build Prober reads session diff | Code audit by Architect catches remainder |
| Cross-engine contract breakage | HIGH | Boundary validator hook | Pre-commit, result regression, integration canary |
| Silent Arabic text corruption | HIGH | Arabic safety hook + fidelity scoring | NFC check, adversarial Arabic fixtures |
| Novel patterns overwhelming Architect | MEDIUM | Count of CANDIDATE_PATTERN per engine | Verifier B pre-investigates; Architect validates only |
| Red Team overhead during build | MEDIUM | Build Prober runs per-session, not per-commit | 4-7 runs per engine, not hundreds |

---

## 9. What This Architecture Does NOT Cover

1. **Stage 2 expansion** — adding non-core capabilities to built engines
2. **Scholar Interface** — the owner-facing application
3. **Full library population** — Tier 3 production run (deferred until all engines proven)
4. **Cross-engine optimization** — performance tuning across the pipeline
5. **The science tree prerequisite** — needed before taxonomy engine, separate work item
