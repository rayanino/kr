# Normalization Engine — محرك التطبيع

**Purpose:** Transform frozen source files into the universal normalized format. One normalizer per source type. Guardian of the normalization boundary — the last engine to touch format-specific data.

**Phase:** 1 (source-format-specific, above the normalization boundary).

**Core scope:** Shamela HTML + Plain Text normalizers. Multi-layer detection (typographic). Structure discovery (4-tier). Page boundary preservation. Diacritics preservation. Cross-page boundary continuity. Content flagging. §5 validation checks 1–10.

---

## Governing Documents (read order for new sessions)

1. **This file** — orientation (<200 lines)
2. **`SPEC.md`** (2,049L) — Behavioral authority. §4.A is core (PRECISION/HARDENED — do not rewrite). §4.B is mostly deferred (see CORE_EXTRACTION.md).
3. **`contracts.py`** — Schema authority. Pydantic models for the normalized package.
4. **`CORE_EXTRACTION.md`** — Which §4 capabilities are core vs deferred, with rationale.
5. **`MUSTFIX_RESOLUTIONS.md`** — MF-1 (DivisionNode 9-field) and MF-2 (LayerMapEntry rename) designs.
6. **`reference/SPEC_INTEGRITY_AUDIT_NORMALIZATION.md`** — 22 applied SPEC fixes, 3 MUST-FIX, 9 SHOULD-FIX.
7. **`reference/SPEC_ADVERSARY_NORMALIZATION.md`** (51 cases) — Adversarial test catalog. ~47 cases are core.
8. **`engines/source/contracts.py`** — Upstream boundary. `SourceMetadata` is the input.
9. **`engines/passaging/contracts.py`** — Downstream boundary. Passaging reads the normalized package.
10. **`reference/ENGINE_BUILD_BLUEPRINT.md`** §2 — Build procedure.

## Architecture

```
Input:  frozen source files + SourceMetadata (from source engine)
        ↓
        dispatcher.py (§4.A.1) — routes by source_format
        ↓
        normalizers/shamela.py (§4.A.2)     ← core, 6 passes
        normalizers/plain_text.py (§4.A.4c)  ← core, simple
        ↓
Output: manifest.json + content.jsonl (normalized package)
```

### Module Map

| Module | SPEC | What It Does |
|--------|------|-------------|
| `src/dispatcher.py` | §4.A.1 | Routes `source_format` → normalizer. Extensible registry. |
| `src/normalizers/base.py` | §4.A.1 | Abstract interface: `normalize()` + `validate_input()` |
| `src/normalizers/shamela.py` | §4.A.2 | 6-pass pipeline (parse → footnotes → clean → structure → layers → assemble) |
| `src/normalizers/plain_text.py` | §4.A.4c | Paragraph splitting, keyword structure, no HTML |
| `src/structure_discovery.py` | §4.A.6 | 4-tier heading detection, division tree construction |
| `src/layer_detector.py` | §4.A.5 | Typographic layer detection (bold, brackets, transition phrases) |
| `src/boundary_continuity.py` | §4.B.8 | Page boundary continuity signals (mid_sentence → division_break) |
| `src/content_flagger.py` | §4.A.9 | Boolean content flags per page |
| `src/validation.py` | §5 | Self-validation checks 1–10 |
| `src/writer.py` | §4.A.2 | Atomic write (temp dir → rename → cleanup) |
| `src/errors.py` | §7 | Error codes, severities, structured logging |
| `prompts/` | §4.A.6 Tier 3 | LLM prompt templates for structure discovery |

### Deferred Modules (not built, not stubbed beyond current state)

`content_census.py` (§4.B.5), fine-grained footnote classifier (§4.B.4), OCR normalizers (§4.A.4), discourse flow (§4.B.10), fingerprints (§4.B.9), tahqiq topology (§4.B.7).

## Key Contract Details

**Output: Normalized Package** = `manifest.json` + `content.jsonl`

- `manifest.json` → `NormalizedManifest` in contracts.py. Key fields: `source_id`, `division_tree` (array of `DivisionNode`), `layer_map`, `structural_format`, `total_content_units`, `quality_report`. Optional deferred fields: `content_census`, `tahqiq_topology`, `layer_fingerprints`, `discourse_flow_summary` — all `None` in core build.
- `content.jsonl` → one `ContentUnit` per physical page. Key fields: `unit_index` (authoritative position), `primary_text` (diacritics preserved), `text_layers`, `footnotes`, `structural_markers`, `content_flags`, `text_fidelity`, `boundary_continuity` (§4.B.8, core). Optional deferred: `discourse_flow` — `None` in core build.

**Input:** `SourceMetadata` from source engine. Key fields consumed: `source_id`, `source_format`, `work_id`, `text_fidelity`, `structural_format`, `is_multi_layer`, `genre`, `page_count`, `volume_count`.

## Reference Code

ABD-era code in `reference/archive/abd_code/normalization/`:
- `normalize_shamela.py` (1,123L) — Shamela normalizer baseline for Passes 1–3
- `discover_structure.py` (2,896L) — 4-tier structure discovery
- `validate_structure.py` (333L) — Structure validation
- `reference/structural_patterns.yaml` (340L) — Arabic heading keyword patterns (loaded with PyYAML)
- `reference/ABD_NORMALIZATION_SPEC.md` — v0.5 normalization specification

The ABD code is REFERENCE, not implementation. Build fresh code that matches SPEC.md, using ABD code for behavioral insight on Shamela HTML quirks.

## Build Session Plan

| Session | Focus | Key SPEC Sections | Status |
|---------|-------|--------------------|--------|
| 1 | Contracts alignment (MF-1, MF-2) + complete error codes | contracts.py, errors.py, §7 | ✅ Done |
| 2 | Shamela Passes 1–3 (HTML parse → footnotes → clean) | §4.A.2 Passes 1–3 | ✅ Done |
| 3 | Structure discovery (4-tier headings, division tree) | §4.A.6, structural_patterns.yaml | ✅ Done |
| 4 | Layer detection (typographic signals for Shamela) | §4.A.5 |  |
| 5 | Pass 6 assembly (boundary continuity, flagging, output) | §4.B.8, §4.A.9, §4.A.2 Pass 6 |  |
| 6 | Validation + writer + plain text normalizer | §5 checks 1–10, §4.A.4c |  |
| 7 | Integration testing on fixtures | Full pipeline, adversarial cases |  |

**Build metrics after Session 3:** 3,266 impl lines, 1,919 test lines, 125 tests passing, 13/51 ADV covered (ADV-001–010 + ADV-016–018). Known limitations: L-001 (bare-number footnotes), L-002 (ضياء السالك collision), L-003 (same-page heading chaining).

## Critical Rules

1. **Diacritics are sacred.** No Unicode normalization (NFC/NFD/NFKC/NFKD) on Arabic text. Every diacritical mark preserved exactly. §5 check 8 verifies this.
2. **Never lose data silently.** Every error has a §7 code. Log everything. Fail loud.
3. **unit_index is the authority.** Not page numbers. 29.8% of Shamela has duplicate/non-sequential page numbers.
4. **Layer misattribution is the worst failure.** Attributing text to the wrong author means the owner studies a text believing the wrong person wrote it.
5. **Normalization boundary test:** If adding a new source type requires changing ANY Phase 2 engine, the boundary is violated.
6. **D-023:** Never delete upstream metadata. Pass through everything via `source_id` reference.
7. **Atomic writes only.** No partial packages visible to downstream engines. Temp dir → verify → rename.

## Test Fixtures Available

- `tests/fixtures/shamela_real/` — 11 real Shamela books (nahw, fiqh, hadith, tafsir, usul, balagha, edge cases)
- `engines/normalization/tests/fixtures/shamela_ibn_aqil.htm` — Multi-layer commentary fixture
- `reference/SPEC_ADVERSARY_NORMALIZATION.md` — 51 adversarial test cases (~47 core)
