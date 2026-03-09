# Phase 0 Findings — Deterministic Test Results

## A3: Scholar Name Matching — ISSUES FOUND

### Finding A3-1: Full name vs short name falls below gate threshold
**Severity:** HIGH — would create duplicate scholar records

The `normalized_name_similarity` function using `SequenceMatcher` produces dangerously low scores when comparing a full patronymic name against a short commonly-used name:

| Name A | Name B | Similarity | Zone |
|--------|--------|-----------|------|
| أبو زكريا يحيى بن شرف النووي | النووي | 0.267 | new_record |
| عبد الرحمن بن أبي بكر السيوطي | جلال الدين السيوطي | 0.410 | new_record |
| عبد الرحمن بن إسحاق البغدادي النهاوندي الزجاجي أبو القاسم | أبو القاسم الزجاجي | 0.222 | new_record |

These are all the SAME scholar. The algorithm would create separate records for each.

**Root cause:** `SequenceMatcher.ratio()` penalizes length differences heavily. When "النووي" (4 chars normalized) is compared against a 24-char patronymic, the shared substring is a tiny fraction.

**Impact on production:** The SPEC's `compute_scholar_match_score` uses multiple signals (name + death date + school + works), but even the composite score fails:
- name_sim=0.27 * weight 0.50 = 0.135
- death_date match (exact) * weight 0.30 = 0.300
- Total = 0.435 → still below 0.50 gate threshold

**Proposed SPEC fix:** Add a **substring containment boost** to `normalized_name_similarity`:
```
After computing SequenceMatcher ratio, also check:
if shorter_normalized is fully contained in longer_normalized:
    score = max(score, 0.70)  # Force into human_gate zone at minimum
```
This is safe because Arabic scholarly names are distinctive — "نووي" appearing inside a longer name almost certainly means the same scholar.

### Finding A3-2: Disambiguation works correctly
Ibn Hajar al-Asqalani vs Ibn Hajar al-Haytami scores 0.643 → human_gate. This is correct behavior: similar but distinct scholars are routed for human review.

### Finding A3-3: Name matching works well when names are similar length
Identical names, diacritics-only differences, and teacher/student pairs (الزجاجي vs الزجاج at 0.786) all score correctly.

---

## A4: Trust Weight Calibration — THRESHOLD MISMATCH

### Resolution: Ground truth updated (Option C — owner decision)
Owner principle: "flagged" means genuinely untrustworthy, not just incomplete metadata. A classical primary text from Shamela with an unknown muhaqiq is still trusted scholarship. The muhaqiq absence is noted in metadata (`muhaqiq: null`, `needs_review_fields` entry) but does not trigger a flag by itself.

Fixtures 01, 02, 04, 08 changed from expected_trust "flagged" → "verified".

### Result: 13/13 correct at threshold 0.65
Sensitivity analysis confirms 0.65 is uniquely optimal:

| Threshold | Correct | % |
|-----------|---------|---|
| 0.55 | 12/13 | 92% |
| 0.60 | 12/13 | 92% |
| **0.65** | **13/13** | **100%** |
| 0.70 | 12/13 | 92% |
| 0.75 | 7/13 | 54% |

**A4 assumption validated. No SPEC change needed for weights or threshold.**

### SPEC clarification needed at build time
Document the trust semantics: "flagged" indicates genuinely low trust — sources where reliance would be risky (unknown modern authors, low text fidelity, no scholarly provenance). It does NOT flag classical works merely for lacking a named muhaqiq. When a muhaqiq cannot be identified, the metadata records `muhaqiq: null` and a `needs_review_fields` entry is added, but `trust_tier` remains based on the overall weighted evaluation.

### Finding A4-2: Alfiyyah plain text correctly flagged
Score = 0.647 (just below 0.65) due to `text_fidelity: medium` (0.60 for plain text). This is correct — plain text without structural markup or provenance has uncertain digital lineage, distinct from the work's scholarly authority.

---

## Remaining decisions for build phase

1. **A3 substring boost:** The name matching needs a substring containment fix before build. Documented here; implementation is a build-phase task.
