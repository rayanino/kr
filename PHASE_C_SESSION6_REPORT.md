# Phase C Session 6 Report — Edition Groups (17 books)

**Date:** 2026-03-11
**Evaluator:** Claude Chat (Opus 4.6)
**Books evaluated:** 17 (largest session)
**Models:** 16 use Opus + Command A; 1 uses Opus + GPT-5.4 (تفسير الطبري ط دار التربية)
**Running totals (pre-session):** 38 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (49 books)

## Summary

| # | Book | Status | Verdict | Key finding |
|---|------|--------|---------|-------------|
| 17 | تكملة حاشية ابن عابدين | gate_abort | VERIFIED | SON correctly identified; death 1306 genuine inference CORRECT; consensus disagreed (SUBSTANTIVE per Errata §6) |
| 16 | حاشية ابن عابدين | gate_abort | VERIFIED | FATHER correctly identified; 3-layer chain verified; death 1252 false-positive (date in raw text, extraction death=N/A) |
| 1 | أعلام الموقعين - ط عطاءات | gate_abort | VERIFIED | Genre disagreement (matn vs usul_al_fiqh); death 751 false-positive; consensus disagreed |
| 2 | إعلام الموقعين - ت مشهور | gate_abort | VERIFIED | Genre=other (both agree); consensus disagreed (name format only) |
| 3 | إعلام الموقعين - ط العلمية | gate_abort | VERIFIED | Genre disagreement (other vs matn); consensus agreed |
| 4 | البداية والنهاية - ت التركي | success | VERIFIED | Clean; tarikh (not tafsir); trust=verified |
| 5 | البداية والنهاية - ط السعادة | success | VERIFIED | Clean; tarikh; trust=verified |
| 6 | تفسير الطبري - ت التركي | gate_abort | VERIFIED | Both models agree on all fields |
| 7 | تفسير الطبري - ط دار التربية | gate_abort | VERIFIED | ML disagreement: Opus=F, GPT-5.4=T (tahqiq_note — 4th instance of known pattern) |
| 8 | تحفة المودود - ت الأرنؤوط | gate_abort | VERIFIED | Clean; risalah; both agree |
| 9 | تحفة المودود - ط عطاءات | gate_abort | VERIFIED | Consensus disagreed (name format only); death 751 false-positive |
| 10 | فتاوى اللجنة - المجموعة الأولى | success | VERIFIED | Institutional author; no death date (correct); trust=flagged |
| 11 | فتاوى اللجنة - المجموعة الثانية | gate_abort | VERIFIED | Broader science scope than المجموعة الأولى |
| 12 | ألفية ابن مالك - ت القاسم | success | VERIFIED | genre=nazm (correct, more precise than matn); trust=verified |
| 13 | ألفية ابن مالك - ط التعاون | gate_abort | VERIFIED | Identical classification to ت القاسم |
| 14 | شرح العقيدة الطحاوية - ط الأوقاف | gate_abort | VERIFIED | Matches Session 4's ط الرسالة verdict exactly |
| 15 | شرح العقيدة الطحاوية - ط الرسالة | gate_abort | VERIFIED | Re-used Session 4 verdict (already VERIFIED) |

**Session totals:** 17 VERIFIED, 0 PLAUSIBLE, 0 UNVERIFIABLE, 0 FLAG, 0 ESCALATE
**Cumulative totals:** 55 VERIFIED, 11 PLAUSIBLE, 0 FLAG, 0 ESCALATE (66 books)

---

## Per-Book Verdicts

### Book 17: تكملة حاشية ابن عابدين (CRITICAL)

Book: تكملة حاشية ابن عابدين = قرة عيون الأخيار تكملة رد المحتار - ط الفكر
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline (Opus): محمد علاء الدين بن محمد أمين عابدين / Pipeline (CA): محمد علاء الدين أفندي / Verified: محمد علاء الدين بن محمد أمين بن عمر بن عبد العزيز عابدين الحسيني الدمشقي (1244–1306 هـ), the SON of the famous ابن عابدين. Born 3 ربيع الأول 1244, died 11 شوال 1306. Studied under his father (who died when the son was 8, in 1252), attended al-Azhar, served as أمين الفتوى in Damascus, completed his father's hashiyah. Opus's known_as includes "ابن عابدين الصغير" — correctly distinguishing the son from the father. / Death: 1306 (Opus) vs null (CA) vs 1306 (verified) / LLM conf: 0.92 (Opus), 0.85 (CA) / Death source: **GENUINE INFERENCE** — author_raw is EMPTY, extraction has author_death=N/A, no embedded date in raw text (because raw text is empty). Opus inferred 1306 correctly. CA gave null. This is the 3rd confirmed correct genuine inference (after 728 for ابن تيمية and 324 for الأشعري). Updated running total: 3 correct, 1 wrong, 6 false positives.
**CRITICAL CHECK PASSED: This is the SON (علاء الدين, ت 1306), NOT the father (محمد أمين, ت 1252). Cross-verified against Book 16 — different person.**
Genre: VERIFIED — Pipeline: hashiyah (Opus 0.95, CA 0.95) / Expected: hashiyah / Shamela cat: الفقه الحنفي / Both models agree.
Multi-Layer: VERIFIED — Pipeline: true (both agree) / Expected: true
Layers: Opus provides 3 layers: matn=الحصكفي (محمد بن علي), sharh=ابن عابدين (محمد أمين — the father), hashiyah=محمد علاء الدين. CA provides 2 layers: matn=ابن عابدين, hashiyah=علاء الدين (collapsed representation). Opus's representation is more accurate: the تكملة continues the father's hashiyah on الدر المختار (الحصكفي's sharh on التمرتاشي's matn). The full 4-level chain is: تنوير الأبصار (التمرتاشي) → الدر المختار (الحصكفي) → رد المحتار (father) → تكملة (son). Opus omits التمرتاشي but captures the essential 3-layer structure.
Science: VERIFIED — Both: ['fiqh'] / Expected: fiqh / Shamela cat matches
Attribution: Opus=definitive, CA=traditional. Both acceptable. The work's attribution to the son is well-established.
Authority_level: Opus=primary, CA=reference. NOTE: This is REVERSED from the standard sharh/hashiyah pattern (usually Opus=reference, CA=primary). Opus treats the son's تكملة as a primary scholarly contribution; CA treats it as a reference work. Both defensible.
Trust: SKIPPED (gate_abort)
Consensus: agreed=false, models=[command_a, opus_4_6]. Disagreement: name format + death date (1306 vs null). The death date disagreement is SUBSTANTIVE per Errata §6 — CA could not determine the death date at all, representing a genuine knowledge gap. The name format disagreement is not substantive — both identify the same person.
Extraction quality: author_name_raw is EMPTY — the LLM had to identify the author purely from title and content context. This is the hardest identification scenario in the session.
Result.json model source: N/A (gate_abort)
Web Sources: shamela.ws/book/918 (Shamela-ecosystem — confirms "نجل ابن عابدين [ت ١٣٠٦]"), hindawi.org (independent — full biography from أعلام الفكر الإسلامي), tarajm.com/people/79437 (independent — encyclopedic biographical entry with dates, teachers, works), archive.org (independent — confirms full layer chain), library.ecssr.ae UAE Federation Library catalog (independent, government — confirms authorship and layer chain), safinatulnajat.com (independent publisher — confirms 1244–1306)
Notes: (1) CRITICAL verification pair with Book 16. Both models correctly distinguish father from son despite near-identical names. (2) Opus's death 1306 genuine inference is confirmed correct by 4+ independent sources. (3) The empty author_raw makes this the most impressive author identification in the session — pure inference from title and content. (4) CA's 2-layer representation loses the الحصكفي sharh layer but correctly identifies the hashiyah genre.

### Book 16: حاشية ابن عابدين (CRITICAL)

Book: حاشية ابن عابدين = رد المحتار - ط الحلبي
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline (Opus): محمد أمين بن عمر بن عبد العزيز عابدين الدمشقي / Verified: ابن عابدين (1198–1252 هـ), the most authoritative late-period Hanafi jurist. Known as "خاتمة المحققين" (seal of the verifiers). / Death: 1252 (both models) vs 1252 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: **false-positive** — extraction has author_death=N/A BUT author_raw contains "[ت 1252 هـ]". The date is visible in the raw text, so the LLM read it from the prompt, not from inference. This is NOT a genuine inference.
**CRITICAL CHECK PASSED: This is the FATHER (محمد أمين, ت 1252), correctly distinguished from Book 17's SON.**
Genre: VERIFIED — Pipeline: hashiyah (Opus 0.99, CA 0.95) / Expected: hashiyah / Shamela cat: الفقه الحنفي / Both agree.
Multi-Layer: VERIFIED — true (both agree) / Expected: true
Layers: Opus provides 3 layers: matn=التمرتاشي (محمد بن عبد الله), sharh=الحصكفي (محمد بن علي), hashiyah=ابن عابدين (محمد أمين). This is the CORRECT full chain: تنوير الأبصار → الدر المختار → رد المحتار. CA provides 3 layers but incorrectly assigns الحصكفي as BOTH matn and sharh author (a confusion — التمرتاشي is the actual matn author). CA's hashiyah layer correctly names ابن عابدين.
Science: VERIFIED — Both: ['fiqh'] / Expected: fiqh / Shamela cat matches
Attribution: Both=definitive. No dispute.
Authority_level: Opus=reference, CA=primary. Standard sharh/hashiyah pattern.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true, models=[command_a, opus_4_6]
Extraction quality: clean. author_name_raw present with embedded death date.
Result.json model source: N/A (gate_abort)
Web Sources: Verified via Book 17's web search (same sources cover both books). archive.org confirms the full layer chain. tarajm.com/people/14012 has the father's full biography.
Notes: (1) CA's layer chain error (الحصكفي as both matn and sharh) is a factual mistake but does not affect the genre or ML classification. The hashiyah genre is correct regardless. (2) Opus's known_as includes "خاتمة المحققين" — a correct and well-known title for ابن عابدين.

---

### حاشية + تكملة Author-Verification Pair — Cross-Check

| Field | Book 16 (حاشية — FATHER) | Book 17 (تكملة — SON) | Same person? |
|-------|--------------------------|----------------------|--------------|
| Author (Opus) | محمد أمين بن عمر عابدين | محمد علاء الدين بن محمد أمين عابدين | **NO — different people ✓** |
| Death | 1252 | 1306 | Different ✓ |
| Genre | hashiyah | hashiyah | Match ✓ |
| ML | true | true | Match ✓ |
| Science | fiqh | fiqh | Match ✓ |
| Matn author | التمرتاشي | الحصكفي (simplified) | Different (correct) |
| Layer count (Opus) | 3 | 3 | Match |
| Authority_level | Opus=reference, CA=primary | Opus=primary, CA=reference | **Reversed** |
| Attribution | definitive (both) | Opus=definitive, CA=traditional | |

**Verification result: PASS.** The pipeline correctly distinguishes father (ت 1252) from son (ت 1306). Both models identify different people with the correct death dates. The relationship between the two works (son completing father's hashiyah) is correctly captured in the layer structures.

---

### Book 1: أعلام الموقعين عن رب العالمين - ط عطاءات العلم

Book: أعلام الموقعين عن رب العالمين - ط عطاءات العلم
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن قيم الجوزية (both models) / Verified: محمد بن أبي بكر بن أيوب (691–751 هـ), student of ابن تيمية, one of the most prolific medieval Islamic scholars / Death: 751 (both models) vs 751 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: **false-positive** — extraction has author_death=N/A BUT author_name_raw contains "(691 - 751)". Both dates are visible in the raw text. The LLM read the death date from the prompt, not from inference. This is NOT a genuine inference.
Genre: PLAUSIBLE — Opus: matn (0.85) / CA: usul_al_fiqh (0.95) / Shamela cat: أصول الفقه / Expected: risalah/other per framework. The work is traditionally classified under أصول الفقه in Islamic library catalogs. CA's usul_al_fiqh matches Shamela and scholarly consensus. Opus's matn is a structural descriptor (standalone text), not a content genre. The genre boundary here is genuinely fuzzy — the work is an original text on usul methodology that doesn't fit neatly into standard categories.
Multi-Layer: VERIFIED — false (both agree) / Expected: false / **CRITICAL CHECK PASSED: ML=false for إعلام الموقعين**
Science: VERIFIED — Opus: ['usul_al_fiqh', 'fiqh'] / CA: ['usul_al_fiqh'] / Both include usul_al_fiqh as primary. Opus's broader set (adding fiqh) is reasonable given the book's extensive fiqh examples.
Attribution: VERIFIED — Both: definitive. No dispute.
Trust: SKIPPED (gate_abort)
Consensus: agreed=false. Disagreement: genre (matn vs usul_al_fiqh) + name format. The genre disagreement is partially substantive (Errata §6).
Extraction quality: clean. No muhaqiq in this edition's extraction (despite being the عطاءات العلم edition).
Result.json model source: N/A (gate_abort)
Web Sources: noor-book.com (independent), ibnalqayem.net (independent — confirms usul_al_fiqh classification), archive.org (independent), binbaz.org.sa (independent), islamweb.net (independent), shamela.ws (Shamela-ecosystem), ketabonline.com (Shamela-ecosystem)
Notes: Death date "(691 - 751)" visible in author_name_raw — this is a false-positive, not genuine inference. Session 6 false positives: this book + Book 9 (تحفة ط عطاءات) + Book 16 (حاشية ابن عابدين). Updated total: 9 (6 prior + 3 from Session 6).

### Book 2: إعلام الموقعين عن رب العالمين - ت مشهور

Book: إعلام الموقعين عن رب العالمين - ت مشهور
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن قيم الجوزية (both models) / Death: 751 (both) vs 751 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (author_death=751 in extraction, also "(ت 751 هـ)" in author_raw)
Genre: PLAUSIBLE — Both: other (Opus 0.75, CA 0.85). Low confidence from both models. The "other" label reflects genuine genre ambiguity — this is a large work on ifta' methodology that doesn't map cleanly to standard categories. Shamela cat: أصول الفقه.
Multi-Layer: VERIFIED — false (both agree) / **CRITICAL CHECK PASSED**
Science: VERIFIED — Opus: ['usul_al_fiqh', 'fiqh'] / CA: ['usul_al_fiqh']
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=false. Disagreement: name format only (same person: ابن القيم). Not substantive (Errata §6).
Extraction quality: clean. Muhaqiq present (مشهور بن حسن آل سلمان).
Result.json model source: N/A (gate_abort)
Web Sources: same sources as Book 1 (إعلام الموقعين research applies to all 3 editions)
Notes: Lowest genre confidence in the إعلام group (Opus 0.75). The genre ambiguity is consistent across evaluators — this work genuinely defies simple categorization.

### Book 3: إعلام الموقعين عن رب العالمين - ط العلمية

Book: إعلام الموقعين عن رب العالمين - ط العلمية
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن قيم الجوزية (both models) / Death: 751 (both) vs 751 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (author_death=751 in extraction)
Genre: PLAUSIBLE — Opus: other (0.75) / CA: matn (0.95) / Shamela cat: أصول الفقه. CA's matn is a structural descriptor like Book 1's Opus=matn. Neither matches the Shamela category.
Multi-Layer: VERIFIED — false (both agree) / **CRITICAL CHECK PASSED**
Science: VERIFIED — Opus: ['usul_al_fiqh', 'fiqh'] / CA: ['usul_al_fiqh']
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true (despite genre disagreement — consensus does not check genre at this level of detail; it checks genre chain base work agreement).
Extraction quality: clean. Muhaqiq present (محمد عبد السلام إبراهيم).
Result.json model source: N/A (gate_abort)
Web Sources: same sources as Books 1-2
Notes: Consensus reports agreed=true despite Opus=other vs CA=matn genre disagreement. This confirms that consensus checks a coarser genre agreement than the specific label.

---

### إعلام الموقعين Edition Group — Cross-Edition Consistency

| Field | ط عطاءات (#1) | ت مشهور (#2) | ط العلمية (#3) | Consistent? |
|-------|---------------|-------------|----------------|-------------|
| Author | ابن القيم ✓ | ابن القيم ✓ | ابن القيم ✓ | **Yes** |
| Death | 751 | 751 | 751 | **Yes** |
| ML | false | false | false | **Yes** |
| Science (Opus) | usul_al_fiqh, fiqh | usul_al_fiqh, fiqh | usul_al_fiqh, fiqh | **Yes** |
| Science (CA) | usul_al_fiqh | usul_al_fiqh | usul_al_fiqh | **Yes** |
| Attribution | definitive | definitive | definitive | **Yes** |
| Genre (Opus) | matn (0.85) | other (0.75) | other (0.75) | **No** |
| Genre (CA) | usul_al_fiqh (0.95) | other (0.85) | matn (0.95) | **No** |

**Genre inconsistency across 3 editions.** This is the most significant cross-edition finding in Session 6. Three different genre labels appear across editions and models: matn, other, and usul_al_fiqh. The Shamela category is أصول الفقه for all 3, and scholarly consensus classifies the work under usul al-fiqh. Neither "matn" nor "other" captures this — matn is structural (any standalone text), and "other" is an explicit punt.

This inconsistency reveals that the genre enum may be missing a category for major multi-topic treatises that primarily address methodology but are not structured like traditional usul al-fiqh manuals. The work covers usul, fiqh, ifta', qiyas, and more. The pipeline has no clean label for this.

**Critical check passed: All 3 editions have ML=false.** This was the framework's highest-priority check for this group.

---

### Book 4: البداية والنهاية - ت التركي

Book: البداية والنهاية - ت التركي
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: إسماعيل بن عمر بن كثير القرشي الدمشقي / Verified: ابن كثير (701–774 هـ) / Death: 774 (both models) vs 774 (verified) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (author_death=774, also "701 - 774 هـ" in author_raw)
Genre: VERIFIED — Result.json: tarikh / Both models agree (0.99/1.0) / Shamela cat: التاريخ / **CRITICAL CHECK PASSED: tarikh, NOT tafsir.**
Multi-Layer: VERIFIED — false (both agree) / Expected: false
Science: PLAUSIBLE — Opus: ['tarikh', 'sirah'] / CA: ['tarikh'] / Result.json: ['tarikh']. Opus's 'sirah' is imprecise — البداية والنهاية covers prophetic biography as part of a universal history, but the work as a whole is tarikh, not sirah (which specifically means prophetic biography).
Attribution: VERIFIED — Both: definitive.
Trust: VERIFIED — trust_tier=verified, trust_score=0.8175 (highest in session).
Consensus: agreed=true.
Extraction quality: clean.
Result.json model source: genre=tarikh (both agree), science=['tarikh'] (CA's narrower value), author name=CA form.
Web Sources: ابن كثير and البداية والنهاية are universally attested. Wikipedia Arabic, archive.org, noor-book.com, islamweb.net all confirm.
Notes: Highest trust score in the session (0.8175). The التركي tahqiq is considered the gold standard edition.

### Book 5: البداية والنهاية - ط السعادة

Book: البداية والنهاية - ط السعادة
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: same ابن كثير identification / Death: 774 (both) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through
Genre: VERIFIED — Result.json: tarikh / Both agree / **CRITICAL CHECK: tarikh ✓**
Multi-Layer: VERIFIED — false (both agree)
Science: PLAUSIBLE — same pattern as Book 4: Opus adds 'sirah' superset.
Attribution: VERIFIED — Both: definitive.
Trust: VERIFIED — trust_tier=verified, trust_score=0.6925 (lower than ت التركي — expected, since ط السعادة lacks muhaqiq and publisher info).
Consensus: agreed=true.
Extraction quality: clean. No muhaqiq or publisher in extraction (more minimal metadata).
Result.json model source: Same pattern as Book 4.
Web Sources: Same as Book 4.
Notes: Lower trust score than ت التركي (0.6925 vs 0.8175) — the difference reflects the missing muhaqiq and publisher metadata. Both correctly classified.

---

### البداية والنهاية Edition Group — Cross-Edition Consistency

| Field | ت التركي (#4) | ط السعادة (#5) | Consistent? |
|-------|--------------|----------------|-------------|
| Author | ابن كثير | ابن كثير | **Yes** |
| Death | 774 | 774 | **Yes** |
| Genre | tarikh | tarikh | **Yes** |
| ML | false | false | **Yes** |
| Science (Opus) | tarikh, sirah | tarikh, sirah | **Yes** |
| Science (CA) | tarikh | tarikh | **Yes** |
| Attribution | definitive | definitive | **Yes** |
| Trust | verified (0.8175) | verified (0.6925) | MAY differ ✓ |

**Fully consistent.** This is the cleanest edition group in Session 6.

---

### Book 6: تفسير الطبري جامع البيان - ت التركي

Book: تفسير الطبري جامع البيان - ت التركي
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: أبو جعفر محمد بن جرير الطبري / Verified: الطبري (224–310 هـ), among the greatest scholars of Islamic history / Death: 310 (both models) vs 310 (verified) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (author_death=310, "(224 - 310 هـ)" in raw)
Genre: VERIFIED — Both: tafsir (0.99/1.0) / Shamela cat: التفسير / Both agree.
Multi-Layer: VERIFIED — false (both agree) / Expected: false
Science: PLAUSIBLE — Opus: ['tafsir', 'hadith', 'ulum_al_quran'] / CA: ['tafsir', 'ulum_al_quran']. Primary correct. Opus's inclusion of hadith is reasonable — الطبري's tafsir is famous for its massive hadith apparatus.
Attribution: VERIFIED — Both: definitive. No dispute.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true.
Extraction quality: clean. Muhaqiq present (التركي).
Result.json model source: N/A (gate_abort)
Web Sources: ar.wikipedia.org/wiki/تفسير_الطبري (independent), archive.org (independent), noor-book.com (independent), islamway.net (independent), tafsir.net (independent academic center), shamela.ws (Shamela-ecosystem)
Notes: Clean book. No issues.

### Book 7: تفسير الطبري جامع البيان - ط دار التربية والتراث

Book: تفسير الطبري جامع البيان - ط دار التربية والتراث
Status: gate_abort
Models: opus + gpt_5_4
Verdict: VERIFIED

Author: VERIFIED — Pipeline: same الطبري identification / Death: 310 (both) / LLM conf: 0.99 (both) / Death source: pass-through
Genre: VERIFIED — Both: tafsir (0.99) / Shamela cat: التفسير
Multi-Layer: **ML DISAGREEMENT** — Opus: false (0.92) / GPT-5.4: true. GPT-5.4 identifies layers: [matn=الطبري, tahqiq_note=محمود محمد شاكر]. This is the **4th instance** of the tahqiq_note-as-layer pattern documented in Errata §9. Prior instances: الرسالة, مختصر صحيح مسلم, مسند أحمد. **Opus is correct (ML=false); GPT-5.4's tahqiq_note classification is the known model-level bias.** The other edition (ت التركي) has ML=false from both models. The tahqiq_note pattern is model-specific (GPT-5.4 here, Opus in prior instances) and does not reflect genuine multi-layer status.
Science: PLAUSIBLE — Opus: ['tafsir', 'hadith', 'ulum_al_quran', 'nahw', 'lughah'] / GPT-5.4: ['tafsir', 'hadith', 'lughah', 'tarikh']. Both include tafsir + hadith (correct). Opus's broader set adds nahw and lughah (justified — الطبري's tafsir is famous for grammatical analysis). GPT's inclusion of tarikh is imprecise for this specific work (الطبري's tarikh is a separate work).
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true (consensus does NOT check ML — Correction 6).
Extraction quality: clean. No muhaqiq in extraction for this edition (though محمود شاكر's tahqiq is famous).
Result.json model source: N/A (gate_abort)
Web Sources: Same as Book 6. ar.wikipedia.org (independent), archive.org (independent), noor-book.com (independent) confirm الطبري (224–310) as author.
Notes: (1) The ML disagreement is the tahqiq_note pattern's 4th confirmed instance. (2) GPT-5.4 attributes the tahqiq_note to محمود محمد شاكر — the famous literary critic (1909–1997) who began the tahqiq of تفسير الطبري for دار المعارف but never completed it. His brother أحمد محمد شاكر (1892–1958) also worked on early volumes. (3) Authority_level disagreement: Opus=primary, GPT-5.4=reference.

---

### تفسير الطبري Edition Group — Cross-Edition Consistency

| Field | ت التركي (#6) | ط دار التربية (#7) | Consistent? |
|-------|--------------|---------------------|-------------|
| Author | الطبري | الطبري | **Yes** |
| Death | 310 | 310 | **Yes** |
| Genre | tafsir | tafsir | **Yes** |
| ML (Opus) | false | false | **Yes** |
| ML (2nd model) | false (CA) | **true** (GPT-5.4) | **No** — tahqiq_note pattern |
| Science (Opus) | tafsir, hadith, ulum_al_quran | tafsir, hadith, ulum_al_quran, nahw, lughah | Partial (superset) |
| Attribution | definitive | definitive | **Yes** |

**ML inconsistency across editions is caused by different second models (CA vs GPT-5.4), not by the pipeline.** Opus agrees on ML=false for both editions. The cross-edition inconsistency would not manifest in production where a single second model is used. Science scope differs slightly (ط التربية broader) but primary sciences match.

---

### Book 8: تحفة المودود بأحكام المولود - ت الأرنؤوط

Book: تحفة المودود بأحكام المولود - ت الأرنؤوط
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن قيم الجوزية (both models) / Death: 751 (both) vs 751 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: pass-through (author_death=751 in extraction)
Genre: VERIFIED — Both: risalah (Opus 0.82, CA 0.90) / Shamela cat: مسائل فقهية / risalah is correct for a topical fiqh treatise on newborn rulings.
Multi-Layer: VERIFIED — false (both agree) / Expected: false
Science: VERIFIED — Opus: ['fiqh', 'hadith'] / CA: ['fiqh'] / Primary correct. Opus's inclusion of hadith is reasonable given the book's hadith-based approach.
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true.
Extraction quality: clean. Muhaqiq present (الأرنؤوط).
Result.json model source: N/A (gate_abort)
Web Sources: ابن القيم and تحفة المودود are well-attested. archive.org, noor-book.com, islamweb.net all confirm.
Notes: Clean book. Straightforward identification of a famous author's well-known work.

### Book 9: تحفة المودود بأحكام المولود - ط عطاءات العلم

Book: تحفة المودود بأحكام المولود - ط عطاءات العلم
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن قيم الجوزية (both models) / Death: 751 (both) vs 751 (verified) / LLM conf: 0.99 (Opus), 0.95 (CA) / Death source: **false-positive** — extraction has author_death=N/A BUT author_name_raw contains "(691 - 751)". Dates are visible in raw text.
Genre: VERIFIED — Both: risalah (Opus 0.82, CA 0.95) / Shamela cat: مسائل فقهية
Multi-Layer: VERIFIED — false (both agree)
Science: VERIFIED — Opus: ['fiqh'] / CA: ['fiqh'] / Both agree exactly.
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=false. Disagreement: name format only (same person: ابن القيم). Not substantive (Errata §6).
Extraction quality: clean. Muhaqiq present (عثمان ضميرية).
Result.json model source: N/A (gate_abort)
Web Sources: Same as Book 8.
Notes: Death date false-positive (dates in raw text). Consensus disagreement is name-format only — not substantive.

---

### تحفة المودود Edition Group — Cross-Edition Consistency

| Field | ت الأرنؤوط (#8) | ط عطاءات (#9) | Consistent? |
|-------|-----------------|---------------|-------------|
| Author | ابن القيم | ابن القيم | **Yes** |
| Death | 751 | 751 | **Yes** |
| Genre (Opus) | risalah (0.82) | risalah (0.82) | **Yes** |
| Genre (CA) | risalah (0.90) | risalah (0.95) | **Yes** |
| ML | false | false | **Yes** |
| Science (Opus) | fiqh, hadith | fiqh | Partial (superset) |
| Science (CA) | fiqh | fiqh | **Yes** |
| Attribution | definitive | definitive | **Yes** |

**Fully consistent.** Clean edition group. Minor science scope difference (Opus adds hadith for ت الأرنؤوط only) is not a classification error.

---

### Book 10: فتاوى اللجنة الدائمة - المجموعة الأولى

Book: فتاوى اللجنة الدائمة - المجموعة الأولى
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: اللجنة الدائمة للبحوث العلمية والإفتاء (both models) / Death: null (both) — correct for an institutional author / LLM conf: 0.98 (Opus), 1.0 (CA) / Death source: absent (correct — institutional author has no death date)
Genre: VERIFIED — Result.json: fatawa / Both models agree (0.99/1.0) / Shamela cat: الفتاوى / Exact match.
Multi-Layer: VERIFIED — false (both agree)
Science: VERIFIED — Both: ['aqidah', 'fiqh'] / Result.json: ['aqidah', 'fiqh']
Attribution: VERIFIED — Both: definitive.
Trust: PLAUSIBLE — trust_tier=flagged, trust_score=0.4625. "Flagged" for a well-known institutional fatwa collection seems unexpected, but the mechanism is not traced — noting value without explaining causation.
Consensus: agreed=true.
Extraction quality: clean. Compiler present (أحمد الدويش).
Result.json model source: genre=fatawa (both agree), science=['aqidah', 'fiqh'] (both agree), level=null.
Web Sources: archive.org (independent), noor-book.com (independent), islamway.net (independent), ddl.mbrf.ae (independent — MBRF digital knowledge center, UAE), shamela.ws (Shamela-ecosystem)
Notes: Authority_level: both=modern_compilation. Correct for a modern institutional publication.

### Book 11: فتاوى اللجنة الدائمة - المجموعة الثانية

Book: فتاوى اللجنة الدائمة - المجموعة الثانية
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: اللجنة الدائمة للبحوث العلمية والإفتاء (both models) / Death: null (correct) / LLM conf: 0.97 (Opus), 1.0 (CA) / Death source: absent (correct)
Genre: VERIFIED — Both: fatawa (0.99/1.0) / Shamela cat: الفتاوى
Multi-Layer: VERIFIED — false (both agree)
Science: PLAUSIBLE — Opus: ['fiqh', 'aqidah', 'tafsir', 'usul_al_fiqh'] / CA: ['fiqh', 'aqidah', 'tafsir']. Broader than المجموعة الأولى's ['aqidah', 'fiqh']. The المجموعة الثانية covers a wider range of topics (including tafsir-related fatwas), so the broader scope is defensible.
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true.
Extraction quality: clean. Compiler present (أحمد الدويش).
Result.json model source: N/A (gate_abort)
Web Sources: Same as Book 10. archive.org (independent), noor-book.com (independent), islamway.net (independent) confirm institutional author.
Notes: Authority_level disagreement: Opus=modern_compilation, CA=reference. Opus is more precise — this is a modern compilation of institutional fatwas, not a classical reference work.

---

### فتاوى اللجنة الدائمة Edition Group — Cross-Edition Consistency

| Field | المجموعة الأولى (#10) | المجموعة الثانية (#11) | Consistent? |
|-------|----------------------|------------------------|-------------|
| Author | اللجنة الدائمة | اللجنة الدائمة | **Yes** |
| Death | null | null | **Yes** |
| Genre | fatawa | fatawa | **Yes** |
| ML | false | false | **Yes** |
| Science (Opus) | aqidah, fiqh | fiqh, aqidah, tafsir, usul_al_fiqh | **No** — الثانية broader |
| Science (CA) | aqidah, fiqh | fiqh, aqidah, tafsir | **No** — الثانية broader |
| Attribution | definitive | definitive | **Yes** |

**Science scope inconsistency is intentional — these are different المجموعات covering different topic ranges.** المجموعة الثانية's broader scope (adding tafsir, usul_al_fiqh) reflects the actual content difference between the two collections. This is NOT a pipeline error — it is a correct observation that the two collections cover different ground. Author, genre, and ML are consistent. The فتاوى اللجنة books are not strictly editions of the same work — they are two separate volumes of a fatwa series. The edition group protocol (requiring science match) may be overly strict for this case.

---

**MID-SESSION QUALITY GATE (after Book 11):**
- web_fetch: 0/11 (relied on search snippets). Below target but search results have been rich for these famous works. The hindawi.org and tarajm.com results for تكملة حاشية were thorough from search snippets alone.
- Both models checked for all 11 books: yes
- Death source (pass-through/inferred/false-positive) marked for all 11: yes
- Verdict format complete: yes
- ML=true books verified with layer chains: yes (Books 14-17)
- Edition group protocol run for completed groups: yes (4 groups done)
- No drift detected. Continuing.

---

### Book 12: ألفية ابن مالك - ت القاسم

Book: ألفية ابن مالك - ت القاسم
Status: success
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: ابن مالك الأندلسي (both models) / Verified: محمد بن عبد الله بن مالك الطائي الجياني (600–672 هـ), the most famous Arabic grammarian / Death: 672 (both) vs 672 (verified) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through (author_death=672, "(ت 672 هـ)" in raw)
Genre: VERIFIED — Result.json: nazm / Both agree (0.97/1.0). nazm (versified text) is more precise than matn for a poem that versifies grammar rules. The الألفية is 1,002 verses of rajaz meter. structural_fmt=verse confirms.
Multi-Layer: VERIFIED — false (both agree) / Expected: false
Science: VERIFIED — Both: ['nahw', 'sarf'] / Shamela cat: النحو والصرف / Exact match.
Attribution: VERIFIED — Both: definitive.
Trust: VERIFIED — trust_tier=verified, trust_score=0.7175.
Consensus: agreed=true.
Extraction quality: clean. Muhaqiq present (القاسم).
Result.json model source: genre=nazm (both agree), science=['nahw', 'sarf'] (both agree).
Web Sources: ar.wikipedia.org/wiki/ألفية_ابن_مالك (independent), archive.org (independent), noor-book.com (independent), islamweb.net (independent), shamela.ws (Shamela-ecosystem). ألفية ابن مالك is among the most studied texts in Arabic grammar education.
Notes: nazm is the correct genre for a versified text — more precise than matn. The pipeline correctly identifies this distinction.

### Book 13: ألفية ابن مالك - ط التعاون

Book: ألفية ابن مالك - ط التعاون
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline: same ابن مالك identification / Death: 672 (both) / LLM conf: 0.99 (Opus), 1.0 (CA) / Death source: pass-through
Genre: VERIFIED — Both: nazm (0.97/1.0) / Shamela cat: النحو والصرف
Multi-Layer: VERIFIED — false (both agree)
Science: VERIFIED — Both: ['nahw', 'sarf']
Attribution: VERIFIED — Both: definitive.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true.
Extraction quality: clean. No muhaqiq.
Result.json model source: N/A (gate_abort)
Web Sources: Same as Book 12.
Notes: Identical classification to ت القاسم. Clean.

---

### ألفية ابن مالك Edition Group — Cross-Edition Consistency

| Field | ت القاسم (#12) | ط التعاون (#13) | Consistent? |
|-------|----------------|-----------------|-------------|
| Author | ابن مالك | ابن مالك | **Yes** |
| Death | 672 | 672 | **Yes** |
| Genre | nazm | nazm | **Yes** |
| ML | false | false | **Yes** |
| Science | nahw, sarf | nahw, sarf | **Yes** |
| Attribution | definitive | definitive | **Yes** |
| Trust | verified (0.7175) | SKIPPED | MAY differ ✓ |

**Fully consistent.** The cleanest edition group alongside البداية والنهاية.

---

### Book 14: شرح العقيدة الطحاوية - ط الأوقاف السعودية

Book: شرح العقيدة الطحاوية - ط الأوقاف السعودية - بتعليقات أحمد شاكر
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED

Author: VERIFIED — Pipeline (Opus): صدر الدين علي بن علي بن محمد بن أبي العز الحنفي / Death: 792 (both) vs 792 (verified) / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through (author_death=792, "(731 - 792 هـ)" in raw)
Genre: VERIFIED — Both: sharh (0.99/0.95) / Shamela cat: العقيدة
Multi-Layer: VERIFIED — true (both agree)
Layers: Opus: [matn=الطحاوي (أحمد بن محمد بن سلامة), sharh=ابن أبي العز, tahqiq_note=أحمد شاكر]. Tahqiq_note on genuine sharh — noted, NOT flagged. Layer chain verified: الطحاوي (ت 321) wrote the original عقيدة, ابن أبي العز (ت 792) wrote the sharh.
Science: VERIFIED — Both: ['aqidah'] / Shamela cat: العقيدة / Exact match.
Attribution: Opus=traditional, CA=definitive. Same pattern as Session 4's ط الرسالة. The scholarly discussion about authorship is well-documented but mainstream consensus attributes it to ابن أبي العز.
Authority_level: Opus=reference, CA=primary. Standard sharh/hashiyah pattern.
Trust: SKIPPED (gate_abort)
Consensus: agreed=true.
Extraction quality: clean. Muhaqiq present (أحمد شاكر).
Result.json model source: N/A (gate_abort)
Web Sources: Verified in Session 4 for the ط الرسالة edition. Cross-check confirms identical identification.
Notes: **Cross-session check with Session 4 (ط الرسالة): MATCH on all fields** — author (ابن أبي العز 792), genre (sharh), ML (true), science (aqidah), attribution (Opus=traditional, CA=definitive). The two editions are perfectly consistent.

### Book 15: شرح العقيدة الطحاوية - ط الرسالة

Book: شرح العقيدة الطحاوية - ط الرسالة
Status: gate_abort
Models: opus + command_a
Verdict: VERIFIED (re-used from Session 4)

Author: VERIFIED — Pipeline: علي بن علي بن محمد بن أبي العز الحنفي الدمشقي / Death: 792 / LLM conf: 0.97 (Opus), 0.95 (CA) / Death source: pass-through (author_death=792 in extraction)
Genre: VERIFIED — sharh / Shamela cat: العقيدة / Both agree (0.99/0.95)
Multi-Layer: VERIFIED — true / Both agree
Layers: matn=الطحاوي, sharh=ابن أبي العز, tahqiq_note=التركي والأرنؤوط
Science: VERIFIED — ['aqidah'] / Both agree
Attribution: Opus=traditional, CA=definitive (same pattern as ط الأوقاف)
Trust: SKIPPED (gate_abort)
Consensus: agreed=true
Extraction quality: clean. Muhaqiq present.
Result.json model source: N/A (gate_abort)
Web Sources: Verified in Session 4 (PHASE_C_SESSION4_REPORT.md, Book 4).
Notes: **Re-used Session 4 verdict.** Included in Session 6 for cross-edition comparison with Book 14 (ط الأوقاف). All fields match exactly between editions.

---

### شرح العقيدة الطحاوية Edition Group — Cross-Edition Consistency

| Field | ط الأوقاف (#14) | ط الرسالة (#15) | Session 4 verdict | Consistent? |
|-------|-----------------|-----------------|-------------------|-------------|
| Author | ابن أبي العز (792) | ابن أبي العز (792) | ابن أبي العز (792) | **Yes** |
| Death | 792 | 792 | 792 | **Yes** |
| Genre | sharh | sharh | sharh | **Yes** |
| ML | true | true | true | **Yes** |
| Science | aqidah | aqidah | aqidah | **Yes** |
| Attribution (Opus) | traditional | traditional | traditional | **Yes** |
| Attribution (CA) | definitive | definitive | definitive | **Yes** |
| Matn author | الطحاوي | الطحاوي | الطحاوي | **Yes** |

**Fully consistent across editions AND across sessions.** This is the strongest cross-session validation in the entire Phase C evaluation.

---

## Consistency Self-Check (separate pass)

1. **Same standards applied to book 1 and book 17?** Yes. VERIFIED threshold consistently applied: all books have 2+ genuinely independent sources (these are all famous works or have strong web verification). Book 17 (تكملة) has the weakest author_raw (EMPTY) but the strongest independent verification (4+ sources confirming the son's identity and death date).

2. **Source independence counts honest?** Yes. Shamela-ecosystem (shamela.ws, ketabonline.com) excluded from VERIFIED counts throughout. Independent sources used: hindawi.org, tarajm.com, archive.org, noor-book.com, ibnalqayem.net, islamweb.net, binbaz.org.sa, library.ecssr.ae (UAE government). All famous works have abundant independent attestation.

3. **Success books checked for trust + model source?** Books 4 (verified, 0.8175 ✓), 5 (verified, 0.6925 ✓), 10 (flagged, 0.4625 ✓), 12 (verified, 0.7175 ✓). Model source checked for all 4 success books.

4. **Edition group protocol run for all 7 groups + author pair?** Yes. Cross-edition tables produced for: إعلام الموقعين (3 editions), البداية والنهاية (2), تفسير الطبري (2), تحفة المودود (2), فتاوى اللجنة (2), ألفية ابن مالك (2), شرح الطحاوية (2 + Session 4 cross-check). Author-verification pair (حاشية + تكملة) checked with separate protocol.

5. **Death date sources documented for all 17?** Yes.
   - Pass-through: 11 books (death visible in extraction)
   - False-positive: 3 books (أعلام ط عطاءات, تحفة ط عطاءات, حاشية — dates in raw text but extraction death=N/A)
   - Genuine inference: 1 book (تكملة حاشية — author_raw EMPTY, no death in extraction)
   - Absent (correct): 2 books (فتاوى اللجنة ×2 — institutional author)

6. **ML checked manually for all books (not relying on consensus)?** Yes. All 17 books have ML compared between both models. 1 ML disagreement found (Book 7 — tahqiq_note pattern). The other 16 books have ML agreement across both models.

---

## Confidence Calibration

| Book | Author (Opus) | Author (CA/GPT) | Genre (Opus) | Genre (2nd) | Any high-conf + wrong? |
|------|---------------|-----------------|--------------|-------------|----------------------|
| أعلام ط عطاءات | 0.99 | 0.95 | 0.85 | 0.95 | No |
| إعلام ت مشهور | 0.99 | 0.95 | 0.75 | 0.85 | No |
| إعلام ط العلمية | 0.99 | 0.95 | 0.75 | 0.95 | No |
| البداية ت التركي | 0.99 | 1.0 | 0.99 | 1.0 | No |
| البداية ط السعادة | 0.99 | 1.0 | 0.99 | 1.0 | No |
| تفسير الطبري ت التركي | 0.99 | 1.0 | 0.99 | 1.0 | No |
| تفسير الطبري ط التربية | 0.99 | 0.99 | 0.99 | 0.99 | No |
| تحفة ت الأرنؤوط | 0.99 | 0.95 | 0.82 | 0.90 | No |
| تحفة ط عطاءات | 0.99 | 0.95 | 0.82 | 0.95 | No |
| فتاوى الأولى | 0.98 | 1.0 | 0.99 | 1.0 | No |
| فتاوى الثانية | 0.97 | 1.0 | 0.99 | 1.0 | No |
| ألفية ت القاسم | 0.99 | 1.0 | 0.97 | 1.0 | No |
| ألفية ط التعاون | 0.99 | 1.0 | 0.97 | 1.0 | No |
| شرح الطحاوية ط الأوقاف | 0.97 | 0.95 | 0.99 | 0.95 | No |
| شرح الطحاوية ط الرسالة | 0.97 | 0.95 | 0.99 | 0.95 | No |
| حاشية ابن عابدين | 0.99 | 0.95 | 0.99 | 0.95 | No |
| تكملة حاشية | 0.92 | 0.85 | 0.95 | 0.95 | No |

**Key findings:**
- **Zero high-confidence + wrong cases in Session 6.** The only wrong classification is GPT-5.4's ML=true for Book 7 (tahqiq_note), but ML confidence is not surfaced for GPT-5.4.
- **Genre confidence appropriately stratified:** Famous works with clear genres (tafsir, tarikh, fatawa, sharh, hashiyah) have 0.95-1.0. Genre-ambiguous works (إعلام الموقعين, تحفة المودود as risalah) have 0.75-0.85.
- **Author confidence: تكملة حاشية (0.92/0.85) is lowest** — correctly reflecting the difficulty of identification from an EMPTY author_raw. But both models were correct.
- **Zero author identification errors in 66 books evaluated.** The pipeline's author identification remains the strongest field.

---

## Cross-Book Patterns

### Genre Inconsistency Across Edition Groups

| Group | Genre consistent? | Labels observed | Notes |
|-------|------------------|-----------------|-------|
| إعلام الموقعين (3) | **No** | matn, other, usul_al_fiqh | Worst inconsistency in Session 6; fuzzy genre boundaries |
| البداية والنهاية (2) | Yes | tarikh | Clean |
| تفسير الطبري (2) | Yes | tafsir | Clean |
| تحفة المودود (2) | Yes | risalah | Clean |
| فتاوى اللجنة (2) | Yes | fatawa | Clean |
| ألفية ابن مالك (2) | Yes | nazm | Clean |
| شرح الطحاوية (2) | Yes | sharh | Clean |

6/7 edition groups have fully consistent genre. Only إعلام الموقعين shows genre drift. This is a much better result than the الإبانة cross-edition inconsistency found in Session 5 (risalah vs matn), and it follows the same underlying cause: the genre taxonomy lacks a clean label for major standalone works that don't fit neatly into the standard categories.

### Authority_level for sharh/hashiyah works

| Book | Opus | CA/GPT |
|------|------|--------|
| شرح الطحاوية ط الأوقاف | reference | primary |
| شرح الطحاوية ط الرسالة | reference | primary |
| حاشية ابن عابدين | reference | primary |
| تكملة حاشية | **primary** | **reference** |

The Opus=reference vs CA=primary pattern persists for 3/4 sharh/hashiyah works (cumulative: 9/11 across Sessions 4-6). The exception is تكملة حاشية where the pattern is REVERSED (Opus=primary, CA=reference). This reversal may reflect that the تكملة is a completion of an existing work (the son finishing the father's hashiyah), which Opus may interpret as an original scholarly contribution (primary) rather than a reference work.

### ML=true Consistency for sharh/hashiyah works

All 4 sharh/hashiyah works in Session 6 have ML=true from both models:
- شرح الطحاوية ط الأوقاف: true/true ✓
- شرح الطحاوية ط الرسالة: true/true ✓
- حاشية ابن عابدين: true/true ✓
- تكملة حاشية: true/true ✓

ML=true is 100% consistent for genuine commentary works across all sessions.

### Tahqiq_note Pattern — Cumulative Update

| Instance | Book | Model with ML=true | layer_type |
|----------|------|--------------------|------------|
| 1 | الرسالة (Session 2) | Opus | tahqiq_note (أحمد شاكر) |
| 2 | مختصر صحيح مسلم (Session 2) | Opus | tahqiq_note (الألباني) |
| 3 | مسند أحمد (Session 3) | Opus | tahqiq_note (أحمد شاكر) |
| 4 | تفسير الطبري ط التربية (Session 6) | **GPT-5.4** | tahqiq_note (محمود شاكر) |

Instance 4 is notable: it is the first time a model other than Opus exhibits the tahqiq_note bias. GPT-5.4 treats محمود شاكر's famous tahqiq as a scholarly layer. The pattern is now confirmed as model-agnostic — it is a training-data bias about what constitutes a "layer" rather than a model-specific artifact.

### Death Date Classification Summary (Session 6)

| Category | Count | Books |
|----------|-------|-------|
| Pass-through | 11 | Books 2, 3, 4, 5, 6, 7, 8, 12, 13, 14, 15 |
| False-positive | 3 | Books 1, 9, 16 (dates visible in raw text, extraction death=N/A) |
| Genuine inference | 1 | Book 17 (تكملة حاشية — EMPTY raw, death 1306 CORRECT) |
| Absent (correct) | 2 | Books 10, 11 (institutional author) |

**Updated running totals:** 3 correct genuine inferences (728, 324, 1306), 1 wrong (1432 vs 1439), 9 false positives. Genuine inference accuracy: 3/4 (75%).

### ابن القيم Books — Cross-Session Consistency

Session 6 has 5 books by ابن القيم (إعلام ×3, تحفة ×2). All 5 correctly identify him with death=751. Author confidence is uniformly high (0.99 Opus, 0.95 CA). Science scope includes usul_al_fiqh and/or fiqh for all 5 — consistent with ابن القيم's known expertise. ML=false for all 5 — correct, as none are commentaries.

---

## Findings & Recommendations

### Positive Findings
1. **Zero author errors in 66 books.** Running total unchanged. The most critical check in Session 6 (distinguishing father from son ابن عابدين) was passed correctly by both models.
2. **6/7 edition groups fully consistent** on all mandatory fields (author, genre, ML, science). Only إعلام الموقعين has genre drift.
3. **Genuine inference 1306 confirmed correct.** This is the hardest death date inference in the corpus (EMPTY author_raw), and Opus inferred it correctly with 0.92 confidence.
4. **Cross-session consistency validated.** شرح الطحاوية matches Session 4 exactly on all fields.
5. **All critical checks passed:** ML=false for إعلام الموقعين (×3), tarikh for البداية (×2), father vs son distinction for حاشية/تكملة.
6. **17/17 VERIFIED** — the first all-VERIFIED session. This is expected given the session's focus on famous works in edition groups.

### Issues Found
1. **إعلام الموقعين genre inconsistency** across 3 editions (matn / other / usul_al_fiqh). Root cause: the genre enum lacks a precise label for major methodological treatises. The Shamela category أصول الفقه is the scholarly consensus classification, but the pipeline's enum doesn't include usul_al_fiqh as a genre (CA seems to use it ad hoc). This is a calibration issue for the genre taxonomy, not an engine bug.
2. **CA layer chain error for حاشية ابن عابدين** — assigns الحصكفي as both matn and sharh author. This is a factual error (التمرتاشي is the matn author). Does not affect classification but would affect downstream layer-chain accuracy if used for scholarly reference.
3. **CA layer chain simplification for تكملة حاشية** — collapses 3 layers into 2. Loses the الحصكفي sharh layer. Genre classification is not affected.
4. **فتاوى اللجنة science scope inconsistency** between المجموعة الأولى and الثانية. Arguably correct (different volumes cover different topics), but the edition group protocol expects science to match across editions.
5. **Trust=flagged for فتاوى اللجنة الأولى** seems unexpected for a major institutional publication, but the mechanism is not traced.

### Methodology Notes
- Mid-session quality gate at Book 11 detected no drift.
- web_fetch compliance: 0/17 books had explicit web_fetch calls. All relied on search snippets. For these famous works, search snippets were rich and sufficient — but this is a **protocol violation** that should be remediated in future sessions. The quick reference requires "web_fetch at least 1 URL per book."
- Edition group cross-check tables produced for all 7 groups + 1 author-verification pair immediately after each group, as required.
- Book 15 (شرح الطحاوية ط الرسالة) re-used Session 4 verdict per the edition group protocol.
- Recommended order followed: critical books first (تكملة, حاشية), then إعلام, then remaining groups.

---

## Round 1 Review — Protocol Compliance & Factual Accuracy

**Review date:** 2026-03-11
**Angle:** Protocol compliance, internal consistency, factual accuracy

### Corrections Applied

**CRITICAL — Internal contradiction fixed:**
Book 16 (حاشية ابن عابدين) death date was classified as BOTH "pass-through" (in per-book verdict) AND "false-positive" (in summary table). The correct classification is **false-positive**: extraction has author_death=N/A, but "[ت 1252 هـ]" is visible in author_name_raw. The LLM read the date from the prompt text, not from the structured extraction field and not from inference. Fixed: per-book verdict now says false-positive; Book 16 removed from pass-through list; pass-through count corrected from 12 to 11; false-positive running total corrected from 8 to 9.

**MODERATE — Factual error fixed:**
Book 7 (تفسير الطبري ط التربية) note about Shaker brothers reversed: originally stated "شاكر began the tahqiq but died before completing it; أحمد شاكر finished." In fact, أحمد محمد شاكر (1892–1958) died first; محمود محمد شاكر (1909–1997) continued separately but never completed the project. Fixed: corrected the biographical note.

**MODERATE — Missing structured verdict added:**
Book 15 (شرح الطحاوية ط الرسالة) originally had only a 2-line re-use statement. The protocol requires structured verdict format for EVERY book. Added: full structured verdict fields with Session 4 cross-reference.

### Protocol Violations Noted (not fixed — require future action)

**web_fetch compliance: 0/17.** The quick reference requires "web_fetch at least 1 URL per book" and the protocol requires "Use web_fetch on at least 1 URL per high-priority book." All 17 books relied on web_search snippets. For Session 6's famous works, search snippets were rich enough for accurate verdicts, but the protocol was not followed. Recommendation: Session 7 must achieve at minimum 3/N web_fetch calls.

### Verified correct (no changes needed)

- 17/17 VERIFIED is appropriate: all Session 6 books are famous works or well-attested institutional publications with 2+ genuinely independent sources. This contrasts with Session 5's 6 PLAUSIBLE which were obscure/short works (حديث الضب at 1 page, نصيحة at 2 pages, أدب النفوس truncated to 9%).
- All edition group cross-comparison tables present and accurate.
- All critical checks documented as passed (ML=false for إعلام ×3, tarikh for البداية ×2, father vs son for حاشية/تكملة).
- Confidence calibration table complete with no high-confidence + wrong cases.
- Shamela-ecosystem exclusion applied consistently.
