# Roadmap Revision Session — Strategic Reframe

## What happened before this session

The factory planning is complete — three governing documents were adversarially reviewed and committed:
- `reference/FACTORY_ROADMAP_v2.md` (setup: 10 sessions, 5 phases)
- `reference/AUTONOMOUS_QUALITY_SYSTEM.md` (operation: 6 modes, hunt/fix/evaluate cycle)
- `reference/TEAM_ARCHITECTURE.md` (collaboration: never solo, always a team)

A Paperclip evaluation was conducted (verdict: EVALUATE_FURTHER). The Claude Chat environment was built out: 3 new skills (technology-landscape, factory-session, tool-evaluation), critical-review updated, 5 memory entries refreshed, kr-research description fixed. An execution plan with 58 micro-tasks was committed to `reference/FACTORY_EXECUTION_PLAN.md`.

During the environment build session, two critical findings emerged that require resolution before execution begins:

**Finding 1:** The source engine is NOT complete. Memory, roadmap, and all documents say "Source ✅" but `engines/source/VALIDATION_PLAN.md` shows Steps 3-4 (LLM validation on 30→200 books) are still PENDING. Only 13 fixtures have been tested with real LLM calls. This means the foundation of the entire pipeline has unvalidated inference logic.

**Finding 2:** The owner provided strategic comments (below) that fundamentally reframe what the factory IS. The current roadmap designs an "autonomous engine builder that also hunts." The owner's vision is an "autonomous quality guardian that the architect feeds testable components into." This changes the factory's identity, priority ordering, team compositions, and several roadmap sessions.

---

## Owner's Strategic Comments (VERBATIM — analyze every sentence)

"My biggest concern, and the entire reason I even want to setup this factory, is rigourous testing and hardening of the pipeline ... I'm almost finished with the excerpting engine, after which the taxonomy engine follows. Since it's pretty much only one more engine that needs to be done, I feel like we don't need to have a whole separate functionality for the factory called 'build engine from spec'; I can just continue building the taxonomy spec manually (claude chat as architect, claude code, ...) since it's merely one last engine.

After these two are done, one of two main functions of the library (getting excerpts at their right location) is done ... after this, I want to pause and run long (months possibly) exhaustive, extensive yet genuinely revealing and beneficial stress testing of the pipeline. I'm talking genuinely stress testing the engine, bug hunting, ... literally pulling its inside out, giving it hard edge mock cases, ... Obviously, this is not mere cosmetic testing, but any flaws found, or any areas to improve on found, need to be at least clearly logged. How that improvement will actually happen (dedicated cases or instantly after identification) is an architectural decision that needs to be made by you, since you're in charge.

Then, after long and exhaustive testing, the next step would be to add features to the then perfectly reliable pipeline. The main features and ones that will most likely bring most benefit is for the pipeline to accept more sources than merely shamela exports. I have some other valuable sources I really want integrated (especially PDF scans since that would literally open up a whole new potential of books and knowledge).

The synthesizing engine can be forgotten about during this period. It is the second major functionality of the library. However, I do not want to continue forward to it until the first major part (everything up until the taxonomy engine) is 100% robust and bulletproof.

Note: the factory will most likely be ready before the taxonomy engine. Therefore, the scope of the factory needs to be always clearly defined; what parts of the pipeline can undergo the testing and robusting the pipeline provides. I'm saying this so that the work-in-progress (me and you manually working out an engine) will not be interfered by the factory; they can happen at the same time. Then everytime a testable part of the current engine in progress is done, it needs to be relayed to the factory. This way, the factory and manual building of engines can happen at the same time. As you can tell, I have no problem with manually building engines (though it is a little tedious); because of how important it is, and since there is only a certain amount of engines (so the effort is worth it). My main concern is with constant and creative out of the box and exhaustive testing and improvement, together with implementing features. Though those features are - in some way - also part of 'building engines' which I also have no problem doing manually, but only in case the factory genuinely cannot reliable implement those features."

---

## Architect's Analysis of the Owner's Comments

### What the owner is actually saying (implicit architecture decisions)

**1. The factory's purpose is NARROWER and MORE FOCUSED than the roadmap assumes.**

The roadmap designs 6 operating modes with BUILD as a first-class citizen. The owner is saying: BUILD is not why the factory exists. The factory exists for one thing — relentless, creative, exhaustive quality hunting that runs for MONTHS on proven engines. Everything else in the factory serves that purpose. This is not a small adjustment. It changes the factory from a general-purpose autonomous development platform into a specialized quality weapon.

**2. The pipeline has TWO distinct phases, and the factory serves the gap between them.**

Phase 1 (excerpts at their right location): Source → Normalization → Excerpting → Taxonomy. This is the first complete product — a reader can open the library and find scholarly excerpts organized by topic. Phase 2 (what scholars say): Synthesis engine transforms organized excerpts into encyclopedic entries. The owner explicitly says: do NOT start Phase 2 until Phase 1 is "100% robust and bulletproof." The factory's primary mission is to GET Phase 1 to that standard.

**3. There is an explicit WIP/TESTED boundary that doesn't exist in the current architecture.**

The owner says the factory and manual engine-building should happen simultaneously without interfering. The factory hunts what's proven; the architect builds what's next. When a "testable part" of the WIP engine is complete, it crosses the boundary into factory scope. This requires a clean interface — probably a git tag or branch convention — that the roadmap currently lacks. This is a CRITICAL missing design element. Without it, the factory might run tests against half-built code and flood the findings queue with irrelevant failures, or worse, the factory's automated commits might conflict with the architect's manual work.

**4. Feature expansion (PDF sources, new formats) is a THIRD phase, after exhaustive testing.**

The owner's timeline: finish building → months of testing → expand. The factory serves ALL three phases but in different ways: during building it hunts what's done; during testing it's the primary activity; during expansion it validates new capabilities against the proven baseline. This is a maturity progression that the current roadmap doesn't model.

**5. The owner is NOT delegating quality judgment to the factory.**

"How that improvement will actually happen is an architectural decision that needs to be made by you, since you're in charge." The factory finds problems. The architect decides what to do about them. The factory does not auto-fix, does not auto-prioritize, does not make design decisions. This aligns with D-F020 (escalation protocol) but goes further — even the FIX mode's automated fix-review-verify cycle might be too autonomous for what the owner envisions. This needs explicit discussion.

### What the architect independently adds

**6. The roadmap has a BUILD-shaped hole that creates unnecessary complexity.**

Concretely: Session 6 (orchestrator) spends significant effort on work-unit decomposition and SPEC-to-task conversion. Session 3 (CLI setup) designs 4-agent BUILD team compositions. Session 4.5 (synthetic data) includes full-pipeline synthetic books that traverse all engines including ones that don't exist yet. If BUILD is not a primary mode, all of this becomes simpler. The orchestrator's mode priority becomes FIX > EVALUATE > HUNT > CROSS-ENGINE > BENCHMARK. The SPEC-to-task decomposition engine (listed as a custom-build item in the Paperclip evaluation) is no longer needed AT ALL. Team compositions shrink: HUNT (3 agents), FIX (3 agents), EVALUATE (2 agents) — no BUILD team needed.

**7. The "testable boundary" interface is the MOST important design decision in this revision.**

If this boundary is wrong, two failure modes occur:
- **Too permissive:** Factory tests half-built code → findings queue fills with noise → real bugs hide among false positives → the owner loses trust in the factory's output
- **Too restrictive:** Factory only tests fully-complete engines → months pass before the factory does anything useful → the taxonomy engine finishes before the factory has hunted excerpting

The right answer is probably granular: the architect tags specific engine PHASES as testable (e.g., "excerpting Phase 1 segmentation is testable, Phase 3 enrichment is not yet"), and the factory's hunt cycle respects those tags. But this needs careful design — it affects the synthetic data system (which phases to generate test data for), the findings classifier (which findings are real vs. expected-from-WIP), and the dashboard (which quality levels are meaningful).

**8. The source engine validation gap (Steps 3-4) becomes URGENT in this reframe.**

If the factory's primary job is exhaustive testing of the Phase 1 pipeline, and the source engine's LLM inference has only been tested on 13 fixtures, then the factory's very first hunt cycle on source engine output might discover that the foundation is broken. That's not a hunt finding — that's a "we built on sand" finding. Source Steps 3-4 should complete BEFORE the factory starts hunting, or at minimum, the factory's initial scope should exclude source engine LLM inference until Steps 3-4 validate it.

**9. PDF scan integration is a bigger project than it sounds, and it's an excellent factory test case.**

Adding PDF scans means: OCR integration (probably Tesseract or a cloud OCR API for Arabic), handling variable scan quality (some manuscripts are pristine, some are barely legible), detecting multi-column layouts common in Islamic manuscripts, handling marginal annotations (حاشية written in margins), and producing output that matches the same contracts.py schemas the Shamela path uses. This is genuinely hard — Arabic OCR accuracy is still significantly below Latin-script OCR, especially for classical texts with dense diacritics. But it's also the perfect first job for the factory's feature-expansion mode: the architect designs the extension, the factory tests it exhaustively against known-good Shamela output for the same books (ground truth already exists).

**10. The synthesis engine deferral is architecturally correct and the owner should feel good about it.**

Synthesis is where the highest-risk epistemic operations happen — flattening disagreements, confusing quotation with endorsement, hallucinating scholarly consensus. Building synthesis on an unproven pipeline would be building a confidence machine on top of uncertainty. The owner's instinct to defer synthesis until Phase 1 is bulletproof is exactly right. This also means the factory has months of meaningful work (hunting Phase 1) before synthesis is even on the table.

---

## Decisions Needed in This Session

### Decision 1: Factory Identity Reframe
Revise FACTORY_ROADMAP_v2.md to reflect: factory = quality guardian, not engine builder. Specifically:
- Remove or demote BUILD mode from primary operating mode
- Simplify Session 6 (no SPEC-to-task decomposition needed)
- Simplify Session 3 (no 4-agent BUILD team needed)
- Update AQS mode priorities and time allocations
- Update TEAM_ARCHITECTURE to remove BUILD team

### Decision 2: WIP/TESTED Boundary Design
How does the architect signal "this part of the engine is ready for factory testing"?
- Git tag convention? (`factory-scope-excerpting-v1`)
- Directory-level scope file? (`engines/excerpting/FACTORY_SCOPE.md`)
- Manifest entry? (ops_manifest.json tracks which engine phases are in scope)
- Something else?

### Decision 3: Source Engine Steps 3-4
When and how? Options A/B/C from the agenda file. The owner's reframe makes this more urgent: the factory can't hunt a foundation it hasn't validated.

### Decision 4: Factory Scope on Day 1
When the factory first starts running (after Session 7), what is in scope?
- Source engine deterministic processing (Step 2 already passed 2,519 books) — YES
- Source engine LLM inference — DEPENDS on Decision 3
- Normalization engine (420 tests, proven) — YES
- Excerpting engine (593+ tests, real LLM call succeeded) — PARTIALLY (which phases?)
- Taxonomy engine — NO (not built yet)

### Decision 5: Autonomy Level for FIX Mode
The owner says the architect decides how fixes happen. Current AQS design: factory auto-fixes, auto-reviews, auto-verifies. Owner's comment suggests: factory finds and logs, architect decides response. Which model?
- **Full autonomy:** Factory finds → fixes → reviews → verifies → logs (current AQS design)
- **Semi-autonomy:** Factory finds → classifies → proposes fix → architect approves → factory implements
- **Manual:** Factory finds → logs → architect reviews → architect directs CC to fix
- This might vary by severity: CRITICAL = architect reviews, MEDIUM = factory auto-fixes?

### Decision 6: Feature Expansion Architecture
Not urgent now, but scoping it early prevents drift. When the owner says "accept PDF scans":
- Does this mean a new source engine format path (extending `engines/source/`)?
- Or a new engine entirely?
- Does the factory test this, or is it manually built and tested like taxonomy?

### Decision 7: Interleaving Priority
When both tracks need the owner, what comes first? (Same as agenda Issue 3.)

### Decision 8: Paperclip Timeline
Same as agenda Issue 4. The factory reframe might change this — a quality-guardian factory needs less infrastructure than an engine-builder factory, potentially making Paperclip's dashboard-and-scheduling value proportionally larger.

---

## Session Protocol

1. Clone/pull repo
2. Read `reference/ROADMAP_DISCUSSION_AGENDA.md` (6 issues from the environment session)
3. Read this document in full (it extends the agenda with the owner's reframe)
4. `git log --oneline -10` (CC has been active — 3 new commits since environment session)
5. `ls /mnt/skills/user/` — pick relevant skills: thinking-frameworks, critical-review, factory-session
6. DRIFT CHECK: Does the factory reframe still serve the goal — a study companion where the owner reads an entry and sees what every scholar said?
7. Work through Decisions 1-8 in order
8. For each decision: multi-angle analysis (thinking-frameworks), then decide (not defer)
9. After all decisions: produce a revised FACTORY_ROADMAP_v3.md outline showing concrete changes
10. Update memory entries if any decisions change stored facts
