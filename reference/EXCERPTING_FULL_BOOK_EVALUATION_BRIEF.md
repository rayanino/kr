> Purpose: Define the evaluation layer for KR's upcoming 5-book excerpting campaign.
> Status: design-grade brief for bounded implementation.
> Scope: analyzer-first workflow, review-packet exporter, and formal test interpretation.
> Non-goals: prompt tuning, engine redesign, taxonomy/synthesis design.

# Excerpting Full-Book Evaluation Brief

## 1. Why this brief exists

The upcoming 5-book excerpting campaign should produce decision-grade evidence, not just a directory full of artifacts. The repo already emits rich intermediate and final outputs, but those outputs are not yet interpreted by a disciplined evaluation layer. Without that layer, a campaign can appear successful while silently hiding structural failures, dropped units, truncated model responses, metadata weaknesses, or review burdens that only become visible through manual browsing.

This brief adopts an analyzer-first workflow. The analyzer is the authoritative machine interpretation layer for a run. Human review happens through a review-packet exporter that consumes analyzer output, not through ad hoc folder inspection.

## 2. Evidence basis from the current repo

This brief is grounded in the current excerpting SPEC, the integration runners, and the most recent integration artifacts already committed in `integration_tests/run_20260328/`.

Three concrete findings from the current artifacts drive the design:

1. **Phase-accounting gaps are already real.** In `taysir`, Phase 2b produced 11 teaching units, but the final `excerpts.jsonl` contains only 9 excerpts. The run logged two `EX-V-002` errors. The evaluation layer must therefore reconcile grouped units against final excerpts and flag any unit loss instead of trusting final excerpt count alone.

2. **Silent failure is already possible.** In `ibn_aqil_v3`, the run shows a long Phase 2a duration and zero final excerpts, but `processing_log.jsonl` and `run_metadata.json` report zero errors. The evaluation layer must therefore detect impossible or suspicious run states even when the run's own error logs are clean.

3. **LLM call traces require structural interpretation.** In `ibn_aqil_v3/raw_llm_responses/enrich_0001.json`, the response is actually classification-shaped output and ends with `finish_reason = length`. The evaluation layer must therefore inspect call content and finish reasons, not rely on filename or client label alone.

These are not hypothetical edge cases. The analyzer must be explicitly designed to catch them.

## 3. Design principle: analyzer first, review second

The workflow is:

1. Run excerpting on one or more books.
2. Run the analyzer over the run directory.
3. Have the analyzer produce per-book and campaign summaries, metrics, lineage accounting, and anomaly flags.
4. Run the review-packet exporter on analyzer output.
5. Perform bounded human review only through the exported packets.
6. Interpret the campaign using the formal pass / concern / fail protocol in this brief.

This means:

- the analyzer, not manual browsing, is the first interpretive layer;
- the review packet is a derived artifact, not a parallel truth surface; and
- campaign judgment is based on explicit accounting, flags, and targeted review buckets.

## 4. Analyzer v1 contract

### 4.1 Inputs

The analyzer must accept either:

- a single book run directory produced by `scripts/run_integration_test.py`, or
- a campaign directory produced by `scripts/run_full_integration.py` containing multiple per-book run directories.

For each book, the analyzer must ingest these artifacts when present:

- `phase1_chunks.json`
- `phase2a_classifications/`
- `phase2b_groupings/`
- `excerpts.jsonl`
- `gate_queue.jsonl`
- `processing_log.jsonl`
- `timing.json`
- `run_metadata.json`
- `raw_llm_requests/`
- `raw_llm_responses/`

The analyzer must treat missing artifacts as evidence, not as absence of evidence.

### 4.2 Canonical internal entities

Analyzer output must be built around a normalized lineage/accounting model with at least these entities:

- **BookRun** — one source/package execution.
- **ChunkRecord** — one Phase 1 chunk with chunk_id, div_id, div_path, size metadata.
- **LLMCallRecord** — one raw request/response pair with inferred semantic phase, model, finish_reason, latency, token usage, cost, and parse status.
- **GroupedUnitRecord** — one Phase 2b teaching unit keyed by `(chunk_id, unit_index)`.
- **ExcerptRecordView** — one final excerpt keyed by `excerpt_id`, plus lineage fields `(div_id, chunk_index, unit_index)`.
- **GateRecord** — one human-gate entry when present.
- **RunIssue** — one detected anomaly or contradiction, with severity and evidence.

The critical rule is that grouped units and final excerpts must be reconcilable at unit level. The analyzer must not reduce everything to aggregated counts.

### 4.3 Per-book required metrics

#### A. Stage-accounting metrics

For every book, the analyzer must compute:

- phase1 chunk count
- phase2a-classified chunk count
- phase2b-grouped chunk count
- grouped teaching-unit count
- final excerpt count
- gate entry count
- grouped-to-final yield ratio
- excerpts per chunk
- grouped units per chunk
- dropped-unit count
- dropped-chunk count

The analyzer must also compute explicit phase transitions:

- Phase 1 -> Phase 2a coverage
- Phase 2a -> Phase 2b coverage
- Phase 2b -> final excerpt coverage
- final excerpt -> gate queue relationship

#### B. Structural integrity metrics

For every book, the analyzer must measure:

- missing expected artifact files
- chunk ids present upstream but missing downstream
- grouped units with no corresponding final excerpt
- final excerpts whose lineage does not resolve back to a grouped unit
- duplicate excerpt ids
- duplicate `(chunk_id, unit_index)` mappings
- gaps in unit indices within a chunk
- contradiction between artifact-derived counts and `processing_log.jsonl` / `run_metadata.json`
- number of LLM calls ending with `finish_reason = length`
- number of LLM calls that cannot be parsed into an expected semantic shape
- number of raw call files whose semantic content disagrees with their filename label

#### C. Quality-proxy metrics

The analyzer is not a substitute for human scholarly judgment, but it must surface measurable proxies that help interpret quality:

- self-containment distribution: FULL / PARTIAL / DEPENDENT
- PARTIAL-with-context_hint coverage
- DEPENDENT count and rate
- review_flag frequency by type
- gate_flag frequency by type
- consensus usage rate
- school attribution rate
- quoted_scholars rate
- evidence_refs density
- cross_reference density and unresolved rate
- structural_transition share
- editorial_note share
- ultra-short excerpt rate (for example <15 words and <30 words)
- short excerpt rate (<50 words)
- excerpt word-count distribution
- content-type distribution
- primary_function distribution

These metrics are for interpretation and triage, not automatic scholarly verdict by themselves.

#### D. Operational metrics

The analyzer must compute:

- total runtime per book
- phase1 / phase2a / phase2b / phase3 durations
- time per chunk for each phase when derivable
- per-model call count
- per-model prompt/completion/total tokens
- per-model cost
- total cost per book
- cost per final excerpt
- cost per grouped unit
- slowest calls by latency
- slowest chunks by phase duration

### 4.4 Required analyzer flags

Analyzer flags must be explicit, typed, and severity-scored. Minimum required flags:

#### Hard-failure flags

- `zero_excerpt_run_with_upstream_activity`
- `phase_accounting_break`
- `grouped_unit_loss`
- `unexplained_chunk_drop`
- `truncated_llm_response`
- `artifact_log_contradiction`
- `missing_gate_artifact`
- `unparseable_call_trace`

#### Concern flags

- `high_partial_rate`
- `dependent_units_present`
- `high_structural_transition_share`
- `high_editorial_note_share`
- `high_ultra_short_excerpt_rate`
- `high_consensus_load`
- `high_unresolved_cross_reference_rate`
- `cost_outlier`
- `latency_outlier`
- `semantic_phase_label_mismatch`

#### Informational flags

- `no_evidence_refs_detected`
- `no_school_attribution_detected`
- `no_quoted_scholars_detected`
- `positive_control_candidates_available`

### 4.5 Required per-book outputs

For each book, analyzer v1 must produce at least:

1. `analysis/book_summary.json`
   - machine-readable metrics, flags, and verdict inputs.

2. `analysis/book_summary.md`
   - compact narrative summary for a human reviewer.

3. `analysis/anomalies.json`
   - one record per detected anomaly with severity, evidence paths, and lineage identifiers.

4. `analysis/review_candidates.jsonl`
   - unit/excerpt level candidates for review-packet export.

The analyzer must also emit a single per-book headline status:

- `PASS`
- `CONCERN`
- `FAIL`

This status is provisional and machine-derived. It feeds the full-book testing protocol; it does not replace human review.

### 4.6 Required cross-book outputs

For a full campaign directory, the analyzer must produce:

1. `analysis/campaign_summary.json`
2. `analysis/campaign_summary.md`
3. `analysis/campaign_book_table.json`

The campaign summary must include:

- per-book status table
- cross-book metric table
- outlier rankings
- repeated anomaly patterns across books
- total campaign cost and timing
- campaign-level recommendation: proceed / fix-before-scale / block

The analyzer must answer these campaign questions directly:

- Which books are structurally healthy?
- Which books show silent or contradictory failure states?
- Are observed issues isolated or systematic?
- What should be reviewed first by a human?

## 5. Review-packet exporter v1 contract

### 5.1 Purpose

The review-packet exporter turns analyzer results into bounded human-review artifacts. It is not a second analyzer. It does not recompute metrics. It selects and formats cases for inspection.

### 5.2 Input

The exporter must consume analyzer output, not raw run directories directly.

Minimum inputs:

- `analysis/book_summary.json`
- `analysis/anomalies.json`
- `analysis/review_candidates.jsonl`
- raw artifact pointers required to reconstruct unit/excerpt text and local context

### 5.3 Required review buckets

Every exported packet must contain explicitly labeled sections for:

1. **Hard failures**
   - dropped grouped units
   - zero-output runs
   - truncated-call consequences
   - unresolved lineage/accounting breaks

2. **Self-containment risk**
   - all DEPENDENT units
   - highest-risk PARTIAL units
   - PARTIAL units missing or weak context hints

3. **Fragmentation / boundary-risk cases**
   - shortest excerpts
   - dense runs of very short consecutive excerpts
   - chunks with unusually high unit counts

4. **Structural/editorial noise**
   - structural_transition-heavy excerpts
   - editorial_note-heavy excerpts
   - front-matter dominated books or chunks

5. **Attribution / evidence-sensitive cases**
   - school-attributed excerpts
   - evidence-rich excerpts
   - excerpts with quoted scholars
   - excerpts carrying consensus metadata

6. **Positive controls**
   - strong FULL excerpts that appear structurally clean and pedagogically useful

The packet must never be only a failure scrapbook. Positive controls are required so the campaign can be judged on both yield and defects.

### 5.4 Required packet card structure

Each review card must include:

- book/package name
- div_id
- chunk_id when available
- unit_index and/or excerpt_id
- selection reason / anomaly bucket
- stage state (`grouped_only`, `final_excerpt`, `gated_excerpt`, etc.)
- primary text
- immediately adjacent local context when available (previous/current/next grouped unit or excerpt)
- key metadata summary
- linked anomaly or flag ids
- source artifact pointers

For dropped units, the exporter must still generate cards from Phase 2b groupings even when no final excerpt exists.

### 5.5 Sampling logic

The exporter must support both:

- **required inclusions** — all hard-failure cases and all DEPENDENT cases, and
- **bounded samples** — top-N candidates for softer buckets.

Default v1 packet sizing:

- include all hard-failure cases
- include all DEPENDENT cases
- include up to 10 highest-risk PARTIAL cases per book
- include up to 10 fragmentation cases per book
- include up to 10 structural/editorial cases per book
- include up to 10 attribution/evidence-sensitive cases per book
- include 5 positive controls per book

The exact thresholds are implementation defaults, not durable law. They may be tuned after the first real campaign.

## 6. Formal full-book testing protocol

### 6.1 Execution sequence

For the 5-book campaign, the protocol is:

1. Run excerpting for all five books.
2. Run analyzer across all books.
3. Produce per-book statuses and campaign summary.
4. Export review packets per book.
5. Perform bounded human review of the exported packets.
6. Issue final campaign interpretation.

No book should be judged by folder browsing alone.

### 6.2 Automatic per-book machine status

A book is an automatic **FAIL** if any of these conditions hold:

- zero final excerpts despite upstream processing
- any grouped-unit loss without explicit accounted reason
- any chunk lifecycle break
- any truncation event that clearly corrupts or aborts downstream flow
- contradiction between actual artifacts and logged success state
- missing gate artifact where one is required

A book is an automatic **CONCERN** if it avoids FAIL but shows one or more of:

- elevated PARTIAL rate
- any DEPENDENT units
- unusually high structural/editorial share
- unusually high ultra-short excerpt rate
- high unresolved cross-reference burden
- unusually high consensus/review-flag load
- major timing or cost outlier without obvious explanation

A book is machine **PASS** only when:

- phase accounting is intact,
- no hard-failure flags are present,
- no major contradictions exist,
- and soft metrics are within normal cross-book range.

### 6.3 Human review protocol

Human review should answer four questions per book:

1. Are the exported positive-control excerpts genuinely good teaching units?
2. Are flagged PARTIAL / DEPENDENT cases correctly judged?
3. Do fragmentation buckets reveal oversplitting or noisy boundary decisions?
4. Do attribution/evidence-sensitive cases feel trustworthy enough for continued scale-up?

Human review is not expected to reread the whole book output. It is expected to inspect the exported packets only.

### 6.4 Final campaign interpretation

The campaign is **PASS** if:

- no more than isolated CONCERN books remain,
- no repeated structural hard failures are present,
- positive controls are strong across genres,
- and human review does not discover a hidden systematic defect.

The campaign is **CONCERN** if:

- the system yields meaningful excerpts,
- but recurring soft issues suggest threshold calibration or modest implementation work before larger scale.

The campaign is **FAIL** if:

- structural accounting failures recur,
- silent failures appear in more than an isolated book,
- or human review shows that apparently successful books are pedagogically unreliable.

## 7. Historical anomalies the analyzer must explicitly catch

Analyzer v1 is not complete unless it catches these already-observed patterns on `integration_tests/run_20260328/`:

### 7.1 Taysir unit-loss anomaly

The analyzer must detect that `taysir` has more grouped units than final excerpts and must identify which grouped units did not survive into `excerpts.jsonl`.

Expected analyzer behavior:

- mark book status at least `FAIL`
- emit `grouped_unit_loss`
- list missing unit lineages explicitly
- attach the corresponding `EX-V-002` run evidence

### 7.2 Ibn Aqil v3 silent-zero anomaly

The analyzer must detect that `ibn_aqil_v3` has substantial upstream runtime but zero final excerpts and no logged errors.

Expected analyzer behavior:

- mark book status `FAIL`
- emit `zero_excerpt_run_with_upstream_activity`
- emit `artifact_log_contradiction` or equivalent silent-failure flag
- highlight the abnormal Phase 2a duration

### 7.3 Truncation anomaly

The analyzer must detect any raw response ending with `finish_reason = length` and treat it as a first-class evaluation signal.

Expected analyzer behavior:

- attach truncation to the affected book and call record
- infer likely downstream impact when correlated with missing outputs
- never let a truncated run appear clean just because error logs stayed empty

### 7.4 Semantic phase-label mismatch

The analyzer must inspect call content and detect when a file label like `enrich_0001.json` actually contains classification-shaped output.

Expected analyzer behavior:

- infer semantic phase from response structure when possible
- flag mismatches instead of trusting filename convention blindly
- use this to make downstream metrics and debugging credible

## 8. Implementation boundary after this brief

The next work is suited for bounded implementation, not more architectural debate.

### 8.1 Bounded implementation tasks

These are now appropriate for Codex or Claude Code:

1. Implement analyzer ingestion and lineage accounting.
2. Implement per-book metrics and flag generation.
3. Implement campaign aggregation.
4. Implement review candidate generation.
5. Implement review-packet exporter formatting.
6. Wire analyzer execution into the full-run workflow, either as a follow-on script or as a distinct post-run command.
7. Prove analyzer v1 on `integration_tests/run_20260328/` before the real 5-book campaign.

### 8.2 What still remains reasoning work

These items should stay out of the immediate implementation ticket unless the historical run proves them necessary:

- threshold calibration for soft concern flags
- dashboard/UI decisions
- prompt changes to the excerpting engine
- new excerpting features beyond evaluation infrastructure
- taxonomy or synthesis interpretation layers

## 9. Minimal success definition for analyzer v1

Analyzer v1 is successful if it can run on `integration_tests/run_20260328/` and produce:

- a correct per-book status for all five books,
- explicit detection of the `taysir` grouped-unit loss,
- explicit detection of the `ibn_aqil_v3` silent-zero/truncation failure,
- campaign-level comparison across the five books,
- and review packets that a human can use without browsing raw run folders.

That is enough to make the upcoming full-book campaign genuinely diagnostic.