# Gemini Analysis & Advice: Campaign 20260331

Based on my analysis of the 2,303 excerpts from the campaign_20260331 run, here is my expert advice on the scholarly quality and future strategy for this dataset.

### 1. SCHOLARLY QUALITY: Full-Book vs. Smoke Test
The full-book run demonstrates a significant leap in **functional awareness** compared to standard chunk-based extraction.
*   **Contextual Intelligence:** Unlike the smoke test which often cut mid-paragraph, this run successfully identifies structural markers like "الحديث الأول" or "المعنى الإجمالي" as natural boundaries.
*   **Self-Containment Logic:** The use of `PARTIAL` self-containment with `context_hint` (seen in *Taysir* and *ext_39*) is superior. It acknowledges that a "General Meaning" (Ma'na Ijmali) unit inherently depends on the preceding "Hadith Text" unit, rather than forcing them into a single, oversized excerpt.
*   **Result:** The full-book run produces **atomized scholarly units** that are ready for study, whereas the smoke test produced **fragments**.

### 2. GOLD STANDARD SELECTION: Genre-Specific Criteria
A "perfect" excerpt must respect the unique logic of its genre:

*   **Fiqh Sharh (Taysir):**
    *   **Criteria:** Must isolate the **Hadith Matn** (text) from the **Sharh** (commentary). A gold Hadith commentary excerpt should include the full *Isnad* (chain) starting from the Sahabi (e.g., "عن عبد الله بن عمر...") and end exactly where the author starts the linguistic or legal analysis ("المعنى الإجمالي" or "الإعراب").
*   **Nahw Sharh (Ibn Aqil):**
    *   **Criteria:** Must clearly distinguish between the **Alfiyyah Verse** (Matn) and the **Explanation**. A gold grammar excerpt should capture one complete rule or concept. If Ibn Aqil says "يعني أن..." (meaning that...), the excerpt must include the verse it is explaining to be functionally useful.
*   **Fiqh Masala (ext_39):**
    *   **Criteria:** **Discrete Rulings.** A gold numbered ruling must be a single *Mas'ala*. It should start with the number/title (e.g., "2 - وينبغي عليه...") and include the immediate evidence (Hadith or Ayah) cited for that specific ruling.

### 3. REVIEW STRATEGY: Focus for the Student-Reviewer
Since the owner is a student, he should act as a "Scholarly Quality Controller":

*   **Focus ON:**
    1.  **Functional Mismatch:** Did the LLM call a Hadith a "Definition"? (High taxonomy impact).
    2.  **Boundary Bleed:** Does a "General Meaning" excerpt accidentally start with the last sentence of the Hadith text?
    3.  **Description Accuracy:** Does the `description_arabic` accurately summarize the *content*, or is it just a generic template?
*   **IGNORE:**
    1.  **Technical IDs:** Don't waste time on `excerpt_id` or `chunk_index`.
    2.  **Metadata Confidence:** "Confidence: 0.95" is for developers; the student should only judge the text.

### 4. ARABIC FIDELITY: Automated Checks
With >2,000 excerpts, we must automate these "Sacred Text" integrity checks:
*   **Honorific Completeness:** Flag any mention of "النبي" or "محمد" that lacks the "صلى الله عليه وسلم" (Sallallahu Alayhi wa Sallam) or uses a broken abbreviation (like "صلعم").
*   **Quranic Bracketing:** Ensure Ayahs are consistently enclosed in `{}` or `⌜⌝` as per the source style, and that brackets are not left open.
*   **Isnad Atomicity:** In Hadith texts, verify the "عن" (From...) chain isn't truncated mid-name (e.g., "عن عبد الله بن" without "عمر").
*   **Diacritic Consistency:** Matn (original text) should be fully vocalized (tashkeel), while Sharh (commentary) can be partial. Inconsistencies here indicate a "source layer" mismatch.

### 5. TAXONOMY READINESS: Critical Risks
The taxonomy engine relies heavily on the `primary_function` and `excerpt_topic`.
*   **The "Structural Transition" Trap:** If an excerpt is labeled as `structural_transition` but contains a vital ruling, it will be "hidden" in the taxonomy.
*   **Generic Topics:** Excerpts with topics like "كتاب الطلاق" (The Book of Divorce) are too broad. They must be as specific as "تعريف الطلاق لغةً" (Linguistic definition of divorce) to be placed correctly in a deep taxonomy.
*   **Function Confusion:** Mislabeling "Evidence" (Hadith) as "Editorial Note" will prevent the system from linking it to the *Takhrij* engine, breaking the "Evidence-to-Rule" knowledge graph.

---
*Analysis completed by Gemini CLI - March 31, 2026*
