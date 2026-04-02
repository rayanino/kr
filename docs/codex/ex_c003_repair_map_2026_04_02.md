# `EX-C-003` Repair Map — 2026-04-02

Goal: identify the first engine symbols and tests to open for the second-ranked
failure class: Phase 2a chunk failures.

## Highest-Probability Loci

### 1. `engines/excerpting/src/phase2_classify.py`

Primary symbols:

- `run_phase2a(...)`
- `classify_chunk(...)`
- `normalize_offsets(...)`
- `verify_segments(...)`

Why this is first:

- `run_phase2a()` is the actual failure boundary for `EX-C-003`
- it retries across three phases:
  - classify
  - normalize
  - verify
- failed chunks are removed from the returned dict entirely, so this is the
  point where whole chunks vanish from downstream coverage

### 2. `normalize_offsets(...)` and `verify_segments(...)`

Why these are especially suspect:

- `EX-C-003` is used for normalize failures, which is exactly where snippet
  anchoring can go wrong
- `EX-C-004` covers coverage-invariant failures in `verify_segments(...)`
- the failed chunk set includes both tiny and large chunks, so the next session
  should not assume only transport/API instability

What to inspect first:

- snippet-finding cascade and anchor progression in `normalize_offsets(...)`
- coverage invariant strictness in `verify_segments(...)`
- whether some real chunks with heavy headings / repeated formulas / OCR noise
  produce ambiguous snippet anchors

### 3. Prompt/Schema seam in `classify_chunk(...)`

Why this remains plausible:

- the classify prompt requires exact copied `text_snippet`
- if the model violates exact-copy requirements, the later normalize phase will
  fail even though the JSON schema itself validates
- that would explain large failed chunks without requiring transport failure

## First Tests To Open

1. [test_phase2_classify.py](/home/rayane/kr-codex/engines/excerpting/tests/test_phase2_classify.py)
   - `test_retry_on_normalization_failure`
   - `test_coverage_failure_retry_with_feedback`
   - `test_retry_on_validation_error`

2. [test_phase2_hardening.py](/home/rayane/kr-codex/engines/excerpting/tests/test_phase2_hardening.py)
   - the retry/error-recovery section for mixed error paths
   - add fixtures modeled on the exact failed chunk ids from the packet

3. [test_error_recovery.py](/home/rayane/kr-codex/engines/excerpting/tests/test_error_recovery.py)
   - reuse existing retry-path scaffolding for concrete `EX-C-003` chunk cases

## Exact Evidence Packet

Use:

- [ex_c003_phase2a_failure_packet_2026_04_02.md](/home/rayane/kr-codex/docs/codex/ex_c003_phase2a_failure_packet_2026_04_02.md)

Notable failed chunks to start with:

- `ibn_aqil_v1/div_src_test0001_2_000` (`1397` words)
- `ibn_aqil_v1/div_src_test0001_2_001` (`1381` words)
- `taysir/div_src_test0001_2_006_pre` (`1236` words)
- `taysir/div_src_test0001_6_082` (`816` words)

These are large enough that they are more likely to expose real prompt/anchor
fragility than tiny edge fragments.
