# Confidence Calibration Analysis (CG-1)

## Status: PENDING — Requires integration run with real LLM calls

Run `python scripts/run_session6_integration.py` to populate this analysis.

## Analysis Template

### Per-Fixture Confidence Scores

| Fixture | Genre | Science | Level | Structure | Authority | Multi-layer | Author |
|---------|-------|---------|-------|-----------|-----------|-------------|--------|
| 03_fiqh | — | — | — | — | — | — | — |
| ... | — | — | — | — | — | — | — |

### Overconfident Wrong Answers (>0.90 on incorrect field)

_None identified yet — requires integration data._

### Threshold Gate Rate Analysis

- **0.50 threshold (block)**: N/A fixtures blocked
- **0.70 threshold (review)**: N/A fixtures flagged for review

### CG-1 Conclusion

_To be determined after integration run. The question: Are confidence scores
calibrated well enough that the 0.50/0.70 thresholds produce appropriate
gate rates without excessive false positives or missed errors?_
