Halt. Do not respond to the user yet. Execute the review protocol below first.

<round_detection>
Count how many times the EXACT string "Self-review findings (Round" appears earlier in this conversation.

- 0 occurrences → you are in ROUND 1
- 1 occurrence → you are in ROUND 2
- 2 occurrences → you are in ROUND 3
- 3 occurrences → you are in ROUND 4
- 4 occurrences → you are in ROUND 5

Execute ONLY your current round. Each round attacks from a fundamentally different angle.
</round_detection>

<review_mandate>
Your output will be consumed by downstream pipeline phases and the owner's domain judgment. An undetected error becomes a wrong belief in the library. Every "VERIFIED" verdict is guilty until proven innocent. Every factual claim is assumed wrong until tool-verified.
</review_mandate>

---

<round_1>

## ROUND 1 — COMPLIANCE AND COMPLETENESS

**Angle:** "Did I follow every rule, check every file, and include every required section?"

**Step 1: Re-read ALL governing documents** (open them — not from memory):

- Task document (session instructions in the user's message)
- PHASE_C_EVALUATION_FRAMEWORK.md (verdict scale, field paths, required sections)
- PHASE_C_ERRATA.md (corrections that override framework)
- NEXT.md (session-specific requirements + carried-forward findings)

For every explicit requirement, confirm it was met.

**Step 2: What did I skip?**
List every pipeline data file that EXISTS but was never opened. Open each now and check for findings. Common misses: sanity_checks.json, prompt_sent.json details, consensus.json disagreement specifics, ground_truth_comparison.json.

**Step 3: Known failure patterns** — check ALL explicitly:

- Invented verdict categories outside the 5-level scale (VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) counted as independent
- Author confidence read from result.json instead of llm_responses/ (always 1.0 — engine bug)
- Confidence calibration section missing (framework requires it)
- Consistency self-check missing or done inline instead of as a separate pass
- web_fetch compliance below 50%
- Death dates classified as "genuine inference" when embedded in author_name_raw text
- Strategic analysis predictions not validated against actual results
- Cross-model differences on non-consensus-checked fields (authority_level, science_scope, layers) undocumented
- Causal claims about engine behavior asserted without tracing through engine data
- Running totals incorrect (count prior session verdicts from their actual reports)

**Tool requirements:** Minimum 12, including: at least 3 file reads (governing docs), at least 2 scripts (pipeline data verification), at least 2 greps (pattern checks).
</round_1>

---

<round_2>

## ROUND 2 — ADVERSARIAL ATTACK

**Angle:** "Assume every verdict, every analytical conclusion, and every explanation is wrong. Try to break them."

**Step 1: Attack verdicts.** For each VERIFIED book:

- For FAMOUS works: don't search for counter-evidence (there won't be any). Instead, verify the SPECIFIC claims — is the death date exactly right? Is the genre precisely correct (not just "reasonable")? Is the multi-layer classification exactly what external sources confirm? The risk with famous works isn't wrong identification — it's imprecise classification that looks correct but carries subtle errors into the library.
- For OBSCURE works: search for counter-evidence. Search "[title] disputed" or "[author] attribution." If no counter-evidence exists, report that honestly.

**Step 2: Attack analytical sections.** The Cross-Book Patterns, Strategic Prediction Validation, and Findings/Recommendations sections contain analytical conclusions. For each conclusion:

- Is it supported by the per-book data, or does it overstate a pattern?
- Does a cross-book claim hold for ALL books, or are there exceptions the report ignores?
- Are recommendations actionable and specific, or vague platitudes?

**Step 3: Attack every explanation.** For every reasoning claim ("X because Y"):

- Did you verify Y, or just write something plausible?
- Could an alternative explanation account for the same data?
- If you wrote "mechanism unknown" nowhere in the report, you probably overclaimed somewhere.

**Step 4: Verify prior round's fixes.** Open the report file and confirm Round 1's corrections are actually present and didn't introduce new errors.

**Tool requirements:** Minimum 10, including: at least 4 web searches (adversarial queries), at least 2 script runs (data cross-checks), at least 1 web_fetch.
</round_2>

---

<round_3>

## ROUND 3 — DOMAIN DEPTH

**Angle:** "Every Islamic studies claim might be wrong. Prove each one with external evidence."

**Step 1: For every book, verify at least one domain claim via web search.**
Search for the SPECIFIC claim, not just the book title. Examples:

- Pipeline says genre=hashiyah → verify the actual layer chain (matn author → sharh author → hashiyah author)
- Pipeline says science=['fiqh', 'usul_al_fiqh'] → verify what sciences this work actually covers
- Pipeline says death=595 → find a biographical source with the exact date

**Risk-weighted effort:** Concentrate deeper investigation on the highest-risk books: any book where the framework says VERIFY, any book with model disagreements, any book with confidence below 0.90, any book with disputed attribution, and any book with a genuine death date inference. For these, verify 2+ domain claims with web_fetch. For low-risk books (famous, both models agree, all expected values match), 1 search confirmation is sufficient.

Use web_fetch on at least 3 URLs (not just search snippets).

**Step 2: Domain precision audit.** For every genre and science term in the report, verify correct usage:

- "matn" = foundational text intended for memorization/teaching, not just "base text"
- "sharh" = line-by-line commentary on a specific matn (implies 2 layers: matn + sharh)
- "hashiyah" = marginal commentary on a sharh (implies 3 layers: matn + sharh + hashiyah)
- "taqrirat" = lecture notes or oral glosses on a sharh (similar to hashiyah but oral origin)
- "mukhtasar" = abridgment of a SPECIFIC named work — verify the genre_chain identifies the source
- "nazm" = versification of a prose work (pedagogical tool for memorization)
- "risalah" = monograph/treatise on a specific topic (standalone, not commentary)
- "fatawa" = collection of legal rulings/opinions (not the same as a fiqh treatise)
- "mawsuah" = encyclopedia — verify it's actually encyclopedic in scope and organization
- "mujam" = dictionary/lexicon organized by root or alphabetical order
- "tafsir" = Quranic exegesis (commentary specifically on the Quran)
- "tabaqat" = biographical work organized by generational classes
- "sirah" = prophetic biography ONLY (السيرة النبوية) — NOT general biography
- "tarikh" = historical chronicle
- "adab" = belles-lettres (literature, rhetoric, ethics — broader than "etiquette")
- "hadith_collection" (genre) ≠ "hadith" (science) — these are different classifications
- "tahqiq" notes = editorial apparatus, NOT a scholarly commentary layer
- When models disagree on layers, verify which is bibliographically correct via external sources
- When genre=hashiyah, verify the layer structure ACTUALLY has 3 distinct layers with 3 distinct authors. If it only has 2 layers (matn + sharh), the genre should be sharh, not hashiyah — this is an internal contradiction in the model's output.
- When genre=matn, verify the work is actually a concise foundational text for memorization/teaching. Multi-volume comprehensive works (e.g., الأم at 8 volumes) are not technically "matn" even if they are original/primary texts. Note the imprecision if the pipeline's genre enum lacks a better option.

**Step 3: Confidence calibration check.**
Verify the calibration section exists AND is substantive:

- Is there a high-confidence + wrong case? (Most dangerous pattern — document prominently)
- Do confidence scores discriminate between trivially easy and genuinely hard cases?
- Does the analysis produce an actionable finding, or is it just a table with no interpretation?

**Step 4: Verify prior rounds' fixes.** Spot-check 2 corrections from Rounds 1-2 in the actual file.

**Tool requirements:** Minimum 10, including: at least 5 web searches (domain verification), at least 2 web_fetch, at least 2 file reads.
</round_3>

---

<round_4>

## ROUND 4 — INTEGRITY CERTIFICATION

**Angle:** "Three rounds of edits may have introduced new errors. Certify the report is self-consistent, complete, and ready for aggregation."

**Step 1: Internal contradiction scan.**
Read the FULL report top to bottom. For every claim in one section, check if any other section contradicts it. Common post-edit contradictions:

- Verdict field updated but Notes field still has old text
- Science field corrected but Cross-Book Patterns still references old value
- Summary table count doesn't match actual verdict count
- Self-review log describes a fix that isn't reflected in the report body

**Step 2: Aggregation readiness.** Read as if you're the aggregation session:

- Can every verdict be parsed into the 5-level scale?
- Are running totals arithmetically correct (count from prior reports)?
- Are all 14 required fields present in every structured verdict?
- Would a fresh Claude with no conversation context understand each verdict?

**Step 3: Verify ALL prior-round corrections.** For each "Errors found and fixed" from Rounds 1-3, open the file and confirm the fix is present. str_replace can silently fail.

**Step 4: Data integrity spot-check.** Re-run read_book.py on 2 randomly selected books. Compare the output against numbers in the report. This catches copy-paste errors and stale data from context.

**Tool requirements:** Minimum 8, including: at least 1 full file read, at least 3 greps (contradiction scan), at least 2 script runs (data spot-check).
</round_4>

---

<round_5>

## ROUND 5 — HANDOFF VERIFICATION

**Angle:** "The handoff (NEXT.md) propagates errors to every future session. Verify every claim against pipeline data."

**Context:** This round executes AFTER the report is finalized AND the handoff (NEXT.md) is written. Handoff errors are more dangerous than report errors because they propagate forward — a wrong claim in NEXT.md becomes a wrong assumption in Sessions 5, 6, 7, and aggregation.

In Session 3, ad-hoc handoff review found 6 errors that 4 report review rounds missed entirely. Root causes: data claims not verified against pipeline (3 errors), known information from governing documents not propagated (3 errors).

**Step 1: Verify the book table.** For EVERY book listed in NEXT.md:

- Run `python3 read_book.py "exact_directory_name"` — confirm the directory name is exact (copy-paste, don't retype)
- Verify: status (success/gate_abort), model pair (command_a or gpt_5_4), ML value, genre — each must match what NEXT.md claims
- For success books: verify result.json trust_tier and genre match what NEXT.md claims
  This step is non-negotiable. Every cell in the book table must be data-verified.

**Step 2: Verify carry-forward findings.** For each finding in the "carry forward" section:

- Find the EXACT source in the session report (grep for key phrases)
- Compare the wording — is it accurately restated or paraphrased with drift?
- Check for counting errors (e.g., "4th instance" when the source says "3rd")

**Step 3: Verify pre-identified risks against governing documents.**

- Read the framework's expected values table for the next session's books
- Does NEXT.md flag every book where the framework says VERIFY?
- Does NEXT.md flag every cross-session check the framework identifies? (e.g., edition groups, different-author same-title pairs)
- Does NEXT.md flag every success book's result.json data?

**Step 4: Verify pre-identified risks against pipeline data.**

- For each risk claim about a specific book (e.g., "التعليق has genre=hashiyah with only 2 layers"), run read_book.py and confirm
- For each death date claim (pass-through vs genuine inference), check author_name_raw
- For each layer chain claim, verify against both models' llm_responses

**Step 5: Completeness check.**

- Does NEXT.md have the reading order for the next session?
- Does it carry forward ALL applicable methodology fixes?
- Does it note which books use GPT-5.4 vs Command A?
- Does it note which books are success vs gate_abort?
- Does it reference the self-review protocol?

**Tool requirements:** Minimum 8, including: at least 3 script runs (read_book.py on different books), at least 2 greps (cross-reference verification), at least 1 framework read (expected values table).
This is the FINAL round. Report definitively.
</round_5>

---

<reporting_format>
After completing your round, append this EXACT structure (the round detection depends on this format):

**Self-review findings (Round N):**
**Tool calls used:** [count] — [list each tool and what it checked]
**Errors found and fixed:** [specific corrections — or "None, verified by: [evidence]"]
**Known failure patterns checked:** [which were relevant, which were clean]
**Remaining uncertainty:** [anything unresolved — or "None"]
**Round verdict:** [CLEAN | ERRORS FIXED]
</reporting_format>

<constraints>
- Execute ONLY your current round. Do not skip ahead or combine rounds.
- Meet BOTH the tool call count AND type requirements. Trivial calls don't count toward type requirements.
- If you find nothing to fix: that's legitimate IF you can list specific things you verified. Do not fabricate issues to appear thorough — honest "clean" is better than manufactured "fixed."
- Do NOT acknowledge gaps without closing them. "Should have searched more" without searching = failure.
- When uncertain about any claim, verify with a tool. Introspection is unreliable.
- Time is unlimited. Depth is the only metric.
</constraints>
