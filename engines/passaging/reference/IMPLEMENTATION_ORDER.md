# Passaging Engine — Implementation Order

Build plan for Claude Code. Each phase depends on the previous.
Build §4.A (core processing) first, then §4.B (transformative) incrementally.

---

## Phase 0: Foundation (no SPEC logic — infrastructure only)

**Build first. Everything depends on these.**

1. **errors.py** — Error classes, logging utilities. Uses contracts.py error codes and severity map.
2. **config.py** — Configuration loading from PassagingConfig defaults. Per-science override loading can be stubbed initially.
3. **loader.py** — Read manifest.json + content.jsonl. Parse into NormalizedManifest + list[ContentUnit] using normalization contracts. Implement all 6 input validation checks (§2). This is the most testable module — build tests alongside.

**Test gate:** loader.py passes all 6 validation checks on test fixtures. Fatal errors raise PassagingFatalError. Warnings are collected and returned.

---

## Phase 1: Text Assembly (§4.A.2)

**The hardest core module. Arabic text joining requires extreme care.**

4. **assembly.py** — Cross-page text assembly. Implement in this order:
   - Basic joining (concatenate content unit texts with space)
   - Boundary continuity integration (use signals when present)
   - Character-level heuristics (final-form Arabic letter detection as fallback)
   - Footnote renumbering (sequential from 1 per passage)
   - Text layer rebasing (offsets relative to assembled text)
   - Quran citation bracket handling (﴿...﴾ must stay intact)
   - Tanwin boundary handling (word ending with tanwin must NOT join with next word)

**Test gate:** All 12 §10.1 assembly test cases pass. Character count invariant holds.

---

## Phase 2: Prose Strategy (§4.A.4)

**The default strategy and the most exercised code path.**

5. **strategies/prose.py** — Three-step prose passaging:
   - Step 1: Division tree evaluation (classify divisions by size: merge/direct/split)
   - Step 2: Boundary refinement using boundary_continuity signals
   - Step 3: Splitting — paragraph-based first, LLM-assisted above llm_splitting_threshold
   - Sentence integrity enforcement (no mid-sentence boundaries)
   - Isnad chain preservation
6. **strategy.py** — Strategy selection. Initially maps `prose` → ProseStrategy only. Other formats fall back to prose with PSG_FORMAT_DETECTION_FAILED.

**Test gate:** §10.2 prose sizing tests pass. Sentence integrity verified (§10.6).

---

## Phase 3: Emission and Validation (§4.A.10)

7. **emitter.py** — Passage record assembly, predecessor/successor linking, JSONL serialization, source status update.
8. **validator.py** — All 11 self-validation checks. Implement fatal checks first (#1, #2, #4b, #5, #9, #10), then warning checks (#3, #6, #7, #8, #11).

**Test gate:** §10.5 self-validation tests pass. End-to-end: loader → assembly → prose → emission → validation succeeds on ibn_aqil test fixture.

---

## Phase 4: Engine Orchestrator

9. **engine.py** — Wire together loader → assembly → strategy → emission → validation into the six-phase pipeline. Handle fatal errors (abort + log). Handle warnings (collect + continue).

**Test gate:** `process_source(source_id)` succeeds end-to-end on a prose test fixture. Output validates against PassageRecord schema.

---

## Phase 5: Remaining Format Strategies (§4.A.5–§4.A.9)

Build in order of available test data:

10. **strategies/verse.py** — Verse strategy. Test with alfiyyah_versified fixture. (§10.3)
11. **strategies/masala.py** — Masala-block strategy. Test with mughni_comparative fixture. (§10.4)
12. **strategies/qa.py** — Q&A pair strategy. Needs Q&A test fixture (stub if unavailable).
13. **strategies/commentary.py** — Commentary-unit strategy. Test with ibn_aqil (sharh + matn). (§10.4)
14. **strategies/dictionary.py** — Dictionary entry strategy. Needs dictionary test fixture (stub if unavailable).
15. Update **strategy.py** to route all format types.

**Test gate:** §10.4 format selection tests pass. Each strategy produces valid passages on its test fixture.

---

## Phase 6: §4.B Capabilities (incremental, gated by feature flags)

Build in dependency order:

16. **adaptive_passaging.py** — §4.B.5. Content census adaptation. Only needs config + content_census. (§10.8)
17. **arguments.py** — §4.B.6. Argument detection. Keyword state machine first (fallback), then discourse_flow integration (primary). (§10.9)
18. **discourse_optimization.py** — §4.B.7. Boundary optimization. Depends on discourse_flow. (§10.10)
19. **completeness_forecast.py** — §4.B.8. Completeness forecast + corrective merges. Depends on discourse_flow. (§10.11)
20. **quality_prediction.py** — §4.B.1. Needs sentence embedding model (multilingual-e5-large or Swan-Large). (Deferred)
21. **implicit_structure.py** — §4.B.2. Needs LLM + embedding model. (Deferred)
22. **commentary_alignment.py** — §4.B.3. Needs layer analysis + LLM. (Deferred)
23. **cross_edition.py** — §4.B.4. Needs multiple editions in library. (Deferred)

**Test gate:** §10.8–§10.11 test cases pass for capabilities 16–19.

---

## Dependencies Between Modules

```
loader.py ──────────────► assembly.py ──────► strategy.py ──────► emitter.py ──► validator.py
    │                         │                    │                    │
    │                         │                    ├── strategies/*.py  │
    │                         │                    │                    │
errors.py ◄─── (all modules)  │               arguments.py            │
config.py ◄─── (all modules)  │               discourse_optimization  │
                               │               completeness_forecast   │
                               │               adaptive_passaging      │
                               │                                       │
                          engine.py ◄──────── (orchestrates all) ──────┘
```

---

## External Dependencies

- **LLM API** (via LiteLLM/Instructor): Used in prose semantic splitting (Phase 2), implicit structure discovery (Phase 6). Not needed until Phase 2 Step 3.
- **Sentence embeddings** (multilingual-e5-large or Swan-Large): Used in quality prediction, implicit structure. Not needed until Phase 6 item 20.
- **CAMeL Tools**: Arabic morphological analysis. Used for technical term identification. Not needed until Phase 6 item 16.
- **PyArabic**: Arabic text utilities. May be useful for character analysis in assembly.py (Phase 1).
