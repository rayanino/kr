# Step 3 — Final Bug List

**Produced by:** Claude Chat (Architect) — Final Quality Gate
**Date:** 2026-03-12
**Method:** Three-phase review: (1) absorb aggregation report + errata, (2) query verdict data + read per-book result/LLM files, (3) trace engine source code line by line. Every finding below cites specific files and line numbers.

---

## Summary

**7 bugs total: 3 must-fix, 2 should-fix, 2 nice-to-have.**

The aggregation report identified 7 recommendations. This review confirms 5, refines 2 with new code-level evidence, and downgrades the severity of 1 (tahqiq-note). No additional engine bugs were found beyond the aggregation report's list, but targeted self-review revealed a second layer to BUG-01 that changes its fix significantly.

One significant **correction to the aggregation report** is documented: the ML disagreement analysis (Section 2.7) incorrectly assessed 3 of 4 cases as "Opus won." The canonical selection logic actually picks Command A in those 3 cases. This changes the tahqiq-note bug from "3 books with wrong output" to "latent risk if confidence ordering changes."

**Key self-review finding:** BUG-01 has two layers. Layer 1 (wrong key name `"primary"`) causes 100% gate abort on first encounters. Layer 2 (semantic mismatch between `school_affiliations` keys and sciences) causes an additional 32% false-positive gate abort rate even after Layer 1 is fixed. After structured analysis of all options, decision: downgrade check 5c from gate to warning (see BUG-01 for full reasoning).

---

## BUG-01: Two-layer defect in author-science gate causes 71% gate abort rate

**Severity: MUST-FIX**
**Aggregation ref: §4.1.3**

### Evidence

This bug has two layers. The first was caught during initial review; the second was found during targeted self-review.

**Layer 1 — Wrong key name (surface symptom):**
`engines/source/src/registries/scholar_registry.py`, lines 100–102:
```python
if school:
    new_record.school_affiliations = {"primary": school}
```

The engine stores a single school name under the key `"primary"`. The SPEC (§4.A.8, line 1212) defines `school_affiliations` as `{science → school}` — keys must be science names like `"fiqh"`, `"hadith"`, not `"primary"`.

Validation check 5c (`validation.py` lines 190–193) then compares `{"primary"}` against `science_scope` → never intersects → gate abort on every first-registered scholar.

**Layer 2 — Semantic mismatch in check 5c (deeper root cause):**
Even after fixing the key name, 16 out of 50 author-science gate-abort books (32%) would STILL gate-abort. The reason: `school_affiliations` records *which madhab a scholar follows in which science* (e.g., `{"fiqh": "شافعي"}`), NOT *all sciences the scholar works in*.

A Shafi'i hadith scholar like النووي gets `school_affiliations = {"fiqh": "شافعي"}` (Command A canonical), but his hadith book has `science_scope = ["hadith", "ulum_al_hadith"]`. Check 5c compares `{"fiqh"}` against `{"hadith", "ulum_al_hadith"}` → no overlap → gate abort. The check is treating "sciences where the scholar has a madhab affiliation" as "all sciences the scholar works in."

This is also model-dependent: Command A tends to include only the primary fiqh school in `school_affiliations` (1–2 keys), while Opus includes broader entries (2–4 keys). Since Command A often wins canonical selection (higher author_conf), the narrower set gets stored, increasing false-positive rate.

**Empirical data:**
- Check 5c false-positive rate: 50/50 (100% — zero true positives in Phase C)
- Author identification error rate: 0/76 (the check never catches what it's designed to catch)
- After Layer 1 fix only: 34/50 would pass, 16/50 would still abort (32% false-positive rate)
- The check fires on SELF-COMPARISON for first encounters (same LLM response's school_affiliations keys vs. same response's science_scope)

**SPEC reference:** Line 1458 says this check should trigger a human gate. Line 1461 confirms: "EXCEPT author-science mismatch which triggers a human gate." Downgrading this check requires a SPEC amendment.

### Decision: Option A — Downgrade check 5c to warning

This decision was made by the architect after structured analysis of all three options. Reasoning below for the owner's review.

**Why Option A (warning) over Option B (first-encounter bypass):** Option B fails empirically. Phase C has 6 authors with multiple books. On second encounters, النووي's three hadith books still false-positive against first-book SA keys `{"fiqh", "aqidah"}` because `school_affiliations` keys don't track sciences — they track madhab labels. الطبري's second edition (tafsir vs `{"fiqh"}`) also false-positives. Option B doesn't fix the root cause.

**Why Option A over Option C (fix data source):** Option C (add `known_sciences` accumulation) is the correct long-term fix, but it requires a new field in `ScholarAuthorityRecord`, accumulation logic in `scholar_authority.py`, and testing — too much for a bug-fix cycle. The normalization engine will need author science profiles anyway, so this work belongs there. Option A now + Option C later is the right sequencing.

**Why the safety trade-off is acceptable:** The check's purpose is catching author misidentification. But even in the scenario where consensus fails (both models agree on the wrong author), check 5c provides no reliable signal because: (a) the data source is semantically broken (madhab labels ≠ science portfolio), (b) the most dangerous misidentifications (same name, same science domain) produce NO check 5c signal (overlap exists), and (c) the check fires on 3 of النووي's 4 books — a 75% false-positive rate on the most prolific correct author in the corpus.

**Reversibility:** `validation.py` line 197: `"warning"` → `"gate"`. One word. If Step 4 reveals ANY case where the warning correlates with a genuine author error, re-promote immediately.

**What the owner sees:** At Step 4, books that would have gate-aborted will instead complete with a warning flag visible in `result.json → needs_review_fields`. The warning provides the same diagnostic information — it just doesn't block the pipeline.

### Proposed fix (two parts)

**Part 1 — Layer 1 (fix key names):**
1. `engine.py` line 340–346: pass the full LLM `school_affiliations` dict instead of extracting one value.
2. `scholar_registry.py` `lookup_or_register_author`: accept `school_affiliations: dict` instead of `school: str`. Store it directly. For the `lookup()` call, extract one school value for the `school` parameter (maintains interface compatibility — `scholar_authority.py` line 199–204 reads `.values()`, not `.keys()`).

**Part 2 — Layer 2 (downgrade check 5c severity):**
`validation.py` line 197: change `severity="gate"` to `severity="warning"`. No other code changes needed — the check continues to fire and populate `needs_review_fields`, it just doesn't abort the pipeline.

---

## BUG-02: result.author.confidence is registry match confidence, not LLM identification confidence

**Severity: MUST-FIX**
**Aggregation ref: §4.1.2**

### Evidence

**Code location:** `engines/source/src/registries/scholar_registry.py`, line 104–108:
```python
# action == "new_record": register new scholar
ref = ScholarReference(
    canonical_id=registered.canonical_id,
    name_arabic=name,
    confidence=1.0,  # ← hardcoded for new records
    source_of_identification="extracted",
)
```

For auto-linked records (lines 55–60, 84–89), `confidence=result.match_score` — which is the registry match score, not the LLM's identification confidence.

**Data evidence:** All 22 success books in Phase C have `result.author.confidence = 1.0`. The actual LLM confidence ranges from 0.55 to 0.99 (read from `llm_responses/claude_opus_4_6.json → parsed.author_identification_confidence`).

**Partial fix already applied:** FIX-C04 (commit `2760f62`) added `confidence_scores.author` to `InferredFieldConfidence`, which carries the capped LLM confidence. This field was `None` in all Phase C results (produced before the fix) but will be populated in Step 4. The `result.author.confidence` field remains wrong.

**Impact:** Any downstream engine reading `result.author.confidence` gets a meaningless value (always 1.0 for new scholars). The correct value is in `confidence_scores.author` after FIX-C04, but two fields with different meanings of "author confidence" is confusing and error-prone.

### Proposed fix

Two changes:
1. Rename `ScholarReference.confidence` to `match_confidence` in `contracts.py` to make its meaning explicit. This is the registry matching confidence.
2. Verify that FIX-C04's `confidence_scores.author` correctly carries the capped LLM value end-to-end by running a small test (2–3 books). If it works, document that downstream engines must use `confidence_scores.author` for identification confidence and `author.match_confidence` for registry matching.

Alternative (simpler): leave `ScholarReference.confidence` as-is but populate it with the LLM identification confidence when `action == "new_record"`. This requires passing the LLM confidence through to `lookup_or_register_author()`.

---

## BUG-03: Tahqiq-note ML bias — defense-in-depth fix needed

**Severity: MUST-FIX (downgraded from aggregation's assessment — see correction below)**
**Aggregation ref: §4.1.1**

### Evidence

**The bias is real:** 4 ML disagreements found in Phase C. In all 4, one model classifies tahqiq editorial apparatus as a scholarly commentary layer (`is_multi_layer=true`). Opus produces this bias in 3 of 4 affected cases; GPT-5.4 in 1. Command A has 0 instances across 67 books.

**Correction to aggregation report:** The aggregation report (Section 2.7) claims "3/4 have wrong pipeline output" and "Opus won" in those 3 cases. This is incorrect. The canonical selection logic (`shared/consensus/src/consensus.py`, line 379–383, `_select_canonical`) picks the model with higher `author_identification_confidence`:

| Book | Command A author_conf | Opus author_conf | Canonical model | Canonical ML |
|------|----------------------|-------------------|-----------------|-------------|
| مسند أحمد ت شاكر | 1.0 | 0.99 | **Command A** | false ✓ |
| الرسالة للشافعي | 1.0 | 0.99 | **Command A** | false ✓ |
| تفسير الطبري ط التربية | 0.99 (GPT) | 0.99 | **Opus** (tie→B) | false ✓ |
| مختصر صحيح مسلم | 1.0 | 0.99 | **Command A** | false ✓ |

All 4 canonical results have the CORRECT ML value. The reason the evaluators saw wrong ML is that all 4 books are `gate_abort` (BUG-01), so no `result.json` was produced, and the evaluation reconstructed the output by reading individual LLM response files.

**Why it's still must-fix:** The correctness depends on Command A having higher author confidence than Opus. If Command A ever reports equal or lower confidence (which could happen for obscure books where both models are uncertain), Opus would win on tie-break and the wrong ML would surface. The fix is cheap and eliminates a latent failure mode.

### Proposed fix

Add a post-inference validation rule in `engines/source/src/validation.py` or `metadata_inference.py`:
```
IF is_multi_layer == true
   AND all layer types in text_layers ∈ {matn, tahqiq_note}
THEN auto-correct is_multi_layer to false
     AND log correction as "tahqiq_note_override"
```

The muhaqiq-in-extraction condition from the aggregation report's proposal is intentionally **dropped**. Self-review found that 1 of 4 Phase C false positives (تفسير الطبري ط التربية) has no muhaqiq in the Shamela metadata despite having tahqiq editorial apparatus visible in the text. Requiring muhaqiq presence would create false negatives at scale. The layer-type pattern alone is a reliable discriminator: all 15 genuine sharh/hashiyah books in Phase C have at least one `sharh` or `hashiyah` layer type, so the override would never fire on them.

Additionally, add `is_multi_layer` comparison to the consensus module (`consensus.py`) so ML disagreements are flagged rather than silently resolved by canonical selection.

---

## BUG-04: Death date source not tracked

**Severity: SHOULD-FIX**
**Aggregation ref: §4.2.1**

### Evidence

No `death_date_source` field exists in `SourceMetadata` (`contracts.py`) or `result.json`. The pipeline stores the death date value but not where it came from.

Phase C analysis identified 4 categories of death date provenance:
- **pass-through** (51 books): date visible in extraction fields
- **false-positive** (7 books): date in `author_name_raw` text, misclassified as LLM inference
- **genuine-inference** (5 verdicts, 4 unique): LLM inferred from training knowledge
- **absent** (13 books): no date available

Without tracking the source, the normalization engine cannot distinguish a high-confidence extraction from a speculative inference. The false-positive category (7 books) has correct dates but incorrect provenance — the date was read from text, not inferred.

### Proposed fix

Add `death_date_source` field to `ScholarAuthorityRecord` in `contracts.py` with enum values: `extraction`, `author_raw_text`, `inference`, `absent`. Populate it in `metadata_inference.py` by checking whether `death_date_hijri` appears in any extraction field before labeling it as inference.

---

## BUG-05: Genre/ML auto-correction creates impossible state

**Severity: SHOULD-FIX**
**Aggregation ref: §4.2.2**

### Evidence

**Code location:** `engines/source/src/validation.py`, lines 232–244 (check 5e):
```python
if genre in ("sharh", "hashiyah") and not is_multi_layer:
    data["is_multi_layer"] = True  # Auto-correct in-place
```

Then lines 258–270 (check 6a):
```python
if is_multi_layer and not text_layers:
    errors.append(ValidationError(severity="gate", ...))
```

If a book is misclassified as hashiyah AND has no text_layers (because it's actually a nukat work), 5e auto-corrects ML to true, then 6a fires a gate error for empty layers.

**Data evidence:** النكت على شرح النووي (Phase C Session 7) — Command A incorrectly classified as hashiyah (0.90 confidence), triggered the auto-correction chain, resulting in the only non-author-science gate_abort in Phase C.

### Proposed fix

Make check 5e conditional: only auto-correct ML to true if `text_layers` is non-empty. If genre is sharh/hashiyah but layers are empty, log a warning and set `needs_review` for both genre and is_multi_layer, but do NOT auto-correct.

```python
if genre in ("sharh", "hashiyah") and not is_multi_layer:
    if text_layers:  # Only auto-correct when layers exist
        data["is_multi_layer"] = True
    else:
        # Warning: genre suggests multi-layer but no layers found
        errors.append(ValidationError(severity="warning", ...))
```

---

## BUG-06: Genre taxonomy missing nukat and jarh_wa_tadil

**Severity: NICE-TO-HAVE**
**Aggregation ref: §4.3.1**

### Evidence

The `Genre` enum in `contracts.py` does not include `nukat` (istidrak) or `jarh_wa_tadil`. These map to `risalah`/`other` and `tabaqat` respectively — technically correct but imprecise.

Phase C: 1 nukat work (النكت) classified as hashiyah by Command A, and 1 jarh_wa_tadil work (تاريخ ابن معين) classified as tabaqat. The jarh work had genre_confidence 0.85, reflecting the LLM's awareness of the imprecise fit.

### Proposed fix

Add genre labels `nukat` and `jarh_wa_tadil` to the `Genre` enum. Update the LLM inference prompt with definitions and examples. Can be deferred until Step 4 results show how many books fall into these categories at scale.

---

## BUG-07: Consensus module does not check is_multi_layer agreement

**Severity: NICE-TO-HAVE**
**Aggregation ref: §4.3.2**

### Evidence

**Code location:** `engines/source/src/consensus.py` — the `make_author_agreement_fn` (line 21) and `check_work_agreement` (line 81) and `compare_attribution_status` (line 122) functions check author name, genre chain, and attribution status. There is no function comparing `is_multi_layer` or `authority_level`.

Phase C: 4 books have ML disagreement between models, all with `consensus.agreed=true`. The consensus "agreed" flag only reflects author agreement, not ML agreement.

**Why nice-to-have:** BUG-03's post-inference fix handles the most dangerous ML disagreement pattern (tahqiq-note). Adding ML to consensus is defense-in-depth. The canonical selection already picks the correct model in 4/4 Phase C cases.

### Proposed fix

Add an ML comparison to the consensus module. When models disagree on `is_multi_layer`, flag it as a soft disagreement. If the tahqiq-note override rule (BUG-03) applies, auto-resolve. Otherwise, log the disagreement for review.

---

## Correction to Aggregation Report

### ML Disagreement Analysis (Section 2.7) is Incorrect

The aggregation report states: "3/4 have wrong pipeline output" for ML disagreement cases and lists "Opus won" for مسند أحمد, الرسالة, and مختصر صحيح مسلم.

**This is wrong.** The canonical selection function (`shared/consensus/src/consensus.py`, `_select_canonical`, lines 378–383) picks the model with higher `author_identification_confidence`. In all 3 cases, Command A has confidence 1.0 versus Opus's 0.99. Command A is canonical, and Command A says ML=false (correct).

The evaluators likely assessed the wrong model's output because these books are all `gate_abort` (no `result.json` produced), and the individual LLM response files were read directly. The evaluation methodology for gate_abort books should have reconstructed which model would be canonical.

**Impact on severity:** The tahqiq-note fix (BUG-03) is still recommended as defense-in-depth, but it's not correcting 3 active defects — it's preventing a latent failure mode that depends on relative confidence ordering.

### Evaluation Confidence Values Use Opus-Specific Data

The verdicts JSON stores `author_confidence_opus` and `genre_confidence_opus`, but the pipeline's `result.json` uses the CANONICAL model's confidence (often Command A). The confidence calibration analysis in Sections 2.3 and 2.4 used Opus confidence values, which may differ from the values that actually appear in pipeline output. The overall conclusions (confidence is well-calibrated) likely hold, but specific numbers may be slightly off.

---

## GO/NO-GO Assessment

**GO — all decisions made, ready for Claude Code.**

The bug list is complete and actionable. Every bug has been verified against specific code lines and data evidence. The three highest-risk claims have been independently re-verified during targeted self-review. The BUG-01 Layer 2 severity decision has been made (Option A: downgrade to warning) with full reasoning documented.

Recommended implementation order for Claude Code:
1. **BUG-01 Part 1** — fix `school_affiliations` key from `"primary"` to science names
2. **BUG-01 Part 2** — downgrade check 5c from `gate` to `warning` in `validation.py`
3. **BUG-05** — genre/ML impossible state: make 5e conditional on layers existing
4. **BUG-03** — tahqiq-note override: auto-correct ML when layers ⊆ {matn, tahqiq_note}
5. **BUG-02** — author confidence: verify FIX-C04 works end-to-end, document field semantics
6. **BUG-04** — death_date_source: new field in contracts, populate in metadata_inference

BUG-06 and BUG-07 can be deferred to post-Step-4.

After fixes: run 5–10 books end-to-end as a smoke test to verify BUG-01 fix eliminates gate_abort and BUG-03 fix handles the tahqiq-note pattern. Then proceed to Step 4.

---

## Appendix: Self-Review Findings

**Method:** Targeted review of three highest-risk claims. 16 tool calls, including 6 script runs, 8 code reads.

### Risk 1: ML disagreement correction — CONFIRMED

Traced the full code path: `evaluate()` (consensus.py line 326) → `agreed=True` → `_select_canonical()` (line 332) → higher `author_identification_confidence` wins → Command A canonical in 3/4 cases. Verified model ordering: `DEFAULT_CONSENSUS_MODELS[0]` = Command A, `[1]` = Opus. For the تفسير الطبري GPT-5.4 fallback case: GPT takes index 0 position, both models at 0.99 → Opus wins on tie → Opus's ML=false (correct). Also verified check 5e would not flip any ML disagreement books post-fix.

### Risk 2: BUG-01 deeper root cause — NEW FINDING

Ran a script comparing canonical model's `school_affiliations` keys against `science_scope` for all 73 books. Found 16/55 books (29%) have no overlap even with correct science-name keys. Root cause: `school_affiliations` records `{science: madhab}` (which science has a school affiliation), not `{science: anything_about_this_science}`. A scholar known as Shafi'i in fiqh but writing a hadith book has `{"fiqh": "شافعي"}` vs `science_scope=["hadith"]` → no overlap. Model-dependent: Command A reports 1–2 schools, Opus reports 2–4.

Quantified impact: Layer 1 fix alone reduces gate-abort from 71% to 32%. Both layers fixed: 0%.

### Decision analysis: BUG-01 Layer 2 severity — Option A chosen

Analyzed all three options using competing perspectives and pre-mortem analysis.

**Option B eliminated empirically.** Queried 6 multi-book authors in Phase C. النووي has 4 books: first book SA keys = `{"fiqh", "aqidah"}`, but books 2–4 are hadith → science_scope `{"hadith", "ulum_al_hadith"}` → NO OVERLAP on second encounters. Same for الطبري (tafsir vs `{"fiqh"}`). Option B has the same false-positive problem as first encounters because the semantic mismatch persists.

**Option C deferred.** Correct long-term approach (accumulate known_sciences), but too complex for a bug-fix cycle. Normalization engine will need author science profiles anyway — that's the right place for this work.

**Option A chosen.** Key reasoning: (a) 0/76 true positives across first AND second encounters; (b) pre-mortem failure scenario (both models agree on wrong author) doesn't rely on check 5c because the most dangerous misidentifications (same name, same science) produce no check signal; (c) fully reversible with one-word change in `validation.py`; (d) warning data at Step 4 provides empirical path to re-evaluation.

### Risk 3: BUG-03 muhaqiq condition — DROPPED

Found that 1/4 Phase C tahqiq-note false positives (تفسير الطبري ط التربية) has no muhaqiq in Shamela extraction metadata. Requiring muhaqiq presence would create false negatives at scale. Verified safety of layer-type-only rule: all 15 genuine sharh/hashiyah books have at least one `sharh`/`hashiyah` layer type, so the override never fires on real multi-layer books. Override would fire on exactly 4 model responses in Phase C, all correctly (100% precision).
