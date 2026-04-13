# SPEC Audit B — Normalization Engine

**Auditor:** B (Patterns 5-7, Threats T1-T7)
**SPEC file:** engines/normalization/SPEC.md
**Date:** 2026-03-17

## Summary
- Total defects: 27
- CORRECTNESS: 22 (81%)
- STYLE: 5 (19%)
- Pattern 5: 8, Pattern 6: 10, Pattern 7: 9
- Threats: T1:5, T2:4, T3:2, T4:2, T5:1, T6:4, T7:2
- Sections with 0 defects: §8 (Configuration), §9 (Current Implementation State) — both are descriptive/status sections; Round 1 traces confirmed no behavioral rules to violate.

## Defect Inventory

### D-B01 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.3
**Location:** Line 285-298, PDF Normalizer
**The SPEC says:** "Use Docling (IBM, Apache 2.0) as the primary PDF parsing backend... Text-embedded PDFs default to `high`."
**The problem:** No error path is defined for when Docling fails to parse a PDF (corrupted file, password-protected, unsupported PDF version, or Docling crashes on a specific page). The SPEC has `NORM_OCR_FAILED` for OCR failures and `NORM_NO_TEXT_LAYER` for missing text, but no `NORM_PDF_PARSE_FAILED` error code for the case where Docling itself errors. Docling is experimental for Arabic — this failure is plausible.
**Corruption risk:** If a Docling failure is caught by a generic exception handler that returns empty text, the content unit would have `primary_text: ""` but not be marked `is_blank`, silently losing a page of scholarly text (T-1).
**Evidence:** §7 error table has no code for Docling parse failure. The closest is `NORM_OCR_FAILED` which explicitly says "OCR engine returns error."
**Suggested fix:** Add `NORM_PDF_PARSE_FAILED` (Fatal) error code. Define per-page recovery: if Docling fails on a single page, flag that page with `text_fidelity: "very_low"` and empty primary_text with `is_blank: false` + a warning, then continue processing remaining pages. If Docling fails on >50% of pages, abort the entire source.

### D-B02 [CORRECTNESS] — Pattern 7 / Threat T-2 — §4.B.1
**Location:** Lines 693-727, Scholarly Text Layer Intelligence
**The SPEC says:** "The normalization engine trains an LLM-based layer classifier that operates on a sliding window of text. The classifier receives: a ~500-word window, the source's known layer composition (from metadata), the commentary genre (sharh/hashiyah), and examples of each layer's writing style from the same source (bootstrapped from high-confidence detections in earlier pages)."
**The problem:** This capability requires bootstrapping from "high-confidence detections in earlier pages" — but in old prints without formatting, there may be NO high-confidence detections to bootstrap from. The SPEC does not define what happens when the bootstrapping phase produces zero examples. Also, the "terseness ratio" and "pronoun reference patterns" described are subjective content signals that require NLP capabilities (pronoun resolution, information density measurement) not specified as dependencies. This is scope creep: the normalization engine is performing authorship attribution, which is a scholarly judgment that should involve consensus (D-041).
**Corruption risk:** If bootstrapping fails silently and the LLM classifier runs with no examples, layer assignments are essentially random for old prints. All text could be attributed to the wrong author (T-2). For a source like شرح الورقات without formatting, 100% of content could be misattributed.
**Evidence:** The concrete example (lines 709-725) shows confidence 0.68-0.72 — below the conservative default threshold of 0.50, so it would default to sharh. But the example ALSO shows 0.72 for matn, which is ABOVE 0.50, meaning the classifier's output IS used. If the classifier is wrong, there is no defense.
**Suggested fix:** (1) Define the bootstrapping failure path: if <5 high-confidence segments are found, §4.B.1 is skipped and the source is processed as single-layer with a human gate. (2) Require multi-model consensus for content-based layer inference since it is an attribution decision (T-2 mitigation per reference/KNOWLEDGE_INTEGRITY.md §T-2 chain item 1). (3) Explicitly list NLP tool dependencies (CAMeL Tools morphological analysis, sentence splitter).

### D-B03 [CORRECTNESS] — Pattern 5 / Threat T-2 — §4.A.5
**Location:** Lines 511, typographic signals
**The SPEC says:** "layer-indicating bold spans typically cover 1-3 sentences of terse, definitional text, while emphasis-bold covers individual words or phrases within longer sentences"
**The problem:** "Typically" and "individual words or phrases" vs. "1-3 sentences" is untestable. What is the character-count threshold that distinguishes "a phrase" from "1 sentence"? A matn statement like "المبتدأ هو الاسم المرفوع" (6 words) could be classified as either. Two implementers would use different thresholds. The second heuristic (<5% or >60% bold per page) is testable, but the span-length heuristic is not.
**Corruption risk:** An implementer who sets the threshold too low classifies short matn segments as emphasis-bold, losing them into the sharh layer (T-2). An implementer who sets it too high classifies hadith quotations as layer indicators, creating phantom matn segments.
**Evidence:** The concrete example (line 531-548) shows a matn segment of 35 characters ("ويصح الوضوء بماء البحر"). This is shorter than many emphasized hadith quotations (e.g., "«بُنِيَ الإِسْلَامُ عَلَى خَمْسٍ»" = 28 characters). A length-only heuristic cannot distinguish them.
**Suggested fix:** Define an explicit character-count threshold (e.g., bold spans <80 characters are candidate emphasis, >=80 characters are candidate layer indicators), AND require the span to be checked against the transition marker list before classification. A bold span that begins with "قوله:" or follows a transition marker is a layer indicator regardless of length.

### D-B04 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.2, Pass 3
**Location:** Line 197
**The SPEC says:** "Remove all HTML tags (preserving text content). Decode HTML entities. Normalize line endings and whitespace per ABD rules §4.7–§4.9."
**The problem:** No error path for malformed HTML entities. If the Shamela export contains truncated entities (e.g., `&amp` without semicolon, or `&#x064` without the closing semicolon), what happens? BeautifulSoup may silently drop them, silently pass them through, or raise an error depending on the parser backend (html.parser vs. lxml vs. html5lib). The SPEC delegates to "ABD rules" but does not specify which parser or what happens on malformed entities.
**Corruption risk:** A truncated entity like `&#x064B;` (fatha) that gets mangled to `&#x064` could silently lose a diacritical mark (T-1). The diacritics drift check (§5 check 8) WOULD catch this for Shamela sources, but only if the comparison is done correctly — the check compares diacritic character COUNTS, not positions. If a malformed entity resolves to a different diacritic instead of being lost, the count matches but the text is wrong.
**Evidence:** §5 check 8 says "extract all Unicode characters in the Arabic diacritics range... If the diacritic character counts differ by even one character." Count-based comparison does not catch substitution (one diacritic replaced by another). For example, if fatha (U+064B) becomes damma (U+064F) due to entity corruption, the count is the same but the meaning changes.
**Suggested fix:** (1) Specify the HTML parser backend (lxml or html5lib, not html.parser which has known quirks). (2) Upgrade §5 check 8 from count-based to position-based comparison: each diacritic at position N in the source must match the diacritic at position N in the output.

### D-B05 [CORRECTNESS] — Pattern 7 / Threat T-3 — §4.B.10
**Location:** Lines 1300-1454, Scholarly Discourse Flow Annotation
**The SPEC says:** "the excerpting engine can extract a complete argument cycle as a single excerpt because the normalization engine has already identified where the cycle starts and ends"
**The problem:** Discourse flow annotation is performing taxonomic pre-classification. The `position_metadata.school_hint` field (line 1438: "حُكي عن مالك → school_hint: مالكي") is an attribution decision that belongs to the excerpting or taxonomy engine, not normalization. The normalization engine's job is FORMAT TRANSFORMATION — it should detect structure, not classify scholarly content. The discourse segment types (`ruling`, `evidence_quran`, `objection`, `response`, `preferred`) are taxonomic categories that require domain understanding beyond format-specific signals. This is scope creep: the normalization engine is doing the excerpting engine's job.
**Corruption risk:** If the normalization engine's discourse annotation is wrong (e.g., it classifies a `narration` as a `ruling` because of a false marker match), the excerpting engine may trust the pre-classification and extract a narrative passage as a legal ruling (T-3). The taxonomic hint "مالكي" could poison downstream school attribution if the marker was inside a quotation (T-6).
**Evidence:** §4.B.10 itself acknowledges this risk: "markers inside quotations produce false argument structure" (line 1442). The mitigation (quotation detection) relies on explicit markers that are absent in many texts.
**Suggested fix:** (1) Remove `school_hint` and `attribution_hint` from discourse flow output — these are attribution decisions that belong downstream. (2) Clearly mark discourse flow as ADVISORY metadata with zero authority over downstream taxonomic decisions. (3) Add a field `discourse_annotation_authority: "advisory"` so downstream engines know not to treat these as ground truth.

### D-B06 [CORRECTNESS] — Pattern 6 / Threat T-6 — §3, Enrichment Write-Back
**Location:** Lines 141-148
**The SPEC says:** "During normalization, the engine may discover information that should be recorded in the source metadata... These discoveries are written back to the source metadata record through the enrichment interface defined in the source engine SPEC §2."
**The problem:** No error path for enrichment write-back failure. What happens if the source metadata file is locked (another process is normalizing a different source that shares scholar data), corrupted, or the enrichment interface rejects the update? The SPEC says the write-back goes "through the enrichment interface" but does not specify: (a) whether normalization blocks on the write-back, (b) whether a failed write-back aborts normalization, (c) whether the normalized package is still valid if the write-back failed.
**Corruption risk:** If enrichment write-back fails silently, the normalized package proceeds with a `structural_format` override recorded in the manifest but NOT in the source metadata. A future re-normalization reads the stale source metadata and repeats the same detection-override cycle. Worse: if the source metadata was enriched for a DIFFERENT field by another process between the first and second normalization, the re-normalization produces a different result because it reads different metadata (T-6).
**Evidence:** §4.B.2 (line 777) says "Enrichment write-back: The source metadata's `structural_format` is updated from `"prose"` to `"qa_format"`." But §7 has no error code for write-back failure.
**Suggested fix:** Add `NORM_ENRICHMENT_WRITEBACK_FAILED` (Warning). Define: normalization completes successfully even if write-back fails (the normalized package is self-contained via `source_id` reference). Log the failed write-back. Add a reconciliation check at next normalization: if `manifest.structural_format != source_metadata.structural_format`, log and re-attempt write-back.

### D-B07 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.8
**Location:** Line 651
**The SPEC says:** "Whitespace normalization (conservative): `\r\n`/`\r` → `\n`. Non-breaking spaces → regular spaces. 2+ consecutive spaces → single space. Three+ blank lines → one blank line. Leading/trailing line whitespace trimmed."
**The problem:** No error path for encountering non-standard Unicode whitespace characters beyond NBSP. Arabic texts may contain: zero-width space (U+200B), zero-width non-joiner (U+200C — ZWNJ, explicitly preserved elsewhere), thin space (U+2009), medium mathematical space (U+205F), ideographic space (U+3000). The SPEC says "no other text transformation" but does not address whether these exotic whitespace characters are preserved or normalized. An implementer might normalize them (data loss) or preserve them (downstream parsing issues).
**Corruption risk:** ZWNJ (U+200C) is explicitly used as a heading marker in 9.5% of Shamela corpus (line 203). If a whitespace normalization step inadvertently normalizes ZWNJ to regular space or removes it, heading detection breaks AND the primary text is corrupted (T-1).
**Evidence:** §4.A.2 Pass 3 (line 197) says "Preserve asterisks, ZWNJ characters, and all other source data markers." But §4.A.8's whitespace rules say "Non-breaking spaces → regular spaces" without listing what IS and IS NOT a "non-breaking space." Unicode has multiple non-breaking space characters (U+00A0, U+202F narrow no-break space, U+FEFF zero-width no-break space / BOM).
**Suggested fix:** Explicitly enumerate which Unicode whitespace characters are normalized and which are preserved. At minimum: U+00A0 (NBSP) → regular space. U+200C (ZWNJ) → PRESERVED. U+200B (zero-width space) → PRESERVED (may be intentional). U+FEFF (BOM) → stripped only at file start. All others → preserved with info-level log.

### D-B08 [CORRECTNESS] — Pattern 5 — §4.A.9
**Location:** Lines 657-658
**The SPEC says:** "`has_quran_citation`: Quran citation markers detected ({verse text}, 'قال تعالى', surah/ayah references). `has_hadith_citation`: hadith citation patterns detected ('قال النبي ﷺ', 'عن ... قال', collection references)."
**The problem:** The Quran and hadith detection patterns are incompletely specified. "Surah/ayah references" — what format? "Collection references" — which collections? Two implementers would produce different detection rates. More critically, the pattern "عن ... قال" is extremely common in non-hadith contexts (e.g., "عن ابن قدامة قال" — reporting a scholar's opinion, not a hadith). The `...` wildcard makes the pattern match almost any Arabic narrative sentence that quotes a person.
**Corruption risk:** This is STYLE (advisory flags), not CORRECTNESS in isolation. But if downstream engines use `has_hadith_citation: true` to adjust extraction strategy, a false positive could cause the excerpting engine to search for non-existent hadith takhrij data, wasting effort or producing confused metadata (T-6 via false flag).
**Evidence:** The SPEC itself says "Flags are advisory. Downstream engines may override based on deeper analysis." (line 665). However, §4.B.5 content census uses these flags for `hadith_citation_ratio` which feeds downstream strategy selection.
**Suggested fix:** Define the detection patterns precisely: (a) Quran: curly braces `{...}` containing Arabic text, OR "قال تعالى" / "قال الله تعالى" / "قال عز وجل" within 200 chars of text in curly braces or guillemets. (b) Hadith: "قال النبي" / "قال رسول الله" / "عن النبي ﷺ" / guillemet-bracketed text `«...»` preceded by narrator chain, OR explicit collection reference (البخاري, مسلم, الترمذي, أبو داود, النسائي, ابن ماجه + a number).

### D-B09 [CORRECTNESS] — Pattern 7 / Threat T-6 — §4.B.4
**Location:** Lines 832-877, Footnote Apparatus Classification
**The SPEC says:** "Each footnote is classified using pattern matching (for structured markers like 'رواه البخاري') and LLM classification (for footnotes without clear markers)."
**The problem:** The fine-grained footnote taxonomy (`variant_reading`, `hadith_takhrij`, `cross_reference`, `biographical_note`, `linguistic_note`, `correction_note`, `general_commentary`) requires SCHOLARLY UNDERSTANDING to classify accurately. Pattern matching works for clear cases but LLM classification of ambiguous footnotes is a content decision that the reference/KNOWLEDGE_INTEGRITY.md says should use consensus (D-041: "Multi-model consensus for all attribution decisions"). The SPEC explicitly uses single-model LLM classification (§6, line 1542: "Footnote classification: Single-model with pattern matching as primary, LLM as fallback").
**Corruption risk:** A `correction_note` misclassified as `variant_reading` tells the synthesizer that the editor is reporting manuscript variation when in fact the editor is asserting the text is WRONG. The synthesizer might present the "variant" as a legitimate alternative reading when it is actually an error (T-6). A `hadith_takhrij` misclassified as `general_commentary` causes the loss of hadith grading data that the synthesizer needs for evidence-aware entries.
**Evidence:** §6 (line 1542) explicitly exempts footnote classification from consensus. The justification is "pattern matching as primary, LLM as fallback" — but pattern matching cannot distinguish `correction_note` from `variant_reading` when both use similar language (e.g., "في نسخة أ: كذا" could be either).
**Suggested fix:** (1) Require consensus for footnotes where pattern matching is ambiguous (confidence < 0.85). (2) Add a `classification_method` field ("pattern" vs "llm" vs "consensus") to each footnote so downstream engines can weight accordingly. (3) Define explicitly which footnote types are distinguishable by pattern alone and which require LLM/consensus.

### D-B10 [CORRECTNESS] — Pattern 6 / Threat T-7 — §4.A.2, Pass 1
**Location:** Line 190
**The SPEC says:** "For multi-volume sources, process each file with its volume number derived from the filename stem."
**The problem:** No error path for volume number derivation failure. What if the filename stem is not a number (e.g., `المجلد_الأول.htm`, `vol_one.htm`, or a corrupted filename)? What if two files produce the same volume number? What if files are present that are NOT volume files (e.g., an index file, a cover page file)? The SPEC says "derived from the filename stem" but gives no pattern or fallback.
**Corruption risk:** If volume numbers are assigned incorrectly, pages from volume 2 could receive volume 1's number. The passaging engine and citation system would produce wrong citations: "المغني ج١ ص٢٤٥" when the text is actually from ج٢ (T-7 — same page number in different volumes treated as duplicates, or wrong volume in citations).
**Evidence:** §5 check 2 (coverage check) validates page COUNT but not volume assignment correctness. No check verifies that volume numbers extracted from filenames match volume numbers found in the content.
**Suggested fix:** (1) Define the filename-to-volume-number parsing rule explicitly (e.g., numeric suffix after stripping extension, or regex pattern). (2) Add a `NORM_VOLUME_NUMBER_UNPARSEABLE` error code (Warning). (3) Cross-validate: after Pass 1, compare filename-derived volume numbers against any volume references found in PageHead elements or content. Mismatches trigger `NORM_VOLUME_MISMATCH` (Warning) + human gate.

### D-B11 [CORRECTNESS] — Pattern 5 / Threat T-2 — §4.A.5
**Location:** Lines 515-518, content-based inference
**The SPEC says:** "Terse, definitional text → likely Layer 1 (matn). Explanatory, discursive text → likely Layer 2 (sharh). Opinion reporting verbs (قال, ذهب, يرى) → likely Layer 2."
**The problem:** "Terse" and "explanatory, discursive" are untestable subjective criteria. More critically, the verb "قال" appears in BOTH layers: the matn author writes "قال أبو حنيفة" (reporting a position) and the sharh author writes "قال المصنف" (referencing the matn). The SPEC lists "قال" as a Layer 2 signal without distinguishing its usage. An implementer treating all "قال" occurrences as sharh signals would misclassify matn text that reports scholarly positions.
**Corruption risk:** In fiqh texts, the matn frequently contains "قال" with attribution (e.g., "قال أحمد: يجوز"). If this is classified as Layer 2 (sharh), the matn author's reporting of scholarly positions is attributed to the commentator (T-2).
**Evidence:** The verb "قال" is among the most frequent words in Arabic scholarly text. In al-Mughni alone, it appears thousands of times in both matn and sharh contexts.
**Suggested fix:** (1) Replace subjective "terse/explanatory" with quantitative metrics (sentence length < 15 words, information density > 0.65 → likely matn). (2) Refine "قال" heuristic: "قال المصنف/قال الشيخ" → Layer 2 reference TO matn author. "قال أبو حنيفة/قال مالك" → could be either layer, do NOT use as layer signal. (3) Specify that content-based inference (lowest reliability tier) is NEVER used alone — it only confirms or weakens typographic/marker signals.

### D-B12 [STYLE] — Pattern 5 — §4.A.6
**Location:** Line 566, ZWNJ heading markers
**The SPEC says:** "ZWNJ heading markers (double ZWNJ at line start, 9.5% of Shamela corpus)."
**The problem:** "Double ZWNJ at line start" is imprecise. Does this mean two consecutive U+200C characters? Or two U+200C characters separated by something? What is "line start" — the first non-whitespace position, or byte position 0 of the line? How many characters after the double ZWNJ constitute the heading text — until end of line, until the next sentence, until a specific terminator?
**Evidence:** This is a STYLE issue because the behavior is likely well-defined in the ABD reference documents (line 1631: "15 ABD-era reference documents"). But the SPEC should be self-contained.
**Suggested fix:** Define: "Two consecutive U+200C characters (with no intervening characters) at the first non-whitespace position of a line. The heading text extends from after the ZWNJ pair to the end of the line or the next period/full stop, whichever comes first."

### D-B13 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.4, OCR
**Location:** Lines 356-358
**The SPEC says:** "Page rendering. For PDFs: render each page at 300+ DPI (600 DPI for scholarly texts with small print). For images: use as-is with pre-processing."
**The problem:** No error path for image pre-processing failure. "Perspective correction for angled photos" (line 370) can fail on severely distorted images. "Auto-detect orientation and rotate" can detect the wrong orientation for Arabic text (Arabic RTL can confuse orientation detectors trained on LTR languages). If orientation detection rotates the page 180 degrees, OCR produces text from the bottom of the page upward — valid Arabic words in reverse page order.
**Corruption risk:** A 180-degree rotation produces text that reads bottom-to-top. Each individual line may OCR correctly (Arabic RTL within a line is preserved), but the LINE ORDER is reversed. The primary_text would contain correct Arabic sentences in wrong sequence — essentially scrambling the scholarly argument (T-1, T-4). This would not be caught by §5 check 3 (the text is valid Arabic with >70% Arabic characters).
**Evidence:** Orientation detection is listed as a capability but has no error handling. The §7 error table has no code for orientation detection failure.
**Suggested fix:** Add `NORM_ORIENTATION_UNCERTAIN` (Warning). After orientation detection, validate: (a) the first line of OCR output should not begin with a sentence-ending pattern, (b) the last line should not begin with "بسم الله الرحمن الرحيم" or a chapter heading (signs of reversed page). If validation fails, try the 180-degree alternative and compare OCR confidence. Present both to human gate if ambiguous.

### D-B14 [CORRECTNESS] — Pattern 7 / Threat T-5 — §4.B.3
**Location:** Lines 781-830, Fine-Grained Text Fidelity Mapping
**The SPEC says:** "Morphological validation: words that don't exist in the Arabic lexicon are lower-fidelity than valid words"
**The problem:** This requires a comprehensive Arabic lexicon, which the normalization engine does not have as a declared dependency. CAMeL Tools is mentioned (line 1668) for morphological analysis, but its lexicon coverage for classical Arabic scholarly terminology is unknown. Classical fiqh texts contain specialized terms (e.g., istihsan, istihlak) that may not be in a modern Arabic lexicon. If the morphological validator flags valid classical terms as non-existent, fidelity scores are artificially lowered, and pages of correct text are sent for unnecessary human review.
**Corruption risk:** If the morphological validator rejects valid classical Arabic, the fidelity map becomes unreliable. Downstream engines that trust high-fidelity markers may distrust correct text, and the "correction" process could introduce errors by "fixing" terms that were correct (T-5 — the correction creates text not in the source).
**Evidence:** The SPEC depends on "the Arabic lexicon" without specifying which lexicon or its coverage of classical scholarly Arabic. CAMeL Tools' morphological analyzer covers Modern Standard Arabic primarily.
**Suggested fix:** (1) Specify the lexicon: CAMeL Tools + a supplementary classical Arabic term list derived from the KR technical glossary (which already exists per §4.B.5). (2) Define the failure mode: words not in the lexicon receive `fidelity: "unknown"` (not "low"), and only words that the morphological analyzer POSITIVELY identifies as impossible Arabic morphemes receive `fidelity: "low"`. (3) Require human gate when >20% of unique words on a page are flagged as unknown.

### D-B15 [CORRECTNESS] — Pattern 6 / Threat T-4 — §4.B.8
**Location:** Lines 1115-1207, Cross-Page Continuity Intelligence
**The SPEC says:** "Non-page-based sources (plain text, owner-authored): `boundary_continuity` is null for all content units (boundaries are artificial)."
**The problem:** Setting continuity to null for ALL plain text boundaries means the passaging engine receives NO continuity guidance for these sources. But plain text content units are split at paragraph boundaries or ~2000-character intervals (§4.A.4c, line 457). A 2000-character split could fall mid-sentence or mid-argument. The passaging engine, receiving null continuity, treats all boundaries as equally valid split points, potentially fracturing arguments.
**Corruption risk:** A plain text source of 20,000 characters split at 2000-character intervals could have an argument split mid-sentence at position 2000. Without continuity signals, the passaging engine creates a passage boundary there. An excerpt from the first passage ends mid-sentence; an excerpt from the second passage starts mid-sentence — both are context-deficient (T-4).
**Evidence:** §4.B.8 provides continuity analysis for Shamela, PDF, and OCR sources but explicitly excludes plain text and owner-authored content. Yet §4.A.4c says content units are created "at paragraph boundaries OR ~2000-character intervals" — the 2000-character case needs continuity analysis.
**Suggested fix:** For plain text sources, compute `boundary_continuity` using punctuation analysis (the same algorithm used for Shamela without the format-specific signals). Boundaries at paragraph breaks → `section_break`. Boundaries at 2000-character splits within paragraphs → `mid_paragraph` or `mid_sentence` based on terminal punctuation.

### D-B16 [CORRECTNESS] — Pattern 7 / Threat T-6 — §4.B.7
**Location:** Lines 1018-1113, Tahqiq Apparatus Topology Extraction
**The SPEC says:** "The normalization engine extracts from the footnote apparatus a manuscript witness network — a structured graph of which manuscripts and editions the tahqiq editor consulted"
**The problem:** This capability depends entirely on §4.B.4 (footnote classification) producing correct `variant_reading` classifications. But §4.B.4 uses single-model LLM classification for ambiguous footnotes (see D-B09). The topology extraction compounds the classification error: a misclassified footnote produces a wrong manuscript witness entry, which feeds into the "textual stability signals for synthesis" (line 1104). The topology is presented as factual scholarly data ("which manuscripts the editor consulted") but is derived from potentially unreliable classification. More critically, this is scope creep: extracting a "manuscript witness network" requires understanding codicological notation, which is a specialized scholarly skill beyond format transformation.
**Corruption risk:** If a `general_commentary` footnote is misclassified as `variant_reading`, the topology records a phantom manuscript disagreement. The synthesizer reports "manuscripts disagree on this passage" when in fact there is no disagreement — only an editor's general comment (T-6).
**Evidence:** Lines 1108-1110 handle the case where "Editor uses the apparatus but never names manuscripts" but do not handle the case where the footnote is not actually a variant reading at all.
**Suggested fix:** (1) Add a confidence field to the topology: `topology_confidence` derived from the mean confidence of the `variant_reading` footnotes that feed it. (2) When topology_confidence < 0.85, add a `topology_reliability: "uncertain"` flag. (3) The synthesizer MUST check `topology_reliability` before citing variant reading data.

### D-B17 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.2, Pass 2
**Location:** Lines 192-195
**The SPEC says:** "Split at `<hr width='95'>` to separate primary text from footnotes. If the separator is absent on a page, the entire page content is treated as primary text with no footnotes."
**The problem:** The separator detection is exact-match on `<hr width='95'>`. The SPEC acknowledges non-standard separators in Appendix A.1 Cascade 1 (line 1804: "a non-standard footnote separator e.g., `<hr width='90'>`"). But the error handling only logs `NORM_FOOTNOTE_SEPARATOR_ABSENT` at info severity. The SPEC does not define a fuzzy match or list known alternative separator patterns. A Shamela export with `<hr width="95">` (double quotes instead of single quotes) or `<hr width='95' />` (self-closing) would not match the exact pattern.
**Corruption risk:** Footnote text injected into primary_text is attributed to the source author (T-1). The Appendix A.2 Cascade 1 trace shows this leads to "false scholarly claims" — editor's corrections presented as the author's opinions.
**Evidence:** Appendix A.1 Cascade 1 (line 1803-1815) fully traces this cascade and upgrades severity for tahqiq editions. But the fix only elevates severity — it does not add fuzzy matching to prevent the cascade from starting.
**Suggested fix:** Define separator detection as: any `<hr>` element with a `width` attribute between 80 and 100 (inclusive), regardless of quote style or self-closing syntax. This catches `<hr width='90'>`, `<hr width="95">`, `<hr width='95' />`, etc. If no `<hr>` element exists on a page at all, then `NORM_FOOTNOTE_SEPARATOR_ABSENT` applies.

### D-B18 [STYLE] — Pattern 5 — §4.B.5
**Location:** Lines 886-888
**The SPEC says:** "`sparse_page_count` (int, pages with <200 chars), `dense_page_count` (int, pages with >3000 chars)."
**The problem:** The thresholds 200 and 3000 are presented without justification. Are these based on empirical analysis of the Shamela corpus? What distribution of Arabic scholarly texts informed these cutoffs? If the owner's library is primarily short devotional texts or very dense legal compendia, these defaults may be inappropriate.
**Evidence:** These are configurable-seeming values hardcoded in the SPEC without a configuration parameter in §8.
**Suggested fix:** Either (a) add these as configuration parameters in §8 with the current values as defaults, or (b) add a brief justification (e.g., "200 chars corresponds to approximately 30 Arabic words, the minimum for a meaningful page; 3000 chars corresponds to approximately 450 words, the 95th percentile in the Shamela corpus").

### D-B19 [CORRECTNESS] — Pattern 7 / Threat T-3 — §4.B.2
**Location:** Lines 729-779, Structural Format Auto-Detection
**The SPEC says:** "Auto-detection results are compared against the source engine's initial genre classification. If they disagree... the normalizer's detection in the manifest's `structural_format` field, with a note that it overrides the source metadata's classification. An enrichment write-back updates the source metadata."
**The problem:** The normalization engine is OVERRIDING the source engine's classification and writing the override back to source metadata. This is a taxonomic decision (T-3). The source engine's genre classification was produced with multi-model consensus (D-041). The normalization engine's format detection uses single-source content analysis of the first 20 pages. Overriding a consensus-validated classification with a single-engine heuristic is a regression in confidence. Furthermore, the detection thresholds are arbitrary: Q&A requires >30% marker pages, tabular_khilaf >20%, verse >50%. These thresholds are different for different formats with no stated justification.
**Corruption risk:** A fiqh book that quotes 8 fatwas in its first 20 pages (40% Q&A pattern) is reclassified from `prose` to `qa_format`. The passaging engine then creates passage boundaries at question-answer pairs throughout the ENTIRE book, even though only the first section is Q&A. The rest of the book receives wrong passage boundaries (T-3 — taxonomic misplacement of passages).
**Evidence:** §4.B.2 samples only the first 20 content units (line 733). A source that begins with a fatwa compilation section but transitions to discursive commentary would be misclassified.
**Suggested fix:** (1) The normalization engine should NOT override the source engine's classification — it should PROPOSE an alternative and record both. The `structural_format` in the manifest should be the normalization engine's detection, but the source metadata should NOT be overwritten without human gate approval. (2) Increase the sample to all content units (not just 20) for format detection. (3) Support `mixed` classification with per-division format annotation instead of a single source-level label.

### D-B20 [CORRECTNESS] — Pattern 6 / Threat T-7 — §4.A.2
**Location:** Line 234, atomic write procedure
**The SPEC says:** "If a previous `normalized/` directory exists (reprocessing), it is renamed to `normalized_prev_{timestamp}/` before the swap, then deleted only after the new package passes verification."
**The problem:** No error path for the case where a `normalized_prev_{timestamp}/` directory ALREADY exists from a previous interrupted reprocessing. If two reprocessing attempts both fail at the final deletion step, there would be two `normalized_prev_*` directories. The interrupted write recovery (line 236) handles `normalized_tmp_*` + `normalized_prev_*` but does not handle multiple `normalized_prev_*` directories. Which one is the correct fallback?
**Corruption risk:** If recovery selects the wrong `normalized_prev_*` directory, the source reverts to a stale normalization (T-7 — the same source has been processed differently at different times, and the wrong version is restored).
**Evidence:** The recovery rule says "if a `normalized_prev_*` directory exists" (singular). With multiple prev directories, the behavior is undefined.
**Suggested fix:** Recovery should select the `normalized_prev_*` with the LATEST timestamp. Additionally, the atomic write procedure should check for existing `normalized_prev_*` directories and delete them before creating a new one (ensuring at most one prev directory exists at any time).

### D-B21 [STYLE] — Pattern 5 — §4.B.9
**Location:** Line 1267
**The SPEC says:** "Pages where the local fingerprint diverges by >2.5 standard deviations from the global fingerprint are flagged as potential misattribution."
**The problem:** The threshold 2.5 standard deviations is presented without justification. In a normal distribution, 2.5 SD corresponds to the 99.4th percentile — meaning only 0.6% of pages would be flagged even with random fingerprints. For a 400-page source, this flags ~2.4 pages. If 15% of pages are misattributed (the scenario in Attack 1, line 1868), the flagging rate should be much higher. The threshold may be too permissive.
**Evidence:** Appendix A.4 Attack 1 (line 1870) acknowledges: "The fingerprint's Mahalanobis distance threshold (>2.5 std dev) may not catch pages where the misattribution is partial."
**Suggested fix:** Either (a) justify the 2.5 threshold with empirical data from real Arabic scholarly texts, (b) make it configurable in §8, or (c) use a more sensitive threshold (e.g., 2.0 SD) with a minimum-flagging rule (flag at least N% of pages in sources where any anomaly is detected).

### D-B22 [CORRECTNESS] — Pattern 6 / Threat T-1 — §4.A.4
**Location:** Lines 343-414, Scanned PDF and Image Normalizer
**The SPEC says:** "Send to Mistral OCR 3 via API. Parse returned Markdown..."
**The problem:** No error path for Mistral OCR API returning valid but EMPTY Markdown for a page that clearly has content (the API succeeds with 200 OK but returns no text). This differs from `NORM_OCR_FAILED` (API error/empty result) — the API technically succeeded. Some OCR APIs return empty results for pages they cannot process, without an error status. The difference matters because `NORM_OCR_FAILED` triggers a retry, but an "empty success" might not.
**Corruption risk:** An empty-success page produces a content unit with empty `primary_text` and `is_blank: false` (the source image clearly has content). The text is silently lost (T-1). §5 check 3 says "primary_text must be non-empty (except for `is_blank` pages)" — this WOULD catch it, but only if `is_blank` is correctly set to false.
**Evidence:** §5 check 3 provides the defense, but the SPEC should define the behavior proactively rather than relying on validation to catch it.
**Suggested fix:** Define: after OCR returns, if `primary_text` is empty or <10 characters AND the page image is not blank (DPI/pixel analysis shows content), treat as `NORM_OCR_FAILED` and trigger the retry/fallback chain regardless of API status code.

### D-B23 [CORRECTNESS] — Pattern 7 / Threat T-6 — §4.B.9
**Location:** Lines 1209-1298, Authorial Voice Fingerprint
**The SPEC says:** "When the source metadata identifies the matn author as having other works already in the library, the engine compares this source's matn fingerprint against the author's known fingerprint from single-layer works."
**The problem:** This cross-source fingerprint comparison requires the normalization engine to READ the library's existing normalized packages for other sources by the same author. This means the normalization engine must query the source registry, find other sources by the same `author_canonical_id`, locate their normalized packages, and read their `layer_fingerprints`. This is a significant scope expansion: the normalization engine is no longer just transforming a single source — it is performing library-wide author verification. This crosses a module boundary: the normalization engine should produce a fingerprint and let a higher-level validation layer (Layer 3 in reference/KNOWLEDGE_INTEGRITY.md) perform cross-source comparison.
**Corruption risk:** If the cross-source comparison uses a contaminated reference fingerprint (Appendix A.4 Attack 2, line 1874-1878), it INCREASES confidence in wrong layer attributions, actively poisoning the validation (T-6). The minimum-sources rule (≥2 sources) mitigates this but does not eliminate it — if both sources have the same systematic bias (e.g., both are Shamela exports with the same bold-formatting convention error), the contamination is confirmed rather than detected.
**Evidence:** Appendix A.4 Attack 2 explicitly identifies this contamination risk and adds the minimum-sources rule. But the root cause is that the normalization engine is performing library-wide validation that exceeds its scope.
**Suggested fix:** (1) Cross-source fingerprint comparison should be a SEPARATE validation step (Layer 3 integrity check), not part of the normalization engine's per-source processing. The normalization engine computes and stores the fingerprint; a library-wide validator compares across sources. (2) If kept in the normalization engine, add a `cross_source_validation_confidence` field that reflects the reliability of the reference fingerprints used.

### D-B24 [STYLE] — Pattern 5 — §5 Check 3
**Location:** Line 1470
**The SPEC says:** ">70% Arabic characters (excluding whitespace and punctuation). A page with <70% Arabic characters is flagged as potentially corrupted."
**The problem:** The 70% threshold is reasonable for pure Arabic texts but may be too high for texts with heavy footnote apparatus containing Latin transliteration, publisher information in French/English (common in Maghrebi editions), or mathematical notation in legal texts (inheritance calculation chapters). These pages would be falsely flagged.
**Evidence:** This is a testable rule, so the imprecision is minor. But tahqiq editions of North African scholars often include French publisher information, and inheritance (mawaarith) chapters include mathematical fractions.
**Suggested fix:** Add exceptions: (a) pages with `content_flags.is_index_page: true` or `is_toc_page: true` are exempt from the 70% check, (b) add a per-source configuration override for the threshold, (c) document that 70% is the default with known exceptions for mixed-script content.

### D-B25 [CORRECTNESS] — Pattern 6 / Threat T-4 — §4.A.6
**Location:** Lines 552-609, Structure Discovery
**The SPEC says:** "For regions with no signals, assign the default layer (Layer 2 in sharh, Layer 3 in hashiyah)."
**The problem:** This rule is in §4.A.5 (line 525) for layer detection, not §4.A.6. But the structure discovery section has a related gap: when structure discovery detects a heading at a specific location, there is no defined behavior for what happens if the heading TEXT is damaged or partially unreadable (common in OCR sources). §4.A.6 defines `heading_text` as a string but does not specify what value it takes when OCR only partially reads the heading (e.g., "باب ال..." where the rest is unreadable).
**Corruption risk:** A partial heading "باب ال..." entered as `heading_text` propagates to the passaging engine's `division_path` and eventually to the citation system. The owner sees "باب ال..." as a division label — uninformative at best, misleading at worst. If OCR hallucinates the missing text, the heading could be wrong (T-4 — context loss through corrupted heading).
**Evidence:** §4.A.6 mentions heading confidence (Tiers 1-4) but not heading TEXT quality. A Tier 1 heading in OCR could have confirmed structural detection but partially corrupted text.
**Suggested fix:** Add a `heading_text_fidelity` field (high/medium/low/partial) to structural_markers. When OCR confidence for heading characters is <0.80 on average, set `heading_text_fidelity: "low"`. When >20% of heading characters are uncertain, set `heading_text_fidelity: "partial"`. Downstream engines receiving partial headings know to present them with uncertainty markers.

### D-B26 [STYLE] — Pattern 5 — §4.B.10
**Location:** Line 1335
**The SPEC says:** "For pages where marker-based detection produces fewer than 2 segments (i.e., the text is largely unmarked scholarly prose), invoke an LLM to classify paragraphs by discourse function."
**The problem:** "Fewer than 2 segments" as the threshold for invoking an LLM is arbitrary and could be very expensive. A 500-page source where 300 pages have <2 detected markers would require 300 LLM calls for discourse classification. No cost control or budget limit is defined for discourse flow LLM calls, unlike OCR where `max_api_cost_per_source` is defined (line 1014).
**Evidence:** §4.B.6 (OCR) defines `max_api_cost_per_source` (default $50) for cost control. No equivalent exists for discourse flow LLM calls.
**Suggested fix:** Add a cost control: (a) max LLM calls per source for discourse flow (e.g., 50 calls), (b) if the threshold is exceeded, remaining pages receive `discourse_flow: null`, (c) add this to §8 configuration table.

### D-B27 [CORRECTNESS] — Pattern 6 / Threat T-2 — §4.A.5
**Location:** Lines 520-529, detection algorithm
**The SPEC says:** "Start with the source metadata's layer specification... For regions with no signals, assign the default layer (Layer 2 in sharh, Layer 3 in hashiyah)."
**The problem:** Step 1 says "Start with the source metadata's layer specification." But the source metadata's `text_layers` field (from the source engine) contains `author_canonical_id` values. What happens when the source engine's `author_canonical_id` for the matn author is WRONG? The normalization engine propagates this wrong ID into every `text_layers` segment. There is no validation that the `author_canonical_id` values in the source metadata are correct — the normalization engine trusts them completely.
**Corruption risk:** If the source engine's consensus incorrectly identified the matn author (e.g., attributing الروض المربع to ابن قدامة instead of الحجاوي), EVERY layer segment in the entire normalized package carries the wrong `author_canonical_id`. All downstream engines attribute text to the wrong scholar (T-2). This is not caught by any §5 validation check — the checks verify consistency with source metadata, not correctness of source metadata.
**Evidence:** §5 check 4 says "Layer `author_canonical_id` values match the source metadata's layer specification." This ensures consistency but not correctness. If the source metadata is wrong, the check PASSES while the data is corrupt.
**Suggested fix:** (1) This is fundamentally an upstream problem (source engine), but the normalization engine should add a CROSS-CHECK: compare the `author_canonical_id` against the layer fingerprint's stylometric properties. If the matn author's fingerprint differs dramatically from the same author's fingerprint in other library sources, flag `NORM_AUTHOR_FINGERPRINT_MISMATCH` (Warning). (2) Add this cross-check to §4.B.9 validation explicitly.

## Self-Review Notes

### Round 1 — Zero-Defect Section Traces

**§8 (Configuration):** Traced through: what if `fidelity_high_threshold` (0.95) is set to 0.99? Then almost all OCR pages would be medium/low fidelity, triggering mass human gate reviews. But this is a valid configuration choice, not a SPEC defect — the ranges are constrained (0.85-0.99). What if `layer_matn_max_ratio` is set to 0.10? Then any source with >10% matn text triggers a Layer 1 proportion warning. Again, this is a valid (if aggressive) configuration. No defect.

**§9 (Current Implementation State):** This is purely descriptive. Traced: what if the "292 tests" referenced are actually 0 tests? This would be a documentation accuracy issue, not a behavioral SPEC defect. No defect in scope.

**Appendix A (Hardening Analysis):** Re-read all 12 scenarios. Scenario 3 (PageHead injection) — the fix says "if PageHead text does NOT match any heading pattern AND exceeds 100 characters, treated as primary text." But what if it is exactly 100 characters? The threshold should be ">100" not "exceeds 100" for precision. However, this is in the Appendix (analysis section), not a behavioral rule in §4. The actual §4.A.6 rule (line 558-560) says "PageHead elements are Shamela's navigation metadata, NOT part of the author's text. They are recorded in structural_markers but EXCLUDED from primary_text." The Appendix adds a clarification that is not reflected back in §4.A.6. This is a minor inconsistency but within Appendix scope (it documents the fix as "SPEC fix needed" but the §7 error code was added). Not counted as a new defect since the Appendix is self-documenting analysis.

**§2 (Input Contract):** Traced: شرح ابن عقيل arrives with `source_format: "shamela_html"`, `is_multi_layer: true`, `text_layers: [{matn, ibn_malik_672}, {sharh, ibn_aqil_769}]`. Input validation passes. What if `genre` is missing? §2 lists genre as a read field but does not list it among the "required fields" in validation step 2. Is genre required? If not, what default does the normalizer use for genre-dependent processing (e.g., nazm-triggered verse-aware processing)? This is borderline — the input validation lists "required fields" but does not exhaustively enumerate them. I decided NOT to add this as a defect because the SPEC says "required fields listed above" and the list includes genre implicitly (line 53: "genre: affects normalization strategy"). But the ambiguity about which fields are REQUIRED vs. OPTIONAL for input validation is worth noting.

### Round 2 — Ratio Check

CORRECTNESS: 22 (81%)
STYLE: 5 (19%)

Ratio passes the >80% STYLE check (only 19% STYLE). Threat distribution:
- T-1 (Silent Text Corruption): 5 defects — concentrated in HTML parsing, OCR, and whitespace normalization. These are the highest-risk areas for the normalization engine.
- T-2 (Attribution Error): 4 defects — concentrated in layer detection and author ID propagation. Layer misattribution is correctly identified as the highest-integrity-risk operation.
- T-3 (Taxonomic Misplacement): 2 defects — discourse flow annotation and format auto-detection overriding upstream classification.
- T-4 (Context Loss): 2 defects — plain text continuity gap and partial heading text in OCR.
- T-5 (Synthesis Hallucination): 1 defect — morphological validation creating false corrections.
- T-6 (Metadata Poisoning): 4 defects — enrichment write-back, footnote classification, topology extraction, cross-source fingerprint contamination.
- T-7 (Duplication and Contradiction): 2 defects — volume number parsing and atomic write recovery with multiple prev directories.

The distribution reflects the normalization engine's primary risks: text corruption (T-1) and attribution error (T-2) dominate, which aligns with the engine's role as the format transformation layer that produces the text and layer annotations every downstream engine consumes.
