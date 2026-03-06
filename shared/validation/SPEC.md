# Algorithmic Validation — التحقق الخوارزمي — Specification

## 1. Purpose and Scope

The validation component provides a shared toolkit of deterministic, algorithmic checks that engines call to verify their own outputs and that the system calls to verify library-wide integrity. It is Layer 2 of the quality architecture (VISION.md §8.1) — the detection layer that catches mechanical errors through structural invariant enforcement, schema conformance, referential integrity, and hash-chain verification.

**What this component does.** It provides four categories of validation tools: (1) schema validators that check artifacts against JSON Schema definitions, (2) structural validators that enforce domain-specific invariants (offset integrity, passage containment, coverage completeness, type consistency), (3) referential integrity validators that verify cross-artifact references resolve correctly (source_id exists in the source registry, canonical_id exists in the scholar authority, confirmed_leaf exists in the active tree), and (4) integrity verifiers that check hash chains from frozen source files through intermediate artifacts to placed excerpts. It also provides a background sweep capability that performs library-wide integrity checks on a schedule (VISION.md §8.4).

**What this component does NOT do.** It does not perform content-level validation that requires understanding text meaning — self-containment evaluation, topic relevance, placement correctness, and scholarly accuracy are LLM-driven judgments that belong to each engine's Layer 1 self-validation or to the consensus component. It does not manage human gates — flagging conditions that trigger human review are defined by each engine's SPEC; this component reports failures that engines may use to trigger their own gates. It does not store corrections or analyze feedback patterns — that is the feedback component's responsibility. It does not construct the schemas it validates against — schemas are defined in engine SPECs and materialized as JSON Schema files during implementation.

**Phase classification.** The validation component is phase-agnostic infrastructure. It validates artifacts from all pipeline stages: source metadata (Phase 1), normalized packages (normalization boundary), passages, atoms, excerpts, placed excerpts, and entries (Phase 2 and beyond). It has no awareness of source formats — all validation operates on normalized, schema-defined structures.

**User scenarios served.** The validation component is invisible to the owner. It serves all USER_SCENARIOS.md scenarios indirectly by preventing mechanical errors from entering the library: corrupted metadata (Scenario 1), malformed passages (Scenario 2), broken referential links (Scenarios 1–8), and integrity degradation (Scenario 7 — correction integrity). The owner experiences validation through its effects — fewer errors reaching human gates, trustworthy provenance chains, and confidence that the library's stored data is uncorrupted.

**Relationship to engine self-validation.** Every engine defines its own self-validation checks in its SPEC §5. Some of those checks are algorithmic and could be implemented using this component's tools; others are engine-specific and implemented inline. This component provides reusable validation primitives that engines call — it does not replace or duplicate engine-specific validation logic. The boundary: if a check applies to a single engine's specific output format, it belongs in that engine. If a check applies to a schema shared across engines (e.g., JSON Schema compliance, referential integrity against shared registries), it belongs here.

---

## 2. Input Contract

The validation component is a library, not a service. Engines and the background sweep import validation functions and call them directly. There is no single input type — each validation category has its own input signature.

**Schema validation input.** A schema validation call receives: the artifact to validate (a Python dict or a file path to a JSON file), and either a schema identifier (a string like `"source_metadata"` or `"excerpt"` that maps to a registered schema) or a JSON Schema object directly. The component resolves schema identifiers to schema files from the schema registry (§4.A.1).

**Structural validation input.** A structural validation call receives: the artifact to validate, the check identifier (which specific structural check to run), and any check-specific parameters. For example, the offset integrity check receives an atom stream and the source text it should map to; the passage containment check receives an excerpt and the passage it claims to belong to. Each structural check's input signature is defined in §4.A.2.

**Referential integrity input.** A referential integrity call receives: a set of references to verify (e.g., a list of `source_id` values), the registry to verify against (e.g., the source registry path), and optionally a reference type identifier that selects the appropriate lookup logic. See §4.A.3 for reference types.

**Integrity verification input.** A hash verification call receives: an artifact file path and an expected hash value. A provenance chain verification call receives: a placed excerpt and the library root path. See §4.A.4 for chain verification logic.

**Background sweep input.** The sweep runner receives: the library root path, a sweep scope (full library, single science, single source), and an optional list of check categories to run. See §4.A.5.

**Validation on input.** Every validation function validates its own inputs before proceeding. A validation call with an invalid input (missing artifact, unrecognized schema identifier, unreadable file) returns a `ValidationResult` with status `error` and error code `VAL_INVALID_INPUT` — it does not raise an exception. Validation tools must never crash; they report problems, including problems with themselves.

---

## 3. Output Contract

Every validation function returns a `ValidationResult` object. This is the component's universal output format, regardless of which validation category was invoked.

**ValidationResult fields:**

- `check_id` (string): Identifier of the check that was run. Format: `{category}_{check_name}` (e.g., `schema_source_metadata`, `structural_offset_integrity`, `referential_scholar_authority`, `integrity_hash_chain`).
- `status` (enum): One of `pass`, `fail`, `warning`, `error`. `pass` means the artifact satisfies the check. `fail` means the artifact violates the check — a structural problem exists. `warning` means the artifact is technically valid but exhibits a condition that may indicate a problem (e.g., unusually high percentage of low-confidence atoms). `error` means the check itself could not complete (missing file, corrupt input, internal error).
- `severity` (enum): One of `fatal`, `blocking`, `warning`, `info`. `fatal` means the artifact must not be used — the error is unrecoverable. `blocking` means the artifact should not proceed to the next pipeline stage without resolution. `warning` means the artifact can proceed but the condition should be reviewed. `info` means the condition is logged for diagnostic purposes only. Severity is defined per check, not per invocation — each check has a fixed severity level.
- `artifact_id` (string, optional): Identifier of the artifact that was validated (source_id, passage_id, excerpt_id, etc.). Present when the artifact carries an identifier.
- `details` (list of `ValidationDetail`): One entry per specific finding within the check. A single check may produce multiple findings (e.g., schema validation may find multiple field violations). Each `ValidationDetail` contains:
  - `field_path` (string, optional): JSON path to the problematic field (e.g., `$.atoms[3].char_offsets.start`).
  - `message` (string): Human-readable description of the finding.
  - `expected` (any, optional): What was expected.
  - `actual` (any, optional): What was found.
  - `context` (dict, optional): Additional context for debugging (e.g., the atom_id, the page number, the schema rule that was violated).
- `timestamp` (string): ISO 8601 timestamp of when the check was run.
- `check_duration_ms` (int): How long the check took in milliseconds. Useful for identifying expensive checks during background sweeps.

**Batch validation output.** When multiple checks are run together (e.g., all checks for a normalized package, or a background sweep), the result is a `ValidationReport`:

- `report_id` (string): Unique identifier. Format: `valrpt_{scope}_{timestamp}_{random_4}`.
- `scope` (string): What was validated (e.g., `source:src_a3f2b1c4`, `library:full`, `science:nahw`).
- `results` (list of `ValidationResult`): All individual check results.
- `summary` (object): Aggregated counts — `total_checks`, `passed`, `failed`, `warnings`, `errors`. Also: `fatal_count` (how many fatal failures — if >0, the artifact/scope has critical problems).
- `timestamp` (string): ISO 8601 timestamp of the report.
- `duration_ms` (int): Total time for all checks.

**Metadata pass-through (D-023).** The validation component does not produce metadata that flows downstream to the synthesizer. It produces diagnostic metadata (validation reports) that is stored alongside artifacts for auditability (Layer 5). Validation reports are referenced by engine processing logs but do not enter the excerpt→entry data flow.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Schema Validation

The schema registry is a mapping from schema identifiers to JSON Schema files. During implementation, schema files are generated from engine SPEC §3 output contract definitions and stored in `schemas/`. The registry is loaded at component initialization from a configuration file that lists schema identifiers and their file paths.

**Supported schema identifiers and their engine boundaries:**

- `source_metadata` — Source engine output (§3), consumed by normalization engine (§2).
- `normalized_package_manifest` — Normalization engine output manifest (§3).
- `normalized_content_unit` — Normalization engine output per-page content unit (§3).
- `passage` — Passaging engine output (§3), consumed by atomization engine (§2).
- `atom_stream` — Atomization engine output (§3), consumed by excerpting engine (§2).
- `excerpt` — Excerpting engine output draft excerpt (§3), consumed by taxonomy engine (§2).
- `placed_excerpt` — Taxonomy engine placed excerpt (§3), consumed by synthesizing engine (§2).
- `entry` — Synthesizing engine output entry (§3).
- `scholar_authority_record` — Shared registry record for scholars.
- `work_registry_record` — Shared registry record for works.
- `consensus_audit` — Consensus component audit log entry.

Each schema identifier resolves to a JSON Schema file (Draft 2020-12 format). Schema validation uses the `jsonschema` library (v4.26+) with full Draft 2020-12 support. Validation is performed using `jsonschema.Draft202012Validator` with `format_checker` enabled for format-annotated fields (e.g., ISO 8601 dates, URI references).

**Schema validation behavior.** The validator iterates all errors (using `iter_errors`) rather than stopping at the first error. Each error becomes a `ValidationDetail` entry with the JSON path, the error message, the expected type/constraint, and the actual value. Schema validation severity is `blocking` — a schema-invalid artifact must not proceed downstream.

**Schema version tracking.** Each schema file carries a `$id` field with a version suffix (e.g., `https://kr.dev/schemas/excerpt/v1.0`). The validation component logs the schema version used for each validation. When a schema is updated, old artifacts validated against the previous version are not automatically re-validated — re-validation is triggered by the background sweep or by the engine that owns the artifact.

#### §4.A.2 — Structural Validators

Structural validators enforce domain-specific invariants that JSON Schema alone cannot express. Each validator is a standalone function with a defined input signature, a fixed severity, and a fixed error code. Engines call whichever validators apply to their output.

**CHECK: Offset Integrity (`structural_offset_integrity`).** Severity: `fatal`. Error code: `VAL_OFFSET_INTEGRITY`. Input: an atom stream (list of atom objects with `char_offsets`) and the source text they map to. Checks: (a) every atom's `char_offsets.start` < `char_offsets.end`, (b) offsets are non-overlapping when sorted, (c) the text extracted by each atom's offset range from the source text matches the atom's `text` field exactly, (d) the union of all atom offset ranges covers the entire source text with no gaps (complete coverage). Failure of any sub-check produces a `ValidationDetail` with the offending atom_id, the expected and actual values, and the specific sub-check that failed. This check is consumed by the atomization engine (SPEC §5, self-validation check 1).

**CHECK: Passage Containment (`structural_passage_containment`).** Severity: `fatal`. Error code: `VAL_PASSAGE_CONTAINMENT`. Input: an excerpt and the passage it references. Checks: every `atom_id` in the excerpt's `atom_ids` list exists in the passage's atom stream. An excerpt referencing atoms from a different passage violates D-011 (passage containment rule). This check is consumed by the excerpting engine (SPEC §5, V-1).

**CHECK: Atom Uniqueness (`structural_atom_uniqueness`).** Severity: `fatal`. Error code: `VAL_ATOM_UNIQUENESS`. Input: all excerpts from a single passage. Checks: no atom_id appears in more than one excerpt. Duplicate atom assignment indicates a boundary detection error. This check is consumed by the excerpting engine (SPEC §5, V-2).

**CHECK: Atom Coverage (`structural_atom_coverage`).** Severity: `warning`. Error code: `VAL_ATOM_COVERAGE`. Input: all excerpts from a single passage, and the passage's complete atom stream. Checks: every non-heading atom in the passage appears in exactly one excerpt. Missing atoms are reported individually. This check is consumed by the excerpting engine (SPEC §5, V-3) and the atomization engine (SPEC §5, coverage check).

**CHECK: Text Integrity (`structural_text_integrity`).** Severity: `fatal`. Error code: `VAL_TEXT_INTEGRITY`. Input: an excerpt and its referenced atoms. Checks: the excerpt's `primary_text` field matches the concatenation of its atoms' text values (joined by the configured separator, default: single space). This check is consumed by the excerpting engine (SPEC §5, V-4).

**CHECK: Arabic Text Plausibility (`structural_arabic_plausibility`).** Severity: `warning`. Error code: `VAL_ARABIC_PLAUSIBILITY`. Input: a text string and an optional page/unit identifier. Checks: (a) >70% of non-whitespace, non-punctuation characters are Arabic script (Unicode block 0600–06FF, 0750–077F, 08A0–08FF, FB50–FDFF, FE70–FEFF), (b) no runs of >20 identical characters (OCR garbage indicator), (c) no common mojibake patterns for Arabic UTF-8 encoding errors (e.g., sequences like `Ø§Ù` that indicate double-encoding). Thresholds are configurable (§8). This check is consumed by the normalization engine (SPEC §5, text extraction verification).

**CHECK: Layer Coverage (`structural_layer_coverage`).** Severity: `blocking`. Error code: `VAL_LAYER_COVERAGE`. Input: a content unit with `primary_text` and `text_layers` segments. Checks: every character position in `primary_text` is covered by exactly one `text_layers` segment — no gaps, no overlaps. This check is consumed by the normalization engine (SPEC §5, layer consistency check).

**CHECK: Division Tree Validity (`structural_division_tree`).** Severity: `blocking`. Error code: `VAL_DIVISION_TREE`. Input: a normalized package manifest with its division tree. Checks: (a) every division node has valid `start_unit_index` ≤ `end_unit_index`, (b) sibling divisions do not overlap in page ranges, (c) child divisions are contained within their parent's page range, (d) the tree covers all content units (no unit outside the root division). Uses simple range arithmetic — no external libraries needed. This check is consumed by the normalization engine (SPEC §5, division tree validity).

**CHECK: Tree Integrity (`structural_tree_integrity`).** Severity: `fatal`. Error code: `VAL_TREE_INTEGRITY`. Input: a science tree (as a NetworkX DiGraph or equivalent adjacency structure). Checks: (a) every leaf is reachable from the root (using BFS/DFS), (b) no node has zero children except leaves, (c) node IDs are unique, (d) the graph is acyclic (using NetworkX `is_directed_acyclic_graph`), (e) the graph is a valid arborescence (using NetworkX `is_arborescence`). This check is consumed by the taxonomy engine (SPEC §5, tree integrity validation).

**CHECK: Monotonic Sequencing (`structural_monotonic_sequence`).** Severity: `warning`. Error code: `VAL_MONOTONIC_SEQUENCE`. Input: a list of identifiers with embedded sequence numbers (e.g., atom_ids across passages for a source). Checks: sequence numbers are globally monotonic (strictly increasing). Non-monotonic sequences indicate a processing ordering error. This check is consumed by the atomization engine (SPEC §5, cross-passage monotonic atom_id check).

**CHECK: Excerpt Size Bounds (`structural_excerpt_size`).** Severity: `warning`. Error code: `VAL_EXCERPT_SIZE`. Input: an excerpt. Checks: atom count between 1 and 50, Arabic word count in `primary_text` between 20 and 5000. Outliers are reported with the actual values. This check is consumed by the excerpting engine (SPEC §5, V-7).

**CHECK: Footnote Integrity (`structural_footnote_integrity`).** Severity: `warning`. Error code: `VAL_FOOTNOTE_INTEGRITY`. Input: a content unit with `primary_text` and `footnotes`. Checks: (a) every footnote reference marker (`⌜N⌝`, per D-031) in `primary_text` has a corresponding entry in `footnotes` with matching index, (b) every footnote entry has non-empty text, (c) no orphaned footnotes (entries without a reference marker in the text). This check is consumed by the normalization engine (SPEC §5, footnote integrity).

#### §4.A.3 — Referential Integrity Validators

Referential integrity validators verify that cross-artifact references resolve to existing records. These checks operate against the library's registries and file system.

**CHECK: Source Registry Reference (`referential_source_registry`).** Severity: `blocking`. Error code: `VAL_REF_SOURCE`. Input: a `source_id` value and the source registry path. Checks: a source metadata file exists at the expected path (`library/sources/{source_id}/metadata.json`) and is valid JSON. Does NOT re-validate the metadata's schema (that is a separate schema validation call). This check is consumed by any engine that receives a `source_id` in its input.

**CHECK: Scholar Authority Reference (`referential_scholar_authority`).** Severity: `blocking`. Error code: `VAL_REF_SCHOLAR`. Input: a `canonical_id` value and the scholar authority registry path. Checks: a record with the given `canonical_id` exists in the scholar authority registry. This check is consumed by the source engine (SPEC §5, referential integrity check 2) and any downstream engine that carries `canonical_id` in its metadata.

**CHECK: Work Registry Reference (`referential_work_registry`).** Severity: `blocking`. Error code: `VAL_REF_WORK`. Input: a `work_id` value and the work registry path. Checks: a record with the given `work_id` exists in the work registry (including placeholder records with `status: "referenced_not_acquired"`). This check is consumed by the source engine (SPEC §5, referential integrity check 2).

**CHECK: Tree Leaf Reference (`referential_tree_leaf`).** Severity: `fatal`. Error code: `VAL_REF_LEAF`. Input: a `confirmed_leaf` node ID, a `science_id`, and the taxonomy tree path. Checks: (a) a tree for the given `science_id` exists, (b) the node ID exists in the tree, (c) the node is a leaf (has no children). A placed excerpt referencing a non-existent or non-leaf node is a critical integrity failure. This check is consumed by the taxonomy engine (SPEC §5, placement validation).

**CHECK: Atom Reference (`referential_atom`).** Severity: `fatal`. Error code: `VAL_REF_ATOM`. Input: a list of `atom_id` values and a passage file path. Checks: every referenced atom_id exists in the passage's atom stream. Missing atom references indicate data loss or corruption between atomization and excerpting. This check is consumed by the excerpting engine (SPEC §5, V-1 expansion).

**Batch referential integrity.** For efficiency, all referential integrity validators support batch mode: the caller provides a list of references to check, and the validator loads the registry once and checks all references. The result is a single `ValidationResult` with one `ValidationDetail` per failed reference.

#### §4.A.4 — Integrity Verification

Integrity verification ensures that stored artifacts have not been corrupted or tampered with since they were written. This implements VISION.md §8.4's continuous integrity property and D-033's corruption detection principle.

**CHECK: File Hash Verification (`integrity_file_hash`).** Severity: `fatal`. Error code: `VAL_HASH_MISMATCH`. Input: a file path and an expected SHA-256 hash. Checks: the file exists, is readable, and its computed SHA-256 hash matches the expected hash. Hash computation reads the file in 64KB chunks to handle large files efficiently. This is the foundation check — all other integrity checks build on hash verification. Used primarily for frozen source files (source engine SPEC §4.A.2: frozen files carry SHA-256 hashes).

**CHECK: Provenance Chain Verification (`integrity_provenance_chain`).** Severity: `fatal`. Error code: `VAL_PROVENANCE_BROKEN`. Input: a placed excerpt and the library root path. This check verifies the complete provenance chain from the placed excerpt back to the frozen source:

1. The placed excerpt's `source_id` resolves to a source metadata record.
2. The source metadata record's `frozen_files` list contains at least one file with a valid hash.
3. The frozen file exists on disk and its hash matches the recorded hash.
4. The placed excerpt's `passage_id` resolves to a passage file within the source's processing output.
5. The placed excerpt's `atom_ids` all resolve to atoms within the referenced passage.

If any link in the chain is broken (missing file, hash mismatch, missing reference), the check fails with a `ValidationDetail` identifying the broken link and its position in the chain. A broken provenance chain means the excerpt cannot be traced to its original source — a critical scholarly integrity failure (D-033 principle 5: provenance is mandatory).

**CHECK: Library Consistency (`integrity_library_consistency`).** Severity: `blocking`. Error code: `VAL_LIBRARY_INCONSISTENT`. Input: the library root path and a scope (full, per-science, per-source). This is a composite check that runs multiple sub-checks across the library:

- Every placed excerpt's `confirmed_leaf` resolves to a leaf in the current tree version for its science.
- Every source metadata record's `canonical_id` resolves in the scholar authority registry.
- Every source metadata record's `work_id` resolves in the work registry.
- Every science tree is structurally valid (tree integrity check).
- No orphaned files exist (excerpt files not referenced by any tree, source directories with no metadata record).

This check is expensive and runs as part of the background sweep (§4.A.5), not at processing time.

#### §4.A.5 — Background Sweep

The background sweep is a scheduled operation that performs library-wide integrity verification (VISION.md §8.4). It runs as a single-threaded batch process that iterates library artifacts and runs applicable checks.

**Sweep scopes.** Three scopes are supported:

- `full` — Validates every artifact in the library. Expected to run weekly or on-demand after major operations (batch imports, tree evolutions).
- `science:{science_id}` — Validates all artifacts within a single science. Useful after science-specific operations.
- `source:{source_id}` — Validates all artifacts derived from a single source. Useful after source-level reprocessing.

**Sweep phases.** The sweep runs in four phases, in order:

Phase 1: Registry integrity. Verify that the scholar authority registry and work registry are internally consistent (no duplicate canonical_ids, no orphaned work_ids). Verify that the schema registry is complete (all expected schema files exist and are valid JSON Schema).

Phase 2: Source integrity. For each source in scope: verify frozen file hashes, verify source metadata schema compliance, verify referential integrity of author and work references.

Phase 3: Artifact integrity. For each source in scope: verify that normalized packages, passages, atom streams, and excerpts conform to their schemas. Run structural checks on a sample basis for large sources (configurable sample percentage, default 10%, minimum 5 artifacts per category).

Phase 4: Library consistency. Run the library consistency check (§4.A.4) for the sweep scope. Verify cross-artifact referential integrity at all engine boundaries.

**Sweep output.** The sweep produces a `ValidationReport` (§3) containing all individual check results, plus a sweep-specific summary that includes: total artifacts checked, artifacts sampled (for sample-based checks), check-category breakdowns, and a list of artifacts with fatal or blocking failures.

**Sweep scheduling.** The sweep does not manage its own scheduling. It exposes a `run_sweep(library_root, scope, config)` function that external scheduling infrastructure (cron, the application's task runner) calls. The sweep is designed to be interruptible — it checkpoints progress after each source, so a killed sweep can resume from the last completed source.

**Sweep performance.** For a library with 100 sources and 10,000 excerpts, a full sweep should complete in under 10 minutes. The primary bottleneck is disk I/O for hash verification. Schema validation and structural checks are CPU-bound and fast. The sweep logs progress every 30 seconds and reports estimated time remaining.

#### §4.A.6 — Validation Orchestration

Engines often need to run multiple checks on a single artifact. The validation component provides an orchestration function that accepts an artifact, a list of check identifiers, and returns a `ValidationReport` with all results. The orchestrator runs checks in dependency order — schema validation before structural checks (a schema-invalid artifact may crash a structural check that assumes valid structure), referential integrity before provenance chain verification (a broken reference makes the chain check meaningless).

**Check dependencies.** The following dependency ordering is enforced:

1. Schema validation (must pass before structural checks run on the same artifact).
2. Structural checks (independent of each other — can run in any order).
3. Referential integrity (independent of structural checks).
4. Integrity verification (depends on referential integrity for chain verification).

If a check with `fatal` severity fails, subsequent checks on the same artifact in the same orchestration run are skipped — the artifact is already known to be critically broken, and running further checks wastes time and may produce misleading secondary errors. Checks with `blocking` or `warning` severity do not abort subsequent checks.

### §4.B — Transformative Capabilities

#### §4.B.1 — Validation Failure Pattern Intelligence

**What this enables that was previously impossible.** Manual quality assurance in scholarly text processing treats each error as an isolated event — a bad OCR page, a misattributed excerpt, a broken reference. But errors are not isolated. They cluster by cause: a specific source type produces specific failure patterns, a specific OCR engine fails on specific page layouts, a specific LLM model misclassifies specific scholarly structures. Detecting these patterns manually requires reviewing thousands of validation reports and recognizing recurring signatures. The validation component can do this automatically, turning error detection into error prediction and systematic quality improvement.

**Capability specification.** The validation component maintains a persistent failure log — a structured append-only store of every `ValidationResult` with status `fail` or `warning`. Each entry in the failure log carries the check result plus enrichment metadata: the `source_id` of the artifact's originating source, the source's `structural_format` (from source metadata), the source's `text_fidelity` level, the engine that produced the artifact, and the processing timestamp.

**Pattern detection.** A pattern analysis function runs periodically (triggered by the background sweep or on-demand). It computes:

- **Failure rate by check × source_type:** For each combination of check identifier and source structural format, compute the failure rate (failures / total checks). Source types with failure rates >3x the overall average for that check are flagged as systematic issues. Example: if `structural_arabic_plausibility` fails on 40% of iPhone-photo sources but only 5% of Shamela sources, the pattern "iPhone photos have high OCR quality issues" is detected.

- **Failure rate by check × engine_version:** Tracks whether failure rates change across engine code versions. A spike in failures after a code change indicates a regression.

- **Temporal clustering:** Detects whether failures cluster in time (many failures in a short period, suggesting a batch processing issue) or are evenly distributed (suggesting a systematic processing weakness).

- **Co-occurrence analysis:** Identifies checks that tend to fail together. If `structural_offset_integrity` and `structural_text_integrity` fail on the same artifacts, they likely share a root cause (corrupted atom boundaries).

**Output.** Pattern analysis produces a `ValidationPatternReport` containing: detected patterns (each with: check IDs, source type or engine version involved, failure rate, co-occurring checks), recommended actions (human-readable suggestions — e.g., "Review OCR configuration for iPhone-photo sources"), and trend indicators (improving, stable, or degrading quality for each check category).

**Technology approach.** Pattern detection uses basic statistical analysis (failure rate computation, z-score anomaly detection for temporal clustering, co-occurrence matrices). No ML models required — the patterns are statistical, not semantic. Implementation uses NumPy for numerical computation and Python's `collections.Counter` for frequency analysis. The failure log is stored as newline-delimited JSON (NDJSON) for efficient append-only writing and streaming reads.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: the background sweep producing sufficient failure data (§4.A.5), and engines consistently calling validation tools on their outputs (each engine SPEC §5 defines which checks they use).

#### §4.B.2 — Provenance Completeness Scoring

**What this enables that was previously impossible.** In manual scholarship, provenance is binary: you either know where a quote came from or you don't. But in a processing pipeline with multiple stages, provenance has degrees. An excerpt might have a verified source hash, a validated passage reference, confirmed atom boundaries — full provenance. Or it might have a source reference but a broken passage link — partial provenance. Or the source hash might not match because the frozen file was corrupted — broken provenance. Currently, scholars and library systems have no way to express or query provenance completeness as a continuous signal. KR can.

**Capability specification.** The provenance completeness scorer assigns a numerical score (0.0–1.0) to any placed excerpt or entry, reflecting how many links in its provenance chain are verified and intact.

The provenance chain has five links, each contributing 0.2 to the score:

1. **Source integrity** (0.2): The excerpt's `source_id` resolves, the source metadata is schema-valid, and at least one frozen file's hash is verified.
2. **Normalization traceability** (0.2): The source's normalized package exists, and the content unit referenced by the excerpt's passage can be located.
3. **Passage traceability** (0.2): The excerpt's `passage_id` resolves to a passage file, the passage is schema-valid, and the passage contains the atoms referenced by the excerpt.
4. **Excerpt integrity** (0.2): The excerpt itself is schema-valid, its `primary_text` matches its atoms' text concatenation, and all referential links (source_id, passage_id, atom_ids) are verified.
5. **Placement integrity** (0.2): The excerpt's `confirmed_leaf` resolves to a valid leaf in the current tree version, and the excerpt file exists at the expected library path.

Each link scores either 0.2 (fully verified), 0.1 (partially verified — the reference exists but secondary checks fail), or 0.0 (broken — the reference does not resolve). The total score is the sum.

**Consumer integration.** The provenance score is stored as metadata on placed excerpts (`provenance_completeness_score`). The synthesizing engine can use this signal when generating entries: excerpts with provenance score < 0.6 could be weighted lower or flagged in the entry's analytical layer with `grounding_type: "library_excerpt_partial_provenance"`. The scholar interface can display provenance scores, enabling the owner to identify which excerpts have the strongest evidence chain.

**Periodic recomputation.** Provenance scores are recomputed during the background sweep (Phase 4) because upstream changes (source re-processing, tree evolution) can change an excerpt's provenance completeness without modifying the excerpt itself.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: all engine boundaries producing traceable references (verified during cross-SPEC consistency check), and the background sweep (§4.A.5).

---

## 5. Validation and Quality

The validation component validates itself — this is not circular; it means the component's own outputs must be trustworthy and its own code must not introduce false positives or false negatives.

**Self-validation.** Every `ValidationResult` is schema-validated against the ValidationResult schema before being returned. If the component's own output is malformed, that is a critical bug — it returns a hard-coded error response and logs the internal failure. The component never silently returns an invalid result.

**False positive prevention.** Structural checks are deterministic — given the same input, they always produce the same result. There are no probabilistic thresholds in structural validation (unlike LLM-based content validation). This eliminates false positives from stochastic variation. The only source of false positives is bugs in the check implementation, which is addressed by the test suite (§10).

**False negative prevention.** Schema validation is comprehensive (iterates all errors, not just the first). Structural checks are explicit about what they verify and what they do not — each check's scope is defined precisely so that there is no ambiguity about which invariants are covered. If a new invariant needs checking, a new check is added; existing checks are not silently extended.

**Human gate integration.** The validation component does not have its own human gate. Validation results flow to the engine that invoked the validation, and that engine decides whether to trigger its own human gate based on the results. The validation component's contract is: report accurately, let the caller decide what to do.

**Scholarly integrity contribution.** The validation component is the mechanical backbone of D-033 (secure by design). Every deterministic invariant that can be checked algorithmically SHOULD be checked algorithmically, freeing LLM-based validation and human review to focus on content-level judgments that require understanding. Schema violations, broken references, hash mismatches, offset errors — these are all mechanical failures that deterministic code catches perfectly. An error that reaches the synthesizer despite a failed validation check represents a process failure, not a validation gap.

---

## 6. Consensus Integration

The validation component does NOT use multi-model consensus. All validation checks are deterministic algorithms — they produce the same result regardless of which model or how many models run them. Consensus is designed for content decisions where reasonable disagreement exists; structural validation has no room for reasonable disagreement — an offset is correct or it isn't, a hash matches or it doesn't.

---

## 7. Error Handling

The validation component's error philosophy: a validation check that cannot complete is ALWAYS reported as an `error` status in the `ValidationResult` — never as a silent skip, never as a false pass, never as an exception that crashes the calling engine.

**Error codes and recovery actions:**

| Code | Severity | Condition | Recovery |
|------|----------|-----------|----------|
| `VAL_INVALID_INPUT` | error | Validation function received invalid input | Return error result. Caller fixes input and retries. |
| `VAL_SCHEMA_NOT_FOUND` | error | Schema identifier not in registry | Return error result. Log missing schema. Register schema. |
| `VAL_SCHEMA_INVALID` | error | Schema file is not valid JSON Schema | Return error result. Regenerate schema file. |
| `VAL_FILE_UNREADABLE` | error | File cannot be read (permissions, encoding) | Return error result with OS error details. |
| `VAL_FILE_NOT_FOUND` | error | Target file does not exist | Return error result. |
| `VAL_INTERNAL_ERROR` | error | Unexpected exception during check | Catch, log traceback, return error result. Never propagate. |
| `VAL_SWEEP_INTERRUPTED` | warning | Background sweep interrupted | Checkpoint written. Next sweep resumes. |
| `VAL_OFFSET_INTEGRITY` | fatal | Atom offsets do not match source text | Reprocess from atomization. |
| `VAL_PASSAGE_CONTAINMENT` | fatal | Excerpt references atoms outside its passage | Reprocess excerpt. |
| `VAL_ATOM_UNIQUENESS` | fatal | Same atom in multiple excerpts | Rerun excerpting for passage. |
| `VAL_TEXT_INTEGRITY` | fatal | Excerpt text does not match atom concatenation | Reprocess excerpt. |
| `VAL_HASH_MISMATCH` | fatal | File hash does not match | Re-acquire or verify original source. |
| `VAL_PROVENANCE_BROKEN` | fatal | Provenance chain has a broken link | Re-process from broken stage. |
| `VAL_LIBRARY_INCONSISTENT` | blocking | Cross-artifact references inconsistent | Run targeted re-validation. |
| `VAL_REF_SOURCE` | blocking | source_id does not resolve | Verify source registration. |
| `VAL_REF_SCHOLAR` | blocking | canonical_id does not resolve | Verify scholar record creation. |
| `VAL_REF_WORK` | blocking | work_id does not resolve | Verify work record creation. |
| `VAL_REF_LEAF` | fatal | confirmed_leaf does not resolve to active leaf | Run excerpt migration. |
| `VAL_REF_ATOM` | fatal | atom_id does not resolve in passage | Reprocess from atomization. |
| `VAL_ARABIC_PLAUSIBILITY` | warning | Text fails Arabic plausibility checks | Review OCR quality. |
| `VAL_LAYER_COVERAGE` | blocking | Character positions not fully covered | Rerun normalization. |
| `VAL_DIVISION_TREE` | blocking | Division tree has structural problems | Rerun normalization. |
| `VAL_TREE_INTEGRITY` | fatal | Science tree has structural corruption | Repair or rollback tree. |
| `VAL_MONOTONIC_SEQUENCE` | warning | Identifiers not monotonically ordered | Review processing order. |
| `VAL_EXCERPT_SIZE` | warning | Excerpt size outside bounds | Review excerpting config. |
| `VAL_FOOTNOTE_INTEGRITY` | warning | Footnote references inconsistent | Review normalization footnotes. |

**Logging.** Every validation check logs: the check_id, the artifact_id (if available), the status, and the duration. Fatal and blocking failures at ERROR level. Warnings at WARN level. Passes at DEBUG level to avoid log flooding. The background sweep logs a summary at INFO level after each source and a full summary at completion.

**Pipeline control separation.** Validation results are returned to the calling engine — the validation component does not block the pipeline itself. Each engine defines in its own SPEC §5 which validation failures are blocking. The validation component provides severity classification; the engine decides the action.

---

## 8. Configuration

**Schema registry configuration:**

- `schema_registry_path` (string, default: `schemas/registry.json`): Path to the schema registry mapping file.
- `schema_base_dir` (string, default: `schemas/`): Base directory for schema files.

**Structural check thresholds:**

- `arabic_plausibility_min_ratio` (float, default: 0.70): Minimum ratio of Arabic characters. Configurable per source type.
- `arabic_plausibility_max_identical_run` (int, default: 20): Maximum consecutive identical characters.
- `excerpt_min_atoms` (int, default: 1): Minimum atoms per excerpt.
- `excerpt_max_atoms` (int, default: 50): Maximum atoms per excerpt.
- `excerpt_min_words` (int, default: 20): Minimum Arabic words in excerpt text.
- `excerpt_max_words` (int, default: 5000): Maximum Arabic words in excerpt text.

**Background sweep configuration:**

- `sweep_sample_percentage` (float, default: 0.10): Sample percentage for large sources. Range: 0.01–1.0.
- `sweep_sample_minimum` (int, default: 5): Minimum artifacts per category.
- `sweep_checkpoint_interval` (int, default: 1): Checkpoint after every N sources.
- `sweep_progress_log_interval_seconds` (int, default: 30): Progress log frequency.

**Hash configuration:**

- `hash_algorithm` (string, default: `sha256`): Hardcoded for now; configurable for forward compatibility.
- `hash_chunk_size` (int, default: 65536): Chunk size for file hash computation.

**Failure log configuration (§4.B.1):**

- `failure_log_path` (string, default: `library/diagnostics/validation_failures.ndjson`): Failure log file.
- `failure_log_max_size_mb` (int, default: 100): Maximum size before rotation.
- `pattern_analysis_min_samples` (int, default: 50): Minimum records before pattern analysis.

**What is configurable vs. hardcoded.** Thresholds are configurable because valid ranges vary by source type and science. The hash algorithm is configurable for future-proofing. Check definitions (what each check verifies) are hardcoded. Severity levels are hardcoded per check. Error codes are hardcoded — they are part of the API contract.

---

## 9. Current Implementation State

**Existing files:**

- `shared/validation/src/cross_validate.py` (393 lines): ABD-era cross-validation with three LLM-based checks. **ABD legacy (D-019):** Implements content-level validation, not algorithmic validation. The algorithmic field-checking function (`_check_fields_algorithmic`) is a useful implementation reference for excerpt schema validation. LLM components are out of scope for this component.

- `shared/validation/src/run_all_validations.py` (106 lines): ABD-era CI runner for gold baselines. **ABD legacy:** Gold baseline discovery pattern is relevant to sweep design (§4.A.5) but tightly coupled to ABD file layout.

- `shared/validation/tests/test_cross_validate.py`: Tests for ABD-era code. Will need rewrite.

**Known gaps — everything is [NOT YET IMPLEMENTED]:**

- Schema validation infrastructure (§4.A.1) — no registry, no JSON Schema validation calls.
- All 12 structural validators (§4.A.2) — none exist as reusable functions.
- All 5 referential integrity validators (§4.A.3) — no cross-registry checking.
- All integrity verification checks (§4.A.4) — no hash or provenance chain verification.
- Background sweep (§4.A.5) — no library-wide sweep infrastructure.
- Validation orchestration (§4.A.6) — no multi-check orchestration.
- Failure pattern intelligence (§4.B.1) — no failure log or pattern analysis.
- Provenance completeness scoring (§4.B.2) — no scoring function.
- ValidationResult/ValidationReport Pydantic v2 models — not implemented.
- JSON Schema files regenerated from engine SPECs — current files are ABD-era.

**External tools and libraries:**

- `jsonschema` (v4.26+, PyPI): JSON Schema validation, Draft 2020-12. Pure Python.
- `Pydantic` (v2.12+, PyPI): Runtime type validation for output models. Already a project dependency.
- `hashlib` (Python stdlib): SHA-256 hash computation. No installation needed.
- `NetworkX` (v3.x, PyPI): Graph validation for tree integrity. Already a project dependency.
- `NumPy` (PyPI): Numerical computation for pattern analysis. Already a project dependency.

No new external dependencies introduced.

---

## 10. Test Requirements

**Schema validation tests.** For each registered schema identifier: (a) validate a known-good artifact (must pass), (b) validate with each required field removed (must fail with specific field_path), (c) validate with type violations (must fail with specific message), (d) validate with format violations for date/URI fields. Minimum: 5 test cases per schema.

**Structural check tests.** For each check: (a) pass case, (b) fail case for each sub-check, (c) edge cases (empty input, single-element input, maximum-size input). Each test verifies error code, severity, and ValidationDetail content. Minimum: 3 test cases per check.

**Referential integrity tests.** For each reference type: (a) resolves successfully, (b) does not resolve, (c) batch mode with mixed valid/invalid. Tests use temporary library with known registry contents.

**Integrity verification tests.** (a) Hash matches, (b) hash does not match, (c) file does not exist, (d) provenance chain fully intact, (e) chain with each of 5 links broken individually. Tests use minimal temporary library with known hashes.

**Background sweep tests.** (a) Full sweep on minimal library completes clean, (b) sweep detects seeded error in correct phase, (c) checkpoint/resume works, (d) scoping works (source-scoped checks only specified source).

**Orchestration tests.** (a) Dependency ordering, (b) fatal failure skips subsequent checks, (c) blocking failure does NOT skip subsequent checks.

**Regression strategy.** Adding a new check must not break existing tests. Schema updates require corresponding test updates. The minimal-library sweep test serves as integration regression.

**Gold baselines.** No gold baselines for validation itself (it is deterministic — the test suite IS the baseline). The validation component is infrastructure for other engines' gold baselines — engine regression tests call validation checks on their outputs.
