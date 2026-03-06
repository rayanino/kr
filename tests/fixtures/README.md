# Test Fixtures — بيانات الاختبار

Real Arabic scholarly sources for engine testing. All data provided by the owner.

---

## Fixture Inventory

### waraqat_usul/ — متن الورقات في أصول الفقه (الجويني)
**Format:** PDF (from Noor-Book.com)
**Type:** Single-layer prose, single author, one science
**Tests:** Basic source intake, metadata extraction (title, author, science), PDF text extraction
**Metadata:** Author: إمام الحرمين الجويني | Science: أصول الفقه | Single layer | No tahqiq

### ibn_aqil_alfiyyah/ — شرح ابن عقيل على ألفية ابن مالك
**Format:** PDF (4 volumes: vol6, vol7, vol8, vol9 from Noor-Book.com)
**Type:** Multi-layer (matn verses + sharh prose), multi-volume, with tahqiq
**Tests:** Multi-layer detection (D-030), genre chain (sharh → ألفية ابن مالك), multi-volume tracking, gap detection (volumes 1-5 missing), trustworthiness scoring (has muhaqiq), footnote extraction
**Metadata:** Commentator: ابن عقيل | Original author: ابن مالك | Muhaqiq: محمد محيي الدين عبد الحميد | Science: النحو والصرف | Genre chain: sharh on ألفية ابن مالك

### mughni_comparative/ — المغني (ابن قدامة)
**Format:** ZIP containing 69 Word documents (.doc), organized by كتاب (topic)
**Type:** Multi-volume comparative fiqh (presents multiple school positions)
**Tests:** Word document intake, chapter-based organization, comparative content extraction (for synthesis testing), large corpus handling
**Metadata:** Author: ابن قدامة المقدسي | Science: الفقه | Authority: primary source | Comparative (presents Hanbali position with other schools' views)
**Note:** Filenames in zip have encoding issues (Arabic encoded as CP1256 stored in a zip with no encoding flag). This is itself a useful edge case for the normalization engine.

### alfiyyah_versified/ — ألفية ابن مالك (متن)
**Format:** Plain text (.txt), copy-pasted from web source
**Type:** Versified text (منظومة), fully diacritized
**Tests:** Versified structural format detection, diacritic preservation, verse parsing (¤ separator between half-verses), text from web source (different quality than tahqiq edition)
**Metadata:** Author: ابن مالك | Science: النحو والصرف | Format: versified (منظومة) | ~1000 verses
**Source URL:** https://belajar-alfiyah-ibnumalik.blogspot.com/2011/09/blog-post.html

### photo_scan_ilm/ — كتاب العلم (ابن عثيمين)
**Format:** 6 iPhone JPEG photos of physical book pages
**Type:** Scanned pages requiring OCR
**Tests:** Photo intake path, OCR accuracy on printed Arabic, page number extraction, footnote detection in scanned text, colored text detection (red for Quran/hadith quotes)
**Metadata:** Author: ابن عثيمين | Science: general (العلم) | Pages around p.118

### owner_note/ — Owner-authored study note
**Format:** Plain text (.txt)
**Type:** Owner-authored tarjih (personal scholarly reasoning)
**Tests:** Owner-authored content intake, input type classification (tarjih), no external metadata to extract
**Content:** Brief reasoning about the ruling on photography, citing the principle لا يزول الحكم بتغير الآلات

### html_export_minimal/ — Synthetic HTML test data
**Format:** HTML files (info.html + content.html)
**Type:** Minimal HTML export simulating a structured Islamic text library export
**Tests:** HTML metadata extraction, heading hierarchy, page markers, matn/sharh CSS class detection, footnote markers
**Note:** This is synthetic (created by Claude), not from a real source. Use real fixtures above for integration testing.

---

## Coverage Matrix

| Test Case | Fixture |
|-----------|---------|
| Single-layer intake | waraqat_usul |
| Multi-layer detection (D-030) | ibn_aqil_alfiyyah, html_export_minimal |
| Multi-volume tracking | ibn_aqil_alfiyyah (vols 6-9), mughni_comparative (69 chapters) |
| Gap detection | ibn_aqil_alfiyyah (vols 1-5 missing) |
| Versified text (منظومة) | alfiyyah_versified |
| Genre chain (sharh→matn) | ibn_aqil_alfiyyah |
| Trustworthiness scoring | ibn_aqil_alfiyyah (has muhaqiq, publisher) |
| Comparative fiqh content | mughni_comparative |
| PDF text extraction | waraqat_usul, ibn_aqil_alfiyyah |
| Word document intake | mughni_comparative |
| Plain text intake | alfiyyah_versified |
| OCR / photo intake | photo_scan_ilm |
| Owner-authored content | owner_note |
| Footnote detection | ibn_aqil_alfiyyah, photo_scan_ilm |
| Diacritic preservation | alfiyyah_versified (fully diacritized) |
| Encoding edge cases | mughni_comparative (CP1256 filenames in zip) |
| HTML structured export | html_export_minimal |
