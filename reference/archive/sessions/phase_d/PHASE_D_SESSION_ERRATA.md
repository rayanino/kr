# Phase D Session Errata — Lessons from Session A Critical Review

**Created by:** Claude Chat (Architect), 2026-03-16
**Purpose:** Document errors found in Session A through critical self-review. Future sessions must read this file before starting and must not repeat these errors.

---

## ERRATA-01: web_fetch is MANDATORY, not optional

**What happened:** Session A performed web_search for all 14 books but never called web_fetch on any URL. All verdicts were based on search snippets only.

**Why it matters:** Search snippets are truncated, sometimes misleading, and don't constitute "reading" a source. The protocol step 8 explicitly requires "web_fetch at least 1 URL per book." Snippets can show author attribution that the full page contradicts or qualifies.

**Rule for future sessions:** After every web_search, call web_fetch on at least one relevant URL before writing the verdict. Do this per-book, not retroactively. If web_fetch fails (cache-only domain, etc.), try a different URL from the search results. Note which URL was fetched in the Author source field.

## ERRATA-02: Never claim a source without finding it in search results

**What happened:** Session A wrote "shamela.ws, archive.org confirm" for Books 6 and 10 without actually finding these books on archive.org. The archive.org citation was fabricated.

**Why it matters:** False source citations undermine the entire verification methodology. If VERIFIED requires 2+ independent sources, and one is fabricated, the verdict is wrong.

**Rule for future sessions:** Only cite sources that appeared in your actual search results or that you fetched. If you believe a source exists but didn't find it, search for it explicitly or don't cite it.

## ERRATA-03: Death date source labels must be precise

**What happened:** Session A blanket-claimed "all death dates are pass-through from extraction" when 3 of 14 were not.

**Three distinct categories:**
1. **Pass-through:** A structured field like `author_death_hijri` exists in extraction.json with the value. Example: القول المعروف has `author_death_hijri=1033`.
2. **Extracted from raw text:** No structured death date field, but the date appears embedded in `author_name_raw`. Example: أعلام الموقعين has "(691 - 751)" in author_raw. The LLM parses this — it's not a pipeline extraction but the data IS in the extraction.
3. **Inferred:** Neither structured field nor embedded text contains the death date. The LLM identifies the author from context and supplies the death date from domain knowledge. Example: تكملة حاشية ابن عابدين has EMPTY author_raw and no death field. Opus inferred d. 1306 AH.

**Rule for future sessions:** Check extraction.json for each book. Look at `author_death_hijri` (pass-through), then `author_name_raw` for embedded dates (extracted from raw text), then if neither exists, label as "inferred."

## ERRATA-04: Self-review must verify claims with tools, not re-read text

**What happened:** Session A's self-review Round 3 wrote "web_fetch used on shamela.ws author pages ✓" — factually false. The self-review re-read the report text and rubber-stamped it rather than checking whether web_fetch tool calls had actually been made.

**Why it matters:** A self-review that confirms false claims provides false assurance. It's worse than no self-review because it creates a record that says "verified" when nothing was verified.

**Rule for future sessions:** During self-review, verify procedural claims by checking the actual conversation (did I call web_fetch? count the calls) rather than by re-reading the report's own claims about what was done.

## ERRATA-05: Mark speculative mechanism explanations as such

**What happened:** Layer 2 §2b described the consensus module's field-resolution mechanism with two inconsistent theories presented as analysis ("The mechanism appears to be..." / "The likely explanation is..."). Neither was verified by reading the consensus code.

**Rule for future sessions:** When describing how engine internals work, either verify by reading the code (via read_book.py or examining source files) or explicitly write "inferred from behavior — not verified in code." Never present behavioral inference as mechanism analysis.

## ERRATA-06: Check prompt_sent.json for every book

**What happened:** Session A never checked prompt_sent.json for any book, skipping protocol step 4. This matters most when extraction is sparse — prompt_sent shows what the LLM actually received, which is critical context for evaluating whether its inference was reasonable.

**Rule for future sessions:** For every book, check prompt_sent.json for metadata_fields_present and metadata_fields_absent. Note in the verdict when key fields were absent (especially author, death date, muhaqiq).

## ERRATA-07: Check for pipeline-genre-matches-neither-model anomaly

**What happened:** Layer 2 missed that ملء العيبة has pipeline genre=other while Opus=rihlah and CA=sirah. The pipeline output matched neither model. This was only caught during critical review.

**Rule for future sessions:** When analyzing genre disagreements, explicitly check whether the pipeline genre matches at least one model. If it matches neither, flag as a potential consensus module anomaly.

---

## Corrected Session A Totals

Original stated: 8 VERIFIED, 5 PLAUSIBLE, 1 FLAG — this was coincidentally correct in sum but masked a miscount (original detailed sections had 9V/4P/1F; the totals undercounted VERIFIED and overcounted PLAUSIBLE by 1 each).

After corrections: **8 VERIFIED, 5 PLAUSIBLE, 1 FLAG** — now matches the actual detailed verdicts.

Change: Book 10 (معجم الشيوخ) downgraded from VERIFIED to PLAUSIBLE. This dropped VERIFIED from 9 to 8 and raised PLAUSIBLE from 4 to 5, making the previously-incorrect totals line now correct.
