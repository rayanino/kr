# Architecture C Experiment — Run Summary

**Model:** anthropic/claude-opus-4.6
**Total API calls:** 34
**Total latency:** 1265.2s

## Per-Division Results

| Fixture | Div | Heading | Words | A Units | B Units | C Units | Errors |
|---------|-----|---------|-------|---------|---------|---------|--------|
| 02_nahw_muhaqiq | 10 | باب "حروف زائدة" | 567 | 11 | 11 | — | none |
| 02_nahw_muhaqiq | 20 | باب "ذكر أبنية الأسماء الثنائية والمزيدة | 735 | 26 | 13 | — | none |
| 03_fiqh | 4 | المطلب الأول: تعريف الاضطباع والرمل | 536 | 11 | 8 | 7 | none |
| 03_fiqh | 64 | الفرع الرابع: كيف يصنع من زُحِم في الطوا | 815 | 13 | 8 | 9 | none |
| 06_usul | 22 | فصل فِي أَحْكَام الْمُفْتِينَ | 1040 | 18 | 13 | — | none |
| 06_usul | 9 | فصل فِي أَقسَام الْمُفْتِينَ | 963 | 13 | 13 | — | none |
| 07_balagha | 175 | الفصل الرابع الفصل والوصل | 783 | 9 | 10 | — | none |
| 07_balagha | 197 | تعريفه: | 625 | 12 | 11 | — | none |
| 10_no_author | 31 | بابُ صلاة الجماعة والإمامة | 710 | 18 | 15 | — | none |
| 10_no_author | 68 | باب شروطه وما نُهي عَنْهُ | 750 | 20 | 20 | — | none |

## API Call Log

| Fixture | Div | Approach | Call | Latency (ms) |
|---------|-----|----------|------|-------------|
| 02_nahw_muhaqiq | div_10 | A | extract | 28716 |
| 02_nahw_muhaqiq | div_10 | B | classify | 10467 |
| 02_nahw_muhaqiq | div_10 | B | group | 24787 |
| 02_nahw_muhaqiq | div_20 | A | extract | 70401 |
| 02_nahw_muhaqiq | div_20 | B | classify | 60761 |
| 02_nahw_muhaqiq | div_20 | B | group | 34306 |
| 03_fiqh | div_4 | A | extract | 29817 |
| 03_fiqh | div_4 | B | classify | 29217 |
| 03_fiqh | div_4 | B | group | 26626 |
| 03_fiqh | div_4 | C | classify | 30327 |
| 03_fiqh | div_4 | C | group | 23590 |
| 03_fiqh | div_64 | A | extract | 32849 |
| 03_fiqh | div_64 | B | classify | 25962 |
| 03_fiqh | div_64 | B | group | 25800 |
| 03_fiqh | div_64 | C | classify | 26405 |
| 03_fiqh | div_64 | C | group | 28928 |
| 06_usul | div_22 | A | extract | 73984 |
| 06_usul | div_22 | B | classify | 62676 |
| 06_usul | div_22 | B | group | 50896 |
| 06_usul | div_9 | A | extract | 67672 |
| 06_usul | div_9 | B | classify | 76266 |
| 06_usul | div_9 | B | group | 48801 |
| 07_balagha | div_175 | A | extract | 28021 |
| 07_balagha | div_175 | B | classify | 30510 |
| 07_balagha | div_175 | B | group | 28915 |
| 07_balagha | div_197 | A | extract | 29303 |
| 07_balagha | div_197 | B | classify | 28523 |
| 07_balagha | div_197 | B | group | 28651 |
| 10_no_author | div_31 | A | extract | 42911 |
| 10_no_author | div_31 | B | classify | 20429 |
| 10_no_author | div_31 | B | group | 38567 |
| 10_no_author | div_68 | A | extract | 40911 |
| 10_no_author | div_68 | B | classify | 18122 |
| 10_no_author | div_68 | B | group | 41048 |

**Total API calls:** 34
**Total latency:** 1265.2s
