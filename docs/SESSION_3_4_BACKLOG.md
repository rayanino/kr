# Environment Overhaul — Sessions 3 & 4 Backlog

Deferred items from the environment overhaul roadmap. Each item has a **trigger condition** — implement when the trigger fires, not before.

## Session 3: External Integrations

### 3.1 Usul.ai Scholar Verification

- **What:** API client or web scraping wrapper for Usul.ai's 15,000+ scholar database. Automates death-date and attribution verification.
- **Why:** T-2 (Attribution Error), T-5 (Temporal Corruption). Currently verified manually via `/research` command.
- **Trigger:** LLM evaluation shows death-date or author attribution errors in >20% of evaluated books.
- **Depends on:** Real Phase C/D evaluation results showing which scholars are misidentified.
- **Effort:** ~2-3 hours (API client + caching + skill integration)
- **Current state:** Referenced in `/research` command and `verifier-b` agent. No code.

### 3.2 Sunnah.com Hadith Lookup

- **What:** API wrapper for sunnah.com hadith collection metadata. Enables automated hadith reference verification.
- **Why:** Hadith evidence references in excerpting need cross-validation. Currently manual.
- **Trigger:** Excerpting evaluation on hadith-heavy texts (taysir, ext_46_qa) shows systematically wrong hadith references.
- **Depends on:** Real excerpting results from hadith-heavy test packages.
- **Effort:** ~2-3 hours (API client + hadith matching logic + skill)
- **Current state:** Listed in RESOURCES.md as "future." No code.

### 3.3 Evaluation Batch Runner

- **What:** Script that runs evaluation across multiple books/packages with progress tracking, cost accumulation, and result aggregation.
- **Why:** Currently `run_integration_test.py` handles one package at a time. Batch runs need orchestration.
- **Trigger:** First successful single-package LLM run completes and you want to scale to all 5 packages.
- **Depends on:** Working `--real` mode in integration test script.
- **Effort:** ~1-2 hours (wrapper around existing script + aggregation)
- **Current state:** `run_integration_test.py` handles single packages. No batch orchestration.

### 3.4 Fixture Quality Scoring

- **What:** Automated quality assessment of test fixtures using the arabic-text-quality skill patterns (OCR corruption detection, encoding artifacts, diacritic quality grading A-D).
- **Why:** Bad fixtures produce misleading evaluation results. Quality should be scored before evaluation.
- **Trigger:** Always useful, but especially when adding new fixtures or questioning evaluation results.
- **Depends on:** arabic-text-quality skill (already exists).
- **Effort:** ~2 hours (script applying skill patterns programmatically)
- **Current state:** `scripts/validate_shamela_fixtures.py` exists but checks structure, not text quality.

## Session 4: Advanced Capabilities

### 4.1 Automated Hallucination Detector

- **What:** Pattern-based detector for common LLM hallucination types in Islamic scholarly metadata: invented precision (century→specific year), fabricated scholars, wrong school attribution.
- **Why:** T-2, T-5. The Decision Playbook documents 3 specific hallucination patterns (ERR-03) but detection is manual.
- **Trigger:** Evaluation corpus of 5+ books reveals repeating hallucination patterns across multiple outputs.
- **Depends on:** Corpus of known hallucinations from real LLM evaluation (need examples to calibrate).
- **Effort:** ~3-4 hours (pattern library + detection logic + integration with consensus validation)
- **Current state:** Patterns documented in DECISION_PLAYBOOK.md §2.2 but not automated.

### 4.2 Scholar Authority Heuristics Enhancement

- **What:** Improvements to `shared/scholar_authority/` based on real evaluation data — name disambiguation improvements, death-date validation against multiple sources, confidence scoring based on scholar prominence.
- **Why:** Phase C showed 70% gate_abort rate from sparse scholar registry → 0% after populating science_scope.
- **Trigger:** Gate abort rate >30% in Phase D/E evaluation due to missing scholar data.
- **Depends on:** Real Phase D/E gate abort patterns showing which scholars cause problems.
- **Effort:** ~3-4 hours (heuristic rules + testing against known scholars)
- **Current state:** `shared/scholar_authority/name_matching.py` and `scholar_authority.py` exist with tests. Foundation is solid.

### 4.3 Arabic Semantic Embeddings

- **What:** Arabic name/text similarity embeddings for semantic deduplication beyond token matching. Potentially using CAMeL Tools (NYU/MIT).
- **Why:** Taxonomy engine will need semantic dedup. Scholar name matching currently uses string similarity.
- **Trigger:** Taxonomy engine work begins OR scholar matching shows >10% false negatives from string-only matching.
- **Depends on:** Not relevant until taxonomy engine starts. Lowest priority.
- **Effort:** ~4-6 hours (library survey + integration + testing)
- **Current state:** CAMeL Tools mentioned in technology survey. No implementation.

### 4.4 Tier 1 LLM Trustworthiness Defenses

- **What:** Deterministic defense implementations from `engines/excerpting/docs/llm_trustworthiness_defenses.md`:
  - 1A: Dangling reference detector (back-reference patterns كما تقدم, سيأتي)
  - 1B: School cross-check (madhab attribution vs source metadata)
  - 1C: Quran canonical lookup (verify citations against Uthmani text)
  - 2A: Targeted consensus question (self-containment verification)
- **Why:** These are deterministic checks that catch specific LLM failure modes.
- **Trigger:** First real LLM evaluation completes. These defenses are designed to catch the failure modes that evaluation reveals.
- **Depends on:** Empirical scans (defined in llm_trustworthiness_defenses.md) to determine which defenses are worth building.
- **Effort:** 1B ~30 lines, 1C ~150 lines, 2A ~20 lines, 1A ~80-150 lines
- **Current state:** Fully designed. Empirical scans not yet run.

## Priority Order (post-first-LLM-call)

1. **4.4** Tier 1 defenses — directly improve pipeline quality
2. **3.1** Usul.ai — if attribution errors found
3. **4.1** Hallucination detector — if patterns emerge
4. **3.3** Batch runner — when scaling beyond 1 package
5. **4.2** Scholar heuristics — if gate aborts recur
6. **3.4** Fixture quality — before adding new fixtures
7. **3.2** Sunnah.com — if hadith errors found
8. **4.3** Arabic embeddings — taxonomy engine phase
