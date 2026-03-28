# Roadmap Discussion Agenda — قبل الانطلاق

**Purpose:** Resolve all open questions before executing the factory roadmap.
**For:** Next Claude Chat session where the owner discusses roadmap comments.

---

## Issue 1: Source Engine Status — Is It Really "Done"?

**Current claim:** Memory, factory roadmap, and all docs say "Source ✅"

**Actual state:**
- Code: COMPLETE (758 tests, engine.py built, all modules working)
- Deterministic validation (Step 2): COMPLETE (2,519/2,519 books, 0 errors)
- LLM inference validation: ONLY 13 FIXTURES TESTED
- Steps 3-4 from `engines/source/VALIDATION_PLAN.md` are PENDING:
  - Step 3: Targeted LLM probes on 25-30 books (€5-10)
  - Step 4: Final validation on ~200 books (€20-30)
- The plan explicitly says "There is no Step 5" and "Library population happens
  only after all engines are validated end-to-end"

**Why this matters:** The source engine's metadata extraction (author identification,
genre classification, school detection) uses LLM inference. If the LLM makes systematic
errors that only show up at scale, every downstream engine inherits those errors. This is
T-6 (Metadata Poisoning) at the foundation level.

**Decision needed:** When do Steps 3-4 happen?
- **Option A:** Complete them now (before/alongside excerpting). Cost: 2-3 sessions + €30-40.
  Pro: validates the foundation before building on it.
- **Option B:** Defer to after factory is operational. The factory's hunt system would catch
  source engine bugs. Con: hunting tests model capabilities generically, not the source
  engine's specific prompts and consensus logic.
- **Option C:** Let the factory's benchmark (Session 4-5) partially cover this, then run
  source Steps 3-4 as a factory work unit. Hybrid approach.

**Also:** The `source_engine_roadmap.jsx` project file is stale — it shows a Step 5 "Full
Collection" that the governing VALIDATION_PLAN.md explicitly removed.

---

## Issue 2: Owner's Roadmap Comments

The owner said they have comments on the roadmap. These should be discussed and resolved
in this session. The architect investigates each comment independently (the owner is a
student, not yet a scholar — comments are hypotheses, not instructions).

**Preparation:** The owner should bring their specific comments. The architect should have
`reference/FACTORY_ROADMAP_v2.md` open for reference.

---

## Issue 3: Interleaving Excerpting and Factory Work

The execution plan has two parallel tracks. But the owner is the bottleneck for both:
- Engine track: owner reviews Arabic excerpts (30-book probe = 6 review sessions)
- Factory track: owner sets up WSL2, runs factory_start.py, resolves human gates

**Decision needed:** What's the priority when both tracks need the owner?
- Excerpting review sessions are the non-negotiable owner review gate
- Factory setup is one-time effort (~2-4 hours)
- Once the factory is running, it reduces owner involvement (automated hunting)

**Suggested priority:** WSL2 setup first (one-time, unblocks everything), then excerpting
review sessions take priority, factory sessions fill the gaps.

---

## Issue 4: Paperclip Decision Timeline

Current verdict: EVALUATE_FURTHER. The execution plan defers Paperclip re-evaluation to
Session 8 (dashboard). But if we're going to adopt Paperclip, knowing sooner would save
designing custom components in Sessions 6-7 that Paperclip replaces.

**Decision needed:** When to re-test Paperclip on WSL2?
- **Option A:** Test in Session 3 (alongside CLI setup). If it works on WSL2, revise
  Sessions 6-8 to integrate it. Risk: project is only ~1 month old.
- **Option B:** Defer to Session 8 as planned. Build standalone, integrate later.
  Safer but potentially wastes custom work.
- **Option C:** Quick WSL2 smoke test NOW (just Arabic encoding + basic task execution,
  30 minutes). If it passes, schedule full evaluation in Session 3.

---

## Issue 5: Stale Documents (Confirms Session 1 Scope)

Found during this session's audit:
- `CLAUDE.md` lines 9, 71, 75: references "7-engine pipeline" and "7 test sources"
- `reference/AGENT_ARCHITECTURE.md` lines 58, 61: references "7 engines"
- `source_engine_roadmap.jsx` project file: shows Step 5 that doesn't exist
- Source engine described as ✅ when Steps 3-4 are pending

Factory Session 1 is designed to fix CLAUDE.md and AGENT_ARCHITECTURE.md. The project file
update and source engine status are additional items to resolve.

---

## Issue 6: Model Role Research Sequencing

NEXT.md Task 1 (model role research for excerpting) and the factory benchmark (Session 4-5)
both involve comparing frontier model capabilities on Arabic scholarly tasks. There's overlap:

- NEXT.md asks: which model (Opus/GPT-5.4/Gemini 3.1) is best for verify/escalation roles?
- Benchmark asks: which model scores highest on 12 Arabic scholarly tasks?

**Decision needed:** Should model role research (NEXT.md Task 1) inform the benchmark design,
or should they be independent?
- If informed: do Task 1 first (engine track), use findings to design benchmark
- If independent: run them in parallel, cross-reference results later

---

## Checklist for Closing the Discussion

Before ending the roadmap discussion session, verify:
- [ ] Source engine status resolved (Option A, B, or C)
- [ ] Owner's roadmap comments all addressed
- [ ] Interleaving priority decided
- [ ] Paperclip timeline decided
- [ ] Model role research sequencing decided
- [ ] Any memory entries that need updating from decisions made
- [ ] Clear next action: which track starts first, which session, who does what
