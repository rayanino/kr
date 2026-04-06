# Batch Completeness Verification Amendment v5.0 for Hardening Session Protocol v4.3

## Executive summary

This amendment closes a structural governance gap in the hardening operation: there is currently no batch-level mechanism that *forces* exhaustive, backward (source→queue) verification that **all** owner feedback in a batch has been captured, triaged, and either implemented or explicitly rejected—before the system proceeds into the next phase of work. The failure class that motivated this—**entire source files being silently excluded from extraction** (F1/F2), plus systematic “intensity loss” (ALL‑CAPS urgency normalized)—is documented as a catastrophic, non-random omission pattern with high-stakes implications for downstream doctrine and prompt behavior. fileciteturn3file0L1-L1

The amendment introduces a **new verification-only session** (Session C) and a **Batch Completion Gate** that together create an enforceable, auditable “no silent drops” batch lifecycle. The core mechanism is a deterministic **inventory → verification status ledger → unit-level trace file** pipeline that makes “skipped file” failures architecturally detectable and therefore blockable, rather than discoverable only via post-hoc forensic audits. This builds directly on existing per-file extraction + coverage-table intake safeguards (v3.3+) by adding an independent, backward completeness pass and a formal “batch freeze” concept for moving between phases. fileciteturn2file0L1-L1

## Batch lifecycle protocol

### Lifecycle overview

The batch lifecycle is formalized as a **repeatable phase chain** for each batch (F, G, SC), where a “batch” is the set of collection bundles intended to be hardened together (e.g., F1–F8, G1–G4, SC1–SC3). The lifecycle requires *two different completeness properties*:

- **Capture completeness**: every feedback unit in the batch’s source files is represented in governance (as an atom, a meta-directive, or an explicitly rejected item).
- **Processing completeness**: every queued item is either closed (implemented/verified), deferred with conditions, or rejected—with no silent drops.

The amended lifecycle is:

**Session A — Intake + Extraction (existing, `intake-only`)**  
Goal: ingest batch bundles, inventory all files, extract candidate atoms per-file, generate a coverage table, integrate into `MERGED_ATOM_QUEUE.md`. fileciteturn2file0L1-L1

**Session C — Batch Completeness Verification (new, `verification-only`)**  
Goal: re-read **every file** in the batch (Layer A and Layer B), segment into Meaningful Content Units (MCUs), and ensure every MCU is traced to (a) a queue entry, (b) a meta-directive registry item, or (c) an explicit rejection record. Produce auditable artifacts + coverage metrics. fileciteturn3file0L1-L1

**Session B — Per-Atom Hardening (existing, `full-atom` + supporting types)**  
Goal: process atoms through the 7-stage lifecycle (RAW→CLOSED), including coworker challenge, synthesis, implementation, and Q‑CLOSED verification. fileciteturn2file0L1-L1

**Session D — Adversarial Completeness Review (optional, DR dispatch class)**  
Goal: independent adversarial sampling of the verification artifacts produced in Session C (and optionally the batch closure artifacts) to detect “verification theater” failures and correlated omission patterns.

### Critical ordering decision: where verification belongs

The proposed A→B→C→D ordering is **unsafe for the specific catastrophe class** that motivated this amendment, because it allows substantial hardening work to proceed on a potentially incomplete representation of the owner’s batch signal. The documented failure showed that omission was systematic (entire F1/F2 absent), not random; that makes early detection the dominant leverage point. fileciteturn3file0L1-L1

This amendment therefore mandates **A→C→B**, with D optional but positioned as adversarial validation of the C outcomes.

Rationale:

- If capture completeness is wrong, per-atom rigor only hardens the *wrong* target. The protocol already treats “raw owner text is ground truth” and “fail loud, not silent” as core principles; capture completeness is a prerequisite to applying those principles in good faith. fileciteturn2file0L1-L1
- The existing intake coverage table reduces the chance of a skipped file, but it is still extraction-phase self-attestation. A separate verification phase provides independence and backward traceability (source→queue), which is the missing structural guarantee. fileciteturn2file0L1-L1

### Session count decision for real operations

Four named phases are the right conceptual decomposition, but **Session C must be allowed to span multiple sessions** for large batches; it is not one “meeting,” it is a census process with defined progress checkpoints. The system should treat “C” as a **repeatable session class** (C1, C2, …) until inventory coverage reaches 100% and all gaps are dispositioned.

### Session type mappings

- Session A maps to `intake-only` (existing). fileciteturn2file0L1-L1  
- Session C maps to a **new** `verification-only` session type (added by this amendment).  
- Session B maps primarily to `full-atom`, with `debt-clearance`, `prompt-architecture`, and `validation-only` remaining governed by existing gate precedence. fileciteturn2file0L1-L1  
- Session D is not a CC session type; it is a DR dispatch (recommended as a `phase-gate` or new “batch-audit” relay class—defined below).

## Verification session specification

### Pre-session checklist for verification-only sessions

A verification-only session may begin **only if** all of the following are true:

**Batch intake is complete**
- All bundles belonging to the batch have been unzipped into their collection directories, with required structure present (Layer A + Layer B), and the intake quality gate’s coverage table exists with no unresolved “0 notes in non-empty file” red flags. fileciteturn2file0L1-L1
- No additional bundles for that batch remain at repo root awaiting intake (otherwise the inventory is incomplete by definition). fileciteturn2file0L1-L1

**Repository + doctrine stability**
- Correct branch verified; tests and prompt/SPEC sync pass (same pre-session prerequisites as §0). fileciteturn2file0L1-L1  
- The batch inventory has been (re)generated via script from the current working tree to bind verification to an exact file set (hashes + line counts). (New script defined below.)

**Global blocking conditions cleared**
- No checkpoint states remain uncleared if the protocol’s checkpoint resolution gate is triggered (checkpoint states are globally blocking by design). fileciteturn2file0L1-L1  
- Preliminary debt ceiling conditions are honored (existing precedence). This amendment does not weaken those gates. fileciteturn2file0L1-L1

**Queue readiness**
- `MERGED_ATOM_QUEUE.md` reflects the current post-intake state for the batch (including any already-known gaps from `QUEUE_AUDIT_RAW_VS_EXTRACTION.md`-style audits). fileciteturn4file0L1-L1  
- A writable verification workspace exists for the batch under `engines/excerpting/reference/batch_verification/<BATCH_ID>/`.

### Procedure

#### Reading order

The procedure must be deterministic and layered to prevent the documented “Layer confusion” failure mode (verifying only Layer B when Layer A contains uncaptured owner foundations). fileciteturn3file0L1-L1

Order is:

1. **Layer A first**: `source_artifacts/*.txt` for every collection in the batch.  
2. Then **Layer B**: `01_questionnaire_answer.md`, then `02_*` through `14_*` structured files (including JSONL/YAML/MD). fileciteturn2file0L1-L1  
3. “Glue files” last: README, manifest, traceability files—unless they contain owner directives, in which case they are treated as Layer B content.

Within each layer, sort by:
- Collection series order (F1→F8, G1→G4, SC1→SC3),
- then file path lexical order,
- with an override: files flagged by intake density anomalies (large file, low note count) are moved earlier.

#### Unit of comparison: Meaningful Content Units

A verification session is not sentence-counting. It is a requirements-style traceability exercise: define a unit small enough to be meaningful, stable enough to audit, and cheap enough to enumerate.

**Definition: MCU (Meaningful Content Unit)**  
An MCU is the smallest span in the source that expresses one of the following:
- a directive (“must/never/should”), constraint, prohibition, nonnegotiable, or explicit preference;
- a definition or conceptual model;
- a risk articulation (“dangers when doing what we’re doing…”);
- an example that functions as a rule-specifier (worked example, algorithm, edge case);
- a prioritization / severity signal (ALL‑CAPS pleas, explicit “PLEASE CATCH THIS CLEARLY,” multiple exclamation marks);
- a meta-instruction about how agents should operate (e.g., “think beyond what I say…”). fileciteturn3file0L1-L1

This directly matches the forensic audit’s finding that omissions were concentrated in foundational vision, methodology, and ALL‑CAPS directives—units that are not guaranteed to appear as “atoms” unless explicitly looked for. fileciteturn3file0L1-L1

#### Per-file verification loop

For each file in the batch inventory:

1. **Bind file identity**
   - Record: path, byte size, line count, SHA‑256 hash.
   - If the file changed since inventory generation, mark as `DRIFTED` and re-inventory the batch before continuing.

2. **Enumerate MCUs**
   - Enumerate MCUs with (start_line, end_line) ranges and include **verbatim anchor text** (short excerpts) sufficient to re-locate the unit. The existing “verbatim span extraction” doctrine applies; it exists specifically to avoid meaning loss through paraphrase. fileciteturn2file0L1-L1

3. **Attempt trace mapping (backward traceability)**
   For each MCU, locate its representation as one of:
   - An existing MAQ entry (Sections D–I in `MERGED_ATOM_QUEUE.md`), or an already-finalized / verify-only mapping (Sections A–B), or a meta-directive entry (Section C). fileciteturn4file0L1-L1
   - An explicit rejection record (new artifact defined below).

   Mapping must be recorded as:
   - `mapped_to`: list of IDs (MAQ‑###, META‑###, REJECT‑###),
   - `mapping_confidence`: exact / close paraphrase / weak match,
   - `evidence`: either (a) a direct quote match, or (b) a semantic match explanation referencing unique content tokens.

4. **Classify discrepancies**
   If a mapping fails or is insufficient, classify as MISSED/SOFTENED/DISTORTED (definitions formalized below). fileciteturn3file0L1-L1

5. **Disposition on discovery**
   - MISSED → create a new queue entry immediately (or a new meta-directive entry if it belongs in that class), assign ID, and mark status `NEW` (RAW).  
   - SOFTENED/DISTORTED → create a “queue correction delta” entry referencing the existing ID that must be amended or split.

6. **File-level closure record**
   Mark file status as `VERIFIED` only when:
   - every MCU has a mapping or is explicitly dispositioned;
   - file-level counts and top severities are recorded; and
   - there are no unresolved MCU classifications left hanging (no “TODO map later”).

#### Handling meta-directives

The queue already distinguishes 47 “meta-directives” (foundational vision + behavior directives) as *not traditional atoms* and targets them to CLAUDE.md/MEMORY/USER_MODEL/DEFERRED_FEATURE. fileciteturn4file0L1-L1

Verification must treat these as first-class completeness units, with two additional requirements:

- **Capture requirement**: every meta-directive MCU must map to a `META-###` entry (or produce a new one).
- **Integration requirement**: each `META-###` must have an integration target and an integration status:
  - `INTEGRATED` with a concrete pointer (file path + section anchor), or
  - `DEFERRED` with a specific condition for revisit.
  
This prevents the subtle failure mode where foundational directives are “captured” in a queue but never become operational doctrine.

#### Context budget management

A verification session should not attempt to keep the batch in CC context. It should use a **stateful artifact pipeline** plus deterministic scripts, and treat CC as the adjudicator and report-writer.

- Session C may span multiple sessions; progress is carried by:
  - `inventory.json`
  - `verification_status.json`
  - `mcu_trace.jsonl`
  - `verification_report.md`

Planning rule: compute approximate token load per file from word counts before starting, then set a hard per-session target that leaves a full Zone‑3 buffer consistent with existing context management rules. fileciteturn2file0L1-L1

### Classification system for gaps

The forensic audit defines three categories (MISSED, SOFTENED, DISTORTED) and reports a strong systematic softening pattern (ALL‑CAPS urgency normalized). fileciteturn3file0L1-L1

This amendment keeps the three core categories, and adds *one structural category* that is necessary for “skipped file” prevention:

- **SKIPPED-FILE (structural, not per-MCU)**: a file present in inventory has **no verification record** or is marked verified without any MCU trace records. This is a gate-failing condition by definition.

(Other refinements—severity levels and audit trail—are defined in the Queue Audit Methodology section.)

### Output artifacts

A verification-only session produces these artifacts (all under `engines/excerpting/reference/batch_verification/<BATCH_ID>/`):

- `inventory.json`  
  Deterministic list of files to be verified with hashes and line counts.

- `verification_status.json`  
  One entry per file: status (`UNVERIFIED`, `IN_PROGRESS`, `VERIFIED`, `DRIFTED`), plus counts.

- `mcu_trace.jsonl`  
  The core audit trail: one line per MCU with mapping + classification + severity + disposition.

- `verification_report.md`  
  Human-readable report summarizing:
  - file coverage (verified/total),
  - MCU coverage (mapped/total),
  - top CRITICAL/HIGH gaps,
  - systemic patterns (e.g., consistent softening of intensity markers).

- `delta_queue_patch.md` (optional but recommended)  
  A “patch plan” listing new MAQ/META entries created, existing ones corrected, and required follow-up hardening steps.

Additionally:
- `MERGED_ATOM_QUEUE.md` is updated to include new MAQ/META entries created during verification (this is the canonical queue). fileciteturn4file0L1-L1

### Scripts and automation

This amendment adds a small script suite in the style of existing deterministic checkers (e.g., prompt/SPEC sync). fileciteturn8file0L1-L1 fileciteturn9file0L1-L1

#### Script set

**Script: `scripts/batch_inventory.py`**  
Purpose: generate a deterministic file inventory for a batch.

Inputs:
- `--batch-id` (e.g., `F`, `G`, `SC`)
- `--collections-root` default `engines/excerpting/`
- optional include/exclude globs

Outputs:
- `reference/batch_verification/<BATCH_ID>/inventory.json`

Core logic:
- Enumerate collection directories for the batch (pattern-based, configurable).
- Enumerate files in each directory excluding:
  - the archived zip copy (if present),
  - generated artifacts (status/report files),
  - caches.
- For each file compute:
  - bytes, line_count, sha256.

**Script: `scripts/batch_verification_init.py`**  
Purpose: initialize `verification_status.json` from inventory.

**Script: `scripts/batch_compute_coverage.py`**  
Purpose: compute:
- File coverage = verified_files / total_files
- MCU coverage = mapped_mcus / total_mcus
- Severity-weighted gap counts

Inputs:
- inventory + status + mcu_trace

Outputs:
- prints summary and writes `coverage.json`

**Script: `scripts/batch_generate_trace_report.py`**  
Purpose: generate `verification_report.md` from JSON artifacts.

**Script: `scripts/verify_batch_completion_gate.py`**  
Purpose: deterministic pass/fail for the Batch Completion Gate.

Inputs:
- batch id
- reads artifacts + queue

Exit codes:
- 0 = gate pass
- 1 = gate fail (with reasons)
- 2 = misconfiguration (missing files)

#### Minimal pseudocode sketches

```python
# batch_inventory.py (sketch)
for file in list_all_batch_files(batch_id):
    record = {
        "path": str(file),
        "bytes": file.stat().st_size,
        "line_count": count_lines(file),
        "sha256": sha256(file.read_bytes()),
        "layer": detect_layer(file),   # "A" or "B"
        "collection": detect_collection(file),
    }
    inventory.append(record)

write_json(out_path, {"batch_id": batch_id, "files": inventory})
```

```python
# verify_batch_completion_gate.py (sketch)
inv = read_json(inventory)
status = read_json(verification_status)
trace = read_jsonl(mcu_trace)

failures = []
if any(file not VERIFIED for file in inv.files):
    failures.append("SKIPPED-FILE: unverified files exist")

if any(mcu.classification in {"MISSED","DISTORTED","SOFTENED"} and mcu.disposition not resolved):
    failures.append("UNRESOLVED-GAPS: open audit findings")

if not all_queue_items_terminal(batch_id):
    failures.append("NONTERMINAL-QUEUE: atoms still open")

exit(1 if failures else 0)
```

### Session type integration

This amendment adds a new session type rather than overloading `validation-only`, because verification is neither “run tests” nor “evaluate coworker returns”; it is a batch-level traceability audit with its own artifacts and gates.

- **New session type**: `verification-only`
- **Atom processing**: NO (except creating new RAW entries in queue when MISSED items are found)
- **Compatibility**: stand-alone only (no mixed sessions), consistent with the existing strategy of preventing context overload and governance drift by forbidding multi-purpose sessions. fileciteturn2file0L1-L1

## Batch completion gate

### Gate position in precedence hierarchy

This amendment places the new gate **between bundle intake and prompt refactor/per-atom processing**, because its purpose is to prevent downstream work from proceeding on an incomplete representation of owner feedback.

- It must occur **after** bundle intake inventory, because verification needs a stable unzipped file set. fileciteturn2file0L1-L1  
- It must occur **before** prompt refactor and per-atom processing, because those steps are definitionally downstream of complete owner signal capture.

### Gate condition: measurable pass/fail criteria

The Batch Completion Gate passes only if all conditions below are simultaneously true for the active batch:

**Inventory and verification completeness**
- File coverage = **100%**: every file in `inventory.json` is marked `VERIFIED` in `verification_status.json`.
- No `DRIFTED` files remain.
- `SKIPPED-FILE` count = 0.

**MCU trace completeness**
- For every MCU in `mcu_trace.jsonl`, `mapped_to` is non-empty **and** the mapping confidence is not `weak match` for CRITICAL/HIGH severity items.
- `MISSED` count = 0 (because any MISSED must be converted immediately into a new MAQ/META/REJECT entry; after that conversion, it is no longer MISSED, it is “captured and pending processing”).

**Disposition completeness**
- Every MCU is dispositioned as one of:
  - `CAPTURED_AS_MAQ`
  - `CAPTURED_AS_META`
  - `EXPLICITLY_REJECTED` (with a justification and, for CRITICAL/HIGH, required reviewer sign-off; see workflow below)

**Queue terminality**
- All MAQ entries tagged as belonging to this batch are in a terminal state:
  - `CLOSED-IMPLEMENTED`, `CLOSED-VERIFIED`, `CLOSED-PRELIMINARY`, `DEFERRED-RECORDED`, or `REJECTED`  
  and none are in checkpoint states (`PAUSED-*`, `IMPLEMENTED-*`). fileciteturn2file0L1-L1

**Script attestation**
- `python scripts/verify_batch_completion_gate.py --batch-id <BATCH_ID>` exits 0 and writes a coverage summary for archival.

### Gate failure behavior

Gate failure behavior must preserve “fail loud, not silent.” fileciteturn2file0L1-L1

If the batch completion gate fails:

- **Blocked**:
  - Starting per-atom processing for that batch (no `full-atom` sessions targeting it).
  - Declaring the batch “complete” in NEXT.md planning.

- **Allowed**:
  - Intake-only sessions for newly arrived bundles (existing precedence).
  - Debt-clearance and checkpoint resolution sessions required by higher-precedence gates.
  - Verification-only sessions (this is the primary remediation path).

### Gate artifacts required as proof

A gate pass must be supported by committed artifacts:

- `batch_verification/<BATCH_ID>/inventory.json`
- `batch_verification/<BATCH_ID>/verification_status.json`
- `batch_verification/<BATCH_ID>/mcu_trace.jsonl`
- `batch_verification/<BATCH_ID>/coverage.json`
- `batch_verification/<BATCH_ID>/verification_report.md`
- The console output (or saved log) of `verify_batch_completion_gate.py`

## Queue audit methodology

### Category definitions

These definitions are made precise enough to be testable and script-auditable where possible, while allowing human judgment where necessary.

**MISSED**  
An MCU is MISSED if, after searching the queue and meta-directive registry:
- there is no MAQ/META/REJECT entry that expresses the MCU’s meaning, intent, and constraint direction, even approximately, and
- there is no explicit decision recorded to reject it. fileciteturn3file0L1-L1

**SOFTENED**  
An MCU is SOFTENED if:
- the queue contains a corresponding entry that preserves the *direction* of the instruction or concept, but
- the representation materially reduces priority/urgency/absoluteness signals present in the source.

Test triggers (non-exhaustive):
- MUST/NEVER/ONLY → SHOULD/MAY/OFTEN
- ALL‑CAPS pleas or repeated exclamation marks → neutral paraphrase with no priority signal
- “no room for X” → “prefer to avoid X”

**Clarifying rule for “always → typically”**: classify as SOFTENED (quantifier weakening) unless the original MCU’s correctness depends on strict universality; if strict universality is essential, upgrade severity (see below) and treat remediation as mandatory.

This aligns with the audit’s observation that all softening cases were intensity normalization rather than meaning inversion. fileciteturn3file0L1-L1

**DISTORTED**  
An MCU is DISTORTED if:
- a corresponding entry exists, but the meaning changes in a way that would alter implementation decisions or user experience.

Examples:
- subject/object swaps (“the library does X” becomes “the user does X”),
- added constraints not in source,
- removed conditions that change correctness,
- inverted priority (“taxonomy should not influence excerpting” becomes “taxonomy may guide excerpting under conditions”).

### Severity levels

Severity is required because not all completeness gaps are equally dangerous; the forensics identify foundational vision directives as highest-risk. fileciteturn3file0L1-L1

Severity is a required field on every MCU record:

- **CRITICAL**
  - Defines system purpose, excerpt definition, foundational constraints, or safety invariants.
  - Contains explicit urgency markers (“PLEASE CATCH THIS CLEARLY”, ALL‑CAPS, “nightmare”, “catastrophic”).
  - Would change what gets memorized, or whether the owner trusts the system.

- **HIGH**
  - Strong preferences or worked examples that constrain design.
  - Risk articulations that shape integrity checks.

- **MEDIUM**
  - Implementation suggestions, UI hints, or conditional preferences.

- **LOW**
  - Minor phrasing, redundant restatements, or highly local comments.

### Disposition workflow

Once a gap is classified, the remediation path is deterministic:

**MISSED**
- Create a new entry immediately:
  - If it is an excerpting rule / prompt / SPEC requirement → new MAQ entry (status `NEW`).
  - If it is a project-level directive / study workflow / agent behavior → new META entry.
  - If it is intentionally out of scope → create REJECT record (not “drop”), with reason.

**SOFTENED**
- Create a “correction delta” record referencing the existing mapped ID.
- Required action:
  - either strengthen the existing queue entry (and later its SPEC/prompt representation),
  - or split into two items (meaning + priority signal) if necessary to preserve both.
- Mandatory re-verification of the source file segment after correction.

**DISTORTED**
- Immediate escalation: treat as a correctness defect.
- Required action:
  - halt reliance on the distorted queue entry for downstream work,
  - create correction delta,
  - re-verify any downstream artifacts already derived from it (prompt, SPEC, tests) if it influenced implementation.

### Audit trail requirements

All gap findings must exist in two places:

- In `mcu_trace.jsonl` (machine-readable, complete)
- Summarized in `verification_report.md` (human-readable)

Additionally, a verification session must write a short ledger entry noting:
- batch id,
- file coverage,
- # CRITICAL/HIGH findings,
- whether the session ended with unresolved gaps.

This aligns with the protocol’s existing bias toward explicit artifacts over implicit “done” claims. fileciteturn2file0L1-L1

## Pre-mortem analysis

This pre-mortem uses the prospective hindsight technique described by entity["people","Gary Klein","cognitive psychologist"]: assume failure has already happened, then enumerate plausible causes to surface mitigations early. citeturn0search0turn0search2

### Failure scenario recap

It is October 2026. Verification sessions and adversarial reviews have been performed. Gates were passed. Reports show >95% coverage. Yet the owner later finds 15% of G-batch feedback was never captured.

### Specific failure causes

**Cause: inventory scope bug silently omitted a directory pattern**  
- Domain: Technical (tooling/scripts)  
- Warning sign: inventory file count lower than expected; repeated “0 files found” for a collection; unusually fast verification run time  
- Mitigation: gate requires both (a) manifest-derived inventory and (b) filesystem-derived inventory; any mismatch blocks gate.

**Cause: verifier defined MCUs too coarsely, undercounting meaningful units**  
- Domain: Agent (AI behavior)  
- Warning sign: very low MCU count relative to file length; high coverage with suspiciously few units  
- Mitigation: add density heuristics: “MCU count vs lines/bytes” bounds; require second-pass sampling where MCU density is anomalously low.

**Cause: verification was performed against Layer B only (layer confusion regression)**  
- Domain: Process (protocol compliance)  
- Warning sign: Layer A files show `UNVERIFIED` but overall coverage reported as high; report references mostly structured files  
- Mitigation: hard rule + script enforcement: gate fails if any Layer A file is unverified; report must have Layer A coverage section.

**Cause: context exhaustion led to partial verification with false “VERIFIED” statuses**  
- Domain: Agent (AI behavior)  
- Warning sign: verification status shows abrupt batch completion near context boundary; missing MCU trace entries for the last segment of files  
- Mitigation: status updates must be produced only via script that checks existence of MCU trace records per file; cannot mark VERIFIED without trace count >0.

**Cause: deduplication collapsed distinct owner directives into one queue entry, losing one**  
- Domain: Process + Agent  
- Warning sign: many MCUs map to the same MAQ without preserved separate source anchors; repeated “merged” notes without rationale  
- Mitigation: require “many-to-one mapping justification” when >N MCUs map to a single MAQ; preserve all source anchors.

**Cause: “softening” was treated as cosmetic and not remediated**  
- Domain: Process (governance drift)  
- Warning sign: SOFTENED findings accumulate with “acceptable” disposition; priority signals disappear from queue absolutely  
- Mitigation: severity-based rule: SOFTENED‑CRITICAL/HIGH cannot be closed without either (a) restoring strength markers, or (b) explicit owner acknowledgment that neutralization is acceptable.

**Cause: wrong-batch binding—verification artifacts corresponded to a different batch version**  
- Domain: Technical + Process  
- Warning sign: inventory hashes don’t match working tree; gate scripts pass but later diffs show file drift  
- Mitigation: inventory must record SHA‑256 per file (hash integrity); gate requires hashes match current tree (hashing integrity is standard practice for detecting message/file changes). citeturn0search3

**Cause: verification report was generated from stale trace files**  
- Domain: Technical  
- Warning sign: timestamps inconsistent; report references MCUs not in current queue; coverage.json older than inventory.json  
- Mitigation: scripts enforce monotonic timestamps; gate requires all artifacts share the same `batch_verification_run_id`.

**Cause: adversarial review sampled the wrong strata (only easy structured files)**  
- Domain: Process (review design)  
- Warning sign: sampled files are disproportionately small/structured; no review of raw notes  
- Mitigation: adversarial sampling must be stratified by layer + file size + “emphasis density” (ALL‑CAPS/exclamation markers), with mandatory Layer A inclusion.

**Cause: explicit rejection records were allowed without strong justification**  
- Domain: Organizational (governance drift)  
- Warning sign: many REJECT records marked “out of scope” with minimal reasoning; owner later disagrees  
- Mitigation: for CRITICAL/HIGH, require at least CC + one coworker sign-off on REJECT, and include owner-review flag if it affects UX principles.

**Cause: queue updates were made, but batch state was not reverted from VERIFIED to VERIFICATION_DEBT**  
- Domain: Process  
- Warning sign: new MAQ items added after verification pass without triggering re-verification  
- Mitigation: automated rule: any new MAQ/META added with source path in the batch auto-flips batch status back to `VERIFICATION_DEBT` until re-verified.

**Cause: “search-only verification” substituted for reading**  
- Domain: Agent  
- Warning sign: MCU trace contains keyword heuristics, no verbatim anchors; many “matched by keyword” mappings  
- Mitigation: enforce verbatim anchor requirement per MCU; minimum anchor length and line range required.

**Cause: “coverage >95%” metric was computed on a biased denominator**  
- Domain: Technical + Agent  
- Warning sign: coverage excludes Layer A or excludes short files; denominator is “files attempted” instead of “files in inventory”  
- Mitigation: metric definition is fixed: denominator is always inventory files and total MCUs in trace; anything else is invalid.

**Cause: owner’s own writing style (implicit directives) led to MCU detection misses**  
- Domain: Owner (communication patterns)  
- Warning sign: later discoveries are implicit assumptions not written as “should/must”  
- Mitigation: add MCU detection heuristic: treat “comparisons, metaphors, and fear statements” as MCUs; require adversarial reviewer to specifically hunt implicit constraints.

### Most likely causes given current known weaknesses

1. **Layer confusion regression** (Layer B verified, Layer A missed) because it exactly matches the original catastrophe and is easy to reintroduce if verification is not script-enforced. fileciteturn3file0L1-L1  
2. **Coverage metric gaming via under-segmentation** because MCU definition is inherently judgmental and can be unconsciously minimized.  
3. **Context exhaustion causing partial verification** because 1M-token audits over large file sets are exactly where “silent skip” behavior emerges unless progress is checkpointed.

### Most preventable causes (highest impact protocol changes)

1. **Script-enforced “no VERIFIED without MCU trace”** (prevents fake completeness).  
2. **Hash-bound inventory + drift detection** (prevents verifying the wrong file set; hashing for integrity detection is standard practice). citeturn0search3  
3. **Stratified adversarial sampling** (low cost, high leverage against correlated errors).

### Single point of failure

If the system allows anyone (human or agent) to set batch status to “complete” **without** the existence of MCU-level trace artifacts bound to the inventory, then the entire verification architecture collapses into checkbox theater. The structural defense is: *batch status is derived, not declared*—computed from artifacts, not asserted.

### Additional anti-patterns the protocol must explicitly forbid

- **Self-auditing without independence**: the same extraction prompt/template used for verification (correlated failure).  
- **Denominator manipulation**: reporting coverage on “files attempted” instead of “files in inventory.”  
- **Post-verification queue edits without status rollback**: silently invalidating the verified baseline.  
- **Over-deduplication**: merging multiple distinct directives into one queue item without preserving all source anchors.  
- **Rejection as disposal**: using REJECT as a way to avoid hardening work instead of an explicitly justified decision.

## Protocol integration patches

This section is written as concrete insertions/updates designed to be pasted into `HARDENING_SESSION_PROTOCOL.md`, preserving its conventions. fileciteturn2file0L1-L1

### Version history entry

Add under §0 “Version history”:

```text
- v5.0 (2026-04-06): ChatGPT DR Batch Lifecycle review (DRX, N findings) → adopted: batch completeness verification session type, batch completion gate, formal queue_audit methodology, verification artifact suite + scripts, anti-checkbox safeguards.
```

### New batch verification section insertion

Insert as a new section immediately after the existing intake quality gate (§3.3):

```text
## §3.4 — Batch Completeness Verification (BCV)

Purpose: structurally prevent silent omission of owner feedback by enforcing backward verification (source files → queue).

Definition: A batch is BCV-VERIFIED iff every file in the batch inventory has been audited and every Meaningful Content Unit (MCU) is traced to:
(a) a MAQ entry, (b) a META entry, or (c) an explicit rejection record.

Session type: `verification-only` (see §1.5).
Artifacts (required, committed): inventory.json, verification_status.json, mcu_trace.jsonl, coverage.json, verification_report.md.

Hard rule: No per-atom processing may begin on a batch until BCV-VERIFIED.

Procedure:
1. Run: python scripts/batch_inventory.py --batch-id <BATCH_ID>
2. Run: python scripts/batch_verification_init.py --batch-id <BATCH_ID>
3. For each file in inventory order (Layer A first, then Layer B):
   - Enumerate MCUs with verbatim anchors + line ranges.
   - Map each MCU to MAQ/META/REJECT; classify gaps as MISSED/SOFTENED/DISTORTED with severity.
   - Record in mcu_trace.jsonl; mark file VERIFIED only if MCU trace exists.
4. Generate report + coverage:
   - python scripts/batch_compute_coverage.py --batch-id <BATCH_ID>
   - python scripts/batch_generate_trace_report.py --batch-id <BATCH_ID>
5. BCV passes only when gate conditions in §1.6 are satisfied.
```

### Gate-precedence matrix update

Update §1.6 by inserting a new gate after bundle intake inventory and before prompt refactor:

```text
6. BATCH COMPLETENESS VERIFICATION GATE — If the active batch is not BCV-VERIFIED
   (per scripts/verify_batch_completion_gate.py), session type MUST be verification-only
   until BCV artifacts are complete and the gate passes.
7. PROMPT REFACTOR GATE — §4.11 ...
8. PER-ATOM PROCESSING — ...
```

(Existing gates 6 and 7 are renumbered to 7 and 8.)

### Session-type table update

Update §1.5 to add:

```text
| `verification-only` | Batch completeness verification: backward audit (sources → queue), classify MISSED/SOFTENED/DISTORTED, update MAQ/META/REJECT records | NO (may create new RAW queue entries only) | Artifact-driven; uses batch_verification/<BATCH_ID>/ suite; never mixes with other session types |
```

Update the compatibility matrix by adding `verification-only` as “FORBIDDEN” with all other types (including itself as “—”), i.e., it must be a single-purpose session, same as `intake-only`.

### Batch completion gate definition insertion

Insert within §1.6 (or as a referenced subsection near §3.4):

```text
Batch Completion Gate (BCG) — PASS iff:
- File coverage = 100% (every inventory file VERIFIED)
- No DRIFTED files
- No unresolved MISSED/SOFTENED/DISTORTED findings in mcu_trace.jsonl
- All batch MAQ items are terminal (CLOSED-*, DEFERRED-RECORDED, or REJECTED)
- verify_batch_completion_gate.py exits 0

FAIL behavior:
- Blocks per-atom work on this batch
- Blocks declaring batch complete / moving NEXT.md primary objective to next batch
- Allows debt-clearance, checkpoint resolution, and intake-only (higher precedence)
```

## New hard rules

Add to §1.4 Hard Rules:

- **Never begin per-atom processing on a batch until BCV is complete and the Batch Completion Gate passes.**  
- **Never mark a file VERIFIED without MCU trace records with verbatim anchors and line ranges.**  
- **Never verify Layer B without verifying Layer A; Layer A coverage is required for gate pass.**

(These rules follow the protocol’s “fail loud, not silent” and “raw owner text is ground truth” principles and directly prevent the documented catastrophe class.) fileciteturn2file0L1-L1 fileciteturn3file0L1-L1

## Governance conventions

### Session numbering convention

Decision: keep **global session numbering** as the canonical sequence for handoffs and continuity, because the protocol’s handoff template and governance precedence already assume a single linear sequence of sessions. fileciteturn2file0L1-L1

To preserve batch traceability without renumbering the existing system:
- Every verification artifact directory is per-batch (`batch_verification/<BATCH_ID>/`)
- Every verification report includes a `verification_run_id` that embeds:
  - batch id,
  - global session number,
  - date (e.g., `G_BCV_Session42_2026-10-12`)

This yields strong cross-batch traceability while avoiding collisions, confusion, and retrofitting cost in the established handoff workflow.