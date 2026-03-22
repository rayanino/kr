# Field Coverage and Quality Matrix

**Date:** 2026-03-22
**Total books analyzed:** 347
**Successful (full metadata):** 280
**Gate abort (partial):** 67

## Phase Overview

| Phase | Total | Success | Gate Abort | Success Rate |
|-------|-------|---------|------------|-------------|
| phase_c | 73 | 22 | 51 | 30% |
| phase_d | 204 | 204 | 0 | 100% |
| phase_e | 70 | 54 | 16 | 77% |

## Extraction Field Coverage (Deterministic)

These fields are extracted from Shamela HTML markup without LLM inference.

| Field | Present | Total | Coverage |
|-------|---------|-------|----------|
| title_full | 347 | 347 | 100.0% |
| author_name_raw | 330 | 347 | 95.1% |
| author_short | 347 | 347 | 100.0% |
| shamela_category | 347 | 347 | 100.0% |
| publisher | 296 | 347 | 85.3% |
| edition | 0 | 347 | 0.0% |
| muhaqiq | 0 | 347 | 0.0% |
| is_multi_volume | 347 | 347 | 100.0% |
| volume_count | 347 | 347 | 100.0% |
| has_muqaddima | 347 | 347 | 100.0% |
| death_date_raw | 0 | 347 | 0.0% |

## Result Field Coverage (After LLM Inference)

These fields include LLM-inferred values. Only success books counted.

| Field | Present | Success Books | Coverage |
|-------|---------|--------------|----------|
| title_arabic | 280 | 280 | 100.0% |
| genre | 280 | 280 | 100.0% |
| science_scope | 280 | 280 | 100.0% |
| is_multi_layer | 280 | 280 | 100.0% |
| structural_format | 280 | 280 | 100.0% |
| authority_level | 280 | 280 | 100.0% |
| trust_tier | 280 | 280 | 100.0% |
| trust_score | 280 | 280 | 100.0% |
| text_fidelity | 280 | 280 | 100.0% |
| page_count | 280 | 280 | 100.0% |
| volume_count | 280 | 280 | 100.0% |
| publisher | 233 | 280 | 83.2% |

## Extraction → Inference Improvement

Fields where LLM inference improves coverage over deterministic extraction.

| Field | Extraction % | Result % | Improvement |
|-------|-------------|---------|-------------|
| title_full → title_arabic | 100.0% | 100.0% | 0.0pp |
| volume_count → volume_count | 100.0% | 100.0% | 0.0pp |
| publisher → publisher | 85.3% | 83.2% | -2.1pp |

## LLM-Only Fields

These fields have no deterministic extraction source — they require LLM inference.

| Field | Coverage (success books) |
|-------|------------------------|
| genre | 100.0% |
| science_scope | 100.0% |
| is_multi_layer | 100.0% |
| structural_format | 100.0% |
| authority_level | 100.0% |
| trust_tier | 100.0% |
| trust_score | 100.0% |
| text_fidelity | 100.0% |

## Per-Phase Extraction Coverage

### phase_c (73 books)

| Field | Coverage |
|-------|----------|
| title_full | 100% |
| author_name_raw | 97% |
| author_short | 100% |
| shamela_category | 100% |
| publisher | 86% |
| edition | 0% |
| muhaqiq | 0% |
| is_multi_volume | 100% |
| volume_count | 100% |
| has_muqaddima | 100% |
| death_date_raw | 0% |

### phase_d (204 books)

| Field | Coverage |
|-------|----------|
| title_full | 100% |
| author_name_raw | 97% |
| author_short | 100% |
| shamela_category | 100% |
| publisher | 87% |
| edition | 0% |
| muhaqiq | 0% |
| is_multi_volume | 100% |
| volume_count | 100% |
| has_muqaddima | 100% |
| death_date_raw | 0% |

### phase_e (70 books)

| Field | Coverage |
|-------|----------|
| title_full | 100% |
| author_name_raw | 89% |
| author_short | 100% |
| shamela_category | 100% |
| publisher | 79% |
| edition | 0% |
| muhaqiq | 0% |
| is_multi_volume | 100% |
| volume_count | 100% |
| has_muqaddima | 100% |
| death_date_raw | 0% |
