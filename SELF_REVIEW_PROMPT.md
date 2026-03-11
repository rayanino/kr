Halt. Do not respond to the user yet. Execute the review protocol below first.

<round_detection>
Count the number of "**Self-review findings:**" blocks that already exist in this conversation. That count determines your current round:
- 0 prior blocks → you are in ROUND 1
- 1 prior block → you are in ROUND 2
- 2 prior blocks → you are in ROUND 3
- 3 prior blocks → you are in ROUND 4

Execute ONLY the instructions for your current round. Do NOT repeat checks from prior rounds — they already ran. Each round attacks from a fundamentally different angle. If a prior round reported "X is clean," trust that and move on to your round's unique concerns.
</round_detection>

<review_mandate>
Your output contains claims. Some of them are wrong. An undetected error becomes a wrong belief in the owner's library, permanently embedded across 6 downstream engines. Every "VERIFIED" verdict is guilty until proven innocent. Every factual claim is assumed wrong until tool-verified. If you finish any round and report "nothing to fix," you almost certainly didn't look hard enough.
</review_mandate>

---

<round_1>
## ROUND 1 — COMPLIANCE AND COMPLETENESS (broadest sweep)
**Angle:** "Did I follow every rule, and did I check every file?"

**Step 1: Re-read ALL governing documents** (not from memory — open them):
- Task document (the session instructions in the user's message)
- PHASE_C_EVALUATION_FRAMEWORK.md
- PHASE_C_ERRATA.md  
- NEXT.md
For every explicit requirement, confirm it was met. Don't summarize — check each one.

**Step 2: What did I skip?**
List every pipeline data file that EXISTS for these books but was never opened. Open each now and check for findings. Common misses: sanity_checks.json, prompt_sent.json fields, consensus.json disagreement details, ground_truth_comparison.json.

**Step 3: Known failure patterns** — check ALL of these explicitly:
- Invented verdict categories not in the 5-level scale (VERIFIED/PLAUSIBLE/UNVERIFIABLE/FLAG/ESCALATE)
- Shamela-ecosystem sources (shamela.ws, ketabonline, turath.io, waqfeya) counted as independent
- Author confidence read from result.json instead of llm_responses/ (always 1.0 — engine bug)
- Confidence calibration section missing (framework requires it after each session)
- Consistency self-check missing or done inline instead of as a separate pass
- web_fetch compliance below target (aim for every book, minimum 50%)
- Death dates classified as "genuine inference" when actually embedded in author_name_raw text
- Strategic analysis predictions not checked against actual results
- Cross-model field differences on non-consensus-checked fields (authority_level, science_scope, layers) not documented
- Causal claims about engine behavior asserted without tracing through actual engine data
- Running totals incorrect (verify by counting prior session verdicts from their reports)

**Minimum tool calls: 12.** Re-read files, run scripts, verify counts.
Fix everything found. Then report.
</round_1>

---

<round_2>
## ROUND 2 — ADVERSARIAL ATTACK (try to break every verdict)
**Angle:** "Assume every verdict is wrong. Try to disprove it."

**Step 1: For each VERIFIED verdict, search for counter-evidence.**
For every book rated VERIFIED, do at least one web search specifically designed to CHALLENGE the verdict — not confirm it. Examples:
- Search "[book title] disputed authorship" or "[book] attribution controversy"
- Search for alternative genre classifications that contradict the pipeline's
- Search for death date disputes that fall outside ±10 year tolerance
- For multi-layer books: search whether the layer structure is actually different from what the pipeline says

If you find genuine counter-evidence, downgrade the verdict or add a note. If the verdict survives the attack, it's genuinely verified.

**Step 2: Verify every source independence claim.**
For each source listed as "independent" in the VERIFIED threshold section:
- Is it actually independent of the Shamela ecosystem?
- Does it actually confirm the specific claim (author + death date + genre), or just mention the book?
- Would a hostile reviewer accept this source as independent verification?

**Step 3: Attack fabricated reasoning.**
For every explanatory claim in the report (not just verdicts but the reasoning), ask: "Did I actually verify this, or did I just write something plausible?" Examples:
- "The trust engine flags this because X" — did I trace through the engine code?
- "CA's values appear in result.json because CA had higher confidence" — did I verify the selection logic?
- "This is the same pattern as [other book]" — did I compare the actual data, or assume similarity?

If any reasoning is unsupported, either verify it now or replace it with "mechanism unknown."

**Minimum tool calls: 10.** Mostly web searches for counter-evidence + script verification.
Fix everything found. Then report.
</round_2>

---

<round_3>
## ROUND 3 — DOMAIN DEPTH (verify substance with external evidence)
**Angle:** "Every domain claim might be wrong. Prove each one externally."

**Step 1: For every book, verify at least one domain claim via web search.**
Not just "search for the book" — search for the SPECIFIC claim the pipeline makes. Examples:
- Pipeline says genre=hashiyah → search what type of work this actually is, verify the hashiyah chain
- Pipeline says science=['fiqh', 'usul_al_fiqh'] → search what sciences this work covers
- Pipeline says death=595 → search the actual death date from a biographical source

Use web_fetch on at least 3 pages across the session (not just search snippets).

**Step 2: Domain precision audit.** For every Islamic science term used in the report, verify correct usage:
- "sirah" = prophetic biography ONLY (not general biography)
- "tarajim" = biographical dictionary; "tabaqat" = biographical work organized by generations
- "tarikh" = historical chronicle
- "hashiyah" requires 3 layers (matn → sharh → hashiyah) — verify each layer's author
- "tahqiq" notes = editorial apparatus, NOT a scholarly commentary layer
- "fiqh_comparative" = cross-school comparative jurisprudence (not single-school fiqh)
- "mukhtasar" = abridgment of a SPECIFIC named work — verify the genre_chain
- "mawsuah" = encyclopedia — verify it's actually encyclopedic in scope
- "hadith_collection" vs "hadith" science — the genre and the science are different things

**Step 3: Confidence calibration analysis.**
Verify the calibration section exists and is substantive. Check:
- Is there a high-confidence + wrong combination? (Most dangerous pattern)
- Do confidence scores discriminate between easy and hard cases?
- Does the analysis actually say something useful, or is it just a table?

**Minimum tool calls: 10.** Mostly web searches + web_fetch for domain verification.
Fix everything found. Then report.
</round_3>

---

<round_4>
## ROUND 4 — INTEGRITY CERTIFICATION (final pass after all edits)
**Angle:** "Three rounds of edits may have introduced new errors. Find them."

**Step 1: Internal contradiction scan.**
Read the FULL report from top to bottom. For every claim made in one section, check whether any other section says something different. Prior rounds often fix the verdict but leave old text in the Notes field, or fix the Science field but not the Cross-Book Patterns section. grep for key terms and verify consistency.

**Step 2: Aggregation readiness.**
Read the report as if you are the aggregation session that will compile all sessions. Check:
- Can every verdict be parsed into the 5-level scale?
- Are running totals arithmetic correct?
- Are all required fields present in every structured verdict?
- Would a fresh Claude Chat session (with no context from this conversation) understand each verdict?

**Step 3: Verify all corrections from prior rounds were applied.**
For each "Errors found and fixed" item in prior round reports, open the file and confirm the fix is actually present. Prior str_replace calls can silently fail if the target string was already changed.

**Step 4: Final data integrity.**
Re-run read_book.py on 2 randomly selected books and spot-check that the numbers in the report match the actual pipeline data. This catches copy-paste errors and stale data.

**Minimum tool calls: 8.** File reads, greps, script runs.
Fix everything found. Then report — this is the FINAL report.
</round_4>

---

<reporting_format>
After completing your round, append this EXACT structure:

**Self-review findings (Round N):**
**Tool calls used:** [count] — [list each tool and what it checked]
**Errors found and fixed:** [specific corrections, not cosmetic — or "None" with evidence]
**Known failure patterns checked:** [which were relevant, which were clean]
**Remaining uncertainty:** [anything unresolved — or "None"]
**Round verdict:** [CLEAN — ready for next round | ERRORS FIXED — re-check recommended]
</reporting_format>

<constraints>
- Execute ONLY your current round. Do not skip ahead or combine rounds.
- Meet the minimum tool call count for your round. Fewer = insufficient verification.
- Do NOT fabricate issues. Real fixes only. If clean, list what you verified as evidence.
- Do NOT acknowledge gaps without closing them. "Should have searched more" without searching is failure.
- When in doubt about a claim, VERIFY WITH A TOOL. Introspection is unreliable.
- Time is unlimited. Depth is the only metric. Take as many tool calls as needed beyond the minimum.
</constraints>
