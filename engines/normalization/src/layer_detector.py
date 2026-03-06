"""Multi-layer text detection — SPEC §4.A.5.

For sources where is_multi_layer is true (or where layer signals are detected),
identifies which portions of each page belong to which text layer.

Shamela-specific layer signals (SPEC §4.A.2 Pass 5):
  - Bold text (<b> tags): ~75% of Shamela commentary exports use bold for matn
  - Bracket markers: matn enclosed in [ ]
  - Transition phrases: "قال المصنف", "قوله", "قال الشارح"
  - Font size differences: minority of exports use <font size> tags

Output: per-page text_layers array with layer types, author IDs, offsets, confidence.

Implementation order: Step 4 in IMPL_BRIEF.md.
"""

from __future__ import annotations

from engines.normalization.contracts import TextLayerSegment


def detect_layers_shamela(
    primary_text: str,
    html_before_stripping: str,
    source_layer_spec: list | None = None,
) -> list[TextLayerSegment]:
    """Detect text layers in a single Shamela page.

    Args:
        primary_text: The cleaned text (Pass 3 output).
        html_before_stripping: Raw HTML for this page (for bold/font detection).
        source_layer_spec: Source metadata text_layers (expected layers + authors).

    Returns:
        Ordered list of TextLayerSegment covering every character in primary_text.
        For single-layer sources, returns one segment covering the full text.
    """
    # TODO (Claude Code): Implement. See SPEC §4.A.5 and §4.A.2 Pass 5.
    raise NotImplementedError("detect_layers_shamela")
