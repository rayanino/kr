# Gemini Evaluation: Taysir al-'Alam Excerpts

## Overview
- **Source:** تيسير العلام شرح عمدة الأحكام (Taysir al-'Alam Sharh 'Umdat al-Ahkam)
- **Author:** عبد الله البسام (Abdullah al-Bassam)
- **School:** Hanbali (Modern)
- **Total Excerpts reviewed:** 28

## Detailed Evaluation

### 1. Functional Classification (primary_function)
Most excerpts were classified correctly, especially `evidence_hadith` and `definition`. However, there were some inconsistencies in summarizing sections:
- **Successes:** Correct identification of `definition` for "غريب الحديث" and `opinion_statement` for "اختلاف العلماء".
- **Errors:** 
    - `exc_src_test0001_div_src_test0001_6_000_0_8`: Classified as `condition_exception`. This is a "ما يؤخذ من الحديث" (Takeaways) section which is primarily a collection of `rule_statement`s.
    - `exc_src_test0001_div_src_test0001_7_000_0_5`: Classified as `evidence_rational`. "المعنى الإجمالي" (General Meaning) is typically an `opinion_statement` or `rule_statement` summary, not a logical proof.

### 2. Self-Containment (self_containment)
High accuracy in identifying `PARTIAL` vs `FULL`.
- **Success:** `exc_src_test0001_div_src_test0001_6_000_0_0` correctly flagged as `PARTIAL` due to its nature as a numbered list of "additional" benefits following a prior context.
- **Success:** `exc_src_test0001_div_src_test0001_6_000_0_4` (Hadith text only) correctly flagged as `PARTIAL`.

### 3. School Attribution (school)
The system generally identifies `cross_school` when multiple Imams are mentioned, but misses sectarian comparative contexts.
- **Error:** `exc_src_test0001_div_src_test0001_6_000_0_3` mentions "شذوذ الشيعة" (Shia deviation) vs "إجماع الأمة" (Consensus of the Ummah). This should be flagged as `cross_school` or a sectarian attribute, not `null`.
- **Note:** `exc_src_test0001_div_src_test0001_7_000_0_8` was correctly flagged as `حنبلي` (Hanbali) based on the specific legal tone/preference.

### 4. Scholar Resolution (quoted_scholars)
Excellent resolution of major figures:
- `ابن رجب` -> `عبد الرحمن بن أحمد بن رجب الحنبلي`
- `البيضاوي` -> `عبد الله بن عمر البيضاوي`
- `النووي` -> `يحيى بن شرف النووي`

---

## Prompt Fixes (Error Prevention Rules)

For every error class found, the following rules/examples should be added to the LLM prompt:

### Error Class: Rule Statement vs. Condition/Exception
- **Issue:** Classifying "Takeaways" (ما يؤخذ من الحديث) as narrow functions like `condition_exception`.
- **Prompt Fix:** "When a text block is introduced by 'ما يؤخذ من الحديث' or 'الفوائد المستنبطة' and consists of a list of derived legal or ethical points, its `primary_function` MUST be `rule_statement`, even if individual points contain conditional logic or exceptions."

### Error Class: General Meaning (المعنى الإجمالي)
- **Issue:** Classifying summaries as `evidence_rational`.
- **Prompt Fix:** "Sections titled 'المعنى الإجمالي' (General Meaning) are summaries of the primary text. Classify them as `opinion_statement` (if summarizing the author's view) or `rule_statement` (if summarizing the resulting rules). Use `evidence_rational` ONLY if the text is primarily a logical or philosophical argument for a specific ruling."

### Error Class: Sectarian/Comparative Attribution
- **Issue:** Missing `cross_school` attribution when sects or 'the Ummah' are mentioned.
- **Prompt Fix:** "If the text contrasts the majority Sunni consensus ('جماهير الأمة', 'إجماع') with other sects (e.g., 'الشيعة', 'الخوارج', 'المعتزلة') or lists the 'four schools' vs a single outlier, always classify the `school` as `cross_school`."

### Error Class: Linguistic vs. Legal Definition
- **Issue:** Classification of grammatical/syntactic explanation.
- **Prompt Fix:** "Explanations of sentence structure (e.g., 'جملة شرطية', 'جواب الشرط') or the meaning of particles (e.g., 'إنما تفيد الحصر') should be classified as `definition` (Linguistic), with `secondary_functions` including `example` if a specific case is used to illustrate the rule."

---
*Evaluation completed on: 2026-03-31*
