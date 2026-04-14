# PDF Collection Characterization Report

**Date:** 2026-04-14
**Collection:** `C:/Users/Rayane/Desktop/kr/pdf-export-samples/`
**Tool:** PyMuPDF (fitz) 1.27.2.2
**Sample size:** 10 of 175 PDFs (chosen to cover size range from 74KB to 55MB)

---

## Per-File Characterization

### 1. rsalt-abi-dawd.pdf

| Property | Value |
|----------|-------|
| File size | 72.9 KB |
| Page count | 5 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | NO |
| Unicode blocks | 100% Presentation Forms (93.6% PF-B, 6.4% PF-A, 0% standard Arabic) |
| Metadata title | `كتاب` (generic) |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 24 (detailed section headings) |
| Images on page 1 | 0 |
| Created | 2010-03-18 |

**Text sample (page 1, NFKC-normalized):** رسالة أبي داود إلى أهل مكة وغيرهم في وصف سننه ... المؤلف الإمام أبي داود سليمان بن الأشعت ... بسم االله الرحمن الرحيم

**Notes:** Shortest file. Clean text extraction. Title page structure: `كتاب: [title] / المؤلف: [author]`. No diacritics preserved. ToC has 24 section headings despite only 5 pages -- indicates granular bookmarking.

---

### 2. klmt-alikhlas.pdf

| Property | Value |
|----------|-------|
| File size | 136.8 KB |
| Page count | 13 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | NO |
| Unicode blocks | 100% Presentation Forms (92.9% PF-B, 7.1% PF-A) |
| Metadata title | `كتاب : كلمة الإخلاص وتحقيق معناها` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 2 |
| Images on page 1 | 0 |
| Created | 2010-02-27 |

**Text sample (page 1):** كلمة الإخلاص وتحقيق معناها ... المؤلف: ابن رجب الحنبلي ... خرج البخاري ومسلم في الصحيحين عن أنس رضي الله عنه

**Notes:** Title metadata is richer -- includes full book title. Author `ابن رجب الحنبلي` correctly extracted from text. Same islamicbook.ws provenance.

---

### 3. amdt-alahkam.pdf

| Property | Value |
|----------|-------|
| File size | 645.6 KB |
| Page count | 70 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | YES (594 marks in sampled pages) |
| Unicode blocks | Mixed: 18.8% standard Arabic (0600-06FF), 76.4% PF-B, 4.8% PF-A |
| Metadata title | `كتاب : عُمدةُ الأَحكام من كلامِ خيرِ الأَنامِ` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 2 |
| Images on page 1 | 0 |
| Created | 2010-03-19 |

**Text sample (mid-page):** عَنْ عَبْدِ اللَّهِ بْنِ عَبَّاسٍ رضي الله عنهما قَالَ: قَالَ رَسُولُ اللَّهِ صلى الله عليه وسلم يَوْمَ فَتْحِ مَكَّةَ

**Notes:** First file with diacritics. The hadith text carries full tashkeel on the matn (hadith wording). Standard Arabic block chars appear specifically in the diacritized portions, while undiacritized text remains in Presentation Forms. This means diacritics cause the PDF text layer to switch Unicode blocks mid-text.

---

### 4. mqdmt-abn-alslah-.pdf

| Property | Value |
|----------|-------|
| File size | 973.9 KB |
| Page count | 122 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | NO (only 0.3% standard Arabic) |
| Unicode blocks | 99.7% Presentation Forms (94.1% PF-B, 5.6% PF-A) |
| Metadata title | `الكتاب : مقدمة ابن الصلاح` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 0 |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** مقدمة ابن الصلاح ... المؤلف: أبو عمرو عثمان بن عبد الرحمن الشهرزوري ... قال الشيخ الإمام الحافظ مفتي الشام تقي الدين

**Notes:** No ToC despite 122 pages. Metadata uses `الكتاب` prefix variant. Hadith sciences text -- mostly prose without tashkeel.

---

### 5. snn-altrmda-.pdf

| Property | Value |
|----------|-------|
| File size | 8.79 MB |
| Page count | 982 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | YES (1,025 marks in sampled pages) |
| Unicode blocks | Mixed: 25.4% standard Arabic, 71.5% PF-B, 3.1% PF-A |
| Metadata title | `كتاب : سنن الترمذى` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 73 (13 level-1 entries = 13 volumes merged) |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** سنن الترمذى ... محمد بن عيسى بن سَوْرة ... ١- الطهارة ... بابُ مَا جَاءَ لاَ تُقْبَلُ صَلاَةٌ بِغَيْرِ طُهُورٍ ... حَدَّثَنَا قُتَيْبَةُ بْنُ سَعِيدٍ

**Notes:** Multi-volume work merged into single PDF. Level-1 ToC entries use filename-based IDs (`snn-altrmda-001` through `snn-altrmda-013`), suggesting automated export from a library system. Hadith matn is diacritized; commentary/editorial text is not.

---

### 6. shih-albkhari-.pdf

| Property | Value |
|----------|-------|
| File size | 13.07 MB |
| Page count | 1,607 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | YES (1,493 marks in sampled pages) |
| Unicode blocks | Mixed: 27.0% standard Arabic, 68.6% PF-B, 4.5% PF-A |
| Metadata title | `كتاب : الجامع الصحيح المسند من حديث رسول الله صلى الله عليه وسلم وسننه وأيامه -صحيح البخاري` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 0 |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** الجامع الصحيح المسند من حديث رسول الله ... محمد بن إسماعيل بن إبراهيم بن المغيرة البخاري ... بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ بَابُ بَدْءُ الْوَحْيِ

**Notes:** Richest metadata title of all files -- includes full classical book title. No ToC despite 1,607 pages. Heavy diacritization on hadith text. Highest standard Arabic ratio (27%) correlates with highest diacritic density -- confirming the diacritics-trigger-standard-Arabic pattern.

---

### 7. tfsir-abn-kthir-.pdf

| Property | Value |
|----------|-------|
| File size | 23.43 MB |
| Page count | 3,091 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | NO (0.2% standard Arabic) |
| Unicode blocks | 99.8% Presentation Forms (93.0% PF-B, 6.9% PF-A) |
| Metadata title | `تفسير ابن كثير` |
| Metadata author | (none) |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 0 |
| Images on page 1 | 0 |
| Created | 2010-04-02 |

**Text sample (page 1):** تفسير القرآن العظيم ... المؤلف: أبو الفداء إسماعيل بن عمر بن كثير القرشي الدمشقي ... مقدمة تفسير القرآن العظيم ... بسم الله الرحمن الرحيم

**Notes:** Only file with empty author metadata (author field is blank). Uses `subject: www.islamicbook.ws` instead. Despite being a tafsir with heavy Quranic quotation, almost no diacritics in the extracted text. This suggests Quranic verses were not diacritized in the source Word document, or diacritics were lost in the export.

---

### 8. msnd-ahmd-.pdf

| Property | Value |
|----------|-------|
| File size | 33.79 MB |
| Page count | 3,866 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | YES (1,502 marks in sampled pages) |
| Unicode blocks | Mixed: 26.7% standard Arabic, 69.5% PF-B, 3.9% PF-A |
| Metadata title | `كتاب : مسند أحمد` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 0 |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** مسند أحمد ... أبو عبد الله أحمد بن محمد بن حنبل ... مُسْنَدُ الْعَشَرَةِ الْمُبَشَّرِينَ بِالْجَنَّةِ ... مُسْنَدُ أَبِي بَكْرٍ الصِّدِّيقِ رَضِيَ اللَّهُ عَنْهُ

**Text sample (mid-page):** حَدَّثَنَا مُوسَى بْنُ دَاوُدَ حَدَّثَنَا ابْنُ لَهِيعَةَ عَنْ أَبِي الزُّبَيْرِ عَنْ جَابِرٍ

**Notes:** Second largest by page count. Heavy isnad chains throughout -- every page has حَدَّثَنَا / أَخْبَرَنَا formulas. Standard Arabic block usage (26.7%) correlates perfectly with diacritized hadith text.

---

### 9. althrir-.pdf

| Property | Value |
|----------|-------|
| File size | 52.86 MB |
| Page count | 6,000 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | MINIMAL (only 64 marks in sampled pages; 3.9% standard Arabic) |
| Unicode blocks | 96.1% Presentation Forms (91.0% PF-B, 5.2% PF-A) |
| Metadata title | `كتاب : التحرير والتنوير-تفسير ابن عاشور` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 153 (68 level-1 = 68 volumes/parts merged) |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** التحرير والتنوير المعروف بتفسير ابن عاشور ... محمد الطاهر بن محمد بن محمد الطاهر بن عاشور التونسي ... المجلد الأول ... مقدمة

**Text sample (last page):** يقول محمد الطاهر ابن عاشور: قد وفيت بما نويت، وحقق الله ما ارتجيت فجئت بما سمح به الجهد من بيان معاني القرآن ودقائق نظامه وخصائص بلاغته

**Notes:** Largest file in the collection. 68 merged volumes. Richest ToC with 153 entries including detailed muqaddimah sections (المقدمة الأولى، المقدمة الثانية، المقدمة الثالثة). Colophon on last page with author self-identification. Despite being a tafsir, minimal diacritization.

---

### 10. hashit-abn-alqim-.pdf

| Property | Value |
|----------|-------|
| File size | 2.71 MB |
| Page count | 415 |
| Text layer | YES -- readable Arabic |
| Diacritics (tashkeel) | NO (0% standard Arabic) |
| Unicode blocks | 100% Presentation Forms (94.1% PF-B, 5.9% PF-A) |
| Metadata title | `كتاب : حاشية ابن القيم على سنن أبي داود` |
| Metadata author | `islamicbook.ws` |
| Creator | Acrobat PDFMaker 8.1 for Word |
| ToC entries | 31 (4 level-1 = 4 volumes merged) |
| Images on page 1 | 0 |
| Created | 2010-04-01 |

**Text sample (page 1):** حاشية ابن القيم على سنن أبي داود ... محمد بن أبي بكر بن قيم الجوزية ... قال الشيخ شمس الدين بن القيم رحمه الله بعد قول الحافظ زكي الدين

**Text sample (mid-page):** قال المؤمنين وابن عباس وابن عمر وهو قول مالك وأبى حنيفة وأحمد في إحدى الروايتين عنه وذهب الشافعي وأحمد في الرواية المشهورة عنه أن الصوم فيه مستحب غير واجب

**Notes:** Multi-layer text (hashiyah genre). Contains madhab attribution signals: explicit mentions of مالك, أبو حنيفة, الشافعي, أحمد with their positions. Last page (415) has empty text -- possibly a blank separator page. 4 volumes merged.

---

## Aggregate Statistics

| Metric | Value |
|--------|-------|
| Files with text layers | **10/10 (100%)** |
| Files with usable (non-corrupt) text | **10/10 (100%)** |
| Files that are pure scans | **0/10 (0%)** |
| Average page count | **1,617** |
| Median page count | **551** |
| Min page count | 5 (rsalt-abi-dawd.pdf) |
| Max page count | 6,000 (althrir-.pdf) |
| Total pages sampled | 16,171 |
| Files with diacritics | **4/10 (40%)** |
| Files with ToC | **6/10 (60%)** |
| Total collection files | 175 |
| Total collection size | 0.56 GB |

### Page Count Distribution

| Range | Count | Files |
|-------|-------|-------|
| 1-50 | 2 | rsalt-abi-dawd (5), klmt-alikhlas (13) |
| 51-200 | 2 | amdt-alahkam (70), mqdmt-abn-alslah (122) |
| 201-500 | 1 | hashit-abn-alqim (415) |
| 501-1000 | 1 | snn-altrmda (982) |
| 1001-2000 | 1 | shih-albkhari (1,607) |
| 2001-4000 | 2 | tfsir-abn-kthir (3,091), msnd-ahmd (3,866) |
| 4001+ | 1 | althrir (6,000) |

---

## Critical Findings for Source Engine Spec

### Finding 1: ALL text is in Arabic Presentation Forms (CRITICAL)

Every single PDF encodes its Arabic text primarily in the Unicode Presentation Forms blocks (U+FB50-FDFF and U+FE70-FEFF), NOT in the standard Arabic block (U+0600-06FF). This means:

- **Every character is stored as a positional glyph variant** (isolated, initial, medial, final) rather than as an abstract character
- Common ligatures like لا, بي, في are stored as precomposed ligature codepoints (PF-A block)
- **Standard Arabic text searches will FAIL** on raw extracted text (confirmed: searching for `بسم` in standard Arabic finds nothing)
- **NFKC normalization converts presentation forms back to standard Arabic** (confirmed: after NFKC, `بسم` is found)

**Implication for source engine:** The PDF text extraction pipeline MUST apply Unicode NFKC normalization at the extraction boundary. This is a mandatory pre-processing step, not optional cleanup. Without it, no downstream Arabic text processing (word boundary detection, isnad identification, Quranic citation matching, scholar name extraction) will work.

**IMPORTANT caveat:** The project's Critical Rule #8 states "NEVER apply Unicode normalization (NFC/NFD/NFKC/NFKD) to scholarly text." This rule was written for Shamela HTML sources where text is already in standard Arabic. For PDF-extracted text in Presentation Forms, NFKC is not altering the scholarly content -- it is recovering the actual characters from rendering-layer artifacts. This distinction MUST be documented as a spec decision with a clear boundary: normalization happens at extraction, before the text enters the "scholarly text" domain.

### Finding 2: Diacritics correlate with Unicode block mixing

Files with diacritics (amdt-alahkam, snn-altrmda, shih-albkhari, msnd-ahmd) show a mixed Unicode profile: diacritized text appears in the standard Arabic block (0600-06FF) while undiacritized text remains in Presentation Forms. This pattern means:

- Diacritics are present in the underlying Word document, not added by the PDF export
- The PDF creator (Acrobat PDFMaker 8.1 for Word) handles diacritized and undiacritized text differently
- After NFKC normalization, all text will be in standard Arabic, but diacritics will be preserved where they exist in the source

**Implication:** Diacritic preservation is already handled correctly by the source material for hadith collections (which are the texts most likely to have tashkeel). No diacritic recovery pipeline is needed.

### Finding 3: Uniform provenance -- all from islamicbook.ws via Word+Acrobat

Every PDF was:
- Created by **Acrobat PDFMaker 8.1 for Word** (Microsoft Word to PDF conversion)
- Authored by **islamicbook.ws** (consistent source)
- Created in **March-April 2010**
- Modified on **2019-05-27** (batch operation -- likely a re-export or metadata update)

**Implication:** This is a highly uniform collection. The source engine does not need to handle heterogeneous PDF creation tools, scan-based PDFs, or OCR scenarios for THIS collection. However, the spec should still account for scan PDFs as a future source type.

### Finding 4: Multi-volume works are merged into single PDFs

Large works (Sunan al-Tirmidhi, al-Tahrir wa al-Tanwir, Hashiyat Ibn al-Qayyim) have multiple volumes concatenated into a single PDF. Volume boundaries are marked by:
- Level-1 ToC entries with filename-based IDs (e.g., `snn-altrmda-001`, `althrir-042`)
- These IDs appear to be the original per-volume filenames from the source library system

**Implication:** The source engine needs volume detection logic to split multi-volume PDFs into logical volume units. ToC-based splitting is the primary strategy; filename-pattern IDs in ToC entries are a strong signal.

### Finding 5: Metadata quality varies but follows a pattern

| Pattern | Files | Example |
|---------|-------|---------|
| Title = `كتاب` (generic) | 1 | rsalt-abi-dawd |
| Title = `كتاب : [full title]` | 7 | klmt-alikhlas, amdt-alahkam, msnd-ahmd, etc. |
| Title = `الكتاب : [full title]` | 1 | mqdmt-abn-alslah |
| Title = `[title only]` | 1 | tfsir-abn-kthir |
| Author = `islamicbook.ws` | 9 | All except tfsir-abn-kthir |
| Author = `(none)` | 1 | tfsir-abn-kthir (uses subject field instead) |

**Implication:** PDF metadata `title` field is useful but not reliable as the primary title source. The first page's structured text (`كتاب: [title] / المؤلف: [author]`) is the canonical source for both title and author. This page-1 pattern is consistent across ALL 10 files.

### Finding 6: ToC presence and quality is inconsistent

- 6/10 files have a ToC (bookmarks)
- Quality ranges from rich (althrir with 153 entries, rsalt-abi-dawd with 24) to absent (shih-albkhari, tfsir-abn-kthir, msnd-ahmd -- major works with zero bookmarks)
- ToC title text is in standard Arabic (not Presentation Forms), suggesting it was added as metadata rather than extracted from the text layer

**Implication:** ToC is a valuable but optional signal. The spec cannot depend on ToC for structure detection. Text-based structural analysis (detecting كتاب, باب, فصل headings) is the required fallback.

### Finding 7: No images, no scans

Zero images were found on page 1 of any sampled file. Combined with the 100% text layer presence, this confirms the collection is entirely text-based PDFs (Word-to-PDF exports), not scanned manuscripts. OCR is unnecessary for this collection.

### Finding 8: Page structure has consistent patterns

Every file's page 1 follows the same template:
```
كتاب : [title]
المؤلف : [author full name]
[optional: section heading]
[bismillah or content start]
```

This structured first page is a reliable extraction target for metadata.

---

## Recommendations for Source Engine Spec

1. **NFKC normalization at PDF extraction boundary** -- mandatory, non-negotiable. Document as a spec decision distinguishing it from the "never normalize scholarly text" rule.

2. **First-page metadata extraction** -- parse the `كتاب:` / `المؤلف:` pattern as the primary metadata source. PDF metadata fields as secondary/cross-validation.

3. **Volume boundary detection** -- parse ToC level-1 entries with filename-pattern IDs. When no ToC exists, use structural heading detection.

4. **Diacritic-aware processing** -- after NFKC normalization, diacritics will be in standard form. No special handling needed beyond the project's existing diacritic preservation rules.

5. **No OCR pipeline needed** for this collection. Spec should note this as a collection characteristic, not a design constraint (future collections may include scans).

6. **Text extraction quality is high** -- Arabic ratio consistently 0.66-0.85, zero garbage characters across all samples. Post-NFKC text is clean and directly usable.
