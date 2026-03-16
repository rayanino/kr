# Open Problems — المشاكل المفتوحة

Last updated: 2026-03-08 (v5 — shared components, mature SPECs, contract sync, engine-specific guidance)

## The Principle

**Depth over breadth. Reliability over features. Every block proven before building on it.**

Validate the pipeline shape first with a tracer bullet. Then build a narrow pipeline that works, one engine at a time. Then expand it.

---

## Where You Are

Source engine Steps 0–2 complete. Step 3 (build prep) is next. The SPEC is hardened and all LLM assumptions are validated. Ready to prepare for the build phase.

---

## What You Should Do RIGHT NOW

### Step 3: Build Prep (1 session, Claude Chat)

In the source engine project: "Use kr-build-prep."

This session produces the architecture doc, technology inventory, shared component requirements, 6 session plans, and updated CLAUDE.md. See `NEXT.md` for full scope.

### Then: Build (6 sessions, Claude Code)

Claude Code executes the session plans, building the source engine one pipeline step at a time. Each session ends with committed, tested code.

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
| Setup (capabilities, skills, project) | DONE | |
| API keys (.env file) | DONE | |
| **Step 0: Tracer bullet** | DONE | Contract boundaries validated |
| **Source engine** | | |
| Step 1: SPEC core architecture | DONE | 8+ review passes, kr-integrity audit |
| Step 2: Research assumptions | DONE | All 5 assumptions tested. See `engines/source/review/STEP2_EVALUATION.md` |
| Step 3: Build prep | **ACTIVE** | Technology survey, session plans, shared component requirements |
| Step 3: Build (incl. shared components) | BLOCKED | Waiting on build prep |
| Step 4: Test + prove + gold baselines | BLOCKED | Waiting on build |
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
| Nahw science tree sanity check | Taxonomy engine Step 3 | Architect generates the tree via multi-source AI research; owner validates "does this match how I learned nahw?" |
| Experiential sanity check (source engine) | Source engine Step 4 | "Is this the right book? Right author? Does the text look right?" — 10-15 minutes |
| Experiential sanity check (synthesis engine) | Synthesis engine Step 4 | "Does this entry seem useful for study? Does it make sense?" — 10-15 minutes |
| Sanity check (other engines) | Each engine's Step 4 | Light review — flag anything that looks obviously wrong. "I'm not sure" is valid. |
| Gold baseline verification | Each engine's Step 4 | Owner spot-checks recognizable fields, automated verification handles scholarly precision |

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
| Step 0: Tracer bullet — contract reconciliation, shared component stubs | 2026-03-09 |
| Step 1: SPEC hardening — 8 review passes, integrity audit, core extraction | 2026-03-09 |
| Step 2: LLM assumption testing — A1-A5 validated across 5 production models | 2026-03-09 |
| Step 2 evaluation — 5 binding decisions, ASSUMPTION markers resolved | 2026-03-09 |

---

## Open Research Problems

### Compiler Detection (Source Engine)

**Problem:** Shamela may list classical source authors in `author_name_raw` while placing the actual compiler/arranger in `muhaqiq_name_raw`. The pipeline treats muhaqiq as an editor, not as a potential author, so it misattributes compiled works. Confirmed in ERR-02 (السراج المنير: compiler عصام موسى هادي listed as muhaqiq, classical authors السيوطي and الألباني listed as authors).

**Potential approach:** Add a detection heuristic — when muhaqiq is contemporary (no death date or recent) but listed authors are classical (death date > 200 years ago), flag as potential compilation rather than tahqiq. Requires a new LLM inference step to distinguish muhaqiq-as-editor from muhaqiq-as-compiler.

**Status:** Documented in SPEC_CORE.md. No code fix planned — requires design work for a "compiler" role concept.

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
