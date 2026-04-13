# Engine Build Blueprint — المخطط التفصيلي لبناء المحركات

**Authority:** Concrete implementation of `skills/shared/ENGINE_PROTOCOL.md`.
ENGINE_PROTOCOL defines the 4-step framework; this Blueprint fills in
exactly how each step is executed, grounded in what actually happened
during the source engine build (March 2026, €30.60 spent, 379 test
functions (some parametrized → 500+ test cases), 204 validated books).

**Audience:** Claude Chat (architect/evaluator), Claude Code (builder),
and any future agent assigned to build an engine. Every step specifies
who does it. If a Claude Code session following this Blueprint would
need to improvise, the Blueprint is not specific enough.

**Governing principle:** Every step that produces output includes a
mandatory self-review protocol. The source engine's worst bugs were
self-review failures — protocol violations that produced output that
*looked* correct but was subtly wrong. See §Review Protocols below.

---

## Prerequisites: Before Any Engine

### 0a. Read Institutional Memory

Before starting any engine, the assigned agent reads:

| File | Why | Who reads |
|------|-----|-----------|
| `reference/KNOWLEDGE_INTEGRITY.md` | The 7 corruption threats. Every design decision must be checked against these. | Claude Chat |
| `reference/RESULT_PRESERVATION.md` | How results feed downstream. Every pipeline run must follow this. | Claude Chat + Claude Code |
| `reference/SILENT_FAILURES.md` | The 7 patterns that produce output that looks correct but isn't. | Claude Chat |
| `reference/DECISION_PLAYBOOK.md` | Accumulated domain heuristics (trigger→action pairs). | Claude Chat + Oracle |
| Previous engine's `LESSONS.md` | What the upstream engine learned. | Claude Chat |
| Previous engine's output contract | What this engine receives as input. | Claude Chat + Claude Code |

**Self-review:** After reading, list the 3 most relevant corruption
threats and 2 most relevant silent failure patterns for THIS engine.
If you cannot identify them, you have not read carefully enough.

### 0b. Verify Contract Boundary

Before writing any SPEC text, verify the input contract:

1. Read the upstream engine's `contracts.py` output classes
2. Read this engine's `contracts.py` input classes
3. Run `scripts/verify_metadata_flow.py` if available (caveat: this
   script can produce false positives from matching enum value names
   as field names — manually verify each flagged field before treating
   it as a real gap)
4. For each field this engine expects: confirm the upstream engine
   produces it, with the same name, same type, same optionality
5. Document any gaps in `reference/CONTRACT_VERIFICATION_REPORT.md`
6. Fix gaps BEFORE proceeding (update contracts.py on both sides)

**Evidence from source engine:** 5 contract defects were found at the
source→normalization boundary during pre-batch hardening (Step 3C of
the execution protocol). Each would have caused silent failures if
discovered during normalization engine development instead.

---

## Step 1: SPEC Design

**Who:** Claude Chat (architect). Owner provides domain input when asked.
**Duration:** 2-4 sessions.
**Input:** Existing SPEC (if any), upstream contracts, reference/KNOWLEDGE_INTEGRITY.md.
**Output:** Engine SPEC at architecture-decision depth.

### 1a. Cold Read and Defect Inventory

If the engine already has a SPEC draft (all 7 engines have initial
SPECs from the design phase), read the entire SPEC and create a defect
inventory. Check every section against the 7 silent failure patterns:

1. **Hollow examples** — Would a wrong implementation pass this example?
2. **Circular definitions** — Replace defined terms with definitions. Does content remain?
3. **Hand-waving technology** — Does the named tool actually work for Arabic? Search to verify.
4. **Phantom metadata** — Is every field that's consumed also produced upstream?
5. **Untestable rules** — Can you write a pass/fail test for this rule?
6. **Missing error paths** — What happens when this step fails?
7. **Scope creep** — Can this be implemented with only THIS engine's input and tools?

**Files produced:** Defect inventory as a numbered list with severity
(CORRECTNESS vs. STYLE) and affected SPEC section.

**Self-review (2 rounds):**
- Round 1: For each "no defect found" section, re-read with the
  specific question: "If I implemented this section literally, what
  would go wrong?" If nothing comes to mind, pick the most complex
  rule and trace its execution path through a concrete book.
- Round 2: Count the ratio of CORRECTNESS to STYLE defects. If >80%
  are STYLE, you are reviewing too superficially — CORRECTNESS defects
  hide in the interaction between rules, not in individual sentences.

### 1b. Owner Domain Comments (if applicable)

Some engines (source, normalization, taxonomy, synthesis) have
domain-sensitive design decisions. Others (passaging, atomization,
excerpting) are primarily technical.

For domain-sensitive engines:
1. Present the SPEC's core design decisions as specific questions
2. Owner answers based on domain knowledge
3. Claude Chat investigates each answer independently — owner comments
   are hypotheses, not instructions

**Skill:** `use kr-spec-review` for each comment batch.

**Key lesson from source engine:** The owner's domain input was
valuable for *what* (correct genre boundaries, attribution rules,
trust semantics) but not for *how* (data structures, validation
logic, error handling). Never let domain input override technical
architecture decisions.

### 1c. Research-Backed Resolution

For each CORRECTNESS defect and each domain comment, research before
resolving:

- Simple factual checks: 1-2 web searches
- Design decisions with multiple viable approaches: 5+ searches
- Novel capabilities or technology choices: 8+ searches via `use kr-research`

**Evidence from source engine:** The tahqiq-note ML bias (BUG-03) was
a design decision made without research — "editorial apparatus counts
as a scholarly layer" seemed reasonable but was systematically wrong.
Research into Islamic scholarly text structure would have revealed that
tahqiq notes are editor additions, not scholarly commentary layers.

**Files produced:** Updated SPEC sections. Each resolved defect gets a
brief rationale (1-2 sentences) explaining why this resolution was
chosen over alternatives.

**Self-review (2 rounds):**
- Round 1: For each resolution that required web search, re-read the
  actual search results (not your summary). Did you accurately
  represent what the sources said? Did you search for contradicting
  evidence?
- Round 2: For each design decision, ask: "What is the strongest
  argument this decision is wrong?" If you cannot generate a
  counterargument, you haven't understood the decision deeply enough.

### 1d. Integrity Audit

After all comments are resolved and defects fixed:

**Skill:** `use kr-integrity` — runs a technical audit checking for:
- Ambiguous rules that two implementers would interpret differently
- Missing error paths (every processing step needs: what if this fails?)
- Silent failure patterns from reference/SILENT_FAILURES.md
- Knowledge corruption paths from reference/KNOWLEDGE_INTEGRITY.md threats T1-T7
- Contract alignment with upstream and downstream engines

**Files produced:** Integrity audit report with findings categorized as
MUST-FIX (blocks build) or SHOULD-FIX (fix during build).

**Self-review (2 rounds):**
- Round 1: Re-read each MUST-FIX finding and verify it is not a false
  positive by tracing the relevant code path (or SPEC path) manually.
- Round 2: For each SHOULD-FIX, ask: "If this becomes a bug in
  production, how would it manifest? Would it be caught by any
  existing validation?" If no existing validation would catch it,
  upgrade to MUST-FIX.

### 1e. Core vs. Deferred Classification

**Skill:** `use kr-core-extract`

For every capability in §4:
- **Core:** The engine cannot fulfill its fundamental purpose without this
- **Deferred:** This extends the core but the engine works without it

**Evidence from source engine:** The initial SPEC had ~40 capabilities
in §4. After core extraction, the source engine shipped with 10 core
capabilities (§4.A.1 through §4.A.10). The deferred capabilities did
not block any downstream engine. Attempting to build all 40 would have
tripled the build time and budget.

**Rule:** When uncertain whether something is core, ask: "Does the
downstream engine's SPEC reference this capability's output?" If no,
it's deferred. If yes, it's core.

**Files produced:** Classification table in the SPEC. Each deferred
capability gets a one-sentence extension hook documenting what the
core must not assume (to keep the door open for Stage 2).

### Step 1 Completion Criteria

The SPEC is ready for build when:
- [ ] Every §4.A rule can be tested with a pass/fail criterion
- [ ] Every processing step has a defined error path
- [ ] Every metadata field consumed is produced by the upstream engine
- [ ] Every metadata field produced is consumed by the downstream engine (or explicitly documented as engine-internal)
- [ ] The integrity audit has zero MUST-FIX findings remaining
- [ ] Examples test the rule they claim to illustrate (no hollow examples)

---

## Step 2: Build

**Who:** Claude Code (builder), directed by Claude Chat handoff prompts.
**Duration:** 3-6 sessions (varies by engine complexity).
**Input:** Finalized SPEC, upstream contracts, test fixtures.
**Output:** Working engine code with comprehensive tests.

### 2a. Build Preparation

**Skill:** `use kr-build-prep`

Before Claude Code writes any engine code:

1. **Technology survey** — For each capability that involves an
   external tool or library, verify it exists, works for Arabic, and
   has the specific API the SPEC assumes. This is NOT optional.
   Evidence: the source engine's initial SPEC referenced
   sentence-transformers for Arabic semantic search; actual Arabic
   support was poor. Catching this before build saved a redesign.

2. **Module architecture** — Define the module structure:
   - `src/` — engine implementation (one file per major processing step)
   - `tests/` — test files mirroring src/ structure
   - `prompts/` — LLM prompt templates (if engine uses LLM inference)
   - `contracts.py` — Pydantic models (input, output, internal)
   - `SPEC_CORE.md` — governing specification
   - `CLAUDE.md` — Claude Code orientation (<200 lines)

3. **Test fixture inventory** — List every fixture needed. For each:
   what it tests, where it lives, whether it exists yet or must be
   created. Fixtures are production-quality test data, not throwaway.

4. **Stub architecture** — Write module stubs with:
   - Complete type signatures (input and return types)
   - Docstrings referencing the SPEC section they implement
   - `raise NotImplementedError` bodies
   - These stubs ARE the build plan — Claude Code fills them in.

**Files produced:** `engines/{engine}/CLAUDE.md`, stub files, test
fixture list. Committed to repo before Claude Code starts.

**Self-review (2 rounds):**
- Round 1: For each stub, verify the type signature matches the SPEC.
  Read the SPEC section, then read the stub. Do they agree on input
  types, return types, and optionality?
- Round 2: Trace a single book through ALL stubs in sequence. Does
  the output of stub N match the input of stub N+1? This catches
  phantom metadata (Silent Failure Pattern 4) at the intra-engine
  level.

### 2b. Claude Code Session Design

Split the build into independent, focused Claude Code sessions. Each
session has a single purpose and a clear completion criterion.

**Session design principles (from source engine):**

1. **One concern per session.** The source engine's worst sessions
   tried to do extraction + inference + validation in one prompt.
   The best sessions did one thing well: "implement extraction" or
   "implement the consensus integration" or "write all validation
   checks."

2. **Handoff prompts, not verbal instructions.** Every Claude Code
   session starts by reading a committed markdown file that specifies:
   - What files to read first
   - What to implement (with SPEC section references)
   - What tests to write
   - What NOT to change (explicit exclusion list)
   - Verification commands to run before committing
   - Expected outcome (how to know you're done)

3. **Context budget awareness.** Claude Code has ~1M context. A
   session that reads the full SPEC (1,820 lines) plus all source
   files plus all test files will exhaust context before finishing.
   The handoff prompt must specify exactly which files to read, in
   what order, and which sections of the SPEC are relevant.

4. **Tests alongside code, not after.** Every session that writes
   implementation code also writes tests for that code, in the same
   session. Tests written in a separate session by the same agent
   tend to test what the code does (tautological) rather than what
   the SPEC says it should do.

**Handoff prompt template:**

```markdown
# Claude Code — {Engine} {Module} Implementation

## Context
{1-2 sentences: where we are in the build, what's already done}

## Read First (in this order)
1. `engines/{engine}/CLAUDE.md` — module orientation
2. `engines/{engine}/SPEC_CORE.md` §{section} — governing rules
3. `engines/{engine}/contracts.py` lines {range} — relevant models
4. {any other files}

## Implement
{Specific functions/classes to implement, with SPEC references}

## Tests to Write
{Specific test cases, including negative tests for error paths}

## Do NOT Change
{Explicit list of files/functions that must not be modified}

## Verification
Run: `pytest engines/{engine}/tests/ -v`
Run: `mypy engines/{engine}/src/ --ignore-missing-imports`
Expected: 0 failures, 0 type errors

## After Implementation
Commit with message: "{descriptive message}"
```

**Self-review of handoff prompts (2 rounds):**
- Round 1: Re-read every file referenced in "Read First." Are the
  line ranges still correct? (Files shift after commits.) Are the
  SPEC sections the right ones for the task?
- Round 2: Read the "Implement" section as if you are Claude Code
  seeing it for the first time. Is there any ambiguity about what to
  build? Any place where Claude Code would need to make a judgment
  call not covered by the SPEC?

**Concrete example (adapted from source engine Fix 1 handoff):**

```markdown
# Claude Code — Source Engine Genre Enum Fix

## Context
Post-evaluation fix. The Genre enum is missing 2 values that LLMs
correctly produce, causing valid output to silently fall back to "other".

## Read First (in this order)
1. `engines/source/CLAUDE.md` — module orientation
2. `engines/source/SPEC_CORE.md` §4.A.4 — genre classification rules
3. `engines/source/contracts.py` Genre class — current enum values
4. `engines/source/src/metadata_inference.py` validate_enum_value() —
   the function that silently falls back

## Implement
1. Add RIHLAH="rihlah" and USUL_AL_FIQH="usul_al_fiqh" to Genre enum
   in contracts.py
2. Add both genres to the prompt enum list in prompts/inference_v1.py
3. Add Arabic synonyms to library/config/genre_synonyms.json:
   "رحلة"→"rihlah", "أصول الفقه"→"usul_al_fiqh"
4. Add logging to validate_enum_value when falling back to default
   (SPEC requires this, currently missing)

## Tests to Write
- Test: genre="rihlah" passes validation without fallback
- Test: genre="usul_al_fiqh" passes validation without fallback
- Test: Arabic synonym "رحلة" maps to "rihlah"
- Test: Arabic synonym "أصول الفقه" maps to "usul_al_fiqh"

## Do NOT Change
- shared/consensus/src/consensus.py — consensus module is working
  correctly; this is an enum bug, not a consensus resolution bug
- _select_canonical() in metadata_inference.py — do not modify the
  canonical selection logic

## Verification
Run: pytest engines/source/tests/test_metadata_inference.py -v
Run: mypy engines/source/src/ --ignore-missing-imports
Expected: 0 failures, 0 type errors, new tests pass

## After Implementation
Commit with message: "Fix missing genre enum values (rihlah, usul_al_fiqh)"
```

### 2c. Incremental Build Order

Build from the outside in: contracts first, then extraction/parsing
(deterministic), then LLM inference, then validation, then the engine
orchestrator that ties it all together.

**Recommended session sequence (source engine example — adapt categories per engine):**

The specific modules change per engine, but the DEPENDENCY STRUCTURE
is universal: contracts first → deterministic processing → LLM
inference → consensus → validation → orchestrator → integration.

| Session | Source Engine Example | Adapt to... | Depends on |
|---------|---------------------|-------------|------------|
| 1 | Contracts (Pydantic models) | Same for all engines | Nothing |
| 2 | Deterministic processing (extraction, parsing, hashing) | Normalization: format detection + text normalization. Passaging: boundary detection rules. | Session 1 |
| 3 | LLM prompt templates + inference parsing | Any engine with LLM inference | Session 1 |
| 4 | Consensus integration | Same for any multi-model engine | Session 3 |
| 5 | Validation checks | Same structure, engine-specific checks | Sessions 1-4 |
| 6 | Engine orchestrator | Same for all engines | Sessions 1-5 |
| 7 | Integration tests + mypy cleanup | Same for all engines | Sessions 1-6 |

**Evidence from source engine:** Session 6 (13-fixture integration)
found 4 bugs that unit tests missed because integration tests exercise
the interaction between modules, not just individual functions. The
code audit (Step 1 of validation) found 6 more bugs because it read
code against the SPEC rather than against the tests.

### 2d. Test Requirements

Every engine must have:

1. **Deterministic tests** — No LLM calls. Test extraction, parsing,
   hashing, validation logic, contract serialization. These run in
   CI, cost €0, and catch most bugs.

2. **LLM-worker tests** — Real LLM calls on fixtures. Test prompt
   quality, response parsing, confidence calibration, consensus
   behavior. These cost money and run only on demand.

3. **Negative tests** — Verify that invalid input is rejected, low
   confidence triggers human gates, missing required fields raise
   errors. Evidence from source engine: the code audit found that
   several validation checks were dead code because no negative test
   exercised the error path.

4. **Arabic text tests** — Adversarial inputs: mixed diacritics, NFC
   vs. NFD, Arabic comma (،) vs. Western comma, zero-width joiners,
   truncated UTF-8 sequences. Evidence: the source engine had a
   subtle bug where Arabic comma in nasab chains broke name matching.

5. **Gold baselines** — Hand-verified expected output for a small
   number of fixtures (5-10 books). These are the ground truth for
   regression testing. Gold baselines are NEVER auto-generated — they
   are created by Claude Chat after web-search verification of each
   field.

**Gold baseline self-review (3 rounds):**
- Round 1: For each field in the baseline, document the source (web
  URL, SPEC rule, or manual verification) that confirms the value.
- Round 2: For each author attribution in the baseline, perform an
  independent web search. Does the search confirm the baseline? This
  catches cases where the evaluator's domain knowledge is wrong.
- Round 3: Check Arabic text fields character-by-character against
  the original source. A single wrong diacritic invalidates the
  baseline.

### 2e. Code Audit (Claude Chat, before any pipeline run)

After Claude Code finishes the build but BEFORE running books through
the pipeline, a Claude Chat session reads every module against the SPEC.

**Why this step exists:** The source engine code audit (roadmap Step 1,
commit 4b51718) found 6 bugs that 768 passing unit tests missed. Tests
written by the same agent as the code tend to test what the code does,
not what the SPEC says it should do. A fresh pair of eyes reading code
against the SPEC catches different bugs than tests do.

**Procedure:**
1. Read the full SPEC §4.A (core processing rules)
2. For each rule, read the implementing function in src/
3. Check: does the code do what the SPEC says? Not "is the code
   reasonable?" but "does the code match the SPEC?"
4. Check error handling: does every branch that can fail have a
   defined recovery?
5. Check data flow: are all required fields propagated through the
   processing chain?
6. Document findings as a numbered list with file, function, and
   the specific discrepancy

**Self-review (2 rounds):**
- Round 1: For each "no issues found" module, re-read the most
  complex function and trace one edge-case input through it.
- Round 2: Count total findings. If <3 across the entire engine,
  you are reviewing too superficially. The source engine audit found
  6 bugs in ~1,500 lines of code — roughly 1 per 250 lines.

### Step 2 Completion Criteria

The build is ready for evaluation when:
- [ ] All deterministic tests pass
- [ ] mypy reports 0 errors on all source files
- [ ] At least 5 gold baselines exist with documented sources
- [ ] Every SPEC §4.A capability has at least one test
- [ ] Every SPEC §5 validation check has a positive and negative test
- [ ] The engine processes at least one real book end-to-end without error

---

## Step 3: Evaluate

**Who:** Claude Chat (evaluator), with web search. Claude Code runs
scripts and pipeline. Owner reviews specific escalated questions only.
**Duration:** 4-8 sessions (scales with book count).
**Input:** Built engine, test fixtures, real book collection.
**Output:** Structured evaluation report with per-book verdicts, error
classification, and GO/NO-GO recommendation.

### The 4-Layer Evaluation Methodology

This methodology was developed iteratively during the source engine's
Phase C and Phase D evaluations. It is the proven approach.

#### Layer 1: Programmatic Validation (Claude Code, €0)

Write and run automated checks on ALL processed books. These catch
mechanical errors that don't require domain knowledge:

- **Math verification** — Recompute every calculated field (trust
  scores, confidence aggregates) and compare to pipeline output
- **Internal consistency** — Genre implies multi-layer? Multi-layer
  implies layers present? Attribution status consistent with
  confidence?
- **Contract compliance** — Every output field present, correct type,
  within valid range
- **Regression** — If books were processed in a prior phase, compare
  key fields (no negative regressions allowed)
- **Cross-book consistency** — Same author in multiple books should
  have consistent metadata

**Files produced:** `PHASE_X_TRIAGE.json` — per-book flags sorted by
severity, feeding Layer 2-3 session planning.

**Self-review (2 rounds):**
- Round 1: For each automated check, verify it actually tests what
  it claims. Evidence from source engine: check 5f (BUG-03 tahqiq-note
  override) had zero end-to-end test coverage because the check was
  implemented but never fired on any test book.
- Round 2: Run the checks on a book you've manually verified. Do the
  automated results match your manual assessment?

#### Layer 2: Pattern Analysis (Claude Chat, 1 session)

Analyze programmatic flags as *cohorts*, not individual books. The goal
is to identify engine behavior patterns — systematic biases, prompt
boundary issues, and validation gaps.

**What to analyze:**
- Disagreement clusters: Which fields do the models disagree on most?
  Is there a pattern (e.g., all disagreements involve the same genre
  boundary)?
- Confidence outliers: Which fields consistently have low confidence?
  Is this a calibration issue or genuine uncertainty?
- Error code distribution: Which validation checks fire most often?
  Are they catching real problems or creating false positives?

**Evidence from source engine:** Pattern analysis revealed:
- 39/204 genre disagreements, with 14 clustering on the
  risalah/matn/other boundary (prompt issue, not engine bug)
- 8 ML disagreements, all from Opus tahqiq-note bias (systematic,
  mitigated by BUG-03 override)
- 47/47 attribution disagreements resolved correctly by SPEC §6.3
  (definitive→traditional default — working as designed)

**Files produced:** `PHASE_X_PATTERN_ANALYSIS.md`

**Self-review (2 rounds):**
- Round 1: For each "not a bug" conclusion, state the specific
  evidence. "It's a prompt issue" is not evidence. "14 books share
  the same genre pair (risalah/matn), no structural processing
  differs between them, and the downstream engine treats them
  identically" is evidence.
- Round 2: For each claimed pattern, check: could this be an artifact
  of the book selection rather than a genuine engine behavior? Would
  a different set of books show the same pattern?

#### Layer 3: Per-Book Web Search Verification (Claude Chat, 3-5 sessions)

The most labor-intensive layer. Individually verify a sample of books
using web search, structured by risk tier from Layer 1.

**Adaptation note:** The procedure below is specific to engines that
produce *knowledge output* (author attribution, genre classification,
scholarly metadata) verifiable via web search. For engines that produce
*structural output* (passage boundaries, atom classifications, excerpt
boundaries), Layer 3 replaces web search with manual inspection of
the structural decisions against the source text. The risk-tier
structure and self-review protocol remain the same.

**Session structure — define risk tiers per engine, then assign sessions.**

The source engine used these tiers; other engines define their own:

| Session | Source Engine Tiers | Generalized Principle |
|---------|--------------------|-----------------------|
| A | Consensus disagreements, confirmed errors | **Highest risk:** Items where the pipeline's internal mechanisms disagreed or where Layer 1 found confirmed errors |
| B | No extracted author, low confidence, death date disagreement | **Input uncertainty:** Items where the engine had to infer heavily from sparse input |
| C | ML-affecting genre disagreements, genre-structure inconsistencies | **Structural flags:** Items where the output structure may be internally inconsistent |
| D | Stratified random from unflagged books | **Random calibration:** Unbiased sample. If ANY error found, expand. |

**For the normalization engine,** tiers might be: (A) format detection
failures or fidelity warnings, (B) multi-layer text processing
results, (C) genre-specific normalization strategy choices, (D) random.
**Define the tiers after Layer 1 triage reveals the actual risk distribution.**

**Per-book evaluation procedure:**

1. **Read pipeline data** — All available files: result.json,
   extraction.json, consensus.json, llm_responses/*.json. Know
   exactly which file each field comes from (use the field source
   table from the evaluation protocol).

2. **Compare both models** — Check llm_responses/ for both models.
   Note which fields agree/disagree, which model appears canonical,
   whether the "wrong" model had a reasonable alternative.

3. **Web search verification** — Minimum: 1 search + 1 web_fetch per
   book. Source hierarchy: ar.wikipedia.org (most reliable for
   well-known works) > archive.org > shamela.ws (same ecosystem as
   input, use cautiously) > noor-book.com > hindawi.org. Critical
   rule: shamela.ws, ketabonline.com, turath.io, waqfeya.net count
   collectively as ONE source for VERIFIED threshold.

4. **Write structured verdict** — Use the exact format:

```
### Book N: {title}

- **Status:** {success/gate_abort}
- **Pipeline author:** {name} (d. {death} AH)
- **Author verdict:** VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- **Author source:** {web sources with URLs}
- **Pipeline genre:** {genre} ({confidence})
- **Genre verdict:** VERIFIED/PLAUSIBLE/FLAG
- **Pipeline ML:** {true/false}
- **ML verdict:** VERIFIED/PLAUSIBLE/FLAG
- **Pipeline science:** {list}
- **Science verdict:** VERIFIED/PLAUSIBLE
- **Trust tier:** {verified/flagged} ({score})
- **Death date:** {date AH} — source: pass-through/extracted-from-raw/inferred
- **Model agreement:** {agreed/disagreed on: fields}
- **Overall verdict:** VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE
- **Notes:** {free text}
```

**Verdict scale:**
- **VERIFIED** — 2+ independent web sources confirm. Ground truth candidate.
- **PLAUSIBLE** — 1 source confirms OR extraction cross-check consistent. No red flags.
- **UNVERIFIABLE** — No sources found. Output looks reasonable but unconfirmed.
- **FLAG** — Evidence suggests pipeline may be wrong. Concern documented.
- **ESCALATE** — Cannot resolve. Document for owner review.

**Per-session self-review (5 rounds — this is the gold standard):**

- **Round 1 — Checklist compliance:** All books have web search? All
  use exact 14-field format? Death dates marked pass-through vs.
  inferred? Confidence read from llm_responses (not result.json)?

- **Round 2 — Internal contradictions:** For each book, do the field
  verdicts and the notes tell the same story? A verdict of VERIFIED
  with notes saying "could not confirm independently" is a
  contradiction.

- **Round 3 — Web source verification (CRITICAL):** Were web_fetch
  calls actually performed, not just web_search? Search snippets are
  often insufficient. Evidence from source engine Session A: a
  protocol violation was caught in Round 3 where all verdicts were
  based on search snippets only, never on fetched page content. Two
  books were corrected after retroactive fetching.

- **Round 4 — Death date source tracking:** For every death date,
  verify the source label is correct. "Pass-through" means a
  structured extraction field contained the date. "Extracted from raw
  text" means the date was embedded in author_raw as "(691 - 751)".
  "Inferred" means the LLM supplied it from domain knowledge with no
  extraction support. Evidence from source engine: Round 4 found 3
  books with wrong source labels — a seemingly trivial error that
  would have hidden a systematic hallucination pattern.

- **Round 5 — Post-review corrections:** Apply all fixes from Rounds
  1-4. Update the summary table. Verify totals are correct after
  corrections. Document exactly what changed and why.

**Anti-patterns to avoid (from source engine Phase C):**
1. Accepting imprecise terms without checking domain meaning
2. Counting Shamela-ecosystem as multiple independent sources
3. Inventing verdict categories not in the 5-item scale
4. Internal contradictions introduced by multi-round edits
5. Asserting causation without counterexamples
6. Accepting structural genre (hashiyah) when layer count doesn't match
7. Describing result.json with the wrong model's values

#### Layer 4: Aggregation and GO/NO-GO (Claude Chat, 1-2 sessions)

Read all Layer 2-3 outputs. Compute aggregate statistics. Write the
GO/NO-GO recommendation.

**Aggregation report structure:**

1. **Evaluation coverage** — How many books in each layer, what
   percentage of total received per-book verification
2. **Aggregate verdicts** — Count of VERIFIED/PLAUSIBLE/FLAG/ESCALATE
   per session and total
3. **Error classification** — Confirmed errors (require action) vs.
   flagged issues (need review, may not be errors) vs. escalated
   (owner decision needed). Each error gets: ID, book, type,
   severity, description.
4. **Error rate analysis** — Hard errors / total evaluated. Compare
   to previous phase if applicable.
5. **Pattern findings** — Summary of Layer 2 patterns with assessment
   (working correctly / needs fix / needs investigation)
6. **GO/NO-GO decision** — Against the gate criteria defined in the
   evaluation protocol

**On NO-GO:** Return to the appropriate step. If errors are in SPEC
design → Step 1. If errors are in implementation → Step 2 (with
specific bug fix specs from Step 4a). If errors are in evaluation
coverage → expand Layer 3 scope. Per ENGINE_PROTOCOL Rule 8: do not
patch code without updating the SPEC. A NO-GO is not a failure — it
means the evaluation caught problems before they corrupted the library.

**Mandatory: adversarial review of GO verdict.**

After writing the aggregation report and GO recommendation, a SEPARATE
Claude Chat session (fresh context) performs an adversarial review:

1. Spot-check 3 VERIFIED books (especially any with ERRATA violations)
2. Examine ALL FLAG books — verify flag reasons, check for unflagged
   books that should be flagged
3. Audit the most severe error type found — is it truly isolated or
   is there a systematic pattern?
4. Check books that SHOULD be flagged but weren't — pick 2-3
   unevaluated books with the highest risk profile and verify them
5. Produce a revised bottom line: does GO hold under adversarial
   scrutiny?

Evidence from source engine: the adversarial review found a consensus
module bug (ملء العيبة — pipeline fabricated a genre neither model
proposed) that the original evaluation missed, and upgraded the ERR-03
death date fix scope.

**Self-review (2 rounds):**
- Round 1: For each "not an error" conclusion in the aggregation, state
  the specific evidence. "The evaluator checked it" is not evidence
  if the evaluator had protocol violations.
- Round 2: For the GO verdict specifically: list every assumption
  that must hold for GO to be correct. For each assumption, state
  whether it was verified by tools/searches or accepted on evaluator
  judgment. If >30% are judgment-only, the evaluation is weak.

### Step 3 Completion Criteria

Evaluation is complete when:
- [ ] Layer 1 programmatic checks run on ALL processed books
- [ ] Layer 2 pattern analysis covers all significant flag cohorts
- [ ] Layer 3 per-book verification covers ≥25% of processed books, with ALL Layer 1 flagged books verified before any random sampling begins
- [ ] Layer 4 aggregation includes adversarial review
- [ ] Error classification has clear severity for every finding
- [ ] GO/NO-GO verdict is supported by evidence, not judgment alone

---

## Step 4: Harden and Fix

**Who:** Claude Chat (specification), Claude Code (implementation).
**Duration:** 2-4 sessions.
**Input:** Evaluation report, error classification, pattern analysis.
**Output:** Fixed engine code, updated SPEC, verification evidence.

### 4a. Bug Specification

Claude Chat writes precise fix specifications for Claude Code. This is
NOT a description of the problem — it is a complete implementation
spec that tells Claude Code exactly what to change.

**Fix specification template (from source engine post-eval fixes):**

```markdown
## Fix N: {Title}

### Root Cause (confirmed by code investigation)
{What is actually wrong, traced to specific files and line ranges.
NOT "the validation is too lenient" — instead: "check 5e in
validation.py fires at severity=warning for hashiyah+ML=false,
but hashiyah structurally requires 3 layers, so this should be
severity=gate"}

### Files to Modify
1. **`{file}`** — {what to change, with code snippets if small}
2. **`{file}`** — {what to change}

### Tests to Add
- Test: {input} → {expected output} (confirms fix works)
- Test: {input} → {expected output} (confirms no regression)

### What NOT to Change
{Explicit list. Evidence from source engine: Fix 1 (genre enum) could
have been misdiagnosed as a consensus module bug. The "What NOT to
Change" section preventing consensus module modification was critical
because the actual root cause was a missing enum value, not a
consensus resolution bug.}
```

**Self-review (2 rounds):**
- Round 1: For each fix, re-read the actual code file (not your
  memory of it). Are your line references correct? Does the function
  signature match what you described?
- Round 2: For each fix, ask: "Could this fix break an unrelated
  test? What side effect am I not seeing?" Trace the data flow
  through the fix point and check what else reads/writes the same
  data.

### 4b. Pre-Batch Verification (Zero-Cost Hardening)

Before spending ANY money on re-running the pipeline, exhaust every
zero-cost verification method:

1. **mypy** — Run on all source files. Fix crash risks (null access
   on Optional). Fix contract mismatches (missing required fields).
   Accept type-narrowing issues if runtime-safe.

2. **SPEC-to-code consistency audit** — Read the SPEC, then read the
   code. Do they describe the same behavior? Evidence from source
   engine: 3 inconsistencies found where the code had evolved past
   the SPEC (check 5c was downgraded from gate to warning in code
   but SPEC still said gate) (since fixed in commit 473a7a9 — code
   now matches SPEC).

3. **Contract boundary re-verification** — After fixes, re-run
   `verify_metadata_flow.py`. Did the fixes create any new gaps?

4. **SPEC quality triage** — Run spec quality checker if available.
   Triage HIGH defects as CORRECTNESS (fix now) vs. STYLE (defer).
   Fix only correctness-affecting defects.

**Evidence from source engine:** Every verification layer found bugs
the previous layer missed. Code audit caught what tests missed. mypy
caught what code audit missed. Contract verification caught what mypy
missed. The cheapest, most productive bug-finding happens BEFORE any
books are processed.

### 4c. End-to-End Fix Verification

After Claude Code implements fixes, run a targeted e2e test:

1. Select 1 book per fix that exercises the specific bug
2. Select 1-2 "control" books that should be unaffected
3. Run the full pipeline on these books
4. For each fix: verify the expected behavioral change occurred
5. For control books: verify zero regressions

**Budget:** Cap at €2-3 for e2e verification.

**Self-review (2 rounds):**
- Round 1: Read the actual result.json files (not just the
  verification script's summary). Does the file contain what the
  script claims?
- Round 2: For each control book, compare key fields against the
  previous phase's result. Any unexpected changes (even cosmetic)
  should be investigated.

### 4d. Final Batch (if applicable)

If the engine is the first in a new phase (like the source engine was),
run a final batch to:
1. Validate fixes at scale
2. Produce structured input the next engine needs for development
3. Cover genre/category gaps from earlier phases

**Book selection for final batch:**
- Genres underrepresented in earlier phases
- Structural variants the downstream engine needs (multi-layer, multi-volume)
- Mix of classical and modern works
- Verify every selected book's directory/file name exists in the collection

**Self-review of book selection (2 rounds):**
- Round 1: Pre-mortem — "The batch ran and the downstream engine
  can't use the output. What went wrong?" → verify selection covers
  the downstream engine's needs.
- Round 2: Verify every book directory name against the actual
  collection. A single typo wastes the entire pipeline run for that
  book.

### Step 4 Completion Criteria

Hardening is complete when:
- [ ] All mandatory fixes from evaluation are implemented
- [ ] mypy reports 0 errors
- [ ] SPEC reflects current code behavior (no stale sections)
- [ ] e2e verification passes for each fix
- [ ] Contract boundary verified after fixes
- [ ] Final batch (if applicable) processed and spot-checked

---

## Step 5: Prove Complete

**Note:** ENGINE_PROTOCOL includes completion documentation as the final
substep of Step 4. The Blueprint elevates it to its own step because the
source engine showed this work is substantial — the completion report,
lessons learned, and institutional memory updates took a full session
and benefited from their own self-review.

**Who:** Claude Chat writes completion report. Owner acknowledges.
**Duration:** 1 session.
**Input:** All evaluation reports, fix verification, test results.
**Output:** Completion report, NEXT.md pointing to next engine.

### 5a. Completion Report

Document:
1. **What the engine does** (1 paragraph)
2. **Validation evidence** — test count, book count per phase, fix
   verification results
3. **Known limitations** — accepted issues that don't block downstream
4. **Output for downstream engine** — how many records, what diversity,
   where they live
5. **Human gate design note** — how gate resolution works (owner is
   decision authority, not domain researcher)

### 5b. Lessons Learned

Every engine produces `engines/{engine}/LESSONS.md`:

```markdown
# {Engine} Lessons Learned

## Bugs Found
- **[BUG-001] Description**: What, which books affected, fix commit

## Patterns Observed
- Pattern: description
- Implication: what downstream engines should know

## What Went Wrong
- Anything that wasted time, money, or produced misleading results

## What Worked
- Approaches or tools that performed better than expected

## Recommendations for Next Engine
- Specific things the next session's agent should do differently

## Impact on Downstream Engines
- Field distributions, quality patterns, structural variants
```

### 5c. Update Institutional Memory

1. Add new trigger→action pairs to `reference/DECISION_PLAYBOOK.md`
2. Add new silent failure patterns to `reference/SILENT_FAILURES.md` if discovered
3. Update `reference/KNOWLEDGE_INTEGRITY.md` if new corruption threats emerged
4. Update `reference/RESULT_PRESERVATION.md` if result structure evolved
5. Update NEXT.md to point to the next engine

**Self-review (2 rounds):**
- Round 1: Re-read the completion report as if you are the next
  engine's architect seeing it for the first time. Does it contain
  everything you would need to know? Or does it assume context that
  a fresh session wouldn't have?
- Round 2: Check the "known limitations" section. Is every limitation
  genuinely acceptable, or is one of them a bug you're rationalizing?
  For each limitation, state the specific evidence that it doesn't
  block the downstream engine.

---

## Cross-Cutting Protocols

### Session Handoff

Sessions hand off via NEXT.md and committed handoff files. NEXT.md
always contains:

```markdown
## Current position: {Step N} — {Subtask}
## What to do: {exact instruction}
## Context: {state from previous subtask}
## Owner action needed: {yes/no, what}
```

**Evidence from source engine:** The source engine build spanned ~118
commits touching the source engine directory (engines/source/), across many sessions. Every session started by reading
NEXT.md. Sessions that diverged from NEXT.md's directive wasted time.
Sessions that updated NEXT.md before ending enabled clean handoffs.

### Result Preservation

Every pipeline run follows `reference/RESULT_PRESERVATION.md`:

1. **Save everything:** Raw LLM responses, extraction intermediates,
   full output records, per-field confidence, consensus details,
   human gate checkpoints, file hashes.
2. **Phase manifests:** After each phase, produce a manifest listing
   every book processed with status and needs_rerun flag.
3. **Skip already-processed:** Later phases read the manifest and skip
   books with status=success and needs_rerun=false.
4. **Targeted re-runs only:** When a bug is found, mark only affected
   books as needs_rerun=true. Never blanket re-run.

### Budget Discipline

- Track every euro in `COST_LOG.json`
- Estimate cost before every pipeline run: (book_count × cost_per_book)
- Set a budget cap on every Claude Code session
- The 5-layer budget protection system from the source engine:
  per-call cap, per-book cap, per-session cap, cumulative cap, and
  kill-switch file

### Arabic Text Rules

Apply everywhere Arabic text is processed:

1. NFC Unicode normalization only — never NFD, never NFKC
2. Preserve all diacritics exactly
3. Primary text is NEVER modified after extraction
4. Arabic comma (،) must be handled in name matching
5. Encoding is always UTF-8
6. Test with adversarial inputs: mixed diacritics, rare codepoints,
   zero-width joiners

### When Things Go Wrong

Recovery paths for common failure states. If none apply, document the
situation in the engine's LESSONS.md and escalate to the owner.

**Contract incompatibility between adjacent engines.** Not a field name
mismatch (fixable) but a fundamental schema shape disagreement — one
produces a flat record, the other expects a nested tree. Fix: update
the SPEC of the engine with the less-justified design. Re-verify the
boundary. Do not proceed until the boundary passes Pydantic validation.

**LLM accuracy <70% on a core task (discovered in Step 2 or Step 3).**
The SPEC's approach doesn't work. Fix: redesign — options include a
different prompt strategy, a two-stage pipeline (LLM proposes, rules
verify), a lookup table for known values, or reclassifying the task as
always-human-gated. If no approach reaches 70% after 3 attempts,
escalate: "This task cannot be reliably automated. Accept the error
rate with mandatory review?"

**Claude Code session exhausts context mid-build.** Fix: before
context gets tight (>70% usage), commit all work, write a handoff
file at `engines/{engine}/docs/HANDOFF_{date}.md` describing: what's
built, what's tested, what's next, what decisions were made.

**Step 3 evaluation produces NO-GO verdict.** This means confirmed
errors in core functionality. Fix: return to the appropriate step.
If the error is in SPEC design → Step 1 (write a comment, resolve,
update SPEC). If the error is in implementation → Step 2 (fix code).
If the error is in validation coverage → expand Step 3 scope. Do not
patch code without updating the SPEC (ENGINE_PROTOCOL Rule 8).
Evidence from source engine: ERR-01 (hashiyah/ML validation gap) was
a SPEC-level fix; Fix-1 (missing genre enum) was an implementation
fix; both were identified in evaluation and fixed in Step 4.

**Pipeline integration test fails.** The engine's output breaks the
downstream stub. Fix: first verify the output matches its own
contracts.py. If it does, the boundary contract is wrong — update
both engines. If it doesn't, the engine has a bug — fix and re-test.

**Owner not providing domain comments.** Step 1b benefits from owner
input but does not hard-block. Fix: after 3 days with no comments,
proceed with best assessment, mark domain-dependent decisions as
`[OWNER REVIEW PENDING]`, and add cross-provider verification for
those decisions. This does NOT apply to preference gates (edition
choice, curriculum decisions), which block until the owner responds
per reference/KNOWLEDGE_INTEGRITY.md Invariant 5.

**Misleading error messages during pipeline runs.** Evidence from
source engine: BUG-C03 was initially reported as "Command A
unavailable" based on stderr timeout messages. Actual data showed
67/73 books used Command A successfully — the timeouts were retries
on a minority of attempts. Fix: always verify error claims against
actual output data (check the files, not the logs).

---

## Review Protocol Summary

Every output in this Blueprint has a self-review protocol. Here is the
minimum standard, regardless of what the specific step says:

**Minimum: 2 rounds.**

**Critical: Production and review must be separate cognitive acts.**
The source engine's pre-batch execution protocol enforced this by
splitting every task into subtask A (do the work) and subtask B
(review the work), with the owner saying "continue" between them.
This forces a context break — you cannot review work you just
produced in the same mental flow. In practice: finish the work, stop,
re-read NEXT.md, then start the review as if you are a different
agent seeing this work for the first time.

- **Round 1 — Tool-grounded verification.** Do NOT just re-read your
  output. USE TOOLS: re-read source files your work references,
  re-run scripts that verify your claims, web-search to verify
  factual claims. List every claim in your output. For each: how do
  you KNOW this? If "I inferred it," verify with a tool.

- **Round 2 — Adversarial challenge.** For each conclusion: "What is
  the strongest argument this is wrong?" "What would I see if the
  opposite were true?" "What am I assuming that I haven't verified?"

**Elevated: 5 rounds (for per-book evaluation verdicts and gold baselines).**

Rounds 1-2 as above, plus:
- Round 3: Verify web sources were fetched, not just searched
- Round 4: Verify source labels (pass-through vs. inferred vs. extracted)
- Round 5: Apply all corrections, update summary tables, verify totals

**The Session A example.** `reference/archive/sessions/phase_d/PHASE_D_SESSION_A_REPORT.md` is the gold
standard. Round 3 caught a protocol violation (no web_fetch performed).
Round 4 caught wrong death date source labels on 3 books. Round 5
applied corrections that changed 6 books' data and rewrote Round 3 to
honestly document the violation. Without this protocol, the evaluation
would have contained 3 wrong source labels, 1 wrong verdict, and 1
undisclosed protocol violation. Each of these would have propagated as
institutional memory into future evaluations.

---

## Scaling Guidance

Not every engine needs the full treatment at full depth. The source
engine was the first build — it discovered the methodology as it went.
Later engines benefit from that methodology being established but may
not need every step at the same intensity.

**Full treatment (source engine level):**
- Engines with complex LLM tasks (source, excerpting, synthesis)
- Engines where errors cascade into knowledge corruption
- The first engine built in any new phase

**Compressed treatment:**
- Engines with simple cores (passaging, taxonomy in core-only mode)
- Engines where the primary work is deterministic (hashing, formatting)
- Steps 1-2 can compress to 2-3 sessions combined when the core is
  well-understood and the SPEC is mature
- Steps 3-4 maintain the same rigor regardless — the build may be
  faster but the evaluation cannot be shallower

**What "compressed" means concretely:**
- Step 1: Skip 1b (owner comments) if no domain-sensitive decisions.
  Combine 1a + 1c into a single pass if defect count is low (<10).
- Step 2: Combine sessions when modules are small. A simple engine
  might need 2-3 sessions instead of 7.
- Step 3: Layer 3 (per-book verification) can use a smaller sample
  (15-20% instead of 25-30%) IF Layer 1 programmatic checks are
  comprehensive and Layer 2 pattern analysis finds no concerning
  patterns. Never skip Layer 4 (aggregation + adversarial review).
- Step 4: May not need a "final batch" if the evaluation already
  covers enough books for downstream engine development.

---

## Engine-Specific Notes

This section captures specific guidance for each remaining engine,
based on what the source engine learned about their needs.

### Normalization Engine (next)

- **Input:** 209 real SourceMetadata records from source engine Phase
  C, D, and e2e validation
- **Key challenge:** Multi-layer text detection and per-layer
  processing (20 multi-layer books in Phase D output)
- **Watch for:** Genre→processing-strategy mapping. Source engine
  learned that genre boundaries (risalah/matn/other) are fuzzy.
  Normalization should not assume genre is always correct — use genre
  as a hint, not a gate.
- **Contract boundary:** 12 fields verified (9 declared + 3 undeclared
  dependencies) in `reference/CONTRACT_VERIFICATION_REPORT.md`. Death
  dates available via `confidence_scores` path, not
  `author.death_date_hijri`.

### Subsequent Engines

- **Passaging:** Source engine's `structural_format` field (prose/
  verse/commentary/mixed) determines passage boundary strategy.
  Test with all 4 format types.
- **Atomization:** First engine where LLM does the primary work.
  Step 2 research on LLM accuracy for scholarly function
  classification is critical — if <70%, redesign before building.
- **Taxonomy:** Needs a parsed science tree BEFORE Step 3. The
  architect generates the tree; the owner validates experientially.

---

## What This Blueprint Does NOT Cover

1. **Stage 2 expansion** — Adding non-core capabilities. To be
   defined. Extension hooks documented in each engine's §4.B.
2. **Agent team architecture** — Autonomous builder + researcher
   agents. Discussion pending. See NEXT.md.
3. **The abstract ENGINE_PROTOCOL** — This Blueprint is the concrete
   implementation. ENGINE_PROTOCOL (`skills/shared/ENGINE_PROTOCOL.md`)
   remains as the governing framework. Note: ENGINE_PROTOCOL defines
   4 steps where the Blueprint uses 5 — the Blueprint elevates
   completion documentation to its own Step 5.
4. **The ENGINE_FACTORY_PLAN** — Deferred as over-engineered.
   Previous draft archived.
