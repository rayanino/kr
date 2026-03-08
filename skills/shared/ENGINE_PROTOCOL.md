# Engine Protocol — المسار لكل محرك

This is YOUR guide. Follow it top to bottom for each engine. Don't skip steps. Don't mix steps.

---

## The Principle

**Depth over breadth. Reliability over features. Every block proven before building on it.**

Each engine has a core — the fundamental thing it does, the reason it exists. A source engine ingests and registers sources. A normalization engine transforms raw formats into a single clean structure. A passaging engine divides text into coherent units. That core must be specified in sufficient detail, tested against reality, built, and made bulletproof — before anything else.

Features that extend the core (more input formats, advanced detection, clever optimizations) come later. They build ON the core. If the core is unreliable, features built on it are unreliable. If the core is solid, features are straightforward additions.

---

## Two Stages

### Stage 1: Core Pipeline (v0.0.1)

Build all 7 engines, one at a time in pipeline order, each focused only on its core architecture. The goal: a narrow but reliable pipeline where data flows from source intake to knowledge entry. Every engine does its fundamental job well on a small number of supported inputs.

Stage 1 begins with a **tracer bullet** — a thin end-to-end slice that validates every contract boundary before any engine is deepened. Then each engine is built through a 4-step process.

### Stage 2: Expansion

Go back engine by engine and add capabilities. More input formats, advanced features, §4.B transformative capabilities. Each addition is a scoped project built on a proven foundation, informed by real evidence from Stage 1.

**This document governs Stage 1.** Stage 2 gets its own protocol when Stage 1 is complete.

---

## Step 0: Tracer Bullet — Validate the Pipeline Shape

**This step happens ONCE, before the per-engine cycle begins.**

**Goal:** Get data flowing from a Shamela HTML file to a rough knowledge entry through all 7 engines. Not good data — rough, ugly, minimal. The point is to validate every contract boundary, every metadata pass-through, and every data structure assumption with real data. This is the most important risk-reduction step in the entire project.

**Why this matters:** The biggest risks in a 7-engine pipeline are not within engines — they are at the boundaries between engines. What metadata does the normalization engine actually need from the source engine? What does the passaging engine need from normalization? These questions can only be answered by running real data through real (if rough) code. Without a tracer bullet, you discover boundary mismatches engine by engine over weeks, each discovery potentially requiring rework on earlier engines.

The concept comes from Alistair Cockburn's "walking skeleton" and Hunt & Thomas's "tracer bullets" in The Pragmatic Programmer: build a thin, production-quality slice that exercises all layers of the system, then deepen each layer iteratively.

**Existing assets:** All 7 engines already have SPECs (918-2,006 lines) and contracts.py files (491-825 lines). Four engines have partial src/ directories. The tracer bullet's job is NOT to create these from scratch — it is to reconcile, validate, and connect what exists.

**What happens:**

1. **Reconcile the 7 existing contracts.py files.** Load source output into normalization input. Load normalization output into passaging input. Repeat for every boundary. Fix every mismatch: type conflicts, missing fields, renamed enums, incompatible schemas. Currently only the passaging engine imports from normalization — the other 5 boundaries have no Python-level enforcement. The tracer bullet enforces all 6.

2. **Stub shared components.** The engines depend on shared infrastructure that has SPECs but no implementation: consensus (multi-model LLM verification), human_gate (owner approval checkpoints), scholar_authority (scholar identity registry), and validation (output checks). Build minimal stubs for each — just enough that engine code can call them without crashing. Consensus returns hardcoded agreement. Human gate auto-approves. Scholar authority stores and retrieves records. Validation passes everything. These stubs evolve into real implementations during the source engine build (Step 3 for engine 1).

3. **Build rough stubs for all 7 engines.** Each stub accepts its input contract, performs the simplest possible transformation (even if the output quality is terrible), and produces output conforming to its output contract. LLM calls can return hardcoded plausible values for now. The goal is data flowing, not data quality.

4. **Build a pipeline runner script.** A simple script (`scripts/run_pipeline.py`) that chains the 7 engines sequentially: runs engine 1 on a fixture, feeds output to engine 2, feeds that to engine 3, etc. This does not need to be the final orchestration system — it just needs to execute the chain and report contract violations at each boundary.

5. **Run one Shamela HTML file through the full pipeline.** Feed the `html_export_minimal` fixture through all 7 stubs. The output will be a rough, probably wrong knowledge entry. That is fine. What you are checking: Does data flow without contract violations? Does metadata accumulate correctly (D-023)? Are there fields engine N needs that engine M does not produce? Does the final entry have all the pieces (even if they are wrong)?

6. **Document every boundary issue found.** Every contract mismatch, every missing field, every assumption that broke. These findings feed directly into the engine-by-engine SPECs.

**Skills used:** `kr-research` for contract design questions. `kr-build-prep` for the stub architecture.

**Rules:**
- Keep it lean. The tracer bullet is 3-5 sessions, not a month-long project.
- Stubs are production code structure with placeholder logic — they will evolve into the real engines.
- Do NOT optimize any engine's logic during this step. Resist the temptation to make the source engine "good" while the others are stubs.
- The tracer bullet code lives in the main engine directories, not in a throwaway prototype folder. It IS the skeleton the real engines grow on.
- Shared component stubs live in their existing `shared/` directories.

**You're done when:** One Shamela HTML fixture produces one (rough) knowledge entry with no contract violations at any boundary. All 7 contracts.py files are reconciled and import-tested against their neighbors. Shared component stubs exist. The pipeline runner works. Boundary issues are documented in `reference/TRACER_FINDINGS.md`.

---

## Stage 1: Per-Engine Process

After the tracer bullet validates the pipeline shape, each engine goes through 4 steps. You are always in exactly ONE step.

### Step 1: SPEC — Core Architecture

**Goal:** Produce a SPEC that describes the core engine in enough detail that Claude Code can build it correctly. The spec depth is iterative — start with significant decisions, deepen after test feedback reveals where more detail is needed.

**What "core" means:**

The core is the engine's identity — what makes it THIS engine and not something else. It is the minimum set of behaviors that, if any were removed, the engine would no longer fulfill its purpose in the pipeline.

For the source engine: format detection, metadata extraction, metadata inference (LLM), freezing, deduplication, registration, trust evaluation. On TWO formats: Shamela HTML and plain text. That's the core.

NOT core: audio transcription, OCR from phone photos, citation network discovery, tahqiq apparatus fingerprinting, source difficulty prediction. These are extensions that build on a working core.

**What happens in this step:**

1. **Identify core vs. deferred.** Read the current SPEC. Draw the line: what is the engine's fundamental job? What is an extension? Everything deferred gets a single line: "Deferred to Stage 2 expansion." The SPEC's depth budget goes entirely toward the core. For each deferred capability, note what the core must NOT assume in order to keep the extension path open (see Extension Hooks below).

2. **Assess SPEC maturity.** Not all SPECs need the same treatment. Some have been through multiple refinement passes (normalization has had 4 passes; synthesis has had 3). Others are rougher. For mature SPECs where §4.A has already been through PRECISION and HARDENING: core extraction is surgical — move §4.B to deferred, add extension hooks, verify §4.A is still implementation-ready. Do NOT rewrite refined §4.A content. For immature SPECs where §4.A has known defects or vague language: core extraction includes rewriting §4.A to significant-decisions depth.

3. **Owner domain review.** The owner reads the core sections and writes comments. The depth of owner involvement varies by engine:
   - **Heavy domain review** (source engine, synthesis engine): The owner has strong domain knowledge about how Islamic books work and what scholarly entries should look like. Full comment process.
   - **Moderate domain review** (normalization engine): The owner knows about matn/sharh layer conventions, footnote styles, and physical book structure. Comments focus on "would this correctly handle my real books?"
   - **Light domain review** (passaging, atomization, excerpting, taxonomy): The owner's expertise is less relevant at the spec stage. A brief read-through for anything surprising is sufficient. The owner's real contribution for these engines comes at Step 4, reviewing actual Arabic output.

4. **Claude investigates comments.** Research-heavy. Claude uses web search, Exa, Scholar Gateway, Tavily — whatever tools help find the best approach. For every core design decision, Claude researches how similar systems handle it, what the tradeoffs are, what the state of the art is. This is not a quick review — it's deep architectural research grounded in domain feedback.

5. **Write the core SPEC to significant-decisions depth.** The SPEC should cover every data structure (field names, types, constraints), every LLM call (input, prompt strategy, structured output, model, fallback), every error path (code, severity, recovery), and every decision point (threshold, logic). The goal is that Claude Code can build the right architecture with zero clarifying questions about *what* to build. Where exact thresholds or prompt templates are uncertain, mark them as `[ASSUMPTION — NEEDS STEP 2 TESTING]` rather than guessing a precise value. Step 4 (TEST) will reveal which areas need further specification — deepen iteratively rather than trying to anticipate every edge case upfront.

**Extension hooks:** When deferring a capability, add one line noting what the core architecture must not assume. Examples: "Core must not assume exactly one author per source — multi-author support is deferred but the data model must accommodate it." "Core must not hardcode Shamela HTML parsing logic into the metadata extraction flow — format-specific logic must be in pluggable modules." This costs almost nothing but prevents the core from accidentally closing doors on Stage 2 extensions.

**Skills used:** `kr-core-extract` for the classification and rewrite. `kr-spec-review` for comment resolution. `kr-research` when deep research is needed. `kr-integrity` as the final quality gate — audits the SPEC for technical defects that domain review can't catch (ambiguous rules, missing error paths, knowledge corruption risks, untested assumptions, extension-blocking assumptions).

**Rules:**
- Do comments in batches of 3-5 per chat. Fresh chat when things get long.
- Claude may disagree with your comments. Listen on technical matters. Push back on domain matters — you're the authority.
- If a design question can't be resolved by discussion alone, it becomes a research question for Step 2.

**You're done when:** The core SPEC has passed kr-integrity's technical audit with all HIGH-severity defects fixed. Every sentence in §4.A is either a binding rule with enough detail for implementation, or a marked assumption that Step 2 will answer through testing. All §4.B content and non-core features are explicitly deferred with extension hooks documented.

---

### Step 2: RESEARCH — Validate Assumptions

**Goal:** Every assumption the core SPEC rests on gets tested BEFORE building. If an assumption fails, the SPEC changes. The SPEC drives the build, so the SPEC must be grounded in evidence.

**What gets tested:**

Any part of the SPEC where the design depends on something unproven. Common categories:

- **LLM reliability.** The SPEC says "use an LLM to identify the author." Can it? Run the actual call on your actual fixtures. Measure accuracy. If it's unreliable, the SPEC changes — maybe to a different prompt, a two-stage approach, a lookup table, or a human gate.

- **Data structure fitness.** The SPEC defines output schemas. Do they carry enough information for the next engine? The tracer bullet already validated the basic contract shape, but the SPEC may have added fields or constraints that need verification. Run realistic data through the contracts and check.

- **Tool capabilities.** The SPEC says "use X library for Y." Does it actually handle Arabic text correctly? Does it handle your specific formats? Run it on your fixtures.

- **Architectural questions.** Should this be one LLM call or two? Should consensus require 2 models or 3? What confidence threshold separates "accept" from "human review"? These are empirical questions with testable answers.

**How it works:**

Claude designs and runs targeted experiments. Not building the engine — running isolated tests of specific assumptions. Each experiment:
1. States the assumption being tested
2. Describes the test (input, method, expected output)
3. Shows the actual results
4. Recommends a SPEC change if the assumption failed

Results are documented in the engine directory as `engines/{engine}/research/`. Every finding feeds back into the SPEC. The SPEC is updated before moving to Step 3.

**Important boundary:** Some assumptions can only be validated by running data through the engine or a downstream engine. If an assumption requires building engine code to test, do not hold Step 2 open waiting — mark it as `[BUILD-PHASE VALIDATION]` with a specific test to run during Step 3. Step 2 tests assumptions that can be tested in isolation; Step 3 tests those that require integrated code.

**Tools:** This is where you use everything — Exa for finding similar architectures, Scholar Gateway for academic approaches, Tavily for comprehensive research, web search for tool comparisons, actual API calls to test LLM reliability. Assume infinite budget.

**You're done when:** Every marked assumption in the SPEC has been tested on at least 3 representative fixtures, or explicitly deferred to BUILD-PHASE VALIDATION. The SPEC has been updated with findings. There are no open questions that would change the architecture.

For LLM reliability assumptions specifically: ≥85% accuracy across fixtures means the design holds. <70% means redesign the approach (different prompt, two-stage pipeline, lookup table, or human gate). Between 70-85% means add an explicit fallback path in the SPEC and proceed to BUILD with test coverage for the fallback.

**Constraint:** Do not run more than 3 research sessions per engine. If assumptions are still uncertain after 3 sessions, they become BUILD-phase experiments with explicit test coverage — building and testing will resolve them faster than more isolated experiments.

---

### Step 3: BUILD

**Goal:** Turn the SPEC into a working, testable engine.

**What happens:**

1. **Build prep** (first session). Set up the Claude Code environment: CLAUDE.md, architecture doc, testing infrastructure, session plan. This is one session of build prep, not a separate phase. The tracer bullet stub for this engine already exists — the build deepens it into a real implementation.

2. **Build shared component dependencies.** If this engine requires shared components (consensus, human_gate, scholar_authority, validation) that are still stubs, build the minimum viable versions needed for THIS engine's core. The source engine will need to build the most — it is the first consumer of consensus (for author identification), human_gate (for low-confidence decisions), scholar_authority (for scholar records), and validation (for output checks). Later engines reuse what the source engine built and extend as needed.

3. **Incremental build.** Each session adds one capability with its tests. 5a deterministic tests run continuously. 5b LLM-worker tests run as each LLM-dependent feature is added. No session ends with untested code.

4. **Core formats only.** The engine supports exactly the formats specified in the core SPEC. No scope creep.

5. **BUILD-PHASE VALIDATION.** Run the tests marked `[BUILD-PHASE VALIDATION]` from Step 2 as the relevant code is implemented. Update the SPEC if results require design changes.

6. **Contract sync.** If this engine's build reveals that its contracts.py needs changes (new fields, type changes), update the neighboring engines' contracts.py files to match. Run the pipeline runner script to verify no downstream stubs break. Commit contract changes together with the engine changes, never separately.

**You're done when:** The engine runs on all specified input formats, all 5a tests pass, 5b tests show ≥90% accuracy, all BUILD-PHASE VALIDATION items are resolved, and contract changes are synced with neighbors.

---

### Step 4: TEST — Prove Reliability

**Goal:** Subject the engine to ruthless testing until it is bulletproof. Find core gaps — not nice-to-haves, but things that would corrupt the pipeline if left unfixed.

**What happens:**

1. **Full 5a/5b/5c evaluation** across all test fixtures appropriate for the core formats.

2. **You review output.** Not "does this look OK?" but specific questions: "Is this author identification correct?" "Is this science classification right?" "Does this metadata capture everything a downstream engine needs?"

3. **Every finding is categorized:**
   - **Core gap:** Something fundamental is wrong or missing. Metadata that downstream engines need but isn't captured. A failure mode that corrupts data. An unreliable LLM task. **These get fixed before moving on.**
   - **Extension opportunity:** Something that would improve the engine but isn't required for the pipeline to work. Audio support, better OCR, advanced features. **These get documented for Stage 2.**
   - **Lesson learned:** An insight about LLM reliability, data structure design, testing approaches, or anything else. **These feed forward to the next engine.**

4. **Fix core gaps → re-test → repeat** until no core gaps remain.

5. **Document everything.** Findings, lessons, extension opportunities. This documentation is as valuable as the code — it's the knowledge that informs every subsequent engine and all of Stage 2.

6. **Run pipeline integration test.** Feed the engine's output into the next engine's tracer bullet stub. Run `scripts/run_pipeline.py` from this engine's output through the remaining stubs. Verify the contract boundary holds with real (not mocked) data. If it breaks, fix the contract mismatch before moving on.

7. **For the synthesis engine only:** Build a minimal entry viewer (`scripts/render_entry.py`) that converts the output JSON into readable Markdown or HTML. Without this, the owner cannot assess the most important quality metric: "Does this read like a scholarly reference I would trust?" The entry viewer is a Step 4 prerequisite for engine 7, not a nice-to-have.

**You're done when:**
- All 5a deterministic checks pass
- 5b LLM-worker accuracy ≥90%
- 5c independent review finds no errors that self-validation missed
- You have reviewed and approved the output on your real sources
- All core gaps are fixed
- Pipeline integration test passes against the next engine's stub
- Lessons and extension opportunities are documented

Then you start Step 1 for the NEXT engine in the pipeline.

---

## Lessons Backward Review

**After engines 2, 4, and 6,** spend one session reviewing whether lessons from recent engines suggest changes to earlier engines. This is not rebuilding — it is documenting what you would change and making targeted fixes where the cost is low.

Specifically:
- Do the LLM consensus thresholds from earlier engines still seem right given what you learned since?
- Did any data structure pattern emerge that earlier engines should adopt?
- Did any testing approach prove more effective than what earlier engines used?
- Are there extension hook assumptions that need updating?

If a backward fix is small (adding a metadata field, adjusting a threshold), make it and re-run that engine's tests. If it requires significant redesign, document it in `reference/BACKWARD_LESSONS.md` for Stage 2.

---

## Engine Order

Pipeline order. Each engine's core must be reliable before starting the next.

```
0. Tracer bullet        (رصاصة كاشفة)     ← validates all boundaries first
1. Source engine        (محرك المصادر)
2. Normalization engine (محرك التسوية)    ← lessons backward review after this
3. Passaging engine     (محرك التقطيع)
4. Atomization engine   (محرك التذرية)    ← lessons backward review after this
5. Excerpting engine    (محرك الاستخراج)
6. Taxonomy engine      (محرك التصنيف)    ← lessons backward review after this
7. Synthesis engine     (محرك التركيب)
```

After engine 7's core is proven: **Stage 1 is complete.** You have v0.0.1 — a narrow, reliable pipeline. Data flows from a Shamela HTML file to a knowledge entry. Every engine does its fundamental job. Every block is proven.

---

## Engine-Specific Notes

Not all engines are equal in complexity. These notes prevent misclassification and call out prerequisites.

**Source engine (1).** The heaviest build — it bootstraps the shared components (consensus, human_gate, scholar_authority, validation). Plan for extra sessions. Trust evaluation is core but keep it simple for v0.0.1: a 3-tier classification (verified / flagged / unknown) rather than the elaborate scoring algorithm in the current SPEC.

**Normalization engine (2).** Basic layer detection (matn vs sharh vs hashiyah) using format-specific CSS classes is CORE, not deferred. Without it, the passaging engine cannot align commentary to base text, the atomization engine cannot attribute atoms to the right author, and the synthesis engine cannot produce the narratives shown in ENTRY_EXAMPLE.md. The test fixture (Ibn Aqil's sharh) IS a multi-layer text. Advanced layer detection (inferring layers when markup is absent) is deferred.

**Passaging engine (3).** Fast-track candidate — its core is simple (heading-based splitting for structured text, fixed-size for unstructured). The existing SPEC's §4.A is reasonably mature. Expect light Step 1, minimal Step 2, and a straightforward build. Core structural formats: prose and commentary-with-layers. Verse and dictionary are deferred.

**Atomization engine (4).** The first engine where the LLM does the primary work (classifying scholarly function). Step 2 research is critical: if LLM accuracy on scholarly function classification is below 70%, the approach needs fundamental redesign before building.

**Excerpting engine (5).** Self-containment evaluation is the highest-risk LLM task in the pipeline (T-4: Context Loss). Step 2 research must determine whether LLMs can reliably judge "can a reader understand this excerpt alone?" If unreliable, consider larger excerpts with guaranteed surrounding context rather than precise self-containment judgments.

**Taxonomy engine (6).** **Prerequisite:** The engine needs a parsed science tree to place excerpts into. The library has SCIENCE.md files for 5 sciences, but these are prose research documents, not the data structures the engine consumes. Before Step 3, the owner must define at minimum the nahw (grammar) tree structure, and the architect must translate it into the engine's expected format. This is an owner deliverable — call it out early.

**Synthesis engine (7).** Core quality bar: structured compilation with temporal ordering, school attribution, and correct traceability (all claims to excerpt IDs). The full scholarly narrative quality from ENTRY_EXAMPLE.md (intellectual genealogy, "why scholars disagreed", "what to read next") can start basic in v0.0.1. Flat compilations are unacceptable even for core.

**Fast-track guidance.** Engines with simple cores (passaging, taxonomy in core-only mode) may not need the full 4-step treatment at full depth. Allow compressed Steps 1-2 (2-3 sessions combined) when the core is well-understood and the SPEC is mature. The same rigor applies to Step 3 (BUILD) and Step 4 (TEST) — the build just happens faster.

---

## What Gets Documented Per Engine

At the end of each engine's Step 4, produce:

```
engines/{engine}/LESSONS.md
```

Contents:
- What LLM tasks worked reliably, and what didn't
- What data structures worked, and what needed changing
- What testing approaches were effective
- Architectural decisions that affected downstream engines
- Extension opportunities identified (for Stage 2)
- Extension hooks that need updating based on what was learned
- Anything the next engine should know

These lessons accumulate. By engine 7, you have a comprehensive understanding of the pipeline's strengths and weaknesses — real evidence, not theory.

---

## Rules

1. **One engine at a time.** Don't start normalization until source is proven.
2. **Core only in Stage 1.** Every feature request gets asked: "Is this core, or is this an extension?" If extension, it goes in LESSONS.md for Stage 2.
3. **Test assumptions before building.** If the SPEC says "use an LLM for X," test whether an LLM can actually do X reliably. Before writing engine code.
4. **Fresh chats when context gets long.** 30+ turns or sluggish responses = time for a handoff.
5. **Always invoke skills by name.** "Use kr-spec-review" not "handle my comment."
6. **Document everything.** Lessons are as valuable as code.
7. **Quality over speed.** A narrow engine that works is worth infinitely more than a wide engine that doesn't.
8. **If Step 4 reveals a core design problem, go back to Step 1.** Write a new comment, resolve it, update the SPEC, rebuild. Don't patch.
9. **If engine N reveals that engine M (upstream) needs a change:** Document the required change in engine M's directory. Assess impact on engines M+1 through N-1. Update engine M's SPEC and code. Re-run engine M's Step 4 tests to confirm no regressions. Verify downstream contracts still hold. Then continue engine N. This is not a violation of Rule 1 — it is a targeted fix, not restarting engine M from scratch.
10. **Keep extension doors open.** When core architecture makes a structural decision (data model shape, module boundaries, processing flow), verify it does not block known Stage 2 extensions. One sentence per deferred capability noting the constraint.
11. **Iterate spec depth.** The first SPEC pass covers significant decisions — architecture, data structures, major error paths. Step 4 test feedback reveals where more detail is needed. Deepen the SPEC iteratively rather than trying to specify every edge case before any code runs.
12. **Keep contracts in sync.** When any engine's contracts.py changes, update neighboring engines' contracts.py to match and run `scripts/run_pipeline.py` to verify no stubs break. Contract changes are committed alongside the engine changes that caused them.
