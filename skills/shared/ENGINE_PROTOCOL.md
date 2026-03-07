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

## Phase 6: BUILD + EVALUATE

**What you do:** Run Claude Code (or agent teams). Review test results with Claude Chat.
**What Claude Code does:** Implements the engine.
**What Claude Chat does:** Helps you interpret test results.
**Skills used:** `kr-evaluate` (in Claude Chat, after each build cycle).

This phase is a loop:

```
BUILD (Claude Code) → TEST (automated) → EVALUATE (Claude Chat) → FIX → repeat
```

1. **Build:** Run Claude Code on the engine. It reads CLAUDE.md and NEXT.md, implements code, runs tests.
2. **Test:** Automated tests run (deterministic checks, LLM quality checks, LLM evaluation).
3. **Evaluate:** Open Claude Chat. Upload or reference the test results. Say "use kr-evaluate." Claude categorizes every failure (engine bug? SPEC gap? data issue?) and helps you spot-check Arabic output.
4. **Fix:** Based on evaluation:
   - Engine bugs → Claude Code fixes them (next build cycle)
   - SPEC gaps → Back to Phase 2 (write a new comment, re-resolve)
   - Data issues → You provide a better test fixture
   - LLM quality issues → Claude Code adjusts prompts/models

**You're done with Phase 6 when:** The engine passes its inter-engine gate: output is trustworthy enough to feed the next engine. Then you start Phase 1 for the NEXT engine in the pipeline.

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
║  Phase 6: BUILD+EVAL    Claude Code builds, you evaluate  ║
║     ↓                   (kr-evaluate)                     ║
║     ↓                                                     ║
║  ✓ ENGINE DONE → Start Phase 1 for next engine            ║
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
