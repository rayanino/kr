# LLM Trustworthiness Defenses — Excerpting Engine

**Status:** RESEARCH COMPLETE — Tier 1 defenses ready for implementation. Empirical scan required before Session 4 handoff.
**Date:** 2026-03-23
**Author:** Claude Chat (Architect)
**Authority:** This document is MANDATORY READING for Sessions 4–6 handoffs. Referenced from CLAUDE.md.

---

## Why This Exists

The excerpting engine has 4 LLM-dependent operations. Each can produce errors the owner cannot detect — errors that become wrong beliefs. The deterministic parts (Phase 1 assembly, Phase 3 deterministic) are verified by 177+ tests. The LLM parts have multi-model consensus but no deterministic cross-checks. This document closes that gap.

**Principle:** Every LLM claim that CAN be checked against observable evidence MUST be checked. LLM judgment that cannot be deterministically verified relies on consensus + human gate.

---

## Failure-Mode Matrix

Every LLM-dependent operation, its failure modes, threat mapping, and whether deterministic verification is possible.

### Operation 1 — Segment Classification (Phase 2a)

| ID | Failure | Threat | Severity | Deterministic check? |
|----|---------|--------|----------|---------------------|
| F1a | Wrong scholarly function (e.g., rule_statement when actually refutation) | T-3, T-4 | HIGH | **Partial** — evidence types only |
| F1b | Wrong segment boundary (splits isnad chain) | T-4 | MEDIUM | No |
| F1c | Missed evidence classification | T-3 | MEDIUM | **Yes** — markers detectable |

### Operation 2 — Teaching Unit Grouping (Phase 2b)

| ID | Failure | Threat | Severity | Deterministic check? |
|----|---------|--------|----------|---------------------|
| F2a | **Decontextualization** — refutation separated from position it refutes | T-2 + T-4 | **CRITICAL** | No — requires semantic understanding |
| F2b | Over-grouping (unit too broad) | T-3 | LOW | No |
| F2c | Under-grouping (evidence separated from ruling) | T-4 | HIGH | **Partial** — sequence patterns |
| F2d | Self-containment mis-assessment (says FULL, has dangling references) | T-4 | HIGH | **Partial** — back-reference markers |

### Operation 3 — LLM Enrichment (Phase 3, Session 4)

| ID | Failure | Threat | Severity | Deterministic check? |
|----|---------|--------|----------|---------------------|
| F3a | Wrong school attribution | T-2, T-6 | HIGH | **Yes** — cross-check source metadata |
| F3b | Wrong topic keywords | T-3 | MEDIUM | No |
| F3c | Fabricated takhrij (wrong hadith/Quran reference) | T-5 | HIGH | **Partial** — Quran verifiable, hadith hard |
| F3d | Wrong cross-references | T-3 | LOW | No |
| F3e | Missing context_hint for PARTIAL units | T-4 | MEDIUM | No |

### Operation 4 — Consensus Verification (Phase 3, Session 4)

| ID | Failure | Threat | Severity | Deterministic check? |
|----|---------|--------|----------|---------------------|
| F4a | Same-model bias (both models wrong for same reason) | T-2 | MEDIUM | No |

**Summary:** 6 of 13 failure modes are at least partially deterministically verifiable. We currently verify 0 of them.

---

## Tier 1 Defenses — Build Into Excerpting Engine

These are cheap, deterministic, and directly address the highest-severity gaps. Target: implement during Sessions 4–5.

### Defense 1A: Dangling Reference Detector

**Addresses:** F2d (self-containment mis-assessment, T-4 HIGH)

Scan `primary_text` for Arabic back-reference patterns that indicate the text depends on external context. If any pattern is found AND the LLM assessed `self_containment=FULL`, automatically downgrade to PARTIAL and add a review flag.

**Candidate patterns (MUST be empirically validated before committing):**

| Pattern | Arabic | Meaning |
|---------|--------|---------|
| Back-reference | كما تقدم | "as previously mentioned" |
| Back-reference | كما سبق | "as preceded" |
| Back-reference | ما تقدم | "what preceded" |
| Back-reference | المذكور آنفاً | "the aforementioned" |
| Back-reference | ما سبق ذكره | "what was previously mentioned" |
| Forward-reference | سيأتي | "will come later" |
| Forward-reference | كما سيأتي | "as will come" |
| Cross-reference | انظر | "see/refer to" |
| Cross-reference | راجع | "refer back to" |
| Section-reference | في الباب السابق | "in the previous chapter" |
| Section-reference | في الفصل الآتي | "in the coming section" |

**CRITICAL: Empirical scan required.** Before building this, run against all 66 fixtures / 16.7M chars and measure:
- Total hits per pattern
- False positive rate (pattern appears but text IS self-contained)
- Overlap with self_containment=PARTIAL/DEPENDENT assessments

The evidence marker scan (DD-S3-8) is the template: 66 fixtures, count matches, check false positives, make the decision empirically. If hit rate is near-zero (like ﴿﴾ delimiters), don't build it. If substantial, this becomes one of the highest-value defenses.

**Implementation location:** Phase 3 validation (Session 5) or as a post-LLM-enrichment cross-check in Session 4.

### Defense 1B: Source Metadata School Cross-Check

**Addresses:** F3a (wrong school attribution, T-2 + T-6 HIGH)

When LLM enrichment sets `school` on an ExcerptRecord, compare against the source engine's metadata for that `source_id`. If the source is tagged as a Shafi'i work and the LLM says "Hanafi," flag with a review code.

**Implementation:** One conditional check in the post-enrichment validation. Requires: source metadata accessible at excerpting time (already available through NormalizedManifest).

**Edge cases to handle:**
- Multi-school sources (comparative fiqh works) — source metadata may say "multi" or have no school
- Excerpts that quote another school's position — the excerpt's school may legitimately differ from the source's school if the excerpt is quoting/refuting an opposing view
- Source metadata may be null — no cross-check possible, don't flag

**Resolution:** Flag as review, not as error. The review queue distinguishes "LLM says X, source says Y" for human evaluation.

### Defense 1C: Quran Canonical Text Lookup

**Addresses:** F3c for Quran references (fabricated references, T-5 HIGH)

**Data source:** AlQuran Cloud API (`api.alquran.cloud/v1/quran/quran-uthmani`) — full Quran in Uthmani script, 6,236 verses, ~2MB JSON. Download once, store as `data/quran_uthmani.json`.

**Algorithm:**
1. For any `evidence_ref` with `type="quran"`, take the `text_snippet`
2. Strip diacritics from both snippet and canonical text
3. For each verse in the canonical Quran: check if the stripped snippet is a substring of the stripped verse
4. If matched: fill `surah` and `ayah_start`/`ayah_end` deterministically
5. If LLM enrichment (Session 4) claims a specific verse reference AND the deterministic match contradicts it: flag

**Why this is high-value:** The Quran is a fixed, canonical text with zero variation. Matching is deterministic. This turns every Quran citation from an LLM claim into a verifiable fact.

**Implementation location:** Can be built as a standalone utility called by Phase 3 deterministic (F-DET-5) AND by Phase 3 enrichment validation. Replaces the "canonical Quran lookup deferred" note (DD-S3-3).

### Defense 1D: Classification-Evidence Cross-Validation

**Addresses:** F1a (wrong scholarly function, partial), F1c (missed evidence classification)

After Phase 2a classification AND Phase 3 deterministic evidence detection (F-DET-5), compare:

| LLM says | Deterministic scanner finds | Action |
|----------|---------------------------|--------|
| `evidence_hadith` | Zero hadith markers in segment | Review flag |
| NOT evidence type | Dense hadith/Quran markers in segment | Review flag |
| `evidence_quran` | Quran canonical lookup finds no match | Review flag |
| `evidence_ijma` | Zero ijma markers in segment | Review flag |

**Limitation (be honest):** This only catches evidence-vs-non-evidence misclassification. It cannot distinguish rule_statement from opinion_statement from refutation — those are genuinely semantic judgments with no deterministic signal. The coverage is ~30% of classification errors (evidence types are 5 of 16 scholarly functions).

**Implementation location:** Phase 3 validation (Session 5) as a cross-phase consistency check.

---

## Tier 2 Defenses — Add During Evaluation Phase

### Defense 2A: Targeted Self-Containment Consensus Question

During Session 4 consensus verification, add a specific question for FULL self-containment units: "Given only this text and no surrounding context, are there any references, pronouns, or assumptions that require information from outside this passage to understand?"

This focuses the second model specifically on T-4 rather than general attribution consensus.

### Defense 2B: Calibration from 30-Book Probe

During the owner's review: log every correction. After: compute accuracy per scholarly_function type, identify systematic biases, adjust gate queue thresholds. Natural byproduct of evaluation, not separate engineering.

---

## Tier 3 Defenses — Defer to Post-Excerpting

### OpenITI/KITAB Text Reuse (T-7 defense)

Cross-source verification using the OpenITI corpus and KITAB's passim text reuse data. Library-level integrity tool, not engine-level. Defer until all 5 engines are built.

### Hadith Database Fuzzy Matching (T-5 defense)

Hadith collections are vast, text varies between editions, and fuzzy matching against Arabic text is an unsolved problem. The best systems use LLMs for verification — circular dependency. Defer.

### Arabic Coreference Resolution (T-4 defense)

Neural Arabic coreference resolution exists (AraBERT-based, 2020) but is trained on OntoNotes modern Arabic, not classical scholarly Arabic. Would need domain adaptation. Research-grade, not production-ready. Defer.

---

## What RAG Cannot Solve Here

RAG (Retrieval-Augmented Generation) helps when the model lacks information. In excerpting, the model already sees the full division text — all the context exists in the prompt. The problem is not context-poverty; it's *judgment*. The LLM sometimes misinterprets text it can see perfectly well. RAG doesn't fix judgment errors; it fixes knowledge gaps. Wrong tool for this problem.

The exception: if we wanted to give the LLM examples of correctly-excerpted teaching units from the same genre as few-shot examples, that's a form of RAG that could improve judgment. This is worth exploring during evaluation (Defense 2B calibration) but not worth engineering into the pipeline now.

---

## What Cannot Be Verified Deterministically

**F2a (decontextualization)** is the hardest failure. "والصحيح في المسألة أنه يجب الغسل" ("and the correct position on this issue is that ghusl is obligatory") looks self-contained. But "this issue" might refer to a debate 50 pages earlier. No scanner, no RAG, no second model will catch this consistently.

The defense is the human gate. The owner reviewing 30 books, reading actual Arabic excerpts, catching the ones that don't make sense standalone — that's the primary defense for the hardest failure category.

The system is trustworthy not because any single layer is perfect, but because errors must survive all three layers (deterministic checks → consensus → human gate) to reach the owner.

---

## Empirical Scans Required Before Session 4

| Scan | What | Decision it informs |
|------|------|-------------------|
| Back-reference patterns | Run Defense 1A candidate patterns against 66 fixtures / 16.7M chars | Build or skip dangling reference detector |
| Quran text coverage | Download Uthmani text, run against all قال تعالى / قوله تعالى hits from Step 6 scan | Feasibility of canonical lookup on our data |
| Evidence-classification overlap | After Session 3, compare F-DET-5 evidence_refs against Phase 2a scholarly_functions on test data | Coverage of cross-validation defense |

These scans should be run during Session 4 handoff preparation (before writing NEXT.md for Session 4).

---

## Integration Points in Build Plan

| Session | Defense | What to add |
|---------|---------|-------------|
| Session 4 handoff | 1A scan | Run back-reference pattern scan during handoff prep |
| Session 4 handoff | 1C data | Download Quran canonical text, add to repo as `data/quran_uthmani.json` |
| Session 4 | 1B | School cross-check in enrichment validation |
| Session 4 | 1C | Quran canonical lookup in enrichment validation |
| Session 4 | 2A | Targeted self-containment consensus question |
| Session 5 | 1A | Dangling reference detector (if scan justifies it) |
| Session 5 | 1D | Classification-evidence cross-validation |
| Evaluation | 2B | Calibration from 30-book probe |
