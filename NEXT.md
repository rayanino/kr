# NEXT — Tracer Bullet (Step 0)

**Session type:** BUILD
**Goal:** Get real Arabic text flowing from `html_export_minimal` through all 7 engines to a rough knowledge entry. Validate every contract boundary with real data.

---

## What to read first

1. `skills/shared/ENGINE_PROTOCOL.md` — Step 0 section (the tracer bullet spec)
2. `reference/CORE_CONTRACT_CLASSIFICATION.md` — which models to reconcile (125 core, skip 171 deferred)
3. `tests/fixtures/html_export_minimal/` — the input fixture (Shamela HTML: info.html + content.html)
4. `reference/archive/abd_code/normalization/` — working Shamela parser to adapt for the normalization stub

## What NOT to read

- Full SPECs (1000+ lines each) — only consult specific sections when a contract question arises
- VISION.md — not needed for the tracer bullet
- kr_decisions.md — not needed
- Deferred contract classes — skip everything marked DEFERRED in CORE_CONTRACT_CLASSIFICATION.md

---

## The work (in order)

### Phase 1: Contract reconciliation (core-only)
For each of the 6 boundaries (source→norm, norm→passaging, passaging→atom, atom→excerpt, excerpt→taxonomy, taxonomy→synthesis):
- Load upstream CORE output model
- Load downstream CORE input expectations
- Fix type conflicts, missing fields, renamed enums
- Verify with `python3 -c "from engines.X.contracts import ...; from engines.Y.contracts import ..."`
- Document every mismatch found in `reference/TRACER_FINDINGS.md`

### Phase 2: Shared component stubs
Build minimal stubs in `shared/*/src/`:
- `consensus`: `evaluate(task, models, threshold)` → returns hardcoded agreement
- `human_gate`: `create_checkpoint(source_id, reason, context)` → auto-logs, returns checkpoint_id
- `scholar_authority`: `lookup(name)` → returns None; `register(record)` → stores in JSON
- `validation`: `validate_output(data, schema)` → returns empty list (passes everything)

### Phase 3: Engine stubs
Each engine gets a `process(input_path, output_path, config)` function that:
- Reads input JSON from disk
- Performs the simplest possible transformation
- Writes output JSON conforming to its CORE output contract

**Source engine:** Read `html_export_minimal/`, extract title+author from info.html, freeze files, write SourceMetadata JSON.
**Normalization engine:** Adapt ABD Shamela parser from `reference/archive/abd_code/normalization/` to produce a NormalizedPackage. This is the one stub that should produce REAL output, not placeholders.
**Passaging–Synthesis:** Minimal transformations. LLM calls return hardcoded plausible values. The output quality will be terrible — that's fine. Data flowing > data quality.

### Phase 4: Pipeline runner
Build `scripts/run_pipeline.py`:
- Chains 7 engines sequentially
- At each boundary: validates output against next engine's CORE input contract using Pydantic `model_validate()`
- Logs every validation error with field name and details
- Continues through all 7 even if errors occur (collect all issues in one pass)

### Phase 5: Run it
Feed `html_export_minimal` through the full pipeline. Document:
- Every contract violation at every boundary
- Every metadata field that was lost (D-023)
- Every assumption that broke
- The rough entry that came out (even if terrible)

---

## Done when

- [ ] One Shamela HTML fixture produces one rough knowledge entry
- [ ] Zero contract violations at all 6 boundaries (or all violations documented with fixes)
- [ ] All 7 CORE contracts import-tested against neighbors
- [ ] Shared component stubs exist and are callable
- [ ] Pipeline runner script works
- [ ] `reference/TRACER_FINDINGS.md` documents all boundary issues
- [ ] Everything committed and pushed

---

## Then show the owner

The rough output from `html_export_minimal`. Ask:
- "Is this the right book?"
- "Is this the right author?"
- "Does the text look right?"

Owner sanity check — 10 minutes, not scholarly audit.
