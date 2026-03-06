# Feedback Loop Infrastructure — حلقة التغذية الراجعة — Specification

## 1. Purpose and Scope

The feedback component is the learning infrastructure that makes KR improve over time. It is Layer 3 of the quality architecture (VISION.md §8.1 — Correction) — the mechanism by which errors detected at human gates and through owner corrections are recorded, analyzed for systemic patterns, transformed into training data for engine optimization, and verified through regression testing before new rules take effect.

**What this component does.** It provides five capabilities: (1) correction recording — structured capture of every instance where the owner corrects the application's output, including what was proposed, what it was corrected to, why, and which engine at which processing stage produced the incorrect output, (2) pattern analysis — detecting systemic patterns across accumulated corrections that indicate a common root cause in an engine's processing rules, (3) training data management — organizing corrections into DSPy-compatible training examples that individual engines consume for prompt optimization, (4) regression test coordination — managing gold baseline collections, orchestrating regression test runs when engine rules or models change, and blocking updates that degrade quality on previously correct outputs, and (5) model change monitoring — detecting when underlying LLM models used by any engine are updated and triggering mandatory regression tests.

**What this component does NOT do.** It does not optimize prompts — each engine owns its own DSPy programs, signatures, and optimization runs. The feedback component provides the structured correction data and gold baselines that engines use as training and validation sets. It does not present corrections to the owner or manage the review interface — that is the scholar interface's responsibility (D-016). It does not manage human gate checkpoints or their lifecycle — that is the human gate component's responsibility. It does not decide what constitutes a correct excerpt, placement, or entry — each engine defines its own correctness criteria. It does not modify library state (placed excerpts, entries, taxonomy trees) — engines perform their own corrections using data this component provides.

**The core insight.** Every owner correction is an investment. A single correction to a school misattribution should not just fix one excerpt — it should improve how the excerpting engine handles school attribution across ALL future excerpts. The feedback component exists to transform individual corrections into systemic improvements. Without it, KR makes the same mistakes repeatedly; with it, KR accumulates the owner's scholarly expertise into its processing rules over time. This is what makes KR a learning system rather than a static pipeline.

**Phase classification.** The feedback component is phase-agnostic infrastructure. It consumes corrections from all engines across both pipeline phases. However, its outputs are consumed differently: Phase 2 engines (excerpting, taxonomy, synthesis) generate more corrections than Phase 1 engines (source, normalization, passaging) because Phase 2 involves more subjective scholarly judgments. The component treats all corrections uniformly regardless of source engine.

**User scenarios served.** Scenario 8 (KR Gets It Wrong) is the primary scenario — the feedback component is the mechanism by which Scenario 8's "pattern flagged" step works. Scenario 2 (Active Study) benefits because corrections made during active study sessions improve future processing quality. Every scenario benefits indirectly because the feedback component's systemic improvements raise baseline quality for all engine outputs.

---

## 2. Input Contract

The feedback component receives input from three paths.

**Correction records from human gate resolutions.** When the owner resolves a human gate checkpoint with `resolution: "modified"` or `resolution: "rejected"`, the feedback component receives a correction notification containing: `checkpoint_id` (linking to the full checkpoint record in the human gate archive), `gate_type`, `engine_id`, `artifact_id`, `science` (if applicable), `resolution` (modified or rejected), `original_output` (the engine's proposed output — extracted from the checkpoint payload), `corrected_output` (the owner's modification — extracted from the checkpoint modifications, or null for rejections), `reason` (the owner's explanation, if provided), and `timestamp`. The feedback component reads the full checkpoint record from the human gate's resolved archive to obtain additional context (confidence scores, review flags, related checkpoints). This is a pull model, not a push model: the feedback component periodically scans the human gate's resolved archive for new resolutions that haven't been processed yet.

**Direct owner corrections from the scholar interface.** When the owner identifies an error outside the human gate flow — for example, spotting a factual error in a generated entry (Scenario 8) — the correction arrives as: `correction_type` (one of `factual_error`, `attribution_error`, `school_misattribution`, `placement_error`, `missing_content`, `excess_content`, `relationship_error`, `structural_feedback`), `target_type` (one of `entry`, `excerpt`, `placement`, `source_metadata`, `taxonomy_node`), `target_id` (the identifier of the corrected artifact), `engine_id` (which engine is responsible — inferred from target_type if not explicit), `science` (if applicable), `description` (owner's explanation of the error), `correction_data` (structured correction details — schema depends on correction_type and target_type), and `timestamp`. The scholar interface submits these corrections through a function call.

**Model change notifications.** When any engine updates its underlying LLM model (new version, changed provider, updated configuration), it notifies the feedback component with: `engine_id`, `model_role` (what the model is used for in that engine — e.g., `boundary_detection`, `self_containment_evaluation`, `placement_ranking`), `old_model` (model identifier string), `new_model` (model identifier string), `change_timestamp`. This triggers mandatory regression testing (VISION.md §8.3).

**Validation on input.** Correction records must have a non-empty `engine_id` and a valid `correction_type`. Direct corrections must have a non-empty `target_id` and a recognized `target_type`. Model change notifications must have both `old_model` and `new_model` (which must differ). Malformed inputs are rejected with `FEEDBACK_INVALID_INPUT` and logged. The feedback component never silently drops a correction — every submission is either accepted and recorded, or rejected with a specific error.

---

## 3. Output Contract

The feedback component produces four categories of output, each consumed by different downstream systems.

**Correction database.** The persistent, structured archive of all recorded corrections. Each correction record contains:

- `correction_id` (string): Unique identifier, format `cor_{8_char_hash}_{timestamp}`.
- `source` (string): One of `human_gate` or `direct_correction`.
- `checkpoint_id` (string, optional): Link to the human gate checkpoint, if the correction originated there.
- `correction_type` (string): The category of error (see §2 for the enumeration).
- `target_type` (string): What was corrected (entry, excerpt, placement, etc.).
- `target_id` (string): The corrected artifact's identifier.
- `engine_id` (string): The responsible engine.
- `science` (string, optional): The science context.
- `model_id` (string, optional): The LLM model that produced the incorrect output, if known.
- `original_output` (dict): What the engine proposed.
- `corrected_output` (dict, optional): What the owner corrected it to (null for rejections).
- `reason` (string, optional): Owner's explanation.
- `confidence_at_production` (float, optional): The engine's confidence when it produced the incorrect output. Extracted from checkpoint payload or engine metadata. High-confidence errors are more informative for pattern analysis than low-confidence ones.
- `review_flags_at_production` (list, optional): Any review flags present when the error was produced.
- `timestamp` (string, ISO 8601): When the correction was recorded.
- `pattern_ids` (list of strings): Pattern identifiers this correction has been associated with (populated by pattern analysis, initially empty).
- `training_status` (string): One of `unprocessed`, `included`, `excluded`. Whether this correction has been incorporated into training data.

**Training data exports.** Per-engine collections of correction-derived examples formatted for DSPy consumption. Each export is a JSON file at `library/feedback/training/{engine_id}/corrections.json` containing an array of DSPy-compatible examples. Each example contains: `input` (the input that was processed — passage text, excerpt, placement context, etc.), `expected_output` (the owner's corrected output), `metadata` (correction_id, science, correction_type, timestamp). The specific fields within `input` and `expected_output` depend on the engine's DSPy signature — the feedback component uses engine-registered schemas to format the data correctly (see §4.A.4). Training data exports are regenerated whenever new corrections are recorded for an engine.

**Pattern reports.** When the pattern analysis engine detects a systemic pattern, it produces a pattern report containing:

- `pattern_id` (string): Unique identifier, format `pat_{engine_id}_{sequence}`.
- `engine_id` (string): The engine with the systemic issue.
- `pattern_type` (string): The category of pattern (see §4.A.3 for the taxonomy).
- `description` (string): Human-readable explanation of the pattern.
- `evidence` (dict): The corrections that constitute this pattern, with counts and examples.
- `severity` (string): One of `critical`, `significant`, `minor`. Based on correction frequency and impact.
- `suggested_action` (string): What should be done — one of `prompt_optimization`, `rule_update`, `architecture_review`, `data_quality_check`.
- `affected_scope` (dict): What's affected — science, source, correction_type, confidence_range.
- `created_at` (string, ISO 8601).
- `status` (string): One of `detected`, `acknowledged`, `resolved`, `dismissed`.

Pattern reports are stored at `library/feedback/patterns/` and are consumed by: (1) the scholar interface, which presents them to the owner as "KR is learning" transparency notifications, and (2) the owning engine's optimization pipeline, which uses them as signals to trigger a prompt optimization run.

**Regression test results.** When a regression test suite runs (triggered by model change, prompt update, or manual request), the component produces a result report containing:

- `run_id` (string): Unique identifier.
- `trigger` (string): What triggered this run (model_change, prompt_update, manual).
- `engine_id` (string): Which engine's baselines were tested.
- `baseline_count` (integer): How many gold baseline examples were tested.
- `pass_count` (integer): How many passed.
- `fail_count` (integer): How many regressed.
- `new_pass_count` (integer): How many previously failing examples now pass (improvement).
- `failures` (list): Detailed failure records with baseline input, expected output, actual output, and delta.
- `verdict` (string): One of `pass` (no regressions), `fail` (regressions detected), `degraded` (quality decreased but within tolerance).
- `timestamp` (string, ISO 8601).

Regression results are stored at `library/feedback/regression_runs/` and determine whether an engine update is applied to production.

**Metadata pass-through (D-023).** The feedback component does not sit in the main processing pipeline — it is a side-channel that consumes checkpoint archives and direct corrections. It does not transform or pass through pipeline artifacts. However, correction records preserve all metadata from the original checkpoint payload and the owner's modifications, ensuring that the full context of every correction is available for pattern analysis and training data generation.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Correction Recording

The feedback component processes corrections from two sources with different intake paths, producing a unified correction record for both.

**Human gate corrections.** The component periodically scans the human gate's resolved checkpoint archive (`library/gates/resolved/`) for checkpoints resolved as `modified` or `rejected` that have not yet been recorded. The scan frequency is configurable (default: on-demand when any engine signals a processing run, plus a configurable periodic interval). For each unprocessed checkpoint, the component:

1. Reads the full checkpoint record from the archive.
2. Extracts the original engine output from the checkpoint's `payload`.
3. Extracts the owner's correction from the checkpoint's `modifications` (for `modified` resolutions) or records the rejection (for `rejected` resolutions).
4. Identifies the responsible engine from the checkpoint's `engine_id` and `gate_type`.
5. Extracts confidence-at-production from the payload's confidence fields (gate-type-specific — the component maintains a mapping from gate_type to the payload field containing confidence).
6. Creates a unified correction record with all fields from §3.
7. Writes the correction record to `library/feedback/corrections/{year-month}/`.
8. Marks the checkpoint as processed by recording its `checkpoint_id` in `library/feedback/processed_checkpoints.jsonl` (append-only ledger to prevent re-processing).

Auto-approved checkpoints (human gate's pre-approval policies) are NOT recorded as corrections — they represent decisions the owner implicitly agrees with. Only explicit owner modifications and rejections enter the correction database.

**Direct owner corrections.** When the scholar interface submits a direct correction, the component:

1. Validates the correction against the input contract (§2).
2. Resolves the `engine_id` from the `target_type` if not explicitly provided. The mapping is: `entry` → `synthesis`, `excerpt` → `excerpting`, `placement` → `taxonomy`, `source_metadata` → `source`, `taxonomy_node` → `taxonomy`.
3. Retrieves the current state of the target artifact to populate `original_output`.
4. Creates a unified correction record.
5. Writes and indexes the record.

**Correction immutability.** Once written, correction records are never modified or deleted. They are append-only historical facts. If a correction is later found to be wrong (the owner reverses their correction), a new correction record is created that supersedes the original — the original is marked with `superseded_by: {new_correction_id}` but not deleted. This preserves the complete audit trail and prevents training data poisoning from silent record changes.

#### §4.A.2 — Correction Indexing

The correction database is indexed along multiple dimensions to support efficient pattern analysis. The component maintains secondary index files (JSON) at `library/feedback/indexes/`:

- `by_engine.json`: Maps `engine_id` → list of `correction_id` values, sorted by timestamp.
- `by_science.json`: Maps `science` → list of `correction_id` values.
- `by_type.json`: Maps `correction_type` → list of `correction_id` values.
- `by_source.json`: Maps `source_id` (of the source that produced the corrected artifact) → list of `correction_id` values.
- `by_model.json`: Maps `model_id` → list of `correction_id` values.

Indexes are updated incrementally when new corrections are recorded. They are rebuilt from scratch if they become corrupted (detected by a count mismatch between the index and the actual correction files).

The component also maintains aggregate counters in `library/feedback/stats.json`:
- Total corrections by engine, by science, by type, by model.
- Corrections per time period (weekly, monthly).
- Correction rate trends (is the rate increasing, decreasing, or stable per engine?).

#### §4.A.3 — Pattern Analysis

Pattern analysis is the intelligence layer that transforms individual corrections into systemic insights. It runs incrementally: after each new correction is recorded, the component checks whether it contributes to a known pattern or forms a new one.

**Pattern taxonomy.** The feedback component detects the following pattern types:

- `type_concentration`: A single correction_type dominates an engine's corrections within the analysis window. Trigger: one correction_type accounts for ≥40% of the corrections in the window AND the window contains at least 20 corrections for this engine. Example: 8 of 20 excerpting corrections are `school_misattribution` — the excerpting engine's school identification rules need improvement.

- `science_concentration`: Corrections cluster in a specific science. Trigger: one science accounts for ≥50% of the corrections in the window AND the window contains at least 20 corrections. Example: most taxonomy placement errors are in Fiqh — the Fiqh tree may have structural issues.

- `source_concentration`: Corrections cluster around a specific source. Trigger: one source accounts for ≥30% of corrections in a 30-day window. Example: a specific source generates disproportionate errors — may indicate source quality issues rather than engine issues.

- `model_concentration`: Corrections cluster around a specific LLM model. Trigger: one model accounts for ≥60% of corrections when multiple models are in use. Example: Model A produces more errors than Model B on the same tasks — may indicate model degradation or poor model-task fit.

- `confidence_miscalibration`: The engine's confidence scores don't predict correctness. Trigger: ≥30% of corrections occur on outputs where the engine reported confidence ≥0.80. Example: the excerpting engine thinks it's right when it's wrong — its confidence calibration needs adjustment.

- `recurring_pair`: The same input pattern repeatedly produces the same error. Trigger: ≥3 corrections with the same (engine_id, correction_type, input_signature) triple within 60 days. The `input_signature` is a canonicalized representation of the input that caused the error: for excerpting corrections, it is the combination of (source_format, layer_count, scholarly_function_of_first_atom); for taxonomy corrections, it is (science, proposed_leaf_depth); for synthesis corrections, it is (science, excerpt_count_at_leaf). The purpose of canonicalization is to detect when structurally similar inputs repeatedly cause the same error type, even if the specific text differs. Example: every time a passage contains an implicit reported opinion (حكي/قيل), the excerpting engine misattributes it — the input_signature captures this as (shamela, single_layer, reported_position).

- `correction_cascade_needed`: A correction at one artifact implies corrections may be needed at related artifacts. Trigger: a correction to source metadata (author ID, school) implies all excerpts from that source may have the same metadata error. (See §4.B.1 for the full cascade intelligence specification.)

**Pattern detection algorithm.** Pattern analysis uses a sliding window approach:

1. For each new correction, the component retrieves the correction's engine, science, type, source, and model from the indexes.
2. It computes the distribution of corrections along each dimension within the analysis window. The analysis window is the intersection of two constraints: at most the last `pattern_window_count` corrections for this engine (default: 50) AND at most the last `pattern_window_days` days (default: 90). If an engine has 100 corrections in the last 30 days, the window includes only the most recent 50. If an engine has 10 corrections in 90 days, the window includes all 10. If an engine has fewer than 20 corrections total, pattern analysis is deferred — there is not enough data for statistically meaningful patterns.
3. It checks each distribution against the pattern-specific thresholds defined above.
4. If a threshold is crossed, it checks whether an existing pattern already captures this concentration (same engine + same pattern_type + overlapping evidence). If yes, the existing pattern is updated with the new correction. If no, a new pattern is created.
5. Patterns with `status: "detected"` that have not received new evidence in 90 days are automatically moved to `status: "stale"`. Stale patterns are not deleted — they remain in the archive for historical analysis.

**Severity assignment.** A pattern's severity is computed from two factors: frequency (how many corrections contribute) and impact (what was affected). `critical`: ≥10 corrections AND the corrections involve verified-tier content or entry-level errors. `significant`: ≥5 corrections OR corrections affect multiple sciences. `minor`: all others (3-4 corrections, single science, low-impact corrections).

**Pattern analysis is purely statistical.** It uses counting, distribution analysis, and threshold comparison. No LLM calls. No ML models. This is deliberate: pattern analysis must be deterministic, fast, and auditable. The intelligence in interpreting patterns and deciding what to do belongs to the owning engine's optimization pipeline and to the owner's judgment — not to the feedback component.

#### §4.A.4 — Training Data Management

The feedback component maintains per-engine collections of DSPy-compatible training examples derived from corrections. This is the bridge between "the owner corrected an error" and "the engine's prompts improve."

**Engine registration.** Each engine registers with the feedback component by providing: (1) its `engine_id`, (2) a list of `task_signatures` — named DSPy signature schemas that the engine uses for LLM calls. Each task signature specifies: `signature_name` (e.g., `school_attribution`, `self_containment_evaluation`, `placement_ranking`), `input_fields` (list of field names and types), `output_fields` (list of field names and types), and `correction_type_mapping` (which correction_types map to this signature). Registration is stored in `library/feedback/engine_registry.json`.

The registration tells the feedback component: "When you see a correction of type `school_misattribution` for engine `excerpting`, format it as a training example for the `school_attribution` signature with these input/output fields." Without registration, the feedback component stores the raw correction but cannot produce formatted training data — the engine must handle formatting itself.

**Training example generation.** When a new correction is recorded for a registered engine, the component:

1. Identifies which task signature(s) the correction maps to, using the `correction_type_mapping` from the engine's registration.
2. Extracts the input fields from the correction's context. For human gate corrections, the `original_output` dict contains the full checkpoint payload, which includes all information the engine provided when creating the checkpoint — for excerpting gates, this means the passage text, atom sequence, and draft excerpt; for taxonomy gates, this means the excerpt, proposed leaf, and candidate alternatives; for source gates, this means the source metadata and candidate matches. For direct corrections, the component reads the target artifact from the library to reconstruct the input context. If a required input field cannot be extracted (the checkpoint payload does not contain the needed data), the training example is excluded with `training_status: "excluded"` and a warning log identifying the missing field.
3. Sets the output fields to the owner's corrected values from `corrected_output`.
4. Creates a DSPy example object: `{"input": {...}, "expected_output": {...}, "metadata": {"correction_id": ..., "science": ..., "timestamp": ...}}`.
5. Appends the example to the engine's training data file at `library/feedback/training/{engine_id}/{signature_name}.json`.

**Training data quality.** Not all corrections produce good training examples. The component applies quality filters:
- Corrections without a `corrected_output` (rejections without an alternative) are excluded from training data but included in pattern analysis.
- Corrections that have been superseded are excluded.
- Corrections where the owner provided no structured correction data (only a free-text description) are flagged as `training_status: "excluded"` — they inform pattern analysis but cannot be formatted as DSPy examples.

**Training data versioning.** Each time the training data for an engine is updated, the component increments a version counter stored in the training data file's header. The engine checks this version before optimization runs to determine whether new training data is available since the last optimization.

#### §4.A.5 — Regression Test Coordination

The feedback component coordinates regression testing across all engines. It does not run the tests itself — each engine implements its own regression test logic against its own gold baselines. The feedback component manages the orchestration: what triggers a test, what baselines exist, whether the result permits an update.

**Gold baseline registry.** The component maintains a registry of gold baseline collections at `library/feedback/baselines/registry.json`. Each entry contains: `engine_id`, `baseline_set_name`, `baseline_path` (directory containing gold examples), `baseline_count` (number of examples), `created_at`, `last_validated` (when the baselines were last run), `last_result` (pass/fail), and `required_pass_rate` (minimum proportion that must pass — default 1.0 for gold baselines, configurable per engine).

Gold baselines are distinct from training data. Gold baselines are manually verified, immutable ground truth examples that test whether the engine STILL works correctly. Training data is owner corrections that teach the engine to work BETTER. A regression test verifies that "learning to work better" didn't break "working correctly."

**Regression test triggers.** Three events trigger mandatory regression testing:

1. **Model change.** When the feedback component receives a model change notification (§2), it creates a regression test request for the affected engine. The engine must run its full gold baseline suite against the new model before using it in production. If the test fails (any gold baseline regresses), the model change is blocked — the engine must continue using the previous model until the issue is resolved.

2. **Prompt update.** When an engine completes a DSPy optimization run and produces updated prompts, it notifies the feedback component with: `engine_id`, `signature_name`, `old_prompt_hash`, `new_prompt_hash`. The feedback component creates a regression test request. The engine must run its gold baseline suite against the new prompts before applying them.

3. **Manual request.** The owner or an engine can request a regression test at any time.

**Regression test protocol.** A regression test run proceeds as follows:

1. The feedback component records the test request in `library/feedback/regression_runs/pending/`.
2. The owning engine receives the request (by checking for pending requests at processing start).
3. The engine runs its gold baseline suite and reports results back to the feedback component.
4. The feedback component records the result, updates the baseline registry's `last_validated` and `last_result`, and produces the regression test result report (§3).
5. If the verdict is `pass`, the engine may apply the update. If `fail`, the update is blocked. If `degraded` (quality decreased but within a configured tolerance), the result is flagged for owner review — the owner decides whether to accept the degradation.

**Blocking semantics.** "Blocked" means the feedback component records that the update has not passed regression testing. Enforcement is cooperative: the engine checks the regression result before applying an update. There is no technical lock — KR is a single-user, batch-processing system where cooperative enforcement is sufficient. The audit trail ensures that any update applied without passing regression is detectable after the fact.

#### §4.A.6 — Model Change Monitoring

The feedback component tracks which LLM models each engine uses and detects changes. Each engine self-reports its model configuration at startup by writing a model manifest to `library/feedback/models/{engine_id}.json` containing: `engine_id`, a list of `model_assignments` (each with: `model_role`, `model_id`, `provider`, `last_updated`).

At each processing run, the feedback component compares the current model manifest against the previous version. If any `model_id` has changed for a given `model_role`, it generates a model change notification and triggers regression testing (§4.A.5). The previous manifest is archived at `library/feedback/models/archive/{engine_id}_{timestamp}.json`.

Model change detection is critical because VISION.md §1.9 identifies silent behavioral drift as a risk. A model provider may update a model's weights without changing the model identifier (e.g., `gpt-4o` may silently improve or degrade). For this reason, the feedback component also supports periodic regression tests (configurable interval, default: weekly) that run gold baselines against current models to detect silent drift, regardless of whether a model_id change was detected.

#### §4.A.7 — Correction Lifecycle and Cleanup

Correction records are permanent. They are never deleted. However, the component manages the lifecycle of associated artifacts:

**Training data refresh.** When an engine's DSPy optimization run succeeds and the new prompts pass regression testing, the feedback component marks all corrections that were included in the training data with `training_status: "included"` and records which optimization run consumed them. Future corrections continue to accumulate for the next optimization cycle.

**Pattern resolution.** When the owner or an engine acknowledges a pattern and takes action (prompt optimization, rule update), the pattern status changes to `acknowledged`. After the action passes regression testing, the pattern status changes to `resolved`. New corrections of the same type reset the status to `detected` if the pattern recurs — indicating the fix was insufficient.

**Statistics refresh.** Aggregate statistics are recomputed on demand (when queried) and cached for the configured interval (default: 1 hour). Stale statistics are acceptable for monitoring; they do not affect processing decisions.

### §4.B — Transformative Capabilities

#### §4.B.1 — Correction Cascade Intelligence

**Capability:** When a correction implies that related artifacts may share the same error, the feedback component detects this and generates cascade review signals — proactive notifications that other artifacts need attention, without waiting for the owner to discover each error individually.

**Why this is transformative.** In manual scholarship, finding one error in a source often means checking other passages from the same source for similar issues. A scholar who discovers that a particular edition misattributes commentary text to the matn author doesn't just fix one passage — they suspect ALL passages from that edition may have the same problem. KR should exhibit the same scholarly awareness. Without cascade intelligence, each error is an isolated fix; with it, one correction triggers a systematic review that prevents the same class of error from persisting elsewhere.

**Cascade rules.** The component maintains a set of cascade rules that define which corrections imply broader impacts:

1. **Author correction cascade.** If the owner corrects the author attribution of a source (at the source engine level), all excerpts from that source may have incorrect author metadata. Cascade signal: mark all excerpts from the affected `source_id` as needing author metadata review. Scope: all excerpts where `source_id` matches.

2. **School correction cascade.** If the owner corrects the school attribution of an excerpt, other excerpts from the same source AND the same author may have the same misattribution. Cascade signal: flag excerpts from the same source with the same `author_id` for school attribution review. Scope: same source + same author.

3. **Layer attribution cascade.** If the owner corrects which text layer (matn vs. sharh) an excerpt's content belongs to, other passages from the same source may have the same layer confusion. Cascade signal: flag all normalized pages from the same source for layer attribution review. Scope: all content units from the same source.

4. **Placement correction cascade.** If the owner moves an excerpt from Leaf A to Leaf B, other excerpts with similar topic metadata at Leaf A may also belong at Leaf B. Cascade signal: flag excerpts at Leaf A whose topic keywords overlap with the moved excerpt. Scope: excerpts at the original leaf with topic similarity above a threshold.

5. **Trust reclassification cascade.** If the owner reclassifies a source's trust tier (verified → flagged or flagged → verified), all excerpts from that source need their classification updated. Cascade signal: mark all excerpts from the source for reclassification. Scope: all excerpts from the affected source.

**Cascade signal format.** A cascade signal is a structured notification written to `library/feedback/cascades/pending/`:
- `cascade_id` (string): Unique identifier.
- `trigger_correction_id` (string): The correction that triggered this cascade.
- `cascade_rule` (string): Which rule fired.
- `affected_artifacts` (list): Identifiers of artifacts that need review, with the reason.
- `priority` (string): Derived from the triggering correction's impact — `high` if the correction affects verified-tier content, `normal` otherwise.
- `status` (string): One of `pending`, `in_review`, `completed`, `dismissed`.

The scholar interface presents pending cascade signals to the owner as "KR suspects related issues." The owner can review the affected artifacts in batch. If the owner dismisses a cascade (the related artifacts are actually correct), the dismissal is recorded — and feeds back into the cascade rules' precision metrics so the component can tighten thresholds for false-positive-prone rules over time.

**Technical approach.** Cascade detection is rule-based: each correction is checked against the cascade rule set using the correction's metadata (engine_id, correction_type, target_id, source_id). Affected artifacts are identified by querying the library's indexes (source registry, placed excerpts). No LLM calls. The cascade rules are a configuration file at `library/feedback/cascade_rules.json` — adding new rules requires no code changes.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: correction recording (§4.A.1), library indexes (source registry, placed excerpts at taxonomy leaves), scholar interface for cascade presentation.

#### §4.B.2 — Cross-Engine Root Cause Analysis

**Capability:** When corrections at a downstream engine (e.g., excerpting, taxonomy) trace back to errors introduced at an upstream engine (e.g., normalization, passaging), the feedback component detects this cross-boundary pattern and routes the correction signal to the responsible upstream engine rather than letting the downstream engine repeatedly compensate.

**Why this is transformative.** In a multi-engine pipeline, the error source and the error manifestation are often in different engines. A normalization engine that systematically confuses layer boundaries (matn vs. sharh) causes the excerpting engine to misattribute text — but the corrections arrive at the excerpting engine's gate, not the normalization engine's. Without cross-engine root cause analysis, the excerpting engine receives a stream of corrections and tries to optimize its prompts to work around the normalization error — a fundamentally wrong approach. The correct response is to fix the normalization engine's layer detection.

**Root cause detection.** The component analyzes correction records for cross-engine patterns:

1. **Provenance-based analysis.** Each correction record links to an artifact, which has a provenance chain (excerpt → passage → normalized page → source). When corrections cluster on excerpts from passages that share a common normalization characteristic (same source format, same layer detection strategy, same OCR quality tier), the component identifies the upstream normalization step as a potential root cause. Trigger: ≥5 corrections on excerpts whose provenance shares a common upstream characteristic, within 60 days.

2. **Error type correlation.** Certain downstream correction types correlate with upstream causes. The component maintains a correlation table:
   - `attribution_error` at excerpting + source has multi-layer text → likely normalization layer detection issue.
   - `school_misattribution` at excerpting + source is a multi-author work → likely normalization layer attribution issue.
   - `placement_error` at taxonomy + excerpt has low self-containment → likely excerpting boundary issue, which may trace to passaging boundary issue.
   - `missing_content` at synthesis + leaf has few excerpts → likely taxonomy coverage gap, not synthesis error.

3. **Correction propagation tracking.** When a correction is applied at one engine and the owner then corrects the same artifact at a different engine, the component detects this "re-correction" pattern. Two corrections on the same artifact from different engines within 30 days suggests the first correction addressed a symptom, not the root cause.

**Root cause report format.** A root cause detection produces a report stored alongside pattern reports:
- `root_cause_id` (string): Unique identifier.
- `downstream_engine` (string): Where the corrections manifest.
- `upstream_engine` (string): Where the root cause likely is.
- `evidence` (list): The corrections and provenance analysis supporting this conclusion.
- `correlation_type` (string): Which correlation pattern was detected.
- `suggested_action` (string): What should be investigated upstream.

The report is surfaced to the owner through the scholar interface and recorded as a pattern with `suggested_action: "architecture_review"` — because cross-engine root causes often require pipeline-level changes, not just prompt optimization.

**Technical approach.** Provenance-based analysis uses the library's artifact provenance chains (already stored as metadata on excerpts and entries). Error type correlation uses a static lookup table maintained in the component's configuration. No LLM calls. Correction propagation tracking uses timestamp comparison on corrections sharing an artifact_id. This is computationally lightweight — the most expensive operation is reading provenance chains from the library, which are small JSON files.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: correction recording (§4.A.1), artifact provenance chains (stored by excerpting and synthesis engines), correction indexes (§4.A.2).

#### §4.B.3 — Learning Velocity Tracking

**Capability:** The feedback component monitors how quickly each engine improves on each correction type over time, identifying stagnant patterns where prompt optimization has reached its ceiling and a different approach (architectural change, new model, additional training data, or rule redesign) is needed.

**Why this is transformative.** DSPy optimization is powerful but not omnipotent. Some error types respond well to prompt improvement (better few-shot examples, clearer instructions). Others persist because the error is structural — the engine's task decomposition is wrong, or the model lacks the capability, or the data doesn't contain enough signal. Knowing WHEN to stop optimizing prompts and start redesigning is critical to efficient development. Without velocity tracking, the owner and architect waste optimization cycles on problems that need architectural solutions.

**Velocity metrics.** For each (engine_id, correction_type) pair, the component tracks:

- `correction_rate`: Rolling 30-day count of corrections.
- `rate_history`: Monthly correction rates for the last 12 months.
- `optimization_events`: List of DSPy optimization runs targeting this correction type, with dates.
- `post_optimization_rate`: Correction rate in the 30 days following each optimization event.
- `improvement_ratio`: For each optimization event, the ratio of pre-optimization rate to post-optimization rate. A ratio > 1.0 means the optimization helped; < 1.0 means it made things worse; ≈ 1.0 means no effect.

**Stagnation detection.** An engine's handling of a correction type is flagged as `stagnant` when ALL of the following are true:
1. At least 2 DSPy optimization runs have targeted this correction type.
2. The most recent optimization event has an improvement_ratio ≤ 1.1 (less than 10% improvement).
3. The correction rate remains above a minimum threshold (default: 2 corrections per 30 days).

A stagnation flag produces a pattern report with `severity: "significant"` and `suggested_action: "architecture_review"`, signaling to the architect that prompt optimization is not solving this problem.

**Improvement tracking.** Conversely, the component also detects when an engine is rapidly improving: correction rate decreasing by ≥50% over 3 consecutive months. This produces an `info`-level notification that can be surfaced to the owner as encouragement — "KR is getting significantly better at school attribution in Nahw."

**Technical approach.** Velocity tracking uses time-series analysis of correction counts. All metrics are computed from the correction index and the optimization event log. No LLM calls. The analysis runs on-demand when the component generates its statistics report, and incrementally when new corrections arrive.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: correction recording (§4.A.1), correction indexes (§4.A.2), DSPy optimization event logging by engines.

---

## 5. Validation and Quality

**Layer 1: Self-validation.** The feedback component validates its own outputs:
- Every correction record written to disk is immediately read back and verified against the correction schema. Mismatches trigger a retry; persistent failure produces `FEEDBACK_WRITE_FAILED`.
- Index consistency: after each index update, the component verifies that the index entry count matches the correction file count for the affected dimension. Mismatches trigger a full index rebuild.
- Training data validation: each generated training example is validated against the registered engine's task signature schema. Examples that fail schema validation are excluded with a warning log and `training_status: "excluded"`.
- Pattern threshold validation: when a pattern is detected, the component re-counts the evidence from the raw correction records (not from the index) to verify the threshold was genuinely crossed. This catches index corruption that might produce false pattern detections.

**Layer 2: Algorithmic validation.** The validation component (shared/validation) can verify:
- Correction schema conformance: every correction record matches the Correction schema from §3.
- Referential integrity: every `checkpoint_id` in a correction record references an actual checkpoint in the human gate archive. Every `target_id` references an artifact that exists (or existed) in the library.
- Temporal integrity: correction timestamps are monotonically increasing within each correction file. Regression test results reference existing baseline sets.
- Training data consistency: the count of corrections with `training_status: "included"` for an engine matches the count of examples in that engine's training data file.

**What prevents errors from reaching the library.** The feedback component does not directly modify the library — it produces correction data, patterns, and regression results that engines consume. Its contribution to library integrity is indirect but critical: by providing high-quality training data, accurate pattern analysis, and reliable regression testing, it ensures that engine improvements are real improvements. The regression test gate (§4.A.5) is the feedback component's strongest contribution to error prevention: it blocks engine updates that would degrade quality on known-correct outputs.

**Scholarly integrity safeguard.** The feedback component's correction cascade intelligence (§4.B.1) is a direct scholarly integrity mechanism: it ensures that a single correction's implications are propagated to all potentially affected artifacts, preventing errors from persisting in corners of the library that the owner hasn't revisited.

---

## 6. Consensus Integration

The feedback component does NOT use multi-model consensus. This is a deliberate decision.

**Rationale.** The feedback component performs four types of operations: (1) correction recording, which is a data persistence operation requiring no intelligence, (2) pattern analysis, which is statistical counting requiring no LLM judgment, (3) training data formatting, which is schema transformation requiring no content understanding, and (4) regression test coordination, which is orchestration requiring no content evaluation. None of these benefit from multiple LLM opinions. The intelligence in the feedback loop lives in the engines that consume the feedback component's outputs — their DSPy optimizers use LLM calls to generate improved prompts, and their regression tests use LLM calls to evaluate output quality. The feedback component is the plumbing that connects corrections to improvements; it is not the intelligence that makes the improvements.

---

## 7. Error Handling

| Error Code | Severity | Condition | Recovery |
|---|---|---|---|
| `FEEDBACK_INVALID_INPUT` | Warning | Correction submission fails validation | Return error with specific validation failures. Correction not recorded. |
| `FEEDBACK_WRITE_FAILED` | Fatal | Correction could not be written to disk after retry | Return error. Log the full correction record to stderr so it is not lost. |
| `FEEDBACK_CHECKPOINT_NOT_FOUND` | Warning | Referenced checkpoint_id does not exist in the human gate archive | Record correction without checkpoint context. Flag as `incomplete_provenance`. |
| `FEEDBACK_ARTIFACT_NOT_FOUND` | Warning | Target artifact does not exist in the library | Record correction anyway (the artifact may have been deleted/reprocessed since the correction was submitted). Flag as `orphaned_target`. |
| `FEEDBACK_INDEX_CORRUPTED` | Warning | Index count mismatch detected during update | Trigger full index rebuild from correction files. Log the corruption. Processing continues after rebuild. |
| `FEEDBACK_ENGINE_NOT_REGISTERED` | Info | Correction received for an engine without a registered task signature | Record the correction for pattern analysis. Training data generation is skipped — the correction is stored as `training_status: "unprocessed"` until the engine registers. |
| `FEEDBACK_REGRESSION_TIMEOUT` | Warning | Regression test did not complete within the configured timeout | Record result as `timeout`. The update is blocked (same as `fail`). The owner is notified. |
| `FEEDBACK_BASELINE_MISSING` | Warning | Engine requested regression test but has no registered gold baselines | Regression test skipped with warning. The update is permitted but flagged as `unvalidated`. |
| `FEEDBACK_TRAINING_SCHEMA_MISMATCH` | Warning | Correction data does not match the engine's registered task signature schema | Correction recorded for pattern analysis. Training example excluded. Warning logged with the specific schema mismatch. |
| `FEEDBACK_CASCADE_SCOPE_EXCEEDED` | Info | A cascade rule would affect more than the configured maximum artifacts (default: 200) | Cascade signal created but truncated to the maximum. The cascade signal notes that additional artifacts exist beyond the truncation limit. |
| `FEEDBACK_DUPLICATE_CORRECTION` | Info | A correction for the same (target_id, correction_type) exists within the last 24 hours | Record the correction anyway (it may be a different error on the same artifact). Flag as `possible_duplicate` for manual review. |

**What gets logged.** Every correction recording (success or failure), every pattern detection, every regression test trigger and result, every cascade signal generated, every training data export update, and every error. The log is append-only and stored at `library/logs/feedback.jsonl`.

**What triggers alerts.** Write failures (potential disk issue), index corruption (potential data integrity issue), regression test failures (blocked updates), stagnation detections (architectural attention needed), and a sudden spike in correction rate (potential systematic upstream issue — more than 3× the 30-day average in a single week).

**What blocks the pipeline.** The feedback component does not directly block the processing pipeline. It blocks ENGINE UPDATES: model changes and prompt updates that fail regression testing cannot be applied (cooperative enforcement, §4.A.5). The processing pipeline itself continues using the existing (pre-update) configuration.

---

## 8. Configuration

| Parameter | Default | Range | Purpose |
|---|---|---|---|
| `scan_interval_minutes` | 60 | 5–1440 | How often to scan the human gate archive for new corrections |
| `pattern_window_count` | 50 | 20–200 | Number of recent corrections per engine to analyze for patterns |
| `pattern_window_days` | 90 | 30–365 | Maximum age of corrections included in pattern analysis |
| `type_concentration_threshold` | 0.40 | 0.20–0.80 | Proportion of one correction_type to trigger type_concentration pattern |
| `science_concentration_threshold` | 0.50 | 0.20–0.80 | Proportion of one science to trigger science_concentration pattern |
| `source_concentration_threshold` | 0.30 | 0.10–0.60 | Proportion of one source to trigger source_concentration pattern |
| `model_concentration_threshold` | 0.60 | 0.30–0.90 | Proportion of one model to trigger model_concentration pattern |
| `confidence_miscalibration_threshold` | 0.30 | 0.10–0.50 | Proportion of high-confidence errors to trigger miscalibration pattern |
| `recurring_pair_count` | 3 | 2–10 | Minimum occurrences of the same error pattern to trigger recurring_pair |
| `recurring_pair_window_days` | 60 | 30–180 | Time window for recurring_pair detection |
| `cascade_max_artifacts` | 200 | 50–1000 | Maximum artifacts in a single cascade signal |
| `regression_timeout_minutes` | 30 | 5–120 | Maximum time for a regression test run to complete |
| `periodic_regression_interval_days` | 7 | 1–30 | Interval for periodic silent-drift regression tests |
| `stagnation_min_optimizations` | 2 | 1–5 | Minimum optimization runs before stagnation detection activates |
| `stagnation_improvement_threshold` | 1.10 | 1.00–1.50 | Minimum improvement_ratio to NOT be flagged as stagnant |
| `stagnation_min_correction_rate` | 2 | 1–10 | Minimum corrections per 30 days for stagnation to be meaningful |
| `stats_cache_minutes` | 60 | 5–1440 | How long cached statistics remain valid |

**Per-science configuration.** Pattern analysis thresholds can be overridden per science. This is stored in `library/feedback/config/science_overrides.json`. For example, a new science with few sources may need a lower `source_concentration_threshold` because most corrections will naturally cluster around the few available sources — that's not a pattern, it's an artifact of small sample size.

**What is configurable vs. hardcoded.** Pattern thresholds, scan intervals, and cascade limits are configurable because optimal values depend on library size, processing volume, and correction frequency — unknowable at design time. The pattern taxonomy (§4.A.3) is hardcoded because adding a new pattern type requires defining its trigger logic, not just changing a threshold. The cascade rules (§4.B.1) are configurable (JSON file) because new cascade types may emerge as the library grows. The correction schema (§3) is hardcoded — changing it requires a migration, not a configuration change.

---

## 9. Current Implementation State

**Existing code:** None specific to the feedback component. The ABD-era code in `shared/human_gate/src/human_gate.py` contains correction persistence (~200 lines), correction replay (~250 lines), and pattern detection (~200 lines) that were originally part of a monolithic human_gate module. In KR's architecture, these responsibilities are split: the human gate SPEC (already complete) manages checkpoint lifecycle, and the feedback component manages correction storage, pattern analysis, training data, and regression coordination. The ABD-era pattern detection code (lines 400-600 of human_gate.py) uses a simple `Counter`-based approach for frequency counting per correction type, per taxonomy node, per model, and per science — this validates the statistical approach specified in §4.A.3, though KR's implementation will be more sophisticated (sliding windows, threshold-based pattern detection, cascade intelligence).

**Existing tests:** None for the feedback component.

**Known gaps between current code and this SPEC:**
- [NOT YET IMPLEMENTED] Correction recording (§4.A.1) — no code exists.
- [NOT YET IMPLEMENTED] Correction indexing (§4.A.2) — no code exists.
- [NOT YET IMPLEMENTED] Pattern analysis (§4.A.3) — ABD code has basic frequency counting; KR needs sliding windows, multi-dimensional analysis, and pattern lifecycle management.
- [NOT YET IMPLEMENTED] Training data management (§4.A.4) — no code exists. Depends on DSPy integration in calling engines.
- [NOT YET IMPLEMENTED] Regression test coordination (§4.A.5) — no code exists. Depends on gold baseline creation by each engine.
- [NOT YET IMPLEMENTED] Model change monitoring (§4.A.6) — no code exists.
- [NOT YET IMPLEMENTED] Correction cascade intelligence (§4.B.1) — no code exists.
- [NOT YET IMPLEMENTED] Cross-engine root cause analysis (§4.B.2) — no code exists.
- [NOT YET IMPLEMENTED] Learning velocity tracking (§4.B.3) — no code exists.

**External dependencies:**
- **Python standard library:** `json`, `os`, `datetime`, `hashlib`, `collections` — for file operations, correction ID generation, and basic counting.
- **Pydantic v2** (already a project dependency): for correction, pattern, and regression result model definitions.
- **DSPy** (MIT license, already cataloged in RESOURCES.md): for understanding task signature schemas and producing DSPy-compatible training examples. The feedback component does NOT call DSPy optimization functions — it only uses DSPy's `Example` format for training data export. DSPy's MIPROv2 and SIMBA optimizers are used by individual engines, not by the feedback component.
- **shared/human_gate:** for reading resolved checkpoint records (read-only access to the archive).
- **shared/validation:** for schema validation and referential integrity checks.

No new external dependencies beyond what is already in the project. The feedback component is deliberately lightweight — it manages data and runs statistical analysis. The heavy lifting (DSPy optimization, regression test execution) happens in the calling engines.

---

## 10. Test Requirements

**Correction recording tests.** Must cover: recording from human gate checkpoint (modified and rejected), recording from direct owner correction, deduplication handling (two corrections on the same artifact), immutability (correction records never modified), supersession (new correction supersedes old), validation rejection (malformed input produces FEEDBACK_INVALID_INPUT), checkpoint not found (FEEDBACK_CHECKPOINT_NOT_FOUND recorded with incomplete_provenance).

**Correction indexing tests.** Must cover: index creation from empty state, incremental index update, index rebuild after corruption, multi-dimensional query (corrections for engine X in science Y of type Z), aggregate statistics accuracy.

**Pattern analysis tests.** Must cover: each pattern type triggers at its threshold (type_concentration, science_concentration, source_concentration, model_concentration, confidence_miscalibration, recurring_pair), patterns do NOT trigger below threshold (off-by-one correctness), existing patterns are updated (not duplicated) when new evidence arrives, pattern severity assignment (critical vs. significant vs. minor), pattern staleness after 90 days without new evidence.

**Training data management tests.** Must cover: engine registration, training example generation from correction, quality filters (rejections excluded, superseded excluded), schema validation against registered task signatures, training data versioning, training example for unregistered engine stored as unprocessed.

**Regression test coordination tests.** Must cover: model change triggers regression, prompt update triggers regression, regression pass permits update, regression fail blocks update, regression timeout blocks update, missing baselines produce warning and permit update with flag, periodic regression scheduling.

**Cascade intelligence tests (§4.B.1).** Must cover: each cascade rule fires on the appropriate correction type, cascade scope is correctly computed (affected artifacts), cascade truncation at max_artifacts, cascade dismissal tracking, cascade does NOT fire for corrections that don't match any rule.

**Integration tests.** Must verify: the feedback component can read resolved checkpoints from the human gate archive, correction records reference artifacts that exist in the library, training data exports are valid DSPy Example format, pattern reports are correctly consumed by the scholar interface (mock), regression test requests are correctly received by engines (mock).

**Gold baseline for the feedback component itself.** A set of 30+ correction records covering all correction types, all engines, and both input paths (human gate + direct). Pattern analysis gold baselines: known correction sets that should and should not trigger each pattern type. Regression coordination gold baselines: known test scenarios with expected pass/fail verdicts.

**Regression testing strategy.** After any change to pattern analysis logic: re-run pattern detection on gold baseline correction sets and verify expected patterns are detected. After any change to training data generation: re-run generation on gold baseline corrections and verify output matches expected DSPy examples. After any change to cascade rules: re-run cascade detection on gold baseline corrections and verify expected cascades are generated.
