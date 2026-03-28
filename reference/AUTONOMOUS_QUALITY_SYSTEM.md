# KR Autonomous Quality System — نظام الجودة المستقل

**Authority:** GOVERNING for factory operational behavior. Complements `FACTORY_ROADMAP_v2.md` (which covers setup). This document covers **ongoing operation** — what the factory does with every minute of runtime, forever.
**Written:** 2026-03-28
**Design principle:** The factory is a knowledge guardian that continuously hunts for corruption, tests edge cases, and hardens the pipeline. Building engines is one of its activities, not its identity. When there is nothing to build, the factory does not idle — it hunts.

---

## The Axiom

Every hour the factory runs without actively hunting for bugs is an hour where a corruption pattern might exist undiscovered. The pipeline processes Arabic scholarly texts that become the owner's knowledge. An undiscovered bug is not a technical debt item — it is a wrong belief waiting to be learned. The factory's job is to find that bug before the owner reads the output.

---

## Operating Modes

The factory has six modes. At any given moment, exactly one mode is active. The orchestrator selects the mode based on what work exists. **Hunt is the default.** The factory never idles.

### Mode 1: BUILD

**Trigger:** A SPEC exists in `work_queue/` with type `implement`.
**What happens:** CC implements SPEC sections as work units. Codex reviews. Gemini challenges. Standard build pipeline from FACTORY_ROADMAP_v2.md.
**Priority:** HIGH when triggered (SPECs are human-authored and represent deliberate decisions).
**Exit condition:** All work units for the SPEC are complete, reviewed, and owner-approved.
**Time allocation:** ~5-15% of total factory runtime over a year (building is fast; hardening is permanent).

### Mode 2: HUNT

**Trigger:** No BUILD or FIX work exists. This is the **default mode**.
**What happens:** The factory generates synthetic adversarial data designed to trigger specific corruption threats, runs it through the pipeline, and compares output against known-correct ground truth. Findings are documented, never fixed in the same session.
**Priority:** HIGHEST default priority. When there's nothing else to do, the factory hunts.
**Exit condition:** Never. Hunting is continuous. Each cycle picks a threat type, generates synthetic data for it, and runs the test.
**Time allocation:** ~50-60% of total factory runtime.

### Mode 3: FIX

**Trigger:** `findings_queue/pending/` contains unresolved findings with severity CRITICAL or HIGH.
**What happens:** A dedicated CC session fixes ONE finding. The fix is reviewed by Codex and challenged by Gemini. The full regression suite runs. The synthetic case that found the bug becomes a permanent test.
**Priority:** HIGH — above HUNT because a known bug is more dangerous than an unknown one.
**Exit condition:** The finding is resolved (fix committed + regression test added + full suite passes).
**Time allocation:** ~15-20% of total factory runtime.
**Strict separation:** The CC session that fixes NEVER hunts. The CC session that hunts NEVER fixes. This prevents "make the failing test pass" optimization — the fixer must understand root cause because it doesn't control what gets tested.

### Mode 4: EVALUATE

**Trigger:** Pipeline has produced output on real data that the owner hasn't reviewed yet.
**What happens:** The factory prepares evaluation packets — formatted Arabic excerpts with metadata, highlighted areas of uncertainty, comparison with synthetic test expectations. These go to `human_gate/pending/` for the owner.
**Priority:** MEDIUM — below BUILD and FIX, above routine hunting.
**Time allocation:** ~5-10% of total factory runtime.

### Mode 5: CROSS-ENGINE

**Trigger:** Scheduled (weekly) or after any engine modification.
**What happens:** The factory generates synthetic output from engine N that is technically valid but designed to stress engine N+1's assumptions. Tests every adjacent pair: source→normalization, normalization→excerpting, excerpting→taxonomy, taxonomy→synthesis. Also tests full-pipeline synthetic books that traverse all engines.
**Priority:** MEDIUM — runs weekly or after changes.
**Time allocation:** ~5-10% of total factory runtime.

### Mode 6: BENCHMARK

**Trigger:** Scheduled (monthly), after model updates, or after routing table staleness exceeds 90 days.
**What happens:** Re-runs the benchmark suite against all CLIs. Updates routing table. Detects model capability drift.
**Priority:** LOW — runs monthly.
**Time allocation:** ~2-5% of total factory runtime.

### Mode priority when multiple modes have work:

```
FIX (known bugs) > BUILD (SPECs) > EVALUATE (owner review prep) > HUNT (default) > CROSS-ENGINE (weekly) > BENCHMARK (monthly)
```

FIX is above BUILD because: a known corruption bug in the existing pipeline is more dangerous than an unbuilt SPEC section. The existing pipeline may be producing output the owner is reading RIGHT NOW. The unbuilt SPEC section has no output yet.

---

## The Synthetic Adversarial Data System

This is the heart of the quality system. Without it, the factory only catches bugs that real data happens to trigger. With it, the factory systematically probes every known failure mode.

### Architecture

```
┌─────────────────────────────────────────────┐
│           THREAT TEMPLATE LIBRARY            │
│  One template per threat (T-1 through T-7)  │
│  + cross-engine boundary templates           │
│  + full-pipeline templates                   │
│  Designed by: Architect (Claude Chat)        │
│  Written as: structured JSON specifications  │
└──────────────────────┬──────────────────────┘
                       │
           ┌───────────▼───────────┐
           │   SYNTHETIC GENERATOR │
           │   Codex CLI or        │
           │   Gemini CLI          │
           │   (NEVER Claude Code) │
           │   Fills templates     │
           │   with Arabic content │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │   GROUND TRUTH        │
           │   Known at generation │
           │   time because WE     │
           │   designed the input  │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │   PIPELINE EXECUTION  │
           │   Run synthetic data  │
           │   through target      │
           │   engine(s)           │
           └───────────┬───────────┘
                       │
           ┌───────────▼───────────┐
           │   COMPARISON          │
           │   Actual output vs    │
           │   ground truth        │
           │   Automated scoring   │
           └───────────┬───────────┘
                       │
              ┌────────▼────────┐
              │ PASS: record    │
              │ FAIL: → finding │
              └─────────────────┘
```

### Why Codex/Gemini generate and CC processes (not the other way around)

CC built the pipeline. If CC also generates the test data, it will unconsciously generate data that its own pipeline handles well — same reasoning patterns, same assumptions, same blind spots. Codex and Gemini have different training data and different biases. Their synthetic data is more likely to probe CC's blind spots.

This is the knowledge-diversity principle (D-F002) applied to test generation, not just code review.

### Threat templates

Each template is a JSON specification that describes:
- Which threat it tests (T-1 through T-7)
- The structure of the synthetic input (what the text should contain)
- The trap (what makes this input dangerous)
- The ground truth (what correct processing produces)
- The failure signature (what incorrect processing produces)

#### T-1: Silent Text Corruption

```
Template: Generate a 2-page Arabic scholarly text where a single diacritic
change in paragraph 3 reverses the meaning of a legal ruling.
Trap: The diacritically-sensitive word is inside a long sentence that reads
fluently either way.
Ground truth: The pipeline preserves the exact diacritics from the frozen source.
Failure signature: Diacritics are dropped or normalized, changing the meaning.
Variations: test with tashkeel, with hamza variants, with ta marbuta/ha.
```

#### T-2: Attribution Error (Decontextualization)

```
Template: Generate a 3-page multi-layer text where Scholar A quotes Scholar B's
position in order to refute it. The quote and the refutation are on the same
page but separated by a footnote or editorial comment.
Trap: If the excerpting engine splits them into separate teaching units, the
owner reads Scholar A's quote as if Scholar A HOLDS that position.
Ground truth: The quote and refutation are kept together in one teaching unit,
or the quote is annotated with "quoted for refutation."
Failure signature: Two separate excerpts — one showing Scholar A "stating"
Scholar B's position, one showing the refutation without its target.
Variations: separated by 1 paragraph, by 2 pages, by a footnote, by a
different author's comment in a hashiyah layer.
```

#### T-3: Taxonomic Misplacement

```
Template: Generate an excerpt that discusses a concept that exists in two
different sciences (e.g., "niyyah" appears in both worship and contracts).
Trap: The excerpt discusses niyyah in the context of trade contracts, but uses
terminology common to worship discussions.
Ground truth: Placed under contracts, not worship.
Failure signature: Placed under worship because the terminology triggered the
wrong classification.
Variations: cross-science terms, ambiguous chapter headings, misleading keywords.
```

#### T-4: Context Loss (Self-Containment Failure)

```
Template: Generate a text where a ruling depends on a condition stated 3
paragraphs earlier. The ruling paragraph says "the ruling is as we mentioned"
with a back-reference but no inline restatement.
Trap: If excerpted alone, the ruling is meaningless — "as we mentioned" has
no referent.
Ground truth: Either (a) the excerpt includes the referenced condition, or
(b) the self_containment_context field supplies it.
Failure signature: Excerpt passes self-containment check but the reader
cannot understand what "as we mentioned" refers to.
Variations: back-references by pronoun, by "above", by "as stated in the
first chapter", by implicit assumption.
```

#### T-5: Synthesis Hallucination

```
Template: Provide 4 excerpts where 3 scholars agree on a position and 1
disagrees. The dissenting scholar uses subtle language (not explicit refutation
but careful qualification).
Trap: The synthesizer flattens this into "scholars agree" because 3>1 and the
dissent is subtle.
Ground truth: Synthesis mentions all 4 positions, noting the qualification.
Failure signature: "Scholars unanimously agree..." or the dissenting position
is omitted entirely.
Variations: dissent via qualification, via exception, via silence (not
mentioning what others mention), via different scope definition.
```

#### T-6: Metadata Poisoning

```
Template: Generate a source where the title page says "Hanafi fiqh" but the
actual content discusses a Shafi'i position extensively (because the Hanafi
author is responding to Shafi'i arguments).
Trap: The pipeline tags the entire source as "Hanafi" and all excerpts inherit
this tag, including the pages where Shafi'i positions are presented.
Ground truth: Per-excerpt school attribution, not per-source.
Failure signature: A Shafi'i position attributed to the Hanafi school because
the source-level metadata propagated incorrectly.
Variations: multiple schools discussed, compiler vs author school mismatch,
muhaqiq's notes misattributed to original author.
```

#### T-7: Duplication and Contradiction

```
Template: Generate the same passage appearing in two different sources with
slightly different wording (one has an extra sentence, one uses a synonym).
Trap: The pipeline treats these as two different excerpts and they end up at
the same taxonomy node with contradictory metadata.
Ground truth: Duplicate detection identifies them as the same passage.
Variations: verbatim duplicate, near-duplicate with added footnotes,
same content in different editions with different pagination.
```

#### Cross-engine boundary templates

```
Template: Generate normalized output that is technically valid per the
normalization contract but has unusual structure — very short pages,
pages with only footnotes, pages where the primary text is entirely
inside a table, pages with mixed RTL/LTR content.
Trap: The excerpting engine assumes "normal" page structure.
Ground truth: Excerpting handles every valid normalized format correctly.
Failure signature: Crash, silent data loss, or garbled output.
```

#### Full-pipeline template

```
Template: Generate a complete synthetic book (20-30 pages) with known
properties: specific author, specific school, multi-layer structure,
known excerpts with known topics, known taxonomy placements.
Process through the entire pipeline: source → normalization → excerpting
→ taxonomy → synthesis.
Ground truth: Every property survives the full pipeline intact.
Failure signature: Any property is lost, changed, or corrupted at any stage.
This is the ultimate integration test — it tests what the owner actually
experiences.
```

### Generating synthetic data — the concrete process

Each HUNT cycle:

1. The orchestrator selects a threat type. Selection is **coverage-weighted**: threats with fewer synthetic test cases get selected more often. This ensures systematic coverage rather than random exploration.

2. The orchestrator selects a template and variation for that threat type.

3. The orchestrator dispatches Codex CLI (or Gemini CLI, alternating) with a generation prompt:
   ```
   Generate a synthetic Arabic scholarly text that matches this specification:
   [template JSON]
   
   Requirements:
   - The Arabic must be grammatically correct classical Arabic
   - The scholarly structure must be realistic (not obviously fake)
   - The text must be 1-3 pages
   - Include the ground truth answer in your response
   
   Output format:
   {
     "synthetic_text": "...",
     "ground_truth": { ... },
     "threat_type": "T-2",
     "variation": "separated by footnote",
     "difficulty": "hard"
   }
   ```

4. The orchestrator validates the synthetic data (well-formed JSON, Arabic text present, ground truth specified).

5. The orchestrator formats the synthetic data as pipeline input (mimicking the format the target engine expects).

6. The orchestrator dispatches CC to process it: `claude -p "Process this input through the excerpting engine phase 1. Output the result as JSON." --output-format json`

7. The orchestrator compares the actual output against the ground truth using automated scoring (exact match for metadata, semantic comparison for text boundaries).

8. PASS → record in `synthetic_tests/results/`. FAIL → create finding in `findings_queue/pending/`.

---

## The Findings Lifecycle

Every finding flows through a structured lifecycle. No finding is ever "acknowledged and deferred." Every finding is either resolved or actively being worked on.

### Finding structure

```json
{
  "finding_id": "F-2026-0342",
  "discovered_at": "2026-04-15T03:22:00Z",
  "discovered_by": "hunt_cycle_847",
  "threat_type": "T-2",
  "engine": "excerpting",
  "severity": "CRITICAL",
  "epistemic_impact": "Owner would read Scholar A as holding a position he actually refutes",
  "synthetic_input_id": "syn-T2-047",
  "expected_output": { ... },
  "actual_output": { ... },
  "divergence_description": "Refutation separated from target position into different teaching units",
  "status": "pending_fix",
  "fix_commit": null,
  "regression_test_id": null,
  "pattern_id": "PAT-T2-separation",
  "spec_amendment": null,
  "benchmark_case_added": false
}
```

### Lifecycle stages

```
DISCOVERED → CLASSIFIED → TRIAGED → FIXING → FIXED → VERIFIED → HARDENED
```

**DISCOVERED:** The hunt cycle found a divergence. An automated classifier assigns threat type and severity based on the template's threat mapping. The finding enters `findings_queue/pending/`.

**CLASSIFIED:** The orchestrator enriches the finding: which engine, which SPEC section, which code path. Codex and Gemini independently assess severity. If they disagree on severity, the higher severity wins.

**TRIAGED:** The orchestrator sorts pending findings by severity. CRITICAL findings jump to the front of the FIX queue. The owner sees all findings on the dashboard, but only CRITICAL/HIGH findings require their attention.

**FIXING:** A dedicated CC session receives the finding, the synthetic input, the expected output, and the actual output. CC diagnoses root cause and implements a fix. The fix session produces:
- The code change
- A root cause analysis (which assumption was wrong?)
- A pattern entry (what class of input triggers this?)

**FIXED:** The fix is committed. Codex reviews the fix. Gemini challenges it. Both must agree the root cause was addressed (not just the symptom patched). If either disagrees, the finding returns to FIXING with their feedback.

**VERIFIED:** Full regression suite runs. The synthetic case that found the bug passes. No other tests broke. The fix is merged.

**HARDENED:** The finding produces five outputs:
1. **Regression test:** The synthetic case becomes a permanent test in the engine's test suite. This bug can never return without being detected.
2. **Pattern entry:** Added to `findings_db/patterns/`. The pattern describes the CLASS of input that triggers this failure (e.g., "any multi-layer text where a refutation is separated from its target by >1 paragraph"). Future hunt cycles use patterns to generate MORE synthetic data in this class.
3. **SPEC amendment recommendation:** If the SPEC doesn't cover this edge case, a recommendation is queued for the architect. The architect (Claude Chat) decides whether to amend the SPEC.
4. **Benchmark case:** If the finding tests model capability (not just code logic), it's added to the benchmark suite.
5. **Metric data point:** The finding is recorded in `findings_db/metrics/` — threat type, engine, severity, time-to-fix, discovery method. These metrics track quality trends over time.

---

## The Findings Database

Not a traditional database — a structured directory in the repo.

```
findings_db/
  pending/           ← findings awaiting fix
  in_progress/       ← findings being fixed (one at a time)
  resolved/          ← fixed and verified findings
  patterns/          ← discovered failure patterns
  metrics/           ← quality trend data
  synthetic_library/ ← all synthetic test cases (permanent)
    T-1/             ← per threat type
    T-2/
    ...
    cross-engine/
    full-pipeline/
  regression_tests/  ← generated regression tests (copied into engine test suites)
```

The `synthetic_library/` is the system's immune memory. It grows continuously. Every bug that was ever found has a synthetic case that prevents it from returning. After 6 months of hunting, the library contains hundreds of adversarial cases covering every known failure pattern. After a year, thousands. The pipeline gets HARDER to break over time, not easier.

### Metrics tracked

- **Findings per threat type per month:** Which threats are we weakest on?
- **Findings per engine per month:** Which engine has the most bugs?
- **Time to fix:** How long from discovery to resolution?
- **Regression rate:** How often do fixes break other things?
- **Hunt yield:** What fraction of hunt cycles find bugs? (Declining yield = improving quality)
- **Coverage map:** Which threat×engine combinations have the most synthetic tests? Which have the fewest? (Directs future hunting)

These metrics appear on the owner's dashboard. A rising finding rate in a specific threat type is an early warning. A declining hunt yield is evidence of improving quality.

---

## The Quality Maturity Model

Five levels, each with concrete exit criteria. The factory tracks which level each engine has reached.

### Level 1: Basic coverage
- Every threat type (T-1 through T-7) has ≥5 synthetic test cases for this engine
- All pass
- All cross-engine boundaries for this engine have ≥3 adversarial cases
- All pass

### Level 2: Systematic coverage
- Every threat type has ≥20 synthetic test cases including ≥5 adversarial variations per template
- All pass
- Cross-engine boundaries have ≥10 cases each
- The findings database has pattern entries for every threat type
- At least one full-pipeline synthetic book has been processed without errors

### Level 3: Adversarial hardening
- Every threat type has ≥50 synthetic test cases
- The hunt yield (fraction of cycles finding new bugs) is below 10%
- Every pattern in the findings database has ≥3 regression tests
- Cross-provider adversarial data generation has been used (Codex generates data that Gemini designed the template for, and vice versa)
- Five full-pipeline synthetic books have been processed without errors

### Level 4: Production confidence
- Hunt yield below 5% sustained over 30 consecutive hunt days
- Zero CRITICAL findings in the last 60 days
- The owner has reviewed real pipeline output for this engine (Arabic review gate passed)
- Every SPEC section has ≥1 synthetic test case directly testing it
- Cross-engine boundary tests include cases designed by patterns from other engines' findings

### Level 5: Sustained quality
- Three consecutive monthly full-audit cycles find zero CRITICAL or HIGH findings
- Hunt yield below 2%
- The synthetic library has >200 cases for this engine
- The owner has reviewed output from ≥30 diverse books
- No silent failure patterns from `SILENT_FAILURES.md` have been triggered in 90 days

**Level 5 does not mean "done."** Hunting continues indefinitely. Level 5 means "confident enough that the owner can read this engine's output and trust it." The hunting continues because models update, edge cases are infinite, and the threat landscape evolves.

---

## Cross-Engine Boundary Testing

Adjacent engines communicate via contracts (defined in each engine's `contracts.py`). A bug at the boundary — where engine N's output meets engine N+1's input — is especially dangerous because both engines' internal tests pass while the interaction fails.

### Test strategy per boundary

**Source → Normalization:**
- Source output with unusual HTML structures (deeply nested tables, inline CSS, mixed encodings)
- Source output with minimal metadata (only title, no author — how does normalization handle missing fields?)
- Source output with conflicting metadata (title says one author, footer says another)

**Normalization → Excerpting:**
- Normalized pages with zero text content (only images or tables)
- Normalized pages with extremely long paragraphs (>5000 characters)
- Normalized pages where the page boundary splits a sentence mid-word
- Normalized output with unusual Unicode (rare Arabic characters, mathematical Arabic, Ottoman Turkish in Arabic script)

**Excerpting → Taxonomy:**
- Excerpts with ambiguous topic classification (could belong to multiple taxonomy nodes)
- Excerpts with self_containment_context that references content not in the excerpt
- Excerpts with extremely high or low confidence scores
- Excerpts with empty or malformed metadata fields

**Taxonomy → Synthesis:**
- Taxonomy nodes with only one excerpt (can a synthesis be meaningful?)
- Taxonomy nodes with 100+ excerpts (does synthesis handle scale?)
- Excerpts from sources that contradict each other at the same node
- Excerpts where all agree (does synthesis add value or just repeat?)

### Execution

Cross-engine tests run weekly (Mode 5). The orchestrator:
1. Selects a boundary and a test template
2. Generates synthetic output from engine N (using Codex/Gemini)
3. Feeds it into engine N+1 (using CC)
4. Compares against expected behavior
5. Findings enter the same lifecycle as hunt findings

---

## Full-Pipeline Synthetic Books

The ultimate test: a complete synthetic book with known properties, processed through every engine from source to synthesis.

### Construction

1. The architect designs a synthetic book specification:
   - Title, author, school, genre, era
   - Multi-layer structure (matn + sharh + hashiyah if applicable)
   - Known excerpts at known positions
   - Known topics for taxonomy placement
   - Known inter-scholar relationships (agreement, refutation, qualification)
   - Embedded traps: one T-2 decontextualization, one T-5 synthesis risk, one cross-engine stress case

2. Codex/Gemini generates the Arabic content according to the specification

3. The orchestrator processes it through the full pipeline

4. Every property is checked at every stage:
   - Source: metadata extracted correctly?
   - Normalization: text preserved, layers identified?
   - Excerpting: teaching units correct, self-contained, attributed correctly?
   - Taxonomy: placed at correct nodes?
   - Synthesis: disagreements preserved, attributions correct, no hallucination?

5. The ground truth for the entire pipeline is known at generation time. Every divergence is a finding.

### Cadence

- One full-pipeline book per week during Level 1-2
- Two per week during Level 3
- Five during Level 4 push
- Monthly maintenance runs at Level 5

---

## Integration with FACTORY_ROADMAP_v2.md

### New sessions required

**Session 4.5 (NEW) — Synthetic Data Infrastructure**
Added between benchmark (Session 4) and benchmark run (Session 5).

CC builds:
- `synthetic_tests/` directory structure
- `scripts/synthetic_generator.py` — dispatches Codex/Gemini with threat templates, validates output
- `scripts/synthetic_runner.py` — runs synthetic data through target engine, compares against ground truth
- `scripts/finding_classifier.py` — auto-classifies findings by threat type and severity
- `findings_db/` directory structure
- `findings_db/templates/` — the threat template library (T-1 through T-7 + cross-engine + full-pipeline)
- 7 initial threat templates (one per threat type) designed by the architect

**Session 6 amendment — Orchestrator modes**
Session 6 now also implements the six operating modes and the priority selection logic. When the orchestrator wakes and has no BUILD or FIX work, it automatically enters HUNT mode.

**Session 8 amendment — Dashboard additions**
The dashboard includes: findings count by threat type, hunt yield trend, quality maturity level per engine, synthetic library size, coverage map (which threat×engine combinations have the most/fewest tests).

**Session 10 amendment — Sustained hunting**
Session 10's health monitoring includes hunt yield trends, finding rates, and maturity level tracking. The factory self-test includes a mini hunt cycle to verify the hunting infrastructure works.

### Revised session plan (complete)

| Session | Content | Effort |
|---------|---------|--------|
| 1 | Operational truth + doc reconciliation | 1 session |
| 2 | CI/CD + policies + hook fixes + hook overhead docs | 1 session |
| 2.5 | WSL setup (owner) | Owner time |
| 3 | CLI abstraction + extend orchestrator + Gemini dispatch | 1-2 sessions |
| 4 | Benchmark design (Codex+Gemini design, owner verifies) | 2 sessions |
| **4.5** | **Synthetic data infrastructure + threat templates + findings DB** | **1-2 sessions** |
| 5 | Run benchmark + routing table | 1 session |
| 6 | Orchestrator modes (BUILD/HUNT/FIX/EVALUATE/CROSS-ENGINE/BENCHMARK) + response contracts + escalation | 2 sessions |
| 7 | Scheduler + recovery + factory-ops branch | 1 session |
| 8 | Dashboard + human gate + Arabic formatter + findings dashboard | 2 sessions |
| 9 | 15-point acceptance + hunt cycle acceptance + fix cycle acceptance | 1-2 sessions |
| 10 | Health monitoring + sustained hunting infrastructure | 1 session |
| **Total** | | **~14-17 sessions** |

### Interleaving with engine work (updated)

| Timeline | Engine work | Factory work |
|----------|------------|--------------|
| Now | Excerpting: model role research | Sessions 1-2 |
| Week 1-2 | Excerpting: 5-book LLM test | Owner: WSL setup (2.5) |
| Week 3-4 | Excerpting: 30-book probe | Session 3 (CLI setup) |
| Week 5-6 | Excerpting: completion | Sessions 4, 4.5 (benchmark + synthetic infra) |
| Week 7-8 | Excerpting: owner review | Session 5 (benchmark run) |
| Week 9-10 | — | Sessions 6-7 (orchestrator + scheduler) |
| Week 11-12 | Factory hunts excerpting engine 24/7 | Sessions 8-10 (interface + hardening) |
| Week 13+ | Taxonomy SPEC design | Factory hunts excerpting to Level 3+ |
| Week 15+ | Taxonomy: factory-built | Factory hunts BOTH engines continuously |

The key insight: **after the excerpting engine is complete, the factory spends weeks hunting it before taxonomy even begins.** Taxonomy SPEC design happens in Claude Chat while the factory hunts excerpting. By the time taxonomy is ready to build, excerpting has been hunted to Level 3 or higher.

---

## What the Owner Sees

The owner's dashboard shows, at a glance:

**Quality status per engine:**
```
Source Engine:        Level 4 ████████░░ (192 synthetic tests, 0 CRITICAL in 60 days)
Normalization Engine: Level 3 ██████░░░░ (87 synthetic tests, hunt yield 8%)
Excerpting Engine:    Level 2 ████░░░░░░ (34 synthetic tests, 3 CRITICAL pending fix)
Taxonomy Engine:      Building ░░░░░░░░░░ (not yet started)
Synthesis Engine:     Not started
```

**Recent findings:**
```
F-2026-0342 [CRITICAL] T-2 decontextualization in excerpting — refutation separated from target
F-2026-0339 [HIGH] T-6 metadata — compiler school propagated to original author
F-2026-0335 [MEDIUM] T-4 self-containment — "as above" back-reference not resolved
```

**Hunt activity (last 7 days):**
```
Hunt cycles run: 47
Findings discovered: 3 (yield: 6.4%)
Findings fixed: 5
Regression tests added: 5
Synthetic library size: 342 cases
```

**Pending for owner:**
```
2 escalations needing your decision
1 Arabic review packet ready (5 excerpts from Book 14)
0 CRITICAL findings needing your attention
```

The owner doesn't need to understand the hunting infrastructure. He sees: are the engines getting safer? Are there problems I need to look at? Is the factory doing its job?

---

## The Standard the System Is Held To

The factory runs 24/7 (when the PC is on). It generates synthetic adversarial data. It hunts for bugs. It finds them. It fixes them. It verifies the fixes. It builds an immune memory. It tracks quality trends. It prepares evidence for the owner. It never stops.

Every corruption threat (T-1 through T-7) is systematically targeted. Every cross-engine boundary is tested. Every full-pipeline flow is verified. Every finding produces five outputs. Every fix is independently reviewed. Every regression test is permanent.

The pipeline gets harder to break over time. The synthetic library grows. The hunt yield declines. The maturity levels rise. And the owner reads output that has been tested against hundreds of adversarial scenarios designed specifically to corrupt his knowledge — and survived all of them.

This is the standard. Nothing less.
