"""Source Engine — محرك المصادر

Orchestrates the 9-step acquisition workflow (SPEC §4.A.2):
1. Staging → 2. Format detection → 3. Metadata extraction →
4. Metadata inference → 5. Duplicate detection → 6. Freezing →
7. Registration → 8. Trustworthiness evaluation → 9. Handoff

Entry point: acquire_source(staging_path, owner_hints) → SourceMetadata

This module coordinates the steps. Each step delegates to specialized modules:
- Format detection: format_detector.py
- Metadata extraction: extractors/ (one per format)
- Metadata inference: metadata_inference.py
- Duplicate detection: deduplication.py
- Freezing: freezer.py
- Registration: registries/
- Trustworthiness: trust_evaluator.py
"""
