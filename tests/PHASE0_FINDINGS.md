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

### Finding A4-1: Classical primary sources score above threshold regardless of muhaqiq
**Severity:** MEDIUM — over-trusts unedited classical texts

Four fixtures score as "verified" but ground truth expects "flagged":

| Fixture | Score | Expected | Why flagged in GT |
|---------|-------|----------|-------------------|
| 01_nahw_simple | 0.693 | flagged | No muhaqiq |
| 02_nahw_muhaqiq | 0.718 | flagged | Unknown muhaqiq |
| 04_hadith | 0.718 | flagged | Unknown muhaqiq |
| 08_death_date | 0.718 | flagged | Unknown muhaqiq |

**Root cause:** `author_standing` at weight 0.30 with score 0.90 contributes 0.270 alone. Combined with `source_authority: primary` (0.128) and `text_fidelity: high` (0.135), the base score for any classical primary Shamela source is already 0.533 before tahqiq and publisher are even considered. Any tahqiq score ≥ 0.40 pushes the total above 0.65.

**The distinguishing fixtures (06 verified, 11 verified)** have the same scores as the failing ones. The ground truth assumes that known publisher (دار الفكر for 06) and/or exceptional work reputation (همع الهوامع for 11) provide the extra signal. But the algorithm doesn't capture either.

### Finding A4-2: Sensitivity analysis shows no single threshold works perfectly

| Threshold | Correct | % |
|-----------|---------|---|
| 0.55 | 8/13 | 62% |
| 0.60 | 8/13 | 62% |
| 0.65 | 9/13 | 69% |
| 0.70 | 10/13 | 77% |
| 0.75 | 11/13 | 85% |

No threshold produces better than 85% accuracy because fixtures 06 and 11 (expected verified) have the same factor scores as fixtures 02, 04, 08 (expected flagged).

### Proposed SPEC fixes (choose one)

**Option A: Add critical-low rule for muhaqiq + publisher combo.**
Flag when `tahqiq_quality ≤ 0.50 AND publisher_reputation ≤ 0.40` regardless of combined score.
- This requires known_publishers.json to distinguish 06 (دار الفكر → higher score) from the rest.
- Problem: fixture 11 (المكتبة التوفيقية) is not a particularly well-known publisher either.

**Option B: Raise threshold to 0.72 and add "exceptional work" override.**
Works scored ≥ 0.72 are verified. Below → flagged. Add a configurable "canonical works" list where specific well-known work_ids get an automatic verified status (همع الهوامع, Alfiyyah sharh, etc.).
- This is more explicit but requires manual curation.

**Option C: Revise ground truth expectations.**
Accept that classical primary sources from Shamela HTML are inherently higher-trust than the ground truth assumes. Change fixtures 01, 02, 04, 08 to expected_trust: "verified". The flagged status should be reserved for: unknown modern authors, low text fidelity, or sources with specific quality concerns.
- This is the least-engineering-effort option but changes the trust semantics.

**Recommendation: Option A + known_publishers.json bootstrap.**
This is most consistent with the SPEC's intent. Requires:
1. A minimal known_publishers.json with ~10 well-known publishers (دار الفكر, دار المعارف, المكتبة التوفيقية, etc.)
2. The critical-low rule addition
3. Re-evaluate whether 11 should genuinely be "verified" or if the GT needs adjustment for that one fixture

### Finding A4-3: Alfiyyah plain text correctly flagged
Score = 0.647 (just below 0.65) due to `text_fidelity: medium` (0.60 for plain text). This is correct — plain text without structural markup or provenance should be treated with more caution.

---

## Decisions needed before Phase 1

1. **A3 substring boost:** Implement and retest? Or defer to build phase?
2. **A4 approach:** Which option (A/B/C) for trust calibration? This affects the ground truth and therefore all scoring.
3. **Ground truth fixtures 01, 02, 04, 08:** Adjust to "verified" or keep "flagged" and fix the algorithm?
