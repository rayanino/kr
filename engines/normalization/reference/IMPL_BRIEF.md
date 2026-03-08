# Normalization Engine — Implementation Brief

**Audience:** Claude Code. This document tells you what to build, in what order, with what constraints.

**Read before coding:**
- `engines/normalization/SPEC.md` — the behavioral authority (full SPEC)
- `engines/normalization/contracts.py` — the schema authority (Pydantic models)
- `engines/normalization/src/errors.py` — error codes (already defined)
- `engines/normalization/src/normalizers/base.py` — normalizer interface (already defined)

**Do NOT use ABD code as a reference or starting point.** ABD code (D-019) has zero design authority. Build from the SPEC. The SPEC describes what each normalizer does; Claude Code implements it fresh.

---

## Architecture

The normalization engine is format-agnostic by design:

```
Source (any format) → Dispatcher → Format-specific Normalizer → Normalized Package (uniform schema)
```

- The **dispatcher** routes sources to normalizers by `source_format` field
- Each **normalizer** implements the `BaseNormalizer` interface
- All normalizers produce the same output schema (`NormalizedPackage` in contracts.py)
- **Validation** and **writing** are shared — they work on any normalized package regardless of which normalizer produced it

Adding a new format means adding ONE normalizer module and registering it. No other code changes.

---

## What Exists Today

| File | Status |
|------|--------|
| `contracts.py` | Complete — output schema, all enums, all models |
| `src/errors.py` | Complete — all error codes defined |
| `src/normalizers/base.py` | Complete — normalizer interface |
| `src/dispatcher.py` | Stub — register normalizers after building them |
| `src/normalizers/shamela.py` | Stub — ONE of the format normalizers |
| `src/validation.py` | Stub — validate any normalized package |
| `src/writer.py` | Stub — atomic write of any normalized package |
| `src/layer_detector.py` | Stub — detect text layers (format-agnostic interface, format-specific backends) |
| `src/content_flagger.py` | Stub — flag content types |
| `src/content_census.py` | Stub — statistical profiling |

## Implementation Order

**Build format-agnostic infrastructure FIRST. Then add normalizers one at a time.**

### Phase 1: Format-Agnostic Foundation (no format-specific code)

**Step 1: Output schema + atomic writer**
- Implement `writer.py`: takes a `NormalizedManifest` + stream of `ContentUnit`, writes to disk atomically
- Test: write a manually-constructed NormalizedPackage, verify JSON schema compliance

**Step 2: Validation**
- Implement `validation.py`: 8 checks from SPEC §5 that apply to ANY normalized package
- Test: valid package passes, packages with missing fields / broken references / empty content fail

**Step 3: Dispatcher**
- Implement `dispatcher.py`: registry pattern, routes `source_format` → normalizer instance
- Test: known formats route correctly, unknown format raises `NORM_UNKNOWN_SOURCE_FORMAT`

**Step 4: Layer detector interface**
- Implement `layer_detector.py` with format-agnostic interface: `detect_layers(page_content, format_hints) → List[TextLayerSegment]`
- Format-specific detection backends are plugged in per-format (each normalizer registers its layer detection strategy)
- Test: interface contract verified with mock backends

**Step 5: Content flagger + census**
- Implement `content_flagger.py` and `content_census.py` — both operate on ANY normalized content stream
- Test: flag detection and census statistics on synthetic content units

### Phase 2: First Normalizer (proves the architecture)

Build whichever normalizer has the best test data available. Currently the Shamela fixture exists (`tests/fixtures/shamela_ibn_aqil.htm`), so Shamela is a reasonable first choice — but the architecture does not depend on this choice.

**Step 6: Shamela normalizer (or whichever format has test data)**
- Implement `src/normalizers/shamela.py` following SPEC §4.A.2
- Register in dispatcher
- Test: end-to-end from fixture → validated normalized package

### Phase 3: Additional Normalizers (one at a time)

Each new normalizer follows the same pattern: implement the `BaseNormalizer` interface, register in dispatcher, test end-to-end.

Priority order (based on likely source availability):
1. PDF (text-embedded) — using Docling
2. Plain text — simplest normalizer
3. Image scan — using QARI-OCR / Mistral OCR
4. Word document — using Docling
5. EPUB
6. Owner-authored content

---

## Test Strategy

Tests are organized in two layers:

**Layer 1: Format-agnostic tests** (test_validation.py, test_writer.py, test_dispatcher.py)
- These test the shared infrastructure with synthetic data
- They pass regardless of which normalizers are implemented

**Layer 2: Per-normalizer tests** (test_shamela.py, test_pdf.py, etc.)
- These test specific normalizers with format-specific fixtures
- Each normalizer's tests verify: input validation, content extraction, layer detection, structure discovery, output schema compliance

Gold baselines are created per fixture: run the normalizer, verify output manually, save as expected output.

---

## Constraints

- **D-019:** ABD code has zero design authority. Do not copy or adapt ABD code. Build from the SPEC.
- **D-023:** All upstream metadata passes through. The normalized package includes ALL source metadata fields.
- **Normalization boundary:** No format-specific logic exists below this engine. The normalized package is the contract.
- **Text integrity:** Primary text bytes are never modified after extraction. Normalization transforms format, not content.
