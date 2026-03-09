# Owner Sanity Check — Source Engine Core SPEC

**Purpose:** Experiential review. You're not checking technical correctness — you're checking "does this match the books I actually use?"

**Time needed:** 15-20 minutes. Answer each question with: ✓ (looks right), ✗ (something's wrong), or ? (not sure). For ✗ answers, describe what's wrong.

---

## §4.A.3 — Shamela HTML Extraction

**Q1-Q3: ANSWERED EMPIRICALLY.** The owner provided 2,519 real Shamela exports. A structural survey of all 2,519 files answered these questions definitively. The results are in `reference/SHAMELA_FORMAT_ANALYSIS.md` and the SPEC extraction rules have been rewritten accordingly. No owner input needed on these questions.

Key findings: No `info.html` file. Metadata uses `<span class='title'>` pattern, not `<table>`. No `class="matn"` / `class="sharh"` CSS classes. See the full analysis for details.

---

## §4.A.4 — Genre and Science Classification

**Q4: Does the genre list cover your library?**
The 18 genres are: matn, sharh, hashiyah, mukhtasar, nazm, risalah, taqrirat, mawsuah, fatawa, mujam, tabaqat, fiqh_comparative, hadith_collection, tafsir, sirah, tarikh, adab, other. Is there a genre you use frequently that's missing?

**Q5: Is "commentary" the right structural_format for a sharh?**
When a sharh like شرح ابن عقيل quotes the matn verses and then explains them, the SPEC classifies the structural format as `commentary`. Does this feel right? The alternatives are `prose`, `verse`, `mixed`.

---

## §4.A.8 — Trustworthiness

**Q6: Do you recognize these muhaqiqs as trusted editors?**
The recognized muhaqiq list is: شعيب الأرناؤوط، أحمد شاكر، عبد السلام هارون، عبد الله التركي، محمد فؤاد عبد الباقي، عبد القادر الأرناؤوط، محمد ناصر الدين الألباني، محمد محيي الدين عبد الحميد. Would you add or remove anyone?

**Q7: Do you recognize these publishers as scholarly?**
دار الرسالة, مؤسسة الرسالة, دار التراث, دار الكتب العلمية, المكتب الإسلامي, دار ابن حزم, دار ابن الجوزي. Would you add or remove any?

**Q8: Does the trust scoring make sense for your books?**
A source like شرح ابن عقيل (classical author + recognized muhaqiq + known publisher + Shamela HTML) scores 0.86 → verified. A source like "ملخص النحو الميسر" (unknown modern author + no muhaqiq + unknown publisher + photos) would score ~0.30 → flagged. Do these outcomes feel right?

---

## §4.A.9 — Work Relationships

**Q9: Are the relationship types complete for your library?**
The 7 types are: sharh_of, hashiyah_on, mukhtasar_of, nazm_of, taqrirat_on, responds_to, cites. For the books you plan to add, is there a relationship type that's missing?

---

## General

**Q10: Is plain text a useful second format for Stage 1?**
Besides Shamela HTML, the core supports plain text (.txt) files. Your alfiyyah_versified fixture is a plain text file. Will you actually use plain text intake for any real study sources, or would a different format (like PDF) be more useful as the second core format?

---

Return this file with your answers. Any ✗ answer becomes a SPEC comment to investigate.
