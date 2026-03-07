# Honest Plan: SPECs → Trusted Pipeline

**Date:** 2026-03-07
**Author:** External review (not the autonomous prep sessions)
**Replaces:** POST_PREP_PLAN.md (partially), supersedes NEXT.md directive

---

## What I Found

After cloning the repo and reading everything, here is the honest state:

**What exists and is good:**
- 7 engine SPECs, 500–2000 lines each, with concrete Arabic examples, error codes, edge cases
- 6 shared component SPECs (368–462 lines), drafted but unrefined
- 2 engines (passaging, atomization) went through full CREATIVE → PRECISION → HARDENING → IMPL_PREP
- 7 diverse test fixtures (PDF, DOC, HTML, TXT, JPG) — real source data
- Pydantic contracts for all 7 engines
- 42 architectural decisions documented and cross-referenced
- Cross-SPEC boundary consistency verified across all 14 components
- An experiment script (experiment1) already drafted

**What does not exist:**
- Zero lines of running code. Every `src/` file is a stub with docstrings.
- No gold baselines (hand-verified expected outputs)
- No CLI tool — nothing can be run
- No validation experiments completed
- No API keys configured
- The 5 remaining engines (source, normalization, excerpting, taxonomy, synthesis) have NOT been through domain review with the owner

**What went wrong:**
- The autonomous sessions over-optimized on SPEC quality and under-invested in building. Passaging and atomization are polished to an extreme degree (1000+ lines, 38 test cases specified), but they can't run.
- NEXT.md was pointing to implementing atomization — the 4th engine in pipeline order — skipping source and normalization entirely. You can't test atomization without something feeding it.
- The refinement cycle (4 sessions × 7 engines = 28+ sessions) would take months before a single line of code runs. Two engines consumed ~8 sessions of refinement alone.
- The shared components (consensus, human_gate, validation) have draft SPECs but the engines that DEPEND on them are being sent to implementation. The consensus module is referenced by every LLM-dependent engine, but has no contracts.py and no refinement.

---

## Critical Assessment of Existing Plans

### POST_PREP_PLAN.md
**Good:** Identifies the right experiments (LLM evaluation, synthesis quality, Arabic tokenization, multi-layer detection, RAGAS faithfulness). Correctly says "run experiments, not more planning."
**Bad:** Written in a single session that kept second-guessing itself. The experiments are described but not prioritized — experiments 1 and 2 are existential (if they fail, the entire approach changes), while 3 and 5 are informational (nice to know, won't change the plan). The phase structure (PREP → VALIDATE → BUILD+TEST → SCALE → APPLICATION) is correct at a high level but has no concrete dates, no dependencies, and Phase 3 just says "incremental."

### JUDGE_PANEL_ARCHITECTURE.md
**Good:** The three-tier evaluation design (deterministic → cheap LLM → expert panel) is well-supported by research. Cost model is reasonable.
**Bad:** It's theoretical. The rubric prompts are untested. The cost estimates assume English tokenization. The "autonomous fix loop" section copies the C compiler pattern without adapting it to KR's specific constraints (KR processes one source through 7 engines, not independent compilation units). Most importantly: it should not be built as a system upfront. It should emerge from testing each engine.

### MILESTONES.md
**Good:** Milestone 1 (source + normalization) and Milestone 2 (passaging → excerpting) are well-decomposed into atomic tasks.
**Bad:** Milestones 3–6 are placeholders. The task decomposition for M1 and M2 was written without running code — the tasks may not decompose correctly once implementation starts. Building engines in strict pipeline order makes sense, but the current NEXT.md contradicts this by jumping to atomization.

### SPEC_REFINEMENT.md
**The refinement tracking is broken.** The refinement_status.py script says 0 cycles for all engines, but the SESSION_LOG clearly shows passaging and atomization went through 4+ sessions. The status tracking doesn't match reality.

---

## The Plan

### Principle: Build → Test → Learn → Fix, not Specify → Specify → Specify → Build

The project's SPECs are good enough to build from. Not perfect — but the remaining imperfections are the kind you discover BY building, not by reading. The 5 un-refined engines (source, normalization, excerpting, taxonomy, synthesis) each have 500–2000 line SPECs with examples, error codes, and edge cases. That's more specification than most production systems ever get.

The owner's domain review is valuable and should happen — but as a focused, one-session review per engine, not a 4-session refinement cycle.

### No Standalone Experiments — Validation is Per-Engine

The previous plan (POST_PREP_PLAN.md) proposed 5 standalone experiments before building anything. Drop them. The research already answers the general questions — LLMs CAN evaluate Arabic (50-93% accuracy depending on model and task), multi-model evaluation IS justified, RAG faithfulness checking IS a solved problem. Running synthetic versions of these experiments adds marginal information.

What we actually need to know is engine-specific: "Can an LLM correctly judge whether the source engine identified ابن عقيل as the author of this specific Shamela export?" That question only becomes testable when the source engine exists and produces real output.

The per-engine cycle is:

```
Per engine:
  1. You review the SPEC, bring domain comments    (1 session, you + Claude Chat)
  2. Discuss and finalize the SPEC
  3. Claude Code builds as testable CLI             (1-3 Claude Code sessions)
  4. Run on real sources
  5. Test output:
     5a. Deterministic checks (schema, coverage, text integrity)
     5b. LLM-as-worker: do the LLMs INSIDE the engine get their tasks right?
         (e.g., did the source engine's LLM correctly classify this book's science?)
     5c. LLM-as-evaluator: can an INDEPENDENT LLM review this engine's complete
         output and catch errors that self-validation missed?
         (e.g., give a different model the metadata and ask "is this correct?")
  6. Fix, re-run, iterate until trusted
  7. Next engine
```

Steps 5b and 5c test two distinct things. 5b tests the engine's internal machinery — if the LLM calls inside the engine don't work, the engine doesn't work. 5c tests whether LLM-based output review is viable and valuable for this specific engine's output type. Both are tested with real pipeline output, not synthetic examples.

### Open Design Question: Inter-Engine LLM Gates

**Question:** Should the production pipeline include an independent LLM review of each engine's output before the next engine consumes it?

**Current architecture:** Engine self-validates → writes to disk → next engine reads. No independent review between engines. Human gates trigger only for specific low-confidence decisions, not as general output review.

**The gap:** Self-validation is checking your own homework. The source engine's LLM infers science=nahw, and the source engine's self-validation checks that the science field is non-empty and valid — it doesn't ask a different model "is this actually a nahw book?" Errors that pass self-validation compound downstream.

**Resolution:** This decision is deferred until we have real engine output. Step 5c of each engine's build cycle gathers the evidence: how many errors does self-validation catch? How many additional errors does independent LLM evaluation catch? What's the cost? By the time we've built 3-4 engines, the data will make the decision for us. If LLM evaluation consistently catches critical errors that self-validation misses, it becomes a production gate. If self-validation + human gates are sufficient, it stays a testing-only tool.

**Owner action required before starting:** Provide the OpenRouter API key and create `.env` from `.env.template`. LLM calls are needed from the source engine's metadata enrichment onward.

---

### Phase 1: Source + Normalization — The Foundation (4–6 Claude Code sessions)

This is the right starting point. Everything downstream depends on it.

**Before Claude Code starts — Owner Domain Review (1 session):**
You said you're currently reading the source engine SPEC. Good. Here's what to focus on:

1. **Format coverage:** The SPEC lists format-specific extractors (Shamela HTML, PDF, image, Word, plain text, owner-authored). Look at the test fixtures — you have examples of HTML export, PDF, DOC, TXT, JPG, and owner notes. Does the SPEC handle what you actually have?
2. **Metadata extraction:** The SPEC says it extracts author, title, science, school, death date, etc. For YOUR actual sources, is this realistic? Some PDFs might just be scans with no machine-readable metadata.
3. **Trust scoring:** The SPEC has a 5-factor trustworthiness model. Does this match how you actually evaluate sources? Are there factors it misses (e.g., which tahqiq edition)?

After your review, a single Claude Chat session incorporates your feedback into the SPEC. Not a full refinement cycle — just your domain corrections.

**Claude Code builds (pipeline order):**

```
M1.1  Source engine: data models, identity, registries          (~1 session)
M1.2  Source engine: first format intake (HTML export — you have   (~1 session)
      html_export_minimal fixture for this)
M1.3  Source engine: metadata enrichment (needs API key)          (~1 session)
M1.4  Normalization engine: HTML export normalizer                (~1 session)
M1.5  Integration test: source → normalization end-to-end         (~1 session)
M1.6  Second format: PDF intake + normalization                   (~1 session)
      (waraqat_usul.pdf or ibn_aqil PDFs as test data)
```

**Testing at this phase:**

*5a — Deterministic:* The source and normalization engines are mostly deterministic. The right checks are:
- Does the frozen source match the input byte-for-byte?
- Does metadata.json have all required fields?
- Does content.jsonl preserve all Arabic text including diacritics?
- Does the normalization boundary contract hold? (source output → normalization input)
- Do page references survive normalization?

*5b — LLM-as-worker:* The source engine uses LLMs for metadata enrichment (science classification, school detection, author identification). Test: run the engine on the test fixtures, then manually check whether the LLM-produced fields are correct. For the first few sources, YOU are the ground truth — you know what science الورقات belongs to, you know who wrote المغني.

*5c — LLM-as-evaluator:* After the source engine produces metadata for a real source, give a DIFFERENT model the frozen source + the metadata and ask "is this metadata correct?" Track: what errors does this catch that self-validation didn't? What errors does it miss? This is the first data point for the inter-engine LLM gate decision.

Gold baselines: YOU create these for the first 2–3 sources. Hand-verify one HTML export and one PDF through the whole Source → Normalization chain. This is maybe 2 hours of your time but it's the foundation everything else calibrates against.

**Shared component: consensus module (minimal)**
The source engine's metadata enrichment (M1.3) needs LLM calls. Rather than building the full consensus SPEC, build JUST enough:
- A function that calls 2+ models via OpenRouter and compares responses
- Returns (answer, confidence, agreement_level)
- This is maybe 100 lines of code, not the full 405-line SPEC

The full consensus module can be built later when the excerpting engine needs it. Don't let shared component scope creep block engine progress.

---

### Phase 2: Passaging + Atomization (3–5 Claude Code sessions)

These two engines are the most refined SPECs in the project. They should build quickly.

**Owner Domain Review: probably not needed.**
These engines are format-agnostic (they work on normalized packages, not raw sources) and they've been through 4+ refinement sessions. Unless you have specific scholarly concerns about how text should be divided into passages or atoms, Claude Code can build directly from the SPECs.

If you DO want to review, focus on: "When I'm studying a sharh, how do I think about where one topic ends and another begins?" and "What counts as a single scholarly atom — one opinion? one piece of evidence? one complete argument?"

**Claude Code builds:**

```
M2.1    Passaging: loader + assembly + prose strategy            (~1 session)
M2.2    Passaging: emission + validation + orchestrator          (~1 session)
M2.3    Atomization: errors + config + loader + predetection     (~1 session)
M2.4    Atomization: LLM atomizer + post-processing + validator  (~1 session)
M2.5    Integration: normalization → passaging → atomization     (~1 session)
```

**Testing at this phase:**

*5a — Deterministic:* Passage coverage (every unit in exactly one passage), atom coverage (every character in exactly one atom), ordering invariants, text preservation. These engines have extensive self-validation checks already specified (11 checks for passaging, 9 for atomization).

*5b — LLM-as-worker:* The atomization engine uses LLMs for boundary detection and scholarly function classification. Test: are the atom boundaries sensible? Are scholarly functions correctly identified (opinion vs evidence vs definition)? Run on all 7 test fixtures and spot-check results.

*5c — LLM-as-evaluator:* Have a different model read each passage and say whether it's a complete, coherent unit of text. Have it review atom boundaries and say whether any atoms were split mid-argument or mid-sentence. Track error catch rates vs self-validation — second data point for the inter-engine gate decision.

Run on ALL 7 test fixtures, not just one format. The passaging and atomization engines should work the same regardless of source format (that's the normalization boundary guarantee).

**Additional format strategies** (verse, masala, commentary, etc.) are deferred until the prose strategy works. Alfiyyah and Ibn Aqil fixtures can test these later.

---

### Phase 3: Excerpting + Taxonomy (4–6 Claude Code sessions)

This is where the pipeline crosses from "text processing" to "knowledge extraction." This is also where LLMs become essential and where errors become dangerous (wrong attributions, misclassifications).

**Owner Domain Review (1 session, essential):**
The excerpting engine decides what's worth extracting and who said what. The taxonomy engine decides where it goes. These are scholarly judgment calls. Focus on:

1. **Excerpting:** Read SPEC §4.A.3 (self-containment rules) and §4.A.4 (attribution detection). Ask yourself: "If this engine extracts an excerpt from الكتاب and says سيبويه said X, how confident should it be? What are the ways it could get this wrong?"
2. **Taxonomy:** Read SPEC §4.A.2 (tree structure). Does the science tree in `library/sciences/` match how you actually organize your studies? Are there sciences missing? Are the subdivisions right?

**Claude Code builds:**

```
M3.1    Excerpting: foundation (loader, context builder)         (~1 session)
M3.2    Excerpting: LLM extraction + self-containment check      (~1 session)
M3.3    Excerpting: attribution detection + consensus             (~1 session)
M3.4    Taxonomy: tree operations + placement                    (~1 session)
M3.5    Integration: atoms → excerpts → placed in taxonomy       (~1 session)
```

**Testing at this phase — this is where evaluation gets serious:**

*5a — Deterministic:* Every excerpt traces to source atoms, every placed excerpt has a taxonomy leaf, metadata passes through (D-023), school consistency across excerpts from the same author.

*5b — LLM-as-worker:* The excerpting engine uses LLMs for self-containment evaluation, attribution detection, and implicit reference resolution. The taxonomy engine uses LLMs for placement scoring. These are the highest-risk LLM tasks in the pipeline — a wrong attribution here propagates all the way to synthesis. Test: for each source, manually verify a sample of attributions and placements. "Did the LLM correctly identify that this is ابن قدامة's opinion, not المرداوي's commentary on it?"

*5c — LLM-as-evaluator:* Give a different model each excerpt with its metadata and ask: "Is this self-contained? Is the attribution correct? Is the school classification right?" Give it placed excerpts and ask: "Does this excerpt belong in this taxonomy leaf?" Track catch rates — third data point. By now we should have enough data from three engine pairs to make the inter-engine gate decision.

*Owner spot-check:* You review 10–20 excerpts and placements from each source. This is where you catch the errors LLMs miss — subtle misattributions, wrong school classifications, placement in the wrong science branch.

---

### Phase 4: Synthesis (3–4 Claude Code sessions)

The highest-risk engine. This is the product.

**Owner Domain Review (1 session, essential and intensive):**
Read the full synthesis SPEC §4. Focus on:
1. **Entry structure:** Does the output structure in §3 match ENTRY_EXAMPLE.md? Will it produce entries you'd actually study from?
2. **Grounding rules (D-040):** Every claim must be tagged as source_grounded, metadata_derived, or analytical. Are there claims you'd expect in an entry that don't fit these categories?
3. **Arabic quality:** The synthesizer writes Arabic scholarly text. Read the examples in §4.B. Does the Arabic sound like scholarship or like AI-generated text?

This review should happen during step 1 of the synthesis engine's per-engine cycle. By now you'll have real excerpts and taxonomy placements to use as input, not synthetic examples.

**Claude Code builds:**

```
M4.1    Synthesis: foundation (loader, excerpt aggregation)      (~1 session)
M4.2    Synthesis: entry generation (LLM-based, core §4.A rules) (~1 session)
M4.3    Synthesis: grounding verification + self-validation      (~1 session)
M4.4    Integration: full pipeline source → entry                (~1 session)
```

**Testing at this phase — all dimensions:**

*5a — Deterministic:* Every claim tagged with grounding_type. Every source_grounded claim cites a real excerpt. Schema compliance. Temporal ordering consistency (earlier scholars cited before later ones).

*5b — LLM-as-worker:* The synthesis engine IS an LLM worker — it generates the entire entry. This is where 5b and the product quality converge. Test: does the generated entry match the quality target in ENTRY_EXAMPLE.md? Does it produce scholarly narratives (not flat compilations)? Does it use metadata for intellectual genealogy (teacher-student chains, school context, temporal depth)?

*5c — LLM-as-evaluator (multi-model panel):* Three different models evaluate accuracy, attribution, completeness, and tone (the rubrics from JUDGE_PANEL_ARCHITECTURE.md). This is the only engine where a full multi-model panel is justified from the start — the synthesis engine's output is the product.

*Faithfulness check (RAGAS-style):* Extract claims from the entry, verify each against the cited excerpt. Use SelfCheckGPT: run synthesis 3 times on the same excerpts, check consistency. Claims that appear in all 3 runs are high-confidence. Claims in only 1 run are likely hallucinated.

*Owner review:* You read every entry produced during testing. All of them. This is the product. If you won't study from it, nothing else matters.

**Consistency oracle:** Run the same 5 sources through synthesis 3 times. Claims that appear in all 3 runs are high-confidence. Claims that appear in only 1 run are likely hallucinated. (This is the SelfCheckGPT method from Research Finding 11c.)

---

### Phase 5: Scale Testing (ongoing, weeks not sessions)

Only after the pipeline works end-to-end on the 7 test fixtures.

**What changes at scale:**
- Source diversity: add more formats (EPUB, scanned images via OCR, owner notes). Milestone 6 from MILESTONES.md.
- Volume: run 50 real sources through the full pipeline. The autonomous loop (C compiler pattern) can handle this — Claude Code processes sources, evaluates output, logs findings, fixes bugs.
- Edge cases: sources with unusual structure, missing metadata, mixed languages, heavily damaged text.

**What to build for scale testing:**
1. `kr-pipeline` CLI: `kr-pipeline run <source_path>` → runs all 7 engines, produces output at every stage
2. `kr-evaluate` CLI: `kr-evaluate <source_id>` → runs deterministic checks + LLM evaluation, produces a report
3. `kr-findings` tracker: OPEN.md file listing all evaluation failures with severity and engine
4. Regression test suite: every bug fixed gets a test case that prevents recurrence

**Do NOT build upfront:**
- Complex orchestration (Paperclip, agent teams). Bash scripts + git are sufficient for 3–4 parallel agents.
- A full judge panel system. The evaluation should be a simple Python script that calls OpenRouter, not a framework.
- Dashboard or visualization. Text reports are fine for one user.

**Trust graduation (adapted from JUDGE_PANEL_ARCHITECTURE.md):**

```
Level 0: Pipeline runs without crashing on all 7 fixtures     ← Phase 1-4
Level 1: Deterministic checks pass on 20+ sources             ← Phase 5 start
Level 2: LLM evaluation >90% CORRECT on 20+ sources           ← Phase 5 middle
Level 3: Owner approves 10 full entries                        ← Phase 5 end
Level 4: 100+ sources processed, 0 open CRITICAL findings     ← Pipeline trusted
```

Only after Level 4: build the application (GUI, scholar interface).

---

## What to Do About the Shared Components

The 6 shared components (consensus, validation, human_gate, feedback, user_model, scholar_authority) have draft SPECs but no refinement and no contracts.

**The honest recommendation: build them incrementally, not as a separate milestone.**

- **Consensus:** Build a minimal version for M1.3 (source metadata enrichment). Expand when excerpting needs it (M3.3). The full SPEC is overkill for the first pass.
- **Validation:** Already partially embedded in each engine's §5. A shared module can be extracted when patterns repeat across 2+ engines.
- **Human gate:** Build when the first irreversible library write happens (likely M3.4, taxonomy placement). Start with a simple "write a JSON file, owner reviews it" pattern.
- **Feedback, user model, scholar authority:** These are application-layer concerns. Don't build them during pipeline testing. They matter when the GUI exists.

---

## Concrete Next Steps (what to do Monday)

1. **Configure API keys.** Create `.env` from `.env.template`. Add OpenRouter key. This unblocks all LLM-dependent work.
2. **Finish your source engine domain review.** You said you're reading it now. Write your comments. Focus on format coverage, metadata extraction, and trust scoring. This is step 1 of the per-engine cycle.
3. **We discuss your comments in a session.** Incorporate your domain corrections into the SPEC. One session, not a full refinement cycle.
4. **Fix NEXT.md.** It currently points to atomization implementation (engine 4 in pipeline order). It should point to source engine implementation (engine 1). The pipeline must be built in order.
5. **Update SPEC refinement tracking.** refinement_status.py is wrong — passaging and atomization DID go through refinement. Fix the tracking so the status reflects reality.
6. **Claude Code starts M1.1** (source engine data models and identity). After your domain review is incorporated.

---

## Timeline Estimate (honest, with uncertainty)

| Phase | Sessions | Elapsed time (estimate) | Depends on |
|-------|----------|------------------------|------------|
| Phase 1: Source + Norm | 5–7 | 2–3 weeks | API key, owner domain review |
| Phase 2: Pass + Atom | 4–6 | 2 weeks | Phase 1 complete |
| Phase 3: Exc + Tax | 5–7 | 2–3 weeks | Owner domain review |
| Phase 4: Synthesis | 4–5 | 2 weeks | Owner domain review |
| Phase 5: Scale | ongoing | 4–8 weeks | Pipeline works end-to-end |

**Total to trusted pipeline: roughly 3–4 months.** This is longer than any previous estimate in the repo, but it's honest. The previous estimates didn't account for the owner domain reviews or the reality that Claude Code sessions have a learning curve on a new codebase. The per-engine validation (step 5 in the cycle) is embedded in each phase, not a separate phase.

---

## What This Plan Kills

1. **The 4-session refinement cycle for remaining engines.** Replaced with 1 focused owner domain review per engine. The SPECs are good enough. Build, then fix.
2. **Atomization as the next implementation target.** Build in pipeline order: source first.
3. **The full judge panel as an upfront system.** Build evaluation incrementally per engine — deterministic checks first, LLM checks at step 5 of each engine's cycle, the full panel only for synthesis.
4. **Shared components as a separate milestone.** Build them when the engines need them, not before.
5. **Elaborate autonomous agent infrastructure.** Start with `python3 kr-pipeline run <source>` and `python3 kr-evaluate <source_id>`. Add autonomy when you need scale.

## What This Plan Preserves

1. **The owner's domain review before each engine.** You want this. It's the right instinct. But 1 session, not 4.
2. **Testing each engine after it's built** — including LLM evaluation of that engine's specific output (step 5 of the per-engine cycle).
3. **The pipeline CLI as the build target.** Not the application.
4. **The research findings.** Multi-model evaluation, cascaded checking, RAGAS faithfulness — all used at the right time, per engine, grounded in real output.
5. **All 7 SPECs.** Nothing gets thrown away. They're the implementation guide for Claude Code.
6. **The experiment1 script.** Gets adapted for each engine's step 5 evaluation, using real pipeline output instead of synthetic claims.
