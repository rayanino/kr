# Atomization Engine — Implementation Order

Build plan for Claude Code. Each phase depends on the previous.
Build §4.A (core processing) first, then §4.B (transformative) incrementally.

---

## Phase 0: Foundation (no SPEC logic — infrastructure only)

**Build first. Everything depends on these.**

1. **errors.py** — Error classes, structured logging to atomization_log.jsonl. Uses contracts.py AtomizationErrorCode enum (22 codes) and ERROR_SEVERITY map.
2. **config.py** — Configuration loading from AtomizationConfig defaults. Per-science override loading can be stubbed initially.
3. **loader.py** — Read passages.jsonl. Parse into passage records using passaging contracts. Implement all 5 input validation checks (§2). NFC normalization safety net (step 5). This is the most testable module — build tests alongside.

**Test gate:** loader.py passes all 5 validation checks on test fixtures. Invalid passages produce ATOM_INVALID_INPUT. NFC normalization detected and applied when needed.

---

## Phase 1: Pre-Processing (§4.A.1 phases 1–2)

4. **prescreen.py** — Phase 1: strategy selection based on structural_format, model selection based on text_fidelity, confidence adjustment for low-fidelity text.
5. **predetection.py** — Phase 2: rule-based pattern scanning. Implement in this order:
   - Footnote marker detection (⌜N⌝ pattern — simplest)
   - Quran fragment detection (Quran_Detector library + ﴿...﴾ brackets)
   - Hadith evidence marker detection (lexicon-based)
   - Isnad chain pattern detection
   - Poetry marker detection

**Test gate:** Pre-detection correctly identifies Quran citations, hadith markers, and footnote references in gold passages. Confidence values are in expected ranges.

---

## Phase 2: LLM Atomization (§4.A.5)

6. **llm_atomizer.py** — Phase 3: LLM-driven boundary detection and classification. Implement in this order:
   - Prompt construction with atom boundary rules and type taxonomy
   - Instructor integration for structured output
   - Few-shot example loading from gold baselines
   - Pre-detection hint injection as constraints
   - Schema violation retry logic
7. **format_strategies/prose.py** — Default prose strategy (most exercised path)

**Test gate:** LLM atomization produces valid atom objects for gold prose passages. Schema violations trigger retries. Pre-detection constraints are respected.

---

## Phase 3: Post-Processing (§4.A.1 phase 4, §4.A.8)

**The most critical deterministic logic — offset integrity is the core invariant.**

8. **postprocessor.py** — Implement in this order:
   - Offset verification and correction (§4.A.8) ← hardest sub-module
   - Coverage enforcement (gap filling, overlap resolution)
   - Atom_id assignment (globally monotonic)
   - Atom density check (V-9/ADV-12)
   - Attribution marker verification (ADV-3)
   - Orphaned footnote marker detection (ADV-8)
   - Evidence type conflict detection (ADV-5)
9. **layer_attribution.py** — Multi-layer attribution (§4.A.6)
10. **footnote_atomizer.py** — Footnote atomization (§4.A.9)

**Test gate:** Offset correction finds matches for common drift patterns (§10.10). Coverage enforcement fills gaps with synthetic atoms. Layer attribution correctly handles multi-layer passages and boundary-spanning atoms.

---

## Phase 4: Validation and Emission (§4.A.10, output)

11. **validator.py** — All 9 self-validation checks. Implement fatal checks first (V-1 coverage, V-2 offset integrity), then warning checks (V-3 through V-9).
12. **emitter.py** — JSONL serialization, source status update, secondary artifact stubs.

**Test gate:** V-1 and V-2 catch all synthetic test violations. End-to-end: loader → prescreen → predetection → LLM → postprocess → validate → emit succeeds on gold prose passage.

---

## Phase 5: Engine Orchestrator

13. **engine.py** — Wire together all five phases. Handle fatal errors (skip passage, log, continue). Handle retries (up to max_retries_per_passage with error feedback). Handle source-level checks (unclassified rate, review flag rate).

**Test gate:** `process_source(source_id)` succeeds end-to-end on a prose test fixture. Output validates against AtomRecord schema. atomization_log.jsonl records all warnings.

---

## Phase 6: Remaining Format Strategies (§4.A.7)

Build in order of available test data:

14. **format_strategies/verse.py** — Test with alfiyyah_versified fixture (§10.23)
15. **format_strategies/commentary.py** — Test with ibn_aqil fixture (§10.17, §10.24)
16. **format_strategies/masala.py** — Test with mughni_comparative fixture (§10.26)
17. **format_strategies/qa.py** — Needs Q&A test fixture (stub if unavailable)
18. **format_strategies/dictionary.py** — Needs dictionary test fixture (stub if unavailable)
19. Update **prescreen.py** to route all format types.

**Test gate:** Each strategy produces valid atoms on its test fixture. Verse strategy trusts verse_info over LLM (§10.23). Commentary strategy detects suspicious single-layer distribution (§10.24).

---

## Phase 7: §4.B Capabilities (incremental, gated by feature flags)

Build in dependency order:

20. **fingerprinting.py** — §4.B.5 Tier 1 (text hash, deterministic) + Tier 2 (key terms, LLM). Tier 3 (embeddings) deferred until GPU available. (§10.12, §10.13)
21. **distribution_analytics.py** — §4.B.3. Per-passage and per-source statistics. (§10.26 integration)
22. **attribution_detection.py** — §4.B.4. Integrated into LLM prompt. (§10.11)
23. **concordance.py** — §4.B.7. Extracts from definition atoms. (§10.27, §10.28)
24. **evidence_quality.py** — §4.B.8. Lexicon-based + LLM verification. (§10.29, §10.30)
25. **rhetorical_analysis.py** — §4.B.1. Pattern detection for completeness scoring. (§10.26)
26. **completeness_scoring.py** — §4.B.6. Depends on §4.B.1. (§10.26)
27. **implicit_layers.py** — §4.B.2. Deferred — needs multi-layer gold data.

**Test gate:** Fingerprint hash is deterministic across diacritical variants (§10.12). Attribution detection finds named scholars, isnad chains, and school attributions (§10.11). Concordance extraction produces correct defined_term (§10.27). Evidence quality signals detected from lexicon phrases (§10.29).

---

## Dependencies Between Modules

```
loader.py ──────► prescreen.py ──────► predetection.py ──────► llm_atomizer.py
    │                  │                      │                       │
    │                  │                      │              format_strategies/*.py
    │                  │                      │                       │
    │                  │                      │               postprocessor.py
    │                  │                      │                  │    │    │
    │                  │                      │    layer_attribution  │  footnote_atomizer
    │                  │                      │                       │
errors.py ◄── (all)   │                      │               validator.py
config.py ◄── (all)   │                      │                       │
                       │                      │               emitter.py
                       │                      │                  │
                  engine.py ◄──────── (orchestrates all) ────────┘
                       │
              §4.B modules (feature-flagged):
              fingerprinting.py, distribution_analytics.py,
              attribution_detection.py, concordance.py,
              evidence_quality.py, rhetorical_analysis.py,
              completeness_scoring.py, implicit_layers.py
```

---

## External Dependencies

- **Instructor** (Python): Structured LLM output. Needed from Phase 2 (LLM atomization).
- **Quran_Detector** (GitHub): Quran fragment detection. Needed from Phase 1 (predetection.py).
- **CAMeL Tools** (NYU): Arabic text normalization. Needed from Phase 1 (predetection.py offset matching) and Phase 7 (fingerprinting.py).
- **LiteLLM / OpenRouter / Anthropic API**: LLM providers. Needed from Phase 2.
- **DSPy** (Stanford): Optional prompt optimization against gold baselines. Deferred.
- **Arabic embedding model**: Needed only for §4.B.5 Tier 3 (deferred until GPU available).
