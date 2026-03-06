"""Deduplication — SPEC §4.A.7

Two levels:
1. Source-level (exact): SHA-256 hash match → SRC_DUPLICATE_EXACT
2. Work-level: same abstract work, different edition → SRC_DUPLICATE_WORK (info)

Near-duplicate detection: [NOT YET IMPLEMENTED]
"""
