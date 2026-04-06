# Hardening Traceability and Knowledge Integrity Review

## Scope and primary artifacts consulted

This report is based on the governing hardening protocol and the batch-level verification amendment that introduces a batch lifecycle and script suite. fileciteturn2file0L1-L1 fileciteturn25file0L1-L1

The operational scale and “no silent drops” ambition are represented by the merged atom inventory and the hardening ledger state. fileciteturn4file0L1-L1 fileciteturn17file0L1-L1

Key established constraints used without re-derivation (explicitly supplied as ground facts in the prompt) include: 139 owner-feedback files as ground truth; 7-stage atom lifecycle; prompt budget near cap; and available empirical fixtures and sciences/families taxonomy.

## Pre-mortem failure analysis

### Findings for the five specified loss manifestations

FINDING [Q1]-1: Implemented atoms without behavior-change proof becomes “paper implementation”
SEVERITY: CRITICAL  
PROTOCOL SECTION: §4 (Q‑CLOSED terminal gate) and §1.6 (gate precedence) fileciteturn2file0L1-L1  
CAUSE/GAP: The lifecycle can reach IMPLEMENTED (and even be marked “closed” administratively) without a *required* empirical confirmation that the excerpting engine’s observable output differs in the intended way. The v5.0 amendment’s Batch Completion Gate enforces capture completeness and queue terminality, but it does not make “behavior-change evidence” a mandatory property of Q‑CLOSED for each prompt-affecting atom; it focuses on MCU→queue completeness and on the existence of artifacts, not on effect. fileciteturn25file0L1-L1  
WARNING SIGN: The ledger shows atoms in IMPLEMENTED or Q‑CLOSED while (a) no atom_test evidence is linked to the atom ID, or (b) tests exist but only validate code-path execution (structural assertions) rather than output deltas tied to the atom’s claim. fileciteturn17file0L1-L1  
RECOMMENDATION:  
Concrete protocol amendment text (copy‑paste):  
```text
NEW — proposed §4.10.1 Impact Evidence Requirement (IER)

Definition: A prompt-affecting atom MAY NOT enter Q‑CLOSED unless it has Impact Evidence attached:
- at least one empirical run that demonstrates an output delta consistent with the atom’s doctrine claim, OR
- an explicit waiver signed in DECIDED with a reason ("not empirically testable yet") and a scheduled validation debt entry.

Impact Evidence MUST include:
- fixture_id, chunk_id, model_id, timestamp, prompt_hash, spec_hash
- before/after outputs and a short diff rationale.
```
PRIORITY: 1

FINDING [Q1]-2: Silent regression after later prompt changes is not structurally blocked
SEVERITY: CRITICAL  
PROTOCOL SECTION: §1.6 (gate precedence) and §4 (atom lifecycle closure semantics) fileciteturn2file0L1-L1  
CAUSE/GAP: The v5.0 amendment adds batch completeness verification (A→C→B ordering) and a Batch Completion Gate, but it does not introduce a *mandatory* “post-change regression sweep” gate that re-validates previously Q‑CLOSED behavioral commitments after any new prompt change. atom_test as described is atom-scoped (“one atom at a time”), which can allow later atoms to override or degrade earlier behaviors without detection if prior tests are not systematically rerun. fileciteturn25file0L1-L1  
WARNING SIGN: After a sequence of prompt edits, previously stable fixtures begin showing drift in unit boundaries or classification behavior, but no process artifact records a failure because only the newest atom’s test was executed. A validation-only session could detect this by re-running a fixed “regression pack” (see Q2/Q3) and observing failures on already-closed atoms.  
RECOMMENDATION:  
```text
NEW — proposed §1.6.1 Regression Gate

If ANY prompt text changes OR any Phase-2 behavior prompt-affecting rule changes,
a Regression Gate MUST run before any atom can be marked Q‑CLOSED.

Regression Gate passes iff:
- the regression suite for ALL atoms with prior Impact Evidence passes on the canonical regression fixture(s)
- results are stored under engines/excerpting/reference/regression_runs/<run_id>/ with prompt_hash.
```
PRIORITY: 1

FINDING [Q1]-3: False “already covered by existing FP” categorization creates functional loss with zero silent drops
SEVERITY: HIGH  
PROTOCOL SECTION: §4 (CHALLENGED and DECIDED gates) and §1.4 (hard rules: fail loud, ground truth discipline) fileciteturn2file0L1-L1  
CAUSE/GAP: The traceability system can remain internally consistent (every MCU mapped; 0 silent drops) even if an MCU is mapped to “existing foundations principle (FP) coverage” incorrectly. v5.0’s MCU mapping requires each MCU map to MAQ/META/REJECT, but it does not require *counterexample validation* that the mapped “already covered” rule actually addresses the owner’s specific edge case. fileciteturn25file0L1-L1  
WARNING SIGN: A verification-only session can detect an abnormal concentration of MCUs mapped as “covered” with “close paraphrase/weak match” confidence for HIGH/CRITICAL MCUs (v5.0 already tracks mapping confidence); additionally, “covered” mappings that lack a cited FP clause + a fixture-backed demonstration are early indicators. fileciteturn25file0L1-L1  
RECOMMENDATION:  
```text
NEW — proposed §3.4.5 Coverage-Claim Validation

Rule: An MCU may be dispositioned as "ALREADY COVERED" ONLY if:
(1) the exact FP clause is cited (file + section anchor),
(2) a minimal counterexample is written (what would fail if not covered),
(3) either:
    (a) an existing empirical test already demonstrates coverage, OR
    (b) a new micro-test is added to the regression pack.
Otherwise the MCU MUST become a new atom or a correction delta.
```
PRIORITY: 2

FINDING [Q1]-4: Interpretation drift during expansion survives gates when expansion is not “anchor-bound”
SEVERITY: CRITICAL  
PROTOCOL SECTION: §4 (RAW→EXPANDED→CHALLENGED) fileciteturn2file0L1-L1  
CAUSE/GAP: v5.0’s batch verification is primarily about ensuring the source is *represented* (MCUs traced), not that the subsequent expansion preserves intent. Drift can occur when CC expands an MCU into a doctrine statement using plausible scholarly framing that is not the owner’s intent, and coworker challenge focuses on coherence rather than fidelity—especially if the expansion lacks “verbatim anchors” and “negative constraints” (what the owner explicitly rejects). v5.0 requires verbatim anchors for MCUs during verification, but it does not require expansions to remain explicitly bound to those anchors through the EXPANDED and DECIDED stages. fileciteturn25file0L1-L1  
WARNING SIGN: Early signal is a growing distance between MCU anchor text and expansion language: expansions introduce new universals, new priority claims, or new scope boundaries not present in the MCU anchors; a validation-only session can spot-check by selecting a stratified sample of expansions and performing “anchor-to-expansion entailment checks”.  
RECOMMENDATION:  
```text
NEW — proposed §4.2.2 Anchor-Bound Expansion Rule

Every EXPANDED atom MUST include:
- Source Anchors: list of MCU anchors (verbatim spans + file path + line range)
- Fidelity Notes: a bullet list of assertions that are strictly entailed by the anchors
- Non-Entailed Additions: any interpretive enrichments marked explicitly as INFERENCE

Gate: CHALLENGED may not pass unless at least one challenger explicitly audits fidelity
("What in the anchors proves this claim?").
```
PRIORITY: 1

FINDING [Q1]-5: Cross-batch contradiction goes undetected because verification is batch-local
SEVERITY: CRITICAL  
PROTOCOL SECTION: §1.6 (gate precedence across sessions/batches) and §4 (DECIDED and Q‑CLOSED consistency duties) fileciteturn2file0L1-L1  
CAUSE/GAP: v5.0 formalizes a per-batch capture/processing lifecycle (F then G then SC) and introduces batch artifacts under `batch_verification/<BATCH_ID>/`. That structure strengthens *intra-batch* completeness but does not impose a cross-batch doctrine coherence check before Q‑CLOSED or before advancing batches. Contradictions can appear when a later generalization atom overrides a previously finalized foundation atom (or vice versa), and because the system records “no silent drops,” the contradiction is not categorized as loss. fileciteturn25file0L1-L1  
WARNING SIGN: Earliest indicator is the presence of two Q‑CLOSED atoms whose doctrine contains opposing quantifiers or opposing scope clauses (“always” vs “never”; “fiqh only” vs “all sciences”), discovered by a rule-level lint pass over SPEC + prompt + doctrine summaries.  
RECOMMENDATION:  
```text
NEW — proposed §1.6.2 Cross-Batch Coherence Gate

Before starting G-batch hardening and before any SC-batch atom enters DECIDED:
- run a "doctrine coherence scan" across all Q‑CLOSED atoms (F + prior batches)
- fail the gate if:
   (a) two atoms assert conflicting constraints on the same concept, OR
   (b) a later-batch atom narrows/overrides a foundational invariant without explicit "OVERRIDE" marking.

Required artifact: coherence_report.md listing conflicts and required resolutions.
```
PRIORITY: 2

### Findings for three additional failure causes not listed by the prompt

FINDING [Q1]-6: Many-to-one traceability hides “semantic compression loss” despite perfect MCU accounting
SEVERITY: HIGH  
PROTOCOL SECTION: §3.4 (MCU mapping) and §4 (atom splitting discipline) fileciteturn25file0L1-L1 fileciteturn2file0L1-L1  
CAUSE/GAP: v5.0 explicitly allows many MCUs to map to one MAQ entry (“mapped_to: list of IDs”). This is necessary, but it creates a failure mode: all MCUs are “accounted for,” yet the single downstream atom cannot faithfully implement all distinct constraints, so some are lost as semantic compression. The existing scripts/gates can still pass because the mapping is non-empty and appears confident. fileciteturn25file0L1-L1  
WARNING SIGN: Atypical clustering where a small number of atoms absorb a large fraction of MCUs (high fan-in), especially for CRITICAL/HIGH MCUs; also “merged” rationales that lack explicit sub-claims in the EXPANDED text.  
RECOMMENDATION:  
```text
NEW — proposed §3.4.6 Fan-In Threshold Rule

If a single MAQ atom maps to >N MCUs (default N=5) OR to >1 CRITICAL MCU,
then the verifier MUST either:
- split the atom, OR
- add a Sub-Claim Table to the atom showing a 1:1 mapping from each MCU to a specific clause in EXPANDED doctrine.

Gate: Batch Completion Gate fails if fan-in violations are unresolved.
```
PRIORITY: 2

FINDING [Q1]-7: Model-environment mismatch invalidates empirical proofs
SEVERITY: CRITICAL  
PROTOCOL SECTION: §0 (pre-session prerequisites) and §4 (validation evidence semantics) fileciteturn2file0L1-L1  
CAUSE/GAP: If empirical runs are executed via OpenRouter with a specific model/version/temperature and production usage differs (different model, different system prompt wrapper, different sampling settings), then “tests passed” may not imply runtime behavior changed or stayed fixed. Neither v4.3 nor v5.0, as written in the amendment, requires test runs to be bound to a production-equivalence contract (“same model, same settings, same prompt hash”), even though v5.0 does require hash-bound inventory for files. fileciteturn25file0L1-L1  
WARNING SIGN: Empirical behavior is inconsistent across repeated runs or across models; Q‑CLOSED evidence lacks model_id/prompt_hash/spec_hash, making later reproduction impossible.  
RECOMMENDATION:  
```text
NEW — proposed §0.4 Empirical Equivalence Contract

All empirical validations MUST record:
- model provider, model id, model version (if available)
- sampling parameters (temperature, top_p, max_tokens)
- prompt_hash and spec_hash

A Q‑CLOSED validation is INVALID if the recorded contract does not match the
declared "production validation profile" for the excerpting engine.
```
PRIORITY: 1

FINDING [Q1]-8: Fixture overfitting creates “passing tests / failing library” loss
SEVERITY: HIGH  
PROTOCOL SECTION: §4 (validation scope) and NEW fixture governance fileciteturn2file0L1-L1  
CAUSE/GAP: With a limited fixture set heavily concentrated in fiqh/nahw sharh structures, tests can pass while the owner’s true library (covering ENT/SEQ families and other sciences) remains uncorrected. This is functional loss that will not appear as silent drops in MAQ/ledger; it is a representativeness failure. fileciteturn25file0L1-L1  
WARNING SIGN: High pass rate on fixtures while owner continues to report errors concentrated in sciences/genres not represented by fixtures (e.g., hadith collection structure, tarajim entries, sequential tasawwuf manuals).  
RECOMMENDATION:  
```text
NEW — proposed §4.10.2 Fixture Representativeness Gate

At least one fixture MUST exist for each structural family [ENT],[ARG],[RUL],[SEQ].
No batch may be declared complete (Ijazah/Batch Completion equivalent) unless
all prompt-affecting atoms have been validated against:
- the canonical regression fixture, AND
- at least one non-overlapping family fixture when applicable.

If fixtures are missing, the protocol MUST schedule fixture creation debt
before continuing to the next batch.
```
PRIORITY: 3

### Ranking and single-point-of-failure diagnosis for all eight causes

Most likely given project history (Session 1 skipped files; OPS-DEC-006 single-model miss; prompt cap exhaustion):
1) FINDING [Q1]-2 (Regression without detection): history shows evaluation gaps can miss quality problems; prompt cap pressure incentivizes dense edits that can regress earlier behaviors without obvious local changes. fileciteturn2file0L1-L1  
2) FINDING [Q1]-4 (Expansion drift): the system depends on expansion quality; drift is structurally plausible even when capture completeness is perfect because it is a semantic fidelity problem, not a coverage problem. fileciteturn2file0L1-L1  
3) FINDING [Q1]-3 (False coverage categorization): functions as a “silent mis-triage” that keeps 0 silent drops while losing specific edge cases. fileciteturn25file0L1-L1  

Most preventable with the least additional mechanism:
1) FINDING [Q1]-3 (Coverage-claim validation): add a small, enforceable rule requiring FP clause citation + counterexample + test linkage.  
2) FINDING [Q1]-6 (Fan-in threshold): purely analytic check over existing MCU→atom mappings plus a required sub-claim table. fileciteturn25file0L1-L1  
3) FINDING [Q1]-7 (Empirical equivalence contract): simple metadata logging requirement; low engineering footprint.  

Single point of failure causing cascading loss:
- FINDING [Q1]-2 (Regression without detection) is the dominant cascade risk: one later prompt refactor can silently invalidate many earlier atoms at once, while all artifacts still show completion and 0 silent drops. This is precisely the kind of downstream “behavior not reflecting intent” loss that survives traceability accounting.

## Script completeness analysis

The v5.0 amendment defines a script suite oriented around batch inventory determinism, verification artifact generation, and a Batch Completion Gate. fileciteturn25file0L1-L1

### Lifecycle tracing of a single owner note and script coverage

FINDING [Q2]-1: The five scripts cover capture completeness but not per-atom hardening → behavior integrity
SEVERITY: CRITICAL  
PROTOCOL SECTION: §3.4 (batch verification) vs §4 (7-stage atom lifecycle) fileciteturn25file0L1-L1 fileciteturn2file0L1-L1  
CAUSE/GAP: A raw note enters as a .txt inside a zip bundle; the five scripts cover: inventorying files, initializing verification state, computing coverage, generating trace report, and verifying Batch Completion Gate. They do **not** cover these stages:
- expansion fidelity checks (RAW→EXPANDED),
- coworker challenge outcome validation (CHALLENGED),
- implementation-to-empirical-evidence binding (IMPLEMENTED→Q‑CLOSED),
- regression sweeps after later changes,
- runtime equivalence checks on a new unseen book. fileciteturn25file0L1-L1  
WARNING SIGN: Perfect batch completion artifacts (“100% verified files, 0 MISSED”) coexisting with ongoing owner reports that engine behavior ignores specific items indicates the “uncaptured” layer is not capture but behavior integrity.  
RECOMMENDATION:  
```text
NEW — proposed §4.10 Validation Artifact Binding

Add a required per-atom record:
validation/<ATOM_ID>.json containing test runs, prompt_hash, spec_hash, and outcome.

Gate: Q‑CLOSED requires presence of validation/<ATOM_ID>.json meeting schema.
```
PRIORITY: 1

FINDING [Q2]-2: No script detects regression across previously validated atoms
SEVERITY: CRITICAL  
PROTOCOL SECTION: NEW — proposed §1.6.1 Regression Gate (see Q1-2) fileciteturn2file0L1-L1  
CAUSE/GAP: The suite lacks an automated runner that re-executes *all* previously validated atom checks (or an equivalent consolidated regression pack) after any new prompt change. Batch Completion Gate enforces “queue terminality,” not “behavior remains true after subsequent changes.” fileciteturn25file0L1-L1  
WARNING SIGN: The number of Q‑CLOSED atoms rises while no artifact directory exists that stores “regression run results” keyed by prompt_hash; a validation-only session could detect this absence immediately.  
RECOMMENDATION:  
```text
NEW script: scripts/run_regression_suite.py

Input contract:
- --profile production_validation_profile.json
- reads: validation/ directory, canonical fixtures, prompt.txt, SPEC hashes
Output contract:
- writes: regression_runs/<run_id>/summary.json + junit-style report
- exit 0 on pass, 1 on regression
Lifecycle stage:
- runs after ANY prompt/SPEC change before allowing Q‑CLOSED or merge
Workflow trigger:
- mandatory in validation-only sessions and before closing IMPLEMENTED atoms
Prevents:
- regression without detection (Q1-2) and paper implementation drift (Q1-1)
```
PRIORITY: 1

FINDING [Q2]-3: No script validates prompt coherence under near-cap compression
SEVERITY: HIGH  
PROTOCOL SECTION: §4.11 (prompt refactor gate due to prompt budget) fileciteturn2file0L1-L1  
CAUSE/GAP: With the prompt at ~1,474/1,500 words (given), the system will perform high-density edits where contradictions/redundancies are easy to introduce. The five scripts do not parse or lint prompt structure for internal coherence (duplicate directives, conflicting quantifiers, unreachable conditions). v5.0 enforces “no mixed sessions” and batch audit discipline, but not prompt static analysis. fileciteturn25file0L1-L1  
WARNING SIGN: Prompt diffs show atomic additions that partially restate or negate earlier clauses; reviewers start requiring “interpretation notes” to explain the prompt itself—an indicator the prompt no longer has a single stable semantics.  
RECOMMENDATION:  
```text
NEW script: scripts/prompt_coherence_lint.py

Input:
- prompt source (canonical prompt file) + a small rule schema describing allowed sections/tags
Output:
- coherence_report.md with:
   - duplicate clause detection (string + semantic similarity)
   - conflicting modal/quantifier detection (MUST vs MAY on same predicate)
   - token budget accounting by section
Exit:
- nonzero if contradictions or duplicated constraints exceed thresholds

Runs:
- automatically before and after §4.11 prompt refactor sessions, and before Q‑CLOSED on any prompt-affecting atom.
Prevents:
- cross-atom contradiction and silent prompt incoherence contributing to Q1-2/Q1-5 cascades.
```
PRIORITY: 2

FINDING [Q2]-4: No script computes atom-to-behavior impact deltas (doctrine matters)
SEVERITY: CRITICAL  
PROTOCOL SECTION: NEW — proposed §4.10.1 Impact Evidence Requirement (see Q1-1) fileciteturn2file0L1-L1  
CAUSE/GAP: atom_test can show that the system produces expected boundary patterns on a chunk, but without a “toggle baseline” (run with and without the atom’s SPEC/prompt contribution), you cannot prove the atom caused the change rather than incidental variability. The five scripts never compute “with_atom vs without_atom” diffs. fileciteturn25file0L1-L1  
WARNING SIGN: Tests pass, but removing the atom’s prompt clause yields indistinguishable outputs on the same fixture chunk (or conversely, outputs vary randomly). This can be detected by an explicit delta-runner.  
RECOMMENDATION:  
```text
NEW script: scripts/atom_impact_diff.py

Input:
- --atom-id ATOM_### 
- --fixture, --chunk
- requires ability to render:
   (a) prompt/spec with atom enabled
   (b) prompt/spec with atom disabled (feature-flagged)

Output:
- impact/<ATOM_ID>/<run_id>.json containing:
   - before/after outputs
   - structured diff metrics (unit boundary count, classification labels)
   - "impact verdict": meaningful / negligible / indeterminate

Runs:
- mandatory before Q‑CLOSED for prompt-affecting atoms
Prevents:
- paper implementation (Q1-1) and false confidence in doctrine effectiveness.
```
PRIORITY: 1

### Answering the three explicit devil’s-advocate questions

- Regression detection script exists? **Not in the 5-script design.** A 6th script (run_regression_suite.py) is required to re-run previously validated checks keyed by prompt_hash/spec_hash. fileciteturn25file0L1-L1  
- Prompt coherence script exists? **Not in the 5-script design.** A 7th script (prompt_coherence_lint.py) is required, especially under §4.11 prompt refactor pressure. fileciteturn2file0L1-L1  
- Atom-to-behavior impact computation exists? **Not in the 5-script design.** An 8th script (atom_impact_diff.py) is required to produce causal evidence.  

## Fixture strategy for empirical testing

The fixture inventory is concentrated in fiqh and nahw/sharh styles, and atom_test executes Phase 2 classify+group on a selected chunk with live OpenRouter calls (cost-bearing). (All from established facts in the prompt.)

FINDING [Q3]-1: Adopt a canonical regression fixture to make regressions observable
SEVERITY: CRITICAL  
PROTOCOL SECTION: NEW — proposed §4.10.3 Canonical Regression Fixture fileciteturn2file0L1-L1  
CAUSE/GAP: Without a single canonical fixture applied across prompt-affecting atoms, later changes can regress earlier behavior without a common comparison point. This is the same structural class as OPS-DEC-006 (“single eval missed quality”), but now at the atom level. fileciteturn2file0L1-L1  
WARNING SIGN: Empirical results become non-comparable across atoms because each atom is validated on a different fixture, eliminating a stable baseline to detect regressions.  
RECOMMENDATION:  
```text
NEW — proposed §4.10.3 Canonical Regression Fixture

Decision: designate "taysir" as the canonical regression fixture.
Rationale: it is fiqh/sharh with explicit analytical moves and boundary-sensitive structure, making it high-signal for unit-boundary and grouping directives across many atoms.

Rule: Every prompt-affecting atom MUST have at least one canonical regression run recorded (taysir, fixed chunk set).
```
PRIORITY: 1

FINDING [Q3]-2: Layer genre coverage by adding one additional “matched” fixture per atom category
SEVERITY: HIGH  
PROTOCOL SECTION: NEW — proposed §4.10.4 Matched Fixture Policy fileciteturn2file0L1-L1  
CAUSE/GAP: A canonical fixture alone risks overfitting (Q1-8). But testing every atom on every fixture exhausts budget. The missing mechanism is a rule-based mapping from atom category → 1 additional fixture selected by highest likelihood of exercising the targeted behavior.  
WARNING SIGN: Categories tied to nahw morphology or to Q&A segmentation show weak or noisy evidence on fiqh fixtures, implying the test is not exercising the behavior.  
RECOMMENDATION:  
```text
NEW — proposed §4.10.4 Matched Fixture Policy

In addition to canonical regression (taysir), each prompt-affecting atom gets ONE matched fixture run:

- Boundary / granularity / self-containment in sharh-style explanation: ibn_aqil_v3
- Nahw/sarf technical parsing behaviors: ibn_aqil_v3 (and v1 for edition robustness when high-risk)
- Fiqh mas'ala segmentation / rule-listing constraints: ext_39_masala
- Q&A structural directives: ext_46_qa
- Tarjih/khilaf/proof presentation within fiqh: taysir + ext_39_masala (choose one based on the atom’s stated target)

Document the mapping in validation/<ATOM_ID>.json as matched_fixture.
```
PRIORITY: 2

FINDING [Q3]-3: SPEC-only atoms require a different validation harness than atom_test Phase 2
SEVERITY: CRITICAL  
PROTOCOL SECTION: NEW — proposed §4.10.5 SPEC Validation Harness fileciteturn2file0L1-L1  
CAUSE/GAP: Many future atoms will be SPEC-only due to prompt cap pressure. atom_test targets Phase 2 LLM behavior and will not validate post-processing doctrine that operates after the LLM output. The missing mechanism is an end-to-end SPEC harness that (a) runs the pipeline, (b) applies SPEC validators/post-processors, and (c) asserts the SPEC-only rule’s observable effect (errors raised, transformations applied, outputs rejected/accepted).  
WARNING SIGN: SPEC-only atoms reach Q‑CLOSED with no empirical artifact beyond unit tests of helper functions, while real pipeline output remains unchanged.  
RECOMMENDATION:  
```text
NEW — proposed §4.10.5 SPEC Validation Harness

Add scripts/spec_test.py with fixtures that run the full excerpting pipeline end-to-end.

For every SPEC-only atom:
- define an expected SPEC outcome (pass/fail reason, or output transform)
- store golden results under spec_golden/<fixture>/<chunk>/<atom_id>.json
- require at least one run before Q‑CLOSED.
```
PRIORITY: 1

FINDING [Q3]-4: Current fixtures leave ENT and SEQ families uncovered; add 2–3 new fixture packages
SEVERITY: HIGH  
PROTOCOL SECTION: NEW — proposed §4.10.6 Fixture Family Coverage fileciteturn2file0L1-L1  
CAUSE/GAP: Existing fixtures (fiqh/nahw sharh, mas’ala, Q&A) are primarily [ARG]/[RUL] structures; ENT (entity-centric: hadith collections, tarajim) and SEQ (sequential-progressive: tasawwuf maqamat) have zero coverage, making many owner-intent behaviors untestable and increasing risk of “passing tests / failing library.”  
WARNING SIGN: Owner reports persistent failures in hadith/tarajim or sequential texts while test suite remains green.  
RECOMMENDATION:  
```text
NEW — proposed §4.10.6 Fixture Family Coverage

Add at minimum these new packages:

1) hadith_collection_ent
   - Science: hadith
   - Structural family: [ENT]
   - Ideal example: Riyad al-Salihin (chapter headings + hadith blocks)

2) tarajim_dictionary_ent
   - Science: tarajim (biographical entries)
   - Structural family: [ENT]
   - Ideal example: Taqrib al-Tahdhib or similar entry-based rijal compendium

3) tasawwuf_maqamat_seq
   - Science: tasawwuf
   - Structural family: [SEQ]
   - Ideal example: al-Risala al-Qushayriyya (maqamat/ahwal progression sections)

Each fixture must include phase1_chunks.json and at least 5 representative chunks.
```
PRIORITY: 3

FINDING [Q3]-5: Minimum run policy per atom under budget: 2 runs baseline, 3 for high-risk, plus periodic regression sweeps
SEVERITY: HIGH  
PROTOCOL SECTION: NEW — proposed §4.10.7 Budgeted Validation Policy fileciteturn2file0L1-L1  
CAUSE/GAP: The core tradeoff (single fixture gives regression sensitivity; multi-fixture gives genre coverage) requires an explicit budgeted policy or it will be applied inconsistently.  
WARNING SIGN: Validation plans vary atom-to-atom without a stable rule; later it becomes impossible to reason about what was actually covered.  
RECOMMENDATION:  
```text
NEW — proposed §4.10.7 Budgeted Validation Policy

For each prompt-affecting atom:
- Run 1: canonical regression fixture (taysir) on 1 fixed chunk.
- Run 2: matched fixture (per §4.10.4) on 1 chunk.
- Run 3 (only for HIGH-risk classes: boundary/granularity, safety, cross-book invariants):
    canonical fixture on a second chunk to reduce noise and increase regression sensitivity.

Additionally:
- After every prompt refactor (§4.11), run the full regression suite pack (see scripts/run_regression_suite.py).
```
PRIORITY: 2

## Priority matrix and implementation map

### Priority matrix ranked by likelihood × impact

1) FINDING [Q1]-2 (Regression gate + regression suite): highest cascade risk; likely under iterative prompt pressure.  
2) FINDING [Q1]-4 (Anchor-bound expansion): prevents semantic drift that survives perfect traceability.  
3) FINDING [Q1]-1 (Impact evidence requirement + impact diff): blocks paper implementation.  
4) FINDING [Q2]-2 (run_regression_suite.py): concrete mechanism enabling Q1-2.  
5) FINDING [Q2]-4 (atom_impact_diff.py): concrete mechanism enabling Q1-1.  
6) FINDING [Q3]-1 (Canonical fixture): prerequisite for meaningful regression suite.  
7) FINDING [Q1]-3 (Coverage-claim validation): cheap, prevents false coverage loss.  
8) FINDING [Q1]-5 (Cross-batch coherence gate): high impact, medium likelihood, important before G/SC scale-up.  
9) FINDING [Q2]-3 (prompt_coherence_lint.py): rises in importance as prompt approaches cap and refactors begin.  
10) FINDING [Q1]-7 (Empirical equivalence contract): critical correctness of evidence, low effort.  
11) FINDING [Q1]-6 (Fan-in threshold): prevents “semantic compression loss” with full MCU accounting.  
12) FINDING [Q3]-3 (SPEC validation harness): essential as SPEC-only atoms increase.  
13) FINDING [Q3]-2 (Matched fixtures policy): improves coverage efficiently.  
14) FINDING [Q3]-4 (New fixtures ENT/SEQ): strategic medium-term coverage expansion.  
15) FINDING [Q3]-5 (Budgeted validation policy): governance glue.

### Dependency map

- FINDING [Q2]-2 (run_regression_suite.py) depends on FINDING [Q3]-1 (canonical regression fixture) and on having per-atom validation artifacts (FINDING [Q2]-1).  
- FINDING [Q1]-1 (Impact evidence requirement) depends on FINDING [Q2]-4 (atom_impact_diff.py) or an equivalent mechanism to produce deltas.  
- FINDING [Q1]-5 (Cross-batch coherence gate) depends on having stable doctrine summaries for atoms (from §4 lifecycle) and ideally prompt lint infrastructure (FINDING [Q2]-3) to automate detection.  
- FINDING [Q3]-3 (SPEC harness) depends on the existence of deterministic pipeline entrypoints and stable fixture packaging conventions (already implied by existing phase1_chunks.json usage in the established facts).  
- FINDING [Q1]-3 (Coverage-claim validation) depends minimally on the MCU trace artifacts (v5.0) and does not require new fixtures.

### Effort estimate per finding

- FINDING [Q1]-1: MEDIUM (2–3 sessions) — requires designing schema + “impact” semantics and integrating into Q‑CLOSED gate.  
- FINDING [Q1]-2: MEDIUM (2–3 sessions) — needs protocol gate + automation + suite definition.  
- FINDING [Q1]-3: SMALL (1 session) — mostly governance + a lightweight micro-test or counterexample requirement.  
- FINDING [Q1]-4: SMALL (1 session) — primarily atom template/gate update; minimal code.  
- FINDING [Q1]-5: MEDIUM (2–3 sessions) — requires defining contradiction taxonomy and coherence scan output.  
- FINDING [Q1]-6: SMALL (1 session) — analytic checks over traceability artifacts + atom template addition.  
- FINDING [Q1]-7: TRIVIAL (1h) — metadata logging requirement + schema.  
- FINDING [Q1]-8: LARGE (dedicated milestone) — fundamentally needs new fixtures and representativeness governance.  
- FINDING [Q2]-1: SMALL (1 session) — standardize validation/<ATOM_ID>.json and gate binding.  
- FINDING [Q2]-2: MEDIUM (2–3 sessions) — implement regression runner + suite management.  
- FINDING [Q2]-3: MEDIUM (2–3 sessions) — prompt lint requires text model + contradiction heuristics.  
- FINDING [Q2]-4: LARGE (dedicated milestone) — requires “atom toggling” capability and stable diff metrics.  
- FINDING [Q3]-1: TRIVIAL (1h) — choose canonical fixture + lock chunk IDs.  
- FINDING [Q3]-2: SMALL (1 session) — mapping policy + documentation conventions.  
- FINDING [Q3]-3: MEDIUM (2–3 sessions) — implement spec_test harness + golden outcomes.  
- FINDING [Q3]-4: LARGE (dedicated milestone) — curate new books, chunk them, compute phase1_chunks, stabilize.  
- FINDING [Q3]-5: SMALL (1 session) — policy definition and protocol insertion.

