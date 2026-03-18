# Normalization Engine — Core vs Deferred Classification

**Date:** 2026-03-18
**Classifier:** Architect (Claude Chat)
**Input:** `engines/normalization/SPEC.md` (2,049 lines), `engines/passaging/SPEC.md` §2, `engines/passaging/contracts.py`
**Method:** kr-core-extract skill. Each capability tested against: (1) "Would the engine still fulfill its purpose without this?" (2) "Does the passaging engine require this capability's output?" Verified every downstream field reference against actual contracts.

---

## §4.A — Core Processing

| # | Capability | Classification | Reason |
|---|-----------|---------------|--------|
| §4.A.1 | Normalizer Architecture (dispatcher pattern) | **CORE** | Engine structural backbone. Without it, no source is processed. |
| §4.A.2 | Shamela Normalizer (6-pass pipeline) | **CORE** | Primary test format. ~2,500 test books. The core build target. |
| §4.A.3 | PDF Normalizer (text-embedded) | DEFERRED | No PDF sources in test collection. Depends on PyMuPDF + python-bidi. |
| §4.A.4 | Scanned PDF & Image Normalizer | DEFERRED | Requires OCR infrastructure (Mistral API, QARI-OCR). No scanned sources. |
| §4.A.4a | EPUB Normalizer | DEFERRED | Behavioral outline only. No EPUB sources. |
| §4.A.4b | Word Document Normalizer | DEFERRED | Behavioral outline only. No Word sources. |
| §4.A.4c | Plain Text Normalizer | **CORE** | Second core format. Validates source-agnosticism of output schema. Low implementation cost. |
| §4.A.4d | Owner Content Normalizer | DEFERRED | Distinct input type with special handling. Not needed until owner adds notes. |
| §4.A.5 | Multi-Layer Text Detection (typographic) | **CORE** | Every downstream engine depends on knowing which layer text belongs to. Layer misattribution is the highest-integrity-risk operation. |
| §4.A.6 | Structure Discovery (4-tier confidence) | **CORE** | Passaging engine §2 reads `division_tree` as "primary boundary guidance signal." |
| §4.A.7 | Page Boundary Preservation | **CORE** | Scholars cite by volume/page. Breaking this chain breaks citation traceability. |
| §4.A.8 | Diacritics and Arabic Text Handling | **CORE** | Diacritics preservation is the #1 text fidelity invariant. Destruction is irreversible. |
| §4.A.9 | Content Flagging | **CORE** | Passaging reads `content_flags` to determine digestibility (excluding TOC/index/blank). Low cost. |

## §4.B — Transformative Capabilities

| # | Capability | Classification | Reason |
|---|-----------|---------------|--------|
| §4.B.1 | Scholarly Text Layer Intelligence (content-based inference) | DEFERRED | Extends §4.A.5 for sources WITHOUT typographic markers. §4.A.5 handles Shamela commentary exports (bold, brackets, transition phrases). Content-based inference needs LLM prompt engineering + per-source bootstrapping. |
| §4.B.2 | Structural Format — manifest field | **CORE** | Passaging §2 line 29 reads `structural_format` to select strategy. Core: pass through from source engine metadata into manifest. |
| §4.B.2 | Structural Format — auto-detection override | DEFERRED | The 20-page content analysis that proposes format overrides. Source engine's classification is authoritative until human gate resolves disagreements. `structural_format_proposed` manifest field is the extension hook. |
| §4.B.3 | Fine-Grained Text Fidelity Mapping | DEFERRED | Character-level fidelity with semantic confusion tracking. OCR-specific — Shamela sources default to `text_fidelity: "high"`. |
| §4.B.4 | Footnote Apparatus Classification (fine-grained) | DEFERRED | §4.A.2 Pass 2 already does COARSE classification (tahqiq_editor/author_original/unknown). The 7 fine-grained sub-types with structured data extraction (variant_data, takhrij_data, etc.) are enrichment. Passaging does not consume fine-grained footnote types. |
| §4.B.5 | Content Census | DEFERRED | Passaging §2 line 34: "If absent, the passaging engine uses default configuration values." Explicit graceful-absence path. |
| §4.B.6 | Adaptive Multi-Engine OCR Orchestration | DEFERRED | OCR-specific. No scanned sources. Depends on 4 external OCR engines. |
| §4.B.7 | Tahqiq Apparatus Topology | DEFERRED | Passaging §2 line 35: "If absent, this metadata is simply not emitted." Depends on §4.B.4 fine-grained classification. |
| §4.B.8 | Cross-Page Continuity Intelligence | **CORE** | All of §4.B.8 — including `mid_argument` detection. Pure pattern matching with zero external dependencies. The passaging engine uses `boundary_continuity` as a primary signal for text assembly (§4.A.2) and treats `mid_argument` with confidence ≥0.7 as non-fracturable (§2 line 40). Continuity signals are format-specific and lost after normalization — this is the only opportunity to capture them. Implementation: ~50-80 lines of pattern matching. |
| §4.B.9 | Authorial Voice Fingerprint | DEFERRED | Statistical validation layer on top of §4.A.5. `layer_fingerprints` is `Optional` — passaging works without it. |
| §4.B.10 | Scholarly Discourse Flow Annotation | DEFERRED | High implementation cost (LLM per page, 16-type taxonomy, per-science calibration). Passaging has its own keyword fallback (§4.B.6). `discourse_flow` is `Optional`. |

## Summary

- **Core capabilities: 13** (§4.A.1–§4.A.9 including §4.A.4c, §4.B.2 manifest field, §4.B.8 full)
- **Deferred capabilities: 11** (§4.A.3, §4.A.4, §4.A.4a-b, §4.A.4d, §4.B.1, §4.B.2 auto-detection, §4.B.3–§4.B.7, §4.B.9–§4.B.10)
- **Core input formats:** `shamela_html`, `plain_text`
- **Deferred input formats:** `pdf_text`, `pdf_scanned`, `image_scan`, `epub`, `word_doc`, `owner_authored`
- **Core §5 checks:** 1–10 (deferred: 11–14)
- **Pre-build MUST-FIX:** MF-1 (DivisionNode), MF-2 (LayerMapEntry). MF-3 deferred (OCR-only).

## Extension Hooks

| Deferred Capability | Core Must Not Assume |
|---------------------|---------------------|
| §4.A.3–§4.A.4d Normalizers | Dispatcher type map must be extensible. No hardcoded normalizer list. `LayerType` enum must accept `OWNER_CONTENT`. |
| §4.B.1 Content-based layers | §4.A.5 `detection_method` distinguishes how layers were detected. Confidence thresholds configurable. |
| §4.B.2 Auto-detection logic | `structural_format_proposed` manifest field exists (`Optional`). Human gate interface defined. |
| §4.B.3 Fine-grained fidelity | `TextFidelity` model accepts optional additional fields. |
| §4.B.4 Fine-grained footnotes | `FootnoteType` enum already contains fine types. Structured data fields already `Optional` on `Footnote`. Core uses coarse types only. |
| §4.B.5 Content census | `NormalizedManifest.content_census` is `Optional[ContentCensus]`. Core leaves it `None`. |
| §4.B.6 OCR orchestration | Contained within deferred normalizers. |
| §4.B.7 Tahqiq topology | `NormalizedManifest.tahqiq_topology` is `Optional[TahqiqTopology]`. Core leaves it `None`. |
| §4.B.9 Layer fingerprints | `NormalizedManifest.layer_fingerprints` is `Optional`. Core leaves it `None`. |
| §4.B.10 Discourse flow | `ContentUnit.discourse_flow` is `Optional`. Core leaves it `None`. |
