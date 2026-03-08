# Engine Protocol — المسار لكل محرك

This is YOUR guide. Follow it top to bottom for each engine. Don't skip phases. Don't mix phases.

Each engine goes through 6 phases. You are always in exactly ONE phase. If you're unsure which phase you're in, something went wrong — go back to the last phase you completed.

---

## Phase 1: READ THE SPEC

**What you do:** Read the engine SPEC. Write numbered comments.
**What Claude does:** Nothing yet. This is your solo reading time.
**Skill used:** None.

Read the SPEC section by section. For anything that confuses you, surprises you, seems wrong, or triggers a domain insight, write a comment. Use this format:

```
## Comment #1
Section: §4.A.2
SPEC text: "The source engine identifies the author from the info.html file"
Observation: In many classical texts, the author field in Shamela contains 
the muhaqiq (editor), not the original author. This would misattribute the work.
Direction: Maybe check against a known-authors list?
```

Save all comments in a file. Commit to the repo as `engines/{engine}/owner-comments.md`.

**You're done with Phase 1 when:** You've read the entire SPEC and written all your comments. You don't need to comment on everything — only things that trigger a reaction. Zero comments is fine if the SPEC is solid, but unlikely for a first read.

---

## Phase 2: COMMENT RESOLUTION

**What you do:** Give Claude your comments, one or a few at a time.
**What Claude does:** Investigates each comment, forms a position, proposes SPEC changes.
**Skill used:** `kr-spec-review` — say "use kr-spec-review for comment #1" or "handle comments #3-5."

This is where the real work happens. For each comment:
1. You give Claude the comment
2. Claude researches it (web searches, cross-references, feasibility checks)
3. Claude forms its OWN position — it may agree, disagree, or partially agree
4. Claude proposes a specific SPEC change (or explains why no change is needed)
5. **You decide.** Accept, reject, or discuss further.

**Important rules:**
- Do comments in batches of 3-5 per chat. Don't try to do 20 in one chat.
- If a chat gets long (30+ turns or things start feeling sluggish), tell Claude: "Let's handoff." It will produce a summary. Start a fresh chat.
- If Claude disagrees with your comment, listen. It may be right about the technical implications. But if it's wrong about the domain (Islamic studies), push back — you're the authority there.
- Track status: each comment is either **Resolved** (SPEC change accepted), **Rejected** (no change needed), or **Open** (needs more discussion).

**You're done with Phase 2 when:** Every comment is either Resolved or Rejected. No Open items remain.

---

## Phase 3: DEEP AUDIT

**What you do:** Ask Claude to audit the SPEC for things you COULDN'T catch as a domain reader.
**What Claude does:** Runs the full quality gauntlet on the SPEC.
**Skill used:** `kr-integrity` — say "use kr-integrity to audit §4" or "audit the full SPEC."

This catches what your domain reading missed: ambiguous sentences that would confuse a builder, missing error handling, contradictions between sections, silent failure patterns, threats to knowledge integrity. You couldn't catch these because they're technical — Claude can.

The audit is done in chunks (one major SPEC section per chat) to avoid context overload:
- Chat 1: Audit §1-§3 (Purpose, Input, Output — the contracts)
- Chat 2: Audit §4 (Processing — usually the longest section)
- Chat 3: Audit §5-§7 (Validation, Consensus, Errors)
- Chat 4: Audit §8-§10 (Config, State, Tests)

Each audit chat produces a defect list with exact fixes. You review the fixes — most will be technical improvements you can accept. Some may touch domain content, where you weigh in.

**You're done with Phase 3 when:** All defect fixes are accepted or rejected. The SPEC has no known quality issues.

---

## Phase 4: FINALIZE

**What you do:** Tell Claude to assemble the final SPEC.
**What Claude does:** Applies all changes, checks consistency, produces the complete updated document.
**Skill used:** `kr-finalize` — say "use kr-finalize" or "finalize the SPEC."

This is assembly, not new work. Claude:
1. Collects every resolved comment change and every audit fix
2. Checks for interactions between changes (does fix #3 break fix #7?)
3. Checks cross-engine consistency (does the output contract still match the next engine's input?)
4. Produces the COMPLETE updated SPEC text — the authoritative version
5. Runs the "anti-secretary test": did the SPEC get RICHER, not just cleaner?

You review the final SPEC. If something looks off, you're back in Phase 2 (write a new comment). Otherwise, commit it.

**You're done with Phase 4 when:** The final SPEC is committed to the repo. This is the document Claude Code will build from.

---

## Phase 5: BUILD PREP

**What you do:** Tell Claude to prepare everything Claude Code needs.
**What Claude does:** Technology survey, architecture design, stubs, test infrastructure, CLAUDE.md.
**Skill used:** `kr-build-prep` — say "use kr-build-prep" or "prepare for building."

This is the bridge from Claude Chat (design) to Claude Code (implementation). Claude:
1. Surveys available tools and libraries (what to use vs. what to build)
2. Designs the module architecture
3. Writes stub files (function signatures with types and docstrings, no bodies)
4. Sets up test infrastructure (deterministic checks, LLM evaluation prompts)
5. Writes a CLAUDE.md under 200 lines for Claude Code to read
6. Writes the first NEXT.md (narrow scope: one format, one fixture)
7. Optionally: defines agent team templates for the build phase

After this, you switch from Claude Chat to Claude Code. You don't need to understand the technical deliverables — they're for Claude Code, not for you.

**You're done with Phase 5 when:** The build prep deliverables are committed to the repo. Claude Code can start building.

---

## Phase 6: BUILD, TEST, EVALUATE

This is not building the application. This is building a **testable engine** and then **extensively testing it.** The engine is built as a CLI that can be run on real sources and produce inspectable output at every stage. The goal is to reach trust — proof that this engine's output is reliable enough to feed the next engine.

**What Claude Code does:** Builds the engine as a testable CLI, runs it on real sources, runs all three test dimensions, stores results.
**What you do:** Review test results with Claude Chat. Spot-check Arabic output.
**Skill used:** `kr-evaluate` (in Claude Chat) — say "use kr-evaluate on these results."

### The Three Test Dimensions

Every engine is tested along three dimensions. They test DIFFERENT things:

**5a — Deterministic checks (automated, no LLM needed)**
Binary pass/fail tests that any computer can verify:
- Does the output match the schema? (every field present, correct types)
- Is the Arabic text preserved exactly? (diacritics, characters, no corruption)
- Is metadata complete? (no missing required fields)
- Is upstream metadata passed through? (D-023 — nothing lost)
- Do all IDs resolve? (no broken references)

A 5a failure is always a bug. No ambiguity.

**5b — LLM-as-worker (tests the LLMs INSIDE the engine)**
The engine uses LLMs internally for tasks like classifying a book's science, identifying the author, or detecting text layers. 5b tests whether those internal LLM calls get their tasks right:
- Did the source engine's LLM correctly classify this book as نحو?
- Did it correctly identify ابن عقيل as the author, not the muhaqiq?
- Did it correctly detect that this is a sharh on a matn?

A 5b failure means the engine's LLM prompts, model choice, or task design needs work.

**5c — LLM-as-evaluator (INDEPENDENT review of the engine's output)**
A DIFFERENT model reviews the engine's complete output and judges whether it's correct. This is like checking your own homework — by having someone else check it:
- Give a different model the frozen source + the engine's metadata and ask: "Is this metadata correct?"
- Give it the extracted passages and ask: "Are these complete, coherent text units?"
- Track: what errors does this independent review catch that self-validation missed?

A 5c finding tells you whether LLM-based quality gates are worth adding to the production pipeline. By the time you've tested 3-4 engines, you'll have data to decide.

### The Build-Test-Evaluate Loop

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│  Claude Code BUILDS the engine                      │
│     ↓                                               │
│  Claude Code RUNS it on real sources (your fixtures) │
│     ↓                                               │
│  Claude Code runs all THREE test dimensions          │
│     ↓                                               │
│  Test results are STORED in files                    │
│  (so Claude Chat can read and evaluate them)         │
│     ↓                                               │
│  You open Claude Chat                                │
│  "use kr-evaluate on these test results"             │
│     ↓                                               │
│  Claude Chat categorizes every failure:              │
│     • Engine bug → Claude Code fixes it              │
│     • SPEC gap → back to Phase 2 (new comment)       │
│     • Data issue → you provide better fixture        │
│     • LLM quality → Claude Code adjusts prompts      │
│     • Evaluator noise → dismiss (tune evaluator)     │
│     • Upstream error → fix the previous engine first  │
│     ↓                                               │
│  You spot-check Arabic output where Claude asks      │
│  (specific questions, not "does this look right?")   │
│     ↓                                               │
│  Fix issues → loop back to BUILD                     │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Why Test Results Must Be Stored

Claude Code and Claude Chat are separate tools with separate context windows. Claude Code can't hand its results directly to Claude Chat. The bridge is FILES:

- Claude Code writes test results to `engines/{engine}/test-results/`
- Each test run produces a structured report (what passed, what failed, what was flagged)
- You open Claude Chat and point it at the results: "evaluate the test results in engines/source/test-results/"
- Claude Chat reads them and applies the kr-evaluate analysis

This separation is by design. Claude Code is good at running tests and fixing code. Claude Chat (with you) is good at interpreting results, making judgment calls on Arabic content, and deciding whether a SPEC gap needs revisiting.

### Trust Graduation

The engine isn't "done" when it runs. It's done when it's TRUSTED:

```
Level 0: Engine runs without crashing on test fixtures
Level 1: All 5a deterministic checks pass
Level 2: 5b LLM-worker checks show >90% accuracy
Level 3: 5c LLM-evaluator review doesn't find errors self-validation missed
Level 4: You (the owner) approve the output for your actual sources
```

**You're done with Phase 6 when:** The engine reaches at least Level 2, and you've approved its output on your real sources. Then you start Phase 1 for the NEXT engine in the pipeline.

---

## The Full Picture

```
╔═══════════════════════════════════════════════════════════╗
║                    PER ENGINE CYCLE                       ║
╠═══════════════════════════════════════════════════════════╣
║                                                           ║
║  Phase 1: READ          You read the SPEC, write comments ║
║     ↓                                                     ║
║  Phase 2: RESOLVE       Claude investigates your comments ║
║     ↓                   (kr-spec-review)                  ║
║     ↓                                                     ║
║  Phase 3: AUDIT         Claude finds technical defects    ║
║     ↓                   (kr-integrity)                    ║
║     ↓                                                     ║
║  Phase 4: FINALIZE      Claude assembles final SPEC       ║
║     ↓                   (kr-finalize)                     ║
║     ↓                                                     ║
║  Phase 5: BUILD PREP    Claude prepares for Claude Code   ║
║     ↓                   (kr-build-prep)                   ║
║     ↓                                                     ║
║  Phase 6: BUILD, TEST, EVALUATE                           ║
║     ↓  Claude Code builds a testable engine               ║
║     ↓  Claude Code runs it on real sources                ║
║     ↓  Claude Code runs 3 test dimensions:                ║
║     ↓    5a: deterministic (schema, text, metadata)       ║
║     ↓    5b: LLM-as-worker (engine's own LLM calls)      ║
║     ↓    5c: LLM-as-evaluator (independent review)       ║
║     ↓  Test results stored in files                       ║
║     ↓  You + Claude Chat evaluate results (kr-evaluate)   ║
║     ↓  Fix → re-run → re-evaluate until TRUSTED           ║
║     ↓                                                     ║
║  ✓ ENGINE TRUSTED → Start Phase 1 for next engine         ║
║                                                           ║
╚═══════════════════════════════════════════════════════════╝
```

**Engine order (following the pipeline):**
1. Source engine (محرك المصادر) ← you are here
2. Normalization engine (محرك التسوية)
3. Passaging engine (محرك التقطيع)
4. Atomization engine (محرك التذرية)
5. Excerpting engine (محرك الاستخراج)
6. Taxonomy engine (محرك التصنيف)
7. Synthesis engine (محرك التركيب)

---

## Where Does kr-research Fit?

`kr-research` is not a phase — it's a tool you can invoke DURING Phase 2, 3, or 5 when Claude needs to explore something deeply. Examples:
- During Phase 2: your comment raises a question about how other digital projects handle X → "use kr-research to explore how OpenITI handles multi-edition works"
- During Phase 3: the audit reveals a design weakness → "use kr-research to find a better approach"
- During Phase 5: the technology survey needs deeper exploration → Claude invokes it automatically

You don't schedule kr-research. It happens when the work demands it.

---

## Rules That Prevent Chaos

1. **One engine at a time.** Don't start the normalization engine until the source engine passes Phase 6.
2. **One phase at a time.** Don't jump to Phase 4 while Phase 2 comments are still Open.
3. **Fresh chats between phases.** Start Phase 3 in a new chat, not at the tail end of a Phase 2 chat.
4. **Fresh chats within long phases.** If Phase 2 takes 5 chats, that's fine. Handoff between them.
5. **Always invoke skills by name.** Say "use kr-spec-review" not "handle my comment." Auto-triggering is unreliable.
6. **When in doubt, tell Claude which phase you're in.** "I'm in Phase 2, comment resolution. Here's comment #4."
7. **If you discover a SPEC problem during Phase 6 (building), go back to Phase 2.** Write a new comment, resolve it, re-audit that section, re-finalize. Don't patch the SPEC informally.
