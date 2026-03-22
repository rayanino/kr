# Format Diversity Experiment — Run Summary

**Model:** anthropic/claude-opus-4.6
**Approaches:** A (single-call) + B (classify-then-group)
**Total divisions:** 13
**Total API calls:** 39 (13 for A, 26 for B classify+group)

**Note:** Taysir Approach B required MAX_TOKENS=32768 (classify produces 125-166 segments for 2500-3100w text).

## Per-Division Results

| Fixture | Div | Heading | Words | A Units | B Units | Errors |
|---------|-----|---------|-------|---------|---------|--------|
| ext_39_masala | 23 | غسل الميت | 1162 | 10 | 10 | none |
| ext_39_masala | 29 | تكفين الميت | 703 | 12 | 11 | none |
| ext_46_qa | 308 | تنبيه | 451 | 7 | 10 | none |
| ibn_aqil_v1 | 115 | العلم | 865 | 8 | 13 | none |
| ibn_aqil_v1 | 174 | المعرف بأداة التعريف | 836 | 11 | 8 | none |
| ibn_aqil_v1 | 7 | الكلام وما يتألف منه | 1376 | 16 | 21 | none |
| ibn_aqil_v3 | 101 | إعمال اسم الفاعل | 967 | 10 | 10 | none |
| ibn_aqil_v3 | 153 | نعم وبئس وما جرى مجراهما | 1097 | 12 | 15 | none |
| ibn_aqil_v3 | 166 | أفعل التفضيل | 1270 | 13 | 12 | none |
| taysir | 117 | بَابُ الإمَامَة | 2513 | 21 | 20 | none |
| taysir | 233 | بَابُ صَلَاةِ العيدَين | 2522 | 19 | 28 | none |
| taysir | 478 | بَابُ الرِّبا والصَّرْف | 2881 | 22 | 27 | none |
| taysir | 661 | كِتاب الأيمَان والنذور | 3111 | 24 | 41 | none |

**All 13 divisions processed successfully with both approaches. Zero errors.**
