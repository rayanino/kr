# Normalization Corpus Sweep — Summary Report

**Date:** 2026-03-23 05:16 UTC
**Total books:** 100
**Processing time:** 26 seconds (0.4 minutes)
**Mean per-book:** 0.26s

## Status Distribution

| Status | Count | Percentage |
|--------|-------|-----------|
| OK | 100 | 100.0% |
| CRASH | 0 | 0.0% |
| VALIDATION_FAILED | 0 | 0.0% |

## Crash Analysis

No crashes.

## Content Unit Statistics

| Metric | Min | Max | Mean | Median |
|--------|-----|-----|------|--------|
| Content units | 6 | 870 | 199 | 83 |
| Page loss | 1 | 19 | 1.4 | — |
| Arabic ratio | 72.99% | 87.45% | 80.43% | — |
| Diacritics/book | 15 | 112659 | 14288 | — |

## Page Loss Distribution

| Page Loss | Count | Percentage |
|-----------|-------|-----------|
| 1 | 81 | 81.0% |
| 2 | 17 | 17.0% |
| 8 | 1 | 1.0% |
| 19 | 1 | 1.0% |

**Books with page loss > 5:** 2
- آراء ابن الجوزي التربوية: loss=8 (raw=609, units=601)
- أجنحة المكر الثلاثة: loss=19 (raw=751, units=732)

## Arabic Ratio

Books below 70%: 0 (0.0%)

## Warning Patterns (210 total)

- char_run: 116
- division_overlap: 55
- low_arabic_ratio: 39

## Multi-Layer Detection

Books with multi-layer segments: 2 (2.0%)

## Passaging Contract Alignment

Books failing any passaging input check: 22/100

## Boundary Continuity

Mean coverage: 97.49%
Books with 0% BC: 0

## Content Flags (aggregate)

- Hadith pages: 7729
- Quran pages: 4652
- Verse pages: 3743
