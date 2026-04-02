# `EX-V-002` Repair Map — 2026-04-02

Goal: identify the first engine symbols and tests to open for the top-ranked
failure class: post-grouping validation drops before final excerpt output.

## Highest-Probability Loci

### 1. `engines/excerpting/src/phase3_validation.py`

Primary symbols:

- `validate_excerpt(...)`
- `validate_batch(...)`

Why this is first:

- `validate_excerpt()` has exactly one hard drop path: V-P3-2 text integrity.
- That drop is triggered when `text_snippet` does not match the normalized
  prefix of `primary_text`.
- The validation-drop ledgers from completed books are therefore almost
  certainly manifestations of this path, not writer corruption.
- The strongest current evidence is that the gate is plausibly over-strict in
  two distinct ways:
  - short structural units fail only because `compare_len < 20`
  - other units fail on small character drift that whitespace normalization
    does not forgive

What to inspect first:

- whether the V-P3-2 comparison is too strict for short structural units
- whether tiny fragments like `الثالثة`, `الرابعة`, `انتهى`, and pure headings
  are being dropped correctly or incorrectly
- whether the compare-length / normalization rules are miscalibrated for
  headings, newline-heavy snippets, or short-unit excerpts
- whether diacritic-form or tiny prefix drift (`َّ` vs `َّ`, dropped leading
  conjunctions, etc.) is creating false negatives that should be tolerated

### 2. `engines/excerpting/src/phase3_deterministic.py`

Primary symbols:

- `build_deterministic_excerpts(...)`
- `ExcerptRecord(... text_snippet=unit.text_snippet, primary_text=...)`

Why this is second:

- deterministic assembly copies `unit.text_snippet` directly from Phase 2b
  into the final `ExcerptRecord`
- V-P3-2 later compares that carried-forward snippet against the newly
  extracted `primary_text`
- if these are constructed from slightly different assumptions, validation
  will drop the excerpt even when the unit itself is legitimate
- the smoke artifacts suggest the grouped snippet is preserved verbatim while
  the reconstructed `primary_text` is source-correct, so the mismatch can be
  produced upstream of validation even when writer behavior is fine

What to inspect first:

- whether `unit.text_snippet` from Phase 2b is always guaranteed to be the
  prefix of the final `primary_text`
- whether short structural/heading units violate that assumption
- whether the final `primary_text` extraction path and the Phase 2b snippet
  path are normalized differently for short or heading-like units

### 3. `engines/excerpting/src/phase3_orchestrator.py`

Primary symbols:

- `run_phase3(...)`
- the `validation_drops` collection block

Why this is third:

- this is the seam where dropped excerpts become visible artifacts
- it already records per-unit identity, so it is the right place to attach
  richer reason codes later if engine work opens

What to inspect first:

- whether `validation_drops` should also record emitted validation error codes
- whether the orchestrator can distinguish “expected trivial drop” from
  “structural bug” without changing the engine behavior yet
- whether adding compared-prefix evidence here would remove the need to
  reconstruct failures manually from `validation_drops.jsonl`

## First Tests To Open

1. [test_state_machine_edge.py](/home/rayane/kr-codex/engines/excerpting/tests/test_state_machine_edge.py)
   - `test_text_integrity_validation_drops_corrupt`
   - expand this from a single obviously bad mismatch to real short structural
     cases and tiny-prefix drift cases from the smoke artifacts

2. [test_phase3_validation.py](/home/rayane/kr-codex/engines/excerpting/tests/test_phase3_validation.py)
   - add regression fixtures from the `EX-V-002` packet and
     `validation_drops.jsonl`

3. [test_phase3_deterministic.py](/home/rayane/kr-codex/engines/excerpting/tests/test_phase3_deterministic.py)
   - add assertions that `unit.text_snippet` and final `primary_text` stay aligned
   - especially for tiny headings / structural transitions / newline-heavy prefixes

4. [test_integration.py](/home/rayane/kr-codex/engines/excerpting/tests/test_integration.py)
   - current helpers appear too idealized to expose the real smoke-run failure
     shapes; open these once the direct validation and deterministic tests are
     in view

## Working Hypothesis

The broadest likely seam is:

`Phase 2b unit.text_snippet` -> carried into deterministic `ExcerptRecord`
-> compared by V-P3-2 against final `primary_text` prefix

That makes `phase3_validation.py` the first place to inspect, but
`phase3_deterministic.py` is the likely upstream producer of the mismatch.
