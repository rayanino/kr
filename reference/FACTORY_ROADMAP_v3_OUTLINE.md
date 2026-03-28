# FACTORY_ROADMAP_v3 Outline — Changes from v2

**Authority:** This outline governs the rewrite of `FACTORY_ROADMAP_v2.md` into v3.
**Date:** 2026-03-28
**Source:** Roadmap Revision Session — 8 decisions + 2 additional decisions.
**Method:** Claude Chat architect analysis of owner's strategic reframe, repo state verification (365-book source engine validation confirmed), adversarial review of each decision from 3+ perspectives.

---

## Identity Change (Decision 1)

**Old identity:** "Build a control plane that autonomously builds, tests, evaluates, and hardens KR engines."
**New identity:** "Build a control plane that autonomously tests, evaluates, and hardens KR engines. The architect builds engines manually; the factory ensures they are bulletproof."

### What changes in the Goal section
- Remove "builds" from the goal statement
- Remove "receives a SPEC → decomposes it into work units → builds across multiple CC sessions" from the "Done means" definition
- Replace with: "receives a tagged engine phase → generates adversarial tests → hunts for bugs → classifies findings by epistemic severity → fixes what it can → escalates what it can't → presents the owner with evidence packets for genuine human decisions → produces a proven engine"
- Add: "The factory does NOT build engines from SPECs. Engine building happens manually (Claude Chat architect + Claude Code builder). The factory's job is to make what's been built bulletproof."

### What changes in the Architecture diagram
- Remove "SPEC-to-task decomposition" from orchestrator description
- Add "factory_scope reader" to orchestrator description
- Add "noise circuit-breaker" to orchestrator description
- Add "severity classifier" to orchestrator description

---

## AQS Changes (Decision 1 + Decision 5)

### Mode list (was 6, now 5)
1. ~~BUILD~~ — **REMOVED**
2. HUNT (default) — unchanged
3. FIX — **MODIFIED** (severity-graduated autonomy, see below)
4. EVALUATE — unchanged
5. CROSS-ENGINE — unchanged
6. BENCHMARK — unchanged

### Mode priority
**Old:** `FIX > BUILD > EVALUATE > HUNT > CROSS-ENGINE > BENCHMARK`
**New:** `FIX > EVALUATE > HUNT > CROSS-ENGINE > BENCHMARK`

### FIX mode autonomy (Decision 5)

Replace the current FIX description with severity-graduated model:

| Severity | Definition | Factory Action | Merge Authority |
|----------|-----------|---------------|----------------|
| CRITICAL | Owner would learn something false (wrong attribution, decontextualized excerpt, conflated positions) | Log finding. **PAUSE hunting that engine phase.** Do NOT auto-fix. Flag in morning report. | Architect reviews and directs fix |
| HIGH | Structural correctness at risk (crash, contract violation, data loss) | Log finding. CC proposes fix on branch. Codex reviews. Gemini challenges. Do NOT merge. | Architect approves merge |
| MEDIUM | Defensive gap, no current epistemic impact (missing edge case, incomplete validation) | CC auto-fixes. Codex reviews. Gemini challenges. Full regression. Auto-merge if all pass. | Factory (cross-provider consensus) |
| LOW | No epistemic or structural impact (log quality, naming, dead code) | CC auto-fixes. CC self-reviews. Auto-merge if tests pass. | Factory (single-provider) |

**CRITICAL pause mechanism:** When a CRITICAL finding is logged, the orchestrator sets the affected engine phase to `status: "paused"` in `ops_manifest.json` with `reason: "CRITICAL finding [ID]"`. Hunting that phase stops until the architect reviews the finding, directs a fix, and manually unpauses the scope. Other engine phases continue being hunted normally.

### Time allocation (revised)
- HUNT: ~55-65% (increased from 50-60% — absorbs former BUILD allocation)
- FIX: ~15-20% (unchanged)
- EVALUATE: ~10-15% (slightly increased — more emphasis on owner review prep)
- CROSS-ENGINE: ~5-10% (unchanged)
- BENCHMARK: ~2-5% (unchanged)

---

## Team Architecture Changes (Decision 1)

### Remove BUILD team entirely
The BUILD team section (4 teammates: IMPLEMENT, REVIEW, TEST, VALIDATE) is removed. The BUILD team communication diagram is removed.

### Retained teams
- HUNT team (3 agents) — unchanged
- FIX team (3 agents) — add severity awareness (CRITICAL/HIGH findings get logged, not auto-fixed)
- EVALUATE team (2 agents) — unchanged
- CROSS-ENGINE uses HUNT team composition

### Add to team principles
"No team composition exists for BUILD mode. Engine building is manual (Claude Chat architect designs, Claude Code implements, structured review protocol verifies). The factory hunts what's been built."

---

## WIP/TESTED Boundary (Decision 2)

### New section in FACTORY_ROADMAP_v3: "Factory Scope Management"

**The factory only hunts what the architect has explicitly tagged as testable.**

Machine-readable scope in `ops_manifest.json`:
```json
{
  "factory_scope": {
    "<engine_name>": {
      "status": "tested|partial|paused|wip|not_started",
      "testable_phases": ["phase1_assembly", ...],
      "excluded_phases": ["phase3_enrichment", ...],
      "ground_truth_books": 365,
      "owner_review": "pending|partial|complete",
      "paused_reason": null,
      "since": "ISO-8601 date"
    }
  }
}
```

Human-readable documentation: each engine gets `engines/<name>/FACTORY_SCOPE.md`.

**Noise circuit-breaker:** If a single hunt cycle produces >10 findings against one engine phase, that phase is auto-paused with reason "noise_threshold_exceeded". The morning report flags this. The architect investigates — either the scope is wrong (fix manifest) or there's a genuine cluster of bugs (triage findings).

**Status transitions:**
- `not_started` → `wip`: Architect begins engine design
- `wip` → `partial`: Architect tags specific phases as testable
- `partial` → `tested`: All phases tagged as testable
- `tested` → `paused`: CRITICAL finding or noise threshold
- `paused` → `tested`: Architect reviews and unpauses
- Any → `paused`: Automatic on CRITICAL finding

### New section: "Day 1 Scope" (Decision 4)

When the factory first runs after Session 7:

| Engine | Phases in Scope | Ground Truth | Notes |
|--------|----------------|-------------|-------|
| Source | All | 398 tests + 2,519-book sweep + 365-book LLM results + transition gate approved (a21aab9a) | Owner metadata review pending |
| Normalization | All | 404 tests + transition gate approved | Engine complete |
| Excerpting | Phase 1 only | ~200 Phase 1 tests + fixtures | Phases 2-3 excluded (active development) |
| Taxonomy | None | N/A | Not started |

Cross-engine boundaries: source→norm (tested), norm→excerpting Phase 1 (tested).

---

## Session Changes

### Session 1 — Operational Truth + Document Reconciliation
**Changes from v2:**
- ADD: `factory_scope` section to `ops_manifest.json` schema
- ADD: Update source engine status in all docs — "Source ✅ (transition gate approved a21aab9a; LLM validated on 365 books including 70 edge-case Phase E books; owner metadata review pending — integrated into excerpting review)"
- ADD: Create `engines/source/FACTORY_SCOPE.md`, `engines/normalization/FACTORY_SCOPE.md`, `engines/excerpting/FACTORY_SCOPE.md`
- ADD: Update `VALIDATION_PLAN.md` — mark Phases C, D, E as complete with actual costs
- ADD: Reconcile `source_engine_roadmap.jsx` project file (remove non-existent Step 5, update costs, mark Steps 2-4 complete)
- KEEP: Everything else (ops_manifest creation, AGENT_ARCHITECTURE update, CLAUDE.md update, Playbook provenance)

### Session 2 — CI/CD Hardening + Policy Engine
**Changes from v2:** None. This session is infrastructure — unaffected by the reframe.

### Session 2.5 — WSL2 Setup
**Changes from v2:**
- ADD: Paperclip Arabic smoke test during setup (~15 min)
  - Install Paperclip in WSL2
  - Create a test task with Arabic text (real excerpt from Phase C results)
  - Verify: Arabic renders correctly, diacritics preserved, RTL handled
  - Verdict: PASS (proceed to Session 8 evaluation) or FAIL (Paperclip eliminated)

### Session 3 — CLI Setup + Dispatch Layer
**Changes from v2:**
- REMOVE: BUILD team composition design (no BUILD team needed)
- SIMPLIFY: Team compositions cover HUNT, FIX, EVALUATE only
- KEEP: CLI abstraction layer, AGENTS.md (Codex context), GEMINI.md (Gemini context), dispatch scripts, artifact ledger
- KEEP: Cross-provider cycle test

### Session 4 — Benchmark Design
**Changes from v2:**
- ADD: Use excerpting model role research findings (NEXT.md Task 1) to inform benchmark task design
- ADD: Weight benchmark tasks by epistemic impact, not uniform
- KEEP: 9 task types, adversarial cases, ground truth verification

### Session 4.5 — Synthetic Adversarial Data
**Changes from v2:**
- REMOVE: "Full-pipeline synthetic books that traverse all engines including ones that don't exist yet"
- REPLACE WITH: Synthetic data targets in-scope engines only (source, normalization, excerpting Phase 1)
- ADD: Synthetic data respects `factory_scope` — only generates data for testable phases
- KEEP: Threat templates, generation process, Codex/Gemini generate + CC processes pattern

### Session 5 — Benchmark Run + Routing Table
**Changes from v2:** Minimal. Same process, same output.

### Session 6 — Orchestrator Extension
**Changes from v2 (SIGNIFICANT SIMPLIFICATION):**
- REMOVE: SPEC-to-task decomposition engine
- REMOVE: Work-unit system for BUILD-type tasks
- REPLACE: Orchestrator EXTENDS `scripts/overnight_orchestrator.py` (1,405 lines of battle-tested code)
- ADD: Multi-mode dispatch (HUNT/FIX/EVALUATE/CROSS-ENGINE/BENCHMARK)
- ADD: Factory scope reader (reads `ops_manifest.json` factory_scope section)
- ADD: Findings management with severity classification (CRITICAL/HIGH/MEDIUM/LOW)
- ADD: Severity-graduated fix autonomy (Decision 5 rules)
- ADD: CRITICAL pause mechanism (auto-pauses scope on CRITICAL findings)
- ADD: Noise circuit-breaker (auto-pauses on >10 findings per phase per cycle)
- KEEP: Work-unit queue for FIX/HUNT tasks (simplified — no BUILD units)
- KEEP: Artifact provenance bundles
- KEEP: Policy enforcement

### Session 7 — Scheduled Execution + Recovery
**Changes from v2:**
- ADD: Recovery handles paused scopes (doesn't unpause — that requires architect review)
- ADD: Morning report includes: paused scopes with CRITICAL finding IDs, findings queue depth by severity, hunt coverage by engine phase
- KEEP: Task Scheduler, lock file, heartbeat, crash recovery

### Session 8 — Dashboard + Human Gate + Arabic Formatter
**Changes from v2:**
- ADD: Paperclip decision point (if WSL2 smoke test passed in Session 2.5)
- ADD: Dashboard shows factory scope status per engine per phase
- ADD: Dashboard shows findings by severity with CRITICAL findings highlighted
- ADD: Source engine metadata review packets in EVALUATE mode output
- KEEP: Arabic formatter with Amiri font, human gate queue, evidence packets

### Sessions 9-10 — Hardening
**Changes from v2:**
- MODIFY: Acceptance test point 1 — "Autonomous wake-up" tests hunt mode, not build mode
- MODIFY: Acceptance test point 4 — "Policy enforcement" tests severity-graduated fix, not same-provider-only review
- ADD: Acceptance test — "CRITICAL pause": inject a CRITICAL finding → verify scope pauses → verify morning report flags it
- ADD: Acceptance test — "Noise circuit-breaker": inject >10 findings → verify scope auto-pauses
- KEEP: All other acceptance test points

---

## New Design Decisions

Add to the Design Decisions section:

**D-F013: PDF scan integration is a format path within the source engine.**
Not a new engine. The factory validates by cross-referencing PDF extraction against Shamela extraction for overlapping books. Phase 3 work — not designed until Phase 1 is bulletproof. (Decision 6)

**D-F014: Synthesis engine deferred until Phase 1 reaches Quality Level 4+.**
All Phase 1 engines (Source, Normalization, Excerpting, Taxonomy) must reach Quality Level 4 in the AQS maturity model before synthesis work begins. Level 4 = factory has hunted for weeks, CRITICAL findings resolved, owner has reviewed real output. This is "100% robust and bulletproof" expressed in measurable terms. (Owner directive, formalized)

**D-F015: Factory identity is quality guardian, not engine builder.**
The factory does not build engines from SPECs. Engine building is manual (Claude Chat architect + Claude Code builder). The factory's sole purpose is making what's been built bulletproof through relentless, creative, exhaustive quality hunting. BUILD mode exists only as a documented future capability, not an active operating mode. (Decision 1)

**D-F016: FIX autonomy is severity-graduated.**
CRITICAL and HIGH findings require architect review before merge. MEDIUM and LOW findings are auto-fixed with appropriate review levels. CRITICAL findings additionally pause hunting of the affected engine phase. (Decision 5)

---

## Interleaving Timeline (Revised — Decision 7)

| Timeline | Engine Track | Factory Track | Owner Involvement |
|----------|-------------|---------------|-------------------|
| Week 0 | — | Owner: WSL2 setup + Paperclip smoke test | ~3 hours one-time |
| Week 1 | Excerpting: model role research (Task 1) | CC: Sessions 1-2 (no owner needed) | Excerpting review priority |
| Week 2-3 | Excerpting: 5-book integration review | Owner: CLI auth (30 min for Session 3) | Excerpting review priority |
| Week 4-5 | Excerpting: 30-book owner probe begins | CC: Sessions 4-5 (benchmark) | Excerpting review priority |
| Week 6-7 | Excerpting: probe continues | CC: Sessions 6-7 (orchestrator + scheduler) | Excerpting review priority |
| Week 8 | Factory starts hunting (Day 1 scope) | CC: Sessions 8-10 (dashboard, hardening) | Factory runs autonomously |
| Week 9+ | Excerpting: probe completes, engine tagged testable | Factory scope expands to excerpting Phases 2-3 | Owner reviews factory findings |
| Week 12+ | Taxonomy: SPEC design begins | Factory hunts source + norm + excerpting | Architect + owner on taxonomy |
| Week 16+ | Taxonomy: build + review | Factory hunts all Phase 1 engines | Factory scope grows |
| Week 20+ | All Phase 1 engines complete | Factory hunts continuously for months | Owner reads excerpts |
| Month 6+ | Phase 1 at Quality Level 4+ | Feature expansion (PDF scans) | Decision point: Phase 2? |

---

## What This Plan Does NOT Include (Updated)

1. **No BUILD mode.** Engine building is manual. The factory hunts, fixes, evaluates.
2. **No Claude Chat in the autonomous loop.** Requires owner presence.
3. **No frozen Arabic model roles.** Blocked on benchmark (Session 5).
4. **No database.** File-based state suffices for single-user.
5. **No synthesis engine work.** Deferred until Phase 1 at Quality Level 4+ (D-F014).
6. **No auto-fix of CRITICAL findings.** Architect reviews these. (D-F016).
7. **No SPEC-to-task decomposition.** The factory doesn't need to understand SPECs — it tests tagged engine phases.
8. **No Paperclip commitment.** Quick smoke test during WSL2 setup; full decision at Session 8.
9. **No full-pipeline synthetic books.** Synthetic data targets in-scope engines only.
10. **No agent society.** Models are workers dispatched by software.
