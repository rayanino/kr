# Gate Abort Deep Dive

**Date:** 2026-03-22
**Total gate aborts:** 67 across 3 phases
**Cost of aborted processing:** 6.7 EUR

## Overview by Phase

| Phase | Gate Aborts | Total Books | Abort Rate |
|-------|-----------|-------------|------------|
| phase_c | 51 | 73 | 70% |
| phase_d | 0 | 204 | 0% |
| phase_e | 16 | 70 | 23% |

## Gate Abort Reasons (Grouped)

### science_scope_mismatch (66 books)

**Phases:** phase_c: 50, phase_e: 16

**Has author in extraction:** 66/66

**Sample errors:**
- Author's known sciences {'primary'} don't overlap with source sciences {'adab', 'tasawwuf'}
- Author's known sciences {'primary'} don't overlap with source sciences {'fiqh', 'usul_al_fiqh'}
- Author's known sciences {'primary'} don't overlap with source sciences {'sarf', 'lughah'}
- Author's known sciences {'primary'} don't overlap with source sciences {'ulum_al_hadith', 'hadith'}

**Books:**
- [phase_c] آداب الصحبة لأبي عبد الرحمن السلمي (author: محمد بن الحسين بن محمد بن موسى)
- [phase_c] آداب الفتوى والمفتي والمستفتي (author: أبو زكريا يحيى بن شرف النووي ()
- [phase_c] أبنية الأسماء والأفعال والمصادر (author: ابن القَطَّاع الصقلي (ت 515 هـ)
- [phase_c] أحاديث أيوب السختيانى (author: القاضي أبو إسحاق إسماعيل بن إس)
- [phase_c] أحاديث العطار عن شيوخه (author: محمد بن الحسن بن يعقوب بن الحس)
- [phase_c] أخبار أبي القاسم الزجاجي (author: عبد الرحمن بن إسحاق البغدادي ا)
- [phase_c] أدب النفوس للآجري (author: أبو بكر محمد بن الحسين بن عبد )
- [phase_c] أعلام الموقعين عن رب العالمين - ط عطاءات العلم (author: أبو عبد الله محمد بن أبي بكر ب)
- [phase_c] ألفية ابن مالك - ط التعاون (author: محمد بن عبد الله، ابن مالك الط)
- [phase_c] أمالي المحاملي رواية ابن الصلت (author: أبو عبد الله البغدادي الحسين ب)
- [phase_c] أنوار الهلالين في التعقبات على الجلالين (author: محمد بن عبد الرحمن الخميس)
- [phase_c] إعلام الموقعين عن رب العالمين - ت مشهور (author: أبو عبد الله محمد بن أبي بكر ب)
- [phase_c] إعلام الموقعين عن رب العالمين - ط العلمية (author: محمد بن أبي بكر بن أيوب بن سعد)
- [phase_c] الأذكار للنووي ت الأرنؤوط (author: أبو زكريا محيي الدين يحيى بن ش)
- [phase_c] الأربعون النووية (author: أبو زكريا محيي الدين يحيى بن ش)
- ... and 51 more

### is_multi_layer=true but text_layers is empty — cannot determ (1 books)

**Phases:** phase_c: 1

**Has author in extraction:** 1/1

**Sample errors:**
- is_multi_layer=true but text_layers is empty — cannot determine layer attribution (T-2 prevention)

**Books:**
- [phase_c] النكت على شرح النووي على صحيح مسلم (author: د هاني فقيه)

## Analysis: Is the Gate Correct?

### Science Scope Mismatch
**66 books** failed because the LLM-inferred 
science scope doesn't overlap with the scholar's known sciences in the authority DB.

This is the **correct behavior** — the gate catches cases where the LLM may have 
misidentified the science or where the scholar authority record is incomplete. 
These books need human review to determine which is correct.

### Threshold Adjustment Candidates

Books where extraction data is rich but gate still triggers are candidates for 
threshold tuning. Currently, the gate is conservative (any validation issue 
triggers abort). Possible improvements:

1. **Distinguish hard vs soft gate errors** — science scope mismatch could be soft
2. **Author matching confidence** — books with high-confidence author matches could bypass some checks
3. **Phase C had 70% abort rate** — the earliest probes hit the most obscure books
