# Session C Preparation Plan

**Purpose:** Ensure zero-error evaluation of 15 structural flag books.
**Lesson from Session B:** 9 errors found across 19 verdicts (47% error rate before correction). Root causes: memory-based transcription (4 errors), insufficient research (1 critical), unchecked claims against data (2), arithmetic (2). This plan eliminates each root cause.

---

## Error Prevention Rules

### RULE 1: No memory-based transcription — EVER.
Every field value in a verdict must be copy-pasted from `session_c_extract.py` output or from a tool call in the SAME message. If the output scrolled past, re-run the extraction. Never write a number, name, or classification from memory.

### RULE 2: Web search + web_fetch BEFORE writing any verdict.
Minimum per book: 1 search + 1 successful fetch. If fetch fails, try another URL. If no URL works, document the failure explicitly. Never write "search confirms" without an actual search result visible in the conversation.

### RULE 3: Verify verdict against data IMMEDIATELY after writing.
After writing each verdict, run `session_c_extract.py` on that book and compare every field. Fix any mismatch before moving to the next book. This is not optional.

### RULE 4: Cross-check counts after every 5 books.
Count VERIFIED/PLAUSIBLE/FLAG/ESCALATE and compare against the sum of individual verdicts. Fix any arithmetic error immediately.

### RULE 5: For research claims, search for CONTRADICTING evidence.
Before asserting "X is the genre" or "X is correct," search for evidence that X might be wrong. The ابن العربي error happened because I searched for the famous scholars but not for descendants. For every classical book, search for the specific claim, not just the general topic.

---

## Book Categories and Investigation Plans

### Type 1: Genre + ML structural investigation (3 books)
**These are the hardest books. Web research determines the verdict.**

| Book | Issue | Investigation needed |
|------|-------|---------------------|
| 1. أمالي الأذكار | sharh vs hadith_collection, ML=True | Is this genuinely a sharh with embedded matn, or a standalone hadith collection? Search for the work's structure. |
| 11. النكت على شرح النووي | ERR-01: hashiyah + ML=False | Is this actually a hashiyah (3-layer), or something else? Title says "notes on النووي's sharh" which could be hashiyah or risalah. |
| 12. تفسير ابن كمال باشا | tafsir + ML=False | Is this a full multi-layer tafsir (Quran + commentary), or partial/specialized? Search for the work's scope. |

### Type 2: ML disagreement — BUG-03 override (5 books)
**Verify the override fired correctly. Check if Opus's ML=True was tahqiq-based.**

| Book | Opus ML | CA ML | Pipeline ML | Task |
|------|---------|-------|-------------|------|
| 4. الأدب المفرد | True | False | False | Verify ML=False is correct. Is this a standalone hadith collection? |
| 7. الرسالة للشافعي | True | False | False | Phase C VERIFIED book — confirm BUG-03 fix improved result |
| 9. القسم الثالث المعجم الأوسط | True | False | False | Also has genre disagree (mujam vs hadith_collection) |
| 14. مختصر صحيح مسلم | True | False | False | Phase C book — confirm BUG-03 fix |
| 15. مسند أحمد | True | False | False | Phase C book — confirm BUG-03 fix |

### Type 3: Genre disagreement, non-ML-affecting (1 book)
| Book | Issue | Task |
|------|-------|------|
| 2. إعلام الموقعين ط العلمية | other vs usul_al_fiqh | This is the edition group inconsistency from Layer 2. Verify against Session A verdict for the other editions. |

### Type 4: Disputed attribution (2 books)
| Book | Issue | Task |
|------|-------|------|
| 5. الإبانة العصيمي | Opus: disputed, CA: definitive | الإبانة عن أصول الديانة attributed to الأشعري — genuinely disputed in scholarship. Research the dispute. |
| 6. الإبانة فوقية | Same pattern | Same work, different tahqiq. Compare with book 5. |

### Type 5: Layer verification (3 books)
**Both models agree ML=True. Verify the layers are genuine scholarly layers, not tahqiq notes.**

| Book | Layers | Task |
|------|--------|------|
| 3. الأحاديث الأربعين | matn (النووي) + sharh (?) | Verify: who wrote the sharh? The title mentions ابن رجب additions + "الشرح الموجز المفيد" |
| 8. الروضة الندية | matn (الشوكاني) + sharh (?) | Verify: this is a known sharh of الدرر البهية. Who is the sharih? |
| 13. شرح المفصل لابن يعيش | matn (الزمخشري) + sharh (ابن يعيش) | Famous work — easy to verify. |

### Type 6: Unknown reason for inclusion (1 book)
| Book | Issue | Task |
|------|-------|------|
| 10. المسائل النحوية | No structural flags detected | Investigate why it's in Session C. May be a title-genre mismatch or new ML book needing verification. |

---

## Session Workflow

1. **Pre-load:** Run `session_c_extract.py --all` at the start. Save output.
2. **Per book:** 
   a. Re-run `session_c_extract.py "book"` (get current data)
   b. Read the COPY-PASTE BLOCK and STRUCTURAL FLAGS
   c. Web search (per investigation plan above)
   d. Web fetch at least 1 URL
   e. Write verdict using COPY-PASTE BLOCK as skeleton
   f. **IMMEDIATELY** re-run `session_c_extract.py "book"` and compare every field
   g. Fix any mismatch
3. **Every 5 books:** Count verdicts. Compare sum.
4. **After all 15:** Full self-review with systematic data verification (same as the critical review that caught errors 6-9 in Session B).

---

## Key Reminders from Session B Errata + Session A Errata

- web_fetch is MANDATORY (ERRATA-01)
- Never fabricate sources (ERRATA-02)
- Death date labels must be precise: pass-through vs extracted-from-raw vs inferred (ERRATA-03)
- Self-review must use tools (ERRATA-04)
- Mark speculation as speculation (ERRATA-05)
- Check prompt_sent.json (ERRATA-06)
- Check pipeline-genre-matches-neither-model (ERRATA-07)
- Never confuse result.json values with Opus values (Session B Error 7)
- Never write muhaqiq or author values from wrong books (Session B Error 1)
- For classical books, search for descendants/variants, not just famous namesakes (Session B Error 4)
- Always verify trust_tier from result.json, never assume (Session B Error 6)
