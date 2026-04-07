# Campaign Evaluation Plan — Session 11

**Target:** `taysir` package from campaign_20260331 ($97 run)
**Excerpts:** 1,283
**Goal:** Evaluate existing campaign output against new D3 SPEC rules (§6.18-6.23, ADV-E-13-22)

---

## Why taysir

1. Largest excerpt set (1,283) — most statistical power
2. Source book for D3 الكلالة case (تيسير العلام شرح عمدة الأحكام)
3. Hanbali fiqh — genre where school-specific branching, attribution coupling matter most
4. Had 62+7 chunk failures + 187 LLM errors — most error surface to analyze

## D3-Rule Impact Assessment (from campaign data)

### §6.19 PO-1 / §6.23 AC-1 — Packaging vs Ontology

| Function | Total | With Proof Indicators | With Attribution Indicators |
|----------|-------|-----------------------|----------------------------|
| definition | 105 | 48 (46%) | 1 (1%) |
| rule_statement | 556 | 302 (54%) | 31 (6%) |
| opinion_statement | 228 | 112 (49%) | 92 (40%) |
| evidence_hadith | 160 | 138 (86%) | 7 (4%) |

**Finding:** Nearly half of all definitions and rule statements contain proof indicators embedded in the classified text. These are cases where the engine classified the passage by its primary function but didn't separate distinct scholarly layers. For many, the proof material may be harmless carry-over (§6.19 PO-1). For some, it may be substantial enough to warrant separate treatment.

### §6.18 LP-1 — Leaf Pollution

158 excerpts have <20 words. Top function: `rule_statement` (118). These are candidates for leaf pollution — short rule mentions that may exist as brief supporting references within a larger discussion. Need to check if the same topics appear in more substantive excerpts elsewhere.

### §6.21 SSB-1 — School-Specific Branching

11 excerpts contain explicit school-specific terms (عند الحنابلة, عند الشافعية, etc.). These are the passages where SSB-1's three-scenario framework applies — the engine needs to determine whether school attribution is a genuine definition variant or merely attribution of the same definition.

## Evaluation Approach (1 book, ~10 excerpts deep-evaluated)

### Step 1: Sample selection (10 excerpts)
- 3 definition excerpts with proof indicators (§6.19/§6.23 relevance)
- 2 short rule_statements (<20 words) (§6.18 relevance)
- 2 opinion_statements with both proof + attribution (§6.23 relevance)
- 2 school-specific excerpts (§6.21 relevance)
- 1 the الكلالة excerpt itself (D3 ground truth)

### Step 2: Per-excerpt evaluation (for each of the 10)
For each excerpt, answer:
1. **Function classification correct?** Does `primary_function` match the actual scholarly function?
2. **Layer separation adequate?** Are distinct layers (definition/proof/attribution) identified?
3. **Packaging appropriate?** If mixed content, is carry-over harmless per §6.19?
4. **Leaf-worthy?** Does this passage merit its own excerpt per §6.18?
5. **School handling correct?** If school-specific content, which SSB-1 scenario applies?
6. **Self-containment accurate?** Does `self_containment` rating match reality?

### Step 3: Findings synthesis
- Count: how many of the 10 would be classified differently under hardened SPEC
- Classify: which D3 rules caught real quality issues vs false alarms
- Project: extrapolate % impact across all 1,283 taysir excerpts

## Budget
- API cost: EUR 0 (evaluating existing data, no new LLM calls)
- Time: ~30 minutes for 10-excerpt deep evaluation

## Prerequisites
- D3 SPEC additions must be reviewed by coworkers (PENDING — 2 CC agents dispatched)
- CRITICAL/HIGH findings from coworker review must be resolved before evaluation
