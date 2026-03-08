# Open Problems — المشاكل المفتوحة

Last updated: 2026-03-08 (v5 — shared components, mature SPECs, contract sync, engine-specific guidance)

## The Principle

**Depth over breadth. Reliability over features. Every block proven before building on it.**

Validate the pipeline shape first with a tracer bullet. Then build a narrow pipeline that works, one engine at a time. Then expand it.

---

## Where You Are

Pre-engine. You need to complete setup, then run the tracer bullet (Step 0) before starting the source engine.

---

## What You Should Do RIGHT NOW

### 1. Setup (15 minutes, one time)

**Enable capabilities:**
- Settings > Capabilities > Enable **Code execution and file creation**

**Upload skills:**
- Customize > Skills > Upload all 6 `.zip` files from `skills/` > Toggle ON
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

### 2. Tracer Bullet (Step 0)

Before deepening any engine, validate that data can flow through all 7 engines end-to-end. This is 3-5 sessions that prevent weeks of rework from contract mismatches.

All 7 engines already have SPECs and contracts.py files. The tracer bullet reconciles them (fixing mismatches between adjacent contracts), stubs the shared components (consensus, human_gate, scholar_authority, validation), builds rough engine stubs, and runs one Shamela HTML file through the full pipeline.

In the source engine project: "We need to run Step 0 from ENGINE_PROTOCOL.md — the tracer bullet. Reconcile the existing 7 contracts.py files, stub the shared components, build engine stubs, and run html_export_minimal through the full pipeline."

Output is documented in `reference/TRACER_FINDINGS.md`.

### 3. Source Engine Step 1: Classify Core vs Deferred

After the tracer bullet: "Use kr-core-extract on the source engine SPEC. Classify core vs deferred."

Claude reads the full SPEC and produces a classification table — every capability tagged CORE or DEFERRED with extension hooks. Review this table and correct any misclassifications. Then Claude rewrites the SPEC focused on core only.

### 4. Read the Core SPEC and Write Comments

Read the rewritten SPEC. Focus on core behavior.

As you read, write comments about the CORE behavior:
- Things that are wrong ("Shamela puts the muhaqiq in the author field, not the author")
- Things that are confusing ("I don't understand what trust evaluation means here")
- Things that are missing ("What about books with multiple authors?")
- Things that surprise you ("Why does it need an LLM for this?")

Use the template in `skills/shared/COMMENT_TEMPLATE.md`. Save as `engines/source/owner-comments.md`.

### 5. Resolve Comments

In the source engine project, say: "I have comments on the core SPEC. Use kr-spec-review."

Give Claude your comments in batches of 3-5. Claude will research each one deeply and propose SPEC changes. You decide.

---

## The Full Process (Per Engine)

See `skills/shared/ENGINE_PROTOCOL.md` for the complete process. Summary:

```
Step 0: TRACER BULLET — Validate all 7 contract boundaries (one time)
Step 1: SPEC          — Define core architecture at architecture-decision depth
Step 2: RESEARCH      — Test every assumption before building
Step 3: BUILD         — Turn SPEC into code (deepening the tracer bullet stub)
Step 4: TEST          — Prove reliability, create gold baselines, document lessons
```

Steps 1-4 repeat for all 7 engines in pipeline order. After every 2 engines, a lessons backward review. After all 7: v0.0.1 — a narrow, reliable pipeline.

**Create each engine's Claude.ai project when you start that engine's Step 1, not all upfront.** Use the matching template from `skills/engine-project-template/`. Sync knowledge files from GitHub.

---

## Status

| Item | Status | Notes |
|------|--------|-------|
| Setup (capabilities, skills, project) | TODO | Owner action, 15 minutes |
| API keys (.env file) | TODO | Owner action, needed for Step 2 |
| **Step 0: Tracer bullet** | TODO | 3-5 sessions, reconcile contracts, stub shared components |
| **Source engine** | | |
| Step 1: SPEC core architecture | TODO | After tracer bullet. Heavy domain review needed. |
| Step 2: Research assumptions | TODO | After SPEC passes kr-integrity |
| Step 3: Build (incl. shared components) | TODO | Builds consensus, human_gate, scholar_authority, validation |
| Step 4: Test + prove + gold baselines | TODO | Owner reviews Arabic output. Gold baselines created here. |
| **Normalization engine** | BLOCKED | Waiting on source engine |
| Lessons backward review | BLOCKED | After normalization Step 4 |
| **Passaging engine** | BLOCKED | 25 HIGH-severity SPEC defects — needs substantive Step 1 work |
| **Atomization engine** | BLOCKED | Critical Step 2 research — LLM classification accuracy |
| Lessons backward review | BLOCKED | After atomization Step 4 |
| **Excerpting engine** | BLOCKED | Highest-risk LLM task (self-containment) |
| **Taxonomy engine** | BLOCKED | **Prereq:** Owner validates nahw science tree |
| Lessons backward review | BLOCKED | After taxonomy Step 4 |
| **Synthesis engine** | BLOCKED | Needs entry viewer script for Step 4 |

### Owner Deliverables (non-code, blocks specific engines)
| Item | Blocks | Notes |
|------|--------|-------|
| Nahw science tree validation | Taxonomy engine Step 3 | A tree exists at library/sciences/nahw/tree.yaml — owner must validate it matches his study structure |
| Domain comments (source engine) | Source engine Step 1 | Heavy review — how Shamela works, metadata conventions, author identification |
| Domain comments (synthesis engine) | Synthesis engine Step 1 | Heavy review — what makes a good entry, scholarly narrative expectations |
| Domain comments (other engines) | Each engine's Step 1 | Light review — flag anything surprising, Claude proceeds after 3 days |
| Gold baseline verification | Each engine's Step 4 | Owner spot-checks engine output for correctness, Claude produces the JSON |

### Completed
| Item | Date |
|------|------|
| Testing framework design | 2026-03-08 |
| Engine protocol rewrite (core-first) | 2026-03-08 |
| Protocol evaluation + fixes (tracer bullet, iterative depth, extension hooks) | 2026-03-08 |
| Deep analysis + corrections (shared components, mature SPECs, contract sync) | 2026-03-08 |
| Repo audit round 1: archive 6 obsolete root protocols, fix stale references | 2026-03-08 |
| Repo audit round 2: archive old engine artifacts, handoffs, premature files | 2026-03-08 |
| Meta-audit: apply kr-integrity lenses to ENGINE_PROTOCOL, fix 10 HIGH defects | 2026-03-08 |
| Rewrite all 7 engine CLAUDE.md files for current protocol | 2026-03-08 |

---

## Files That Matter

**Your daily files:**
- `OPEN_PROBLEMS.md` — this file, your roadmap
- `skills/shared/ENGINE_PROTOCOL.md` — the process (Step 0 + 4-step per engine)
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
