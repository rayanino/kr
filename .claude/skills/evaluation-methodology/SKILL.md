---
name: evaluation-methodology
description: Complete Phase C/D/E evaluation protocol with all errata corrections from calibration and Session 1. Use when evaluating any book's pipeline results. Prevents methodology drift across sessions.
disable-model-invocation: true
---

# Evaluation Methodology — Corrected Protocol

This skill is the single authoritative reference for evaluating Phase C/D/E pipeline results. It incorporates all 12 corrections from calibration, all 6 methodology fixes from Session 1, and all strategic analysis insights. **Do NOT read the original framework without also reading this skill** — the framework contains known errors corrected here.

Source documents (read for full expected values table and worked examples):
- `PHASE_C_EVALUATION_FRAMEWORK.md` — base protocol (Section 7 is inapplicable; field source table replaced below)
- `PHASE_C_ERRATA.md` — 12 corrections
- `PHASE_C_SESSION1_STRATEGIC_ANALYSIS.md` — predictions and risk map
- `NEXT.md` — current session assignment and pre-identified risks

---

## The Six Methodology Rules

These are non-negotiable. Session 1 found 3 violations. Every evaluation must follow all 6.

**M-1: Search BEFORE verdict.** Never write a verdict first and search to confirm. Search independently, then form the verdict from evidence. Violation = confirmation bias.

**M-2: web_fetch 1+ URL per book.** Search snippets alone are insufficient. Fetch at least one full page for direct textual evidence.

**M-3: shamela_category cross-check.** For every book, compare `extraction.shamela_category` against pipeline `genre`. Note discrepancies. Remember: shamela_category is weak genre evidence (partially circular with pipeline input).

**M-4: Distinguish death-date pass-through vs inference.** Compare `extraction.author_death_hijri` to LLM `death_date_hijri`. If they match, the LLM parroted the extraction — NOT a real inference. Only where extraction has NO death date but LLM provides one is it a genuine inference worth verifying.

**M-5: Check model source per book.** Look at `llm_responses/` directory contents. 67/73 books use `command_a.json`, 6 use `gpt_5_4.json`. Never assume the model pair.

**M-6: Session-end consistency check.** After all books in a session, re-read all verdicts as a batch. Check: Did I apply the same standard to book 1 and book 10? Did I actually web-search every book? For VERIFIED, did I actually find 2+ independent sources?

---

## Corrected Field Source Table

**This table replaces the framework's original.** The framework's author confidence path was wrong (Errata #4).

| Field | Source (success) | Source (gate_abort) | Notes |
|-------|-----------------|---------------------|-------|
| Author name | `result.author.name_arabic` | `llm_responses/*.parsed.author_identification.canonical_name_ar` | |
| Author confidence | **`llm_responses/*.parsed.author_identification_confidence`** | Same | **NEVER** `result.author.confidence` (always 1.0 — registry bug) |
| Death date | `llm_responses/*.parsed.author_identification.death_date_hijri` | Same | NOT in result.json at all |
| Genre | `result.genre` | `llm_responses/*.parsed.genre` | |
| Genre confidence | **`llm_responses/*.parsed.genre_confidence`** | Same | result confidence_scores.genre may differ (rounding) |
| Multi-layer | `result.is_multi_layer` | `llm_responses/*.parsed.is_multi_layer` | |
| Science | `result.science_scope` | `llm_responses/*.parsed.science_scope` | |
| Trust | `result.trust_tier` | NOT AVAILABLE — skip | |
| Attribution | `result.attribution_status` | `llm_responses/*.parsed.attribution_status` | |
| Model pair | `consensus.successful_models` | Same | Check for gpt_5_4 vs command_a |

---

## File Path Corrections (Errata)

| What | Wrong | Correct |
|------|-------|---------|
| Opus filename | `opus_4_6.json` | `claude_opus_4_6.json` |
| Second model | always command_a | `command_a.json` (67 books) OR `gpt_5_4.json` (6 books) |
| Framework Section 7 | Applies to Phase C | **Skip entirely** — 0/73 books are single_model_fallback |
| Author confidence cap (0.85) | Applies | **Does NOT apply** — both models ran for all 73 books |

The 6 books using GPT-5.4 instead of Command A:
أبنية الأسماء والأفعال والمصادر, أنوار الهلالين في التعقبات على الجلالين, الأذكار للنووي ت الأرنؤوط, المستدرك على مجموع الفتاوى, تفسير الطبري جامع البيان - ط دار التربية والتراث, حاشية العطار على شرح الجلال المحلي على جمع الجوامع

---

## Verdict Decision Tree

### VERIFIED
- 2+ genuinely independent non-Shamela-ecosystem sources confirm
- All core fields (author, genre, ML) match evidence
- Ground truth candidate

### PLAUSIBLE
- 1 source confirms OR extraction cross-check consistent
- No red flags but not fully confirmed
- NOT a ground truth candidate

### UNVERIFIABLE
- No independent sources found
- Output looks reasonable but cannot be confirmed
- NOT an error, NOT ground truth

### FLAG
- Evidence suggests output may be wrong
- Document the specific discrepancy with reasoning
- If high-confidence + wrong: mark severity "SYSTEMATIC"

### ESCALATE
- Contradictory evidence found OR requires domain expertise
- Frame as specific multiple-choice question for owner

---

## Known Systematic Patterns (from Session 1 + Strategic Analysis)

### Tahqiq-as-Layer Bias (Errata #9)
Opus classifies 3 non-commentary books as multi-layer because they have tahqiq notes:
- الرسالة للشافعي, مختصر صحيح مسلم, مسند أحمد
- All have Opus `is_multi_layer=true` with `layer_type="tahqiq_note"`, Command A says `false`
- Command A is correct. Tahqiq notes are editorial apparatus, not scholarly commentary layers.
- **Action:** When a non-sharh/hashiyah book has ML=true with tahqiq_note, FLAG as Opus bias.

### Attribution: Opus Has Real Domain Knowledge (Strategic Analysis §IV)
- Opus's "disputed" calls for الإبانة and الفقه الأكبر are genuinely correct
- The 9 "traditional vs definitive" disagreements reflect a calibration question, not model error
- Do not dismiss Opus's conservative attribution calls — they reflect real scholarly debate

### Consensus Does NOT Check Multi-Layer (Errata #10)
- `consensus.agreed=true` can coexist with ML disagreement between models
- 4 books in Phase C have this exact situation
- **Action:** Even for agreed books, manually compare both models' `is_multi_layer`.

### Gate Abort Rate (Strategic Analysis §I)
- 51/73 (70%) are gate_abort. 50/51 share identical trigger: "Author's known sciences {'primary'} don't overlap with source sciences"
- This is a 98% false positive rate from empty scholar registry (bootstrapping artifact)
- **Action:** Do NOT treat gate_abort as a negative signal. Evaluate classifications from llm_responses/ as normal.

### Death Date: 10 Real Inferences (Strategic Analysis §II)
- Only 10 books have genuine death-date inferences (extraction had no date, LLM provided one)
- Current accuracy: 1/2 verified (50%) — famous scholars likely correct, modern/obscure authors are the real test
- **Action:** Every real inference is a high-priority verification target. Use web_fetch on biographical pages.

### Genre: Most Likely Source of FLAGS (Strategic Analysis §VI)
- 3 إعلام الموقعين editions have inconsistent genre (matn, other, other)
- Genre has 17+ enum values and genuinely ambiguous cases
- Prediction: 3-5 genre FLAGs across Sessions 2-5

---

## Anti-Patterns to Avoid

### Circular Verification
Shamela metadata card + extraction.json + LLM response all originate from the same Shamela database. If all three agree, that is ONE source — not three. For VERIFIED, you need sources OUTSIDE the Shamela ecosystem.

### Confidence Inflation
LLMs give 0.99 confidence for everything. 10/10 famous authors get 0.99. High confidence does NOT mean correctness. The one verified wrong death date (أساليب بلاغية: 1432 vs actual 1439) had 0.95 confidence.

### Edition Confusion
Different editions of the same work MUST have consistent author, genre, and multi-layer status. Muhaqiq and trust may differ. If editions disagree on core fields, FLAG the inconsistency.

### Skipping Web Search for "Obvious" Books
Session 1 self-review found 3 books where web search was skipped because the answer seemed obvious. Never skip. Training data may contain the same errors as the pipeline.

### Anti-Anchoring
The expected values table in the framework may contain errors. It was written from general knowledge, not independent verification. Your web search results OVERRIDE the expected values. Trust evidence over hypotheses.

---

## Gate Abort Evaluation Protocol

1. Read `result.json` — confirm status is gate_abort, note error_code and gate_errors
2. Read `llm_responses/claude_opus_4_6.json` — get ALL classification fields from `parsed`
3. Read the second model file (command_a.json or gpt_5_4.json) — compare
4. Read `consensus.json` — note agreement status
5. Read `extraction.json` — note what metadata was available to the LLM
6. Evaluate the classification quality INDEPENDENT of the gate trigger
7. Note: trust_tier is NOT available for gate_abort books — skip trust evaluation

The gate trigger (author-science mismatch) is 98% false positive. The underlying classifications may be perfectly correct.

---

## Ground Truth Proposal Criteria

A book qualifies for GT proposal ONLY if ALL of these are true:
1. Overall verdict is VERIFIED
2. Author name + death date confirmed by 2+ independent sources (at least one non-Shamela)
3. Genre verified by title analysis AND at least one external classification
4. Multi-layer status is deterministic from genre/title
5. Pipeline confidence scores are reasonably calibrated
6. Consensus `agreed=true` (both models ran for all 73 Phase C books)

---

## Session Risk Map (from Strategic Analysis §VII)

| Session | Difficulty | Key Risks |
|---------|-----------|-----------|
| 2 | Low | مسند أحمد tahqiq-as-layer bias |
| 3 | Medium | الرسالة ML disagree + tahqiq bias + death inference; الأم genre ambiguity |
| 4 | Medium | Multi-layer binary checks; المآخذ NOT sharh (criticism, not commentary) |
| 5 | **High** | الإبانة + الفقه الأكبر disputed attribution; الورقة النحوية lowest conf (0.55) |
| 6 | Medium | Cross-edition consistency; إعلام الموقعين genre inconsistency |
| 7 | Low-Med | Riwayah mostly extraction-quality issue; 4/5 have null extraction |
