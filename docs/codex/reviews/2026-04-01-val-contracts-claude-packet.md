# KR `val-contracts` Review Packet

Date: 2026-04-01
Authority: `active_authority: claude`
Runtime mode: `shadow_setup`
Source artifacts:

- `overnight_codex/results/val-contracts/final_response.json`
- `overnight_codex/results/val-contracts/summary.md`

## Executive Summary

`val-contracts` found one cross-boundary cluster that is immediately blocking for correctness: the live excerpting, taxonomy, and synthesis boundaries no longer describe the same machine-readable shapes, and one excerpting fallback output that is currently considered valid upstream is rejected downstream. A second blocker is text integrity: excerpting mutates serialized primary text on write despite its own output contract promising byte preservation.

Under the current authority lane, Codex should not implement any engine-side fixes. This packet is therefore a decision-ready handoff for Claude-owned engine follow-up. The top 3 blockers below should be handled before any contract-tooling refresh, because the tooling rewrite would otherwise risk freezing the wrong boundary shape into validation.

## Ordered Blockers

### 1. A3 `TEXT_INTEGRITY`

- Boundary: `excerpting output -> taxonomy input`
- Severity: HIGH
- Why this matters now: this is the only finding that directly describes downstream text mutation on disk, which makes it a knowledge-integrity risk rather than only a schema mismatch.
- Evidence:
  - `engines/excerpting/contracts.py:468-472`
  - `engines/excerpting/src/writer.py:26-27`
  - `engines/excerpting/src/writer.py:77-87`
  - `engines/excerpting/tests/test_writer.py:330-360`
- Current contradiction:
  - `ExcerptRecord.primary_text` says primary text is never modified after extraction.
  - the writer strips consecutive ZWNJ characters before serializing `excerpts.jsonl`.
- Smallest safe fix:
  - decide whether the current ZWNJ stripping is a bug fix or a contract violation
  - then align the writer behavior, the excerpting contract text, and the Arabic-integrity regression tests to one rule
- Owner lane: Claude engine lane

### 2. A2 `EXCERPTING_TO_TAXONOMY`

- Boundary: `excerpting -> taxonomy`
- Severity: HIGH
- Why this matters now: this is a direct valid-upstream / invalid-downstream mismatch on a live adjacent boundary.
- Evidence:
  - `engines/excerpting/contracts.py:516-519`
  - `engines/excerpting/src/phase3_deterministic.py:600-642`
  - `engines/excerpting/src/phase3_validation.py:114-124`
  - `engines/taxonomy/src/engine.py:45-47`
  - `engines/taxonomy/src/engine.py:230-237`
- Current contradiction:
  - excerpting allows `excerpt_topic=[]` when enrichment failed and treats that state as valid if `llm_enrichment_failed` is present
  - taxonomy rejects the same record because `excerpt_topic` is required and empty lists are refused
- Smallest safe fix:
  - either taxonomy must explicitly accept the empty-topic fallback when `llm_enrichment_failed` is present
  - or excerpting must guarantee at least one topic before write
- Owner lane: Claude engine lane

### 3. A1 `TAXONOMY_CONTRACTS`

- Boundary: `taxonomy -> synthesis`
- Severity: HIGH
- Why this matters now: this is the main authoritative-contract drift. Until this is fixed, synthesis expectations and taxonomy runtime output are not describing the same boundary.
- Evidence:
  - `engines/taxonomy/src/engine.py:17-24`
  - `engines/taxonomy/contracts.py:156-171`
  - `engines/taxonomy/contracts_core.py:153-175`
  - `engines/taxonomy/src/writer.py:45-63`
  - `engines/synthesis/contracts.py:147-183`
  - `engines/synthesis/SPEC.md:31-35`
  - `engines/synthesis/SPEC.md:202-208`
  - `engines/synthesis/SPEC.md:920-925`
  - `engines/synthesis/src/tracer.py:27-30`
- Current contradiction:
  - taxonomy runtime uses `contracts_core.py`
  - published taxonomy contract requires fields the runtime shape omits, including `verified_flagged_status`
  - synthesis has no machine-readable placed-excerpt input model matching the runtime taxonomy output
  - taxonomy writes one file per excerpt while the current synthesis tracer expects one aggregate taxonomy JSON object
- Smallest safe fix:
  - choose one authoritative runtime contract for taxonomy
  - align synthesis input expectations to that contract and actual on-disk taxonomy output
  - only after that, update downstream validation/tracer assumptions
- Owner lane: Claude engine lane

## Verification Confidence Blocker

### 4. A4 `VALIDATION_TOOLING`

- Boundary: tooling across `source -> normalization -> excerpting -> taxonomy -> synthesis`
- Severity: HIGH
- Why this matters now: current verification scripts would miss active drift even if engine code is partially fixed.
- Evidence:
  - `scripts/verify_metadata_flow.py:22-30`
  - `tools/check_cross_engine_contracts.py:26-29`
  - `tools/check_cross_engine_contracts.py:128-145`
  - `tools/check_cross_engine_contracts.py:197-232`
  - `engines/normalization/tests/test_contract_boundaries.py:1-8`
  - `engines/normalization/tests/test_contract_boundaries.py:107-112`
  - `engines/excerpting/contracts.py:5-9`
- Current contradiction:
  - tooling still models the retired passaging/atomization chain
  - active taxonomy runtime contracts and enum drift are not being checked
- Smallest safe fix:
  - refresh verification only after A1/A2/A3 define the live adjacent boundaries that should be enforced
- Owner lane: Claude engine lane after boundary decisions are locked

## Structural Follow-Ons

### 5. `source -> normalization` enum mismatch

- Severity: MEDIUM
- Evidence:
  - `engines/source/contracts.py:46-55`
  - `engines/normalization/src/dispatcher.py:25-29`
  - `engines/normalization/tests/test_contract_boundaries.py:67-74`
- Current issue:
  - source can emit eight `SourceFormat` values
  - normalization only dispatches `SHAMELA_HTML` and `PLAIN_TEXT`
- Smallest safe fix:
  - either narrow the adjacent contract or make normalization explicitly encode unsupported-but-valid upstream enum handling
- Owner lane: Claude engine lane

### 6. D-023 adjacent-schema weakness

- Severity: MEDIUM
- Evidence:
  - `engines/source/contracts.py:732-847`
  - `engines/normalization/contracts.py:660-723`
  - `engines/excerpting/src/pipeline.py:98-100`
  - `engines/normalization/tests/test_contract_boundaries.py:76-85`
  - `engines/synthesis/SPEC.md:35`
  - `engines/synthesis/SPEC.md:207-208`
- Current issue:
  - metadata flow is mostly preserved indirectly by `source_id` and late lookup, not by adjacent-schema carry-forward
- Smallest safe fix:
  - decide whether adjacent boundaries must carry more machine-readable metadata directly, or whether registry-only resolution is the accepted contract
- Owner lane: Claude engine lane

## Recommended Execution Order

1. Decide A3 first: the writer text-mutation rule is a direct integrity question and should not remain ambiguous.
2. Resolve A2 next: adjacent excerpting→taxonomy acceptance must become internally coherent.
3. Unify A1 after that: lock one authoritative taxonomy runtime contract and one synthesis-side input expectation.
4. Resolve the medium structural follow-ons in the context of the chosen authoritative contract.
5. Only then perform A4 and refresh the contract-validation tooling to the actual direct boundaries.

## Review Ask

- Confirm whether the blocker ordering above is correct.
- Challenge any evidence link that is overstated or missing a necessary counterexample.
- If any finding should be downgraded, say exactly why.
- If any omitted blocker is higher priority than the current top 3, identify it with exact evidence.
