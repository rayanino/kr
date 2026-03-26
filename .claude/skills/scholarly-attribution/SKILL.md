---
name: scholarly-attribution
description: How to identify, verify, and disambiguate author attributions in Islamic scholarly texts. Use when processing author metadata, verifying attribution claims, implementing scholar matching, or evaluating LLM author identification outputs.
---

# Scholarly Attribution Heuristics

Incorrect author attribution is threat T-2 — one of the most dangerous knowledge integrity failures. An error here means the owner's mental model attributes ideas to the wrong scholar. This skill provides the heuristics needed to identify, verify, and disambiguate authorship.

---

## 1. Arabic Naming Convention Structure

A full scholarly name follows this pattern (not all elements present in every reference):

```
كنية (Kunyah)  +  اسم (Ism)  +  نسب (Nasab)  +  لقب (Laqab)  +  نسبة (Nisba)
أبو عبد الله      محمد         بن إسماعيل      —               البخاري
```

### Components

| Component | Arabic | Function | Example | KR Implication |
|-----------|--------|----------|---------|----------------|
| **اسم (Ism)** | First name | Given name | محمد, أحمد, عبد الله | Not unique — thousands of scholars share common isms |
| **نسب (Nasab)** | بن/ابن chain | Patronymic | بن إسماعيل بن إبراهيم | Best disambiguator when complete — unique genealogy |
| **كنية (Kunyah)** | أبو/أم + name | Honorific father/mother name | أبو عبد الله, أبو حنيفة | Often the most commonly used identifier |
| **لقب (Laqab)** | Title/epithet | Descriptive title | شيخ الإسلام, إمام الحرمين | DANGEROUS — multiple scholars share laqabs |
| **نسبة (Nisba)** | Relational adjective | Geographic/tribal/school | البخاري, الشافعي, البغدادي | Strong disambiguator when combined with era |

### Disambiguation Priority

When matching a name to a known scholar, use this hierarchy:
1. **Nasab chain (4+ generations)** — nearly unique
2. **Nisba + death date** — strong disambiguation
3. **Kunyah + nisba** — moderate disambiguation
4. **Full name (ism + nasab + nisba)** — strong
5. **Ism + laqab** — WEAK — many scholars share this pattern
6. **Ism alone** — USELESS for disambiguation — never match on ism alone

### DANGER: Common Shared Names

These names are shared by multiple prominent scholars. ALWAYS require additional disambiguation:

| Name | Scholars Who Share It | Disambiguation |
|------|----------------------|----------------|
| **ابن حجر** | العسقلاني (d.852), الهيتمي (d.974) | Era + nisba + works |
| **ابن قدامة** | صاحب المغني (d.620), صاحب الشرح الكبير (d.682) | Works + nasab |
| **ابن تيمية** | المجد (d.652), الحفيد شيخ الإسلام (d.728) | Laqab + era |
| **ابن القيم** | ابن قيم الجوزية (d.751) is usually intended, but verify | Works cited |
| **النووي** | يحيى بن شرف (d.676) is usually intended | Almost always unambiguous, but verify era |
| **ابن كثير** | المفسر (d.774) vs المقرئ (d.738) | Works + field |
| **ابن عبد البر** | القرطبي (d.463) — usually unambiguous | Verify era |
| **السيوطي** | جلال الدين (d.911) — usually unambiguous | Verify |

---

## 2. Author Signal Locations in Text

### Signal Reliability Hierarchy (highest → lowest)

| Location | Reliability | Why | What to Extract |
|----------|------------|-----|-----------------|
| **Colophon (خاتمة/التتمة)** | HIGHEST | Author's own statement of completion | Name, date of completion, place |
| **Author's introduction (مقدمة المؤلف)** | HIGH | First-person declaration "أنا فلان..." or "قال المصنف" | Full name, purpose, date |
| **Isnad of the text** | HIGH (for hadith works) | Chain of transmission back to author | Author at end of chain |
| **Title page (if from manuscript)** | MODERATE | Added by scribes, can be wrong | Cross-check with introduction |
| **Shamela metadata** | LOW-MODERATE | Shamela editors sometimes err | Always cross-check against text content |
| **External bibliographies** | MODERATE | Compiled independently | Death dates, works lists |
| **Content inference by LLM** | LOW | Inference from style/terminology | NEVER trust alone — use for hypothesis, verify externally |

### Extraction Patterns

**Colophon patterns** (look at last 2-3 pages):
- `تم الكتاب بحمد الله` / `فرغ من تأليفه` / `وكان الفراغ منه`
- `على يد` (scribe attribution — NOT author)
- `كتبه` + name (may be author OR scribe — disambiguate from context)
- `في شهر [month] سنة [year]` — composition or copy date

**Introduction patterns** (look at first 3-5 pages):
- `أما بعد فيقول العبد الفقير` + name — author declaration
- `قال الشيخ الإمام` + name — editorial attribution (lower reliability)
- `سألني` / `طلب مني` — commissioning context (identifies audience, not author)
- `هذا كتاب` + title + `ألفه` / `صنفه` + name

**Shamela HTML patterns**:
- `<div class="nass">المؤلف: [name]</div>` — check but verify
- Author name in URL path or database ID — very low reliability

---

## 3. Multi-Author Scenarios

### Commentary Attribution
In a multi-layer text (matn + sharh + hashiyah):
- **Each layer has a different author.** The sharh author is NOT the matn author.
- The matn text is typically quoted in a distinctive style (often smaller font, or preceded by "قال المصنف")
- The sharh author's voice is the main narrative
- Attribution must track which author said what

### Compilation vs. Authorship
- **Compiler (جامع/مصنف)**: Selected and organized others' content. Example: البخاري compiled hadith.
- **Author (مؤلف)**: Wrote original content. Example: الغزالي wrote إحياء علوم الدين.
- **Editor (محقق)**: Modern critical edition editor. NOT the author. Track separately.
- **Scribe (ناسخ)**: Copied the manuscript. NOT the author. Track separately.
- **Annotator (معلق)**: Added footnotes to someone else's text. Separate layer.

### KR Pipeline Handling
- `author`: the primary intellectual author/compiler
- `editor`: the tahqiq editor (modern, separate field)
- `related_scholars`: others mentioned (matn author if this is sharh, etc.)
- NEVER merge compiler and author attributions

---

## 4. Death Date Verification

Death dates are the single most powerful disambiguator. Two scholars rarely share both name AND death date.

### Death Date Signal Sources

| Source | Format | Reliability | Notes |
|--------|--------|-------------|-------|
| Text colophon | Hijri year | HIGH | Author's own dating |
| Biographical dictionaries (tabaqat) | Hijri year, sometimes exact date | HIGH | Independent source |
| Shamela metadata | Hijri year | MODERATE | Cross-check |
| LLM inference | Hijri year | LOW | Must verify externally |
| Usul.ai | Hijri year | HIGH | 15,000+ scholars |

### Verification Heuristic
1. Extract death date from LLM output
2. Compare against extraction metadata (Shamela)
3. If they MATCH: suspicious — LLM may have parroted extraction, not independently verified (M-4 methodology rule)
4. If they DIFFER: investigate both. If extraction has no date but LLM provides one → genuine inference, verify via web search
5. Cross-check: the death date must be PLAUSIBLE given the text's content (a text referencing events in 800 AH cannot be by an author who died in 600 AH)

### Era Plausibility Checks
- Content references to specific events/scholars provide a terminus post quem
- Madhab references: a text following late Hanafi terminology post-dates ~4th century AH
- Language style: classical vs. late medieval vs. modern Arabic differ noticeably
- If death date contradicts content-implied era → FLAG for human review

---

## 5. Confidence Scoring

### Confidence Levels for Attribution

| Level | Threshold | Criteria | KR Action |
|-------|-----------|----------|-----------|
| **CONFIRMED** | ≥0.95 | 2+ independent sources agree on full name + death date | Accept |
| **STRONG** | 0.80-0.94 | 1 reliable source (colophon/introduction) + era plausibility | Accept with note |
| **MODERATE** | 0.60-0.79 | Shamela metadata matches LLM inference, no contradictions | Accept, flag for verification |
| **WEAK** | 0.40-0.59 | Name match only, no death date or era verification | Human gate |
| **UNCERTAIN** | <0.40 | Conflicting sources, or inference only | Human gate, mark unverified |

### Name-Only Match Cap
Per KR decision: **name-only matches are capped at confidence 0.65.** This prevents auto-linking a text to a scholar based solely on a shared name without additional evidence (death date, works list, or biographical confirmation).

---

## 6. Common Attribution Errors

### Error: Confusing Tahqiq Editor with Author
**Pattern:** Shamela metadata lists the tahqiq editor (محقق) as the author.
**Detection:** Author death date is modern (post-1350 AH) but text content is clearly classical.
**Fix:** The modern name is the editor. Search the introduction for the original author.

### Error: Attributing Compilation to Compiler's Source
**Pattern:** A mukhtasar (abridgment) is attributed to the original author instead of the abridger.
**Detection:** Text structure is condensed; references "the original" or "the author said."
**Fix:** The mukhtasar author is the abridger. Add `mukhtasar_of` reference to original.

### Error: Confusing Namesakes Across Centuries
**Pattern:** ابن حجر attributed to d.852 when the text is actually by ابن حجر الهيتمي d.974.
**Detection:** Content discusses Shafi'i fiqh in a late style → likely الهيتمي. Hadith commentary → likely العسقلاني.
**Fix:** Use science + era + works list for disambiguation.

### Error: Anonymous Works
**Pattern:** No author identified in text or metadata.
**Detection:** Introduction uses passive voice ("جُمع هذا الكتاب"), no colophon attribution.
**Fix:** Mark as `attribution_status: "unattributed"`, confidence 0.0. Do NOT assign an author by inference — flag for human research.
