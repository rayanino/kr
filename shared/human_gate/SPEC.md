# Human Gate — بوابة الإنسان — Specification

## 1. Purpose and Scope

The human gate component is the shared infrastructure that manages checkpoints where the owner must approve, reject, or modify the application's proposed actions before they take effect. It is Layer 3 of the quality architecture (VISION.md §8.1) — the judgment layer that provides human oversight over irreversible or high-impact decisions that no automated mechanism can replace.

**What this component does.** It provides four capabilities: (1) checkpoint lifecycle management — creating, querying, resolving, and expiring checkpoints that engines submit when they need owner decisions, (2) pre-approval policy management — maintaining standing policies that allow specific categories of decisions to proceed without pausing, (3) bidirectional validation — verifying the owner's decisions against the library's existing knowledge to catch human errors before they take effect, and (4) owner confidence calibration — adjusting gate behavior per science based on the owner's declared expertise level, so that automated layers compensate when the owner's review is less effective.

**What this component does NOT do.** It does not present checkpoints to the owner — presentation, notification, and interaction are the scholar interface's responsibility (D-016). The human gate manages the queue; the scholar interface renders it. It does not analyze correction patterns or store corrections for feedback loop purposes — that is the feedback component's responsibility (VISION.md §8.3). When the owner modifies a proposed action at a gate, this component records the resolution and hands it back to the calling engine; the feedback component separately records and analyzes the correction for systemic pattern detection. It does not define what makes a good excerpt, a correct placement, or a valid taxonomy evolution — each engine defines its own review criteria and provides them as structured payloads when creating checkpoints. It does not make content decisions — it facilitates the owner's decisions and validates them structurally.

**Phase classification.** The human gate component is phase-agnostic infrastructure. It serves engines from all pipeline stages: the source engine (Phase 1) creates checkpoints for author disambiguation and trust evaluation; normalization creates checkpoints for low-fidelity sources; the taxonomy engine (Phase 2) creates checkpoints for placement review and evolution proposals. The component has no awareness of what the checkpoint's content means — it manages the lifecycle.

**User scenarios served.** The human gate is experienced directly by the owner in every scenario that involves review: Scenario 1 (first launch — reviewing initial source metadata), Scenario 2 (active study — approving newly discovered sources), Scenario 6 (new book briefing — confirming source identity when OCR is uncertain), Scenario 7 (science map — approving taxonomy evolution proposals), and Scenario 8 (error correction — the human gate is where the owner catches and corrects errors). The component serves USER_SCENARIOS.md by ensuring that no incorrect decision enters the library unchallenged, while avoiding unnecessary interruptions that would slow the owner's study workflow.

---

## 2. Input Contract

The human gate component is a library, not a service. Engines import checkpoint management functions and call them directly. There is no single input type — each operation has its own input signature.

**Checkpoint creation input.** A checkpoint creation call receives: the `gate_type` (a string identifying the category of decision — see §4.A.1 for the registry of gate types), the `engine_id` (which engine created this checkpoint), the `artifact_id` (the identifier of the artifact being gated — a source_id, excerpt_id, tree version, etc.), a `payload` (a structured dict containing all information the owner needs to make the decision — the specific fields depend on the gate type and are defined by the creating engine's SPEC), an optional `priority` (one of `critical`, `high`, `normal`, `low` — default `normal`), an optional `science` (the science this checkpoint relates to, used for confidence calibration), and an optional `related_checkpoints` (list of checkpoint IDs that are related — e.g., multiple excerpts from the same passage that should be reviewed together).

**Checkpoint resolution input.** A checkpoint resolution call receives: the `checkpoint_id`, the `resolution` (one of `approved`, `rejected`, `modified`), an optional `modifications` dict (required when resolution is `modified` — contains the owner's changes in the same schema as the original payload), and an optional `reason` (free-text explanation of the owner's decision, primarily for the feedback component's pattern analysis).

**Pre-approval policy input.** A policy creation call receives: the `gate_type` this policy applies to, the `scope` (a dict specifying the policy's boundaries — which science, which source, which engine, which confidence range), the `conditions` (a dict specifying when auto-approval applies — e.g., `{"min_confidence": 0.85, "science": "nahw"}`), and the `policy_description` (human-readable explanation of what this policy does, for the owner's review).

**Owner confidence declaration input.** A confidence update call receives: the `science` identifier and the `confidence_level` (one of `expert`, `intermediate`, `beginner`, `none`). See §4.A.4 for how confidence levels affect gate behavior.

**Checkpoint query input.** A query call receives: optional filters including `gate_type`, `engine_id`, `science`, `state` (pending/resolved/expired), `priority`, `created_after`, `created_before`, and `artifact_id`. Returns matching checkpoints sorted by priority (critical first) then by creation time (oldest first within same priority).

**Validation on input.** Every function validates its own inputs. A checkpoint creation call with an unregistered gate_type is rejected with error `GATE_UNKNOWN_TYPE`. A resolution call for a checkpoint that is not in `pending` state is rejected with `GATE_NOT_PENDING`. A policy creation call with conditions that reference a non-existent science is rejected with `GATE_INVALID_SCOPE`. Missing required fields produce `GATE_MISSING_FIELD`. The component never crashes on bad input — it returns structured error results.

---

## 3. Output Contract

Every checkpoint management function returns a `GateResult` object. This is the component's universal output format.

**GateResult fields:**

- `success` (boolean): Whether the operation completed successfully.
- `checkpoint_id` (string, optional): The checkpoint's unique identifier. Present on creation and resolution.
- `checkpoint` (Checkpoint object, optional): The full checkpoint record. Present on creation, resolution, and individual query.
- `checkpoints` (list of Checkpoint objects, optional): Present on batch query.
- `error` (GateError object, optional): Present when `success` is false. Contains `error_code` (string), `message` (string), and `details` (dict, optional).
- `validation_warnings` (list of ValidationWarning, optional): Present on resolution when bidirectional validation detected potential issues with the owner's decision. Each warning contains `warning_type`, `message`, and `severity` (one of `info`, `caution`, `conflict`). Warnings do not block resolution — they inform the scholar interface, which presents them to the owner for consideration.

**Checkpoint record fields:**

- `checkpoint_id` (string): Unique identifier, format `gate_{8_char_hash}_{timestamp}` where the hash is derived from gate_type + artifact_id + creation timestamp.
- `gate_type` (string): The registered gate type identifier.
- `engine_id` (string): Which engine created this checkpoint.
- `artifact_id` (string): The identifier of the gated artifact.
- `science` (string, optional): The science this checkpoint relates to.
- `priority` (string): One of `critical`, `high`, `normal`, `low`.
- `state` (string): One of `pending`, `approved`, `rejected`, `modified`, `expired`.
- `payload` (dict): The structured information for the owner's review.
- `created_at` (string, ISO 8601): When the checkpoint was created.
- `resolved_at` (string, ISO 8601, optional): When the checkpoint was resolved.
- `resolved_by` (string, optional): Always `owner` in v1 (only one user). Reserved for future multi-user.
- `resolution` (string, optional): One of `approved`, `rejected`, `modified`. Present after resolution.
- `modifications` (dict, optional): The owner's changes. Present when resolution is `modified`.
- `reason` (string, optional): The owner's explanation.
- `validation_warnings` (list, optional): Bidirectional validation results from resolution.
- `auto_approved` (boolean): Whether this checkpoint was auto-approved by a pre-approval policy (true) or reviewed by the owner (false).
- `policy_id` (string, optional): The pre-approval policy that auto-approved this checkpoint. Present only when `auto_approved` is true.
- `related_checkpoints` (list of strings, optional): IDs of related checkpoints.
- `confidence_context` (dict, optional): The owner's confidence level for this science at the time the checkpoint was created. Preserved for audit purposes — if the owner later changes their confidence level, the checkpoint records what it was at creation time.

**Metadata pass-through (D-023).** The human gate component does not consume or produce pipeline artifacts directly. It manages checkpoint records that engines create and resolve. The checkpoint's `payload` field is opaque to the human gate — it passes through whatever the engine puts in. This means all metadata the engine includes in the payload is preserved without loss. When a checkpoint is resolved with modifications, the `modifications` dict contains only the fields the owner changed — the engine must merge modifications with the original payload to produce the updated artifact.

**Guarantees.** Every checkpoint creation produces a persistent record that survives process restarts. Every resolution is atomic — a checkpoint transitions from `pending` to its resolved state in a single write, with no intermediate state visible to concurrent readers. Checkpoint records are append-only for audit purposes: resolved checkpoints are never deleted, only queried. The complete history of all gate decisions is available for the feedback component's pattern analysis and for provenance tracing.

---

## 4. Processing Specification

### §4.A — Core Processing

#### §4.A.1 — Gate Type Registry

Every checkpoint must declare a registered gate type. The gate type determines: what the checkpoint's payload schema is, what bidirectional validation rules apply on resolution, and what pre-approval policies are eligible. The gate type registry is a configuration file at `library/gates/gate_types.json` that maps gate type identifiers to their specifications.

The initial gate types, derived from all engine SPECs that reference human gates:

**Source engine gates:**
- `source_author_disambiguation`: Author identification is ambiguous. Payload: candidate scholar records, confidence scores, context clues. Resolution: owner selects the correct scholar or confirms a new record.
- `source_work_match`: Work matching confidence is in the 0.50–0.85 range. Payload: the new source metadata, the candidate work match, match confidence, distinguishing features. Resolution: owner confirms match, rejects match (new work created), or provides corrections.
- `source_trust_evaluation`: Source trustworthiness could not be determined automatically. Payload: source metadata, trust factors, fidelity assessment, recommended trust tier. Resolution: owner sets trust tier (verified/flagged) with optional reason.
- `source_low_confidence`: Critical metadata field confidence < 0.50. Payload: the metadata record with confidence scores per field, the fields that triggered the gate. Resolution: owner provides or confirms field values.
- `source_ocr_quality`: OCR confidence < 0.70 on critical fields for photographic sources. Payload: OCR output, confidence scores, original image reference. Resolution: owner provides manual transcription or confirms OCR output.
- `source_consensus_disagreement`: Multi-model consensus disagreement on author identification or work matching. Payload: both models' outputs with reasoning. Resolution: owner selects the correct answer.

**Normalization engine gates:**
- `norm_low_fidelity`: Proportion of low-fidelity pages exceeds the configured threshold. Payload: quality report, sample low-fidelity pages with issues, source metadata. Resolution: owner approves (proceed with flagged fidelity), rejects (source not worth processing), or provides guidance.
- `norm_layer_uncertainty`: Layer attribution could not be confidently determined for significant portions. Payload: uncertain regions with context, candidate attributions. Resolution: owner confirms attribution or corrects.
- `norm_format_disagreement`: Format classification or structural analysis produced uncertain results. Payload: classification candidates, evidence. Resolution: owner confirms format.

**Excerpting engine gates (surfaced during taxonomy placement):**
- `excerpt_review`: Draft excerpt requires review. Payload: the full excerpt with atoms, self-containment score, all metadata fields with confidence scores, review flags from atomization and excerpting. Resolution: owner approves, rejects, or modifies (boundary changes, metadata corrections, school attribution changes).

**Taxonomy engine gates:**
- `tax_placement_review`: Excerpt placement for review. Created for all placements unless a pre-approval policy covers them. Payload: the excerpt, the proposed leaf with score, top 3 alternative candidates with scores, existing excerpts at the proposed leaf (sample). Resolution: owner approves placement, selects different leaf, or marks as unplaceable.
- `tax_placement_ambiguous`: Placement confidence in 0.5–0.8 range, or tie condition. Always created regardless of pre-approval policies. Payload: same as placement_review but with emphasis on the ambiguity. Resolution: same as placement_review.
- `tax_evolution_proposal`: Taxonomy tree evolution proposed. Always human-gated, never pre-approvable. Payload: structural diff (current vs. proposed tree), affected excerpts with redistribution plan, trigger signal, invariant check results. Resolution: owner approves, rejects, or modifies the proposed structure.
- `tax_rollback`: Owner-requested rollback of a previous evolution. Payload: the evolution being rolled back, affected excerpts, entries that will be marked stale. Resolution: owner confirms rollback.
- `tax_verified_override`: Request to promote an individually flagged excerpt from flagged to verified status. Payload: the excerpt, the flag reason, evidence for/against verification. Resolution: owner approves promotion or maintains flagged status.

**Cross-engine gates:**
- `batch_processing`: A batch of sources or artifacts is proposed for processing. Payload: batch summary, source list, estimated processing scope. Resolution: owner approves batch, selects subset, or rejects.

**Meta-gates (managed by the human gate component itself):**
- `gate_policy_suggestion`: A pre-approval policy suggestion from the gate learning capability (§4.B.1). Payload: the suggested policy, evidence, explanation. Resolution: owner approves (policy created), rejects (suggestion dismissed).

The gate type registry is extensible: new engines or components can register new gate types by adding entries to the configuration file. The human gate component validates that every checkpoint's gate_type exists in the registry before accepting it. Unregistered gate types are rejected with `GATE_UNKNOWN_TYPE`.

#### §4.A.2 — Checkpoint Lifecycle

A checkpoint progresses through a defined lifecycle:

**Creation.** An engine calls the checkpoint creation function with the gate type, artifact ID, and payload. The human gate component: (1) validates the gate_type is registered, (2) checks pre-approval policies — if a matching policy exists and the checkpoint meets the policy's conditions, the checkpoint is immediately auto-approved (state set to `approved`, `auto_approved` set to true, `policy_id` recorded), (3) if no policy matches, applies confidence calibration adjustments (§4.A.4) and sets the checkpoint to `pending` state, (4) writes the checkpoint record to disk, (5) returns the GateResult with the checkpoint.

Auto-approval at creation time means the calling engine receives the approval immediately in the same call. The engine does not need to poll or wait — if the GateResult contains a checkpoint in `approved` state, the engine proceeds. If the checkpoint is `pending`, the engine must not proceed with the gated action until the checkpoint is resolved.

**Pending.** The checkpoint is in the review queue. The scholar interface queries pending checkpoints and presents them to the owner. The checkpoint remains pending until the owner resolves it or it expires.

**Resolution.** The owner (via the scholar interface) resolves the checkpoint by calling the resolution function. The human gate component: (1) validates the checkpoint is in `pending` state, (2) if the resolution is `modified`, validates that the modifications dict is non-empty, (3) runs bidirectional validation (§4.A.3) on the owner's decision, (4) records the resolution (state, modifications, reason, timestamp, validation warnings), (5) writes the updated checkpoint record to disk, (6) returns the GateResult with validation warnings if any.

The calling engine is responsible for checking whether its checkpoints have been resolved. The component provides a query function that engines call to check checkpoint state. There is no callback or event mechanism in v1 — engines poll their pending checkpoints. This is a deliberate simplicity choice: KR is a single-user application where processing runs in batches, not in real-time. Engines check their gates at the start of each processing run.

**Expiration.** Checkpoints can expire if the gated artifact becomes irrelevant. An engine can explicitly expire a checkpoint by calling the expiration function. There is no automatic time-based expiration — a checkpoint for an unresolved author disambiguation remains pending indefinitely until the owner addresses it. The only automatic state change is auto-approval via pre-approval policies, which happens at creation time, not later.

**Batch resolution.** The scholar interface may present multiple related checkpoints for batch resolution. The component supports resolving multiple checkpoints in a single call: each checkpoint in the batch receives the same resolution and modifications. This is common for excerpt review: the owner reviews 10 excerpts from the same passage and approves them all. Batch resolution calls the individual resolution function for each checkpoint — there is no transactional guarantee across the batch. If one resolution fails (e.g., a checkpoint was already resolved), the others still proceed, and the result indicates which succeeded and which failed.

#### §4.A.3 — Bidirectional Validation

VISION.md §9.2 (Reason 3) establishes that human gates are bidirectional: the owner verifies the application's proposals, and the application verifies the owner's decisions. When the owner resolves a checkpoint, the human gate component runs validation rules to catch potential human errors before they take effect.

Bidirectional validation does NOT block resolution. The owner's decision is always recorded and the checkpoint transitions to its resolved state. Validation produces warnings that are returned in the GateResult and stored in the checkpoint record. The scholar interface presents these warnings to the owner, who can choose to reconsider or proceed. This design respects the owner's authority (VISION.md §9.2 Reason 1) while providing the safety net of mutual verification (§9.2 Reason 3).

Validation rules are organized by gate type. Each gate type in the registry specifies zero or more validation rules that run on resolution. Validation rules fall into three categories:

**Structural validation.** Checks that the owner's modifications produce a structurally valid result. For `tax_placement_review`: the selected leaf must exist in the current active tree. For `source_trust_evaluation`: the trust tier must be one of the valid values. For `excerpt_review` with boundary modifications: the modified atom set must still satisfy the passage containment rule (D-011). Structural validation uses the validation component's checks (shared/validation) where applicable.

**Consistency validation.** Checks the owner's decision against existing library knowledge. For `tax_placement_review` where the owner selects a different leaf: the component queries the selected leaf's existing excerpts and checks whether the new excerpt's science, school, and topic are consistent with them. A placement of a Nahw excerpt at a Fiqh leaf produces a `conflict`-severity warning. For `source_author_disambiguation` where the owner selects a scholar: the component checks whether the selected scholar's known works and science scope are consistent with the source being processed.

**Cross-reference validation.** Checks the owner's decision against related checkpoints and recent decisions. For `excerpt_review` batch approvals: if the owner approves all excerpts from a passage but one excerpt contradicts another (e.g., attributes the same text to different schools), a `caution`-severity warning is generated. For `source_trust_evaluation`: if the owner marks a source as verified but related sources from the same repository have been flagged, a `caution`-severity warning is generated.

Validation rules are specified as named functions in the gate type registry. Each rule receives the original checkpoint payload, the owner's resolution and modifications, and read-only access to the library's registries (source registry, scholar authority, active tree). Rules must be deterministic and fast — no LLM calls, no network requests. If a rule needs information from the library, it reads from the local filesystem. Rules must not modify library state.

#### §4.A.4 — Owner Confidence Calibration

VISION.md §9.4 specifies that the owner's declared confidence level per science calibrates processing conservatism. The human gate component manages confidence declarations and applies them to checkpoint creation.

**Confidence levels.** Four levels, each with specific behavioral effects:

- `expert`: The owner has deep knowledge of this science. Gate behavior: standard thresholds apply. Pre-approval policies are fully effective. The owner's corrections carry high weight in feedback analysis.
- `intermediate`: The owner has working knowledge. Gate behavior: standard thresholds apply. Pre-approval policies are effective.
- `beginner`: The owner is new to this science. Gate behavior: confidence thresholds for auto-approval are raised by a configurable amount (default: +0.10). This means more decisions are escalated to the gate. Pre-approval policies still apply but with tightened conditions. Checkpoints include an additional `expertise_note` in the payload: a brief explanation from the creating engine of why this decision matters, to help the owner make an informed choice.
- `none`: The owner has no knowledge of this science. Gate behavior: all pre-approval policies for this science are suspended. Every gated decision requires explicit review. The `expertise_note` is mandatory in the payload — the engine must explain the decision in accessible terms. The scholar interface should present these checkpoints with additional context and guidance.

**Calibration data source (D-042).** The user model (shared/user_model) is the canonical owner of per-science expertise data. The human gate reads expertise levels from the user model's `expertise_levels` instead of maintaining a separate `confidence.json`. The mapping from user model's five-level scale to the human gate's behavioral rules: `researcher` or `advanced` → `expert` behavior, `intermediate` → `intermediate` behavior, `beginner` → `beginner` behavior, `none` → `none` behavior. The default expertise level for sciences not yet tracked by the user model is `beginner` — the component errs on the side of caution for sciences the owner hasn't explicitly assessed. The `library/gates/confidence.json` file is no longer maintained by this component.

**Calibration at checkpoint creation.** When an engine creates a checkpoint with a `science` field, the component looks up the owner's confidence level for that science and records it in the checkpoint's `confidence_context`. If the confidence level is `beginner` or `none`, the component adjusts the effective thresholds: a pre-approval policy with `min_confidence: 0.85` effectively becomes `min_confidence: 0.95` for `beginner` sciences and is suspended entirely for `none` sciences.

#### §4.A.5 — Pre-Approval Policy Management

Pre-approval policies are standing decisions that allow specific categories of checkpoints to be auto-approved at creation time, without the owner reviewing each one individually.

**Policy structure.** Each policy has:
- `policy_id` (string): Unique identifier, format `pol_{gate_type}_{sequence}`.
- `gate_type` (string): Which gate type this policy covers.
- `scope` (dict): Boundaries of the policy. Fields include: `science` (optional — if set, only applies to this science), `source_id` (optional — if set, only applies to checkpoints from this source), `engine_id` (optional — if set, only applies to checkpoints from this engine).
- `conditions` (dict): When auto-approval applies within the scope. Fields include: `min_confidence` (optional — the minimum confidence score in the payload for auto-approval; the specific payload field checked depends on the gate type and is declared in the gate type registry), `max_review_flags` (optional — maximum number of review flags on the artifact for auto-approval; default 0, meaning any review flag blocks auto-approval).
- `description` (string): Human-readable description.
- `created_at` (string, ISO 8601): When the policy was created.
- `active` (boolean): Whether the policy is currently active. The owner can deactivate without deleting.
- `auto_approve_count` (integer): Running count of checkpoints this policy has auto-approved. For transparency and for the owner to assess the policy's scope.

**Policy matching.** At checkpoint creation, the component evaluates all active policies whose `gate_type` matches the checkpoint's gate type. For a policy to match, ALL of its scope fields must match (or be absent, which means "any"), and ALL of its conditions must be satisfied. If multiple policies match, the most specific one (most scope fields set) takes precedence. If no policy matches, the checkpoint goes to `pending` state.

**Policy restrictions.** Some gate types are never eligible for pre-approval, regardless of policies:
- `tax_evolution_proposal`: Taxonomy evolution always requires explicit owner review. This is the highest-impact decision — an incorrect evolution misplaces excerpts across the entire tree.
- `tax_rollback`: Rollback always requires explicit confirmation.
- `source_trust_evaluation`: Trust determination always requires owner judgment. A wrong trust evaluation affects every excerpt from the source.
- `gate_policy_suggestion`: Policy suggestions must be explicitly reviewed.

These restrictions are hardcoded in the component, not configurable. If an engine attempts to create a policy for a restricted gate type, the creation fails with `GATE_POLICY_RESTRICTED`.

**Policy lifecycle.** Policies are created by the owner (via the scholar interface) or suggested by the gate learning capability (§4.B.1). The owner can activate, deactivate, or delete policies at any time. Deactivating a policy does not affect previously auto-approved checkpoints — their `auto_approved` and `policy_id` fields are historical records.

#### §4.A.6 — Checkpoint Storage

Checkpoints are stored as JSON files in the `library/gates/` directory structure:

```
library/gates/
├── gate_types.json           # Gate type registry
├── # confidence.json removed (D-042) — expertise data now in user model
├── policies/                 # Pre-approval policies
│   ├── pol_tax_placement_review_001.json
│   └── ...
├── pending/                  # Pending checkpoints (indexed for fast query)
│   ├── gate_a1b2c3d4_20260305T143022.json
│   └── ...
├── resolved/                 # Resolved checkpoints (append-only archive)
│   ├── 2026-03/              # Organized by month for manageability
│   │   ├── gate_a1b2c3d4_20260305T143022.json
│   │   └── ...
│   └── ...
└── stats.json                # Aggregate statistics (§4.B.2)
```

**Pending vs. resolved separation.** Pending checkpoints are in a flat directory for fast listing. When a checkpoint is resolved, it is moved from `pending/` to `resolved/{year-month}/`. This ensures that the pending directory stays small (the owner should keep up with the queue) while the resolved archive grows without affecting query performance on pending items.

**Atomicity.** Checkpoint writes use the write-to-temp-then-rename pattern: the component writes the JSON to a temporary file in the same directory, then atomically renames it to the final filename. This prevents partial writes from corrupting checkpoint records on crash or power loss.

**Concurrency.** KR is a single-user, single-process application. The human gate component does not implement locking. If future versions require concurrent access (e.g., background processing creating checkpoints while the owner reviews), file-level locking or a SQLite backend can be added. For v1, sequential access is sufficient and simpler.

#### §4.A.7 — Queue Health Monitoring

The component maintains aggregate statistics in `library/gates/stats.json`:
- Total pending checkpoints, broken down by gate type and priority.
- Average resolution time per gate type (time from creation to resolution).
- Auto-approval rate per gate type (proportion of checkpoints auto-approved by policy).
- Queue depth history (daily snapshots of pending count).

**Alert conditions.** The component checks alert conditions when new checkpoints are created:
- Pending queue exceeds the configured threshold (default 20 items): generates a `GATE_QUEUE_GROWING` warning in the creation result. The scholar interface should alert the owner that the review queue needs attention.
- A specific gate type has more than 10 pending items: generates a `GATE_TYPE_BACKLOG` warning. May indicate a systematic issue upstream (e.g., a source producing many low-confidence excerpts).
- A checkpoint has been pending for more than the configured stale threshold (default 7 days): the checkpoint is flagged as `stale` in query results. The scholar interface should highlight stale checkpoints.

### §4.B — Transformative Capabilities

#### §4.B.1 — Gate Learning and Policy Suggestion

**Capability:** The human gate component analyzes the owner's resolution patterns over time and suggests pre-approval policies for decision categories where the owner consistently approves without modification. This reduces the owner's review burden for routine decisions while maintaining oversight for genuinely uncertain ones.

**Trigger.** After every checkpoint resolution, the component updates its pattern statistics. When a gate type + scope combination reaches a configurable threshold of consecutive approvals without modification (default: 30), the component generates a policy suggestion.

**Pattern analysis.** The component tracks, per gate type and per science:
- Consecutive approval streak (reset to 0 on any rejection or modification).
- Confidence score distribution of approved checkpoints (what range is the owner consistently approving?).
- Modification rate (what proportion of resolutions involve modifications?).
- Resolution time (how quickly does the owner resolve these — fast resolutions suggest the decision is routine).

A policy suggestion is generated when ALL of the following conditions are met:
1. Consecutive approval streak ≥ the suggestion threshold (default 30).
2. The owner has not modified a checkpoint in this category in the last 50 resolutions.
3. The average confidence score of approved checkpoints is above a minimum (default 0.80).
4. The gate type is not in the restricted list (§4.A.5).

**Suggestion format.** A policy suggestion is stored as a special checkpoint of gate type `gate_policy_suggestion`. Its payload contains: the suggested policy (gate type, scope, conditions derived from the pattern analysis), the evidence (approval streak count, confidence distribution, modification rate), and a human-readable explanation. The owner reviews the suggestion at the gate — approving it creates the policy, rejecting it dismisses it and resets the streak counter.

**Technical approach.** Pattern analysis is purely statistical — no ML models, no LLM calls. It counts approvals, rejections, modifications, and confidence scores in the resolved checkpoint archive. The analysis runs incrementally: each new resolution updates running counters stored in `library/gates/stats.json`. This approach is sufficient because the patterns are simple (consecutive approvals at high confidence) and the owner population is one person. The lightweight implementation means no external dependencies beyond Python's standard library.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: resolved checkpoint archive (§4.A.6), stats tracking (§4.A.7).

#### §4.B.2 — Review Efficiency Intelligence

**Capability:** The human gate component produces metadata about the owner's review behavior that the scholar interface uses to optimize the review experience — presenting the right checkpoints at the right time in the right order.

**What it produces.** A review profile stored in `library/gates/stats.json` that includes:
- Per gate type: average resolution time, modification rate, rejection rate. This tells the scholar interface which gate types the owner finds routine (fast resolution, low modification rate) vs. which require careful thought (slow resolution, high modification rate).
- Per science: average resolution time, modification rate. This tells the scholar interface which sciences the owner reviews confidently vs. which require more context.
- Time-of-day patterns: when the owner most often resolves checkpoints (morning, evening, weekends). This enables the scholar interface to batch notifications appropriately.
- Review session patterns: how many checkpoints the owner typically resolves in a single session. This enables the scholar interface to present appropriate batch sizes.

**Update mechanism.** The review profile is updated after every checkpoint resolution. Updates are incremental: running averages, not full recomputation. The profile is read-only for the scholar interface — the human gate component is the sole writer.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: resolved checkpoint archive (§4.A.6).

#### §4.B.3 — Bidirectional Validation Depth: Library Consistency Checking

**Capability:** Beyond the basic bidirectional validation in §4.A.3, this capability performs deeper consistency checks that detect when the owner's decision, while structurally valid, would create semantic inconsistencies in the library. It turns the human gate into a collaborative partner that helps the owner make better decisions, not just a rubber stamp.

**Deep consistency checks.** These go beyond the §4.A.3 structural and consistency checks:

- **Placement coherence analysis.** When the owner modifies a placement (selects a different leaf), the component examines the target leaf's existing excerpt population. It computes a topic coherence signal by comparing the excerpt's metadata (topic keywords, school, content type) against the distribution of these fields across existing excerpts at the target leaf. A significant divergence (e.g., 95% of existing excerpts at the leaf are about المبتدأ but the new excerpt is about الفاعل) produces a `caution`-severity warning explaining the divergence. This is NOT a blocking check — the owner may intentionally place the excerpt at an unusual leaf — but it catches accidental misplacements.

- **Temporal consistency checking.** When the owner resolves a `source_author_disambiguation` or `source_trust_evaluation` gate, the component checks whether the resolution is temporally consistent. If the owner identifies an author as someone who died in 300 AH but the source references scholars from 700 AH, this is a temporal inconsistency that suggests a misidentification. The check uses death dates from the scholar authority registry.

- **Cross-gate consistency.** When the owner resolves a checkpoint, the component checks whether the resolution is consistent with the owner's decisions on related checkpoints. If the owner approved 9 excerpts from a passage and rejected 1, but the rejected excerpt is referenced by one of the approved excerpts (e.g., as context), the component warns that the approval may need reconsideration.

**Technical approach.** All deep consistency checks use existing library data (registries, placed excerpts, tree structure) and standard comparison algorithms (set intersection, distribution comparison, date range checks). No LLM calls. The checks must complete in under 500ms per resolution to avoid degrading the review experience. If a check takes longer (e.g., a large leaf with thousands of excerpts), it times out and is skipped with an `info`-severity note.

[NOT YET IMPLEMENTED] — Full specification provided; no code exists. Depends on: library registries (source registry, scholar authority), active taxonomy tree, placed excerpts.

---

## 5. Validation and Quality

**Layer 1: Self-validation.** The human gate component validates its own outputs:
- Every checkpoint written to disk is immediately read back and verified against the checkpoint schema. If the read-back fails, the write is retried once. If the retry fails, the error is logged and the creation call returns `GATE_WRITE_FAILED`.
- Every resolution updates the checkpoint's state atomically. After resolution, the component verifies that the checkpoint's state in the file matches the intended resolution. Mismatches are logged as `GATE_STATE_MISMATCH` — a potential corruption indicator.
- The pending directory is periodically scanned (at component initialization) to detect orphaned checkpoints — checkpoints whose gated artifacts no longer exist (e.g., a source was deleted). Orphaned checkpoints are flagged as `stale` but not automatically expired, because the artifact's absence might be the problem that needs investigation.

**Layer 2: Algorithmic validation.** The validation component (shared/validation) can verify:
- Checkpoint schema conformance: every checkpoint record matches the Checkpoint schema defined in §3.
- Referential integrity: every checkpoint's `artifact_id` references an artifact that exists in the library. Every `policy_id` references an active or deactivated (not deleted) policy. Every `science` field references a science that exists in the library's science inventory.
- Temporal integrity: `resolved_at` is always after `created_at`. Checkpoint files in `resolved/` have a non-pending state. Checkpoint files in `pending/` have state `pending`.

**Layer 3: Human gate integration.** The human gate component does not have its own human gate — it IS the human gate. However, one meta-gate exists: the `gate_policy_suggestion` type (§4.B.1), where the component's own policy suggestions are reviewed by the owner at the gate. This is the only case where the human gate creates checkpoints for itself.

**What prevents errors from reaching the library.** The human gate is the last line of defense before an engine's decision takes effect. Its contribution to error prevention is: (1) ensuring that high-impact decisions are reviewed by a human, (2) validating the human's decisions against existing library knowledge (bidirectional validation), and (3) maintaining a complete audit trail that enables post-hoc error detection by the feedback component. An error that passes through the human gate — the owner approves a wrong placement — is caught by the feedback component when the owner later notices the error (Scenario 8). The human gate's audit record enables the feedback component to trace the error to its source.

---

## 6. Consensus Integration

The human gate component does NOT use multi-model consensus. This is a deliberate decision.

**Rationale.** Consensus is valuable for decisions where multiple LLMs independently evaluate the same input and agreement increases confidence (source SPEC §6, excerpting SPEC §6, taxonomy SPEC §6). The human gate component makes no content decisions — it manages checkpoint lifecycle, applies policies, and runs validation rules. None of these operations benefit from multiple LLM opinions. The bidirectional validation rules (§4.A.3) are deterministic checks against library data, not LLM-driven assessments.

The engines that CREATE checkpoints may have used consensus as part of their decision process — e.g., the source engine uses consensus for author identification (source SPEC §6) and creates a checkpoint when consensus disagrees. This is the engine's domain, not the human gate's. The human gate receives the checkpoint and manages its lifecycle regardless of how the engine arrived at the decision to create it.

---

## 7. Error Handling

| Error Code | Severity | Condition | Recovery |
|---|---|---|---|
| `GATE_UNKNOWN_TYPE` | Fatal | Checkpoint creation with unregistered gate type | Return error. Calling engine must fix the gate type. |
| `GATE_NOT_PENDING` | Warning | Resolution attempted on non-pending checkpoint | Return error with current state. No state change. |
| `GATE_MISSING_FIELD` | Fatal | Required field missing from creation or resolution | Return error listing missing fields. |
| `GATE_WRITE_FAILED` | Fatal | Checkpoint could not be written to disk after retry | Return error. Calling engine must not proceed with the gated action. Log the failure for investigation. |
| `GATE_STATE_MISMATCH` | Fatal | Post-write verification detected state inconsistency | Log as potential corruption. Return error. The checkpoint's disk state is the source of truth — the in-memory state must be reloaded. |
| `GATE_POLICY_RESTRICTED` | Warning | Policy creation attempted for a restricted gate type | Return error explaining the restriction. |
| `GATE_INVALID_SCOPE` | Warning | Policy scope references non-existent science or artifact | Return error with the invalid reference. |
| `GATE_QUEUE_GROWING` | Info | Pending queue exceeds threshold | Warning in creation result. No action required from calling engine. |
| `GATE_TYPE_BACKLOG` | Info | Single gate type has >10 pending items | Warning in creation result. |
| `GATE_VALIDATION_ERROR` | Warning | Bidirectional validation rule failed to execute | Log the error. Validation warning is skipped — the resolution proceeds. Validation must never block resolution. |
| `GATE_ARTIFACT_MISSING` | Warning | Checkpoint's artifact_id references a nonexistent artifact | Flagged as stale during periodic scan. Not auto-expired. |
| `GATE_BATCH_PARTIAL` | Info | Batch resolution had partial success | Return result indicating which checkpoints succeeded and which failed, with per-checkpoint error codes. |

**What gets logged.** Every checkpoint creation, every resolution (including auto-approvals), every validation warning, every error, and every policy change. The log is append-only and stored at `library/logs/human_gate.jsonl`. Each log entry includes: timestamp, operation type, checkpoint_id (if applicable), result (success/failure), and any error or warning details.

**What triggers alerts.** Queue growing beyond threshold (§4.A.7), write failures (potential disk issue), state mismatches (potential corruption), and a sudden spike in checkpoint creation rate (potential upstream systematic issue).

**What blocks the pipeline.** A `GATE_WRITE_FAILED` error means the checkpoint could not be persisted. The calling engine must NOT proceed with the gated action because the checkpoint is the only record that this action was proposed. If the checkpoint is lost, the action could take effect without any record of review. This is worse than a visible failure that stops processing (D-033).

---

## 8. Configuration

| Parameter | Default | Range | Purpose |
|---|---|---|---|
| `queue_alert_threshold` | 20 | 5–100 | Pending checkpoints before queue growing alert |
| `stale_checkpoint_days` | 7 | 1–30 | Days before a pending checkpoint is flagged as stale |
| `default_confidence_level` | `beginner` | expert/intermediate/beginner/none | Confidence for undeclared sciences |
| `beginner_threshold_boost` | 0.10 | 0.05–0.20 | Added to confidence thresholds for beginner sciences |
| `policy_suggestion_threshold` | 30 | 10–100 | Consecutive approvals before suggesting a policy |
| `policy_suggestion_min_confidence` | 0.80 | 0.60–0.95 | Minimum average confidence for policy suggestion |
| `validation_timeout_ms` | 500 | 100–2000 | Maximum time for a single bidirectional validation check |
| `batch_resolution_max` | 50 | 10–200 | Maximum checkpoints in a single batch resolution |

**Per-science configuration (D-042).** Per-science expertise levels are stored and managed by the user model (shared/user_model). The human gate reads them on demand. These are user preferences managed through the scholar interface.

**What is configurable vs. hardcoded.** Alert thresholds, suggestion thresholds, and validation timeouts are configurable because optimal values depend on usage patterns that cannot be predicted at design time. The restricted gate types (§4.A.5) are hardcoded because they represent fundamental safety constraints — taxonomy evolution and trust evaluation must always be human-gated regardless of the owner's preferences.

---

## 9. Current Implementation State

**Existing code:** `shared/human_gate/src/human_gate.py` (881 lines). This is ABD-era code (D-019) with zero design authority in KR. The existing code provides four capabilities that may inform implementation but should not constrain design:

1. **Correction persistence** (~200 lines): Creates and stores correction records in JSONL format. KR equivalent: this is the feedback component's responsibility, not the human gate's. The correction record format is ABD-specific (book_id, passage_id fields).

2. **Correction replay** (~250 lines): Re-extracts passages with correction context injected into prompts. KR equivalent: this is DSPy prompt optimization in each engine, triggered by the feedback component. Not a human gate responsibility.

3. **Pattern detection** (~200 lines): Analyzes corrections for patterns using simple frequency counting. KR equivalent: this belongs in the feedback component. However, the approach (frequency counting per correction type, per book, per science) is a useful reference for §4.B.1.

4. **Gate checkpoints** (~230 lines): Manages review states (pending/approved/rejected/corrected) for excerpts. Uses a JSON file per extraction directory. KR equivalent: this is the closest to the human gate SPEC's checkpoint lifecycle, but it's excerpt-specific and lacks the generality needed for KR's multiple gate types, pre-approval policies, and bidirectional validation.

**Existing tests:** `shared/human_gate/tests/test_human_gate.py` (45 items collected). Tests cover ABD-era functionality. All tests need rewriting for KR's design.

**Known gaps between current code and this SPEC:**
- [NOT YET IMPLEMENTED] Gate type registry (§4.A.1) — ABD code has no concept of gate types.
- [NOT YET IMPLEMENTED] Pre-approval policies (§4.A.5) — ABD code has no policy mechanism.
- [NOT YET IMPLEMENTED] Bidirectional validation (§4.A.3) — ABD code has no validation on owner decisions.
- [NOT YET IMPLEMENTED] Owner confidence calibration (§4.A.4) — ABD code has no confidence concept.
- [NOT YET IMPLEMENTED] Gate learning and policy suggestion (§4.B.1) — no code exists.
- [NOT YET IMPLEMENTED] Review efficiency intelligence (§4.B.2) — no code exists.
- [NOT YET IMPLEMENTED] Library consistency checking (§4.B.3) — no code exists.
- [NOT YET IMPLEMENTED] Checkpoint storage with pending/resolved separation (§4.A.6) — ABD uses flat per-directory JSON.
- [NOT YET IMPLEMENTED] Queue health monitoring (§4.A.7) — no code exists.

**External dependencies:**
- Python standard library: `json`, `os`, `shutil`, `datetime`, `hashlib` — for file operations and checkpoint ID generation.
- Pydantic v2 (already a project dependency): for checkpoint, policy, and GateResult model definitions.
- shared/validation component: for schema validation and referential integrity checks used in self-validation (§5) and bidirectional validation (§4.A.3).

No new external dependencies are required. The human gate component is deliberately lightweight — it manages state and runs deterministic checks. The complexity lives in the engines that create checkpoints and the scholar interface that presents them.

---

## 10. Test Requirements

**Checkpoint lifecycle tests.** Must cover: creation with all gate types → pending state, resolution with approve/reject/modify → correct state transitions, attempted resolution of non-pending checkpoint → error, batch resolution with partial success, checkpoint write-and-read-back integrity, pending→resolved file movement.

**Pre-approval policy tests.** Must cover: policy creation with valid and invalid gate types (restricted types must fail), policy matching — single policy match, multiple policy match (most specific wins), no match → pending, policy deactivation stops matching, confidence calibration affects policy thresholds (beginner raises threshold, none suspends policies).

**Bidirectional validation tests.** Must cover: structural validation catches invalid modifications (non-existent tree leaf, invalid trust tier), consistency validation catches mismatches (Nahw excerpt at Fiqh leaf), validation warnings don't block resolution, validation timeout handling (slow check is skipped with info note).

**Owner confidence calibration tests.** Must cover: undeclared science gets default level, explicit declaration overrides default, beginner boost applied to policy threshold, none suspends all policies, confidence context recorded in checkpoint.

**Gate learning tests (§4.B.1).** Must cover: streak counting (resets on modification/rejection), suggestion threshold triggering, suggestion format, restricted types excluded from suggestions, suggestion approval creates policy, suggestion rejection resets streak.

**Integration tests.** Must verify: the source engine can create and query checkpoints, the taxonomy engine's placement workflow creates and resolves checkpoints, the validation component can validate checkpoint schema, sequential checkpoint creation and resolution (file operations don't interfere).

**Gold baseline.** A set of 20+ checkpoint records covering all gate types, with known-correct resolutions. Used to verify that the lifecycle, policy matching, and bidirectional validation produce expected results. The baseline is created during initial development and maintained as a regression test fixture.

**Regression testing.** After any code change, the full lifecycle test suite runs. After any policy logic change, the policy test suite runs. After any validation rule change, the bidirectional validation suite runs. Test failures block deployment.
