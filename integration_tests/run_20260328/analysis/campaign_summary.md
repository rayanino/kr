# Excerpting Campaign Analysis

**Recommendation:** block
**Books:** 5

## Book Status Table

| Book | Status | Chunks | Units | Excerpts | Errors | Anomalies | Time | Cost |
|------|--------|--------|-------|----------|--------|-----------|------|------|
| ext_39_masala | STRUCTURALLY_CLEAN | 16 | 14 | 14 | 0 | 0 | 129s | EUR 0.4163 |
| ext_46_qa | STRUCTURALLY_CLEAN | 38 | 13 | 13 | 0 | 0 | 125s | EUR 0.3824 |
| ibn_aqil_v1 | STRUCTURALLY_CLEAN | 14 | 5 | 5 | 0 | 0 | 84s | EUR 0.3238 |
| ibn_aqil_v3 | STRUCTURAL_FAIL | 28 | 0 | 0 | 0 | 3 | 726s | EUR 1.4887 |
| taysir | STRUCTURAL_FAIL | 184 | 11 | 9 | 2 | 1 | 81s | EUR 0.2608 |

## Campaign Totals

- Total chunks: 280
- Total units: 43
- Total excerpts: 41
- Total anomalies: 4
- Total cost: EUR 2.8720
- Total time: 1144s

## Key Questions Answered

**Structurally healthy:** ext_39_masala, ext_46_qa, ibn_aqil_v1
**Structural failures:** ibn_aqil_v3, taysir
**Recurring anomaly patterns:** none detected

### ibn_aqil_v3 anomalies

- **ANO-ZERO-OUTPUT** [structural_fail] (observed): Zero excerpts produced despite upstream processing activity
- **ANO-TRUNCATION** [structural_fail] (observed): 6 LLM response(s) truncated (finish_reason=length)
- **ANO-CONTRADICTION** [structural_fail] (inferred_high_confidence): Zero output + zero logged errors despite substantial activity

### taysir anomalies

- **ANO-UNIT-LOSS** [structural_fail] (inferred_moderate_confidence): 2 grouped unit(s) lost between Phase 2b and final excerpts
