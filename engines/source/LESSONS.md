# Source Engine — Lessons Learned

**Engine:** Source (محرك المصادر)
**Build:** 6 sessions + code audit, March 2026
**Validation:** 5 phases (0, A, C, D, E), 347 LLM-probed books, €36.70
**Final metrics:** 566 tests, 0 failures, 274 books in master manifest

Per-phase details: `tests/results/source_engine/phase_{c,d,e}/PHASE_{C,D,E}_LESSONS.md`, `engines/source/review/PHASE_A_LESSONS.md`

---

## Bugs Found

### Extraction (Phase A — deterministic)

- **القسم header leak (BUG-A1):** Shamela card header line matched as a bibliographic field, causing 32 books to get category text as muhaqiq name. Fix: skip fields with القسم in label.
- **Format B colon-in-label (BUG-A2):** Variant HTML card format had value embedded inside the label span. 64 books affected. Fix: detect colon in label after strip_tags, split to recover real value.
- **Missing title_full (BUG-A3):** 32 books had display_title but no title_full. Fix: fallback copy. Result: 100% title coverage.
- **Edition text leak into author (BUG-A4):** Publication details appended to author name. Fix: regex to strip trailing edition/publisher text.
- **Duplicate card fields (BUG-A5):** 2,193 books had redundant header data in extra_card_fields. Fix: القسم guard (same as BUG-A1).

### Pipeline (Phase C — LLM probes)

- **BUG-C01:** Edition group detection used shortened titles that didn't match collection directory names. Only 1 of 9 groups detected. Fix: use full directory names.
- **BUG-C02:** Edition groups excluded gate_abort books despite complete LLM data. Fix: include gate_abort books with data from llm_responses/.

### Validation (Code Audit — commit 4b51718)

- **6 bugs found by manual code review** that 768 passing unit tests missed. Tests written by the same agent as the code tend to test what the code does, not what the SPEC says. A fresh code audit against the SPEC catches different bugs.

### Post-Evaluation (ERR-01 through ERR-03)

- **ERR-01:** hashiyah genre + is_multi_layer=false is an impossible state. Pipeline didn't validate this. Fix: added validation rule.
- **ERR-02:** Compiler-as-muhaqiq pattern (السراج المنير). Shamela lists source authors in author field while actual compiler is in muhaqiq field. Documented in DECISION_PLAYBOOK as known limitation with extension hook.
- **ERR-03:** Death date hallucination — systematic pattern. Opus hallucinates death dates 2-6 years off for modern scholars when extraction provides no date. Fix: added validation warning (check 5g) for single-model death dates.

## Patterns Observed

### Scholar Authority

- **Scholar registry sparseness caused 70% gate_abort rate in Phase C.** Populating science_scope for major scholars before Phase D dropped the rate to 0%. This was the single most impactful fix across all phases.
- **Author name is the most disputed field.** 100% of consensus disagreements (27/347 books) involve author name. The models identify the same person but describe them differently (kunya vs. nasab, with/without laqab).

### Consensus Mechanism

- **92.2% agreement rate** across 347 books. The disagreement rate (7.8%) is appropriate — it catches genuine ambiguity without over-triggering.
- **Science scope is the second most disputed field** (48% of disagreements). Models disagree on scope breadth (e.g., "usul_al_fiqh + fiqh" vs. "usul_al_fiqh" alone).
- **Consensus module was oversensitive to cosmetic differences** in Phase C/D. 13 of 14 Phase D "disagreements" were the same person described differently — not substantive factual disagreements.

### Metadata Quality

- **Deterministic extraction: 100% title, 95% author, 100% category, 85% publisher.** These rates are inherent to Shamela HTML card format.
- **LLM-only fields: 100% coverage on success books.** Genre, science_scope, is_multi_layer, structural_format, authority_level — all reliably inferred when LLM runs succeed.
- **Major extraction gap: edition (0%), muhaqiq (0%), death_date (0%).** These fields require LLM inference or external lookup. The extraction regex was extended in Phase A but these fields are rarely in Shamela's HTML card structure.

### Gate Behavior

- **66 of 67 gate aborts are science_scope_mismatch** — the gate is working correctly. It catches cases where the scholar authority database lacks the inferred science, requiring human review.
- **Phase C had 70% abort rate (sparse registry), Phase D had 0%, Phase E had 23% (edge cases).** The rate correlates with scholar registry coverage, not pipeline quality.

## What Went Wrong

- **Phase C: Misleading stderr during run.** Command A timeout messages suggested model unavailability. Actual data: 67/73 books used Command A successfully. Lesson: always verify error claims against actual output data (check the files, not the logs).
- **Phase D aggregation: ERR-03 nearly missed.** The death date hallucination pattern was only found in Round 5 (critical self-review). Without the 5-round review protocol, 3+ hallucinated death dates would have entered the library as verified facts.
- **Code audit found 6 bugs that 768 tests missed.** Tests by the same author as the code are structurally insufficient for catching SPEC-vs-implementation divergence.

## What Worked

- **5-round evaluation protocol** caught protocol violations (Round 3), wrong source labels (Round 4), and a systematic hallucination pattern (Round 5). Each round found issues the previous rounds missed.
- **Multi-model consensus** correctly flagged every confirmed error (ERR-01, ERR-02, ERR-03 were all in books where models disagreed or confidence was low).
- **Gate abort mechanism** preserved all LLM data for reuse — 51 Phase C gate_aborts became Phase D successes without re-running inference.
- **Budget protection** held costs to €36.70 of €100 ceiling (36.7%). The per-book cost (€0.10) was stable across phases.
- **Edition group consistency** validated pipeline reproducibility — all 9 groups had consistent metadata across editions.

## Recommendations for Downstream Engines

1. **Genre is a hint, not a gate.** The risalah/matn/other boundary is fuzzy (7 genre disagreements in consensus analysis). Downstream engines should use genre to inform processing strategy, not as a hard routing decision.
2. **Trust tier "flagged" is common and normal.** 33% of books are trust=flagged due to missing muhaqiq/publisher/death_date. This reflects extraction sparseness, not actual quality concerns. The owner's gate queue will be large.
3. **Multi-layer detection confidence matters.** Source engine LLM and normalization auto-detection disagree on 9 books. Low confidence (0.62-0.66) correctly signals uncertainty. Downstream engines should treat confidence < 0.70 as unreliable layer boundaries.
4. **Compiler-as-muhaqiq pattern (ERR-02) is unresolved.** Books where the muhaqiq field contains the actual compiler/arranger are misattributed. Future enhancement: detect when muhaqiq is contemporary but listed authors are classical.
5. **Death dates from single-model inference are unreliable.** Check 5g flags these. Downstream engines should not treat flagged death dates as ground truth.

## Impact on Normalization Engine

- 274 SourceMetadata records across 19 of 32 Shamela categories
- 20 multi-layer books with explicit layer attribution
- Cross-engine validation: 70/70 Phase E books normalize successfully with 0 crashes
- Contract boundary verified: 5 defects found and fixed before normalization build
