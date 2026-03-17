# SPEC Adversary Catalog — Normalization Engine

**Date:** 2026-03-17
**SPEC file:** engines/normalization/SPEC.md
**SPEC lines:** 2,047
**Total adversarial cases:** 51
**By category:** boundary_value: 10, arabic_trap: 10, silent_corruption: 15, format_edge_case: 11, multi_signal_conflict: 5

**Purpose:** These test cases are designed to catch WRONG implementations that would still pass superficial testing. Each case targets a specific SPEC rule and describes the input that would distinguish a correct implementation from a naive one.

**Coverage gaps (deferred normalizers):** Sections §4.A.3 (PDF text normalizer), §4.A.4 (scanned PDF/image normalizer), §4.A.4a–§4.A.4d (EPUB, Word, plain text, owner content normalizers) are marked [NOT YET IMPLEMENTED] in the SPEC. No adversarial cases are provided for these sections. Write adversarial cases when each normalizer is implemented.

---

## §4.A.2 — Shamela Normalizer

### ADV-001 boundary_value — Footnote separator width at lower boundary

**SPEC rule:** "Split at any `<hr>` tag whose `width` attribute has a numeric value between 80 and 100 (inclusive)."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 12)</span>
المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية
(1) هذا تعريف النحويين
<hr width='79'>
(1) انظر شرح الكافية للرضي
</div>
```

**Correct behavior:** `<hr width='79'>` is NOT a footnote separator (79 < 80). The entire page content including "(1) انظر شرح الكافية" is treated as primary text. The footnote array is empty.
**Wrong behavior (naive impl):** Uses `width >= 75` or `width > 0` — treats the `<hr>` as a separator and incorrectly splits the content.
**Why it matters:** Text after the `<hr>` would be silently moved to footnotes, removing scholarly content from the primary text (T-4 Context Loss).
**Detection:** Assert `len(content_unit.footnotes) == 0` and assert "انظر شرح الكافية" is in `primary_text`.

---

### ADV-002 boundary_value — Footnote separator width at upper boundary

**SPEC rule:** "Split at any `<hr>` tag whose `width` attribute has a numeric value between 80 and 100 (inclusive)."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 15)</span>
باب الصلاة
<hr width='101'>
(1) الصلاة لغة الدعاء
</div>
```

**Correct behavior:** `<hr width='101'>` is NOT a footnote separator (101 > 100). Entire content is primary text.
**Wrong behavior (naive impl):** Uses `width <= 110` or any `<hr>` with width attribute — incorrectly splits.
**Why it matters:** Same as ADV-001. Text silently moved from primary_text to footnotes.
**Detection:** Assert empty footnotes array; assert "الصلاة لغة الدعاء" is in `primary_text`.

---

### ADV-003 format_edge_case — Footnote separator with percentage width

**SPEC rule:** Regex: `<hr\s+[^>]*width\s*=\s*['"]?(\d{2,3})['"]?[^>]*>` where captured group is 80-100.
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 20)</span>
فصل في المسح على الخفين
<hr width="95%">
(1) ثبت المسح في أحاديث كثيرة
</div>
```

**Correct behavior:** `width="95%"` — the regex captures `95` from `95%`. The `%` character is NOT part of the `\d{2,3}` group, so `95` IS captured and IS in range 80-100. This SHOULD be treated as a footnote separator.
**Wrong behavior (naive impl):** (a) Strips `%` before parsing and works correctly — acceptable. (b) Rejects because the value contains non-numeric character — incorrectly keeps all text as primary.
**Why it matters:** Tests regex precision. The SPEC's regex is intentionally designed to handle this case because `\d{2,3}` stops at the `%`.
**SPEC-AMBIGUITY NOTE:** The SPEC says "numeric value between 80 and 100" without clarifying whether this applies only to pixel values or also to percentage values. `width="95%"` means 95% of container width, semantically different from `width="95"` (95 pixels). The regex captures `95` from both. Current behavior (match both) is safer — missing a footnote separator is worse than a false positive split. The SPEC should clarify this during build.
**Detection:** Assert footnotes array has 1 entry with text "ثبت المسح في أحاديث كثيرة".

---

### ADV-004 format_edge_case — Self-closing HR with extra attributes

**SPEC rule:** "Self-closing variants (`/>`) are also matched."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 33)</span>
وقال الشافعي رحمه الله في هذه المسألة
<hr width=95 align='right' color='gray' />
(1) نقله عنه البيهقي في السنن الكبرى
</div>
```

**Correct behavior:** The `<hr>` has `width=95` (no quotes), extra attributes (`align`, `color`), and is self-closing. The regex matches because `width\s*=\s*['"]?(\d{2,3})['"]?` allows no-quote values. The `[^>]*` allows extra attributes. Correctly splits at the separator.
**Wrong behavior (naive impl):** Only matches `width='95'` (requires quotes) or only matches simple `<hr width='95'>` without extra attributes.
**Why it matters:** Real Shamela HTML has variable formatting. A rigid regex misses valid separators.
**Detection:** Assert footnotes array has 1 entry; assert "نقله عنه البيهقي" is in footnote text, not in `primary_text`.

---

### ADV-005 silent_corruption — Footnote marker with no matching footnote

**SPEC rule:** "Strip footnote reference markers from primary text only when a matching footnote exists on the same page."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 44)</span>
قال ابن تيمية (3) في مجموع الفتاوى: إن الأصل في العبادات التوقيف
<hr width='95'>
(1) مجموع الفتاوى ج١٢ ص٣٤٥
(2) وانظر إعلام الموقعين لابن القيم
</div>
```

**Correct behavior:** Footnote markers (1) and (2) have matching footnotes below the separator. Marker (3) in the text has NO matching footnote — it's an orphan reference. Per SPEC: "(3)" remains as literal text in `primary_text`, NOT replaced with `⌜3⌝`. Markers (1) and (2) are replaced with `⌜1⌝` and `⌜2⌝` only if they appear in the primary text. Log `NORM_ORPHAN_FOOTNOTE_REF`.
**Wrong behavior (naive impl):** (a) Replaces ALL `(N)` markers including orphan (3) with `⌜N⌝`, creating a dangling reference. (b) Strips ALL markers blindly.
**Why it matters:** Orphan references in universal format (`⌜3⌝`) with no footnote entry corrupt downstream engines' footnote linking.
**Detection:** Assert "(3)" appears literally in `primary_text`; assert `⌜3⌝` does NOT appear; assert `NORM_ORPHAN_FOOTNOTE_REF` was logged.

---

### ADV-006 arabic_trap — Diacritics corruption during HTML entity decoding

**SPEC rule:** "Post-parse validation: compare diacritic positions between raw HTML text nodes and parsed output. If any diacritic at a known position is absent or substituted, raise `NORM_DIACRITICS_ENTITY_CORRUPTION`."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 7)</span>
بِسْمِ اللَّهِ الرَّحْمَ&#x0670;نِ الرَّحِيمِ
</div>
```

**Correct behavior:** The entity `&#x0670;` is Unicode U+0670 (ARABIC LETTER SUPERSCRIPT ALEF), producing "الرَّحْمٰنِ". After HTML parsing, the diacritic positions are verified. The superscript alef is preserved.
**Wrong behavior (naive impl):** (a) The parser resolves `&#x0670;` but a downstream `.strip()` or normalization removes the superscript alef. (b) The parser resolves it to a different character. (c) No post-parse validation — corruption goes undetected.
**Why it matters:** T-1 (Silent Text Corruption). Superscript alef on "الرحمن" is a critical Quranic spelling convention. Dropping it silently corrupts sacred text.
**Detection:** Assert `U+0670` is present in the output `primary_text` at the correct position. Assert `NORM_DIACRITICS_ENTITY_CORRUPTION` is NOT raised (because the diacritic was correctly preserved).

---

### ADV-007 arabic_trap — ZWNJ preserved vs stripped in whitespace normalization

**SPEC rule:** "U+200C (ZWNJ) → PRESERVED (used for heading detection in 9.5% of Shamela corpus)"
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 55)</span>
&#x200C;&#x200C;باب الوضوء&#x200C;&#x200C;
والوضوء في اللغة مأخوذ من الوضاءة
</div>
```

**Correct behavior:** Double ZWNJ at line start is preserved (it's a heading detection signal per §4.A.6 Tier 2). The ZWNJ characters remain in the text. Structure discovery detects this as a Tier 2 heading with "high" confidence.
**Wrong behavior (naive impl):** (a) Whitespace normalization strips ZWNJ as "invisible characters." (b) ZWNJ is treated as whitespace and collapsed. (c) Heading detection doesn't check for ZWNJ pattern.
**Why it matters:** 9.5% of Shamela corpus uses ZWNJ for headings. Stripping ZWNJ destroys heading signals, causing NORM_SPARSE_STRUCTURE for thousands of sources.
**Detection:** Assert ZWNJ characters (U+200C) are present in output. Assert `structural_markers.heading_detected == true` with `heading_detection_method == "keyword_heuristic"`.

---

### ADV-008 format_edge_case — PageText div with no PageNumber span

**SPEC rule:** "Extract page numbers from `<span class='PageNumber'>(ص: N)</span>`."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageHead'>فصل في أركان الصلاة</span>
أركان الصلاة أربعة عشر: القيام مع القدرة، وتكبيرة الإحرام
</div>
```

**Correct behavior:** No `PageNumber` span → `page_number_display: null`, `page_number_int: null`. The content unit is still created with a valid `unit_index`. The content is extracted normally.
**Wrong behavior (naive impl):** (a) Crashes with NoneType error when parsing page number. (b) Skips the page entirely (silent page loss). (c) Uses a default page number like 0 that collides with the first real page.
**Why it matters:** Silent page loss (skipping) violates completeness guarantee. Crashing on missing optional data is fragile.
**Detection:** Assert content unit exists with `page_number_int == null` and `page_number_display == null`. Assert `primary_text` contains "أركان الصلاة أربعة عشر".

---

### ADV-009 format_edge_case — Empty PageText div

**SPEC rule:** "Every physical page in the source that contains extractable text produces a content unit. Pages that are blank... still produce a content unit with the corresponding `content_flags` set (`is_blank`)."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 100)</span>
</div>
<div class='PageText'>
<span class='PageNumber'>(ص: 101)</span>
تابع: باب الصلاة على الميت
</div>
```

**Correct behavior:** Page 100 produces a content unit with `is_blank: true`, empty `primary_text`, `text_fidelity.score: "very_low"`. Page 101 produces a normal content unit. `unit_index` values are contiguous across both.
**Wrong behavior (naive impl):** (a) Skips empty page — `unit_index` gap. (b) Doesn't set `is_blank` flag — downstream treats it as data loss rather than known empty page.
**Why it matters:** Unit index gap breaks passaging engine's adjacency assumption. Missing blank page marker loses information about the source's physical structure.
**Detection:** Assert two content units produced. Assert first has `is_blank: true`. Assert `unit_index` values are contiguous.

---

### ADV-010 silent_corruption — PageHead content leaking into primary_text

**SPEC rule:** "Shamela HTML: `PageHead` elements are Shamela's navigation metadata... EXCLUDED from `primary_text`. Inline headings detected by keyword heuristics within the page text ARE part of the text and remain in `primary_text`."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 30)</span>
<span class='PageHead'>باب صفة الصلاة</span>
يستحب أن يقرأ بعد الفاتحة سورة في الركعتين الأوليين
</div>
```

**Correct behavior:** "باب صفة الصلاة" is recorded in `structural_markers.heading_text` but EXCLUDED from `primary_text`. The `primary_text` starts with "يستحب أن يقرأ".
**Wrong behavior (naive impl):** (a) Includes PageHead text in `primary_text` — the heading appears twice (once in structural_markers, once in text), inflating word counts and confusing downstream engines. (b) Includes PageHead AND marks it as inline heading — double heading detection.
**Why it matters:** PageHead is navigation metadata added by Shamela, not the author's text. Including it corrupts the primary text (T-5 synthesis would attribute Shamela metadata to the author).
**Detection:** Assert "باب صفة الصلاة" is NOT in `primary_text`. Assert `structural_markers.heading_text == "باب صفة الصلاة"`.

---

## §4.A.5 — Multi-Layer Text Detection

### ADV-011 multi_signal_conflict — Bold span meets character threshold but has transition marker

**SPEC rule:** "Bold spans are classified using a two-factor test: character count >=80 AND the span does not contain a transition marker from the §4.A.5 marker list. Both conditions must be met for layer-indicator classification."
**Adversarial input (after HTML stripping, bold region marked):**
```
[BOLD START]قوله: المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية في اصطلاح النحويين وهو المجرد عن العوامل[BOLD END]
أي أن المبتدأ يكون مرفوعاً
```

**Correct behavior:** The bold span is 87 characters (>=80) BUT contains "قوله:" (a transition marker). The two-factor test requires BOTH conditions: >=80 chars AND no transition marker. Since condition 2 fails, the span is classified as `uncertain`, not as a layer indicator.
**Wrong behavior (naive impl):** (a) Only checks character count (>=80), ignores transition marker → incorrectly classifies as matn layer indicator. (b) Treats "قوله:" as the transition but classifies the bold region as matn anyway.
**Why it matters:** T-2 (Attribution Error). If "قوله:" is a transition marker introducing matn text, the bold region is the commentator quoting the matn author. Incorrectly classifying the entire bold span as matn misattributes commentary as original text.
**Detection:** Assert the bold region's `text_layers` entry has `confidence` <= 0.50 or `layer_type: "uncertain"`.

---

### ADV-012 boundary_value — Bold text at exactly 5% of page

**SPEC rule:** "If the source metadata indicates `is_multi_layer: true` and bold text constitutes <5% or >60% of primary text on a page, the bold signal is treated as emphasis rather than layer indicator."
**Adversarial input:** A page with 1000 characters total, where exactly 50 characters are bold (5.0%).
```
[BOLD]المبتدأ هو الاسم المرفوع العاري عن العوامل اللفظية[/BOLD]
أي المبتدأ في اصطلاح النحويين هو الاسم المجرد عن العوامل اللفظية مرفوعاً والخبر هو المرفوع المسند إليه وقوله المرفوع يخرج المنصوب والمجرور ويخرج الفاعل ونائبه فإنهما وإن كانا مرفوعين إلا أنهما ليسا مجردين عن العوامل اللفظية فالفاعل مرفوع بفعله ونائب الفاعل مرفوع بالفعل المبني للمفعول والمبتدأ مرفوع بالابتداء على الصحيح والخبر مرفوع بالمبتدأ أو بهما معاً والمبتدأ قسمان مبتدأ له خبر ومبتدأ له فاعل أغنى عن الخبر
```

**Correct behavior:** Bold is exactly 5% of text. The SPEC says `<5%` for the "too little" threshold. At exactly 5%, bold is NOT below the threshold — so bold IS treated as a layer indicator.
**Wrong behavior (naive impl):** Uses `<= 5%` or rounds down — treats bold as emphasis at exactly 5%.
**Why it matters:** Off-by-one at the boundary. Treating valid layer signals as emphasis causes multi-layer sources to be processed as single-layer (T-2).
**Detection:** Assert that at 5.0%, bold is treated as a layer indicator. At 4.9%, bold is treated as emphasis.

---

### ADV-013 silent_corruption — Entire page bold (emphasis, not layer)

**SPEC rule:** "bold text constitutes... >60% of primary text on a page, the bold signal is treated as emphasis rather than layer indicator"
**Adversarial input:** `is_multi_layer: true` source. A page where 100% of text is bold.
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 78)</span>
<b>وإذا أراد المصلي أن يسجد فليكبر وليضع ركبتيه قبل يديه ثم ليضع يديه ثم جبهته وأنفه وإذا رفع فليرفع رأسه ثم يديه ثم ركبتيه</b>
</div>
```

**Correct behavior:** 100% bold (>60% threshold). Bold signal is treated as emphasis, NOT as layer indicator. The page is attributed to the default layer (Layer 2 in sharh) rather than being classified as all-matn.
**Wrong behavior (naive impl):** (a) Classifies entire page as matn because it's all bold — misattributes a full page of commentary. (b) Doesn't check the bold percentage threshold.
**Why it matters:** Some Shamela exports bold entire pages for emphasis (e.g., important fiqh rulings). A naive implementation would misattribute these pages to the matn author.
**Detection:** Assert the page's `text_layers` assigns the default commentary layer (sharh), not matn.

---

### ADV-014 silent_corruption — Layer coverage gap

**SPEC rule:** "every character in `primary_text` is covered by exactly one segment in `text_layers`. No character is unattributed."
**Adversarial input:** Multi-layer page with 200 characters.
```
Layer segments: [
  {"start": 0, "end": 90, "layer_type": "matn"},
  {"start": 95, "end": 200, "layer_type": "sharh"}
]
```

**Correct behavior:** Characters 91-94 are not covered by any segment — this is a coverage gap. The normalizer MUST NOT produce this output. §5 check 4 catches it. If the normalizer can't determine the layer for characters 91-94, it assigns `layer_type: "uncertain"` with `confidence <= 0.30`.
**Wrong behavior (naive impl):** Produces segments with gaps between them. §5 check 4 doesn't run or doesn't catch gaps.
**Why it matters:** Phase 2 engines use layer segments to attribute text. Unattributed characters are invisible — they exist in `primary_text` but have no layer, so they're silently dropped from layer-specific processing.
**Detection:** Assert: for every `i` in `range(len(primary_text))`, exactly one segment satisfies `start <= i < end`.

---

### ADV-015 multi_signal_conflict — Source metadata says single-layer, normalizer detects multi-layer signals

**SPEC rule:** "For sources where `is_multi_layer` is true in the source metadata (or where the normalizer detects layer signals even when the source engine didn't flag it), identify which portions of each page's text belong to which layer."
**Adversarial input:** Source metadata has `is_multi_layer: false`. But the HTML has:
```html
<b>المبتدأ هو الاسم المرفوع</b>
أي المبتدأ في اصطلاح النحويين هو الاسم المرفوع
قوله: والخبر المرفوع المسند إليه
```

**Correct behavior:** Despite `is_multi_layer: false`, the normalizer detects bold + transition markers. It performs layer detection and writes back a multi-layer discovery to source metadata as an enrichment. The output has multi-layer `text_layers` segments.
**Wrong behavior (naive impl):** Trusts `is_multi_layer: false` blindly and skips layer detection entirely → produces single-layer output with one segment covering all text, attributed to one author.
**Why it matters:** The source engine may have missed multi-layer signals (it uses LLM inference, not format-specific detection). If the normalizer doesn't detect layers when signals are present, downstream engines attribute commentary to the wrong author (T-2).
**Detection:** Assert `text_layers` has >1 segment. Assert an enrichment write-back was triggered.

---

### ADV-046 silent_corruption — Layer fingerprint inversion (NORM_LAYER_FINGERPRINT_INVERSION)

**SPEC rule (§4.B.9):** "If the 'matn' fingerprint has sentence_length.mean > 22 AND connective_frequency > 0.08 AND the 'sharh' layer has sentence_length.mean < 16 AND connective_frequency < 0.06, the inversion signal is strong — trigger human gate review."
**Adversarial input:** Multi-layer source where the layer detection assigned labels backwards. The "matn" layer fingerprint: sentence_length.mean = 28, connective_frequency = 0.11. The "sharh" layer fingerprint: sentence_length.mean = 12, connective_frequency = 0.04.
**Correct behavior:** §4.B.9 detects the inversion signal (matn has sharh-like properties, sharh has matn-like properties). NORM_LAYER_FINGERPRINT_INVERSION (warning) logged. Human gate triggered. Labels NOT auto-corrected.
**Wrong behavior (naive impl):** (a) Fingerprint validation not implemented. (b) Only checks one direction (matn has high values) but not both conditions simultaneously. (c) Auto-corrects labels without human gate.
**Why it matters:** T-2 (Attribution Error). Full layer inversion means EVERY matn excerpt is attributed to the commentator and vice versa. The single highest-impact T-2 failure — corrupts the entire source.
**Detection:** Assert NORM_LAYER_FINGERPRINT_INVERSION is raised. Assert human gate triggered. Assert labels NOT swapped.

---

## §4.A.6 — Structure Discovery

### ADV-016 arabic_trap — "باب" appearing as part of a name, not a heading

**SPEC rule:** "Scan cleaned text for structural keywords (باب, فصل, مبحث...) at line beginnings"
**Adversarial input (cleaned text):**
```
وقد نقل هذا القول عن أبي عبد الله باب الباب الشيرازي
وهو من أعلام الحنفية في القرن الخامس
```

**Correct behavior:** "باب" appears in the middle of a line as part of a scholar's name ("باب الباب الشيرازي"), NOT at a line beginning. It is NOT detected as a structural heading.
**Wrong behavior (naive impl):** Uses `"باب" in line` instead of checking line beginning → false positive heading detection. Alternatively, regex doesn't anchor to `^`.
**Why it matters:** False positive headings fragment the division tree incorrectly. A page about a scholar gets split into a bogus "باب" division.
**Detection:** Assert `structural_markers.heading_detected == false` for this page.

---

### ADV-017 format_edge_case — Division tree child extends beyond parent

**SPEC rule:** "Child divisions are contained within their parent's page range."
**Adversarial input (constructed division tree):**
```json
{
  "div_id": "kitab_salat",
  "start_unit_index": 10,
  "end_unit_index": 50,
  "child_div_ids": ["bab_wudu"],
  "children": [
    {"div_id": "bab_wudu", "start_unit_index": 10, "end_unit_index": 55}
  ]
}
```

**Correct behavior:** §5 check 5 catches this: child `bab_wudu` (10-55) extends beyond parent `kitab_salat` (10-50). Validation fails.
**Wrong behavior (naive impl):** §5 check 5 only verifies `start_unit_index >= parent.start` but not `end_unit_index <= parent.end`.
**Why it matters:** Division tree inconsistency confuses passaging engine's segment allocation.
**Detection:** Assert validation raises an error for this tree.

---

### ADV-018 multi_signal_conflict — Tier 1 heading also matches Tier 2 keyword

**SPEC rule:** Tier 1 headings are `<span class="title">` elements. Tier 2 headings are keyword heuristics.
**Adversarial input:**
```html
<span class="title">باب الطهارة</span>
```

**Correct behavior:** "باب الطهارة" is detected as Tier 1 (html_tagged, confirmed). It is NOT also counted as a Tier 2 keyword match. One heading, one division node.
**Wrong behavior (naive impl):** Tier 1 and Tier 2 each detect the heading independently → duplicate division nodes, or the same heading with conflicting confidence levels.
**Why it matters:** Duplicate headings corrupt the division tree structure and inflate division counts.
**Detection:** Assert exactly one division node for "باب الطهارة" with `detection_method: "html_tagged"` and `confidence: "confirmed"`.

---

## §4.A.7 — Page Boundary Preservation

### ADV-019 boundary_value — Unit index monotonicity with skipped pages

**SPEC rule:** "`unit_index` values across all content units must form a contiguous zero-based sequence: 0, 1, 2, ..., N-1"
**Adversarial input:** A Shamela source with 5 PageText divs. The 3rd div fails HTML parsing (malformed).
**Correct behavior:** Either: (a) the malformed div still produces a content unit (with degraded content), OR (b) parsing fails entirely with `NORM_SCHEMA_VIOLATION`. The normalizer MUST NOT produce unit_index 0, 1, 3, 4 (skipping 2).
**Wrong behavior (naive impl):** Skips malformed pages with a `try/except: continue` and produces non-contiguous unit_index.
**Why it matters:** `NORM_UNIT_INDEX_VIOLATION` is fatal because passaging uses adjacency. A gap means the passaging engine treats pages 1 and 3 as adjacent when they're not.
**Detection:** Assert all unit_index values form 0..N-1. Assert no gaps.

---

### ADV-020 silent_corruption — Duplicate page numbers across volumes

**SPEC rule:** "`unit_index` is the ONLY positional identifier Phase 2 engines may use. `page_number_int` is display metadata only."
**Adversarial input:** Vol 1 page 12 and Vol 3 page 12:
```
unit_index: 11, volume: 1, page_number_int: 12
unit_index: 476, volume: 3, page_number_int: 12
```

**Correct behavior:** Both content units exist with the same `page_number_int: 12` but different `unit_index` and `volume` values. No collision.
**Wrong behavior (naive impl):** Uses `page_number_int` as a key or identifier → collision. Or deduplicates pages with same `page_number_int` across volumes.
**Why it matters:** 29.8% of Shamela corpus has duplicate page numbers. Using `page_number_int` as a key silently drops content.
**Detection:** Assert both content units exist. Assert `unit_index` values are unique. Assert `page_number_int` values can duplicate across volumes.

---

### ADV-049 boundary_value — Page number integer overflow from corrupt Shamela HTML

**SPEC rule (§4.A.7):** "Extract page numbers from `<span class='PageNumber'>(ص: N)</span>`."
**Adversarial input:**
```html
<div class='PageText'>
<span class='PageNumber'>(ص: 999999999999999999999)</span>
حدثنا أبو بكر
</div>
```
**Correct behavior:** Page number stored as string in page_number_display. page_number_int may be null (unparseable for downstream) or the large integer if supported. Content unit created with valid unit_index. No crash.
**Wrong behavior (naive impl):** JSON schema uses 32-bit integer causing overflow. Or page number used in arithmetic that overflows.
**Why it matters:** Corrupt Shamela HTML exists. The normalizer must never crash on unexpected page number values.
**Detection:** Assert content unit created. Assert no crash. Assert unit_index valid.

---

## §4.A.8 — Diacritics and Arabic Text Handling

### ADV-021 arabic_trap — NFC normalization silently changing Arabic text

**SPEC rule:** "NFC, NFD, NFKC, NFKD normalization is NOT applied to Arabic text."
**Adversarial input:**
```python
text = "لَا إِلٰهَ إِلَّا اللّٰهُ"  # Contains U+0670 (superscript alef)
# After NFKC: U+0670 might be decomposed or substituted
```

**Correct behavior:** The text passes through with zero Unicode normalization. Every byte is identical between source and output.
**Wrong behavior (naive impl):** A JSON serializer, file writer, or string library applies NFC normalization by default (many Python JSON libraries do this). The superscript alef changes form or is lost.
**Why it matters:** T-1 (Silent Text Corruption). Unicode normalization changes that are invisible in display can alter scholarly text semantically.
**Detection:** Assert byte-level comparison: `source_bytes == output_bytes` for all Arabic text.

---

### ADV-045 silent_corruption — Diacritics drift from Python JSON serializer (NORM_DIACRITICS_DRIFT)

**SPEC rule (§5 check 8):** "Extract all Unicode characters in the Arabic diacritics range (U+064B–U+0652, U+0670, U+0640) from both source and output for each page. If the diacritic character counts differ by even one character, the page fails with NORM_DIACRITICS_DRIFT (fatal)."
**Adversarial input:** Source text:
```
بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ
```
Contains 14 diacritics. A Python JSON library applies NFC normalization during json.dumps(), or a file write utility applies it transparently.
**Correct behavior:** §5 check 8 detects the diacritic count mismatch between source (14) and output (e.g., 13 after NFC drops the superscript alef). NORM_DIACRITICS_DRIFT (fatal) is raised. Normalization aborts.
**Wrong behavior (naive impl):** (a) §5 check 8 is not implemented — diacritics drift goes undetected. (b) Check compares total character count instead of diacritic-specific count — NFC changes can be count-neutral. (c) Check runs but uses NFKC-normalized text for comparison (defeats purpose).
**Why it matters:** T-1 (Silent Text Corruption). This is the primary defense against silent diacritics loss. If check 8 doesn't work, every downstream engine receives corrupted text.
**Detection:** Assert NORM_DIACRITICS_DRIFT is raised when even 1 diacritic differs. Assert normalization aborts (no output written).

---

### ADV-022 arabic_trap — Custom whitespace cleanup removing trailing diacritics

**SPEC rule:** "Preserve all diacritics exactly." (§4.A.8) + "Leading/trailing line whitespace trimmed" (§4.A.8)
**Adversarial input:**
```python
# A text-cleaning function that tries to strip "non-letter" characters at string edges:
import re
text = "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ"
# The last codepoint is kasra (U+0650), a combining character
# A naive cleanup might use:
cleaned = re.sub(r'[^\w\s]+$', '', text)  # Strips "non-word" chars at end
# But \w in Python regex does NOT reliably match Arabic combining marks
# depending on regex flags and locale, this could strip the trailing kasra
```

**Correct behavior:** The trailing kasra on مِ is preserved. The text is byte-identical after whitespace trimming. Only ASCII whitespace (spaces, tabs, newlines) is removed.
**Wrong behavior (naive impl):** A regex-based cleanup function, a custom strip function, or a call to `.rstrip()` with a character class that includes Arabic combining marks, removes the trailing kasra. The text LOOKS identical in many display fonts (kasra is small and often invisible) but the bytes differ.
**Why it matters:** T-1 (Silent Text Corruption). Diacritics at string boundaries are especially vulnerable because they're the characters most likely to be caught by edge-trimming functions. In Quranic text, every diacritic is critical.
**Detection:** Assert byte-level equality: `source_bytes == output_bytes` for all Arabic text after whitespace trimming. Specifically assert U+0650 (kasra) is present as the final combining character.

---

### ADV-023 arabic_trap — Mixed Arabic-Indic and ASCII digits in footnote markers

**SPEC rule:** "Parse footnotes into individual entries using the `(N)` marker pattern."
**Adversarial input:**
```
Primary text: قال المصنف (١) في هذه المسألة (2)
---
(١) انظر الأصل
(2) وقد خالف في ذلك
```

**Correct behavior:** Both Arabic-Indic `(١)` and ASCII `(2)` markers are recognized. Both footnotes are extracted and matched to their references.
**Wrong behavior (naive impl):** Only matches ASCII `(N)` patterns → misses Arabic-Indic markers. Or matches Arabic-Indic markers in the footnote section but not in the primary text (or vice versa).
**Why it matters:** Shamela exports sometimes mix digit forms within the same source. Missing Arabic-Indic markers means an unknown but potentially significant fraction of footnote references could be orphaned — the actual frequency needs corpus measurement.
**Detection:** Assert both footnotes are extracted. Assert both reference markers in primary_text are replaced with `⌜N⌝` format.

---

## §4.A.9 — Content Flagging

### ADV-024 arabic_trap — Quran citation without standard prefix

**SPEC rule:** "Quran citation markers detected ({verse text}, 'قال تعالى', surah/ayah references)."
**Adversarial input:**
```
قال الله سبحانه: {وَأَقِيمُوا الصَّلَاةَ}
```

**Correct behavior:** "قال الله سبحانه:" is a Quran citation marker (variation of "قال تعالى"). The curly-brace verse text confirms it. `has_quran_citation: true`.
**Wrong behavior (naive impl):** Only matches exact "قال تعالى" string → misses variations like "قال الله سبحانه:", "قال عز وجل:", "قال جل وعلا:", "قال الحق سبحانه:".
**Why it matters:** Quran citation detection affects downstream excerpting (citations need special attribution). Missing citations means Quranic text is attributed to the scholar, not to the Quran.
**Detection:** Assert `has_quran_citation: true` for all common Quran introduction patterns.

---

### ADV-050 arabic_trap — Hadith citation with non-standard introduction

**SPEC rule (§4.A.9):** "Hadith citation markers detected."
**Adversarial input:**
```
أخبرنا أبو بكر محمد بن الحسين عن عبد الله بن مسعود رضي الله عنه قال: قال رسول الله ﷺ: «إنما الأعمال بالنيات»
```
**Correct behavior:** The isnad chain (أخبرنا...عن...قال: قال رسول الله) detected as hadith citation. has_hadith_citation: true.
**Wrong behavior (naive impl):** Only detects "حدثنا" as hadith marker, misses "أخبرنا" (both are hadith transmission verbs with identical function).
**Why it matters:** Hadith citations need special downstream treatment. Missing them means hadith text is treated as the author's own words.
**Detection:** Assert has_hadith_citation: true. Assert detection covers أخبرنا, حدثنا, أنبأنا transmission forms.

---

### ADV-051 format_edge_case — Table of contents page detection

**SPEC rule (§4.A.9):** Content flags include is_toc_page.
**Adversarial input:**
```
فهرس الكتاب
باب الطهارة ............... ١٢
باب الصلاة ............... ٤٥
باب الزكاة ............... ٨٩
باب الصيام ............... ١٢٣
```
**Correct behavior:** Page flagged as is_toc_page: true. Leader dots + page numbers + "فهرس" keyword identify it as TOC.
**Wrong behavior (naive impl):** (a) Only checks "فهرس" keyword without leader-dots pattern — false positive on pages mentioning "فهرس". (b) Detects as TOC but also detects structural headings (باب) from TOC entries, creating phantom divisions.
**Why it matters:** TOC pages should not generate structural divisions — they're metadata about the structure, not structure itself. Phantom divisions from TOC entries double every entry in the division tree.
**Detection:** Assert is_toc_page: true. Assert no structural heading detections from TOC entry text.

---

## §5 — Validation and Quality

### ADV-025 boundary_value — Arabic character ratio at exactly 70%

**SPEC rule:** "Character distribution must be plausible for Arabic text: ≥70% Arabic characters (excluding whitespace and punctuation)."
**Adversarial input:** Page text with exactly 70.0% Arabic characters:
```
المبتدأ هو الاسم المرفوع - The nominative noun - والخبر هو المرفوع المسند
```
(Calculated: 70 Arabic chars out of 100 total non-whitespace-non-punctuation chars = 70.0%)

**Correct behavior:** The SPEC originally said `>70%` for the pass condition and `<70%` for the flag condition, leaving exactly 70% undefined — a SPEC gap. After the fix (see K1), the threshold is `≥70%` pass / `<70%` flag. At exactly 70.0%, the page passes.
**Wrong behavior (naive impl):** (a) Uses `> 70%` strictly, leaving exactly 70% in an undefined state. (b) Uses `>= 70%` without updating the flag condition, creating overlap at 70%. (c) Doesn't strip whitespace/punctuation from the denominator.
**Detection:** Assert page at 70.0% passes (≥70%). Assert page at 69.9% is flagged (<70%). Assert page at 70.1% passes.

---

### ADV-026 silent_corruption — mid_sentence boundary with terminal punctuation

**SPEC rule (§5 check 10c):** "if `type` is `mid_sentence`, the `primary_text` does not end with terminal punctuation (period, question mark, exclamation mark — a contradiction would indicate a detection bug)"
**Adversarial input:** A content unit where boundary_continuity algorithm outputs `mid_sentence` but the page's `primary_text` ends with:
```
وقد اختلف العلماء في هذه المسألة.
```

**Correct behavior:** §5 check 10c detects the contradiction: `mid_sentence` + period at end. Produces `NORM_CONTINUITY_INCONSISTENT` (warning). Sets `boundary_continuity.confidence` to 0.0.
**Wrong behavior (naive impl):** (a) Doesn't check for this contradiction. (b) Checks but uses wrong punctuation set (misses Arabic question mark `؟`). (c) Raises fatal error instead of warning.
**Why it matters:** Downstream passaging engine trusts `mid_sentence` to join pages. If the text actually ends at a sentence boundary, joining produces wrong passages.
**Detection:** Assert `NORM_CONTINUITY_INCONSISTENT` is produced. Assert `boundary_continuity.confidence == 0.0`.

---

### ADV-027 silent_corruption — argument_cycle_complete with non-empty missing_elements

**SPEC rule (§5 check 11b):** "if `argument_cycle_complete` is `true`, then `cycle_missing_elements` is empty (a complete cycle cannot have missing elements)"
**Adversarial input:** Discourse flow output:
```json
{
  "argument_cycle_complete": true,
  "cycle_missing_elements": ["evidence", "conclusion"]
}
```

**Correct behavior:** §5 check 11 catches the contradiction. `NORM_DISCOURSE_INCONSISTENT` warning. Set `discourse_flow` to null for this content unit.
**Wrong behavior (naive impl):** (a) Doesn't validate this combination. (b) Nullifies only one of the two fields instead of the entire `discourse_flow` object.
**Why it matters:** Contradictory discourse signals confuse downstream synthesis. A "complete" cycle with "missing elements" is logically impossible — it indicates a bug.
**Detection:** Assert `NORM_DISCOURSE_INCONSISTENT` is logged. Assert `discourse_flow` is null for the affected content unit.

---

### ADV-028 boundary_value — Coverage check tolerance at exactly 10%

**SPEC rule (§5 check 2):** "The number of content units must match the expected page count from the source metadata (±10% tolerance for skipped metadata/blank pages)."
**Adversarial input:** Source metadata `page_count: 100`. Normalizer produces 89 content units (11% fewer).

**Correct behavior:** 89/100 = 89% → 11% mismatch, exceeding 10% tolerance. Triggers `NORM_PAGE_COUNT_MISMATCH`.
**Wrong behavior (naive impl):** Uses `>= 10%` instead of `> 10%` → 11% passes. Or calculates tolerance wrong (e.g., 10 pages absolute instead of 10%).
**Why it matters:** Missing 11 pages from a 100-page source is likely a parsing bug, not metadata inaccuracy.
**Detection:** Assert `NORM_PAGE_COUNT_MISMATCH` for 89/100. Assert NO warning for 91/100 (9% mismatch, within tolerance).

---

### ADV-029 boundary_value — Identical character run at exactly 20

**SPEC rule (§5 check 3):** "No runs of >20 identical characters (suggests OCR garbage)."
**Adversarial input:**
```
كتاب الصلاة aaaaaaaaaaaaaaaaaaaa وباب الوضوء
```
(Exactly 20 `a` characters)

**Correct behavior:** The SPEC says `>20` (strictly greater than). A run of exactly 20 identical characters does NOT trigger the garbage check.
**Wrong behavior (naive impl):** Uses `>= 20` → falsely flags legitimate text containing repeated characters.
**Why it matters:** Some Arabic texts legitimately contain repeated punctuation or decoration. The threshold must be exact.
**Detection:** Assert 20 identical characters → no flag. Assert 21 identical characters → flagged.

---

## §7 — Error Handling

### ADV-030 format_edge_case — OCR empty-success (HTTP 200 with no text)

**SPEC rule (NORM_OCR_FAILED):** "OCR returns HTTP 200 but output text is empty or <10 characters for a page whose image contains visible content (empty-success case)"
**Adversarial input:** OCR API returns 200 OK with body: `{"text": "", "confidence": 0.95}`

The page image contains visible Arabic text (pixel variance > threshold).

**Correct behavior:** Despite HTTP 200 and high confidence, the empty text triggers the empty-success detection: (a) OCR returned successfully, (b) extracted text <10 chars, (c) page image is not blank. Raises `NORM_OCR_FAILED`. Retries with fallback engine.
**Wrong behavior (naive impl):** (a) Checks only HTTP status code — 200 means success. (b) Produces a content unit with empty `primary_text` and `text_fidelity: "high"` (because confidence was 0.95). Silent data loss.
**Why it matters:** OCR APIs sometimes return empty results for complex layouts. Treating empty OCR as "blank page" loses content.
**Detection:** Assert `NORM_OCR_FAILED` is raised. Assert fallback engine is invoked. Assert no content unit with empty text and high fidelity.

---

### ADV-031 format_edge_case — Footnote separator absence threshold for tahqiq editions

**SPEC rule (NORM_FOOTNOTE_SEPARATOR_ABSENT):** "For tahqiq editions (source metadata indicates tahqiq editor): if >10% of pages have this, trigger human gate"
**Adversarial input:** Source metadata has `muhaqiq_name_raw: "الشيخ الألباني"` (tahqiq editor present). 15 out of 100 pages lack footnote separators (15%).

**Correct behavior:** 15% > 10% threshold for tahqiq editions → human gate triggered. The separator pattern may be non-standard and needs manual identification.
**Wrong behavior (naive impl):** (a) Uses the general 30% threshold instead of the tahqiq-specific 10% threshold. At 15%, the general threshold (30%) is not met, so no human gate. (b) Doesn't check for tahqiq editor in source metadata.
**Why it matters:** Tahqiq editions MUST have footnotes. If the separator isn't being detected, the tahqiq apparatus is silently lost — the most important scholarly content in the source.
**Detection:** Assert human gate triggered at 15% for a tahqiq source. Assert NO human gate at 15% for a non-tahqiq source (which uses the 30% threshold).

---

### ADV-032 silent_corruption — Enrichment write-back failure should not block normalization

**SPEC rule (NORM_ENRICHMENT_WRITEBACK_FAILED):** "Normalization completes — the normalized package is valid without the write-back."
**Adversarial input:** Normalization succeeds for all passes. During Pass 6, the normalizer detects a structural format override (SPEC says to write back this discovery). The write-back fails (file locked by another process).

**Correct behavior:** `NORM_ENRICHMENT_WRITEBACK_FAILED` is logged as Warning. Normalization COMPLETES. The normalized package is written to disk. Source registry updated to `normalized`.
**Wrong behavior (naive impl):** Write-back failure cascades → normalization aborted → source stays at `acquired` status despite valid output being ready.
**Why it matters:** Write-backs are supplementary information. Blocking normalization on a write-back failure means a locked file prevents the entire pipeline from progressing.
**Detection:** Assert normalization status is `normalized` despite write-back failure. Assert warning is logged.

---

### ADV-047 format_edge_case — Atomic write failure and recovery (NORM_WRITE_FAILED / NORM_WRITE_RECOVERY)

**SPEC rule (§4.A.2 Atomic write / Interrupted write recovery):** "If multiple normalized_prev_* directories exist, select the one with the LATEST timestamp."
**Adversarial input:** Simulated state on disk:
- `normalized_tmp_20260317T120000/` exists (contains manifest.json only, no content.jsonl)
- `normalized_prev_20260317T115500/` exists (contains both files, valid)
- `normalized_prev_20260317T110000/` exists (contains both files, valid, older)
- No `normalized/` directory exists.
**Correct behavior:** Recovery validates temp → fails (content.jsonl missing). Selects LATEST prev (T115500, not T110000). Restores from T115500 → `normalized/`. Cleans up temp and all prev directories. Logs NORM_WRITE_RECOVERY (info).
**Wrong behavior (naive impl):** (a) Selects first prev alphabetically or by creation time instead of latest timestamp. (b) Promotes incomplete temp to normalized/. (c) Restores but doesn't clean up — orphaned state remains. (d) Crashes on multiple prev directories.
**Why it matters:** Incorrect recovery promotes a partial package or restores from an older backup.
**Detection:** Assert restored from T115500. Assert temp and both prev cleaned up. Assert NORM_WRITE_RECOVERY logged.

---

### ADV-048 format_edge_case — Windows-1256 encoded Shamela export (NORM_ENCODING_ERROR)

**SPEC rule (§7):** "NORM_ENCODING_ERROR (Warning) — Source uses unrecognized or corrupted encoding. Convert what is possible. Flag affected pages as text_fidelity: 'low'."
**Adversarial input:** A Shamela .htm file saved in Windows-1256 encoding instead of UTF-8. Opening as UTF-8 produces mojibake.
**Correct behavior:** Normalizer detects encoding mismatch. Attempts Windows-1256 → UTF-8 conversion. If successful: NORM_ENCODING_ERROR (warning), affected pages get text_fidelity: "low". If conversion fails: NORM_ENCODING_ERROR with details, human gate triggered.
**Wrong behavior (naive impl):** (a) Opens with encoding='utf-8' and crashes. (b) Opens with errors='ignore' — silently drops non-ASCII. (c) Opens with errors='replace' — replaces Arabic with U+FFFD.
**Why it matters:** T-1 (Silent Text Corruption). Windows-1256 is a real encoding used by older Shamela versions.
**Detection:** Assert NORM_ENCODING_ERROR logged. Assert Arabic text correctly converted. Assert text_fidelity downgraded.

---

## §3 — Output Contract (Cross-Cutting)

### ADV-033 silent_corruption — Manifest total_content_units disagrees with JSONL line count

**SPEC rule:** "`total_content_units`: the number of content unit records in the accompanying JSONL."
**Adversarial input (constructed):** Manifest says `total_content_units: 100`. JSONL file has 99 lines.

**Correct behavior:** §5 check (internal consistency) catches this. Normalization aborts.
**Wrong behavior (naive impl):** `total_content_units` is set early in processing and not updated when a page is skipped or fails. The manifest and JSONL disagree.
**Why it matters:** Downstream engines may pre-allocate based on `total_content_units` or use it for progress tracking. A mismatch indicates data loss.
**Detection:** Assert `total_content_units` always equals the actual JSONL line count.

---

### ADV-034 silent_corruption — Footnote universal marker format inconsistency

**SPEC rule:** "Footnote reference markers in the primary text are replaced with inline markers in a universal format (`⌜1⌝` — using Unicode half-brackets)"
**Adversarial input:** Source has footnote markers in format `(1)`, `[1]`, `{1}`, and `¹` (superscript).

**Correct behavior:** ALL matched markers (those with corresponding footnotes) are replaced with the universal `⌜N⌝` format, regardless of their original format. The original format is NOT preserved for matched markers.
**Wrong behavior (naive impl):** (a) Only replaces `(N)` format — misses `[N]`, `{N}`, superscript. (b) Preserves original format alongside universal format — duplicate markers. (c) Uses wrong Unicode characters (regular brackets instead of half-brackets).
**Why it matters:** Downstream engines expect exactly one marker format (`⌜N⌝`). Mixed formats break footnote linking in the passaging and excerpting engines.
**Detection:** Assert no `(N)`, `[N]`, `{N}` markers remain in `primary_text` when they have matching footnotes. Assert all replaced markers use `⌜` (U+231C) and `⌝` (U+231D).

---

## §4.B.2 — Structural Format Auto-Detection (T-3 defense)

### ADV-043 boundary_value — Q&A format detection at exactly 30% threshold

**SPEC rule (§4.B.2):** "Q&A pattern markers (سُئل + فأجاب or مسألة + الجواب) found on 30% or more of sampled pages triggers qa_format classification."
**Adversarial input:** A 20-page sample where exactly 6 pages (30.0%) contain Q&A markers.
**Correct behavior:** 30.0% meets the "30% or more" threshold → classified as qa_format. `structural_format_proposed: "qa_format"`.
**Wrong behavior (naive impl):** Uses `> 30%` (strictly greater than) → 30.0% doesn't trigger → source stays classified as prose, losing the Q&A structure signal.
**Why it matters:** T-3 (Taxonomic Misplacement). Q&A format affects how the taxonomy engine places the source. Missing the classification means fiqh fatwa collections are treated as prose, losing their question-answer structure for downstream processing.
**Detection:** Assert qa_format classification at 30.0%. Assert NO classification at 29.9%.

---

### ADV-044 multi_signal_conflict — Commentary markers and Q&A markers co-occurring

**SPEC rule (§4.B.2):** Structural format auto-detection with precedence rules.
**Adversarial input:** A source where: 35% of pages have Q&A markers (سُئل/فأجاب) AND 25% of pages have commentary markers (bold matn + unbold sharh pattern). The source engine classified it as `commentary`.
**Correct behavior:** Q&A markers exceed the threshold but the source engine's consensus classification is authoritative. The normalizer proposes qa_format but does NOT override. Human gate created. `structural_format_proposed: "qa_format"`, `structural_format: "commentary"` (unchanged per M-31 fix).
**Wrong behavior (naive impl):** (a) Auto-overrides to qa_format without human gate. (b) Ignores Q&A markers because commentary was already classified. (c) Creates two simultaneous proposals.
**Why it matters:** Mixed-format sources exist — a commentary can use Q&A format. Overriding multi-model consensus with a single-engine heuristic is exactly the M-31 bug that Probe 1 caught.
**Detection:** Assert `structural_format` unchanged. Assert `structural_format_proposed` is set. Assert human gate created.

---

## §4.B — Transformative Capabilities

> **NOTE:** §4.B test cases (ADV-035 through ADV-042) target transformative capabilities that are deferred from core build. Implement these tests when the corresponding §4.B capabilities are built. They are included here for completeness and to guide future build sessions.

### ADV-035 multi_signal_conflict — Cross-validation: mid_argument continuity vs complete discourse cycle

**SPEC rule (§4.A.2 Pass 6, step 9):** "if a content unit has `boundary_continuity.type: 'mid_argument'` but the same unit's `discourse_flow.argument_cycle_complete: true`, the continuity signal takes precedence — the discourse flow's `argument_cycle_complete` is set to `false`"
**Adversarial input:** A content unit where:
- Boundary continuity algorithm says: `type: "mid_argument"` (the argument continues on the next page)
- Discourse flow algorithm says: `argument_cycle_complete: true` (the argument cycle is complete on this page)

**Correct behavior:** Continuity takes precedence. `discourse_flow.argument_cycle_complete` is overridden to `false`. `cycle_missing_elements` is populated with the expected continuation.
**Wrong behavior (naive impl):** (a) No cross-validation — both contradictory signals reach downstream. (b) Discourse flow takes precedence — incorrect per SPEC. (c) Cross-validation runs but produces `null` for discourse_flow instead of fixing the specific field.
**Why it matters:** The passaging engine reads BOTH signals. Contradictory signals produce wrong passage boundaries.
**Detection:** Assert `argument_cycle_complete == false` when `boundary_continuity.type == "mid_argument"`. Assert `cycle_missing_elements` is non-empty.

---

### ADV-036 boundary_value — Content census HyperLogLog on full text vs sampling

**SPEC rule (§4.B.5):** "Content census estimated_unique_terms changed from 20-page sampling to full HyperLogLog processing of all content units"
**Adversarial input:** A 500-page source where the first 20 pages have very repetitive vocabulary (introduction, table of contents), but pages 21-500 have highly diverse scholarly vocabulary.

**Correct behavior:** HyperLogLog processes ALL 500 pages → `estimated_unique_terms` reflects the full vocabulary diversity.
**Wrong behavior (naive impl):** Samples only the first 20 pages (the old approach) → drastically underestimates vocabulary diversity, signaling a simpler source than it actually is.
**Why it matters:** `estimated_unique_terms` is a downstream adaptation signal. Underestimating it causes the passaging engine to create passages that are too short for the actual content complexity.
**Detection:** Assert `estimated_unique_terms` increases significantly when including pages beyond the first 20.

---

### ADV-037 arabic_trap — Morphological validation accepting classical Arabic terms

**SPEC rule (§4.A.4 Arabic-specific post-processing):** "Terms not found in the lexicon receive `analysis_status: 'unknown'` — they are NOT flagged as OCR errors. Only terms that are morphologically impossible (no valid Arabic root pattern) are flagged."
**Adversarial input:** OCR output includes classical Arabic terms not in the MSA database:
```
وَالْمُؤَلَّلَةُ قُلُوبُهُمْ هُمْ قَوْمٌ مِنَ الطُّلَقَاءِ
```
"الطلقاء" (those freed at the conquest of Mecca) — a rare classical term unlikely to be in CAMeL Tools' MSA database.

**Correct behavior:** "الطلقاء" is not in the MSA lexicon → `analysis_status: "unknown"`. It is NOT flagged as an OCR error. The normalizer does not attempt correction.
**Wrong behavior (naive impl):** Treats all unknown-to-lexicon words as OCR errors → falsely flags valid classical Arabic vocabulary, producing noise in the fidelity map.
**Why it matters:** Classical Arabic scholarly texts contain thousands of terms not in MSA databases. Flagging them as OCR errors creates false warnings that bury real OCR problems.
**Detection:** Assert classical terms receive `analysis_status: "unknown"`, not OCR error flags.

---

### ADV-038 silent_corruption — Atomic write interrupted between manifest and content

**SPEC rule (§4.A.2 Atomic write):** "Both `manifest.json` and `content.jsonl` are written and flushed to disk in the temporary directory. After both files are verified... atomically renames."
**Adversarial input:** Simulated crash after writing `manifest.json` but before writing `content.jsonl` to the temp directory.

**Correct behavior:** On next startup, the recovery procedure finds a `normalized_tmp_*` directory. It attempts validation: manifest exists but content.jsonl is missing → validation fails → temp directory is removed. If `normalized_prev_*` exists, restore from it. No partial package is visible.
**Wrong behavior (naive impl):** (a) Recovery renames the incomplete temp dir to `normalized/` → downstream engines get manifest with no content. (b) Recovery doesn't check content.jsonl existence during validation.
**Why it matters:** A partial normalized package (manifest without content) would cause downstream engines to crash or produce empty results.
**Detection:** Assert recovery does NOT promote an incomplete temp directory. Assert `normalized/` either has both files or doesn't exist.

---

### ADV-039 arabic_trap — Semantic confusion: valid Arabic word substitution

**SPEC rule (§4.A.4 Semantic confusion hazard):** "the normalizer flags words where: (a) the OCR confidence for any character is below 0.90, AND (b) substituting a visually similar letter produces a different valid Arabic word"
**Adversarial input:** OCR output: "حَرَمَ" (he deprived). OCR confidence for the shaddah position: 0.85 (<0.90). Substituting shaddah: "حَرَّمَ" (he prohibited). Both are valid Arabic words.

**Correct behavior:** The word is flagged with `semantic_confusion_risk` containing both readings: `["حَرَمَ", "حَرَّمَ"]`. Downstream engines are warned.
**Wrong behavior (naive impl):** (a) Only checks letter substitution (ب↔ت↔ث↔ن), not diacritic variations. (b) Doesn't check confidence thresholds — flags every word. (c) Only checks morphological validity of the current reading, not alternative readings.
**Why it matters:** "حَرَمَ" vs "حَرَّمَ" changes fiqh rulings (deprivation vs prohibition). This is a scholarly integrity risk that only Arabic-aware systems can catch.
**Detection:** Assert `semantic_confusion_risk` entry with both readings. Assert both readings are valid Arabic.

---

### ADV-040 format_edge_case — Multi-volume source with Arabic filename stems

**SPEC rule (NORM_VOLUME_NUMBER_UNPARSEABLE):** "Filename stem cannot be parsed as a volume number (e.g., `المجلد_الأول.htm`, non-numeric stems)"
**Adversarial input:** Multi-volume source with filenames:
```
المجلد_الأول.htm    (Volume "The First")
المجلد_الثاني.htm   (Volume "The Second")
المجلد_الثالث.htm   (Volume "The Third")
```

**Correct behavior:** Numeric parsing fails for all filenames → `NORM_VOLUME_NUMBER_UNPARSEABLE`. Volumes assigned sequentially by filename sort order (Arabic sort of these names). Human gate triggered to confirm volume assignment.
**Wrong behavior (naive impl):** (a) Crashes on `int("المجلد_الأول")`. (b) Assigns random volume numbers. (c) Doesn't sort filenames properly for Arabic (locale-dependent).
**Why it matters:** Incorrect volume ordering means pages from volume 3 could appear before volume 1, scrambling the entire source.
**Detection:** Assert `NORM_VOLUME_NUMBER_UNPARSEABLE` is logged. Assert human gate is triggered. Assert volumes are assigned sequentially by sort order.

---

### ADV-041 silent_corruption — Fingerprint validation threshold with small corpus

**SPEC rule (§4.B.9):** "Fingerprint validation threshold reduced to 2.0 SD with explicit weak-check caveat and 5000-word minimum corpus requirement"
**Adversarial input:** Multi-layer source where one layer has only 3000 words attributed (below the 5000-word minimum).

**Correct behavior:** The fingerprint for that layer is marked `fingerprint_reliability: "insufficient_data"`. The fingerprint IS computed (for informational purposes) but validation IS NOT applied. No false alerts from small-sample statistics.
**Wrong behavior (naive impl):** (a) Applies the 2.0 SD threshold anyway on 3000 words → noisy false alerts from small sample. (b) Skips fingerprint computation entirely → no data available even for advisory purposes.
**Why it matters:** Statistical tests on small samples produce unreliable results. False alerts from fingerprint validation would cause unnecessary human gate triggers.
**Detection:** Assert `fingerprint_reliability: "insufficient_data"` for layers with <5000 words. Assert no validation alert for that layer.

---

### ADV-042 silent_corruption — Footnote classification: pattern match vs consensus boundary

**SPEC rule (§6 Consensus Integration, §4.B.4):** "Pattern matching against known tahqiq footnote patterns. If pattern confidence >= 0.85, accept classification without consensus. For ambiguous footnotes (pattern confidence < 0.85), require multi-model consensus per D-041."
**Adversarial input:** A footnote:
```
وقد ذكر المؤلف رحمه الله في كتابه الآخر نحو هذا المعنى
```
Pattern matching confidence: 0.84 (just below 0.85 — the "انظر:" pattern partially matches but the footnote is ambiguous between `cross_reference` and `general_commentary`).

**Correct behavior:** Confidence 0.84 < 0.85 → requires multi-model consensus. The footnote is classified via D-041 consensus, not single-model. `classification_method: "consensus"`.
**Wrong behavior (naive impl):** (a) Uses `>= 0.84` or rounds up → accepts pattern-only classification. (b) Runs consensus for ALL footnotes (wasteful). (c) Doesn't record `classification_method`.
**Why it matters:** A `cross_reference` misclassified as `general_commentary` (or vice versa) affects how the excerpting engine processes the footnote. The 0.85 boundary separates cheap pattern matching from expensive consensus.
**Detection:** Assert footnotes at 0.84 confidence use `classification_method: "consensus"`. Assert footnotes at 0.86 use `classification_method: "pattern"`.

---

## Summary by Threat

| Threat | Adversarial Cases | Key Tests |
|--------|------------------|-----------|
| T-1 (Silent Text Corruption) | ADV-006, ADV-007, ADV-021, ADV-022, ADV-039, ADV-045, ADV-048 | Diacritics, ZWNJ, NFC, entity corruption, semantic confusion, drift detection, encoding |
| T-2 (Attribution Error) | ADV-011, ADV-012, ADV-013, ADV-014, ADV-015, ADV-046 | Bold threshold, multi-signal, layer coverage, metadata override, fingerprint inversion |
| T-3 (Taxonomic Misplacement) | ADV-043, ADV-044 | Format detection threshold, competing format signals |
| T-4 (Context Loss) | ADV-001, ADV-002, ADV-017, ADV-019 | Footnote separator, division tree, unit_index gaps |
| T-5 (Synthesis Hallucination) | ADV-010, ADV-030 | PageHead leak, OCR empty-success |
| T-6 (Metadata Poisoning) | ADV-033, ADV-034, ADV-035 | Manifest count, marker format, cross-validation |
| T-7 (Duplication) | ADV-018, ADV-020 | Duplicate headings, duplicate page numbers |
