> Purpose: Harden the excerpting evaluation brief into an implementation-safe contract.
> Status: authoritative implementation supplement.
> Scope: analyzer v1, campaign aggregation, and review-packet export for excerpting runs.
> Authority rule: If this file conflicts with `reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md`, this file wins for implementation semantics.

# Excerpting Evaluation Hardening Pack

## 1. Final judgment

The excerpting evaluation layer should be built now, but not from the original brief alone. The strategic direction is correct, the repo is ready enough, and the historical run already proves the need. However, the implementation contract must be hardened in a few non-negotiable ways so the analyzer does not become a polished source of false certainty.

## 2. Non-negotiable corrections

### 2.1 Canonical lineage key
The analyzer must normalize grouped units and final excerpts into one canonical unit ledger keyed by:

`(source_id, div_id, chunk_index, unit_index)`

`chunk_id` is retained as auxiliary metadata only. It is not the primary join key.

### 2.2 Unit-ledger first
The analyzer must be built around a per-unit ledger, not around aggregate counts. All summaries, anomalies, and review candidates must derive from that ledger.

### 2.3 Observed vs inferred
Every anomaly, review candidate, and review card must declare an `evidence_basis` value:
- `observed`
- `inferred_high_confidence`
- `inferred_moderate_confidence`

The analyzer may detect loss, truncation, and contradictions exactly, but it must not overclaim per-unit root causes when current artifacts only support inference.

### 2.4 Structural status first
The analyzer must not emit final scholarly `PASS / CONCERN / FAIL` as its primary machine status.

Machine status must be:
- `STRUCTURAL_FAIL`
- `STRUCTURAL_CONCERN`
- `STRUCTURALLY_CLEAN`

Final `PASS / CONCERN / FAIL` belongs only after review-packet generation and bounded human review.

### 2.5 Request-first raw-trace inference
Raw request/response files such as `enrich_0001.json` are client-label artifacts, not authoritative semantic stage labels. The analyzer must infer semantic phase from request structure first, use response structure as corroboration, and treat file/client prefixes as non-authoritative metadata.

Do not flag filename/client-label ambiguity as a true semantic mismatch by itself.

### 2.6 Metric authority tiers
Metrics must be explicitly tiered:
- decision-grade structural
- operational
- review-risk / triage
- descriptive

Heuristic or LLM-enriched metrics must not directly determine machine structural status.

### 2.7 Packet anti-bias requirements
The review packet must not be anomaly-only and must not be a positive-control scrapbook. It must include:
1. mandatory observed failures
2. inferred diagnostics
3. self-containment / boundary-risk cases
4. a sentinel audit sample chosen independently of anomaly ranking
5. stratified positive controls
6. ambiguity / near-threshold cases

Each section must show denominators and sample policy.

### 2.8 Standalone post-run implementation first
The first implementation must be standalone and post-run. Do not begin by rewiring engine execution or building a dashboard/UI.

## 3. Safest implementation shape

Implement these standalone scripts:
- `scripts/analyze_excerpting_run.py`
- `scripts/analyze_excerpting_campaign.py`
- `scripts/export_excerpting_review_packet.py`

They should consume existing run folders and write `analysis/` artifacts into those folders.

## 4. Required outputs

### 4.1 Per-book analyzer outputs
- `analysis/book_summary.json`
- `analysis/book_summary.md`
- `analysis/anomalies.json`
- `analysis/review_candidates.jsonl`

### 4.2 Campaign outputs
- `analysis/campaign_summary.json`
- `analysis/campaign_summary.md`
- `analysis/campaign_book_table.json`

### 4.3 Review-packet outputs
- `analysis/review_packet.md`
- `analysis/review_packet.json`
- `analysis/review_manifest.json`

## 5. Required analyzer behavior

### 5.1 Structural anomalies the analyzer must catch
The analyzer is not complete unless it explicitly catches these on `integration_tests/run_20260328/`:

- `taysir`: grouped-unit loss between Phase 2b and final excerpts.
- `ibn_aqil_v3`: zero-output run with upstream activity.
- truncation via `finish_reason = length`.
- correct treatment of client-label ambiguity in raw traces.
- correct semantic phase inference from request content.

### 5.2 Structural hard-failure conditions
These may directly drive `STRUCTURAL_FAIL`:
- grouped-unit loss
- unexplained chunk drop
- zero final excerpts despite upstream activity
- artifact/log contradiction
- missing gate artifact only when gate existence is independently evidenced
- critical truncation correlated with downstream absence
- request expected but response and error artifacts both missing

### 5.3 Structural concerns
These may drive `STRUCTURAL_CONCERN`:
- incomplete trace pairing
- unparseable response for expected semantic phase
- unresolved lineage join requiring fallback logic
- observability gaps that prevent confident interpretation

### 5.4 Review-risk / triage concerns
These must feed packet composition and review ordering, not structural status by themselves:
- elevated PARTIAL / DEPENDENT burden
- clustered short-excerpt patterns
- unresolved cross-reference burden
- high consensus load
- structural/editorial-heavy output populations

## 6. Metric authority model

### 6.1 Decision-grade structural metrics
Examples:
- phase coverage metrics
- grouped-to-final survival metrics
- dropped-unit and dropped-chunk counts
- artifact/log contradictions
- zero-output-with-upstream-activity
- trace truncation and missing-call metrics

### 6.2 Operational metrics
Examples:
- runtime
- per-model token usage
- latency
- cost
- parse-status distribution

### 6.3 Review-risk / triage metrics
Examples:
- PARTIAL / DEPENDENT rates
- context-hint coverage
- unresolved cross-reference rate
- consensus-load rate
- clustered shortness and boundary-risk patterns

### 6.4 Descriptive metrics
Examples:
- function distributions
- content-type mix
- quoted-scholar density
- school-attribution density
- evidence-like density
- topic density

Each metric should carry provenance where practical, such as:
- `artifact_accounting`
- `deterministic_structural`
- `heuristic_extracted`
- `llm_enriched`
- `consensus_adjusted`
- `derived_operational`

## 7. Review-packet design rules

### 7.1 Required packet lanes
Every packet must include:
1. observed structural failures
2. inferred diagnostics
3. self-containment / boundary-risk cases
4. sentinel audit sample
5. stratified positive controls
6. ambiguity / near-threshold cases

### 7.2 Card requirements
Each card must include:
- canonical unit key
- bucket tags
- stage state
- evidence basis
- primary text
- context view
- observed facts
- inferred interpretation
- artifact pointers
- review questions

### 7.3 Section header requirements
Each packet section must show:
- denominator / population size
- selected sample count
- selection rule
- prevalence when applicable

## 8. Known observability limits the analyzer must respect

Current repo artifacts are strong enough for analyzer v1, but the analyzer must remain conservative because:
- failed Phase 2a / Phase 2b chunks may be absent rather than explicitly ledgered;
- validation drops are not persisted as first-class artifacts;
- `verify_gate_queue()` exists but is not currently invoked by the runner;
- raw trace logs do not explicitly store semantic phase or chunk ID.

The analyzer must compensate where possible, but it must not overclaim certainty.

## 9. Acceptance checklist

The implementation is acceptable only if all of the following are true:

- it runs on `integration_tests/run_20260328/` without changing excerpting prompts or phase logic;
- it builds a canonical per-unit ledger keyed by `(source_id, div_id, chunk_index, unit_index)`;
- it emits machine structural status rather than final scholarly verdict;
- it catches `taysir` grouped-unit loss;
- it catches `ibn_aqil_v3` zero-output-with-upstream-activity;
- it detects truncation via `finish_reason = length`;
- it infers semantic phase from request content correctly;
- it does not misreport `enrich_0001.json` as a true phase-label anomaly when the request itself is classification-shaped;
- it emits review packets that include sentinel audit sampling and stratified positive controls;
- it explicitly lists any remaining observability limits it could not eliminate.

## 10. Implementation handoff prompt

```text
Read these first, in this order:

1. .kr/README.md
2. .kr/CHARTER.md
3. .kr/ACTIVE.md
4. .kr/HANDOFF.md
5. reference/EXCERPTING_FULL_BOOK_EVALUATION_BRIEF.md
6. reference/EXCERPTING_EVALUATION_HARDENING_PACK.md

Then implement the active frontier exactly, with the hardening rules below.

Task:
Build a standalone, post-run excerpting evaluation layer consisting of:
1. a per-book analyzer,
2. a campaign aggregator,
3. and the first review-packet exporter.

Inputs:
- engines/excerpting/SPEC.md
- engines/excerpting/contracts.py
- scripts/run_integration_test.py
- scripts/run_full_integration.py
- integration_tests/run_20260328/

Implementation shape:
- Do NOT modify excerpting prompts or phase logic.
- Do NOT build a dashboard/UI.
- Do NOT deeply wire this into engine execution yet.
- Build standalone scripts that read existing run folders and write analysis outputs into analysis/ subdirectories.

Required scripts:
- scripts/analyze_excerpting_run.py
- scripts/analyze_excerpting_campaign.py
- scripts/export_excerpting_review_packet.py

Non-negotiable analyzer rules:
1. Build a canonical per-unit ledger first.
   Canonical unit key:
   (source_id, div_id, chunk_index, unit_index)

2. Treat chunk_id as auxiliary metadata only, not the primary join key.

3. Separate observed facts from inferred causes everywhere.
   Every anomaly and review candidate must declare evidence_basis:
   - observed
   - inferred_high_confidence
   - inferred_moderate_confidence

4. Use machine structural status, not final scholarly verdict:
   - STRUCTURAL_FAIL
   - STRUCTURAL_CONCERN
   - STRUCTURALLY_CLEAN

5. Infer raw-call semantic phase from request structure first.
   Treat raw filename/client prefixes like enrich_0001.json as non-authoritative.
   Do not flag client-label ambiguity as a true semantic mismatch by itself.

6. Tier metrics by authority:
   - decision-grade structural
   - operational
   - review-risk / triage
   - descriptive
   Weak heuristic or LLM-enriched metrics must not directly determine structural status.

Required per-book outputs:
- analysis/book_summary.json
- analysis/book_summary.md
- analysis/anomalies.json
- analysis/review_candidates.jsonl

Required campaign outputs:
- analysis/campaign_summary.json
- analysis/campaign_summary.md
- analysis/campaign_book_table.json

Required packet outputs:
- analysis/review_packet.md
- analysis/review_packet.json
- analysis/review_manifest.json

Required packet design:
Include these lanes:
1. mandatory observed failures
2. inferred diagnostics
3. self-containment / boundary risk
4. sentinel audit sample chosen independently of anomaly ranking
5. stratified positive controls
6. ambiguity / near-threshold cases

Each section must show denominators and sample policy.
Each card must include:
- canonical unit key
- bucket tags
- stage state
- evidence basis
- primary text
- context
- observed facts
- inferred interpretation
- artifact pointers
- review questions

Mandatory regression checks on integration_tests/run_20260328/:
- detect taysir grouped-unit loss
- detect ibn_aqil_v3 zero-output-with-upstream-activity
- detect truncation via finish_reason=length
- detect client-label ambiguity correctly
- infer semantic phase from request content correctly
- do NOT misreport enrich_0001.json as a true phase-label anomaly if the request itself is classification-shaped

Important observability cautions:
- failed Phase 2a / 2b chunks may be absent rather than explicitly logged
- validation drops are not persisted as first-class artifacts
- gate_queue verification exists in code but is not currently invoked by the runner
- raw traces do not explicitly store semantic phase or chunk_id
The analyzer must compensate conservatively and must not overclaim certainty.

Success criteria:
- analyzer runs on integration_tests/run_20260328/
- it catches the known taysir and ibn_aqil_v3 failures
- it emits structurally honest summaries
- it emits review packets that are not anomaly-only and not cherry-picked reassurance
- it keeps structural status separate from final scholarly verdict

At the end:
- show changed files
- explain how each file maps to the hardened contract
- report whether each mandatory regression check passed
- explicitly list any remaining observability limitations the implementation could not eliminate
- update .kr/HANDOFF.md and .kr/ACTIVE.md only if the frontier is truly completed or materially narrowed
```

## 11. After analyzer v1 lands

The highest-value observability upgrades after analyzer v1 proves itself are:
1. invoke `verify_gate_queue()` from the runner;
2. persist Phase 2a and Phase 2b failure ledgers;
3. persist validation-drop ledgers;
4. include semantic phase and chunk metadata in raw trace logs.

Those are important next improvements, but they are not prerequisites for analyzer/exporter v1.