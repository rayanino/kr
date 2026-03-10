# Source Engine Testing Protocol — Post-Build Validation

**Status:** BASE PLAN — refine after Session 6 with real engine output
**Budget ceiling:** €80-100 total API credits across all phases
**Principle:** Every euro spent must produce saved, reviewable results. No run without a saved artifact.

---

## Result Format: One File Per Book

Every book that passes through the engine produces a self-contained result file at `tests/results/source_engine/{source_id}.json`. This file is the unit of review — the owner brings 3-5 of these per Claude Chat session for evaluation.

```json
{
  "source_id": "src_a7c3e91f",
  "fixture_path": "tests/fixtures/shamela_real/01_nahw_simple/book.htm",
  "run_timestamp": "2026-03-12T14:30:00Z",
  "run_phase": "C",
  "run_cost_usd": 0.08,

  "extraction": {
    "title_arabic": "أخبار أبي القاسم الزجاجي",
    "author_name_raw": "أبو القاسم عبد الرحمن بن إسحاق الزجاجي (ت 337هـ)",
    "publisher": null,
    "muhaqiq_name_raw": null,
    "page_count": 45,
    "quality_issues": []
  },

  "inference": {
    "genre": "adab",
    "genre_confidence": 0.88,
    "author_identification": {
      "canonical_name_ar": "أبو القاسم الزجاجي",
      "death_date_hijri": 337
    },
    "author_confidence": 0.92,
    "science_scope": ["adab"],
    "is_multi_layer": false,
    "attribution_status": "definitive",
    "model_a": {"model": "cohere/command-a", "raw_genre": "adab", "raw_author": "..."},
    "model_b": {"model": "anthropic/claude-opus-4-6", "raw_genre": "adab", "raw_author": "..."},
    "consensus_agreed": true,
    "scholarly_context_summary": "3rd century AH grammarian..."
  },

  "trust": {
    "tier": "verified",
    "score": 0.693,
    "factors": [
      {"name": "author_standing", "score": 0.90, "reason": "Classical (d. 337 AH)"},
      {"name": "tahqiq_quality", "score": 0.40, "reason": "No muhaqiq, pre-modern"},
      {"name": "publisher_reputation", "score": 0.40, "reason": "Unknown publisher"},
      {"name": "source_authority", "score": 0.85, "reason": "Primary source"},
      {"name": "text_fidelity", "score": 0.90, "reason": "High (shamela)"}
    ]
  },

  "registration": {
    "scholar_action": "new_record",
    "scholar_canonical_id": "sch_00001",
    "work_id": "wrk_zajjaji_akhbar",
    "relationships": [],
    "human_gates_created": []
  },

  "validation": {
    "errors": [],
    "warnings": [],
    "needs_review_fields": []
  },

  "ground_truth": {
    "expected_genre": "adab",
    "expected_trust": "verified",
    "genre_match": true,
    "trust_match": true,
    "author_match": true
  }
}
```

**Why this format:** Every section maps to one pipeline step. The owner can scan `ground_truth` for pass/fail, then drill into whichever section has a mismatch. The `model_a` / `model_b` raw outputs let us debug consensus disagreements without re-running. The `run_cost_usd` tracks spend per book.

---

## Review Workflow

```
Owner in Claude Chat:                    Repo:
                                         
  "Here are 5 results from Phase C"      tests/results/source_engine/
  [uploads 5 JSON files]                   ├── src_a7c3e91f.json
         │                                 ├── src_b2d4f6e8.json
         ▼                                 ├── ...
  Claude Chat: kr-evaluate                 └── PHASE_C_SUMMARY.json
  - Categorizes each finding              
  - Spots Arabic errors                   After review:
  - Identifies patterns                    tests/results/source_engine/
         │                                   └── reviews/
         ▼                                       ├── phase_c_batch_1.md
  Owner confirms / corrects                      └── phase_c_batch_2.md
         │
         ▼
  Fix list → Claude Code session
```

**Batch size:** 3-5 books per chat turn. More than that bloats context and reduces review quality.

**Summary file:** After each phase, a `PHASE_X_SUMMARY.json` aggregates: total books run, pass/fail counts per field, cost spent, patterns found, fix list for next session.

---

## Phase A: Deterministic Sweep (€0)

**Goal:** Find every bug that doesn't require an LLM call to discover.

**What runs:** Steps 1-3 only (staging → format detection → encoding detection → extraction). Plus: hashing, deduplication check (against empty registry), freezing simulation (without actual file copy — just hash computation).

**Input:** Full Shamela collection from `shamela export samples/`. Every .htm file.

**Output:** `tests/results/source_engine/phase_a_extraction/` — one JSON per book with extraction results and any errors.

**Success criteria:** 
- 0 crashes (every file either extracts or produces a structured error)
- Error codes match SPEC §7 (no uncaught exceptions)
- Extraction results spot-checked on 20 random books by owner

**What to fix before Phase B:**
- Every crash is a code bug → fix
- Every unexpected error code → investigate
- Structural variants not handled → extend extractor

**Script:** `scripts/run_phase_a.py` — iterates collection, runs extraction, saves results, produces summary.

---

## Phase B: Code Audit (€0)

**Goal:** Find logic bugs that unit tests miss because the tests were written by the same agent as the code.

**Method:** Claude Chat session (not Claude Code). The architect reads each module against the SPEC, checking:

1. **Consensus flow:** Does timeout → retry → simplified → fallback actually work? Is the fallback swap (Command A → GPT-5.4) wired correctly?
2. **Registration atomicity:** Does the WAL rollback actually restore from .bak? What if .bak is also corrupt?
3. **Trust re-evaluation path:** Is the "prior sources" check correctly gated to re-evaluation only?
4. **Human gate auto-approve:** Does auto-approve really use the same code path as real review?
5. **Scholar update consistency checks:** What happens if two concurrent intakes try to update the same scholar?
6. **Validation check ordering:** Does Check 5e auto-correction propagate correctly to Check 6?

**Output:** `engines/source/review/CODE_AUDIT_SESSION6.md` — findings and fixes.

---

## Phase C: Targeted LLM Probes (€5-10)

**Goal:** Test LLM inference quality and consensus behavior on real diversity. This is the first time API credits are spent.

**GO/NO-GO gate:** Phase A and B must be complete. Zero known code bugs. Owner has reviewed 20 extraction samples and confirmed correctness.

**Selection strategy (25-30 books, hand-picked for diversity):**

| Category | Count | Selection Criteria | Why |
|----------|-------|-------------------|-----|
| Genre coverage | 12 | One book per active Genre enum value (matn, sharh, hashiyah, mukhtasar, nazm, risalah, fatawa, hadith_collection, tafsir, mawsuah, tabaqat, other) | Verifies genre classification across the full enum |
| Multi-layer | 3 | One sharh, one hashiyah, one taqrirat (if available) | Tests layer detection and attribution on real multi-layer texts |
| Disputed attribution | 3 | Known disputed works (contested Ghazali, anonymous compilations, student compilations under teacher's name) | Tests §6.3 directed attribution comparison — currently untested |
| Edge cases | 3 | Versified fiqh, multi-author compilation, very short juz' | Structural edge cases |
| High-value | 5 | Most commonly studied books (متن الآجرومية, ألفية ابن مالك, الأربعين النووية, العقيدة الواسطية, بلوغ المرام) | Must get these right — owner will use them daily |
| Modern | 4 | Contemporary authors, journal articles, non-scholarly | Tests flagging behavior and trust evaluation |

**Cost estimate:** 25 books × ~$0.08-0.12/book (2 model calls) = ~$2-3. Buffer for retries: $5-10 total.

**Output:** `tests/results/source_engine/phase_c/` — one JSON per book in the standard format.

**Review:** Owner reviews all 25 in 5 chat sessions (5 books each). Every mismatch is categorized (CORE GAP / ENGINE BUG / LLM QUALITY / DATA ISSUE). Fix list produced.

---

## Phase D: Calibration Run (€20-30)

**GO/NO-GO gate:** Phase C findings all resolved. Owner has reviewed all 25 Phase C results and confirmed the engine handles the full genre range correctly.

**Selection strategy (100-150 books):**
- Random stratified sample from the full collection
- Stratified by: Shamela category (proportional), estimated era (pre-1000 AH, 1000-1300, post-1300), with/without muhaqiq
- Include all Phase C books (regression check)

**What this tests that Phase C doesn't:**
- Scholar registry growth (does matching improve or degrade as the registry fills?)
- Work deduplication (multiple editions of the same work)
- Trust distribution (is the verified/flagged split reasonable across 100+ books?)
- Confidence threshold calibration (are thresholds at 0.50/0.70 producing the right gate rate?)
- Cost at scale (actual per-book cost with caching, retries, timeouts)

**Output:** `tests/results/source_engine/phase_d/` + `PHASE_D_SUMMARY.json` with aggregate statistics.

**Review:** Owner reviews a targeted sample:
- All books where `ground_truth` fields mismatch (if ground truth exists)
- All books that triggered human gates
- All books where consensus disagreed
- 10% random sample of "clean" books (verify no silent errors)
- All books with trust_score near the 0.65 boundary (±0.05)

---

## Phase E: Full Collection (€40-50)

**GO/NO-GO gate:** Phase D calibration passes. Trust distribution looks reasonable. Gate rate is manageable (<15% of books). No CORE GAP findings remaining.

**Input:** Entire Shamela collection.

**What this produces:** A populated library. After this, the source engine is done and the normalization engine can begin processing real sources.

**Output:** Full `library/` populated: registries, frozen sources, metadata.json files, human gate queue.

**Review:** Statistical summary only (not per-book). Owner reviews the human gate queue and resolves pending checkpoints.

---

## Cost Tracking

```
tests/results/source_engine/COST_LOG.json

{
  "phases": {
    "A": {"books": 2519, "cost_usd": 0.00, "cost_eur": 0.00},
    "C": {"books": 25,   "cost_usd": 0.00, "cost_eur": 0.00},
    "D": {"books": 0,    "cost_usd": 0.00, "cost_eur": 0.00},
    "E": {"books": 0,    "cost_usd": 0.00, "cost_eur": 0.00}
  },
  "total_usd": 0.00,
  "total_eur": 0.00,
  "budget_ceiling_eur": 100.00,
  "remaining_eur": 100.00
}
```

Updated after every run. Script refuses to start a new phase if remaining budget is below estimated cost.

---

## Key Rules

1. **No run without a saved result file.** Every API call produces a persisted JSON artifact. If it didn't save, it didn't happen.
2. **No phase starts without the previous phase's GO/NO-GO gate passing.** Phase C doesn't start until A and B are clean. Phase D doesn't start until C findings are resolved.
3. **Fixes happen between phases, not during.** A phase runs to completion, results are reviewed, fixes are made in a Claude Code session, then the next phase begins. No mid-phase code changes.
4. **Cost log is updated before every run.** The script checks remaining budget and refuses to proceed if insufficient.
5. **Owner reviews happen in Claude Chat with kr-evaluate.** 3-5 result files per turn. Findings categorized. No result is silently accepted.
6. **Ground truth is expanded incrementally.** Phase C adds 25 manually verified entries to GROUND_TRUTH.json. Phase D adds more. By Phase E, the ground truth covers the full genre range.
