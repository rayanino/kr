# Excerpting Campaign Analysis

**Recommendation:** block
**Books:** 5

## Book Status Table

| Book | Status | Chunks | Units | Excerpts | Errors | Anomalies | Time | Cost |
|------|--------|--------|-------|----------|--------|-----------|------|------|
| ext_39_masala | STRUCTURAL_FAIL | 16 | 203 | 200 | 3 | 1 | 2302s | EUR 3.2735 |
| ext_46_qa | STRUCTURAL_FAIL | 38 | 289 | 277 | 13 | 2 | 2762s | EUR 4.2960 |
| ibn_aqil_v1 | STRUCTURAL_FAIL | 14 | 243 | 241 | 3 | 2 | 2655s | EUR 4.4037 |
| ibn_aqil_v3 | STRUCTURAL_FAIL | 28 | 283 | 278 | 6 | 2 | 2670s | EUR 4.2977 |
| taysir | STRUCTURAL_FAIL | 184 | 3107 | 0 | 1 | 4 | 28801s | EUR 42.8193 |

## Campaign Totals

- Total chunks: 280
- Total units: 4125
- Total excerpts: 996
- Total anomalies: 11
- Total cost: EUR 59.0902
- Total time: 39189s

## Key Questions Answered

**Structurally healthy:** none
**Structural failures:** ext_39_masala, ext_46_qa, ibn_aqil_v1, ibn_aqil_v3, taysir
**Recurring anomaly patterns:** {"grouped_unit_loss": 5, "phase2a_chunk_failures": 4}

### ext_39_masala anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 3 grouped unit(s) lost between Phase 2b and final excerpts

### ext_46_qa anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 12 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-P2A-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2a classification

### ibn_aqil_v1 anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 2 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-P2A-FAILURES** [structural_fail] (observed): 2 chunk(s) failed Phase 2a classification

### ibn_aqil_v3 anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 5 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-P2A-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2a classification

### taysir anomalies

- **ANO-UNIT-LOSS** [structural_fail] (observed): 3107 grouped unit(s) lost between Phase 2b and final excerpts
- **ANO-ZERO-OUTPUT** [structural_fail] (observed): Zero excerpts produced despite upstream processing activity
- **ANO-P2A-FAILURES** [structural_fail] (observed): 4 chunk(s) failed Phase 2a classification
- **ANO-P2B-FAILURES** [structural_fail] (observed): 1 chunk(s) failed Phase 2b grouping
