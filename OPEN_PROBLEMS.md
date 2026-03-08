# Open Problems — المشاكل المفتوحة

Last updated: 2026-03-08 (v3 — core-first rewrite)

## The Principle

**Depth over breadth. Reliability over features. Every block proven before building on it.**

Build a narrow pipeline that works. Then expand it. Not: build a wide engine that handles everything, then discover the architecture is wrong.

---

## Where You Are

The source engine. Step 1 (SPEC — Core Architecture). You need to read the core sections of the SPEC and write your domain comments.

---

## What You Should Do RIGHT NOW

### 1. Setup (15 minutes, one time)

**Enable capabilities:**
- Settings > Capabilities > Enable **Code execution and file creation**

**Upload skills:**
- Customize > Skills > Upload all 5 `.zip` files from `skills/` > Toggle ON
- Test: in any chat, say "use kr-research" — if it activates, skills work

**Create the source engine project:**
1. Create a new project: "Source Engine — محرك المصادر"
2. Add knowledge from GitHub (`rayanino/kr`):
   - `engines/source/`, `STEERING.md`, `KNOWLEDGE_INTEGRITY.md`, `SILENT_FAILURES.md`
   - `reference/DOMAIN.md`, `reference/ENTRY_EXAMPLE.md`, `reference/DEEP_REASONING_PROTOCOL.md`
   - `skills/shared/`, `NEXT.md`
3. Paste custom instructions from `skills/engine-project-template/source.md`
4. Keep `Github_key` as fallback knowledge

**Set up API keys:**
- Copy `.env.template` to `.env`
- Fill in: `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `MISTRAL_API_KEY`
- Needed for Step 2 (research/testing LLM assumptions)

### 2. Classify Core vs Deferred

Start a chat in the source engine project: "Use kr-core-extract on the source engine SPEC. Classify core vs deferred."

Claude reads the full SPEC and produces a classification table — every capability tagged CORE or DEFERRED with reasons. Review this table and correct any misclassifications. Then Claude rewrites the SPEC with exhaustive depth on core only.

### 3. Read the Core SPEC and Write Comments

Read the rewritten SPEC. Focus on core behavior.

As you read, write comments about the CORE behavior:
- Things that are wrong ("Shamela puts the muhaqiq in the author field, not the author")
- Things that are confusing ("I don't understand what trust evaluation means here")
- Things that are missing ("What about books with multiple authors?")
- Things that surprise you ("Why does it need an LLM for this?")

Use the template in `skills/shared/COMMENT_TEMPLATE.md`. Save as `engines/source/owner-comments.md`.

### 4. Resolve Comments

In the source engine project, say: "I have comments on the core SPEC. Use kr-spec-review."

Give Claude your comments in batches of 3-5. Claude will research each one deeply and propose SPEC changes. You decide.

---

## The Full Process (Per Engine)

See `skills/shared/ENGINE_PROTOCOL.md` for the complete process. Summary:

```
Step 1: SPEC    — Define core architecture in exhaustive detail
Step 2: RESEARCH — Test every assumption before building
Step 3: BUILD   — Turn SPEC into code
Step 4: TEST    — Prove reliability, document lessons
```

Do this for all 7 engines in pipeline order. After all 7: v0.0.1 — a narrow, reliable pipeline.

---

## Status

| Item | Status | Notes |
|------|--------|-------|
| Setup (capabilities, skills, project) | TODO | Owner action, 15 minutes |
| API keys (.env file) | TODO | Owner action, needed for Step 2 |
| **Source engine** | | |
| Step 1: SPEC core architecture | TODO | Read §1-§4.A, write comments |
| Step 2: Research assumptions | TODO | After SPEC is finalized |
| Step 3: Build | TODO | After research validates design |
| Step 4: Test + prove | TODO | After build |
| **Normalization engine** | BLOCKED | Waiting on source engine |
| **Passaging engine** | BLOCKED | Waiting on normalization |
| **Atomization engine** | BLOCKED | Waiting on passaging |
| **Excerpting engine** | BLOCKED | Waiting on atomization |
| **Taxonomy engine** | BLOCKED | Waiting on excerpting |
| **Synthesis engine** | BLOCKED | Waiting on taxonomy |

### Completed
| Item | Date |
|------|------|
| Testing framework design | 2026-03-08 |
| Repo cleanup | 2026-03-08 |
| Engine protocol rewrite (core-first) | 2026-03-08 |

---

## Files That Matter

**Your daily files:**
- `OPEN_PROBLEMS.md` — this file, your roadmap
- `skills/shared/ENGINE_PROTOCOL.md` — the 4-step process per engine
- `engines/source/SPEC.md` — the source engine specification

**For the source engine project:**
- `STEERING.md` — project overview
- `KNOWLEDGE_INTEGRITY.md` — corruption threats
- `SILENT_FAILURES.md` — silent failure patterns
- `reference/DOMAIN.md` — Islamic studies domain
- `reference/ENTRY_EXAMPLE.md` — target output quality
- `reference/DEEP_REASONING_PROTOCOL.md` — quality standard
- `reference/TESTING_FRAMEWORK.md` — testing architecture

**Everything else** is either archived, deferred to Stage 2, or infrastructure that Claude reads on demand.
