"""Content census — SPEC §4.B.5.

Post-processing step that computes statistical profile of the entire source
after all content units are generated. Enables downstream engines to adapt
processing strategy per-source.

Profiles computed:
  - Text density (chars/page distribution)
  - Content type ratios (verse, table, Quran, hadith)
  - Layer complexity (transition density, matn ratio)
  - Structural depth (division count, tree depth)
  - Footnote density (per-page distribution)
  - Vocabulary profile (unique terms estimate, technical density, diacritics density)
  - Fidelity distribution

Implementation order: Step 6 in IMPL_BRIEF.md.
"""

from __future__ import annotations

from engines.normalization.contracts import ContentUnit, ContentCensus, NormalizedManifest


def compute_census(
    content_units: list[ContentUnit],
    manifest: NormalizedManifest,
) -> ContentCensus:
    """Compute the content census for a normalized source.

    Args:
        content_units: All content units in the package.
        manifest: The manifest (for division tree, layer map info).

    Returns:
        ContentCensus with all statistical profiles.
    """
    # TODO (Claude Code): Implement. See SPEC §4.B.5 for all metrics.
    raise NotImplementedError("compute_census")
