# Fixture Quality Summary — 2026-04-02

Source: `scripts/validate_shamela_fixtures.py` run over the default corpus with
machine-readable output enabled.

## Corpus Coverage

- targets checked: `78`
- provenance mix:
  - `real`: `12`
  - `synthetic`: `1`
  - `real_extended`: `50`
  - `edge_extract`: `14`
  - `hand_crafted`: `1`

## Current Summary

- active findings: `1149`
- quality score: `0/100`
- top finding codes:
  - `metadata_missing_category`: `572`
  - `metadata_missing_title_span`: `571`
  - `missing_pagehead`: `3`
  - `fixture_doc_count_drift`: `2`
  - `western_page_digits`: `1`

## Important Reading

This result is useful, but it is **not** yet a clean “corpus is bad” verdict.

The two dominant codes are metadata-shape related and likely need calibration
against the expanded corpus before they are used as hard gates:

- `metadata_missing_category`
- `metadata_missing_title_span`

By contrast, the doc-drift findings are immediately actionable and trustworthy:

- real fixture README still says `12` fixtures while the manifest has `13`
- another source-facing doc/test location still reflects the old count

## What This Means

1. The validator is now broad enough to see the real evaluation corpus.
2. The next fixture-quality session should separate:
   - genuine corpus/doc drift
   - expected synthetic/hand-crafted deviations
   - over-strict metadata checks that need calibration

## Relevant Files

- `scripts/validate_shamela_fixtures.py`
- `tests/fixtures/shamela_real/README.md`
- `tests/fixtures/shamela_real/MANIFEST.json`
- `reference/SHAMELA_COLLECTION.md`
- `engines/source/tests/test_deterministic.py`
