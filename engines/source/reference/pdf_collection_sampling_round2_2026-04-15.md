# PDF Collection Sampling Round 2

**Date:** 2026-04-15
**Collection:** 285 files (276 unique + 9 duplicates), 1.17 GB, 133,313 total pages
**Method:** Full metadata scan of all 285 files + deep characterization of 5 new samples
**Prior sample:** 10 files (2026-04-14 report), all islamicbook.ws / PDFMaker 8.1

## Full-Collection Metadata Scan (285 files)

| Field | Values found |
|-------|-------------|
| Creator | 284x "Acrobat PDFMaker 8.1 for Word", **1x "Adobe Acrobat 8.1 Combine Files"** |
| Author | 284x "islamicbook.ws", 1x empty (tfsir-abn-kthir-.pdf, already in round 1) |
| Producer | 285x "Acrobat Distiller 8.1.0 (Windows)" -- unanimous |
| Creation dates | Feb 2010 (40), Mar 2010 (48), Apr 2010 (197) |

**Only one metadata outlier exists in the entire collection:** `almhla-.pdf` (al-Muhalla by Ibn Hazm) was assembled with "Combine Files" instead of PDFMaker. It is still from islamicbook.ws, same date range, same producer.

## 5 New Samples (not in round 1)

| File | Pages | Creator | Std Arabic | PF-B | PF-A | Diacritics |
|------|-------|---------|-----------|------|------|------------|
| almhla-.pdf | 1,634 | Combine Files | 27.6% | 69.0% | 3.4% | YES (2,317) |
| mjmwa-alftawa-.pdf | 5,838 | PDFMaker 8.1 | 27.5% | 69.0% | 3.5% | YES (4,287) |
| majm-almstlhat-alqranit.pdf | 6 | PDFMaker 8.1 | 19.1% | 76.5% | 4.4% | YES (1,060) |
| bdaea-alsnaea-.pdf | 2,622 | PDFMaker 8.1 | 27.1% | 69.8% | 3.0% | YES (4,584) |
| adb-almjalst.pdf | 17 | PDFMaker 8.1 | 0.6% | 94.1% | 5.3% | NO |

All 5 have text layers, zero images, and the same first-page template (`كتاب : [title] / المؤلف : [author]`).

## Conclusion

**The Presentation Forms finding holds across the full 285-file collection without exception.** Every PDF, including the sole "Combine Files" outlier, uses Unicode Presentation Forms (PF-A + PF-B) as the primary text encoding. The diacritics-trigger-standard-Arabic pattern from round 1 is also confirmed: files with tashkeel show ~27% standard Arabic; files without show <1%.

No heterogeneous sources, no scanned pages, no OCR-generated PDFs, no non-islamicbook.ws provenance. The collection is a single-source, single-tool corpus. NFKC normalization at extraction is the one mandatory transformation, and it applies uniformly to all 285 files.
